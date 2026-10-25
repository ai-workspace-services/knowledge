---
title: 参考资料总索引与 PDF 合订编排 / Reference index and PDF compilation plan
description:多云白皮书、总体架构、容灾、四仓契约、共用规范、数据库安全操作、三档权限、CMDB、AI Workspace、10 大核心服务 OrbStack 验证与性能调优规范及验收归档来源索引。
slug: index
lang: zh
tags:
  - docs
  - reference
  - multi-cloud
  - pdf
---

# 参考资料总索引与 PDF 合订编排

本页是参考资料的可编辑索引，服务于多云平台工程白皮书、总体架构评审和后续 PDF 合订准备。条目按主题分组，优先链接到本仓库真实文件；跨仓库条目使用固定 `origin/main` SHA 的 GitHub 链接，便于复核来源版本。实施规划条目不代表功能或运行验收已完成。

GitHub 组织入口：[ai-workspace-infra](https://github.com/ai-workspace-infra)。

## PDF 合订编排规则

### 中文主册

中文白皮书与总体架构正文按以下顺序作为主册：

1. [多云平台工程技术白皮书（中文）](multi-cloud-platform-engineering-whitepaper.zh.md)
2. [多云 Hybrid / Selfhost / Serverless 编排架构规划](../../content/02-iac-devops/cloud-infrastructure-devsecops-baseline/10-multi-cloud-orchestrator-architecture.zh.md)
3. [多云身份 Bootstrap 与状态契约](../../content/02-iac-devops/cloud-infrastructure-devsecops-baseline/11-cloud-oidc-bootstrap-contract.zh.md)
4. [Cloud OIDC Bootstrap：操作 TLDR](../../content/04-infra-platform/public-cloud-iaas/cloud-oidc-bootstrap-tldr.zh.md)
5. [平台操作中心与 Daily Snapshot 发布验收架构](../design/platform-operations-daily-snapshot.zh.md)

以上五项是主册正文，不以索引条目或链接清单替代正文。英文白皮书是独立版本，不重复夹入中文主册：[Multi-Cloud Platform Engineering Technical White Paper (English)](multi-cloud-platform-engineering-whitepaper.en.md)。

### 附录来源

混合部署与容灾指南、四仓契约、共用工程规范和专题索引作为附录来源。附录应保留原文标题、语言和来源版本；如果导出工具只支持链接快照，必须先把源文件纳入同一导出输入，再生成 PDF，不能把本页的链接打印结果宣称为完整正文。

### 当前导出能力

本仓库当前提供 Markdown 源文件、文档目录和内容服务/Portal 的渲染链路；本次核查未发现专用的 Markdown-to-PDF 脚本、Make 目标或已登记的 PDF 导出命令。因此，完整 PDF 导出方式仍是**待补能力**：需要在确定的导出环境中登记工具、字体、Mermaid/代码块处理和合订顺序后再执行。本文只准备源文件顺序和版本记录，不声称 PDF 已生成或已有可直接运行的导出命令。

## 部署形态专题归档

- [Proxy Server 三种部署形态与控制面边界](proxy-server-deployment-profiles.zh.md) · [English](proxy-server-deployment-profiles.en.md)：GitOps PR #428 原文归档，固定来源 `4c965e657441140c65ae50cfaa52b2c2647571f1`；仅文档归档，不改变主册基线或代表生产验收。

## 来源版本记录

- **knowledge**：本地工作树 `feat/ai-gateway-home-lab-practical-doc`，基线 `6765f91b39a3911298c41eb694159ad449710611`；本页及部分来源文件存在未提交本地修改，导出前需固定提交或快照。
- **platform-ops-toolkit**：`origin/main@14560c07dd6e57131ce5c34ac9996ee3c73ab86b`。
- **gitops**：`origin/main@f95197ef8e8078748f0b8471f9fe9aabd47cc0b7`。
- **iac_modules**：`origin/main@50ae2e67811cf54acedd47450f96dd02991be6b3`。
- **playbooks**：`origin/main@bde23b1f96668b850e1bcfaac1064bf029e6191a`。
- **xworkspace-core-skills**：`origin/main@0ece30c9aca907323b6bfbdf7d9995afe75d7916`。

## 一、白皮书与总体架构

| # | 标题 | 语言 | 来源版本 | 文件或入口 |
| ---: | --- | --- | --- | --- |
| 1 | 多云平台工程技术白皮书 | zh | knowledge working tree | [docs/reference/multi-cloud-platform-engineering-whitepaper.zh.md](multi-cloud-platform-engineering-whitepaper.zh.md) |
| 2 | Multi-Cloud Platform Engineering Technical White Paper | en | knowledge working tree | [docs/reference/multi-cloud-platform-engineering-whitepaper.en.md](multi-cloud-platform-engineering-whitepaper.en.md) |
| 3 | 多云 Hybrid / Selfhost / Serverless 编排架构规划 | zh | knowledge working tree | [content/.../10-multi-cloud-orchestrator-architecture.zh.md](../../content/02-iac-devops/cloud-infrastructure-devsecops-baseline/10-multi-cloud-orchestrator-architecture.zh.md) |
| 4 | 多云身份 Bootstrap 与状态契约 | zh | knowledge working tree | [content/.../11-cloud-oidc-bootstrap-contract.zh.md](../../content/02-iac-devops/cloud-infrastructure-devsecops-baseline/11-cloud-oidc-bootstrap-contract.zh.md) |
| 5 | Cloud OIDC Bootstrap：操作 TLDR | zh | knowledge working tree | [content/.../cloud-oidc-bootstrap-tldr.zh.md](../../content/04-infra-platform/public-cloud-iaas/cloud-oidc-bootstrap-tldr.zh.md) |
| 6 | 平台操作中心与 Daily Snapshot 发布验收架构 | zh | knowledge working tree | [docs/design/platform-operations-daily-snapshot.zh.md](../design/platform-operations-daily-snapshot.zh.md) |

## 二、混合部署、容灾与运行时

| # | 标题 | 语言 | 来源版本 | 文件或入口 |
| ---: | --- | --- | --- | --- |
| 7 | VPS + Serverless 混合部署极简成本架构规划与工程落地指南（含 7 章） | zh | knowledge working tree | [docs/zh/hybrid-serverless-architecture-vault-pipeline-plan/README.md](../zh/hybrid-serverless-architecture-vault-pipeline-plan/README.md) |
| 8 | 控制面混合云弹性容灾与零成本流量调度架构实践 | zh | knowledge working tree | [docs/zh/hybrid-serverless-architecture-and-zero-cost-failover.md](../zh/hybrid-serverless-architecture-and-zero-cost-failover.md) |
| 9 | 全栈三层立体容灾矩阵架构设计与工程落地 | zh | knowledge working tree | [docs/zh/full-stack-three-tier-fallback-matrix.md](../zh/full-stack-three-tier-fallback-matrix.md) |
| 10 | UAT Serverless 运行时拓扑、路由契约与全链路验证指南 | zh | knowledge working tree | [docs/zh/serverless-uat-runtime-topology-and-verification.md](../zh/serverless-uat-runtime-topology-and-verification.md) |
| 11 | Console Frontend Router 与 Edge Gateway 目标架构及实施计划 | zh | knowledge working tree | [docs/zh/frontend-edge-routing-target-architecture.md](../zh/frontend-edge-routing-target-architecture.md) |

## 三、四仓契约

| # | 标题 | 语言 | 来源版本 | 文件或入口 |
| ---: | --- | --- | --- | --- |
| 12 | Multi-cloud account contract | en | platform-ops-toolkit `origin/main@14560c07` | [platform-ops-toolkit/docs/iac/multi-cloud-account-contract.md](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/14560c07dd6e57131ce5c34ac9996ee3c73ab86b/docs/iac/multi-cloud-account-contract.md) |
| 13 | 统一多云 IaC State 契约 | zh | iac_modules `origin/main@50ae2e67` | [iac_modules/docs/howto/unified-iac-state-contract.md](https://github.com/ai-workspace-infra/iac_modules/blob/50ae2e67811cf54acedd47450f96dd02991be6b3/docs/howto/unified-iac-state-contract.md) |
| 14 | 多云多环境交付与发布规范 | zh | platform-ops-toolkit `origin/main@14560c07` | [platform-ops-toolkit/docs/standards/multi-environment-delivery-and-release-standard.md](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/14560c07dd6e57131ce5c34ac9996ee3c73ab86b/docs/standards/multi-environment-delivery-and-release-standard.md) |
| 15 | 环境数据操作：统一控制面与执行归属 | zh | platform-ops-toolkit `origin/main@14560c07` | [platform-ops-toolkit/docs/data_migration/environment-data-operations.md](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/14560c07dd6e57131ce5c34ac9996ee3c73ab86b/docs/data_migration/environment-data-operations.md) |
| 16 | 独立 UAT / PROD 升级流水线 | zh | platform-ops-toolkit `origin/main@14560c07` | [platform-ops-toolkit/docs/data_migration/environment-upgrade.md](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/14560c07dd6e57131ce5c34ac9996ee3c73ab86b/docs/data_migration/environment-upgrade.md) |
| 17 | 执行职责迁移交接快照（2026-10-05） | zh | platform-ops-toolkit `origin/main@14560c07` | [platform-ops-toolkit/docs/agent/2026-10-05-ownership-migration-handoff.md](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/14560c07dd6e57131ce5c34ac9996ee3c73ab86b/docs/agent/2026-10-05-ownership-migration-handoff.md) |
| 18 | Cloud-Neutral Toolkit GitOps | en | gitops `origin/main@f95197ef` | [gitops/README.md](https://github.com/ai-workspace-infra/gitops/blob/f95197ef8e8078748f0b8471f9fe9aabd47cc0b7/README.md) |
| 19 | scripts/pipeline | en | iac_modules `origin/main@50ae2e67` | [iac_modules/scripts/pipeline/README.md](https://github.com/ai-workspace-infra/iac_modules/blob/50ae2e67811cf54acedd47450f96dd02991be6b3/scripts/pipeline/README.md) |
| 20 | scripts/pipeline | en | playbooks `origin/main@bde23b1f` | [playbooks/scripts/pipeline/README.md](https://github.com/ai-workspace-infra/playbooks/blob/bde23b1f96668b850e1bcfaac1064bf029e6191a/scripts/pipeline/README.md) |
| 21 | Vault authorization declarations | en | platform-ops-toolkit `origin/main@14560c07` | [platform-ops-toolkit/scripts/vault/README.md](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/14560c07dd6e57131ce5c34ac9996ee3c73ab86b/scripts/vault/README.md) |
| 22 | Vault KV v2 contract | en | gitops `origin/main@f95197ef` | [gitops/docs/vault-kv-paths.md](https://github.com/ai-workspace-infra/gitops/blob/f95197ef8e8078748f0b8471f9fe9aabd47cc0b7/docs/vault-kv-paths.md) |

## 四、共用工程规范

| # | 标题 | 语言 | 来源版本 | 文件或入口 |
| ---: | --- | --- | --- | --- |
| 23 | Project Development Standard | en | xworkspace-core-skills `origin/main@0ece30c9` | [skills/engineering-standards/project-development-standard/SKILL.md](https://github.com/ai-workspace-lab/xworkspace-core-skills/blob/0ece30c9aca907323b6bfbdf7d9995afe75d7916/skills/engineering-standards/project-development-standard/SKILL.md) |
| 24 | Multi-Environment Delivery and Release Standard | en | xworkspace-core-skills `origin/main@0ece30c9` | [skills/engineering-standards/multi-environment-delivery-and-release/SKILL.md](https://github.com/ai-workspace-lab/xworkspace-core-skills/blob/0ece30c9aca907323b6bfbdf7d9995afe75d7916/skills/engineering-standards/multi-environment-delivery-and-release/SKILL.md) |
| 25 | Infrastructure-as-Code (IAC) 规范指南 | zh/en | xworkspace-core-skills `origin/main@0ece30c9` | [skills/engineering-standards/infrastructure-as-code-spec/SKILL.md](https://github.com/ai-workspace-lab/xworkspace-core-skills/blob/0ece30c9aca907323b6bfbdf7d9995afe75d7916/skills/engineering-standards/infrastructure-as-code-spec/SKILL.md) |
| 26 | Config-as-Code (Playbooks) Specification | en | xworkspace-core-skills `origin/main@0ece30c9` | [skills/engineering-standards/config-as-code-spec/SKILL.md](https://github.com/ai-workspace-lab/xworkspace-core-skills/blob/0ece30c9aca907323b6bfbdf7d9995afe75d7916/skills/engineering-standards/config-as-code-spec/SKILL.md) |
| 27 | Execution ownership migration | en | xworkspace-core-skills `origin/main@0ece30c9` | [skills/engineering-standards/execution-ownership-migration/SKILL.md](https://github.com/ai-workspace-lab/xworkspace-core-skills/blob/0ece30c9aca907323b6bfbdf7d9995afe75d7916/skills/engineering-standards/execution-ownership-migration/SKILL.md) |
| 28 | GitOps Canonical Resource Delivery | en | xworkspace-core-skills `origin/main@0ece30c9` | [skills/engineering-standards/gitops-canonical-resource-delivery/SKILL.md](https://github.com/ai-workspace-lab/xworkspace-core-skills/blob/0ece30c9aca907323b6bfbdf7d9995afe75d7916/skills/engineering-standards/gitops-canonical-resource-delivery/SKILL.md) |
| 29 | CI/CD Workflow Specification | en | xworkspace-core-skills `origin/main@0ece30c9` | [skills/engineering-standards/ci-cd-workflow-spec/SKILL.md](https://github.com/ai-workspace-lab/xworkspace-core-skills/blob/0ece30c9aca907323b6bfbdf7d9995afe75d7916/skills/engineering-standards/ci-cd-workflow-spec/SKILL.md) |
| 30 | Zero-Trust Overlay Delivery Standard | en | xworkspace-core-skills `origin/main@0ece30c9` | [skills/engineering-standards/zero-trust-overlay-delivery/SKILL.md](https://github.com/ai-workspace-lab/xworkspace-core-skills/blob/0ece30c9aca907323b6bfbdf7d9995afe75d7916/skills/engineering-standards/zero-trust-overlay-delivery/SKILL.md) |

## 五、专题索引

| # | 标题 | 语言 | 来源版本 | 文件或入口 |
| ---: | --- | --- | --- | --- |
| 31 | 撕破云厂高墙：把割裂的异构云拧成一股绳 | zh | knowledge working tree | [why-i-built-multi-cloud-iac-mesh-cn.md](../../why-i-built-multi-cloud-iac-mesh-cn.md) |
| 32 | Global Mesh 产品介绍与云中立现代架构深度白皮书 | zh | knowledge working tree | [docs/zh/products-global-mesh.md](../zh/products-global-mesh.md) |
| 33 | cloud-infrastructure-devsecops-baseline 目录 | mixed | knowledge working tree | [content/02-iac-devops/cloud-infrastructure-devsecops-baseline/](../../content/02-iac-devops/cloud-infrastructure-devsecops-baseline/) |
| 34 | 02-iac-devops 目录 | mixed | knowledge working tree | [content/02-iac-devops/](../../content/02-iac-devops/) |

## 六、数据库与安全操作

| # | 标题 | 语言 | 来源版本 | 文件或入口 |
| ---: | --- | --- | --- | --- |
| 35 | Supabase 操作参考：专用只读角色、RLS 与受控连接 | zh | knowledge working tree | [docs/reference/supabase-operations.zh.md](supabase-operations.zh.md) |
| 36 | Supabase Operations Reference: Dedicated Read-only Role, RLS, and Controlled Connections | en | knowledge working tree | [docs/reference/supabase-operations.en.md](supabase-operations.en.md) |
| 37 | Platform Ops Toolkit Daily Main Snapshot 实施规划 | zh | knowledge working tree | [docs/reference/platform-ops-toolkit-daily-main-snapshot-plan.zh.md](platform-ops-toolkit-daily-main-snapshot-plan.zh.md) |
| 38 | 多云与 Serverless 动态 CMDB：独立 PostgreSQL 与 Grafana 落地规划 | zh | knowledge working tree · implementation-plan | [docs/reference/multi-cloud-cmdb-postgresql-grafana-plan.zh.md](multi-cloud-cmdb-postgresql-grafana-plan.zh.md) |
| 39 | 多云资源三档权限、IAM 与 Vault 安全集成及 Shared CMDB 技术规范白皮书 | zh | knowledge working tree · v1.2 · 云账号/OS/自建服务三层权限补充 · proposed-not-applied | [docs/reference/multi-cloud-iam-vault-cmdb-security-whitepaper.zh.md](multi-cloud-iam-vault-cmdb-security-whitepaper.zh.md) |

## 七、AI Workspace、执行器与记忆

| # | 标题 | 语言 | 来源版本 | 文件或入口 |
| ---: | --- | --- | --- | --- |
| 40 | AI Workspace、XWorkmate 多执行器与三级记忆技术白皮书规划（含独立 macOS / Home-Lab Workspace profiles） | zh | knowledge working tree · review-draft · proposed-not-applied | [docs/reference/ai-workspace-agent-memory-whitepaper-plan.zh.md](ai-workspace-agent-memory-whitepaper-plan.zh.md) |
| 41 | AI Workspace 三套架构版本图与迁移验收索引 | zh | knowledge working tree · review-draft · A historical / B transition / C target-pending | [docs/reference/ai-workspace-agent-memory-variants.zh.md](ai-workspace-agent-memory-variants.zh.md) |
| 42 | QMD + PG + 云盘三级任务聚合与记忆系统落地规范 | zh | knowledge working tree · v1.0-release · approved | [docs/reference/qmd-pg-cloud-drive-three-tier-memory-spec.zh.md](qmd-pg-cloud-drive-three-tier-memory-spec.zh.md) |

## 八、性能调优与容量规划

| # | 标题 | 语言 | 来源版本 | 文件或入口 |
| ---: | --- | --- | --- | --- |
| 43 | XWorkTech 性能调优技术白皮书与工程规范 | zh | knowledge working tree · v1.0 · review-draft · 未执行环境变更或运行验收 | [docs/reference/performance-optimization-whitepaper.zh.md](performance-optimization-whitepaper.zh.md) |
| 43 | jp-xconnect 内存与日志优化分析报告（2026-10-10） | zh | knowledge working tree · reported-results-pending-follow-up | [docs/performance-optimization/jp-xconnect-memory-log-optimization-20261010.zh.md](../performance-optimization/jp-xconnect-memory-log-optimization-20261010.zh.md) |
| 44 | JP XConnect 稳定性增量配置验证报告（2026-10-14） | zh | knowledge working tree · v0.1 · prod-partial-validated | [docs/reference/performance-optimization-jp-xconnect-stability-20261014.zh.md](performance-optimization-jp-xconnect-stability-20261014.zh.md) |
| 45 | XConnect Free 节点大文件上传实测与优化验收（2026-10-18） | zh | knowledge working tree · v1.1 · partial-acceptance · Linux 58/60 & MacOS 27/60 | [docs/performance-optimization/xconnect-free-proxy-upload-acceptance-20261018.zh.md](../performance-optimization/xconnect-free-proxy-upload-acceptance-20261018.zh.md) |

### 全链路网络性能与双链路可观测性专题（2026-10-23）

| 文档 | 用途 | 状态 |
| --- | --- | --- |
| [客户端与代理节点深化实施规划](dual-link-client-edge-observability-implementation-plan.zh.md) | 工具选型、采集契约、任务与验收 | 规划，未部署 |
| [双链路实施与交付交接手册](dual-link-observability-handoff-handbook-20261023.md) | 交付基准、历史回执、PR 进展及校正 | 历史证据与规划分开记录 |
| [全链路网络性能分析白皮书](network-full-path-performance-whitepaper.zh.md) | TCP/TLS、双端重传、吞吐与 L4/L7 方法 | 诊断参考 |
| [JP 双入口诊断实测记录](network-performance-jp-comparison-20261023.zh.md) | TUN、DNS、TLS 与 mtr 数据及根因边界 | 有限样本，根因未确认 |

## 九、平台工程单机验证与本地基座

| # | 标题 | 语言 | 来源版本 | 文件或入口 |
| ---: | --- | --- | --- | --- |
| 46 | 11 大核心服务类别 macOS OrbStack 单机部署与健康验收矩阵 | zh | knowledge working tree · v1.1-release · approved | [docs/reference/platform-core-services-orbstack-acceptance-matrix.zh.md](platform-core-services-orbstack-acceptance-matrix.zh.md) |

## 使用与维护约束

- 本索引记录的是来源入口，不改变各仓库的架构结论、权限边界或部署授权。
- 导出前应重新核对固定 SHA、语言版本、图片/代码块/Mermaid 支持和章节顺序；未提交工作树不得直接作为已发布版本声明。
- 目录条目是导航，不等于已经把目录下所有文件纳入 PDF；若要合订完整附录，必须明确附录文件清单并将其加入导出输入。
- 不把不存在的文件、未验证的命令、凭据、内网地址或本机绝对路径写入公开索引。
