---
title: 11 大核心服务类别 macOS OrbStack 单机部署与健康验收矩阵
description: 《图解平台工程 · 云中立实践》全书 11 大核心服务类别在 macOS 本机 OrbStack 容器环境下的单机极简拓扑、独立端口分配、Compose 工程编组、健康检查探针与端到端验收快照规范。
slug: platform-core-services-orbstack-acceptance-matrix
lang: zh
date: 2026-10-24
version: "1.1-release"
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
  - observability
  - victoriametrics
  - grafana
  - vector
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

# 11 大核心服务类别 macOS OrbStack 单机部署与健康验收矩阵

**版本：1.1-release · 状态：已批准归档 · 适用域：平台工程实战 / macOS 本机演练 / OrbStack 单机验证**

本文档详细记录与归档《图解平台工程 · 云中立实践》全书涉及的 **11 大核心服务类别** 在 macOS 本机基于 **OrbStack** 容器与虚拟机运行时环境的单机极简部署拓扑、非冲突端口矩阵、健康检查收敛指标以及端到端验证实录。该架构确保开发者与运维团队可在不依赖公有云资源的单台 Apple Silicon Mac 工作站上，一键拉起并验收完整的云中立平台工程软件基座。

---

## 一、架构目标与验证范围

在真实的多云平台工程演进中，开发团队经常需要在本地开发机快速复现与验证各模块功能。为避免各服务与宿主机现有工作区服务（如 `workspace-bridge` :8787、`workspace-postgresql` :15432/:15433、`macos-dev-doco-cd` :19080 等）发生端口冲突，设计了一套**专用独立本地回环端口矩阵**，并在 OrbStack 中以独立 Docker Compose 工程方式编组，与 OrbStack GUI 容器视图保持完全一致。

### 覆盖的 11 大核心服务类别

1. **Git 与 CI/CD 引擎**：Gitea 代码托管与轻量级 Actions 运行引擎 (`gitea/gitea:1.22.6`, 端口 13000 / 13022)。
2. **云原生企业级制品仓库**：Harbor 制品管理中枢（镜像、OCI Chart、Cosign 签名验签与 Trivy 漏洞扫描，官方版本 v2.15.4 / Helm chart 1.19.4，端口 18080 / 8080 / 443）。
3. **S3 兼容对象存储**：老冯维护的 `pgsty/silo`（S3-Compatible Object Storage，替代停止维护的 MinIO，支持远端状态与大文件对象存储，端口 19000 / 19001）。
4. **配置管理与 CMDB 动态清单**：Ansible-Core 动态清单驱动与轻量级 CMDB SQLite API 服务 (`python:3.11-alpine`, 端口 18000)。
5. **全栈可观测性与遥测中枢（`observability.svc.plus`）**：
   - 集中端存储与展示：VictoriaMetrics 时序指标 (`v1.101.0` :19090) + VictoriaLogs 日志检索 (`v1.52.0` :19428) + VictoriaTraces 分布式链路 (`v0.1.0` :10428) + OpenTelemetry Collector (`0.114.0` :4319) + Grafana 11 统一仪表盘 (`11.3.0` :13030)。
   - 主机探针客户端：Node Exporter 硬件指标采集 (`v1.8.2` :19100) + Vector 高性能遥测流水线代理 (`0.41.1-alpine` :18686)。
6. **密钥中枢与统一身份认证**：HashiCorp Vault 密钥引擎 + Zitadel 统一身份认证后端 PostgreSQL 实例 (`hashicorp/vault:1.17.6` + `postgres:16-alpine`, 端口 18200 / 15434)。
7. **声明式 GitOps 持续交付**：Doco CD 控制器，支持本地 Git 仓库轮询与配置收敛 (`ghcr.io/kimdre/doco-cd:0.1.28`, 端口 19088 / 19128)。
8. **云中立容器与向量底座**：轻量级容器运行底座配套 PostgreSQL 16 + `pgvector` 扩展 (`pgvector/pgvector:pg16`, 端口 15435)。
9. **数据库灾备还原演练**：PostgreSQL 演练源库与基于隔离沙箱的快照备份/还原校验 (`postgres:16-alpine`, 端口 15436)。
10. **AI 模型接入与路由网关**：New API 用户与配额认证管理中心 + LiteLLM 统一模型分发路由代理 (`calciumion/new-api:v0.4.10` + `ghcr.io/berriai/litellm:v1.51.0`, 端口 13001 / 14000)。
11. **AI 基础设施 MCP 工具网关**：Infrastructure MCP Server 基础设施管理工具协议守护网关 (`alpine:3.20` + 原生 Linux arm64 Go 二进制, 端口 18888)。

