---
title: 开源自主 AI Bot、云桌面与三级记忆全栈自建技术白皮书
description: 深度整合 DeepSeek Harness AI Bot、DSH Session SuperAgent、AI Desktop (IceWM/DISPLAY=:1)、QMD 任务看板与三级记忆、AI 聚合网关与 XConnect 零信任穿透网络的完整开源自建解决方案与生产工程规范。
slug: ai-bot-desktop-qmd-selfhost-whitepaper
lang: zh
date: 2026-11-14
version: "1.0-release"
status: approved
tags:
  - ai-bot
  - deepseek-harness
  - ai-desktop
  - qmd
  - postgresql
  - pgvector
  - ai-aggregator
  - xconnect
  - xworkmate-app
  - self-host
  - zero-trust
category: reference
---

# 开源自主 AI Bot、云桌面与三级记忆全栈自建技术白皮书

**版本：1.0-release · 状态：已批准归档 · 适用域：AI Workspace / DeepSeek Harness / AI Desktop / 存储与互联体系**

---

## 摘要 (Executive Summary)

随着大语言模型（LLM）从单次文本问答演进为具备工具调用、环境感知与自主循环的智能体（Agent），开发者对运行环境的**自主可控性**、**数据主权**以及**环境执行能力**提出了前所未有的要求。传统的商业 SaaS Agent 与封闭式云桌面存在三大致命短板：
1. **黑盒托管与数据主权丧失**：核心代码、终端执行日志与长短期记忆托管在第三方平台，存在严重的合规与泄密风险；
2. **执行沙箱与图形环境割裂**：多数 Agent 仅局限于无状态容器内的基础 Shell 执行，缺乏完整的图形桌面（GUI）、浏览器会话、本地持久化工作区与实时人工接管（Human-in-the-loop）通道；
3. **单体记忆与并发控制缺失**：多 Agent 并发协作时容易出现任务竞争（Race Condition）、记忆覆盖或上下文污染，缺乏兼顾“微秒级向量检索”与“ACID 事务保障”的多层记忆底座。

为彻底解决上述行业痛点，**AI Workspace Lab** 联合开源生态构建并发布本套**全栈开源、安全闭环、可私有化自建的 AI Bot 与云桌面整体解决方案**。本方案深度整合六大核心子系统：
- **AI 执行宿主 (AI Desktop)**：基于 Linux 轻量级 IceWM 会话（`DISPLAY=:1`）、Chrome 浏览器与持久化终端沙箱，提供确定性的图形与命令行执行空间；
- **智能体自主调度中枢 (DeepSeek Harness & DSH Session SuperAgent)**：集成 Cordis 扩展架构，内置 QMD TaskBoard 自动认领引擎（`qmd-watch`），实现无锁并发轮询、任务状态机与自动唤醒；
- **远程流媒体与零信任配对服务 (ds-harness-remote & xworkmate-app)**：彻底废除第三方平台依赖，采用标准 `xworkmate-pairing-v1` 协议与 WebRTC 高清流，支持移动端/跨平台安全扫码接入与远程接管；
- **状态看板与三级记忆系统 (QMD + PostgreSQL/pgvector)**：构建 L1 检索热层（QMD :8181）、L2 权威事实源（PostgreSQL 17+ / pgvector / pg_jieba / pgmq :5432）以及 L3 冷归档层（S3/对象存储）的三级记忆与任务治理体系；
- **统一模型聚合网关 (AI Aggregator)**：采用 Caddy 自动 TLS 双层鉴权 + New API 多租户计量 + CPA (CLIProxyAPI) 凭据代理，输出标准 `/v1/chat/completions` 与稳定模型别名；
- **零信任穿透互联网络 (XConnect-Gateway & XConnect-One)**：基于 WireGuard overlay 与 Xray VLESS/XHTTP + TLS 封装，实现云桌面“对外零入站端口开放（Zero Inbound Exposure）”跨 NAT 安全互联。

本文档全面阐述该体系的系统架构、数据与控制平面流向、协议规约、完整自建部署脚本清单以及生产级运维排障手册，为企业和极客开发者提供一份开箱即用、工业级可靠的自建参考规范。

---

## 一、系统全景拓扑与六层解耦模型

本架构秉持“**控制面与数据面分离**”、“**记忆热冷解耦**”与“**执行环境强隔离**”三大设计哲学，整体划分为纵向贯通的六层拓扑结构。

### 1.1 系统全景架构图 (Architecture Diagram)

