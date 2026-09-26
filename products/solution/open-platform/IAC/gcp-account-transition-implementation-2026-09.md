# GCP 账号切换迁移实施文档（2026-09）

## 目标与执行边界

使用当前 `gcloud` 登录的 `haitaopan@xworktech.com`，在 GitOps 声明的项目中无状态重部署
Cloud Run 服务，并将现有域名路由 upstream 对齐到新服务：

| 环境 | GCP Project ID | 区域 | Cloud Run 服务 |
| --- | --- | --- | --- |
| UAT | `open-platform-uat` | `asia-east1` | `uat-accounts`、`uat-billing-service`、`uat-content-service` |
| PROD | `open-platform-prod` | `asia-east1` | `prod-accounts`、`prod-billing-service`、`prod-content-service` |

域名和 DNS 记录保持现有值，只更新 GitOps 的 Cloud Run upstream，再重新部署消费这些 upstream
的 Cloudflare Workers/Pages。此次不复制旧 revision、流量权重、实例状态或业务数据，不执行
数据库迁移。截图中的旧服务位于显示为 `xworktech` 的项目、区域 `asia-northeast1`；它们不作为
部署源。

GCP 项目管理员邮箱与 CI 部署 Service Account 是两种身份。`GCP_SERVICE_ACCOUNT_EMAIL`
不能填个人邮箱；如果只变更人员管理员，原 CI Service Account 可以不变，但它必须对目标项目
具备部署权限并由目标项目的 WIF provider 信任。若要轮换 CI 身份，作为这次实施中的单独步骤
创建/授权新 Service Account，并从 GitOps OIDC bootstrap 输出取得 provider 和账号邮箱。

## 实施前提

本机 `gcloud auth list` 在不同终端输出过不同 ACTIVE 账号。开始每次操作前都以
`gcloud config get-value account` 与 `gcloud auth list` 的现场输出为准。工具终端当前活动账号
是 `haitaopan@xworktech.com`，当前配置的默认 project 为 `open-platform-prod`。旧账号
`haitaopanhq@gmail.com` 仅保留用于旧项目只读盘点和回退，不作为新项目部署身份。

Cloud Run 的默认 `run.app` URL 含项目编号。新项目编号和新服务 URL 需在获准访问并创建服务后
读取，不能从项目 ID 推算。GitOps 中现有 `1004637461064.asia-northeast1.run.app` upstream
属于旧部署；部署完成后必须更新为目标服务的真实 URL，再执行 Worker/路由切换。

## 0. 现有服务只读基线

当前 `gcloud` configuration 已核实为：

```text
configuration: default (active)
account: haitaopan@xworktech.com
project: open-platform-prod
```

这只说明本机默认上下文已经切到新账号和 PROD 目标项目；实际服务操作仍显式传入
`--project`、`--region`，避免被默认 project 误导。

`haitaopanhq@gmail.com` 在本次盘点可见项目如下：

| Project ID | 显示名 | Project number |
|---|---|---|
| `xworktech` | xworktech | `1004637461064` |
| `xzerolab-480008` | xzerolab | `266500572462` |

六个服务都在 `xworktech / asia-northeast1`；每项的 Ingress 为 `all`，IAM invoker 含
`allUsers`，100% 流量指向最新 Ready revision，运行身份均为
`1004637461064-compute@developer.gserviceaccount.com`。

| 服务 | 当前 status URL | 最新 Ready revision（UTC） | 镜像 tag |
|---|---|---|---|
| `prod-accounts` | `https://prod-accounts-whjqcl3zcq-an.a.run.app` | `prod-accounts-00071-n2x`（09-20 05:46） | `v2026.09.13-r4` |
| `prod-billing-service` | `https://prod-billing-service-whjqcl3zcq-an.a.run.app` | `prod-billing-service-00072-85q`（09-20 05:48） | `v2026.09.13-r4` |
| `prod-content-service` | `https://prod-content-service-whjqcl3zcq-an.a.run.app` | `prod-content-service-00075-ct4`（09-22 04:15） | `v2026.09.22-r8` |
| `uat-accounts` | `https://uat-accounts-whjqcl3zcq-an.a.run.app` | `uat-accounts-00256-kk2`（09-25 19:52） | `daily-build-2026.09.25-r1` |
| `uat-billing-service` | `https://uat-billing-service-whjqcl3zcq-an.a.run.app` | `uat-billing-service-00248-stf`（09-25 19:54） | `daily-build-2026.09.25-r1` |
| `uat-content-service` | `https://uat-content-service-whjqcl3zcq-an.a.run.app` | `uat-content-service-00250-2kg`（09-25 19:53） | `daily-build-2026.09.25-r1` |

运行时环境变量只记录名称。Accounts 使用 Supabase/internal token、账号 bootstrap/auth、GitHub
OAuth、租户、Bridge、SMTP、Stripe、XConnect 等配置；其 SMTP Secret Manager 引用为
`smtp-username:latest` 和 `smtp-password:latest`，UAT 另有两个 XConnect gateway Xray 字段。
Billing 使用 Supabase/internal token、连接池设置和 `BILLING_INGEST_MODE`。Content 使用
Supabase/internal token 与 `KNOWLEDGE_REPO_PATH/URL/REF`。没有读取或记录任何环境变量值。

