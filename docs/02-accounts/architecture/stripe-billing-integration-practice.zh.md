---
title: Stripe 订阅与权益对接实战
description: 从 Checkout、Webhook、财务账本到退款恢复、配额与 Agent 同步的完整工程闭环。
slug: stripe-billing-integration-practice
lang: zh
tags:
  - stripe
  - billing
  - subscription
  - engineering
---

# Stripe 订阅与权益对接实战：从 Checkout 到退款恢复的完整工程闭环

> **INFO**  Stripe 集成不是把 `create checkout session` 接上页面就结束。可靠的订阅系统还要把支付模式、价格目录、Webhook 投递、本地账务、订阅状态、配额、访问策略、Agent 连接、退款与运维发布连成可恢复、可核对、可审计的一条链。

**适用对象：**有订阅、按量计费或账户权益的 SaaS 团队。本文以 XWorkmate 的 Accounts、Portal、Stripe Sandbox、Billing 与 Agent 链路为例，解释设计边界、实现要点、测试矩阵和上线验收。

**阅读提示：**本文记录截至 2026-10-21 的工程实践。示例中的套餐和金额用于说明业务映射；密钥、Webhook signing secret、客户资料和完整支付凭据不得写入代码、日志、工单或本文。

## 先定义谁拥有哪类事实

Stripe 是支付提供方，负责 Checkout、收款、发票、订阅和退款等外部支付对象。它并不直接决定应用内部所有访问行为。应用需要在本地维护一套可追溯的账务与权益状态，并定义 Stripe 事件如何更新这些状态。

| 事实 | 权威来源 | 责任 |
| --- | --- | --- |
| 客户实际是否付款、Provider 退款是否成功 | Stripe 对象与已验签事件 | 证明外部支付结果 |
| 本地 invoice/payment/refund 账务记录 | Accounts 财务账本 | 记录外部财务事实，不以套餐标价伪造收款 |
| 当前套餐、订阅生命周期、配额上限和重置日 | Accounts 本地订阅/权益模型 | 决定产品内权益 |
| 计量与使用量 | Billing / 用量存储 | 记录实际消耗，不能因重复支付事件被重置 |
| Portal 页面展示 | Portal 经 BFF 读取 Accounts | 呈现同一份服务端状态，不自行推断已付款或授予权益 |
| 节点/Agent 是否允许新连接 | Accounts 访问策略及 Agent 同步结果 | 将权益变化落实到服务访问 |

关键原则是：**浏览器回跳不是付款证明，Webhook 签名也不代替账户归属核验；权益只在可信的支付事实与业务校验都成立后改变。**

```text
用户 → Portal → Accounts 创建 Checkout Session → Stripe Checkout
                                            ↓
用户浏览器 ← success/cancel URL ←──────────┘

Stripe → Accounts Webhook → 验签/模式/归属 → 持久事件处理
                          → invoice/payment/refund 账务事实
                          → subscription/lifecycle/quota 权益投影
                          → 访问策略 revision / Agent 同步
                          → Portal 轮询或订阅状态刷新
```

## 一、先把支付模式、环境和密钥边界做对

Sandbox 与 Live 是两套独立的支付环境。同一产品在两个模式下可以有不同的 Price ID、API key、Webhook endpoint 和 signing secret。配置应按支付模式命名，例如 `SANDBOX_STRIPE_*` 与 `STRIPE_*`（Live），不要把部署代号 部署版本 编进变量名；部署版本和 Stripe 支付模式是两个维度。

| 配置项 | Sandbox | Live | 放置位置 |
| --- | --- | --- | --- |
| Webhook URL | Sandbox Accounts 的 HTTPS endpoint | Live Accounts 的 HTTPS endpoint | 公开配置/运维文档 |
| Secret API key | Sandbox secret key | Live secret key | Vault → Accounts 服务端 |
| Webhook signing secret | 对应 Sandbox endpoint 的 secret | 对应 Live endpoint 的 secret | Vault → Accounts 服务端 |
| Price ID | Sandbox 产品目录价格 | Live 产品目录价格 | 套餐目录/受控配置 |
| Publishable key | 只有确需浏览器 Stripe.js 才由前端构建使用 | 同左 | 前端公开配置；不得放 Secret key |

