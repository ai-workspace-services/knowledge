---
title: 附录：自建 observability → 观测云 迁移矩阵与验证实验
status: outline
series: quarterly-guance-collaboration
article_no: 02
fact_checked: 2026-10-12
---

# 附录｜迁移矩阵与验证实验

服务于 [文章 02 大纲](./outline.md)。现状以 `ai-workspace-infra/observability` 及其固定的 `ai-workspace-infra/playbooks` 提交为准；观测云能力以官方文档为准（见文末）。

图例：🟢 官方文档支持、低改动 · 🟡 支持但需实测/改写 · 🔴 免费版不可用或不建议迁 · ⚪ 保留在自建

## 1. 采集与数据通道

| 现有 | 观测云对应 | 双写方式 | 难度 | 备注 |
| --- | --- | --- | --- | --- |
| 应用 OTLP → OTel Collector | DataKit `opentelemetry` 采集器 | Collector 增加 exporter：gRPC（避开现有 Trace 后端已占用端口）或 HTTP（仅 `application/x-protobuf`） | 🟢 | 改动最小，回退即删一个 exporter |
| spanmetrics（OTel connector） | 观测云 APM 自带 RED 指标 | 不双写，避免重复计费 | 🟢 | |
| Vector Remote Write sink（主机指标） | DataKit `prom_remote_write` 采集器 | Vector 第二个 sink | 🟡 | 需实测编码兼容；必须白名单过滤控制时间线 |
| node_exporter | 透传 `node_*`，或 DataKit 原生主机采集 | 先透传，P3 在 UAT 主机改原生 | 🟢 | 只有原生采集会进入“基础设施 > 主机”并计入 10 台主机 |
| process_exporter | DataKit 进程采集或透传部分 namegroup 指标 | 只透传进程级，**丢弃线程级** | 🟡 | 线程级指标是时间线大头 |
| postgres_exporter | DataKit PostgreSQL 采集器或透传 | P3 评估 | 🟡 | 托管数据库只能透传或用云集成 |
| xray-exporter | 透传 `xray_*` | 可选 | 🟡 | 业务特有指标 |
| Vector `internal_metrics` | 不迁 | — | ⚪ | 留在自建，用于监控双写管道本身 |
| Vector 日志 HTTP sink（file/journald/docker） | DataKit `logstreaming`（带 `source/service`）或原生日志采集 | Vector 第二个 sink | 🟡 | 先在 Vector VRL 本地脱敏（免费版无脱敏） |
| k6 Remote Write | 同 `prom_remote_write`，或只打发布/压测事件 | 可选 | 🟡 | |
| 中心端 blackbox + 主机 SSL 探测 | 可用性监测（HTTP/SSL/TCP/DNS） | 与 blackbox 并行，不关 | 🟡 | 免费版拨测节点范围待确认 |
| opencost-exporter | 云账号管理 / 账单 | 不迁 | ⚪ / 🔴 | 免费版不支持云账号管理 |
| MCP 适配器 | Obsy MCP / Agent Teams | 不在本文范围 | 🔴 | Agent Teams 为付费订阅 |
| 写入入口鉴权 | DataKit → 观测云（workspace token） | — | — | token 只存 Vault（占位 `<vault-kv-path>/guance`），不进仓库与 CI 日志 |

## 2. 数据源与查询

| 现有数据源 | 观测云对应 | 难度 | 备注 |
| --- | --- | --- | --- |
| VictoriaMetrics（PromQL，默认） | 指标 + 图表/查询工作台 PromQL 模式 | 🟡 | 指标名经 DataKit 转换后能否原样执行需实测（E3） |
| VictoriaLogs（LogsQL） | 日志查看器 + DQL | 🟡 | 查询需重写 |
| VictoriaTraces（Jaeger） | APM 链路查看器 | 🟢 | |
| logs↔traces 跳转（derivedFields / tracesToLogs） | 内置 `trace_id` 关联 | 🟢 | 前提：日志带 `trace_id` |
| 让观测云直接查询自建库 | 外部数据源 | 🔴 | 免费版不支持 |

## 3. 仪表板（11 个，免费版上限 10 个）

