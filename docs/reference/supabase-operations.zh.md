---
title: Supabase 操作参考：专用只读角色、RLS 与受控连接
description: 在不暴露项目标识和凭据的前提下，说明如何为审计、报表和受控数据操作准备 Supabase PostgreSQL 专用只读角色。
slug: supabase-operations
lang: zh
date: 2026-10-07
status: review-draft
tags:
  - supabase
  - postgresql
  - rls
  - least-privilege
  - data-migration
category: reference
---

# Supabase 操作参考：专用只读角色、RLS 与受控连接

本文是公开的操作参考，不包含任何真实项目 ID、DSN、密码、内网地址或 Vault 值。所有尖括号和方括号都是必须由管理员从目标项目 **Connect** 对话框或组织的安全凭据流程填入的占位符。本文只描述准备和核验方法；不授权本次执行创建角色、写入 Vault、复制业务数据或切换生产入口。

## 1. 什么时候使用只读数据库账号

“数据库只读”“只读用户”“只读事务”和“只读副本”是四个不同层次，不能互相替代：

| 层次 | 作用 | 适用场景 | 不能证明什么 |
| --- | --- | --- | --- |
| 专用只读角色 | 用 PostgreSQL 权限禁止 DML、序列变更和 RLS 绕过 | 最小权限分析/报表、审计、受控迁移源账号 | 不代表数据是一致快照 |
| `default_transaction_read_only=on` | 让该角色新事务默认只读，降低误操作概率 | 人工检查、脚本预检、长事务读取 | 不是权限边界；高权限角色仍可能改变设置 |
| `SET TRANSACTION READ ONLY` | 只约束当前事务 | repeatable-read 快照、复制一致性预检 | 不替代角色权限和连接身份核验 |
| Read replica | 把读取流量导向复制副本 | 规模化查询、降低主库读取压力 | 可能有延迟；不自动满足切主或数据晋级资格 |

典型使用场景是：

1. **最小权限分析和报表**：只读角色只收到被批准的 `public` 表的 `SELECT`。
2. **审计和排障**：用明确身份读取目录、权限、RLS 和业务摘要，不把管理员 DSN 交给工具。
3. **受控迁移源账号**：源库只读，目标库由另一条受控链路负责写入；源连接不执行 schema、seed 或业务写入。
4. **复制一致性预检**：在 repeatable-read、只读事务中取得一致性观察点，再由数据 owner 决定是否进入暂停 writer、最终追平和切换阶段。

Serverless 仍使用 primary 时，只限制迁移或审计账号，不应因为账号只读就停止整库写入。生产切换还必须单独确认完整 writer 清单、停写窗口、最终追平、一致性回执和回退点；point-in-time equality 本身不是切主资格。

## 2. SQL Editor 中的创建顺序

### 2.1 先查角色，禁止接管现有身份

在 Supabase Dashboard 的 SQL Editor 中先运行只读检查。SQL Editor 由 Dashboard 以管理员上下文执行；这一步只确认角色和成员关系，不会创建或修改对象。

```sql
SELECT
  rolname,
  rolcanlogin,
  rolsuper,
  rolcreatedb,
  rolcreaterole,
  rolreplication,
  rolbypassrls,
  rolinherit,
  rolconfig
FROM pg_roles
WHERE rolname = 'readonly_release';

SELECT
  member_role.rolname AS member_role,
  parent_role.rolname AS granted_role,
  member_of.inherit_option,
  member_of.set_option
FROM pg_auth_members AS member_of
JOIN pg_roles AS member_role ON member_role.oid = member_of.member
JOIN pg_roles AS parent_role ON parent_role.oid = member_of.roleid
WHERE member_role.rolname = 'readonly_release';
```

如果角色已经存在，先停止并由 owner 审核它的 owner、成员、继承、表/序列权限、默认权限和 RLS 状态。不要把既有角色改名、补权限或重置密码后当作本合同的角色；这会接管未知消费者。只有确认没有需要保留的现有身份、或得到明确变更批准后，才继续下一步。

### 2.2 创建具有明确负向属性的角色

确认角色不存在且取得批准后，在 SQL Editor 执行以下最小创建语句。语句故意不内嵌密码：

```sql
CREATE ROLE readonly_release LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOINHERIT NOBYPASSRLS;
```

随后仍在 SQL Editor 中执行数据库、schema 和会话默认值设置：

