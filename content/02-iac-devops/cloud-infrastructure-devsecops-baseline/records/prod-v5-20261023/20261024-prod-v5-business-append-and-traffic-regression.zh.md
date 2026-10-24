# V5 在线业务追加与实时流量回归回执

时间口径：Asia/Shanghai。本文只提交脱敏摘要；原始数据库、完整计划、用户数据和认证材料留在受控证据库。历史失败不由后续成功覆盖。

[当前 V5 基线](prod-v5-runtime-and-snapshot-baseline-20261023.zh.md) · [V4→V5 复盘](../../17-prod-v4-v5-baseline-and-upgrade-retrospective.zh.md) · [历史 Billing/Vector 故障](../prod-v2-v3-20261019/20261020-billing-vector-ingest-p0.zh.md) · [V3→V4 回归清单](../prod-v3-v4-20261020/regression-and-closure-checklist-20261021.zh.md)

## 业务追加边界

此前 users-only 成功只证明用户迁入；目标套餐、订阅、额度及历史账务表为空，不能据此推导全业务通过。源端 33 名用户、目标 33 名用户均保留；关联业务外键映射到目标既有内部 UUID。唯一默认 Sandbox 用户的代理 UUID 差异由用户明确接受，保留目标值；其他用户仍必须匹配归一化邮箱、密码摘要和代理身份。原始身份与密码数据不进入文档。

源数据通过只读事务导出为隔离快照，迁移使用隔离快照专用只读身份，不改变在线源端授权或 RLS。目标迁移前的加密异机备份已实际解密恢复到独立数据库，并核验 33 名用户及迁移前空业务基线。原始证据不删除。

新增 `migratectl reconcile-business` 使用预构建版本，取得目标事务锁后读取目标、重建计划、校验摘要并追加缺失行。应用无需声称写入进程已暂停；已有业务行字段不同即冲突，目标独有行保留，不覆盖套餐、订阅、额度或财务事实。

## 已执行回执

| 阶段 / run_id | 北京时间 | 固定构件与退出结果 | 证据与结论 |
| --- | --- | --- | --- |
| 真实业务追加 / `online-apply-r105-attempt1` | 2026-10-24 10:41:30–10:42:03 | Accounts main `e0d6b8ddc0865c39a897e8aa2ce57c3a5e95c261`；预构建 `daily-build-2026.10.24-r105`；exit 0 | 追加 152,353 行；33 名用户前后摘要一致，schema 前后摘要一致；仅事件身份序列单调推进 1 项 |
| r105 幂等重验 | 2026-10-24；逐次准确时间见受控执行日志 | 业务表 append 0、冲突 0；计划/结构保护拒绝，非成功重放 | 无关心跳被绑定进计划；PostgreSQL 统计刷新被误识别为结构变化。未重复写入，不计入三轮成功 |

预构建 r105 Linux 二进制 SHA-256：`06f3013d29fdf062bf288869671fde454630fc5fdac0b0068984722868a8dede`。目标 native schema 版本 `2026102002`，校验和 `f45db2423f11d9dcc7f3cc58c72b52228a27d7b6ccfc717faf2bbb56fa0498b1`；CLI 编译 Billing 合同校验和 `a7133f3ef2ea9013a055cfd1442a7488d2b837f289e0f5d9b61624d4fde9bc53`。这些校验和分别对应各自合同，不与 GitOps 增量 SQL 校验和混用。

| 业务表 | 实际追加行数 |
| --- | ---: |
| billing_plans | 18 |
| account_billing_profiles / account_quota_states | 33 / 33 |
| account_policy_snapshots | 0（源端也是 0；不编造策略） |
| subscriptions / subscription_records / subscription_lifecycle_states | 7 / 13 / 5 |
| traffic_stat_checkpoints / traffic_minute_buckets | 49 / 76,079 |
| billing_ledger | 76,081 |
| finance_invoices / finance_payments / finance_refunds | 5 / 5 / 2 |
| finance_operations / finance_operation_events | 8 / 15 |

