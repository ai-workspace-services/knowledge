---
title: JP 双入口网络与 TLS 性能诊断记录（2026-10-23）
description: 当前 TUN 路径下两个入口的 DNS、TLS、SSH 与 mtr 观测，根因仍待直连和服务器侧证据确认。
slug: network-performance-jp-comparison-20261023
lang: zh
date: 2026-10-23
status: partial-evidence-root-cause-unconfirmed
category: reference
tags:
  - performance
  - tcp
  - tls
  - xconnect
---

# JP 双入口网络与 TLS 性能诊断记录

[全链路网络性能分析参考白皮书](network-full-path-performance-whitepaper.zh.md) · [性能调优技术白皮书](performance-optimization-whitepaper.zh.md)

## 1. 范围与证据来源

2026-10-23 20:07–20:15，Asia/Shanghai。来源为本次会话中在用户 macOS 终端执行的只读命令及用户粘贴的 mtr 输出。少量探测并行执行，样本量有限，不适合作容量或长期 SLO 结论。未修改生产配置；本机经用户授权安装 mtr 0.96。目标映射仅为本窗口观测，未核实两个 IP 是否对应独立主机、同一部署或不同入口角色。

| 域名 | 观测 IPv4 |
| --- | --- |
| jp-xconnect-01.svc.plus | 35.79.83.48 |
| jp-xconnect.svc.plus | 54.199.179.163 |

客户端目标 IP 和默认路由经过 utun7，scutil 显示 VPN server 为 127.0.0.1；本机未显示可用 IPv6 状态，两域名查询均未返回 AAAA。curl 使用 --noproxy '*'，仍经过系统 TUN。

## 2. 初轮数据：20:07–20:11

| 项目 | 实际观测 | 限制 |
| --- | --- | --- |
| 01 域名 DNS | 首次 3180 ms，随后 dig 0–1 ms；curl 存在解析超时 | 不能将缓存结果当权威解析耗时 |
| IPv6 请求 | 解析阶段约 5 秒超时，未连接 | 未测得 IPv6 TCP/TLS 性能 |
| 01 IPv4 HTTPS / | 5 次仅 1 次成功，HTTP/2 200，总计 7.040 s | 其他请求为 DNS、TLS 或响应等待超时 |
| 成功样本 | DNS 1.578 ms；TCP 阶段 0.311 ms；TLS 阶段 6472.302 ms；TLS 后首字节等待 566.147 ms | TCP 可能由 TUN 本地终止；TLS 阶段不等于 Caddy CPU 时间 |
| 01 固定 IP/SNI | /、/split/ 各 3 次，6 次均约 5 秒 TLS 超时 | 未进入 XHTTP/VLESS 认证测试 |
| 01 ping | 10 次，0% 丢包，平均 0.632 ms | 不代表跨境真实 RTT |
| UDP traceroute | 前 14 跳无响应 | 不能直接认定路径丢包 |
| TCP traceroute | pcap_activate 失败 | 无可用路由结果 |
| jp 固定 IP/SNI HTTPS | TLS 等待约 8 秒超时 | 不能仅凭此认定 Caddy 故障 |

SSH 用户最初使用默认本机用户，后按用户提供入口改为 ubuntu；两个目标均补测 ubuntu。认证前超时未形成任何服务器侧诊断证据。尝试 grafana.svc.plus/api/health 时 DNS 超时，该候选入口未验证为有效监控入口，也未取得 VictoriaMetrics 数据。

## 3. 复测：约 20:13

每个域名固定此前 IP、保留 SNI 和证书验证，3 次新 curl 进程。connect-timeout=8 秒、max-time=12 秒。

| 目标/样本 | TCP 阶段 ms | TLS 阶段 ms | HTTP/首字节后续 | 总耗时 ms |
| --- | ---: | ---: | --- | ---: |
| 01 / 1 | 0.383 | 265.317 | HTTP/2 200；TLS 后至首字节 320.052 ms | 585.973 |
| 01 / 2 | 1.103 | 274.608 | HTTP/2 200；TLS 后至首字节 390.139 ms | 665.939 |
| 01 / 3 | 0.358 | 6810.725 | TLS 完成后未取得首字节，最终超时 | 12005.615 |
| jp / 1 | 0.239 | 未完成 | SSL connection timeout | 8005.505 |
| jp / 2 | 0.359 | 未完成 | SSL connection timeout | 8006.472 |
| jp / 3 | 0.937 | 未完成 | SSL connection timeout | 8006.645 |