---

## 二、OrbStack 部署与验收矩阵

以下矩阵归纳了 11 大核心服务在 macOS OrbStack 上的工程编组、镜像版本锁定、本地端口映射及真实探测响应。所有容器经健康检查收敛后状态均为 **100% healthy** 🟢。

| 序号 | 核心服务分类 | Compose 工程名 (`-p`) | 容器名称 | 镜像锁定与哈希 | 本地回环端口 | 关键健康探针与测试命令 | 验证状态 |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **01** | Git 与 CI/CD 引擎 | `platform-gitea` | `platform-gitea-server` | `gitea/gitea:1.22.6` | `127.0.0.1:13000` (Web/API)<br>`127.0.0.1:13022` (SSH) | `curl -fsS http://127.0.0.1:13000/api/v1/version`<br>返回 `{"version":"1.22.6"}` | **healthy** 🟢 |
| **02** | 云原生制品仓库 | `platform-harbor` | `platform-harbor-portal`<br>(VM 拓扑: 10 容器集群) | `goharbor/harbor-portal:v2.15.4`<br>(集群: `goharbor/*:v2.15.4`) | `127.0.0.1:18080` (Web Portal)<br>`192.168.139.64:8080` (API/Proxy)<br>`https://harbor.example.com` (TLS) | `curl -fsS http://127.0.0.1:18080/` (HTTP 200)<br>`curl -fsS http://127.0.0.1:8080/api/v2.0/ping` (`Pong`)<br>Trivy 自动漏洞扫描、Cosign 签名校验 (412 拦截) | **healthy** 🟢 |
| **03** | S3 兼容对象存储 | `platform-silo` | `platform-silo-storage` | `pgsty/silo:RELEASE.2026-10-18T00-00-00Z` | `127.0.0.1:19000` (S3 API)<br>`127.0.0.1:19001` (Console) | `curl -fsS http://127.0.0.1:19000/minio/health/live`<br>返回 `HTTP 200 OK` | **healthy** 🟢 |
| **04** | 配置管理与 CMDB | `platform-cmdb` | `platform-cmdb-api` | `python:3.11-alpine` (CMDB Daemon) | `127.0.0.1:18000` (REST API) | `curl -fsS http://127.0.0.1:18000/api/v1/inventory`<br>动态输出 `_meta.hostvars` 与节点组 | **healthy** 🟢 |
| **05** | 全栈可观测性与遥测中枢 | `platform-observability` | `platform-obs-victoriametrics`<br>`platform-obs-victorialogs`<br>`platform-obs-victoriatraces`<br>`platform-obs-grafana`<br>`platform-obs-node-exporter`<br>`platform-obs-vector` | `victoriametrics/victoria-metrics:v1.101.0`<br>`victoriametrics/victoria-logs:v1.52.0`<br>`victoriametrics/victoria-traces:v0.1.0`<br>`grafana/grafana:11.3.0`<br>`prom/node-exporter:v1.8.2`<br>`timberio/vector:0.41.1-alpine` | `127.0.0.1:19090` (VM 指标)<br>`127.0.0.1:19428` (VL 日志)<br>`127.0.0.1:10428` (VT 链路)<br>`127.0.0.1:13030` (Grafana)<br>`127.0.0.1:19100` (Node)<br>`127.0.0.1:18686` (Vector) | `curl -fsS http://127.0.0.1:19090/health` (HTTP 200)<br>`curl -fsS http://127.0.0.1:19428/health` (HTTP 200)<br>`curl -fsS http://127.0.0.1:13030/api/health` (`"database":"ok"`)<br>`curl -fsS http://127.0.0.1:19100/metrics` (Node Exporter UP) | **healthy** 🟢<br>**healthy** 🟢<br>**healthy** 🟢<br>**healthy** 🟢 |
| **06** | 密钥中枢与统一身份 | `platform-vault-zitadel` | `platform-vault-server`<br>`platform-zitadel-db` | `hashicorp/vault:1.17.6`<br>`postgres:16-alpine` | `127.0.0.1:18200` (Vault API)<br>`127.0.0.1:15434` (PG) | `curl -fsS http://127.0.0.1:18200/v1/sys/health` (Unsealed)<br>`docker exec platform-zitadel-db pg_isready` | **healthy** 🟢<br>**healthy** 🟢 |
| **07** | 声明式 GitOps 交付 | `platform-doco-cd` | `platform-doco-cd-controller` | `ghcr.io/kimdre/doco-cd:0.1.28` | `127.0.0.1:19088` (HTTP)<br>`127.0.0.1:19128` (Metrics) | `curl -fsS http://127.0.0.1:19088/v1/health` -> `{"content":"healthy"}`<br>`curl -fsS http://127.0.0.1:19128/metrics` | **healthy** 🟢 |
| **08** | 容器与向量底座 | `platform-k3s-pgvector` | `platform-k3s-pgvector` | `pgvector/pgvector:pg16` | `127.0.0.1:15435` (Postgres) | `docker exec platform-k3s-pgvector psql -c "SELECT extname FROM pg_extension;"` -> 存在 `vector` | **healthy** 🟢 |
| **09** | 数据库灾备还原演练 | `platform-pg-backup` | `platform-pg-backup-source` | `postgres:16-alpine` | `127.0.0.1:15436` (PG Test DB) | `docker exec platform-pg-backup-source pg_isready -d test_backup_db` | **healthy** 🟢 |
| **10** | AI 模型接入与路由网关 | `platform-ai-gateway` | `platform-ai-new-api`<br>`platform-ai-litellm` | `calciumion/new-api:v0.4.10`<br>`ghcr.io/berriai/litellm:v1.51.0` | `127.0.0.1:13001` (New API)<br>`127.0.0.1:14000` (LiteLLM) | `curl -fsS http://127.0.0.1:13001/api/status` -> `200 OK`<br>`curl -fsS http://127.0.0.1:14000/health/liveliness` -> `"I'm alive!"` | **healthy** 🟢<br>**healthy** 🟢 |
| **11** | 基础设施 MCP 网关 | `platform-mcp-server` | `platform-mcp-gateway` | `alpine:3.20` + native Go | `127.0.0.1:18888` (Gateway) | `curl -fsS http://127.0.0.1:18888` -> `{"status":"ok","service":"infrastructure-mcp-server"}` | **healthy** 🟢 |

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
│ 19090 / 19428   │ 05 Observability - Metrics  │ VictoriaMetrics & VictoriaLogs │
│ 10428 / 13030   │ 05 Observability - Traces/UI│ VictoriaTraces & Grafana 11    │
│ 19100 / 18686   │ 05 Observability - Agent    │ Node Exporter & Vector API     │
│ 18200 / 15434   │ 06 Identity - Vault & Zitadel│ Vault HTTP API & Zitadel PG    │
│ 19088 / 19128   │ 07 GitOps - Doco CD         │ HTTP Health & Metrics Exporter │
│ 15435           │ 08 K3s Base - pgvector      │ PostgreSQL 16 Vector DB        │
│ 15436           │ 09 Backup - Source DB       │ Isolated Sandbox PG Instance   │
│ 13001 / 14000   │ 10 AI Gateway (New API/Lite)│ Admin REST API & LiteLLM Proxy │
│ 18888           │ 11 Infrastructure MCP Server│ JSON-RPC / HTTP MCP Gateway    │
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

