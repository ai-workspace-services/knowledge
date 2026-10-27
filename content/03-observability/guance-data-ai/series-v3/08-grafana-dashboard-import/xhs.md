# Grafana 面板搬家，我一次控制台都没点🚚

## P1 背景
指标和日志已经并行写进观测云，面板还在 Grafana，数据源是 VictoriaMetrics（PromQL）和 VictoriaLogs（LogsQL）。问题：Grafana JSON 不等于观测云 JSON，官方也提示部分高级特性可能显示不了；免费版仪表板最多 10 个，还没有 Open API。

## P2 三条路对比 🆚
A 转换脚本：grafanaCovertToGuance（npm 包 @cloudcare/guance-front-tools）离线转成观测云 JSON，AI 再拆成声明
B AI 直出声明：读 Grafana JSON 直接写声明，适合要重写查询的面板
C 暂保留：跨层总览、管道自监控留在 Grafana

## P3 同一条流水线 🏭
声明进 GitOps → PR 审查 → iac_modules renderer 生成 guance_dashboard 的 HCL → Terraform plan → 人审 plan。免费空间 apply 被 Open API 限制阻断，plan 和 import【待授权空间实测】。

## P4 我的漏斗 🔻
首批只选 3 个：资源健康、API 流量与错误、k6 压测延迟。每个只判三种：可迁移 / 需重写 / 暂保留。历史数据留在原存储。结果【待实测】。

## P5 决策表 📋
| 功能 | 特性 | 成本 | 依据 | 场景 |
| --- | --- | --- | --- | --- |
| 转换脚本 | 可进 Git | 修复【待实测】 | 场景 FAQ | 简单面板 |
| AI 直出声明 | 可重写查询 | 审查【待实测】 | 兼容性提示 | 复杂面板 |
| apply | 需 Open API | 【待授权空间实测】 | 版本区分页 | 授权空间 |

上一篇：日志双写不丢 trace_id｜下一篇：PromQL 搬过去还能跑吗

#Grafana #GitOps #观测云 #Terraform #独立开发
