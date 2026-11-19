---
title: XConnect 三层分流路由与多端兼容开发任务拆解（含试点节点基线验证）
description: 基于对 jp-xconnect-free-01 (Shared)、ph-xconnect (Plus)、jp-xconnect-02 (Pro) 三台试点节点的现网基线核查，以及对 ai-workspace-service、ai-workspace-xstream 与 ai-workspace-infra/playbooks 的源码级扫描，拆解三层分流路由、GitOps 声明同步、第三方 vless:// 无感知与 xconnect-app 自动覆盖的完整可执行开发任务单。
slug: xconnect-zero-implementation-task-breakdown-and-pilot-verification
lang: zh
tags:
  - xconnect
  - task-breakdown
  - pilot-verification
  - xconnect-edge-agent
  - xconnect-app
  - accounts
  - portal
  - gitops
---

# XConnect 三层分流路由与多端兼容开发任务拆解（含试点节点基线验证）

> [!NOTE]
> 本文档为 [05-three-tier-traffic-split-routing-and-observability.md](05-three-tier-traffic-split-routing-and-observability.md) 的工程执行拆解清单，所有文件路经、符号名称与试点节点基线事实均来自本轮实测核查与源码扫描。
>
> **节点安全边界**：先期试点仅覆盖 `jp-xconnect-free-01.svc.plus` (`Shared`)、`ph-xconnect.svc.plus` (`Plus`) 与 `jp-xconnect-02.svc.plus` (`Pro`)；**`jp-xconnect-01.svc.plus`、`us-xconnect.svc.plus`、`us-xconnect-los-angeles-custom-01.svc.plus` 保持原状不变**。

---

## 一、试点节点现网基线验证报告

| 试点节点 | 类别 / 目标池 | 硬件 / OS | 入口与核心服务状态 | Xray 资源与 `/scrape` 就绪度 | 发现的问题与前置修补项 |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **`jp-xconnect-free-01.svc.plus`** | `Shared` → `Media-Pool` | 1 vCPU / 967 MiB / Debian 13 (Linode) | `fluxgate` (`active`)<br>`xray` / `xray-tcp` (`active`)<br>`xconnect-edge-agent` (`active`)<br>`xray-exporter-xhttp/tcp` (`active`)<br>**`vector.service` (`failed`)** | Xray `26.3.27`；已存在 `geoip.dat` & `geosite.dat`；已开启 `statsOutboundUplink/Downlink`；`8080/scrape` 已导出 `dimension="outbound"` | 1. **`vector.service` 启动失败**：报错 `vector-agent-domain-env: Agent config must contain a valid agent.id`，需先补齐 `/etc/agent/account-agent.yaml` 并重启 Vector；<br>2. `xhttp` inbound 尚未开启 `sniffing`。 |
| **`ph-xconnect.svc.plus`** | `Plus` → `Media-Pool` | 1 vCPU / 960 MiB / Ubuntu 24 (KVM) | `fluxgate` (`active`)<br>`xray` / `xray-tcp` (`active`)<br>`xconnect-edge-agent` (`active`)<br>`xray-exporter-xhttp/tcp` (`active`)<br>`vector.service` (`active`) | Xray `26.3.27`；已存在 `geoip.dat` & `geosite.dat`；已开启 `statsOutboundUplink/Downlink`；`8080/scrape` 已有真实 `direct` 上下行字节 | 1. `xhttp` inbound 尚未开启 `sniffing`；<br>2. `/etc/vector/vector.toml` 尚未注入 `routing_pool` / `pricing_group` 标签。 |
| **`jp-xconnect-02.svc.plus`** | `Pro` → `Pro-EC2-Pool` | DNS: `35.79.83.48` (AWS 东京) | **SSH 当前不可达** (`Connection timed out during banner exchange`) | 控制面板 Agent 心跳正常（未直连执行只读核查） | 需核查 AWS 安全组 22 端口放行策略，或通过 `ansible-pull` + Agent 自动更新通道下发配置。 |

---

## 二、客户端兼容与 GitOps 同步架构闭环

