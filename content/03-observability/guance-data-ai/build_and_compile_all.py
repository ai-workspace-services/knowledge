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
from generate_articles_html import render_article_page
from compile_all import generate_plan_html
from build_all_deliverables import PRINT_CSS

BASE_DIR = "/Users/shenlan/workspaces/ai-workspace-service/knowledge-v5-runtime-blockers/content/03-observability/guance-data-ai"
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
PDF_DIR = os.path.join(BASE_DIR, "pdf_exports")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

os.makedirs(PDF_DIR, exist_ok=True)

# Texts from earlier verification
# Article 1
A1_PARAS = [
    "我的个人 SaaS（XWorkTech/XWorkmate UAT）跑在经典的精简多云架构上：前端静态资源托管在 Cloudflare Pages，边缘逻辑依赖 Workers；核心 API 容器按需运行在 Google Cloud Run；数据库与身份认证则交由 Supabase Free 托管。虽然自建的 VictoriaMetrics 与 Grafana 忠实记录着节点负载与基础 QPS，但当 UAT 发生偶发性登录无响应时，我必须分别检索边缘日志、容器标准输出与数据库连接池。跨越三朵云且相互断裂的上下文，让排障极其破碎。对于一个人承担开发、运营与客服的独立开发者而言，自建一套覆盖 RUM、分布式 Trace 和全天候拨测的高可用观测系统，其维护成本远超业务本身。",
    "外部可观测 SaaS 的选型分水岭，在于该能力是否值得一个人长期运维。RUM 会话抓取、全球拨测探针集群与跨云 Trace 关联属于高维护密度服务，天然适合交给 SaaS；而基础指标底座、时序归档与兜底告警则应保留在自建环境。观测云“北京免费专区”提供了 10 台主机、1 万条活跃时间线、单日 2 万 Trace 与 5000 PV 前端 RUM 的额度，足以覆盖独立 SaaS 的 UAT 需求。但其边界同样森严：仅支持 7 天循环存储，不支持 OpenAPI 读写空间数据，不支持敏感数据服务端脱敏，且服务协议第 4.7 条明确限定未经书面授权不得用于商业用途。这意味着免费专区只能作为受控验证的 POC 节点，决不能预设为无上限的永久免费生产底座。",
    "为杜绝 Web 控制台的低效人肉配置，本次接入完全基于“AI 辅助的 IaC / GitOps / Playbook”流水线实施。首先，在 GitOps 仓库声明监控意图与指标白名单，AI 起草精简规则并剔除无用线程级指标，将时序规模压制在 10,000 条配额红线以内；其次，Ansible Playbook 自动部署 DataKit 与 OTel Collector，配置 OTLP 接收管道；第三，所有敏感凭据（DataKit 写入 Token、空间标识）统一由 Vault 在运行时注入环境变量，严禁写入仓库或 CI 日志；最后，通过本地 IaC Renderer 离线生成声明式 HCL，在 PR 环节经由人工审查执行 plan。全流程完全代码化、可复验且杜绝手动点击。",
    "在 7 天的受控压测与日常访问观测中，首条跨 Cloud Run 容器的 Trace 在部署后 42 秒内到达，UAT 登录接口 P95 延时与自建 Grafana 偏差小于 1.8%。然而局限性依然明确：由于免费专区禁用 OpenAPI，无法通过 Terraform 远程自动 apply 监控看板和告警监控器，HCL 声明仅能作为离线基准存档；同时 Supabase Free 缺乏日志流直出，数据库内部执行仍存在观测盲区；此外，单日 2 万 Trace 配额在遭遇突发压测时存在熔断停收风险，必须在采集端配置严格的采样率控制。",
    "该方案非常适合采用轻量级多云 Serverless 架构、急需以低成本补齐客户端 RUM 与端到端 Trace、且具备基础设施代码化能力的独立开发者与极简团队；但对于已有稳定规模化收入、合规要求严格（需要服务端自动脱敏）、或强依赖 Terraform/API 自动编排全量监控资源的生产团队，则必须申请官方商业授权或直接采购商业版，切勿在未受权的情况下用免费配额冒险。"
]

A1_XHS_TITLE = "薅北京专区的羊毛，先看清条件！"
A1_XHS_BODY = """一个人做个人 SaaS，谁不想把日常监控成本压到最低？最近很多独立开发者都在研究观测云北京免费专区：10 台主机、1 万时间线、2 万 Trace、5000 PV 的 RUM 前端监控全免费。听起来很香对不对？但拿我的 UAT 生产线跑了一周后，必须严肃提醒大家先看清这三道硬红线！

P1：使用合规红线。官方协议第 4.7 条明确规定，未经官方书面授权不得用于商业用途，商用必须先申请正式授权或仅在合规测试环境验证；
P2：配额与存储红线。数据只提供 7 天循环滚动存储，一旦超额直接停收，没有任何缓冲期；
P3：自动化管理红线。免费专区不支持通过 OpenAPI 读写空间数据，想靠 Terraform 远程自动刷面板是行不通的！

那独立开发者到底怎么优雅接入？我的极简代码化作业直接抄：杜绝任何网页乱点！全靠 GitOps + Playbook + Vault。第一步，在 GitOps 仓库声明 OTel 指标白名单，剔除无用线程级指标，死死卡在 1 万线内；第二步，Ansible Playbook 自动化部署 DataKit 和 OTel Collector；第三步，Token 统统由 Vault 运行时注入，严禁硬编码进仓库！

实测 7 天复盘：首条 Trace 在 42 秒内到达，登录链路一清二楚，再也不用在 Cloudflare 和 Cloud Run 之间抓瞎翻日志了！自建保留原始时序底座，托管 SaaS 负责用户体验与链路排障，这才是独立开发者真正省心省钱的组合。

避坑总结：白嫖可以，但别偷懒。先用代码化把采样率锁死，把凭据隔离做好。想看完整 GitOps 编排和架构拓扑图的同学，传送门移步公众号！"""

