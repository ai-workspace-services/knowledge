# V2 → V3 升级关联 P0：Vector 流量入库被入口规则阻断

时区：Asia/Shanghai（北京时间）。事件编号：`P0-V3-BILLING-INGEST-20261020`。

## 影响与当前结论

V3 Accounts/Console 正常响应，Agent 也持续心跳，但 Billing 的公开入口沿用了恢复演练的 probe-only 策略，仅允许健康检查。Vector 发往 `POST /v1/ingest/snapshots` 的流量被 Caddy 返回 403，导致实时用量和账本停止更新。`/readyz=200` 只能证明数据库连通，未覆盖采集数据面。

本轮保持 **Xray Exporter → Vector → Billing → PostgreSQL**。未启用 Billing 主动拉取，未让 Agent 绕过 Vector，未回灌或修改 V2。共享凭据权威来源为 `kv/prod/accounts/runtime` → `INTERNAL_SERVICE_TOKEN`；使用独立 scoped credential 的 Agent 保留独立授权。

## 升级与事件时间线

| 北京时间 | 事件 | 证据与解释 |
| --- | --- | --- |
| 2026-10-18 01:21:45 | V2 r5 对账完成 | V2 历史恢复记录；不是本次 P0 修复时间 |
| 2026-10-19 17:02:04 | V2 一致性快照跨机恢复到 V3 | 33 用户、13 订阅、32,847 条账本；后续受控升级到 `2026101902` |
| 2026-10-19 17:03 | 修复前 V3 所见最新账本业务区间结束 | 最新实际写入为 17:02:04 左右，来自旧快照；不能据此认定网络故障恰在 17:03 开始 |
| 2026-10-19 20:54 | V3 共享服务令牌一致性验收 | Accounts/Billing/Console 从 canonical Vault Key 统一取值；令牌一致不代表 Vector 上报已通 |
| 2026-10-19 23:02:02 | VLESS 路径 P0 修复应用启动 | `prod-v3-vless-path-2026.10.19-r1`；该修复没有验证 Billing 新数据入库 |
| 2026-10-19 23:16:28 | V3 最新逻辑全量快照创建 | 隔离恢复通过，但快照中的账本仍为 32,847；备份验证不代表在线采集正常 |
| 2026-10-20 10:41–10:43 | 用户截图与只读排查 | 全部历史流量桶最近一小时为零；六个节点存在新鲜心跳；SG/PH Vector 持续 403 |
| 2026-10-20 10:43 | 根因交叉确认 | 公网采集 GET=403、直连 Billing GET=405；线上 Caddy 与 Role 均无采集放行；DB 角色可写 |
| 2026-10-20 10:47:47–10:49:52 | SSH/IAP → Playbooks 修复 V3 | IaC CMDB 限定目标，校验证书/SAN，在固定 Caddy 镜像中离线校验、保留旧配置，然后仅重启 Caddy |
| 2026-10-20 10:49:52 | Caddy 新配置生效 | Accounts/Billing/Console/PostgreSQL 启动时间保持不变 |
| 2026-10-20 10:50:27 | 首次确认真实入库恢复 | 账本由 32,847 增至 32,852，最新业务区间至 10:51；两个既有 XHTTP 数据通道出现新流量桶 |
| 2026-10-20 10:52:06 | 第二次确认持续增长 | 账本达 32,863；两个通道分别有 5 / 11 个近十分钟流量桶，checkpoint 时间继续前进 |

17:03 到次日修复约 17 小时 47 分钟是 **V3 中已观测到的业务数据断档跨度**，不是已精确定位的网络故障持续时间。公共 DNS 每次切换的准确时间尚未从独立审计记录重建，不补写推测时间。

## 根因与修复

