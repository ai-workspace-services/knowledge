---
title: 再也不用多账号切换了：手把手教你搭建个人专属全能 AI 聚合网关（一）—— 选型篇：告别割裂，个人网关与 Kong/APISIX 深度抉择
description: 面向个人与小团队的 AI 聚合网关选型全景剖析，深度对比 Kong 与 APISIX Standalone 在 GitOps、控制面依赖、AI 插件生态与运维复杂度上的权衡考量。
slug: ai-aggregator-gateway-01-selection
lang: zh
date: 2026-10-01T00:00:00Z
author: shenlan
tags:
  - ai-gateway
  - apisix
  - kong
  - home-lab
  - architecture
category: essays
---

# 再也不用多账号切换了：手把手教你搭建个人专属全能 AI 聚合网关（一）

> **导读**：在各类 AI 辅助工具井喷的今天，开发者每天都在多个订阅账号、API Key、不同的 Base URL 和异构的协议端点之间来回切换。本文作为“全能 AI 聚合网关”实战系列的开篇，将深入剖析这套架构的产生背景、核心组件分工，以及在 API 网关选型中为何最终选择 Apache APISIX Standalone 而非 Kong。

![AI 聚合网关选型与多账号聚合](/assets/images/gateway-01-selection-cover.jpg)

---

## 一、痛点：被撕裂的 AI 生产力

随着 AI 编程与 Agent 生态的快速演进，工程师日常打交道的工具链已经极度碎片化：
* **命令行终端**：活跃着 Codex CLI、Claude Code、Google Gemini CLI 等常驻开发 Agent；
* **IDE 与编辑器**：配置着 Google Antigravity、Android Studio、Cursor、VS Code 插件；
* **业务开发与自动化**：用 Python / Node.js 官方 SDK 编写各类大模型工作流；
* **账号与资源体系**：手握多个 ChatGPT Plus/Pro 订阅账号、Claude Team 订阅、Google 账号，外加若干按量计费的官方 OpenAI、Anthropic、xAI 商业 API Key。

日常使用中，这种“多源并存”带来了巨大的摩擦力：
1. **认证与地址碎片化**：不同工具对 Base URL、Header 命名（`Authorization` vs `x-api-key`）、模型参数命名规范要求各异；
2. **账号利用率极不均衡**：有的订阅账号在月底额度闲置浪费，有的账号却频繁触发小时级或周级速率限制；
3. **缺乏故障容灾与平滑降级**：当某一订阅渠道出现网络抖动或上游风控封锁时，终端工具往往直接崩溃报错，缺乏透明重试与自动切换机制。

我们的目标非常明确：**在 Home-Lab 或小团队私有环境中，搭建一套统一的 AI 聚合网关（AI Aggregator Gateway）。对外暴露单一 HTTPS 域名、单一标准化 Token，向上兼容主流大模型协议，向下聚合个人订阅账号与商业按量 API，实现智能路由、负载均衡与安全隔离。**

---

## 二、总体架构与核心组件分工

为了兼顾轻量化、高可靠与后续扩展性，我们摒弃了把所有功能强行揉入单个单体程序的做法，采用分层解耦的组件矩阵：

| 核心组件 | 承担职责 | 运行形态与存储依赖 |
| :--- | :--- | :--- |
| **Caddy** | 边缘 TLS 终止、域名证书生命周期管理、端口反向代理 | systemd 原生服务，静态配置 |
| **APISIX** | 统一入口鉴权、IP 白名单、多租户 ACL、动态限流、审计分流 | Standalone 文件模式，systemd，无 etcd/DB 依赖 |
| **New API** | 统一模型目录聚合、Model Alias 映射、CPA 渠道负载均衡与健康探活 | systemd 服务，PostgreSQL 数据库 |
| **LiteLLM** | 官方按量 API（OpenAI / Anthropic / xAI）适配、Retry、用量与成本核算 | systemd 服务，独立 PostgreSQL 库 |
| **CLIProxyAPI (CPA)** | 单账号 OAuth 订阅转换、本地协议兼容适配（OpenAI/Claude 等） | 多实例矩阵，每实例独立 Linux 用户与 systemd unit |
| **Vault** | 数据库连接串（DSN）、网关凭据、官方 Provider API Key 安全托管 | 部署编排时读取，运行时注入内存 tmpfs |

### 核心分工原则

在这套拓扑中，**LiteLLM 与 New API 是平级上游**。
* **New API** 负责聚合多账号矩阵（CPA Channels），通过 Model Alias 机制为上游提供统一模型名称映射；
* **LiteLLM** 负责对接外部各大商用官方按量 API，处理复杂的厂商错误重试与 Token 成本记账。
* **坚决杜绝让 LiteLLM 作为 CPA 的前置代理**，避免引入双重重试风暴、用量重复统计与链路耗时增加。

