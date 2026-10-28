---
title: 线上出问题，让编程 Agent 直接查，还是让观测 Agent 先巡检？
series: 独立开发观察者计划 · 2026-11 开篇补充案例（OPE）
status: draft
fact_checked: 2026-10-28（观测云官方文档）
---

# 线上出问题，让编程 Agent 直接查，还是让观测 Agent 先巡检？

> 本篇是观察者计划 11 月开篇的补充案例（OPE：平台编排仓库 Platform-Orchestrator 的日常巡检流水线）。单一主题：**线上排障的入口该放在哪一类 Agent 上**。Obsy Agent Teams 一侧目前只完成了文档核验，实测部分全部标注「待实测」。

## 一、案例：一条每天都会跑的快照流水线，两次红灯

OPE 里有一条定时的「每日快照编排」流水线，开工前先做一道 Gate：逐项探测依赖服务的健康状态。最近两次失败，都是用编程 Agent（Codex / Claude Code 一类）直接读 CI 日志、读代码、在本地复现定位的：

1. **Gate 失败**：探测 Grafana 时访问 `/grafana/api/health` 收到 302，被重定向到登录页；而根路径 `/api/health` 返回 200、数据库状态正常。结论是 Grafana 已不再挂载在 `/grafana` 子路径下，问题在探测脚本的地址，不在 Grafana 本身，重跑无效。
2. **IaC 准备失败**：Serverless 编排在 UAT 运行时报 `ContractError: unsupported environment`。原因是 GitOps 新增了一个 `environment: dev` 的目标，而工作流锁定的 IaC 模块版本早于支持 `dev` 的版本；用新版本模块离线校验，全部目标通过。修法是升级版本锁，而不是改 GitOps 去迁就旧校验。

两次都定位准确，但有一个共同点：**都是流水线已经红了以后，人把 Agent 拉进来，从代码和日志倒推**。

## 二、两条路径的本质差别

**A. 编程 Agent 直接 debug**（ChatGPT/Codex、Claude Code、Antigravity）：工作对象是仓库、CI 日志和终端。强项是能读懂代码、在本地复现、直接给出最小 PR。短板是每次都从零收集上下文；它看到的是「这次失败」的日志，看不到这个端点过去一周的状态变化；想让它看线上，就得把 shell / kubectl / 云凭据交给它，权限边界由人临时把控。

**B. Obsy Agent Teams 巡检排查**：工作对象是观测云工作空间里的指标、日志、链路和告警。按官方文档[^1][^2]：
- Agent 有独立职责、权限范围和部署环境，Agent 本体自托管安装；可按职责启用 Skill 与 MCP 服务；
- 自动化任务支持每小时 / 每天 / 工作日 / 每周 / 每月 / Crontab 计划，每个任务使用**固定会话**，历次执行与追问连续保留，可横向比较[^3]；
- 可由告警策略或外部 Webhook 经「任务接入」触发；结果可投递到已配置的消息渠道；
- 权限模式分「默认权限 / 完全访问」，文档建议首次使用默认权限；**注意：通过对话创建的自动化任务默认是完全访问权限**，需要创建后改回[^3]；
- 前置条件：工作空间拥有者需开启空间 AI 功能，免费功能也需开启[^4]。当前我们的空间此开关为关闭、尚未创建任何 Agent。

一句话：A 擅长「从代码侧修」，B 擅长「从数据侧先发现、持续盯」。

## 三、代码化落地主线（不走控制台点击）

- **GitOps**：在仓库中声明巡检意图——检查对象（如 Grafana 健康端点）、期望状态码、时间窗、输出格式；只放非敏感参数。
- **IaC-modules**：Renderer 把巡检意图渲染为 HCL，`terraform plan` 离线验证监控器与拨测定义；免费空间无 OpenAPI 时只产出离线 HCL。
- **Playbook**：Ansible 下发 DataKit / OTel Collector，把流水线 Gate 结果和健康探测作为指标、日志写入观测云，这是 B 路径能「看见」问题的前提。
- **Vault**：DataKit 写入 Token、只读查询 Key 运行时注入；巡检 Agent 只拿只读凭据，不复用生产写凭据。
- **AI 分工**：观测 Agent 负责发现与证据整理（只读）；编程 Agent 负责起草修复 PR；人审核 PR 与 plan，决定是否合并。

