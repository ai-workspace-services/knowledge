# AI Aggregator Gateway 对接与验证 TLDR

本文衔接 [AI Aggregator Gateway：选型、架构与 Home-Lab 实施](./ai-aggregator-gateway-architecture.zh.md)，用于完成 CPA OAuth 后的客户端对接。验收记录日期：2026-10-01；记录是当时实测快照，重新部署后需重复检查。

## 1. 接入契约

```text
客户端 AI_GATEWAY_CLIENT_KEY
  → Caddy TLS
  → APISIX 认证、ACL、限流
  → 注入独立的 New API 客户端 Token
  → New API 按模型选择 CPA Channel
  → CPA 内部 Channel Token → 本地 OAuth → Provider
```

客户端只需要一个网关 Token。APISIX 接受 `Authorization: Bearer`、`x-api-key` 或 `apikey`，随后使用内部 Token 访问 New API。客户端无须同时提供两个密钥。New API 客户端 Token 与 New API→CPA Channel Token 是不同凭据。

| 客户端 | Base URL | SDK 请求格式 |
| --- | --- | --- |
| OpenAI SDK、支持自定义端点的 IDE/Agent | `https://ai-internal.onwalk.net/v1` | Bearer；Chat / Responses |
| Anthropic SDK、Claude Code | `https://ai-internal.onwalk.net` | `x-api-key`；`/v1/messages` |

域名解析到内网 `10.79.0.7`，客户端必须有对应内网/VPN 可达性。Cursor 等产品仅在支持自定义 Base URL 的功能中使用；不能据此保证所有 IDE 功能均兼容。旧 `ai.onwalk.net` 不作为本次 Home-Lab 验收入口。

## 2. 凭据准备

Vault 逻辑路径为 `kv/uat/ai-aggregator/gateway/apisix#bootstrap_client_key`，KV v2 API 路径为 `kv/data/uat/ai-aggregator/gateway/apisix`。客户端变量统一叫 `AI_GATEWAY_CLIENT_KEY`。

在客户端终端通过隐藏输入设置，避免明文写入 shell history：

```bash
read -r -s -p 'Gateway token: ' AI_GATEWAY_CLIENT_KEY; printf '\n'
export AI_GATEWAY_CLIENT_KEY
```

以上使用 Bash；macOS zsh 可用 `read -r -s 'AI_GATEWAY_CLIENT_KEY?Gateway token: '`。需要查看密钥时，通过受控 Vault UI/凭据管理流程获取，不粘贴到聊天或文档。

Home-Lab root shell 可从受限运行文件加载：

```bash
AI_GATEWAY_CLIENT_KEY=$(< /run/ai-aggregator/apisix/client-key)
export AI_GATEWAY_CLIENT_KEY
```

该文件是 tmpfs 上的 `root:root 0600` 运行时明文。APISIX 路由配置含可用认证值，也位于 tmpfs，允许 worker 读取；不能称为“运行时无明文”。内部 New API Token 不发给客户端。不要开启 `set -x`、curl `-v` 或收集包含认证头的日志。

## 3. 列出聚合模型

下面命令校验证书、绕过终端代理，并在失败时返回非零退出码：

```bash
curl --noproxy '*' -fsS \
  -H "Authorization: Bearer ${AI_GATEWAY_CLIENT_KEY}" \
  https://ai-internal.onwalk.net/v1/models \
  | jq -r '.data[].id'
```

DNS 尚未更新时，在同一 curl 命令加入 `--resolve ai-internal.onwalk.net:443:10.79.0.7`。常规接入不使用 `-k` 跳过 TLS 校验。

检查 HTTP 状态与响应体：

```bash
curl --noproxy '*' -sS --http1.1 \
  -H "x-api-key: ${AI_GATEWAY_CLIENT_KEY}" \
  -w '\nHTTP_STATUS=%{http_code}\n' \
  https://ai-internal.onwalk.net/v1/models
```

预期为 `200` 和非空 `data`。返回 `200`、`data: []` 表示目录链路成功但没有可见模型。`000`/`Empty reply` 是传输失败，不能当成成功；检查终端代理、Caddy 与 APISIX worker 日志。`Invalid API key` 来自 APISIX，`new_api_error / Invalid token` 表示内部 New API 认证有问题。

## 4. OpenAI SDK 最小请求

在已有测试虚拟环境安装 `openai`，使用模型目录中的真实模型 ID，不假设 `codex-main` 等别名已配置。

