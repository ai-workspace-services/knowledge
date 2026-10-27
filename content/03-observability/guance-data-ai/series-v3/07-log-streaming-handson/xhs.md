# 日志双写，别把 trace_id 弄丢了🧵

## P1 背景
指标控住了，轮到日志。我的 Vector 采 systemd 和应用日志，经 HTTP 推进 VictoriaLogs，用 LogsQL 查。现在要多写一份到观测云。

## P2 坑在哪 ⚠️
日志进去如果只是一整行文本、又没有 trace_id：字段搜不了，也跳不到链路。免费版日志每天上限 1,000 万条，Pipeline 只能用本地的。

## P3 Step1 第二个 sink 🔌
原 sink 不动，Vector 新增 HTTP sink → DataKit /v1/write/logstreaming，开关默认关。URL 参数很好用：
source = 指标集名（默认 default）
service = service 标签（默认同 source）
pipeline = 本地 Pipeline 脚本
tags = 自定义标签，逗号分隔

## P4 Step2 JSON 变字段 🧩
Playbook 下发的 DataKit 配置里设 json_as_fields = true，每行 JSON 根对象直接转字段；默认 false 整行进 message。注意它不是 URL 参数！敏感字段在 Vector 侧先删或哈希。

## P5 Step3 带上 trace_id 🔗
应用日志输出 trace_id，观测云才能日志 ↔ 链路互跳。对账：条数差【待实测】，trace_id 可查【待实测】，原 sink 不受影响【待实测】。LogsQL 要在观测云重写。

## P6 决策表 📋
| 功能 | 特性 | 成本 | 依据 | 场景 |
| --- | --- | --- | --- | --- |
| 第二 sink | 原链路不动 | 工时【待实测】 | 现有 Vector | 双写 |
| json_as_fields | JSON 转字段 | 0 元 | 采集器文档 | 结构化日志 |
| trace_id | 日志↔链路 | 改造【待实测】 | 迁移矩阵 | 跨信号排障 |

上一篇：1 万条时间线≠1 万个指标｜下一篇：Grafana 面板搬家不点控制台

#日志 #可观测性 #观测云 #Vector #独立开发