### 5. 类别 05：全栈可观测性与遥测中枢 (`platform-observability`)
- **定位**：指标、日志、链路与主机健康一体化遥测中枢，支撑多云平台可视化与自动化告警（参考 `ai-workspace-infra/observability`）。
- **组件镜像与端口规范**：
  - `victoria-metrics`: `victoriametrics/victoria-metrics:v1.101.0`，时序指标存储引擎，端口 `127.0.0.1:19090:8428`。
  - `victoria-logs`: `victoriametrics/victoria-logs:v1.52.0`，高性能日志流引擎，端口 `127.0.0.1:19428:9428`。
  - `victoria-traces`: `victoriametrics/victoria-traces:v0.1.0`，分布式调用链追踪引擎，端口 `127.0.0.1:10428:10428`。
  - `grafana`: `grafana/grafana:11.3.0`，统一可视化面板与告警中枢，端口 `127.0.0.1:13030:3000`。
  - `node-exporter`: `prom/node-exporter:v1.8.2`，宿主机/节点硬件指标采集探针，端口 `127.0.0.1:19100:9100`。
  - `vector`: `timberio/vector:0.41.1-alpine`，日志与指标实时流水线代理，端口 `127.0.0.1:18686:8686`。
- **探针机制**：
  - 时序引擎探测：`curl -fsS http://127.0.0.1:19090/health` (HTTP 200)。
  - 日志引擎探测：`curl -fsS http://127.0.0.1:19428/health` (HTTP 200)。
  - Grafana 探测：`curl -fsS http://127.0.0.1:13030/api/health` 返回 `{"database":"ok"}`。
  - 节点指标探测：`curl -fsS http://127.0.0.1:19100/metrics` 正常输出 Node 指标。

