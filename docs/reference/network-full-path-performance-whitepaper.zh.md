---
title: 全链路网络性能分析参考白皮书：DNS、TCP、TLS、L4/L7 与 XHTTP
description: 从客户端路由到服务器及隧道出口，定义双端重传、吞吐量、协议时延与 DeepFlow 类观测的证据口径。
slug: network-full-path-performance-whitepaper
lang: zh
date: 2026-10-23
version: "1.0"
status: diagnostic-reference-partial-evidence
category: reference
tags:
  - performance
  - tcp
  - observability
  - xhttp
  - deepflow
---

# 全链路网络性能分析参考白皮书

## 范围补充与实施入口（2026-10-23）

网络主链路固定为 **客户端 → 本地 TUN/真实出站 → 公网路径 → 代理节点入站与出口**，数据库不属于网络延迟归因。下文通用工具表中的数据库/应用追踪内容仅适用于独立流量统计链路。

流量统计链路固定为 **Vault → 配置校验 → 0600 凭据文件 → Exporter → 快照探针 → Vector → Billing → PostgreSQL → Accounts → Portal**。两链独立测量、按节点/transport/版本/窗口关联。

工具选型、客户端/core 与代理节点采集契约、PR 进展、任务拆解和验收见[双链路深化实施规划](dual-link-client-edge-observability-implementation-plan.zh.md)。既有 Exporter httptrace 仅覆盖快照上报 HTTP，不等于用户代理链路。

[性能调优技术白皮书](performance-optimization-whitepaper.zh.md) · [2026-10-23 双入口实测记录](network-performance-jp-comparison-20261023.zh.md)

本文规定从客户端到节点、反向代理、协议隧道及业务出口的分析方法。命令是操作参考，不表示已经执行；部署采集 Agent、调整分流、抓取生产报文及压测需另行明确目标、采集窗口、权限与数据保留范围。本次仅执行了低频客户端探测，未修改生产配置。

## 1. 链路与采集位置

```text
业务应用 → 客户端 TCP/TUN → 代理进程真实出站连接 → 上游/公网
 → 节点 TCP:443 → Caddy TLS/HTTP → Xray XHTTP/VLESS
 → 节点出站 TCP → 业务目标
```

每个终止 TCP 的代理都产生独立连接。不同连接的序列号、RTT、窗口及重传计数不能直接拼成一个端到端连接；NAT、连接池、HTTP/2 多路复用也会改变关联关系。

至少区分四个观测点：客户端应用侧、客户端真实出口侧、节点入站侧、节点业务出口侧。TUN 内的 TCP 建连成功可能只是本地代理接受连接；必须查看代理真实出口、选择的节点和规则。不能把本地亚毫秒响应当作跨境 RTT。

所有记录带测试 ID、时间/时区、网络及 TUN 状态、目标域名/SNI、实际 IP、接口、协议、工具版本、样本数、超时上限和方向。单向时延需要可量化的时钟同步误差；未同步时优先比较同端时间差及双端序列号。

## 2. 分层工具、操作与指标

| 层次 | 工具/操作 | 观察指标 | 解释边界 |
| --- | --- | --- | --- |
| DNS | dig A/AAAA；scutil --dns | 响应 IP、解析耗时、失败率、缓存差异 | dig 与系统解析器不一定走相同路径；无 AAAA 与 IPv6 网络不可达分别记录 |
| 路由 | route -n get IP；scutil --nwi | 出口接口、IPv6 状态、TUN/代理路径 | --noproxy 不绕过系统 TUN |
| TCP 建连 | nc；curl；双端抓包 | SYN/SYN-ACK/ACK、握手成功率、重传及耗时 | TUN 本地 TCP 完成不代表远端建立完成 |
| 路由质量 | ping、mtr、traceroute | 终点丢包、RTT、抖动及路径变化 | 中间跳限速/不回复不能直接解释为转发丢包 |
| TLS | curl、握手抓包、服务端本机对照 | 握手成功率、ClientHello/ServerHello 间隔、证书错误 | TLS 等待可能含代理真实出站建连；不能直接等同密码学 CPU 耗时 |
| HTTP | curl、Caddy access log、OTel | 状态码、TTFB、请求耗时、请求/响应字节 | TTFB 含网络、传输和服务处理；access log 通常不覆盖完整 TLS 握手 |
| 主机 | ss、nstat、ip -s link、系统/进程指标 | socket RTT/重传/队列、网卡 drop、CPU/内存/重启 | 主机总计数不能直接归到某域名或某用户 |
| XHTTP/VLESS | 真实客户端、Xray/Caddy 事件 | 认证、上下行建链、首个有效业务响应、断流/重连 | GET /split/ 或 HTTP 400 不能证明认证后的隧道健康 |
| 出口业务 | 经隧道访问受控目标 | 业务成功率、首响应、有效吞吐 | 需分别测节点到业务目标和客户端到节点 |

