# `accounts` 纯净回归与非核心服务双形态拆分演进规划

> [!NOTE]
> **关联文档导航**：
> - 集群总览与演进基线：[PROD-K3S-V6-模块化交付与特性规划.md](./PROD-K3S-V6-模块化交付与特性规划.md)
> - XConnect 控制面拆分与状态持久化专项规划：[11-xconnect-controller-accounts-split-and-persistence-plan.md](../../../xconnect-zero-control-data-plane/11-xconnect-controller-accounts-split-and-persistence-plan.md)
>
> 本文档沉淀 **2026-11-27** 对 `accounts` 线上日志（`prod-k3s-v6`）、代码边界与 Cloudflare Workers Free 配额的联合审计结论，明确 **`marketing-email-service` 仅走 VPS/K3s Go 自部署微服务（不启用 Cloudflare Worker）**，其余满足边缘运行条件的非核心服务采用 **Cloudflare Worker Free 优先 + 本地 Go 自部署兜底** 的双形态调度，并给出分阶段（Wave 1 → Wave 4）可落地工程路线图。

---

## 一、核心结论与服务拆分决策矩阵

### 1.1 为什么 `accounts` 当前仍存在慢请求与重启？
从 `prod-k3s-v6` `web-saas-accounts-primary` 线上日志与源码对照确认：
1. **营销与引导邮件后台循环（`startEmailWorker`）**：[email_campaigns.go](https://github.com/ai-workspace-services/accounts/blob/main/api/email_campaigns.go#L464-L496) 每 `10s` 启动 `45s` 上下文扫表，执行 `email_onboarding_steps` 事务插入（线上实测单条 SQL `33.2s`、`context deadline exceeded`）与 SMTP 批量发送，拖累 `/readyz` 探针返回 `503`。
2. **`Agent-Server` 节点高频轮询内嵌全表写对账**：近 500 条请求日志中 `/api/agent-server/v1/{status,users,nodes}` 占 **105 条**；[agent_server.go](https://github.com/ai-workspace-services/accounts/blob/main/api/agent_server.go#L128-L140) 在每次 `GET /api/agent-server/v1/users` 读路径内遍历全量用户并串行调用 `archiveInactiveFreeUser` + `ensureExpiredSubscriptionDowngrade`，导致 `19s–21s` 延迟尖刺。

### 1.2 非核心服务拆分布局矩阵

| 服务名称 | 部署形态 | 是否开 CF Worker | 数据与凭据边界 | 对 `accounts` 收益与稳定性保障 |
|---|---|---|---|---|
| **`marketing-email-service`** | **纯 Go 自部署独立微服务（VPS / K3s）** | **否（关闭 Worker）** | 共享 PG 营销表（`email_campaigns`、`email_deliveries`、`email_onboarding_steps`、`email_preferences`、`email_suppressions`）+ 复用 `web-saas-secrets` 的 `SMTP_*`；只读 `accounts` 用户/订阅视图 | 1. CF Worker Free 无原生 TCP SMTP（587/465）且无免费 Queues；<br>2. **注册验证码、找回密码、MFA 恢复等强实时认证事务邮件保留在 `accounts` 内直连 SMTP**，保证核心找回密码 100% 不受营销队列重试影响；<br>3. 彻底消除 `accounts` 内 `startEmailWorker` `33s` 阻塞与重启 |
| **`xconnect-controller`**（已完成 Overlay，补齐 **Agent-Server + Sync**） | **双形态：CF Worker Free 优先 + Go 自部署兜底** | **是**（`workers/xconnect-controller-edge` + Edge Cache） | JWKS 离线验签（`accounts/.well-known/jwks.json`）+ PG（Cloudflare Tunnel + Hyperdrive Free / 直连）；SSE 长连接与超限流量回切 Go 兜底 | 承接剩余 `/api/agent-server/v1/*`、`/api/agent/nodes`、`/api/auth/sync/*`、`/api/internal/nodes/heartbeat`、`/api/observability/internal/xconnect/identity`，彻底清空 `accounts` 高频节点轮询 |
| **`portal-public-config`** | **双形态：CF Worker Free 优先 + Go 兜底** | **是**（Workers + KV/Cache API） | `homepage-video`、`/api/internal/public-overview`、`/api/internal/sandbox/guest` | 纯读多写少、零核心状态；CF Worker KV/Cache 全球免费扛匿名突发流量（<5ms），本地 `web-saas-content` 或 Go 兜底 |
| **`task-session-orchestrator`** | **双形态：CF Worker Free 优先 + Go 兜底** | **是**（SQLite Durable Objects / Hyperdrive） | `task_namespaces`、`task_sessions`、`task_session_events`、`task_runs` + `TASK_SCHEDULER_TOKEN` | 与用户/计费零外键耦合；DO SQLite（Free 100k req/day + 13k GB-s/day）天然适配单会话顺序 `seq` 与 `fence` 租约抢锁 |
| **`xworkmate-profile-bridge`** | **Go 自部署优先 + 可选 CF Worker 边缘自省** | **可选**（仅 `/bridge/credentials/introspect` 等无 Vault 管理接口适合 Worker） | `tenants`、`tenant_domains`、`xworkmate_profiles`、`bridge_credentials` + Vault KV HTTP | 把 `XWORKMATE_VAULT_TOKEN` 彻底移出 `accounts` Pod，缩减核心 IAM 凭据暴露面 |

---

## 二、Cloudflare Worker Free 资源约束、XConnect Tunnel 集成与 Go 兜底调度策略

Cloudflare Free 方案关键配额（2026 核实基线）：
- **Workers**：`100,000 req/day`，单次请求 `10ms CPU` 硬上限；
- **Hyperdrive**：约 `100,000 queries/day`（支持 **Workers VPC TCP Service → Cloudflare Tunnel** 访问私网数据库）；
- **Durable Objects（SQLite）**：`100,000 req/day`，`13,000 GB-s/day`；
- **KV**：`100,000 reads/day`，`1,000 writes/day`，`1 GB`。

### 2.1 Cloudflare Tunnel 使用 XConnect Gateway/One 打通集成
相比在 `prod-k3s-v6` 单节点 K3s 内部额外运行 `cloudflared` Pod，直接复用现网已稳定的 **XConnect Zero Overlay Mesh（`10.67.0.0/24`）** 与 **XConnect Gateway（`jp-xconnect-gateway-01` `10.67.0.1`，可用内存 `1330 MiB`）/ `xconnect-one`**：

```text
Cloudflare Worker (Free)
  └─> Hyperdrive / Workers VPC TCP Service (port 5432)
        └─> Cloudflare Tunnel (cloudflared 运行于 jp-xconnect-gateway-01 [10.67.0.1])
              └─> XConnect Zero WireGuard Mesh (signed Ed25519 policy_json ACL)
                    └─> prod-k3s-v6 xconnect-one (10.67.0.2:5432 -> ClusterIP 10.55.35.251:5432)
```

- **双重零信任隔离**：
  - **外层（Cloudflare）**：通过 `wrangler vpc service create ... --type tcp --tcp-port 5432 --app-protocol postgresql --tunnel-id <TUNNEL_ID> --ipv4 10.67.0.2` 与 Hyperdrive Private DB 绑定，PostgreSQL **不暴露公网端口**。
  - **内层（XConnect Zero）**：`10.67.0.2:5432`（转发至 `postgresql-postgresql.postgresql-prod.svc.cluster.local:5432`）仅在签名下发的 `policy_json` 中对网关/Tunnel Connector `device_id` 放行，其他 Overlay 终端一律默认拒绝。
- **防自环死锁约束（Critical）**：
  - **基础设施组网链路严禁经由自身隧道依赖的 Worker 回源**：`jp-xconnect-gateway-01` 与 `prod-k3s-v6` `xconnect-one` 节点的控制面引导、凭据刷新与配置同步（`/api/overlay/v1/*`）**必须直连 Go 自部署入口**（`accounts-selfhost-prod-v6.svc.plus` / K3s Traefik），确保即使 Cloudflare Tunnel 或 Worker 异常，底层 WireGuard Mesh 仍可独立自愈拉起。
- **单点隧道复用 & 零 K3s 内存挤占**：`jp-xconnect-gateway-01` 上的单个 `cloudflared`（仅 ~25–40 MiB）即可同时覆盖 `prod-k3s-v6`（`10.67.0.2`）、`sit-k3s-v6`（`10.67.0.3`）等经 XConnect Mesh 互联的多集群私网服务。

### 2.2 调度与兜底规则（Free 资源最大化 + 零单点故障）
1. **边缘 Cache API / KV 优先拦截读请求**：`signing-keys`、`policy-artifacts/:gen/:digest`、`homepage-video`、`/api/auth/sync/subscription` 优先命中 Cloudflare Edge Cache / KV（`ETag`/`304`），不消耗 Hyperdrive 查询配额。
2. **协议与长连接能力分流**：Worker Free 不适合常驻长挂 SSE（`/api/agent-server/v1/users/events`），默认由 **Cloudflare Route / Traefik** 路由回本地 Go 兜底实例，或通过 DO WebSocket/轮询模式降级兼容。
3. **配额与异常自动兜底（Failover）**：
   - 公网高频客户端/门户静态与中等频度控制面请求优先进入 Cloudflare Worker（Cloudflare Custom Route）；
   - 当 Worker Free 配额接近日上限（HTTP `429`/`1027` 或超出 10ms CPU）或 Cloudflare Tunnel 抖动时，通过 Cloudflare Origin Rule / 客户端降级路由直接回落到 `prod-k3s-v6` Traefik 背后的 Go 自部署 Pod（如 `web-saas-xconnect-controller`）。

---

## 三、`accounts` 终态边界（纯 IAM + 订阅 + 计费核心服务）

完成全部拆分后，`accounts` 仅保留强一致核心域：
1. **身份与认证（IAM + 强实时事务邮件）**：
   - `/api/auth/{login,register*,oauth*,mfa*,password*,session,token*,refresh}`、`/.well-known/jwks.json`、`/api/users`
   - 注册验证码、找回密码、MFA 恢复直接通过轻量 `SMTP_*` 发送器投递（**独立于营销邮件队列**）。
2. **订阅、团队商业权益与账务计费**：
   - `/api/billing/*`、`/api/auth/stripe/*`、`/api/auth/subscriptions*`、`/api/referrals*`、`/api/account/*`
   - `/api/auth/network-access`、`/api/auth/network-team*`、`/api/auth/admin/agents/grants`、`/api/auth/admin/agents/team-enrollments`、`/api/auth/admin/users/:userId/network-access`
   - 内部权威只读契约：`GET /api/internal/network/identities`、`GET /api/internal/policy/:accountUUID`
3. **后台任务收敛**：仅保留轻量、限批的 `annual-quota` 与 `subscription-access`（`StartSubscriptionAccessReconciler` 每分钟最多 500 用户）。

---

## 四、四阶段（Wave 1 → Wave 4）执行计划

### Wave 1：`accounts` 立即止血 + 开关固化 + `xconnect-controller` 吸收 Agent-Server（立即开始）
1. **`accounts` 稳定化与解耦开关**：
   - 移除 `GET /api/agent-server/v1/users`（`authorizedAgentClientsWithPolicy`）读路径内的同步全表写循环（`archiveInactiveFreeUser` + `ensureExpiredSubscriptionDowngrade`），彻底依赖已上线的异步有界对账器 `StartSubscriptionAccessReconciler`。
   - 新增开关（保持零中断平滑过渡）：
     - `ENABLE_MARKETING_EMAIL_WORKER`（支持关闭 `accounts` 进程内 10s 营销邮件/onboarding 循环而不影响找回密码与注册验证码）
     - `ENABLE_LEGACY_AGENT_SERVER_ROUTES`（先保留 `true`，待 `xconnect-controller` 承接并切流后切为 `false`）
     - 保持 `ENABLE_LEGACY_OVERLAY_ROUTES=false`（已由 PR #345 下线，确认无回退需求后在 Wave 4 删除遗留代码）。
2. **扩展 `xconnect-controller`（Go 形态 A + TS Worker 形态 B）承接 Agent-Server + Sync**：
   - 迁入 `/api/agent-server/v1/*`（使用只读 PG 视图/查询 + `ETag`）、`/api/agent/nodes`、`/api/auth/sync/*`、`/api/internal/nodes/heartbeat`、`/api/observability/internal/xconnect/identity`。
   - 更新 `gitops` `traefik-routes.yaml`，将 `/api/agent-server`、`/api/agent`、`/api/auth/sync`、`/api/internal/nodes`、`/api/observability/internal/xconnect` 高优先级路由切换至 `web-saas-xconnect-controller`。
   - 将 `accounts` 的 `ENABLE_LEGACY_AGENT_SERVER_ROUTES` 切换为 `false` 并上线验证。

### Wave 2：独立 Go 微服务 `marketing-email-service`（VPS/K3s，不开 Cloudflare Worker）
1. 将营销活动、邮件引导序列、退订/偏好（[email_campaigns.go](https://github.com/ai-workspace-services/accounts/blob/main/api/email_campaigns.go)、[marketing_email.go](https://github.com/ai-workspace-services/accounts/blob/main/api/marketing_email.go)、[email_preferences.go](https://github.com/ai-workspace-services/accounts/blob/main/api/email_preferences.go)、`internal/service/email_*`）拆为独立 Go 服务 `marketing-email-service`（内置 JWKS 离线验签、50m/128Mi 轻量 Deployment、复用 `web-saas-secrets` 的 `SMTP_*`）。
2. 在 `artifacts` `web-saas-fullstack` Chart 新增 `marketingEmail` 子 Chart 并发布 OCI Chart。
3. 通过 Traefik 将 `/api/auth/admin/email-*`、`/api/auth/email-preferences`、`/api/auth/email-unsubscribe` 路由至 `web-saas-marketing-email`；确认线上 SMTP 营销投递 & `accounts` 找回密码/注册验证邮件双双正常后，关闭 `accounts` 的 `ENABLE_MARKETING_EMAIL_WORKER=false` 与 `ENABLE_LEGACY_MARKETING_EMAIL_ROUTES=false`。

### Wave 3：打通 XConnect Gateway/One ↔ Cloudflare Tunnel + Hyperdrive Free，调度非核心服务上线
1. **XConnect Gateway/One 集成 Cloudflare Tunnel（替代 K3s 单节点新增 `cloudflared` Pod）**：
   - 在 `jp-xconnect-gateway-01`（`10.67.0.1`）通过 Ansible Role / systemd 部署并纳管 `cloudflared`，保持 Gateway 与 `prod-k3s-v6` `xconnect-one`（`10.67.0.2`）的控制面直连 Go 入口（`accounts-selfhost-prod-v6.svc.plus`）以防止自环死锁；
   - 在 `prod-k3s-v6` 的 `xconnect-one` 侧配置私网端口转发（仅向签名 `policy_json` 授权的 `jp-xconnect-gateway-01` 开放 `10.67.0.2:5432 -> 10.55.35.251:5432`）；
   - 通过 `wrangler vpc service create` 创建 Workers VPC TCP Service（`--tcp-port 5432 --app-protocol postgresql --ipv4 10.67.0.2`）并绑定 Cloudflare Hyperdrive Config（落实原 `T3.3`）。
2. 上线 `workers/xconnect-controller-edge`（含 Overlay + Agent-Server/Sync 只读边缘缓存），配置业务流量走 Cloudflare Worker Route 与本地 Go `web-saas-xconnect-controller` 兜底回切验证。
3. 依次以「CF Worker Free 主力 + Go 兜底」落地：
   - `portal-public-config`（Workers + KV/Cache，本地 Go 兜底）
   - `task-session-orchestrator`（Workers + SQLite Durable Objects / Hyperdrive，Go 服务兜底）
   - `xworkmate-profile-bridge`（Go 服务承接 Vault + Profile，可选 Worker 边缘自省 `/bridge/credentials/introspect`）

### Wave 4：`accounts` 收尾清理（纯 IAM + 订阅 + 计费终态）
1. 线上各拆分服务稳定运行观察期结束后，在 `accounts` 仓库正式移除 `internal/overlay`、`api/overlay*.go`、`api/agent_server.go`、`api/email_campaigns.go`、`api/task_sessions*.go`、`api/xworkmate*.go`、`api/homepage_video.go` 等已下线模块，裁剪二进制体积与连接池占用，完成完全解耦。
