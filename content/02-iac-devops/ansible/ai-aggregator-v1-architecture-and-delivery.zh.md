# 个人 AI 聚合服务 v1：架构、选型与实施交付契约

状态：v1 实施基线；默认 disabled，尚未完成真实节点部署、OAuth 登录或请求验收。
v1 公共入口只有 Caddy；Cloudflare Worker/Pages、Cloud Run、Bedrock、Vertex AI、Azure Foundry 均不在 v1 运行链路。

---

## 一、目标、调用链路与部署模式

### 1. 核心调用链路
```
 [ 客户端 (IDE / SDK / 终端工具) ]
           │
           │ HTTPS (:443) / IP 白名单 / 设备级 Key (sk-device-xxx)
           ▼
   [ Caddy 网关 (:443) ]
           │
           │ 127.0.0.1 内部转发 (API 直通 Bearer / Console 叠加 Basic Auth)
           ▼
  [ New API (:3000) ] ── (Token 校验 / 模型稳定映射 / 统一日志 / PostgreSQL 状态)
           │
           │ 私网 / WireGuard / 宿主 loopback (禁止公网直接暴露)
           ├── CPA Codex 逻辑 Channels (:8317/:8320) ── tmpfs 认证 ──► OpenAI / Codex 账号实例
           ├── CPA Claude Code 逻辑 Channel (:8318)   ── tmpfs 认证 ──► Anthropic / Claude 账号实例
           └── CPA Grok 逻辑 Channel (:8319)          ── tmpfs 认证 ──► xAI / Grok 账号实例

 [ Caddy direct.ai.* ] ──► LiteLLM (:4000) ──► 官方 OpenAI / Anthropic / xAI API
```

这里是两条并列的聚合承载链路：`New API → CPA` 面向订阅账号和 CLI/IDE
应用适配，`LiteLLM` 面向官方 API 的统一协议、模型路由和直连调用；LiteLLM
不作为 CPA 的前置代理，二者也不互相串联。客户端根据需要选择 `ai.*` 或
`direct.ai.*`，但两者都必须经过 Caddy 的 HTTPS、IP 白名单和独立 token 校验。

外部客户端只看到两个受控聚合入口之一（`https://ai.svc.plus` 或
`https://direct.ai.svc.plus`）和分发的业务 Key（`sk-client-xxxxxxxx`），完全不知道底层的
CPA 地址、CPA 内部通信 Key 以及具体的 OAuth Token。

### 3. 第三方客户端接入目标

v1 的完成定义包含“第三方客户端可配置接入”，而不仅是服务端进程启动：

| 客户端 | 推荐入口 | 北向协议 | 默认链路 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| Claude Code / Claude SDK | `https://ai.svc.plus` | Anthropic Messages (`/v1/messages`) | New API → CPA Claude | 使用独立 client token；不得把账号 OAuth 放到客户端 |
| Codex CLI / OpenAI SDK | `https://ai.svc.plus/v1` | OpenAI Responses / Chat | New API → CPA Codex | 使用 `codex-main` 稳定别名 |
| Android Studio Third-Party Remote Provider | `https://direct.ai.svc.plus/v1` | OpenAI-compatible Chat / Models | LiteLLM → 官方 API | 使用 `anthropic-api` 等已声明模型并刷新模型列表 |
| 其他 IDE / SDK / Web SaaS | `https://direct.ai.svc.plus/v1` 或 `https://ai.svc.plus/v1` | OpenAI-compatible | 按 client profile 选择并列承载链路 | 只发放设备或应用级 token |

Claude Code 的 gateway 配置使用 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_AUTH_TOKEN`，其中 token 由本机密钥链或 Vault helper 提供；不写入项目文件。Android Studio 的远程模型配置需要 HTTPS API endpoint、API key，并通过 `/v1/models` 刷新模型；因此 Caddy、模型列表和 Bearer token 校验都是 v1 验收项。详见 [Anthropic LLM gateway configuration](https://docs.anthropic.com/en/docs/claude-code/llm-gateway) 和 [Android Studio remote model](https://developer.android.com/studio/gemini/use-a-remote-model)。

GitOps 中的 `client_profiles` 是非敏感接入契约；实际 token 只使用对应的 `clients/<client-id>` Vault 路径。客户端接入前必须通过固定 IP 白名单，客户端配置不得包含 CPA 地址、OAuth token 或数据库凭据。

推荐接入方式：

```bash
# Claude Code：走 New API -> CPA Claude；值由本机密钥链 / Vault helper 注入
export ANTHROPIC_BASE_URL="https://ai.svc.plus"
export ANTHROPIC_AUTH_TOKEN="<从本机安全存储读取的 client token>"
claude

