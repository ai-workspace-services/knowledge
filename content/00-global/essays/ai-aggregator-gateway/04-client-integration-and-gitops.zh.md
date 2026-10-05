---
title: 再也不用多账号切换了：手把手教你搭建个人专属全能 AI 聚合网关（四）—— 实战篇：统一客户端零心智接入与 GitOps 自动化编排交付
description: 以 Home-Lab 当前部署为例，完成 XConnect、Caddy、New API、CPA 与 LiteLLM 的客户端接入、验证和可回滚交付。
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

前几篇解决了架构、路由和凭据隔离，真正上线还差最后一公里：客户端如何接入，Home-Lab 如何远程维护，配置如何从 Git 交付到主机，又如何在失败时回滚。

本文按当前 Home-Lab 的实际运行基线编写。现行主链路不是“客户端直连 CPA”，也不是把 APISIX 当成唯一入口，而是：

```text
OpenCode / SDK / IDE
        ↓ XConnect-One VPN
Caddy :443（TLS）
        ↓
New API :3000（用户、模型、额度、消费记录）
        ├── CPA（订阅账号矩阵）
        └── LiteLLM（官方 API）
```

Home-Lab 主机为 `xworkmate-bridge.svc.plus`，VPN 地址为 `10.79.0.7`，统一域名为 `ai-internal.onwalk.net`。APISIX/Kong 是可选的认证、限流和租户网关模式；切换前必须单独验证，不能和直连模式同时占用 Caddy 的公网路由。

## 一、先恢复 XConnect，再碰 AI Gateway

XConnect-One 负责 VPN 互联，XConnect APP 负责桌面代理、托盘和后台运行。它们职责不同。SSH 失败时，先检查本机数据面和路由：

```bash
ifconfig utun5
route -n get 10.79.0.7
nc -vz 10.79.0.7 22
ssh -t root@10.79.0.7
```

`utun5` 不存在或没有到 `10.79.0.7` 的路由时，先恢复 XConnect-One 会话；不要在无法确认网络路径的情况下重启 Caddy、New API 或 CPA。登录 Home-Lab 后，再使用远程桌面完成 CPA 的浏览器 OAuth。OAuth bundle 只留在对应实例的本地认证目录，不复制到客户端、Git 或 Vault。

## 二、客户端凭据只进安全存储

客户端使用的是 New API 用户 API Key，不是 APISIX 的 `bootstrap_client_key`，也不是 CPA OAuth token。建议用静默输入临时注入当前 shell，避免把完整密钥写入命令历史：

```bash
printf 'New API user key: '
read -r -s NEW_API_USER_KEY
printf '\n'
export NEW_API_USER_KEY
```

长期使用时，把密钥保存到 OpenCode 的账户凭据存储、操作系统钥匙串或企业密码管理器；不要写进 `opencode.json`、`.env`、README、GitHub Actions artifact 或截图。失效时在 New API 的 `/keys` 页面撤销并重新创建。

## 三、先验证模型目录，再验证真实推理

模型目录只能证明路由和权限可达，不能证明每个模型都能完成推理。外部 DNS 已指向 `10.79.0.7` 时直接请求；排查 DNS 时可以用 `--resolve` 固定目标地址，但仍保留 TLS 校验：

```bash
curl --http1.1 --fail-with-body \
  --resolve ai-internal.onwalk.net:443:10.79.0.7 \
  -H "Authorization: Bearer ${NEW_API_USER_KEY}" \
  -D - \
  https://ai-internal.onwalk.net/v1/models \
  | jq -r '.data[].id'
```

不应使用 `-k` 绕过证书校验，也不要盲目添加 `--noproxy '*'`；Home-Lab 的访问依赖 XConnect 路由。然后从返回目录中挑选一个已验证的模型进行最小请求：

```bash
MODEL=gpt-5.6-luna
curl --http1.1 --fail-with-body \
  -H "Authorization: Bearer ${NEW_API_USER_KEY}" \
  -H 'Content-Type: application/json' \
  https://ai-internal.onwalk.net/v1/chat/completions \
  -d "{\"model\":\"${MODEL}\",\"messages\":[{\"role\":\"user\",\"content\":\"Reply with only OK.\"}],\"max_tokens\":16}"
```

Claude Messages 使用 Anthropic 原生头部：

