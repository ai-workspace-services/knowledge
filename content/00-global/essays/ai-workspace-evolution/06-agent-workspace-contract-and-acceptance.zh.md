---
title: 最终 AgentWorkspace：职责、实施次序与验收
description: 给出 AgentWorkspace 的职责契约、分阶段实施顺序和从设计到真实端到端验收的证据门槛。
slug: ai-workspace-agent-contract-and-acceptance
lang: zh
date: 2026-10-13
status: review-draft
tags: [agent-workspace, bridge, dsh, memory, acceptance]
category: ai-engineering
---

# 最终 AgentWorkspace：职责、实施次序与验收

## 摘要

最终的 AgentWorkspace 不需要一个神秘的自治内核，而需要一份能被实现、测试和回滚的职责契约：App 负责用户，编排器负责任务，执行器负责工具，Gateway 负责模型，记忆层负责事实，Accounts 负责会话与审计。实施顺序必须从契约和证据开始，而不是从 UI 口号开始。

## 真实问题

“已支持 Agent”可能只意味着画了架构图，也可能意味着源码合并、单元测试通过，甚至真实端到端已完成。若不区分这些状态，团队会把规划当成能力，把一次成功 Demo 当成可靠系统。

## 最终职责

XWorkmate App 提交请求、展示进度并承接审批；Bridge 提供共享控制面或薄连接；DSH + plugins 统一编排；OpenCode 等是可替换执行器；Gateway 是可选模型连接器；Accounts/Session Center 保存任务、事件、审批和回执；QMD 是可重建热层，权威记忆和冷层由独立 ADR 决定。WebRTC 只负责实时媒体与人工接管，不持久化任务。

当前源码链可概括为 App → Bridge → Accounts 持久状态 → DSH 编排 → OpenCode/Codex/Claude Code/Grok Build；[aiw-orchestrator 说明](https://github.com/ai-workspace-lab/DeepSeek-Bot/blob/main/aiw-orchestrator/README.md) 是实现边界的重要记录。QMD 采用 precontext/postcandidate，不把模型结果自动升级为 `confirmedFact`。截至来源包记录，实际测试主要覆盖 DSH + fake ACP、Accounts、catalog 与 MCP，不能写成全链路成功；App 人工审批的状态与接口仍是后续工作。

## 实施次序

第一阶段登记仓库、版本、owner 和证据等级；第二阶段冻结任务、事件、取消、审批和 receipt 契约；第三阶段实现 Bridge 与编排器的最小闭环；第四阶段逐个接入执行器并跑同一基准；第五阶段加入记忆写入、脱敏、重建和跨实例同步；第六阶段再开放 UI 的更多模式与远程接管。

每一阶段都要有回滚点。不要因为某个模型或 CLI 暂时可用，就把它写死成唯一执行器；也不要因为 Gateway 能转发请求，就让它承担业务路由。

## 验收门槛

- 设计：职责、状态机、权限和失败路径有可审查文档。
- 源码合并：固定仓库和提交包含实现，且 owner 清楚。
- 单元测试：取消、拒绝、重复事件、幂等和错误分类有自动化覆盖。
- 真实 E2E：在指定版本、环境和目标上完成从请求到回执，并保留脱敏证据。
- 发布验收：明确批准人、兼容窗口、监控、回滚和未完成事项。

只有最后两项成立，才可以写“真实链路已验收”；前两项不能替代运行证据。

## 尚未完成事项

仍待确认 DSH 与各 CLI 的统一协议、记忆权威归属、跨实例授权和实际断线恢复。Agent OS 仍是工作环境/产品架构，不是已经完成的自研自治操作系统。

## 相关引用与导航

上一篇：[OpenCode、DeepSeek Harness 与 DS Bot](05-opencode-deepseek-harness.zh.md)。回到[系列目录](index.md)。

相关背景：[白皮书规划](../../../../docs/reference/ai-workspace-agent-memory-whitepaper-plan.zh.md)、[迁移验收契约](../../../../docs/reference/ai-workspace-agent-memory-variants.zh.md)。
