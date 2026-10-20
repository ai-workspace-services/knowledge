# V3 → V4 主线候选与实际验收检查点（2026-10-21）

结论：**不可切换**。V3 继续在线服务并保有公共流量及写入权。未冻结源、未切公共 DNS、未执行真实扣款或退款、未将 V4 登记为下一轮来源。

## 主线不可变基线

收到从 main 固定候选的授权后，创建候选 tag `prod-v4-acceptance-2026.10.21-r1`。它是代码基线，不是验收通过或正式发布声明；后续修复必须用新 tag，不能移动此 tag。

| 仓库 | tag 对应 main SHA |
| --- | --- |
| GitOps | `28044ec777e1ed012ad58aeb4577db0403719d4f` |
| Playbooks | `551730ce7917ae1f8869a24031c3a73335d488cd` |
| Accounts | `6565297116c502c1b89557b201234f9d6e8f5e08` |
| Billing | `22cbfc06d3fe030c2d32fa076335853fa6aa2865` |
| Portal | `22e1485bad13995caa4012316c9cf0012e265059` |
| IaC modules | `cc15b90aa2c463e57618b574b2764cc2e4470720` |

主线 GitOps 尚无 V4 声明，主线 Billing 不接受原生 schema `2026102002`。因此**没有将这个主线 tag 交给 Doco-CD**；不能把原分支演练结果移作此 tag 的通过证据。

## 已执行的 V4 分支演练：与主线候选分开记录

- 执行链路：GCP SSH → Playbook → 固定 GitOps commit → Doco-CD，无 CI 部署。
- run_id：`v3-v4-native-20261020-233500`。
- V4 GitOps 实际选择：`b5987fefc5e591e0fdba33c684ca83766a16ff37`，属于草稿 PR，不是 main tag。
- 迁移工具来源：Accounts `6565297116c502c1b89557b201234f9d6e8f5e08`，二进制 SHA-256 `00b276dba8008900e84a1fb1f5231789643a4ab0a84726793a4eb32b3b2433b1`。
- 原生 schema SHA-256：`f45db2423f11d9dcc7f3cc58c72b52228a27d7b6ccfc717faf2bbb56fa0498b1`；Billing 附加 SQL SHA-256：`a7133f3ef2ea9013a055cfd1442a7488d2b837f289e0f5d9b61624d4fde9bc53`。未修改历史 migration/checksum。
- V4 新建独立原生 `account` 库，再从 V4 上保留的 V3 只读快照库单向同步。没有清理旧业务库或演练库。
- V3 快照边界：2026-10-20 12:26:27 UTC；归档 SHA-256 `d09ad7a6ba1cfeb426196fe6c89789af2183b7440f6754e7857c7f36f410725d`。V3 持续服务，所以这不是当前零延迟追齐证明。
- 对齐后：33 用户、13 订阅、35306 账本记录，schema `2026102002`，dirty=false。完整只读比较通过，无目标写入。
- 数据保护：目标空库备份隔离恢复通过；含业务数据的加密备份再次隔离恢复，业务行、schema、表/序列权限指纹一致，应用角色可查询。**尚未完成真实应用进程连接恢复库的验收**。
- V4 应用仅有只读数据库权限，生产采集器和 Agent 没有改投 V4，不双投记账。

## 阶段 0–7 状态

| 阶段 | 分支演练事实 | 主线 tag 放行 |
| --- | --- | --- |
| 0 固定构件 | 固定 commit/digest/SQL；主线候选 tag 已创建 | BLOCKED：主线缺 V4 声明及 Billing 修复，Portal 最新镜像还需对齐 |
| 1 前置检查 | V4 独立数据盘、版本解析、证书、源保有流量已核验 | 不转用旧证据 |
| 2 全新部署 | Accounts/Console/Caddy 已运行；Billing 不接受新版 checkpoint | FAIL |
| 3 核心数据对齐 | 对保留快照完整比较通过 | 实时最终追齐不在本轮 |
| 4 业务备份恢复 | 加密备份、隔离恢复、数据/schema/权限相等 | BLOCKED：应用连接恢复库待验 |
| 5 历史回归 | TLS/域名/Token/数据比较通过；Billing 失败，端到端依赖阻断 | FAIL/BLOCKED |
| 6 重跑与恢复 | 相同 Doco-CD 选择重跑 changed=0，未重建控制器 | BLOCKED：全栈健康重跑、迁移并发/重启/遗漏用户 fixture 待验 |
| 7 稳定观察 | 单独保留观察回执；Billing 故障不能算稳定通过 | 不可切换 |

