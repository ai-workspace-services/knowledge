---
hero:
  badge: '开源解决方案'
  title: 'Open-platform'
  subtitle: '涵盖 IAC、DevOps、安全、IAM 以及全局可观测性的平台解决方案。'
  cta:
    label: '了解更多'
    href: '/panel'
wizard:
  title: '3 步构建云原生开放底座'
  description: '以基础设施即代码（IaC）方式快速部署可信、可控的企业级平台。'
  steps:
    - step: 1
      title: '初始化基础组件'
      description: '一键拉起 Gitea、Vault、Zitadel 与 APISIX 核心控制面。'
      link: '/panel'
    - step: 2
      title: '配置安全与权限策略'
      description: '开箱即用的零信任鉴权与自动化 Secret / ACME 证书轮转。'
    - step: 3
      title: '声明式交付工作流'
      description: '基于 GitOps 理念实现环境清单版本化与自动化部署。'
showcases:
  - title: '统一开放控制面'
    description: '集成 Gitea, Vault, Zitadel 等开源基础设施，为您提供一站式的企业级控制平面。'
    icon: 'layers'
    image: '/marketing/Open-Platform/unified-open-control-plane.png'
  - title: '安全交付生命周期'
    description: '从代码提交到生产部署，每一步都内置安全审计和策略合规，确保研发流程无懈可击。'
    icon: 'shield-check'
    image: '/marketing/Open-Platform/secure-delivery-lifecycle.png'
    reverse: true
  - title: '可信基础设施'
    description: '以基础设施即代码 (IaC) 的形式管理所有资源，实现版本化、可追溯和可复制的云原生底座。'
    icon: 'lock'
    image: '/marketing/Open-Platform/four-trusted-foundations.png'
solutions:
  - title: '多云架构'
    description: '从多云编排边界、状态契约到公开架构白皮书，先理解系统边界再选择实现路径。'
    links:
      - label: '参考资料总索引与 PDF 合订编排'
        href: '/docs/reference/index'
      - label: '多云平台工程技术白皮书'
        href: '/docs/reference/multi-cloud-platform-engineering-whitepaper'
      - label: '多云编排架构'
        href: '/blogs/02-iac-devops/cloud-infrastructure-devsecops-baseline/10-multi-cloud-orchestrator-architecture.zh'
  - title: '部署与交付'
    description: '查看 OIDC Bootstrap、GitOps 和执行 owner 的公开入口与实现仓库。'
    links:
      - label: '多云身份 Bootstrap 与状态契约'
        href: '/blogs/02-iac-devops/cloud-infrastructure-devsecops-baseline/11-cloud-oidc-bootstrap-contract.zh'
      - label: 'platform-ops-toolkit'
        href: 'https://github.com/ai-workspace-infra/platform-ops-toolkit'
      - label: 'gitops'
        href: 'https://github.com/ai-workspace-infra/gitops'
      - label: 'iac_modules'
        href: 'https://github.com/ai-workspace-infra/iac_modules'
      - label: 'playbooks'
        href: 'https://github.com/ai-workspace-infra/playbooks'
  - title: '数据迁移与容灾'
    description: '以发布快照、验收证据和混合部署指南为入口，区分规划、预演与真实验收。'
    links:
      - label: '平台操作中心与 Daily Snapshot'
        href: '/docs/design/platform-operations-daily-snapshot'
      - label: '混合部署架构源码 README'
        href: 'https://github.com/ai-workspace-services/knowledge/blob/main/docs/zh/hybrid-serverless-architecture-vault-pipeline-plan/README.md'
      - label: 'Serverless 与低成本架构指南'
        href: '/blogs/04-infra-platform/serverless-edge-cloud/how-to-leverage-free-saas-for-online-services.zh'
  - title: '安全与工程规范'
    description: '从无密钥 CI、内容契约和覆盖矩阵开始，保持公开文档与实现边界一致。'
    links:
      - label: 'GitHub 组织：ai-workspace-infra'
        href: 'https://github.com/ai-workspace-infra'
      - label: 'OIDC 无密钥 CI'
        href: '/blogs/02-iac-devops/cloud-infrastructure-devsecops-baseline/01-github-actions-oidc-keyless-ci'
      - label: '参考资料总览'
        href: '/docs/reference/overview'
      - label: '内容规范'
        href: '/docs/reference/content-schema'
      - label: '覆盖矩阵'
        href: '/docs/reference/coverage-matrix'
      - label: '历史文档映射'
        href: '/docs/reference/legacy-docs'
---