每个 endpoint 有自己的 signing secret。Stripe CLI 本机监听器输出的 `whsec_...` 只用于 CLI 转发的本地监听器，不能代替 Dashboard 中远程 endpoint 的 signing secret。Secret 值只通过既有 Vault/密钥注入流程传递；日志只打印“已配置/缺失”之类状态，不打印值或可逆编码。

服务启动和每次事件处理都应做 fail-closed 校验：识别当前 `STRIPE_MODE`，确认 API key 类型和允许的 key 前缀/类型相符；Webhook 必须有明确的 `livemode`，与运行模式相符；未知、缺失或矛盾配置在产生 Stripe API 副作用或写入任何业务事实之前拒绝。不要只验证 Sandbox 收到 Live 事件，也要验证 Live 收到 Test 事件会被拒绝。Connect 账户事件若产品不支持，也应明确拒绝或隔离。

Stripe MCP 很适合核对当前账户、mode、Price、Subscription、Invoice、PaymentIntent、Refund、Event 和 endpoint 监听项。查询前先确认选中的账号和 `livemode`；把 MCP 当作诊断证据，不要把它当作生产业务数据库写工具。写操作要有明确授权、幂等键、目标对象核验和可审计记录。

## 二、建立本地套餐目录，不让浏览器决定价格

用户可以选择 `planId`，但金额、币种、周期、额度、Price ID、是否允许新购/变更必须由服务端套餐目录决定。浏览器传来的价格或任意 Stripe 参数不能成为收费依据。

一次目录核验至少包括：

1. Stripe Sandbox 与 Live 分别存在所需 Product/Price；核对 `active`、币种、单位金额、recurring interval、interval count、税务策略和产品归属。
2. 每个内部套餐只有预期的 Price 映射；数据库迁移里的 `NULL stripe_price_id` 只是初始化状态，不能单独证明运行配置缺失，也不能证明后台已配置成功。
3. 代码目录、运行环境映射和 Stripe Dashboard 三边一致，并有可重复的只读核验记录。
4. 订阅周期与权益周期分开建模。例如年付可以每年收款、每自然月发放额度；不能把年费误发成全年总额度。
5. Free/人工赠送等非 Stripe 权益不伪造 Stripe Price，也不生成虚假 payment。

历史 Sandbox 核验过的目录包括 Plus 月付 ¥20/20 GiB、Pro 月付 ¥50/50 GiB、Pro 年付 ¥500/不限流量。文章记录的是曾核实的业务映射；变更产品目录后仍需对当前模式重新读取验证。

## 三、Checkout 要有预览、并发保护和正确回跳

### 服务端创建 Session

Checkout API 应从已认证会话得到用户和账单账户身份，只接受服务端允许的 `planId`/受控价格选择；服务端再次检查套餐状态、当前订阅、欠费发票、未完成操作、支付模式、币种和价格。用户传入的 email 不能用来绑定账单归属。

在创建 Checkout 前，通常还需要：

- 对目标变更生成服务端预览，说明应付金额、套餐/额度变化、生效时间、续费时间和 proration 规则。
- 对同一账户同一变更持久化 pending operation，使用稳定幂等键；重复点击、并发请求和网络重试不得创建多份有效订阅或重复扣款。
- 对现有订阅明确允许的变更组合。暂不支持的降级或年付转换应在 UI/API 返回一致、可理解的原因，不允许 Stripe Checkout 绕过业务规则。
- `success_url` / `cancel_url` 使用配置允许列表中的 HTTPS Portal 域名；不能接受任意用户输入 URL。检查子路径、反向代理、CORS、CSRF、Cookie SameSite 与登录态恢复。
- Session metadata 只放不可变内部关联标识和版本化操作引用；不要放密钥、卡资料或不必要的个人信息。

