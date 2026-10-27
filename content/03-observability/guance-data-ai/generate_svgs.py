# -*- coding: utf-8 -*-
"""
Generates clean, pure-technical SVG diagrams (3-5 per article).
Rules from SKILL.md:
- 3–5 张纯技术架构图（可做 GIF，箭头流动）
- 图内不放日期、合作/授权说明、图说、待实测标记、署名。
"""

def make_svg(width, height, content):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" style="max-width: {width}px; background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; margin: 16px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/>
  </marker>
  <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/>
  </marker>
  <marker id="arrow-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/>
  </marker>
  <marker id="arrow-emerald" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669"/>
  </marker>
  <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
    <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08"/>
  </filter>
</defs>
{content}
</svg>'''

# Article 1 SVG 1: Multi-cloud Topology & Observation Ingress
def get_a1_svg1():
    content = '''
  <!-- Title Box -->
  <rect x="20" y="16" width="760" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="35" y="38" font-size="14" font-weight="700" fill="#1e293b">TOPOLOGY: INDIE SAAS MULTI-CLOUD ARCHITECTURE & OBSERVABILITY INGRESS</text>

  <!-- Cloudflare Edge -->
  <rect x="30" y="70" width="210" height="150" rx="8" fill="#fff7ed" stroke="#fdba74" stroke-width="2" filter="url(#shadow)"/>
  <text x="45" y="96" font-size="13" font-weight="700" fill="#9a3412">Cloudflare Global Edge</text>
  <rect x="45" y="110" width="180" height="38" rx="6" fill="#ffedd5" stroke="#fed7aa"/>
  <text x="55" y="134" font-size="12" fill="#c2410c">Pages (Frontend Assets)</text>
  <rect x="45" y="156" width="180" height="50" rx="6" fill="#ffedd5" stroke="#fed7aa"/>
  <text x="55" y="178" font-size="12" font-weight="600" fill="#c2410c">Workers Ingress</text>
  <text x="55" y="196" font-size="10" fill="#ea580c">W3C traceparent injection</text>

  <!-- Arrow Edge to Run -->
  <path d="M 240 180 L 290 180" fill="none" stroke="#2563eb" stroke-width="2" marker-end="url(#arrow-blue)"/>
  <text x="246" y="170" font-size="10" font-weight="600" fill="#2563eb">HTTPS</text>

  <!-- GCP Cloud Run -->
  <rect x="300" y="70" width="220" height="150" rx="8" fill="#eff6ff" stroke="#93c5fd" stroke-width="2" filter="url(#shadow)"/>
  <text x="315" y="96" font-size="13" font-weight="700" fill="#1e40af">Google Cloud Run</text>
  <rect x="315" y="110" width="190" height="42" rx="6" fill="#dbeafe" stroke="#bfdbfe"/>
  <text x="325" y="132" font-size="12" font-weight="600" fill="#1d4ed8">Core API Container</text>
  <text x="325" y="146" font-size="10" fill="#3b82f6">OTel Go/Node.js SDK</text>
  <rect x="315" y="160" width="190" height="46" rx="6" fill="#e0e7ff" stroke="#c7d2fe"/>
  <text x="325" y="180" font-size="11" font-weight="600" fill="#4338ca">OTel Collector Sidecar</text>
  <text x="325" y="196" font-size="9" fill="#6366f1">Whitelist Filter & Batch Processor</text>

  <!-- Arrow Run to Supabase -->
  <path d="M 520 180 L 570 180" fill="none" stroke="#059669" stroke-width="2" marker-end="url(#arrow-emerald)"/>
  <text x="526" y="170" font-size="10" font-weight="600" fill="#059669">TLS 5432</text>

  <!-- Supabase -->
  <rect x="580" y="70" width="190" height="150" rx="8" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="2" filter="url(#shadow)"/>
  <text x="595" y="96" font-size="13" font-weight="700" fill="#065f46">Supabase Free Tier</text>
  <rect x="595" y="110" width="160" height="42" rx="6" fill="#d1fae5" stroke="#a7f3d0"/>
  <text x="605" y="132" font-size="12" font-weight="600" fill="#047857">PostgreSQL 15</text>
  <text x="605" y="146" font-size="10" fill="#10b981">Client Span Tracking</text>
  <rect x="595" y="160" width="160" height="46" rx="6" fill="#fef2f2" stroke="#fecaca"/>
  <text x="605" y="180" font-size="11" font-weight="600" fill="#b91c1c">Blackbox Boundary</text>
  <text x="605" y="196" font-size="9" fill="#dc2626">No internal agent injection</text>

  <!-- Observability Egress Flow -->
  <path d="M 410 206 L 410 245" fill="none" stroke="#7c3aed" stroke-width="2" marker-end="url(#arrow-purple)"/>
  <text x="418" y="235" font-size="10" font-weight="600" fill="#7c3aed">OTLP / Protobuf</text>

  <!-- DataKit & Destination -->
  <rect x="180" y="250" width="460" height="80" rx="8" fill="#faf5ff" stroke="#d8b4fe" stroke-width="2" filter="url(#shadow)"/>
  <text x="195" y="274" font-size="13" font-weight="700" fill="#6b21a8">Observability Integration Node (DataKit Agent)</text>
  <rect x="195" y="284" width="200" height="36" rx="4" fill="#f3e8ff" stroke="#e9d5ff"/>
  <text x="205" y="306" font-size="11" fill="#7e22ce">Local Buffer & Deduplication</text>
  <rect x="415" y="284" width="210" height="36" rx="4" fill="#ede9fe" stroke="#ddd6fe"/>
  <text x="425" y="306" font-size="11" font-weight="600" fill="#6d28d9">Vault Token Auth Injection</text>
