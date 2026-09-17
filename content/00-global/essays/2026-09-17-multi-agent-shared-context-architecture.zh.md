# 破解商业壁垒：在 Google Antigravity、GPT Codex 与 Claude Code 之间打通多 Agent 共享任务上下文的架构实践

**——以 Git PR/分支为锚点、本地会话直采与轻量协调中枢的工程突围**

---

**作者信息**

- 作者：Haitao Pan
- 职位：平台工程师（Platform Engineer）
- 所在项目：XWorkmate · QMD · Open Platform
- 开源组织：ai-workspace-infra（https://github.com/ai-workspace-infra）
- 一句话自述：Bring AI into real work, not just chat——从想法到工作流，再到可控制的落地。

---

## 摘要

在现代软件工程交付中，资深开发者往往同时订阅了多家顶级 AI 编码工具——如 **Google Antigravity**、**GPT Codex（多账号）** 以及 **Claude Code**。然而，由于厂商间的商业竞争与生态封闭壁垒，“A 执行的任务 B 不知道，C 也不了解”，跨客户端切换时上下文归零、重复踩坑、代码冲突频发。

本文结合三大核心工程仓库——任务协调中枢 **QMD**（`ai-workspace-lab/qmd`）、单向转发网关 **xworkmate-bridge**（`ai-workspace-lab/xworkmate-bridge`）以及定制化数据库容器 **postgresql.svc.plus**（`ai-workspace-service/postgresql.svc.plus`），详述如何推翻早期“独立 Go 协调服务”的过度设计，收敛为“以本地 Desktop/CLI 会话为第一数据源、QMD 为任务协调中枢、Git PR/分支为唯一锚点、PostgreSQL 承载确定性合并”的轻量化生产级架构。

文章深入拆解了核心领域模型设计、确定性纯函数合并状态机、GB 级日志增量扫描游标、密钥脱敏与建议锁并发治理，并提出“时间、Token、金钱平衡”的工程哲学，用我们自己的 Agent 编排体系反向调度顶级模型，实现真正的“用魔法打败魔法”。

---

## 1. 开篇痛点：昂贵的“孤岛舰队”与商业利益的暗墙

在日常复杂系统的开发与架构重构中，许多工程团队或个人开发者都在同时采购多套顶级 AI 工具：

- **Google Antigravity**：深度融合 Google 研发体系，擅长超大工程上下文检索、代码依赖图谱分析与多 Agent 联合推演；
- **GPT Codex（多账号订阅）**：单点逻辑推导极快、算法与特定函数重构能力强，适合小步快跑与边缘测试用例补全；
- **Claude Code**：终端命令行原生集成，工具调用（Tool Use）严谨，在中长篇代码重构与架构规划上表现稳定。

按理说，这应当是一支互补协作的“超级工程特遣队”。但在实际开发中，我们遇到的最大痛点是：

> **A 执行的任务 B 不知道，B 踩过的坑 C 又踩了一遍；每次切换客户端，一切都从零开始。**

在真实研发场景下，我们的核心协作载体通常是 **Git PR 或功能分支（Feature Branch）**。理想的流转节奏应当是：
1. 先在 **Antigravity** 梳理架构全貌，理清系统调用链，输出分步重构方案；
2. 切换到终端里的 **Claude Code**，针对重点模块编写核心业务逻辑并就地运行测试；
3. 遇到棘手的并发死锁或算法性能瓶颈时，切到 **Codex** 针对单个函数进行算法优化与单测补齐。

但现实却充满了撕裂：

| 切换客户端或多工作区时丢失的内容 | 各自的原生载体 | 核心痛点与缺陷 |
|---|---|---|
| **分支核心目标与推进进度** | 各 Agent 专有 Transcript | 格式私有互不兼容，且上下文压缩后容易遗忘 |
| **已探索出的架构决定与设计共识** | 各 Agent 本地缓存 | 散落各处，切换后必须重新向新 Agent 交代一遍 |
| **踩过的坑与失败路径** | 无集中沉淀 | Agent B 不知 Agent A 试过某方案行不通，重新踩坑 |
| **本地验证结论（Pass/Fail）** | 终端临时输出 | Git/CI 只知道提交状态，不知道“本地某命令在当前 Commit 失败” |
| **谁当前在主导推进** | 无跨端机制 | 缺乏轻量租约，多端并行时互相覆盖修改 |

