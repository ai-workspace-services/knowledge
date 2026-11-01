# 通用 Vault 工作负载身份契约

状态：通用身份契约仍为设计，尚未完成通用声明及调用方实现。本文不自动授权写入 Vault、切换 Flux、迁移凭据或删除旧资源。

**最新执行记录（2026-11-01，北京时间）：** 经用户明确要求，公共 Vault 的旧 `jwt-prod-k3s-v6` mount 已停用，其下旧 TLS reader role 随之删除，mount 签发的 token 已撤销；同名 reader policy 保留。当前 V6 SecretStore 仍引用旧 mount，证书同步失败。新集群专用 mount、role 和通用 GitOps 引用尚未创建或切换；执行前配置快照及脱敏操作记录由操作方保管。详见 [V6 最新部署状态](PROD-K3S-V6-规划与部署状态归档.md)。

## 创建命令与脚本记录

**状态：以下为待执行的命令模板，不是创建或验证成功的记录。** 现有执行脚本归 Playbooks 所有：[workload_identity_operation.py](https://github.com/ai-workspace-infra/playbooks/blob/main/scripts/workload_identity_operation.py) 调用 `vault_jwt_workload_identity.yml` 和 `vhosts/vault_jwt_workload_identity` role。执行时必须固定并记录实际 Playbooks commit；以上链接只用于定位入口，不代表固定运行版本。

先准备已审查的 GitOps 身份操作声明及其干净 checkout、精确目标的 CMDB、已验证的 bootstrap 回执、已认证的 SSH host key 和隔离 SSH agent。`VAULT_ADDR` 必须与声明一致；`configure` 使用仅含声明的管理 policy、有效期不超过 1200 秒的短期 Vault token。凭据通过受控运行环境提供，不能写入脚本、命令参数、仓库、日志或回执。以下大写参数均为操作方提供的非敏感路径或摘要，须在执行前核对；不要用旧集群回执冒充当前集群证据。

```bash
# 创建新 mount、policy 和 role；输出是脱敏回执，路径必须不存在。
python3 "$PLAYBOOKS_DIR/scripts/workload_identity_operation.py" \
  --mode configure \
  --gitops "$GITOPS_DIR" --gitops-sha "$GITOPS_SHA" \
  --operation-path "$IDENTITY_OPERATION_PATH" \
  --cmdb "$CMDB_PATH" --cmdb-sha256 "$CMDB_SHA256" \
  --bootstrap-receipt "$BOOTSTRAP_RECEIPT_PATH" \
  --known-hosts "$VERIFIED_KNOWN_HOSTS_PATH" \
  --receipt "$CONFIGURE_RECEIPT_PATH"

# 单独使用真实 ServiceAccount TokenRequest 验证允许与拒绝；另用新的回执路径。
python3 "$PLAYBOOKS_DIR/scripts/workload_identity_operation.py" \
  --mode verify \
  --gitops "$GITOPS_DIR" --gitops-sha "$GITOPS_SHA" \
  --operation-path "$IDENTITY_OPERATION_PATH" \
  --cmdb "$CMDB_PATH" --cmdb-sha256 "$CMDB_SHA256" \
  --bootstrap-receipt "$BOOTSTRAP_RECEIPT_PATH" \
  --known-hosts "$VERIFIED_KNOWN_HOSTS_PATH" \
  --receipt "$VERIFY_RECEIPT_PATH"
```

`configure` 成功只证明配置步骤完成；`verify` 须单独证明指定证书路径允许、相邻路径和错误 audience / ServiceAccount 拒绝。若创建中断，可能留下部分 Vault 配置；重试前读取脱敏失败阶段并检查现有对象。记录执行时间、目标实例和集群身份、GitOps/Playbooks SHA、mount、role、policy、命令模式、结果及允许/拒绝测试，不记录 token、JWT、证书私钥或秘密值。验证通过后才通过 GitOps 切换 SecretStore，再记录 Flux revision、SecretStore 与 ExternalSecret 状态。

执行记录应保留实际使用的非敏感名称和引用，包括 Vault 地址、环境、cluster ID、节点和实例标识、JWT mount、role、policy、namespace、ServiceAccount、audience、KV 路径和字段名、SecretStore、ExternalSecret 和目标 Secret 名称，以及命令中非敏感的文件路径、SHA 和操作模式。名称可以完整记录，不必统一替换为占位符；未确定或未创建的名称标为待定，不能把示例写成实际执行结果。token、ServiceAccount JWT、证书私钥、密码及其他凭据值不得记录。

## Vault、ESO 与 Secret 名称的关系

```text
GitOps ──> Flux 控制器 ──> ServiceAccount / SecretStore / ExternalSecret / 工作负载声明
                                      │
ESO controller Deployment ──TokenRequest──> ServiceAccount JWT
           │                                   │
           │                             Vault JWT mount / role / policy
           │                                   │
           └──读取 SecretStore 和 ExternalSecret──> 外部 Vault KV 路径及字段
                                                        │
                                 ExternalSecret target.name ──> Kubernetes Secret
                                                                    │
                                        业务 Deployment / StatefulSet 引用或挂载
```

### 运行组件

| 组件 | 职责 | 名称或位置示例 | 与 Secret 的关系 |
| --- | --- | --- | --- |
| 外部 Vault 服务 | 提供 JWT 登录、策略授权及 KV 数据；可独立部署于业务集群之外 | `https://vault.svc.plus` | 保存源证书和凭据；不因 SecretStore 名称而自动授权 |
| Flux 控制器 | 从 GitOps 调谐集群声明并报告状态 | `flux-system` 中的 source、kustomize、helm 控制器 | 创建或更新声明；Flux Ready 不等于 ESO 已同步或业务已就绪 |
| ESO controller Deployment | 读取 SecretStore 和 ExternalSecret，申请 ServiceAccount TokenRequest，访问 Vault 并维护目标 Secret | V6 当前为 `external-secrets/external-secrets` | 负责同步；自身运行身份需对目标 ServiceAccount 的 TokenRequest 有必要权限 |
| ESO webhook 与证书控制器 | 提供 ESO 资源校验及 webhook 证书管理 | V6 当前为 `external-secrets-webhook` 和 `external-secrets-cert-controller` | 支持 ESO 运行，不是业务 Secret 或 Vault 凭据的来源 |
| Vault JWT auth、role 与 policy | 校验集群签名及身份声明，并限定可读路径 | 每集群独立 mount，TLS reader 使用专用 role 和 policy | 登录成功后才能按 policy 读取上游 KV；与 Kubernetes Secret 分属不同系统 |
| 业务 Deployment 或 StatefulSet | 以声明的 Secret 名称挂载证书或消费必需字段 | V6 集群内 Vault 的工作负载引用 `vault-prod/vault-server-tls` | 引用必须指向同 namespace 中已同步的目标 Secret；业务运行身份和权限须独立验证 |

ESO controller 的运行 ServiceAccount 与 SecretStore 引用的 Vault reader ServiceAccount 可以不同：前者运行控制器并获得受限的 TokenRequest 权限；后者的 JWT subject 用于 Vault 登录。不能仅凭两者名称或 Pod Running 推断 Vault 授权和 Secret 同步成功。

| 对象或字段 | 作用 | TLS 引导规划示例 | 对应关系 |
| --- | --- | --- | --- |
| ServiceAccount | Kubernetes 中的工作负载身份；ESO 为它申请短期 JWT | `vault-prod/vault-tls-reader` | SecretStore 的 `serviceAccountRef.name` 指向它；Vault role 的 subject 必须绑定该 namespace 和名称 |
| JWT mount | Vault 验证当前集群签名的认证入口 | `jwt-prod-k3s-<cluster-id>` | SecretStore 的认证 `path` 指向它；不同实际集群使用独立 mount |
| Vault role | 验证 subject、audience 并授予关联 policy | `prod-k3s-tls-reader` | SecretStore 的 `role` 指向该 mount 内的 role；audience 必须与 TokenRequest 一致 |
| Vault policy | 约束认证后可访问的 Vault 路径和操作 | `prod-k3s-tls-reader` | 由 Vault role 引用；policy 名称与 role 名称可以相同，但二者是不同对象 |
| Vault KV 记录及字段 | 保存证书链和私钥，作为 ESO 的上游数据源 | KV v2 逻辑路径 `kv/CICD/domains/svc.plus`；字段 `tls_fullchain_pem_b64`、`tls_key_pem_b64` | policy 授权的 API data 路径为 `kv/data/CICD/domains/svc.plus`；ExternalSecret 的 `remoteRef.key` 不重复写 `kv` mount 或 `data` API 前缀 |
| SecretStore | 声明 Vault 地址、KV mount 与认证方式 | `vault-prod/vault-tls-bootstrap` | ExternalSecret 的 `secretStoreRef.name` 引用同 namespace 中的 SecretStore；此名称无需与 Vault role 或 Secret 同名 |
| ExternalSecret | 声明上游字段如何同步和转换为 Kubernetes Secret | `vault-prod/vault-server-tls` | 通过 `spec.target.name` 指定输出 Secret 名称；ExternalSecret 和 Secret 名称可以相同，但不是同一个对象 |
| Kubernetes Secret | ESO 同步后供工作负载挂载的集群内对象 | `vault-prod/vault-server-tls` | Vault 工作负载的卷或配置必须引用 `spec.target.name` 指定的名称；TLS 字段为 `tls.crt` 和 `tls.key` |

本表使用现有 V6 TLS 字段映射和规划身份名称说明关系；实际记录、字段、授权及同步状态均须在目标环境验证。`secretStoreRef` 使用 `SecretStore` 时按 namespace 解析；若以后采用 `ClusterSecretStore`，须单独审查其作用域和授权。Secret 名称本身不是 Vault KV 路径，也不是 Vault role；不要用相同名称推断它们已连接或已同步。

## 集群身份与职责

外部 Vault 服务独立于业务集群部署。每个实际集群显式声明不可变、非敏感的 `clusterId`，该标识在同一环境和 Vault 实例内唯一，不包含代际或节点版本，也不从 hostname 推导。即使重建后的集群沿用 hostname，也须分配新的 ID。通过 IaC/CMDB 证据及经认证的 cluster UID、node UID 将声明与实际目标绑定；名称本身不能证明身份。运行时 UID、密钥和 token 不提交到仓库。

GitOps 声明环境、集群 ID、Vault 地址、JWT mount、工作负载身份、精确 KV 路径及预期 audience；Playbooks 负责 Vault 和集群身份操作；Flux 负责 Kubernetes ServiceAccount、SecretStore 和 ExternalSecret 声明；IaC 提供目标事实和 CMDB。人工执行也须使用同一固定 GitOps 声明及其证据，不要求使用流水线。

## GitOps 声明字段与规划命名

以下名称为规划示例，不代表已有 schema 字段已实现或 Vault 对象已创建。具体值须显式声明，不能从节点版本或目录名推导。

| 声明项 | 作用和范围 | 规划命名或示例 |
| --- | --- | --- |
| 环境 | 隔离生产、预发布和测试的身份与授权 | `prod`、`uat`、`sit` |
| 集群 ID | 同一 Vault 和环境内标识一个实际集群；重建时分配新 ID | `clusterId: <cluster-id>`；随机生成且不含版本号 |
| Vault 地址 | 外部 Vault 的 HTTPS 地址，与集群部署位置无关 | `https://vault.svc.plus` |
| JWT auth mount | 每个实际集群的独立签名信任边界 | `jwt-<environment>-k3s-<cluster-id>`，例如 `jwt-prod-k3s-a7f39c` |
| 工作负载 namespace | ServiceAccount 所在 Kubernetes namespace | TLS 引导示例：`vault-prod` |
| ServiceAccount | 工作负载获取短期 TokenRequest 的身份 | TLS 引导示例：`vault-tls-reader` |
| Vault role | 在集群对应的 mount 内绑定 subject、audience 与 policy | TLS 引导示例：`prod-k3s-tls-reader` |
| Vault policy | 精确约束可访问的 Vault 路径和操作；名称在 Vault 内全局有效 | TLS 引导示例：`prod-k3s-tls-reader` |
| KV 路径 | 对消费者授权的精确 KV v2 API data 路径 | TLS 引导示例：`kv/data/CICD/domains/svc.plus` |
| Audience | 限定 JWT 的预期接收用途 | TLS 引导示例：`vault-prod-k3s-tls` |
| SecretStore | Flux 管理的 ESO Vault 连接和身份引用 | TLS 引导示例：`vault-tls-bootstrap` |

Vault policy 在 Vault 内是全局对象：仅当精确 policy 内容确实需要共享且生命周期得到协调时，才能共用同一个名称；否则应声明独立 policy 名称。不同 mount 本身不能隔离全局 policy。表中的 cluster ID 仅为说明性示例，并非已分配的实际值。

每个 role 绑定精确的 subject 和 audience，使用短期 token，仅授予必需的 KV v2 data 路径。各工作负载使用独立的 ServiceAccount、role 和最小权限 policy。以经过身份验证的集群 JWKS 为公钥来源，不要求外部 Vault 访问私有集群 API。禁止使用跨集群通配授权或关闭 TLS 校验。

## 调用方契约

GitOps 身份操作声明和对应的 Flux SecretStore 必须解析到相同的 mount、role、ServiceAccount 和 audience。这些值须由一份权威声明驱动或进行一致性校验；缺失、冲突或未展开的字段必须报错。身份操作须包含环境、目标声明引用、集群 ID、Vault 地址、policy，以及明确的允许和拒绝测试路径。调用方不得从 `v6`/`v7` 名称推断目标，也不得静默回退到旧 mount。

现有 `VaultWorkloadIdentityOperation` schema 已包含显式参数，但尚未实现 cluster ID 分配、共享声明渲染或与 Flux 资源的一致性自动校验。现有 Playbooks role 接受显式身份参数，但其 `refresh` 会替换 mount 的整组验签密钥。这些缺口须先完成实现和测试，才能将本契约作为部署证据。

## 迁移与验收

1. 盘点当前 mount、实际 role、policy、消费者和密钥指纹。认证目标集群，并记录 CMDB 和 GitOps revision 证据；不能假定带版本的 hostname 足以识别集群。
2. 准备通用 owner 和声明调用方，实现缺参即失败的契约校验。测试缺失输入、声明不一致、集群重建，以及两个集群使用不同 mount 同时运行的情况。
3. 使用范围受限的短期 Vault 管理身份配置新 mount 和精确工作负载 role，并将其密钥指纹与目标集群核对。验证指定 ServiceAccount 和精确路径允许访问；错误 ServiceAccount、错误 audience 和相邻路径均被拒绝。
4. 新身份验证通过后，一次切换一个 Flux 管理的 SecretStore。记录已应用的 GitOps revision，确认 SecretStore `Valid`、ExternalSecret `SecretSynced`；按用途验证证书链、SAN、有效期、证书与私钥匹配及实际 SNI。其他工作负载须在各自 role 和路径就绪后逐项切换。
5. 在确认所有实际消费者已迁移且完成独立退役授权前，保留旧 mount、policy 和源服务。若切换失败且旧身份仍有效，可恢复先前的 GitOps 引用；重试前须调查任何部分完成的 Vault 写入。

未完成消费者盘点、独立指纹审查和串行执行前，不得使用 `refresh` 替换共享 mount 的密钥。Vault JWT 配置没有 compare-and-swap。未来部署 V7 时只改变目标事实和 cluster ID，不复制实现；V6 与 V7 可以并存，且不共享签名信任。