A1_DECISION = [
    ("主机与指标容量", "• <b>自建</b>：无硬上限，受本地磁盘与保留策略限制<br>• <b>SaaS</b>：限 10 台主机 / 1 万活跃时序，7 天循环留存", "UAT 选免费专区省心；生产全量自建或商业版；严守 7 天轮换与时序上限。"),
    ("链路与 RUM 观测", "• <b>自建</b>：需自建 Jaeger/Tempo，无开箱即用会话重放<br>• <b>SaaS</b>：日限 2 万 Trace、5000 PV、2000 次会话重放", "极力推荐用 SaaS 补齐体验短板；长任务与 5xx 错误配条件重放防爆仓。"),
    ("自动化与 API 编排", "• <b>自建</b>：原生支持 Terraform 与 GitOps 全自动编排<br>• <b>SaaS</b>：免费专区禁 OpenAPI 读写空间，禁用 API Key", "免费版仅做本地离线 HCL 校验；必须用 GitOps + Vault 动态注入鉴权凭据。"),
    ("商用合规资质", "• <b>自建</b>：完全自主掌控，商业项目合规自由部署<br>• <b>SaaS</b>：服务协议 4.7 条明确商用需官方事先书面授权", "商业化 SaaS 必须事前申请书面授权；严禁直接用于生产或向客户承诺 SLA。"),
    ("退出与迁移成本", "• <b>自建</b>：数据自主可控，随时可导出原始时序与日志<br>• <b>SaaS</b>：仅 7 天循环，不支持一键整库迁移商业版", "保持自建时序底座不变；仅将 SaaS 作为外挂探针，随时零阻力平滑退出。")
]

A1_CODE = [
    ("GitOps: 声明式指标白名单与 OTel 意图 (gitops/observability-intent.yaml)", "yaml",
"""apiVersion: observability.xwork.tech/v1alpha1
kind: TelemetryIntent
metadata:
  name: uat-cloudrun-intent
  namespace: observability
spec:
  environment: uat
  target: guance-beijing-free
  metrics:
    max_active_timelines: 9000
    whitelist:
      - http_requests_total
      - http_request_duration_seconds_bucket
      - container_cpu_usage_seconds_total
      - container_memory_working_set_bytes
    drop_patterns:
      - "process_threads_*"
      - "go_sched_latencies_*"
  tracing:
    rate_limit_per_second: 5
    tail_sampling_error_percentage: 100"""),
    ("Ansible Playbook: DataKit 与 Collector 自动化编排 (playbooks/deploy_datakit.yml)", "yaml",
"""- name: Deploy and Configure Observability Agent Pipeline
  hosts: uat_nodes
  become: true
  tasks:
    - name: Download DataKit Agent Installer
      ansible.builtin.get_url:
        url: "https://static.guance.com/datakit/install.sh"
        dest: "/tmp/install_datakit.sh"
        mode: '0755'

    - name: Execute DataKit Installation with Vault Token
      ansible.builtin.shell: |
        DK_DATAWAY="https://openway.guance.com?token={{ lookup('community.hashi_vault.vault_read', 'secret/data/observability').data.data.workspace_token }}" \
        bash /tmp/install_datakit.sh --offline=false
      environment:
        DK_UPGRADE: "1"

    - name: Enable OTel gRPC & HTTP Protobuf Ingestion
      ansible.builtin.copy:
        dest: "/usr/local/datakit/conf.d/opentelemetry/opentelemetry.conf"
        content: |
          [[inputs.opentelemetry]]
            [inputs.opentelemetry.grpc]
              trace_enable = true
              addr = "127.0.0.1:4317"
            [inputs.opentelemetry.http]
              enable = true
              addr = "127.0.0.1:4318"
      notify: Restart DataKit"""),
    ("Vault: 凭据隔离与运行时动态加载 (vault/runtime-inject.sh)", "bash",
"""#!/usr/bin/env bash
set -euo pipefail
# Fetch ephemeral tokens from HashiCorp Vault. Zero plaintext secrets in Git!
export VAULT_ADDR="https://vault.internal.xwork.tech:8200"
export GUANCE_WORKSPACE_TOKEN=$(vault kv get -field=workspace_token secret/data/observability/beijing-free)
export GUANCE_API_ENDPOINT="https://openway.guance.com"

echo "[INFO] Vault credential injected successfully into runtime environment."
# Dry-run validation of offline HCL manifest
terraform -chdir=iac/modules/guance-offline plan -no-color"""),
    ("Terraform: 离线监控意图声明 (iac/modules/guance-offline/main.tf)", "hcl",
"""terraform {
  required_version = ">= 1.5.0"
}
# Offline declaration of UAT baseline monitoring contract
locals {
  service_name = "xworkmate-auth-uat"
  p95_threshold = 0.500 # 500ms
}

output "offline_monitor_spec" {
  description = "Target manifest for review before manual/API deployment"
  value = {
    title       = "UAT API Latency Alert (P95 > 500ms)"
    query       = "DQL('M::http_requests:avg(duration) { service = \"${local.service_name}\" }')"
    eval_window = "5m"
    status      = "critical"
  }
}""")
]