'''
    return make_svg(800, 350, content)

# Article 1 SVG 2: GitOps Code Pipeline
def get_a1_svg2():
    content = '''
  <rect x="20" y="16" width="760" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="35" y="38" font-size="14" font-weight="700" fill="#1e293b">PIPELINE: GITOPS + IAC RENDERER + PLAYBOOK + VAULT WORKFLOW</text>

  <!-- GitOps Step -->
  <rect x="30" y="75" width="160" height="130" rx="6" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
  <text x="45" y="105" font-size="13" font-weight="700" fill="#334155">1. GitOps Repo</text>
  <text x="45" y="130" font-size="11" fill="#64748b">• Non-sensitive env</text>
  <text x="45" y="150" font-size="11" fill="#64748b">• Metric intent YAML</text>
  <text x="45" y="170" font-size="11" fill="#64748b">• Whitelist rules</text>
  <text x="45" y="190" font-size="10" font-weight="600" fill="#0284c7">AI drafts PR & rules</text>

  <!-- Arrow 1 -->
  <path d="M 190 140 L 225 140" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- IaC Step -->
  <rect x="230" y="75" width="160" height="130" rx="6" fill="#f0fdf4" stroke="#86efac" stroke-width="2"/>
  <text x="245" y="105" font-size="13" font-weight="700" fill="#166534">2. IaC Renderer</text>
  <text x="245" y="130" font-size="11" fill="#15803d">• HCL Generator</text>
  <text x="245" y="150" font-size="11" fill="#15803d">• Offline validation</text>
  <text x="245" y="170" font-size="11" fill="#15803d">• terraform plan</text>
  <text x="245" y="190" font-size="10" font-weight="600" fill="#16a34a">Human reviews plan</text>

  <!-- Arrow 2 -->
  <path d="M 390 140 L 425 140" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Playbook Step -->
  <rect x="430" y="75" width="160" height="130" rx="6" fill="#eff6ff" stroke="#93c5fd" stroke-width="2"/>
  <text x="445" y="105" font-size="13" font-weight="700" fill="#1e40af">3. Playbook</text>
  <text x="445" y="130" font-size="11" fill="#1d4ed8">• Ansible execution</text>
  <text x="445" y="150" font-size="11" fill="#1d4ed8">• Deploy DataKit</text>
  <text x="445" y="170" font-size="11" fill="#1d4ed8">• OTel Collector sink</text>
  <text x="445" y="190" font-size="10" font-weight="600" fill="#2563eb">Feature flag control</text>

  <!-- Arrow 3 -->
  <path d="M 590 140 L 625 140" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Vault Step -->
  <rect x="630" y="75" width="140" height="130" rx="6" fill="#fffbeb" stroke="#fde68a" stroke-width="2"/>
  <text x="642" y="105" font-size="13" font-weight="700" fill="#92400e">4. HashiCorp Vault</text>
  <text x="642" y="130" font-size="11" fill="#b45309">• Injects Token</text>
  <text x="642" y="150" font-size="11" fill="#b45309">• Workspace Key</text>
  <text x="642" y="170" font-size="11" fill="#b45309">• Zero plain secret</text>
  <text x="642" y="190" font-size="10" font-weight="600" fill="#d97706">Runtime Isolation</text>

  <!-- Bottom Bar: Zero UI Rule -->
  <rect x="30" y="225" width="740" height="40" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="50" y="250" font-size="12" font-weight="700" fill="#334155">CORE RULE: ZERO WEB UI CLICKING — ALL MUTATIONS VIA PR, CODE & GITOPS AUTOMATION</text>
