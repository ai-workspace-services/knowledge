# 修复重复 `EXPORTER_NODE_ID` 导致的 Checkpoint 乒乓重复计费与配额误耗尽

- **日期**: 2026-11-23
- **所属组织 / 服务**: `ai-workspace-services`（`accounts`、`billing-service`、`portal`、PostgreSQL `account`）
- **关联外部仓修复**:
  - `ai-workspace-infra/playbooks#1046`（强制 `EXPORTER_NODE_ID == AGENT_PROXY_DOMAIN`）
  - `ai-workspace-xstream/xconnect-edge-agent#167`（`setup-observability.sh` 显式注入 `AGENT_PROXY_DOMAIN` / `xray_exporter_node_id`）
- **关联 XStream 故障复盘**: `ai-workspace-xstream/docs` (`incidents/2026-11-23-duplicate-exporter-node-id-billing-pingpong.md`)
- **关联 Infra Runbook**: `ai-workspace-infra/docs` (`runbooks/2026-11-23-exporter-node-id-uniqueness-and-billing-pingpong.md`)

---

## 1. 问题描述

1. **实时用量账单异常虚增**:
   - `accounts.svc.plus` / Portal 用量汇总（数据源 PostgreSQL `traffic_minute_buckets`）在单一用户无异常大流量下载的情况下，出现**最近 24 小时 `75.82 GiB`、本月合计 `482.84 GiB`** 的账单虚增（同期底层真实代理流量仅约 `21.78 GiB`）。
   - 该虚增扣费导致 Pro 套餐 `50 GiB` 基础配额被提前扣穿（`remaining_included_quota = 0`）。
2. **客户端异常差异**:
   - 当配额被扣为 `0` 后，`accounts` 对 `/api/agent-server/v1/nodes` 与 `/api/auth/sync/config` 返回 `HTTP 403 quota_exhausted`，触发 macOS `xconnect-app` 的 `DesktopSyncService` 进入 `_stopManagedAccess('quotaPaused')` 停用托管节点；同时未开启单机邮箱白名单兜底的边缘节点将用户 UUID 从 Xray 运行配置移除。
   - 配有单机 `allowedEmails` 白名单的节点短期仍可放行移动客户端，掩盖了控制面已配额耗尽的事实。

---

## 2. 诊断步骤与证据链

### 2.1 检查 `traffic_stat_checkpoints` 高频重置与分钟桶平台连跳

```sql
-- 1) 排查 reset_epoch 异常攀升的 node_id
SELECT node_id, count(*), max(reset_epoch) AS max_reset_epoch, max(updated_at)
FROM traffic_stat_checkpoints
GROUP BY node_id
ORDER BY max_reset_epoch DESC;

-- 2) 排查连续分钟反复出现相近大额差值的平台连跳窗口
WITH lagged AS (
  SELECT bucket_start, node_id, account_uuid, uplink_bytes, downlink_bytes, total_bytes,
         lag(uplink_bytes) OVER (PARTITION BY node_id, account_uuid ORDER BY bucket_start) AS prev_up,
         lag(total_bytes) OVER (PARTITION BY node_id, account_uuid ORDER BY bucket_start) AS prev_total,
         lag(bucket_start) OVER (PARTITION BY node_id, account_uuid ORDER BY bucket_start) AS prev_ts
  FROM traffic_minute_buckets
  WHERE bucket_start >= now() - interval '72 hours' AND total_bytes > 0
)
SELECT date_trunc('hour', bucket_start) AS hr,
       node_id,
       count(*) AS mins,
       round(sum(total_bytes)/1073741824.0, 3) AS sum_gib,
       round(avg(total_bytes)/1048576.0, 2) AS avg_mib
FROM lagged
WHERE total_bytes > 100 * 1048576
  AND prev_total > 100 * 1048576
  AND bucket_start - prev_ts <= interval '5 minutes'
  AND abs(uplink_bytes - prev_up)::numeric / GREATEST(uplink_bytes, 1) < 0.25
GROUP BY 1, 2
ORDER BY sum_gib DESC;
```

### 2.2 根因机理（`billing-service` Checkpoint 乒乓循环）

`billing-service/internal/service/service.go` 中的 `processSampleLocked` 以 `(node_id, account_uuid)` 作为 `traffic_stat_checkpoints` 主键计算单调递增差值：

1. 两台物理边缘节点（`jp-xconnect-01.svc.plus` 与 `jp-xconnect-02.svc.plus`）的 `xray-exporter` 使用了相同的 `EXPORTER_NODE_ID=jp-xconnect-02.svc.plus`，两者均以 `prod:jp-xconnect-02.svc.plus-xhttp` 每分钟错开约 30 秒推送快照。
2. 当累计值较小的节点先推送时，`delta < 0` 触发计数器重置分支（`reset_epoch++`），将 `traffic_stat_checkpoints` 覆盖为较小累计值后返回，不写分钟桶。
3. 约 30 秒后累计值较大的节点推送时，`billing-service` 计算 `delta = 较大累计值 - 较小累计值 > 0`，将**两节点历史累计值之差**作为当分钟新增流量写入 `traffic_minute_buckets` 并扣减配额。
4. 下一分钟循环往复（2026-11-22 `16:41~17:06 UTC` 连续每分钟均被记入 `~1,079.9 MiB`），仅 24 小时内就制造了 `> 55 GiB` 的虚假计费。

---

## 3. 修复与数据订正

1. **边缘侧唯一标识对齐**：
   - 将受影响节点 `/etc/xray-exporter.env` 的 `EXPORTER_NODE_ID` 与 `AGENT_PROXY_DOMAIN` 对齐为各自唯一域名，同步更新 systemd `--node-id`、重命名本地 72h 快照缓存的 `node_id`，并在数据库中预先同步新 `node_id` 的当前累计 `traffic_stat_checkpoints`，防止重启瞬间重放历史总量。
2. **PROD 数据库备份与清洗**：
   - 备份 11 月原始分钟桶至 `public.traffic_minute_buckets_backup_20261123`（`278,619` 行）。
   - 对留存原始快照的 72h 窗口（`2026-11-19 23:47 UTC ~ 2026-11-23 00:05 UTC`），从两节点本地 `/var/lib/xray-exporter/xhttp-snapshots.json` 重建真实单调增量桶（`18,820` 行替换混合期间的 `20,444` 行）。
   - 对更早期无原始快照窗口，基于 `(node_id, account_uuid)` 15 分钟前序高水位差值去重（修正 `10,859` 行异常记录）。
   - 基于清洗后的 `traffic_minute_buckets` 重算全部 `41` 个账户的 `account_quota_states`（按双桶区分 `routing_pool = 'Pro-EC2-Pool'` 与常规池）。
3. **编排层防呆**：
   - 通过 `playbooks#1046` 与 `xconnect-edge-agent#167` 强制断言 `EXPORTER_NODE_ID == AGENT_PROXY_DOMAIN` 且禁止 `localhost`。

---

## 4. 验证与回滚

- **验证指标（受影响账号恢复前后对比）**：
  - 最近 24 小时用量：`75.82 GiB` → **`20.65 GiB`**（消除虚增 `-55.17 GiB`）
  - 本月合计用量：`482.84 GiB` → **`205.19 GiB`**（消除虚增 `-277.65 GiB`）
  - 配额状态恢复正常，不再错误返回 `403 quota_exhausted`。
- **回滚方案**：若需回滚数据库清洗，可在一个事务内从 `public.traffic_minute_buckets_backup_20261123` 恢复 11 月分钟桶并重新汇总配额（注意：**禁止回滚边缘节点的重复 `EXPORTER_NODE_ID`**）。
