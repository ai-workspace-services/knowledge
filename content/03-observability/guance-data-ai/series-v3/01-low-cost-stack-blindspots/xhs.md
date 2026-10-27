# 一次登录失败，我翻了三个后台😵

## P1 省钱栈很香
Cloudflare Pages/Workers 做入口，Cloud Run 跑后端，Supabase Free 存数据，自建 Grafana 看基础指标。Workers Free 每天 10 万请求，Supabase Free 闲置 1 周会暂停，各层都有条件，不是永久全免费。

## P2 复盘：卡在哪 🔍
用户说登录失败：先翻 Workers 日志 → 再看 Cloud Run → 最后查 Supabase 日志。三处没有共同请求 ID，只能对时间戳；浏览器里发生了什么完全看不到。Supabase Free 没有 Log Drain，API 和数据库日志只留 1 天。定位耗时【待实测】。

## P3 根因 💡
缺的不是指标，是一次请求的前因后果：真实用户体验、跨层上下文、数据库查询级可视性，三个盲区。

## P4 改进 ✅
只挑一条链路建证据链：前端 RUM + 后端 Trace + W3C trace context，统一 env/service/route/trace_id 字段。用观测云免费版做 POC，没实测关联上的环节老实标“盲区”。基础指标继续留在 Grafana。

## P5 适合谁 🙋
适合：已有基础监控、想补用户体验和请求关联的独立开发者。不适合：指望一个免费空间兜住全部生产流量。

## P6 决策表 📋
| 功能 | 特性 | 成本 | 依据 | 场景 |
| --- | --- | --- | --- | --- |
| 自建 Grafana | 基础指标 | 运维【待实测】 | 现有栈 | 兜底 |
| Supabase 自带日志 | 留 1 天 | 0 元 | 定价页 | 当天排查 |
| RUM+Trace | 同一 trace_id | 额度内 0 元 | 版本区分页 | 单链路 POC |

上一篇：迁移监控最怕回不去｜下一篇：观测云免费版的账本

#独立开发 #可观测性 #观测云 #Cloudflare #SaaS
