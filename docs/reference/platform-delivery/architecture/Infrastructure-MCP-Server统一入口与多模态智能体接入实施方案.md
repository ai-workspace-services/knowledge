# Infrastructure-MCP-Server (mcp.svc.plus) 统一入口与多模态智能体接入实施方案

> **发布基线**：2026-11-10 · **源码状态**：PR #12（已合入 `main`）· **GitOps 提交**：PR #863（已合入）  
> **服务入口**：`https://mcp.svc.plus` · **聚合中枢**：Infrastructure MCP Server (含 ssh-mcp-server)

---

## 1. 架构目标与基础设施中枢

1. **统一入口与域名绑定**：
   - 入口 FQDN：`https://mcp.svc.plus`（SIT-K3S-V6 宿主机 `172.237.9.58:443`）
   - Traefik IngressRoute 绑定权威 Let's Encrypt 证书 `shared-observability-tls`（`*.svc.plus, svc.plus`），提供标准 HTTPS/H2 访问，无需跳过证书验证。
   - 兼容保留原 `mcp.sit.onwalk.net` 与 `mcp-sit.onwalk.net`。
2. **统一聚合中枢（Unified MCP Gateway）**：
   - 上游直连各智能体（Claude, Cursor, Antigravity, Third-Party AI Agent Teams）。
   - 下游统一级联聚合：
     - `ssh-mcp-server`（受控 SSH 节点运维通道）
     - `mcp-grafana`（`:8000/v1/grafana/sse` 大盘与告警通道）
     - `mcp-victoriametrics`（`:8428` 指标 TSDB）
     - `mcp-victorialogs`（`:9428` 高基数日志）
     - `mcp-victoriatraces`（`:10428` 分布式链路 - 可选）
     - `Blackbox` 探测（`:9115` HTTP/TCP 探活）
3. **四种智能体 / 客户端接入模式全支持**：
   - **Mode 1: Web REST API**（`/api/v1/tools`, `/api/v1/catalog`, `/api/v1/flagger`, `/api/v1/gateway`, `/api/v1/cmdb`, `/api/v1/graph`, `/api/v1/telemetry/*`, `/api/v1/domains`）
   - **Mode 2: MCP 通用工具调用接口**（`POST /api/v1/tools/call`）
   - **Mode 3: SSE 实时事件推流**（`/api/v1/events` 与 MCP 标准 `/sse`）
   - **Mode 4: 标准 JSON-RPC 2.0 stdio 管道**（标准 stdin/stdout）
4. **全维度资源与遥测查询能力**：
   - `catalog`：统一三级路由与微服务 API 目录
   - `flagger`：灰度发布进度、流量切分权重、Canary 状态、门禁判定
   - `gateway`：网关（Traefik/Caddy）路由映射、TLS 证书、域名状态
   - `cmdb`：基础设施资产、计算节点、服务库存
   - `graph`：环境依赖拓扑图谱与连通子图
   - `资源拓扑`：多集群（PROD-K3S-V6 / SIT-K3S-V6）及服务拓扑
   - `域名 API 接口`：全量域名映射、路由探针与观测指标
   - `指标 (Metrics)`：VictoriaMetrics PromQL/MetricsQL 直查
   - `日志 (Logs)`：VictoriaLogs LogsQL 直查
   - `链路 (Traces)`：VictoriaTraces 链路 Span 直查

---

## 2. 实施与验证状态（全部完成）

1. [x] **`Infrastructure-MCP-Server` 代码拓展 (PR #12 已合并至 main)**：
   - 扩充内置工具集至 17 个：`infra.gateway.query`、`infra.domains.query`、`infra.topology.query`、`infra.metrics.query`、`infra.logs.query`、`infra.traces.query`；
   - 拓展 REST 路由：`/api/v1/gateway`、`/api/v1/domains`、`/api/v1/graph`、`/api/v1/topology`、`/api/v1/telemetry/metrics`、`/api/v1/telemetry/logs`、`/api/v1/telemetry/traces`；
   - 拓展 SSE 事件推流：推送 `flagger_status`、`gateway_status`、`telemetry_ping`；
   - 升级元数据卡片说明，清晰标注 4 种接入模式；
   - 单元测试 `go test -v ./...` 100% 通过。
2. [x] **GitOps 配置更新 (PR #863 已合并至 main)**：
   - 在 `services/sit-k3s-v6/ingress-sit/traefik-routes.yaml` 中配置 `sit-mcp-svc-plus-routes`，匹配 `Host(mcp.svc.plus) || Host(mcp-sit.svc.plus)`，绑定 Let's Encrypt 证书 `shared-observability-tls`；
   - 更新 `deployment-infrastructure-mcp.yaml` 镜像至 `v0.3.0-sit`；
   - 保持向后兼容支持 `mcp.sit.onwalk.net`。
3. [x] **构建、打包与集群上线**：
   - 镜像 `ghcr.io/ai-workspace-infra/infrastructure-mcp-server:v0.3.0-sit` 成功导入 SIT containerd；
   - Pod `infrastructure-mcp-server-c6ff78cd-knpf4` 在 `platform-mcp-sit` 命名空间 1/1 Running。
4. [x] **外部真实域名实盘验证 (`https://mcp.svc.plus`)**：
   - TLS 证书验证合法（Let's Encrypt 签发，CN=svc.plus，SAN 包含 `*.svc.plus`）；
   - Mode 1 Web REST API 验证通过；
   - Mode 2 MCP Tool Call (`POST /api/v1/tools/call`) 验证通过；
   - Mode 3 SSE 事件流 (`/api/v1/events?env=sit`) 验证通过；
   - Mode 4 标准 JSON-RPC 2.0 stdio 管道验证通过。
5. [x] **环境清理**：
   - 宿主机 `/tmp` 临时镜像包及构建目录已全部清理完成。