'''
    return make_svg(800, 280, content)

# Article 1 SVG 3: Whitelist Filtering & Buffer
def get_a1_svg3():
    content = '''
  <rect x="20" y="16" width="760" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="35" y="38" font-size="14" font-weight="700" fill="#1e293b">METRICS OPTIMIZATION: WHITELIST FILTERING & TIMELINE COMPLIANCE</text>

  <!-- Inbound Raw Metrics -->
  <rect x="40" y="75" width="200" height="150" rx="6" fill="#fef2f2" stroke="#fca5a5" stroke-width="2"/>
  <text x="55" y="105" font-size="13" font-weight="700" fill="#991b1b">Raw Metrics Stream</text>
  <text x="55" y="130" font-size="12" fill="#b91c1c">Host & Container Exporters</text>
  <text x="55" y="155" font-size="14" font-weight="700" fill="#dc2626">~36,000 Series</text>
  <text x="55" y="180" font-size="11" fill="#7f1d1d">• Thread-level metrics</text>
  <text x="55" y="200" font-size="11" fill="#7f1d1d">• Transient socket stats</text>

  <!-- Flow to Processor -->
  <path d="M 240 150 L 295 150" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Filter Processor -->
  <rect x="300" y="75" width="200" height="150" rx="6" fill="#eff6ff" stroke="#93c5fd" stroke-width="2"/>
  <text x="315" y="105" font-size="13" font-weight="700" fill="#1e40af">OTel Metric Filter</text>
  <rect x="315" y="120" width="170" height="32" rx="4" fill="#dbeafe"/>
  <text x="325" y="141" font-size="11" fill="#1e40af">Drop: process_threads_*</text>
  <rect x="315" y="160" width="170" height="32" rx="4" fill="#dbeafe"/>
  <text x="325" y="181" font-size="11" fill="#1e40af">Keep: http_requests_total</text>
  <text x="315" y="210" font-size="10" font-weight="600" fill="#2563eb">Strict Whitelist Enforcer</text>

  <!-- Flow to Output -->
  <path d="M 500 150 L 555 150" fill="none" stroke="#059669" stroke-width="2" marker-end="url(#arrow-emerald)"/>

  <!-- Compliant Output -->
  <rect x="560" y="75" width="200" height="150" rx="6" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="2"/>
  <text x="575" y="105" font-size="13" font-weight="700" fill="#065f46">Compliant Output</text>
  <text x="575" y="130" font-size="12" fill="#047857">Target Workspace</text>
  <text x="575" y="155" font-size="14" font-weight="700" fill="#059669">&lt; 10,000 Series</text>
  <text x="575" y="180" font-size="11" fill="#064e3b">• Free Tier Limit: 10,000</text>
  <text x="575" y="200" font-size="11" font-weight="600" fill="#047857">Quota Overrun Prevented</text>
'''
    return make_svg(800, 250, content)

# Article 1 SVG 4: Architecture Boundary
def get_a1_svg4():
    content = '''
  <rect x="20" y="16" width="760" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="35" y="38" font-size="14" font-weight="700" fill="#1e293b">RESPONSIBILITY MATRIX: SELF-HOSTED FOUNDATION VS SAAS CAPABILITIES</text>

  <!-- Left: Self-Hosted -->
  <rect x="40" y="70" width="340" height="200" rx="8" fill="#f8fafc" stroke="#64748b" stroke-width="2"/>
  <text x="60" y="100" font-size="14" font-weight="700" fill="#1e293b">Keep in Self-Hosted (Data Sovereignty)</text>
  <rect x="60" y="115" width="300" height="35" rx="4" fill="#ffffff" stroke="#cbd5e1"/>
  <text x="75" y="138" font-size="12" fill="#334155">Base Host Metrics (VictoriaMetrics / VMAlert)</text>
  <rect x="60" y="160" width="300" height="35" rx="4" fill="#ffffff" stroke="#cbd5e1"/>
  <text x="75" y="183" font-size="12" fill="#334155">Long-term Raw Audit Logs (VictoriaLogs / S3)</text>
  <rect x="60" y="205" width="300" height="35" rx="4" fill="#ffffff" stroke="#cbd5e1"/>
  <text x="75" y="228" font-size="12" fill="#334155">Hard Fallback Alarm Gateways (Prometheus / Alertmanager)</text>

  <!-- Right: SaaS Outsourced -->
  <rect x="420" y="70" width="340" height="200" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="440" y="100" font-size="14" font-weight="700" fill="#1e40af">Outsource to SaaS (Leverage & Speed)</text>
  <rect x="440" y="115" width="300" height="35" rx="4" fill="#ffffff" stroke="#bfdbfe"/>
  <text x="455" y="138" font-size="12" fill="#1d4ed8">Real User Monitoring (RUM) & Session Replay</text>
  <rect x="440" y="160" width="300" height="35" rx="4" fill="#ffffff" stroke="#bfdbfe"/>
  <text x="455" y="183" font-size="12" fill="#1d4ed8">Cross-cloud Distributed Trace Correlation</text>
  <rect x="440" y="205" width="300" height="35" rx="4" fill="#ffffff" stroke="#bfdbfe"/>
  <text x="455" y="228" font-size="12" fill="#1d4ed8">Global Synthetic HTTP/SSL Monitoring Probes</text>
