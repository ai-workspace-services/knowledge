# XConnect Agent 配置收敛与 Free 临时白名单规划

> 2026-11-06 · 规划。现有版本已完成本地兼容基线检查和一台日本 Shared 节点的只读检查。新版实现、部署与端到端验收待执行。

## 目标与范围

将 Free 用户短期授权移到 Accounts，由 Portal 管理，Agent 通过现有同步通道应用。先在具有独立入口和绑定凭证的 Custom 节点验证授权和到期回收，再收敛边缘启动配置。两批分别交付和回滚。

| 实施仓库 | 负责内容 |
| --- | --- |
| `ai-workspace-services/accounts` | 节点管理清单、授权与审计、节点发现及订阅准入、用户快照和事件。 |
| `ai-workspace-services/portal` | 管理工作台的 Agents 标签及管理 API 代理。 |
| `ai-workspace-xstream/xconnect-edge-agent` | 旧配置兼容、五字段启动、短期授权执行与回收、节点回执。 |

**零 SQL schema 改动**是交付门槛。临时授权的持久化仅使用已存在且适合该用途的服务端存储。实施前在 Accounts 确认存储归属、跨副本一致性、并发更新和持久审计；存储通过验证后才开放写入。通过 schema 对比和启动测试确认没有 migration、新表、新列、新索引或 ORM 自动迁移。Playbooks、GitOps 和现网配置生成模板在三仓实施范围之外，主机批量切换另行交付。

## 第一批 · Free 临时白名单

### 授权与管理

