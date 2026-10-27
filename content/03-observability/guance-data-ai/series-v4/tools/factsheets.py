import sys,os; sys.path.insert(0,os.path.dirname(__file__))
from titles import TITLES
U={'版本区分':'https://docs.guance.com/plans/differences/','注册免费版':'https://docs.guance.com/plans/free/','免费版订阅协议':'https://docs.guance.com/agreements/free-agreement/',
'OpenTelemetry 采集器':'https://docs.guance.com/integrations/opentelemetry/','Prometheus Remote Write 采集器':'https://docs.guance.com/integrations/prom_remote_write/','Log Streaming 采集器':'https://docs.guance.com/integrations/logstreaming/',
'Open API':'https://docs.guance.com/open-api/','仪表板入门':'https://docs.guance.com/getting-started/get-started-with-dashboards/','场景 FAQ':'https://docs.guance.com/scene/faq/',
'PromQL 查询':'https://docs.guance.com/scene/visual-chart/chart-promql-query/','阈值检测':'https://docs.guance.com/monitoring/monitor/threshold-detection/','SSL 拨测':'https://docs.guance.com/synthetic-tests/request-task/ssl/','HTTP 拨测':'https://docs.guance.com/synthetic-tests/request-task/http/',
'Terraform Provider GuanceCloud/guance':'https://registry.terraform.io/providers/GuanceCloud/guance/latest/docs','Cloudflare Workers 定价':'https://developers.cloudflare.com/workers/platform/pricing/','Cloud Run 定价':'https://cloud.google.com/run/pricing','Supabase 定价':'https://supabase.com/pricing'}
TODO={'Agent 监测（待核验）':'https://docs.guance.com/agent/','更新日志（待核验 Codex 集成）':'https://docs.guance.com/release-notes/','AI 能力 / Obsy Copilot（待核验）':'https://docs.guance.com/ai/','商业版计费（待核验）':'https://docs.guance.com/billing-method/commercial-plan-billing/','RUM 接入（待核验）':'https://docs.guance.com/real-user-monitoring/'}
S={
'01':(['版本区分','注册免费版','免费版订阅协议','Open API','Terraform Provider GuanceCloud/guance','OpenTelemetry 采集器','Cloudflare Workers 定价','Cloud Run 定价','Supabase 定价'],[],'Cloudflare Pages/Workers、Cloud Run、Supabase Free、观测云免费专区（北京）；DataKit 版本【待实测】；Provider 0.1.0（community）','UAT 一条登录 / 内容读取链路：DataKit 主机与 Trace、RUM、拨测','观测云免费版 0 元；Cloudflare / Cloud Run / Supabase 按各自免费条件；超出部分按真实账单【待实测】'),
'02':(['场景 FAQ','仪表板入门','PromQL 查询','Prometheus Remote Write 采集器','版本区分','Terraform Provider GuanceCloud/guance'],[],'自建 Grafana + VictoriaMetrics + VictoriaLogs；grafanaCovertToGuance 版本【待实测】；沿用 #01 空间','3 个面板：资源健康、API 流量与错误、k6 压测延迟；历史数据不迁','双写期间额度占用【待实测】；修正工时记录'),
'03':(['版本区分'],['RUM 接入（待核验）'],'UAT 前端（AI 生成页面）；RUM SDK 版本【待实测】','UAT 页面会话；生产不接','计入每天 5,000 PV；会话重放每天 2,000 个'),
'04':(['OpenTelemetry 采集器','版本区分','Supabase 定价'],[],'Cloudflare Workers、Cloud Run、Supabase Free；OTel Collector + DataKit opentelemetry','UAT 登录链路一条','计入每天 20,000 Trace（与 Agent 监测共用）'),
'05':(['版本区分','阈值检测','SSL 拨测'],[],'自建 Grafana 告警规则；观测云监控器（仅阈值检测）','现有告警规则（条数是否公开待确认）','监控器 ≤10 个；拨测计入每天 20 万次'),
'06':(['版本区分'],['Agent 监测（待核验）','更新日志（待核验 Codex 集成）'],'Codex（主线工具）；Agent 监测接入方式【待授权空间实测】','开发任务的 Agent 元数据；不采凭据与完整 Prompt','计入 Trace 额度；Agent Monitoring 权益单独核验'),
'07':(['版本区分'],['Agent 监测（待核验）','商业版计费（待核验）'],'订阅制与按量 API 并存；AgentMeter 权益【待授权空间实测】','一周任务的 Token 与交付记录（脱敏）','按真实账单；订阅不按单次 API 价格折算'),
'08':(['阈值检测','版本区分'],['Agent 监测（待核验）'],'Agent 长任务；阈值检测规则','重复工具调用与重试元数据；禁采凭据、Token 原文、完整 Prompt','计入 Trace 额度与监控器名额'),
'09':(['版本区分'],[],'GitHub Actions、release tag、Cloud Run revision','发布前后同时长窗口','计入采集额度'),
'10':(['仪表板入门','Open API'],['AI 能力 / Obsy Copilot（待核验）'],'Obsy Copilot 或只读 MCP；Copilot、OWL/MCP 权益单独核验','一次告警相关的指标、日志、Trace（只读）','权益是否收费【待授权空间实测】'),
'11':(['HTTP 拨测','SSL 拨测','版本区分'],[],'自建 Grafana + Blackbox Exporter；观测云拨测（中国节点）','UAT 服务入口与自建监控入口；受控故障只在 UAT','计入每天 20 万次拨测'),
'12':(['版本区分','注册免费版','免费版订阅协议'],['商业版计费（待核验）'],'本季全部接入组件','本季 UAT 链路的用量、账单、排障与工时记录','按真实工作空间记录；无账单估算须写明假设'),
}
for k,(src,todo,env,scope,cost) in S.items():
    d=[x for x in TITLES if x.startswith(k)][0]; w,x,tp,st=TITLES[d]
    with open(f'{d}/sources.md','w') as f:
        f.write('# 来源\n\n已核验（页面抓取日期 2026-10-27，发布前 48 小时复核）：\n\n'+''.join(f'- 观测云 {n}：{U[n]}\n' if not any(n.startswith(p) for p in ('Terraform','Cloudflare','Cloud Run','Supabase')) else f'- {n}：{U[n]}\n' for n in src))
        if todo: f.write('\n待核验（成稿前必须抓取并确认）：\n\n'+''.join(f'- {n}：{TODO[n]}\n' for n in todo))
    with open(f'{d}/fact-sheet.md','w') as f:
        f.write(f'''# Fact sheet｜{w}

| 项 | 内容 |
| --- | --- |
| 状态 | {st}｜模板：{tp} |
| 时间范围 | 官方文档核验：2026-10-27；实测窗口：【待实测】（起止日期实测时填写） |
| 环境 / 版本 | {env} |
| 数据范围 | {scope}；UAT 与生产严格分离，生产数据不进入本篇 |
| 证据来源 | 见 sources.md；实测截图：【待实测截图】（脱敏后才可使用） |
| 隐私 | 不采凭据、Token 原文、完整 Prompt、邮箱、Cookie、IP；截图打码 workspace token、URL 参数、用户 ID |
| 合作披露 | 正文按要求不含署名与合作披露行；是否属于合作内容、免费版商业用途书面授权（协议 4.7）状态：【待确认】 |
| 权益 | 免费专区 Open API 受限；公开 Terraform Provider 不代表免费空间有控制面 API；Copilot、Agent Monitoring、AgentMeter、OWL/MCP 为独立权益，逐项核验 |
| 成本口径 | {cost} |
| 可迁移性 | 遥测到达不等于数据可迁移；原始数据以自建存储为准，声明保存在 Git |
| 篇幅 | 默认公众号 ≤1500 字、小红书 600–800 字；最终篇幅与版式以合作方确认为准 |

## 发布后反馈（发布后填写）

- 发布日期 / 渠道：
- 读者问题与更正：
- 数据更新（实测替换【待实测】项）：
- 合作方意见：
''')
print('ok')