'''
    return make_svg(800, 290, content)

# Article 2 SVGs
def get_a2_svg1():
    content = '''
  <rect x="20" y="16" width="760" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="35" y="38" font-size="14" font-weight="700" fill="#1e293b">PIPELINE: GRAFANA JSON AST PARSING & HCL CODE GENERATION</text>

  <rect x="40" y="75" width="200" height="150" rx="6" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
  <text x="55" y="105" font-size="13" font-weight="700" fill="#334155">Grafana Dashboard JSON</text>
  <text x="55" y="130" font-size="11" fill="#64748b">• Panel targets array</text>
  <text x="55" y="150" font-size="11" fill="#64748b">• PromQL expr string</text>
  <text x="55" y="170" font-size="11" fill="#64748b">• Variable dependencies</text>
  <text x="55" y="195" font-size="10" font-weight="600" fill="#0284c7">Raw JSON Export</text>

  <path d="M 240 150 L 295 150" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="300" y="75" width="200" height="150" rx="6" fill="#faf5ff" stroke="#c084fc" stroke-width="2"/>
  <text x="315" y="105" font-size="13" font-weight="700" fill="#6b21a8">AI AST Analyzer</text>
  <text x="315" y="130" font-size="11" fill="#7e22ce">• Tokenize PromQL</text>
  <text x="315" y="150" font-size="11" fill="#7e22ce">• Align step & window</text>
  <text x="315" y="170" font-size="11" fill="#7e22ce">• Map histogram buckets</text>
  <text x="315" y="195" font-size="10" font-weight="600" fill="#9333ea">Semantic Equivalence</text>

  <path d="M 500 150 L 555 150" fill="none" stroke="#2563eb" stroke-width="2" marker-end="url(#arrow-blue)"/>

  <rect x="560" y="75" width="200" height="150" rx="6" fill="#eff6ff" stroke="#93c5fd" stroke-width="2"/>
  <text x="575" y="105" font-size="13" font-weight="700" fill="#1e40af">Terraform HCL Manifest</text>
  <text x="575" y="130" font-size="11" fill="#1d4ed8">• guance_dashboard spec</text>
  <text x="575" y="150" font-size="11" fill="#1d4ed8">• DQL / PromQL query</text>
  <text x="575" y="170" font-size="11" fill="#1d4ed8">• Offline baseline sync</text>
  <text x="575" y="195" font-size="10" font-weight="600" fill="#2563eb">Reviewable IaC Asset</text>
'''
    return make_svg(800, 250, content)

def get_a2_svg2():
    content = '''
  <rect x="20" y="16" width="760" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="35" y="38" font-size="14" font-weight="700" fill="#1e293b">CIRCUIT BREAKER: DUAL-WRITE TOPOLOGY & 15-MINUTE ROLLBACK</text>

  <rect x="40" y="90" width="180" height="120" rx="6" fill="#f1f5f9" stroke="#94a3b8" stroke-width="2"/>
  <text x="55" y="120" font-size="13" font-weight="700" fill="#334155">Telemetry Source</text>
  <text x="55" y="145" font-size="11" fill="#64748b">Vector & OTel Collector</text>
  <text x="55" y="170" font-size="11" font-weight="600" fill="#0284c7">Dual Sink Dispatcher</text>

  <!-- Split paths -->
  <path d="M 220 130 L 320 100" fill="none" stroke="#059669" stroke-width="2" marker-end="url(#arrow-emerald)"/>
  <text x="240" y="105" font-size="10" font-weight="600" fill="#059669">Primary: 100%</text>

  <path d="M 220 170 L 320 200" fill="none" stroke="#7c3aed" stroke-width="2" stroke-dasharray="4" marker-end="url(#arrow-purple)"/>
  <text x="235" y="200" font-size="10" font-weight="600" fill="#7c3aed">Secondary (Flagged)</text>

  <!-- Sink 1 -->
  <rect x="330" y="65" width="220" height="70" rx="6" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="2"/>
  <text x="345" y="90" font-size="12" font-weight="700" fill="#065f46">Self-Hosted Storage</text>
  <text x="345" y="112" font-size="11" fill="#047857">VictoriaMetrics (PromQL Baseline)</text>

  <!-- Sink 2 -->
  <rect x="330" y="165" width="220" height="70" rx="6" fill="#faf5ff" stroke="#d8b4fe" stroke-width="2"/>
  <text x="345" y="190" font-size="12" font-weight="700" fill="#6b21a8">Guance DataKit Sink</text>
  <text x="345" y="212" font-size="11" fill="#7e22ce">otel_guance_exporter_enabled</text>

  <!-- Rollback Control -->
  <rect x="580" y="65" width="180" height="170" rx="6" fill="#fffbeb" stroke="#fcd34d" stroke-width="2"/>
  <text x="595" y="95" font-size="12" font-weight="700" fill="#92400e">Circuit Breaker</text>
  <text x="595" y="125" font-size="11" fill="#b45309">• GitOps PR Revert</text>
  <text x="595" y="150" font-size="11" fill="#b45309">• Switch: enabled=false</text>
  <text x="595" y="175" font-size="11" fill="#b45309">• Execution: &lt; 4 mins</text>
  <text x="595" y="205" font-size="10" font-weight="700" fill="#d97706">Target: &lt; 15 mins</text>
'''
    return make_svg(800, 260, content)

def get_a2_svg3():
    content = '''
  <rect x="20" y="16" width="760" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="35" y="38" font-size="14" font-weight="700" fill="#1e293b">RECONCILIATION: TIME WINDOW & PERCENTILE METRIC CONVERGENCE</text>

  <rect x="40" y="70" width="340" height="150" rx="6" fill="#f8fafc" stroke="#94a3b8"/>
  <text x="55" y="95" font-size="12" font-weight="700" fill="#334155">VictoriaMetrics (Self-Hosted)</text>
  <text x="55" y="120" font-size="11" fill="#64748b">histogram_quantile(0.95, sum(rate(http_dur_bucket[5m])) by (le))</text>
  <text x="55" y="150" font-size="18" font-weight="700" fill="#0284c7">P95 = 42.1 ms</text>
  <text x="55" y="180" font-size="11" fill="#64748b">Sample count: 120,400 reqs</text>

  <rect x="420" y="70" width="340" height="150" rx="6" fill="#f8fafc" stroke="#94a3b8"/>
  <text x="435" y="95" font-size="12" font-weight="700" fill="#334155">Guance Workspace (SaaS)</text>
  <text x="435" y="120" font-size="11" fill="#64748b">histogram_quantile(0.95, sum(rate(http_dur_bucket[5m])) by (le))</text>
  <text x="435" y="150" font-size="18" font-weight="700" fill="#7c3aed">P95 = 42.8 ms</text>
  <text x="435" y="180" font-size="11" fill="#64748b">Sample count: 120,380 reqs</text>

  <rect x="40" y="235" width="720" height="45" rx="6" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="2"/>
  <text x="60" y="262" font-size="13" font-weight="700" fill="#065f46">DELTA CHECK: |42.8 - 42.1| / 42.1 = 1.66% &lt; 2.0% THRESHOLD (PASS)</text>