```sql
GRANT CONNECT ON DATABASE postgres TO readonly_release;
GRANT USAGE ON SCHEMA public TO readonly_release;
ALTER ROLE readonly_release SET default_transaction_read_only = on;
```

`default_transaction_read_only=on` 只是防误操作的默认值，不是权限边界。真正的边界来自角色属性、没有成员继承、没有 `BYPASSRLS`、没有 DML 权限、没有序列变更权限和显式的表白名单。

### 2.3 逐表授予 53 张业务表的 `SELECT`

生产全业务合同是 **目标 53 张表**；来源允许 **44～53 张表**，其中下面标为“来源可选”的 9 张表可能不存在。目标缺少任一必需表时应停止，不得用 `GRANT SELECT ON ALL TABLES` 或静默缩小范围掩盖差异。`auth`、`storage` 及其他 schema 不在本合同中。

下面是显式 allowlist。每个表名都是人工审阅的对象名，不要改成 `ALL TABLES`、通配符或未来默认权限：

```sql
GRANT SELECT ON TABLE public.account_billing_profiles TO readonly_release;
GRANT SELECT ON TABLE public.account_lifecycle_events TO readonly_release; -- 来源可选
GRANT SELECT ON TABLE public.account_policy_snapshots TO readonly_release;
GRANT SELECT ON TABLE public.account_quota_states TO readonly_release;
GRANT SELECT ON TABLE public.admin_settings TO readonly_release;
GRANT SELECT ON TABLE public.agents TO readonly_release;
GRANT SELECT ON TABLE public.audit_logs TO readonly_release;
GRANT SELECT ON TABLE public.billing_ledger TO readonly_release;
GRANT SELECT ON TABLE public.billing_plans TO readonly_release;
GRANT SELECT ON TABLE public.billing_source_sync_state TO readonly_release;
GRANT SELECT ON TABLE public.bridge_credentials TO readonly_release;
GRANT SELECT ON TABLE public.cloud_vendor_costs TO readonly_release; -- 来源可选
GRANT SELECT ON TABLE public.email_blacklist TO readonly_release;
GRANT SELECT ON TABLE public.finance_invoices TO readonly_release; -- 来源可选
GRANT SELECT ON TABLE public.finance_operation_events TO readonly_release; -- 来源可选
GRANT SELECT ON TABLE public.finance_operations TO readonly_release; -- 来源可选
GRANT SELECT ON TABLE public.finance_payments TO readonly_release; -- 来源可选
GRANT SELECT ON TABLE public.finance_refunds TO readonly_release; -- 来源可选
GRANT SELECT ON TABLE public.homepage_video_settings TO readonly_release;
GRANT SELECT ON TABLE public.identities TO readonly_release;
GRANT SELECT ON TABLE public.mfa_recovery_codes TO readonly_release; -- 来源可选
GRANT SELECT ON TABLE public.node_health_snapshots TO readonly_release;
GRANT SELECT ON TABLE public.nodes TO readonly_release;
GRANT SELECT ON TABLE public.oauth_exchange_codes TO readonly_release;
GRANT SELECT ON TABLE public.overlay_config_acks TO readonly_release;
GRANT SELECT ON TABLE public.overlay_device_credentials TO readonly_release;
GRANT SELECT ON TABLE public.overlay_devices TO readonly_release;
GRANT SELECT ON TABLE public.overlay_enrollment_sessions TO readonly_release;
GRANT SELECT ON TABLE public.overlay_invites TO readonly_release;
GRANT SELECT ON TABLE public.overlay_networks TO readonly_release;
GRANT SELECT ON TABLE public.overlay_nodes TO readonly_release;
GRANT SELECT ON TABLE public.overlay_registrations TO readonly_release;
GRANT SELECT ON TABLE public.overlay_signed_config_acks TO readonly_release;
GRANT SELECT ON TABLE public.password_recovery_challenges TO readonly_release; -- 来源可选
GRANT SELECT ON TABLE public.rbac_permissions TO readonly_release;
GRANT SELECT ON TABLE public.rbac_role_permissions TO readonly_release;
GRANT SELECT ON TABLE public.rbac_roles TO readonly_release;
GRANT SELECT ON TABLE public.sandbox_bindings TO readonly_release;
GRANT SELECT ON TABLE public.scheduler_decisions TO readonly_release;
GRANT SELECT ON TABLE public.sessions TO readonly_release;
GRANT SELECT ON TABLE public.stripe_webhook_events TO readonly_release;
GRANT SELECT ON TABLE public.subscriptions TO readonly_release;
GRANT SELECT ON TABLE public.task_namespaces TO readonly_release;
GRANT SELECT ON TABLE public.task_runs TO readonly_release;
GRANT SELECT ON TABLE public.task_session_events TO readonly_release;
GRANT SELECT ON TABLE public.task_sessions TO readonly_release;
GRANT SELECT ON TABLE public.tenant_domains TO readonly_release;
GRANT SELECT ON TABLE public.tenant_memberships TO readonly_release;
GRANT SELECT ON TABLE public.tenants TO readonly_release;
GRANT SELECT ON TABLE public.traffic_minute_buckets TO readonly_release;
GRANT SELECT ON TABLE public.traffic_stat_checkpoints TO readonly_release;
GRANT SELECT ON TABLE public.users TO readonly_release;
GRANT SELECT ON TABLE public.xworkmate_profiles TO readonly_release;
```