```mermaid
flowchart TD
    subgraph L0["层级 0：客户端与控制终端 (Presentation Tier)"]
        App["xworkmate-app (Flutter 跨平台客户端)\n• 任务看板聚合 [Bridge/QMD]\n• WebRTC 实时看屏与操作\n• xworkmate-pairing-v1 安全扫码"]
    end

    subgraph L1["层级 1：零信任网络覆盖层 (Zero-Trust Overlay Network)"]
        XGW["XConnect-Gateway (公网中继节点)\n• 仅暴露 TCP 443 (VLESS/XHTTP + TLS)\n• WireGuard 隧道转发"]
        XOne["XConnect-One (宿主内网客户端)\n• 单向出站安全长连接\n• 宿主机对外零开放端口 (0 Inbound)"]
    end

    subgraph L2["层级 2：AI 执行宿主与沙箱 (AI Desktop Execution Domain)"]
        subgraph HostDesktop["Linux Host / Contabo VPS (5.189.172.69)"]
            IceWM["IceWM X11 窗口环境 (DISPLAY=:1)\n• 分辨率: 1920x1080\n• 自动化壁纸与状态面板"]
            Browser["Chrome 自动化浏览器\n• DevTools 协议支持\n• 独立 Cookie/Session 隔离"]
            Term["PTY 交互式终端 / Shell\n• 工作区: /var/lib/xworkmate/workspaces\n• 编译工具链与 Git 凭据沙箱"]
        end
    end

    subgraph L3["层级 3：智能体自主编排引擎 (Autonomous Agent Engine)"]
        DSHCore["DeepSeek Harness Bot Core\n• Cordis 插件系统\n• 智能体生命周期与工具分发"]
        SuperAgent["dsh-session-superagent\n• QMD TaskBoard 轮询器 (qmd-watch)\n• task_claim 原语与咨询锁抢占\n• 自动唤醒上下文构建"]
        RemoteServer["ds-harness-remote\n• WebRTC 流媒体服务\n• xworkmate-pairing-v1 扫码配对服务\n• 键鼠事件虚拟注入"]
    end

    subgraph L4["层级 4：状态看板与三级记忆层 (State & Three-Tier Memory)"]
        subgraph MemoryL1["L1: 热检索与任务看板 (QMD Server)"]
            QMD["QMD Engine (:8181)\n• TaskBoard HTTP & MCP 接口\n• 任务状态机: pending/claimed/done\n• 毫秒级向量召回 (可随时重建)"]
        end
        subgraph MemoryL2["L2: 权威事实源 (SSOT Database)"]
            PG["PostgreSQL 17+ (:5432 / :15432)\n• pgvector 稠密向量索引\n• pg_jieba / pg_trgm 中文全文检索\n• pgmq 高可靠消息队列\n• 绝对权威层，数据持久持久化"]
        end
        subgraph MemoryL3["L3: 冷归档层 (Archive Storage)"]
            Drive["S3 / MinIO / WebDAV 云盘\n• GGUF 权重缓存\n• ≥30天历史会话快照\n• 附件与不可变工件 (sha256)"]
        end
    end

    subgraph L5["层级 5：统一模型聚合网关 (AI Aggregator Gateway)"]
        Caddy["Caddy 反向代理\n• 自动 TLS 证书续期\n• 双层 Token 认证与反爬防护"]
        NewAPI["New API 聚合中枢 (:3000)\n• 账本、配额审计与多租户管理\n• 统一暴露标准 /v1 接口"]
        CPA["CPA (CLIProxyAPI) / LiteLLM\n• 本地 OAuth 凭据保持\n• 模型别名映射 (deepseek-chat 等)"]
    end

    %% 连接关系
    App <==>|"WebRTC 流 / 扫码信令"| RemoteServer
    App <==>|"HTTPS / REST API"| XGW
    XGW <==>|"VLESS/XHTTP 443 TLS 隧道"| XOne
    XOne -.->|"内部隧道接入"| IceWM

    RemoteServer -->|"捕获 X11 屏幕画面"| IceWM
    RemoteServer -->|"注入按键与指针事件"| IceWM

    SuperAgent -->|"长轮询与状态汇报"| DSHCore
    SuperAgent -->|"轮询并抢占任务 task_claim"| QMD
    DSHCore -->|"工具调用与脚本执行"| Term
    DSHCore -->|"页面控制与内容获取"| Browser
    DSHCore -->|"请求推理 /v1/chat/completions"| Caddy

    Caddy --> NewAPI --> CPA
    QMD <==>|"读写数据与向量同步"| PG
    PG -.->|"归档备份"| Drive
```

### 1.2 六层架构职责与交互规约

| 层级 | 核心组件 | 技术栈 | 核心职责 | 禁止行为 |
| :--- | :--- | :--- | :--- | :--- |
| **L0 表现层** | `xworkmate-app` | Flutter, WebRTC Native | 统一移动端/桌面端交互、任务展示、审批确认、实时看屏与远控 | 不直接写入 L2 数据库；不绕过 Bridge 直接调用执行器内部 API |
| **L1 互联层** | `XConnect-Gateway`<br>`XConnect-One` | Go, Xray-Core, WireGuard | 构建零信任虚拟私有覆盖网，穿透复杂 NAT，隐藏云桌面真实 IP | 绝不在宿主机防火墙开放裸 WireGuard UDP 端口或未鉴权的 HTTP 端口 |
| **L2 沙箱层** | `AI Desktop` | Linux, IceWM, X11, Chrome | 提供隔离的 GUI 渲染平面、浏览器环境、标准工作区文件系统 | 禁止沙箱环境直接挂载宿主机根目录敏感路径（如 `/etc/shadow`, `~/.ssh`） |
| **L3 智能体** | `DeepSeek Harness`<br>`dsh-session-superagent`<br>`ds-harness-remote` | Node.js, TypeScript, Cordis, WebRTC | 任务编排调度、QMD 看板任务自主认领（`task_claim`）、远程视讯串流 | 不硬编码任何外部平台的 OAuth 流程；严禁向远端日志输出模型 Key |
| **L4 记忆层** | `QMD Server`<br>`PostgreSQL (pgvector)`<br>`云盘/S3` | Rust/Go, Node, PostgreSQL 17+, MinIO | L1 毫秒级任务锁与检索，L2 事务性持久化与向量 SSOT，L3 大文件不可变归档 | L1 严禁持有独占数据；数据写入必须具备回写 L2 或从 L2 恢复的能力 |
| **L5 网关层** | `Caddy` + `New API` + `CPA` | Go, Vue, Python | 统一大模型 API 抽象、提供稳定别名（`deepseek-chat`）、配额扣减与多上游负载均衡 | 严禁通过未加密 HTTP 明文暴露 `/v1` 接口；严禁将原始上游 Key 落盘 |

