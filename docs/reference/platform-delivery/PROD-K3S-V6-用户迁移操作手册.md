# V5 → V6 用户迁移操作命令与认证契约

更新时间：2026-11-02。状态：命令及源码核对完成；未执行数据复制，未通过迁移验收。

源节点 `104.105.141.213`，源 namespace `web-saas-k3s-v5`；目标节点 `172.237.24.232`，目标 namespace `web-saas-prod`，PostgreSQL namespace `postgresql-prod`。方向固定 V5 → V6。用户操作不等于订阅、账单、配额和财务迁移，也不授权 DNS 或生产写者切换。

## 认证与执行材料

| 材料 | 要求及提供方式 |
|---|---|
| SSH | 已授权的节点管理 SSH；管理身份负责迁移执行，不作为日常应用身份 |
| 源数据库 | 优先 `readonly_release` 专用登录：NOINHERIT、无成员关系、无管理及业务写权限、无序列 USAGE/UPDATE；对范围内表完整 SELECT，RLS 必须满足工具的明确只读策略 |
| 目标数据库 | 独立迁移执行身份，对必要对象有读取、写入及锁权限；与应用运行身份区分，不能把管理员凭据长期注入业务 |
| DSN | 运行时注入 `SOURCE_MIGRATION_DSN`、`TARGET_MIGRATION_DSN`；不放入命令参数、Git、回执或日志 |
| 数据库网络 | 受控 VPN/隧道；远程源连接要求 TLS、无明文 fallback；环回隧道须独立核验另一端身份，不能把地址不同作为环境证明 |
| 固定工具 | 受审核的预编译 `migratectl` 及独立取得的 SHA-256；本地源码与部署二进制必须分别核对 |
| 数据保护 | 目标加密备份及实际隔离恢复回执、准确数据库身份、源快照边界、写者状态 |
| Vault | 只记录已有凭据引用。源迁移 DSN、目标迁移 DSN 的 Vault 路径及字段尚未核实，不虚构；不得复用文档中的示例作为真实凭据 |

`kv/prod/Accounts-service` 的 `DATABASE_URL` 是现有应用连接来源，不代表已具备源只读身份或独立迁移身份。不得输出该值。Vault token、数据库密码、密码散列、用户 UUID、邮箱均不得进入公开记录。

## 执行前核对

在受控执行主机上使用同一个固定二进制，两端连接通过环境变量注入。禁止 `set -x`。以下变量中的审核值必须先取得，不可填入猜测值：

```bash
set -euo pipefail
: "${MIGRATECTL_BIN:?固定二进制绝对路径}"
: "${MIGRATECTL_SHA256:?独立审核的二进制摘要}"
: "${SOURCE_MIGRATION_DSN:?运行时注入源只读连接}"
: "${TARGET_MIGRATION_DSN:?运行时注入目标迁移连接}"
: "${REVIEWED_ACCOUNTS_SCHEMA_SHA256:?审核的原生schema摘要}"
: "${REVIEWED_BILLING_SCHEMA_SHA256:?审核的Billing契约摘要}"
printf '%s  %s\n' "$MIGRATECTL_SHA256" "$MIGRATECTL_BIN" | sha256sum -c -
"$MIGRATECTL_BIN" native-schema
"$MIGRATECTL_BIN" compare-core-users --help
"$MIGRATECTL_BIN" copy-core-users --help
```

本次现场 V6 `native-schema` 报告版本 `2026102002`、74 张表，schema 摘要 `f45db2423f11d9dcc7f3cc58c72b52228a27d7b6ccfc717faf2bbb56fa0498b1`。这只证明二进制内置清单，不证明实际库结构一致。本地代码 Billing 常量为 `a7133f3ef2ea9013a055cfd1442a7488d2b837f289e0f5d9b61624d4fde9bc53`，尚不能作为部署二进制已核实值。

## 核心用户比较与复制

以下命令仅在目标写者已真实暂停、Flux/Helm 不会自动恢复写者、备份恢复验证通过、结构和版本守卫通过后运行。当前本地实现连只读比较也要求 `--writers-paused`；不能为通过检查而虚报暂停状态。目标暂停须由 GitOps/Flux 的受控执行方案交付，不能只 scale 后任由调谐恢复。

```bash
umask 077
: "${RUN_DIR:?受限运行目录}"
install -d -m 0700 "$RUN_DIR"
"$MIGRATECTL_BIN" compare-core-users \
  --source-dsn-env SOURCE_MIGRATION_DSN \
  --target-dsn-env TARGET_MIGRATION_DSN \
  --environment prod --writers-paused \
  --schema-sha256 "$REVIEWED_ACCOUNTS_SCHEMA_SHA256" \
  --billing-schema-sha256 "$REVIEWED_BILLING_SCHEMA_SHA256" \
  -o markdown > "$RUN_DIR/core-users-before.md"
```

比较发现差异会返回非零，同时输出脱敏汇总；此时停止并审核，不能把非零一律吞掉。`copy-core-users` 没有 dry-run 参数。审核差异及写入范围后，显式执行：

```bash
"$MIGRATECTL_BIN" copy-core-users \
  --source-dsn-env SOURCE_MIGRATION_DSN \
  --target-dsn-env TARGET_MIGRATION_DSN \
  --environment prod --writers-paused \
  --schema-sha256 "$REVIEWED_ACCOUNTS_SCHEMA_SHA256" \
  --billing-schema-sha256 "$REVIEWED_BILLING_SCHEMA_SHA256" \
  > "$RUN_DIR/core-users-copy.json"
# 然后重复上面的 compare-core-users，另存 core-users-after.md，必须成功退出。
```

按规范化 email 匹配；已有用户保留目标 UUID，但可能更新 email、密码散列、Proxy UUID。缺失用户复制其用户行。它不是只追加操作，也不复制 OAuth identities、会话、账单或订阅；复制前须审核触发器及关联影响。

## 基线与单用户补齐

后续按 [用户基线与切换后补齐](../../02-accounts/migratectl-generation-users.md) 执行：两端身份一致后 `capture-user-baseline`；有有效基线后 `check-late-users`；选择具体遗漏 UUID 后 `sync-user` 默认预览，真实 apply 绑定预览 SHA、双重 UUID 确认及源写者隔离。

代际参数用 `--source-generation prod-v5 --target-generation prod-v6`，与 Kubernetes clusterId `prod-k3s-v6` 分开。单用户关联订阅、配额、用量或财务记录会拒绝补齐。基线记录的是时间边界，V5 继续写入时不能声称最终切换已完成。

## 当前阻断与禁止绕过

本地 `internal/migrate/core_users.go` 要求目标为 PG17 的 `account` 库及干净 `schema_migrations`。`native_runtime.go` 的 `verifyCatalogCheckpoint` 仅接受 `FullBusinessVersion`（`2026100701`）或经审核历史支持的 `2026101901/2026101902`，与现场二进制内置 `2026102002` 不一致。必须先核对同一部署构件对应源码并修复/确认兼容范围，不能改写 migration version、伪造历史或取消守卫。

真实源只读凭据、目标迁移身份、实际库版本/结构、备份恢复、工具版本对应关系及写者隔离尚未验收。本文件是受条件约束的操作手册，不是已成功执行回执。

源码入口：Accounts `cmd/migratectl/full_business.go`、`internal/migrate/core_users.go`、`internal/migrate/native_runtime.go`、`internal/migrate/generation_users.go`。全量业务复制另行核对 `copy-full-business` 范围；不得以用户比较成功代替账单订阅一致性。
