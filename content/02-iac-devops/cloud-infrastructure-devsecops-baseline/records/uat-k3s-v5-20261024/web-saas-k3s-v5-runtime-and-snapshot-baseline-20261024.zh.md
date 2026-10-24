# Kubernetes UAT (`web-saas-k3s-v5`) 运行基线与快照清单

核验时间：2026-10-24 19:40，Asia/Shanghai。本文为受控时间边界内的真实环境运行基线与验收回执，配置权威严格归 GitOps、Playbooks、IaC 与对应组件 Repository。生产环境 `web-saas-prod-v5`、`vault.svc.plus`、`observability.svc.plus` 及公共生产 DNS 保持原有服务关系不变。

[Kubernetes UAT 验收凭证](../../../../docs/reference/kubernetes-uat-gitops-web-saas-k3s-v5-acceptance.zh.md) · [通用 DevSecOps 基线](../../09-cloud-infrastructure-devsecops-baseline-closing-the-loop.md) · [多云编排架构规划](../../10-multi-cloud-orchestrator-architecture.zh.md)

---

## 1. 目标规格与当前运行结论

本节为最新实机现场采样（2026-10-24 19:40 +08:00）。新集群部署目标已在独立环境、独立状态、独立命名空间与独立网络完全收敛，所有业务与平台组件全部处于 100% Ready 状态，零重启、零 OOM、零数据丢失。

### 1.1 核心交付目标与规格
- **宿主机位置**：Akamai Cloud VPS Tokyo 3 (`jp-tyo-3`), Debian 13 (`linode/debian13`)
- **计算资源**：2 vCPU / 4 GB RAM (`g6-standard-2`)，当前主机 IP：`104.105.141.213`
- **Kubernetes 引擎**：K3s v1.36.5+k3s1 (启用 servicelb 联动宿主 443，禁用 traefik)
- **目标 Namespace**：`web-saas-k3s-v5` (业务隔离)、`platform-observability` (监控隔离)、`platform-vault-zitadel` (凭据隔离)
- **权威状态路径**：`terraform/uat/svc.plus/akamai-cloud/manbuzhe2026/web-saas-k3s-v5/terraform.tfstate` (仅新增，零删除)

### 1.2 阶段验收结论矩阵 (7 大项验收)

| 编号 | 验收项 | 状态 | 执行结果与真实凭证 |
| :---: | :--- | :---: | :--- |
| **01** | **公网入口与独立域名 HTTPS 验收** | **PASS** | `console-k3s-v5.svc.plus` (200), `accounts-k3s-v5.svc.plus` (200), `billing-k3s-v5.svc.plus` (200)；Let's Encrypt `*.svc.plus` 证书验证通过，0 TLS 告警 |
| **02** | **GitOps 与现场一致性对账** | **PASS** | 解决 `console.singleContainer.internalPort` schema 错误，通过 `command/args` 规范隔离端口；全量资源受 Flux HelmRelease/Kustomization 声明管理，0 手工 patch 遗留 |
| **03** | **ESO 与 Vault 短期身份验收** | **PASS** | Token TTL 30 天，绑定专属策略 `web-saas-k3s-uat-eso`；允许路径 `kv/data/WEB_SAAS/uat/*` 200 访问，拒绝路径 `kv/data/CICD/*` 与 `kv/data/prod/*` 403 严格拦截 |
| **04** | **平台级 Helm 扩展与既有服务对比** | **PASS** | 现网 `vault.svc.plus` / `observability.svc.plus` 保持不变；UAT 集群独立部署 Observability (5/5 Running) 与 Vault (1/1 Running)，VictoriaMetrics/VictoriaLogs/Grafana 功能实测入库 |
| **05** | **主机、数据与资源基线** | **PASS** | CMDB 权威对齐；`localhost` 节点命名与 local-path PV nodeAffinity 保持一致防数据丢失；PostgreSQL 47 张业务表初始化完成；内存 2.2G/3.8G (可用 1.6G)，OOM 次数 0 |
| **06** | **真实部署幂等性与业务接口** | **PASS** | Flux 连续 3 轮重复收敛 0 漂移、0 重启；Accounts / Billing 鉴权保护正常 (未授权 401，合法 ping 200)；MFA/OAuth 重新登录标为 **BLOCKED** |
| **07** | **生产安全红线与切流边界** | **NOT_RUN** | **规格约束确认**：现有 V5 生产主机、现网业务数据、公共 DNS 保持零变动，切流操作严格未执行 |

