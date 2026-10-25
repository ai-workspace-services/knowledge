# GitHub ↔ 新 Vault：30 角色 / 11 策略矩阵与复用待办

记录日期：2026-10-25，Asia/Shanghai。本页是 V5 K3s all-in-one 核心控制面的身份配置与验收附件，不包含秘密值或秘密存储路径。

[部署快照与完成状态](prod-v5-vps-to-k3s-runtime-and-acceptance-20261025.zh.md) · [可复用 23 组检查表](deployment-migration-acceptance-checklist.template.zh.md) · [V4→V5 白皮书索引](../../17-prod-v4-v5-baseline-and-upgrade-retrospective.zh.md)

## 1. 固定来源及验证边界

- Toolkit 声明：`ccc5b992e4a23b59f2edeb27d045ed069e9d7c02`（PR #1443/#1444）。
- Playbooks 协调 owner：`447ac6270e6482c53506d9d6e76e4a8193f81046`（PR #765）。
- GitHub issuer/discovery：`https://token.actions.githubusercontent.com`；audience=`vault`；user claim=`sub`。
- 全部角色保留精确 repository、workflow allowlist、ref 约束；batch Token TTL/max TTL=`1h`；`token_no_default_policy=true`。
- 17:58:02–17:58:19 完成最后 3 个角色对齐，exit 0；17:58:20–17:58:39 同输入重跑，exit 0、changed=0。后续独立读回 30/30 角色匹配声明。
- GitOps PR 的真实 CI 登录已通过：[运行回执](https://github.com/ai-workspace-infra/gitops/actions/runs/40180407033)。未取得其他角色逐仓、逐环境真实登录回执，不把配置匹配当作流水线完成。
- 六个访问边界单元测试通过，覆盖错误生产 ref、通配仓库/工作流、无关策略写入和默认策略授权。这不是用真实其他仓库 JWT 执行的越权请求。
- 不恢复 bootstrap、Raft operator、旧主机恢复等专项高权限角色，不派发部署/迁移/云资源操作。

## 2. 30 个角色矩阵

“配置/回读 PASS”表示角色已恢复并匹配固定声明；“CI PASS”只适用于列出的真实运行。工作流引用数是明确 allowlist 的条目数，不表示这些文件都调用过 Vault。

| 完成配置 | Repository | 环境 | Vault role | 策略 | 工作流引用数 | ref 绑定 | 配置/回读 | 真实 CI 登录 |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| [x] | `ai-workspace-services/accounts` | SIT | `github-actions-accounts-sit` | `github-actions-accounts` | 1 | `refs/pull/*/merge`, `refs/heads/*`, `refs/tags/sit-*` | PASS | NOT_RUN |
| [x] | `ai-workspace-services/accounts` | UAT | `github-actions-accounts-uat` | `github-actions-accounts` | 1 | `refs/heads/main`, `refs/heads/release/*`, `refs/heads/daily-build-*`, `refs/tags/uat-*`, `refs/tags/daily-build-*` | PASS | NOT_RUN |
| [x] | `ai-workspace-services/accounts` | PROD | `github-actions-accounts-prod` | `github-actions-accounts` | 1 | `refs/tags/v*`, `refs/heads/release/v*` | PASS | NOT_RUN |
| [x] | `ai-workspace-infra/artifacts` | SIT | `github-actions-artifacts-sit` | `github-actions-artifacts` | 69 | `refs/pull/*/merge`, `refs/heads/*`, `refs/tags/sit-*` | PASS | NOT_RUN |
| [x] | `ai-workspace-infra/artifacts` | UAT | `github-actions-artifacts-uat` | `github-actions-artifacts` | 69 | `refs/heads/main`, `refs/heads/feature/*`, `refs/heads/daily-build-*`, `refs/tags/uat-*`, `refs/tags/daily-build-*` | PASS | NOT_RUN |
| [x] | `ai-workspace-infra/artifacts` | PROD | `github-actions-artifacts-prod` | `github-actions-artifacts` | 69 | `refs/tags/v*`, `refs/heads/release/v*` | PASS | NOT_RUN |
| [x] | `ai-workspace-services/billing-service` | SIT | `github-actions-billing-service-sit` | `github-actions-billing-service` | 1 | `refs/pull/*/merge`, `refs/heads/*`, `refs/tags/sit-*` | PASS | NOT_RUN |
| [x] | `ai-workspace-services/billing-service` | UAT | `github-actions-billing-service-uat` | `github-actions-billing-service` | 1 | `refs/heads/main`, `refs/heads/release/*`, `refs/heads/daily-build-*`, `refs/tags/uat-*`, `refs/tags/daily-build-*` | PASS | NOT_RUN |
| [x] | `ai-workspace-services/billing-service` | PROD | `github-actions-billing-service-prod` | `github-actions-billing-service` | 1 | `refs/tags/v*`, `refs/heads/release/v*` | PASS | NOT_RUN |
| [x] | `ai-workspace-services/portal` | SIT | `github-actions-console-sit` | `github-actions-console` | 2 | `refs/pull/*/merge`, `refs/heads/*`, `refs/tags/sit-*` | PASS | NOT_RUN |
| [x] | `ai-workspace-services/portal` | UAT | `github-actions-console-uat` | `github-actions-console` | 2 | `refs/heads/main`, `refs/heads/release/*`, `refs/heads/daily-build-*`, `refs/tags/uat-*`, `refs/tags/daily-build-*` | PASS | NOT_RUN |
| [x] | `ai-workspace-services/portal` | PROD | `github-actions-console-prod` | `github-actions-console` | 2 | `refs/tags/v*`, `refs/heads/release/v*` | PASS | NOT_RUN |
| [x] | `ai-workspace-services/content-service` | SIT | `github-actions-content-service-sit` | `github-actions-content-service` | 1 | `refs/pull/*/merge`, `refs/heads/*`, `refs/tags/sit-*` | PASS | NOT_RUN |
| [x] | `ai-workspace-services/content-service` | UAT | `github-actions-content-service-uat` | `github-actions-content-service` | 1 | `refs/heads/main`, `refs/heads/release/*`, `refs/heads/daily-build-*`, `refs/tags/uat-*`, `refs/tags/daily-build-*` | PASS | NOT_RUN |
| [x] | `ai-workspace-services/content-service` | PROD | `github-actions-content-service-prod` | `github-actions-content-service` | 1 | `refs/tags/v*`, `refs/heads/release/v*` | PASS | NOT_RUN |
| [x] | `ai-workspace-services/docs` | SIT | `github-actions-docs-sit` | `github-actions-docs` | 1 | `refs/pull/*/merge`, `refs/heads/*`, `refs/tags/sit-*` | PASS | NOT_RUN |
| [x] | `ai-workspace-services/docs` | UAT | `github-actions-docs-uat` | `github-actions-docs` | 1 | `refs/heads/main`, `refs/heads/release/*`, `refs/heads/daily-build-*`, `refs/tags/uat-*`, `refs/tags/daily-build-*` | PASS | NOT_RUN |
| [x] | `ai-workspace-services/docs` | PROD | `github-actions-docs-prod` | `github-actions-docs` | 1 | `refs/tags/v*`, `refs/heads/release/v*` | PASS | NOT_RUN |
| [x] | `ai-workspace-infra/gitops` | SIT | `github-actions-gitops-sit` | `github-actions-gitops` | 1 | `refs/pull/*/merge` | PASS | PASS（上述 PR 运行） |
| [x] | `ai-workspace-infra/gitops` | UAT | `github-actions-gitops-uat` | `github-actions-gitops` | 1 | `refs/heads/main` | PASS | NOT_RUN |
| [x] | `ai-workspace-infra/gitops` | PROD | `github-actions-gitops-prod` | `github-actions-gitops` | 1 | `refs/tags/v*`, `refs/heads/release/v*` | PASS | NOT_RUN |
| [x] | `ai-workspace-infra/platform-ops-toolkit` | SIT | `github-actions-platform-ops-toolkit-sit` | `github-actions-platform-ops-toolkit-sit` | 25 | `refs/pull/*/merge`, `refs/heads/*` | PASS | NOT_RUN |
| [x] | `ai-workspace-infra/platform-ops-toolkit` | UAT | `github-actions-platform-ops-toolkit-uat` | `github-actions-platform-ops-toolkit-uat` | 38 | `refs/heads/main`, `refs/heads/release/*`, `refs/heads/bugfix/*`, `refs/heads/daily-build-*`, `refs/tags/daily-build-*` | PASS | NOT_RUN |
| [x] | `ai-workspace-infra/platform-ops-toolkit` | PROD | `github-actions-platform-ops-toolkit-prod` | `github-actions-platform-ops-toolkit-prod` | 28 | `refs/tags/v*`, `refs/heads/release/v*` | PASS | NOT_RUN |
| [x] | `ai-workspace-infra/playbooks` | SIT | `github-actions-playbooks-sit` | `github-actions-platform-ops-toolkit-sit` | 5 | `refs/pull/*/merge`, `refs/heads/*` | PASS | NOT_RUN |
| [x] | `ai-workspace-infra/playbooks` | UAT | `github-actions-playbooks-uat` | `github-actions-platform-ops-toolkit-uat` | 5 | `refs/heads/main`, `refs/heads/release/*`, `refs/heads/bugfix/*`, `refs/heads/daily-build-*`, `refs/tags/daily-build-*` | PASS | NOT_RUN |
| [x] | `ai-workspace-infra/playbooks` | PROD | `github-actions-playbooks-prod` | `github-actions-platform-ops-toolkit-prod` | 5 | `refs/tags/v*`, `refs/heads/release/v*` | PASS | NOT_RUN |
| [x] | `ai-workspace-services/postgresql` | SIT | `github-actions-postgresql-sit` | `github-actions-postgresql` | 1 | `refs/pull/*/merge`, `refs/heads/*`, `refs/tags/sit-*` | PASS | NOT_RUN |
| [x] | `ai-workspace-services/postgresql` | UAT | `github-actions-postgresql-uat` | `github-actions-postgresql` | 1 | `refs/heads/main`, `refs/heads/release/*`, `refs/heads/daily-build-*`, `refs/tags/uat-*`, `refs/tags/daily-build-*` | PASS | NOT_RUN |
| [x] | `ai-workspace-services/postgresql` | PROD | `github-actions-postgresql-prod` | `github-actions-postgresql` | 1 | `refs/tags/v*`, `refs/heads/release/v*` | PASS | NOT_RUN |

生产只接受 `refs/tags/v*` 与 `refs/heads/release/v*`；已移除 Console 的旧代际 tag 例外。SIT/UAT 保留各自既有 ref 绑定，不据此推定共享策略内的凭据已实现字段级或完整环境物理隔离。

## 3. 11 个既有策略矩阵

以下 capability 是每个策略各路径规则的并集，**不表示这些动作授予全部 Vault 路径**。实际对象范围以固定声明中的策略文件为准；本页不公开路径明细，也不扩大原有授权。

| 策略 | 消费者 | 绑定角色数 | 声明中的 capability 并集 | 本次处理 |
| --- | --- | ---: | --- | --- |
| `github-actions-accounts` | `ai-workspace-services/accounts` | 3 | `list`, `read` | 按既有声明恢复 |
| `github-actions-artifacts` | `ai-workspace-infra/artifacts` | 3 | `list`, `read` | 按既有声明恢复 |
| `github-actions-billing-service` | `ai-workspace-services/billing-service` | 3 | `list`, `read` | 按既有声明恢复 |
| `github-actions-console` | `ai-workspace-services/portal` | 3 | `list`, `read` | 按既有声明恢复 |
| `github-actions-content-service` | `ai-workspace-services/content-service` | 3 | `list`, `read` | 按既有声明恢复 |
| `github-actions-docs` | `ai-workspace-services/docs` | 3 | `list`, `read` | 按既有声明恢复 |
| `github-actions-gitops` | `ai-workspace-infra/gitops` | 3 | `list`, `read` | 按既有声明恢复 |
| `github-actions-platform-ops-toolkit-sit` | `ai-workspace-infra/platform-ops-toolkit`, `ai-workspace-infra/playbooks` | 2 | `create`, `delete`, `list`, `read`, `update` | 按既有声明恢复 |
| `github-actions-platform-ops-toolkit-uat` | `ai-workspace-infra/platform-ops-toolkit`, `ai-workspace-infra/playbooks` | 2 | `create`, `delete`, `list`, `read`, `update` | 按既有声明恢复 |
| `github-actions-platform-ops-toolkit-prod` | `ai-workspace-infra/platform-ops-toolkit`, `ai-workspace-infra/playbooks` | 2 | `create`, `list`, `read`, `update` | 按既有声明恢复 |
| `github-actions-postgresql` | `ai-workspace-services/postgresql` | 3 | `list`, `read` | 按既有声明恢复 |

同一策略可被多个环境角色引用，所以 30 个角色不对应 30 个策略。业务构建/GitOps 的 8 个策略为 read/list；Toolkit 的 3 个环境策略还包含既有的限定路径写入动作，并由 Playbooks 对应环境角色复用。不能将本次恢复统称为“全部只读”。

## 4. 自动化证据与待办矩阵

| 完成 | 检查项 | 状态 | 可复核证据 / 下一步 |
| --- | --- | --- | --- |
| [x] | GitHub issuer/discovery 与网络可达 | PASS | GitHub OIDC discovery/JWKS HTTPS 成功；GitOps 实际 CI 可登录 |
| [x] | 30 个普通角色 / 11 个策略恢复 | PASS（配置范围） | 固定来源、精确选择、无专项高权限角色 |
| [x] | 角色回读 | PASS | 30/30 与固定声明匹配 |
| [x] | 同输入幂等 | PASS | 最终重跑 exit 0、changed=0 |
| [x] | 生产 ref 与工作流边界单元测试 | PASS（本地六项） | 不接受 main/旧代际生产 tag、通配 repository/workflow、无关策略或默认策略 |
| [x] | GitOps SIT 真实登录 | PASS | 本页运行链接 |
| [ ] | GitOps UAT/PROD 真实登录 | NOT_RUN | 需要对应合法事件/ref 下的无业务副作用认证回执 |
| [ ] | 其余仓库分环境真实登录 | NOT_RUN | 不用另一仓库的成功冒充；不为验收擅自派发部署 |
| [ ] | 真实错误 repo/ref/workflow/audience 拒绝 | NOT_RUN | 使用受控 JWT 负向验证；不伪造签名或放宽绑定 |
| [ ] | 按实际消费者继续缩小 allowlist | 待审查 | Artifacts 当前枚举其原有匹配范围；文件数量不等于最小消费者集合 |

## 5. 下一轮可复用填写表

| 完成 | Repository / 环境 / role | 固定声明 SHA | 配置比对 | 允许登录 run_id / attempt | 错误身份拒绝证据 | Token TTL/策略核验 | 退出码 / 待办 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [ ] | `<repo>/<env>/<role>` | `<SHA>` | NOT_RUN | `<CI run URL>` | `<受控 evidence_id>` | `<无 Token 值>` | `<exit/null>` |

每轮记录带时区起止和精确选中角色。不得复制 root token、短期 JWT/Token、输出凭据内容或通过放宽 ref/工作流通配来让检查变绿。所有需要部署、迁移、写入权或云资源副作用的工作流仍按原审批与 owner 边界执行。