---

## 三、网关选型深度权衡：Kong vs APISIX

作为整个系统的流量守门人，网关层的稳定性至关重要。业内最常被对比的是 Kong 和 Apache APISIX。在此次实践中，我们选择 APISIX Standalone，主要依据是**声明式 GitOps 契约、无数据库依赖、以及开源多模型调度探索**：

| 对比维度 | Kong | Apache APISIX | 本项目实战决策依据 |
| :--- | :--- | :--- | :--- |
| **配置存储后端** | Traditional 模式依赖 PostgreSQL；DB-less 模式加载 YAML/JSON | 传统集群模式依赖 etcd；**Standalone 模式直接加载本地 `apisix.yaml`** | 本项目推行 **GitOps 文件驱动与部署对账**。APISIX Standalone 彻底免除了控制面数据库与 etcd 依赖，架构极简。 |
| **PostgreSQL 依赖** | 原生深度支持 Traditional 配置存储，由 decK 或 Admin API 管理 | 不是原生控制面配置存储库 | 若强依赖关系型数据库管理动态路由实体，Kong 是首选；但对于文件驱动场景，无库更清爽。 |
| **通用网关能力** | 强大的认证、ACL、路由重写、限流与成熟的插件体系 | Consumer 权限、路由组、插件链路、多租户 ACL | 两者通用能力高度相当，均能出色完成流量安全防线与流控职责。 |
| **AI 代理能力** | 提供基础 `ai-proxy`；多模型调度与成本控制为 `ai-proxy-advanced` | 开源生态提供 `ai-proxy` 与 `ai-proxy-multi` | 两者均具备 AI 适配能力，但 Kong 的高级特性存在商业 License 边界；APISIX 的 `ai-proxy-multi` 属于自由开源插件。 |
| **动态租户维护** | Traditional 模式通过受控 Admin API 实时更新网关实体 | Standalone 模式通过重新渲染并下发完整 YAML 声明对账 | 个人与小团队场景完全可接受声明式对账与 Reload，不需要高频热更新控制面。 |
| **多节点限流状态** | 依赖插件配置策略及外部集中式存储（如 Redis） | 当前 `limit-count` 采用 local 模式单节点内存计数 | 本阶段 Home-Lab 单机性能充裕；横向扩展多节点时再引入共享 Redis 配额。 |
| **运维复杂度** | Traditional 增加网关 DB、Migration 及备份心智负担 | Standalone 彻底砍掉控制面组件，仅需管理文本配置文件 | 依赖组件越少，系统的平均无故障时间（MTBF）越长。 |

---

## 四、选型代价与实战边界保留

选用 APISIX Standalone 带来了极简的运维体验，但也伴随着明确的技术约束与实操代价：

1. **运行时环境强绑定与版本固化**：当前网关运行在固定的 APISIX 3.16.0 源码与独立 OpenResty Runtime 之上。在初期落地中，曾踩过动态链接库缺失、共享内存字典（Shared Dict）未初始化、worker 进程读取配置文件权限不足等坑。因此，必须将所有的编译参数、依赖组合和权限规范完全沉淀在 Ansible Role 中，切忌通过最新镜像进行黑盒盲测。
2. **放弃动态 REST 控制面**：Standalone 模式意味着无法通过 HTTP API 动态下发单个路由。所有的路由扩容、租户增删、限流调优必须遵循 GitOps 流水线：修改声明文件 → 渲染生成 `apisix.yaml` → 触发服务 Reload。
3. **架构排他性约束**：早期部署的 Kong 实例已在系统中被全面禁用并停用（Disabled），禁止在同一入口机器上同时监听处理相同流量，避免路由语义冲突与排障困扰。

---

## 五、小结

选型的本质是在**业务规模、开发维护成本与系统控制力**之间寻找最优平衡点。通过采用 Caddy + APISIX Standalone + New API + LiteLLM + CPA 的组合，我们成功构建了一个既支持声明式交付，又完全摒弃了冗余控制面数据库的现代化网关底座。

在下一篇中，我们将深入网关的核心内部，全面剖析流量的分流细节与安全鉴权解耦：
**《再也不用多账号切换了：手把手教你搭建个人专属全能 AI 聚合网关（二）—— 架构篇：双层分流与安全契约，从 Caddy 到 APISIX 的流量中枢设计》**。

---

## 六、多平台发布矩阵适配（微信公众号 / 小红书 / X）

### 1. 微信公众号 & 朋友圈文案

