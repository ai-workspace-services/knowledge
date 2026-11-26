---
title: XConnect Zero 控制面与数据面解耦、混合部署及控制台全链路规划
description: 围绕 xconnect-edge-agent、XConnect-Gateway、XConnect-One、accounts.svc.plus 与 console.svc.plus/panel/xconnect-zero 的目标架构、职责边界、Agent Proxy 混合部署规范与后续任务拆解。
slug: xconnect-zero-control-data-plane-readme
lang: zh
tags:
  - xconnect
  - xconnect-zero
  - xconnect-edge-agent
  - xconnect-gateway
  - xconnect-one
  - architecture
  - planning
---

# XConnect Zero 控制面与数据面解耦、混合部署及控制台全链路规划

> [!NOTE]
> 本文档目录为**实施规划（Planning / Target Architecture）**，记录目标架构、职责边界、接口契约与后续任务拆解，不代表对应代码或线上环境已完成验收。所有现状核查基线均基于 `xconnect-edge-agent`、`XConnect-Gateway`、`XConnect-One`、`accounts` 与 `portal` 仓库当前代码实现。

---

## 一、规划背景与核心目标

当前 XConnect Zero 体系存在以下跨仓库断点：

1. **控制面与数据面边界尚未完全收口**：`XConnect-Gateway` 进程内部仍直接承载 `accounts.svc.plus` 配置拉取与 ACK 轮询循环（`syncConfig` / `serveContainer`），同时缺乏标准化的本地非敏感遥测输出；`xconnect-edge-agent` 在 `role: gateway` 模式下仅做被动文件读取，未接管 Gateway 控制面编排与 WireGuard/Xray/Relay 数据面采集上报。
2. **`XConnect-One` 缺少统一登录与 Gateway Endpoint 选择体验**：客户端缺少 `xconnect login` 对接 `accounts.svc.plus` 认证系统并交互选择 Gateway Endpoint 的流程，且仍保留未签名的 `ConfigContractLegacy`（`/api/overlay/v1/devices/register` + `/api/overlay/v1/config`）双轨代码。
3. **`accounts.svc.plus` 遥测汇聚与模式切换接口未闭环**：`reportAgentStatus` 仅更新设备 `last_seen_at`，未持久化 `OverlayStatus` 中的路径、RTT、流量及连接用户信息；缺少面向控制台的遥测聚合 API 与互联网络模式（`wg_vless_l3` / `wg_udp_l3` / `wg_vless_l2`）下发接口。
4. **`console.svc.plus/panel/xconnect-zero` 控制台数据待点亮**：概览页 4 张 SASE 遥测分析卡片（`SASE 流量分析`、`已连接用户`、`热门专用应用程序`、`热门用户`）当前显示 `暂无数据`，配置管理页的 3 张互联网络模式卡片因控制面下发接口未接入而处于禁用状态。

本次规划采用 **Clean Cut（无需向后兼容）** 原则，在**尽可能保持 Web Console 现有 UI 结构与交互布局不变**的前提下，完成全链路职责收敛与功能完善。

---

## 二、目标架构与职责边界

```text
+-----------------------+         +----------------------------------------+
|  console.svc.plus     | <-----> |           accounts.svc.plus            |
|  /panel/xconnect-zero |  BFF    |  - 统一身份认证 (/api/auth/*)          |
|  (保持现有 UI 布局)   |         |  - Overlay 控制面 (/api/overlay/v1/*)  |
+-----------------------+         |  - Edge Agent 网关控制面 & 遥测聚合    |
                                  +----+-----------------------------+-----+
                                       ^                             ^
         控制面同步 + 采集上报          |                             | 仅用户登录 +
         (/api/agent-server/v1/*       |                             | 设备会话/签名配置
          & /api/overlay/v1/*)         |                             |
                                  +----+---------------+     +-------+-----------+
                                  | xconnect-edge-agent|     |   XConnect-One    |
                                  |  (role: gateway)   |     | (CLI / app-bridge)|
                                  |  - Gateway 控制面  |     | - login 认证      |
                                  |  - 采集 & 上报     |     | - 选 Gateway EP   |
                                  +----+---------------+     | - 本地数据面隧道  |
                                       | 本地控制/状态契约    +---------+---------+
                                       v                               |
                                  +----+---------------+               |
                                  |  XConnect-Gateway  | <-------------+
                                  |  (纯网络数据面)     |  VLESS/XHTTP + WG /
                                  |  WG + Xray + Relay |  UDP 直连 / Relay
                                  +--------------------+
```

### 四条刚性设计准则

