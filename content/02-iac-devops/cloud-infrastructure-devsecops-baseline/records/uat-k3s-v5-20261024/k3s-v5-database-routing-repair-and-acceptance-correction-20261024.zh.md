# Kubernetes UAT：数据库连接修复与验收结论更正

记录日期：2026-10-24，Asia/Shanghai。接手诊断及修复窗口约 20:38—20:48；完整起止以受控执行记录为准。run_id：`k3s-uat-takeover-20261024`。本文为实测追加回执，不覆盖此前材料的时间背景。

[先前验收报告](web-saas-k3s-v5-data-migration-vault-recovery-observability-acceptance-20261024.zh.md) · [增强准入方案](k3s-v5-migration-enhanced-guardrails-20261024.zh.md) · [运行基线](web-saas-k3s-v5-runtime-and-snapshot-baseline-20261024.zh.md)

## 1. 登录异常的实际原因与修复

用户报告迁移后登录失败。只读复核发现迁移数据已位于权威业务库，但 Accounts 与 Billing 仍通过 Secret 中的旧 DATABASE_URL 连接初始化库。仅更新 DB_NAME 环境变量与 PostgreSQL 初始化参数并未改变应用实际连接。

证据：迁移库有 33 名用户，初始化库有 3 名用户；pg_stat_activity 显示两个业务服务连接初始化库。源/目标全部 33 名用户的 31 个字段在内存中比较，无缺失、无额外用户、无字段差异，包含密码哈希和 MFA。管理员在源与迁移库均启用 MFA，但修复前 UAT API 返回 MFA 未启用，表明 API 没有读取迁移库。

修复进入 [GitOps #536](https://github.com/ai-workspace-infra/gitops/pull/536)，8 项 CI 检查通过后 squash 合并；固定 merge commit 为 `2d678835f03254ea0b6b0176d33cb5518a7b6499`。ExternalSecret v2 模板固定目标数据库路径，保留凭据、连接参数及其他 Secret 字段。服务端 dry-run 通过。Flux 两个 Kustomization 已应用该 commit，生成的 Secret 数据库路径正确；仅滚动重启目标 Accounts 和 Billing，rollout 均成功、退出码 0。

修复后 pg_stat_activity 显示两个业务服务均连接迁移库；Console 与 Accounts 的 MFA 状态 API 均以 HTTP 200 返回已启用，与源端一致。未重置密码、未关闭 MFA、未重写用户，也未删除旧初始化库。

**真实账号登录尚待账号持有者完成动态验证码并确认业务页面；上述证据不能代替真实登录验收。**

## 2. 数据复核、备份与隔离恢复

- PostgreSQL 实测为 17.11；公共 schema 76 表；schema_migrations 为 2026102002、dirty=false。
- 本轮采样：用户 33、套餐 18、订阅 7、会话 8、账本 79,236、分钟流量 79,234，与原报告目标数量一致。
- 使用只读事务分别核对源和目标 76 表的内容摘要，70 表相同；差异为配额、智能体、节点健康、账本、分钟流量和检查点。该采样源账本 79,467、目标 79,236，源分钟流量 79,465、目标 79,234；源持续写入，差异不是零延迟同步证明，也不能单凭数量判断历史漏迁。仍需显式增量窗口及工具支持核验后才可追加。
- 目标迁移库与初始化库均保存加密逻辑备份，解密往返验证通过。备份仅保存于本机受控私有证据目录，权限受限，未上传仓库。加密依赖本机既有 SSH 私钥的完整内容派生口令，恢复需保留对应原始密钥；密钥未写入证据或仓库。
- 迁移库备份已恢复至独立 UAT 校验库，pg_restore 退出码 0；校验用户 33、套餐 18、账本 79,236、流量 79,234、版本 2026102002、dirty=false。校验库保留，未挂接业务服务。

本轮未重新执行数据复制，未验证迁移工具重放幂等；数据库备份恢复成功不等于业务验收成功。

## 3. Vault：此前完整恢复结论证据不足

实测目标 Vault 为 1.21.4，initialized=true、sealed=false，但 **storage_type=file**，配置也明确使用 File 后端。PVC 10Gi 已绑定，不能因此认定报告所称的完整 Raft 快照恢复已完成。需补正确恢复路径、源快照来源、版本与 seal 兼容、解封、对象完整性和目标身份收敛证据。

ESO 的 SecretStore 当前仍指向源端生产 Vault，并非目标本地 Vault。本轮修复通过 GitOps 模板完成，未写源 Vault。不能将“目标 Vault 运行”误当成“ESO 已完成目标凭据切换”。

用户指定通过现有 GCP SSH 获取恢复材料；当前 gcloud 认证刷新失败，提示需重新登录。完整恢复标记 BLOCKED，待认证恢复后继续受控核验，未删除或覆盖现有 Vault 数据。

## 4. 观测：健康通过但全链路未通过

只读配置与查询表明：

- 5 容器运行；Grafana 健康接口正常。
- Prometheus 抓取配置仅包含 VictoriaMetrics 自身；count(up)=1。
- 查询具有目标集群及 environment=uat 标签的指标为空。总时序数量 1,056 不证明目标业务覆盖或标签隔离。
- OTel traces pipeline 仅导出 debug；metrics 导出 Prometheus，但抓取配置没有对应 Collector exporter；没有 logs pipeline。
- 因此不能认定真实业务指标、日志、trace、仪表盘及告警全链路验证通过。此轮没有修改生产观测或宣称修复完成。

## 5. 本轮阶段判定

| 阶段 | 判定 | 说明 |
| --- | --- | --- |
| 用户全字段对账 | PASS（采样时刻） | 33 用户、31 字段，无差异 |
| 应用数据库连接修复 | PASS | GitOps 合并、Flux 应用、进程连接和 MFA API 已复核 |
| 数据库加密备份与隔离恢复 | PASS（数据库层） | 恢复退出码 0，关键数据及迁移状态符合备份 |
| 持续增量迁移 | NOT_RUN | 源持续写入，未宣称追平 |
| 迁移重复执行幂等 | NOT_RUN | 本轮没有重跑复制 |
| 真实账号业务验收 | BLOCKED | 待持有者完成登录与业务确认 |
| Vault 完整恢复及 ESO 本地切换 | BLOCKED | 后端/接入不符，恢复身份访问待补 |
| 观测业务全链路 | BLOCKED | 抓取、标签和 OTLP 路由存在已确认缺口 |
| 生产切流 | NOT_RUN | 未改公共 DNS、未冻结源业务写入 |

原始查询内容、个人数据、凭据、密码哈希、MFA 材料及备份均不进入公开档案。源端仅作只读诊断；完整验收须在阻断项关闭后追加新回执。


## 后续规划与重新认证补充

用户已完成 GCP 重新认证，SSH 与受控恢复材料入口已核实，故此前认证阻断仅保留为历史状态。独立 Raft 目标声明已合并，但尚未完成恢复。应用启动后再次核对出现内置 sandbox/review 账号更新，其中包含 review 密码及组变化，不能扩大既有例外自动放行。[用户与核心身份及 Vault 平滑迁移规划](k3s-v5-core-identity-and-vault-smooth-migration-plan-20261024.zh.md)列出初始化整改、同输入三轮幂等、完整 Raft 恢复和 ESO 影子切换门槛。


## PROD 后续执行回执

历史采样保留；当前进展见[数据库重建与身份重验回执](k3s-v5-prod-rebuild-and-identity-revalidation-20261024.zh.md)。真实登录与完整遥测验收分开报告。
