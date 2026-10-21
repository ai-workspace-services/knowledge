# PROD V4 运行基线与快照清单

核验日期：2026-10-21，Asia/Shanghai。与[升级复盘](v3-v4-upgrade-retrospective-20261021.zh.md)、[回归清单](regression-and-closure-checklist-20261021.zh.md)配套使用。本文是有时间边界的运维记录，不是第二套配置源。

## 后续应用发布：r8，13:23–13:24

以下为 2026-10-21 13:23:50 +08:00 的新核验。原第 1–7 节保留此前的采样和快照事实，其中 r4 构件不再代表当前 Accounts/Console 版本。权威期望状态为 [GitOps r8](https://github.com/ai-workspace-infra/gitops/tree/v2026.10.21-r8/compose/web-saas)，本文不生成第二套配置。

| 项目 | r8 现场结果 |
| --- | --- |
| 发布路径 | SSH → Playbook → 固定 GitOps → Doco-CD；本次未使用 CI 部署 |
| GitOps | [PR #487](https://github.com/ai-workspace-infra/gitops/pull/487)，tag `v2026.10.21-r8`，SHA `e5e11d2718c9f992c760b6c542d3c40b48fdf7bb` |
| Playbook | [select-doco-cd-release.yml](https://github.com/ai-workspace-infra/playbooks/blob/c2203a388efa0eb0815c6594509137df96532cc9/select-doco-cd-release.yml)，选择既有 V4 reconciler；云控制面核定后生成单次临时 inventory，执行后删除 |
| Doco-CD | target=`prod-v4-stripe-sandbox`；13:23:30 +08:00 报告成功，运行容器标签的 ref/SHA 与固定 tag 一致 |
| Accounts | source `21de352383d183be5bbbf5b3109a19c52a408abe`；digest `sha256:b23c205a72cb580262a62916cee1a8d54ee9a5639327496283ac23532b960baf` |
| Console | 保留 r7 source `422c74e695de04bfc53b962ba0bbc5440bac794b`；digest `sha256:590b6cbe4d4d68d16b7d4c85f646cfa87833e9e47cd1a998ec3a1638e0c756a2` |
| schema | `2026102002`，dirty=false；无新增迁移，无 schema SQL 变化 |
| 启动写入 | `schema_management=external`；bootstrap/background writers/proxy UUID rotator 均 false |
| 健康与版本 | Accounts ping/readyz、Console ping、Billing readyz 均 200；Accounts source/image 与锁定构件一致 |
| 未更新的服务 | Console、Billing、PostgreSQL、Caddy 的镜像及启动时间与发布前相同 |
| 数据核验 | 订阅、订阅记录、套餐、账户计费配置、发票、付款共六表的行数与稳定内容指纹前后一致；不将此扩大为全部用量表静止 |
| 配置核验 | 受保护的 account/Caddy 配置及 secrets/business-database/internal-service 环境文件 hash 前后一致；不记录值 |

r7 已修复首次 Free→Plus 激活：Free 的 5GB 耗尽后获得完整新付费周期 20GB，已消费额度不会因重投事件补满。r8 增加 [Accounts #257 模式隔离](https://github.com/ai-workspace-services/accounts/pull/257) 和 [#258 完成记录失败重试](https://github.com/ai-workspace-services/accounts/pull/258)：错误支付模式、缺失事件字段和不支持的 Connect 上下文在持久化前拒绝；完成记录写入失败返回 503，不能误报 200。

本轮 Stripe MCP 仅选择 svc.plus Sandbox：三个当前活动 Price 与本地目录匹配，分别为 Plus ¥20/月20GiB、Pro ¥50/月50GiB、Pro ¥500/年不限流量。Canonical 测试端点仍为 `https://accounts.svc.plus/api/billing/stripe/webhook`；12:48:23 的 Checkout 和 12:48:08 的 invoice 投递均 200。周窗口 25 次尝试中有 14 次历史失败，不能冒充最新事件仍失败，也不能写成整周零失败。旧 UAT 端点未改动。r8 未签名请求返回 401 `invalid_signature`，是预期的安全拒绝，不是新的真实 Stripe 投递失败。

凭据继续引用 `kv/prod/billing-service` 的 `SANDBOX_STRIPE_SECRET_KEY`、`SANDBOX_STRIPE_WEBHOOK_SECRET`；部署版本不构成 Stripe 支付模式，不新增 V3/V4 secret 字段。本次没有新付款、事件重投、手工修改业务行、Live 操作或密钥变更。

验证分层：[Accounts #259](https://github.com/ai-workspace-services/accounts/pull/259) 的本地 PostgreSQL 17 副本只含 public 结构、四条必要套餐目录和合成测试身份，内部网络无主机端口，未复制原用户/财务记录/Stripe 凭据。三个套餐均通过完整激活、未付拒绝、节点 API 403→200、finish 故障后重建 handler 重试、财务去重和消费保留。provider 为 loopback fixture，不等同真实新付款或 Agent 连接验收。独立公共回调入口与 Agent 仍待 [F9](https://github.com/ai-workspace-services/.github/issues/36)；并发/崩溃恢复、退款事件订阅及完整端到端矩阵继续保留。

回滚只需通过相同 Playbook 选择保留的 `v2026.10.21-r7`；不执行数据库 down/覆盖恢复，不撤销已有金融事实。第 6 节的备份与恢复清单仍是其原时间边界，本轮没有新增完整环境快照或恢复演练，不能把本次结构副本测试记作业务备份恢复验收。

## 1. 环境与实际部署

| 项目 | 现场结果 |
| --- | --- |
| 主机 | `web-saas-prod-v4`；GCP 控制面及 SSH hostname 一致 |
| 平台 | GCP，`open-platform-prod / asia-east1-a` |
| 部署模式 | SSH → Playbook → 固定 GitOps → Doco-CD；本次现场核验未使用 CI 部署 |
| 发布引用 | `v2026.10.21-r4` 是历史候选引用，不足以代表当前所有运行容器 |
| GitOps 实际 SHA | `5c602b6874e9cf2c37be43dd02c4472c1234778b`，Doco-CD 当前 revision |
| Doco-CD | target=`prod-v4-stripe-sandbox`，interval=60 秒；2026-10-21 12:28–12:31 +08 连续成功任务 |
| 独立数据盘 | 50 GiB，ext4，挂载 `/data`；根盘约 20 GiB |
| PostgreSQL 挂载 | `/data/postgresql` → `/var/lib/postgresql/data`，读写 |
| 实际业务库 | `account`，PostgreSQL 17.10 |
| Caddy 主机配置 | `/etc/xcontrol/web-saas-recovery/Caddyfile`；路径含 recovery 不代表当前仍是候选模式 |
| Caddy 激活模式 | `generation=prod-v4`、`runtime_mode=primary`、target 与主机一致 |
| 入口配置 SHA-256 | `42f01244e16fa3fe3274fedfd52e443d4287dd2f7f1b437f7f431539c3348d83` |

GitOps 声明见 [compose/web-saas](https://github.com/ai-workspace-infra/gitops/tree/5c602b6874e9cf2c37be43dd02c4472c1234778b/compose/web-saas)。该 revision 对应提交 `fix: release paid sandbox activation recovery to V4 (#486)`。本次没有核实一个同时绑定所有当前服务镜像的统一不可变 release tag；应用镜像各自的 tag/digest 见下表。此前 `prod-v4-acceptance-2026.10.21-r1`、`v2026.10.21-r4` 和分支演练 SHA 都是历史引用，不能冒充当前运行版本。

## 2. 容器构件

以下为实际容器 `Config.Image` 与本机镜像 digest 交叉核实结果。六个服务容器运行；PostgreSQL 和 Doco-CD 带 healthy 状态。Content、Stunnel、OTel 未出现在本次运行容器清单，不能沿抄 V2 模板为“已运行”。

| 服务 | tag / source SHA | 完整 digest |
| --- | --- | --- |
| Accounts | `sha-1a82ca1621dbb2959f289de5b14723a157999515` | `sha256:462492053d8e5c8effc4fb34a678a1aee536cdcb525847f724f55f080214ad61` |
| Billing | `sha-77557d796a66dcd3373d7731125890bd91ebc5d3` | `sha256:974a012cd032a291c495120f70dc1da1dbe35d05c7554b4912836cac983d438b` |
| Console | `sha-422c74e695de04bfc53b962ba0bbc5440bac794b` | `sha256:590b6cbe4d4d68d16b7d4c85f646cfa87833e9e47cd1a998ec3a1638e0c756a2` |
| PostgreSQL | `sha-7759f4513e1710e86332795b611507bbed37ea39` | `sha256:f97857bd59c1fc55e3be3942b2c8f5554a8e9ee1d08bf3e834940c33189a141c` |
| Caddy | `959d6c8` | `sha256:9895385033fea2bdb445841b45f37e6cd58b9e071a16e4c147e483abb74a0acf` |
| Doco-CD | digest 固定，无需推断 tag | `sha256:46f3e44106fd0f4f30bc450682038509484d9aa28916edd6039b0af45bdc1cec` |

本表来自 2026-10-21 12:32 +08 的运行容器只读盘点；Accounts、Console 于 12:19 +08 左右启动，Billing 沿用前一日运行容器。当前运行版本及已测试版本并非始终一致；应用 tag 不等同于 GitOps revision。回退构件先保留当前上述 digest 和此前固定声明，业务库的回退需独立评估。

## 3. 域名、SNI 与路由

核验边界：2026-10-21 12:36 +08；DNS 解析和 HTTPS/SNI 均为只读检查。当前根域及 `www` 均指向 V4（`35.229.188.193`）。

| 域名 | 当前解析归属 | 本轮 HTTPS/SNI 结果 |
| --- | --- | --- |
| `console.svc.plus` | V4 CNAME → `console-selfhost-prod-v4.svc.plus` → `35.229.188.193` | `/login` 200；证书主机名校验通过 |
| `accounts.svc.plus` | V4 CNAME → `accounts-selfhost-prod-v4.svc.plus` → `35.229.188.193` | `/readyz` 200；API 服务，证书主机名校验通过 |
| `billing.svc.plus` | V4 CNAME → `billing-selfhost-prod-v4.svc.plus` → `35.229.188.193` | `/readyz` 200；API 服务，证书主机名校验通过 |
| `xworktech.com` | V4 A → `35.229.188.193` | `/` 200；证书主机名校验通过 |
| `www.xworktech.com` | V4 A → `35.229.188.193` | 301 到 `https://xworktech.com/`；证书主机名校验通过 |
| `console-selfhost-prod-v4.svc.plus` | V4 A → `35.229.188.193` | `/login` 200；证书主机名校验通过 |
| `accounts-selfhost-prod-v4.svc.plus` | V4 A → `35.229.188.193` | `/readyz` 200；API 版本别名，证书主机名校验通过 |
| `billing-selfhost-prod-v4.svc.plus` | V4 A → `35.229.188.193` | `/readyz` 200；API 版本别名，证书主机名校验通过 |
| `postgresql-selfhost-prod-v4.svc.plus` | V4 A → `35.229.188.193` | DB 预留别名；不是普通 HTTPS 服务，本轮未验证数据库隧道/TLS |

三个公共 `svc.plus` SNI、两个品牌域名及三个版本 HTTPS 别名均使用正常 CA/主机名校验通过；`/readyz` 只证明 API 基础就绪，不代表写入、OAuth、Webhook 或端到端业务验收通过。证书有效期核验至 2027-01-05（`svc.plus` 与品牌证书分别略有差异）。

此前记录的品牌域名仍指向 V3 已过时；本节以上述 12:36 +08 只读核验为当前状态。DNS 变更审批和历史操作回执见[品牌 DNS 交接记录](brand-dns-handoff-20261021.zh.md)。本轮没有修改 DNS。

Caddy 的证书目录 `/etc/xcontrol/tls` 为只读挂载；Caddyfile 也为只读挂载。03:09 正式入口激活后，Accounts 与 Console 采用正常业务代理规则；Billing 仅开放受应用 Token 鉴权的 `POST /v1/ingest/snapshots` 及探针。数据库不作为普通 HTTPS 页或直接公网数据库开放。

## 4. 运行配置、身份与权威引用

| 项目 | 核验结果／合同 |
| --- | --- |
| Accounts 实际 DB 角色 | `account_user`，库 `account` |
| Billing 实际 DB 角色 | `account_user`，库 `account` |
| 数据库密码权威来源 | `kv/prod/databases` → `account_pg_password`；只记录路径和 Key |
| 共享服务令牌权威来源 | `kv/prod/accounts/runtime` → `INTERNAL_SERVICE_TOKEN`；Accounts/Billing/Console/Agent 共用此 Key |
| Accounts `DATABASE_BACKGROUND_WRITERS` | **false** |
| Billing `DATABASE_BACKGROUND_WRITERS` | **false** |
| Billing `BILLING_INGEST_MODE` | `push`，保留 Xray Exporter → Vector → Billing |
| Billing `DEFAULT_REGION` | `jp` |
| Accounts 共享租户域 | `svc.plus` |
| Console `RUNTIME_HOSTNAME` | `console-selfhost-prod-v4.svc.plus` |
| Accounts 配置挂载 | 主机 `account.yaml` → `/app/config/account.yaml`，只读 |

业务写入权限、后台任务开关、入口方法限制及实际进程身份是四项独立验收。后台开关 false 不意味着 API 完全不能写入；正式 Caddy 模式也不会自动打开后台任务。

对 `users`、`subscriptions`、`traffic_minute_buckets`、`billing_ledger` 检查，`account_user` 均具备 SELECT/INSERT/UPDATE/DELETE。角色不是 superuser，不具备 createdb/createrole。本轮只查询权限，未试写生产业务数据。

`readonly_release` 只用于快照、迁移读取及审计；不可注入业务连接。现场仍存在 `generation_auth`、`generation_app` 角色对象，业务连接已不使用它们；是否可撤销登录/回收对象需先核验依赖，不能在文档任务中直接删除。`recovery_app` 未在本次指定角色查询中出现。

其他凭据引用沿用所属声明：OAuth、SMTP、Billing 和域名证书。当前只重新读取了脱敏进程元数据，没有重新导出所有 Vault 值，也未验证最新三服务 Token 与 Vault 的逐项相等；早期 Token case PASS 见历史证据，不能代替本版本复核。

### Stripe Sandbox / Live 配置合同（2026-10-21 补记）

Billing 的 Stripe 配置统一以 `kv/prod/billing-service` 为权威 Vault 路径，按 Stripe 环境区分 Key；**不得添加 V3/V4 等部署代际后缀**。Vault 保存密钥及相关配置值；文档、GitOps 和快照清单仅记录字段名、非敏感路由及核验状态，不记录 secret value。

| 配置项 | Sandbox / Test | Live | 说明 |
| --- | --- | --- | --- |
| Webhook URL | `SANDBOX_STRIPE_WEBHOOK_URL`；当前有效接收端点：`https://accounts.svc.plus/api/billing/stripe/webhook` | `PROD_STRIPE_WEBHOOK_URL`；现存记录仅到 `https://accounts-serverless-prod.svc.plus/api/billing/`，**完整路径待补** | Sandbox 的 Vault URL 字段记录为空，实际端点由 GitOps 配置；源任务记载验签正常。Live 路径不完整，不据此推断 webhook suffix。 |
| API secret key | `SANDBOX_STRIPE_SECRET_KEY`；仅记录预期格式 `sk_test_…` | `PROD_STRIPE_SECRET_KEY`；仅记录预期格式 `sk_live_…` | 不记录、展示或复制密钥值；`PROD_` 是既有 Live 命名，不按 V3/V4 分叉。 |
| Webhook signing secret | `SANDBOX_STRIPE_WEBHOOK_SECRET`；仅记录预期格式 `whsec_…` | `PROD_STRIPE_WEBHOOK_SECRET`；仅记录预期格式 `whsec_…` | 不记录或比较 secret 明文；运行时验签应与实际 Stripe endpoint 配对。 |

关联来源：Codex 任务 `01a15c72-9370-7372-928c-e4a2ec93886c`（修复订阅 Sandbox 结算）；既有 P0 问题与回归状态见[历史 V3→V4 P0 记录](20261021-prod-v3-v4-p0-regression-record.zh.md)。表中 Sandbox 验签状态是该来源任务的历史记录，不替代对当前 V4 运行配置的重新核验。

## 5. 数据与 schema 基线

采样边界：2026-10-21 **12:35:59 +08:00**（数据库 UTC 时间 04:35:59），只读事务采样。对象计数在同一 PostgreSQL 会话内读取。

| 对象 | 数量／版本 |
| --- | --- |
| schema | `2026102002`，dirty=false |
| `users` | 33 |
| `subscription_records` | 13 |
| `subscriptions` | 3；与 `subscription_records` 是不同统计对象 |
| `account_quota_states` | 33 |
| `traffic_minute_buckets` | 39,850；最新 bucket `2026-10-21 12:35:00 +08`，最新 created_at `12:35:59 +08` |
| `billing_ledger` | 39,850；最新 created_at `12:35:59 +08` |

`traffic_minute_buckets` 与 `billing_ledger` 在本次采样的行数一致，且最新时间接近采样时刻，说明数据写入有新鲜度；这不能单独证明每个节点均有非零字节增量，也不能替代逐用户金额/额度指纹或 V3→V4 一致性比较。本轮未执行 migratectl 数据同步，也没有产生新的完整数据指纹。

历史审核迁移：`2026101902 → 2026102001 → 2026102002`。对应 SQL SHA-256：

- `2001`：`6e1528c1ef6259270fba1a8fae7f86da25d8d695c63e3da24b597f62cd89096d`。
- `2002`：`5ae75bdf216f243523abf0c9e26bef37b45cb289a1b7f39993c8e71e6c13d0cc`。
- PostgreSQL 17 原生 schema artifact：`f45db2423f11d9dcc7f3cc58c72b52228a27d7b6ccfc717faf2bbb56fa0498b1`。
- migratectl 二进制：`00b276dba8008900e84a1fb1f5231789643a4ab0a84726793a4eb32b3b2433b1`，工具来源与 Accounts SHA 相同。

这些来自历史迁移回执，不是本轮重新执行迁移的结果；历史 migration/checksum 不改写。

## 6. 快照清单：完成状态必须分开

### V2 历史全量快照

沿用[历史白皮书](../prod-v2-v3-20261019/web-saas-prod-v2-cold-backup-disaster-recovery-whitepaper.zh.md)：2026-10-18 记录，schema `2026101703`、30 用户、12 条订阅、12,218 条账本，DB 隔离恢复及 Vault inspect 通过。这是历史边界，不是 V4 的当前计数；本轮未重验 V2。

### V3 在线快照与跨机恢复

V4 主机保留 `prod-v3-online-full-2026.10.20-r2/1792496457/restore-verify-receipt.json`，记录：33 用户、13 订阅、schema `2026101902`、dirty=false、isolated_restore_verified=true；archive SHA-256=`a8bb99b039f395efd982a3c5c57e5610b915961e4c238262be9b91f037cff6d0`。

另一个独立归档 `d09ad7a6ba1cfeb426196fe6c89789af2183b7440f6754e7857c7f36f410725d` 的边界为 2026-10-20 20:26:27 +08:00，在 V4 的 `isolated-restore-20261020/1792504001/` 回执中恢复并重启通过，33 用户、13 订阅、35,306 条账本、75 表。两个归档的 SHA 不同，禁止混作同一文件。

### V4 含业务数据的历史备份及隔离恢复

受保护证据目录：`/data/backups/web-saas/prod-v4/fresh-native-20261020-233500/`。

| 项目 | 回执事实 |
| --- | --- |
| 备份 | `account.after-sync.dump.enc` |
| 归档 SHA-256 | `c82e0bbfb4237770cded91986a9a8f230cfba6520cf607589c1438eac7e5a109` |
| 完成时间 | 2026-10-20 23:50:25 +08:00 |
| 隔离恢复库 | `fresh_after_verify_20261020233500`，现场仍保留 |
| 数据恢复结果 | `post-sync-restore.json`：passed，business_data_populated=true |
| 恢复前后业务行指纹 | `f257cd457dffdfc03285ee8d94934355ba3dbd3684ce8b671d5c6de3a22717e2` |
| 恢复 schema 指纹 | `8e6e55a1a5373d16f5cdcc5a9fb7cdc2e8ec82aa58544e280e88a95c418862d7` |
| 权限指纹 | `cc65f0ffdbabe78cb93a4c1f5964051a5e18ce4074c57160f32628b8f5fd4d58` |
| 业务验收边界 | 未取得本轮真实应用进程连接该恢复库的新证据 |

它是已验证的业务 DB 备份，不等同于最新完整环境快照，更不包含随后权限、凭据渲染和入口变更的完整恢复证明。

### 最新发现的 V4 全量快照候选

目录：`/data/backups/web-saas/prod-v4/full-snapshot-20261020/20261020T182308Z/`，即 2026-10-21 02:23:08 +08:00 的命名时间，早于 03:09 正式入口修复。

| 文件 | 本轮重新计算的 SHA-256 |
| --- | --- |
| `db/account.dump.enc` | `2b393a529b12562f1f9c9cced0f9205e6e827de36b93b0eeed067c0fb492f425` |
| `db/globals.sql.enc` | `ae8eba36b74c29284808c53d449ccf39b0af5a5c9d9eb2f5ccbb39e64a546bd8` |
| `runtime/configuration.tar.gz.enc` | `fe9f706fb32e7540d9d0d08d332a19087303fc575fa20fb4e0981a4a9f13a821` |
| `runtime/manifest.json` | `d8428269daf5fe660b2a6202debe210303b85aae19541b3e49729af04a411844` |

四个文件权限均为 0600。随附 `runtime/manifest.json` 记录该快照对应的 schema `2026102002`、33 用户、13 条订阅、35,306 条账本，并标记隔离恢复 `passed`；源与恢复后的行指纹均为 `156ecdcbdcaf93ca913e041b418857e8bcd18cdab56866e9bf86f856373bf229`。这证明该时间点的 DB 归档曾完成隔离恢复及行指纹比对，但该快照早于 2026-10-21 12:19 +08 的应用重部署，且本轮未重新执行恢复。目录未发现完整 `SHA256SUMS` 和 Vault 加密快照，因此不能宣称它是覆盖当前运行配置与密钥引用的最新完整环境快照。本轮未解密、恢复或补建快照。

后续应按模板补齐最新发布、在线一致性边界、配置/角色/DB 归档、加密校验清单、独立恢复、应用连接和主机外副本。共享 Vault 的独立实例恢复与 DB 恢复分开授权、分开留证，不覆盖共享 Vault。

## 7. 当前证据限制

本轮未读取或改变 V3 的写入端状态，无法据此确认当前全局单写入者；未完整验证登录/MFA、OAuth、Stripe Sandbox、所有 Agent/Vector 节点、实时配额扣减与退款状态机。具体收尾项见[回归清单](regression-and-closure-checklist-20261021.zh.md)。
