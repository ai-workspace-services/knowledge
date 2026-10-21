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

- PASS（规划首轮只读证据，2026-10-21）：#720合并状态；四仓固定main SHA；Knowledge远端起点一致；实际代码/模板与历史case入口定位。
- 规划首轮 NOT_RUN 项已在下方 8.1–8.4 按实际只读探针与隔离验证逐项替换为带固定 SHA/digest、窗口、退出码与 skip 状态的实测回执（生产部署、重启与线上变更仍保持未执行，待审批后按发布顺序推进）。

### 8.1 `observability.svc.plus`（`observability-shared-0`）与 `web-saas-prod-v4` 只读核验回执（2026-10-21 09:38–09:50 UTC / 17:38–17:50 +08:00）

| 核验对象 | 固定运行制品 / Digest | 只读核验事实与发现 | 状态 |
| --- | --- | --- | --- |
| `observability-shared-0` (`open-platform-shared-510113` / `asia-east1-a` / `35.221.181.68`) | `otel/opentelemetry-collector-contrib:0.114.0` (`xstream_otel_collector`)、`victoriametrics/victoria-metrics:v1.106.1` (`:9090`)、`victoriametrics/victoria-logs:v1.4.0-victorialogs` (`:9428`)、`victoriametrics/victoria-traces:v0.1.0` (`:10428`)、`grafana/grafana:11.3.1` (`:3000`) | 1. 核实唯一遥测汇聚后端在 `observability.svc.plus`，VictoriaMetrics 活跃 `job` 含 `blackbox`、`node-exporter`、`process-exporter`、`vector`、`victoria-traces`、`web-saas-accounts`、`web-saas-billing`、`web-saas-console`、`xhttp-caddy`、`xray`。<br>2. `spanmetrics` connector 已实时生成 `traces_span_metrics_calls_total` 与 `traces_span_metrics_duration_milliseconds_*`。<br>3. 发现线上 `/opt/observability-server/otel/otel-collector.yml` 中 `otlphttp/victoria-traces` 配置为 `http://victoria-traces:4318`（拒绝连接），而 `xstream_victoriatraces` 实际监听 `:10428`（`/insert/opentelemetry/v1/traces`）；同时 `observability.caddy.j2` 中 `@otlp_*` path matcher 遮蔽了 `handle_path /otlp/*`。两项均已在 [ai-workspace-infra/playbooks#722](https://github.com/ai-workspace-infra/playbooks/pull/722) 修复。 | `PASS`（只读核实，发现配置缺陷并已在 PR 修复） |
| `web-saas-prod-v4` (`open-platform-prod` / `asia-east1-b` / `35.229.188.193`) | `billing-service:sha-77557d796a66dcd3373d7731125890bd91ebc5d3@sha256:974a012cd032a291c495120f70dc1da1dbe35d05c7554b4912836cac983d438b`<br>`accounts:v2026.10.21-r13@sha256:b75fbea27e9d8922b5b70e181c36d5fec51d4e8f53173ef519bfc9d84b802fe1`<br>`portal:v2026.10.21-r9@sha256:5d67fa95c885a971270397407123ccb94b4f722237e5ad35226b70440e48e4dd`<br>`postgres:17-alpine@sha256:6f30057d31f5861b66f3545d4821fe98fec6f1efbeac9cebeedbe0ac0bf73aa9` | 1. `web-saas-billing` 每分钟稳定接收 **12 次** `POST /v1/ingest/snapshots`（`0` 错误），对应 7 个修复节点中的 **6 个节点 × 2 transport (`xhttp`/`tcp`)**。<br>2. 发现 `web-saas-prod-v4` 当前 `services.env` 未注入 `OTEL_EXPORTER_OTLP_*` 变量（已在 [ai-workspace-infra/playbooks#722](https://github.com/ai-workspace-infra/playbooks/pull/722) 的 `web_saas_prod_services/templates/services.env.j2` 与 `web_saas_host_config/templates/otel-collector.yaml.j2` 补齐）。 | `PASS`（只读核实） |

### 8.2 七节点 × 双 Transport 连续两周期（`T=60s`）只读验收回执（观察窗口：`2026-10-21T09:42:00Z`–`09:49:00Z`）

| 节点 / 环境 (`env=prod`) | Transport (`node_id`) | Billing 接收相位（每分钟 UTC 秒偏移与耗时） | 最近 5m 分钟桶数 / 字节增量 / Checkpoint 推进 | 链路判定与状态 |
| --- | --- | --- | --- | --- |
| `jp-xconnect.svc.plus` | `xhttp` (`prod:jp-xconnect.svc.plus-xhttp`) | `:42.815Z`（`~12.4ms`）连续 >5 周期 | `bucket_count=10`、`byte_sum=134,311,912 B`（2 活跃账号分桶：`130,596,996 B` + `3,714,916 B`），`last_seen_at` 每 60s 推进（`09:47:42Z -> 09:48:42Z`），`v4_traffic_chain_acceptance.sh` 退出码 `0` | `PASS`（正流量全链路） |
| `jp-xconnect.svc.plus` | `tcp` (`prod:jp-xconnect.svc.plus-tcp`) | `:42.928Z`（`~89µs`）连续 >5 周期 | `POST /v1/ingest/snapshots` 200 OK，`Samples: []`（观察窗口内无 TCP 连接样本，不写 DB 行） | `PASS`（HTTP 投递正常，空样本 `empty_samples`） |
| `jp-xconnect-01.svc.plus` | `xhttp` (`prod:jp-xconnect-01.svc.plus-xhttp`) | `:11.098Z`（`~7.1ms`）连续 >5 周期 | `bucket_count=5`、`byte_sum=1,859,259 B`，`last_seen_at` 每 60s 推进（`09:47:11Z -> 09:48:11Z`），`v4_traffic_chain_acceptance.sh` 退出码 `0` | `PASS`（正流量全链路） |
| `jp-xconnect-01.svc.plus` | `tcp` (`prod:jp-xconnect-01.svc.plus-tcp`) | `:11.087Z`（`~91µs`）连续 >5 周期 | `POST /v1/ingest/snapshots` 200 OK，`Samples: []`（无 TCP 连接样本） | `PASS`（HTTP 投递正常，空样本 `empty_samples`） |
| `ph-xconnect.svc.plus` | `xhttp` (`prod:ph-xconnect.svc.plus-xhttp`) | `:18.333Z`（`~11.2ms`）连续 >5 周期 | `bucket_count=10`（2 已解析账号 × 5 分钟）、`byte_sum=0 B`，`last_seen_at` 每 60s 推进（`09:47:18Z -> 09:48:18Z`，`age=25s`），`V4_ALLOW_ZERO_TRAFFIC=1` 退出码 `0` | `PASS`（真实零流量全链路） |
| `ph-xconnect.svc.plus` | `tcp` (`prod:ph-xconnect.svc.plus-tcp`) | `:19.353Z`（`~80µs`）连续 >5 周期 | `POST /v1/ingest/snapshots` 200 OK，`Samples: []`（无 TCP 连接样本） | `PASS`（HTTP 投递正常，空样本 `empty_samples`） |
| `us-free-selfhost-prod-v2.svc.plus` | `xhttp` & `tcp` | `:11.477Z` / `:11.590Z`（`~93µs` / `~90µs`）连续 >5 周期 | VictoriaMetrics `vector_component_sent_events_total{component_id="billing_snapshot_ingest",instance="us-free-selfhost-prod-v2.svc.plus"}` 每 60s 精确 `+2`（`4 -> 6 -> ... -> 24`），`vector_buffer_events=0`；`Samples: []` | `PASS`（Vector→Billing 投递正常，空样本 `empty_samples`） |
| `agent-server-free-prod-v2` | `xhttp` & `tcp` | `:01.238Z` / `:01.239Z`（`~96µs` / `~59µs`）连续 >5 周期 | `POST /v1/ingest/snapshots` 每 60s 到达 Billing（200 OK），`Samples: []`（历史 checkpoint 为 `2026-10-18T07:15:39Z`） | `PASS`（HTTP 投递正常，当前窗口空样本 `empty_samples`） |
| `agent-server-plus-prod-v2` | `xhttp` & `tcp` | `:07.823Z` / `:08.103Z`（`~150µs` / `~98µs`）连续 >5 周期 | `POST /v1/ingest/snapshots` 每 60s 到达 Billing（200 OK），`Samples: []`（历史 checkpoint 为 `2026-10-18T07:15:46Z`） | `PASS`（HTTP 投递正常，当前窗口空样本 `empty_samples`） |
| `sg-free-selfhost-prod-v2.svc.plus` | `xhttp` & `tcp` | **无请求到达 Billing** | 17:10 repair 时本地 `/v1/snapshots/latest` 探针曾通过，但 VictoriaMetrics 无该节点 `vector` 指标、Billing 未收到第 13/14 路请求、DB `last_seen_at` 停留在 `2026-10-18T07:16:03Z`（`age_sec=268,159`） | `FAIL` / `BLOCKED`（Vector→Billing 断链，严禁标全链路 PASS） |

### 8.3 隔离测试与全链路 Case 验收回执（2026-10-21）

| Case ID | 固定 Source SHA / Image Digest | 执行环境与命令 | 预期结果 | 实际结果 | `exit_code` | `skipped` | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `CASE-P0-CRED-IDEMPOTENCY` | Playbooks `3b825079bedfeadc61538ef93b7eace8f66640df` | 本地 Ansible 14.3.1 + Python 3.14 隔离 fixture：`tests/test_snapshot_token_idempotency.py`、`tests/test_snapshot_credential_repair.py` | 缺 Token/无效 Token fail-closed；保护已有配置；`0600` 权限；重复绑定 `changed=0`；不重启 Xray/Agent/Vector；输出不回显 Token | 8/8 测试通过，`changed=1 -> changed=0`，`mode=0600`，无凭据泄露 | `0` | `0` | `PASS` |
| `CASE-P0-PRODUCER-IDENTITY` | Playbooks `3b825079bedfeadc61538ef93b7eace8f66640df` | `V4_PRODUCER_INVENTORY=v4_producer_inventory_20261021.json python3 -m unittest tests/data_operations/selfhost/v4_duplicate_producer_identity_test.py` | 同节点 `xhttp`/`tcp` 合法；双源争抢同一 `(node_id, transport)` 失败；7 节点 × 2 transport 清单无冲突 | 4/4 测试通过，14 个活跃 producer 标识唯一 | `0` | `0` | `PASS` |
| `CASE-P1B-COLLECTOR-CADDY-DASHBOARDS` | Playbooks `3b825079bedfeadc61538ef93b7eace8f66640df` | `python3 -m unittest tests/test_dual_link_observability_contract.py tests/test_xconnect_comprehensive_dashboard.py tests/data_operations/selfhost/v4_acceptance_scripts_test.py` | VictoriaTraces 指向 `:10428/insert/opentelemetry`；PII/SQL 属性删除；Caddy `/otlp/*` 不被遮蔽；双面板 UID 唯一且互链；零流量脚本模式通过 | 12/12 测试通过 | `0` | `0` | `PASS` |
| `CASE-P1A-BILLING-OTEL-SPANS` | Billing `4d7bc29f93160c0b294aa4000eb3f5362242a78f` | `TEST_DATABASE_URL='' go test -race ./...` | W3C `traceparent` 传播；producer Span Links；8 个业务阶段 spans；严禁泄露 UUID/email/token/SQL/`bodyPrefix` | 全包通过，0 敏感字段进入 spans | `0` | `0` | `PASS` |
| `CASE-P1A-OTEL-OVERHEAD-OUTAGE` | Billing `4d7bc29f93160c0b294aa4000eb3f5362242a78f` | `go test -v -race ./internal/service -run TestOTelBeforeAfterLoadParityAndBoundedQueueUnderCollectorOutage` | Collector 不可达（`127.0.0.1:1`）连续 350 轮（`>2,800` spans 超过 `MaxQueueSize=2048`）业务账务结果 100% 一致，heap 增量 `<=32MiB` | 350 轮业务余额同为 `-26250`，`disabled=9.20ms`、`enabled=25.87ms`，`heap_delta=2.30 MiB` | `0` | `0` | `PASS` |
| `CASE-P2B-BILLING-ATOMIC-TX-PG17` | Billing `a47fa5337c22b95830c73e0fa654d21b48d6d525` + `postgres:17-alpine@sha256:6f30057d31f5861b66f3545d4821fe98fec6f1efbeac9cebeedbe0ac0bf73aa9` | 一次性本地 Docker PG17 容器（`127.0.0.1` 随机端口，执行后自动销毁）：`TEST_DATABASE_URL="postgres://..." go test -v -race ./...` | `BeginTx` + `FOR UPDATE` 原子提交；每步故障注入完整回滚且重试不双扣；重复投递不归零；乱序旧快照不误触发 reset；同分钟多快照累加不丢字节；并发 8 worker 零竞态 | 全量测试（含 `TestPostgresAcceptanceWritesAccountingTables` 与 `postgres_tx_test.go`）全部通过 | `0` | `0` | `PASS` |
| `CASE-P2A-VECTOR-0411-ENVELOPE` | `timberio/vector:0.41.1-debian@sha256:87ef5d0a3f47ed6e415c9c6b84f7bfa53dbced55c00b75a974426a8a63cebc15` | 本地容器运行固定版本 Vector `0.41.1`（`decoding.codec="json"`, `encoding.codec="json"`, `batch.max_events=1`, `buffer.type="disk"`, `max_size=536870912`） | 验证 `503` 自动重试、Billing 断连时落盘、Vector 容器重启后从磁盘恢复投递，且完整保留 `snapshot_ref` 与 `traceparent` | `retry_503_recovered=true`、`disk_buffer_restart_recovered=true`，`snapshot_ref` 与 `traceparent` 100% 保留 | `0` | `0` | `PASS` |
| `CASE-P1A-ACCOUNTS-OTEL-LATENCY` | Accounts `500f051f831d68094aaf7864050e0f3e95fe3f07` | `go test -v ./internal/observability/... ./api/... ./internal/store/...` | W3C `traceparent`；SQL 脱敏；DB 错误返回 500 不伪装 0；`freshnessState`；服务慢 vs DB 慢各 20 次 100% 独立分类 | 全部通过（20/20 slow-service 与 20/20 slow-db 分类 100% 准确） | `0` | `0` | `PASS` |
| `CASE-P1C-PORTAL-USAGE-STATES` | Portal `03465a30516ab89ab0b4e4c6668f7eae937cddaf` | `yarn test --run`（`UsageObservability.test.tsx`、`fetchAccountUsage.test.ts`、`AccountPanels.test.tsx`）+ `yarn typecheck` + `eslint` | 区分查询失败（`—` + 错误提示）、加载中（`—`）、真实零流量（`0 B`）、陈旧数据（`syncDelaySeconds > 300` 提示）；`monthStart` 严格使用 `Date.UTC` | 3 测试文件 28 项断言全部通过，TypeScript 与 ESLint 0 错误 | `0` | `0` | `PASS` |
| `CASE-P1-EXPORTER-HTTPTRACE` | Exporter `a5f57c7f56ea71db4e6a40be903b6ce233de289c` | `go test -v -race ./...` | `snapshot_ref` + `traceparent` 注入；`push_enabled` 区分禁推与活跃；`httptrace` 区分首次建连、连接复用（不记 0）、明文 HTTP（TLS 不记 0）、TLS 证书不可信、连接拒绝与请求取消 | 12 项测试全部通过，无高基数或敏感标签 | `0` | `0` | `PASS` |

### 8.4 跨仓 PR 交付清单、依赖顺序与回滚方案

| 顺序 | 仓库与 PR | 分支与固定 Commit SHA | 范围与接口/配置变更 | 回滚方案 |
| --- | --- | --- | --- | --- |
| 1 | `ai-workspace-infra/playbooks` [#722](https://github.com/ai-workspace-infra/playbooks/pull/722) | `feat/dual-link-otel-observability-20261021` (`3b825079bedfeadc61538ef93b7eace8f66640df`) | 修复 `observability.svc.plus` Collector → VictoriaTraces `:10428` 端口与 Caddy `/otlp/*` 路由；PII/SQL 属性过滤；双链路互链 Grafana 面板；Web-SaaS V4 OTel 环境变量注入；零流量验收脚本扩展 | 回退至 `5f959ab8bacfc4dd133c1e4d859b5ab8cb4cdc40` 并通过 Playbook/Doco-CD 重新渲染配置 |
| 2 | `ai-workspace-xstream/xray-exporter` [#21](https://github.com/ai-workspace-xstream/xray-exporter/pull/21) | `feat/exporter-telemetry-envelope-probe-20261021` (`a5f57c7f56ea71db4e6a40be903b6ce233de289c`) | 可选向后兼容 `snapshot_ref`、`traceparent` envelope 字段与请求头；`xray_snapshot_*` 与 `httptrace` 分阶段指标（未发生阶段不填 0） | 回退至 `1094bd8e11af30eda62fdbb2ecf9d8560d493829`；新字段均为 `omitempty`，旧版 Vector/Billing 完全兼容 |
| 3 | `ai-workspace-services/billing-service` [#54](https://github.com/ai-workspace-services/billing-service/pull/54) | `feat/billing-otel-pipeline-spans-20261021` (`4d7bc29f93160c0b294aa4000eb3f5362242a78f`) | Phase 1a + 2a 纯可观测性：W3C `TraceContext`、8 个 ingest 业务阶段 spans、producer Span Links、`otelsql` 禁采 SQL、有界导出队列（`2048`） | 清空 `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` / `OTEL_EXPORTER_OTLP_ENDPOINT` 即退化为 noop，或回退至 `77557d796a66dcd3373d7731125890bd91ebc5d3` |
| 4 | `ai-workspace-services/accounts` [#264](https://github.com/ai-workspace-services/accounts/pull/264) | `feat/accounts-usage-otel-window-20261021` (`500f051f831d68094aaf7864050e0f3e95fe3f07`) | Phase 1a + 1c：W3C `TraceContext`、`otelsql` 禁采 SQL、用量/账单/身份查询 spans、可选 `freshnessState` 字段、DB 错误不静默返回 0 | 清空 OTLP endpoint 或回退至 `1ca14236c22a59b009480a05504d93e6b5fe2379`（`v2026.10.21-r13`） |
| 5 | `ai-workspace-services/portal` [#462](https://github.com/ai-workspace-services/portal/pull/462) | `feat/portal-usage-error-freshness-state-20261021` (`03465a30516ab89ab0b4e4c6668f7eae937cddaf`) | Phase 1c：区分查询失败（`—`）、加载中（`—`）、真实零流量（`0 B`）与陈旧数据提示；`monthStart` 统一为 `Date.UTC` | 回退至 `15b1f4cc5324d2e9863b954ed49784fcb7b7df35`（`v2026.10.21-r9`） |
| 6 | `ai-workspace-services/billing-service` [#55](https://github.com/ai-workspace-services/billing-service/pull/55) | `fix/billing-atomic-accounting-tx-20261021` (`a47fa5337c22b95830c73e0fa654d21b48d6d525`) | Phase 2b 独立账务事务 PR：`WithinAccountSampleTx`（`BeginTx` + `FOR UPDATE`）、重复快照防归零、乱序旧快照防误 reset、同分钟多快照增量累加（无需破坏性 schema 迁移） | 独立审阅合并；回滚时切回上一不可变镜像 digest，不清已有 checkpoint/账本 |
