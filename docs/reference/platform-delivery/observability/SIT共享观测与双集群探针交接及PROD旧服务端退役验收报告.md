# SIT 共享观测与双集群探针交接及 PROD 旧服务端退役验收报告

> **交接执行时间**：2026-11-08（Asia/Shanghai）  
> **目标环境**：SIT (`172.237.9.58`, Tokyo 3) 与 PROD (`172.237.24.232`, Tokyo 2)  
> **执行原则**：严格遵循 **Zero Touch PROD** 原则，保障生产环境无损平滑切换，保留全部底层持久化卷及回退锚点。

---

## 摘要与交接背景

为了优化资源利用率并实现多集群统一可观测性：
1. **SIT 保留共享观测服务端与 Infra MCP**：在 SIT 集群构建统一的共享可观测性服务端（VictoriaMetrics, VictoriaLogs, VictoriaTraces, OTel Collector, Ingest Auth vmauth, Grafana v13.2.4）以及平台 Infra MCP 服务。
2. **双集群独立部署轻量采集探针**：SIT 与 PROD 各自部署轻量级 `observability-agent`（Chart `1.2.1+5c4fb411cffa`），管理各环境 10 个核心业务服务探测目标（Console, Accounts, Billing），并负责宿主机节点、进程、Kubernetes 状态及 Traefik/PostgreSQL 指标采集。
3. **域名收敛与认证切流**：将公共入口 `observability.svc.plus` 权威 DNS 由 PROD 平滑切换至 SIT；所有写入与查询均通过 `vmauth` 经由外部 Vault JWT 角色和短期动态凭据完成严格双向鉴权。
4. **PROD 旧观测服务端与 Infra MCP 安全退役**：在跨集群指标流入、Flagger 灰度分析以及 Grafana 仪表盘全量验收后，通过 GitOps 声明式停用并分步骤优雅缩容 PROD 旧服务端，底层持久卷（PV）策略锁定为 `Retain`，零数据丢失。

---

## 一、全链路交付与执行状态汇总

| 阶段 / 检查项 | 目标与规范要求 | 线上实际状态 / 验收证据 | 状态 |
| :--- | :--- | :--- | :---: |
| **1. 凭据与权限** | Vault JWT Role 绑定两集群 ServiceAccount，只读读取 `CICD/observability` | SIT/PROD `observability-ingest-reader` / `observability-query-reader` 角色生效，ESO Secret `Ready` | **PASS** |
| **2. SIT 共享入口** | `shared-observability-tls` 证书挂载，vmauth 反代指标/日志/链路 | `*.svc.plus` Let's Encrypt 证书有效；未认证访问报 `401 Unauthorized`；认证访问 `200 OK` | **PASS** |
| **3. GitOps PR 合并** | PR #844、PR #845、PR #848 分步交付与 CI 门禁检查 | 合并至 `main`（HEAD `288fa22`），两端 Flux 自动同步生效 | **PASS** |
| **4. 权威 DNS 切流** | `observability.svc.plus` A/CNAME 切至 SIT (`172.237.9.58`) | 公共 DNS (`1.1.1.1` / `8.8.8.8`) 均解析至 `172.237.9.58`，保留回退锚点 `observability-selfhost-prod-v6` | **PASS** |
| **5. 双集群独立探针** | 双集群 `observability-agent` Chart 1.2.1，各 10 项 Release 探针 | SIT 与 PROD 各 10 个探针全部采样到达，`probe_success` 全部为 1 | **PASS** |
| **6. Flagger 与跨集群指标** | PROD Flagger 认证查询 SIT 端点，Traefik 请求样本采集与错误率计算 | 认证查询 `https://observability.svc.plus` 成功；PROD Traefik 93 条时序连续写入 SIT；Canary 状态 `Succeeded` | **PASS** |
| **7. PROD 旧服务端退役** | GitOps 挂起旧 Release，分步平滑回收 Pod，保持 PVC Retain | GitOps `spec.suspend: true`；PV 策略置为 `Retain`；旧服务端 6 项 Deployment 优雅缩容至 0 | **PASS** |

---

## 二、关键验证证据

### 1. 双集群独立探针验收数据 (SIT VictoriaMetrics 实测)

双集群各自运行 `observability-agent`，独立通过 Blackbox Exporter 执行探测并由 `vmagent` 写入 SIT VictoriaMetrics。