这 53 张表来自 Accounts native manifest 加 Billing 的 `cloud_vendor_costs`。`public.users`、`mfa_recovery_codes`、`sessions`、`bridge_credentials`、`overlay_device_credentials` 等仍可能含密码、MFA、会话、凭据或其他敏感业务资料；“只读”不等于“低敏感度”。复制这些表必须有独立的数据范围批准和安全执行窗口。

不要在本次固定合同中执行 `ALTER DEFAULT PRIVILEGES ... GRANT SELECT`。未来由真实 object creator 按需登记默认权限，并重新评审 scope；否则新表会绕过 53 表合同自动开放。

### 2.4 密码由管理员在 psql 交互设置

密码应由数据库管理员在受保护终端以交互方式设置，例如：

```bash
psql '<ADMIN_DSN_FROM_SECURE_CHANNEL>'
```

进入 `psql` 后执行元命令：

```text
\password readonly_release
```

密码由密码管理器生成并安全提交给批准的运行时凭据流程。`\password` 是 psql 元命令，不是 SQL；不能在 Dashboard SQL Editor 中运行，也不能把密码写入仓库、脚本、命令参数、CI 日志、工单或本文。若管理员不能使用交互 psql，应暂停并走组织批准的密钥轮换流程，不要把明文密码改写成 SQL 或环境文件。

## 3. RLS：保持开启并为批准表提供完整可见性

### 3.1 `row_security` 的 fail-closed 语义

普通 `readonly_release` 不能绕过 RLS。`row_security=off` 不是“读取全部行”的开关；对本应应用 RLS 的查询，它应报错而不是静默漏读。只有 superuser 或 `BYPASSRLS` 角色不受这个设置影响，因此本合同明确使用 `NOBYPASSRLS`。

连接后的预检应看到：

```sql
SHOW row_security;
SHOW default_transaction_read_only;
SELECT
  current_user,
  session_user,
  current_setting('role') AS role_setting,
  current_database(),
  current_setting('transaction_read_only') AS transaction_read_only;
```

期望 `row_security` 为 `on`，`current_user` 和 `session_user` 最终匹配 `readonly_release`，`transaction_read_only` 为 `on`。如果驱动、DSN 或 Supavisor role override 使实际角色不同，应拒绝这条连接；不要仅凭 DSN 中的用户名自证身份。

### 3.2 每张启用 RLS 的表使用明确的 SELECT policy

只对获准 allowlist 中、确实启用 RLS 的表创建或审核以下形状的 policy；`<APPROVED_TABLE>` 必须逐表替换，不能对全库生成：

```sql
CREATE POLICY release_initialization_readonly
ON public.<APPROVED_TABLE>
AS PERMISSIVE
FOR SELECT
TO readonly_release
USING (true);
```

合同要求：

- policy 名为 `release_initialization_readonly`，`AS PERMISSIVE`，`FOR SELECT`，角色精确为 `readonly_release`，`USING (true)`；
- 不写 `WITH CHECK`，因为这是 SELECT policy；
- 不存在适用于该角色的 restrictive `SELECT` 或 `ALL` policy，且不依赖 `PUBLIC` 或 `authenticated` 的偶然继承；
- 不关闭全库 RLS，不授予 `BYPASSRLS`，不把 owner 或管理员连接伪装成只读角色；
- 如果业务本身要求行级隔离，不应把本参考中的全行读取 policy 直接套用到业务 API 角色；它只适用于已批准的受控读取源。

