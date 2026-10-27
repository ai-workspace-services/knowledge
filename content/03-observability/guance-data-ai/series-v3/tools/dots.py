import os
H='''digraph G { rankdir=%s; graph [bgcolor="white", fontname="Noto Sans CJK SC", pad=0.4, nodesep=0.45, ranksep=0.55];
node [shape=box, style="rounded,filled", fillcolor="#F5F7FA", color="#9AA5B1", fontname="Noto Sans CJK SC", fontsize=18, margin="0.25,0.14", penwidth=1.4];
edge [color="#52606D", fontname="Noto Sans CJK SC", fontsize=15, penwidth=1.4, arrowsize=0.8];
'''
B='fillcolor="#EAF2FF", color="#4C7BD9"'
G='fillcolor="#EEF8F0", color="#3E8E5A"'
Y='fillcolor="#FFFBEA", color="#C99A06"'
R='fillcolor="#FFF4F4", color="#D64545", fontcolor="#9B2C2C"'
D={}
# ---------- 01 why: blindspots ----------
D['01-low-cost-stack-blindspots']={
'stack-blindspots':('TB',f'''
user [label="用户浏览器", fillcolor="#FFFFFF"];
subgraph cluster_run {{ label="业务链路"; style="rounded,dashed"; color="#CBD2D9"; fontsize=16;
 cf [label="Cloudflare Pages / Workers\\n入口与边缘逻辑", {B}];
 cr [label="Cloud Run\\n弹性后端", {B}];
 sb [label="Supabase Free\\nPostgres", {B}];
}}
graf [label="Grafana / VictoriaMetrics\\n基础指标", {G}];
b1 [label="盲区：真实用户体验\\n页面错误 · 加载耗时", shape=note, style="filled,dashed", {R}];
b2 [label="盲区：跨层请求上下文\\n边缘 → 后端 → 数据库", shape=note, style="filled,dashed", {R}];
b3 [label="盲区：数据库查询级可视性\\n无 Log Drain · 无 Metrics endpoint", shape=note, style="filled,dashed", {R}];
user -> cf -> cr -> sb;
cf -> graf [style=dotted]; cr -> graf [style=dotted];
user -> b1 [style=dashed, color="#D64545", arrowhead=none];
cr -> b2 [style=dashed, color="#D64545", arrowhead=none];
sb -> b3 [style=dashed, color="#D64545", arrowhead=none];
'''),
'triage-path':('TB',f'''
s [label="现象\\n用户登录失败", fillcolor="#FFFFFF"];
a [label="查边缘\\nWorkers 日志", {B}];
b [label="查后端\\nCloud Run 日志 / 指标", {B}];
c [label="查数据库\\nSupabase 日志\\nAPI / DB 日志留 1 天", {B}];
x [label="断点\\n三处时间线无共同 ID\\n无前端视角", style="rounded,filled,dashed", {R}];
s -> a -> b -> c -> x;
a -> x [style=dashed, color="#D64545"]; b -> x [style=dashed, color="#D64545"];
'''),
'evidence-chain':('TB',f'''
u [label="浏览器\\nRUM 会话", fillcolor="#FFFFFF", style="rounded,dashed"];
e [label="Cloudflare Workers\\n边缘逻辑", style="rounded,filled,dashed", {R}];
s [label="Cloud Run 服务\\nTrace · 日志 · trace_id", {B}];
span [label="应用侧 DB 调用 span\\n只见调用耗时", {B}];
d [label="Supabase Free\\n数据库内部", style="rounded,filled,dashed", {R}];
u -> e [label="请求"]; e -> s [label="W3C trace context"]; s -> span -> d [style=dashed];
'''),
'field-contract':('LR',f'''
f [label="关联字段\\nenv · service · route\\nrevision · release_tag · trace_id", {Y}];
l1 [label="RUM", {B}]; l2 [label="边缘日志", {B}]; l3 [label="后端 Trace / 日志", {B}]; l4 [label="DB 调用 span", {B}];
q [label="同一请求可跨层检索", {G}];
f -> l1; f -> l2; f -> l3; f -> l4; l1 -> q; l2 -> q; l3 -> q; l4 -> q;
'''),
}
# ---------- 02 boundaries: quota ledger ----------
D['02-free-zone-quota-ledger']={
'quota-map':('LR',f'''
w [label="免费版工作空间\\n免费专区（北京）\\n1 个空间 · 最多 5 人", fillcolor="#FFFFFF"];
m [label="指标\\n10,000 条时间线\\n最多 10 台主机", {B}];
l [label="日志类\\n每天 1,000 万条", {B}];
t [label="Trace（APM + Agent 共用）\\n每天 20,000 个", {B}];
r [label="RUM\\nPV 每天 5,000 个\\n会话重放每天 2,000 个", {B}];
s [label="可用性监测\\n每天 20 万次", {B}];
k [label="存储\\n7 天循环", {G}];
o [label="超额：不再上报", {R}];
w -> m; w -> l; w -> t; w -> r; w -> s;
m -> k; l -> k; t -> k; r -> k; s -> k; k -> o [style=dashed, color="#D64545"];
'''),
'feature-limits':('LR',f'''
c [label="免费版功能边界", fillcolor="#FFFFFF"];
a1 [label="仪表板 / 笔记 / 查看器\\n各 ≤ 10", {Y}];
a2 [label="监控器 ≤ 10\\n仅阈值检测", {Y}];
a3 [label="Pipeline\\n仅本地 Pipeline", {Y}];
n1 [label="不支持 Open API\\n读写工作空间数据", {R}];
n2 [label="不支持\\n数据转发 / 备份 · 外部数据源", {R}];
n3 [label="不支持\\n敏感数据脱敏 / 扫描", {R}];
n4 [label="不支持\\n快照 / 图表 / iframe 分享", {R}];
c -> a1; c -> a2; c -> a3; c -> n1; c -> n2; c -> n3; c -> n4;
'''),
'poc-scoping':('TB',f'''
inv [label="盘点现有环境\\n主机 · 时间线 · 仪表板 · 监控器 · PV", fillcolor="#FFFFFF"];
q [label="每项 ≤ 免费上限？", shape=diamond, style=filled, {Y}, margin="0.05,0.05"];
y [label="整体接入 POC", {G}];
n [label="瘦身：一条链路\\n白名单采集 · 选定面板", {B}];
u [label="采集侧统计发送量\\n占比留余量", {Y}];
inv -> q; q -> y [label="是"]; q -> n [label="否"]; y -> u; n -> u;
'''),
}
# ---------- 03 boundaries: privacy ----------
D['03-privacy-before-ingest']={
'mask-options':('TB',f'''
src [label="日志 · Trace 属性\\n前端会话", fillcolor="#FFFFFF"];
o1 [label="方案 A：平台侧脱敏\\n免费版不支持", style="rounded,filled,dashed", {R}];
o2 [label="方案 B：采集前过滤\\nVector · Collector\\nDataKit 本地 Pipeline", {G}];
o3 [label="方案 C：不采集\\n字段契约外一律丢弃", {B}];
dst [label="观测云工作空间", {B}];
src -> o1 [style=dashed, color="#D64545"]; src -> o2; src -> o3;
o2 -> dst; o3 -> dst;
'''),
'pre-ingest-layers':('LR',f'''
app [label="应用 / 主机", fillcolor="#FFFFFF"];
v [label="Vector\\nremap 改写 · 丢字段", {G}];
oc [label="OTel Collector\\n属性删除 / 哈希", {G}];
dk [label="DataKit\\n本地 Pipeline", {G}];
rum [label="浏览器 RUM SDK\\n隐私遮罩", {B}];
g [label="观测云", {B}];
app -> v -> dk; app -> oc -> dk; dk -> g; rum -> g;
'''),
'field-allowlist':('LR',f'''
in [label="原始字段", fillcolor="#FFFFFF"];
ok [label="保留\\nenv · service · route · status\\nrevision · trace_id", {G}];
h [label="哈希或聚合后保留\\n租户 ID · 用户 ID", {Y}];
no [label="不采集\\n邮箱 · Cookie · IP · Token · Prompt 原文", {R}];
in -> ok; in -> h; in -> no [style=dashed, color="#D64545"];
'''),
}
# ---------- 04 boundaries: terraform provider ----------
D['04-terraform-provider-qa']={
'endpoint-check':('TB',f'''
s [label="工作空间", fillcolor="#FFFFFF"];
q1 [label="版本支持 Open API？", shape=diamond, style=filled, {Y}, margin="0.05,0.05"];
q2 [label="站点在 Open API\\nendpoint 列表中？", shape=diamond, style=filled, {Y}, margin="0.05,0.05"];
k [label="DF-API-KEY\\n归属工作空间即作用域", {B}];
tf [label="Terraform Provider\\nplan / import / apply", {G}];
off [label="HCL 照常生成并审查\\napply 被阻断", {R}];
s -> q1; q1 -> q2 [label="是"]; q1 -> off [label="否（免费版）"]; q2 -> k [label="是"]; q2 -> off [label="否"]; k -> tf;
'''),
'gitops-hcl':('TB',f'''
g [label="GitOps\\n监控意图 + 非敏感模板", {B}];
r [label="renderer\\nPython + Jinja2", {B}];
h [label="显式 HCL\\n可读 · 可审查", fillcolor="#F5F7FA"];
pr [label="PR 审查", {Y}];
dec [label="空间有\\nAPI 权限？", shape=diamond, style=filled, {Y}, margin="0.05,0.05"];
yes [label="terraform plan\\n→ import 已有资源\\n→ apply", {G}];
no [label="apply 被阻断\\nHCL 保留在 PR", {R}];
g -> r -> h -> pr -> dec; dec -> yes [label="有"]; dec -> no [label="无"];
'''),
'resource-map':('LR',f'''
p [label="GuanceCloud/guance\\nProvider", fillcolor="#FFFFFF"];
d [label="guance_dashboard", {B}];
m [label="guance_monitor", {B}];
mj [label="guance_monitor_json", {B}];
i1 [label="import：文档已写明", {G}];
i2 [label="import：文档未写明", {Y}];
p -> d; p -> m; p -> mj; mj -> i1; d -> i2 [style=dashed]; m -> i2 [style=dashed];
'''),
}
# ---------- 05 how: collector gitops ----------
D['05-collector-gitops-handson']={
'automation-path':('TB',f'''
ai [label="AI 助手\\n起草声明与配置", shape=ellipse, fillcolor="#FFFFFF"];
g [label="GitOps\\n非敏感参数 · 采集意图 · 开关", {B}];
pr [label="PR 审查", {Y}];
pb [label="Playbook\\n部署 DataKit 与采集配置", {B}];
v [label="Vault\\n运行时注入写入 Token", {G}];
ok [label="验证\\n首条数据 · 字段对照", fillcolor="#F5F7FA"];
ai -> g -> pr -> pb -> ok; v -> pb [style=dashed];
'''),
'ingest-ports':('LR',f'''
oc [label="OTel Collector", {G}];
ve [label="Vector\\n指标 sink", {G}];
vl [label="Vector\\n日志 sink", {G}];
subgraph cluster_dk {{ label="DataKit"; style=rounded; color="#4C7BD9"; fontsize=16;
 i1 [label="opentelemetry\\ngRPC · HTTP（仅 protobuf）", {B}];
 i2 [label="prom_remote_write\\n/prom_remote_write", {B}];
 i3 [label="logstreaming\\n/v1/write/logstreaming", {B}];
}}
g [label="观测云", {B}];
oc -> i1; ve -> i2; vl -> i3; i1 -> g; i2 -> g; i3 -> g;
'''),
'credential-split':('LR',f'''
v [label="Vault", {G}];
k1 [label="写入 Token", {Y}]; k2 [label="查询 Key", {Y}]; k3 [label="管理 API Key", {Y}];
c1 [label="Playbook 部署时\\n注入 DataKit", {B}];
c2 [label="对账脚本\\n只读", {B}];
c3 [label="IaC 流水线\\n仅在 plan / apply 时", {B}];
v -> k1 -> c1; v -> k2 -> c2; v -> k3 -> c3;
'''),
}
# ---------- 06 how: timeseries budget ----------
D['06-timeseries-budget']={
'cardinality':('TB',f'''
m [label="一个指标名", fillcolor="#FFFFFF"];
l [label="× 标签取值组合\\nhost · pid · thread …", {Y}];
t [label="= 时间线条数", {B}];
cap [label="空间上限\\n10,000 条时间线", {R}];
m -> l -> t -> cap;
'''),
'three-gates':('TB',f'''
ex [label="exporter\\nnode · process · blackbox", fillcolor="#FFFFFF"];
g1 [label="闸 1：发送端\\nwrite_relabel keep\\n或 Vector 过滤", {G}];
g2 [label="闸 2：DataKit 指标过滤\\nmetric_name_filter\\nmeasurement_name_filter", {B}];
g3 [label="闸 3：标签裁剪\\ntags_only / tags_ignore", {B}];
g [label="观测云", {B}];
ex -> g1 -> g2 -> g3 -> g;
'''),
'red-no-dup':('TB',f'''
app [label="应用 OTLP", fillcolor="#FFFFFF"];
oc [label="OTel Collector", {G}];
sm [label="spanmetrics\\n留在自建", {G}];
dk [label="DataKit opentelemetry", {B}];
rm [label="链路指标\\ntrace_hits · trace_latency\\ntrace_errors · trace_apdex", {B}];
app -> oc; oc -> sm; oc -> dk; dk -> rm;
'''),
}
# ---------- 07 verify: grafana import ----------
D['08-grafana-dashboard-import']={
'migration-funnel':('TB',f'''
inv [label="Grafana JSON 盘点\\ndatasource · panel · 变量 · 查询\\n单位 · 聚合窗口 · 阈值", fillcolor="#F5F7FA"];
pick [label="首批 3 个面板\\n资源健康 · API 流量与错误 · k6 压测延迟", {B}];
ai [label="AI 映射清单 + 候选声明", fillcolor="#FFFFFF"];
hu [label="人工核对口径", {Y}];
o1 [label="可迁移", {G}]; o2 [label="需重写", {Y}]; o3 [label="暂保留在 Grafana", {R}];
inv -> pick -> ai -> hu; hu -> o1; hu -> o2; hu -> o3;
'''),
'json-to-plan':('TB',f'''
gj [label="Grafana 导出 JSON", fillcolor="#FFFFFF"];
cv [label="grafanaCovertToGuance\\n离线转换", {B}];
ai [label="AI 映射\\n生成面板声明", {B}];
g [label="GitOps 声明", {B}];
pr [label="PR 审查", {Y}];
r [label="iac_modules renderer\\nguance_dashboard HCL", {B}];
p [label="terraform plan\\n人审 plan", {Y}];
q [label="空间支持\\nOpen API？", shape=diamond, style=filled, {Y}, margin="0.05,0.05"];
ap [label="apply", {G}];
blk [label="apply 被阻断", style="rounded,filled,dashed", {R}];
gj -> cv -> ai; gj -> ai; ai -> g -> pr -> r -> p -> q; q -> ap [label="是"]; q -> blk [label="否"];
'''),
'path-compare':('LR',f'''
s [label="Grafana 面板", fillcolor="#FFFFFF"];
a [label="A 转换脚本\\n→ 观测云 JSON → 声明", {B}];
b [label="B AI 直出声明\\n重写查询", {B}];
c [label="C 暂保留\\n跨层总览 · 自监控", {G}];
h [label="renderer → HCL → plan", {Y}];
s -> a -> h; s -> b -> h; s -> c;
'''),
}
# ---------- 08 verify: query semantics ----------
D['09-query-semantics-qa']={
'query-traps':('TB',f'''
src [label="原查询\\nPromQL（VictoriaMetrics）\\nLogsQL（VictoriaLogs）", {G}];
t1 [label="指标名 / 标签\\n转换后是否一致", {Y}];
t2 [label="rate / increase\\n窗口与 step", {Y}];
t3 [label="分位数\\n计算方式", {Y}];
t4 [label="单位换算", {Y}];
t5 [label="缺数\\n补零还是断线", {Y}];
t6 [label="变量与时间范围", {Y}];
dst [label="观测云图表\\nPromQL 模式 / DQL", {B}];
chk [label="同一时间窗并排比对", fillcolor="#F5F7FA"];
src -> t1 -> t2 -> t3 -> t4 -> t5 -> t6 -> dst -> chk;
'''),
'metric-naming':('TB',f'''
raw [label="Remote Write 指标\\ngo_memstats_heap_objects", fillcolor="#FFFFFF"];
d0 [label="默认\\n指标集 go\\n字段 memstats_heap_objects", {Y}];
d1 [label="keep_exist_metric_name = true\\n字段 go_memstats_heap_objects", {G}];
raw -> d0 [label="首个下划线切分"]; raw -> d1 [label="保留原名"];
'''),
'step-priority':('TB',f'''
a [label="查询内窗口\\n如 [5m]", {B}];
b [label="interval 参数", {B}];
c [label="timerange", {B}];
d [label="默认 5m", {Y}];
a -> b [label="未指定"]; b -> c [label="未指定"]; c -> d [label="均无"];
'''),
'filter-conversion':('LR',f'''
f [label="PromQL 模式筛选条件", fillcolor="#FFFFFF"];
y1 [label="多个 AND\\n→ 逗号连接", {G}];
y2 [label="同 label 多值 OR\\n→ 正则 =~", {G}];
y3 [label="= != =~ !~\\n直接转换", {G}];
n1 [label="不同 label 之间 OR", {R}];
n2 [label="数值比较", {R}];
n3 [label="函数类筛选", {R}];
f -> y1; f -> y2; f -> y3; f -> n1 [style=dashed, color="#D64545"]; f -> n2 [style=dashed, color="#D64545"]; f -> n3 [style=dashed, color="#D64545"];
'''),
}
# ---------- 09 verify: alerts ledger ----------
D['10-alert-monitor-ledger']={
'alert-triage':('TB',f'''
r [label="自建告警规则", fillcolor="#FFFFFF"];
q [label="规则类型", shape=diamond, style=filled, {Y}, margin="0.05,0.05"];
a [label="资源阈值\\nCPU · 内存 · 磁盘", {G}];
b [label="失联 / 无数据", {B}];
c [label="站点与证书", {B}];
d [label="采集管道自监控", {R}];
a2 [label="阈值检测监控器", {G}];
b2 [label="阈值检测 + 数据断档事件", {B}];
c2 [label="可用性监测\\nHTTP / SSL 拨测", {B}];
d2 [label="留在 Grafana", {R}];
r -> q; q -> a; q -> b; q -> c; q -> d; a -> a2; b -> b2; c -> c2; d -> d2;
'''),
'threshold-pipeline':('TB',f'''
f [label="检测频率", {B}];
w [label="检测区间\\n≥ 检测频率", {B}];
m [label="检测指标\\nDQL / PromQL", {B}];
t [label="触发条件\\n致命 · 严重 · 重要 · 警告", {Y}];
n [label="恢复条件\\n连续 N 次正常", {G}];
gap [label="数据断档策略\\n优先于触发条件", {R}];
f -> w -> m -> t -> n; m -> gap [style=dashed];
'''),
'pipeline-self-monitor':('LR',f'''
v [label="Vector", {G}];
s1 [label="自建存储", {G}];
s2 [label="DataKit → 观测云", {B}];
gm [label="Grafana 告警\\n缓冲积压 · 组件错误", {Y}];
v -> s1; v -> s2 [style=dashed]; v -> gm [style=dotted];
'''),
}
# ---------- 10 rollback/evolve ----------
D['12-dual-write-rollback']={
'side-by-side':('TB',f'''
src [label="真实请求 / k6 压测", fillcolor="#FFFFFF"];
col [label="现有采集", fillcolor="#F5F7FA"];
subgraph cluster_old {{ label="原链路"; style=rounded; color="#3E8E5A"; fontsize=16;
 vm [label="VictoriaMetrics / VictoriaLogs\\n原始存储", {G}];
 gf [label="Grafana", {G}];
 vm -> gf;
}}
subgraph cluster_new {{ label="新增链路"; style="rounded,dashed"; color="#4C7BD9"; fontsize=16;
 dk [label="第二写入\\n失败不阻断原采集", {B}];
 gc [label="观测云面板", {B}];
 dk -> gc;
}}
cmp [label="同时间窗对照", {Y}];
src -> col; col -> vm; col -> dk [style=dashed]; gf -> cmp; gc -> cmp;
'''),
'switch-states':('LR',f'''
sw [label="采集开关\\n默认关", shape=diamond, style=filled, {Y}, margin="0.05,0.05"];
off [label="单 sink\\n仅自建存储", {G}];
on [label="双 sink\\n自建存储 + DataKit", {B}];
sw -> off [label="关"]; sw -> on [label="开"];
'''),
'rollback-runbook':('TB',f'''
t [label="回退触发\\n偏差超门槛 · 额度告急 · 敏感字段命中", {R}];
s1 [label="排障入口切回 Grafana", {G}];
s2 [label="开关置关 → Playbook 重跑", {B}];
s3 [label="停用 DataKit · 移除 RUM SDK", {B}];
s4 [label="Git 回退监控器与拨测声明\\nplan / apply", {B}];
s5 [label="轮换写入 Token / 管理 Key", {Y}];
s6 [label="校验 Grafana 面板与告警", {G}];
t -> s1 -> s2 -> s3 -> s4 -> s5 -> s6;
'''),
'data-lifecycle':('LR',f'''
w [label="观测云免费空间", {B}];
r [label="7 天循环删除", {Y}];
x [label="空间不可解散\\nOwner 不可移交", {R}];
s [label="原始存储\\n数据回退依据", {G}];
w -> r; w -> x [style=dashed]; s -> w [style=invis];
'''),
}