新账号已按目标创建 `open-platform-uat` 和 `open-platform-prod`：

| Project ID | Project number | 访问结果 |
|---|---:|---|
| `open-platform-uat` | `142822217216` | 新账号可读 |
| `open-platform-prod` | `986070475391` | 新账号可读 |

PROD 目标项目在 `asia-east1` 当前没有 Cloud Run 服务，也没有 Artifact Registry 仓库；UAT 新项目
已创建且目标 API 已启用，因此服务/仓库清单仍为空，等待无状态部署。此前 GitOps 中的
`xworktech-open-platform-uat/prod` 已确认是错误项目 ID，已修正为 `open-platform-uat` /
`open-platform-prod`。UAT runtime KV 已完成 legacy key 清理（version `10`，仅保留 WIF provider
和 deploy Service Account）；PROD 等 bootstrap 完成后再执行同样替换。

## 0.1 迁移脚本 pre-check 阶段

`scripts/gcp/gcp_account_migration.sh` 的 `plan` 是只读检查；`prepare` 会在任何账单/API
变更前先验证 Vault，并解析一个短期 GCP token。默认 `--token-source=auto` 按以下顺序尝试：
显式 `GCP_ACCESS_TOKEN`、ADC、当前 `gcloud` 活动账号 token。脚本不会把 token 写入参数、日志
或 Git；因此 ADC 失效时，只要当前 `gcloud` 账号仍有效，流程可以非交互式继续。

先设置当前目标参数：

```bash
cd /Users/shenlan/workspaces/ai-workspace-infra/platform-ops-toolkit

export GCP_ENVIRONMENT=uat
export GCP_PROJECT_ID=open-platform-uat
export GCP_REGION=asia-east1
export GCP_ACCOUNT_ID=xworktech
export GCP_BILLING_ACCOUNT=01180B-F40C7F-BADE24
export GCP_GITOPS_MANIFEST=/Users/shenlan/workspaces/ai-workspace-infra/gitops/resources/xworktech.com/uat/gcp/open-platform-uat.yaml
export GCP_OIDC_CONFIG=/Users/shenlan/workspaces/ai-workspace-infra/gitops/resources/xworktech.com/uat/gcp/github-actions-oidc.yaml
export VAULT_ADDR=https://vault.svc.plus
```

执行 pre-check：

```bash
scripts/gcp/gcp_account_migration.sh plan
```

推荐先直接运行 `plan`。若输出 `gcp_bootstrap_token=available (source=auto)`，不需要额外
建立 ADC，可直接执行。若本机 ADC 已失效，但管理员已经在受控终端取得一个仍有效的短期
OAuth token，可以显式传入；脚本会把该 token 写入临时权限文件，让项目查询、账单/API 操作和
bootstrap 全部使用同一个 token，不依赖失效的本地 ADC：

```bash
GCP_ACCESS_TOKEN="$SHORT_LIVED_TOKEN" \
  scripts/gcp/gcp_account_migration.sh prepare \
  --token-source=explicit \
  --skip-api-enable
```

`SHORT_LIVED_TOKEN` 只存在于当前 shell 环境和临时文件，命令完成后自动删除；不要把实际值写入
聊天、GitHub、文档或 shell history。没有有效短期 token 时，按下方 `--no-browser` 流程重新授权。

如果 `plan` 已显示 token 可用，且账单/API 尚未完成，再执行准备阶段：

```bash
scripts/gcp/gcp_account_migration.sh prepare --link-billing
```

如果组织策略要求 bootstrap 必须使用 ADC，可显式切换严格模式；出现
`invalid_grant: Token has been expired or revoked` 或 ADC scope 未 consent 时，先清理本机
失效 ADC 并用无浏览器流程重新授权 `cloud-platform` scope：

```bash
gcloud auth application-default revoke --quiet
gcloud auth application-default login \
  --no-browser \
  --scopes=https://www.googleapis.com/auth/cloud-platform
```

如果命令进入 remote bootstrap 提示，请在另一台可打开浏览器的终端运行它打印出的完整
`--remote-bootstrap` 命令，在浏览器中选择 `haitaopan@xworktech.com` 并同意
`cloud-platform` scope，再把命令输出复制回原终端。不要把 URL、授权码或 token 发到聊天中。
严格 ADC 模式验证：

```bash
gcloud auth application-default print-access-token >/dev/null \
  && echo 'GCP_ADC_TOKEN=available'
VAULT_ADDR="$VAULT_ADDR" vault token lookup >/dev/null \
  && echo 'VAULT_SESSION=available'
```

ADC 和 Vault 都通过后，以严格 ADC 模式执行：

```bash
scripts/gcp/gcp_account_migration.sh prepare --link-billing --token-source=adc
```

