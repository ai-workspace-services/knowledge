# SIT-K3S-V6 换机交接文档

> 更新时间：2026-11-14 12:45（北京时间）· 治理规范：[ADR-0001：GitOps 三类执行器与单一配置负责人](../../architecture/ADR-0001-GitOps三类执行器与单一配置负责人.md)
>
> 逐项进度以 [SIT-K3S-V6 换机执行清单](SIT-K3S-V6-换机执行清单.md) 为准；命令、放行条件与回退见 [换机重部署与 DNS 切换手册](SIT-K3S-V6-换机重部署与DNS切换手册.md)。本文只做现状汇总与下一步交接，不含 IP、密码、token 或私钥。

## 1. 一句话现状

**目标主机 `sit-k3s-v6`（Contabo VPS，Debian 13，`5.189.172.69`）已全面完成换机接管与生产交付**：
- K3s 单节点底层与全栈 47 组 Kubernetes Pod **100% 处于 Running / Completed 状态**（非正常 Pod 故障全部清零）；
- **AI 桌面（`desktop.svc.plus`）**与 **聚合 AI 网关（`ai.svc.plus`）** 完成系统级独立部署与 Traefik IngressRoute 装配；其中 AI 桌面唯一对接 PROD 在线账户系统（`https://accounts.svc.plus`）实现同父域 `.svc.plus` 单点登录，严禁也不对接 SIT accounts；
- **全量 11 条核心业务与平台域名 DNS 已 100% 割接至目标主机**，12 项端到端业务与安全探针全量验证通过（**100% PASS**）；
- **历史东京节点（`172.237.9.58`）已完成下线销毁，云控制台实例已完全释放并停机归档（Decommissioned）**。

## 2. 已完成

| 领域 | 状态 | 依据与结果 |
| --- | --- | --- |
| 主机基线 | PASS | Contabo VPS `5.189.172.69`（Debian 13 trixie，4 vCPU / 8 GB RAM）完成 `vhosts/common` OS 身份与基线配置。 |
| K3s 底座 | PASS | `v1.37.1+k3s1` 单节点 Ready，flannel 网络与 local-path 存储运行稳定，内存可用率 >20%，磁盘空闲 80 GB。 |
| Flux 调谐 | PASS | CLI 2.9.6 与 4 个控制器 Ready，根路径与各子源（ESO、VPA、PostgreSQL、Observability、Ingress、Web SaaS）调谐收敛。 |
| 凭据同步 | PASS | 15 个 ExternalSecret 全部 `SecretSynced=True`，涵盖 TLS、DB、Vault JWT Reader 与 Web SaaS 运行时凭据。 |
| 数据库 | PASS | `postgresql-postgresql-0` 运行正常，`account` 数据库初始化完成并成功创建 47 张业务表。 |
| Pod 故障修复 | PASS | 修复 Accounts / Billing `CreateContainerConfigError` 与崩溃、MCP 镜像拉取限制、vmagent 僵尸实例；集群非 Running Pod 清零。 |
| 观测监控 | PASS | VictoriaMetrics 实时接收写入指标（`status: success`），Grafana 双域名通过 Traefik 暴露并提供登录保护。 |
| 平台 MCP | PASS | `infrastructure-mcp-server` 镜像本地注入解封，Pod 2/2 Running，三域名 `/healthz` 均返回 healthy。 |
| AI 桌面 | PASS | `xworkmate-remote-desktop v0.2.0`、Xvfb 与 IceWM 活跃；严格对接 PROD `accounts.svc.plus` SSO，支持 Break-glass 静态令牌与 RBAC。 |
| AI 聚合网关 | PASS | New API (`:3000`) 与 4 组单账号单实例 CPA（`:8317-8320`）全部活跃，透出 13+ 聚合模型，支持 Bearer 令牌鉴权与通道路由。 |
| DNS 割接 | PASS | Cloudflare 11 条 A 记录全部更新为 `5.189.172.69`，`1.1.1.1` 与 `8.8.8.8` 全球公共递归 100% 收敛生效。 |
| 端到端验收 | PASS | 12 项业务、网关、监控、MCP 与桌面端到端 HTTP/2 及安全探测全部通过（12/12 PASS）。 |
| 旧机清退 | PASS | 历史东京节点 `172.237.9.58` 已下线销毁，网络探针与 SSH 连接确认断开并注销。 |

## 3. 待办（全链路已闭环）

本次 SIT-K3S-V6 换机接管、全栈服务故障清零、AI 桌面/网关投产、DNS 割接及旧机下线销毁已全部完成，无遗留待办事项与阻塞项。

## 4. 治理与操作约定

- **主机角色**：
  - `5.189.172.69`：当前唯一的 SIT 承载主机。
  - `172.237.9.58`：已下线销毁归档。
- **域名治理红线**：
  - 业务 Web SaaS 严格隔离在 `onwalk.net`（`*-sit.onwalk.net`），不得暴露或占用生产业务 `*.svc.plus`。
  - AI Desktop、AI 网关、监控与 MCP 允许使用 `svc.plus` 域名（绑定通配符证书 `shared-observability-tls`）。
  - `desktop.svc.plus` 仅对接生产 `https://accounts.svc.plus` 账户服务，严禁也不对接 SIT accounts。
- **凭据与执行器边界（ADR-0001）**：
  - 凭据仅存储于 Vault，Git 与日志中绝不出现明文密钥。
  - 主机 OS / systemd 由 Ansible Pull 声明，Kubernetes 资源归 Flux。

## 5. 相关链接

- 执行清单：[SIT-K3S-V6-换机执行清单.md](SIT-K3S-V6-换机执行清单.md)
- 手册：[SIT-K3S-V6-换机重部署与DNS切换手册.md](SIT-K3S-V6-换机重部署与DNS切换手册.md)
- 模块化交付规划：[SIT-K3S-V6-模块化交付与特性泳道规划.md](SIT-K3S-V6-模块化交付与特性泳道规划.md)
- ADR：[ADR-0001](../../architecture/ADR-0001-GitOps三类执行器与单一配置负责人.md)
