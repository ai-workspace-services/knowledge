---
title: 从自建 observability 到 Guance 的平滑迁移与可回退切换
status: outline
series: quarterly-guance-collaboration
article_no: 02
target_length: 1000–1500 字（公众号）+ XHS 8 页；完整矩阵与实验见附录
fact_checked: 2026-10-12
---

# 02｜从自建 observability 到 Guance 的平滑迁移与可回退切换

## 文章定位

这不是“Grafana 面板一键迁移”的宣传稿，而是一篇短小的迁移工程实录。

> **核心观点**：迁移监控最怕的不是麻烦，是回不去。可回退的迁移 = **开关 + 双写 + 字段契约 + 对账门槛**；迁走的是排障入口，不是数据主权。

正文只放结论与关键表格；完整的迁移矩阵（采集、数据源、11 个仪表板、9 条告警）和 8 个验证实验放在 [附录：迁移矩阵与验证实验](./migration-matrix.md)。

## 当前系统事实（以仓库为准）

`ai-workspace-infra/observability`（服务角色固定在 `ai-workspace-infra/playbooks`）：VictoriaMetrics 单机（内置 promscrape）、VictoriaLogs、VictoriaTraces（Jaeger 查询 API）、OpenTelemetry Collector（spanmetrics）、blackbox-exporter、Grafana（11 个 provisioning 仪表板、9 条 Unified Alerting 规则）；主机侧 Vector 抓取 node/process/blackbox（按需 postgres/xray）exporter，以 Prometheus Remote Write 推指标、以 HTTP 推日志；凭据由 Vault 注入。**未部署 Loki 与独立 Prometheus**（VictoriaLogs 只提供兼容 Loki 的写入路径）。

## 公众号结构（1,000–1,500 字）

| 节 | 内容 | 字数 |
| --- | --- | ---: |
| 1. 起点 | 一张现有架构图，“它一直在工作”；为什么引入 SaaS 而不是替换 Grafana（引文章 01） | ~150 |
| 2. 先写回退再动手 | 资产盘点、字段契约 `env/service/host/region/version/route/trace_id/release_tag`、四个开关 | ~200 |
| 3. 迁移矩阵 | 精简表（下方）：搬 / 重做 / 留下；完整版链接附录 | ~250 |
| 4. 六个阶段 | 阶段表（下方），每阶段一句话 + 回退触发 | ~300 |
| 5. 切换标准与回退 | 7 条切换标准；关开关回退，目标 15 分钟 | ~250 |
| 6. 结论 | 免费版只够 UAT 演示；生产全量需商业版并公开算账；一个“不迁”的判断 | ~150 |
| CTA | 下载迁移清单模板（单一） | — |

## 迁移矩阵（精简版）

图例：🟢 官方支持、低改动 · 🟡 支持但需实测/改写 · 🔴 免费版不可用 · ⚪ 保留在自建

| 资产 | 观测云对应 | 难度 |
| --- | --- | --- |
| 应用 OTLP → OTel Collector | Collector 增加 exporter → DataKit `opentelemetry`（gRPC 或 HTTP protobuf） | 🟢 |
| Vector Remote Write（主机指标） | Vector 第二个 sink → DataKit `prom_remote_write`（白名单过滤，丢弃线程级进程指标） | 🟡 |
| Vector 日志 HTTP sink | 第二个 sink → DataKit `logstreaming`（先在本地脱敏，免费版无脱敏） | 🟡 |
| blackbox / SSL 探测 | 可用性监测（HTTP/SSL）拨测，与 blackbox 并行 | 🟡 |
| 3 个数据源（VM / VL / VT） | 指标（PromQL 模式）/ 日志查看器 / APM；外部数据源免费版不可用 | 🟡 / 🔴 |
| 11 个仪表板 | 4 个用内置视图替换，≤3 个做 Grafana JSON 导入实验，其余重做或不迁（免费上限 10 个） | 🟢–🟡 |
| 9 条告警 | 7 个阈值监控器；2 条 Vector 管道自监控留在 Grafana | 🟢–🟡 / ⚪ |
| opencost、MCP、Vector 自监控 | 不迁 | ⚪ / 🔴 |

逐项映射见 [附录 §1–§4](./migration-matrix.md)。

## 六个阶段