---

## 二、核心子系统架构规约与交互协议

### 2.1 智能体自主任务调度中枢 (`dsh-session-superagent` + QMD)

在传统多 Agent 系统中，任务分发通常依赖主从集中调度（Master-Worker），一旦 Master 宕机或网络分区，整个协作网络即刻瘫痪。本方案采用**基于 QMD TaskBoard 状态看板的去中心化竞争认领机制**。

#### 2.1.1 任务状态机生命周期 (Task Lifecycle)

```mermaid
stateDiagram-v2
    [*] --> pending: 任务提交 (App / Bridge / CLI)
    pending --> claimed: SuperAgent 轮询发现并抢占 (task_claim)
    claimed --> in_progress: DSH 初始化执行环境并唤醒 Bot
    in_progress --> in_progress: 心跳续约 (task_heartbeat) / 记录执行笔记 (task_note)
    in_progress --> completed: 目标达成，写入产物与审计日志
    in_progress --> failed: 执行出错且不可恢复，写明根因
    in_progress --> handed_off: 超过能力范围，流转给下级专家 Agent (task_handoff)
    claimed --> pending: 认领租约超时 (Heartbeat Timeout)，自动释放
    completed --> [*]
    failed --> [*]
    handed_off --> pending: 重新进入任务看板等待接管
```

#### 2.1.2 咨询锁与无锁竞争原语 (`lib/qmd-watch.js`)

`dsh-session-superagent` 通过内置的 `qmd-watch` 模块实现对 QMD 看板的高效长轮询与安全抢占：
1. **任务过滤与分区 (`partitionQmdTasks`)**：通过标签过滤出 `[Bridge/QMD]` 任务，依据 `status === 'pending'` 筛选候选集；
2. **原子抢占原语 (`task_claim`)**：向 QMD MCP 接口发送 `task_claim` 请求：
   ```json
   {
     "taskId": "task-uuid-v4",
     "assignee": "dsh-desktop-superagent-01",
     "leaseTimeoutMs": 300000
   }
   ```
   QMD 内部通过 PostgreSQL 的行级排他锁（`SELECT ... FOR UPDATE SKIP LOCKED`）确保同时只有一个 Agent 能成功认领，从底层彻底消除脑裂与重复执行；
3. **唤醒提示词生成 (`buildQmdWakeText`)**：抢占成功后，构造结构化的注入上下文：
   ```markdown
   【QMD 任务触发唤醒】
   - 任务标识: task-5739-prod-delivery
   - 目标标题: 自动化构建并在云桌面部署验证服务
   - 优先级: HIGH
   - 约束规范: 遵守三级记忆不落盘原则，产物放置于 workspace/artifacts
   请立即检索相关代码与工作区，执行对应指令并更新 task_note。
   ```

---

### 2.2 远程控制与去中心化安全配对 (`ds-harness-remote` & `xworkmate-app`)

针对旧版本中硬编码第三方平台（如知乎二维码、DSH Go）导致的安全性缺陷与依赖脆弱性，本白皮书规范了全新的 **`xworkmate-pairing-v1` 原生配对与控制协议**。

#### 2.2.1 配对握手与信令流向

```mermaid
sequenceDiagram
    autonumber
    participant DSH as ds-harness-remote (AI Desktop)
    participant Relay as XConnect-Gateway / 信令中继
    participant App as xworkmate-app (移动/桌面端)

    Note over DSH: 宿主机生成瞬时配对令牌 (TTL: 180s)
    DSH->>DSH: 内存生成 xworkmate-pairing-v1 载荷
    DSH-->>App: 展示配对二维码 (Base64) 或终端字符画
    Note over App: 移动端摄像头扫码 / 粘贴密钥
    App->>Relay: 建立 TLS 信令长连接，提交配对请求
    Relay->>DSH: 校验 Pairing Token 签名
    DSH-->>Relay: 确认配对成功，生成短期 WebRTC 凭据
    DSH->>App: 交换 SDP Offer / Answer 与 ICE Candidates
    Note over DSH,App: 基于 DTLS-SRTP 建立端到端加密 WebRTC 隧道
    DSH-->>App: 传输高清视频流 (H.264/VP8, 1080P @ 30FPS)
    App-->>DSH: 传输鼠标移动、点击、键盘按键 DataChannel 事件
```

#### 2.2.2 协议载荷规约 (`xworkmate-pairing-v1`)

扫码配对的二维码解析结果必须为符合下述规范的结构化 JSON 格式：

```json
{
  "version": "xworkmate-pairing-v1",
  "sessionId": "sess_89f02c7a102b4d8e",
  "name": "Contabo-Tokyo-AI-Desktop",
  "relayUrl": "wss://gateway.svc.plus/webrtc/signaling",
  "publicKey": "ed25519_pk_7b9a12c8e3f...",
  "authChallenge": "chal_6d9e01fbc34a",
  "expiresAt": 1794648000
}
```

**安全约束**：
- 严禁任何硬编码的第三方 OAuth 认证跳转；
- 令牌纯内存生成，未落地写入任何磁盘文件，失效期默认 ≤ 300 秒；
- 每次配对完成后，一次性 Challenge 立即作废，防止重放攻击。

