# 品牌域补齐 V4：DNS 变更回执

时间：2026-10-21 03:27（Asia/Shanghai）。用户在运行基线盘点后明确要求将 `xworktech.com` 和 `www.xworktech.com` 对齐 V4。

## 范围与依据

- 仅变更 Cloudflare `xworktech.com` zone 的根域与 www 两条既有 A 记录，V3 → V4。
- 使用已合并 GitOps `prod-v4-dns-handoff.yaml` 的品牌域声明；主机地址以已核实的 GCP 主机身份解析。
- 执行 owner：IaC Modules `scripts/pipeline/cloudflare-record-switch.py`，固定 commit `daf5bb919424c691d5fd08aead5b8d1b171900be`；脚本 SHA-256 `aeaa972150bedb3101f12cb7dfe97a5d4feb1ab627bc2c82893b5e55eddbd159`。
- 先完成 V4 五公共 SNI/证书/路由预检，再执行 provider 只读预览与精确变更。无 CI 部署。
- 原记录均为 DNS-only A；保留原类型、代理标记及 TTL（根域 60，www 的 provider 自动值 1）。没有顺便改成 CNAME、打开代理或改其他记录。

## 执行与验证

计划 SHA-256：`df40e4338a7184b7f2ef0777c0384a6253c437a511f9293999f8e91851cb8115`。

1. 预览返回 `status=preview`、record_count=2，源记录与预期 V3 一致。
2. 首次 apply 在 provider 读取阶段发生连接断开，未进入写入；保留错误，使用同一计划/检查点安全重试。
3. 重试返回 `status=provider-verified`、record_count=2；两条记录回读等于 V4 目标。
4. Cloudflare 两个权威 NS、1.1.1.1 和 8.8.8.8 均解析到 V4。
5. 实际公网请求的 remote_ip 为 V4：根域 HTTPS 200；www 返回 301，`/panel?from=dns-check` 路径和 query 保留到根域。
6. 03:27:26 与 03:28:26 两次公网采样均到 V4，根域 200、www 301；覆盖根域原 60 秒 TTL。此为短期 DNS/HTTP 验证，不是全业务稳定观察完成。

## 边界与恢复

受保护检查点保留两条原 provider payload 及变更意图，用于另行审查的精确恢复。本次没有修改 V3 容器、业务库、数据、后台开关或写入权。服务三域原已指向 V4，本次是品牌域遗漏补齐；不把这项成功扩展为整轮升级验收。

旧 TTL 缓存期间可能仍有客户端访问 V3。此窗口不代表允许两代同时承接业务写入；单写入者证据仍需独立核实。V4 已有新业务数据，不能自动以 DNS 回退代替数据库恢复。

关联：[运行基线](prod-v4-runtime-and-snapshot-baseline-20261021.zh.md)、[V4-18 问题台账](v3-v4-upgrade-retrospective-20261021.zh.md)、[旧 V2→V3 事件索引](../../15-prod-v2-v3-snapshots-and-upgrade-retrospective.zh.md)。

## 跨代归档回链

[统一流程](https://github.com/ai-workspace-services/.github/blob/main/docs/control-plane-deployment-and-migration.zh.md) → [跨代基线、逐轮回执、真实 case 与重验](../generation-deployment-evidence-index-20261025.zh.md)。本页保留原采样、固定构件和结果；后续成功不覆盖历史失败，源码/PR 状态不代替本页的真实运行回执。