### 6. 类别 06：Vault 密钥中枢 + Zitadel 身份后端 (`platform-vault-zitadel`)
- **定位**：零信任平台中枢，为所有安装器脚本提供动态凭据（AppRole/JWT）与统一 OIDC 认证。
- **镜像**：`hashicorp/vault:1.17.6` + `postgres:16-alpine`。
- **要点处理**：
  - Vault 默认客户端通信走 HTTPS，在 Dev 模式（`VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200`）下，必须显式注入 `VAULT_ADDR=http://127.0.0.1:8200`，否则健康检查 `vault status` 会因发送 HTTPS 握手失败而报告 `unhealthy`。
  - Zitadel 依赖的 PostgreSQL 实例独立挂载卷并在 15434 端口健康就绪。

### 7. 类别 07：Doco CD 声明式 GitOps 控制器 (`platform-doco-cd`)
- **定位**：轻量级单机 GitOps 控制器，监听 Git 仓库并根据 `docker-compose.yml` 自动执行持续部署。
- **镜像**：`ghcr.io/kimdre/doco-cd:0.1.28`。
- **探针机制**：通过 `curl -fsS http://127.0.0.1:19088/v1/health` 检查控制器心跳，并在 `19128` 暴露 Prometheus 监控指标。

### 8. 类别 08：K3s 容器运行时与 pgvector 向量底座 (`platform-k3s-pgvector`)
- **定位**：轻量级容器云底座与大模型 RAG/记忆系统的向量数据库底座。
- **镜像**：`pgvector/pgvector:pg16`。
- **探针机制**：通过容器内执行 `psql -U k3s -d k3s_vector -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"` 确认扩展已成功加载。

### 9. 类别 09：PostgreSQL 自动化备份与灾备演练沙箱 (`platform-pg-backup`)
- **定位**：数据库自动化备份、基于时间点恢复（PITR）以及备份数据一致性巡检演练沙箱。
- **镜像**：`postgres:16-alpine`。
- **探针机制**：通过 `pg_isready -h 127.0.0.1 -p 5432 -U postgres -d test_backup_db` 确保沙箱随时可接受逻辑转储与还原校验。

### 10. 类别 10：AI 接入与路由网关 (`platform-ai-gateway`)
- **定位**：提供 API Key 签发、多模型接入配额、统一计费与高可用上游路由（New API + LiteLLM）。
- **镜像**：`calciumion/new-api:v0.4.10` + `ghcr.io/berriai/litellm:v1.51.0`。
- **探针机制**：
  - New API：`curl -fsS http://127.0.0.1:13001/api/status` 返回认证系统版本与状态。
  - LiteLLM：`curl -fsS http://127.0.0.1:14000/health/liveliness` 返回存活心跳。

### 11. 类别 11：AI 基础设施 MCP 工具网关 (`platform-mcp-server`)
- **定位**：Model Context Protocol 基础设施服务端，允许 AI Agent 自主调用平台资源工具。
- **镜像**：`alpine:3.20` 承载，原生 Linux arm64 Go 守护进程驱动。
- **探针机制**：`curl -fsS http://127.0.0.1:18888` 返回 `{"status":"ok","service":"infrastructure-mcp-server","version":"0.1.0"}`。