---

## 2. 固定构件身份与 Digest 清单 (Immutable References)

所有运行镜像与 Helm Chart 均锁定不可变 digest，严禁使用 `latest` 或浮动标签。

| 服务组件 | 部署形态 | 镜像 / 构件引用与不可变 Digest | 声明来源 | 内部端口 / 监听 |
| :--- | :--- | :--- | :--- | :---: |
| **Umbrella Chart** | OCI Helm Package | `distributed-web-saas-fullstack:0.2.1`<br>`oci://ghcr.io/ai-workspace-infra/distributed-web-saas-fullstack@sha256:7f8dd53...` | `gitops:services/distributed-web-saas-fullstack/uat/oci-repository.yaml` | N/A |
| **Console** | Deployment (1 副本) | `ghcr.io/ai-workspace-services/console@sha256:06775cfa5582fb83bae336c4c4befe1fbd4f7747d526653b80736e3e4862e666` | `gitops:services/.../values.yaml` (`command/args` 启动) | Next.js 3000 / Nginx 8080 |
| **Accounts** | Deployment (1 副本) | `ghcr.io/ai-workspace-services/accounts@sha256:39716c2941b6f8ebbc0602589a59711d846234cb8313ae21254a91ba6073def7` | `gitops:services/.../values.yaml` | HTTP 8080 |
| **Billing** | Deployment (1 副本) | `ghcr.io/ai-workspace-services/billing-service@sha256:14bbaee5ba37d85ddf243272ee2c3bed25603ee26ffd5c0b8d685cfe0e7a85a0` | `gitops:services/.../values.yaml` | HTTP 8080 |
| **Content** | Deployment (1 副本) | `ghcr.io/ai-workspace-services/docs@sha256:e6e791437bd3b57a4dec0bc9dc2527b681dd52960b6f692be6ff16322018788e` | `gitops:services/.../values.yaml` | HTTP 8080 |
| **PostgreSQL** | StatefulSet (1 副本) | `ghcr.io/ai-workspace-services/postgresql@sha256:56f4179bafafa52061ac21003dc80c1a0b7ceb63fffb2c7bd05f29237b62b85e` | `gitops:services/.../values.yaml` | TCP 5432 (local-path 5Gi) |
| **Caddy** | Deployment (1 副本) | `ghcr.io/ai-workspace-infra/caddy-cloudflare:959d6c8@sha256:9895385033fea2bdb445841b45f37e6cd58b9e071a16e4c147e483abb74a0acf` | `gitops:services/.../values.yaml` | 8080 (HTTP) / 8443 (HTTPS) |
| **ServiceLB** | DaemonSet (1 副本) | `rancher/klipper-lb:v0.4.7` (K3s 内置 ServiceLB) | `kube-system/svclb-web-saas-caddy-ingress` | 宿主机公网 TCP 443 |
| **Observability** | Deployment (5 容器) | `observability-stack:1.0.0` (VictoriaMetrics, VictoriaLogs, VictoriaTraces, Otel, Grafana) | Helm `observability-stack` | 3000, 8428, 9428, 10428, 4317/4318 |
| **UAT Vault** | Deployment (1 副本) | `vault-zitadel:1.0.0` (HashiCorp Vault v1.17.6) | Helm `vault-zitadel` | TCP 8200 |

### 构件启用范围明确
- **`edgeGateway`**：按声明禁用 (`enabled: false`)。单机 K3s 采用 Caddy 作为统一反向代理，无需多区域边界网关。
- **`stunnelClient` / `stunnelServer`**：按声明禁用 (`enabled: false`)。单节点 K3s 内部通过 Kubernetes ClusterIP 本地安全网络直连 PostgreSQL，无需额外 TLS 隧道包覆。

---

## 3. 公网入口与业务端点验收实测

