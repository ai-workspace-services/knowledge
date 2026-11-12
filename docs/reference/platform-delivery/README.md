# 平台交付与节点运维文档

本目录汇集专项参考文档、跨组件总体架构、双轨可观测性规范以及代际集群交付手册。规划和目标图不代表代码已实现或线上已验收；运行状态以各文档标注的观察时间、GitOps 提交哈希与实际集群回执为准。

> [!IMPORTANT]
> **核心交付归档与白皮书**：
> - 📋 [**Hand-Off 交付与交接报告 (终态完整版)**](Hand-Off-交付与交接报告-终态完整版.md)：全量架构对齐、SIT 与 PROD 双集群 DataKit / VictoriaMetrics 修复回执、标准仪表盘调试及异构时序映射。
> - 📘 [**Web Console 前端全量路由与后端微服务 API 目录统计白皮书**](Web-Console-前端全量路由与后端微服务-API-目录统计白皮书.md)：181 项全量监控资产收敛（65 前端页面路由 7 大类 + 116 后端微服务 API 8 大类）、三级树状分组架构规范、Flagger 渐进发布与门禁联动（0/1/2 状态映射、Billing 未配置金丝雀 Not configured 规范、双色加权流量切分条）以及 VictoriaMetrics 动态遥测接入规范。

---

## 目录分层架构 (Subdirectory Structure)

```
docs/reference/platform-delivery/
├── README.md                                             # 平台交付索引与总体导航
├── Hand-Off-交付与交接报告-终态完整版.md                   # 双集群全量交付与交接总报告
├── Web-Console-前端全量路由与后端微服务-API-目录统计白皮书.md # 181 项全量监控资产、三级树状架构、Flagger金丝雀与动态遥测白皮书
├── architecture/                                         # 基础运行环境、身份契约与统一交付架构
├── observability/                                        # 可观测性、Grafana 面板、观测云双轨与 MetricMap
├── clusters/                                             # 节点与集群环境独立归档
│   ├── prod-k3s-v6/                                      # 生产集群 (PROD-K3S-V6) 专属规划与运行手册
│   └── sit-k3s-v6/                                       # 测试集群 (SIT-K3S-V6) 特性泳道与乐高架构
└── agent-delivery/                                       # AI 协同接力、向量归档与网络边界试点
```

---

## 一、总体架构与基础契约 (`architecture/`)

| 文档名称 | 核心内容与技术边界 |
| :--- | :--- |
| [OpenplatForm Delivery Architecture](architecture/OpenplatForm-Delivery-Architecture.md) | 基础运行环境、统一架构拓扑图、多环境发布演进与安全边界。 |
| [通用 Vault 工作负载身份契约](architecture/通用-Vault-工作负载身份契约.md) | 外部 Vault、ESO 与业务工作负载间的身份认证、Secret 声明与跨集群迁移设计。 |
| [Linux OS 三类操作身份：最小实施草案](architecture/Linux-OS三类操作身份-最小实施草案.md) | `root`、`operator`、`auditor` 三权分立运维账号权限模型与安全基线。 |
| [环境与业务发布解析：最小实施草案](architecture/环境与业务发布解析-最小实施草案.md) | 环境分层语义、域名解析策略与业务发布规范。 |
| [GitHub Actions 流水线实施草案](architecture/GitHub-Actions流水线实施草案.md) | CI/CD 流水线编排规范与自动化质量门禁。 |
| [K3s role 职责与依赖清单](architecture/K3s-role职责与依赖清单.md) | Ansible K3s 角色拆分、输入变量定义与依赖矩阵。 |

---

## 二、中央监控与可观测性体系 (`observability/`)

本模块覆盖权威源 VictoriaMetrics（`https://observability.svc.plus`）与观测云（Guance Cloud）双轨指标采集、时序映射、面板规范与租户隔离设计。