账单/API 已经完成时，重复执行是幂等的；如果只需要绑定账单并启用 API、不写 bootstrap KV，
可使用 `--skip-bootstrap`。如果只需要重新写 bootstrap KV，可使用 `--skip-api-enable`。

2026-09-26 实际执行结果：活动账号为 `haitaopan@xworktech.com`；UAT 和 PROD 的
`prepare --link-billing --token-source=auto` 均成功，账单均为 `01180B-F40C7F-BADE24`，
所需 API 各 5 项全部启用。`kv/CICD/uat/gcp-bootstrap/xworktech` 与
`kv/CICD/prod/gcp-bootstrap/xworktech` 均已写入 version `2`。复核只读取 KV 键名，当前均为
`GCP_ACCESS_TOKEN,GCP_PROJECT_ID`，没有把 token 写入记录。下一步运行 UAT OIDC bootstrap
workflow；provider 和 deploy Service Account 在 workflow 成功前保持未创建状态。

## 1. 授予新管理员访问

状态：绑定命令已执行（用户确认）；新账号已可读取真实 UAT/PROD 目标项目。旧账号仍保留作为
短期回退入口，暂不撤销。

如果当前要用 `haitaopanhq@gmail.com` 盘点旧服务，`gcloud auth login` 显示
`Re-using locally stored credentials` 时，说明没有重新进行 OAuth。使用 `--force` 后再切换并
核对活动账号：

```bash
gcloud auth login --force haitaopanhq@gmail.com
gcloud config set account haitaopanhq@gmail.com
gcloud config get-value account
gcloud auth list
```

如果 `auth list` 中没有期望账号，检查当前 configuration：

```bash
gcloud config configurations list
gcloud config list
```

需要隔离配置时，新建 configuration 后再登录；不要撤销另一个账号已保存的凭据：

```bash
gcloud config configurations create gcp-account-inventory
gcloud config configurations activate gcp-account-inventory
gcloud auth login --force haitaopanhq@gmail.com
gcloud config set account haitaopanhq@gmail.com
```

此前使用旧账号尝试绑定时，两个项目曾返回
`does not have permission to access ... getIamPolicy (or it may not exist)`。本次步骤 1 已由有
权限的管理员完成；后续以新账号的只读验证结果作为准入条件。不要用旧账号重复覆盖 IAM policy，
也不要未经确认改绑到名字相近的项目。

## 1.1 清理新账号下无关项目

迁移目标项目已统一为 `open-platform-uat` 和 `open-platform-prod`。截图中的以下项目属于
新账号下的其他项目，按项目显示名核对后的确切 Project ID 如下：

| 显示名 | Project ID | 处理状态 |
|---|---|---|
| POC project | `cs-poc-nvea0hpeuovvhd20lrhz0fy` | 已清理，复核列表中已不存在 |
| XWork Open Platform UAT（旧项目） | `xwork-open-platform-uat` | 已清理，复核列表中已不存在 |
| nonprod | `cs-project-grymwqlt` | 已清理，复核列表中已不存在 |
| central-logging-monitoring | `cs-project-leatk5hv` | 已清理，复核列表中已不存在 |
| My First Project | `crypto-will-508602-m0` | 已清理，复核列表中已不存在 |

清理前必须确认当前账号是新账号，并先做只读预览。以下命令已用于本次清理复核：

```bash
gcloud config set account haitaopan@xworktech.com

projects_to_delete=(
  cs-poc-nvea0hpeuovvhd20lrhz0fy
  xwork-open-platform-uat
  cs-project-grymwqlt
  cs-project-leatk5hv
  crypto-will-508602-m0
)

for project_id in "${projects_to_delete[@]}"; do
  gcloud projects describe "$project_id" \
    --format='table(projectId,name,projectNumber,lifecycleState)'
done
```

确认预览结果与上表完全一致后，逐个执行删除；不要使用 `--quiet`，让 `gcloud` 对每个项目
再次显示确认提示：

```bash
for project_id in "${projects_to_delete[@]}"; do
  gcloud projects delete "$project_id"
done
```

绝对不要删除本次迁移目标：

```text
open-platform-uat
open-platform-prod
```

执行完成后回填验证：

```bash
gcloud projects list \
  --filter='projectId:(cs-poc-nvea0hpeuovvhd20lrhz0fy OR xwork-open-platform-uat OR cs-project-grymwqlt OR cs-project-leatk5hv OR crypto-will-508602-m0)' \
  --format='table(projectId,lifecycleState)'
```

该清理步骤不改变 GitOps、Vault、Cloud Run 或域名配置；它只移除新账号下与迁移无关的 GCP
项目。删除结果需在本节记录为“已提交删除”或“保留及原因”。

历史执行命令模板：

```bash
for project in open-platform-uat open-platform-prod; do
  gcloud projects add-iam-policy-binding "$project" \
    --member='user:haitaopan@xworktech.com' \
    --role='roles/browser'
done
```

