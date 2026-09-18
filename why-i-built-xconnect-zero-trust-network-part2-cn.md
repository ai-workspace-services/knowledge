# 一个人、4台设备、5端全平台（二）：XConnect 控制面上线与抗干扰落地

> **作者**：沈蓝（IT 运维老兵 / 独立开发者）  
> **分类**：架构实践 / 网络工程 / 独立开发产品日志  
> **系列**：1人·4机·5端全平台自建私网连载（第 2 篇）  
> **关键词**：XConnect Zero, WireGuard over VLESS, XHTTP, 零信任私网, 控制平面, 抗干扰网络, GitOps  

---

## 摘要

在上一篇[《一个人、4台设备、5端全平台（一）：成熟方案为何不够？自建零信任私网》](./why-i-built-xconnect-zero-trust-network-cn.md)中，我复盘了为什么成熟的商业组网方案（Tailscale、ZeroTier）和纯 WireGuard 在复杂的真实网络中屡屡碰壁：纯 UDP 极易遭遇运营商 QoS 惩罚与阻断，公共中继延迟不可控，且无法与自建的云原生凭据及微服务架构深度契合。

经过近期的闭关攻坚，自建的 **XConnect Zero 零信任管理网络** 正式迎来了阶段性里程碑：基于 Serverless 架构的前端控制面在 UAT 环境（`console-serverless-uat`）完成首轮联调，核心的“抗干扰连接数据面”（WireGuard over VLESS / XHTTP）全面打通。

这不是什么宏大的“骨干网”，而是一套为我个人手头 4 台主力设备、5 端全平台量身定制的**稳定连接的专属管理网络**。本文将同步第一阶段的落地成果，公开背后的真实代码仓库与流水线矩阵，并正式预留后续的两大核心实战篇章。

---

## 一、 控制面上线：XConnect Zero 架构解耦与核心落地

在刚刚交付的 UAT 控制台页面上，XConnect Zero 的定位被严格收敛为：**使用 Zero Trust 管理私有网络、Gateway 与 One 节点**。整体系统分为轻量 Serverless 控制平面与底层强抗干扰数据平面。

### 1. 核心杀手锏：默认「抗干扰连接」（WireGuard over VLESS / XHTTP / L3）
传统自建私网在遇到严苛的公网 NAT、酒店或移动蜂窝网络时极易失联。在控制台的“配置管理”中，我设计了三种互联网络模式，并在当前 UAT 阶段默认下发 **抗干扰连接**：
- **高性能直连（WireGuard UDP / L3）**：保留极速直连能力，但公网默认不开放 51820 UDP 端口，最大化收敛暴露面；
- **抗干扰连接（WireGuard over VLESS / XHTTP / L3，推荐·默认）**：核心技术突破在于**将 WireGuard 报文通过 VLESS/XHTTP 封装进标准 TLS TCP 443 流量中**。在外人与中间设备看来，它只是合规的 HTTPS 流量，既保留了 WireGuard 的内核级低延迟与高安全性，又彻底免疫了运营商对 UDP 的丢包、降速与特征识别；
- **二层互联（WireGuard over VLESS / L2-MAC）**：规划中的二层扩展模式，用于后续跨物理机房桥接广播域与特殊网络设备。

### 2. 严密的节点生命周期与零信任签发
网络拓扑严格划分为两类角色：
- **Gateway 节点**：固定为 Linux 实例，部署在多云或关键入口，承担受控中继与安全路由；
- **One 节点**：覆盖 **Linux、macOS、Windows、iOS、Android 5 端全平台**，受策略保护，即插即用。

控制台落实端到端零信任原则：
- **无私钥上云**：客户端入网操作严格遵循 `diagnose -> init (本机生成公私钥) -> 登记网络/签发 Gateway/One 邀请 -> join -> up`，私钥永远不出设备本地；
- **短时令牌握手**：控制台仅签发 15 / 30 / 60 分钟有效期的短时加入邀请，通过后端 API 交换公钥，并依赖设备上报 ACK 闭环确认状态。

---

## 二、 场景结合：自建管理网络究竟为谁服务？

构建这套稳定连接的管理网络，终极目标是为了给自己的高价值业务资产提供一层“隐形防弹衣”。接下来的连载将重点展开两大核心场景：

### 【连载篇三预留】一个人、4台设备、5端全平台（三）：零信任私网打通 AI 聚合网关集群
- **场景痛点**：我的私有 AI 聚合网关汇聚了 Caddy 边缘反代、Kong 流量网关、LiteLLM 与 New API 调度中心，以及独立 VPS 上的 CPA（CLIProxyAPI）多账号池（Codex、Claude Code、Grok 等）。网关承载着高价值的 API Key 与 OAuth Bundle，严禁将 3000、8317 等内部端口暴露在公网上。
- **结合方案**：
  1. **零外网暴露**：CPA 与 New API 仅绑定私网虚拟 IP 与本地回环，公网不可探针；
  2. **跨端即时访问**：笔记本或移动设备挂载 XConnect One 节点后，犹如坐在机房内网一样直接调用 `/v1/responses` 与 `/v1/messages` 原生协议；
  3. **凭据安全闭环**：结合 HashiCorp Vault KV CAS 单写者刷新机制与宿主机 `tmpfs` 内存认证注入，彻底消除凭据泄露风险。