## 3. 客户端最小测量

macOS 示例；替换为获授权的目标。首次和重复 DNS 分开记录，避免将缓存命中解释为权威 DNS 性能。

```bash
h=target.example.com
ip=203.0.113.10

dig +time=3 +tries=1 "$h" A
dig +time=3 +tries=1 "$h" AAAA
scutil --dns
scutil --nwi
route -n get "$ip"
nc -vz -G 5 "$ip" 443
ping -c 10 "$ip"
sudo /opt/homebrew/sbin/mtr -n -r -c 20 -T -P 443 "$ip"
traceroute -n -m 16 -q 1 -w 1 "$ip"

# 删除 --resolve 参数后重复一次，比较普通解析与固定 IP。
curl --noproxy '*' --resolve "$h:443:$ip" \
  --connect-timeout 8 --max-time 15 -sS -o /dev/null \
  -w 'ip=%{remote_ip} code=%{http_code} http=%{http_version} dns=%{time_namelookup} tcp=%{time_connect} tls=%{time_appconnect} first=%{time_starttransfer} total=%{time_total}\n' \
  "https://$h/"
```

curl 时间单位为秒，均从请求开始累计：DNS = namelookup；TCP 阶段 = connect − namelookup；TLS 阶段 = appconnect − connect；TLS 完成至首字节 = starttransfer − appconnect；响应体接收 = total − starttransfer。未完成阶段的零值不能作为实际零耗时。仅在相应阶段成功完成、无重定向等混杂因素时使用以上分解。

分别测试 TUN 开启、目标绕过 TUN、其他网络；固定 IP/SNI、请求路径、协议、超时和样本数。实际绕过应由路由与代理真实出站记录共同验证。新连接与复用连接、HTTP/1.1 与 HTTP/2 分组比较。IPv6 在存在有效 AAAA 且客户端可达时才有可比较数据。

## 4. TCP 底层：双端重传、窗口与拥塞

### 4.1 Linux 节点采样

以下为只读示例。确认服务名和连接方向；记录多个时间点，不以单帧快照判定趋势。

```bash
date -u
uptime
free -m
sudo ss -lntp
sudo ss -lxnp
sudo ss -tinmp '( sport = :443 or dport = :443 )'
nstat -az
ip -s link
systemctl show caddy xray -p ActiveState -p SubState -p NRestarts -p MemoryCurrent
sudo journalctl -u caddy -u xray --since '15 minutes ago' --no-pager -n 150
```

`ss -i` 字段随内核/iproute2 版本和连接状态变化，缺少字段标记未观测。macOS 的 `netstat -s -p tcp` 可提供主机累计 TCP 统计，但不能替代 Linux ss 或逐连接指标；macOS 客户端可用受控抓包及应用/代理遥测补齐。

