---
title: Platform Ops Toolkit Daily Main Snapshot 实施规划
description: 按流水线、jobs、steps 关联 Action uses、Playbook Roles 与 IaC 模块，并提供固定源码基线的更新与审计工具。
slug: platform-ops-toolkit-daily-main-snapshot-plan
lang: zh
date: 2026-10-07
version: "1.1"
status: implementation-plan
tags:
  - platform-engineering
  - github-actions
  - execution-ownership
  - gitops
  - iac
category: reference
---

# Platform Ops Toolkit Daily Main Snapshot 实施规划

[技术白皮书](multi-cloud-platform-engineering-whitepaper.zh.md) · [参考资料总览](overview.zh.md) · [Python 更新脚本](../../scripts/platform_ops_snapshot_audit.py) · [人工映射与固定版本配置](../../scripts/platform_ops_snapshot_audit.json)

## 1. 范围和状态

本文把白皮书的高层职责落实到 **流水线 → jobs → steps → Action/Workflow uses → Playbook/Role → IaC 模块**。先建立 owner 能力，再切换 caller；实际运行仍由 Pipeline 编排 IaC 与 Playbooks。应用编译和制品构建继续由应用/制品仓库 CI 负责。

本规划依据 2026-10-07 的固定源码版本整理。本次仅写入 knowledge 文档和只读审计工具，没有修改基础设施执行代码、Vault、云资源、主机或数据库，也没有运行部署。本文的“验收”列是后续执行的判定条件，不是已完成记录。

| 标记 | 含义 | 不代表什么 |
| --- | --- | --- |
| 现有调用 | 源码存在调用；必须查看实际 caller 和消费 SHA | 真实环境可用或已验收 |
| 现有实现 | 在指定仓库基线找到模块、Role 或执行器 | Daily 已调用该实现 |
| 待接入 | 实现已有，owner workflow 或 caller 接入尚需调整 | 迁移已经完成 |
| 待新增 | 建议补充接口，名称和契约尚未确定 | 可直接执行的 uses |
| LEGACY | 兼容执行路径，记录目标 owner 和删除关卡 | 无效或可立即删除 |
| — | 当前步骤不需要该能力 | 需要补造一个模块来填表 |

## 2. 五层职责

