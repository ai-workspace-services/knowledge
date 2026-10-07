## 自动生成：流水线与调用盘点

证据等级：**源码盘点**。人工映射的路径存在检查不等于调用、运行或业务验收。

| 仓库 | 固定 SHA |
| --- | --- |
| platform-ops-toolkit | `feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8` |
| playbooks | `2dd12e6e12ce8b0b07bdae8290f96257fde67f07` |
| iac_modules | `c128442c35024f75bcd9f9cb771dc882d9d4d2ed` |
| gitops | `437014ff401e7a0a122725945c093a71ab756dd1` |

| 流水线 | 触发 | jobs | steps 定义 | 输出 |
| --- | --- | --- | --- | --- |
| [Daily Main Snapshot](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/daily-main-snapshot.yaml) | schedule、workflow_dispatch; cron=['0 16 * * *'] | 6 | 33 | 构建状态、环境派发回执、最终汇总 |

### Jobs 汇总

| Job | 任务 | 依赖 | 输入 | 源码 outputs | 结果／制品 | 条件 | 矩阵 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| resolve-snapshot-tag | 确定统一快照 tag | — | deploy_env、snapshot_tag、snapshot_source_ref、repositories | {"snapshot_tag": "${{ steps.resolve.outputs.snapshot_tag }}"} | snapshot_tag | — | — |
| snapshot | 按组织创建 tag、构建并记录状态 | resolve-snapshot-tag | 统一 tag、源码 ref、构建清单、组织矩阵 | — | daily-snapshot-status-<organization> | — | {"organization": ["ai-workspace-infra", "ai-workspace-lab", "ai-workspace-services", "ai-workspace-xstream"]} |
| resolve-built-snapshot-tag | 确认完成的统一版本 | ["resolve-snapshot-tag", "snapshot"] | 各组织状态 artifact | {"snapshot_tag": "${{ steps.resolve.outputs.snapshot_tag }}"} | 完成的 snapshot_tag | ${{ always() && needs.resolve-snapshot-tag.result == 'success' && needs.snapshot.result == 'success' && (inputs.repositories &#124;&#124; '') == '' }} | — |
| shared-readiness | 检查 Shared 服务 | resolve-built-snapshot-tag | Vault/Grafana/IAM endpoint、issuer、超时 | — | readiness 成功/失败 | ${{ always() && needs.resolve-built-snapshot-tag.result == 'success' }} | — |
| dispatch-environment | 读取 GitOps，派发并等待环境部署 | ["resolve-built-snapshot-tag", "shared-readiness"] | 完成的 tag、环境、GitOps topology | — | run_url、environment-dispatch-<environment> | ${{ always() && needs.resolve-built-snapshot-tag.result == 'success' && needs.shared-readiness.result == 'success' && (inputs.repositories &#124;&#124; '') == '' && matrix.environment == (inputs.deploy_env &#124;&#124; 'uat') }} | {"include": [{"environment": "sit", "name": "Serverless Orchestrator", "operation": "deploy", "target_domains": "web-saas", "topology_mode": "serverless", "workflow": "serverless-orchestrator.yml"}, {"environment": "uat", "name": "Hybrid Orchestrator", "operation": "deploy", "target_domains": "all", "topology_mode": "hybrid", "workflow": "hybrid-orchestrator.yml"}]} |
| snapshot-summary | 汇总构建及环境派发 | ["resolve-snapshot-tag", "snapshot", "resolve-built-snapshot-tag", "shared-readiness", "dispatch-environment"] | 组织状态、环境派发回执 | — | daily-snapshot-summary.json、environment-dispatch-summary.json、Actions Summary | ${{ always() && needs.resolve-snapshot-tag.result == 'success' && needs.snapshot.result != 'skipped' && needs.resolve-built-snapshot-tag.result != 'failure' && needs.shared-readiness.result != 'failure' && needs.dispatch-environment.result != 'failure' }} | — |

### Steps 关联汇总

#### 1. `resolve-snapshot-tag`

| Step | 任务 | Action uses／脚本 run | Playbook／Role | IaC | 输出／验证 | 条件 |
| --- | --- | --- | --- | --- | --- | --- |
| 1.1 | Checkout repository | uses: `actions/checkout@v7` | — | — | 工作目录和控制脚本可用 | — |
| 1.2 | Load GitHub App private key from Vault | uses: `hashicorp/vault-action@v4` | — | — | 运行时授权成功；不持久化或输出私钥 | — |
| 1.3 | Create GitHub App installation token for infra | uses: `actions/create-github-app-token@v3` | — | — | infra 组织访问权限 | — |
| 1.4 | Create GitHub App installation token for lab | uses: `actions/create-github-app-token@v3` | — | — | lab 组织访问权限 | — |
| 1.5 | Create GitHub App installation token for services | uses: `actions/create-github-app-token@v3` | — | — | services 组织访问权限 | — |
| 1.6 | Create GitHub App installation token for xstream | uses: `actions/create-github-app-token@v3` | — | — | xstream 组织访问权限 | — |
| 1.7 | Resolve snapshot tag across all organizations | run: [.github/scripts/snapshots/resolve-snapshot-tag.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/snapshots/resolve-snapshot-tag.sh) | — | — | 输出合法统一 tag；范围/环境不符时停止 | — |

#### 2. `snapshot`

| Step | 任务 | Action uses／脚本 run | Playbook／Role | IaC | 输出／验证 | 条件 |
| --- | --- | --- | --- | --- | --- | --- |
| 2.1 | Checkout repository | uses: `actions/checkout@v7` | — | — | 工作目录和控制脚本可用 | — |
| 2.2 | Load GitHub App private key from Vault | uses: `hashicorp/vault-action@v4` | — | — | 运行时授权成功；不持久化或输出私钥 | — |
| 2.3 | Create GitHub App installation token | uses: `actions/create-github-app-token@v3` | — | — | 当前组织权限 | — |
| 2.4 | Create cross-repository main snapshot | run: [.github/scripts/snapshots/tag-daily-main-snapshot.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/snapshots/tag-daily-main-snapshot.sh) | — | — | tag、构建结果和制品状态可关联 | ${{ inputs.repositories == '' &#124;&#124; contains(inputs.repositories, matrix.organization) }} |
| 2.5 | Trigger XConnect multi-platform release | run: gh api repository_dispatch（仅 xstream） | — | — | 仅证明 repository_dispatch 已提交；未等待发布完成 | ${{ success() && matrix.organization == 'ai-workspace-xstream' }} |
| 2.6 | Upload snapshot status | uses: `actions/upload-artifact@v7` | — | — | 组织状态 artifact；失败时也尝试上传 | always() |

#### 3. `resolve-built-snapshot-tag`

| Step | 任务 | Action uses／脚本 run | Playbook／Role | IaC | 输出／验证 | 条件 |
| --- | --- | --- | --- | --- | --- | --- |
| 3.1 | Checkout repository | uses: `actions/checkout@v7` | — | — | 工作目录和控制脚本可用 | — |
| 3.2 | Download all organization snapshot status artifacts | uses: `actions/download-artifact@v8` | — | — | 组织状态集合完整 | — |
| 3.3 | Resolve immutable completed snapshot tag | run: [.github/scripts/snapshots/resolve-daily-snapshot-tag.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/snapshots/resolve-daily-snapshot-tag.sh) | — | — | 解析完成的统一 tag；指定 repositories 时跳过 | — |

#### 4. `shared-readiness`

| Step | 任务 | Action uses／脚本 run | Playbook／Role | IaC | 输出／验证 | 条件 |
| --- | --- | --- | --- | --- | --- | --- |
| 4.1 | Checkout repository | uses: `actions/checkout@v7` | — | — | 工作目录和控制脚本可用 | — |
| 4.2 | Check Shared platform readiness (read-only) | run: [.github/scripts/snapshots/check-shared-readiness.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/snapshots/check-shared-readiness.sh) | B11 待新增 owner 接口；当前仍执行 Toolkit 探针 | — | Vault initialized 且 unsealed；Grafana DB ok；IAM issuer 匹配 | — |

#### 5. `dispatch-environment`

| Step | 任务 | Action uses／脚本 run | Playbook／Role | IaC | 输出／验证 | 条件 |
| --- | --- | --- | --- | --- | --- | --- |
| 5.1 | Checkout repository | uses: `actions/checkout@v7` | — | — | 工作目录和控制脚本可用 | — |
| 5.2 | Load GitHub App private key from Vault | uses: `hashicorp/vault-action@v4` | — | — | 运行时授权成功；不持久化或输出私钥 | — |
| 5.3 | Create GitHub App installation token | uses: `actions/create-github-app-token@v3` | — | — | 读取 GitOps 和派发权限 | — |
| 5.4 | Checkout selected GitOps topology | uses: `actions/checkout@v7` | — | — | 获得对应环境和模式的拓扑 | — |
| 5.5 | Resolve target domain from GitOps | run: [.github/scripts/snapshots/resolve-dispatch-gitops-target.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/snapshots/resolve-dispatch-gitops-target.sh) | — | — | target_domain_base；环境和模式校验 | — |
| 5.6 | Dispatch ${{ matrix.name }} | run: [.github/scripts/snapshots/dispatch-environment-combined.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/snapshots/dispatch-environment-combined.sh) | B01—B10 下游条件调用 | I01—I09 下游条件调用 | 精确子运行 URL、终态、环境和 tag；按目标选择执行 | — |
| 5.7 | Write dispatch receipt | run: jq 写脱敏派发回执 | — | — | 环境、操作、workflow、tag、run_url、结果 | always() |
| 5.8 | Upload dispatch receipt | uses: `actions/upload-artifact@v7` | — | — | 环境回执 artifact | always() |

#### 6. `snapshot-summary`

| Step | 任务 | Action uses／脚本 run | Playbook／Role | IaC | 输出／验证 | 条件 |
| --- | --- | --- | --- | --- | --- | --- |
| 6.1 | Checkout repository | uses: `actions/checkout@v7` | — | — | 工作目录和控制脚本可用 | — |
| 6.2 | Download all organization snapshot status artifacts | uses: `actions/download-artifact@v8` | — | — | 构建状态集合 | — |
| 6.3 | Publish unified snapshot matrix summary | run: [.github/scripts/snapshots/aggregate-daily-snapshot-status.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/snapshots/aggregate-daily-snapshot-status.sh) | — | — | 构建汇总 JSON 和 Actions Summary | — |
| 6.4 | Download environment dispatch receipts | uses: `actions/download-artifact@v8` | — | — | 部署未跳过时获得回执 | ${{ needs.dispatch-environment.result != 'skipped' }} |
| 6.5 | Publish environment dispatch summary | run: [.github/scripts/snapshots/aggregate-environment-dispatch-status.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/snapshots/aggregate-environment-dispatch-status.sh) | — | — | 环境派发汇总 JSON | ${{ needs.dispatch-environment.result != 'skipped' }} |
| 6.6 | Upload environment snapshot summary | uses: `actions/upload-artifact@v7` | — | — | daily-snapshot-summary-<environment> artifact | always() |
| 6.7 | Fail when the selected environment dispatch failed | run: exit 1 | — | — | 失败状态；当前外层 job 条件会阻止部分失败路径进入汇总 | ${{<br>  needs.snapshot.result == 'failure' &#124;&#124;<br>  needs.shared-readiness.result == 'failure' &#124;&#124;<br>  needs.dispatch-environment.result == 'failure'<br>}} |

### 下游 workflow 范围（人工登记，非全链路可达性证明）

| 路径 | 用途 |
| --- | --- |
| [.github/workflows/daily-main-snapshot.yaml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/daily-main-snapshot.yaml) | Daily 入口、构建、readiness、派发和汇总 |
| [.github/workflows/hybrid-orchestrator.yml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/hybrid-orchestrator.yml) | UAT 矩阵编排；并非所有 lane 都执行 |
| [.github/workflows/selfhost-orchestrator.yml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/selfhost-orchestrator.yml) | 资源、CMDB、主机和服务交付；含 Daily 不使用的 PROD 条件分支 |
| [.github/workflows/serverless-orchestrator.yml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/serverless-orchestrator.yml) | SIT/UAT Serverless；含其他操作与环境分支 |
| [.github/workflows/external-inventory-state.yml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/external-inventory-state.yml) | TW/PH existing inventory / State 路径 |
| [.github/workflows/xconnect-zero-cloud.yaml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/xconnect-zero-cloud.yaml) | 显式迁移分支；普通 Daily 不启用 |
| [.github/workflows/environment-data-operations.yml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/environment-data-operations.yml) | 数据操作薄调用与 owner workflow 接入 |
| [.github/workflows/environment-upgrade-ci.yml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/environment-upgrade-ci.yml) | 数据升级/rehearsal 调用入口 |

### 下游 Role／IaC 映射（人工登记 + 固定版本路径检查）

| ID | 任务 | Owner | 入口／实现 | 目标接入状态 | 输入 | 输出／验证 | 路径检查 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| I01 | GCP Web SaaS 主机/网络/数据盘 | IaC Modules | [iac_modules/terraform-hcl-standard/gcp-cloud/modules/project](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/project)<br>[iac_modules/terraform-hcl-standard/gcp-cloud/modules/network](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/network)<br>[iac_modules/terraform-hcl-standard/gcp-cloud/modules/spot_vm](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/spot_vm)<br>[iac_modules/terraform-hcl-standard/gcp-cloud/modules/persistent_data_disk](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/persistent_data_disk) | 模块现有；待 owner workflow 接入 | GitOps resources/onwalk.net/uat/gcp/web-saas.yaml、环境、账户、State | 资源 ID、State、CMDB；与目标声明一致 | 路径存在；不证明调用 |
| I02 | GCP US Agent Proxy | IaC Modules | [iac_modules/terraform-hcl-standard/gcp-cloud/modules/project](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/project)<br>[iac_modules/terraform-hcl-standard/gcp-cloud/modules/network](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/network)<br>[iac_modules/terraform-hcl-standard/gcp-cloud/modules/spot_vm](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/spot_vm) | 模块现有；待 owner workflow 接入 | US lane 声明、账户、State | US 实例身份、网络、CMDB | 路径存在；不证明调用 |
| I03 | AWS JP Agent Proxy | IaC Modules | [iac_modules/terraform-hcl-standard/aws-cloud/modules/ec2](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/aws-cloud/modules/ec2)<br>[iac_modules/terraform-hcl-standard/aws-cloud/modules/spot_ec2](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/aws-cloud/modules/spot_ec2) | 当前 JP on-demand 用 ec2；Spot 声明才用 spot_ec2；待 owner workflow 接入 | JP lane 声明、AWS 身份、State | JP 实例、地址、CMDB | 路径存在；不证明调用 |
| I04 | Akamai SG Agent Proxy | IaC Modules | [iac_modules/terraform-hcl-standard/akamai-cloud/modules/compute](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/akamai-cloud/modules/compute)<br>[iac_modules/terraform-hcl-standard/akamai-cloud/modules/storage](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/akamai-cloud/modules/storage)<br>[iac_modules/terraform-hcl-standard/akamai-cloud/templates/hosts.tf.j2](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/akamai-cloud/templates/hosts.tf.j2) | compute 现有；storage 条件使用；防火墙由模板生成；待 owner workflow 接入 | SG lane 声明 | SG 实例、防火墙、CMDB | 路径存在；不证明调用 |
| I05 | TW/PH existing 资源事实 | IaC Modules | [platform-ops-toolkit/scripts/iac/write_external_inventory.py](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/scripts/iac/write_external_inventory.py)<br>[platform-ops-toolkit/.github/workflows/external-inventory-state.yml](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/workflows/external-inventory-state.yml) | LEGACY Toolkit 执行；待迁入 IaC；不创建外部主机 | existing 声明、环境、账户、State | existing inventory/State；不等于服务部署 | 路径存在；不证明调用 |
| I06 | Registry 基础资源/制品晋级 | IaC Modules | [iac_modules/terraform-hcl-standard/gcp-cloud/modules/artifact_registry](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/artifact_registry)<br>[iac_modules/scripts/pipeline/artifact-registry-promote.sh](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/scripts/pipeline/artifact-registry-promote.sh)<br>[iac_modules/scripts/pipeline/artifact-registry-wait.sh](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/scripts/pipeline/artifact-registry-wait.sh) | 现有脚本由 Toolkit 调用；待 owner workflow 接入 | 源 digest、目标 Registry、环境 | 目标 digest 可核对 | 路径存在；不证明调用 |
| I07 | Cloud Run 单服务部署 | IaC Modules | [iac_modules/terraform-hcl-standard/gcp-cloud/modules/cloud_run](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/terraform-hcl-standard/gcp-cloud/modules/cloud_run)<br>[platform-ops-toolkit/scripts/serverless_uat/deploy_cloudrun_services.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/scripts/serverless_uat/deploy_cloudrun_services.sh) | 模块存在但当前部署仍走 Toolkit 脚本；接入需单独实施 | 服务声明、镜像 digest、配置引用 | revision、实际运行 digest | 路径存在；不证明调用 |
| I08 | Cloudflare Worker/Pages 发布 | IaC Modules | [platform-ops-toolkit/.github/scripts/serverless/run_cloudflare_target.sh](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/feb5bc18b5ae6a90784d324e5b2fb8df4251e6c8/.github/scripts/serverless/run_cloudflare_target.sh) | 当前 Toolkit 执行；未确认完整替换模块；待 owner 接入 | 发布包、checksum、账户、目标 | deployment ID、制品 checksum | 路径存在；不证明调用 |
| I09 | Cloudflare 域名/DNS | IaC Modules | [iac_modules/.github/workflows/cloudflare-serverless-domains.yml](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/.github/workflows/cloudflare-serverless-domains.yml)<br>[iac_modules/.github/actions/cloudflare-serverless-domains/action.yml](https://github.com/ai-workspace-infra/iac_modules/blob/c128442c35024f75bcd9f9cb771dc882d9d4d2ed/.github/actions/cloudflare-serverless-domains/action.yml) | 已有固定 SHA owner workflow 调用；实际消费 SHA 见 uses 表 | environment、gitops_ref、dns_mode | 域名归属、DNS 模式与执行结果 | 路径存在；不证明调用 |
| B01 | Web SaaS 主机配置/交付 | Playbooks Roles | [playbooks/setup-web-saas-domain.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/setup-web-saas-domain.yml)<br>[playbooks/roles/vhosts/web_saas_host_config](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/web_saas_host_config)<br>[playbooks/roles/vhosts/Doco-CD](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/Doco-CD) | Playbook/Role 现有；不把 pull-only CD 观察当成全部部署 | inventory、环境、版本、配置 | 主机配置、实际版本、服务交付状态 | 路径存在；不证明调用 |
| B02 | Caddy 证书恢复 | Playbooks Roles | [playbooks/caddy_certificate_restore.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/caddy_certificate_restore.yml)<br>[playbooks/roles/docker/caddy_certificate_restore](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/docker/caddy_certificate_restore) | 下游已有执行；待收敛至固定 SHA owner workflow | 单一目标、证书材料引用 | 目标正确、证书有效 | 路径存在；不证明调用 |
| B03 | 区域 Agent Proxy 部署 | Playbooks Roles | [playbooks/setup-agent-proxy-domain.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/setup-agent-proxy-domain.yml)<br>[playbooks/deploy_xray_proxy_server.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/deploy_xray_proxy_server.yml)<br>[playbooks/roles/vhosts/caddy](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/caddy)<br>[playbooks/roles/vhosts/vault-agent-tls](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/vault-agent-tls)<br>[playbooks/roles/vhosts/tky-proxy](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/tky-proxy)<br>[playbooks/roles/vhosts/agent-proxy](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/agent-proxy) | 入口/Role 现有；TLS Role 条件执行 | lane inventory、精确组件版本、配置引用 | Caddy/Xray/Agent 状态及版本 | 路径存在；不证明调用 |
| B04 | Xray Exporter | Playbooks Roles | [playbooks/deploy_xray_exporter.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/deploy_xray_exporter.yml)<br>[playbooks/roles/vhosts/xray-exporter](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/xray-exporter) | 现有入口/Role | inventory、exporter 版本及配置 | 进程及指标 | 路径存在；不证明调用 |
| B05 | Observability Agent | Playbooks Roles | [playbooks/deploy_observability_agent.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/deploy_observability_agent.yml)<br>[playbooks/roles/vhosts/node_exporter](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/node_exporter)<br>[playbooks/roles/vhosts/process_exporter](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/process_exporter)<br>[playbooks/roles/vhosts/blackbox_exporter](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/blackbox_exporter)<br>[playbooks/roles/vhosts/vector-agent](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/vector-agent) | 按条件执行；下列 Role 非全部必跑 | inventory、采集目标和配置 | 采集器、指标/日志链路 | 路径存在；不证明调用 |
| B06 | Web SaaS 部署后检查 | Playbooks Roles | [playbooks/verify_web_saas_post_deploy.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/verify_web_saas_post_deploy.yml)<br>[playbooks/roles/vhosts/web_saas_post_deploy_readiness](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/web_saas_post_deploy_readiness) | 现有入口/Role | 精确主机、readiness 参数 | 服务 readiness | 路径存在；不证明调用 |
| B07 | Agent Proxy DNS 后检查 | Playbooks Roles | [playbooks/verify_agent_proxy_post_dns.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/verify_agent_proxy_post_dns.yml)<br>[playbooks/roles/vhosts/agent_proxy_post_dns_readiness](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/vhosts/agent_proxy_post_dns_readiness) | 现有入口/Role | 精确目标、域名和检查参数 | DNS 后入口及服务链路 | 路径存在；不证明调用 |
| B08 | 数据备份 | Playbooks Roles | [playbooks/web-saas-backup.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/web-saas-backup.yml)<br>[playbooks/roles/site_migration](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/site_migration) | 现有；site_migration tasks_from=extract；实际链路需按数据操作选择 | 源目标、备份配置、release 身份 | 备份与完整性 | 路径存在；不证明调用 |
| B09 | 数据恢复 | Playbooks Roles | [playbooks/web-saas-restore.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/web-saas-restore.yml)<br>[playbooks/roles/site_migration](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/roles/site_migration) | 现有；site_migration tasks_from=load；独立恢复门槛 | 备份材料、精确恢复目标 | 恢复结果与数据检查 | 路径存在；不证明调用 |
| B10 | Serverless 数据库操作 | Playbooks Roles | [playbooks/.github/workflows/serverless-database-operations.yml](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/.github/workflows/serverless-database-operations.yml)<br>[playbooks/scripts/data_operations/serverless](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/scripts/data_operations/serverless)<br>[playbooks/scripts/data_operations/database/create_release_checkpoint.sh](https://github.com/ai-workspace-infra/playbooks/blob/2dd12e6e12ce8b0b07bdae8290f96257fde67f07/scripts/data_operations/database/create_release_checkpoint.sh) | owner workflow 现有；并非全部封装为 Role | 数据库目标、操作、schema 版本、SQL hash | checkpoint、schema version、迁移回执 | 路径存在；不证明调用 |
| B11 | Shared readiness | Playbooks Roles | 待新增，名称未确定 | 待新增；当前探针仍在 Toolkit；不得自动宣称已迁移 | Vault/Grafana/IAM endpoint、issuer、timeout | 三项探针证据；Toolkit 判断放行 | 待新增 |

### 源码实际 uses（含条件分支；不等于 Daily 必跑）

| Workflow | Job | 位置 | 实际 uses |
| --- | --- | --- | --- |
| .github/workflows/daily-main-snapshot.yaml | resolve-snapshot-tag | 1 | `actions/checkout@v7` |
| .github/workflows/daily-main-snapshot.yaml | resolve-snapshot-tag | 2 | `hashicorp/vault-action@v4` |
| .github/workflows/daily-main-snapshot.yaml | resolve-snapshot-tag | 3 | `actions/create-github-app-token@v3` |
| .github/workflows/daily-main-snapshot.yaml | resolve-snapshot-tag | 4 | `actions/create-github-app-token@v3` |
| .github/workflows/daily-main-snapshot.yaml | resolve-snapshot-tag | 5 | `actions/create-github-app-token@v3` |
| .github/workflows/daily-main-snapshot.yaml | resolve-snapshot-tag | 6 | `actions/create-github-app-token@v3` |
| .github/workflows/daily-main-snapshot.yaml | snapshot | 1 | `actions/checkout@v7` |
| .github/workflows/daily-main-snapshot.yaml | snapshot | 2 | `hashicorp/vault-action@v4` |
| .github/workflows/daily-main-snapshot.yaml | snapshot | 3 | `actions/create-github-app-token@v3` |
| .github/workflows/daily-main-snapshot.yaml | snapshot | 6 | `actions/upload-artifact@v7` |
| .github/workflows/daily-main-snapshot.yaml | resolve-built-snapshot-tag | 1 | `actions/checkout@v7` |
| .github/workflows/daily-main-snapshot.yaml | resolve-built-snapshot-tag | 2 | `actions/download-artifact@v8` |
| .github/workflows/daily-main-snapshot.yaml | shared-readiness | 1 | `actions/checkout@v7` |
| .github/workflows/daily-main-snapshot.yaml | dispatch-environment | 1 | `actions/checkout@v7` |
| .github/workflows/daily-main-snapshot.yaml | dispatch-environment | 2 | `hashicorp/vault-action@v4` |
| .github/workflows/daily-main-snapshot.yaml | dispatch-environment | 3 | `actions/create-github-app-token@v3` |
| .github/workflows/daily-main-snapshot.yaml | dispatch-environment | 4 | `actions/checkout@v7` |
| .github/workflows/daily-main-snapshot.yaml | dispatch-environment | 8 | `actions/upload-artifact@v7` |
| .github/workflows/daily-main-snapshot.yaml | snapshot-summary | 1 | `actions/checkout@v7` |
| .github/workflows/daily-main-snapshot.yaml | snapshot-summary | 2 | `actions/download-artifact@v8` |
| .github/workflows/daily-main-snapshot.yaml | snapshot-summary | 4 | `actions/download-artifact@v8` |
| .github/workflows/daily-main-snapshot.yaml | snapshot-summary | 6 | `actions/upload-artifact@v7` |
| .github/workflows/hybrid-orchestrator.yml | preflight | 1 | `actions/checkout@v7` |
| .github/workflows/hybrid-orchestrator.yml | preflight | 2 | `actions/checkout@v7` |
| .github/workflows/hybrid-orchestrator.yml | data_operations | 1 | `actions/checkout@v7` |
| .github/workflows/hybrid-orchestrator.yml | resource_orchestration | 1 | `actions/checkout@v7` |
| .github/workflows/hybrid-orchestrator.yml | resource_orchestration | 2 | `actions/checkout@v7` |
| .github/workflows/hybrid-orchestrator.yml | resource_orchestration | 4 | `actions/upload-artifact@v7` |
| .github/workflows/hybrid-orchestrator.yml | verify | 1 | `actions/checkout@v7` |
| .github/workflows/hybrid-orchestrator.yml | verify | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 3 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 4 | `./.github/actions/configure-gcp-oidc` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 5 | `google-github-actions/setup-gcloud@v2` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 6 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 7 | `ai-workspace-infra/iac_modules/.github/actions/prod-selfhost-access@254dd6321449ab12b862220c8876b482d7032fcd` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 8 | `ai-workspace-infra/playbooks/.github/actions/prod-native-standby@c6a4cb6c54c7e6dd2d63c43767f44a228385312a` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 9 | `ai-workspace-infra/iac_modules/.github/actions/prod-selfhost-access@254dd6321449ab12b862220c8876b482d7032fcd` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 10 | `actions/upload-artifact@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_standby | 11 | `actions/upload-artifact@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 3 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 4 | `./.github/actions/configure-gcp-oidc` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 5 | `google-github-actions/setup-gcloud@v2` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 6 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 7 | `ai-workspace-infra/iac_modules/.github/actions/prod-selfhost-access@254dd6321449ab12b862220c8876b482d7032fcd` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 8 | `ai-workspace-infra/playbooks/.github/actions/prod-native-init@ff7b09e135f52301e7605dcdf6f3b303c9c2dd32` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 9 | `ai-workspace-infra/iac_modules/.github/actions/prod-selfhost-access@254dd6321449ab12b862220c8876b482d7032fcd` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 10 | `actions/upload-artifact@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_init | 11 | `actions/upload-artifact@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 3 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 4 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 5 | `./.github/actions/configure-gcp-oidc` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 6 | `google-github-actions/setup-gcloud@v2` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 7 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 8 | `ai-workspace-infra/iac_modules/.github/actions/prod-selfhost-access@254dd6321449ab12b862220c8876b482d7032fcd` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 9 | `ai-workspace-infra/playbooks/.github/actions/prod-native-billing-upgrade@ff7b09e135f52301e7605dcdf6f3b303c9c2dd32` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 10 | `ai-workspace-infra/iac_modules/.github/actions/prod-selfhost-access@254dd6321449ab12b862220c8876b482d7032fcd` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 11 | `actions/upload-artifact@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_billing | 12 | `actions/upload-artifact@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 3 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 4 | `./.github/actions/configure-gcp-oidc` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 5 | `google-github-actions/setup-gcloud@v2` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 6 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 7 | `ai-workspace-infra/iac_modules/.github/actions/prod-selfhost-access@254dd6321449ab12b862220c8876b482d7032fcd` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 8 | `ai-workspace-infra/playbooks/.github/actions/prod-full-business@7e9b16fa6c83a2dd8bafc22dca5870e06154253f` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 9 | `ai-workspace-infra/iac_modules/.github/actions/prod-selfhost-access@254dd6321449ab12b862220c8876b482d7032fcd` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 10 | `actions/upload-artifact@v4` |
| .github/workflows/selfhost-orchestrator.yml | native_prod_business | 11 | `actions/upload-artifact@v4` |
| .github/workflows/selfhost-orchestrator.yml | provision | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | provision | 4 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | provision | 9 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | provision | 10 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | provision | 11 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | provision | 13 | `aws-actions/configure-aws-credentials@v4` |
| .github/workflows/selfhost-orchestrator.yml | provision | 14 | `./.github/actions/configure-gcp-oidc` |
| .github/workflows/selfhost-orchestrator.yml | provision | 15 | `azure/login@v2` |
| .github/workflows/selfhost-orchestrator.yml | provision | 18 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | provision | 19 | `hashicorp/setup-terraform@v4` |
| .github/workflows/selfhost-orchestrator.yml | provision | 20 | `actions/setup-python@v6` |
| .github/workflows/selfhost-orchestrator.yml | provision | 43 | `actions/upload-artifact@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_xconnect_zero_uat | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 3 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 4 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 5 | `actions/create-github-app-token@v3` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 6 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 7 | `actions/download-artifact@v8` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 9 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 11 | `actions/cache@v6` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 12 | `./.github/actions/setup-deployment-runner` |
| .github/workflows/selfhost-orchestrator.yml | deploy_base | 14 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | capture_web_saas_baseline | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | capture_web_saas_baseline | 3 | `actions/download-artifact@v8` |
| .github/workflows/selfhost-orchestrator.yml | update_gitops_tags | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | update_gitops_tags | 2 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | update_gitops_tags | 3 | `actions/create-github-app-token@v3` |
| .github/workflows/selfhost-orchestrator.yml | update_gitops_tags | 4 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | initialize_empty_web_saas | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_web_saas | job | `ai-workspace-infra/playbooks/.github/workflows/web-saas-domain-cd.yaml@main` |
| .github/workflows/selfhost-orchestrator.yml | accept_web_saas_upgrade | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | switch_dns | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | switch_dns | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | switch_dns | 3 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | switch_dns | 5 | `actions/download-artifact@v8` |
| .github/workflows/selfhost-orchestrator.yml | switch_dns | 6 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | switch_dns | 7 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | switch_dns | 8 | `./.github/actions/setup-deployment-runner` |
| .github/workflows/selfhost-orchestrator.yml | switch_dns | 11 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | bootstrap_stripe_catalog | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | bootstrap_stripe_catalog | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | bootstrap_stripe_catalog | 5 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | observe_web_saas_after_dns | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | observe_web_saas_after_dns | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | observe_web_saas_after_dns | 3 | `actions/download-artifact@v8` |
| .github/workflows/selfhost-orchestrator.yml | observe_web_saas_after_dns | 4 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | observe_web_saas_after_dns | 5 | `./.github/actions/setup-deployment-runner` |
| .github/workflows/selfhost-orchestrator.yml | observe_agent_proxy_after_dns | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | observe_agent_proxy_after_dns | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | observe_agent_proxy_after_dns | 3 | `actions/download-artifact@v8` |
| .github/workflows/selfhost-orchestrator.yml | observe_agent_proxy_after_dns | 4 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | observe_agent_proxy_after_dns | 5 | `./.github/actions/setup-deployment-runner` |
| .github/workflows/selfhost-orchestrator.yml | deployment_summary | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_infra_platform | job | `ai-workspace-infra/playbooks/.github/workflows/open-platform-domain-cd.yaml@main` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy | 3 | `actions/download-artifact@v8` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy | 5 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy | 6 | `actions/cache@v6` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy | 7 | `./.github/actions/setup-deployment-runner` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy_non_iac | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy_non_iac | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy_non_iac | 3 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy_non_iac | 4 | `actions/download-artifact@v8` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy_non_iac | 6 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy_non_iac | 8 | `./.github/actions/setup-deployment-runner` |
| .github/workflows/selfhost-orchestrator.yml | deploy_agent_proxy_non_iac | 16 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_ai_workspace | job | `ai-workspace-infra/playbooks/.github/workflows/ai-workspace-domain-cd.yaml@main` |
| .github/workflows/selfhost-orchestrator.yml | deploy_monitor_agent | 1 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_monitor_agent | 2 | `actions/checkout@v7` |
| .github/workflows/selfhost-orchestrator.yml | deploy_monitor_agent | 3 | `actions/download-artifact@v8` |
| .github/workflows/selfhost-orchestrator.yml | deploy_monitor_agent | 4 | `hashicorp/vault-action@v4` |
| .github/workflows/selfhost-orchestrator.yml | deploy_monitor_agent | 5 | `actions/cache@v6` |
| .github/workflows/selfhost-orchestrator.yml | deploy_monitor_agent | 6 | `./.github/actions/setup-deployment-runner` |
| .github/workflows/selfhost-orchestrator.yml | trigger_data_migration | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | preflight | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | preflight | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | preflight | 3 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | supabase | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | uat_accounts_schema_probe | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | uat_accounts_baseline | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | uat_accounts_schema_migration | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 5 | `hashicorp/vault-action@v4` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 6 | `actions/create-github-app-token@v3` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 7 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 8 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 10 | `google-github-actions/auth@v2` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 11 | `google-github-actions/setup-gcloud@v2` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 12 | `docker/setup-qemu-action@v3` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 13 | `docker/setup-buildx-action@v3` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 16 | `docker/build-push-action@v6` |
| .github/workflows/serverless-orchestrator.yml | cloud_run | 23 | `actions/upload-artifact@v7` |
| .github/workflows/serverless-orchestrator.yml | artifact_manifest | 1 | `actions/download-artifact@v8` |
| .github/workflows/serverless-orchestrator.yml | artifact_manifest | 3 | `actions/upload-artifact@v7` |
| .github/workflows/serverless-orchestrator.yml | cloudflare_ssr | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | cloudflare_ssr | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | cloudflare_ssr | 5 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | cloudflare_ssr | 6 | `actions/setup-node@v7` |
| .github/workflows/serverless-orchestrator.yml | cloudflare_ssr | 7 | `hashicorp/vault-action@v4` |
| .github/workflows/serverless-orchestrator.yml | cloudflare_ssr | 9 | `actions/upload-artifact@v7` |
| .github/workflows/serverless-orchestrator.yml | frontend_router | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | frontend_router | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | frontend_router | 5 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | frontend_router | 6 | `actions/setup-node@v7` |
| .github/workflows/serverless-orchestrator.yml | frontend_router | 7 | `hashicorp/vault-action@v4` |
| .github/workflows/serverless-orchestrator.yml | edge_gateway | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | edge_gateway | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | edge_gateway | 5 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | edge_gateway | 6 | `actions/setup-node@v7` |
| .github/workflows/serverless-orchestrator.yml | edge_gateway | 7 | `hashicorp/vault-action@v4` |
| .github/workflows/serverless-orchestrator.yml | static_pages | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | static_pages | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | static_pages | 5 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | static_pages | 6 | `actions/setup-node@v7` |
| .github/workflows/serverless-orchestrator.yml | static_pages | 7 | `hashicorp/vault-action@v4` |
| .github/workflows/serverless-orchestrator.yml | static_pages | 8 | `actions/download-artifact@v8` |
| .github/workflows/serverless-orchestrator.yml | serverless_domains_provider | job | `ai-workspace-infra/iac_modules/.github/workflows/cloudflare-serverless-domains.yml@a7ac40fb0c3e620bdec89edd72b172afefc1f2ee` |
| .github/workflows/serverless-orchestrator.yml | serverless_domains | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | serverless_domains | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | trigger_data_migration | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | stripe_catalog | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | stripe_catalog | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | stripe_catalog | 3 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | stripe_catalog | 7 | `hashicorp/vault-action@v4` |
| .github/workflows/serverless-orchestrator.yml | destroy | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | destroy | 2 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | destroy | 4 | `hashicorp/vault-action@v4` |
| .github/workflows/serverless-orchestrator.yml | destroy | 6 | `google-github-actions/auth@v2` |
| .github/workflows/serverless-orchestrator.yml | destroy | 7 | `google-github-actions/setup-gcloud@v2` |
| .github/workflows/serverless-orchestrator.yml | verify | 1 | `actions/checkout@v7` |
| .github/workflows/serverless-orchestrator.yml | verify | 2 | `hashicorp/vault-action@v4` |
| .github/workflows/serverless-orchestrator.yml | console_release_metadata | 2 | `actions/upload-artifact@v7` |
| .github/workflows/external-inventory-state.yml | sync | 1 | `actions/checkout@v4` |
| .github/workflows/external-inventory-state.yml | sync | 4 | `actions/checkout@v4` |
| .github/workflows/external-inventory-state.yml | sync | 5 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | preflight | 1 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | declared_network | 1 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | declared_network | 2 | `actions/setup-python@v5` |
| .github/workflows/xconnect-zero-cloud.yaml | declared_network | 4 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | declared_network | 5 | `actions/create-github-app-token@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | declared_network | 6 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | resolve_ai_aggregator_matrix | 1 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | resolve_ai_aggregator_matrix | 2 | `actions/setup-python@v5` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 1 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 3 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 4 | `actions/create-github-app-token@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 5 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 6 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 7 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 10 | `actions/create-github-app-token@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 12 | `hashicorp/setup-terraform@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 14 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 15 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 16 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 18 | `aws-actions/configure-aws-credentials@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | apply | 28 | `actions/upload-artifact@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | existing_one | 1 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | existing_one | 3 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | existing_one | 4 | `actions/create-github-app-token@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | existing_one | 5 | `actions/create-github-app-token@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | existing_one | 6 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | existing_one | 7 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | existing_one | 9 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | enroll_node_matrix | 2 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | enroll_node_matrix | 3 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | enroll_node_matrix | 4 | `actions/create-github-app-token@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | enroll_node_matrix | 5 | `actions/create-github-app-token@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | enroll_node_matrix | 6 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | enroll_node_matrix | 7 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | enroll_node_matrix | 8 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | enroll_node_matrix | 9 | `aws-actions/configure-aws-credentials@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | reconcile_mesh | 1 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | reconcile_mesh | 2 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 1 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 3 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 4 | `actions/create-github-app-token@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 5 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 6 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 7 | `actions/checkout@v7` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 9 | `hashicorp/setup-terraform@v3` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 10 | `hashicorp/vault-action@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 11 | `aws-actions/configure-aws-credentials@v4` |
| .github/workflows/xconnect-zero-cloud.yaml | cleanup | 13 | `aws-actions/configure-aws-credentials@v4` |
| .github/workflows/environment-data-operations.yml | request_gate | 1 | `actions/checkout@v7` |
| .github/workflows/environment-data-operations.yml | legacy_import | job | `ai-workspace-infra/playbooks/.github/workflows/uat-data-import.yaml@b82d727808696278613df248e01c29059048be35` |
| .github/workflows/environment-data-operations.yml | akamai_preflight | job | `ai-workspace-infra/iac_modules/.github/workflows/akamai-state-preflight.yml@f8b3d52e4f2b6528fcf4fa762ea7bf83f8145d06` |
| .github/workflows/environment-data-operations.yml | serverless_database | job | `ai-workspace-infra/playbooks/.github/workflows/serverless-database-operations.yml@5a1f68c6de22010b20771ea7583f892c2c899da3` |
| .github/workflows/environment-data-operations.yml | selfhost_database | job | `ai-workspace-infra/playbooks/.github/workflows/selfhost-database-operations.yml@7d660cdb4066e2a4cf3fed68bccafea939771e64` |
| .github/workflows/environment-data-operations.yml | selfhost_components | job | `ai-workspace-infra/playbooks/.github/workflows/selfhost-data-lifecycle.yml@5a1f68c6de22010b20771ea7583f892c2c899da3` |
| .github/workflows/environment-data-operations.yml | release_controller | 1 | `actions/checkout@v7` |
| .github/workflows/environment-data-operations.yml | release_controller | 5 | `actions/upload-artifact@v7` |
| .github/workflows/environment-upgrade-ci.yml | offline-rehearsal | 1 | `actions/checkout@v7` |
| .github/actions/configure-gcp-oidc/action.yml | __composite_action__ | 1 | `hashicorp/vault-action@v4` |
| .github/actions/configure-gcp-oidc/action.yml | __composite_action__ | 2 | `hashicorp/vault-action@v4` |
| .github/actions/configure-gcp-oidc/action.yml | __composite_action__ | 3 | `google-github-actions/auth@v2` |

### 审计分类汇总

| 类别 | 数量 |
| --- | --- |
| EXECUTION_CANDIDATE | 101 |
| FLOATING_MAIN_CANDIDATE | 10 |
| FLOATING_OWNER_REF | 3 |
| UNREFERENCED_INPUT | 9 |
| UNRESOLVED_SCRIPT_LITERAL | 26 |

完整候选明细见同目录 audit.md 和 audit.json；规则命中需要人工判断，不是部署验收。
