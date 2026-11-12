# SIT-K3S-V6 换机执行清单

2026-11-12（北京时间） · 本地配套清单 · 源 `172.237.9.58` → 目标 `5.189.172.69`

在目标新建 K3s 和空数据卷，完整部署 SIT 服务，以测试账号和新观测样本验收。执行范围包括已批准域名的 DNS 切换。旧 PostgreSQL、PVC、历史观测数据和旧 kubeconfig 不导入。旧机保留到切换观察完成，并继续承载尚未交接的服务。

逐步命令、放行条件和回退见 [Knowledge 正式手册与索引](https://github.com/ai-workspace-services/knowledge/tree/main/docs/reference/platform-delivery/clusters/sit-k3s-v6)（[PR #383](https://github.com/ai-workspace-services/knowledge/pull/383)）。本清单中的域名、IP 和 Vault 路径供内部执行使用，表中不含密钥值。

**当前状态（2026-11-12）**：目标为 Debian 13、4 vCPU、约 8 GiB 内存，系统盘约 100 GiB，无独立数据盘。已将 PROD 三条 OS 公钥记录复制到 SIT Vault 并回读一致。`vhosts/common` OS 身份与主机基线已执行，主机名为 `sit-k3s-v6`。K3s `v1.37.1+k3s1` 单节点已 Ready，API `/readyz` 通过，kubeconfig 为 `0600`。UFW 保留 SSH、HTTP、HTTPS，nftables 持久规则在 K3s 前置 hook 丢弃外部控制面流量。Flux、业务服务和 DNS 切换尚未执行。

**V6 现有 SSH 来源核对**：`kv/sit/platform/mcp` 的 `ssh_private_key_b64` 是 SIT MCP SSH sidecar 的既有私钥来源；其公钥指纹与目标机当前 root 授权公钥一致。GitOps 文档描述该密钥在旧环境供多个角色共用。`kv/sit/security/{root,operator,auditor}` 是当前 `vhosts/common` OS 身份 profile 的输入，已在 SIT Vault 建立并应用到目标机。用户确认由一人管理，三账户复用同一把 SSH key 是预期配置。账户仍分别使用独立 Unix 身份、组、sudo 和文件权限。持钥人均可登录三账户，权限验收按实际账户分别核对。

## 1. 仓库和引导参数

| 仓库 / 项目 | 固定基线和执行定位 |
| --- | --- |
| GitOps | [`fc9c199` SIT 根图](https://github.com/ai-workspace-infra/gitops/tree/fc9c199721d3f9b063735726f03e4b2cb1e5ccbf/environments/clusters/sit-k3s-v6)。`flux-system/config-sit` → `flux-system/sit-k3s` → `./environments/clusters/sit-k3s-v6`。八个子单元为 `cluster-identities-sit`、`postgresql-sit`、`observability-sit`、`vpa-sit`、`platform-mcp-sit`、`ingress-sit`、`external-dns-sit`、`web-saas-sit`，GitRepository 名为相应单元加 `-config`。根和子源当前声明 `main`，候选要固定全部 ref。 |
| 服务声明 | [`services/sit-k3s-v6`](https://github.com/ai-workspace-infra/gitops/tree/fc9c199721d3f9b063735726f03e4b2cb1e5ccbf/services/sit-k3s-v6)。`ingress-sit/{ingress,gateway-api}.yaml` 写有旧 IP。Traefik 配置 LoadBalancer 80/443，Caddy 声明 ClusterIP。现有 PostgreSQL 5 GiB 与观测 10 GiB 静态 PV 绑定旧节点和路径。候选准备新卷，重新渲染绑定。 |
| Playbooks | [`26394b8e` bootstrap 入口](https://github.com/ai-workspace-infra/playbooks/blob/26394b8ef6d034ac87ce6fbc595d63c387d1b9e5/scripts/pipeline/bootstrap-k3s.sh) → `k3s_platform_bootstrap.yml` → `inventory/terraform_cmdb.py`。`--limit` 仅选目标。受控输入包括 `MATRIX_HOST`、`CMDB_FILE`、`K3S_CMDB_SHA256`、`K3S_GITOPS_CHECKOUT`、`K3S_GITOPS_SHA`、`K3S_RESOURCE_MANIFEST`、`K3S_BOOTSTRAP_RECEIPT`。 |
| IaC | [`464fca6` IaC](https://github.com/ai-workspace-infra/iac_modules/tree/464fca63f4917b0a51370a7969a3b615f6a3bd41) 负责验证云资源及 CMDB/inventory，DNS 执行入口由域名 owner 选定。现有标准引导断言数值实例 ID、provider/region 与 `data_volume.linode_id` 等匹配。目标 IP 还没有本轮可用的经核实实例、卷或 SIT 资源清单，先补齐声明及执行契约。 |
| 运行构件 | `web-saas-fullstack` Chart digest `sha256:8f8db066583002eb8146b2103ab02cbbe1f2a5b786605d66542dc51ab60a010f`。观测 Chart digest `sha256:5773f62a8c0df0235891a2c778cffcd535e29534c254caaf72d573406dce60cf`。SIT MCP 独立 Deployment 的镜像 tag 为 `v0.4.0-sit`，执行前解析真实 digest。以上是主干声明，需与旧机实际运行状态和本轮候选对照。 |

## 2. 域名、后端与 DNS 动作

证据来自 2026-11-12 对 Cloudflare 权威 NS 与公共递归解析器的 A/AAAA/CNAME 查询。以下“已解析”表示 DNS 可见。四个共享入口的 HTTPS HEAD 通过当前网络超时，服务健康待用有效来源和业务路径复验。

| 域名 | 本次 DNS 观察 | 声明后端与切换决策 |
| --- | --- | --- |
| `mcp.svc.plus` | CNAME → `mcp-sit-k3s-v6.svc.plus` → A `172.237.9.58` | Traefik 指向 `platform-mcp-sit/infrastructure-mcp-server:8080`。核实规范域与直接目标的其他调用方，再按变更单选择更新目标 A 或切换 CNAME。直接目标有 A 记录，但候选仍需核实是否接收其 Host 和证书。 |
| `observability.svc.plus` | CNAME → `observability-sit-k3s-v6.svc.plus` → A `172.237.9.58` | Traefik 将指标/日志的匹配路径送观测鉴权服务，根路径送 Grafana。确认共享采集者、告警、数据源以及采用空历史的影响，由观测 owner 决定是否同轮接管。 |
| `ai.svc.plus`、`desktop.svc.plus` | 分别 A → `172.237.9.58` | GitOps 的 `topology/sit/selfhost/ai-aggregator.yaml` 指向 systemd Aggregator/CPA 与 Desktop，Playbooks 还有对应静态 DNS 引用。保留旧入口，若纳入切换则先独立部署并验收 AI 网关及 WebRTC 后更新 A。 |
| `console-sit.onwalk.net`、`app-sit.onwalk.net`、`console.sit.onwalk.net`、`app.sit.onwalk.net` | NXDOMAIN | Console 的主入口与别名。验收 `web-saas-console:80`、Accounts 的同源 API 路径及 Flagger，再按清单新增。 |
| `accounts-sit.onwalk.net`、`accounts.sit.onwalk.net` | NXDOMAIN | `web-saas-accounts:80` / TraefikService。启用时新增。 |
| `billing-sit.onwalk.net`、`billing.sit.onwalk.net` | NXDOMAIN | `web-saas-billing:80` / TraefikService。启用时新增，支付使用沙箱。 |
| `grafana-sit.onwalk.net`、`grafana.sit.onwalk.net` | NXDOMAIN | 当前入口引用 `observability-observability-stack:3000`，主干同时禁用观测 Chart 内嵌 Grafana，并有独立 `observability-grafana` HelmRelease。核实实际 Service 和 EndpointSlice，验收后新增。 |
| `mcp-sit.onwalk.net`、`mcp.sit.onwalk.net`、`mcp-sit.svc.plus` | NXDOMAIN | MCP 兼容入口，按启用清单新增。核对重复路由的实际接管者。 |
| `ai.sit.onwalk.net`、`desktop.sit.onwalk.net` | NXDOMAIN | 宿主机服务的兼容域名。随 AI/Desktop 单独决策。 |
| `console-selfhost-sit.onwalk.net`、`accounts-selfhost-sit.onwalk.net`、`billing-selfhost-sit.onwalk.net`、`postgresql-selfhost-sit.onwalk.net`、`agent-proxy-selfhost-sit.onwalk.net` | NXDOMAIN | selfhost 拓扑另有声明。核实调用方和实际用途再纳入，PostgreSQL 保持仅向获准的网络开放。 |
| `xconnect-referral-sit.onwalk.net`、`accounts-xconnect-referral-sit.onwalk.net`、`billing-xconnect-referral-sit.onwalk.net` | A → `172.237.5.48` | 现有特性泳道样例，属于不同地址。维护窗口前以 DNS 记录清单与各环境 inventory 枚举全部实际泳道。 |
| `vault.svc.plus` | CNAME → `vault-selfhost-prod-v6.svc.plus` → A `172.237.24.232` | 外部 Vault 依赖。目标验证连通、TLS 信任和新 JWT 身份。 |

两套格式的 SIT 域名都出现在配置中，`*.onwalk.net` 的证书不能单独覆盖 `console.sit.onwalk.net` 等两层别名。切换前逐域名检查 SAN、DNS 目标以及 Caddy/Traefik 的实际路由。ExternalDNS 的上层 `external-dns-sit` Kustomization 当前声明 `suspend: true`，下层 HelmRelease 值为 `enabled: true`。若旧集群已经存在 Deployment，暂停 Kustomization 不会停止它。实际写入者需要在 DNS 放行前确认。

## 3. Vault KV、Kubernetes Secret 与消费方

下表用逻辑 KV 路径 `kv/<记录>`。ACL/API 使用 `kv/data/<记录>`，ESO 以 `path: kv` 配 `remoteRef.key: <记录>`。路径和字段来源为固定主干或明确标注的历史文档，OS 公钥已回读核对，其他记录的状态按各行所述核实。

| 用途 | Vault KV / 字段 | K8s Secret → 消费方 | 证据与待办 |
| --- | --- | --- | --- |
| 共享入口 TLS | `kv/CICD/domains/svc.plus` · `tls_fullchain_pem_b64`、`tls_key_pem_b64` | `ingress-sit/shared-observability-tls` · `tls.crt` / `tls.key` → Traefik 的 MCP 和共享观测路由 | GitOps 直接 ESO 引用。 |
| SIT onwalk.net TLS | 历史候选 `kv/CICD/domains/onwalk.net` 或 `kv/sit/domains/onwalk.net` · `tls_fullchain_pem_b64`、`tls_key_pem_b64` | `external-secrets/sit-domains-onwalk-net` → Kubernetes provider → `ingress-sit/{console-tls,accounts-tls,billing-tls}` | 当前清单从 K8s 本地源读取。先确认哪个受控来源写入本地 Secret，别名逐个验 SAN。 |
| 共享观测鉴权 | `kv/CICD/observability` · `user`、`password` | `observability-sit/observability-ingest-auth` → vmauth 与观测 agent | GitOps 直接 ESO 引用。历史 `kv/sit/observability/ingest` 的 token 口径与当前字段不同。 |
| MCP Bearer / SSH | `kv/sit/platform/mcp` · `mcp_service_token`、`ssh_private_key_b64` | `platform-mcp-sit/platform-mcp` · `mcp-service-token` / `ssh-private-key` → gateway 与 SSH sidecar | GitOps 直接 ESO 引用。历史 `infra-mcp-auth` 属早期引导口径。政策另有 `kv/sit/platform/observability` 读取，当前 ESO 未引用该路径。 |
| PostgreSQL 三类身份 | 历史 `kv/sit/database/postgresql/{admin,operator,auditor}` · 各 `password` | `postgresql-sit/{postgresql-admin,postgresql-operator,postgresql-auditor}` → PostgreSQL；exporter 使用 auditor | 主干有 Secret 消费，SIT 根图未找到对应 ExternalSecret。核实所有者和新机注入路径，使用独立 SIT 角色。 |
| Accounts DB | 历史 `kv/sit/accounts-service` · `POSTGRES_PASSWORD`、`DATABASE_URL` | `web-saas-sit/accounts-db-runtime` → Accounts | 主干引用 Secret。目标按实际 app 契约注入并验证连接新库。 |
| Billing DB | 历史 `kv/sit/billing-service` · `DATABASE_URL` | `web-saas-sit/billing-db-runtime` → Billing | 主干引用 Secret。用 Billing 独立角色核实连接。 |
| Web SaaS 运行 | 历史 `kv/sit/web-saas/runtime` · `JWT_SECRET`、`SESSION_SECRET` | `web-saas-sit/web-saas-secrets` → Accounts / Billing / Content | 主干引用 Secret。按实际构件确认全部字段和跨服务一致性。 |
| Accounts 初始化 / 支付 | 当前 `web-saas-sit/secrets.yaml` 声明 K8s 对象，Vault 路径待 owner 核实 | `accounts-controller-config`、`accounts-bootstrap`、`accounts-stripe` → Accounts | 检查新机控制配置、初始账号和 Stripe 沙箱字段均由受控来源提供。 |
| Grafana 管理 | 历史 `kv/sit/observability/grafana` · `password` | `observability-sit/grafana-admin` → 独立 Grafana | 主干仅消费。检查 Grafana 数据源、面板及告警是否需要额外配置，历史面板数据不导入。 |
| vmagent 写入 | 主干引用 `observability-remote-write`，SIT 根图未找到对应生产者 | `observability-sit/observability-remote-write` · `password` → vmagent remote-write | 与共享 vmauth 的接收认证分别核实。基线配置跳过远端 TLS 校验，候选应补齐可信证书链并验证。 |
| Cloudflare | 历史 `kv/sit/platform/cloudflare` · `api_token`、`account_id`、`zone_id`。泳道角色有 `kv/sit/platform/cloudflare/feature-dns` ACL | `external-dns/external-dns-cloudflare` · `CF_API_TOKEN` → ExternalDNS | 特性泳道与集群 ExternalDNS 分开授权。候选保持 DNS 禁写，实际切换由确认的 DNS owner 执行。 |
| OS / K3s 身份 | OS 公钥 `kv/sit/security/{root,operator,auditor}` · `authorized_keys`。K3s 签发归档契约 `kv/<environment>/<cluster>/<role>` | OS 的 authorized keys 和独立的 K3s 身份配置 | 目标使用独立的 cluster 标识和限定路径的写入身份，保留旧集群归档。 |

三个直接引用 Vault 的 SecretStore 当前指向 `https://vault.svc.plus` 的 JWT mount `jwt-sit-k3s-sit-k3s-v6`。角色为 `sit-k3s-v6-observability-domain-tls-reader`、`sit-k3s-v6-observability-ingest-reader`、`sit-k3s-v6-platform-mcp-reader`，audience 为各角色名加 `vault-` 前缀。相应的 ServiceAccount 分别为 `ingress-sit/observability-domain-tls-reader`、`observability-sit/observability-ingest-reader`、`platform-mcp-sit/platform-mcp-reader`。双机阶段为新 cluster UID/JWKS 建立独立信任，在候选中引用新 mount/role 并做允许与拒绝验收。直接改旧 mount 的签名键会影响旧机 ESO 续用。

## 4. 按顺序执行

1. **SSH 只读预检。** 云控制面核对两机身份、SSH 指纹和目标空卷。源端收集 Flux revision、Ingress 和 ServiceLB、现有 DNS 写入者、共享服务和活跃泳道。目标 OS、容量和 root SSH 已初检，云控制面身份和正式管理网络仍待核实。
2. **候选声明。** 固定目标独立资源清单、CMDB、Playbooks 和 GitOps SHA。新增独立 Flux 根路径，按已审查的 ref 固定子源。基础阶段只启用身份和 ESO，后续依次放行 PostgreSQL/观测/VPA、应用/MCP、入口。候选 ExternalDNS 保持暂停。
3. **Playbooks 引导。** 由 `k3s_platform_bootstrap` 入口按顺序调度各 role：先调用 `vhosts/common` 完成主机名、OS 三类身份和所需基线，验证 SSH 登录及审计权限，取得 `COMMON_NODE_VERIFIED`；再执行 `vhosts/k3s-cluster-server`，随后按部署阶段执行 Helm、Flux controllers、Flux GitOps 交接和 K3s 身份 role。单独调用 K3s server role 时，它只校验主机名和 kubeconfig 权限，不能替代 common 初始化及验收。现有 `k3s_platform_bootstrap.yml` 在进入聚合 role 前调用 common，但其入口要求数值实例 ID 和 Linode 数据卷，且会继续 Flux 交接；目标当前条件不满足该入口，须先补齐并核实适用于目标的执行契约，不能伪造 CMDB 或跳过 common。此阶段授权仅覆盖 OS 和 K3s，Flux 及后续工作分阶段执行。

**逐项执行状态**

- [x] 目标 root SSH 可登录，目标 OS、容量和 K3s 缺失状态已核对。
- [x] 将 `kv/prod/security/{root,operator,auditor}` 的 `authorized_keys` 分别复制到对应 SIT 路径，并逐条回读确认一致。
- [x] 使用 SSH 实测地址和已固定主机密钥作为本次命令行 Ansible 目标，无需 Toolkit 或 GitHub Actions。
- [x] 通过 `vhosts/common` 完成主机名、OS 三类身份与基线。三类用户均实测 SSH 登录，auditor 的 shadow 读取、系统目录写入和 sudo 均被拒绝，operator 仅能执行批准的系统状态检查。
- [x] 由本次 platform 初始化入口先执行 common，再执行 `vhosts/k3s-cluster-server`。K3s 节点 Ready、API readiness 通过、管理 kubeconfig 为 `0600`。
- [x] 配置并验证主机防火墙。外部 2379、2380、6443、10250、10257、10259/TCP 和 8472/UDP 由 nftables 丢弃，SSH 保持可达，80/443 预留给后续服务入口。
- [ ] 后续独立执行 Flux/GitOps、服务验收和 DNS 切换。
4. **Flux 部署和验收。** 注册目标 Vault JWT 信任，准备本地来源 Secret 和业务 Secret。调谐后核对 Kustomization 与 HelmRelease、PV/PVC Bound、ESO 同步，验证空库初始化、Console/Accounts/Billing/Content、VPA/Flagger、MCP、Grafana/观测及实际需要的泳道。目标限定域名测试示例为 `curl --fail --show-error --resolve console-sit.onwalk.net:443:5.189.172.69 https://console-sit.onwalk.net/`，应用功能和证书须同时通过。
5. **DNS 交接和观察。** 导出 DNS 原记录，确定唯一写入者。对已存在的两条 CNAME 链及 AI/Desktop A 分别审查，对需要启用的 NXDOMAIN 域名新增。切后校验公共解析、TLS 和业务，观察至少覆盖旧 TTL 及一个任务周期。失败则恢复原记录/删除本轮新增记录并核对旧服务，值守记录新旧测试数据的独立边界。

仓库基线、公开 DNS、目标 SSH 和 SIT OS 公钥已核对。OS 三身份与 common 基线已验收，K3s 单节点已 Ready。Flux/GitOps、SIT 服务、DNS 写入者核对和 DNS 切换仍未执行或验收。
