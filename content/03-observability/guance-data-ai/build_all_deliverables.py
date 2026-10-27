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
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
PDF_DIR = os.path.join(BASE_DIR, "pdf_exports")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

os.makedirs(PDF_DIR, exist_ok=True)

def count_non_space(text):
    return len(re.sub(r'\s+', '', text))

# CSS Style for PDF
PRINT_CSS = """
@page {
    size: A4;
    margin: 14mm 16mm 14mm 16mm;
    @bottom-center {
        content: counter(page);
        font-size: 9pt;
        color: #94a3b8;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Segoe UI", Roboto, sans-serif;
    color: #1e293b;
    line-height: 1.65;
    font-size: 10.5pt;
    margin: 0;
    padding: 0;
    background-color: #ffffff;
}
.header-banner {
    border-bottom: 2px solid #2563eb;
    padding-bottom: 8px;
    margin-bottom: 18px;
}
.series-tag {
    font-size: 8.5pt;
    font-weight: 700;
    text-transform: uppercase;
    color: #2563eb;
    letter-spacing: 0.8px;
}
h1 {
    font-size: 19pt;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.25;
    margin: 4px 0 6px 0;
}
.sub-title {
    font-size: 11pt;
    color: #475569;
    font-weight: 500;
    margin-bottom: 12px;
}
.meta-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 8.5pt;
    margin-bottom: 16px;
}
.meta-item strong {
    color: #334155;
    display: block;
}
h2 {
    font-size: 13pt;
    font-weight: 700;
    color: #1e3a8a;
    border-left: 4px solid #2563eb;
    padding-left: 8px;
    margin: 18px 0 10px 0;
}
h3 {
    font-size: 11pt;
    font-weight: 600;
    color: #0f172a;
    margin: 14px 0 6px 0;
}
p {
    margin: 0 0 10px 0;
    text-align: justify;
}
.decision-table, .data-table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 8.5pt;
    line-height: 1.5;
    word-break: break-word;
}
.decision-table th, .data-table th {
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
    border: 1px solid #cbd5e1;
    padding: 8px 10px;
    text-align: left;
}
.decision-table td, .data-table td {
    border: 1px solid #e2e8f0;
    padding: 8px 10px;
    vertical-align: top;
}
.decision-table tr:nth-child(even), .data-table tr:nth-child(even) {
    background-color: #fafbfc;
}
.badge-self {
    display: inline-block;
    padding: 1px 6px;
    background: #e2e8f0;
    color: #334155;
    border-radius: 3px;
    font-weight: 600;
}
.badge-free {
    display: inline-block;
    padding: 1px 6px;
    background: #e0e7ff;
    color: #3730a3;
    border-radius: 3px;
    font-weight: 600;
}
.badge-pro {
    display: inline-block;
    padding: 1px 6px;
    background: #dbeafe;
    color: #1e40af;
    border-radius: 3px;
    font-weight: 600;
}
.xhs-card {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 16px;
    margin: 14px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.xhs-header {
    background: #ffe4e6;
    border-left: 4px solid #f43f5e;
    padding: 8px 12px;
    border-radius: 4px;
    margin-bottom: 12px;
}
.xhs-header h3 {
    color: #be123c;
    margin: 0;
    font-size: 12pt;
}
.code-block {
    background: #0f172a;
    color: #f8fafc;
    padding: 10px 14px;
    border-radius: 6px;
    font-family: "JetBrains Mono", Consolas, Monaco, monospace;
    font-size: 8pt;
    line-height: 1.45;
    overflow-x: auto;
    margin: 10px 0;
}
.page-break {
    page-break-after: always;
    break-after: page;
}
.callout {
    background: #eff6ff;
    border-left: 3px solid #3b82f6;
    padding: 8px 12px;
    font-size: 9pt;
    margin: 10px 0;
    border-radius: 0 4px 4px 0;
}
"""

print("Build script framework ready.")
