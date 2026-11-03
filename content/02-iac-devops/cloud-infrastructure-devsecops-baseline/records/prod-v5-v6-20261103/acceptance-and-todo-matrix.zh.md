# PROD V5 → V6 验收状态与未决事项矩阵

> 记录日期：2026-11-03，Asia/Shanghai。
> 统一入口：[PROD V5 → V6 复盘与演进总述](../../18-prod-v5-v6-deployment-and-migration-retrospective.zh.md) · [归档索引](README.md)。

---

## 1. 验收标准与状态定义

本矩阵遵循客观存证原则，严格区分以下 4 类事实边界：
- **PASS**：具备完整现场只读取证、脱敏回执或双向校验闭环证据，测试通过；
- **PARTIAL**：部分通过或存在边界限制（如预览通过但未二次写入、端口通但应用协议未连通）；
- **BLOCKED**：因只读身份权限边界、安全网络隔离或外部约束导致的取证受阻，忠实保留现状，绝不盲目提权；
- **NOT_RUN**：规划中但明确未在本轮执行的操作（如破坏性故障演练、WireGuard 即刻拔线等）。

---

## 2. 23 项细粒度验收矩阵清单

| 编号 | 检查领域与项目 | 验收状态 | 核心证据与观察值 | 证据来源与边界说明 |
| :---: | :--- | :---: | :--- | :--- |
| **01** | **V6 物理节点与 OS** | **PASS** | `prod-k3s-v6`，Debian 13 (`6.12.113+deb13-amd64`)，内存 4GB，根分区与 `/data` 正常挂载。 | 现场 `auditor` SSH 执行 `uname -a`, `df -h` 取证。 |
| **02** | **V6 独立存储卷** | **PASS** | 100GB 块存储挂载至 `/data`，local-path 根目录配置为 `/data/k3s-storage`，挂载状态稳定。 | 现场 `auditor` 查询 mount 与 storageclass。 |
| **03** | **K3s 集群控制面** | **PASS** | K3s `v1.37.1+k3s1` 单节点，状态 `Ready,control-plane,etcd`，组件 0 重启。 | 现场 `auditor` 执行 `kubectl get nodes -o wide`。 |
| **04** | **网段划分与 CoreDNS** | **PASS** | Pod CIDR `10.52.0.0/16`（节点分配 `10.52.0.0/24`），Service `10.53.0.0/16`，CoreDNS `10.53.0.10` 正常解析。 | 现场网络自省：集群 `/16` 与节点 `/24` 边界清晰。 |
| **05** | **WireGuard 迁移隧道** | **PASS** | 接口 `v5v6` (`10.254.250.2/30`) 状态 UP，静态路由 `10.42.0.0/16 dev v5v6` 生效，握手持续。 | 现场 `ip addr`、`ip route`；作为迁移期依赖运行。 |
| **06** | **ServiceLB 与公网入口** | **PASS** | `svclb-caddy` DaemonSet 正常绑定宿主机 443，LoadBalancer 获取 External-IP `172.237.24.232`。 | 现场 `kubectl get svc -n ingress-prod` 取证。 |
| **07** | **Caddy Ingress 网关** | **PASS** | Caddy Pod `1/1 Running`，Let's Encrypt 证书有效，各子域名 HTTPS 探测均 HTTP 200、TLS 握手成功。 | 现场取证与公共 DoH 拨测。 |
| **08** | **Vault Raft 恢复与解封** | **PASS** | Raft 快照恢复完成（Index 315185），`post-unseal setup complete`，`initialized=true, sealed=false`，Pod 0 重启。 | 历史 API 204 回执与 Pod 日志存证。 |
| **09** | **Vault 工作负载契约** | **PASS** | 9 个 SecretStore 基于 SA TokenRequest 的 JWT 认证 100% 成功，抽查 8 个关键 KV 摘要完全一致。 | 跨命名空间 ExternalSecret 状态 `SecretSynced`。 |
| **10** | **PostgreSQL 数据持久化**| **PASS** | 单节点 StatefulSet `postgresql-0` (`1/1 Running`)，挂载 `/data` 持久卷，`account` 业务库健康。 | 现场 Pod 状态与持久卷 Binding 检查。 |
| **11** | **业务数据单向初次同步** | **PASS** | `migratectl transfer-api` 导入 42 表；客户端超时后重试返回 `state=applied` 事务提交；37 用户、7 订阅、92143 账本。 | 历史操作端脱敏回执与目标端表记录核对。 |
| **12** | **业务数据增量追齐预览** | **PARTIAL**| `catchup-api` 预览通过，42 表主数据无冲突，记录 1 条源变更与 30 条目标自举变更；**未执行二次 apply**。 | 保留追齐缺口，不宣称实时逐行绝对一致。 |
| **13** | **Console 前端服务** | **PASS** | Console Pod `1/1 Running`，`/healthz` 匹配固定构件，环境变量显式指向 V6 Accounts ClusterIP。 | 现场 Pod 取证及 HTTP 探针。 |
| **14** | **Accounts 核心服务** | **PASS** | Pod `1/1 Running`，模板已移除伪凭据，合入 `custom` 等级代码，`/api/ping` 返回提交与 digest 一致。 | 现场 Pod 状态、GitOps #771/#772 合并凭据。 |
| **15** | **Billing 计费服务** | **PASS** | Billing Pod `1/1 Running`，`/readyz` HTTP 200，支持 Vector push 数据采集链路。 | 现场 Pod 状态与健康探针。 |
| **16** | **Content 内容服务** | **PASS** | Content Pod `1/1 Running`，`/healthz` HTTP 200，`xworktech.com` 主页内容渲染正常。 | 现场 Pod 状态与公网 HTTP 200。 |
| **17** | **Datakit 观测稳定性** | **PASS** | Datakit Pod `1/1 Running`，配额升至 128/512Mi 后连续运行 **22 小时+** 无 OOMKilled，0 重启。 | 现场 `kubectl get pods -n observability-prod`。 |
| **18** | **canonical DNS 切换** | **PASS** | 7 个 canonical 域名在 Cloudflare API 完成 A/CNAME 指向 V6，公共解析器（1.1.1.1/8.8.8.8）生效。 | 权威 API 回读与公共 DNS 查询存证。 |
| **19** | **JP 边缘节点同步** | **PASS** | JP Agent 鉴权恢复，心跳在线，持续同步 12 个客户端，Xray 同步状态正常。 | 现场心跳时间戳与客户端列表核对。 |
| **20** | **US 边缘节点注册** | **PASS** | US 节点 scope 识别为 `custom`，白名单下发 3 个客户端，下发列表严格匹配三人名单。 | 现场心跳时间戳与名单匹配比对。 |
| **21** | **用户界面可见性验收** | **PASS** | 2026-11-03 名单内账号刷新页面后，用户明确回复“US 已出现”。 | **标为用户提供的登录态验收**，不推断端到端流量。 |
| **22** | **V5 实例删除锁解除** | **PASS** | 经明确授权调用 Linode CLI 解除 V5 保护锁，回读确认实例仍处于 `running` 状态。 | 受控回执存证；V6 `cannot_delete` 锁保持激活。 |
| **23** | **PostgreSQL 公网协议访问**| **PARTIAL**| 公网 DNS `postgresql.svc.plus` 解析已切至 V6；TCP connect 成功，但原生 `pg_isready` 探测不响应。 | **未决事项**：内部为 ClusterIP，公网协议未验收。 |