- 管理员选择节点、输入邮箱、设置有效期，可新增、续期和提前撤销。默认 3 天，最长 5 天。Accounts 将邮箱解析为稳定的账号 ID，以 `nodeId + accountId` 保存授权及 UTC 到期时间，并记录操作者、操作和前后值。
- 首批只在一个独立入口的 `custom` Agent Proxy 试点。节点凭证须绑定 Agent ID 与稳定 Node ID，并验证其支持到期回收。仅符合现有账号、配额和网络隔离条件的 Free 用户可获临时授权。长期名单、既有 `customAllowFree` 规则、付费与团队用户的准入继续由现有规则决定。
- Portal 在 `/panel/management` 增加 **Agents** 标签，支持通过 `?tab=agents` 直达。按 Free、Shared、Plus、Pro、Custom 筛选，显示节点身份、健康、最近同步和授权状态。分类由 Accounts 返回。
- 管理员和运营通过现有管理入口查看。运营默认只读，写入须有单独的白名单权限。Accounts 同时校验角色、权限及节点范围。管理清单和普通用户的节点发现分别授权。
- 管理页区分「待下发」「已生效」「已到期」「已撤销」。授权到期或撤销后，若尚未收到回收回执，单独显示「待回收确认」。 [Portal 管理工作台](https://github.com/ai-workspace-services/portal/blob/351e076/src/modules/extensions/builtin/user-center/routes/management.tsx) · [Accounts 管理 API](https://github.com/ai-workspace-services/accounts/blob/30b225c7/api/admin_agents.go)

### 下发与回收

1. Accounts 用同一准入判定生成节点发现、订阅配置和现有 `/api/agent-server/v1/users` 快照，并通过 `/users/events` 通知变更。快照只为依赖本次临时授权的用户附带 `expiresAt`。用户同时具备独立准入时，保留该准入。
2. Agent 验证节点身份与快照版本，在应用前持久化回收所需的到期信息。控制面断联时按本地时钟回收，重启时先处理已过期项，避免旧快照或部分失败恢复已过期授权。状态回执以全部目标已应用为准。
3. XHTTP 和 TCP 使用已验证的单用户热增删和定向会话撤销能力。回收后目标用户的新连接被拒绝，已有会话关闭，同时其他用户的长连接持续、Xray PID 稳定。定向能力不足或任一目标失败时，记录失败并暂缓放行。
4. 在线下发和提前撤销的建议门槛为 60 秒。另验控制面断联、Agent 重启、Agent 停止而 Xray 仍运行三个场景。若最后一种场景存在过期窗口，在试点节点为同一个回收入口提供独立的本地定时触发，再验收断联到期。 [节点凭证绑定](https://github.com/ai-workspace-services/accounts/blob/30b225c7/docs/agent-node-bound-credentials.md) · [Accounts 快照和事件](https://github.com/ai-workspace-services/accounts/blob/30b225c7/api/agent_server.go) · [Xray 定向撤销](https://github.com/ai-workspace-xstream/xconnect-edge-agent/blob/6dc3dc14/internal/xrayconfig/dynamic_users.go)

## 第二批 · 五字段启动配置

`/etc/agent/account-agent.yaml` 的目标格式如下。前三项为示例占位，实际凭证沿用受控交付和最小读取权限。

```yaml
agent:
  id: ""
  controllerUrl: ""
  apiToken: ""
  syncInterval: 5m
  tls:
    insecureSkipVerify: false
```

五字段格式只负责建立受认证的控制面连接。Agent 根据绑定节点获取已登记的角色、资源类别和业务配置，匹配本地受控运行配置。Xray 模板、目标路径、执行命令和证书材料由本地运行配置管理。只有识别出完整的五字段格式、且身份和运行配置都能解析，才启动托管模式；解析失败时报错退出。现有格式继续按历史路径加载并保留环境变量优先级。 [启动入口](https://github.com/ai-workspace-xstream/xconnect-edge-agent/blob/6dc3dc14/cmd/agent/main.go) · [配置解析](https://github.com/ai-workspace-xstream/xconnect-edge-agent/blob/6dc3dc14/internal/config/config.go)

| 场景 | 验收要求 |
| --- | --- |
| 旧 YAML → 新 Agent | 原文件可直接启动。保留角色、资源类别、静态名单、同步周期、TLS、Billing、环境变量覆盖顺序和 Xray 目标行为。历史间隔按原值使用。 |
| 五字段 YAML → 新 Agent | 认证后解析角色及运行配置。Agent Proxy 保留单目标或双目标布局及对应更新方式。Gateway 和 One 保留状态上报，由原有组件管理数据面。 |
| 回滚到旧 Agent | 在重新启动前成对恢复旧制品和原 YAML。旧启动入口依赖 `mode: agent`，缺少 Xray 目标时会回退到默认单目标。 |

对照样本覆盖旧单目标、XHTTP/TCP 双目标、Gateway、One、容器和 Cloud Run。每种运行形态核对其有效角色、上报和数据面归属。历史配置文件、凭证和制品校验值由原交付路径保管。

## 五类节点独立验收

表中结果是无额外授权时的历史准入基线。每一行分别验收旧 YAML 升级、五字段启动和旧制品与原 YAML 成对回滚，并核对节点可见性、用户快照和实际连接结果。

| 节点类别 | 必测准入与隔离 |
| --- | --- |
| `free` | 显式识别为 Free；Free、Plus、Pro 用户按原规则准入。 |
| `shared` | 显式识别为 Shared；Free、Plus、Pro 用户按原规则准入。验证现有公共访问和连接持续。 |
| `plus` | Plus、Pro 准入，Free 默认拒绝。 |
| `pro` | Pro 准入，Free、Plus 默认拒绝。 |
| `custom` | 旧静态空名单拒绝。分别验证 `customAllowFree` 开启和关闭、名单内外、已有付费名单不受影响。对临时授权验证授权前、有效期内、提前撤销及到期后四个状态，并验证其他节点凭证不能取得该授权。 |

**已有基线。** Accounts 的套餐准入、节点发现、Custom 白名单与绑定节点隔离测试通过。Agent 用五类独立历史 YAML 样本与模拟控制面，均生成预期的 XHTTP 和 TCP 用户清单；Custom 覆盖 Free 开关两种状态。Agent 基线命令为 `go test ./internal/config ./internal/agentmode`。日本节点的只读检查确认类别为 Shared，两个目标运行且持续同步，历史间隔为 `10m`，TLS 校验开启。节点现有 Xray 提供定向撤销命令，配置尚未启用会话终止，因此该检查只作为 Shared 运行基线。 [Accounts 准入矩阵测试](https://github.com/ai-workspace-services/accounts/blob/30b225c7/api/resource_entitlement_matrix_test.go) · [Agent 已有配置样本测试](https://github.com/ai-workspace-xstream/xconnect-edge-agent/blob/6dc3dc14/internal/agentmode/shipped_config_test.go)

**新版证据待补。** 各类别单独记录样本、固定制品、快照或回执版本、双目标应用结果及连接探针。临时授权回收、五字段启动与成对回滚需要在隔离环境实测。核对零 schema 改动和旧节点准入一致后，才允许单节点灰度。

## 实施任务与回滚

| 任务 | 归属与退出条件 |
| --- | --- |
| T0 固定基线 | Accounts 与 Agent 确认存储和试点身份、专属凭证、双目标定向回收能力，留存可恢复的旧制品与配置。 |
| T1 交付控制面 | Accounts 增加管理清单及权限隔离，再完成授权、审计及兼容快照。旧节点按原准入路径运行。入口路径包括 `api/admin_agents.go`、`api/agent_server.go`、`api/agent_routes.go` 及订阅发现调用方。 |
| T2 交付边缘回收 | Agent 在 `internal/agentproto/`、`internal/agentmode/` 和 `internal/xrayconfig/` 完成有效期、回收和回执。双目标和断联验收通过后才启用试点写入。 |
| T3 接入管理页 | Portal 在 User Center 的 `routes/management.tsx` 接入 Agents 标签，并通过 `/api/admin/agents/` 代理 Accounts。验证管理员、运营、普通用户的允许与拒绝用例。 |
| T4 收敛启动配置 | Agent 在 `cmd/agent/`、`internal/config/` 和现有运行入口完成双格式兼容。五类节点的三条路径及 Gateway、One 的数据面隔离均通过后，交付五字段支持。 |

Accounts 负责关闭试点授权入口并停止发放，Agent 负责核验存量临时授权回收。完成回收后，再恢复旧 Agent 制品和原 YAML，确认节点身份、同步和两个 Xray 目标恢复。各仓 PR 回指同一任务，验收记录区分本地测试、环境部署和真实连接结果。
