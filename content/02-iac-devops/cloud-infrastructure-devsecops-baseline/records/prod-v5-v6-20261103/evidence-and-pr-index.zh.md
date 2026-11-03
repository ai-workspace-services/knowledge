# PROD V5 → V6 证据索引、跨仓 PR 与不可变构件清单

> 记录日期：2026-11-03，Asia/Shanghai。
> 统一入口：[PROD V5 → V6 复盘与演进总述](../../18-prod-v5-v6-deployment-and-migration-retrospective.zh.md) · [归档索引](README.md)。

---

## 1. 跨仓库 PR 索引与提交追踪

本代际演进与修复涉及 5 个核心仓库（`gitops`、`playbooks`、`accounts`、`knowledge`、`portal/console`）。所有线上生效配置均已通过 PR 合入主分支并由 Flux/Ansible 自动调谐收敛，消除了任何脱离代码库的未受控临时修改。

### 1.1 GitOps 仓库 (`ai-workspace-infra/gitops`)

| PR 编号 | 核心提交 SHA | 变更内容与目的 | 线上生效与调谐状态 |
| :--- | :--- | :--- | :--- |
| **#743** | `3f8a12e5` | 修复私有 GHCR 镜像 403 阻断，将应用镜像引用切换为公开包路径并固定 digest | Flux Reconciled, Pods Ready |
| **#744** | `7d10b429` | 修复 K3s 默认配置禁用 ServiceLB 导致 Ingress 无法获取 External-IP 的缺陷 | Ingress LB IP 获取成功 (172.237.24.232) |
| **#745** | `a90c431b` | 补全 Caddy Ingress 跨子域路由定义与 ExternalSecret 同步声明 | Caddy ConfigMap Synced |
| **#746** | `c128e674` | 建立 Datakit 观测栈的 SecretStore 声明及 Vault KV 路径字段映射 | ExternalSecret Synced |
| **#747** | `e45b8901` | 修复 Console 容器内部 Nginx 缓存目录特权限制导致的前端 500 异常 | Console Pod Ready, HTTP 200 |
| **#750** | `b891d45a` | 调优 Datakit 容器资源限制（Memory Request 128Mi / Limit 512Mi），根治 OOMKilled | Datakit 稳定运行 22h+ 无重启 |
| **#751-#770** | 见 Git 记录 | 数据库 NetworkPolicy 约束、内部 CoreDNS 服务发现与 HelmRelease 依赖锁紧 | 全部由 Flux 声明式收敛 |
| **#771** | `69afa51a` | 剔除 Accounts 控制器模板内置的示例凭据，防止环境变量注入 Token 被静默覆盖导致 JP 401 | JP Agent 鉴权恢复，12 客户端恢复 |
| **#772** | `bc32fac4` | 引入 Accounts 单节点 `custom` 资源等级与 `customAllowFree` 授权逻辑 | US Agent 注册恢复，HTTP 200 |
| **#773** | `32695533` | Console 明确指定 V6 Accounts ClusterIP 认证地址，避免沿用 Cloud Run 默认地址 | Console /healthz 匹配固定构件 |

### 1.2 Playbooks 仓库 (`ai-workspace-infra/playbooks`)

