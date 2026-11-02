# 独立开发观察者计划：AI × 可观测 SaaS 首季文章工作区

本目录收录《独立开发观察者计划：AI × 可观测 SaaS》首季全部 15 篇成套双端图文交付草稿（12 篇核心主题 + R1–R3 可替换候选池）。

所有文章均严格遵循以下工程交付铁律：
1. **微信公众号长文**：InfoQ 客观技术深度风格，严格 1000–1500 字，结构化 5 大段落，正文穿插无文字标题的技术动图（GIF）。
2. **移动端决策表**：精简为移动端友好的 3 列布局（`决策维度 | 方案对比 (自建基准 vs 观测云) | 独立开发建议与避坑`），杜绝横向挤压。
3. **小红书图文笔记**：口语化、痛点引入、严格 600–800 字、P1–Pn 结构化要点、代码化极简作业直抄与真实 UAT 复盘。
4. **全代码化交付**：彻底杜绝 Web 界面手动点击与控制台截图，全量基于 GitOps / IaC (Terraform) / Ansible Playbook / Vault 凭据隔离。
5. **素材纯粹性**：所有图文配套 GIF 均为纯拓扑、数据流与状态机动画，**图片内不带标题文本**。

---

## 首季 15 篇全量文章索引

| 序号 | 目录路径 | 微信公众号技术长文标题 | 小红书笔记封面标题 | 核心唯一知识点 |
| :---: | :--- | :--- | :--- | :--- |
| **01** | [`01-free-tier-for-indie-saas`](./01-free-tier-for-indie-saas/article_draft.md) | 我的个人 SaaS 已经够便宜了，还能用什么补上监控？ | 薅北京专区的羊毛，先看清条件！ | 免费额度与服务选型 |
| **02** | [`02-observability-migration-with-rollback`](./02-observability-migration-with-rollback/article_draft.md) | AI 帮我搬 Grafana 面板：先让数字对上，再决定切换 | 监控面板搬家，最怕搬错数字！ | 面板语义对账与可回退切换 |
| **03** | [`03-real-user-experience-rum`](./03-real-user-experience-rum/article_draft.md) | AI 生成的页面上线后变卡，我先看用户体验而不是 CPU | 用户说卡，AI 写的页面哪里慢？ | 真实用户体验与 RUM 分析 |
| **04** | [`04-cross-cloud-distributed-tracing`](./04-cross-cloud-distributed-tracing/article_draft.md) | 一个登录请求经过几朵云？用 Trace 把它接起来 | 一个登录请求到底去了哪里？ | 跨多云分布式追踪上下文传播 |
| **05** | [`05-actionable-alerts-and-noise-reduction`](./05-actionable-alerts-and-noise-reduction/article_draft.md) | AI 帮我生成的告警，怎样才能真的值得打断我？ | 告警太多，AI 能帮我筛吗？ | 可行动告警与降噪抑制 |
| **06** | [`06-agent-execution-chain-monitoring`](./06-agent-execution-chain-monitoring/article_draft.md) | Codex 的一次任务，到底调用了多少次工具？ | AI 说完成了，我想看它做了什么 | Agent 执行链与 Tool Span 观测 |
| **07** | [`07-ai-cost-attribution-and-delivery`](./07-ai-cost-attribution-and-delivery/article_draft.md) | Token 花掉以后，怎样知道它有没有换来交付？ | Token 用得多，不代表真的干成了 | AI 业务成本归因与交付关联 |
| **08** | [`08-agent-loop-and-retry-postmortem`](./08-agent-loop-and-retry-postmortem/article_draft.md) | Agent 没有报错，为什么我的任务一直跑不完？ | AI 没崩，但一直在原地打转 | 死循环识别与代码化看门狗熔断 |
| **09** | [`09-canary-release-observability-baseline`](./09-canary-release-observability-baseline/article_draft.md) | AI 改完代码就发布？我用观测数据检查这一版 | AI 写完了，怎么确认没变差？ | 发布前后金丝雀对比与基线门禁 |
| **10** | [`10-evidence-driven-ai-incident-investigation`](./10-evidence-driven-ai-incident-investigation/article_draft.md) | 凌晨收到告警，让 AI 先帮我整理排障线索 | 没有值班团队，AI 先查什么？ | 证据驱动的 AI 调查与只读 MCP |
| **11** | [`11-independent-failure-domain-synthetic-monitoring`](./11-independent-failure-domain-synthetic-monitoring/article_draft.md) | 自建监控自己挂了，谁来提醒我？ | 监控坏了，谁来监控监控？ | 独立故障域与异地网络拨测 |
| **12** | [`12-quarterly-tco-and-exit-strategy`](./12-quarterly-tco-and-exit-strategy/article_draft.md) | 和 AI 一起运营个人 SaaS 90 天，我还会继续用观测 SaaS 吗？ | AI、监控、账单：这一季到底值不值 | 季度 TCO 账本与无损退出演练 |
| **13** | [`13-data-portability-platform-migration`](./13-data-portability-platform-migration/article_draft.md) | AI 帮我做一次“换平台”演练：观测数据如何双写与无损迁出？ | AI 帮我做一次“换平台”演练 | 数据可移植性与换平台演练 (R1) |
| **14** | [`14-ai-latency-breakdown-llm-vs-tools`](./14-ai-latency-breakdown-llm-vs-tools/article_draft.md) | 一次 AI 调用慢，到底是模型还是外部工具？ | 一次 AI 调用慢，到底是模型还是外部工具？ | 调用延迟细粒度拆分与流式诊断 (R2) |
| **15** | [`15-least-privilege-readonly-mcp-audit`](./15-least-privilege-readonly-mcp-audit/article_draft.md) | 给 AI 只读工具后，它能不能解释一次异常？ | 给 AI 只读工具后，它能不能解释一次异常？ | 最小权限原则与只读沙箱审计 (R3) |
