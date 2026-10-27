# 一个登录请求到底去了哪里？🧭

![evidence-chain](diagrams/gif/evidence-chain-xhs.gif)

## P1 复盘 🔍
一次 UAT 登录失败：先翻 Workers 日志，再看 Cloud Run，最后查 Supabase。三处没有共同请求 ID，只能对时间戳。Supabase Free 没有 Log Drain，日志只留 1 天，第二天证据就不全了。

## P2 根因 💡
一个请求跨了三朵云，却没有一条线把它串起来。Trace 能串多远，取决于每一跳有没有把 W3C trace context 传下去，断一跳就断在那里。

## P3 怎么接 🔗
AI 起草 OTel SDK 配置和 Collector exporter 声明，人审 PR；Playbook 部署 exporter 指向 DataKit，开关默认关，写入 Token 由 Vault 注入。DataKit 推荐 gRPC，HTTP 只收 protobuf。字段统一 env、service、route、revision、release_tag、trace_id。

## P4 老实标盲区 🙈
Workers 能不能透传 trace context【待实测】；Supabase 内部看不到，只有应用侧 DB 调用耗时。没关联上的环节，就写“盲区”。

## P5 适合谁 🙋
请求跨多个托管平台、排障要翻好几个后台的独立开发者。想看托管数据库内部执行计划的，Supabase Free 给不了。

【待实测截图】：一条真实登录请求的脱敏 Trace 瀑布图，放这里；没有真实截图就不发。

结论：链路是接出来的，不是买来的；每一跳都要传上下文。

上一篇：用户说卡，AI写的页面哪里慢？｜下一篇：告警太多，AI能帮我筛吗？

#可观测性 #Trace #观测云 #Cloudflare #独立开发
