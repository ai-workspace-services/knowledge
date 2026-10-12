---
title: Guance 可观测 SaaS 深度调研与独立开发内容事实基线
description: 面向“独立开发 × 可观测 SaaS 服务”合作方向的 Guance 产品、服务、案例、价值与表达边界研究。
slug: guance-research-brief
lang: zh
date: 2026-09-09T00:00:00Z
author: shenlan
tags:
  - guance
  - observability
  - agent-observability
  - research
category: observability
status: research
---

# Guance 可观测 SaaS 深度调研与独立开发内容事实基线

## 执行摘要

Guance 当前官网叙事已经从传统“全栈可观测平台”向“AI 时代的监控观测基础服务”扩展。首页使用“让数据说话，让 AI 感知，让人决策，让 Agent 行动”的表达，产品全景则把能力分为统一观测、异常响应、数据治理、AI 与 Agent 四层。[^1][^2]

本专题的研究对象不是抽象的 Data + AI 趋势，而是“可观测 SaaS 能否成为独立开发者长期可负担的服务”。自建栈负责开放数据底座、长期控制和兜底；Guance 负责统一上下文、用户体验、托管运营和专业服务。最需要验证的不是企业功能数量，而是能否减少上下文切换、维护面和夜间排障时间，以及这些收益是否值得订阅成本。

研究同时显示，Guance 的 SaaS 能力既覆盖基础设施、日志、APM、RUM、拨测、告警与故障响应，也延伸到 Agent Session/Trace、Token、模型/Tool/Skill、Eval、Obsy AI、MCP 与受控审批。[^3][^4][^5][^6] AI 能力适合作为独立开发运营中的一个季度子专题，但不能覆盖“产品上线、用户体验、成本、值班与长期维护”这条主线。

本研究中的产品矩阵仅作为案例选材库，不直接转换成文章目录。正式内容必须从独立开发过程中的真实触发出发，例如第一次接入、第一次告警、用户反馈卡顿、海外不可用、数据库变慢、AI 改动上线或 90 天续费判断；只有解决该问题确实需要时，才引用对应的 Guance 能力。

内容总纲固定为：独立开发者如何选择、接入和长期使用可观测 SaaS；Guance 是贯穿全年的真实服务案例。Data + AI、Vibe Coding、Grafana 迁移和 Agent 观测都只是该过程中的具体场景，不独立发展为产品功能复述。

## 1. 研究范围与判断方法

研究范围包括：

- Guance 官网首页、产品全景、产品页、定价页和开源对比页；
- Guance 官方文档的 Agent 监测、Obsy AI、Agent Teams、MCP、Skill 和更新日志；
- Guance 官方客户案例集合与公开实践文章；
- 本仓库已有 `observability.svc.plus`、Grafana、OpenTelemetry 和独立开发内容风格。

判断分为三层：

| 层级 | 定义 | 在文章中的写法 |
| --- | --- | --- |
| 官方事实 | 官网或文档明确说明的功能、额度、接入方式 | “官方文档显示/当前支持……”并标注核验日期 |
| 分析判断 | 根据产品结构与目标读者推导的价值 | “更适合验证的价值是……”并说明推理 |
| 实践结论 | 在作者环境实际接入、测量和复盘 | “在本次测试中……”并给出证据与口径 |

## 2. 产品定位：从 Dashboard 到 Agent 行动

官网首页呈现的价值链可以压缩为：

```text
Telemetry Data
      ↓
统一采集、标签、存储与界面
      ↓
基础设施 / 日志 / APM / RUM / 可用性
      ↓
告警 / 事件 / SLO / 故障响应
      ↓
Obsy AI Copilot / Agent Monitoring / Agent Teams
      ↓
人在环决策 + 受控 Agent 行动
```

这一定位与独立开发者叙事的契合点在于：一个人既是开发、SRE、DBA、产品和客服，也最容易被工具切换和维护工作吞噬。平台价值应被翻译为“少搬运上下文、少维护一套产品、缩短从用户问题到可操作证据的路径”，而不是“功能更多”。

## 3. 已确认产品矩阵

> 本节用于事实核验，不用于按产品逐项写软文。一个真实案例可以跨多个信号，也可以只使用一项能力。

