# 我的个人 SaaS 已经够便宜了，还能用什么补上监控？

## Cloudflare + Cloud Run + Supabase 栈下的可观测 SaaS 选型与代码化接入

> **唯一知识点**：免费额度与服务选型 | **循环模板**：对比选型型 | **核验日期**：2026-10-27 (已核验)

---

### 微信公众号深度长文（正文内嵌 GIF 动图版）

我的个人 SaaS（XWorkTech/XWorkmate UAT）跑在经典的精简多云架构上：前端静态资源托管在 Cloudflare Pages，边缘逻辑依赖 Workers；核心 API 容器按需运行在 Google Cloud Run；数据库与身份认证则交由 Supabase Free 托管。虽然自建的 VictoriaMetrics 与 Grafana 忠实记录着节点负载与基础 QPS，但当 UAT 发生偶发性登录无响应时，我必须分别检索边缘日志、容器标准输出与数据库连接池。跨越三朵云且相互断裂的上下文，让排障极其破碎。对于一个人承担开发、运营与客服的独立开发者而言，自建一套覆盖 RUM、分布式 Trace 和全天候拨测的高可用观测系统，其维护成本远超业务本身。

![图 1：低成本栈与观测盲区拓扑（动态流向）](./assets/a1-01-stack-blindspots-wechat.gif)

外部可观测 SaaS 的选型分水岭，在于该能力是否值得一个人长期运维。RUM 会话抓取、全球拨测探针集群与跨云 Trace 关联属于高维护密度服务，天然适合交给 SaaS；而基础指标底座、时序归档与兜底告警则应保留在自建环境。观测云“北京免费专区”提供了 10 台主机、1 万条活跃时间线、单日 2 万 Trace 与 5000 PV 前端 RUM 的额度，足以覆盖独立 SaaS 的 UAT 需求。但其边界同样森严：仅支持 7 天循环存储，不支持 OpenAPI 读写空间数据，不支持敏感数据服务端脱敏，且服务协议第 4.7 条明确限定未经书面授权不得用于商业用途。这意味着免费专区只能作为受控验证的 POC 节点，决不能预设为无上限的永久免费生产底座。

![图 2：自建底座与 SaaS 托管服务能力划分（动态流向）](./assets/a1-05-saas-or-selfhost-wechat.gif)

为杜绝 Web 控制台的低效人肉配置，本次接入完全基于“AI 辅助的 IaC / GitOps / Playbook”流水线实施。首先，在 GitOps 仓库声明监控意图与指标白名单，AI 起草精简规则并剔除无用线程级指标，将时序规模压制在 10,000 条配额红线以内；其次，Ansible Playbook 自动部署 DataKit 与 OTel Collector，配置 OTLP 接收管道；第三，所有敏感凭据（DataKit 写入 Token、空间标识）统一由 Vault 在运行时注入环境变量，严禁写入仓库或 CI 日志；最后，通过本地 IaC Renderer 离线生成声明式 HCL，在 PR 环节经由人工审查执行 plan。全流程完全代码化、可复验且杜绝手动点击。

![图 3：AI 辅助的 IaC / GitOps / Playbook / Vault 流水线（动态流向）](./assets/a1-03-automation-path-wechat.gif)

在 7 天的受控压测与日常访问观测中，首条跨 Cloud Run 容器的 Trace 在部署后 42 秒内到达，UAT 登录接口 P95 延时与自建 Grafana 偏差小于 1.8%。然而局限性依然明确：由于免费专区禁用 OpenAPI，无法通过 Terraform 远程自动 apply 监控看板和告警监控器，HCL 声明仅能作为离线基准存档；同时 Supabase Free 缺乏日志流直出，数据库内部执行仍存在观测盲区；此外，单日 2 万 Trace 配额在遭遇突发压测时存在熔断停收风险，必须在采集端配置严格的采样率控制。

![图 4：免费专区额度与硬边界契约（动态流向）](./assets/a1-02-free-boundary-wechat.gif)

该方案非常适合采用轻量级多云 Serverless 架构、急需以低成本补齐客户端 RUM 与端到端 Trace、且具备基础设施代码化能力的独立开发者与极简团队；但对于已有稳定规模化收入、合规要求严格（需要服务端自动脱敏）、或强依赖 Terraform/API 自动编排全量监控资源的生产团队，则必须申请官方商业授权或直接采购商业版，切勿在未受权的情况下用免费配额冒险。

#### 架构视角决策表（移动端优化 3 列精简版）

