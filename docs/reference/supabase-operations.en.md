---
title: 'Supabase Operations Reference: Dedicated Read-only Role, RLS, and Controlled Connections'
description: A credential-free procedure for preparing a dedicated Supabase PostgreSQL read-only role for audit, reporting, and controlled data operations.
slug: supabase-operations
lang: en
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

# Supabase Operations Reference: Dedicated Read-only Role, RLS, and Controlled Connections

This public reference contains no real project ID, DSN, password, private address, or Vault value. Angle brackets and square brackets are placeholders that an administrator must fill from the target project's **Connect** dialog or an approved secure-credential process. This page describes preparation and verification only; it does not authorize creating a role, changing Vault, copying business data, or switching a production entry point.

## 1. When to use a read-only database account

“Read-only database”, “read-only user”, “read-only transaction”, and “read replica” are different controls:

| Layer | What it does | Suitable use | What it does not prove |
| --- | --- | --- | --- |
| Dedicated read-only role | Blocks DML, sequence mutation, and RLS bypass through PostgreSQL privileges | Least-privilege analysis/reporting, audit, controlled migration source | That the data is a consistent snapshot |
| `default_transaction_read_only=on` | Makes new transactions read-only by default for the role | Human inspection, script preflight, long reads | A privilege boundary; a higher-privileged role may change settings |
| `SET TRANSACTION READ ONLY` | Constrains only the current transaction | Repeatable-read snapshots and replication preflight | Role and connection identity or object privileges |
| Read replica | Sends reads to a replicated database | Scale reads and reduce primary pressure | That replication is current or that cutover is qualified |

Typical uses are:

1. **Least-privilege analysis and reporting**: grant `SELECT` only on the approved `public` tables.
2. **Audit and diagnostics**: inspect catalogs, privileges, RLS, and business summaries without handing an administrator DSN to a tool.
3. **Controlled migration source**: keep the source read-only while another controlled owner writes the target; never run schema, seed, or business writes on the source.
4. **Replication consistency preflight**: take a repeatable-read observation point, then let the data owner separately approve writer pause, final catch-up, and cutover.

When Serverless still uses the primary, restrict the migration or audit account; do not stop all database writers merely because that account is read-only. A production cutover separately requires the complete writer list, a freeze window, final catch-up, an equality receipt, and a rollback point. Point-in-time equality alone is not cutover qualification.

## 2. Creation order in the SQL Editor

### 2.1 Inspect the role before creating it

First run read-only inspection in the Supabase Dashboard SQL Editor. Dashboard queries run in an administrator context; these queries inspect role and membership state and do not create or modify objects.

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

If the role exists, stop and have the owner review its owner, memberships, inheritance, table/sequence privileges, default privileges, and RLS state. Do not rename, broaden, or reset an existing role and then treat it as this contract; that would take over unknown consumers. Continue only after confirming that no existing identity must be preserved or after receiving an explicit change approval.

### 2.2 Create the role with explicit negative attributes

After confirming that the role is absent and the change is approved, execute this minimum creation statement in the SQL Editor. It intentionally contains no password:

```sql
CREATE ROLE readonly_release LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOINHERIT NOBYPASSRLS;
```

Then set database, schema, and session defaults in the SQL Editor:

```sql
GRANT CONNECT ON DATABASE postgres TO readonly_release;
GRANT USAGE ON SCHEMA public TO readonly_release;
ALTER ROLE readonly_release SET default_transaction_read_only = on;
```

`default_transaction_read_only=on` is an accident-prevention default, not the privilege boundary. The actual boundary is the role attributes, no inherited memberships, no `BYPASSRLS`, no DML or sequence mutation privileges, and the explicit table allowlist.

### 2.3 Grant `SELECT` table by table

The production full-business contract has **53 target tables**. The source may contain **44–53 tables** because nine source tables are optional. A missing required target table must stop the operation; do not hide scope drift with `GRANT SELECT ON ALL TABLES` or by silently shrinking the catalog. `auth`, `storage`, and other schemas are outside this contract.

The following is the explicit allowlist. Each object name is reviewed; do not replace it with `ALL TABLES`, a wildcard, or future default privileges:

