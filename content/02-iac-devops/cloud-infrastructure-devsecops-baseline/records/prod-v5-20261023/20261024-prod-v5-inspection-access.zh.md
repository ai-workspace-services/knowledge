# PROD V5 系统与业务只读巡检回执

采样及执行：2026-10-24 13:11:56–13:14:58，Asia/Shanghai；run_id：`v5-inspection-access-20261024`。本记录仅补充巡检权限，未执行数据迁移、镜像更新、公共 DNS 或 V4 变更。

[运行基线与快照清单](prod-v5-runtime-and-snapshot-baseline-20261023.zh.md) · [V4→V5 复盘](../../17-prod-v4-v5-baseline-and-upgrade-retrospective.zh.md) · [统一流程白皮书](https://github.com/ai-workspace-services/.github/blob/main/docs/control-plane-deployment-and-migration.zh.md)

## 缺口与实际修复

初次检查未发现独立 OS 巡检登录账号；已有 `readonly_release` 可登录、默认只读，但业务库 76 张表可读数为 0，不能承担业务巡检。该历史迁移角色保留原权限，没有重命名、删除或扩大授权。

本轮创建 `auditor` 与 `db_readonly`。云控制面核对目标为 V5，SSH 使用已有可信主机密钥；资源身份、地址、公钥和原始日志仅保存在受控证据中。权限配置由 Playbooks 管理，不写入 GitOps 业务声明或 IaC 云资源模块。

| 对象 | 权限与边界 | 真实验收 |
| --- | --- | --- |
| OS `auditor` | SSH 公钥登录、密码锁定，无特权组；禁止 TCP/Agent/X11 转发及隧道 | 登录成功；仅普通用户组 |
| 受限 sudo | `/usr/local/sbin/platform-inspect` 固定子命令 `containers`、`container-logs`、`logs`、`services`、`processes`、`database` | 容器、系统/容器日志、服务、进程查看全部 exit 0 |
| Docker | 通过 root 所有、不可由审计账号修改的固定入口读取；不授予 Docker socket 或管理权 | 直接 `docker ps` 被拒绝，exit 1 |
| 系统保护 | 不授予通用 sudo；无保护文件写权限 | `sudo id` 被拒绝，exit 1；`test -w /etc/passwd` 返回 1 |
| DB `db_readonly` | 独立 LOGIN 角色、无密码，仅用于既有容器本地连接；非超级用户，无建库/建角色/复制/BYPASSRLS/继承权限 | 网关实际连接身份为 `db_readonly`，users 计数 33；未归档用户字段 |
| 业务库权限 | public 表/序列 SELECT、schema USAGE；给配置 owner 的后续表/序列授予默认 SELECT；现有 RLS 表配置 SELECT-only 策略 | 76/76 张表可读、0 张可写；主动 `BEGIN READ WRITE` 后零行 DELETE 仍报 permission denied，exit 1 |
| 重复应用 | 最终配置真实复跑 | `changed=0`、`failed=0`、`unreachable=0` |

普通 OS 用户仍可写自己的 home 和系统允许的临时目录，不能称为内核级全文件系统只读沙箱。日志与业务查询可能包含敏感数据，仅向获准巡检者开放，不将原始输出提交公开仓库。未来新增 RLS 表须单独复核 SELECT 策略；默认 SELECT 不自动越过 RLS。

## 固定实现、回归与证据

- [Playbooks #747](https://github.com/ai-workspace-infra/playbooks/pull/747)：实际执行 source commit `54b8fc9370182ecf347000e82382ec9b497bbdf9`；随后于 2026-10-24 13:16:32 +08 合并，main commit `93fb9b95a752fb5d06a1c56c69e274e17164402b`。现场执行早于合并，不把合并后的 ref 冒充执行 ref。
- [入口 playbook](https://github.com/ai-workspace-infra/playbooks/blob/93fb9b95a752fb5d06a1c56c69e274e17164402b/configure_inspection_access.yml)仅选择目标并调用 role；[role README](https://github.com/ai-workspace-infra/playbooks/blob/93fb9b95a752fb5d06a1c56c69e274e17164402b/roles/inspection_access/README.md)定义输入、权限边界及撤销方式。
- [真实回归 case](https://github.com/ai-workspace-infra/playbooks/blob/93fb9b95a752fb5d06a1c56c69e274e17164402b/tests/test_inspection_access.py)：非法操作不执行、SQL 固定 reader 与非 meta-command 入口、日志有界且无分页器，3/3 PASS；Ansible syntax-check PASS；PR 安全检查 PASS。
- 受控证据索引：`verification.json`、`apply-1.log`、`apply-2.log`、`apply-3.log`；前两轮包含首次创建与新增巡检入口，不能记成三轮无差异。仅最终复跑为零变更。单次临时 inventory 执行后已删除。
- 本轮只变更访问控制与 SSH drop-in；未重启业务服务，SSH 配置校验后 reload。镜像/tag/digest、业务 schema 版本与迁移校验和沿用既有基线，本轮未重新采集，标 NOT_RUN，不能推断全部环境无差异。

## 快照边界与后续恢复

既有 11:19–11:21 逻辑快照早于本次权限修复，不能声称已包含新 OS 用户、网关脚本、sudoers 或 DB 授权。本轮未重新生成或验证数据/整机快照（NOT_RUN）。恢复旧快照后须从固定 Playbooks ref 重新收敛权限，再执行允许读取与拒绝写入测试；全新恢复后的权限验收尚 NOT_RUN。

撤销时先禁用专用登录和 sudo 入口，再撤销该数据库角色的 CONNECT/SELECT、默认授权与专属 RLS 策略；不删除业务数据，不修改既有迁移角色。恢复与切换仍按统一白皮书独立验收。