### 商业利益的局限：“单向导入”背后的护城河与暗墙

为什么各家商业大模型平台迟迟不解决这个问题？答案在于**商业利益局限**与**生态锁定（Vendor Lock-in）**：

- **鼓励单向迁入**：各大厂商会热衷于开发“从竞品导入提示词/会话”的功能，目标是方便用户从竞争对手阵营“迁移”过来；
- **严禁向外共享**：没有任何一家平台会主动暴露标准实时的任务状态共享协议，允许自身的状态无缝交接给竞品。它们的目标是成为开发者桌面上“唯一的全天候 AI 工作台”。

**商业公司有壁垒，但开发者的机器是自由的。**
所有这些 CLI 和 Desktop 客户端最终都运行在本机，它们的本地会话日志、改动文件、Git 仓库都物理存在于开发者的文件系统上。通过构建一套轻量、开放、标准化的任务协调协议，我们完全可以在本地打碎这些生态孤岛。

---

## 2. 架构演进与反思：为什么推翻“独立 Go 协调服务”

在架构设计初期（见 `qmd/docs/plan/multi-agent-shared-context.md` 早期草案），我们曾倾向于一个经典的分布式分层架构：
在 `xworkmate-bridge` 后方搭建一个独立的 Go 语言微服务（`task-coordination` 服务），由该服务持有数据库 Schema，负责所有的关联、并发控制与合并，QMD 仅退化为本地 CLI 缓存。

但在真实环境验证中，该方案迅速暴露了明显的弊端：

```
[早期被否决的方案]
Agent CLI (localhost) ──> QMD 本地缓存 ──> Bridge ──> 独立 Go 协调服务 ──> PostgreSQL
                                                      (持有完整 Schema)
* 弊端:
  1. 本地单机环境拓扑过长，排障复杂度成倍增加；
  2. QMD 已有 Task 认领逻辑，再起一个 Go 服务导致 Schema 双重维护；
  3. 强行让 Bridge 卷入内部业务编排，破坏了网关的轻量与无状态原则。
```

经过团队的审视与实测，我们做出了关键的**架构收敛与重构决策**：

```
[最终确认的收敛架构]
本地原生目录 (主数据源) 
 ├─ ~/.claude/projects/
 ├─ ~/.codex/sessions/
 ├─ ~/.gemini/antigravity/
 └─ ~/.local/share/opencode/ (预留)
         │
         ▼ (本地增量扫描与规则抽取)
┌────────────────────────────────────────────────────────────┐
│                    QMD Daemon (协调中枢)                   │
│                    (npx tsx src/cli/qmd.ts)                │
│                                                            │
│   src/collect/*      --> 规则提取、密钥脱敏 (Redact)       │
│   src/pg/context-merge.ts --> 纯函数确定性合并算法          │
│   src/pg/context-store.ts --> 事务级建议锁 (Advisory Lock) │
│   src/pg/schema-pg.ts     --> 统一 Schema 事实源           │
│   src/mcp/server.ts       --> MCP 工具 (resume/note/handoff)│
└──────────────┬─────────────────────────────▲───────────────┘
               │                             │
 (127.0.0.1:15432, 直连)                     │ POST /api/v1/agent/ingest
               │                             │ (带 QMD_INGEST_TOKEN)
               ▼                             │
┌──────────────────────────────┐  ┌──────────┴───────────────┐
│     postgresql.svc.plus      │  │     xworkmate-bridge     │
│   PostgreSQL 17 (arm64)      │  │  (8787, 纯单向透传网关)  │
│  - pgvector, pg_jieba, pg_trgm│  └──────────▲───────────────┘
│  - qmd 核心库与部分唯一索引  │             │
└──────────────────────────────┘             │ POST (带用户 Token)
                                  ┌──────────┴───────────────┐
                                  │ Web / 移动端连接器       │
                                  │ (ChatGPT Web / Claude Web)│
                                  └──────────────────────────┘
```

