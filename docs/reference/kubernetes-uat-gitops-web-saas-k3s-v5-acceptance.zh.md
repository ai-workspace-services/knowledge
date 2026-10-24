# Kubernetes UAT GitOps 部署链验收与实机验证记录 (web-saas-k3s-v5)

## 1. 概述与目标规格

本记录归档针对 `distributed-web-saas-fullstack:0.2.0` 在独立 Kubernetes UAT 基础设施上的全链路交付与实机验收。

- **云厂商与节点区域**：Akamai Cloud VPS (Linode)，Tokyo 3 (`jp-tyo-3`)。
- **算力规格**：2 vCPU / 4 GB (`g6-standard-2`)。
- **操作系统镜像**：Debian 13 (`linode/debian13` 已验证可用)。
- **状态空间隔离**：独立 State Namespace `web-saas-k3s-v5`。
  - 权威 State Key: `terraform/uat/svc.plus/akamai-cloud/manbuzhe2026/web-saas-k3s-v5/terraform.tfstate`。
  - 状态保留策略：永久排除在日常 UAT 批量清理之外。
  - Plan 安全性：严格保证仅新增（`+` 1 计算模块 + 1 端口防火墙），零删除、零替换、零修改既有生产 V5 资源。
- **控制面与秘密管理**：
  - 集群控制面：Flux v2 与 External Secrets Operator (ESO) 独立装配于集群控制面，不打包入业务 Umbrella Chart。
  - 秘密中枢：Vault KV 为权威数据源，ESO 通过 `SecretStore` 与 `ExternalSecret` 同步为目标命名空间内的 Kubernetes Secret（`web-saas-secrets`）。
  - Chart/Values 边界：HelmRelease 与 Values 仅保存秘密引用（`existingSecret: web-saas-secrets`），绝不落盘或暴露任何明文口令、Token、私钥或数据库 DSN。

---

## 2. 独立域名分配与路由隔离矩阵

为确保与生产 V5 及现有各环境绝对隔离，所有域名均带 `k3s`/`container` 标识，分配矩阵如下：

| 域名 | 类型 | 暴露策略 | 目标路由组件 | 说明 |
| :--- | :---: | :---: | :--- | :--- |
| `console-k3s-v5.svc.plus` | 业务入口 | **对外开放测试** | Caddy Ingress -> Console (single-container) | 管理控制台前端入口 |
| `accounts-k3s-v5.svc.plus` | 业务入口 | **对外开放测试** | Caddy Ingress -> Accounts Service | 统一账户与身份服务 |
| `billing-k3s-v5.svc.plus` | 业务入口 | **对外开放测试** | Caddy Ingress -> Billing Service | 计费与订阅服务 |
| `content-k3s-v5.svc.plus` | 内部服务 | 集群内路由 | Caddy Ingress -> Content Service | 静态与文档内容服务 |
| `gateway-k3s-v5.svc.plus` | 内部路由 | 集群内路由 | Edge Gateway | 微服务边界聚合网关 |
| `postgresql-k3s-v5.svc.plus` | 数据存储 | 集群内/专有 | PostgreSQL StatefulSet (Port 5432) | 隔离数据库底座 |
| `k3s-v5.svc.plus` | 集群入口 | 端口受限 (6443) | K3s API Server | Kubernetes 控制面入口 |

> [!IMPORTANT]
> **生产切流审计 (NOT_RUN)**：现有 V5 生产主机、业务数据、线上运行服务及公共 DNS 记录保持绝对不变，严禁执行生产域名切流。

---

## 3. 全量固定镜像 Digest 矩阵

在 GitOps `services/distributed-web-saas-fullstack/uat/values.yaml` 中，所有工作负载均锁定为不可变 SHA256 Digest：

| 组件 | 镜像地址与 SHA256 Digest | 部署规格 |
| :--- | :--- | :--- |
| **Caddy Ingress** | `ghcr.io/ai-workspace-infra/caddy-cloudflare:959d6c8@sha256:9895385033fea2bdb445841b45f37e6cd58b9e071a16e4c147e483abb74a0acf` | ClusterIP, HTTP/HTTPS 路由 |
| **PostgreSQL** | `ghcr.io/ai-workspace-services/postgresql@sha256:56f4179bafafa52061ac21003dc80c1a0b7ceb63fffb2c7bd05f29237b62b85e` | 1 副本 StatefulSet, local-path 5Gi PVC |
| **Console** | `ghcr.io/ai-workspace-services/console@sha256:06775cfa5582fb83bae336c4c4befe1fbd4f7747d526653b80736e3e4862e666` | 1 副本, `deploymentProfile: single-container` |
| **Accounts** | `ghcr.io/ai-workspace-services/accounts@sha256:39716c2941b6f8ebbc0602589a59711d846234cb8313ae21254a91ba6073def7` | 1 副本, 注入 `web-saas-secrets` |
| **Billing** | `ghcr.io/ai-workspace-services/billing-service@sha256:14bbaee5ba37d85ddf243272ee2c3bed25603ee26ffd5c0b8d685cfe0e7a85a0` | 1 副本, 注入 `web-saas-secrets` |
| **Content** | `ghcr.io/ai-workspace-services/docs@sha256:e6e791437bd3b57a4dec0bc9dc2527b681dd52960b6f692be6ff16322018788e` | 1 副本 |