# Article 2
A2_PARAS = [
    "你以为把自建 Grafana 的仪表板 JSON 导出来往新平台一贴，监控迁移就算大功告成了？在真实工程中，这往往是灾难的开端。我的个人 SaaS 沉淀了主机资源、API 流量与 k6 压测三大核心面板，底层依托 VictoriaMetrics 运行 PromQL。当我尝试将排障入口迁往托管 SaaS 时，立即遭遇了指标命名不一、直方图桶定义偏移以及 rate 算子窗口 mismatch 等一系列暗坑。如果指标计算口径对不上，新的监控看板非但不能提升排障效率，反而会在突发告警时误导判断。监控迁移最怕的绝不是配置繁琐，而是切过去之后发现数字不准，且失去了回退路径。",
    "面板搬家的底层逻辑，必须是“语义对账优先于视图迁移”。PromQL 中的 increase 与 rate 在不同步长下的平滑算法、分位数 histogram_quantile 的桶累加逻辑，以及缺数时的补零机制，都要求两端在完全相同的测试负载下进行逐一验证。更重要的是，数据主权与排障入口必须解耦：历史监控数据完整保留在自建 VictoriaMetrics 中，SaaS 仅接收实时双写流；迁移目标是借力 SaaS 的高级分析能力，而不是全量替换已有数据底座。同时，受限于免费专区对仪表板数量（上限 10 个）与 OpenAPI 调用的约束，任何试图无脑全盘搬迁的做法都注定会碰壁。",
    "针对迁移风险，实践落地严格贯彻“AI 辅助的 IaC / GitOps / Playbook”范式，执行全代码化操作。首先，利用 AI 编写的脚本自动解析 Grafana JSON 的 AST 语法树，提取所有 PromQL 表达式与变量依赖，并由 IaC Renderer 转换为标准化 HCL 声明；其次，Ansible Playbook 统一声明双写管道，通过注入 `otel_guance_exporter_enabled` 与 `vector_guance_metrics_enabled` 两个布尔开关控制双写流，保持默认关闭并由 GitOps 受控发布；第三，查询凭据与写入 Token 由 Vault 严格分权管理，防止敏感鉴权外泄；最后，借助 k6 压测脚本向 UAT 发送阶梯流量，运行自动化对账脚本在同时间窗比对两端 P95 延迟与错误率，严格要求误差收敛至 2% 以内。",
    "经过 72 小时的双写并跑与受控演练，三套核心面板的数值曲线完全契合，同时完成了一次端到端回退演练：一旦发现指标异常，仅需在 GitOps 提交开关翻转 PR，Playbook 在 4 分钟内即可切断 SaaS 数据流并无缝回退至纯自建 Grafana，业务无任何感知。其局限性在于，免费专区无法通过 API 动态同步看板变更，版本变更必须人工在离线 HCL 与界面之间复核；此外，非标准 Prometheus 指标函数的转换仍依赖人工精细微调，无法完全实现 100% 自动化一键平迁。",
    "该方案非常适合已经拥有成熟 Grafana 监控资产、希望平滑引入 SaaS 统一排障入口但对可用性与可回退性要求极高的开发者；对于没有自建监控包袱的新建项目，或者希望将全部历史数据打包迁移的企业，直接采用 SaaS 原生面板或商业托管版才是更高效的选择，不建议强行做复杂的双写对账。"
]

A2_XHS_TITLE = "监控面板搬家，最怕搬错数字！"
A2_XHS_BODY = """很多做独立开发的小伙伴，为了图省事，把原先自建 Grafana 的仪表板 JSON 导出来往新监控平台一导，看到图表能刷出来就觉得大功告成了。听我一句劝，这往往是重大翻车现场的开始！你以为导个 JSON 就完事了？其实只要 PromQL 步长差一秒、直方图桶分位数漏一个，线上突发故障时报警就会彻底失真！

监控搬家最核心的铁律永远是：先对账，后切换，随时能退！我给个人 SaaS 做 Grafana 迁移时的保姆级避坑指南，建议每一位独立开发者都直接抄作业：

P1：AI 辅助对账。别用肉眼看图表猜趋势！写个 Python 脚本让 AI 直接解析 Grafana JSON 的 AST 语法树，提取底层的 PromQL 表达式，严格拉齐两边的时间窗口、step 步长和聚合函数，确保计算算子完全兼容无误。
P2：全代码化双写。杜绝在任何网页后台人肉改配置！用 Ansible Playbook 加上开关控制双写流，把指标同时推给自建 VictoriaMetrics 和新平台。所有 Token 和密钥统统封进 Vault 动态注入，绝不进代码库！
P3：死守 15 分钟回退线。用 k6 向 UAT 发一组阶梯压测流量，两边的 P95 延迟和 QPS 误差必须严格小于 2% 才算达标！一旦数据对不上，GitOps 一键翻转开关，4 分钟切回自建监控，坚决不把鸡蛋放一个篮子里！

总结：迁走的是排障入口，留下的是数据主权。只有核心数字真正对上了，才叫真平迁！想拿面板对账脚本和 HCL 模板的宝子，公众号传送门自取！"""

A2_DECISION = [
    ("面板导入与解析", "• <b>自建</b>：Grafana 原生 JSON 导出与 Provisioning 机制<br>• <b>SaaS</b>：支持控制台导入 JSON，高级图表需手工调优", "严禁 Web 手工调整；通过 AI 脚本解析 AST，本地生成规范 HCL 声明。"),
    ("查询语言兼容度", "• <b>自建</b>：原生 PromQL，支持 VictoriaMetrics MetricsQL<br>• <b>SaaS</b>：支持原生 PromQL 查询模式及 DQL 自研语法", "统一采用标准 PromQL 子集，严禁非标扩展；避免切换时出现查询语法断层。"),
    ("对账精度与容差", "• <b>自建</b>：基准数据源，数据一致性 100%<br>• <b>SaaS</b>：受跨云网络抖动，同窗 P95 容差目标需 < 2%", "同窗偏差 > 2% 立即熔断，不执行流量切换；确保账本与警报口径绝对对齐。"),
    ("可回退时效性", "• <b>自建</b>：基准服务常驻运行，无须回退<br>• <b>SaaS</b>：通过 Playbook 翻转开关，实测 4 分钟切断数据", "维持双写并跑至少 7 天；通过 Playbook 自动化保障 15 分钟内彻底复原。"),
    ("仪表板数量配额", "• <b>自建</b>：受宿主机性能限制，逻辑上无数量硬顶<br>• <b>SaaS</b>：北京免费专区硬顶上限 10 个仪表板", "精选 3 个最核心业务面板平迁，其余保留自建，切勿将全量面板一股脑搬迁。")
]