### 【连载篇四预留】一个人、4台设备、5端全平台（四）：零信任私网打通 Multi AI-Workspace
- **场景痛点**：个人拥有 4 台核心物理设备（MacBook Pro、Linux 算力工作站、家庭 NAS/私服、移动终端），分散在不同网络环境。同时，各个工作空间常驻运行着 CodeAgent、Antigravity SDK 智能体集群，跨设备远程调试（VS Code Remote、LSP 语义索引、Agent RPC 跨机通信）面临严重的 NAT 穿透壁垒与 IP 漂移问题。
- **结合方案**：
  1. **同网段化安全互联**：通过 XConnect Zero 为所有物理机与云端工作空间分配静态专用内网 IP，实现全局无缝直通；
  2. **多 Agent 状态实时同步**：跨机器消除公网代理开销，打造高可用、抗弱网的个人专属分布式开发工作站。

---

## 三、 工程化落地：真实的本地仓库与 CI/CD 流水线清单

整套方案拒绝“PPT 架构”，目前已在本地工作空间沉淀为严谨的 GitOps 与代码仓库矩阵：

### 1. 核心仓库矩阵
| 仓库路径 | 核心职责与工程分工 |
| :--- | :--- |
| **`ai-workspace-service/portal`** | **前端控制面**：基于 Next.js / OpenNext 部署至 Cloudflare Pages 的 Serverless 控制台，内置 `src/modules/extensions/builtin/xconnect-zero` 扩展与 `/api/xconnect-zero` BFF 代理层 |
| **`ai-workspace-service/accounts`** | **控制面核心服务**：Go + PostgreSQL 驱动，负责 `/api/overlay/v1` 接口、维护 `overlay_devices`、`overlay_nodes` 与 `overlay_config_acks` 状态机，提供 `cmd/overlayctl` 运维命令行 |
| **`xconnect-edge-agent`** | **边缘节点代理**：部署在 Linux Gateway 上的控制守护进程，对接 accounts 控制面，动态生成/热加载 Xray 传输配置，配合 Caddy 自动化 TLS 证书管理 |
| **`ai-workspace-infra/gitops`** | **声明平面**：以代码化方式声明 Gateway 节点拓扑、内网网段划分、VPC 对等与访问控制 ACL 规则 |
| **`ai-workspace-infra/playbooks`** | **自动化交付**：Ansible 自动化编排 Linux 宿主机 BBR 队列优化、WireGuard 接口配置与 systemd 服务托管 |
| **`ai-workspace-infra/platform-ops-toolkit`** | **交付流水线**：跨平台二进制交叉编译、Gitleaks 密钥扫描与端到端抗干扰链路探针脚本 |
| **`ai-workspace-service/knowledge`** | **架构知识库**：本连载系列与 ADR 架构决策记录的技术事实源 |

### 2. CI/CD 核心流水线清单
- **`ci-xconnect-client-build.yml`**：跨平台自动化交叉编译 macOS、Linux、Windows 客户端二进制制品，自动签名并生成 SHA-256 校验和；
- **`cd-portal-cloudflare-pages.yml`**：前端 Portal 控制台代码 Push 自动触发编译，秒级同步至 Cloudflare Pages 边缘节点；
- **`deploy-overlay-gateway-ansible.yml`**：Ansible 幂等对账流水线，一键初始化异地 Linux Gateway 节点及抗干扰中继通道；
- **`e2e-overlay-mesh-verify.yml`**：在 UAT 环境中对 Gateway 和 One 节点执行端到端握手、XHTTP 封装抗弱网丢包率与时延探针测试。

---

## 四、 尾巴与真实碎碎念

> **真实的研发日常**：  
> 底层的网络数据面（WireGuard over VLESS / XHTTP）因为有扎实的协议和 Linux 内核网络栈加持，配好路由规则和封装，网络打通其实神速；  
> 反而是前端控制面的对接——从 Next.js SSR / BFF 代理路由的边界校验、Accounts API 的跨域与鉴权、节点公钥初始化的短时邀请弹窗，到配置同步 ACK 的状态机闭环，扣各种交互细节花了大把时间和心力。  
> 
> 这周高强度拉通全链路流水线、调完前后端，**跟 AI 结对编程的 Token 额度彻底见底跑空了！** 😅  
> 
> 先缓一口气，等下周 Token 满血复活，我们立刻进入硬核落地的连载第三篇：**《一个人、4台设备、5端全平台（三）：零信任私网打通 AI 聚合网关集群》**，下篇见！
