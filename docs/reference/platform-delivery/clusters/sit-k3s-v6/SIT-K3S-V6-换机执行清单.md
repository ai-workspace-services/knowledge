# SIT-K3S-V6 换机执行记录

> 本文只记录任务执行状态、核验证据和遗留项，不承载架构规划、操作方案或放行步骤。唯一规划来源为 [SIT-K3S-V6 模块化交付与特性泳道规划](SIT-K3S-V6-模块化交付与特性泳道规划.md)。执行边界遵循 [ADR-0001：GitOps 三类执行器与单一配置负责人](../../architecture/ADR-0001-GitOps三类执行器与单一配置负责人.md)。

## 执行范围

- 集群逻辑名：`sit-k3s-v6`。
- 目标：Contabo 手动创建的独立节点 `5.189.172.69`，Debian 13、4 vCPU、约 8 GiB RAM、约 99 GiB 根盘；`/data` 是根文件系统上的受控分配目录，不是独立数据卷。
- 参考源：`172.237.9.58`，仅用于 auditor 只读对照，不是新 SIT 部署目标。
- 执行身份：目标由 `operator@5.189.172.69` 执行 Playbook/Flux 操作；源端使用 `auditor@172.237.9.58` 只读核查。
- 本轮约束：源端 PVC、数据库和历史观测数据未迁移。ExternalDNS 已退出 dry-run 并以 `upsert-only` 工作；本次回执未核验权威 DNS 记录及公共解析结果，不据此宣称域名已完成切换。

## 已执行并核验

| 日期 | 执行记录 | 结果 / 证据 |
| --- | --- | --- |
| 2026-11-12 | 以源机 `auditor` 身份进行只读进程和服务盘点。 | 已完成。该盘点不等同于源端完整 Kubernetes/Helm/PVC 清单；源端 auditor kubeconfig 未交付。 |
| 2026-11-12 | 将 `kv/prod/security/{root,operator,auditor}` 的 `authorized_keys` 复制到对应 SIT 路径，并回读核对。 | 已完成；未在文档中记录密钥材料。 |
| 2026-11-12—13 | 目标机完成 `vhosts/common` OS 初始化和 `/data` 目录交付。 | 已完成。OS 三类身份登录与 auditor 拒绝项完成核验；operator 的受限 sudo 已配置。目录由 root 拥有，组/其他用户不可写。Playbooks #1015。 |
| 2026-11-13 | 目标机初始化 K3s 单节点。 | 已完成。节点 `sit-k3s-v6` 为 `Ready`，K3s `v1.37.1+k3s1`，Debian 13，4 CPU、8,138,640 KiB 可分配内存。 |
| 2026-11-13 | 以 operator 身份安装 Flux CLI/控制器并交接独立 Contabo 根路径。 | 初始交接曾应用 r5；该状态已由下方 r19 交接取代。 |
| 2026-11-13 | ESO、VPA 与集群身份控制器核验。 | 已完成。ESO 三个 Pod、VPA 三个 Pod、Flux 四个控制器均为 `1/1 Running`；目标 K3s 三类身份的允许/拒绝验收已完成。 |
| 2026-11-13 | ExternalDNS dry-run 交付核验。 | 部分完成。Vault JWT 身份、SecretStore 和 ExternalSecret 为 Ready；Cloudflare API 返回 HTTP 403 / code 9109 `Invalid access token`，ExternalDNS Pod 为 `CrashLoopBackOff`。日志确认 `--dry-run`，未写入 DNS。 |
| 2026-11-13 | PostgreSQL Vault/ESO 声明 PR #904、GitOps r6 PostgreSQL rollout PR #905 合并核验。 | 当时目标 Flux 尚未接收 r6，`postgresql-sit` 仍挂起；该阶段已由后续 r19 交付取代。 |
| 2026-11-13 | GitOps r19 根源交接与模块状态复核。 | 目标 `config-sit` 切至 `sit-k3s-v6-contabo-r19`，Flux 根及各子源报告应用 SHA `84f427cdfaa2d4d98e6b5621ddbaf1f53dae0859`。身份、ESO、ExternalDNS、Ingress/Routes、Observability、PostgreSQL、VPA Kustomization 均 Ready；`observability-agent` HelmRelease UpgradeSucceeded，TLS ExternalSecret 均 SecretSynced，PostgreSQL 三个 Vault/ESO 凭据 ExternalSecret 均 SecretSynced。MCP Vault role 已按 GitOps 声明建成，ESO resync 后 SecretSynced；MCP Pod 被未发布/无权限拉取的 GHCR 镜像阻塞（403）。Web SaaS 的 SecretStore 为 Valid，但 `kv/sit/web-saas/runtime` 不存在，ExternalSecret 和 HelmRelease 未 Ready。证据为 operator 交互 shell、受限 `sudo k3s kubectl` 与只输出字段名的 Vault/JWT 校验；未读取 Secret 值。 |