```sql
GRANT SELECT ON TABLE public.account_billing_profiles TO readonly_release;
GRANT SELECT ON TABLE public.account_lifecycle_events TO readonly_release; -- optional at source
GRANT SELECT ON TABLE public.account_policy_snapshots TO readonly_release;
GRANT SELECT ON TABLE public.account_quota_states TO readonly_release;
GRANT SELECT ON TABLE public.admin_settings TO readonly_release;
GRANT SELECT ON TABLE public.agents TO readonly_release;
GRANT SELECT ON TABLE public.audit_logs TO readonly_release;
GRANT SELECT ON TABLE public.billing_ledger TO readonly_release;
GRANT SELECT ON TABLE public.billing_plans TO readonly_release;
GRANT SELECT ON TABLE public.billing_source_sync_state TO readonly_release;
GRANT SELECT ON TABLE public.bridge_credentials TO readonly_release;
GRANT SELECT ON TABLE public.cloud_vendor_costs TO readonly_release; -- optional at source
GRANT SELECT ON TABLE public.email_blacklist TO readonly_release;
GRANT SELECT ON TABLE public.finance_invoices TO readonly_release; -- optional at source
GRANT SELECT ON TABLE public.finance_operation_events TO readonly_release; -- optional at source
GRANT SELECT ON TABLE public.finance_operations TO readonly_release; -- optional at source
GRANT SELECT ON TABLE public.finance_payments TO readonly_release; -- optional at source
GRANT SELECT ON TABLE public.finance_refunds TO readonly_release; -- optional at source
GRANT SELECT ON TABLE public.homepage_video_settings TO readonly_release;
GRANT SELECT ON TABLE public.identities TO readonly_release;
GRANT SELECT ON TABLE public.mfa_recovery_codes TO readonly_release; -- optional at source
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
GRANT SELECT ON TABLE public.password_recovery_challenges TO readonly_release; -- optional at source
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

These 53 tables are the Accounts native manifest plus Billing's `cloud_vendor_costs`. `public.users`, `mfa_recovery_codes`, `sessions`, `bridge_credentials`, and `overlay_device_credentials` may contain passwords, MFA material, sessions, credentials, or other sensitive business data. “Read-only” does not mean “low sensitivity”. Copying these tables requires an independent data-scope approval and a secure execution window.

Do not execute `ALTER DEFAULT PRIVILEGES ... GRANT SELECT` for this fixed contract. A real object creator may register a future default privilege only after a new scope review; otherwise future tables would bypass the 53-table contract.

### 2.4 Set the password interactively with administrator psql

The database administrator should set the password interactively from a protected terminal, for example:

```bash
psql '<ADMIN_DSN_FROM_SECURE_CHANNEL>'
```

Inside `psql`, use the meta-command:

```text
\password readonly_release
```

Generate the password with an approved password manager and deliver it through the secure runtime-credential process. `\password` is a psql meta-command, not SQL: it cannot run in the Dashboard SQL Editor. Do not write the password to the repository, scripts, command arguments, CI logs, tickets, or this document. If interactive psql is unavailable, stop and use the approved rotation procedure rather than converting the password into SQL or an environment file.

## 3. RLS: keep it enabled and prove complete visibility

### 3.1 `row_security` fails closed

An ordinary `readonly_release` role must not bypass RLS. `row_security=off` is not a “read every row” switch: queries that would apply a policy should error instead of silently returning an incomplete result. Superusers and `BYPASSRLS` roles are exceptions, which is why this contract uses `NOBYPASSRLS`.

The connection preflight should show:

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

Expect `row_security=on`, `current_user` and `session_user` to resolve to `readonly_release`, and `transaction_read_only=on`. If a driver, DSN, or Supavisor role override changes the effective role, reject the connection; the username text in a DSN is not proof of the server-side identity.

### 3.2 Use an explicit SELECT policy on each approved RLS table

Only create or audit the following policy shape on an approved allowlist table that actually has RLS enabled. Replace `<APPROVED_TABLE>` one table at a time; do not generate this across the database:

```sql
CREATE POLICY release_initialization_readonly
ON public.<APPROVED_TABLE>
AS PERMISSIVE
FOR SELECT
TO readonly_release
USING (true);
```

The contract requires:

- policy name `release_initialization_readonly`, `AS PERMISSIVE`, `FOR SELECT`, exact role `readonly_release`, and `USING (true)`;
- no `WITH CHECK`, because this is a SELECT policy;
- no applicable restrictive `SELECT` or `ALL` policy for this role, and no accidental reliance on `PUBLIC` or `authenticated` membership;
- no database-wide RLS disablement, no `BYPASSRLS`, and no use of an owner/admin connection as the read-only role;
- if the application requires row isolation, do not apply this full-visibility policy to its API role; this shape is only for an approved controlled-read source.

Inspect before creating anything, so an existing policy is not mistaken for this contract:

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

### 3.3 Audit public privileges and function boundaries

Audit the effective privileges of the real `readonly_release` role, then audit direct `PUBLIC` ACL entries and function metadata. `PUBLIC` is PostgreSQL's implicit pseudo-role: it is not a row in `pg_roles`, so it must never be passed as the user argument to `has_*_privilege`. `information_schema.role_table_grants` is a useful display view, but it is not a complete `PUBLIC` or effective-privilege audit because it does not replace the `has_*` checks below.

```sql
-- Run this precheck first. If it returns zero rows, stop: do not run
-- the effective-role queries until an administrator has reviewed the role.
SELECT oid, rolname, rolsuper, rolbypassrls, rolinherit
FROM pg_roles
WHERE rolname = 'readonly_release';