---

### 2.3 零信任穿透互联网络 (`XConnect-Gateway` & `XConnect-One`)

AI Desktop 通常部署在公有云 NAT 后方或家庭本地网络（Home-Lab）中，直接开放 22/80/443 等入站端口极易遭受全网扫描与零日漏洞攻击。本方案采用 **XConnect 双端穿透架构**：

```text
+-----------------------+                    +--------------------------+
|  xworkmate-app (用户) |                    |  XConnect-Gateway (中继) |
|  - 拥有网络访问凭据   |                    |  - 域名: tw-xconnect.svc.plus |
+-----------+-----------+                    |  - 仅开放 TCP 443 端口   |
            |                                +------------+-------------+
            | 建立安全访问                                 ^
            v                                             | 出站 VLESS/XHTTP
+-----------+-----------+                                 | 443 TLS 长连接
| XConnect Client (TUN) | <===============================+
+-----------------------+           (零入站开放 Zero Inbound Ports)
                                                          |
                                             +------------+-------------+
                                             |  XConnect-One (宿主守护)  |
                                             |  - 承载 WireGuard 虚拟网卡 |
                                             |  - 宿主机内部 IP: 10.99.0.2|
                                             +------------+-------------+
                                                          |
                                             +------------v-------------+
                                             |   AI Desktop / QMD / DSH |
                                             |   (127.0.0.1 闭环监听)   |
                                             +--------------------------+
```

1. **出站优先原则**：`XConnect-One` 客户端通过标准的 HTTPS/443 协议主动向公网 `XConnect-Gateway` 发起加密长连接（VLESS + XHTTP 传输），流量特征与常规 HTTPS 访问完全一致；
2. **零入站端口暴露**：AI Desktop 宿主机防火墙可配置为 **`INPUT DROP`**，无需开放任何公网入站规则；
3. **WireGuard 内层保护**：网络层内部封装标准 WireGuard 隧道协议，提供端到端 Curve25519 加密与高效点对点路由。

---

### 2.4 三级记忆底座技术细则 (Three-Tier Memory Architecture)

```mermaid
erDiagram
    QMD_L1 ||--o{ PG_L2 : "定时回写与失效恢复 (Sync/Restore)"
    PG_L2 ||--o{ DRIVE_L3 : "周期性冷归档与大文件外部化 (Archive)"

    QMD_L1 {
        string task_id PK "任务唯一标识"
        string status "pending / claimed / done"
        string assignee "抢占 Agent 标识"
        vector embedding "本地快速语义检索 (768/1536 dim)"
    }

    PG_L2 {
        uuid id PK "全局事件唯一 UUID"
        text content "会话上下文与执行明细"
        jsonb metadata "Agent 执行证据、Token 消耗"
        vector embedding "HNSW/IVFFlat 稠密向量索引"
        tsvector tsv_body "pg_jieba 中文分词倒排索引"
        timestamp created_at "权威入库时间戳"
    }

    DRIVE_L3 {
        string file_key PK "S3/WebDAV 对象路径"
        string sha256 "内容不可变哈希校验"
        bigint size_bytes "文件体积"
        jsonb provenance "产生该工件的 Agent 会话链路"
    }
```

- **L1 热检索层 (QMD Server)**：以轻量级高性能为首要目标，维护高频上下文与当前任务看板；当节点发生故障或重启时，**L1 数据允许完全清空**，并通过回放脚本直接从 L2 权威层全量重建；
- **L2 权威事实源 (PostgreSQL + pgvector)**：作为系统唯一的 SSOT（Single Source of Truth），所有任务认领日志、会话事件、代码改动差分（Diff）均由事务保证写入，集成 `pg_jieba` 中文分词与 `pg_trgm` 模糊检索；
- **L3 冷归档层 (Object Storage / Cloud Drive)**：存放历史会话备份、多模态屏幕截图录像、模型微调权重与大体积输出产物，通过 SHA-256 确保工件防篡改。

---

### 2.5 统一模型聚合网关与 DSH 长任务 WORK 模型路由规约

在复杂工程交付、长时间跨会话开发及代码重构等长任务（Long-Horizon Tasks）场景下，传统单次推理小模型容易发生上下文截断、指令漂移与幻觉。本架构通过 **AI 聚合网关（Caddy + New API + CPA）** 统一收敛模型端点，将 DSH 的模型解析层全量重定向至网关的标准 `/v1` 接口，并全面升级为主流的 **WORK 级长任务模型**。

#### 2.5.1 DSH 聚合网关路由拓扑与端点声明

```mermaid
flowchart LR
    DSH["DeepSeek Harness Bot / SuperAgent\n(@deepseek-ai/dsh-llm-pi-ai)"] -->|"标准 /v1 接口 (OpenAI 协议)"| GW["AI 聚合网关 (http://127.0.0.1:3000/v1)"]
    GW --> CPA1["CPA Claude (200K 上下文 / 8K 输出)\nclaude-3-5-sonnet / claude-3-7-sonnet"]
    GW --> CPA2["CPA DeepSeek (64K-128K 上下文 / 8K 输出)\ndeepseek-chat (V3) / deepseek-reasoner (R1)"]
    GW --> CPA3["CPA OpenAI (128K 上下文)\ngpt-4o / codex-main"]
```

#### 2.5.2 主流长任务 WORK 模型矩阵

