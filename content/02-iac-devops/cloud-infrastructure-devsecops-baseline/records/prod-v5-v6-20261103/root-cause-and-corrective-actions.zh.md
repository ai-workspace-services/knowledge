# PROD V5 → V6 故障根因分析与纠正措施复盘

> 记录日期：2026-11-03，Asia/Shanghai。
> 统一入口：[PROD V5 → V6 复盘与演进总述](../../18-prod-v5-v6-deployment-and-migration-retrospective.zh.md) · [归档索引](README.md)。

---

## 复盘结构规范

本篇严格遵循 DevSecOps 故障复盘八步法对 2026-11-01 至 2026-11-03 期间发生的 9 项关键故障展开全景剖析：
`症状 (Symptom)` → `证据 (Evidence)` → `原因 (Root Cause)` → `最小修改 (Minimal Modification)` → `Owner / PR / 构件 (Owner/PR/Artifact)` → `调谐 (Reconciliation)` → `运行验证 (Live Verification)` → `未决项与教训 (Open Items & Lessons Learned)`。

---

## 案例 1：私有 GHCR 镜像拉取报 403 阻断

1. **症状 (Symptom)**：
   - K3s 首次应用 GitOps 声明后，Web-SaaS 各 Pod 处于 `ImagePullBackOff` 或 `ErrImagePull` 状态，应用无法拉起。
2. **证据 (Evidence)**：
   - Pod 描述输出：`Failed to pull image "ghcr.io/ai-workspace-infra/accounts:...": rpc error: code = Unknown desc = failed to pull and unpack image ...: unexpected status code 403 Forbidden`。
3. **原因 (Root Cause)**：
   - K3s 节点拉取 GHCR 私有包时，未正确挂载具备 `read:packages` 范围的容器镜像注册表 Secret，且旧配置直接引用了私有镜像仓库路径。
4. **最小修改 (Minimal Modification)**：
   - 将镜像发布流中的构件统一发布至公开（Public）包路径，同时在 GitOps 中更新镜像路径并固定不可变 SHA-256 digest。
