---
title: 全链路接口契约、数据模型与控制台对齐规范
description: 详述 XConnect-Gateway、xconnect-edge-agent、XConnect-One、accounts.svc.plus 与 console.svc.plus/panel/xconnect-zero 之间的接口契约、字段定义与安全校验边界。
slug: xconnect-zero-wire-contracts-and-apis
lang: zh
tags:
  - xconnect-zero
  - api-contract
  - telemetry
  - accounts
  - portal
---

# 全链路接口契约、数据模型与控制台对齐规范

## 一、`XConnect-Gateway` ↔ `xconnect-edge-agent` 本地契约

### 1.1 本地配置应用契约（控制面下发）

由 `xconnect-edge-agent`（`role: gateway`）负责向 `accounts.svc.plus` 拉取 `GatewaySignedConfig`、校验 Ed25519 签名与 `generation` 单调性，并在本地落盘后触发 `XConnect-Gateway` 纯数据面应用：

- **落盘文件**（`0700` 目录 / `0600` 文件）：`<gateway-state-dir>/runtime/signed-config.json`
- **本地应用命令**：
  ```bash
  xconnect-gateway apply \
    --state-dir /var/lib/xconnect-gateway \
    --config /var/lib/xconnect-gateway/runtime/signed-config.json \
    --frontend caddy-unix-h2c \
    --listen-socket /run/xconnect-gateway/xray.sock
  ```
- **核心行为（独立于 Agent Proxy 的 Xray 后端）**：
  1. 解析 `GatewaySignedConfig.connection_mode`（`wg_vless_l3` / `wg_udp_l3` / `wg_vless_l2`）：
     - `wg_vless_l3`：渲染独立的 `/var/lib/xconnect-gateway/runtime/xray.json`（使用宿主共享的 `xray-core` 二进制，独立进程 `xconnect-gateway-xray.service`，监听 `/run/xconnect-gateway/xray.sock` 或独立 TLS 端口，开启本地独立 Stats API 如 `127.0.0.1:10087`）+ WireGuard `xconzero0` + Peer Relay。
     - `wg_udp_l3`：应用 WireGuard `xconzero0` 公网 UDP 端口（`listen_port`）与对等端配置，允许直连流量进入；按需保持或关闭 Xray VLESS 入口。
     - `wg_vless_l2`：预留 Linux L2/TAP 桥接模式字段校验与能力标记。
  2. 执行 `xray run -test -config <gateway-xray.json>`，通过后仅重启/重载 `xconnect-gateway-xray.service`（**严禁触碰 Agent Proxy 的 `xray.service` 与 `/usr/local/etc/xray/config.json`**）。
  3. 对 WireGuard 执行无损 `wg syncconf` 与路由调和（`reconcileWireGuardRoutes`）。
  4. 返回结构化退出状态与已应用摘要（`config_id`、`generation`、`xray_config_sha256`），由 `xconnect-edge-agent` 据此向 `accounts.svc.plus` 发送 ACK。

### 1.2 本地非敏感遥测导出契约（采集上报）

`XConnect-Gateway` 周期性（如每 10s，原子写 `.tmp` → `rename`，权限 `0640`/`0600`）输出以下两类**严格不含私钥与 Bearer 凭据**的只读 JSON 文件（亦可通过 `xconnect-gateway status --json` 触发即时采集）：

1. **`<gateway-state-dir>/runtime/overlay-status.json`**（沿用并对齐 `xconnect-edge-agent/internal/agentproto.OverlayStatus`）：
   ```json
   {
     "network_id": "net_prod_jp",
     "device_id": "gw-jp-01",
     "role": "gateway",
     "capabilities": ["wg_vless_l3", "gateway-relay-v1", "caddy-unix-h2c"],
     "healthy": true,
     "updated_at": "2026-11-17T12:30:00Z",
     "expires_at": "2026-11-17T12:31:00Z",
     "paths": [
       {
         "device_id": "one-macbook-01",
         "path": "vless-xhttp",
         "endpoint": "203.0.113.10:54321",
         "rtt_ms": 28,
         "sent_packets": 14200,
         "received_packets": 18950,
         "reason": "handshake_recent"
       }
     ]
   }
   ```
   > 注意：需同步放宽 `xconnect-edge-agent` 中 `readOverlayStatus` 对 `path` 枚举值的校验，支持 `direct-lan`、`relay`、`vless-xhttp`、`wg-udp`。