## 四、实践：用六层底座把两类 Agent 接到同一套事实上

前面的对比里，编程 Agent 缺的是「历史与线上数据」，观测 Agent 缺的是「代码与变更通道」。下半篇把两者需要的东西拆成六层，统一用 MCP 暴露出来，作为 AI Ops 的底座。原则只有三条：**默认只读；凭据运行时从 Vault 注入；任何变更只走 GitOps PR + 人工审核**。

### 4.1 六层底座

| 层 | 承载物 | 对 Agent 暴露的方式 | 权限 |
|---|---|---|---|
| 代码 | `iac_modules`（GitOps YAML → 显式 HCL，`terraform plan`）、`playbooks`（部署与就绪探测脚本）、`Platform-Orchestrator`（流水线编排，原名 platform-ops-toolkit），均为公开仓库 | 仓库只读 + PR | 只读；写入仅经 PR |
| 环境 | `gitops` 仓库中的环境 / 目标声明（sit、uat、prod、shared，以及新增的 dev 目标） | 声明文件即环境清单 | 只读 |
| 配置 | 网关路由、适配器参数、客户端 MCP 配置；只放非敏感参数 | 随代码层进入 Git | 只读；敏感值只存引用 |
| 资源 | 运行中的集群、服务与观测数据（指标 / 日志 / 链路 / 告警） | 观测服务上的 MCP 适配器；本机 Infrastructure MCP Server 聚合 | 只读服务账号 |
| 知识库 | 历史排障记录、knowledge 仓库 `docs/reference` 下的参考文档 | QMD MCP Server（PostgreSQL 后端），定期导入并向量化 | 只读检索 |
| MCP | 把上面五层统一成工具面的协议层 | 本地 stdio 服务 + 远端 SSE 适配器 | 按工具粒度控制 |

```text
           编程 Agent（Codex / Claude Code / Antigravity）      观测 Agent（Obsy Agent Teams 等）
                         │                                              │
                         └──────────────── MCP ─────────────────────────┘
                                  │                         │
                 本机：Infrastructure MCP Server       远端：观测服务网关（Basic Auth）
                   ├─ CMDB / 拓扑 / 环境图                 ├─ /mcp/v1/grafana/*  → mcp-grafana（只读）
                   ├─ 观测服务作为数据源                    ├─ /mcp/v1/metrics|logs|traces/* → 规划中
                   └─ QMD（历史记忆 / 参考文档检索）          └─ 其余路径 → Grafana Web UI
                                  │
            代码层（iac_modules / playbooks / Platform-Orchestrator）+ 环境层（gitops）
                                  │
                     变更：只能 GitOps PR → CI（plan / 自检）→ 人审 → 合并
```

两类 Agent 的消费方式：

- **编程 Agent**：在本机通过 stdio 挂载 Infrastructure MCP Server 与 QMD；先查环境图与历史记忆，再读仓库，最后只产出 PR。
- **观测 Agent**：通过远端 MCP 端点只读查询 Grafana 数据源、仪表盘与告警；输出证据与结论，不直接改任何东西。Obsy 能按职责启用 MCP 服务[^1]，但接入远端端点的效果**待实测**。

### 4.2 步骤即代码

**Step 1 · GitOps 声明**（环境层）：在 `gitops` 中声明观测服务要多一个 MCP 适配器——镜像、监听端口、只读开关、凭据在 Vault 中的**引用名**。不写明文。

**Step 2 · Playbook 部署适配器**（代码层）：由 `playbooks` 下发官方 `grafana/mcp-grafana` 容器。按官方 README[^5]，相关参数为：

