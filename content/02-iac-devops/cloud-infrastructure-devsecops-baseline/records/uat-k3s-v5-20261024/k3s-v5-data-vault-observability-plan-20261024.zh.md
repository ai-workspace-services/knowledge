# Kubernetes UAT：业务数据迁移、Vault 隔离恢复及观测对接方案归档

归档日期：2026-10-24，Asia/Shanghai。资料类型：用户提供的实施方案脱敏整理；**不是本次执行回执，也不是迁移成功或切换证明**。资料中的现场数值尚未在本次归档中独立实测。

[运行基线](web-saas-k3s-v5-runtime-and-snapshot-baseline-20261024.zh.md) · [基线总索引](../../README.md) · [统一流程](../../09-cloud-infrastructure-devsecops-baseline-closing-the-loop.md) · [平台工程白皮书](../../../../../docs/reference/multi-cloud-platform-engineering-whitepaper.zh.md)

## 1. 来源、时间与边界

- 来源：用户于 2026-10-24 提供的《web-saas-k3s-v5 数据迁移、Vault 隔离恢复及观测对接实施方案》。原始材料保留于受控附件位置，本公开记录不复制主机地址、部署入口、凭据存储路径、账号标识或原始备份。
- 已有运行基线采样时间：2026-10-24 19:40（Asia/Shanghai）；方案另报告 Vault 快照采样时间为当日 20:02:54 CST，按北京时间归档，其时区仍需原执行者确认。
- 迁移执行起止时间、run_id、执行人和退出码：未提供；状态为 NOT_RUN（本次未执行，既有执行情况待凭证确认）。
- 源端为仍在服务的生产环境；“只读”指迁移访问权限，**不表示冻结生产业务写入**。目标为独立 Kubernetes UAT。
- 不切流、不改公共 DNS、不冻结生产写入、不删除旧资源。目标端操作须通过独立资源身份确认，源端不执行赋权、重启或配置变更。

## 2. 方案报告的现场采样

| 范围 | 方案报告内容 | 证据边界 |
| --- | --- | --- |
| 目标计算 | Tokyo 3、2 vCPU / 4 GB、79 GB、Debian 13；K3s v1.36.5+k3s1 | 尚缺当前 CMDB 与不可变声明版本对应回执 |
| 目标存储 | PostgreSQL 5Gi、观测栈 20Gi local-path PVC；PV 绑定 hostname `localhost` | 保持节点名；需补 PVC/PV UID、reclaimPolicy、卷路径和恢复证据 |
| 工作负载 | 6 个业务工作负载 Ready；4 个 Flux 控制器、3 个 ESO 组件及 5 容器观测栈 Running；报告零重启 | 属于采样结果，不能推出零数据丢失或业务验收通过 |
| HTTPS | Console 首页和登录页、Accounts 健康、Billing 就绪均报告 200，正常 CA 校验 | 不代表真实账号登录、完整数据或业务链路通过 |
| 当前 Vault | 临时内存实例，无 PVC | 持久化恢复仍为计划 |
| 源数据库 | PostgreSQL 17；schema 2026102002、dirty=false；76 个表/关系 | 需区分表、视图和其他关系的统计口径 |
| 目标数据库 | PostgreSQL 16；47 个自动创建业务表、3 个种子账号；迁移元数据未初始化 | 现有结构不可直接假定等价于迁移版本 0 |

### 2.1 源端数据量（方案采样）

| 数据类别 | 表及行数 |
| --- | --- |
| 用户、结算及配额 | users 33；account_billing_profiles 33；account_quota_states 33 |
| 套餐与订阅 | billing_plans 18；subscriptions 7；subscription_records 13；subscription_lifecycle_states 5 |
| 财务 | finance_operations 8；finance_operation_events 15；finance_invoices 5；finance_payments 5；finance_refunds 2 |
| 账本与流量 | billing_ledger 79,117；traffic_minute_buckets 79,115；traffic_stat_checkpoints 49 |
| 智能体与审计 | agents 5；team_agent_enrollments 1；node_health_snapshots 5；audit_logs 3；sessions 8 |

源端持续写入，以上不是未来目标必须恒等的实时总数。验收必须针对同一一致性快照或明确的增量窗口；仅记录最大 ID 或时间戳不能覆盖更新、删除和跨表一致性。

### 2.2 方案提供的校验和

| 对象 | SHA-256 / 大小 | 状态 |
| --- | --- | --- |
| migratectl | `93a0ca7d52dad8599188ab3bf80a947fc237899a32c857c08b5ce18e287bb12a` | 方案报告两端相同；release/tag、源码 commit、迁移包版本待补 |
| 原生 schema | `f45db2423f11d9dcc7f3cc58c72b52228a27d7b6ccfc717faf2bbb56fa0498b1` | 目标版本 2026102002；实际迁移后摘要待验证 |
| Billing schema | `a7133f3ef2ea9013a055cfd1442a7488d2b837f289e0f5d9b61624d4fde9bc53` | 原方案参数引用；计算对象与方法待补 |
| 源 Vault Raft 快照 | `642a6e8ee8b286f3bf6589748490e338f66a9d2faaa9af5f28b402fd66dede32`；1,501,138 字节 | 方案报告已提取；大小和摘要不能代替恢复验证 |