# OpenAI-compatible SDK / IDE：走 New API -> CPA Codex
export OPENAI_BASE_URL="https://ai.svc.plus/v1"
export OPENAI_API_KEY="<从本机安全存储读取的 client token>"
```

Android Studio 配置为 Tools → AI → Model Providers → Third-Party Remote Provider，URL 填
`https://direct.ai.svc.plus/v1`，API key 填 Android Studio 专用 client token，点击 Refresh
确认能看到 `anthropic-api`、`openai-api` 或 `xai-api` 等模型。Android Studio 的 Chat 与 AI Agent
是 v1 目标能力；依赖 Google/Gemini 特有协议的功能不作为 v1 兼容承诺。

### 2. 两种部署模式
- **模式一：独立部署 (Standalone)**
  - **适用场景**：全新独立节点或后续物理迁移。
  - **架构特征**：本项目直接管理 Caddy；绑定独立公网域名；管理 New API、LiteLLM、CPA 等全套 systemd 单元及 PostgreSQL 连接。
- **模式二：嵌入 AI Workspace (Embedded - v1 首选)**
  - **适用场景**：复用现有运行节点（如 `jp-xhttp-contabo.svc.plus`）。
  - **架构特征**：**复用宿主机已有的 Caddy 网关**，通过 `conf.d` 引入两个域名路由；New API 与 LiteLLM 在不同端口并行运行。New API→CPA 面向 AI App，LiteLLM 面向直接 AI API，互不串联。

两种模式统一由同一套 GitOps 拓扑模型与 Ansible Role 交付：
```yaml
spec:
  deployment_mode: embedded # 或 standalone
  entrypoint:
    domain: ai.svc.plus
    direct_api_domain: direct.ai.svc.plus
    reuse_existing_caddy: true
  upstream:
    app_gateway: new-api
    direct_api: litellm
```

---

## 二、纯技术选型对比：Sub2API vs CPA + New API

| 维度 | New API (独立) | Sub2API | CPA + New API (三件套) |
| :--- | :--- | :--- | :--- |
| **核心定位** | 通用 LLM API Gateway | 订阅账号池 + 垂直网关一体机 | 账号/OAuth 适配器 + 通用 API Gateway |
| **架构范式** | 单层网关 | **单体一体化** (All-in-One) | **分层解耦** (Adapter + Gateway) |
| **网络调用链路** | 客户端 → New API → 上游 | 客户端 → Sub2API → 上游 (少 1 跳) | 客户端 → New API → CPA → 上游 |
| **订阅账号池化** | ⭐⭐⭐ (依赖第三方适配) | ⭐⭐⭐⭐⭐ (原生设计核心) | ⭐⭐⭐⭐ (由 CPA 账号池承载) |
| **Sticky Session / 429 调度** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ (原生智能调度与熔断) | ⭐⭐⭐⭐ (依赖 CPA 内部策略) |
| **多 Provider / API 接入** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ (任意扩展 Adapter 与商用 API) |
| **模型协议完整度** | ⭐⭐⭐⭐⭐ (Chat/Responses/Messages) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ (完整保留上游协议特性) |
| **运维与故障定位** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ (单组件极简) | ⭐⭐⭐ (分层排查，需厘清各层边界) |
| **长期演进弹性** | ⭐⭐⭐⭐ | ⭐⭐⭐ (强耦合订阅池逻辑) | ⭐⭐⭐⭐⭐ (随时平滑替换 CPA 或接入外部 API) |

### 选型裁决依据
1. **个人 / 小团队自用订阅资源整合**: **Sub2API > CPA + New API**。Domain Model 高度契合，链路更短，部署运维开销极小。
2. **长期演化 / 多来源统一 AI 基础设施**: **CPA + New API > Sub2API**。Adapter（CPA）与 Gateway（New API）清晰解耦，后续可无缝接入自建模型、外部正规商用 API 或更换适配器。
3. **纯商用 API Key 汇聚与转售**: **New API 单独使用**，无需引入 CPA 或 Sub2API。

---

## 三、资源预算与测试环境硬约束 (Spot t4g 1h)