| 文档名称 | 核心内容与技术边界 |
| :--- | :--- |
| [**Web Console 前端全量路由与后端微服务 API 目录统计白皮书**](Web-Console-前端全量路由与后端微服务-API-目录统计白皮书.md) | **【资产与发布白皮书】** 181 项全量监控资产（65 前端路由 7 大类 + 116 后端 API 8 大类）系统收敛梳理、前端/后端/大类/子组件三级树状分组架构规范、Flagger 金丝雀发布与门禁联动（0/1/2 映射、Billing 未配置金丝雀 Not configured 规范、双色流量切分条）及 VictoriaMetrics 动态遥测接入规范。 |
| [**DataKit 跨云可观测性与 OpenTelemetry 数据网关交付白皮书**](observability/DataKit跨云可观测性与OpenTelemetry数据网关交付白皮书.md) | **【体系白皮书】** 双轨可观测性战略定位、Vault KV v2 路径按 `observability` 领域类别极致收敛（`observability/datakit/bj-free` vs `observability/datakit/hk-commercial`）、Playbook/GitOps 动态无缝切换契约、4 大 Prometheus 端点实盘采集与 OpenTelemetry 数据网关接入规范。 |
| [**SIT-K3S-V6 VictoriaMetrics 到观测云双轨采集与 MetricMap 映射交付手册**](observability/SIT-K3S-V6-VictoriaMetrics到观测云双轨采集与MetricMap映射交付手册.md) | **【核心交付】** 权威源 VictoriaMetrics 与观测云 MetricMap 链路映射总览、DataKit 4 大 Target 抓取规范、GitOps/Playbook 幂等交付及免费额度超限（`kodo.beyondDataUsage`）诊断手册。 |
| [**SIT 共享观测与双集群探针交接及 PROD 旧服务端退役验收报告**](observability/SIT共享观测与双集群探针交接及PROD旧服务端退役验收报告.md) | **【验收报告】** SIT 共享观测服务端与双集群探针全链路交接验收，权威 DNS 切流、PROD 全量指标汇聚、Flagger 金丝雀认证查询、Grafana 凭据同步与 PROD 旧服务端无损退役运行回执。 |
| [21个 Grafana 面板数据流检查与修复验收报告](observability/21个Grafana面板数据流检查与修复验收报告.md) | 21 个 Grafana 核心面板的数据流校验、图表指标源梳理与修复验收回执。 |
| [Antigravity：21个 Grafana 面板数据流检查与修复提示词](observability/Antigravity-21个Grafana面板数据流检查与修复提示词.md) | Agent 自动化修复与数据流逐 Panel 核验工程提示词。 |
| [Grafana 独立 PostgreSQL 与 GitOps 持久化规划](observability/Grafana独立PostgreSQL与GitOps持久化规划.md) | 共享业务 PostgreSQL 实例、独立 `grafana` 数据库、生命周期与 GitOps 持久化配置。 |
| [Grafana 租户隔离与 Portal 嵌入规划](observability/Grafana租户隔离与Portal嵌入规划.md) | 客户组织隔离、数据源白名单、Portal JWT 同源单点登录与防跨租户越权。 |
| [Grafana 面板丢失排查与恢复规划](observability/Grafana面板丢失排查与恢复规划.md) | V5（21面板）与 V6 差异核验、UID 恢复、ConfigMap 声明与现场检查。 |
| [Pro Custom 与 Grafana 升级完整规划](observability/Pro-Custom与Grafana升级完整规划.md) | Pro Custom 专项架构决策、固定源码证据与四页面集成规划。 |
| [Pro Custom 专属资源工作台规划](observability/Pro-Custom专属资源工作台规划.md) | 功能边界、权益配额、创建任务与 Grafana 快捷入口。 |
| [Pro Custom 与 Grafana 分阶段交付验收规划](observability/Pro-Custom与Grafana分阶段交付验收规划.md) | 阶段依赖矩阵、验收标准、回退方案与多阶段里程碑。 |
| [PROD-K3S-V6 ServiceLB、Caddy 与 Datakit 修复提示词](observability/PROD-K3S-V6-ServiceLB-Caddy与Datakit修复提示词.md) | 历史生产现场 ServiceLB 穿透、Caddy 外部接入与 DataKit OOM 排障参考。 |

---

## 三、集群环境专项 (`clusters/`)

### 1. 生产集群 (`clusters/prod-k3s-v6/`)
- [PROD-K3S-V6 独立节点、集群冷启动规划与部署状态归档](clusters/prod-k3s-v6/PROD-K3S-V6-规划与部署状态归档.md) — 节点规格、持久化卷规划、集群冷启动与运行状态基线归档。
- [PROD-K3S-V6 用户迁移操作手册](clusters/prod-k3s-v6/PROD-K3S-V6-用户迁移操作手册.md) — 生产环境用户数据单向迁移、数据库初始化与割接验证。
- [PROD-K3S-V6 Accounts 迁移 API 单向同步规划](clusters/prod-k3s-v6/PROD-K3S-V6-Accounts迁移API单向同步规划.md) — 账户系统数据单向同步接口契约与网关限制。

### 2. 测试集群 (`clusters/sit-k3s-v6/`)
- [SIT-K3S-V6 模块化交付与特性泳道规划](clusters/sit-k3s-v6/SIT-K3S-V6-模块化交付与特性泳道规划.md) — 模块化乐高交付体系、免本地 Vault Server 设计，支持 Feature $\rightarrow$ SIT 特性泳道持续验证。
- [SIT-K3S-V6 换机重部署与 DNS 切换手册](clusters/sit-k3s-v6/SIT-K3S-V6-换机重部署与DNS切换手册.md)。涵盖 SSH 预检、Playbooks 引导、Flux 接管、空环境验收及 DNS 回退。

---

## 四、AI 协同与边界试点 (`agent-delivery/`)

- [XConnect Agent 配置收敛与 Free 临时白名单规划](agent-delivery/XConnect-Agent配置收敛与Free临时白名单规划.md) — 三仓实施范围、零 SQL schema 改动、五字段兼容、五类节点验收与回滚。
- [本机 QMD 跨 Code APP 接力与 Knowledge 向量归档](agent-delivery/本机QMD跨CodeAPP接力与Knowledge向量归档.md) — 本机任务状态持久化、跨会话 Agent 接力、Ollama 向量计算与归档验收。
- [XConnect 日本 HAProxy 试点规划草稿](agent-delivery/XConnect-日本HAProxy试点规划草稿.md) — 边缘节点反向代理与连接优化草案。