| 层 | 已确认能力 | 适合的合作内容 | 验证要求 |
| --- | --- | --- | --- |
| 数据与基础设施 | DataKit、650+ 集成、指标、日志、主机、容器、Kubernetes、GuanceDB、Pipeline | 自建栈接入、标签、日志治理、成本与保留 | 接入耗时、资源开销、字段完整性 |
| 应用 | APM、Trace、服务拓扑、Profile、日志与资源关联 | API 慢请求、代码热点、PostgreSQL 故障链 | 保留 Trace ID 和修复前后对比 |
| 用户体验 | RUM、前端错误、Session Replay | “服务器健康但用户卡”、多端体验 | 隐私遮罩与用户授权优先 |
| 外部可用性 | API/网站/DNS/网络拨测、全球与自建节点 | 海外访问、多云/边缘服务验证 | 固定地域、频率、失败判定和成本 |
| 响应与治理 | 告警、事件、SLO、故障中心、CI 可视化、权限 | 一人值班、发布与故障复盘 | 告警噪声、MTTA/MTTR 口径 |
| Agent 监测 | Session、Trace、Span、Token、模型、Tool、Skill、风险事件、Eval | Codex 行车记录仪、Tool Loop、成本与质量 | 内容采集模式、敏感字段与样本可复算 |
| AI 助手 | Obsy AI Copilot：页面上下文、自然语言分析、查询与 Dashboard/Pipeline 草稿 | “不会查询语言也能开始分析” | 区分草稿生成与生产可用结果 |
| Agent Teams | 可配置 Agent、Skill、MCP、任务接入、协作渠道、审批与运行观测 | 告警研判、RCA、源码定位、受控恢复 | 只读优先、审批、回滚和审计证据 |

产品矩阵来源于官方产品全景、Agent 监测和 Obsy AI 文档。[^2][^3][^5]

## 4. Agent 与 Data + AI：最有差异化的内容机会

### 4.1 Agent Monitoring 不是 Token Dashboard

官方文档将 Agent 监测的核心拆成全链路追踪、质量评估和成本计量。查看器可以按 User、Session、Trace 下钻，并展示模型、Tool、Skill、Token、耗时、错误和风险操作。[^3][^4]

因此内容应明确区分：

```text
Usage Observability
  用了多少 Token？哪个模型最多？

Execution Observability
  Agent 调了什么 Tool？哪里重试？哪个 Span 最慢？

Outcome Observability
  任务是否完成？质量是否合格？是否产生业务结果？
```

Guance 当前公开材料对前两层支持明确，并已加入 Prompt Eval、Schema Eval 等质量能力；第三层仍需要作者自行设计业务结果字段和评估口径。[^7]

### 4.2 Codex 接入是可直接实测的传播入口

Agent 监测接入文档已列出 Codex、Claude Code、OpenClaw、Hermes、Qoder、WorkBuddy、OpenCode 等集成类型（截至 2026-10-12 的更新日志另新增 CodeBuddy、Cursor、Deepseek Harness、Kiro、Dcode、Grok Agent/Grok Build、OMP、MiMo、Pi Agent 等）；Codex 等类型通过 `obs-agent-connector` 接入。[^8] 这让“给 Coding Agent 装行车记录仪”可以从观点文章升级为可复现实验。

发布时需要特别说明：安装器可接入不等于所有字段都在所有 Agent/版本上完全一致。每篇都应记录 Agent 版本、连接器版本、采集模式和字段缺失情况。

### 4.3 Copilot 与 Agent Teams 必须分开写

官方文档把 Obsy AI Copilot 定位为工作空间内即时、由用户发起的辅助；Agent Teams 则面向可配置、可部署、可编排的持续工作流。[^5]

内容表达可采用：

- Copilot：人在当前页面提问，AI 帮助理解、查询和生成草稿；
- Agent Teams：给 Agent 明确职责、Skill、MCP、权限和触发方式，让它持续处理一类工作；
- Agent Monitoring：观察 Agent 自己运行得是否健康、昂贵、异常或越界。

三者是互补关系，不能混写成一个“AI 自动运维”概念。

### 4.4 Skill、MCP 和审批是可信内容的关键

官方定义中，Skill 负责告诉 Agent“怎么做”，MCP 负责提供“用什么做”；二者都不会自动扩大权限。文档建议最小范围接入，涉及敏感数据或写操作时优先只读并保留人工确认。[^6][^9]

