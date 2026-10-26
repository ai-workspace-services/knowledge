---
title: Stripe 环境隔离规划（dev / SIT / UAT / Prod）
description: Stripe Sandbox 与 Live 模式按环境隔离的密钥、Webhook、Vault 路径、最小权限与迁移规划。
slug: stripe-environments
lang: zh
tags:
  - reference
  - billing
  - stripe
  - vault
---

# Stripe 环境隔离规划（dev / SIT / UAT / Prod）

> 更新日期：2026-10-26。状态：**规划**，尚未实施。本文不包含任何真实密钥、账户 ID、主机或地址。

## 1. 目标与原则

- 每个非生产环境使用独立的 Stripe Sandbox；生产只使用 Live 模式。
- **生产不在 Sandbox 中测试**：Sandbox 与 Live 的数据、Webhook 与密钥互不相通，Sandbox 通过不代表 Live 配置正确。
- 生产验证 = 发布后使用 Live 密钥做冒烟检查（只读接口、Webhook 签名校验等），不做真实扣款回归。
- 非生产环境不涉及真实扣款、真实返现付款。
- 密钥统一用受限密钥（`rk_`），不在服务中使用完整权限的 `sk_` 密钥。

## 2. 环境矩阵

| 环境 | Stripe 空间 | 密钥 | Webhook |
|---|---|---|---|
| dev / 功能泳道 | Sandbox「dev」 | 受限 `rk_test`（替代 `sk_test`），`pk_test` | 每条泳道建自己的端点，或用 `stripe listen` 转发 |
| SIT | Sandbox「sit」 | `rk_test` / `pk_test` | 固定 SIT 端点，自带 `whsec` |
| UAT | Sandbox「uat」 | `rk_test` / `pk_test` | 固定 UAT 端点，自带 `whsec` |
| Prod | Live 模式 | `rk_live` / `pk_live` | 只有生产端点，自带 `whsec` |

## 3. Vault 路径与字段

每个环境一条独立路径：`kv/{dev,sit,uat,prod}/billing/stripe`。

| 字段 | 说明 |
|---|---|
| `STRIPE_SECRET_KEY` | 该环境的受限密钥（`rk_test_…` 或 `rk_live_…`） |
| `STRIPE_PUBLISHABLE_KEY` | 该环境的 `pk_test_…` / `pk_live_…` |
| `STRIPE_WEBHOOK_SECRET` | 该环境端点的 `whsec_…` |
| `STRIPE_ACCOUNT_MODE` | `test` 或 `live`；仅 prod 为 `live` |

功能泳道如需独立 Webhook 端点，可在 dev 路径下按泳道细分（例如 `kv/dev/billing/stripe/<lane>`），只覆盖 `STRIPE_WEBHOOK_SECRET`，其余字段沿用 dev。

## 4. 最小权限

- 每个环境一条 Vault policy，只允许 `read` 本环境路径，例如 `sit-billing-stripe-read` 只能读 `kv/sit/billing/stripe`（KV v2 对应 `data/` 与 `metadata/` 前缀）。
- 非生产的 CI 角色、Kubernetes auth 角色、开发者 token **不能读取** `kv/prod/billing/stripe`。
- prod 路径只绑定生产集群的服务账户与生产发布流水线；写权限仅限安全管理员。
- 禁止把生产密钥复制到任何非生产路径或环境。

## 5. 服务启动校验

服务启动时检查运行环境与密钥前缀，不符合即拒绝启动：

- `env != prod` 时，若 `STRIPE_SECRET_KEY` 以 `sk_live`/`rk_live` 开头，或 `STRIPE_PUBLISHABLE_KEY` 以 `pk_live` 开头，或 `STRIPE_ACCOUNT_MODE=live`，直接失败退出。
- `env == prod` 时，要求 `STRIPE_ACCOUNT_MODE=live` 且密钥为 live 前缀，防止生产误用测试密钥。
- 日志只输出模式与前缀类型，不输出密钥内容。

## 6. Webhook

- 每个端点有自己的 `whsec`，**不跨环境、不跨端点共享**。
- dev 泳道：泳道独立端点，或本地/泳道内用 `stripe listen` 转发（转发生成的临时 `whsec` 只用于该会话）。
- SIT / UAT：各一个固定端点，只订阅业务需要的事件类型。
- Prod：只有生产端点；轮换 `whsec` 时先在 Vault 更新再滚动服务。

## 7. 受限密钥权限范围建议

按服务实际调用的 API 最小授权，示例：

- 支付/订阅：Checkout Sessions、PaymentIntents、Customers、Subscriptions、Prices/Products 读取，按需写。
- Webhook 处理：只需读取相关对象（Events、Charges、Invoices）。
- 返现/转账（Transfers、Payouts）：默认不授予；仅在明确需要的环境单独开启，非生产不涉及真实付款。
- 不授予账户设置、API Keys、Webhook 端点管理等管理类权限；端点由管理员在控制台维护。
- 每个环境、每个服务各发一把受限密钥，便于独立轮换与吊销。

## 8. 从混合路径迁移

现状：`kv/billing-service` 同时存放 `PROD_` 与 `SANDBOX_` 前缀的 `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET`，非生产与生产凭据混在一条路径里，无法按环境做最小权限。

迁移步骤：

1. 在 Stripe 中为 dev / sit / uat 各建 Sandbox，并为各环境签发受限密钥与端点 `whsec`（不复用旧的 Sandbox 密钥到多个环境）。
2. 写入 `kv/{dev,sit,uat}/billing/stripe`；生产 Live 受限密钥写入 `kv/prod/billing/stripe`。
3. 创建各环境 policy，并把服务/CI 角色改绑到新路径。
4. 服务切换读取新路径并上线启动校验（第 5 节），按 dev → SIT → UAT → Prod 顺序推进。
5. 确认无服务再读取旧路径（审计日志）后，备份并吊销旧密钥，**退役** `kv/billing-service`。

## 9. 不在范围内

- 非生产环境的真实扣款、真实返现付款。
- 在 Sandbox 中“测试生产”。
- 本文不记录任何真实密钥、账户 ID、主机或地址。
