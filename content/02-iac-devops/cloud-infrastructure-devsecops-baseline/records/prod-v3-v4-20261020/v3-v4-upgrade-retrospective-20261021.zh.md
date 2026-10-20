# V3 → V4 升级复盘：从候选恢复到正式运行

记录：2026-10-21，Asia/Shanghai。关联[运行基线](prod-v4-runtime-and-snapshot-baseline-20261021.zh.md)、[历史 V2→V3 事件](../../15-prod-v2-v3-snapshots-and-upgrade-retrospective.zh.md)与[回归清单](regression-and-closure-checklist-20261021.zh.md)。

## 1. 目标、影响与证据边界

目标是 V4 全新部署，从 V3 只读取数并审查后单向对齐核心业务，独立验证恢复能力，再由人工放行正式运行和流量。源继续服务；创建在线快照本身不需要停止 Accounts、Billing、Console、Caddy 或 Doco-CD。

已识别影响包括：候选阶段登录失败、VLESS 配置无法生成、Billing 对新版 schema 不兼容、服务角色权限不足、候选入口误用于公共服务导致 Agent 403，以及构件、快照、域名和正式模式未作为同一交付状态收敛。本记录不虚构总故障时长、受影响用户数量或数据损失；缺完整起止回执的事件明确待核实。

历史案例曾在 V3 验证，也在 V4 的配置路径重现。根本改进是把部署/恢复共用准备逻辑、候选与正式模式、真实进程配置、业务闭环以及回执绑定纳入同一工作流；不能用 readyz、文档或合并状态代替现场验收。

## 2. 可确认时间线

以下 PR 时间是 GitHub 合并时间转为北京时间，不是故障发生或部署完成时间。