### 回跳页面只负责恢复体验

`success_url` 表示浏览器从 Stripe 页面返回，可能早于 Webhook，也可能回跳但付款失败/未结算。回跳页应提示“正在确认”，轮询服务端 pending/订阅状态并在事实收敛后刷新；不能根据 URL 参数自行升级账户。cancel URL 清除本次浏览器流程状态，保留原套餐与配额。

前端错误信息要保留稳定错误码与可定位的关联 ID，向用户展示安全、具体的下一步。不要把 409 一律改成“支付失败”：它可能是当前订阅/发票冲突，需要刷新订阅、结清当前发票或走受支持的变更流程。

## 四、Webhook 是可靠消息消费，不是一个 HTTP 回调函数

### 接收阶段

1. 基于原始 request body 验证 `Stripe-Signature` 与该 endpoint 的 signing secret；不能先 JSON 重序列化再验签。
2. 校验 event ID、type、明确的 `livemode`、Stripe account/context 和对象所属关系。
3. 将 event ID、类型、模式、接收时间、状态和安全关联写入持久事件表，并通过唯一约束防止重复接收。
4. 对无法验签或模式不匹配的事件返回 4xx，并且不创建账务或权益副作用。
5. 对已验签但临时数据库/处理错误的事件返回可重试状态（例如 5xx），不要先回 2xx 再把事件永久标记完成。

### 处理阶段

事件至少要有 `received / processing / processed / failed` 之类的持久状态，明确处理租约或并发互斥、尝试次数、最后错误分类与可恢复时间。副作用与完成标记之间的崩溃窗口必须能重放修复；重复事件应能检查并修复目标后置条件，而不重复入账或发放额度。

Stripe 事件可能重复、乱序或在本地依赖尚未到达时先到。处理器应：

- 用 Provider event ID 做投递去重，用 invoice/payment/refund/subscription 的 Provider object ID 做跨事件对象幂等；外部 ID 是引用，不是本地主键。
- 必要时从 Stripe 当前对象读取最新状态，结合本地 invoice/payment/subscription 关系核对；不要假设单个事件快照包含完整关联对象。
- 对缺少本地前置事实的事件保留可重试错误或进入对账队列，不能静默丢弃后返回成功。
- 定义事件版本、API 版本、分页/expand 行为和兼容解析。对 Clover 等新快照结构，提取字段要有明确回归测试，且历史事件要保留兼容处理。
- 先提交账务事实，再按事务边界或可恢复操作更新权益；如果跨库/外部 Agent 无法同事务，使用 outbox/revision/重试而非“写完就假设同步成功”。

## 五、把账务事实与权益投影分开

本地账务要保存 Provider 发票、实际支付、退款、币种、最小货币单位金额和对象关联。账单标价不等于到账金额：折扣、税、零额发票、部分付款、异步支付和失败支付都要明确定义。金额冲突、币种冲突、对象归属不明要停止自动入账并进入可审计核对流程。

订阅表描述生命周期；权益投影描述当前可用套餐、流量上限、周期、重置时间和访问状态。两者通过明确规则联系：

- Free 首次付费成功：从 Free 进入付费套餐，应授予完整的新周期额度。
- 同周期升级：按已定义的 proration/差额规则改变上限，保留已用量，不能把“已用”重置成 0 或把新额度再加一遍。
- 续费：根据新周期账务事实推进周期和额度；同一 invoice 的重复事件不得重复重置。
- 取消：按期取消时，当前已付周期仍可使用，周期结束后再转 Free。
- 失败付款：只进入明确的欠费/宽限策略；不得因为 Checkout 创建成功就授予新额度。
- 全额退款：仅在 Stripe 已确认退款成功且本地能把退款、支付、invoice、订阅和账户关联核实后，按产品退款策略撤销对应权益；不能误降账户上其他仍有效的付费订阅。
- 部分退款、pending 或失败退款：不按全额退款路径立即撤销订阅。处理规则应显式化并覆盖争议/撤销事件。
- 退款、取消、到期、人工暂停和额度耗尽是不同原因，不能只用单一 `active` 布尔值覆盖。

