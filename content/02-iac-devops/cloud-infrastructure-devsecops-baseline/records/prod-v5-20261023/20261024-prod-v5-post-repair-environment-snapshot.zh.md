# PROD V5 修复后环境快照与恢复验证

采样日期：2026-10-24，Asia/Shanghai。run_id：`20261024031956`。这是在线 V5 的逻辑环境快照，未停止服务、修改 DNS、操作 V4 或改变写入权。原始配置、数据库、角色与证据只保留在受控位置，本文只记录脱敏回执。

[统一流程白皮书](https://github.com/ai-workspace-services/.github/blob/main/docs/control-plane-deployment-and-migration.zh.md) → [V4→V5 复盘索引](../../17-prod-v4-v5-baseline-and-upgrade-retrospective.zh.md) → [V5 运行基线](prod-v5-runtime-and-snapshot-baseline-20261023.zh.md) → [业务追加与流量重验](20261024-prod-v5-business-append-and-traffic-regression.zh.md) → 本快照。[部署流程复盘](prod-v5-deployment-postmortem-20261023.zh.md)提供故障与改进关联。

## 执行回执

| 阶段 | 北京时间 | 结果与证据 |
| --- | --- | --- |
| 在线捕获 | 2026-10-24 11:19:56–2026-10-24 11:20:50 | 现有 Playbooks `web_saas_data_backup` full-database/root profile；76 张 public 业务表在同一 exported MVCC 边界下计算行摘要并导出；exit 0 |
| 独立数据库恢复 | 2026-10-24 11:21:16–2026-10-24 11:21:27 | 使用与现场 PostgreSQL 相同 image ID；独立容器无网络、无端口、无业务挂载，数据位于临时内存文件系统；完整恢复 exit 0，数据库恢复及核验 11.13 秒 |
| 异机副本验证 | 2026-10-24 11:21:57 完成 | 全文件 SHA-256 一致；操作员既有密钥解开 age 密钥信封；异机解密归档并读取 pg_restore 目录成功，exit 0。异机仅验证可读性，不冒称第二次完整数据库恢复 |
| 运行保护 | 覆盖捕获及恢复窗口 | 9 个常驻容器镜像、启动时间、重启计数均与捕获前一致；非业务验证容器在成功回执持久化后删除；业务重启 0 |

数据库 schema 版本 `2026102002`，dirty=false。Playbooks owner 固定为 `fa8458c2b5bdbd51b1d2b05cb340f1dab01f70eb`；GitOps 部署引用 `ed6a5d0cd2e50dbd5cf35abff5cd019a8ec001b8`。服务仍为 r101 协调基线加 Portal r106 维护构件，不把迁移 CLI r106 当作 Accounts 服务版本。所有实际容器引用保存在受控 manifest，前一回执记录公开发布来源。

## 恢复后的业务样本

| 对象 | 恢复数量 |
| --- | ---: |
| 用户 | 33 |
| 套餐目录 | 18 |
| 账户计费配置 / 额度状态 | 33 / 33 |
| 订阅 / 订阅记录 | 7 / 13 |
| 策略快照 | 0（源端本就没有，不编造） |
| 流量分钟桶 / 账本 | 76,131 / 76,133 |
| public 业务表 | 76 |

全表所有字段及序列状态的组合摘要一致，不只比较行数。schema 摘要保留对象所有权、ACL 与默认授权。隔离恢复使用无登录凭据的角色占位身份，因此没有验证生产密码、角色登录属性、应用连库或完整身份恢复；原始 globals 已单独加密保留供受控恢复。

## 快照清单及完整性

| 组件 | 状态 | 边界 |
| --- | --- | --- |
| 活跃 account 完整数据库 | CREATED / RESTORE_PASS | 保留 schema、所有表数据、序列、所有权和权限；不包含旧 scratch 数据库 |
| PostgreSQL globals | CREATED / DECRYPT_PASS | 角色与全局授权信息加密保存；未将生产角色密码载入验证容器 |
| 主机配置、TLS、SSH、部署控制器配置 | CREATED / DECRYPT_PASS | 加密配置归档 93 个条目，目录可读；未在生产主机覆盖恢复配置 |
| 完整容器元数据 | CREATED / DECRYPT_PASS | 加密保存环境与挂载元数据，公开文档不输出环境秘密 |
| 固定镜像引用与运行状态 | RECORDED | 不归档 registry 镜像层；重建仍需获得对应不可变构件 |
| 异机副本、密钥信封 | VERIFIED | 副本密文逐项校验；解密能力依赖操作员既有密钥，私钥不复制到目标机 |
| 云磁盘镜像、共享 Vault、原始 Terraform state | NOT_RUN / OUT_OF_SCOPE | 本次不是整机镜像、共享 Vault restore/unseal 或资源 state 恢复演练 |

| 校验项 | SHA-256 |
| --- | --- |
| 数据库加密归档 | `26d7e2dc60654c8d2b41a3190e987fffb32a4a6039cae10b56b3e95c711d90d4` |
| schema（含所有权/权限） | `38284258697ca86a7f6577295561fd2d72b496f2a9b3adcc61c56d742f9c6945` |
| 全行与序列 | `0565da02c95384a90c078f5ef40538308a9445b4b604a32e558e3c13ce519296` |
| 完整文件校验清单 | `0b26409282819be37166484a7b8d06db4865cf89139ce2ea1999236574a12808` |

数据库归档约 4,581,392 字节。主机同机快照使用已声明的 root storage profile，系统盘故障不能依赖同机副本，故另有已校验的异机加密副本。原始快照、密钥信封及恢复证据不删除；本次未新增自动过期或删除策略。

数据库是一个 MVCC 一致性边界；globals、运行配置和元数据分别采样，并非跨所有组件的全局原子快照。采样后的在线新写入不包含在此恢复点。11.13 秒只衡量本次数据库恢复/核验，**不作为整代环境 RTO**；备份调度频率、业务 RPO 目标与整机恢复演练未由本次测定。

## 证据索引及结论

受控证据按 run_id 关联：捕获命令回执、数据库组件回执、encrypted account/globals/config/container 归档、固定构件 manifest、恢复角色名称元数据、捕获前进程指纹、`restore-verification`、`SHA256SUMS`、异机复核回执及 age 密钥信封。捕获组件的自检字段不替代独立恢复结论，以恢复及异机回执为准。

**PASS：V5 修复后有业务数据的逻辑环境快照、独立数据库恢复与异机副本校验。** 不推导 OAuth/MFA 重登录、支付、所有代理正流量、完整权限登录恢复、云磁盘恢复、最终追齐或写入权切换通过。V4 继续在线，源端与目标的持续增量不是靠此静态快照自动保持同步。
