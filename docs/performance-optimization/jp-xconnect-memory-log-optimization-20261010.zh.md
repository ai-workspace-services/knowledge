---
title: jp-xconnect 内存与日志优化分析报告
description: XHTTP 取消请求引发的 Caddy 日志放大、journald 保留治理、Vector 内存优化与凭据风险复盘。
slug: jp-xconnect-memory-log-optimization-20261010
lang: zh
date: 2026-10-10T20:28:00+08:00
author: Haitao Pan
category: performance-optimization
status: reported-results-pending-follow-up
tags:
  - xconnect
  - xray
  - caddy
  - vector
  - observability
  - linux-runtime
---

# jp-xconnect 内存与日志优化分析报告

2026 年 10 月 10 日 · Haitao Pan · 时间口径：Asia/Shanghai

## 结论与证据范围

jp-xconnect 的主要问题是日志放大及保留策略缺少约束。现有数据没有显示明确的内存泄漏：优化前系统仍有约 1143M available，日志治理后提升到约 1264M。Caddy、journald 和 Vector 的占用都得到改善，但 Caddy 重启后仅观察到 44 分钟，尚不能据此彻底排除泄漏或证明长期稳态。

本报告依据用户提供的排查与两次复查记录整理。主机数值、脚本行为及 PASS 结果为该记录所述，本次文档整理未重新登录主机验证，也未取得三份脚本源码、完整 11 项检查清单或原始采样。一般机制以官方文档补充说明；待办不代表本次已执行。

当前优先级是吊销并轮换已泄露的 billing token、确认 Vector 配置与 TLS/认证行为，然后完成内存趋势观察和日志治理源头固化。降配到 1G 仍需独立容量验收，暂不替换 Caddy。

## 问题链路

记录中的 Caddy WARN 为 `aborting with incomplete response … reading: context canceled`，上游为 `unix//dev/shm/xray.sock`，请求路径为 XHTTP `/split/<uuid>`，耗时不到 1ms。每分钟约 30–220 条，每条 2–5KB，完整请求头中的 Referer / `x_padding` 占了大量文本。

```text
XHTTP 客户端取消下行 GET
  → Caddy reverse_proxy 记录含完整请求头的 WARN
  → journald 持久化
  → rsyslog 写入 syslog
  → Vector 读取、处理并上报 VictoriaLogs
```

按记录中的样本，取消行为与 XHTTP 请求生命周期相符，日志噪声是主要治理对象。不能仅凭 `context canceled` 将所有代理 WARN 判定为无害；需结合错误率、延迟、完成率和真实客户端连接判断。

原始日志输入约为 60–1100KB/分钟；这是按条数和单条大小估算的范围，不是实际流量测量。多层保留与上报进一步放大磁盘写入和处理开销。日志序列化、缓冲及连接状态是 Caddy 内存变化的合理解释，但尚无 pprof 证据证明各自贡献。

## 优化前基线与内存口径

| 进程 | 记录中的占用 | 运行时长 | 判断 |
| --- | --- | --- | --- |
| Caddy | RSS 167M；cgroup 205M | 1h46m | 日志噪声与代理运行状态均需检查 |
| Vector | RSS 137M，另一采样为 134M | 1h44m | 需区分固定开销、batch、buffer 与输入量 |
| Xray 两个进程 | RSS 66M + 32M | 7m | 当前样本未见异常 |
| systemd-journald | RSS 63M；journal 磁盘约 1.0G | 7d | 保留空间偏大；RSS 与磁盘占用是不同指标 |
| Vault | RSS 50M | 2d | 当前样本未见异常 |
| blackbox / process / node exporter | RSS 28M / 23M / 21M | 未记录 | 需纳入降配总预算 |

`free` 只有 64M 并不等于仅剩 64M 可供应用使用，应同时看 available、swap、内存压力与 OOM。记录中的 buff/cache 为 1250M，但不能断言其全部都可立即回收。`shared=0` 也不能单独证明 journal 的存储位置，应检查 journald 的 Storage 配置以及 `/var/log/journal`、`/run/log/journal` 的实际使用。

RSS 与 cgroup 用量不可直接比较。本文保留原始单位 M/G，不补充未经确认的字节换算；后续采样应同时记录 RSS、PSS（如可用）、cgroup `memory.current` 与系统 available，并固定采样窗口及负载。

## 已实施治理（据用户记录）

### Caddy 与 journald

`log-tune.sh` 执行前备份到 `/root/log-tune-backup-<时间>`，记录称可重复执行。Caddy 全局配置从 default logger 排除 `http.handlers.reverse_proxy`，另建 ERROR 级 logger；先 `caddy validate`，通过后 reload，校验失败自动还原。随后重启 Caddy 释放旧进程内存；重启会中断现有连接。

该策略会屏蔽此 logger 的全部 WARN，而非仅屏蔽取消请求样本。推广时需保留 ERROR 与代理链路监测，并检查是否遗漏其他有诊断价值的 WARN。

