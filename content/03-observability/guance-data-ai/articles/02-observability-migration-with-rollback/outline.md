---
title: 从自建 observability 到 Guance 的平滑迁移与可回退切换
status: outline
series: quarterly-guance-collaboration
article_no: 02
---

# 02｜从自建 observability 到 Guance 的平滑迁移与可回退切换

## 文章定位

这不是“Grafana 面板一键迁移”的宣传稿，而是一篇迁移工程实录：保留现有 `ai-workspace-infra/observability` 的 Prometheus/VictoriaMetrics、Loki、Grafana、OpenTelemetry/Vector 与 Vault 体系，把 Guance 作为并行目标，通过对照、灰度、验收和回退逐步切换。

## 当前系统事实

仓库公开说明：服务端与主机探针可独立安装，使用 OTel/Vector 采集，Grafana 查询 VictoriaMetrics，日志/指标由自建入口接收；凭据通过 Vault 注入，仓库还维护安装器验证与凭据扫描。文章只引用仓库当前 README 和脚本中能复现的内容，不把规划中的 Guance 接收端写成已完成。

## 迁移原则

1. **数据源先不切断**：现有 Grafana 继续作为基线与回退面板。
2. **先迁采集路径，再迁查询体验**：优先验证一台 UAT 主机、一个服务和一条 API 链路。
3. **同一字段契约**：`env/service/host/region/version/route/trace_id/release_tag` 保持一致。
4. **双写或可重放**：只有在 Guance 接收协议、权限和成本确认后，才启用选择性双写；不把密钥写进仓库或 CI 日志。
5. **以业务故障验收**：不以“数据进来了”作为完成标准，要用一次用户慢请求、一次告警和一次发布回归验证。
6. **回退可执行**：保留原 Vector/OTel 配置、Grafana 数据源、Vault secret path 和切换开关，出现丢数、成本失控或查询不可用时恢复原链路。

## 分阶段方案

| 阶段 | 动作 | 退出/回退条件 |
| --- | --- | --- |
| 0. 盘点 | 导出 Grafana 面板、告警、数据源、保留周期和仪表盘截图；建立字段映射 | 缺少 owner、密钥或数据口径不明则不接入 |
| 1. UAT 影子流量 | 在 `console-cloudflare-uat.onwalk.net` 选择一台探针/一个服务，保留写入自建 Grafana，同时将非敏感样本送 Guance | 数据量、延迟、标签或权限不达标立即停止 Guance 写入，不影响 Grafana |
| 2. 对照验证 | 对比同一时间窗的主机指标、日志、Trace、错误率、P95 和告警触发 | 关键指标无法对账、免费额度快速耗尽或查询不可用，回退到自建查询 |
| 3. 小范围切换 | 只把一个 UAT 用户流程的排障入口切到 Guance；发布前后保留 Grafana 对照 | 业务验证失败时切回 Grafana，不改生产路由 |
| 4. PROD 只读/低风险 | 先接入生产低敏信号或拨测，不切断原始采集；建立成本、保留和权限门槛 | 无明确回滚 owner、数据不可解释或合同边界未确认，不扩大范围 |

## 验收清单

- 同一 trace/request id 能关联边缘、应用、数据库或日志证据；
- 现有 Grafana 和 Guance 的关键指标在同一时间窗可解释；
- 发布、告警和故障复盘能标记 `release_tag`；
- Guance 不接收 Vault token、Cookie、Prompt、用户隐私和原始业务密钥；
- 关闭 Guance 写入后，Grafana 基础监控仍可工作；
- 明确免费版额度、7 天存储、专属站点与数据不可迁移等限制；
- 迁移记录包含负责人、时间、变更开关、验证结果和回退命令。

## 公众号结构

1. 先展示现有自建观测栈，而不是贬低它；
2. 解释为什么要引入外部 SaaS，而不是为什么要“替换 Grafana”；
3. 给出迁移前资产清单和字段契约；
4. 展示 UAT 影子流量与双写/对照结果；
5. 公开一次失败或不迁移的判断；
6. 用回退演练证明切换不是不可逆绑定；
7. 最后再讨论 Guance 在本次链路中解决了什么、没有解决什么。

## XHS 版本

- P1：`迁移监控最怕的不是麻烦，是回不去`
- P2：我的 Grafana、VictoriaMetrics、Loki、Vector、Vault 现状
- P3：为什么不直接全量切换
- P4：UAT 影子流量架构
- P5：同一请求在两套系统中的对照
- P6：迁移验收表：字段、延迟、告警、成本、权限
- P7：一键回退需要保留哪些东西
- P8：最终结论：迁移的是排障入口，不是系统主权

## 证据与链接

- [observability 仓库](https://github.com/ai-workspace-infra/observability)
- [UAT Console](https://console-cloudflare-uat.onwalk.net/)
- [自建 Grafana](https://observability.svc.plus/grafana/)
- [观测云数据接入文档](https://docs.guance.com/)

Guance 的具体接收协议、Agent/OTel 配置和免费版限制必须在实施和发布前按官方文档复核；本大纲不假设存在未经确认的一键迁移或 Prometheus Remote Write 兼容性。