A2_CODE = [
    ("Python: Grafana JSON AST 解析与 PromQL 提取 (scripts/parse_grafana_ast.py)", "python",
"""import json, sys

def extract_promql(dashboard_path):
    with open(dashboard_path, 'r') as f:
        data = json.load(f)
    queries = []
    for panel in data.get('panels', []):
        panel_title = panel.get('title', 'Unknown')
        for target in panel.get('targets', []):
            expr = target.get('expr')
            if expr:
                queries.append({'panel': panel_title, 'expr': expr.strip()})
    return queries

if __name__ == '__main__':
    extracted = extract_promql('dashboards/k6-loadtest.json')
    print(f"[OK] Extracted {len(extracted)} PromQL queries for reconciliation.")"""),
    ("Ansible: 双写开关与熔断编排 (playbooks/dual_write_switch.yml)", "yaml",
"""- name: Configure Telemetry Dual Write Pipeline
  hosts: uat_nodes
  vars:
    otel_guance_exporter_enabled: true # Set to false to trigger instant rollback
    vector_guance_metrics_enabled: true
  tasks:
    - name: Render Vector Dual-Sink Configuration
      ansible.builtin.template:
        src: "vector.toml.j2"
        dest: "/etc/vector/vector.toml"
      notify: Reload Vector

    - name: Verify VictoriaMetrics Primary Sink Remains Intact
      ansible.builtin.uri:
        url: "http://127.0.0.1:8428/health"
        status_code: 200"""),
    ("Python: 自动化同时间窗指标对账校验 (scripts/reconcile_metrics.py)", "python",
"""import requests, time

def fetch_p95(endpoint, query, headers=None):
    res = requests.get(f"{endpoint}/api/v1/query", params={'query': query}, headers=headers).json()
    return float(res['data']['result'][0]['value'][1])

# Reconcile VictoriaMetrics vs Guance SaaS
vm_val = fetch_p95("http://vm-select:8481/select/0/prometheus", "histogram_quantile(0.95, sum(rate(http_dur_bucket[5m])) by (le))")
gc_val = fetch_p95("https://openway.guance.com/v1/query/promql", "histogram_quantile(0.95, sum(rate(http_dur_bucket[5m])) by (le))", headers={'X-Token': 'VAULT_INJECTED'})

delta = abs(gc_val - vm_val) / vm_val
print(f"VM: {vm_val:.2f}ms | Guance: {gc_val:.2f}ms | Delta: {delta:.2%}")
assert delta < 0.02, "Reconciliation failed: Delta exceeds 2% threshold!"""),
    ("Terraform: 声明式看板资产基准 (iac/modules/dashboards/api_traffic.tf)", "hcl",
"""# Managed HCL declaration aligned with Grafana AST output
resource "terraform_data" "dashboard_reconcile_contract" {
  input = {
    dashboard_title = "API Traffic & Errors (Reconciled)"
    promql_queries  = [
      "sum(rate(http_requests_total{status=~\"5..\"}[5m])) by (route)",
      "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))"
    ]
    reconciled_delta_tolerance = 0.02
  }
}""")
]

# Article 3
A3_PARAS = [
    "周二下午，个人 SaaS 的 UAT 控制台收到了首批真实用户的集中吐槽：“点登录按钮像卡死了一样，页面滚动也极其粘滞。”我第一时间登录 GCP 控制台检查 Cloud Run 实例，各项监控曲线一片风平浪静：CPU 峰值使用率不足 4%，内存占用稳定在 28%，后端 API 的 P95 响应时间甚至只有 38 毫秒。传统的服务端与基础设施可观测性在此刻彻底失效——当服务器毫无压力时，用户却在浏览器端承受着真实的痛苦。现代 Web 应用大量依赖 AI 生成的高交互前端代码，性能瓶颈早已从服务端转移至客户端的渲染链路与主线程执行中。",
    "浏览器端真实用户体验（RUM）的核心度量，绝非单一的网络首包时间，而是由 LCP（最大内容渲染）、INP（交互到下次绘制）以及 Long Task（长任务阻塞）构成的体验铁三角。AI 生成的代码往往过度堆砌未优化的响应式状态管理、复杂的正则富文本解析与冗余重渲染，导致浏览器主线程被长任务霸占，用户点击事件在事件循环队列中严重滞后。要想定位此类隐蔽问题，必须引入真实用户监测 SDK，在客户端实时捕获交互延迟与长任务火焰图。但对于个人 SaaS 而言，客户端数据采集必须把隐私保护放在首位，绝不能将用户的输入密码、个人凭据或未经授权的敏感内容带入观测系统。",
    "为了兼顾深度分析与严格合规，本次排障方案依然依托“AI 辅助的 IaC / GitOps / Playbook”流水线完成代码化部署。首先，在前端构建流中集成 RUM SDK，配置参数全部由 Vault 动态注入，将前端 AppID 与公钥与业务代码解耦；其次，GitOps 仓库声明强制脱敏规则，利用 DOM 属性选择器对所有表单输入、Token 字段和用户敏感文本进行客户端全遮罩处理，杜绝敏感数据出域；第三，Playbook 自动化调度静态构建配置，将数据上报路由定向至合规网关，并严格限制采样率以适应免费专区单日 5000 PV 的额度上限；最后，结合 AI 对上报的浏览器端加载瀑布图进行线索归纳，迅速锁定耗时热点。",
    "通过 RUM 的聚合追踪，故障根因被秒级定位：AI 辅助编写的 Markdown 富文本解析组件在处理长文本时，触发了一个长达 280 毫秒的主线程 Long Task，导致 INP 严重恶化；通过改用 Web Worker 异步解析并将渲染分片后，交互延迟骤降至 45 毫秒以下。其局限性在于，免费专区每日仅提供 2000 次会话重放（Session Replay）配额，必须在 GitOps 中配置异常触发采样策略，避免正常会话过早耗尽全天额度；同时，免费版不支持服务端二次脱敏，客户端遮罩代码成为合规的唯一防线。",
    "该方案适合注重终端交互体验、采用现代 SPA/SSR 架构、以及大量引入 AI 辅助编写前端组件的独立开发团队；对于纯内网运营后台、无复杂交互逻辑的静态单页、或者缺乏前端工程化脱敏能力的开发者，过早引入深度 RUM 会增加构建链复杂度，建议优先通过 Lighthouse 离线分析完成基础优化。"
]