| 模型稳定别名 (Model Alias) | 底层对齐上游 | 上下文容量 (Context Window) | 最大输出 (Max Tokens) | 核心应用场景与 WORK 定位 |
| :--- | :--- | :--- | :--- | :--- |
| **`claude-3-5-sonnet`** | Claude 3.5 Sonnet (20241022) | 200,000 | 8,192 | **首选主力 WORK 模型**：超长代码审查、多文件架构重构、复杂工具链链式调用 |
| **`claude-3-7-sonnet`** | Claude 3.7 Sonnet | 200,000 | 8,192 | **高阶深度推理模型**：复杂系统架构演进、数学建模与端到端系统排错 |
| **`deepseek-chat`** | DeepSeek V3 | 65,536 | 8,192 | **性价比日常 WORK 模型**：常规业务编码、自动化运维脚本、QMD 任务初筛 |
| **`deepseek-reasoner`** | DeepSeek R1 | 65,536 | 8,192 | **长链思考推理模型**：算法设计、高难度死锁与并发边界条件诊断 |
| **`gpt-4o`** | OpenAI GPT-4o / Codex | 128,000 | 4,096 | **全能兼容 WORK 模型**：多模态截图诊断、跨语言生态代码生成与转换 |

#### 2.5.3 DSH Profile 配置规范 (`cordis.patch.yml`)

DSH 客户端通过如下 Patch 声明完成模型重定向与默认 WORK 模型绑定：

```yaml
- id: agent-default-model
  name: "@deepseek-ai/dsh-agent-default-model"
  config:
    provider: ai-aggregator
    model: claude-3-5-sonnet

- id: llm-pi-ai
  name: "@deepseek-ai/dsh-llm-pi-ai"
  config:
    providers:
      ai-aggregator:
        displayName: "AI Aggregator (Work Gateway)"
        api: openai-completions
        baseURL: "http://127.0.0.1:3000/v1"
        apiKeyEnv: AI_WORKSPACE_AUTH_TOKEN
        models:
          - id: claude-3-5-sonnet
            name: "Claude 3.5 Sonnet (WORK - Long Task)"
            contextWindow: 200000
            maxTokens: 8192
          - id: claude-3-7-sonnet
            name: "Claude 3.7 Sonnet (WORK - Advanced)"
            contextWindow: 200000
            maxTokens: 8192
          - id: deepseek-chat
            name: "DeepSeek V3 (Chat/Work)"
            contextWindow: 65536
            maxTokens: 8192
          - id: deepseek-reasoner
            name: "DeepSeek R1 (Reasoner/Work)"
            contextWindow: 65536
            maxTokens: 8192
          - id: gpt-4o
            name: "GPT-4o (Work)"
            contextWindow: 128000
            maxTokens: 4096
```

---

## 三、开源自建全栈实施指南 (Self-Hosting Implementation)

本节提供在全新 Linux 服务器（Ubuntu 22.04 / 24.04 LTS 或 Debian 12，推荐配置：4 核 CPU / 8GB 内存 / 50GB SSD）上完整落地自建环境的详尽步骤。

### 3.1 基础设施与运行时准备

在宿主机上安装 Docker Engine、Docker Compose v2 与必要的系统级工具链：

```bash
# 1. 更新系统并安装前置工具
sudo apt-get update && sudo apt-get install -y \
    ca-certificates curl gnupg lsb-release jq git xvfb x11vnc icewm dbus-x11

# 2. 安装 Docker 与 Compose 插件
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 3. 配置安全隔离的工作区目录
sudo mkdir -p /var/lib/xworkmate/{workspaces,storage,certs}
sudo chmod 700 /var/lib/xworkmate
```

---

### 3.2 声明式服务编排 (`docker-compose.yml`)

创建统一编排文件 `/var/lib/xworkmate/docker-compose.yml`。按照“**不落盘、不进明文配置**”的安全红线，敏感变量全部采用 `${VAR:?VAR is required}` 规范：

```yaml
version: "3.8"

networks:
  xworkmate-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16

services:
  # =========================================================================
  # 1. L2 权威数据源：PostgreSQL 17 + pgvector
  # =========================================================================
  workspace-postgres:
    image: pgvector/pgvector:pg17
    container_name: workspace-postgres
    restart: always
    environment:
      POSTGRES_DB: xworkmate
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?Required}
    volumes:
      - /var/lib/xworkmate/storage/postgres-data:/var/lib/postgresql/data
    networks:
      - xworkmate-net
    # 仅暴露给本地回环或内部网络，生产环境下禁止直接公网发布 5432
    ports:
      - "127.0.0.1:15432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d xworkmate"]
      interval: 5s
      timeout: 5s
      retries: 5

  # =========================================================================
  # 2. L1 热记忆与任务看板：QMD Server
  # =========================================================================
  workspace-qmd:
    image: ghcr.io/ai-workspace-lab/qmd:latest
    container_name: workspace-qmd
    restart: always
    environment:
      QMD_BACKEND: postgres
      QMD_PG_DSN: postgres://postgres:${POSTGRES_PASSWORD}@workspace-postgres:5432/xworkmate?sslmode=disable
      QMD_MCP_TOKEN: ${QMD_MCP_TOKEN:?Required}
      QMD_INGEST_TOKEN: ${QMD_INGEST_TOKEN:?Required}
    depends_on:
      workspace-postgres:
        condition: service_healthy
    networks:
      - xworkmate-net
    ports:
      - "127.0.0.1:8181:8181"
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://127.0.0.1:8181/mcp', r => process.exit(r.statusCode < 500 ? 0 : 1))"]
      interval: 10s
      timeout: 5s
      retries: 3

  # =========================================================================
  # 3. AI 聚合网关与模型代理：New API + CPA
  # =========================================================================
  workspace-ai-aggregator:
    image: calciumion/new-api:latest
    container_name: workspace-ai-aggregator
    restart: always
    environment:
      SQL_DSN: "postgres://postgres:${POSTGRES_PASSWORD}@workspace-postgres:5432/xworkmate?sslmode=disable"
      GLOBAL_WEB_TOKEN: ${GLOBAL_WEB_TOKEN:?Required}
    depends_on:
      workspace-postgres:
        condition: service_healthy
    networks:
      - xworkmate-net
    ports:
      - "127.0.0.1:3000:3000"

  # =========================================================================
  # 4. 边界安全入口反向代理：Caddy
  # =========================================================================
  workspace-caddy:
    image: caddy:2-alpine
    container_name: workspace-caddy
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/lib/xworkmate/Caddyfile:/etc/caddy/Caddyfile:ro
      - /var/lib/xworkmate/certs:/data
    networks:
      - xworkmate-net
    depends_on:
      - workspace-qmd
      - workspace-ai-aggregator
```

