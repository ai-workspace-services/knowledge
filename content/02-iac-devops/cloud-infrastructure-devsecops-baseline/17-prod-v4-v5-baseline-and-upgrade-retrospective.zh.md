# PROD V4 → V5：基线与升级复盘索引

记录更新：2026-10-24（Asia/Shanghai）。本页连接统一流程、V4/V5 运行基线、部署回执、恢复证据与仓库内回归 case；不替代各 owner 的 GitOps、Playbooks 或 IaC 配置。公开副本使用逻辑代际及脱敏摘要，主机身份、地址、凭据、秘密存储路径、原始 state、数据库和备份保留在受控位置。

统一流程：[Selfhost 控制面部署与核心数据迁移](https://github.com/ai-workspace-services/.github/blob/main/docs/control-plane-deployment-and-migration.zh.md)。前序记录：[V3→V4 快照与升级复盘](16-prod-v3-v4-baseline-and-upgrade-retrospective.zh.md)；[V2→V3 快照与升级复盘](15-prod-v2-v3-snapshots-and-upgrade-retrospective.zh.md)。

## 最新入口与环境修订（2026-10-24 12:18 +08）

[V5 当前环境总表](records/prod-v5-20261023/prod-v5-runtime-and-snapshot-baseline-20261023.zh.md)现按服务、固定来源、数据库链路、代理状态及验收范围汇总。[公共 Console 白屏回执](records/prod-v5-20261023/20261024-prod-v5-public-console-route-repair.zh.md)纠正“DNS 到达即页面通过”的遗漏：三业务别名已交接，但 Console 的 host matcher 后补修复才完成页面验收。公共 PostgreSQL 别名仍指 V2；V5 服务内部已连接本机数据库，两者不能混淆。11:21 快照早于本次路由修复，恢复后必须按最新固定配置收敛。

## 修复后业务与快照结论（2026-10-24 后续回执）

[在线业务追加与实时流量回归](records/prod-v5-20261023/20261024-prod-v5-business-append-and-traffic-regression.zh.md)记录追加 152,353 行、r106 三轮真实无写入重放、JP Plus 两周期真实入库及页面核验；[修复后环境快照](records/prod-v5-20261023/20261024-prod-v5-post-repair-environment-snapshot.zh.md)补齐含套餐/订阅/账务的 76 表独立恢复和异机验证。users-only 不再代表最新业务恢复范围。默认 Sandbox 的单一代理 UUID 差异经明确接受保留目标值；策略快照源端也为空。其他节点的空闲/未验收状态、角色登录恢复和整机演练仍分别记录，不能据此宣称最终切换完成。

<!-- BEGIN CLEANROOM 20261024 -->
## 净室执行与三轮重验（2026-10-24 03:09 +08）

新增[实际执行回执](records/prod-v5-20261023/prod-v5-cleanroom-deployment-migration-validation-20261024.zh.md)，与[当前 V5 基线](records/prod-v5-20261023/prod-v5-runtime-and-snapshot-baseline-20261023.zh.md)双向关联。候选精确删除、净室创建、首次部署、r104 users-only 同步及含 33 users 的独立恢复已通过；完整带数据重放为 **PASS（3/3）**。首次失败、修复 PR 与仓库内真实回归 case 在该回执逐项关联。范围保持 users-only；终点 V4 字段相对快照已有增量，最终追齐仍 BLOCKED，未执行业务及切换不因三轮结果升级为 PASS。

<!-- END CLEANROOM 20261024 -->

## 阅读链

| 阶段 | 权威记录 | 作用 |
| --- | --- | --- |
| V4 源基线 | [PROD V4 运行基线与快照清单](records/prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md) | 记录其采样时的服务、构件、数据、权限、域名和快照；不自动代表当前 V4 状态 |
| V4→V5 执行/故障 | [V5 部署流程复盘](records/prod-v5-20261023/prod-v5-deployment-postmortem-20261023.zh.md) | 保留旧实例/旧 apply 失败时间线；明确历史采样已被后续回执取代 |
| V5 当前候选基线 | [PROD V5 运行基线与快照清单](records/prod-v5-20261023/prod-v5-runtime-and-snapshot-baseline-20261023.zh.md) | 逐次绑定 fixed refs、镜像/工具摘要、schema、退出码、迁移、恢复及未验收项 |
| 回归与重验 | [V4 回归检查清单](records/prod-v3-v4-20261020/regression-and-closure-checklist-20261021.zh.md)、[V3→V4 P0 case 记录](records/prod-v2-v3-20261019/20261021-prod-v3-v4-p0-regression-record.zh.md)、本页下方专项记录 | 具体 case 链到配置 owner 仓库的测试/PR；未运行项保持 NOT_RUN |

## 已记录的阶段结论（2026-10-24 01:07 +08 前）

- V5 candidate 的 r5 首次固定部署与同输入一次重跑均 exit 0，8 项组件/数据库/可信 HTTPS 探测通过；容器、配置及数据库身份在两次运行间无差异。此历史只证明一次重复，后续 clean-room “至少三次无差异”仍是单独 gate。
- r102 迁移预览在空目标失败且未写入；[Accounts #270](https://github.com/ai-workspace-services/accounts/pull/270) 修复后，预构建 r103 users-only 工具从逻辑源 V4 追加 33 用户到 V5，exit 0，字段摘要核对通过。服务未停止，V4 未写入。
- 迁移后完整加密备份与隔离恢复通过，目标恢复为 33 users；订阅仍为 0。因此该恢复不等于全业务恢复或业务验收。
- 真实凭据登录、OAuth、支付、Agent、订阅、完整 Billing/Vector 周期及最终业务验收仍 NOT_RUN/BLOCKED；最终 DNS/流量/写入切换未执行，须人工另行明确确认。
- 本节 01:07 采样时，新一轮 V5 主机删除/重建及部署、迁移各三次重复验证尚未执行，状态 NOT_RUN；后续实际进展见上方净室执行回执。旧“Docker 未安装、旧 apply 运行中”等文字仅属于 2026-10-23 前序采样，已由后续 r5/r103 回执取代，不作为当前状态。

## 专项故障与仓库内真实回归

| 风险 | 原记录 / 可导航回归 | 状态边界 |
| --- | --- | --- |
| 共享 Token 来源与进程注入 | [V3 canonical service token](records/prod-v2-v3-20261019/20261019-prod-v3-canonical-service-token.zh.md)、[V3→V4 P0 case](records/prod-v2-v3-20261019/20261021-prod-v3-v4-p0-regression-record.zh.md) | 历史 PASS 不替代当前代际新鲜值核验；绝不公开 Token 或 Vault 路径 |
| 公共 SNI/证书链 | [公共 SNI 修复](records/prod-v2-v3-20261019/20261019-prod-v3-public-sni-repair.zh.md)、[Playbooks #741](https://github.com/ai-workspace-infra/playbooks/pull/741) | r4 首次部署仍失败；后续 r5 信任探测通过，不改写 r4 失败 |
| VLESS 路径 | [VLESS P0 发布记录](records/prod-v2-v3-20261019/20261019-prod-v3-vless-path-p0-release.zh.md) | 历史版本的真实回归；未作为本轮 V5 用户迁移验收 |
| Billing/Vector | [Billing/Vector 入库 P0](records/prod-v2-v3-20261019/20261020-billing-vector-ingest-p0.zh.md)、[V4 网络与流量回归计划](records/prod-v3-v4-20261020/network-and-traffic-otel-plan-20261021.zh.md) | 旧采样仅有探针；后续 JP Plus 两周期正向入库及未验收节点见上方新回执 |
| 数据恢复权限 | [新代际恢复 runbook](records/prod-v2-v3-20261019/new-generation-recovery-runbook.zh.md)、[V4 恢复记录](records/prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md) | 旧 users-only 恢复保留；后续含业务数据的全表/schema/sequence 独立恢复 PASS，生产角色登录与应用权限恢复仍未验收 |
| 域名交接 | [品牌域名交接回执](records/prod-v3-v4-20261020/brand-dns-handoff-20261021.zh.md) | 历史 V3→V4 交接；本轮 V4→V5 不改公共 DNS |
| 回归清单 | [V4 regression and closure checklist](records/prod-v3-v4-20261020/regression-and-closure-checklist-20261021.zh.md) | 每个 case 绑定源码/测试/结果；未覆盖项保持 BLOCKED/NOT_RUN |

## Clean-room 验收标准

使用固定 GitOps/Playbooks/installer 引用与预构建 `migratectl`；先保护现有备份、state 和任何可恢复数据，再只替换 V5 candidate。每次独立执行记录 Asia/Shanghai 起止、run_id、源/目标逻辑身份、固定 commit/tag/digest、schema/checksum、阶段、exit code、原因、修复 PR 与脱敏证据索引。

- 部署：首次成功后，使用完全相同的固定输入再运行三次；每次 exit 0，期望配置、运行版本、数据身份和容器状态无非预期差异，无不必要重启。
- 迁移：源端只读快照，目标只在精确预览计划下写入批准范围；应用后再预览/应用三次。相同内容须为空操作，所有用户字段摘要稳定，目标独有事实不覆盖；V4 业务和源状态不改变。
- 恢复：对有代表性数据的目标备份做独立 restore 并核对 schema/data/sequence/权限和应用连接。空目标备份只作为部署前恢复演练，不冒充数据迁移后恢复。
- 回归/切换：历史 case 逐条实际执行；登录、外部 OAuth/支付、Agent 和业务账务未通过前不得称业务验收完成。此页不授权 DNS 切换或写入权转移。

结果只在实际运行后追加到[V5 运行基线](records/prod-v5-20261023/prod-v5-runtime-and-snapshot-baseline-20261023.zh.md)；任何失败保留在原时间线上，并以新 run/revision 记录修复与重验。


## 追加：2026-10-25 V5 VPS → K3s 容器化承载

本节保留上文采样背景，不把旧 VPS/UAT 的成功重写为当前 PROD K3s 全流程通过。

- [V5 VPS → V5 K3s 运行快照、服务配置路径与验收 TODO](records/prod-v5-k3s-20261025/prod-v5-vps-to-k3s-runtime-and-acceptance-20261025.zh.md)
- [可复用 Markdown 验收检查表](records/prod-v5-k3s-20261025/deployment-migration-acceptance-checklist.template.zh.md)
- [GitHub ↔ 新 Vault：30 角色 / 11 策略矩阵与复用待办](records/prod-v5-k3s-20261025/github-vault-role-policy-matrix-20261025.zh.md)

归档 PR：Knowledge [#224](https://github.com/ai-workspace-services/knowledge/pull/224)（快照与检查表）、[#225](https://github.com/ai-workspace-services/knowledge/pull/225)（角色/策略矩阵）；实现 PR：Toolkit [#1443](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/1443)、[#1444](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/1444)，Playbooks [#765](https://github.com/ai-workspace-infra/playbooks/pull/765)；组织流程索引：[.github #48](https://github.com/ai-workspace-services/.github/pull/48)。这些 PR 均已合并；运行及验收状态仍以各自证据为准。

本轮采用 V5 K3s all-in-one，将 Web-SaaS、Vault Server 与 Grafana/观测栈这一核心控制面汇聚到一台 Linode 2C4G VPS，以资源整合进一步降本；当前固定构件、DNS、数据范围、批准例外及待办见新回执。资源整合不等于已完成旧资源回收或已实现账单节省。


GitHub 与新 Vault 的[30 角色 / 11 策略矩阵及复用待办](records/prod-v5-k3s-20261025/github-vault-role-policy-matrix-20261025.zh.md)：按仓库与环境列出工作流/ref、权限类型、回读、幂等和实际 CI 证据。
