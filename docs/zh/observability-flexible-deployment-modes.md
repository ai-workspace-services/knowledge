# Observability 多模式兼容与平滑演进指南

> **2026-10-26 状态补充**：原有 Ansible 三模式说明和示例保留，但不能据此推断本轮 K3s 的托管模式、全部 Agent 或数据迁移均已验收。本轮真实 Chart 边界、Flux 交付、故障与恢复证据统一记录在下方「五、K3s Chart 与 Flux 运行记录」；已验证项与待验证项分列。

> **适用范围**：`ai-workspace-infra/playbooks` (`deploy_observability.yml`, `deploy_observability_server.yml`, `deploy_observability_agent.yml`)  
> **核心原则**：完整保留原有的 **`self_hosted`（自建全栈）模式**作为默认兜底方案，同时无缝扩展对 **`grafana_cloud`** 与 **`victoria_cloud`** 托管模式的支持。

---

## 一、 架构设计：三轨并行兼容模式

在 Ansible Playbooks 中通过全局变量 `observability_mode` 控制部署行为，默认保持完全向下兼容：

```mermaid
graph TD
    Playbook[deploy_observability.yml] --> Check{observability_mode 变量}

    Check -->|self_hosted <默认>| Mode1[模式 1: 完整自建 Self-Hosted]
    Check -->|grafana_cloud| Mode2[模式 2: Grafana Cloud 托管]
    Check -->|victoria_cloud| Mode3[模式 3: Victoria Cloud 托管]

    subgraph 模式 1: Self-Hosted (原方案 100% 保留)
        Mode1 --> Server1[deploy_observability_server.yml<br/>拉起 Prometheus / VictoriaLogs / Grafana 容器]
        Mode1 --> Agent1[deploy_observability_agent.yml<br/>推送遥测数据至本地 Server IP]
    end

    subgraph 模式 2 & 3: 云端托管模式
        Mode2 --> Server2[deploy_observability_server.yml<br/>自动跳过/输出提示]
        Mode2 --> Agent2[deploy_observability_agent.yml<br/>根据 Cloud 凭据推送至 Grafana OTLP/Loki]

        Mode3 --> Server3[deploy_observability_server.yml<br/>自动跳过/输出提示]
        Mode3 --> Agent3[deploy_observability_agent.yml<br/>推送至 VictoriaMetrics/Logs Cloud API]
    end
```

---

## 二、 三种兼容模式详细对比

| 部署模式 (`observability_mode`) | **1. `self_hosted` (默认原方案)** | **2. `grafana_cloud` (云端模式)** | **3. `victoria_cloud` (云端模式)** |
| :--- | :--- | :--- | :--- |
| **`deploy_observability_server.yml`** | ✅ **正常运行**，拉起本地全套 Docker 容器 | ⏸️ **自动跳过**（输出 Cloud 模式提示） | ⏸️ **自动跳过**（输出 Cloud 模式提示） |
| **`deploy_observability_agent.yml`** | ✅ **正常运行**，遥测数据送往本地 IP | ✅ **正常运行**，遥测数据送往 Grafana Cloud | ✅ **正常运行**，遥测数据送往 Victoria Cloud |
| **数据目的地 (Sink)** | 本地 Prometheus (9090) & VictoriaLogs (9428) | Grafana Prometheus RemoteWrite & Loki Endpoint | VictoriaMetrics RemoteWrite & VictoriaLogs Endpoint |
| **适用场景** | 私有云、局域网物理集群、完全数据自主 | 云原生 Serverless、免服务端运维、使用云端大盘 | 预测型 Tier 计费、超高吞吐日志与指标 |

---

## 三、 Ansible Playbook 落地扩充方案

在保持原有 Playbook 文件结构不变的前提下，通过增加条件渲染实现兼容：

### 1. 全局变量配置 (`group_vars/all.yml` 或 `.env`)

