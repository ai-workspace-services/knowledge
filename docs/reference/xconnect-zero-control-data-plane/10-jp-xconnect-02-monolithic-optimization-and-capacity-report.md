---
title: XConnect 边缘节点单体聚合架构优化、全链路压测与 2C1G ROI 容量报告
description: 以 jp-xconnect-02.svc.plus 为金丝雀节点，系统记录从拆分布署到单体 Xray-core + 内存 stats.Manager 聚合、Fluxgate v0.2.1 低延迟调优、journald/Vector/非核心服务瘦身，以及 40 VU / 500 VU × 30m k6 压测、Little's Law 拐点、P95 SLO 与 AWS Lightsail 2C1G ROI 评估全过程。
slug: jp-xconnect-02-monolithic-optimization-and-capacity-report
lang: zh
tags:
  - xconnect
  - xconnect-proxy-xray
  - xconnect-gateway-xray
  - fluxgate
  - vector
  - k6
  - lightsail
  - capacity-planning
  - roi
---

# XConnect 边缘节点单体聚合架构优化、全链路压测与 2C1G ROI 容量报告

> [!NOTE]
> 本文档沉淀 **2026-11-24 ~ 2026-11-25** 在 `jp-xconnect-02.svc.plus`（`AWS Lightsail 2 vCPU / 939 MiB RAM / 0 Swap`）金丝雀节点及 `jp-xconnect-01.svc.plus`（`1936 MiB RAM` 对照基线）上完成的端到端优化、现网实测、压测数据与跨仓库持久化证据。

- **交互式 Grafana 动态 ROI 面板预览页面**：[xconnect-core-topology.html](xconnect-core-topology.html)（四合一动态拓扑 + `40 vs 500 VU` 时序 + 拐点/内存缩放 + `P95 SLO & Lightsail ROI` 联动仿真器）
- **Grafana 仪表盘 JSON 定义**：[xconnect-topology-roi-dashboard.json](xconnect-topology-roi-dashboard.json)（对应 `ai-workspace-infra/artifacts` 插件 `plugins/xconnect-topology-roi-panel`）
- **PDF 归档版本**：[10-jp-xconnect-02-monolithic-optimization-and-capacity-report.pdf](10-jp-xconnect-02-monolithic-optimization-and-capacity-report.pdf)

---

## 一、完整优化演进历程与跨仓库落地清单

本次优化围绕 **"控制面查询阻塞修复 -> 代理与遥测进程合一降内存 -> 媒体低延迟调优 -> 宿主系统与采集探针极限瘦身 -> 40/500 VU 极限压测与容量定标"** 五个阶段展开，所有运行态变更均已通过 PR 固化到代码与声明仓库：