2. **`<gateway-state-dir>/runtime/gateway-telemetry.json`**（供 `xconnect-edge-agent` 汇总上报 SASE 与连接分析）：
   ```json
   {
     "schema_version": 1,
     "network_id": "net_prod_jp",
     "gateway_id": "gw-jp-01",
     "endpoint_host": "gw-jp-01.svc.plus",
     "connection_mode": "wg_vless_l3",
     "applied_config_id": "cfg_...",
     "applied_generation": 12,
     "wireguard_running": true,
     "xray_running": true,
     "relay_running": true,
     "relay_active_sessions": 4,
     "sampled_at": "2026-11-17T12:30:00Z",
     "expires_at": "2026-11-17T12:31:00Z",
     "traffic": {
       "rx_bytes_total": 1073741824,
       "tx_bytes_total": 2147483648,
       "internet_rx_bytes": 600000000,
       "internet_tx_bytes": 1200000000,
       "private_rx_bytes": 473741824,
       "private_tx_bytes": 947483648
     },
     "peers": [
       {
         "device_id": "one-macbook-01",
         "wireguard_address": "10.77.0.10/32",
         "connected": true,
         "path": "vless-xhttp",
         "latest_handshake_at": "2026-11-17T12:29:48Z",
         "rx_bytes": 52428800,
         "tx_bytes": 104857600,
         "rtt_ms": 28
       }
     ],
     "top_apps": [
       { "app": "ssh (tcp/22)", "rx_bytes": 10485760, "tx_bytes": 20971520, "connections": 3 },
       { "app": "https (tcp/443)", "rx_bytes": 512000000, "tx_bytes": 1024000000, "connections": 42 }
     ]
   }
   ```
   - `xconnect-edge-agent` 遵循既有安全红线：只读取**绝对路径、非 symlink、大小不超过限额（如 256 KiB）的普通文件**，按强类型结构体白名单反序列化并校验 `NetworkID`、`GatewayID/NodeID` 与 `ExpiresAt` 未过期，丢弃所有未知字段。

---

## 二、`xconnect-edge-agent` → `accounts.svc.plus` 上报与控制契约

### 2.1 Gateway 状态与遥测上报（`POST /api/agent-server/v1/status`）

扩展 `agentproto.StatusReport`（`xconnect-edge-agent` 与 `accounts` 两仓同步定义）：

```go
type StatusReport struct {
    Overlay          *OverlayStatus    `json:"overlay,omitempty"`
    GatewayTelemetry *GatewayTelemetry `json:"gatewayTelemetry,omitempty"`
    AgentID          string            `json:"agentId"`
    Role             string            `json:"role,omitempty"`
    Healthy          bool              `json:"healthy"`
    Message          string            `json:"message,omitempty"`
    HeartbeatAt      time.Time         `json:"heartbeatAt"`
    Users            int               `json:"users"`
    SyncRevision     string            `json:"syncRevision,omitempty"`
    Xray             XrayStatus        `json:"xray"`
}
```

- `accounts` 侧 `reportAgentStatus`（`api/agent_server.go`）在校验 `identity.NodeID` 与边界长度后：
  1. 校验 `report.GatewayTelemetry` 绑定关系（`NetworkID`、`GatewayID == identity.NodeID`、非空且 `Peers <= 512`、`TopApps <= 64`）；
  2. 调用 `h.overlayService.RecordRuntimeObservation` **不仅更新 `overlay_devices.last_seen_at`**，同时将实时遥测与每 Peer 增量/快照写入 PostgreSQL 遥测表；
  3. 若发现设备处于 `revoked` 状态，拒绝观测更新并返回明确拒绝（触发 Edge Agent 侧告警与配置收敛）。

### 2.2 Gateway 控制面同步（`xconnect-edge-agent` 接管）

`xconnect-edge-agent`（`role: gateway`）接管以下 `accounts.svc.plus` 接口调用（原在 `XConnect-Gateway/internal/gateway/client.go` 中）：
- `POST /api/overlay/v1/device/session`：使用节点受保护的 `DeviceCredential` 换取短期 `EnrollmentToken`；
- `GET /api/overlay/v1/gateway/signed-config`：拉取最新 `GatewaySignedConfig`（校验 `ETag` 与 Ed25519 签名）；
- `POST /api/overlay/v1/enrollment/signed-config/:generation/ack`：在 `xconnect-gateway apply` 成功并验证接口/Xray/Relay 健康后回传 ACK。