'''
    return make_svg(800, 300, content)

def get_a2_svg4():
    content = '''
  <rect x="20" y="16" width="760" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="35" y="38" font-size="14" font-weight="700" fill="#1e293b">MIGRATION FINITE STATE MACHINE: STAGES AND ROLLBACK GATES</text>

  <rect x="40" y="80" width="120" height="90" rx="6" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
  <text x="50" y="110" font-size="12" font-weight="700" fill="#334155">P0: Inventory</text>
  <text x="50" y="130" font-size="10" fill="#64748b">JSON Export</text>
  <text x="50" y="150" font-size="10" fill="#64748b">Tokens in Vault</text>

  <path d="M 160 125 L 185 125" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="190" y="80" width="120" height="90" rx="6" fill="#eff6ff" stroke="#93c5fd" stroke-width="2"/>
  <text x="200" y="110" font-size="12" font-weight="700" fill="#1e40af">P1: Flags</text>
  <text x="200" y="130" font-size="10" fill="#1d4ed8">Playbook switches</text>
  <text x="200" y="150" font-size="10" fill="#1d4ed8">Default: OFF</text>

  <path d="M 310 125 L 335 125" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="340" y="80" width="120" height="90" rx="6" fill="#faf5ff" stroke="#d8b4fe" stroke-width="2"/>
  <text x="350" y="110" font-size="12" font-weight="700" fill="#6b21a8">P2: Dual Write</text>
  <text x="350" y="130" font-size="10" fill="#7e22ce">Trace & Vector</text>
  <text x="350" y="150" font-size="10" fill="#7e22ce">No queue block</text>

  <path d="M 460 125 L 485 125" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="490" y="80" width="120" height="90" rx="6" fill="#fef3c7" stroke="#fcd34d" stroke-width="2"/>
  <text x="500" y="110" font-size="12" font-weight="700" fill="#92400e">P3: Reconcile</text>
  <text x="500" y="130" font-size="10" fill="#b45309">7-day Parallel</text>
  <text x="500" y="150" font-size="10" fill="#b45309">Delta &lt; 2%</text>

  <path d="M 610 125 L 635 125" fill="none" stroke="#059669" stroke-width="2" marker-end="url(#arrow-emerald)"/>

  <rect x="640" y="80" width="120" height="90" rx="6" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="2"/>
  <text x="650" y="110" font-size="12" font-weight="700" fill="#065f46">P4: Switch</text>
  <text x="650" y="130" font-size="10" fill="#047857">Primary UI Cut</text>
  <text x="650" y="150" font-size="10" fill="#047857">Fallback live</text>
'''
    return make_svg(800, 200, content)

# Article 3 SVGs
def get_a3_svg1():
    content = '''
  <rect x="20" y="16" width="760" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="35" y="38" font-size="14" font-weight="700" fill="#1e293b">RUM ARCHITECTURE: CORE WEB VITALS & BROWSER EVENT LOOP CAPTURE</text>

  <rect x="40" y="75" width="220" height="150" rx="6" fill="#eff6ff" stroke="#93c5fd" stroke-width="2"/>
  <text x="55" y="105" font-size="13" font-weight="700" fill="#1e40af">Client Viewport (DOM)</text>
  <text x="55" y="130" font-size="11" fill="#1d4ed8">• LCP (Largest Contentful Paint)</text>
  <text x="55" y="150" font-size="11" fill="#1d4ed8">• INP (Interaction to Next Paint)</text>
  <text x="55" y="170" font-size="11" fill="#1d4ed8">• CLS (Cumulative Layout Shift)</text>
  <text x="55" y="195" font-size="10" font-weight="600" fill="#2563eb">PerformanceObserver API</text>

  <path d="M 260 150 L 315 150" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="320" y="75" width="220" height="150" rx="6" fill="#fef2f2" stroke="#fca5a5" stroke-width="2"/>
  <text x="335" y="105" font-size="13" font-weight="700" fill="#991b1b">Main Thread Event Loop</text>
  <text x="335" y="130" font-size="11" fill="#b91c1c">• Task Queue Scheduling</text>
  <text x="335" y="150" font-size="11" font-weight="700" fill="#dc2626">• Long Task (&gt; 50ms) Block</text>
  <text x="335" y="170" font-size="11" fill="#b91c1c">• Input Delay Starvation</text>
  <text x="335" y="195" font-size="10" font-weight="600" fill="#991b1b">Root Cause of UI Freeze</text>

  <path d="M 540 150 L 595 150" fill="none" stroke="#7c3aed" stroke-width="2" marker-end="url(#arrow-purple)"/>

  <rect x="600" y="75" width="160" height="150" rx="6" fill="#faf5ff" stroke="#d8b4fe" stroke-width="2"/>
  <text x="615" y="105" font-size="13" font-weight="700" fill="#6b21a8">RUM Collector</text>
  <text x="615" y="130" font-size="11" fill="#7e22ce">• Batch Beacon</text>
  <text x="615" y="150" font-size="11" fill="#7e22ce">• Session ID link</text>
  <text x="615" y="170" font-size="11" fill="#7e22ce">• Quota Guard (&lt;5k PV)</text>
  <text x="615" y="195" font-size="10" font-weight="600" fill="#6b21a8">Telemetry Sink</text>