# ---------- 07 how: logs dual write ----------
D['07-log-streaming-handson']={
'logs-dual-sink':('TB',f'''
src [label="主机日志\\nsystemd · 应用", fillcolor="#FFFFFF"];
v [label="Vector", {G}];
vl [label="VictoriaLogs\\nLogsQL 查询", {G}];
dk [label="DataKit logstreaming\\n/v1/write/logstreaming", {B}];
g [label="观测云日志查看器\\nDQL 查询", {B}];
src -> v; v -> vl [label="原 sink"]; v -> dk [style=dashed, label="第二 sink"]; dk -> g;
'''),
'url-params':('LR',f'''
u [label="logstreaming URL 参数", fillcolor="#FFFFFF"];
p1 [label="source\\n指标集名 · 默认 default", {B}];
p2 [label="service\\nservice 标签 · 默认同 source", {B}];
p3 [label="pipeline\\n指定本地 Pipeline 脚本", {Y}];
p4 [label="tags\\n自定义标签 · 逗号分隔", {B}];
u -> p1; u -> p2; u -> p3; u -> p4;
'''),
'json-as-fields':('TB',f'''
l [label="一行 JSON 日志", fillcolor="#FFFFFF"];
q [label="json_as_fields", shape=diamond, style=filled, {Y}, margin="0.05,0.05"];
a [label="false（默认）\\n整行进入 message", {R}];
b [label="true\\nJSON 根对象转为字段", {G}];
l -> q; q -> a; q -> b;
'''),
'trace-log-join':('LR',f'''
lg [label="日志\\n含 trace_id 字段", {B}];
tr [label="APM 链路\\ntrace_id", {B}];
j [label="按 trace_id 互相跳转", {G}];
n [label="日志无 trace_id\\n无法关联", style="rounded,filled,dashed", {R}];
lg -> j; tr -> j; n -> j [style=dashed, color="#D64545", arrowhead=none];
'''),
}
# ---------- 11 verify: synthetic vs blackbox ----------
D['11-synthetic-vs-blackbox']={
'probe-split':('TB',f'''
t [label="站点 · 接口 · 证书", fillcolor="#FFFFFF"];
bb [label="自建 Blackbox Exporter\\n自定探测间隔 · 进 Grafana", {G}];
st [label="观测云可用性监测\\n平台节点 · 外部视角", {B}];
a [label="Grafana 告警", {G}];
b [label="拨测结果 · 告警", {B}];
t -> bb -> a; t -> st -> b;
'''),
'frequency-tiers':('TB',f'''
h [label="HTTP 拨测频率", fillcolor="#FFFFFF"];
c [label="商业版及以上\\n1 分钟 · 5 分钟 · 15 分钟", {Y}];
f [label="所有版本\\n30 分钟 · 1 / 6 / 12 / 24 小时\\n自定义 crontab", {G}];
n1 [label="中国地区节点", {G}];
n2 [label="海外地区节点\\n商业版及以上", {Y}];
h -> c; h -> f; f -> n1; c -> n2;
'''),
'check-modes':('TB',f'''
r [label="HTTP 响应", fillcolor="#FFFFFF"];
m1 [label="默认模式\\n状态码 · 响应时间 · 请求头\\n所有（AND）/ 任意（OR）", {B}];
m2 [label="脚本模式\\nPipeline 解析响应体\\n自定义 is_failed", {G}];
o [label="拨测成功 / 失败", {Y}];
r -> m1 -> o; r -> m2 -> o;
'''),
'probe-privacy':('LR',f'''
req [label="拨测请求\\nHeader · Cookie · 认证", {Y}];
opt [label="不保存响应内容", {G}];
res [label="拨测结果\\n不含响应体", {B}];
req -> opt -> res;
'''),
}

import os; root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for art,ds in D.items():
    d=f'{root}/{art}/diagrams/src'; os.makedirs(d,exist_ok=True)
    for n,(rk,body) in ds.items():
        open(f'{d}/{n}.dot','w').write(H%rk+body+'}\n')
    print(art,len(ds))
