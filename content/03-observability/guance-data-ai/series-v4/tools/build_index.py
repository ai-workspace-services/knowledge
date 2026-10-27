import sys,os,subprocess,glob; sys.path.insert(0,os.path.dirname(__file__))
from titles import TITLES
def cnt(p): return subprocess.check_output(['python3','tools/count.py',p]).decode().split()[1]
STAGE={'01':'第一月·接得上','02':'第一月·接得上','03':'第一月·接得上','04':'第一月·接得上','05':'第二月·看得懂 AI','06':'第二月·看得懂 AI','07':'第二月·看得懂 AI','08':'第二月·看得懂 AI','09':'第三月·守得住、退得出','10':'第三月·守得住、退得出','11':'第三月·守得住、退得出','12':'第三月·守得住、退得出'}
EV={'01':'UAT 首条数据到达截图；额度占比','02':'3 个面板同窗对照截图；转换修正记录','03':'RUM 文档抓取核验；UAT 页面会话截图','04':'Workers trace context 透传验证；Trace 瀑布图','05':'告警演练事件截图；名额占用','06':'Agent 监测文档 + Codex 集成核验；执行链截图','07':'AgentMeter 权益核验；一周 Token 与交付记录','08':'Agent 循环受控复现；阈值规则效果','09':'同窗发布前后数据；revision / release_tag 关联','10':'Copilot / OWL / MCP 权益核验；一次告警线索记录','11':'UAT 受控故障演练；免费版拨测频率档位','12':'一季账本；退出演练记录'}
PRE={'01':'书面商用授权【待确认】；免费空间 apply 阻断【待授权空间实测】','02':'Remote Write keep_exist_metric_name；双写开关默认关','03':'RUM 只接 UAT；字段白名单','04':'OTel SDK 接入；写入 Token Vault 注入','05':'监控器 ≤10、仅阈值检测','06':'Agent Monitoring 独立权益；不采凭据与完整 Prompt','07':'订阅不按 API 单价折算；成本按真实工作空间','08':'不采凭据与完整 Prompt','09':'发布标签与 revision 进遥测字段','10':'AI 只读、不自动修复；查询 Key 单独授权','11':'受控故障只在 UAT，绝不碰生产','12':'遥测到达≠数据可迁移；空间不可解散'}
R=[('R1-otel-dual-target-portability','换平台演练：同一份 OTel 数据，能不能同时送进自建和观测云？','动手实操型','可替换 #08','UAT 双目标对账'),
   ('R2-ai-latency-model-vs-tool','AI 调用慢，是模型慢还是工具慢？','问答拆解型','可替换 #08','Agent 监测核验；分段耗时'),
   ('R3-readonly-mcp-explain','只给 AI 只读工具，它能解释异常吗？','动手实操型','可替换 #10','OWL / MCP 权益核验；受控异常解释')]
ks=sorted(TITLES)
rows=[];prow=[]
for k in ks:
    w,x,tp,st=TITLES[k]; n=k[:2]
    g=len(glob.glob(f'{k}/diagrams/gif/*-wechat.gif'))
    rows.append(f'| {n} | [{w}]({k}/wechat.md) | [{x}]({k}/xhs.md) | {tp} | {STAGE[n]} | {st} | {cnt(k+"/wechat.md")} | {cnt(k+"/xhs.md")} | {g} |')
    prow.append(f'| {n} | {w} | {tp} | {st} | {EV[n]} | {PRE[n]} |')
rr=[f'| {d[:2]} | [{t}]({d}/outline.md) | {tp} | {rep} | 替补大纲 | {cnt(d+"/outline.md")} |' for d,t,tp,rep,_ in R]
prr=[f'| {d[:2]} | {t} | {tp} | 替补大纲（{rep}） | {ev} | 只在 UAT；权益逐项核验 |' for d,t,tp,rep,ev in R]
open('index.md','w').write(f'''# 独立开发观察者计划：AI × 可观测 SaaS 首季（v4）

本季主题：AI 如何帮助一个个人 SaaS 被开发出来、被看懂、被持续运行。共 12 篇核心稿，另有 R1–R3 替补选题（不额外增加篇数）。

公众号结构：一段真实场景 → 一个知识点 → 最小实践 → 结果和局限 → 适用 / 不适用人群 + 决策表。小红书结构：一个冲突标题、一张链路图、一张脱敏实测图（【待实测截图】占位，不编造）、一个结论。默认篇幅：公众号 ≤1500 字，小红书 600–800 字，最终以合作方确认为准。

每篇目录：wechat.md、xhs.md、fact-sheet.md、sources.md、diagrams/（src 为 .dot，gif 为动图）。字数为可见非空白字符（不含图片行、链接地址与 Markdown 符号）。

## 核心 12 篇

| # | 公众号标题 | 小红书标题 | 模板 | 阶段 | 状态 | 公众号字数 | 小红书字数 | 动图数 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(rows)}

## 替补选题

| # | 标题 | 模板 | 用途 | 状态 | 大纲字数 |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(rr)}

阅读顺序为 01 → 12，每篇末尾有上一篇 / 下一篇链接，12 回到 01 形成闭环；相邻两篇模板不重复。季度计划见 [quarterly-plan.md](quarterly-plan.md)。
''')
open('quarterly-plan.md','w').write(f'''# 首季计划（v4）

## 本季弧线

- 第一月·接得上（01–04）：在 Cloudflare + Cloud Run + Supabase 的低成本栈上，用 AI 辅助 IaC 接入观测云免费专区，搬面板、看用户体验、接通一条登录链路。
- 第二月·看得懂 AI（05–08）：告警是否值得打断人；Codex 做了什么、Token 换来了什么、Agent 为什么原地打转。
- 第三月·守得住、退得出（09–12）：发布前后对比、AI 整理排障线索、外部拨测兜底，季末算账并演练退出。

## 12 篇 + 替补

| # | 标题 | 模板 | 状态 | 证据依赖 | 前提条件 |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(prow)}
{chr(10).join(prr)}

状态说明：全文稿 = 依据已核验官方文档成稿，实测数据仍标【待实测】；大纲 = 关键证据尚未就绪，只保留大纲与 fact sheet，证据补齐后再成稿。替补选题不额外增加篇数：R1 / R2 可替换 #08，R3 可替换 #10。

## 全季前提

- 所有接入走 AI 辅助的 IaC / GitOps / Playbook：AI 起草，人审 PR 与 plan；首次启用人工确认；不写控制台点击步骤。
- 免费专区 Open API 受限；公开 Terraform Provider 不等于免费空间有控制面 API，相关 apply 一律标【待授权空间实测】。
- 免费版订阅协议要求商业用途取得书面授权；授权状态【待确认】。
- Copilot、Agent Monitoring、AgentMeter、OWL / MCP 为独立权益，逐项单独核验。
- 成本按真实工作空间记录；估算必须写明假设。
- UAT 与生产严格分离；#11 的受控故障只在 UAT，绝不碰生产。
- 遥测数据到达不等于数据可迁移；原始数据以自建存储为准。
- #08 不采集凭据或完整敏感 Prompt；#10 不做自动修复。
- 管理 API Key、查询 Key、写入 Token 分开存放、分开授权，运行时由 Vault 注入，不进仓库与 CI 日志。

## 篇幅与发布

默认公众号 ≤1500 字、小红书 600–800 字；合作方可调整篇幅与版式。每篇发布前 48 小时复核 sources.md 中的官方页面，发布后在 fact-sheet.md 的反馈栏记录更正。
''')
print('ok')
