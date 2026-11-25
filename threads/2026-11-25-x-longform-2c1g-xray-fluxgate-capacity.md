---
title: "只用 2C1G（$7/月）AWS Lightsail，如何扛住 500 并发不 OOM？—— 边缘代理节点单体聚合、Vector/Journald 极限瘦身与 k6 全周期压测复盘"
date: 2026-11-25
tags: ["Xray", "VLESS", "XHTTP", "Fluxgate", "Vector", "k6", "Lightsail", "DevOps"]
type: "longform"
platform: "x"
status: "draft"
---

# 只用 2C1G（$7/月）AWS Lightsail，如何扛住 500 并发不 OOM？

很多做科学上网与跨境加速服务的朋友有个常见误区：节点一卡、一掉线、一内存吃紧，第一反应就是加钱升配（2C2G、4C4G）。

最近我们在东京线 **`jp-xconnect-02.svc.plus`**（AWS Lightsail **2 vCPU / 939 MiB RAM / 0 Swap**）上做了一次彻底的架构重构与极限压测：在不升配、保证 **VLESS + XHTTP + TLS** 与 **VLESS + TCP + Vision** 双协议在线、控制面/计费/监控全开的前提下，硬扛了 **500 并发 VU × 30 分钟（250,172 次请求）零 OOM、零重启**。

把完整排障、内存瘦身黑魔法、k6 实测拐点与单机 ROI 账本拆开复盘👇

---

## 一、重构前为什么 1G 内存总觉得不够用？

以前边缘节点是典型的“多进程拼装态”：
- L7 入口用 HAProxy（约 `110 MiB`）
- `xray`（XHTTP）+ `xray`（TCP）+ `xray-exporter-xhttp` + `xray-exporter-tcp` **4 个进程**，光代理和采集就吃掉 **`319.1 MiB`**，还开了 `10086 / 10087` 两个 gRPC 端口轮询
- `systemd-journald` 放任 300M/14 天日志，mmap 缓存直接膨胀到 **`105.8 MiB`**
- `vector` 采集探针莫名其妙吃 **`124 MiB`**
- 再加上 `fail2ban`、`unattended-upgrades`、`auditd` 等后台进程，还没上真实用户流量，1G 机器一半内存已经没了。

---

## 二、五大核心服务收口与三个关键“狠刀”

重构后，节点只保留职责完全隔离的 **5 个核心/支撑服务**：
1. **`xconnect-edge-agent`（`24.1 MiB`）**：唯一控制面，对接 `accounts.svc.plus`，分别驱动 Proxy（`SIGHUP` 热加载）与 Gateway（WireGuard `xconzero0`）。
2. **`fluxgate v0.2.1`（`28.1 MiB`）**：Rust 自研 L7 TLS 入口（替代 HAProxy，内存直接从 `110 MiB` 降到 `28 MiB`），`:443` 按 Host+Path 分流到 `/dev/shm/xray.sock` 与 `/run/xconnect-gateway/xray.sock`。
3. **`xconnect-proxy-xray`（`59.4 MiB`）**：把 `Xray-core` 与 `xray-exporter` **内嵌编译成单一二进制**（`xray-exporter#23`），一个 `core.Instance` 同时托管 `proxy-xhttp-in` 与 `proxy-tcp-in`（`:1443` Vision），直读进程内内存 `stats.Manager`，彻底干掉 `10086/10087` gRPC 和独立 exporter——**4 进程 `319.1 MiB` 压缩成 1 进程 `59.4 MiB`（-83%）**。
4. **`xconnect-gateway-xray`（`36.8 MiB`）**：与 Proxy 配置/进程完全独立，专门承接零信任组网流量进 WireGuard。
5. **`vector`（`71.5 MiB`）**：核心监控与计费汇聚探针（`:8686` 接收 Xray 每分钟推送的计费快照，15s 抓取全节点 Prometheus 指标）。

