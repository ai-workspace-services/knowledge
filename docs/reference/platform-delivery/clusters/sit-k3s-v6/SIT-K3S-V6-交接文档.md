# SIT-K3S-V6 换机交接文档

> 交接时间：2026-11-13 01:00（北京时间）· 治理规范：[ADR-0001：GitOps 三类执行器与单一配置负责人](../../architecture/ADR-0001-GitOps三类执行器与单一配置负责人.md)
>
> 逐项进度以 [SIT-K3S-V6 换机执行清单](SIT-K3S-V6-换机执行清单.md) 为准；命令、放行条件与回退见 [换机重部署与 DNS 切换手册](SIT-K3S-V6-换机重部署与DNS切换手册.md)。本文只做现状汇总与下一步交接，不含 IP、密码、token 或私钥。

## 1. 一句话现状

目标主机 `sit-k3s-v6`（Contabo VPS，Debian 13）上 K3s 单节点与 4 个 Flux controller 已就绪，候选 Flux 根路径已固定到 tag `sit-k3s-v6-contabo-r1`；**尚未执行 Flux 根交接、身份签发、新集群 Vault JWT 信任、服务放行和 DNS 切换**。旧机继续承载全部 SIT 流量。

## 2. 已完成

| 领域 | 状态 | 依据 |
| --- | --- | --- |
| 主机基线 | `vhosts/common` OS 身份（root / operator / auditor）与主机名已应用 | 清单 §执行记录 |
| K3s | `v1.37.1+k3s1` 单节点 Ready，`data-dir` 为 `/opt/rancher/k3s`，flannel，内置 traefik 关闭 | auditor 核对 |
| Flux | CLI 2.9.6 + 4 个 controller（`flux-system` 全部 1/1 Ready）；尚无 `config-sit` / `sit-k3s` 对象 | 清单 |
| 候选根路径 | `environments/clusters/sit-k3s-v6/overlays/contabo-vps`，第一阶段只启用 namespaces、External Secrets、`cluster-identities-sit` | gitops#895、#896 |
| Git 源钉选 | overlay 内 9 个 GitRepository 统一指向 tag `sit-k3s-v6-contabo-r1`（tag 位于合并提交 `34974b9`），替代原先自引用的 commit 钉选 | [gitops#899](https://github.com/ai-workspace-infra/gitops/pull/899) |
| 身份声明 | SIT `k3s_identity` 声明在 `resources/svc.plus/sit/Contabo-VPS/sit-k3s-v6.yaml`，TLS 目录 `/opt/rancher/k3s/server/tls` | gitops#896、#898，playbooks#1011 |
| become 密码 | operator sudo 密码只存 Vault `kv/sit/security/become/operator`（v3），Ansible 通过 `become_from_vault.yml` 注入；泄露过的 v1/v2 已 destroy | playbooks#1013、#1014 |
| sudo 边界 | operator 仅 `k3s`、`ctr`、`kubectl`、`flux` 免密，其余需 Vault 注入的密码；auditor 无 sudo | 清单 |
| identity-writer | SIT identity-writer 策略与角色已应用到 Vault（绑定 Platform-Orchestrator、环境 sit、batch token 30m） | 清单 |
| 数据契约 | `/data` 支持独立 ext4 卷（`k3s_platform_data_mode: volume`，默认）或分配目录（`directory`）；本机无数据盘，交接用 `directory` | [playbooks#1015](https://github.com/ai-workspace-infra/playbooks/pull/1015) |
| 主机防火墙 | `sit-k3s-guard` 已修复：先放行 `lo`/`cni0`/`flannel.1`，公网侧控制面端口仍拦截 | 清单 |

## 3. 待办（按执行顺序）

1. **Flux 根交接**：以 operator 运行 `flux_gitops` 的 `declarative_active` 模式，root `sit-k3s`、source `config-sit`、path `environments/clusters/sit-k3s-v6/overlays/contabo-vps`，`ref` 为 tag `sit-k3s-v6-contabo-r1`（commit `34974b9`），`k3s_platform_data_mode=directory`，GitOps 仓库公开、无需 Git 凭据。验收标志 `FLUX_HANDOVER_VERIFIED`。
2. **身份签发**：重跑 `k3s_identity_bootstrap.yml`，`k3s_identity_gitops_sha` 用上一步实际调谐的 40 位 commit，`common_os_identity_key_source=vault-cli`，Vault token 用 identity-writer 策略签发的 30 分钟 batch token。`rbac_wait` 要求 `cluster-identities-sit` 的 `lastAppliedRevision` 与该 sha 一致。验收标志 `K3S_IDENTITIES_VERIFIED`，再由 auditor 复核。
3. **新集群 Vault JWT 信任**：从新集群的 issuer/JWKS 新建独立挂载（例如 `jwt-sit-k3s-sit-k3s-v6-contabo`），在 contabo overlay 中修补 SecretStore 指向新挂载。**不得修改旧集群挂载 `jwt-sit-k3s-sit-k3s-v6`**，旧集群仍依赖它。
4. **`sit-k3s-guard` 纳入 playbooks**：按 ADR-0001 改由 playbooks 防火墙 role 下发，规则声明放 GitOps，移除主机手工文件（备份 `.bak-20261113` 仍在主机上）。
5. **分阶段放行服务**：PostgreSQL / 观测 / VPA → 应用与 MCP → 入口，逐段验收（PV/PVC、ESO 同步、空库初始化、业务冒烟、证书 SAN）。
6. **DNS 切换与观察**：按手册导出原记录、确定唯一写入者（注意 `external-dns-sit` 暂停状态与实际 Deployment），观察至少一个旧 TTL 和一个任务周期。

## 4. 操作约定

- **账户**：目标机变更用 `operator@sit-k3s-v6`，核对用 `auditor@sit-k3s-v6`；root 不用于日常操作。三账户共用同一把 SSH key 是确认过的配置，权限由 OS 账户区分。
- **执行器边界**（ADR-0001）：主机 OS / 防火墙 / systemd / K3s 安装归 Ansible Pull，Compose 栈归 Doco CD，集群内资源归 Flux；同一资源只有一个声明式负责人。
- **密钥**：所有凭据只在 Vault；仓库和聊天里只出现 KV 路径。GitOps 可写主机名与账户名，不写 IP，IP 由 CMDB 动态引用。
- **环境顺序**：先 SIT，PROD 不在本次范围内。
- **长任务**：Ansible 长任务用后台方式运行并看日志，避免会话中断导致半途终止。

## 5. 已知坑

- operator 的 `become` 依赖 Vault 注入的密码：先绑定密码再 `gather_facts`，否则报 “Missing sudo password”（已在 #1014 固化）。
- `sit-k3s-guard` 重启时会连带重启 k3s；改规则后要确认 Flux 与 metrics-server 恢复。
- `rbac_wait` 会一直等到 Flux 根交接完成，交接前跑身份签发必然在这一步失败，属于预期。
- 标准 `bootstrap-k3s.sh` 入口要求数值实例 ID 与 Linode 数据卷，本目标不满足，按 operator SSH inventory 分阶段调用 role，不伪造 CMDB 字段。
- 旧观测 / PostgreSQL 静态 PV 绑定旧节点和路径，新机需重新渲染绑定。

## 6. 相关链接

- 执行清单：[SIT-K3S-V6-换机执行清单.md](SIT-K3S-V6-换机执行清单.md)
- 手册：[SIT-K3S-V6-换机重部署与DNS切换手册.md](SIT-K3S-V6-换机重部署与DNS切换手册.md)
- 模块化交付规划：[SIT-K3S-V6-模块化交付与特性泳道规划.md](SIT-K3S-V6-模块化交付与特性泳道规划.md)
- ADR：[ADR-0001](../../architecture/ADR-0001-GitOps三类执行器与单一配置负责人.md)
- 关键 PR：gitops [#895](https://github.com/ai-workspace-infra/gitops/pull/895) [#896](https://github.com/ai-workspace-infra/gitops/pull/896) [#898](https://github.com/ai-workspace-infra/gitops/pull/898) [#899](https://github.com/ai-workspace-infra/gitops/pull/899)；playbooks [#1011](https://github.com/ai-workspace-infra/playbooks/pull/1011) [#1013](https://github.com/ai-workspace-infra/playbooks/pull/1013) [#1014](https://github.com/ai-workspace-infra/playbooks/pull/1014) [#1015](https://github.com/ai-workspace-infra/playbooks/pull/1015)