1. **控制面与数据面解耦**：
   - `XConnect-Gateway` 与 `XConnect-One` 除必要的设备会话/登录认证外，只负责网络数据面（WireGuard、Xray、Peer Relay），不再承担长期配置轮询或遥测直报；
   - `xconnect-edge-agent` 负责对接 `XConnect-Gateway` 的配置控制面（拉取校验 `GatewaySignedConfig`、触发本地 `apply`、回传 ACK）与运行时遥测采集上报。
2. **Agent Proxy 与 `XConnect-Gateway` 同机混合部署规范**：
   - 每个 Agent Proxy 节点均可混合部署一个拥有唯一 `Gateway ID` 与独立域名入口的 `XConnect-Gateway` 服务；
   - 两者复用同一宿主代理引擎二进制（`xray-core`）与宿主 Ingress（`Caddy` / `Fluxgate` / `HAProxy :443` 按域名 SNI/Host 分流），但运行各自独立的 `xray` 后端进程、配置文件与 Socket：
     - **Agent Proxy**：`xray.service` + `/usr/local/etc/xray/config.json` + `/dev/shm/xray.sock` + Stats `127.0.0.1:10086`；
     - **`XConnect-Gateway`**：`xconnect-gateway-xray.service` + `/var/lib/xconnect-gateway/runtime/xray.json` + `/run/xconnect-gateway/xray.sock` + Stats `127.0.0.1:10088`（规划；`10087` 已被 Agent Proxy 的 `xray-tcp.service` 占用，见 [04 文档](04-ansible-role-decomposition-and-orchestration.md) 第三、七节）。
3. **Clean Cut（无需向后兼容）**：
   - 直接下线 `XConnect-One` 与 `accounts` 中未签名的旧版 `ConfigContractLegacy`（`/api/overlay/v1/devices/register` + `/api/overlay/v1/config`）以及 `XConnect-Gateway` 内嵌的独立控制面轮询器。
4. **Web Console 保持 UI 布局不变**：
   - `https://console.svc.plus/panel/xconnect-zero` 保留现有 `Zero 概览`、`节点管理`、`配置管理` 三栏 Tab 及全部卡片骨架，仅通过真实数据流点亮 4 张 SASE 遥测卡、节点实时状态及 3 张互联网络模式切换卡片。

---

## 三、目录文档索引

