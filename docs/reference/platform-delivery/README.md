# 平台交付与节点运维文档

本目录汇集专项参考文档和跨组件总体架构。规划和目标图不代表代码已实现或线上已验收；运行状态以各文档标注的观察时间和回执为准。

**当前 V6 运行与复盘状态（2026-11-03）：** V5 → V6 迁移、K3s 平台故障修复与 canonical DNS 切换已全部完成，最新基线与复盘详见 [PROD V5 → V6 部署架构演进与复盘总述](../../../content/02-iac-devops/cloud-infrastructure-devsecops-baseline/18-prod-v5-v6-deployment-and-migration-retrospective.zh.md) 及 [V5-V6 归档记录库](../../../content/02-iac-devops/cloud-infrastructure-devsecops-baseline/records/prod-v5-v6-20261103/README.md)。原 [V6 最新状态与偏差清单](PROD-K3S-V6-规划与部署状态归档.md) 保留作为历史时点归档。生产环境沿用 Ansible Playbooks + GitOps + Flux、Caddy + K3s ServiceLB，四个 Web SaaS 应用均平稳运行（0 重启），Datakit OOM 已通过资源扩容解决，JP 及 US 边缘 Agent 均已恢复接入，用户登录态页面可见性已获确认。剩余未决事项（如审计身份 Secret 读取授权收敛、PostgreSQL 原生公网探测）由复盘验收矩阵跟踪。

## 总体架构

- [OpenplatForm Delivery Architecture](OpenplatForm-Delivery-Architecture.md) — 基础运行环境、统一架构图、多环境发布、观测与安全边界。

## Pro Custom 工作台与 Grafana 升级规划（2026-11-03）

本组先交付独立文档，完整记录用户确认的方案；尚未执行面板恢复、数据库迁移或客户功能上线。上文 V6 基础服务和入口切换完成，不代表本专项的 Grafana 面板完整性或租户隔离已验收。需求与文档交付由 [Knowledge #351](https://github.com/ai-workspace-services/knowledge/issues/351) 跟踪。

后续现场与修复（2026-11-03）：V5 保留 21 个面板、V6 原为 0，已由 [GitOps #775](https://github.com/ai-workspace-infra/gitops/pull/775) 恢复全部 21 个 UID，并经公网登录态 API 核对；部分代表指标仍为空，完整图表数据及客户隔离未验收。PostgreSQL 方案已澄清为可共用业务实例、独立 `grafana` 数据库与账户。见[恢复回执](Grafana面板丢失排查与恢复规划.md#75-随后执行的最小恢复与结果)。

| 文档 | 内容 |
| --- | --- |
| [完整规划总述](Pro-Custom与Grafana升级完整规划.md) | 完整保留决策、V5/V6 固定源码证据、存储分层、GitOps、恢复、隔离、四页面及验收 |
| [Pro Custom 专属资源工作台](Pro-Custom专属资源工作台规划.md) | 功能边界、权益与归属、创建任务、资源列表、Grafana 入口和密钥占位 |
| [Grafana 独立 PostgreSQL 与 GitOps 持久化](Grafana独立PostgreSQL与GitOps持久化规划.md) | 可共用业务 PostgreSQL 实例、独立 grafana 数据库与账户，数据生命周期、发布、备份和 SQLite 迁移 |
| [Grafana 面板丢失排查与恢复](Grafana面板丢失排查与恢复规划.md) | 声明与现场差异：V5 保留 21 个 Dashboard，V6 为 0；迁移缺项、恢复来源和运行验收 |
| [Grafana 租户隔离与 Portal 嵌入](Grafana租户隔离与Portal嵌入规划.md) | 客户组织、受限数据源、指标归属、同源认证和跨租户拒绝测试 |
| [分阶段交付与验收](Pro-Custom与Grafana分阶段交付验收规划.md) | 仓库 owner、阶段依赖、验收矩阵、回执、观察与回退 |

## 专项参考

1. [环境与业务发布解析：最小实施草案](环境与业务发布解析-最小实施草案.md)
2. [GitHub Actions 流水线实施草案](GitHub-Actions流水线实施草案.md)
3. [Linux OS 三类操作身份：最小实施草案](Linux-OS三类操作身份-最小实施草案.md)
4. [K3s role 职责与依赖清单](K3s-role职责与依赖清单.md)
5. [PROD-K3S-V6 独立节点、集群冷启动规划与部署状态归档](PROD-K3S-V6-规划与部署状态归档.md)
6. [通用 Vault 工作负载身份契约](通用-Vault-工作负载身份契约.md) — 外部 Vault、ESO 和工作负载之间的身份、Secret 引用与跨集群迁移设计。

前五份专项参考来源于 `ai-workspace-infra/docs` 的 `archives/2026-10-30`；其中流水线草案与 V6 状态归档包含归档时尚未提交的工作树更新。K3s role 清单中的日期和运行状态反映其原始记录；当前 V6 状态以 V6 归档中最新核对条目为准。

## 当前执行交接与代际演进

- [本机 QMD 跨 Code APP 接力与 Knowledge 向量归档](本机QMD跨CodeAPP接力与Knowledge向量归档.md) — 本机免密任务读写、同一线程接力、Ollama embedding 和归档后检索验收。

- [Antigravity：21 个 Grafana 面板数据流检查与修复提示词](Antigravity-21个Grafana面板数据流检查与修复提示词.md) — 三个 Agent Proxy 与 V6、五组 sub-agent、Dashboard 模型保护、逐 panel 数据验收及 Knowledge → QMD 归档检索流程。

- [PROD V5 → V6 复盘与演进总述](../../../content/02-iac-devops/cloud-infrastructure-devsecops-baseline/18-prod-v5-v6-deployment-and-migration-retrospective.zh.md) — 总体叙事、架构对照、三幅拓扑图与复盘经验。
- [控制面代际迁移标准化运行手册](../../../content/02-iac-devops/cloud-infrastructure-devsecops-baseline/records/prod-v5-v6-20261103/migration-runbook.zh.md) — 标准化 7 阶段迁移与恢复操作手册。
- [V6 ServiceLB、Caddy 与 Datakit 修复提示词](PROD-K3S-V6-ServiceLB-Caddy与Datakit修复提示词.md) — 历史现场排障参考。
