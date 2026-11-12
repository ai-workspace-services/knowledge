# ADR-0001：GitOps 三类执行器与单一配置负责人

- 状态：已接受（2026-11-13）
- 适用范围：ai-workspace-infra 全部环境（SIT / UAT / PROD），新机与换机优先落地
- 相关：[SIT-K3S-V6 换机执行清单](../clusters/sit-k3s-v6/SIT-K3S-V6-换机执行清单.md)、[Linux OS 三类操作身份](Linux-OS三类操作身份-最小实施草案.md)、[K3s role 职责与依赖清单](K3s-role职责与依赖清单.md)

## 背景

基础设施同时存在宿主机、Docker Compose 与 K3s/Kubernetes 三类运行面。过去存在同一配置由多处修改的情况（例如装机时手工写入的主机防火墙规则，仓库中没有来源），导致漂移难以发现，也难以审计。

## 决策

统一的是 **GitOps 治理规范**，而不是要求三个工具具备相同能力：

> Git 定义期望状态 → 执行器负责收敛 → Observability 负责观测 → Audit 负责追踪。

### 1. 三层执行器职责

| 执行器 | 管理对象 | 核心职责 |
| --- | --- | --- |
| Ansible Pull | Linux / VPS / Bare Metal | OS、SSH、Firewall、systemd、软件包、宿主机配置，以及 K3s 安装所需的主机级配置 |
| Doco CD | Docker / Docker Compose | Compose Stack、容器服务、镜像版本、环境配置 |
| Flux CD | K3s / Kubernetes | Helm Chart、Kustomize、K8s Workloads、Operator |

不重叠：Ansible 不发布容器应用；Doco CD 不负责宿主机系统配置；Flux 不直接管理裸机 OS。

### 2. 唯一配置负责人

| 管理层 | 唯一配置负责人 |
| --- | --- |
| Host OS | Ansible Pull |
| Docker Compose | Doco CD |
| Kubernetes / Helm | Flux CD |
| Secrets | Vault / SOPS，按环境适配 |
| Metrics / Logs | vmagent / Vector |
| Infrastructure Provisioning | OpenTofu / Terraform |

**同一资源只能有一个声明式配置负责人。** 例如 K3s 节点上，Ansible Pull 负责宿主机 OS 与 K3s 安装（含 `config.yaml`、sudoers、OS 账号、主机防火墙），Flux CD 负责集群内资源；两者不得同时修改同一份配置。

### 3. 收敛能力边界（不强求对等）

- Ansible Pull：周期运行 Playbook，可修复主机配置漂移。
- Doco CD：以 Git 变更（轮询或 Webhook）驱动 Compose / Swarm 部署，不等同于完整的运行时调谐控制器。
- Flux CD：通过 Kubernetes Controller 持续协调声明式资源。

## 结果与约束

- 主机上不得保留无仓库来源的手工配置；发现即登记待办并收归对应执行器。
- doco-cd 自身由 Ansible（playbooks 角色，独立 Docker Compose）安装，它部署的 Compose 应用归 Doco CD 收敛。
- Helm Chart 仅在 `ai-workspace-infra/artifacts`（`oci/charts`）维护，由 Flux 引用；playbooks 不含 Chart 代码。
- 架构形态：GitOps Governance → Host / Compose / Kubernetes 三类执行器 → Central Observability & Audit，不引入额外的统一控制器。

## 落地记录

- 2026-11-13 sit-k3s-v6：operator 免密 sudo 与 OS 身份经 `vhosts/common` 由 Ansible 下发（playbooks#1013、#1014）；Flux 仅负责集群内资源。
- 2026-11-13 sit-k3s-v6：发现手工防火墙 `sit-k3s-guard`（违反本 ADR），已临时修复放行 Pod 网段接口，待收归 playbooks firewall 角色并由 GitOps 声明规则。
