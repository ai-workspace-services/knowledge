# 网络延迟与流量统计：双链路 OTel 实施及验收方案

日期：2026-10-21（Asia/Shanghai）。状态：可审阅规划，尚未实施。需求来源：本次规划任务；历史上下文 `codex://threads/01a12e73-ea52-7011-9fb8-56cdcb33cdd8`。

本轮只读代码、远端 PR、历史记录并新增本文；没有读取凭据值，没有 SSH 执行生产探针、部署、重启、生成业务流量、真实扣费或写账本。所有未执行的运行验收均为 NOT_RUN。既有模板、基线和历史回执原样保留。

配套：[V4 基线](prod-v4-runtime-and-snapshot-baseline-20261021.zh.md)、[历史回归与收尾](regression-and-closure-checklist-20261021.zh.md)。本文不替代 GitOps、Vault、CMDB 或账务事实。

## 1. 当前证据与缺口

| 项目 | 本次核实与边界 |
| --- | --- |
| Knowledge | 远端 main 与工作树起点同为 `65278eadf1155d5ecdd27d4018e8e12c1f6a2de5`；SSH fetch 主机校验失败后用 HTTPS ls-remote 只读核对，无放宽 SSH 校验 |
| Playbooks | 重新 fetch main=`5f959ab8bacfc4dd133c1e4d859b5ab8cb4cdc40`；[#720](https://github.com/ai-workspace-infra/playbooks/pull/720) 已于 17:07:03 +08 合并，原 head=`c986bc3a42785b5a20b1daff9b8a8607826bd87c`；候选 tag 和 GitOps pin 不因合并自动成为新部署 |
| 凭据 repair | 用户提供的 17:09–17:12 回执：7/7 可达、failed=0；JP Team changed=2，其余六节点 changed=0；鉴权快照探针全部通过。本文未重跑；未证明 Billing 投递、PostgreSQL 增量或页面恢复 |
| Billing | HTTPS fetch main=`77557d796a66dcd3373d7731125890bd91ebc5d3`；已有 OTel SDK、otelhttp、otelsql；`internal/service/service.go` 没有业务 spans。`internal/repository/postgres.go` 各表调用独立 Exec，没有统一 BeginTx |
| Exporter | HTTPS fetch main=`1094bd8e11af30eda62fdbb2ecf9d8560d493829`；`internal/snapshot/{service,push,types,identities}.go` 已有身份解析、累计快照、本地存储、向 Vector 推送；缺 token 时 Pusher.Enabled=false，不能把进程存活当成投递成功 |
| Accounts / Portal | Accounts fetch main=`1ca14236c22a59b009480a05504d93e6b5fe2379`；`api/accounting.go` 直接从 store 查用量，不是每次查询 Billing HTTP。Portal `fetchAccountUsage.ts` 请求 summary/buckets，在客户端汇总分钟桶；本地均有其他改动，未动 |
| 既有后端 | Playbooks `roles/docker/observability-server/templates/otel-collector.yml.j2` 已有 OTLP HTTP :4318、memory_limiter、batch 5s、VictoriaTraces/Logs/Metrics 与 spanmetrics；`web_saas_host_config/templates/otel-collector.yaml.j2` 是另一部署上下文，需核实实际选择，不并行新建 |
| 部署差异 | V4 基线明确当时运行容器没有 OTel，不能从模板推断 Collector 已运行。Billing SDK 支持 gRPC 与 HTTP，而中心模板只开 HTTP，需核实实际 endpoint/protocol/auth/TLS |
| 现有图表 | Playbooks observability-server/files 中已有 blackbox-exporter-dashboard.json、postgres-exporter-dashboard.json、victoria-traces-dashboard.json；运行生效、数据新鲜度、datasource UID 本轮 NOT_RUN |

原工作树的 Billing、Accounts、Portal、Playbooks、GitOps、Knowledge 脏改动均未修改、暂存或清理。本文位于独立 `feature/traffic-otel-plan-20261021` 工作树。

## 2. 流量统计链路逐跳契约

以下周期为已查模板默认值，必须用实际渲染配置及进程参数覆盖；探针均为后续只读计划。

| 跳 | 输入 → 输出、权威与鉴权 | 周期 / 时间边界 / 新鲜度 | 错误分类与只读证明 |
| --- | --- | --- | --- |
| Vault → 解析 | 唯一权威 `kv/prod/accounts/runtime` 的 `INTERNAL_SERVICE_TOKEN`；公共 resolver 在控制端内存解析，no_log | 新机、升级、恢复都先执行；check-mode 仍读取与校验，不写文件 | Vault 连接/权限/字段缺失/格式无效分别失败；只记录成功布尔和失败阶段，不记录值或指纹 |
| 校验 → 0600 | 非空及格式 assert → Exporter env；保护已启用有效配置，禁止空输入覆盖 | 内容变化才 notify Exporter handler；同版重跑 changed=0、无重启 | 比较执行前后 stat mode/owner、内容相等布尔、unit invocation 变化；不 cat env |
| 文件 → Exporter | systemd EnvironmentFile → 实际进程；JP Free `/etc/xray-exporter/runtime.env`，其他节点历史为 `/etc/xray-exporter.env` | 每实例快照默认 1m，本地保留 72h；区分 xhttp/tcp 两个 source | 空 token 可静默禁推；核实 env 文件路径与注入非空布尔，不能仅查 active |
| 快照探针 | 鉴权 GET `/v1/snapshots/latest` → collected_at/node/env/累计样本 | UTC collected_at；连续两轮递增且 age≤2T+10s（建议门槛） | 401、空 samples、旧快照、身份未解析、真实零累计分别标记；输出样本数/总量/时间，不输出身份 |
| Exporter → Vector | JSON cumulative snapshot + Bearer → loopback HTTP source | 推送随快照；客户端默认 timeout 10s；本地保存成功不等于已投递 | timeout/refused/非2xx/禁推；核对 Pusher 成功与 Vector received 增量，禁止直接向 Billing 改投 |
| Vector → Billing | http_server → HTTP sink POST `/v1/ingest/snapshots`；sink token 来自同一权威 | 模板 batch max_events=1、timeout=5s；disk 512MiB；retry初始5s、最大3600s | 入口403/下游401、429、5xx、满盘/队列、永久拒绝；HTTP source 当前未显式 auth/ack，需核实仅loopback绑定及版本默认确认语义 |
| Billing → PostgreSQL | 解码、身份/来源校验、delta/reset、桶/账本/配额/checkpoint；DB连接源由现有运行配置/Vault提供 | push处理立即执行；minuteStart=collected_at.UTC().Truncate(minute)；非单独轮询 | schema/权限/锁/连接/事务失败；只读核对各表增量、最新checkpoint与来源，不开启 Billing 主动拉取 |
| PostgreSQL → Accounts | `traffic_minute_buckets` / quota / ledger → 认证账号过滤查询 | summary与指定start/end桶查询；没有单独周期，随请求 | DB有新桶而API无结果：账号归属、时间谓词、权限、分页或查询失败；事务只读、限时、仅聚合输出 |
| Accounts → Portal | session → summary/buckets → 最近1小时/日/月汇总 | RFC3339 UTC instant；建议统一[start,end)，边界须核查store实际谓词后加测试 | API新鲜而页面0：客户端窗口、时区、缓存/刷新、错误被当0；登录浏览器对比同账号同窗口求和 |

现有 `vector-agent/templates/vector.toml.j2` 中 TLS verify 默认 false、sink healthcheck disabled，是配置风险证据，不证明现场如此。实施要检查当前生效值和 CA 信任，再单独审阅收敛，不能在本文中变更生产。

### 故障判别顺序

1. 快照时间不推进：采集/身份服务/Exporter故障；不能判“零流量”。
2. 新鲜快照 counter 不变、两周期无增量、身份映射完整且链路无错误：可判观察窗口内真实零流量。
3. 快照推进且 counter 增长，Vector received不增：Exporter→Vector；received增而sent/DB不增：队列、403/401/5xx或Billing拒绝。
4. 接收次数增但幂等命中增且账务不变：去重；不得用重复请求数当流量。
5. counter下降并reset_epoch推进：重置基线，本轮不产生负增量；下一轮正增量另验。
6. DB新增而Accounts无：查询/归属/窗口；API有而页面无：展示；任何阶段采样缺失均用unknown，不能填0。

重点账务缺口：当前按账号读取checkpoint，负增量更新reset checkpoint后返回；首次无checkpoint会将累计值作为增量。重复分钟 Upsert 会覆盖桶数值，ledger ID确定性本身不证明全事务幂等。必须增加重复后桶内容保持、同分钟多快照、乱序/旧样本、并发、各写入点崩溃重试测试。OTel一期只观测现有步骤，不伪造“transaction committed” span；原子事务修复独立PR、独立账务审阅。

## 3. 网络延迟链路（独立一等范围）

已发现：Playbooks Blackbox角色与Vector 60s SSL probe、15s其他probe配置；Node/Process指标；Agent已有 sync/command spans（`internal/xrayconfig/syncer.go`）及协议 `rtt_ms` 字段，但字段存在不证明RTT采集运行。xconnect-app已有 `lib/services/tunnel_data_plane_probe.dart` DNS/transport探测与诊断面板；探测成功/耗时不能自动解释成ICMP RTT。Observability `docs/zh/{network-quality-sdk-plan,xconnect-user-tracing-plan,xconnect-user-diagnostics-dashboard-plan}.md` 是既有规划，eBPF/双端core SDK不能视为已交付。

| 采集点 | 精确定义 | metrics / logs / traces 与关联 | 验收目标（建议，尚未执行） |
| --- | --- | --- | --- |
| Blackbox ICMP / TCP | ICMP往返与TCP建连分别计；TCP connect含握手，不等于内核srtt | 复用probe_success、probe_duration_seconds及实际暴露分阶段指标；固定probe地点/target class/module | 正常/丢包/超时fixture分类100%正确；无ICMP样本显示not_observed |
| 客户端 DNS/TCP/TLS/首响应 | 各阶段单调时钟耗时；复用连接时DNS/TLS可不发生 | 客户端/core SDK有限阶段spans，记录connection_reused与coverage；受控诊断session，禁止原始目标URL | TLS/DNS失败、连接复用、休眠/中断分别展示；TTFB不能标RTT |
| Caddy → Xray → 出口 | proxy总耗时、upstream header等待、出口DNS/dial/首响应 | 复用Caddy metrics与Vector日志；core实际可埋点时才生成spans；准确匹配才link | 502/reset/EOF与Xray重启同窗可见；没有dial测量显示unknown，不能由proxy总耗时倒推 |
| 网络内核 | TCP srtt、重传、丢包、队列 | 先复用node级指标；需要连接归因时另评审eBPF，控制权限/开销 | 主机重传不能归属具体用户；不在一期新增quality gateway |
| Portal → Accounts → DB | 浏览器请求总耗时、服务处理与DB客户端耗时 | HTTP client/server +业务查询+DB spans；traceparent贯通实际HTTP，浏览器Resource Timing受跨源限制 | UAT注入100ms服务延迟只增加service阶段；SQL慢只增加DB阶段；每场景≥20次且分类全正确 |
| Exporter/Vector/Billing网络 | HTTP请求总时长、connect/TLS（若用httptrace）；loopback与公网分开 | Exporter SDK client span，Billing server span；Vector异步按下节关联 | 网络断开只表现投递/queue问题，不解释为RTT变大或用量0 |

网络case要补充：DNS失败、TLS不可信、连接拒绝/超时、连接复用、HTTP2多路复用、代理取消、Xray重启、设备休眠、DB慢与网络慢对照；复用现有探针测试目录，尚无统一可执行case harness，明确NOT_RUN。故障注入只在隔离fixture，不能改生产网络、证书或进程。

## 4. 双链路 OTel 设计与异步关联

Billing复用现有Configure：默认ParentBased 5% head sampling、批量导出、endpoint空时noop。增加固定命名 `billing.ingest.decode`、`validate`、`deduplicate`、`delta`、`bucket.write`、`ledger.write`、`quota.write`、`checkpoint.write`；DB客户端复用otelsql。后续事务实现后才增加 `billing.accounting.transaction` 与commit/rollback结果。Accounts补用量查询span及DB关联；PostgreSQL服务端用exporter、连接池等待/锁/慢查询聚合指标，不假设数据库内运行SDK。

当前Configure未见显式SetTextMapPropagator：需配置W3C TraceContext并测试跨HTTP提取注入；只允许可信内部context，不传账号baggage。网络SDK使用客户端httptrace/core钩子提供阶段，普通otelhttp请求span本身不分解RTT。不要把SQL耗时减去请求耗时当网络延迟。

Vector官方能力核实：HTTP source可配置捕获header，HTTP sink支持header模板和batch；这不构成自动逐事件trace传播。当前max_events=1仍不能证明原始header已保留。依据[HTTP source](https://vector.dev/docs/reference/configuration/sources/http_server/)和[HTTP sink](https://vector.dev/docs/reference/configuration/sinks/http/)，需用实际固定版本验证编码、元数据保留、重试与确认边界，不能仅凭最新文档认定线上支持。

一期采用可实现的降级路径：Exporter与Billing分别建trace，用node/env/transport、collected_at和受控snapshot_ref关联，Vector internal metrics和日志显示队列/重试；尚无snapshot_ref时仅标时间窗关联，不展示连续瀑布。二期在兼容的可选envelope telemetry字段携带W3C span context与opaque snapshot_ref；Vector保留字段，Billing读取后以span links关联每个生产者context。一个HTTP批次的入口span属于该HTTP请求，各快照处理span链接原生产者，不能把整个batch强行设成某一snapshot的子span。按[OTel span links](https://opentelemetry.io/docs/concepts/signals/traces/)设计。

batch_ref为每次HTTP请求生成；snapshot_ref跨重试稳定；二者只进受控logs/spans，不进metric labels、不参与计费去重键。限制每batch links数量（建议128）并记录truncated计数。Vector不能产生精确出队timestamp时，collected_at→Billing接收只能称端到端投递年龄，不能称纯排队时间；精确queue时间需可验证入/出队事件，否则not_observed。

统一时间：t_collect、t_vector_receive（若可测）、t_billing_receive、t_db_commit（仅事务存在时）、t_accounts_response、t_ui_render。跨主机差值需NTP offset证据，建议offset≤100ms，负差值或偏差超限标clock_skew；进程内部持续时间用单调时钟。网络与用量以同node/transport/environment/revision及窗口关联，只有真实context才link；时间相关性不宣称因果。

## 5. 三种信号、隐私与开销

- Metrics：全量低基数成功/失败、freshness、reset/dedup、queue、DB耗时与网络分阶段分布；labels限service/environment/revision/region/transport/stage/outcome/error_class，不含snapshot、batch、UUID、email、trace ID。
- Logs：脱敏失败分类、重试、重置与关联reference；禁止当前handler bodyPrefix和含UUID错误被直接带入OTel。SQL statement/parameters、DSN、Authorization、Cookie、密码全部禁采；otelsql默认行为须专项测试，使用库选项关闭statement采集并由Collector白名单二次过滤。
- Traces：解释单次处理路径与依赖等待；采样trace不代表完整请求数，更不是扣费依据。spanmetrics由采样spans形成时必须标采样覆盖，业务正确率由全量计数和DB事实计算。
- 常规保持5%；受控UAT/短诊断窗口100%，不能在head丢弃后承诺tail保留所有错误。导出失败不得改变业务HTTP结果或事务；bounded queue、超时、丢弃计数，禁无限阻塞。建议trace/log诊断留存7天，经容量审阅定值。
- UAT同负载对照：SDK开启后p95服务耗时增加≤5%、CPU增加≤5个百分点、RSS增加≤32MiB；后端不可达持续10分钟业务通过率不降、无账务差异、队列有界。以上为提议门槛，未实测。

## 6. 历史case与可执行验收清单

脚本基准为Playbooks `5f959ab8`，Billing `77557d79`，Exporter `1094bd8e`。所有运行结果NOT_RUN。退出码0仅说明脚本自身预期通过，skip不通过业务门禁。

| case | 实际入口 / 缺口 | 预期、失败与退出码 |
| --- | --- | --- |
| 缺Token/保护配置 | Playbooks `tests/test_snapshot_credential_repair.py`、`tests/test_snapshot_token_idempotency.py`；repair入口 `repair_xray_snapshot_credentials.yml` | 离线Ansible fixture缺token失败且原文件保持；有效重跑不重启；Python 0/1。实际apply本轮禁止 |
| 入口403/鉴权401 | Billing `internal/httpapi/handler_test.go:TestIngestSnapshotRequiresInternalServiceToken`；Playbooks `docs/cases/runbooks/2026-10-21-v4-p0-regression-cases.md` | 鉴权单测0/1；合法POST穿Caddy正向用隔离样本，不能靠GET或故意向生产POST验收；入口集成harness待补 |
| Vector编码/非2xx | `TestDecodeSnapshotsAcceptsBothVectorFramings`；Exporter `TestPusherTreatsNon2xxAsError` | array/对象/NDJSON按契约接收；非2xx明确失败；go test 0/1，不能代替实际Vector版本测试 |
| 重复/双源 | Billing `TestDuplicateMinuteIsReplaySafe`、`TestMultiInboundDuplicateWindowIsReplaySafe`；Playbooks `tests/data_operations/selfhost/v4_duplicate_producer_identity_test.py` | 合成重复余额/配额/账本/桶内容全部不变，来源ID唯一；后者是契约测试，不是现场生产者完整清单；0/1 |
| reset/重启 | Billing `TestNegativeDeltaProtection`、`TestRestartRecoveryFromCheckpoint`、`TestMultiInboundOneInboundStopsReportingIsConservativeReset` | 无负计费、reset后下一轮只算新增；重启恢复checkpoint；当前缺事务崩溃点测试，补齐前不放行；0/1 |
| 身份/多inbound | Exporter `TestNormalizeResolvesEmailAndAggregatesCounters`、`TestNormalizeDropsUnresolvedEmail`；Billing `TestMultiInboundSamplesAggregateIntoSingleAccountBucket` | 同账号聚合、未知邮箱不上账、不同账号不串账；代理UUID→account归属及重映射仍需端到端case；0/1 |
| 非零两周期 | Playbooks `tests/data_operations/selfhost/v4_traffic_chain_acceptance.sh` | 只读查最近5分钟至少两个不同分钟且positive bytes；缺node变量2、无增量/格式错1、通过0；必须传DB实际env:node键。单次查询可能包含历史桶，需前后基线和相同新鲜snapshot配对 |
| 零流量 | 复用Exporter/Billing fixture新增专用case，当前无完整脚本 | 新鲜时间连续推进，counter不变、无新收费，传输正常；零与旧快照不得同PASS；计划0/1，当前NOT_RUN |
| 落库 | Billing `TestPostgresAcceptanceWritesAccountingTables` | TEST_DATABASE_URL未设会skip；测试含DELETE，严格只用一次性PG17库，禁连接真实业务库；0且无skip才算fixture通过 |
| 最近1小时0 | Accounts `api/accounting.go`；Portal `fetchAccountUsage.test.ts`及AccountPanels测试，新增UTC边界case | 认证同账号API桶和页面求和一致，边界[start,end)含/不含明确，刷新后新桶可见；浏览器case尚缺，不能沿用页面200 |
| 网络延迟 | 现有Blackbox图表、tunnel_data_plane_probe及第3节故障矩阵 | 独立RTT/握手/请求/DB阶段；unknown/failed不转0；新harness计划0成功/1断言失败/2前置缺失，未实现 |

可复现命令（只在固定ref隔离checkout与一次性fixture中执行，以下本轮均未运行）：

```sh
# Playbooks，离线fixture使用匹配Ansible/PyYAML的解释器
python3 tests/test_snapshot_token_idempotency.py
python3 tests/test_snapshot_credential_repair.py
python3 tests/data_operations/selfhost/v4_p0_regression_cases_test.py
python3 tests/data_operations/selfhost/v4_duplicate_producer_identity_test.py
# Billing：主动清空真实DB变量，下面仅memory/HTTP测试
TEST_DATABASE_URL='' go test ./internal/httpapi ./internal/service -run 'Test(IngestSnapshot|DecodeSnapshots|DuplicateMinute|NegativeDelta|RestartRecovery|MultiInbound|DeltaCalculation)'
# Exporter
 go test ./internal/snapshot
# 只读候选观察：从已批准inventory传入实际DB node键，非硬编码清单
V4_TRAFFIC_NODE_ID='<env:stable-node-id>' bash tests/data_operations/selfhost/v4_traffic_chain_acceptance.sh
```

脱敏回执必须包含case_id、固定source SHA/image digest、环境/稳定node/transport、实际起止UTC与本地时区、T、至少两个完整周期、各跳计数/最大时间/增量、status、exit_code、skipped、证据路径。身份只用短期受控reference；不附完整快照、SQL参数、UUID、邮箱或秘密散列。NOT_RUN退出码null；BLOCKED不放行。历史PASS保留其日期与环境，不覆盖成当前PASS。

## 7. 最小一期、PR职责与发布顺序

| 阶段 / PR | 责任与最小范围 | 接口 / 配置 / schema | 通过条件 |
| --- | --- | --- | --- |
| P0证据与风险 | Knowledge本文；Playbooks补双周期只读回执与来源唯一清单 | 不改业务schema；回执schema单列版本 | 七节点×实际transport逐一有freshness/投递/DB/查询证据；没有凭据暴露 |
| P1a Billing/Accounts | 复用现有SDK，业务spans、propagator、SQL脱敏、DB pool与错误分类；HTTPtrace分段 | 复用OTEL配置；无账务schema迁移 | 受控trace包含入口/校验/delta/每次DB操作，未知事务不造span；OTLP断连不影响业务 |
| P1b 网络与图表 | Observability/Playbooks复用Blackbox、Node、现有Collector与三个后端；网络/用量两个面板互链 | 固定已有endpoint/protocol，图表和白名单；不新增网关 | 网络故障矩阵通过；线上collector receiver/backend query/图表新鲜度独立通过 |
| P1c Portal | Accounts查询trace与API/页面延迟、用量新鲜度与未知态；不将故障显示0 | 如增加freshness字段，使用可选字段向后兼容；新配置须独立评审 | 同账号同UTC窗口DB/API/UI一致；无缓存伪0 |
| P2关联契约 | Exporter/Vector/Billing可选telemetry envelope、snapshot_ref与span links；验证ack/disk/retry | 新可选字段需版本化契约与旧新混用测试；不改变去重/计费键 | 实际固定Vector通过batch/重试/重启/links测试，不能只测mock |
| P2账务可靠性 | Billing仓单独PR：原子事务、并发锁/唯一约束、乱序/同分钟/崩溃重试 | repository接口需变；schema是否需要唯一键变更须审计现有索引后决定 | 每故障点重试保持桶/ledger/quota/checkpoint一致，双投不重复扣费；独立PG17隔离验收 |
| 声明与交付 | GitOps仅固定非敏感版本与配置，Playbooks执行，Toolkit只编排（如必要） | 不复制Vault字段/静态主机列表；无IaC资源新增 | 精确ref/tag/digest、CMDB目标、回滚版本与回执绑定 |

最小一期可在不改变账务语义的前提下交付“双链路独立测量＋业务阶段trace＋缺口明确展示”；不能在P2账务测试未完成时宣称幂等/崩溃安全已经闭环。

实施发布顺序：各仓隔离实现/单测 → PR审查及合并 → 不可变制品/tag → GitOps固定已发布digest与Playbooks SHA → UAT按 **SSH → Playbook → 固定 GitOps → Doco-CD** 交付 → 两周期业务验收及开销/断连测试 → 取得生产授权后同路径逐节点推广。当前 `v2026.10.21-r5-rc.1` 与GitOps `c7580401b9e8545730e1277edd07d5b6d44bdf94` 只作为用户提供的repair候选组合保留，不擅自替换运行r8声明或视为统一发布版本。

SSH保持默认私钥及严格主机校验，目标来自审批后的CMDB；七节点连接信息不复制成仓库inventory。新机/升级/恢复全部先resolver→校验→保护→0600→内容变更handler→鉴权快照，再验Vector/Billing/DB/API/UI。禁止用重启Xray/Vector/Billing掩盖未知断点。

量化放行建议：全部目标各至少两个完整T周期，snapshot age≤2T+10s；无401/403/5xx与新drop，queue不持续增长；受控正流量分钟增量与DB/API/UI相等，合成测试字节精确相等，真实流量与应用payload因协议开销不得硬比；零流量用零case独立通过。时钟偏差≤100ms；UAT ingest p95≤1s、Accounts用量查询p95≤500ms、页面请求完成后≤5s可见（均为提议预算，需baseline确认）；重复/重启/乱序不得新增扣费。缺任一前置BLOCKED；未运行NOT_RUN。

回滚：先恢复上一不可变应用与GitOps配置，使用同一Playbook/Doco-CD路径；只关闭新增trace导出/采样，不倒退账务事实、不清checkpoint/账本。涉及schema的P2另做备份与隔离恢复演练，不混入观测一期。

## 8. 本轮验证回执

- PASS（只读证据）：#720合并状态；四仓固定main SHA；Knowledge远端起点一致；实际代码/模板与历史case入口定位。
- NOT_RUN：生产SSH、Vault实际读取、渲染配置/进程一致性、线上Collector/后端查询、七节点双周期、Billing投递、PostgreSQL增量、网络故障矩阵、API/浏览器、PG17事务测试与开销测试。
- 本文的PASS只属于文档事实核对，不构成运行验收。正式实施需按case回执逐项替换NOT_RUN。