5. **Owner / PR / 构件**：
   - Owner：GitOps / CI 负责人
   - PR：[GitOps #743](https://github.com/ai-workspace-infra/gitops/pull/743)
   - 构件：切换为公开 OCI 镜像引用
6. **调谐 (Reconciliation)**：
   - Flux 自动调谐 `web-saas-prod` Kustomization，拉取更新后的 Deployment 声明。
7. **运行验证 (Live Verification)**：
   - 镜像拉取全部耗时低于 15 秒，Pod 状态由 `ImagePullBackOff` 转为 `Running`，拉取重试计数清零。
8. **未决项与教训 (Lessons Learned)**：
   - 生产集群部署必须在前置阶段明确镜像仓库的访问策略（公开 vs 私有+严格 ImagePullSecret），避免冷启动阶段受阻。

---

## 案例 2：Datakit 观测栈 Secret 缺失与 128Mi 内存 OOMKilled 连环故障

1. **症状 (Symptom)**：
   - Datakit Pod 频繁重启（`CrashLoopBackOff`），同时出现 `OOMKilled` 现象，观测指标流完全中断。
2. **证据 (Evidence)**：
   - `kubectl describe pod datakit-...` 显示：`Last State: Terminated, Reason: OOMKilled, Exit Code: 137`。
   - ESO 状态报错：`SecretStore "vault-backend" not found`，且缺少字段 `dataway_token` 映射。
3. **原因 (Root Cause)**：
   - 1）GitOps 中 Datakit 的 ExternalSecret 引用了不存在的旧 SecretStore，且 Vault KV 路径字段大小写漂移；
   - 2）Datakit DaemonSet 容器初始内存 Limit 仅设置为 `128Mi`，当抓取 K3s 节点全部系统日志和指标时瞬时峰值超出配额。
4. **最小修改 (Minimal Modification)**：
   - 1）修正 ExternalSecret 声明，对齐 Vault 真实路径 `kv/datakit/shared/dataway`；
   - 2）调整资源配置：将 Memory Request 调整为 `128Mi`，Limit 放宽至 `512Mi`。
5. **Owner / PR / 构件**：
   - Owner：平台运维与可观测性负责人
   - PR：[GitOps #746](https://github.com/ai-workspace-infra/gitops/pull/746)（Secret 修复）、[GitOps #750](https://github.com/ai-workspace-infra/gitops/pull/750)（资源调整）
6. **调谐 (Reconciliation)**：
   - ESO 成功生成 Secret `datakit-secret`；DaemonSet 更新资源配额后重新滚动 Pod。
7. **运行验证 (Live Verification)**：
   - 现场核查 `auditor` 证据：Datakit Pod `1/1 Running`，已平稳运行超过 **22 小时**，重启次数为 **0**，内存占用稳定在约 180Mi。
8. **未决项与教训 (Lessons Learned)**：
   - 观测组件常驻守护进程的资源配额不能简单套用极低资源规格，须基于实际指标采集量预留安全缓冲，并建立 OOMKilled 告警基线。

---

## 案例 3：ServiceLB 默认禁用导致 Ingress External-IP 长期 Pending

1. **症状 (Symptom)**：
   - Ingress 控制器创建的 `LoadBalancer` 类型 Service 长期处于 `<pending>` 状态，公网 443 端口无法接收流量。
2. **证据 (Evidence)**：
   - `kubectl get svc -n ingress-prod` 显示 `caddy-ingress-caddy-ingress LoadBalancer <pending>`。
   - 节点进程自检未发现 K3s 内置 ServiceLB 的 Pod。
3. **原因 (Root Cause)**：
   - 安装 K3s 时配置参数包含了 `--disable servicelb`（沿用自旧版独立独立外部网关的设计），导致轻量集群内缺少默认的 LoadBalancer 控制器实现。
4. **最小修改 (Minimal Modification)**：
   - 修改 K3s 配置文件 `/etc/rancher/k3s/config.yaml`，移除禁令并恢复 ServiceLB 部署，确保宿主机 443/80 端口可由 ServiceLB 守护 Pod 绑定。
5. **Owner / PR / 构件**：
   - Owner：IaC / Playbooks 负责人
   - PR：[Playbooks #958](https://github.com/ai-workspace-infra/playbooks/pull/958)、[GitOps #744](https://github.com/ai-workspace-infra/gitops/pull/744)
6. **调谐 (Reconciliation)**：
   - 重启 K3s 守护进程，ServiceLB 自动部署 DaemonSet `svclb-caddy-ingress-...`。
7. **运行验证 (Live Verification)**：
   - 现场 `kubectl get svc` 输出：`caddy-ingress-caddy-ingress LoadBalancer 10.53.189.155 172.237.24.232 443:22299/TCP,80:22080/TCP`；
   - 外部 HTTP 443 端口探测直接命中 Caddy，握手成功。
8. **未决项与教训 (Lessons Learned)**：
   - 在轻量级单节点集群中，内置组件的启用/禁用必须在基线规范中显式声明，不能凭历史经验随意关闭基础功能。

---

## 案例 4：Console Nginx 容器非特权缓存目录权限报错与 API 路径 500

1. **症状 (Symptom)**：
   - Console Pod 启动后探针失败，容器日志报非特权权限错误，访问页面报 500。
2. **证据 (Evidence)**：
   - 容器标准错误：`nginx: [emerg] mkdir() "/var/cache/nginx/client_temp" failed (13: Permission denied)`。
3. **原因 (Root Cause)**：
   - 镜像以非 root 用户（UID 1000）运行，但默认的 Nginx 配置文件仍试图向 `/var/cache/nginx` 和 `/var/run` 写入临时文件，违反最小权限安全约束。
4. **最小修改 (Minimal Modification)**：
   - 修改 Nginx 启动模板，将临时文件目录、客户端请求缓存路径重定向至非 root 拥有的 `/tmp/nginx` 目录，并注入无特权运行参数。
5. **Owner / PR / 构件**：
   - Owner：前端与 Console 维护团队
   - PR：[GitOps #747](https://github.com/ai-workspace-infra/gitops/pull/747)
6. **调谐 (Reconciliation)**：
   - Flux 自动调谐 Console Deployment，Pod 优雅重建。
7. **运行验证 (Live Verification)**：
   - Console Pod `1/1 Running`，就绪探针与存活探针均返回 HTTP 200，静态文件及 API 正常加载。
8. **未决项与教训 (Lessons Learned)**：
   - 实施容器非 root 安全准则时，必须完整梳理基础服务（如 Nginx）的默认写路径，使用 `/tmp` 或声明式 `emptyDir` 承载可写状态。

---

## 案例 5：Caddy Ingress ConfigMap 更新未自动 Reload

1. **症状 (Symptom)**：
   - GitOps 中合并了新的 Caddy 路由规则，Flux 也报告调谐成功，但外部请求依然命中旧路由，新增的重写与转发未生效。
2. **证据 (Evidence)**：
   - Caddy 容器日志在 GitOps 变更时间点未输出任何 `configuration reloaded` 记录；请求新路径依然返回旧响应。
3. **原因 (Root Cause)**：
   - Kubernetes 将 ConfigMap 挂载为文件系统时存在异步延迟，且 Caddy 进程默认不会主动对挂载文件设置 inotify 监听，导致配置未热加载。
4. **最小修改 (Minimal Modification)**：
   - 在配置变更后，通过受控手段显式调用 Caddy admin API `POST http://localhost:2019/load` 或触发 Deployment 滚动重启。
5. **Owner / PR / 构件**：
   - Owner：网关与 Ingress 负责人
   - 归档文件：[PROD-K3S-V6-ServiceLB-Caddy与Datakit修复提示词.md](../../../../../docs/reference/platform-delivery/PROD-K3S-V6-ServiceLB-Caddy与Datakit修复提示词.md)
6. **调谐 (Reconciliation)**：
   - 对 `caddy-ingress` 执行滚动更新，新 Pod 加载最新 ConfigMap。
7. **运行验证 (Live Verification)**：
   - 外部通过 DoH 与特定 Host 请求测试，新路由与精确重写立即生效，响应状态码符合预期。
8. **未决项与教训 (Lessons Learned)**：
   - ConfigMap 更新不等于应用进程生效；涉及网关等核心入口，必须将“重载或滚动更新”明确纳入操作手册的标准步骤。

---

## 案例 6：Accounts 控制器模板示例凭据覆盖真实 Token 导致 JP Agent 401

1. **症状 (Symptom)**：
   - canonical DNS 切换到 V6 后，日本边缘节点（JP Edge Agent）上报与拉取任务请求全部报 `401 invalid_token`，Agent 事件流中断。
2. **证据 (Evidence)**：
   - JP Agent 日志：`401 invalid_token`；
   - 现场比对发现：Agent 本地配置的 Token 与 V6 Vault 注入的 `INTERNAL_SERVICE_TOKEN` 完全一致；但 Accounts 运行时实际内存注册表中的 Token 却不匹配。
3. **原因 (Root Cause)**：
   - V6 镜像内的 Accounts 配置模板中包含了一条示例凭据（`agents.credentials: [...]`）。Accounts 启动时的加载优先级为：**模板内静态凭据列表 > 环境变量**。因此，示例列表中的假凭据直接屏蔽了 Vault 注入的有效真实 Token。
4. **最小修改 (Minimal Modification)**：
   - 1）提取模板并将 `agents.credentials` 显式设为空列表 `[]`；
   - 2）在 V6 Vault `kv/prod/Accounts-service` 增加 `ACCOUNTS_CONTROLLER_CONFIG_TEMPLATE` 字段，KV 版本由 6 升级至 7；
   - 3）Accounts Deployment 挂载该模板，确保系统环境变量注入的 Token 成为唯一的认证回退源。
5. **Owner / PR / 构件**：
   - Owner：Accounts 核心团队 / GitOps
   - PR：[GitOps #771](https://github.com/ai-workspace-infra/gitops/pull/771)
   - Commit：`69afa51a94d96a5bb9cddc8e56b8a68741aae844`
6. **调谐 (Reconciliation)**：
   - ESO 自动感知 Vault 版本变更，同步 Secret `accounts-controller-config`；Accounts Pod 滚动更新。
7. **运行验证 (Live Verification)**：
   - JP Agent 事件流瞬间自愈，Xray 配置同步恢复，返回 HTTP 200，心跳恢复；抽查数据库确认 JP 节点健康状态为在线，同步客户端数为 **12**。
8. **未决项与教训 (Lessons Learned)**：
   - 严禁在生产配置模板中写入任何伪造或示例凭据；任何静态配置必须保持干净，凭据注入必须保证绝对优先权。

---

## 案例 7：Accounts 旧镜像拒绝 custom 资源等级导致 US Agent 400 失败

1. **症状 (Symptom)**：
   - 美国单节点 Agent（US Edge Agent）请求注册与拉取名单时，Accounts 返回 `400 agent_scope_invalid`，导致 US 节点无法接入。
2. **证据 (Evidence)**：
   - US Agent 请求响应体明确指出所请求的 `resourceClass: custom` 不在当前支持的等级列表中。
3. **原因 (Root Cause)**：
   - V6 初始部署所引用的旧版本 Accounts 镜像中尚未合入单节点 `custom` 资源等级与 `customAllowFree` 授权逻辑，硬编码了资源等级校验范围。
4. **最小修改 (Minimal Modification)**：
   - 复用上游主线已合并的单节点特性代码，更新 Accounts 部署至支持 `custom` 等级与白名单过滤逻辑的不可变镜像，坚决不引入多虚拟节点复杂方案。
5. **Owner / PR / 构件**：
   - Owner：Accounts 团队
   - PR：[GitOps #772](https://github.com/ai-workspace-infra/gitops/pull/772)
   - 构件：Commit `bc32fac4846cea5281e9e764c5224a581dff1ed1`，Digest `sha256:f57e46a2624f554b92bd4983aede203c5cfcb0d2b83f3be33836cc715ec6eed4`
6. **调谐 (Reconciliation)**：
   - 手动触发 Flux 调谐，应用部署并执行健康检查。
7. **运行验证 (Live Verification)**：
   - US 节点再次发起请求，Accounts 返回 HTTP 200，scope 识别为 `custom`，下发邮箱名单严格等于三人白名单；US Agent 恢复持续同步 3 个客户端。
8. **未决项与教训 (Lessons Learned)**：
   - 代际迁移前必须完整审查历史特性集，确保目标环境镜像版本对全部在役边缘节点的业务协议具备向后兼容性。

---

## 案例 8：Console 镜像默认 Cloud Run 认证地址导致跨代调用异常

1. **症状 (Symptom)**：
   - Console 页面在向 Accounts 发送认证鉴权请求时，偶尔请求被抛向外部过期的 Cloud Run 接口，导致登录态验证不稳定。
2. **证据 (Evidence)**：
   - 浏览器网络调用分析显示，未配置运行期环境变量时，Console 前端代码默认回退至旧的 Cloud Run 后端域名。
3. **原因 (Root Cause)**：
   - 容器镜像打包时预设了跨云构建的默认端点，在 K3s 内部署时未显式覆盖内部服务通信地址。
4. **最小修改 (Minimal Modification)**：
   - 在 Console Deployment 的环境变量配置中，显式将认证/Zero 地址设置为内部 Kubernetes Service `http://accounts.web-saas-prod.svc.cluster.local:8080`，并锁定 `FRONTEND_IMAGE`。
5. **Owner / PR / 构件**：
   - Owner：前端与 Console 团队
   - PR：[GitOps #773](https://github.com/ai-workspace-infra/gitops/pull/773)
   - 构件：Commit `32695533eeb39f1af351cc3b4876aa9d23150c62`，Digest `sha256:5ee55a96a8184074ea4186cf38b426a0d368b686866afc345d2991b0eb02e8b9`
6. **调谐 (Reconciliation)**：
   - Flux 自动完成调谐，Console Pod 成功重启并就绪。
7. **运行验证 (Live Verification)**：
   - Console `/healthz` 接口输出完全匹配固定构件，前端向 Accounts 发起的跨容器请求 100% 命中集群内 ClusterIP，网络往返延迟由公网跨云的 150ms 降至 2ms 以内。
8. **未决项与教训 (Lessons Learned)**：
   - 微服务跨组件通信必须在 GitOps 环境配置中显式绑定内部服务发现地址，杜绝运行时依赖任何隐式代码默认值。

---

## 案例 9：Console 页面 Team 分配路径 404 导致前端报错

1. **症状 (Symptom)**：
   - 控制台 Team 分配页面加载时产生前端解析错误弹窗。
2. **证据 (Evidence)**：
   - 控制台前端请求路径为 `/api/admin/agents/team-enrollments`，Caddy 原生转发给 Accounts 时返回了纯文本的 `404 page not found`，前端在尝试将其作为 JSON 解析时抛出语法异常。
3. **原因 (Root Cause)**：
   - Accounts 服务的实际内部路由注册在 `/api/auth/admin/agents/team-enrollments`，由于 Caddy 配置中缺少对该特定管理路径的前缀重写，导致请求路径不匹配。
4. **最小修改 (Minimal Modification)**：
   - 在 Caddy 配置文件中为三个 Console 主机增加一条精确路径重写规则：将 `/api/admin/agents/team-enrollments` 精确重写转发至 Accounts 的 `/api/auth/admin/agents/team-enrollments`。
5. **Owner / PR / 构件**：
   - Owner：网关与 Ingress 负责人
   - 涉及配置：Caddy Ingress ConfigMap
6. **调谐 (Reconciliation)**：
   - 更新 ConfigMap 并执行 Caddy 滚动重启。
7. **运行验证 (Live Verification)**：
   - 经测试，未携带凭据的请求正确返回 JSON 格式的 `401 Unauthorized`（证明已成功由 Accounts 内部安全中间件处理，而非 404 路由丢失），TLS 正常。
8. **未决项与教训 (Lessons Learned)**：
   - API 网关路由映射应与后端路由契约保持单测同步，避免由前端界面报错才暴露出路径不一致问题。
