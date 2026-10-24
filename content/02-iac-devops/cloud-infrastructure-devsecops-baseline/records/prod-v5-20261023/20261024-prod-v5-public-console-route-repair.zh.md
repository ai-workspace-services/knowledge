# V5 公共 Console 白屏：路由遗漏与修复回执

日期：2026-10-24，Asia/Shanghai。本文承接 [V5 基线](prod-v5-runtime-and-snapshot-baseline-20261023.zh.md)、[业务及流量回执](20261024-prod-v5-business-append-and-traffic-regression.zh.md)和[修复后快照](20261024-prod-v5-post-repair-environment-snapshot.zh.md)，保留先前结果的时间与范围，不将 DNS 校验改写为业务访问成功。

## 根因与现场证据

公共 Console DNS 已指向 V5，但实际 Caddy site 和 Console host matcher 只有候选专属域名，缺少公共别名。公共首页及登录页都返回 HTTP 200、响应体 0 字节；专属域名对应页面分别返回 78,724 与 30,891 字节的 HTML。浏览器白屏来自入口未匹配，不能归为浏览器缓存，也不能由 CNAME 正确推导入口通过。

先验证最小配置并保存原配置，再将公共 Console 别名同时加入 site 和 matcher，仅重启 Caddy。公共首页、登录 HTML 恢复，三个前端脚本资源均非空 HTTP 200；浏览器实际显示首页及登录页，已有登录会话也能被识别。不存在的合成身份登录请求返回结构化 `user_not_found`，仅证明认证 BFF 路由正常，不计作真实凭据/MFA 重登录验收。

## 持久修复与防回归

[Playbooks #746](https://github.com/ai-workspace-infra/playbooks/pull/746) 为 `target.console_public_domain` 提供显式合同，校验本域名基座及服务之间的冲突，并传递到已有 alias-aware Caddy 模板。HTTPS readiness 对 Console 要求真实 HTML，并验证公共首页与登录页；空 HTTP 200 必须失败。`tests/control_plane/test_owner.py` 覆盖无效别名、实际 Ansible 渲染、空 200 拒绝及公共域名探测；本地 52 tests / 2 optional skips 通过。

[GitOps #521](https://github.com/ai-workspace-infra/gitops/pull/521) 已合并为 `01461922e2c91da946c68626d88d5ffc9472d3a7`，固定 Playbooks owner `a675ce0bd049834c4668b36bba10fa2b80871dbc`，声明 Console 公共别名；两仓适用 CI 检查均通过。

| 阶段 | 2026-10-24 北京时间 | 结果 |
| --- | --- | --- |
| 规范模板应用 | 12:17:12 完成 | 使用声明输入渲染已合并 owner 模板，并用运行中 Caddy 镜像先验证后应用；仅 Caddy 重启 |
| 相同模板重放 | 12:17:13 完成 | changed=false、caddy_restart=false；配置 SHA-256 `471178a53d28c384b2d393c8224ad33b245f4a09f1c4eb54a55e4582bb32c90a` |
| 固定 GitOps 选择 | 12:17:14–12:17:21 | Doco-CD 选择新 commit；配置校验通过，仅控制器重建；Accounts/Billing/Console/PostgreSQL 镜像与启动时间保持原值 |
| 选择重放 | 12:17:45–12:17:49 | changed=0，无额外重建 |
| 最终可信 HTTPS/SNI | 12:18:32 完成 | 公共/候选 Console 的首页、登录页均为实际 HTML；公共 Accounts/Billing readiness 均 200；6 项通过 |

浏览器首页与登录页实际呈现已核对。受控证据保存规范配置两次应用、控制器两次选择、SNI 探测、恢复后截图及 DNS 回读；公开不存 Cookie、身份明细或实际主机地址。

## 与快照和其他入口的边界

11:19–11:21 的逻辑快照是本次路由修复之前的恢复点，恢复证明仍有效；恢复后须使用包含公共 Console 别名的最新固定 owner/声明收敛，不把旧 Caddy 配置当作最终入口。

本次不修改 DNS、数据库、V4 或代理服务。同期只读检查发现公共 PostgreSQL 别名仍指向旧代际，不能沿用“所有四个公共别名均已指向 V5”的描述；本次未切换数据库入口。代理节点的最新心跳、DNS 和健康状态按其采样时间分别核对，不由 Console 页面恢复推导全节点健康。
