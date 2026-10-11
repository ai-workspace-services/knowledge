---
title: 多云 IaC Pipeline v0.6：清理与执行归属迁移记录
description: 分批记录 Toolkit、IaC Modules 与 Playbooks 的清理、固定 SHA caller 交接、验证结果和旧副本退休条件。
slug: multi-cloud-iac-cleanup-batches-20261007
lang: zh
date: 2026-10-07
version: "0.2"
status: implementation-partial
author: shenlan
tags: [multi-cloud, iac, pipeline, gitops, execution-ownership]
category: reference
---

# 多云 IaC Pipeline v0.6：清理与执行归属迁移记录

本轮按 [设计 v0.6](multi-cloud-iac-unified-pipeline-design.zh.md) 继续清理、移动与合并。三个 subagents 使用 GPT 5.6 Sol、high reasoning 分组编码；主代理负责交叉复核、整合、PR 与远端 CI 核验。**已合并的执行库不等于 caller 已上线，静态检查与 mock 不等于真实 UAT。**

## 1. 保持不变的契约

- 六个 provider：`aws-cloud`、`azure-cloud`、`vultr-vps`、`gcp-cloud`、`ucloud`、`akamai-cloud`。
- Toolkit 持有入口、审批、目标选择、正反向 DAG、运行关联与最终放行。
- IaC Modules 提供依赖 GitOps 声明的 actions、Terraform 模块与云资源执行脚本。
- Playbooks 提供 controller adapter、主机/服务执行 actions 与 Roles；Vault 授权与私密交接留 Toolkit。
- master 八个 job、stages 三个 job 保持原契约；`plan/apply` 按 bootstrap → account → resources，销毁按 resources → account → bootstrap。共享身份、网络与 backend 保护保持原声明与 gate。

## 2. 批次与结果