## 历史 case 实际执行

所属脚本：Playbooks `roles/web_saas_generation_fresh/files/regression_cases.py`，具体问题引用、脚本 hash、预期、起止时间、退出码及实际检查保存在逐 case JSON。

| case | 最新结果 | 退出码 |
| --- | --- | --- |
| public-sni-cert | PASS：五个公共 SNI 和三个 HTTPS 版本别名证书可信、只读挂载 | 0 |
| public-host-completeness | PASS：四个版本别名指向 V4，公共五域仍 V3，www 跳转保留 URI | 0 |
| runtime-secret-injection | PASS：三服务运行配置与权威 Vault Key 一致，仅输出布尔结果 | 0 |
| schema-data-protection | PASS：完整业务比较，无目标写入 | 0 |
| billing-ingest | FAIL：后端重启导致 502，不能宣称采集入口通过 | 1 |
| exporter-vector / agent-registration / client-transport / auth-callback / repeat-deploy-restore | BLOCKED：独立完整 fixture 和健康运行条件未就绪 | 2 |

首轮数据 case 因 Doco-CD 重建 PostgreSQL 容器导致 `/tmp` 工具消失而失败，未据此认定数据差异。随后从保留的主机检查点核对原二进制 SHA 并重新注入，重跑比较通过；失败回执保留。另发现 compare 默认 dry-run 仅预检，已显式执行完整比较并核对 equal=true，未使用预检冒充数据一致。

私有脱敏证据根目录：`/data/backups/web-saas/prod-v4/fresh-native-20261020-233500/`，包括 `verify-full.json`、`post-sync-restore.json`、`cases/b5987fefc5e591e0fdba33c684ca83766a16ff37/`。备份和凭据不得提交仓库。

业务备份归档 SHA-256：`c82e0bbfb4237770cded91986a9a8f230cfba6520cf607589c1438eac7e5a109`；恢复库 `fresh_after_verify_20261020233500`；恢复前后业务行指纹均为 `f257cd457dffdfc03285ee8d94934355ba3dbd3684ce8b671d5c6de3a22717e2`，schema 指纹 `8e6e55a1a5373d16f5cdcc5a9fb7cdc2e8ec82aa58544e280e88a95c418862d7`，权限指纹 `cc65f0ffdbabe78cb93a4c1f5964051a5e18ce4074c57160f32628b8f5fd4d58`。

观察实际起止：2026-10-20 16:06:10.231874 UTC 至 16:09:10.343903 UTC（本地 2026-10-21 00:06:10 至 00:09:10），180 秒、60 秒一次、4 份五服务状态采样，覆盖 3 个 Doco-CD 轮询间隔。结果 FAIL：Billing 未健康收敛；**不能将 Doco-CD 轮询周期替代 Exporter/Vector 的相关业务采集周期**，后者仍未验证。回执 `observation-20261021.json`。

## 修复与后续门禁

- [GitOps #475](https://github.com/ai-workspace-infra/gitops/pull/475)：V4 声明与不可变镜像。
- [Playbooks #703](https://github.com/ai-workspace-infra/playbooks/pull/703)：统一新部署/恢复入口、原生数据演练和 case 回执。
- [IaC #454](https://github.com/ai-workspace-infra/iac_modules/pull/454)：四个版本别名的受控准备。
- [Billing #53](https://github.com/ai-workspace-services/billing-service/pull/53)：仅允许审核过的 2026102002 checkpoint，拒绝 dirty/关系漂移/未知版本；针对性及全量 Go 测试通过，未发布修复镜像。

上述均为草稿，未推定合并授权。先审查修复并生成新的主线候选 tag 和镜像 digest，再重跑受影响阶段及下游依赖；不能沿用旧候选 PASS。隔离 Collector/Agent、OAuth/Stripe Sandbox、并发/重试/重启/单用户补同步必须补齐；不少于两个完整相关采集周期，记录实际起止和周期，未完成即阻断。

本轮不执行切换。未来另获人工明确授权后：冻结源业务写入、排空事务、最终只读预览及无冲突追齐、记录用户 UUID 基线、核验数据与 schema、移交单写入权、切流量。旧代际保持禁写候选；失败停止，不自动破坏性降级或回切数据库，保留恢复构件。切换后稳定验收通过前，V4 不作为下一轮来源。
