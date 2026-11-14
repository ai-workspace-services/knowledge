# QMD Hub 登录：`qmd login` 统一认证使用说明

> 基线：[QMD 单体运行与分布式异步同步架构规范](QMD单体运行与分布式异步同步架构规范.md)（ai-workspace-services/knowledge#400），模式 2（Hub-Spoke）/ 模式 4（企业持久存储）。
> 实现：ai-workspace-lab/qmd#13（CLI）、ai-workspace-infra/playbooks#1026（Hub `whoami` 端点）。部署背景见 [QMD Hub-Spoke 部署回执（2026-11-14）](QMD-Hub-Spoke部署回执-20261114.md)。

## 一、定位

`qmd login` 让任意 Spoke（个人桌面、VPS、Agent 节点）以 **accounts.svc.plus 统一账户** 登录 QMD Hub：

- 官方 Hub：`https://qmd.svc.plus`（默认）；
- 自定义 Hub：任意 https 域名（`--hub qmd.example.com`）。

认证模型与 `desktop.svc.plus`（ai-desktop-lab/xworkmate-remote-desktop）一致：人用 accounts 会话（`Authorization: Bearer <session>`，Hub 经 `GET {accounts}/api/auth/session` 校验并按角色放行，官方 Hub 仅 `admin`）；机器用 Hub 的 sync token。

## 二、命令速查

| 场景 | 命令 |
|---|---|
| 交互式登录（默认 Hub） | `qmd login` → 依次提示账号、密码（隐藏输入）、开启 MFA 时提示 TOTP |
| 自定义域名 Hub | `qmd login --hub qmd.example.com` |
| 非交互一次给全（推荐） | `qmd login --email me@example.com --password-stdin --mfa-code 123456 < ~/.secrets/pw` |
| 非交互（环境变量） | `QMD_EMAIL=… QMD_PASSWORD=… QMD_MFA_CODE=… qmd login` |
| 机器 token | `qmd login --token-stdin < /etc/qmd/hub-token`，或 `QMD_HUB_TOKEN=… qmd login` |
| 查看身份 | `qmd whoami [--json]`，等价 `qmd login status` / `qmd login --status` |
| 登出 | `qmd logout`（同时吊销 accounts 会话），`qmd logout --all`，`--keep-session` 仅删本地 |

退出码：`0` 成功；`1` 认证/网络失败；`2` 缺少输入；`3` 账户需要 MFA 但非交互模式未提供 `--mfa-code`/`--totp`/`QMD_MFA_CODE`（不会二次提示）。

## 三、流程

1. 解析 Hub：`--hub` > `QMD_HUB_URL` > `index.yml` 的 `hub.url` > 上次登录 > `https://qmd.svc.plus`；仅允许 https（localhost 例外）。
2. 解析账户服务：`--accounts-url` > `QMD_ACCOUNTS_URL` > `index.yml hub.accounts_url` > 已保存 profile > Hub 401 响应体中的 `accounts_url` > `https://accounts.svc.plus`。
3. 调用 accounts 公开接口（未改动 accounts）：
   - `POST /api/auth/login` `{identifier, password[, totpCode]}`；非交互模式把 TOTP 一并提交，单次调用完成登录 + MFA；
   - 交互模式收到 `mfaRequired` 时提示 TOTP，再 `POST /api/auth/mfa/verify` `{mfa_ticket, code, method: totp}`。
4. 以会话 token 调 Hub `GET /api/v1/auth/whoami`（旧 Hub 回退 `GET /`），由 Hub 执行角色策略；被拒（403）时立即 `DELETE /api/auth/session` 吊销，不落盘。
5. 按 Hub 域名保存到 `~/.config/qmd/credentials.json`（0600，目录 0700，`QMD_CREDENTIALS_FILE` 可覆盖）。任何输出都不打印 token / 密码。

> 选择密码 + TOTP 而非浏览器/设备码：accounts.svc.plus 目前没有设备码端点，OAuth 回跳 `frontend_url` 只接受已登记租户域名（不支持 loopback 回调），因此 CLI 采用与 xworkmate-remote-desktop 登录代理相同的公开接口；密码只走隐藏输入或 stdin，文档不推荐在参数中写明文。仅绑定 GitHub/Google、没有密码的账户暂不能用交互登录，可改用机器 token。

