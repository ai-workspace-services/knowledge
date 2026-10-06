---
title: 再也不用多账号切换了：手把手教你搭建个人专属全能 AI 聚合网关（四）—— 实战篇：统一客户端零心智接入与 GitOps 自动化编排交付
description: 像 Quick Start 一样，在任意 VPS 或云主机上完成 AI 聚合网关的准备、安装、验证和回滚，并以 Home-Lab 作为实际示例。
slug: ai-aggregator-gateway-04-integration
lang: zh
date: 2026-10-05T00:00:00Z
author: shenlan
tags:
  - ai-gateway
  - gitops
  - ansible
  - sdk
  - claude-code
category: essays
---

# 再也不用多账号切换了：手把手教你搭建个人专属全能 AI 聚合网关（四）

前几篇完成了架构、路由和凭据隔离。本篇只做一件事：把已经设计好的网关真正接起来。结构参考 K3s Quick Start：先确认条件，再执行一条默认命令，接着验证结果；需要特殊网络或自定义清单时，再进入高级模式。

本文的脚本是通用部署入口，不绑定某个云厂商或某台主机。它可以部署到已有的 VPS、云主机或内网服务器；目标主机只需要满足 SSH、sudo、运行时依赖和网络可达条件。Home-Lab 仅用于展示一套已运行的实例。

本方案面向个人和工作站使用。XConnect-One 不只是传输通道，也是私有网络和工作站之间的安全边界：优先让可信设备通过 VPN 访问网关，减少公网暴露面。它不是为了搭建面向陌生用户的公开 Token 中转站；客户端 Key、用户额度和上游 OAuth 仍由 New API、Vault 与 CPA 本地目录分别管理。

标准链路如下：

```text
OpenCode / SDK / IDE
        ↓
Caddy :443（TLS）
        ↓
New API :3000（用户、模型、额度、消费记录）
        ├── CPA（订阅账号矩阵）
        └── LiteLLM（官方 API）
```

Home-Lab 的实际参数是 `ai-internal.onwalk.net` 和 `10.79.0.7`，网络通过 XConnect-One 访问；这些参数只作为示例，不是公共脚本的唯一目标。APISIX/Kong 是可选认证、限流和租户网关模式，不是本篇默认链路。

## 开始前：准备目标主机

任意部署目标都需要：

- 可用的 Linux 主机、SSH 用户和 sudo 权限；
- Caddy、New API、LiteLLM、CPA、PostgreSQL 及 Vault 运行时依赖；
- 域名解析到目标入口，或通过 NAT、split-horizon DNS、XConnect 提供可达路径；
- Vault 已准备好对应环境的数据库、网关和 Provider 秘密；
- CPA 的 OAuth 登录可在目标节点的远程桌面中人工完成。

脚本负责应用配置和部署，不负责创建云资源、修改 DNS 或生成凭据。CPA OAuth bundle 只留在对应实例的本地认证目录，不复制到客户端、Git、Vault、Terraform state 或 CI artifact。

如果目标通过 XConnect 访问，先恢复 XConnect-One，再检查 VPN 数据面和路由：

```bash
ifconfig utun5
route -n get 10.79.0.7
nc -vz 10.79.0.7 22
ssh -t root@10.79.0.7
```

`utun5` 或到目标地址的路由不存在时，先修复 XConnect，不要在网络路径不明时重启 AI Gateway。

## 默认安装：无参数启动 Quick Start

先固定一个已经审核的提交或标签。不要直接使用不受控的 `main`：

```bash
export REF=<reviewed-commit-or-tag>
```

然后执行默认安装命令。管道后的 `bash` 不需要任何参数：

```bash
curl -fsSL \
  "https://raw.githubusercontent.com/ai-workspace-services/ai-aggregato-Gateway/${REF}/scripts/home-lab/one-shell.sh" \
  | bash
```

无参数时，脚本按“默认目标”执行安装。默认目标由 `AI_AGGREGATOR_*` 环境变量和目标清单决定；本地未覆盖时，当前示例版本提供 Home-Lab 默认值：

```text
域名：ai-internal.onwalk.net
目标地址：10.79.0.7
网络模式：xconnect
操作：activate
```

因此这条命令可直接用于当前 Home-Lab；部署到其他环境时，可以在同一条命令前设置目标环境变量，管道后的 `bash` 仍然不需要参数：