---

### 3.3 边界反代配置 (`/var/lib/xworkmate/Caddyfile`)

```caddyfile
# 生产自建域名（替换为你自己的注册域名或动态 DNS）
desktop.yourdomain.com {
    # 强制 TLS 与 HSTS
    tls internal # 若具备公网域名则替换为管理员邮箱，自动申领 Let's Encrypt 证书
    
    # 1. 统一大模型 API 网关
    handle_path /v1/* {
        reverse_proxy workspace-ai-aggregator:3000 {
            header_up Host {upstream_hostport}
            header_up X-Real-IP {remote_host}
        }
    }

    # 2. QMD 记忆与看板接口
    handle_path /qmd/* {
        @token_check {
            header Authorization "Bearer {$QMD_INGEST_TOKEN}"
        }
        handle @token_check {
            reverse_proxy workspace-qmd:8181
        }
        handle {
            respond "Unauthorized Access to Memory Hub" 401
        }
    }

    # 3. 默认桌面引导与状态页
    handle {
        respond "AI Workspace Sovereign Host Online" 200
    }
}
```

---

### 3.4 AI Desktop 宿主图形与远程守护配置

#### 3.4.1 X11 与 IceWM Systemd 守护单元 (`/etc/systemd/system/xworkmate-desktop.service`)

```ini
[Unit]
Description=AI Desktop Virtual X11 & IceWM Session (:1)
After=network.target

[Service]
Type=simple
User=root
Environment=DISPLAY=:1
Environment=HOME=/root
ExecStartPre=/bin/sh -c 'rm -f /tmp/.X1-lock /tmp/.X11-unix/X1'
ExecStart=/usr/bin/xinit /usr/bin/icewm-session -- /usr/bin/Xvfb :1 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### 3.4.2 智能体远程看屏与配对守护 (`/etc/systemd/system/dsh-remote.service`)

```ini
[Unit]
Description=DeepSeek Harness Remote Control & WebRTC Server
After=xworkmate-desktop.service
Requires=xworkmate-desktop.service

[Service]
Type=simple
User=root
WorkingDirectory=/var/lib/xworkmate/workspaces/ds-harness-remote
Environment=DISPLAY=:1
Environment=NODE_ENV=production
Environment=PORT=8090
ExecStart=/usr/local/bin/node apps/server/dist/index.js --port 8090 --pairing-protocol xworkmate-pairing-v1
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### 3.4.3 智能体自主轮询调度守护 (`/etc/systemd/system/dsh-superagent.service`)

```ini
[Unit]
Description=DSH Session SuperAgent Autonomous QMD Watcher
After=dsh-remote.service
Requires=dsh-remote.service

[Service]
Type=simple
User=root
WorkingDirectory=/var/lib/xworkmate/workspaces/dsh-session-superagent
Environment=NODE_ENV=production
Environment=QMD_URL=http://127.0.0.1:8181
Environment=POLL_INTERVAL_MS=3000
ExecStart=/usr/local/bin/node bin/dsh-session-superagent.js --watch qmd://default --auto-claim
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

### 3.5 极简一键安全启动脚本 (`launch-all.sh`)

创建启动执行脚本，贯彻“**纯内存注入机密、执行后即刻销毁环境变量**”的安全红线：

```bash
#!/usr/bin/env bash
set -euo pipefail

# 强制压制调试日志输出，杜绝泄露机密
set +x

echo "=========================================================="
echo "    启动 AI Workspace / AI Bot 全栈自建环境"
echo "=========================================================="

# 1. 纯内存生成高强度随机凭据
export POSTGRES_PASSWORD=$(openssl rand -hex 24)
export QMD_MCP_TOKEN="qmd_mcp_$(openssl rand -hex 16)"
export QMD_INGEST_TOKEN="qmd_ing_$(openssl rand -hex 16)"
export GLOBAL_WEB_TOKEN="ai_gw_$(openssl rand -hex 20)"

# 2. 退出清理 Trap，确保环境变量在脚本终止时被完全抹除
trap 'unset POSTGRES_PASSWORD QMD_MCP_TOKEN QMD_INGEST_TOKEN GLOBAL_WEB_TOKEN; echo "[Security] 机密变量已从内存完全清除。"' EXIT

