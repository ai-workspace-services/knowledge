# SIT-K3S-V6 换机重部署与 DNS 切换手册

本手册用于同代换机。新主机以独立 K3s 集群和空数据卷部署 SIT，使用测试账号和新观测样本验收。旧 PostgreSQL、监控历史及本地卷不导入。先验证目标服务，再交接域名。共享服务如果由旧机承载，按服务所有者批准的清单逐项切换。

本文给出执行步骤与停止条件。执行单保存实例身份、地址、SSH 主机指纹、DNS 记录、Vault 引用、固定版本、值班人和运行回执。相关历史配置见[模块化交付与特性泳道规划](SIT-K3S-V6-模块化交付与特性泳道规划.md)。

## 1. 固定执行输入

| 项目 | 执行单必填 |
| --- | --- |
| 源、目标和卷 | 从云控制面核实两端账号、区域、实例 ID、地址和 SSH host key。为目标绑定独立节点名和空卷，记录设备、文件系统标识和挂载点。旧主机仍提供回退入口。 |
| GitOps | 固定可拉取的提交 SHA、候选路径、`flux-system`、源 `config-sit` 和根 `sit-k3s`。当前 SIT 基线根为 `environments/clusters/sit-k3s-v6`，模块位于 `services/sit-k3s-v6`。目标候选应有独立声明入口，候选提交不得被旧集群的跟踪路径消费。 |
| Playbooks 与构件 | 固定 Playbooks SHA、K3s/Flux/Helm/ESO 版本、OCI Chart digest 和实际镜像 digest。解析所有子 GitRepository 的目标 ref。 |
| 身份 | 准备主机管理 SSH 密钥、短期运行 Vault 身份和独立 Kubernetes 身份签发凭据。为目标集群准备独立的工作负载 JWT 信任，保留旧集群的有效身份。 |
| DNS | 对每个域名记录区、记录类型、当前值、候选值、TTL、代理状态、写入者、证书及回退值。记录 CNAME 的直接目标和最终 A/AAAA。对共用 CNAME 目标先盘点其他调用方。 |

