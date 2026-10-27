# -*- coding: utf-8 -*-
import os
import re
import subprocess
from generate_svgs import (
    get_a1_svg1, get_a1_svg2, get_a1_svg3, get_a1_svg4,
    get_a2_svg1, get_a2_svg2, get_a2_svg3, get_a2_svg4,
    get_a3_svg1, get_a3_svg2, get_a3_svg3, get_a3_svg4,
    get_a4_svg1, get_a4_svg2, get_a4_svg3, get_a4_svg4
)

BASE_DIR = "/Users/shenlan/workspaces/ai-workspace-service/knowledge-v5-runtime-blockers/content/03-observability/guance-data-ai"
PDF_DIR = os.path.join(BASE_DIR, "pdf_exports")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Import CSS from previous step
from build_all_deliverables import PRINT_CSS, count_non_space

# 1. PLAN HTML
def generate_plan_html():
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>独立开发观察者计划：AI × 可观测 SaaS 首季策划方案</title>
<style>
{PRINT_CSS}
</style>
</head>
<body>

<div class="header-banner">
    <div class="series-tag">INDIE HACKER OBSERVABILITY OBSERVATION PROGRAM · SEASON 1 MASTER PLAN</div>
    <h1>独立开发观察者计划：AI × 可观测 SaaS 首季策划方案</h1>
    <div class="sub-title">一人运营个人 SaaS 的可观测服务选型、代码化实践与 90 天演化路线（GitOps / IaC / Playbook / Vault 主线）</div>
</div>

<div class="meta-grid">
    <div class="meta-item"><strong>执行周期</strong>2026 Q4 (首合同 12 周)</div>
    <div class="meta-item"><strong>交付形态</strong>12 篇核心公众号 + 12 组小红书</div>
    <div class="meta-item"><strong>核心主线</strong>GitOps / IaC / Playbook / Vault</div>
    <div class="meta-item"><strong>技术栈底座</strong>Cloudflare + Cloud Run + Supabase</div>
</div>

<h2>一、合作范围与选题立场</h2>
<p>本次首个季度合同按每周一个独立技术主题，规划 <strong>12 篇核心交付</strong>；每个主题以微信公众号深度技术长文为主（InfoQ 客观实战风格，严格 ≤1500 字，3–5 段落，配套架构视角决策表），并同步配套一组小红书种草图文（严格 600–800 字，口语化、P1–Pn 分页排版）。另设 <strong>R1–R3 三篇可替换候选</strong>，用于在缺真实证据、外部权益不满足或双方评估需要微调时无缝替换相近核心篇，不占用额外交付承诺。</p>
<p>整个季度内容的核心命题是：<strong>AI 如何帮助个人 SaaS 被开发、被理解和持续运行</strong>。前两篇聚焦开放接入、额度边界与自建 Grafana 面板平迁对账；随后依次深入终端用户真实体验、跨多云请求链路、AI Agent 执行链与成本归因；再延伸至 AI 协助发布验证、故障根因调查与独立可用性探测；最终以 90 天真实 TCO 账本、投入产出比与无损退出机制收尾。每篇坚持<strong>“一个知识点、一个真实 Case、一项可复验代码化证据”</strong>，观测云的具体能力仅在解决特定工程断点时自然引入，严禁软文堆砌。</p>
<p>读者主角是独立开发者与精简技术团队。自建 Grafana / VictoriaMetrics / OTel 底座与商业 SaaS 可以且应当同时存在。决定 SaaS 采购与留存价值的唯一准则，是它<strong>减少了多少日常运维与排障负担、付出了多少显性与隐性费用，以及在发生技术路线转移时能否低成本退出</strong>。</p>

<h2>二、整季叙事演化路线</h2>
<div class="callout">
<strong>叙事主轴</strong>：个人 SaaS 已经上线，但一个人需要独自承担开发、SRE、客服与运营<br>
→ <strong>阶段一：接入与平迁（#01–#02）</strong>：挑选可观测 SaaS 并接入，AI 辅助将已有自建面板平迁对账并保留回退；<br>
→ <strong>阶段二：端到端穿透（#03–#05）</strong>：看见终端真实用户性能瓶颈，串联跨多云分布式 Trace，建立防打扰的可行动告警；<br>
→ <strong>阶段三：Agent 观测与成本（#06–#08）</strong>：全链路观测 Coding Agent 工具链执行，对账 Token 与业务交付，捕获死循环重试；<br>
→ <strong>阶段四：发布与排障（#09–#11）</strong>：利用观测数据做发布前后比对，AI 辅助夜间异常调查，建立独立外部可用性探测；<br>
→ <strong>阶段五：TCO 复盘（#12）</strong>：汇总 90 天完整用量、真实账单与退出演练，科学决定是否继续采购 SaaS。
</div>