```yaml
# 遥测模式选型: self_hosted (默认) | grafana_cloud | victoria_cloud
observability_mode: "{{ lookup('ansible.builtin.env', 'OBSERVABILITY_MODE') | default('self_hosted', true) }}"

# ===== 模式 2: Grafana Cloud 专属凭据 =====
grafana_cloud_metrics_url: "https://prometheus-prod-us-central-0.grafana.net/api/v1/push"
grafana_cloud_metrics_user: "{{ lookup('ansible.builtin.env', 'GRAFANA_CLOUD_METRICS_USER') | default('', true) }}"
grafana_cloud_api_key: "{{ lookup('ansible.builtin.env', 'GRAFANA_CLOUD_API_KEY') | default('', true) }}"
grafana_cloud_logs_url: "https://logs-prod-us-central-0.grafana.net/loki/api/v1/push"
grafana_cloud_logs_user: "{{ lookup('ansible.builtin.env', 'GRAFANA_CLOUD_LOGS_USER') | default('', true) }}"

# ===== 模式 3: Victoria Cloud 专属凭据 =====
victoria_cloud_metrics_url: "https://<your-instance>.victoriametrics.com/api/v1/write"
victoria_cloud_bearer_token: "{{ lookup('ansible.builtin.env', 'VICTORIA_CLOUD_BEARER_TOKEN') | default('', true) }}"
```

### 2. 保留并增强 `deploy_observability_server.yml`

```yaml
---
- name: Deploy Observability Server Stack (Prometheus, VictoriaLogs, VictoriaTraces & Grafana)
  hosts: "{{ observability_server_hosts | default('install.svc.plus') }}"
  become: true
  tasks:
    - name: Run Self-Hosted Server Role
      ansible.builtin.include_role:
        name: docker/observability-server
      when: (observability_mode | default('self_hosted')) == 'self_hosted'

    - name: Notice for Cloud Mode
      ansible.builtin.debug:
        msg: "observability_mode is set to '{{ observability_mode }}'. Skipping local server stack deployment."
      when: (observability_mode | default('self_hosted')) != 'self_hosted'
```

### 3. 增强 `deploy_observability_agent.yml` (Vector Agent 动态模版)

修改 Vector Agent 配置模板（`vector.yaml.j2`），实现按模式分发：

```toml
# Prometheus 指标采集源
[sources.prometheus_scrapers]
type = "prometheus_scrape"
endpoints = ["http://localhost:9100/metrics", "http://localhost:9187/metrics"]

{% if observability_mode == 'grafana_cloud' %}
# ----------------------------------------------------------------------
# 模式 2: Grafana Cloud 适配 Sink
# ----------------------------------------------------------------------
[sinks.grafana_cloud_metrics]
type = "prometheus_remote_write"
inputs = ["prometheus_scrapers"]
endpoint = "{{ grafana_cloud_metrics_url }}"
auth.strategy = "basic"
auth.user = "{{ grafana_cloud_metrics_user }}"
auth.password = "{{ grafana_cloud_api_key }}"

[sinks.grafana_cloud_logs]
type = "loki"
inputs = ["journal_logs", "docker_logs"]
endpoint = "{{ grafana_cloud_logs_url }}"
auth.strategy = "basic"
auth.user = "{{ grafana_cloud_logs_user }}"
auth.password = "{{ grafana_cloud_api_key }}"

{% elif observability_mode == 'victoria_cloud' %}
# ----------------------------------------------------------------------
# 模式 3: Victoria Cloud 适配 Sink
# ----------------------------------------------------------------------
[sinks.victoria_cloud_metrics]
type = "prometheus_remote_write"
inputs = ["prometheus_scrapers"]
endpoint = "{{ victoria_cloud_metrics_url }}"
auth.strategy = "bearer"
auth.token = "{{ victoria_cloud_bearer_token }}"

{% else %}
# ----------------------------------------------------------------------
# 模式 1: Self-Hosted 本地自建 Sink (默认 100% 保持原逻辑)
# ----------------------------------------------------------------------
[sinks.local_prometheus]
type = "prometheus_remote_write"
inputs = ["prometheus_scrapers"]
endpoint = "http://{{ observability_server_ip | default('127.0.0.1') }}:9090/api/v1/write"

[sinks.local_victorialogs]
type = "vector"
inputs = ["journal_logs", "docker_logs"]
address = "{{ observability_server_ip | default('127.0.0.1') }}:9428"
{% endif %}
```

