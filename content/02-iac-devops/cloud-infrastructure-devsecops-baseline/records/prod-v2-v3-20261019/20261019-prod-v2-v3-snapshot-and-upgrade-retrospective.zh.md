# PROD V2 → V3 全量快照、恢复与升级复盘

日期：2026-10-19（北京时间）

执行路径：SSH → Playbooks → GitOps → Doco-CD；未 dispatch GitHub Actions 部署。
本文只保留脱敏运行事实，不包含 secret value、DSN、私钥、完整用户标识、备份内容或 Vault 解封材料。

## 1. 结论先行

**2026-10-20 后续 P0**：[Billing/Vector 采集阻断事件与升级时间线](20261020-billing-vector-ingest-p0.zh.md)。本白皮书的快照恢复结论仍针对快照边界；不代表后来实时流量持续入库。入口已修复并观测到真实账本增长，历史断档和全部节点覆盖继续分别验收。

V2 → V3 的核心恢复、数据库升级和应用验收已经有独立证据：V3 在源快照边界恢复了 33 个用户、13 条订阅记录和 32,847 条账本记录，schema 最终为 `2026101902 / dirty=false`，两段审核迁移的 SQL checksum 已记录，隔离恢复与应用健康验收通过。

本轮已新建 V3 可恢复逻辑全量快照：数据库、全局角色、运行配置与 TLS、加密容器配置、固定镜像引用及共享 Vault Raft 快照。数据库在独立 PostgreSQL 容器恢复成功，75 张表的源/恢复指纹一致。该集合不包含云磁盘镜像、非活跃旧库、Registry 镜像层或可重建缓存；镜像恢复仍依赖 Registry 与授权。Vault 与运行配置分别采集，不宣称整个系统在同一时刻原子冻结。

## 2. V2 全量快照（已完成）

### 2.1 环境基线

| 项目 | 事实 |
| --- | --- |
| 主机 | `web-saas-prod-v2` |
| GCP | `open-platform-prod / asia-east1-a` |
| GitOps release | `prod-v2-2026.10.18-r5` |
| GitOps commit | `060dadeca933700254d9153632345f0fc8b402d7` |
| Doco-CD | target `prod-v2`，轮询 60 秒 |
| 数据盘/数据库目录 | `/data` / `/data/postgresql` |
| 公共域名 | `console.svc.plus`、`accounts.svc.plus`、`billing.svc.plus` |
| 内部别名 | `console-selfhost-prod-v2.svc.plus`、`accounts-selfhost-prod-v2.svc.plus` |

### 2.2 快照证据

正式目录：

`/data/backups/web-saas/prod-v2/full-snapshot-20261018/20261017T173532Z/`

包含 `db/account.dump`、`db/globals.sql`、`db/checkpoint.txt`、`runtime/manifest.txt`、Vault 原生加密快照、KV 路径清单、inspect 输出和 `SHA256SUMS`。目录 `0700`，文件 `0600`。

已记录的非敏感证据：

- DB archive SHA-256：`84db2c11bf3d7de163ba5b43f332ce86e9d4e8ad56e9534a91546f1a53070e2d`
- Vault 加密快照 SHA-256：`8d65db42689f4eb92431cf0b5cfb32f9d3f26ebd64a0abd9c783ef3759f7a2ff`
- schema：`2026101703`
- 用户/订阅/快照账本：`30 / 12 / 12,218`
- PostgreSQL 17 隔离恢复：`PASS`
- Vault snapshot inspect 与解密回读：`PASS`

V2 未停机、未清理、未修改生产业务数据。Vault 只完成快照验证，没有在共享 PROD Vault 上覆盖式恢复。

## 3. V3 恢复与升级阶段证据

### 3.1 目标环境

| 项目 | 事实 |
| --- | --- |
| 主机 | `web-saas-prod-v3` |
| 数据盘 | 20 GB 系统盘 + 独立 50 GB `/data` |
| 私有别名 | `console-selfhost-prod-v3.svc.plus`、`accounts-selfhost-prod-v3.svc.plus`、`billing-selfhost-prod-v3.svc.plus`、`postgresql-selfhost-prod-v3.svc.plus` |
| 公共域名 | 后续曾切换到 V3；切换前完成证书/SNI/路由修复，失败时保留 V2 回退能力 |
| GitOps release | `prod-v3-billing-catalog-2026.10.19-r2` |
| GitOps commit | `cc72b7b4275530ec11c9bf1adfe0ffdca23b9f5a` |
| Doco-CD target | `prod-v3-stripe-sandbox` |