<h2>三、核心实践铁律：全代码化交付主线</h2>
<p>本季所有文章的技术落地，<strong>彻底杜绝在 Web 控制台做任何人肉点按与截屏演示</strong>。全部围绕现代化平台工程与代码化实践展开：</p>
<table class="data-table">
    <thead>
        <tr>
            <th style="width: 20%;">交付层级</th>
            <th style="width: 35%;">工程职责与实现准则</th>
            <th style="width: 45%;">安全与代码化红线</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>GitOps</strong></td>
            <td>只存放非敏感环境参数、服务元数据与监控意图声明（YAML）。</td>
            <td>严禁包含任何环境凭据、工作空间 Token、API Key 或内网地址。</td>
        </tr>
        <tr>
            <td><strong>IaC-modules</strong></td>
            <td>本地 Renderer 将声明式意图编译为显式 HCL，执行 <code>terraform plan</code> 离线验证。</td>
            <td>普通免费空间不支持 OpenAPI 时仅输出离线 HCL，严禁使用私有 API 逆向绕过。</td>
        </tr>
        <tr>
            <td><strong>Playbook</strong></td>
            <td>Ansible 自动化编排 DataKit 守护进程、OTel Collector 路由与双写布尔开关。</td>
            <td>配置具备幂等性与熔断机制，确保数据流故障时不阻塞核心业务请求。</td>
        </tr>
        <tr>
            <td><strong>Vault 运行时注入</strong></td>
            <td>HashiCorp Vault 动态注入写入 Token、只读查询 Key 与管理凭据。</td>
            <td>管理 Key、查询 Key 与写入 Token 物理隔离，绝不进入 Git 仓库或 CI/CD 构建日志。</td>
        </tr>
        <tr>
            <td><strong>AI 角色边界</strong></td>
            <td>AI 负责起草配置声明、解析 AST 语法树、生成 PR 说明与对账分析脚本。</td>
            <td>人类工程师最终审核 PR、核对 Terraform plan 并执行凭据签发。</td>
        </tr>
    </tbody>
</table>

<div class="page-break"></div>

