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
| **`platform-ops-toolkit`** | [PR #1436](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/1436) | `a40b7a6a` | 派生 `.github/workflows/web-saas-k3s-orchestrator.yml`，解耦纯编排的 5 阶段串行流水线 |
