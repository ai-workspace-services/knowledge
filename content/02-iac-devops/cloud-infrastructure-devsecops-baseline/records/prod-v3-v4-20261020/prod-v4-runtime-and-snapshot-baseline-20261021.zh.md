# PROD V4 运行基线与快照清单

核验日期：2026-10-21，Asia/Shanghai。与[升级复盘](v3-v4-upgrade-retrospective-20261021.zh.md)、[回归清单](regression-and-closure-checklist-20261021.zh.md)配套使用。本文是有时间边界的运维记录，不是第二套配置源。

## 1. 环境与实际部署

| 项目 | 现场结果 |
| --- | --- |
| 主机 | `web-saas-prod-v4`；GCP 控制面及 SSH hostname 一致 |
| 平台 | GCP，`open-platform-prod / asia-east1-a` |
| 运行路径 | SSH → Playbook → 固定 GitOps → Doco-CD；未使用 CI 部署 |
| 发布引用 | `refs/tags/v2026.10.21-r4`，不可移动或复用 |
| GitOps 实际 SHA | `cbdd876e088176e10128cc5f9f3153b82c0500e4`，由 Doco-CD 日志核实 |
| Doco-CD | target=`prod-v4`，interval=60 秒；03:16:50 完成一次成功任务 |
| 独立数据盘 | 50 GiB，ext4，挂载 `/data`；根盘约 20 GiB |
| PostgreSQL 挂载 | `/data/postgresql` → `/var/lib/postgresql/data`，读写 |
| 实际业务库 | `account`，PostgreSQL 17.10 |
| Caddy 主机配置 | `/etc/xcontrol/web-saas-recovery/Caddyfile`；路径含 recovery 不代表当前仍是候选模式 |
| Caddy 激活模式 | `generation=prod-v4`、`runtime_mode=primary`、target 与主机一致 |
| 入口配置 SHA-256 | `42f01244e16fa3fe3274fedfd52e443d4287dd2f7f1b437f7f431539c3348d83` |

GitOps 声明见 [compose/web-saas](https://github.com/ai-workspace-infra/gitops/tree/cbdd876e088176e10128cc5f9f3153b82c0500e4/compose/web-saas)。此前 `prod-v4-acceptance-2026.10.21-r1` 和分支演练 SHA 为历史候选，不能冒充上述运行版本。

## 2. 容器构件

以下为实际容器 `Config.Image` 与本机镜像 digest 交叉核实结果。六个服务容器运行；PostgreSQL 和 Doco-CD 带 healthy 状态。Content、Stunnel、OTel 未出现在本次运行容器清单，不能沿抄 V2 模板为“已运行”。

| 服务 | tag / source SHA | 完整 digest |
| --- | --- | --- |
| Accounts | `sha-6565297116c502c1b89557b201234f9d6e8f5e08` | `sha256:53bdb8037ddbd32516bff965e0853d4767e2f6eecde13284b7f39eb4dc91356e` |
| Billing | `sha-77557d796a66dcd3373d7731125890bd91ebc5d3` | `sha256:974a012cd032a291c495120f70dc1da1dbe35d05c7554b4912836cac983d438b` |
| Console | `sha-22e1485bad13995caa4012316c9cf0012e265059` | `sha256:a0b0935ca530b44b02d1e165ed16c9f71636f98abb3404675a287eef575a1810` |
| PostgreSQL | `sha-7759f4513e1710e86332795b611507bbed37ea39` | `sha256:f97857bd59c1fc55e3be3942b2c8f5554a8e9ee1d08bf3e834940c33189a141c` |
| Caddy | `959d6c8` | `sha256:9895385033fea2bdb445841b45f37e6cd58b9e071a16e4c147e483abb74a0acf` |
| Doco-CD | digest 固定，无需推断 tag | `sha256:46f3e44106fd0f4f30bc450682038509484d9aa28916edd6039b0af45bdc1cec` |

当前运行版本及已测试版本并非始终一致；应用 tag 不等同于 GitOps tag。回退构件先保留当前上述 digest 和此前固定声明，业务库的回退需独立评估。

## 3. 域名、SNI 与路由

| 域名 | 当前解析归属 | 本轮 HTTPS 结果 |
| --- | --- | --- |
| `console.svc.plus` | V4 | `/login` 200 |
| `accounts.svc.plus` | V4 | `/readyz` 200；API 服务 |
| `billing.svc.plus` | V4 | `/readyz` 200；API 服务 |
| `xworktech.com` | V3 | `/` 200 |
| `www.xworktech.com` | V3 | 301 到根域 |
| `console-selfhost-prod-v4.svc.plus` | V4 | 登录页此前已核验 200 |
| `accounts-selfhost-prod-v4.svc.plus` | V4 | API 版本别名 |
| `billing-selfhost-prod-v4.svc.plus` | V4 | API 版本别名 |
| `postgresql-selfhost-prod-v4.svc.plus` | V4 | 预留解析；本轮未做 DB 隧道/TLS 连接验收 |

使用 `curl --resolve` 对 V4 执行五个公共 SNI 检查，使用正常 CA 校验、不加 `-k`：Console 登录及两个 API readyz 返回 200，品牌根域 200，www 301。这证明 V4 的五域证书/路由可响应，不代表品牌 DNS 已切换。

**03:27 后续更新**：按用户明确授权，两条品牌 A 记录已从 V3 改为 V4，保留代理/TTL。两个权威 NS 及 1.1.1.1、8.8.8.8 均验证到 V4；根域 200，www 301 且保留 URI。上表保留初次盘点事实，当前解析以[变更回执](brand-dns-handoff-20261021.zh.md)为准。

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

## 5. 数据与 schema 基线

采样边界：2026-10-21 **03:17:27 +08:00**，一个 `REPEATABLE READ READ ONLY` 事务。

| 对象 | 数量／版本 |
| --- | --- |
| schema | `2026102002`，dirty=false |
| `users` | 33 |
| `subscription_records` | 13（另次只读核实） |
| `subscriptions` | 1；不是历史 13 条的同一统计对象 |
| `account_quota_states` | 33（另次只读核实） |
| `traffic_minute_buckets` | 35,369 |
| `billing_ledger` | 35,369 |

另次查询两表最新时间约为 03:17:53。计数与最新时间证明当时存在数据，不能替代逐用户金额/额度指纹、逐节点采集归属或 V3→V4 最新一致性比较。本轮未执行 migratectl 数据同步，也没有产生新的完整数据指纹。

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

四个文件权限均为 0600。本轮目录检查未发现该候选的完整 `SHA256SUMS`、隔离恢复完成回执或 Vault 加密快照；不能宣称“V4 最新全量快照及全部恢复验收通过”。名称里有 full-snapshot 不能代替完成状态。本轮未解密、恢复或补建快照。

后续应按模板补齐最新发布、在线一致性边界、配置/角色/DB 归档、加密校验清单、独立恢复、应用连接和主机外副本。共享 Vault 的独立实例恢复与 DB 恢复分开授权、分开留证，不覆盖共享 Vault。

## 7. 当前证据限制

本轮未读取或改变 V3 的写入端状态，无法据此确认当前全局单写入者；未完整验证登录/MFA、OAuth、Stripe Sandbox、所有 Agent/Vector 节点、实时配额扣减与退款状态机。具体收尾项见[回归清单](regression-and-closure-checklist-20261021.zh.md)。
