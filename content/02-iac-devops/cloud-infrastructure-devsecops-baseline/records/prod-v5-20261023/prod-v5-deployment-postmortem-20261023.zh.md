# PROD V5 部署中断复盘：资源替换后未进入可部署状态

记录日期：2026-10-23（Asia/Shanghai）。本记录按该日可见的实例、构件、DNS 与 PR
证据整理；主机检查是有时间边界的样本，不代表后续状态。与[V4 运行基线](prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md)
及[V3→V4 复盘](prod-v3-v4-20261020/v3-v4-upgrade-retrospective-20261021.zh.md)
配套阅读。

## 1. 结论与影响边界

V5 只完成了获授权的云实例替换和基础云初始化；没有完成控制面安装、服务部署、PostgreSQL
初始化、业务数据迁移或应用验收。V4 仍是公共服务与业务写入来源；V5 未接管写入，公共 DNS
未切换。本次记录不代表 V5 已上线或可承载流量。

本次可确认的故障边界是“基础设施已替换，但部署链未到达可运行应用”：主机采样显示仅 SSH
监听，未发现 Docker、控制面目录或 PostgreSQL 数据目录；四个 V5 版本别名均无 A 记录，直接
HTTPS/SNI 请求失败。尚无证据表明服务启动后发生应用或数据库故障，因为服务部署和迁移都未运行。

## 2. 证据时间线

| 阶段 | 已观察到的事实 | 证据边界 |
| --- | --- | --- |
| V4 基线 | 依照[既有 V4 运行快照](prod-v3-v4-20261020/prod-v4-runtime-and-snapshot-baseline-20261021.zh.md)，V4 仍承接公共入口和业务写入。 | V4 基线有自己的采样时间；不据此推断 V5 状态。 |
| 云资源替换 | 按明确授权将 V5 实例替换为 2 vCPU、4 GiB 内存、80 GiB 磁盘规格；替换后的 IaC 计划为 0 项变更，既有防火墙保持不变。 | 不在公开记录中保存实例 ID、IP 或防火墙 ID。该步骤只证明资源变更，不证明主机配置管理或应用部署完成。 |
| 主机采样（10-23） | SSH 主密钥可连接；cloud-init 已完成。采样中只有 22 端口监听，未发现 Docker、`/etc/xcontrol` 或 PostgreSQL 数据目录。 | 这是当日主机状态样本；没有容器、进程或数据库健康证据。 |
| 不可变构件 | `daily-build-2026.10.23-r101` 的四个应用构件曾发布；PostgreSQL 有干净源码构建，源码提交为 `253d69a3ad19558a4bd272dee0509a498e091e24`，配置摘要前缀为 `56f4179b`。 | 未核验完整 registry manifest。PostgreSQL 本地编译产物/镜像 ID 不能替代 registry manifest 或 digest。 |
| 推送失败 | PostgreSQL GHCR 推送遇到代理连接关闭（`use of closed network connection`）。 | 未得到可读回的 registry manifest；不能把编译成功写成制品发布成功。 |
| DNS 与 HTTPS | 四个版本服务别名均无 A 记录，解析失败；对目标的直接 HTTPS/SNI 检查失败。 | 不包含 DNS 写入或证书签发/安装证明；没有切换公共入口。 |
| 数据迁移与验收 | 没有执行迁移；没有服务健康、数据对账、回归或用户流量验收回执。 | 全链路部署、迁移与验收均为 **NOT_RUN**，不是 PASS。 |

