# AI生成的页面上线后变卡，我先看用户体验而不是CPU

> 状态：大纲（证据未就绪，暂不成稿）｜模板：误区纠偏型

## 一、场景

你以为用户说“卡”就该先看 CPU，其实先该看浏览器里发生了什么：AI 生成的页面上线后，服务端指标正常，用户仍反馈变慢。

## 二、知识点

- RUM 视角：页面加载、慢资源、JS 错误，按 trace_id 关联后端 Trace（关联方式需按 RUM 文档核验）
- 免费版额度：用户访问 PV 每天 5,000 个，会话重放每天 2,000 个（版本区分页）
- 免费版不支持平台侧敏感数据脱敏，遮罩须在 SDK 侧完成

![field-allowlist](diagrams/gif/field-allowlist-wechat.gif)

## 三、最小实践（AI 辅助 IaC / GitOps / Playbook）

- AI 起草 RUM SDK 接入配置与遮罩规则，随前端发布进入 UAT；人审 PR
- RUM 应用 ID 等非敏感参数放 GitOps，写入凭据由 Vault 注入
- 只在 UAT 开启，生产不接

![rum-pipeline](diagrams/gif/rum-pipeline-wechat.gif)

## 四、结果和局限

- 首屏耗时、慢资源、错误率：【待实测】
- SDK 遮罩效果：【待实测】
- 会话重放是否开启需单独评估隐私

![ux-before-cpu](diagrams/gif/ux-before-cpu-wechat.gif)

## 五、适合 / 不适合

适合：前端由 AI 生成、上线后体验难以复现的独立开发者。不适合：不允许在前端注入第三方 SDK 的项目。

## 决策表（草案）

| 功能 | 特性 | 成本 | 客观事实依据 | 适用场景 |
| --- | --- | --- | --- | --- |
| RUM | 页面视角 | 计入 PV 额度 | 版本区分页 | 用户体验排查 |
| 会话重放 | 复现操作 | 计入每天 2,000 个 | 版本区分页 | 疑难复现 |
| SDK 遮罩 | 前端侧遮盖 | 【待实测】 | 免费版无平台脱敏 | 所有 RUM 数据 |

## 成稿前须补的证据

- RUM 接入文档与 SDK 遮罩配置（未核验）
- UAT 前端一次真实慢页面的 RUM 截图（脱敏）

上一篇：[《AI 辅助 Grafana 面板搬家：从 JSON 到观测云配置，保留回退》](../02-dashboard-semantic-reconcile/wechat.md)｜下一篇：[《一个登录请求经过几朵云？用Trace把它接起来》](../04-login-trace-across-clouds/wechat.md)
