# 云基础设施 DevSecOps 基线与代际演进目录索引 (PROD V2 - V5)

部署记录完整链路：[既有统一流程](https://github.com/ai-workspace-services/.github/blob/main/docs/control-plane-deployment-and-migration.zh.md) → [跨代基线、逐轮回执、专项故障、固定源码 case 与重验](records/generation-deployment-evidence-index-20261025.zh.md)。V5 VPS / Compose 与 V5 K3s PROD 独立采样；字段缺失、旧 OPEN PR 与新回执替代关系也在该证据索引中逐项列明。

## 1. 概述与代际演进规格

本目录归档 `cloud-infrastructure-devsecops-baseline` 系列核心文档，涵盖跨多云环境的 DevSecOps 底层基线、多云编排蓝图、OIDC 身份契约，以及生产环境全生命周期的代际演进（**PROD V2 → V3 → V4 → V5**）运行基线、快照证据、升级复盘与事故修复回执。

- **基础设施范围**：Akamai Cloud (Linode)、AWS、GCP、Cloudflare 及本地自建环境。
- **架构演进脉络**：
  - **V2**：单机高配容器化控制面（Caddy + Next.js Console + Accounts/Billing + PostgreSQL），确立不可变构件与增量迁移恢复基线。
  - **V2 → V3**：全量代际快照冷备、跨主机恢复与平滑切库演练，修复 SNI、服务 Token 与传输路由，建立故障归档机制。
  - **V3 → V4**：Console/Accounts/Billing 正式域名接流、品牌域名补齐、双链路 OTel 可观测性方案落地与 P0 回归测试集。
  - **V4 → V5**：净室全新环境部署验证、用户三轮幂等对账、前端路由修复、实时业务流量追加与修复后环境全量快照。
- **安全与对账准则**：所有代际升级与恢复严格遵循“单向数据流动、不可变快照存证、最小权限访问、零数据丢失”原则。

---

## 2. 通用架构基线与跨代际契约规范

收录通用于各代际的底层 DevSecOps 方法论、多云编排架构、OIDC 身份契约与单向数据晋级状态机。

| 编号 | 文档名称 / 标题 | 相对路径与链接 | 文档类型 | 核心范围与说明 |
| :---: | :--- | :--- | :---: | :--- |
| **01** | **云基础设施 DevSecOps 基线方法论** | [`09-cloud-infrastructure-devsecops-baseline-closing-the-loop.md`](09-cloud-infrastructure-devsecops-baseline-closing-the-loop.md) | 方法论基线 | 贯穿生命周期的安全长线，不可变构件与安全闭环原则 |
| **02** | **多云 Hybrid / Selfhost / Serverless 编排架构规划** | [`10-multi-cloud-orchestrator-architecture.zh.md`](10-multi-cloud-orchestrator-architecture.zh.md) | 架构规划 | 状态契约、环境分层（UAT/SIT/PROD）与编排控制面设计 |
| **03** | **多云身份 Bootstrap 与状态契约** | [`11-cloud-oidc-bootstrap-contract.zh.md`](11-cloud-oidc-bootstrap-contract.zh.md) | 操作契约 | Vault KV 与 GitHub Actions OIDC 对接规范，状态锁与免密发布 |
| **04** | **数据库同步与发布晋级状态机** | [`12-uat-database-sync-and-prod-promotion-state-machine.zh.md`](12-uat-database-sync-and-prod-promotion-state-machine.zh.md) | 状态机规范 | UAT 验证到 PROD 晋级六步状态流转，单向数据流动与门禁控制 |

---

## 3. PROD V2 阶段基线与实战复盘

聚焦单机容器化 Selfhost 架构下的冷备容灾、恢复模板与 7 重连环故障下的“零数据丢失”实战。

| 编号 | 文档名称 / 标题 | 相对路径与链接 | 文档类型 | 核心范围与说明 |
| :---: | :--- | :--- | :---: | :--- |
| **01** | **PROD V2 升级零数据丢失实战复盘** | [`13-prod-v2-upgrade-recovery-zero-data-loss-case.zh.md`](13-prod-v2-upgrade-recovery-zero-data-loss-case.zh.md) | 深度案例复盘 | 面对镜像 digest 错误、Schema 漂移等 7 重故障的 Code Agent 自主恢复全过程 |
| **02** | **PROD V2 升级突发断门与自愈传播案例** | [`14-wechat-mp-prod-v2-code-agent-zero-loss-case.zh.md`](14-wechat-mp-prod-v2-code-agent-zero-loss-case.zh.md) | 媒体/对外版本 | 微信公众号传播版，侧重工程技能护栏与自动化容灾表现 |
| **03** | **web-saas PROD V2 冷备、容灾与跨机恢复技术白皮书** | [`records/prod-v2-v3-20261019/web-saas-prod-v2-cold-backup-disaster-recovery-whitepaper.zh.md`](records/prod-v2-v3-20261019/web-saas-prod-v2-cold-backup-disaster-recovery-whitepaper.zh.md) | 技术白皮书 | 冷备策略、物理盘持久化规范与跨机演练技术标准 |
| **04** | **web-saas 代际快照与恢复证据模板** | [`records/prod-v2-v3-20261019/web-saas-generation-snapshot-recovery-template.zh.md`](records/prod-v2-v3-20261019/web-saas-generation-snapshot-recovery-template.zh.md) | 标准模板 | 代际演进中标准证据采集、数据完整性比对模板 |

---

## 4. PROD V2 → V3 代际迁移、快照与修复回执

记录 2026-10-19 V2 到 V3 的代际跃迁、全量快照归档脚本、SNI 与路由修复，以及 Vector 流量中断 P0 复盘。

| 编号 | 文档名称 / 标题 | 相对路径与链接 | 文档类型 | 核心范围与说明 |
| :---: | :--- | :--- | :---: | :--- |
| **01** | **PROD V2 → V3：快照、跨机恢复与升级复盘索引** | [`15-prod-v2-v3-snapshots-and-upgrade-retrospective.zh.md`](15-prod-v2-v3-snapshots-and-upgrade-retrospective.zh.md) | 总索引 | V2→V3 核心导航，关联 P0 事件与历史快照证据 |
| **02** | **V2/V3 快照与恢复记录归档说明** | [`records/prod-v2-v3-20261019/README.md`](records/prod-v2-v3-20261019/README.md) | 归档说明 | V2/V3 历史归档清单与环境状态总述 |
| **03** | **PROD V2 → V3 全量快照、恢复与升级复盘** | [`records/prod-v2-v3-20261019/20261019-prod-v2-v3-snapshot-and-upgrade-retrospective.zh.md`](records/prod-v2-v3-20261019/20261019-prod-v2-v3-snapshot-and-upgrade-retrospective.zh.md) | 升级复盘 | 跨主机迁移、切库、停机窗口与全量业务核验全景 |
| **04** | **V2 → V3 快照恢复、切库与平滑升级验收** | [`records/prod-v2-v3-20261019/v2-to-v3-snapshot-refresh-20261019.zh.md`](records/prod-v2-v3-20261019/v2-to-v3-snapshot-refresh-20261019.zh.md) | 验收回执 | 数据目录挂载、数据库同步与业务切库验收凭证 |
| **05** | **新代际主机快照恢复演练** | [`records/prod-v2-v3-20261019/new-generation-recovery-runbook.zh.md`](records/prod-v2-v3-20261019/new-generation-recovery-runbook.zh.md) | 演练手册 | 目标主机初始化、快照解压与沙箱环境重建指引 |
| **06** | **V3 共享服务令牌来源修正与部署验收** | [`records/prod-v2-v3-20261019/20261019-prod-v3-canonical-service-token.zh.md`](records/prod-v2-v3-20261019/20261019-prod-v3-canonical-service-token.zh.md) | 修复验收 | 服务互信 Token 来源收敛与部署校验 |
| **07** | **V3 公共 SNI 证书恢复与发布验收** | [`records/prod-v2-v3-20261019/20261019-prod-v3-public-sni-repair.zh.md`](records/prod-v2-v3-20261019/20261019-prod-v3-public-sni-repair.zh.md) | 修复验收 | 边缘网关 TLS/SNI 证书缺失修复与拨测验证 |
| **08** | **V3 VLESS 传输路径 P0 修复发布验收** | [`records/prod-v2-v3-20261019/20261019-prod-v3-vless-path-p0-release.zh.md`](records/prod-v2-v3-20261019/20261019-prod-v3-vless-path-p0-release.zh.md) | P0 修复 | 传输网关路径转发异常修复及发布验证 |
| **09** | **V2 → V3 关联 P0：Vector 流量入库被阻断** | [`records/prod-v2-v3-20261019/20261020-billing-vector-ingest-p0.zh.md`](records/prod-v2-v3-20261019/20261020-billing-vector-ingest-p0.zh.md) | P0 复盘 | 探针正常但采集 POST 被入口规则拦截事件分析 |
| **10** | **V3 全量快照维护源码归档说明及脚本** | [`examples/prod-v3-full-snapshot-20261019/README.md`](examples/prod-v3-full-snapshot-20261019/README.md) | 工具集归档 | 包含 `capture.py`, `capture_remote.py`, `capture_vault.py` 等 5 个快照工具 |

---

## 5. PROD V3 → V4 运行基线、DNS 变更与 OTel 方案

记录 2026-10-21 V3 到 V4 的主线候选验收、品牌域名切换回执、全链路 OTel 方案与收尾检查表。

| 编号 | 文档名称 / 标题 | 相对路径与链接 | 文档类型 | 核心范围与说明 |
| :---: | :--- | :--- | :---: | :--- |
| **01** | **PROD V3 → V4：运行基线、快照与升级复盘** | [`16-prod-v3-v4-baseline-and-upgrade-retrospective.zh.md`](16-prod-v3-v4-baseline-and-upgrade-retrospective.zh.md) | 总索引 | V3→V4 核心导航，线上服务状态盘点与待决事项 |
| **02** | **PROD V4 运行基线与快照清单** | [`records/prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md`](records/prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md) | 权威基线 | V4 运行组件版本、Digest、数据库状态及快照清单 |
| **03** | **V3 → V4 升级复盘：从候选恢复到正式运行** | [`records/prod-v3-v4-20261020/v3-v4-upgrade-retrospective-20261021.zh.md`](records/prod-v3-v4-20261020/v3-v4-upgrade-retrospective-20261021.zh.md) | 升级复盘 | 候选环境拉起、数据对齐到正式接流复盘 |
| **04** | **品牌域补齐 V4：DNS 变更回执** | [`records/prod-v3-v4-20261020/brand-dns-handoff-20261021.zh.md`](records/prod-v3-v4-20261020/brand-dns-handoff-20261021.zh.md) | 变更回执 | 品牌双域名对齐 V4 入口的变更证据与解析验证 |
| **05** | **V3 → V4 主线候选与实际验收检查点** | [`records/prod-v3-v4-20261020/main-candidate-acceptance-20261021.zh.md`](records/prod-v3-v4-20261020/main-candidate-acceptance-20261021.zh.md) | 验收清单 | 各服务端到端可用性及逐项测试结果检查点 |
| **06** | **V3 → V4 回归检查点与收尾清单** | [`records/prod-v3-v4-20261020/regression-and-closure-checklist-20261021.zh.md`](records/prod-v3-v4-20261020/regression-and-closure-checklist-20261021.zh.md) | 收尾清单 | 权限、出站 Webhook、用量展示等收尾清单 |
| **07** | **网络延迟与流量统计：双链路 OTel 实施及验收方案** | [`records/prod-v3-v4-20261020/network-and-traffic-otel-plan-20261021.zh.md`](records/prod-v3-v4-20261020/network-and-traffic-otel-plan-20261021.zh.md) | 方案规格 | 客户端与边缘端双链路 OpenTelemetry 追踪及验收规范 |
| **08** | **PROD V3 → V4 P0 事件记录与回归 Case** | [`records/prod-v2-v3-20261019/20261021-prod-v3-v4-p0-regression-record.zh.md`](records/prod-v2-v3-20261019/20261021-prod-v3-v4-p0-regression-record.zh.md) | 回归测试集 | 跨代际边界 P0 故障集与自动化回归用例 |

---

## 6. PROD V4 → V5 净室部署、路由修复与环境快照

记录 2026-10-23 至 2026-10-24 向 V5 演进的净室部署实测、Console 路由白屏修复、实时流量追加与修复后基线。

| 编号 | 文档名称 / 标题 | 相对路径与链接 | 文档类型 | 核心范围与说明 |
| :---: | :--- | :--- | :---: | :--- |
| **01** | **PROD V4 → V5：基线与升级复盘索引** | [`17-prod-v4-v5-baseline-and-upgrade-retrospective.zh.md`](17-prod-v4-v5-baseline-and-upgrade-retrospective.zh.md) | 总索引 | V4→V5 核心导航，连接统一流程、修复回执与回归结论 |
| **02** | **PROD V5 运行基线与快照清单** | [`records/prod-v5-20261023/prod-v5-runtime-and-snapshot-baseline-20261023.zh.md`](records/prod-v5-20261023/prod-v5-runtime-and-snapshot-baseline-20261023.zh.md) | 权威基线 | V5 服务组件、固定来源、内部数据库与快照状态总表 |
| **03** | **PROD V4 → V5 部署流程复盘** | [`records/prod-v5-20261023/prod-v5-deployment-postmortem-20261023.zh.md`](records/prod-v5-20261023/prod-v5-deployment-postmortem-20261023.zh.md) | 部署复盘 | 发布中断与恢复复盘，明确净室流程与边界缺失分析 |
| **04** | **PROD V5：净室部署、用户同步与三轮幂等验证回执** | [`records/prod-v5-20261023/prod-v5-cleanroom-deployment-migration-validation-20261024.zh.md`](records/prod-v5-20261023/prod-v5-cleanroom-deployment-migration-validation-20261024.zh.md) | 验证回执 | Cleanroom 环境全新拉起、账号增量对账及幂等性实测 |
| **05** | **V5 公共 Console 白屏：路由遗漏与修复回执** | [`records/prod-v5-20261023/20261024-prod-v5-public-console-route-repair.zh.md`](records/prod-v5-20261023/20261024-prod-v5-public-console-route-repair.zh.md) | 修复回执 | Caddy host matcher 遗漏导致的前端白屏紧急排障与回执 |
| **06** | **V5 在线业务追加与实时流量回归回执** | [`records/prod-v5-20261023/20261024-prod-v5-business-append-and-traffic-regression.zh.md`](records/prod-v5-20261023/20261024-prod-v5-business-append-and-traffic-regression.zh.md) | 验证回执 | 在线业务数据追加、真实流量拨测与完整性对账 |
| **07** | **PROD V5 修复后环境快照与恢复验证** | [`records/prod-v5-20261023/20261024-prod-v5-post-repair-environment-snapshot.zh.md`](records/prod-v5-20261023/20261024-prod-v5-post-repair-environment-snapshot.zh.md) | 快照验证 | 路由修复后的最终干净基线快照与跨环境恢复验证 |

---

## 7. Kubernetes UAT (`web-saas-k3s-v5`) 运行基线与快照清单

记录 2026-10-24 Akamai Cloud VPS (Tokyo 3, Debian 13) 上基于 K3s + Flux v2 + ESO 的全新 Kubernetes UAT 交付收尾、7 项实测验收与全量基线快照。

| 编号 | 文档名称 / 标题 | 相对路径与链接 | 文档类型 | 核心范围与说明 |
| :---: | :--- | :--- | :---: | :--- |
| **01** | **Kubernetes UAT (`web-saas-k3s-v5`) 运行基线与快照清单** | [`records/uat-k3s-v5-20261024/web-saas-k3s-v5-runtime-and-snapshot-baseline-20261024.zh.md`](records/uat-k3s-v5-20261024/web-saas-k3s-v5-runtime-and-snapshot-baseline-20261024.zh.md) | 权威基线 | Akamai VPS 实机全栈工作负载、不可变构件 Digest、公网 HTTPS 验证与快照矩阵 |
| **02** | **Kubernetes UAT GitOps web-saas-k3s-v5 验收与验证回执** | [`../../../docs/reference/kubernetes-uat-gitops-web-saas-k3s-v5-acceptance.zh.md`](../../../docs/reference/kubernetes-uat-gitops-web-saas-k3s-v5-acceptance.zh.md) | 验收回执 | 跨仓库 PR 追踪、流水线 Run 40086294084 证据与 7 阶段全流程验收 |

---

> [!NOTE]
> **版本演进阅读建议**：
> - 查找**通用标准与多云身份**：参考 [第 2 节 通用架构基线与跨代际契约规范]（09-12 篇）；
> - 查找**特定代际的基线与快照**：各版本均以其对应的总索引（`15-...`、`16-...`、`17-...`）及 `runtime-and-snapshot-baseline` 权威表作为首选入口。

### Kubernetes UAT 后续方案归档

- [业务数据迁移、Vault 隔离恢复及观测对接方案（2026-10-24）](records/uat-k3s-v5-20261024/k3s-v5-data-vault-observability-plan-20261024.zh.md)：用户材料脱敏归档，保留待决项与阶段状态，未执行项不作为验收成功。

- [Kubernetes UAT 增强安全与严格准入方案（2026-10-24）](records/uat-k3s-v5-20261024/k3s-v5-migration-enhanced-guardrails-20261024.zh.md)：追加计划标识、期望状态和证据缺口；不代表迁移完成。


## 追加：2026-10-25 V5 VPS → K3s 容器化承载

本节保留上文采样背景，不把旧 VPS/UAT 的成功重写为当前 PROD K3s 全流程通过。

- [V5 VPS → V5 K3s 运行快照、服务配置路径与验收 TODO](records/prod-v5-k3s-20261025/prod-v5-vps-to-k3s-runtime-and-acceptance-20261025.zh.md)
- [可复用 Markdown 验收检查表](records/prod-v5-k3s-20261025/deployment-migration-acceptance-checklist.template.zh.md)
- [GitHub ↔ 新 Vault：30 角色 / 11 策略矩阵与复用待办](records/prod-v5-k3s-20261025/github-vault-role-policy-matrix-20261025.zh.md)（实现：[Toolkit #1443](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/1443)、[#1444](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/1444)；[Playbooks #765](https://github.com/ai-workspace-infra/playbooks/pull/765)；归档：[Knowledge #225](https://github.com/ai-workspace-services/knowledge/pull/225)）

本组快照与检查表归档于 [Knowledge #224](https://github.com/ai-workspace-services/knowledge/pull/224)，组织流程入口见 [.github #48](https://github.com/ai-workspace-services/.github/pull/48)。

本轮采用 V5 K3s all-in-one，将 Web-SaaS、Vault Server 与 Grafana/观测栈这一核心控制面汇聚到一台 Linode 2C4G VPS，以资源整合进一步降本；当前固定构件、DNS、数据范围、批准例外及待办见新回执。资源整合不等于已完成旧资源回收或已实现账单节省。


GitHub 与新 Vault 的[30 角色 / 11 策略矩阵及复用待办](records/prod-v5-k3s-20261025/github-vault-role-policy-matrix-20261025.zh.md)：按仓库与环境列出工作流/ref、权限类型、回读、幂等和实际 CI 证据。