### 架构定型的四大核心原则

1. **QMD 即协调服务本身**：废除独立 Go 服务方案，Schema 统一收敛至 QMD（`src/pg/schema-pg.ts`），QMD 直接承接 Task 认领与上下文协调，杜绝跨语言 Schema 不一致。
2. **本地文件系统为第一数据源**：以 Desktop / CLI 在本机可读的会话目录为基础，使用规则抽取事实。
3. **Bridge 严守“纯单向”底线**：Bridge 仅作为浏览器插件或移动端的数据接入漏斗，只允许 `POST /api/v1/agent/ingest`，无状态、不存数据、不提供读接口，转发时进行令牌置换（用户 Token -> 内部 `QMD_INGEST_TOKEN`）。
4. **PostgreSQL 容器化底座**：基于 `postgresql.svc.plus` 仓库构建 arm64 原生 PostgreSQL 17 容器，本地直连，提供 `pgvector` 与 `pg_jieba` 扩展能力。

---

## 3. 核心领域模型与合并哲学：“只记事实，拒绝制品”

跨 Agent 共享最忌讳把 Agent 的会话全文（Transcript）或代码 Diff 当作上下文同步。这不仅会撑爆存储，更会在下次喂给 Agent 时迅速耗尽 Context Window。

### 3.1 准入红线：什么该记，什么坚决不记

| 允许入库的条目（✅ 高价值事实） | 坚决拒绝的条目（❌ 严禁入库） | 替代/收敛方式 |
|---|---|---|
| **任务目标（Goal）**：当前 PR/分支的核心交付物 | 完整源码、修改前后的代码全貌 | 依赖 Git 分支与工作区文件本身 |
| **步骤计划（Plan Step）**：状态只前进的待办步骤 | 代码补丁（Unified Diff / `apply_patch`） | 仅记录改动的**仓库相对路径（Path）** |
| **关键决策（Decision）**：架构取舍及理由 | 几千行的测试输出日志、构建输出 | 仅提取命令（如 `go test`）与退出码（0/1） |
| **踩坑记录（Pitfall）**：已证实行不通的方案 | 图片、截图、Base64 编码附件 | 丢弃或仅记录引用链接 |
| **验证结论（Verification）**：命令 + 结果 + Git Commit | Agent 间的客套话、Token 消耗统计 | 丢弃 |

为了防止脏数据膨胀，系统在数据库层设置硬约束：
- 每一个 `ContextItem` 的 `body jsonb` 严格限制在 **≤ 4 KiB**；
- 凡是超出大小限制的条目，在规则抽取层直接丢弃，不静默截断。

---

### 3.2 数据库 Schema 与实体关系

在 `src/pg/schema-pg.ts` 中，我们通过 `bootstrapContextSchema` 建立了完整的上下文协同模型：

