---
title: OpenClaw、Hermes 与 Bridge：从集成试错到职责收敛
description: 复盘 OpenClaw、Hermes 和 Bridge 在 AI Workspace 中的连接位置、试错路径与职责边界。
slug: ai-workspace-openclaw-hermes-bridge
lang: zh
date: 2026-10-13
status: review-draft
tags: [openclaw, hermes, bridge, xworkmate, agent]
category: ai-engineering
---

# OpenClaw、Hermes 与 Bridge：从集成试错到职责收敛

## 摘要

OpenClaw、Hermes、Bridge 看起来都可能成为“AI 助手入口”，但它们解决的不是同一个问题。复盘它们的组合，最重要的收获不是挑出一个赢家，而是确认连接、唤醒、任务编排、模型访问和执行必须分账。

## 真实问题

当一个助手既要响应聊天，又要在后台跑任务，还要接受桌面或远程控制时，很容易出现第二套队列、第二套重试和第二个路由器。这样做短期能让 Demo 连起来，长期却让取消、审批、失败补偿和状态回放变得不可解释。

## 设计变化

在目标结构中，OpenClaw 更适合作为渠道、唤醒或兼容连接器，而不是全局角色路由器；Hermes 的具体上游能力和接口需要以公开源码与版本核验，不能因为名字相近就推断其承担任务编排。Bridge 的位置也经历了收敛：历史设计中它可能直接选择并派发多个执行器；过渡设计中它更多负责连接、会话映射、事件转发和审批回传；精简目标则要求它保持薄，避免重新规划、重试或升级。

这种收敛让“谁拥有状态”变得清楚：编排器拥有任务生命周期，执行器拥有工具调用，Bridge 传递规范化事件，Gateway 只连接模型。OpenClaw 或 Hermes 即使提供很好的交互体验，也不应因此获得全局权限。

## 证据与判断

可核验的 [Hermes ACP 提交](https://github.com/ai-workspace-lab/xworkmate-bridge/commit/1e6c644a92f9895d4b9cb9d29e8ea22b9ac1aab9) 与 [OpenClaw 多会话插件提交](https://github.com/ai-workspace-lab/openclaw-multi-session-plugins/commit/529965aa3b65dcfce0996e2ed1381a4e0845a0b5) 支持“并行试错”。Bridge 的[角色选择 ADR](https://github.com/ai-workspace-lab/xworkmate-bridge/blob/1394d927b579eb745f2b7d35ad5d9d466ebbca44/docs/architecture/adr-v2.1-role-selection-in-dsh.md) 则把方向收敛到 DSH 编排；这些证据不代表所有 provider 已接通。

## 尚未完成事项

需要核对 OpenClaw、Hermes 的上游仓库、版本、协议、工具权限、取消语义和会话恢复；还要验证 Bridge 在断线、重复事件和审批拒绝时是否只做传递而不偷偷改变任务语义。

## 相关引用与导航

上一篇：[AI Workspace 为什么诞生](01-birth-and-timeline.zh.md)。下一篇：[桌面、远控、共享记忆与持久任务](03-desktop-remote-memory-tasks.zh.md)。

相关背景：[架构版本图](../../../../docs/reference/ai-workspace-agent-memory-variants.zh.md)、[Console Web 架构](../../../../docs/01-console/architecture/web-console/overview.md)。