<h2>四、首合同核心 12 篇选题矩阵明细</h2>
<table class="data-table">
    <thead>
        <tr>
            <th style="width: 5%;">周</th>
            <th style="width: 20%;">公众号候选标题 / 模板</th>
            <th style="width: 15%;">小红书封面标题</th>
            <th style="width: 25%;">唯一知识点 / 真实 SaaS Case</th>
            <th style="width: 20%;">代码化切入及 AI 角色</th>
            <th style="width: 15%;">验收素材与依赖</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>01</td>
            <td><strong>我的个人 SaaS 已经够便宜了，还能用什么补上监控？</strong><br><span class="badge-self">对比选型型</span></td>
            <td>薅北京专区的羊毛，先看清条件！</td>
            <td><strong>免费额度与服务选型</strong>：Cloudflare Pages/Workers + Cloud Run + Supabase 的 UAT 接入观测。</td>
            <td>Playbook 分发 DataKit 配置；Vault 注入 Token；AI 辅助指标白名单过滤。</td>
            <td>7 天用量比例、OTel 指标精简流、离线 HCL 声明。</td>
        </tr>
        <tr>
            <td>02</td>
            <td><strong>AI 帮我搬 Grafana 面板：先让数字对上，再决定切换</strong><br><span class="badge-free">误区纠偏型</span></td>
            <td>监控面板搬家，最怕搬错数字！</td>
            <td><strong>面板语义对账</strong>：自建 Grafana 资源、流量和压测面板平迁与双写。</td>
            <td>AI 解析 Grafana AST；Playbook 下发双写开关；Python 对账脚本。</td>
            <td>P95 误差 &lt;2%、k6 压测曲线、15 分钟回退演练。</td>
        </tr>
        <tr>
            <td>03</td>
            <td><strong>AI 生成的页面上线后变卡，我先看用户体验而不是 CPU</strong><br><span class="badge-pro">故障复盘型</span></td>
            <td>用户说卡，AI 写的页面哪里慢？</td>
            <td><strong>真实用户体验</strong>：UAT 页面卡顿的浏览器端根因分析与 Core Web Vitals。</td>
            <td>前端 CI 注入 RUM SDK；DOM 属性隐私掩码；AI 归纳主线程长任务。</td>
            <td>脱敏会话、INP 交互延迟、280ms Long Task 修复前后对比。</td>
        </tr>
        <tr>
            <td>04</td>
            <td><strong>一个登录请求经过几朵云？用 Trace 把它接起来</strong><br><span class="badge-self">动手实操型</span></td>
            <td>一个登录请求到底去了哪里？</td>
            <td><strong>分布式上下文传播</strong>：Cloudflare → Worker → Cloud Run → Supabase 跨云 Trace。</td>
            <td>W3C TraceContext 注入；Terraform 声明容器环境变量；OTel 收集器。</td>
            <td>同一 TraceID 跨云瀑布图、Supabase 鉴权延迟分析。</td>
        </tr>
        <tr>
            <td>05</td>
            <td><strong>AI 帮我生成的告警，怎样才能真的值得打断我？</strong><br><span class="badge-free">成本账本型</span></td>
            <td>告警太多，AI 能帮我筛吗？</td>
            <td><strong>可行动告警与降噪</strong>：单人运维下的 API 错误率与静默规则。</td>
            <td>AI 起草监控器规则；IaC 声明阈值；Webhook 接入移动通知。</td>
            <td>一次故障演练告警到达时间、误报率与恢复通知。</td>
        </tr>
        <tr>
            <td>06</td>
            <td><strong>Codex 的一次任务，到底调用了多少次工具？</strong><br><span class="badge-pro">问答拆解型</span></td>
            <td>AI 说完成了，我想看它做了什么</td>
            <td><strong>Agent 执行链观测</strong>：编码任务的 Session → Trace → Tool Span 追踪。</td>
            <td>Agent Monitoring 探针接入；AI 作为被观测对象；捕获 Tool 步骤。</td>
            <td>脱敏 Agent 会话流水、Tool 执行耗时瀑布图。</td>
        </tr>
        <tr>
            <td>07</td>
            <td><strong>Token 花掉以后，怎样知道它有没有换来交付？</strong><br><span class="badge-self">成本账本型</span></td>
            <td>Token 用得多，不代表真的干成了</td>
            <td><strong>AI 成本归因</strong>：将 Agent 任务关联到 Git Commit、测试通过率与真实交付。</td>
            <td>AgentMeter 统计消费；GitOps 关联 commit 标记；成本分摊计算。</td>
            <td>Token 消耗曲线、每次任务产出比、订阅折算模型。</td>
        </tr>
        <tr>
            <td>08</td>
            <td><strong>Agent 没有报错，为什么我的任务一直跑不完？</strong><br><span class="badge-free">故障复盘型</span></td>
            <td>AI 没崩，但一直在原地打转</td>
            <td><strong>死循环与异常重试</strong>：工具调用反复执行导致的任务卡死排查。</td>
            <td>Agent Trace 捕获循环 Span；AI 辅助生成终止假设与断路策略。</td>
            <td>循环调用时间线、重复 Tool 步骤证据、熔断退出机制。</td>
        </tr>
        <tr>
            <td>09</td>
            <td><strong>AI 改完代码就发布？我用观测数据检查这一版</strong><br><span class="badge-pro">对比选型型</span></td>
            <td>AI 写完了，怎么确认没变差？</td>
            <td><strong>发布前后金丝雀对比</strong>：Cloud Run / Worker 版本迭代的质量基线。</td>
            <td>GitOps 关联 release tag；同一时间窗比对错误率与 P95 延迟。</td>
            <td>GitHub Actions 运行记录、版本指标比对看板、回滚决策依据。</td>
        </tr>
        <tr>
            <td>10</td>
            <td><strong>凌晨收到告警，让 AI 先帮我整理排障线索</strong><br><span class="badge-self">动手实操型</span></td>
            <td>没有值班团队，AI 先查什么？</td>
            <td><strong>证据驱动的 AI 调查</strong>：只读 MCP 关联指标、日志与 Trace 定位故障。</td>
            <td>经授权只读 MCP Server；严格禁止写操作；AI 生成假设与证据链。</td>
            <td>同一故障上下文、AI 引用证据列表、人工校验复核耗时。</td>
        </tr>
        <tr>
            <td>11</td>
            <td><strong>自建监控自己挂了，谁来提醒我？</strong><br><span class="badge-free">误区纠偏型</span></td>
            <td>监控坏了，谁来监控监控？</td>
            <td><strong>独立故障域与外部探测</strong>：自建观测入口中断时的异地外部拨测。</td>
            <td>外部 HTTP/SSL 拨测；独立通知网络；发现链路不依赖自建组件。</td>
            <td>自建入口模拟故障、拨测告警通知到达时间与恢复记录。</td>
        </tr>
        <tr>
            <td>12</td>
            <td><strong>和 AI 一起运营个人 SaaS 90 天，我还会继续用观测 SaaS 吗？</strong><br><span class="badge-pro">成本账本型</span></td>
            <td>AI、监控、账单：这一季到底值不值</td>
            <td><strong>季度 TCO 账本与退出演练</strong>：自建 + 托管 SaaS 综合成本收益复盘。</td>
            <td>AI 辅助提取真实账单与维护工时；人工审查财务底稿；一键退出演练。</td>
            <td>90 天账单、省下的工时、未解决盲区、完整退出耗时记录。</td>
        </tr>
    </tbody>
