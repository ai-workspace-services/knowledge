# -*- coding: utf-8 -*-
import os
import subprocess
from generate_svgs import (
    get_a1_svg1, get_a1_svg2, get_a1_svg3, get_a1_svg4,
    get_a2_svg1, get_a2_svg2, get_a2_svg3, get_a2_svg4,
    get_a3_svg1, get_a3_svg2, get_a3_svg3, get_a3_svg4,
    get_a4_svg1, get_a4_svg2, get_a4_svg3, get_a4_svg4
)
from build_all_deliverables import PRINT_CSS
from build_and_compile_all import (
    A1_PARAS, A1_DECISION, A1_XHS_TITLE, A1_XHS_BODY, A1_CODE,
    A2_PARAS, A2_DECISION, A2_XHS_TITLE, A2_XHS_BODY, A2_CODE,
    A3_PARAS, A3_DECISION, A3_XHS_TITLE, A3_XHS_BODY, A3_CODE,
    A4_PARAS, A4_DECISION, A4_XHS_TITLE, A4_XHS_BODY, A4_CODE
)

BASE_DIR = "/Users/shenlan/workspaces/ai-workspace-service/knowledge-v5-runtime-blockers/content/03-observability/guance-data-ai"
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
PDF_DIR = os.path.join(BASE_DIR, "pdf_exports")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def render_inline_article_html(art_no, title, subtitle, meta, paras, decision_table_rows, inline_svgs, xhs_data, code_blocks):
    """
    Renders article HTML with images strictly inserted between paragraphs:
    - Para 0 -> SVG 0 (Topology / Problem)
    - Para 1 -> SVG 1 (Architecture Boundary / Model)
    - Para 2 -> SVG 2 (GitOps / Code Pipeline)
    - Para 3 -> SVG 3 (Optimization / Waterfall / Reconcile)
    - Para 4 -> Decision Table
    - XHS Card -> with embedded Link Diagram & Metric Diagram!
    """
    rows_html = "".join([f"""<tr>
        <td><strong>{r[0]}</strong></td>
        <td>{r[1]}</td>
        <td>{r[2]}</td>
        <td>{r[3]}</td>
        <td>{r[4]}</td>
        <td>{r[5]}</td>
    </tr>""" for r in decision_table_rows])

    # Build interwoven body
    body_interwoven_html = f"""
    <p>{paras[0]}</p>
    <div style="margin: 12px 0 16px 0;">
        <div style="font-size: 8.5pt; font-weight: 700; color: #475569; margin-bottom: 2px;">图 1：{inline_svgs[0][0]}</div>
        {inline_svgs[0][1]}
    </div>

    <p>{paras[1]}</p>
    <div style="margin: 12px 0 16px 0;">
        <div style="font-size: 8.5pt; font-weight: 700; color: #475569; margin-bottom: 2px;">图 2：{inline_svgs[1][0]}</div>
        {inline_svgs[1][1]}
    </div>

    <div class="page-break"></div>

    <p>{paras[2]}</p>
    <div style="margin: 12px 0 16px 0;">
        <div style="font-size: 8.5pt; font-weight: 700; color: #475569; margin-bottom: 2px;">图 3：{inline_svgs[2][0]}</div>
        {inline_svgs[2][1]}
    </div>

    <p>{paras[3]}</p>
    <div style="margin: 12px 0 16px 0;">
        <div style="font-size: 8.5pt; font-weight: 700; color: #475569; margin-bottom: 2px;">图 4：{inline_svgs[3][0]}</div>
        {inline_svgs[3][1]}
    </div>

    <p>{paras[4]}</p>
    """

    xhs_html = f"""<div class="xhs-card">
        <div class="xhs-header">
            <h3>📱 小红书配套图文笔记（种草与避坑实录）</h3>
        </div>
        <div style="font-size: 11pt; font-weight: 800; color: #be123c; margin-bottom: 8px;">{xhs_data['title']}</div>
        <div style="font-size: 9.5pt; line-height: 1.6; color: #334155; white-space: pre-wrap;">{xhs_data['body']}</div>
        
        <div style="margin-top: 14px; border-top: 1px dashed #cbd5e1; padding-top: 10px;">
            <div style="font-size: 8.5pt; font-weight: 700; color: #be123c; margin-bottom: 4px;">【小红书附图 1：核心多云链路拓扑】</div>
            {inline_svgs[0][1]}
            <div style="font-size: 8.5pt; font-weight: 700; color: #be123c; margin: 10px 0 4px 0;">【小红书附图 2：脱敏实测数据与指标验证】</div>
            {inline_svgs[3][1]}
        </div>
    </div>"""

    code_html = "".join([f"""<div style="margin: 12px 0;">
        <div style="font-size: 9pt; font-weight: 600; color: #475569; margin-bottom: 2px;">{c_title}</div>
        <pre class="code-block"><code>{c_code}</code></pre>
    </div>""" for c_title, c_lang, c_code in code_blocks])

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
{PRINT_CSS}
</style>
</head>
<body>

