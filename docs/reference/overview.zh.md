---
title: 参考资料总览
description: 用于维护 docs 源树的结构与运维参考页。
slug: overview
lang: zh
tags:
  - docs
  - reference
---

# 参考资料总览

参考页用于保证这套文档系统可维护：包括规范、覆盖跟踪与历史文档映射。

## 平台工程白皮书

[多云平台工程技术白皮书](multi-cloud-platform-engineering-whitepaper.zh.md)完整整理四仓职责、40 个 workflow、GitOps/state/CMDB、Vault 路径与权限、升级验收和迁移路线，固定基线为 2026-10-05，并明确区分已实现、规划目标及待验收事项。

## Proxy Server 部署形态归档（2026-10-25）

[Proxy Server 三种部署形态与控制面边界](proxy-server-deployment-profiles.zh.md)记录 GitOps PR #428 的三种部署形态、声明与控制面边界及固定原文来源。此项是文档归档补充，不改变本白皮书原有源码基线，也不代表运行验收。

## 性能调优与容量规划

[XWorkTech 性能调优技术白皮书与工程规范](performance-optimization-whitepaper.zh.md)定义 Open Platform、XConnect、XWorkmate 与 AI Workspace 的观测、诊断、优化、验证和容量规划流程，包含指标契约、证据分类、变更与回滚边界、成本评估及九节诊断报告模板。当前为 v1.0 规范评审稿，不代表实际环境已完成调优或验收。

实测与阶段性验收归档见 [性能优化归档](../performance-optimization/README.md)，包含：
- [jp-xconnect 内存与日志优化分析报告（2026-10-10）](../performance-optimization/jp-xconnect-memory-log-optimization-20261010.zh.md)
- [JP XConnect 稳定性增量配置验证报告（2026-10-14）](performance-optimization-jp-xconnect-stability-20261014.zh.md)
- [XConnect Free 节点大文件上传实测与优化验收（2026-10-18）](../performance-optimization/xconnect-free-proxy-upload-acceptance-20261018.zh.md)

## 平台工程单机验证与本地基座

[11 大核心服务类别 macOS OrbStack 单机部署与健康验收矩阵](platform-core-services-orbstack-acceptance-matrix.zh.md)规范了在 macOS 本机 OrbStack 环境下，对 Git/CI、Harbor 制品管理、Silo S3 存储、CMDB 动态清单、全栈可观测性与遥测中枢、Vault/Zitadel 身份中枢、Doco CD GitOps、K3s 容器与 pgvector 向量底座、PG 灾备演练、New API + LiteLLM AI 网关及 MCP Server 守护网关这 11 大类别的 Compose 单机拓扑编组、非冲突回环端口分配及自动化健康探测验收标准。

## 可观测性、CMDB 与基础设施 MCP 网关

[Infrastructure-MCP-Server 部署、集中式可观测性、CMDB 与 QMD 记忆系统交付全景技术规范](infrastructure-mcp-observability-cmdb-qmd-delivery-spec.zh.md)规范了基于 Go 原生开发部署的本机只读 MCP 网关，对接 `observability.svc.plus` 4-MCP 适配器、SIT/UAT/PROD 多云 CMDB 资源动态对账、Environment Graph 15 条依赖拓扑图、安全受控只读 Cloud CLI 工具调用及 QMD 知识库每日自动增量向量化同步机制。

## 相关引用

- [参考资料总索引与 PDF 合订编排](index.md)
- [Platform Ops Toolkit 运维体系参考文档汇编（183 份多云平台工程与运维全景索引）](platform-ops-toolkit/README.md)
- [11 大核心服务类别 macOS OrbStack 单机部署与健康验收矩阵](platform-core-services-orbstack-acceptance-matrix.zh.md)
- [多云平台工程技术白皮书——英文版](multi-cloud-platform-engineering-whitepaper.en.md)
- [Toolkit Daily Main Snapshot 实施规划与表格审计](platform-ops-toolkit-daily-main-snapshot-plan.zh.md)
- [内容规范](content-schema.zh.md)
- [覆盖矩阵](coverage-matrix.zh.md)
- [历史文档映射](legacy-docs.zh.md)
- [信息架构](../core-concepts/information-architecture.zh.md)
