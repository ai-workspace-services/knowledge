# PROD V3 → V4：运行基线、快照与升级复盘

更新：2026-10-21，Asia/Shanghai。现场核验窗口约 03:16–03:22。

以下运行事实与 PR 的 OPEN 状态均以原核验窗口为界。2026-10-25 补链：[跨代证据、固定源码 case 与重验](records/generation-deployment-evidence-index-20261025.zh.md)；[Playbooks #712](https://github.com/ai-workspace-infra/playbooks/pull/712)后已合并，merge SHA `611cc12b443ea669dc1460e6597320acaed7a418`。合并不替代本页候选的重新部署/回归。

V4 已承接 Console、Accounts、Billing 三个公共服务域名；正式 Caddy 入口已激活，Agent 状态上报恢复。03:27 按用户补充授权将品牌两域也对齐 V4。**这不等于整轮升级全部验收完成**：后台写入开关仍关闭、最新全量快照候选缺完成回执，部分业务回归仍无当前版本通过证据。

环境盘点只读取线上状态并整理文档，没有生成新快照、同步数据、重启服务或执行扣款退款。随后获明确授权的品牌 DNS 变更单独留证，此前入口修复也单独记录。

| 阅读目的 | 文档 |
| --- | --- |
| 当前主机、固定构件、配置、权限、数据及快照 | [V4 运行基线与快照清单](records/prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md) |
| 过程、全部已识别问题、原因、修复和未闭环项 | [V3→V4 升级复盘](records/prod-v3-v4-20261020/v3-v4-upgrade-retrospective-20261021.zh.md) |
| 每个历史问题对应的脚本、预期及证据缺口 | [回归检查点与收尾清单](records/prod-v3-v4-20261020/regression-and-closure-checklist-20261021.zh.md) |
| 品牌根域/www 从 V3 补齐到 V4 | [03:27 DNS 变更回执](records/prod-v3-v4-20261020/brand-dns-handoff-20261021.zh.md) |
| 较早候选版本与当时不可切换的结论 | [主线候选验收历史记录](records/prod-v3-v4-20261020/main-candidate-acceptance-20261021.zh.md) |
| 上一轮升级及事故来源 | [V2→V3 历史索引](15-prod-v2-v3-snapshots-and-upgrade-retrospective.zh.md) |
| V4 保持服务时的 V5 部署中断、证据边界与恢复门禁 | [V5 部署复盘](records/prod-v5-20261023/prod-v5-deployment-postmortem-20261023.zh.md) |
| 可复用记录格式 | [代际快照与恢复模板](records/prod-v2-v3-20261019/web-saas-generation-snapshot-recovery-template.zh.md) |
| V5 VPS 历史采样、后续净室部署与实际恢复点 | [V5 VPS 运行基线与快照清单](records/prod-v5-20261023/prod-v5-runtime-and-snapshot-baseline-20261023.zh.md) |
| V5 K3s PROD 后续承载与独立验收状态 | [V5 K3s all-in-one 运行基线](records/prod-v5-k3s-20261025/prod-v5-vps-to-k3s-runtime-and-acceptance-20261025.zh.md) |

## 本次核验得到的关键事实

- Doco-CD 固定 `refs/tags/v2026.10.21-r4`，实际解析 GitOps `cbdd876e088176e10128cc5f9f3153b82c0500e4`，target=`prod-v4`，60 秒轮询。
- Accounts/Billing 业务连接均为 `account_user`，四张检查表的 SELECT/INSERT/UPDATE/DELETE 权限均具备；后台写入开关仍为 `false`，与数据库权限、HTTP 请求入口是不同控制面。
- PostgreSQL 17.10，`account` schema=`2026102002`，dirty=false；用户 33，`subscription_records` 13，`subscriptions` 1，配额状态 33。两张订阅表口径不可混用。
- 同一只读事务中流量桶与账本均为 35,369 条；另一次查询的两表最新时间约为 03:17:53，说明该时刻存在新数据。尚未逐节点证明采集完整性或历史断档补齐。
- 五个公共 SNI 直连 V4 可完成可信 TLS 请求；初次盘点服务三域到 V4、品牌两域到 V3，03:27 品牌两域也已补齐 V4，权威及两个公共 resolver 验证通过。
- 03:09 入口修复后，Agent 状态 POST 连续多个周期返回 204。持久修复 [Playbooks #712](https://github.com/ai-workspace-infra/playbooks/pull/712) 仍 OPEN，不能记为已合并。

## 证据使用规则

同一记录必须绑定候选 SHA、digest、SQL checksum、run_id 和采集时间。旧快照恢复通过、早期集成测试通过、当前探针通过分别陈述；不能拼成一个实际上没有执行过的完整验收。原始备份、数据库内容、凭据和用户标识不进入 Knowledge。

当前已接收 V4 写请求，不能直接把公共 DNS 回指旧库作为数据库回退。具体恢复计划应先判断新写入、数据差异和单写入者状态，再另行审核执行。完成正式稳定验收前，不把 V4 登记为下一轮来源。

## 代际关联与重验入口

统一流程：[Selfhost 控制面部署与核心数据迁移](https://github.com/ai-workspace-services/.github/blob/main/docs/control-plane-deployment-and-migration.zh.md)。本轮由[V4 运行基线](records/prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md)、[回归清单](records/prod-v3-v4-20261020/regression-and-closure-checklist-20261021.zh.md)、[域名交接](records/prod-v3-v4-20261020/brand-dns-handoff-20261021.zh.md)和[V3→V4 P0 case 记录](records/prod-v2-v3-20261019/20261021-prod-v3-v4-p0-regression-record.zh.md)组成；下一代入口为[V4→V5 基线与复盘](17-prod-v4-v5-baseline-and-upgrade-retrospective.zh.md)。各 case 的原时间与 PASS/FAIL/BLOCKED/NOT_RUN 状态以对应回执为准。