<div class="header-banner">
    <div class="series-tag">INDIE OBSERVER · ARTICLE {art_no:02d}</div>
    <h1>{title}</h1>
    <div class="sub-title">{subtitle}</div>
</div>

<div class="meta-grid">
    <div class="meta-item"><strong>唯一知识点</strong>{meta['knowledge']}</div>
    <div class="meta-item"><strong>循环模板</strong>{meta['template']}</div>
    <div class="meta-item"><strong>真实业务 Case</strong>{meta['case']}</div>
    <div class="meta-item"><strong>实测/核验日期</strong>{meta['date']}</div>
</div>

<h2>一、微信公众号深度长文（正文图文贯穿）</h2>
{body_interwoven_html}

<h3>架构视角决策表</h3>
<table class="decision-table">
    <thead>
        <tr>
            <th style="width: 15%;">评估维度</th>
            <th style="width: 17%;">自建 Victoria+Grafana</th>
            <th style="width: 17%;">观测云免费专区 (北京)</th>
            <th style="width: 17%;">观测云商业版 (估算)</th>
            <th style="width: 18%;">客观事实依据与来源</th>
            <th style="width: 16%;">独立开发适用场景</th>
        </tr>
    </thead>
    <tbody>
        {rows_html}
    </tbody>
</table>

<div class="page-break"></div>

<h2>二、小红书图文笔记与核心工程资产</h2>
{xhs_html}

<h3>三、GitOps / IaC / Playbook / Vault 代码化工程落地范式</h3>
<p style="font-size: 8.5pt; color: #64748b; margin-bottom: 6px;">
遵循“杜绝 Web 界面手工操作”铁律，所有观测链路接入、探针注入、双写开关与凭据隔离均通过声明式代码固化：
</p>
{code_html}

