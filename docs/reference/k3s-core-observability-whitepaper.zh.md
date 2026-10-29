---
title: K3s 基础与核心业务监控白皮书
description: 集群基础监控、入口探测、Caddy 和 PostgreSQL 的采集架构、标签、验收与生产复盘。
slug: k3s-core-observability-whitepaper
lang: zh
tags: [observability, k3s, victoriametrics, grafana, blackbox, caddy, postgresql, gitops]
---

# K3s 基础与核心业务监控白皮书

> 状态：实施复盘与目标方案；运行态证据截至 2026-10-29 15:25（Asia/Shanghai），会随部署变化。本文不是生产验收证明。

## 1. 目标和边界

以集群基础监控定位资源与工作负载问题，以三个业务入口回答可用性问题：Blackbox 检查证书和入口，Caddy exporter 检查入口处理，PostgreSQL exporter 检查数据库。指标、日志、链路共同支持排障，但 Pod Running、HTTP 200 或 pg_up=1 均不能单独证明业务流程成功。

自建链路由 vmagent 负责指标抓取和写入 VictoriaMetrics，Vector 负责日志并写入 VictoriaLogs，追踪由实际接入的追踪采集器写入 VictoriaTraces，Grafana 查询自建数据源。DataKit 是观测云 SaaS 的辅助采集与上报链路；自建 Victoria 全家桶与观测云服务端独立，互不回写或同步。按实际数据源和指标边界避免重复采集，不能仅凭图示认定双端均已收数。

## 2. 环境和标签

| 用途 | environment | cluster 目标值 | 事实与差异 |
| --- | --- | --- | --- |
| PROD | `prod` | `prod-k3s-v5` | PostgreSQL 和手动部署的探测已使用目标标签；既有节点、Caddy 仍为 `web-saas-k3s-v5`。 |
| SIT | `sit` | `dev-k3s-v5` | SIT 节点实际名 `dev-k3s-v5`；中央数据源的 SIT 指标尚未验证。 |

`environment`、`cluster`、`service`、`instance` 用于级联与隔离；PostgreSQL 的 `datname` 用于数据库层级。节点名、Service DNS、机器 ID 与集群标签是不同字段，不应相互覆盖。生产节点当前报告的 hostname 为 `localhost`，不等于集群标签或服务名。Dashboards 以数据源 → 环境 → 集群 → 服务 → 实例 → 数据库（适用时）级联，变量查询及面板查询均按同一标签范围过滤。历史时序不会因为标签调整自动改写。

## 3. 集群基础监控

节点侧覆盖 CPU、内存、磁盘、文件系统、网络及进程；Kubernetes 侧覆盖节点状态、Pod 与容器状态、资源请求/限制、CPU、内存、重启和工作负载就绪。典型数据源包括 node-exporter、process-exporter、kube-state-metrics、kubelet/cAdvisor。`kube_node_info`、`kube_pod_info` 和 `container_cpu_usage_seconds_total` 用于确认采集、标签和新鲜度；业务容器指标存在不代表应用自身业务指标已接入。

验收同时检查发现目标、`up`、最新采样时间和 Dashboard 变量；`up=1` 只是抓取成功，不能替代服务健康。资源指标必须限定环境、集群、命名空间、Pod 和容器，避免多个集群的同名对象混合。

## 4. 三类核心业务监控

| 能力 | 关注项 | 典型指标 | 验收要求 |
| --- | --- | --- | --- |
| Blackbox：证书和入口 | DNS/TCP/TLS、证书有效期、HTTP 状态和耗时 | `probe_success`、`probe_http_status_code`、`probe_ssl_earliest_cert_expiry` | 为每个目标定义协议、路径和预期状态；探测失败保持失败，不转换为零或成功。 |
| Caddy：入口处理 | 入口流量、状态码、错误、配置加载和处理时延 | `caddy_http_requests_total` 及实际导出的错误/延迟指标 | 验证 exporter 端点、标签和最近采样；单独检查反向代理后端与用户路径。 |
| PostgreSQL：数据库 | 实例连通性、连接数、TPS、事务回滚、缓存、数据库容量、死锁和冲突 | `pg_up`、`pg_stat_database_numbackends`、`pg_stat_database_xact_commit`、`pg_database_size_bytes` | exporter 使用独立监控账号；验证可登录、状态指标、权限与采样新鲜度。 |

Blackbox 的 HTTP 探测必须使用经服务 owner 确认的健康路径与预期状态。`/` 返回 404 只说明根路径不满足当前 2xx 探测，不能单独断言整个服务不可用。证书时间指标需检查目标和阈值；TCP/TLS 探测与 PostgreSQL 协议连通性也不是同一个结论。

Caddy 面板按数据源 → 环境 → 集群 → 服务 → 实例过滤。反向代理数据不等同于应用内部成功率；如服务提供业务指标，应额外接入，不将其伪装成 Caddy 指标。

PostgreSQL 统一面板包含摘要、详细指标和连接/数据库大小样本分布热力图；这些热力图不是请求延迟分布。事务提交与回滚之和是 TPS，不是 SQL QPS。数据库名范围只用于数据库级指标；`pg_up`、bgwriter 等实例级指标不应受数据库选择器误过滤。PostgreSQL 17 部分旧 bgwriter 时序与 checkpointer 统计口径发生变化：当前生产 exporter 未观察到部分旧指标或 checkpointer 序列，面板应显示无数据，不得伪造为零。新增采集器应先核实版本、权限与语义。

## 5. 2026-10-29 运行态复盘

以下为当时的只读查询快照，不代表当前实时状态：

