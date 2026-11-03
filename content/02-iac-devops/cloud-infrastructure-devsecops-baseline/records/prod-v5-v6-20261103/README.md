# PROD V5 → V6 迁移、K3s 修复与代际演进归档 (2026-11-03)

> 记录日期：2026-11-03，Asia/Shanghai。
> 统一入口：[PROD V5 → V6 复盘与演进总述](../../18-prod-v5-v6-deployment-and-migration-retrospective.zh.md) · [跨代证据索引](../generation-deployment-evidence-index-20261025.zh.md) · [既有统一部署迁移流程](https://github.com/ai-workspace-services/.github/blob/main/docs/control-plane-deployment-and-migration.zh.md)。
> 本目录归档 2026-11-01 至 2026-11-03 期间完成的 V5 → V6 迁移、K3s 平台故障修复、数据迁移、DNS 切换及边缘 Agent 恢复的全量证据。

---

## 1. 归档原则与安全红线

根据 `system-db-three-role-security` 与最小权限只读核查规约，本套归档严格执行以下纪律：

1. **事实证据边界划分**：
   - **现场只读核验 (Live Auditor)**：使用独立受限 `auditor` 账号对 V6（`172.237.24.232`）执行零状态变更查询（`id=1001`, groups=1000, 专有 kubeconfig），严格禁止任何破坏性操作与提权。
   - **脱敏历史回执 (Receipts)**：V5 主机（`104.105.141.213`）因只读凭据连接超时，忠实标记 `BLOCKED：只读身份缺少 V5 SSH 现场连接证据`，严格遵循规约不尝试非法提权或绕过主机指纹校验，转用仓库已固化的时点脱敏回执。
   - **用户确认事实 (User Confirmed)**：针对 2026-11-03 用户明确回复的“US 已出现”，记录为“用户提供的登录态页面可见性验收”，明确区分于“服务端名单检查”与“真实代理流量”。
   - **绝不推断与编造**：未执行项目标记 `NOT_RUN`，受阻项标记 `BLOCKED`，禁止将 Pod Ready 或 PR 合并直接推断为业务通过。
2. **秘密绝不入库**：
   - 绝不打印或记录 kubeconfig、Token、DSN、密码、Raft unseal key、私钥、会话、代理 UUID、用户邮箱或原始账单明细。
3. **保护现有系统状态**：
   - 本次为复盘与文档归档任务，未进行重新部署、数据再迁移、DNS 切换或任何线上配置修改。

---

## 2. 归档文件索引

本目录包含以下 5 篇结构化文档：

| 文件名 | 类型 | 核心内容与作用 |
| :--- | :--- | :--- |
| [**baseline-and-timeline.zh.md**](baseline-and-timeline.zh.md) | 基线与全景时间线 | 记录 V5 vs V6 硬件规格、操作系统、K3s、网络 CIDR、存储挂载差异，以及 2026-11-01 至 2026-11-03 双时区关键事件时间线。 |
| [**evidence-and-pr-index.zh.md**](evidence-and-pr-index.zh.md) | 证据与不可变构件索引 | 跨仓库 PR 索引（GitOps、Playbooks、Accounts、Knowledge、Console）、提交 SHA、OCI 镜像 Digest、Schema 校验和及证据 ID 索引。 |
| [**root-cause-and-corrective-actions.zh.md**](root-cause-and-corrective-actions.zh.md) | 故障根因与纠正措施 | 详尽复盘 9 项关键故障（GHCR 403、Datakit OOM、ServiceLB pending、Caddy reload、Accounts 凭据覆盖、Custom 等级拒绝等），按 8 步规范分析。 |
| [**acceptance-and-todo-matrix.zh.md**](acceptance-and-todo-matrix.zh.md) | 验收与未决事项矩阵 | 23 项细粒度验收状态分类表（PASS / PARTIAL / BLOCKED / NOT_RUN），明确线上取证结论、用户确认边界及后续工程待办。 |
| [**migration-runbook.zh.md**](migration-runbook.zh.md) | 可复用代际迁移运行手册 | 提炼 7 阶段操作流程（前置准备、Vault 状态迁移、数据库迁移、服务调谐、DNS 切换、边缘恢复与回滚预案），供后续代际演进复用。 |

---

## 3. 代际演进核心指标概览 (2026-11-03 采样)

- **节点状态**：`prod-k3s-v6` Ready (control-plane,etcd v1.37.1+k3s1, Debian 13)。
- **核心工作负载**：
  - `web-saas-prod`：accounts (1/1), billing (1/1), console (1/1), content (1/1) 全 Ready，0 重启。
  - `ingress-prod`：caddy (1/1 Ready, 0 重启)；`kube-system`：svclb-caddy (1/1 Ready, 443 -> 8443)。
  - `observability-prod`：datakit (1/1 Ready, 内存限制 128/512Mi，持续稳定 22h+), observability-stack (5/5 Ready)。
  - `vault-prod`：vault-0 (1/1 Ready, Raft unsealed, post-unseal complete, 9 个 SecretStore JWT 认证通过)。
  - `postgresql-prod`：postgresql-0 (1/1 Ready, 单节点 StatefulSet, account 业务库, 100GB 独立挂载盘)。
- **数据时点指标 (2026-11-03)**：
  - 42 张业务表完整对齐，37 用户，7 订阅，13 订阅记录，92,143 账本，20 套餐，5 发票 / 5 付款 / 2 退款。
- **公共解析与入口**：
  - 7 个 canonical 域名（`xworktech.com`, `console.svc.plus`, `accounts.svc.plus`, `billing.svc.plus`, `vault.svc.plus`, `observability.svc.plus`, `postgresql.svc.plus`）已切换至 V6 IP `172.237.24.232`。
- **边缘 Agent 接入**：
  - JP 节点（12 客户端）持续同步；US 节点经 Accounts 支持 custom 等级更新后恢复（3 客户端同步，下发与白名单一致）。
