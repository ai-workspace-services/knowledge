---
title: Infrastructure-MCP-Server 部署、集中式可观测性、CMDB 与 QMD 记忆系统交付全景技术规范
description: 面向 macOS/本地基座部署的 Infrastructure-MCP-Server、集中式可观测性 4-MCP、多云 CMDB 动态对账、Environment Graph 15 依赖边拓扑与 QMD 知识向量化同步的全景交付技术规范。
slug: infrastructure-mcp-observability-cmdb-qmd-delivery-spec
lang: zh
date: 2026-10-28
version: "1.0"
status: release
category: reference
tags:
  - infrastructure-mcp-server
  - observability
  - cmdb
  - qmd
  - graph-database
  - multi-cloud
  - safe-cli
---

# Infrastructure-MCP-Server 部署、集中式可观测性、CMDB 与 QMD 记忆系统交付全景技术规范

**版本：1.0 · 发布基线：2026-10-28 · 源码提交：`36f7441`（PR #4 合并） · 状态：已验证并落地**

[参考资料总索引](index.md) · [多云平台工程技术白皮书](multi-cloud-platform-engineering-whitepaper.zh.md) · [多云资源三档权限与 Shared CMDB 技术规范白皮书](multi-cloud-iam-vault-cmdb-security-whitepaper.zh.md) · [QMD 三级任务聚合与记忆系统落地规范](qmd-pg-cloud-drive-three-tier-memory-spec.zh.md)

---

## 摘要

本白皮书记录了在 macOS 开发者环境部署 **`Infrastructure-MCP-Server`** 基础设施模型上下文协议（MCP）网关、对接 **`observability.svc.plus`** 集中式监控集群数据源、打通四仓（GitOps、Playbooks、IaC Modules、Platform-Orchestrator）及 Vault 密钥路径、建立 **CMDB 多云资源动态对账与受控 CLI 工具调用**、关联 **Environment Graph 15 条依赖边拓扑**，以及本地 **QMD MCP** 历史记忆与参考文档向量化同步的完整交付规范。

本规范确立了以“**网关统一收口、只读协议保全、图谱动态联动、受控安全执行、记忆每日对齐**”为核心原则的基础设施可观测性与资产运维体系。

---

## 一、系统架构全景与组件职责分工

```mermaid
flowchart TD
    subgraph ClientLayer ["Agent & IDE 客户端交互层"]
        Agent["Antigravity / Codex / XWorkmate Agent / Trae / Cursor"]
    end

    subgraph DevK3sV5 ["dev-k3s-v5 节点 (Akamai Linode jp-tyo-3 2C4G 独立网关集群)"]
        Traefik_Edge["Traefik Ingress Controller (dev-web-saas / hostPort 80/443 / ACME dev-http01)"]
        
        subgraph PlatformMCP ["Namespace: platform-mcp (Restricted PSA)"]
            Infra_Gateway_Pod["infrastructure-mcp-server:8080<br>(mcp-server.svc.plus /)<br>SSE / Streamable HTTP"]
            Obsy_Gateway_Pod["observability-mcp-gateway:8000<br>(mcp-server.svc.plus /v1/grafana)<br>mcp-grafana (SSE --base-path /v1/grafana)"]
        end
    end

    subgraph LocalHost ["MacOS 开发者本机运行环境 (可选本地 CLI 模式)"]
        MCP_Config["~/.gemini/config/mcp_config.json"]
        Infra_Bin["/Users/shenlan/.local/bin/infrastructure-mcp-server"]
        Infra_Cfg["~/.config/infrastructure-mcp-server/config.json"]
        
        subgraph LocalMCP ["本机 MCP 服务阵列"]
            Infra_Gateway["Infrastructure-MCP-Server (Local Stdio)"]
            CMDB_Store["CMDB Store (SIT / UAT / PROD 多云资产)"]
            Graph_Store["Environment Graph (15 边依赖拓扑引擎)"]
            CLI_Exec["Safe Read-Only CLI Runner (linode/aws/gcloud/gh)"]
            QMD_MCP["QMD MCP Server (pg + pgvector :15432)"]
        end
        
        QMD_Sync["scripts/sync-knowledge-to-qmd.sh (每日 03:00 Cron)"]
    end

    subgraph ObservabilityStack ["集中式可观测性服务核心集群 (observability.svc.plus)"]
        Caddy_Edge["Caddy 反向代理网关 (TLS / Zitadel JWT Forward Auth)"]
        VM["VictoriaMetrics (Metrics TSDB: :8428)"]
        VL["VictoriaLogs (LogsQL 引擎: :9428)"]
        VT["VictoriaTraces (OTLP 链路: :10428)"]
        GF["Grafana (仪表盘与告警: :3000)"]
        BB["Blackbox Exporter (网络与主机拨测: :9115)"]
    end

    subgraph KnowledgeBase ["历史参考文档 (Knowledge Base)"]
        RefDocs["ai-workspace-service/knowledge/docs/reference (194 篇 Markdown)"]
    end

    Agent -->|远程 HTTPS/SSE| Traefik_Edge
    Traefik_Edge -->|mcp-server.svc.plus /| Infra_Gateway_Pod
    Traefik_Edge -->|mcp-server.svc.plus /v1/grafana| Obsy_Gateway_Pod
    
    Infra_Gateway_Pod -->|内部聚合 / 遥测查询| Obsy_Gateway_Pod
    Obsy_Gateway_Pod -->|上游数据查询透传| Caddy_Edge
    Caddy_Edge --> VM & VL & VT & GF
    
    Agent -.->|本地开发模式| MCP_Config
    MCP_Config --> Infra_Bin
    MCP_Config --> QMD_MCP
    Infra_Bin --> Infra_Gateway
    Infra_Gateway --> CMDB_Store & Graph_Store & CLI_Exec
    
    RefDocs -->|定时增量对齐/BM25/向量索引| QMD_Sync
    QMD_Sync --> QMD_MCP
```