| 阶段 | 核心问题与改造动作 | 关键量化收益 | 对应仓库与 PR |
| :--- | :--- | :--- | :--- |
| **1. 用量/配额查询超时修复** | `accounts` 用量查询将 `usage/summary` 改为 PostgreSQL 服务端聚合与精简 `buckets` 去零行 | `64,835` 行扫描收敛至 `2,606` 行（`~308ms`），线上 `/api/account/usage/buckets` 恢复 `200 OK`（`556–780ms`） | `ai-workspace-services/accounts#338`、`ai-workspace-infra/gitops#976` |
| **2. Xray-core + 内存 `stats.Manager` 内嵌合并** | 将 `Xray-core` 内嵌至 `xray-exporter`，同一进程直接读取内存 `stats.Manager` 暴露 `/scrape` 并每分钟直推 Vector `:8686`，消除 gRPC `:10086/:10087` | 保留与 Gateway 共用的同一 `/usr/local/bin/xray` 二进制；支持 `SIGHUP` 热加载 | [`ai-workspace-xstream/xray-exporter#23`](https://github.com/ai-workspace-xstream/xray-exporter/pull/23) |
| **3. 低延迟网络栈与 Fluxgate 0.2.1 调优** | `sysctl` 开启 `tcp_slow_start_after_idle=0`、`tcp_notsent_lowat=131072`；Fluxgate 0.2.1 配置 `h2_stream_window_size=4MiB`、`h2_connection_window_size=16MiB`、`h2_ping_interval=15s`；Xray `bufferSize=128`、`uplinkOnly=15`、`downlinkOnly=30` | 消除闲置回落慢启动与 HTTP/2 窗口瓶颈，优化语音/图片突发流延迟；`jp-01` HAProxy 同步对齐 `bufsize 65536` / `http-no-delay` | `ai-workspace-xstream/fluxgate#4`、`ai-workspace-infra/gitops#977`、`ai-workspace-infra/playbooks#1062` |
| **4. `jp-02` 单体服务收敛 & Gateway 修复** | 停用 `xray-tcp.service` 与双 `xray-exporter`；将 `proxy-xhttp-in` + `proxy-tcp-in` 合并为统一 **`xconnect-proxy-xray.service`**；修复 `02-xconnect-gateway.yaml` `gateway_id` 错配（对齐 `jp-xconnect-gateway-02` / `net-jp-xconnect-02`）；对齐 `ansible-pull` 自动探测 | Proxy+遥测由 **4 进程 `319.1 MiB` 降至 1 进程 `54.3–59.4 MiB`（-83%）**；Fluxgate (`28.1 MiB`) vs HAProxy (`110.0 MiB`) 再省 ~82 MiB | `ai-workspace-infra/playbooks#1063` |
| **5. `systemd-journald` 与非核心服务停用** | 收紧 journald（`64M` 盘、`8M` 单文件、`3day`、`16M` runtime、`daily` vacuum + `24M/48M` cgroup 上限）；在 `roles/vhosts/common` 默认停用 `unattended-upgrades`、`apt-daily*`、`fail2ban`、`auditd`、`polkit` | `systemd-journald` RSS 从 `105.8 MiB`（`jp-02`）/ `59.8 MiB`（`jp-01`）降至 **`9.9–16.0 MiB`**；卸载冗余守护进程 ~35–40 MiB | `ai-workspace-infra/gitops#978`、`ai-workspace-infra/playbooks#1064`、`ai-workspace-infra/playbooks#1065` |
| **6. Vector jemalloc THP 内存瘦身** | 定位 Vector 0.41.1 内嵌 jemalloc 5.3.0 在 Linux `THP=always` 下产生 `61–73 MiB AnonHugePages`；注入 `MALLOC_CONF=narenas:1,dirty_decay_ms:1000,muzzy_decay_ms:0,thp:never,retain:false`、`TOKIO_WORKER_THREADS=1`、`MALLOC_ARENA_MAX=2`，停用无宿主的 `system_logs` 文件源，收紧 `disk_v2` buffer 至 `256 MiB` 下限、`MemoryHigh=72M / MemoryMax=128M` | `vector` RSS 降至 **`71.5 MiB`**（`jp-02`，**-39.6%**）与 **`80.4 MiB`**（`jp-01`，**-38.5%**），`AnonHugePages` 清零（`61.4 MiB -> 0`），cgroup 降至 `45–54 MiB`，`:8686` 与远端写零中断 | `ai-workspace-infra/gitops#979`、`ai-workspace-infra/playbooks#1066` |

---

## 二、XConnect 五大核心服务链路拓扑大图

经过上述收口，边缘节点上严格运行 **5 个核心/支撑服务**（控制面、L7 入口、双独立数据面、核心监控计费探针），配置、端口与 Unix Socket 完全隔离：

![XConnect 五大核心服务链路拓扑大图](assets/xconnect-core-topology.png)

### 五大核心服务与 Playbook Role 对应关系

| 核心服务 | 二进制与运行模式 | 监听 / Socket / 关键路径 | 对应 Playbook Role |
| :--- | :--- | :--- | :--- |
| **`xconnect-edge-agent`** | `/usr/local/bin/agent-proxy`（控制面唯一同步器） | `/etc/agent/conf.d/01-agent-proxy.yaml`（Proxy）<br>`/etc/agent/conf.d/02-xconnect-gateway.yaml`（Gateway） | `roles/vhosts/xconnect-edge-agent` |
| **`fluxgate`** | `/usr/local/bin/fluxgate v0.2.1`（L7 TLS 入口） | `*:443`（`*.svc.plus`）、`127.0.0.1:9102/metrics`<br>`/split/* -> /dev/shm/xray.sock`<br>`/xconnect/* -> /run/xconnect-gateway/xray.sock` | `roles/vhosts/fluxgate` |
| **`xconnect-proxy-xray`** | `/usr/local/bin/xray`（内嵌 `xray-exporter` + 内存 `stats.Manager`） | `/dev/shm/xray.sock,0666`（`proxy-xhttp-in`）<br>`0.0.0.0:1443`（`proxy-tcp-in` Vision）<br>`127.0.0.1:8080/scrape`、POST `:8686` | `roles/vhosts/xconnect_proxy`（`xray_merged_mode: true`，依赖 `xray-core`） |
| **`xconnect-gateway-xray`** | `/usr/local/bin/xray`（独立裸 `-config` 进程，无 exporter） | `/run/xconnect-gateway/xray.sock,0660`（`xconnect-vless-in`）<br>outbound `redirect 127.0.0.1:51820`（WireGuard `xconzero0`） | `roles/vhosts/xconnect_gateway` |
| **`vector`** | `/usr/bin/vector 0.41.1`（`MemoryHigh=72M / MemoryMax=128M`） | `127.0.0.1:8686` 计费中继（256 MiB disk_v2）<br>15s 抓取 `:8080 / :9102 / :9100 / :9256` + 单 `journald` | `roles/vhosts/vector-agent` + `roles/vhosts/xconnect_node_log_policy` |

---

## 三、40 VU × 30 分钟 vs 500 VU × 30 分钟 k6 实测压测结果

两次压测均在 macOS 客户端通过本地 `/opt/homebrew/bin/xray`（VLESS+XHTTP+TLS，`address=jp-xconnect-02.svc.plus:443`，`path=/split`，`mode=auto`，`fp=chrome`，`alpn=h2,http/1.1,h3`）向 `https://cp.cloudflare.com/generate_204` 发起连续加压（`k6_test_profile=proxy_capacity`：`7.5m` 线性爬坡 -> `15m` 峰值保持 -> `7.5m` 线性降载，每次请求附带 `sleep(1)` 思考时间）。

![40 VU vs 500 VU 30分钟 1s 级实测吞吐与延迟曲线对比](assets/k6-40vu-vs-500vu-timeseries.png)

### A. 客户端 k6 全周期核心指标对比

| 指标项 | 40 VU × 30 分钟基线 | 500 VU × 30 分钟极限压测 | 阈值标准 |
| :--- | :---: | :---: | :---: |
| **最大并发 VU** | `40` VUs | **`500` VUs**（`ulimit -n 65536`） | — |
| **总请求数 / 平均 QPS** | `47,896`（`26.60 req/s`；稳态 `35.34/s`） | **`250,172`（`138.90 req/s`；预热后稳态 `206.24/s`）** | — |
| **HTTP 错误率 (`http_req_failed`)** | `0.10%`（`50` 次；可用率 `99.90%`） | **`0.33%`（`843 / 250,172`；可用率 `99.66%`）** | **`PASS`**（`< 1.00%`） |
| **延迟 Min / Avg / P50** | `0.00 / 130.70 / 107.75 ms` | `0.00 / 1,623.76 / 965.44 ms` | — |
| **延迟 P90 / P95 / Max** | `172.20 /` **`207.10 ms`** `/ 3,235.09 ms` | `3,082.56 /` **`4,591.57 ms`** `/ 60,003.77 ms` | 40 VU **`PASS`** / 500 VU **`FAIL`**（`<= 1500 ms`） |
| **网络总流量** | `28 MB` 收 / `4.2 MB` 发 | `147 MB` 收 / `23 MB` 发 | — |

- **500 VU 失败请求拆解（`843 / 250,172`）**：`647` 次 `unexpected EOF`、`185` 次 `request timeout (60s)`、`10` 次 `EOF`、`1` 次本机 `connection reset by peer`；全周期 `proxy duration < 1500ms` 占比 `69%`（`174,508 / 250,172`），`k6` 退出码 `99`（容量可用率过关，延迟阈值超标）。
- **连接池滞后效应（Hysteresis）**：从上方时间序列曲线可见，500 VU 刚进入稳态前段（`455–660s`）吞吐一度停滞在 `86.22 req/s`（推算均延 `4,798.8 ms`）；在 `t ≈ 600s` 触发一轮连接重置后，H2/XHTTP 多路复用连接池完成重建，**`900–1350s` 稳态飙升并持续稳定在 `206.24 req/s`（推算均延回落至 `1,424.3 ms`）**。

### B. 500 VU 压测期间 `jp-xconnect-02.svc.plus` 服务端健康度

在 `939 MiB RAM / 0 Swap` 条件下全程 **零 OOM、5 大核心服务 `NRestarts = 0`、核心服务日志 0 条 `error/warn`**：

| 服务端指标 | 压测前 (`01:12Z`) | 500 VU 峰值 (`01:30Z`) | 压测结束 (`01:43Z`) | 增量 / 备注 |
| :--- | :---: | :---: | :---: | :--- |
| **Load Avg (`2 vCPU`)** | `0.00, 0.03, 0.06` | `0.79, 0.70, 0.44` | `0.28, 0.49, 0.48` | CPU 未达饱和 |
| **内存 Used / Free / Avail (MiB)** | `499 / 165 / 440` | **`810 / 93 / 128`** | `798 / 59 / 141` | 峰值吃紧，未触及 OOM |
| **Socket（Total / TCP / Estab）** | `207 / 65 / 45` | **`1,498 / 1,274 / 1,222`** | `835 / 700 / 591` | 峰值稳定支撑 >1,200 并发连接 |
| **`fluxgate` RSS / CPU** | `28.1 MiB` (`0.8%`) | `199.1 MiB` (`2.0%`) | `202.0 MiB` (`2.9%`) | UDS `status=200` **`+270,033`**、`502` **`+0`**、`upstream_errors` **`+0`** |
| **`xconnect-proxy-xray` RSS / CPU** | `60.0 MiB` (`0.3%`) | `149.1 MiB` (`1.9%`) | `179.7 MiB` (`3.1%`) -> 回落至 `121.0 MiB` | `goroutines` 峰值 `2,923`；`alloc` 峰值 `60.68 MB` |

---

## 四、实测拐点与内存缩放模型（k6 1s 级采样曲线）

![实测并发拐点与 939 MiB 内存缩放模型曲线](assets/knee-and-memory-scaling.png)

### 1. 爬坡阶段 Little's Law 拐点分析

由于每个 VU 每轮执行 `XHTTP GET + sleep(1s)`，由 Little's Law 可由瞬时 QPS 反推平均请求延迟 $\text{Lat}_{\text{ms}} = (\text{VUs}/\text{QPS} - 1)\times 1000$：

| 爬坡采样 VU | 实际吞吐 QPS (req/s) | 边际效率 (`QPS/VU`) | 推算平均延迟 | 区间状态判定 |
| :---: | :---: | :---: | :---: | :--- |
| **`40`** *(40VU 稳态)* | `35.34` | **`0.8835`** | `131.9 ms` | 线性无拥塞（实测 `P95 = 207.1 ms`） |
| **`100`** | `59.24` | `0.5945` | `682.1 ms` | 健康线性扩张 |
| **`150`** | **`86.62`** | **`0.5790`** | **`727.0 ms`** | **拐点前最佳甜蜜点上限** |
| **`200`** | `84.67` | **`0.4244`** | **`1,356.3 ms`** | **Little's Law 排队拐点（吞吐停滞、延迟近翻倍）** |
| **`250`** | `96.24` | `0.3858` | `1,592.0 ms` | 平均延迟越过 `1500 ms` 线 |
| **`300` – `500`** | `92.0 – 100.5` | `0.327 -> 0.187` | `2,056 -> 4,348 ms` | 吞吐平台期，新增并发全部转化为排队延迟 |

### 2. 939 MiB 内存缩放模型与 OOM 物理边界

- **Proxy 边际内存斜率（`Fluxgate + xconnect-proxy-xray`）**：从 `88.1 MiB`（`0 VU`）-> `~90 MiB`（`40 VU`）-> `381.7 MiB`（`500 VU` 并发峰值，`VmHWM` 合计 `390.8 MiB`），线性斜率为 **`0.587 – 0.634 MiB/VU`**。
- **非代理固定开销（Vector 优化后实测 `09:50 CST`）**：整机非 Proxy 已提交内存为 **`451.7 MiB`**（含 `vector 71.1 + journalctl 15.1 MiB`、`xconnect-host-metrics 49.0 MiB`、`xconnect-edge-agent 19.2 MiB`、`xconnect-gateway-xray 13.5 MiB` 及 OS/内核/`/tmp` tmpfs **`75 MiB`**）；若清理 `/tmp` `75 MiB` tmpfs，固定开销仅 **`376.7 MiB`**。
- **OOM 安全容量对比**：

| 内存警戒线 | 现状（含 `/tmp` `75 MiB`） | 清理 `/tmp` 后 |
| :--- | :---: | :---: |
| **75% RAM（`704.2 MiB`，留 `235 MiB` 缓冲）** | Proxy 预算 `252.6 MiB` -> **`280 – 296 VUs`** | Proxy 预算 `327.6 MiB` -> **`408 – 415 VUs`** |
| **80% RAM（`751.2 MiB`，留 `188 MiB` 缓冲）** | Proxy 预算 `299.5 MiB` -> **`360 – 370 VUs`** | Proxy 预算 `374.5 MiB` -> **`488 – 489 VUs`** |
| **最佳运营甜点（CPU/延迟优先约束）** | **`100 – 150 VUs`（等效 `300 – 750` 在线用户）** | 同右（CPU 拐点早于内存红线到达） |

---

## 五、P95 延迟监控上限与 2C1G AWS Lightsail ROI 对比

![P95 延迟监控分级阈值与 AWS Lightsail 2C1G ROI 曲线](assets/p95-slo-and-lightsail-roi.png)

### 1. 分级 P95 延迟 SLO 与告警阈值

实测 Fluxgate `:9102/metrics`（`328,397` 次 UDS 请求）中 **`87.61%` 在 `<= 50 ms` 内完成**（`83.47% <= 10 ms`），其余 `~12.4%` 长尾由 XHTTP 长连接存活周期贡献。因此端到端延迟监控与网关连接数必须配合使用：

| 告警级别 | 端到端 P95 阈值（Blackbox / k6） | Fluxgate UDS 短请求快路径（`<= 50 ms` 占比） | `fluxgate_active_connections` | 可用内存 (`MemAvailable`) | 自动化/运维动作 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **SLO 正常区** | **`<= 500 ms`**（40 VU 基线 `207 ms`） | `>= 85%` | `< 150` | `>= 300 MiB`（占用 `< 68%`） | 正常流量调度 |
| **P1 预警 (Warn)** | **`> 800 ms` 持续 5m** | `< 80%` | `>= 160` 持续 5m | `< 235 MiB`（占用 `> 75%`） | 下调节点权重 / 预热备用节点 |
| **P2 排空扩容 (Page)** | **`> 1,500 ms` 持续 3m** | `< 70%` 或 `5xx > 0.5%` | `>= 200` 持续 3m | `< 188 MiB`（占用 `> 80%`） | **调度器排空新连接**至同区其他节点 |
| **P3 熔断隔离** | **`> 3,000 ms` 持续 2m** 或错误率 `> 1%` | `5xx > 1%` | `>= 280` | `< 120 MiB`（占用 `> 87%`） | **强制从节点池摘除**，防止 OOM |

```yaml
- alert: XConnectProxyP95LatencyWarn
  expr: histogram_quantile(0.95, sum by (le, instance) (rate(k6_http_req_duration_bucket[5m]))) > 0.8
  for: 5m
  labels: { severity: warning }

- alert: XConnectProxyP95LatencyPage
  expr: histogram_quantile(0.95, sum by (le, instance) (rate(k6_http_req_duration_bucket[5m]))) > 1.5
  for: 3m
  labels: { severity: critical }

- alert: FluxgateShortPathDegraded
  expr: |
    sum by (instance) (rate(fluxgate_http_request_duration_seconds_bucket{route="uds",le="0.05"}[5m]))
    / sum by (instance) (rate(fluxgate_http_request_duration_seconds_count{route="uds"}[5m])) < 0.75
  for: 3m
  labels: { severity: critical }

- alert: FluxgateActiveConnsDrain
  expr: fluxgate_active_connections >= 200
  for: 3m
  labels: { severity: critical }
```

### 2. 2C1G AWS Lightsail 经济性 ROI 对比（计算费用均摊 + 流量费用均摊）

AWS Lightsail Linux `2 vCPU / 1 GiB RAM` 实例（IPv4 参考价 **`$7/月`**，同时列出 **`$10/月`** 与 **`$12/月`** 对照档）套餐自带 **`2 TB/月`（`2,048 GB`）免费数据传输包**。评估单用户月综合成本时，必须同时计入 **计算费用均摊 (`Compute/人`)** 与 **流量费用均摊 (`Traffic/人`)**：

- **计算均摊基线**：在真实在线用户 `U = 4 × VU` 下，每位用户每月单机计算成本为 `C_comp = P_plan / U`，并天然享有 `G_free = 2048 GB / U` 的套餐内免费流量额度（如 `120 VU = 480 人` 时，计算均摊 **`$0.0146/人/月`**，含 **`4.27 GB/人/月`** 免流额度）。
- **流量均摊的两种路径对比**（当人均月流量 `G_user > G_free` 时）：
  1. **横向扩充 2C1G 节点池化 `2 TB` 流量包（推荐架构）**：新增 `$7/月` 节点不仅线性扩充 CPU/RAM，还将流量包等效单价锁定在 **`$7 / 2048 GB = $0.00342 / GB`**（`$10` 档 `$0.00488/GB`；`$12` 档 `$0.00586/GB`），此时单用户综合成本为 `C_total = C_comp + max(0, G_user - G_free) × $0.00342/GB`。
  2. **单机硬抗 AWS 亚太（东京）超额流量费（反面基准）**：超出 `2 TB/月` 后 AWS 按 **`$0.09 / GB`** 计费（比节点池化流量包贵 **26.3 倍**），会导致流量成本瞬间反客为主。

#### A. 不同并发水位下的计算均摊、免流配额与综合成本矩阵（`$7 / $10 / $12` 档）

| 运营并发水位 (`@4x` 在线用户) | 稳态 QPS / 月请求 | 人均套餐免流额度 (`2048GB / U`) | `$7/月` 计算均摊 + 流量均摊<br>(`纯计算≤免流` \| `10GB/人池化` \| `20GB/人池化`) | `$10/月` 对照档<br>(`纯计算` \| `10GB/人池化`) | `$12/月` 对照档<br>(`纯计算` \| `10GB/人池化`) | 单机硬抗 `$0.09/GB` 超额费<br>(`@10GB/人` 反面基准) | SLO 状态 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`40 VU` 保守基线** (`~160` 人) | `35.34` (`91.6M`) | `12.80 GB/人` | `$0.0438` \| `$0.0438` *(免流内)* \| `$0.0684` | `$0.0625` \| `$0.0625` | `$0.0750` \| `$0.0750` | `$0.0438` *(整机 1.6TB 未超额)* | `PASS` (`207ms`) |
| **`120 VU` 最佳甜点** (`~480` 人) | `80.0` (`207.4M`) | **`4.27 GB/人`** | **`$0.0146` \| `$0.0342` \| `$0.0684`** | **`$0.0208` \| `$0.0488`** | **`$0.0250` \| `$0.0586`** | **`$0.5306/人`** *(超额费 $247.7/月)* | **`PASS` (最佳 ROI)** |
| **`160 VU` 软上限** (`~640` 人) | `100.0` (`259.2M`) | `3.20 GB/人` | `$0.0109` \| `$0.0342` \| `$0.0684` | `$0.0156` \| `$0.0488` | `$0.0188` \| `$0.0586` | `$0.6229/人` *(超额费 $391.7/月)* | 临界预警线 |
| **`200 VU` 排空线** (`~800` 人) | `110.0` (`285.1M`) | `2.56 GB/人` | `$0.0088` \| `$0.0342` \| `$0.0684` | `$0.0125` \| `$0.0488` | `$0.0150` \| `$0.0586` | `$0.6784/人` *(超额费 $535.7/月)* | 排队拐点（切流） |
| **`500 VU` 极限压测** (`~2000` 人) | `138.9` (`360.0M`) | `1.02 GB/人` | `$0.0035` \| `$0.0342` \| `$0.0684` | `$0.0050` \| `$0.0488` | `$0.0060` \| `$0.0586` | `$0.8113/人` *(超额费 $1,615.7/月)* | **`FAIL` (`4.59s`, 89% RAM)** |

#### B. `120 VU`（`480` 在线用户，`$7/月` 档）三档典型流量画像的成本拆解

| 用户流量画像 | 人均月流量 (`整机月总流量`) | ① 计算费用均摊 (`Compute/人`) | ② 流量费用均摊 (`池化 $0.00342/GB`) | **池化综合月成本 (`计算 + 流量`)** | 对比：单机硬抗超额 (`$0.09/GB`) | 架构结论 |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **轻量信令/网页档** | **`<= 4.27 GB/人`** (`<= 2.0 TB`) | **`$0.0146 / 人`** | **`$0.0000 / 人`** *(2TB 包内全免)* | **`$0.0146 / 人 / 月`** | **`$0.0146 / 人 / 月`** | 单节点 `120 VU` 即可吃满计算与免流包双红利 |
| **日常办公/AI 辅助档** | **`10.0 GB/人`** (`4.8 TB`) | **`$0.0146 / 人`** | **`+$0.0196 / 人`** *(补 5.73 GB)* | **`$0.0342 / 人 / 月`** | `$0.5306 / 人 / 月` *(贵 15.5×)* | 用 `2.4` 台 `$7` 节点池化流量包，人均仅 3.4 美分 |
| **流媒体/视频重度档** | **`20.0 GB/人`** (`9.6 TB`) | **`$0.0146 / 人`** | **`+$0.0538 / 人`** *(补 15.73 GB)* | **`$0.0684 / 人 / 月`** | `$1.4306 / 人 / 月` *(贵 20.9×)* | 流量带宽成为主导约束，必须按 `2 TB/台` 横向铺节点 |

### 核心运行建议
1. **将单台 2C1G 调度水位定标在 `120–150 VUs`（约 `480–600` 在线用户）**：相比 `40 VU` 纯计算均摊成本下降 **3×**（`$0.0438 -> $0.0146/人/月`）；若考虑人均 `10 GB/月` 流量，通过多台 `$7/月` 2C1G 节点横向池化 `2 TB` 免费流量包（`$0.00342/GB`），**“计算 `$0.0146` + 流量 `$0.0196` = `$0.0342/人/月`”** 即可实现性能与成本帕累托最优。
2. **以 `200 VUs` / `P95 > 1500 ms` / `MemAvailable < 188 MiB` / `月出站流量 > 1.8 TB (90%)` 作为四维统一扩缩与切流触发器**，严禁让 0-Swap 实例长期运行在 `> 80%` 内存区或触发 `$0.09/GB` 超额流量惩罚。
3. **清理 `/tmp` 75 MiB tmpfs 残留并纳入 Vector `:8686` 流量快照账单熔断**：当单节点当月累计出站流量达到 `1.8 TB` 时由 `accounts.svc.plus` 自动下调该节点路由权重，将新增流量平滑分摊至同池未满 `2 TB` 的兄弟节点。
