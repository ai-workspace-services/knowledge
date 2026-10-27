# Dev V5 职责调整：临时 SIT、持久 Serverless UAT、2C4G

修订日期：2026-10-27，Asia/Shanghai。本文修改目标，不覆盖同日 08:46 的历史快照；尚未发生的云变更不记为完成。

## 当前确定的流程

关联跨仓 PR → 固定完整构件 → Dev K3s V5 临时 SIT Namespace＋特性域名 → 自动测试和最新 main 组合验证 → 按门禁合并 main。

Dev K3s V5 的特性验收闭环终点为合并 main。UAT 是独立的持久 Serverless 环境，消费 main 的受控构建与固定 digest，另行出具部署和回归证据。合并并不自动代表 UAT 已发布或验收通过。

| 维度 | 临时 SIT | 持久 UAT |
|---|---|---|
| 运行平台 | Dev K3s V5，目标 2C4G | 既有 Serverless 平台 |
| 发布输入 | 多仓 PR 固定 head SHA、digest、Chart、配置指纹 | main 固定 SHA 与构建 digest |
| 隔离 | 每功能完整 Namespace、独立 PostgreSQL、凭据与会话 | Cloud Run / Pages 服务、独立 UAT Supabase 与 UAT 凭据 |
| 入口 | xconnect-referral-sit.onwalk.net 等特性域名 | console-serverless-uat.onwalk.net、accounts-serverless-uat.onwalk.net、billing-serverless-uat.onwalk.net |
| 生命周期 | 测试后按批准回收 | 持续保留；发布版本可回滚 |
| 当前状态 | 尚无业务栈；临时环境声明待发布 | 已有声明，本轮未做运行验收 |

UAT 权威声明沿用 `topology/uat/serverless/runtime-topology.yaml` 和 `iac/targets/uat-serverless-runtime.yaml`，架构为 Cloudflare Pages + Cloud Run + Supabase。持久指环境及数据生命周期，不要求 Cloud Run 始终保留运行实例或取消 scale-to-zero。现有 Pages branch 字段为 uat；它不能证明 main 自动发布已连通，应由既有 Serverless 编排器明确将 main 构件发布至 UAT。

原 K3s `web-saas-uat` 候选从当前 Dev 功能候选中移除。旧的三个 K3s UAT DNS 记录不会因此自动迁移或删除；Serverless 部署只消费其既有目标域名。历史六份 UAT Terraform state 不在本次清理范围。

## 2C4G 降配预检与实况

云 API 确认实例 109277144、label dev-k3s-v5、jp-tyo-3，当前仍为 g6-standard-4。目标为 g6-standard-2：2 vCPU、4096 MiB RAM、81920 MiB 磁盘配额。该实例的动态 IP 需每次重新解析。

严格 host-key SSH 只读预检：4 CPUs，内存 7940 MiB、使用 1467 MiB、可用 6473 MiB；根文件系统 ext4，使用 3819 MiB；Kubernetes 节点样本 CPU 98m、内存 1556 MiB；仅基础 Pod，无业务 PVC。此为单次闲置采样，不是完整 SIT 容量或负载测试。

当前根盘 204036933 分配 163328 MiB，swap 204036934 分配 512 MiB，合计 163840 MiB，超过目标 81920 MiB。因此不能只改 Terraform type 后直接视为可 apply。候选操作为停机 → 根盘缩至不超过 81408 MiB（保留 512 MiB swap）→ IaC 按既有 Dev state 更新 type → 刷新 CMDB → 验证 2 CPUs、4 GiB、文件系统、K3s/Flux Ready 与入口。执行前再次核实实例/磁盘、无活跃 SIT 和恢复方案；失败不得默认为删机重建。

官方依据：[Resize a Linode](https://techdocs.akamai.com/linode-api/reference/post-resize-linode-instance)、[Resize a disk](https://techdocs.akamai.com/linode-api/reference/post-resize-disk)。现有通用 Resize Instance 仅支持 Vultr，不能作为 Linode 缩盘执行入口。本轮只提交规格声明及预检，不宣称硬件已降配。

2C4G 初始仅允许一个完整功能泳道并发；以实际 Pod requests、平台开销和运行峰值决定后续并发。SIT 回收不删除平台入口、ACME 数据或持久 Serverless UAT 数据。

## 剩余交付

1. 完成可信 SIT 部署、SMTP/Stripe 注入与真实自动测试。
2. 审核并通过 Linode owner 完成离线缩盘与 IaC 降配，输出实际规格回执。
3. 通过既有 Serverless 发布链交付 main 构件到 UAT；验证路由、数据与权限边界。
4. 禁止继续将旧 K3s UAT writer 候选作为当前发布方案；其历史 PR 须按依赖关系重构或关闭。

## 重建回执（2026-10-27）

用户删除旧 Dev 实例后，GitOps #604、#608 已合入 main，2C4G / 80、443 的最终声明 SHA 为 `f861be448ea495905ec614d82dedc45ab1197149`。Dev 专用 [IaC 计划](https://github.com/ai-workspace-infra/platform-ops-toolkit/actions/runs/40438938089) 记录创建 1、更新 0、删除 0；[创建 run](https://github.com/ai-workspace-infra/platform-ops-toolkit/actions/runs/40439068564) 的资源回执为 applied_verified，创建 1、更新 0、删除 0。云 API 确认新实例 `109324752`、`g6-standard-2`、running，当前动态 IP `172.237.5.48`，Dev 防火墙已绑定 HTTP/HTTPS 规则。

该 run 的 bootstrap job 失败，日志只显示 `ValueError`，具体原因尚未确定。旧 Dev SSH 绑定与新实例身份不一致，需要独立核验新服务器 host key 并更新既有 Dev SSH 记录，再仅重试该失败 job；新主机、K3s、SIT 与业务验收尚无 PASS 回执。此回执取代上文“实例仍为 4C8G、降配需缩盘”的当前状态，上文保留为操作前历史。