| 指标 | 观测/计算 | 诊断意义与限制 |
| --- | --- | --- |
| RTT/rttvar、RTO | 发送端 socket TCP_INFO/ss | 区分稳定高 RTT、抖动与超时退避；不是纯服务器处理时间 |
| 重传段/重传字节 | 双端发送 socket 计数器窗口增量 | 客户端重传指客户端重发自己发送的数据；服务端同理，不能据此直接定位丢包位置 |
| 重传率 | Δ重传段/Δ发送段，或 Δ重传字节/Δ发送字节 | 明确分母是否含重传、数据/控制包范围和观察点；分母为零时不计算；不同口径不混比 |
| cwnd、ssthresh、MSS | ss/TCP_INFO，按实现确认单位 | 拥塞窗口与接收窗口共同限制在途量；cwnd 通常以段表示，不能直接当字节 |
| 接收窗口/Zero Window | 双端包头窗口、socket 字段 | 接收端读取/缓冲压力线索；区分 TCP 窗口与 HTTP/2 流控 |
| Send-Q/Recv-Q、unacked | 连续采样 | 队列积压需结合应用读写、ACK 与窗口；单次非零不构成异常 |
| out-of-order、Dup ACK、SACK | 抓包/协议分析 | 可能为丢包、乱序、ACK 路径问题或采集缺口；分析器标签不是最终根因 |
| TCP timeout/reset/握手失败 | socket、内核计数、双端报文 | 区分建立、传输、关闭阶段；RST 来源需观察点佐证 |
| 网卡 drop/error、softnet、CPU | 节点/接口计数增量 | 区分主机接收压力和公网丢包；检查采集本身是否丢包 |

### 4.2 如何定位重传方向

客户端显示重传，说明发送数据未及时得到确认；可能是正向数据丢失、反向 ACK 丢失、乱序、严重延迟或本机排队。服务端重传也遵循相同逻辑。双端抓包按相同 TCP 段序列号/长度和 ACK/SACK 关联：发送端看见原段而接收端未见，是两观察点之间缺失的线索，仍需排除抓包丢失及卸载差异。经 TUN/代理终止后应分别关联每段连接，不能直接跨代理匹配序列号。

### 4.3 受控抓包与 Wireshark/tshark

先确认真实出口接口。以下是待执行模板，不会自动启动抓包：

```bash
# 双端分别替换接口/IP；约定采集 120 秒并手动结束，使用环形文件限制体积。
# snaplen=128 仅减少载荷，仍可能含应用信息；pcap 留在受控目录。
sudo tcpdump -i INTERFACE -nn -s 128 -U -C 10 -W 3 \
  -w tcp-diagnostic.pcap 'host 203.0.113.10 and tcp port 443'
# 到约定时间 Ctrl-C，记录 tcpdump 的 captured / dropped 统计。
```

Wireshark 显示过滤器：`tcp.analysis.retransmission`、`tcp.analysis.fast_retransmission`、`tcp.analysis.spurious_retransmission`、`tcp.analysis.out_of_order`、`tcp.analysis.duplicate_ack`、`tcp.analysis.zero_window`、`tcp.flags.reset == 1`。用 `tcp.stream` 分流，结合时序图、ACK RTT 和吞吐图分析，不能把这些启发式标签视为精确的内核重传计数。

TSO/GSO/GRO/LRO、checksum offload 可能造成超大段、看似坏校验和及不同分段。不要据此直接认定线上坏包，也不要为诊断默认关闭生产卸载。记录抓包位置、截断长度和采集丢包。仅有包头无法解析完整 L7；扩大采集范围前明确数据边界。

## 5. 吞吐量、Goodput 与容量

| 测量 | 定义 | 必须控制的变量 |
| --- | --- | --- |
| 线速/接口流量 | 接口统计的字节增量 × 8 / 窗口秒数 | 包含重传、协议开销及其他业务；不等于有效吞吐 |
| TCP 传输吞吐 | 明确观察点的 TCP 传输速率 | 重传计入方式、方向、并发、窗口、时长 |
| 业务 Goodput | 成功交付的有效业务字节 / 耗时 | TLS/隧道开销、压缩、缓存、失败/重试是否计入 |
| 请求容量 | RPS、并发、成功率及 P50/P95/P99 | 请求体/响应体、连接复用、业务类型、超时和失败样本 |