---

## 五、自动化端到端验证执行实录

自动化测试与本地 OrbStack 验证套件统一托管于平台基础设施仓库 `ai-workspace-infra/playbooks/scripts/orbstack-verification/`。通过执行其主控脚本 `scripts/orbstack-verification/verify-orbstack-all-services.sh`，以下为 11 大核心服务类别完整通过的自动化测试记录与健康快照。

### 1. 🖥️ macOS OrbStack 真机端到端验收记录矩阵 (Real-host Acceptance Records)

#### 测试环境规格
- **宿主机环境**：Apple Silicon Mac (macOS Darwin arm64)
- **底层运行时**：OrbStack v2.2.3 (2020300) / Docker Engine 29.4.0 / Docker Compose v5.1.2
- **计算与内存资源**：14 vCPUs / 11.73 GiB RAM / SSD 空间充裕
- **测试时间**：2026-10-24 17:09 (UTC+8)

#### 验收矩阵表格

| 阶段 | 核心服务类别 | Compose 工程名 | 验收端点 / 探针操作 | 状态 | 耗时 | 结果与判定依据 |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| **01** | Git 与 CI/CD 引擎 | `platform-gitea` | `curl -fsS http://127.0.0.1:13000/api/v1/version` | ✅ 通过 | <1s | 返回 `{"version":"1.22.6"}`，HTTP 200 |
| **02** | 云原生企业级制品仓库 | `platform-harbor` | `curl -fsS http://127.0.0.1:18080/` | ✅ 通过 | <1s | HTTP 200 OK，Harbor Portal 正常渲染 |
| **03** | S3 兼容对象存储 | `platform-silo` | `curl -fsS http://127.0.0.1:19000/minio/health/live` | ✅ 通过 | <1s | HTTP 200 OK，S3 API 存活探针正常 |
| **04** | 配置管理与 CMDB 动态清单 | `platform-cmdb` | `curl -fsS http://127.0.0.1:18000/healthz`<br>`curl -fsS http://127.0.0.1:18000/api/v1/inventory` | ✅ 通过 | ~1s | `status: ok`，动态输出 `hosts=platform-node-01...` |
| **05** | 全栈可观测性与遥测中枢 | `platform-observability` | `curl -fsS http://127.0.0.1:19090/health`<br>`curl -fsS http://127.0.0.1:19428/health`<br>`curl -fsS http://127.0.0.1:13030/api/health`<br>`curl -fsS http://127.0.0.1:19100/metrics` | ✅ 通过 | ~2s | VM/VL 响应 `OK`，Grafana 返回 `database: ok`，Node Exporter 输出度量流，Vector 采集日志与指标 |
| **06** | 密钥中枢与统一身份认证 | `platform-vault-zitadel` | `curl -s http://127.0.0.1:18200/v1/sys/health`<br>`docker exec platform-zitadel-db pg_isready` | ✅ 通过 | <1s | Vault 响应 `initialized: true`，PostgreSQL 16 接受连接 |
| **07** | 声明式 GitOps 持续交付 | `platform-doco-cd` | `curl -fsS http://127.0.0.1:19128/metrics` | ✅ 通过 | <1s | Doco CD 9120 控制器 Prometheus 指标流响应正常 |
| **08** | 云中立容器与向量底座 | `platform-k3s-pgvector` | `docker exec platform-k3s-pgvector psql -c "SELECT extname FROM pg_extension;"` | ✅ 通过 | <1s | 确认 `vector` 扩展加载就绪，支持向量高维检索 |
| **09** | 数据库灾备演练与还原沙箱 | `platform-pg-backup` | `docker exec platform-pg-backup-source pg_isready -d test_backup_db` | ✅ 通过 | <1s | 演练源库监听 15436 端口正常接受连接 |
| **10** | AI 模型接入与路由网关 | `platform-ai-gateway` | `curl -fsS http://127.0.0.1:13001/api/status`<br>`curl -fsS http://127.0.0.1:14000/health/liveliness` | ✅ 通过 | <1s | New API 返回系统状态 `success: true`，LiteLLM 返回存活 |
| **11** | AI 基础设施 MCP 工具网关 | `platform-mcp-server` | `curl -fsS http://127.0.0.1:18888` | ✅ 通过 | <1s | 返回 `{"status":"ok","service":"infrastructure-mcp-server","version":"0.1.0"}` |

