import os,sys
sys.path.insert(0,os.path.dirname(__file__))
from _v3_defs import H,B,G,Y,R,D as V3
def v3(name):
    for art,ds in V3.items():
        if name in ds: return ds[name]
    raise KeyError(name)
N={}
N['onboarding-pipeline']=('TB',f'''
ai [label="AI 起草\\n接入清单 · 声明 · 配置 · PR 说明", shape=ellipse, fillcolor="#FFFFFF"];
g [label="GitOps\\n非敏感环境参数 · 监控意图", {B}];
pr [label="PR 审查", {Y}];
r [label="iac_modules renderer\\n显式 HCL", {B}];
tf [label="terraform plan\\n人审 plan", {Y}];
pb [label="Playbook\\nDataKit · OTel Collector 配置", {B}];
v [label="Vault\\n运行时注入 · 凭据分开", {G}];
q [label="空间支持 Open API？", shape=diamond, style=filled, {Y}, margin="0.05,0.05"];
ap [label="apply 远端资源", {G}];
blk [label="免费空间：apply 被阻断", style="rounded,filled,dashed", {R}];
ai -> g -> pr; pr -> r -> tf -> q; q -> ap [label="是"]; q -> blk [label="否"]; pr -> pb; v -> pb [style=dashed]; v -> tf [style=dashed];
''')
N['signal-scope']=('LR',f'''
s [label="首批接入范围", fillcolor="#FFFFFF"];
a [label="DataKit\\n主机 · Trace 接收", {B}];
b [label="RUM\\n浏览器 SDK · 隐私遮罩", {B}];
c [label="拨测\\nHTTP · SSL", {B}];
w [label="观测云免费空间\\nUAT 数据", {G}];
s -> a -> w; s -> b -> w; s -> c -> w;
''')
N['rum-pipeline']=('TB',f'''
br [label="浏览器\\nRUM SDK · 隐私遮罩", fillcolor="#FFFFFF"];
w [label="观测云 RUM", {B}];
p [label="页面加载 · 资源 · JS 错误", {B}];
t [label="后端 Trace\\n按 trace_id 关联", {G}];
br -> w -> p; p -> t [style=dashed];
''')
N['ux-before-cpu']=('TB',f'''
c [label="用户反馈：页面卡", fillcolor="#FFFFFF"];
a [label="先看用户体验\\n页面耗时 · 慢资源 · 错误", {G}];
b [label="再看服务端\\nTrace 慢 span", {B}];
d [label="最后看资源\\nCPU · 内存", {Y}];
c -> a -> b -> d;
''')
N['alert-as-code']=('TB',f'''
ai [label="AI 草拟告警规则\\n含触发条件与处置动作", shape=ellipse, fillcolor="#FFFFFF"];
g [label="GitOps 监控声明", {B}];
pr [label="PR 审查\\n是否值得打断", {Y}];
r [label="renderer\\nguance_monitor HCL", {B}];
p [label="terraform plan", {Y}];
blk [label="免费空间 apply 被阻断", style="rounded,filled,dashed", {R}];
ai -> g -> pr -> r -> p -> blk [style=dashed];
''')
N['agent-chain']=('LR',f'''
t [label="一次 Codex 任务", fillcolor="#FFFFFF"];
s [label="Session", {B}];
c1 [label="模型调用", {B}];
c2 [label="工具调用", {B}];
o [label="交付结果\\nPR · 提交 · 失败", {G}];
t -> s; s -> c1; s -> c2; c1 -> o; c2 -> o;
''')
N['agent-ingest']=('TB',f'''
a [label="Agent 运行环境", fillcolor="#FFFFFF"];
f [label="采集前过滤\\n不采凭据 · 不采完整 Prompt", {R}];
dk [label="Agent 监测接入", {B}];
q [label="Trace 额度\\n与应用性能监测共用", {Y}];
a -> f -> dk -> q;
''')
N['token-attribution']=('LR',f'''
s [label="Session", fillcolor="#FFFFFF"];
tk [label="Token 用量", {B}];
task [label="任务", {B}];
d [label="交付证据\\nPR · release tag · 验证结果", {G}];
s -> tk -> task -> d;
''')
N['cost-scope']=('TB',f'''
c [label="成本口径", fillcolor="#FFFFFF"];
a [label="订阅计划\\n不能按单次 API 价格折算", {Y}];
b [label="按量 API\\n按调用计费", {B}];
w [label="观测数据费用\\n按真实工作空间记录", {B}];
e [label="无账单时的估算\\n写明假设", {R}];
c -> a; c -> b; c -> w; w -> e [style=dashed];
''')
N['loop-detect']=('TB',f'''
s [label="Agent Session", fillcolor="#FFFFFF"];
r [label="重复工具调用 · 重试", {Y}];
m [label="按 Session 聚合\\n调用次数 · 时长", {B}];
a [label="阈值检测\\n避免高基数分组", {B}];
h [label="人判断\\n终止或改提示", {G}];
s -> r -> m -> a -> h;
''')
N['never-collect']=('LR',f'''
in [label="Agent 遥测字段", fillcolor="#FFFFFF"];
ok [label="保留\\nsession · tool 名 · 耗时 · 状态", {G}];
h [label="哈希或聚合\\n用户 · 仓库标识", {Y}];
no [label="不采集\\n凭据 · Token 原文 · 完整 Prompt", {R}];
in -> ok; in -> h; in -> no [style=dashed, color="#D64545"];
''')
N['release-window']=('LR',f'''
gh [label="GitHub Actions run", fillcolor="#FFFFFF"];
tag [label="release tag", {B}];
rev [label="Cloud Run revision", {B}];
ev [label="发布事件", {Y}];
cmp [label="同一时长窗口\\n发布前 vs 发布后", {G}];
gh -> tag -> rev -> ev -> cmp;
''')
N['before-after']=('TB',f'''
e [label="发布事件", {Y}];
a [label="发布前窗口\\n错误率 · 延迟 · RUM", {B}];
b [label="发布后窗口\\n错误率 · 延迟 · RUM", {B}];
d [label="判定\\n保持 · 观察 · 回滚", {G}];
e -> a; e -> b; a -> d; b -> d;
''')
N['ai-triage']=('TB',f'''
al [label="告警事件", fillcolor="#FFFFFF"];
ai [label="AI 助手\\nObsy Copilot 或只读 MCP", {B}];
q [label="只读查询\\n指标 · 日志 · Trace", {B}];
l [label="线索清单\\n证据链接 · 假设", {Y}];
h [label="人决定处置", {G}];
x [label="不自动修复", style="rounded,filled,dashed", {R}];
al -> ai -> q -> l -> h; ai -> x [style=dashed, arrowhead=none];
''')
N['least-privilege']=('LR',f'''
v [label="Vault", {G}];
k [label="只读查询 Key", {Y}];
m [label="MCP / Copilot", {B}];
w [label="写入 · 管理权限\\n不授予", {R}];
v -> k -> m; m -> w [style=dashed, color="#D64545", arrowhead=none];
''')
N['failure-domain']=('TB',f'''
subgraph cluster_a {{ label="同一故障域"; style="rounded,dashed"; color="#D64545"; fontsize=16;
 app [label="UAT 服务", {B}];
 mon [label="自建监控\\nGrafana 告警", {G}];
}}
ext [label="外部拨测\\n平台节点", {B}];
f [label="受控 UAT 故障\\n不碰生产", {Y}];
f -> app; f -> mon [style=dashed]; ext -> app; ext -> mon [label="探测监控入口"];
''')
N['exit-choice']=('TB',f'''
s [label="一季结束", fillcolor="#FFFFFF"];
a [label="继续免费空间\\nPOC 范围", {G}];
b [label="升级商业版\\n按量付费", {B}];
c [label="退出\\n回到自建", {Y}];
r [label="依据\\n用量 · 账单 · 定位收益 · 维护工时", {B}];
s -> r; r -> a; r -> b; r -> c;
''')
N['portability']=('LR',f'''
t [label="遥测已到达", fillcolor="#FFFFFF"];
p [label="≠ 数据可迁移", {R}];
o [label="原始存储自持\\n声明在 Git", {G}];
t -> p; p -> o [style=dashed];
''')
ART={
'01-free-zone-onboarding':['quota-map','onboarding-pipeline','signal-scope','credential-split'],
'02-dashboard-semantic-reconcile':['json-to-plan','query-traps','side-by-side','switch-states'],
'03-rum-ai-page-slow':['ux-before-cpu','rum-pipeline','field-allowlist'],
'04-login-trace-across-clouds':['triage-path','stack-blindspots','evidence-chain','field-contract'],
'05-actionable-alerts':['alert-triage','alert-as-code','threshold-pipeline'],
'06-codex-tool-calls':['agent-chain','agent-ingest','never-collect'],
'07-token-to-delivery':['token-attribution','cost-scope','agent-chain'],
'08-agent-loops':['loop-detect','never-collect','threshold-pipeline'],
'09-release-before-after':['release-window','before-after','side-by-side'],
'10-ai-triage-clues':['ai-triage','least-privilege','evidence-chain'],
'11-who-monitors-monitoring':['failure-domain','probe-split','frequency-tiers','check-modes'],
'12-season-review-exit':['exit-choice','cost-scope','rollback-runbook','portability'],
}
root=os.path.join(os.path.dirname(__file__),'..')
for art,names in ART.items():
    d=f'{root}/{art}/diagrams/src'; os.makedirs(d,exist_ok=True)
    for n in names:
        rk,body=N[n] if n in N else v3(n)
        open(f'{d}/{n}.dot','w').write(H%rk+body+'}\n')
    print(art,len(names))