| 阶段 | 动作 | 继续条件 | 立即回退触发 |
| --- | --- | --- | --- |
| P0 盘点 | 导出仪表板 JSON、告警、数据源；定字段契约与对账方法 | 资产表完成，凭据位置就绪 | — |
| P1 加开关 | playbooks 增加 `otel_guance_exporter_enabled`、`vector_guance_metrics_enabled`、`vector_guance_logs_enabled`、`guance_datakit_enabled`（**提议**，默认关）；workspace token 只存 Vault | 开关为关时配置与现状逐字节一致 | 任一开关为关时出现配置差异 |
| P2 双写 | 先开 Trace exporter（1 个 UAT 服务），再对 1–3 台 UAT 主机开 Vector 第二 sink | 两边写入稳定，无积压 | Collector 错误率上升、Vector 缓冲积压、超额停收、敏感字段命中 |
| P3 并行运行 | 两套系统并行 ≥7 天并每日对账；补 DataKit 原生采集、RUM、拨测、7 个监控器 | 偏差在门槛内，两次故障演练完成 | 演练失败、隐私问题 |
| P4 切换评审 | 逐条核对 7 条切换标准 | 7 条全部满足 + 作者书面确认 | 任一条不满足 |
| P5 切换 | UAT 排障首选入口改为观测云，Grafana 保留为对照与兜底；生产只在商业版合同后另行评估 | 连续 14 天无回退事件 | 关键指标对不上、观测云不可用、成本超上限 |

## 7 条切换标准

1. 数据完整：连续 7 天，主机关键指标同窗偏差 <2%，日志条数与 Trace 数差 <1%。
2. 额度：每项用量 <免费额度 70%。
3. 告警：7 个监控器在 2 次演练中全部触发，延迟不晚于 Grafana 2 分钟，无漏报。
4. 关联：任选 3 个 UAT 请求，能 RUM → Trace → 日志 → 主机一路跳转。
5. 安全：抽查 7 天数据无 token、Cookie、邮箱、Prompt 原文；workspace token 不出现在仓库与 CI 日志。
6. 回退演练：至少 1 次完整回退，15 分钟内恢复“只用 Grafana”。
7. 授权：作者书面确认，并取得观测云对免费版商业用途的书面授权。

## 回退（目标 ≤15 分钟）

自建栈全程未停，所以回退只需要**翻开关**：

1. 值班手册把 UAT 首选入口改回 Grafana。
2. 四个 `*_guance_*_enabled` 开关置为 `false`，按 playbooks 现有方式重跑（或 revert 开关提交），Vector / Collector 恢复单 sink。
3. 停用并禁用 DataKit；随下次前端发布或特性开关移除 RUM SDK。
4. 在观测云停用监控器与拨测，避免误告警。
5. 验证：Grafana 11 个仪表板、9 条告警正常，Vector 无积压。
6. 完全退出时撤销并轮换 workspace token；免费空间不能解散，数据 7 天后滚动删除，需保留的证据提前导出。

## 8 个验证实验（发文前必须跑，详见附录 §5）

| # | 实验 |
| --- | --- |
| E1 | Vector Remote Write → DataKit `prom_remote_write` 兼容性与指标名转换 |
| E2 | Vector HTTP(NDJSON) → DataKit `logstreaming` 字段保留 |
| E3 | 现有 9 条告警 PromQL 在观测云能否执行 |
| E4 | 3 个仪表板 Grafana JSON 导入成功率 |
| E5 | OTel Collector → DataKit（gRPC / HTTP protobuf） |
| E6 | 白名单前后时间线数量 |
| E7 | 免费版拨测节点与任务数上限 |
| E8 | 回退演练计时 |

## 必须披露的限制

- 免费版只够 UAT 演示：10 台主机、1 万时间线、7 天保留、仪表板 ≤10、无 OpenAPI（无法 GitOps 与自动对账，只能 UI 导出）、无脱敏、无外部数据源；免费版商业用途需书面授权。
- Grafana 仪表板可在 UI 导入（2026-04-01 起），但官方提示部分高级特性需手动重配，不是一键迁移；PromQL 兼容需实测。
- 双写期间存储与出网成本翻倍；不承诺 MTTR 降低比例，只报告作者环境实测。

## XHS 版本

- P1：`迁移监控最怕的不是麻烦，是回不去`
- P2：我的 Grafana、VictoriaMetrics、VictoriaLogs、VictoriaTraces、Vector、Vault 现状
- P3：为什么不直接全量切换（免费版装不下，生产要商业版）
- P4：四个开关 + 双写架构
- P5：迁移矩阵：搬 / 重做 / 留下
- P6：7 条切换标准
- P7：翻开关回退，15 分钟
- P8：迁移的是排障入口，不是系统主权

## 证据与链接

- [observability 仓库](https://github.com/ai-workspace-infra/observability)
- [UAT Console](https://console-cloudflare-uat.onwalk.net/)
- [DataKit Prometheus Remote Write](https://docs.guance.com/integrations/prom_remote_write/) · [OpenTelemetry](https://docs.guance.com/integrations/opentelemetry/) · [Log Streaming](https://docs.guance.com/integrations/logstreaming/)
- [仪表板入门（Grafana 导入）](https://docs.guance.com/getting-started/get-started-with-dashboards/) · [版本区分](https://docs.guance.com/plans/differences/)
- [2026-10 事实核验记录](../../03-fact-check-2026-10.md)

截图与配置片段只展示脱敏后的内容；不展示 token、内部地址和未鉴权的接口路径。