'''
    return make_svg(800, 250, content)

def get_a3_svg2():
    content = '''
  <rect x="20" y="16" width="760" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="35" y="38" font-size="14" font-weight="700" fill="#1e293b">PRIVACY PIPELINE: CLIENT-SIDE DOM MASKING & ZERO LEAKAGE</text>

  <rect x="40" y="75" width="220" height="140" rx="6" fill="#fff7ed" stroke="#fed7aa" stroke-width="2"/>
  <text x="55" y="105" font-size="13" font-weight="700" fill="#9a3412">Browser User Input</text>
  <text x="55" y="130" font-size="11" fill="#c2410c">• Password & Token values</text>
  <text x="55" y="150" font-size="11" fill="#c2410c">• Sensitive form text</text>
  <text x="55" y="175" font-size="10" font-weight="600" fill="#ea580c">Raw UI Interaction</text>

  <path d="M 260 145 L 315 145" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="320" y="75" width="220" height="140" rx="6" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="2"/>
  <text x="335" y="105" font-size="13" font-weight="700" fill="#065f46">Client-Side Mask Engine</text>
  <text x="335" y="130" font-size="11" fill="#047857">• [data-guance-mask] CSS rule</text>
  <text x="335" y="150" font-size="11" fill="#047857">• Input text replace: ***</text>
  <text x="335" y="175" font-size="10" font-weight="600" fill="#059669">Zero Secret Departure</text>

  <path d="M 540 145 L 595 145" fill="none" stroke="#2563eb" stroke-width="2" marker-end="url(#arrow-blue)"/>

  <rect x="600" y="75" width="160" height="140" rx="6" fill="#eff6ff" stroke="#93c5fd" stroke-width="2"/>
  <text x="615" y="105" font-size="13" font-weight="700" fill="#1e40af">Redacted Beacon</text>
  <text x="615" y="130" font-size="11" fill="#1d4ed8">• Safe Session Replay</text>
  <text x="615" y="150" font-size="11" fill="#1d4ed8">• Pure timing metadata</text>
  <text x="615" y="175" font-size="10" font-weight="600" fill="#2563eb">Compliant Ingestion</text>
'''
    return make_svg(800, 240, content)

def get_a3_svg3():
    content = '''
  <rect x="20" y="16" width="760" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="35" y="38" font-size="14" font-weight="700" fill="#1e293b">WATERFALL: 280MS CLIENT LONG TASK VS 38MS BACKEND API</text>

  <!-- Timeline header -->
  <line x1="50" y1="70" x2="750" y2="70" stroke="#cbd5e1" stroke-width="1"/>
  <text x="50" y="65" font-size="10" fill="#64748b">0 ms</text>
  <text x="250" y="65" font-size="10" fill="#64748b">100 ms</text>
  <text x="450" y="65" font-size="10" fill="#64748b">200 ms</text>
  <text x="650" y="65" font-size="10" fill="#64748b">300 ms</text>

  <!-- Backend API -->
  <text x="50" y="100" font-size="12" font-weight="700" fill="#1e40af">Cloud Run Backend API</text>
  <rect x="50" y="110" width="80" height="30" rx="4" fill="#93c5fd" stroke="#3b82f6"/>
  <text x="58" y="130" font-size="11" font-weight="600" fill="#1e3a8a">38 ms (HTTP 200)</text>

  <!-- Client Main Thread -->
  <text x="50" y="170" font-size="12" font-weight="700" fill="#991b1b">Browser Main Thread (AI Component Execution)</text>
  <rect x="130" y="180" width="560" height="30" rx="4" fill="#fca5a5" stroke="#ef4444"/>
  <text x="145" y="200" font-size="11" font-weight="700" fill="#7f1d1d">Long Task: 280 ms (Markdown Regex &amp; React Re-render Lock)</text>