正式 owner：[Playbooks PR #699](https://github.com/ai-workspace-infra/playbooks/pull/699)。

`roles/web_saas_public_ingress/templates/public-sites.caddy.j2` 原先只代理 `GET/HEAD /readyz /healthz /api/ping`，其余请求统一 403。修复仅放行 `POST /v1/ingest/snapshots`，Authorization 原样转发，由 Billing 执行已有 Bearer Token 验证。其他方法及管理/job 路径保持拒绝。

Role 增加默认关闭的 `web_saas_public_ingress_activate`。显式激活时才重启选定代际的 Caddy；Caddy 管理 API 在当前恢复配置中关闭，不能把单纯写文件称为在线配置已生效。旧配置有备份，回退时只处理入口配置，不自动回退数据库。

鉴权验收：

| 请求 | 修复后 |
| --- | --- |
| 采集 POST，无 Token | 401 |
| 采集 POST，错误 Token | 401 |
| 采集 GET | 403 |
| 管理 `/v1/status` GET | 403 |

没有发送伪造有效采集负载、创建测试用户或人工账务记录。新增账本来自真实采集链路。

## 逐节点验收边界

排查时已核对 SG Free、US Free、PH、日本 `jp-xconnect-01` 的 Vector 配置、运行服务与投递 Token；四者 Vector Token 均与 canonical Vault Key 相同。JP Free 和 `jp-xconnect` 当时 SSH 鉴权未通过，其 Agent 心跳和数据库采集通道单独核验，不伪称已经检查全部主机的本地日志。

首个恢复窗口已看到 `prod:agent-server-free-prod-v2-xhttp` 与 `prod:jp-xconnect.svc.plus-xhttp` 的新流量桶。旧的 exporter `node_id` 名称不因控制面改为 V3 自动更名，也不能只凭后缀判定请求仍发往 V2。

空 samples 不会产生用户流量桶，不能仅以无新增桶判定节点投递失败。仍需结合 exporter 最新快照、样本数量、Vector 投递结果和 Billing 接收结果逐项验收；节点局部问题继续跟踪，不把两个通道恢复扩大为全部节点全部线路验收通过。

后续只读检查同时核对了 exporter 的环境与命令行参数，得到以下补充：

| 节点/通道 | 本轮状态 | 后续 |
| --- | --- | --- |
| `agent-server-free-prod-v2-xhttp` | checkpoint、桶和账本已恢复前进 | 保留原 node_id，继续观察 |
| `jp-xconnect.svc.plus-xhttp` | checkpoint、桶和账本已恢复前进 | SSH 本机鉴权仍需另行核实 |
| SG Free | exporter Token 正确，最新快照新鲜但 samples=0；此前有 Vector 403 | 未宣称流量桶恢复；排查空样本/本地采集状态 |
| PH | exporter Token 正确，最新快照新鲜但 samples=0；此前有 Vector 403 | 未宣称流量桶恢复；排查空样本 |
| US Free | Vector Token 正确，exporter 进程有效 Token 缺失，快照停止更新 | 单独修复 exporter 凭据注入后验收 |
| `jp-xconnect-01` | Vector Token 正确，exporter 进程有效 Token 缺失 | 单独修复 exporter 凭据注入后验收 |

美国与日本节点是 **exporter** 缺少 Token，不能表述为 Vector 的 Token 不一致。本轮遵守“只修复 Billing 入口 403”的范围，没有重启或修改远端 exporter、Vector、Agent 或 Xray。Accounts、Billing、Console 三个运行容器已在本轮重新与 canonical Vault 值做内存比对，结果均一致；没有输出值或其散列。

## 断档数据与安全跟进

- 当前入口恢复与历史断档补齐分别处理。Exporter 的 72 小时保留、Vector 磁盘 buffer 不能直接证明未丢消息；先预览覆盖范围、counter reset、重复批次及账务冲突，再决定受控重放。
- Caddy 403 可能使投递端按不可重试错误处理；累计计数差值后来入库也不保证原分钟时间分布已完整恢复。不得人工补造用量或直接覆盖财务记录。
- 诊断中曾因 DSN 格式识别错误使数据库凭据进入工具输出。未复述或写入本记录；需要独立受控轮换，本文不宣称已经完成。
- 备份成功保护的是快照边界内已有数据；本次新发现的采集断档不被此前“恢复零丢失”的结论覆盖。

## 后续升级验收补充

Vn→Vn+1 的放行须同时验证：公共 SNI、采集 POST 鉴权、真实 Vector 投递、目标库 checkpoint/分钟桶/账本连续增长及关键节点覆盖。Agent 心跳与 API 健康不能替代。稳定后才把目标代际作为下一轮来源。

关联：[历史总索引](../../15-prod-v2-v3-snapshots-and-upgrade-retrospective.zh.md)、[快照与升级复盘](20261019-prod-v2-v3-snapshot-and-upgrade-retrospective.zh.md)、[共享令牌修复](20261019-prod-v3-canonical-service-token.zh.md)、[VLESS 路径 P0](20261019-prod-v3-vless-path-p0-release.zh.md)、[V2→V3 数据恢复](v2-to-v3-snapshot-refresh-20261019.zh.md)。

## 跨代归档回链

[统一流程](https://github.com/ai-workspace-services/.github/blob/main/docs/control-plane-deployment-and-migration.zh.md) → [跨代基线、逐轮回执、真实 case 与重验](../generation-deployment-evidence-index-20261025.zh.md)。本页保留原采样、固定构件和结果；后续成功不覆盖历史失败，源码/PR 状态不代替本页的真实运行回执。
