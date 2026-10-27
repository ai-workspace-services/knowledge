# 1 万条时间线≠1 万个指标‼️

## P1 你以为…其实… 🙅
你以为免费版 10,000 条时间线 = 1 万个指标？其实时间线 = 指标名 × 标签取值组合。同一个指标带上 host、pid，瞬间裂变成很多条。超额就不再上报，数据直接断。

## P2 误区：只在接收端过滤 🚧
应该层层设闸👇
闸 1 发送端：remote_write 里用 write_relabel_configs 按 __name__ keep，Vector 侧同理
闸 2 DataKit：metric_name_filter、measurement_name_filter，支持正则
闸 3 标签：tags_only 白名单或 tags_ignore 黑名单

## P3 误区：黑白名单一起配更保险 ❌
文档原话：黑名单和白名单同时配置，会全部失效。二选一！

## P4 误区：链路指标也要双写 ❌
DataKit 的 OTel 采集器能从链路里提取 trace_hits、trace_latency、trace_errors、trace_apdex。所以自建的 spanmetrics 留在自建，不再重复写，省时间线。

## P5 我的结果 📊
白名单前后时间线数量【待实测】，额度占比【待实测】。数字出来再决定要不要扩大采集范围。

## P6 决策表 📋
| 功能 | 特性 | 成本 | 依据 | 场景 |
| --- | --- | --- | --- | --- |
| 发送端 keep | 不出网 | 工时【待实测】 | write_relabel 示例 | 白名单 |
| tags_only | 砍高基数标签 | 0 元 | 不可与黑名单同配 | 控时间线 |
| 链路指标 | Trace 派生 | 计入 Trace | 采集器文档 | 替代双写 |

上一篇：采集端照样 GitOps｜下一篇：日志双写不丢 trace_id

#可观测性 #Prometheus #观测云 #降本 #独立开发
