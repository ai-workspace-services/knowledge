> **说明**：v3 是素材归档；当前计划以 [v4](../series-v4/) 为准。

# 观测云可观测性系列（12 篇）索引

阅读顺序：为什么（01）→ 边界（02–04）→ 怎么做（05–07）→ 验证（08–11）→ 回退/演进（12）→ 回到 01，形成闭环。相邻两篇模板均不同（首尾 12→01 亦不同）。排期草案见 quarterly-plan.md。

计数口径（tools/count.py）：公众号 = 全文可见字符（含标题、表格、参考行、上一篇/下一篇行；去掉图片行、链接 URL、表格分隔行与 Markdown 符号 # * > ` |；不含空白），上限 1500。XHS = 同口径非空白字符，要求 600–800；括号内为连 Markdown 符号一起计的原始非空白字符数，同样落在 600–800 内。

| # | 阶段 | 模板 | 标题 | 背景 | 痛点 | 方案 | 公众号字数 | XHS 字数 | 图（每图有 -wechat.gif 1080 宽 / -xhs.gif 1080×1440） | 达标 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 01 | 为什么 | 故障复盘型 | [一次登录失败翻了三个后台：低成本 SaaS 栈的可观测盲区复盘](01-low-cost-stack-blindspots/wechat.md) | Cloudflare Pages/Workers + Cloud Run + Supabase Free 低成本栈，自建 Grafana/VictoriaMetrics 看基础指标 | 一次登录失败要翻三处后台，无共同请求 ID、无前端视角，Supabase Free 日志只留 1 天 | 只为一条链路建证据链：RUM + Trace + W3C trace context + 统一字段，未关联环节标盲区 | 1120 | 660（含标记 723） | 4：evidence-chain、field-contract、stack-blindspots、triage-path | ✅ |
| 02 | 边界 | 成本账本型 | [观测云免费版的账本：10 台主机、1 万时间线够不够](02-free-zone-quota-ledger/wechat.md) | 准备用观测云免费版（免费专区·北京）做单链路 POC | 额度与功能边界多维，任一项超额即不再上报 | 按版本区分页逐项记账，超限则瘦身为一条链路 + 白名单 | 959 | 667（含标记 730） | 3：feature-limits、poc-scoping、quota-map | ✅ |
| 03 | 边界 | 对比选型型 | [免费版没有平台脱敏：敏感字段该在哪一层拦](03-privacy-before-ingest/wechat.md) | 日志、Trace 属性、前端会话将写入 SaaS 工作空间 | 免费版不支持敏感数据脱敏/扫描，Span 属性默认最多提取 500 键 | 对比平台脱敏/采集前过滤/不采集，选采集前过滤 + 字段白名单 | 1090 | 647（含标记 710） | 3：field-allowlist、mask-options、pre-ingest-layers | ✅ |
| 04 | 边界 | 问答拆解型 | [观测云能 Terraform 吗？面板即代码的 5 个问答](04-terraform-provider-qa/wechat.md) | 现有 IaC：GitOps → renderer → HCL → plan/apply，想把面板与监控器代码化 | 远端资源依赖 Open API，免费版不支持且免费专区不在 endpoint 列表 | 按空间分流：有 API 权限走 plan/import/apply，免费空间只做离线 HCL | 1304 | 734（含标记 799） | 3：endpoint-check、gitops-hcl、resource-map | ✅ |
| 05 | 怎么做 | 动手实操型 | [采集端照样 GitOps：DataKit 接入的 Playbook 实操](05-collector-gitops-handson/wechat.md) | Vector + OTel Collector 采集栈由 Playbook 部署、Vault 注入凭据 | 新增 SaaS 写入通道易泄漏写入 Token、可能拖垮原采集 | 声明进 Git（开关默认关）→ Playbook 部署 DataKit 三个接入口 → 凭据三分 | 1216 | 734（含标记 799） | 3：automation-path、credential-split、ingest-ports | ✅ |
| 06 | 怎么做 | 误区纠偏型 | [1 万条时间线≠1 万个指标：采集前的三道闸](06-timeseries-budget/wechat.md) | Vector 以 Remote Write 推主机指标，新增 sink 写往免费空间 | 时间线上限 10,000，高基数标签放大时间线，超额不再上报 | 三道闸（发送端 keep / DataKit 指标过滤 / 标签裁剪）+ 链路指标不双写 | 1223 | 651（含标记 714） | 3：cardinality、red-no-dup、three-gates | ✅ |
| 07 | 怎么做 | 动手实操型 | [日志双写不丢 trace_id：Vector 接 Log Streaming 实操](07-log-streaming-handson/wechat.md) | Vector 采集 systemd/应用日志经 HTTP 写入 VictoriaLogs（LogsQL） | 日志进观测云若是整行文本且无 trace_id，则无法按字段检索、无法与 Trace 关联 | Vector 第二 sink → logstreaming（source/service/pipeline/tags）+ json_as_fields + 日志带 trace_id | 1227 | 730（含标记 793） | 4：json-as-fields、logs-dual-sink、trace-log-join、url-params | ✅ |
| 08 | 验证 | 对比选型型 | [Grafana 面板搬家不点控制台：JSON 转声明，再 plan](08-grafana-dashboard-import/wechat.md) | 指标与日志已并行写入，面板仍在 Grafana（VictoriaMetrics + VictoriaLogs） | Grafana JSON 不等于观测云 JSON，免费版仪表板 ≤10 且无 Open API，面板无法经 Terraform 写入免费空间 | 对比转换脚本 / AI 直出声明 / 暂保留；统一走 声明 → renderer → HCL → plan，apply 待授权空间实测 | 1157 | 683（含标记 744） | 3：json-to-plan、migration-funnel、path-compare | ✅ |
| 09 | 验证 | 问答拆解型 | [PromQL 搬过去还能跑吗？查询口径的 5 个问答](09-query-semantics-qa/wechat.md) | 面板查询为 PromQL（VictoriaMetrics）与 LogsQL（VictoriaLogs） | 语法能转但语义不一致：指标名切分、step、筛选、P99 算法 | 口径清单逐项核对 + 同一时间窗并排比对 | 1112 | 705（含标记 772） | 4：filter-conversion、metric-naming、query-traps、step-priority | ✅ |
| 10 | 验证 | 成本账本型 | [只有 10 个阈值监控器：告警迁移的预算账](10-alert-monitor-ledger/wechat.md) | 自建告警在 Grafana：资源、失联、站点证书、管道自监控 | 免费版监控器 ≤10 且仅阈值检测，配置不当会被自动暂停 | 按科目分流：阈值/数据断档进监控器，证书站点走拨测，管道自监控留 Grafana | 947 | 657（含标记 726） | 3：alert-triage、pipeline-self-monitor、threshold-pipeline | ✅ |
| 11 | 验证 | 误区纠偏型 | [拨测≠blackbox：免费版 HTTP 拨测最快 30 分钟一次](11-synthetic-vs-blackbox/wechat.md) | 站点与证书类告警已划给可用性监测，自建侧有 Blackbox Exporter | 免费版 HTTP 拨测 1/5/15 分钟档与海外节点仅限商业版，频率档位与节点受限，不能当作 Blackbox 的原样替身 | 分工：Blackbox 保留自建探测，拨测承担外部视角、证书剩余天数与脚本模式业务断言 | 1026 | 648（含标记 711） | 4：check-modes、frequency-tiers、probe-privacy、probe-split | ✅ |
| 12 | 回退/演进 | 动手实操型 | [迁移监控最怕回不去：双写、开关与回退实操](12-dual-write-rollback/wechat.md) | 自建栈持续运行，观测云为并行新链路 | 免费空间 7 天循环、不可解散、可被通知终止，新链路失败时回不去 | 开关 + 双 sink 双写 + 并排对照 + 回退/退出顺序 | 979 | 654（含标记 717） | 4：data-lifecycle、rollback-runbook、side-by-side、switch-states | ✅ |

每篇目录：wechat.md、xhs.md、sources.md（完整来源 URL，不计入字数）、diagrams/src/*.dot、diagrams/gif/*.gif。重新出图：`python3 tools/dots.py && for a in [0-9]*; do python3 tools/render.py $a; done`；重新生成本索引：`python3 tools/build_index.py`。
