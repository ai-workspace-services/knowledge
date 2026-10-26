---
title: Stripe 环境隔离规划（dev / SIT / UAT / Prod）
description: Stripe Sandbox 与 Live 模式的环境使用规则；当前以 V5 基线的 kv/prod/billing-service 为准，按环境拆路径为以后可选。
slug: stripe-environments
lang: zh
tags:
  - reference
  - billing
  - stripe
  - vault
---

# Stripe 环境隔离规划（dev / SIT / UAT / Prod）

> 更新日期：2026-10-26。状态：**当前标准以 V5 基线为准**；第 9 节按环境拆分路径为**以后可选，当前不执行**。本文不包含任何真实密钥、账户 ID、主机或地址。
>
> 依据：
> - [V5 运行基线白皮书](../../content/02-iac-devops/cloud-infrastructure-devsecops-baseline/records/prod-v5-20261023/prod-v5-runtime-and-snapshot-baseline-20261023.zh.md)
> - [Accounts Stripe 恢复 Runbook](https://github.com/ai-workspace-services/accounts/blob/main/docs/Runbook/Stripe-Free-To-Paid-Recovery.md)

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

## 3. Vault 路径与字段（当前标准，V5 基线）

Stripe 密钥保存在既有的 Vault KV v2 路径中，**不新建、不重新创建密钥，不按 V3/V4/V5 分别复制，不加版本后缀**：

- Vault CLI 路径：`kv/prod/billing-service`
- KV v2 HTTP API 路径：`kv/data/prod/billing-service`

| 字段 | 用途 |
|---|---|
| `SANDBOX_STRIPE_SECRET_KEY` | Sandbox API 密钥 |
| `SANDBOX_STRIPE_WEBHOOK_SECRET` | Sandbox Webhook 验签密钥 |
| `PROD_STRIPE_SECRET_KEY` | Live API 密钥 |
| `PROD_STRIPE_WEBHOOK_SECRET` | Live Webhook 验签密钥 |

使用规则：

- 非生产（dev / 功能泳道 / SIT / UAT）**只读取 `SANDBOX_*` 字段**，任何情况下不得切换为 `PROD_*`。
- Prod 使用 `PROD_*` 字段。
- Sandbox 恢复、排障时同样只用 `SANDBOX_*`，不能误切到 `PROD_*`。

## 4. 最小权限（当前）

- 读取 `kv/prod/billing-service` 的角色/token 只授予 `read`，范围限定该路径。
- 非生产注入时只映射 `SANDBOX_*` 字段，不把 `PROD_*` 字段映射或落盘到任何非生产环境。
- 写权限仅限安全管理员。
- **Rootless 原则**：
  - 日常部署与验证只使用非 root、最小权限的 Vault 身份：按环境划分的 role 与 policy（如 CI 走 jwt auth、集群内工作负载走 Kubernetes auth role），非生产只能读取 `SANDBOX_*` 字段。
  - root token 仅作 break-glass：需要时临时生成（如 `vault operator generate-root`），用完立即吊销，不保存、不用于日常操作。
  - 工作负载本身也以非 root 运行（`runAsNonRoot`、非 0 UID、只读根文件系统等）。
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

## 9. 按环境拆分路径（以后可选，当前不执行）

> 以下内容仅作未来选项记录，**当前不执行**；当前标准见第 3、4 节。

可选目标：每个环境一条独立路径 `kv/{dev,sit,uat,prod}/billing/stripe`，字段为 `STRIPE_SECRET_KEY`、`STRIPE_PUBLISHABLE_KEY`、`STRIPE_WEBHOOK_SECRET`、`STRIPE_ACCOUNT_MODE`（仅 prod 为 `live`）；功能泳道可在 `kv/dev/billing/stripe/<lane>` 只覆盖 `STRIPE_WEBHOOK_SECRET`。每个环境一条只读 policy，非生产角色不能读取 prod 路径。

如未来决定实施，可参考步骤：

1. 在 Stripe 中为 dev / sit / uat 各建 Sandbox，并签发受限密钥与端点 `whsec`。
2. 写入各环境路径，创建对应 policy，把服务/CI 角色改绑到新路径。
3. 服务切换读取新路径，按 dev → SIT → UAT → Prod 顺序推进。
4. 审计确认无服务再读取 `kv/prod/billing-service` 后，再评估是否备份并退役旧字段。

## 10. 不在范围内

- 非生产环境的真实扣款、真实返现付款。
- 在 Sandbox 中“测试生产”。
- 本文不记录任何真实密钥、账户 ID、主机或地址。