### 3.2 已完成的恢复、升级和验收

- V3 旧库先做独立备份并通过隔离恢复；旧库未直接被迁移覆盖。
- 从 V2 生成一致性快照并跨机恢复到 V3 候选库，使用相同快照边界核对用户、订阅、配额、分钟流量桶和财务记录。
- 执行两段审核迁移：

| 起始版本 | 目标版本 | SQL SHA-256 |
| --- | --- | --- |
| `2026101703` | `2026101901` | `b9fee298512e7d888fe619917c8238120f0e227f4ea348e59397d074c41f878d` |
| `2026101901` | `2026101902` | `53f9aaf7c56a14fd7c132c6649b79582cd2063f8903b94efb4e23cbf4895437c` |

- `migratectl` SHA-256：`5c74aa3c5bdb7268c1183ebbf1058b1ec33835ebec677e167055fe9ecdc6b4f0`。
- 源快照边界：2026-10-19 17:02:04（北京时间）。
- 用户/订阅/账本：`33 / 13 / 32,847`。
- 最终 schema：`2026101902 / dirty=false`。
- 受保护业务指纹集合 SHA-256：`377b8ada1f1b12d3b31078b5507c3d41b4a3de9049ac7008bad8a67a40aec357`。
- Accounts/Billing ready、Console 未登录跳转、固定镜像、Doco-CD tag/commit 对账：`PASS`。
- 原密码登录、终端代理连接、真实支付/退款：未由自动探针证明，必须单独验收。

## 4. 事故与修复复盘

### 4.1 数据和迁移保护

1. **旧 V3 存在脏数据**：没有直接清库或重建生产表，而是保留旧库，先做备份和隔离恢复，再将候选库切换为业务库。
2. **迁移版本与审计表边界容易混淆**：只排除固定内部迁移审计表，保留未知业务关系、列定义、权限和账务数据校验。
3. **账务/订阅差异不能靠覆盖解决**：使用快照边界、行级指纹和审核迁移；身份或财务冲突必须停止。
4. **数据库回退不能直接 down**：只允许兼容当前 schema 的应用 digest 回退，数据库问题优先隔离恢复和前向修复。

### 4.2 发布和凭据保护

1. **镜像 config digest 曾被误当 manifest digest**：后续固定 OCI manifest/index digest，并在主机拉取验证。
2. **共享服务令牌来源不一致**：恢复 Role 统一改为 Vault `kv/prod/accounts/runtime` 的 `INTERNAL_SERVICE_TOKEN`；Accounts、Billing、Console 使用同一运行时来源，Agent 继续按自身授权范围处理。
3. **证书/SNI 曾返回 TLS internal error**：问题定位为 V3 未正确从 `kv/CICD/domains/svc.plus` 恢复证书及只读挂载/站点路由；修复后先直连 V3 验证，再允许公共 DNS 切换。
4. **Doco-CD 不重复安装或重写凭据**：Playbook 只更新已安装控制器的 `POLL_CONFIG`，GitOps 负责不可变声明，SSH/Playbooks 负责主机执行。

### 4.3 Agent 注册与代际切换

1. `/panel/agent` 展示的是 Accounts 内存中的 Agent registry，不是单独的区域入口表；恢复数据库本身不会恢复实时心跳。
2. 用户观察到重启 `xconnect-edge-agent` 后才重新注册；连接复用或重试行为仍需代码与网络证据确认。节点自身的 `*-prod-v2` entrypoint 仍是节点身份，不应因控制面代际切换被批量改名。
3. 新代际切换必须分开验证：控制面健康、Agent status 心跳、区域 pool、用户配置同步和终端连接，不能用任一项替代全部验收。

## 5. 当前 V3 全量快照状态

实际快照目录：

```text
/data/backups/web-saas/prod-v3/full-snapshot-20261019/20261019T151628Z/
```

数据库快照时间为北京时间 **2026-10-19 23:16:28**。Vault 初次授权失败后，经用户认证恢复读取权限，已完成本轮备份。备份密钥引用 `kv/prod-v3/backups` → `web_saas_release_passphrase`；只在进程内存和受控 stdin 中传递。

