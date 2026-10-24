# K3s V5 PROD 目标数据库重建与身份重验回执

本记录追加在历史 UAT 目录中以保留原有链接；本轮目标按 PROD 管理。历史“全部通过”报告不能替代本轮证据。源端仍在线写入；迁移连接只读。公共 DNS、生产流量及原环境写入权切换均为 `NOT_RUN`。

## 本轮依据与固定版本

- run_id：`k3s-prod-rebuild-20261024`；时间基准：Asia/Shanghai。
- 源端：既有单机 V5 权威业务库；目标：独立 K3s V5 PROD，资源 ID、地址、PVC 和节点名保持原有身份。
- 用户明确授权目标 DB 可以重建。保留原目标库及重建前加密备份，未删除原生产库。
- Accounts 修复：[PR 274](https://github.com/ai-workspace-services/accounts/pull/274)、[PR 275](https://github.com/ai-workspace-services/accounts/pull/275)、[PR 276](https://github.com/ai-workspace-services/accounts/pull/276)。固定 release tag `v2026.10.25`，commit `3ef09c82f46152096bfc16edc9ba767f128a197f`，image digest `sha256:b5bf111a64ca2f2ed5e74d2ab1f87e0e164d09869a32832368fb43e577fdf37b`。
- GitOps：[PR 538](https://github.com/ai-workspace-infra/gitops/pull/538)、[PR 540](https://github.com/ai-workspace-infra/gitops/pull/540)；固定 tag `v2026.10.24.1`，commit `44d2f83eca4adad9fccf6cfc0f17ca688a31dfab`。所有 PR 检查通过后合并。
- Native schema `2026102002`，SHA-256 `f45db2423f11d9dcc7f3cc58c72b52228a27d7b6ccfc717faf2bbb56fa0498b1`；Billing schema `2026101902`，SHA-256 `a7133f3ef2ea9013a055cfd1442a7488d2b837f289e0f5d9b61624d4fde9bc53`。

## 数据复制及三轮验证

一致性源快照与复制窗口：2026-10-24 **22:11:09–22:20:38**。`migratectl copy-full-business` 回执为 `copied`、`source_read_only=true`、`full_business_equal=true`。本轮复制 75 张业务表，另有迁移版本表；不能把“76 个关系”误当成 76 张业务表。

| 类别 | 本轮快照条数 |
| --- | ---: |
| 用户 | 33 |
| 套餐 | 18 |
| 订阅 / 订阅记录 / 生命周期 | 7 / 13 / 5 |
| 配额 / 结算 Profile | 33 / 33 |
| 计费账本 | 80,132 |
| 分钟流量 / 检查点 | 80,130 / 49 |
| 会话 | 8 |

以源用户集合为准，没有额外累加种子账号。全部用户字段逐项比对无差异，包括邮箱、密码哈希、代理 UUID、组、权限与 MFA；不在文档保存这些字段的实际值。

- 身份修复三轮真实 preview/apply：每轮 33 用户、0 修改、退出码 0。
- 从迁移后加密备份恢复独立固定基线库，再执行三轮 `reconcile-business --migration-mode=replatform`：每轮 15 类业务表、0 追加、0 更新、0 冲突，退出码 0。不能将持续变化的三个源快照当成同一输入。
- 目标 Accounts 采用已管理 schema 的 primary 模式，后台初始化写入关闭。启动和显式重启后再次比对，33 用户全部字段仍无差异。
- 加密备份解密往返校验及独立恢复退出码均为 0；旧目标库继续保留。

## 故障与实际验收边界

1. 新库预检正确拦下缺失 Billing 附加表；按固定校验和补齐后重新预检并复制。
2. 复制外围脚本退出判定异常；检查工具 JSON 确认事务已成功，未重复全库复制。
3. PROD Chart 正确拒绝缺少 Secret 引用的 Content，导致 Accounts/Billing 未启动、认证接口出现 502。PR 540 补齐专属最小字段 Secret 后恢复。
4. Accounts 健康、MFA 查询、Billing 就绪均返回 HTTPS 200；未登录 session 返回 401。该结果只证明链路恢复，**真实密码与 MFA 登录仍待账号持有者验收**。
5. 观测升级发现共享 PVC 的滚动升级产生存储锁竞争；PR 540 改为 Recreate。完整指标、日志、trace、仪表盘和告警闭环尚未准出，不能沿用旧报告的全通过结论。

## Vault 与控制面状态

独立 Raft PVC 已恢复，真实后端为 Raft；原 File 实例保留。快照复制的 cluster ID 不能作为物理隔离证明。目标已独立 rekey，复制的生产 Token 与外部认证入口在目标侧撤销或限制，源身份不变。解封材料加密保存在目标节点之外。

内部 TLS 严格验证通过；Kubernetes 身份绑定专属 ServiceAccount、命名空间和 audience，TTL 5 分钟，授权路径 200、越界路径 403。影子 SecretStore/ExternalSecret Ready，业务 Secret 7 个字段和 TLS 2 个字段与当前目标完全一致后，才切换实际 ESO。

Flux 已读取固定 tag；目标应用与 Vault 声明 Ready。遥测声明使用 `cluster=web-saas-k3s-v5, environment=prod`；运行闭环仍需后续回执补证。

## 证据与索引

原始数据库备份、Vault 快照、解封材料、连接信息和完整比对记录保存在受控本机/目标证据目录，未提交到仓库。公开副本只保留版本、摘要、计数、状态和 PR。

- [历史基线](web-saas-k3s-v5-runtime-and-snapshot-baseline-20261024.zh.md)
- [既有身份与 Vault 规划](k3s-v5-core-identity-and-vault-smooth-migration-plan-20261024.zh.md)
- [先前验收纠偏](k3s-v5-database-routing-repair-and-acceptance-correction-20261024.zh.md)
