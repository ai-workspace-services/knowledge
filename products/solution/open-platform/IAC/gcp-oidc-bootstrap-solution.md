# GCP Cloud IAC 方案：Bootstrap OIDC、凭据分层与多云 Landing Zone 接入

> 关联 Epic：[`ai-workspace-infra/platform-ops-toolkit#804`](https://github.com/ai-workspace-infra/platform-ops-toolkit/issues/804) — 多云 IAC 对接与 Landing Zone
> 关联 P0：[`ai-workspace-infra/platform-ops-toolkit#805`](https://github.com/ai-workspace-infra/platform-ops-toolkit/issues/805) — GCP bootstrap E2E
> Project Board：https://github.com/orgs/ai-workspace-infra/projects/2
> 涉及仓库：`platform-ops-toolkit`（workflows/scripts/docs/tests）、`iac_modules`（Terraform 模块）、`gitops`（环境/资源声明）
> 最后更新：2026-09-22

## 1. 背景与目标

Multi Cloud IAC 对接与 Landing Zone Epic 要求 GCP 侧对齐 AWS 已有的模式：GitHub Actions OIDC → Vault JWT role → 云厂商 STS/WIF → 短期部署身份，日常变更流水线不出现任何固定的云账号密钥。审计 Project Board 时发现 GCP bootstrap（`#805`）长期卡在 P0，问题看似是"缺 IAM 权限"，实际根因是 GCP 项目 ID 配置错误；此外，bootstrap 阶段本身如何在"零人工长期凭据"的前提下完成第一次 WIF 落地，是一个此前未被写清楚的架构问题。本方案覆盖：

1. 根因定位与修复（错误的项目 ID）。
2. Bootstrap 与 Runtime 两个阶段的凭据分层架构，以及为什么 Bootstrap 阶段必须允许一次性 Admin JSON key。
3. 一次性 Admin SA key 的完整生命周期实现（创建 → 使用 → 吊销），以及组织策略（Org Policy）约束下的应对方式。
4. IaC 渲染管线的条件化改造：让一个"只创建 Spot VM"的最小 manifest 可以安全地跑通 GitOps → Terraform → GitHub Actions 全链路，而不触碰完整平台栈（network/Artifact Registry/Cloud Run）。
5. Terraform state 按 manifest 隔离，避免最小验证 manifest 与完整平台 state 相互覆盖。
6. 当前已合并 / 待合并的变更清单，以及尚未完成的收尾工作。

## 2. 根因：GCP 项目 ID 拼写错误，而非权限问题

`#805` 的历史评论一直假设是 IAM 权限不足，实际诊断链路：

```
gcloud projects add-iam-policy-binding xworktech-open-platform-uat ...
  → PERMISSION_DENIED: ... does not have permission ... getIamPolicy (or it may not exist)
```

用多个账号跑 `gcloud projects list` 交叉验证后确认：GitOps 里声明的项目 ID `xworktech-open-platform-uat` / `xworktech-open-platform-prod` 在 GCP 中根本不存在；真实项目是：

| 环境 | 错误 ID（GitOps 原声明） | 真实 ID |
|---|---|---|
| UAT | `xworktech-open-platform-uat` | `xwork-open-platform-uat` |
| PROD | `xworktech-open-platform-prod` | `xwork-open-platform-prod` |

两个真实项目都挂在 Organization `744119519286`（xworktech.com）下。修复方式是在三个仓库里做了一次全局订正（详见第 7 节），而不是去追加 IAM 授权——追加权限只会授权到一个不存在的项目，永远不会生效。

## 3. 凭据分层架构

这是本方案的核心约定，已同步写入 Epic `#804` 的"凭据分层约定"章节。设计目标是：Bootstrap（第一次把 WIF 打通）允许一次性使用 Admin 级凭据；一旦 WIF 建立，日常变更流水线永远不允许再出现任何固定的 Service Account 凭据，效果对齐 AWS 的 `AssumeRoleWithWebIdentity` 模式。

| 阶段 | 触发方式 | 允许的凭据 | 凭据来源 |
|---|---|---|---|
| **Bootstrap Init**（一次性，按环境执行一次） | `gcp-oidc-bootstrap.yml` 手动 `workflow_dispatch` | 一个 Admin 权限的 Service Account JSON key：`GCP_AUTH_JSON` | Vault `kv/CICD/<env>/gcp-bootstrap/<account>`，Job 内换取短期 access token 后立即吊销 |
| **日常变更流水线**（`gcp-iac-pipeline.yml` 及所有 LandingZone/Account/Resources/Master matrix workflow） | 正常 CI 触发 | 仅短期 WIF 凭据，**禁止任何固定 JSON key / 长期 token / Admin 身份** | GitHub OIDC → Vault JWT role `github-actions-platform-ops-toolkit-<env>-gcp-oidc-<account>` → Google STS/WIF |

### 3.1 为什么 Bootstrap 必须允许一次性 Admin JSON key

WIF Pool、Provider、deploy Service Account 这些资源本身还不存在，第一次创建它们时不可能已经有 WIF 身份可用——这是一个先有鸡还是先有蛋的问题。因此 Bootstrap 阶段必须允许两种输入之一：

- 一个已经有权限的人类账号的短期 `GCP_ACCESS_TOKEN`（`gcloud auth application-default print-access-token`，约 1 小时过期，无需修改任何组织策略）；
- 或者一个专门创建的一次性 Admin Service Account 的 `GCP_AUTH_JSON` key（本方案新增，见第 4 节），适合没有常驻管理员账号、需要脚本化/无人值守完成 bootstrap 的场景。

两条路径都只在 Bootstrap 这一次性 Job 里使用，且都不落地到 GitHub Secrets、Git 仓库或 runner 磁盘——只经过内存/Vault。

### 3.2 日常流水线的强约束

- 唯一身份来源是 `configure-gcp-oidc` composite action：GitHub OIDC token → Vault JWT role → `kv/<env>/platform/oidc/<account>`（Bootstrap apply 成功后由 Terraform 输出写入）→ Google WIF 换取的短期凭据。
- deploy Service Account 按最小权限授予（见 4.4），不授予 `Owner`/`Editor`/任何 IAM 管理类角色。
- Contract test（`.github/scripts/tests/gcp_oidc_bootstrap_contract_test.sh`）强制：
  - `credentials.json` / `service_account_key` / `private_key` 等字符串不得出现在 Bootstrap 以外的任何 workflow/action 中；
  - `bootstrap_gcp_auth_kv.sh` 的角色列表（`kv_helper` 变量）不得出现 `roles/owner`、`roles/editor`；
  - Bootstrap workflow 必须包含 key 删除与 Vault 字段销毁的步骤字符串。

## 4. Bootstrap 一次性 Admin SA key：`--auth-json` 实现

`scripts/gcp/bootstrap_gcp_auth_kv.sh` 原本只支持写入/校验短期 `GCP_ACCESS_TOKEN`（token 模式）。本方案为其新增 `--auth-json` 模式，把"人工准备"压缩成一条命令，并内建吊销机制。

### 4.1 两种模式对比

| | token 模式（默认，原有） | `--auth-json` 模式（新增） |
|---|---|---|
| 用途 | 已有管理员人类账号，临时借用其 ADC | 无常驻管理员账号，或需要脚本化 bootstrap |
| Vault 写入字段 | `GCP_ACCESS_TOKEN`、`GCP_PROJECT_ID` | `GCP_AUTH_JSON`、`GCP_PROJECT_ID`、`GCP_BOOTSTRAP_SERVICE_ACCOUNT`、`GCP_AUTH_KEY_ID` |
| 是否需要改组织策略 | 否 | 是（见 4.3），用完必须改回 |
| 有效期 | 约 1 小时（GCP token 天然过期） | 长期有效的 SA key，**必须**在 bootstrap apply 成功后立即用 `revoke` 吊销 |
| 触发方式 | `GCP_BOOTSTRAP_ACTION=write \| check` | 同上，外加 `GCP_BOOTSTRAP_ACTION=revoke` |

### 4.2 专用 Bootstrap Service Account

`--auth-json` 不复用任何已有账号，而是为每个环境创建一个专用、职责单一的 Service Account：

- 账号 ID：`gcp-bootstrap-<env>`（如 `gcp-bootstrap-uat`）
- 授予的角色，与 Terraform `bootstrap/identity` 模块里 `service_account_roles` 变量的默认值完全一致（详见 4.4），**只有这 4 个，不给 Owner/Editor**：

  | 角色 | 用途 |
  |---|---|
  | `roles/iam.workloadIdentityPoolAdmin` | 创建 WIF Pool / Provider |
  | `roles/iam.serviceAccountAdmin` | 创建 deploy Service Account、设置其 IAM policy |
  | `roles/resourcemanager.projectIamAdmin` | 给 deploy Service Account 授予项目级角色 |
  | `roles/serviceusage.serviceUsageAdmin` | 启用 Bootstrap 阶段需要的平台 API |

`ensure_bootstrap_service_account()` 是幂等的：SA 不存在则创建并启用，存在则只确保已启用，然后无条件补齐这 4 个角色绑定。

### 4.3 组织策略约束：`iam.disableServiceAccountKeyCreation`

实测确认该组织策略在 Organization `744119519286` 上是 `enforced: true`：

```
gcloud resource-manager org-policies describe iam.disableServiceAccountKeyCreation \
  --organization=744119519286 --effective
booleanPolicy:
  enforced: true
```

这意味着**默认无法**在任何项目下创建 SA key，包括给刚创建的 `gcp-bootstrap-<env>` 生成 key。`--auth-json` 的 `preflight_key_creation_policy()` 会在真正尝试建 key 之前，先用 `--effective` 读取该项目上的生效策略；如果仍是 enforced，直接失败并打印精确的修复步骤（而不是让用户在几层 API 错误里猜）：

```bash
# 临时豁免（需要 roles/orgpolicy.policyAdmin，项目 Owner 默认没有这个角色）
cat > /tmp/allow-sa-key.yaml <<'YAML'
name: projects/<PROJECT_ID>/policies/iam.disableServiceAccountKeyCreation
spec:
  rules:
  - enforce: false
YAML
gcloud org-policies set-policy /tmp/allow-sa-key.yaml

# ...执行 --auth-json write / revoke...

# Bootstrap 和 revoke 完成后必须改回组织默认值
gcloud org-policies delete iam.disableServiceAccountKeyCreation --project=<PROJECT_ID>
```

这是一个只有拥有 `roles/orgpolicy.policyAdmin` 的账号才能做的操作，project Owner 角色不够——这一点在设计里被显式记录下来，避免误以为"用 Owner 账号跑脚本就一定能成功"。

同时建议为一次性 key 配置组织策略 `constraints/iam.serviceAccountKeyExpiryHours`，作为吊销步骤失败时的硬性兜底（key 到期自动失效）。

### 4.4 一次性 key 的完整生命周期

`write_auth_json()`：

1. 在 `mktemp -d` 生成的 `0700` 临时目录里、`umask 077` 下调用 `gcloud iam service-accounts keys create` 生成 key 文件，全程不落地到用户目录或 CI 工作区之外。
2. 用 `jq` 校验 key 内容：`.type == "service_account"`、`.project_id` 与目标项目一致、`.client_email` 与目标 SA 一致——防止意外写入一把指向错误项目/账号的 key。
3. 提取 `private_key_id`，和 key JSON 一起，通过 `vault kv put`（整体替换，不是 patch）写入 `GCP_AUTH_JSON`（原始 JSON 字符串）、`GCP_PROJECT_ID`、`GCP_BOOTSTRAP_SERVICE_ACCOUNT`、`GCP_AUTH_KEY_ID` 四个字段——一次 `kv put` 会替换整个 secret，因此旧的 `GCP_ACCESS_TOKEN`（如果之前用过 token 模式）会被自动清除，保证同一时刻只存在一种 bootstrap 凭据。
4. 立即 `rm -rf` 临时目录并清除 `trap`，key 文件在磁盘上的存活时间被压缩到最短。

`revoke_auth_json()`（bootstrap apply 成功后必须执行）：

1. 从 Vault 读回当前记录，取出 `GCP_BOOTSTRAP_SERVICE_ACCOUNT` 和 `GCP_AUTH_KEY_ID`。
2. `gcloud iam service-accounts keys delete <key_id>` 删除这把 key（按 `private_key_id` 精确匹配，不会误删其他 key）。
3. `gcloud iam service-accounts disable <sa>` 禁用整个 bootstrap SA（即使 key 删除失败，SA 也无法再被使用）。
4. 销毁 Vault 中这个路径的**全部历史版本**（`vault kv metadata delete` / `DELETE kv/metadata/<path>`），而不仅仅是删除当前版本——KV v2 的软删除只是打标记，历史版本仍能被读到，必须连元数据一起销毁。
5. 重新写入 Vault，只保留 `GCP_PROJECT_ID` 一个字段，方便下次重新 bootstrap 时复用同一路径。

`check:auth_json` 校验 `GCP_AUTH_JSON` 是合法的 `service_account` 类型 JSON 且 `project_id` 匹配，`GCP_PROJECT_ID` 字段一致，用于 CI 里的只读自检，不需要真的解出 key 内容。

### 4.5 命令示例

```bash
export VAULT_ADDR=https://vault.svc.plus   # 已 vault login 或设置 VAULT_TOKEN
gcloud config set account <项目 Owner>

# 一次性生成并写入
GCP_ENVIRONMENT=uat GCP_ACCOUNT_ID=xworktech GCP_PROJECT_ID=xwork-open-platform-uat \
bash scripts/gcp/bootstrap_gcp_auth_kv.sh --auth-json

# 只读校验（CI 里用）
GCP_BOOTSTRAP_ACTION=check GCP_ENVIRONMENT=uat GCP_ACCOUNT_ID=xworktech \
GCP_PROJECT_ID=xwork-open-platform-uat bash scripts/gcp/bootstrap_gcp_auth_kv.sh --auth-json

# bootstrap apply 成功后立即吊销
GCP_BOOTSTRAP_ACTION=revoke GCP_ENVIRONMENT=uat GCP_ACCOUNT_ID=xworktech \
GCP_PROJECT_ID=xwork-open-platform-uat bash scripts/gcp/bootstrap_gcp_auth_kv.sh
```

已用桩（stub）`gcloud`/`vault` 可执行文件跑过完整行为测试：策略未豁免时的失败路径、write 成功路径、check 通过、revoke 清理、token 模式不受影响、非法 action、非法参数——共 7 个场景全部符合预期。

## 5. IaC 渲染管线：按 manifest 条件化生成资源

在完整平台 manifest（`open-platform-<env>.yaml`）之外，新增了一个只声明 Spot VM 的最小验证 manifest，用来在不触碰 network/Artifact Registry/Cloud Run 的前提下，端到端验证"deploy SA 能否通过 WIF 真正创建一个 GCP 资源"。为此对渲染管线做了条件化改造。

### 5.1 `scripts/generate.py` 的开关推导

```python
enable_network            = bool(global_config.get("network_name"))
enable_artifact_registry  = bool(global_config.get("artifact_registry_id"))
enable_cloud_run          = bool(global_config.get("cloud_run_service_name"))
```

并加入一致性校验（避免声明不完整导致渲染出无效 Terraform）：

- 声明了 `nodes` 或 `spot_vms` 但没有 `network_name` → `SystemExit`；
- `enable_network` 为真但没有 `subnet_cidr` → `SystemExit`；
- `enable_artifact_registry` 为真但没有 `artifact_registry_location` → `SystemExit`；
- `enable_cloud_run` 为真但没有 `cloud_run_image` → `SystemExit`。

`vault_machine_type` / `vault_image` 改为 `.get(...)` 带默认值，最小 manifest 不必声明 Vault 相关配置。

### 5.2 模板条件渲染

`templates/open-platform.tf.j2`：

```jinja
{% if enable_network %}
module "network" { ... }
{% endif %}
{% if enable_artifact_registry %}
module "artifact_registry" { ... }
{% endif %}
{% if enable_cloud_run %}
module "cloud_run" { ... }
{% endif %}
```

`platform_runtime` 输出里的 `cloud_run_uri` 相应改为条件值：`enable_cloud_run` 为假时输出 `null`，而不是引用一个不存在的 module。

`templates/variables.tf` 里 `network_name`、`subnet_cidr`、`artifact_registry_location`、`artifact_registry_id`、`cloud_run_service_name`、`cloud_run_image` 从必填 `string` 改为 `string`、`default = null`，配合上面的开关使用。

### 5.3 最小 Spot 验证 manifest

新建 `gitops` 下的独立 manifest（而不是复用完整平台 manifest 里的 `spot_vms` 字段），保证"只创建一个可丢弃的验证资源"这件事和"平台正式资源"在 GitOps 声明层面就是两个完全独立的文件：

`resources/xworktech.com/uat/gcp/spot-validation-uat.yaml`：

```yaml
global:
  network_name: spot-validation-uat
  subnet_cidr: 10.61.0.0/24
spot_vms:
  - name: oidc-spot-validation-uat
    zone: asia-east1-a
    machine_type: e2-micro
    image: debian-12
    labels:
      owner: platform-ops
      purpose: oidc-e2e-validation
      ttl: disposable
```

原 `open-platform-uat.yaml` 里的 `spot_vms` 块已移除，Spot 验证资源只在这一个文件里管理。触发方式是把它作为 `gcp-iac-pipeline.yml` 的 `gcp_resource_manifest` 输入覆盖默认路径，`deploy_action=plan|apply|destroy` 均可独立对这一个最小 state 操作，不会 plan 到完整平台栈。

### 5.4 deploy SA 只新增一个角色

按照"最小 manifest，而不是给 deploy SA 补齐一整套角色"的思路，`bootstrap/identity/main.tf` 的 `deploy_service_account_roles` 只新增了 `roles/compute.networkAdmin`（Spot VM 需要在新建的验证子网里创建实例）：

```hcl
variable "deploy_service_account_roles" {
  type = set(string)
  default = [
    "roles/artifactregistry.writer",
    "roles/compute.instanceAdmin.v1",
    "roles/compute.networkAdmin",   # 新增：仅为 Spot 验证 manifest 需要的网络创建权限
    "roles/run.admin",
    "roles/serviceusage.serviceUsageConsumer",
  ]
}
```

### 5.5 平台 API 启用前移到 Bootstrap

为了让日常 deploy SA 不需要 `serviceusage.services.enable` 这种偏管理性的权限，把平台用到的 API 启用整体前移到 Bootstrap 阶段的 Terraform（`bootstrap/identity/main.tf` 新增 `platform_services` 变量 + `google_project_service.platform` for_each 资源：`artifactregistry`、`compute`、`logging`、`monitoring`、`run`、`secretmanager` 六个 API），并从 `modules/project/main.tf` 里删除了原来 8 个 `google_project_service` 资源，只留一条注释说明"API 由 bootstrap/identity 启用"。效果：runtime deploy SA 的角色列表里只保留 `serviceusage.serviceUsageConsumer`（消费已启用的 API），不再需要任何"启用 API"权限。

## 6. Terraform State 按 manifest 隔离

多个 manifest（完整平台 + 最小 Spot 验证）如果共用同一个 state key，`terraform plan` 会把彼此声明之外的资源识别为"待删除"，非常危险。`gcp-iac-pipeline.yml` 因此新增了 `state_workspace` 的推导逻辑：

```bash
# 使用默认 manifest（完整平台）→ workspace 固定为 "platform"
# 使用自定义 manifest（如 spot-validation-uat.yaml）→ workspace = manifest 文件名（去掉 .yaml）
state_workspace="platform"   # 默认路径分支
state_workspace="$(basename "${manifest}" .yaml)"   # 自定义 manifest 分支
# 校验命名合法性
[[ "${state_workspace}" =~ ^[a-z0-9][a-z0-9-]*$ ]]
```

Terraform backend 的 `key=` 从原来写死的 `.../platform/terraform.tfstate` 改为：

```
terraform/${DEPLOY_ENV}/${project_id}/gcp-cloud/${GCP_ACCOUNT_ID}/${state_workspace}/terraform.tfstate
```

效果：`open-platform-uat.yaml`（完整平台栈）用 `.../platform/terraform.tfstate`，`spot-validation-uat.yaml` 用 `.../spot-validation-uat/terraform.tfstate`，两者物理隔离，互不感知对方声明的资源，`plan`/`apply`/`destroy` 都可以独立对其中一个操作。

## 7. Runtime OIDC/WIF 认证链路（现状，未改动）

日常 `gcp-iac-pipeline.yml`（及其余 LandingZone/Account/Resources/Master matrix workflow）通过 `configure-gcp-oidc` composite action 认证：

```
GitHub Actions OIDC token
  → Vault JWT role: github-actions-platform-ops-toolkit-<env>-gcp-oidc-<account>
  → Vault 读出: kv/<env>/platform/oidc/<account>（provider、deploy SA email、audience、project_id）
  → google-github-actions/auth@v2，用 Bootstrap 阶段创建的 WIF Provider 换取短期凭据
```

这一段链路本身在此前已经落地（不是本轮改动），本轮工作是确保它的"上游"——Bootstrap 阶段——能以一次性凭据、而不是长期凭据的方式把 WIF Provider 和 deploy SA 创建出来，并保证 runtime 侧读取的 `kv/<env>/platform/oidc/<account>` 始终不含私钥（Terraform 输出里只有 provider resource name 和 SA email，没有任何 key material）。

## 8. Bootstrap Workflow（`gcp-oidc-bootstrap.yml`）现状

`workflow_dispatch` 输入 `environment`（uat/prod）、`action`（plan/apply）。主要步骤：

1. 分别 checkout `gitops`（sparse-checkout 仅取 `github-actions-oidc.yaml`）和 `iac_modules`，均按固定 commit SHA pin 住（`ref:` / `iac_ref:`），避免 Bootstrap 意外拉到未审查的最新代码。
2. `resolve_github_oidc_config.sh` 解析 GitOps 声明的 audience/organization_id 等。
3. `hashicorp/vault-action@v3` 用 role `github-actions-platform-ops-toolkit-<env>-gcp-bootstrap-<account>` 读取 `kv/data/CICD/<env>/gcp-bootstrap/<account>`（`GCP_ACCESS_TOKEN` | `GCP_PROJECT_ID`）和 `kv/data/CICD/<env>/iac_state`（Terraform state backend 凭据）。
4. 校验 Vault 里的 `GCP_PROJECT_ID` 与 GitOps 声明一致。
5. 用 `cloudresourcemanager.googleapis.com:testIamPermissions` 预检 `iam.serviceAccounts.create`、`iam.serviceAccounts.setIamPolicy`、`resourcemanager.projects.setIamPolicy`、`serviceusage.services.enable` 四项权限（WIF Pool/Provider 相关的两项权限因为目标 Pool 还不存在，无法预检，只能等 apply 时由 IAM API 校验）。
6. 写 Terraform tfvars，对 `bootstrap/identity` 模块执行 `init/fmt/validate/plan/apply`。
7. 捕获 `provider_resource_name` / `service_account_email` 输出。
8. 用刚创建的 WIF 通过 `google-github-actions/auth@v2` 做自检认证，`gcloud projects describe` 验证可访问，并显式验证 UAT 身份不能访问 PROD 项目。
9. `apply` 成功后把 OIDC 输出（不含私钥）POST 到 `kv/<env>/platform/oidc/<account>`。

**尚未完成**：这个 workflow 目前只消费 `GCP_ACCESS_TOKEN`（token 模式），还没有改造成支持读取 `GCP_AUTH_JSON` 并在 Job 内换取短期 token，也没有在 apply 成功后自动调用第 4 节的 `revoke` 逻辑。这是第 4 节功能落地后的下一步（见第 10 节）。

## 9. 变更清单与合并状态

| 仓库 | 分支/PR | 内容 | 状态 |
|---|---|---|---|
| `gitops` | PR #274 | 修正 GCP 项目 ID（`xworktech-open-platform-*` → `xwork-open-platform-*`）；新增 `spot-validation-uat.yaml` 最小验证 manifest；`open-platform-uat.yaml` 移除内嵌 `spot_vms` | ✅ 已合并（main `b7268fe`） |
| `iac_modules` | PR #324 | 修正项目 ID；`deploy_service_account_roles` 新增 `compute.networkAdmin`；新增 `platform_services` API 前移；模板/变量/generate.py 条件渲染改造 | ✅ 已合并（main `2ba98f3`） |
| `platform-ops-toolkit` | PR #855 | 修正项目 ID；`iac_ref`/`ref:` 更新为上述两个新 SHA；`gcp-iac-pipeline.yml` 按 manifest 隔离 state workspace | ✅ 已合并（main 含 `a77f3e2` 与合并提交 `dcb679f`） |
| `platform-ops-toolkit` | PR #870 | `bootstrap_gcp_auth_kv.sh` 新增 `--auth-json`/`revoke`；contract test 新增对应断言；howto 文档新增"一次性 Admin SA key"章节 | ✅ 已合并（main `ccf892f`） |
| Epic `#804` | Issue body | 新增"凭据分层约定"章节，明确 Bootstrap 允许一次性 Admin JSON key、日常流水线禁止任何固定 JSON key | ✅ 已更新（GitHub 上直接编辑生效） |

### 关于合并方式的说明

由于本次工作在一个隔离的云端会话中完成，该会话的 git 出站请求被仓库授权代理拒绝（`access denied by the git proxy: ... is not in this session's authorized repository set`），无法直接 `git push` 到这三个仓库。所有实际的 PR 提交、CI 检查、合并动作，都是通过交付到用户本机的可执行脚本（`~/Downloads/gcp-auth-json-pr.sh`）、由用户在本地终端运行 `gh` CLI 完成的：clone → 应用 patch → 本地跑 contract test → push → `gh pr create` → 轮询 CI checks → 全绿后 squash merge。四项改动（gitops #274、iac_modules #324、platform-ops-toolkit #855、platform-ops-toolkit #870）均已按此方式合并完毕。

## 10. 尚未完成的工作

1. **`gcp-oidc-bootstrap.yml` 消费 `GCP_AUTH_JSON`**：目前 workflow 只读 `GCP_ACCESS_TOKEN`。下一步需要在 workflow 里判断 Vault 记录中是否存在 `GCP_AUTH_JSON`，若存在则用 `google-github-actions/auth@v2` 的 `credentials_json` 输入（`create_credentials_file: false`，不落盘）换取短期 token，apply 成功后在同一个 Job 内调用第 4 节的 `revoke_auth_json` 逻辑（或等价的 Terraform/gcloud 步骤）。这是一个独立 PR，不在本轮 `--auth-json` 助手脚本 PR 的范围内。
2. **真实的 UAT E2E 验证从未在任何自动化环境里跑过**：本次工作在的云端沙箱既不能访问 Terraform provider registry（`registry.terraform.io` 等被出站策略拦截），也无法代替用户触发 GitHub Actions workflow，因此"Bootstrap plan → apply → runtime plan → Spot VM apply → destroy"这条链路目前只完成了**静态/离线验证**（模板渲染逻辑、contract test、`terraform fmt -check`、桩 `gcloud`/`vault` 的行为测试），真实的 `terraform plan`/`apply` 结果需要用户在本机触发 workflow 后回填。
3. **完整 E2E 执行顺序**（`feat/gcp-bootstrap-auth-json` 合并后按序执行）：
   - 用 token 或 `--auth-json` 模式刷新 `kv/CICD/uat/gcp-bootstrap/xworktech`；
   - 触发 `GCP OIDC Bootstrap`：`environment=uat`，`action=plan` → 确认预检权限齐全、plan 只包含 WIF Pool/Provider/deploy SA/IAM binding；
   - 同参数 `action=apply` → 确认 WIF 认证自检通过、UAT 无法访问 PROD、`kv/uat/platform/oidc/xworktech` 已写入、（若使用 `--auth-json`）一次性凭据已吊销；
   - 触发 `gcp-iac-pipeline.yml`：`gcp_resource_manifest=resources/xworktech.com/uat/gcp/spot-validation-uat.yaml`，`deploy_action=plan` → 确认只 plan 网络 + 一个 Spot 实例，state workspace 为 `spot-validation-uat`；
   - `deploy_action=apply` → 确认真实创建的实例 `provisioningModel == SPOT`；
   - 验证完成后 `deploy_action=destroy` 清理该一次性验证资源；
   - 回填结果到 `#805`/`#806`，并按 Epic `#804` 的完成定义逐项勾选。
4. **PROD 环境**：本方案的所有改动对 UAT/PROD 是对称的（PROD 项目 ID 同样已修正为 `xwork-open-platform-prod`），但按 Epic 约定，PROD 的 bootstrap/apply 必须经过受保护 GitHub Environment 审批，本轮工作未涉及 PROD 的实际执行。

## 11. 关键路径速查

| 项目 | 值 |
|---|---|
| Organization | `744119519286`（xworktech.com） |
| UAT 项目 ID | `xwork-open-platform-uat` |
| PROD 项目 ID | `xwork-open-platform-prod` |
| Bootstrap 凭据 Vault 路径 | `kv/CICD/<env>/gcp-bootstrap/<account>` |
| Terraform state 凭据 Vault 路径 | `kv/CICD/<env>/iac_state` |
| Runtime WIF 输出 Vault 路径 | `kv/<env>/platform/oidc/<account>` |
| Bootstrap Vault JWT role | `github-actions-platform-ops-toolkit-<env>-gcp-bootstrap-<account>` |
| Runtime Vault JWT role | `github-actions-platform-ops-toolkit-<env>-gcp-oidc-<account>` |
| Bootstrap 专用 SA（`--auth-json`） | `gcp-bootstrap-<env>@<project>.iam.gserviceaccount.com` |
| Bootstrap Terraform 模块 | `iac_modules/terraform-hcl-standard/gcp-cloud/bootstrap/identity` |
| Runtime Terraform 模板 | `iac_modules/terraform-hcl-standard/gcp-cloud/templates/open-platform.tf.j2` |
| 完整平台 manifest | `gitops/resources/xworktech.com/<env>/gcp/open-platform-<env>.yaml` |
| 最小 Spot 验证 manifest | `gitops/resources/xworktech.com/uat/gcp/spot-validation-uat.yaml` |
| Bootstrap workflow | `platform-ops-toolkit/.github/workflows/gcp-oidc-bootstrap.yml` |
| Runtime workflow | `platform-ops-toolkit/.github/workflows/gcp-iac-pipeline.yml` |
| 一次性凭据助手脚本 | `platform-ops-toolkit/scripts/gcp/bootstrap_gcp_auth_kv.sh` |
| Contract test | `platform-ops-toolkit/.github/scripts/tests/gcp_oidc_bootstrap_contract_test.sh` |
| 操作手册 | `platform-ops-toolkit/docs/howto/GCP-OIDC-Bootstrap-howto.md` |
