---
title: V2 至 V5 部署、迁移、故障与回归证据索引
date: 2026-10-25
lang: zh
tags:
  - platform-engineering
  - deployment-evidence
  - regression
---

# V2 至 V5：部署回执、故障复盘与重验双向索引

本页是[既有统一部署迁移流程](https://github.com/ai-workspace-services/.github/blob/main/docs/control-plane-deployment-and-migration.zh.md)的证据附件。需求：[Knowledge #227](https://github.com/ai-workspace-services/knowledge/issues/227)。文档核对基线为 Knowledge `87ae34a6aca3aaaae72c6ff85202bfd084f9e2ff`、组织流程 `d179da5b3ec7c0cc83e4fbb1bac92719934730b6`；这是归档版本，不能当成部署版本。

本次没有重新执行部署、迁移、恢复、业务登录、DNS 或写入权交接。下列结果来自各自标注时间的原回执；2026-10-25 K3s 的最近已归档运行采样，也不能自动延伸为持续健康证明。原始证据继续留在受控位置。

## 1. 按代际导航

统一流程 → 本表基线 → 逐轮回执 → 复盘 → [固定源码 case](#3-专项故障真实-case-与重验) → 对应重验。各文档也回链到本页。

| 范围 | 运行基线或真实历史记录 | 逐轮部署 / 迁移 / 恢复回执 | 故障复盘与重验入口 |
| --- | --- | --- | --- |
| V2→V3 | [V2 冷备基线](prod-v2-v3-20261019/web-saas-prod-v2-cold-backup-disaster-recovery-whitepaper.zh.md)、[V3 快照与恢复](prod-v2-v3-20261019/20261019-prod-v2-v3-snapshot-and-upgrade-retrospective.zh.md) | [快照刷新、候选库切换与 SQL 升级](prod-v2-v3-20261019/v2-to-v3-snapshot-refresh-20261019.zh.md) | [V2→V3 索引](../15-prod-v2-v3-snapshots-and-upgrade-retrospective.zh.md)及下方 Token / SNI / VLESS / Billing 专项 |
| V3→V4 | [V4 运行基线](prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md) | 同页 r8 发布、历史 DB 隔离恢复；[品牌域名交接](prod-v3-v4-20261020/brand-dns-handoff-20261021.zh.md) | [V3→V4 复盘](prod-v3-v4-20261020/v3-v4-upgrade-retrospective-20261021.zh.md) → [回归检查点与收尾](prod-v3-v4-20261020/regression-and-closure-checklist-20261021.zh.md) |
| V4→V5 VPS | [V5 VPS 基线](prod-v5-20261023/prod-v5-runtime-and-snapshot-baseline-20261023.zh.md) | [净室部署及 users-only 三轮](prod-v5-20261023/prod-v5-cleanroom-deployment-migration-validation-20261024.zh.md)、[业务追加及三轮 no-op](prod-v5-20261023/20261024-prod-v5-business-append-and-traffic-regression.zh.md)、[完整业务库快照与恢复](prod-v5-20261023/20261024-prod-v5-post-repair-environment-snapshot.zh.md) | [V4→V5 部署复盘](prod-v5-20261023/prod-v5-deployment-postmortem-20261023.zh.md)、[公共 Console 路由重验](prod-v5-20261023/20261024-prod-v5-public-console-route-repair.zh.md) |
| V5 VPS→V5 K3s PROD | [K3s all-in-one 基线](prod-v5-k3s-20261025/prod-v5-vps-to-k3s-runtime-and-acceptance-20261025.zh.md) | 同页三轮 Flux/Helm 协调及按服务配置、数据例外；[GitHub / Vault 矩阵](prod-v5-k3s-20261025/github-vault-role-policy-matrix-20261025.zh.md) | 同页故障与 23 项状态 → [可复用检查表](prod-v5-k3s-20261025/deployment-migration-acceptance-checklist.template.zh.md)；不是 VPS 三轮部署/迁移回执的复用 |

V5 K3s 将 Web-SaaS、Vault Server、Grafana/观测栈汇聚到单台 Linode 2C4G；命名空间、身份与卷保持独立。资源整合、旧资源回收和实际账单节省分别留证。K3s 初始 [UAT 基线](uat-k3s-v5-20261024/web-saas-k3s-v5-runtime-and-snapshot-baseline-20261024.zh.md)及[历史综合报告](uat-k3s-v5-20261024/web-saas-k3s-v5-data-migration-vault-recovery-observability-acceptance-20261024.zh.md)保留原环境与时间口径，不替代后续 PROD 候选验收。

## 2. 每轮证据的覆盖与缺口

每轮应由原始回执绑定：`run_id/attempt`、Asia/Shanghai 起止、源/目标及环境、逐仓固定 commit/tag、镜像/Chart/工具 digest、schema 版本/dirty 与迁移校验和、阶段/状态/退出码、原因、修复 PR、真实 case、重验及受控 evidence_id。下面链接原有逐轮表，避免复制另一套运行结果。

| 回执组 / 源→目标 | 起止 / run_id / 退出码 | 固定来源、校验与结果边界 |
| --- | --- | --- |
| V2→V3 数据恢复与升级 | [原回执](prod-v2-v3-20261019/v2-to-v3-snapshot-refresh-20261019.zh.md)记录源快照边界 2026-10-19 17:02:04 +08；完整执行起止、统一 run_id 及阶段退出码在公开回执中 `NOT_RECORDED`，不拿目录时间充作 run_id | [完整复盘](prod-v2-v3-20261019/20261019-prod-v2-v3-snapshot-and-upgrade-retrospective.zh.md)有固定发布、工具 SHA-256 及两段 SQL checksum，最终 `2026101902/dirty=false`；DB 恢复、Vault inspect 与真实业务分别判断；按新证据合同重验为 BLOCKED，等待缺失回执 |
| V4 r8 原位应用发布 | [V4 基线](prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md)采样 2026-10-21 13:23:50 +08；标题 13:23–13:24 是发布窗口，不推算精确退出时刻；公开 run_id/各阶段退出码 `NOT_RECORDED` | `v2026.10.21-r8` / `e5e11d2718c9f992c760b6c542d3c40b48fdf7bb`，逐镜像 digest、历史 SQL/native checksum 见原文；本轮无新增迁移，SQL 执行为 N/A；历史恢复不能顶替 r8 的新恢复 |
| V4 只读快照→V5 VPS，净室及 users-only | [逐轮表](prod-v5-20261023/prod-v5-cleanroom-deployment-migration-validation-20261024.zh.md#每轮真实执行)列出 10-24 02:16–03:07 的 destroy/apply/deploy/migrate 与失败、[08:56–09:02 追加轮](prod-v5-20261023/prod-v5-cleanroom-deployment-migration-validation-20261024.zh.md#additional-replay-20261024)；完整 run_id、带时区起止及 exit code 均按原表，不把本地 ID 拼成 CI URL | 同页固定 IaC/GitOps/Playbooks/installer、r104 工具 digest、Accounts/Billing schema；无 DDL，SQL checksum N/A。三轮固定输入 PASS；末次源鲜度比较 exit 1 保留 BLOCKED；users-only 不含完整账务 |
| V4 隔离快照→在线 V5 VPS，业务追加 | [r105 首轮与 r106 三轮](prod-v5-20261023/20261024-prod-v5-business-append-and-traffic-regression.zh.md)，2026-10-24 10:41:30–10:42:03 首次 exit 0；r105 重放被保护拒绝；r106 `verified-repeat-1/2/3` 11:02:03–11:05:50，各 preview/apply exit 0 | 工具 tag、源码 SHA、二进制/native/Billing checksum 见原文。公开仅保留重放 ID 前缀，完整 ID/attempt 待受控日志复核，标 `NOT_RECORDED`；数据 no-op 3/3 不能顶替完整部署或单写者交接 |
| V5 VPS→独立数据库恢复实例 | [快照与恢复](prod-v5-20261023/20261024-prod-v5-post-repair-environment-snapshot.zh.md)，`20261024031956`；2026-10-24 11:19:56–11:20:50 捕获、11:21:16–11:21:27 恢复，均 exit 0；异机校验结束 11:21:57，异机阶段起点 `NOT_RECORDED` | 固定 Playbooks/GitOps、加密归档及 schema 校验和见原文；76 表/字段/序列一致。未验证生产角色密码、应用登录和完整环境恢复；不把 11.13 秒当整机 RTO |
| K3s PROD→同一 K3s PROD，Flux/Helm 同版协调 | `k3s-v5-reconcile-3rounds-hsr8rj9c`，attempt=`NOT_RECORDED`；1：2026-10-25 17:40:47.294894–17:41:01.426178 +08；2：17:41:01.427178–17:41:13.069436 +08；3：17:41:13.069998–17:41:30.912696 +08；三轮 exit 0 | [K3s 基线](prod-v5-k3s-20261025/prod-v5-vps-to-k3s-runtime-and-acceptance-20261025.zh.md)固定 `v2026.10.25.3` / `78c49d92f2be6078b83f88097e9f4ea5295055ff`、Chart 0.2.5 与完整 digest；spec、Pod 身份及重启计数不变。无 SQL 迁移，checksum N/A；本轮 native schema checksum `NOT_RECORDED`，不可借用旧版本；IaC 重建、迁移重放及恢复各自 NOT_RUN |
| 新 Vault 常规 GitHub 身份协调 | [矩阵原回执](prod-v5-k3s-20261025/github-vault-role-policy-matrix-20261025.zh.md)：2026-10-25 17:58:02–17:58:19 及 17:58:20–17:58:39 +08，exit 0；统一 run_id/attempt `NOT_RECORDED` | 固定 Toolkit / Playbooks SHA；30 角色、11 策略回读，重跑 changed=0。非 DB 迁移，schema checksum N/A；仅 GitOps SIT 有实际 CI 登录证据，其余逐环境登录和真实负向认证保持 NOT_RUN |

`NOT_RECORDED` 表示历史字段未取得，不推断当时没有执行；需要它作为下一门禁时，该项为 `BLOCKED`。未执行阶段用 `NOT_RUN`。checksum 只在证明本轮不适用时写 `N/A` 并附理由。构建、部署、迁移、恢复、业务验收、DNS/流量和写入权分别记录；exit 0 只说明该阶段在其范围内成功。

## 3. 专项故障、真实 case 与重验

下列 Playbooks 链接固定到已核对主线 `a7a01ac734968aa6e5f7baec0e172ae06a0b461d`；这只是源码目录核对，不表示本次运行了这些脚本。Accounts 的历史 case 保留对应发布源码，不换成漂移的 main。

| 主题 | 既有专项 / 修复来源 | 仓库内真实 case 或执行入口 | 重验及未关闭项 |
| --- | --- | --- | --- |
| 共享 Token、Exporter 凭据 | [V3 Token 权威来源](prod-v2-v3-20261019/20261019-prod-v3-canonical-service-token.zh.md)、[V5 追加/Exporter 回执](prod-v5-20261023/20261024-prod-v5-business-append-and-traffic-regression.zh.md)、[K3s 修复](prod-v5-k3s-20261025/prod-v5-vps-to-k3s-runtime-and-acceptance-20261025.zh.md)；[Playbooks #763](https://github.com/ai-workspace-infra/playbooks/pull/763) | [Exporter 凭据回归](https://github.com/ai-workspace-infra/playbooks/blob/a7a01ac734968aa6e5f7baec0e172ae06a0b461d/tests/test_snapshot_credential_repair.py)，对应 `V4-P0-EXPORTER-TOKEN` | 原位值比较与精确字段同步不输出秘密或其可复用摘要；K3s 最近归档为 3/5 新鲜 Agent，不能宣称全节点已验收 |
| 公共 SNI、证书与品牌路由 | [V3 公共 SNI](prod-v2-v3-20261019/20261019-prod-v3-public-sni-repair.zh.md)、[V5 公共 Console 空 200](prod-v5-20261023/20261024-prod-v5-public-console-route-repair.zh.md) | [历史 SNI/Host 回归入口](https://github.com/ai-workspace-infra/playbooks/blob/e2b584716fd6770f64d2ba2a7c4137fa4117c7ae/roles/web_saas_generation_fresh/files/regression_cases.py)、[品牌路由测试](https://github.com/ai-workspace-infra/playbooks/blob/a7a01ac734968aa6e5f7baec0e172ae06a0b461d/tests/test_web_saas_brand_route.py) | 旧候选域名预期需按声明阶段审核；可信 TLS、非空 HTML/静态资源及真实浏览器分别验收；K3s 原回执首页/登录 200 不推出单写者通过 |
| VLESS / XHTTP 路径 | [V3 路径修复及构件](prod-v2-v3-20261019/20261019-prod-v3-vless-path-p0-release.zh.md)，[Accounts #250](https://github.com/ai-workspace-services/accounts/pull/250) | 上述 `regression_cases.py` 的 `client-transport`；[固定历史 case 说明](prod-v3-v4-20261020/regression-and-closure-checklist-20261021.zh.md) | `/split` 修复、发布和探针不替代实际客户端连接；缺 fixture/客户端证据保持 BLOCKED/NOT_RUN |
| Billing / Vector 真入库 | [P0 时间线](prod-v2-v3-20261019/20261020-billing-vector-ingest-p0.zh.md)、[在线业务及两周期](prod-v5-20261023/20261024-prod-v5-business-append-and-traffic-regression.zh.md) | [`V4-P0-TRAFFIC-CHAIN` 的实际 SQL/探针脚本](https://github.com/ai-workspace-infra/playbooks/blob/a7a01ac734968aa6e5f7baec0e172ae06a0b461d/tests/data_operations/selfhost/v4_traffic_chain_acceptance.sh) | VPS 的 JP Plus 两周期 +8 桶/+8 账本是该节点历史实证；K3s 后续正增量另列。正流量、空闲、历史导入与每账户页面分别判断 |
| 恢复角色、ACL 与业务权限 | [V3 恢复授权边界](prod-v2-v3-20261019/20261019-prod-v2-v3-snapshot-and-upgrade-retrospective.zh.md)、[V4 权限故障](prod-v3-v4-20261020/v3-v4-upgrade-retrospective-20261021.zh.md)、[V5 恢复范围](prod-v5-20261023/20261024-prod-v5-post-repair-environment-snapshot.zh.md) | [`V4-P0-DB-ROLE` 只读权限验收](https://github.com/ai-workspace-infra/playbooks/blob/a7a01ac734968aa6e5f7baec0e172ae06a0b461d/tests/data_operations/selfhost/v4_business_role_acceptance.sh)、[隔离 PG case](https://github.com/ai-workspace-infra/playbooks/blob/a7a01ac734968aa6e5f7baec0e172ae06a0b461d/roles/web_saas_generation_fresh/files/postgres_cases.py) | `--no-owner/--no-acl`、占位角色恢复、真实业务身份连库是不同证据；禁止用 schema 恢复通过宣称密码/权限登录完整恢复 |
| 域名交接、入口模式与源只读 | [V4 品牌交接](prod-v3-v4-20261020/brand-dns-handoff-20261021.zh.md)、[V5 净室复盘](prod-v5-20261023/prod-v5-deployment-postmortem-20261023.zh.md) | [正式入口幂等保护测试](https://github.com/ai-workspace-infra/playbooks/blob/a7a01ac734968aa6e5f7baec0e172ae06a0b461d/tests/test_recovery_public_ingress_idempotency.py)、[域名合同](https://github.com/ai-workspace-infra/playbooks/blob/a7a01ac734968aa6e5f7baec0e172ae06a0b461d/tests/test_web_saas_domain_alias_contract.py) | [Playbooks #712](https://github.com/ai-workspace-infra/playbooks/pull/712)现已 MERGED，`611cc12b443ea669dc1460e6597320acaed7a418`；旧“OPEN”仍是原采样事实。DNS、HTTP 路由与写入权三项分别验收 |
| 追加迁移、计划、冲突与三轮 | [V5 r104 净室](prod-v5-20261023/prod-v5-cleanroom-deployment-migration-validation-20261024.zh.md)、[r106 业务重放](prod-v5-20261023/20261024-prod-v5-business-append-and-traffic-regression.zh.md) | [r104 PG 并发/旧计划 case](https://github.com/ai-workspace-services/accounts/blob/74442911247866edfa43217a51ff8a59a7ed1dcb/internal/migrate/full_business_postgres_test.go)、[r106 usage merge case](https://github.com/ai-workspace-services/accounts/blob/04c711bf73097be63827e990569abd72fc3b1bc9/internal/migrate/usage_merge_postgres_test.go) | 保留失败→修复 PR→相同输入重验；源鲜度不同、Sandbox 例外和 K3s 80,130 历史桶范围分别记录，不把例外写成全量零差异 |
| 完整回归清单与当前自动化 | [V3→V4 P0 事件映射](prod-v2-v3-20261019/20261021-prod-v3-v4-p0-regression-record.zh.md)、[K3s 23 项](prod-v5-k3s-20261025/deployment-migration-acceptance-checklist.template.zh.md) | [真实 P0 case 目录](https://github.com/ai-workspace-infra/playbooks/blob/a7a01ac734968aa6e5f7baec0e172ae06a0b461d/docs/cases/runbooks/2026-10-21-v4-p0-regression-cases.md)、[目录契约测试](https://github.com/ai-workspace-infra/playbooks/blob/a7a01ac734968aa6e5f7baec0e172ae06a0b461d/tests/data_operations/selfhost/v4_p0_regression_cases_test.py)、[新只读观测 role](https://github.com/ai-workspace-infra/playbooks/blob/a7a01ac734968aa6e5f7baec0e172ae06a0b461d/roles/v5_readonly_acceptance/README.md) | [Playbooks #764](https://github.com/ai-workspace-infra/playbooks/pull/764)已合并，只实现 23 项的只读子集；源码存在、目录单测或预期拒绝均不等于 23 项业务 PASS。本归档没有新执行回执 |

## 4. 历史交接如何被后续证据取代

| 观察 / 时点 | 原结论 | 后续证据及使用边界 |
| --- | --- | --- |
| 2026-10-23 早期目标采样 | Docker 未安装、仅 SSH、部署未完成 | 保留于[VPS 基线历史节](prod-v5-20261023/prod-v5-runtime-and-snapshot-baseline-20261023.zh.md)及[部署复盘](prod-v5-20261023/prod-v5-deployment-postmortem-20261023.zh.md)，不可当作现在状态 |
| 旧线程交接，精确采样起止未归档 | Docker 已安装、旧部署进程已停止，用户授权 IaC 重建 | 这是历史交接；授权本身不证明执行成功。后由 10-24 净室实际 run/exit 与恢复回执取代，进一步由 10-25 K3s 独立样本承接 |
| [Knowledge #196](https://github.com/ai-workspace-services/knowledge/pull/196)，本次复核仍 OPEN | 其分支描述 Docker 已安装、旧 apply 当时仍运行 | 未合并的历史样本，不重复提交、不继续作为当前结论；本次不关闭该 PR 或删除原证据 |
| [Knowledge #208](https://github.com/ai-workspace-services/knowledge/pull/208)，本次复核仍 OPEN | OS / DB 只读巡检与快照边界归档 | 统一流程先前引用的 inspection-access 回执尚在此 PR，未进入 Knowledge main；保留待审链接，本次不重抄执行材料或宣称已正式归档 |
| [Knowledge #210](https://github.com/ai-workspace-services/knowledge/pull/210)，本次复核仍 OPEN | 10-24 V5 VPS PostgreSQL 公共别名交接记录 | 该历史交接不等于 10-25 K3s 数据库隧道验收；不重复提交此 PR 的旧 DNS 证据，不新增 DNS 操作 |
| [Knowledge #222](https://github.com/ai-workspace-services/knowledge/pull/222)，已合并 | 初始 K3s UAT 综合报告 | 原有 PASS 属于当时报告范围；不能覆盖后续 PROD 的 Vault KV、一代写入权、完整恢复或真实遥测等证据缺口 |
| [Knowledge #223](https://github.com/ai-workspace-services/knowledge/pull/223)，本次复核仍 OPEN | UAT 数据库连接更正、身份初始化问题及 Vault 迁移规划 | 仍为待审修订，不把规划或旧综合报告直接当作 PROD 实施回执；本次不重复提交该修订 |
| [Knowledge #224](https://github.com/ai-workspace-services/knowledge/pull/224)、[#225](https://github.com/ai-workspace-services/knowledge/pull/225)、[#226](https://github.com/ai-workspace-services/knowledge/pull/226)，已合并 | K3s PROD 运行快照、角色/策略矩阵、PR 溯源 | 当前本轮整理所用最新归档；保留 PARTIAL/BLOCKED/NOT_RUN，不把文档合并当作完整切换验收 |

## 5. 复用及公开边界

新一轮填写[代际快照/恢复模板](prod-v2-v3-20261019/web-saas-generation-snapshot-recovery-template.zh.md)，并将 [23 项检查表](prod-v5-k3s-20261025/deployment-migration-acceptance-checklist.template.zh.md)复制为独立执行附件。使用通用逻辑身份和 evidence_id；真实主机/库身份、原始 state、备份及原始日志只在受控索引绑定，不提交 Token、密码、私钥、含凭据 DSN、密码/MFA 数据、Cookie 或个人身份。

只有取得对应固定候选的真实新回执，才能追加阶段成功。缺字段先定位受控原件，仍无法取证则保留缺口；不擅自删除原件、重新签造历史时间或把失败覆盖为成功。公共 DNS 与写入权的任何新操作仍需要独立的明确授权，本任务不执行。