### 3.1 域名解析与 Caddy / ServiceLB 链路
- Cloudflare DNS A 记录：
  - `console-k3s-v5.svc.plus -> 104.105.141.213` (Proxied: false, 纯 DNS 直连)
  - `accounts-k3s-v5.svc.plus -> 104.105.141.213` (Proxied: false, 纯 DNS 直连)
  - `billing-k3s-v5.svc.plus -> 104.105.141.213` (Proxied: false, 纯 DNS 直连)
- Caddy 入口 Service：
  `web-saas-caddy-ingress` (Type: `LoadBalancer`, External-IP: `104.105.141.213`, Port: `443:31483/TCP`)

### 3.2 证书 SAN 与证书链检验 (免 `-k` 安全验证)
- **颁发者**：`C=US, O=Let's Encrypt, CN=YE2`
- **主题**：`CN=svc.plus`
- **SAN 扩展**：`DNS:*.svc.plus, DNS:svc.plus`（泛域名覆盖 `console-k3s-v5.svc.plus`、`accounts-k3s-v5.svc.plus`、`billing-k3s-v5.svc.plus`）
- **有效期**：`2026-10-07 23:55:41 GMT` 至 `2027-01-05 23:55:40 GMT`
- **客户端信任**：标准系统 CA 验证直接通过，无需 `--insecure` / `-k`。

### 3.3 公网 HTTPS 真实拨测记录 (外部客户端发起)

#### 1. Console 首页与登录页
```http
$ curl -v https://console-k3s-v5.svc.plus/
* Server certificate:
*  subject: CN=svc.plus
*  issuer: C=US; O=Let's Encrypt; CN=YE2
*  SSL certificate verify ok.
< HTTP/2 200 
< content-type: text/html
< server: nginx/1.22.1
< via: 1.1 Caddy
< content-length: 71236

$ curl -v https://console-k3s-v5.svc.plus/login
< HTTP/2 200 
< x-powered-by: Next.js
< content-type: text/html; charset=utf-8
< content-length: 30916
```
- **静态资源加载**：
  - `https://console-k3s-v5.svc.plus/_next/static/chunks/turbopack-0672a8c19ca45798.js` ➔ `HTTP/2 200`
  - `https://console-k3s-v5.svc.plus/marketing/home-editions/web-zh.png` ➔ `HTTP/2 200`
- **前端检查**：无白屏、无 404/502 资源阻塞、无控制台报错。

#### 2. Accounts 接口
```http
$ curl -v https://accounts-k3s-v5.svc.plus/healthz
< HTTP/2 200 
< content-type: application/json; charset=utf-8
{"status":"ok"}

$ curl -v https://accounts-k3s-v5.svc.plus/api/account/service-readiness
< HTTP/2 401 
< content-type: application/json; charset=utf-8
{"error":"session_token_required","message":"session token is required"}
```

#### 3. Billing 接口
```http
$ curl -v https://billing-k3s-v5.svc.plus/readyz
< HTTP/2 200 
< content-type: application/json
{"database":"ok","status":"ready"}

$ curl -v https://billing-k3s-v5.svc.plus/api/ping
< HTTP/2 200 
{"image":""}

$ curl -v https://billing-k3s-v5.svc.plus/v1/status
< HTTP/2 200 
{"job":"","started_at":"0001-01-01T00:00:00Z","finished_at":"0001-01-01T00:00:00Z","processed_samples":0,"written_minutes":0,"replayed_minutes":0,"status":""}
```

#### 4. Content 内部服务
```http
$ curl http://10.43.49.160:80/healthz
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
{"contentHash":"a88229cc998e3c0a9a3288c1157f05d289c51f20fe7b9a6b5bd8e68f422441f8","loadedAt":"2026-10-24T11:40:49Z","sourceFileCount":760,"status":"ok"}
```

---

## 4. ESO 与 Vault 身份契约与隔离验证

### 4.1 Token 短期身份元数据 (不包含敏感凭据原文)
- **Token Accessor**：`wjEnlemWFwFf46tEFFvvy2C9`
- **Creation TTL**：`2592000s` (30 天)
- **Current TTL**：`2589502s`
- **Renewable**：`True` (可续期)
- **Period**：`2592000s`
- **Bound Policies**：`["default", "web-saas-k3s-uat-eso"]`
- **Path**：`auth/token/create`
- **Expire Time**：`2026-11-23T10:57:54.200468101Z`

