# PROD V5：净室部署、用户同步与三轮幂等验证回执

采样更新：2026-10-24 03:09:59 +0800，Asia/Shanghai。所有执行为操作员本地调用已合并 owner 的实际操作；`local-*`、`deploy-*`、`users-*` 是真实本地 run_id，不构造 GitHub Actions 运行链接。只有 r104 发布是 [Accounts CI run 40005176848](https://github.com/ai-workspace-services/accounts/actions/runs/40005176848)。

[统一流程白皮书](https://github.com/ai-workspace-services/.github/blob/main/docs/control-plane-deployment-and-migration.zh.md) → [V4→V5 索引](../../17-prod-v4-v5-baseline-and-upgrade-retrospective.zh.md) → [V5 基线](prod-v5-runtime-and-snapshot-baseline-20261023.zh.md) → 本回执 → [故障复盘](prod-v5-deployment-postmortem-20261023.zh.md) → 下方真实回归与重验。

## 范围与结论

源为仍持续服务的 PROD V4；目标为独立 PROD V5 候选，Akamai JP Tokyo 3。源/目标 namespace、state key、lineage 和实际云资源身份均不同。只删除旧 V5 的一个计算实例；防火墙、独立存储、备份与远端 state 不删除，V4 state 在删除前后摘要一致。删除前已有完整数据库加密备份及独立恢复证明，17 个原备份/原迁移证据文件已逐文件校验并异机保留；受控原件未擅自清理。

净室创建、完整指纹核验、严格 SSH、首次真实部署、33 用户同步与迁移后独立恢复均 **PASS**。带数据的三轮完整 IaC/部署/迁移重放：**PASS（3/3）**。末次只读源复核发现窗口内上游字段增量，最终一致性仍 **BLOCKED**，见“终点上游增量”。本轮只同步批准的 `public.users`；不称为订阅、OAuth、MFA 关联表或完整财务数据迁移。V4 公共服务、公共 DNS 与写入权未改变，最终切换 **NOT_RUN，未授权**。

## 固定输入

| Owner / 构件 | 精确来源 |
| --- | --- |
| IaC 资源与 CMDB owner | `9a5ff9a139509ca18759191370d9788df49b221c`；删除前版本为 `339dbe28c88ccc8699c87ea299ffa88e6f0d7ddd`，早期失败版本单列保留 |
| GitOps 当前 main 固定声明 | `615beaab59330fec1b595fa462138d4f05ebbe9b`，[#516](https://github.com/ai-workspace-infra/gitops/pull/516)、[#517](https://github.com/ai-workspace-infra/gitops/pull/517) |
| Playbooks main 固定角色 | `ff984bce9ebddef3e93f1dde7a98b1987245b143`；基础 OS、Docker、配置、备份恢复及服务管理由此 owner 执行 |
| 安装入口 | services `.github` `d35ce6f5457e3d2ecebbc0b3fdbfa1cb410e074e` |
| 部署构件 | `daily-build-2026.10.23-r101` 的五个固定 registry digest；运行时 `Config.Image` 与 GitOps 的五项 digest 逐项匹配，不用 image config ID 替代 registry 引用 |
| 预构建 migratectl | [daily-build-2026.10.24-r104](https://github.com/ai-workspace-services/accounts/releases/tag/daily-build-2026.10.24-r104)；commit `74442911247866edfa43217a51ff8a59a7ed1dcb`；Linux amd64 SHA-256 `f3079133e58cda41faa7d9f7a11195e456422dbb5efc75239b35c93b4a50ab03` |
| 发布核验 | GitHub asset digest、字节数、release manifest、SHA256SUMS 和 annotated tag 对应 commit 均核对；目标未本地构建 |
| Accounts schema | `f45db2423f11d9dcc7f3cc58c72b52228a27d7b6ccfc717faf2bbb56fa0498b1` |
| Billing schema | `7faf46295b419102e4bbcb8cef67db14ba3beef1d46ee945fd4acfb86541c39b` |
| checkpoint / DDL | `2026102002 / dirty=false`；本轮 users-only 无 DDL，迁移 SQL checksum 记 N/A，未强制版本 |

IaC 的目标与源声明、资源模式和 state namespace 来自 GitOps；这里不再复制实际账号、主机地址、完整资源标识、秘密引用或受控存储位置。真实身份、数据库 system identifier、计划摘要、配置/数据校验摘要与云端证明通过下方证据编号在受控索引内绑定。

## 每轮真实执行

| run_id | Asia/Shanghai 起止（含时区） | 阶段 / exit code | 结果 |
| --- | --- | --- | --- |
| `local-apply-20261024T022230+0800` | 2026-10-24T02:22:32.598817+08:00 → 2026-10-24T02:24:20.477343+08:00 | apply / 1 | FAIL，保留原失败；见下方根因 |
| `local-apply-20261024T022609+0800` | 2026-10-24T02:26:11.869499+08:00 → 2026-10-24T02:26:42.498642+08:00 | apply / 0 | PASS，受 owner 回执验证 |
| `local-apply-20261024T024909+0800` | 2026-10-24T02:49:11.321964+08:00 → 2026-10-24T02:49:41.291574+08:00 | apply / 0 | PASS，受 owner 回执验证 |
| `local-apply-20261024T025450+0800` | 2026-10-24T02:54:52.464406+08:00 → 2026-10-24T02:55:20.785686+08:00 | apply / 0 | PASS，受 owner 回执验证 |
| `local-apply-20261024T030034+0800` | 2026-10-24T03:00:35.821001+08:00 → 2026-10-24T03:01:05.024811+08:00 | apply / 0 | PASS，受 owner 回执验证 |
| `local-destroy-20261024T021655+0800` | 2026-10-24T02:16:57.583448+08:00 → 2026-10-24T02:17:30.191982+08:00 | destroy / 1 | FAIL，保留原失败；见下方根因 |
| `local-destroy-20261024T022006+0800` | 2026-10-24T02:20:08.459275+08:00 → 2026-10-24T02:22:15.865271+08:00 | destroy / 0 | PASS，受 owner 回执验证 |
| `final-resource-witness-20261024T030218` | 2026-10-24T03:02:18.456267+08:00 → 2026-10-24T03:02:35.986985+08:00 | 全部资源操作后的只读复核 / 0 | PASS，源 state/防火墙/lineage 保留，新 CMDB 身份及默认删除保护通过 |
| `deploy-20261024T022652+0800` | 2026-10-24T02:26:52.690130+08:00 → 2026-10-24T02:34:42.744710+08:00 | deployment / 0 | PASS，候选运行就绪 |
| `deploy-20261024T023522+0800` | 2026-10-24T02:35:23.054290+08:00 → 2026-10-24T02:39:53.497687+08:00 | deployment / 0 | PASS，候选运行就绪 |
| `deploy-20261024T024941+0800` | 2026-10-24T02:49:41.998019+08:00 → 2026-10-24T02:54:03.147719+08:00 | deployment / 0 | PASS，候选运行就绪 |
| `deploy-20261024T025520+0800` | 2026-10-24T02:55:21.370503+08:00 → 2026-10-24T02:59:44.654237+08:00 | deployment / 0 | PASS，候选运行就绪 |
| `deploy-20261024T030105+0800` | 2026-10-24T03:01:05.567436+08:00 → 2026-10-24T03:06:22.754282+08:00 | deployment / 0 | PASS，候选运行就绪 |
| `data-bearing-round-1-20261024T024909+0800` | 2026-10-24T02:49:09.525026+08:00 → 2026-10-24T02:54:50.706208+08:00 | 完整带数据重放 / 0 | PASS |
| `data-bearing-round-2-20261024T025450+0800` | 2026-10-24T02:54:50.706804+08:00 → 2026-10-24T03:00:33.945969+08:00 | 完整带数据重放 / 0 | PASS |
| `data-bearing-round-3-20261024T030033+0800` | 2026-10-24T03:00:33.946725+08:00 → 2026-10-24T03:07:10.424431+08:00 | 完整带数据重放 / 0 | PASS |
| NOT_RECORDED（终点只读鲜度探针 ID） | 2026-10-24T03:07:39.681370+08:00 → 2026-10-24T03:07:43.281156+08:00 | SQL 读取 exit 0；一致性比较 exit 1 | DIFF，源快照已出现上游增量；不计入三轮固定输入结果 |

首次用户同步：`users-initial-20261024T024737+0800`，2026-10-24T02:47:39.558988+08:00 → 2026-10-24T02:47:59.944830+08:00，exit 0。预览和应用绑定同一精确计划摘要；计划在受控原件内保留，不公开用户或连接数据。

三轮每轮顺序为 **IaC 保存计划/应用与 0 变更收敛 → 固定入口真实部署 → 运行状态比较 → 新预览/精确计划应用/只读复核 → 再次比较**。首次迁移后的基线包含 33 users。每轮要求同一数据库身份、schema/checkpoint、76 张业务表内容，以及 13 个主机配置文件和 255 个静态文件不变。常驻容器 ID、镜像、启动时间与 restart count 不变；用户 tuple 版本也必须不变，以排除无内容变化但实际 UPDATE 的假 no-op。声明的一次性资源任务只排除其预期启动时间，仍要求同一身份/镜像、成功退出和完整资源内容一致。各轮新生成的 no-op 计划摘要也必须相同。

空库先验部署重放单列：部署 exit 0，规范化后的全部状态相同；它不替代迁移后的三轮。采集器升级一次性任务比较口径时，运行中的比较器仍持有旧基线，产生一次“containers 不同”的采集判断；原判断和原始基线保留。按明确的声明口径重新比较，同一份实测样本无差异，不归因为业务部署失败。

<a id="additional-replay-20261024"></a>

## 追加一轮真实重放（2026-10-24 08:56–09:02）

原三轮回执保持不变。本追加轮沿用相同固定输入和不可变源快照，不重新删除主机、不读取最新 V4 作为同步输入，V4、公共 DNS 与写入权不变。

| run_id | Asia/Shanghai 起止（含时区） | 阶段 / exit code | 结果 |
| --- | --- | --- | --- |
| `local-apply-20261024T085631+0800` | 2026-10-24T08:56:33.232775+08:00 → 2026-10-24T08:57:06.515200+08:00 | iac / 0 | PASS |
| `deploy-20261024T085706+0800` | 2026-10-24T08:57:07.103739+08:00 → 2026-10-24T09:02:02.646905+08:00 | deployment / 0 | PASS |
| `users-repeat3-20261024T090214+0800` | 2026-10-24T09:02:15.825859+08:00 → 2026-10-24T09:02:37.308759+08:00 | migration / 0 | PASS |
| `extra-data-bearing-round-3-20261024T085631+0800` | 2026-10-24T08:56:31.266899+08:00 → 2026-10-24T09:02:49.149597+08:00 | 完整带数据重放 / 0 | PASS |

IaC 0 create/update/delete，完整部署 8 项就绪探测通过。users-only 目标仍为 33 users，76 表内容、13 个文件、255 个静态文件、数据库身份/checkpoint 和常驻容器状态均无差异，用户 tuple 版本不变。新生成的 no-op 计划 SHA-256 为 `ec18936d0d1df6608b4685780b31107a7f6dc96d09686228d4718698c5558a9c`，与原三轮一致。证据仍归 E02/E04/E05，在受控原件中保留本轮日志与比较结果。

用户明确接受 V5 生成目标内部 UUID，不将其作为迁移阻断项；其余字段比较继续执行。这不等于接受或消除了源端 `proxy_uuid` 等业务字段的后续增量。此轮没有重做备份恢复或真实凭据登录，也没有重新验证最新 V4 的一致性；沿用先前已通过的恢复证据，最终追齐及切换门禁保持未完成。

## 故障 → 修复 → 真实回归

| Case | 原失败 / 防护 | 修复 owner 与真实测试 | 本轮重验 |
| --- | --- | --- | --- |
| 候选精确删除与源隔离 | 通用生产 destroy 仍拒绝；不提供 provider-delete 或 state-rm 绕过 | [IaC #463](https://github.com/ai-workspace-infra/iac_modules/pull/463)，[真实失败用例](https://github.com/ai-workspace-infra/iac_modules/blob/9a5ff9a139509ca18759191370d9788df49b221c/scripts/pipeline/tests/test_validation_cleanup.py) | 只删除 1 实例；保留资源、源 state 与收敛门禁通过 |
| 源 state 校验集合顺序 | 首次删除前误报源 state 改变，exit 1；没有删除实例。三次实际读取 serial、资源与状态值相同，仅 `check_results` 顺序不同 | [IaC #465](https://github.com/ai-workspace-infra/iac_modules/pull/465)，同一测试文件中的 state witness 回归；只归一化两个无序集合 | 新保存计划删除与前后源 state 比较 PASS |
| 完整云侧 SSH 身份 | 旧屏幕不能作为新机完整指纹证明；不接受前缀或跳过 StrictHostKeyChecking | [IaC #464](https://github.com/ai-workspace-infra/iac_modules/pull/464)，[hostkey proof tests](https://github.com/ai-workspace-infra/iac_modules/blob/9a5ff9a139509ca18759191370d9788df49b221c/scripts/pipeline/tests/test_cloud_hostkey_proof.py) | TLS 云控制台完整 256 位指纹与网络公钥一致；指定操作员密钥严格 SSH PASS |
| IPv6 主机地址发布 | 实例实际创建成功，随后 CMDB sanitizer 拒绝 `/128`，owner exit 1；不误写为创建失败或部署成功 | [IaC #466](https://github.com/ai-workspace-infra/iac_modules/pull/466)，[single-host CIDR test](https://github.com/ai-workspace-infra/iac_modules/blob/9a5ff9a139509ca18759191370d9788df49b221c/scripts/pipeline/tests/test_unified_iac.py) | 归一化后 owner apply 0 create/update/delete，正式 CMDB 发布 PASS |
| users-only 在线同步 | r103 要求已暂停写进程，不能用无真实依据的声明跳过；本轮未使用本地未发布补丁 | [Accounts #271](https://github.com/ai-workspace-services/accounts/pull/271)，[PostgreSQL 17 并发提交/旧计划拒绝 case](https://github.com/ai-workspace-services/accounts/blob/74442911247866edfa43217a51ff8a59a7ed1dcb/internal/migrate/full_business_postgres_test.go) | r104 预构建首次同步 PASS；服务未停止，锁前读保护与锁内复核来自该发布版本；真实三轮按上表计数 |
| 新环境错误只读入口 | 历史 `candidate_mode` 与拒绝 POST 绑定已删除，源迁移只读保护保留 | [Playbooks #742](https://github.com/ai-workspace-infra/playbooks/pull/742)，[当前 Caddy 模板](https://github.com/ai-workspace-infra/playbooks/blob/ff984bce9ebddef3e93f1dde7a98b1987245b143/roles/vhosts/web_saas_host_config/templates/Caddyfile.j2) | 不存在的合成身份 POST 返回业务 `user_not_found`，MFA status 200；未复现 403/405/503。不是用真实密码登录的验收 |

## 数据、恢复与验收边界

迁移前以只读角色采集并加密 V4 users 快照；隔离恢复后，应用前再次核对当前 V4 的 33 users **全部字段，包括原 UUID** 与快照一致。users-only 在 V5 生成目标内部 UUID，其他用户字段复核一致；其余业务表内容不变。源快照及原始数据库材料只在受控存储保留；不提交密码/MFA 数据或用户标识。

新目标在迁移前（0 users）和迁移后（33 users）分别运行固定 Playbooks 的完整数据库备份与独立恢复；加密归档均校验后异机保留。恢复结果包含 schema、数据、sequence 与权限核验；这些只覆盖本轮 V5 实际状态，不冒充 V4 完整账务/订阅迁移或 G3 全业务验收。

Accounts、Billing、Content、Console 的 readiness，以及可信 HTTPS/SNI 共 8 项通过。合成登录路由回归通过；真实凭据登录、OAuth callback、支付 webhook、Agent/VLESS、真实采集/计费周期仍 **NOT_RUN / BLOCKED**。Collector 配置存在但本轮未作为运行服务验收。公共 DNS 未改，不能把 direct-candidate HTTPS 成功当成公网 DNS 已交接。所有用户数据的最终增量追齐、写入归属转移与切换均需另行明确确认。

## 终点上游增量与未完成门禁

三轮结束后的只读鲜度复核发现：V4 仍为 33 users，但相对已核验的固定快照，`proxy_uuid`、`version`、`updated_at`、`proxy_uuid_expires_at` 的字段摘要发生变化。源 SQL 读取成功，一致性比较 exit 1；未公开任何具体值或用户标识。迁移应用前全部字段一致的结论只属于当时的采样边界，不能延伸为终点的实时一致性。本轮没有停止 V4 或取得其写入权，不能推断具体业务触发原因，也不追逐移动源而覆盖已验证的目标基线。

**固定快照输入的三轮幂等 PASS，与当前上游最终追齐 BLOCKED 同时成立。** 最终一致性、Proxy UUID/有效期与身份版本语义、真实登录及完整业务验收须在切换前另行核对；最终追齐和源写入隔离需独立明确授权。公共 DNS 仍未切换。该差异保留为真实末次回执，不把它覆盖为成功，也不把它误记为同输入重放产生的数据漂移。

## 脱敏证据索引

| 编号 | 受控原件范围 | 公开保留内容 |
| --- | --- | --- |
| E01 | 删除前源/候选 raw state、云 API 身份、异机备份与原证据保留清单 | 隔离/完整性/可恢复性通过与数量；不提交 state、备份或地址 |
| E02 | 每次 owner contract、保存计划摘要、receipt、私有执行日志 | run_id、固定 SHA、阶段、退出码、create/update/delete 与防护结果 |
| E03 | TLS 云控制台输出、完整主机公钥校验、严格 SSH 与 CMDB | 完整 256 位校验通过；秘密、会话令牌和真实主机标识留在原件 |
| E04 | 每次安装日志、13 文件元数据、镜像/容器状态、76 表内容摘要、数据库身份 | 相等性、范围和固定发布来源，不公开秘密派生文件摘要或用户内容 |
| E05 | V4 只读字段核对、加密快照、隔离恢复、每次预览/应用/复核计划与用户 tuple 摘要 | 33 users、字段一致性、no-op 与源只读；密码/MFA、DSN 与个人信息不公开 |
| E06 | 迁移前/后完整备份、恢复与异机校验 | 对应用户数、schema/checkpoint 与恢复 PASS；原件继续受控保留 |
| E07 | 合成身份的可信 direct HTTPS 请求与响应 | `user_not_found` / MFA 200、非 403/405/503，不含真实用户状态 |

历史 01:07 的 r5/r103 成功与早期 Docker/exit 4 失败均在原[运行基线](prod-v5-runtime-and-snapshot-baseline-20261023.zh.md)保留。Knowledge [#196](https://github.com/ai-workspace-services/knowledge/pull/196) 仍是较早 Docker/collection 漂移样本的待审 PR；本轮不重复提交该样本，不以其“旧 apply 运行中”替代新回执，也不擅自关闭。服务级配置路径继续由运行基线汇总，本文件仅记录本轮实际执行。