### 1. 测试与验证阶段硬约束 (AWS Spot t4g 1h)
> [!IMPORTANT]
> **测试阶段统一计算规格：AWS Spot t4g.medium (ARM64) 1小时生命周期实例！**
> - **实例类型**：`t4g.small` (2 vCPU / 2 GiB) 或 `t4g.medium` (2 vCPU / 4 GiB ARM64)。
> - **竞价模式**：`spot_instance: true`（one-time 临时竞价实例）。
> - **硬性生命周期限制**：`max_runtime_minutes: 60`。实例启动时通过 `user_data` 注入到期自动关机脚本（`sleep 3600 && /sbin/shutdown -h now`），结合 AWS `instance_initiated_shutdown_behavior: terminate` 实现物理自动销毁，坚决杜绝因人工遗忘产生的闲置计费。
> - **架构构建要求**：所有构建物料（New API 二进制、CPA 二进制）必须提供 Linux `arm64` 原生二进制及对应 SHA-256 校验和。

### 2. 生产与长效运行容量规划
| 组件 | CPU 预留 | 内存预留 | 磁盘占用 | 关键说明 |
| :--- | :--- | :--- | :--- | :--- |
| **Caddy** | 0.1–0.3 核 | 30–80 MB | 极少 | 仅做 TLS、IP 白名单与反向代理，开销极低 |
| **New API** | 0.5–1 核 | 150–400 MB | 1–5 GB | PostgreSQL 状态库，数据库连接从 Vault 注入 |
| **LiteLLM** | 0.5–1 核 | 200–600 MB | 1–5 GB | 直接聚合 OpenAI/Anthropic/xAI API，数据库独立 |
| **单个 CPA 实例** | 0.3–1 核 | 100–300 MB | 100–500 MB | 纯协议适配层开销轻量，OAuth 状态暂存 |
| **CodeAgent CLI** | 0.5–2 核 | 200–800 MB | 1–5 GB (缓存) | 运行时主要资源消耗者（依赖解析、代码索引、缓存） |
| **系统与日志余量**| 1 核 | 1–2 GB | 5–10 GB | 保障 OS 稳定、监控探针与轮转日志安全 |

- **最低可运行配置 (2 vCPU / 4 GB RAM / 40 GB SSD)**: 承载 Caddy + New API + 1 个 CPA 实例。
- **推荐 Gateway 配置 (4 vCPU / 8 GB RAM / 80 GB SSD)**: 承载 Caddy + New API + LiteLLM。
- **每个 CPA 节点建议 (2 vCPU / 2–4 GB RAM / 40 GB SSD)**: 承载一个 CPA + 一个 CodeAgent CLI 账号实例。
- **多实例横向扩展规则**: 每增加 1 个 CPA + CLI 实例，追加预留 `+1 vCPU`、`+512 MB 至 1 GB RAM`、`+5 GB SSD`。

---

## 四、网络收敛与边界加固规范

### 1. 宿主机网络边界收敛
宿主机执行 `ss -lntp`，**理想状态仅允许**：
- `0.0.0.0:22` (SSH 受控运维端口)
- `0.0.0.0:443` (Caddy HTTPS 唯一对外入口)
- **严禁外部监听**：`0.0.0.0:3000` (New API) ❌, `0.0.0.0:8317-8319` (CPA) ❌。必须严格绑定 `127.0.0.1` 或加密私网。

### 2. Caddy 双域名与双层认证防御
- **API 路径 (`/v1/*`, `/v1beta/*`)**:
  - 反向代理至 New API `:3000`，由 New API 严格校验客户端 Bearer Token。
- **直接 API 域名 (`direct.ai.*`)**:
  - `/v1/*` 反向代理至 LiteLLM `:4000`，由 LiteLLM 校验 direct API key。
- **管理控制台 (`/`, `/console/*`)**:
  - 在 Caddy 层叠加 **Basic Auth**，然后再反代至 New API 后台，形成 **Caddy Basic Auth + New API Admin Login** 双层防护。
  - Caddy 使用物理连接源 IP 判定白名单；客户端自报 `X-Forwarded-For` 无效。空白名单部署直接阻断。

### 3. CPA Management API 彻底关闭
- CPA 默认暴露的 `/v0/management` 必须在配置文件中彻底禁用公网访问：
  ```yaml
  remote-management:
    allow-remote: false
    secret-key: "" # 为空且不设密码，关闭公开管理接口
  ```
- 账号维护与 OAuth 登录必须通过 SSH 登录节点或临时端口映射执行。

---

## 五、多账号池与路由治理最佳实践

### 1. 单层调度原则（收敛于 CPA）
- 每个 CPA 实例严格绑定一个账号；多个 CPA 实例通过 New API 的多个同类 channel 实现横向扩展。
- New API 不把 LiteLLM 放在 CPA 前面；直接 API 请求走独立 LiteLLM 域名。
- Codex 使用 `8317/8320`，Claude 使用 `8318`，Grok 使用 `8319`；远端地址由 CMDB 私网事实注入。