`roles/browser` 只提供项目查看，不授予部署权限。要让新用户查看 Cloud Run/镜像，按需授予
`roles/run.viewer` 和 `roles/artifactregistry.reader`。GitHub Actions 应使用 WIF impersonate 的
deploy Service Account；按需给它 Cloud Run 部署、Artifact Registry 读取、目标 runtime service
account impersonation 及 Secret Manager secret 读取权限。避免给个人邮箱宽泛权限，也不要默认授予
`Owner`。

现在切换到新账号并确认两个目标 Project ID 可见。只读核对：

```bash
gcloud projects describe open-platform-uat --format='yaml(projectId,projectNumber,name)'
gcloud projects describe open-platform-prod --format='yaml(projectId,projectNumber,name)'
```

记录 project number（非 Secret），并核对组织归属、账单、启用的 Cloud Run/Artifact Registry API。
如果新账号仍无法看到项目，停止后续 Vault/WIF 操作，回到 IAM 绑定检查。

## 2. 准备目标项目的 WIF 与部署 Service Account

分别检查 GitOps 中 UAT/PROD 的 GCP OIDC 声明：

```text
gitops/resources/xworktech.com/uat/gcp/github-actions-oidc.yaml
gitops/resources/xworktech.com/prod/gcp/github-actions-oidc.yaml
```

先以 `gcp-oidc-bootstrap.yml` 的 `action=plan` 检查声明和 Vault bootstrap 输入。确认项目 ID、
账号标识和环境无误后，再按受控发布流程执行 `action=apply`。PROD 按 GitHub Environment
审批保护执行。Bootstrap 使用短期 ADC/OAuth token，不生成长期 Service Account JSON key。
若现有 WIF/Service Account 已属于正确目标项目且权限完整，复用并验证；不要仅因个人 Gmail
变更而无必要地轮换服务账号。若其仍指向旧项目，则先为目标项目建立新 WIF 与 deploy service
account，并从 bootstrap 输出获取新值。

从成功的 bootstrap 输出/GitOps OIDC 声明取得每个环境的：

- `GCP_WORKLOAD_IDENTITY_PROVIDER`：属于目标项目的 WIF provider resource name；
- `GCP_SERVICE_ACCOUNT_EMAIL`：该环境的 deploy Service Account；
- `GCP_PROJECT_ID` 与 `GCP_REGION`：分别固定为上表值。

确认该 Service Account 有最小化的 Cloud Run 部署、Artifact Registry 读取、所需 Secret Manager
读取权限；WIF principal 仅允许指定仓库、workflow、ref 和 environment。人员邮箱不写入这些字段。

### 2.1 按新项目引导 GitHub OIDC/WIF bootstrap

当前 UAT 缺少 `github-actions/github` provider，且 UAT 项目尚未启用必要 API；PROD provider
存在，但声明的 `github-actions-prod` Service Account 尚未创建。按以下顺序处理：

1. 先为 UAT 绑定账单账号。没有账单账号时，Cloud Run、Artifact Registry、Secret Manager 等
   API 不能启用。绑定后执行：

   ```bash
   gcloud services enable \
     run.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com \
     sts.googleapis.com iamcredentials.googleapis.com \
     --project=open-platform-uat
   ```

2. 将两个 OIDC 声明合并到 GitOps `main`。当前声明已统一使用规范的数字项目号 audience：
   UAT `142822217216`、PROD `986070475391`；这与 `google-github-actions/auth` 的默认 audience
   一致。`gcp-oidc-bootstrap.yml` 已固定到 GitOps 合并提交
   `7b8528e2dad579ec8bd38e743510ee8dc7721c78`，运行 workflow 前仍要确认 ref 没有回退。

3. 管理员在受控终端建立短期 bootstrap 输入。推荐使用短期 ADC token，不生成长期 key：

   ```bash
   gcloud auth application-default login
   export VAULT_ADDR=https://vault.svc.plus
   vault login

   GCP_ENVIRONMENT=uat \
   GCP_ACCOUNT_ID=xworktech \
   GCP_PROJECT_ID=open-platform-uat \
   GCP_EXPECTED_PROJECT_ID=open-platform-uat \
   bash scripts/gcp/bootstrap_gcp_auth_kv.sh
   ```

   该命令只把一次性的 `GCP_ACCESS_TOKEN` 和非敏感校验字段写入
   `kv/CICD/uat/gcp-bootstrap/xworktech`。不得把 token 复制到 GitHub、聊天或文档。

4. 在 GitHub Actions 手动运行 `GCP OIDC Bootstrap`：

   ```text
   environment=uat
   action=plan
   ```

   `plan` 通过后，在受保护的 UAT Environment 再运行 `action=apply`。它会创建 UAT 的
   `github-actions` pool/provider 和 `github-actions-uat` deploy Service Account，并自动将
   provider resource name、Service Account email 写入 `kv/uat/platform/oidc/xworktech`。