```sql
-- 1. 任务线程表 (以 PR 或活跃分支为键)
CREATE TABLE IF NOT EXISTS qmd_ctx_thread (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scope TEXT NOT NULL,                  -- 仓库归一化标识 (如 github.com/org/repo)
  head_branch TEXT NOT NULL,            -- 分支名
  pr_number INT,                        -- PR 编号 (若已建 PR)
  state TEXT NOT NULL DEFAULT 'open',   -- open / paused / handed_off / done
  merged_into UUID REFERENCES qmd_ctx_thread(id),
  driver_session TEXT,                  -- 当前持有主导租约的 Session ID
  fence INT NOT NULL DEFAULT 1,         -- 递增租约围栏号
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 部分唯一索引: 一个活跃分支全局唯一, 一个 PR 全局唯一
CREATE UNIQUE INDEX IF NOT EXISTS idx_qmd_ctx_thread_active_branch 
  ON qmd_ctx_thread(scope, head_branch) 
  WHERE state IN ('open', 'paused', 'handed_off') AND merged_into IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_qmd_ctx_thread_active_pr 
  ON qmd_ctx_thread(scope, pr_number) 
  WHERE state IN ('open', 'paused', 'handed_off') AND pr_number IS NOT NULL AND merged_into IS NULL;

-- 2. 会话关联表 (记录参与过该分支的所有 Agent 客户端会话)
CREATE TABLE IF NOT EXISTS qmd_ctx_session (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL,                 -- claude-code / codex / antigravity 等
  source_session_id TEXT UNIQUE NOT NULL,
  agent_kind TEXT NOT NULL,
  head_sha TEXT,
  first_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. 上下文条目表 (合并后的原子事实)
CREATE TABLE IF NOT EXISTS qmd_ctx_item (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  thread_id UUID NOT NULL REFERENCES qmd_ctx_thread(id) ON DELETE CASCADE,
  kind TEXT NOT NULL,                   -- goal / plan_step / decision / pitfall / verification / path
  item_key TEXT NOT NULL,               -- 业务唯一键 / 规范化哈希
  status TEXT NOT NULL DEFAULT 'active',-- proposed / active / resolved / obsolete
  body JSONB NOT NULL,                  -- 硬限制 <= 4 KiB
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(thread_id, kind, item_key)
);

-- 4. 增量扫描游标 (防止重复扫描 GB 级会话日志)
CREATE TABLE IF NOT EXISTS qmd_ctx_ingest_cursor (
  source TEXT NOT NULL,
  path TEXT NOT NULL,
  size BIGINT NOT NULL DEFAULT 0,
  mtime BIGINT NOT NULL DEFAULT 0,
  byte_offset BIGINT NOT NULL DEFAULT 0,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY(source, path)
);
```

---

### 3.3 纯函数合并状态机（Deterministic Context Merge Engine）

多 Agent 协同的核心难题在于**并发与分歧**。如果依赖 LLM 对多端信息做“模糊摘要”，会带来巨大的幻觉、时序混乱与 Token 消耗。

在 `src/pg/context-merge.ts` 中，我们设计了**基于数学规范化的确定性合并函数**：
`mergeItem(existing, incoming, actor)`

```mermaid
flowchart TD
    Start[新条目 Ingest] --> FieldType{判断字段类别}
    
    FieldType -->|主导字段: goal / next_action| DriverCheck{当前 Agent 是否持主导租约?}
    DriverCheck -->|是| Overwrite[直接更新 / 旧值入审计事件]
    DriverCheck -->|否| Downgrade[降级为 status: proposed 提议状态]
    
    FieldType -->|计划步骤: plan_step| StepCheck{状态变迁}
    StepCheck -->|todo -> doing -> done| Advance[允许前进]
    StepCheck -->|done -> doing| Reject[拒绝后退: 状态只进不退]
    
    FieldType -->|累积字段: decision / pitfall / path| HashDedup[Unicode NFKC + SHA256 哈希]
    HashDedup --> Union[并集去重，并在 item_sources 追加会话记录]
    
    FieldType -->|验证记录: verification| HeadCheck{Commit Head 是否匹配?}
    HeadCheck -->|匹配当前分支最新 HEAD| Prioritize[置为最高权重通过结论]
    HeadCheck -->|落后于当前 HEAD| MarkStale[标记为 STALE 已过期]
```

#### 合并规则精要：
1. **主导字段（Dominant Fields）**：`goal` 与 `next_action` 是方向标。仅持有写租约（Fence）的会话能够覆盖；非主导会话的写入自动保存为 `status: 'proposed'`，并在下一次生成的交接简报（Briefing）中以“分歧与提议”的形式展示，由主导会话显式采纳。
2. **计划步骤只进不退**：任何参与的 Agent 都可以将某个 `plan_step` 从 `todo` 推进到 `doing` 再到 `done`。但任何人都无法单方面将其逆向改回 `todo`，避免由于日志读取时序倒错引起倒退。
3. **Commit 敏感的验证结论**：每一个验证条目必须附带 `gitHead`。如果本地代码有了新的提交，旧的验证记录不会被粗暴删除，而是自动呈现为 `[STALE]`，提示当前 Agent 必须重新执行验证。