```bash
curl --http1.1 --fail-with-body \
  -H "x-api-key: ${NEW_API_USER_KEY}" \
  -H 'anthropic-version: 2023-06-01' \
  -H 'content-type: application/json' \
  https://ai-internal.onwalk.net/v1/messages \
  -d '{"model":"claude-sonnet-5","max_tokens":16,"messages":[{"role":"user","content":"Reply with only OK."}]}'
```

失败时按层定位：TLS/域名看 Caddy，`401` 看 New API 用户 Key，模型权限和余额看 New API 控制台，CPA 订阅看对应账号状态，官方 API 错误看 LiteLLM Provider 和用量日志。

## 四、OpenAI、Claude Code 与 IDE 接入

OpenAI SDK 使用统一的 `/v1` 前缀：

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://ai-internal.onwalk.net/v1",
    api_key=os.environ["NEW_API_USER_KEY"],
    timeout=60,
    max_retries=0,
)
answer = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=[{"role": "user", "content": "Reply with only OK."}],
)
print(answer.choices[0].message.content)
```

Anthropic SDK 和 Claude Code 使用不带 `/v1` 的根地址：

```bash
export ANTHROPIC_BASE_URL=https://ai-internal.onwalk.net
export ANTHROPIC_API_KEY="$NEW_API_USER_KEY"
claude --model claude-sonnet-5
```

OpenCode、Cursor、Android Studio 或其他 OpenAI-compatible 客户端，只需配置：

```text
Base URL: https://ai-internal.onwalk.net/v1
API Key: 通过应用的安全凭据入口保存
Model: 从 /v1/models 返回的真实模型 ID
```

OpenCode 桌面版在 Providers/Add account 中建立自定义 Provider；CLI 使用其认证存储。`opencode.json` 可以保存 endpoint、Provider 和模型映射，但不保存 API Key。不同客户端对 Responses、Chat Completions、Messages 的支持不同，接入后应分别发送最小请求，不要只以模型下拉列表作为验收。

## 五、固定版本的一行安装与部署

公共组件仓库为 `ai-workspace-services/ai-aggregato-Gateway`。生产和 Home-Lab 都应固定审核过的 tag 或完整 commit，不能直接执行 `main`：

```bash
export REF=<reviewed-commit-or-tag>
curl -fsSL "https://raw.githubusercontent.com/ai-workspace-services/ai-aggregato-Gateway/${REF}/scripts/home-lab/one-shell.sh" \
  | bash -s -- --ref "$REF"
```

默认动作只有本地安装和预检，不会 SSH、不读取 Token，也不会修改 Home-Lab。对 `PersonalAIAggregator` GitOps 清单，先执行可审计的 `plan`：

```bash
curl -fsSL "https://raw.githubusercontent.com/ai-workspace-services/ai-aggregato-Gateway/${REF}/scripts/home-lab/one-shell.sh" \
  | bash -s -- --ref "$REF" --operation plan \
    --inventory /path/to/inventory.ini \
    --manifest /path/to/ai-aggregator.yaml
```

如果目标是已有的单节点 VPS 或云主机，可以让脚本生成非敏感的 inventory 和单节点清单。三种网络模式的含义是：

```text
public      ：SSH/服务公网 IP → DNS 公网 IP → Caddy 公网接口
private-nat ：SSH/服务私网 IP → DNS 公网 IP → NAT/端口转发 → Caddy 私网接口
xconnect    ：SSH/服务 XConnect IP → split-horizon DNS XConnect IP → Caddy XConnect 接口
```

公网节点示例：

```bash
curl -fsSL "https://raw.githubusercontent.com/ai-workspace-services/ai-aggregato-Gateway/${REF}/scripts/home-lab/one-shell.sh" \
  | bash -s -- --ref "$REF" \
    --domain ai.example.com \
    --target-ip 198.51.100.20 \
    --network-mode public
```

私网 NAT 节点必须把 SSH 私网地址和 DNS 公网地址分开：

```bash
curl -fsSL "https://raw.githubusercontent.com/ai-workspace-services/ai-aggregato-Gateway/${REF}/scripts/home-lab/one-shell.sh" \
  | bash -s -- --ref "$REF" \
    --domain ai.example.com \
    --target-ip 10.0.0.10 \
    --dns-ip 198.51.100.20 \
    --network-mode private-nat
```

Home-Lab 使用 XConnect-One 地址：

```bash
curl -fsSL "https://raw.githubusercontent.com/ai-workspace-services/ai-aggregato-Gateway/${REF}/scripts/home-lab/one-shell.sh" \
  | bash -s -- --ref "$REF" \
    --domain ai-internal.onwalk.net \
    --target-ip 10.79.0.7 \
    --network-mode xconnect