| 项目 | 观察结果 | 边界 |
| --- | --- | --- |
| PROD 基础 | `kube_node_info` 有数据；集群标签仍为 `web-saas-k3s-v5`。 | 不证明 SIT 上报或目标标签已统一。 |
| PROD Caddy | `caddy_http_requests_total` 有数据；集群标签仍为 `web-saas-k3s-v5`。 | 环境级 Dashboard 和业务端到端验收另行验证。 |
| PROD PostgreSQL | `pg_up=1`，标签 `environment=prod`、`cluster=prod-k3s-v5`、`service=postgresql`；`account` 连接数及容量指标有数据。 | 账号表级写权限自省无命中，其他数据库、函数及真实拒绝测试未完成，不能声称审计隔离全面通过。 |
| PROD Blackbox | Console、Observability、品牌站目标为 1；Accounts `/`、Billing `/` 和 PostgreSQL TLS tunnel 当前为 0。 | Accounts/Billing 根路径返回 404；需确认健康路径；TLS tunnel 需单独诊断。 |
| SIT | 中央 VictoriaMetrics 未观察到 SIT 节点指标；SIT 线上 Flux 根固定旧提交，监控子资源仍指向 DataKit 子目录。 | DataKit 运行与中央 VictoriaMetrics 收数是两项独立证据；功能环境数据库不可直接当成正式 SIT 数据库。 |
| Flux | `platform-observability-prod` 仍由 `platform-config-prod` 的 `v2026.10.28.5` 管理；独立监控 Source 已创建并 Ready。 | 独立来源存在不等于监控 Kustomization 已交接或新面板已由 Flux 管理。 |
| Dashboard | 统一 PostgreSQL 面板曾通过 Grafana API 确认存在；变量转义导致 422 的修复及中文说明已进入 PR。 | 手动导入与 Grafana 渲染验收、SIT 选择及 Flux 持续管理分别验证。 |

**后续修复记录：**同日约 15:28，经核对 Accounts `/healthz` 与 Billing `/readyz` 是实际探测路径，已手动更新 vmagent 配置；VictoriaMetrics 对这两个新目标均观察到 `probe_success=1`。旧根路径历史时序可能暂时仍可见；PostgreSQL TLS tunnel 的失败仍待诊断。此路径修复尚未纳入 Flux。

PROD 的 vmagent、blackbox、postgres-exporter、数据库账号与新增网络策略曾通过 SSH 手动建立；应尽快纳入受审查的 GitOps 和凭据生命周期管理，并核查无重复抓取。不要把手动资源、PR 合并或 Kustomize 渲染写成自动交付验收。

## 6. 安全与网络

系统管理、业务运行和审计监控分离。Exporter 使用独立数据库监控账号，不复用应用账号；不授予超级用户、建库、建角色、复制或绕过 RLS 权限。权限验收覆盖 PUBLIC、继承、其他数据库、函数和允许/拒绝证据；默认只读事务不替代权限约束。V5 的现有应用 `app` 超级用户权限是已知暂时例外，不代表监控账户可以复用。

监控凭据由受控密钥系统管理，GitOps 仅存引用；不把密码、DSN 或 token 写进仓库。PostgreSQL 的 NetworkPolicy 仅允许已确认的 exporter 身份访问 5432；exporter 的指标端点限定采集器访问。跨集群写入须验证 TLS、认证、网络策略、排队和失败告警。DataKit 权限及 hostNetwork 等既有例外需单独审查，不因采集正常就宣称符合三权分立。

## 7. 交付与验收

1. 将 exporter、采集配置、凭据引用和 NetworkPolicy 分别纳入相应仓库；对手动资源进行所有权交接，防止重复采集或被旧 Flux 根覆盖。
2. 生产监控使用可独立推进的 Flux 来源。比较根目录渲染与 inventory，保证业务、Vault、DataKit 未被意外推进或删除；升级前核对监控存储卷、容量、备份和回退。
3. SIT 核实独立采集器、中央 VictoriaMetrics 的受保护写入口和 DataKit 的 SaaS 路径；验证实际目标及 namespace，保留 `sit/dev-k3s-v5` 标签，不将 feature lane 冒充正式环境。
4. 四组指标（集群、Blackbox、Caddy、PostgreSQL）分别检查 `up`、指标值、新鲜度、标签和时间范围；再在 Grafana 实际选择 PROD 与 SIT，验证级联与每类面板。
5. 故障演练与回退以经授权的隔离环境为先；记录版本、时间、目标、变更、验证和回退，不对生产数据库执行破坏性拒绝测试。

## 8. 参考及交付记录

- [PostgreSQL 统一面板与 PromQL 修复：Playbooks #853](https://github.com/ai-workspace-infra/playbooks/pull/853)；[GitOps #656](https://github.com/ai-workspace-infra/gitops/pull/656)。
- [Caddy Dashboard 变量：GitOps #650](https://github.com/ai-workspace-infra/gitops/pull/650)。
- [PROD 独立监控来源：GitOps #652](https://github.com/ai-workspace-infra/gitops/pull/652)；[根交接覆盖：GitOps #653](https://github.com/ai-workspace-infra/gitops/pull/653)。实际源与协调状态须现场复核。
- [PostgreSQL exporter 官方 Mixin 固定版本](https://github.com/prometheus-community/postgres_exporter/blob/281cf032091aaaffded97f7df29b8ab29be051bd/postgres_mixin/dashboards/postgres-overview.json)；[PostgreSQL 17 统计视图](https://www.postgresql.org/docs/17/monitoring-stats.html)。