## 3. 数据迁移范围与实施前待决项

迁移覆盖用户及身份、RBAC、套餐、订阅、配额、策略、财务单据、计费账本、分钟流量、智能体与相关业务结构。密码、MFA、会话凭据仅在受控传输和数据库内处理，公开证据只记录脱敏对账结论。

1. **源端权限**：原方案 Step 1 包含 GRANT，属于源端写操作，与只读边界冲突；该步骤不作为执行授权。使用已有只读身份验证权限，缺权限则报告 BLOCKED。
2. **数据库版本与既有结构**：先验证 PostgreSQL 17→16 的迁移兼容性，以及已有 47 表与 forward migrations 的兼容方式。不得凭“元数据表缺失”直接运行迁移或伪造 baseline；目标写入前保存可恢复点。
3. **工具能力**：原方案列出的 compare-full-business、参数及事务导入行为均需以固定版本的帮助、代码和 dry-run 回执核实；本记录不把示例命令认定为已验证操作。
4. **一致性与并发**：确定一致性快照、目标事务锁、锁超时、失败回滚及增量重放策略。不能以“低峰窗口”代替目标写入协调，也不能由本方案推导生产停写授权。
5. **种子与身份冲突**：33 名源用户与目标 3 个种子账号的保留、合并及冲突规则须明确；“保留种子账号”与“目标总数必须为 33”不一定相容。sandbox 代理 UUID 差异可按用户既有要求列为明确例外，其他身份差异不可泛化忽略。
6. **序列与依赖**：依外键依赖导入，核对金额、状态和时间戳。原方案通过序列名称猜表名的通用 SQL 不纳入执行指令；应按真实序列依赖核验，禁止错误重置序列。
7. **验收**：逐表比对行数、稳定摘要、外键、序列和获准例外；真实登录后验证套餐、余额、配额、策略及 Exporter→Vector→Billing→Accounts→页面链路。健康接口 200 不替代业务验收。

## 4. Vault 隔离恢复计划

目标拟使用独立持久化 Vault，10Gi PVC。Raft 快照恢复路线必须使用兼容的 Raft 存储与 Vault 版本，并验证 seal/unseal 配置及密钥可用性；原方案的 File 后端或筛选 KV 导入不能作为完整 Raft 恢复的等价替代方案。

完整快照可能包含生产身份、策略、外部集成和敏感数据。目标应先隔离网络与生产依赖，再恢复并完成目标侧身份、策略、审计和凭据收敛。所有撤销操作必须证明作用于目标 Vault，不能误吊销源端凭据。ESO 仅授予目标环境专属路径权限，记录允许/拒绝结果，不公开路径原文或 token/accessor。

验收需覆盖快照检查、恢复与解封、选定挂载/对象清单及脱敏摘要对账、目标写入隔离、ESO 越权拒绝和 Pod 重建后数据保持。Pod 重建不等于宿主重启验证；local-path 单节点 PVC 也不等于异机灾备，分别记录结果。RPO/RTO、加密备份位置和恢复负责人待补。

## 5. 观测对接计划

范围为 VictoriaMetrics、VictoriaLogs、VictoriaTraces、OTel Collector、Grafana 的组件、配置、数据源及仪表盘验证。既有生产观测系统保持原部署关系；本任务不要求迁移其全部历史数据。

方案报告 VictoriaMetrics 298 项系统指标及各组件健康。待执行验证需从应用产生可关联的真实指标、日志和 trace，检查采集、入库、查询及仪表盘；并验证告警规则和通知路径。标签包含目标集群、UAT、区域、节点和云厂商；标签本身不构成访问或告警隔离，仍需检查租户、存储、网络及规则范围。

## 6. 阶段状态与回执合同

| 阶段 | 本次归档状态 | 下一份证据 |
| --- | --- | --- |
| 用户材料及历史运行基线 | 已归档，现场声明待独立核验 | 原执行者补不可变证据引用 |
| 只读预检与工具能力核对 | NOT_RUN | 目标身份、权限、固定构件、退出码 |
| Schema 与版本兼容 gate | BLOCKED | 17→16、既有表及迁移元数据处理证明 |
| 目标业务数据导入 | NOT_RUN | 一致性快照、事务、差异报告与回滚点 |
| Vault 持久化恢复 | NOT_RUN | 恢复、解封、权限隔离与重建验证 |
| 观测全链路验证 | NOT_RUN | 真实遥测、仪表盘与告警回执 |
| 真实账号业务验收 | NOT_RUN | 登录、业务数据与实时用量验证 |
| DNS/流量切换 | NOT_RUN | 仍需单独明确授权 |

每轮追加 Asia/Shanghai 起止时间、run_id、执行者、受控源/目标身份引用、commit/tag/digest、schema/迁移校验和、阶段、退出码、错误原因、修复 PR、重验结果和脱敏证据索引。未提供项填写“未提供”，不得补造成功。后续执行回执以新记录追加并回链本文，保留本次方案的时间背景。


### 增强准入方案追加（2026-10-24）

[增强安全与严格准入版](k3s-v5-migration-enhanced-guardrails-20261024.zh.md)补充本轮 run_id、计划窗口、逐类对账、种子身份条件、Vault 与观测验收门槛。该记录为方案，实际执行及切流状态仍需各自凭证，不覆盖已有历史采样。
