# V3 → V4 回归检查点与收尾清单

记录日期：2026-10-21，Asia/Shanghai。状态区分 PASS、FAIL、BLOCKED、NOT_RUN；人工探针结果与脚本 case 回执单列，不互相冒充。当前基线见[运行记录](prod-v4-runtime-and-snapshot-baseline-20261021.zh.md)，问题编号见[复盘](v3-v4-upgrade-retrospective-20261021.zh.md)。

2026-10-25 归档补链：[跨代回执、真实源码和后续重验](../generation-deployment-evidence-index-20261025.zh.md)。下表仍为 10-21 历史结果；[Playbooks #712](https://github.com/ai-workspace-infra/playbooks/pull/712)后已合并 `611cc12b443ea669dc1460e6597320acaed7a418`，不覆盖原“未合并”采样，不据此把待重验 case 改成 PASS。

## 历史脚本与真实结果

脚本归属 Playbooks：

- [regression_cases.py](https://github.com/ai-workspace-infra/playbooks/blob/e2b584716fd6770f64d2ba2a7c4137fa4117c7ae/roles/web_saas_generation_fresh/files/regression_cases.py)：SNI、域名、Token、采集入口、身份/数据与业务验收回执。
- [postgres_cases.py](https://github.com/ai-workspace-infra/playbooks/blob/e2b584716fd6770f64d2ba2a7c4137fa4117c7ae/roles/web_saas_generation_fresh/files/postgres_cases.py)：独立 PostgreSQL 17 fixture、迁移、冲突、幂等、重启与用户补同步。
- [入口重跑保护测试](https://github.com/ai-workspace-infra/playbooks/pull/712)：激活记录写入、恢复保留条件；未合并。

当前历史 regression 脚本的域名 case 仍以“五个公共域保留 V3”为候选预期。进入正式运行后，该预期必须按声明阶段参数化，再重新固定脚本 SHA；不能为追求 PASS 擅自把 DNS 改回去。其他含 fixture 未实现、默认 BLOCKED 的 case 也不能改写成通过。

## 运行回归矩阵

| case / 问题 | 预期 | 最近可复核证据 | 当前判断 |
| --- | --- | --- | --- |
| public-sni-cert / V4-03 | 五域与版本别名可信 TLS、证书只读挂载 | 旧候选 case PASS/0；本次 V4 五公共 SNI curl 成功、业务探针 200/www 301 | 当前基础边界通过；整个脚本未重跑 |
| public-host-completeness / V4-18 | 按阶段声明核实域名，www 保留 URI；DB 仅预留解析/隧道 | 当前 DNS 与旧候选预期不同；品牌修复另附回执 | 需阶段参数化并重跑 |
| runtime-secret-injection / V4-14 | 三服务实际进程等于权威 Key | 历史两个候选 PASS/0；本次未复核全部值 | 当前候选 NOT_RUN；不输出 Token 或散列 |
| billing-ingest / V4-04、15 | 缺/错 Token 401，管理及错误方法 403，合法样本幂等落库 | 本次缺 Token 401、management GET 403；旧 case 为 BLOCKED/2 或 FAIL/1 | 仅鉴权边界通过；正向去重样本待验 |
| exporter-vector / V4-04、20 | 每节点 Exporter→Vector→Billing→用量/账本，无双投 | DB 时间新鲜；历史完整 case BLOCKED/2 | 未证明逐节点完整性，不放行全链路 |
| agent-registration / V4-15 | 状态、配置、用户连接均成功 | 03:09 后真实状态 POST 多周期 204；旧隔离 case BLOCKED/2 | 注册上报运行恢复；全链路待验 |
| client-transport / V4-21 | node 非空、VLESS 路径与 Xray 一致、实际可连接 | 旧 case BLOCKED/2；历史截图报 node undefined | 当前 NOT_RUN |
| auth-callback / V4-07、21 | 实际登录/MFA/OAuth、Webhook/Sandbox 关联正确 | 登录页 200；旧 case BLOCKED/2 | 页面 200 不能代替会话与付款验证 |
| schema-data-protection / V4-11、12 | 完整源目标比较、身份/财务/配额冲突即停 | 旧 b598 候选先 FAIL/1 后 PASS/0；后 765ea 候选 FAIL/1 | 当前源目标比较待重验，不能只挑早期 PASS |
| repeat-deploy-restore / V4-16、20 | 同版无意外重启/重复写；含业务备份恢复且应用可连接 | 旧 case BLOCKED/2；历史业务恢复 passed；入口保护 5 项单测通过 | 当前全栈重跑/应用恢复连接待验 |
| business-runtime-role / V4-08、09、10、17 | account_user、权威密码、精确表权限、任务开关与声明一致 | 当前两服务连接及四表 DML 权限通过；后台开关 false | 配置不完全收敛，待核查 |
| writer-ownership / V4-01、22 | 一代承担业务写入，旧源禁止写，记录用户基线 | 本轮不读取源端，当前无完整单写入回执 | 待核查，不能推断已完成 |

## PostgreSQL fixture 回执

证据目录：`fresh-native-20261020-233500/`；最后一轮回执为 `postgres-cases-20261020T162919330798Z.json`，始于北京时间 10-21 00:29:19，约 00:32 完成。六类结果均 PASS、exit_code=0、skipped=false：

| case | 验证内容 | 结果 |
| --- | --- | --- |
| native-initialization | PG17 原生 schema 初始化 | PASS/0 |
| migration-concurrency-retry | 并发迁移、锁、重试 | PASS/0 |
| lifecycle-migration-rollback | 生命周期迁移与回滚保护 | PASS/0 |
| business-conflict-rollback | 业务身份/关联冲突事务回滚 | PASS/0 |
| usage-merge-conflicts | 用量合并冲突 | PASS/0 |
| late-users-single-backfill | 遗漏用户检测、单用户补同步 | PASS/0 |

更早两轮出现 business-conflict 和 usage-merge 失败，原回执保留。上述为隔离 fixture，不能当作当前生产库比较，也不能代表退款审核、多笔部分退款恢复、Schedule 及乱序 webhook 的 Stripe Sandbox 验收。

## 收尾任务与验收证据

下列 owner 为职责归属；具体责任人和时间应在对应实施任务排定，不伪造已分派状态。

| 优先级 | 事项 | Owner | 完成条件 |
| --- | --- | --- | --- |
| 高 | 正式运行配置逐层对账及后台任务策略 | GitOps / Playbooks / Accounts / Billing | 声明、落盘、实际进程、DB 权限、Caddy 模式、单写入者一致；真实业务写入正确 |
| 高 | #712 审查合并与固定版本重跑 | Playbooks | 必需检查与审查通过；新固定 ref；恢复重跑不覆盖正式入口，配置未变不重启 |
| 高 | 最终候选最新全量快照与恢复 | Playbooks / 备份 owner | 完整加密清单、同边界数据/schema、角色、配置、隔离恢复、应用连接、异地副本回执 |
| 高 | 当前源目标只读核验和例外清单 | Accounts migratectl / 迁移 owner | 同口径身份及记录/配额/用量/账务指纹，明确被接受的滞后；冲突不覆盖 |
| 高 | 逐节点采集和 Agent 连接 | Proxy / Vector / Billing / Accounts | 每节点至少两个完整相关采集周期、状态新鲜、无401/403、配置下发、连接成功、无双记账 |
| 高 | 实际认证、OAuth、Webhook 和 Sandbox | Accounts / Portal / Billing | 登录/MFA、provider 回调、退款审批/执行、部分恢复、Schedule、幂等和乱序事件回执 |
| 中 | 回归脚本适配阶段和目标，去硬编码 | Playbooks / Accounts | candidate/primary 预期来自声明，Vnext 无固定 V2/V3/V4 检查，必测缺 fixture 仍阻断 |
| 中 | 旧 DB 角色与演练库生命周期 | DB owner | 先查 LOGIN/成员/owner/依赖和保留期，审查后精确回收；不因文档生成而删除 |
| 中 | 回退与异地恢复方案 | 运维 / 数据 owner | 镜像与配置恢复点、写入后数据收敛方向、停止条件、演练及授权点明确 |

稳定观察必须记录实际起止、相关业务周期和失败阈值。旧 180 秒观察只覆盖 Doco-CD 且当时 Billing 失败，不能复用为当前稳定通过。当前这次只读盘点也不是一个完整的稳定观察任务。

## V5 后续重验索引

历史故障按本清单采样背景保留。对应 [V5 在线业务追加与流量重验](../prod-v5-20261023/20261024-prod-v5-business-append-and-traffic-regression.zh.md)区分历史账务导入、公共入口真实转发、Exporter 凭据和新入库周期；未执行项不继承本代结论。
