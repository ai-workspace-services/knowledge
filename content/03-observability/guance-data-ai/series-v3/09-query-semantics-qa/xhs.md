# PromQL 照抄能跑吗？查询口径 5 问🧐

## P1 背景
面板背后是查询：自建侧是 PromQL（VictoriaMetrics）和 LogsQL（VictoriaLogs）。观测云图表支持 PromQL，也有自己的 DQL。语法能转，语义未必一样，曲线“看着差不多”最危险。

## P2 Q1 指标名会变吗？🔤
会！Remote Write 默认按第一个下划线切：go_memstats_heap_objects → 指标集 go + 字段 memstats_heap_objects。设 keep_exist_metric_name = true 才保留原名。先定这项，不然查询全要改。

## P3 Q2 step 怎么定？⏱️
优先级：查询里的 [5m] → interval → timerange → 默认 5m。rate/increase 窗口必须和原面板对齐。

## P4 Q3 筛选都能转吗？🔁
能：多个 AND、同 label 多值 OR、= != =~ !~
不能：不同 label 之间 OR、数值比较、函数类筛选

## P5 Q4 P99 一样吗？📐
观测云：原始点排序取“点数 × 99%”位置；Prometheus histogram_quantile 是桶内插值。可能不一样，要逐项比。

## P6 Q5 LogsQL 呢？📝
没有直接对应，改写成 DQL 写进声明。统一验收：同一时间窗并排比，曲线一致才算可迁移，偏差【待实测】。

## P7 决策表 📋
| 功能 | 特性 | 成本 | 依据 | 场景 |
| --- | --- | --- | --- | --- |
| PromQL 模式 | 复用原查询 | 改写【待实测】 | PromQL 文档 | 指标面板 |
| 保留原名 | 少改写 | 0 元 | prom_remote_write 文档 | 迁移前 |
| DQL 重写 | 原生语义 | 工时【待实测】 | 查询语言 | LogsQL |

上一篇：Grafana 面板搬家不点控制台｜下一篇：只有 10 个阈值监控器

#PromQL #可观测性 #观测云 #Grafana #迁移