审计事件保留转换前后状态、来源、操作人/系统、原因、时间、幂等键与关联 ID。金融历史和用量事实不可因用户降级而删除。

## 六、订阅状态必须一路传到 Agent 访问策略

购买成功之后，用户体验的终点不是数据库里的 `plan=PLUS`，而是用户在规定时间内能够建立应有连接；退款/额度耗尽之后，也必须按策略阻止新的访问。

推荐使用单调递增的权益 revision 或可靠 outbox：

1. Accounts 事务更新 subscription/lifecycle/quota/访问策略版本。
2. 产生一个可重试的同步任务/事件，绑定 account 与 revision。
3. Portal、Agent 控制面和节点读取同一权益快照或版本。
4. Agent 应用新 revision 后回执；重复消息幂等，旧 revision 不覆盖新状态。
5. 同步失败保持“待同步”并呈现可诊断原因；恢复成功后清除 pending，并让连接发现逻辑读取新快照。

状态页不要把额度显示正常等同于 Agent 已恢复。反过来，非账单策略拒绝（比如人工暂停或策略缺失）也不应被伪装成支付问题。对 `/api/account/policy` 这类策略接口要区分“允许的空策略”与存储/读取故障；对 Agent 节点 API 的 403 需记录脱敏原因码，区分暂停、额度、订阅、策略、资源不可用等门禁。

端到端验收要观察：账务已到账 → 权益 revision 增长 → pending 清除 → 页面状态刷新 → Agent/节点策略更新 → 新连接成功。HTTP 200、额度卡更新或已有连接仍存活都不能单独证明新连接恢复。

## 七、退款是一个可恢复的财务操作状态机

退款不能只是“调用 Stripe refund API 然后改订阅”。至少应持久记录：资格/人工审核结果、操作请求、幂等键、Provider refund ID、退款状态、金额/币种、对账状态、权限撤销结果和通知/审计。

典型流程：

```text
退款申请 → 资格与 MFA 校验 →（需要时）人工审核
         → 创建持久操作与幂等键 → Stripe Refund
         → Provider 确认 succeeded → 本地退款账务落账
         → 订阅/权益按策略调整 → Agent 同步 → 完成审计
```

超时不能直接重新创建第二笔退款：先按幂等键或 Provider 对象查询原请求状态，再决定继续、等待或人工对账。Provider 已成功但本地写入失败时，要从同一个 Refund/事件恢复；退款成功但 Agent 同步失败时，账务与权益应保留一致的中间状态并重试同步。用户退款申请、管理员批准、Stripe 退款成功和最终权益撤销是不同状态，UI 和审计不应混成一个“已退款”字段。

## 八、测试要覆盖失败、重放和真实 Sandbox 链路

### 单元与集成测试

- 金额/币种/Price/interval 映射、折扣税费、零额发票、失败付款。
- 相同事件重复投递、不同事件指向同一 invoice/payment/refund、并发领取、处理崩溃后重启、finalize 失败再投递。
- 乱序：refund 先于 payment、subscription update 先于 invoice、取消和付款事件交错。
- 错误签名、缺 `livemode`、Test/Live 双向串用、Connect account 未支持、账户/对象归属不匹配。
- 部分退款、全额退款、pending/失败/取消中的退款、已处理事件重放修复后置条件。
- Free 首次付费完整额度、付费升级保留用量、续费不双重重置、取消期末降级、失败恢复、退款撤权与其他活跃订阅保护。
- Agent 同步超时、重复 revision、乱序 revision、重启后补发，以及实际新连接成功/拒绝。

### Sandbox 端到端矩阵

