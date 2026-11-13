# SIT-K3S-V6 换机执行记录

> 本文只记录任务执行状态、核验证据和遗留项，不承载架构规划、操作方案或放行步骤。唯一规划来源为 [SIT-K3S-V6 模块化交付与特性泳道规划](SIT-K3S-V6-模块化交付与特性泳道规划.md)。执行边界遵循 [ADR-0001：GitOps 三类执行器与单一配置负责人](../../architecture/ADR-0001-GitOps三类执行器与单一配置负责人.md)。

## 执行范围

- 集群逻辑名：`sit-k3s-v6`。
- 目标：Contabo 手动创建的独立节点 `5.189.172.69`，Debian 13、4 vCPU、约 8 GiB RAM、约 99 GiB 根盘；`/data` 是根文件系统上的受控分配目录，不是独立数据卷。
- 参考源：`172.237.9.58`，仅用于 auditor 只读对照，不是新 SIT 部署目标。
- 执行身份：目标由 `operator@5.189.172.69` 执行 Playbook/Flux 操作；源端使用 `auditor@172.237.9.58` 只读核查。
- 本轮约束：ExternalDNS 保持 dry-run；未执行 DNS 写入或切换；源端 PVC、数据库和历史观测数据未迁移。

## 已执行并核验

| 日期 | 执行记录 | 结果 / 证据 |
| --- | --- | --- |
| 2026-11-12 | 以源机 `auditor` 身份进行只读进程和服务盘点。 | 已完成。该盘点不等同于源端完整 Kubernetes/Helm/PVC 清单；源端 auditor kubeconfig 未交付。 |
| 2026-11-12 | 将 `kv/prod/security/{root,operator,auditor}` 的 `authorized_keys` 复制到对应 SIT 路径，并回读核对。 | 已完成；未在文档中记录密钥材料。 |
| 2026-11-12—13 | 目标机完成 `vhosts/common` OS 初始化和 `/data` 目录交付。 | 已完成。OS 三类身份登录与 auditor 拒绝项完成核验；operator 的受限 sudo 已配置。目录由 root 拥有，组/其他用户不可写。Playbooks #1015。 |
| 2026-11-13 | 目标机初始化 K3s 单节点。 | 已完成。节点 `sit-k3s-v6` 为 `Ready`，K3s `v1.37.1+k3s1`，Debian 13，4 CPU、8,138,640 KiB 可分配内存。 |
| 2026-11-13 | 以 operator 身份安装 Flux CLI/控制器并交接独立 Contabo 根路径。 | 已完成。目标当前根 revision 为 `sit-k3s-v6-contabo-r5@sha1:9e5066014ce3b03292be1331e18c40be315dddb5`；`sit-k3s`、`external-secrets`、`cluster-identities-sit`、`vpa-sit`、`external-dns-sit` Kustomization 为 Ready。 |
| 2026-11-13 | ESO、VPA 与集群身份控制器核验。 | 已完成。ESO 三个 Pod、VPA 三个 Pod、Flux 四个控制器均为 `1/1 Running`；目标 K3s 三类身份的允许/拒绝验收已完成。 |
| 2026-11-13 | ExternalDNS dry-run 交付核验。 | 部分完成。Vault JWT 身份、SecretStore 和 ExternalSecret 为 Ready；Cloudflare API 返回 HTTP 403 / code 9109 `Invalid access token`，ExternalDNS Pod 为 `CrashLoopBackOff`。日志确认 `--dry-run`，未写入 DNS。 |
| 2026-11-13 | PostgreSQL Vault/ESO 声明 PR #904、GitOps r6 PostgreSQL rollout PR #905 合并核验。 | 已完成代码合并；目标 Flux 仍在 r5，尚未接收 r6；`postgresql-sit` 仍挂起，目标未创建 PostgreSQL Pod/PVC/ExternalSecret。 |

## 未完成或阻塞

| 项目 | 当前状态 | 后续执行记录条件 |
| --- | --- | --- |
| GitOps r6 根源交接 | 待执行。远端尚无 `sit-k3s-v6-contabo-r6` 发布 tag；目标当前仍为 r5。 | 记录 tag/SHA、operator handover 回执和 Flux `lastAppliedRevision`。 |
| PostgreSQL 凭据交付 | 待执行。目标 ESO JWT reader role、ExternalSecret 同步、数据库实例和 PVC 尚未核验。 | 记录三个既有 Vault 字段到 ESO Secret 的 Ready 结果、数据库健康状态、PVC 与账户权限验收；不记录凭据值。 |
| Observability、MCP、Ingress、Web SaaS | 当前 Flux Kustomization 均为 `suspend: true`，未部署。 | 每个模块分别记录启用 revision、Kustomization/HelmRelease Ready、Pod/Service/PVC 和功能验收。 |
| operator sudo 最小权限 | 尚未符合规划目标。`sudo -n -l` 显示 K3s/容器工具免密规则，同时 operator 仍有密码保护的 `(ALL : ALL) ALL` 通用 sudo 规则。 | 由主机权限变更移除/收敛通用 sudo 后，用 operator 实测批准/拒绝命令，再更新状态。 |
| ExternalDNS 凭据 | 阻塞。当前 Vault 所供 token 被 Cloudflare 拒绝。 | 凭据所有者更新原有记录后，仅记录 API 读取和 dry-run 结果；不得把 token 写入本文。 |
| DNS 与入口验收 | 未执行。目标路由/TLS 尚未部署，公共 DNS 未切换。 | 规划文档指定的各域名路由、证书和服务健康逐项通过后，再记录单独获准的 DNS 变更及回滚结果。 |
| 源端完整服务清单 | 未完成。auditor 仅完成主机级只读盘点，不能读取源端 Kubernetes 管理凭据。 | 获得审计身份后补充 Flux/Helm/PVC/Ingress 实际状态；不得从进程名推断版本或声明部署一致。 |

## 运行记录约定

每次续执行只追加日期、操作者、目标 revision/SHA、实际动作、Ready/健康结果、脱敏证据链接和失败/回退结果。未执行事项保持未完成；规划变更回到模块化交付规划文档，不在本清单复制操作方案。