> **标题备选**：
> 1. 再也不用多账号切换了：手把手教你搭建个人专属全能 AI 聚合网关（选型篇）
> 2. 别再手动切 Token 了！我用 APISIX + Caddy 撸了一套全能 AI 聚合网关
> 3. 为什么做个人 AI 网关，我选了 APISIX Standalone 而彻底放弃 Kong？

**推文导语与摘要**：
一边是 Codex、Claude Code、Gemini CLI，另一边是 ChatGPT Plus、Claude Team 和一堆按量付费的官方 Key……每次写代码都要在各种环境变量和反代端口里疲于奔命？这篇硬核实战带你搞懂个人专属 AI 聚合网关的架构选型全景，手把手拆解为什么 APISIX Standalone 才是适合 GitOps 声明式对账的极简解法。

**朋友圈转发文案**：
手里攥着 4 个大模型订阅账号和 3 家官方 API Key，每次配置各种 CLI 和 IDE 都像打仗一样切环境变量……
花了几天时间把整个链路彻底重构了：
Caddy (TLS) + APISIX Standalone (鉴权/限流) + New API (模型目录) + LiteLLM (官方兜底) + CPA (单账号矩阵)。
彻底摆脱 etcd 和数据库控制面依赖，直接 GitOps 声明式对账！
第一篇先把“为什么选 APISIX 而不是 Kong”的底层逻辑和踩坑代价讲透，欢迎技术同好交流拍砖！👇

---

### 2. 小红书爆款图文文案

**笔记封面大字**：
🔥 告别多账号切换！
💻 个人专属全能 AI 聚合网关搭建指南
⚡ 选型篇：Kong vs APISIX 深度权衡

**正文内容**：
救命！谁懂每天在不同 AI 工具里来回切账号的痛苦啊😭😭
终端跑着 Claude Code、Codex CLI；
IDE 挂着 Antigravity、Android Studio；
脚本里还调着官方 OpenAI 和 Anthropic 的按量 Key……
经常这个账号限流了，那个账号快到期了额度还没用完！

受够了碎片化的配置，我花时间在自己的 Home-Lab 里搭了一套全能 AI 聚合网关：
✅ 统一域名：所有工具只认一个 Base URL！
✅ 统一 Token：一个网关 Key 跑通所有工具！
✅ 智能聚合：既能跑 ChatGPT Plus/Claude 订阅，又能跑官方商业 API！

今天第一篇先聊最硬核的【网关选型】：
为什么我选了 **APISIX Standalone**，而彻底禁用了 Kong？
💡 传统网关都要连 PostgreSQL 或 etcd，维护太重；
💡 APISIX 的 Standalone 模式直接读一个 `apisix.yaml`，纯纯的 GitOps 文件驱动；
💡 开源自带 `ai-proxy-multi`，多模型调度完全自由，不需要商业 License！

实测代码与避坑指南已整理好，下期讲《双层流量中枢与安全分流》，建议收藏关注防走丢～✨

🏷️ #AI工具 #程序员生产力 #HomeLab #大模型 #技术架构 #APISIX #ClaudeCode #后端日常

---

### 3. X (Twitter) Thread / 文章

**Tweet 1 (Hook)**:
Tired of constantly switching between ChatGPT Plus, Claude Team subscriptions, and official API keys across different CLIs and IDEs? 

I built a self-hosted, all-in-one AI Aggregator Gateway in my Home-Lab.

Here is Part 1 of the architecture blueprint: Why APISIX Standalone won over Kong 🧵👇

**Tweet 2 (The Multi-Account Pain)**:
If you run Codex CLI, Claude Code, and Gemini CLI side by side:
- Authentication headers diverge (`Authorization` vs `x-api-key`).
- Quotas are imbalanced across subscription tiers.
- A single upstream rate limit crashes your local coding agents.

The fix? A unified gateway exposing a single HTTPS endpoint and one token.

**Tweet 3 (The Gateway Battle: Kong vs APISIX)**:
Why APISIX Standalone?
1. Zero DB / etcd dependency: Reads local YAML directly for GitOps reconciliation.
2. Open-source `ai-proxy-multi` plugin: No enterprise license traps for multi-model routing.
3. Minimal operational footprint: Less moving parts = fewer runtime crashes in Home-Lab.

**Tweet 4 (The Caveats)**:
No architecture is free lunch:
- Requires strict OpenResty runtime & Lua lib pinning (APISIX 3.16.0).
- Surrenders dynamic REST Admin API for pure GitOps declarations.
- Mutual exclusivity: Disabled Kong completely to avoid semantic collisions.

Next up: Dual-layer Caddy + APISIX traffic routing and single-token decoupling!
Like & Repost to follow the series 🚀 #AIGateway #APISIX #HomeLab #DevOps