1. **第三方 `vless://` 客户端配置无感知**：
   - 标准 `vless://` URI 保持原样（不引入私有非标 Query 参数）。
   - 用户选择不同节点即物理绑定不同服务端权益与策略：`Media-Pool` 节点（`jp-xconnect-free-01` / `ph-xconnect`）全放行无限制；`Pro-EC2-Pool` 节点（`jp-xconnect-02`）服务端强制 `blackhole` 拒绝流媒体；`Custom` 节点（保持不变）仅对白名单用户开放且全无限制。
2. **`xconnect-app` 自动下发覆盖新配置**：
   - `DesktopSyncService.syncNow` 拉取 `/api/agent-server/v1/nodes` 中的三层路由策略，幂等覆写本地 `node-<code>-config.json` 并保留 `domainStrategy`（不再被 `buildSecureDnsRoutingConfig` 强行覆写回 `AsIs`），同时在检测到活动节点配置变更时自动触发连接热重启使新分流立即生效。
3. **Web Console 页面更新 GitOps 仓库同步**：
   - 将 Clash/Mihomo 等价的三层 `proxy-groups`（`Media-Pool`、`Pro-EC2-Pool`）与 `rules` 声明文件持久化在 GitOps 仓库（`ai-workspace-infra/playbooks`），Web Console 提供可视化编辑/提交 GitOps PR 或 Commit 的能力，`accounts` 与 `ansible-pull` 均从同一份 GitOps 声明源消费同步。

---

## 三、分仓库可执行开发任务拆解（Task List）

### Workstream A：`ai-workspace-service/accounts`（控制面、5+1 分组映射、GitOps 路由源与多格式订阅）

| Task ID | 目标文件与符号点 | 具体开发改造内容 | 验证命令 |
| :---: | :--- | :--- | :--- |
| **A1** | `accounts/internal/routingpolicy/` *(新建包)*<br>`accounts/internal/agentproto/types.go` | 1. 定义三层规则规范包：Tier 1 (`DIRECT`)、Tier 2 (`Media-Pool` 优先与 `MATCH` 兜底，无限制)、Tier 3 (`Pro-EC2-Pool` AI/开发/商务办公白名单，服务端 `MediaOnProAction: "blackhole"`)，支持从 GitOps YAML 声明源加载；<br>2. 在 `agentproto.types` 新增 `RoutingPolicy` 结构体（含预留字段 `SubPoolTags []string` 及 `PublicResource bool`），嵌入 `ClientListResponse` 并在 `authorizedAgentClients` 中参与 SHA-256 `Revision` 计算。 | `go test ./internal/agentproto ./internal/routingpolicy` |
| **A2** | `accounts/internal/store/store.go`<br>`accounts/api/network_access.go`<br>`accounts/api/admin_plan_groups.go`<br>`accounts/api/free_quota.go`<br>`accounts/api/regional_pools.go` | 1. 统一 `5+1` 分组语义并修复 `segment:quota:free-3gb` vs `free-5gb` 命名漂移；<br>2. 新增 `agentResourceCustom = "custom"` 与 `Custom-Dedicated` 非公共隔离校验：禁止 `agent:configure-public` 认领 `resource:custom`，在 `registeredRegionalPools` / `regionalPoolsForUser` 中确保 `Custom` 节点仅对显式白名单用户可见，绝不混入公共 `Media-Pool` / `Pro-EC2-Pool`；<br>3. `quotaExhaustedForUser` 豁免无限制的 `Custom-Dedicated` 与 `Media-Pool` 对应流媒体放行策略。 | `go test ./api -run "TestAgentResource\|TestRegionalPools"` |
| **A3** | `accounts/internal/subscription/` *(新建包)*<br>`accounts/api/config_sync.go`<br>`accounts/api/user_agents.go`<br>`accounts/api/api.go` | 1. 新建多格式订阅生成器（Clash / Mihomo / Sing-box / Xray / One），按用户权限输出三层分流模板（`Media-Pool` 规则位于 `Pro-EC2-Pool` 之前，末尾 `MATCH,Media-Pool`）；<br>2. 完善 `config_sync.go` `respondSyncConfigSnapshot` 中的 `routes`（替换当前空切片 `[]gin.H{}`），并在 `GET /api/agent-server/v1/nodes` 返回节点的 `routingPool` / `pricingGroup` 与三层路由策略供 `xconnect-app` 消费；<br>3. 保持 `vless://` 标准格式输出不受影响，确保第三方客户端配置无感知。 | `bash scripts/test.sh` |

