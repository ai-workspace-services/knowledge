# Grafana 面板丢失排查与恢复规划

日期：2026-11-03。状态：故障输入已记录、声明缺口已核对，现场根因与恢复未验收。需求：[Knowledge #351](https://github.com/ai-workspace-services/knowledge/issues/351)。[完整规划](Pro-Custom与Grafana升级完整规划.md) · [持久化](Grafana独立PostgreSQL与GitOps持久化规划.md) · [交付验收](Pro-Custom与Grafana分阶段交付验收规划.md)

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

本轮此前公开健康响应为 Grafana `13.2.4`、database `ok`，只证明当时该接口的进程/数据库健康；没有登录面板、核对数据库对象或确认运行发布来源。

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

优先调查“新部署身份未继承原存储/配置，且未加载旧包”，但在完成上述核验前保持假设状态。

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