```bash
export OPENAI_BASE_URL='https://ai-internal.onwalk.net/v1'
export OPENAI_API_KEY="$AI_GATEWAY_CLIENT_KEY"
export TEST_OPENAI_MODEL='<从目录选择 GPT 模型 ID>'
```

```python
import os
from openai import OpenAI

client = OpenAI(base_url=os.environ['OPENAI_BASE_URL'],
                api_key=os.environ['OPENAI_API_KEY'], timeout=45, max_retries=0)
model = os.environ['TEST_OPENAI_MODEL']
response = client.chat.completions.create(
    model=model, messages=[{'role': 'user', 'content': 'Reply only OK.'}])
assert response.choices and response.choices[0].message.content
print('OpenAI Chat PASS')

response = client.responses.create(model=model, input='Reply only OK.')
assert response.output
print('OpenAI Responses PASS')

seen = False
for chunk in client.chat.completions.create(
        model=model, messages=[{'role': 'user', 'content': 'Reply only OK.'}], stream=True):
    seen |= bool(chunk.choices and chunk.choices[0].delta.content)
assert seen
print('OpenAI streaming PASS')
```

## 5. Anthropic SDK / Claude Code

在已有测试虚拟环境安装 `anthropic`：

```bash
export ANTHROPIC_BASE_URL='https://ai-internal.onwalk.net'
export ANTHROPIC_API_KEY="$AI_GATEWAY_CLIENT_KEY"
export TEST_CLAUDE_MODEL='<从目录选择 Claude 模型 ID>'
```

```python
import os
from anthropic import Anthropic

client = Anthropic(base_url=os.environ['ANTHROPIC_BASE_URL'],
                   api_key=os.environ['ANTHROPIC_API_KEY'], timeout=45, max_retries=0)
model = os.environ['TEST_CLAUDE_MODEL']
message = client.messages.create(
    model=model, max_tokens=32,
    messages=[{'role': 'user', 'content': 'Reply only OK.'}])
assert message.content
print('Anthropic Messages PASS')

with client.messages.stream(model=model, max_tokens=32,
        messages=[{'role': 'user', 'content': 'Reply only OK.'}]) as stream:
    text = ''.join(stream.text_stream)
assert text
print('Anthropic streaming PASS')
```

Claude Code 使用同一环境变量，执行 `claude --model "$TEST_CLAUDE_MODEL"`，确认实际发出请求。IDE 使用自定义 OpenAI Base URL、同一网关 Token 和可见模型 ID。独立 CPA OAuth 登录与客户端 SDK 接入是两个步骤。

## 6. 验收记录与未完成项

| 检查 | 2026-10-01 实测 |
| --- | --- |
| Caddy→APISIX→New API 内部 Token 转换 | 已修复 |
| 无 Token 请求 | `401` |
| Bearer / x-api-key 查询模型目录 | `200`，非空列表 |
| 四个 CPA 模型目录 | 均可读取 |
| 四个 New API Channel | 均已启用，status=1 |
| Claude 最小推理 | 上游 `403 Request not allowed`，未通过 |
| Google 最小推理 | 测试失败，未通过 |
| GPT 最小推理 | 尚无成功证据 |
| 官方 SDK 完整请求、Responses、streaming、工具调用、IDE/Agent | 待验收 |

两个 Codex 渠道各同步 14 个模型；Claude 同步当时的 17 个模型，Antigravity 同步 12 个。目录可能重叠或变化，不能相加当作独立模型总数。目录可读和渠道 enabled 不证明所有模型都能推理。

后续完成每个平台的最小请求，再验证 streaming、工具调用参数与结果往返、错误格式、跨租户拒绝、限流和单 CPA 故障隔离。记录协议、模型 ID、HTTP 状态、耗时和失败类别；不记录认证值或 OAuth 内容。官方 Provider/LiteLLM 路由需单独验证，本表不覆盖其可用性。

## 7. 运维检查

```bash
systemctl is-active caddy ai-aggregator-apisix ai-aggregator-new-api ai-aggregator-litellm
for id in cpa-codex-01 cpa-codex-02 cpa-claude-01 cpa-antigravity-01; do
  systemctl is-active "ai-aggregator-$id.service"
done
```

APISIX worker 必须可读配置；曾将配置统一设为 root-only 造成 worker 初始化失败。敏感路由放入 tmpfs 后应校验 worker 身份、目录穿越权限、文件权限及重启恢复。Home-Lab 专用 bootstrap 的修复仍需收敛回 GitOps/Ansible，避免重部署覆盖。

操作完成后清除当前 shell 变量：

```bash
unset AI_GATEWAY_CLIENT_KEY OPENAI_API_KEY ANTHROPIC_API_KEY
```