| 路径 | Stripe 侧检查 | Accounts/Portal 检查 | Agent 检查 |
| --- | --- | --- | --- |
| Plus 月付成功 | Checkout、Subscription、Invoice、PaymentIntent 状态与 Price | 账务一笔、Plus 配额/周期正确、pending 清除 | 权益 revision 到达，新连接成功 |
| Pro 月付/年付成功 | 正确 interval、币种、金额、续费日 | 年付按月额度规则正确，不一次发全年额度 | 对应访问策略生效 |
| 用户取消 Checkout | 无已付款事实/订阅权益 | 当前套餐和用量不变、操作可重试 | 访问不变 |
| 付款失败后恢复 | invoice.payment_failed 后的恢复账单 | 未支付前不授新权益，恢复后按规则补齐 | 失败期和恢复期门禁正确 |
| 期末取消 | `cancel_at_period_end` 与周期末删除/更新事件 | 当前周期保留，到期后降 Free | 到期策略更新并验证新连接拒绝/Free 规则 |
| 部分/全额退款 | Refund 对象最终状态、关联 PaymentIntent/Charge/Invoice | 部分退款不误撤权；全额退款按策略降级且账务只记一次 | 撤权或其他订阅保护正确 |
| webhook 暂时失败 | Stripe 有重试记录，最终投递成功 | 重放后只一份财务事实，pending 收敛 | 同步恢复且无服务重启依赖 |

### 隔离原则

真实测试卡应只对专用 Sandbox 测试用户、专用 endpoint 和隔离数据库产生事件。若任务目标包含连接恢复，还要有专用 Agent 和测试节点。不要把新测试事件投进含业务数据的 目标部署环境 库，也不要把共享生产 Agent 当故障注入目标。先证明错误模式/错误对象会被拒绝且生产哨兵不变，再做支付验证。

## 九、可观测性与对账

每个事件用 event ID、内部 operation ID、invoice/payment/refund/subscription 本地 ID、account ID（脱敏或不可逆标识）形成关联链。日志应包括接收结果、验签/模式分类、处理状态、重试次数、耗时、幂等命中、最终 revision 和 Agent 回执；不写密钥、完整卡资料、签名头、Session URL 或不必要的个人信息。

运维视图至少需要：

- Webhook 按 endpoint/type/status 的 2xx、4xx、5xx 和延迟；Stripe Dashboard 的 pending delivery 与服务端事件记录交叉核对。
- `received/processing/failed` 的事件积压年龄、超时租约和重放结果。
- Stripe 与本地按日/币种对账：invoice 总额、实际 payment、refund、未匹配对象、差额和重复项。
- 订阅与权益投影不一致、待同步 revision 年龄、Agent ack 差距、页面仍 pending 的账户数。
- 对账修复须幂等、可预览、可审批、可回滚/补偿；禁止用手工 SQL 改业务账本作为常规操作。

Webhook 端点的整体错误率会混入旧 UAT 或其他测试 endpoint。报告应按 endpoint 单独统计，并区别“最近投递成功”与“过去一周曾失败”；不能只看一个账户级 `pending_webhooks` 数字就断定某个 endpoint 的故障原因。

## 十、发布流程也是支付可靠性的一部分

实现代码通过测试，不表示目标环境已经运行它。交付链需要记录：

1. 需求与 GitHub Project 任务关联；各仓库由所属团队维护实现。
2. PR 检查通过并合并到 main；必要时把 Accounts、Portal、GitOps 的变更分别追踪。
3. 用不可变 tag 构建并记录镜像 digest，确认 GitOps 引用的是该 digest。
4. 依据环境既有方式经 SSH → Playbook → GitOps → Doco-CD 发布，避免绕过配置事实源直接手改容器。
5. 发布前后核对 schema 版本、关键财务/订阅哨兵、Stripe mode、配置 key 是否存在、后台 writer 标志和其他服务镜像；无 schema 变更不代表可以忽略数据保护。
6. 分开报告构建、Doco-CD 收敛、容器 digest、健康接口、Webhook 投递、浏览器用户状态、Agent 新连接等验收门槛。
7. 保留失败回滚/前向修复方案；不得把健康检查 200 写成支付闭环完成。

