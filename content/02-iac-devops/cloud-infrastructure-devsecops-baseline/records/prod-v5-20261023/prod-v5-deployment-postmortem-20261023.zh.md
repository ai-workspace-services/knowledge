# PROD V4→V5 部署流程复盘

## 公共 Console 后续故障（2026-10-24 12:18 +08 更新）

DNS 校验正确仍发生白屏：实际 Caddy 缺少公共 Console site/matcher，返回空 HTTP 200。已由 [Playbooks #746](https://github.com/ai-workspace-infra/playbooks/pull/746) 与 [GitOps #521](https://github.com/ai-workspace-infra/gitops/pull/521)修复，增加真实 HTML 的可信 HTTPS 门禁；规范配置和控制器选择重放均无变更。详见[完整回执](20261024-prod-v5-public-console-route-repair.zh.md)。本次修订把当前环境与旧时间线分开，保留先前仅检查 DNS 的证据范围。

## 后续复盘与闭环（2026-10-24）

[业务追加与真实流量回执](20261024-prod-v5-business-append-and-traffic-regression.zh.md)和[修复后环境快照](20261024-prod-v5-post-repair-environment-snapshot.zh.md)补充以下结论；原有失败时间线保留，不被后续成功覆盖。

| 问题源头 | 修复与最佳实践 | 回归/实证 |
| --- | --- | --- |
| 控制器 collection 未在角色解析前准备 | 安装入口先准备解析依赖；OS/角色执行仍归 Playbooks | 原净室部署回执及固定 installer 引用 |
| 全新候选误带只读写方法限制 | 新部署正常服务请求不套用迁移源保护；迁移源只读独立实施 | 原登录 403/解析故障与修复链按原时间保留 |
| 公共 Agent/Billing 域名未匹配实际 upstream | 明确公共别名路由；Billing 只放行快照与健康检查，不能把空 HTTP 200 当成功 | Playbooks #744/#745、GitOps #518/#519；`tests/control_plane/test_owner.py`，真实采集入库 |
| users-only 被误作完整业务迁移 | 先列数据范围，再追加套餐/订阅/额度/历史账务；关联到目标既有用户 UUID | Accounts #272；实际追加 152,353 行，其他用户身份冲突继续阻断 |
| 在线计划绑定无关心跳及引擎统计 | 计划绑定被审查业务范围与已验证身份映射；事务内保护所有非同步表，结构校验排除非结构统计 | Accounts #273；`TestFullBusinessUsageMergePostgres17`；V5 三轮零写入重放 |
| Exporter 进程缺少 canonical 凭据 | 比对 Vault、文件及实际进程；只修复 Exporter，保留 Vector 推送路径 | JP01/JP Plus 修复及三节点零变更复跑；JP Plus 两周期 +8 桶/+8 账本 |
| 没有策略也显示正常 | 区分未生成、未就绪、过期与空闲；余额和采样不造默认成功值 | Portal #466、GitOps #520；真实登录会话与数据库汇总一致 |
| 旧恢复点只含用户、不能证明迁移后可恢复 | 完成数据迁移和采集修复后重新取完整快照，再实际隔离恢复与异机校验 | 本次 76 表、33 users、7 subscriptions、18 plans，摘要及序列一致，业务重启 0 |

仍未关闭：源端没有策略快照生产结果、空闲/未验收节点正流量、OAuth/MFA 重新登录、支付及完整环境恢复演练。静态快照不解决 V4/V5 持续并行写入的最终追齐问题；DNS 与写入权变化保持独立人工门禁。

---

原始故障主题：资源替换后未进入可部署状态（2026-10-23 历史样本）。

记录日期：2026-10-23（Asia/Shanghai）；状态更新至 18:29 +08。主机检查是有时间边界的
样本；DNS 写入与 PR 状态按本次更新分别记录。本文保留该时点的部署中断事实；2026-10-24 r5 部署、r103 users-only 同步与隔离恢复已由[V5 运行基线](prod-v5-runtime-and-snapshot-baseline-20261023.zh.md)追加，不把旧“Docker 未安装/部署待执行”表述沿用为当前状态。与[V4 运行基线](../prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md)
及[V3→V4 复盘](../prod-v3-v4-20261020/v3-v4-upgrade-retrospective-20261021.zh.md)配套阅读。

代际索引：[V4→V5 基线与升级复盘](../../17-prod-v4-v5-baseline-and-upgrade-retrospective.zh.md) · [统一部署与迁移流程](https://github.com/ai-workspace-services/.github/blob/main/docs/control-plane-deployment-and-migration.zh.md)。

<!-- BEGIN CLEANROOM 20261024 -->
## 2026-10-24 净室周期追加（2026-10-24 03:09 +08）

原 10-23 的 Docker/依赖/SSH 采样及 01:07 的 r5/r103 回执保持原时点。最新[净室回执](prod-v5-cleanroom-deployment-migration-validation-20261024.zh.md)已实测 V5 精确删除、重建、部署、在线 users-only 同步与独立恢复。新周期发现并分别修复：源 state 无序校验集合导致删除前误报（[IaC #465](https://github.com/ai-workspace-infra/iac_modules/pull/465)）；创建后 IPv6 `/128` 导致 CMDB 发布失败（[IaC #466](https://github.com/ai-workspace-infra/iac_modules/pull/466)）；新机缺完整可信 SSH 指纹采集路线（[IaC #464](https://github.com/ai-workspace-infra/iac_modules/pull/464)）；users-only 沿用暂停写进程前提（[Accounts #271](https://github.com/ai-workspace-services/accounts/pull/271)，真实使用预构建 r104）。三轮带数据重验为 **PASS（3/3）**。终点只读复核另发现上游 Proxy UUID/版本/有效期字段增量，最终追齐仍 BLOCKED，未改变 V4 写入权。每个失败与重验独立记录，不将资源创建成功改写为当次 owner 全流程成功，也不把候选就绪写成业务或切换通过。

<!-- END CLEANROOM 20261024 -->

## 1. 结论与影响边界

V5 已完成获授权的云实例替换和基础云初始化；主线 DNS owner 后续通过 `--apply` 创建了四条
版本化记录，并收到 Cloudflare 创建成功回执。但应用容器仍未部署，控制面安装、PostgreSQL
初始化、业务数据迁移及应用验收均未完成。V4 仍是公共服务与业务写入来源；V5 未接管写入，
公共服务 DNS 未切换。本次记录不代表 V5 已上线或可承载流量。

状态更新（2026-10-23 18:29 +08）：四条版本化 DNS 记录由主线 owner 的 apply 创建，Cloudflare
回执确认创建成功，且 `public_aliases_modified=false`。之后的 provider preview 对四条记录均返回
`noop`，目标地址与预期 V5 地址一致，provider 幂等性 **PASS**。Google DoH 已验证 Console 的 A
查询返回预期 V5 地址，TTL 60、状态 0（NOERROR）；仅 Console 的外部递归解析记为 **PASS**，其余
三个别名尚无同等外部核验。与此同时，本机 `dig` 仍返回 NXDOMAIN，符合本地负缓存/网络代理路径的
现象；这不推翻 provider 写入或 Google DoH 的结果，也不等于权威记录不存在。权威服务器直接查询、
其余三个别名的外部解析及 HTTPS/SNI 仍待独立验证。当前没有 Docker 应用容器；DNS 成功不代表服务
已部署。用户期望在前置输入和运行时 Vault 引用修复就绪后，一次性执行实际部署并紧接 runtime
测试；该操作与测试仍为 **PENDING / NOT_RUN**。

本次可确认的故障边界是“基础设施已替换，但部署链未到达可运行应用”：主机采样显示仅 SSH
监听，未发现 Docker、控制面目录或 PostgreSQL 数据目录；初始 DNS 检查时四个 V5 版本别名均无
A 记录，直接 HTTPS/SNI 请求失败。之后记录已创建且 provider preview 返回 noop，但独立解析及
HTTPS/SNI 复核仍 pending。尚无证据表明服务启动后发生应用或数据库故障，因为服务部署和迁移都未运行。

## 2. 证据时间线

| 阶段 | 已观察到的事实 | 证据边界 |
| --- | --- | --- |
| V4 基线 | 依照[既有 V4 运行快照](../prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md)，V4 仍承接公共入口和业务写入。 | V4 基线有自己的采样时间；不据此推断 V5 状态。 |
| 云资源替换 | 按明确授权将 V5 实例替换为 2 vCPU、4 GiB 内存、80 GiB 磁盘规格；替换后的 IaC 计划为 0 项变更，既有防火墙保持不变。 | 不在公开记录中保存实例 ID、IP 或防火墙 ID。该步骤只证明资源变更，不证明主机配置管理或应用部署完成。 |
| 主机采样（10-23） | SSH 主密钥可连接；cloud-init 已完成。采样中只有 22 端口监听，未发现 Docker、`/etc/xcontrol` 或 PostgreSQL 数据目录。 | 这是当日主机状态样本；没有容器、进程或数据库健康证据。 |
| 不可变构件 | `daily-build-2026.10.23-r101` 的四个应用构件曾发布；PostgreSQL 有干净源码构建，源码提交为 `253d69a3ad19558a4bd272dee0509a498e091e24`。观察到的 OCI index descriptor 摘要前缀为 `56f4179b`，其下 image config digest 前缀为 `6cc…`。 | OCI index 与 image config 是不同层级的摘要；二者不同是预期结构，不是损坏证据。完整 registry manifest 回读仍未完成；本地构建本身不证明制品已部署。 |
| 推送失败 | 较早一次 PostgreSQL GHCR 推送遇到代理连接关闭（`use of closed network connection`）。 | 这是该次推送尝试的失败记录；不把 index/config 摘要差异误判为损坏，也不据此声称随后完成了 registry 回读。 |
| DNS 初始采样 | 初始检查中四个版本服务别名均无 A 记录，解析失败；对目标的直接 HTTPS/SNI 检查失败。 | 这是 apply 之前的时间点，不代表后续 DNS 状态。 |
| DNS 写入更新（18:21 +08） | 主线 DNS owner 执行 `--apply`，Cloudflare 返回四条版本化记录已创建，`public_aliases_modified=false`。 | 该回执证明 provider 写入结果，不证明权威/public propagation 已完成。 |
| DNS provider preview（18:22 +08） | 首次 preview 因网络错误失败；后续 preview 对四条记录均返回 `noop`，目标地址与预期 V5 地址一致，`public_aliases_modified=false`。provider 幂等性 **PASS**。 | 不将 provider noop 扩大为解析/TLS 或应用验收。 |
| 外部解析与本机 resolver（18:29 +08） | Google DoH 对 Console A 查询返回预期 V5 地址，TTL 60、状态 0（NOERROR）；本机 `dig` 仍为 NXDOMAIN。 | 仅 Console 的外部递归解析 **PASS**；本机结果按负缓存/网络代理路径单列，不覆盖外部结果。其余三个别名、权威 DNS 直接查询与 HTTPS/SNI 仍 **PENDING**。 |
| 数据迁移与验收 | 没有执行迁移；没有服务健康、数据对账、回归或用户流量验收回执。 | 全链路部署、迁移与验收均为 **NOT_RUN**，不是 PASS。 |

历史 `r101` 工作流还保留了 PostgreSQL GitHub App dispatch 的 HTTP 422 与 actor 权限问题；它是早先的工作流事实，不应改写成此次主机运行错误。之后获准的本地构建路径属于单独的构建路线，不会自动补齐 registry push、manifest read-back 或部署证据。完整交付仍须满足 [`.github` PR #41](https://github.com/ai-workspace-services/.github/pull/41) 所述的来源、摘要、manifest 与制品回读契约。

## 3. 根因判断与促成因素

### 有证据支持的根因

交付流程把“实例替换及 cloud-init 完成”推进到了可交付边界之前，没有先取得全部服务的、可从 registry
回读的不可变构件，也没有完成主机引导和控制面 reconcile。证据是主机样本仍只有 SSH 入口、所需
运行目录/数据库目录不存在，同时 PostgreSQL 完整 registry manifest 回读尚缺。初始 DNS 检查
也未解析到目标；之后四条记录创建并通过 provider 幂等预检，Google DoH 已确认 Console 记录可解析，
但其余别名、权威查询和 HTTPS/SNI 尚未核验。DNS 初始失败已不能代表当前 Console 外部解析状态，
本机 NXDOMAIN 属于单独的 resolver 观察，不改变主机未部署这一根因判断。

这是阶段与交接门禁未收敛导致的部署中断。没有证据支持把根因归为应用回归、数据库迁移错误或
V4 数据问题，因为这些步骤没有开始。

### 促成因素和已知限制

- `r101` 的历史 dispatch 失败与后续手工构建路线没有被统一成完整制品证明；本地构建和四个应用
  构件发布的记录，不能覆盖 PostgreSQL manifest 缺口。
- GitOps 部署合同要求五个服务的不可变镜像 pin、Playbooks owner SHA 及新主机初始化元数据；
  schema/example 校验通过只证明合同检查，不会生成真实运行输入或完成部署。
- DNS 生成器使用 GitOps 声明和 IaC CMDB 作为输入；声明、渲染逻辑和 CI 通过均不等于 DNS
  已经写入，也不等于记录当前解析正确。
- [Playbooks #731](https://github.com/ai-workspace-infra/playbooks/pull/731) 合并的是离线回归清单与
  新鲜输入门禁。其 manifest 要求目标运行时输入，不能作为运行时 PASS 回执。
- [Playbooks #732：允许已建立的生产运行时 Vault 引用](https://github.com/ai-workspace-infra/playbooks/pull/732)
  已合并（merge commit `9ffee25530ddc10a1ad11a54252ea7d8297a58f7`）。它修复 Playbooks 对既有生产
  AUTH、CICD TLS/GHCR 引用的精确校验映射，不读取或改写 Vault 值、不创建凭据，也不运行安装器；
  合并不证明目标运行时 Vault 内容存在或部署已执行。

## 4. 已合并修复与当前 PR 状态

| PR | 当前状态 | 对本次复盘的意义 |
| --- | --- | --- |
| [IaC #460：生产资源替换需显式授权](https://github.com/ai-workspace-infra/iac_modules/pull/460) | MERGED；`ecddc9073d57a00abba79bb38f1bd26af1192583` 已核对为 `main` | 默认保留 `prevent_destroy`；生产替换必须显式授权。PR 本身未执行云资源操作。 |
| [IaC #461：由 GitOps/CMDB 渲染四个版本别名](https://github.com/ai-workspace-infra/iac_modules/pull/461) | MERGED；`8a0bb4440af820b9f2f0091ed00023f8e5e7de95` 已核对为 `main` | 固定声明、CMDB、四条记录的验证和预检已实现；合并本身不证明 DNS 写入，本次 apply 回执另见上文。 |
| [GitOps #504：部署与迁移声明合同](https://github.com/ai-workspace-infra/gitops/pull/504) | MERGED | 明确五服务镜像 pin、Playbooks SHA、初始化输入和分阶段验收；示例仍不能替代真实输入。 |
| [Playbooks #730：安装、权限与路由修复](https://github.com/ai-workspace-infra/playbooks/pull/730) | MERGED | 包含恢复 ACL/grant 导致 SQLSTATE `42501` 的路径，以及持久目标私有路由目录设计；合并不代表本机已执行。 |
| [Playbooks #731：V5 回归批次准备](https://github.com/ai-workspace-infra/playbooks/pull/731) | MERGED | 1d64444d5a99d8eb45ee9c2004dd4f404be6272a 提供离线回归 manifest 和输入门禁；不是部署或运行验收。 |
| [Playbooks #732：允许已建立的生产运行时 Vault 引用](https://github.com/ai-workspace-infra/playbooks/pull/732) | MERGED；`9ffee25530ddc10a1ad11a54252ea7d8297a58f7` | 精确修复引用校验映射；不读取 Vault 值、不创建凭据、不运行安装器，亦不代表运行时值/访问或部署已就绪。 |
| [`.github` #41：部署证据与切流门禁](https://github.com/ai-workspace-services/.github/pull/41) | MERGED；`546cac02dd7f492e54e02eaf4ff0e2fc8c768404` 已核对为 `main` | 已合入八阶段交付、不可变制品证明及 DNS/切流授权边界；合并不代表 V5 已部署或验收。 |

## 5. 恢复顺序与验收门

以下是后续交付的证据顺序，不是本次已执行操作。每个阶段必须绑定实际引用和回执；任一前置项缺失
时，后续阶段保持 **BLOCKED / NOT_RUN**。

1. **固定输入**：完成 GitOps 所需五个服务的源码 SHA、不可变 registry 引用及 manifest/digest
   回读；确认 PostgreSQL 摘要对应实际发布制品，而非本地镜像 ID。记录 Playbooks owner SHA、
   初始化元数据与目标 CMDB 来源。
2. **主机引导**：通过授权的 SSH → Playbook → 固定 GitOps → Doco-CD 路径安装依赖并 reconcile。
   留存主机配置、容器清单、挂载、网络边界及各进程来源核验；确认 PostgreSQL 完成原生初始化、
   持久数据目录就绪，再进入服务健康检查。
3. **一次性部署与 runtime 测试**：在运行时 Vault 引用修复已合入、运行时值/访问已核验、五项不可变
   制品和新鲜部署输入齐备后，按授权路径一次性执行实际部署，并紧接着运行服务、数据库、身份/账务及
   Console 健康测试；保存命令回执、固定 SHA/digest、运行容器和测试结果。该阶段当前 **PENDING / NOT_RUN**，
   不得用 DNS、Playbook 校验或旧主机采样代替。部署/测试通过仍不代表迁移或切流获准。
4. **候选域名验证**：先核对 GitOps 声明、CMDB、四条版本别名的计划和 DNS 查询结果；执行 DNS
   写入需要独立授权。验证解析、证书/SNI 和各服务版本/健康端点，不将渲染或 CI 结果记作写入回执。
5. **备份与迁移预检**：确认源端只读、目标端隔离和真实备份/恢复收据；使用固定迁移工具执行只读
   预览，对身份、账务、配额和权限冲突停止，不覆盖源数据。缺少数据边界、双端身份或恢复证明时不 apply。
6. **迁移和回归**：仅在独立审批及前置证明具备后执行受控单向迁移。对目标进行数据对账、权限、登录、
   Accounts/Billing/Console/PostgreSQL 健康、采集写入和业务回归；以固定 SHA、digest、SQL 版本、
   采样时间及可复查回执记录结果。
7. **保持 V4 写入与最终切换分离**：V4 公共服务和写入继续作为来源，直到目标部署、恢复、迁移、
   回归及稳定观察均有通过证据。公共 DNS 切换是独立的人工门禁，需要重新确认写入所有权、数据
   追齐和回滚方向；任何 PR merge、CI 绿灯或主机健康探针都不授权切流。

## 6. 状态总表

| 项目 | 2026-10-23 状态 |
| --- | --- |
| 获授权的云实例替换 | 已完成；资源身份不公开记录 |
| cloud-init / SSH | 样本中已完成 / 可连接 |
| Docker、控制面、PostgreSQL 初始化 | 未观察到 / 未完成 |
| V5 DNS | 四条记录 apply 已确认，四条 provider preview 均 `noop`（provider 幂等性 PASS）；Google DoH 的 Console A 查询 TTL 60/status 0，外部解析 PASS；本机 `dig` NXDOMAIN（本地负缓存/网络代理路径观察）；其余三个别名、权威直接查询与 HTTPS/SNI PENDING |
| 应用构件 | 四个应用构件曾发布；完整 registry manifest 未逐项回读 |
| PostgreSQL 构件 | 本地干净源码构建；OCI index descriptor `56f4179b…` 与 image config `6cc…` 为不同层级、属于预期结构；早先 push 失败，完整 registry manifest 回读未完成 |
| Docker 应用 | 仍未部署；DNS apply 不代表应用容器已运行 |
| Playbooks #732 Vault 引用校验修复 | MERGED；`9ffee25530ddc10a1ad11a54252ea7d8297a58f7`；不代表 Vault 值/访问就绪 |
| 一次性实际部署及紧接 runtime 测试 | **PENDING / NOT_RUN**；等待真实输入与运行时访问核验 |
| 数据迁移、业务回归/验收 | **NOT_RUN** |
| V4 公共流量与写入 | 保持为来源；无 V5 接管证据 |
| 公共 DNS 切换 | 未执行；仍需单独人工授权及完整验收 |

本文件只记录证据与门禁，不是第二套 GitOps 配置、部署授权或生产操作回执。原始日志、凭据、
实例 IP/ID、防火墙 ID 及具体内部主机名不进入该公开知识库。