| 仪表板 | 观测云方式 | 优先级 | 难度 |
| --- | --- | --- | --- |
| 平台导航与总览（homepage-navigation） | 不迁，用观测云首页/目录替代 | 低 | ⚪ |
| Node Exporter Dashboard | DataKit 主机内置视图替换 | 高 | 🟢 |
| process exporter with treemap | 内置进程视图；treemap 插件无对应 | 低 | 🟡 |
| Blackbox Exporter & SSL Probe | 可用性监测内置视图 | 中 | 🟡 |
| Xray Dashboard | Grafana JSON 导入 + 手工修查询（导入实验） | 低 | 🟡 |
| PostgreSQL Database Overview | DataKit PostgreSQL 内置视图 | 中 | 🟡 |
| 全栈无服务器与边缘架构总览 | 重做：APM 服务拓扑 + RUM + 少量自定义图表（部分做导入实验） | 高 | 🟡 |
| Agent / AI Application Observability | Agent 监测原生视图 | 中 | 🟢 |
| VictoriaTraces APM | APM 内置视图替换 | 高 | 🟢 |
| Victoria Logs Overview | 日志查看器 + 1 个自定义视图 | 中 | 🟢 |
| k6 Performance & Capacity | Grafana JSON 导入（导入实验） | 低 | 🟡 |

导入方法：UI“导入仪表板 > Grafana 仪表板”（2026-04-01 起）或 `grafanaCovertToGuance`；逐面板记录“正常 / 需改 / 无法显示”。

## 4. 告警（9 条 → 观测云监控器，免费版最多 10 个、仅阈值检测）

| 现有规则 | 观测云监控器 | 难度 |
| --- | --- | --- |
| 主机 CPU > 85% | 阈值检测（主机指标）或官方主机模板 | 🟢 |
| 主机内存 > 90% | 同上 | 🟢 |
| 根分区 > 85% | 同上 | 🟢 |
| 边缘 Agent 失联 > 300s | 阈值检测“数据断档”/ 主机离线 | 🟡 需确认是否属于阈值检测 |
| xray 探测 DOWN | 阈值检测 `xray_up` | 🟡 |
| Vector 缓冲积压 | **留在 Grafana**（监控双写管道本身） | ⚪ |
| Vector 组件错误 | **留在 Grafana** | ⚪ |
| 站点探测失败 | 拨测任务自带可用性判断 | 🟡 |
| 证书 < 14 天 | SSL 拨测按剩余天数判定 | 🟡 |

共 7 个监控器，在免费上限内；通知用邮件 / 钉钉 / 飞书 / Webhook（免费版无短信）。

## 5. 验证实验（发文前必须跑）

| # | 实验 | 通过标准 | 记录 |
| --- | --- | --- | --- |
| E1 | Vector Remote Write → DataKit `prom_remote_write` | 无报错写入；指标名/标签转换规则明确 | 配置 diff、转换样例 |
| E2 | Vector HTTP(NDJSON) → DataKit `logstreaming` | 字段保留为可查询字段，条数差 <1% | 字段对照表 |
| E3 | 9 条告警 PromQL 在观测云执行 | 7 条迁移规则全部可执行或有等价写法 | 表达式对照 |
| E4 | 3 个仪表板 Grafana JSON 导入 | 统计面板正常/需改/失败比例 | 截图 + 比例 |
| E5 | OTel Collector → DataKit（gRPC / HTTP protobuf） | 7 天 Trace 数差 <1%，P95 偏差 <5% | 对账表 |
| E6 | 白名单前后时间线数量 | 用量 <免费额度 70% | 前后数字 |
| E7 | 免费版拨测节点与任务数上限 | 记录实际可选节点与任务上限 | 截图 |
| E8 | 回退演练计时 | ≤15 分钟恢复“只用 Grafana” | 计时截图 |

## 来源

- [Prometheus Remote Write 采集器](https://docs.guance.com/integrations/prom_remote_write/)
- [OpenTelemetry 采集器](https://docs.guance.com/integrations/opentelemetry/)
- [Log Streaming 采集器](https://docs.guance.com/integrations/logstreaming/)
- [仪表板入门](https://docs.guance.com/getting-started/get-started-with-dashboards/)、[场景 FAQ](https://docs.guance.com/scene/faq/)
- [PromQL 查询](https://docs.guance.com/scene/visual-chart/chart-promql-query/)
- [版本区分](https://docs.guance.com/plans/differences/)
- [SSL 拨测](https://docs.guance.com/synthetic-tests/request-task/ssl/)