这恰好可以形成系列的可信安全立场：不是宣传“AI 自动修生产”，而是展示“证据优先、只读优先、有限行动、人工审批、完整审计”。

## 5. 从自建 Grafana 到 Guance：不应写成迁移替代

### 5.1 自建栈的持续价值

`observability.svc.plus` 已形成以开放组件为基础的指标、日志、Trace 和 Dashboard 能力。它可承担：

- 基础设施核心指标与长期数据控制；
- 自定义 Dashboard 和独立故障兜底；
- 对采集链、标签和存储成本的深度理解；
- 不依赖单一 SaaS 的最低观测能力。

### 5.2 Guance 更值得验证的增量价值

官方“Guance vs 开源自建”材料强调端到端覆盖、统一查询界面、上下文关联、OpenAPI/Func、兼容开源采集和企业级治理。[^10] 该材料属于厂商自述，不能直接当作效果证据，但可以转化成以下实测问题：

1. 接入一条新信号需要多少时间？
2. 从 RUM 事件到后端 Trace、日志和资源需要多少次页面切换？
3. 一次夜间故障的定位路径是否变短？
4. 自建栈需要新增哪些组件才能达到同等体验？
5. 免费版/商业版用量在真实独立开发环境中的成本是多少？
6. 数据导出、开放接入和退出路径是否满足数据主权要求？

### 5.3 推荐架构假设

```text
                 OpenTelemetry / Open Signals
                              │
               ┌──────────────┴──────────────┐
               ↓                             ↓
    observability.svc.plus                 Guance
    自建存储 / Grafana              RUM / APM / Agent / AI
    核心指标 / 长期底座             统一上下文 / 托管分析
    独立兜底 / 可迁移性             服务支持 / 协作行动
               └──────────────┬──────────────┘
                              ↓
                   Evidence-based Feedback
```

这一“双层架构”是待验证的编辑假设，不是预设结论。第 04、05、15、24、59 篇应逐步用数据验证或修正它。

### 5.4 现有栈事实与官方接入路径（2026-10-12 复核）

- 现有 `ai-workspace-infra/observability`（服务角色固定在 `ai-workspace-infra/playbooks`）实际组件为：VictoriaMetrics 单机（内置 promscrape 抓取）、VictoriaLogs、VictoriaTraces（Jaeger 查询 API）、OpenTelemetry Collector（spanmetrics）、blackbox-exporter、Grafana（Unified Alerting）；主机侧由 Vector 抓取 node/process/blackbox（按需 postgres/xray）exporter，以 Prometheus Remote Write 推送指标、以 HTTP 推送日志。**没有部署 Loki，也没有独立 Prometheus**；VictoriaLogs 只是提供兼容 Loki 的写入路径。
- 官方 DataKit 提供 `prom_remote_write` 采集器，可直接接收 Prometheus Remote Write，是 Vector 双写的最低改动路径（与 Vector sink 的编码兼容性仍需实测）。[^19]
- DataKit `opentelemetry` 采集器支持 gRPC 与 HTTP；HTTP 路径只接受 `application/x-protobuf`，DataKit 1.85.0 起不再支持 `http/json`。[^20]
- DataKit `logstreaming` 采集器可通过 HTTP 接收日志，并支持 `source/service/pipeline` 参数。[^21]
- 自 2026-04-01 起可在观测云 UI 直接导入 Grafana 仪表板 JSON，官方提示部分高级特性可能无法显示或需要手动重配；Guance CLI 对 PromQL 只翻译 `label_values` 的非嵌套表达式。图表与查询工作台支持 PromQL。**这不是一键迁移**。[^22][^23]

## 6. 免费版与独立开发者进入路径

截至 2026-09-09，定价页公开的免费版上限包括 10 台主机、1 万时间线/天、1,000 万日志/天、2 万 Trace/天、5,000 RUM PV/天、2,000 Session Replay Session/天、20 万次 API 拨测/天、10 个监控器和 7 天循环数据存储；页面同时说明免费版需要资格审核，且免费版数据不能迁移到商业版工作空间。[^11]

2026-10-12 复核补充（[^16][^17][^18]）：