---

## 三、`XConnect-One` ↔ `accounts.svc.plus` 统一登录与 Gateway 选点契约

### 3.1 登录认证命令（`xconnect login` / `xconnect logout`）

1. **账号密码 + MFA 登录**：
   - 调用 `accounts.svc.plus` 既有 `POST /api/auth/login`（请求体携带 `identifier` + `password` + 可选 `totp`）；
   - 当返回 `mfaRequired: true` 与 `mfaTicket` 时，交互提示输入 6 位 TOTP 验证码二次提交完成换票；
   - 严禁通过 CLI Flag 传明文密码（仅允许交互隐藏读取或 `--password-stdin` / `--token-file`）。
2. **浏览器 OAuth / SSO 登录**：
   - `xconnect login --web --server https://accounts.svc.plus [--provider github|google]`；
   - 本地监听 `127.0.0.1:<ephemeral_port>/callback`，引导浏览器打开 `accounts.svc.plus` 登录并在回调获取 `exchange_code` 后，调用 `POST /api/auth/token/exchange` 换取会话 `access_token`。
3. **凭据持久化**：
   - 将 `{ server, access_token, expires_at, user_email, user_id }` 安全写入平台凭据存储（macOS Keychain / Linux 0600 保护文件 / Windows DPAPI），并与设备级 `DeviceCredential` 分区存储。

### 3.2 新增：可用 Gateway Endpoint 发现（`GET /api/overlay/v1/gateways`）

挂载于 `accounts` 的 `userGroup`（受 `AuthMiddleware` + `RequireActiveUser` 保护）：

```json
{
  "gateways": [
    {
      "network_id": "net_prod_jp",
      "display_name": "JP Hybrid Mesh",
      "cidr": "10.77.0.0/24",
      "gateway_id": "gw-jp-01",
      "gateway_endpoint_host": "gw-jp-01.svc.plus",
      "gateway_endpoint_port": 51820,
      "transport_server_name": "gw-jp-01.svc.plus",
      "transport_port": 443,
      "connection_mode": "wg_vless_l3",
      "runtime_healthy": true,
      "last_seen_at": "2026-11-17T12:30:00Z",
      "connected_peers": 6
    }
  ]
}
```

### 3.3 新增：登录后直接设备注册/换证（`POST /api/overlay/v1/devices/enroll`）

在用户已登录 `accounts.svc.plus` 并选定 `network_id` + `gateway_id` 后调用（替代旧版 `/devices/register` + `/config`，并免去手动复制邀请码）：

- **请求**：
  ```json
  {
    "network_id": "net_prod_jp",
    "gateway_id": "gw-jp-01",
    "device_id": "xconnect-darwin-macbook",
    "name": "MacBook Pro",
    "platform": "darwin",
    "hostname": "macbook.local",
    "wireguard_public_key": "<base64-32B>"
  }
  ```
- **响应**（与 `ExchangeResponse` 对齐，确保后续全链路统一走 `SignedConfig v2`）：
  ```json
  {
    "enrollment_token": "xenr_...",
    "token_type": "Bearer",
    "expires_at": "2026-11-17T13:30:00Z",
    "scope": ["overlay:config:read", "overlay:config:ack", "overlay:device:revoke"],
    "device_credential": {
      "credential_id": "xdcid_...",
      "credential": "xdc_...",
      "token_type": "Device",
      "issued_at": "2026-11-17T12:30:00Z",
      "expires_at": "2026-12-17T12:30:00Z",
      "scope": ["overlay:session:mint", "overlay:credential:rotate", "overlay:device:revoke"]
    },
    "device": { "...": "..." },
    "network": { "...": "..." },
    "signing_keys": [ "..." ]
  }
  ```
- **桌面端联动（`cmd/xconnect/app_bridge.go`）**：扩展 `appBridgeMethods`，新增 `"login"`、`"logout"`、`"gateways"` 方法，并在 `appBridgeJoinParams` 中支持可选 `"gateway_id"` 与 `"endpoint"`（允许在已登录状态下免 invite 直接入网），供 `xconnect-app` 桌面端直接调用同一套认证与选点能力。

---

## 四、`accounts.svc.plus` ↔ `console.svc.plus/panel/xconnect-zero` 控制台契约

### 4.1 保持 UI 不变的后端字段增强