- `-t sse`：SSE 传输，端点为 `/sse`；`--address` 默认 `localhost:8000`，容器内需改为监听全部地址；
- `GRAFANA_URL` 指向集群内部的 Grafana 服务名，`GRAFANA_SERVICE_ACCOUNT_TOKEN` 运行时由 Vault 注入；
- 只读：官方开关是 `--disable-write`（禁用创建 / 更新类工具）[^5]；
- `--allowed-hosts`：默认只允许回环地址，传 `*` 会关闭 Host 校验，官方说明「仅在有可信反向代理校验 Host 时安全」[^5]；
- 调用方鉴权：未设 `--server-auth-token` 且监听非回环地址时，服务能启动但会记安全错误日志[^5]。本案例由网关层的 Basic Auth 承担这一职责；
- 注意：SSE 模式下请求头里的凭据不会传给工具调用，统一用服务端环境凭据[^5]——也就是所有调用方共享同一个只读服务账号。

**Step 3 · 网关精确路由**（配置层，已脱敏）：

```caddyfile
https://observability.example.com {
  basic_auth /mcp/* {
    mcp_agent {$MCP_BASIC_AUTH_PASSWORD_HASH}   # 哈希来自 Vault，运行时注入
  }
  handle_path /mcp/v1/grafana/* {
    reverse_proxy http://mcp-grafana:8000
  }
  handle_path /mcp/v1/metrics/* { reverse_proxy http://mcp-metrics:<port> }  # 规划中
  handle_path /mcp/v1/logs/*    { reverse_proxy http://mcp-logs:<port> }     # 规划中
  handle_path /mcp/v1/traces/*  { reverse_proxy http://mcp-traces:<port> }   # 规划中
  handle {
    reverse_proxy http://grafana:3000   # 兜底：Grafana Web UI 挂在根路径
  }
}
```

`handle_path` 会剥掉匹配前缀再转发，所以适配器收到的是自己的 `/sse`；Basic Auth 与观测站点共用同一套凭据，密码哈希放在 Vault。

**Step 4 · 客户端配置**（MCP 层）：远端适配器全部就绪前，本地客户端只挂两个已握手验证的组件[^6]，路径与连接串都用占位符：

```json
{
  "mcpServers": {
    "infrastructure": {
      "command": "<INSTALL_DIR>/infrastructure-mcp-server",
      "args": ["-config", "<CONFIG_DIR>/config.json"]
    },
    "qmd": {
      "command": "node",
      "args": ["<QMD_DIR>/dist/cli/qmd.js", "mcp"],
      "env": {
        "QMD_BACKEND": "pg",
        "QMD_PG_URL": "<PG_URL from Vault>"
      }
    }
  }
}
```

**Step 5 · 知识库导入**：定期把 knowledge 仓库 `docs/reference` 导入 QMD。按 Infrastructure MCP Server 仓库的说明，当前已生效的是 BM25 词法检索，向量检索需注入外部向量 API Key 后才激活[^6]。

### 4.3 回到 302：底座能不能更早发现

就绪探测脚本 `playbooks/scripts/pipeline/check-shared-readiness.sh` 访问的是 `<observability>/grafana/api/health`。而新的网关配置里，Grafana 由兜底 `handle` 挂在**根路径**，`/grafana` 前缀不再被剥离。两者放在一起看，与「`/grafana/api/health` 被 Grafana 当成未知页面跳到登录页（302）、根路径 `/api/health` 返回 200」的现象**一致**；但这只是一致，没有逐条回放网关变更时间线，**不能当作已证实的根因**。

有了底座之后，同一件事可以这样走（全部**待实测**）：

1. 网关路由变更本身走 GitOps PR；编程 Agent 审 PR 时，用 QMD 检索「哪些脚本依赖 `/grafana` 前缀」，在合并前就指出探测脚本要同步改；
2. 观测 Agent 的每日巡检通过 mcp-grafana 读健康数据，发现「根路径 200、旧前缀 302」的分裂，在流水线红灯前给出证据；
3. 修复仍由编程 Agent 起草 PR（改探测地址或恢复前缀路由二选一），人审后合并。

## 五、待实测清单（本篇发布前必须补齐）