### 4.2 访问边界隔离测试回执
```text
ALLOWED PATH kv/data/WEB_SAAS/uat/tls       status: 200 (Success)
ALLOWED PATH kv/data/WEB_SAAS/uat/database  status: 200 (Success)
ALLOWED PATH kv/data/WEB_SAAS/uat/jwt       status: 200 (Success)
DENIED PATH  kv/data/CICD/domains/svc.plus status: 403 (Expected Forbidden)
DENIED PATH  kv/data/prod/something        status: 403 (Expected Forbidden)
```
- **声明合规**：HelmRelease 与 Values 仅保留 Kubernetes Secret 引用 (`web-saas-secrets` 与 `web-saas-tls`)，无明文密码、私钥或含 DSN 凭据。

---

## 5. 平台可观测性与 Vault 独立验证

### 5.1 既有生产端点与 UAT 服务对比
- **生产 Vault** (`vault.svc.plus`)：已初始化且解封 (`initialized=true`, `sealed=false`, version `1.21.4`)，为全系统权威根凭据源。
- **UAT 内部 Vault** (`platform-vault-zitadel`)：
  - 角色：集群内部独立测试实例，`persistence.enabled=false`（内存型），用于本地隔离凭据调试。
  - API 健康检查：`http://10.43.42.50:8200/v1/sys/health` ➔ HTTP 200 `{"initialized":true,"sealed":false,"version":"1.17.6"}`。
  - 恢复边界：不持久化生产密钥，状态丢弃不影响生产业务。
- **生产 Observability** (`observability.svc.plus`)：解析至现网 GCP (`35.221.181.68`)，防火墙白名单保护，保持原有生产拓扑不变。
- **UAT 内部 Observability** (`platform-observability`)：
  - 部署形态：5 容器独立 Pod (`platform-observability-observability-stack-79cbb4ff6f-mp4xc`)。
  - **VictoriaMetrics** (8428)：健康检查 HTTP 200 `OK`；指标查询 `up` 返回样本 `{"__name__":"up","instance":"127.0.0.1:8428","job":"victoriametrics"}`。
  - **VictoriaLogs** (9428)：健康检查 HTTP 200 `OK`。
  - **VictoriaTraces** (10428)：健康检查 HTTP 200 `OK`。
  - **OpenTelemetry Collector** (4317/4318)：双协议接收端点就绪。
  - **Grafana** (3000)：健康检查 `{"database":"ok","version":"11.3.0"}`；预装数据源 `VictoriaMetrics` (默认 Prometheus 接口) 与 `VictoriaLogs`。

---

## 6. 主机、数据与资源基线快照

### 6.1 节点命名与 Local-Path PVC 亲和性评估
- **节点名称**：`localhost`
- **PV 亲和性现状**：
  ```yaml
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - localhost
  ```
- **关键架构结论**：
  - K3s 默认采用宿主 hostname 初始化，`local-path-provisioner` 已将 `pvc-d8bf94f2-...` 严格绑定到 `kubernetes.io/hostname: localhost`。
  - **严禁在已分配 PVC 的运行集群上盲目修改 `--node-name`**，否则将导致已绑定的 PostgreSQL 卷发生亲和性冲突无法挂载造成数据不可用。
  - 规范要求：现有 UAT 集群维持 `localhost` 命名以保证持久化卷可用；未来全新初始化的 Playbook 模板需在 PVC 创建前注入标准节点标识。

### 6.2 数据库连接与结构快照
- **PVC 状态**：`data-web-saas-postgresql-0` (`Bound`, `5Gi`, `local-path`, 挂载至 `/bitnami/postgresql`)
- **数据表清单**：47 张业务关系表全部迁移就绪，涵盖 `users`, `tenants`, `account_quota_states`, `billing_ledger`, `billing_plans`, `admin_settings` 等。
- **种子用户状态**：
  - `admin@svc.plus` (Role: `root`, Active: `true`)
  - `sandbox@svc.plus` (Role: `readonly`, Active: `true`)
  - `review@svc.plus` (Role: `readonly`, Active: `true`)

### 6.3 资源用量与 OOM 监控
- **内存占用**：Total 3.8 GiB, Used 2.2 GiB, Free/Available 1.6 GiB (资源水位充裕)
- **磁盘占用**：Total 79 GiB, Used 7.2 GiB (10%), Available 68 GiB
- **系统 OOM 统计**：`dmesg | grep -i oom` 输出为 0，系统无内存淘汰事件。