### 顺手挖出的三个隐蔽内存杀手：
1. **Vector 的 jemalloc + 透明大页（THP）陷阱**：Vector 0.41.1 内嵌 `jemalloc 5.3.0`（默认 8 arenas + `thp:default`），在 Linux `THP=always` 下即便单线程也会产生 **61–73 MiB `AnonHugePages`**。注入 `MALLOC_CONF=narenas:1,dirty_decay_ms:1000,muzzy_decay_ms:0,thp:never,retain:false`、`TOKIO_WORKER_THREADS=1` 并移除不存在的 `/var/log/syslog` 文件源后，Vector RSS 从 `121.3 MiB` 暴降到 **`71.5 MiB`（-39.6%）**，`AnonHugePages` 直接清零！
2. **`systemd-journald` 的 mmap 膨胀**：把日志上限从 `300M/14day` 收紧到 `64M / 8M 单文件 / 3day / daily vacuum`，并加上 `MemoryHigh=24M / MemoryMax=48M` cgroup 限制，RSS 从 `105.8 MiB` 降到 **`9.9–16.0 MiB`**（实时监控靠 Vector 往 VictoriaLogs 推，本地留 3 天排障足矣）。
3. **非核心后台服务清理**：既然 SSH 早已强制纯公钥登录（`PasswordAuthentication no`），`fail2ban`（~30 MiB）、`unattended-upgrades`（~10 MiB）、`auditd`、`polkit` 全部停用禁用并固化到 Ansible `common` role。

最终冷启动可用内存拉回 **`432+ MiB`**，还补充了 `tcp_slow_start_after_idle=0`、`tcp_notsent_lowat=131072`、`fluxgate` `4MiB/16MiB` H2 窗口和 Xray `bufferSize=128 / uplinkOnly=15 / downlinkOnly=30`，专门治好科学上网场景下语音/图片推送卡顿与丢帧。

---

## 三、40 VU vs 500 VU × 30 分钟 k6 极限压测实录

用 macOS 本机跑 `xray` 客户端（`VLESS + XHTTP + TLS`，`fp=chrome`，`alpn=h2,http/1.1,h3`）+ `k6` 对 `jp-xconnect-02.svc.plus` 分别打了两轮 30 分钟压测：

- **40 VU × 30 分钟（日常基线）**：
  - 总请求 `47,896`（稳态 `35.34 req/s`），**可用率 `99.90%`**
  - 延迟 `P50 = 107.75 ms`，**`P95 = 207.10 ms`**（稳如老狗）
- **500 VU × 30 分钟（极限压测）**：
  - 总请求 `250,172`（全周期均速 `138.90 req/s`，H2 复用预热后稳态达 **`206.24 req/s`**）
  - **可用率 `99.66%`**（`0.33%` 失败率，远低于 1% 红线）
  - 节点峰值 `1,498` 个 Socket（`1,222` Estab TCP），内存峰值 `810 / 939 MiB`（`88.8%`），**全程零 OOM、五大核心服务 `NRestarts = 0`、Fluxgate UDS `502 = 0`！**
  - 但代价也很真实：500 并发下 `P95` 被排队拉升到 **`4,591.57 ms`**（超出 `1500 ms` 阈值）。

---

## 四、Little's Law 拐点与 $7/月 Lightsail 的最佳 ROI

把 500 VU 爬坡期按 1 秒级采样拆开看，吞吐与边际效率（`QPS/VU`）给出了非常清晰的物理拐点：
- **`150 VU` 以前**：吞吐线性冲到 `86.6 req/s`，边际效率 `0.579 QPS/VU`，推算平均延迟 `727 ms`。
- **`200 VU` 拐点**：吞吐停滞在 `84.7–100 req/s`，`QPS/VU` 断崖跌到 `0.424`，延迟直接翻倍到 `1.36s+`——**2 vCPU 算力先于 1G 内存到达瓶颈**。
- **内存缩放斜率**：`Fluxgate + xconnect-proxy-xray` 每增加 1 个并发 VU 仅增长 **`0.59–0.63 MiB`**，因此 75% 内存安全线在 `~296 VU`（若清理 `/tmp` `75 MiB` 残留还能再抗到 `408 VU`）。

### 结论与调度参数（直接抄作业）：
1. **单台 2C1G 最佳运营甜点：`100 – 150 VUs`**（按 4x 思考时间折算，约承载 **`400 – 600` 名同时在线用户**）。
2. **ROI 对比（以 Lightsail `$7/月` IPv4 2C1G 计）**：
   - 保守跑 `40 VU`：单在线用户成本 `$0.0438/月`，每百万请求 `$0.0764`
   - 跑在 **`120 VU` 甜点**：单在线用户成本降至 **`$0.0146/月`**，每百万请求 **`$0.0338`**——**性价比直接提升 3 倍**，同时还能留出 `> 300 MiB` 内存冗余与 `P95 < 1s` 的丝滑体验。
3. **监控红线**：`P95 > 800ms` 预警、`> 1500ms` 或 `fluxgate_active_connections >= 200` / `MemAvailable < 188 MiB` 调度排空、`> 3000ms` 硬熔断。

小机器不是不能打，把多余进程、多级 RPC 和大页内存泄漏清理干净，一台 `$7/月` 的 2C1G 节点也能稳稳当当撑起一个中型边缘节点池的体面体验。
