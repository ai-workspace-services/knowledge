# R1｜换平台演练：同一份 OTel 数据，能不能同时送进自建和观测云？

> 状态：替补大纲（不额外增加篇数；可替换 #08）｜模板：动手实操型｜XHS 标题：换平台要重写代码吗？先做一次双目标演练

![portability](diagrams/gif/portability-wechat.gif)

## 一、场景
担心被单一平台锁定：如果明天要换观测平台，应用代码要不要改？

## 二、知识点
- OTel Collector 一份数据可配置多个 exporter，应用侧 SDK 不感知后端
- DataKit opentelemetry 推荐 gRPC；HTTP 只接受 application/x-protobuf，路径 /otel/v1/traces
- 遥测到达不等于数据可迁移：观测云免费版数据 7 天循环，原始数据只以自建 VictoriaTraces / VictoriaMetrics 为准

## 三、最小实践（AI 辅助 IaC / GitOps / Playbook）
- AI 起草 Collector 双 exporter 配置，人审 PR；Playbook 下发，开关默认关
- 写入 Token 由 Vault 运行时注入，不进仓库与 CI 日志
- 关闭观测云 exporter 再验证自建侧完整，作为退出演练

## 四、结果和局限
- 两端 span 数量差、关闭一端对另一端的影响：【待实测】
- 只在 UAT 演练，不碰生产

## 五、适合 / 不适合
适合：已用 OTel、想保留退出权的人。不适合：应用直连厂商私有 SDK、短期内无法改造的项目。

## 决策表（草案）
| 功能 | 特性 | 成本 | 客观事实依据 | 适用场景 |
| --- | --- | --- | --- | --- |
| Collector 多 exporter | 应用无感切换 | 自建资源【待实测】 | OTel Collector 配置模型 | 平台评估期 |
| DataKit OTLP 接收 | gRPC 推荐 | 计入每天 20,000 Trace | OpenTelemetry 采集器文档 | 观测云侧 |
| 自建原始存储 | 可导出 | 自建运维工时【待实测】 | 免费版数据 7 天循环 | 长期留存 |

## 成稿前须补的证据
- UAT 双目标对账截图（脱敏）；关闭 exporter 前后对比