本轮 01 的 A 查询也发生超时；jp 的 A 查询返回 54.199.179.163、耗时 0 ms。ubuntu SSH 固定 IP 复测两目标均在 banner 阶段超时，未进入认证。

## 4. 用户提供的 mtr 数据

命令为 TCP 443、20 个周期、数字地址报告模式，均在 TUN 开启的原网络中：

| 开始时间 +08:00 | 目标 | 跳数 | Snt | Loss | Avg ms | Best ms | Worst ms | StDev ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20:15:23 | 35.79.83.48 | 1 | 20 | 0.0% | 0.6 | 0.3 | 1.3 | 0.2 |
| 20:15:34 | 54.199.179.163 | 1 | 20 | 0.0% | 0.9 | 0.4 | 4.9 | 1.0 |

结合 utun7 路由，单跳亚毫秒结果强烈提示本地 TUN/代理应答，不能证明远端真实路径无丢包。尚无真实公网逐跳路径或两端 TCP 重传数据。此前“未安装 mtr”的状态仅适用于最初探测；后续已安装，并由用户以 sudo 完成上述测试。

## 5. 根因排序与否定条件

1. **TUN 真实出站/所选上游异常，优先假设。** 支持：本地极快 TCP 与数秒 TLS 等待不匹配，SSH 也慢；否定/收敛方法：对两 IP 绕过 TUN 并确认真实路径，重复同条件测量。
2. **DNS 间歇迟滞，已观测的并行问题。** 固定 IP 后仍慢，说明不是唯一原因。
3. **目标路径或服务端 TLS/资源异常，未排除。** 两入口表现不同，但未取得服务器指标；不能以 SSH 超时完全排除 Caddy 的独立问题。
4. **XHTTP/VLESS 建链、认证与吞吐问题，未观测。** HTTP 首页和非认证 /split/ 不等价于真实隧道。

“TLS 6472 ms”指 curl TCP 完成到 TLS 完成的差值，可能含 TUN 接受本地连接后建立真实远端连接的等待、路径往返/重传及服务端处理。当前不支持“Caddy TLS 卸载导致延迟”的根因结论。

## 6. 下一轮证据与最小行动

| 优先级 | 操作 | 验收/观察 |
| --- | --- | --- |
| P1 | 两目标绕过 TUN 与现路径对照 | 记录真实出口，至少多次重复，失败/超时保留 |
| P1 | 既有授权 SSH 会话只读检查 | 资源、监听、服务状态、重启、Caddy/Xray 事件 |
| P1 | 服务器本机同 SNI curl | 分离客户端路径与服务端 TLS，确认监听条件一致 |
| P2 | 双端 TCP_INFO/ss 和受控抓包 | 客户端/服务端发送重传、RTT/RTO、窗口、队列及采集丢包 |
| P2 | 受控上传/下载/iperf3 | 单流与多流、Goodput、重传、CPU、方向；先约定负载 |
| P2 | DeepFlow 类 Agent/日志/OTel 方案核对 | 区分 L4 密文可见性、TLS 明文采集能力、L7 请求及隧道盲区 |

不依据现有证据调整生产 TCP buffer、Caddy TLS 参数、Xray 配置、实例规格或新增 Relay。所有指标为空缺时标记未观测，不能记为零重传、正常吞吐或服务健康。

## 7. 从实测缺口到实施任务

后续按[双链路深化实施规划](dual-link-client-edge-observability-implementation-plan.zh.md)执行：本例的 TUN 假快 TCP 映射到 NET-03，双端重传缺口映射到 NET-04，TLS/Caddy/Xray/出口边界映射到 NET-05，吞吐与抓包映射到 NET-06；当前均未获得运行验收。

2026-10-21 的快照投递/分钟桶历史回执只能说明对应窗口的流量统计链路状态，不能解释本例 2026-10-23 用户到代理出口的 TLS 性能。数据库仅属于统计链路。

## 相关文档

- [深化实施规划](dual-link-client-edge-observability-implementation-plan.zh.md)：工具选型、采集契约、任务拆解与验收条件。
- [实施与交付交接手册](dual-link-observability-handoff-handbook-20261023.md)：交付顺序、现有进展和历史说明校正。
- [全链路性能分析白皮书](network-full-path-performance-whitepaper.zh.md)：分层方法、TCP 重传、RTT、窗口、吞吐与 L4/L7 分析。
