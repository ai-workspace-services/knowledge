# PROD V5 → V6 基线参数、网络拓扑与全景时间线

> 记录日期：2026-11-03，Asia/Shanghai。
> 统一入口：[PROD V5 → V6 复盘与演进总述](../../18-prod-v5-v6-deployment-and-migration-retrospective.zh.md) · [归档索引](README.md)。

---

## 1. V5 vs V6 基础运行基线对比

下表对比本次迁移的源端（V5 K3s）与目标端（V6 K3s）真实环境配置。早期 V5 单机 VPS Compose（2026-10-23）仅为历史过渡形态，不与本次源端混淆。

| 参数维度 | PROD-K3S-V5 (迁移源端) | PROD-K3S-V6 (目标生产) | 说明与审计核验结论 |
| :--- | :--- | :--- | :--- |
| **云提供商与规格** | Akamai Cloud (Linode) 2C4G | Akamai Cloud (Linode) `g6-standard-2` 2C4G | 均为 2 vCPU / 4 GB 内存规格 |
| **公网入口 IP** | `104.105.141.213` | `172.237.24.232` | 2026-11-03 DNS 已完全指向 V6 |
| **操作系统与内核** | Debian 12 (bookworm), Linux 6.1.x | Debian 13 (trixie), `Linux prod-k3s-v6 6.12.113+deb13-amd64` | V6 经 auditor SSH 现场取证核实 |
| **持久化存储架构** | 根文件系统 local-path (50GB 混用) | 独立 100GB 块存储挂载至 `/data` (`/dev/disk/by-id/linode-v6-data`) | V6 将 `/data/k3s-storage` 作为 local-path 根目录 |
| **K3s 控制面版本** | v1.31 系列 | `v1.37.1+k3s1` (`prod-k3s-v6 Ready control-plane,etcd`) | Kubernetes 核心组件与安全能力演进 |
| **集群 Pod CIDR** | `10.42.0.0/16` | `10.52.0.0/16` | **禁止混淆**：集群范围为 `/16` |
| **节点 Pod CIDR** | `10.42.0.0/24` (eth0/cni0) | `10.52.0.0/24` (`cni0` 接口分发) | 节点具体分配为 `/24` |
| **集群 Service CIDR** | `10.43.0.0/16` | `10.53.0.0/16` | 两代服务网段完全隔离，防冲突 |
| **CoreDNS ClusterIP**| `10.43.0.10` | `10.53.0.10` | DNS 服务内部固定虚拟地址 |
| **WireGuard 隧道** | `10.254.250.1/30` (`dev v5v6`) | `10.254.250.2/30` (`dev v5v6` UP) | 点对点加密传输通道，支持 Pod 路由互通 |
| **生命周期锁保护** | `cannot_delete_with_subresources`（已解除） | `cannot_delete`（当前有效生效中） | 2026-11-03 经授权解锁 V5，V6 锁受保护 |
| **线上只读核验状态** | `BLOCKED：只读身份缺少 V5 SSH 现场连接证据` | `PASS：auditor 专有凭据取证完成` | V5 审计连接超时，依规转用脱敏历史回执 |

---

## 2. 网络规划、WireGuard 隧道与独立运行条件

### 2.1 网段设计与接口自省

现场通过 `auditor` 身份执行 `ip addr` 与 `ip route` 取证核实：
1. **集群 CIDR 与节点 CIDR 区分**：
   - V6 集群声明的 Pod CIDR 为 `10.52.0.0/16`，由 Flannel 在单节点分配子网 `10.52.0.0/24` 给网桥接口 `cni0`。
   - Service CIDR 为 `10.53.0.0/16`，Kube-DNS ClusterIP 为 `10.53.0.10`。
2. **WireGuard 隧道接口与路由**：
   - 接口名：`v5v6`，IP 配置为 `10.254.250.2/30`。
   - 静态路由表项：`10.42.0.0/16 dev v5v6 scope link`。该路由使得 V6 节点及 Pod 能够直接将对端 V5 Pod 网段流量导入 WireGuard 隧道。
   - 对端 V5 配置有对等路由：`10.52.0.0/16 dev v5v6`。

### 2.2 WireGuard 隧道的作用边界与独立运行撤除条件

- **当前角色（迁移期依赖）**：
  - WireGuard 隧道仅在迁移窗口作为安全管理与数据通道使用（如 `accounts-migration-listener` 接收抽取数据、跨集群 Vault 内部管理交互、内部验证等）。
  - **重要约束**：本复盘任务严格只读，**严禁在本次任务中主动断开或操作隧道**。