</table>

<h2>五、R1–R3 可替换候选池</h2>
<table class="data-table">
    <thead>
        <tr>
            <th style="width: 8%;">编号</th>
            <th style="width: 25%;">候选主题 / 对应核心篇</th>
            <th style="width: 32%;">唯一知识点与真实 Case</th>
            <th style="width: 35%;">代码化切入与验证证据</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>R1</strong></td>
            <td><strong>AI 帮我做一次“换平台”演练</strong><br>（备选替换 #08）</td>
            <td><strong>数据可移植性</strong>：Trace 与日志从现有采集端同时流向自建与外部双目标。</td>
            <td>OTel Collector 多 exporter 路由；对账时间戳、TraceID 与字段无损性测试。</td>
        </tr>
        <tr>
            <td><strong>R2</strong></td>
            <td><strong>一次 AI 调用慢，到底是模型还是外部工具？</strong><br>（备选替换 #08）</td>
            <td><strong>调用延迟细粒度拆分</strong>：XWorkmate 模型推理耗时与外部网络工具耗时剖析。</td>
            <td>LLM Trace 探针拆分 Time-to-First-Token、Token 流速与工具调用网络 Span。</td>
        </tr>
        <tr>
            <td><strong>R3</strong></td>
            <td><strong>给 AI 只读工具后，它能不能解释一次异常？</strong><br>（备选替换 #10）</td>
            <td><strong>最小权限原则</strong>：利用只读 MCP/OWL 接口执行故障证据聚合。</td>
            <td>官方工具权限配置；系统级拦截写入调用；人工与 AI 假设对照报告。</td>
        </tr>
    </tbody>
</table>

<h2>六、事实依据与合规硬约束</h2>
<ol>
    <li><strong>北京免费专区 OpenAPI 约束</strong>：免费空间不支持通过 OpenAPI 读写数据，公开的 Terraform Provider 在免费空间仅用于离线生成与验证 HCL 语法，不宣称自动化远程 apply。商业空间额外权限单独披露。</li>
    <li><strong>服务协议第 4.7 条商用授权</strong>：免费版协议明确要求“未经书面授权不得用于商业用途”。XWorkTech 属于商业 SaaS 项目，使用免费版前必须确认书面授权范围，未授权前仅在非商业实验或授权空间验证。</li>
    <li><strong>数据安全红线</strong>：客户端 RUM 强制开启 DOM 输入框遮罩；分布式 Trace 严禁携带 JWT 密钥、Cookie、数据库明文密码及大模型 Prompt 敏感原文。</li>
    <li><strong>成本真实性</strong>：90 天账单必须严格按照实际工作空间资源量与官方计费单价核算，无账单时必须标注“假设估算”，严禁编造财务收益。</li>
</ol>

</body>
</html>"""

print("Plan HTML generator ready.")