### 1.1 核心组件边界与职责

1. **Infrastructure-MCP-Server 网关**：
   * 采用 Go 原生并发模型编写，支持 Streamable HTTP / SSE 远程后端协议与本地 CLI 进程子通道。
   * 屏蔽后端网络差异与认证细节，向智能体呈现统一的 `infra.*` 工具空间。
2. **集中式可观测性集群（`observability.svc.plus`）**：
   * 部署于核心节点，由 Caddy 承接统一反向代理与 TLS 卸载。
   * 遥测数据通道与 Agent 诊断通道物理隔离，MCP 适配器实施严格只读限制（禁止修改仪表盘、告警策略或重写时序数据）。
3. **动态 CMDB 存储引擎**：
   * 自动聚合 GitOps 声明、Ansible Playbooks 清单、Terraform 状态（State）及流水线部署元数据。
   * 将异构多云资源映射为标准化的 `Resource` 模型，并输出环境部署综述（`EnvironmentSummary`）。
4. **Environment Graph 拓扑图**：
   * 维护服务节点、数据源节点、代码仓库节点、凭据节点及多云环境节点的依赖网络。
   * 支持精确按 `node_id` 进行一阶邻居子图（Subgraph）检索，为发布变更影响面分析提供数学图模型支撑。
5. **本地 QMD 记忆系统**：
   * 基于本地 PostgreSQL 15432（搭载 `pgvector` 扩展）搭建，承载全量历史白皮书、运维手册与架构契约检索。
   * 提供 Lexical（BM25）与 Vector 双通道混合检索，确保在离线或无外部嵌入 API 密钥时依然具备可靠记忆检索能力。

---

## 二、集中式可观测性对接规范 (`observability.svc.plus` 与 `mcp-server.svc.plus`)

集中式可观测性平台承载多云双平面的实时遥测数据存储与分析，各组件直查路径（数据面）与解耦后的统一 MCP 接入网关（控制面，统一收敛至 `mcp-server.svc.plus/v1`，部署于 `dev-k3s-v5`）映射如下：

