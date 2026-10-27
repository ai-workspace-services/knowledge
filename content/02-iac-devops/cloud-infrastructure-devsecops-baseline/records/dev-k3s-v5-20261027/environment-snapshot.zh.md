# Dev K3s V5：SIT / UAT 环境快照与发布缺口

采集时间：2026-10-27 08:46，Asia/Shanghai。本文保存该时点的历史快照，后续部署须追加新回执，不能将本记录作为实时状态。凭据仅记录逻辑路径和字段名，不包含值、验证码或测试邮箱地址。

## 1. 目标与当前结论

实测需求为 XConnect 邀请活动后端接入。用户确定的流程是：规划特性 → 拆解并关联跨仓 PR → 固定构件 → 临时完整 SIT Namespace＋特性域名 → 自动测试 → 组合验证并合并 main → 同节点独立完整 UAT Namespace。UAT 持续跟踪 main 的受控构建，每次部署仍须固定 SHA/digest。此流程采用合并后 UAT，与技能默认的合并前冻结 UAT 有差异，以本次用户确定的流程为准。

**当前结论：平台基础就绪，业务发布 BLOCKED，SIT/UAT 均未部署、未验收。** DNS、CI、Vault 记录存在均不能代替运行和业务验收。

## 2. 主机与集群实况

| 项目 | 08:46 观测值 | 状态与限制 |
|---|---|---|
| 逻辑主机 | dev-k3s-v5 | 云实例身份 109277144 |
| 当前连接地址 | 172.237.5.48 | 动态值，执行前必须重新通过实例身份解析 |
| OS / 架构 | Debian 12 / amd64 | 旧交接的 Debian 13 与当前观测不符 |
| K3s | v1.37.1+k3s1 | 单节点 Ready |
| Node UID | 597c8c54-d9ff-45a8-8bce-b6a4a53bf2de | 当前观测 |
| Cluster UID | 49c0dccb-9243-4972-8c4c-a3bf550b9d26 | 以前次当日只读回执为依据 |
| Flux source / root | 60bf8621c5a0d1dfd3f7ce38758a48740f9f14e7 | platform-config / platform-root generation 与 observedGeneration 均为 1 |
| 基础 Pod | 7 个 Running / Ready | 4 Flux、CoreDNS、local-path、metrics-server；另 CRD 安装 Job 完成 |
| Namespace | default、feature-xconnect-referral、flux-system、kube-node-lease、kube-public、kube-system | 旧 feature-xconnect-referral 只是占位，不能算 SIT |
| 业务资源 | 业务 Pod、HelmRelease、Ingress、StatefulSet、业务 Service 均为 0 | 无实际业务 imageID/readiness |

## 3. SIT / UAT 与入口

| 项目 | SIT 待发布声明 | UAT 待发布声明 | 当前实况 |
|---|---|---|---|
| Namespace | feature-xconnect-referral-sit | web-saas-uat | 两者均不存在 |
| Console | xconnect-referral-sit.onwalk.net | web-saas-uat.onwalk.net | A 记录均为 172.237.5.48 |
| Accounts | accounts-xconnect-referral-sit.onwalk.net | accounts-web-saas-uat.onwalk.net | 同上 |
| Billing | billing-xconnect-referral-sit.onwalk.net | billing-web-saas-uat.onwalk.net | 同上 |
| 组件范围 | Caddy / Console / Accounts / Billing / Content / PostgreSQL | 同左 | 均未运行 |
| 生命周期 | 功能临时泳道，验收并授权后回收 | 持久环境，受控跟踪 main | 生命周期控制尚未完成实测 |
| HTTP / TLS | 目标对外 80/443 | 目标对外 80/443 | 六域名 HTTP /health HEAD 断连、HTTPS 失败，无有效状态码及证书成功证据 |

SIT/UAT 使用 onwalk.net，生产使用 svc.plus。本快照没有修改生产。DNS 解析到节点不表示 80/443 已具备业务服务；本次未重新审计云防火墙完整规则。

