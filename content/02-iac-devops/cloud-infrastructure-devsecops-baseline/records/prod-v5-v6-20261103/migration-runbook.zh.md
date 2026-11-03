# 控制面代际迁移与 K3s 部署标准化运行手册 (Runbook)

> 记录日期：2026-11-03，Asia/Shanghai。
> 统一入口：[PROD V5 → V6 复盘与演进总述](../../18-prod-v5-v6-deployment-and-migration-retrospective.zh.md) · [归档索引](README.md)。

---

## 1. 运行规约与安全红线

本运行手册提炼自 V5 → V6 迁移实战经验，为下一次控制面代际演进提供可复用、标准化的工程指引。执行过程必须严格遵循以下安全红线：

1. **零状态变更审计先行**：
   - 线上巡检使用独立的 `auditor` 账号，禁止使用 root/operator 或通用 sudo 执行盘点；
   - 数据库仅使用 `db_readonly` 角色及受控视图，严禁直接使用业务写角色或 postgres 超级账号。
2. **秘密信息不落盘、不进日志**：
   - 所有 Token、DSN、密码、Unseal Key 仅在操作端受控进程内存中传递，严禁写入 Shell 脚本、Git 提交或日志文件；
   - 受控备份目录权限必须设定为 `0700`，备份与快照文件权限设定为 `0600`。
3. **单向数据晋级与防脏写**：
   - 迁移方向永远为“源端（只读）→ 目标端（候选写入）”，严禁双向混合写入；
   - 目标端执行数据注入前，必须**停用目标端所有后台写者**并取得前置加密快照。
4. **不可变构件与版本锁定**：
   - 禁止在部署声明中使用 `latest` 等浮动标签，全部依赖不可变 Git Commit SHA 与 OCI 镜像 Digest。

---

## 2. 7 阶段标准迁移流程

### 阶段 1：前置准备与基线冻结

1. **环境连通性与权限核验**：
   - 验证源端与目标端 `auditor` 账号连通性与 sudo 限制；
   - 创建本地受控操作目录，设定受限权限：
     ```bash
     mkdir -p ~/.local/share/generation-migration/backups/
     chmod 0700 ~/.local/share/generation-migration/backups/
     ```
2. **数据契约与 Schema 锁定**：
   - 确认待迁移数据表清单（如 `identity-billing-v1` 42 表），核验源库 Schema 版本，确保 `dirty=false`；
   - 生成数据源校验指纹，冻结源端任何 DDL 变更。

---

### 阶段 2：宿主机初始化与 K3s 集群拉起

1. **独立存储挂载**：
   - 确保独立的持久化云盘已格式化并挂载至 `/data`；
   - 配置 `/etc/fstab` 确保开机自动持久化挂载，将 local-path 根路径配置于 `/data/k3s-storage`。
2. **操作系统三类身份初始化**：
   - 执行 Playbook `roles/host_bootstrap`，初始化 `admin`、`operator`、`auditor` 三类账号及最小权限 sudoers。
3. **K3s 规范参数安装**：
   - 明确网段规划，避免与源端重叠：
     - Pod CIDR：`10.X.0.0/16`（节点分配 `/24` 给 `cni0`）
     - Service CIDR：`10.Y.0.0/16`
     - CoreDNS：`10.Y.0.10`
   - **关键避坑**：确保 K3s 配置文件中**未禁用** ServiceLB，保留内置 LoadBalancer 控制器能力。
4. **P2P 迁移隧道建立**：
   - 配置临时 WireGuard 点对点加密隧道，互通 Pod CIDR 静态路由，打通跨集群内网通信链路。

---

### 阶段 3：Vault 状态全量迁移与身份契约校验

1. **源端快照导出与前置检查**：
   - 通过 HTTPS API 导出源端 Raft 快照并存入受限目录：
     ```bash
     VAULT_ADDR=https://vault.source.domain vault operator raft snapshot save source-latest.snap
     vault operator raft snapshot inspect source-latest.snap
     shasum -a 256 source-latest.snap
     ```
2. **目标端前置回退快照留存**：
   - 导入前必须留存目标端快照 `target-before.snap`，作为失败回退基准。