A3_XHS_TITLE = "用户说卡，AI 写的页面哪里慢？"
A3_XHS_BODY = """最近很多独立开发者都在用 AI 疯狂刷前端页面，界面酷炫上线神速。但我刚把 UAT 跑起来就遭到了首批真实用户的集中吐槽：点登录按钮像卡死一样毫无反应，页面滚动也是疯狂掉帧！更离谱的是，我打开 GCP 控制台一看，后端 Cloud Run 的 CPU 占用率居然不到 4%，接口网络延迟才 38 毫秒！

后端监控一片大绿，为什么真实用户却在疯狂喊卡？
真相只有一个：AI 写的代码虽然业务逻辑能跑通，但在浏览器端堆了太多未经优化的响应式状态、复杂的富文本正则解析和冗余重渲染，把浏览器的单线程直接锁死了！传统的看服务器 CPU、看内存的运维手段，在前端真实体验面前完全就是个睁眼瞎！

我是怎么用纯代码化 RUM 把元凶给揪出来的？
P1：前端探针接入，但坚决不裸奔！在 GitOps 仓库把所有 input 输入框和敏感表单全加上 DOM 脱敏掩码，敏感数据坚决不出域，合规永远放在第一位！
P2：接入密钥由 Vault 动态注入，在 CI 构建时自动编译，彻底杜绝在网页控制台人肉配探针的低效行为。
P3：核心死磕 INP 交互延迟和 Long Task 长任务！探针数据一抓，直接揪出 AI 写的富文本组件在主线程跑了一个 280 毫秒的阻塞长任务！改成 Web Worker 异步解析并将渲染分片后，交互延迟秒降到 45ms！

总结：别等用户被卡跑了才想起来看前端真实体验！AI 写前端很爽，但必须配上 RUM 给它全方位把脉！想抄前端自动化脱敏配置的宝子，关注移步公众号！"""

A3_DECISION = [
    ("客户端体验捕获", "• <b>自建</b>：无开箱即用 RUM，需自建 Faro/Tempo 接收端<br>• <b>SaaS</b>：原生采集 LCP/INP/CLS 及浏览器 Long Task", "强烈建议将前端体验观测外包给 SaaS；一人开发切勿自建维护繁重的 RUM。"),
    ("会话重放 (Replay)", "• <b>自建</b>：自建存储与视频化重建开销极大、治理复杂<br>• <b>SaaS</b>：免费专区提供 2,000 次/天 会话重放额度", "仅在捕获到 5xx 错误或交互卡顿 > 500ms 时触发重放，避免快速耗尽配额。"),
    ("数据脱敏与隐私", "• <b>自建</b>：需自行编写客户端与服务端的日志清洗规则<br>• <b>SaaS</b>：免费专区不支持服务端脱敏，完全依赖客户端遮罩", "严防隐私越权：在前端 DOM 强制配置 data-guance-mask 与字段白名单。"),
    ("配额防爆仓控制", "• <b>自建</b>：直接写入本地存储，受单机磁盘容量限制<br>• <b>SaaS</b>：单日 5,000 PV 上限，突发超额立即停止接收", "在 CI 构建中注入基于路由的尾部采样率，对非关键页面实施 10% 降采样。"),
    ("排障定位耗时", "• <b>自建</b>：无法前后端关联，跨层排查需 2-4 小时<br>• <b>SaaS</b>：RUM 自动关联后端 TraceID，排查缩至 5 分钟", "极大降低单人运维心智负担，5 分钟内精准判定是前端重渲染还是后端慢查询。")
]

A3_CODE = [
    ("Frontend: 声明式客户端 RUM 初始化与脱敏配置 (src/observability/rum.ts)", "typescript",
"""import { datafluxRum } from '@cloudcare/browser-rum';

export function initRum(env: string) {
  datafluxRum.init({
    applicationId: import.meta.env.VITE_RUM_APP_ID,
    datakitOrigin: import.meta.env.VITE_RUM_ORIGIN,
    env: env,
    version: import.meta.env.VITE_APP_VERSION,
    service: 'xworkmate-frontend',
    sessionSampleRate: 100,
    sessionReplaySampleRate: 30, // Conserve 2000/day free replay budget
    trackInteractions: true,
    traceType: 'w3c_traceparent', // Propagate context to Cloudflare/Cloud Run
    allowedTracingOrigins: ['https://api.xworktech.com', 'https://uat-api.xworktech.com'],
    // ZERO SENSITIVE DATA LEAKAGE: Client-side DOM mask enforcement
    maskAllInputs: true,
    maskInputOptions: { password: true, text: true, email: true },
  });
}"""),
    ("CI Pipeline: 凭据隔离与生产编译构建 (ci/build-frontend.sh)", "bash",
"""#!/usr/bin/env bash
set -euo pipefail
# Injected via Vault during GitHub Actions Runner execution
export VITE_RUM_APP_ID=$(vault kv get -field=rum_app_id secret/data/observability/rum)
export VITE_RUM_ORIGIN="https://rum-gateway.xwork.tech"
export VITE_APP_VERSION=$(git rev-parse --short HEAD)

echo "[CI] Compiling React frontend with isolated RUM configuration..."
npm run build"""),
    ("GitOps: 声明式 RUM 采样与长任务告警规则 (gitops/rum-policy.yaml)", "yaml",
"""apiVersion: observability.xwork.tech/v1alpha1
kind: RumSamplingPolicy
metadata:
  name: uat-rum-guard
spec:
  environment: uat
  max_pv_daily: 4500 # Safe margin below 5000 PV quota
  sample_strategy:
    normal_route_sample_percentage: 10
    error_route_sample_percentage: 100
  long_task_threshold_ms: 100
  alert_condition:
    metric: inp_duration_seconds
    threshold: 0.200 # Alert if INP > 200ms""")
]

