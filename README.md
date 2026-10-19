# knowledge

云原生应用工坊的内容资产仓库，用于存放工程信号、技术长文、随笔与 Workshop 文档。

- `docs/` 是 `docs.svc.plus` 的规范输入，入口见 [docs/README.md](docs/README.md)，导航由 [docs/navigation.zh.yaml](docs/navigation.zh.yaml) / [docs/navigation.en.yaml](docs/navigation.en.yaml) 控制。
- `content/` 存放博客式内容（随笔、资讯雷达、技术专题）和 Portal 网站文案（`content/website/`）。
- 新文档的 frontmatter 约定见 [docs/CONTENT_SCHEMA.md](docs/CONTENT_SCHEMA.md)。
- 本页只做导航：文件不因本索引而移动；标注为 draft / review-draft / proposed 的条目不代表已实施或已验收。

## 目录

1. [产品与解决方案](#1-产品与解决方案)
2. [多云平台工程：白皮书与参考规范](#2-多云平台工程白皮书与参考规范)
3. [架构与设计](#3-架构与设计)
4. [IaC、GitOps 与 DevSecOps](#4-iacgitops-与-devsecops)
5. [网关、网络与基础设施平台](#5-网关网络与基础设施平台)
6. [可观测性](#6-可观测性)
7. [性能优化与验收报告](#7-性能优化与验收报告)
8. [与 AI 协作参考指南（2026）](#8-与-ai-协作参考指南2026)
9. [服务文档集（docs.svc.plus）](#9-服务文档集docssvcplus)
10. [随笔与系列专栏](#10-随笔与系列专栏)
11. [研究报告](#11-研究报告)
12. [Cloud-Neutral Radar 资讯雷达](#12-cloud-neutral-radar-资讯雷达)
13. [网站内容（Portal）](#13-网站内容portal)
14. [运营、发布与工具](#14-运营发布与工具)
15. [目录结构](#目录结构)

双语页按「中文 · English」成对列出。

## 1. 产品与解决方案

### 产品专题（2026-09-22）

- XWorkmate：[如何把 AI 带进真实工作](content/00-global/products/2026-09-22-xworkmate-product-focus.zh.md) · [English](content/00-global/products/2026-09-22-xworkmate-product-focus.en.md)
- XConnect：[为 AI 工作提供稳定连接](content/00-global/products/2026-09-22-xconnect-product-focus.zh.md) · [English](content/00-global/products/2026-09-22-xconnect-product-focus.en.md)
- AI Workspace：[从对话走向交付](content/00-global/products/2026-09-22-ai-workspace-product-focus.zh.md) · [English](content/00-global/products/2026-09-22-ai-workspace-product-focus.en.md)
- Open Platform：[保留代码、数据与部署控制权](content/00-global/products/2026-09-22-open-platform-product-focus.zh.md) · [English](content/00-global/products/2026-09-22-open-platform-product-focus.en.md)

### XWorkmate / AI Workspace

- [AI Workspace 顶层架构与远景项目设计（系列 5 篇）](docs/design/ai-workspace-architecture-vision/README.md)（Vision / Architecture Draft）：[1 愿景与组织边界](docs/design/ai-workspace-architecture-vision/01-vision-and-org-boundaries.zh.md) · [2 总体架构与声明式契约](docs/design/ai-workspace-architecture-vision/02-architecture-and-workspace-spec.zh.md) · [3 Lego 模型与产品演进](docs/design/ai-workspace-architecture-vision/03-lego-model-and-product-evolution.zh.md) · [4 Services、Lab、XConnect 与 Infra](docs/design/ai-workspace-architecture-vision/04-services-lab-xconnect-infra.zh.md) · [5 治理、Roadmap 与 North Star](docs/design/ai-workspace-architecture-vision/05-governance-roadmap-north-star.zh.md)
- [AI Workspace 演变记录：从 Chat 到可验证的 Agent 工作空间](content/00-global/essays/ai-workspace-evolution/index.md)（review-draft，6 篇）
- [AI Workspace 架构验证 Test Cases](docs/ai-workspace-validation-test-cases.md)
- [AI App 都卷成这样了，我为什么还要继续做 Xworkmate？](content/00-global/essays/2026-07-30-Why-I-Keep-Building-Xworkmate.zh.md) · [English](content/00-global/essays/2026-07-30-Why-I-Keep-Building-Xworkmate.en.md)
- 使用案例（见 [§10 使用案例](#xworkmate--ai-workspace-使用案例)）

### XConnect

- [一个人、4 台设备、5 端全平台：自建 XConnect 零信任私网（系列 5 篇）](content/04-infra-platform/xconnect-zero-trust-network/README.md)：[1 成熟方案为何失灵](content/04-infra-platform/xconnect-zero-trust-network/01-why-mature-mesh-falls-short.zh.md) · [2 分层设计与拓扑演进](content/04-infra-platform/xconnect-zero-trust-network/02-architecture-and-topology.zh.md) · [3 三大场景实战](content/04-infra-platform/xconnect-zero-trust-network/03-field-scenarios.zh.md) · [4 指标对比与写在最后](content/04-infra-platform/xconnect-zero-trust-network/04-benchmarks-and-reflections.zh.md) · [5 控制面上线](content/04-infra-platform/xconnect-zero-trust-network/05-control-plane-launch.zh.md)
  - English (Parts 1–4): [1](content/04-infra-platform/xconnect-zero-trust-network/01-why-mature-mesh-falls-short.en.md) · [2](content/04-infra-platform/xconnect-zero-trust-network/02-architecture-and-topology.en.md) · [3](content/04-infra-platform/xconnect-zero-trust-network/03-field-scenarios.en.md) · [4](content/04-infra-platform/xconnect-zero-trust-network/04-benchmarks-and-reflections.en.md)
- [XConnect 架构演进与突围之路](content/00-global/essays/2026-08-14-XConnect-Architecture-Evolution-and-Breakthrough.zh.md) · [English](content/00-global/essays/2026-08-14-XConnect-Architecture-Evolution-and-Breakthrough.en.md)
- [自建零信任网络应用案例：XConnect + AI Agent 协同 Vault 跨云迁移](content/00-global/essays/2026-10-01-xconnect-zero-trust-vault-migration.zh.md) · [English](content/00-global/essays/2026-10-01-xconnect-zero-trust-vault-migration.en.md)
- [XConnect + Vault 迁移、部署、扩缩容与回滚运行手册](products/solution/open-platform/IAC/xconnect-vault-migration-runbook.zh-CN.md) · [English](products/solution/open-platform/IAC/xconnect-vault-migration-runbook.en.md)
- 性能与稳定性报告见 [§7](#7-性能优化与验收报告)

### Open Platform / 多云 IaC

- [撕破云厂高墙：把割裂的异构云拧成一股绳（系列 5 篇）](content/02-iac-devops/multi-cloud-iac-mesh/README.md)：[1 背景与 FinOps 对冲](content/02-iac-devops/multi-cloud-iac-mesh/01-background-and-finops-arbitrage.zh.md) · [2 S3 统一 IaC 状态](content/02-iac-devops/multi-cloud-iac-mesh/02-unified-iac-state-on-s3.zh.md) · [3 Zero-Secret 凭据网络](content/02-iac-devops/multi-cloud-iac-mesh/03-zero-secret-credential-mesh.zh.md) · [4 Global Mesh 与跨仓库闭环](content/02-iac-devops/multi-cloud-iac-mesh/04-global-mesh-and-cross-repo-orchestration.zh.md) · [5 迁移与验收](content/02-iac-devops/multi-cloud-iac-mesh/05-migration-and-verification.zh.md)
  - English: [1](content/02-iac-devops/multi-cloud-iac-mesh/01-background-and-finops-arbitrage.en.md) · [2](content/02-iac-devops/multi-cloud-iac-mesh/02-unified-iac-state-on-s3.en.md) · [3](content/02-iac-devops/multi-cloud-iac-mesh/03-zero-secret-credential-mesh.en.md) · [4](content/02-iac-devops/multi-cloud-iac-mesh/04-global-mesh-and-cross-repo-orchestration.en.md) · [5](content/02-iac-devops/multi-cloud-iac-mesh/05-migration-and-verification.en.md)
- [GCP Cloud IAC 方案：Bootstrap OIDC、凭据分层与多云 Landing Zone 接入](products/solution/open-platform/IAC/gcp-oidc-bootstrap-solution.md)
- [GCP OIDC Bootstrap 交接文档](products/solution/open-platform/IAC/gcp-oidc-bootstrap-handoff.md)

### Global Mesh / Cloud Hub

- [Global Mesh（Cloud Hub）产品介绍与云中立现代架构深度白皮书](docs/zh/products-global-mesh.md) · [English](docs/en/products-global-mesh.md)（唯一权威版本，原副本已合并）
- [App Hub、Cloud Hub、FinOps 统一数据模型](docs/reference/unified-hub-data-model.zh.md)（0.1，待评审）

## 2. 多云平台工程：白皮书与参考规范

- [参考资料总索引与 PDF 合订编排](docs/reference/index.md)（42 项来源索引）
- [多云平台工程技术白皮书](docs/reference/multi-cloud-platform-engineering-whitepaper.zh.md) · [English](docs/reference/multi-cloud-platform-engineering-whitepaper.en.md)（review-draft；覆盖四仓职责、40 个 workflow 调用链、GitOps 与 IaC state、Vault 路径/权限及迁移验收，源码基线 2026-10-05）
- [多云资源三档权限、IAM 与 Vault 安全集成及 Shared CMDB 技术规范白皮书](docs/reference/multi-cloud-iam-vault-cmdb-security-whitepaper.zh.md)（proposed-not-applied）
- [App Hub、Cloud Hub、FinOps 统一数据模型](docs/reference/unified-hub-data-model.zh.md)（draft，待评审）

### CMDB

- [多云与 Serverless 动态 CMDB：独立 PostgreSQL 与 Grafana 落地规划](docs/reference/multi-cloud-cmdb-postgresql-grafana-plan.zh.md)（implementation-plan）
- [CMDB 多云采集与数据库 Vault 路径规划](docs/reference/cmdb-vault-paths.zh.md)（proposed-not-applied）
- [CMDB Shared UAT 部署与采集验收记录（2026-10-09）](docs/reference/cmdb-shared-uat-evidence-20261009.zh.md)（partial-live-verification）

### IaC Pipeline 与 Daily Snapshot

- [六云统一 IaC Pipeline：Bootstrap、账号、资源与销毁设计](docs/reference/multi-cloud-iac-unified-pipeline-design.zh.md)（design-draft）
- [多云 IaC Pipeline v0.6：清理与执行归属迁移记录（2026-10-07）](docs/reference/multi-cloud-iac-cleanup-batches-20261007.zh.md)
- [Platform Ops Toolkit Daily Main Snapshot 实施规划](docs/reference/platform-ops-toolkit-daily-main-snapshot-plan.zh.md) · 附：[源码审计候选](docs/reference/platform-ops-toolkit-daily-main-snapshot/audit.md) · [表格](docs/reference/platform-ops-toolkit-daily-main-snapshot/tables.md)
- [平台操作中心与 Daily Snapshot 发布验收架构](docs/design/platform-operations-daily-snapshot.zh.md)

### 数据库安全操作

- [Supabase 操作参考：专用只读角色、RLS 与受控连接](docs/reference/supabase-operations.zh.md) · [English](docs/reference/supabase-operations.en.md)

### AI Workspace 执行器与记忆

- [AI Workspace、XWorkmate 多执行器与三级记忆技术白皮书规划](docs/reference/ai-workspace-agent-memory-whitepaper-plan.zh.md)（review-draft）
- [AI Workspace 三套架构版本图与迁移验收索引](docs/reference/ai-workspace-agent-memory-variants.zh.md)（review-draft）

## 3. 架构与设计

### 混合部署、容灾与运行时

- [VPS + Serverless 混合部署极简成本架构规划与工程落地指南（7 章）](docs/zh/hybrid-serverless-architecture-vault-pipeline-plan/README.md) · 单页合订版：[中文](docs/zh/hybrid-serverless-architecture-vault-pipeline-plan.md) · [English（UAT on Serverless）](docs/en/uat-serverless-architecture-vault-pipeline-plan.md)
- [控制面混合云弹性容灾与零成本流量调度架构实践](docs/zh/hybrid-serverless-architecture-and-zero-cost-failover.md) · [English](docs/en/hybrid-serverless-architecture-and-zero-cost-failover.md)
- [全栈三层立体容灾矩阵架构设计与工程落地](docs/zh/full-stack-three-tier-fallback-matrix.md) · [English](docs/en/full-stack-three-tier-fallback-matrix.md)
- [UAT Serverless 运行时拓扑、路由契约与全链路验证指南](docs/zh/serverless-uat-runtime-topology-and-verification.md) · [English](docs/en/serverless-uat-runtime-topology-and-verification.md)
- [Console Frontend Router 与 Edge Gateway 目标架构及实施计划](docs/zh/frontend-edge-routing-target-architecture.md)
- [多云 Hybrid / Selfhost / Serverless 编排架构规划](content/02-iac-devops/cloud-infrastructure-devsecops-baseline/10-multi-cloud-orchestrator-architecture.zh.md)

### 数据与可观测架构选型

- [PostgreSQL 架构选型与 Observability 接入指南](docs/zh/supabase-architecture-and-observability.md) · [English](docs/en/supabase-architecture-and-observability.md)
- [Observability 多模式兼容与平滑演进指南](docs/zh/observability-flexible-deployment-modes.md) · [English](docs/en/observability-flexible-deployment-modes.md)

### 内容与网站架构

- [Console 与 content-service 内容架构规范](docs/design/console-docs-content-architecture.zh.md) · [English](docs/design/console-docs-content-architecture.en.md)
- [公司主页、产品矩阵与合规审核规范](docs/website/company-homepage-and-product-verification-specification.md)

## 4. IaC、GitOps 与 DevSecOps

### 云基础设施 DevSecOps 基线（系列）

- [云基础设施 DevSecOps 基线方法论](content/02-iac-devops/cloud-infrastructure-devsecops-baseline/09-cloud-infrastructure-devsecops-baseline-closing-the-loop.md)
- [多云 Hybrid / Selfhost / Serverless 编排架构规划](content/02-iac-devops/cloud-infrastructure-devsecops-baseline/10-multi-cloud-orchestrator-architecture.zh.md)
- [多云身份 Bootstrap 与状态契约](content/02-iac-devops/cloud-infrastructure-devsecops-baseline/11-cloud-oidc-bootstrap-contract.zh.md) · 操作版：[Cloud OIDC Bootstrap TLDR](content/04-infra-platform/public-cloud-iaas/cloud-oidc-bootstrap-tldr.zh.md)
- [数据库同步与发布晋级状态机](content/02-iac-devops/cloud-infrastructure-devsecops-baseline/12-uat-database-sync-and-prod-promotion-state-machine.zh.md)
- [PROD V2/V3 快照、跨机恢复与升级复盘](content/02-iac-devops/cloud-infrastructure-devsecops-baseline/15-prod-v2-v3-snapshots-and-upgrade-retrospective.zh.md) · 含最新快照证据、复用模板和维护源码归档
- [生产环境“带病升级”如何实现零数据丢失](content/02-iac-devops/cloud-infrastructure-devsecops-baseline/13-prod-v2-upgrade-recovery-zero-data-loss-case.zh.md) · 公众号版：[AI 如何做到 300 客户与 12 万账本零丢失](content/02-iac-devops/cloud-infrastructure-devsecops-baseline/14-wechat-mp-prod-v2-code-agent-zero-loss-case.zh.md)

### GitOps 实践

- [实践验证：Docker 单机也能玩 GitOps](content/00-global/essays/2026-07-31-Docker-Single-Node-GitOps.zh.md) · [English](content/00-global/essays/2026-07-31-Docker-Single-Node-GitOps.en.md)
- [从单机到多云：Zero-Trust GitOps & AI 重塑多环境交付](content/00-global/essays/2026-07-30-From-Single-Node-to-Multi-Cloud.zh.md) · [English](content/00-global/essays/2026-07-30-From-Single-Node-to-Multi-Cloud.en.md)
- [平台工程的核心命题：开发环境 ≠ 构建环境 ≠ 运行环境](content/00-global/essays/2026-07-31-Platform-Engineering-Environment-Isolation-and-Convergence.zh.md) · [English](content/00-global/essays/2026-07-31-Platform-Engineering-Environment-Isolation-and-Convergence.en.md)
- [实践验证：PROD 数据如何安全“倒灌”到 UAT](content/00-global/essays/2026-08-07-PROD-to-UAT-Data-Mirror-and-Validation.zh.md) · [English](content/00-global/essays/2026-08-07-PROD-to-UAT-Data-Mirror-and-Validation.en.md)
- [Argo CD 系列](content/02-iac-devops/argo-cd/README.md)（已有：[使用 Argo CD 管理 Helm / Helmfile](content/02-iac-devops/argo-cd/04-helm-and-helmfile.md)、[Application 与同步模型](content/02-iac-devops/argo-cd/03-application-and-sync-model.md)）

### AI 聚合服务（Ansible 交付）

- [个人 AI 聚合服务 v1：架构、选型与实施交付契约](content/02-iac-devops/ansible/ai-aggregator-v1-architecture-and-delivery.zh.md)
- [AI Gateway v1 架构图](content/02-iac-devops/ansible/ai-aggregator-v1-architecture-diagram.zh.md)
- [AI Aggregator：GitOps 声明路径与 Vault 凭据全景规格说明书](content/02-iac-devops/ansible/ai-aggregator-vault-and-gitops-specification.zh.md)

### Workshop

- [AWS × GitHub 一次性 Bootstrap（Terraform Backend + GitHub OIDC）](content/06-workshops/id-security-workshop-01-AWS-Global-Bootstrap-Terraform-Backend-GitHub-OIDC.md)

## 5. 网关、网络与基础设施平台

- [AI Gateway 统一入口：设计、Home-Lab 状态与实施任务](content/04-infra-platform/apisix/ai-gateway-unified-entrypoint.zh.md)
- [AI Aggregator Gateway：选型、架构与 Home-Lab 实施](content/04-infra-platform/apisix/ai-aggregator-gateway-architecture.zh.md)
- [AI Aggregator Gateway 对接与验证 TLDR](content/04-infra-platform/apisix/ai-aggregator-client-acceptance-tldr.zh.md)
- [CPA 人工 OAuth TLDR](content/04-infra-platform/apisix/ai-aggregator-cpa-oauth-tldr.zh.md)
- [如何利用好 Free SaaS 开启自己的在线服务](content/04-infra-platform/serverless-edge-cloud/how-to-leverage-free-saas-for-online-services.zh.md) · [English](content/04-infra-platform/serverless-edge-cloud/how-to-leverage-free-saas-for-online-services.en.md)

## 6. 可观测性

- [集中式可观测性服务端架构解密：VictoriaMetrics、VictoriaLogs、Grafana 与 MCP](content/03-observability/observability-server-core.zh.md) · [English](content/03-observability/observability-server-core.en.md)
- [云原生可观测性 Agent 架构：Vector 与 Exporters 数据管线](content/03-observability/vector/observability-agent-architecture.zh.md) · [English](content/03-observability/vector/observability-agent-architecture.en.md)
- [独立开发观察者计划：可观测 SaaS 实践专题（观测云 / Guance）](content/03-observability/guance-data-ai/README.md)（planning）
  - [年度内容合作方案](content/03-observability/guance-data-ai/00-annual-content-plan.md) · [深度调研与事实基线](content/03-observability/guance-data-ai/01-guance-research-brief.md) · [UAT 到 PROD 接入路线图](content/03-observability/guance-data-ai/02-xworktech-guance-integration-roadmap.md) · [2026-10 事实核验记录](content/03-observability/guance-data-ai/03-fact-check-2026-10.md)
  - 文章大纲：[个人 SaaS 为什么先试观测云免费专区](content/03-observability/guance-data-ai/articles/01-free-tier-for-indie-saas/outline.md) · [从自建 observability 到 Guance 的平滑迁移](content/03-observability/guance-data-ai/articles/02-observability-migration-with-rollback/outline.md)（附 [迁移矩阵](content/03-observability/guance-data-ai/articles/02-observability-migration-with-rollback/migration-matrix.md)）

## 7. 性能优化与验收报告

- [性能优化归档](docs/performance-optimization/README.md)
- [XWorkTech 性能调优技术白皮书与工程规范](docs/reference/performance-optimization-whitepaper.zh.md)（review-draft）
- [jp-xconnect 内存与日志优化分析报告（2026-10-10）](docs/performance-optimization/jp-xconnect-memory-log-optimization-20261010.zh.md)
- [JP XConnect 稳定性增量配置验证报告（2026-10-14）](docs/reference/performance-optimization-jp-xconnect-stability-20261014.zh.md)
- [XConnect Free 节点大文件上传实测与优化验收（2026-10-18）](docs/performance-optimization/xconnect-free-proxy-upload-acceptance-20261018.zh.md)

## 8. 与 AI 协作参考指南（2026）

从 Model Selection（模型选秀）走向 Model Routing（模型路由与团队建制）：

- [中文专栏索引与全渠道指南](docs/ai-collaboration-guide/overview.zh.md) · [English Series Index](docs/ai-collaboration-guide/overview.en.md)
- 完整版：[中文](docs/ai-collaboration-guide/full-guide.zh.md) · [English](docs/ai-collaboration-guide/full-guide.en.md)
- 第 1 篇 认知重构：[中文](docs/ai-collaboration-guide/01-cognitive-shift.zh.md) · [English](docs/ai-collaboration-guide/01-cognitive-shift.en.md)
- 第 2 篇 执行双核：[中文](docs/ai-collaboration-guide/02-dual-execution-engines.zh.md) · [English](docs/ai-collaboration-guide/02-dual-execution-engines.en.md)
- 第 3 篇 工程中枢：[中文](docs/ai-collaboration-guide/03-engineering-backbone-and-judge.zh.md) · [English](docs/ai-collaboration-guide/03-engineering-backbone-and-judge.en.md)
- 第 4 篇 事实与壁垒：[中文](docs/ai-collaboration-guide/04-research-grounding-and-specialist.zh.md) · [English](docs/ai-collaboration-guide/04-research-grounding-and-specialist.en.md)
- 第 5 篇 闭环与模型路由：[中文](docs/ai-collaboration-guide/05-closed-loop-and-model-routing.zh.md) · [English](docs/ai-collaboration-guide/05-closed-loop-and-model-routing.en.md)

## 9. 服务文档集（docs.svc.plus）

### 文档站入口与规范

- [docs/ 总入口](docs/README.md) · [中文首页](docs/zh/README.md) · [English home](docs/en/README.md) · [文档首页（服务列表）](docs/index.md)
- 开始使用：[欢迎页](docs/get-started/overview.zh.md) · [Welcome](docs/get-started/overview.en.md)；[快速开始](docs/get-started/quickstart.zh.md) · [Quickstart](docs/get-started/quickstart.en.md)；[项目地图](docs/get-started/project-map.zh.md) · [Project map](docs/get-started/project-map.en.md)
- 基础认知：[总览](docs/core-concepts/overview.zh.md) · [EN](docs/core-concepts/overview.en.md)；[信息架构](docs/core-concepts/information-architecture.zh.md) · [EN](docs/core-concepts/information-architecture.en.md)；[双语支持](docs/core-concepts/bilingual-support.zh.md) · [EN](docs/core-concepts/bilingual-support.en.md)；[发布流程](docs/core-concepts/publishing-workflow.zh.md) · [EN](docs/core-concepts/publishing-workflow.en.md)
- 集成关系：[总览](docs/integrations/overview.zh.md) · [EN](docs/integrations/overview.en.md)；[docs.svc.plus](docs/integrations/docs-svc-plus.zh.md) · [EN](docs/integrations/docs-svc-plus.en.md)；[同步链路](docs/integrations/sync-pipeline.zh.md) · [EN](docs/integrations/sync-pipeline.en.md)
- 参考：[总览](docs/reference/overview.zh.md) · [EN](docs/reference/overview.en.md)；[内容规范](docs/reference/content-schema.zh.md) · [EN](docs/reference/content-schema.en.md)；[覆盖矩阵](docs/reference/coverage-matrix.zh.md) · [EN](docs/reference/coverage-matrix.en.md)；[历史文档映射](docs/reference/legacy-docs.zh.md) · [EN](docs/reference/legacy-docs.en.md)
- 仓库级双语页：[架构](docs/zh/architecture.md) · [EN](docs/en/architecture.md)；[设计](docs/zh/design.md) · [EN](docs/en/design.md)；[部署](docs/zh/deployment.md) · [EN](docs/en/deployment.md)；[使用手册](docs/zh/user-guide.md) · [EN](docs/en/user-guide.md)；[开发手册](docs/zh/developer-guide.md) · [EN](docs/en/developer-guide.md)；[Vibe Coding 参考](docs/zh/vibe-coding-reference.md) · [EN](docs/en/vibe-coding-reference.md)
- 实用指南：[海外 AI 服务注册与订阅实践攻略](docs/get-started/overseas-ai-service-access-guide.zh.md)

### 服务集合

| 服务 | 总览 | 中文 | English | 覆盖矩阵 |
| --- | --- | --- | --- | --- |
| Console（控制台） | [README](docs/01-console/README.md) | [zh](docs/01-console/zh/README.md) | [en](docs/01-console/en/README.md) | [DOC_COVERAGE](docs/01-console/DOC_COVERAGE.md) |
| Accounts（账号与身份） | [README](docs/02-accounts/README.md) | [zh](docs/02-accounts/zh/README.md) | [en](docs/02-accounts/en/README.md) | [DOC_COVERAGE](docs/02-accounts/DOC_COVERAGE.md) |
| RAG Server | [README](docs/03-rag-server/README.md) | [zh](docs/03-rag-server/zh/README.md) | [en](docs/03-rag-server/en/README.md) | [DOC_COVERAGE](docs/03-rag-server/DOC_COVERAGE.md) |
| PostgreSQL | [README](docs/04-postgresql/README.md) | [zh](docs/04-postgresql/zh/README.md) | [en](docs/04-postgresql/en/README.md) | [DOC_COVERAGE](docs/04-postgresql/DOC_COVERAGE.md) |

各服务集合下的计划（`plans/`）、任务归档（`tasks/`）、Runbook 与审计记录：

- Console：[Plans](docs/01-console/plans/README.md) · [任务归档](docs/01-console/tasks/README.md) · [Runbooks](docs/01-console/operations/runbooks/README.md) · [多设备共享会话与任务索引架构](docs/01-console/multi-session-tasks-architecture.md) · [UI 主题与风格重构方案](docs/01-console/ui-refactor-proposal.md) · [首页设计语言：从对话到交付](docs/01-console/design/homepage-conversation-to-delivery.md)
- Accounts：[Runbook 目录](docs/02-accounts/Runbook/README.md) · [任务归档](docs/02-accounts/tasks/README.md) · [Deployment environments](docs/02-accounts/deployment-environments.md) · [Overlay Config Contract](docs/02-accounts/overlay-config-contract.md)
- RAG Server：[Token Auth 维护手册](docs/03-rag-server/TOKEN_AUTH_MANUAL.md) · [Cloud Run 部署指南](docs/03-rag-server/google-cloud-run-howto.md)
- PostgreSQL：[pgvector 初始化](docs/04-postgresql/pg-vector-db-init.md) · [pglogical 双向逻辑复制](docs/04-postgresql/pglogical.md) · [单节点融合迁移手册](docs/04-postgresql/operations/node-consolidation-migration.md) · [Supabase 迁移交接方案](docs/04-postgresql/plan/supabase_migration_handoff.md) · [GitHub Actions CI/CD 配置指南](docs/04-postgresql/guides/github-actions-cicd.md)

## 10. 随笔与系列专栏

### 系列专栏

- [全能 AI 聚合网关实战系列（中英双语，6 篇）](content/00-global/essays/ai-aggregator-gateway/README.md)
  - 选型篇：[中文](content/00-global/essays/ai-aggregator-gateway/01-selection-kong-vs-apisix.zh.md) · [English](content/00-global/essays/ai-aggregator-gateway/01-selection-kong-vs-apisix.en.md)
  - 架构篇：[中文](content/00-global/essays/ai-aggregator-gateway/02-architecture-and-traffic-routing.zh.md) · [English](content/00-global/essays/ai-aggregator-gateway/02-architecture-and-traffic-routing.en.md)
  - 凭据篇：[中文](content/00-global/essays/ai-aggregator-gateway/03-cpa-matrix-and-vault-credentials.zh.md) · [English](content/00-global/essays/ai-aggregator-gateway/03-cpa-matrix-and-vault-credentials.en.md)
  - 实战篇：[中文](content/00-global/essays/ai-aggregator-gateway/04-client-integration-and-gitops.zh.md) · [English](content/00-global/essays/ai-aggregator-gateway/04-client-integration-and-gitops.en.md)
  - 排障篇：[中文](content/00-global/essays/ai-aggregator-gateway/05-inference-troubleshooting-and-ops.zh.md) · [English](content/00-global/essays/ai-aggregator-gateway/05-inference-troubleshooting-and-ops.en.md)
  - [OpenCode CLI 与桌面 App 接入 AI Gateway](content/00-global/essays/ai-aggregator-gateway/06-opencode-cli-and-desktop-integration.zh.md)
- [《AI 时代需要掌握的开发基础知识》（10 篇 + 总结）](content/00-global/essays/ai-era-development-basics/README.md)
- [AI Workspace 演变记录（6 篇）](content/00-global/essays/ai-workspace-evolution/index.md)
- 十一 AI 七日乐：[7 篇独立图文专栏](content/00-global/essays/2026-09-30-7-days-ai-native-daily-posts.zh.md) · [选题与关键词](content/00-global/essays/2026-09-30-golden-week-ai-native-7-day-series.zh.md) · [秋日奥德赛假期漫游手记](content/00-global/essays/2026-10-01-autumn-odyssey-ai-native-news-series.md)

### 技术随笔

- [破解商业壁垒：在多家 AI 编码工具之间打通多 Agent 共享上下文](content/00-global/essays/2026-09-17-multi-agent-shared-context-architecture.zh.md) · [English](content/00-global/essays/2026-09-17-multi-agent-shared-context-architecture.en.md)
- [从刀耕火种到 AI 编程：当代码生成成本趋零，工程师的核心壁垒是什么？](content/00-global/essays/2026-09-29-from-primitive-tools-to-ai-coding.zh.md) · [English](content/00-global/essays/2026-09-29-from-primitive-tools-to-ai-coding.en.md)
- [设计与构建多模型协同软件开发平台](content/00-global/essays/Designing-and-Building-a-Multi-Model-Collaborative-Software-Development-Platform.md)
- [2025：在多云现实中重建工程认知体系](content/00-global/essays/2025-Tech-Exploration-Reframing-Cloud-DevOps-Automation.md)
- [IT 沙龙：从裸金属到云，我们与复杂性的长期战争（2025-12-21）](content/00-global/essays/IT-Salon_From-Bare-Metal-to-the-Cloud-Our-Long-War-on-Complexity_20251221.md)
- [IT 漫谈｜当“小红书下云”遇上“阿里云辟谣”](content/00-global/essays/Beyond-the-Rumor_What-the-Xiaohongshu–Alibaba-Cloud-Controversy-Really-Teaches-Us-About-Cloud-Computing.md)

### AI 与生活 / 创作者

- [2025 年，我已经把 AI 当成了生活的一部分](content/00-global/essays/2025-Living-With-AI-Daily.md)
- [AI 与日常 · 从选题到 AI 辅助创作](content/00-global/essays/AI-and-writing-01.md) · [我开始这样做视频](content/00-global/essays/AI-and-Visual-Expression-02.md) · [一切从人类生活中来，又回到生活中去](content/00-global/essays/AI-and-Everyday-Life-03.md)
- [微信平台｜文字、图文与视频的投入产出比较](content/00-global/essays/WeChat-as-a-Creator-Platform_Traffic-Ads-and-Returns-on-Time.md)
- [注册公司不是终点：内地、香港、美国的真实成本](content/00-global/essays/2026-08-05-company-registration-real-costs-china-hong-kong-us-llc.zh.md) · [English](content/00-global/essays/2026-08-05-company-registration-real-costs-china-hong-kong-us-llc.en.md)

### XWorkmate / AI Workspace 使用案例

| # | 中文 | English | 随笔版 |
| ---: | --- | --- | --- |
| 01 | [一键输出自媒体矩阵文案](content/00-global/use-cases/case_01/XWorkmate_AI-Workspace_使用案例-01：一键输出自媒体矩阵文案_ZH.md) | [EN](content/00-global/use-cases/case_01/XWorkmate_AI-Workspace_Use_Case-01_One-Click_Social_Media_Matrix_EN.md) | [中文](content/00-global/essays/2026-08-12-XWorkmate-Use-Case-01-Social-Media-Matrix.zh.md) · [EN](content/00-global/essays/2026-08-12-XWorkmate-Use-Case-01-Social-Media-Matrix.en.md) |
| 02 | [一句话输出可编辑的 PPT 文件](content/00-global/use-cases/case_02/XWorkmate_AI-Workspace_使用案例-02：一句话输出可编辑的PPT文件_ZH.md) | [EN](content/00-global/use-cases/case_02/XWorkmate_AI-Workspace_Use_Case-02_One-Sentence_to_Editable_PPT_EN.md) | — |
| 03 | [最短一句话快速制作视频](content/00-global/use-cases/case_03/XWorkmate_AI-Workspace_使用案例-03：最短一句话快速制作视频_ZH.md) | [EN](content/00-global/use-cases/case_03/XWorkmate_AI-Workspace_Use_Case-03_Quick_Video_Generation_EN.md) | — |
| 04 | [快速整理个人简历](content/00-global/use-cases/case_04/XWorkmate_AI-Workspace_使用案例-04：快速整理个人简历_ZH.md) | [EN](content/00-global/use-cases/case_04/XWorkmate_AI-Workspace_Use_Case-04_Quick_Resume_Organization_EN.md) | [中文](content/00-global/essays/2026-08-12-XWorkmate-Use-Case-04-Quick-Resume-Organization.zh.md) · [EN](content/00-global/essays/2026-08-12-XWorkmate-Use-Case-04-Quick-Resume-Organization.en.md) |
| 05 | [如何制作视频](content/00-global/use-cases/case_05/XWorkmate_AI-Workspace_使用案例-05：如何制作视频_ZH.md) | [EN](content/00-global/use-cases/case_05/XWorkmate_AI-Workspace_Use_Case-05_How_to_Make_a_Video_EN.md) | — |
| 06 | [把零碎进展，沉淀为清晰工作](content/00-global/use-cases/case_06/XWorkmate_AI-Workspace_使用案例-06：把零碎进展，沉淀为清晰工作_ZH.md) | [EN](content/00-global/use-cases/case_06/XWorkmate_AI-Workspace_Use_Case-06_Turn_Fragmented_Progress_into_Clear_Work_EN.md) | [中文](content/00-global/essays/2026-08-12-XWorkmate-Use-Case-06-Turn-Fragmented-Progress-into-Clear-Work.zh.md) · [EN](content/00-global/essays/2026-08-12-XWorkmate-Use-Case-06-Turn-Fragmented-Progress-into-Clear-Work.en.md) |

案例 07–10 为预留占位，暂不收录。

## 11. 研究报告

- [从对话到工作流的认知跃迁：AI Agent 分层记忆系统与三大纯开源落地架构](research/ai-workspace-and-agent-systems.zh.md) · [English](research/ai-workspace-and-agent-systems.en.md)
- [海外“小而美” Micro-SaaS 深度解构](research/micro-saas-analysis.zh.md) · [English](research/micro-saas-analysis.en.md)
- [国内外电商平台“开放性与垄断性”对比研究](research/e-commerce-openness-vs-monopoly.md)

## 12. Cloud-Neutral Radar 资讯雷达

每个技术领域目录下的 `README.md` 是该项 Radar 的落点；`content/00-global/news/` 存放资讯稿。已有正文的资讯稿：

- 平台基础设施：[KVM / QEMU](content/00-global/news/Cloud-Neutral-Radar-Platform-Foundation-KVM-QEMU.md) · [K3K](content/00-global/news/Cloud-Neutral-Radar-Platform-Foundation-k3k.md) · [K3s](content/00-global/news/Cloud-Neutral-Radar-Platform-Foundation-k3s.md) · [Kubernetes（控制平面）](content/00-global/news/Cloud-Neutral-Radar-Platform-Foundation-kubernetes.md) · [容器引擎](content/00-global/news/Cloud-Neutral-Radar_Runtime-Boundary_Container-Engine.md)
- 交付与变更控制：[Ansible](content/00-global/news/Cloud-Neutral-Radar_Delivery-Change-Control_Ansible.md) · [Argo CD](content/00-global/news/Cloud-Neutral-Radar_Delivery-Change-Control_Argo-CD.md) · [GitLab](content/00-global/news/Cloud-Neutral-Radar_Delivery-Change-Control_GitLab.md) · [Terraform / OpenTofu](content/00-global/news/Cloud-Neutral-Radar_Delivery-Change-Control_Terraform-OpenTofu.md)
- 交付、测试与安全合规：[Teleport](content/00-global/news/Cloud-Neutral-Radar_Delivery-Security-Compliance_Teleport.md) · [DevTools MCP](content/00-global/news/Cloud-Neutral-Radar_Delivery-Test-Quality_DevToolsMCP.md) · [Grafana k6](content/00-global/news/Cloud-Neutral-Radar_Delivery-Test-Quality_Grafana-k6.md) · [Playwright](content/00-global/news/Cloud-Neutral-Radar_Delivery-Test-Quality_Playwright.md)
- 可观测与数据：[DeepFlow](content/00-global/news/Cloud-Neutral-Radar_Observability_DeepFlow.md) · [PostgreSQL 扩展生态](content/00-global/news/Cloud-Neutral-Radar_Data-AI_PostgreSQL.md)
- [Global Weekly Radar](content/00-global/weekly-radar/README.md) · [Global Essays](content/00-global/essays/README.md)

### Radar 覆盖（按领域目录）

- Identity & Security：[Keycloak](content/01-id-security/keycloak/README.md) · [ZITADEL](content/01-id-security/zitadel/README.md) · [Dex](content/01-id-security/dex/README.md) · [Vault](content/01-id-security/vault/README.md) · [SPIFFE / SPIRE](content/01-id-security/spiffe-spire/README.md) · [Trivy](content/01-id-security/trivy/README.md) · [Cosign](content/01-id-security/cosign/README.md)
- IaC & DevOps：[Terraform / OpenTofu](content/02-iac-devops/terraform-opentofu/README.md) · [Pulumi](content/02-iac-devops/pulumi/README.md) · [Argo CD](content/02-iac-devops/argo-cd/README.md) · [FluxCD](content/02-iac-devops/fluxcd/README.md) · [Ansible](content/02-iac-devops/ansible/README.md) · [Puppet](content/02-iac-devops/puppet/README.md) · [GitLab](content/02-iac-devops/gitlab/README.md) · [Gitea](content/02-iac-devops/gitea/README.md)
- Observability：[Prometheus](content/03-observability/prometheus/README.md) · [VictoriaMetrics](content/03-observability/victoriametrics/README.md) · [VictoriaLogs](content/03-observability/victorialogs/README.md) · [OpenTelemetry](content/03-observability/opentelemetry/README.md) · [Grafana](content/03-observability/grafana/README.md) · [OpenObserve](content/03-observability/openobserve/README.md) · [Vector](content/03-observability/vector/README.md)
- Infra & Platform（运行时与资源边界）：[Linux (Runtime)](content/04-infra-platform/linux-runtime/README.md) · [containerd](content/04-infra-platform/containerd/README.md) · [Kubernetes](content/04-infra-platform/kubernetes/README.md) · [Cilium](content/04-infra-platform/cilium/README.md) · [Calico](content/04-infra-platform/calico/README.md) · [Kube-OVN](content/04-infra-platform/kube-ovn/README.md) · [Nginx](content/04-infra-platform/nginx/README.md) · [OpenResty](content/04-infra-platform/openresty/README.md) · [Kong](content/04-infra-platform/kong/README.md) · [APISIX](content/04-infra-platform/apisix/README.md)
- Platform Foundation：[Linux (Platform)](content/04-infra-platform/linux-platform/README.md) · [KVM / QEMU](content/04-infra-platform/kvm-qemu/README.md) · [OpenStack](content/04-infra-platform/openstack/README.md) · [SUSE Harvester](content/04-infra-platform/harvester/README.md) · [Public Cloud IaaS](content/04-infra-platform/public-cloud-iaas/README.md) · [Kubernetes (Platform)](content/04-infra-platform/kubernetes-platform/README.md) · [Serverless & Edge Cloud](content/04-infra-platform/serverless-edge-cloud/README.md)
- Data & AI：[PostgreSQL (pgvector)](content/05-data-ai/postgresql/README.md) · [MySQL](content/05-data-ai/mysql/README.md) · [ClickHouse](content/05-data-ai/clickhouse/README.md) · [DuckDB](content/05-data-ai/duckdb/README.md) · [Doris / StarRocks](content/05-data-ai/doris-starrocks/README.md) · [Databend](content/05-data-ai/databend/README.md) · [Iceberg / Delta Lake](content/05-data-ai/iceberg-delta/README.md) · [Flink](content/05-data-ai/flink/README.md) · [Milvus / Qdrant](content/05-data-ai/milvus-qdrant/README.md)

## 13. 网站内容（Portal）

`content/website/` 由 Portal 仓库按 [content-manifest.yaml](content/website/content-manifest.yaml) 消费，说明见 [content/website/README.md](content/website/README.md)。

- 首页区块（zh / en）：[Hero](content/website/homepage/zh/hero.md) · [EN](content/website/homepage/en/hero.md)；[产品专题](content/website/homepage/zh/products.md) · [EN](content/website/homepage/en/products.md)；[云原生套件](content/website/homepage/zh/operations.md) · [EN](content/website/homepage/en/operations.md)；[快讯](content/website/homepage/zh/news.md) · [EN](content/website/homepage/en/news.md)；[社区](content/website/homepage/zh/community.md) · [EN](content/website/homepage/en/community.md)；[资源](content/website/homepage/zh/resources.md) · [EN](content/website/homepage/en/resources.md)；[支持](content/website/homepage/zh/support.md) · [EN](content/website/homepage/en/support.md)；[营销](content/website/homepage/zh/marketing.md) · [EN](content/website/homepage/en/marketing.md)
- 产品页 Hero（zh / en）：[XWorkmate](content/website/product/xworkmate/zh/hero.md) · [EN](content/website/product/xworkmate/en/hero.md)；[XConnect](content/website/product/xconnect/zh/hero.md) · [EN](content/website/product/xconnect/en/hero.md)；[AI Workspace](content/website/product/ai-workspace/zh/hero.md) · [EN](content/website/product/ai-workspace/en/hero.md)；[Open Platform](content/website/product/open-platform/zh/hero.md) · [EN](content/website/product/open-platform/en/hero.md)；[Global Mesh](content/website/product/global-mesh/zh/hero.md) · [EN](content/website/product/global-mesh/en/hero.md)；[XCloudFlow](content/website/product/xcloudflow/zh/hero.md) · [EN](content/website/product/xcloudflow/en/hero.md)；[XScopeHub](content/website/product/xscopehub/zh/hero.md) · [EN](content/website/product/xscopehub/en/hero.md)；[XStream](content/website/product/xstream/zh/hero.md) · [EN](content/website/product/xstream/en/hero.md)（[功能](content/website/product/xstream/zh/features.md) · [EN](content/website/product/xstream/en/features.md)）
- 长文素材：[LinkedIn：AI 与关键平台工程案例](content/website/product/ai-workspace/linkedin-ai-platform-engineering-case-study.en.md) · [LinkedIn：AI、平台工程与超大规模云谬误](content/website/product/global-mesh/linkedin-ai-platform-engineering.en.md)
- 其他：[Core Team](content/website/about/team.md) · [Docs 首页文案](content/website/docs/zh/home.md) · [EN](content/website/docs/en/home.md) · [Operations Hero](content/website/operations/zh/hero.md) · [EN](content/website/operations/en/hero.md)

## 14. 运营、发布与工具

- X 发布：[@Cloud_Neutral 发布队列总控](threads/x-publish-queue.md) · [X 自动发布系统设计](threads/automation/README.md) · [OpenClaw Cron 调度方案](threads/automation/cron-plan.md)
- 应用商店开发者账号注册攻略模板：[Apple Developer Program](platform-registration/apple_developer_program_org_guide.md) · [Google Play Console](platform-registration/google_play_console_org_guide.md) · [Microsoft Partner Center](platform-registration/microsoft_partner_center_store_guide.md)
- 仓库 Skill：[release-branch-policy](skills/release-branch-policy/SKILL.md)
- 脚本：[scripts/](scripts/)（PDF 生成、Daily Snapshot 审计、服务文档同步等）

### Cloud-Neutral Writing Skills

`scripts/` 下的 `.skill` 文件是 Cloud-Neutral Radar 与 Workshop 内容的可复用写作模板，每个文件是一份独立的指令集，每次生成只加载一个：

- [radar-news.skill](scripts/radar-news.skill)：短 Radar / 判断卡片
- [radar-essay.skill](scripts/radar-essay.skill)：长篇工程分析
- [radar-workshop.skill](scripts/radar-workshop.skill)：决策驱动的 Workshop
- [radar-update.skill](scripts/radar-update.skill)：Radar 更新
- [One-Image-One-Story.skill](scripts/One-Image-One-Story.skill)：一图一故事

## 目录结构

```
README.md                 # 本索引
docs/                     # docs.svc.plus 规范输入
├── get-started/ core-concepts/ integrations/ reference/   # 公开导航四组
├── design/ performance-optimization/ website/
├── zh/ en/               # 仓库级中英文专题与 AI 协作指南
└── 01-console/ 02-accounts/ 03-rag-server/ 04-postgresql/  # 服务文档集
content/                  # 博客式内容与网站文案
├── 00-global/            # essays/ news/ products/ use-cases/ weekly-radar/
├── 01-id-security/  02-iac-devops/  03-observability/
├── 04-infra-platform/  05-data-ai/  06-workshops/
└── website/              # Portal 文案（content-manifest.yaml）
products/solution/        # 产品解决方案与运行手册
research/                 # 研究报告
threads/                  # X 发布队列与自动化
platform-registration/    # 开发者账号注册模板
skills/  scripts/  assets/
```

## 维护说明

- 本索引的链接均为仓库内相对路径，可用 `python3` 脚本校验无死链；新增文档后请同步在对应分类登记。
- 标注 draft / review-draft / proposed-not-applied / implementation-plan 的条目不代表已实施或已验收。
- 尚未撰写的 Radar 资讯稿、Argo CD 与 DevSecOps 基线章节不预建空文件，写好正文后再新增并登记。