- V3 业务服务继续运行，启动时间与重启计数保持不变；未修改业务行、V2 或 DNS。
- 完整 `account` dump 与源表指纹使用同一个导出的 REPEATABLE READ READ ONLY 快照，避免在线流量使备份与验收跨越不同边界。
- 隔离容器使用相同 PostgreSQL 镜像、`--network none`、tmpfs、无生产挂载及发布端口；恢复完成后核对全部 75 张表指纹及版本/计数，成功后清理本轮专属临时容器。
- 用户/订阅/账本为 **33 / 13 / 32,847**；schema **2026101902 / dirty=false**。
- 源与恢复行指纹：`e8b2334f32d28110b56b3d3a14b52070737ffc1ef117ba32ea05d269ca908be9`。序列值由 pg_dump 观察并恢复，不宣称其属于 MVCC 行指纹。
- Vault 新快照经加密、解密回读、字节 checksum 比对和原生 inspect；未执行独立 Vault 实例恢复。临时原生/解密校验文件已清理。
- 目录 `0700`，文件 `0600`，`SHA256SUMS` 全部校验通过。
- 主机外维护工作站副本已拉取并逐成员核对 checksum：`/Users/shenlan/.codex/backups/web-saas/prod-v3/prod-v3-full-snapshot-20261019T151628Z.tar`，文件 `0600`，外层 tar SHA-256 为 `52d158d17991986f8526b5ffbba8796f7387a3ed1a394f5706b9b08794b36a07`。外层 tar 未额外加密，数据库、globals、配置、容器 inspect 和 Vault 内容均已分别加密；明文成员只有脱敏元数据。此副本不等于已完成第三地点灾备。
- 备份后 Accounts/Billing V3 别名 `/readyz` 均 200，Console `/panel` 返回 307。
- 既有 `web_saas_cold_recovery` 的数据指纹与 dump 分开读取，会受持续写入影响。本轮采用限定 V3 的维护执行器完成导出与恢复；**通用 Role 的同快照能力尚待固化，不能宣称此次已由该 Role 完整自动执行**。

| 文件 | SHA-256 |
| --- | --- |
| `db/account.dump.enc` | `6609f47c61f24b66c3cf96934cb2e1004404c21213020b939320dd2b84b4e035` |
| `db/globals.sql.enc` | `efaade22c6688f4a5754fc9fc9ab41c9fa0d00e688a67b9848fd1b05aaa374a2` |
| `runtime/configuration.tar.gz.enc` | `887f9ca95e187e29c5c23daf4bb07b5ab8f5675063b139dae87362453c51b9b5` |
| `runtime/container-inspect.json.enc` | `48956cec39ac4ed1c6e0714a83ba9b66663cf0f851633d6d82b7168bb68babc8` |
| `vault/vault-raft.snapshot.enc` | `3f33d66bddc46db9a9f1870725f1f0e6f9233c306cb859e74ac9e35f4b7170c8` |

配置归档含 `/etc/xcontrol`（含 TLS）和 `/opt/doco-cd`；Docker inspect 的完整输出已加密。公开 manifest 仅包含镜像、挂载、状态和计数。角色 globals 已归档，未在临时实例恢复源口令或角色；本轮 DB 恢复使用 `--no-owner --no-acl`，跨机恢复还需按 Playbooks 恢复经审核的应用角色与 ACL。

### 5.1 当前应用构件

| 服务 | source/tag | digest |
| --- | --- | --- |
| Accounts | `fe7a146c4c2bdc94e9d4f80cb3800e245eee54a5` | `sha256:a8e1b425509e036bef38a3e80bbabb0219ddb0870ca39fb8a02bfaf067fdf2e8` |
| Billing | `22cbfc06d3fe030c2d32fa076335853fa6aa2865` | `sha256:462a7835f649ffad3bd88cb7e51e8e6ea4deb1f8fa6509f6a5ed5d9259058db4` |
| Console | `121569cda404c6a9a9bc6e1784f2f8c37f0c82b8` | `sha256:9fc0fb54fb680d553fbce23bff1ca1bebba60b070d039ff76ce43d3a035f15b4` |
| PostgreSQL | `sha-7759f4513e1710e86332795b611507bbed37ea39` | `sha256:f97857bd59c1fc55e3be3942b2c8f5554a8e9ee1d08bf3e834940c33189a141c` |
| Caddy | `959d6c8` | `sha256:9895385033fea2bdb445841b45f37e6cd58b9e071a16e4c147e483abb74a0acf` |
| Doco-CD | fixed digest | `sha256:46f3e44106fd0f4f30bc450682038509484d9aa28916edd6039b0af45bdc1cec` |

