import subprocess
import os
import shutil

ASSETS_DIR = "/Users/shenlan/workspaces/ai-workspace-service/knowledge/assets/images"
DESKTOP_DIR = "/Users/shenlan/Desktop/AI团队协作Bento海报"
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(DESKTOP_DIR, exist_ok=True)

SHARED_CSS = """
  :root {
    --bg: #f3f2ed;
    --ink: #19231f;
    --muted: #65716a;
    --line: #dce1d9;
    --green: #c7f068;
    --dark: #172c25;
    --orange: #ffba75;
    --peach: #ffead4;
    --mint: #e6ece5;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 896px;
    height: 1024px;
    background: var(--bg);
    color: var(--ink);
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Segoe UI", Roboto, sans-serif;
    padding: 24px 32px;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  header {
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(0,0,0,0.06);
    padding-bottom: 8px;
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 800;
    font-size: 16px;
    color: var(--ink);
  }
  .logo {
    background: var(--dark);
    color: var(--green);
    width: 32px;
    height: 32px;
    border-radius: 9px;
    display: grid;
    place-items: center;
    font-size: 18px;
    font-weight: 800;
  }
  nav {
    display: flex;
    align-items: center;
    gap: 18px;
    font-size: 12.5px;
    font-weight: 600;
    color: var(--muted);
  }
  .nav-pill {
    background: #e5e9e2;
    padding: 3px 9px;
    border-radius: 999px;
    color: var(--dark);
    font-weight: 700;
  }
  .hero {
    padding: 12px 0 16px;
    display: grid;
    grid-template-columns: 1.45fr 1fr;
    gap: 20px;
    align-items: end;
  }
  .eyebrow {
    font-size: 11px;
    letter-spacing: 2px;
    font-weight: 800;
    color: var(--muted);
    text-transform: uppercase;
  }
  h1 {
    font-size: 38px;
    line-height: 1.15;
    letter-spacing: -1.5px;
    margin: 8px 0 0;
    font-weight: 900;
    color: var(--dark);
    white-space: nowrap;
  }
  h1 span {
    color: #55893b;
  }
  .hero p {
    font-size: 13px;
    line-height: 1.6;
    color: var(--muted);
    margin-bottom: 12px;
  }
  .actions {
    display: flex;
    gap: 8px;
  }
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 8px 14px;
    border-radius: 8px;
    background: var(--dark);
    color: white;
    font-size: 12px;
    font-weight: 700;
    border: none;
    text-decoration: none;
  }
  .btn.secondary {
    background: white;
    color: var(--ink);
    border: 1px solid var(--line);
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 12px;
    flex: 1;
    margin-bottom: 4px;
  }
  .card {
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 16px;
    overflow: hidden;
    position: relative;
  }
  .label {
    font-size: 10.5px;
    letter-spacing: 1px;
    font-weight: 800;
    color: var(--muted);
    text-transform: uppercase;
  }
  .flow {
    grid-column: span 8;
    background: var(--dark);
    color: #fff;
    border: none;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .flow:after {
    content: "";
    position: absolute;
    right: -40px;
    top: -70px;
    width: 200px;
    height: 200px;
    border: 1px solid #ffffff15;
    border-radius: 50%;
    pointer-events: none;
  }
  .flow .label { color: #aec2b7; }
  .flow h2 {
    font-size: 19px;
    letter-spacing: -0.5px;
    margin: 6px 0 10px;
    font-weight: 850;
  }
  .flow-row {
    display: flex;
    align-items: center;
    gap: 6px;
    margin: 8px 0;
    position: relative;
    z-index: 1;
  }
  .node {
    border: 1px solid #537365;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 11.5px;
    text-align: center;
    font-weight: 700;
    background: rgba(255,255,255,0.04);
  }
  .node.primary {
    background: var(--green);
    color: var(--dark);
    border-color: var(--green);
  }
  .connector {
    height: 2px;
    background: #52705f;
    flex: 1;
    min-width: 10px;
    position: relative;
  }
  .branches {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .branch {
    border: 1px solid #3c584b;
    border-radius: 10px;
    padding: 8px 10px;
    background: rgba(0,0,0,0.15);
  }
  .branch strong {
    display: block;
    font-size: 12.5px;
    margin-bottom: 2px;
  }
  .branch small {
    color: #aec2b7;
    line-height: 1.4;
    font-size: 10.5px;
  }
  .footnote {
    font-size: 10.5px;
    color: #aec2b7;
    margin-top: 8px;
  }
  .numbers {
    grid-column: span 4;
    background: var(--green);
    border: none;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 16px;
  }
  .numbers .label { color: #436024; }
  .stat-main {
    font-size: 62px;
    font-weight: 900;
    letter-spacing: -3px;
    line-height: 1.0;
    color: #172c25;
    margin: 8px 0;
  }
  .stat-main small {
    font-size: 14px;
    letter-spacing: 0;
    margin-left: 6px;
    font-weight: 700;
  }
  .stat-sub {
    font-size: 11.5px;
    color: #37531d;
    font-weight: 600;
    line-height: 1.4;
  }
  .stats {
    display: flex;
    gap: 16px;
    padding-top: 10px;
    border-top: 1px solid #9abb56;
  }
  .stats strong {
    font-size: 20px;
    display: block;
    color: #172c25;
    font-weight: 850;
  }
  .stats span {
    font-size: 10.5px;
    color: #436024;
    font-weight: 600;
  }
  .source {
    grid-column: span 4;
    min-height: 130px;
    padding: 14px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .source-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .icon {
    width: 28px;
    height: 28px;
    border-radius: 7px;
    display: grid;
    place-items: center;
    background: #f0f3ed;
    font-weight: 800;
    font-size: 13px;
  }
  .badge {
    font-size: 10.5px;
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 2px 7px;
    color: #567447;
    font-weight: 700;
    background: #fff;
  }
  .source h3 {
    font-size: 15px;
    margin: 8px 0 4px;
    font-weight: 850;
    color: var(--dark);
  }
  .source p {
    font-size: 11px;
    color: var(--muted);
    line-height: 1.45;
  }
  .source .tags {
    display: flex;
    gap: 4px;
    margin-top: 8px;
    flex-wrap: wrap;
  }
  .tag {
    font-size: 10px;
    padding: 3px 6px;
    border-radius: 4px;
    background: #f3f4ef;
    font-weight: 600;
    color: #374151;
  }
  .workspace {
    grid-column: span 8;
    background: var(--mint);
    border: 1px solid #cbd5c9;
    padding: 16px;
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 14px;
  }
  .workspace .label { color: #52635a; }
  .workspace h2 {
    font-size: 18px;
    margin: 4px 0 6px;
    font-weight: 850;
    color: #172c25;
  }
  .workspace p {
    font-size: 11px;
    color: var(--muted);
    line-height: 1.45;
  }
  .endpoint {
    font-size: 10.5px;
    display: block;
    padding: 6px 8px;
    border-radius: 6px;
    background: #fff;
    border: 1px solid #cbd5c9;
    margin: 8px 0;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    color: #1e3a8a;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .ui-mockup {
    background: #ffffff;
    border: 1px solid #c0ccc0;
    border-radius: 10px;
    padding: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-size: 11px;
  }
  .mockup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #eef2ed;
    padding-bottom: 5px;
    font-weight: 700;
    color: #374151;
  }
  .mockup-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 6px;
    border-radius: 6px;
    background: #f9faf8;
    border: 1px solid #eef2ee;
  }
  .mockup-item.active {
    background: #172c25;
    color: #fff;
    border-color: #172c25;
  }
  .mockup-pill {
    font-size: 9.5px;
    padding: 2px 5px;
    border-radius: 4px;
    font-weight: 700;
  }
  .mockup-pill.lime {
    background: var(--green);
    color: var(--dark);
  }
  .mockup-pill.gray {
    background: #e5e7eb;
    color: #374151;
  }
  .security {
    grid-column: span 4;
    background: var(--peach);
    border: 1px solid #f6d0af;
    padding: 16px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .security .label { color: #8a653d; }
  .security h2 {
    font-size: 18px;
    margin: 4px 0 6px;
    font-weight: 850;
    color: #432818;
    line-height: 1.2;
  }
  .security ul {
    padding-left: 14px;
    font-size: 11px;
    line-height: 1.8;
    color: #432818;
    font-weight: 600;
  }
  .security .rule-box {
    font-size: 10px;
    color: #78350f;
    background: rgba(255,255,255,0.6);
    padding: 6px 8px;
    border-radius: 6px;
    border: 1px dashed #f59e0b;
    font-weight: 700;
    margin-top: 6px;
  }
  footer {
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 11px;
    color: var(--muted);
    border-top: 1px solid rgba(0,0,0,0.06);
    padding-top: 6px;
  }
"""

