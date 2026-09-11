# 个人 AI 聚合服务 v1：架构、选型与实施交付契约

状态：设计基线；尚未完成节点部署、OAuth 登录或请求验收。配置中的节点与域名为候选，必须通过预检后启用。

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
  [ New API (:3000) ] ── (Token 校验 / 模型稳定映射 / 统一日志 / SQLite 状态)
           │
           │ 私网 / WireGuard / 宿主 loopback (禁止公网直接暴露)
           ├── CPA Codex 逻辑 Channel (:8317)       ── tmpfs 认证 ──► OpenAI / Codex 账号池 (A/B/C)
           ├── CPA Claude Code 逻辑 Channel (:8318) ── tmpfs 认证 ──► Anthropic / Claude 账号池 (A/B)
           └── CPA Grok 逻辑 Channel (:8319)        ── tmpfs 认证 ──► xAI / Grok 账号池 (A/B)
```

外部客户端永远只看到统一入口（例如 `https://ai.svc.plus`）和分发的业务 Key（`sk-newapi-xxxxxxxx`），完全不知道底层的 CPA 地址、CPA 内部通信 Key 以及具体的 OAuth Token。

### 2. 两种部署模式
- **模式一：独立部署 (Standalone)**
  - **适用场景**：全新独立节点或后续物理迁移。
  - **架构特征**：本项目直接管理 Caddy；绑定独立公网域名；管理 New API、CPA 等全套 systemd 单元及 SQLite 状态。
- **模式二：嵌入 AI Workspace (Embedded - v1 首选)**
  - **适用场景**：复用现有运行节点（如 `jp-xhttp-contabo.svc.plus`）。
  - **架构特征**：**复用宿主机已有的 Caddy 网关**，仅通过 `conf.d` 引入经过验证的路由片段；不修改或覆盖现有 LiteLLM 配置，New API 与 LiteLLM 在不同端口并行运行；LiteLLM 保留在客户端回退链路中，支持按客户端和模型平滑灰度切流。

