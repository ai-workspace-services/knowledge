---
title: 10 大核心服务类别 macOS OrbStack 单机部署与健康验收矩阵
description: 《图解平台工程 · 云中立实践》全书 10 大核心服务类别在 macOS 本机 OrbStack 容器环境下的单机极简拓扑、独立端口分配、Compose 工程编组、健康检查探针与端到端验收快照规范。
slug: platform-core-services-orbstack-acceptance-matrix
lang: zh
date: 2026-10-24
version: "1.0-release"
status: approved
tags:
  - platform-engineering
  - orbstack
  - macos
  - cloud-neutral
  - docker-compose
  - gitea
  - harbor
  - silo
  - cmdb
  - vault
  - zitadel
  - doco-cd
  - k3s
  - pgvector
  - postgresql
  - ai-gateway
  - mcp-server
category: reference
---

# 10 大核心服务类别 macOS OrbStack 单机部署与健康验收矩阵

**版本：1.0-release · 状态：已批准归档 · 适用域：平台工程实战 / macOS 本机演练 / OrbStack 单机验证**

本文档详细记录与归档《图解平台工程 · 云中立实践》全书涉及的 **10 大核心服务类别** 在 macOS 本机基于 **OrbStack** 容器与虚拟机运行时环境的单机极简部署拓扑、非冲突端口矩阵、健康检查收敛指标以及端到端验证实录。该架构确保开发者与运维团队可在不依赖公有云资源的单台 Apple Silicon Mac 工作站上，一键拉起并验收完整的云中立平台工程软件基座。

---

## 一、架构目标与验证范围

在真实的多云平台工程演进中，开发团队经常需要在本地开发机快速复现与验证各模块功能。为避免各服务与宿主机现有工作区服务（如 `workspace-bridge` :8787、`workspace-postgresql` :15432/:15433、`macos-dev-doco-cd` :19080 等）发生端口冲突，设计了一套**专用独立本地回环端口矩阵**，并在 OrbStack 中以独立 Docker Compose 工程方式编组，与 OrbStack GUI 容器视图保持完全一致。

### 覆盖的 10 大核心服务类别

1. **Git 与 CI/CD 引擎**：Gitea 代码托管与轻量级 Actions 运行引擎 (`gitea/gitea:1.22.6`, 端口 13000 / 13022)。
2. **云原生企业级制品仓库**：Harbor 制品管理中枢（镜像、OCI Chart、Cosign 签名验签与 Trivy 漏洞扫描，官方版本 v2.15.4 / Helm chart 1.19.4，端口 18080 / 8080 / 443）。
3. **S3 兼容对象存储**：老冯维护的 `pgsty/silo`（S3-Compatible Object Storage，替代停止维护的 MinIO，支持远端状态与大文件对象存储，端口 19000 / 19001）。
4. **配置管理与 CMDB 动态清单**：Ansible-Core 动态清单驱动与轻量级 CMDB SQLite API 服务 (`python:3.11-alpine`, 端口 18000)。
5. **密钥中枢与统一身份认证**：HashiCorp Vault 密钥引擎 + Zitadel 统一身份认证后端 PostgreSQL 实例 (`hashicorp/vault:1.17.6` + `postgres:16-alpine`, 端口 18200 / 15434)。
6. **声明式 GitOps 持续交付**：Doco CD 控制器，支持本地 Git 仓库轮询与配置收敛 (`ghcr.io/kimdre/doco-cd:0.1.28`, 端口 19088 / 19128)。
7. **云中立容器与向量底座**：轻量级容器运行底座配套 PostgreSQL 16 + `pgvector` 扩展 (`pgvector/pgvector:pg16`, 端口 15435)。
8. **数据库灾备还原演练**：PostgreSQL 演练源库与基于隔离沙箱的快照备份/还原校验 (`postgres:16-alpine`, 端口 15436)。
9. **AI 模型接入与路由网关**：New API 用户与配额认证管理中心 + LiteLLM 统一模型分发路由代理 (`calciumion/new-api:v0.4.10` + `ghcr.io/berriai/litellm:v1.51.0`, 端口 13001 / 14000)。
10. **AI 基础设施 MCP 工具网关**：Infrastructure MCP Server 基础设施管理工具协议守护网关 (`alpine:3.20` + 原生 Linux arm64 Go 二进制, 端口 18888)。

---

## 二、OrbStack 部署与验收矩阵