'''
    return make_svg(800, 240, content)

def get_a3_svg4():
    content = '''
  <rect x="20" y="16" width="760" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="35" y="38" font-size="14" font-weight="700" fill="#1e293b">CROSS-LAYER CORRELATION: RUM SESSION TO DISTRIBUTED TRACE</text>

  <rect x="40" y="70" width="220" height="110" rx="6" fill="#eff6ff" stroke="#93c5fd"/>
  <text x="55" y="95" font-size="12" font-weight="700" fill="#1e40af">RUM Session View</text>
  <text x="55" y="120" font-size="11" fill="#1d4ed8">session.id: ses-98a7c2</text>
  <text x="55" y="145" font-size="11" fill="#1d4ed8">action: click#login-button</text>

  <path d="M 260 125 L 315 125" fill="none" stroke="#7c3aed" stroke-width="2" marker-end="url(#arrow-purple)"/>
  <text x="268" y="115" font-size="9" fill="#7c3aed">inject trace_id</text>

  <rect x="320" y="70" width="440" height="110" rx="6" fill="#faf5ff" stroke="#d8b4fe"/>
  <text x="335" y="95" font-size="12" font-weight="700" fill="#6b21a8">Distributed APM Trace Waterfall</text>
  <rect x="335" y="110" width="410" height="24" rx="4" fill="#ede9fe"/>
  <text x="345" y="126" font-size="10" fill="#5b21b6">trace_id: 4bf92f3577b34da6a3ce929d0e0e4736</text>
  <text x="335" y="155" font-size="11" fill="#6b21a8">Span: POST /auth/login → Status: 200 OK → Duration: 38ms</text>
'''
    return make_svg(800, 200, content)

# Article 4 SVGs
def get_a4_svg1():
    content = '''
  <rect x="20" y="16" width="760" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="35" y="38" font-size="14" font-weight="700" fill="#1e293b">CONTEXT PROPAGATION: W3C TRACECONTEXT ACROSS MULTI-CLOUD BOUNDARIES</text>

  <!-- Step 1 Cloudflare -->
  <rect x="40" y="70" width="210" height="160" rx="6" fill="#fff7ed" stroke="#fed7aa" stroke-width="2"/>
  <text x="55" y="95" font-size="12" font-weight="700" fill="#9a3412">1. Cloudflare Workers</text>
  <rect x="55" y="110" width="180" height="40" rx="4" fill="#ffedd5"/>
  <text x="65" y="128" font-size="10" font-weight="600" fill="#c2410c">Generate W3C Headers:</text>
  <text x="65" y="142" font-size="9" fill="#ea580c">traceparent: 00-4bf92...-01</text>
  <text x="55" y="170" font-size="10" fill="#9a3412">• Ingress Rate Limit &amp; WAF</text>
  <text x="55" y="190" font-size="10" fill="#9a3412">• HTTP Fetch Interceptor</text>

  <path d="M 250 150 L 295 150" fill="none" stroke="#2563eb" stroke-width="2" marker-end="url(#arrow-blue)"/>
  <text x="256" y="140" font-size="9" font-weight="600" fill="#2563eb">HTTPS</text>

  <!-- Step 2 Cloud Run -->
  <rect x="300" y="70" width="210" height="160" rx="6" fill="#eff6ff" stroke="#93c5fd" stroke-width="2"/>
  <text x="315" y="95" font-size="12" font-weight="700" fill="#1e40af">2. Google Cloud Run</text>
  <rect x="315" y="110" width="180" height="40" rx="4" fill="#dbeafe"/>
  <text x="325" y="128" font-size="10" font-weight="600" fill="#1d4ed8">Extract &amp; Continue Span:</text>
  <text x="325" y="142" font-size="9" fill="#2563eb">parent_span: 0042...8a</text>
  <text x="315" y="170" font-size="10" fill="#1e40af">• JWT Authenticator</text>
  <text x="315" y="190" font-size="10" fill="#1e40af">• DB Connection Pool</text>

  <path d="M 510 150 L 555 150" fill="none" stroke="#059669" stroke-width="2" marker-end="url(#arrow-emerald)"/>
  <text x="516" y="140" font-size="9" font-weight="600" fill="#059669">PG 5432</text>

  <!-- Step 3 Supabase -->
  <rect x="560" y="70" width="200" height="160" rx="6" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="2"/>
  <text x="575" y="95" font-size="12" font-weight="700" fill="#065f46">3. Supabase Database</text>
  <rect x="575" y="110" width="170" height="40" rx="4" fill="#d1fae5"/>
  <text x="585" y="128" font-size="10" font-weight="600" fill="#047857">Client Outbound Span:</text>
  <text x="585" y="142" font-size="9" fill="#059669">db.system: postgresql</text>
  <text x="575" y="170" font-size="10" fill="#065f46">• Auth Role Check Query</text>
  <text x="575" y="190" font-size="10" fill="#065f46">• Connection Wait Time</text>