---

### Workstream B：`ai-workspace-service/portal`（Web Console `/panel/gateway` 与 GitOps 同步界面）

| Task ID | 目标文件与符号点 | 具体开发改造内容 | 验证命令 |
| :---: | :--- | :--- | :--- |
| **B1** | `portal/src/app/panel/gateway/page.tsx` *(新建)*<br>`portal/src/modules/extensions/builtin/user-center/routes/gateway.tsx` *(新建)*<br>`.github/capabilities/modules.yaml`<br>`portal/src/config/feature-toggles.json` | 注册并实现 `/panel/gateway` 路由与页面能力声明（当前两套 portal 均缺少该路由文件）。 | `yarn capabilities:generate && yarn capabilities:check` |
| **B2** | `portal/src/modules/extensions/builtin/user-center/lib/regionalPools.ts`<br>`AccountPanels.tsx` (`NodesTable`)<br>`UserGroupManagement.tsx`<br>参考：`components/iac/ServiceDetailView.tsx` | 1. 替换纯主机名正则识别，改用后端返回的 `routingPool` / `resourceClass` 展示标签徽章（`Media-Pool 无限制`、`Pro-EC2-Pool 白名单 & Blackhole 保护`、`Custom 专属无限制`）；<br>2. 统一 `segment:quota:free-3gb` / `free-5gb` 常量并补齐 `5+1` 分组筛选器；<br>3. 在网关/路由配置面板复用 `GitOps` 编辑提交组件模式，支持直接在 Web Console 编辑 `proxy-groups` 与 `rules` 并更新至 GitOps 仓库同步下发。 | `yarn typecheck && yarn lint && yarn test:unit` |

---

### Workstream C：`ai-workspace-xstream/xconnect-edge-agent` & `xray-exporter`（边缘三层路由渲染与统计）

| Task ID | 目标文件与符号点 | 具体开发改造内容 | 验证命令 |
| :---: | :--- | :--- | :--- |
| **C1** | `xconnect-edge-agent/internal/agentproto/types.go`<br>`internal/config/config.go`<br>`internal/agentmode/runner.go` | 1. 在 `ClientListResponse` / `xrayconfig.Client` 接收控制面下发的 `RoutingPolicy`；<br>2. 更新 `runner.go` 将节点 `opts.Agent.Pool` 与 `opts.Agent.PricingGroup` 传入 `xrayconfig.Generator` 作为本地兜底基线。 | `go test ./internal/agentmode ./internal/config` |
| **C2** | `xconnect-edge-agent/internal/xrayconfig/templates.go`<br>`generator.go`<br>`syncer.go`<br>`config/xray.xhttp.template.json` | 1. 在 `defaultTemplate` 及 xhttp/tcp 模板启用 `inbounds[].sniffing` (`enabled: true, destOverride: ["http","tls","quic"]`) 与 `policy.system.statsOutboundUplink/Downlink: true`；<br>2. 在 `Generator.Render` 新增 `applyRoutingPolicy`：对 `Pro-EC2-Pool` 渲染 `blocked-media-on-pro` (`blackhole`) 拒绝高流量流媒体/下载；对 `Media-Pool` 渲染 `pool-media-stream` + `pool-media-fallback` (`freedom` 无限制)；对 `Custom-Dedicated` 保持全直出无限制；<br>3. **关键修复 `syncer.go` (`PeriodicSyncer.sync`)**：目前热新增用户仅调 `xray api adu` 不会重载 `routing`/`outbounds`，需在 `RoutingPolicy` 或 `configHash` 变更时强制触发全量写入并执行 `restartCommand`。 | `go test ./...` |
| **C3** | `xray-exporter/exporter_test.go` *(新建)* | `exporter.go` 现网与源码已验证原生导出 `xray_traffic_{uplink,downlink}_bytes_total{dimension="outbound",target=...}` 到 `/scrape` 且不污染计费快照；补充基于 Mock gRPC `StatsServiceClient` 的回归单测确保不被过滤。 | `go vet ./... && go test ./...` |

