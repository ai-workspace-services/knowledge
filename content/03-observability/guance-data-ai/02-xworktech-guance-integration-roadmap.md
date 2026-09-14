---
title: XWorkTech 从 UAT 到 PROD 的 Guance 可观测接入路线图
description: 以 xworktech 的 Cloudflare、Cloud Run、Supabase 与 GitHub Actions 为真实案例，规划独立开发者逐步接入和长期使用 Guance 的实践路径。
slug: xworktech-guance-integration-roadmap
lang: zh
date: 2026-09-15T00:00:00Z
author: shenlan
tags:
  - guance
  - xworktech
  - indie-developer
  - serverless
  - uat
  - production
category: observability
status: planning
---

# XWorkTech 从 UAT 到 PROD 的 Guance 可观测接入路线图

## 1. 这不是产品清单，而是一条真实工程路径

本方案的主角是独立开发者正在维护的 XWorkTech/XWorkmate 系统，Guance 是贯穿开发、发布、验证和运营的真实 SaaS 服务案例。当前已经使用 [自建 Grafana](https://observability.svc.plus/grafana/) 完成基础监控，因此目标不是替换或否定它，而是在已有指标之上补齐跨层关联、真实用户体验、发布反馈和 AI 任务观测。

> **Grafana 负责“基础信号和自有底座”；GitOps 负责“要发布什么”；Guance 负责“运行得怎样、用户是否受影响、下一步该怎么行动”。**

当前 UAT 拓扑来自 [UAT Serverless 运行时拓扑](../../../docs/zh/serverless-uat-runtime-topology-and-verification.md)：

```text
console-cloudflare-uat.onwalk.net
  ├─ Cloudflare Pages / SSR Workers ×5 / Edge Gateway Workers ×3
  ├─ Cloud Run: uat-accounts / uat-content-service / uat-billing-service
  └─ Supabase Cloud PostgreSQL: xworktech

GitHub Actions + Vault OIDC
  ├─ serverless-orchestrator（部署、迁移、验证）
  ├─ hybrid-orchestrator（自建主链路与 Cloud Run 兜底）
  ├─ rollback-orchestrator（软/硬回滚）
  └─ k6-performance-test（当前 Prometheus Remote Write 写入 observability.svc.plus）
```

用户可从 [xworktech.com](https://xworktech.com/) 了解产品入口；本轮验证与发布应优先使用 [UAT Console](https://console-cloudflare-uat.onwalk.net/)，生产入口和域名切换仍以 GitOps 拓扑与发布流水线为准。[XWorkmate Console](https://console.svc.plus/) 的公开定位是把 Plan → Connect → Execute → Deliver 串成可追踪工作流，这使“用户任务 → API → 数据库 → 交付结果”成为最有价值的端到端观测样本。

## 2. 观测对象：六个平面，先串链路再扩范围

| 平面 | 要回答的独立开发问题 | 现有 Grafana 基础 | Guance 的增量价值 |
| --- | --- | --- | --- |
| 用户体验 | UAT 页面为何慢、白屏或登录失败？ | 通常不在基础 Prometheus 面板内 | RUM、页面加载、JS 错误、会话回放（脱敏），并跳到具体路由和发布版本 |
| Cloudflare 边缘 | 请求被哪个 Worker 接住？是否发生重试/超时/兜底？ | 可保留现有边缘/入口指标 | 看清 Pages、SSR、Gateway 的边界，而非只看总 5xx |
| Cloud Run | 冷启动、revision、实例和接口延迟是否异常？ | 保留现有服务、资源与压测面板 | 把一次 API 慢请求定位到服务版本，并和用户请求关联 |
| Supabase 数据 | 是应用慢还是数据库慢？ | 保留现有 DB latency、连接池、慢查询面板 | 把业务请求与数据层证据关联；日志能力以当前套餐和官方接入方式为准 |
| 发布与回滚 | 哪次 workflow 改坏了线上？回滚是否真的恢复？ | 现有面板通常无法关联 GitHub workflow | 把 release tag、workflow run、部署时间、验证结果和指标放在同一上下文 |
| AI 工作流 | Agent 花费的时间/Token 是否带来交付结果？ | 基础 Grafana 尚未覆盖 Agent 语义 | 让 Xworkmate 的 AI 任务拥有成本、质量和失败路径证据 |

Guance 官方资料已将基础设施、日志、APM、RUM、会话回放、告警和 AI/Agent 观测放在统一平台中；Agent Monitoring 还覆盖 Session、Trace、Token、模型、Tool 与 Skill。接入时应以官方文档和当前套餐为准，而不是预设所有能力默认可用（[产品总览](https://www.guance.com/product-dashboard)、[Agent Monitoring](https://docs.guance.com/agent/)、[AI 能力](https://docs.guance.com/ai/)）。

## 3. 分阶段接入：UAT 先行，PROD 只扩大已验证的契约

### 3.0 先定义两套系统的边界

| 系统 | 保留职责 | 不建议重复建设 |
| --- | --- | --- |
| `observability.svc.plus/grafana/` | Prometheus/OTel 基础指标、主机与服务健康、k6 原始趋势、故障时的自有数据兜底 | 不为同一批基础指标再维护一套完全相同的仪表盘 |
| Guance | 跨信号 Trace、RUM/会话、发布关联、告警协同、Agent/LLM 观测与团队共享 | 不把 GitOps 配置、Vault 密钥或原始 Prompt 当作观测数据源 |

推荐先采用“选择性双写/按信号分流”：基础指标继续进入 Grafana；从 UAT 选一条用户链路把 Trace、错误、发布事件和 RUM 送入 Guance。只有当 Guance 的查询、告警或协作价值被案例验证后，才扩大采集范围。

### 阶段 0：建立观测契约（不改变生产流量）

先统一资源命名和关联字段：`env`、`service`、`component`、`route`、`region`、`revision`、`release_tag`、`workflow_run_id`、`trace_id`、`status`。租户、邮箱、Cookie、IP、Prompt 和 Token 原文不直接采集，必要时只保留哈希或聚合值。

**验收**：同一请求在 UAT 能从 `console-cloudflare-uat.onwalk.net` 的页面/网关，跳到 Cloud Run，再关联 Supabase；没有 trace id 的信号暂不进入下一阶段。

### 阶段 1：UAT 最小闭环

只选一个业务链路（建议登录或内容读取）和一个 Cloud Run 服务，接入 OTel/官方 Agent，保留 `observability.svc.plus/Grafana` 作为并行对照。建立三张视图：UAT 总览、单请求 Trace、错误与延迟。

**验收**：用一次真实 UAT 操作复现“页面 → Worker → Gateway → Cloud Run → Supabase”，能回答耗时最长的环节和对应 release tag。

### 阶段 2：边缘到后端的上下文传播

在 frontend router、5 个 SSR Worker 和 3 个 Gateway 之间保持 W3C Trace Context；Gateway 记录路由边界、上游选择、超时和 failover 标记。Cloud Run 记录 revision 与区域，避免把 Cloudflare 的边缘耗时误判为数据库耗时。

**重点案例**：`api-core` 的 2500ms 超时/兜底路径，比较正常请求、超时请求和 fallback 请求的完整瀑布图。

### 阶段 3：把 GitHub Actions 变成发布证据

在 workflow 中增加 release marker 或等价事件（不把 Vault 密钥写入日志）：

| Workflow | 应关联的观测事件 |
| --- | --- |
| `serverless-orchestrator.yml` | 环境、不可变 tag、Cloud Run revision、Worker 边界、Supabase checkpoint、部署后验证结果 |
| `hybrid-orchestrator.yml` | primary/fallback、路由策略、切换原因、恢复时间、两条链路的同指标对比 |
| `rollback-orchestrator.yml` | 目标 tag、软/硬回滚、数据库 checkpoint、回滚前后错误率与延迟 |
| `k6-performance-test.yaml` | 测试环境、profile、VUs、duration、target URL、release tag；当前写入自建 Prometheus Remote Write，先验证 Guance 接收路径，再决定双写或导出摘要事件 |
| `ai-aggregator-v1.yml` / `xconnect-one-uat.yaml` | AI 任务 session、工具调用、交付结果状态，不采集 Prompt/密钥原文 |

**验收**：在 Guance 中打开一条异常 Trace，可以反查对应 GitHub workflow run 和发布 tag；打开一次回滚事件，可以对比回滚前后 SLO。

### 阶段 4：UAT 验证环境产品化

把 [UAT Console](https://console-cloudflare-uat.onwalk.net/) 作为每周演示和回归入口：固定 5 个黄金用户流程（注册/登录、内容读取、工作区任务、计费查询、失败重试），每次发布自动执行合成检查，并把结果写成可检索事件。RUM 只在 UAT 开启完整诊断，生产默认采样和脱敏。

### 阶段 5：PROD 分层启用

按“只读验证 → 单服务 → 受控流量 → 全链路”的顺序扩大，不先把全部生产数据导入。每一步都使用阶段 0 的同一字段契约，保留 UAT/PROD 对比视图；发生异常时先冻结发布，再用 Trace、release marker 和回滚 checkpoint 判定是否回滚。

## 4. Guance 何时真正产生价值

1. **从“服务挂了”变成“哪个用户流程、哪条路由、哪个 revision 受影响”。**
2. **从“Grafana 面板很多”变成“发布前后同一组业务指标可比较”。**
3. **从“Cloud Run 看起来正常”变成“边缘、计算、数据库在一条 Trace 上对账”。**
4. **从“AI 用了很多 Token”变成“哪个 Agent/Tool/重试环节消耗，是否换来交付结果”。**
5. **从“回滚成功了吧”变成“回滚前后错误率、延迟、用户流程确实恢复”。**

## 5. 首批可写成内容的真实案例

1. **《我没有拆掉 Grafana：把 Cloudflare + Cloud Run + Supabase 的 UAT 最小链路接入观测云》**：展示并行接入、字段契约和第一条完整 Trace。
2. **《AI 帮我迁移 Grafana 面板：资源、指标、流量、压测面板哪些该保留，哪些该重做》**：把面板迁移写成验证过程，而非产品功能罗列。
3. **《从 GitHub Actions 发布到 Cloud Run revision：一条 release trace 如何串起 UAT》**：展示 `serverless-orchestrator` 的部署、验证和 Guance 发布标记。
4. **《console-cloudflare-uat.onwalk.net 的一次 2500ms 超时：我如何判断是 Worker、Cloud Run 还是 Supabase》**：用一次真实故障拆解边界定位。
5. **《混合架构的兜底不是“切过去就算”：用观测数据验证 selfhost 与 Cloud Run fallback》**：对应 `hybrid-orchestrator`。
6. **《AI 工作区一次任务到底做了什么：从 Session、Tool 到交付结果的观测》**：对应 XWorkmate 的用户任务路径，避免展示敏感内容。

## 6. 长期运营与退出边界

- 每周：检查黄金流程、错误预算、异常 Trace、AI 成本和新发布版本。
- 每月：复盘采样率、数据保留、告警噪声、SaaS 费用与自建 Grafana 的重复采集。
- 每季度：只把已证明有价值的服务扩大到 PROD；评估是否需要 RUM、Agent 或更多数据库信号。
- 双写与退出：自建采集和 GitOps 配置保持可用；Guance 连接、仪表盘和告警规则都用文档化字段契约，避免形成不可迁移的数据锁定。

## 7. 资料与事实边界

- 本文的拓扑、服务名和 workflow 名称来自仓库文档与 `platform-ops-toolkit/.github/workflows`，应在每次发布前复核。
- Guance 能力、套餐和接入限制以 [Guance 官网](https://www.guance.com/)、[官方文档](https://docs.guance.com/) 和当期发布说明为准。
- 本文中的“阶段 0–5”是实施建议，不代表当前已经完成的接入；所有生产启用都需要脱敏、权限和回滚演练。
