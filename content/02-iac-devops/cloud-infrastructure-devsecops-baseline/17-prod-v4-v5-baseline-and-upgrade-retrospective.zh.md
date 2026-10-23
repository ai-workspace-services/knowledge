# PROD V4 → V5：基线与升级复盘索引

记录更新：2026-10-24（Asia/Shanghai）。本页连接统一流程、V4/V5 运行基线、部署回执、恢复证据与仓库内回归 case；不替代各 owner 的 GitOps、Playbooks 或 IaC 配置。公开副本使用逻辑代际及脱敏摘要，主机身份、地址、凭据、秘密存储路径、原始 state、数据库和备份保留在受控位置。

统一流程：[Selfhost 控制面部署与核心数据迁移](https://github.com/ai-workspace-services/.github/blob/main/docs/control-plane-deployment-and-migration.zh.md)。前序记录：[V3→V4 快照与升级复盘](16-prod-v3-v4-baseline-and-upgrade-retrospective.zh.md)；[V2→V3 快照与升级复盘](15-prod-v2-v3-snapshots-and-upgrade-retrospective.zh.md)。

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
- 最新新一轮 V5 主机删除/重建及部署、迁移各三次重复验证在本页记录时尚未执行，状态 NOT_RUN。旧“Docker 未安装、旧 apply 运行中”等文字仅属于 2026-10-23 前序采样，已由后续 r5/r103 回执取代，不作为当前状态。

## 专项故障与仓库内真实回归

| 风险 | 原记录 / 可导航回归 | 状态边界 |
| --- | --- | --- |
| 共享 Token 来源与进程注入 | [V3 canonical service token](records/prod-v2-v3-20261019/20261019-prod-v3-canonical-service-token.zh.md)、[V3→V4 P0 case](records/prod-v2-v3-20261019/20261021-prod-v3-v4-p0-regression-record.zh.md) | 历史 PASS 不替代当前代际新鲜值核验；绝不公开 Token 或 Vault 路径 |
| 公共 SNI/证书链 | [公共 SNI 修复](records/prod-v2-v3-20261019/20261019-prod-v3-public-sni-repair.zh.md)、[Playbooks #741](https://github.com/ai-workspace-infra/playbooks/pull/741) | r4 首次部署仍失败；后续 r5 信任探测通过，不改写 r4 失败 |
| VLESS 路径 | [VLESS P0 发布记录](records/prod-v2-v3-20261019/20261019-prod-v3-vless-path-p0-release.zh.md) | 历史版本的真实回归；未作为本轮 V5 用户迁移验收 |
| Billing/Vector | [Billing/Vector 入库 P0](records/prod-v2-v3-20261019/20261020-billing-vector-ingest-p0.zh.md)、[V4 网络与流量回归计划](records/prod-v3-v4-20261020/network-and-traffic-otel-plan-20261021.zh.md) | V5 本轮探针不证明真实采集/计费周期，当前业务链 NOT_RUN |
| 数据恢复权限 | [新代际恢复 runbook](records/prod-v2-v3-20261019/new-generation-recovery-runbook.zh.md)、[V4 恢复记录](records/prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md) | users-only V5 restore PASS；完整财务/订阅 G3 不在范围 |
| 域名交接 | [品牌域名交接回执](records/prod-v3-v4-20261020/brand-dns-handoff-20261021.zh.md) | 历史 V3→V4 交接；本轮 V4→V5 不改公共 DNS |
| 回归清单 | [V4 regression and closure checklist](records/prod-v3-v4-20261020/regression-and-closure-checklist-20261021.zh.md) | 每个 case 绑定源码/测试/结果；未覆盖项保持 BLOCKED/NOT_RUN |

## Clean-room 验收标准

使用固定 GitOps/Playbooks/installer 引用与预构建 `migratectl`；先保护现有备份、state 和任何可恢复数据，再只替换 V5 candidate。每次独立执行记录 Asia/Shanghai 起止、run_id、源/目标逻辑身份、固定 commit/tag/digest、schema/checksum、阶段、exit code、原因、修复 PR 与脱敏证据索引。

- 部署：首次成功后，使用完全相同的固定输入再运行三次；每次 exit 0，期望配置、运行版本、数据身份和容器状态无非预期差异，无不必要重启。
- 迁移：源端只读快照，目标只在精确预览计划下写入批准范围；应用后再预览/应用三次。相同内容须为空操作，所有用户字段摘要稳定，目标独有事实不覆盖；V4 业务和源状态不改变。
- 恢复：对有代表性数据的目标备份做独立 restore 并核对 schema/data/sequence/权限和应用连接。空目标备份只作为部署前恢复演练，不冒充数据迁移后恢复。
- 回归/切换：历史 case 逐条实际执行；登录、外部 OAuth/支付、Agent 和业务账务未通过前不得称业务验收完成。此页不授权 DNS 切换或写入权转移。

结果只在实际运行后追加到[V5 运行基线](records/prod-v5-20261023/prod-v5-runtime-and-snapshot-baseline-20261023.zh.md)；任何失败保留在原时间线上，并以新 run/revision 记录修复与重验。