推荐先检查再创建，避免重复或把不匹配的现有 policy 当作合同：

```sql
SELECT
  n.nspname AS schema_name,
  c.relname AS table_name,
  c.relrowsecurity,
  c.relforcerowsecurity,
  p.polname,
  p.polpermissive,
  p.polcmd,
  pg_get_expr(p.polqual, p.polrelid) AS using_expression,
  pg_get_expr(p.polwithcheck, p.polrelid) AS with_check_expression,
  p.polroles
FROM pg_class AS c
JOIN pg_namespace AS n ON n.oid = c.relnamespace
LEFT JOIN pg_policy AS p ON p.polrelid = c.oid
WHERE n.nspname = 'public'
  AND c.relname IN ('<APPROVED_TABLE_1>', '<APPROVED_TABLE_2>')
ORDER BY c.relname, p.polname;
```

### 3.3 权限和公开面审计

逐表 allowlist 之外还要审计 schema、PUBLIC、函数和 owner。单独 `REVOKE` 某个角色的权限，不能移除 `PUBLIC` 继承的权限；发现 PUBLIC 写权限、`public` schema 的 `CREATE`、不必要的 `SECURITY DEFINER` 函数或错误 owner 时，应由安全/数据库 owner 另行批准修复。

```sql
SELECT table_schema, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE grantee IN ('PUBLIC', 'readonly_release')
  AND table_schema = 'public'
ORDER BY grantee, table_name, privilege_type;

SELECT
  has_schema_privilege('public', 'public', 'USAGE') AS public_schema_usage,
  has_schema_privilege('public', 'public', 'CREATE') AS public_schema_create;

SELECT
  n.nspname AS schema_name,
  p.proname,
  p.prosecdef AS security_definer,
  pg_get_userbyid(p.proowner) AS owner
FROM pg_proc AS p
JOIN pg_namespace AS n ON n.oid = p.pronamespace
WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
  AND p.prosecdef
ORDER BY n.nspname, p.proname;
```

对于 `readonly_release`，还应确认没有 INSERT/UPDATE/DELETE/TRUNCATE、sequence `USAGE/UPDATE`、role membership、owner、`CREATEROLE`、`BYPASSRLS` 或隐式 `PUBLIC` 写路径。审计应保存脱敏的 role、对象、策略摘要和连接身份 hash，不保存结果集、DSN、密码或 Vault response。

## 4. 连接方式、TLS 与 Supavisor

### 4.1 从 Connect 对话框复制，不拼接主机

Supabase 的连接方式取决于运行位置。Direct 通常用于持久后端、迁移和 PostgreSQL 原生工具；Supavisor Session 通常用于 IPv4-only 网络或需要会话语义的第三方工具。主机的 cluster index 不能从 region 推导，必须从 Connect 对话框复制，并强制 TLS 证书校验。

Direct 连接的用户名是角色本身：

```text
postgresql://readonly_release:[ENCODED_PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres?sslmode=verify-full
```

Supavisor Session 连接的用户名是 `role.projectref` 形式，端口是 `5432`：

```text
postgresql://readonly_release.[PROJECT-REF]:[ENCODED_PASSWORD]@[POOLER-HOST-FROM-CONNECT]:5432/postgres?sslmode=verify-full
```

`[POOLER-HOST-FROM-CONNECT]` 形如 `aws-[N]-[REGION].pooler.supabase.com`，其中 `[N]` 是 pooler cluster index，不是可以猜测的区域编号。保留 `verify-full`（或组织批准的等价证书校验）；不要以 `sslmode=disable`、`allow` 或跳过 hostname 验证替代 TLS。

生产全业务 pipeline 有更窄的合同：它严格只接受 `aws-[N]-[REGION].pooler.supabase.com` 的 **Supavisor Session** URI、`readonly_release.[PROJECT-REF]` 用户名、`5432` 和 TLS。这个合同不表示 Direct URI 可以直接套入现有 pipeline；运行时应使用 pipeline 的明确输入校验。

### 4.2 连接预检

在不读取业务全量数据的情况下，连接预检至少核对：

```sql
SELECT
  current_database(),
  current_user,
  session_user,
  current_setting('role'),
  current_setting('transaction_read_only'),
  current_setting('row_security');

SELECT
  has_database_privilege(current_user, current_database(), 'CONNECT') AS can_connect,
  has_schema_privilege(current_user, 'public', 'USAGE') AS can_use_public;
```

