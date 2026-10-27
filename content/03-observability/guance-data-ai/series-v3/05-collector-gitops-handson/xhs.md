# 远端管不了？采集端照样 GitOps🛠️

## P1 背景
免费空间远端写不进去（无 Open API），但采集端在自己机器上，部署、配置、凭据都能代码化。现有栈：Vector 推指标和日志，OTel Collector 收应用 Trace，Playbook 负责部署。

## P2 怕什么 😨
新加一条写往 SaaS 的通道，最怕两件事：写入 Token 混进仓库或 CI 日志；新通道出错把原采集拖垮。

## P3 Step1 声明进 Git 📝
GitOps 只放非敏感参数：采集目标、白名单、开关。开关默认关，关着的时候配置和现状一致。AI 起草声明和 PR 说明，人审 PR 与 plan。

## P4 Step2 DataKit 三个入口 🔌
① OTel Collector → opentelemetry：官方推荐 gRPC；HTTP 只收 protobuf，路由 /otel/v1/traces
② Vector 指标 → prom_remote_write
③ Vector 日志 → logstreaming，URL 可带 source、service、pipeline

## P5 Step3 凭据三分 🔐
写入 Token 部署时注入 DataKit；查询 Key 给只读对账；管理 Key 只在有 API 权限的空间 plan/apply 时用。全部进 Vault，分开授权。

## P6 Step4 验证 ✅
首条数据到达【待实测】，字段对照【待实测】，原采集不受影响【待实测】。

## P7 决策表 📋
| 功能 | 特性 | 成本 | 依据 | 场景 |
| --- | --- | --- | --- | --- |
| OTLP gRPC | 开销低 | 额度内 0 元 | 采集器文档 | 应用 Trace |
| Remote Write | 第二 sink | 计入时间线 | prom_remote_write 文档 | 主机指标 |
| Vault 注入 | 不落盘 | 现有组件 | Playbook 机制 | 全部凭据 |

上一篇：观测云能 Terraform 吗｜下一篇：1 万条时间线≠1 万个指标

#GitOps #Ansible #观测云 #DataKit #独立开发