| 组件名称 | 核心功能 | 遥测写入 / 直查路径 (`observability.svc.plus`) | 统一 MCP 网关 Endpoint (`mcp-server.svc.plus`) | 数据传输协议 | 只读安全基线 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **VictoriaMetrics** | 指标存储与 MetricsQL 分析 | `https://observability.svc.plus/ingest/metrics/api/v1/write`<br>`https://observability.svc.plus/vmetrics/` | `https://mcp-server.svc.plus/v1/metrics/mcp` | Streamable HTTP / MetricsQL | 只读时序检索 |
| **VictoriaLogs** | 高基数系统与应用日志 | `https://observability.svc.plus/ingest/logs/insert/jsonline`<br>`https://observability.svc.plus/vlogs/` | `https://mcp-server.svc.plus/v1/logs/mcp` | Streamable HTTP / LogsQL | 只读日志检索 |
| **VictoriaTraces** | 分布式微服务调用链追踪 | `https://observability.svc.plus/ingest/otlp/v1/traces`<br>`https://observability.svc.plus/vtraces/` | `https://mcp-server.svc.plus/v1/traces/mcp` | Streamable HTTP / TraceQL | 只读链路排查 |
| **Grafana** | 统一大盘与告警可视化 | `https://observability.svc.plus/grafana/` | `https://mcp-server.svc.plus/v1/grafana/sse` | **SSE** (`--base-path /v1/grafana`) | `--disable-write`<br>`--disable-admin`<br>Viewer Token |
| **Blackbox Exporter** | 网络、端口与域名探测 | `https://observability.svc.plus/blackbox/` | 内置合成拨测链路 | HTTP/TCP ICMP Prober | 只读网络拨测 |

### 2.1 探测工具：`infra.observability.status`

网关内置非阻塞探测探针，执行以下流程：
1. 发送 HTTP `HEAD` 请求至 `https://observability.svc.plus/`（配置 5 秒超时，不跟随重定向）。
2. 计算实时网络往返延迟（Latency），验证 Caddy 反向代理网关在线健康度。
3. 输出完整的 4-MCP 适配器地址、对应仓库链接（`gitops`, `playbooks`, `iac_modules`, `Platform-Orchestrator`, `knowledge`）及 Vault 密钥路径：
   * `kv/<env>/platform/observability`
   * `kv/data/observability/mcp`
   * `kv/data/prod/ulighthost-xconnect/observability.svc.plus`

---

## 三、CMDB 资产模型与 Environment Graph 15 依赖边拓扑

### 3.1 `service/observability-gateway` 拓扑拓扑网络

在系统架构中，`service/observability-gateway` 处于中心反向代理枢纽位置。通过图数据库拓扑引擎分析，其精确关联 15 条有向依赖边：

```mermaid
flowchart LR
    subgraph UpstreamSources ["上游配置与编排声明源 (6 条入边)"]
        GitOps["repo/gitops"] -->|declares_topology| GW["service/observability-gateway<br>(observability.svc.plus)"]
        Playbooks["repo/playbooks"] -->|deploys| GW
        IaC["repo/iac-modules"] -->|provisions_dns| GW
        Orch["repo/platform-orchestrator"] -->|orchestrates| GW
        Vault["service/vault"] -->|provides_credentials| GW
        IAM["service/iam"] -->|provides_auth| GW
    end

    subgraph InternalRoutes ["网关内部反向代理路由 (5 条出边)"]
        GW -->|routes_to| VM["datasource/victoriametrics"]
        GW -->|routes_to| VL["datasource/victorialogs"]
        GW -->|routes_to| VT["datasource/victoriatraces"]
        GW -->|routes_to| GF["datasource/grafana"]
        GW -->|routes_to| BB["datasource/blackbox"]
    end

    subgraph MCPExposures ["只读智能体 MCP 适配器暴露 (4 条出边)"]
        GW -->|exposes_mcp| MCP_GF["mcp/grafana"]
        GW -->|exposes_mcp| MCP_VM["mcp/victoriametrics"]
        GW -->|exposes_mcp| MCP_VL["mcp/victorialogs"]
        GW -->|exposes_mcp| MCP_VT["mcp/victoriatraces"]
    end
```

通过调用 `infra.cmdb.query` 传入参数 `{"node_id": "service/observability-gateway"}`，网关可在 10 毫秒内完成子图抽取，同时命中 CMDB 资源 `prod/dns/observability-prod`，输出完整的依赖边清单与关联节点属性。

