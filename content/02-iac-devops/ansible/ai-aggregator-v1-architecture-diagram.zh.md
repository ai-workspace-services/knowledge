# AI Gateway v1 架构图

> 本图是 AI Gateway v1 的拓扑事实源。CPA 节点必须通过 `AI Desktop Role`
> 部署桌面基线，再装配 Agent Runtime、基础监控和一个账号对应的 CPA 实例。

## 运行时拓扑

```mermaid
flowchart LR
    client[Claude Code / Codex CLI / Android Studio / SDK / Web SaaS]
    dns[ai.*\n direct.ai.*]
    caddy[Caddy :443\nTLS + IP 白名单]
    kong[Kong :8000\nJWT/Key Auth\nTenant ACL\nRate Limit\nHost Route\nAudit Metadata]
    newapi[New API :3000\n模型别名\nCPA Channel\nAccount Health]
    litellm[LiteLLM :4000\n官方 API 聚合\nRetry + Usage/Cost]
    pg[(PostgreSQL\nKong / New API / LiteLLM 独立 DB)]
    vault[(Vault\nDB + Gateway + Provider API Key\n不保存 CPA OAuth)]
    desktop1[AI Desktop Node\nCPA Codex-01 + CodeAgent\n2C2G / 2C4G]
    desktop2[AI Desktop Node\nCPA Codex-02 + CodeAgent\n2C2G / 2C4G]
    desktop3[AI Desktop Node\nCPA Claude-01 + CodeAgent\n2C2G / 2C4G]
    desktop4[AI Desktop Node\nCPA Grok-01 + CodeAgent\n2C2G / 2C4G]
    upstream1[OpenAI / Codex\n单账号 OAuth]
    upstream2[Anthropic / Claude\n单账号 OAuth]
    upstream3[xAI / Grok\n单账号 OAuth 或 API]
    desktoprole[AI Desktop Role\nXFCE/XRDP + Agent Runtime\nnode_exporter]

    client --> dns --> caddy --> kong
    kong -->|Host ai.*| newapi
    kong -->|Host direct.ai.*| litellm
    newapi -->|私网 / CPA Channel| desktop1
    newapi -->|私网 / CPA Channel| desktop2
    newapi -->|私网 / CPA Channel| desktop3
    newapi -->|私网 / CPA Channel| desktop4
    desktop1 --> upstream1
    desktop2 --> upstream1
    desktop3 --> upstream2
    desktop4 --> upstream3
    litellm --> upstream1
    litellm --> upstream2
    litellm --> upstream3
    kong --- pg
    newapi --- pg
    litellm --- pg
    vault -.运行时注入.-> kong
    vault -.运行时注入.-> newapi
    vault -.运行时注入.-> litellm
    desktoprole -.部署基线.-> desktop1
    desktoprole -.部署基线.-> desktop2
    desktoprole -.部署基线.-> desktop3
    desktoprole -.部署基线.-> desktop4

    classDef public fill:#fff3cd,stroke:#b7791f,color:#111;
    classDef control fill:#e8f0fe,stroke:#4772c2,color:#111;
    classDef private fill:#e6ffed,stroke:#2f855a,color:#111;
    classDef secret fill:#fde8e8,stroke:#c53030,color:#111;
    class client,dns,caddy public;
    class kong,newapi,litellm,pg control;
    class desktop1,desktop2,desktop3,desktop4,upstream1,upstream2,upstream3,desktoprole private;
    class vault secret;
```

## 边界与部署模型

- 公网只开放 Caddy `:443`；Caddy 负责 TLS 和物理源 IP 白名单。
- Kong 只监听 loopback，负责 Token、租户 ACL、限流、Host 路由和审计元数据；使用 PostgreSQL，不部署 etcd。
- `ai.<domain>` 进入 New API，再按 CPA channel 访问私网 CPA；`direct.ai.<domain>` 进入 LiteLLM，直连官方 OpenAI、Anthropic、xAI API。
- CPA 每个实例只绑定一个账号；OAuth bundle 仅位于该节点的加密本地 `auth/` 目录，不进入 Vault、Git、Terraform state 或 CI artifact。
- CPA 节点由 `deploy_ai_desktop.yml -e ai_desktop_cpa_codeagent=true` 调用现有 `roles/vhosts/ai_desktop`，并启用 `roles/ai_agent_runtime` 与 `roles/vhosts/node_exporter`。
- UAT 是 AWS ARM64 Spot、默认 60 分钟；Prod 复用现有持久节点。每个 CPA 节点最低 2C2G，建议 2C4G。

## 交付顺序

```text
GitOps 声明
  → Terraform/CMDB 生成节点
  → deploy_ai_desktop.yml(cpa_codeagent) + AI Desktop Role + Agent Runtime + node_exporter
  → CPA 本地 auth 目录初始化
  → Gateway Vault 凭据注入
  → Kong / CPA / LiteLLM / New API stage
  → 人工完成 4 个 CPA OAuth 登录
  → 协议、租户、故障隔离验证
  → activate
```