最新应用 release `prod-v3-vless-path-2026.10.19-r1`，GitOps `28044ec777e1ed012ad58aeb4577db0403719d4f`，target `prod-v3-stripe-sandbox`；本轮快照无 SQL 迁移。Accounts 前一 digest 可用于 schema 兼容性回退，但会重新引入旧 VLESS 路径缺陷，不能当作功能无损回退。

### 5.2 Vault 路径与键名

仅列出经本轮读取确认的键名，值不进入记录。更全的路径/键名元数据存于快照 `vault/vault-kv-paths-and-keys.json`；这里的有限清单不沿用历史 104 个路径的发现数量。

| path | keys |
| --- | --- |
| `kv/prod/accounts/runtime` | `INTERNAL_SERVICE_TOKEN`, `BRIDGE_CREDENTIAL_TOKEN_PEPPER` |
| `kv/prod/accounts/oauth/github` | `client_secret` |
| `kv/prod/accounts/oauth/google` | `client_id`, `client_secret`, `enabled`, `redirect_url` |
| `kv/prod/billing-service` | `PROD_STRIPE_SECRET_KEY`, `PROD_STRIPE_WEBHOOK_SECRET`, `PROD_STRIPE_WEBHOOK_URL`, `SANDBOX_STRIPE_SECRET_KEY`, `SANDBOX_STRIPE_WEBHOOK_SECRET` |
| `kv/prod/database-upgrade` | `PROD_SUPABASE_READONLY_DSN` |
| `kv/prod/platform/smtp/google` | `username`, `password` |
| `kv/CICD/domains/svc.plus` | `backed_up_at`, `caddy_data_tar_b64`, `domains`, `not_after_epoch`, `source_host`, `tls_ca_pem_b64`, `tls_cert_pem_b64`, `tls_fullchain_pem_b64`, `tls_key_pem_b64`, `tls_trust_bundle_pem_b64` |
| `kv/CICD/prod/gcp-bootstrap/xworktech` | `GCP_PROJECT_ID` |
| `kv/CICD/prod/iac_state` | `SSH_PRIVATE_DEPLOY_KEY_B64`, `SSH_PUBLIC_DEPLOY_KEY`, `TF_STATE_ACCESS_KEY`, `TF_STATE_BUCKET`, `TF_STATE_ENDPOINT`, `TF_STATE_REGION`, `TF_STATE_SECRET_KEY`, `VULTR_API_KEY` |
| `kv/prod-v3/backups` | `web_saas_release_passphrase` |

`kv/prod-v2/web-saas` 保留为历史引用，其 key 名列表已在快照元数据中记录；共享服务令牌的权威源为不含代际号的 `kv/prod/accounts/runtime`。恢复密钥必须另有可用的授权/托管途径，仅保存在同一个待恢复 Vault 内不能构成独立灾备闭环。

## 6. 后续可重复流程

使用模板文件：`web-saas-generation-snapshot-recovery-template.zh.md`。

固定顺序：

```text
源代际只读预检
  → 目标代际独立备份
  → 运行时 Vault 密钥门禁
  → 加密快照与唯一 receipt
  → 目标 /data stage
  → 隔离 PostgreSQL restore_verify
  → schema/数据/账务指纹验收
  → Playbooks 服务验收
  → GitOps/Doco-CD 对账
  → 明确授权后才切写入权/DNS
```

每一代均记录：`源/目标代际 + release tag + source SHA + image digest + SQL checksum + 迁移前后版本 + 备份/恢复结果 + 数据指纹 + 验收结果 + 回退 digest`。V3 作为 V4 来源时还需检查独立备份副本、密钥可用性、角色/ACL 恢复、公共 SNI、Agent 新鲜报告及单写入者门禁；本轮数据库隔离恢复通过不等于这些验收全部完成。

## 7. 关联记录

- [V2 冷备白皮书](web-saas-prod-v2-cold-backup-disaster-recovery-whitepaper.zh.md)：2026-10-18 历史截面；“V3 未创建”等措辞仅适用于当时。
- [V2→V3 恢复与迁移](v2-to-v3-snapshot-refresh-20261019.zh.md)。
- [共享令牌修复](20261019-prod-v3-canonical-service-token.zh.md)。
- [VLESS 路径 P0](20261019-prod-v3-vless-path-p0-release.zh.md)。
- [可复用证据模板](web-saas-generation-snapshot-recovery-template.zh.md)。
