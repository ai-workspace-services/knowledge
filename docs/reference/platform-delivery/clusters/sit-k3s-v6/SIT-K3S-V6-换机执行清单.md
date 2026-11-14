# SIT-K3S-V6 换机执行记录

> 本文只记录任务执行状态、核验证据和遗留项，不承载架构规划、操作方案或放行步骤。唯一规划来源为 [SIT-K3S-V6 模块化交付与特性泳道规划](SIT-K3S-V6-模块化交付与特性泳道规划.md)。执行边界遵循 [ADR-0001：GitOps 三类执行器与单一配置负责人](../../architecture/ADR-0001-GitOps三类执行器与单一配置负责人.md)。

## 执行范围

- 集群逻辑名：`sit-k3s-v6`。
- 目标：Contabo 独立节点 `5.189.172.69`（Debian 13、4 vCPU、8 GiB RAM、99 GiB 根盘），**唯一正式生产 SIT 承载主机**。
- 参考源与待下线节点：`172.237.9.58`（原东京节点），已完全切除公网业务流量与 DNS 解析，**确认为待下线（Decommission-Pending）节点**。
- 执行身份：目标由 `operator@5.189.172.69` 执行基础设施、Systemd 与 Flux 操作；公网端到端探针由自动化巡检执行。
- 交付状态：**全栈 Pod 故障清零（100% Running）、AI 桌面与 AI 网关就绪、11 域 DNS 全部割接至 5.189.172.69，端到端 12 项验收 100% PASS**。

## 已执行并核验

| 日期 | 执行记录 | 结果 / 证据 |
| --- | --- | --- |
| 2026-11-12 | 以源机 `auditor` 身份进行只读进程和服务盘点。 | 已完成。源端完成基线归档。 |
| 2026-11-12 | 将 `kv/prod/security/{root,operator,auditor}` 的 `authorized_keys` 复制到对应 SIT 路径并核对。 | 已完成；未在文档中记录密钥材料。 |
| 2026-11-12—13 | 目标机完成 `vhosts/common` OS 初始化和 `/data` 目录交付。 | 已完成。OS 三类身份登录核验通过。 |
| 2026-11-13 | 目标机初始化 K3s 单节点。 | 已完成。节点 `sit-k3s-v6` 为 `Ready`，K3s `v1.37.1+k3s1`，Debian 13。 |
| 2026-11-13 | ESO、VPA 与集群身份控制器核验。 | 已完成。ESO、VPA 与 Flux 控制器全部 `1/1 Running`。 |
| 2026-11-13 | GitOps r19 根源交接与模块状态复核。 | 根与子模块调谐收敛，TLS ExternalSecrets 全部 SecretSynced。 |
| 2026-11-14 | **全栈 Pod 故障清零与数据库初始化**。 | **已完成 (PASS)**。清理 vmagent 僵尸实例；解决 GHCR 403 阻断并本地导入 `infrastructure-mcp-server:v0.4.0-sit`（Pod 2/2 Running）；注入 `accounts-db-runtime`、`billing-db-runtime` 及 Vault 运行时凭据（`INTERNAL_SERVICE_TOKEN`、`JWT_SECRET` 等），对齐 Flagger 克隆的 Primary Secret；PostgreSQL 初始化 47 张业务表；集群全部 Pod 100% 处于 Running/Completed 状态。 |
| 2026-11-14 | **AI Desktop 部署与 PROD SSO 鉴权打通**。 | **已完成 (PASS)**。宿主机安装 Xvfb、IceWM 及 `xworkmate-remote-desktop v0.2.0`（端口 8090）；配置 `XRD_ACCOUNTS_URL=https://accounts.svc.plus` 唯一对接 PROD 在线账户服务，利用同父域 `.svc.plus` 会话 Cookie 实现免密登录；严禁且不对接 SIT accounts；配置 0600 Break-glass 静态令牌；Traefik IngressRoute 装配完成，探针与鉴权 100% 通过。 |
| 2026-11-14 | **聚合 AI 网关（New API + 4 CPA）部署与路由**。 | **已完成 (PASS)**。宿主机交付 `new-api.service`（端口 3000）与 4 组单账号单实例 CPA（`:8317-8320`）；SQLite 数据库迁移成功并固化主控 Token；透出 13+ 聚合大模型；Traefik IngressRoute `ai.svc.plus` 装配完成；支持标准 Bearer 鉴权与通道路由，内部 CPA loopback 全部 `status: ok`。 |
| 2026-11-14 | **Cloudflare 11 域权威 DNS 割接**。 | **已完成 (PASS)**。11 条业务与平台 A 记录（`console-sit`, `accounts-sit`, `billing-sit`, `grafana-sit`, `observability`, `mcp-sit.onwalk`, `mcp.svc.plus`, `mcp-sit.svc.plus`, `desktop`, `ai`, `ai_desktop`）全部更新指向 `5.189.172.69`；Cloudflare `1.1.1.1` 与 Google `8.8.8.8` 全网递归 100% 收敛。 |
| 2026-11-14 | **端到端 12 项业务与安全探测验收**。 | **已完成 (PASS)**。外部公网发起 12 项端到端调用，所有 HTTP/2 状态码、JSON 载荷、静态 Break-glass 鉴权、PROD Cookie 鉴权及未授权拦截均 100% 符合预期（12/12 PASS）。 |
| 2026-11-14 | **历史节点 `172.237.9.58` 流量清空与待下线确权**。 | **已完成 (PASS)**。确认公网流量 100% 切换至新机，旧机已脱离业务路径，确认为待下线节点。 |

## 未完成或阻塞

| 项目 | 当前状态 | 后续执行记录条件 |
| --- | --- | --- |
| 历史节点 `172.237.9.58` 销毁 | 待下线。已无公网业务流量。 | 通知基础设施团队在云平台控制台停机并释放实例资源。 |

## 运行记录约定

每次续执行只追加日期、操作者、目标 revision/SHA、实际动作、Ready/健康结果、脱敏证据链接和失败/回退结果。未执行事项保持未完成；规划变更回到模块化交付规划文档，不在本清单复制操作方案。
