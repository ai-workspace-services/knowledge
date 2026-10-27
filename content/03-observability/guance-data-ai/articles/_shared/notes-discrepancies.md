# 核验与差异记录（内部，不发布）

- 核验日期：2026-10-27（北京时间），全部来源以 curl 抓取当日页面；快照在 `_sources/`。
- 规则：页面与 brief 不一致时以页面为准；与知识库大纲冲突处列在第 2 节。

## 1. 官方页面 vs brief

| # | brief 说法 | 官方页面（2026-10-27） | 处理 |
| --- | --- | --- | --- |
| 1 | 免费专区在“北京” | 版本区分页没有写“北京”；“免费专区（北京）节点”出现在《注册免费版》页（docs.guance.com/plans/free/） | 文中加引《注册免费版》作为来源 |
| 2 | 1 万时间线 | 版本区分页写“10,000 条时间线”，不带“/天” | 文中不写“每日” |
| 3 | 每日 2 万 Trace | “每天 20,000 个”，且注明含应用性能监测与 Agent 监测（共用额度） | 一致；共用口径写入备注 |
| 4 | 5,000 PV | “每天 5,000 个” | 一致 |
| 5 | 10 个监控器 | 最多 10 个，且**仅支持阈值检测** | 文中补“仅阈值检测” |
| 6 | 超额不再上报 | 版本区分页一致；协议 3.2 另称超额时观测云**有权暂停或限制服务使用权限** | 公众号未展开；建议发布前视篇幅补一句 |
| 7 | 不支持 OpenAPI 获取和更新工作空间数据 | 一致（“API Key：不支持通过调用 Open API 接口获取和更新工作空间数据”） | 一致 |
| 8 | 合作空间先确认站点 endpoint | Open API 页公布的 SaaS endpoint 列表（杭州、宁夏、广州、香港、俄勒冈、法兰克福、新加坡×2、南非、雅加达）中**没有免费专区（北京）** | 支持“免费空间远端 API 不可用”的判断；合作空间必须先确认实际站点 |
| 9 | Terraform 管理 Dashboard/Monitor | GuanceCloud/guance Provider（Registry 最新 0.1.0，2026-06-18 UTC 发布，community 层）有 `guance_dashboard`、`guance_monitor`、`guance_monitor_json` 等资源，基于 Open API、用工作空间 API Key；文档中只有 `guance_monitor_json` 写明 `terraform import`，Dashboard 未写 | 文 2 写明“Dashboard import 需实测” |
| 10 | Grafana 面板迁移 | 仪表板入门页：支持界面导入 Grafana JSON，并提示“部分高级特性……可能无法正常显示或需要手动重新配置”；场景 FAQ 提供 `grafanaCovertToGuance` 脚本 | 一致：不承诺直接兼容 |
| 11 | PromQL/**LogQL** → DQL | 现有栈是 VictoriaLogs（**LogsQL**），未部署 Loki（知识库核验记录 + observability 仓库） | 正文与图改为 LogsQL；观测云图表支持 PromQL 模式，故写“PromQL 模式 / DQL” |
| 12 | 免费版缺平台脱敏 | 一致（不支持敏感数据脱敏 / 扫描） | 一致 |
| 13 | Supabase Free 不预设 Log Drain / 完整查询可视 | Free：Log Drain 不包含；Metrics endpoint 不包含；API 与数据库日志保留 1 天；闲置 1 周暂停；最多 2 个活跃项目；500 MB 数据库、5 GB 出口 | 一致，补充事实已写入 |
| 14 | Cloudflare 条件 | Workers Free 每天 100,000 请求、单次 10 ms CPU；Paid 每账号每月最低 5 美元（含 1,000 万请求、3,000 万 CPU 毫秒/月）；静态资源请求免费不限量；Pages Functions 按 Workers 计费 | 已写入 |
| 15 | Cloud Run 条件 | 请求计费：每月前 180,000 vCPU 秒、360,000 GiB 秒、200 万请求免费（基于 us-central1 价格，按结算账号跨项目汇总）；实例计费：240,000 vCPU 秒、450,000 GiB 秒；价格随地区变化；Cloud Build / Artifact Registry 另计 | 已写入（文中写请求计费模式；**需确认实际计费模式与 region**） |
| 16 | brief 用字“薍羊毛” | 疑为“薅羊毛”的输入法错字 | 稿件统一用“薅羊毛”，如确为有意请改回 |
| 17 | 自建站点 observability-k3s-v5.svc.plus | 知识库路线图写的是 observability.svc.plus | 按 brief 用 observability-k3s-v5.svc.plus，请确认 |
| 18 | Terraform 管理获授权的 SaaS 资源 | iac_modules README：Terraform 在该仓库只负责 compute / network / storage / identity，软件配置归 playbooks；且仓库实际用 OpenTofu CLI | 文中只写“renderer 生成 HCL、Terraform plan”；把观测云资源纳入 iac_modules 属于**新增范围**，需作者确认归属 |
| 19 | 免费服务稳定性 | 协议 2.2/10.2/10.4：可修改、暂停或终止，不保证永久；10.3.2 可提前 15 天通知终止 | 文 1 第六节写入 |

## 2. 知识库大纲（ai-workspace-services/knowledge）vs brief

读取的文件（只读，main 分支，未提交任何改动）：
`content/03-observability/guance-data-ai/` 下 README.md、00-annual-content-plan.md（仅确认存在，未逐段采用）、01-guance-research-brief.md（同上）、02-xworktech-guance-integration-roadmap.md、03-fact-check-2026-10.md、articles/README.md、articles/01-free-tier-for-indie-saas/outline.md、articles/02-observability-migration-with-rollback/outline.md、articles/02-observability-migration-with-rollback/migration-matrix.md、assets/README.md。

| # | 冲突点 | 大纲 | brief | 本稿处理 |
| --- | --- | --- | --- | --- |
| A | 文 1 标题与起点 | 《个人 SaaS 为什么先试观测云免费专区》；起点是自建 Vector/VictoriaMetrics/Grafana 栈 | 起点是 Cloudflare + Cloud Run + Supabase 低成本栈 | 用 brief 标题与顺序；第二节保留大纲“自建栈已在工作、缺 RUM/跨信号”的论点（两者 1:1 对应：起点→为什么 SaaS→边界→动手→7 天判断→结论） |
| B | 文 1 动手方式 | 5 步 UI 操作（申请、装 DataKit、OTel exporter、RUM、拨测） | 核心是 IaC/GitOps/Playbook 自动化，不写逐步点击 | 按 brief；大纲中 DataKit + OTel Collector exporter 作为 Playbook 部署对象保留 |
| C | 文 1 商业版估算 | 给出估算 ¥870/月、¥3,700/月（基于 3.6 万序列、15 秒间隔假设，标“未经确认”） | 未要求 | 不引用数字，改为“7 天用量后按官方单价估算【待实测】” |
| D | 作者环境规模 | 约 11 台主机、3.6 万序列、11 个仪表板、9 条告警（“公开前需作者确认”） | 未提 | 未写数字，用【待作者确认是否公开】 |
| E | Trace 额度 | 大纲记录 `/free` 落地页写 1 万/天、`/billing` 与版本区分页 2 万/天 | 2 万/天 | 以版本区分页 2 万为准（本次未复抓 guance.com/free 与 /billing，发布前复核） |
| F | 免费版能否 GitOps | 文 2 大纲：“无 OpenAPI（无法 GitOps 与自动对账，只能 UI 导出）” | 采集端仍可 GitOps；Terraform 只做离线生成 | 按 brief：采集端 GitOps 可行，远端面板不可 |
| G | 文 2 范围 | 11 个仪表板、9 条告警、四个开关、六阶段、7 条切换标准、15 分钟回退目标、8 个验证实验 | 首批 3 个面板（资源健康 / API 流量与错误 / k6 压测延迟） | 按 brief 的 3 个面板；吸收大纲的开关（默认关）、并行对照、切换条件、回退步骤；15 分钟目标未写死，回退耗时【待实测】 |
| H | 文 2 Grafana 导入时间 | “2026-04-01 起支持 UI 导入” | — | 当日仪表板入门页未见日期，正文不写日期 |
| I | XHS 分页 | 两篇大纲各有不同的 8 页 | brief 指定 8 页 | 按 brief |
| J | UAT 域名 | 大纲与路线图使用 UAT 控制台域名 | 只允许两个公开域名 | 未写入稿件 |
| K | 披露 | 大纲要求写明内容合作，并取得 XWorkTech 使用免费版的书面授权；未落实则改用非商业 side project | brief 要求合作权益单列 | 两篇均加披露；授权状态为【待确认】 |

## 3. 仓库角色（只读 README，未改动）

- ai-workspace-infra/gitops：权威声明层，存 Kubernetes/Flux 资源、非敏感多环境参数、IaC 拓扑声明；不放任何密钥，凭据经 Vault 运行时下发。
- ai-workspace-infra/iac_modules：读取 GitOps 声明，用 Python + Jinja2 渲染显式 HCL，按环境 apply，产出 CMDB 供 Ansible 使用；当前 Terraform 范围限于计算/网络/存储/身份（见差异 18）。
- ai-workspace-infra/playbooks：按 role 组织的 Ansible 控制面，含可观测性栈部署；团队模式经 Vault 注入凭据。
- ai-workspace-infra/platform-ops-toolkit：AI 驱动的迁移自动化与平台工具（Gitea/Actions、Vault + Zitadel 安装等），提供 `setup-iac-env` 等流水线入口。
- 观测栈仓库 ai-workspace-infra/observability：安装入口复用 playbooks 的 roles。
