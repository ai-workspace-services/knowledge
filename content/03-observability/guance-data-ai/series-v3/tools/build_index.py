import glob,os,re,sys
sys.path.insert(0,os.path.dirname(__file__)); import count
from PIL import Image
M={
'01':('为什么','故障复盘型','Cloudflare Pages/Workers + Cloud Run + Supabase Free 低成本栈，自建 Grafana/VictoriaMetrics 看基础指标','一次登录失败要翻三处后台，无共同请求 ID、无前端视角，Supabase Free 日志只留 1 天','只为一条链路建证据链：RUM + Trace + W3C trace context + 统一字段，未关联环节标盲区'),
'02':('边界','成本账本型','准备用观测云免费版（免费专区·北京）做单链路 POC','额度与功能边界多维，任一项超额即不再上报','按版本区分页逐项记账，超限则瘦身为一条链路 + 白名单'),
'03':('边界','对比选型型','日志、Trace 属性、前端会话将写入 SaaS 工作空间','免费版不支持敏感数据脱敏/扫描，Span 属性默认最多提取 500 键','对比平台脱敏/采集前过滤/不采集，选采集前过滤 + 字段白名单'),
'04':('边界','问答拆解型','现有 IaC：GitOps → renderer → HCL → plan/apply，想把面板与监控器代码化','远端资源依赖 Open API，免费版不支持且免费专区不在 endpoint 列表','按空间分流：有 API 权限走 plan/import/apply，免费空间只做离线 HCL'),
'05':('怎么做','动手实操型','Vector + OTel Collector 采集栈由 Playbook 部署、Vault 注入凭据','新增 SaaS 写入通道易泄漏写入 Token、可能拖垮原采集','声明进 Git（开关默认关）→ Playbook 部署 DataKit 三个接入口 → 凭据三分'),
'06':('怎么做','误区纠偏型','Vector 以 Remote Write 推主机指标，新增 sink 写往免费空间','时间线上限 10,000，高基数标签放大时间线，超额不再上报','三道闸（发送端 keep / DataKit 指标过滤 / 标签裁剪）+ 链路指标不双写'),
'07':('怎么做','动手实操型','Vector 采集 systemd/应用日志经 HTTP 写入 VictoriaLogs（LogsQL）','日志进观测云若是整行文本且无 trace_id，则无法按字段检索、无法与 Trace 关联','Vector 第二 sink → logstreaming（source/service/pipeline/tags）+ json_as_fields + 日志带 trace_id'),
'08':('验证','对比选型型','指标与日志已并行写入，面板仍在 Grafana（VictoriaMetrics + VictoriaLogs）','Grafana JSON 不等于观测云 JSON，免费版仪表板 ≤10 且无 Open API，面板无法经 Terraform 写入免费空间','对比转换脚本 / AI 直出声明 / 暂保留；统一走 声明 → renderer → HCL → plan，apply 待授权空间实测'),
'09':('验证','问答拆解型','面板查询为 PromQL（VictoriaMetrics）与 LogsQL（VictoriaLogs）','语法能转但语义不一致：指标名切分、step、筛选、P99 算法','口径清单逐项核对 + 同一时间窗并排比对'),
'10':('验证','成本账本型','自建告警在 Grafana：资源、失联、站点证书、管道自监控','免费版监控器 ≤10 且仅阈值检测，配置不当会被自动暂停','按科目分流：阈值/数据断档进监控器，证书站点走拨测，管道自监控留 Grafana'),
'11':('验证','误区纠偏型','站点与证书类告警已划给可用性监测，自建侧有 Blackbox Exporter','免费版 HTTP 拨测 1/5/15 分钟档与海外节点仅限商业版，频率档位与节点受限，不能当作 Blackbox 的原样替身','分工：Blackbox 保留自建探测，拨测承担外部视角、证书剩余天数与脚本模式业务断言'),
'12':('回退/演进','动手实操型','自建栈持续运行，观测云为并行新链路','免费空间 7 天循环、不可解散、可被通知终止，新链路失败时回不去','开关 + 双 sink 双写 + 并排对照 + 回退/退出顺序'),
}
rows=[];tot=[]
for d in sorted(glob.glob(os.path.join(os.path.dirname(__file__),'..','[0-9][0-9]-*'))):
    k=os.path.basename(d)[:2]; slug=os.path.basename(d)
    w=open(f'{d}/wechat.md').read(); title=w.splitlines()[0].lstrip('# ').strip()
    wc=count.counts(f'{d}/wechat.md')[0]; xc=count.counts(f'{d}/xhs.md')[0]
    xraw=len(re.sub(r'\s','',open(f'{d}/xhs.md').read()))
    dots=sorted(os.path.basename(p)[:-4] for p in glob.glob(f'{d}/diagrams/src/*.dot'))
    for n in dots:
        for v in ('wechat','xhs'):
            g=f'{d}/diagrams/gif/{n}-{v}.gif'; im=Image.open(g); assert im.n_frames>1 and im.size[0]==1080, g
        assert f'diagrams/gif/{n}-wechat.gif' in w, (slug,n)
    ok='✅' if wc<=1500 and 600<=xc<=800 and 3<=len(dots)<=5 else '❌'
    st,tp,bg,pp,so=M[k]
    rows.append(f'| {k} | {st} | {tp} | [{title}]({slug}/wechat.md) | {bg} | {pp} | {so} | {wc} | {xc}（含标记 {xraw}） | {len(dots)}：{"、".join(dots)} | {ok} |')
    tot.append(tp)
for i in range(len(tot)): assert tot[i]!=tot[i-1]
out=['# 观测云可观测性系列（12 篇）索引','',
'阅读顺序：为什么（01）→ 边界（02–04）→ 怎么做（05–07）→ 验证（08–11）→ 回退/演进（12）→ 回到 01，形成闭环。相邻两篇模板均不同（首尾 12→01 亦不同）。排期草案见 quarterly-plan.md。','',
'计数口径（tools/count.py）：公众号 = 全文可见字符（含标题、表格、参考行、上一篇/下一篇行；去掉图片行、链接 URL、表格分隔行与 Markdown 符号 # * > ` |；不含空白），上限 1500。XHS = 同口径非空白字符，要求 600–800；括号内为连 Markdown 符号一起计的原始非空白字符数，同样落在 600–800 内。','',
'| # | 阶段 | 模板 | 标题 | 背景 | 痛点 | 方案 | 公众号字数 | XHS 字数 | 图（每图有 -wechat.gif 1080 宽 / -xhs.gif 1080×1440） | 达标 |',
'| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']+rows+['',
'每篇目录：wechat.md、xhs.md、sources.md（完整来源 URL，不计入字数）、diagrams/src/*.dot、diagrams/gif/*.gif。重新出图：`python3 tools/dots.py && for a in [0-9]*; do python3 tools/render.py $a; done`；重新生成本索引：`python3 tools/build_index.py`。']
open(os.path.join(os.path.dirname(__file__),'..','index.md'),'w').write('\n'.join(out)+'\n')
print('\n'.join(rows))
