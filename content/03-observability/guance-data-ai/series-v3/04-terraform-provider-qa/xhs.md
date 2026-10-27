# 观测云能用 Terraform 管吗？5 问 5 答🤔

## P1 背景
我的 IaC 链路：GitOps 声明 → Python + Jinja2 renderer 生成 HCL → plan/apply。想让观测云的面板和监控器也走这条路。

## P2 Q1 免费版能管远端吗？❌
不能。版本区分页写明免费版不支持 Open API 读写工作空间数据。Open API 页列的 10 个 SaaS endpoint 里，也没有免费专区（北京）。

## P3 Q2 怎么认证？🔑
Header 带 DF-API-KEY，Key 属于哪个工作空间就作用于哪个。管理 Key 只在 plan/apply 时从 Vault 注入，不进仓库和 CI 日志。

## P4 Q3 Provider 能管啥？📦
Registry 上 GuanceCloud/guance，community 层，最新 0.1.0：guance_dashboard、guance_monitor、guance_monitor_json 等资源。

## P5 Q4 存量能 import 吗？🧐
文档只写明 guance_monitor_json 支持 import；Dashboard 没写，【待实测】。

## P6 Q5 免费空间还能干嘛？💡
有 API 权限的空间：plan → import → apply。免费空间：HCL 照常生成、进 PR，但 apply 被 Open API 限制阻断【待授权空间实测】，绝不用浏览器私有接口绕权限。

## P7 决策表 📋
| 功能 | 特性 | 成本 | 依据 | 场景 |
| --- | --- | --- | --- | --- |
| 免费空间 apply | 被阻断 | — | 不支持 Open API | 【待授权空间实测】 |
| 离线 HCL | 可审查 | 0 元 | renderer 只生成文件 | 预演 |
| Provider | plan/import/apply | 商业版【待实测】 | community 0.1.0 | 有 API 权限 |

上一篇：免费版没有平台脱敏｜下一篇：采集端照样 GitOps

#Terraform #IaC #观测云 #GitOps #可观测性