另由客户端记录脱敏的 host、port、database、用户名形态、TLS verify 结果和项目绑定摘要。审计 `DSN` 与 `role override`：比较 `session_user`、`current_user`、`current_setting('role')`，拒绝被 `SET ROLE`、连接 `options` 或中间层参数改成其他角色的连接。连接成功不等于 53 表 scope、RLS、敏感字段和一致性合同通过。

## 5. 受控迁移与 Vault 字段边界

当前 PROD 全业务工具的公开非敏感合同可概括为：Accounts native 52 张表加 Billing 1 张表，共 53 张目标表；来源为 44～53 张，9 张来源可选；源角色是 `readonly_release`，TLS 必须开启，方向为 PROD Supabase → PROD Selfhost。目标写入、停 writer、最终追平和切换资格属于其他 owner/阶段。

Vault 只描述字段和逻辑路径，不在本文或 Git 中保存值：

| 层 | 合同 |
| --- | --- |
| 逻辑 KV 路径 | `kv/prod/database-upgrade` |
| KV v2 API 路径 | `kv/data/prod/database-upgrade` |
| 字段 | `PROD_SUPABASE_READONLY_DSN` |
| 运行时映射 | `PROD_SUPABASE_READONLY_DSN` → `NATIVE_SOURCE_DSN` |
| 提交方式 | 凭据由用户通过安全凭据流程提交，不进入仓库、日志、聊天、artifact 或命令参数 |

来源身份 hash 不包含密码，也不能由调用者自行生成后把 source 标成 ready。至少要先审核 canonical tuple：角色、project ref、session pooler host、端口、数据库、TLS 校验结果、方向和批准的来源环境；然后由受控流程生成并登记摘要。当前配置若 `ready=false` 或 identity 摘要为空，必须保持未批准。

不要把 `UAT bootstrap_full_business_credentials.py` 的硬编码 UAT 52 表、两跳传输或目标隧道语义直接用于 PROD 53 表来源。UAT 与 PROD 的来源身份、网络边界、表范围和批准阶段不同。

## 6. 53 表复制的停止条件

以下任何一项失败都应停止，而不是扩大权限或降级为管理员账号：

- 角色已存在但 owner、membership、继承或权限未知；
- `current_user`、`session_user`、`role` override、host/port/database 或 TLS 与批准摘要不符；
- `row_security` 不是 `on`，或启用 RLS 的表没有精确的 `release_initialization_readonly` policy；
- 存在 restrictive `SELECT/ALL` policy、缺少必需表、出现未登记 public relation，或来源超出 53 表合同；
- 任意 public 业务表存在 DML/序列变更权限，或 PUBLIC/schema/function owner 暴露出未审计写路径；
- source identity、schema/billing hash、完整 53 表 scope、canonical user tuple 或回执不是独立审核结果；
- 只证明了 point-in-time equality，却没有全 writer 清单、停写窗口、最终 catch-up、回退点和业务验收。

真正的复制还需由固定版本的 Accounts/Playbooks/Toolkit owner 产生脱敏回执：每表 row count/full-field digest、来源 snapshot/catalog hash、用户 email 与 PROD Proxy UUID 的 canonical tuple、`source_read_only=true`、target write 状态及独立 cutover gate。身份 hash 不含密码，来源用户匹配必须先通过 canonical tuple 审核，不能自证 `identity_sha` 或 `ready`。

## 7. 参考来源

- [Supabase：Postgres Roles](https://supabase.com/docs/guides/database/postgres/roles)
- [Supabase：Connect to your database](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [PostgreSQL：`row_security` 与 `default_transaction_read_only`](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-ROW-SECURITY)
- [Accounts：full business migration contract（固定 commit `7b3112e`）](https://github.com/ai-workspace-services/accounts/blob/7b3112eb09ec1e7fbb9d35f25029818d8500980f/internal/migrate/full_business.go)
- [Toolkit：PROD full-business config](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/14560c07dd6e57131ce5c34ac9996ee3c73ab86b/.github/config/prod-full-business.json)
- [Playbooks：full-business transfer owner（固定 commit `7e9b16f`）](https://github.com/ai-workspace-infra/playbooks/blob/7e9b16fa6c83a2dd8bafc22dca5870e06154253f/roles/web_saas_full_business_transfer/README.md)

相关源码只用于核对非敏感合同；本文不声称这些引用已授权执行任何生产数据库或 Vault 操作。