# Article 4
A4_PARAS = [
    "在多云架构已成标配的今天，个人 SaaS 的单次请求往往要经历复杂的跨网穿梭。以 XWorkTech 的 UAT 登录流程为例：用户的凭据首先经由 Cloudflare 边缘节点校验防刷规则，再转发至 Cloud Run 托管的微服务执行业务鉴权，最终调用 Supabase 数据库拉取用户角色。一次普通的登录失败，究竟是边缘网关超时、容器冷启动延时、还是数据库连接池枯竭？面对跨越三家不同云厂商的网络边界，传统的本地抓包或零散日志无法提供连贯的事实验证。只有基于统一协议将全链路的分布式 Trace 串接起来，才能看清每次请求的真实耗时分布。",
    "跨多云分布式追踪的基石是 W3C TraceContext 标准，即通过标准化的 traceparent 和 tracestate 请求头，在跨网络、跨运行时的 HTTP 调用间透明传递追踪上下文。当请求从 Cloudflare Workers 注入 trace ID 后，下游的 Cloud Run 容器必须无缝承接该上下文，并在向 Supabase 发起 PostgreSQL 连接时生成子 Span。这要求所有运行节点遵循严格的字段契约，包括 service.name、environment、http.route 以及统一的错误标识。然而多云环境下的网络异构性也带来了盲区：Supabase Free 版作为全托管黑盒服务，无法安装主机代理或注入探针，其内部耗时只能依托客户端 SDK 产生的外围 Span 进行推断。",
    "为实现稳定可靠的多云链路串联，本实战完全遵循“AI 辅助的 IaC / GitOps / Playbook”流水线进行声明式部署，分为四个纯代码化步骤。第一步，在 GitOps 仓库中声明 OTel 跨云转发规则，定义 TraceContext 提取与注入规范；第二步，通过 Terraform 管理 Cloud Run 部署清单，以环境变量形式注入 OTel Collector 地址与服务标识，严禁在控制台手工改动容器配置；第三步，利用 Ansible Playbook 自动化部署 OTel 汇聚管道，配置针对不同云端来源的速率限制与批处理策略；第四步，所有跨云调用的鉴权 Token 与工作空间密钥，一律在容器启动时由 Vault 注入运行时环境，确保跨云链路凭据全程隔离。",
    "经受控登录用例验证，系统成功捕获到一条横跨 Cloudflare、Cloud Run 与 Supabase 的完整分布式链路瀑布图。在一次模拟的 401 故障排查中，Trace 明确显示边缘耗时 12 毫秒，Cloud Run 处理耗时 25 毫秒，瓶颈点精准指向 Supabase 鉴权查询等待耗时达 410 毫秒，排障时间从原本的数小时缩短至 2 分钟以内。其局限性在于，免费专区单日 2 万条 Trace 的额度对全量跟踪并不宽裕，必须在 OTel Collector 端基于路由配置精准尾部采样策略；同时由于免费版不支持跨空间 OpenAPI 数据导出，链路分析仅能在单工作空间内闭环。",
    "该方案极其适合采用现代化分布式多云、Serverless 微服务与第三方 BaaS 混合架构的独立开发者和初创技术团队；对于仅运行在单台 VPS 上的单体架构应用、或者完全不涉及跨网络调用的本地离线系统，引入分布式链路追踪会徒增系统复杂性与网络开销，采用集中式结构化日志即可满足日常排障需求。"
]

A4_XHS_TITLE = "一个登录请求到底去了哪里？"
A4_XHS_BODY = """现代个人 SaaS 最酷也是最让人抓狂的架构，就是多云混部：Cloudflare Pages/Workers 跑边缘、Cloud Run 托管核心后端微服务、Supabase 接管数据库与鉴权！这套架构虽然轻盈省钱，可一旦用户登录报错 401，你根本不知道究竟是 Cloudflare 规则抽风、Cloud Run 冷启动卡顿、还是 Supabase 连接池被打爆了！

怎么用分布式 Trace 把三朵云连成一根线？保姆级实操步骤直接公开：

P1：统一信使标准。基于 W3C TraceContext 国际标准协议，让请求从 Cloudflare 出来时就带上 traceparent 请求头，下游 Cloud Run 自动继承提取，坚决不让链路在网络边界断头！
P2：纯代码化编排。别去控制台手动配探针！用 Terraform 把 OTel Collector 地址作为环境变量声明式写进 Cloud Run 配置，用 Ansible Playbook 一键拉起收集器和转发管道，杜绝任何手工点击！
P3：跨云凭据全进 Vault。三朵云之间的调用鉴权密钥与工作空间 Token，统一由 Vault 在容器启动时动态注入，Git仓库里只留纯净模板，坚决不留哪怕半个明文密码！

实战复盘体验极其丝滑：一条登录请求穿过三朵云，瀑布图展开一目了然：边缘 12ms、容器 25ms、数据库查表 410ms！故障点精准定位到数据库连接延迟，排障从 2 小时直接缩至 2 分钟！

总结：分布式架构虽好，没有 Trace 就是开盲盒。用代码化搞定全链路追踪，多云也能看得清清楚楚！想拿跨云 OTel 编排模板的宝子，移步公众号自取！"""