## 未完成或阻塞

| 项目 | 当前状态 | 后续执行记录条件 |
| --- | --- | --- |
| GitOps r19 根源交接 | 已完成。根、子源和核心 Kustomization 已报告 r19 SHA `84f427cdfaa2d4d98e6b5621ddbaf1f53dae0859`。 | 保留 `config-sit` tag、Flux `lastAppliedRevision` 和 Ready 状态回执。 |
| PostgreSQL 凭据交付 | 基础交付完成。三个 PostgreSQL Vault/ESO ExternalSecret 与 HelmRelease 均 Ready；PVC 使用根盘 `local-path`。 | 仍需单独完成业务连接与三类数据库角色允许/拒绝验收；不记录凭据值。 |
| Observability 与 Ingress | 控制器/HelmRelease、Ingress routes 和 TLS ExternalSecret 已 Ready；本次未做所有公开域名的端到端功能验收。 | 保留当前健康状态，逐域名核对入口、证书、服务和外部回调。 |
| MCP | Vault JWT login/限定路径 read 已通过临时实际工作负载身份验证，ExternalSecret Ready；Deployment init container 因 GHCR 镜像 403 `ErrImagePull` 未启动。镜像包 API 对当前仓库查询返回 404，且没有发现已发布 tag。 | 发布/授权可拉取的固定 MCP 镜像后再通过 GitOps 更新引用，并验证 Pod 与 MCP initialize/tools/list。不可借用 feature-lane registry 凭据扩大范围。 |
| Web SaaS | SecretStore Valid；ExternalSecret 失败，因为 `kv/sit/web-saas/runtime` 不存在；HelmRelease InstallFailed，Accounts/Billing/Content Pods 因 `web-saas-secrets` 缺失未运行，Canary 依赖未 Ready。 | 凭据 owner 在既定 Vault path 提供 `JWT_SECRET`、`SESSION_SECRET` 后安全重同步；再验应用数据库连接与三组 Canary。 |
| operator sudo 最小权限 | 尚未符合规划目标。`sudo -n -l` 显示 K3s/容器工具免密规则，同时 operator 仍有密码保护的 `(ALL : ALL) ALL` 通用 sudo 规则。 | 由主机权限变更移除/收敛通用 sudo 后，用 operator 实测批准/拒绝命令，再更新状态。 |
| ExternalDNS 与 DNS | ExternalDNS Pod/HelmRelease Ready，参数无 `--dry-run` 且 `policy=upsert-only`，域名过滤包含 `onwalk.net`、`svc.plus`。Cloudflare 公共解析器 `1.1.1.1` 当前将 `ai_desktop.svc.plus`、`ai.svc.plus` 解析到 `5.189.172.69`，TLS 校验通过但 HTTPS `/` 为 404；目标缺少相应 IngressRoute/后端。`observability.svc.plus` 仍解析到旧节点 `172.237.9.58`；用 `curl --resolve` 直探新节点时 TLS 校验通过并返回 302 `/login`。 | 为 Desktop/AI Gateway 先交付主机服务或独立后端与 SIT IngressRoute，逐域名健康探测通过后记录当前 DNS/TXT 所有权和回退值。Observability 域名已有其他集群/生产远程写入依赖，未完成调用方交接前保持旧入口。 |
| 源端完整服务清单 | 未完成。auditor 仅完成主机级只读盘点，不能读取源端 Kubernetes 管理凭据。 | 获得审计身份后补充 Flux/Helm/PVC/Ingress 实际状态；不得从进程名推断版本或声明部署一致。 |

## 运行记录约定

每次续执行只追加日期、操作者、目标 revision/SHA、实际动作、Ready/健康结果、脱敏证据链接和失败/回退结果。未执行事项保持未完成；规划变更回到模块化交付规划文档，不在本清单复制操作方案。