### 3.2 SIT / UAT / PROD 部署现状对照表

CMDB 对全环境资产进行了动态纳管与分类：

| 环境层级 | 部署模式与架构定位 | 云基础设施供应商 | 托管域名与端点 | 运行健康状态 |
| :--- | :--- | :--- | :--- | :--- |
| **SIT** | 100% selfhost VPS（`all-in-one.yaml`），按 PR 自动化流水线按需触发拉起 | Vultr, Cloudflare | `console-sit.onwalk.net`<br>`accounts-sit.onwalk.net` | **standby**（待命状态，触发 PR 时唤醒并更新 DNS） |
| **UAT** | 混合架构（Akamai Linode open-platform 核心节点 + Vultr Web SaaS + GCP Serverless 兜底） | Akamai Linode, Vultr, GCP, Cloudflare | `console-uat.onwalk.net` (200 OK)<br>`accounts-uat.onwalk.net`<br>`agent-proxy.onwalk.net`<br>`infra-platform.onwalk.net` | **healthy**（全栈运行中，Linode `45.79.175.119` 承载可观测性/Vault/IAM） |
| **PROD** | 多云双平面（GCP 控制台节点 + AWS Tokyo 边缘代理 + Vultr K3s + Cloudflare CDN 全局接入） | GCP, AWS, Vultr, Cloudflare | `svc.plus` (200 OK)<br>`console.svc.plus` (200 OK)<br>`observability.svc.plus` (200 OK)<br>`vault.svc.plus` (200 OK) | **healthy**（高可用多活，具备零成本故障切换与只读诊断接口） |

---

## 四、安全受控本地 CLI 执行规范 (Safe CLI Guardrails)

为赋予智能体在本地排障时直接利用云厂商官方 CLI（`linode-cli`, `aws`, `gcloud`, `gh`）和基础网络工具（`curl`, `jq`）的能力，同时严防越权写操作与误删线上资产，网关实施了强制只读拦截策略：

```mermaid
flowchart TD
    Req["Agent 发起 infra.cli.exec(command, args)"] --> WhiteCheck{"命令是否在白名单中?<br>(linode-cli / aws / gcloud / gh / curl / jq)"}
    WhiteCheck -- 否 --> Err1["返回拦截错误: 不受支持或未授权的命令"]
    WhiteCheck -- 是 --> VerbCheck{"参数中是否包含变更/破坏性动词?<br>(delete / destroy / drop / rm / stop / apply / push / write 等)"}
    VerbCheck -- 是 --> Err2["返回安全违背错误: 变更操作被只读安全策略拦截"]
    VerbCheck -- 否 --> MethodCheck{"是否为 curl 命令?"}
    MethodCheck -- 是 --> CurlCheck{"是否包含 -X POST/PUT/DELETE<br>或包含 -d / --data 提交请求体?"}
    CurlCheck -- 是 --> Err3["返回安全违背错误: 拦截非 GET/HEAD 请求或数据提交"]
    CurlCheck -- 否 --> Exec["context.WithTimeout (15s) 受控执行命令"]
    MethodCheck -- 否 --> Exec
    Exec --> Res["返回 stdout, stderr, exit_code 结构化 JSON"]
```

### 4.1 安全红线策略矩阵

1. **白名单命令集**：`linode-cli`, `aws`, `gcloud`, `gh`, `curl`, `jq`。
2. **绝对阻断词（忽略大小写精确与前缀匹配）**：
   * 破坏性动作：`delete`, `destroy`, `remove`, `rm`, `drop`, `terminate`, `kill`, `reboot`, `shutdown`, `stop`。
   * 变更性动作：`create`, `insert`, `post`, `put`, `update`, `modify`, `set`, `apply`, `push`, `write`, `patch`, `truncate`。
3. **HTTP 规范约束**：`curl` 禁止使用 `-X POST`, `-X DELETE`, `-X PUT`, `-X PATCH`，且严禁传递任何请求体（`-d`, `--data`）。
4. **运行超时硬限制**：所有命令通过独立的 `context.WithTimeout` 运行，上限设置为 15 秒，超时强制 `SIGKILL`。