### 2. 模型稳定别名抽象 (Model Mapping)
- 客户端绝不直连具体服务商底层模型名，而是在 New API 建立稳定别名映射：
  - `codex-main` ──► 映射为底层最新的 GPT/Codex 模型
  - `claude-main` ──► 映射为底层最新的 Claude 3.7 Sonnet
  - `grok-main` ──► 映射为底层最新的 Grok 模型
- 上游模型升级迭代时，仅需在 New API / CPA 修改映射表，所有客户端与 IDE 零改造。

### 3. 原生协议全量保留
- **拒绝强行将所有请求压缩为 `/v1/chat/completions`**:
  - 保留 `/v1/responses`：满足 OpenAI/Codex 原生推理、thinking 过程与高级工具调用。
  - 保留 `/v1/messages`：满足 Claude 原生上下文协议与客户端最佳体验。
  - 保留 `/v1/models`：供客户端自动发现能力。

### 4. 设备级 API Key 隔离
- 严禁全局共用单一 Master Key。按客户端与设备独立派发专属 Key（`sk-macbook-xxx`, `sk-desktop-xxx`），单设备密钥泄露时可在 New API 秒级单独吊销。

---

## 六、账号矩阵与 Vault 凭据平面

### 1. 账号矩阵（非敏感声明）
| 实例 ID | 平台 / 账号别名 | node_ref | 本机端口 | 数据库记录 |
| :--- | :--- | :--- | :--- | :--- |
| `cpa-codex-01` | OpenAI / Codex CLI（账号邮箱见 GitOps） | UAT: `cpa-codex-01`；Prod: `tky-proxy.svc.plus` | 8317 | `ai_aggregator_accounts` + `ai_aggregator_instances` |
| `cpa-codex-02` | OpenAI / Codex CLI（账号邮箱见 GitOps） | UAT: `cpa-codex-02`；Prod: `tky-proxy.svc.plus` | 8320 | `ai_aggregator_accounts` + `ai_aggregator_instances` |
| `cpa-claude-01` | Anthropic / Claude Code（账号邮箱见 GitOps） | UAT: `cpa-claude-01`；Prod: `tky-proxy.svc.plus` | 8318 | `ai_aggregator_accounts` + `ai_aggregator_instances` |
| `cpa-grok-01` | xAI / Grok CLI（账号邮箱见 GitOps） | UAT: `cpa-grok-01`；Prod: `tky-proxy.svc.plus` | 8319 | `ai_aggregator_accounts` + `ai_aggregator_instances` |

- 严格遵循 **1:1:1:1 隔离模型**：1 个 CPA 实例 绑定 1 个 Provider 账号 对应 1 个独立 Unix 用户 对应 1 个独立 Vault Secret。

### 2. Vault KV v2 路径与内容规范
Vault API: `https://vault.svc.plus` (KV v2 挂载于 `kv/data/...`)

- `kv/<env>/ai-aggregator/database`: `new_api_dsn`, `litellm_dsn`, `backup_credentials`。
- `kv/<env>/ai-aggregator/gateway/new-api`: `session_secret`, `crypto_secret`, `bootstrap_admin_password`, `api_client_token`。
- `kv/<env>/ai-aggregator/gateway/litellm`: `master_key`, `proxy_secret`。
- `kv/<env>/ai-aggregator/gateway/caddy`: `admin_password_hash`。
- `kv/<env>/ai-aggregator/litellm/providers/<provider>`: `api_key`（仅 `openai`、`anthropic`、`xai`）。
- `kv/<env>/ai-aggregator/gateway/cpa/<id>`: 仅保存 `oauth_bundle` 与 `channel_token`；这是 CPA 运行所必需的最小敏感材料。
- `kv/<env>/ai-aggregator/clients/<client-id>`: `client_token`（外部客户端接入 Token）。

`accounts/<id>` 与 `instances/<id>` 是 PostgreSQL 中的逻辑记录，不是 Vault KV 路径。数据库保存账号邮箱、Provider、CLI、节点、端口、状态、模型映射和 Vault 引用；不保存 OAuth token、API key、session secret 或 channel token 明文。上述 Secret 值只允许存在 Vault 和运行时 tmpfs，不得写入 Git、文档、Terraform state、CI artifact、Ansible facts 或 systemd unit。

建议最小数据库记录：

- `ai_aggregator_accounts(id, provider, cli, account_email, status, vault_auth_ref)`。
- `ai_aggregator_instances(id, account_id, node_ref, bind_address, port, vault_channel_ref, status)`。
- `ai_aggregator_instances` 与 `ai_aggregator_accounts` 为一对一绑定；一个账号不得同时绑定多个活动 CPA 实例。

