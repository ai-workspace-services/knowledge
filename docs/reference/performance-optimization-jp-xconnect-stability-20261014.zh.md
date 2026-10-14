---
title: JP XConnect 稳定性增量配置验证报告
description: jp-xconnect.svc.plus 的 XHTTP 上传与请求延迟第一阶段稳定性配置及短窗口验证。
slug: performance-optimization-jp-xconnect-stability-20261014
lang: zh
date: 2026-10-14
version: "0.1"
status: prod-partial-validated
category: reference
tags:
  - performance
  - xconnect
  - xhttp
  - caddy
  - xray
---

## Change Log

| 日期 | 版本 | 变更 | 验证/记录 |
| --- | --- | --- | --- |
| 2026-10-14 | 0.1 | Xray XHTTP 日志降为 `warning`，连接 buffer 设置为 512 KiB；Caddy Unix socket 反代启用 `flush_interval -1`。 | 线上配置校验通过，服务 active；[playbooks PR #650](https://github.com/ai-workspace-infra/playbooks/pull/650) 已合并到 `main`。 |

# Performance Diagnosis

## 1. Executive Summary

目标是降低 `jp-xconnect.svc.plus` 的请求延迟，并缓解图片上传卡顿。本阶段采用两项小步、可回滚的线上配置：Xray XHTTP 使用 `warning` 日志和 512 KiB 连接 buffer；Caddy XHTTP Unix socket 反代使用 `flush_interval -1`。两项配置均已通过配置校验并生效，服务保持 active。

当前结论为 **已定位待优化 / 短窗口已验证**。短窗口未发现 Caddy 或 Xray 的 warning/error，不能替代真实客户端大图上传验收。

## 2. Environment

- 目标：`jp-xconnect.svc.plus`（SSH 通过现有 `tky-proxy.svc.plus` 管理入口执行）
- 平台：Debian 12、Linux ARM64、2 vCPU、约 1.96 GiB 内存
- 组件：Caddy 2.11.4、Xray 26.3.27、XHTTP over Unix socket + h2c
- 变更时间：2026-10-14 18:54–18:55（Asia/Shanghai）
- 责任源文件：`ai-workspace-infra/playbooks/roles/vhosts/agent-proxy/templates/xray.xhttp.template.json.j2`、`ai-workspace-infra/playbooks/roles/vhosts/tky-proxy/templates/agent-proxy.conf.j2`

## 3. Observations

变更前实测配置为 `loglevel=debug`，XHTTP 模板没有 `policy.levels.0.bufferSize`。历史客户端调优评审指出，ARM64 节点缺少该设置时会使用较小的默认连接 buffer，可能限制中大块上传吞吐。

本阶段执行后：

- `xray run -test -config`：通过
- `caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile`：通过
- `xray.service`、`caddy.service`：active
- 远端本机 HTTPS 健康请求：HTTP 200，`time_starttransfer` 约 6.2–6.4 ms，`time_total` 约 6.3–6.5 ms（5 次样本，仅代表本机路径）
- 观察窗口内 Xray RSS 约 96 MB，主机 Available Memory 约 1.07 GiB，已建立连接约 224–240
- 观察窗口内 Caddy/Xray 没有 warning/error 日志

## 4. Findings

1. **已确认**：Xray XHTTP 模板原为 debug 日志，且未显式设置连接 buffer。
2. **已确认**：当前 ARM64 节点的生成配置已变为 `loglevel=warning`、`bufferSize=512`。
3. **已确认**：Caddy 的 XHTTP 两个站点反代已启用低延迟响应刷新，并完成无停机 reload。
4. **待验证**：图片上传卡顿是否主要由客户端 XHTTP 分片参数、节点 buffer 或网络重传共同造成；本报告没有执行破坏性压测，也没有伪造上传成功结论。

## 5. Root Cause

- 实测事实：服务端模板缺少显式 `bufferSize`，日志级别为 debug。
- 指标推断：ARM64 小 buffer 可能增加分片处理和系统调用压力，造成中大图上传抖动；降低日志级别可减少无效日志开销。
- 待验证假设：Caddy 默认响应刷新策略可能放大上传完成确认的感知延迟；`flush_interval -1` 仅影响响应刷新，不改变请求体路由或认证。

## 6. Optimization Plan

| 项目 | 修改 | 预期收益 | 风险 | 回滚 |
| --- | --- | --- | --- | --- |
| Xray XHTTP | `warning` 日志、`policy.levels.0.bufferSize=512` | 降低日志开销，改善 ARM64 分片上传吞吐稳定性 | 每连接 buffer 增大，峰值连接数高时内存上升 | 恢复 `/var/backups/xconnect-performance/20261014T105456Z` 或 `20261014T105504Z` 中的模板和 config 后重新校验并重启 Xray |
| Caddy XHTTP | Unix socket 反代添加 `flush_interval -1` | 更快返回上传确认和流式响应 | 长连接响应刷新频率增高 | 恢复 `/var/backups/xconnect-performance/20261014T105546Z/agent-proxy.caddy`、`tky-proxy.caddy`，校验后 reload Caddy |

本地源模板已同步记录在 playbooks；线上修改仍应通过后续 PR 和部署回执收敛，避免配置漂移。

## 7. Validation

已完成：配置语法校验、服务 active 检查、短窗口内存/连接观察、本机 HTTPS 200 响应检查。

尚未完成：真实 iOS/Android/Desktop 客户端连续大图上传、上传 P50/P95/P99、失败率、重传率、跨公网 RTT 对照，以及客户端调优 PR 的签名真机验收。因此本阶段不能标记为“上传问题已解决”。

建议验收门槛：同一客户端、同一节点、同一图片集合，对比变更前后上传完成时间、卡顿次数、失败/重试次数、TCP retransmission、Xray RSS 峰值和 Caddy/Xray 错误日志。

## 8. Cost Impact

未升级实例、未改变云资源规格，计算成本没有直接变化。512 KiB buffer 可能增加内存占用，应结合并发峰值继续观察；当前短窗口 Available Memory 仍约 1.07 GiB。

## 9. Next Actions

1. 在低峰用真实客户端完成连续大图上传，至少覆盖 iOS、Android 或 Desktop 中实际受影响的客户端。
2. 对照客户端调优历史任务，修复已发现的缓存失效、404 回退和显式默认值覆盖问题后，再验证 `scMaxEachPostBytes` 与分片间隔。
3. 将线上 Caddy/Xray 修改通过 playbooks PR 收敛，并在下一次 agent 同步后再次确认模板与生成 config 一致。
4. 若上传仍卡顿，下一步只采集 TCP retransmission、RTT、XHTTP 分片耗时和客户端日志，再决定是否调 `scMaxEachPostBytes` 或 `scMaxBufferedPosts`。