对真实账务环境，必须先明确目标是 Sandbox 还是 Live、是否会产生扣款/退款、数据库是否隔离、是否需要迁移和备份恢复。PR、CI、tag 或用户请求部署本身不能替代商业/数据操作授权。

## 本次排障：退款成功，为什么用户仍显示 Plus 和“同步中”

这次问题展示了为什么 API 连通只覆盖了很小一部分工作。

### 故障一：Stripe 已全额退款，本地仍保留 Plus

Stripe Test 中 ¥20 退款成功，对应的 `charge.refunded` Clover 事件快照没有 invoice 字段。旧处理分支因缺失 invoice 关联提前结束，却把事件记成已处理；再次投递时，系统只看到“已处理”而跳过了权益修正。

修复让 Accounts 从 PaymentIntent → 本地 payment/invoice → subscription 解析关联，核对 Provider 当前状态、全额退款金额/币种和订阅身份，再调用现有撤权策略。重复的已处理事件可以修复缺失的最终权益，但仍只保留一笔本地退款事实。目标部署环境 沙盒账户最终回到 Free 5 GiB；没有直接写数据库，没有 schema migration。

### 故障二：已降级，但套餐按钮一直禁用

另一处状态查询只把 `canceled`、`expired` 等识为终态，遗漏了 `refunded`。`/stripe/subscription/pending` 因查询错误持续返回 pending，Portal 就一直显示“同步中”。Accounts 把 `refunded` 纳入终态后，按钮状态可以收敛；UI 布局没有改动。

### 工程交付证据