粗略窗口上限：吞吐 ≤ min(cwnd 字节数, 接收窗口字节数) / RTT；仅是窗口约束近似，还受带宽、pacing、CPU、应用供应和协议流控影响。目标在途量可按 BDP = 带宽(bit/s) × RTT(s) / 8 估算，不能据此直接调整生产 buffer。

`iperf3` 只在获授权、已有或专门安排的测试端点运行，不能直接对 Caddy 443 使用，也不默认开放生产端口：

```bash
# 以下服务端已存在且已授权；每组 20 秒，约定最大带宽和窗口。
iperf3 -c TEST_ENDPOINT -p TEST_PORT -t 20 -P 1 -J
iperf3 -c TEST_ENDPOINT -p TEST_PORT -t 20 -P 1 -R -J
# 多流仅用于后续容量比较，不能替代单流用户体验。
```

以上命令未设置通用安全带宽上限，执行前按当前 iperf3 版本配置已约定的限速；不在繁忙生产上直接执行。比较直连/隧道、上传/下载、单流/多流；保留发送端和接收端报告、CPU、TCP 重传及速率曲线。短流首响应慢而长流吞吐正常，优先查建链/握手；单流慢而多流快可能涉及窗口/丢包/单连接约束，仍需指标佐证。固定业务文件测试应使用获授权资源并记录大小、校验结果及缓存状态。

## 6. TLS、Caddy 和 Xray 的分界

Caddy TLS 终止异常只是候选原因。验证顺序：客户端固定 IP/SNI → 绕过 TUN 对照 → 服务器本机同 SNI TLS → 双端握手时序 → Caddy CPU/错误及生命周期 → Xray upstream/认证与业务出口。

服务端本机示例，先确认监听地址；若 Caddy 仅监听特定地址，替换回环地址：

```bash
h=target.example.com
curl --noproxy '*' --resolve "$h:443:127.0.0.1" \
  --connect-timeout 5 --max-time 10 -sS -o /dev/null \
  -w 'tcp=%{time_connect} tls=%{time_appconnect} first=%{time_starttransfer}\n' \
  "https://$h/"
```

本机快、远端慢提示路径/客户端问题，但不能单独排除服务端外部监听、防火墙或不同证书/路由条件。本机也慢，再结合资源和握手事件分析；不要直接调密码套件或重启。SSH 也慢说明现象不限 HTTPS，但 SSH 仍可能有独立配置问题，不能据此彻底排除 Caddy。

TLS 1.3 后续握手消息及应用数据加密，纯网络抓包不一定能看见完整握手边界；不要以一个 ServerHello 等同完整握手完成。XHTTP 的 HTTP/2 复用、上下行会话和 VLESS 认证需要真实客户端及服务端日志关联；TLS 正常不等于隧道正常。

## 7. DeepFlow 类 L4/L7 观测方案

此节是能力设计，不表示当前已安装 DeepFlow Agent、已启用相关采集或已取得指标。部署前核对 Agent/Server 版本、内核与 eBPF 支持、进程语言/加密库、协议支持列表、资源开销和权限。

| 层次 | 目标数据 | 关键关联字段 | 验收条件 |
| --- | --- | --- | --- |
| L4 流 | TCP 建立/关闭、方向流量、RTT、重传、异常 | 观察点、时间窗、连接生命周期、五元组、进程/容器/节点 | 与同端 ss/受控抓包在定义一致的窗口内对照 |
| L7 请求 | 协议、请求/响应关联、状态、时延、字节量 | 协议请求 ID、连接/流 ID、服务和进程身份 | 受控请求能被关联，失败/超时单列，明确采样比例 |
| 应用追踪 | Caddy upstream、Xray 会话、业务依赖 | trace/span 或受控测试 ID、时间、连接映射 | 能解释用户一次请求在哪段等待，不能仅有节点流量总图 |
| 采集健康 | Agent CPU/内存、丢弃、队列、解码失败、指标延迟 | Agent 版本、采集点、最后样本时间 | 无数据与零错误明确区分；过载和盲区可见 |

