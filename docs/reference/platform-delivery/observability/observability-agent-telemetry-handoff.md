---
title: 全栈可观测性与 Agent 节点采集治理交接报告 (Hand-Off)
description: 覆盖 observability.svc.plus 故障排查、全网 8 台 Edge Agent 节点时序指标与流量采集上报治理、Vault 权威路径统一收敛及日常维护指南。
slug: observability-agent-telemetry-handoff
lang: zh
date: 2026-11-09
version: "1.1"
status: release
category: platform-delivery
tags:
  - observability
  - victoriametrics
  - vector
  - xray
  - caddy
  - edge-agent
  - vault
  - handoff
---

# 全栈可观测性与 Agent 节点采集治理交接报告 (Hand-Off)

> **交付日期**：2026-11-09  
> **责任范围**：`observability.svc.plus` 监控集群、8 个 Edge Agent 节点、Vault 凭据规范、Grafana 插件与 Chart 泛化沉淀

---

## 一、交付背景与核心成果总览

本阶段针对 `observability.svc.plus` 访问故障、全网 8 个 Edge Agent 节点的流量统计与节点指标采集上报异常、以及 Vault 密钥路径的历史漂移进行了全链路端到端排查、闭环修复与规范化统一：

1. **监控端公网入口彻底恢复**：
   - 解决 `https://observability.svc.plus/` 报 503 `no available server`；
   - Grafana、VictoriaMetrics、VictoriaLogs、vmauth 读写与查询接口全量恢复正常。
2. **8 台 Agent 节点 100% 正常采集上报**：
   - 补齐了 3 台缺失 Basic Auth 的节点（`jp-xconnect-02`、`sg-xconnect`、`us-xconnect-01`）配置，彻底消除网关 401 丢弃；
   - 恢复了洛杉矶节点（`us-xconnect-los-angeles-custom-01`）挂死的 Vector 服务；
   - 全网 8 台节点 Node CPU/内存、Xray 流量计数与 Goroutines、Caddy 网关指标全量实时入库。
3. **CoreDNS 链路自愈**：
   - 清理了 K3s 节点变更残留的 CoreDNS CrashLoop 实例，恢复集群内部 UDP 53 解析。
4. **统一 Vault 权威路径标准**：
   - **域名 TLS 证书密钥对**：全量废除历史旧路径 `kv/data/prod/ulighthost-xconnect/observability.svc.plus`，统一收敛至 `VAULT_TLS_SECRET_PATH="kv/data/CICD/domains/svc.plus"`；
   - **监控认证鉴权凭据**：统一使用 `AGENT_PROXY_VECTOR_VAULT_KV_PATH="kv/data/CICD/observability"`；
   - `Infrastructure-MCP-Server` 代码、测试用例及 50 份规范交付白皮书完成全量重构对齐。
5. **Chart 模板泛化沉淀**：
   - 4 个 MCP Server、Traefik 独立路由与动态 `--allowed-hosts` 注入已合入 `ai-workspace-infra/artifacts` 主干（PR #276）。

---

## 二、关键故障排查与根因分析 (RCA)

### 1. `https://observability.svc.plus/` 报 503 No Available Server

- **故障现象**：公网访问 Grafana 与各监控接口均返回 HTTP 503。
- **根因分析**：
  1. 宿主机主机名从 `localhost` 变更为 `sit-k3s-v6`，K3s 重新注册了新节点 `sit-k3s-v6`，旧节点 `localhost` 变为 `NotReady`；
  2. `local-path` PersistentVolume 的 `nodeAffinity` 不可变字段锁定在 `localhost`，导致调度器报错 `didn't match PersistentVolume's node affinity`；
  3. VictoriaMetrics 与 Grafana Pod 处于 `Pending` 状态，Traefik Ingress 后端 Endpoints 为空，触发 503；
  4. CoreDNS 实例因节点 CNI 漂移引起的健康检查超时，内部服务无法完成 DNS 解析。
- **处置方案**：
  - 对活跃节点打标签 `kubernetes.io/hostname=localhost` 满足 PV 拓扑约束；
  - 删除失效 `localhost` 节点，强制清理 Terminating 挂起 Pod，调度器立即完成挂载启动；
  - 修复集群 CoreDNS 实例，DNS 响应恢复正常，Endpoints 成功挂载。

