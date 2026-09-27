# GCP OIDC Bootstrap 交接文档（供后续 Code Agent 接手）

> 目的：如果这个 Cowork 会话中断、或换一个 Claude Code / Code Agent 会话接手，读这一份文档就能知道现在做到哪一步、下一步具体要做什么、每个仓库的确切状态。
> 关联：Epic [`ai-workspace-infra/platform-ops-toolkit#804`](https://github.com/ai-workspace-infra/platform-ops-toolkit/issues/804)、P0 [`#805`](https://github.com/ai-workspace-infra/platform-ops-toolkit/issues/805)
> 架构/方案文档（背景知识，先读这个）：用户本机 `~/workspaces/ai-workspace-service/knowledge/products/solution/open-platform/IAC/gcp-oidc-bootstrap-solution.md`
> 最后更新：2026-09-22（持续更新中）

## 0. 一句话现状

六个改动全部合并完毕（项目 ID 修正、条件渲染、state 隔离、auth-json 助手脚本、workflow 消费 `GCP_AUTH_JSON` + 自动吊销）。**代码层面的工作已经做完**。用户已经明确表态目标：bootstrap job 用一次性 `GCP_AUTH_JSON`、用完当场吊销，之后 runtime 全程只走 GitHub OIDC → Vault JWT role → Google WIF，再建一台约 1 小时的 GCP Spot 实例验证整条链路。为此已经准备好一个一键脚本 `gcp-e2e-verification.sh`（默认就是 `auth_json` 模式，发给用户 + 写到 Mac `~/Downloads/`），串联 Vault Policy 同步 + 组织策略临时豁免 + 自动创建 bootstrap SA/生成 key + 触发两个工作流 plan/apply/持有约 1 小时/destroy。**这一步只能用户在自己电脑的真实 Terminal 里跑**（需要本地已登录的 `gh`/`vault`/`gcloud`，Cowork 云端会话和桌面 App 的隔离 VM 都没有这些真实凭据）。见第 4 节的完整说明。

## 1. 环境与协作方式（新会话必读）

- 这个 Cowork 会话运行在一个隔离的云端沙箱容器里，本地克隆了 4 个仓库到 `/home/claude/repos/`：`gitops`、`iac_modules`、`platform-ops-toolkit`、`playbooks`。
- **这个沙箱的 git 出站请求会被拒绝**：`git push` 到这三个仓库（gitops/iac_modules/platform-ops-toolkit）永远返回 `access denied by the git proxy: ... is not in this session's authorized repository set`，HTTP 403。这是结构性限制，不是权限配置问题，新会话不用重复排查，直接采用下面的绕过方式。
- **绕过方式**：在沙箱里把改动做完、跑完本地测试、`git format-patch` 生成 patch、base64 编码后内嵌进一个自包含的 shell 脚本（`clone → git am 应用 patch → 本地跑 contract test → push → gh pr create → 轮询 CI → 询问后 squash merge`），通过 `SendUserFile` 发给用户，并用 `mcp__remote-devices__device_commit_files` 顺手写一份到用户 Mac 的 `~/Downloads/`。用户在自己电脑的真实 Terminal（不是 Cowork 桌面 App 里那个隔离 VM）里跑这个脚本，因为只有那里的 `gh` CLI 是登录状态。
- **这个会话也能连到用户的 Mac**（`mcp__remote-devices__*` 工具），但那是桌面 App 里一个隔离的 Linux VM，用来读写用户挂载的文件夹（目前挂了 `~/Downloads` 和 `~/workspaces/ai-workspace-service`），**没有装 `gh`、也没有用户真实终端里那份已登录的 GitHub 凭据**，不能代替用户本机跑 PR 脚本。用这个 VM 只做文件读写/改名/删除（`device_bash`、`device_commit_files`、`device_request_folder_access`、`device_request_delete_permission`）。
- 每次生成新 patch 前，**先 `git fetch origin main` 并 rebase**——这个仓库合并频率很高（其他人/其他 agent 也在提交），origin/main 经常在几分钟内就往前走，直接用旧的 base 生成的 patch 大概率会 push 冲突（non-fast-forward）。已经踩过这个坑（见第 5 节）。

## 2. 已经完全合并、不用再管的部分

| 仓库 | PR | 内容 | Main 上的 commit |
|---|---|---|---|
| `gitops` | #274 | 项目 ID 修正（`xworktech-open-platform-*` → `xwork-open-platform-*`）；新增 `spot-validation-uat.yaml` 最小验证 manifest | `b7268fe` |
| `iac_modules` | #324 | 项目 ID 修正；`deploy_service_account_roles` 加 `compute.networkAdmin`；`platform_services` API 前移到 bootstrap；模板/变量/`generate.py` 条件渲染 | `2ba98f3` |
| `platform-ops-toolkit` | #855 | 项目 ID 修正；`iac_ref`/`ref:` 更新为上面两个新 SHA；`gcp-iac-pipeline.yml` 按 manifest 隔离 state workspace | `a77f3e2` + 合并提交 `dcb679f` |
| `platform-ops-toolkit` | #870 | `scripts/gcp/bootstrap_gcp_auth_kv.sh` 新增 `--auth-json`/`revoke` 模式；对应 contract test；howto 文档新增"一次性 Admin SA key"章节 | `ccf892f` |
| `platform-ops-toolkit` | #881 | `gcp-oidc-bootstrap.yml` 消费 `GCP_AUTH_JSON`（in-job 换 token + 自动吊销）；两个环境的 Vault policy HCL 放开 create/update/delete；contract test 和 howto 同步更新 | `03974c6` |
| Epic `#804`（GitHub issue 正文，非 git 提交） | — | 新增"凭据分层约定"章节：Bootstrap Init 允许一次性 Admin JSON key，日常流水线禁止任何固定 JSON key | 直接在 GitHub 网页编辑生效 |

这六项工作的完整设计细节都写在架构文档（见文首链接）里，不用重复看这份交接文档。第 3 节（原来描述 #881 还没开 PR 时的设计细节）保留作为参考，但状态已经是"已合并"，不用再执行第 3.3 节里的脚本。

## 3. ✅ 已合并：PR #881（workflow 消费 GCP_AUTH_JSON + 自动吊销）

**状态**：已合并到 `platform-ops-toolkit` main，squash commit `03974c65e581d85190e7c7fd4a727ca1695d51bb`（`03974c6`）。用户本机跑 `~/Downloads/gcp-auth-json-workflow-pr.sh` 完成的，CI 全绿后手动确认了 squash merge。以下 3.1/3.2/3.3 是这次改动的设计和验证细节，供理解代码用；3.3 提到的脚本已经跑完、不用再跑。

### 3.1 改了什么

1. **`.github/workflows/gcp-oidc-bootstrap.yml`**（核心改动）
   - 原来只会从 Vault 读 `GCP_ACCESS_TOKEN`（vault-action 的静态 `secrets:` 字段列表，如果字段不存在会直接报错，所以没法同时兼容 `GCP_AUTH_JSON` 和 `GCP_ACCESS_TOKEN` 二选一的情况）。
   - 新增一个 `id: credential` 的 step："Load GCP bootstrap credential from Vault"：改用原始 `curl` + `X-Vault-Token`（这个 token 来自同一个 `hashicorp/vault-action` step 的 `outputToken: true` 输出）直接读整个 KV secret JSON，用 `jq -r '.XXX // empty'` 判断字段是否存在，据此决定 `credential_mode` 是 `auth_json` 还是 `token`。
   - 新增 `id: exchange` 的 step："Exchange one-time GCP_AUTH_JSON for a short-lived access token"：只在 `credential_mode == 'auth_json'` 时运行，用 `google-github-actions/auth@v2`，`credentials_json` 传入刚读出来的 JSON，`token_format: access_token`，**关键**：显式 `create_credentials_file: false`（这个 action 默认是 `true`，会把 key 写到 runner 磁盘上，必须显式关掉）。
   - 新增 `id: token` 的 step："Resolve bootstrap access token"：统一两种模式，输出 `access_token`，后续所有步骤（`Verify GCP project bootstrap permissions`、`Terraform init/plan/apply` 的 `TF_VAR_access_token`）都改用这一个统一的 `steps.token.outputs.access_token`。
   - `Verify bootstrap project matches GitOps` 的 `VAULT_PROJECT_ID` 改用 `steps.credential.outputs.project_id`。
   - **新增 "Revoke one-time bootstrap credential" step**，紧跟在 "Capture bootstrapped identity outputs" 之后（也就是 Terraform apply 成功、拿到新建的 WIF/deploy SA 信息之后，做 WIF 自检之前）：
     - 条件：`always() && inputs.action == 'apply' && steps.credential.outputs.credential_mode == 'auth_json'`——用 `always()` 是因为哪怕后面的步骤失败，一次性 key 也应该尽早吊销，泄露风险比"多吊销一次"更严重。
     - 用刚才换出来的 access token 直接调 GCP IAM REST API：`DELETE .../serviceAccounts/{email}/keys/{key_id}`（删 key）、`POST .../serviceAccounts/{email}:disable`（禁用 SA，这一步失败会让整个 job 失败，因为这是安全关键操作）、`POST oauth2.googleapis.com/revoke`（显式吊销这个 access token 本身，失败只警告不阻断）。
     - 再用 `X-Vault-Token`（来自 `steps.vault.outputs.vault_token`）调 Vault HTTP API：`DELETE kv/metadata/CICD/<env>/gcp-bootstrap/<account>`（销毁全部历史版本），成功后再 `POST kv/data/CICD/<env>/gcp-bootstrap/<account>` 只写回 `GCP_PROJECT_ID`。
     - **如果 Vault 那两步因为权限不够而失败**（见下面 3.2），不会让 job 失败，只打印 `::warning::`，并在警告文本里给出精确的手动兜底命令（`GCP_BOOTSTRAP_ACTION=revoke ... bash scripts/gcp/bootstrap_gcp_auth_kv.sh`）——因为此时 GCP 侧的 key 已经删了、SA 已经禁用了，真正的安全目标已经达成，Vault 里剩的只是一条"已经失效的历史记录"，不是紧急问题。

2. **`scripts/vault/policies/github-actions-platform-ops-toolkit-{uat,prod}-gcp-bootstrap-xworktech.hcl`**
   - 这两个文件是 Vault Policy 的**声明式代码**（不是纯文档！`platform-ops-toolkit` 这个仓库把 Vault policy/role 当代码管理，在 `scripts/vault/policies/*.hcl` 和 `scripts/vault/roles/*.json`，用 `scripts/create_vault_service_repo_roles.sh --apply` 手动同步到真实 Vault，没有 CI 自动跑这个同步）。
   - `path "kv/data/CICD/<env>/gcp-bootstrap/xworktech"` 的 `capabilities` 从 `["read"]` 改成 `["read", "create", "update"]`（新增的吊销 step 要重新写回精简后的 secret）。
   - `path "kv/metadata/CICD/<env>/gcp-bootstrap/xworktech"` 的 `capabilities` 从 `["read"]` 改成 `["read", "delete"]`（要销毁全部历史版本）。
   - **这个改动合并到 main 之后，需要 Vault 管理员额外手动跑一次**：
     ```bash
     export VAULT_ADDR=https://vault.svc.plus
     bash scripts/create_vault_service_repo_roles.sh --apply --env uat
     bash scripts/create_vault_service_repo_roles.sh --apply --env prod
     ```
     在这一步跑之前，如果真的触发了 `--auth-json` bootstrap，workflow 的自动吊销会走上面说的"降级到警告"分支，不会把整个 bootstrap 流程搞失败。

3. **`.github/scripts/tests/gcp_oidc_bootstrap_contract_test.sh`**
   - 删掉了一条已经失效的必需字符串检查（`'kv/data/CICD/${{ inputs.environment }}/gcp-bootstrap/${{ steps.config.outputs.account_id }}'`，这个字面字符串在新代码里不存在了，因为改成了 shell 变量插值 `${ENVIRONMENT}`/`${ACCOUNT_ID}` 而不是 GitHub Actions 表达式插值）。
   - 新增了一大串针对新 step 名字/关键字符串的必需检查（`credential_mode=auth_json`、`create_credentials_file: false`、`Revoke one-time bootstrap credential` 等等）。
   - 新增了对两个 policy 文件的 capabilities 检查（确认 `["read", "create", "update"]` 和 `["read", "delete"]` 都存在）。
   - 本地跑过：`bash .github/scripts/tests/gcp_oidc_bootstrap_contract_test.sh` → `PASS`。

4. **`docs/howto/GCP-OIDC-Bootstrap-howto.md`**
   - "一次性 Admin SA key（`--auth-json`）" 这一节补充说明：workflow 现在会自动消费 `GCP_AUTH_JSON` 并自动吊销，之前写的手动 `revoke` 命令降级为"Vault Policy 还没同步时的兜底手段"，并加了 Vault Policy 同步的前提说明和命令。

### 3.2 我做过的验证（都在这个云端沙箱本地完成，没有真实 GCP/GitHub Actions 执行）

- `bash .github/scripts/tests/gcp_oidc_bootstrap_contract_test.sh` → PASS（改动后每次都重新跑过）。
- `python3 -c "import yaml; yaml.safe_load(...)"` → 确认整个 workflow YAML 语法合法，21 个 step 顺序符合设计（一开始漏了一个 heredoc 在 YAML block scalar 里顶格写导致 YAML 解析报错，已经改成单行 `echo` 修掉）。
- 对每个 `run:` 块用 `bash -n`（把 `${{ ... }}` 表达式临时替换成占位符再检查）→ 全部语法合法。
- **行为测试**（重点，不只是语法检查）：写了一个 stub `curl`（记录调用、根据 URL 和几个环境变量开关返回预设 JSON/退出码），把 `credential`、`token`（resolve）、`revoke` 三个 step 的 `run:` 脚本提取出来单独跑，覆盖了：
  - `credential` step：`auth_json` 模式、`token` 模式、两者都没有（应该报错退出 1）、缺 `GCP_PROJECT_ID`（应该报错退出 1）——全部符合预期。
  - `token`（resolve）step：`auth_json` 模式取 exchange 输出、`token` 模式取原始 token、两者都是空（应该报错）——全部符合预期。
  - `revoke` step：**全部成功**（GCP key 删除+SA 禁用+Vault 清理都成功，job 应该 exit 0）、**Vault Policy 还没同步**（GCP 侧成功，Vault 侧失败但只警告，job 仍应 exit 0）、**SA 禁用失败**（应该硬失败，job exit 1）——三种场景全部符合预期，跟设计意图完全一致。
- 没有测试的部分（这个沙箱做不到，需要真实环境）：真的调用 `google-github-actions/auth@v2` 交换 token、真的调用 GCP IAM API、真的调用 Vault HTTP API、真的在 GitHub Actions runner 上跑这个 workflow。这些只能等 PR 合并、workflow 真实触发时才能验证。

### 3.3 交付物（已跑完，仅作记录）

- `gcp-auth-json-workflow-pr.sh` —— 跟之前 `#870` 用的是同一套模式：`clone → git am 应用内嵌 patch → 本地跑 contract test → push → gh pr create → 轮询 CI → 问用户要不要 squash merge`。用户在自己 Mac 终端跑完，PR #881 CI 全绿，手动确认 `y` 后 squash merge 成功。
- 对应的 patch 文件（沙箱内路径，仅存档）：`/mnt/user-data/outputs/patches/platform-ops-toolkit-auth-json-consumption.patch`。
- **合并结果**：`ai-workspace-infra/platform-ops-toolkit` main 上的 commit `03974c65e581d85190e7c7fd4a727ca1695d51bb`，5 个文件、203 行新增/15 行删除，跟沙箱里验证过的内容完全一致。

## 4. 下一步该做什么（按顺序，当前从这里开始）

**用户已经明确表态目标（2026-09-22，两条消息）**：
1. "验证完成一次从 GCP Bootstrap 到 Runtime 创建资源"；
2. 具体要求："完成 bootstrap Job 用，Job 用完当场吊销。之后所有 IaC 流水线只走 GitHub OIDC → Vault JWT role → Google WIF，不再持有任何 GCP 密钥。然后创建一台 1h 的 GCP spot 实例验证"——也就是明确要用 `--auth-json` 一次性凭据模式（而不是退而求其次的 token 模式），因为只有 `--auth-json` 模式才会触发 #881 新加的"job 内自动吊销"逻辑；"之后 IaC 流水线只走 OIDC/WIF"是既有 runtime 架构，本来就是这样，不需要改代码，只需要在验证时观察确认。

这是整个 Epic #804 / Issue #805 最终要证明的事——到目前为止全部工作都还只是"代码正确"（contract test + stub 行为测试），从立项到现在从没有一次真实执行过。

我把 Vault Policy 同步 + 组织策略临时豁免（仅 auth_json 模式需要）+ `bootstrap_gcp_auth_kv.sh --auth-json` 写入一次性凭据 + 触发两个工作流 plan/apply/持有约 1 小时/destroy + 抓日志核对关键点，全部串成了一个脚本 `gcp-e2e-verification.sh`，**已发给用户、也写到了 Mac 的 `~/Downloads/`**。这个脚本只能在用户自己电脑的真实 Terminal 里跑（需要本地已登录的 `gh`/`vault`/`gcloud`），Cowork 云端会话和桌面 App 里的隔离 VM 都没有 Vault/GCP 的真实凭据，做不了这一步。

1. **在真实 Terminal 里跑**（默认就是 `auth_json` 模式，符合用户的明确要求，不用加任何参数）：
   ```bash
   bash ~/Downloads/gcp-e2e-verification.sh
   ```
   脚本依次做：
   - Vault Policy 同步（`scripts/create_vault_service_repo_roles.sh --apply --env uat`，除非加 `--skip-policy-sync`）——这是 job 内自动吊销能把 Vault 里的一次性凭据清理干净的前提。
   - 检查 `iam.disableServiceAccountKeyCreation` 组织策略在 `xwork-open-platform-uat` 上是否 enforced；如果是，询问是否临时豁免（需要用户的 gcloud 账号有 `roles/orgpolicy.policyAdmin`），生成 key 后立即改回，把豁免窗口压到最短。
   - `bash scripts/gcp/bootstrap_gcp_auth_kv.sh --auth-json`：**自动**创建/复用专用服务账号 `gcp-bootstrap-uat`（幂等，只给 4 个必需角色，不给 Owner/Editor）、生成一次性 key、写入 `kv/CICD/uat/gcp-bootstrap/xworktech`——用户不需要自己手动建服务账号或准备 key 文件。
   - 触发 **GCP OIDC Bootstrap**：`environment=uat action=plan` → 打印关键日志 → 等你确认 → `action=apply`（workflow 自己的 "Revoke one-time bootstrap credential" step 会在 job 内把这把 key 删除+禁用 SA；脚本会去读这一段日志，明确打印"✅ 自动吊销成功"或警告）。
   - 触发 **gcp-iac-pipeline.yml**（manifest=`resources/xworktech.com/uat/gcp/spot-validation-uat.yaml`）：`plan` → 等你确认 → `apply`（真的建一台 `e2e-micro` Spot VM）→ 用 `gcloud compute instances describe` 核对 `provisioningModel == SPOT` → **持有约 60 分钟**（`--hold-minutes` 可调，期间可以 Ctrl+C 中断保留实例）→ 确认后 `destroy` 清理。
   - 每个 apply/destroy、以及临时改组织策略之前，都会停下来手动确认，不会自己往下冲。
   - 结束后打印 5 个 GitHub Actions run 链接，可以直接贴进 `#805`/`#806` 作为验证证据。
   - 如果用户的 gcloud 账号没有 `roles/orgpolicy.policyAdmin`、又赶时间想先跑通主链路，可以加 `--token` 退回到短期 admin token 模式（不需要改组织策略），但这样就验证不了 #881 的自动吊销逻辑，属于降级方案，不是用户明确要的那个。
2. **跑完之后**：把脚本结尾打印的 5 个 run 链接和关键结论（一次性 key 用完当场吊销成功、`kv/uat/platform/oidc/xworktech` 已写入、runtime 阶段全程只用 OIDC/WIF 没有任何固定密钥、Spot 实例确认建成功又销毁）回填到 `#805`/`#806`，Epic `#804` 的完成定义逐项勾选。
3. **PROD 环境**：本次和之前几轮的改动对 UAT/PROD 都是对称的，但 PROD 的 bootstrap/apply 需要走受保护的 GitHub Environment 审批，目前完全没有在 PROD 上执行过任何东西。先把 UAT 这条链路验证通过之后，再考虑要不要对 PROD 也跑一次。

### 4.1 关于这个脚本的设计说明（新会话如果要改这个脚本，先看这个）

- **默认 `auth_json` 凭据模式**（不是 token）：这是用户在这次对话里明确要求的——"完成 bootstrap Job 用，Job 用完当场吊销"，只有 auth_json 模式会触发 #881 新加的 job 内自动吊销逻辑，token 模式没有一次性密钥可吊销（它本来就是短期 token，自然过期）。`--token` 保留作为降级选项，仅当用户的 gcloud 账号没有组织策略管理权限时使用。
- **不需要用户手动准备 key 文件**：`bootstrap_gcp_auth_kv.sh --auth-json` 自己的 `ensure_bootstrap_service_account()` + `write_auth_json()` 会自动创建专用服务账号、生成 key、写入 Vault，全程在用户本机的临时目录（`0700`/`umask 077`）里完成，不落地到别处。脚本最初的一版设计错误地要求用户预先提供一个 key 文件路径（`--auth-json <path>`），读了 `platform-ops-toolkit` 方案文档第 4.4 节后发现这是不对的，已经改成直接调用 `--auth-json` 无参数用法。
- **组织策略豁免窗口尽量短**：`iam.disableServiceAccountKeyCreation` 只在"创建 key"这个动作上生效，key 一旦生成、写入 Vault 后就不再需要豁免（后续的删除 key、禁用 SA 不受这条策略约束），所以脚本在 `bootstrap_gcp_auth_kv.sh --auth-json` 成功返回后立刻调用 `restore_org_policy()` 改回默认值，而不是等到整个脚本跑完。
- **Spot 实例持有约 1 小时**（`--hold-minutes`，默认 60）：用户明确要求"创建一台 1h 的 GCP spot 实例验证"，脚本在 apply 成功、`gcloud compute instances describe` 确认是 `SPOT` 之后，会分 10 分钟一档地 sleep 到设定时长，再进入 destroy 确认，而不是 apply 完立刻销毁——留出时间让用户自己去控制台/SSH 上去看一眼。
- 脚本自己不会一路跑到底：每个 `apply`/`destroy`、以及组织策略豁免之前，都用 `confirm()` 停下来等人工输入 `y`，因为这是这个项目历史上第一次真实执行，宁可多问一次也不要在没人盯着的情况下改组织策略、建/销毁真实云资源。
- `run_workflow()` helper 用"触发前记录最新 run id → 轮询等新 run 出现 → `gh run watch --exit-status`"这个模式，因为 `gh workflow run` 本身不会返回 run id（GitHub API 目前就是这样），这是驱动 `workflow_dispatch` 类型工作流最常见的绕过方式。
- 脚本里硬编码的 `IAC_REF=2ba98f30c3e4199e01eb940bb1951549fca0ae3e`、`gcp_account_id=xworktech`、manifest 路径，都是从 `gitops/resources/xworktech.com/uat/gcp/github-actions-oidc.yaml` 和 `gcp-iac-pipeline.yml` 的 `workflow_dispatch.inputs` 默认值里核对过的当前真实值，不是猜的；如果这几个仓库后续又有新 PR 改了这些值，新会话要重新核对一遍再跑。

## 5. 踩过的坑（新会话不用重复踩）

- **origin/main 移动很快**：这个仓库有其他自动化/人工提交在持续合并，生成 patch 前必须先 `fetch` + `rebase` 到最新 `origin/main`，否则 `git push` 会因为 `non-fast-forward` 被拒绝（已经真实发生过一次，用户手动跑脚本时遇到，靠删除远程残留分支+重新生成 patch 解决）。
- **YAML block scalar 里不能顶格写 heredoc 内容**：`run: |` 里如果用 `cat <<EOF ... EOF`，heredoc 正文和结束标记如果顶格写（列 1）会被 YAML 解析器当成"block scalar 结束了，新的顶层节点开始了"，导致语法错误。要么把 heredoc 每一行都缩进到和其他 `run:` 内容一样的层级（heredoc 内容会带上这些前导空格，除非用 `<<-` 配合 TAB），要么像这次一样干脆改成单行 `echo "..."`。
- **`hashicorp/vault-action` 的 `secrets:` 静态字段列表在字段不存在时会直接报错**，不支持"这个字段可能不存在，缺了就跳过"。当一个 Vault secret 里两个字段互斥存在（这次是 `GCP_AUTH_JSON` 和 `GCP_ACCESS_TOKEN` 二选一）时，不能用这个机制同时列出两个字段，要么用 `ignoreNotFound`（但这是整个 secret 级别的开关，粒度太粗，会连带影响必需字段），要么像这次一样改用原始 Vault HTTP API + `jq` 自己判断。
- **`google-github-actions/auth@v2` 的 `create_credentials_file` 默认值是 `true`**，不是 `false`——用 `credentials_json` 输入时如果不显式设成 `false`，会把 key 文件写到 runner 磁盘上，直接违反"一次性凭据全程不落盘"的设计目标。这个默认值容易想当然搞错，新会话如果要改类似逻辑务必查文档确认。
- **`token_format: access_token` 必须同时提供 `service_account` 输入**（SA 邮箱），不能只给 `credentials_json`。
- **这个云端沙箱里没有 `gh` CLI、也没有 GitHub 凭据**，`mcp__remote-devices__device_bash`（用户 Mac 上桌面 App 的隔离 VM）里也一样没有——两边都不能直接开 PR/合并，必须让用户在自己电脑的真实 Terminal 里跑交付的脚本。不要在这两个环境里反复尝试装 `gh` 或找凭据，直接采用"生成 patch + 脚本 + 让用户跑"这条路径。

## 6. 完整仓库/分支/commit 速查表（接手时先跑这几条确认状态是否还准确）

```bash
cd /home/claude/repos/platform-ops-toolkit   # 或新会话里重新 clone
git fetch origin main
git log --oneline -1 origin/main             # 确认基线
git log --oneline origin/main | grep -i "auth-json\|gcp-bootstrap-auth-json-consumption"  # 确认这次改动是否已经合并
git branch -a | grep gcp-bootstrap            # 看看有没有残留的远程/本地分支
```

如果 `git log origin/main | grep` 已经能搜到 "consume GCP_AUTH_JSON in gcp-oidc-bootstrap.yml with in-job revoke"，说明这份交接文档描述的这一步已经完成，直接跳到第 4 节的第 2、3 步（Vault Policy 同步 + 真实 E2E 验证）。
