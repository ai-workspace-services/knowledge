---
title: Platform Ops Toolkit 运维体系参考文档汇编
description: 集中管理 platform-ops-toolkit 迁移至 knowledge 仓库的 183 份多云平台工程、编排交付、安全与数据运维参考文档。
slug: platform-ops-toolkit
lang: zh
tags:
  - docs
  - reference
  - platform-ops-toolkit
  - devops
  - iac
---

# Platform Ops Toolkit 运维体系参考文档汇编

本文档目录统一归档来自 [platform-ops-toolkit](https://github.com/ai-workspace-infra/platform-ops-toolkit) 的全部运维与工程参考文档（共 183 份）。按多云平台工程、安全规范、流水线交付与历史审计分为 10 大核心主题目录及 1 个静态资源目录。

## 目录导航

- [01. 架构规范与标准定义 (Architecture & Standards)](#01-architecture-and-standards)：平台核心服务单元划分、多环境发布交付工程规范、域名与资产规范及顶层架构模型。
- [02. 交付编排与发布流水线 (Delivery & Orchestration)](#02-delivery-and-orchestration)：Serverless 与 Selfhost 多环境编排矩阵、Daily Snapshot 自动化、GitOps 路由与发布清单契约。
- [03. 数据运维与数据库迁移 (Data Operations & Migration)](#03-data-operations-and-migration)：Supabase / PostgreSQL 数据快照与增量迁移、UAT 升级回执审计、Stripe 目录对齐及双语灾备方案。
- [04. 密钥安全与身份中枢 (Security, Vault & IAM)](#04-security-vault-and-iam)：HashiCorp Vault 密钥分层模型、多云 OIDC 身份互信 Bootstrap、访问控制策略 (HCL) 与应急解封。
- [05. 多云基础设施与 IaC 状态 (Cloud Infrastructure & IaC)](#05-cloud-infrastructure-and-iac)：多云账户契约、Terraform 状态存储与孤儿锁治理、Akamai / UCloud 节点编排与配置。
- [06. 零信任网络与 XConnect 组网 (Network & XConnect)](#06-network-and-xconnect)：XConnect 零信任网络边界、Overlay 组网原则、网关高可用传输及端到端可观测性。
- [07. Agent 调度与执行权归属 (Agent & Execution Ownership)](#07-agent-and-execution-ownership)：四仓职责边界（Toolkit / Playbooks / IaC / GitOps）、代码所有权扫描契约与交接凭证。
- [08. 运维实战、演练与案例 (Runbooks & Cases)](#08-runbooks-and-cases)：生产/UAT 故障排查、TLS 死锁修复、全链路演练手册及双语灾难恢复演练记录。
- [09. 规划方案与产品蓝图 (Plans & Blueprints)](#09-plans-and-blueprints)：AI Aggregator 聚合网关规划、控制台演进方案与多环境资源复用规划。
- [10. 历史研发任务审计归档 (Historical Tasks Archive)](#10-tasks-archive)：2026-07 至 2026-10 阶段性交付记录、排障日志、密钥修复底账与日常工作计划。
- [11. 视觉资产与监控拓扑 (Assets)](#assets)：Grafana 监控看板截图、Process Exporter 资源分布树状图、UAT 控制台界面与业务流程图。

---

## <a id="01-architecture-and-standards"></a>01. 架构规范与标准定义 (Architecture & Standards)

> 平台核心服务单元划分、多环境发布交付工程规范、域名与资产规范及顶层架构模型。

| 文件 | 标题 / 说明 | 格式 / 大小 |
| :--- | :--- | :--- |
| [README.md](01-architecture-and-standards/README.md) | Site Migration Toolkit: 基于 AI 驱动的站点级自动化迁移容灾解决方案 | `MD` (8 KB) |
| [akamai-cloud/README.md](01-architecture-and-standards/akamai-cloud/README.md) | Akamai Cloud/Linode Vault KV | `MD` (3 KB) |
| [dev-tools-setup.md](01-architecture-and-standards/dev-tools-setup.md) | Development Tools Setup | `MD` (4 KB) |
| [domains/README.md](01-architecture-and-standards/domains/README.md) | Domain delivery model | `MD` (1 KB) |
| [domains/action-runner/README.md](01-architecture-and-standards/domains/action-runner/README.md) | Action Runner 部署前置条件 | `MD` (3 KB) |
| [domains/agent-proxy/README.md](01-architecture-and-standards/domains/agent-proxy/README.md) | 加速代理与网关域 (Domain: agent-proxy) | `MD` (1 KB) |
| [domains/ai-workspace/README.md](01-architecture-and-standards/domains/ai-workspace/README.md) | AI Workspace 核心业务域 (Domain: ai-workspace) | `MD` (2 KB) |
| [domains/open-platform/README.md](01-architecture-and-standards/domains/open-platform/README.md) | 开放平台与基础设施域 (Domain: open-platform) | `MD` (3 KB) |
| [domains/web-saas/README.md](01-architecture-and-standards/domains/web-saas/README.md) | Web SaaS 服务与入口域 (Domain: web-saas) | `MD` (14 KB) |
| [multi-environment-delivery-and-release-standard.md](01-architecture-and-standards/multi-environment-delivery-and-release-standard.md) | 多云多环境交付与发布规范 | `MD` (12 KB) |
| [open-platform-observability-migration.md](01-architecture-and-standards/open-platform-observability-migration.md) | Open Platform Observability migration plan | `MD` (11 KB) |
| [open-platform-service-units.md](01-architecture-and-standards/open-platform-service-units.md) | Open Platform service units | `MD` (3 KB) |
| [public-website-review-and-homepage-standard.md](01-architecture-and-standards/public-website-review-and-homepage-standard.md) | 公开主页与应用商店审核规范 | `MD` (9 KB) |
| [resource-aggregation-model.md](01-architecture-and-standards/resource-aggregation-model.md) | UAT / PROD resource aggregation contract | `MD` (3 KB) |

## <a id="02-delivery-and-orchestration"></a>02. 交付编排与发布流水线 (Delivery & Orchestration)

> Serverless 与 Selfhost 多环境编排矩阵、Daily Snapshot 自动化、GitOps 路由与发布清单契约。

| 文件 | 标题 / 说明 | 格式 / 大小 |
| :--- | :--- | :--- |
| [DELIVERY-MANIFEST.md](02-delivery-and-orchestration/DELIVERY-MANIFEST.md) | 领域交付清单 (Domain Delivery Manifest) | `MD` (4 KB) |
| [IMAGE-TAG-CONTRACT.md](02-delivery-and-orchestration/IMAGE-TAG-CONTRACT.md) | 镜像 Tag 跨仓契约 (Image Tag Contract) | `MD` (4 KB) |
| [control-plane-owner-cleanup.md](02-delivery-and-orchestration/control-plane-owner-cleanup.md) | YAML/Shell 控制面清理审核状态 | `MD` (6 KB) |
| [daily-snapshot-manual.md](02-delivery-and-orchestration/daily-snapshot-manual.md) | Daily Snapshot 手动执行版 | `MD` (8 KB) |
| [gitops-serverless-routing.md](02-delivery-and-orchestration/gitops-serverless-routing.md) | GitOps serverless routing backend | `MD` (2 KB) |
| [iac-self-check-matrix.md](02-delivery-and-orchestration/iac-self-check-matrix.md) | IAC 自检矩阵 | `MD` (2 KB) |
| [iam-integration-testing.md](02-delivery-and-orchestration/iam-integration-testing.md) | iam.svc.plus 自动测试与手动验收 | `MD` (11 KB) |
| [observability-mcp-tldr.md](02-delivery-and-orchestration/observability-mcp-tldr.md) | Observability MCP TL;DR | `MD` (3 KB) |
| [owner-followup-20261007.zh.md](02-delivery-and-orchestration/owner-followup-20261007.zh.md) | Toolkit 脚本清理与 owner 交接记录 | `MD` (6 KB) |
| [prod-selfhost-acceptance.md](02-delivery-and-orchestration/prod-selfhost-acceptance.md) | PROD Selfhost acceptance | `MD` (2 KB) |
| [prod-selfhost-mainline-status.md](02-delivery-and-orchestration/prod-selfhost-mainline-status.md) | PROD Selfhost 主线交付状态（2026-10-07） | `MD` (29 KB) |
| [serverless-orchestrator-matrix.md](02-delivery-and-orchestration/serverless-orchestrator-matrix.md) | Serverless Orchestrator 矩阵部署 | `MD` (17 KB) |
| [uat-akamai-selfhost-profile.md](02-delivery-and-orchestration/uat-akamai-selfhost-profile.md) | UAT Akamai Cloud Selfhost Profile | `MD` (3 KB) |
| [uat-dynamic-region-delivery.md](02-delivery-and-orchestration/uat-dynamic-region-delivery.md) | UAT dynamic regional-entry delivery | `MD` (2 KB) |
| [unified-iac-state-validation.md](02-delivery-and-orchestration/unified-iac-state-validation.md) | 统一多云 IaC State 验证用例 | `MD` (6 KB) |
| [web-saas/remodeling.md](02-delivery-and-orchestration/web-saas/remodeling.md) | Unify Web SaaS Deployment into Docker Compose and Helm Chart | `MD` (2 KB) |

## <a id="03-data-operations-and-migration"></a>03. 数据运维与数据库迁移 (Data Operations & Migration)

> Supabase / PostgreSQL 数据快照与增量迁移、UAT 升级回执审计、Stripe 目录对齐及双语灾备方案。

| 文件 | 标题 / 说明 | 格式 / 大小 |
| :--- | :--- | :--- |
| [EN/BackUP/postgresql_disaster_recovery.md](03-data-operations-and-migration/EN/BackUP/postgresql_disaster_recovery.md) | Unified Database Backup & DR Plan (PostgreSQL) | `MD` (4 KB) |
| [ZH/BackUP/postgresql_disaster_recovery.md](03-data-operations-and-migration/ZH/BackUP/postgresql_disaster_recovery.md) | 统一数据库备份与灾备方案 (PostgreSQL) | `MD` (5 KB) |
| [accounts-bridge-credential-pepper-tldr.zh-CN.md](03-data-operations-and-migration/accounts-bridge-credential-pepper-tldr.zh-CN.md) | Accounts Bridge Credential Pepper：TL;DR | `MD` (3 KB) |
| [accounts_prod_to_uat_migration_guide.md](03-data-operations-and-migration/accounts_prod_to_uat_migration_guide.md) | PROD 至 UAT Accounts 账号数据单向增量迁移方案与操作指南 | `MD` (13 KB) |
| [akamai-cloud/uat-six-namespace-migration-plan.md](03-data-operations-and-migration/akamai-cloud/uat-six-namespace-migration-plan.md) | Akamai Cloud UAT six-namespace migration plan | `MD` (14 KB) |
| [core_delivery_overview_and_observability_guide.md](03-data-operations-and-migration/core_delivery_overview_and_observability_guide.md) | 核心落地成果概览与可观测性集成指南 | `MD` (32 KB) |
| [environment-data-operations.md](03-data-operations-and-migration/environment-data-operations.md) | 环境数据操作：统一控制面与执行归属 | `MD` (11 KB) |
| [environment-upgrade.md](03-data-operations-and-migration/environment-upgrade.md) | 独立 UAT / PROD 升级流水线 | `MD` (12 KB) |
| [gitops_data_migration_and_pipeline_trigger_plan.md](03-data-operations-and-migration/gitops_data_migration_and_pipeline_trigger_plan.md) | GitOps 数据迁移拓扑与流水线触发机制优化方案 (Implementation Plan) | `MD` (6 KB) |
| [howto/akamai-uat-migration-preflight.md](03-data-operations-and-migration/howto/akamai-uat-migration-preflight.md) | Akamai UAT migration preflight | `MD` (7 KB) |
| [howto/stripe-billing-catalog-tldr.md](03-data-operations-and-migration/howto/stripe-billing-catalog-tldr.md) | Stripe 套餐目录初始化 TL;DR | `MD` (3 KB) |
| [howto/supabase-postgres-observability.md](03-data-operations-and-migration/howto/supabase-postgres-observability.md) | Supabase PostgreSQL → Observability | `MD` (3 KB) |
| [howto/uat-split-selfhost-migration.md](03-data-operations-and-migration/howto/uat-split-selfhost-migration.md) | UAT split Selfhost deployment and migration runbook | `MD` (6 KB) |
| [release_tag_database_checkpoint_and_upgrade_plan.md](03-data-operations-and-migration/release_tag_database_checkpoint_and_upgrade_plan.md) | 架构规划：基于 Release Tag 的数据库原子化升级与备份回滚体系 (Supabase & VPS PostgreSQL) | `MD` (9 KB) |
| [supabase_cloud_one_way_migration.md](03-data-operations-and-migration/supabase_cloud_one_way_migration.md) | VPS 数据迁移模式 | `MD` (6 KB) |
| [uat-schema-repair-2026-10-04.md](03-data-operations-and-migration/uat-schema-repair-2026-10-04.md) | UAT Accounts schema repair — 2026-10-04 | `MD` (5 KB) |
| [uat-upgrade-promotion-evidence-2026-10-04.md](03-data-operations-and-migration/uat-upgrade-promotion-evidence-2026-10-04.md) | UAT 旧版升级验收与 PROD 晋级证据 | `MD` (9 KB) |

## <a id="04-security-vault-and-iam"></a>04. 密钥安全与身份中枢 (Security, Vault & IAM)

> HashiCorp Vault 密钥分层模型、多云 OIDC 身份互信 Bootstrap、访问控制策略 (HCL) 与应急解封。

| 文件 | 标题 / 说明 | 格式 / 大小 |
| :--- | :--- | :--- |
| [2026-09-27-gcp-vault-migration-implementation-record-zh.md](04-security-vault-and-iam/2026-09-27-gcp-vault-migration-implementation-record-zh.md) | GCP Vault 迁移与资源对账实施记录 | `MD` (6 KB) |
| [ZH/BackUP/vault_disaster_recovery.md](04-security-vault-and-iam/ZH/BackUP/vault_disaster_recovery.md) | Vault 统一数据备份与灾备方案 | `MD` (6 KB) |
| [ZH/BackUP/vault_oidc_policy_troubleshooting.md](04-security-vault-and-iam/ZH/BackUP/vault_oidc_policy_troubleshooting.md) | Vault OIDC 策略配置与 403 Forbidden 权限排障指南 | `MD` (5 KB) |
| [ZH/Systems-Overview/PROD/oidc_cloud_integration.md](04-security-vault-and-iam/ZH/Systems-Overview/PROD/oidc_cloud_integration.md) | 多云架构 CI/CD OIDC 免密认证指南 | `MD` (6 KB) |
| [ai-aggregator-v1-caddy-policy.hcl](04-security-vault-and-iam/ai-aggregator-v1-caddy-policy.hcl) | ai-aggregator-v1-caddy-policy.hcl | `HCL` (1 KB) |
| [ai-aggregator-v1-litellm-policy.hcl](04-security-vault-and-iam/ai-aggregator-v1-litellm-policy.hcl) | ai-aggregator-v1-litellm-policy.hcl | `HCL` (1 KB) |
| [ai-aggregator-v1-minimal-kv.md](04-security-vault-and-iam/ai-aggregator-v1-minimal-kv.md) | AI Aggregator v1 minimal Vault KV contract | `MD` (2 KB) |
| [ai-aggregator-v1-new-api-policy.hcl](04-security-vault-and-iam/ai-aggregator-v1-new-api-policy.hcl) | ai-aggregator-v1-new-api-policy.hcl | `HCL` (1 KB) |
| [ai-aggregator-v1-policy.hcl](04-security-vault-and-iam/ai-aggregator-v1-policy.hcl) | ai-aggregator-v1-policy.hcl | `HCL` (1 KB) |
| [akamai-cloud/bootstrap-vault-kv-tldr.md](04-security-vault-and-iam/akamai-cloud/bootstrap-vault-kv-tldr.md) | Akamai Cloud/Linode Vault KV 初始化 TL;DR | `MD` (3 KB) |
| [akamai-cloud/init-vault-kv.sh](04-security-vault-and-iam/akamai-cloud/init-vault-kv.sh) | init-vault-kv.sh | `SH` (5 KB) |
| [architecture/node-deployment-oidc.md](04-security-vault-and-iam/architecture/node-deployment-oidc.md) | Provider-neutral OIDC and node deployment | `MD` (9 KB) |
| [data_migration/uat-readiness-vault-audit-2026-10-04.md](04-security-vault-and-iam/data_migration/uat-readiness-vault-audit-2026-10-04.md) | UAT 旧版升级与 Vault 清理：真实增量证据 | `MD` (8 KB) |
| [howto/GCP-OIDC-Bootstrap-howto.md](04-security-vault-and-iam/howto/GCP-OIDC-Bootstrap-howto.md) | GCP OIDC Bootstrap 操作指南 | `MD` (21 KB) |
| [howto/GCP-OIDC-Bootstrap-test-cases.md](04-security-vault-and-iam/howto/GCP-OIDC-Bootstrap-test-cases.md) | GCP OIDC Bootstrap 验证用例 | `MD` (11 KB) |
| [howto/Vault-Server-Migration.md](04-security-vault-and-iam/howto/Vault-Server-Migration.md) | Migrate vault.svc.plus to a new Raft cluster | `MD` (6 KB) |
| [howto/Vault-Shared-GCP-OIDC-Setup.md](04-security-vault-and-iam/howto/Vault-Shared-GCP-OIDC-Setup.md) | Shared Vault GCP OIDC prerequisites | `MD` (16 KB) |
| [howto/XConnect-Vault-Migration-Deployment-Scale-Rollback.zh-CN.md](04-security-vault-and-iam/howto/XConnect-Vault-Migration-Deployment-Scale-Rollback.zh-CN.md) | XConnect + Vault 迁移、部署、扩缩容与回滚运行手册 | `MD` (20 KB) |
| [howto/aws-github-oidc-bootstrap-tldr.md](04-security-vault-and-iam/howto/aws-github-oidc-bootstrap-tldr.md) | AWS GitHub OIDC 首次 Bootstrap TL;DR | `MD` (8 KB) |
| [howto/gcp-oidc-bootstrap-vault-kv.md](04-security-vault-and-iam/howto/gcp-oidc-bootstrap-vault-kv.md) | GCP Terraform bootstrap 的 Vault KV 规划 | `MD` (5 KB) |
| [howto/supabase-account-vault-init-tldr.md](04-security-vault-and-iam/howto/supabase-account-vault-init-tldr.md) | Supabase 调试环境 Vault 初始化 TL;DR | `MD` (3 KB) |
| [howto/supabase-account-vault-init.md](04-security-vault-and-iam/howto/supabase-account-vault-init.md) | Supabase Account DB 初始化 | `MD` (3 KB) |
| [howto/ucloud-vault-kv.md](04-security-vault-and-iam/howto/ucloud-vault-kv.md) | UCloud provider credentials in Vault | `MD` (2 KB) |
| [howto/vault-migrate-cicd-details-tldr.md](04-security-vault-and-iam/howto/vault-migrate-cicd-details-tldr.md) | Vault CICD 凭据迁移 TL;DR | `MD` (3 KB) |
| [howto/zitadel-server.md](04-security-vault-and-iam/howto/zitadel-server.md) | 独立 Shared ZITADEL 部署 | `MD` (5 KB) |
| [kv_layout_and_migration.md](04-security-vault-and-iam/kv_layout_and_migration.md) | Vault KV 布局梳理与迁移计划 | `MD` (12 KB) |
| [kv_tier_model.md](04-security-vault-and-iam/kv_tier_model.md) | Vault KV 三层模型（规范） | `MD` (6 KB) |
| [manual-unseal.md](04-security-vault-and-iam/manual-unseal.md) | Manually unseal shared Vault cluster nodes | `MD` (3 KB) |
| [multi-cloud-shared-iac-pipeline.md](04-security-vault-and-iam/multi-cloud-shared-iac-pipeline.md) | Provider-neutral shared Vault IaC pipeline design | `MD` (6 KB) |
| [vault-server-goals.md](04-security-vault-and-iam/vault-server-goals.md) | Vault Server goals | `MD` (5 KB) |
| [vault_authentication_and_policy_isolation.md](04-security-vault-and-iam/vault_authentication_and_policy_isolation.md) | Vault Authentication and Policy Isolation | `MD` (9 KB) |

## <a id="05-cloud-infrastructure-and-iac"></a>05. 多云基础设施与 IaC 状态 (Cloud Infrastructure & IaC)

> 多云账户契约、Terraform 状态存储与孤儿锁治理、Akamai / UCloud 节点编排与配置。

| 文件 | 标题 / 说明 | 格式 / 大小 |
| :--- | :--- | :--- |
| [cleanup-batches-20261007.md](05-cloud-infrastructure-and-iac/cleanup-batches-20261007.md) | IaC owner 清理批次与交接记录 | `MD` (7 KB) |
| [howto/terraform-state-storage-multicloud.md](05-cloud-infrastructure-and-iac/howto/terraform-state-storage-multicloud.md) | 多云 Terraform IAC State 存储规范 | `MD` (4 KB) |
| [issue/2026-08-06-terraform-state-orphan-deadlock.md](05-cloud-infrastructure-and-iac/issue/2026-08-06-terraform-state-orphan-deadlock.md) | 案例：Terraform state 里的孤儿实例让 provision 永久卡死（2026-08-06） | `MD` (17 KB) |
| [multi-cloud-account-contract.md](05-cloud-infrastructure-and-iac/multi-cloud-account-contract.md) | Multi-cloud account contract | `MD` (6 KB) |
| [resize-instance.md](05-cloud-infrastructure-and-iac/resize-instance.md) | Resize Instance Workflow | `MD` (2 KB) |
| [uat-prod-bootstrap-runbook.md](05-cloud-infrastructure-and-iac/uat-prod-bootstrap-runbook.md) | Akamai Cloud/Linode UAT 与 PROD Bootstrap Runbook | `MD` (5 KB) |
| [unified-pipeline-v06-implementation.md](05-cloud-infrastructure-and-iac/unified-pipeline-v06-implementation.md) | 多云 IaC pipeline v0.6 实施与验证 | `MD` (6 KB) |

## <a id="06-network-and-xconnect"></a>06. 零信任网络与 XConnect 组网 (Network & XConnect)

> XConnect 零信任网络边界、Overlay 组网原则、网关高可用传输及端到端可观测性。

| 文件 | 标题 / 说明 | 格式 / 大小 |
| :--- | :--- | :--- |
| [XConnect-Zero-Network-Bootstrap.md](06-network-and-xconnect/XConnect-Zero-Network-Bootstrap.md) | XConnect Zero network bootstrap workflow | `MD` (4 KB) |
| [xconnect-cloud-lab.md](06-network-and-xconnect/xconnect-cloud-lab.md) | Formal XConnect UAT integration validation | `MD` (11 KB) |
| [xconnect-gateway-public-transport.md](06-network-and-xconnect/xconnect-gateway-public-transport.md) | XConnect Gateway 公网安全传输入口 | `MD` (2 KB) |
| [xconnect-observability.md](06-network-and-xconnect/xconnect-observability.md) | XConnect Gateway and One observability | `MD` (1 KB) |
| [xconnect-one-network-principles.zh-CN.md](06-network-and-xconnect/xconnect-one-network-principles.zh-CN.md) | XConnect One 网络设计原则 | `MD` (3 KB) |
| [xconnect-persistent-gateway-uat.md](06-network-and-xconnect/xconnect-persistent-gateway-uat.md) | UAT persistent XConnect Gateway | `MD` (3 KB) |
| [xconnect-three-network-boundaries.zh.md](06-network-and-xconnect/xconnect-three-network-boundaries.zh.md) | XConnect Zero 三网络边界 | `MD` (3 KB) |
| [xconnect-uat-overlay-reset.md](06-network-and-xconnect/xconnect-uat-overlay-reset.md) | UAT XConnect overlay reset and address/key policy | `MD` (8 KB) |
| [xconnect-zero-one-gateway-plan.md](06-network-and-xconnect/xconnect-zero-one-gateway-plan.md) | XConnect Zero / Gateway / One 首期闭环规划与实施记录 | `MD` (25 KB) |

## <a id="07-agent-and-execution-ownership"></a>07. Agent 调度与执行权归属 (Agent & Execution Ownership)

> 四仓职责边界（Toolkit / Playbooks / IaC / GitOps）、代码所有权扫描契约与交接凭证。

| 文件 | 标题 / 说明 | 格式 / 大小 |
| :--- | :--- | :--- |
| [2026-10-04-execution-ownership-migration-handoff.md](07-agent-and-execution-ownership/2026-10-04-execution-ownership-migration-handoff.md) | Toolkit 执行职责迁移交接与评估（2026-10-05 更新） | `MD` (32 KB) |
| [2026-10-04-observability-local-health-migration.md](07-agent-and-execution-ownership/2026-10-04-observability-local-health-migration.md) | P0a：Observability 本地 Grafana 健康检查归属迁移 | `MD` (3 KB) |
| [2026-10-05-next-execution-batches-contract.md](07-agent-and-execution-ownership/2026-10-05-next-execution-batches-contract.md) | 后续执行职责迁移合同草案（P3 / P4 / 横向收敛） | `MD` (14 KB) |
| [2026-10-05-ownership-migration-handoff.md](07-agent-and-execution-ownership/2026-10-05-ownership-migration-handoff.md) | 执行职责迁移交接快照（2026-10-05） | `MD` (12 KB) |
| [2026-10-05-ownership-scanner-contract.md](07-agent-and-execution-ownership/2026-10-05-ownership-scanner-contract.md) | Toolkit ownership scanner 行为合同（2026-10-05） | `MD` (4 KB) |
| [2026-10-06-uat-web-saas-close-loop.md](07-agent-and-execution-ownership/2026-10-06-uat-web-saas-close-loop.md) | UAT Web SaaS empty-host acceptance closure | `MD` (4 KB) |
| [2026-10-07-xconnect-host-owner-cutover.md](07-agent-and-execution-ownership/2026-10-07-xconnect-host-owner-cutover.md) | XConnect host owner cutover gate (2026-10-07) | `MD` (3 KB) |
| [uat-feature-release-and-schema-upgrade.md](07-agent-and-execution-ownership/uat-feature-release-and-schema-upgrade.md) | UAT 特性验收与原地 Schema 升级工作流 | `MD` (5 KB) |
| [workflow-dispatch-catalog.md](07-agent-and-execution-ownership/workflow-dispatch-catalog.md) | Agent workflow_dispatch 目录 | `MD` (14 KB) |
| [xworkmate-openclaw-uat-automation.md](07-agent-and-execution-ownership/xworkmate-openclaw-uat-automation.md) | XWorkmate / OpenClaw UAT 自动化边界 | `MD` (3 KB) |

## <a id="08-runbooks-and-cases"></a>08. 运维实战、演练与案例 (Runbooks & Cases)

> 生产/UAT 故障排查、TLS 死锁修复、全链路演练手册及双语灾难恢复演练记录。

| 文件 | 标题 / 说明 | 格式 / 大小 |
| :--- | :--- | :--- |
| [EN/BackUP/backup_dr_plan.md](08-runbooks-and-cases/EN/BackUP/backup_dr_plan.md) | Full-Site Unified Backup & DR Plan | `MD` (1 KB) |
| [EN/Systems-Overview/PROD/live_systems_overview.md](08-runbooks-and-cases/EN/Systems-Overview/PROD/live_systems_overview.md) | Live Environment Business Systems Topology Overview (Caddy) | `MD` (6 KB) |
| [ZH/BackUP/Site-Migration/implementation_plan.md](08-runbooks-and-cases/ZH/BackUP/Site-Migration/implementation_plan.md) | 全站单向数据流迁移与环境复制方案 (Implementation Plan) | `MD` (4 KB) |
| [ZH/BackUP/Site-Migration/walkthrough.md](08-runbooks-and-cases/ZH/BackUP/Site-Migration/walkthrough.md) | 站点迁移与数据同步实施总结 (Walkthrough) | `MD` (4 KB) |
| [ZH/Systems-Overview/PROD/live_systems_overview.md](08-runbooks-and-cases/ZH/Systems-Overview/PROD/live_systems_overview.md) | 线上环境全业务系统拓扑梳理 (Caddy) | `MD` (6 KB) |
| [ZH/Systems-Overview/PROD/orchestrator_api_design.md](08-runbooks-and-cases/ZH/Systems-Overview/PROD/orchestrator_api_design.md) | Orchestrator API Design (后端调度 API 设计) | `MD` (5 KB) |
| [ZH/Systems-Overview/PROD/saas_legacy_backup_guide.md](08-runbooks-and-cases/ZH/Systems-Overview/PROD/saas_legacy_backup_guide.md) | Web SaaS Legacy 旧环境链路资源与备份指南 | `MD` (3 KB) |
| [ZH/Systems-Overview/PROD/services_mapping.md](08-runbooks-and-cases/ZH/Systems-Overview/PROD/services_mapping.md) | 控制面节点 (jp-xhttp-contabo) 服务链路与代理映射白皮书 | `MD` (4 KB) |
| [ZH/security_architecture_matrix.md](08-runbooks-and-cases/ZH/security_architecture_matrix.md) | 全站服务架构与安全基线矩阵 (Security & Architecture Matrix) | `MD` (8 KB) |
| [howto/2026-09-07-prod-login-regional-nodes-recovery.md](08-runbooks-and-cases/howto/2026-09-07-prod-login-regional-nodes-recovery.md) | PROD login and regional node recovery — 2026-09-07 | `MD` (5 KB) |
| [runbook/2026-07-31-web-saas-tls-persistence-deadlock.md](08-runbooks-and-cases/runbook/2026-07-31-web-saas-tls-persistence-deadlock.md) | 案例：web-saas 泛域名证书从未真正复用过（2026-07-28 ~ 2026-07-31） | `MD` (17 KB) |
| [runbook/2026-08-19-serverless-frontend-router-static-quota-optimization.md](08-runbooks-and-cases/runbook/2026-08-19-serverless-frontend-router-static-quota-optimization.md) | 架构案例：Serverless 前端静态资产穿透 Frontend Router 额度优化与多环境 CDN 契约落地 | `MD` (9 KB) |

## <a id="09-plans-and-blueprints"></a>09. 规划方案与产品蓝图 (Plans & Blueprints)

> AI Aggregator 聚合网关规划、控制台演进方案与多环境资源复用规划。

| 文件 | 标题 / 说明 | 格式 / 大小 |
| :--- | :--- | :--- |
| [ai-aggregator-provider-matrix.md](09-plans-and-blueprints/ai-aggregator-provider-matrix.md) | AI Aggregator v1 provider matrix | `MD` (3 KB) |
| [ai-aggregator-v1-cross-repo-delivery.md](09-plans-and-blueprints/ai-aggregator-v1-cross-repo-delivery.md) | AI Aggregator v1 Cross-Repository Delivery | `MD` (3 KB) |
| [gcp-spot-ai-workspace-uat.md](09-plans-and-blueprints/gcp-spot-ai-workspace-uat.md) | AI Workspace UAT：Existing Selfhost 默认路径 | `MD` (2 KB) |
| [hybrid-uat-multicloud-resource-reuse.md](09-plans-and-blueprints/hybrid-uat-multicloud-resource-reuse.md) | UAT Hybrid 多云资源复用与串行部署计划 | `MD` (29 KB) |
| [release-status-console.md](09-plans-and-blueprints/release-status-console.md) | Release status console contract | `MD` (5 KB) |
| [shared-uat-prod-multicloud-environment-delivery.md](09-plans-and-blueprints/shared-uat-prod-multicloud-environment-delivery.md) | Shared / UAT / PROD 多云环境与发布链路规划 | `MD` (57 KB) |

## <a id="10-tasks-archive"></a>10. 历史研发任务审计归档 (Historical Tasks Archive)

> 2026-07 至 2026-10 阶段性交付记录、排障日志、密钥修复底账与日常工作计划。

| 文件 | 标题 / 说明 | 格式 / 大小 |
| :--- | :--- | :--- |
| [2026-07-23-uat-web-saas-deploy-unblocking.md](10-tasks-archive/2026-07-23-uat-web-saas-deploy-unblocking.md) | UAT web-saas 部署解阻 —— 逐层记录 | `MD` (6 KB) |
| [2026-07-24-populate-web-saas-vault-secrets.sh](10-tasks-archive/2026-07-24-populate-web-saas-vault-secrets.sh) | 2026-07-24-populate-web-saas-vault-secrets.sh | `SH` (3 KB) |
| [2026-07-24-secret-leak-ledger.md](10-tasks-archive/2026-07-24-secret-leak-ledger.md) | 密钥泄露台账（2026-07-24） | `MD` (3 KB) |
| [2026-07-24-web-saas-uat-session-summary.md](10-tasks-archive/2026-07-24-web-saas-uat-session-summary.md) | web-saas UAT 打通 —— 阶段汇总（2026-07-24） | `MD` (8 KB) |
| [2026-07-25-delivery-chain-workplan.md](10-tasks-archive/2026-07-25-delivery-chain-workplan.md) | 交付链工作计划：CI 收敛 → compose 补全 → UAT 端到端 | `MD` (16 KB) |
| [2026-07-25-service-repo-ci-only-migration.md](10-tasks-archive/2026-07-25-service-repo-ci-only-migration.md) | 任务规划:业务仓库收敛为纯 CI(交接文档) | `MD` (10 KB) |
| [2026-07-26-ci-debugging-subagents-compose-and-uat-end-to-end.md](10-tasks-archive/2026-07-26-ci-debugging-subagents-compose-and-uat-end-to-end.md) | 任务 4 详细规划：CI 子代理调试 + 四域 compose 补全 + UAT 端到端跑通 | `MD` (16 KB) |
| [2026-07-26-console-build-and-prod-leak-audit.md](10-tasks-archive/2026-07-26-console-build-and-prod-leak-audit.md) | console 构建解阻 + PROD 直连审计 —— 记录 | `MD` (4 KB) |
| [2026-07-26-gitops-compose-domain-migration-plan.md](10-tasks-archive/2026-07-26-gitops-compose-domain-migration-plan.md) | 任务 2 详细规划：`ai-workspace` / `agent-proxy` / `open-platform` 迁移到 compose + Doco-CD | `MD` (7 KB) |
| [2026-07-26-single-tag-environment-replica.md](10-tasks-archive/2026-07-26-single-tag-environment-replica.md) | 单个 tag 点拉起 SIT / UAT / PROD 环境副本 | `MD` (5 KB) |
| [2026-07-29-daily-snapshot-immutable-tag-and-latest-success.md](10-tasks-archive/2026-07-29-daily-snapshot-immutable-tag-and-latest-success.md) | Daily Snapshot：不可变 Tag 与最新成功快照 | `MD` (6 KB) |
| [2026-07-29-domain-wildcard-tls-reuse.md](10-tasks-archive/2026-07-29-domain-wildcard-tls-reuse.md) | DNS-01 wildcard TLS reuse for Caddy and stunnel | `MD` (4 KB) |
| [2026-07-29-observability-agent-deployment.md](10-tasks-archive/2026-07-29-observability-agent-deployment.md) | 监控 Agent 自动部署功能交付报告 | `MD` (2 KB) |
| [2026-07-29-rotate-domain-tls-certs.sh](10-tasks-archive/2026-07-29-rotate-domain-tls-certs.sh) | 2026-07-29-rotate-domain-tls-certs.sh | `SH` (6 KB) |
| [2026-07-30-multi-resource-vps-end-to-end-verification-summary.md](10-tasks-archive/2026-07-30-multi-resource-vps-end-to-end-verification-summary.md) | 2026-07-30 独立 VPS 多域组合 (web-saas + agent-proxy) 端到端验证与架构优化总结 | `MD` (4 KB) |
| [2026-07-30-tech-sharing-multi-cloud-gitops-linkedin.md](10-tasks-archive/2026-07-30-tech-sharing-multi-cloud-gitops-linkedin.md) | 🚀 Elevating Multi-Cloud Delivery: Our Journey with Docker, GitOps, Vault, and GitHub Actions | `MD` (9 KB) |
| [2026-07-30-tech-sharing-multi-cloud-gitops.md](10-tasks-archive/2026-07-30-tech-sharing-multi-cloud-gitops.md) | 🚀 多云多环境下的 Docker + GitOps + Vault 自动化工程实践 | `MD` (10 KB) |
| [2026-07-30-verify-vault-tls-cert.sh](10-tasks-archive/2026-07-30-verify-vault-tls-cert.sh) | 2026-07-30-verify-vault-tls-cert.sh | `SH` (2 KB) |
| [2026-07-31-upload-vault-tls-cert.sh](10-tasks-archive/2026-07-31-upload-vault-tls-cert.sh) | 2026-07-31-upload-vault-tls-cert.sh | `SH` (10 KB) |
| [2026-08-01-uat-probes-production-endpoints.md](10-tasks-archive/2026-08-01-uat-probes-production-endpoints.md) | UAT `web-saas + agent-proxy` 鲁棒性部署验收用例 | `MD` (8 KB) |
| [2026-08-02-billing-caddy-cross-node-ingress.md](10-tasks-archive/2026-08-02-billing-caddy-cross-node-ingress.md) | Billing Caddy 跨节点入口交付记录 | `MD` (2 KB) |
| [2026-08-02-uat-agent-proxy-r3-debug.md](10-tasks-archive/2026-08-02-uat-agent-proxy-r3-debug.md) | UAT agent-proxy r3 / r4 链路调试记录 | `MD` (8 KB) |
| [2026-08-02-uat-only-dns-auto-update-audit.md](10-tasks-archive/2026-08-02-uat-only-dns-auto-update-audit.md) | UAT-only DNS 自动更新审计与实现记录 | `MD` (3 KB) |
| [2026-08-02-uat-r2-xray-billing-observability-change-log.md](10-tasks-archive/2026-08-02-uat-r2-xray-billing-observability-change-log.md) | UAT r2：Xray → Exporter → Billing → PostgreSQL → Accounts → Portal 变更记录 | `MD` (10 KB) |
| [2026-08-02-uat-r6-chain-closeout.md](10-tasks-archive/2026-08-02-uat-r6-chain-closeout.md) | UAT r6：Xray 账单与实时监控链路收口记录 | `MD` (6 KB) |
| [2026-08-02-uat-snapshot-deploy-progress.md](10-tasks-archive/2026-08-02-uat-snapshot-deploy-progress.md) | UAT 快照部署与统计链路进度（2026-08-02） | `MD` (6 KB) |
| [2026-08-02-uat-xray-billing-fanout-r5-rerun.md](10-tasks-archive/2026-08-02-uat-xray-billing-fanout-r5-rerun.md) | UAT r5：Xray → Exporter → Vector → Billing 闭环重跑 | `MD` (2 KB) |
| [2026-08-02-uat-xray-billing-observability-chain-audit.md](10-tasks-archive/2026-08-02-uat-xray-billing-observability-chain-audit.md) | UAT 两条 Xray 链路分段审计与验收清单 | `MD` (5 KB) |
| [2026-08-03-local-ansible-hvac.md](10-tasks-archive/2026-08-03-local-ansible-hvac.md) | 2026-08-03 UAT Agent Proxy Gate: local Ansible hvac dependency | `MD` (1 KB) |
| [2026-08-03-readonly-sources-web-saas-migration-plan.md](10-tasks-archive/2026-08-03-readonly-sources-web-saas-migration-plan.md) | Web SaaS 只读 Source → Target 单向迁移规划 | `MD` (9 KB) |
| [2026-08-03-uat-bootstrap-runtime.md](10-tasks-archive/2026-08-03-uat-bootstrap-runtime.md) | UAT Bootstrap / Gate 运行时问题记录 | `MD` (1 KB) |
| [2026-08-03-uat-destroy-redeploy-routing-fix.md](10-tasks-archive/2026-08-03-uat-destroy-redeploy-routing-fix.md) | UAT destroy/redeploy routing fix — 2026-08-03 | `MD` (3 KB) |
| [2026-08-03-uat-r6-final-handoff.md](10-tasks-archive/2026-08-03-uat-r6-final-handoff.md) | UAT r6 deployment and pipeline handoff | `MD` (23 KB) |
| [2026-08-03-uat-r7-chain-findings.md](10-tasks-archive/2026-08-03-uat-r7-chain-findings.md) | UAT r7:计费链路实勘与两处源头修复 | `MD` (7 KB) |
| [2026-08-11-github-actions-observability-plan.md](10-tasks-archive/2026-08-11-github-actions-observability-plan.md) | GitHub Actions CI/CD 可观测性计划草案 | `MD` (13 KB) |
| [2026-08-15-github-actions-composite-actions-refactor.md](10-tasks-archive/2026-08-15-github-actions-composite-actions-refactor.md) | GitHub Actions Composite Actions 与 Vault SMTP 迁移 | `MD` (4 KB) |
| [2026-08-19-cloudflare-uat-login-path-repair.md](10-tasks-archive/2026-08-19-cloudflare-uat-login-path-repair.md) | Cloudflare UAT 登录链路修复（跨界导航 + CORS 403 + 网关白名单 + 错误码映射） | `MD` (11 KB) |
| [2026-08-21-uat-serverless-billing-dynamic-routing-case.md](10-tasks-archive/2026-08-21-uat-serverless-billing-dynamic-routing-case.md) | UAT Serverless Billing 动态入口验证 Case | `MD` (8 KB) |
| [2026-09-04-prod-agent-proxy-debug-runbook.md](10-tasks-archive/2026-09-04-prod-agent-proxy-debug-runbook.md) | PROD Agent Proxy 调试与验收 Runbook | `MD` (15 KB) |
| [handover_dns_switch_debugging.md](10-tasks-archive/handover_dns_switch_debugging.md) | Handover: CD Pipeline & DNS Switch Debugging | `MD` (7 KB) |
| [migrate_multi_cloud_oidc_and_cleanup_pipeline.md](10-tasks-archive/migrate_multi_cloud_oidc_and_cleanup_pipeline.md) | Migrate Multi-Cloud Auth to OIDC and Cleanup Pipeline Dependencies | `MD` (3 KB) |
| [project_planning_and_progress.md](10-tasks-archive/project_planning_and_progress.md) | Platform Operations Toolkit (SVC.plus) - 项目规划与进度 | `MD` (5 KB) |
| [tag-ai-workspace-mains.sh](10-tasks-archive/tag-ai-workspace-mains.sh) | tag-ai-workspace-mains.sh | `SH` (12 KB) |

## <a id="assets"></a>11. 视觉资产与监控拓扑 (Assets)

> Grafana 监控看板截图、Process Exporter 资源分布树状图、UAT 控制台界面与业务流程图。

| 文件 | 标题 / 说明 | 格式 / 大小 |
| :--- | :--- | :--- |
| [node-exporter.png](assets/node-exporter.png) | node-exporter.png | `PNG` (250 KB) |
| [plans/homepage/homepage-01.png](assets/plans/homepage/homepage-01.png) | homepage-01.png | `PNG` (1173 KB) |
| [plans/homepage/homepage-02.png](assets/plans/homepage/homepage-02.png) | homepage-02.png | `PNG` (1190 KB) |
| [plans/homepage/homepage-03.png](assets/plans/homepage/homepage-03.png) | homepage-03.png | `PNG` (1196 KB) |
| [plans/open-platform/homepage-overview.png](assets/plans/open-platform/homepage-overview.png) | homepage-overview.png | `PNG` (1252 KB) |
| [plans/open-platform/panel.png](assets/plans/open-platform/panel.png) | panel.png | `PNG` (1235 KB) |
| [plans/open-platform/price.png](assets/plans/open-platform/price.png) | price.png | `PNG` (1169 KB) |
| [plans/open-platform/product.png](assets/plans/open-platform/product.png) | product.png | `PNG` (1198 KB) |
| [plans/open-platform/serivces-01.png](assets/plans/open-platform/serivces-01.png) | serivces-01.png | `PNG` (1257 KB) |
| [plans/xstream-platform/homepage-overview.png](assets/plans/xstream-platform/homepage-overview.png) | homepage-overview.png | `PNG` (1252 KB) |
| [plans/xstream-platform/panel.png](assets/plans/xstream-platform/panel.png) | panel.png | `PNG` (1235 KB) |
| [plans/xstream-platform/price.png](assets/plans/xstream-platform/price.png) | price.png | `PNG` (1169 KB) |
| [plans/xstream-platform/product.png](assets/plans/xstream-platform/product.png) | product.png | `PNG` (1198 KB) |
| [plans/xstream-platform/serivces-01.png](assets/plans/xstream-platform/serivces-01.png) | serivces-01.png | `PNG` (1257 KB) |
| [platform-ops-workflow.png](assets/platform-ops-workflow.png) | platform-ops-workflow.png | `PNG` (98 KB) |
| [process-exporter-metrics.png](assets/process-exporter-metrics.png) | process-exporter-metrics.png | `PNG` (159 KB) |
| [process-exporter-treemap.png](assets/process-exporter-treemap.png) | process-exporter-treemap.png | `PNG` (101 KB) |
| [uat-console.png](assets/uat-console.png) | uat-console.png | `PNG` (339 KB) |