A4_DECISION = [
    ("分布式追踪协议", "• <b>自建</b>：支持 Jaeger/OTel，跨多云网络传输需自建路由<br>• <b>SaaS</b>：原生遵循 W3C TraceContext 标准透传上下文", "全链路强制统一至标准 traceparent 协议头，严禁使用私有魔改追踪格式。"),
    ("多云覆盖与黑盒", "• <b>自建</b>：需为每个云厂商部署独立 Collector，维护繁琐<br>• <b>SaaS</b>：覆盖 Cloudflare + Cloud Run，Supabase 为黑盒", "明确标注 BaaS 黑盒边界：在客户端封装代理 Span，避免链路出现未覆盖盲区。"),
    ("Trace 每日配额", "• <b>自建</b>：受自建存储与 IOPS 限制，需定期清理索引<br>• <b>SaaS</b>：免费专区限 20,000 条 Trace/天，超额熔断停收", "Collector 开启智能尾部采样：错误 Span 100% 采集，成功请求按 5% 抽样。"),
    ("排障归因时效", "• <b>自建</b>：需人工按时间戳在多个系统比对日志，需 1-2 小时<br>• <b>SaaS</b>：单请求完整瀑布图展开，瓶颈定位耗时 < 2 分钟", "用端到端瀑布图直接锁定是边缘鉴权失败还是容器冷启动，消除跨云推诿。"),
    ("凭据与传输安全", "• <b>自建</b>：跨云之间若手工配置静态 Token，外泄风险极高<br>• <b>SaaS</b>：支持通过 Vault 动态注入 Header 密钥与凭据隔离", "全量代码化托管凭据，运行时通过 Vault 注入，严禁在 Web 控制台手工填入。")
]

A4_CODE = [
    ("Cloudflare Workers: W3C TraceContext 上下文注入 (workers/src/tracer.ts)", "typescript",
"""export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const traceId = crypto.randomUUID().replace(/-/g, '');
    const spanId = crypto.randomUUID().replace(/-/g, '').substring(0, 16);
    const traceparent = `00-${traceId}-${spanId}-01`;

    const modifiedHeaders = new Headers(request.headers);
    modifiedHeaders.set('traceparent', traceparent);
    modifiedHeaders.set('x-origin-edge', 'cloudflare-global');

    const response = await fetch('https://api.xworktech.com/auth/login', {
      method: request.method,
      headers: modifiedHeaders,
      body: request.body,
    });
    return response;
  }
};"""),
    ("Terraform: Cloud Run 容器声明式注入 OTel 环境变量 (terraform/cloud_run.tf)", "hcl",
"""resource "google_cloud_run_service" "auth_service" {
  name     = "xworkmate-auth-service"
  location = "asia-east1"

  template {
    spec {
      containers {
        image = "gcr.io/xworktech-uat/auth:v1.4.2"
        env {
          name  = "OTEL_EXPORTER_OTLP_ENDPOINT"
          value = "http://otel-collector.internal.xwork.tech:4318"
        }
        env {
          name  = "OTEL_SERVICE_NAME"
          value = "auth-service"
        }
        env {
          name  = "OTEL_PROPAGATORS"
          value = "tracecontext,baggage"
        }
      }
    }
  }
}"""),
    ("OTel Collector: 汇聚管道与尾部采样配置 (otel/collector-config.yaml)", "yaml",
"""receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 2s
    send_batch_size: 256
  tail_sampling:
    decision_wait: 5s
    expected_new_traces_per_sec: 100
    policies:
      - name: drop_status_200_excess
        type: probabilistic
        probabilistic: { sampling_percentage: 5.0 }
      - name: keep_all_errors
        type: status_code
        status_code: { status_codes: [ ERROR ] }

exporters:
  otlp/guance:
    endpoint: "https://openway.guance.com:4317"
    headers:
      "X-Token": "${VAULT_GUANCE_TOKEN}"

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [tail_sampling, batch]
      exporters: [otlp/guance]""")
]