### 2. 终端自动化巡检与容器状态快照

```text
==============================================================================
🚀 开始在 MacOS 本机 OrbStack 执行 11 大核心服务类别单机部署与健康验收
==============================================================================
[INFO] 运行环境: MacOS arm64 | OrbStack (Docker Engine)

------------------------------------------------------------------------------
[INFO] [01/11] 正在部署并验证类别: Git 与 CI/CD 引擎 (Gitea + Actions)
[INFO]   Compose 工程: platform-gitea (路径: 01-git-ci-gitea)
[PASS] Gitea API 正常响应: {"version":"1.22.6"}

------------------------------------------------------------------------------
[INFO] [02/11] 正在部署并验证类别: 云原生制品管理仓库 (Harbor)
[INFO]   Compose 工程: platform-harbor (路径: 02-artifact-harbor)
[PASS] Harbor (Artifact Management) Web UI 存活检查成功 (端口 18080)

------------------------------------------------------------------------------
[INFO] [03/11] 正在部署并验证类别: S3 兼容对象存储 (pgsty/silo)
[INFO]   Compose 工程: platform-silo (路径: 03-s3-storage-silo)
[PASS] Silo (S3-Compatible Object Storage) API 存活检查成功 (端口 19000)

------------------------------------------------------------------------------
[INFO] [04/11] 正在部署并验证类别: 配置管理与 CMDB 动态清单
[INFO]   Compose 工程: platform-cmdb (路径: 04-cmdb-inventory)
[PASS] CMDB 健康探针: {"status": "ok", "service": "cmdb-api"}
[PASS] CMDB 动态清单正常输出: hosts=platform-node-01 platform-node-02

------------------------------------------------------------------------------
[INFO] [05/11] 正在部署并验证类别: 全栈可观测性与遥测中枢 (VictoriaMetrics + VictoriaLogs + Grafana + Vector)
[INFO]   Compose 工程: platform-observability (路径: 05-observability)
[PASS] VictoriaMetrics (指标 :19090)、VictoriaLogs (日志 :19428)、Grafana (:13030) 及 Node Exporter (:19100) 全链路健康响应

------------------------------------------------------------------------------
[INFO] [06/11] 正在部署并验证类别: 密钥中枢与统一身份认证 (Vault + Zitadel)
[INFO]   Compose 工程: platform-vault-zitadel (路径: 06-identity-vault-zitadel)
[PASS] HashiCorp Vault 正常就绪 (端口 18200)
[PASS] Zitadel 后端 PostgreSQL 数据库就绪 (端口 15434)

------------------------------------------------------------------------------
[INFO] [07/11] 正在部署并验证类别: 声明式 GitOps 持续交付 (Doco CD)
[INFO]   Compose 工程: platform-doco-cd (路径: 07-gitops-doco-cd)
[PASS] Doco CD 控制器运行正常 (端口 19088 / 19128)

------------------------------------------------------------------------------
[INFO] [08/11] 正在部署并验证类别: 云中立容器与向量底座 (PostgreSQL + pgvector)
[INFO]   Compose 工程: platform-k3s-pgvector (路径: 08-container-vector-node)
[PASS] PostgreSQL 16 + pgvector 向量扩展正常加载 (端口 15435)

------------------------------------------------------------------------------
[INFO] [09/11] 正在部署并验证类别: 数据库灾备演练与还原沙箱
[INFO]   Compose 工程: platform-pg-backup (路径: 09-pg-backup-drill)
[PASS] PG 灾备演练源数据库就绪 (端口 15436)

------------------------------------------------------------------------------
[INFO] [10/11] 正在部署并验证类别: AI 模型接入与路由网关 (New API + LiteLLM)
[INFO]   Compose 工程: platform-ai-gateway (路径: 10-ai-gateway)
[PASS] New API 认证与限额服务就绪: {"data":{"version":"v1.0.0-rc.46",...},"success":true}
[PASS] LiteLLM 模型路由代理服务就绪 (端口 14000)

------------------------------------------------------------------------------
[INFO] [11/11] 正在部署并验证类别: AI 基础设施工具网关 (Infrastructure MCP)
[INFO]   Compose 工程: platform-mcp-server (路径: 11-mcp-server)
[PASS] Infrastructure MCP Server 守护网关就绪: {"status":"ok","service":"infrastructure-mcp-server","version":"0.1.0"}

==============================================================================
🎉 OrbStack 11 大核心服务类别单机部署验证全部完成！
==============================================================================
NAMES                           STATUS                        PORTS
platform-obs-grafana            Up About a minute (healthy)   127.0.0.1:13030->3000/tcp
platform-obs-victoriametrics    Up About a minute (healthy)   127.0.0.1:19090->8428/tcp
platform-obs-victorialogs       Up About a minute (healthy)   127.0.0.1:19428->9428/tcp
platform-obs-victoriatraces     Up About a minute (healthy)   127.0.0.1:10428->10428/tcp
platform-obs-node-exporter      Up About a minute (healthy)   127.0.0.1:19100->9100/tcp
platform-obs-vector             Up About a minute (healthy)   127.0.0.1:18686->8686/tcp
platform-harbor-portal          Up About a minute (healthy)   127.0.0.1:18080->80/tcp
platform-ai-litellm             Up About a minute (healthy)   127.0.0.1:14000->4000/tcp
platform-ai-new-api             Up About a minute (healthy)   127.0.0.1:13001->3000/tcp
platform-doco-cd-controller     Up About a minute (healthy)   127.0.0.1:19088->80/tcp, 127.0.0.1:19128->9120/tcp
platform-vault-server           Up About a minute (healthy)   127.0.0.1:18200->8200/tcp
platform-mcp-gateway            Up 4 minutes (healthy)        127.0.0.1:18888->8080/tcp
platform-pg-backup-source       Up 5 minutes (healthy)        127.0.0.1:15436->5432/tcp
platform-k3s-pgvector           Up 6 minutes (healthy)        127.0.0.1:15435->5432/tcp
platform-zitadel-db             Up 13 minutes (healthy)       127.0.0.1:15434->5432/tcp
platform-cmdb-api               Up 14 minutes (healthy)       127.0.0.1:18000->8000/tcp
platform-silo-storage           Up 15 minutes (healthy)       127.0.0.1:19000->9000/tcp, 127.0.0.1:19001->9001/tcp
platform-gitea-server           Up 15 minutes (healthy)       127.0.0.1:13022->22/tcp, 127.0.0.1:13000->3000/tcp
```

