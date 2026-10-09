---
title: CMDB 多云采集与数据库 Vault 路径规划
lang: zh
date: 2026-10-09
status: proposed-not-applied
category: reference
---

# CMDB 多云采集与数据库 Vault 路径规划

路径沿用平台白皮书的 `kv/<scope>/<project>/<category>/.../<record>`。逻辑项目使用 `svc.plus`；GCP project ID、AWS account ID 等放在 provider/account 层。这里声明字段与权限，不创建 Vault 记录、policy、role 或 bootstrap 脚本。

## 路径与字段

表中的路径是 KV v2 的逻辑路径；API 读取在 mount 后插入 `/data/`，例如 `kv/data/uat/svc.plus/services/observability/database/cmdb/reader`。metadata/list API 使用 `/metadata/`，仅管理员或确有需求的管理流程获得 list 权限。

| 用途 | 逻辑 KV 路径 | 字段合同 |
| --- | --- | --- |
| Shared GCP 项目只读联邦绑定 | `kv/shared/svc.plus/cloud/gcp/<project-id>/federation/cmdb-readonly` | `project_id`、`service_account_email`、`workload_identity_provider`、`audience`；优先动态身份，不保存 service-account 私钥或 access token |
| PROD GCP 资源只读绑定 | `kv/prod/svc.plus/cloud/gcp/open-platform-prod/federation/cmdb-readonly` | 同上；UAT 汇总器读取该范围需要单独精确授权，仅允许资源只读 |
| AWS 只读联邦绑定 | `kv/<scope>/svc.plus/cloud/aws/<12-digit-account-id>/federation/cmdb-readonly` | `account_id`、`role_arn`、`audience`；区域 allowlist 在 GitOps，临时 STS credentials 仅在内存 |
| Linode / Akamai API | `kv/<scope>/svc.plus/cloud/linode/<account-id>/api/cmdb-readonly` | `account_id`、`token`；仅实例读取所需 scopes，禁止复用基础设施写入 token |
| UCloud Global 轻量产品 API | `kv/<scope>/svc.plus/cloud/ucloud/<project-id>/api/cmdb-readonly` | `project_id`、`public_key`、`private_key`；先验证轻量产品只读 API，TW/PH 实际 region 代码在 GitOps |
| Cloudflare Workers/Pages | `kv/<scope>/svc.plus/cloud/cloudflare/<account-id>/api/cmdb-readonly` | `account_id`、`api_token`；限定对应 account、Workers/Pages 读取权限 |
| Supabase 管理 API | `kv/<scope>/svc.plus/cloud/supabase/<organization-id>/api/cmdb-readonly` | `organization_id`、`management_token`；按产品实际可用权限核实，禁止以数据库 `service_role` key 替代管理身份 |
| CMDB 迁移 | `kv/uat/svc.plus/services/observability/database/cmdb/migrator` | `host`、`port`、`database`、`username`、`password`、`sslmode`、`ca_ref` |
| CMDB 采集写入 | `kv/uat/svc.plus/services/observability/database/cmdb/writer` | 同上；`cmdb_writer` 仅指定表 SELECT/INSERT/UPDATE、必要 sequence 权限 |
| Grafana 只读查询 | `kv/uat/svc.plus/services/observability/database/cmdb/reader` | 同上；`cmdb_reader` 只读脱敏视图，无 writer/migrator 权限 |
| 审计读取 | `kv/uat/svc.plus/services/observability/database/cmdb/auditor` | 同上；限定历史与采集回执视图 |
| 备份读取 | `kv/uat/svc.plus/services/observability/database/cmdb/backup` | 同上；独立备份 principal 的授权待数据库 owner 评审，不复用 migrator |
| 探针认证写入 | `kv/<scope>/svc.plus/services/observability/integrations/remote-write/<binding>` | `metrics_username`、`metrics_password`、`logs_username`、`logs_password`；按当前实际 consumer 字段适配，endpoint 配置在 GitOps |
| 精确主机 SSH | `kv/<scope>/svc.plus/hosts/<provider-native-node-ref>/ssh/<user>` | 只在产品需要时存 `private_key`、`known_hosts`；GCP 优先 OS Login，无静态私钥 |

`<scope>`、账号、region、principal 必须先经 API 和声明核实；这些模板不能作为默认账号或有效凭据。两个 Shared 项目分别使用 `open-platform-shared` 和 `open-platform-shared-510113`，不能相互覆盖。跨环境的云资源读取身份与 UAT 数据库写入身份独立，读取 PROD 库存不会授予 PROD 主机、数据库或部署权限。

## 授权与运行时交付

CMDB collector 只读各个已确认 provider 的精确 `data` 路径及 writer 路径。Grafana 只读 reader 路径；迁移执行只读 migrator；备份任务只读 backup。rotation 管理身份才允许对应记录 create/update，常驻服务不能写入或吊销凭据。禁止 `kv/data/*`、整棵 `shared/*`、跨环境通配 read/list。

GitHub Actions 使用受约束 OIDC→Vault JWT role，绑定仓库、固定 workflow、ref 与实际 environment。Shared 主机采用独立 Vault workload identity/Agent；GCP metadata service account 当前查询 Compute API 返回 403，需要明确增加最小只读能力后才能启用定时采集。权限提案为 Compute 资源 list/get 与 Cloud Run service list/get；不得附带实例启停、部署、DNS 或 IAM 写权限。

运行时材料由 Vault Agent 写入专用受控文件或短期进程环境，文件 root-owned `0600`，不打印 token/DSN/密码，不使用 `env`/`set` 展示环境，不把秘密传到 CLI 参数或 Git。远程数据库使用 TLS 与 CA 验证；当前 UAT Docker 私网连接采用内部网络，尚未达到远程 TLS 发布条件。

## 迁移顺序与当前状态

先固定账号及 scope → 精确路径/字段与 policy 声明 → 管理员受控 provision/rotation → consumer 只读 check → UAT 验证 → 切换固定版本 consumer → 保留旧记录回退 → 单独评审清理。按用户要求，本次不补全 bootstrap 脚本，也不写入 Vault 或修改现有 policy。

已有 `kv/data/CICD/observability`、`kv/data/observability/cmdb-grafana` 均为 LEGACY consumer 引用；本规划不表示已完成路径迁移。Shared UAT 主机的数据库凭据当前仍是主机内生成的 root-owned `0600` 运行时文件；应在新 Vault consumer 验证后轮换和切换，不能复制密码到文档、PR 或聊天。

待补身份：AWS 账号/region，Linode account，UCloud 轻量产品 project/API/TW-PH region，Cloudflare account，Supabase organization/project。无身份的 provider 保持 pending，不标记成成功且零资源。

关联：[CMDB 落地规划](multi-cloud-cmdb-postgresql-grafana-plan.zh.md)、[多云平台白皮书](multi-cloud-platform-engineering-whitepaper.zh.md)。
