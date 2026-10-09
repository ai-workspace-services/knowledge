---
title: CMDB Shared UAT 部署与采集验收记录
lang: zh
date: 2026-10-09
status: partial-live-verification
category: reference
---

# CMDB Shared UAT 部署与采集验收记录

## 目标和版本

本次直接通过 gcloud SSH 操作 GCP `open-platform-shared`、`asia-east1-a`、`observability-shared-0`。独立容器 `xstream_cmdb_postgres_uat`、持久卷 `xstream_cmdb_postgres_uat_data`、数据库/schema `cmdb` 已运行，容器健康为 healthy。当前公共 Observability DNS 指向另一个 Shared 项目的主机，本次没有进行 DNS 切换。

| Owner | 已执行源码与 PR |
| --- | --- |
| IaC GCP 采集 | `79d14f03dbd8cd57acdd240db19f232f70a4d16b`；[PR #420](https://github.com/ai-workspace-infra/iac_modules/pull/420) |
| Playbooks 事务入库、权限与迁移验证 | `9d4fbf77d8f9c18d4fd452d20d2c16bdace1178d`；[PR #639](https://github.com/ai-workspace-infra/playbooks/pull/639) |
| Playbooks Grafana 面板验证 | `1bd26e9411be0eb6b36778ec42a15bf070e6d98b`；同一 PR |
| GitOps 采集范围 | `291e0e9cf35e3c72e26a97bc1703adffc52e7328`；[PR #418](https://github.com/ai-workspace-infra/gitops/pull/418) |

以上为本次直接 UAT 执行的固定 commit；PR 提交不等于已 merge main、不可变发布 tag 或 PROD 晋级。当前运行的是按需采集快照，定时采集没有启用。按用户最新要求，不补全 bootstrap 脚本。

## 真实 API 结果

2026-10-09 的 GCP 原生 API 观察与 PG/Grafana 查询一致：

| 资源范围 | 状态 | 数量 |
| --- | --- | ---: |
| open-platform-prod Compute | running | 2 |
| 两个 Shared 项目 Compute | running | 5 |
| open-platform-shared-510113 Compute | suspended | 1 |
| open-platform-prod Cloud Run / asia-east1 | ready | 4 |
| open-platform-shared Cloud Run / asia-east1 | 完整范围成功、无服务 | 0 |
| open-platform-shared-510113 Cloud Run / asia-east1 | HTTP 403；API 未启用 | 未知，不能解释为 0 |

Compute 共 8 台、运行 7 台；Cloud Run 服务共 4 个，仅代表本次声明的 `asia-east1` 范围。两个项目的同名主机按 numeric instance ID 保持独立，服务使用 Cloud Run UID；没有把修订或路由计入服务数量。

| Collector 范围 | run ID | 结果 |
| --- | --- | --- |
| Shared Compute | `19120fff-f424-4afb-bbb7-ed4bddca5e0e` | success / 3 |
| Shared-510113 Compute | `7afb59f5-cfb9-4cb3-ae0a-d2eeec73ad2c` | success / 3 |
| PROD Compute | `5edf62af-0ba0-41be-a97b-7f792992cf07` | success / 2 |
| PROD Cloud Run | `937f9d04-da1a-475f-bf22-e6684437dad5` | success / 4 |
| Shared Cloud Run | `97a3343a-ee07-4e7d-b249-481d19163bfe` | success / 0 |
| Shared-510113 Cloud Run | `a279f9ee-828d-4ea2-b20a-2f97b0ba9ef8` | failed / http_403 |

6 个回执与 12 条真实观察已入 PG。整体采集是 partial，失败范围的库存仍未知。旧 UAT fixture 已设为 retired，保留历史；迁移 `002_present_provider_summary.sql` 排除非 present 资源，避免污染当前数量。

## 数据库、重放与 Grafana 验证

- `001` 初始 schema 与 `002` summary 迁移已显式执行；普通 ingestion 不初始化 database、role 或 schema。
- 真实使用 `cmdb_reader` 尝试 UPDATE 被拒绝；使用 `cmdb_writer` 尝试在 cmdb schema 建表被拒绝，测试事务均回滚。
- 写入前备份位于主机 `/opt/observability-server/cmdb-uat/backups/`，包含 `cmdb-before-ingest-20261009T132333Z-1935450.dump` 与重放前的 `cmdb-before-ingest-20261009T132508Z-1937641.dump`。已验证 custom archive manifest；尚未证明完整恢复演练。
- 同一 envelope/run 重放后 raw_snapshots 仍为 12 条、真实当前资源仍为 12 条，历史记录幂等。
- datasource `cmdb_postgres_uat` 使用 `cmdb_reader`，health=OK；dashboard `cmdb-resource-overview` 的 6 个 SQL 面板全部通过。
- 面板显示 Compute=8、Serverless=4、stale/unknown=0（验证时刻）、monitoring coverage=0；这不能推断探针已部署。
- 主机 release artifact 路径为 `/opt/observability-server/cmdb-uat/releases/9d4fbf77-79d14f03/`，权限验证回执保留于 `verify.poa1W2Id`、`verify.lo7MlyZG`；快照新鲜度随时间自然转为 stale。

## 身份、网络与未完成项

当前本地 GCP 登录身份能查询指定范围，Shared 主机 metadata service account 查询 Compute 返回 403。没有修改 IAM、启用 Cloud Run API、写入 Vault 或启动定时采集。

SSH 规则 `open-platform-shared-observability-ssh-current-egress` 允许当时出口 `54.199.179.163/32` 的 TCP/22，目标 tag 为 vault。直连已验证；临时 IAP 规则 `cmdb-uat-iap-ssh-1791550421` 已删除。出口变化时需按实际 IP 重新核实，不能将该值当作永久出口。

数据库仍使用主机内生成、root-owned 0600 的运行时凭据文件。Vault 路径及字段见[路径规划](cmdb-vault-paths.zh.md)，尚未 provision 或切换 consumer；Docker 私网数据库连接尚未启用远程 TLS。

仍需完成：精确只读 workload identity、Vault Agent 与凭据轮换、定时采集、AWS/Linode/UCloud TW-PH 只读身份及实际产品 adapter、Cloudflare/Supabase 范围与身份、主机探针逐台部署与两周期中心端上报验收、完整备份恢复演练及受保护发布流程。当前 API、PG 和 Grafana 的 GCP 结果不能替代这些证据。