#### SIT 集群 (`cluster="SIT-K3S-V6"`, `environment="sit"`)
- **健康探针统计**：`count(probe_success{cluster="SIT-K3S-V6"} == 1)` = **`10`**
- **探测目标明细**：
  1. `http://web-saas-console.web-saas-sit.svc/healthz` (Status: 200, Module: release_http_ok)
  2. `http://web-saas-console.web-saas-sit.svc/login` (Status: 200, Module: release_http_ok)
  3. `http://web-saas-console.web-saas-sit.svc/panel/agent` (Status: 307, Module: release_login_redirect)
  4. `http://web-saas-accounts.web-saas-sit.svc/healthz` (Status: 200, Module: release_http_ok)
  5. `http://web-saas-accounts.web-saas-sit.svc/readyz` (Status: 200, Module: release_http_ok)
  6. `http://web-saas-accounts.web-saas-sit.svc/api/ping` (Status: 200, Module: release_http_ok)
  7. `http://web-saas-accounts.web-saas-sit.svc/api/billing/plans` (Status: 200, Module: release_http_ok)
  8. `http://web-saas-billing.web-saas-sit.svc/healthz` (Status: 200, Module: release_http_ok)
  9. `http://web-saas-billing.web-saas-sit.svc/readyz` (Status: 200, Module: release_http_ok)
  10. `http://web-saas-billing.web-saas-sit.svc/api/ping` (Status: 200, Module: release_http_ok)

#### PROD 集群 (`cluster="PROD-K3S-V6"`, `environment="prod"`)
- **健康探针统计**：`count(probe_success{cluster="PROD-K3S-V6"} == 1)` = **`10`**
- **跨集群写入链路**：PROD `vmagent` 经由公网通过 HTTPS 及 Basic Auth（`observability` 凭据）写入 SIT 端点 `https://observability.svc.plus/ingest/metrics/api/v1/write`。
- **探测目标明细**：
  1. `https://console.svc.plus/healthz` (Status: 200, Module: release_http_ok)
  2. `https://console.svc.plus/login` (Status: 200, Module: release_http_ok)
  3. `https://console.svc.plus/panel/agent` (Status: 307, Module: release_login_redirect)
  4. `https://accounts.svc.plus/healthz` (Status: 200, Module: release_http_ok)
  5. `https://accounts.svc.plus/readyz` (Status: 200, Module: release_http_ok)
  6. `https://accounts.svc.plus/api/ping` (Status: 200, Module: release_http_ok)
  7. `https://accounts.svc.plus/api/billing/plans` (Status: 200, Module: release_http_ok)
  8. `https://billing.svc.plus/healthz` (Status: 200, Module: release_http_ok)
  9. `https://billing.svc.plus/readyz` (Status: 200, Module: release_http_ok)
  10. `https://billing.svc.plus/api/ping` (Status: 200, Module: release_http_ok)

---

### 2. PROD 全量指标汇聚与 Flagger 验收数据

#### PROD Agent 采集时序持续写入 SIT
通过在 `services/prod-k3s-v6/observability-prod/agent-release.yaml` 中配置 `vmagent.scrapeConfigs`，PROD 的核心业务与系统时序全量流入 SIT 共享存储：
- `traefik_service_requests_total`: **93 series**（包含 Primary 与 Canary 流量）
- `node-exporter`: **1,986 series**
- `kube-state-metrics`: **3,100 series**
- `process-exporter`: **1,841 series**
- `postgres-exporter`: **2,829 series**

#### Flagger 认证查询与 Canary 分析验证
- **鉴权配置**：PROD `web-saas-prod` 命名空间下的 `traefik-error-rate` MetricTemplate 配置指向 `https://observability.svc.plus`，通过 ExternalSecret `observability-query-auth` 自动从 Vault 注入认证。
- **实际查询验证**：
  从 PROD 宿主机直接调用鉴权接口，实测返回值如下：
  ```bash
  # 查询账户服务金丝雀错误率
  query: (100 - (sum(rate(traefik_service_requests_total{exported_service=~"web-saas-prod-web-saas-accounts-canary-80(@kubernetescrd)?",code!~"5.*"}[2m])) / sum(rate(traefik_service_requests_total{exported_service=~"web-saas-prod-web-saas-accounts-canary-80(@kubernetescrd)?"}[2m]))) * 100) or vector(0)
  # 返回: value: 0 (错误率 0%)

  # 查询主本实时请求速率
  query: sum by (exported_service) (rate(traefik_service_requests_total{exported_service=~"web-saas-prod.*"}[2m]))
  # 返回: 
  # web-saas-prod-web-saas-accounts-primary-80@kubernetescrd: ~0.97 req/s
  # web-saas-prod-web-saas-console-primary-80@kubernetescrd:  ~0.17 req/s
  ```
- **PROD Canary 运行状态保持正常**：
  ```
  NAMESPACE       NAME                STATUS      WEIGHT   LASTTRANSITIONTIME
  web-saas-prod   web-saas-accounts   Succeeded   0        2026-11-07T11:28:02Z
  web-saas-prod   web-saas-console    Succeeded   0        2026-11-07T11:30:12Z
  ```

---

### 3. 业务服务与公共 HTTPS 状态

