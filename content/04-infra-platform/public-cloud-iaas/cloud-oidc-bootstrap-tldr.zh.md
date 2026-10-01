# Cloud OIDC Bootstrap：操作 TLDR

> 身份和 state 的跨云契约见 [多云身份 Bootstrap 与状态契约](../../02-iac-devops/cloud-infrastructure-devsecops-baseline/11-cloud-oidc-bootstrap-contract.zh.md)。以下命令在 `platform-ops-toolkit` 仓库根目录执行。不要把 Token、ADC 文件或 Vault Secret 写进 Git、Issue、日志或聊天。

## 1. GCP shared 项目：本机 ADC → Vault → GitHub OIDC

`gcloud auth login` 与 ADC 是不同的本地凭据。浏览器里选择有权限访问 `open-platform-shared` 的账号；验证命令只检查退出码，不显示 Token。

```bash
cd /Users/shenlan/workspaces/ai-workspace-infra/platform-ops-toolkit
export VAULT_ADDR='https://vault.svc.plus'
gcloud auth application-default login
gcloud auth application-default print-access-token >/dev/null
```

先确认本机 Vault 已登录，再使用带输入校验的脚本写入一次性短期凭据。运行此脚本的 Google 身份还须具有目标项目中创建 WIF、Service Account 和项目 IAM 绑定所需权限。脚本在 ADC 失效时停止，不会把空 Token 写入 KV；不要使用未检查退出码的 `export GCP_ACCESS_TOKEN="$(gcloud …)"` 加 `vault kv put` 组合。

```bash
vault token lookup >/dev/null
GCP_ENVIRONMENT=shared \
GCP_ACCOUNT_ID=open-platform-shared \
GCP_PROJECT_ID=open-platform-shared \
bash scripts/cloud/bootstrap/gcp/bootstrap_gcp_auth_kv.sh

GCP_BOOTSTRAP_ACTION=check \
GCP_ENVIRONMENT=shared \
GCP_ACCOUNT_ID=open-platform-shared \
GCP_PROJECT_ID=open-platform-shared \
bash scripts/cloud/bootstrap/gcp/bootstrap_gcp_auth_kv.sh
```

Vault Bootstrap Role 和 Runtime Role 是两个独立角色。首次建立时由已登录 Vault 的管理员执行：

```bash
bash scripts/create_vault_service_repo_roles.sh --apply \
  --role github-actions-platform-ops-toolkit-shared-gcp-bootstrap-open-platform-shared
bash scripts/create_vault_service_repo_roles.sh --apply \
  --role github-actions-platform-ops-toolkit-shared-gcp-oidc-open-platform-shared
```

角色和短期凭据均可用后尽快运行；先 `plan`，核对工作流预期变更，再执行 `apply`。短期 Token 过期时重新运行上面的 KV 脚本，不复用旧值。

```bash
gh workflow run gcp-oidc-bootstrap.yml \
  --repo ai-workspace-infra/platform-ops-toolkit --ref main \
  -f environment=shared -f action=plan \
  -f gcp_oidc_manifest=resources/svc.plus/shared/gcp/github-actions-oidc-open-platform-shared.yaml

gh workflow run gcp-oidc-bootstrap.yml \
  --repo ai-workspace-infra/platform-ops-toolkit --ref main \
  -f environment=shared -f action=apply \
  -f gcp_oidc_manifest=resources/svc.plus/shared/gcp/github-actions-oidc-open-platform-shared.yaml
```

确认 Bootstrap `apply` 成功、运行时 Vault 记录存在且 GCP WIF 可登录后，才运行 UAT Daily Snapshot。OIDC Bootstrap 使用独立控制面 state；Daily Snapshot 再按 Vault → Observability → IAM 顺序处理三个工作负载 state，之后调度 UAT Hybrid。默认 shared action 为 `apply`，此操作可能真实创建云资源。

```bash
gh workflow run daily-main-snapshot.yaml \
  --repo ai-workspace-infra/platform-ops-toolkit --ref main \
  -f deploy_env=uat
```

## 2. 其他云的入口速查

| 云 | Bootstrap 入口 | 当前注意事项 |
| --- | --- | --- |
| AWS | `scripts/cloud/bootstrap/aws/`、`aws-oidc-bootstrap.yml`；一次性 `kv/CICD/<env>/aws-bootstrap` | 日常运行用 GitHub OIDC → STS；bootstrap/recovery 支持临时 STS 会话，不要求根账号凭据 |
| Azure | `selfhost-orchestrator.yml` 中 `azure/login@v2` | 当前 ID 为占位值；先创建 Federated Credential 并替换配置，尚不能宣称可用 |
| Akamai Cloud/Linode | `scripts/cloud/bootstrap/Akamai-Cloud/`；`kv/CICD/<env>/akamai-cloud/<真实账号>` | Provider 使用 `LINODE_TOKEN`；GitHub OIDC 用于登录 Vault，不代表 Linode 原生 OIDC |
| UCloud/Ulighthost | GitOps existing 声明、Vault 主机事实、external inventory/Playbook | 本轮复用的 Ulighthost 等 existing 节点不执行 Terraform；UCloud 另有 Terraform 声明和工作流，须按具体 `management_mode` 路由 |
| Vultr Cloud/VPS | `scripts/cloud/bootstrap/vultr-VPS/`；`kv/CICD/<env>` 的 `VULTR_API_KEY` | Vault JWT 提供运行时 Token；与 `kv/CICD/<env>/iac_state` 的 state 凭据分离 |

所有 Terraform 云共用 `kv/data/CICD/<env>/iac_state` 的 `TF_STATE_*` 字段，以及 `terraform/<env>/<project>/<cloud>/<account>/<workspace>/terraform.tfstate` 的五级 key。账号填真实名称或 ID，不能用 `primary` 占位。

参考：[Google 本机 ADC 设置](https://docs.cloud.google.com/docs/authentication/set-up-adc-local-dev-environment)、[Toolkit bootstrap 目录](https://github.com/ai-workspace-infra/platform-ops-toolkit/tree/main/scripts/cloud/bootstrap)。
