# PROD V3→V4 P0 事件记录与回归 Case

记录日期：2026-10-21（Asia/Shanghai）。本文追加到 V2→V3 历史升级索引，记录本轮 V3→V4 候选运行中报告或观察到的问题。此文是事件索引，不代替当前在线状态检查；除明确标记“已验证”的证据外，Case 状态均不得推断为通过。

## 关联记录与构件

- 上一代历史索引：[PROD V2→V3 快照与升级复盘](../../15-prod-v2-v3-snapshots-and-upgrade-retrospective.zh.md)
- Playbooks 回归目录：[V4 upgrade regression cases](https://github.com/ai-workspace-infra/playbooks/blob/main/docs/cases/runbooks/2026-10-21-v4-p0-regression-cases.md)
- 本轮 Accounts/Portal 构件：用户提供的记录为不可变 tag `v2026.10.21-r5`；其具体镜像 digest 应以对应发布回执补齐。
- GitOps：Accounts/Portal 相关 PR #481 的合并 SHA 据记录为 `9c53e45babf5f4cdba07946838812fffb15a5cb3`。
- Playbooks：凭据修复 PR #714 的合并 SHA 据记录为 `300fb0829d49e55a056bbb46d4b419b80cd06307`。
- GitOps 出站网络修复 PR #483 在本次交接记录中为“CI 通过、尚未合并部署”；后续状态需重新核实，不可据此宣称现网已修复。

## 事件摘要

本轮主要故障集中于候选 V4 与 V3 的运行合同没有完整对齐：数据库业务角色授权、Stripe 网络/签名配置、恢复期入口规则、Exporter 共享令牌、单一采集者身份以及 UI 对最新流量的时间窗展示。登录或基础健康检查成功不能证明注册、账单、采集和前端用量展示链路通过。

| Case ID | 事件与已知证据 | 回归要求 | 当前记录状态 |
| --- | --- | --- | --- |
| `V4-P0-DB-ROLE` | V4 曾报告业务表写入权限错误；后续纠正明确规定业务运行连接使用权威 `account_user`，迁移/备份审计身份不得替代业务账号。 | PostgreSQL 17 候选库验证应用使用 `account_user`，注册、账本及流量写入所需权限齐全；同时核验应用连接未注入恢复/审计角色。 | 脚本提供只读授权核验；真实应用写路径仍须候选环境集成验收。 |
| `V4-P0-STRIPE-EGRESS` | 订阅预览曾返回 409；排查指出 V4 Accounts 容器无法连接 Stripe，而 V3 可连接。PR #483 被报告为出站修复，但当时未合并部署。 | 仅在 Stripe Sandbox 候选配置运行 HTTPS/DNS/TLS 连通性探针，再由 Sandbox 预览/结账验收补足应用层证明；不执行真实扣款。 | 本地/候选连通性脚本已建立；线上修复状态待核对，Sandbox 流程待执行。 |
| `V4-P0-WEBHOOK-SECRET` | 相同 Stripe 事件据报告在 V3 验签成功、V4 返回 401；怀疑 V4 使用了不匹配的 endpoint secret。此为排查结论，不是已确认根因。 | Sandbox endpoint 发送签名事件；正确 secret 成功、错误 secret 被拒、重复事件幂等；确认 endpoint 与 Vault key 映射但不记录 secret 值。 | Accounts 自动化测试及 Sandbox endpoint 核验待绑定同一候选回执。 |
| `V4-P0-AGENT-INGRESS` | JP Agent 状态上报曾连续收到 403；V4 页面显示 0 个区域入口/Team 节点。历史上恢复期 probe-only Caddy 规则曾拦截状态 POST。 | 用候选专用令牌验证 POST 路由、注册状态落库、无凭据/错误凭据拒绝；另验证配置下发和连接，不以 GET 健康检查代替。 | 作为独立集成 Case；当前候选实测结果待登记。 |
| `V4-P0-EXPORTER-TOKEN` | JP01 Exporter 的 canonical shared token 曾为空，快照上报未启用。经 Playbooks PR #714 执行后记录 `ok=19 changed=2`；同版本重跑无变化且无服务重启；随后观察到最新 JSON 采样。 | 检查 Vault 权威引用、渲染 env 与运行进程注入；重跑幂等；获取新鲜快照且不输出令牌。 | Playbooks 修复和重跑有历史回执；新候选仍需绑定版本回归。 |
| `V4-P0-TRAFFIC-CHAIN` | 最近一小时 UI 曾显示 0 B；DB 可见新桶但字节增量为 0。之后 JP01 两个相邻分钟桶分别增长 `20,655,875` 与 `32,880,714` bytes，Exporter 累计计数同步递增，构成真实采集到 PostgreSQL 的正向证据。 | 已有正常客户端访问时核对 Exporter 单调计数、Vector 转发、Billing 接收和 DB 连续正值分钟桶；不伪造生产流量、不手写账本。 | 这组 JP01 历史采样通过；不代表所有节点/用户均已通过。 |
| `V4-P0-DUPLICATE-NODE` | 两个活跃生产源曾声称同一 `jp-xconnect.svc.plus` 身份，来源地址不同，观测到异常字节差值；单纯看到正桶不足以证明没有重复采集。 | 全活跃源清单按稳定 node/transport ID 去重；同身份多源必须失败并定位，不以相似域名或 IP 猜测归属。 | 纯函数回归测试已建立；未知来源主机身份仍须完成现场核验。 |
| `V4-P0-UI-FRESHNESS` | 数据库有流量但订阅页/控制台最近一小时仍显示 0 B；最近 24 小时/月度值非零。 | 同一账户对照数据库 UTC 时间窗、Accounts 响应和刷新后浏览器数字；覆盖边界时刻与零/正桶，区分新鲜度延迟和真实零流量。 | 手工浏览器 Case；Portal 单元测试尚未建立，UI 验收不可宣称通过。 |
| `V4-P0-LOGIN-SESSION` | V4 登录页曾返回 `500/session_creation_failed`；直接 GET 登录 API 返回 `method_not_allowed`，后者本身符合 POST-only 接口语义，不应作为根因。 | 候选环境 POST 正确登录凭据并验证服务端会话/cookie；覆盖会话存储不可用错误，不记录凭据或 cookie。 | 历史故障已登记；自动化集成回归待补。 |
| `V4-P0-ACCOUNT-BOOTSTRAP` | 控制台截图报告 `/api/account/policy` 404 与 VLESS URI `node is undefined`。 | 候选浏览器/API 测试确认 policy 路由存在、区域节点数据加载完成后才构造 URI；空节点呈现可恢复状态，不抛未捕获异常。 | 历史故障已登记；前端自动化回归待补。 |

## 时间顺序与边界

1. `2026-10-21`：JP `xconnect-edge-agent` 日志显示状态上报连续 403；该日志证明当时上报未成功，不证明是令牌本身错误。
2. `2026-10-21`：V4 Accounts/Portal tag `v2026.10.21-r5` 与 GitOps PR #481 作为该轮发布依据记录；具体镜像 digest、逐服务运行镜像和部署收敛 receipt 应补齐后再作为完整不可变证据链。
3. `2026-10-21`：Playbooks PR #714 关联 Exporter token 修复。记录的第一次执行有两项变更，第二次同版本执行无变更/重启；JP01 后续出现新鲜采样及两分钟正向桶增量。
4. 同轮另有重复生产者身份线索；在完成全部活跃生产者清点前，不能将总字节增长归因到唯一节点，也不能声称所有用户的最近一小时展示通过。
5. Stripe 出站修复 PR #483 在交接时仅有“检查通过、尚未合并部署”的记录；Webhook secret mismatch 是待验证假设。当前状态需通过 GitHub 和 Sandbox endpoint 重新取证。

## 关闭规则

每一个 Case 的正式收据应记录 `case_id`、候选 source SHA、镜像 digest、GitOps SHA、run ID、执行时间、预期、实际、退出码、脱敏证据位置及 `PASS/FAIL/BLOCKED/NOT_RUN`。只有绑定同一候选构件的真实回归通过才可关闭；未运行、环境不具备或只有 PR/CI 通过均不能记 PASS。生产流量切换、真实支付/退款以及 V3 写入状态不在本记录授权范围内。