---

## 3. 阻塞项与未决待办清单 (Open Items & Blockers)

根据 DevSecOps 安全基线要求，下列项目必须保持明确的开放状态并纳入后续工程跟踪：

1. **`BLOCKED：只读身份缺少 V5 SSH 现场连接证据`**：
   - 现状：在 2026-11-03 取证期间，使用 `auditor@104.105.141.213` 发起的 SSH 连接均返回连接超时；
   - 处置准则：严格遵循规约，不尝试高权限身份，不关闭主机 HostKey 检查，忠实记录为阻断，转用仓库已有脱敏回执。
2. **`postgresql.svc.plus` 原生公网访问未决**：
   - 现状：外部 TCP 连接探测端口开放（可能来自宿主机网关或重定向），但原生 PostgreSQL 握手探针 `pg_isready` 无响应；
   - 边界：K3s 内部 PostgreSQL 为 ClusterIP 模式，禁止将 DNS 切换与 TCP 握手简单表述为公网数据库服务已验收通过。后续若需开放必须走双向 mTLS 隧道或受控网关。
3. **`auditor` 账号 RBAC 权限过度暴露待收敛**：
   - 现状：现场 RBAC 自省显示 `kubectl auth can-i get secrets -A` 返回 `yes`；
   - 待办：违反最小权限原则，后续应调整 ClusterRole，收回 `auditor` 对 Secret 资源的读取权限，仅保留非敏感资源（Pod, Service, Node, Ingress）的只读盘点权限。
4. **WireGuard 迁移依赖通道安全下线**：
   - 现状：`v5v6` 隧道当前仍在承载可能的跨代依赖，不能随意切断；
   - 待办：在彻底确认二次追齐无需求、所有依赖解除后，按 Runbook 执行路由下发撤回与网卡注销。
5. **共享服务 Token 轮换与清理**：
   - 现状：历史操作中曾涉及共享内部服务 Token；
   - 待办：制定消费者平滑轮换清单，逐步迁移至基于 Vault AppRole / SA Token 的动态鉴权机制，避免单点泄露风险。
6. **V5 云资源最终退役与实例销毁**：
   - 现状：仅解除了删除保护锁，实例仍在运行；
   - 待办：待业务平稳运行 14 天观察期满且全量离线冷备归档后，发起独立的退役注销流程。
