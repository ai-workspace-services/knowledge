# docs/tasks — 任务归档(项目记忆)

每次任务对话结束后,在此按**任务**建一个 Markdown 文件:目标、结论、关联 PR(带 ID + 状态)、验证、遗留待办。作为跨会话的全局项目记忆。

## 约定

- 文件名:`YYYY-MM-DD-<kebab-任务名>.md`
- 顶部状态块(Status / Date / Related PRs);PR 用完整链接标 [MERGED]/[OPEN]/[CLOSED]
- 跨仓任务在每个相关仓库各留一份(本仓视角),互相引用

## 索引

| 日期 | 任务 | 状态 | 关联 PR |
|---|---|---|---|
| 2026-08-19 | [Cloudflare UAT 登录链路修复(portal 视角:跨界导航 + 错误码映射)](2026-08-19-cloudflare-uat-login-path-repair.md) | 🟡 代码已提交,待合并 + 重新部署 | 本仓 PR + accounts [#90](https://github.com/ai-workspace-services/accounts/pull/90) · edge-gateway [#16](https://github.com/ai-workspace-services/edge-gateway/pull/16) · toolkit [#433](https://github.com/ai-workspace-infra/platform-ops-toolkit/pull/433) |
| 2026-08-01 | [`/panel/account` UAT 页面补全](2026-08-01-panel-account-uat.md) | ⏳ 待审阅与认证浏览器复核 | [portal #132 OPEN](https://github.com/ai-workspace-services/portal/pull/132) |
| 2026-07-11 | [主页导航登录态显示](2026-07-11-homepage-auth-nav.md) | ⏳ 待合并部署 | portal (本 PR) |