### 3. 凭据隔离与单写者 CAS 约束
1. **最小权限**: 每个 CPA 实例专属身份只能读取属于其 `gateway/cpa/<id>` 的路径，禁止通配读取全部账号；数据库账号只允许访问 AI Aggregator schema。
2. **运行时存储**: 凭据落地仅允许在 `/run/ai-aggregator/` 等受限 `tmpfs` 内存文件系统中暂存，文件属主 `ai-aggregator`，权限 `0700`；严禁落盘持久盘，检查 core dump 与 swap 避免泄露。
3. **OAuth 刷新单写者**:
   - Vault Agent **不负责**刷新 Provider OAuth。
   - 由 CPA / 独立同步器与提供方握手刷新，并采用 Vault KV CAS (Check-And-Set) 写回新版本。
   - 若发生 CAS 冲突或 Vault 异常，立即告警并冻结，防止以旧覆盖新。
   - 同一 Provider 账号严禁在两个节点同时激活。
4. **New API 数据库审计**: 审计锁定 fork 是否明文保存 key，不盲目宣称零明文持久化。

---

## 七、四仓库协作与流水线闭环 (Delivery Pipeline)

### 1. 仓库职责与事实源
| 仓库 | 关键路径 | 核心职责 |
| :--- | :--- | :--- |
| **knowledge** | `content/02-iac-devops/ansible/ai-aggregator-v1-architecture-and-delivery.zh.md` | 架构决策记录 (ADR) 与运行手册事实源 |
| **gitops** | `topology/<env>/selfhost/ai-aggregator.yaml` | 非敏感期望状态（默认 `enabled: false`，空白名单防误跑） |
| **playbooks** | `deploy-ai-aggregator-v1.yml` / `roles/vhosts/ai_aggregator_v1` | Ansible 幂等对账、systemd/Caddy 模板渲染与前置检查 |
| **platform-ops-toolkit** | `.github/workflows/ai-aggregator-v1.yml`, `validate_ai_aggregator_manifest.py` | 静态检查、OIDC 换权、端到端验证与切流编排 |

### 2. 交付生命周期阶段
```
[ 1. PR 静态校验 ] ──► [ 2. Plan ] ──► [ 3. Preflight 资源探针 ] ──► [ 4. Build 制品校验 ]
        │
        ▼
[ 5. Stage 无密钥渲染 ] ──► [ 6. Bootstrap 临时认证注入 ] ──► [ 7. Activate 服务启动 ]
        │
        ▼
[ 8. Verify 端到端验收 ] ──► [ 9. Cutover 流量切换 ] ──► [ 10. Rollback 回滚预案 ]
```

- **Stage 阶段防呆**: GitOps 未启用 (`enabled: false`)、IP 白名单为空、制品缺少 SHA-256 校验和、或 New API 启动命令未固定 loopback 时，Stage 必须直接阻断。
- **Activate 顺序**: Vault 凭据注入 tmpfs 就绪 ──► CPA 实例启动并健康 ──► New API 启动并绑定 127.0.0.1 ──► Caddy validate 检查通过并 reload。

### 3. GitOps 如何声明和使用资源

`spec.infrastructure` 是环境资源使用契约，服务声明与资源声明分离：

| 环境 | GitOps provider / provisioner | 资源来源 | 生命周期 | 下游使用 |
| :--- | :--- | :--- | :--- | :--- |
| UAT | `aws` / `terraform` | `iac_modules/terraform-hcl-standard/aws-cloud/config/resources/uat/ai-aggregator.yaml` | AWS ARM64 Spot，60 分钟 | Terraform 输出 `cmdb_runtime`，渲染 inventory，Ansible 连接并部署 |
| Prod | `existing` / `ansible` | 现有 CMDB/inventory 与持久 vhost/CPA 节点 | 持久，由 Terraform 排除 | Ansible 按 `inventory_host` 对账，不创建、不替换、不销毁节点 |

UAT 每个 `nodes[].resource_ref` 对应资源 contract 中的一个显式 host；流水线读取
`resource_contract.path`，渲染 Terraform，再把私网地址等非敏感输出写入临时 CMDB/inventory。
Prod 的 `resource_ref` 指向现有 CMDB 节点，GitOps 只声明角色、绑定和服务配置，不接管节点生命周期。
Vultr/GCP contract 只作为后续 provider adapter 的声明入口，v1 不自动应用。

---

## 八、验收矩阵与排障清单 (Acceptance Checklist)

