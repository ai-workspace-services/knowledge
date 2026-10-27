# -*- coding: utf-8 -*-
import os
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

articles_meta = [
    ("01-free-tier-for-indie-saas", [
        ("fig1_topology", "个人 SaaS 多云拓扑与观测注入点", get_a1_svg1()),
        ("fig2_pipeline", "GitOps + IaC + Playbook + Vault 交付流水线", get_a1_svg2()),
        ("fig3_optimization", "指标白名单过滤与配额防溢出缓冲架构", get_a1_svg3()),
        ("fig4_boundary", "自建底座与 SaaS 托管服务能力划分拓扑", get_a1_svg4())
    ]),
    ("02-observability-migration-with-rollback", [
        ("fig1_ast_parser", "Grafana JSON AST 解析与 HCL 转换流水线", get_a2_svg1()),
        ("fig2_circuit_breaker", "双写并跑与 15 分钟熔断回退拓扑", get_a2_svg2()),
        ("fig3_reconciliation", "PromQL 语义对账与指标差异收敛矩阵", get_a2_svg3()),
        ("fig4_state_machine", "监控状态机：从验证、双写到平滑切流状态转移图", get_a2_svg4())
    ]),
    ("03-real-user-experience-rum", [
        ("fig1_vitals", "现代 Web 前端性能瓶颈与 Core Web Vitals 采集流", get_a3_svg1()),
        ("fig2_privacy", "代码化客户端脱敏与 DOM 掩码过滤管线", get_a3_svg2()),
        ("fig3_waterfall", "前端长任务（Long Task）与后端 API 瀑布流关联剖析", get_a3_svg3()),
        ("fig4_correlation", "客户端 RUM 会话与分布式 Trace 关联打通机制", get_a3_svg4())
    ]),
    ("04-cross-cloud-distributed-tracing", [
        ("fig1_context_prop", "W3C TraceContext 跨多云边界上下文传递全貌", get_a4_svg1()),
        ("fig2_collector_pipe", "OTel Collector 多云汇聚与动态路由管道", get_a4_svg2()),
        ("fig3_auth_waterfall", "登录链路 Span 拓扑与延时耗时瀑布图", get_a4_svg3()),
        ("fig4_vault_security", "多云边界安全鉴权与凭据动态注入架构", get_a4_svg4())
    ])
]

# Save all SVGs and render PNGs
for folder, fig_list in articles_meta:
    assets_dir = os.path.join(ARTICLES_DIR, folder, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    for fig_id, fig_title, svg_code in fig_list:
        svg_path = os.path.join(assets_dir, f"{fig_id}.svg")
        png_path = os.path.join(assets_dir, f"{fig_id}.png")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_code)
        # Render PNG via headless chrome
        subprocess.run([
            CHROME, "--headless", f"--screenshot={png_path}",
            "--window-size=800,320", "--default-background-color=00000000",
            svg_path
        ], check=True)
        print(f"Exported: {png_path}")

print("All standalone SVGs and PNGs successfully exported into article assets/ folders.")