- 口径不一致：`/free` 落地页写 Trace 1 万/天，`/billing` 与版本区分页写 2 万/天；版本区分页的时间线写作“10,000 条”（不带“/天”）。引用时注明页面与日期，或请观测云书面确认。
- 注册：仅在“免费专区（北京）”站点；12 小时内审核；每个账号只能创建 1 个工作空间，最多 5 个成员；免费工作空间不支持解散，Owner 不能移交。
- 功能限制：仪表板/笔记/自定义查看器各最多 10 个；监控器仅“阈值检测”；不支持 Profiling、异常追踪、定时报告、短信、SSO；不支持 OpenAPI/API Key、数据转发/备份、敏感数据脱敏与扫描、外部数据源、快照/图表/iframe 分享；Pipeline 仅本地 Pipeline。
- 协议：**4.7 未经书面授权不得将免费版用于商业用途或向第三方提供服务**；观测云可修改、暂停或终止免费服务，可提前 15 天通知终止，不保证永久提供；超额可暂停或限制服务；不开票；无电话/优先工单；6.2.2 可在非商业目的下以聚合或匿名化方式使用业务数据。
- 合作前置条件：XWorkTech 属于商业项目，使用免费版前需取得观测云书面授权，并在文章中披露。
- 容量对照（作者环境，2026-10-12 只读观察，公开前需作者确认）：自建栈约 11 台主机、约 3.6 万条活跃时间序列、11 个 Grafana 仪表板，分别超过免费版 10 台主机、1 万时间线、10 个仪表板的上限。因此免费版只适合“瘦身”后的 UAT 单链路 POC（白名单过滤指标、丢弃线程级进程指标），生产全量切换需要商业版。

逐条来源与结论见 [2026-10 事实核验记录](./03-fact-check-2026-10.md)。

对内容的意义：

- 免费版适合做“能否覆盖一个独立开发者真实工作负载”的连续实验；
- “功能不打折”或“永久免费”等营销句不应脱离当期页面限制单独引用；
- 免费版到商业版的数据迁移限制是重要决策信息，必须在测评中显著说明；
- 所有额度与价格在正式发布前 48 小时重新核验。

## 7. 官方客户案例能提供什么

官方客户页覆盖汽车、零售、制造、互联网、游戏、金融等行业。可迁移到本专题的方法，不是“大客户背书”，而是问题模式。[^12]

| 官方案例公开主线 | 可迁移的问题模式 | 适合引用的专题 |
| --- | --- | --- |
| 安踏：从零散开源监控到统一平台 | 开源工具多、上下文分散、治理成本上升 | #05、#24、#59 |
| 通力电梯：日志、链路、指标与前端行为统一 | 设备/应用/用户数据需要同一时间轴 | #08、#18、#26 |
| 美宜佳：端到端交易链路与团队协作 | 从网络、服务器、应用到 POS/前端定位 | #06、#08、#52 |
| 英雄互娱：Profile 结合链路做代码调优 | 平均指标正常时寻找代码热点 | #32 |
| 晨星资讯：CDN 与端到端用户体验 | 海外访问和外部依赖 | #09、#33、#35 |
| 极氪/圣戈班：多云与混合环境统一 | 多云资源与观测上下文统一 | #18、#24、#59 |

这些案例只能引用公开页面已经披露的范围。任何具体降幅、成本或 MTTR 数据若页面未公开，必须由 Guance 或客户另行书面授权。

## 8. 内容机会排序

| 优先级 | 主题 | 理由 | 首次出现 |
| --- | --- | --- | --- |
| P0 | Coding Agent 监测 | 与 Vibe Coding 强关联，可形成个人真实数据 | #01–#03、#10 |
| P0 | 自建 + 托管的混合路线 | 作者独有工程实践，避免普通软文 | #04–#06 |
| P0 | RUM→APM→DB 证据链 | 容易用截图和故障故事解释平台价值 | #07–#08 |
| P1 | MCP + Agent Teams RCA | 品牌差异化强，但必须做好权限与实测 | #11 |
| P1 | 免费版独立开发者实测 | 转化路径短，时效和限制需严格复核；免费版商业用途需书面授权 | #01、#16 |
| P1 | 全球拨测 | 可结合 XConnect/多云节点 | #09、#35 |
| P2 | Copilot 自然语言分析 | 易演示，但需避免只做“AI 总结” | #49 |
| P2 | 企业客户案例迁移 | 有品牌背书，需转译成小团队方法 | 2027 各季度 |

## 9. 风险、缺口与验证计划

### 9.1 关键风险