5. 将 bootstrap 输出中的两个敏感运行时字段写入 Serverless KV；项目 ID 和区域不写入该 KV，
   workflow 从 GitOps manifest 读取：

   ```bash
   vault kv patch kv/uat/serverless/gcp \
     GCP_WORKLOAD_IDENTITY_PROVIDER='<terraform provider resource name>' \
     GCP_SERVICE_ACCOUNT_EMAIL='<terraform service account email>'
   ```

   用同样流程处理 PROD，但将项目改为 `open-platform-prod`、环境改为 `prod`，并先通过
   GitHub Production Environment 审批。写入后只核对 key 名和 KV version，不输出值：

   ```bash
   vault kv get -format=json kv/uat/serverless/gcp \
     | jq '{version:.data.metadata.version,keys:(.data.data|keys)}'
   vault kv get -format=json kv/prod/serverless/gcp \
     | jq '{version:.data.metadata.version,keys:(.data.data|keys)}'
   ```

Serverless workflow 的 `GCP_PROJECT_ID`、`GCP_REGION` 来自 GitOps GCP manifest；Vault
`kv/<env>/serverless/gcp` 只保存 WIF provider 和 deploy Service Account。bootstrap 的 Vault
写入仍需在目标项目 API 和 WIF plan/apply 完成后执行。

### 2.2 可重复执行的迁移脚本

上述步骤已收敛到 `platform-ops-toolkit/scripts/gcp/gcp_account_migration.sh`。脚本默认只读，
所有目标值通过参数或环境变量传入，不内置项目 ID、账单账号或 Vault token：

```bash
scripts/gcp/gcp_account_migration.sh plan \
  --environment "$GCP_ENVIRONMENT" \
  --project-id "$GCP_PROJECT_ID" \
  --region "$GCP_REGION" \
  --account-id "$GCP_ACCOUNT_ID" \
  --gitops-manifest "$GCP_GITOPS_MANIFEST" \
  --oidc-config "$GCP_OIDC_CONFIG"
```

准备阶段需要显式允许账单绑定；不带 `--link-billing` 时脚本不会修改账单：

```bash
scripts/gcp/gcp_account_migration.sh prepare \
  --billing-account "$GCP_BILLING_ACCOUNT" \
  --link-billing \
  --environment "$GCP_ENVIRONMENT" \
  --project-id "$GCP_PROJECT_ID" \
  --region "$GCP_REGION" \
  --account-id "$GCP_ACCOUNT_ID" \
  --gitops-manifest "$GCP_GITOPS_MANIFEST" \
  --oidc-config "$GCP_OIDC_CONFIG"
```

之后用 `dispatch --bootstrap-action plan`、确认 plan 后再用
`dispatch --bootstrap-action apply`；bootstrap 完成后用 `finalize` 将 provider 和 Service
Account 写入对应的 `kv/<env>/serverless/gcp`。脚本的 `--help` 列出所有可覆盖参数。

## 3. 更新 Vault runtime KV

管理员在受控终端登录 Vault；不要把 token 放进 shell 命令参数、聊天或 Git。先仅核对 key 名、
版本号和目标值，勿输出 Secret 值：

```bash
vault kv get -format=json kv/uat/serverless/gcp \
  | jq '{version:.data.metadata.version, keys:(.data.data|keys)}'
vault kv get -format=json kv/prod/serverless/gcp \
  | jq '{version:.data.metadata.version, keys:(.data.data|keys)}'
```

将各环境 runtime path 更新为（项目 ID 和区域由 GitOps manifest 读取，不写入该运行时 KV）：

| KV path | 必须值 | 来自 |
| --- | --- | --- |
| `kv/uat/serverless/gcp` | `GCP_WORKLOAD_IDENTITY_PROVIDER`、`GCP_SERVICE_ACCOUNT_EMAIL` | UAT OIDC bootstrap 输出 |
| `kv/prod/serverless/gcp` | `GCP_WORKLOAD_IDENTITY_PROVIDER`、`GCP_SERVICE_ACCOUNT_EMAIL` | PROD OIDC bootstrap 输出 |
| GitOps manifest | `project_id`、`region` | 分别为 `open-platform-uat`/`open-platform-prod`、`asia-east1` |

用 Vault KV v2 的 `vault kv patch` 只更新已确认字段；保留同路径的其他 key。写入后再次只读核对
字段是否与 GitOps 一致，并记录 KV version 和 key 名，不记录凭据值。写入由管理员在 Vault
完成；本次代码变更不会代替该步骤。

## 4. UAT 无状态重部署与域名路由对齐

1. 用 GitOps UAT manifest 与 Vault UAT path 核对项目/区域。`serverless-orchestrator.yml` 的
   Cloud Run job 会在认证前比较两者；不一致会失败关闭。
2. 确认 `asia-east1-docker.pkg.dev/open-platform-uat/serverless/` 中存在
   `accounts`、`billing-service`、`content-service` 的同一不可变 release tag 镜像；未发布时
   先通过已有构建发布流程推送目标项目 Artifact Registry。
