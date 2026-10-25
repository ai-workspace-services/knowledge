# 部署与迁移验收检查表（可复用执行附件）

本表是[统一流程](https://github.com/ai-workspace-services/.github/blob/main/docs/control-plane-deployment-and-migration.zh.md)的执行附件，不创建第二套权威流程。每轮复制到独立记录，用实际证据更新；不得把模板勾选当成执行。

## 执行信息

| 字段 | 本轮填写 |
| --- | --- |
| run_id / attempt | `<唯一运行标识>` / `<次数>` |
| 环境 / 源 / 目标 | `<环境>` / `<逻辑身份>` / `<逻辑身份>`；原始资源 ID 留在受控证据 |
| Asia/Shanghai 起止 | `<开始>` / `<结束>` |
| GitOps / IaC / Playbooks / Toolkit 固定 SHA | `<逐仓填写>` |
| 生产 tag、镜像/Chart digest | `<不可变引用>` |
| schema / migration checksum | `<版本、dirty、各自 checksum>` |
| 允许操作与审批引用 | `<只读、目标写入、DNS、停写、恢复分别填写>` |
| 数据范围 / 获准例外 | `<集合、时间边界、例外及确认依据>` |
| 备份 / 隔离恢复 / 单写者证据 | `<受控 evidence_id；缺失写 BLOCKED>` |

## Markdown TODO 表

`[x]` 仅对应 PASS；`[ ]` 对应 FAIL、BLOCKED、PARTIAL、NOT_RUN。例外必须写明批准依据与范围，不能冒充全量一致。每行证据需绑定 run_id/attempt、owner、固定 SHA、目标、带时区起止、退出码和可复核 evidence_id。缺失、无效或 skipped receipt 不得放行。

| 完成 | ID / 阶段 | 检查点 | 状态 | 验收标准 | 执行 owner / 工具 | 退出码 / 证据 / 待办 |
| --- | --- | --- | --- | --- | --- | --- |
| [ ] | C01 / S0 | 资源、CMDB、源/目标基线冻结 | NOT_RUN | 源/目标身份、CMDB、state/备份边界与固定运行绑定齐全 | IaC / provider, DNS, CMDB | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C02 / S0 | 固定生产版本 | NOT_RUN | 生产 tag/SHA、镜像/Chart digest 与实际运行对应 | Toolkit / ref 与 receipt gate | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C03 / S1 | 主机、服务与持久卷 | NOT_RUN | 独立目标资源、卷亲和性、服务、容量和连接身份正确 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C04 / S2/S5 | 公共 Web/DNS/TLS | NOT_RUN | 权威及公共解析、SNI/证书链、业务 Host 与路径正确 | IaC / provider, DNS, CMDB | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C05 / S2/S5 | PostgreSQL 外部入口 | NOT_RUN | DNS 与实际数据库协议/隧道分别通过；不以 HTTP 代替 | IaC / provider, DNS, CMDB | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C06 / S4 | Console/Accounts/Billing 健康 | NOT_RUN | 各服务返回其合同要求的响应并实际连接正确数据库 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C07 / S4 | 登录 POST 与 Session/MFA 路由 | NOT_RUN | 合法登录/会话与未授权路径正确；外部回调单列 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C08 / S4 | Billing 拒绝空 200 吞请求 | NOT_RUN | 认证拒绝、合法采集、重复投递语义均正确 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C09 / S3 | Schema 版本/dirty | NOT_RUN | schema version/dirty、结构和迁移包 checksum 正确 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C10 / S3 | 身份字段及批准例外 | NOT_RUN | 固定用户集合及核心身份逐字段一致；批准例外单列 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C11 / S3 | 套餐/订阅/账务范围 | NOT_RUN | 套餐、订阅、额度、财务、用量按批准范围与业务语义一致 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C12 / S3 | 订阅外键 | NOT_RUN | 外键、唯一约束、序列及未验证约束状态均有证据 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C13 / S4/S6 | 新流量入库 | NOT_RUN | 真实来源至少两个相关周期正增量落库并可查询 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C14 / S4/S6 | 全节点 Agent 心跳/配置下发 | NOT_RUN | 声明的全部节点身份唯一、心跳新鲜、配置下发成功 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C15 / S6 | 区域池/客户端实际连接 | NOT_RUN | 区域池返回正确并完成授权客户端真实连接 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C16 / S2/S4 | Flux/ESO 正式接管 | NOT_RUN | Flux/ESO Ready，固定 ref，允许及越界拒绝均验证 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C17 / S2/S7 | Vault Raft 与恢复演练 | NOT_RUN | Vault 正确后端、独立恢复、重启重新解封与持久化通过 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C18 / S2/S3 | Vault KV 双端一致性 | NOT_RUN | 批准路径的 path/key/value 双端比较；秘密不进入回执 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C19 / S2/S4 | GitHub ↔ 新 Vault | NOT_RUN | 精确 GitHub workload 绑定；正确身份成功，错误身份失败 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C20 / S4/S6 | Grafana/遥测/告警闭环 | NOT_RUN | 数据源、面板/变量/插件、metrics/logs/traces、内部告警闭环 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C21 / S6 | 真实登录及页面对账 | NOT_RUN | 账号持有者登录；页面与同一账号/窗口 API/DB 精确对账 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C22 / S7 | 三轮幂等及故障恢复 | NOT_RUN | 同输入三轮部署/迁移、并发锁、重试及隔离恢复分别通过 | Playbooks / Ansible, API, SQL, browser | `<exit/null>` / `<evidence_id>` / `<待办>` |
| [ ] | C23 / S5/S8 | 单写者交接与最终关闭 | NOT_RUN | 单写者、旧路径隔离、最终边界、观察及恢复计划完整 | Toolkit / ref 与 receipt gate | `<exit/null>` / `<evidence_id>` / `<待办>` |

## 关闭规则

- 环境重建、备份恢复、迁移重放、写入权交接和真实支付/通知不得由普通定时任务自动触发。
- 生产只读检查不能替代隔离环境中的冲突、回滚、中断恢复及故障注入。
- 协调三次成功不能替代 IaC 重建三次或迁移重放三次；各自记录次数与数据不变量。
- 目标有新增写入后，DNS 回退不能自动恢复旧库写入；必须先明确数据协调和单写者方案。
- 所有必需项完整 PASS 后才关闭。证据不足保持 BLOCKED/NOT_RUN；不为提高通过率删除必测项。

[本轮 V5 VPS → K3s 实例](prod-v5-vps-to-k3s-runtime-and-acceptance-20261025.zh.md)