| PR 编号 | 涉及 Role / 文件 | 核心变更目的 | 验证与执行结果 |
| :--- | :--- | :--- | :--- |
| **#956** | `roles/host_bootstrap` | Debian 13 内核参数调优、系统依赖安装、OS 三类身份（admin/operator/auditor）初始化与受控 sudo 配置 | 主机安全合规校验 PASS |
| **#957** | `roles/wireguard_tunnel` | 建立 V5 (`10.254.250.1/30`) 与 V6 (`10.254.250.2/30`) P2P 隧道，配置 Pod CIDR 路由 | 隧道握手成功，内网互通 |
| **#958** | `roles/k3s_install` | 安装 K3s `v1.37.1+k3s1`，确保 `--no-deploy servicelb` 未被误配，设置 `/data/k3s-storage` | K3s 集群自检 Ready |
| **#959** | `roles/storage_data` | 100GB 独立云磁盘格式化（ext4）、挂载 `/data` 与 fstab 持久化配置 | 磁盘挂载状态核验 PASS |
| **#960** | `roles/db_baseline` | PostgreSQL 数据库初始化、`db_readonly` 角色授予及 auditor 只读视图绑定 | 审计只读自省 PASS |
| **#961** | `roles/vault_bootstrap` | Vault Raft 集群配置、通用 SA TokenRequest JWT Auth 契约与 AppRole 注入 | JWT 跨命名空间校验 PASS |
| **#962** | `roles/monitoring_agent` | Datakit 守护进程安装与日志、指标采集通道配置 | 观测流上报链路通畅 |

### 1.3 Accounts 仓库 (`ai-workspace-services/accounts`)

| PR 编号 | 模块 / Commit | 功能描述与迁移支持 | 验证方式 |
| :--- | :--- | :--- | :--- |
| **#289** | `internal/migrate/listener` | 实现专有数据迁移监听器，替代宽权限直连 DSN | Listener Pod 启动并通过鉴权 |
| **#291** | `cmd/migratectl` | 构建 `migratectl transfer-api` 与 `catchup-api` 客户端工具 | CLI 本地单元测试与端到端模拟 |
| **#292** | `internal/schema/v1` | 严格固化 `identity-billing-v1` 42 张业务表的数据契约与结构校验 | Schema 校验一致 |
| **#294** | `internal/migrate/plan` | 增加迁移前置冲突预览、目标写入白名单与 409 阻断保护 | 冲突检测逻辑覆盖测试 |
| **#296** | `internal/crypto` | 实现数据传输零落盘内存加密与受限目录临时加密暂存 | 密文解密完整性测试通过 |
| **#297** | `internal/migrate/writer` | 支持迁移期间优雅暂停目标端后台写者，防止数据脏写 | 目标写者锁状态回读验证 |
| **#298** | `internal/migrate/tx` | 实现全量写入单事务边界与超时幂等二次执行支持 | 超时幂等测试（state=applied） |
| **#300-#304** | `internal/agent` | 支持 Agent 单节点模式下的 `custom` 资源等级与免费白名单判定 | 单元测试与注册回归测试通过 |
| **#305** | `internal/api/admin` | 修复 `/api/auth/admin/agents/team-enrollments` 路径的响应契约 | Console 接口转发测试通过 |

### 1.4 Knowledge 仓库 (`ai-workspace-services/knowledge`)

- **#343**：K3s V6 架构设计与单节点冷启动交付规范。
- **#344**：通用 Vault 工作负载身份契约（外部 Vault、ESO、ServiceAccount TokenRequest）。
- **#345**：Accounts 迁移 API 单向同步规范与安全防护红线。
- **#346**：PROD K3s V6 用户迁移操作手册与回退预案。
- **#347**：ServiceLB、Caddy 与 Datakit 专项修复提示词与排障手册。
- **#348**：PROD K3s V6 规划与部署状态全量历史归档。

---

## 2. 不可变构件清单 (Immutable Artifacts)

以下构件构成了 2026-11-03 迁移与部署的精确物料清单。所有镜像均采用不可变 digest 固化，严禁在生产中使用浮动 tag（如 `latest`）。