- **产品迭代快**：截至 2026-10-12，更新日志在 9 月仍持续增加 Agent 类型、AI 监控器、指标型 SLO、Status Page 和 Copilot 场景，文章截图和术语可能很快过期。[^7]
- **厂商资料单边性**：产品优势和客户价值主要来自官方资料，效果必须用作者实测或客户授权补强。
- **隐私风险**：Agent 输入输出、Session Replay、日志和 Trace 可能包含源代码、用户信息、密钥或业务参数。
- **自动行动风险**：MCP 或 Agent Teams 接入生产系统后可能具备写能力，应默认只读并设置人工审批。
- **成本口径风险**：Token、日志条数、Trace 数、时间线和任务调用可能来自不同计量体系，不能混算。
- **标题事实风险**：“8 天 30 亿 Token”等强数字在去重、缓存、上下文重复计算后可能变化。

### 9.2 首轮必须完成的实验

1. 一台测试主机接入基础设施与日志，记录安装时间和资源开销；
2. 一条 Web 用户请求打通 RUM、APM、日志与 PostgreSQL；
3. 三个地区对同一 API 做拨测并设计失败告警；
4. Codex 接入 Agent 监测，验证 Session/Trace/Tool/Skill/Token 字段；
5. 捕获并解释一次 Tool 重试或循环；
6. Copilot 对同一故障生成查询与分析，由人工验证准确性；
7. Codex 通过只读 MCP 请求 RCA Agent，把证据映射回源码；
8. 对自建与 Guance 各自的维护工时、页面切换和定位时间做对比。

## 10. 研究结论

最有潜力的合作定位不是“一个 Grafana 用户为什么换平台”，而是：

> **一个独立开发者如何从开放的自建 Telemetry 底座出发，为 Vibe Coding 建立可以被人和 Agent 共同使用的反馈系统。**

Guance 在这条故事线中的价值应通过三类证据逐步建立：

1. **统一上下文**：用户、应用、资源与 Agent 数据能否沿同一问题路径关联；
2. **注意力杠杆**：是否减少工具维护、上下文搬运和夜间排障成本；
3. **受控智能**：AI 能否基于真实证据工作，同时保留权限、审批、审计和人工决策。

这三类证据一旦建立，12 篇最低合约可以自然延展为 2027 年 AgentOps、一人 SRE、真实用户体验和 AI SRE 四个季度专题，而不需要每年重新发明一套内容逻辑。

## Sources

