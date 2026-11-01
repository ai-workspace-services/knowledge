# 通用 Vault 工作负载身份契约

状态：通用身份契约仍为设计，尚未完成通用声明及调用方实现。本文不自动授权写入 Vault、切换 Flux、迁移凭据或删除旧资源。

**最新执行记录（2026-11-01，北京时间）：** 经用户明确要求，公共 Vault 的旧 `jwt-prod-k3s-v6` mount 已停用，其下旧 TLS reader role 随之删除，mount 签发的 token 已撤销；同名 reader policy 保留。当前 V6 SecretStore 仍引用旧 mount，证书同步失败。新集群专用 mount、role 和通用 GitOps 引用尚未创建或切换；执行前配置快照及脱敏操作记录由操作方保管。详见 [V6 最新部署状态](PROD-K3S-V6-规划与部署状态归档.md)。

## 创建命令与脚本记录

**2026-11-01 V6 执行记录：** 公共 Vault 已创建 mount `jwt-prod-k3s-prod-k3s-v6`、role 和 policy `prod-k3s-tls-reader`。使用真实 V6 ServiceAccount 验证指定记录允许、相邻记录及错误 audience / ServiceAccount 被拒绝；公钥 PEM SHA-256 为 `2a0b1cbe6522f9eadc8cc1e10367f4d10671b47a0d248476305be0c37ff1524e`。用户指定当前 cluster ID 为 `prod-k3s-v6`，其带版本号，属于对通用命名约定的显式例外；重建集群不能仅凭同名复用信任。此前创建的 `jwt-prod-k3s-2519bf1ba3d7db80` 暂保留且未切换消费者。创建使用了本机已有 root 会话，而非下述短期受限管理身份；该偏离需后续治理。GitOps 引用和 ESO 同步尚未验证。

**以下为 Vault CLI 命令模板。** 执行前核验 GitOps 声明、CMDB、实际 cluster UID 和节点 UID、SSH host key、issuer 及集群签名公钥。使用受限、短期的 Vault 管理身份；token 通过受控环境提供，不写入命令参数、脚本、仓库、日志或回执。准备 `jq` 和经过核验的公钥 PEM 文件，不使用私钥。

```bash
export VAULT_ADDR="https://vault.svc.plus"
CLUSTER_ID="prod-k3s-v6" # 当前 V6；其他集群使用其独立声明的 ID
MOUNT="jwt-prod-k3s-${CLUSTER_ID}"
ROLE="prod-k3s-tls-reader"
POLICY="prod-k3s-tls-reader"
ISSUER="https://kubernetes.default.svc.cluster.local"
AUDIENCE="vault-prod-k3s-tls"
SUBJECT="system:serviceaccount:vault-prod:vault-tls-reader"
PUBLIC_KEY_FILE="<已核验的JWT公钥PEM路径>"

# 人工核对：新 mount 不存在；同名 policy 不存在，或内容及所有消费者已审查。
vault auth list
vault policy list

# 仅在新 mount 不存在且 policy 可安全创建时执行。
vault auth enable -path="$MOUNT" jwt
jq -n --arg issuer "$ISSUER" --rawfile key "$PUBLIC_KEY_FILE" \
  '{bound_issuer:$issuer,jwt_validation_pubkeys:[$key]}' | \
  vault write "auth/${MOUNT}/config" -
vault policy write "$POLICY" - <<'POLICY_EOF'
path "kv/data/CICD/domains/svc.plus" {
  capabilities = ["read"]
}
path "auth/token/lookup-self" {
  capabilities = ["read"]
}
POLICY_EOF
vault write "auth/${MOUNT}/role/${ROLE}" \
  role_type=jwt user_claim=sub bound_subject="$SUBJECT" \
  bound_audiences="$AUDIENCE" token_policies="$POLICY" \
  token_no_default_policy=true token_type=batch \
  token_ttl=10m token_max_ttl=10m token_explicit_max_ttl=10m
```

`vault policy write` 会覆盖同名 policy；仅在确认不存在时使用上面的创建命令。若已存在，先核对实际内容和消费者，内容完全匹配时复用，不执行覆盖。命令中的名称是规划示例，实际运行必须与已审查的 GitOps 声明一致。执行若中断，可能留下部分配置；重试前检查 mount、配置、role 和 policy，不盲目重复创建。

创建后以真实 ServiceAccount TokenRequest 验证指定证书路径允许、相邻路径及错误 audience 和 ServiceAccount 被拒绝；不得将 JWT、Vault token 或读取到的秘密输出到终端或日志。记录实际非敏感名称、目标、GitOps commit、公钥指纹、执行时间、命令和脱敏结果；未确定的名称标为待定。验证通过后才通过 GitOps 切换 SecretStore，并记录 Flux revision、SecretStore 与 ExternalSecret 状态。CLI 创建成功不等于上述验证或服务就绪。

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