---

### Workstream D：`ai-workspace-xstream/xconnect-app`（客户端自动下发覆盖 & 第三方无感知）

| Task ID | 目标文件与符号点 | 具体开发改造内容 | 验证命令 |
| :---: | :--- | :--- | :--- |
| **D1** | `lib/services/sync/desktop_sync_service.dart`<br>`lib/services/vpn_config_service.dart`<br>`lib/services/sqlite_node_store.dart` | 1. 保持 `parseVlessUri` / `tryGenerateXrayJsonFromVlessUri` 纯净标准解析，兼容手动/第三方 `vless://` 无感知；<br>2. 扩展 `SyncedNodeMetadata`、`_parseNode`、`VpnNode` 与 `SqliteNodeStore` (`vpn_nodes` 表迁移增加 `routing_pool` / `pricing_group`) 以解析和持久化控制面同步的三层策略与节点池标签；<br>3. 新增幂等合并方法 `VpnConfig.applySyncedRoutingConfig`，并修复 `buildSecureDnsRoutingConfig`（第 1420 行）无条件强制覆盖 `routing['domainStrategy'] = 'AsIs'` 的缺陷（允许保留 `IPIfNonMatch`）。 | `flutter analyze && flutter test` |
| **D2** | `lib/services/sync/desktop_sync_service.dart`<br>`lib/services/sync/xray_config_writer.dart`<br>`lib/utils/native_bridge.dart` | 1. 在 `XrayConfigWriter.writeConfigForNode` 计算 SHA-256 感知配置变更，同时确保带 `owner` 场景下按 `serviceName` 原地覆写而不产生重复节点；<br>2. 在 `DesktopSyncService.syncNow` 检测**当前已连接的活动节点**配置是否被覆写，若变更则自动调用 `NativeBridge` 重载 TUN / Proxy 隧道（无需用户手工重连，覆盖生效），并同步刷新持久化 iOS `PacketTunnelProfile`。 | `flutter analyze && flutter test` |

---

### Workstream E：`ai-workspace-infra/playbooks`（试点节点修复、GitOps 源与 Grafana 调度大盘）

| Task ID | 目标文件与符号点 | 具体开发改造内容 | 验证命令 |
| :---: | :--- | :--- | :--- |
| **E1** | 试点节点前置修复 & GitOps 配置源 | 1. 修复 `jp-xconnect-free-01.svc.plus` 上处于 `failed` 状态的 `vector.service`（补齐 `agent.id`）；<br>2. 在 `playbooks` 落盘统一的三层分流 GitOps 声明源（如 `config/xconnect-routing-policy.yaml`），作为 Web Console 更新同步与 `accounts` 订阅下发的单一事实来源。 | `vector validate --no-environment --config-toml /etc/vector/vector.toml` |
| **E2** | `roles/vhosts/vector-agent/defaults/main.yml`<br>`templates/xray-metrics.toml.j2`<br>`deploy_observability_agent.yml` / `pull_observability_agent.yml` | 在 `add_xray_xhttp_labels`、`add_xray_tcp_labels`（及可选 `add_labels`）VRL 中注入 `.tags.routing_pool`（`Media-Pool` / `Pro-EC2-Pool` / `Custom-Dedicated`）与 `.tags.pricing_group`（`5+1`）。 | `ansible-playbook --syntax-check deploy_observability_agent.yml pull_observability_agent.yml` |
| **E3** | `roles/docker/observability-server/files/xconnect-traffic-split-scheduling.json` *(新建)*<br>`tasks/xhttp_monitoring.yml` | 创建 Grafana 流量分类调度大盘（`datasource.uid: "victoriametrics"`, `schemaVersion: 39`），展示 `pool-media-stream` / `pool-media-fallback` / `pool-pro-ai-dev` / `blocked-media-on-pro` 实时带宽、24h 流量与 `Pro-EC2-Pool` 违例拦截告警。 | `python3 -m json.tool roles/docker/observability-server/files/xconnect-traffic-split-scheduling.json > /dev/null` |