1. 观测云，《[观测云：AI 时代的监控观测基础服务](https://www.guance.com/)》，访问于 2026-09-09。
2. 观测云，《[可观测性平台与全栈监控产品](https://www.guance.com/product-dashboard)》，访问于 2026-09-09。
3. 观测云文档，《[Agent 监测](https://docs.guance.com/agent/)》，访问于 2026-09-09。
4. 观测云文档，《[Agent 监测查看器](https://docs.guance.com/agent/explorer/)》，访问于 2026-09-09。
5. 观测云文档，《[Obsy AI](https://docs.guance.com/ai/)》，访问于 2026-09-09。
6. 观测云文档，《[Skill 与 MCP：如何选择](https://docs.guance.com/agent-teams/agent-capabilities/)》，访问于 2026-09-09。
7. 观测云文档，《[更新日志](https://docs.guance.com/release-notes/)》，访问于 2026-09-09，复核于 2026-10-12。
8. 观测云文档，《[新建 Agent 监测应用](https://docs.guance.com/agent/agent-apps/)》，访问于 2026-09-09。
9. 观测云文档，《[MCP 服务](https://docs.guance.com/agent-teams/mcp-services/)》，访问于 2026-09-09。
10. 观测云，《[观测云与开源自建监控方案对比](https://www.guance.com/whitepaper/guanceVSopensource)》，访问于 2026-09-09。
11. 观测云，《[价格：免费版、商业版与企业版](https://www.guance.com/billing?version=free)》，访问于 2026-09-09。
12. 观测云，《[客户案例](https://www.guance.com/customer)》，访问于 2026-09-09。
13. 观测云，《[基于 AI Agent Teams 能力的场景实践](https://www.guance.com/learn/articles/guance-ai-agent-teams-scene)》，访问于 2026-09-09。
14. 观测云，《[与本地 Coding Agent 协作排障](https://www.guance.com/learn/articles/coding-agent)》，访问于 2026-09-09。
15. 观测云，《[对接 OpenTelemetry 最佳实践](https://www.guance.com/learn/articles/OpenTelemetry)》，2024-08-12。
16. 观测云文档，《[注册免费版](https://docs.guance.com/plans/free/)》，访问于 2026-10-12。
17. 观测云文档，《[版本区分](https://docs.guance.com/plans/differences/)》，访问于 2026-10-12。
18. 观测云文档，《[观测云免费版订阅协议](https://docs.guance.com/agreements/free-agreement/)》，修订 2026-07-29，生效 2026-08-29，访问于 2026-10-12。
19. 观测云文档，《[Prometheus Remote Write 采集器](https://docs.guance.com/integrations/prom_remote_write/)》，访问于 2026-10-12。
20. 观测云文档，《[OpenTelemetry 采集器](https://docs.guance.com/integrations/opentelemetry/)》，访问于 2026-10-12。
21. 观测云文档，《[Log Streaming 采集器](https://docs.guance.com/integrations/logstreaming/)》，访问于 2026-10-12。
22. 观测云文档，《[仪表板入门](https://docs.guance.com/getting-started/get-started-with-dashboards/)》与《[场景 FAQ](https://docs.guance.com/scene/faq/)》，访问于 2026-10-12。
23. 观测云文档，《[PromQL 查询](https://docs.guance.com/scene/visual-chart/chart-promql-query/)》，访问于 2026-10-12。

[^1]: 观测云，《[观测云：AI 时代的监控观测基础服务](https://www.guance.com/)》，访问于 2026-09-09。
[^2]: 观测云，《[可观测性平台与全栈监控产品](https://www.guance.com/product-dashboard)》，访问于 2026-09-09。
[^3]: 观测云文档，《[Agent 监测](https://docs.guance.com/agent/)》，访问于 2026-09-09。
[^4]: 观测云文档，《[Agent 监测查看器](https://docs.guance.com/agent/explorer/)》，访问于 2026-09-09。
[^5]: 观测云文档，《[Obsy AI](https://docs.guance.com/ai/)》，访问于 2026-09-09。
[^6]: 观测云文档，《[Skill 与 MCP：如何选择](https://docs.guance.com/agent-teams/agent-capabilities/)》，访问于 2026-09-09。
[^7]: 观测云文档，《[更新日志](https://docs.guance.com/release-notes/)》，访问于 2026-09-09，复核于 2026-10-12。
[^8]: 观测云文档，《[新建 Agent 监测应用](https://docs.guance.com/agent/agent-apps/)》，访问于 2026-09-09。
[^9]: 观测云文档，《[MCP 服务](https://docs.guance.com/agent-teams/mcp-services/)》，访问于 2026-09-09。
[^10]: 观测云，《[观测云与开源自建监控方案对比](https://www.guance.com/whitepaper/guanceVSopensource)》，访问于 2026-09-09。
[^11]: 观测云，《[价格：免费版、商业版与企业版](https://www.guance.com/billing?version=free)》，访问于 2026-09-09。
[^12]: 观测云，《[客户案例](https://www.guance.com/customer)》，访问于 2026-09-09。
[^16]: 观测云文档，《[注册免费版](https://docs.guance.com/plans/free/)》，访问于 2026-10-12。
[^17]: 观测云文档，《[版本区分](https://docs.guance.com/plans/differences/)》，访问于 2026-10-12。
[^18]: 观测云文档，《[观测云免费版订阅协议](https://docs.guance.com/agreements/free-agreement/)》，访问于 2026-10-12。
[^19]: 观测云文档，《[Prometheus Remote Write 采集器](https://docs.guance.com/integrations/prom_remote_write/)》，访问于 2026-10-12。
[^20]: 观测云文档，《[OpenTelemetry 采集器](https://docs.guance.com/integrations/opentelemetry/)》，访问于 2026-10-12。
[^21]: 观测云文档，《[Log Streaming 采集器](https://docs.guance.com/integrations/logstreaming/)》，访问于 2026-10-12。
[^22]: 观测云文档，《[仪表板入门](https://docs.guance.com/getting-started/get-started-with-dashboards/)》与《[场景 FAQ](https://docs.guance.com/scene/faq/)》，访问于 2026-10-12。
[^23]: 观测云文档，《[PromQL 查询](https://docs.guance.com/scene/visual-chart/chart-promql-query/)》，访问于 2026-10-12。