---

## 4. 三大仓库关键改造与工程落地

### 4.1 `postgresql.svc.plus`：macOS Apple Silicon (arm64) 容器适配

`postgresql.svc.plus` 仓库是我们的企业级数据库底座。由于其官方 CI 默认只编译 `linux/amd64` 镜像，在 macOS arm64（M系列芯片）上运行时会触发 Rosetta 2 转译，引发严重 I/O 阻塞。

我们通过本地多阶段构建快速产出原生 arm64 镜像：

```bash
cd /Users/shenlan/workspaces/ai-workspace-service/postgresql.svc.plus
docker build --build-arg PG_MAJOR=17 -f deploy/base-images/postgres-runtime-wth-extensions.Dockerfile -t postgres-extensions:17 .
```

#### 隔离与无侵入启动
为了不污染任何代码仓库，所有本地运行时配置统一存放在专用配置目录：
`~/.config/xworkmate-local/env`（权限 `0600`）：

```bash
# 生成高强度密码与本地映射端口
POSTGRES_PASSWORD=<随机生成的 24 位字符>
PG_DATA_PATH=~/.local/share/xworkmate-local/pgdata
PG_LOCAL_PORT=15432
QMD_BACKEND=pg
QMD_PG_URL=postgres://postgres:${POSTGRES_PASSWORD}@127.0.0.1:15432/qmd
QMD_PG_SSL=disable
AI_WORKSPACE_AUTH_TOKEN=<随机生成>
QMD_INGEST_TOKEN=<随机生成>
```

启动命令：
```bash
docker compose --env-file ~/.config/xworkmate-local/env -f deploy/docker/docker-compose.yml up -d postgres
```
初始化时确保 `vector`、`pg_trgm` 与 `pg_jieba` 成功装载，为多 Agent 上下文的向量与全文混合检索奠定物理基础。

---

### 4.2 `qmd`：中枢核心重构（feat/task-coordination）

QMD 既是 CLI 工具，也是常驻后台的协调 Daemon。为解决本地 node 与 bun ABI 混用问题，本地统一通过 `npx tsx src/cli/qmd.ts` 启动。

#### 1. 会话采集器矩阵（`src/collect/`）
我们在 QMD 中编写了针对四大客户端的原生探针：
- **Claude Code CLI** (`claude-code.ts`)：深度扫描 `~/.claude/projects/<slug>/<sessionId>.jsonl`，行级捕获 `cwd`、`gitBranch`，从 `tool_use`（Edit/Write）抽取相对路径，从 `Bash` 抽取测试命令。
- **Claude Desktop** (`claude-desktop.ts`)：扫描 `~/Library/Application Support/Claude/claude-code-sessions/**/local_*.json`，抽取关联的 PR 编号及 `cliSessionId`。
- **GPT Codex CLI / Desktop** (`codex.ts`)：
  - Codex 的会话日志往往庞大（单机积累可达 2 GB 以上）；
  - 我们借助 `qmd_ctx_ingest_cursor` 记录 `byte_offset`，每次增量只读取追加字节，解析 `custom_tool_call`（`apply_patch` 头部）与 `function_call` 执行结果。
- **Google Antigravity** (`antigravity.ts`)：
  - 使用 `better-sqlite3` 以 **`readonly: true`** 模式打开 `~/.gemini/antigravity/conversation_summaries.db`，杜绝与 Antigravity IDE 发生锁冲突；
  - 增量抽取 `title`、`workspace_uris`、`status` 及 `transcript.jsonl` 中的关键工具调用。
- **OpenCode** (`opencode.ts`)：
  - 预留抽象探针。检测 `~/.local/share/opencode`，未安装时安静返回，接口就绪但不做无谓解析。

#### 2. 安全扫描与脱敏（`src/collect/redact.ts`）
所有从会话日志抽取的文本，在写入前必须经过正则扫描管道：
自动识别并抹除 GitHub Token、OpenAI Key、Claude Key、AWS 凭证与内网密码特征，杜绝本地凭据泄露进协同层。

