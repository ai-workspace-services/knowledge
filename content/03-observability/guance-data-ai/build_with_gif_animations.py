# -*- coding: utf-8 -*-
import os
import subprocess
from build_all_deliverables import PRINT_CSS
from build_and_compile_all import (
    A1_PARAS, A1_DECISION, A1_XHS_TITLE, A1_XHS_BODY, A1_CODE,
    A2_PARAS, A2_DECISION, A2_XHS_TITLE, A2_XHS_BODY, A2_CODE,
    A3_PARAS, A3_DECISION, A3_XHS_TITLE, A3_XHS_BODY, A3_CODE,
    A4_PARAS, A4_DECISION, A4_XHS_TITLE, A4_XHS_BODY, A4_CODE
)
from compile_all import generate_plan_html

BASE_DIR = "/Users/shenlan/workspaces/ai-workspace-service/knowledge-v5-runtime-blockers/content/03-observability/guance-data-ai"
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
PDF_DIR = os.path.join(BASE_DIR, "pdf_exports")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

articles_gif_config = [
    (1, "我的个人 SaaS 已经够便宜了，还能用什么补上监控？",
     "Cloudflare + Cloud Run + Supabase 栈下的可观测 SaaS 选型与代码化接入",
     {"knowledge": "免费额度与服务选型", "template": "对比选型型", "case": "XWorkTech UAT 多云环境观测接入", "date": "2026-10-27 (已核验)"},
     A1_PARAS, A1_DECISION,
     [("图 1：低成本栈与观测盲区拓扑（动态流向）", "a1-01-stack-blindspots-wechat.gif"),
      ("图 2：自建底座与 SaaS 托管服务能力划分（动态流向）", "a1-05-saas-or-selfhost-wechat.gif"),
      ("图 3：AI 辅助的 IaC / GitOps / Playbook / Vault 流水线（动态流向）", "a1-03-automation-path-wechat.gif"),
      ("图 4：免费专区额度与硬边界契约（动态流向）", "a1-02-free-boundary-wechat.gif")],
     {"title": A1_XHS_TITLE, "body": A1_XHS_BODY,
      "xhs_img1": "a1-01-stack-blindspots-xhs.gif", "xhs_img2": "a1-04-evidence-chain-xhs.gif"},
     A1_CODE, "01_免费额度与服务选型_图文草稿.pdf", "01-free-tier-for-indie-saas"),

    (2, "AI 帮我搬 Grafana 面板：先让数字对上，再决定切换",
     "从自建 VictoriaMetrics 到可观测 SaaS：语义对账、双写并跑与 15 分钟回退",
     {"knowledge": "面板语义对账与指标兼容", "template": "误区纠偏型", "case": "资源/流量/k6 压测三大核心面板平迁", "date": "2026-10-27 (已核验)"},
     A2_PARAS, A2_DECISION,
     [("图 1：自建面板迁移判定与漏斗模型（动态流向）", "a2-01-migration-funnel-wechat.gif"),
      ("图 2：三处最容易踩坑的查询算子与口径差异（动态流向）", "a2-02-query-traps-wechat.gif"),
      ("图 3：GitOps → renderer → HCL 代码化交付流（动态流向）", "a2-03-gitops-hcl-wechat.gif"),
      ("图 4：双写并跑与 15 分钟回退状态机（动态流向）", "a2-04-side-by-side-rollback-wechat.gif")],
     {"title": A2_XHS_TITLE, "body": A2_XHS_BODY,
      "xhs_img1": "a2-01-migration-funnel-xhs.gif", "xhs_img2": "a2-04-side-by-side-rollback-xhs.gif"},
     A2_CODE, "02_面板语义对账与平滑迁移_图文草稿.pdf", "02-observability-migration-with-rollback"),

    (3, "AI 生成的页面上线后变卡，我先看用户体验而不是 CPU",
     "UAT 页面卡顿的浏览器侧根因定位：Core Web Vitals、长任务与代码化脱敏",
     {"knowledge": "真实用户体验与前端 RUM 分析", "template": "故障复盘型", "case": "AI 生成高交互页面卡顿与 Long Task 排查", "date": "2026-10-27 (已核验)"},
     A3_PARAS, A3_DECISION,
     [("图 1：看用户体验而不是看 CPU（UX Before CPU 动图）", "ux-before-cpu-wechat.gif"),
      ("图 2：客户端字段白名单与隐私掩码（动态流向）", "field-allowlist-wechat.gif"),
      ("图 3：RUM 探针注入与流水线构建（动态流向）", "rum-pipeline-wechat.gif"),
      ("图 4：前端长任务（Long Task）与后端 API 关联（动态流向）", "ux-before-cpu-wechat.gif")],
     {"title": A3_XHS_TITLE, "body": A3_XHS_BODY,
      "xhs_img1": "ux-before-cpu-xhs.gif", "xhs_img2": "rum-pipeline-xhs.gif"},
     A3_CODE, "03_前端真实体验与RUM分析_图文草稿.pdf", "03-real-user-experience-rum"),

    (4, "一个登录请求经过几朵云？用 Trace 把它接起来",
     "Cloudflare → Cloud Run → Supabase 跨云分布式链路上下文传播与 OTel 实践",
     {"knowledge": "分布式上下文传播与跨云追踪", "template": "动手实操型", "case": "跨三朵云单次鉴权失败链路定位", "date": "2026-10-27 (已核验)"},
     A4_PARAS, A4_DECISION,
     [("图 1：一次多云登录失败的排障路径（Triage Path 动图）", "triage-path-wechat.gif"),
      ("图 2：多云栈下的观测盲区分布（Stack Blindspots 动图）", "stack-blindspots-wechat.gif"),
      ("图 3：跨多云分布式追踪证据链（Evidence Chain 动图）", "evidence-chain-wechat.gif"),
      ("图 4：W3C 统一字段契约与上下文传递（Field Contract 动图）", "field-contract-wechat.gif")],
     {"title": A4_XHS_TITLE, "body": A4_XHS_BODY,
      "xhs_img1": "triage-path-xhs.gif", "xhs_img2": "evidence-chain-xhs.gif"},
     A4_CODE, "04_跨多云链路上下文追踪_图文草稿.pdf", "04-cross-cloud-distributed-tracing")
]