| # | 实验 | 期望证据 | 状态 |
|---|---|---|---|
| E1 | 开启空间 AI 功能，自托管部署 1 个只读运维 Agent | Agent 列表、权限模式截图（脱敏） | 待实测 |
| E2 | 每日巡检任务：检查 Grafana 健康端点与 Gate 结果 | 固定会话中的连续报告 | 待实测 |
| E3 | 回放「302 跳登录页」场景，看 Agent 能否区分「端点挂载变化」与「服务故障」 | Agent 引用的证据列表 | 待实测 |
| E4 | 同一故障分别交给编程 Agent 与观测 Agent，记录定位耗时与人工复核耗时 | 两组计时 | 待实测 |
| E5 | 用量统计中的积分消耗 | 7 天积分曲线 | 待实测 |
| E6 | 远端 mcp-grafana（SSE + Basic Auth）分别接入编程 Agent 与 Obsy | 握手与只读工具列表 | 待实测 |
| E7 | 在 `--disable-write` 下尝试写操作，确认被拒 | 工具列表中无写工具 | 待实测 |
| E8 | QMD 检索「依赖 `/grafana` 前缀的脚本」能否命中探测脚本 | 检索结果 | 待实测 |

## 六、决策表

| 功能 | 特性 | 成本 | 客观事实依据 | 适用场景 |
|---|---|---|---|---|
| 编程 Agent 直接 debug（Codex / Claude Code / Antigravity） | 读代码、读 CI 日志、本地复现、直接产出 PR；按次介入，无历史上下文 | 订阅或 Token；需临时授予 shell/集群权限，权限边界靠人把控 | OPE 两次失败均由此路径定位：302 跳登录页、`unsupported environment` 版本锁过旧 | 根因在代码、配置、版本锁，需要改仓库的问题 |
| Obsy Agent Teams 巡检 | 基于工作空间指标/日志/链路/告警；Crontab 周期任务、固定会话、告警或 Webhook 触发、渠道投递 | 按积分计量（见用量统计）；需先接入数据；Agent 自托管 | 官方文档[^1][^2][^3]；本空间 AI 开关未开、无 Agent，效果待实测 | 持续巡检、红灯前发现趋势、夜间告警的首轮证据整理 |
| Obsy Copilot 即时问答 | 随空间提供，无需部署，结合当前页面上下文提问 | 需开启空间 AI 功能 | 官方文档[^4] | 临时查询语句生成、单次异常分析 |
| 六层底座 + MCP（代码/环境/配置/资源/知识库/MCP） | 两类 Agent 共用同一套只读工具面；凭据 Vault 运行时注入；变更只走 GitOps PR | 自建：适配器容器、网关路由、QMD 的 PostgreSQL；mcp-grafana 开源 | mcp-grafana 官方 README[^5]；Infrastructure MCP Server 与 QMD 本地握手通过[^6]；远端端点接入待实测 | 一人运维、多 Agent 并用，需要可审计的权限边界 |
| 组合：观测 Agent 发现 → 编程 Agent 修复 → 人审 PR | 只读发现与可写修复分离，各自最小权限 | 两侧成本叠加，换取更早发现与更清晰的权限边界 | 由上两行推出；组合效果待实测（E4） | 一人运维的个人 SaaS 与平台流水线 |

[^1]: 观测云文档《Obsy Agent Teams》 https://docs.guance.com/agent-teams/ ，访问于 2026-10-28。
[^2]: 观测云文档《设置中心》 https://docs.guance.com/agent-teams/settings-center/ ，访问于 2026-10-28。
[^3]: 观测云文档《自动化》 https://docs.guance.com/agent-teams/scheduled-tasks/ ，访问于 2026-10-28。
[^4]: 观测云文档《Obsy AI》 https://docs.guance.com/ai/ ，访问于 2026-10-28。
[^5]: grafana/mcp-grafana README（Usage / HTTP Transport Security / Read-Only Mode）https://github.com/grafana/mcp-grafana ，访问于 2026-10-28。
[^6]: ai-workspace-infra/Infrastructure-MCP-Server README https://github.com/ai-workspace-infra/Infrastructure-MCP-Server ，访问于 2026-10-28。
