# 全能 AI 聚合网关实战系列（中英双语 · 多平台兼容版）
# All-in-One AI Aggregator Gateway Series (Bilingual & Multi-Platform Ready)

> **系列主旨**：面向个人与小团队，手把手教你搭建高可用、双层安全防线、多账号隔离的私有 AI 聚合网关，告别碎片化 Token 与多账号频繁切换的困扰。
> 
> 本系列所有文章均已完成 **首页配图** 与 **微信公众号、小红书、X (Twitter)、LinkedIn** 等社交媒体发布矩阵的多渠道分发适配。

---

## 📚 文章索引与配图全览 / Series Index & Cover Gallery

| 篇章 / Part | 工程决策画布 / Decision Canvas | 中文版 / Chinese | 英文版 / English | 核心要点 / Highlights |
| :---: | :---: | :--- | :--- | :--- |
| **01 选型篇** | ![选型画布](/assets/images/gateway-canvas-01-selection.png) | [选型篇：Kong vs APISIX 深度抉择](./01-selection-kong-vs-apisix.zh.md) | [Part 1: Technology Selection](./01-selection-kong-vs-apisix.en.md) | 告别多账号割裂；APISIX Standalone GitOps 极简对账优势与无 DB 架构权衡。 |
| **02 架构篇** | ![架构画布](/assets/images/gateway-canvas-02-architecture.png) | [架构篇：双层分流与安全契约](./02-architecture-and-traffic-routing.zh.md) | [Part 2: Architecture & Routing](./02-architecture-and-traffic-routing.en.md) | Caddy TLS 卸载 + APISIX 流量中枢；“单一网关 Token”无感解耦置换契约；Real-IP 信任链。 |
| **03 凭据篇** | ![凭据画布](/assets/images/gateway-canvas-03-credentials.png) | [凭据篇：CPA 矩阵与 Vault 注入](./03-cpa-matrix-and-vault-credentials.zh.md) | [Part 3: Credentials & Matrix](./03-cpa-matrix-and-vault-credentials.en.md) | CPA 单账号物理隔离防封号矩阵；0700 本地存储铁律；无头服务器 SSH 隧道 OAuth 回调；Vault tmpfs 内存化注入。 |
| **04 实战篇** | ![实战画布](/assets/images/gateway-canvas-04-integration.png) | [实战篇：客户端接入与 GitOps 交付](./04-client-integration-and-gitops.zh.md) | [Part 4: Integration & GitOps](./04-client-integration-and-gitops.en.md) | 环境变量安全注入；OpenAI SDK、Responses 新协议、流式输出与 Claude Code 原生接入；Ansible 编排流水线。 |
| **05 排障篇** | ![排障画布](/assets/images/gateway-canvas-05-troubleshooting.png) | [排障篇：真实推理避坑与运维复盘](./05-inference-troubleshooting-and-ops.zh.md) | [Part 5: Operations & Troubleshooting](./05-inference-troubleshooting-and-ops.en.md) | 四大可用性状态绝不等价；504 链路超时、403 风控阻断、连接异常排查；轻量级自动化探活脚本。 |

---

## 🚀 系列进阶应用案例 / Continuation Case Study

作为 AI 聚合网关底层“凭据中枢（Vault）”与“安全网络（XConnect）”的深度延展，本篇应用案例深度复盘了底层 Vault 集群如何在零信任私网保护下平滑跨云迁移：

* **中文版**：[《自建零信任网络应用案例：告别裸奔，XConnect + AI Agent 协同 生产级 Vault Server 跨云迁移实战》](../2026-10-01-xconnect-zero-trust-vault-migration.zh.md)
* **English**：[Self-Hosted Zero-Trust Network in Action: Production-Grade Vault Server Multi-Cloud Migration](../2026-10-01-xconnect-zero-trust-vault-migration.en.md)

---

## 📱 多平台发布套件说明 / Multi-Platform Adaptation Suite

每篇文章文末均已完整内置专属的社交平台分发物料，开箱即用：

1. **微信公众号 & 朋友圈**：
   * 包含强悬念爆款标题备选、推文摘要与黄金前三屏痛点导语；
   * 提供适合技术极客朋友圈与社群转发的观点型短文案。
2. **小红书 (XHS)**：
   * 提取痛点强烈的图文双列封面大字；
   * 碎碎念风格干货拆解、易于阅读的 Emoji 视觉断句；
   * 预置精准的行业流量标签（#AI工具 #大模型开发 #HomeLab #程序员生产力 等）。
3. **X (Twitter) & LinkedIn**：
   * 英文/中英双语技术 Thread（包含 Hook、架构痛点、核心选型原因与技术边界）；
   * 面向国际化技术社区的 LinkedIn 架构长文与 Hacker News / Reddit 极客简报。

---

## 🔗 相关工程参考与基础设施文档

* 架构总体规范：[`content/04-infra-platform/apisix/ai-aggregator-gateway-architecture.zh.md`](../../../04-infra-platform/apisix/ai-aggregator-gateway-architecture.zh.md)
* 客户端对接与验证 TLDR：[`content/04-infra-platform/apisix/ai-aggregator-client-acceptance-tldr.zh.md`](../../../04-infra-platform/apisix/ai-aggregator-client-acceptance-tldr.zh.md)
* CPA 人工 OAuth 登录 TLDR：[`content/04-infra-platform/apisix/ai-aggregator-cpa-oauth-tldr.zh.md`](../../../04-infra-platform/apisix/ai-aggregator-cpa-oauth-tldr.zh.md)
* 自动化探活脚本：[`scripts/ai-gateway-internal-verify.sh`](../../../../scripts/ai-gateway-internal-verify.sh)