新增 `/etc/systemd/journald.conf.d/90-limits.conf`，设置 `SystemMaxUse=300M`、`MaxRetentionSec=14day`、`RuntimeMaxUse=64M`，并开启压缩和速率限制；压缩及速率限制的具体值未提供。执行 vacuum 清理已有 journal，删除 `/var/log` 下超过 14 天的 `.gz`、`.1`、`.old` 轮转日志，并执行 `apt-get clean`。

这些删除操作不能靠配置备份恢复。推广前应确认日志保留要求及所需历史已归档，检查清理目标确为可删除的轮转日志。

### Vector

正文明确记载 `vector-tune.sh` 已执行并重启，26 分钟时 RSS 118M；原文附录和待办又写“待执行”。统一记录为：**据正文已执行，配置写入和 systemd 限额仍待复核**，不能直接重复执行来替代状态核验。

| 项目 | 记录中的拟应用/已报告变更 | 待核验证据 |
| --- | --- | --- |
| internal_metrics | `scrape_interval_secs = 30` | 实际 source 配置 |
| system_logs / process_logs | 丢弃 reverse_proxy 日志，其他记录截断到 4KB | VRL 规则、长度口径和日志样本 |
| VictoriaLogs sink | batch 1MB，内存 buffer 500 条 | 实际 sink 类型、参数名及版本兼容性 |
| docker_logs | Docker 未运行时移除；`KEEP_DOCKER=1` 可保留 | 容器日志采集需求及实际 source |
| 工作线程与 systemd | `VECTOR_THREADS=1`、MemoryHigh 150M、MemoryMax 250M | 环境变量、drop-in、cgroup 与重启/OOM 记录 |

记录称脚本先检查 TOML，在副本上修改，通过 `vector validate` 后应用；重启后 10 秒内未正常运行则自动回滚，备份位于 `/root/vector-tune-backup-<时间>`。脚本源码未附，不能将这些保护视为已完成源码审计。