| 构件名称 / 服务 | 固定来源提交 (Commit SHA) | OCI 镜像 Digest / 构件校验和 (SHA-256) | 部署位置 / Namespace |
| :--- | :--- | :--- | :--- |
| **Accounts** | `bc32fac4846cea5281e9e764c5224a581dff1ed1` | `sha256:f57e46a2624f554b92bd4983aede203c5cfcb0d2b83f3be33836cc715ec6eed4` | `web-saas-prod/accounts` |
| **Console** | `32695533eeb39f1af351cc3b4876aa9d23150c62` | `sha256:5ee55a96a8184074ea4186cf38b426a0d368b686866afc345d2991b0eb02e8b9` | `web-saas-prod/console` |
| **Billing** | `a17b89e4c19203941a87b64082dc590a3b2b8109` | `sha256:92cb1f57138b55694c92bfae4c9f116a443a7da9d80d285098ffb8f6451a89c2` | `web-saas-prod/billing` |
| **Content** | `0d8923a17e0b5c19266a4f9b8c081e7d41f71a93` | `sha256:4b9181fa83f81e32d56c072c4e1a7b88939c086435c24e83c2718e285a8efb48` | `web-saas-prod/content` |
| **Caddy Ingress** | N/A (Official upstream) | `caddy:2.8.4-alpine` / `sha256:9234b6b1424...` | `ingress-prod/caddy` |
| **Vault Server** | HashiCorp v1.21.4 | `hashicorp/vault:1.21.4` (Raft engine) | `vault-prod/vault-0` |
| **Datakit Agent** | Guance 1.34.0 | `pubrepo.guance.com/datakit/datakit:1.34.0` | `observability-prod/datakit` |
| **K3s 运行时** | Rancher v1.37.1+k3s1 | Release v1.37.1+k3s1 | 宿主机节点 |

### 快照与备份不可变存证表

| 快照文件 / 存证标识 | 产生时间 (Asia/Shanghai) | SHA-256 校验和 | 属性 / Inspect 结论 | 存放路径 / 介质 |
| :--- | :--- | :--- | :--- | :--- |
| **`v5-source.snap`** | 2026-11-03 00:24:14 | `df27a6449d1d9d1e35dddc99fccf2643dc9222beee9e6424d040ab9df4ea1087` | Raft Inspect Index: **315185** | 操作端受控备份目录 (`0600`) |
| **`v6-before.snap`** | 2026-11-03 00:24:14 | `a2271c962e979b9aab97b571c8c6aa0765413884032b6cd5e02af88cf200cf32` | Raft Inspect Index: **266759** | 操作端受控备份目录 (`0600`) |
| **`v6-pre-import-...`** | 2026-11-03 01:43:52 | `11b00a96cfd9d0a8606c9ea496283e2d921a4404f7b4abda0b0a190add49f0af` | PostgreSQL 密文 dump，已验目录可读 | `accounts-migration/backups/` |

---

## 3. 证据分类与核验边界

本复盘文档对所有事实证据进行严格的等级与来源标注，拒绝混淆：

1. **现场只读核验 (Live Auditor)**：
   - 现场通过 `auditor@172.237.24.232` 及专用 kubeconfig 执行非提权查询。
   - 验证内容：Pod 运行状态（全部 1/1 Running，0 重启）、网络接口（`v5v6`、`cni0`）、路由表项（`10.42.0.0/16 dev v5v6`）、ServiceLB 外部 IP 分配（`172.237.24.232`）、RBAC 自省结论（无 exec、无 pod 增删权、禁止签发 Token）。
2. **脱敏历史回执 (Receipts)**：
   - 包含快照导出记录、Vault HTTPS 流导入 204 返回、PostgreSQL 迁移事务提交回执、Cloudflare API DNS 更新回执。
   - 忠实记录受阻状态：V5 SSH 只读连接因超时标记为 `BLOCKED`，严格依规转用归档历史数据。
3. **用户确认事实 (User Confirmed)**：
   - 针对 2026-11-03 名单内账号刷新后，用户明确反馈“US 已出现”，记录为“用户提供的登录态页面可见性验收”，不替代端到端真实代理流量拨测与完整计费周期回归。
4. **明确未决事项 (Open Items)**：
   - `postgresql.svc.plus` 原生 5432 协议公网探测未响应（保持未决，不标为公网验收通过）；
   - WireGuard 隧道仍存续（作为迁移过渡期依赖保留，待彻底解耦后按 Runbook 撤除）；
   - `auditor` 账号对 Secret 具备过多 get/list 权限待收敛。
