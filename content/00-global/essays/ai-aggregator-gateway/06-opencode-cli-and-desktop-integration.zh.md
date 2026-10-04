# OpenCode CLI 与桌面 App 接入 AI Gateway

## 目标

统一使用 Home-Lab 的 AI Gateway：

```text
OpenCode CLI / OpenCode App
        ↓
https://ai-internal.onwalk.net/v1
        ↓
Caddy → New API → CPA / LiteLLM
```

CLI 与桌面 App 使用同一个 Provider ID、同一个端点和同一套 OpenCode 本地凭据。

## 非敏感配置

OpenCode 配置文件：

```text
~/.config/opencode/opencode.json
```

配置只保存端点、模型和超时，不保存真实 API Key：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "ai-internal/gpt-5.6-luna",
  "provider": {
    "ai-internal": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "AI Gateway Home-Lab",
      "options": {
        "baseURL": "https://ai-internal.onwalk.net/v1",
        "timeout": 600000,
        "headerTimeout": 120000,
        "chunkTimeout": 120000
      }
    }
  }
}
```

不要在该文件中写入：

- New API 用户 API Key；
- APISIX bootstrap key；
- New API 管理员密码；
- CPA OAuth token。

## 凭据配置

在本机执行：

```bash
opencode auth login ai-internal
```

输入 New API 用户 API Key。OpenCode 官方凭据存储位置为：

```text
~/.local/share/opencode/auth.json
```

凭据文件只允许当前用户读取：

```bash
chmod 700 ~/.local/share/opencode
chmod 600 ~/.local/share/opencode/auth.json
```

API Key 只在 New API 的 Keys 页面创建和撤销：

```text
https://ai-internal.onwalk.net/keys
```

如果 Key 曾经进入聊天、日志、截图或 Git，必须先撤销，再创建新 Key。

## CLI 验证

检查凭据是否登记，只输出 Provider 名称：

```bash
opencode auth list
```

列出 Gateway 模型：

```bash
opencode models | grep '^ai-internal/'
```

发送最小推理请求：

```bash
opencode run \
  --model ai-internal/gpt-5.6-luna \
  "Reply exactly: hello"
```

成功标准：返回模型文本，且没有 `Invalid token`、`401` 或上游超时。

## 桌面 App 验证

1. 完全退出 OpenCode App。
2. 重新打开 App。
3. 新建会话。
4. 选择 Provider `AI Gateway Home-Lab`。
5. 选择 `gpt-5.6-luna`。
6. 发送 `hello`。

桌面 App 从 Finder 启动时不应依赖 `.zshrc` 中的环境变量；使用 OpenCode 凭据存储最可靠。

## 故障判断

### `command not found: opencode`

确认 `~/.local/bin` 已加入 PATH：

```bash
export PATH="$HOME/.local/bin:$PATH"
rehash
opencode --version
```

### `Invalid token`

说明请求已经到达 New API，但 OpenCode 使用的 Key 无效、过期或不是 New API 用户 API Key。重新执行：

```bash
opencode auth login ai-internal
```

不要使用 APISIX bootstrap key 或管理员密码。

### `/v1/models` 能访问但推理失败

模型目录只能证明路由和配置可见，不能证明用户凭据和上游账号可用。必须执行一次最小推理请求。

## 当前验证记录

截至 2026-10-04：

- `opencode.json` JSON 语法通过；
- `ai-internal` Provider 配置存在；
- Base URL 为 `https://ai-internal.onwalk.net/v1`；
- 本地模型目录可加载 22 个 `ai-internal/*` 模型；
- OpenCode 凭据登记项存在；
- 最小推理请求仍返回 `Invalid token`；
- 需要撤销暴露过的旧 Key，并在本机重新执行 `opencode auth login ai-internal`。

完成重新登录后，重新执行 CLI 和桌面 App 两套验证，才能判定端到端可用。