历史 `r101` 工作流还保留了 PostgreSQL GitHub App dispatch 的 HTTP 422 与 actor 权限问题；它是早先的工作流事实，不应改写成此次主机运行错误。之后获准的本地构建路径属于单独的构建路线，不会自动补齐 registry push、manifest read-back 或部署证据。完整交付仍须满足 [`.github` PR #41](https://github.com/ai-workspace-services/.github/pull/41) 所述的来源、摘要、manifest 与制品回读契约。

## 3. 根因判断与促成因素

### 有证据支持的根因

交付流程把“实例替换及 cloud-init 完成”推进到了可交付边界之前，没有先取得全部服务的、可从 registry
回读的不可变构件，也没有完成主机引导和控制面 reconcile。证据是主机仍只有 SSH 入口、所需
运行目录/数据库目录不存在，同时 PostgreSQL registry manifest 缺失。随后版本别名也未解析到
目标，因此无法通过 HTTPS 验证服务入口。

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

## 4. 已合并修复与当前 PR 状态

| PR | 当前状态 | 对本次复盘的意义 |
| --- | --- | --- |
| [IaC #460：生产资源替换需显式授权](https://github.com/ai-workspace-infra/iac_modules/pull/460) | OPEN | 默认保留 `prevent_destroy`；生产替换必须显式授权。PR 本身未执行云资源操作。 |
| [IaC #461：由 GitOps/CMDB 渲染四个版本别名](https://github.com/ai-workspace-infra/iac_modules/pull/461) | MERGED | 固定声明、CMDB、四条记录的验证和预检已实现；不等于 DNS 已写入。 |
| [GitOps #504：部署与迁移声明合同](https://github.com/ai-workspace-infra/gitops/pull/504) | MERGED | 明确五服务镜像 pin、Playbooks SHA、初始化输入和分阶段验收；示例仍不能替代真实输入。 |
| [Playbooks #730：安装、权限与路由修复](https://github.com/ai-workspace-infra/playbooks/pull/730) | MERGED | 包含恢复 ACL/grant 导致 SQLSTATE `42501` 的路径，以及持久目标私有路由目录设计；合并不代表本机已执行。 |
| [Playbooks #731：V5 回归批次准备](https://github.com/ai-workspace-infra/playbooks/pull/731) | MERGED | 1d64444d5a99d8eb45ee9c2004dd4f404be6272a 提供离线回归 manifest 和输入门禁；不是部署或运行验收。 |
| [`.github` #41：部署证据与切流门禁](https://github.com/ai-workspace-services/.github/pull/41) | OPEN | 记录八阶段交付、不可变制品证明及 DNS/切流授权边界；不能视为已合入规范。 |

## 5. 恢复顺序与验收门

以下是后续交付的证据顺序，不是本次已执行操作。每个阶段必须绑定实际引用和回执；任一前置项缺失
时，后续阶段保持 **BLOCKED / NOT_RUN**。

1. **固定输入**：完成 GitOps 所需五个服务的源码 SHA、不可变 registry 引用及 manifest/digest
   回读；确认 PostgreSQL 摘要对应实际发布制品，而非本地镜像 ID。记录 Playbooks owner SHA、
   初始化元数据与目标 CMDB 来源。
2. **主机引导**：通过授权的 SSH → Playbook → 固定 GitOps → Doco-CD 路径安装依赖并 reconcile。
   留存主机配置、容器清单、挂载、网络边界及各进程来源核验；确认 PostgreSQL 完成原生初始化、
   持久数据目录就绪，再进入服务健康检查。
3. **候选域名验证**：先核对 GitOps 声明、CMDB、四条版本别名的计划和 DNS 查询结果；执行 DNS
   写入需要独立授权。验证解析、证书/SNI 和各服务版本/健康端点，不将渲染或 CI 结果记作写入回执。
4. **备份与迁移预检**：确认源端只读、目标端隔离和真实备份/恢复收据；使用固定迁移工具执行只读
   预览，对身份、账务、配额和权限冲突停止，不覆盖源数据。缺少数据边界、双端身份或恢复证明时不 apply。
5. **迁移和回归**：仅在独立审批及前置证明具备后执行受控单向迁移。对目标进行数据对账、权限、登录、
   Accounts/Billing/Console/PostgreSQL 健康、采集写入和业务回归；以固定 SHA、digest、SQL 版本、
   采样时间及可复查回执记录结果。
6. **保持 V4 写入与最终切换分离**：V4 公共服务和写入继续作为来源，直到目标部署、恢复、迁移、
   回归及稳定观察均有通过证据。公共 DNS 切换是独立的人工门禁，需要重新确认写入所有权、数据
   追齐和回滚方向；任何 PR merge、CI 绿灯或主机健康探针都不授权切流。

## 6. 状态总表

| 项目 | 2026-10-23 状态 |
| --- | --- |
| 获授权的云实例替换 | 已完成；资源身份不公开记录 |
| cloud-init / SSH | 样本中已完成 / 可连接 |
| Docker、控制面、PostgreSQL 初始化 | 未观察到 / 未完成 |
| 四个 V5 版本别名与 HTTPS | DNS 无 A / 解析失败；直接 HTTPS 检查失败 |
| 应用构件 | 四个应用构件曾发布；完整 registry manifest 未逐项回读 |
| PostgreSQL 构件 | 本地干净源码构建；registry push 失败；manifest 未验证 |
| 服务部署、数据库迁移、业务验收 | **NOT_RUN** |
| V4 公共流量与写入 | 保持为来源；无 V5 接管证据 |
| 公共 DNS 切换 | 未执行；仍需单独人工授权及完整验收 |

本文件只记录证据与门禁，不是第二套 GitOps 配置、部署授权或生产操作回执。原始日志、凭据、
实例 IP/ID、防火墙 ID 及具体内部主机名不进入该公开知识库。