- **撤除 WireGuard 达到完全独立运行的前提条件**：
  1. **所有 canonical 外部域名与服务**（Web-SaaS、Vault、Grafana、Agent Registry）均稳定直连 V6，且无跨集群内网 DNS 解析依赖；
  2. **Accounts 迁移监听器已下线**：确认无需再执行任何二次增量追齐 (`catchup-api`)，下线 `accounts-migration` 命名空间；
  3. **数据写入方单一性核验**：确认 V5 业务实例完全停用，所有 Agent（JP、US 等）心跳与请求 100% 直达 V6；
  4. **Vault 依赖解耦**：确认 V6 Vault 完全独立自持，无跨节点 Raft 状态交互；
  5. **下线操作**：经明确授权后，按标准 Runbook 移除静态路由 `10.42.0.0/16`，停用并删除 `v5v6` 虚拟网卡，安全回收对端公网白名单。

---

## 3. 全景执行时间线 (2026-11-01 至 2026-11-03)

本时间线严格按 **Asia/Shanghai (UTC+8)** 与 **UTC** 双时区对照记录。

```
[2026-11-01] 节点与底层网络初始化 (Linode g6-standard-2 / Debian 13 / WireGuard)
     │
[2026-11-02] K3s 冷启动与首轮故障处置 (GHCR 403 / Datakit OOM / ServiceLB / Nginx)
     │
[2026-11-03 00:24-08:26] Vault 状态迁移 (Raft Snapshot HTTPS 流传输与恢复验证)
     │
[2026-11-03 01:43-09:30] 业务数据迁移 (Accounts 42 表加密传输、冲突处置与事务提交)
     │
[2026-11-03 09:30-10:15] canonical DNS 切换 (Cloudflare API 更新 7 域名)
     │
[2026-11-03 10:15-11:45] 边缘 Agent 与 Ingress 修复 (JP 401 模板修复 / US Custom 等级恢复)
     │
[2026-11-03 11:45+]      用户登录态验收 ("US 已出现") 与 V5 删除保护锁安全解除
```

### 详细事件记录表