| 北京时间 | 事件与证据 | 不能据此推断的事项 |
| --- | --- | --- |
| 10-20 19:51 | [Playbooks #702](https://github.com/ai-workspace-infra/playbooks/pull/702) 合并：在线 MVCC 快照、恢复演练及最终写入门禁分离 | 不代表 V4 应用或切换验收完成 |
| 10-20 20:26:27 | 一份 V3 只读归档边界，之后在 V4 恢复，33 用户/13 订阅/35,306 账本 | 不是源后来持续写入后的最新追齐 |
| 10-20 23:50:25 | V4 含业务数据备份隔离恢复回执 passed | 不代表实际应用已连接恢复库 |
| 10-21 00:18–00:28 | GitOps #475/#476、Playbooks #703/#704/#705 相继合并；全新原生候选、TCP readiness、独立会话权限 | 候选权限不能直接用作正式业务权限 |
| 10-21 00:29–00:32 | 最后一轮 PostgreSQL fixture 六类 case PASS；更早失败回执保留 | 不覆盖随后每个运行候选版本 |
| 10-21 01:15 | [Playbooks #706](https://github.com/ai-workspace-infra/playbooks/pull/706) 合并：专用 reader 与代际参数化 | 只读审计身份不能成为业务身份 |
| 10-21 01:36–01:48 | #707/#708/#709、GitOps #477/#478：正式配置、实际快照 payload 校验、恢复启动时序和公共别名声明 | 不代表上述声明已全部生效 |
| 10-21 02:25–02:38 | [Playbooks #710](https://github.com/ai-workspace-infra/playbooks/pull/710)/[#711](https://github.com/ai-workspace-infra/playbooks/pull/711)、[GitOps #479](https://github.com/ai-workspace-infra/gitops/pull/479)/[#480](https://github.com/ai-workspace-infra/gitops/pull/480) 合并：权威业务身份和 dotenv 兼容 | 需继续核实运行进程与入口 |
| 10-21 02:54 起有用户日志 | JP Agent 可同步 31 个客户端，但状态 POST 持续 403；全故障起点未确认 | 读取配置成功不能证明注册/状态成功 |
| 10-21 03:09:18 | 现有 Playbook 切换 V4 正式 Caddy 入口，语法/证书验证通过，仅重启 Caddy | 不会自动提升 DB 角色或启用后台任务 |
| 10-21 03:09:20–03:12:23 | V4 Accounts 多个 Agent 状态 POST 204；JP 同时正常配置同步 | 不代表全部节点的连接和采集通过 |
| 10-21 03:16–03:22 核验 | 固定 r4/实际 SHA、account_user 权限、schema/计数、域名分流、现存快照与历史 case 回执 | 尚不能宣布整轮全部闭环 |
| 10-21 03:27 | 用户授权补齐品牌两域到 V4，权威/公共解析、根域200、www保留URI的301均通过 | 不代表单写入者或数据迁移全部验收完成 |

## 3. 问题与修复台账

状态规则：**运行恢复**表示有现场正向证据；**已合并**仅表示代码合入；**待复验**表示当前候选缺足够证据；**待核查**表示原因/边界尚不完整。

| ID | 问题、原因与影响 | 修复／依据 | 当前状态与后续 |
| --- | --- | --- | --- |
| V4-01 | 把源“版本冻结”扩成停业务容器，在线快照与最终停写混淆 | #702 分离 MVCC 在线快照与写入权交接 | 设计已合并；本轮未检查源端单写入状态 |
| V4-02 | 目标必须来自历史 CMDB，现场身份已确认仍不能推进 | #702 支持从云控制面核实生成单次临时 inventory，校验精确目标和 SSH 身份 | 保留精确身份校验；不能伪造持久 CMDB |
| V4-03 | 全新部署与恢复配置分叉：缺版本域名、443、证书，旧 Caddy 内部 CA | #703 复用证书/入口 owner；Vault 静态证书和五个公共 SNI | 当前可信 TLS/只读挂载通过；旧历史通过不迁移到新候选 |
| V4-04 | Billing 不接受 `2026102002`，重启/502，readyz 不能代表写入健康 | [Billing #53](https://github.com/ai-workspace-services/billing-service/pull/53) 的审核 checkpoint 修复；当前 Billing 镜像见基线 | 当前 readyz=200 且 DB 时间新鲜；逐节点入库、重复投递仍待验 |
| V4-05 | 临时 PostgreSQL init server 先 socket-ready 后退出，恢复连接中断 | #704/#709 改为等待最终服务 TCP listener；保留隔离网络 | 已合并；新快照仍需对应恢复完成回执 |
| V4-06 | 只检查源脚本，实际 Ansible 渲染 payload 的转义/编译失败未拦住 | #708 编译真实 payload，先验证再访问数据库 | 已合并；每次 payload 变化重跑 |
| V4-07 | Accounts 只读身份导致 session_creation_failed；只给会话权限又掩盖注册/账务权限不足 | #705/#476 为早期候选会话折中，后被统一业务身份替代 | 当前 account_user 具备检查表权限；真实注册/MFA/会话待当前版本验收 |
| V4-08 | 为业务注入 recovery_app、generation_auth、generation_app，偏离原生权威凭据合同 | #710/#479 统一 `account_user`，密码读取 `kv/prod/databases` 的 `account_pg_password` | 运行连接已对齐；旧角色对象仍存在，依赖审计后再清理 |
| V4-09 | 误把 readonly_release 与业务身份混在一起；审计 OS/Docker 权限边界不清 | #706 专用 reader，业务与审计身份职责分开 | 权限收窄及 OS peer/受限 sudo 后续独立验收；不授予通用 Docker/root |
| V4-10 | 新配置依赖 `env_file.format=raw`，固定控制器不支持；普通 dotenv 又可能插值凭据 | #711/#480 使用现有控制器可读格式并正确保留字面量 | 当前容器已使用 account_user；不得靠轮换密码掩盖解析问题 |
| V4-11 | reconcile-usage 硬编码 V2→V3；diff 误要求停写；比较预检曾被误当完整数据一致 | #706 及 Accounts migratectl 的 source/target 参数化；完整只读比较单列回执 | 早期完整比较通过；后续 case 仍有 FAIL，当前最新源目标一致性不得补记 PASS |
| V4-12 | 重建容器丢失 `/tmp` 工具，比较失败被误认为数据问题 | 从保留主机检查点校验 SHA，再注入固定二进制重试 | 保留失败回执；迁移工具不用脏工作区重建 |
| V4-13 | 用户遗漏与单用户补同步、业务冲突/用量合并 fixture 首轮失败 | postgres_cases 最后一次六类 PASS，见回归清单 | 实库 fixture 通过不代表已对线上执行补同步 |
| V4-14 | 共享 Token 曾按代际路径取值；401/403 容易一概归因于 Token | 权威路径统一 `kv/prod/accounts/runtime`；JP 与 Vault 值仅做相等比较 | 本次故障关键原因是入口，未轮换 Token；当前全三服务相等仍需独立复验 |
| V4-15 | V4 承接公共域后仍用候选 Caddy：Accounts 所有非 GET/HEAD 403；Billing probe-only | 03:09 显式正式模式激活，401 缺 Token、真实状态 POST 204 | **运行恢复**；[Playbooks #712](https://github.com/ai-workspace-infra/playbooks/pull/712) 持久修复仍 OPEN |
| V4-16 | 文档写了入口激活标记，代码却没写；恢复重跑无条件覆盖候选规则 | #712 写模式标记并保留已激活配置，5 项测试通过 | 等审查合并和固定构件重验；线上标记已写 |
| V4-17 | 后台 writer=false、入口正式、DB可写三个状态没有一同验收 | 当前 Accounts/Billing 仍 false；与正式配置声明存在差异 | **待核查**；按服务任务语义、单写入者和配置 owner 修复，不能只看到权限就判正式完成 |
| V4-18 | 品牌域切换遗漏：服务三域与 xworktech/www 不同代际；预留 DB 别名被当普通 HTTPS | 记录精确域名矩阵；03:27 按授权将品牌两域改到 V4 | 品牌 DNS/HTTPS 已验证，见[回执](brand-dns-handoff-20261021.zh.md)；DB 隧道另验 |
| V4-19 | `subscriptions=1` 被误与历史 13 条比较，易误判丢订阅 | 查明历史统计对象 `subscription_records`，当前为 13 | 口径已确认；数据指纹仍按同表/同边界比较 |
| V4-20 | 目录命名 full-snapshot、文件存在或旧恢复成功被当最新完整恢复能力 | 最新候选四文件和 checksum 单列，缺 Vault/清单/恢复完成证据明确未完成 | **待补齐**，入口修复后的最新环境快照尚未建立 |
| V4-21 | VLESS node undefined、policy 404、MFA/退款/套餐状态机及 OAuth/Webhook 只做局部测试 | 现场截图与 #174 历史记录 | 当前版本正向会话/业务回归待验，不把 GET 登录 API 的 method_not_allowed 误当 POST 登录根因 |
| V4-22 | Sandbox 账号豁免、账本落后被接受后，可能扩展为“全数据通过” | 单列授权例外、对象与边界 | 接受历史滞后不豁免身份冲突、双写、重复记账或缺单写入证据 |

## 4. 仍需闭环的交付问题

1. **模式收敛**：GitOps 正式声明、实际 dotenv/挂载配置、容器进程环境、入口 marker、Doco-CD target 和任务开关逐项对账。当前正式入口恢复后，后台开关仍 false，不能称正式运行配置全部完成。
2. **数据收敛**：对当前源目标执行有明确边界的只读比较，区分同步范围、目标独有事实与已接受的账务滞后；身份、财务、配额冲突停，不能覆盖。
3. **完整恢复**：对最终候选生成在线一致性加密快照，完成校验清单、隔离恢复、应用连接恢复库、主机外副本和密钥可获得性证明。DB、运行配置、Vault 分别说明原子边界。
4. **业务收敛**：真实 Agent 注册/配置/连接、逐节点 Exporter→Vector→Billing、流量桶及账本增长、实际登录/MFA、OAuth/Webhook、Stripe Sandbox 全链路回执分别补齐。
5. **交付收敛**：#712 等修复审查后合并，再固定新 tag；部署/恢复路径变化要验证重跑和故障恢复。同一候选至少覆盖两个完整相关业务采集周期，不能用 Doco-CD 轮询代替 Vector 周期。

本轮不能从“文档已整理”推导这些事项已完成。回退保留旧构件和快照；当前 V4 已接收写入，DNS 回退前必须评估数据方向，不能自动破坏性降级数据库或重新开放旧代际写入。

## 5. 下一轮执行顺序

固定各仓库 main SHA/唯一 tag/digest/SQL → 读取源和目标实际状态 → Vnext 全新部署（独立于恢复演练）→ 目标可恢复保护 → 核心只读预览及受控单向合并 → 含业务数据备份与隔离恢复 → 历史问题真实 case → 同版本重跑及中断恢复 → 稳定观察和报告 → 人工确认单写入者/最终追齐/切流量 → 正式稳定验收后登记下一轮来源。

代际只是部署身份；业务角色、共享令牌和证书的权威来源不随 vN 自动生成。修复必须进入所属仓库并绑定新构件，不能依赖主机热修和旧回执拼接。