## 四、Hub 侧契约（qmd-hub-syncd）

- `GET /api/v1/auth/whoami`（别名 `/api/v1/sync/whoami`）：认证后返回 `{service, identity:{method, email, name, roles}, accounts_url}`；
- 未认证：401，JSON 体含 `login_url`、`accounts_url`；**没有新增匿名路径**，Traefik forwardAuth 仍覆盖 `qmd.svc.plus` 全部路径；
- sync token 通道不变；`qmd-spoke-sync` 在未配置 `QMD_HUB_TOKEN_FILE` 时回退读取 `qmd login` 保存的 profile。

## 五、自测

```sh
qmd login                    # 用 admin 角色的 svc.plus 账户；开启 MFA 时输入 TOTP
qmd whoami                   # 期望：Identity: <email> [admin]，Method: accounts_session
qmd logout
# DNS 未生效时可固定解析（TLS 仍按真实域名校验）：
QMD_HUB_RESOLVE=qmd.svc.plus:443:5.189.172.69 qmd whoami
```

## 六、验证回执（2026-11-14）

- 单测 `test/hub-login.test.ts` 15 例：交互/非交互 × 有/无 MFA、缺 MFA 码退出 3、缺密码退出 2、错误密码/TOTP、Hub 403 吊销、机器 token、多 Hub profile、logout 吊销。
- 实测：box 上 `qmd login --token-stdin` 对 `https://qmd.svc.plus`（固定解析到 5.189.172.69）识别为 `static_token`；伪造 token 返回 401。真实账户交互登录待用户自测。

## 七、合并与重新部署回执（2026-11-14 20:36–20:50，UTC+8）

**合并（squash）**：ai-workspace-lab/qmd#13 → `f626412`；ai-workspace-infra/playbooks#1026 → `58f890f`；本仓库 #415 → `9e89190`。

**Hub（sit-k3s-v6，5.189.172.69）**：playbooks main `58f890f` 的 `deploy_qmd_hub.yml`，`-e qmd_hub_version=f626412`（单次临时 inventory）。

| 运行 | ok | changed | failed | 说明 |
|---|---|---|---|---|
| `--check --diff` | 33 | 2 | 0 | 预期变更：QMD 源码 checkout、syncd 脚本 |
| 正式执行 | 56 | 5 | 0 | checkout、构建、脚本、重启 syncd、重启 qmd-hub；新增 whoami 校验通过 |
| 再次执行 | 53 | 0 | 0 | 幂等 |

**Spoke（Grok Bot box `~/qmd-spoke`）**：`deploy_qmd_standalone.yml`，`-e qmd_standalone_version=f626412`；check `ok=17 changed=3`，执行 `ok=20 changed=4`，再次执行 `ok=19 changed=1`。剩下的 1 项是 `config/index.yml`：`qmd update` 会把配置改写成等价格式（补上 `models`、去掉注释和引号），所以每次运行模板都会再写一次。部署前就是这样，不是这次改动引入的，留作待办。

**验证（经 Traefik `https://qmd.svc.plus`，在 Hub 本机固定解析，TLS 校验 0）**：

- 无凭据：`/`、`/api/v1/auth/whoami`、`/api/v1/sync/whoami`、`/api/v1/sync/{health,auth,changes,events}`、`/mcp`、`/random` 全部 401；401 响应体含 `login_url` 与 `accounts_url`。伪造的 Bearer 和伪造的 `xc_session` 也都是 401。
- sync token：`/api/v1/auth/whoami` 返回 200，`identity.method=static_token`；`/api/v1/sync/whoami` 和 `/health` 也是 200。
- box 上的 `qmd`（`f626412`）：`qmd login --token-stdin` 与 `qmd whoami --json` 都识别为 `static_token`；`--non-interactive` 缺密码时退出码 2。
- `sync.sh` 双向（transport `https`）：push 6 个文件，`hub_fence=741`；pull 拉回 1 条 Hub 笔记（fence 734→741）。box 上搜得到 Hub 笔记，Hub 上也搜得到 box 笔记。
- 版本固定：playbooks 默认值仍是 `917637d`，已开 ai-workspace-infra/playbooks#1027 改为 `f626412`（待批准）。