def render_gif_html(art_no, title, subtitle, meta, paras, decision_table_rows, images, xhs_data, code_blocks, folder_name):
    rows_html = "".join([f"""<tr>
        <td style="font-weight: 700; color: #0f172a; background-color: #f8fafc; border: 1px solid #cbd5e1; padding: 7px 10px; width: 22%;">{r[0]}</td>
        <td style="border: 1px solid #cbd5e1; padding: 7px 10px; width: 44%; font-size: 8.5pt; line-height: 1.55;">{r[1]}</td>
        <td style="border: 1px solid #cbd5e1; padding: 7px 10px; width: 34%; font-size: 8.5pt; line-height: 1.55; color: #1e293b;">{r[2]}</td>
    </tr>""" for r in decision_table_rows])

    assets_rel_path = f"../articles/{folder_name}/assets"

    body_interwoven_html = f"""
    <p>{paras[0]}</p>
    <div style="margin: 14px 0 18px 0; text-align: center;">
        <img src="{assets_rel_path}/{images[0][1]}" style="max-width: 100%; height: auto; border-radius: 6px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.06);" />
        <div style="font-size: 8.5pt; font-weight: 700; color: #475569; margin-top: 4px;">{images[0][0]}</div>
    </div>

    <p>{paras[1]}</p>
    <div style="margin: 14px 0 18px 0; text-align: center;">
        <img src="{assets_rel_path}/{images[1][1]}" style="max-width: 100%; height: auto; border-radius: 6px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.06);" />
        <div style="font-size: 8.5pt; font-weight: 700; color: #475569; margin-top: 4px;">{images[1][0]}</div>
    </div>

    <div class="page-break"></div>

    <p>{paras[2]}</p>
    <div style="margin: 14px 0 18px 0; text-align: center;">
        <img src="{assets_rel_path}/{images[2][1]}" style="max-width: 100%; height: auto; border-radius: 6px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.06);" />
        <div style="font-size: 8.5pt; font-weight: 700; color: #475569; margin-top: 4px;">{images[2][0]}</div>
    </div>

    <p>{paras[3]}</p>
    <div style="margin: 14px 0 18px 0; text-align: center;">
        <img src="{assets_rel_path}/{images[3][1]}" style="max-width: 100%; height: auto; border-radius: 6px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.06);" />
        <div style="font-size: 8.5pt; font-weight: 700; color: #475569; margin-top: 4px;">{images[3][0]}</div>
    </div>

    <p>{paras[4]}</p>
    """

    xhs_html = f"""<div class="xhs-card">
        <div class="xhs-header">
            <h3>📱 小红书配套图文笔记（GIF 动图素材版）</h3>
        </div>
        <div style="font-size: 11pt; font-weight: 800; color: #be123c; margin-bottom: 8px;">{xhs_data['title']}</div>
        <div style="font-size: 9.5pt; line-height: 1.6; color: #334155; white-space: pre-wrap;">{xhs_data['body']}</div>
        
        <div style="margin-top: 14px; border-top: 1px dashed #cbd5e1; padding-top: 10px;">
            <div style="font-size: 8.5pt; font-weight: 700; color: #be123c; margin-bottom: 4px;">【小红书附图 1：核心多云链路拓扑 (GIF 动图)】</div>
            <img src="{assets_rel_path}/{xhs_data['xhs_img1']}" style="max-width: 100%; height: auto; border-radius: 6px; border: 1px solid #fed7aa; margin-bottom: 8px;" />
            <div style="font-size: 8.5pt; font-weight: 700; color: #be123c; margin-bottom: 4px;">【小红书附图 2：脱敏实测数据与指标验证 (GIF 动图)】</div>
            <img src="{assets_rel_path}/{xhs_data['xhs_img2']}" style="max-width: 100%; height: auto; border-radius: 6px; border: 1px solid #fed7aa;" />
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

<h2>一、微信公众号深度长文（正文内嵌 GIF 动图版）</h2>
{body_interwoven_html}

<h3>架构视角决策表（移动端 3 列精简版）</h3>
<table class="decision-table mobile-optimized" style="width: 100%; border-collapse: collapse; margin: 12px 0;">
    <thead>
        <tr>
            <th style="width: 22%; background-color: #e2e8f0; color: #0f172a; font-weight: 700; border: 1px solid #cbd5e1; padding: 8px 10px; text-align: left;">决策维度</th>
            <th style="width: 44%; background-color: #e2e8f0; color: #0f172a; font-weight: 700; border: 1px solid #cbd5e1; padding: 8px 10px; text-align: left;">方案对比 (自建基准 vs 观测云)</th>
            <th style="width: 34%; background-color: #e2e8f0; color: #0f172a; font-weight: 700; border: 1px solid #cbd5e1; padding: 8px 10px; text-align: left;">独立开发建议与避坑 (移动端决策)</th>
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

def build_gif_bundle():
    print("[1/6] Master Plan PDF...")
    plan_html = generate_plan_html()
    plan_html_path = os.path.join(PDF_DIR, "00_plan.html")
    plan_pdf_path = os.path.join(PDF_DIR, "00_独立开发观察者计划_首季完整策划方案.pdf")
    with open(plan_html_path, "w", encoding="utf-8") as f:
        f.write(plan_html)
    subprocess.run([CHROME, "--headless", "--no-pdf-header-footer", f"--print-to-pdf={plan_pdf_path}", plan_html_path], check=True)
    print(f"  -> Generated: {plan_pdf_path}")

    combined_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>独立开发观察者计划：首季核心前 4 篇图文草稿全集（GIF 动图素材版）</title>
<style>
{PRINT_CSS}
</style>
</head>
<body>
<div style="text-align: center; padding: 40px 0 60px 0; border-bottom: 2px solid #2563eb;">
    <div class="series-tag">INDIE HACKER OBSERVABILITY OBSERVATION PROGRAM · MASTER COMPILATION</div>
    <h1 style="font-size: 26pt; margin: 16px 0;">首季核心前 4 篇图文草稿全集（GIF 动图素材版）</h1>
    <div style="font-size: 13pt; color: #475569;">微信公众号 InfoQ 实战长文 + 小红书种草笔记 + Google Drive GIF 动图素材插图 + 全代码化交付清单</div>
</div>
<div class="page-break"></div>
"""

    for art_no, title, subtitle, meta, paras, decision, imgs, xhs, code, pdf_name, folder_name in articles_gif_config:
        print(f"[{art_no + 1}/6] Generating Article {art_no:02d} with GIF animation materials...")
        
        # 1. Update Markdown draft
        md_path = os.path.join(ARTICLES_DIR, folder_name, "article_draft.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n## {subtitle}\n\n")
            f.write(f"> **唯一知识点**：{meta['knowledge']} | **循环模板**：{meta['template']} | **核验日期**：{meta['date']}\n\n---\n\n")
            f.write("### 微信公众号深度长文（正文内嵌 GIF 动图版）\n\n")
            
            f.write(f"{paras[0]}\n\n")
            f.write(f"![{imgs[0][0]}](./assets/{imgs[0][1]})\n\n")
            
            f.write(f"{paras[1]}\n\n")
            f.write(f"![{imgs[1][0]}](./assets/{imgs[1][1]})\n\n")
            
            f.write(f"{paras[2]}\n\n")
            f.write(f"![{imgs[2][0]}](./assets/{imgs[2][1]})\n\n")
            
            f.write(f"{paras[3]}\n\n")
            f.write(f"![{imgs[3][0]}](./assets/{imgs[3][1]})\n\n")
            
            f.write(f"{paras[4]}\n\n")
            f.write("#### 架构视角决策表（移动端优化 3 列精简版）\n\n")
            f.write("| 决策维度 | 方案对比 (自建基准 vs 观测云) | 独立开发建议与避坑 (移动端决策) |\n")
            f.write("| :--- | :--- | :--- |\n")
            for r in decision:
                f.write(f"| **{r[0]}** | {r[1]} | {r[2]} |\n")
            f.write("\n---\n\n")
            
            f.write("### 小红书配套图文笔记\n\n")
            f.write(f"**{xhs['title']}**\n\n")
            f.write(f"{xhs['body']}\n\n")
            f.write(f"![小红书配图 1：链路拓扑 (GIF 动图)](./assets/{xhs['xhs_img1']})\n\n")
            f.write(f"![小红书配图 2：脱敏实测数据 (GIF 动图)](./assets/{xhs['xhs_img2']})\n\n---\n\n")
            
            f.write("### GitOps / IaC / Playbook / Vault 代码化工程落地范式\n\n")
            for c_title, c_lang, c_code in code:
                f.write(f"#### {c_title}\n```{c_lang}\n{c_code}\n```\n\n")
                
        print(f"  -> Markdown updated with GIF references: {md_path}")

        # 2. Render HTML
        html_content = render_gif_html(art_no, title, subtitle, meta, paras, decision, imgs, xhs, code, folder_name)
        html_path = os.path.join(PDF_DIR, f"{art_no:02d}_article.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # 3. Print PDF via Chrome
        pdf_path = os.path.join(PDF_DIR, pdf_name)
        subprocess.run([CHROME, "--headless", "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", html_path], check=True)
        print(f"  -> Recompiled PDF with GIF animations: {pdf_path}")

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
    print(f"  -> Recompiled Combined PDF with GIF animations: {combined_pdf_path}")

if __name__ == '__main__':
    build_gif_bundle()
    print("\n[SUCCESS] All articles and PDFs compiled with Google Drive GIF animation materials!")