#### 3. 事务级建议锁（Advisory Lock）
当多个 Agent 在同一分支并发被唤醒时，为了防止重复创建 Thread，在 `src/pg/context-store.ts` 中通过 PostgreSQL 事务锁进行序列化：

```typescript
await client.query(
  `SELECT pg_advisory_xact_lock(hashtext($1))`,
  [`thread:${scope}:${headBranch}`]
);
```
该机制天然防止了网络/本地并发竞态带来的分支线程分叉。

#### 4. 标准 MCP 接口（`src/mcp/server.ts`）
通过标准协议向所有支持 MCP 的客户端暴露协同工具：
- `task_resume(cwd)`：拉取当前分支由所有 Agent 共同沉淀的交接简报，立即可用；
- `task_note(cwd, kind, note)`：轻量追加一条决策或避坑经验；
- `task_handoff(cwd, next_action)`：收工前交接，明确释放主导权并指定后续建议。

---

### 4.3 `xworkmate-bridge`：严密单向入站网关

在 `xworkmate-bridge` 仓库中（从 `main` 切出 `feat/qmd-ingest-forward`）：
- **单一路由**：仅实现 `POST /api/v1/agent/ingest`，严格限制报文尺寸在 **128 KiB** 以内；
- **令牌置换**：验证外部传入的 `AI_WORKSPACE_AUTH_TOKEN`，在转发给 QMD 的内部请求中置换为 `QMD_INGEST_TOKEN`；
- **只进不出**：不提供任何 `GET` 读接口，彻底保证即使网关暴露在公网，外部也无法探测和逆向内部的任务全貌。

---

## 5. 端到端多 Agent 协作工作流实录

在完成上述改造后，三大 Agent 在同一个 Git PR / 分支上的工作流转变得丝滑且严谨：

```mermaid
sequenceDiagram
    autonumber
    actor Dev as 开发者
    participant AGY as Google Antigravity (IDE)
    participant QMD as QMD Daemon (Local)
    participant Claude as Claude Code (CLI)
    participant Codex as GPT Codex (CLI)
    participant PG as PostgreSQL 17

    Note over Dev, AGY: 阶段 1: 全局规划
    Dev->>AGY: 提需求: "在 feature-auth 分支重构 Session 验证"
    AGY->>AGY: 分析跨模块调用链，生成任务规划
    QMD->>QMD: 本地增量扫描，提取 AGY 会话中的 Goal 与 Plan
    QMD->>PG: 写入 qmd_ctx_thread (关联当前分支)
    
    Note over Dev, Claude: 阶段 2: 核心攻坚
    Dev->>Claude: claude "接着做当前分支任务"
    Claude->>QMD: MCP: task_resume(cwd)
    QMD-->>Claude: 返回简报 (含 AGY 规划的目标与步骤)
    Claude->>Claude: 编写核心鉴权逻辑，跑测试发现: "Token 刷新需防重放"
    Claude->>QMD: MCP: task_note("pitfall: Token 刷新必须验证 JTI 防重放")
    Claude->>QMD: MCP: task_handoff("建议补充并发压测")
    
    Note over Dev, Codex: 阶段 3: 边界测试与修复
    Dev->>Codex: codex "接手任务，补充单测"
    Codex->>QMD: MCP: task_resume(cwd)
    QMD-->>Codex: 返回简报 (含 Claude 留下的避坑要点与交接建议)
    Codex->>Codex: 针对 JTI 重放逻辑编写并发单测并跑通
    QMD->>PG: 增量提取 Codex 的测试通过记录 (Verification: pass)

    Note over Dev, PG: 阶段 4: 交付汇总
    Dev->>QMD: CLI: qmd ctx brief --cwd .
    QMD-->>Dev: 输出聚合卡片: 3家 Agent 协同履历、改动路径、验证结论一目了然
```

---

## 6. 四大里程碑落地与验证路径（M1 ~ M4）

为确保方案具备严格的工程可落地性，实施过程严格划分为四个阶段：

