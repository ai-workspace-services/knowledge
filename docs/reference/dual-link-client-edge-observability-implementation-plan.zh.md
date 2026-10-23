---
title: 双链路可观测性深化实施规划：客户端、代理节点与流量统计
description: 固定客户端至代理出口和独立流量统计两条基准，记录工具选型、实现契约、进展、任务拆解和验收门禁。
slug: dual-link-client-edge-observability-implementation-plan
lang: zh
date: 2026-10-23
version: "1.0"
status: implementation-plan-not-deployed
category: reference
tags:
  - observability
  - performance
  - tcp
  - otel
  - xconnect
---

# 双链路可观测性深化实施规划

[性能方法白皮书](network-full-path-performance-whitepaper.zh.md) · [JP 双入口诊断案例](network-performance-jp-comparison-20261023.zh.md) · [Projects #4](https://github.com/orgs/ai-workspace-services/projects/4)

## 1. 不变基准与本轮交付

**网络延迟链路：客户端 → 本地 TUN/真实出站 → 公网路径 → 代理节点入站与出口。**

**流量统计链路：Vault → 配置校验 → 0600 凭据文件 → Exporter → 快照探针 → Vector → Billing → PostgreSQL → Accounts → Portal。**

网络性能归因到代理节点出口为止，数据库不属于该链路。节点出口的 DNS/dial/首响应以受控诊断目标作参照，不扩展成对任意网站或其数据库的追踪。流量链路的 DB/API/UI 耗时仅用于解释用量上报/展示延迟，不计入用户代理连接耗时。

本轮落地的是可审阅文档、工具决策和任务契约；没有实现新采集器、部署 Agent、调整路由、合并应用 PR 或执行压测。任务编号为本文规划 ID，尚不是新建 GitHub Issue，也未修改看板字段。

## 2. 证据来源与状态规则

- 历史方案及回执：[Knowledge #183 固定合并版本的方案文档](https://github.com/ai-workspace-services/knowledge/blob/38d15a0840d71edb52ac9caf63782d544a6a8ab2/content/02-iac-devops/cloud-infrastructure-devsecops-baseline/records/prod-v3-v4-20261020/network-and-traffic-otel-plan-20261021.zh.md)。用户另提供了 2026-10-21 方案全文和 2026-10-23 交接手册。
- 本轮在线读取了下列七个 PR 元数据；没有重新执行其中测试或远端运行验收。Project 链接作为组织入口，未读取卡片字段，不能据此宣称看板状态已核验。
- 2026-10-21 线上/隔离回执属于历史证据；2026-10-23 Mac 探测属于另一窗口，不混成同一次事件。
- 状态使用 PLANNED、CODE_REVIEW、MERGED、DEPLOYED、RUNTIME_PASS、FAIL、BLOCKED、NOT_RUN。一个 PR 可合并不代表 CI/review 全满足；MERGED 不代表线上生效。

## 3. 现有 PR 与能力映射

| PR | 本轮在线状态 | 能力及对应链路 | 剩余边界 |
| --- | --- | --- | --- |
| [Billing #54](https://github.com/ai-workspace-services/billing-service/pull/54) | OPEN；mergeable=true；clean | 流量 ingest 的业务阶段 spans、W3C、Span Links | 不提供用户到节点的 TCP RTT；保持未合并 |
| [Billing #55](https://github.com/ai-workspace-services/billing-service/pull/55) | OPEN；mergeable=true；clean | 流量账务事务、重放/同分钟幂等修复 | 独立账务审查；不是网络采集前置；保持未合并 |
| [Accounts #264](https://github.com/ai-workspace-services/accounts/pull/264) | OPEN；mergeable=null；unknown | 流量查询 spans、SQL 脱敏、错误与新鲜度 | 合并性尚待 GitHub 计算，不能写 CLEAN；保持未合并 |
| [Portal #462](https://github.com/ai-workspace-services/portal/pull/462) | OPEN；mergeable=true；clean | 用量加载/失败/零值/陈旧状态与 UTC 窗口 | 不是代理性能仪表盘；保持未合并 |
| [Exporter #21](https://github.com/ai-workspace-xstream/xray-exporter/pull/21) | OPEN；mergeable=true；unstable | 快照上报 envelope、探针、httptrace | 测的是上报 HTTP，不是用户 XHTTP/VLESS 路径；unstable 原因未审计，保持未合并 |
| [Playbooks #722](https://github.com/ai-workspace-infra/playbooks/pull/722) | MERGED；2026-10-21T10:59:17Z | 既有 Collector/路由修正、双面板、零流量脚本 | 部署、接收、查询、面板数据仍需分别证明 |
| [Knowledge #183](https://github.com/ai-workspace-services/knowledge/pull/183) | MERGED；2026-10-23T04:03:19Z | 历史验收与跨仓交付记录 | 文档合并不代表新增采集已部署 |

五个 OPEN 应用 PR 均继续保持不合并。本文不改变其源码或授权范围。

## 4. 工具选型结论

| 能力 | 首选方案 | 备选/扩展 | 决策与限制 |
| --- | --- | --- | --- |
| 客户端阶段耗时 | 既有客户端诊断模块 + core 实际 dial/TLS/会话钩子 | macOS curl/dig/route/mtr 手工对照 | 应用层 SDK 不能冒充真实 core 出站；各平台先做能力盘点 |
| 双端 TCP | Linux ss/TCP_INFO、nstat、node 指标；客户端原生 socket API（可用时） | Linux 节点 eBPF 连接事件 | macOS/iOS 不部署 Linux eBPF Agent；TUN 用户态栈统计需独立适配 |
| L7 入站与反代 | Caddy 现有指标/脱敏日志、Xray core 会话事件 | 受支持进程的 eBPF 明文采集 | TLS 密文不能自动解析 L7，Go TLS/h2/Unix socket 能力需 PoC |
| 临时协议分析 | 双端受控 tcpdump + Wireshark/tshark | 针对故障连接的短诊断会话 | 不默认全量抓包、不上传正文、不默认关闭网卡卸载 |
| 吞吐/Goodput | 受控大小资源与客户端有效字节统计 | 已授权临时 iperf3 单流/反向测试 | 不默认开新公网端口；并发/带宽/时间均有上限 |
| 遥测汇聚 | 既有 Vector/OTel Collector → VictoriaMetrics/Logs/Traces → Grafana | 无第二套默认存储 | 先核实实际协议与出口鉴权；不将 Prometheus pull 重复转换成多条写入 |
| DeepFlow 类能力 | 先用现有栈补 L4 连接摘要与 L7 日志/span | 隔离 Linux PoC 比较 DeepFlow/BCC 类工具 | DeepFlow 完整平台非默认新增；不能假定 Agent 可直接替代 OTel exporter 或原生写入 Victoria 系列 |

推荐先实现“客户端真实出站事件 + 节点连接摘要 + Caddy/Xray 事件 + 既有后端”，再决定是否需要 DeepFlow 完整平台。eBPF PoC 必须先证明增量价值、协议覆盖、开销和数据出口兼容；若需要额外后端，应另立架构决策，不能静默变成第二套观测中心。

## 5. 网络链路采集契约

| 点位 | 采集/实现方式 | 必须输出 | 不能推断的内容 |
| --- | --- | --- | --- |
| C0 客户端会话 | 复用诊断入口，生成短期诊断 session；单调时钟计时 | 客户端/core 版本、节点别名、网络类型、TUN 模式、连接复用/覆盖状态 | 不把一次首页请求当完整隧道验收 |
| C1 应用→TUN | 用户态 TCP 栈/core adapter 事件 | 本地接受、排队、真实出站开始事件与 connection mapping | 本地 TCP ACK 不等于远端握手 |
| C2 真实出站 | 在实际 DNS/dial/TLS 所在组件埋点；代理连接池记录复用 | DNS、dial、TLS、认证建链开始/完成/失败、首个有效响应；可得时 TCP_INFO | 另起旁路 curl 仅算主动探针，不能替代生产连接 |
| P 公网 | 同条件主动探针、双端 TCP 摘要、必要时抓包 | 终点 RTT、重传/抖动、观察点与方向、探针路径是否经过 TUN | 单端重传不能定位具体路由跳；单跳 mtr 不能证明公网无丢包 |
| E1 节点入站 | Linux socket 摘要；必要时 eBPF accept/connect/state 事件 | socket 生命周期、RTT/RTO、发送重传、字节增量、窗口、队列、进程 | 节点全局计数不能归某用户 |
| E2 Caddy | 实际版本可用 metrics、access/error 日志；受控请求 ID | TLS 错误、HTTP 状态、处理/反代耗时及 upstream 事件（有则采） | 没有独立 TLS 事件时，access duration 不能当 TLS 耗时 |
| E3 Xray | 不含凭据的会话生命周期、入站/出口 connection ID 映射 | 认证结果、会话建立、异常关闭、出口 dial/排队/有效字节（有钩子才采） | 不声称当前已有这些钩子；定制协议不默认被通用 L7 解码 |
| E4 节点出口 | 出口 socket TCP_INFO/连接事件，受控目标测试 | 发送/接收字节、重传、RTT、建连、方向吞吐及出口资源 | 不扩展至目标应用/数据库追踪 |

阶段覆盖枚举：observed、not_applicable、not_observed、failed、cancelled。复用连接的 DNS/TLS 为 not_applicable；失败阶段保留实际等待与错误，未发生阶段不填零。RTT 与 TTFB 独立命名；队列仅在明确入队/出队事件均存在时计算。

### 5.1 字段与连接关联

受控日志/span 的最小字段：schema_version、diagnostic_session_id、event_id、wall_time、monotonic_duration、clock_quality、observation_point、node_alias、environment、revision、transport、direction、stage、outcome、error_class、coverage、connection_reused、connection_ref、parent_connection_ref。

- diagnostic_session_id 是短期随机值，不含账号、设备永久标识或 VLESS UUID；只进受控日志/span，不作长期指标标签。
- 五元组/端口只在必要的受控连接明细中短期使用，落盘前脱敏；连接复用必须加生命周期，避免端口复用串联。
- 有明确 core mapping 的跨代理连接按 mapping 关联；仅有相同 IP/时间不声称强关联。NAT 后的映射不可靠时标 probable/unknown。
- HTTP/2 每请求按 stream ID（限定连接内有效）区分；XHTTP 上下行会话按协议实际关联，不随意往 VLESS 或任意用户流量注入 traceparent。
- 仅在受控 HTTP 端点或已支持的内部协议传播 W3C；其他场景使用真实事件映射/Span Links。不能伪造贯通 TCP 的连续父子 trace。

### 5.2 TCP 与吞吐指标定义

按 socket/观察点/方向记录 RTT/rttvar/RTO、bytes_sent/acked/received/retrans、segments_sent/retrans（字段存在才用）、cwnd/MSS、接收窗口、Send-Q/Recv-Q、unacked、close/reset。各平台按能力表转换，保留字段来源和单位。

客户端重传 = 客户端真实发送 socket 的重发；服务端重传 = 服务端对应发送 socket 的重发。两者都可能来自数据丢失、ACK 丢失、乱序或严重延迟。不得将客户端接收的重复段算作客户端发送重传。重传率必须说明分母及是否包含重发，使用同观察点同窗口增量；重置或分母为零标记不可计算。

Goodput = 已成功交付的有效业务字节/窗口秒数；接口速率含协议开销、重传和其他流，不与账务字节直接相等。窗口吞吐、整个会话平均吞吐、新建短流耗时分开展示。不得以 minute bucket 字节变化反推瞬时网络吞吐。

## 6. 流量统计逐跳落地契约

| 跳 | 实现与观测 | 验收 |
| --- | --- | --- |
| Vault→校验→0600 | 既有公共 resolver；只输出解析/校验结果、文件权限与内容相等布尔 | 缺/无效输入 fail-closed；保护有效配置；幂等 changed=0；不输出值/指纹 |
| 配置→Exporter→探针 | 检查实际 EnvironmentFile、push_enabled、collected_at、样本分类 | 连续两周期新鲜；禁推/空样本/真实零/陈旧分别显示 |
| Exporter→Vector | #21 上报 httptrace；push 成功、Vector receive 增量 | 同一受控 snapshot_ref 对齐；不绕过 Vector |
| Vector→Billing | 接收/送出/重试/磁盘队列/drop、脱敏错误 | 失败/恢复/重启重放有证据；投递 age 不冒充纯 queue 时间 |
| Billing→PostgreSQL | #54 阶段 spans；#55 独立事务审查 | 非零/零/重复/乱序/reset/同分钟/并发各有独立 case；不从 span 判扣费事实 |
| PostgreSQL→Accounts→Portal | #264 查询与错误分类；#462 四态和 UTC 窗口 | 同账号同窗口 DB/API/UI 核对；缺数据不伪装零；数据库只属于统计链路 |

snapshot_ref 跨重试稳定，batch_ref 属于一次投递请求；两者不参与账务幂等键、不进 metrics 标签。异步用 Span Links，Vector 缺出队事件时 queue_duration=not_observed。历史 Samples: [] 仅能证明空样本投递，不能等同账号真实零用量。

## 7. 汇聚、可视化与权限

网络：客户端受控诊断数据通过既有认证 API/允许的采集入口，校验与限流后进入现有 Collector；具体复用入口需代码核实，尚未实现，不把管理 OTLP 暴露给无鉴权客户端。节点的 metrics 保持既有 scrape 或 remote-write 路径，日志复用 Vector，新增 spans 复用 OTel；同一信号选定一个写入路径避免双计数。

流量：保持 Exporter→Vector→Billing，业务快照不是遥测副本；metrics/logs/traces 汇聚现有观测后端，PostgreSQL 保持账务权威。

Grafana 复用网络/统计两面板，网络面板增加客户端阶段、TUN 真实出站、双端 L4、节点入站/出口、采集覆盖/健康六个视图；统计面板展示凭据阶段结果、快照 age、Vector 队列/丢弃、Billing 结果及 DB/API/UI 新鲜度。面板以 node/transport/environment/revision/窗口互链，精确 session/trace 下钻只在受控明细中进行。

低基数指标标签限阶段、结果、节点、环境、方向、传输及有限错误类别；不包含账号、邮件、原始 URL/IP、UUID、五元组、trace/session/snapshot ID。诊断关闭后停止细粒度采样；默认不抓包。日志/trace 诊断保留 7 天、连接明细建议 24 小时仅为待容量/隐私审阅的初始方案。导出失败必须有界且不影响代理和账务，不能承诺“完全零开销”。

## 8. 任务拆解与依赖

下列 owner 为责任组件，不指派个人；仓库精确路径在实施前核对。未创建远端任务、未更新 Project 状态。

| ID | 任务/责任组件 | 交付物 | 依赖 | 当前进展 | 通过条件 |
| --- | --- | --- | --- | --- | --- |
| PLAN-00 | Knowledge / 需求固化 | 两链基准、范围、字段、PR 映射、任务正文 | 用户确认基准 | 本文已本地编写 | 链接/格式检查；后续形成可追溯 Issue |
| NET-01 | 客户端/core 能力盘点 | macOS/iOS/Android/其他平台钩子矩阵，区分原生/用户态 TCP | PLAN-00 | PLANNED | 每个阶段给实际代码位置、可得字段与 NOT_SUPPORTED 项 |
| NET-02 | 客户端阶段事件 | session/coverage、DNS/dial/TLS/首响应/取消/复用事件 | NET-01 | PLANNED | 各故障 fixture≥20 次分类正确，无缺失填零 |
| NET-03 | TUN/core 真实出站映射 | local accept→outbound→node 映射和阶段耗时 | NET-01 | PLANNED | 代理本地 ACK 不被计为远端 RTT；直连/TUN 对照可复现 |
| NET-04 | Linux 节点 L4 摘要 | ss/TCP_INFO 原型、双方向计数与重置处理 | PLAN-00 | PLANNED | 受控丢包 fixture 与内核/抓包口径对照；主机量不冒充连接量 |
| NET-05 | Caddy/Xray 入站与出口 | 脱敏事件、upstream/会话/出口 mapping | NET-03/04 | PLANNED | TLS/认证/反代/出口分别注入延迟并正确定位，不含数据库 |
| NET-06 | 吞吐/双端诊断工具 | 限时限速脚本、Goodput、tcpdump/Wireshark 操作单 | NET-03/04 | 手工方法已记录，脚本 NOT_RUN | 上传/下载单流可复现，采集 drop 和 offload 边界明确 |
| NET-07 | eBPF/DeepFlow 适配 PoC | 支持矩阵、内核权限、Go TLS/h2/UDS、资源/输出对照 | NET-04/05 | PLANNED，非前置阻塞 | 证明新增价值与既有后端兼容；否则不引入 |
| OBS-01 | Playbooks/观测后端 | 固定版本 pipeline、数据契约、网络面板扩展 | NET-02/04/05 | #722 MERGED；新增扩展未实现 | 接收→存储→查询→面板逐一有数据证据 |
| FLOW-01 | Exporter | #21 上报探针/envelope | 既有契约 | CODE_REVIEW，保持未合并 | 审计 unstable 原因；真实固定 Vector 重试/重启验证 |
| FLOW-02 | Billing | #54 纯观测 | FLOW-01/OBS-01 | CODE_REVIEW，保持未合并 | W3C/Links、脱敏、有界队列，账务结果不变 |
| FLOW-03 | Accounts/Portal | #264/#462 查询/四态 | FLOW-02 | CODE_REVIEW，保持未合并 | 同窗口 API/UI 对照与错误/陈旧态 |
| FLOW-04 | Billing 独立账务 | #55 事务及幂等 | 独立账务评审 | CODE_REVIEW，保持未合并 | 一次性 PG 崩溃/并发/重放；不阻塞网络分析 PoC |
| FLOW-05 | SG 历史断链复核 | 接收→投递→桶/新鲜度定位 | 目标/访问核实 | 10-21 历史 BLOCKED，当前未复核 | 先复核断点，不以重启掩盖；未修复不报全节点 PASS |
| QA-01 | 隔离验收与开销 | 故障 harness、复测报告、诊断开关回退 | 对应 NET/FLOW | PLANNED | 下节矩阵通过，未跑/skip 明示 |
| REL-01 | 发布交付记录 | PR→制品→GitOps pin→UAT→运行证据 | 独立后续授权 | NOT_RUN | 不可变 ref/digest、回滚明确；本轮不合并/部署 |

推荐次序：PLAN-00 → NET-01 → NET-02/03 与 NET-04 分别完成 → NET-05/06 → OBS-01 扩展 → QA-01；NET-07 为可选增强。流量 PR 独立保持审阅，不能等它们全部合并才开始网络能力盘点，也不能将 #55 当作网络测量能力。

## 9. 统一验收矩阵

故障注入限隔离 fixture/UAT，生产只做授权的有限探测；不得修改生产网络或证书制造故障。

| 场景 | 要区分的证据 | 成功条件 |
| --- | --- | --- |
| DNS 失败/慢 | resolve 与后续未发生阶段 | 固定 IP 对照；失败不变成零延迟 |
| TUN 接受快、真实 dial 慢 | local_accept 与 outbound_connect | 人为延迟只落入真实出站，mtr 本地应答有盲区标记 |
| TCP 丢包/乱序/ACK 延迟 | 双端重传、RTT/RTO、采集丢包 | 能指出观察方向及不确定性，不虚构丢包跳点 |
| TLS 慢/不可信 | TCP 正常、TLS 等待或证书失败 | 与受控本机 TLS 对照，不归到 XHTTP 认证 |
| 复用/HTTP2/上下行分离 | connection/stream/session 映射 | 不重复算 DNS/TLS，不按连接混合请求延迟 |
| 节点排队/出口慢 | 明确队列事件、出口 dial/RTT/窗口 | 不减总耗时猜队列，不引入数据库归因 |
| 吞吐受限 | Goodput/线速/窗口/重传/CPU | 单流/多流、上传/下载分别报告；不等同账务速率 |
| 休眠/取消/切网/重连 | session 生命周期/coverage | 不产生负耗时或无限悬挂 span |
| 统计禁推/空/零/陈旧 | push_enabled、样本/时间/链路错误 | 四类分别验收；空样本不算真实零 |
| Vector 重试/断连重启 | ref/Links、队列/投递/age | 未测出队则纯排队耗时 unknown；不改变计费键 |
| DB/API/UI 展示 | 同账号同 UTC 窗口 | 仅用于统计链路；失败不能显示 0 B |
| 后端不可达/采集过载 | SDK/Agent 队列、drop、业务对照 | 有界且不中断代理/账务，采集缺口可见 |

阶段分类 fixture 每场景建议至少 20 次，全部正确；这是分类门槛，不是尾延迟统计样本量。开销初始预算：同负载 p95 额外延迟≤5%、CPU 增加≤5 个百分点、应用 SDK RSS 增量≤32 MiB；节点 Agent 单独制定资源预算，不套用 SDK 限额。上述均为提议门槛、未实测。时钟偏差建议≤100 ms，超限不算跨机单向差；毫秒级细分需更严同步或同端测量。

判定 PASS 需绑定代码 SHA、制品 digest、配置版本、节点/窗口、命令/查询、退出码、skip 数及实际数据。历史 350 轮总耗时 disabled=9.20 ms、enabled=25.87 ms 仅支持该 fixture 的正确性/有界队列证据，不证明 p95 开销≤5%或持续十分钟故障验收。

## 10. 当前结论、校正与实施前置

已有基础：双链路方案/历史回执、五个待审应用 PR、已合并的中心配置与文档 PR，以及 Mac 双节点诊断案例。尚缺：真实出站映射、逐连接双端 L4、Caddy/Xray/出口事件、统一自动化诊断、当前部署与开销证据。

历史手册中的下列表述不得当执行指令：

- “所有 PR 均保持打开”应改为五个 OPEN 应用 PR 保持不合并，#722/#183 已合并。
- SG 的 404 根因、固定 SSH 用户、8686 端口角色和健康 URL 未在本轮验证。8686 不能自动当快照 HTTP source；先查实际绑定和配置，禁止打印含 token 的配置正文。
- 容器内 127.0.0.1:4318 是否正确取决于网络模式和 Collector 所在命名空间，不能直接照抄注入。
- 不默认重启 Caddy；由 Playbook 确认 validate/reload/必要重启策略。清空 OTLP endpoint 的 noop 行为需按服务实现验证，不能承诺完全消除开销。
- “统计历史 PASS”不证明当前用户网络好；“TLS 慢”不证明用量不上报。两链只在相同节点/transport/版本/窗口下作关联，不互相代替验收。

后续实现先为上述任务建立带验收条件的 Issue 并关联 Project #4，再进入隔离实现/PR 流程；本轮只交付规划文档，无远端任务或生产变更。

## 11. 工具依据

2026-10-23 核对官方资料；具体落地必须固定实际版本，不以最新文档替代现场能力：

- [OTel Collector Receivers](https://opentelemetry.io/docs/collector/components/receiver/) 与 [Agent 模式](https://opentelemetry.io/docs/collector/deploy/agent/)：用于核对 receiver/exporter 与既有汇聚契约。
- [DeepFlow 产品与平台范围](https://deepflow.io/docs/about/editions/) 与 [Agent 配置源码](https://github.com/deepflowio/deepflow/blob/main/server/agent_config/example.yaml)：Linux 采集能力及独立平台边界；不代表 macOS/iOS 支持或直接对接现有后端已验证。
- [iperf3 官方调用说明](https://software.es.net/iperf/invoking.html)：正反向、并发、JSON 与速率参数；实际压测另定目标/限额。
- [Linux TCP/TCP_INFO](https://man7.org/linux/man-pages/man7/tcp.7.html)：内核观测字段基础。

## 相关文档

- [实施与交付交接手册](dual-link-observability-handoff-handbook-20261023.md)：交付顺序、现有进展和历史说明校正。
- [全链路性能分析白皮书](network-full-path-performance-whitepaper.zh.md)：分层方法、TCP 重传、RTT、窗口、吞吐与 L4/L7 分析。
- [双入口实测记录](network-performance-jp-comparison-20261023.zh.md)：实际数据、根因排序与待补证据。
