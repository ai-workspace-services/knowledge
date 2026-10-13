---
title: 桌面、远控、共享记忆与持久任务：工作空间开始像工作空间
description: 讨论桌面 App、WebRTC 远控、共享记忆和持久任务如何组成独立 Workspace 的基础能力。
slug: ai-workspace-desktop-remote-memory-persistent-tasks
lang: zh
date: 2026-10-13
status: review-draft
tags: [desktop, webrtc, memory, tasks, xworkmate]
category: ai-engineering
---

# 桌面、远控、共享记忆与持久任务：工作空间开始像工作空间

## 摘要

真正的工作空间必须能在 App 关闭、浏览器断开或执行主机暂时离线时继续表达任务状态。桌面入口、远程看屏、共享记忆和持久任务不是四个孤立卖点，而是同一条可靠性链上的不同环节。

## 真实问题

只把终端嵌进网页，仍然解决不了长任务。用户还需要知道谁在执行、执行到了哪一步、是否等待审批、失败能否重试、换一台 Workspace 后能否继续。把全部 transcript 上传到云端又会带来隐私、成本和权威性问题。

## 设计变化

规划中的职责分层是：XWorkmate App 做轻量交互、审批、进度和结果展示；WebRTC 做看屏、远程操作和人工接管，不承担队列或持久化；任务中心保存任务、会话、事件、审批、回执和补偿状态；执行器在可用 Workspace 中运行；记忆分为可重建热层、权威事实层和冷层原件。

这套分层允许 Mac、Home-Lab 或未来其他 profile 独立运行，而不把 Home-Lab 设为隐含单点。实例之间只同步经过授权的事件、版本、checkpoint 和 receipt/hash。异步同步的目标不是复制所有文件，而是让另一端知道任务事实和可继续的边界。

## 证据

桌面侧的 [XLaunch 设计](https://github.com/ai-desktop-lab/XLaunch/blob/main/docs/en/designs/2026-06-07-ai-workspace-desktop-design.md) 选择复用 XFCE、Plank 和 systemd；[WebRTC 抽离提交](https://github.com/ai-desktop-lab/xworkmate-remote-desktop/commit/9ce351c92e6ac8d0eb6c7266453087ba0286455d) 说明实时接管逐步分离。记忆侧有 [QMD memory bridge](https://github.com/ai-workspace-lab/qmd/commit/6b74f19fc3d38b1b64f9cdf5b34633ee5d57188f)、[共享 context](https://github.com/ai-workspace-lab/qmd/commit/819a5b68b36b3c22df23e3320f82146b5eeaf0a5) 和 [Accounts 任务状态](https://github.com/ai-workspace-services/accounts/commit/aed911975b7cda0d3211033f7569bf9e845368dd)。这些是源码证据，仍不等于跨实例 E2E。

## 尚未完成事项

必须测试 App/WebRTC 断开后的后台继续、重连恢复、重复和乱序事件、lease/心跳、单控制者租约、脱敏失败隔离、L1/L2/L3 写入及重建。测试通过也只说明指定版本和环境通过，不能外推成所有 Workspace 都可靠。

## 相关引用与导航

上一篇：[OpenClaw、Hermes 与 Bridge](02-openclaw-hermes-bridge.zh.md)。下一篇：[海外产品从 Chat 到 Agent Workspace](04-overseas-chat-to-agent-workspace.zh.md)。

相关背景：[白皮书规划](../../../../docs/reference/ai-workspace-agent-memory-whitepaper-plan.zh.md)、[记忆版本说明](../../../../docs/reference/ai-workspace-agent-memory-variants.zh.md)。