以下矩阵归纳了 10 大核心服务在 macOS OrbStack 上的工程编组、镜像版本锁定、本地端口映射及真实探测响应。所有容器经健康检查收敛后状态均为 **100% healthy** 🟢。

| 序号 | 核心服务分类 | Compose 工程名 (`-p`) | 容器名称 | 镜像锁定与哈希 | 本地回环端口 | 关键健康探针与测试命令 | 验证状态 |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **01** | Git 与 CI/CD 引擎 | `platform-gitea` | `platform-gitea-server` | `gitea/gitea:1.22.6` | `127.0.0.1:13000` (Web/API)<br>`127.0.0.1:13022` (SSH) | `curl -fsS http://127.0.0.1:13000/api/v1/version`<br>返回 `{"version":"1.22.6"}` | **healthy** 🟢 |
| **02** | 云原生制品仓库 | `platform-harbor` | `platform-harbor-portal`<br>(VM 拓扑: 10 容器集群) | `goharbor/harbor-portal:v2.15.4`<br>(集群: `goharbor/*:v2.15.4`) | `127.0.0.1:18080` (Web Portal)<br>`192.168.139.64:8080` (API/Proxy)<br>`https://harbor.example.com` (TLS) | `curl -fsS http://127.0.0.1:18080/` (HTTP 200)<br>`curl -fsS http://127.0.0.1:8080/api/v2.0/ping` (`Pong`)<br>Trivy 自动漏洞扫描、Cosign 签名校验 (412 拦截) | **healthy** 🟢 |
| **03** | S3 兼容对象存储 | `platform-silo` | `platform-silo-storage` | `pgsty/silo:RELEASE.2026-10-18T00-00-00Z` | `127.0.0.1:19000` (S3 API)<br>`127.0.0.1:19001` (Console) | `curl -fsS http://127.0.0.1:19000/minio/health/live`<br>返回 `HTTP 200 OK` | **healthy** 🟢 |
| **04** | 配置管理与 CMDB | `platform-cmdb` | `platform-cmdb-api` | `python:3.11-alpine` (CMDB Daemon) | `127.0.0.1:18000` (REST API) | `curl -fsS http://127.0.0.1:18000/api/v1/inventory`<br>动态输出 `_meta.hostvars` 与节点组 | **healthy** 🟢 |
| **05** | 密钥中枢与统一身份 | `platform-vault-zitadel` | `platform-vault-server`<br>`platform-zitadel-db` | `hashicorp/vault:1.17.6`<br>`postgres:16-alpine` | `127.0.0.1:18200` (Vault API)<br>`127.0.0.1:15434` (PG) | `curl -fsS http://127.0.0.1:18200/v1/sys/health` (Unsealed)<br>`docker exec platform-zitadel-db pg_isready` | **healthy** 🟢<br>**healthy** 🟢 |
| **06** | 声明式 GitOps 交付 | `platform-doco-cd` | `platform-doco-cd-controller` | `ghcr.io/kimdre/doco-cd:0.1.28` | `127.0.0.1:19088` (HTTP)<br>`127.0.0.1:19128` (Metrics) | `curl -fsS http://127.0.0.1:19088/v1/health` -> `{"content":"healthy"}`<br>`curl -fsS http://127.0.0.1:19128/metrics` | **healthy** 🟢 |
| **07** | 容器与向量底座 | `platform-k3s-pgvector` | `platform-k3s-pgvector` | `pgvector/pgvector:pg16` | `127.0.0.1:15435` (Postgres) | `docker exec platform-k3s-pgvector psql -c "SELECT extname FROM pg_extension;"` -> 存在 `vector` | **healthy** 🟢 |
| **08** | 数据库灾备还原演练 | `platform-pg-backup` | `platform-pg-backup-source` | `postgres:16-alpine` | `127.0.0.1:15436` (PG Test DB) | `docker exec platform-pg-backup-source pg_isready -d test_backup_db` | **healthy** 🟢 |
| **09** | AI 模型接入与路由网关 | `platform-ai-gateway` | `platform-ai-new-api`<br>`platform-ai-litellm` | `calciumion/new-api:v0.4.10`<br>`ghcr.io/berriai/litellm:v1.51.0` | `127.0.0.1:13001` (New API)<br>`127.0.0.1:14000` (LiteLLM) | `curl -fsS http://127.0.0.1:13001/api/status` -> `200 OK`<br>`curl -fsS http://127.0.0.1:14000/health/liveliness` -> `"I'm alive!"` | **healthy** 🟢<br>**healthy** 🟢 |
| **10** | 基础设施 MCP 网关 | `platform-mcp-server` | `platform-mcp-gateway` | `alpine:3.20` + native Go | `127.0.0.1:18888` (Gateway) | `curl -fsS http://127.0.0.1:18888` -> `{"status":"ok","service":"infrastructure-mcp-server"}` | **healthy** 🟢 |