---

## 四、 总结

1. **核心文件原封不动**：`deploy_observability.yml`、`deploy_observability_server.yml` 和 `deploy_observability_agent.yml` 保持不变。
2. **零破坏性扩展**：在 `observability_mode: self_hosted` 默认配置下，运行逻辑与过去 100% 一致。
3. **一键切云**：只需在执行命令前传入 `OBSERVABILITY_MODE=grafana_cloud`，即可自动跳过本地 Server 部署并将 Agent 流量安全引入云端托管平台！


## 五、K3s Chart 与 Flux 运行记录（2026-10-26）

本节是现有指南的增量运行记录，不另建一份同主题白皮书。范围为单个已授权 K3s 目标上的 Observability 发布、采集链路和当前数据验证；不记录运行地址、秘密、原始业务数据或手工资产清单。发布与验收主线：[GitOps #570](https://github.com/ai-workspace-infra/gitops/issues/570)。

### 5.1 实际 Chart 归属与拆分边界

| 位置 | 实际职责 | 本轮边界 |
| --- | --- | --- |
| `artifacts/oci/charts/open-platform/charts/observability-agent` | 通用 kube-state-metrics、Node Exporter、process exporter，以及可选 Vector 指标转发 | 独立 HelmRelease；本目标启用三个 exporter，Vector 保持关闭。集群参数来自 GitOps，不硬编码到通用 Chart。 |
| `artifacts/oci/charts/open-platform/charts/observability-stack` | VictoriaMetrics、VictoriaLogs、VictoriaTraces、Grafana、集中 OTLP 接收与查询 | 独立服务端 HelmRelease；采集声明接入现有 backend，不为字面兼容再装一套 Prometheus 存储。 |
| `artifacts/oci/charts/observability` | 旧 Flux 子 HelmRelease 组合与旧 Vector/process 资源 | 冻结兼容，仍有旧声明消费者；没有直接删除模板、替换旧 PVC 或声称所有消费者已迁。 |
| Playbooks | 可复现 Dashboard 导入、最小 Source promotion owner、身份分离的查询验收 | 不通过全量 K3s/Flux/ESO bootstrap 或直接工作负载 apply 完成升级。 |
| GitOps | 目标 values、OCI digest、独立 HelmRelease 与被选中的 release snapshot | main 中存在声明不等于运行中的 Source 已选择它。 |

Node Exporter 的只读宿主 proc/sys/root 和 host-network 例外必须明确验证；process exporter 使用非 root、只读 proc，不以 hostPID 或管理员 API token 作为默认方案；KSM 不为面板统计开放 Secret/ConfigMap 读取。以上不等于整个集群或宿主机已完成 rootless 改造。

本轮实际运行身份另作分层记录，不用安全配置声明替代现场事实：三个 exporter 的 UID 为 `65534`；Stack 中 Grafana 为 `472`、OTel 为 `10001`，VictoriaMetrics / VictoriaLogs / VictoriaTraces 仍沿用既有 UID `0`。因此当前**不是全栈 rootless**。本次保留既有卷与权限，不为补齐标签而递归扩大卷权限，也不将服务降权、数据卷所有权或整个集群迁移捆绑到观测修复。

Vector 的可选 federation → remote-write 是独立参数化能力，不是本轮已启用的跨集群通路，也不承诺历史逐样本重放。旧 journald → VictoriaLogs 迁移仍在 [Artifacts #227](https://github.com/ai-workspace-infra/artifacts/issues/227) 跟踪；服务端具备 OTLP 日志接收不能替代节点日志采集与真实权限验证。

实现与迁移边界：[Artifacts #229](https://github.com/ai-workspace-infra/artifacts/pull/229)、[Chart 收敛预检与运行手册 #228](https://github.com/ai-workspace-infra/artifacts/pull/228)。旧消费者、PVC 身份及日志迁移未全部验收前，不关闭旧实现退役事项。

### 5.2 Flux 驱动部署、普通升级与受约束恢复

正常交付顺序：

1. 合并经过 review/CI 的 producer，使用既有 Chart 发布 workflow 生成新版本；核实 source SHA、包内容及 registry 返回的 OCI manifest digest。不得覆盖已发布版本或把本地包 hash 当作 OCI digest。
2. GitOps 只选择已发布不可变 digest。Agent 和 Stack 的 HelmRelease 分别管理；普通 exporter 升级只动 Agent，不连带重建 Stack/PVC。
3. 从已部署的 release 基线制作只含观测声明及自身 Source tag 的 snapshot，防止把 main 中其他业务变更一并晋级。先核对 old→new 文件差异、scope 与目标身份，再创建 append-only tag。
4. 使用固定 Playbooks owner SHA、真实环境/实例/主机身份及严格 SSH known-host 验证的 operator plan。默认 plan 不改 Source；实际晋级需显式 apply。Owner 仅并发安全地更新精确 GitRepository ref，等待 Flux Source/root/子 HelmRelease 正常协调，不安装 K3s/Flux/ESO，不写业务 Secret、PVC、DNS 或数据库。
5. 使用独立受限查询身份核实实际 workload、metrics 与 Dashboard。管理身份能够执行只读命令，不等于审计身份的权限隔离通过；Grafana Viewer 查询证据也不代替完整 Linux/Kubernetes 权限审计。

Source 选择的是固定 GitOps tag。**合并 main 后等待一个五分钟周期，不会自动把该 Source 晋级到 main。** 本轮主干 pin 对齐另由 [GitOps #580](https://github.com/ai-workspace-infra/gitops/pull/580) 跟踪；这类声明同步不能代替实际 promotion 或运行证据。

默认 forward 继续拒绝不健康的 expected 基线。发生已知失败时，可选择两种**互斥且必须显式授权**的恢复计划；不能把恢复选项用于普通发布的健康门禁旁路：

| 路径 | CLI 与 plan 标记必须一致 | 不可变提交关系与原因 |
| --- | --- | --- |
| 祖先回退 | `--rollback` 与 `rollback: true` | desired 是 expected 的已验证、不同的祖先；必须提供 `rollback_reason` |
| 前向修复恢复 | `--recover-forward` 与 `recover_forward: true` | expected 是 desired 的已验证、不同的祖先，即 **expected → desired**；必须提供有界、非空的 `recovery_reason` |

两者不能同时开启；缺 CLI、缺对应布尔标记、缺原因或祖先方向不符均拒绝。默认仍是只读 plan，实际变更另需 `--apply`。本地和远端 tag/SHA、同一目标 machine/SSH 身份、固定 owner SHA、观测专属 diff 与精确 Source 绑定全部保留。仅显式恢复允许 root 因 health check 未通过而非 Ready，且 last-applied 必须是已知 expected/desired 版本；Source 自身的 Ready、observed generation 和选中版本的 artifact SHA 仍须准确。JSON Patch 仍测试 resourceVersion 与旧 ref，只替换同一 Source 的 ref，不修改 workload 或扩大权限。

成功仍要求最终 Source/root 在 desired 版本 Ready，运行/数据验收另行执行。失败、超时或丢失 patch 响应时保留恢复方向、原因、祖先关系和已知/未知变更证据，不自动伪装成成功，也不自动挑选另一个版本。

Owner：[Playbooks #776](https://github.com/ai-workspace-infra/playbooks/pull/776)；明确祖先回退：[Playbooks #785](https://github.com/ai-workspace-infra/playbooks/pull/785)；失败基线上的受约束前向修复：[Playbooks #792](https://github.com/ai-workspace-infra/playbooks/pull/792)，固定实现 commit `a933bcaceb7bcd8949dd2f9632052fe4ea069ac8`。这里选择的是配置，不是数据库历史回放、存储格式降级或数据恢复授权。

### 5.3 26.2 的真实故障：合法插件包被 50 MB reader 截断

`v2026.10.26.2` 的服务端冷启动被 `verified-grafana-plugins` init gate 阻断，入口出现 502。问题不是未知包被重新信任：既有固定 release asset 为 **50,833,418 bytes**，SHA256 仍是 `e7486697858edf02929f57e068b2971ab23c2f183727d1c28004bfba4c42c2eb`。旧 installer 最多读取 `50,000,001` bytes，并用 `50,000,000` 上限与 checksum 合并断言，因此截断合法 ZIP 后报了统一的 `Archive checksum mismatch`。

最小修复将 archive 上限固定为 **64 MiB**，继续只读 cap+1，并分别报告 size 与 hash 错误。原 SHA、ID/version、200 MB 解包总量、路径及 symlink 校验全部保留。两个独立完整下载得到相同原 SHA；新 installer 对真实包的本地临时验证成功：16 个 ZIP 条目、解包 **148,597,712 bytes**、14 个实际文件、无 symlink、正确插件 ID/version。没有刷新 checksum 来接受未知内容，也未因解包需求继续扩大上限。

源码与发布证据：

- [合法固定插件 release](https://github.com/ai-workspace-infra/observability/releases/tag/xconnect-user-diagnostics-v0.1.0)。
- [Artifacts #235：64 MiB 修复及真实包验证](https://github.com/ai-workspace-infra/artifacts/pull/235)，producer commit `1d3812d386924105498afefbe3c1ad3e418fd90a`。
- [Chart 发布 run 40212878369](https://github.com/ai-workspace-infra/artifacts/actions/runs/40212878369)：source SHA 匹配，发布成功。
- [GitOps #581：通过 Flux 的恢复 snapshot](https://github.com/ai-workspace-infra/gitops/pull/581)。

回退到含同一旧 reader 的 Chart 不能仅凭 tag 已变就称为健康恢复；必须检查新 Pod、用户边界与数据查询。新 patch 版本和已知健康配置分别核实，不挪动原发布 tag。

### 5.4 26.3 恢复基线与后续 26.5 部署状态

恢复 tag：`v2026.10.26.3` → `f7b0b35bcf53184094d821e678212fd3811b86f1`。

| 构件 | 固定版本 / OCI manifest digest |
| --- | --- |
| Observability Stack | `1.1.5` / `sha256:6cf607b36fa0c92fd14f06d4db5186242dba85b7171757257242c0c6f90162a0` |
| Observability Agent | `1.1.1` / `sha256:4095ed924194c7a91aaa2ad00dd21cec3ccfdcd4c342951ac95aec56fe041f12` |

固定声明：[Stack](https://github.com/ai-workspace-infra/gitops/blob/f7b0b35bcf53184094d821e678212fd3811b86f1/services/platform-observability/prod/release.yaml)、[Agent](https://github.com/ai-workspace-infra/gitops/blob/f7b0b35bcf53184094d821e678212fd3811b86f1/services/platform-observability/prod/agent-release.yaml)、[Source](https://github.com/ai-workspace-infra/gitops/blob/f7b0b35bcf53184094d821e678212fd3811b86f1/environments/clusters/prod-web-saas-k3s-v5/source.yaml)。这些文件证明版本选择；下表运行事实来自本轮受控操作者回执，原始状态/查询证据留在受控验收记录，不把生产原始数据写入知识库。

| 验收层 | 本轮记录 | 能证明的范围 |
| --- | --- | --- |
| Source/root/子声明协调 | **PASS**，2026-10-26 00:52:35 Asia/Shanghai（2026-10-25 16:52:35 UTC）记录 verified | 固定 Source 与各级 Flux 协调一致，不等于所有 Panel 正确 |
| Stack 基础健康 | **PASS**，五容器 Ready、零重启；公开健康接口 HTTP 200 | 当前实例与入口已恢复；不证明历史数据迁入 |
| 指定 Viewer 实时查询 | **PASS**，`node-exporter`、`process-exporter`、`kube-state-metrics`、`kubelet`、`cadvisor` 五个 canonical jobs 为 up=1；每 node 覆盖及 CPU/memory 新鲜度通过 | 指定 cluster/environment/node 的实时链路，不代表其他集群或存量主机 |
| Dashboard 配置 | **PASS**，18 个 UID 及 StarsL 模型检查通过 | 原 17 个加新增 StarsL；不是所有 Panel 的真实查询都通过 |
| 30 分钟连续性与稳定观察 | **PENDING** | 观察起点约 2026-10-26 00:47:33 Asia/Shanghai（16:47:33 UTC）；最早完整窗口到 01:17:33。须用实际区间查询和故障/恢复记录结论，不能以时间流逝代替验收 |
| 全量 Panel 数据与隔离 | **PENDING** | UID、模型与代表性查询不能替代逐 Panel/变量/单位/过滤范围验收 |
| 跨集群 Vector | **OFF / NOT_RUN** | 未选远端、未启用生产转发，不宣称多集群闭环 |
| journald 日志迁移 | **NOT_RUN** | 后续 #227；未借本次指标修复扩大日志读取权限 |
| CMDB / 其他主机 / 历史数据 | **未完成 / 未在本轮验收** | 不把本目标 exporter 就绪写成多云资源对账、全量主机部署或历史 metrics/logs/traces 迁入 |

后续不可变发布 `v2026.10.26.5` → `6a63055e84e220ad9ad8d4780a9ad35043fcc0ec`，来自 [GitOps #591 发布 snapshot](https://github.com/ai-workspace-infra/gitops/pull/591)，包含 [#590 的两条 Node exporter 自身 FD 查询 job 约束修复](https://github.com/ai-workspace-infra/gitops/pull/590)。[主干 Source 对齐 #592](https://github.com/ai-workspace-infra/gitops/pull/592) 已合并；Stack/Agent 版本与上表相同。[26.5 固定 Source 声明](https://github.com/ai-workspace-infra/gitops/blob/6a63055e84e220ad9ad8d4780a9ad35043fcc0ec/environments/clusters/prod-web-saas-k3s-v5/source.yaml) 与实际受控晋级回执分别留证，主干合并本身不代表部署。

受控操作者最新回执：2026-10-25 17:18:22 UTC（2026-10-26 01:18:22 Asia/Shanghai）核实 Source/root 指向该 26.5 SHA，子声明也协调至相同 revision；HelmRelease 配置 revision 14 于 17:23:16 UTC 完成最新部署。新 Pod 五容器 Ready、零重启，原 20 GiB PVC 保留；部署 bundle checksum 为 `3874615d42d7565bcf0dff1c83bc4fab5f77434282477450c0ae0c47c3807cfd`。ConfigMap 与 HelmRelease 的正常周期协调存在先后，不能仅凭声明已更新就认为新 Pod 已接收配置。

此回执只补充 26.5 部署状态，不将上表历史 26.3 查询结果挪作新版本验收。26.5 最终 301 条 Viewer 查询、修复后的 Node family/query 覆盖，以及 30 分钟连续性仍 **PENDING**；须以本版本实际查询与完整时间窗口回执更新，不能预写全量 PASS。

上述 PENDING/NOT_RUN 项未完成前，不关闭 [#570](https://github.com/ai-workspace-infra/gitops/issues/570)，也不把此次恢复称为全平台业务验收。后续新增数据证据应更新本节相应行及受控回执，保留本次故障、固定版本和时间边界。