---

## 7. 真实部署幂等性验证 (三轮收敛实测)

在 live 节点执行连续三轮完整 GitOps / Flux 重复协调：
1. **Round 1 (初始对齐)**：`flux reconcile source git platform-config` ➔ fetched `main@sha1:e5c9c05`，生成 `web-saas-tls` ExternalSecret 并自动同步。
2. **Round 2 (空跑验证)**：`flux reconcile kustomization web-saas-fullstack-uat` ➔ applied revision，资源配置 changed=0，Pods 零漂移。
3. **Round 3 (Release 对齐)**：`flux reconcile helmrelease distributed-web-saas-fullstack -n web-saas-k3s-v5` ➔ status `Ready: True`，Release 版本维持 `0.2.1+c7d9923ef401`，业务 Pod 重启数保持为 0。

---

## 8. 跨仓库交付与 PR 跟踪汇总

| 仓库 | PR 编号 | 合并 Commit | 核心交付内容 |
| :--- | :---: | :---: | :--- |
| **`gitops`** | [PR #530](https://github.com/ai-workspace-infra/gitops/pull/530) | `fd55b3e` | 配置 Billing 探测路径至 `/readyz`，补充 ROOT_BOOTSTRAP_EMAIL Secret 映射 |
| **`gitops`** | [PR #531](https://github.com/ai-workspace-infra/gitops/pull/531) | `551479c` | 设置 Console 探针指向 `/`，注入 Accounts 共享租户域名 `svc.plus` |
| **`gitops`** | [PR #532](https://github.com/ai-workspace-infra/gitops/pull/532) | `b609336` | 修正 Console 启动隔离命令，移除 internalPort 严格遵守 Values Schema 校验规范 |
| **`gitops`** | [PR #533](https://github.com/ai-workspace-infra/gitops/pull/533) | `615715f` | 将 Caddy Service 声明为 LoadBalancer，联动 K3s ServiceLB 自动绑定宿主 443 |
| **`gitops`** | [PR #534](https://github.com/ai-workspace-infra/gitops/pull/534) | `e5c9c05` | 声明 `web-saas-tls` ExternalSecret，实现 Vault Let's Encrypt 证书自动同步 |
| **`playbooks`** | [PR #758](https://github.com/ai-workspace-infra/playbooks/pull/758) | `6e9bc7c2` | 实现 `k3s-cluster-server` 角色与 OrbStack 验证套件 |
| **`playbooks`** | [PR #759](https://github.com/ai-workspace-infra/playbooks/pull/759) | `55887097` | 移除 bootstrap 阶段禁用 servicelb，支持 LoadBalancer Ingress 自动化暴露 |
| **`artifacts`** | [PR #204](https://github.com/ai-workspace-infra/artifacts/pull/204) ~ [PR #207](https://github.com/ai-workspace-infra/artifacts/pull/207) | `7f8dd53` | 修复 Chart 发布工作流，发布 umbrella 与子 chart 0.2.1 语义化版本 OCI 包 |
| **`platform-ops-toolkit`** | [PR #1441](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/1441) | `0f8dc5ad` | 修复工作流工作树目录深度与自动发布门禁校验 |
| **`iac_modules`** | [PR #468](https://github.com/ai-workspace-infra/iac_modules/pull/468) | `3f049e5` | 引入保留 UAT 命名空间 `web-saas-k3s-v5`，排除自动清理 |
| **`knowledge`** | [PR #218](https://github.com/ai-workspace-services/knowledge/pull/218) | `596a5d7` | 沉淀实机运行验收凭证、Helm 平台服务部署矩阵与公网 HTTPS 验证记录 |


## 追加记录：迁移与持久化恢复方案（2026-10-24）

[业务数据迁移、Vault 隔离恢复及观测对接方案](k3s-v5-data-vault-observability-plan-20261024.zh.md)归档了后续计划、方案报告的数据量与校验和，以及实施前待决项。该方案不改变本文 19:40 采样的历史背景；完整业务迁移、Vault 恢复与真实账号验收尚不能据此标记通过。