1. **`GET /api/overlay/v1/admin/overview`**（扩展 `AdminOverview` 非敏感字段）：
   - 保留原有 `status`、`networkCount`、`deviceCount`、`gatewayCount`、`oneCount`、`gatewayStatus`、`oneStatus`、`signingKeyId`；
   - 补充：`onlineGatewayCount`、`onlineOneCount`、`ackedDeviceCount`、`totalRxBytes`、`totalTxBytes`、`lastTelemetryAt`。
   - **状态判定融合**：结合 `overlay_signed_config_acks`（当前代 ACK）与 `xconnect-edge-agent` 实时上报的 `runtime_healthy` / `last_seen_at`（在活跃窗口内即视为在线），解决目前"设备已上报但未发当前代 ACK 时前端仍显示未配置/无近期确认"的问题。
2. **`GET /api/overlay/v1/admin/devices`**（扩展 `AdminDevice` 非敏感字段）：
   - 新增：`runtime_healthy`（bool）、`active_path`（`direct-lan` / `relay` / `vless-xhttp` / `wg-udp`）、`rtt_ms`、`rx_bytes`、`tx_bytes`、`applied_generation`、`connection_mode`、`latest_handshake_at`。
3. **新增 `GET /api/overlay/v1/admin/telemetry?window=1h|24h|7d`**：
   - 直接服务于 `console.svc.plus/panel/xconnect-zero` 概览页的 **4 张现有 Telemetry 卡片**：
     1. `sase_traffic`（对应 **SASE 流量分析**）：按时间桶聚合 `internet_rx_bytes`、`internet_tx_bytes`、`private_rx_bytes`、`private_tx_bytes`；
     2. `connected_users`（对应 **已连接用户**）：当前在线设备与归属用户邮箱、接入 Gateway、路径类型、RTT、最近握手；
     3. `top_private_apps`（对应 **热门专用应用程序**）：按应用/目标服务聚合流量与连接数 Top N；
     4. `top_users`（对应 **热门用户**）：按用户聚合总 RX/TX 传输量 Top N。
4. **新增 `PUT /api/overlay/v1/admin/networks/:networkID/mode`**：
   - 请求体：`{ "connection_mode": "wg_vless_l3" | "wg_udp_l3" | "wg_vless_l2" }`；
   - 权限：`xconnect.zero.manage` 且校验网络 `owner_user_id`；
   - 逻辑：校验模式合法性（`wg_vless_l2` 校验 Linux Gateway 约束），更新 `overlay_networks.connection_mode` 并**递增 `config_generation`**，重新签名后即刻被 `xconnect-edge-agent` 与 `XConnect-One` 下一次同步消费。

### 4.2 `portal` BFF 与页面映射（零破坏 UI）

| Portal 位置 | 改动内容 | UI 影响 |
| :--- | :--- | :--- |
| `src/app/api/xconnect-zero/[...segments]/route.ts` | `ALLOWED_ROUTES` 增加 `GET telemetry -> /admin/telemetry`（透传 `?window=`）；`resolveRoute` 增加 `PUT networks/:id/mode -> /admin/networks/:id/mode` | 无 UI 变更 |
| `src/lib/xconnectZero.ts` | 扩充 `XConnectZeroAdminOverview`、`XConnectZeroNetwork`、`XConnectZeroDevice` 可选只读字段，新增 `XConnectZeroTelemetry` 接口 | 无 UI 变更 |
| `xconnect-zero-node-management.tsx` (`Zero 概览`) | 1. 顶部 `账户运行状况` 4 行显示真实在线数、ACK 数与控制面连接状态<br>2. 下方 4 张 `Telemetry` 卡片保留原有外框、标题与描述，当有数据时渲染轻量级 SVG 折线/条形与明细列表，无数据时仍保留 `暂无数据` | **卡片网格、标题、结构 100% 不变** |
| `xconnect-zero-node-management.tsx` (`节点管理`) | 1. `已加入节点` 每行副标题追加 `在线/离线 · 路径 · RTT · 流量`<br>2. One 接入指南补充 `xconnect login` + Gateway 选点命令 | **沿用既有列表与折叠脚本样式** |
| `xconnect-zero-node-management.tsx` (`配置管理`) | 1. 解除 3 张 `Gateway / One 互联网络模式` 卡片的 `disabled`，支持选定网络后切换并调用 `PUT .../mode`<br>2. `IP 分配`、`WG 与签名证书` 填充真实已分配 IP 计数与 `signingKeyId` / `config_generation` | **三卡片样式与下方 2×2 配置帧保持原样** |
