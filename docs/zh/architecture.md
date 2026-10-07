# 架构

该仓库以内容资产为主，文档重点是内容结构、发布流程与知识组织方式。

本页作为系统边界、核心组件与仓库职责的双语总览入口。

## 架构设计篇

- [平台操作中心与 Daily Snapshot 发布验收架构](../design/platform-operations-daily-snapshot.zh.md)：Operations 全量参数、发布计划、父子工作流同步与 Releases 验收证据；目标设计，尚未实现。

## 与当前代码对齐的说明

- 文档目标仓库: `knowledge`
- 仓库类型: `content`
- 构建与运行依据: repository structure and scripts only
- 主要实现与运维目录: `scripts/`, `content/`
- `package.json` 脚本快照: No package.json scripts were detected.

## 需要继续归并的现有文档

- `04-postgresql/ARCHITECTURE.md`
- `04-postgresql/PROJECT_STRUCTURE.md`
- `04-postgresql/overview.md`

## 本页下一步应补充的内容

- 先描述当前已落地实现，再补充未来规划，避免只写愿景不写现状。
- 术语需要与仓库根 README、构建清单和实际目录保持一致。
- 将上方列出的历史 runbook、spec、子系统说明逐步链接并归并到本页。
- 随着目录结构、服务关系和集成依赖变化，持续同步图示与职责说明。