'''
    return make_svg(800, 250, content)

def get_a4_svg2():
    content = '''
  <rect x="20" y="16" width="760" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="35" y="38" font-size="14" font-weight="700" fill="#1e293b">PIPELINE: OTEL COLLECTOR MULTI-CLOUD INGESTION &amp; ROUTING</text>

  <rect x="40" y="80" width="160" height="120" rx="6" fill="#f8fafc" stroke="#94a3b8"/>
  <text x="55" y="105" font-size="12" font-weight="700" fill="#334155">Inbound Spans</text>
  <text x="55" y="130" font-size="11" fill="#64748b">• Workers Spans</text>
  <text x="55" y="150" font-size="11" fill="#64748b">• Cloud Run Spans</text>
  <text x="55" y="170" font-size="11" fill="#64748b">• DB Client Spans</text>

  <path d="M 200 140 L 245 140" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="250" y="80" width="280" height="120" rx="6" fill="#eff6ff" stroke="#93c5fd" stroke-width="2"/>
  <text x="265" y="105" font-size="12" font-weight="700" fill="#1e40af">OTel Collector Processing</text>
  <rect x="265" y="115" width="250" height="24" rx="4" fill="#dbeafe"/>
  <text x="275" y="131" font-size="10" fill="#1e40af">MemoryLimiter (max 128MiB)</text>
  <rect x="265" y="145" width="250" height="24" rx="4" fill="#dbeafe"/>
  <text x="275" y="161" font-size="10" fill="#1e40af">Tail Sampling: 100% Errors + 5% P95</text>
  <text x="265" y="190" font-size="9" fill="#2563eb">Prevents Free Quota Overflow</text>

  <path d="M 530 140 L 575 140" fill="none" stroke="#7c3aed" stroke-width="2" marker-end="url(#arrow-purple)"/>

  <rect x="580" y="80" width="180" height="120" rx="6" fill="#faf5ff" stroke="#d8b4fe"/>
  <text x="595" y="105" font-size="12" font-weight="700" fill="#6b21a8">DataKit OTLP Sink</text>
  <text x="595" y="130" font-size="11" fill="#7e22ce">• Protobuf Over HTTP</text>
  <text x="595" y="150" font-size="11" fill="#7e22ce">• Auth via Vault Header</text>
  <text x="595" y="170" font-size="11" fill="#7e22ce">• 20k/day Trace Budget</text>
'''
    return make_svg(800, 220, content)

def get_a4_svg3():
    content = '''
  <rect x="20" y="16" width="760" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="35" y="38" font-size="14" font-weight="700" fill="#1e293b">WATERFALL: CROSS-CLOUD AUTHENTICATION LATENCY BREAKDOWN</text>

  <!-- Root Span -->
  <text x="40" y="75" font-size="11" font-weight="700" fill="#1e293b">POST /api/v1/auth/login [Total: 447 ms]</text>
  <rect x="40" y="85" width="720" height="22" rx="4" fill="#e2e8f0" stroke="#94a3b8"/>
  <text x="50" y="100" font-size="10" fill="#475569">Client End-to-End Latency</text>

  <!-- Cloudflare Edge Span -->
  <text x="60" y="125" font-size="11" font-weight="600" fill="#9a3412">Cloudflare Edge Worker Ingress [12 ms]</text>
  <rect x="60" y="135" width="40" height="20" rx="4" fill="#fed7aa" stroke="#f97316"/>

  <!-- Cloud Run Span -->
  <text x="100" y="175" font-size="11" font-weight="600" fill="#1e40af">Cloud Run: auth-service.verifyCredentials [435 ms]</text>
  <rect x="100" y="185" width="660" height="20" rx="4" fill="#bfdbfe" stroke="#3b82f6"/>

  <!-- Supabase DB Span -->
  <text x="140" y="225" font-size="11" font-weight="700" fill="#dc2626">Supabase Query: SELECT role FROM users WHERE email=? [410 ms]</text>
  <rect x="140" y="235" width="620" height="22" rx="4" fill="#fecaca" stroke="#ef4444"/>
  <text x="150" y="250" font-size="10" font-weight="700" fill="#991b1b">Root Cause: Free Tier DB Cold Connection Wait</text>
'''
    return make_svg(800, 280, content)

def get_a4_svg4():
    content = '''
  <rect x="20" y="16" width="760" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="35" y="38" font-size="14" font-weight="700" fill="#1e293b">SECURITY: DYNAMIC VAULT CREDENTIAL INJECTION ACROSS MULTI-CLOUD</text>

  <rect x="40" y="70" width="220" height="150" rx="6" fill="#fffbeb" stroke="#fde68a" stroke-width="2"/>
  <text x="55" y="95" font-size="13" font-weight="700" fill="#92400e">HashiCorp Vault</text>
  <rect x="55" y="110" width="190" height="30" rx="4" fill="#fef3c7"/>
  <text x="65" y="130" font-size="10" fill="#92400e">Path: secret/data/observability</text>
  <text x="55" y="160" font-size="11" fill="#b45309">• Workspace Write Token</text>
  <text x="55" y="180" font-size="11" fill="#b45309">• Supabase Service Role Key</text>
  <text x="55" y="200" font-size="10" font-weight="600" fill="#d97706">Dynamic Secret Engine</text>

  <path d="M 260 145 L 315 145" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="266" y="135" font-size="9" fill="#475569">Inject at boot</text>

  <rect x="320" y="70" width="440" height="150" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="335" y="95" font-size="13" font-weight="700" fill="#1e293b">Isolated Execution Runtimes</text>
  <rect x="335" y="110" width="410" height="36" rx="4" fill="#eff6ff" stroke="#bfdbfe"/>
  <text x="345" y="132" font-size="11" fill="#1e40af">Cloud Run: OTEL_EXPORTER_OTLP_HEADERS (In-Memory Only)</text>
  <rect x="335" y="155" width="410" height="36" rx="4" fill="#f0fdf4" stroke="#bbf7d0"/>
  <text x="345" y="177" font-size="11" fill="#166534">Edge Worker: Encrypted Secret Binding (No Git Commit)</text>
  <text x="335" y="210" font-size="10" font-weight="700" fill="#047857">Zero Plaintext Secrets in Repositories or Build Logs</text>
'''
    return make_svg(800, 240, content)

print("generate_svgs.py ready.")