```bash
export AI_AGGREGATOR_DOMAIN=ai.example.com
export AI_AGGREGATOR_TARGET_IP=198.51.100.20
export AI_AGGREGATOR_NETWORK_MODE=public

curl -fsSL \
  "https://raw.githubusercontent.com/ai-workspace-services/ai-aggregato-Gateway/${REF}/scripts/home-lab/one-shell.sh" \
  | bash
```

私网 NAT 还设置 `AI_AGGREGATOR_DNS_IP`；XConnect 环境设置对应的 `AI_AGGREGATOR_TARGET_IP` 和 `AI_AGGREGATOR_DOMAIN`。脚本不会打印或接收 New API 用户 Key、Vault 密钥、CPA OAuth token 或 Provider API Key。凭据由 Vault、New API 控制台和本地安全凭据存储提供。

## 第一次验证：从目录到真实请求

客户端使用的是 New API 用户 API Key，不是 APISIX 的 `bootstrap_client_key`，也不是 CPA OAuth token。建议临时输入，避免进入命令历史：

```bash
printf 'New API user key: '
read -r -s NEW_API_USER_KEY
printf '\n'
export NEW_API_USER_KEY
```

先验证入口和模型目录。模型目录只能证明路由和权限可达，不代表每个模型都能推理：

```bash
curl --http1.1 --fail-with-body \
  -H "Authorization: Bearer ${NEW_API_USER_KEY}" \
  https://<gateway-domain>/v1/models \
  | jq -r '.data[].id'
```

排查 DNS 时可以固定目标地址，但仍保留 TLS 校验：

```bash
curl --http1.1 --fail-with-body \
  --resolve <gateway-domain>:443:<target-ip> \
  -H "Authorization: Bearer ${NEW_API_USER_KEY}" \
  https://<gateway-domain>/v1/models \
  | jq -r '.data[].id'
```

从返回目录中挑选一个真实模型，发送最小 Chat 请求：

```bash
curl --http1.1 --fail-with-body \
  -H "Authorization: Bearer ${NEW_API_USER_KEY}" \
  -H 'Content-Type: application/json' \
  https://<gateway-domain>/v1/chat/completions \
  -d '{"model":"<verified-model>","messages":[{"role":"user","content":"Reply with only OK."}],"max_tokens":16}'
```

Claude Messages 使用原生请求头：

```bash
curl --http1.1 --fail-with-body \
  -H "x-api-key: ${NEW_API_USER_KEY}" \
  -H 'anthropic-version: 2023-06-01' \
  -H 'content-type: application/json' \
  https://<gateway-domain>/v1/messages \
  -d '{"model":"<verified-claude-model>","max_tokens":16,"messages":[{"role":"user","content":"Reply with only OK."}]}'
```

失败时按链路定位：TLS/DNS 看 Caddy；`401` 看 New API 用户 Key；模型权限、套餐和额度看 New API 控制台；订阅模型失败看对应 CPA 账号；官方 API 失败看 LiteLLM Provider 和用量日志。

## 客户端接入

OpenAI SDK 的根地址带 `/v1`：

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://<gateway-domain>/v1",
    api_key=os.environ["NEW_API_USER_KEY"],
    timeout=60,
    max_retries=0,
)
response = client.chat.completions.create(
    model="<verified-model>",
    messages=[{"role": "user", "content": "Reply with only OK."}],
)
print(response.choices[0].message.content)
```

Claude Code 使用根域名，不额外拼 `/v1`：

```bash
export ANTHROPIC_BASE_URL=https://<gateway-domain>
export ANTHROPIC_API_KEY="$NEW_API_USER_KEY"
claude --model <verified-claude-model>
```

OpenCode、Cursor、Android Studio 和其他 OpenAI-compatible 客户端填写：

```text
Base URL: https://<gateway-domain>/v1
API Key: 使用应用的安全凭据入口保存
Model: 使用 /v1/models 返回的真实模型 ID
```

OpenCode 桌面版在 Providers/Add account 中建立自定义 Provider；CLI 使用自身的认证存储。`opencode.json` 只保存 endpoint、Provider 和模型映射，不保存 API Key。配置完成后必须发送最小请求，不能只以模型下拉列表作为验收。

## 高级模式：预览、网络和自定义清单

查看所有参数：

```bash
curl -fsSL \
  "https://raw.githubusercontent.com/ai-workspace-services/ai-aggregato-Gateway/${REF}/scripts/home-lab/one-shell.sh" \
  | bash -s -- --help