GitOps 声明集群组合、资源引用和期望状态。IaC 生成实例及卷的 CMDB/inventory，并执行经审查的 DNS 变更。Playbooks 执行主机引导、身份与 Vault 配置，Flux 调谐 Kubernetes 资源。[GitOps](https://github.com/ai-workspace-infra/gitops) · [Playbooks](https://github.com/ai-workspace-infra/playbooks) · [IaC Modules](https://github.com/ai-workspace-infra/iac_modules)

## 2. SSH 和目标预检

先在执行控制机准备经云控制面核实的 `known_hosts` 与专用 SSH agent。以下变量来自受控执行单。新机的首轮检查以系统管理身份执行。

```bash
: "${SIT_TARGET_IP:?}" "${SIT_KNOWN_HOSTS:?}" "${SIT_ADMIN:?}"
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes \
  -o UserKnownHostsFile="$SIT_KNOWN_HOSTS" "$SIT_ADMIN@$SIT_TARGET_IP" \
  'hostname; uname -m; sed -n "/^PRETTY_NAME=/p" /etc/os-release;
   nproc; free -m; lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINTS;
   df -hT; ip -br addr; ss -lnt'
```

核对返回地址与 CMDB、空卷与容量、80/443 是否占用、目标到 GitHub/GHCR/Vault 的访问以及管理面防火墙。控制面只向获准管理网络开放。发现目标已有 K3s、业务进程、未知文件系统或卷挂载与 CMDB 不一致时停止引导。源端用独立审计身份读取节点、Flux 状态、ServiceLB、对外入口、命名空间和控制器状态，保留切换与回退基线。

## 3. 准备候选 GitOps 图

在 GitOps PR 中加入目标的资源声明和独立 Flux 路径。候选的根与所有子源须解析到审查过的 SHA。Playbooks 的 `declarative_active` 引导将根源固定为 `spec.ref.commit`，保留根源的 `kustomize.toolkit.fluxcd.io/ssa: IfNotPresent` 注解。子源由 GitOps 声明固定。若子源与根要使用同一提交，可在候选中声明本轮唯一 tag，提交审查后创建该 tag，并验证所有来源解析结果。每次变更使用新的固定版本。

| 阶段 | GitOps 模块及依赖 |
| --- | --- |
| 基础 | 根创建命名空间，`cluster-identities-sit` 提供 RBAC。SIT 基线根只有 ESO 命名空间，没有 ESO 控制器发行单元。为目标加入 SIT 专用 ESO 模块，先调谐 CRD、控制器及 webhook，再放行使用 SecretStore / ExternalSecret 的模块。 |
| 卷和平台服务 | 为 PostgreSQL 与观测栈声明目标 PV/PVC 和挂载路径，校验节点亲和性与 UID/GID。初始化空库、独立业务角色和观测数据目录。先启用 VPA，再启用依赖它的 `platform-mcp-sit`。 |
| 应用 | `web-saas-sit` 在 PostgreSQL 就绪、业务连接 Secret 和数据库初始化就绪后启动。检查 Console、Accounts、Billing、Content、Flagger 与三组 Canary。未明确纳入的旧 PR 泳道按执行单关闭或按固定构件重建。 |
| 入口 | 当前配置同时声明 Caddy 和 Traefik。Playbooks 的 K3s 默认禁用内置 Traefik 和 ServiceLB。若使用 K3s ServiceLB 暴露 Flux 部署的 Traefik，声明 `k3s_platform_disable_components` 只保留 `traefik`，并核对实际 80/443 归属。若由独立负载均衡器提供入口，明确其 Service 绑定及健康检查。按实际路由验证 Host、TLS、跨命名空间后端与 Flagger 权重。候选入口地址由已验证的运行输入提供。 |
| DNS | `external-dns-sit` 在基线根图中暂停，而下游 HelmRelease 声明启用。目标在切换前保留暂停状态，独立核对目标无可写 Cloudflare 凭据和无运行中的遗留控制器。 |

首次引导的候选只放行根、身份和基础依赖，保留其他单元的分阶段放行条件。每阶段从干净的固定 checkout 渲染根和对应模块，保存资源清单与版本。审查启动顺序、默认启用的调度任务、Webhook、远程写入、邮件与支付沙箱。若目标的 Vault JWT 签名键尚未注册，先准备目标集群，采集 cluster UID 与签名键指纹，再由 Vault owner 建立并验证独立信任。原集群 JWT mount 的签名键不得随目标部署替换。

本地执行入口与资源路径的检查示例：

```bash
test "$(git -C "$K3S_GITOPS_CHECKOUT" rev-parse HEAD)" = "$K3S_GITOPS_SHA"
test -z "$(git -C "$K3S_GITOPS_CHECKOUT" status --porcelain --untracked-files=all)"
kubectl kustomize "$K3S_GITOPS_CHECKOUT/$SIT_ROOT_PATH"
for module in postgresql-sit observability-sit platform-mcp-sit ingress-sit web-saas-sit; do
  kubectl kustomize "$K3S_GITOPS_CHECKOUT/services/sit-k3s-v6/$module" >/dev/null || exit 1
done
```

## 4. Playbooks 引导与 Flux 接管

`scripts/pipeline/bootstrap-k3s.sh` 是已核对的 IaC/CMDB 引导入口。它校验 GitOps checkout、CMDB 摘要、目标和回执路径，运行 `k3s_platform_bootstrap.yml` 并严格限制 `--limit`。主干入口要求数值型实例 ID、匹配 provider/region、卷附着和文件系统标签，当前卷契约包含 `data_volume.linode_id`。执行前确认目标 provider、卷和库存是否满足此契约。若不匹配，在所属仓库补齐目标的资源/CMDB 与 Playbooks 输入支持并通过检查，禁止伪造字段来通过断言。

资源声明中的 `hosts[].host_vars` 至少核对这四组输入：

| 组别 | 关键字段 |
| --- | --- |
| 主机 | `deployment_mode: kubernetes`，`k3s_platform_node_name` 等于 CMDB 节点名，节点 K3s 版本和 kubeconfig 权限 `0600`。 |
| 数据 | `hosts[].volume` 的 label 和 filesystem label 对应空卷。配置实际存储路径和挂载要求，并验证 `k3s_platform_local_storage_path` 落在该挂载。 |
| Flux | `k3s_platform_flux_bootstrap_mode: declarative_active`，Git URL、认证模式、source/root 名称、根路径、命名空间和 `k3s_platform_acceptance_objects`。 |
| 身份 | `k3s_identity_environment: sit`、独立 `k3s_identity_cluster`、目标 `k3s_identity_api_server`、`k3s_identity_tls_dir`、三个身份的 `k3s_identity_checks` 和 `k3s_identity_rbac_kustomizations`。 |

```bash
: "${SIT_PLAYBOOKS_CHECKOUT:?}" "${MATRIX_HOST:?}" "${CMDB_FILE:?}" "${SIT_KNOWN_HOSTS:?}"
: "${K3S_GITOPS_CHECKOUT:?}" "${K3S_GITOPS_SHA:?}" "${K3S_RESOURCE_MANIFEST:?}"
: "${K3S_CMDB_SHA256:?}" "${K3S_BOOTSTRAP_RECEIPT:?}"
export MATRIX_HOST CMDB_FILE K3S_GITOPS_CHECKOUT K3S_GITOPS_SHA
export K3S_RESOURCE_MANIFEST K3S_CMDB_SHA256 K3S_BOOTSTRAP_RECEIPT
export AI_WORKSPACE_CMDB_JSON="$CMDB_FILE"
export ANSIBLE_HOST_KEY_CHECKING=True
export ANSIBLE_SSH_COMMON_ARGS="-o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=$SIT_KNOWN_HOSTS"
cd "$SIT_PLAYBOOKS_CHECKOUT" || exit 1
ansible-playbook -i inventory/terraform_cmdb.py k3s_platform_bootstrap.yml \
  --limit "$MATRIX_HOST" --list-hosts
# 核对只选中目标、文件均为绝对路径、目标卷为空、回执路径未使用，再执行。
bash scripts/pipeline/bootstrap-k3s.sh
```

执行机需满足 Playbooks 控制端依赖，运行时按现有 Vault 登录流程注入系统和 Kubernetes 身份所需的不同凭据。`K3S_RESOURCE_MANIFEST` 是 GitOps checkout 内的资源声明相对路径，`SIT_ROOT_PATH` 是声明中指向 Flux 根目录的相对路径。先核对 Playbooks 固定 SHA 和 CMDB 生成回执。成功后应有 `COMMON_NODE_VERIFIED`、`FLUX_HANDOVER_VERIFIED`、`K3S_IDENTITIES_VERIFIED`，并绑定本次 SHA 和目标。`k3s_platform_bootstrap_with_gitops.yml` 只调用协调角色，已有主机和卷前置条件由调用方交付。[Playbooks 引导契约](https://github.com/ai-workspace-infra/playbooks/tree/main/roles/vhosts/k3s_platform_bootstrap)

在目标管理 SSH 会话确认节点与 cluster UID，再以目标私有 kubeconfig 调谐根。候选变更先由 Playbooks 的 `vhosts/flux_gitops` 按审查后的 checkout 交接固定根源，`reconcile` 只刷新当前引用。

```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
k3s kubectl get ns kube-system -o jsonpath='{.metadata.uid}{"\n"}'
flux reconcile kustomization sit-k3s -n flux-system --with-source --timeout=10m
flux get sources git -n flux-system
flux get kustomizations -n flux-system
flux get helmreleases -A
k3s kubectl get nodes,pvc -A -o wide
k3s kubectl get externalsecrets -A
```

根与每个启用模块的 revision 对应执行单，HelmRelease 就绪，PV/PVC Bound，ESO 同步成功后再放行依赖单元。根 Ready 只证明根已对账。遇到 `ArtifactFailed`、CRD 缺失、Helm 渲染异常或 Secret 未同步时，从相应 owner 修正声明，换固定候选后重跑。证据记录 revision、对象 condition 和事件类别，凭据及配置原值留在其受控存储。

## 5. 凭据交付与业务验收

按受控执行单为每条引用登记 **Vault KV 路径及字段 → JWT 身份或受控注入方式 → Kubernetes Secret → 消费方**。旧的规划路径和当前实际 SecretStore 有差异，以下按消费契约核对。

| 用途 | 目标交付与通过条件 |
| --- | --- |
| PostgreSQL | 管理员、操作员、审计和业务身份分别准备。先初始化空库与受审查的 schema，业务连接使用新库和独立最小 DML，管理连接不进入业务容器。审计使用真实身份验证授权读与写入拒绝。 |
| Console / Accounts / Billing / Content | 配齐应用引用的运行 Secret、独立 DB 连接、Accounts 控制配置与沙箱支付。确认 Accounts/Billing 连接目标数据库，Console 登录和会话成功，Billing 沙箱场景产生预期记录，Content 路径返回正常内容。 |
| 域名证书 | SIT 证书的 ESO 声明使用 Kubernetes provider，需要先准备本地源 Secret；共享入口证书使用 Vault provider。核对两层各自 Secret 来源、实际使用的证书、SAN、完整链和续期归属。 |
| Grafana / Victoria / DataKit | 确认 Grafana 登录和数据源，查到目标产生的新指标与日志。检查实际入口指向的是可用 Grafana Service。共享采集端的认证及 remote-write 凭据分别验收，按预期只投递一次。 |
| MCP | Vault provider 投影工作负载所需 Secret。若对应域名列入切换，验证 MCP `initialize`、`tools/list`、适用后端查询与授权拒绝，核对实际运行构件与路由。 |
| Flagger | 验证三组 Canary 的主路由和指标有数据，至少演练一次 SIT 候选加权、成功推广或受控回退。确认实际 Traefik 路由经过对应 TraefikService，记录流量权重和错误率。 |

对公有入口逐条执行目标预检。`SIT_HOST`、`SIT_HEALTH_PATH` 取自执行单，不能只检查根路径或只看 200。

```bash
curl --fail --silent --show-error --max-time 15 \
  --resolve "$SIT_HOST:443:$SIT_TARGET_IP" "https://$SIT_HOST$SIT_HEALTH_PATH"
```

验证每个主域名和兼容别名的证书 SAN。单层泛域名证书不能覆盖多层别名。外部 OAuth、Webhook 和异地采集通过已获准的隔离入口验收，因为本地指定解析不会改变第三方的 DNS 结果。

## 6. DNS 切换、观察与回退

1. **冻结清单**。从权威 NS 和公共递归 DNS 获取 A/AAAA/CNAME。对照供应商记录的 ID、TTL、代理状态和 TXT 所有权。确认哪些是已有入口，哪些需要新增，哪些别名共用同一目标。已被其他环境使用的泳道和共享域名由各自 owner 判定，不能从名称推断归属。
2. **锁定写入者**。检查两端 ExternalDNS 的 Kustomization、HelmRelease 和实际 Deployment，另查 IaC/自动化是否会写相同记录。切换期间由审批过的 IaC DNS 入口写入，暂停或排除会回写本次记录的自动化。旧记录回执和旧入口可用性先归档。
3. **执行最小变更**。已存在 CNAME 的入口按批准方案更新其独立目标或 CNAME；同时使用该目标的其他域名须一并通过验收。缺失的 SIT 域名按新增写入。先发布测试域名并验收，再按变更单切其余入口。旧、新 SIT 使用独立空库，避免同一入口在缓存期写两端。按流量特性收敛旧写请求，并提前约定空环境的测试账号与会话重登方式。
4. **切换后验收**。对比权威和公共 DNS，在两个独立网络检查 HTTPS 证书、Console 登录、API、MCP 或 Grafana 等所选功能，验证观测数据新鲜度、外部回调与错误率。观察至少覆盖已记录的旧 TTL 和一个相关任务周期。共享监控入口切换前需确认其调用方是否接受新的空历史边界及告警连续性。
5. **回退**。DNS 指向错误、证书校验失败、核心业务失败或观测持续缺失时，暂停推进，恢复记录原值、TTL、代理状态和写入归属。若原本缺失则撤销本轮新增记录。验证旧路由和运行状态。切换后在新环境产生的测试记录留在新环境，值守记录该数据边界。保留旧主机直到观察结束且共享依赖逐项完成交接。

本轮记录既可能包含 SIT 新增，也可能包含共享 CNAME 和 A 更新。先选定接受相应环境和记录类型的 DNS 执行入口。现有 `cloudflare-dns-record.py` 只接受 UAT/PROD 已有 A，`dns-reconcile.py` 只接受 UAT 单条 A。若 IaC 尚无匹配入口，由区所有者在 Cloudflare 按同一变更单逐条执行并记录 record ID，或者先补齐 IaC 契约。Terraform 已管理的记录通过所属 state 的 plan/apply 交付。每一条更新按记录 ID 检查前值，避免覆盖窗口内的并发变更。[Cloudflare A 记录执行器](https://github.com/ai-workspace-infra/iac_modules/blob/main/scripts/pipeline/cloudflare-dns-record.md) · [DNS 调谐契约](https://github.com/ai-workspace-infra/iac_modules/blob/main/scripts/pipeline/dns-reconcile.md)

建议的记录查询格式：

```bash
for type in A AAAA CNAME; do
  dig @"$SIT_AUTHORITATIVE_NS" "$SIT_HOST" "$type" +noall +comments +answer
  dig @"$SIT_PUBLIC_RESOLVER" "$SIT_HOST" "$type" +noall +comments +answer
done
```

执行回执附上目标实例和 cluster UID、GitOps/Playbooks SHA、引导回执、Flux revisions、启用模块的运行状态、DNS 变更 ID、功能验收及观察窗口。所有结果按 `PASS`、`FAIL`、`BLOCKED` 或 `NOT_RUN` 记录。本手册随文档发布，目标部署和 DNS 切换的实际结果另行登记。