500 条 buffer 是事件数限制，1MB batch 是另一阶段的边界，不能据此将进程内存预算直接等同于两者之和。Vector 的 sink 数量、batch 和 buffer 会影响内存；118M 中各部分占比仍待测量。[Vector 容量规划](https://vector.dev/docs/setup/going-to-prod/sizing/)

原文把剩余占用归因于固定运行时开销和 billing 512MB 磁盘 buffer 的内存映射。磁盘容量并非 RSS 容量，是否使用映射、驻留多少需要进程映射及 buffer 指标支持；当前保留为待验证解释。[Vector buffering model](https://vector.dev/docs/architecture/buffering-model/)

## 效果与两次复查

记录中的两次验证均为 `PASS 11 / WARN 0 / FAIL 0`，涵盖 HTTPS 200、证书校验、Caddy 到 Xray socket 正常及最近 10 分钟无 ERROR 等项目。该结果支持检查窗口内服务可用，但 HTTPS 首页 200 不能替代完整 XHTTP 客户端与隧道业务验收。

| 指标 | 优化前 | 第一次复查 | 第二次复查（20:28） |
| --- | --- | --- | --- |
| Caddy 日志量 | 30–220 条/分钟 | 记录为 0 | 最近 20 分钟仅 1 条 |
| journal 磁盘用量 | 约 1.0G | 298M | 306M |
| Caddy RSS | 167M | 71M，重启后 5 分钟 | 108M，重启后 44 分钟 |
| journald RSS | 63M | 11M | 25M |
| Vector RSS | 134–137M，不同采样 | 134M | 118M，变更后约 26 分钟 |
| Xray RSS | 66M + 32M | 64M + 29M | 65M + 29M |
| 系统 used / available | 721M / 1143M | 589M / 1275M | used 约 600M / available 1264M |
| 根分区 | 未提供 | 4.4G / 7.7G，记录为 60% | 未提供新样本 |

按第二次样本，available 比优化前增加约 121M；第一次样本增加约 132M。Vector 从 134M 降至 118M，约下降 12%，未达到先前预估的 60–80M。Caddy 从重启后 5 分钟的 71M 到 44 分钟的 108M，需继续观察，不能用重启后的最低值作为长期效果。

306M 超过配置目标 300M，但仍在脚本所述 10% 容差内（330M）。验证提示应写“306M > 300M，处于验收容差内”，不能写“306M ≤ 300M”。journald 仅删除归档文件，活动文件也计入磁盘用量，因此 vacuum 后总用量不一定立即低于目标；原文“50M 文件粒度”尚需读取实际配置确认。[journald 保留机制](https://www.freedesktop.org/software/systemd/man/252/journald.conf.html)、[journalctl vacuum 行为](https://www.freedesktop.org/software/systemd/man/255/journalctl.html)

## 安全问题与后续执行顺序

| 优先级 | 待办 | 完成证据 |
| --- | --- | --- |
| P0 | 吊销已泄露 billing token，生成并部署新 token | 旧 token 失效、新 token 最小必要权限且 billing 成功；文档与日志均无凭据值 |
| P0 | 排查凭据泄露路径 | 配置输出、终端记录及日志访问范围已核查并按策略处理 |
| P1 | 恢复三个 sink 的 TLS 证书校验 | CA/主机名校验成功，Vector 无 certificate 错误，sink 实际交付成功 |
| P1 | 核实 observability basic auth 的字面量 `Bearer` | 服务端认证契约确认，真实凭据通过，匿名/错误凭据按预期拒绝 |
| P1 | 核验 Vector 配置和限额 | `vector validate`、实际 systemd 参数、RSS/cgroup、无 401/403/OOM，日志和 billing 均成功送达 |
| P2 | 处理旧 journald `1G / 30day` 配置 | 合并配置与运行状态确认，重复声明按配置归属清理 |
| P2 | 轮转 syslog 中的历史 WARN | 先检查 logrotate 策略与归档要求，再执行必要轮转；无持续重复输入 |
| P2 | 修正验证脚本容差提示 | 实测值、目标值与容差清楚显示；未取得源码前不声称已修复 |
| P2 | 观察 Caddy 与 Vector 稳态 | 每 5 分钟采样、至少 1 小时，记录负载/连接数/GC/内存，长时及峰值复查 |
| P3 | 评估 1G 实例 | 代表性负载、日志积压、sink 故障、发布重启下无 OOM，延迟/错误率与余量符合验收要求 |

新 token 可通过 Vault 或受控运行时环境注入。若采用 `/etc/vector/secrets.env`，需先确认 Vector 配置引用和 systemd EnvironmentFile，设置受限权限，并验证未在排查输出中泄露；仅创建文件不会自动完成 consumer 切换。本报告不保存任何 token、密码或认证响应正文。

## Go 服务内存调优与 1G 降配

原文“Caddy 暂不需要 GOMEMLIMIT”与“下一步给 Go 服务设置 GOGC/GOMEMLIMIT”可同时成立：当前先完成日志治理，Go 调优是降配评估阶段的候选措施，不能把它写成已实施。

先以实测峰值为每个 Go 服务建立预算，再逐服务试验。`GOGC` 降低可能增加 GC CPU 开销；`GOMEMLIMIT` 是 Go runtime 的软限制，不是 RSS 或 cgroup 的硬上限，过低可能导致频繁 GC。不要给所有进程统一套用未经验证的值。[Go GC guide](https://go.dev/doc/gc-guide)

Vector 使用 Rust/Tokio，不适用 Go 的 GOGC/GOMEMLIMIT。Vault、Caddy、Xray、agent 和 exporters 则需各自确认运行时与版本。当前约 600M used 来自约 2G 主机，缓存行为、峰值与发布时并存进程会变化，不能据此直接批准 1G 降配。

Caddy 100–130M 仅作为本次记录建议的观察区间，不是通用正常阈值。若在相近负载下仍持续增长，应收集 Go heap/GC、连接数和 pprof 等证据定位。

## 配置源头固化与推广范围

将日志级别、journald 限额、Vector batch/buffer、运行时凭据引用及验证提示纳入 Playbooks 的实际模板与角色；GitOps 声明目标和版本。先对照现有配置，再固化变更，避免下一次发布覆盖手工调优。

PROD 延续 immutable `v*` release tag 的发布约束。手动 SSH / gcloud SSH 发布时也应记录固定版本、精确主机、备份、应用差异、服务验证和回滚结果。此前 `v2026.10.10-r1` 是 Xray stats/exporter 修复版本，不能视为本次日志优化已入版本或已推广的证据。

原文提出向 us、hk、ph-xconnect 推广；SG 是否纳入另行确定。每台先用只读检查建立基线，再逐台验证代理链路、日志输入及指标上报。本次未对其他节点执行调优。

用户认为此次与 tky-proxy 历史问题相同。本报告将其记录为相似的日志/代理生命周期现象；历史完整指标关联尚不足，不能合并为已证明相同根因。

## 脚本与回滚记录

| 脚本 | 作用 | 统一状态 |
| --- | --- | --- |
| `log-tune.sh` | Caddy ERROR logger、journald 限额、旧日志清理 | 据记录已执行；源码及版本待归档 |
| `verify-log-tune.sh` | 只读验证，FAIL 时非零退出 | 据记录两次 11 项通过；容差提示待修正 |
| `vector-tune.sh` | Vector 输入/batch/buffer/线程与限额调优 | 据正文已执行；配置、凭据与 TLS 加固待核验 |
| Go 调优脚本（文件名未提供） | GOGC/GOMEMLIMIT 试验 | 记录称已就绪；源码、参数与执行情况待确认 |

脚本没有随原文提供，本文不生成同名脚本或将示例命令当成执行授权。重启 Vector 后存活 10 秒仅是基础健康检查，仍需检查 sink 错误和实际业务交付。

回滚应选择明确的本次备份目录，核验对应版本与文件完整性。Caddy 恢复配置后先 validate 再 reload；journald 恢复本次改动涉及的文件；Vector 恢复配置及本次 drop-in 后 validate、daemon-reload、restart，并复验业务。不得凭目录字典序自动选择“最新”备份，也不得删除原本存在的 drop-in 来代替恢复。

旧凭据已泄露，回滚不能重新启用该 token。journal vacuum、旧日志删除和缓存清理不属于配置回滚可恢复的内容。