| 验证项 | 成功条件 | 检查方法 |
| :--- | :--- | :--- |
| **静态校验** | YAML/schema、Ansible syntax、模板渲染、systemd/Caddy 配置检查通过 | Toolkit 校验脚本 & `ansible-playbook --syntax-check` |
| **网络边界** | 公网直接访问 `:3000` (New API) 或 `:8317-8319` (CPA) 超时或拒绝；宿主机仅监听 22/80/443 | `ss -lntp` 检查监听地址 |
| **IP 白名单** | 非白名单 IP 访问 Caddy `:443` 返回 `403 Forbidden`；伪造 `X-Forwarded-For` 头无效 | curl 模拟非白名单 IP 测试 |
| **双层防御** | 访问后台控制台触发 Caddy Basic Auth；通过后方可进入 New API 登录页 | 浏览器访问 `/console` 或 `/` |
| **Token 鉴权** | 白名单内 IP 缺少或使用错误 Bearer Token 时返回 `401 Unauthorized`；有效 Token 正常响应 | curl 带/不带 Bearer 验证 |
| **模型与协议** | `/v1/models` 返回与 GitOps 声明一致；`/v1/responses` 与 `/v1/messages` SSE 流式交互与 Tool Calling 正常 | 真实流式客户端交互测试 |
| **第三方客户端** | Claude Code 能完成一次 Messages 请求；Android Studio 能刷新 `/v1/models` 并完成 Chat/Agent 请求；OpenAI-compatible SDK 能完成 Chat/Responses 请求 | 使用对应 `client_profiles` 与独立 client token 验证 |
| **单层调度** | 多次并发请求，CPA 内部多账号正常轮询，New API 仅感知单一 Channel，日志无调度冲突报错 | 查看 New API 渠道日志 |
| **故障隔离** | 模拟单个 CPA 进程停止 (`systemctl stop cliproxyapi-cpa-codex-01.service`)，仅该模型 Channel 返回不可用，其余 CPA 和 LiteLLM 链路正常 | systemd 进程停止实验 |
| **凭据持久化** | 检查持久盘 `/var/lib`、systemd unit、环境文件及日志，确认不存在任何明文 Token / OAuth 凭据 | 磁盘与文件 grep 扫描 |
| **一键回滚** | 触发回滚指令后，客户端流量迅速切回原 LiteLLM 链路，版本和数据状态保持一致 | 验证客户端 fallback 到 LiteLLM |

---

## 九、备份与待实施状态

1. **数据库备份**: New API 与 LiteLLM 使用独立 PostgreSQL 数据库和用户；升级前分别执行一致性备份，备份流直接加密并通过 Vault 中的备份凭据写入受控存储，严禁生成明文 SQL dump。
2. **OAuth 凭据备份**: 由 Vault 内建版本机制及 Vault 灾备系统保护，禁止打包运行时 tmpfs auth 目录。
3. **当前落地状态**:
   - 已落地：四仓库的 v1 文档、GitOps UAT/Prod 声明、Ansible systemd/Caddy/Vault 注入角色、AWS Spot 渲染 contract、AWS/Vultr/GCP provider contract、manifest 校验器与 UAT 流水线骨架。
   - 待实施：提交并合并各仓库变更、配置 GitHub OIDC/Vault role 与 AWS role、填入固定 SSH/API 白名单、锁定并发布 New API/CPA/LiteLLM 制品、真实节点部署、OAuth 人工登录、New API channel 建立和完整 smoke test。

---

## 十、后续云原生与 Serverless 演进（非 v1 运行链路）

本节只记录后续演进选项。Cloudflare Worker/Pages、GCP Cloud Run、Supabase 不属于 v1 部署路径，不能替换 v1 的 Caddy、宿主持久进程或 PostgreSQL 运行约束。

当聚合服务从单节点 VPS 进一步演进时，核心原则为：**非 CPA 节点全量上 Serverless 云原生，CPA 节点保持独立 VPS 账号执行层**。