生产与观测入口经全球 DNS 校验，全部保持 HTTPS/2 200 正常响应：
```
https://console.svc.plus/healthz       -> HTTP 200
https://accounts.svc.plus/healthz      -> HTTP 200
https://billing.svc.plus/healthz       -> HTTP 200
https://observability.svc.plus/login   -> HTTP 200 (SIT Grafana v13.2.4，内置 25 套生产仪表盘)
```

---

### 4. Grafana 凭据与 Vault 契约同步记录

- **Vault KV Path**：`kv/data/CICD/observability/grafana-admin`
- **Secret 字段**：`grafana_password`
- **管理员用户**：`admin`
- **密码**：`a4h3ljbn`
- **故障排查与对齐**：
  - 现象：切流后访问 `https://observability.svc.plus/login`，输入习惯密码 `a4h3ljbn` 提示 `Invalid username or password`。
  - 原因：SIT 初始搭建阶段在 SQLite/PVC 内初始化了临时随机密码，未挂载 Vault 同步。
  - 修复：通过内部管理 API 将数据库内 `admin` 密码对齐重置为 `a4h3ljbn`，并同步更新 SIT `grafana-admin` Kubernetes Secret。
  - 验证：调用 API 验证返回 `{"message":"Logged in","redirectUrl":"/"}`，浏览器端认证恢复正常。

---

## 三、PROD 旧服务端退役与资源留存情况

为防止资源抢占并彻底收敛监控端点，在完成上述验收后对 PROD 旧服务端进行分步骤安全回收：

### 1. GitOps 声明式停用
在 `services/prod-k3s-v6/observability-prod/helmrelease.yaml` 中合并提交：
```yaml
spec:
  suspend: true
```
PR #848 已合并至主干。FluxCD 已停止该 Release 的生命周期调谐。

### 2. 底层存储安全性 (PV Retain)
- PROD 旧服务端绑定的持久化卷：
  `pvc-15d8a4da-4dce-4c33-be2a-c7d7e3c4b252`（20Gi local-path）
- **持久化策略加锁**：
  已将 PV 的 `persistentVolumeReclaimPolicy` 显式由 `Delete` 修改为 **`Retain`**。
- **物理数据状态**：
  宿主机物理目录 `/data/k3s/storage/pvc-15d8a4da-4dce-4c33-be2a-c7d7e3c4b252_observability-prod_observability-observability-stack-data` 完好无损保留，可作为历史审计与瞬时恢复底座。

### 3. 旧服务端 Pod 优雅回收
已通过优雅缩容命令回收 PROD 旧服务端负载：
- `observability-observability-stack-grafana` $\rightarrow$ 0 副本
- `observability-observability-stack-otel-collector` $\rightarrow$ 0 副本
- `observability-observability-stack-victoria-traces` $\rightarrow$ 0 副本
- `observability-observability-stack-victoria-logs` $\rightarrow$ 0 副本
- `observability-observability-stack-victoria-metrics` $\rightarrow$ 0 副本
- `observability-ingest-auth` $\rightarrow$ 0 副本

PROD 的 `observability-prod` 命名空间下当前处于纯净探针运行态：
```
NAME                                            READY   STATUS    RESTARTS   AGE
observability-agent-blackbox-8644464dd5-7t6j6   1/1     Running   0          25m
observability-agent-n5zww                       1/1     Running   12         6d13h
observability-agent-process-8skfq               1/1     Running   0          4d16h
observability-agent-state-5857d98bf6-zd5qn      1/1     Running   0          8m
observability-agent-vmagent-7b5db89979-7tfbj    1/1     Running   0          7m
```

---

## 四、回退指引 (Rollback Runbook)

如遇重大灾备或跨云链路异常，可使用以下固化的回退基线：

### 1. DNS 瞬时回退
在 Cloudflare 将 `observability.svc.plus` CNAME 指向保留的锚点：
- 目标：`observability-selfhost-prod-v6.svc.plus`（权威 IP：`172.237.24.232`）。
- PROD 端的 TLS 证书与 Ingress 路由保持就绪状态。

### 2. PROD 服务端快速拉起
在 GitOps 仓库将 `services/prod-k3s-v6/observability-prod/helmrelease.yaml` 的 `spec.suspend` 恢复为 `false`。Flux 自动调谐后，各组件将基于已保留的 20Gi 数据卷就地恢复所有时序历史。

### 3. Agent 探针版本回退
如遇 Agent 异常，可将 `agent-release.yaml` 回退至前序固定 OCI 摘要：
- Chart Digest: `sha256:4095ed924194c7a91aaa2ad00dd21cec3ccfdcd4c342951ac95aec56fe041f12`（Chart 1.1.5）。

### 4. Flagger 指标源回退
若外部查询受阻，可直接将 PROD Canary 的 MetricTemplate `address` 切回本地：
- `http://observability-observability-stack-victoria-metrics.observability-prod.svc:8428`
