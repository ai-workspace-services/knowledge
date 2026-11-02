# V5 → V6 用户迁移操作手册

更新时间：2026-11-02。当前选定 [Accounts 独立迁移 API + migratectl transfer-api 方案](PROD-K3S-V6-Accounts迁移API单向同步规划.md)，Mac 仅访问 HTTPS 及专用 Vault token 引用。快照、预览无需停服务；事务写入仍需真实备份恢复证明、稳定目标基线和明确的冲突语义。

此前直连 DSN 的 compare/copy 命令属于旧路径，不再作为本轮首选执行入口。最新固定发布的 compare-core-users 不需要 writers-paused/Billing hash，不能混用旧二进制参数。本轮未进行数据库迁移。

## 已核实的应用连接来源

| 环境 | Vault CLI 路径 | 字段 | 当前消费者 |
|---|---|---|---|
| V5 | `kv/prod/services/web-saas-k3s-v5/database` | `database_url` | web-saas-k3s-v5/web-saas-secrets 的 DATABASE_URL，业务角色 app |
| V6 | `kv/prod/Accounts-service` | `DATABASE_URL` | web-saas-prod/accounts-db-runtime、billing-db-runtime，业务连接当前使用 postgres |

V5 SecretStore 指向集群内 Vault，V6 指向 https://vault.svc.plus；本机公共 Vault 会话本次也可读取上述两条记录。DSN 内是集群内数据库地址，Mac 不能直接解析连接；应用角色不能冒充专用迁移身份。API 模式下这些路径仅作来源盘点，不在Mac加载。迁移数据库、signing/staging key 和短期 token 分离，具体规划与简化命令见链接方案。

## 历史用户补齐工具

[用户基线与单用户补齐](../../02-accounts/migratectl-generation-users.md) 用于已对齐后的身份基线与遗漏检查，不负责订阅和账单。sync-user apply 的源写者隔离等约束仍按其真实实现执行；不能将其约束套到 transfer-api，也不能据 API 不含停写参数忽略最终单写者交接。