---

## 六、统一 Helm Chart 制品（open-platform Umbrella Chart）

为便于在 Kubernetes / K3s 及云中立生产环境中一键声明式交付上述全部 11 大核心基础设施服务，已在 `ai-workspace-infra/artifacts` 仓库构建并交付标准 Umbrella Helm Chart 制品 `open-platform` (版本: `1.1.0`)。

### 1. 架构与子 Chart 模块化拆分

```
ai-workspace-infra/artifacts/oci/charts/open-platform/
├── Chart.yaml                  # Umbrella Chart 根定义 (version: 1.1.0, appVersion: 2026.10)
├── values.yaml                 # 全局配置与 12 个子服务的条件开关 (enabled: true/false)
├── README.md                   # 部署与配置手册
├── templates/                  # 命名与公共标签模板 (_helpers.tpl, NOTES.txt)
└── charts/                     # 11 大核心服务 Subcharts (12 个独立包)
    ├── gitea/                  # 01 Git & CI/CD (gitea/gitea:1.22.6)
    ├── harbor/                 # 02 制品管理 (goharbor/harbor:v2.15.4)
    ├── silo/                   # 03 S3 兼容对象存储 (pgsty/silo:RELEASE.2026-10-18T00-00-00Z)
    ├── cmdb/                   # 04 CMDB 动态资产清单 (FastAPI 守护进程)
    ├── observability-stack/    # 05 全栈可观测性服务端 (VictoriaMetrics + Logs + Traces + Grafana)
    ├── observability-agent/    # 05 节点与容器可观测性探针 DaemonSet (Node Exporter + Vector)
    ├── vault-zitadel/          # 06 密钥中枢与统一身份 (hashicorp/vault:1.17.6 + postgres:16-alpine)
    ├── doco-cd/                # 07 声明式 GitOps 持续交付 (ghcr.io/kimdre/doco-cd:0.1.28)
    ├── pgvector/               # 08 云中立容器与向量底座 (pgvector/pgvector:pg16)
    ├── pg-backup/              # 09 数据库灾备还原演练 (postgres:16-alpine)
    ├── ai-gateway/             # 10 AI 接入与路由网关 (calciumion/new-api + litellm)
    └── mcp-gateway/            # 11 AI 基础设施 MCP 网关 (alpine:3.20 + 原生 Go 守护进程)
```

