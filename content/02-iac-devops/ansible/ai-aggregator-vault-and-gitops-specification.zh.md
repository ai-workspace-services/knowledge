# AI Aggregator：GitOps 声明路径与 Vault 凭据全景规格说明书

状态：正式规划规范基线 (Normative Baseline)  
适用环境：`uat`, `prod`  
统一入口域名：`ai.onwalk.net` (UAT) / `ai.svc.plus` (PROD)

---

## 目录
- [一、核心架构与两平面映射原则](#一定位与两平面映射原则)
- [二、域名 ai.svc.plus 流量拓扑与路由规则](#二域名-aisvcplus-流量拓扑与路由规则)
- [三、GitOps 声明路径全景（非敏感期望状态）](#三gitops-声明路径全景非敏感期望状态)
  - [1. 目录结构树](#1-目录结构树)
  - [2. 核心拓扑声明：topology/<env>/selfhost/ai-aggregator.yaml](#2-核心拓扑声明)
  - [3. Cloudflare 边缘路由：resources/svc.plus/<env>/cloudflare/ai-gateway-worker.yaml](#3-cloudflare-边缘路由声明)
  - [4. Supabase 数据库声明：resources/svc.plus/<env>/supabase/ai-aggregator-db.yaml](#4-supabase-数据库声明)
  - [5. Cloud Run 容器服务声明：services/ai-aggregator/cloudrun/service.yaml](#5-cloud-run-服务声明)
- [四、Vault KV v2 路径与凭据字段全景（敏感材料）](#四vault-kv-v2-路径与凭据字段全景敏感材料)
  - [1. Vault 目录树](#1-vault-目录树)
  - [2. 凭据字段规范详表](#2-凭据字段规范详表)
  - [3. Vault 访问策略 (ACL Policy) 示例](#3-vault-访问策略-acl-policy)
- [五、New API 部署位置可拔插切换机制 (VPS vs Cloud Run)](#五new-api-部署位置可拔插切换机制-vps-vs-cloud-run)
- [六、CPA + CodeAgent CLI 账号矩阵与生命周期 (1:1:1:1 隔离)](#六cpa--codeagent-cli-账号矩阵与生命周期-1111-隔离)
- [七、前端 Token 配额分析看板与 Supabase 直连数据流](#七前端-token-配额分析看板与-supabase-直连数据流)

---

## 一、定位与两平面映射原则

本系统由两个严格正交、互不妥协的平面组成：

> [!IMPORTANT]
> **绝对准则：账号矩阵元数据在 GitOps，认证材料在 Vault！**
> - **GitOps 平面**：只声明节点引用（`node_ref`）、组件角色、拓扑网络、监听端口、模型稳定别名与 Vault 逻辑引用别名。严禁任何 Token、密码、OAuth Bundle 或明文 Key 进入 Git。
> - **Vault 平面**：托管全部 OAuth 凭据、数据库连接口令、网关密钥、内部通讯 Token 及客户端业务 Key。单实例专属权限，内存 tmpfs 暂存，单写者 CAS 回写。

```
 [ 客户端 (IDE / SDK / Web) ]
           │
           │ HTTPS: https://ai.svc.plus
           ▼
 ┌─────────────────────────────────────────────────────────────────────────────────────────┐
 │                      Cloudflare 边缘分流层 (ai.svc.plus)                                  │
 │   - 路径 / 与 /dashboard*  ──► Cloudflare Pages (Token 配额分析看板 SPA)                │
 │   - 路径 /v1/*, /v1beta/*  ──► Cloudflare Worker (边缘 Key 预检、Rate Limit、路由分发)  │
 │   - 路径 /console/*        ──► 边缘 Basic Auth 防护 ──► 后台管理通道                      │
 └──────────────────────────────┬─────────────────────────────┬────────────────────────────┘
                                │                             │
                 (模式 A: Cloud Run 容器化)      (模式 B: 现有 VPS 嵌入 Caddy)
                                │                             │
                                ▼                             ▼
                ┌──────────────────────────────┐  ┌──────────────────────────────┐
                │ GCP Cloud Run (Serverless)   │  │ VPS: jp-xhttp-contabo:3000   │
                │   New API 容器 (Scale-to-Zero)│  │   New API (systemd loopback) │
                └───────────────┬──────────────┘  └──────────────┬───────────────┘
                                │                                │
                                ├────────────────────────────────┘
                                │
                                │ WireGuard 私网加密隧道 / 宿主 loopback
                                ▼
 ┌─────────────────────────────────────────────────────────────────────────────────────────┐
 │                     VPS 专属账号执行层 (CPA + CodeAgent CLI)                             │
 │   - 实例 codex-gpt-01   (:8317) ── tmpfs 认证注入 ──► OpenAI / Codex 账号                │
 │   - 实例 claude-code-01 (:8318) ── tmpfs 认证注入 ──► Anthropic / Claude 账号            │
 │   - 实例 grok-01        (:8319) ── tmpfs 认证注入 ──► xAI / Grok 账号                    │
 └─────────────────────────────────────────────────────────────────────────────────────────┘
                                ▲
                                │ 状态、配额与用量时序
 ┌──────────────────────────────┴──────────────────────────────────────────────────────────┐
 │                     Supabase Cloud (Free Tier Managed PostgreSQL)                       │
 │   - 承载 New API 用户、API Key、Token 额度、7天滚动消耗、模型用量分布、缓存命中统计         │
 │   - 通过 RLS + REST API 直接向 Cloudflare Pages 前端看板提供只读查询                     │
 └─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 二、域名分流与环境映射 (UAT: ai.onwalk.net / PROD: ai.svc.plus)

统一对外入口收敛至 `https://ai.svc.plus`，通过 Cloudflare 边缘 Worker 实现零信任智能分流：

| 匹配路径 | 命中规则 / 前置拦截 | 目标上游组件 | 承载能力 |
| :--- | :--- | :--- | :--- |
| **`/`**<br>**`/dashboard*`** | 静态资产直通，全球边缘 CDN 缓存 | **Cloudflare Pages** | “Token 配额分析”交互式仪表盘，展示 5h/7d 额度、缓存命中率、用量趋势柱状图 |
| **`/v1/chat/completions`**<br>**`/v1/responses`**<br>**`/v1/messages`**<br>**`/v1beta/*`** | 1. 提取 `Authorization: Bearer sk-xxx`<br>2. 边缘速率限制 (120 RPM)<br>3. 跨域 CORS 头注入 | **New API Gateway**<br>(GCP Cloud Run 或 VPS Caddy) | 核心 AI 协议通道。保留 OpenAI / Codex / Claude 原生协议特性，执行模型别名映射 |
| **`/console*`**<br>**`/admin*`** | **强制 Basic Auth 弹窗认证**<br>(不通过直接 401 拦截) | **New API Web 后台** | 避免管理后台直接暴露公网，形成双层防御 |
| **其他未匹配路径** | 默认拦截 | 阻断响应 `404 Not Found` | 收敛攻击面 |

---

## 三、GitOps 声明路径全景（非敏感期望状态）

### 1. 目录结构树
```text
gitops/
├── resources/
│   └── svc.plus/
│       ├── uat/
│       │   ├── cloudflare/
│       │   │   ├── ai-gateway-dns.yaml       # DNS CNAME 记录定义
│       │   │   └── ai-gateway-worker.yaml    # Cloudflare Worker 路由与 Pages 绑定
│       │   └── supabase/
│       │       └── ai-aggregator-db.yaml     # Supabase 项目与数据库连接规格
│       └── prod/
│           ├── cloudflare/...
│           └── supabase/...
├── topology/
│   ├── uat/
│   │   └── selfhost/
│   │       └── ai-aggregator.yaml            # 核心主拓扑：部署模式、节点矩阵、CPA 实例
│   └── prod/
│       └── selfhost/
│           └── ai-aggregator.yaml
└── services/
    └── ai-aggregator/
        └── cloudrun/
            └── service.yaml                  # 当 New API 切至 Cloud Run 时的容器配置
```

### 2. 核心拓扑声明
**文件路径**：`topology/uat/selfhost/ai-aggregator.yaml`
```yaml
apiVersion: gitops.svc.plus/v1alpha1
kind: PersonalAIAggregator
metadata:
  name: ai-aggregator
  environment: uat
spec:
  enabled: true
  entrypoint:
    domain: ai.svc.plus
    managed_by: cloudflare-worker # cloudflare-worker | caddy
    routing_profile: hybrid-serverless

  # 1. New API 部署位置可拔插声明 (embedded | cloudrun | standalone)
  new_api:
    deployment_target: embedded # 可一键切换为 cloudrun
    embedded_config:
      node_ref: jp-xhttp-contabo.svc.plus
      bind_address: 127.0.0.1
      port: 3000
    cloudrun_config:
      service_name: uat-ai-aggregator-gateway
      region: us-central1
      min_instances: 0          # 闲置自动缩容到 0
      max_instances: 2
      concurrency: 80           # 单容器 80 并发复用，优化 SSE 长连接成本
    database_backend: supabase  # 状态存储切换为 Supabase 托管 PostgreSQL

  # 2. CPA 账号执行层矩阵（严格 1:1:1:1 隔离）
  cpa_instances:
    - id: codex-gpt-01
      provider: openai
      cli: codex
      account_alias: codex-gpt-01
      node_ref: jp-xhttp-contabo.svc.plus
      bind_address: 127.0.0.1
      port: 8317
      auth_secret_ref: vault://kv/uat/ai-aggregator/accounts/codex-gpt-01#oauth_bundle
      channel_token_ref: vault://kv/uat/ai-aggregator/instances/codex-gpt-01#channel_token
      model_aliases:
        codex-main: gpt-5.x-codex
        codex-fast: gpt-5.x-mini

    - id: claude-code-01
      provider: anthropic
      cli: claude-code
      account_alias: claude-code-01
      node_ref: tky-proxy.svc.plus
      bind_address: 127.0.0.1
      port: 8318
      auth_secret_ref: vault://kv/uat/ai-aggregator/accounts/claude-code-01#oauth_bundle
      channel_token_ref: vault://kv/uat/ai-aggregator/instances/claude-code-01#channel_token
      model_aliases:
        claude-main: claude-3-7-sonnet
        claude-fast: claude-3-5-haiku

    - id: grok-01
      provider: xai
      cli: grok
      account_alias: grok-01
      node_ref: tky-proxy.svc.plus
      bind_address: 127.0.0.1
      port: 8319
      auth_secret_ref: vault://kv/uat/ai-aggregator/accounts/grok-01#oauth_bundle
      channel_token_ref: vault://kv/uat/ai-aggregator/instances/grok-01#channel_token
      model_aliases:
        grok-main: grok-3
```

### 3. Cloudflare 边缘路由声明
**文件路径**：`resources/svc.plus/uat/cloudflare/ai-gateway-worker.yaml`
```yaml
apiVersion: gitops.svc.plus/v1alpha1
kind: CloudflareGatewayRoute
metadata:
  name: ai-gateway-routes
  environment: uat
spec:
  domain: ai.svc.plus
  dns:
    proxied: true
    type: CNAME
    target: uat-gateway.svc.plus
  routes:
    - pattern: "ai.svc.plus/"
      target: cloudflare_pages
      pages_project: ai-quota-dashboard
    - pattern: "ai.svc.plus/dashboard*"
      target: cloudflare_pages
      pages_project: ai-quota-dashboard
    - pattern: "ai.svc.plus/v1/*"
      target: upstream_gateway
      rate_limit_rpm: 120
    - pattern: "ai.svc.plus/v1beta/*"
      target: upstream_gateway
    - pattern: "ai.svc.plus/console*"
      target: upstream_gateway
      require_basic_auth: true
```

### 4. Supabase 数据库声明
**文件路径**：`resources/svc.plus/uat/supabase/ai-aggregator-db.yaml`
```yaml
apiVersion: gitops.svc.plus/v1alpha1
kind: SupabaseProjectSpec
metadata:
  name: ai-aggregator-db
  environment: uat
spec:
  project_id: "qwerasdfzxcv"
  region: "us-east-1"
  features:
    pgbouncer_enabled: true
    rls_enabled: true
    auto_schema_migration: true
  credential_ref: vault://kv/uat/ai-aggregator/supabase/project_credentials
  db_connection_ref: vault://kv/uat/ai-aggregator/supabase/database_connection
```

### 5. Cloud Run 服务声明
**文件路径**：`services/ai-aggregator/cloudrun/service.yaml`
```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: uat-ai-aggregator-gateway
  namespace: default
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "2"
        run.googleapis.com/container-concurrency: "80"
        run.googleapis.com/cpu-throttling: "true" # 仅在请求期间计费
    spec:
      containers:
        - image: ai-workspace-lab/new-api:pinned-v1.0.0
          resources:
            limits:
              cpu: "1000m"
              memory: "512Mi"
          envFrom:
            - secretRef:
                name: new-api-runtime-secrets
```

---

## 四、Vault KV v2 路径与凭据字段全景（敏感材料）

Vault API: `https://vault.svc.plus`  
Mount Path: `kv/` (API 前缀 `kv/data/...`)

### 1. Vault 目录树
```text
kv/data/<env>/ai-aggregator/
├── cloudflare/
│   ├── api_token                   # Cloudflare 运维管理 Token
│   └── worker_secrets              # Worker 运行环境变量与密钥
├── supabase/
│   ├── project_credentials         # Supabase API URL 与 API Keys
│   └── database_connection         # PostgreSQL 数据库连接串与认证参数
├── gateway/                        # New API 网关核心运行凭据
│   ├── session_secret
│   ├── crypto_secret
│   ├── bootstrap_admin_password
│   └── master_client_token
├── accounts/                       # 各 Provider 上游账号原生凭据 (1:1:1:1 隔离)
│   ├── codex-gpt-01
│   ├── claude-code-01
│   └── grok-01
├── instances/                      # New API -> CPA 内部通信 Bearer 凭据
│   ├── codex-gpt-01
│   ├── claude-code-01
│   └── grok-01
└── clients/                        # 分设备派发的客户端 API Key
    ├── macbook-dev
    ├── desktop-workstation
    └── opencode-cli
```

### 2. 凭据字段规范详表

| 相对路径 | Key (字段名) | 敏感度 | 字段内容与使用方式 |
| :--- | :--- | :--- | :--- |
| **`cloudflare/api_token`** | `token`<br>`account_id` | 高 | 自动化发布 Worker 与 Pages 使用的 API Token |
| **`cloudflare/worker_secrets`** | `UPSTREAM_URL`<br>`SHARED_SECRET`<br>`BASIC_AUTH_HASH` | 高 | Worker 环境变量：后端 New API 地址；边缘签名校验 Key；控制台 Basic Auth 密码哈希 |
| **`supabase/project_credentials`** | `supabase_url`<br>`supabase_anon_key`<br>`supabase_service_key` | 极高 | `anon_key` 注入 Cloudflare Pages 前端拉取用量；`service_key` 供网关写入审计日志 |
| **`supabase/database_connection`** | `connection_string`<br>`direct_url`<br>`db_password` | 极高 | `postgresql://postgres:[pwd]@[host]:6543/postgres?pgbouncer=true`，New API 启动时连接数据库 |
| **`gateway/`** | `session_secret`<br>`crypto_secret`<br>`bootstrap_admin_password` | 极高 | 无论部署在 VPS 还是 Cloud Run，启动时注入内存环境变量 |
| **`accounts/<alias>`**<br>*(例: `accounts/codex-gpt-01`)* | `oauth_bundle`<br>`refresh_token`<br>`expires_at` | **最高** | Provider 原生完整 JSON 认证包；单写者 CAS 回写更新；严禁多实例共享 |
| **`instances/<id>`**<br>*(例: `instances/codex-gpt-01`)* | `channel_token` | 高 | New API 访问对应 CPA 本地端口（8317~8319）时必须携带的 Bearer 内部令牌 |
| **`clients/<device-id>`** | `api_key`<br>`allocated_quota` | 高 | 派发给开发终端的 `sk-device-xxxx`，在 New API 中绑定设备配额并支持单独吊销 |

### 3. Vault 访问策略 (ACL Policy)
按最小权限原则，节点与服务仅授权读取自身专属路径：

```hcl
# CPA 实例 codex-gpt-01 专属策略
path "kv/data/{{identity.entity.metadata.env}}/ai-aggregator/accounts/codex-gpt-01" {
  capabilities = ["read", "update"] # 允许 CAS 刷新写回
}

# New API 专属策略
path "kv/data/{{identity.entity.metadata.env}}/ai-aggregator/gateway" {
  capabilities = ["read"]
}
path "kv/data/{{identity.entity.metadata.env}}/ai-aggregator/supabase/*" {
  capabilities = ["read"]
}
path "kv/data/{{identity.entity.metadata.env}}/ai-aggregator/instances/*" {
  capabilities = ["read"]
}
```

---

## 五、New API 部署位置可拔插切换机制 (VPS vs Cloud Run)

系统支持两种部署形态，且通过 GitOps 声明即可秒级切换：

| 对比维度 | 模式 A：Embedded (VPS 主机) | 模式 B：Cloud Run (Serverless) |
| :--- | :--- | :--- |
| **GitOps 开关** | `deployment_target: embedded` | `deployment_target: cloudrun` |
| **网络监听** | 宿主机 `127.0.0.1:3000` (仅内部 loopback) | GCP 内部私有 Endpoint / 托管 HTTPS |
| **前端流量入口** | Cloudflare Worker ──► VPS Caddy (`:443`) | Cloudflare Worker ──► GCP Cloud Run |
| **状态数据库** | 本地 SQLite 或 Supabase PostgreSQL | **强制使用 Supabase 托管 PostgreSQL** |
| **长流式计费** | **$0 增量**（固定包月 VPS 算力，无长连接时长惩罚） | 依赖并发复用（`concurrency=80`），闲置缩容为 0 |
| **运维复杂度** | 需维护 systemd unit 与本地依赖 | 免操作系统运维，自动水平扩缩容 |

---

## 六、CPA + CodeAgent CLI 账号矩阵与生命周期 (1:1:1:1 隔离)

1. **1:1:1:1 物理与逻辑隔离**：
   - **1 个 CPA 实例** 严格对应 **1 个 Provider 账号** 对应 **1 个独立系统用户** 对应 **1 个独立 Vault Secret**。
   - 实例运行目录：`/run/ai-aggregator/cpa/<id>/auth`（基于受控 `tmpfs` 内存文件系统，模式 `0700`）。
2. **CAS 单写者刷新机制**：
   - Vault Agent 不刷新 Provider OAuth。
   - 实例本地刷新 Token 后，由守护进程通过 Vault KV CAS (`check-and-set`) 写回新版本。
   - CAS 版本冲突时立即报警，严禁以旧覆新；同一账号严禁多节点并发激活。

---

## 七、前端 Token 配额分析看板与 Supabase 直连数据流

针对类似截图风格的可视化前端仪表盘（[token_usage_dashboard.html](file:///Users/shenlan/.gemini/antigravity/brain/c2936dc3-490c-4bbb-950b-6b0c81c832e7/token_usage_dashboard.html)）：

1. **部署形态**：通过 **Cloudflare Pages** 托管静态 SPA 构建产物，绑定路由 `ai.svc.plus/` 与 `ai.svc.plus/dashboard*`。
2. **数据交互**：
   - 采用 Supabase 客户端直连模式（`@supabase/supabase-js`）。
   - 前端仅持有只读权限的 `supabase_anon_key`。
   - 在 Supabase PostgreSQL 中配置 Row Level Security (RLS) 策略，仅允许匿名客户端通过关联 Key 查询只读用量时序表（`token_usage_daily`、`model_distribution`、`cache_metrics`）。
3. **优势**：看板查询流量完全不穿透至后端 New API 或 CPA 节点，彻底保障核心执行层的算力纯净与安全。
