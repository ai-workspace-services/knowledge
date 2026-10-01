# 多云身份 Bootstrap 与状态契约

> 操作命令见 [Cloud Bootstrap TLDR](../../04-infra-platform/public-cloud-iaas/cloud-oidc-bootstrap-tldr.zh.md)。

## 统一入口

GitOps 声明环境、项目、云、真实账号和 workspace；敏感值从 Vault KV 读取。Terraform 使用同一套 S3 兼容状态参数，不把访问密钥写进 GitOps 或 backend 模板：

```text
kv/data/CICD/<env>/iac_state
  TF_STATE_ENDPOINT
  TF_STATE_BUCKET
  TF_STATE_ACCESS_KEY
  TF_STATE_SECRET_KEY
  TF_STATE_REGION

terraform/<env>/<project>/<cloud>/<account>/<workspace>/terraform.tfstate
terraform/<env>/<project>/<cloud>/<account>/<workspace>/terraform.tfstate.tflock
```

`account` 是实际云账号或项目 ID，不使用 `primary` 等别名。这里的 `<workspace>` 指状态隔离用的资源命名空间；每个命名空间有独立 state 和锁。Provider 身份与 state 凭据分开加载；Bootstrap 凭据只用于建立初始信任，不能替代运行时身份。上述五级 key 是工作负载约定；身份 Bootstrap 可以使用独立的控制面 key。

## Provider 槽位

用户列出的范围为六个槽位，其中 UCloud/Ulighthost 共用一个现有资源纳管组。

| 槽位 | 运行时身份 / Vault 入口 | 本轮管理模式 | Bootstrap 完成判据 |
| --- | --- | --- | --- |
| AWS | GitHub OIDC → AWS STS；一次性恢复凭据在 `kv/data/CICD/<env>/aws-bootstrap` | Terraform | 对应账号信任策略生效；工作流无需长期 Access Key 即可 plan |
| GCP | GitHub OIDC → Vault JWT → Google WIF；一次性 `GCP_ACCESS_TOKEN` 在 `kv/data/CICD/<env>/gcp-bootstrap/<account>` | Terraform | WIF、Service Account、项目 IAM 与 Vault 运行时记录可用；plan 成功 |
| Azure | GitHub OIDC → Azure Federated Credential（目标设计） | Terraform 槽位预留 | 替换工作流中的占位 `client-id`、`tenant-id`、`subscription-id`，验证联合登录后才允许 apply |
| Akamai Cloud/Linode | GitHub OIDC → Vault JWT → `kv/data/CICD/<env>/akamai-cloud/<account>` 的 `LINODE_TOKEN` | Terraform | Vault Role 绑定 repo/workflow/ref/environment；Linode API 与 plan 成功 |
| UCloud/Ulighthost | Vault KV + external inventory/Playbook；Ulighthost 不依赖原生 Terraform OIDC | 本轮 Hybrid 节点复用 existing | 主机事实、归属、SSH、CMDB 校验；existing 声明不得进入 Terraform apply/destroy |
| Vultr Cloud/VPS | GitHub OIDC → Vault JWT → `kv/data/CICD/<env>` 的 `VULTR_API_KEY` | Terraform | 独立 state、Vault 策略和 provider plan 成功 |

UCloud 已有单独的 Terraform 声明、凭据 bootstrap 和 IaC 工作流，不能笼统标为“不支持 Terraform”。上表的 existing 边界仅适用于本轮选择复用的节点，尤其是 Ulighthost；是否执行 Terraform 由具体 GitOps 声明的 `management_mode` 决定。已有资源改由 Terraform 管理时，须显式修改声明，并完成 state 导入与无漂移 plan。Azure 目前有编排入口，但登录参数仍为占位值。

## GCP `open-platform-shared` 特例

共享项目独立于 `open-platform-uat`、`open-platform-prod`。GitOps 分别声明 Vault、Observability、IAM 三个 workspace：

```text
terraform/shared/open-platform-shared/gcp-cloud/open-platform-shared/open-platform-shared-vault/terraform.tfstate
terraform/shared/open-platform-shared/gcp-cloud/open-platform-shared/open-platform-shared-observability/terraform.tfstate
terraform/shared/open-platform-shared/gcp-cloud/open-platform-shared/open-platform-shared-iam/terraform.tfstate
```

OIDC 声明位于 `gitops/resources/svc.plus/shared/gcp/github-actions-oidc-open-platform-shared.yaml`，其自身的控制面 state key 为 `platform-ops-toolkit/shared/open-platform-shared/gcp-oidc-bootstrap/terraform.tfstate`，不属于上面三个工作负载 state。一次性输入位于 `kv/data/CICD/shared/gcp-bootstrap/open-platform-shared`；GCP OIDC 工作流写入的运行时记录位于 `kv/data/shared/platform/oidc/open-platform-shared`。生产 `vault-prod-0` 属于旧项目的迁移源；新 shared state 不导入或修改这台主机。

## 上线门槛

1. 审 GitOps 账号、workspace、管理模式和区域。
2. Bootstrap Role 与 Runtime Role 分离，策略仅覆盖对应环境与账号。
3. Bootstrap 先 `plan` 再显式 `apply`，验证运行时 OIDC 登录与 state 初始化。
4. 逐 workspace 核对 state key、锁和变更，审批后才 `apply`。
5. existing 资源只输出 inventory/CMDB；改为 Terraform 管理前必须显式导入。

实现入口：[Toolkit cloud bootstrap](https://github.com/ai-workspace-infra/platform-ops-toolkit/tree/main/scripts/cloud/bootstrap)、[GCP OIDC workflow](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/main/.github/workflows/gcp-oidc-bootstrap.yml)、[GitOps shared 声明](https://github.com/ai-workspace-infra/gitops/tree/main/resources/svc.plus/shared/gcp)。