# 3. 启动基础设施与记忆底座
cd /var/lib/xworkmate
docker compose up -d

# 4. 激活并启动系统桌面与 Agent 服务
systemctl daemon-reload
systemctl restart xworkmate-desktop.service
systemctl restart dsh-remote.service
systemctl restart dsh-superagent.service

# 5. 等待健康探测就绪
echo "[Health] 正在执行服务就绪探针..."
for i in {1..30}; do
    if curl -s -f http://127.0.0.1:8181/mcp >/dev/null 2>&1; then
        echo "[Health] QMD 记忆与看板服务就绪！"
        break
    fi
    sleep 1
done

# 6. 打印一次性标准交付卡片
echo "=========================================================================="
echo "              AI Workspace / AI Bot 基础设施自建成功！"
echo "=========================================================================="
echo " 运行模式       : Sovereign Self-Hosted (All-in-One Hardened)"
echo " AI Desktop 会话: DISPLAY=:1 (分辨率: 1920x1080)"
echo " 统一模型网关   : http://127.0.0.1:3000/v1 (反代端点: https://desktop.yourdomain.com/v1)"
echo " QMD 任务看板   : http://127.0.0.1:8181"
echo " QMD Ingest 令牌: ${QMD_INGEST_TOKEN}"
echo " QMD MCP 令牌   : ${QMD_MCP_TOKEN}"
echo ""
echo "📱 【XWorkmate App 客户端连接向导】"
echo "   1. 启动 XWorkmate App -> 进入「设置 (Settings)」->「账户与同步」"
echo "   2. 扫描 AI Desktop 终端生成的 xworkmate-pairing-v1 专属二维码"
echo "   3. 侧栏看板将自动挂载 [Bridge/QMD] 任务流，并激活 WebRTC 实时看屏接管"
echo "=========================================================================="
```

---

## 四、运维验收、监控与排障手册 (Operations & Troubleshooting)

### 4.1 生产就绪黄金验收清单 (Production Acceptance Checklist)

在宣布系统正式上线前，必须逐项执行以下 10 项硬性门禁验证：

| 验收编号 | 检验项 | 验证指令 / 检查方法 | 期望输出 | 严重级别 |
| :---: | :--- | :--- | :--- | :---: |
| **AC-01** | PostgreSQL 向量插件 | `docker exec workspace-postgres psql -U postgres -d xworkmate -c "SELECT extname FROM pg_extension WHERE extname IN ('vector', 'pg_trgm');"` | 返回至少 2 行（`vector`, `pg_trgm`） | 阻断 |
| **AC-02** | QMD MCP 端点连通性 | `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8181/mcp` | 返回 HTTP 状态码 `< 500`（通常为 200 或 400 缺省参数） | 阻断 |
| **AC-03** | TaskBoard 自动抢占 | 注入一条 `status: pending` 测试任务，检查 Agent 日志 | 日志输出 `[qmd-watch] claimed task: <id>` 且任务状态变为 `claimed` | 阻断 |
| **AC-04** | AI Desktop 渲染管线 | `DISPLAY=:1 xwininfo -root` | 成功打印根窗口几何尺寸（如 `1920x1080`） | 阻断 |
| **AC-05** | WebRTC 远程推流 | 打开 XWorkmate App 连接桌面并查看实时视频流 | 延迟 `< 150ms`，画面清晰无花屏，键鼠事件正常响应 | 严重 |
| **AC-06** | 零入站端口合规 | `sudo ss -tuln \| grep -E ':(5432\|8181\|3000)'` | 监听地址均为 `127.0.0.1`，无 `0.0.0.0` 泄露 | 阻断 |
| **AC-07** | 机密防泄露审计 | `grep -rn "${POSTGRES_PASSWORD}" /var/lib/xworkmate/ /var/log/` | 零匹配项（无任何明文落盘） | 阻断 |
| **AC-08** | 模型网关兼容性 | `curl -s http://127.0.0.1:3000/v1/models` | 返回标准 OpenAI JSON 格式的模型清单 | 严重 |
| **AC-09** | XConnect 隧道保活 | `xconnect status` | 返回 `Connected`，且延迟在稳定区间 | 严重 |
| **AC-10** | 内存与进程守护 | `systemctl is-active dsh-superagent dsh-remote xworkmate-desktop` | 全部返回 `active` | 严重 |

---

### 4.2 典型陷阱与排障 Runbook (Troubleshooting Runbook)

#### 陷阱 1：15432 端口冲突 (`port is already allocated`)
- **根因**：宿主机若已存在旧版本 PostgreSQL 容器或其他数据库实例，直接映射 `15432` 会导致容器创建失败；
- **排查与修复**：
  ```bash
  # 查询当前占用者
  sudo lsof -i :15432 || sudo ss -tulpn | grep 15432
  # 规范解法：在 docker-compose.yml 中顺延映射端口至 15433，或通过 Unix Domain Socket 内部互通
  ```

#### 陷阱 2：QMD 容器健康检查持续报 Unhealthy
- **根因**：精简版 Node.js 镜像内部未安装 `curl`，若直接在 `healthcheck` 中调用 `curl` 将导致探针永久退出码 127；
- **规范解法**：采用 Node.js 原生代码进行轻量级 HTTP 探针，无需依赖外部系统二进制：
  ```json
  ["CMD", "node", "-e", "require('http').get('http://127.0.0.1:8181/mcp', r => process.exit(r.statusCode < 500 ? 0 : 1))"]
  ```