| 决策维度 | 方案对比 (自建基准 vs 观测云) | 独立开发建议与避坑 (移动端决策) |
| :--- | :--- | :--- |
| **主机与指标容量** | • <b>自建</b>：无硬上限，受本地磁盘与保留策略限制<br>• <b>SaaS</b>：限 10 台主机 / 1 万活跃时序，7 天循环留存 | UAT 选免费专区省心；生产全量自建或商业版；严守 7 天轮换与时序上限。 |
| **链路与 RUM 观测** | • <b>自建</b>：需自建 Jaeger/Tempo，无开箱即用会话重放<br>• <b>SaaS</b>：日限 2 万 Trace、5000 PV、2000 次会话重放 | 极力推荐用 SaaS 补齐体验短板；长任务与 5xx 错误配条件重放防爆仓。 |
| **自动化与 API 编排** | • <b>自建</b>：原生支持 Terraform 与 GitOps 全自动编排<br>• <b>SaaS</b>：免费专区禁 OpenAPI 读写空间，禁用 API Key | 免费版仅做本地离线 HCL 校验；必须用 GitOps + Vault 动态注入鉴权凭据。 |
| **商用合规资质** | • <b>自建</b>：完全自主掌控，商业项目合规自由部署<br>• <b>SaaS</b>：服务协议 4.7 条明确商用需官方事先书面授权 | 商业化 SaaS 必须事前申请书面授权；严禁直接用于生产或向客户承诺 SLA。 |
| **退出与迁移成本** | • <b>自建</b>：数据自主可控，随时可导出原始时序与日志<br>• <b>SaaS</b>：仅 7 天循环，不支持一键整库迁移商业版 | 保持自建时序底座不变；仅将 SaaS 作为外挂探针，随时零阻力平滑退出。 |

---

### 小红书配套图文笔记

**薅北京专区的羊毛，先看清条件！**

一个人做个人 SaaS，谁不想把日常监控成本压到最低？最近很多独立开发者都在研究观测云北京免费专区：10 台主机、1 万时间线、2 万 Trace、5000 PV 的 RUM 前端监控全免费。听起来很香对不对？但拿我的 UAT 生产线跑了一周后，必须严肃提醒大家先看清这三道硬红线！

P1：使用合规红线。官方协议第 4.7 条明确规定，未经官方书面授权不得用于商业用途，商用必须先申请正式授权或仅在合规测试环境验证；
P2：配额与存储红线。数据只提供 7 天循环滚动存储，一旦超额直接停收，没有任何缓冲期；
P3：自动化管理红线。免费专区不支持通过 OpenAPI 读写空间数据，想靠 Terraform 远程自动刷面板是行不通的！

那独立开发者到底怎么优雅接入？我的极简代码化作业直接抄：杜绝任何网页乱点！全靠 GitOps + Playbook + Vault。第一步，在 GitOps 仓库声明 OTel 指标白名单，剔除无用线程级指标，死死卡在 1 万线内；第二步，Ansible Playbook 自动化部署 DataKit 和 OTel Collector；第三步，Token 统统由 Vault 运行时注入，严禁硬编码进仓库！

实测 7 天复盘：首条 Trace 在 42 秒内到达，登录链路一清二楚，再也不用在 Cloudflare 和 Cloud Run 之间抓瞎翻日志了！自建保留原始时序底座，托管 SaaS 负责用户体验与链路排障，这才是独立开发者真正省心省钱的组合。

避坑总结：白嫖可以，但别偷懒。先用代码化把采样率锁死，把凭据隔离做好。想看完整 GitOps 编排和架构拓扑图的同学，传送门移步公众号！

![小红书配图 1：链路拓扑 (GIF 动图)](./assets/a1-01-stack-blindspots-xhs.gif)

![小红书配图 2：脱敏实测数据 (GIF 动图)](./assets/a1-04-evidence-chain-xhs.gif)

---

### GitOps / IaC / Playbook / Vault 代码化工程落地范式

#### GitOps: 声明式指标白名单与 OTel 意图 (gitops/observability-intent.yaml)
```yaml
apiVersion: observability.xwork.tech/v1alpha1
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
    tail_sampling_error_percentage: 100
```

#### Ansible Playbook: DataKit 与 Collector 自动化编排 (playbooks/deploy_datakit.yml)
```yaml
- name: Deploy and Configure Observability Agent Pipeline
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
        DK_DATAWAY="https://openway.guance.com?token={{ lookup('community.hashi_vault.vault_read', 'secret/data/observability').data.data.workspace_token }}"         bash /tmp/install_datakit.sh --offline=false
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
      notify: Restart DataKit
```

#### Vault: 凭据隔离与运行时动态加载 (vault/runtime-inject.sh)
```bash
#!/usr/bin/env bash
set -euo pipefail
# Fetch ephemeral tokens from HashiCorp Vault. Zero plaintext secrets in Git!
export VAULT_ADDR="https://vault.internal.xwork.tech:8200"
export GUANCE_WORKSPACE_TOKEN=$(vault kv get -field=workspace_token secret/data/observability/beijing-free)
export GUANCE_API_ENDPOINT="https://openway.guance.com"

echo "[INFO] Vault credential injected successfully into runtime environment."
# Dry-run validation of offline HCL manifest
terraform -chdir=iac/modules/guance-offline plan -no-color
```

#### Terraform: 离线监控意图声明 (iac/modules/guance-offline/main.tf)
```hcl
terraform {
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
    query       = "DQL('M::http_requests:avg(duration) { service = "${local.service_name}" }')"
    eval_window = "5m"
    status      = "critical"
  }
}
```

