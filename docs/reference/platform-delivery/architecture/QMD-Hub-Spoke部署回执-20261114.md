# QMD Hub-Spoke 部署回执（2026-11-14）

> **基线**：[knowledge#400](https://github.com/ai-workspace-services/knowledge/pull/400) —
> [`QMD单体运行与分布式异步同步架构规范.md`](QMD单体运行与分布式异步同步架构规范.md)、
> [`qmd-monolithic-engine-distributed-async-sync-spec.zh.md`](../../qmd-monolithic-engine-distributed-async-sync-spec.zh.md)
> **执行时间**：2026-11-14 19:20–19:55（UTC+8）
> **关联 PR**：playbooks [#1024](https://github.com/ai-workspace-infra/playbooks/pull/1024)（roles `qmd_hub` / `qmd_standalone`）·
> gitops [#931](https://github.com/ai-workspace-infra/gitops/pull/931)（`https://qmd.svc.plus` 入口）· 均未合并。
> 本文不含任何 token、密码或凭据值。

## 一、拓扑

| 节点 | 规范级别 | 角色 | 组成 |
|---|---|---|---|
| sit-k3s-v6（5.189.172.69，Debian 13） | **第 4 级 企业持久存储模式** + **Hub-Spoke 中心** | Hub | L1 QMD/SQLite + L2 PostgreSQL 17/pgvector + L3 Google Drive 每日归档（配置就绪、缺凭据） + Delta Sync API |
| Grok Bot box | **第 1 级 最简模式** | Spoke（origin `grok-bot-box`） | QMD + SQLite + sync（push/pull 双向异步） |

源码：`ai-workspace-lab/qmd` main @ `917637d9fea7e7ecaf31d745837983c24eebf202`（qmd 2.8.3，含 memory-tiers / lazy PG bridge）。

## 二、Hub（sit-k3s-v6）

| 项 | 值 |
|---|---|
| 部署方式 | `ansible-playbook deploy_qmd_hub.yml -e target_hosts=sit-k3s-v6`（role `roles/vhosts/qmd_hub`，单次临时 inventory，执行后删除） |
| 系统用户 / 目录 | `qmdhub`（system，密码锁定）· `/opt/qmd-hub`（src/runtime/config/cache/data/state/mem）· `/etc/qmd-hub` |
| Node 运行时 | 独立 `/opt/qmd-hub/runtime/node`（v24.22.1，官方 SHASUMS256 校验），不改系统 node |
| `qmd-hub.service` | `qmd mcp --http` 仅 `127.0.0.1:8181`；`/mcp` `/query` `/search` 需 Bearer（`/etc/qmd-hub/mcp-token`） |
| `qmd-hub-syncd.service` | Delta Sync API，仅绑定 CNI 网桥 `10.42.0.1:8182`；ufw 只放行 `10.42.0.0/16`；Bearer（`/etc/qmd-hub/sync-token`） |
| L2 PostgreSQL | 专用集群 `17/qmdhub`，`127.0.0.1:5433`，库 `qmd_memory`，角色 `qmdhub`（peer + scram，密码 `/etc/qmd-hub/pg-password`）；扩展 `vector` `pg_trgm`；表 `qmd_hub_changes`（fence 日志）、`qmd_hub_archive_runs` |
| L3 归档 | `qmd-hub-archive.timer` 每日 03:00（UTC+8）；rclone `copy --ignore-existing`，只上传新 `.md`（`raw/YYYY/MM/DD/<origin>/<collection>/<path>.<sha8>.md` + 运行 manifest），不原地编辑；疑似密钥文件隔离 |
| 秘密文件 | `/etc/qmd-hub/{mcp-token,sync-token,pg-password}` 均 `qmdhub:qmdhub 0600`，主机本地生成，未回传 |
| 未改动 | k3s、Flux、集群内 `postgresql-sit`、现有端口与服务、DNS 记录 |

**为何不用集群内 PG**：`postgresql-sit` 由 GitOps（`web-saas-fullstack` chart）管理，新增库/角色需经 GitOps/Vault 声明；用 kubectl 直改违背交付规范。Hub 选用本机独立 PG17+pgvector（仅回环），与集群解耦。

## 三、Spoke（Grok Bot box）

| 项 | 值 |
|---|---|
| 部署方式 | `ansible-playbook deploy_qmd_standalone.yml`（role `roles/vhosts/qmd_standalone`，local connection） |
| 目录 | `~/qmd-spoke`（`bin/qmd` 隔离 `QMD_CONFIG_DIR`/`INDEX_PATH`、`notes/`、`mirror/`、`state/`）；源码 `~/.local/src/qmd` |
| Collections | `knowledge`（本仓库 `docs/` 只读镜像，同步前 `git pull --ff-only`）、`notes`、`hub-mirror`（从 Hub 拉回的其他 origin） |
| 同步命令 | `/workspace/qmd-sync/sync.sh`（= push + pull 一条命令；`--watch` 订阅 SSE） |
| 传输 | `https://qmd.svc.plus/api/v1/sync/*`（Bearer，token `~/qmd-spoke/hub-token` 0600）；HTTPS 不可达时回落到受限 SSH 隧道（`qmdhub@5.189.172.69`，仅 `permitopen=10.42.0.1:8182`，无 shell） |

## 四、同步协议（实现）

- **push**：Outbox = 本地 manifest 与上次成功推送 manifest 的差异 → `POST /plan`（Hub 回报缺失/不同文件）→ `POST /put`（仅差量，sha256 校验，原子写）→ `POST /commit`（校验全量哈希，删除多余，`qmd-hub-ingest` 在 PG 中按内容分配递增 `fence`，`qmd update`）。
- **pull**：`GET /changes?since_fence=N&exclude_origin=self` → 每个 key 取最高 fence → 按 sha256 判断后 `GET /file` → 原子写入只读 `mirror/` → 全部校验通过才推进 `since_fence`。
- **冲突**：每个 origin 只写自己的命名空间（Hub 侧笔记为 origin `hub`）；同 key 以最高 fence 为准；内容哈希相同不产生新 fence。
- **断网续传**：状态只在成功步骤后推进；`/plan` 只请求缺失文件，重跑即续传。
- **SSE**：`GET /events` 推送 `fence` 事件。

## 五、验证结果

| 验证 | 命令 / 方式 | 结果 |
|---|---|---|
| Hub role 首次 | `--check --diff`（首装仅预检）→ apply | apply `ok=54 changed=14 failed=0` |
| Hub role 幂等 | 再次 `--check` / apply | `changed=0` / `ok=52 changed=0 failed=0` |
| Hub 服务 | `systemctl is-active qmd-hub qmd-hub-syncd postgresql@17-qmdhub qmd-hub-archive.timer` | 全部 active；监听仅 `127.0.0.1:8181`、`10.42.0.1:8182`、`127.0.0.1:5433` |
| L2 | `qmd pg status` / `qmd tier status` | PostgreSQL 17.12 · `+pg_trgm +pgvector` · invariant ok |
| L3 | `systemctl start qmd-hub-archive` | `credentials-missing`（预期，见第六节） |
| box → Hub | 首次 `sync.sh` | push 727 文件 → fence 1..727；Hub `qmd search qmd-spoke-canary-7f3a` 命中 `grok-bot-box--notes` |
| Hub → box | Hub `qmd-hub-note verify/hub-canary.md` → `sync.sh` | fence 728，pull fetched=1；box `qmd search qmd-hub-canary-91c2` 命中 `hub-mirror` |
| 增量 / 幂等 | 修改 1 篇笔记 → `sync.sh` ×2 | 仅新增 fence 729；第二次 outbox 空、changes=0 |
| HTTPS 入口 | 临时（无 DNS 标签）应用 GitOps 同款对象，在主机 `curl --resolve qmd.svc.plus:443:5.189.172.69` | 证书 `CN=svc.plus`，SAN `*.svc.plus`，Let's Encrypt YE2，到期 2027-01-05，verify=0；`/health` 200；无 token 401；带 token `/changes`、SSE 正常；`/mcp` 404。验证后已删除临时对象 |
| DNS | Cloudflare DoH | `qmd.svc.plus` 当前 NXDOMAIN；待 gitops#931 随新 release ref 生效后由 ExternalDNS 创建 |

## 六、与规范的差异 / 待办

1. **规范示例与仓库能力**：`QMD_ROLE=hub`、`qmd-hub --daemon`、`POST /api/v1/sync/push`、`QMD_HUB_URL` 在 `ai-workspace-lab/qmd` 中不存在（仓库已有：SQLite/FTS5、`qmd sync`（SSH+rsync 双向、不同步索引）、`qmd mcp --http`（/mcp /query /search /health，Bearer）、PG backend、memory-tiers L1/L2/L3）。Hub-Spoke Delta API 由 playbooks role 内的 `qmd-hub-syncd` 实现，端口 `8182`，路径 `/api/v1/sync/*`。
2. **Embedding**：两端均未配置 `QMD_EMBED_API_*`，当前为 BM25（SQLite FTS5 / PG FTS）；“Hub 集中计算向量并随增量下发 sqlite-vec”未实现。
3. **L3 Google Drive 凭据缺失**：需用户提供 `/etc/qmd-hub/rclone.conf`（owner `qmdhub`，`0600`），内含 remote `[qmd-archive]`（Drive 服务账号 JSON 或 OAuth token，建议存 Vault 如 `kv/sit/qmd-hub/archive` 后由运维落盘）；目标路径 `qmd-archive:ai-workspace-archive/qmd-hub/sit-k3s-v6`。未复制任何个人 token。
4. **对外入口未生效**：gitops#931 待合并且需新的 Flux release ref（当前 tag `sit-k3s-v6-contabo-r20`）；期间 box 自动走 SSH 隧道兜底（已验证）。box 出站对未解析的 SNI 会被拦截，DNS 生效后再复测 HTTPS 直连。
5. **鉴权粒度**：单一共享 sync token，未按 Spoke 区分；`pg_jieba` 未安装（FTS 使用 english 配置）。
