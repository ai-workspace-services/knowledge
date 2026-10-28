# 01｜新增素材、核验与后续拆题

状态：2026-10-28 用户提供的实践叙述，**待独立核验**；不可直接作为已完成结果发布。公众号和 XHS 以各自正文为准。

## 字数与版式校验

以各文件正文区（第二个 `---` 后至文末导航分隔线前）为范围，去掉空白后按 Unicode 字符计数；保守计入标题、Markdown 标记和 XHS 标签。当前公众号 1204 字符、4 个正文段落及 1 张决策表；XHS 746 字符、8 页。平台的字数统计方式可能不同，正式发布前按平台再核对。

## 素材分流

| 素材 | 首篇处理 | 后续归属与待核验 |
| --- | --- | --- |
| K3s PROD/SIT、Cloud Run、Cloudflare、PostgreSQL 与 Grafana | 只介绍多云背景、UAT 小范围方案 | 核验实际环境、信号来源及公开授权；不要把 Supabase 与 K3s 的 PostgreSQL 当成同一数据库 |
| Vault、ESO、Flux、Playbook、AI | 介绍拟采用的职责边界，不宣称全流程已运行 | 查 PR、不可变 digest、Flux 对账记录、ESO 的密钥引用与有效权限；不存在证据时写计划 |
| PostgreSQL 独立 exporter 与 restricted:v1.37 | 不展开，留给数据库/安全采集 case（2027 储备或季度可替换提案） | 检查实际 K8s 版本与 Pod Security 标签、exporter 及只读监控账号；对比数据库 Pod UID、重启次数与观测时间，不能由使用独立 Deployment 推出业务零抖动；不得展示连接凭据 |
| 多集群 election pause 和 `election=false` | 不展开，作为候选踩坑案例 | 获取 DataKit/Chart 版本、各集群 namespace、配置、脱敏日志、选举后端、重复采集/数据缺失对照。官方 Helm 与 DaemonSet 开关默认不同，不能泛称所有 prom 场景默认开启；只禁用选举可能重复采集，需验证实例拓扑及标签。见 [DataKit Kubernetes](https://docs.guance.com/datakit/datakit-daemonset-deploy/)、[Helm](https://docs.guance.com/datakit/datakit-helm/)、[Prom 采集器](https://docs.guance.com/integrations/prom/) |
| Cloud Run 直发 OTLP、Cloudflare Logpush 直发 DataWay | 分别预留 #04 跨云 Trace 与后续边缘日志专题 | 测试接收端协议、路径、认证、重试/限流、敏感字段与链路；Cloudflare 的套餐、数据集与目标兼容性待核验。HTTP 目标支持不等于 DataWay 已接受该格式。OTLP headers 在运行时需受保护；不把 Vault 注入等同凭据永不暴露 |
| 100+ 指标、`pg_up=1`、12.15 MB、零重启、完整链路及“秒级” | 均不作为当前实测结果 | 查时间戳、环境、查询结果、Pod 事件、覆盖范围、延迟分布；核验后再决定可公开数字 |

## 发布前证据包

1. 免费专区工作空间类型、地区、套餐和实际权益；如用于商业项目，取得并存档明确的书面授权。没有授权时改用合规非商业实验或获授权空间。
2. 被测服务、版本、环境、配置 PR、数据来源与一次受控验证；记录原有采集未受影响及可回退证据。用户数据、域名细节、token、日志和账号信息脱敏。
3. AI 的具体输入输出、人工审核记录；不能将 Git、Vault、Flux、ESO 或 Terraform 的设计预设为已交付。
4. 7 天内每日用量、计费与人工耗时；未达到 7 天如实报告实际观察期。区分零新增采购费、其他云费用和总拥有成本。
5. 发布前重新核对[套餐](https://docs.guance.com/plans/differences/)、[免费协议](https://docs.guance.com/agreements/free-agreement/)及[注册说明](https://docs.guance.com/plans/free/)，标注核验日期和合作关系。

## 第一篇与第二篇边界

第一篇解决“为何补充 SaaS、如何低风险开始”；第二篇专注 Grafana 面板、指标语义与回退，不塞入 PostgreSQL 采集和边缘直连细节。其余材料优先映射到既有季度主题，或作为未签约储备；不能隐含新增合同交付。

---

专题导航：[公众号初稿](./wechat-draft.md) · [XHS 初稿](./xhs-draft.md) · [文章大纲](./outline.md) · [季度选题](../../series-v4/quarterly-plan.md) · [专题总索引](../../series-v4/index.md)