- Accounts PR [#262](https://github.com/ai-workspace-services/accounts/pull/262) 修复全额退款事件重放与权益收敛。
- Accounts PR [#263](https://github.com/ai-workspace-services/accounts/pull/263) 修复 `refunded` 终态查询。
- GitOps PR [#492](https://github.com/ai-workspace-infra/gitops/pull/492) 与 [#493](https://github.com/ai-workspace-infra/gitops/pull/493) 更新对应 目标部署环境 不可变发布引用。
- 修复版本经 SSH → Playbook → GitOps → Doco-CD 收敛；Accounts digest 与 schema 版本 已核对，账务核心表发布前后未变。
- 仍需区分代码/服务证据与目标用户浏览器验收；当时活动 Chrome 登录的是另一个账户，不能冒充目标用户页面验收。

## GitHub Project #2：从一次修复变成完整交付计划

Project #2 的父任务 [P0-F #21](https://github.com/ai-workspace-services/.github/issues/21) 把 Stripe Sandbox 闭环分成独立责任与验收面。按 2026-10-21 的项目状态：

| 任务 | 当前状态 | 重点 |
| --- | --- | --- |
| [F0 #22](https://github.com/ai-workspace-services/.github/issues/22) Sandbox 基线与测试隔离 | Done | 当前 mode、Price、endpoint、运行基线核验 |
| [F1 #23](https://github.com/ai-workspace-services/.github/issues/23) Webhook 持久接收、去重与失败重放 | In Progress | 完成失败返回码修复后，仍需并发租约和崩溃窗口验收 |
| [F2 #24](https://github.com/ai-workspace-services/.github/issues/24) Invoice/payment 本地事实 | In Progress | 对象归属、金额、币种、局部失败和重放一致性 |
| [F3 #25](https://github.com/ai-workspace-services/.github/issues/25) 退款持久操作与对账恢复 | In Progress | Provider 成功/本地失败、部分/全额退款、重试和争议事件 |
| [F4 #26](https://github.com/ai-workspace-services/.github/issues/26) 配额与 Agent 热恢复 | In Progress | 权益、访问 revision、页面及真实新连接一致 |
| [F5 #27](https://github.com/ai-workspace-services/.github/issues/27) Portal 账单/退款契约回归 | Todo | UI 布局不变，验证各后端状态映射 |
| [F7 #29](https://github.com/ai-workspace-services/.github/issues/29) Sandbox 闭环验收与放行证据 | Todo | 三套餐、失败/取消/退款和连接恢复总验收 |
| [F8 #32](https://github.com/ai-workspace-services/.github/issues/32) Sandbox/Live 模式对称校验 | Done | 配置不一致时 fail closed |
| [#34](https://github.com/ai-workspace-services/.github/issues/34) Stripe MCP 调试手册 | Done | MCP Sandbox 只读排查、写操作边界 |
| [#35](https://github.com/ai-workspace-services/.github/issues/35) Free 首次付费完整额度激活 | Done | 首购完整额度与升级保留用量分开处理 |
| [F9 #36](https://github.com/ai-workspace-services/.github/issues/36) 隔离 Accounts/DB/Agent | Todo | 为真实 Sandbox 端到端付款及连接验收提供隔离目标 |

此外，订阅状态机与自动降级仍在推进；价格目录/权益分组、套餐年付转换、Provider 抽象和 Portal 契约回归各有独立任务。把它们拆开，能避免把“一个 PR 合并了”误读为“付款、退款、配额、UI 和连接全验收了”。

## 落地检查清单

**接入前：**

- [ ] 画清 Portal、Accounts、Stripe、账务、Billing、Agent 的数据流和事实所有者。
- [ ] Sandbox/Live endpoint、key、signing secret、Price 独立；secret 只进 Vault。
- [ ] 服务端套餐目录、允许的变更矩阵、金额/币种/周期/配额规则已核对。
- [ ] success/cancel URL 在 HTTPS 域名允许列表；身份来自认证会话。

**实现时：**

- [ ] Checkout 创建具备鉴权、预览、幂等和 pending operation。
- [ ] Webhook 基于原始 body 验签，校验 mode、账户、对象归属和 event ID。
- [ ] 事件持久化、并发互斥、可重试；账务与权益更新可恢复。
- [ ] invoice/payment/refund 使用唯一 Provider 引用，但本地主键保持独立。
- [ ] 订阅终态、退款策略、额度周期、取消/欠费宽限均有状态机定义。
- [ ] Agent/节点以 revision 幂等同步，并有 ack/失败重试可观测性。

**验收和发布：**

- [ ] 单元、PostgreSQL 集成、重复/乱序/并发/崩溃测试通过。
- [ ] 隔离 Sandbox 实际 Checkout、付款、退款/取消/失败恢复完成。
- [ ] 页面状态收敛，目标用户实际刷新验证；访问策略和 Agent 新连接验证。
- [ ] Stripe Dashboard 与服务端分别核对 endpoint 投递，不把不同 endpoint 的失败率混算。
- [ ] PR、main、不可变 tag/digest、GitOps、部署和运行验收分开记录。
- [ ] 发布前后 schema 与业务哨兵对照；未授权时不做 DB 直写、不切 Live。

## 参考资料与项目入口

- Accounts 内部：[Stripe Test Mode 对接与验收记录](https://github.com/ai-workspace-services/accounts/blob/main/docs/stripe-test-mode-integration.md)
- Accounts 内部：[Stripe 本地财务事实与 Clover 兼容](https://github.com/ai-workspace-services/accounts/blob/main/docs/architecture/stripe-local-finance-clover.md)
- GitHub Project 追踪：[P0-F Stripe Sandbox 闭环 #21](https://github.com/ai-workspace-services/.github/issues/21)
- Stripe 官方：[Webhooks](https://docs.stripe.com/webhooks) · [订阅 Webhooks](https://docs.stripe.com/billing/subscriptions/webhooks) · [Invoice 对象](https://docs.stripe.com/api/invoices/object) · [Refunds](https://docs.stripe.com/api/refunds)