TLS 密文的包头可以支持 L4 分析，不能默认得到 HTTP URL、状态码或完整请求时延。L7 需要可见的明文侧、受支持的进程/eBPF 采集、应用日志或 OTel。对 Caddy/Go TLS 的支持必须核对实际版本和采集方式，不能假设常见 OpenSSL hook 自动适用。Unix socket/h2c 链路也不能默认被网卡抓包或所有 Agent 覆盖。

HTTP/2 多路复用必须按 stream 关联请求；仅按连接汇总会掩盖请求差异。自定义 XHTTP/VLESS 未被解析时，只报告可观测 L4/TLS/HTTP 和应用事件，不能声称已经完成 VLESS 全协议分析。

Grafana/VictoriaMetrics 建议分别呈现：DNS/握手成功率与耗时、各观察点 L4 RTT/重传/流量、L7 状态及分位延迟、节点资源、采集健康、发布/重启标记。先确认真实 metric 名称和标签，再写查询；不要把下表理解为现网已存在的指标。

- 按节点/方向计算 counter 的 rate/increase，并处理重置；瞬时字段用 gauge。
- 重传率用同端同窗口计数之比；跨节点先汇总分子分母，不直接平均百分比。
- P95/P99 用可聚合直方图或原始分布计算；不平均分位数。低样本窗口不形成稳定尾延迟结论。
- 请求、失败、超时均保留；不要仅统计成功请求而隐藏失败延迟。
- 高基数五元组/用户/URL 明细放受控流日志；长期指标只保留有限节点、服务、方向和错误类型标签。

## 8. 根因判定与最小修复顺序

| 证据组合 | 优先验证 | 最小行动 |
| --- | --- | --- |
| DNS 慢，固定 IP 快 | DNS/TUN resolver | 对照解析路径；不要先改服务器 |
| TUN 内 TCP 亚毫秒、TLS 卡顿 | 真实出站建立、代理规则/上游 | 目标绕过 TUN 并验证实际出口 |
| 双端 RTT/重传同步异常 | 方向数据/ACK、路径拥塞 | 双端包头对照及其他网络测试 |
| Zero Window/Recv-Q 长期积压 | 接收应用读取、缓冲压力 | 查接收进程资源与处理，不直接扩 buffer |
| TLS 本机也慢且 CPU/错误相关 | Caddy/主机 | 分析握手资源、事件与配置版本，再提最小变更 |
| TLS 快、upstream/认证慢 | Caddy→Xray/认证服务 | 对齐错误、socket 与依赖指标 |
| 入站正常、节点出口慢 | 出口网络/业务依赖 | 单独测节点到业务目标 |

交付必须包括：已观测事实、根因排序及可否定条件、未观测字段、最小修复提案、回滚与复测方法。检查/构建/进程 active 不替代真实用户路径验收。无需证据时不引入新的 relay、升级硬件或调整 TCP 参数。

## 9. 官方参考与核对范围

以下资料于 2026-10-23 查阅，仅用于方法和能力边界，不是当前环境部署证据：

- [Linux TCP 与 TCP_INFO](https://man7.org/linux/man-pages/man7/tcp.7.html)。
- [DeepFlow Agent 配置源码](https://github.com/deepflowio/deepflow/blob/main/server/agent_config/example.yaml)：配置随版本变化，实施应固定实际 release/commit。
- [DeepFlow L7 协议与调用日志概览](https://web.deepflow.io/embedded-docs/features/l7-protocols/overview)。

## 相关文档

- [深化实施规划](dual-link-client-edge-observability-implementation-plan.zh.md)：工具选型、采集契约、任务拆解与验收条件。
- [实施与交付交接手册](dual-link-observability-handoff-handbook-20261023.md)：交付顺序、现有进展和历史说明校正。
- [双入口实测记录](network-performance-jp-comparison-20261023.zh.md)：实际数据、根因排序与待补证据。