3. **流式上传与异步恢复**：
   - 通过内存流将源快照上传至目标端 Raft 接口，发起 `POST /v1/sys/storage/raft/snapshot`；
   - 接收 HTTP 204 后，持续观察目标端 Vault 日志，直至出现：
     `post-unseal setup complete`
   - 核验 Vault 状态：`initialized=true, sealed=false`，Pod 0 重启。
4. **工作负载身份契约核验**：
   - 验证目标端集群 ServiceAccount TokenRequest 与 Vault JWT Auth 的互信；
   - 检查 ExternalSecret 控制器跨命名空间读取 8 个以上核心 KV 路径，确保状态均为 `SecretSynced`。

---

### 阶段 4：PostgreSQL 数据单向迁移与事务一致性保障

1. **部署专用迁移监听器**：
   - 在目标端拉起 `accounts-migration-listener`，通过安全 Token 接受内网迁移指令。
2. **目标端前置加密备份与隔离恢复演练**：
   - 执行前置 `pg_dump`，内存流加密存证至受控备份目录；
   - 在独立临时数据库中演练解密与恢复，验证备份有效性。
3. **空候选库预览与冲突决策**：
   - 运行 `migratectl transfer-api --preview`；
   - 若检测到测试数据冲突，必须在获得用户书面授权后，由操作者明确传入冲突覆盖指令（`--overwrite-test-data`）。
4. **停止业务写者与单事务注入**：
   - 暂停目标端所有可能产生脏写的工作负载后台任务；
   - 运行 `migratectl transfer-api --apply` 执行 42 张表单向写入；
   - **超时防护**：若因网络或大量账本导致客户端 HTTP 响应超时，严禁重复强制重跑，须先查询目标端状态回执；当回显为 `state=applied` 时表明底层事务已完整提交。
5. **增量变更追齐预览**：
   - 运行 `migratectl catchup-api --preview` 评估源端自初次抽取后的增量变更与目标端自举变更。

---

### 阶段 5：服务配置调谐与网关路由生效

1. **不可变构件与 GitOps 锁定**：
   - 将所有应用镜像的固定 Commit SHA 与 OCI Digest 写入 GitOps 仓库；
   - 触发 Flux 自动调谐并等待 HelmRelease 达到 `Ready=True`。
2. **网关 Caddy 热重载**：
   - 更新 Caddy ConfigMap 后，必须显式调用 admin API 重载或触发 Pod 滚动更新：
     ```bash
     kubectl rollout restart deployment caddy -n ingress-prod
     ```
3. **可观测性资源缓冲**：
   - 确保 Datakit 容器配额合理（Memory Request 128Mi / Limit 512Mi），避免 OOMKilled。

---

### 阶段 6：canonical DNS 切换与边缘节点恢复

1. **留存 DNS 回退映射**：
   - 记录所有 canonical 域名在切换前的当前 DNS 记录 ID 与目标值。
2. **Cloudflare 权威记录更新**：
   - 通过 Cloudflare API 将 canonical 域名（Web-SaaS、Vault、Observability、PostgreSQL）更新至目标端公网 IP；
   - 使用公共 DNS（`1.1.1.1`、`8.8.8.8`）与 DoH 验证全球解析生效情况。
3. **边缘 Agent 接入核验**：
   - 监控各区域 Agent（如 JP、US）与 Accounts 的通信；
   - 检查心跳上报状态、Xray 配置下发客户端数量与白名单过滤正确性。

---

### 阶段 7：用户验收、锁保护与退役标准

1. **用户会话验收**：
   - 请求具有业务权限的用户登录控制台，进行区域节点可见性与控制台核心页面复验；
   - 记录用户明确确认答复作为“登录态验收”凭证。
2. **基础设施生命周期保护管理**：
   - 确认新环境目标实例已开启云厂商实例删除保护锁（`cannot_delete`）；
   - 在用户明确授权后，解除源端旧实例的删除保护锁，但保留实例处于运行状态。
3. **退役前置守则**：
   - 设定至少 **14 天**的生产观察缓冲期；
   - 待所有业务账单、离线冷备归档、WireGuard 依赖完全解除后，方可由管理员执行最终资源回收与磁盘清理。
