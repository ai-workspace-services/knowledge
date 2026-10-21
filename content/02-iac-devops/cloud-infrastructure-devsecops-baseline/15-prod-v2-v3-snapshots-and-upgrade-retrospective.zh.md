# PROD V2 → V3：快照、跨机恢复与升级复盘索引

记录日期：2026-10-19（Asia/Shanghai）。本文汇集已执行的代际升级与快照证据，供 V3→V4 等后续变更参考。历史记录保留当时的计数、release 和验收边界，不作为当前在线状态的自动声明。

## 按类别阅读

后续代际：[V3→V4 运行基线与完整问题复盘（2026-10-21）](16-prod-v3-v4-baseline-and-upgrade-retrospective.zh.md)。历史 V2/V3 快照数值不回写为 V4 当前状态。

2026-10-20 补充：[V2→V3 升级关联 Billing/Vector P0 时间线](records/prod-v2-v3-20261019/20261020-billing-vector-ingest-p0.zh.md)。健康探针通过但采集 POST 被恢复期入口规则拦截；首次真实入库恢复已确认，逐节点和断档覆盖验收单独记录。

2026-10-21 补充：[V3→V4 升级 P0 事件、回归 Case 与证据索引](records/prod-v2-v3-20261019/20261021-prod-v3-v4-p0-regression-record.zh.md)。逐项映射业务 DB 权限、Stripe 出站与 Webhook、Agent 注册、Exporter/Vector/Billing 流量链、重复采集源、最近一小时用量展示及登录/引导 API。可执行检查和未覆盖的人工验收明确分开；未运行或被阻断的 Case 不算通过。

| 类别 | 文档 |
| --- | --- |
| 本轮完整记录与问题复盘 | [V2/V3 快照与升级复盘](records/prod-v2-v3-20261019/20261019-prod-v2-v3-snapshot-and-upgrade-retrospective.zh.md) |
| V2 历史全量快照 | [冷备、容灾与跨机恢复白皮书](records/prod-v2-v3-20261019/web-saas-prod-v2-cold-backup-disaster-recovery-whitepaper.zh.md) |
| V2→V3 数据恢复与 SQL 升级 | [快照刷新、候选库切换与迁移验收](records/prod-v2-v3-20261019/v2-to-v3-snapshot-refresh-20261019.zh.md) |
| 公共 SNI 与证书 | [公共 SNI 修复](records/prod-v2-v3-20261019/20261019-prod-v3-public-sni-repair.zh.md) |
| 共享鉴权凭据 | [Vault 权威来源与运行态核验](records/prod-v2-v3-20261019/20261019-prod-v3-canonical-service-token.zh.md) |
| VLESS 传输路径 | [P0 修复与不可变构件发布](records/prod-v2-v3-20261019/20261019-prod-v3-vless-path-p0-release.zh.md) |
| 后续代际证据模板 | [快照和恢复证据模板](records/prod-v2-v3-20261019/web-saas-generation-snapshot-recovery-template.zh.md) |
| 本轮维护脚本历史源码 | [源码目录与执行边界](examples/prod-v3-full-snapshot-20261019/README.md) |
| V3→V4 P0 故障与回归用例 | [事件时间线、Case ID 与验收状态](records/prod-v2-v3-20261019/20261021-prod-v3-v4-p0-regression-record.zh.md) |

## V3 最新快照结果

- 快照起始时间：2026-10-19 23:16:28（北京时间）。
- 主机路径：`/data/backups/web-saas/prod-v3/full-snapshot-20261019/20261019T151628Z/`。
- 数据库：`account`，schema `2026101902 / dirty=false`。
- 业务计数：33 位用户、13 条订阅、32,847 条账本。
- 75 张表使用同一导出快照读取与导出，独立 PostgreSQL 容器恢复后的行指纹一致。
- DB、globals、配置/TLS、完整容器 inspect 与 Vault 快照均分别加密；完整性清单通过校验。
- Vault 已完成解密回读与 inspect，独立实例恢复尚未执行。
- 主机外副本位于受保护维护工作站，第三地点存储及独立密钥托管仍需补齐。

此处的“全量”指可恢复的逻辑业务库与服务配置集合；不包含云磁盘镜像、历史非活跃库、Registry 镜像层或可重新生成的 Docker 缓存。DB、Vault 和运行配置分别采集，不构成跨组件全局原子快照。

## 复用时必须分开的事实

1. 主机代际、发布版本和数据库 schema 是三个不同维度；记录完整 SHA 和 digest。
2. 快照当时的用户/订阅/账务计数，与后来实时数据分别解释。
3. DB 恢复成功、共享 Token 一致、Agent 新鲜注册、终端可连接和支付验收分别留证。
4. DNS 回退不等于数据库回退；新代际写入后不能直接回到落后的旧库。
5. `/split` 是传输路径；资源类别用于授权和筛选，节点名称中的 `v2` 后缀不代表请求仍到旧 Accounts。

## 维护归属

Knowledge 维护文档、证据及不可直接执行的历史样本。正式主机执行能力由 [Playbooks](https://github.com/ai-workspace-infra/playbooks) 的 Role/入口维护；GitOps 维护发布声明；IaC Modules 维护云资源与 DNS；Toolkit 维护控制入口与放行。

本轮同快照维护代码仍有参数化与门禁固化工作，不能将归档源码当作已验证通用 Role。现有 `web_saas_cold_recovery` 的备份/指纹读取分离问题也在复盘中列为后续事项。

前置设计见[数据库同步与发布晋级状态机](12-uat-database-sync-and-prod-promotion-state-machine.zh.md)。历史 V2 升级案例见[零数据丢失案例](13-prod-v2-upgrade-recovery-zero-data-loss-case.zh.md)。本次仅整理知识库，不触发部署或在线数据操作。