-- Effective database and schema privileges for the actual role. If the
-- role is absent, the CTE makes this return zero rows instead of failing.
WITH target_role AS (
  SELECT oid, rolname
  FROM pg_roles
  WHERE rolname = 'readonly_release'
)
SELECT
  r.rolname,
  current_database() AS database_name,
  has_database_privilege(r.rolname, current_database(), 'CONNECT') AS can_connect,
  has_database_privilege(r.rolname, current_database(), 'CREATE') AS can_create_database,
  has_schema_privilege(r.rolname, 'public', 'USAGE') AS can_use_public,
  has_schema_privilege(r.rolname, 'public', 'CREATE') AS can_create_in_public
FROM target_role AS r;

-- Effective table privileges include PUBLIC and role memberships. The
-- owner column is checked separately because ownership is not a grant.
WITH target_role AS (
  SELECT oid, rolname
  FROM pg_roles
  WHERE rolname = 'readonly_release'
)
SELECT
  c.oid::regclass AS relation,
  pg_get_userbyid(c.relowner) AS owner,
  c.relowner = r.oid AS is_owner,
  has_table_privilege(r.rolname, c.oid, 'SELECT') AS can_select,
  has_table_privilege(r.rolname, c.oid, 'INSERT') AS can_insert,
  has_table_privilege(r.rolname, c.oid, 'UPDATE') AS can_update,
  has_table_privilege(r.rolname, c.oid, 'DELETE') AS can_delete,
  has_table_privilege(r.rolname, c.oid, 'TRUNCATE') AS can_truncate,
  has_table_privilege(r.rolname, c.oid, 'REFERENCES') AS can_references,
  has_table_privilege(r.rolname, c.oid, 'TRIGGER') AS can_trigger
FROM target_role AS r
JOIN pg_class AS c ON c.relkind IN ('r', 'p')
JOIN pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
ORDER BY c.oid::regclass::text;

-- Effective sequence privileges must not provide a write path through
-- nextval/setval or sequence inspection.
WITH target_role AS (
  SELECT oid, rolname
  FROM pg_roles
  WHERE rolname = 'readonly_release'
)
SELECT
  c.oid::regclass AS sequence_name,
  pg_get_userbyid(c.relowner) AS owner,
  c.relowner = r.oid AS is_owner,
  has_sequence_privilege(r.rolname, c.oid, 'USAGE') AS can_use,
  has_sequence_privilege(r.rolname, c.oid, 'SELECT') AS can_select,
  has_sequence_privilege(r.rolname, c.oid, 'UPDATE') AS can_update
FROM target_role AS r
JOIN pg_class AS c ON c.relkind = 'S'
JOIN pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
ORDER BY c.oid::regclass::text;

-- Function metadata is intentionally read-only. Review every public
-- SECURITY DEFINER or otherwise sensitive/volatile function that the role
-- can execute; EXECUTE alone does not prove that the function is harmless.
WITH target_role AS (
  SELECT oid, rolname
  FROM pg_roles
  WHERE rolname = 'readonly_release'
)
SELECT
  n.nspname AS schema_name,
  p.oid::regprocedure AS function_identity,
  p.prosecdef AS security_definer,
  p.provolatile,
  pg_get_userbyid(p.proowner) AS owner,
  p.proowner = r.oid AS is_owner,
  has_function_privilege(r.rolname, p.oid, 'EXECUTE') AS can_execute
