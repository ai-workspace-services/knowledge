# Cloudflare UAT 登录链路修复 —— portal 视角

> **Status**: 🟡 代码已提交，待合并 + 重新部署 SSR boundary
> **Date**: 2026-08-19
> **Related PRs**: 本仓 PR 待填 · accounts [#90](https://github.com/ai-workspace-services/accounts/pull/90) · edge-gateway [#16](https://github.com/ai-workspace-services/edge-gateway/pull/16) · platform-ops-toolkit [#433](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/433)
> **完整跨仓规划**: `platform-ops-toolkit/docs/tasks/2026-08-19-cloudflare-uat-login-path-repair.md`

## portal 承担的两个缺陷

### 1. 首页「登录」按钮点了完全没反应

本仓一套源码被 `scripts/build-open-next-boundary.mjs` 构建 5 次，产出 5 个
OpenNext worker（public / auth / content / console / workspace），各自
`assetPrefix: /_edge/<boundary>`、`generateBuildId: <boundary>-<sha>`，且 app
目录被 `owns()` 过滤 —— **public 构建里没有 `(auth)/login` 这个页面**。

首页的「登录」是 `next/link`，会拦截点击做客户端软导航，拿到的是 auth build 的
RSC payload。buildId 不匹配本应回退整页跳转，实测**只对"动态"目标生效**：
`/ai-workspace`、`/blogs`、`/docs`、`/support`、`/register` 都能正常整页跳转，
而 `/login`、`/logout` 是仅有的两个 `x-nextjs-prerender: 1` 静态预渲染页 ——
点击后 router 去加载 `_edge/auth/_next/static/chunks/*.js`（全部 HTTP 200），
但这些模块 id 属于 auth 的 turbopack runtime，在 public runtime 里永不解析，
React transition 永不 commit：**URL 不变、页面不变、console 零报错**。

判别手法：页面里 `window.__M='x'` 后点击，`__M` 丢了 = 整页跳转（正常）；
`__M` 还在且 URL 没变 = 软导航挂死。

本次把 `/login` 的 `dynamic = "error"` 改成 `force-dynamic`，并给 `/logout`
补上同样的声明（它没有任何 `dynamic` 声明，走 Next 默认的静态预渲染）。
auth 页面本来也不该带 `s-maxage=31536000` 缓存一年。

**这只是止血。** 正解是 P1-1 的 `BoundaryLink`：跨 boundary 一律渲染原生
`<a>`（等同 Next Multi-Zones 的约束）。本仓跨界 href 共 **59 处 / 28 个文件**，
逐个改不现实，计划在 boundary 构建里给 `next/link` 加 alias 单点生效。

### 2. 一切未知失败都显示「登录失败，请稍后再试。」

`LoginForm` 的 switch 只映射 7 个错误码，其余全落 `default` → `genericError`。
accounts 在登录路径上还会返回 `email_not_verified`、`account_suspended`、
`sandbox_no_login`、`password_required`、`mfa_required`、`mfa_setup_required`
等，**在本仓全部无映射**。

更糟的是：accounts 的 CORS 白名单没有 UAT 域名，浏览器登录一律收到**空 body 的
403**（见 accounts#90）。空 body 经 `response.json().catch(() => ({}))` 退化成
`{}`，`payload.error` 为 undefined → `messageKey = "generic_error"` → 同样落
`default`。**前端把一个基础设施配置错误显示成了"请稍后再试"，排查因此绕了很久。**

本次：
- 映射逻辑抽成纯函数 `loginErrors.ts`，配单元测试逐码覆盖；
- `default` 分支带上 **HTTP status 与原始 error code**，不再假装是瞬时故障；
- 修正 MFA 分支：accounts 直连时"需要二次验证"是一个 **200 且不带 `error`**、
  只带 `mfaRequired` 的响应，旧代码只认 BFF 的 `needMfa`，于是把它判成登录成功
  并跳回首页（用户实际仍未登录）。现在两种响应形状都识别。

## 部署形态注记（排查时容易踩）

`/api/auth/*` 在当前 `frontend-router` main 上路由到 `api-auth`（edge-gateway →
Cloud Run accounts），**不经过本仓的 Next BFF `src/app/api/auth/login/route.ts`**。
该归属在 frontend-router 上已反复改过两次（#4 路由到 ssr-auth，#5 又改回
gateway），因此前端必须同时兼容两种响应形状 —— 本次改动即按此处理。
session cookie 两条路径都有：BFF 用 `applySessionCookie`，accounts 自己也
`setSessionCookie`。

## 验收

1. 首页点「登录」跳到 `/login`。
2. 错密码 → 「用户名或密码错误」；邮箱未验证 → 「请先验证邮箱」；未知码 →
   「登录失败（403 / xxx）」而不是光秃秃的"请稍后再试"。
3. 真实账号完成登录并拿到 session（依赖 accounts#90 + toolkit#433 一起上线）。