---

### 2. Agent 节点向中心上报 401 Unauthorized

- **故障现象**：`jp-xconnect-02`、`sg-xconnect`、`us-xconnect-01` 本地采集正常，但中心 VictoriaMetrics 查不到时序样本，Vector 本地日志出现大量 `Http status: 401 Unauthorized` 丢弃。
- **根因分析**：
  - `observability.svc.plus` 接入层 `vmauth` 严格开启 Basic Auth 鉴权（用户名：`observability`，密码来自 `kv/data/CICD/observability`）；
  - 其他 5 台节点配有 `[sinks.prometheus_remote.auth]` 与 `[sinks.victorialogs.auth]`，而上述 3 台机器缺少 auth 块，导致请求为匿名，被网关直接拒收。
- **处置方案**：
  - 自动备份并在 3 台机器的 `/etc/vector/vector.toml` 中补齐 Basic Auth 块；
  - 通过 `vector validate` 验证语法并通过 `systemctl restart vector` 生效，指标即刻开始入库。

---

### 3. 洛杉矶节点（`us-xconnect-los-angeles-custom-01`）采集停滞

- **故障现象**：本地进程在运行但 VictoriaMetrics 长期无时序样本更新。
- **根因分析**：
  - 洛杉矶节点 Vector 进程自 11 月 4 日启动后长期未重启，在 11 月 6 日中心监控维护期间请求失败重试耗尽，且触发了 cgroup 内存阈值（available: 0B），导致协程挂起不再发出 Scrape 请求。
- **处置方案**：
  - 重启 Vector 进程后，内存重置为健康水位，Xray 与 Node 指标采集全量恢复。

---

### 4. 503 与 404 瞬时丢弃及计费触发 503

- **故障现象**：部分节点出现短时 503 重试或 404 丢弃，Caddy 出现 502。
- **根因分析**：
  - 当 Xray 进程重启时，Caddy 与上游之间的 Unix socket 连接断开，导致 Caddy 在重连窗口内记录 502/503；
  - 计费服务如果发生瞬时超时，上报链路会根据重试策略进行指数退避。
- **处置方案**：
  - 配置合理的 systemd socket 激活与依赖启动顺序，减少重启间隙的 socket 缺失窗口。

---

## 三、Vault 权威路径统一规范

为杜绝多仓库配置漂移与凭据不同步，统一规范各组件读取 Vault 的环境变量与物理路径：

| 配置分类 | 环境变量参数 | 权威 Vault KV v2 物理路径 | 作用描述与约束 |
| :--- | :--- | :--- | :--- |
| **域名 TLS 证书密钥对** | `VAULT_TLS_SECRET_PATH` | `kv/data/CICD/domains/svc.plus` | 统一存放 `*.svc.plus` 通配符/主域名证书（`tls.crt` / `tls.key`）。**严禁使用旧路径 `kv/data/prod/ulighthost-xconnect/observability.svc.plus`** |
| **监控认证鉴权凭据** | `AGENT_PROXY_VECTOR_VAULT_KV_PATH` | `kv/data/CICD/observability` | 存放 Agent Vector 上报与查询的鉴权 Basic Auth 凭据（`user` / `password`） |
| **环境基准** | `VAULT_ENV_PATH` | `prod` | 环境标识，与 agent 侧保持一致 |
| **Vault 入口** | `VAULT_ADDR` | `https://vault.svc.plus` | 全局 Vault 集中认证 API 地址 |

### Kubernetes SecretStore (ESO) 对齐规范

在 `sit-k3s-v6` 集群的 `observability-sit` 命名空间中：
- `SecretStore/observability-ingest-reader`：配置 `path: kv` 与 `version: v2`；
- `ExternalSecret/observability-ingest-auth`：`remoteRef.key: CICD/observability`，由 ESO 自动拉取密码生成 Kubernetes Secret；
- `ExternalSecret/shared-observability-tls`：`remoteRef.key: CICD/domains/svc.plus`，自动同步 TLS 证书供 IngressRoute 使用。

---

## 四、全网 8 节点实测采集与上报矩阵 (2026-11-09)

