# web-saas 代际快照与恢复证据模板

版本：YYYY-MM-DD

适用范围：`prod-vN` → `prod-vN+1`、冷备、隔离恢复、滚动升级
安全边界：只记录非敏感事实；不记录密码、Token、私钥、DSN、完整用户标识、备份内容或 unseal/recovery key。

本模板是[既有统一流程](https://github.com/ai-workspace-services/.github/blob/main/docs/control-plane-deployment-and-migration.zh.md)的记录附件；[跨代回执与 case 索引](../generation-deployment-evidence-index-20261025.zh.md)提供实例。每轮复制为独立记录，原失败/原时间保留。历史未取得字段用 `NOT_RECORDED`；依赖该证据的准出为 `BLOCKED`。未执行阶段为 `NOT_RUN`，不适用的 checksum 须写 `N/A` 及原因。

## 1. 变更身份

| 字段 | 值 |
| --- | --- |
| run_id / attempt / 父运行 | `<unique-run-id>` / `<attempt>` / `<parent-or-N/A>`；本地运行不伪装成 Actions URL |
| 环境、操作范围及授权依据 | `<environment>` / `<read-only-or-approved-action>` / `<issue-or-approval>` |
| Asia/Shanghai 起止 | `<YYYY-MM-DDTHH:mm:ss+08:00>` → `<YYYY-MM-DDTHH:mm:ss+08:00>` |
| 源代际 | `prod-vN` |
| 目标代际 | `prod-vN+1` |
| 源主机 | `<source-host>` |
| 目标主机 | `<target-host>` |
| Provider / 账号 / 区域 | `<provider>` / `<logical-account>` / `<region>`；真实资源及 state 身份仅在受控证据绑定 |
| 快照边界（北京时间） | `<timestamp>` |
| release tag | `<immutable-release-tag>` |
| GitOps commit | `<full-sha>` |
| Playbooks/Role commit | `<full-sha>` |
| 工具 commit | `<tool-sha>` |
| 工具/镜像 digest | `<sha256>` |
| Chart / OCI digest | `<immutable-chart-version>` / `<sha256-or-N/A-reason>` |
| schema checkpoint / native checksum | `<version / dirty>` / `<sha256-or-NOT_RECORDED>` |
| SQL / migration package checksum | `<sha256>` 或 `N/A（本轮无 DDL/迁移包）`，不可混用旧候选摘要 |
| IaC / installer / 其他 owner commit | `<each-owner-full-sha>`；固定版本缺失则阻断相应操作 |
| 阶段 / 状态 / 退出码 | `<phase>` / `PASS/FAIL/BLOCKED/NOT_RUN` / `<integer-or-null>` |
| 原因 / 修复 PR / case / 重验 | `<reason>` / `<PR-URL>` / `<fixed-code-case>` / `<new-run-evidence-id>` |
| 受控证据索引 / 归档 PR | `<evidence-id>` / `<archive-PR-URL>`；原件继续受控保留 |

## 2. 源主机只读基线

- 源主机仍服务；未安装、写文件、停服务或重启。
- PostgreSQL 实际挂载：`<mount>`；以 `docker inspect` 为准。
- schema/迁移版本：`<version>`，dirty：`<false|true>`。
- 用户数：`<count>`；订阅数：`<count>`；配额/流量/账务计数：`<count>`。
- 业务数据指纹：`<sha256>`；指纹算法和排除的内部审计表：`<description>`。
- 公共 DNS：`<unchanged|changed with explicit approval>`。

## 3. 快照与恢复证据

| 项目 | 记录 |
| --- | --- |
| 源快照目录 | `<absolute path>` |
| DB archive | `<filename>`，未加密/已加密：`<state>` |
| DB archive SHA-256 | `<sha256>` |
| globals/roles SHA-256 | `<sha256>` |
| Vault 快照路径 | `<path>`，只记录路径，不记录值 |
| Vault 快照 SHA-256 | `<sha256>` |
| Vault inspect | `PASS/FAIL` |
| 目标隔离恢复 | `PASS/FAIL` |
| 恢复 schema/版本 | `<version>` |
| 恢复后数据指纹 | `<sha256>` |
| 备份/恢复 receipt | `<protected path>` |

隔离恢复必须使用独立数据库/网络，不挂载生产数据盘、不绑定生产端口、不覆盖目标业务库。失败时保留候选库、旧库和检查点，不自动删除或执行 down migration。

## 4. 迁移与滚动升级

1. 目标代际先独立备份并通过隔离恢复。
2. 源代际只读导出并记录时间边界、计数和指纹。
3. 只执行审核过的向前兼容迁移，逐段记录 SQL checksum、前后版本和 dirty 状态。
4. 对用户、身份、订阅、配额、用量和财务数据做只读差异预览；身份或财务冲突立即停止。
5. 验证固定镜像、实际数据库连接、公共 SNI 证书 SAN、路由、OAuth/Webhook 和健康检查。
6. 明确单写入者门禁后，才允许写入权和 DNS 变更；源代际保留为只读回退候选。
7. 稳定验收后，目标代际才成为下一轮来源。

## 5. 验收结果

| 阶段 | 状态 | run_id/attempt、起止、exit code 与受控证据 |
| --- | --- | --- |
| 构建 / 不可变构件发布 | NOT_RUN | `<fields>` |
| 主机 / 服务部署 | NOT_RUN | `<fields>` |
| 数据迁移与对账 | NOT_RUN | `<fields>` |
| 独立恢复与权限登录 | NOT_RUN | `<fields>` |
| 真实业务 / 节点 / 遥测验收 | NOT_RUN | `<fields>` |
| DNS / 流量 / 写入权交接 | NOT_RUN | `<separate-authorization-and-receipts>` |

每一轮重跑和每次失败各占独立行；不得把恢复、数据追加 no-op、Flux 协调的成功次数混为完整重建三轮。以下逐项结果仍需对应本轮受控证据。

- 数据：用户/订阅/配额/用量/账务指纹 `PASS/FAIL`。
- schema：`PASS/FAIL`。
- Accounts/Billing `/readyz`：`PASS/FAIL`。
- Console 页面与路由：`PASS/FAIL`。
- 公共 SNI/证书：`PASS/FAIL`。
- Doco-CD 对账的 target/tag/commit：`PASS/FAIL`。
- 原密码登录、终端代理连接、真实支付/退款：分别记录，不能用探针替代。
- 回退 digest：`<immutable digest>`。

## 6. 门禁与未完成项

记录任何未完成项及其阻断原因。没有实际生成的快照不得填写 SHA-256 或 `PASS`；阶段性迁移备份不得冒充全量快照。所有凭据只在 OIDC/Vault 运行时读取。