| 批次 | 清理、移动、合并 | 发布状态 | 尚未满足的运行条件 |
| --- | --- | --- | --- |
| 1 无调用代码与静态触发 | 删除无 caller 的 `terraform-command`、`setup-iac-env`、旧 self-check、SSH helper；PR/push 静态校验集中到矩阵入口 | Toolkit [#1374](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/1374) 已合并 main | AWS 恢复/收养脚本与兼容 wrappers 仍有独立职责，不按文件数机械删除 |
| 2 GCP 云操作 | auth/WIF/state adapter、OS Login、实例事实、临时防火墙与撤销归 IaC；Toolkit 保留环境与 Vault identity policy | IaC [#415](https://github.com/ai-workspace-infra/iac_modules/pull/415) 已合并 main；caller 随 Toolkit #1375 合并 | GCP runtime access 与 cleanup 尚未真实验证；旧副本冻结 |
| 3 主机与 Vault | deployment runner、existing-node inventory、Vault stage/SSH/Raft、自动迁移 observation、精确 controller dependency setup 归 Playbooks | Playbooks [#620](https://github.com/ai-workspace-infra/playbooks/pull/620)、[#621](https://github.com/ai-workspace-infra/playbooks/pull/621) 已合并 main | 未执行 live SSH/Vault/Raft；Toolkit 只消费推荐阶段并展开允许的 stage plan |
| 4 云配置与事实读取 | GCP/AWS 声明读取与校验、Cloud Run revision/traffic/digest、OCI index child 查询归 IaC；Toolkit 保留 digest/traffic 最终 gate | IaC [#416](https://github.com/ai-workspace-infra/iac_modules/pull/416) 已合并 main | 无 Docker 的只读 OCI HTTP 已通过 mock；真实 Registry/Cloud Run 未验收 |
| 5 delivery workflow 归属 | Cloudflare domains、Akamai state preflight 的 delivery job 迁回 Toolkit，调用固定 IaC actions | Toolkit [#1375](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/1375) 已按用户要求合并 main | 新 Vault workflow claim 仅改源码，未应用 live；旧 IaC workflow 保持 LEGACY 回退 |
| 6 XConnect 云与 Accounts | lab Terraform/state/lease/cleanup 归 IaC；Accounts network bootstrap 与一次邀请归 Playbooks；Vault handoff 留 Toolkit | owner 分别在 IaC #416、Playbooks #621；caller 随 Toolkit #1375 合并 | 不触发真实 apply/destroy/Accounts 写入；未知资源或缺 ownership tag 阻断 cleanup |
| 7 non-IaC / TLS | 私密 runtime inventory 与节点 key 适配归 Playbooks；TLS material vars 与恢复复用 `caddy_certificate_restore` Role | Playbooks [#622](https://github.com/ai-workspace-infra/playbooks/pull/622) 已合并 main；caller 随 Toolkit #1375 合并 | 保留旧 renderer、TLS prepare 与 restore shell；尚未真实验证证书恢复 |
| 8 XConnect 主机与数据面 | exact target + 预审 known_hosts 的 Role runner；One/Gateway、TLS、精确 peer handshake、私网 HTTP 证据 | Playbooks #622 为 additive owner；默认 host caller 未切换 | cloud lab 缺可信 host-key 声明与 private probe endpoint/marker；H6 existing-One/额外节点混合 caller 尚未拆完 |
| 9 扫描治理 | 覆盖 `scripts/node_deploy` Python/Shell/import/source 执行链；Accounts 服务写不再作为 control-plane 豁免 | Toolkit #1375 已合并 | 21 项冻结候选是待迁移/待 UAT 债务，不表示新增了 21 个允许执行入口 |

## 3. 本轮修复的失败路径

| 失败路径 | 新行为 | 验证范围 |
| --- | --- | --- |
| Cloudflare Pages GET/DELETE 失败或删除后仍存在 | 不再把失败解释为不存在；必须 authoritative re-read 后确认已脱离 | owner shell mock，包括 query failure、delete failure、still present 与成功重新读取 |
| Cloud Run traffic 为空、混合 revision 或 digest 不匹配 | 拒绝放行；只接受唯一 ready revision，digest 为预期 artifact 或其精确 linux/amd64 child | Toolkit final-gate 正负例；IaC query mock |
| OCI Registry 查询通过 Docker 取元数据 | 改为认证的只读 OCI HTTP；限制 Artifact Registry authority，token 不进入 command argv | owner mock 与禁止 Docker 合同 |
| lab cleanup 缺所有权标签或有未知资源 | 销毁前失败；只接收精确 lab state/resource identity，保留 backend 证据 | state/标签负例与 mock lifecycle |
| XConnect peer 来源存在多个 runtime 配置 | 显式失败，不继续读取第一个配置；单个配置还须绑定精确 device/public key/overlay IP | 实际执行生成的 peer parser，覆盖缺项、多配置、错 peer；receipt 绑定当前 run/attempt 与 owner SHA |
| non-IaC 显式域名记录不完整 | 拒绝执行，不能静默回退到另一节点/根记录的连接信息 | inventory adapter 负例 |
| 新本地 reusable workflow 只允许 main OIDC claim | claim 路径精确，逐项沿用环境已有 ref 规则；PROD tag 可匹配而 main/普通分支不可匹配 | claim 正负例；未应用 live Vault |
| Toolkit root Python 间接执行 SSH/provider | 扫描 subprocess 与递归 import/source；新增执行或修改冻结字节即失败 | 20 个 scanner tests、13 个 active-entry mock checks |

同仓 reusable workflow 使用 caller 的提交，OIDC `job_workflow_ref` 描述被调用 workflow；因此 main-only claim 会挡住 tag caller。规则依据 [GitHub reusable workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) 与 [OIDC reusable workflow claims](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-with-reusable-workflows)。

## 4. 验证与退休门槛

已完成 owner/caller 单测、负例、Shell/YAML/Ansible 静态检查、workflow gating、固定 checkout 引用检查和远端 PR CI。IaC pipeline Python 94 项、Playbooks node-deploy 87 项、pipeline owner 16 项、XConnect Role/evidence contract 8 项通过；对应 shell mocks 和 focused caller tests 通过。两个新增 Toolkit delivery workflow 的 actionlint 通过；修改过的既有 workflows 没有新增 lint diagnostics，仍有基线工具 metadata/choice/matrix diagnostics。

Toolkit caller 固定 IaC `9570b01959396e1d0e20331205b5cb5718f5c588`、Playbooks `18fa333e5d76143f2a3a3ce94b1766a04003ebd8`。两者为已发布且 PR CI 通过的 owner commit；GitOps 声明、运行身份和精确目标仍由 caller 提供。

本轮没有执行 live cloud/state、DNS、SSH、Vault 策略、Raft、数据库或 Accounts 写入，也没有不可变 release/UAT/business acceptance。待退休副本保留原字节；新 owner 与正式 caller 的精确版本、同 run 证据、目标收敛和回退窗口闭合后，再单独提交删除。

| 下一步 | 可复核结果 |
| --- | --- |
| 新 Vault claims 的受控应用与身份验证 | 环境、精确 workflow/ref、允许与拒绝的 claim 证据；不扩大权限掩盖失败 |
| GCP/主机链的非破坏性 UAT | exact owner/Toolkit/GitOps SHA、run/attempt、访问和 cleanup 证据 |
| XConnect 可信 target handoff | IaC/CMDB 或审核声明提供的 host keys、目标、private probe URL/marker；缺项 fail closed |
| caller PR 放行与 legacy 退休 | owner → caller → verification → deletion；逐个删除有替代和证据的副本 |

执行归属规则来源：[execution-ownership-migration](https://github.com/ai-workspace-lab/xworkspace-core-skills/blob/main/skills/engineering-standards/execution-ownership-migration/SKILL.md)。其中要求缺少 UAT 证据阻断 merge/release。用户随后明确要求提交并合并，Toolkit #1375 已合并为 `6a6043da2e61934ce534d08054a35962c6b2c2ca`；这仅更新源码发布状态，不代表 runtime 放行或旧副本可删除。

## 5. 后续 48 文件批次

再次使用 GPT 5.6 Sol/high subagents，按 IaC owner、Playbooks owner、Toolkit 控制面测试三组实施。完整逐文件映射见 [Toolkit owner 交接记录](https://github.com/ai-workspace-infra/platform-ops-toolkit/blob/83cb1bae956cc0120e269db4bd9e45d2f073791f/docs/howto/owner-followup-20261007.zh.md)。

| 顺序 | 实现与证据 | 当前边界 |
| --- | --- | --- |
| owner 实现 | IaC [#417](https://github.com/ai-workspace-infra/iac_modules/pull/417) 已合并，固定 `d7e49189a5de9c105a940f1c79abfb3b2b33bbd4`；Terraform 原始失败退出码、0600 脱敏日志、state-read 失败禁止 destroy、固定 ref lease 契约及远端 CI 通过 | 没有真实 Provider/state 变更 |
| owner 实现 | Playbooks [#623](https://github.com/ai-workspace-infra/playbooks/pull/623) 已合并，固定 `9d585e147348800b1603c4f7b0d8a6bcf0546007`；XHTTP Gateway/One verifier、同 run marker 私网 probe、失败关闭 cleanup、owner tests 与远端 CI 通过 | 没有 SSH/Accounts/service 变更 |
| Toolkit caller | [#1376](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/1376) 远端 CI 全通过并合并 main `310ec72e39932982912f65f1cf8ab56951554045`；两个发布后的固定 owner；runtime-control 和 Gateway reconcile 调用 Role action，service probes/observation 复用现有 owner；12 个测试及 fixture 迁 `scripts/tests/control_plane`，PR/push 静态 CI 覆盖 | 非变更 rehearsal 的精确 run 证据另记 |
| 验证与删除 | 60 个 environment/data/import 测试、迁后 shell contracts、owner route 负例、scanner、refs/gating、Ansible syntax 通过 | 所有旧执行副本仍冻结；只有纯控制面测试迁目录 |

SSH host keys 按部署云资源相同的 KV 环境/目标来源选择：UAT runtime-control 从 `kv/data/CICD/uat` 成对读取 `SSH_PRIVATE_DEPLOY_KEY_B64` / `SSH_KNOWN_HOSTS_B64`；现有外部 Gateway 从自己的精确 record 同时读取 host、user、`ssh_private_key_b64` / `known_hosts_b64`。两个 known_hosts 字段仍待 live seed/匹配证据，不能以源码声明证明已存在。缺 key、target 不匹配或 key 无效时在连接前阻断，不使用 `accept-new` 或 keyscan 首次信任。

Vault role 源码新增 runtime-control 的精确 main claim，并绑定 UAT environment；live apply 未证明。正式 cloud-lab 主机安装、existing-One 和额外节点混合路径仍待拆完。apply/destroy、SSH/XHTTP/WireGuard/私网 HTTP 及业务验收必须另有 exact-version receipt，之后才按文件退役旧副本。

### 5.1 Main 只读 rehearsal

[Run 37641969087 / attempt 1](https://github.com/ai-workspace-infra/platform-ops-toolkit/actions/runs/37641969087) 已成功，参数为 `deployment_profile=cloud-lab`、`mode=dry-run`、`matrix_node_filter=none`。版本精确绑定：Toolkit main `310ec72e39932982912f65f1cf8ab56951554045`、IaC `d7e49189a5de9c105a940f1c79abfb3b2b33bbd4`、Playbooks `9d585e147348800b1603c4f7b0d8a6bcf0546007`、GitOps `28430b835c4275eea1921aa7fd98c96dbc2c50ef`。

- 两个 preflight jobs、现有 cloud-lab Vault OIDC 登录、固定 repo checkout 和声明校验通过。
- Playbooks control-plane probe 验证 Accounts/Portal 匿名响应边界；发布 artifact `owner-receipt-service-xconnect-control-plane`，ID `11492827205`，digest `sha256:afb692da5748c408e4f4e2a3d9501ca52ad81e88363c3cc3e894c71fdb526867`。
- 下载后校验 receipt 的 owner SHA、run/attempt、UAT environment、operation/scope 和 accepted 状态；`receipt.json` SHA-256 为 `0135cfed3f73a5f67bafcfea0264f3fb8ef3cfe63113740c7a226fce810a6f2b`。artifact digest 与文件 checksum 是不同证据。
- 已验证 release artifacts 和 owner Terraform preflight（fmt/init backend=false/validate）。
- 基础设施凭证读取、DNS、AWS OIDC、prepare/apply、Accounts 邀请、主机安装、额外节点、Gateway reconcile 和 cleanup 均跳过。

这份证据证明只读控制面与 owner preflight 路由可运行，不能证明新 runtime-control Vault claim 已生效、known_hosts 字段已 seed、SSH 主机信任或数据面验收，也不授权删除仍被完整部署链调用的旧执行文件。