---

## 五、历史参考文档与 QMD 记忆系统同步机制

### 5.1 QMD 向量化与检索能力

* **底层存储**：本地 PostgreSQL 15432，使用 `pgvector` 插件进行高维相似度向量计算。
* **双模态检索**：
  * **Vector Embedding**：当提供外部 Embedding API 密钥时，自动生成密集向量嵌入。
  * **Lexical BM25 降级**：当无外部 API Key 或处于断网/离线开发模式时，自动采用高性能全文倒排与 BM25 算法检索，确保 100% 检索可用性。
* **当前环境实测状态**：开发机环境未配置外部 Embedding 模型 API Key，系统当前全面运行于高性能 **BM25 词法全文倒排检索模式**，已收录全量 193 篇白皮书；未建立稠密向量索引，待后续注入大模型凭证后可自动激活稠密向量检索。

### 5.2 自动化增量同步流水线

同步脚本位于 [`scripts/sync-knowledge-to-qmd.sh`](file:///Users/shenlan/workspaces/ai-workspace-infra/Infrastructure-MCP-Server/scripts/sync-knowledge-to-qmd.sh)，执行逻辑包含：
1. 校验本地 PostgreSQL 15432 服务可达性与 `qmd` CLI 可用性。
2. 创建或更新专用集合 `knowledge-reference`。
3. 递归扫描 [`knowledge/docs/reference/`](file:///Users/shenlan/workspaces/ai-workspace-service/knowledge/docs/reference) 目录下全部 Markdown 文档（共计 192 篇），生成 SHA-256 校验和以实现增量感知。
4. 捕获 Embedding 退出码；遇 API Key 限制自动记录并安全降级，保障退出码为 0。

### 5.3 `/schedule` 守护定时任务配置

在 Agent 会话中注册了常驻守护定时任务（`task-324`）：
* **任务 ID**：`98968fef-be1e-4f11-9866-7eca7b9ce976/task-324`
* **Cron 表达式**：`0 3 * * *`（每日凌晨 03:00 自动触发）
* **守护模式**：`IsDaemon: true`（会话关闭后持续运行）

---

## 六、交付生命周期与 GitHub PR 记录

| 阶段 | 提交 SHA | 变更内容 | 验证与合并状态 |
| :--- | :--- | :--- | :--- |
| **阶段 1：可观测性对接** | `738d555` | 实现 HTTP/SSE 客户端、`observability.svc.plus` 探针、Seed 拓扑种子与 QMD 同步脚本 | 通过单元测试与集成拨测 |
| **阶段 2：CMDB 与安全 CLI** | `75f6d77` | 新增 `internal/cmdb` 引擎、安全 CLI 守卫拦截、Graph Subgraph 拓扑联动与 GitHub/Cloudflare MCP 插槽 | 通过所有安全拦截测试用例 |
| **阶段 3：代码审查与合并** | [`36f7441`](https://github.com/ai-workspace-infra/Infrastructure-MCP-Server/commit/36f7441) | 提交并在 GitHub 成功合并 [PR #4](https://github.com/ai-workspace-infra/Infrastructure-MCP-Server/pull/4) 到 `main` 分支 | **PR #4 Merged** |
| **阶段 4：客户端配置与验证** | [`4648af6`](https://github.com/ai-workspace-infra/Infrastructure-MCP-Server/commit/4648af6) | 提交并在 GitHub 成功合并 [PR #6](https://github.com/ai-workspace-infra/Infrastructure-MCP-Server/pull/6) 与 [PR #7](https://github.com/ai-workspace-infra/Infrastructure-MCP-Server/pull/7) | **PR #6, #7 Merged** |
| **阶段 5：服务端网关与只读加固** | [`PR #820`](https://github.com/ai-workspace-infra/playbooks/pull/820) | 在 `playbooks` 仓库修复 `mcp-grafana` `--base-path /mcp/v1/grafana`、Caddy `handle` 透传及 `--disable-write` 只读安全红线 | **Playbooks PR #820 Merged** |

编译产物已通过 `go build` 重新编译，落盘至生产路径 [`/Users/shenlan/.local/bin/infrastructure-mcp-server`](file:///Users/shenlan/.local/bin/infrastructure-mcp-server)。

---

## 七、附录：工具接口速查手册 (Tools Catalog)

### 7.1 核心内置工具列表

```json
[
  {
    "name": "infra.cmdb.summary",
    "description": "Concise summary of SIT, UAT, and PROD infrastructure deployments, domains, and statuses."
  },
  {
    "name": "infra.cmdb.query",
    "description": "Query CMDB inventory resources (filters: environment, provider, kind, status) with optional graph topology linkage or node_id inspection."
  },
  {
    "name": "infra.cmdb.sync",
    "description": "Trigger synchronization of CMDB resources from IaC, GitOps, CI/CD pipelines, and local CLI tools."
  },
  {
    "name": "infra.cli.exec",
    "description": "Safely execute read-only cloud/infrastructure CLI commands (linode-cli, aws, gcloud, gh, curl, jq) with strict guardrails."
  },
  {
    "name": "infra.observability.status",
    "description": "Inspect the live status, data ingestion endpoints, and MCP adapters of the centralized observability stack (observability.svc.plus)."
  },
  {
    "name": "infra.graph.query",
    "description": "Query the Environment Graph for infrastructure nodes and relationships."
  },
  {
    "name": "infra.backends",
    "description": "List configured Infrastructure MCP backends and their capabilities."
  },
  {
    "name": "infra.health",
    "description": "Check connectivity to configured Infrastructure MCP backends."
  }
]
```

### 7.2 典型调用示例

#### 1. 精确检索 `service/observability-gateway` 拓扑与资产：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "infra.cmdb.query",
    "arguments": {
      "node_id": "service/observability-gateway"
    }
  }
}
```

#### 2. 安全读取 GitHub CLI 版本：
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "infra.cli.exec",
    "arguments": {
      "command": "gh",
      "args": ["--version"]
    }
  }
}
```

---

## 八、智能体与 IDE 客户端配置与实测验证矩阵

针对各类 Code Agent（**Trae**、**Cursor**、**Cherry Studio**、**Claude Desktop**、**Windsurf**）以及可观测性智能体（**观测云 Obsy Agent Teams**），建立端到端 MCP 接入与协议抓包实测矩阵。

### 8.1 客户端实测验证结论矩阵

| 配置组件 / 服务项 | 接入模式 | 实测结果 | 可用工具数 | 协议抓包与就绪状态说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Infrastructure-MCP-Server** | 本地 Command + Args / Wrapper | ✅ **通过** | **8 个工具** | 成功完成 `initialize` 与 `tools/list` 握手，稳定提供 `infra.cmdb.query`、`infra.cmdb.summary`、`infra.graph.query`、`infra.cli.exec` 等全量工具。 |
| **QMD MCP Server** | 本地 Wrapper 脚本 | ✅ **通过** | **23 个工具** | 握手通过，工具集全量暴露。**检索状态说明**：基于本地 PG 15432 已完整索引 193 篇白皮书并生效 **BM25 词法倒排全文检索**；当前未配置外部 Embedding API Key 故未建立稠密向量索引，后续注入模型 Key 后方可激活稠密向量检索。 |
| **可观测性 4-MCP 端点**<br>(Grafana / Metrics / Logs / Traces) | 远程 SSE | ⚡ **服务端已修复** | 30+ 工具 (Grafana) | **传输与网关加固就绪**：协议严格为 **`SSE`** 传输。服务端已在 [`playbooks PR #820`](https://github.com/ai-workspace-infra/playbooks/pull/820) 修复 `--base-path /mcp/v1/grafana` 前缀透传，消除标准客户端/Bot 的 302 阻断，并启用 `--disable-write` 与 `--disable-admin` 彻底封死写操作。建议在生产部署后进行凭据轮换再行挂载。 |

> [!IMPORTANT]
> **仅有 HTTP 200/302 不代表 MCP 配置可用**。必须返回合法的 JSON-RPC 2.0 / SSE 协议流。各客户端当前应仅挂载已 100% 验证通过的本地 Infrastructure 与 QMD 两个服务。

### 8.2 单服务配置规范（Trae / Cherry Studio 避坑）

在各类国内与国际 IDE（如 **Trae**、**Cherry Studio**）的“添加/编辑单个 MCP 服务”弹窗中：
1. **必须包含 `"mcpServers"` 根节点**，否则触发校验报错：`当前 JSON 配置中没有解析到 MCP 服务项`；
2. **单次仅支持编辑单个服务卡片**，若在弹窗中同时输入包含 2 个服务的 JSON，底层会拦截并报错：`该配置被识别为多配置项`。必须分别添加、分别保存。

#### 1. Infrastructure 单服务标准配置（首选原生模式）
```json
{
  "mcpServers": {
    "infrastructure": {
      "args": [
        "-config",
        "/Users/shenlan/.config/infrastructure-mcp-server/config.json"
      ],
      "command": "/Users/shenlan/.local/bin/infrastructure-mcp-server"
    }
  }
}
```
*表单模式填写*：
* **类型 (Type)**：`STDIO`
* **命令 (Command)**：`/Users/shenlan/.local/bin/infrastructure-mcp-server`
* **参数 (Args)**：
  * `-config`
  * `/Users/shenlan/.config/infrastructure-mcp-server/config.json`
* **环境变量 (Env)**：留空

> 💡 *备选 0 参数 Wrapper 模式*：`"command": "/Users/shenlan/.local/bin/run-infrastructure-mcp.sh"`

#### 2. QMD 单服务标准配置（免参数 Wrapper 模式）
```json
{
  "mcpServers": {
    "qmd": {
      "command": "/Users/shenlan/.local/bin/run-qmd-mcp.sh"
    }
  }
}
```

### 8.3 即刻可用推荐组合（已实测验证通过）

```json
{
  "mcpServers": {
    "infrastructure": {
      "args": [
        "-config",
        "/Users/shenlan/.config/infrastructure-mcp-server/config.json"
      ],
      "command": "/Users/shenlan/.local/bin/infrastructure-mcp-server"
    },
    "qmd": {
      "command": "/Users/shenlan/.local/bin/run-qmd-mcp.sh"
    }
  }
}
```

### 8.4 远程独立双域名全量推荐配置 (GitOps 交付就绪)

在云端 / 远程容器客户端中，推荐通过独立域名直接挂载两大 MCP 服务：

```json
{
  "mcpServers": {
    "infrastructure": {
      "type": "sse",
      "url": "https://mcp-server.svc.plus/sse"
    },
    "observability-grafana": {
      "type": "sse",
      "url": "https://mcp-server.svc.plus/v1/grafana/sse",
      "headers": {
        "Authorization": "Basic <vault-injected-base64-credentials>"
      }
    },
    "observability-metrics": {
      "url": "https://mcp-server.svc.plus/v1/metrics/mcp"
    },
    "observability-logs": {
      "url": "https://mcp-server.svc.plus/v1/logs/mcp"
    },
    "observability-traces": {
      "url": "https://mcp-server.svc.plus/v1/traces/mcp"
    }
  }
}
```

---

## 九、dev-k3s-v5 单独立域名网关收敛与 PROD MCP 下线体系

为避免域名泛滥并彻底规避 `prod-k3s-v5` 生产节点的资源竞争与权限风险，平台工程团队遵照用户指令完成架构收敛：
1. **单一独立域名收敛**：不再分配或使用 `mcp.svc.plus`，所有 MCP 服务统一收敛至单一独立域名 **`mcp-server.svc.plus`**（`/` 为基础设施网关，`/v1/grafana` 为只读 Grafana SSE 网关）。
2. **彻底下线 `prod-k3s-v5` 上遗留的 `observability-mcp` Pod**：针对 `platform-observability-mcp-victoriametrics-bddc8bddc-wzgh9` 等 Pod，在 GitOps `services/platform-observability/prod/retire-observability-mcp.yaml` 中显式声明 `replicas: 0`，由 FluxCD 自动完成缩容回收。
3. **部署集中在 `dev-k3s-v5` 节点**：所有控制面适配器统一部署在轻量级 `dev-k3s-v5`，上游数据面依然直连 `https://observability.svc.plus/`。

```mermaid
flowchart TD
    subgraph DevK3s ["dev-k3s-v5 节点 (Linode jp-tyo-3 2C4G)"]
        Ingress["Traefik Ingress Controller (dev-web-saas / dev-http01)"]
        
        subgraph NS ["Namespace: platform-mcp (Restricted PSA)"]
            InfraMCP["infrastructure-mcp-server:8080<br>路径: /<br>请求: 50m / 64Mi | 限制: 200m / 256Mi"]
            ObsyMCP["observability-mcp-gateway:8000<br>路径: /v1/grafana<br>请求: 50m / 64Mi | 限制: 200m / 256Mi"]
        end
    end

    subgraph CentralTelemetry ["集中式遥测集群 (observability.svc.plus)"]
        CaddyProxy["Caddy 反向代理网关"]
        VMCluster["VictoriaMetrics / Logs / Traces / Grafana"]
    end

    subgraph ProdK3sV5 ["prod-web-saas-k3s-v5 节点 (生产集群)"]
        RetiredPod["platform-observability-mcp-victoriametrics<br>(replicas: 0 / 下线停用)"]
    end

    Ingress -->|mcp-server.svc.plus /| InfraMCP
    Ingress -->|mcp-server.svc.plus /v1/grafana| ObsyMCP
    ObsyMCP -->|上游遥测查询数据流| CaddyProxy
    CaddyProxy --> VMCluster
```

### 9.1 单域名路由分流矩阵 (`mcp-server.svc.plus`)

| 路径匹配 | 目标 Service | 监听端口 | 承载组件 | 核心能力 | 上游数据源 |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **`/`** (Prefix) | `infrastructure-mcp-server` | `8080` | `infrastructure-mcp-server` | 多云 CMDB 对账、15 边依赖图拓扑、安全只读 CLI、QMD 记忆检索 | 下游聚合 `https://mcp-server.svc.plus/v1/...` 与本地/远程 QMD |
| **`/v1/grafana`** (Prefix) | `mcp-grafana` | `8000` | `observability-mcp-gateway` | Grafana SSE 仪表盘/告警检索 | **`https://observability.svc.plus/grafana/`** (集中式监控节点) |

### 9.2 2C4G 节点容量控制与安全红线

1. **资源配额**：
   - `dev-k3s-v5` 采用 Linode `g6-standard-2`（2 vCPU / 4096 MiB RAM）。
   - 两大 MCP 网关容器合计仅占用 **100m CPU Requests (5%)** 与 **128Mi RAM Requests (3.1%)**，预留 > 90% 资源给临时 SIT 特性测试泳道。
2. **只读安全红线**：
   - `mcp-grafana` 容器严格执行启动参数：`-t sse --base-path /v1/grafana --disable-write --disable-admin`。
   - Grafana Service Account 严格配置 `Viewer` 角色，严禁开启任何修改、创建数据源或删除快照工具。
3. **安全准入 (PSA)**：
   - 命名空间 `platform-mcp` 强制实施 `pod-security.kubernetes.io/enforce: restricted`。
   - 容器均运行于非 root 用户（`UID 65532`），挂载只读根文件系统（`readOnlyRootFilesystem: true`），完全丢弃全部内核权限（`capabilities.drop: [ALL]`）。

### 9.3 交付 PR 履历

* **Playbooks 仓库 (PR #820)**：修复 `mcp-grafana` SSE 传输协议、增加 `--base-path /mcp/v1/grafana`、增加 `--disable-write` 与 `--disable-admin` 只读安全红线。
* **Infrastructure-MCP-Server 仓库 (PR #8 & PR #9)**：增加原生 HTTP/SSE 协议引擎、`-listen` 与 `-base-path` 运行时参数、多阶段 Dockerfile、以及单域名 `mcp-server.svc.plus` 聚合拓扑。
* **GitOps 仓库 (PR #612 & PR #613)**：在 `dev-k3s-v5` 编排 `platform-mcp` 命名空间，收敛并入单一 `mcp-server.svc.plus` Ingress 规则，并在 `prod-k3s-v5`（`services/platform-observability/prod/retire-observability-mcp.yaml`）停用并缩容至 0 遗留的 `observability-mcp` 副本。