</body>
</html>"""

articles_config = [
    (1, "我的个人 SaaS 已经够便宜了，还能用什么补上监控？",
     "Cloudflare + Cloud Run + Supabase 栈下的可观测 SaaS 选型与代码化接入",
     {"knowledge": "免费额度与服务选型", "template": "对比选型型", "case": "XWorkTech UAT 多云环境观测接入", "date": "2026-10-27 (已核验)"},
     A1_PARAS, A1_DECISION,
     [("个人 SaaS 多云拓扑与观测注入点", get_a1_svg1(), "fig1_topology.png"),
      ("自建底座与 SaaS 托管服务能力划分拓扑", get_a1_svg4(), "fig4_boundary.png"),
      ("GitOps + IaC + Playbook + Vault 交付流水线", get_a1_svg2(), "fig2_pipeline.png"),
      ("指标白名单过滤与配额防溢出缓冲架构", get_a1_svg3(), "fig3_optimization.png")],
     {"title": A1_XHS_TITLE, "body": A1_XHS_BODY}, A1_CODE,
     "01_免费额度与服务选型_图文草稿.pdf", "01-free-tier-for-indie-saas"),

    (2, "AI 帮我搬 Grafana 面板：先让数字对上，再决定切换",
     "从自建 VictoriaMetrics 到可观测 SaaS：语义对账、双写并跑与 15 分钟回退",
     {"knowledge": "面板语义对账与指标兼容", "template": "误区纠偏型", "case": "资源/流量/k6 压测三大核心面板平迁", "date": "2026-10-27 (已核验)"},
     A2_PARAS, A2_DECISION,
     [("Grafana JSON AST 解析与 HCL 转换流水线", get_a2_svg1(), "fig1_ast_parser.png"),
      ("监控状态机：从验证、双写到平滑切流状态转移图", get_a2_svg4(), "fig4_state_machine.png"),
      ("双写并跑与 15 分钟熔断回退拓扑", get_a2_svg2(), "fig2_circuit_breaker.png"),
      ("PromQL 语义对账与指标差异收敛矩阵", get_a2_svg3(), "fig3_reconciliation.png")],
     {"title": A2_XHS_TITLE, "body": A2_XHS_BODY}, A2_CODE,
     "02_面板语义对账与平滑迁移_图文草稿.pdf", "02-observability-migration-with-rollback"),

    (3, "AI 生成的页面上线后变卡，我先看用户体验而不是 CPU",
     "UAT 页面卡顿的浏览器侧根因定位：Core Web Vitals、长任务与代码化脱敏",
     {"knowledge": "真实用户体验与前端 RUM 分析", "template": "故障复盘型", "case": "AI 生成高交互页面卡顿与 Long Task 排查", "date": "2026-10-27 (已核验)"},
     A3_PARAS, A3_DECISION,
     [("现代 Web 前端性能瓶颈与 Core Web Vitals 采集流", get_a3_svg1(), "fig1_vitals.png"),
      ("客户端 RUM 会话与分布式 Trace 关联打通机制", get_a3_svg4(), "fig4_correlation.png"),
      ("代码化客户端脱敏与 DOM 掩码过滤管线", get_a3_svg2(), "fig2_privacy.png"),
      ("前端长任务（Long Task）与后端 API 瀑布流关联剖析", get_a3_svg3(), "fig3_waterfall.png")],
     {"title": A3_XHS_TITLE, "body": A3_XHS_BODY}, A3_CODE,
     "03_前端真实体验与RUM分析_图文草稿.pdf", "03-real-user-experience-rum"),

    (4, "一个登录请求经过几朵云？用 Trace 把它接起来",
     "Cloudflare → Cloud Run → Supabase 跨云分布式链路上下文传播与 OTel 实践",
     {"knowledge": "分布式上下文传播与跨云追踪", "template": "动手实操型", "case": "跨三朵云单次鉴权失败链路定位", "date": "2026-10-27 (已核验)"},
     A4_PARAS, A4_DECISION,
     [("W3C TraceContext 跨多云边界上下文传递全貌", get_a4_svg1(), "fig1_context_prop.png"),
      ("多云边界安全鉴权与凭据动态注入架构", get_a4_svg4(), "fig4_vault_security.png"),
      ("OTel Collector 多云汇聚与动态路由管道", get_a4_svg2(), "fig2_collector_pipe.png"),
      ("登录链路 Span 拓扑与延时耗时瀑布图", get_a4_svg3(), "fig3_auth_waterfall.png")],
     {"title": A4_XHS_TITLE, "body": A4_XHS_BODY}, A4_CODE,
     "04_跨多云链路上下文追踪_图文草稿.pdf", "04-cross-cloud-distributed-tracing")
]

combined_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>独立开发观察者计划：首季核心前 4 篇图文草稿全集</title>
<style>
{PRINT_CSS}
</style>
</head>
<body>
<div style="text-align: center; padding: 40px 0 60px 0; border-bottom: 2px solid #2563eb;">
    <div class="series-tag">INDIE HACKER OBSERVABILITY OBSERVATION PROGRAM · MASTER COMPILATION</div>
    <h1 style="font-size: 26pt; margin: 16px 0;">首季核心前 4 篇图文草稿全集（正文图片内嵌版）</h1>
    <div style="font-size: 13pt; color: #475569;">微信公众号 InfoQ 实战长文 + 小红书种草笔记 + 矢量技术架构图 + 全代码化交付清单</div>
</div>
<div class="page-break"></div>
"""