```

只生成目标文件、不修改远端主机：

```bash
curl -fsSL \
  "https://raw.githubusercontent.com/ai-workspace-services/ai-aggregato-Gateway/${REF}/scripts/home-lab/one-shell.sh" \
  | bash -s -- --operation plan
```

三种网络模式对应三种地址关系：

```text
public      ：SSH/服务公网 IP → DNS 公网 IP → Caddy 公网接口
private-nat ：SSH/服务私网 IP → DNS 公网 IP → NAT → Caddy 私网接口
xconnect    ：SSH/服务 XConnect IP → split-horizon DNS → Caddy XConnect 接口
```

公网 VPS：

```bash
curl -fsSL \
  "https://raw.githubusercontent.com/ai-workspace-services/ai-aggregato-Gateway/${REF}/scripts/home-lab/one-shell.sh" \
  | bash -s -- --ref "$REF" --operation activate \
    --domain ai.example.com \
    --target-ip 198.51.100.20 \
    --network-mode public
```

私网 NAT 必须区分 SSH 私网地址和 DNS 公网地址：

```bash
curl -fsSL \
  "https://raw.githubusercontent.com/ai-workspace-services/ai-aggregato-Gateway/${REF}/scripts/home-lab/one-shell.sh" \
  | bash -s -- --ref "$REF" --operation activate \
    --domain ai.example.com \
    --target-ip 10.0.0.10 \
    --dns-ip 198.51.100.20 \
    --network-mode private-nat
```

XConnect Home-Lab 可以显式写出默认值：

```bash
curl -fsSL \
  "https://raw.githubusercontent.com/ai-workspace-services/ai-aggregato-Gateway/${REF}/scripts/home-lab/one-shell.sh" \
  | bash -s -- --ref "$REF" --operation activate \
    --domain ai-internal.onwalk.net \
    --target-ip 10.79.0.7 \
    --network-mode xconnect
```

自定义 `inventory`、manifest 或 playbook 时，先执行 `--operation plan`，确认生成文件和目标地址，再显式执行 `activate`。当前 Home-Lab 直连 New API 的过渡 playbook 是 `ai-workspace-infra/playbooks/deploy_ai_gateway_direct_new_api.yml`；APISIX/Kong 模式使用独立入口，不能通过直连模式误切换。

## 交付顺序和回滚

默认操作是 `activate`，所以执行无参数命令前，应确认 DNS、TLS、Vault、数据库和人工 OAuth 已就绪。更稳妥的交付顺序是：

```text
固定 REF → plan → stage → 人工 OAuth
        → /v1/models → 最小推理/streaming
        → 额度与回滚验证 → activate
```

GitOps 只保存域名、节点、模型和生命周期；`playbooks` 负责 systemd、Caddy、New API、LiteLLM 和 CPA；`platform-ops-toolkit` 负责 schema、secret scan、Ansible 和 UAT；Vault 保存运行时秘密。提交、合并或页面可访问都不等于真实验收，必须保留模型请求和回滚证据。

变更失败时先停止流量切换，保留当前 Caddy 配置和服务状态，恢复上一版固定 REF，再验证 `/v1/models`、Chat 和 Messages。不要手工复制 OAuth 文件或在日志中打印凭据。

## 下一步

完成本篇后，客户端只需要一个域名、一个 New API 用户 Key 和标准模型名；复杂度由网关和 GitOps 链路承担。下一篇将进入真实推理排障、CPA 额度、Provider 映射和 Home-Lab 巡检。

完整的 CPA OAuth 操作可阅读：[AI Aggregator Gateway：CPA OAuth 登录与凭据隔离 TLDR](https://github.com/ai-workspace-services/knowledge/blob/main/content/04-infra-platform/apisix/ai-aggregator-cpa-oauth-tldr.zh.md)。

本文的快速开始结构参考 [K3s 中文快速入门指南](https://docs.k3s.io/zh/quick-start)：先决条件、默认安装、验证结果和高级选项分开说明。