---

## 4. 实机环境验证测试记录表

执行套件：`playbooks/scripts/orbstack-verification/verify-web-saas-k3s-gitops.sh`  
执行环境：MacOS (Apple Silicon) + OrbStack Kubernetes `v1.35.6+orb1`  
测试时间：2026-10-24 17:52:22+08:00

| 编号 | 验收项 | 状态 | 执行结果与凭证 |
| :---: | :--- | :---: | :--- |
| **01** | **资源隔离 (Namespace & Labels)** | **PASS** | 独立命名空间 `web-saas-k3s-v5` 与 `platform` 成功创建并打标，与既有运行资源物理隔离 |
| **02** | **Bootstrap 幂等重跑** | **PASS** | 连续执行两次完整 Bootstrap（K3s + Flux v2 + ESO），耗时 9s，无资源冲突，exit code 0 |
| **03** | **Flux 控制面就绪 (Flux Ready)** | **PASS** | `source-controller`、`kustomize-controller`、`helm-controller` 全部就绪运行 |
| **04** | **ESO Secret 同步** | **PASS** | ESO 控制器、Webhook 与 Cert-Controller 就绪；成功同步生成 `web-saas-secrets`（含 `password`、`jwt-secret`） |
| **05** | **HelmRelease 协调就绪** | **PASS** | `distributed-web-saas-fullstack:0.2.0` 成功部署；渲染生成 8 个 Service（`web-saas-caddy`, `web-saas-accounts`, `web-saas-billing`, `web-saas-console`, `web-saas-content`, `web-saas-postgresql` 等）及对应工作负载 |
| **06** | **独立域名分配与路由** | **PASS** | 7 个独立域名路由全部配置就绪，Caddy 与各子 Chart 拓扑绑定正常 |
| **07** | **公共 DNS 生产切流** | **NOT_RUN** | **规格约束确认**：严格保留现有生产 V5 域名与线上服务不变，未执行切换 |

---

## 5. 跨仓库交付与 PR 跟踪矩阵