#### 陷阱 3：WebRTC 视频流黑屏或 ICE 穿透失败
- **根因**：云服务器处于严格 NAT 后方，未正确配置 STUN/TURN 服务器或 UDP 穿透包被拦截；
- **排查与修复**：
  1. 检查 `ds-harness-remote` 配置中是否包含高可用的公网 STUN 节点（如 `stun:stun.l.google.com:19302`）；
  2. 若双方处于对称型 NAT（Symmetric NAT），必须通过 `XConnect-Gateway` 的中继链路路由 WebRTC 媒体包。

#### 陷阱 4：QMD 任务堆积，Agent 无法自动唤醒
- **根因**：任务的标签缺少 `[Bridge/QMD]`，或者之前的 Agent 异常退出未释放锁，导致任务永久停留在 `claimed` 状态；
- **排查与修复**：
  ```bash
  # 检查过期任务并重置状态为 pending
  docker exec workspace-postgres psql -U postgres -d xworkmate -c "
    UPDATE qmd_tasks 
    SET status = 'pending', assignee = NULL 
    WHERE status = 'claimed' AND updated_at < NOW() - INTERVAL '10 minutes';
  "
  ```

---

## 五、开源生态协同与未来演进 (Ecosystem & Roadmap)

### 5.1 组织仓库协同矩阵与 Fork Base 上游溯源声明

本解决方案建立在优秀的开源项目与社区贡献基础之上。为了恪守开源规范并保持清晰的工程演进谱系，各核心组件均建立了严格的溯源声明：

#### 5.1.1 仓库协同与上游溯源矩阵

| 组织 / 仓库 | 模块定位与职责 | 开源协议 | Fork Base (上游基线) | 衍生演进核心成果 |
| :--- | :--- | :--- | :--- | :--- |
| **`ai-workspace-lab/ds-harness-remote`** | 桌面视讯串流与键鼠事件中继 | MIT | [liguobao/ds-harness-remote](https://github.com/liguobao/ds-harness-remote) | 彻底清除知乎/微信第三方依赖；融入 `xworkmate-pairing-v1` 原生配对与 XConnect 零信任隧道 |
| **`ai-workspace-lab/dsh-session-superagent`** | 智能体自主轮询与状态总线 | MIT | [MYCF711/dsh-session-superagent](https://github.com/MYCF711/dsh-session-superagent) | 全面融入 XWorkmate 生态规范；新增 QMD TaskBoard 状态看板长轮询与无锁竞争抢占（`qmd-watch`） |
| **`ai-workspace-lab/deepseek-harness`** | 智能体微内核与生命周期编排 | Apache-2.0 | [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) | 提供 Cordis 插件规范、工具管道上下文与 `@deepseek-ai/dsh-llm-pi-ai` 聚合网关路由 |
| **`ai-workspace-lab/xworkmate-app`** | 跨平台多模态交互客户端 | GPL-3.0 | 原创研发 (Original) | 消费 Bridge Catalog，聚合 QMD 任务列表，提供原生 WebRTC 远程视讯与扫码会话建立 |
| **`ai-workspace-xstream/XConnect-Gateway`** | 零信任跨网穿透服务端 | MPL-2.0 | 原创研发 (Original) | 提供 VLESS/XHTTP 443 传输中继与设备签名配对 |
| **`ai-workspace-xstream/XConnect-One`** | 终端受控轻量级守护客户端 | MPL-2.0 | 原创研发 (Original) | 维护本地 WireGuard 虚拟网卡与单向安全出站长连接 |

### 5.2 未来演进路线 (Future Roadmap)

1. **混合多执行器协同网络 (v2.2)**：在 `dsh-session-superagent` 的基础上，支持接入 OpenCode、Codex CLI、Claude Code 等多样化执行引擎，依据任务类型（架构设计、代码生成、重构测试）实现动态多 Agent 协同分流；
2. **端侧小模型辅助路由 (v2.3)**：在 AI Desktop 内部集成基于 Ollama / llama.cpp 的轻量级本地模型（如 DeepSeek-R1-Distill-7B），负责高频微小任务（语法树解析、正则匹配、日志初筛），大幅降低云端 API Token 成本并提升秒级响应体验；
3. **分布式全局记忆同步网格 (v3.0)**：扩展 QMD 三级记忆为分布式多活网格，支持开发者的移动端、笔记本本地端与云端 AI Desktop 实现跨地域、去中心化的零知识加密记忆同步。

---

## 六、归档与参考索引 (References)

- **总索引归档**：[docs/reference/index.md](index.md)（第 51 条：开源自主 AI Bot、云桌面与三级记忆全栈自建技术白皮书）
- **记忆规约文档**：[QMD + PG + 云盘三级任务聚合与记忆系统落地规范](qmd-pg-cloud-drive-three-tier-memory-spec.zh.md)
- **多云架构白皮书**：[多云平台工程技术白皮书（中文）](multi-cloud-platform-engineering-whitepaper.zh.md)
- **零信任技术选型**：[XConnect 对比 EasyTier、Tailscale、NetBird 技术选型报告](xconnect-vs-easytier-tailscale-netbird-technology-selection-20261026.zh.md)
- **平台可观测性交付规范**：[Infrastructure-MCP-Server 部署与 QMD 交付全景技术规范](infrastructure-mcp-observability-cmdb-qmd-delivery-spec.zh.md)