3. 在 GitHub Actions 手动运行 `serverless-orchestrator.yml`，输入：

   ```text
   operation=deploy
   target_domains=web-saas
   vault_env_path=uat
   tag_ref=<已存在的不可变 release tag>
   deploy_cloudflare=false
   deploy_cloud_run=true
   cloud_run_service=content-service
   ```

   不选 `deploy+migrate`、`destroy`、数据库迁移或 DNS cutover。首个服务验证通过后，重复运行
   `cloud_run_service=accounts` 和 `cloud_run_service=billing-service`。全新部署仍需读取已有运行时
   Supabase URI、应用 token 和服务 Secret；“无状态”表示不迁移旧 Cloud Run 运行状态，不表示
   不需要运行时配置。
4. 在目标项目核实三个 `uat-*` 服务的项目、区域、镜像、Ready revision、服务账号、环境
   配置、Secret 引用、Ingress 和实例设置；运行健康探针与应用日志检查。然后读取每个新服务的
   真实 URL：

   ```bash
   project=open-platform-uat
   region=asia-east1
   for service in uat-accounts uat-content-service uat-billing-service; do
     gcloud run services describe "$service" --project="$project" --region="$region" \
       --format='value(status.url)'
   done
   ```

5. 将真实 URL 更新到 `gitops/topology/uat/serverless/runtime-topology.yaml` 的
   `spec.serverless.cloud_run.accounts`、`content_service`、`billing_service`，并同步
   `hybrid`/`selfhost` topology 中对应的 Cloud Run upstream 与 `fallback_upstream`。合并
   GitOps 变更到 `main` 后，用同一 release tag 再运行 workflow：

   ```text
   operation=deploy
   target_domains=web-saas
   vault_env_path=uat
   tag_ref=<同一不可变 release tag>
   deploy_cloudflare=true
   deploy_cloud_run=false
   dns_mode=none
   ```

   这次重跑 Workers、Pages 和 serverless domains；既有域名/DNS 值保持不变。完成后验证 Worker
   到新 Cloud Run URL 的请求链路。

UAT 通过标准：Vault 与 GitOps 项目/区域校验通过，三个服务在目标项目正常运行，Worker upstream
指向目标服务，登录、Accounts API、Billing API 和 Content API 探针成功，错误率/延迟无异常。

## 5. PROD 无状态全新部署

UAT 全部通过、目标服务已运行、GitOps PROD upstream 已更新并完成审核后，另行批准生产窗口。
确认 `asia-east1-docker.pkg.dev/open-platform-prod/serverless/` 有三项相同不可变
release tag 镜像。先设置 `operation=deploy`、`target_domains=web-saas`、`vault_env_path=prod`、
`deploy_cloudflare=false`、`deploy_cloud_run=true`，逐一指定 `accounts`、`billing-service`、
`content-service`。确认服务 Ready、探针和业务请求正常后，读取真实 URL，更新并发布
`gitops/topology/prod/serverless/runtime-topology.yaml` 与相关 hybrid/selfhost fallback upstream。
再用同一 tag 重跑 `operation=deploy`、`target_domains=web-saas`、`vault_env_path=prod`、
`deploy_cloudflare=true`、`deploy_cloud_run=false`、`dns_mode=none`，验证现有域名到新 Cloud Run
upstream 的链路。公开 canonical DNS cutover 不属于本次。

不能把 Accounts 数据迁移、Supabase 迁移或 DNS/public alias cutover 隐式并入本次 GCP 身份部署。

## 迁移前就绪检查记录（2026-09-26）

| 检查项 | 结果 | 说明 |
|---|---|---|
| `gcloud` 活动账号 | 通过 | `haitaopan@xworktech.com` 为 ACTIVE |
| 新账号项目级 IAM | 通过（需后续收敛） | UAT/PROD 当前均可读；现场策略显示 `haitaopan@xworktech.com` 拥有 `roles/owner`，迁移稳定后再按最小权限拆分，不在本次重部署中撤销 |
| 新账号无关项目清理 | 通过 | 截图中的 5 个 Project ID 已删除并从 `gcloud projects list` 复核消失；`open-platform-uat` 与 `open-platform-prod` 保留 |
| UAT 账单账号 | 通过 | `open-platform-uat` 已绑定 `billingAccounts/01180B-F40C7F-BADE24` |
| UAT 目标项目 | 通过 | `open-platform-uat`，项目号 `142822217216` |
| PROD 目标项目 | 通过 | `open-platform-prod`，项目号 `986070475391` |
| 组织归属 | 通过 | 两个项目均属于 Organization `744119519286` |
| 区域 | 通过 | 目标区域统一为 `asia-east1` |
| Cloud Run API | 通过 | UAT/PROD 均启用 `run.googleapis.com` |
| Artifact Registry API | 通过 | UAT/PROD 均启用 `artifactregistry.googleapis.com` |
| Secret Manager / STS / IAM Credentials API | 通过 | UAT/PROD 均已启用 |
| 目标 Cloud Run 服务 | 通过 | UAT/PROD 六个服务均已在 `asia-east1` Ready，最新修订 100% 流量 |
| Artifact Registry 仓库 | 通过 | UAT/PROD 均使用 `asia-east1` 的 `serverless` 仓库并成功推送部署镜像 |
| GitHub OIDC/WIF | 通过 | UAT/PROD provider、对应 deploy Service Account 已 bootstrap，GitHub Actions 部署成功 |
| Vault runtime session | 通过 | `kv/uat/serverless/gcp`、`kv/prod/serverless/gcp` 已写入 WIF provider 与 Service Account；bootstrap token 已按流程清理 |
| UAT bootstrap KV | 已清理 | apply 后 token 已撤销并 scrub，仅保留项目校验字段；不记录 token |
| PROD bootstrap KV | 已清理 | apply 后 token 已 scrub，仅保留项目校验字段；不记录 token |
| GCP bootstrap token | 已绕过 | 本地 CLI 使用新账号完成部署；后续 bootstrap 不再依赖过期 ADC，使用 GitHub OIDC/WIF |
| Cloud Run upstream | 通过 | GitOps PR #308 已将 UAT/PROD serverless、hybrid、selfhost fallback 更新为新 `asia-east1` `run.app` URL |
| 镜像 | 通过 | UAT 使用 `daily-build-2026.09.25-r1`；PROD 使用 `v2026.09.13-r4`，六个服务均部署成功 |
| 单 VM 成本方案 | 未开始 | 尚未创建 VM、部署 Compose、压测或切换 origin |