### 1. 现代化分工拓扑
```
                                     [ 用户终端 (IDE / Web / 开发者) ]
                                                    │
                                                    │ HTTPS
                                                    ▼
                     ┌─────────────────────────────────────────────────────────────┐
                     │                 Cloudflare 边缘托管层                       │
                     │  - Cloudflare Pages: 托管 "Token 配额分析" 前端 Web 控制台     │
                     │  - Cloudflare Workers: 边缘 API 网关、Key 预检、缓存、速率限制  │
                     └──────────────────────────────┬──────────────────────────────┘
                                                    │ mTLS / 内部签名
                                                    ▼
                     ┌─────────────────────────────────────────────────────────────┐
                     │              GCP Cloud Run (Serverless Gateway)             │
                     │  - 运行 New API (容器化)，支持自动缩容至 0 (Scale to zero)   │
                     │  - 模型稳定别名映射 (codex-main, claude-main, grok-main)    │
                     │  - 协议原生转发 (/v1/responses, /v1/messages, /v1/chat)     │
                     │  - 凭据集成：GCP Secret Manager / Vault                    │
                     └───────────────┬─────────────────────────────┬───────────────┘
                                     │                             │
                                     │ PostgreSQL 连接池            │ WireGuard / 加密私网隧道
                                     ▼                             ▼
   ┌───────────────────────────────────────────────┐     ┌─────────────────────────────────────┐
   │         Supabase Cloud (Free Tier)            │     │          VPS 专属执行节点 (CPA)      │
   │  - 托管 PostgreSQL 数据库 (替代本地 SQLite)      │     │  - 必须常驻 VPS (账号执行层)         │
   │  - Token 配额、7 天滚动用量、缓存命中时序分析     │     │  - 1:1:1:1 账号隔离 (单实例单账号)   │
   │  - Row Level Security (RLS) & REST API        │     │  - tmpfs 认证注入 + Vault CAS 刷新  │
   │  - 为 Cloudflare Pages 前端直接提供用量查询   │     │  - CPA 仅内网绑定，对外零暴露        │
   └───────────────────────────────────────────────┘     └─────────────────────────────────────┘
```

### 2. 核心组件定位与优势
1. **前端展示：Cloudflare Pages**
   - 托管类似截图风格的“Token 配额分析”交互式控制台（单页静态应用 SPA）。
   - 全球边缘 CDN 分发，秒级加载，完全免疫网络攻击，零服务器运维。
2. **边缘调度与防护：Cloudflare Workers**
   - 负责统一入口鉴权与请求转发。
   - 客户端 API Key 格式预校验、防刷限流（Rate Limiting）及 CORS 自动化处理。
3. **核心网关层：GCP Cloud Run**
   - 容器化运行 New API，取代在 VPS 手工常驻进程。
   - 自动弹性扩缩容（具备 Scale-to-Zero 能力），夜间无请求时零计费。
   - 原生集成 Google Secret Manager，开箱即用高可用 HTTPS 终端。
4. **统一状态与数据库：Supabase Cloud (Free Tier)**
   - 免费提供 500MB 托管 PostgreSQL 与连接池（PgBouncer），解决本地 SQLite 无法多实例共享与容易写锁的问题。
   - 提供内置 RLS（行级安全）与自动生成的 REST API，前端控制台可直连 Supabase 安全拉取 Token 用量报表与图表数据。
5. **账号执行层：保留独立 VPS / Spot 实例上的 CPA**
   - 上游 Provider（OpenAI/Claude/Grok）的 OAuth 登录、刷新握手和 CLI 进程必须维持原生网络和持久化进程。
   - 专心充当纯粹的私网上游 Adapter，对公网完全不可见。

---

## 十一、v1 事实模型与后续演进边界

以下云原生拓扑仅作为未来拆分参考；v1 的事实拓扑仍是“Caddy → New API → CPA”与“Caddy → LiteLLM”，且 Caddy 是唯一公网 HTTPS 入口。

AI 聚合服务体系确立了“凭据平面（Vault）”与“声明平面（GitOps）”严格解耦的两平面原则，同时在运行时建立“边缘调度路由引擎”与“账号执行引擎”的双引擎映射。

### 1. 总体架构拓扑图
```
                                     [ 用户终端 (IDE / Web / 开发者) ]
                                                    │
                                                    │ HTTPS: https://ai.svc.plus
                                                    ▼
                     ┌─────────────────────────────────────────────────────────────┐
                     │                 Cloudflare 边缘分流引擎                     │
                     │  - Cloudflare Pages: 托管 "Token 配额分析" 前端 Web 控制台     │
                     │  - Cloudflare Workers: 边缘 API 网关、Key 预检、缓存、速率限制  │
                     └──────────────────────────────┬──────────────────────────────┘
                                                    │ mTLS / 内部签名
                                                    ▼
                     ┌─────────────────────────────────────────────────────────────┐
                     │              GCP Cloud Run (Serverless Gateway)             │
                     │  - 运行 New API (容器化)，支持自动缩容至 0 (Scale to zero)   │
                     │  - 模型稳定别名映射 (codex-main, claude-main, grok-main)    │
                     │  - 协议原生转发 (/v1/responses, /v1/messages, /v1/chat)     │
                     │  - 凭据集成：GCP Secret Manager / Vault                    │
                     └───────────────┬─────────────────────────────┬───────────────┘
                                     │                             │
                                     │ PostgreSQL 连接池            │ WireGuard / 加密私网隧道
                                     ▼                             ▼
   ┌───────────────────────────────────────────────┐     ┌─────────────────────────────────────┐
   │         Supabase Cloud (Free Tier)            │     │       VPS 账号执行引擎 (CPA)         │
   │  - 托管 PostgreSQL 数据库 (替代本地 SQLite)      │     │  - 必须常驻 VPS (账号执行层)         │
   │  - Token 配额、7 天滚动用量、缓存命中时序分析     │     │  - 1:1:1:1 账号隔离 (单实例单账号)   │
   │  - Row Level Security (RLS) & REST API        │     │  - tmpfs 认证注入 + Vault CAS 刷新  │
   │  - 为 Cloudflare Pages 前端直接提供用量查询   │     │  - CPA 仅内网绑定，对外零暴露        │
   └───────────────────────────────────────────────┘     └─────────────────────────────────────┘
```