---

## 三、网络与端口分配设计规范

为了在单机环境下无缝并存多套系统，测试验证套件严格遵循以下端口划分规则：

```text
Host Network (127.0.0.1) Loopback Port Layout:
┌─────────────────┬─────────────────────────────┬────────────────────────────────┐
│ Port Range      │ Service Category            │ Protocol / Endpoint Description│
├─────────────────┼─────────────────────────────┼────────────────────────────────┤
│ 13000 / 13022   │ 01 Gitea Engine             │ HTTP Web UI & SSH Git Push     │
│ 18080           │ 02 Harbor Portal            │ HTTP Web Dashboard & Portal    │
│ 19000 / 19001   │ 03 Silo S3 Object Storage   │ S3 API & Console Dashboard     │
│ 18000           │ 04 CMDB & Inventory API     │ FastAPI Dynamic Inventory API  │
│ 18200 / 15434   │ 05 Identity - Vault & Zitadel│ Vault HTTP API & Zitadel PG    │
│ 19088 / 19128   │ 06 GitOps - Doco CD         │ HTTP Health & Metrics Exporter │
│ 15435           │ 07 K3s Base - pgvector      │ PostgreSQL 16 Vector DB        │
│ 15436           │ 08 Backup - Source DB       │ Isolated Sandbox PG Instance   │
│ 13001 / 14000   │ 09 AI Gateway (New API/Lite)│ Admin REST API & LiteLLM Proxy │
│ 18888           │ 10 Infrastructure MCP Server│ JSON-RPC / HTTP MCP Gateway    │
└─────────────────┴─────────────────────────────┴────────────────────────────────┘
```

---

## 四、各服务 Compose 配置与健康探针实现要点

### 1. 类别 01：Gitea + Actions 引擎 (`platform-gitea`)
- **定位**：代码托管、代码审查、版本发布与轻量自托管 CI/CD。
- **镜像**：`gitea/gitea:1.22.6`。
- **探针机制**：通过 Docker 原生 `curl -fsS http://localhost:3000/api/v1/version` 进行就绪探针，当版本 JSON 返回后收敛为 `healthy`。

### 2. 类别 02：云原生制品仓库 Harbor (`platform-harbor`)
- **定位**：企业级 OCI 容器镜像与 Helm Chart 制品管理中心，提供 Trivy 自动漏洞扫描与 Cosign 内容签名防篡改门禁。
- **版本锁定**：Harbor v2.15.4（离线安装包 md5 校验通过），Helm Chart 1.19.4。
- **双模态验证实录**：
  1. **单机模式（Standalone）**：
     - 在 OrbStack Ubuntu 虚拟机（13 vCPU / 12 GB RAM / 414 GB SSD）部署 10 容器完整集群：`harbor-core`、`harbor-portal`、`registry`、`registryctl`、`harbor-db`、`redis`、`trivy-adapter`、`harbor-jobservice`、`harbor-caddy`、`nginx`。
     - **Web UI & API**：`admin` 成功登录（HTTP 200）。创建项目 `test-library`（开启自动扫描）与 CI 机器人账号 `robot$ci-robot`（HTTP 201）。
     - **Docker Push 与 Trivy 扫描**：推送 `harbor.example.com/test-library/smoke-app:v1.0.0`，Trivy v0.75.0 触发实时扫描，出具安全报告（`scan_status: Success`）。
     - **OCI Chart**：推送 `oci://harbor.example.com/test-library/testchart:0.1.0` 成功。
     - **Cosign 签名与策略门禁**：生成签名密钥对，执行 `cosign sign` 并验签成功；开启「只允许已签名制品」（`enable_content_trust_cosign: true`）策略后，拉取未签名镜像被强阻断并返回 `412 Precondition Failed`。
     - **复制规则与持久化还原**：配置 `replicate-test-library` 复制规则；执行 `--uninstall` 成功保留 `/data/harbor` 卷与数据，重新执行安装脚本后历史项目、镜像、密钥与规则完整恢复。
  2. **K8s 模式（Helm Chart）**：
     - 在 OrbStack Kubernetes v1.35.6 集群部署 `goharbor/harbor 1.19.4`。
     - 5 个 PVC（`harbor-jobservice`、`harbor-registry`、`harbor-redis`、`harbor-database`、`harbor-trivy`）状态全部 `Bound`。
     - 7 个 Pod（`harbor-core`、`harbor-database-0`、`harbor-jobservice`、`harbor-portal`、`harbor-redis-0`、`harbor-registry`、`harbor-trivy-0`）全部进入 `Ready` 状态。
     - 执行 `--uninstall --k8s`，Helm release 清理干净，同时 PVC 数据卷受 `resourcePolicy: keep` 保护完整留存。