实现与重验：[Accounts #272](https://github.com/ai-workspace-services/accounts/pull/272)；在线计划修复 [Accounts #273](https://github.com/ai-workspace-services/accounts/pull/273)。后者保留事务内全部非同步表保护，计划只绑定业务范围与已验证身份映射；忽略统计字段不等于忽略 DDL、权限、触发器或策略变化。

## 采集断点与独立验收

公共 Billing 路由原先返回 HTTP 200 空响应，Vector 可能将其当作投递成功，目标却未入库。已修正为实际 Billing 转发：快照仅允许 POST，健康检查允许 GET/HEAD，其他管理请求拒绝。外部探测 readiness 200，缺失或无效认证的快照 POST 均为 401，不再以空 200 吞掉请求。

修复链：[Playbooks #745](https://github.com/ai-workspace-infra/playbooks/pull/745) → [GitOps #519](https://github.com/ai-workspace-infra/gitops/pull/519)。Agent 公共路由另见 [Playbooks #744](https://github.com/ai-workspace-infra/playbooks/pull/744) → [GitOps #518](https://github.com/ai-workspace-infra/gitops/pull/518)。

前端不得把不存在的策略快照显示为“正常”、把缺少真实采集桶显示为“延迟 0 秒”。[Portal #466](https://github.com/ai-workspace-services/portal/pull/466) 已合入，分别呈现未生成策略、待采集、过期和真实统计状态；发布、目标部署和浏览器验收另行记录。

## r106 三轮真实幂等重验

固定 Accounts main `04c711bf73097be63827e990569abd72fc3b1bc9`，预构建 `daily-build-2026.10.24-r106`，发布流水线 `40056175497` 全部成功。Linux 二进制 SHA-256 `f3113ca79c80c5a2432ba5de107da7404fa1254d98c181fef5926736bd9cb6cf`，下载及目标再次核验；native/Billing 编译合同校验和保持前述值。每轮使用同一隔离源快照，fresh preview 后用精确计划 apply，源/目标分别为 V4 快照与在线 V5。

| run_id 前缀 | 预览起止（北京时间） | 真实 apply 起止（北京时间） | 结果 |
| --- | --- | --- | --- |
| `verified-repeat-1` | 11:02:03–11:02:42 | 11:02:42–11:03:18 | 两阶段 exit 0；append 0、conflicts 0、target_writes false、advanced_sequences 0 |
| `verified-repeat-2` | 11:03:18–11:03:57 | 11:03:57–11:04:33 | 两阶段 exit 0；append 0、conflicts 0、target_writes false、advanced_sequences 0 |
| `verified-repeat-3` | 11:04:33–11:05:12 | 11:05:12–11:05:50 | 两阶段 exit 0；append 0、conflicts 0、target_writes false、advanced_sequences 0 |

三轮均映射 33 users、仅保留已确认的 1 个默认 Sandbox 代理差异；各阶段用户和结构摘要前后一致。结果为 **PASS（在线业务追加重放 3/3）**，不借用早先 IaC/部署/users-only 重放的通过次数。

## 节点修复、两周期入库及页面

| 阶段 / run_id | 北京时间 | 实际结果 |
| --- | --- | --- |
| Portal 选择 / `portal-r106-select` | 10:56:47–10:56:55 | GitOps [#520](https://github.com/ai-workspace-infra/gitops/pull/520) main `ed6a5d0cd2e50dbd5cf35abff5cd019a8ec001b8`；Playbooks 现有 `doco_cd_release_selection` 选择固定 commit，exit 0；10:57:00–10:57:04 重跑 changed 0 |
| Portal 运行版本 | 10:57:24 启动，后续页面核验 | Console 预构建 r106，commit `691b7dcc9870d4ba14b10f4b8dadc4e6d873ca0e`；OCI index `sha256:06775cfa5582fb83bae336c4c4befe1fbd4f7747d526653b80736e3e4862e666`；Accounts/Billing 未重启 |
| 节点预检 | 11:06:17–11:06:26 | 检查脚本最初只读取 Vector auth 配置，未识别现有 request.headers Bearer；exit 1，修改前停止；修正检测后确认 Vector 凭据实际已一致。不是生产认证变更 |
| Exporter 修复 / `exporter-repair-030638` | 11:06:38 完成 | 3 个可访问节点都能以规范凭据读取 33 个身份；JP Free 无改动，JP01/JP Plus 各补齐 1 个配置文件并只重启两个 Exporter，Xray 不重启；exit 0 |
| 节点幂等 / `exporter-repair-030647` | 11:06:47 完成 | 3 节点均 changed_files 0、restarted_exporters 空；exit 0 |
| 真实周期 A | 11:05:41 基线→11:07:47 采样 | checkpoints 鲜度推进到 11:07:39；分钟桶 76,079→76,083，账本 76,081→76,085，字节增加 10,810,538 |
| 真实周期 B | 11:07:47→11:09:00 采样 | 分钟桶再增至 76,087，账本至 76,089，最新桶 11:08:00，字节再增 28,373,855；两周期合计 +39,184,393 字节 |

两次正增量来自 JP Plus 的真实 xhttp 样本，不是导入历史或测试伪造事件。JP01 与 JP Free 的新快照持续生成但当前 samples 为空，标 **IDLE（正流量验收待实际请求）**。其余节点未纳入本轮正向验收，不宣称全节点通过。JP Plus 的 VictoriaLogs/Prometheus 目的地另有超时告警，与 Billing 快照 sink 分开记录；不能由此宣称所有观测管道健康。

真实登录会话已核验 Console 的套餐、配额、历史记录和缺少策略的呈现。Accounts `/api/account/usage/summary` 返回 `sourceOfTruth=postgresql`、`planAssignmentStatus=assigned`、Free 配额 5,368,709,120 字节；该登录账户历史用量 13,389,833,502 字节及最后桶时间与数据库只读汇总精确一致。该账户当前没有新采集流量，页面显示其历史鲜度，不能用别的账户的新流量刷新它。前端如实显示“策略未生成”，不伪造策略或修改余额。此次为已有真实登录会话的业务页面验收，不宣称重新输入凭据/MFA 登录已执行。

证据索引：受控库保留 r105 初次 preview/apply、r105 保护拒绝日志、r106 六份完整计划/应用及六份摘要、迁移前加密备份和独立恢复证明、发布 manifest/checksum、两个节点修复回执、节点快照汇总及 `traffic-before-repair` / 四次 `traffic-after-repair` 采样。公开记录只给阶段与脱敏汇总。仓库真实回归 case 为 `internal/migrate/usage_merge_postgres_test.go::TestFullBusinessUsageMergePostgres17`（非同步数据更新与 ANALYZE 不误阻断，业务并发写仍拒绝旧计划、事务回滚、三次无写入、非默认身份差异阻断）；Portal `accountSyncPresentation.test.ts` 覆盖缺策略/缺采样/过期等状态。

历史导入的桶与账本不等于新采集成功，本轮正向采集结论只覆盖上述两个真实周期和实际有流量的节点。源端继续在线写入，源端进行中财务任务仍由源端持有，目标财务后台执行保持关闭；本轮不修改 DNS、不重复触发支付、不宣称整代切换验收完成。