FROM target_role AS r
JOIN pg_proc AS p ON true
JOIN pg_namespace AS n ON n.oid = p.pronamespace
WHERE n.nspname = 'public'
ORDER BY n.nspname, function_identity::text;

-- Direct PUBLIC ACLs use grantee = 0, not a role name. The COALESCE
-- preserves PostgreSQL defaults when an object's ACL column is NULL.
WITH public_acl AS (
  SELECT 'database'::text AS object_type,
         d.datname AS object_identity,
         a.privilege_type,
         a.is_grantable
  FROM pg_database AS d
  CROSS JOIN LATERAL aclexplode(
    COALESCE(d.datacl, acldefault('d', d.datdba))
  ) AS a
  WHERE d.datname = current_database()
    AND a.grantee = 0

  UNION ALL

  SELECT 'schema'::text,
         n.nspname,
         a.privilege_type,
         a.is_grantable
  FROM pg_namespace AS n
  CROSS JOIN LATERAL aclexplode(
    COALESCE(n.nspacl, acldefault('n', n.nspowner))
  ) AS a
  WHERE n.nspname = 'public'
    AND a.grantee = 0

  UNION ALL

  SELECT CASE WHEN c.relkind = 'S' THEN 'sequence' ELSE 'table' END,
         c.oid::regclass::text,
         a.privilege_type,
         a.is_grantable
  FROM pg_class AS c
  JOIN pg_namespace AS n ON n.oid = c.relnamespace
  CROSS JOIN LATERAL aclexplode(
    COALESCE(
      c.relacl,
      acldefault(
        CASE WHEN c.relkind = 'S' THEN 'S'::"char" ELSE 'r'::"char" END,
        c.relowner
      )
    )
  ) AS a
  WHERE n.nspname = 'public'
    AND c.relkind IN ('r', 'p', 'S')
    AND a.grantee = 0

  UNION ALL

  SELECT 'function'::text,
         p.oid::regprocedure::text,
         a.privilege_type,
         a.is_grantable
  FROM pg_proc AS p
  JOIN pg_namespace AS n ON n.oid = p.pronamespace
  CROSS JOIN LATERAL aclexplode(
    COALESCE(p.proacl, acldefault('f', p.proowner))
  ) AS a
  WHERE n.nspname = 'public'
    AND a.grantee = 0
)
SELECT object_type, object_identity, privilege_type, is_grantable
FROM public_acl
ORDER BY object_type, object_identity, privilege_type;
```

If the role precheck returns no row, stop and report `role_not_found`; do not silently create or substitute another role. Any `is_owner=true`, unexpected effective table privilege, database `CREATE`, schema `CREATE`, sequence `USAGE/UPDATE`, sensitive function `can_execute=true`, or returned direct `PUBLIC` ACL requires review. These queries are metadata evidence only: effective privilege functions fold in `PUBLIC` and memberships, while the ACL query shows direct `PUBLIC` entries; neither proves complete isolation, safe function behavior, RLS correctness, or cutover readiness. Retain only redacted role, object, policy, and connection-identity summaries; never retain result sets, DSNs, passwords, or Vault responses.

## 4. Connection modes, TLS, and Supavisor

### 4.1 Copy from Connect; do not compose the host

Supabase's connection method depends on where the client runs. Direct connections are generally used by persistent backends, migrations, and native PostgreSQL tools. Supavisor Session is generally used by IPv4-only networks or clients that need session semantics. The pooler cluster index cannot be inferred from a region; copy the host from Connect and require certificate verification.

For a Direct connection, the username is the role itself:

```text
postgresql://readonly_release:[ENCODED_PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres?sslmode=verify-full
```

For Supavisor Session, the username is `role.projectref` and the port is `5432`:

```text
postgresql://readonly_release.[PROJECT-REF]:[ENCODED_PASSWORD]@[POOLER-HOST-FROM-CONNECT]:5432/postgres?sslmode=verify-full
```

`[POOLER-HOST-FROM-CONNECT]` has a shape such as `aws-[N]-[REGION].pooler.supabase.com`; `[N]` is a pooler cluster index and must not be guessed. Keep `verify-full` (or an organization-approved equivalent certificate/hostname check); do not replace it with `sslmode=disable`, `allow`, or skipped hostname verification.

The existing PROD full-business pipeline is narrower: it accepts only a **Supavisor Session** URI on `aws-[N]-[REGION].pooler.supabase.com`, the `readonly_release.[PROJECT-REF]` username, port `5432`, and TLS. This does not imply that a Direct URI can be substituted into that pipeline; the runtime must pass its explicit input contract.

### 4.2 Connection preflight

Without streaming the business dataset, preflight at least checks:

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

The client separately records redacted host, port, database, username shape, TLS verification, and project-binding summary. Audit the DSN and any role override by comparing `session_user`, `current_user`, and `current_setting('role')`; reject a connection changed by `SET ROLE`, connection `options`, or middleware parameters. A successful connection does not prove the 53-table scope, RLS, sensitive-field handling, or consistency contract.

## 5. Controlled migration and Vault field boundaries

The current PROD full-business contract can be summarized without exposing secrets: Accounts native 52 tables plus one Billing table, 53 target tables; 44–53 source tables with nine optional; source role `readonly_release`; TLS required; direction PROD Supabase → PROD Selfhost. Target writes, writer pause, final catch-up, and cutover qualification belong to other owners and stages.

Vault carries field and logical-path contracts, not values:

| Layer | Contract |
| --- | --- |
| Logical KV path | `kv/prod/database-upgrade` |
| KV v2 API path | `kv/data/prod/database-upgrade` |
| Field | `PROD_SUPABASE_READONLY_DSN` |
| Runtime mapping | `PROD_SUPABASE_READONLY_DSN` → `NATIVE_SOURCE_DSN` |
| Submission | The user supplies credentials through a secure process; they do not enter the repository, logs, chat, artifacts, or command arguments |

The source identity hash does not contain the password, and a caller cannot self-attest it and mark the source ready. First review the canonical tuple: role, project ref, session-pooler host, port, database, TLS verification, direction, and approved source environment. A controlled process then generates and records the redacted digest. If the configuration remains `ready=false` or its identity digest is empty, it remains unapproved.

Do not reuse `UAT bootstrap_full_business_credentials.py` for the PROD 53-table source. Its hard-coded UAT 52-table, two-hop transport, and target-tunnel semantics have different identity, network, scope, and approval boundaries.

## 6. Stop conditions for the 53-table transfer

Stop rather than expanding privileges or falling back to an administrator account when any of the following occurs:

- the role already exists but its owner, memberships, inheritance, or privileges are unknown;
- `current_user`, `session_user`, a role override, host/port/database, or TLS differs from the approved digest;
- `row_security` is not `on`, or an RLS-enabled table lacks the exact `release_initialization_readonly` policy;
- a restrictive `SELECT/ALL` policy applies, a required table is missing, an unreviewed public relation appears, or the source exceeds the 53-table contract;
- any public business table grants DML or sequence mutation, or PUBLIC/schema/function ownership exposes an unaudited write path;
- source identity, schema/billing hashes, full 53-table scope, canonical user tuple, or the receipt is not independently reviewed;
- only point-in-time equality is proven, without the complete writer list, freeze window, final catch-up, rollback point, and business acceptance.

The actual transfer must produce a redacted receipt from the fixed Accounts/Playbooks/Toolkit owners: per-table row counts and full-field digests, source snapshot/catalog hashes, canonical email and PROD Proxy UUID user tuples, `source_read_only=true`, target-write state, and an independent cutover gate. The identity hash excludes the password; source-user matching must pass canonical-tuple review and cannot self-prove `identity_sha` or `ready`.

## 7. Reference sources

- [Supabase: Postgres Roles](https://supabase.com/docs/guides/database/postgres/roles)
- [Supabase: Connect to your database](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [PostgreSQL: `row_security` and `default_transaction_read_only`](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-ROW-SECURITY)
- [Accounts: full business migration contract (commit `7b3112e`)](https://github.com/ai-workspace-services/accounts/blob/7b3112eb09ec1e7fbb9d35f25029818d8500980f/internal/migrate/full_business.go)
- [Toolkit: PROD full-business config](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/14560c07dd6e57131ce5c34ac9996ee3c73ab86b/.github/config/prod-full-business.json)
- [Playbooks: full-business transfer owner (commit `7e9b16f`)](https://github.com/ai-workspace-infra/playbooks/blob/7e9b16fa6c83a2dd8bafc22dca5870e06154253f/roles/web_saas_full_business_transfer/README.md)

The repository sources are cited only for their non-secret contracts. They do not authorize any production database or Vault operation.