### 3. 类别 03：S3 兼容对象存储 Silo (`platform-silo`)
- **定位**：S3-Compatible Object Storage，MinIO 的现代开源替代分支，由老冯维护。
- **镜像**：`pgsty/silo:RELEASE.2026-10-18T00-00-00Z`。
- **探针机制**：通过 `mc` 或 HTTP 端点 `GET /minio/health/live`，确保存储引擎在 `0.0.0.0:9000` 正常接收 S3 请求。

### 4. 类别 04：CMDB 动态清单与配置管理 (`platform-cmdb`)
- **定位**：Ansible-Core 自动化执行器的动态主机资产元数据提供者。
- **运行载体**：轻量级 Python HTTP 守护进程，常驻提供 `/healthz` 和 `/api/v1/inventory`。
- **探针机制**：定时探测 `/healthz` 返回 `{"status":"ok","service":"cmdb-api"}`。

### 5. 类别 05：Vault 密钥中枢 + Zitadel 身份后端 (`platform-vault-zitadel`)
- **定位**：零信任平台中枢，为所有安装器脚本提供动态凭据（AppRole/JWT）与统一 OIDC 认证。
- **镜像**：`hashicorp/vault:1.17.6` + `postgres:16-alpine`。
- **要点处理**：
  - Vault 默认客户端通信走 HTTPS，在 Dev 模式（`VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200`）下，必须显式注入 `VAULT_ADDR=http://127.0.0.1:8200`，否则健康检查 `vault status` 会因发送 HTTPS 握手失败而报告 `unhealthy`。
  - Zitadel 依赖的 PostgreSQL 实例独立挂载卷并在 15434 端口健康就绪。

### 6. 类别 06：声明式 GitOps 持续交付 (`platform-doco-cd`)
- **定位**：轻量级单机 GitOps 控制器，监听 Git 仓库并执行自动化部署收敛。
- **镜像**：`ghcr.io/kimdre/doco-cd:0.1.28`。
- **要点处理**：
  - 该容器为 Distroless / Scratch 静态二进制镜像，容器内**无 `sh`、`bash` 或 `wget`**，若定义 `CMD-SHELL` 健康检查会导致容器误报退出或 `unhealthy`。
  - 正确规范：去掉容器内 shell 探针，通过宿主机直接探测暴露的 `127.0.0.1:19088/v1/health` (`{"content":"healthy"}`) 以及 `127.0.0.1:19128/metrics`。
  - 数据卷绑定必须精确对齐 `/data`（非 `/app/data`），Docker Socket 绑定只读模式 `/var/run/docker.sock`。

### 7. 类别 07：云中立容器与向量底座 (`platform-k3s-pgvector`)
- **定位**：模拟 K3s 边缘工作节点上的向量知识库底座。
- **镜像**：`pgvector/pgvector:pg16`。
- **探针机制**：
  ```bash
  pg_isready -U k3s -d k3s_vector && psql -U k3s -d k3s_vector -c 'CREATE EXTENSION IF NOT EXISTS vector;'
  ```
  验收脚本在宿主机通过 `docker exec platform-k3s-pgvector psql` 查询 `pg_extension`，确认 `vector` 扩展成功载入。

### 8. 类别 08：数据库灾备还原演练 (`platform-pg-backup`)
- **定位**：用于第 9 章自动化快照、S3 同步及还原演练（Restore Drill）的基准源数据库。
- **镜像**：`postgres:16-alpine`。
- **探针机制**：`pg_isready -U postgres -d test_backup_db`。