POSTERS = [
    {
        "id": "01",
        "fname": "ai-team-bento-01-routing",
        "title_cn": "AI团队协作 · 01 团队建制篇",
        "brand": "AI Team Architecture",
        "navs": ["角色建制", "模型路由", "GitHub ↗"],
        "eyebrow": "FROM MODEL SELECTION TO MODEL ROUTING",
        "h1": "别选模型了。<br>设计团队。<br><span>按责路由。</span>",
        "sub": "不要再寻找“一个最强模型解决所有问题”，而是让不同模型承担不同职责。从 Model Selection 走向 Model Routing。",
        "btn_main": "角色体系规范 ↓",
        "btn_sec": "路由矩阵 ↗",
        
        "c1_label": "01 / ROLE DEFINITIONS & TOPOLOGY",
        "c1_title": "六大角色清晰分工，各司其职。",
        "c1_nodes": [("Prompt", False), ("Chat (控制面)", False), ("Router", True), ("AI Team", False)],
        "c1_b1_title": "执行主力 (Worker / Engineer)",
        "c1_b1_desc": "极速吞吐 · 代码交付 · 单测编写<br>Luna / Sol / Sonnet / Flash",
        "c1_b2_title": "裁决与溯源 (Architect / Researcher)",
        "c1_b2_desc": "全局架构 · 证据链 · 根因归因<br>Astra / Opus / Deep Think",
        "c1_foot": "严禁越权：低阶模型不涉架构裁决，顶配模型不写机械脚本。",
        
        "c2_label": "02 / THE ROUTING ENGINE",
        "c2_stat": "6",
        "c2_stat_unit": "大协作角色",
        "c2_sub": "已有全链路模型分流与自动升舱契约",
        "c2_s1_v": "1",
        "c2_s1_l": "统一 HTTPS 入口",
        "c2_s2_v": "3",
        "c2_s2_l": "次失败自动升舱",
        
        "c3_badge": "4 大商业旗舰",
        "c3_title": "顶峰算力压阵",
        "c3_desc": "OpenAI · Anthropic · Google · xAI，覆盖从快速 Worker 到顶配 Architect 全梯队。",
        "c3_tags": ["Astra", "Opus 5.5", "Argon", "Grok 4.7"],
        
        "c4_badge": "9 大开源中坚",
        "c4_title": "本地与专网基建",
        "c4_desc": "DeepSeek · Kimi · GLM · Qwen · Gemma 等开源模型，低成本吞吐与隐私隔离。",
        "c4_tags": ["MIT 自由", "Apache 2.0", "16GB Mac 本地"],
        
        "c5_badge": "阶梯式算力策略",
        "c5_title": "80/15/5 黄金比例",
        "c5_desc": "80% 任务交由 Worker/Engineer，15% 做溯源调研，仅 5% 难点动用顶配 Architect。",
        "c5_tags": ["降本 80%", "吞吐翻倍", "零死循环"],
        
        "c6_label": "03 / AGENT WORKSPACE SELECTOR",
        "c6_title": "在开发环境，<br>无缝调度多角色。",
        "c6_desc": "统一网关下发角色别名。CLI、IDE 与自动化流水线共享相同角色路由规则。",
        "c6_endpoint": "https://ai.svc.plus/v1/chat/completions",
        "c6_mockup_head": ("🎯 模型工作台", "角色映射模式"),
        "c6_mockup_items": [
            ("worker-batch (GPT-6 Luna)", "极速", "gray"),
            ("engineer-senior (Sonnet 5.5)", "交付", "gray"),
            ("architect-judge (GPT-6 Astra)", "裁决", "lime", True),
            ("researcher-deep (Deep Think)", "溯源", "gray"),
        ],
        
        "c7_label": "04 / ESCALATION CONTRACT",
        "c7_title": "遇到死循环。<br>自动升舱契约。",
        "c7_items": [
            "Worker 失败 2 次 ➔ 升级 Engineer 介入",
            "Engineer 陷入局部最优 ➔ Architect 裁决",
            "涉及合规与敏感数据 ➔ 强制本地开源专网",
            "最终生产发布 ➔ 人类终审审批",
        ],
        "c7_rule": "AI 负责探索与交付 · 人类负责目标与担责",
        "foot_left": "AI Collaboration System · 01 团队建制与角色路由全景",
        "foot_right": "2026 虚拟工程团队架构规范 ↗",
    },
    {
        "id": "02",
        "fname": "ai-team-bento-02-workhorse",
        "title_cn": "AI团队协作 · 02 工程主力篇",
        "brand": "Engineering Workhorse",
        "navs": ["次旗舰革命", "验证闭环", "Harness"],
        "eyebrow": "THE WORKHORSE REVOLUTION & HARNESS",
        "h1": "主力不是最强。<br>是性价比之王。<br><span>验证闭环。</span>",
        "sub": "真正扛起日常 80% 开发的不是顶配 Astra / Opus，而是 1/5 成本的次旗舰。代码不是模型写出来的，是 Harness 跑出来的。",
        "btn_main": "主力梯队 ↗",
        "btn_sec": "验证体系 ↓",
        
        "c1_label": "01 / THE 1/5 COST FORMULA",
        "c1_title": "以 20% 成本，提供近顶级推理能力。",
        "c1_nodes": [("Task Spec", False), ("Harness Runtime", False), ("Sub-Flagship", True), ("Verification", False)],
        "c1_b1_title": "GPT-6.1 Sol / Sonnet 5.5",
        "c1_b1_desc": "接近 Astra 85-90% 性能，Token 仅 1/5<br>日常编码、Feature 交付、单元测试",
        "c1_b2_title": "Grok 4.7 / DeepSeek V4-Pro",
        "c1_b2_desc": "超长上下文代码生成，开源高吞吐<br>极低边际成本与私有集群推理",
        "c1_foot": "公式：交付质量 = 模型能力 (40%) × Harness 适配 (30%) × 工具链验证 (30%)",
        
        "c2_label": "02 / WORKLOAD SPLIT",
        "c2_stat": "80%",
        "c2_stat_unit": "日常工程负载",
        "c2_sub": "由次旗舰模型独立高质闭环交付",
        "c2_s1_v": "1/5",
        "c2_s1_l": "顶配 Token 成本",
        "c2_s2_v": "100%",
        "c2_s2_l": "确定性工具验证",
        
        "c3_badge": "Harness 决定上限",
        "c3_title": "环境承载上下文",
        "c3_desc": "Agent Runtime + LSP + File System + Bash 执行环境，提供丰富上下文支撑。",
        "c3_tags": ["LSP 补全", "AST 解析", "符号跳转"],
        
        "c4_badge": "长任务防漂移",
        "c4_title": "状态机与断点续传",
        "c4_desc": "长任务拆分为离散 Step，每步输出持久化到磁盘与 Git，随时可回滚可恢复。",
        "c4_tags": ["Git 快照", "任务断点", "防死循环"],
        
        "c5_badge": "交叉 Review 机制",
        "c5_title": "双模型互审盲区",
        "c5_desc": "Codex 编写的代码由 Claude Code 审阅，杜绝单一模型向自身偏见妥协。",
        "c5_tags": ["多视角", "边界校验", "零妥协"],
        
        "c6_label": "03 / DETERMINISTIC RUNTIME",
        "c6_title": "不信模型直觉，<br>只信测试通过。",
        "c6_desc": "让模型处于严格闭环流水线中：生成代码 ➔ 编译 ➔ 执行单元测试 ➔ 自动修复。",
        "c6_endpoint": "harness: cargo test --all && golangci-lint run",
        "c6_mockup_head": ("🧪 自动化验证终端", "PASS 100%"),
        "c6_mockup_items": [
            ("cargo test --workspace", "PASS 48/48", "lime"),
            ("golangci-lint run", "0 issues", "lime"),
            ("model: gpt-6.1-sol (Thinking)", "Cost: $0.003", "gray"),
            ("cross-review: sonnet-5.5", "Approved", "gray"),
        ],
        
        "c7_label": "04 / VERIFICATION PROTOCOL",
        "c7_title": "确定性工具。<br>胜于概率推演。",
        "c7_items": [
            "编译器与 Linter 先行拦截语法问题",
            "单元测试与端到端用例自动化回放",
            "双模型交叉 Review 发现安全隐患",
            "严禁模型自己向自己妥协",
        ],
        "c7_rule": "无自动化验证通过 · 绝不合并主干代码",
        "foot_left": "AI Collaboration System · 02 工程主力与闭环验证规范",
        "foot_right": "次旗舰革命与 Harness 架构 ↗",
    },
    {
        "id": "03",
        "fname": "ai-team-bento-03-judge",
        "title_cn": "AI团队协作 · 03 顶配裁决篇",
        "brand": "Top-Tier Strategy",
        "navs": ["裁判机制", "根因诊断", "A/B裁决"],
        "eyebrow": "TOP-TIER AS JUDGE & DEEP REASONING",
        "h1": "顶配不改 YAML。<br>顶配做裁决。<br><span>定位根因。</span>",
        "sub": "不要让 Astra / Opus 5.5 写普通脚本。把最贵的算力留给架构设计、长链条根因诊断与方案 A/B 裁决。",
        "btn_main": "裁判工作流 ↓",
        "btn_sec": "根因诊断 ↗",
        
        "c1_label": "01 / PARALLEL PoC JUDGE FLOW",
        "c1_title": "主力做实现，顶配做裁决。",
        "c1_nodes": [("PoC A / B", False), ("Repo Audit", False), ("Judge Astra", True), ("Human Sign", False)],
        "c1_b1_title": "并行方案探索 (PoC A vs B)",
        "c1_b1_desc": "Sonnet 5.5 生成方案 A (简洁轻量)<br>GPT-6.1 Sol 生成方案 B (高并发连接池)",
        "c1_b2_title": "顶配交叉裁决 (Judge Review)",
        "c1_b2_desc": "Flash 扫描全库找兼容风险<br>Astra / Opus 评估 Trade-off 输出仲裁",
        "c1_foot": "模型成本花在判断力上，而不是机械敲代码上。",
        
        "c2_label": "02 / DECISION LEVERAGE",
        "c2_stat": "10x",
        "c2_stat_unit": "关键决策杠杆",
        "c2_sub": "在系统重构与死锁诊断中发挥终极价值",
        "c2_s1_v": "5%",
        "c2_s1_l": "算力消费占比",
        "c2_s2_v": "4",
        "c2_s2_l": "大顶峰裁决模型",
        
        "c3_badge": "长周期故障定位",
        "c3_title": "树状根因归因",
        "c3_desc": "针对运行数天后的延迟爬升与内存泄漏，构建多维排查树，给出安全验证步骤。",
        "c3_tags": ["FD 泄漏", "GC 停顿", "TCP 状态"],
        
        "c4_badge": "跨区域系统设计",
        "c4_title": "全局容灾架构",
        "c4_desc": "四区域 BGP Anycast、WireGuard 隧道、双活 PostgreSQL 与 Vault 凭据容灾。",
        "c4_tags": ["SLA 99.99%", "零单点故障", "合规边界"],
        
        "c5_badge": "安全与合规审计",
        "c5_title": "零信任准入防线",
        "c5_desc": "审查跨账号隔离策略、OAuth 刷新生命周期与 Vault AppRole 最小权限模型。",
        "c5_tags": ["0700 权限", "Tmpfs 注入", "抗审查"],
        
        "c6_label": "03 / ARCHITECTURAL REVIEW UI",
        "c6_title": "多方案权衡对比，<br>数据说话。",
        "c6_desc": "顶级模型输出详细 Trade-off 评估报告：成本、复杂度、延迟与维护性矩阵。",
        "c6_endpoint": "judge: architecture-tradeoff-matrix.json",
        "c6_mockup_head": ("⚖️ 方案 A/B 裁决面板", "Max Reasoning"),
        "c6_mockup_items": [
            ("方案 A: 架构优雅 · 延迟 12ms", "评分 9/10", "gray"),
            ("方案 B: 高并发优化 · 复杂度高", "评分 8/10", "gray"),
            ("仲裁: 采纳方案 A 骨架 + B 连接池", "裁决通过", "lime", True),
            ("审定人: gpt-6-astra / opus-5.5", "Verified", "lime"),
        ],
        
        "c7_label": "04 / ZERO TOLERANCE BOUNDARY",
        "c7_title": "错一次代价极大。<br>顶配压阵。",
        "c7_items": [
            "核心资金流与数据账本逻辑改造",
            "全球骨干网络拓扑与 BGP 宣告设计",
            "严苛安全准入与 Vault 凭据加密机",
            "终极方案交由人类架构师审批归档",
        ],
        "c7_rule": "将判断力置于机械敲键盘之上",
        "foot_left": "AI Collaboration System · 03 顶配裁决与深度推理策略",
        "foot_right": "顶级模型应用边界规范 ↗",
    },
    {
        "id": "04",
        "fname": "ai-team-bento-04-hybrid-open",
        "title_cn": "AI团队协作 · 04 混合网关篇",
        "brand": "Hybrid AI Gateway",
        "navs": ["商业与开源", "许可证合规", "隐私隔离"],
        "eyebrow": "HYBRID GATEWAY & 13-MODEL ARRAY",
        "h1": "商业做裁决。<br>开源做基建。<br><span>合规不出域。</span>",
        "sub": "四大商业顶峰 + 九大开源中坚。用单一 HTTPS 聚合网关统一收敛，兼顾极致前沿与完全自主掌控。",
        "btn_main": "模型阵列 ↓",
        "btn_sec": "开源许可证 ↗",
        
        "c1_label": "01 / UNIFIED TRAFFIC HUB",
        "c1_title": "双层分流架构，单入口收敛。",
        "c1_nodes": [("Clients", False), ("Caddy TLS", False), ("New API", True), ("13 Models", False)],
        "c1_b1_title": "商业旗舰 (OpenAI / Anthropic / Google)",
        "c1_b1_desc": "承载最高难度推理与架构规划<br>交叉审查、复杂决策与前沿探索",
        "c1_b2_title": "开源中坚 (DeepSeek / Qwen / Gemma)",
        "c1_b2_desc": "本地离线计算、大吞吐批处理<br>敏感数据不出域与低边际成本",
        "c1_foot": "网关校验客户端 Token · 内部动态轮换 Provider Key · 凭据绝不落地。",
        
        "c2_label": "02 / FULL SPECTRUM ARRAY",
        "c2_stat": "13",
        "c2_stat_unit": "款主力模型",
        "c2_sub": "4 大商业旗舰 + 9 大开源中坚统一收敛",
        "c2_s1_v": "1",
        "c2_s1_l": "统一 HTTPS 网关",
        "c2_s2_v": "0",
        "c2_s2_l": "凭据泄露风险",
        
        "c3_badge": "MIT 极度自由",
        "c3_title": "DeepSeek V3 / V4",
        "c3_desc": "允许任意商业使用与闭源集成，无需开源衍生代码，全球顶尖开源生态。",
        "c3_tags": ["代码生成", "复杂推理", "无限制商用"],
        
        "c4_badge": "Apache 2.0 工业标准",
        "c4_title": "gpt-oss · IBM Granite",
        "c4_desc": "标准商业许可，附带明确专利授权，企业合规交付首选。",
        "c4_tags": ["企业友好", "明确专利", "商用免责"],
        
        "c5_badge": "OpenMDW 商业附条件",
        "c5_title": "Nemotron 3.5 / Super",
        "c5_desc": "具备极强长上下文与合成数据能力，商业化需遵循 NVIDIA 接受性使用政策。",
        "c5_tags": ["合成数据", "角色对齐", "合规审查"],
        
        "c6_label": "03 / EDGE RUNTIME CONSOLE",
        "c6_title": "敏感数据不出域，<br>按需本地化。",
        "c6_desc": "16GB Mac 本地运行轻量模型；云端私有算力池运行 MoE 满血版。",
        "c6_endpoint": "https://ai-internal.corp/v1/models",
        "c6_mockup_head": ("💻 本地与专网节点", "13/13 健康"),
        "c6_mockup_items": [
            ("gemma-4-12b (Apple Metal)", "42 t/s 离线", "lime"),
            ("qwen-3.5-9b (Local Code)", "纯离线运行", "lime"),
            ("deepseek-v4-moe (Cloud Private)", "GPU集群", "gray"),
            ("gateway-auth (Vault AppRole)", "动态注入", "gray"),
        ],
        
        "c7_label": "04 / DATA SECURITY COVENANT",
        "c7_title": "你的网关。<br>你的数据主权。",
        "c7_items": [
            "核心代码与财务数据走本地开源模型",
            "架构规划与复杂难题脱敏上云端顶配",
            "Vault AppRole 动态分发后端凭据",
            "全链路 TLS 1.3 与内网 Unix Socket 通信",
        ],
        "c7_rule": "商业保障前沿上限 · 开源托底安全底线",
        "foot_left": "AI Collaboration System · 04 混合网关与开源模型矩阵",
        "foot_right": "许可证合规与私有算力架构 ↗",
    },
    {
        "id": "05",
        "fname": "ai-team-bento-05-human-owner",
        "title_cn": "AI团队协作 · 05 人类终局篇",
        "brand": "Human-AI Symbiosis",
        "navs": ["人类角色", "责任边界", "自主等级"],
        "eyebrow": "FROM PROMPT OPERATOR TO AI LEADER",
        "h1": "AI 负责交付。<br>人负责定义。<br><span>人负责担责。</span>",
        "sub": "当模型能写代码、做调研、改架构，人类不再是低效的逐行敲字工。你成为这支虚拟 AI 军团的首席架构师与终审合伙人。",
        "btn_main": "能力进阶 ↓",
        "btn_sec": "责任边界 ↗",
        
        "c1_label": "01 / THE HUMAN RESPONSIBILITY CORE",
        "c1_title": "AI 擅长找最优解，人类负责定好问题。",
        "c1_nodes": [("Human: Goal", False), ("AI Team: Exec", False), ("Human: Judge", True), ("Human: Account", False)],
        "c1_b1_title": "Goal & Constraints (输入定义)",
        "c1_b1_desc": "真实业务痛点、商业价值定调<br>系统 SLA、安全红线与预算约束",
        "c1_b2_title": "Judgment & Accountability (输出终审)",
        "c1_b2_desc": "复杂矛盾拍板、边界取舍<br>线上事故责任与商业后果最终承担",
        "c1_foot": "模型永远无法替你承担删库、违规或亏损的真实法律与商业责任。",
        
        "c2_label": "02 / AUTONOMY LADDER",
        "c2_stat": "L0➔L5",
        "c2_stat_unit": "自治能力跃迁",
        "c2_sub": "从单点问答走向多智能体团队编排",
        "c2_s1_v": "100%",
        "c2_s1_l": "决策所有权归人类",
        "c2_s2_v": "0",
        "c2_s2_l": "责任可转嫁给模型",
        
        "c3_badge": "从 Prompt 到编排",
        "c3_title": "设计协同流水线",
        "c3_desc": "不再反复调教单句 Prompt，而是设计任务状态机、验收标准与回退策略。",
        "c3_tags": ["状态机", "验收标准", "自动回退"],
        
        "c4_badge": "商业痛点洞察",
        "c4_title": "真实需求共情",
        "c4_desc": "模型看不见用户的真实委屈与商业博弈，人类必须牢牢把握产品灵魂。",
        "c4_tags": ["用户洞察", "业务直觉", "商业模式"],
        
        "c5_badge": "生产责任兜底",
        "c5_title": "安全生产红线",
        "c5_desc": "不可逆的数据库迁移、权限收敛与关键发版，必须由人类物理确认。",
        "c5_tags": ["物理确认", "红线防护", "责任自负"],
        
        "c6_label": "03 / AGENT LEADER DASHBOARD",
        "c6_title": "从微观代码脱身，<br>统揽工程全局。",
        "c6_desc": "监控虚拟团队的任务进度、Token 消耗比、单测覆盖率与回归指标。",
        "c6_endpoint": "orchestrator: ai-workspace-team-status",
        "c6_mockup_head": ("👑 团队统筹控制台", "8 Agents Active"),
        "c6_mockup_items": [
            ("Worker (Luna): 120 文件预处理", "100% 完成", "lime"),
            ("Engineer (Sonnet): 核心 PR 就绪", "测试通过", "lime"),
            ("Architect (Astra): 架构 Review", "审核批准", "lime"),
            ("人类合伙人: 终审发布合并", "待人类确认", "lime", True),
        ],
        
        "c7_label": "04 / THE ULTIMATE HUMAN MOAT",
        "c7_title": "工具越智能。<br>判断力越稀缺。",
        "c7_items": [
            "对业务真实痛点的共情与深度洞察",
            "在不完美现实中制定合理取舍",
            "为线上故障与用户数据承担真实后果",
            "把控产品灵魂与核心竞争力走向",
        ],
        "c7_rule": "技术的终点不是取代人类 · 而是赋予人类超级个体的能力",
        "foot_left": "AI Collaboration System · 05 人类角色与终极责任护城河",
        "foot_right": "从操作工到系统主人 ↗",
    },
]

