# 独立开发观察者计划：AI × 可观测 SaaS 首季（v4）

本季主题：AI 如何帮助一个个人 SaaS 被开发出来、被看懂、被持续运行。共 12 篇核心稿，另有 R1–R3 替补选题（不额外增加篇数）。

公众号结构：一段真实场景 → 一个知识点 → 最小实践 → 结果和局限 → 适用 / 不适用人群 + 决策表。小红书结构：一个冲突标题、一张链路图、一张脱敏实测图（【待实测截图】占位，不编造）、一个结论。默认篇幅：公众号 ≤1500 字，小红书 600–800 字，最终以合作方确认为准。

每篇目录：wechat.md、xhs.md、fact-sheet.md、sources.md、diagrams/（src 为 .dot，gif 为动图）。字数为可见非空白字符（不含图片行、链接地址与 Markdown 符号）。

## 核心 12 篇

| # | 公众号标题 | 小红书标题 | 模板 | 阶段 | 状态 | 公众号字数 | 小红书字数 | 动图数 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 01 | [Cloudflare + Cloud Run + Supabase 之后，我给个人 SaaS 补上了观测云免费专区](01-free-zone-onboarding/wechat.md) | [低成本 SaaS 拼好了，还差一双眼睛](01-free-zone-onboarding/xhs.md) | 成本账本型 | 第一月·接得上 | 全文稿 | 1330 | 637 | 4 |
| 02 | [AI 辅助 Grafana 面板搬家：从 JSON 到观测云配置，保留回退](02-dashboard-semantic-reconcile/wechat.md) | [面板搬家，最难的是查询口径对上](02-dashboard-semantic-reconcile/xhs.md) | 动手实操型 | 第一月·接得上 | 全文稿 | 1378 | 630 | 4 |
| 03 | [AI生成的页面上线后变卡，我先看用户体验而不是CPU](03-rum-ai-page-slow/wechat.md) | [用户说卡，AI写的页面哪里慢？](03-rum-ai-page-slow/xhs.md) | 误区纠偏型 | 第一月·接得上 | 大纲 | 693 | 250 | 3 |
| 04 | [一个登录请求经过几朵云？用Trace把它接起来](04-login-trace-across-clouds/wechat.md) | [一个登录请求到底去了哪里？](04-login-trace-across-clouds/xhs.md) | 故障复盘型 | 第一月·接得上 | 全文稿 | 1169 | 647 | 4 |
| 05 | [AI帮我生成的告警，怎样才能真的值得打断我？](05-actionable-alerts/wechat.md) | [告警太多，AI能帮我筛吗？](05-actionable-alerts/xhs.md) | 问答拆解型 | 第二月·看得懂 AI | 全文稿 | 963 | 635 | 3 |
| 06 | [Codex的一次任务，到底调用了多少次工具？](06-codex-tool-calls/wechat.md) | [AI说完成了，我想看它做了什么](06-codex-tool-calls/xhs.md) | 动手实操型 | 第二月·看得懂 AI | 大纲 | 709 | 256 | 3 |
| 07 | [Token花掉以后，怎样知道它有没有换来交付？](07-token-to-delivery/wechat.md) | [Token用得多，不代表真的干成了](07-token-to-delivery/xhs.md) | 成本账本型 | 第二月·看得懂 AI | 大纲 | 670 | 226 | 3 |
| 08 | [Agent没有报错，为什么我的任务一直跑不完？](08-agent-loops/wechat.md) | [AI没崩，但一直在原地打转](08-agent-loops/xhs.md) | 故障复盘型 | 第二月·看得懂 AI | 大纲 | 629 | 229 | 3 |
| 09 | [AI改完代码就发布？我用观测数据检查这一版](09-release-before-after/wechat.md) | [AI写完了，怎么确认没变差？](09-release-before-after/xhs.md) | 对比选型型 | 第三月·守得住、退得出 | 大纲 | 617 | 244 | 3 |
| 10 | [凌晨收到告警，让AI先帮我整理排障线索](10-ai-triage-clues/wechat.md) | [没有值班团队，AI先查什么？](10-ai-triage-clues/xhs.md) | 问答拆解型 | 第三月·守得住、退得出 | 大纲 | 650 | 215 | 3 |
| 11 | [自建监控自己挂了，谁来提醒我？](11-who-monitors-monitoring/wechat.md) | [监控坏了，谁来监控监控？](11-who-monitors-monitoring/xhs.md) | 误区纠偏型 | 第三月·守得住、退得出 | 全文稿 | 1058 | 626 | 4 |
| 12 | [和AI一起运营个人SaaS一季，我还会继续用观测SaaS吗？](12-season-review-exit/wechat.md) | [AI、监控、账单：这一季到底值不值](12-season-review-exit/xhs.md) | 对比选型型 | 第三月·守得住、退得出 | 全文稿 | 929 | 612 | 4 |

## 替补选题

| # | 标题 | 模板 | 用途 | 状态 | 大纲字数 |
| --- | --- | --- | --- | --- | --- |
| R1 | [换平台演练：同一份 OTel 数据，能不能同时送进自建和观测云？](R1-otel-dual-target-portability/outline.md) | 动手实操型 | 可替换 #08 | 替补大纲 | 757 |
| R2 | [AI 调用慢，是模型慢还是工具慢？](R2-ai-latency-model-vs-tool/outline.md) | 问答拆解型 | 可替换 #08 | 替补大纲 | 600 |
| R3 | [只给 AI 只读工具，它能解释异常吗？](R3-readonly-mcp-explain/outline.md) | 动手实操型 | 可替换 #10 | 替补大纲 | 522 |

阅读顺序为 01 → 12，每篇末尾有上一篇 / 下一篇链接，12 回到 01 形成闭环；相邻两篇模板不重复。季度计划见 [quarterly-plan.md](quarterly-plan.md)。