## 4. 固定候选镜像（声明，非运行 imageID）

以下来自 GitOps #605 候选，实际运行均为空。只有 digest 得到证据，不能据此补写未核实的应用版本号或源 SHA。

| 组件 | SIT digest | UAT digest |
|---|---|---|
| Caddy | sha256:9895385033fea2bdb445841b45f37e6cd58b9e071a16e4c147e483abb74a0acf | 同 SIT |
| Console | sha256:03ffaf0174c64aede7602b5d566ff27921f760e134028afabb62b646324228f9 | 同 SIT |
| Accounts | sha256:97a58ebe7fab56432777591604491c2dea7fc7cc57cd35820fedef78fa328572 | sha256:6edd156ce6974dfd0cd7486beebbb446091e4019eacf3c272e05aba4a609737d |
| Billing | sha256:01cc4490e62be69aaa936dd3c2aa9aa909a876844e2968f0ccdc1cbbdbd44ba2 | 同 SIT |
| Content | sha256:791113978a1f158ae411901f4fc25b18bc3a407fbb858bc89ce669df67469478 | 同 SIT |
| PostgreSQL | sha256:c6ee94d4c91054128823e816e936e03702eee80fdcc04d3271a7e68167974ad2 | 同 SIT |

SIT Accounts 候选关联 Accounts PR #279。UAT 上述固定快照尚不能证明 main 自动发布已生效。其余跨仓源 SHA、Chart digest、候选内容指纹仍需补齐，不能把镜像列表视为完整候选验收凭证。

## 5. 数据与身份隔离

SIT/UAT 声明各部署完整 PostgreSQL 与独立运行时配置。当前没有业务 StatefulSet、业务数据或运行账户证据，因此独立数据库、服务角色权限、迁移幂等、会话隔离与 PVC 生命周期均为 NOT_RUN。

采用系统管理、业务独立读写、审计强制只读三类职责；本次管理员严格 SSH 只读观测不等于独立审计身份已通过拒绝测试。容器非 root、DB 非超级用户及审计禁止秘密读取也均待业务部署后核验。

## 6. Vault KV 路径与消费者

地址为 https://vault.svc.plus。下列为逻辑 KV 路径；KV-v2 API 读取路径需插入 data，例如 kv/data/dev/platform/smtp/google。

| 用途 | Dev 逻辑路径 | 字段 / 证据 | 消费状态 |
|---|---|---|---|
| Bootstrap SSH | kv/CICD/dev/k3s-bootstrap | 已约定 Dev 专用路径，暂复用同一 SSH key pair | 本表不重验字段及值 |
| 云凭据 | kv/CICD/dev/akamai-cloud/manbuzhe2026 | Dev 云身份逻辑路径 | 当前未重读 |
| Terraform backend | kv/CICD/dev/iac_state | 已授权复用非生产连接配置，canonical key 独立 | 当前未重读 state |
| Registry | kv/CICD/dev/ghcr | GHCR_USERNAME、GHCR_TOKEN，授权临时复用 | 不代表业务成功拉取 |
| DNS | kv/CICD/dev/cloudflare | CLOUDFLARE_ACCOUNT_ID、CLOUDFLARE_API_TOKEN；metadata v1 | 仅授权新的 onwalk.net 测试记录 |
| SMTP | kv/dev/platform/smtp/google | username、password；metadata v2，用户自行复制 | 尚无已验证业务注入链路 |
| Stripe Sandbox | kv/dev/billing-service | SANDBOX_STRIPE_SECRET_KEY、SANDBOX_STRIPE_WEBHOOK_SECRET | 尚无已验证业务注入链路 |

SMTP 配置来源声明为 smtp.gmail.com:587、TLS auto。用户授权暂时复用生产 SMTP 凭据；路径分离不代表凭据已经独立。没有执行发信。当前候选仍是 mail-disabled.invalid:1025，且缺少 SMTP egress。

