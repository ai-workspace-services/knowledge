# PROD V5 运行基线与快照清单

核验时间：2026-10-24，Asia/Shanghai。本文是有时间边界的运行回执，配置权威仍归 GitOps、Playbooks、IaC 与控制入口各自 owner。公开版本仅保留逻辑代际、公开代码引用和脱敏摘要；主机标识、地址、秘密存储路径、私有备份位置及原始证据留在受控位置。

[统一部署与迁移流程](https://github.com/ai-workspace-services/.github/blob/main/docs/control-plane-deployment-and-migration.zh.md) · [V4→V5 基线与升级复盘](../../17-prod-v4-v5-baseline-and-upgrade-retrospective.zh.md) · [V5 部署流程复盘](prod-v5-deployment-postmortem-20261023.zh.md)

<!-- BEGIN CLEANROOM 20261024 -->
## 当前净室验证周期（更新至 2026-10-24 09:02:49 +08）

本节及[本轮完整回执](prod-v5-cleanroom-deployment-migration-validation-20261024.zh.md)取代下方 01:07 样本作为新周期事实；原 r5/r103、Docker 未安装、旧 apply 运行中及各次失败仍按采样背景保留。

| 阶段 | 当前证据 | 状态 |
| --- | --- | --- |
| 安全替换 | 源/目标真实 state 和云资源隔离；删除前可恢复备份及原证据异机保留；只删除 1 个 V5 计算实例，保留防火墙与源 state；新机严格 SSH 通过 | PASS |
| 净室资源与首次部署 | 固定 main：IaC `9a5ff9a139509ca18759191370d9788df49b221c`、GitOps `615beaab59330fec1b595fa462138d4f05ebbe9b`、Playbooks `ff984bce9ebddef3e93f1dde7a98b1987245b143`、installer `d35ce6f5457e3d2ecebbc0b3fdbfa1cb410e074e`；8 项运行与 HTTPS/SNI 探测通过 | PASS |
| 用户同步 | 预构建 r104，精确 commit/二进制/schema/计划摘要见本轮回执；迁移应用前 V4 的 33 users 与只读快照全部字段一致；目标 0→33，目标内部 UUID 依目标语义重新生成（用户已明确接受，不作为阻断项），其他字段一致；其余业务表不变，服务未停止 | PASS（users-only） |
| 备份恢复 | 新目标 0 users 迁移前及 33 users 迁移后，完整数据库加密备份、独立恢复与异机校验均通过 | PASS（本轮目标实际数据范围） |
| 带数据完整重放 | 每轮 IaC 0 变更、真实部署、fresh preview/精确计划 apply/只读复核；13 配置文件、255 静态文件、76 业务表、数据库/checkpoint 与常驻容器状态比较；用户 tuple 版本不得变化 | PASS（原三轮 3/3；追加一轮亦通过） |
| 登录路由回归 | 合成不存在身份 POST 为业务 `user_not_found`，MFA status 200，非 403/405/503 | PASS（不代表真实凭据登录） |
| 终点上游鲜度 | V4 仍为 33 users，但 Proxy UUID、版本与有效期等字段摘要相对固定快照出现增量；只读比较 exit 1，最终追齐尚未执行 | BLOCKED（切换前门禁；不否定同输入三轮幂等） |
| 全业务及切换 | OAuth/MFA 关联表、完整账务/订阅、Agent/VLESS 与真实支付/采集周期未纳入 users-only；公共 DNS 和 V4 写入权不变 | NOT_RUN / BLOCKED；切换未授权 |

每轮起止、run_id、退出码、故障、修复 PR、真实回归 case 与受控证据索引均在[完整回执](prod-v5-cleanroom-deployment-migration-validation-20261024.zh.md)。配置路径沿用下方服务汇总：本周期角色精确 ref 为 `ff984bce9ebddef3e93f1dde7a98b1987245b143`、声明 ref 为 `615beaab59330fec1b595fa462138d4f05ebbe9b`；下方固定到 r5 的旧源码链接保留其历史版本含义。

### 追加一轮真实重放（08:56–09:02 +08）

2026-10-24T08:56:31.266899+08:00 → 2026-10-24T09:02:49.149597+08:00，`extra-data-bearing-round-3-20261024T085631+0800`，完整执行 exit 0 / PASS。沿用上述固定版本和已核验的不可变 V4 快照；不是重新采集当前 V4，也没有再次删除主机。IaC 0 create/update/delete；完整部署 8 项运行就绪探测通过；migratectl r104 users-only 新预览、精确计划 apply 与复核均成功，目标仍为 33 users。76 张业务表、13 个文件、255 个静态文件、数据库/checkpoint 和常驻容器状态均与迁移后基线相同，用户 tuple 版本不变。详细阶段回执见[完整回执的追加轮](prod-v5-cleanroom-deployment-migration-validation-20261024.zh.md#additional-replay-20261024)。

目标内部 UUID 的重新生成已被接受；它与源端 `proxy_uuid`、版本及有效期的后续业务增量不同。此次重放不消除 03:07 源鲜度比较发现的差异，也未重新验证实时源一致性。真实凭据业务验收与最终追齐、切换仍保持原有未完成状态。

### 当前服务配置入口（本净室周期固定版本）

本表列出本周期实际使用的配置来源与路径约定，供当前运维查阅。下方 r5 服务表和第 1–7 节均为历史样本，不是当前清单。文件内容、凭据及其派生摘要不公开。

| 范围 / 服务 | 当前固定配置来源 | 目标运行路径 / 本轮状态 |
| --- | --- | --- |
| IaC / CMDB | IaC `9a5ff9a139509ca18759191370d9788df49b221c`；资源身份以受控 CMDB 为准 | JP Tokyo 3 独立候选；本追加轮 0 变更 |
| Doco-CD / 全部业务容器 | [GitOps Compose](https://github.com/ai-workspace-infra/gitops/blob/615beaab59330fec1b595fa462138d4f05ebbe9b/compose/web-saas/docker-compose.yml)及[候选覆盖](https://github.com/ai-workspace-infra/gitops/blob/615beaab59330fec1b595fa462138d4f05ebbe9b/compose/web-saas/docker-compose.prod-v5-candidate.yml) | `/opt/doco-cd/docker-compose.yml`；五项业务镜像实际引用与固定 digest 一致 |
| PostgreSQL | Playbooks `ff984bce9ebddef3e93f1dde7a98b1987245b143` 的 `roles/vhosts/web_saas_host_config/templates/postgresql.conf.j2` | `/etc/xcontrol/web-saas/config/postgresql.conf`；checkpoint `2026102002 / dirty=false` |
| Accounts | 同一固定 role 的 `account.yaml.j2` | `/etc/xcontrol/web-saas/config/account.yaml`；readiness PASS，真实凭据登录 NOT_RUN |
| stunnel server / client | 同一固定 role 的 `stunnel-server.conf.j2`、`stunnel-client.conf.j2` | `/etc/xcontrol/web-saas/config/stunnel-server.conf`、`stunnel-client.conf`；数据库隧道就绪 |
| Caddy | [当前固定模板](https://github.com/ai-workspace-infra/playbooks/blob/ff984bce9ebddef3e93f1dde7a98b1987245b143/roles/vhosts/web_saas_host_config/templates/Caddyfile.j2) | `/etc/xcontrol/web-saas/Caddyfile`；可信 HTTPS/SNI PASS，公共 DNS 未切换 |
| Billing / Content | 上述固定 Compose 和受管运行时配置 | readiness PASS；Content 服务合同探测 PASS；真实账务/采集周期 NOT_RUN |
| Console | 上述固定 Compose 的静态资源任务与 Caddy | 255 个静态文件内容不变；一次性任务正常退出，不计作常驻服务 |
| OpenTelemetry Collector | 同一固定 role 的 `otel-collector.yaml.j2` | `/etc/xcontrol/web-saas/config/otel-collector.yaml` 存在；未作为运行服务验收 |

13 个文件比较对象包含一份历史 Compose 备份文件，并非 13 项生效配置。实际盘点为 9 个运行容器及 1 个成功退出的一次性资源任务；不表述为“10 个运行容器”。

<!-- END CLEANROOM 20261024 -->

## 历史候选状态（2026-10-24 01:07 +08 采样）

源为持续服务的 V4；目标为独立 V5 候选。V4 公共服务、公共 DNS 与写入权保持不变。V5 仍未承接流量；本节只记录当时已完成的部署、users-only 数据追加和恢复演练。随后获明确授权的 V5 主机 clean-room 重建与三次重复验证属于下一轮，本记录不预写其结果。

| 阶段 | 回执 | 状态 |
| --- | --- | --- |
| 固定部署候选 | GitOps #515 / `bf5fab96ee7b7b54066727bb6a03d53c337de36e`；Playbooks #742 / `86c6a3c39c30df079e047eb77194ea670514a6c2`；installer #42 / `2042cfe1e6d6ac66985c4f3e4a44eea15ae7d014`；V5 release `v2026.10.23-v5-r5` | PASS |
| r5 首次部署 | `run-normal-ingress-20261023T1554Z`；2026-10-23 23:55:09–2026-10-24 00:01:09；exit 0；8 项组件、数据库与可信 HTTPS 检查通过；日志 SHA-256 `cdef35d2992f1febfb21b14cacbc4d5f2aab00ddeb01964fc21f3552507c38c5` | PASS |
| r5 同输入重跑 | `run-idempotence-r5-20261023T1602Z`；2026-10-24 00:02:03–00:08:05；exit 0；8 项检查通过；被采样容器 ID、启动时间、重启计数、配置摘要及数据库身份无变化；日志 SHA-256 `08a2314271e07b490bf63376b82557b79b2b350f87f8ac6f95b7e706797e809d` | PASS（一次重复；不满足后续“三次”验收） |
| 数据源快照 | V4 在线用户字段快照与迁移前复核均为 33 条，字段摘要相符；加密快照 SHA-256 `5f999cbd16900a1d003193bf567de272746e4dcdaba15979b64c4969b5bad7ca` | PASS |
| 迁移前目标回滚点 | 空目标完整数据库加密备份与独立恢复通过；归档 SHA-256 `0ea137137a1c7011c4393b71207754ce95b0bfb3cbffc145ac7eb88c9c40ea93` | PASS（仅为空目标恢复证明） |
| r103 users-only 迁移 | 2026-10-24 01:04:47–01:05:06；预构建 `daily-build-2026.10.24-r103`，Accounts commit `fd5aa7dff95bfd324349a303b790738c11487be3`，Linux amd64 SHA-256 `934955967ecb25ed2d41c2a5d5010f9037423faa8c96d4bf18c1fbb7c8f95735`；SSH 执行，exit 0；目标 users 0→33；未停止 V5 服务；源保持只读 | PASS |
| 数据对账 | 全部用户字段摘要一致（目标内部 UUID 按目标语义生成）；其余抽查业务表行数及内容摘要不变；schema checkpoint `2026102002 / dirty=false`；本轮无 DDL，SQL checksum 不适用。`migratectl` 实际 run_id 与 plan SHA-256 未出现在可公开回执中，标记 `NOT_RECORDED`，不推测补造 | PASS（审查过的精确计划执行；字段级重验通过） |
| 迁移后恢复 | 2026-10-24 01:06:01–01:07:12；Playbooks commit `86c6a3c39c30df079e047eb77194ea670514a6c2`；exit 0；加密归档 SHA-256 `ad881ff8881215c8b3b6309a9b833b449bd8df5acf79be34e5ee40eba46ec884`；独立恢复 33 users，schema/data/sequence 检查通过 | PASS（仅 users-only 状态） |
| 登录与业务验收 | Accounts/Billing readiness、Content health/docs、Console HTTP 与可信 HTTPS 8 项探测通过；真实凭据登录、OAuth、支付、Agent、订阅和完整账务链未验收 | NOT_RUN / BLOCKED（不推导为业务验收） |
| 切换 | V4 公共流量、DNS 和写入权保持原状 | NOT_RUN（未授权切换） |
| 新 clean-room 周期 | V5 主机删除/重建；部署与迁移各自三次无差异重复 | NOT_RUN（本回执采样时未执行） |

### 本轮历史部署故障及修复链

| 执行 | Asia/Shanghai 时间 / run_id | 固定版本与结果 | 根因、修复及重验 |
| --- | --- | --- | --- |
| r3 控制面修复 | 2026-10-23 23:21:06–23:28:43；`run-runtime-repair-20261023T1517Z` | GitOps `fdd6dd743acb13f3e7a9150f9c3cbecb58c2cab0`；Playbooks `f9cd01538e5dba4674f8d3b41d09579e0e092f2d`；exit 2 | 修复 stunnel 私钥读取权限、Caddy matcher 去重、Accounts 数据库连接身份摘要；随后发现证书链缺根导致连接失败。脱敏日志 SHA-256 `a2eac5e280e3ee26e8445c3364c9f09be5fe0909822cbaf55c618cd730478cf3`。修复 PR：[Playbooks #740](https://github.com/ai-workspace-infra/playbooks/pull/740)、[GitOps #513](https://github.com/ai-workspace-infra/gitops/pull/513)。 |
| r4 信任链修复 | 2026-10-23 23:35:18–23:44:44；`run-trust-repair-20261023T1532Z` | GitOps `8c70106f0a51a9cdfa2f9a7626e946422f3ab06e`；Playbooks `a898ffc7b304512f2e012a58e0f8ee52089765c4`；exit 2 | 证书链根因修复并验证正确主机名；旧客户端仍缓存 CA 上下文，Content 探针请求头也与应用合同不符。根因和修复 PR：[Playbooks #741](https://github.com/ai-workspace-infra/playbooks/pull/741)、[GitOps #514](https://github.com/ai-workspace-infra/gitops/pull/514)。后续未把探针误判成应用通过。 |
| r5 正常入口 | 2026-10-23 23:55:09–2026-10-24 00:01:09；`run-normal-ingress-20261023T1554Z` | GitOps #515 与 Playbooks #742 固定 ref；exit 0 | 删除将全新目标误设为只读的部署逻辑；迁移源只读保护保留。8 项探测通过。 |
| r5 幂等重跑 | 2026-10-24 00:02:03–00:08:05；`run-idempotence-r5-20261023T1602Z` | 同一固定输入；exit 0 | 服务、数据库、配置与容器身份无差异；此历史结果仅覆盖一次重复。 |

r3/r4 的实际部署 exit 2 保留为失败事实，不被后续 r5 成功覆盖。对应的 Ansible collection 解析缺依赖在本轮 r5 前置检查中通过固定 installer/common 依赖修复；此项不替代 clean-room 后续三次重复验收。

## 按服务查配置路径与部署边界

以下是可公开复用的仓库内声明与模板路径，以及通用运行路径约定。真实目标名、域名、主机地址、凭据值、Vault 路径和具体备份目录不写入公开记录。

| 服务 | GitOps 声明 / 仓库路径 | 主机配置与容器挂载约定 | 秘密边界与核验 |
| --- | --- | --- | --- |
| Doco-CD | [GitOps Compose](https://github.com/ai-workspace-infra/gitops/blob/bf5fab96ee7b7b54066727bb6a03d53c337de36e/compose/web-saas/docker-compose.yml)；Playbooks role `roles/doco_cd_release_selection` | 控制面配置由固定 Playbooks 选择固定 GitOps SHA 与候选；Docker socket/本地状态属于受控运行时 | registry 登录引用仅运行时读取；r5 选择 ref 核对通过 |
| PostgreSQL | [V5 candidate Compose](https://github.com/ai-workspace-infra/gitops/blob/bf5fab96ee7b7b54066727bb6a03d53c337de36e/compose/web-saas/docker-compose.prod-v5-candidate.yml) | Playbooks `roles/vhosts/web_saas_host_config/templates/postgresql.conf.j2`；数据挂载使用 `${DATA_ROOT}/postgresql:/var/lib/postgresql/data`；配置只读挂载 | DB 密码由 secret env 注入；不公开 DSN/值；checkpoint `2026102002/false` |
| stunnel server | 同一候选 Compose | `roles/vhosts/web_saas_host_config/templates/stunnel-server.conf.j2`；私钥由受管角色设置 owner/group/mode，容器只读挂载 | 私钥和 CA 内容不归档；r5 DB tunnel/readiness 通过 |
| stunnel client | 同一候选 Compose | `roles/vhosts/web_saas_host_config/templates/stunnel-client.conf.j2`；应用网络内部监听，证书校验启用 | 不开宿主公网端口；r5 Accounts/Billing 数据库就绪通过 |
| Accounts | 同一候选 Compose；[模板](https://github.com/ai-workspace-infra/playbooks/blob/86c6a3c39c30df079e047eb77194ea670514a6c2/roles/vhosts/web_saas_host_config/templates/account.yaml.j2) | `account.yaml` 由 Playbooks 渲染为只读配置挂载；数据库通过 stunnel | 认证/DB 密钥仅运行时注入；readiness 与数据身份摘要通过；登录仍 NOT_RUN |
| Billing | 同一候选 Compose；非敏感业务项来自 GitOps candidate env | 无独立 YAML；DB 连接通过 stunnel；运行时 env 由 Compose 绑定 | DB/服务 Token 不进入 Git；readiness 通过，真实支付/流量链 NOT_RUN |
| Console | 同一候选 Compose | 静态资源卷只读挂载；由 Caddy 反向代理 | OAuth/认证密钥仅运行时注入；Console HTTP/HTTPS 探针通过，用户登录 NOT_RUN |
| Content | 同一候选 Compose；[探针头合同修复](https://github.com/ai-workspace-infra/playbooks/pull/742) | 内部 API；无外部宿主端口；health/docs 检查走实际服务合同 | `X-Service-Token` 值仅运行时注入；health/docs 探测通过 |
| Caddy | 同一候选 Compose；[模板](https://github.com/ai-workspace-infra/playbooks/blob/86c6a3c39c30df079e047eb77194ea670514a6c2/roles/vhosts/web_saas_host_config/templates/Caddyfile.j2) | Caddyfile 与 TLS 文件由 Playbooks 生成只读挂载；仅边缘入口暴露 HTTP(S) | DNS API Token 只供 Caddy 运行时读取；r5 HTTPS/SNI 探测通过；公共 DNS 未改变 |
| OpenTelemetry Collector | Compose/role 模板中声明；`roles/vhosts/web_saas_host_config/templates/otel-collector.yaml.j2` | 模板存在 | 本轮运行容器盘点未发现该服务，明确标记未运行，不纳入探测 PASS |

### 历史 V5 clean-room 重复验证计划（01:07 采样）

依据[统一流程八阶段](https://github.com/ai-workspace-services/.github/blob/main/docs/control-plane-deployment-and-migration.zh.md)执行。获授权的目标替换尚未在本回执采样时执行，因此以下均为 **NOT_RUN**：

| Gate | 必须采集的证据 | 通过条件 | 当前 |
| --- | --- | --- | --- |
| 固定候选 | GitOps/Playbooks/installer commit、应用镜像 digest、预构建迁移工具 tag/SHA、schema/checksum | 所有 ref 固定、摘要匹配，无敏感值 | NOT_RUN（本轮新候选） |
| 全新部署 + 首次结果 | IaC plan/run、部署 run_id、Asia/Shanghai 起止、exit code、容器/配置/数据库身份摘要 | V5 目标新建成功，V4/DNS 不变 | NOT_RUN |
| 部署重跑 1–3 | 相同输入、每轮 run_id、配置/容器/数据摘要 | 每次 exit 0 且无差异、无不必要重启 | NOT_RUN |
| V4→V5 users-only 首次同步 | V4 只读快照 ID 摘要、V5 初始基线、migratectl tag/digest、预览计划 SHA、schema/字段校验摘要 | 仅追加批准范围，冲突停止；源字段核对通过 | NOT_RUN（新 clean-room 周期） |
| 迁移重放 1–3 | 每轮预览/应用 run_id、计划 SHA、目标行数/字段摘要、schema checkpoint | 同内容重放为空操作，目标无差异；V4 不写入 | NOT_RUN |
| 恢复与业务验收 | 加密备份摘要、独立恢复、真实登录与外部依赖 case | 用户数据恢复通过；业务 case 单独通过 | NOT_RUN |
| 切换 | 人工授权与 DNS 变更回执 | 需单独明确确认 | NOT_RUN；禁止推导授权 |

实际 `migratectl` run_id 与精确 plan SHA 未出现在历史可公开回执中，已标记未记录；新 clean-room 执行必须在受控回执中采集并只公开脱敏标识。不得停止 V4、改变公共 DNS、改变 V4 写入归属或删除现有备份/state/持久数据。

## 历史样本：Singapore r101 预检与早期部署阻断

接管前历史状态（已被本轮替换）：旧目标 `104.64.208.209` 仅 22 端口监听，Docker 未安装，
owner journal 已存在；exit 4 后已实证控制端动态角色解析缺少 `ansible.posix`。安装 `ansible.posix 2.1.0`
后同一最小 syntax-check 从 exit 4 转为 exit 0；旧公共入口 apply `60471` 已在本轮接管前停止，未取得部署成功或 ready 回执。该次不能沿用早期“主机写入前”的阶段结论，
也不能凭 journal 存在推断安装完成。四个版本 A 记录已更新，TTL 60、DNS only；公共 DNS 未改。
PG r101 已发布并通过隔离 smoke；目标 V5 的服务健康、运行镜像匹配与业务验收仍未通过。

本次文档基于最新 main `2dbd9d62869af1096d3f89e30800c2aa92450fde`，即已合并的
[#193](https://github.com/ai-workspace-services/knowledge/pull/193)。后续旧表保留各次样本来源；
当前交付引用与阻断以本文首节“当前净室验证周期”为准。

public install wrapper `59b603a` precheck PASS、exit 0；真实 CMDB 108977826、五项 refs、policy valid。#507 已合并 `4af219e9486bdcd1c7cdb053795fa55e692efb29`（head `08ecf3`，用户最新回执），installer owner 独占 actual apply；首次实际执行已在主机写入前失败，修复后重试待回执。

| 项目 | r101 现场结果 |
| --- | --- |
| 发布路径 | installer owner 独占实际 apply；预检 PASS，部署回执待补 |
| GitOps | #507 已合并 `4af219e9486bdcd1c7cdb053795fa55e692efb29`，head `08ecf3`；owner 975693；历史 precheck `59b603a` PASS、exit 0 |
| Playbook | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Doco-CD | NOT_RUN；最后样本无 Docker/Caddy |
| Accounts | r101 / b423432dc5f993e5261423e27373703aaff48f2d；sha256:39716c2941b6f8ebbc0602589a59711d846234cb8313ae21254a91ba6073def7（已发布；运行匹配 NOT_RUN） |
| Console | r101 / 02607cf315570097606d90a8ba514fe37dcbe9e6；sha256:cc9b85339d82cefd264455c3d28c4e25dcd9e293378675855e23822730d5d0c5（已发布；运行匹配 NOT_RUN） |
| schema | 声明 2026102002；目标实际 schema/dirty NOT_RUN |
| 启动写入 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| 健康与版本 | NOT_RUN；尚无运行应用验收 |
| 未更新的服务 | V5 尚无运行应用；V4 保持服务和写入 |
| 数据核验 | NOT_RUN；无 V5 业务行数/指纹 |
| 配置核验 | precheck policy valid；运行时配置 hash 尚无回执 |
## 历史明细（2026-10-23 早期 Singapore 样本，已被当前净室周期取代）

以下第 1–7 节及其追加记录按原时间背景保留。其中“当前”“本次”“最新”均指各自旧采样，不代表 2026-10-24 净室主机；Docker、运行镜像、schema、33 users 与备份恢复的当前结论见本文首节。

## 1. 环境与实际部署

历史 V5 证据（2026-10-23 早期采样，已取代）：

项目；现场结果

主机；Akamai Singapore，2 vCPU / 4 GiB / 80 GiB；替换后实例 108977826，目标地址 104.64.208.209（用户明确要求记录）
SSH / 初始化；最新交接 SSH 可连接、cloud-init 完成；最后样本仅 22 监听，无 Docker、Caddy、运行应用
部署路径；主线 owner 继续 SSH → Playbook → 固定 GitOps → Doco-CD 安装；本知识库任务未执行
GitOps；[#507](https://github.com/ai-workspace-infra/gitops/pull/507)，precheck 来源 `59b603a`，固定 Playbooks owner `975693`；public install wrapper 真实 precheck PASS、exit 0，真实 CMDB 108977826、五项 refs 和 policy valid。主线已合并 #507（`4af219e9486bdcd1c7cdb053795fa55e692efb29`；head `08ecf3`，用户最新回执）；installer owner 独占 actual apply；首次实际执行已在主机写入前失败，修复后重试待回执
Playbooks；[#732](https://github.com/ai-workspace-infra/playbooks/pull/732)、[#733](https://github.com/ai-workspace-infra/playbooks/pull/733) 已合并（最新交接）；不替代安装与 runtime 结果
服务与写入；V5 尚无运行验收；V4 继续承接公共服务和业务写入，公共 DNS 切换待验收及人工授权

| 项目 | 现场结果 |
| --- | --- |
| 主机 | Akamai Singapore；实例 108977826，104.64.208.209；最后样本 SSH 可用、仅 22 监听 |
| 平台 | Akamai Singapore；2 vCPU / 4 GiB / 80 GiB |
| 部署模式 | SSH → Playbook → 固定 GitOps → Doco-CD；actual apply 已尝试并在主机写入前 FAIL，修复重试 PENDING |
| 发布引用 | daily-build-2026.10.23-r101；候选制品，尚无运行引用 |
| GitOps 实际 SHA | #507 precheck 来源 59b603a；#507 已合并 `4af219e9486bdcd1c7cdb053795fa55e692efb29`（head `08ecf3`，用户最新回执），尚无 Doco-CD runtime revision |
| Doco-CD | NOT_RUN；最后样本无 Docker/Caddy |
| 独立数据盘 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| PostgreSQL 挂载 | NOT_RUN；无实际挂载回执 |
| 实际业务库 | NOT_RUN；最后样本 PG 数据目录不存在 |
| Caddy 主机配置 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Caddy 激活模式 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| 入口配置 SHA-256 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
## 2. 容器构件

历史 V5 证据（2026-10-23 早期采样，已取代）：

以下五项是已发布 r101 候选 pin，**不是运行容器清单**。来源为 GitOps V5 proposal 与用户制品交接；统一 tag `daily-build-2026.10.23-r101`。

服务；tag / source SHA；完整 digest

Accounts / ghcr.io/ai-workspace-services/accounts；b423432dc5f993e5261423e27373703aaff48f2d；39716c2941b6f8ebbc0602589a59711d846234cb8313ae21254a91ba6073def7
Billing / ghcr.io/ai-workspace-services/billing-service；77557d796a66dcd3373d7731125890bd91ebc5d3；14bbaee5ba37d85ddf243272ee2c3bed25603ee26ffd5c0b8d685cfe0e7a85a0
Console / ghcr.io/ai-workspace-services/console；02607cf315570097606d90a8ba514fe37dcbe9e6；cc9b85339d82cefd264455c3d28c4e25dcd9e293378675855e23822730d5d0c5
Content / ghcr.io/ai-workspace-services/docs；94e722c913a8c6e8adbb5b0bd363b20c9d3b4d08；e6e791437bd3b57a4dec0bc9dc2527b681dd52960b6f692be6ff16322018788e
PostgreSQL / ghcr.io/ai-workspace-services/postgresql；253d69a3ad19558a4bd272dee0509a498e091e24；56f4179bafafa52061ac21003dc80c1a0b7ceb63fffb2c7bd05f29237b62b85e

PostgreSQL registry OCI index 已验证，child manifest 前缀 `7f643d59`；chart 来源前缀 `9417`，release 已发布（用户交接，完整 child/chart SHA 待归档）。index、child manifest、image config 是不同层级；不将本地 image ID 作为 registry pin。较早 GHCR 代理推送失败属于历史尝试。五项联合 provenance、目标拉取和运行镜像匹配仍需新鲜回执；CI run ID 未提供，不填推测值。

| 服务 | tag / source SHA | 完整 digest |
| --- | --- | --- |
| Accounts | r101 / b423432dc5f993e5261423e27373703aaff48f2d | sha256:39716c2941b6f8ebbc0602589a59711d846234cb8313ae21254a91ba6073def7（已发布；运行匹配 NOT_RUN） |
| Billing | r101 / 77557d796a66dcd3373d7731125890bd91ebc5d3 | sha256:14bbaee5ba37d85ddf243272ee2c3bed25603ee26ffd5c0b8d685cfe0e7a85a0（已发布；运行匹配 NOT_RUN） |
| Console | r101 / 02607cf315570097606d90a8ba514fe37dcbe9e6 | sha256:cc9b85339d82cefd264455c3d28c4e25dcd9e293378675855e23822730d5d0c5（已发布；运行匹配 NOT_RUN） |
| PostgreSQL | r101 / 253d69a3ad19558a4bd272dee0509a498e091e24 | sha256:56f4179bafafa52061ac21003dc80c1a0b7ceb63fffb2c7bd05f29237b62b85e（已发布；运行匹配 NOT_RUN） |
| Caddy | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Doco-CD | NOT_RUN；最后样本无 Docker/Caddy | NOT_RUN；无运行镜像回执 |
## 3. 域名、SNI 与路由

历史 V5 证据（2026-10-23 早期采样，已取代）：

[IaC #461](https://github.com/ai-workspace-infra/iac_modules/pull/461) 修复 `8a0bb444` 的实际 apply 创建四条 A → `104.64.208.209`；Cloudflare API 已确认，重复 preview 四条均 `noop`，provider 幂等性 PASS，`public_aliases_modified=false`。

域名；当前解析归属；本轮 HTTPS/SNI 结果

console-selfhost-prod-v5.svc.plus；Google DoH A 已验证目标；早期回执 TTL 60、status 0；HTTPS/SNI、登录及 runtime NOT_RUN
accounts-selfhost-prod-v5.svc.plus；provider 已确认；独立查询超时/待补；NOT_RUN
billing-selfhost-prod-v5.svc.plus；provider 已确认；独立查询超时/待补；NOT_RUN
postgresql-selfhost-prod-v5.svc.plus；Google DoH A 已验证目标；DB 连接、隧道/TLS NOT_RUN；不是普通 HTTPS 页面

早期四域 NXDOMAIN 为 apply 前历史状态。本地 resolver 负缓存/代理路径仍可能返回 NXDOMAIN；其他查询超时不能当作记录不存在。尚不能声称所有 resolver 或全球传播均通过。公共别名仍指向 V4，后续人工切换单独留证。

| 域名 | 当前解析归属 | 本轮 HTTPS/SNI 结果 |
| --- | --- | --- |
| `console.svc.plus` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `accounts.svc.plus` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `billing.svc.plus` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `xworktech.com` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `www.xworktech.com` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `console-selfhost-prod-v4.svc.plus` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `accounts-selfhost-prod-v4.svc.plus` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `billing-selfhost-prod-v4.svc.plus` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `postgresql-selfhost-prod-v4.svc.plus` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
## 4. 运行配置、身份与权威引用

历史 V5 证据（2026-10-23 早期采样，已取代）：

只记录路径、字段和状态，不记录任何值。以下路径由用户明确要求写入本白皮书。

用途；Vault KV v2 API 路径；CLI 路径 / 字段

Cloudflare serverless API；`kv/data/prod/serverless/cloudflare`；`kv/prod/serverless/cloudflare`：`ACCOUNT_ID`、`API_TOKEN`
既有 Selfhost DNS；`kv/data/CICD`；`kv/CICD`：`DNS_API_TOKEN`；与上行用途分开
PROD SSH deploy key；`kv/data/CICD/prod`；`kv/CICD/prod`：`SSH_PRIVATE_DEPLOY_KEY_B64`、`SSH_PUBLIC_DEPLOY_KEY_B64`

[写入脚本（固定提交）](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/86366b2c/scripts/vault/write-prod-ssh-deploy-key.sh)：`scripts/vault/write-prod-ssh-deploy-key.sh`，Toolkit commit `86366b2c`，branch `feature/vault-prod-ssh-key-writer-20261023`。脚本已创建并完成语法检查；[Toolkit PR #1428](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/1428) 本次远端复核为 MERGED，merge commit `ae917b221b61845fca8af4e9f63696c63d80d82f`。本任务未执行，不能据此声称生产凭据已更新。链接使用仓库路径，不包含操作员本机 home。

授权操作员从 toolkit checkout 使用：

```bash
VAULT_ADDR=https://vault.svc.plus bash scripts/vault/write-prod-ssh-deploy-key.sh
```

脚本派生公钥并比对本机 key pair，只 patch 两个 B64 字段。本任务未执行脚本、未写 Vault。最新只读 keys 观察确认 public 字段现在存在；Vault 中私钥/公钥是否匹配 **未验证**，字段存在不构成配对通过。实际运行时引用由固定 owner 校验，值与访问就绪需独立证据。

| 项目 | 核验结果／合同 |
| --- | --- |
| Accounts 实际 DB 角色 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Billing 实际 DB 角色 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| 数据库密码权威来源 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| 共享服务令牌权威来源 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Accounts `DATABASE_BACKGROUND_WRITERS` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Billing `DATABASE_BACKGROUND_WRITERS` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Billing `BILLING_INGEST_MODE` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Billing `DEFAULT_REGION` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Accounts 共享租户域 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Console `RUNTIME_HOSTNAME` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Accounts 配置挂载 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
### Stripe Sandbox / Live 配置合同（2026-10-21 补记）

| 配置项 | Sandbox / Test | Live | 说明 |
| --- | --- | --- | --- |
| Webhook URL | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| API secret key | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| Webhook signing secret | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
## 5. 数据与 schema 基线

历史 V5 证据（2026-10-23 早期采样，已取代）：

V5 数据目录在最后主机样本中不存在。没有当前业务库、schema dirty 状态、行数、指纹或迁移 run ID。proposal 所含 schema `2026102002` 是声明输入，不能写成目标实际 schema。源 V4 计数继续保留原采样时间，不复制为 V5 数据事实。迁移及目标对账 **NOT_RUN**。

| 对象 | 数量／版本 |
| --- | --- |
| schema | 声明 2026102002；目标实际 schema/dirty NOT_RUN |
| `users` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `subscription_records` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `subscriptions` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `account_quota_states` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `traffic_minute_buckets` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
| `billing_ledger` | NOT_RUN；实际状态及已有证据见本节 V5 更新，声明不代表运行值 |
## 6. 快照清单：完成状态必须分开

历史 V5 证据（2026-10-23 早期采样，已取代）：

项目；状态；实际位置 / 校验 / run ID

V5 DB / globals 加密备份；NOT_CREATED；无
V5 配置及镜像 manifest；NOT_CREATED；无
V5 Vault 加密快照；NOT_CREATED；无；共享 Vault 恢复须独立范围
V5 SHA256SUMS 与主机外副本；NOT_CREATED；无
V5 隔离恢复与应用连接验收；NOT_RUN；无
V4 历史备份；仅引用 V4 基线第 6 节；不扩大为最新 V5 快照

实际 V5 快照尚未创建；不生成看似真实的目录、文件名、时间戳或 run ID。后续应归档一致性边界、schema/行指纹、加密文件与校验、独立恢复、实际应用连接和主机外副本回执。

### V2 历史全量快照

### V3 在线快照与跨机恢复

### V4 含业务数据的历史备份及隔离恢复

| 项目 | 回执事实 |
| --- | --- |
| V5 备份 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 归档 SHA-256 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 完成时间 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 隔离恢复库 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 数据恢复结果 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 恢复前后业务行指纹 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 恢复 schema 指纹 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 权限指纹 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 业务验收边界 | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
### 历史占位：当时尚未创建的 V5 全量快照

| 文件 | 本轮重新计算的 SHA-256 |
| --- | --- |
| V5 归档（尚未创建） | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 归档（尚未创建） | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 归档（尚未创建） | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
| V5 归档（尚未创建） | NOT_CREATED / NOT_RUN；无 V5 实际文件或校验；历史 V2/V3/V4 仅引用原记录 |
## 7. 历史采样的证据限制

历史 V5 证据（2026-10-23 早期采样，已取代）：

case / action；状态；run ID / 证明

DNS provider apply + repeat preview；PASS（主线交接）；run ID 未提供；CF 四记录及四 noop 回执
Google DoH Console + PostgreSQL；PASS（限定两域）；run ID 未提供；其余域独立验证 PENDING
SSH key 字段可见；OBSERVED；public key 字段存在；pair-match NOT_RUN
SSH 写入脚本；SYNTAX_CHECKED / NOT_EXECUTED_BY_THIS_TASK；无 Vault 写入回执
GitOps #507 public install wrapper precheck；PASS，exit 0；`59b603a`；真实 CMDB 108977826、五项 refs、policy valid；run ID 未提供
#507 main merge / 固定引用安装；已合并 `4af219e9486bdcd1c7cdb053795fa55e692efb29`，head `08ecf3`；actual apply FAIL（主机写入前）；installer owner 独占执行，修复重试 PENDING
一次性实际部署后立即 runtime tests；部署尝试 FAIL，runtime tests NOT_RUN；无 run ID；不以离线 manifest PASS 代替
DB 初始化、迁移、权限与数据对账；NOT_RUN；无运行回执
登录、账务、采集、恢复与稳定观察；NOT_RUN；无运行回执
公共 DNS / 写入切换；NOT_RUN；验收后人工授权

后续 case 结果绑定固定 source SHA、镜像 digest、owner SHA、目标、执行时间与真实 run ID。未获结果继续保留 NOT_RUN/PENDING；本轮知识库变更不执行 installer，不创建快照或迁移。


## 追加执行回执：合并版预检与 SSH 连接阶段失败

2026-10-23 主线最新确认；以下更新覆盖前文旧采样中的待执行状态，不改写旧回执的来源。

| case / action | 实际结果 | 边界与后续动作 |
| --- | --- | --- |
| 合并版 public installer --check | PASS，exit 0 | GitOps `4af219e9486bdcd1c7cdb053795fa55e692efb29`；不同于此前 `59b603a` 预检，run ID 未提供 |
| 完整 installer actual apply | FAIL，主机写入前 | `Owner stage failed; private output withheld`；未产生 Docker/Caddy 部署或 runtime 验收 |
| 主线隔离语法检查 | PASS | 仅证明脚本语法，不证明连接与部署成功 |
| 实际 Ansible 初次 ping | FAIL，exit 4 | SSH banner timeout；手工 SSH 偶尔成功，连接状态并非持续稳定 |
| 显式 identity 的 Ansible 探针 | PASS，changed=false | `-T30`，显式 `id_ed25519`；只证明该次连接探针成功，无应用安装回执 |
| 完整 installer 默认 SSH timeout | FAIL | 默认 10 秒连接超时在主机写入前失败；不能用 30 秒独立探针替代完整 installer 重试 |
| owner 修复 | 实现中 / PENDING | 有界 connect timeout/retry 与脱敏 failure-stage；尚无修复后完整 apply 回执，不记为已修复 |

最后主机样本仍无 Docker/Caddy。实际迁移、runtime 回归和 V5 快照仍未执行/创建；V4 公共服务和业务写入保持原状态。主线 installer owner 独占生产执行，本知识库 PR 仅更新回执。

## 历史追加执行回执：旧固定版本与 exit 4 阻断

2026-10-23 更新。PR/tag 状态由本次远端查询确认；主机、DNS provider 与 smoke 事实来自用户主线核验，
本知识库任务没有再次执行 installer、SSH 或 Vault 读取。新结果不能反向改写早期失败尝试。

| case / action | 当前事实 | 验证边界 / 下一项证据 |
| --- | --- | --- |
| Playbooks owner #734 | MERGED，`19f4c3265dc66a9f561bad0441fd17e40649bc6b` | 有界 SSH timeout/retry 与脱敏阶段修复已合并；尚无完整安装成功回执 |
| GitOps #509 / 不可变 tag | MERGED，`b10d14d35ce77b4fa96d5ad6e7699ea8ec8441f2`；`v2026.10.23-v5-r1` 指向同一提交 | 固定发布引用已核实，目标实际运行 revision 未取得 |
| 先前 launcher binding 尝试 | apply 曾通过 SSH 后在 Vault resolve 阶段失败；launcher 导出 `VAULT_TOKEN`，policy 要求 `V5_CONTROL_PLANE_VAULT_TOKEN` | 该次操作员环境变量绑定不一致；13 个引用字段非空、格式有效。不是凭据无效或 role 格式错误的证据；不将它当作当前 exit 4 的已确认根因 |
| launcher lookup 修正与后续重试 | 主线报告修正并重试；交接标识 `57636` | 未知是否为 CI run ID，不构造 Actions 链接；无最终成功回执 |
| 最新主机样本 | 仅 22 监听，Docker 未安装，owner journal 存在 | journal 证明存在执行记录，不证明应用部署；当前失败阶段需脱敏 journal 回执 |
| 控制端依赖实证 | 初始只有 `community.hashi_vault 7.1`，缺少 `ansible.posix`；最小 `import_role vhosts/docker`、bootstrap=false 的 syntax-check exit 4 | `common/tasks/firewall_ports.yml:56` 不能解析 `ansible.posix.firewalld`。false when 不免除 parse 依赖；该次根因是控制端 collection 缺失，不是 SSH 不可达或云防火墙 |
| 顶层 syntax-check 覆盖缺口 | 原 owner 顶层检查未展开该动态依赖 | 增加动态角色解析 case，不能只检查顶层入口 |
| 控制端依赖补齐及同一复测 | `ansible.posix 2.1.0` 已安装；同一最小 syntax-check 从 exit 4 转为 exit 0 | 只证明该动态解析阻断已解除；不代表完整 installer 或目标运行健康通过 |
| 旧公共入口 actual apply | 固定 ref 重试 `60471` 已停止 | 标识类型未确认，不构造 Actions run 链接；未取得最终完整阶段及 runtime 通过回执，不标 ready |
| 四个版本 A 记录 | 已更新至目标地址，TTL 60、DNS only；公共 DNS 未动 | provider 状态来自主线；本轮只读 Google DoH 对 Console/Accounts/Billing/PostgreSQL 四域均返回 status 0、A `104.64.208.209`、TTL 60。只证明该外部 resolver 本次结果，不扩大为全球传播、TLS 或应用健康通过 |
| PostgreSQL r101 | 已发布；隔离 smoke PASS | 独立构件验证，不代表 V5 已拉取、初始化或服务健康通过；smoke run ID 未提供 |
| V5 runtime / 迁移 / 快照 | 健康验收未通过；迁移 NOT_RUN；快照 NOT_CREATED | 待安装成功、运行镜像与挂载核验、数据库健康、应用回归与独立恢复证据 |

控制端前置条件应固定并核验 collections：保留当前 `community.hashi_vault 7.1` 的已知版本事实，
显式安装固定 `ansible.posix 2.1.0`；持久 dependency manifest/owner 预检是否已实现仍待相应提交回执，
不能把本地安装写成仓库修复已合并。动态角色解析 case 必须在相同固定 owner/ref 下，使用
`import_role vhosts/docker` 和 bootstrap=false 重现解析路径，记录完整 collection 版本及 syntax-check
exit code；缺失 collection 应在主机操作前失败，安装后应复测原 case。云端安装后仍需独立验收。

旧 installer apply `60471` 已停止，该旧目标未验收。此前 exit 4 的已实证原因是控制端动态角色
collection 缺失；旧 SSH timeout 和 launcher binding 保留为各自历史尝试，不能替代此次根因。
主线 owner 继续实际安装；知识库只补充
脱敏事实。公共流量、写入和最终切换仍由 V4 保持，切换须验收后独立人工授权。

## 历代记录（V4 → V3 → V2 → V1）

1. [V4：运行基线与快照清单](../prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md)。
2. V3：仓库内可定位到[V2→V3 快照刷新、恢复与迁移记录](../prod-v2-v3-20261019/v2-to-v3-snapshot-refresh-20261019.zh.md)及[升级复盘](../prod-v2-v3-20261019/20261019-prod-v2-v3-snapshot-and-upgrade-retrospective.zh.md)；未找到独立命名为“V3 运行基线”的文件，保留此缺口。
3. [V2：冷备、容灾与跨机恢复记录](../prod-v2-v3-20261019/web-saas-prod-v2-cold-backup-disaster-recovery-whitepaper.zh.md)。
4. V1：当前仓库未找到可确认的 PROD V1 运行记录，标记为缺失；不以通用流程白皮书冒充历史基线。


## 配置与敏感引用补充（2026-10-24 用户交接）

本节为用户提供的配置及引用清单，V4、V5 共同归档；本次只修改文档，没有读取秘密值、重新枚举 Vault、修改运行配置或执行密钥写入。下列非敏感值不代表两个环境均已现场核验；已有带时间的运行采样继续保留，差异须通过对应环境的固定声明及实际进程独立复核。

### 核心运行配置与 checksum 边界

用户交接说明核心运行配置已保存 checksum、未保存 secret value。此次未提供对应 checksum、采样时间或证据编号，故不补造摘要，也不把此说明代替本文件已有的受控文件比较证据。

| 非敏感配置项 | 用户补充值 | 本次核验边界 |
| --- | --- | --- |
| `DATABASE_BACKGROUND_WRITERS` | `true` | 须分别核对 Accounts、Billing 实际进程；不由文档直接启用 |
| `BILLING_INGEST_MODE` | `push` | 保留 push 模式配置口径；不推导完整采集周期已验收 |
| `DEFAULT_REGION` | `jp` | 非敏感业务配置 |
| `XWORKMATE_SHARED_TENANT_DOMAIN` | `svc.plus` | 非敏感租户域配置 |
| `RUNTIME_HOSTNAME` | `console.svc.plus` | 公共域名配置口径，不代表 V5 已承接公共流量 |

V4 的 2026-10-21 采样记录为 Accounts/Billing 后台写入 `false`、Console 主机名为版本域名；本次补充值与该采样不同，标记 **待现场复核**，不追改历史。V5 的部署/幂等 PASS 证明其固定输入及运行状态稳定，不单独证明本表每项均为其实际生效值。V4 公共服务、公共 DNS 及写入权不因本节改变。

### 敏感信息 KV 路径清单

Vault 保存实际敏感信息；**文档仅保存路径和字段清单，不输出值**。用户交接称当时共发现 104 个 KV 路径；枚举时间及完整受控索引本次未提供，当前总数未重新核验。以下仅为相关引用子集，不声称每条都由 V4 或 V5 当前进程使用，也不创建带部署代际后缀的新权威路径：

- `kv/prod-v2/web-saas`（历史代际路径，保留引用背景）
- `kv/prod/accounts/runtime`
- `kv/prod/accounts/oauth/github`
- `kv/prod/accounts/oauth/google`
- `kv/prod/billing-service`
- `kv/prod/database-upgrade`
- `kv/prod/platform/smtp/google`
- `kv/CICD/domains/svc.plus`
- `kv/CICD/prod/gcp-bootstrap/xworktech`
- `kv/CICD/prod/iac_state`
- `kv/prod/XConnect/PH/PH-XConnect.svc.plus`
- `kv/prod/ulighthost-xconnect/observability.svc.plus`

### 历史部署密钥引用与写入入口

统一引用 `kv/CICD/prod`，字段为 `SSH_PRIVATE_DEPLOY_KEY_B64`、`SSH_PUBLIC_DEPLOY_KEY_B64`。不重复登记，不把 B64 编码视为加密。密钥内容不得提交到 Git、文档或日志。

复用已合并的 [Toolkit 写入脚本](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/ae917b221b61845fca8af4e9f63696c63d80d82f/scripts/vault/write-prod-ssh-deploy-key.sh)，不在 Knowledge 复制第二份执行实现。授权操作员在对应 Toolkit checkout 中运行：

```bash
bash scripts/vault/write-prod-ssh-deploy-key.sh
```

脚本读取当前操作员的 `~/.ssh/id_ed25519` 与 `~/.ssh/id_ed25519.pub`，核对文件归属、私钥权限、Ed25519 类型与密钥配对，通过标准输入向 Vault patch 这两个字段，保留同路径其他字段，失败时隐藏秘密输出。需已有 Vault 认证及该路径 patch 权限；本次仅核对已合并脚本和语法，**未执行写入、未验证 Vault 中现存密钥配对**。更新 Vault 不自动更新主机 authorized_keys，也不自动轮换运行中的连接身份。

### Stripe Sandbox / Live 共用配置合同

统一在 `kv/prod/billing-service` 管理，按 Stripe 环境区分，不添加 V3/V4/V5 部署代际后缀；Live 沿用既有 `PROD_` 命名。

| 配置项 | Sandbox / Test | Live |
| --- | --- | --- |
| Webhook URL | `SANDBOX_STRIPE_WEBHOOK_URL` | `PROD_STRIPE_WEBHOOK_URL` |
| API secret key | `SANDBOX_STRIPE_SECRET_KEY`，预期前缀 `sk_test_…` | `PROD_STRIPE_SECRET_KEY`，预期前缀 `sk_live_…` |
| Webhook signing secret | `SANDBOX_STRIPE_WEBHOOK_SECRET`，预期前缀 `whsec_…` | `PROD_STRIPE_WEBHOOK_SECRET`，预期前缀 `whsec_…` |

用户交接的 Sandbox 端点为 [Accounts Stripe webhook](https://accounts.svc.plus/api/billing/stripe/webhook)：Vault URL 字段当时为空，实际路由来自 GitOps，验签正常属于来源交接的历史结论，本次未重新验证。Live 交接只提供到 `https://accounts-serverless-prod.svc.plus/api/billing/`，路径不完整，标记 **待补**，不猜测后缀、不发送测试付款或重投事件。本合同用于两个环境查阅，不意味着 V5 的支付、回调或业务验收已完成。

对应代际记录：[V4 运行基线与快照清单](../prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md)。