| Asia/Shanghai (UTC+8) | UTC 时间 | 阶段与主题 | 关键操作与证据 | 状态 / 退出码 |
| :--- | :--- | :--- | :--- | :--- |
| **2026-11-01 14:00:00** | 2026-11-01 06:00:00 | **节点拉起与存储** | 创建 Linode `g6-standard-2` 实例与 100GB `/data` 卷，系统装载 Debian 13。格式化并挂载至 `/data`。 | PASS / exit 0 |
| **2026-11-01 16:30:00** | 2026-11-01 08:30:00 | **主机安全与身份** | 执行 Playbooks 初始化主机内核参数，创建 `admin`、`operator`、`auditor` 三类操作系统身份，配置最小权限 sudo。 | PASS / exit 0 |
| **2026-11-01 18:00:00** | 2026-11-01 10:00:00 | **P2P 网络互联** | 配置 V5-V6 WireGuard 隧道（`v5v6`），绑定 `10.254.250.2/30`，注入对端 Pod CIDR 路由 `10.42.0.0/16`。握手正常。 | PASS / exit 0 |
| **2026-11-01 21:00:00** | 2026-11-01 13:00:00 | **K3s 集群冷启动** | 安装 K3s `v1.37.1+k3s1`，指定 Pod CIDR `10.52.0.0/16`、Service CIDR `10.53.0.0/16`、数据目录 `/data/k3s-storage`。 | PASS / exit 0 |
| **2026-11-02 02:15:00** | 2026-11-01 18:15:00 | **GitOps & 镜像故障** | Flux v2 部署应用，GHCR 私有镜像拉取报 403。紧急将 `services/` 镜像源指向公开构件包并锁定 digest。 | PASS (PR #743) |
| **2026-11-02 04:30:00** | 2026-11-01 20:30:00 | **ServiceLB 调度受阻**| K3s 默认配置禁用了 ServiceLB，导致 Caddy LoadBalancer 处于 pending。修正配置恢复 ServiceLB DaemonSet。 | PASS (GitOps #744, PB #958) |
| **2026-11-02 08:00:00** | 2026-11-02 00:00:00 | **Datakit 调谐与 OOM** | Datakit 因内存上限 128Mi 频繁 OOMKilled，且 SecretStore 缺少 Vault 映射。补齐 Secret 映射并调优配额至 128/512Mi。 | PASS (GitOps #746, #750) |
| **2026-11-02 11:30:00** | 2026-11-02 03:30:00 | **Console Nginx 权限**| Console 镜像内置 Nginx 试图写非特权无权访问的 `/var/cache/nginx` 报 500。重构非 root 运行目录配置。 | PASS (PR #747) |
| **2026-11-02 15:45:00** | 2026-11-02 07:45:00 | **数据库初始化与网络**| 部署 PostgreSQL 单节点 StatefulSet；初始化 `account` 业务库、角色契约，配置 ClusterIP 网络访问策略。 | PASS / exit 0 |
| **2026-11-02 19:20:00** | 2026-11-02 11:20:00 | **网关与证书就绪** | 部署 Caddy Ingress，配置各子域名路由规则。配置 Let's Encrypt 证书申请链路，验证内部 ClusterIP 连通性。 | PASS / exit 0 |
| **2026-11-03 00:24:14** | 2026-11-02 16:24:14 | **Vault 前置快照存证**| 比较两端 KV 路径（V5 153 vs V6 146）；导出 `v5-source.snap` (SHA: `df27a644...`) 与 V6 回退快照 `v6-before.snap` (SHA: `a2271c96...`)。 | PASS / exit 0 |
| **2026-11-03 00:45:00** | 2026-11-02 16:45:00 | **Vault 快照流式导入**| 内存 HTTPS 流上传 `v5-source.snap` 至 V6，调用 `POST /v1/sys/storage/raft/snapshot`，API 返回 204 accepted。 | PASS / HTTP 204 |
| **2026-11-03 08:26:00** | 2026-11-03 00:26:00 | **Vault 状态完全收敛**| V6 Vault 日志确认 `post-unseal setup complete`，unsealed，Pod 0 重启。抽查 8 个关键 KV 摘要一致；9 个 SecretStore JWT 认证成功。 | PASS / exit 0 |
| **2026-11-03 01:43:52** | 2026-11-02 17:43:52 | **数据库迁移前置备份**| 取得 V6 `account` 库前置 pg_dump 并加密存证，SHA256: `11b00a96...`，验证受限目录可读。保留回退点。 | PASS / exit 0 |
| **2026-11-03 04:10:00** | 2026-11-02 20:10:00 | **业务数据单向同步** | 停止目标写者，经授权丢弃测试数据，通过 `migratectl transfer-api` 导入 42 表；客户端虽超时但事务完整提交。重跑幂等。 | PASS (state=applied) |
| **2026-11-03 08:45:00** | 2026-11-03 00:45:00 | **增量变更追齐预览** | 执行 `catchup-api` 预览，42 表主数据无冲突，捕获 1 条源变更与 30 条目标自举变更。未执行二次写入，保留缺口。 | PASS / exit 0 (Preview) |
| **2026-11-03 09:30:00** | 2026-11-03 01:30:00 | **canonical DNS 切换**| Cloudflare API 更新 7 个域名记录指向 V6。公共 DNS（1.1.1.1 / 8.8.8.8）生效。记录前置回退映射。 | PASS / exit 0 |
| **2026-11-03 10:15:00** | 2026-11-03 02:15:00 | **JP Agent 401 故障处置**| 发现模板内置示例凭据覆盖环境变量，紧急清除模板凭据列表，更新 Vault KV v2 v6->v7，同步 Secret 并滚动 Accounts。 | PASS (GitOps #771) |
| **2026-11-03 10:45:00** | 2026-11-03 02:45:00 | **Console 404 路由修正**| Console 请求 `/api/admin/agents/team-enrollments` 返回纯文本 404。Caddy 添加精确重写规则并执行 reload。 | PASS / HTTP 401 (Auth) |
| **2026-11-03 11:10:00** | 2026-11-03 03:10:00 | **US Agent 400 故障处置**| Accounts 升级支持 custom 资源等级与 free 策略；Console 显式注入 V6 Accounts ClusterIP 地址。 | PASS (GitOps #772, #773) |
| **2026-11-03 11:35:00** | 2026-11-03 03:35:00 | **用户界面验收确认** | 用户登录 Console 页面刷新核实，明确回复确认“US 已出现”。确认为用户提供的登录态页面可见性验收。 | PASS (User Confirmed) |
| **2026-11-03 11:42:00** | 2026-11-03 03:42:00 | **V5 删除保护锁安全解锁**| 经用户明确授权，使用 Linode CLI 解除 `web-saas-k3s-v5` 实例保护锁；回读确认实例仍为 `running`，V6 锁保持。 | PASS / exit 0 |
