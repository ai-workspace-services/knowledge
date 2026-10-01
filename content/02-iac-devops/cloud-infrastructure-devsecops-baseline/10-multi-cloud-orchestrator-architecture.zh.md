# 多云 Hybrid / Selfhost / Serverless 编排架构规划

> 状态：规划基线
>
> 身份和状态的操作契约：[多云身份 Bootstrap 与状态契约](11-cloud-oidc-bootstrap-contract.zh.md)。
>
> 适用环境：UAT；SIT、PROD 可复用同一架构，但必须使用各自的 Vault 路径、账号、状态前缀和发布策略。
>
> 关联仓库：
> [platform-ops-toolkit](https://github.com/ai-workspace-infra/platform-ops-toolkit)、
> [gitops](https://github.com/ai-workspace-infra/gitops)、
> [iac_modules](https://github.com/ai-workspace-infra/iac_modules)。

## 1. 目标与边界

本架构把三类部署能力统一到一个可审计的编排入口：

1. **Hybrid Orchestrator**：多云和多运行时的统一入口，只负责读取矩阵、建立顺序、派发子工作流和等待结果。
2. **Selfhost Orchestrator**：负责 Terraform VPS、主机初始化、Caddy、Docker、监控探针、Agent Proxy 和 Selfhost 业务部署。
3. **Serverless Orchestrator**：负责 Cloudflare Pages/Workers、Cloud Run、Supabase 及 Serverless 业务发布。

其中 `web-saas` 不是二选一的运行时：Selfhost 承载完整后端栈和 PostgreSQL origin，
Serverless 同时承载 Cloud Run、Supabase 以及 Cloudflare Pages/Workers。Cloudflare
Workers 是统一 SSR/edge gateway，默认将请求路由到 Selfhost origin，只有健康状态、容量
或显式策略允许时才分流到 Cloud Run。

本架构不把所有资源强行纳入 Terraform：

- `terraform` 资源必须有独立 state 和独立锁范围。
- `existing` / `existing-selfhost` 资源只通过 CMDB、Vault 和 Playbook 管理，不创建、不接管、不销毁 Terraform 资源。
- 业务编排不能隐式执行 `destroy`。
- 旧的 `observability.svc.plus` 节点是迁移源和恢复边界，不进入新 state，也不得被新编排销毁。

## 2. 总体架构

```text
GitHub Actions workflow_dispatch
             |
             v
   Hybrid Orchestrator
   (ordering + routing + wait)
       |              |               |
       v              v               v
 Selfhost         Serverless     External Inventory
 Orchestrator     Orchestrator   / Existing Adapter
       |              |               |
       v              v               v
 Terraform +       Pages/Workers  TW/PH Ulighthost
 Playbooks         Cloud Run      existing nodes
       |
       +--> Cloud provider adapters
             AWS / GCP / Azure / Vultr / Akamai / UCloud

 前端入口：Cloudflare Pages + Workers
                   |
                   v
          SSR / Gateway 路由层
            |               |
            v               v
      Selfhost API      Cloud Run API
      + PostgreSQL      （按策略降级/扩展）

 UAT private network gate:
 Terraform readiness -> tw-xconnect.svc.plus -> business/existing deployment
```

### 2.1 责任边界

| 层 | 负责内容 | 不负责内容 |
|---|---|---|
| GitOps | 云厂商、区域、账号、规格、域名、existing 事实和拓扑声明 | Secret、Terraform state、运行时临时 token |
| IaC Modules | Provider tree、backend、资源模块、state key、plan/apply/destroy 契约 | 业务容器迁移和 DNS 所有权决策 |
| Platform Toolkit | Provider registry、路由、Vault 字段加载、工作流、审批、测试和 CMDB 输出 | 直接把 existing 主机转换为 Terraform 资源 |
| Playbooks | 主机基线、Caddy、容器、业务服务、监控探针和注册动作 | 创建 Terraform 云资源 |
| Hybrid | 串行编排、依赖 gate、子工作流结果传播 | 自己实现 Terraform 或业务部署逻辑 |

## 3. 三类 Workflow 设计

### 3.1 Hybrid Orchestrator

文件：`platform-ops-toolkit/.github/workflows/hybrid-orchestrator.yml`

Hybrid 是 UAT 多云部署的唯一推荐入口。它的 `target_domains` 只提供：

```text
all
```

`all` 代表读取版本化 UAT resource matrix，而不是把所有逻辑硬编码在 workflow 中。

Hybrid 必须做到：

- 统一接收 `operation=plan|apply|deploy|destroy`。
- `operation=deploy` 必须要求不可变 `deploy_tag`。
- 依照矩阵和显式依赖串行派发子工作流。
- 派发后等待子运行结束；任意失败立即停止后续阶段。
- 不直接读取云厂商长期密钥。
- 不把 `destroy` 混入 `deploy`。
- 输出每个 namespace 的 workflow run、provider、account、state 或 existing 事实。

### 3.2 Selfhost Orchestrator

文件：`platform-ops-toolkit/.github/workflows/selfhost-orchestrator.yml`

Selfhost 支持细粒度业务域，当前输入选项为：

```text
all
ai-workspace
web-saas
open-platform
infra-platform
agent-proxy
agent-proxy-jp
agent-proxy-us
agent-proxy-sg
web-saas + agent-proxy
```

Selfhost 的职责包括：

- Terraform plan/apply/destroy。
- Provider credentials 和 state credentials 的 Vault 加载。
- AWS/GCP/Azure/Vultr/Akamai 等 provider 路由。
- SSH、sudo、安全基线、Docker 和 Caddy。
- Monitor Agent 默认接入 `https://observability.svc.plus/`。
- Agent Proxy 注册 Accounts controller。
- 输出 inventory、CMDB 和部署摘要。

Selfhost 对 `existing-selfhost` 必须使用 `existing_target_host` 等事实参数；不得因为 `operation=deploy` 而新建或销毁该主机。

### 3.3 Serverless Orchestrator

文件：`platform-ops-toolkit/.github/workflows/serverless-orchestrator.yml`

Serverless 当前输入选项为：

```text
all
ai-workspace
web-saas
infra-platform
agent-proxy
web-saas + agent-proxy
```

Serverless 负责：

- Cloudflare Pages 前端发布。
- Cloudflare Workers edge/gateway 路由。
- Cloud Run SSR/API 版本发布。
- Supabase schema/catalog 等非主机能力。
- `selfhost-first` 路由策略：优先把 SSR/API 请求送到 Selfhost API + PostgreSQL，只有在容量、健康状态或显式策略允许时才使用 Cloud Run。

Serverless 不负责创建 Akamai、AWS 或 GCP VPS；VPS 资源由 Selfhost/IaC 子链路管理。

## 4. UAT 八项资源矩阵

文件：`platform-ops-toolkit/.github/hybrid/uat-resource-matrix.json`

| 顺序 | Namespace | 管理模式 | Provider | 目标规格/位置 | 生命周期 |
|---:|---|---|---|---|---|
| 1 | `open-platform` | `terraform` | `akamai-cloud` | 2C4G | 常驻 |
| 2 | `web-saas` | `existing+serverless` | `gcp-cloud` | 复用现有 Vault node 0 承载 Selfhost 全栈，并部署 Serverless 面 | external |
| 3 | `ai-workspace` | `existing-selfhost` | GCP/private logical identity | 4C8G；复用 `10.79.0.7` | external |
| 4 | `agent-proxy-jp` | `terraform` | `aws-cloud` | AWS JP，2C2G | ephemeral |
| 5 | `agent-proxy-us` | `terraform` | `gcp-cloud` | GCP US，2C2G | ephemeral |
| 6 | `agent-proxy-sg` | `terraform` | `akamai-cloud` | Akamai SG，2C2G | ephemeral |
| 7 | `agent-proxy-tw` | `existing` | `ulighthost` | 复用 TW existing | external |
| 8 | `agent-proxy-ph` | `existing` | `ulighthost` | 复用 PH existing | external |

### 4.1 业务与基础设施顺序

`target_domains=all / operation=deploy` 的目标顺序不是简单的矩阵 order，而是带依赖 gate 的两阶段 DAG：

```text
Phase 1: Terraform readiness
  open-platform
      -> agent-proxy-jp IaC readiness
      -> agent-proxy-us IaC readiness
      -> agent-proxy-sg IaC readiness

Phase 2: Zero Trust and workloads
  XConnect Zero: tw-xconnect.svc.plus
      -> web-saas Selfhost full-stack origin
      -> web-saas Serverless (Cloud Run + Supabase + Pages/Workers)
      -> ai-workspace existing-selfhost: 10.79.0.7
      -> agent-proxy-jp application
      -> agent-proxy-us application
      -> agent-proxy-sg application
      -> agent-proxy-tw existing
      -> agent-proxy-ph existing
```

原因：JP/US/SG 的新节点必须先存在，才能把它们纳入 UAT 跨区域 Zero Trust 网络；XConnect gate 成功后，依赖内网链路的 AI Workspace、Agent Proxy 和 existing 节点才允许继续。

## 5. AWS JP Bootstrap 前置依赖

### 5.1 依赖关系

```text
Vault KV: kv/data/CICD/uat/aws-bootstrap
              |
              v
aws-oidc-bootstrap.yml (uat + apply)
              |
              v
AWS OIDC provider + GithubAction_IAC_Deploy_Role trust
              |
              v
selfhost-orchestrator / agent-proxy-jp
              |
              v
aws-actions/configure-aws-credentials
```

JP AWS 子流程不能直接假设 `GithubAction_IAC_Deploy_Role` 已可用。执行 JP Terraform 之前，必须确认：

- AWS account 为 GitOps 声明的具体账户 `950604983695`。
- OIDC provider 为 `token.actions.githubusercontent.com`。
- audience 为 `sts.amazonaws.com`。
- Role 为 `GithubAction_IAC_Deploy_Role`。
- UAT trust 包含当前 workflow 的 `main` 和 `environment:uat` subject。
- Vault 路径存在 `AWS_ACCESS_KEY_ID` 和 `AWS_SECRET_ACCESS_KEY`。
- AWS bootstrap job 已成功完成。

Bootstrap workflow：

```text
.github/workflows/aws-oidc-bootstrap.yml
```

推荐运行参数：

```text
action=apply
allow_root_break_glass=false
vault_env_path=uat
```

`allow_root_break_glass=true` 只允许经过明确审批的短期 break-glass 会话，不能作为日常配置。

### 5.2 失败处理

若出现：

```text
Not authorized to perform sts:AssumeRoleWithWebIdentity
```

必须停止 Hybrid 后续流程，先检查：

1. AWS bootstrap 是否成功。
2. GitOps OIDC 声明是否与实际 Role ARN 一致。
3. IAM trust 的 `sub` 是否覆盖 `main`、`environment:uat` 和当前 workflow。
4. Vault bootstrap KV 是否同时包含两项 AWS key。
5. GitHub job 是否具备 `id-token: write`。

不能通过静态 AWS access key 绕过 OIDC，也不能在 GitHub Secrets 中复制长期 AWS 凭据。

## 6. XConnect Zero Trust Gate

### 6.1 Gateway

UAT Gateway 使用可配置引用：

```text
tw-xconnect.svc.plus
```

该值必须通过 workflow input `xconnect_gateway_ref` 传递，不应在 TW/PH job 或 Playbook 中硬编码。Gateway 的 Vault 记录按具体 hostname 管理，例如：

```text
kv/data/uat/ulighthost-xconnect/tw-xconnect.svc.plus
kv/data/uat/ulighthost-xconnect/ph-xconnect.svc.plus
```

### 6.2 Gate 规则

XConnect workflow 只允许在以下条件同时满足时启动：

- `open-platform` 成功。
- JP/US/SG Terraform readiness 全部成功。
- Terraform 没有触发 destroy。
- Gateway reference 非空并通过 Vault/CMDB 校验。
- `matrix_node_filter=all`。

XConnect 成功后才允许：

- 复用 AI Workspace `10.79.0.7`。
- 部署 JP/US/SG Agent Proxy 应用。
- 调用 TW/PH external inventory adapter。

XConnect 失败时不得继续部署依赖 private network 的业务节点。

## 7. State、Inventory 与 Secret 契约

### 7.1 Terraform state

Terraform state 必须按环境、项目、云、账号和 namespace 隔离：

```text
terraform/<env>/<project>/<cloud>/<account>/<namespace>/terraform.tfstate
terraform/<env>/<project>/<cloud>/<account>/<namespace>/terraform.tfstate.tflock
```

UAT 示例：

```text
terraform/uat/svc.plus/akamai-cloud/manbuzhe2026/open-platform/terraform.tfstate
terraform/uat/svc.plus/aws-cloud/950604983695/agent-proxy-jp/terraform.tfstate
terraform/uat/svc.plus/gcp-cloud/xworktech/agent-proxy-us/terraform.tfstate
terraform/uat/svc.plus/akamai-cloud/manbuzhe2026/agent-proxy-sg/terraform.tfstate
```

要求：

- S3 兼容 endpoint 由 Vault KV 注入。
- 开启 bucket versioning、server-side encryption 和 `.tflock`。
- backend 不写静态凭据。
- 每个 namespace 独立 plan、apply、inventory 和 CMDB 记录。
- `existing` 资源不生成 Terraform state。

### 7.2 Vault KV

统一 state 参数入口：

```text
kv/data/CICD/uat/iac_state
```

字段契约：

```text
TF_STATE_ENDPOINT
TF_STATE_BUCKET
TF_STATE_ACCESS_KEY
TF_STATE_SECRET_KEY
TF_STATE_REGION
```

Provider token 使用 provider 专属路径，例如 Akamai/Linode：

```text
kv/data/CICD/uat/akamai-cloud/manbuzhe2026
  LINODE_TOKEN
```

AWS bootstrap：

```text
kv/data/CICD/uat/aws-bootstrap
  AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY
  AWS_SESSION_TOKEN      # 可选
```

Existing 节点事实：

```text
kv/data/uat/ulighthost-xconnect/tw-xconnect.svc.plus
kv/data/uat/ulighthost-xconnect/ph-xconnect.svc.plus
```

Secret 不得进入 GitOps、Terraform plan artifact、CMDB 或日志。

## 8. 前端和流量调度

默认入口为：

```text
Cloudflare Pages + Cloudflare Workers
```

推荐的 `selfhost-first` 策略：

1. Pages 提供前端静态资源和 SSR 入口。
2. Workers 执行认证、Host、Tenant、Rate Limit 和路由判断。
3. 健康的 Selfhost API + PostgreSQL 作为第一优先级。
4. Selfhost 不可用、容量不足或请求明确要求 Serverless 时，转发到 Cloud Run。
5. Cloud Run 作为弹性补充，而不是所有请求的默认后端。
6. 所有路由决策必须有可观测指标和回滚开关。

路由模式：

```text
selfhost-first
selfhost-only
cloud-run-first
cloud-run-only
```

UAT 默认使用 `selfhost-first`，DNS 默认 `none`，避免验证阶段误切生产流量。

## 9. 统一部署流程

### 9.1 `plan`

```text
读取 GitOps matrix
  -> 校验 provider registry
  -> 校验 account / state key / Vault path
  -> 校验 AWS bootstrap 前置状态
  -> Terraform init / validate / plan
  -> Serverless plan
  -> Existing inventory 只读检查
```

### 9.2 `deploy`

```text
确认 operation=deploy、target_domains=all、不可变 deploy_tag
  -> AWS bootstrap（JP 前置）
  -> open-platform
  -> JP/US/SG Terraform readiness
  -> XConnect Zero: tw-xconnect.svc.plus
  -> web-saas Selfhost full-stack origin
  -> web-saas Serverless (Cloud Run + Supabase + Pages/Workers)
  -> AI Workspace existing-selfhost: 10.79.0.7
  -> JP/US/SG Agent Proxy application
  -> TW/PH existing inventory + Playbook
  -> Monitor Agent / Accounts heartbeat / HTTPS / SSH 验收
```

### 9.3 `destroy`

`destroy` 必须单独显式触发，且只允许临时 Terraform namespace：

```text
允许：agent-proxy-jp / agent-proxy-us / agent-proxy-sg
按审批允许：web-saas / ai-workspace
禁止：open-platform
禁止：旧 observability.svc.plus 节点
禁止：TW/PH Ulighthost existing
```

`target_domains=all / operation=deploy` 永远不执行 destroy。

## 10. 观测、验收与失败停止条件

每个新建或复用节点默认部署 Monitor Agent，并上报：

```text
https://observability.svc.plus/
```

最低验收项：

| 类别 | 验收内容 |
|---|---|
| IaC | provider、account、region、规格和 namespace 正确 |
| State | backend key 正确，锁文件范围只覆盖当前 namespace |
| AWS | OIDC bootstrap 成功，JP 可 AssumeRoleWithWebIdentity |
| XConnect | `tw-xconnect.svc.plus` gate 成功，跨区域内网可达 |
| 主机 | SSH、sudo、Docker、Caddy、重启恢复通过 |
| 业务 | Web SaaS、AI Workspace、Agent Proxy 健康检查通过 |
| Existing | TW/PH 读取正确 Vault path，不创建 Terraform 资源 |
| 监控 | Monitor Agent 心跳到 Observability 正常 |
| Accounts | JP/US/SG/TW/PH 注册和心跳正常 |
| 安全 | 无 secret 出现在日志、artifact、GitOps 或 plan |
| 清理 | deploy 阶段没有 destroy；受保护节点未被修改或删除 |

任一前置失败，后续依赖阶段必须跳过并保留失败上下文。尤其是 AWS OIDC 或 XConnect gate 失败时，不得继续执行区域业务部署。

## 11. 当前实现差异和后续任务

当前架构目标与代码实现需要持续对齐：

1. Hybrid 输入只暴露 `target_domains=all`，这是预期设计。
2. Selfhost 和 Serverless 保留细粒度业务域，便于单域重跑。
3. JP AWS 必须把 `aws-oidc-bootstrap.yml` 作为显式前置依赖。
4. 当前 `main` 的 routine deploy 逻辑将 `open-platform` 标记为 `shared-infrastructure` 并跳过；如果验收标准要求每次 `all/deploy` 都验证 `open-platform`，需要修改 release scope 或增加显式 `include_shared_infrastructure=true` 输入。
5. Bootstrap 缺少 `AWS_SECRET_ACCESS_KEY` 时必须在 preflight 明确失败，而不是让 JP 子流程延迟失败。
6. Hybrid 应在派发 JP 前检查 bootstrap job 成功状态，并把 bootstrap run URL 写入 deployment summary。
7. XConnect gate 的成功证据应写入统一 run record，并关联 Gateway hostname、矩阵版本和节点列表。

## 12. 推荐实现拆分

### Phase 1：契约和自检

- 固化八项 UAT matrix schema。
- 添加 provider registry 和 release scope 校验。
- 添加 state key、Vault path、AWS bootstrap 和 destroy scope contract test。
- 只执行 `plan` / dry-run，不创建资源。

### Phase 2：前置身份与网络

- 完成 UAT AWS OIDC bootstrap。
- 确认 JP AWS role trust 和 Vault bootstrap KV。
- 完成 Akamai token、GCP OIDC、UCloud/Ulighthost existing 事实读取。
- 完成 Terraform readiness 后触发 XConnect Zero。

### Phase 3：业务和 existing

- 部署 Web SaaS Serverless。
- 验证并复用 AI Workspace `10.79.0.7`。
- 部署 JP/US/SG Agent Proxy 应用。
- 接入 TW/PH existing Playbook。
- 验证 Monitor Agent 和 Accounts heartbeat。

### Phase 4：发布与回滚

- 只使用不可变 daily build tag。
- 默认 `dns_mode=none`。
- 生成每个 namespace 的 inventory、CMDB 和 run record。
- 业务失败时只回滚业务版本，不回滚 open-platform 或旧 observability 节点。
- 资源清理必须按 namespace 显式审批，禁止批量误删。

## 13. 结论

这套架构的核心不是把所有资源放进一个大 workflow，而是通过一个统一 Hybrid 入口，把 Terraform、Serverless、Playbooks 和 Existing inventory 组合成有依赖、有边界、可回滚的执行图：

```text
GitOps 声明
  -> provider/account/state 校验
  -> AWS bootstrap 和 Terraform readiness
  -> XConnect Zero Trust
  -> Selfhost / Serverless / Existing 部署
  -> Monitor Agent + Accounts heartbeat
  -> inventory / CMDB / run record
```

最终必须同时满足：云服务商可替换、state 独立、existing 不被 Terraform 接管、AWS JP 有 bootstrap 前置、XConnect 在 IaC 就绪后建立、前端默认 selfhost-first，以及 `deploy` 永不隐式执行 `destroy`。
