# PROD V5 运行基线与快照清单

记录日期：2026-10-23，Asia/Shanghai。沿用 [V4 基线模板](../prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md) 的七节结构。本文按最新用户交接及本地声明记录证据；远端 API 本轮网络失败，未独立刷新 PR 状态。关联[已合并 #191 部署复盘](https://github.com/ai-workspace-services/knowledge/pull/191)与[复盘正文](prod-v5-deployment-postmortem-20261023.zh.md)。历史记录保留原采样边界。

## 1. 环境与实际部署

| 项目 | 最新证据及边界 |
| --- | --- |
| 主机 | Akamai Singapore，2 vCPU / 4 GiB / 80 GiB；替换后实例 108977826，目标地址 104.64.208.209（用户明确要求记录） |
| SSH / 初始化 | 最新交接 SSH 可连接、cloud-init 完成；最后样本仅 22 监听，无 Docker、Caddy、运行应用 |
| 部署路径 | 主线 owner 继续 SSH → Playbook → 固定 GitOps → Doco-CD 安装；本知识库任务未执行 |
| GitOps | [#507](https://github.com/ai-workspace-infra/gitops/pull/507)，交接 head `59b603a`，固定 Playbooks owner `975693`；实际 `--check`、main 合并及部署回执 PENDING |
| Playbooks | [#732](https://github.com/ai-workspace-infra/playbooks/pull/732)、[#733](https://github.com/ai-workspace-infra/playbooks/pull/733) 已合并（最新交接）；不替代安装与 runtime 结果 |
| 服务与写入 | V5 尚无运行验收；V4 继续承接公共服务和业务写入，公共 DNS 切换待验收及人工授权 |

## 2. 容器构件

以下五项是已发布 r101 候选 pin，**不是运行容器清单**。来源为 GitOps V5 proposal 与用户制品交接；统一 tag `daily-build-2026.10.23-r101`。

| 服务 / registry repository | source SHA | digest（sha256） |
| --- | --- | --- |
| Accounts / ghcr.io/ai-workspace-services/accounts | b423432dc5f993e5261423e27373703aaff48f2d | 39716c2941b6f8ebbc0602589a59711d846234cb8313ae21254a91ba6073def7 |
| Billing / ghcr.io/ai-workspace-services/billing-service | 77557d796a66dcd3373d7731125890bd91ebc5d3 | 14bbaee5ba37d85ddf243272ee2c3bed25603ee26ffd5c0b8d685cfe0e7a85a0 |
| Console / ghcr.io/ai-workspace-services/console | 02607cf315570097606d90a8ba514fe37dcbe9e6 | cc9b85339d82cefd264455c3d28c4e25dcd9e293378675855e23822730d5d0c5 |
| Content / ghcr.io/ai-workspace-services/docs | 94e722c913a8c6e8adbb5b0bd363b20c9d3b4d08 | e6e791437bd3b57a4dec0bc9dc2527b681dd52960b6f692be6ff16322018788e |
| PostgreSQL / ghcr.io/ai-workspace-services/postgresql | 253d69a3ad19558a4bd272dee0509a498e091e24 | 56f4179bafafa52061ac21003dc80c1a0b7ceb63fffb2c7bd05f29237b62b85e |

PostgreSQL registry OCI index 已验证，child manifest 前缀 `7f643d59`；chart 来源前缀 `9417`，release 已发布（用户交接，完整 child/chart SHA 待归档）。index、child manifest、image config 是不同层级；不将本地 image ID 作为 registry pin。较早 GHCR 代理推送失败属于历史尝试。五项联合 provenance、目标拉取和运行镜像匹配仍需新鲜回执；CI run ID 未提供，不填推测值。

## 3. 域名、SNI 与路由

[IaC #461](https://github.com/ai-workspace-infra/iac_modules/pull/461) 修复 `8a0bb444` 的实际 apply 创建四条 A → `104.64.208.209`；Cloudflare API 已确认，重复 preview 四条均 `noop`，provider 幂等性 PASS，`public_aliases_modified=false`。

| 版本域名 | 外部解析证据 | 服务验收 |
| --- | --- | --- |
| console-selfhost-prod-v5.svc.plus | Google DoH A 已验证目标；早期回执 TTL 60、status 0 | HTTPS/SNI、登录及 runtime NOT_RUN |
| accounts-selfhost-prod-v5.svc.plus | provider 已确认；独立查询超时/待补 | NOT_RUN |
| billing-selfhost-prod-v5.svc.plus | provider 已确认；独立查询超时/待补 | NOT_RUN |
| postgresql-selfhost-prod-v5.svc.plus | Google DoH A 已验证目标 | DB 连接、隧道/TLS NOT_RUN；不是普通 HTTPS 页面 |

早期四域 NXDOMAIN 为 apply 前历史状态。本地 resolver 负缓存/代理路径仍可能返回 NXDOMAIN；其他查询超时不能当作记录不存在。尚不能声称所有 resolver 或全球传播均通过。公共别名仍指向 V4，后续人工切换单独留证。

## 4. 运行配置、身份与权威引用

只记录路径、字段和状态，不记录任何值。以下路径由用户明确要求写入本白皮书。

| 用途 | Vault KV v2 API 路径 | CLI 路径 / 字段 |
| --- | --- | --- |
| Cloudflare serverless API | `kv/data/prod/serverless/cloudflare` | `kv/prod/serverless/cloudflare`：`ACCOUNT_ID`、`API_TOKEN` |
| 既有 Selfhost DNS | `kv/data/CICD` | `kv/CICD`：`DNS_API_TOKEN`；与上行用途分开 |
| PROD SSH deploy key | `kv/data/CICD/prod` | `kv/CICD/prod`：`SSH_PRIVATE_DEPLOY_KEY_B64`、`SSH_PUBLIC_DEPLOY_KEY_B64` |

[写入脚本（仓库相对路径）](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/main/scripts/vault/write-prod-ssh-deploy-key.sh)：`scripts/vault/write-prod-ssh-deploy-key.sh`。脚本已创建并完成语法检查，尚不能据此宣称已合入 main；链接是预期仓库路径，不包含操作员本机 home。

授权操作员从 toolkit checkout 使用：

```bash
VAULT_ADDR=https://vault.svc.plus bash scripts/vault/write-prod-ssh-deploy-key.sh
```

脚本派生公钥并比对本机 key pair，只 patch 两个 B64 字段。本任务未执行脚本、未写 Vault。最新只读 keys 观察确认 public 字段现在存在；Vault 中私钥/公钥是否匹配 **未验证**，字段存在不构成配对通过。实际运行时引用由固定 owner 校验，值与访问就绪需独立证据。

## 5. 数据与 schema 基线

V5 数据目录在最后主机样本中不存在。没有当前业务库、schema dirty 状态、行数、指纹或迁移 run ID。proposal 所含 schema `2026102002` 是声明输入，不能写成目标实际 schema。源 V4 计数继续保留原采样时间，不复制为 V5 数据事实。迁移及目标对账 **NOT_RUN**。

## 6. 快照清单：完成状态必须分开

| 项目 | 状态 | 实际位置 / 校验 / run ID |
| --- | --- | --- |
| V5 DB / globals 加密备份 | NOT_CREATED | 无 |
| V5 配置及镜像 manifest | NOT_CREATED | 无 |
| V5 Vault 加密快照 | NOT_CREATED | 无；共享 Vault 恢复须独立范围 |
| V5 SHA256SUMS 与主机外副本 | NOT_CREATED | 无 |
| V5 隔离恢复与应用连接验收 | NOT_RUN | 无 |
| V4 历史备份 | 仅引用 V4 基线第 6 节 | 不扩大为最新 V5 快照 |

实际 V5 快照尚未创建；不生成看似真实的目录、文件名、时间戳或 run ID。后续应归档一致性边界、schema/行指纹、加密文件与校验、独立恢复、实际应用连接和主机外副本回执。

## 7. case / action / 当前证据限制

| case / action | 状态 | run ID / 证明 |
| --- | --- | --- |
| DNS provider apply + repeat preview | PASS（主线交接） | run ID 未提供；CF 四记录及四 noop 回执 |
| Google DoH Console + PostgreSQL | PASS（限定两域） | run ID 未提供；其余域独立验证 PENDING |
| SSH key 字段可见 | OBSERVED | public key 字段存在；pair-match NOT_RUN |
| SSH 写入脚本 | SYNTAX_CHECKED / NOT_EXECUTED_BY_THIS_TASK | 无 Vault 写入回执 |
| GitOps #507 actual --check | PENDING / NOT_RUN | 尚无实际命令回执 |
| #507 main merge / 固定引用安装 | PENDING / NOT_RUN | 主线 owner 继续执行；无运行容器证明 |
| 一次性实际部署后立即 runtime tests | PENDING / NOT_RUN | 无 run ID；不以离线 manifest PASS 代替 |
| DB 初始化、迁移、权限与数据对账 | NOT_RUN | 无运行回执 |
| 登录、账务、采集、恢复与稳定观察 | NOT_RUN | 无运行回执 |
| 公共 DNS / 写入切换 | NOT_RUN | 验收后人工授权 |

后续 case 结果绑定固定 source SHA、镜像 digest、owner SHA、目标、执行时间与真实 run ID。未获结果继续保留 NOT_RUN/PENDING；本轮知识库变更不执行 installer，不创建快照或迁移。