### 9. 类别 09：AI 模型接入与路由网关 (`platform-ai-gateway`)
- **定位**：双层 AI 网关架构——New API 提供多租户、配额管理与渠道接入，LiteLLM 提供高可用负载均衡、重试路由与费用统计。
- **镜像**：`calciumion/new-api:v0.4.10` + `ghcr.io/berriai/litellm:v1.51.0`。
- **要点处理**：
  - New API 容器使用 `/usr/bin/wget -q -O - http://localhost:3000/api/status >/dev/null`（避免 `wget --spider` 默认发送的 HEAD 请求触发 404）。
  - LiteLLM 自 v1.50+ 起严格要求强制设置 Master Key，Compose 中注入 `LITELLM_MASTER_KEY=sk-...`。
  - LiteLLM 容器内无 `curl`，探针采用内置 Python 3 的 `urllib.request` 探测 `http://localhost:4000/health/liveliness`，成功返回 `"I'm alive!"`。

### 10. 类别 10：AI 基础设施 MCP 网关 (`platform-mcp-server`)
- **定位**：将基础设施运维能力（OpenTofu、Ansible、Vault 等）以 Model Context Protocol (MCP) 标准向智能体暴露的聚合网关。
- **架构**：编译为原生 Linux arm64 的 `infrastructure-mcp-server` 二进制，挂载至 `alpine:3.20` 镜像中，由守护进程拉起并通过 HTTP 端口 8080 暴露存活状态。
- **探针机制**：探测 `http://127.0.0.1:18888` 获得 `{"status":"ok","service":"infrastructure-mcp-server","version":"0.1.0"}`。

---

## 五、自动化验收验证脚本规范