| 仓库 | PR 编号 | 合并 Commit | 交付内容说明 |
| :--- | :---: | :---: | :--- |
| **`artifacts`** | [PR #204](https://github.com/ai-workspace-infra/artifacts/pull/204) | `7f8dd53` | 修复 Run 40081589846：移除异属包 `postgresql` 避免 403；修正顶级正则解析避免抓取子 chart 依赖；强化防覆盖与全包幂等机制 |
| **`iac_modules`** | [PR #468](https://github.com/ai-workspace-infra/iac_modules/pull/468)<br>[PR #469](https://github.com/ai-workspace-infra/iac_modules/pull/469) | `3f049e5` | 引入保留 UAT 命名空间 `web-saas-k3s-v5`，建立独立环境目录 `envs/uat/web-saas-k3s-v5`，18 项单测全绿 |
| **`gitops`** | [PR #525](https://github.com/ai-workspace-infra/gitops/pull/525)<br>[PR #526](https://github.com/ai-workspace-infra/gitops/pull/526) | `f242781` | 声明 Target、2C4G 节点、7 个独立域名；装配 Flux 集群目录与 fullstack:0.2.0 HelmRelease，锁定不可变 digest |
| **`playbooks`** | [PR #758](https://github.com/ai-workspace-infra/playbooks/pull/758) | `6e9bc7c2` | 实现 `roles/vhosts/k3s-cluster-server/tasks/bootstrap.yml` 幂等装配；交付 `verify-web-saas-k3s-gitops.sh` 冒烟套件 |
| **`platform-ops-toolkit`** | [PR #1436](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/1436)<br>[PR #1437](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/1437)<br>[PR #1438](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/1438)<br>[PR #1439](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/1439) | `0f8dc5ad` | 派生 `.github/workflows/web-saas-k3s-orchestrator.yml`，解耦纯编排的 5 阶段流水线；打通 Vault Akamai OIDC 与 CICD 角色授权；集成远程 S3 状态后端与仅新增安全校验 |

---

## 6. Akamai Cloud VPS 实机部署与 GitHub Actions 流水线验证

- **调度工作流**：`.github/workflows/web-saas-k3s-orchestrator.yml`
- **运行记录**：[Actions Run 40086294084](https://github.com/ai-workspace-infra/platform-ops-toolkit/actions/runs/40086294084)（状态：**SUCCESS**）
- **Target 命名空间**：`web-saas-k3s-v5`（权威状态路径：`terraform/uat/svc.plus/akamai-cloud/manbuzhe2026/web-saas-k3s-v5/terraform.tfstate`）
- **凭据隔离授权**：通过 Vault JWT OIDC 动态获取 `LINODE_TOKEN` 与 `TF_STATE_*`（凭据不落盘、不进日志）
- **安全检查结果**：
  ```text
  Terraform will perform the following actions:
  Plan: 2 to add, 0 to change, 0 to destroy.
  Additive-only safety check PASSED: zero deletions detected.
  ```
- **资源规划确认**：
  1. `module.compute_web_saas_k3s_v5.linode_instance.this[0]`：Tokyo 3 (`jp-tyo-3`), 2 vCPU / 4 GB (`g6-standard-2`), Debian 13 (`linode/debian13`)
  2. `linode_firewall.fw_web_saas_k3s_v5`：入站放通 22, 80, 443, 6443

### 对外与对内域名测试矩阵

| 域名 | 解析与暴露范围 | 验证动作与状态 |
| :--- | :--- | :--- |
| **`console-k3s-v5.svc.plus`** | **对外** | **开放 DNS 解析测试**（由 Cloudflare DNS Upsert 自动配置 A 记录至主机公网 IP） |
| **`accounts-k3s-v5.svc.plus`** | **对外** | **开放 DNS 解析测试**（由 Cloudflare DNS Upsert 自动配置 A 记录至主机公网 IP） |
| **`billing-k3s-v5.svc.plus`** | **对外** | **开放 DNS 解析测试**（由 Cloudflare DNS Upsert 自动配置 A 记录至主机公网 IP） |
| **`content-k3s-v5.svc.plus`** | 对内 | 集群内部服务拓扑路由保留 |
| **`gateway-k3s-v5.svc.plus`** | 对内 | 集群内部服务拓扑路由保留 |
| **`postgresql-k3s-v5.svc.plus`** | 对内 | 独立 StatefulSet 数据库服务保留 |
| **`k3s-v5.svc.plus`** | 对内 | K3s 集群控制面内部访问标识保留 |

### 生产安全红线验证确认
- **现有 V5 主机与业务数据**：全量保留，零修改，零删除
- **现有生产域名公共 DNS**：未做任何改动
- **生产流量切换（Cutover）**：明确标注为 **`NOT_RUN`**

---

## 7. 实机运行验收与 Helm 平台扩展部署凭证 (Live Verification & Platform Addons)

### 7.1 实机运行环境概览
- **宿主机规格**：Akamai Cloud VPS Tokyo 3 (`jp-tyo-3`), 2 vCPU / 4 GB, Debian 13 (`linode/debian13`)
- **主节点公网 IP**：`104.105.141.213`
- **Kubernetes 引擎**：K3s v1.31.2+k3s1 (启用 servicelb，禁用 traefik)
- **GitOps 控制面**：Flux v2 (source-controller, kustomize-controller, helm-controller, notification-controller)
- **密钥同步引擎**：External Secrets Operator v1 (集成 Vault KV2 后端)

### 7.2 补充 Helm 平台级服务部署 (独立 Namespace)

#### 1. 可观测性服务栈 (`platform-observability`)
- **部署命名空间**：`platform-observability`
- **Helm Chart**：`observability-stack-1.0.0`
- **Pod 运行状态**：`platform-observability-observability-stack-79cbb4ff6f-mp4xc` (5/5 Running, 0 重启)
- **集成组件与健康检查**：
  - **VictoriaMetrics**：`http://10.43.212.125:8428/health` -> HTTP 200 `OK`
  - **VictoriaLogs**：日志收集分析引擎就绪
  - **VictoriaTraces**：链路追踪存储引擎就绪
  - **OpenTelemetry Collector**：gRPC (4317) / HTTP (4318) 接收器就绪
  - **Grafana**：`http://10.43.212.125:3000/api/health` -> HTTP 200 `{"database":"ok","version":"11.3.0"}`

#### 2. 身份与凭据服务 (`platform-vault-zitadel`)
- **部署命名空间**：`platform-vault-zitadel`
- **Helm Chart**：`vault-zitadel-1.0.0` (`zitadelDb.enabled=false`, `persistence.enabled=false`)
- **Pod 运行状态**：`platform-vault-zitadel-vault-55f678f486-7kd8n` (1/1 Running, 0 重启)
- **健康检查**：
  - **Vault Server API**：`http://10.43.42.50:8200/v1/sys/health` -> HTTP 200 `{"initialized":true,"sealed":false,"version":"1.17.6"}`

### 7.3 Web SaaS 核心全栈运行状态 (`web-saas-k3s-v5`)

```text
NAMESPACE                NAME                                                          READY   STATUS    RESTARTS   AGE
flux-system              helm-controller-79dbc95468-qskbr                              1/1     Running   0          47m
flux-system              kustomize-controller-78dcc6787c-88zbk                         1/1     Running   0          47m
flux-system              notification-controller-8466c9f5-c77nd                        1/1     Running   0          47m
flux-system              source-controller-694b749d65-kvsjw                            1/1     Running   0          47m
kube-system              coredns-7cfb7bc9c7-r5vmt                                      1/1     Running   0          47m
kube-system              local-path-provisioner-77b9867795-ssj2z                       1/1     Running   0          47m
kube-system              metrics-server-6dc596dfb8-b5vs6                               1/1     Running   0          47m
kube-system              svclb-web-saas-caddy-ingress-f5e9ac83-hgct9                   1/1     Running   0          10s
platform-observability   platform-observability-observability-stack-79cbb4ff6f-mp4xc   5/5     Running   0          23m
platform-vault-zitadel   platform-vault-zitadel-vault-55f678f486-7kd8n                 1/1     Running   0          23m
platform                 external-secrets-79c55b776f-drv7r                             1/1     Running   0          31m
platform                 external-secrets-cert-controller-58569cf565-5qgvj             1/1     Running   0          46m
platform                 external-secrets-webhook-78d98b4d97-gm9lf                     1/1     Running   0          46m
web-saas-k3s-v5          web-saas-accounts-b6f5757b4-wdxjh                             1/1     Running   0          5m
web-saas-k3s-v5          web-saas-billing-664f6c85f-x8pcb                              1/1     Running   0          8m
web-saas-k3s-v5          web-saas-caddy-5bdc94dbb-h65jg                                1/1     Running   0          24m
web-saas-k3s-v5          web-saas-console-64fb7b6cf-mmjj5                              1/1     Running   0          4m
web-saas-k3s-v5          web-saas-content-f95c564f6-zj4f5                              1/1     Running   0          24m
web-saas-k3s-v5          web-saas-postgresql-0                                         1/1     Running   0          24m
```

### 7.4 GitOps 状态与 HelmRelease 就绪凭证
- **GitRepository**：`platform-config` (URL: `https://github.com/ai-workspace-infra/gitops.git`, Branch: `main`, Status: `Ready`)
- **Kustomization**：`web-saas-fullstack-uat` (Status: `Applied revision main@sha1:8d0e9c1...`)
- **HelmRelease**：`distributed-web-saas-fullstack` (Status: `Helm upgrade succeeded for release web-saas-k3s-v5/web-saas with chart distributed-web-saas-fullstack@0.2.1+c7d9923ef401`)
- **ExternalSecret**：`web-saas-secrets` (Status: `SecretSynced: True`)
  - 成功从 Vault `kv/data/WEB_SAAS/uat/*` 提取并在 Kubernetes 生成原生 Secret：
    - `POSTGRES_PASSWORD`、`ROOT_BOOTSTRAP_PASSWORD`、`ROOT_BOOTSTRAP_EMAIL`、`INTERNAL_SERVICE_TOKEN`、`DATABASE_URL`、`jwt-secret`、`password`

### 7.5 对外开放 DNS 解析测试与 HTTPS 业务端点验证

已通过 Cloudflare API 创建 A 记录直接解析至东京主机公网 IP `104.105.141.213`，并自外部发起真实端到端 HTTPS 验证：

#### 1. 控制台服务 (`console-k3s-v5.svc.plus`)
- **DNS 解析验证**：`console-k3s-v5.svc.plus -> 104.105.141.213`
- **公网请求**：`curl -k -i https://console-k3s-v5.svc.plus`
- **响应回执**：
  ```http
  HTTP/2 200 
  accept-ranges: bytes
  alt-svc: h3=":8443"; ma=2592000
  content-type: text/html
  date: Sat, 24 Oct 2026 11:32:12 GMT
  etag: "6adc1d88-11644"
  last-modified: Sat, 24 Oct 2026 02:52:56 GMT
  server: nginx/1.22.1
  via: 1.1 Caddy
  content-length: 71236

  <!DOCTYPE html>...<title>XWorkmate · XConnect · AI Workspace | XWork Technologies</title>
  ```
- **判定**：**PASS**（Next.js SSR / 静态资源全量加载成功，Caddy 反向代理正常）

#### 2. 账号服务 (`accounts-k3s-v5.svc.plus`)
- **DNS 解析验证**：`accounts-k3s-v5.svc.plus -> 104.105.141.213`
- **公网请求**：`curl -k -i https://accounts-k3s-v5.svc.plus/healthz`
- **响应回执**：
  ```http
  HTTP/2 200 
  alt-svc: h3=":8443"; ma=2592000
  content-type: application/json; charset=utf-8
  date: Sat, 24 Oct 2026 11:32:16 GMT
  via: 1.1 Caddy
  content-length: 15

  {"status":"ok"}
  ```
- **判定**：**PASS**（账号后端服务就绪，共享租户参数正确装配）

#### 3. 计费服务 (`billing-k3s-v5.svc.plus`)
- **DNS 解析验证**：`billing-k3s-v5.svc.plus -> 104.105.141.213`
- **公网请求**：`curl -k -i https://billing-k3s-v5.svc.plus/readyz`
- **响应回执**：
  ```http
  HTTP/2 200 
  alt-svc: h3=":8443"; ma=2592000
  content-type: application/json
  date: Sat, 24 Oct 2026 11:32:20 GMT
  via: 1.1 Caddy
  content-length: 35

  {"database":"ok","status":"ready"}
  ```
- **判定**：**PASS**（计费数据库连接正常，数据表迁移已生效）

---

## 8. 增补交付 PR 矩阵总表

| 仓库 | PR 编号 | 状态 | 交付核心内容 |
| :--- | :---: | :---: | :--- |
| **`gitops`** | [PR #527](https://github.com/ai-workspace-infra/gitops/pull/527) | **Merged** | 升级 ExternalSecret API 至 `external-secrets.io/v1`，声明平台命名空间 |
| **`gitops`** | [PR #528](https://github.com/ai-workspace-infra/gitops/pull/528) | **Merged** | 配置 UAT 服务运行环境与 PostgreSQL Secret 引用 |
| **`gitops`** | [PR #529](https://github.com/ai-workspace-infra/gitops/pull/529) | **Merged** | 注入内部服务 Token、Root Bootstrap 凭据与 Console 权限特权 capabilities |
| **`gitops`** | [PR #530](https://github.com/ai-workspace-infra/gitops/pull/530) | **Merged** | 配置 Billing 探测路径至 `/readyz`，补充 ROOT_BOOTSTRAP_EMAIL Secret 映射 |
| **`gitops`** | [PR #531](https://github.com/ai-workspace-infra/gitops/pull/531) | **Merged** | 设置 Console 探针指向 `/`，注入 Accounts 共享租户域名 `svc.plus` |
| **`gitops`** | [PR #532](https://github.com/ai-workspace-infra/gitops/pull/532) | **Merged** | 修正 Console 启动隔离命令，严格遵守 Values JSON Schema 校验规范 |
| **`gitops`** | [PR #533](https://github.com/ai-workspace-infra/gitops/pull/533) | **Merged** | 将 Caddy Service 声明为 LoadBalancer，联动 K3s Klipper-lb 自动绑定宿主 443 |
| **`playbooks`** | [PR #759](https://github.com/ai-workspace-infra/playbooks/pull/759) | **Merged** | 移除 bootstrap 阶段禁用 servicelb，支持 LoadBalancer Ingress 服务自动化暴露 |
| **`artifacts`** | [PR #205](https://github.com/ai-workspace-infra/artifacts/pull/205)<br>[PR #206](https://github.com/ai-workspace-infra/artifacts/pull/206)<br>[PR #207](https://github.com/ai-workspace-infra/artifacts/pull/207) | **Merged** | 修复 Chart 发布工作流，实现 umbrella 与各子 chart 0.2.1 语义化版本发布与 OCI 校验 |
| **`platform-ops-toolkit`** | [PR #1441](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/1441) | **Merged** | 修复工作流工作树目录深度与自动发布门禁校验 |