共享判定源：[execution-ownership-migration/SKILL.md](https://github.com/ai-workspace-lab/xworkspace-core-skills/blob/main/skills/engineering-standards/execution-ownership-migration/SKILL.md)。

| 层 | 实施范围 | 禁止事项 |
| --- | --- | --- |
| Toolkit | 共享输入/契约校验、GitOps reader、证据校验、状态判断、放行规则 | 直接执行云资源、主机、服务或数据库操作 |
| Pipeline | Actions 入口、审批、阶段顺序、固定版本派发、运行关联、汇总 | 成为新的执行 owner，绕过 owner workflow |
| GitOps | 环境拓扑、资源参数、域名、版本、非敏感配置引用 | 执行代码、秘密值、权威运行时 CMDB |
| IaC Modules | 云资源、Registry、DNS、OS Login、临时防火墙、State、CMDB | 主机/服务/数据库操作、备份恢复、服务健康检查 |
| Playbooks Roles | 主机、服务、证书、迁移、备份恢复、诊断、健康检查 | 云资源/DNS/State 变更、权威 CMDB 生成 |

Toolkit 的 `.github/actions` 只能复用控制面逻辑。IaC 与 Playbooks owner 内部可以有自己的执行 Action；不能把执行代码放进 Toolkit Action 来规避归属。

## 3. 当前流水线与运行范围

```text
resolve-snapshot-tag
        ↓
snapshot（infra / lab / services / xstream 组织矩阵）
        ↓
resolve-built-snapshot-tag
        ↓
shared-readiness
        ↓
dispatch-environment（SIT Serverless / UAT Hybrid）
        ↓
snapshot-summary
```

| 环境/操作 | 实际入口 | 范围/条件 |
| --- | --- | --- |
| 定时 | Daily schedule | cron 为 16:00 UTC，即北京时间次日 00:00；默认 UAT |
| 手动 SIT | serverless-orchestrator.yml | web-saas |
| 手动 UAT | hybrid-orchestrator.yml | all 后由矩阵筛选，不是八条 lane 全部部署 |
| 指定 repositories | snapshot 与 summary | 当前只构建选定仓库，不进入环境部署链路 |
| XConnect 发布 | snapshot 的 repository_dispatch | 仅 xstream 分支；当前 step 不等待发布完成 |
| 普通 Daily | 无显式 XConnect One 迁移 | 不访问保护迁移源 |

| UAT lane | 当前默认行为 | IaC 映射 | Playbooks 映射 | 验收边界 |
| --- | --- | --- | --- | --- |
| open-platform | Shared 独立管理，跳过部署 | 普通 Daily 不修改 Shared | B11 目标接口；当前旧探针 | 只读 readiness |
| web-saas | Terraform + Serverless | I01、I06—I09 中适用项 | B01、B02、B06；数据操作按条件选择 | 主机、运行制品、服务和业务检查 |
| ai-workspace | deploy_on_all=false，默认 all 跳过 | 显式选中后另行展开 | 显式选中后另行展开 | 跳过原因必须保留 |
| agent-proxy-jp | AWS 资源/服务路径 | I03 | B02—B05、B07 中适用项 | JP 实例与区域入口 |
| agent-proxy-us | GCP 资源/服务路径 | I02 | B02—B05、B07 中适用项 | US 实例与区域入口 |
| agent-proxy-sg | Akamai 资源/服务路径 | I04 | B02—B05、B07 中适用项 | SG 实例与区域入口 |
| agent-proxy-tw | existing inventory/State | I05 | 当前 inventory 路径不是服务部署 | existing 资源事实 |
| agent-proxy-ph | existing inventory/State | I05 | 同上 | existing 资源事实 |

lane 表为人工规划映射，来源为 GitOps `topology/uat/hybrid/resource-matrix.json` 和 Toolkit 的 Hybrid 派发器。刷新源码后必须重新审阅此表，不由路径检查自动确认。

## 4. 按阶段实施，先 owner 后 caller

保留当前 jobs/steps 作为工作定位。每批只切换一个明确接口；provider、service、区域分别实例化，避免一次任务包办所有环境。所有状态均为**待实施**。

| 批次 | 定位 | 具体任务 | 输入 | 输出 | 验证与完成条件 | 前置/失败处理 |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Step 4.2 / B11 | 新增 Playbooks Shared 探针接口，再切换 Daily caller | endpoint、issuer、超时、环境、correlation ID | 三项探针回执、owner SHA、run ID | 成功和 sealed/issuer错误/非200/超时反例均验证；Toolkit 只判断结果 | owner 审阅固定版本先就绪；失败停止部署，保留旧副本 |
| P2 | Step 5.6 / I01—I05 | 按 provider/lane 建立 IaC plan/apply/existing/CMDB owner 接口 | GitOps SHA/资源路径、环境、账户引用、State | 资源 ID、State、CMDB、checksum、owner 回执 | 错环境/账户失败；安全重试；existing 不创建/接管；CMDB 来源可核对 | 先 GCP 一个 lane，再 AWS/Akamai/existing；无 CMDB 证据不调用主机部署 |
| P3 | Step 5.6 / B01—B07 | 将主机、证书、Agent、健康检查收敛至 Playbooks workflow | IaC CMDB、精确版本、目标、配置引用 | 主机/服务/版本/健康证据 | 语法检查、inventory身份检查、单 lane UAT 验证；不得绕过 owner | P2 可消费回执就绪；保留旧代码至新 route 验证 |
| P4 | Step 5.6 / I06—I09、B10 | 拆开制品晋级、Cloud Run/Cloudflare 资源发布与数据库操作 | digest/package checksum、声明、数据库操作契约 | revision/deployment ID、实际 digest、DB 回执 | owner 各自验证；数据库写入有 release checkpoint/恢复演练/schema/hash门槛；复用现有域名接口 | 各 owner 接口先就绪；禁止把源码重建当成 digest 晋级 |
| P5 | Jobs 1—6 | 固定版本、补齐参数传递和运行关联，复用控制面 Action | 固定 Toolkit/GitOps/IaC/Playbooks/app SHA、制品身份 | 版本锁、精确 child run、完整终态汇总 | 两个 XConnect tag 输入实际消费或明确拒绝；发布 child 可关联；失败/取消/超时都有 summary；必需跳过不放行 | 不新增执行 owner；OIDC 精确 workflow allowlist 和权限先对齐 |
| P6 | owner/caller 新 route | 验证新路径，最后删除 LEGACY 副本 | 固定版本、UAT运行证据、旧调用清单 | owner实现、caller diff、验证、旧副本删除四份证据 | 单 lane 后完整集合验收；删除后查无旧调用；实际 release/tag/env/target 可追溯 | 验证失败保留旧副本，恢复上一个已审阅 caller ref；无静默回退 |

### 4.1 PROD Selfhost 主库迁移：依赖由下至上验证

迁移的业务目标链路保持不变，但实施顺序必须反过来：先完成最底层依赖和 owner 回执，再允许上一级消费它。聚合流水线是最后一公里的 caller 和证据汇总器，不是第一调试入口。任一层失败时，先在该层的固定 owner、隔离环境或 Playbooks Role 中修复，再以相同输入重跑；不得用上层 job 成功、静态 plan 或单次探针代替下层证据。

```text
身份/输入
  ↓
IaC 资源与 CMDB
  ↓
Selfhost PostgreSQL 与应用运行时
  ↓
53 表 schema 初始化
  ↓
PROD Supabase 只读合同
  ↓
migratectl 全业务复制与比对
  ↓
停写、最终追平、单写者
  ↓
Edge Gateway/CNAME 切换
  ↓
业务验收与可审计回退
```

按以下门槛逐层推进；后一个门槛未通过时，主库仍保持 PROD Serverless，禁止提前切换入口：

| 层级 | 先验证的最小依赖 | 执行 owner | 必须保留的证据 | 放行到下一层的条件 |
| --- | --- | --- | --- | --- |
| L0 身份/输入 | GitHub OIDC、Vault 路径、固定源码和制品身份；输入的环境、项目、区域、域名互相匹配 | Toolkit 控制面 + IaC | 输入摘要、固定 SHA/digest、OIDC job 身份 | 输入合同可重放且无明文凭据 |
| L1 资源/CMDB | `open-platform-prod` 资源、私网访问、OS Login、删除保护、独立数据盘和 CMDB 记录 | IaC Modules | apply/plan 回执、资源 ID、State lineage、CMDB checksum | 目标主机可被受控 Playbooks 身份访问 |
| L2 主机/运行时 | Selfhost PostgreSQL 版本、磁盘、网络、应用运行角色；先做 standby/无 DB 连接探针 | Playbooks Roles | 主机身份、运行时 digest、健康和清理回执 | 目标库可访问且未发生业务写入 |
| L3 schema | 53 表最新 schema 初始化；只允许空库初始化，不回放历史、不 reset/drop | Playbooks DB owner | SQL/版本/hash、迁移前后 schema 摘要、目标为空证明 | 表、列、约束、索引和触发器达到固定版本 |
| L4 来源合同 | Vault `kv/data/prod/database-upgrade/PROD_SUPABASE_READONLY_DSN`；session pooler/TLS；连接级与事务级只读 | Playbooks `serverless_supabase` owner | 脱敏连接指纹、角色、TLS、只读反例（写入被拒） | 只读合同有效，且不把管理员凭据写入文件或 artifact |
| L5 复制/比对 | `migratectl` 全业务 53 表复制；按 email 映射用户，保持 PROD email、Proxy UUID、身份、订阅、额度、账本；再做全字段/行数/摘要/FK 比对 | Accounts migratectl + Playbooks Role | copy/compare receipt、表级摘要、映射统计、失败表清单 | 复制成功且一致性报告无未解释差异；源仍为只读 |
| L6 切换前门槛 | 来源全写者冻结、最终追平窗口、目标单写者和回退点 | 迁移 owner + Edge Gateway owner | 冻结时间、最终追平水位、单写者租约、回退演练 | 新鲜度在约定窗口内，且切换批准明确记录 |
| L7 入口/验收 | Accounts 与 Billing 同步切换；`accounts.svc.plus`、`billing.svc.plus` 由 Worker/CNAME 指向模式别名；主页和 console 保持原职责 | Edge Gateway/CNAME owner + 业务验收 | DNS/Worker 版本、请求探针、账单/账户关键流程、回退记录 | 生产入口验收通过；失败时按目标是否产生新写入选择有证据的回退 |

实施约束：

1. L1—L5 直接由 IaC/Playbooks/DB owner 调试，允许受控 SSH 作为 Role 的传输通道，但不建立绕过 Role 的手工 `psql` 或本地脚本执行路径；凭据只从 Vault 运行时注入，绝不写入聊天、Git 或 artifact。
2. 聚合流水线只负责校验输入、派发固定 owner、等待、关联 run/artifact 和判断门槛。它不复制业务数据、不生成 schema、不自行修复主机；owner 回执缺失时流水线必须失败而不是猜测成功。
3. L5 的时点比对不是 L6 的最终一致性证明。只有完成停写、最终追平和单写者证据，才允许进入 L7；在此之前任何 `edge-gateway`、CNAME 或生产主库标记都不得切换。
4. 每层都要保存可审计的原始回执和脱敏摘要，并记录固定 SHA、镜像 digest、目标环境、时间窗和回退点。失败重试必须复用同一版本和输入，避免“换版本重试”掩盖真实原因。

截至 2026-10-07，资源、运行时资格和 schema/Billing owner 检查已有固定版本；基线复制已完成，但最终追平、单写者、网关切换和生产验收尚未完成。最近一次完整业务 preview（run `37578640206`）已通过输入、OIDC、Vault 和 IaC 访问门槛，但在 Playbooks owner 执行阶段失败；私密输出已清理，因此不能把这次失败解释成数据差异。

### 4.2 主机 owner 实测与来源投影检查点

2026-10-07 已通过 IaC 固定 owner 的临时 `/32` 访问，直接 SSH 执行 Playbooks 只读诊断：目标 PostgreSQL 为 `170010`，业务表数为 53，checkpoint 为 `2026100701:false`，运行中的受管应用写者为 0。访问结束后已撤销临时防火墙和 OS Login 密钥。此结果证明目标运行时和 schema 元数据就绪。

[Playbooks #606](https://github.com/ai-workspace-infra/playbooks/pull/606) 修正来源指纹参数并提供脱敏失败阶段；[#607](https://github.com/ai-workspace-infra/playbooks/pull/607) 请求迁移来源连接 `default_transaction_read_only=on`，并拒绝覆盖该请求的启动选项。两项已合并、隔离 PG17 资格通过。实际 Supabase pooler 未应用此启动参数，因此不能单凭连接串证明默认只读。[Accounts #201](https://github.com/ai-workspace-services/accounts/pull/201) 已合并并通过隔离 PG17 资格，在显式只读事务内设置并核验两个只读状态；实际来源探针证明只读状态生效，rollback 后恢复原连接默认值。正式 Accounts 镜像为 `ghcr.io/ai-workspace-services/accounts:sha-072703033a4038c4025e30043d37c89d4ee3d8c0`，digest `sha256:065615850056aee3fd492f52b6cd383dd29fa0b94ac8cde11cf0e871712909db`，main 发布 run `37582769808` 成功。

来源目录的只读比对定位出两类投影差异，其余现有业务表未发现字段增减或类型差异：

| 来源旧结构 | 最新目标结构与处理 | 证据与状态 |
| --- | --- | --- |
| `users` 缺少 `subscription_valid_from`、`subscription_valid_until`、`last_active_at`、`archived_at` | 只对不存在的四个可空字段使用 `2026091301` 的原生 NULL 默认值；保留已有字段值、订阅表及额度/账本 | [Accounts #199](https://github.com/ai-workspace-services/accounts/pull/199) 已合并；正式 main 镜像 run `37580615861` 成功；用户/Proxy UUID 映射规则保持原样 |
| `email_blacklist` 以 email 为主键，没有 UUID | 校验来源主键确为 email；按原始 email 精确字节推导稳定 UUIDv5，复制/比对使用同一投影；保留 email、创建时间和已有 UUID | [Accounts #200](https://github.com/ai-workspace-services/accounts/pull/200) 已合并，main 发布 run `37582062962` 成功；固定新镜像的真实全业务基线复制已完成 |

目标始终使用完整最新 schema。来源投影须明确列举并经过 owner 资格验证，不通过修改 PROD schema、丢弃业务字段或放宽所有缺失字段来解除失败。

2026-10-07 06:54–06:56 UTC 的基线复制回执证明将来源 44 张表投影到 Selfhost 最新 53 表 schema，24 个用户和 382,312 条业务记录完成一次单向复制，其中 `billing_ledger` 为 179,783 行。该快照中的 `full_business_equal=true`，但 `source_writers_paused=false`、`final_catchup_complete=false`、`database_cutover_approved=false`。它是运行期间快照，不是最终追平证明。随后通过来源只读事务和目标只读事务，按 email 排序，对 24 个用户的 email、password hash、Proxy UUID 计算长度前缀 SHA-256 摘要；双方用户数为 24，摘要相同（`7b10ac27bd520f2876d65b76b3c0161e30a7039f83f9b13c0be3cd919db503fc`），临时 SSH 访问已撤销。该检查证明这三个核心字段在该时点一致，不证明其他业务表一致、来源已停写或具备切库条件。之后单独全业务 compare 未生成有效回执，失败时没有输出表级差异，不能据此判定是数据不一致。

部署与数据入口的能力边界也已实测：`selfhost-orchestrator.yml` 的 release-tag 路由可解析为 PROD `web-saas`、Terraform apply 和应用部署，`dns_mode=none` 保持域名路由不变；工作流包含主机 bootstrap、`roles/vhosts` 配置、GitOps tag 更新及 Doco-CD 部署/验收步骤。定向 dispatch 合同测试通过，但这是路由与合同验证，尚未真实执行 PROD 部署，也未证明指定 tag 的所有应用镜像均可拉取。

`environment-data-operations.yml` 当前没有 PROD 全业务复制/同步模式：`legacy_import`、`migrate` 和 `selfhost_init` 被限制在 UAT，PROD Selfhost 支持的是 probe/verify 等既有操作；`selfhost_verify` 验证发布后运行状态和既存基线，不会从 Supabase 复制数据。Toolkit PROD 环境当前 `prevent_self_review=false`，而请求校验器要求其为 `true`，所以 PROD data-operations dispatch 会在取 Vault 凭据前被拒绝。现有全业务 copy/compare 仍在 `selfhost-orchestrator.yml` 的独立操作中。若后续统一从 data-operations 派发数据同步，需先在 Playbooks owner 建立并隔离资格验证对应的全业务操作，再以固定 owner SHA 接入 caller；不能把当前 selfhost_verify 当作同步证明。

切换前须冻结全部来源写者并完成最终追平、全业务比对和单写者证据。Selfhost 尚未产生新写入时可以按已验证路由恢复 Serverless；一旦产生新写入，禁止直接返回旧 Supabase。此时保留维护态或使用同一 Selfhost 主库的应用版本回退；需要返回旧源时，必须另有获批的追平与重新比对合同。当前单向复制授权不包含反向写回源库。

## 5. 待调用的 uses 接口

Action 放在 `steps[*].uses`；reusable workflow 放在 `jobs.<job>.uses`。Role 由 Playbooks owner 内部调用。下表为接入规划，不自动代表实际调用；实际 uses 在自动生成区列出。

| 接入点 | uses 目标 | 状态/约束 |
| --- | --- | --- |
| Cloudflare 域名 owner | ai-workspace-infra/iac_modules/.github/workflows/cloudflare-serverless-domains.yml@a7ac40fb0c3e620bdec89edd72b172afefc1f2ee | 已有固定 SHA 调用；复用而不是再造 |
| Web SaaS CD | ai-workspace-infra/playbooks/.github/workflows/web-saas-domain-cd.yaml@main | 现有但待固定 SHA；主要验证/观察 pull-only 交付，不等于执行全部部署 |
| Selfhost 数据生命周期 | ai-workspace-infra/playbooks/.github/workflows/selfhost-data-lifecycle.yml@<审阅SHA> | owner 现有；caller 按具体数据链路对齐 |
| Serverless 数据库 | ai-workspace-infra/playbooks/.github/workflows/serverless-database-operations.yml@<审阅SHA> | owner 现有；继续复用并固定版本 |
| Shared readiness | Playbooks reusable workflow，名称未确定 | 待新增 |
| provider plan/apply/CMDB | IaC reusable workflow，名称未确定 | 待接入 owner 接口 |
| Cloud Run/Worker/Pages | IaC reusable workflow，名称未确定 | 待接入 owner 接口 |
| 重复输入校验/派发/等待/证据校验 | Toolkit .github/actions/<name>，名称未确定 | 先搜索现有能力；只封装控制面，并有契约测试 |

`<审阅SHA>` 和 `<name>` 都是规划占位符，不能直接执行。新 caller 启用前检查 owner/caller、资源副作用、固定 SHA、证据来源和精确 `job_workflow_ref` 信任。

## 6. 更新与审计

### 6.1 文件分工

| 文件 | 内容 | 更新方式 |
| --- | --- | --- |
| 本文自动生成区 | 固定 SHA、jobs、steps、实际 uses、映射路径检查、规则计数 | Python 生成；不要手工编辑区内内容 |
| 本文其他章节 | 运行范围、实施阶段、接入规划、验收/删除关卡 | 人工审阅维护；脚本保留 |
| scripts/platform_ops_snapshot_audit.json | 初始固定 SHA、扫描范围、step 输出注释、Role/IaC 映射 | 人工维护；新增 step/路径会提示失效或未映射 |
| platform-ops-toolkit-daily-main-snapshot/tables.md | 独立生成的详细表格 | Python 生成 |
| platform-ops-toolkit-daily-main-snapshot/audit.md | 带固定版本源码链接的审计明细 | Python 生成 |
| platform-ops-toolkit-daily-main-snapshot/audit.json | 基线、jobs、uses、字面调用边、路径检查、候选、源文件 hash | Python 生成，便于查询和比较 |

### 6.2 运行方式

在 knowledge 仓库根目录执行。需要 Python 3.9+、Git 和 PyYAML；建议使用独立 Python 环境。默认读取四仓已提交的 Git 对象，忽略未提交工作目录，不读取运行时凭据，不 checkout，不派发 workflow，不执行源码里的命令。

```bash
# 一次性准备独立环境
python3 -m venv /tmp/knowledge-snapshot-audit-venv
/tmp/knowledge-snapshot-audit-venv/bin/python -m pip install 'PyYAML>=6,<7'

# 按登记的固定 SHA 更新全部表格/报告，只替换本文自动生成区
/tmp/knowledge-snapshot-audit-venv/bin/python scripts/platform_ops_snapshot_audit.py \
  --document docs/reference/platform-ops-toolkit-daily-main-snapshot-plan.zh.md

# 复现检查：无写入；报告/文档漂移或 error 返回非零
/tmp/knowledge-snapshot-audit-venv/bin/python scripts/platform_ops_snapshot_audit.py \
  --document docs/reference/platform-ops-toolkit-daily-main-snapshot-plan.zh.md --check

# 获取四仓远端 main，冻结 SHA 并更新登记基线及报告
# 只 fetch；不改变各仓工作目录/分支。人工规划章节仍需审阅。
/tmp/knowledge-snapshot-audit-venv/bin/python scripts/platform_ops_snapshot_audit.py \
  --refresh-main --update-lock \
  --document docs/reference/platform-ops-toolkit-daily-main-snapshot-plan.zh.md

# 对一个候选 commit 做独立审计，不覆盖已保存规划/基线
/tmp/knowledge-snapshot-audit-venv/bin/python scripts/platform_ops_snapshot_audit.py \
  --ref platform-ops-toolkit=<完整SHA> --output-dir /tmp/toolkit-candidate-audit

# 其他目录布局可指定基础设施仓库父目录
python3 scripts/platform_ops_snapshot_audit.py --infra-root /path/to/ai-workspace-infra

# 运行工具自身的离线契约测试
python3 -m unittest discover -s scripts/tests -p 'test_platform_ops_snapshot_audit.py'
```

默认报告目录为本文同级的 `platform-ops-toolkit-daily-main-snapshot/`。`--refresh-main` 不带 `--update-lock` 只做新基线预览；下一次默认运行仍回到登记 SHA。`--update-lock` 与 `--check` 互斥。

### 6.3 退出码与审计边界

| 分类 | 行为/含义 |
| --- | --- |
| 退出码 0 | 指定版本读取/生成成功且未触发所选门槛；不代表部署合规或 UAT通过 |
| 退出码 1 | --check 发现漂移，或命中 --fail-on 门槛 |
| 退出码 2 | 配置、Git、YAML、文件读写等运行错误 |
| 默认 --fail-on error | 缺失 workflow/Action/现有映射路径、失效人工 step/job 映射阻断 |
| --fail-on warning | 另外阻断浮动 owner ref、未引用输入、未映射新 step/job 等 |
| EXECUTION_CANDIDATE / review | 命令词静态候选；可能是注释以外的字符串/测试，不能自动认定违规；需要检查最终副作用 |
| OWNER_REF_UNVERIFIED | 本地没有实际消费 SHA 的对象；不能拿 owner main 代替证明；补充该对象后重跑 |
| 调用图范围 | workflow_scope 人工登记 + 字面本地脚本/Action追踪；动态 shell/Python路径、运行时矩阵及外部调用不保证完整 |
| 分支范围 | 下游 workflow 包含条件/PROD分支；被扫描不意味着 Daily 执行；逐步查看 if 与实际输入 |
| 映射范围 | Role/模块表只验证固定版本路径存在；人工登记的 owner/接入状态和 lane 筛选仍需评审 |
| 安全范围 | 输出不包含原始 env/with/run 代码或运行时 token；候选保留类别/源码位置；工具不读取 Vault |

```bash
# 示例：查询浮动 owner 引用，或比较两个固定版本报告
python3 - <<'PY'
import json
from collections import Counter
from pathlib import Path
p = Path('docs/reference/platform-ops-toolkit-daily-main-snapshot/audit.json')
r = json.loads(p.read_text())
print(Counter(f['code'] for f in r['findings']))
for f in r['findings']:
    if f['code'] == 'FLOATING_OWNER_REF':
        print(f['path'], f['detail'])
PY
```

## 7. 汇总产物与关键缺口

| 汇总项 | 当前产物/行为 | 能证明什么 | 待补 |
| --- | --- | --- | --- |
| 统一版本 | snapshot_tag | 快照标识 | 固定各仓 SHA 和实际制品 digest |
| 组织构建 | daily-snapshot-status-<organization> | 构建状态 | 必需制品缺失要失败 |
| 构建总览 | daily-snapshot-summary.json | 构建集合 | 完整/选择性构建区分 |
| Shared | 探针日志和退出状态 | 服务探测结果 | Playbooks owner 回执、身份和时间 |
| 环境派发 | environment-dispatch-<environment> | 环境/tag/子运行/结果 | owner SHA 与运行证据关联 |
| 部署汇总 | environment-dispatch-summary.json | 子流水线结果 | 部署完成与业务验收分开 |
| XConnect 发布 | repository_dispatch | 请求提交 | 精确发布运行、等待、制品验收 |
| summary 失败路径 | 部分失败时 job 跳过 | 成功路径汇总 | 失败/取消/超时完整终态 |
| 两个 XConnect release tag 输入 | 入口定义存在 | 接收参数 | 当前未继续传递，需消费或明确拒绝 |

<!-- BEGIN GENERATED DAILY SNAPSHOT AUDIT -->

## 自动生成：流水线与调用盘点

证据等级：**源码盘点**。人工映射的路径存在检查不等于调用、运行或业务验收。

| 仓库 | 固定 SHA |
| --- | --- |
| platform-ops-toolkit | `feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8` |
| playbooks | `2dd12e6e12ce8b0b07bdae8290f96257fde67f07` |
| iac_modules | `c128442c35024f75bcd9f9cb771dc882d9d4d2ed` |
| gitops | `437014ff401e7a0a122725945c093a71ab756dd1` |

| 流水线 | 触发 | jobs | steps 定义 | 输出 |
| --- | --- | --- | --- | --- |
| [Daily Main Snapshot](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/daily-main-snapshot.yaml) | schedule、workflow_dispatch; cron=['0 16 * * *'] | 6 | 33 | 构建状态、环境派发回执、最终汇总 |

### Jobs 汇总

| Job | 任务 | 依赖 | 输入 | 源码 outputs | 结果／制品 | 条件 | 矩阵 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| resolve-snapshot-tag | 确定统一快照 tag | — | deploy_env、snapshot_tag、snapshot_source_ref、repositories | {"snapshot_tag": "${{ steps.resolve.outputs.snapshot_tag }}"} | snapshot_tag | — | — |
| snapshot | 按组织创建 tag、构建并记录状态 | resolve-snapshot-tag | 统一 tag、源码 ref、构建清单、组织矩阵 | — | daily-snapshot-status-<organization> | — | {"organization": ["ai-workspace-infra", "ai-workspace-lab", "ai-workspace-services", "ai-workspace-xstream"]} |
| resolve-built-snapshot-tag | 确认完成的统一版本 | ["resolve-snapshot-tag", "snapshot"] | 各组织状态 artifact | {"snapshot_tag": "${{ steps.resolve.outputs.snapshot_tag }}"} | 完成的 snapshot_tag | ${{ always() && needs.resolve-snapshot-tag.result == 'success' && needs.snapshot.result == 'success' && (inputs.repositories &#124;&#124; '') == '' }} | — |
| shared-readiness | 检查 Shared 服务 | resolve-built-snapshot-tag | Vault/Grafana/IAM endpoint、issuer、超时 | — | readiness 成功/失败 | ${{ always() && needs.resolve-built-snapshot-tag.result == 'success' }} | — |
| dispatch-environment | 读取 GitOps，派发并等待环境部署 | ["resolve-built-snapshot-tag", "shared-readiness"] | 完成的 tag、环境、GitOps topology | — | run_url、environment-dispatch-<environment> | ${{ always() && needs.resolve-built-snapshot-tag.result == 'success' && needs.shared-readiness.result == 'success' && (inputs.repositories &#124;&#124; '') == '' && matrix.environment == (inputs.deploy_env &#124;&#124; 'uat') }} | {"include": [{"environment": "sit", "name": "Serverless Orchestrator", "operation": "deploy", "target_domains": "web-saas", "topology_mode": "serverless", "workflow": "serverless-orchestrator.yml"}, {"environment": "uat", "name": "Hybrid Orchestrator", "operation": "deploy", "target_domains": "all", "topology_mode": "hybrid", "workflow": "hybrid-orchestrator.yml"}]} |
| snapshot-summary | 汇总构建及环境派发 | ["resolve-snapshot-tag", "snapshot", "resolve-built-snapshot-tag", "shared-readiness", "dispatch-environment"] | 组织状态、环境派发回执 | — | daily-snapshot-summary.json、environment-dispatch-summary.json、Actions Summary | ${{ always() && needs.resolve-snapshot-tag.result == 'success' && needs.snapshot.result != 'skipped' && needs.resolve-built-snapshot-tag.result != 'failure' && needs.shared-readiness.result != 'failure' && needs.dispatch-environment.result != 'failure' }} | — |

### Steps 关联汇总

#### 1. `resolve-snapshot-tag`

| Step | 任务 | Action uses／脚本 run | Playbook／Role | IaC | 输出／验证 | 条件 |
| --- | --- | --- | --- | --- | --- | --- |
| 1.1 | Checkout repository | uses: `actions/checkout@v7` | — | — | 工作目录和控制脚本可用 | — |
| 1.2 | Load GitHub App private key from Vault | uses: `hashicorp/vault-action@v4` | — | — | 运行时授权成功；不持久化或输出私钥 | — |
| 1.3 | Create GitHub App installation token for infra | uses: `actions/create-github-app-token@v3` | — | — | infra 组织访问权限 | — |
| 1.4 | Create GitHub App installation token for lab | uses: `actions/create-github-app-token@v3` | — | — | lab 组织访问权限 | — |
| 1.5 | Create GitHub App installation token for services | uses: `actions/create-github-app-token@v3` | — | — | services 组织访问权限 | — |
| 1.6 | Create GitHub App installation token for xstream | uses: `actions/create-github-app-token@v3` | — | — | xstream 组织访问权限 | — |
| 1.7 | Resolve snapshot tag across all organizations | run: [.github/scripts/snapshots/resolve-snapshot-tag.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/snapshots/resolve-snapshot-tag.sh) | — | — | 输出合法统一 tag；范围/环境不符时停止 | — |

#### 2. `snapshot`

| Step | 任务 | Action uses／脚本 run | Playbook／Role | IaC | 输出／验证 | 条件 |
| --- | --- | --- | --- | --- | --- | --- |
| 2.1 | Checkout repository | uses: `actions/checkout@v7` | — | — | 工作目录和控制脚本可用 | — |
| 2.2 | Load GitHub App private key from Vault | uses: `hashicorp/vault-action@v4` | — | — | 运行时授权成功；不持久化或输出私钥 | — |
| 2.3 | Create GitHub App installation token | uses: `actions/create-github-app-token@v3` | — | — | 当前组织权限 | — |
| 2.4 | Create cross-repository main snapshot | run: [.github/scripts/snapshots/tag-daily-main-snapshot.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/snapshots/tag-daily-main-snapshot.sh) | — | — | tag、构建结果和制品状态可关联 | ${{ inputs.repositories == '' &#124;&#124; contains(inputs.repositories, matrix.organization) }} |
| 2.5 | Trigger XConnect multi-platform release | run: gh api repository_dispatch（仅 xstream） | — | — | 仅证明 repository_dispatch 已提交；未等待发布完成 | ${{ success() && matrix.organization == 'ai-workspace-xstream' }} |
| 2.6 | Upload snapshot status | uses: `actions/upload-artifact@v7` | — | — | 组织状态 artifact；失败时也尝试上传 | always() |

#### 3. `resolve-built-snapshot-tag`

| Step | 任务 | Action uses／脚本 run | Playbook／Role | IaC | 输出／验证 | 条件 |
| --- | --- | --- | --- | --- | --- | --- |
| 3.1 | Checkout repository | uses: `actions/checkout@v7` | — | — | 工作目录和控制脚本可用 | — |
| 3.2 | Download all organization snapshot status artifacts | uses: `actions/download-artifact@v8` | — | — | 组织状态集合完整 | — |
| 3.3 | Resolve immutable completed snapshot tag | run: [.github/scripts/snapshots/resolve-daily-snapshot-tag.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/snapshots/resolve-daily-snapshot-tag.sh) | — | — | 解析完成的统一 tag；指定 repositories 时跳过 | — |

#### 4. `shared-readiness`

| Step | 任务 | Action uses／脚本 run | Playbook／Role | IaC | 输出／验证 | 条件 |
| --- | --- | --- | --- | --- | --- | --- |
| 4.1 | Checkout repository | uses: `actions/checkout@v7` | — | — | 工作目录和控制脚本可用 | — |
| 4.2 | Check Shared platform readiness (read-only) | run: [.github/scripts/snapshots/check-shared-readiness.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/snapshots/check-shared-readiness.sh) | B11 待新增 owner 接口；当前仍执行 Toolkit 探针 | — | Vault initialized 且 unsealed；Grafana DB ok；IAM issuer 匹配 | — |

#### 5. `dispatch-environment`

| Step | 任务 | Action uses／脚本 run | Playbook／Role | IaC | 输出／验证 | 条件 |
| --- | --- | --- | --- | --- | --- | --- |
| 5.1 | Checkout repository | uses: `actions/checkout@v7` | — | — | 工作目录和控制脚本可用 | — |
| 5.2 | Load GitHub App private key from Vault | uses: `hashicorp/vault-action@v4` | — | — | 运行时授权成功；不持久化或输出私钥 | — |
| 5.3 | Create GitHub App installation token | uses: `actions/create-github-app-token@v3` | — | — | 读取 GitOps 和派发权限 | — |
| 5.4 | Checkout selected GitOps topology | uses: `actions/checkout@v7` | — | — | 获得对应环境和模式的拓扑 | — |
| 5.5 | Resolve target domain from GitOps | run: [.github/scripts/snapshots/resolve-dispatch-gitops-target.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/snapshots/resolve-dispatch-gitops-target.sh) | — | — | target_domain_base；环境和模式校验 | — |
| 5.6 | Dispatch ${{ matrix.name }} | run: [.github/scripts/snapshots/dispatch-environment-combined.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/snapshots/dispatch-environment-combined.sh) | B01—B10 下游条件调用 | I01—I09 下游条件调用 | 精确子运行 URL、终态、环境和 tag；按目标选择执行 | — |
| 5.7 | Write dispatch receipt | run: jq 写脱敏派发回执 | — | — | 环境、操作、workflow、tag、run_url、结果 | always() |
| 5.8 | Upload dispatch receipt | uses: `actions/upload-artifact@v7` | — | — | 环境回执 artifact | always() |

#### 6. `snapshot-summary`

| Step | 任务 | Action uses／脚本 run | Playbook／Role | IaC | 输出／验证 | 条件 |
| --- | --- | --- | --- | --- | --- | --- |
| 6.1 | Checkout repository | uses: `actions/checkout@v7` | — | — | 工作目录和控制脚本可用 | — |
| 6.2 | Download all organization snapshot status artifacts | uses: `actions/download-artifact@v8` | — | — | 构建状态集合 | — |
| 6.3 | Publish unified snapshot matrix summary | run: [.github/scripts/snapshots/aggregate-daily-snapshot-status.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/snapshots/aggregate-daily-snapshot-status.sh) | — | — | 构建汇总 JSON 和 Actions Summary | — |
| 6.4 | Download environment dispatch receipts | uses: `actions/download-artifact@v8` | — | — | 部署未跳过时获得回执 | ${{ needs.dispatch-environment.result != 'skipped' }} |
| 6.5 | Publish environment dispatch summary | run: [.github/scripts/snapshots/aggregate-environment-dispatch-status.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/snapshots/aggregate-environment-dispatch-status.sh) | — | — | 环境派发汇总 JSON | ${{ needs.dispatch-environment.result != 'skipped' }} |
| 6.6 | Upload environment snapshot summary | uses: `actions/upload-artifact@v7` | — | — | daily-snapshot-summary-<environment> artifact | always() |
| 6.7 | Fail when the selected environment dispatch failed | run: exit 1 | — | — | 失败状态；当前外层 job 条件会阻止部分失败路径进入汇总 | ${{<br>  needs.snapshot.result == 'failure' &#124;&#124;<br>  needs.shared-readiness.result == 'failure' &#124;&#124;<br>  needs.dispatch-environment.result == 'failure'<br>}} |

### 下游 workflow 范围（人工登记，非全链路可达性证明）

| 路径 | 用途 |
| --- | --- |
| [.github/workflows/daily-main-snapshot.yaml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/daily-main-snapshot.yaml) | Daily 入口、构建、readiness、派发和汇总 |
| [.github/workflows/hybrid-orchestrator.yml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/hybrid-orchestrator.yml) | UAT 矩阵编排；并非所有 lane 都执行 |
| [.github/workflows/selfhost-orchestrator.yml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/selfhost-orchestrator.yml) | 资源、CMDB、主机和服务交付；含 Daily 不使用的 PROD 条件分支 |
| [.github/workflows/serverless-orchestrator.yml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/serverless-orchestrator.yml) | SIT/UAT Serverless；含其他操作与环境分支 |
| [.github/workflows/external-inventory-state.yml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/external-inventory-state.yml) | TW/PH existing inventory / State 路径 |
| [.github/workflows/xconnect-zero-cloud.yaml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/xconnect-zero-cloud.yaml) | 显式迁移分支；普通 Daily 不启用 |
| [.github/workflows/environment-data-operations.yml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/environment-data-operations.yml) | 数据操作薄调用与 owner workflow 接入 |
| [.github/workflows/environment-upgrade-ci.yml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/environment-upgrade-ci.yml) | 数据升级/rehearsal 调用入口 |

### 下游 Role／IaC 映射（人工登记 + 固定版本路径检查）

| ID | 任务 | Owner | 入口／实现 | 目标接入状态 | 输入 | 输出／验证 | 路径检查 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| I01 | GCP Web SaaS 主机/网络/数据盘 | IaC Modules | [iac_modules/terraform-hcl-standard/gcp-cloud/modules/project](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/project)<br>[iac_modules/terraform-hcl-standard/gcp-cloud/modules/network](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/network)<br>[iac_modules/terraform-hcl-standard/gcp-cloud/modules/spot_vm](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/spot_vm)<br>[iac_modules/terraform-hcl-standard/gcp-cloud/modules/persistent_data_disk](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/persistent_data_disk) | 模块现有；待 owner workflow 接入 | GitOps resources/onwalk.net/uat/gcp/web-saas.yaml、环境、账户、State | 资源 ID、State、CMDB；与目标声明一致 | 路径存在；不证明调用 |
| I02 | GCP US Agent Proxy | IaC Modules | [iac_modules/terraform-hcl-standard/gcp-cloud/modules/project](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/project)<br>[iac_modules/terraform-hcl-standard/gcp-cloud/modules/network](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/network)<br>[iac_modules/terraform-hcl-standard/gcp-cloud/modules/spot_vm](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/spot_vm) | 模块现有；待 owner workflow 接入 | US lane 声明、账户、State | US 实例身份、网络、CMDB | 路径存在；不证明调用 |
| I03 | AWS JP Agent Proxy | IaC Modules | [iac_modules/terraform-hcl-standard/aws-cloud/modules/ec2](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/aws-cloud/modules/ec2)<br>[iac_modules/terraform-hcl-standard/aws-cloud/modules/spot_ec2](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/aws-cloud/modules/spot_ec2) | 当前 JP on-demand 用 ec2；Spot 声明才用 spot_ec2；待 owner workflow 接入 | JP lane 声明、AWS 身份、State | JP 实例、地址、CMDB | 路径存在；不证明调用 |
| I04 | Akamai SG Agent Proxy | IaC Modules | [iac_modules/terraform-hcl-standard/akamai-cloud/modules/compute](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/akamai-cloud/modules/compute)<br>[iac_modules/terraform-hcl-standard/akamai-cloud/modules/storage](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/akamai-cloud/modules/storage)<br>[iac_modules/terraform-hcl-standard/akamai-cloud/templates/hosts.tf.j2](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/akamai-cloud/templates/hosts.tf.j2) | compute 现有；storage 条件使用；防火墙由模板生成；待 owner workflow 接入 | SG lane 声明 | SG 实例、防火墙、CMDB | 路径存在；不证明调用 |
| I05 | TW/PH existing 资源事实 | IaC Modules | [platform-ops-toolkit/scripts/iac/write_external_inventory.py](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/scripts/iac/write_external_inventory.py)<br>[platform-ops-toolkit/.github/workflows/external-inventory-state.yml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/external-inventory-state.yml) | LEGACY Toolkit 执行；待迁入 IaC；不创建外部主机 | existing 声明、环境、账户、State | existing inventory/State；不等于服务部署 | 路径存在；不证明调用 |
| I06 | Registry 基础资源/制品晋级 | IaC Modules | [iac_modules/terraform-hcl-standard/gcp-cloud/modules/artifact_registry](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/artifact_registry)<br>[iac_modules/scripts/pipeline/artifact-registry-promote.sh](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/scripts/pipeline/artifact-registry-promote.sh)<br>[iac_modules/scripts/pipeline/artifact-registry-wait.sh](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/scripts/pipeline/artifact-registry-wait.sh) | 现有脚本由 Toolkit 调用；待 owner workflow 接入 | 源 digest、目标 Registry、环境 | 目标 digest 可核对 | 路径存在；不证明调用 |
| I07 | Cloud Run 单服务部署 | IaC Modules | [iac_modules/terraform-hcl-standard/gcp-cloud/modules/cloud_run](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/cloud_run)<br>[platform-ops-toolkit/scripts/serverless_uat/deploy_cloudrun_services.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/scripts/serverless_uat/deploy_cloudrun_services.sh) | 模块存在但当前部署仍走 Toolkit 脚本；接入需单独实施 | 服务声明、镜像 digest、配置引用 | revision、实际运行 digest | 路径存在；不证明调用 |
| I08 | Cloudflare Worker/Pages 发布 | IaC Modules | [platform-ops-toolkit/.github/scripts/serverless/run_cloudflare_target.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/serverless/run_cloudflare_target.sh) | 当前 Toolkit 执行；未确认完整替换模块；待 owner 接入 | 发布包、checksum、账户、目标 | deployment ID、制品 checksum | 路径存在；不证明调用 |
| I09 | Cloudflare 域名/DNS | IaC Modules | [iac_modules/.github/workflows/cloudflare-serverless-domains.yml](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/.github/workflows/cloudflare-serverless-domains.yml)<br>[iac_modules/.github/actions/cloudflare-serverless-domains/action.yml](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/.github/actions/cloudflare-serverless-domains/action.yml) | 已有固定 SHA owner workflow 调用；实际消费 SHA 见 uses 表 | environment、gitops_ref、dns_mode | 域名归属、DNS 模式与执行结果 | 路径存在；不证明调用 |
| B01 | Web SaaS 主机配置/交付 | Playbooks Roles | [playbooks/setup-web-saas-domain.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/setup-web-saas-domain.yml)<br>[playbooks/roles/vhosts/web_saas_host_config](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/web_saas_host_config)<br>[playbooks/roles/vhosts/Doco-CD](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/Doco-CD) | Playbook/Role 现有；不把 pull-only CD 观察当成全部部署 | inventory、环境、版本、配置 | 主机配置、实际版本、服务交付状态 | 路径存在；不证明调用 |
| B02 | Caddy 证书恢复 | Playbooks Roles | [playbooks/caddy_certificate_restore.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/caddy_certificate_restore.yml)<br>[playbooks/roles/docker/caddy_certificate_restore](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/docker/caddy_certificate_restore) | 下游已有执行；待收敛至固定 SHA owner workflow | 单一目标、证书材料引用 | 目标正确、证书有效 | 路径存在；不证明调用 |
| B03 | 区域 Agent Proxy 部署 | Playbooks Roles | [playbooks/setup-agent-proxy-domain.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/setup-agent-proxy-domain.yml)<br>[playbooks/deploy_xray_proxy_server.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/deploy_xray_proxy_server.yml)<br>[playbooks/roles/vhosts/caddy](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/caddy)<br>[playbooks/roles/vhosts/vault-agent-tls](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/vault-agent-tls)<br>[playbooks/roles/vhosts/tky-proxy](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/tky-proxy)<br>[playbooks/roles/vhosts/agent-proxy](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/agent-proxy) | 入口/Role 现有；TLS Role 条件执行 | lane inventory、精确组件版本、配置引用 | Caddy/Xray/Agent 状态及版本 | 路径存在；不证明调用 |
| B04 | Xray Exporter | Playbooks Roles | [playbooks/deploy_xray_exporter.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/deploy_xray_exporter.yml)<br>[playbooks/roles/vhosts/xray-exporter](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/xray-exporter) | 现有入口/Role | inventory、exporter 版本及配置 | 进程及指标 | 路径存在；不证明调用 |
| B05 | Observability Agent | Playbooks Roles | [playbooks/deploy_observability_agent.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/deploy_observability_agent.yml)<br>[playbooks/roles/vhosts/node_exporter](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/node_exporter)<br>[playbooks/roles/vhosts/process_exporter](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/process_exporter)<br>[playbooks/roles/vhosts/blackbox_exporter](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/blackbox_exporter)<br>[playbooks/roles/vhosts/vector-agent](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/vector-agent) | 按条件执行；下列 Role 非全部必跑 | inventory、采集目标和配置 | 采集器、指标/日志链路 | 路径存在；不证明调用 |
| B06 | Web SaaS 部署后检查 | Playbooks Roles | [playbooks/verify_web_saas_post_deploy.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/verify_web_saas_post_deploy.yml)<br>[playbooks/roles/vhosts/web_saas_post_deploy_readiness](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/web_saas_post_deploy_readiness) | 现有入口/Role | 精确主机、readiness 参数 | 服务 readiness | 路径存在；不证明调用 |
| B07 | Agent Proxy DNS 后检查 | Playbooks Roles | [playbooks/verify_agent_proxy_post_dns.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/verify_agent_proxy_post_dns.yml)<br>[playbooks/roles/vhosts/agent_proxy_post_dns_readiness](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/agent_proxy_post_dns_readiness) | 现有入口/Role | 精确目标、域名和检查参数 | DNS 后入口及服务链路 | 路径存在；不证明调用 |
| B08 | 数据备份 | Playbooks Roles | [playbooks/web-saas-backup.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/web-saas-backup.yml)<br>[playbooks/roles/site_migration](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/site_migration) | 现有；site_migration tasks_from=extract；实际链路需按数据操作选择 | 源目标、备份配置、release 身份 | 备份与完整性 | 路径存在；不证明调用 |
| B09 | 数据恢复 | Playbooks Roles | [playbooks/web-saas-restore.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/web-saas-restore.yml)<br>[playbooks/roles/site_migration](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/site_migration) | 现有；site_migration tasks_from=load；独立恢复门槛 | 备份材料、精确恢复目标 | 恢复结果与数据检查 | 路径存在；不证明调用 |
| B10 | Serverless 数据库操作 | Playbooks Roles | [playbooks/.github/workflows/serverless-database-operations.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/.github/workflows/serverless-database-operations.yml)<br>[playbooks/scripts/data_operations/serverless](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/scripts/data_operations/serverless)<br>[playbooks/scripts/data_operations/database/create_release_checkpoint.sh](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/scripts/data_operations/database/create_release_checkpoint.sh) | owner workflow 现有；并非全部封装为 Role | 数据库目标、操作、schema 版本、SQL hash | checkpoint、schema version、迁移回执 | 路径存在；不证明调用 |
| B11 | Shared readiness | Playbooks Roles | 待新增，名称未确定 | 待新增；当前探针仍在 Toolkit；不得自动宣称已迁移 | Vault/Grafana/IAM endpoint、issuer、timeout | 三项探针证据；Toolkit 判断放行 | 待新增 |

### 源码实际 uses（含条件分支；不等于 Daily 必跑）

| Workflow | Job | 位置 | 实际 uses |
| --- | --- | --- | --- |
| .github/workflows/daily-main-snapshot.yaml | resolve-snapshot-tag | 1 | `actions/checkout@v7` |
| .github/workflows/daily-main-snapshot.yaml | resolve-snapshot-tag | 2 | `hashicorp/vault-action@v4` |
| .github/workflows/daily-main-snapshot.yaml | resolve-snapshot-tag | 3 | `actions/create-github-app-token@v3` |
| .github/workflows/daily-main-snapshot.yaml | resolve-snapshot-tag | 4 | `actions/create-github-app-token@v3` |
| .github/workflows/daily-main-snapshot.yaml | resolve-snapshot-tag | 5 | `actions/create-github-app-token@v3` |
| .github/workflows/daily-main-snapshot.yaml | resolve-snapshot-tag | 6 | `actions/create-github-app-token@v3` |
| .github/workflows/daily-main-snapshot.yaml | snapshot | 1 | `actions/checkout@v7` |
| .github/workflows/daily-main-snapshot.yaml | snapshot | 2 | `hashicorp/vault-action@v4` |
| .github/workflows/daily-main-snapshot.yaml | snapshot | 3 | `actions/create-github-app-token@v3` |
| .github/workflows/daily-main-snapshot.yaml | snapshot | 6 | `actions/upload-artifact@v7` |
| .github/workflows/daily-main-snapshot.yaml | resolve-built-snapshot-tag | 1 | `actions/checkout@v7` |
| .github/workflows/daily-main-snapshot.yaml | resolve-built-snapshot-tag | 2 | `actions/download-artifact@v8` |
| .github/workflows/daily-main-snapshot.yaml | shared-readiness | 1 | `actions/checkout@v7` |
| .github/workflows/daily-main-snapshot.yaml | dispatch-environment | 1 | `actions/checkout@v7` |
| .github/workflows/daily-main-snapshot.yaml | dispatch-environment | 2 | `hashicorp/vault-action@v4` |
| .github/workflows/daily-main-snapshot.yaml | dispatch-environment | 3 | `actions/create-github-app-token@v3` |
| .github/workflows/daily-main-snapshot.yaml | dispatch-environment | 4 | `actions/checkout@v7` |
| .github/workflows/daily-main-snapshot.yaml | dispatch-environment | 8 | `actions/upload-artifact@v7` |
| .github/workflows/daily-main-snapshot.yaml | snapshot-summary | 1 | `actions/checkout@v7` |
| .github/workflows/daily-main-snapshot.yaml | snapshot-summary | 2 | `actions/download-artifact@v8` |
| .github/workflows/daily-main-snapshot.yaml | snapshot-summary | 4 | `actions/download-artifact@v8` |
| .github/workflows/daily-main-snapshot.yaml | snapshot-summary | 6 | `actions/upload-artifact@v7` |
| .github/workflows/hybrid-orchestrator.yml | preflight | 1 | `actions/checkout@v7` |
| .github/workflows/hybrid-orchestrator.yml | preflight | 2 | `actions/checkout@v7` |
| .github/workflows/hybrid-orchestrator.yml | data_operations | 1 | `actions/checkout@v7` |
| .github/workflows/hybrid-orchestrator.yml | resource_orchestration | 1 | `actions/checkout@v7` |
| .github/workflows/hybrid-orchestrator.yml | resource_orchestration | 2 | `actions/checkout@v7` |
| .github/workflows/hybrid-orchestrator.yml | resource_orchestration | 4 | `actions/upload-artifact@v7` |
| .github/workflows/hybrid-orchestrator.yml | verify | 1 | `actions/checkout@v7` |
| .github/workflows/hybrid-orchestrator.yml | verify | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 3 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 4 | `./.github/actions/configure-gcp-oidc` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 5 | `google-github-actions/setup-gcloud@v2` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 6 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 7 | `ai-workspace-infra/iac_modules/.github/actions/prod-selfhost-access@254dd6321449ab12b862220c8876b482d7032fcd` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 8 | `ai-workspace-infra/playbooks/.github/actions/prod-native-standby@c6a4cb6c54c7e6dd2d63c43767f44a228385312a` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 9 | `ai-workspace-infra/iac_modules/.github/actions/prod-selfhost-access@254dd6321449ab12b862220c8876b482d7032fcd` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 10 | `actions/upload-artifact@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 11 | `actions/upload-artifact@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 3 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 4 | `./.github/actions/configure-gcp-oidc` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 5 | `google-github-actions/setup-gcloud@v2` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 6 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 7 | `ai-workspace-infra/iac_modules/.github/actions/prod-selfhost-access@254dd6321449ab12b862220c8876b482d7032fcd` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 8 | `ai-workspace-infra/playbooks/.github/actions/prod-native-init@ff7b09e135f52301e7605dcdf6f3b303c9c2dd32` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 9 | `ai-workspace-infra/iac_modules/.github/actions/prod-selfhost-access@254dd6321449ab12b862220c8876b482d7032fcd` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 10 | `actions/upload-artifact@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 11 | `actions/upload-artifact@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 3 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 4 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 5 | `./.github/actions/configure-gcp-oidc` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 6 | `google-github-actions/setup-gcloud@v2` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 7 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 8 | `ai-workspace-infra/iac_modules/.github/actions/prod-selfhost-access@254dd6321449ab12b862220c8876b482d7032fcd` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 9 | `ai-workspace-infra/playbooks/.github/actions/prod-native-billing-upgrade@ff7b09e135f52301e7605dcdf6f3b303c9c2dd32` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 10 | `ai-workspace-infra/iac_modules/.github/actions/prod-selfhost-access@254dd6321449ab12b862220c8876b482d7032fcd` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 11 | `actions/upload-artifact@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 12 | `actions/upload-artifact@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 3 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 4 | `./.github/actions/configure-gcp-oidc` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 5 | `google-github-actions/setup-gcloud@v2` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 6 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 7 | `ai-workspace-infra/iac_modules/.github/actions/prod-selfhost-access@254dd6321449ab12b862220c8876b482d7032fcd` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 8 | `ai-workspace-infra/playbooks/.github/actions/prod-full-business@7e9b16fa6c83a2dd8bafc22dca5870e06154253f` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 9 | `ai-workspace-infra/iac_modules/.github/actions/prod-selfhost-access@254dd6321449ab12b862220c8876b482d7032fcd` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 10 | `actions/upload-artifact@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 11 | `actions/upload-artifact@v4` |
| .github/workflows/selfhost-orchestrator.yml | provision | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | provision | 4 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | provision | 9 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | provision | 10 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | provision | 11 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | provision | 13 | `aws-actions/configure-aws-credentials@v4` |
| .github/workflows/selfhost-orchestrator.yml | provision | 14 | `./.github/actions/configure-gcp-oidc` |
| .github/workflows/selfhost-orchestrator.yml | provision | 15 | `azure/login@v2` |
| .github/workflows/selfhost-orchestrator.yml | provision | 18 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | provision | 19 | `hashicorp/setup-terraform@v4` |
| .github/workflows/selfhost-orchestrator.yml | provision | 20 | `actions/setup-python@v6` |
| .github/workflows/selfhost-orchestrator.yml | provision | 43 | `actions/upload-artifact@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_xconnect_zero_uat | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 3 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 4 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 5 | `actions/create-github-app-token@v3` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 6 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 7 | `actions/download-artifact@v8` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 9 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 11 | `actions/cache@v6` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 12 | `./.github/actions/setup-deployment-runner` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 14 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | capture_web_saas_baseline | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | capture_web_saas_baseline | 3 | `actions/download-artifact@v8` |
| .github/workflows/selfhost-orchestrator.yml | update_gitops_tags | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | update_gitops_tags | 2 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | update_gitops_tags | 3 | `actions/create-github-app-token@v3` |
| .github/workflows/selfhost-orchestrator.yml | update_gitops_tags | 4 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | initialize_empty_web_saas | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_web_saas | job | `ai-workspace-infra/playbooks/.github/workflows/web-saas-domain-cd.yaml@main` |
| .github/workflows/selfhost-orchestrator.yml | accept_web_saas_upgrade | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | switch_dns | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | switch_dns | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | switch_dns | 3 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | switch_dns | 5 | `actions/download-artifact@v8` |
| .github/workflows/selfhost-orchestrator.yml | switch_dns | 6 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | switch_dns | 7 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | switch_dns | 8 | `./.github/actions/setup-deployment-runner` |
| .github/workflows/selfhost-orchestrator.yml | switch_dns | 11 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | bootstrap_stripe_catalog | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | bootstrap_stripe_catalog | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | bootstrap_stripe_catalog | 5 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | observe_web_saas_after_dns | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | observe_web_saas_after_dns | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | observe_web_saas_after_dns | 3 | `actions/download-artifact@v8` |
| .github/workflows/selfhost-orchestrator.yml | observe_web_saas_after_dns | 4 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | observe_web_saas_after_dns | 5 | `./.github/actions/setup-deployment-runner` |
| .github/workflows/selfhost-orchestrator.yml | observe_agent_proxy_after_dns | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | observe_agent_proxy_after_dns | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | observe_agent_proxy_after_dns | 3 | `actions/download-artifact@v8` |
| .github/workflows/selfhost-orchestrator.yml | observe_agent_proxy_after_dns | 4 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | observe_agent_proxy_after_dns | 5 | `./.github/actions/setup-deployment-runner` |
| .github/workflows/selfhost-orchestrator.yml | deployment_summary | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_infra_platform | job | `ai-workspace-infra/playbooks/.github/workflows/open-platform-domain-cd.yaml@main` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy | 3 | `actions/download-artifact@v8` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy | 5 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy | 6 | `actions/cache@v6` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy | 7 | `./.github/actions/setup-deployment-runner` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy_non_iac | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy_non_iac | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy_non_iac | 3 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy_non_iac | 4 | `actions/download-artifact@v8` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy_non_iac | 6 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy_non_iac | 8 | `./.github/actions/setup-deployment-runner` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy_non_iac | 16 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_ai_workspace | job | `ai-workspace-infra/playbooks/.github/workflows/ai-workspace-domain-cd.yaml@main` |
| .github/workflows/selfhost-orchestrator.yml | deploy_monitor_agent | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_monitor_agent | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_monitor_agent | 3 | `actions/download-artifact@v8` |
| .github/workflows/selfhost-orchestrator.yml | deploy_monitor_agent | 4 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | deploy_monitor_agent | 5 | `actions/cache@v6` |
| .github/workflows/selfhost-orchestrator.yml | deploy_monitor_agent | 6 | `./.github/actions/setup-deployment-runner` |
| .github/workflows/selfhost-orchestrator.yml | trigger_data_migration | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | preflight | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | preflight | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | preflight | 3 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | supabase | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | uat_accounts_schema_probe | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | uat_accounts_baseline | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | uat_accounts_schema_migration | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 5 | `hashicorp/vault-action@v4` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 6 | `actions/create-github-app-token@v3` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 7 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 8 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 10 | `google-github-actions/auth@v2` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 11 | `google-github-actions/setup-gcloud@v2` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 12 | `docker/setup-qemu-action@v3` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 13 | `docker/setup-buildx-action@v3` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 16 | `docker/build-push-action@v6` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 23 | `actions/upload-artifact@v7` |
| .github/workflows/serverless-orchestrator.yml | artifact_manifest | 1 | `actions/download-artifact@v8` |
| .github/workflows/serverless-orchestrator.yml | artifact_manifest | 3 | `actions/upload-artifact@v7` |
| .github/workflows/serverless-orchestrator.yml | cloudflare_ssr | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | cloudflare_ssr | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | cloudflare_ssr | 5 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | cloudflare_ssr | 6 | `actions/setup-node@v7` |
| .github/workflows/serverless-orchestrator.yml | cloudflare_ssr | 7 | `hashicorp/vault-action@v4` |
| .github/workflows/serverless-orchestrator.yml | cloudflare_ssr | 9 | `actions/upload-artifact@v7` |
| .github/workflows/serverless-orchestrator.yml | frontend_router | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | frontend_router | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | frontend_router | 5 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | frontend_router | 6 | `actions/setup-node@v7` |
| .github/workflows/serverless-orchestrator.yml | frontend_router | 7 | `hashicorp/vault-action@v4` |
| .github/workflows/serverless-orchestrator.yml | edge_gateway | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | edge_gateway | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | edge_gateway | 5 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | edge_gateway | 6 | `actions/setup-node@v7` |
| .github/workflows/serverless-orchestrator.yml | edge_gateway | 7 | `hashicorp/vault-action@v4` |
| .github/workflows/serverless-orchestrator.yml | static_pages | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | static_pages | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | static_pages | 5 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | static_pages | 6 | `actions/setup-node@v7` |
| .github/workflows/serverless-orchestrator.yml | static_pages | 7 | `hashicorp/vault-action@v4` |
| .github/workflows/serverless-orchestrator.yml | static_pages | 8 | `actions/download-artifact@v8` |
| .github/workflows/serverless-orchestrator.yml | serverless_domains_provider | job | `ai-workspace-infra/iac_modules/.github/workflows/cloudflare-serverless-domains.yml@a7ac40fb0c3e620bdec89edd72b172afefc1f2ee` |
| .github/workflows/serverless-orchestrator.yml | serverless_domains | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | serverless_domains | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | trigger_data_migration | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | stripe_catalog | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | stripe_catalog | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | stripe_catalog | 3 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | stripe_catalog | 7 | `hashicorp/vault-action@v4` |
| .github/workflows/serverless-orchestrator.yml | destroy | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | destroy | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | destroy | 4 | `hashicorp/vault-action@v4` |
| .github/workflows/serverless-orchestrator.yml | destroy | 6 | `google-github-actions/auth@v2` |
| .github/workflows/serverless-orchestrator.yml | destroy | 7 | `google-github-actions/setup-gcloud@v2` |
| .github/workflows/serverless-orchestrator.yml | verify | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | verify | 2 | `hashicorp/vault-action@v4` |
| .github/workflows/serverless-orchestrator.yml | console_release_metadata | 2 | `actions/upload-artifact@v7` |
| .github/workflows/external-inventory-state.yml | sync | 1 | `actions/checkout@v4` |
| .github/workflows/external-inventory-state.yml | sync | 4 | `actions/checkout@v4` |
| .github/workflows/external-inventory-state.yml | sync | 5 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | preflight | 1 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | declared_network | 1 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | declared_network | 2 | `actions/setup-python@v5` |
| .github/workflows/xconnect-zero-cloud.yaml | declared_network | 4 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | declared_network | 5 | `actions/create-github-app-token@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | declared_network | 6 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | resolve_ai_aggregator_matrix | 1 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | resolve_ai_aggregator_matrix | 2 | `actions/setup-python@v5` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 1 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 3 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 4 | `actions/create-github-app-token@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 5 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 6 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 7 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 10 | `actions/create-github-app-token@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 12 | `hashicorp/setup-terraform@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 14 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 15 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 16 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 18 | `aws-actions/configure-aws-credentials@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 28 | `actions/upload-artifact@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | existing_one | 1 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | existing_one | 3 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | existing_one | 4 | `actions/create-github-app-token@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | existing_one | 5 | `actions/create-github-app-token@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | existing_one | 6 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | existing_one | 7 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | existing_one | 9 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | enroll_node_matrix | 2 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | enroll_node_matrix | 3 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | enroll_node_matrix | 4 | `actions/create-github-app-token@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | enroll_node_matrix | 5 | `actions/create-github-app-token@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | enroll_node_matrix | 6 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | enroll_node_matrix | 7 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | enroll_node_matrix | 8 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | enroll_node_matrix | 9 | `aws-actions/configure-aws-credentials@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | reconcile_mesh | 1 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | reconcile_mesh | 2 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 1 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 3 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 4 | `actions/create-github-app-token@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 5 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 6 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 7 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 9 | `hashicorp/setup-terraform@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 10 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 11 | `aws-actions/configure-aws-credentials@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 13 | `aws-actions/configure-aws-credentials@v4` |
| .github/workflows/environment-data-operations.yml | request_gate | 1 | `actions/checkout@v7` |
| .github/workflows/environment-data-operations.yml | legacy_import | job | `ai-workspace-infra/playbooks/.github/workflows/uat-data-import.yaml@b82d727808696278613df248e01c29059048be35` |
| .github/workflows/environment-data-operations.yml | akamai_preflight | job | `ai-workspace-infra/iac_modules/.github/workflows/akamai-state-preflight.yml@f8b3d52e4f2b6528fcf4fa762ea7bf83f8145d06` |
| .github/workflows/environment-data-operations.yml | serverless_database | job | `ai-workspace-infra/playbooks/.github/workflows/serverless-database-operations.yml@5a1f68c6de22010b20771ea7583f892c2c899da3` |
| .github/workflows/environment-data-operations.yml | selfhost_database | job | `ai-workspace-infra/playbooks/.github/workflows/selfhost-database-operations.yml@7d660cdb4066e2a4cf3fed68bccafea939771e64` |
| .github/workflows/environment-data-operations.yml | selfhost_components | job | `ai-workspace-infra/playbooks/.github/workflows/selfhost-data-lifecycle.yml@5a1f68c6de22010b20771ea7583f892c2c899da3` |
| .github/workflows/environment-data-operations.yml | release_controller | 1 | `actions/checkout@v7` |
| .github/workflows/environment-data-operations.yml | release_controller | 5 | `actions/upload-artifact@v7` |
| .github/workflows/environment-upgrade-ci.yml | offline-rehearsal | 1 | `actions/checkout@v7` |
| .github/actions/configure-gcp-oidc/action.yml | __composite_action__ | 1 | `hashicorp/vault-action@v4` |
| .github/actions/configure-gcp-oidc/action.yml | __composite_action__ | 2 | `hashicorp/vault-action@v4` |
| .github/actions/configure-gcp-oidc/action.yml | __composite_action__ | 3 | `google-github-actions/auth@v2` |

### 审计分类汇总

| 类别 | 数量 |
| --- | --- |
| EXECUTION_CANDIDATE | 101 |
| FLOATING_MAIN_CANDIDATE | 10 |
| FLOATING_OWNER_REF | 3 |
| UNREFERENCED_INPUT | 9 |
| UNRESOLVED_SCRIPT_LITERAL | 26 |

完整候选明细见同目录 audit.md 和 audit.json；规则命中需要人工判断，不是部署验收。

<!-- END GENERATED DAILY SNAPSHOT AUDIT -->