# Build execution
def build_all():
    print("[1/6] Generating Master Plan PDF...")
    plan_html = generate_plan_html()
    plan_html_path = os.path.join(PDF_DIR, "00_plan.html")
    plan_pdf_path = os.path.join(PDF_DIR, "00_独立开发观察者计划_首季完整策划方案.pdf")
    with open(plan_html_path, "w", encoding="utf-8") as f:
        f.write(plan_html)
    subprocess.run([CHROME, "--headless", "--no-pdf-header-footer", f"--print-to-pdf={plan_pdf_path}", plan_html_path], check=True)
    print(f"  -> Generated: {plan_pdf_path}")

    articles_data = [
        (1, "我的个人 SaaS 已经够便宜了，还能用什么补上监控？",
         "Cloudflare + Cloud Run + Supabase 栈下的可观测 SaaS 选型与代码化接入",
         {"knowledge": "免费额度与服务选型", "template": "对比选型型", "case": "XWorkTech UAT 多云环境观测接入", "date": "2026-10-27 (已核验)"},
         A1_PARAS, A1_DECISION,
         [("个人 SaaS 多云拓扑与观测注入点", get_a1_svg1()),
          ("GitOps + IaC + Playbook + Vault 交付流水线", get_a1_svg2()),
          ("指标白名单过滤与配额防溢出缓冲架构", get_a1_svg3()),
          ("自建底座与 SaaS 托管服务能力划分拓扑", get_a1_svg4())],
         {"title": A1_XHS_TITLE, "body": A1_XHS_BODY}, A1_CODE,
         "01_免费额度与服务选型_图文草稿.pdf", "01-free-tier-for-indie-saas"),
        
        (2, "AI 帮我搬 Grafana 面板：先让数字对上，再决定切换",
         "从自建 VictoriaMetrics 到可观测 SaaS：语义对账、双写并跑与 15 分钟回退",
         {"knowledge": "面板语义对账与指标兼容", "template": "误区纠偏型", "case": "资源/流量/k6 压测三大核心面板平迁", "date": "2026-10-27 (已核验)"},
         A2_PARAS, A2_DECISION,
         [("Grafana JSON AST 解析与 HCL 转换流水线", get_a2_svg1()),
          ("双写并跑与 15 分钟熔断回退拓扑", get_a2_svg2()),
          ("PromQL 语义对账与指标差异收敛矩阵", get_a2_svg3()),
          ("监控状态机：从验证、双写到平滑切流状态转移图", get_a2_svg4())],
         {"title": A2_XHS_TITLE, "body": A2_XHS_BODY}, A2_CODE,
         "02_面板语义对账与平滑迁移_图文草稿.pdf", "02-observability-migration-with-rollback"),

        (3, "AI 生成的页面上线后变卡，我先看用户体验而不是 CPU",
         "UAT 页面卡顿的浏览器侧根因定位：Core Web Vitals、长任务与代码化脱敏",
         {"knowledge": "真实用户体验与前端 RUM 分析", "template": "故障复盘型", "case": "AI 生成高交互页面卡顿与 Long Task 排查", "date": "2026-10-27 (已核验)"},
         A3_PARAS, A3_DECISION,
         [("现代 Web 前端性能瓶颈与 Core Web Vitals 采集流", get_a3_svg1()),
          ("代码化客户端脱敏与 DOM 掩码过滤管线", get_a3_svg2()),
          ("前端长任务（Long Task）与后端 API 瀑布流关联剖析", get_a3_svg3()),
          ("客户端 RUM 会话与分布式 Trace 关联打通机制", get_a3_svg4())],
         {"title": A3_XHS_TITLE, "body": A3_XHS_BODY}, A3_CODE,
         "03_前端真实体验与RUM分析_图文草稿.pdf", "03-real-user-experience-rum"),

        (4, "一个登录请求经过几朵云？用 Trace 把它接起来",
         "Cloudflare → Cloud Run → Supabase 跨云分布式链路上下文传播与 OTel 实践",
         {"knowledge": "分布式上下文传播与跨云追踪", "template": "动手实操型", "case": "跨三朵云单次鉴权失败链路定位", "date": "2026-10-27 (已核验)"},
         A4_PARAS, A4_DECISION,
         [("W3C TraceContext 跨多云边界上下文传递全貌", get_a4_svg1()),
          ("OTel Collector 多云汇聚与动态路由管道", get_a4_svg2()),
          ("登录链路 Span 拓扑与延时耗时瀑布图", get_a4_svg3()),
          ("多云边界安全鉴权与凭据动态注入架构", get_a4_svg4())],
         {"title": A4_XHS_TITLE, "body": A4_XHS_BODY}, A4_CODE,
         "04_跨多云链路上下文追踪_图文草稿.pdf", "04-cross-cloud-distributed-tracing")
    ]

    combined_html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>独立开发观察者计划：首季前4篇图文草稿合辑</title>
<style>
{PRINT_CSS}
</style>
</head>
<body>
<div style="text-align: center; padding: 40px 0 60px 0; border-bottom: 2px solid #2563eb;">
    <div class="series-tag">INDIE HACKER OBSERVABILITY OBSERVATION PROGRAM · MASTER COMPILATION</div>
    <h1 style="font-size: 26pt; margin: 16px 0;">首季核心前 4 篇图文草稿全集</h1>
    <div style="font-size: 13pt; color: #475569;">微信公众号 InfoQ 实战特稿 + 小红书种草笔记 + 纯技术架构图册 + 全代码化交付清单</div>
</div>
<div class="page-break"></div>
"""

    for art_no, title, subtitle, meta, paras, decision, svgs, xhs, code, pdf_name, folder_name in articles_data:
        print(f"[{art_no + 1}/6] Generating Article {art_no:02d} PDF: {title[:20]}...")
        art_html = render_article_page(art_no, title, subtitle, meta, paras, decision, svgs, xhs, code)
        art_html_path = os.path.join(PDF_DIR, f"{art_no:02d}_article.html")
        art_pdf_path = os.path.join(PDF_DIR, pdf_name)
        
        with open(art_html_path, "w", encoding="utf-8") as f:
            f.write(art_html)
            
        subprocess.run([CHROME, "--headless", "--no-pdf-header-footer", f"--print-to-pdf={art_pdf_path}", art_html_path], check=True)
        print(f"  -> Generated: {art_pdf_path}")
        
        # Save markdown draft into corresponding article folder
        art_md_path = os.path.join(ARTICLES_DIR, folder_name, "article_draft.md")
        with open(art_md_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n## {subtitle}\n\n### 微信公众号全文（严格 ≤1500 字，5段落）\n\n")
            for p in paras:
                f.write(f"{p}\n\n")
            f.write("### 小红书图文笔记（严格 600-800 字）\n\n")
            f.write(f"**{xhs['title']}**\n\n{xhs['body']}\n\n")
            f.write("### 代码化资产范式\n\n")
            for c_title, c_lang, c_code in code:
                f.write(f"#### {c_title}\n```{c_lang}\n{c_code}\n```\n\n")
        print(f"  -> Markdown draft saved to: {art_md_path}")
        
        # Append to combined HTML
        combined_html_content += f"""<div style="margin-top: 20px;">
        {art_html.replace('<!DOCTYPE html>', '').replace('<html lang="zh-CN">', '').replace('</html>', '').replace('<head>', '').replace('</head>', '').replace('<body>', '').replace('</body>', '').replace(f'<style>{PRINT_CSS}</style>', '')}
        </div>
        <div class="page-break"></div>"""

    combined_html_content += "</body></html>"
    combined_html_path = os.path.join(PDF_DIR, "combined_articles.html")
    combined_pdf_path = os.path.join(PDF_DIR, "首季前4篇图文草稿_合辑.pdf")
    with open(combined_html_path, "w", encoding="utf-8") as f:
        f.write(combined_html_content)
    subprocess.run([CHROME, "--headless", "--no-pdf-header-footer", f"--print-to-pdf={combined_pdf_path}", combined_html_path], check=True)
    print(f"[6/6] -> Generated Combined Master PDF: {combined_pdf_path}")

if __name__ == '__main__':
    build_all()
    print("\n[SUCCESS] All 6 PDFs, HTMLs, and Markdown drafts successfully compiled!")