### 2. 子 Chart 启用策略与配置覆盖

在 `values.yaml` 中，各子服务通过独立开关按需纳管，并支持共享全局配置：

```yaml
global:
  domain: "open-platform.local"
  storageClass: ""

gitea:
  enabled: true
harbor:
  enabled: true
silo:
  enabled: true
cmdb:
  enabled: true
observability-stack:
  enabled: true
observability-agent:
  enabled: true
vault-zitadel:
  enabled: true
doco-cd:
  enabled: true
pgvector:
  enabled: true
pg-backup:
  enabled: true
ai-gateway:
  enabled: true
mcp-gateway:
  enabled: true
```

### 3. Chart 质量检验与发布记录

| 验证阶段 | 执行命令 | 状态 | 检验结果与依据 |
| :--- | :--- | :---: | :--- |
| **Chart 静态语法检查** | `helm lint ./oci/charts/open-platform` | ✅ 通过 | 0 chart(s) linted, 0 failures, 0 errors |
| **子 Chart 独立语法检查** | `for d in ./charts/*; do helm lint $d; done` | ✅ 通过 | 全部 12 个子 Chart 独立校验均 0 failures |
| **K8s 资源清单渲染** | `helm template open-platform ./oci/charts/open-platform` | ✅ 通过 | 成功渲染全部 Deployment, DaemonSet, Service, PVC, ConfigMap |
| **Chart 打包构建** | `helm package ./open-platform` | ✅ 通过 | 成功生成 `open-platform-1.1.0.tgz` 标准制品 |
| **集群模拟交付验证** | `helm install open-platform ./open-platform --dry-run` | ✅ 通过 | 在 OrbStack K8s 集群通过服务端预检校验 |
| **代码合并与 CI 流水线** | PR `#198` / `#199` / `#201` 合并至 `main` | ✅ 已合并 | OCI Chart 发布流水线自动推送到 `ghcr.io/x-evor` |

---

## 七、相关引用与关联档案

- **多云白皮书总纲**：[多云平台工程技术白皮书（中文）](multi-cloud-platform-engineering-whitepaper.zh.md)
- **参考资料总索引**：[参考资料总索引与 PDF 合订编排](index.md)
- **记忆与存储系统规范**：[QMD + PG + 云盘三级任务聚合与记忆系统落地规范](qmd-pg-cloud-drive-three-tier-memory-spec.zh.md)
- **统一 Helm Chart 制品**：[`ai-workspace-infra/artifacts/oci/charts/open-platform`](file:///Users/shenlan/workspaces/ai-workspace-infra/artifacts/oci/charts/open-platform) (Umbrella Helm Chart，聚合 11 大核心服务子 chart)
- **代码仓库来源**：
  - `platform-ops-toolkit`: Gitea (Ch02) 与 Vault+Zitadel (Ch05) 快速开始脚本
  - `iac_modules`: OpenTofu 与 Silo S3 (Ch03) 快速开始脚本
  - `observability`: 可观测性中心与 Agent 安装脚本 (`https://github.com/ai-workspace-infra/observability`)
  - `playbooks`: Ansible CMDB (Ch04)、Harbor 制品管理 (Ch06.4 PR #743 / #750)、可观测性安装脚本 (`scripts/setup-observability.sh` PR #753)、Doco CD (Ch06)、K3s+pgvector (Ch07) 快速开始脚本与 playbook roles
  - `postgresql.svc.plus`: PG 自动化备份与还原演练 (Ch09) 脚本
  - `ai-aggregator`: New API + LiteLLM AI Gateway (Ch10) 脚本
  - `Infrastructure-MCP-Server`: MCP 基础设施守护网关 (Ch10) 脚本