Stripe 只读预检 GET /v1/balance 返回 HTTP 200、livemode=false，证明测试模式凭据有效；没有创建付款或支付对象，不证明应用支付及 webhook 验收。

## 7. 监控

集群没有 monitoring Namespace、exporter Pod 或业务监控目标。Metrics API 有节点样本，只能说明平台指标可读。候选 vmagent 指向集群内临时 sink，中央 remote-write 路由与写身份未获运行验证；Grafana 匿名 health 200、dashboard 401，不证明目标看板可用或采集入库。日志、指标、告警及 feature/revision 标签关联均未完成验收。

## 8. PR / 声明证据

以下状态为本次采样，可能随后变化。

| 仓库 / PR | 内容 | 观测状态 |
|---|---|---|
| [GitOps #605](https://github.com/ai-workspace-infra/gitops/pull/605) | 完整 SIT/UAT 候选 | OPEN Draft；head 1817161155abc96de873c00174f148688be59be4 |
| [GitOps #606](https://github.com/ai-workspace-infra/gitops/pull/606) | SIT Namespace 与 Flux root wiring | OPEN；叠在 #605；head 6625edae969306bb6410b738bfb6a2a0d5ce7347；8 项检查通过 |
| [GitOps #601](https://github.com/ai-workspace-infra/gitops/pull/601) | Dev 监控声明 | OPEN；head aeab586ebc18b81cd925f14eced2662befb7a852 |
| [GitOps #607](https://github.com/ai-workspace-infra/gitops/pull/607) | 监控标签 / 旧 renderer 整理 | OPEN；叠在 #601；head e433db527bb890ebd3a520faf282853289b7131e；8 项检查通过 |
| Playbooks #806 / #808 | 邀请验收 runner / 运行时 seed | 尚未成为已验证部署链路 |
| Toolkit #1457 / #1458 | 候选发布 / 凭据编排 | 尚未成为已验证 main 发布链路 |

可信 main 部署 caller 与 seed workflow 的此前读取返回 404。旧笔记中“依赖已合并”的描述已被当日远端核对纠正。检查通过、文档存在和工作树代码均不能证明已部署。

## 9. 验收矩阵与修复清单

| 阶段 | 状态 | 待完成 |
|---|---|---|
| 平台 Ready | PASS | 保持动态地址重新解析 |
| DNS | PASS（解析范围） | 部署后验证 HTTP、TLS 与业务路由 |
| 固定候选 / 跨仓 PR 关联 | BLOCKED | 补完整 SHA、Chart 与内容指纹及可信入口 |
| SIT 完整栈 | NOT_RUN | 合规部署并采集 readiness/imageID |
| SMTP / 注册 / 登录 | BLOCKED | 注入、正确配置、egress、两独立测试账户与运行时验证码 |
| Stripe / webhook / 邀请归因 | BLOCKED | 注入 Sandbox 字段并完成真实隔离验收 |
| 数据 / 身份隔离 | NOT_RUN | DB、PVC、会话、权限允许与拒绝证据 |
| 组合验证 / 合并 | NOT_RUN | 固定最新 main 与所有 PR 组合后重新验证 |
| UAT 跟踪 main | NOT_RUN | 建立受控构建、固定构件及独立 Namespace 部署 |
| 监控入库 | BLOCKED | 采集器、中央路由、写身份与认证读取证据 |
| 泳道归档回收 | NOT_RUN | 验收后单独按生命周期授权处理 |

下一步先修复部署 caller、SMTP/Stripe 消费契约及网络声明，再部署 SIT 做真实业务验收；每次变化生成新候选并重验受影响项。后续结果另追加时间戳回执，不覆盖本次未完成状态。

## 10. 证据来源与边界

本记录整理自当日 REVALIDATION-20261027 回执、08:46 严格 SSH 只读盘点、六域名外部探测、GitHub PR 固定 head 及 Vault metadata/字段名核对。未保存秘密值、原始 Secret、真实邮箱、验证码或支付数据。本次快照采集没有部署、合并、Terraform apply/destroy、修改历史 UAT state 或改动生产。
