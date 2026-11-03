# Grafana 独立 PostgreSQL 与 GitOps 持久化规划

日期：2026-11-03。状态：目标架构，未迁移。需求：[Knowledge #351](https://github.com/ai-workspace-services/knowledge/issues/351)。[完整规划](Pro-Custom与Grafana升级完整规划.md) · [恢复规划](Grafana面板丢失排查与恢复规划.md) · [验收](Pro-Custom与Grafana分阶段交付验收规划.md)

## 1. 状态分层与生命周期

Grafana 自身 `[database]` 使用独立 PostgreSQL，保存用户、组织、成员、权限、面板运行状态及适用版本的其他持久对象。标准面板/数据源/告警定义由版本化声明管理；指标仍在 VictoriaMetrics，日志/链路仍在 VictoriaLogs/Traces，不能用迁移 Grafana 元数据来声称迁移了观测历史。

外部是相对于 Grafana 工作负载而言：删除/替换 Grafana Pod、release、namespace 不得连带删除数据库。优先独立平台数据库服务，不使用 Accounts 业务库或随业务代际重建的同一存储。具体承载、可用性、容量和成本由资源 owner 提案，本规划未选择或购买云产品。

初期保持一个 Grafana 副本。数据库外置不等同高可用：Grafana、副本配置、数据源、认证、数据库和密钥均需要单独验证。插件文件和其他本地文件状态也不能因使用 PostgreSQL 就忽略。

## 2. 数据库与三类身份

| 身份 | 用途 | 限制 |
| --- | --- | --- |
| 管理/迁移身份 | 创建数据库、对象权限、批准的 schema 升级、恢复 | 不作为日常连接池身份 |
| Grafana 服务身份 | 本服务必需对象的读写 | 不使用超级用户，不授予其他业务库权限 |
| 审计身份 | 状态和批准的脱敏视图 | 无业务写入、对象所有权、提权或秘密读取 |

Grafana 启动可能自动执行 schema migration；管理迁移与日常 DML 分离必须按拟用版本实测，不能仅宣布“只读写账户”就认为启动兼容。若版本要求运行期保留部分 DDL，应在本服务数据库内记录最小权限例外与退出条件，不能授予集群级超级权限。

业务进程逐步非 root，管理员不承载日常业务；不把 DB 迁移与所有主机/容器降权捆成一次改造。现有卷权限先核对，不递归放宽为全员可写。

数据库配置按环境提供非敏感引用；凭据与 Grafana 加密密钥由受控秘密服务交付。启用验证服务端身份的 TLS，按实际连接模型限制网络访问与连接数，明文 DSN/密码不进入 Git、日志、回执和导出。

## 3. GitOps 与制品契约

标准面板只有一个编辑来源。Artifacts/观测实现 owner 包装版本化面板和插件能力，GitOps 选择目标环境的固定版本及非敏感参数；不得维护两份可独立修改的面板主副本。GitOps 按现有规则保存 YAML，外部 API 所需 JSON 在运行时派生。

面板包最小清单：包版本、源 SHA、校验值、兼容 Grafana 版本、Dashboard UID、Folder UID、Datasource UID、标准面板标题/关键 panel ID、变量契约、插件 ID/版本/校验值、预期指标和标签、显式退役清单。

每个 provider 具有明确 Organization 绑定，禁止继续用固定 `orgId: 1` 隐式代替所有客户。跨组织的标准 Dashboard 逻辑标识与实例标识分别记录；具体 UID 唯一性按目标版本/API 验证，避免直接复用导致覆盖。

`allowUiUpdates: false` 用于标准面板；防误删默认策略采用 `disableDeletion: true` 并验证效果。该选项仅约束文件 provisioning 的删除行为，不防 API 删除、库损坏或权限错误。退役由显式清单和独立审核完成，避免永久残留。

用户自定义面板和平台标准面板分开目录、UID 和 owner。未来开放自定义前定义备份及导出规则；不能在 UI 保存标准面板后承诺 GitOps 会自动回写。

部署前验证面板包不为空、必需 UID 无遗漏、Datasource UID 引用闭合、插件齐备、provider 路径实际挂载、checksum 能触发更新。数据库连通失败或配置包缺失时明确失败，不回退空 SQLite，不静默用默认数据源。

## 4. 备份和恢复目标

暂定 RPO ≤ 1 小时、RTO ≤ 1 小时，未演练前均为目标。若仅每天逻辑备份，不满足一小时 RPO；需要提高备份频率或建立经验证的基础备份与连续 WAL 归档、PITR 链。

| 备份对象 | 触发 | 验证 |
| --- | --- | --- |
| PostgreSQL 一致性数据 | 周期性及每次升级前 | 可恢复、对象完整、校验通过 |
| 配置/面板包/插件清单 | 每个发布版本 | 固定版本可获取并复现 |
| 加密密钥恢复材料 | 按密钥治理流程 | 匹配备份，隔离恢复可解密；不导出明文到报告 |
| 本地插件或其他必要文件 | 根据有效配置盘点 | 文件可重建或已备份 |

建议保留近期逐小时恢复点至少 7 天、日备份至少 30 天、升级前恢复点跨过观察窗口；最终保留周期须由容量和合规评审确认。备份加密、异地保存、访问分离；同一块本地盘上的副本不算独立恢复路径。

每月建议执行一次隔离恢复，重大升级前必须有可用恢复证据；验证用户/组织、标准与自定义面板、数据源解密、权限和查询。演练默认关闭生产通知，防止重复告警。报告测量实际恢复点和耗时，不仅记录上传成功。

## 5. SQLite 到 PostgreSQL 的迁移策略

1. 核实实际数据库类型、路径、版本、对象清单及写入者，保护源备份。
2. 区分配置重建与全状态迁移：标准面板由包重建，UI 对象/权限/告警/加密状态逐类映射。
3. 选定固定版本的 owner 工具，在隔离目标演练；SQLite 备份采用一致性方法，普通文件拷贝须按官方要求停服务。
4. 不直接用未经验证的表转换工具搬整库；Grafana 元数据跨数据库迁移需客户自行验证，不假定修改 DSN 会搬数据。
5. 验证目标对象、身份权限、查询和已填充目标的再次备份/恢复；保留源及失败目标。
6. 在批准窗口冻结相应配置写入、最后同步、交接写者；此步骤不是本轮文档授权的操作。
7. 目标接受新写入后，回退需恢复或核对新增状态，不能仅切回落后的源库。回滚镜像不等于回退数据库 schema。

## 6. 参考

- [Grafana 数据库配置](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/#database)
- [备份 Grafana](https://grafana.com/docs/grafana/latest/administration/back-up-grafana/)
- [Provisioning 与 UI 更新](https://grafana.com/docs/grafana/latest/administration/provisioning/#make-changes-to-a-provisioned-dashboard)
- [数据库加密](https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-database-encryption/)