两种模式统一由同一套 GitOps 拓扑模型与 Ansible Role 交付：
```yaml
spec:
  deployment_mode: embedded # 或 standalone
  entrypoint:
    domain: ai.svc.plus
    reuse_existing_caddy: true
  upstream:
    primary: new-api
    rollback: litellm
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
| **New API** | 0.5–1 核 | 150–400 MB | 1–5 GB (SQLite) | v1 单节点使用内置 SQLite，无需外置 DB |
| **单个 CPA 实例** | 0.3–1 核 | 100–300 MB | 100–500 MB | 纯协议适配层开销轻量，OAuth 状态暂存 |
| **CodeAgent CLI** | 0.5–2 核 | 200–800 MB | 1–5 GB (缓存) | 运行时主要资源消耗者（依赖解析、代码索引、缓存） |
| **系统与日志余量**| 1 核 | 1–2 GB | 5–10 GB | 保障 OS 稳定、监控探针与轮转日志安全 |

- **最低可运行配置 (2 vCPU / 4 GB RAM / 40 GB SSD)**: 承载 Caddy + New API + 1 个 CPA 实例。
- **推荐个人全能配置 (4 vCPU / 8 GB RAM / 80 GB SSD)**: 承载 Caddy + New API + 3 个 CPA 实例 (Codex + Claude Code + Grok)。
- **多实例横向扩展规则**: 每增加 1 个 CPA + CLI 实例，追加预留 `+1 vCPU`、`+512 MB 至 1 GB RAM`、`+5 GB SSD`。

---

## 四、网络收敛与边界加固规范

### 1. 宿主机网络边界收敛
宿主机执行 `ss -lntp`，**理想状态仅允许**：
- `0.0.0.0:22` (SSH 受控运维端口)
- `0.0.0.0:80` (HTTP 跳转)
- `0.0.0.0:443` (Caddy HTTPS 唯一对外入口)
- **严禁外部监听**：`0.0.0.0:3000` (New API) ❌, `0.0.0.0:8317-8319` (CPA) ❌。必须严格绑定 `127.0.0.1` 或加密私网。

### 2. Caddy 双层认证防御
- **API 路径 (`/v1/*`, `/v1beta/*`)**:
  - 反向代理至 New API `:3000`，由 New API 严格校验客户端 Bearer Token。
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
- CPA 原生支持 Codex/Claude/Grok 的多账号轮询与池化管理。
- **严禁**在 New API 中为每个底层账号建立独立 Channel（会导致两层调度器竞态冲突与重试风暴）。
- **正确规范**: 账号池由 CPA 全权管理；New API 仅建立 3 个逻辑 Channel（`CPA-Codex`, `CPA-Claude`, `CPA-Grok`），分别对应端口 8317, 8318, 8319。New API 日志按模型类别清晰可见，底层账号变更完全内聚于 CPA。

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
| 实例 ID | 平台 / 账号别名 | node_ref | 本机端口 | 账号 Vault 路径 |
| :--- | :--- | :--- | :--- | :--- |
| `codex-gpt-01` | openai/codex-gpt-01 | 待预检分配 (t4g.medium) | 8317 | `kv/<env>/ai-aggregator/accounts/codex-gpt-01` |
| `claude-code-01`| anthropic/claude-code-01 | 待预检分配 (t4g.medium) | 8318 | `kv/<env>/ai-aggregator/accounts/claude-code-01` |
| `grok-01` | xai/grok-01 | 待预检分配 (t4g.medium) | 8319 | `kv/<env>/ai-aggregator/accounts/grok-01` |

- 严格遵循 **1:1:1:1 隔离模型**：1 个 CPA 实例 绑定 1 个 Provider 账号 对应 1 个独立 Unix 用户 对应 1 个独立 Vault Secret。

### 2. Vault KV v2 路径与内容规范
Vault API: `https://vault.svc.plus` (KV v2 挂载于 `kv/data/...`)

- `kv/<env>/ai-aggregator/gateway`: `session_secret`, `crypto_secret`。
- `kv/<env>/ai-aggregator/accounts/<alias>`: `oauth_bundle`（完整、版本化认证 JSON 对象），`refresh_token`。
- `kv/<env>/ai-aggregator/instances/<id>`: `channel_token`（New API -> CPA 专用的内部通讯凭据）。
- `kv/<env>/ai-aggregator/clients/<client-id>`: `client_token`（外部客户端接入 Token）。
- `kv/<env>/ai-aggregator/bootstrap`: `bootstrap_admin_password`（仅首次初始化使用，完成后立即吊销）。

### 3. 凭据隔离与单写者 CAS 约束
1. **最小权限**: 每个 CPA 实例专属身份只能读取属于其 `accounts/<alias>` 的路径，禁止通配读取全部账号。
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
| **单层调度** | 多次并发请求，CPA 内部多账号正常轮询，New API 仅感知单一 Channel，日志无调度冲突报错 | 查看 New API 渠道日志 |
| **故障隔离** | 模拟单个 CPA 进程停止 (`systemctl stop cliproxyapi@codex-gpt-01`)，仅该模型 Channel 返回不可用，其余正常 | systemd 进程停止实验 |
| **凭据持久化** | 检查持久盘 `/var/lib`、systemd unit、环境文件及日志，确认不存在任何明文 Token / OAuth 凭据 | 磁盘与文件 grep 扫描 |
| **一键回滚** | 触发回滚指令后，客户端流量迅速切回原 LiteLLM 链路，版本和数据状态保持一致 | 验证客户端 fallback 到 LiteLLM |

---

## 九、备份与待实施状态

1. **数据库备份**: SQLite 升级前必须进行一致性冷备并直接加密输出，严禁先输出明文 SQL dump。
2. **OAuth 凭据备份**: 由 Vault 内建版本机制及 Vault 灾备系统保护，禁止打包运行时 tmpfs auth 目录。
3. **当前落地状态**:
   - 已落地：多仓库特性分支 `feat/ai-aggregator-v1-delivery`、架构设计基线文档、UAT GitOps 拓扑声明、Playbook 编排角色草案及 Toolkit 校验脚本。
   - 待实施：真实的固定出口 IP 采集、AWS Spot t4g 1h 实例拉起、私网联通性核实、上游锁定二进制制品构建与 SHA-256 计算、OAuth 登录与 Vault CAS 联调。