当前结论：账号、项目、账单、区域、API、WIF、Vault、Artifact Registry 和 Cloud Run 部署均已完成；平台修复 PR #1014、#1015 已合并。UAT 部署运行 `36242316355`，PROD 部署运行 `36242819576`，两次运行的 Cloud Run、Gate 和 Verify/Summary 均成功。

## 5.1 本次部署与公网链路核验记录（2026-09-26）

| 环境 | 服务 | 项目 / 区域 | 最新就绪修订 | 运行时身份 | 镜像 | 入口状态 |
|---|---|---|---|---|---|---|
| UAT | `uat-accounts` | `open-platform-uat / asia-east1` | `uat-accounts-00001-q2g` | `142822217216-compute@developer.gserviceaccount.com` | `asia-east1-docker.pkg.dev/open-platform-uat/serverless/accounts:daily-build-2026.09.25-r1` | 100% 最新修订；Ingress `all`；未授权请求 403 |
| UAT | `uat-content-service` | `open-platform-uat / asia-east1` | `uat-content-service-00001-ffm` | 同上 | `asia-east1-docker.pkg.dev/open-platform-uat/serverless/content-service:daily-build-2026.09.25-r1` | 100% 最新修订；Ingress `all`；未授权请求 403 |
| UAT | `uat-billing-service` | `open-platform-uat / asia-east1` | `uat-billing-service-00001-rnh` | 同上 | `asia-east1-docker.pkg.dev/open-platform-uat/serverless/billing-service:daily-build-2026.09.25-r1` | 100% 最新修订；Ingress `all`；未授权请求 403 |
| PROD | `prod-accounts` | `open-platform-prod / asia-east1` | `prod-accounts-00001-l4q` | `986070475391-compute@developer.gserviceaccount.com` | `asia-east1-docker.pkg.dev/open-platform-prod/serverless/accounts:v2026.09.13-r4` | 100% 最新修订；Ingress `all`；未授权请求 403 |
| PROD | `prod-content-service` | `open-platform-prod / asia-east1` | `prod-content-service-00001-thr` | 同上 | `asia-east1-docker.pkg.dev/open-platform-prod/serverless/content-service:v2026.09.13-r4` | 100% 最新修订；Ingress `all`；未授权请求 403 |
| PROD | `prod-billing-service` | `open-platform-prod / asia-east1` | `prod-billing-service-00001-ktq` | 同上 | `asia-east1-docker.pkg.dev/open-platform-prod/serverless/billing-service:v2026.09.13-r4` | 100% 最新修订；Ingress `all`；未授权请求 403 |

实际 Cloud Run URL：

- UAT：`uat-accounts-4ueoyqlpbq-de.a.run.app`、`uat-content-service-4ueoyqlpbq-de.a.run.app`、`uat-billing-service-4ueoyqlpbq-de.a.run.app`。
- PROD：`prod-accounts-b7wzzanztq-de.a.run.app`、`prod-content-service-b7wzzanztq-de.a.run.app`、`prod-billing-service-b7wzzanztq-de.a.run.app`。

`https://console.svc.plus/` 返回 `200`，响应标记为 `x-frontend-route: ssr-public`；访问 `https://console.svc.plus/api/v1/health` 返回 `404` 且带有 `x-upstream-route: cloud-run-serverless` 和 Cloud Trace 标记，证明公网入口已将 API 请求送入 Serverless Cloud Run 链路。未携带业务 Bearer token 的 `/api/health` 返回 `401`，符合认证边界。

