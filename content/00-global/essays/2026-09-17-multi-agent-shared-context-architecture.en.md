# Breaking Vendor Walled Gardens: Practical Architecture for Multi-Agent Shared Task Context Across Google Antigravity, GPT Codex, and Claude Code

**— Anchoring on Git PR/Branches, Local Session Direct Extraction, and a Lightweight Coordination Hub**

---

**Author Profile**

- Author: Haitao Pan
- Role: Platform Engineer
- Projects: XWorkmate · QMD · Open Platform
- Organization: ai-workspace-infra (https://github.com/ai-workspace-infra)
- Motto: Bring AI into real work, not just chat—from ideas to workflows, then to controllable execution.

---

## Abstract

In modern software delivery, experienced engineers often hold annual subscriptions to multiple premier AI coding tools—such as **Google Antigravity**, **GPT Codex (across multiple accounts)**, and **Claude Code**. However, due to commercial rivalry and vendor walled gardens, "what Agent A executes, Agent B does not know, and Agent C has never seen." Whenever a developer switches clients, task context resets to zero, leading to repeated pitfalls, duplicated reasoning, and git branch conflicts.

Drawing upon three core engineering repositories—the task coordination hub **QMD** (`ai-workspace-lab/qmd`), the one-way ingestion proxy gateway **xworkmate-bridge** (`ai-workspace-lab/xworkmate-bridge`), and the extended PostgreSQL container runtime **postgresql.svc.plus** (`ai-workspace-service/postgresql.svc.plus`)—this essay details why we rejected our early over-engineered "standalone Go task-coordination microservice." We converged on a lightweight, production-ready architecture where **local Desktop/CLI session directories serve as the primary data source, QMD acts as the coordination hub right behind Bridge, Git PRs/branches serve as the sole anchor, and PostgreSQL hosts deterministic state merging**.

We unpack the domain entities, the deterministic pure-function merge state machine, incremental cursor tracking across gigabyte-scale logs, secret redaction, advisory transaction locking, and an engineering philosophy balancing Time, Tokens, and Money: using our own agent orchestration architecture to defeat vendor silos—truly "fighting magic with magic."

---

## 1. The Core Problem: Costly "Isolated Fleets" and Commercial Silos

In day-to-day engineering and complex architectural refactoring, many engineers invest in a diversified suite of state-of-the-art AI coding assistants:

- **Google Antigravity**: Deeply integrated into the Google developer infrastructure, featuring exceptional global codebase awareness, dependency graph analysis, and multi-agent collaborative deduction.
- **GPT Codex (Multi-account)**: Extremely agile at localized code logic inference, algorithm optimization, and boundary unit test completion.
- **Claude Code**: Terminal-native CLI workflow, rigorous tool use, and strong architectural planning over medium-to-large codebases.

Theoretically, this combination should function as an elite engineering task force. In practice, however, developers face a crippling bottleneck:

> **What Agent A executes, Agent B has no idea about; the pitfalls Agent B struggled with, Agent C walks straight back into. Switching clients means starting from scratch.**

In real-world software workflows, the unit of delivery is almost always a **Git PR or Feature Branch**:
1. First, you open **Antigravity** in the IDE to trace the system-wide dependency tree, evaluate architectural impacts, and draft a multi-step refactoring plan.
2. Next, you drop into the terminal with **Claude Code** to implement core modules and run unit tests on the fly.
3. Later, hitting tricky concurrency deadlocks or performance bottlenecks, you bring in **Codex** to isolate specific algorithms and backfill edge-case tests.

Yet the reality is severely fragmented:

| Lost When Switching Clients / Worktrees | Native Storage Location | Core Gap & Pain Point |
|---|---|---|
| **Branch goal & plan step progress** | Proprietary agent transcripts | Incompatible formats; wiped out upon context window truncation |
| **Architectural consensus & decisions** | Local cache per tool | Scattered everywhere; context must be re-prompted to each agent |
| **Pitfalls & disproven dead-ends** | No unified persistence | Agent B does not know Agent A already failed at route X |
| **Local validation status (Pass/Fail)** | Ephemeral terminal stdout | Git/CI only knows committed code, not "command Y failed on HEAD" |
| **Active driving session / lease** | None | No lightweight lease; concurrent agents overwrite changes blindly |

### Commercial Realities: "Import-Only" Walled Gardens

Why don't major commercial AI platforms solve this? The answer lies in **vendor lock-in and commercial self-interest**:

- **Eager to import from rivals**: Platforms happily build tools to migrate prompts and chats from competitors to poach active users.
- **Zero interest in exporting or sharing**: No major platform provides an open, standard, real-time shared context protocol to hand off tasks to competing agents. Their business model depends on becoming your sole, all-in-one AI operating environment.

**Vendors have walled gardens, but developers own their local machines.**  
Every CLI and Desktop assistant writes session logs, modifies files, and manipulates git repositories directly on the developer's local filesystem. By constructing an open, standardized, low-overhead coordination protocol anchored to Git branches, we can break through these commercial silos on our own terms.

---

## 2. Architecture Evolution: Rejecting the Standalone Go Service, Converging on QMD as the Hub

In our initial planning (see early drafts in `qmd/docs/plan/multi-agent-shared-context.md`), we designed a traditional centralized microservice topology:
A standalone Go service (`task-coordination`) sat behind `xworkmate-bridge`, owning the PostgreSQL schema, handling coordination, leases, and merges, while QMD was reduced to a local CLI cache.

During single-node and multi-worktree prototyping, this design quickly proved counterproductive:

```
[Deprecated Early Design]
Agent CLI (localhost) ──> QMD Local Cache ──> Bridge ──> Standalone Go Service ──> PostgreSQL
                                                         (Owned Entire Schema)
* Flaws:
  1. Overly complex topology for local development, inflating latency and operational friction.
  2. QMD already manages task claiming; adding a Go service meant maintaining duplicate schemas.
  3. Forced the Bridge gateway into business orchestration, violating its stateless whitelist-proxy rule.
```

After rigorous team review, we pivoted to a clean, consolidated architecture:

```
 [Local Native Data Sources (Local-First)]
   ├── Claude Code CLI:      ~/.claude/projects/<slug>/<sessionId>.jsonl
   ├── Claude Desktop (Code):~/Library/Application Support/Claude/claude-code-sessions/**/local_*.json
   ├── Codex CLI/Desktop:    ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl (2.1GB Cursor)
   ├── Google Antigravity:   ~/.gemini/antigravity/conversation_summaries.db (SQLite) + transcript.jsonl
   ├── OpenCode (Reserved):  ~/.local/share/opencode/ (Probing Ready)
   └── Web/Mobile Connectors: ChatGPT / Claude Web (via browser extensions)
                                    │ (HTTP POST, Strictly One-Way Ingest)
                                    ▼
                         ┌───────────────────────┐
                         │   xworkmate-bridge    │  128 KiB Max Payload / Token Swap
                         │  (8787, Stateless)    │  No Schema / No Storage / No Reads
                         └──────────┬────────────┘
                                    │ POST /api/v1/agent/ingest
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        QMD Daemon (Task-Coordination)                  │
│                        (npx tsx src/cli/qmd.ts mcp --http :8181)       │
│                                                                        │
│  ┌───────────────────────┐  ┌──────────────────────────────────────┐  │
│  │     Local Collector   │  │           Context Merge Engine       │  │
│  │ - Incremental Cursor  │  │ - Pure Function Merge (NFKC + Hash)  │  │
│  │ - Secret Redaction    │  │ - Driver vs. Proposed Discrepancies  │  │
│  │ - Rule-based Extract  │  │ - Commit-Sensitive Verification State│  │
│  └──────────┬────────────┘  └──────────────────┬───────────────────┘  │
│             │                                  │                      │
│             └─────────────────┬────────────────┘                      │
│                               ▼                                        │
│                     PgContextStore (Direct Driver)                     │
│                     (schema-pg.ts as Single Source of Truth)           │
│                               │                                        │
│                 MCP API       │       pg_advisory_xact_lock            │
│        task_resume/note/handoff                                        │
└───────────────────────────────┼────────────────────────────────────────┘
                                │ 127.0.0.1:15432 (Local Direct Connect, SSL disabled)
                                ▼
         ┌───────────────────────────────────────────────┐
         │       postgresql.svc.plus (Containerized)     │
         │  - Base Image: PostgreSQL 17 (macOS arm64)    │
         │  - Core Extensions: pgvector, pg_jieba, trgm  │
         │  - Database: qmd                              │
         └───────────────────────────────────────────────┘
```

### Four Structural Pillars

1. **QMD Is the Coordination Service**: The standalone Go service is deprecated. The schema lives inside QMD (`src/pg/schema-pg.ts`), unifying task claiming and context handoffs under a single codebase.
2. **Local Session Directories as Primary Source**: Native session files generated by Desktop and CLI apps are parsed locally using deterministic rules.
3. **Bridge Enforces Strict One-Way Ingest**: Bridge acts solely as an ingest funnel for browser extensions and mobile clients via `POST /api/v1/agent/ingest`. It holds no state, offers no read endpoints, and swaps user auth tokens for internal `QMD_INGEST_TOKEN`s.
4. **Containerized PostgreSQL 17 Foundation**: Powered by `postgresql.svc.plus` with native arm64 builds, embedding `pgvector` and `pg_jieba` for future semantic and full-text search.

---

## 3. Core Domain Model & Merge Philosophy: "Record Facts, Reject Artifacts"

A catastrophic mistake in multi-agent sharing is attempting to synchronize raw transcripts or code diffs. Doing so inflates databases and consumes agent context windows prematurely.

### 3.1 Strict Ingestion Boundaries

| Allowed Items (✅ High-Value Facts) | Prohibited Items (❌ Artifacts & Redundant Bloat) | Handling / Fallback |
|---|---|---|
| **Goal**: Core deliverable for current branch/PR | Full source code, complete file snapshots | Git branch and working tree files |
| **Plan Steps**: Monotonically advancing step items | Unified Diff patches (`apply_patch` payloads) | Repo-relative file paths touched (`path`) |
| **Decisions**: Key architectural choices & rationales | Verbose build outputs, thousands of log lines | Command string (e.g. `go test`) + exit code (0/1) |
| **Pitfalls**: Disproven routes and known blockers | Screenshots, PDFs, base64 images | Discarded or kept as external URL refs |
| **Verifications**: Command + Pass/Fail + Git Commit | Conversational banter, token usage metrics | Discarded |

**Physical Hard Boundary**:
- Every `ContextItem`'s `body jsonb` is capped at **$\le$ 4 KiB**.
- Items exceeding this limit are discarded during extraction, never silently truncated.

---

### 3.2 Schema Design (`src/pg/schema-pg.ts`)

```sql
-- 1. Thread table (keyed by PR number or active branch)
CREATE TABLE IF NOT EXISTS qmd_ctx_thread (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scope TEXT NOT NULL,                  -- Normalized repo identifier (e.g. github.com/org/repo)
  head_branch TEXT NOT NULL,            -- Branch name
  pr_number INT,                        -- PR number (if PR exists)
  state TEXT NOT NULL DEFAULT 'open',   -- open / paused / handed_off / done
  merged_into UUID REFERENCES qmd_ctx_thread(id),
  driver_session TEXT,                  -- Session ID currently holding active driver lease
  fence INT NOT NULL DEFAULT 1,         -- Monotonically increasing lease fence
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Partial unique indexes: exactly one active thread per branch / PR
CREATE UNIQUE INDEX IF NOT EXISTS idx_qmd_ctx_thread_active_branch 
  ON qmd_ctx_thread(scope, head_branch) 
  WHERE state IN ('open', 'paused', 'handed_off') AND merged_into IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_qmd_ctx_thread_active_pr 
  ON qmd_ctx_thread(scope, pr_number) 
  WHERE state IN ('open', 'paused', 'handed_off') AND pr_number IS NOT NULL AND merged_into IS NULL;

-- 2. Session mapping table
CREATE TABLE IF NOT EXISTS qmd_ctx_session (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL,                 -- claude-code / codex / antigravity, etc.
  source_session_id TEXT UNIQUE NOT NULL,
  agent_kind TEXT NOT NULL,
  head_sha TEXT,
  first_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Context item table (merged atomic facts)
CREATE TABLE IF NOT EXISTS qmd_ctx_item (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  thread_id UUID NOT NULL REFERENCES qmd_ctx_thread(id) ON DELETE CASCADE,
  kind TEXT NOT NULL,                   -- goal / plan_step / decision / pitfall / verification / path
  item_key TEXT NOT NULL,               -- Natural key / normalized hash
  status TEXT NOT NULL DEFAULT 'active',-- proposed / active / resolved / obsolete
  body JSONB NOT NULL,                  -- Hard limit <= 4 KiB
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(thread_id, kind, item_key)
);

-- 4. Ingest cursor table (prevents rescanning multi-GB session logs)
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

### 3.3 Deterministic Merge State Machine (`src/pg/context-merge.ts`)

Instead of unpredictable LLM summarization, merging is handled by pure deterministic TypeScript functions:
`mergeItem(existing, incoming, actor)`

```mermaid
flowchart TD
    Start[Incoming Item Ingestion] --> FieldType{Determine Field Category}
    
    FieldType -->|Dominant: goal / next_action| DriverCheck{Does Agent Hold Active Lease?}
    DriverCheck -->|Yes| Overwrite[Direct Overwrite / Old Value Enters Audit Log]
    DriverCheck -->|No| Downgrade[Demote to status: proposed]
    
    FieldType -->|Plan Step: plan_step| StepCheck{State Transition Valid?}
    StepCheck -->|todo -> doing -> done| Advance[Allow Monotonic Progression]
    StepCheck -->|done -> doing| Reject[Reject Regressive Revert]
    
    FieldType -->|Cumulative: decision / pitfall / path| HashDedup[Unicode NFKC + SHA256 Hash]
    HashDedup --> Union[Union Dedup & Append Source Session ID]
    
    FieldType -->|Verification: verification| HeadCheck{Matches Current Branch HEAD?}
    HeadCheck -->|Matches Current Branch HEAD| Prioritize[Set as Active Verified Record]
    HeadCheck -->|Behind Current HEAD| MarkStale[Tag as STALE in Briefing]
```

#### Merge Rules Summary
1. **Dominant Fields**: `goal` and `next_action` determine direction. Only the session holding an active lease (Fence) can overwrite them. Non-driver updates are stored as `proposed`, appearing in briefings as discussion points for the driver to accept.
2. **Advance-Only Plan Steps**: Any participating agent can advance a step from `todo` to `doing` to `done`. No agent can unilaterally revert a step backwards.
3. **Commit-Sensitive Verification**: Every verification item binds to `gitHead`. If commits advance, older test runs are tagged as `[STALE]`, warning the next agent to re-validate.

---

## 4. Engineering Implementation Across Repositories

### 4.1 `postgresql.svc.plus`: Native arm64 Build on Apple Silicon

Official container registries often only supply `linux/amd64` images. On macOS arm64 machines, running under Rosetta 2 emulation leads to crippling I/O hangs. We build natively using `deploy/base-images/postgres-runtime-wth-extensions.Dockerfile`:

```bash
cd /Users/shenlan/workspaces/ai-workspace-service/postgresql.svc.plus
docker build --build-arg PG_MAJOR=17 -f deploy/base-images/postgres-runtime-wth-extensions.Dockerfile -t postgres-extensions:17 .
```

All credentials reside securely in `~/.config/xworkmate-local/env` (`0600` permissions) without polluting code repositories:
```bash
POSTGRES_PASSWORD=<random-24-char>
PG_DATA_PATH=~/.local/share/xworkmate-local/pgdata
PG_LOCAL_PORT=15432
QMD_BACKEND=pg
QMD_PG_URL=postgres://postgres:${POSTGRES_PASSWORD}@127.0.0.1:15432/qmd
QMD_PG_SSL=disable
AI_WORKSPACE_AUTH_TOKEN=<random-24-char>
QMD_INGEST_TOKEN=<random-24-char>
```

---

### 4.2 `qmd`: Core Engine and Local Probes (`feat/task-coordination`)

To avoid Bun and Node ABI conflicts locally, execution is pinned to `npx tsx src/cli/qmd.ts`.

#### 1. Local Session Collectors (`src/collect/`)
- **Claude Code CLI** (`claude-code.ts`): Reads `~/.claude/projects/<slug>/<sessionId>.jsonl`. Extracts `cwd`, `gitBranch`, `tool_use` file paths, and test commands.
- **Claude Desktop** (`claude-desktop.ts`): Scans `~/Library/Application Support/Claude/claude-code-sessions/**/local_*.json`. Correlates PR numbers and `cliSessionId`.
- **GPT Codex CLI / Desktop** (`codex.ts`): Tracks `qmd_ctx_ingest_cursor` with `byte_offset` on large multi-GB session files. Parses `apply_patch` headers and execution outputs.
- **Google Antigravity** (`antigravity.ts`): Opens `~/.gemini/antigravity/conversation_summaries.db` using `better-sqlite3` in **`readonly: true`** mode, preventing locks with the IDE. Extracts goal summaries and `transcript.jsonl` tool invocations.
- **OpenCode** (`opencode.ts`): Reserved interface stub and directory detection.

#### 2. Secret Redaction (`src/collect/redact.ts`)
A strict regex pipeline scrubs API keys (GitHub, OpenAI, Anthropic, AWS) and credentials before any record hits the database.

#### 3. Advisory Transaction Locking
To prevent race conditions when multiple agents launch concurrently on the same branch:
```typescript
await client.query(
  `SELECT pg_advisory_xact_lock(hashtext($1))`,
  [`thread:${scope}:${headBranch}`]
);
```

#### 4. Standard MCP Tools (`src/mcp/server.ts`)
- `task_resume(cwd)`: Fetches consolidated briefing for the current git branch.
- `task_note(cwd, kind, note)`: Appends an atomic decision or pitfall.
- `task_handoff(cwd, next_action)`: Releases driver lease and specifies next steps.

---

### 4.3 `xworkmate-bridge`: One-Way Ingest Funnel

On branch `feat/qmd-ingest-forward`:
- **Single Ingest Route**: Exposes only `POST /api/v1/agent/ingest` with a strict **128 KiB** payload cap.
- **Token Swap**: Validates incoming `AI_WORKSPACE_AUTH_TOKEN` and swaps it for `QMD_INGEST_TOKEN` upstream.
- **No Read Access**: Any `GET` or alternative path returns 404/405, guaranteeing zero task data leakage.

---

## 5. End-to-End Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer
    participant AGY as Google Antigravity (IDE)
    participant QMD as QMD Daemon (Local)
    participant Claude as Claude Code (CLI)
    participant Codex as GPT Codex (CLI)
    participant PG as PostgreSQL 17

    Note over Dev, AGY: Phase 1: High-Level Exploration & Planning
    Dev->>AGY: Request: "Refactor session auth on branch feat/auth"
    AGY->>AGY: Analyzes full codebase dependencies, generates plan
    QMD->>QMD: Incremental scan extracts Goal & Plan Steps from AGY session
    QMD->>PG: Writes to qmd_ctx_thread keyed to feat/auth
    
    Note over Dev, Claude: Phase 2: Core Implementation
    Dev->>Claude: claude "Continue task on current branch"
    Claude->>QMD: MCP: task_resume(cwd)
    QMD-->>Claude: Returns briefing with AGY's goals & plan
    Claude->>Claude: Implements auth logic, uncovers pitfall during test
    Claude->>QMD: MCP: task_note("pitfall: JTI must be validated to prevent replay")
    Claude->>QMD: MCP: task_handoff("Next: add concurrency stress tests")
    
    Note over Dev, Codex: Phase 3: Boundary Testing & Edge Fixes
    Dev->>Codex: codex "Take over task, backfill unit tests"
    Codex->>QMD: MCP: task_resume(cwd)
    QMD-->>Codex: Briefing returned (includes Claude's pitfall & handoff guidance)
    Codex->>Codex: Writes concurrent unit tests against JTI replay, all passing
    QMD->>PG: Incremental scan ingests Codex verification: pass

    Note over Dev, PG: Phase 4: Delivery Review
    Dev->>QMD: CLI: qmd ctx brief --cwd .
    QMD-->>Dev: Aggregated card: 3 agents' contributions, modified paths, and test pass proof
```

---

## 6. Milestones (M1 ~ M4)

- **M1: Infrastructure Cold-Start**: OrbStack setup, arm64 `postgres-extensions:17` image build, database extension validation, and running existing QMD task-claim integration tests (`test/pg-task.integration.test.ts`).
- **M2: QMD Context Engine & Local Probes**: Schema bootstrap, pure function merge tests, session collectors, CLI and MCP server tools.
- **M3: Bridge Ingest Forwarding**: Implement `POST /api/v1/agent/ingest` in Bridge with payload limits and token replacement.
- **M4: Future Enhancements**: ChatGPT/Claude Web extension ingestion, optional offline LLM summarization, and OpenCode parser implementation.

---

## 7. Summary & Epilogue: Fighting Magic with Magic

As generative AI advances, major commercial vendors will continue erecting walls around their ecosystems. Their commercial incentives dictate that your workflows and data remain locked inside their proprietary apps.

Yet software engineering is fundamentally about **openness, modularity, and control**:
- No single AI model permanently leads across every engineering discipline.
- No single client interface satisfies every phase from system design to terminal debugging.

By anchoring on Git branches, extracting facts from local session directories, and employing an open QMD + PostgreSQL coordination hub, we break free from proprietary silos:

### Epilogue: Balancing Time, Tokens, and Money

When this system first ran end-to-end, the overriding feeling was not technical satisfaction, but **the quiet confidence of taking back control**.

Vendors build walled gardens to force us to purchase separate compute quotas and repeatedly re-feed context. When they build walls, we lay local rails: **using our own agent orchestration architecture to dispatch top-tier models, using software engineering determinism to shatter proprietary black boxes—truly fighting magic with magic.**

This is not an abstract theory, but a pragmatic balance of **Time, Tokens, and Money**:

* **Money**: Having already paid annual subscriptions (Google Antigravity, GPT Codex multi-accounts, Claude Code), we refuse to let any seat sit idle. We maximize utilization and extract full value from every paid compute asset.
* **Tokens**: Strictly storing facts and rejecting artifacts keeps context windows focused on high-value reasoning. Deterministic local rules replace wasteful LLM summary loops.
* **Time**: Anchoring on Git PRs/branches means every agent starts instantly with up-to-date context, eliminating the friction of manual briefings and redundant testing.

Balanced properly, AI ceases to be a set of fragmented toys and becomes an elite, unified engineering task force turning our architectural visions into reality.
