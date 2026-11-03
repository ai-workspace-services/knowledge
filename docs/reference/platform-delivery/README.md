# 平台交付与节点运维文档

本目录汇集专项参考文档和跨组件总体架构。规划和目标图不代表代码已实现或线上已验收；运行状态以各文档标注的观察时间和回执为准。

**当前 V6 运行与复盘状态（2026-11-03）：** V5 → V6 迁移、K3s 平台故障修复与 canonical DNS 切换已全部完成，最新基线与复盘详见 [PROD V5 → V6 部署架构演进与复盘总述](../../../content/02-iac-devops/cloud-infrastructure-devsecops-baseline/18-prod-v5-v6-deployment-and-migration-retrospective.zh.md) 及 [V5-V6 归档记录库](../../../content/02-iac-devops/cloud-infrastructure-devsecops-baseline/records/prod-v5-v6-20261103/README.md)。原 [V6 最新状态与偏差清单](PROD-K3S-V6-规划与部署状态归档.md) 保留作为历史时点归档。生产环境沿用 Ansible Playbooks + GitOps + Flux、Caddy + K3s ServiceLB，四个 Web SaaS 应用均平稳运行（0 重启），Datakit OOM 已通过资源扩容解决，JP 及 US 边缘 Agent 均已恢复接入，用户登录态页面可见性已获确认。剩余未决事项（如审计身份 Secret 读取授权收敛、PostgreSQL 原生公网探测）由复盘验收矩阵跟踪。

## 总体架构

- [OpenplatForm Delivery Architecture](OpenplatForm-Delivery-Architecture.md) — 基础运行环境、统一架构图、多环境发布、观测与安全边界。

## 专项参考

1. [环境与业务发布解析：最小实施草案](环境与业务发布解析-最小实施草案.md)
2. [GitHub Actions 流水线实施草案](GitHub-Actions流水线实施草案.md)
3. [Linux OS 三类操作身份：最小实施草案](Linux-OS三类操作身份-最小实施草案.md)
4. [K3s role 职责与依赖清单](K3s-role职责与依赖清单.md)
5. [PROD-K3S-V6 独立节点、集群冷启动规划与部署状态归档](PROD-K3S-V6-规划与部署状态归档.md)
6. [通用 Vault 工作负载身份契约](通用-Vault-工作负载身份契约.md) — 外部 Vault、ESO 和工作负载之间的身份、Secret 引用与跨集群迁移设计。

前五份专项参考来源于 `ai-workspace-infra/docs` 的 `archives/2026-10-30`；其中流水线草案与 V6 状态归档包含归档时尚未提交的工作树更新。K3s role 清单中的日期和运行状态反映其原始记录；当前 V6 状态以 V6 归档中最新核对条目为准。

## 当前执行交接与代际演进

- [PROD V5 → V6 复盘与演进总述](../../../content/02-iac-devops/cloud-infrastructure-devsecops-baseline/18-prod-v5-v6-deployment-and-migration-retrospective.zh.md) — 总体叙事、架构对照、三幅拓扑图与复盘经验。
- [控制面代际迁移标准化运行手册](../../../content/02-iac-devops/cloud-infrastructure-devsecops-baseline/records/prod-v5-v6-20261103/migration-runbook.zh.md) — 标准化 7 阶段迁移与恢复操作手册。
- [V6 ServiceLB、Caddy 与 Datakit 修复提示词](PROD-K3S-V6-ServiceLB-Caddy与Datakit修复提示词.md) — 历史现场排障参考。
