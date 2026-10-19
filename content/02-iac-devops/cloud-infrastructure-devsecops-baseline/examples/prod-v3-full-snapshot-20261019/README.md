# V3 全量快照：2026-10-19 维护源码归档

这些 `.py.txt` 文件保存本次受授权 V3 维护操作使用的原始源码，供审计与迁入 Playbooks 时参考。扩展名刻意保留为文本，Knowledge 不提供新的生产执行入口。源码不包含凭据值、备份实物、Terraform state、实际用户行或完整 Docker inspect。

| 文件 | 用途 |
| --- | --- |
| [capture.py.txt](capture.py.txt) | 控制机读取 Vault 密钥，通过已验证 SSH 通道向远端 stdin 传递；保存脱敏 receipt |
| [capture_remote.py.txt](capture_remote.py.txt) | 固定 V3 主机预检、导出 PostgreSQL 一致性快照、全库加密 dump、表行指纹、配置归档、独立容器恢复与比对 |
| [capture_vault.py.txt](capture_vault.py.txt) | 原生 Raft 快照、加密、解密回读及 inspect；清理本轮临时原生快照 |
| [finalize.py.txt](finalize.py.txt) | 只输出 KV 路径/键名、组装远端归档、加密 Docker inspect、检查业务容器未重启、生成并核验 SHA256SUMS |
| [fetch_archive.py.txt](fetch_archive.py.txt) | 拉取仅含密文及脱敏元数据的外层 tar，在维护端逐成员验证 checksum |

## 已知限制与移交要求

- 代码含本次 V3 的主机、SSH 身份别名、路径和 schema；`capture.py` 同目录加载 `capture_remote.py`。直接重命名执行可能触发真实维护操作，必须经 Playbooks 参数化、目标身份与数据盘核验后使用。
- 维护过程未暂停业务。DB 表行与 dump 共用一个导出的 MVCC 快照；序列值不是 MVCC 行指纹的一部分。
- 恢复只验证源表行指纹、schema 版本/dirty 与业务计数；不宣称已经逐项验证所有 DDL、序列、角色口令、ACL、扩展依赖或跨机业务启动。globals 单独加密归档，隔离恢复使用 `--no-owner --no-acl`。
- 隔离容器无网络、无宿主机端口、无生产挂载，使用 tmpfs；恢复成功才删除本轮专属容器，失败保留供排查。代码尚未实现完整恢复清单/清理重入协议。
- Vault 备份和 DB 不是同一原子时间边界；独立 Vault 实例 restore/unseal 没有执行。
- 外层 tar 不额外加密，内部敏感内容分别加密；路径/键名和 manifest 仍要按维护元数据保护。
- 首次执行的快照目录与产物不会覆盖，但本地后处理脚本还未统一实现不可覆盖、并发锁、签名证据、容量门禁和安全重跑；不能宣称是通用生产工具。
- 运行参数、日志和失败异常需要在 Role 中统一脱敏；使用 Vault key 作为内存输入，禁止把 key 放入 argv、仓库、receipt 或 PR。
- `capture_vault.py` 保留了一条不会执行的历史表达式，作为原始源码归档；正式 owner 实现应去掉这类维护残留。

正式迁入位置应为 Playbooks 的数据库/冷恢复 Role；Knowledge 只通过固定 commit 引用该入口，避免维护双份执行逻辑。此归档没有重新执行源码，也没有创建新快照、修改 DNS 或部署服务。

完整证据见[快照与升级复盘](../../records/prod-v2-v3-20261019/20261019-prod-v2-v3-snapshot-and-upgrade-retrospective.zh.md)。