GitOps PR [#308](https://github.com/ai-workspace-infra/gitops/pull/308) 已合并（merge commit `9af3d466c63ccc8d8c1a173636709b85ec73d1cd`），更新了 UAT/PROD 的 serverless、hybrid、selfhost Cloud Run origin 与 fallback upstream。

当前新账号可见的开放账单账号有 `01180B-F40C7F-BADE24`（UAT/PROD 当前使用）和
`01E22A-D31C1A-B94A52`。UAT 已沿用 PROD 账单账号并完成绑定；如未来需要改绑，再由项目负责人
明确选择另一个账单账号：

```bash
gcloud billing projects link open-platform-uat \
  --billing-account=01180B-F40C7F-BADE24
```

上例沿用 PROD 账单账号；若应使用另一个账号，将命令中的 ID 替换为
`01E22A-D31C1A-B94A52`。绑定完成后复核：

```bash
gcloud billing projects describe open-platform-uat \
  --format='yaml(projectId,billingAccountName,billingEnabled)'
```

## 6. 成本评估：先验证单 VM，再决定是否保留 Cloud Run

截图中六个旧 Cloud Run 服务显示费用合计约 **US$39.78**（25.89 + 3.07 + 0.04 + 10.64 +
0.11 + 0.03），合计请求速率约 **0.32 req/s**。这是截图所示计费区间的当前读数，不等同于
完整月账单；应再从 Billing Reports 分离 Cloud Run CPU、内存、请求、网络和其他项目费用。

一台约 **US$25/月** 的云主机理论上可节省约 US$14.78，毛成本下降约 37%。比较时还要加入
磁盘、静态公网 IP、备份、监控、出站流量、运维和单机故障成本。Cloud Run 请求计费模式主要按
实例处理请求时的 CPU/内存和请求数计费；设置 min instances 后，空闲实例也会产生费用。最终
金额以 Billing Reports 和 Google Cloud Pricing Calculator 为准。

推荐先在 UAT 的 `open-platform-uat / asia-east1` 建立一台 VM，使用 Docker Compose 或
systemd 管理三个 UAT 服务，生产再部署到 `open-platform-prod`。Supabase、Vault 和 Cloudflare
继续使用现有托管组件；VM 不承载数据库迁移，不把 Secret 明文写入镜像或仓库。

域名名称保持不变。Cloudflare Worker 或反向代理的 origin 从 Cloud Run `run.app` URL 改为 VM
稳定 origin hostname。VM 只开放 80/443 和 SSH 管理入口，容器端口不直接暴露公网。完成健康
检查后再切换 origin，Cloud Run 至少保留 48 小时作为回退。

成本验证顺序：

1. 从 Billing Reports 导出最近完整账期，确认费用主要来自 min instances、CPU/内存、网络还是
   其他资源。
2. 在 UAT VM 部署六个容器对应的同一 release tag，并设定磁盘、备份和带宽上限。
3. 用脱敏真实请求压测 Accounts 登录/API、Billing ingest、Content API；观察 CPU、内存、连接池、
   P95、5xx、重启次数和磁盘增长。验收目标为峰值下保留至少 30% CPU/内存余量，连续 24 小时无异常。
4. 先切换 UAT origin，验证域名、OAuth、Secret、跨服务请求和日志，再安排 PROD 窗口。
5. PROD 切换后观察 48–72 小时，再决定是否停用旧 Cloud Run；停用前保存镜像 tag、配置清单和
   Cloud Run revision。

如果单 VM 压测和观察通过，六个服务迁移到一台 VM 是当前最低成本方案。如果不能接受单机故障，
保留生产 Accounts 或 Billing 在 Cloud Run，其他低流量服务迁移到 VM。若继续使用 Cloud Run，
先检查 min instances、CPU/内存、并发度和 max instances；合理提高并发度和保持 scale-to-zero
可能比直接迁移更省钱。

## 7. 回退与旧资源退役

- IAM 登录问题：保留旧管理员，不改服务；修复新账号权限后重试。
- WIF/Vault 认证问题：停止后续部署；恢复该环境 Vault 先前版本中已核实的 WIF/Service
  Account 字段，或恢复旧 WIF 绑定。
- 新 revision 健康检查失败：将流量切回该目标项目的上一就绪 revision；不要删除服务。
- 新项目服务或 Worker upstream 故障：将 GitOps upstream 恢复为变更前记录的 URL；按独立 DNS
  回退流程恢复入口。旧 `xworktech / asia-northeast1` 服务在稳定观察期内保持运行。
- 旧管理员账号、旧服务和旧身份只在新链路稳定并经单独审批后退役。不要销毁 Vault 历史版本。

## 本次仓库对接

- Serverless 部署和 `destroy` workflow 在调用 Google 认证前校验 Vault 的 project/region 与
  `gitops/resources/xworktech.com/{uat,prod}/gcp/open-platform-*.yaml` 一致，并校验 Artifact
  Registry region 与声明区域相同。
- 部署/销毁脚本不再使用旧的 `ai-workspace-uat-project` 默认目标；缺少 Vault 注入的项目或区域
  时直接失败。
- Cloud Run `run.app` upstream 不在本次猜测性改写；待目标项目实际创建服务并读取 URL 后更新。
- `gitops/topology/{uat,prod}/selfhost/ai-aggregator.yaml` 的 `account_email` 是 Claude/Grok
  provider 元数据，与 GCP 管理员/WIF 无关，不因本次变更而替换。