### M1：基础设施就绪（不改动任何业务代码）
1. 安装轻量容器环境 OrbStack；
2. 基于 `postgresql.svc.plus` Dockerfile 构建本地 arm64 `postgres-extensions:17` 镜像；
3. 本地启动数据库，验证 `vector`、`pg_trgm`、`pg_jieba` 扩展正常；
4. 运行 QMD 原生测试 `test/pg-task.integration.test.ts`，验证认领协议与真实 PG 联调成功；
5. 验证 Bridge 基础转发与鉴权。

### M2：QMD 核心引擎与本地探针落地
1. 在 `src/pg/schema-pg.ts` 追加 `bootstrapContextSchema`；
2. 编写 `src/pg/context-merge.ts`，并通过全量单测覆盖（`test/context-merge.test.ts`）；
3. 实现 Claude Code、Claude Desktop、Codex、Antigravity 会话采集器；
4. 暴露 `qmd ctx sources/collect/threads/brief` CLI 指令与 MCP 协议。

### M3：Bridge 单向接入打通
1. 在 Bridge 中增加 `internal/acp/agent_ingest_http.go`；
2. 实现入站报文 128 KiB 限制与 Token 置换逻辑；
3. 编写 httptest 单元测试，确保无权访问或非 POST 方法严格返回 404/405。

### M4：后续演进（架构预留）
1. 编写 ChatGPT Web 与 Claude Web 浏览器插件的轻量接入规范；
2. 引入轻量级 LLM 语义补全（配置化开关，默认关闭以确保完全本地可用）；
3. 实现 OpenCode 原生会话解析器。

---

## 7. 总结与思考：对抗商业垄断的工程定力

在生成式 AI 狂飙突进的今天，每一家大模型厂商都在全力构筑自己的护城河。商业利益驱动着它们互不妥协，甚至故意互设屏障，试图让开发者将所有的上下文与数据资产锁在其平台内部。

但对于专业工程师而言，**灵活性与控制权才是生产力的生命线**：
- 没有一个单一模型能永久保持在所有维度的全胜；
- 没有任何一个单一客户端能满足开发生命周期中从宏观推演到微观调试的所有诉求。

通过这套架构实践，我们证明了一条切实可行的破局路径：
> **以 Git 分支为全局坐标，以本地原生会话为突破口，以开放的 QMD + PostgreSQL 协议为协调中枢。**

我们不需要等待大厂之间达成虚无缥缈的互通协议，也不需要依赖某一家平台的封闭生态。通过对本机原生数据的掌控与严密的工程设计，开发者完全可以打造一支属于自己的跨阵营多 Agent 联合工程舰队。

---

### 尾声：用魔法打败魔法

在这套架构真正跑通的那一刻，最大的感受不是技术有多复杂，而是**一种把控制权夺回自己手中的踏实感**。

厂商们用精巧的商业契约和生态围墙把我们锁在孤岛里，试图让我们为每一次跨端重复购买算力、重复投喂 Context。既然它们筑起高墙，我们就在本地铺设路网：**用我们自己的 Agent 编排体系，反向调度各家顶级 AI；用代码工程的确定性，打碎专有生态的黑盒垄断——这就是最纯粹的「用魔法打败魔法」。**

在实际工程中，这个目标从不是空中楼阁，其核心就在于**时间、Token 与金钱三者的精妙平衡**：

* **金钱（Money）**：既然年订阅的钱已经花出去了（Google Antigravity、GPT Codex 多账号、Claude Code），就绝不让任何一个闲置，物尽其用，榨干每一份算力资产；
* **Token**：严格奉行“只记事实、拒绝制品”，把宝贵的上下文窗口留给真正的高价值决策，用确定的本地规则代替无谓的 LLM 盲目总结，杜绝 Token 浪费；
* **时间（Time）**：用 Git PR / 分支作为全局锚点，任何端启动即是最新状态，彻底消除反复向不同 Agent 交代背景、重跑测试的无效内耗。

三者权衡得当，AI 就不再是割裂的玩具，而是真正能扎实落地我们每一个架构想法的超级协同工程特遣队。