def render_poster_html(p):
    flow_nodes_html = ""
    for i, (ntext, is_pri) in enumerate(p["c1_nodes"]):
        cls = "node primary" if is_pri else "node"
        flow_nodes_html += f'<div class="{cls}">{ntext}</div>'
        if i < len(p["c1_nodes"]) - 1:
            flow_nodes_html += '<div class="connector"></div>'

    mockup_items_html = ""
    for item in p["c6_mockup_items"]:
        title = item[0]
        badge = item[1]
        badge_cls = item[2]
        is_active = item[3] if len(item) > 3 else False
        act_cls = "mockup-item active" if is_active else "mockup-item"
        mockup_items_html += f"""
        <div class="{act_cls}">
          <span>{title}</span>
          <span class="mockup-pill {badge_cls}">{badge}</span>
        </div>
        """

    c3_tags_html = "".join([f'<span class="tag">{t}</span>' for t in p["c3_tags"]])
    c4_tags_html = "".join([f'<span class="tag">{t}</span>' for t in p["c4_tags"]])
    c5_tags_html = "".join([f'<span class="tag">{t}</span>' for t in p["c5_tags"]])
    c7_items_html = "".join([f'<li>{it}</li>' for it in p["c7_items"]])
    navs_html = f'<span class="nav-pill">{p["navs"][0]}</span>' + "".join([f'<span>{n}</span>' for n in p["navs"][1:]])

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>{p["title_cn"]}</title>
  <style>{SHARED_CSS}</style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="logo">↗</div>
      <span>{p["brand"]}</span>
    </div>
    <nav>
      {navs_html}
    </nav>
  </header>

  <section class="hero">
    <div>
      <div class="eyebrow">{p["eyebrow"]}</div>
      <h1>{p["h1"]}</h1>
    </div>
    <div>
      <p>{p["sub"]}</p>
      <div class="actions">
        <a class="btn" href="#">{p["btn_main"]}</a>
        <a class="btn secondary" href="#">{p["btn_sec"]}</a>
      </div>
    </div>
  </section>

  <section class="grid">
    <!-- Card 01 Flow -->
    <article class="card flow">
      <div>
        <div class="label">{p["c1_label"]}</div>
        <h2>{p["c1_title"]}</h2>
        <div class="flow-row">
          {flow_nodes_html}
        </div>
        <div class="branches">
          <div class="branch">
            <strong>{p["c1_b1_title"]}</strong>
            <small>{p["c1_b1_desc"]}</small>
          </div>
          <div class="branch">
            <strong>{p["c1_b2_title"]}</strong>
            <small>{p["c1_b2_desc"]}</small>
          </div>
        </div>
      </div>
      <div class="footnote">{p["c1_foot"]}</div>
    </article>

    <!-- Card 02 Numbers -->
    <article class="card numbers">
      <div>
        <div class="label">{p["c2_label"]}</div>
        <div class="stat-main">{p["c2_stat"]}<small>{p["c2_stat_unit"]}</small></div>
        <div class="stat-sub">{p["c2_sub"]}</div>
      </div>
      <div class="stats">
        <div><strong>{p["c2_s1_v"]}</strong><span>{p["c2_s1_l"]}</span></div>
        <div><strong>{p["c2_s2_v"]}</strong><span>{p["c2_s2_l"]}</span></div>
      </div>
    </article>

    <!-- Card 03 Source 1 -->
    <article class="card source">
      <div class="source-head">
        <span class="icon">⚡</span>
        <span class="badge">{p["c3_badge"]}</span>
      </div>
      <div>
        <h3>{p["c3_title"]}</h3>
        <p>{p["c3_desc"]}</p>
      </div>
      <div class="tags">{c3_tags_html}</div>
    </article>

    <!-- Card 04 Source 2 -->
    <article class="card source">
      <div class="source-head">
        <span class="icon">🌿</span>
        <span class="badge">{p["c4_badge"]}</span>
      </div>
      <div>
        <h3>{p["c4_title"]}</h3>
        <p>{p["c4_desc"]}</p>
      </div>
      <div class="tags">{c4_tags_html}</div>
    </article>

    <!-- Card 05 Source 3 -->
    <article class="card source">
      <div class="source-head">
        <span class="icon">⚖️</span>
        <span class="badge">{p["c5_badge"]}</span>
      </div>
      <div>
        <h3>{p["c5_title"]}</h3>
        <p>{p["c5_desc"]}</p>
      </div>
      <div class="tags">{c5_tags_html}</div>
    </article>

    <!-- Card 06 Workspace -->
    <article class="card workspace">
      <div>
        <div class="label">{p["c6_label"]}</div>
        <h2>{p["c6_title"]}</h2>
        <p>{p["c6_desc"]}</p>
        <code class="endpoint">{p["c6_endpoint"]}</code>
      </div>
      <div class="ui-mockup">
        <div class="mockup-header">
          <span>{p["c6_mockup_head"][0]}</span>
          <span style="font-size:10px; color:#6b7280;">{p["c6_mockup_head"][1]}</span>
        </div>
        {mockup_items_html}
      </div>
    </article>

    <!-- Card 07 Security -->
    <article class="card security">
      <div>
        <div class="label">{p["c7_label"]}</div>
        <h2>{p["c7_title"]}</h2>
        <ul>
          {c7_items_html}
        </ul>
      </div>
      <div class="rule-box">{p["c7_rule"]}</div>
    </article>
  </section>

  <footer>
    <span>{p["foot_left"]}</span>
    <span>{p["foot_right"]}</span>
  </footer>
</body>
</html>"""
    return html

for p in POSTERS:
    fname = p["fname"]
    tmp_html = f"/tmp/{fname}.html"
    out_png_retina = os.path.join(ASSETS_DIR, f"{fname}.png")
    out_jpg_retina = os.path.join(ASSETS_DIR, f"{fname}.jpg")
    desktop_png = os.path.join(DESKTOP_DIR, f"{p['id']}-{p['title_cn'].replace(' · ', '-')}.png")

    html_content = render_poster_html(p)
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 1. Take high-res retina screenshot with Chrome
    cmd = [
        CHROME_BIN,
        "--headless",
        "--disable-gpu",
        f"--screenshot={out_png_retina}",
        "--window-size=896,1024",
        "--force-device-scale-factor=2",
        f"file://{tmp_html}"
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 2. Convert to high-quality JPEG for web distribution
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "92", out_png_retina, "--out", out_jpg_retina], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. Copy to desktop folder
    shutil.copy2(out_png_retina, desktop_png)
    print(f"Generated {p['id']}: {out_png_retina} ({os.path.getsize(out_png_retina)} bytes)")
    print(f"  Synced to Desktop: {desktop_png}")

print("All 5 Bento Grid Posters generated successfully!")
