# -*- coding: utf-8 -*-
from generate_svgs import (
    get_a1_svg1, get_a1_svg2, get_a1_svg3, get_a1_svg4,
    get_a2_svg1, get_a2_svg2, get_a2_svg3, get_a2_svg4,
    get_a3_svg1, get_a3_svg2, get_a3_svg3, get_a3_svg4,
    get_a4_svg1, get_a4_svg2, get_a4_svg3, get_a4_svg4
)
from build_all_deliverables import PRINT_CSS

def render_article_page(art_no, title, subtitle, meta, wechat_paras, decision_table_rows, svgs, xhs_cards, code_blocks):
    wechat_html = "".join([f"<p>{p}</p>" for p in wechat_paras])
    
    rows_html = ""
    for r in decision_table_rows:
        rows_html += f"""<tr>
            <td><strong>{r[0]}</strong></td>
            <td>{r[1]}</td>
            <td>{r[2]}</td>
            <td>{r[3]}</td>
            <td>{r[4]}</td>
            <td>{r[5]}</td>
        </tr>"""
        
    svg_html = ""
    for idx, (svg_title, svg_code) in enumerate(svgs, 1):
        svg_html += f"""<div style="margin: 18px 0;">
            <div style="font-size: 9.5pt; font-weight: 700; color: #334155; margin-bottom: 4px;">图 {idx}：{svg_title}</div>
            {svg_code}
        </div>"""
        
    xhs_html = f"""<div class="xhs-card">
        <div class="xhs-header">
            <h3>📱 小红书配套图文笔记（种草与避坑实录）</h3>
        </div>
        <div style="font-size: 11pt; font-weight: 800; color: #be123c; margin-bottom: 8px;">{xhs_cards['title']}</div>
        <div style="font-size: 9.5pt; line-height: 1.6; color: #334155; white-space: pre-wrap;">{xhs_cards['body']}</div>
    </div>"""

    code_html = ""
    for c_title, c_lang, c_code in code_blocks:
        code_html += f"""<div style="margin: 12px 0;">
            <div style="font-size: 9pt; font-weight: 600; color: #475569; margin-bottom: 2px;">{c_title}</div>
            <pre class="code-block"><code>{c_code}</code></pre>
        </div>"""

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

<h2>一、微信公众号深度长文（InfoQ 实战特稿）</h2>
{wechat_html}

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

<h2>二、纯技术架构图册（无噪技术矢量流向图）</h2>
{svg_html}

<div class="page-break"></div>

<h2>三、小红书图文笔记与代码化工程资产</h2>
{xhs_html}

<h3>四、GitOps / IaC / Playbook / Vault 代码化工程落地范式</h3>
<p style="font-size: 8.5pt; color: #64748b; margin-bottom: 6px;">
遵循“杜绝 Web 界面手工操作”铁律，所有观测链路接入、探针注入、双写开关与凭据隔离均通过声明式代码固化：
</p>
{code_html}

</body>
</html>"""

print("generate_articles_html.py ready.")
