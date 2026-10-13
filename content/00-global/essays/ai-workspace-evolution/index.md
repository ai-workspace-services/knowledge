---
title: AI Workspace 演变记录：从 Chat 到可验证的 Agent 工作空间
description: 以 XWorkmate、Bridge、OpenClaw、Hermes、OpenCode 与 DeepSeek Harness 为线索，记录 AI Workspace 的设计演变与验收边界。
slug: ai-workspace-evolution
lang: zh
date: 2026-10-13
status: review-draft
tags:
  - ai-workspace
  - agent
  - xworkmate
  - openclaw
  - opencode
category: ai-engineering
---

# AI Workspace 演变记录

这是一组工程复盘文章，讨论一个具体问题：怎样让 AI 从一次性 Chat 进入能够持续接收任务、使用工具、保留证据并在不同 Workspace 间异步协作的工作环境。

系列不把“Agent OS”写成已经完成的自治内核。这里的 Agent OS 只是工作环境与产品架构的称呼；真正的能力仍由 App、Bridge、编排器、执行器、模型连接器、记忆层和验收流程共同提供。

## 文章索引

1. [01：AI Workspace 为什么诞生：从产品入口到工作闭环](01-birth-and-timeline.zh.md)
2. [02：OpenClaw、Hermes 与 Bridge：从集成试错到职责收敛](02-openclaw-hermes-bridge.zh.md)
3. [03：桌面、远控、共享记忆与持久任务：工作空间开始像工作空间](03-desktop-remote-memory-tasks.zh.md)
4. [04：海外产品从 Chat 到 Agent Workspace 的形态变化](04-overseas-chat-to-agent-workspace.zh.md)
5. [05：OpenCode、DeepSeek Harness 与 DS Bot：上游能力如何划边界](05-opencode-deepseek-harness.zh.md)
6. [06：最终 AgentWorkspace：职责、实施次序与验收](06-agent-workspace-contract-and-acceptance.zh.md)

## 证据说明

本文系列当前以仓库内公开文档、设计记录和产品代码中的可见契约为基础。设计稿、源码存在、单元测试通过和真实端到端验收分别记账；没有精确提交、PR 或运行回执的结论，统一写成“设计目标”或“待核验”。

相关背景：[白皮书规划](../../../../docs/reference/ai-workspace-agent-memory-whitepaper-plan.zh.md)、[三套架构版本图](../../../../docs/reference/ai-workspace-agent-memory-variants.zh.md)、[多会话任务架构](../../../../docs/01-console/multi-session-tasks-architecture.md)。