```

脚本不会申请云资源、修改 DNS 或生成凭据。公网模式默认使用 Caddy 自动 TLS；XConnect 模式默认使用已有 runtime TLS 文件。生成清单后，仍需确认主机前置条件、Vault 访问和人工 OAuth。

以上命令默认只生成目标文件；确认 DNS、TLS、Vault 和主机前置条件后，加上 `--operation activate` 才会调用 bundled direct-New-API playbook 执行远程变更：

```bash
curl -fsSL "https://raw.githubusercontent.com/ai-workspace-services/ai-aggregato-Gateway/${REF}/scripts/home-lab/one-shell.sh" \
  | bash -s -- --ref "$REF" --operation activate \
    --domain ai.example.com \
    --target-ip 198.51.100.20 \
    --network-mode public
```

这不是云资源 provisioning；目标机仍需预先具备 SSH/sudo、Caddy、New API、LiteLLM、CPA、Vault 运行时注入和数据库。

只有在 `plan` 检查、人工 OAuth、模型推理、额度记录和回滚条件都完成后，才执行 `stage`、验证，再执行 `activate`。脚本不会接收或打印任何客户端密钥；Ansible role 从 Vault 注入服务秘密，CPA OAuth 仍由人工在远程桌面完成。

当前 Home-Lab 直连 New API 的过渡声明使用 `UnifiedAIGateway`，必须显式指定现有 `ai-workspace-infra/playbooks/deploy_ai_gateway_direct_new_api.yml`，并以 `activate` 表示这是会修改 Caddy 的应用操作：

```bash
curl -fsSL "https://raw.githubusercontent.com/ai-workspace-services/ai-aggregato-Gateway/${REF}/scripts/home-lab/one-shell.sh" \
  | bash -s -- --ref "$REF" --operation activate \
    --inventory /path/to/inventory.ini \
    --manifest /path/to/ai-gateway-unified.yaml \
    --playbook /path/to/ai-workspace-infra/playbooks/deploy_ai_gateway_direct_new_api.yml
```

该过渡 playbook 会先检查 New API、本地保存 Caddy 片段、校验候选配置，再 reload；验证失败时恢复备份。它不是通用的 dry-run，执行前必须人工确认目标 inventory 和 manifest。APISIX/Kong 统一模式另有独立 playbook，不能通过这个直连入口误切换。

## 六、GitOps 交付边界与真实闸门

五个仓库各司其职：`gateway` 保存契约、renderer、脚本和 Home-Lab 文档；`gitops` 保存域名、节点、模型和生命周期；`playbooks` 负责 systemd、Caddy、New API、LiteLLM、CPA；`platform-ops-toolkit` 做 schema、secret scan、Ansible 和 UAT 编排；`knowledge` 保存架构与运维事实。

实际交付顺序不是“提交 YAML 就自动上线”，而是：

```text
Git PR → 静态校验 → plan → stage → 人工 OAuth
      → /v1/models → 最小推理/streaming → 额度与回滚验证 → activate
```

当前 UAT 的 `PersonalAIAggregator` 清单仍可能是 `enabled: false` 或缺少固定 artifact revision；`UnifiedAIGateway` 即使声明 `enabled: true`，其 quota、CPA、LiteLLM acceptance 仍需要完成后才能激活。清单状态与主机实时状态必须分开核对，不能用“PR 已合并”替代线上验收。

## 结语：统一入口只是开始

客户端最终只记住一个域名、一个用户 Key 和一组标准模型名；复杂度被留在 New API 的用户与额度账本、CPA 的账号隔离、LiteLLM 的官方 Provider 适配，以及可审计的 GitOps 交付链中。真正可靠的标准不是“页面能打开”，而是每次变更都有固定版本、明确闸门、真实推理证据和可执行回滚。

下一篇将进入最容易踩坑的深水区：
**《再也不用多账号切换了：手把手教你搭建个人专属全能 AI 聚合网关（五）—— 排障篇：真实推理避坑实测与 Home-Lab 运维巡检复盘》**。

原文与完整 CPA OAuth 操作可继续阅读：
[AI Aggregator Gateway：CPA OAuth 登录与凭据隔离 TLDR](https://github.com/ai-workspace-services/knowledge/blob/main/content/04-infra-platform/apisix/ai-aggregator-cpa-oauth-tldr.zh.md)