### 验证命令
```bash
curl -k -s -u 'observability:<PASSWORD>' \
  'https://observability.svc.plus/api/v1/query?query=count by (instance)(node_cpu_seconds_total)'
```

### 节点状态矩阵

| 节点 FQDN | 操作系统 / 架构 | Vector 服务状态 | Basic Auth 状态 | Node 指标上报 | Xray Goroutines 上报 | 状态评定 |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| `jp-free-selfhost-prod-v2.svc.plus` | Linux / amd64 | Active (Running) | 已配置 | ✅ 正常 (8 CPU series) | ✅ 正常 (2 series) | **健康** |
| `jp-xconnect-01.svc.plus` | Linux / amd64 | Active (Running) | 已配置 | ✅ 正常 (16 CPU series) | ✅ 正常 (2 series) | **健康** |
| `jp-xconnect-02.svc.plus` | Linux / amd64 | Active (Running) | **已修复** | ✅ 正常 (16 CPU series) | ✅ 正常 (2 series) | **已恢复** |
| `ph-xconnect.svc.plus` | Linux / amd64 | Active (Running) | 已配置 | ✅ 正常 (8 CPU series) | ✅ 正常 (2 series) | **健康** |
| `sg-xconnect.svc.plus` | Linux / amd64 | Active (Running) | **已修复** | ✅ 正常 (8 CPU series) | ✅ 正常 (2 series) | **已恢复** |
| `us-xconnect-01.svc.plus` | Linux / amd64 | Active (Running) | **已修复** | ✅ 正常 (8 CPU series) | ✅ 正常 (2 series) | **已恢复** |
| `us-xconnect.svc.plus` | Linux / amd64 | Active (Running) | 已配置 | ✅ 正常 (8 CPU series) | ✅ 正常 (2 series) | **健康** |
| `us-xconnect-los-angeles-custom-01.svc.plus` | Linux / amd64 | Active (Running) | 已配置 (已重启) | ✅ 正常 (8 CPU series) | ✅ 正常 (2 series) | **已恢复** |

---

## 五、Grafana 仪表盘直接核验地址

以下生产监控大盘已恢复实时时序拉取，数据源为 VictoriaMetrics：

1. **Xray 流量与运行时大盘**：  
   `https://observability.svc.plus/d/begqoward2epsf/xray-dashboard?from=now-1h&to=now&timezone=browser&var-job=&var-instance=$__all`
2. **Caddy 代理网关大盘**：  
   `https://observability.svc.plus/d/fed94ifiv8h6oc/caddy?var-interval=10m&from=now-24h&to=now&timezone=browser&var-datasource=P4169E866C3094E38&var-environment=$__all&var-cluster=$__all&var-service=$__all&var-instance=$__all&refresh=1m`
3. **Node 主机状态监控**：  
   `https://observability.svc.plus/d/StarsL-JOB-node/80a0fc1?var-interval=3m&from=now-30m&to=now&timezone=browser&var-cluster=&var-environment=&var-job=&var-name=&var-instance=&var-total=&var-device=&var-maxmount=&var-show_name=`

---

## 六、后续维护与日常操作指引

1. **统一环境变量注入**：
   供运维人员在 Shell 会话中调试使用（切勿写入代码仓库明文）：
   ```bash
   export VAULT_ENV_PATH=prod
   export VAULT_ADDR="https://vault.svc.plus"
   export VAULT_TLS_SECRET_PATH="kv/data/CICD/domains/svc.plus"
   export AGENT_PROXY_VECTOR_VAULT_KV_PATH="kv/data/CICD/observability"
   ```
2. **新增 Edge Agent 节点的交付要求**：
   在通过 Ansible 或 Shell 部署 Vector 时，确保配置模板注入 `[sinks.prometheus_remote.auth]` 与 `[sinks.victorialogs.auth]`，避免匿名裸发被 vmauth 拦截。
3. **K3s 节点改名防范**：
   在单节点 K3s 演进或维护时，避免频繁更改主机名；如因漂移导致 PV `nodeAffinity` 失效，优先为新节点追加原别名标签：
   ```bash
   kubectl label node <new_node_name> kubernetes.io/hostname=localhost --overwrite
   ```
