---
title: 观测云合作专题 · 2026-10 事实核验记录
status: fact-review
fact_checked: 2026-10-12
---

# 观测云合作专题 · 2026-10 事实核验记录

- 核验日期：2026-10-12（北京时间）
- 核验对象：本目录 PR #144 合并时的全部文档（年度方案、研究简报、接入路线图、两篇文章大纲）
- 对照来源：观测云官网与官方文档（逐条附链接）、`ai-workspace-infra/observability` 及其固定的 `ai-workspace-infra/playbooks` 提交
- 方法：只读核对公开页面与仓库；未注册观测云账号
- 标记：✅ 一致 · ⚠️ 不完整或有歧义 · ❌ 错误或过时 · ❓ 未核验

## 1. 主要更正（已在本次修订中落实）

| # | 问题 | 级别 | 落实位置 |
| --- | --- | --- | --- |
| 1 | 免费版协议 **4.7**：未经观测云书面授权，不得将免费版用于商业用途或向第三方提供服务。原文档未提及 | ❌ 遗漏 | 研究简报 §6、年度方案 §11、文章 01/02 大纲 |
| 2 | 文章 02 将现有栈写为“Prometheus/VictoriaMetrics、Loki…”。实际为 VictoriaMetrics 单机（内置 promscrape）+ VictoriaLogs + VictoriaTraces + OTel Collector + Vector + Grafana，**未部署 Loki 与独立 Prometheus** | ❌ | 文章 02 大纲、研究简报 §5.4、路线图 |
| 3 | 文章 02 称“不假设 Prometheus Remote Write 兼容性”。官方 DataKit 提供 `prom_remote_write` 采集器；OTLP HTTP 仅接受 protobuf | ⚠️ 过于保守 | 文章 02 大纲与附录、研究简报 §5.4 |
| 4 | 免费版 Trace 额度口径不一：`/billing` 与版本区分页 2 万/天，`/free` 落地页 1 万/天；时间线在版本区分页不带“/天” | ⚠️ | 研究简报 §6、文章 01 事实表 |
| 5 | 漏列免费版功能限制：仪表板 ≤10、无 OpenAPI/API Key、无数据转发、无敏感数据脱敏、无外部数据源、无分享等 | ⚠️ 遗漏 | 研究简报 §6、文章 01/02 |
| 6 | 漏列注册限制：仅“免费专区（北京）”、每账号 1 个工作空间、最多 5 人、空间不可解散、Owner 不可移交 | ⚠️ 遗漏 | 同上 |
| 7 | 容量不匹配：作者环境约 11 台主机、约 3.6 万条活跃时间序列、11 个仪表板，超过免费版 10 台 / 1 万 / 10 个上限 | ⚠️ 遗漏 | 研究简报 §6、文章 01/02 |
| 8 | 研究简报引用的“2026 年 8 月更新日志”已过时；9 月新增 AI 监控器、指标型 SLO、Status Page 及更多 Agent 类型（含 Cursor、Deepseek Harness、Kiro、Grok Agent/Grok Build 等） | ❌ 过时 | 研究简报 §4.2、§9.1 |
| 9 | #01/#02 定义在年度方案表、12 周顺序、文章工作区之间不一致；“免费版实测”被写成第 05/17 篇 | ⚠️ | 年度方案 §4/§5.2/§10/§11、研究简报 §8，统一以文章工作区为准 |
| 10 | Grafana 仪表板导入：2026-04-01 起支持 UI 导入 JSON，官方提示部分高级特性需手动重配；CLI 对 PromQL 仅翻译 `label_values` | ✅ 补充 | 研究简报 §5.4、文章 02 |

## 2. 免费版逐条核对