| 文档 | 内容概要 |
| :--- | :--- |
| [01-architecture-and-hybrid-deployment.md](01-architecture-and-hybrid-deployment.md) | 控制面/数据面边界定义、`XConnect-Gateway` 与 `Agent Proxy` 混合部署架构（同引擎/独立域名/独立 Xray 后端）、`XConnect-One` 统一认证与选点模型 |
| [02-wire-contracts-and-apis.md](02-wire-contracts-and-apis.md) | 各组件间本地契约与 HTTP API 规范（Gateway 本地状态/遥测、`xconnect-edge-agent` 上报与同步、`XConnect-One` 登录与入网、`accounts` 聚合存储、`portal` BFF 与 UI 数据绑定） |
| [03-task-breakdown-and-roadmap.md](03-task-breakdown-and-roadmap.md) | 可直接派发执行的 **5 大模块、16 个具体开发任务**（`Task A1–A4` / `B1–B3` / `C1–C3` / `D1–D3` / `E1–E2`，含建议分支、文件/签名与可机器判定验收标准）及 **Wave 1–3** 跨仓并行调度矩阵 |
| [04-ansible-role-decomposition-and-orchestration.md](04-ansible-role-decomposition-and-orchestration.md) | 边缘节点 8 个 Ansible Role（`xray-core` / `caddy` / `fluxgate` / `haproxy` / `xconnect-proxy` / `xconnect-gateway` / `xray-exporter` / `xconnect-edge-agent`）的职责边界、资源归属矩阵、契约变量、Proxy / Gateway 流量与账单标签规范、组合场景与迁移步骤（以 `ph-xconnect.svc.plus` 运行态为基线） |
| [05-three-tier-traffic-split-routing-and-observability.md](05-three-tier-traffic-split-routing-and-observability.md) | 基于 `5+1` 节点分组（`Free` / `Shared` / `Plus` / `Pro` / `Custom` / `Team`）的三层分流路由规划（第一层国内与局域网 `DIRECT` -> 第二层 `Media-Pool` VPS 流量优先与 `MATCH` 兜底 -> 第三层 `Pro-EC2-Pool` 定义为高速流量、不做流媒体与下载限制；`Pro` 订阅可用双池、`Plus` 订阅仅 `Media-Pool` 且 `Pro` 节点不可见；`Custom` 专属节点保持白名单绑定机制、没有使用限制）、跨仓库落地设计与 Grafana 流量调度监控面板 |
| [06-implementation-task-breakdown-and-pilot-verification.md](06-implementation-task-breakdown-and-pilot-verification.md) | 试点节点（`jp-xconnect-free-01` / `ph-xconnect` / `jp-xconnect-pro-01`）现网基线验证结果，以及面向 `accounts`、`portal`（GitOps 同步 & `/panel/gateway`）、`xconnect-edge-agent`、`xray-exporter`、`xconnect-app`（自动下发覆盖 + 第三方 `vless://` 无感知）与 `gitops`/`playbooks` 的 5 大模块可执行任务单（`A1–A3`、`B1–B2`、`C1–C3`、`D1–D2`、`E1–E3`） |
| [07-dual-bucket-quota-metering-and-smooth-upgrade-plan.md](07-dual-bucket-quota-metering-and-smooth-upgrade-plan.md) | 双桶配额（`Pro` 30GB 高速流量 + 50GB VPS 流量、`Plus` 仅 `Media-Pool` 且 `Pro` 节点不可见、`Custom` 专属白名单无限制）的分池计费采集任务拆解（`DB-1`、`B-1~B-2`、`A-1~A-3`、`P-1`、`G-1`）与 `Expand -> Shadow -> Verify -> Enforce` 零停机平滑滚动升级方案 |
| [08-gateway-forwarding-policy-and-self-service-access-control.md](08-gateway-forwarding-policy-and-self-service-access-control.md) | Gateway 节点间转发策略执行器（`XCONNECT_ZERO_FWD` + `iptables-restore --noflush`）与 `console.svc.plus/panel/xconnect-zero` 自助访问控制策略全链路规划（含 v1/v2 `Accept` 协商、`accounts` Explain API 与 `ph-xconnect.svc.plus` 试点验收矩阵） |
| [09-xconnect-one-embedded-runtime-libxray-wireguard-go.md](09-xconnect-one-embedded-runtime-libxray-wireguard-go.md) | `XConnect-One` Phase 1 单二进制内嵌运行时规划（`--runtime=embedded\|external`：最小化注册 `xray-core` / `libXray` 协同、内嵌 `wireguard-go` UAPI 与 Level-1 热重启、Linux/macOS/Windows 三端 `NetConfigurator` 替代 `wg-quick`） |
| [10-jp-xconnect-02-monolithic-optimization-and-capacity-report.md](10-jp-xconnect-02-monolithic-optimization-and-capacity-report.md)（[PDF](10-jp-xconnect-02-monolithic-optimization-and-capacity-report.pdf) · [拓扑图](xconnect-core-topology.html)） | **`jp-xconnect-02.svc.plus` 单体聚合架构实战汇总报告**：五大核心服务拓扑、Xray-core+stats.Manager 内嵌合并、Fluxgate 0.2.1/sysctl/journald/Vector THP 极致内存优化、40/500 VU × 30m k6 全周期实测、Little's Law 拐点与 2C1G AWS Lightsail ROI 定标 |
| [11-xconnect-controller-accounts-split-and-persistence-plan.md](11-xconnect-controller-accounts-split-and-persistence-plan.md) | **`xconnect-controller` 与 `accounts` 核心服务按业务域拆分与状态持久化规划**：完整 API 域归属矩阵（Overlay V1/Admin/Legacy + Agent-Server）、Ed25519 签名密钥环持久化与平滑轮换、One 节点幂等重入（Re-join 保留 IP/ACL）、Go 自部署 + JS/TS Cloudflare Worker（Hyperdrive + PostgreSQL）双形态架构与 4 阶段路线图 |

---

## 四、关联代码仓库

| 组件 | GitHub 仓库 | 核心职责 |
| :--- | :--- | :--- |
| `xconnect-edge-agent` | `https://github.com/ai-workspace-xstream/xconnect-edge-agent` | Agent Proxy 用户同步、Gateway 配置控制面、Gateway/One 运行时遥测采集与上报 |
| `XConnect-Gateway` | `https://github.com/ai-workspace-xstream/XConnect-Gateway` | 纯数据面节点（WireGuard + 独立 Xray 后端 + Peer Relay）与本地状态导出 |
| `XConnect-One` | `https://github.com/ai-workspace-xstream/XConnect-One` | 客户端 CLI / `app-bridge`、`accounts.svc.plus` 登录与 Gateway Endpoint 选择、本地隧道与路径管理 |
| `accounts` | `accounts.svc.plus` 控制面后端 | 统一用户认证、Overlay v1 签名控制面、Edge Agent 状态接收与遥测持久化聚合 |
| `portal` | `console.svc.plus/panel/xconnect-zero` | Zero Trust 控制台 BFF 与前端页面（保持现有 UI 布局点亮功能） |