for art_no, title, subtitle, meta, paras, decision, svgs, xhs, code, pdf_name, folder_name in articles_config:
    print(f"Compiling Article {art_no:02d} with inline images...")
    
    # 1. Generate interwoven Markdown
    md_path = os.path.join(ARTICLES_DIR, folder_name, "article_draft.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n## {subtitle}\n\n")
        f.write(f"> **唯一知识点**：{meta['knowledge']} | **循环模板**：{meta['template']} | **核验日期**：{meta['date']}\n\n---\n\n")
        f.write("### 微信公众号深度长文（图文贯穿版）\n\n")
        
        # Para 1 + Fig 1
        f.write(f"{paras[0]}\n\n")
        f.write(f"![图 1：{svgs[0][0]}](./assets/{svgs[0][2]})\n\n")
        
        # Para 2 + Fig 2
        f.write(f"{paras[1]}\n\n")
        f.write(f"![图 2：{svgs[1][0]}](./assets/{svgs[1][2]})\n\n")
        
        # Para 3 + Fig 3
        f.write(f"{paras[2]}\n\n")
        f.write(f"![图 3：{svgs[2][0]}](./assets/{svgs[2][2]})\n\n")
        
        # Para 4 + Fig 4
        f.write(f"{paras[3]}\n\n")
        f.write(f"![图 4：{svgs[3][0]}](./assets/{svgs[3][2]})\n\n")
        
        # Para 5 + Decision Table
        f.write(f"{paras[4]}\n\n")
        f.write("#### 架构视角决策表\n\n")
        f.write("| 评估维度 | 自建 Victoria+Grafana | 观测云免费专区 (北京) | 观测云商业版 (估算) | 客观事实依据与来源 | 独立开发适用场景 |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for r in decision:
            f.write(f"| **{r[0]}** | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |\n")
        f.write("\n---\n\n")
        
        # XHS Section with inline illustrations
        f.write("### 小红书配套图文笔记\n\n")
        f.write(f"**{xhs['title']}**\n\n")
        f.write(f"{xhs['body']}\n\n")
        f.write(f"![小红书配图 1：链路拓扑](./assets/{svgs[0][2]})\n\n")
        f.write(f"![小红书配图 2：脱敏实测数据](./assets/{svgs[3][2]})\n\n---\n\n")
        
        # Code section
        f.write("### GitOps / IaC / Playbook / Vault 代码化工程落地范式\n\n")
        for c_title, c_lang, c_code in code:
            f.write(f"#### {c_title}\n```{c_lang}\n{c_code}\n```\n\n")
            
    print(f"  -> Markdown updated with inline images: {md_path}")

    # 2. Generate HTML with inline images
    html_content = render_inline_article_html(art_no, title, subtitle, meta, paras, decision, svgs, xhs, code)
    html_path = os.path.join(PDF_DIR, f"{art_no:02d}_article.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 3. Print PDF via Chrome
    pdf_path = os.path.join(PDF_DIR, pdf_name)
    subprocess.run([CHROME, "--headless", "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", html_path], check=True)
    print(f"  -> Recompiled PDF: {pdf_path}")

    # Append to combined HTML
    combined_html += f"""<div style="margin-top: 10px;">
    {html_content.replace('<!DOCTYPE html>', '').replace('<html lang="zh-CN">', '').replace('</html>', '').replace('<head>', '').replace('</head>', '').replace('<body>', '').replace('</body>', '').replace(f'<style>{PRINT_CSS}</style>', '')}
    </div>
    <div class="page-break"></div>"""

combined_html += "</body></html>"
combined_html_path = os.path.join(PDF_DIR, "combined_articles.html")
combined_pdf_path = os.path.join(PDF_DIR, "首季前4篇图文草稿_合辑.pdf")
with open(combined_html_path, "w", encoding="utf-8") as f:
    f.write(combined_html)
subprocess.run([CHROME, "--headless", "--no-pdf-header-footer", f"--print-to-pdf={combined_pdf_path}", combined_html_path], check=True)
print(f"  -> Recompiled Master Combined PDF: {combined_pdf_path}")

print("\n[SUCCESS] All articles updated with inline images and PDFs successfully recompiled!")