| 原说法 | 官方当前说法 | 结论 | 来源 |
| --- | --- | --- | --- |
| 免费版需资格审核 | 12 小时内审核并邮件通知 | ✅ 补“12 小时” | [注册免费版](https://docs.guance.com/plans/free/) |
| 最多 5 个成员、7 天循环存储 | 一致 | ✅ | [注册免费版](https://docs.guance.com/plans/free/)、[版本区分](https://docs.guance.com/plans/differences/) |
| 最多 10 台主机 | 一致 | ✅ | [版本区分](https://docs.guance.com/plans/differences/) |
| 1 万时间线/天 | 版本区分页写“10,000 条时间线”（不带“/天”） | ⚠️ 口径待确认 | 同上；[价格页](https://www.guance.com/billing?version=free) |
| 2 万 Trace/天 | `/billing`、版本区分页 2 万；`/free` 1 万 | ⚠️ 页面不一致 | 同上；[免费专区](https://www.guance.com/free) |
| 1,000 万日志/天、5,000 PV/天、2,000 会话重放/天、20 万次拨测/天 | 一致 | ✅ | [版本区分](https://docs.guance.com/plans/differences/) |
| 10 个监控器 | 仅阈值检测，最多 10 个 | ⚠️ 补“仅阈值检测” | 同上 |
| 免费版数据不能迁移到商业版 | 一致；可在其他站点另开商业版 | ✅ | [价格页](https://www.guance.com/billing?version=free) |
| （未提）商业用途 | 协议 4.7：未经书面授权不得商用或向第三方提供服务 | ❌ 遗漏 | [免费版订阅协议](https://docs.guance.com/agreements/free-agreement/) |
| （未提）服务变更 | 可修改、暂停或终止免费服务，不保证永久提供，可提前 15 天通知终止；超额可暂停或限制；不开票；无电话/优先工单 | ❌ 遗漏 | 同上 |
| （未提）数据使用 | 6.2.2：可在非商业目的下以聚合或匿名化方式使用业务数据 | ❌ 遗漏 | 同上 |
| “永久免费”“功能不打折”（落地页） | 与协议“不保证永久提供”及功能限制并存 | ⚠️ 营销语不可单独引用 | [免费专区](https://www.guance.com/free) vs 协议 |
| “免费个人版” | 官方名称为“免费版”，入口为“免费专区” | ⚠️ 用词 | [注册免费版](https://docs.guance.com/plans/free/) |
| 免费版拨测任务数与节点 | 旧版文档提到 5 个任务、仅中国区节点，现行文档未找到 | ❓ 开通后确认 | — |

## 3. 产品能力与接入路径

| 说法 | 核验 | 结论 | 来源 |
| --- | --- | --- | --- |
| Agent 监测集成清单 | 已确认 Codex、Claude Code、Qoder、Hermes、OpenCode、WorkBuddy 等；9 月新增 CodeBuddy、Cursor、Deepseek Harness、Kiro、Dcode、Grok Agent/Grok Build、OMP、MiMo、Pi Agent 等 | ⚠️ 已更新 | [更新日志](https://docs.guance.com/release-notes/) |
| Agent Teams | 月订阅（Pro / Team 两档） | ⚠️ 补“付费订阅” | [商业版计费](https://docs.guance.com/billing-method/commercial-plan-billing/) |
| Prometheus 接入 | DataKit `prom_remote_write` 与 `prom` 抓取 | ✅ | [prom_remote_write](https://docs.guance.com/integrations/prom_remote_write/) |
| OTel 接入 | DataKit `opentelemetry`：gRPC 或 HTTP，HTTP 仅 protobuf（1.85.0 起不支持 http/json） | ✅ | [opentelemetry](https://docs.guance.com/integrations/opentelemetry/) |
| 日志 HTTP 接入 | DataKit `logstreaming`，支持 `source/service/pipeline` 参数 | ✅ | [logstreaming](https://docs.guance.com/integrations/logstreaming/) |
| Grafana 仪表板导入 | 2026-04-01 起 UI 导入；部分高级特性需手动重配；非一键迁移 | ✅ 需说明边界 | [仪表板入门](https://docs.guance.com/getting-started/get-started-with-dashboards/)、[场景 FAQ](https://docs.guance.com/scene/faq/) |
| 图表支持 PromQL | 图表、指标分析、查询工作台支持 | ✅ | [PromQL 查询](https://docs.guance.com/scene/visual-chart/chart-promql-query/) |
| SSL 证书拨测 | 支持按证书剩余天数判定 | ✅ | [SSL 拨测](https://docs.guance.com/synthetic-tests/request-task/ssl/) |
| “650+ 集成” | 9/16 更新日志称集成标签统一为 31 类；总数未逐一核对 | ❓ 引用当期集成页数字 | [更新日志](https://docs.guance.com/release-notes/) |

## 4. 计费与存储（供成本估算引用，以发布当日页面为准）

- 商业版按量、按工作空间、按天结算；中国区数据点单价 ¥0.2 / 千万点·天，时间线、日志、Trace、RUM 等按存储档位（3/7/30 天）分档计价。[商业版计费](https://docs.guance.com/billing-method/commercial-plan-billing/)
- 9/16 起新建费用中心账号默认按“数据点数”计费；指标按存储周期内的数据点总量每日计费，保留期越长费用越高。[更新日志](https://docs.guance.com/release-notes/)、[价格页](https://www.guance.com/billing)
- 缩短指标存储会立即删除旧数据。[数据存储策略](https://docs.guance.com/billing-method/data-storage/)
- 站点之间账号与数据独立、不可迁移。[Open API 站点列表](https://docs.guance.com/open-api/)
- 文章中的成本数字一律标注“估算，未经确认”，7 天实测后以实际账单替换。

## 5. 待确认

1. 免费版 Trace 额度（1 万还是 2 万）与时间线口径（全量还是每日新增）。
2. 免费版拨测任务数与节点范围。
3. 观测云是否就免费版用于 XWorkTech 项目及公开发表给出书面授权。
4. 免费版是否对 `prom_remote_write`、`logstreaming` 等采集器有额外限制（版本区分页仅限制 Pipeline 为本地 Pipeline）。
5. 协议主体与价格页“最终解释权”主体不一致，签约前确认。
6. 作者环境规模数字（主机、序列、仪表板、采集间隔）是否允许公开。