整套验收脚本固化于测试套件目录：
[`scripts/orbstack-verification/verify-orbstack-all-services.sh`](file:///Users/shenlan/workspaces/ai-workspace-service/knowledge/scripts/orbstack-verification/verify-orbstack-all-services.sh)

### 一键执行与对账命令

```bash
# 进入测试目录并执行验收
cd /Users/shenlan/workspaces/ai-workspace-service/knowledge/scripts/orbstack-verification
./verify-orbstack-all-services.sh
```

### 真实输出凭证（OrbStack 实测）

```text
==============================================================================
🚀 开始在 MacOS 本机 OrbStack 执行 10 大核心服务类别单机部署与健康验收
==============================================================================
[INFO] 运行环境: MacOS arm64 | Version: 2.2.3 (2020300)
Commit: c83556b0ef8f1ba9a33abbb194622b6b7a1c0307 (v2.2.3)

------------------------------------------------------------------------------
[INFO] [01/10] 正在部署并验证类别: Git 与 CI/CD 引擎 (Gitea + Actions)
[INFO]   Compose 工程: platform-gitea (路径: 01-git-ci-gitea)
[PASS] Gitea API 正常响应: {"version":"1.22.6"}

------------------------------------------------------------------------------
[INFO] [02/10] 正在部署并验证类别: 云原生制品管理仓库 (Harbor)
[INFO]   Compose 工程: platform-harbor (路径: 02-artifact-harbor)
[PASS] Harbor (Artifact Management) Web UI 存活检查成功 (端口 18080)

------------------------------------------------------------------------------
[INFO] [03/10] 正在部署并验证类别: S3 兼容对象存储 (pgsty/silo)
[INFO]   Compose 工程: platform-silo (路径: 03-s3-storage-silo)
[PASS] Silo (S3-Compatible Object Storage) API 存活检查成功 (端口 19000)

------------------------------------------------------------------------------
[INFO] [04/10] 正在部署并验证类别: 配置管理与 CMDB 动态清单
[INFO]   Compose 工程: platform-cmdb (路径: 04-cmdb-inventory)
[PASS] CMDB 健康探针: {"status": "ok", "service": "cmdb-api"}
[PASS] CMDB 动态清单正常输出: hosts=platform-node-01 platform-node-02

------------------------------------------------------------------------------
[INFO] [05/10] 正在部署并验证类别: 密钥中枢与统一身份认证 (Vault + Zitadel)
[INFO]   Compose 工程: platform-vault-zitadel (路径: 05-identity-vault-zitadel)
[PASS] HashiCorp Vault 正常就绪 (端口 18200)
[PASS] Zitadel 后端 PostgreSQL 数据库就绪 (端口 15434)

------------------------------------------------------------------------------
[INFO] [06/10] 正在部署并验证类别: 声明式 GitOps 持续交付 (Doco CD)
[INFO]   Compose 工程: platform-doco-cd (路径: 06-gitops-doco-cd)
[PASS] Doco CD 控制器运行正常 (端口 19088 / 19128)

------------------------------------------------------------------------------
[INFO] [07/10] 正在部署并验证类别: 云中立容器与向量底座 (PostgreSQL + pgvector)
[INFO]   Compose 工程: platform-k3s-pgvector (路径: 07-container-vector-node)
[PASS] PostgreSQL 16 + pgvector 向量扩展正常加载 (端口 15435)

------------------------------------------------------------------------------
[INFO] [08/10] 正在部署并验证类别: 数据库灾备演练与还原沙箱
[INFO]   Compose 工程: platform-pg-backup (路径: 08-pg-backup-drill)
[PASS] PG 灾备演练源数据库就绪 (端口 15436)

------------------------------------------------------------------------------
[INFO] [09/10] 正在部署并验证类别: AI 模型接入与路由网关 (New API + LiteLLM)
[INFO]   Compose 工程: platform-ai-gateway (路径: 09-ai-gateway)
[PASS] New API 认证与限额服务就绪: {"data":{"version":"v1.0.0-rc.46",...},"success":true}
[PASS] LiteLLM 模型路由代理服务就绪 (端口 14000)

------------------------------------------------------------------------------
[INFO] [10/10] 正在部署并验证类别: AI 基础设施工具网关 (Infrastructure MCP)
[INFO]   Compose 工程: platform-mcp-server (路径: 10-mcp-server)
[PASS] Infrastructure MCP Server 守护网关就绪: {"status":"ok","service":"infrastructure-mcp-server","version":"0.1.0"}

==============================================================================
🎉 OrbStack 10 大核心服务类别单机部署验证全部完成！
==============================================================================
NAMES                         STATUS                        PORTS
platform-harbor-portal        Up About a minute (healthy)   127.0.0.1:18080->80/tcp
platform-ai-litellm           Up About a minute (healthy)   127.0.0.1:14000->4000/tcp
platform-ai-new-api           Up About a minute (healthy)   127.0.0.1:13001->3000/tcp
platform-doco-cd-controller   Up About a minute (healthy)   127.0.0.1:19088->80/tcp, 127.0.0.1:19128->9120/tcp
platform-vault-server         Up About a minute (healthy)   127.0.0.1:18200->8200/tcp
platform-mcp-gateway          Up 4 minutes (healthy)        127.0.0.1:18888->8080/tcp
platform-pg-backup-source     Up 5 minutes (healthy)        127.0.0.1:15436->5432/tcp
platform-k3s-pgvector         Up 6 minutes (healthy)        127.0.0.1:15435->5432/tcp
platform-zitadel-db           Up 13 minutes (healthy)       127.0.0.1:15434->5432/tcp
platform-cmdb-api             Up 14 minutes (healthy)       127.0.0.1:18000->8000/tcp
platform-silo-storage         Up 15 minutes (healthy)       127.0.0.1:19000->9000/tcp, 127.0.0.1:19001->9001/tcp
platform-gitea-server         Up 15 minutes (healthy)       127.0.0.1:13022->22/tcp, 127.0.0.1:13000->3000/tcp
```

---

## 六、相关引用与关联档案

- **多云白皮书总纲**：[多云平台工程技术白皮书（中文）](multi-cloud-platform-engineering-whitepaper.zh.md)
- **参考资料总索引**：[参考资料总索引与 PDF 合订编排](index.md)
- **记忆与存储系统规范**：[QMD + PG + 云盘三级任务聚合与记忆系统落地规范](qmd-pg-cloud-drive-three-tier-memory-spec.zh.md)
- **代码仓库来源**：
  - `platform-ops-toolkit`: Gitea (Ch02) 与 Vault+Zitadel (Ch05) 快速开始脚本
  - `iac_modules`: OpenTofu 与 Silo S3 (Ch03) 快速开始脚本
  - `playbooks`: Ansible CMDB (Ch04)、Harbor 制品管理 (Ch06.4 PR #743)、Doco CD (Ch06)、K3s+pgvector (Ch07) 快速开始脚本与 playbook roles
  - `postgresql.svc.plus`: PG 自动化备份与还原演练 (Ch09) 脚本
  - `ai-aggregator`: New API + LiteLLM AI Gateway (Ch10) 脚本
  - `Infrastructure-MCP-Server`: MCP 基础设施守护网关 (Ch10) 脚本