### 2. 两平面职责矩阵
| 平面 | 承载仓库 / 基础设施 | 核心职责 | 绝对安全红线 |
| :--- | :--- | :--- | :--- |
| **声明平面**<br>(Declarative GitOps Plane) | `gitops/` 仓库 | 声明期望拓扑状态、节点引用 (`node_ref`)、监听端口、模型稳定映射、域名路由规则、制品校验和 | **严禁任何 Token、密码、OAuth bundle、私钥进入 Git！** 即使是 UAT 测试环境也不例外。 |
| **凭据平面**<br>(Credential Vault Plane) | `https://vault.svc.plus`<br>(KV v2 Engine) | 托管所有 Provider 原生 OAuth JSON、内部通讯 Bearer Token、数据库连接串、客户端 Key | **单写者 CAS 回写、仅在 `/run` tmpfs 内存中暂存、模式 0700**；严禁多实例共享凭据目录。 |

### 3. 双引擎映射与数据流
- **引擎一：边缘调度路由引擎 (Edge Routing Engine)**
  - 由 **Cloudflare Pages + Cloudflare Workers + GCP Cloud Run / VPS Caddy** 构成。
  - 职责：处理域名绑定（`ai.svc.plus`）、静态前端资产分发、客户端 API Key 格式校验、速率限制、防刷防御与模型别名路由。
  - 数据流向：客户端请求到达边缘后，Worker 将 API 流量无损送达 New API，同时前台静态看板通过只读匿名 Key 直连 Supabase 获取可视化时序图表。
- **引擎二：账号适配执行引擎 (Account Execution Engine)**
  - 由 **VPS 上的 CLIProxyAPI (CPA) 实例群 + CodeAgent CLI** 构成。
  - 职责：作为 OpenAI/Codex、Anthropic/Claude、xAI/Grok 的底层协议适配器与账号池管理器。
  - 数据流向：CPA 从受控 tmpfs 读取账号凭据，与上游模型供应商握手；Token 刷新时自动触发单写者 CAS 写回 Vault，完全隐藏在私网中，不对公网开放任何管理入口。

---

## 十二、实施闭环与当前状态

交付顺序固定为：

1. 先提交 knowledge、GitOps、playbooks、Terraform contract 和 toolkit 的文档/配置变更。
2. PR 阶段执行 YAML、Vault 引用、CPA 矩阵、Terraform、Ansible、Caddy 模板和 secret scan。
3. 合并后仅在显式开启 `AI_AGGREGATOR_UAT_ENABLED=true` 且已配置 AWS/Vault/OIDC 变量时自动创建 AWS ARM64 Spot UAT。
4. UAT 使用本地 Terraform state，流水线结束或失败时执行 destroy；实例自身在 60 分钟内自动关机并终止。
5. CPA OAuth 必须人工登录；完成后人工确认 Vault 写回、New API channel、协议 smoke test，再启用 provider。
6. Prod 只允许受保护环境手动触发 Ansible，复用既有持久节点，不执行 Terraform 创建、替换或销毁。

当前本地实现状态：

- 已完成：四仓库的非敏感契约、systemd/Caddy/Vault 注入模板、CPA 一实例一账号矩阵、AWS Spot UAT contract、Vultr/GCP adapter contract、manifest validator 和流水线骨架。
- 尚未声称完成：远端 PR/CI 全绿、真实 UAT 创建、Vault role 配置、制品 SHA-256 锁定、私网连通、OAuth 登录、New API channel 初始化、协议和备份恢复验收。
- 发生失败时，先保留旧 Caddy 配置；回滚步骤为恢复上一版本模板与 channel 声明、执行 `caddy validate`、reload，必要时将入口切回原 LiteLLM upstream。
