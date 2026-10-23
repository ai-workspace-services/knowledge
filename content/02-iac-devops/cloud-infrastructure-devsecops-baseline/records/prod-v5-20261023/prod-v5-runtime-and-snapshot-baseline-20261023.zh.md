# PROD V5 运行基线与快照清单

核验日期：2026-10-23，Asia/Shanghai。直接复制 [V4 原版模板](../prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md) 的标题、表格列与章节顺序；V5 尚无运行回执的格位明确留为 NOT_RUN，后续持续按实际回执更新。[已合并 #191](https://github.com/ai-workspace-services/knowledge/pull/191)；[部署复盘](prod-v5-deployment-postmortem-20261023.zh.md)。

## 后续应用发布：r101，预检通过、实际部署仍受阻

最新状态（2026-10-23，用户主线核验）：目标 `104.64.208.209` 仅 22 端口监听，Docker 未安装，
owner journal 已存在；exit 4 后已实证控制端动态角色解析缺少 `ansible.posix`。安装 `ansible.posix 2.1.0`
后同一最小 syntax-check 从 exit 4 转为 exit 0；固定 ref 的公共入口 apply `60471` 运行中，尚未部署成功或 ready。该次不能沿用早期“主机写入前”的阶段结论，
也不能凭 journal 存在推断安装完成。四个版本 A 记录已更新，TTL 60、DNS only；公共 DNS 未改。
PG r101 已发布并通过隔离 smoke；目标 V5 的服务健康、运行镜像匹配与业务验收仍未通过。

本次文档基于最新 main `2dbd9d62869af1096d3f89e30800c2aa92450fde`，即已合并的
[#193](https://github.com/ai-workspace-services/knowledge/pull/193)。后续旧表保留各次样本来源；
当前交付引用与阻断以本文“追加执行回执：最新固定版本与 exit 4 阻断”为准。

public install wrapper `59b603a` precheck PASS、exit 0；真实 CMDB 108977826、五项 refs、policy valid。#507 已合并 `4af219e9486bdcd1c7cdb053795fa55e692efb29`（head `08ecf3`，用户最新回执），installer owner 独占 actual apply；首次实际执行已在主机写入前失败，修复后重试待回执。

| 项目 | r101 现场结果 |
| --- | --- |
| 发布路径 | installer owner 独占实际 apply；预检 PASS，部署回执待补 |
| GitOps | #507 已合并 `4af219e9486bdcd1c7cdb053795fa55e692efb29`，head `08ecf3`；owner 975693；历史 precheck `59b603a` PASS、exit 0 |
| Playbook | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Doco-CD | NOT_RUN；最后样本无 Docker/Caddy |
| Accounts | r101 / b423432dc5f993e5261423e27373703aaff48f2d；sha256:39716c2941b6f8ebbc0602589a59711d846234cb8313ae21254a91ba6073def7（已发布；运行匹配 NOT_RUN） |
| Console | r101 / 02607cf315570097606d90a8ba514fe37dcbe9e6；sha256:cc9b85339d82cefd264455c3d28c4e25dcd9e293378675855e23822730d5d0c5（已发布；运行匹配 NOT_RUN） |
| schema | 声明 2026102002；目标实际 schema/dirty NOT_RUN |
| 启动写入 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| 健康与版本 | NOT_RUN；尚无运行应用验收 |
| 未更新的服务 | V5 尚无运行应用；V4 保持服务和写入 |
| 数据核验 | NOT_RUN；无 V5 业务行数/指纹 |
| 配置核验 | precheck policy valid；运行时配置 hash 尚无回执 |
## 1. 环境与实际部署

本次 V5 证据（逐项更新）：

项目；现场结果

主机；Akamai Singapore，2 vCPU / 4 GiB / 80 GiB；替换后实例 108977826，目标地址 104.64.208.209（用户明确要求记录）
SSH / 初始化；最新交接 SSH 可连接、cloud-init 完成；最后样本仅 22 监听，无 Docker、Caddy、运行应用
部署路径；主线 owner 继续 SSH → Playbook → 固定 GitOps → Doco-CD 安装；本知识库任务未执行
GitOps；[#507](https://github.com/ai-workspace-infra/gitops/pull/507)，precheck 来源 `59b603a`，固定 Playbooks owner `975693`；public install wrapper 真实 precheck PASS、exit 0，真实 CMDB 108977826、五项 refs 和 policy valid。主线已合并 #507（`4af219e9486bdcd1c7cdb053795fa55e692efb29`；head `08ecf3`，用户最新回执）；installer owner 独占 actual apply；首次实际执行已在主机写入前失败，修复后重试待回执
Playbooks；[#732](https://github.com/ai-workspace-infra/playbooks/pull/732)、[#733](https://github.com/ai-workspace-infra/playbooks/pull/733) 已合并（最新交接）；不替代安装与 runtime 结果
服务与写入；V5 尚无运行验收；V4 继续承接公共服务和业务写入，公共 DNS 切换待验收及人工授权

| 项目 | 现场结果 |
| --- | --- |
| 主机 | Akamai Singapore；实例 108977826，104.64.208.209；最后样本 SSH 可用、仅 22 监听 |
| 平台 | Akamai Singapore；2 vCPU / 4 GiB / 80 GiB |
| 部署模式 | SSH → Playbook → 固定 GitOps → Doco-CD；actual apply 已尝试并在主机写入前 FAIL，修复重试 PENDING |
| 发布引用 | daily-build-2026.10.23-r101；候选制品，尚无运行引用 |
| GitOps 实际 SHA | #507 precheck 来源 59b603a；#507 已合并 `4af219e9486bdcd1c7cdb053795fa55e692efb29`（head `08ecf3`，用户最新回执），尚无 Doco-CD runtime revision |
| Doco-CD | NOT_RUN；最后样本无 Docker/Caddy |
| 独立数据盘 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| PostgreSQL 挂载 | NOT_RUN；无实际挂载回执 |
| 实际业务库 | NOT_RUN；最后样本 PG 数据目录不存在 |
| Caddy 主机配置 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Caddy 激活模式 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| 入口配置 SHA-256 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
## 2. 容器构件

本次 V5 证据（逐项更新）：

以下五项是已发布 r101 候选 pin，**不是运行容器清单**。来源为 GitOps V5 proposal 与用户制品交接；统一 tag `daily-build-2026.10.23-r101`。

服务；tag / source SHA；完整 digest

Accounts / ghcr.io/ai-workspace-services/accounts；b423432dc5f993e5261423e27373703aaff48f2d；39716c2941b6f8ebbc0602589a59711d846234cb8313ae21254a91ba6073def7
Billing / ghcr.io/ai-workspace-services/billing-service；77557d796a66dcd3373d7731125890bd91ebc5d3；14bbaee5ba37d85ddf243272ee2c3bed25603ee26ffd5c0b8d685cfe0e7a85a0
Console / ghcr.io/ai-workspace-services/console；02607cf315570097606d90a8ba514fe37dcbe9e6；cc9b85339d82cefd264455c3d28c4e25dcd9e293378675855e23822730d5d0c5
Content / ghcr.io/ai-workspace-services/docs；94e722c913a8c6e8adbb5b0bd363b20c9d3b4d08；e6e791437bd3b57a4dec0bc9dc2527b681dd52960b6f692be6ff16322018788e
PostgreSQL / ghcr.io/ai-workspace-services/postgresql；253d69a3ad19558a4bd272dee0509a498e091e24；56f4179bafafa52061ac21003dc80c1a0b7ceb63fffb2c7bd05f29237b62b85e

PostgreSQL registry OCI index 已验证，child manifest 前缀 `7f643d59`；chart 来源前缀 `9417`，release 已发布（用户交接，完整 child/chart SHA 待归档）。index、child manifest、image config 是不同层级；不将本地 image ID 作为 registry pin。较早 GHCR 代理推送失败属于历史尝试。五项联合 provenance、目标拉取和运行镜像匹配仍需新鲜回执；CI run ID 未提供，不填推测值。

| 服务 | tag / source SHA | 完整 digest |
| --- | --- | --- |
| Accounts | r101 / b423432dc5f993e5261423e27373703aaff48f2d | sha256:39716c2941b6f8ebbc0602589a59711d846234cb8313ae21254a91ba6073def7（已发布；运行匹配 NOT_RUN） |
| Billing | r101 / 77557d796a66dcd3373d7731125890bd91ebc5d3 | sha256:14bbaee5ba37d85ddf243272ee2c3bed25603ee26ffd5c0b8d685cfe0e7a85a0（已发布；运行匹配 NOT_RUN） |
| Console | r101 / 02607cf315570097606d90a8ba514fe37dcbe9e6 | sha256:cc9b85339d82cefd264455c3d28c4e25dcd9e293378675855e23822730d5d0c5（已发布；运行匹配 NOT_RUN） |
| PostgreSQL | r101 / 253d69a3ad19558a4bd272dee0509a498e091e24 | sha256:56f4179bafafa52061ac21003dc80c1a0b7ceb63fffb2c7bd05f29237b62b85e（已发布；运行匹配 NOT_RUN） |
| Caddy | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Doco-CD | NOT_RUN；最后样本无 Docker/Caddy | NOT_RUN；无运行镜像回执 |
## 3. 域名、SNI 与路由

本次 V5 证据（逐项更新）：

[IaC #461](https://github.com/ai-workspace-infra/iac_modules/pull/461) 修复 `8a0bb444` 的实际 apply 创建四条 A → `104.64.208.209`；Cloudflare API 已确认，重复 preview 四条均 `noop`，provider 幂等性 PASS，`public_aliases_modified=false`。

域名；当前解析归属；本轮 HTTPS/SNI 结果

console-selfhost-prod-v5.svc.plus；Google DoH A 已验证目标；早期回执 TTL 60、status 0；HTTPS/SNI、登录及 runtime NOT_RUN
accounts-selfhost-prod-v5.svc.plus；provider 已确认；独立查询超时/待补；NOT_RUN
billing-selfhost-prod-v5.svc.plus；provider 已确认；独立查询超时/待补；NOT_RUN
postgresql-selfhost-prod-v5.svc.plus；Google DoH A 已验证目标；DB 连接、隧道/TLS NOT_RUN；不是普通 HTTPS 页面

早期四域 NXDOMAIN 为 apply 前历史状态。本地 resolver 负缓存/代理路径仍可能返回 NXDOMAIN；其他查询超时不能当作记录不存在。尚不能声称所有 resolver 或全球传播均通过。公共别名仍指向 V4，后续人工切换单独留证。

| 域名 | 当前解析归属 | 本轮 HTTPS/SNI 结果 |
| --- | --- | --- |
| `console.svc.plus` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `accounts.svc.plus` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `billing.svc.plus` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `xworktech.com` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `www.xworktech.com` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `console-selfhost-prod-v4.svc.plus` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `accounts-selfhost-prod-v4.svc.plus` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `billing-selfhost-prod-v4.svc.plus` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `postgresql-selfhost-prod-v4.svc.plus` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
## 4. 运行配置、身份与权威引用

本次 V5 证据（逐项更新）：

只记录路径、字段和状态，不记录任何值。以下路径由用户明确要求写入本白皮书。

用途；Vault KV v2 API 路径；CLI 路径 / 字段

Cloudflare serverless API；`kv/data/prod/serverless/cloudflare`；`kv/prod/serverless/cloudflare`：`ACCOUNT_ID`、`API_TOKEN`
既有 Selfhost DNS；`kv/data/CICD`；`kv/CICD`：`DNS_API_TOKEN`；与上行用途分开
PROD SSH deploy key；`kv/data/CICD/prod`；`kv/CICD/prod`：`SSH_PRIVATE_DEPLOY_KEY_B64`、`SSH_PUBLIC_DEPLOY_KEY_B64`

[写入脚本（固定提交）](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/86366b2c/scripts/vault/write-prod-ssh-deploy-key.sh)：`scripts/vault/write-prod-ssh-deploy-key.sh`，Toolkit commit `86366b2c`，branch `feature/vault-prod-ssh-key-writer-20261023`。脚本已创建并完成语法检查；[Toolkit PR #1428](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/1428) 本次远端复核为 MERGED，merge commit `ae917b221b61845fca8af4e9f63696c63d80d82f`。本任务未执行，不能据此声称生产凭据已更新。链接使用仓库路径，不包含操作员本机 home。

授权操作员从 toolkit checkout 使用：

```bash
VAULT_ADDR=https://vault.svc.plus bash scripts/vault/write-prod-ssh-deploy-key.sh
```

脚本派生公钥并比对本机 key pair，只 patch 两个 B64 字段。本任务未执行脚本、未写 Vault。最新只读 keys 观察确认 public 字段现在存在；Vault 中私钥/公钥是否匹配 **未验证**，字段存在不构成配对通过。实际运行时引用由固定 owner 校验，值与访问就绪需独立证据。

| 项目 | 核验结果／合同 |
| --- | --- |
| Accounts 实际 DB 角色 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Billing 实际 DB 角色 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| 数据库密码权威来源 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| 共享服务令牌权威来源 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Accounts `DATABASE_BACKGROUND_WRITERS` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Billing `DATABASE_BACKGROUND_WRITERS` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Billing `BILLING_INGEST_MODE` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Billing `DEFAULT_REGION` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Accounts 共享租户域 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Console `RUNTIME_HOSTNAME` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Accounts 配置挂载 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
### Stripe Sandbox / Live 配置合同（2026-10-21 补记）

| 配置项 | Sandbox / Test | Live | 说明 |
| --- | --- | --- | --- |
| Webhook URL | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| API secret key | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Webhook signing secret | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
## 5. 数据与 schema 基线

本次 V5 证据（逐项更新）：

V5 数据目录在最后主机样本中不存在。没有当前业务库、schema dirty 状态、行数、指纹或迁移 run ID。proposal 所含 schema `2026102002` 是声明输入，不能写成目标实际 schema。源 V4 计数继续保留原采样时间，不复制为 V5 数据事实。迁移及目标对账 **NOT_RUN**。

| 对象 | 数量／版本 |
| --- | --- |
| schema | 声明 2026102002；目标实际 schema/dirty NOT_RUN |
| `users` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `subscription_records` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `subscriptions` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `account_quota_states` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `traffic_minute_buckets` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `billing_ledger` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
## 6. 快照清单：完成状态必须分开

本次 V5 证据（逐项更新）：

项目；状态；实际位置 / 校验 / run ID

V5 DB / globals 加密备份；NOT_CREATED；无
V5 配置及镜像 manifest；NOT_CREATED；无
V5 Vault 加密快照；NOT_CREATED；无；共享 Vault 恢复须独立范围
V5 SHA256SUMS 与主机外副本；NOT_CREATED；无
V5 隔离恢复与应用连接验收；NOT_RUN；无
V4 历史备份；仅引用 V4 基线第 6 节；不扩大为最新 V5 快照

实际 V5 快照尚未创建；不生成看似真实的目录、文件名、时间戳或 run ID。后续应归档一致性边界、schema/行指纹、加密文件与校验、独立恢复、实际应用连接和主机外副本回执。

### V2 历史全量快照

### V3 在线快照与跨机恢复

### V4 含业务数据的历史备份及隔离恢复

| 项目 | 回执事实 |
| --- | --- |
| V5 备份 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 归档 SHA-256 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 完成时间 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 隔离恢复库 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 数据恢复结果 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 恢复前后业务行指纹 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 恢复 schema 指纹 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 权限指纹 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 业务验收边界 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
### 最新发现的 V5 全量快照候选

| 文件 | 本轮重新计算的 SHA-256 |
| --- | --- |
| V5 归档（尚未创建） | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 归档（尚未创建） | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 归档（尚未创建） | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 归档（尚未创建） | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
## 7. 当前证据限制

本次 V5 证据（逐项更新）：

case / action；状态；run ID / 证明

DNS provider apply + repeat preview；PASS（主线交接）；run ID 未提供；CF 四记录及四 noop 回执
Google DoH Console + PostgreSQL；PASS（限定两域）；run ID 未提供；其余域独立验证 PENDING
SSH key 字段可见；OBSERVED；public key 字段存在；pair-match NOT_RUN
SSH 写入脚本；SYNTAX_CHECKED / NOT_EXECUTED_BY_THIS_TASK；无 Vault 写入回执
GitOps #507 public install wrapper precheck；PASS，exit 0；`59b603a`；真实 CMDB 108977826、五项 refs、policy valid；run ID 未提供
#507 main merge / 固定引用安装；已合并 `4af219e9486bdcd1c7cdb053795fa55e692efb29`，head `08ecf3`；actual apply FAIL（主机写入前）；installer owner 独占执行，修复重试 PENDING
一次性实际部署后立即 runtime tests；部署尝试 FAIL，runtime tests NOT_RUN；无 run ID；不以离线 manifest PASS 代替
DB 初始化、迁移、权限与数据对账；NOT_RUN；无运行回执
登录、账务、采集、恢复与稳定观察；NOT_RUN；无运行回执
公共 DNS / 写入切换；NOT_RUN；验收后人工授权

后续 case 结果绑定固定 source SHA、镜像 digest、owner SHA、目标、执行时间与真实 run ID。未获结果继续保留 NOT_RUN/PENDING；本轮知识库变更不执行 installer，不创建快照或迁移。


## 追加执行回执：合并版预检与 SSH 连接阶段失败

2026-10-23 主线最新确认；以下更新覆盖前文旧采样中的待执行状态，不改写旧回执的来源。

| case / action | 实际结果 | 边界与后续动作 |
| --- | --- | --- |
| 合并版 public installer --check | PASS，exit 0 | GitOps `4af219e9486bdcd1c7cdb053795fa55e692efb29`；不同于此前 `59b603a` 预检，run ID 未提供 |
| 完整 installer actual apply | FAIL，主机写入前 | `Owner stage failed; private output withheld`；未产生 Docker/Caddy 部署或 runtime 验收 |
| 主线隔离语法检查 | PASS | 仅证明脚本语法，不证明连接与部署成功 |
| 实际 Ansible 初次 ping | FAIL，exit 4 | SSH banner timeout；手工 SSH 偶尔成功，连接状态并非持续稳定 |
| 显式 identity 的 Ansible 探针 | PASS，changed=false | `-T30`，显式 `id_ed25519`；只证明该次连接探针成功，无应用安装回执 |
| 完整 installer 默认 SSH timeout | FAIL | 默认 10 秒连接超时在主机写入前失败；不能用 30 秒独立探针替代完整 installer 重试 |
| owner 修复 | 实现中 / PENDING | 有界 connect timeout/retry 与脱敏 failure-stage；尚无修复后完整 apply 回执，不记为已修复 |

最后主机样本仍无 Docker/Caddy。实际迁移、runtime 回归和 V5 快照仍未执行/创建；V4 公共服务和业务写入保持原状态。主线 installer owner 独占生产执行，本知识库 PR 仅更新回执。

## 追加执行回执：最新固定版本与 exit 4 阻断

2026-10-23 更新。PR/tag 状态由本次远端查询确认；主机、DNS provider 与 smoke 事实来自用户主线核验，
本知识库任务没有再次执行 installer、SSH 或 Vault 读取。新结果不能反向改写早期失败尝试。

| case / action | 当前事实 | 验证边界 / 下一项证据 |
| --- | --- | --- |
| Playbooks owner #734 | MERGED，`19f4c3265dc66a9f561bad0441fd17e40649bc6b` | 有界 SSH timeout/retry 与脱敏阶段修复已合并；尚无完整安装成功回执 |
| GitOps #509 / 不可变 tag | MERGED，`b10d14d35ce77b4fa96d5ad6e7699ea8ec8441f2`；`v2026.10.23-v5-r1` 指向同一提交 | 固定发布引用已核实，目标实际运行 revision 未取得 |
| 先前 launcher binding 尝试 | apply 曾通过 SSH 后在 Vault resolve 阶段失败；launcher 导出 `VAULT_TOKEN`，policy 要求 `V5_CONTROL_PLANE_VAULT_TOKEN` | 该次操作员环境变量绑定不一致；13 个引用字段非空、格式有效。不是凭据无效或 role 格式错误的证据；不将它当作当前 exit 4 的已确认根因 |
| launcher lookup 修正与后续重试 | 主线报告修正并重试；交接标识 `57636` | 未知是否为 CI run ID，不构造 Actions 链接；无最终成功回执 |
| 最新主机样本 | 仅 22 监听，Docker 未安装，owner journal 存在 | journal 证明存在执行记录，不证明应用部署；当前失败阶段需脱敏 journal 回执 |
| 控制端依赖实证 | 初始只有 `community.hashi_vault 7.1`，缺少 `ansible.posix`；最小 `import_role vhosts/docker`、bootstrap=false 的 syntax-check exit 4 | `common/tasks/firewall_ports.yml:56` 不能解析 `ansible.posix.firewalld`。false when 不免除 parse 依赖；该次根因是控制端 collection 缺失，不是 SSH 不可达或云防火墙 |
| 顶层 syntax-check 覆盖缺口 | 原 owner 顶层检查未展开该动态依赖 | 增加动态角色解析 case，不能只检查顶层入口 |
| 控制端依赖补齐及同一复测 | `ansible.posix 2.1.0` 已安装；同一最小 syntax-check 从 exit 4 转为 exit 0 | 只证明该动态解析阻断已解除；不代表完整 installer 或目标运行健康通过 |
| 最新公共入口 actual apply | 固定 ref 重试 `60471` 运行中 | 标识类型未确认，不构造 Actions run 链接；最终退出码、完整阶段及 runtime 结果 PENDING，未部署完成，不标 ready |
| 四个版本 A 记录 | 已更新至目标地址，TTL 60、DNS only；公共 DNS 未动 | provider 状态来自主线；不扩大为全部 resolver、TLS 或应用健康通过 |
| PostgreSQL r101 | 已发布；隔离 smoke PASS | 独立构件验证，不代表 V5 已拉取、初始化或服务健康通过；smoke run ID 未提供 |
| V5 runtime / 迁移 / 快照 | 健康验收未通过；迁移 NOT_RUN；快照 NOT_CREATED | 待安装成功、运行镜像与挂载核验、数据库健康、应用回归与独立恢复证据 |

控制端前置条件应固定并核验 collections：保留当前 `community.hashi_vault 7.1` 的已知版本事实，
显式安装固定 `ansible.posix 2.1.0`；持久 dependency manifest/owner 预检是否已实现仍待相应提交回执，
不能把本地安装写成仓库修复已合并。动态角色解析 case 必须在相同固定 owner/ref 下，使用
`import_role vhosts/docker` 和 bootstrap=false 重现解析路径，记录完整 collection 版本及 syntax-check
exit code；缺失 collection 应在主机操作前失败，安装后应复测原 case。云端安装后仍需独立验收。

当前 installer apply `60471` 尚在运行，目标服务未验收。此前 exit 4 的已实证原因是控制端动态角色
collection 缺失；旧 SSH timeout 和 launcher binding 保留为各自历史尝试，不能替代此次根因。
主线 owner 继续实际安装；知识库只补充
脱敏事实。公共流量、写入和最终切换仍由 V4 保持，切换须验收后独立人工授权。

## 历代记录（V4 → V3 → V2 → V1 初始记录）

1. [V4：运行基线与快照清单](../prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md)。
2. [V3：V2→V3 快照恢复、切库与平滑升级验收](../prod-v2-v3-20261019/v2-to-v3-snapshot-refresh-20261019.zh.md)。
3. [V2：冷备、容灾与跨机恢复白皮书](../prod-v2-v3-20261019/web-saas-prod-v2-cold-backup-disaster-recovery-whitepaper.zh.md)。
4. V1 初始记录：当前仓库未找到明确标记为 PROD V1 的独立记录，链接待定位后补齐；现有[云基础设施 DevSecOps 基线方法论](../../09-cloud-infrastructure-devsecops-baseline-closing-the-loop.md)是未标代际的通用基线，不将其冒称 V1 运行记录。

