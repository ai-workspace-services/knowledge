# Grafana 面板丢失排查与恢复规划

日期：2026-11-03。状态：迁移遗漏已核实，21 个面板已通过 GitOps 恢复并经公网登录态 API 验证；浏览器渲染、全部指标数据和观察窗口未验收。需求：[Knowledge #351](https://github.com/ai-workspace-services/knowledge/issues/351)，追加证据：[Knowledge #353](https://github.com/ai-workspace-services/knowledge/issues/353)。[完整规划](Pro-Custom与Grafana升级完整规划.md) · [持久化](Grafana独立PostgreSQL与GitOps持久化规划.md) · [交付验收](Pro-Custom与Grafana分阶段交付验收规划.md)

## 1. 事件边界

用户报告本次升级后所有面板再次丢失。该报告是故障输入，不等于已读取数据库确认对象被删除。需要区分面板列表为空、当前组织错误、无查看权限、面板存在但无指标、插件缺失和链接 UID 失效。

既有文档记录 V6 基础服务与入口切换完成；它不证明本次 Grafana 面板完整性。不得据此否定用户报告，也不能把旧恢复目标或已退役实例当作当前可用回退点。

## 2. 已核对的固定源码

| 证据 | 发现 | 结论限制 |
| --- | --- | --- |
| [GitOps V5 release](https://github.com/ai-workspace-infra/gitops/blob/16b4bc8f419debfd70fbcd2c7920825cadcc543e/services/platform-observability/prod/release.yaml#L25) | valuesFrom 引用 `source-grafana-values` | 证明声明，不证明当前运行 |
| [GitOps V5 导入包](https://github.com/ai-workspace-infra/gitops/blob/16b4bc8f419debfd70fbcd2c7920825cadcc543e/services/platform-observability/prod/imported-grafana/source-grafana-values.yaml#L8) | 数据源、应用和 dashboard provider 引用存在 | 不证明 UI 临时编辑已回写 |
| [GitOps V6 release](https://github.com/ai-workspace-infra/gitops/blob/16b4bc8f419debfd70fbcd2c7920825cadcc543e/services/prod-k3s-v6/observability-prod/helmrelease.yaml#L69) | 启用持久化，未接旧面板导入引用 | 不能断言当前用空盘或空库 |
| [V6 资源图](https://github.com/ai-workspace-infra/gitops/blob/16b4bc8f419debfd70fbcd2c7920825cadcc543e/services/prod-k3s-v6/observability-prod/kustomization.yaml) | 未列旧 imported-grafana 包 | 新路径有可导致面板遗漏的缺口 |
| [Chart provider 模板](https://github.com/ai-workspace-infra/artifacts/blob/8588db1a56a9fb9c2af2833e6b7ee7e866e69816/oci/charts/open-platform/charts/observability-stack/templates/configmap.yaml#L107) | 固定 `orgId: 1`、`disableDeletion: false` | 须核对实际已部署 digest 的模板是否一致 |

最初公开健康响应为 Grafana `13.2.4`、database `ok`，仅证明当时进程/数据库健康。随后追加的数据库和挂载核对见第 7 节；仍未登录浏览器验收面板渲染。

## 3. 只读排查顺序

1. 记录故障发生时间、升级前后版本与 source SHA、Chart/image digest、入口实际路由、运行 release/namespace 与集群身份。不能仅由域名或镜像版本推断代际。
2. 用批准的只读诊断能力核对当前 Grafana 用户、组织 ID 和成员权限；比较管理视角与用户视角的 UID 清单。
3. 读取脱敏有效配置，确认数据库类型、数据目录/数据库身份引用、卷挂载与 PVC/PV 绑定。检查 release/namespace 变化是否建立了新存储；不输出连接密码或 Secret。
4. 比对发布前后 ConfigMap、valuesFrom、provider 路径、组织绑定、bundle checksum、插件清单和启动导入错误。
5. 将预期清单与实际 API 清单逐项对比：UID、folder、datasource、关键 panel、变量。单独运行代表性查询识别“存在但无数据”。
6. 检查源卷、旧数据库和备份是否仍存在及可读，记录可恢复对象范围；不覆盖、不删除、不初始化任何现场。

审计身份不得依赖管理员 kubeconfig、业务写账户或任意 exec；需要读取敏感配置时由受控接口返回脱敏结果，单独记录身份和权限证据。

## 4. 原因与处置映射

| 可能原因 | 应证明的事实 | 最小恢复方向 |
| --- | --- | --- |
| 组织/权限变化 | 对象仍在原组织，当前用户不可见 | 修复成员映射，不重导整个数据库 |
| 新实例/新库 | 存储身份变化、目标对象缺失 | 从包重建标准配置，评估运行状态迁移 |
| 漏带配置包 | provider/挂载/资源引用缺失 | 在配置 owner 修复并按 UID 重放 |
| provisioning 删除 | 来源变化与对象删除时间相符 | 保护证据，恢复批准对象并修复删除契约 |
| 插件/数据源异常 | 面板存在，渲染/查询失败 | 修复版本、UID 或连接，不重复导入同名面板 |
| 指标不匹配 | 原始指标存在但变量/标签过滤错误 | 修复查询契约，不将空值填零 |

最初优先调查“新部署身份未继承原存储/配置，且未加载旧包”。第 7 节已核实源端保留对象、目标端没有对象及面板挂载；这支持迁移交付遗漏，不支持源端面板全部被删除的说法。

## 5. 恢复步骤

保护当前与可用源状态 → 建立 UID 差异清单 → 在隔离环境演练面板重放 → 补齐已批准的数据源/插件依赖 → 核对组织和权限 → 按 owner PR/发布交付 → 验证 → 保留观察窗口。

先恢复原有平台面板，再开放客户组织。保持原 Dashboard、Folder 和 Datasource 的稳定标识，不为消除错误盲目生成新 UID。幂等重放不产生重复；未知同 UID 冲突必须先比较内容和所有者。

UI 自定义、成员、告警、联系人和加密配置不能靠导入标准面板恢复。若需要全库恢复，使用匹配版本/密钥的独立目标验证，不把备份直接覆盖当前活跃库。隔离恢复默认禁用生产通知。

数据库外置与本次最小面板恢复分别交付；不要为恢复面板顺带迁移全部数据库、重建集群、改变采集链路或删除旧卷。

## 6. 恢复验收与回执

每项记录环境标识（受控证据中）、观察时间、实际身份、源 SHA/digest、运行/任务 ID、预期与实际、退出码和脱敏产物校验值。

- 全部预期 UID 可见且 folder、datasource、关键 panel、变量匹配。
- Node、Process、Caddy、Xray 各有代表性查询证据；插件加载成功。
- 无流量时 Caddy 节点仍可发现，避免重复采集计数；Xray 指标维度与流量计数语义正确。
- 权限正确的用户可见，无权限用户不可见，UI 交互和数据新鲜度符合约定。
- 至少再次调谐并检查幂等；重启后对象保留，备份恢复可重复。
- 记录未恢复的自定义/告警/历史数据等缺口，未验证项标 `NOT_RUN` 或 `BLOCKED`，不可填 PASS。

镜像回退不保证数据库回退。恢复后已有新写入时，必须有增量核对或独立恢复方案。只有用户边界、数据源边界与观察窗口均通过，才关闭恢复事项。

## 7. 2026-11-03 V5/V6 现场只读对比补充

用户重新开机后授权检查 V5，SSH 可用，初检 uptime 约 10 分钟、K3s active，源观测 Pod 为 5/5 Running。检查时间为 2026-11-03 14:36–14:37（Asia/Shanghai）；源目标主机身份由用户授权和既有迁移归档对应，本公开记录不复制连接地址、卷 UUID 或凭据。

本次使用 root 管理身份执行只读命令，未建立或证明独立审计身份的权限隔离。Kubernetes 查询经进程筛选，SQLite 以 `mode=ro`、`query_only=ON` 和读取事务查询，未读取密码、Token、私钥或业务表内容。未主动重启、暂停 Flux、恢复数据库、导入面板、切换 DNS 或修改线上配置。服务自行启动和控制器调谐属于现场背景状态。

| 检查项 | V5 源端实际值 | V6 目标端实际值 |
| --- | --- | --- |
| Grafana 镜像 | 13.2.4，digest 与目标相同 | 13.2.4，digest 与源相同 |
| Grafana 数据文件 | 原 PVC 上 SQLite，3,837,952 bytes | 独立新 PVC 上 SQLite，1,626,112 bytes |
| 新版 `resource` 当前 Dashboard | 21 | 0 |
| 新版 `resource` 当前 Folder | 3 | 0 |
| 新版 Dashboard 历史条目 | 44 | 0 |
| 数据源 | 3 个，使用原稳定 UID | 3 个，但 UID 已改变 |
| 用户记录数量 | 2 | 1 |
| 面板文件挂载 | imported providers 和 Platform 文件存在 | 没有面板文件挂载 |
| 数据源/应用配置 | 原专用 ConfigMap、runtime Secret 引用存在 | 仅默认数据源配置，无对应 runtime/app 引用 |

源端目录为 Platform、Observability Alerts、Controlled acceptance。用户数量仅用于比较状态，不导出身份信息。数据库文件大小不是完整性或可恢复性证明。

### 7.1 Grafana 新版存储计数陷阱

源端旧 `dashboard` 表只有 3 行：两个旧 folder 记录和一个 Platform Dashboard；但是新版 `resource` 中实际保留 21 个 Dashboard 与 3 个 Folder。不能以旧表行数宣称只剩一个面板，也不能只搬旧表恢复面板。

此处数字来自实际新旧 schema 和筛选后的元数据读取，不是仅从 ConfigMap 数量推断。恢复清单应优先通过适配该版本的 Grafana API/owner 导出能力生成，再与新版资源存储交叉核对，不直接手工向 `resource` 表写入。

### 7.2 源端保留的 21 个 Dashboard UID

| UID | 标题 |
| --- | --- |
| `StarsL-JOB-node` | Node Exporter Dashboard 20240520 通用JOB分组版 |
| `StarsL_cn_K8S` | K8S Dashboard CN 20240513 StarsL.cn |
| `agent-ai-observability` | Agent / AI Application Observability |
| `ai-aggregator-overview` | AI Aggregator Overview |
| `begqoward2epsf` | Xray Dashboard |
| `blackbox-exporter-overview` | Blackbox Exporter & SSL Probe Overview |
| `cmdb-resource-overview` | CMDB · 多云资源总览 |
| `fed94ifiv8h6oc` | Caddy |
| `homepage-navigation` | 平台导航与总览 (Navigation Homepage) |
| `k6-performance-capacity-overview` | k6 Performance & Capacity Stress Test Dashboard |
| `postgres-exporter-overview` | PostgreSQL Database Overview |
| `postgres-unified-overview` | PostgreSQL 统一监控概览 |
| `process-exporter-with-tree` | process exporter dashboard with treemap |
| `serverless-fullstack-architecture` | 全栈无服务器与边缘架构总览 (Serverless & Edge Full-Stack Topology) |
| `victoria-logs-overview` | Victoria Logs Overview |
| `victoria-traces-overview` | VictoriaTraces Distributed Tracing APM |
| `wGgaPlciz` | Postgres Overview |
| `web-saas-k3s-v5-overview` | Web-SaaS K3s V5 PROD Cluster Overview |
| `xconnect-comprehensive` | XConnect 综合监控 |
| `xconnect-user-connection-diagnostics` | XConnect 用户慢连接诊断 |
| `xhttp-edge-reliability` | XHTTP Edge Reliability |

源端实际挂载的标准 JSON 清单是 19 个，数据库中有 21 个；因此只复制挂载文件并不能证明全部面板恢复。两个额外对象为 PostgreSQL 统一监控概览和 Postgres Overview；须比较数据库/API 现状与仓库较新配置，不能未经核对就断言它们是用户自定义或已纳入目标交付。

### 7.3 数据源 UID 差异

| 数据源 | V5 UID | V6 UID |
| --- | --- | --- |
| VictoriaMetrics | `victoriametrics` | `P4169E866C3094E38` |
| VictoriaLogs | `victorialogs` | `PD775F2863313E6C7` |
| VictoriaTraces | `victoriatraces` | `P14D5514F5CCC0D1C` |

只导入面板而不保留/显式映射数据源 UID，会引入找不到数据源或变量引用不闭合的问题。恢复必须一起处理目标连接地址、UID、凭据引用与所需插件，而不是直接复制源端私密配置。

### 7.4 迁移步骤实际缺口

现有[迁移运行手册](../../../content/02-iac-devops/cloud-infrastructure-devsecops-baseline/records/prod-v5-v6-20261103/migration-runbook.zh.md)的独立数据阶段针对 Vault 与 Accounts 迁移 API，服务调谐阶段检查 Ready 和 Datakit 内存；没有 Grafana 面板/组织配置导出、目标导入及逐 UID 验收。这是流程范围漏项，不能把 Accounts 表迁移完成当作 Grafana SQLite 或新版资源已迁移。

后续应补充独立 Grafana 阶段，依次完成：

1. 保护源/目标恢复点，按实际版本导出全部 21 个 Dashboard、3 个 Folder、数据源 UID 与插件/应用依赖；配置导出和数据库备份分开管理。
2. 比较源 API/数据库对象与固定 GitOps 包，明确两者差异、用户编辑及目标专用参数；保持稳定 UID。
3. 在隔离目标验证受控导入/重建，不照搬源数据库、凭据或生产告警通知；按批准对象范围迁移。
4. 在目标 GitOps 资源图接入完整面板包、provider、数据源及插件配置，不只临时 UI 导入。
5. 逐 UID 对比 21 个面板、3 个目录及数据源引用，执行代表查询、变量/插件渲染、重启和再次调谐验收。
6. 保留 V5 和备份至观察完成。独立 `grafana` PostgreSQL 数据库迁移另阶段完成，可使用业务共用实例，不阻塞最小面板恢复。

结论：已确认源端面板仍在，目标端缺面板对象和交付挂载；结合固定声明与迁移手册，确认漏了 Grafana 配置迁移/交付及完整性验收。尚未确认全部历史指标/日志/链路是否迁移，未验证浏览器实际可见性，也未执行任何恢复。

### 7.5 随后执行的最小恢复与结果

用户随后明确要求先修复当前 Grafana 面板，已通过 [GitOps #775](https://github.com/ai-workspace-infra/gitops/pull/775) 交付；[CI run 41591716846](https://github.com/ai-workspace-infra/gitops/actions/runs/41591716846) 的 YAML 声明检查和凭据扫描通过。合并提交为 `fa0a6997a31dfbd40829258c0ec73b05c5c831b6`，现有 Flux 单元消费该提交，未更换 Chart/image 版本、PVC 或数据库类型，未改 DNS 或业务库。

恢复复用了已版本化标准面板，并通过源端 GET-only API 读取两个补充面板，使用已有 Playbooks 配置 renderer 校验及规范化。21 个源 Dashboard UID、3 个 Folder UID 和 3 个 Datasource UID 保留；必要插件固定为 `victoriametrics-logs-datasource@0.33.1` 和 `marcusolsson-treemap-panel@2.1.1`。源身份联查应用未在未验证目标凭据前启用。

2026-11-03 14:46:12（Asia/Shanghai）经当前公网 Grafana 登录态 API 验证：

- 21 个预期 Dashboard UID 全部返回，无缺项、无额外替代面板；3 个目录及数据源标识匹配。
- 两项必要插件已安装并返回上述版本；公开健康接口为 database `ok`、版本 `13.2.4`。
- Grafana 到 VictoriaMetrics 的查询已成功，`count(up)` 返回 5。
- `count(node_uname_info)`、`count(namedprocess_namegroup_num_procs)`、`count(caddy_config_last_reload_successful)`、`count(xray_up)` 均为查询成功但空结果。面板清单恢复不等同全部指标或采集链路恢复；此项保留独立排查。

本次不是数据库备份恢复或历史遥测迁移，也未验证客户租户隔离、身份联查、浏览器全部变量/插件渲染。第 7 节前半部分是修复前证据，不应与本节修复后状态混为同一时点。PostgreSQL 后续使用共用实例内独立 `grafana` 数据库，尚未执行迁移。
