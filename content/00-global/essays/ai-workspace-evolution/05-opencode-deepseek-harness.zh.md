---
title: OpenCode、DeepSeek Harness 与 DS Bot：上游能力如何划边界
description: 讨论 OpenCode、DeepSeek Harness、DSH 与 DS Bot 在 AgentWorkspace 中的上游关系、适配边界和证据要求。
slug: ai-workspace-opencode-deepseek-harness
lang: zh
date: 2026-10-13
status: review-draft
tags: [opencode, deepseek, dsh, dsbot, executor]
category: ai-engineering
---

# OpenCode、DeepSeek Harness 与 DS Bot：上游能力如何划边界

## 摘要

OpenCode、DeepSeek Harness（DSH）和 DS Bot 不应被简单并列为三个“Agent”。更有用的做法是分别问：谁执行代码，谁编排任务，谁提供交互或插件能力，谁负责模型连接。只有边界稳定，OpenCode 和其他 CLI 才能成为可替换执行器。

## 真实问题

如果每个 CLI 都自带一套任务队列、模型路由和重试策略，Bridge 就会被迫维护多套语义。用户表面上得到更多选择，实际上很难判断取消是否生效、审批是否绕过、失败是否重复副作用。

## 设计变化

三套版本图给出的收敛方向是：A 阶段 Bridge 可直接选择多个执行器；B 阶段 DSH + plugins 接管任务编排、工具调用和任务级升级；C 阶段 DSH + plugins 成为唯一编排和角色策略入口，Bridge 只保留连接、会话映射、事件转发和审批回传。OpenCode、Codex CLI、Claude Code CLI 和 Grok Build CLI 则按能力被 DSH 派发。

DS Bot 在该结构中是 DSH 下的交互/委派插件，不应自行决定角色、重试或升级。AI 聚合网关也只是模型连接器，负责访问控制、用量和账本，不决定业务任务由哪个执行器完成。

## 证据与限制

上游边界可由 [OpenCode](https://github.com/anomalyco/opencode) 及其 [server](https://opencode.ai/docs/server/) 与[权限](https://opencode.ai/docs/permissions/)文档核对：它是独立编码 runtime，不是 DSH 代码上游。[DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) 的 [SAFETY.md](https://github.com/deepseek-ai/deepseek-harness/blob/master/SAFETY.md) 也提醒，实验工程不能自动视为生产审计结论。社区 [DeepSeek-Bot fork](https://github.com/ai-workspace-lab/DeepSeek-Bot) 是独立、非官方实现；NOTICE 所说的设计借鉴不等于包含 Hermes、OpenCode 或 Codex 的代码。DSH 的 [Codex adapter](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/subagent/subagent-codex/README.md) 也不等于完整 CLI 会话能力。

## 尚未完成事项

来源包记录 DSH 最新可见版本为 `0.2.1-alpha.2`，而 Bot 测试基线为 alpha.1，不能自动合并成同一基线。仍需用同一组任务比较补丁质量、工具执行、审批隔离、会话恢复、成本和失败补偿。

## 相关引用与导航

上一篇：[海外产品从 Chat 到 Agent Workspace](04-overseas-chat-to-agent-workspace.zh.md)。下一篇：[最终 AgentWorkspace：职责、实施次序与验收](06-agent-workspace-contract-and-acceptance.zh.md)。

相关背景：[三套架构版本图](../../../../docs/reference/ai-workspace-agent-memory-variants.zh.md)。
