---
hero:
  badge: Open-platform 解决方案
  title: 自主部署，构建可控的开放平台
  subtitle: 面向自主部署与多云平台建设，整合 IaC、GitOps、安全、身份与可观测性。从架构选型到交付治理，保留对代码、数据与部署的控制权。
  cta:
    label: 阅读方案架构
    href: /docs/reference/multi-cloud-platform-engineering-whitepaper
wizard:
  title: 从环境规划到部署验收
  description: 按实际需求选择组件，逐步建立可追溯的交付与运维流程。
  steps:
    - step: 1
      title: 明确环境与组件
      description: 梳理云资源、自建环境、业务依赖与数据边界，选择适合的部署架构。
    - step: 2
      title: 配置身份与交付
      description: 规划身份、权限和密钥管理，用 IaC 与 GitOps 管理资源及环境配置。
    - step: 3
      title: 验证运行与治理
      description: 结合可观测性、发布记录与验收检查，验证部署并规划持续运维。
showcases:
  - title: 基础设施与多云
    description: 用 IaC 管理资源与状态，明确云平台、环境和组件的责任边界。
    icon: layers
    image: ''
  - title: 交付与安全治理
    description: 用 GitOps 管理环境配置，将身份、权限、密钥与发布检查纳入交付流程。
    icon: shield-check
    image: ''
  - title: 可观测性与运维
    description: 结合运行观测、变更记录和部署验收，为故障诊断与持续运维提供依据。
    icon: activity
    image: ''
solutions:
  - title: 多云架构
    description: 从多云编排边界、状态契约到公开架构白皮书，先理解系统边界再选择实现路径。
    links:
      - label: 参考资料总索引与 PDF 合订编排
        href: /docs/reference/index
      - label: 多云平台工程技术白皮书
        href: /docs/reference/multi-cloud-platform-engineering-whitepaper
      - label: 多云编排架构
        href: /blogs/02-iac-devops/cloud-infrastructure-devsecops-baseline/10-multi-cloud-orchestrator-architecture.zh
  - title: 部署与交付
    description: 查看 OIDC Bootstrap、GitOps 和执行 owner 的公开入口与实现仓库。
    links:
      - label: 多云身份 Bootstrap 与状态契约
        href: /blogs/02-iac-devops/cloud-infrastructure-devsecops-baseline/11-cloud-oidc-bootstrap-contract.zh
      - label: platform-ops-toolkit
        href: https://github.com/ai-workspace-infra/platform-ops-toolkit
      - label: gitops
        href: https://github.com/ai-workspace-infra/gitops
      - label: iac_modules
        href: https://github.com/ai-workspace-infra/iac_modules
      - label: playbooks
        href: https://github.com/ai-workspace-infra/playbooks
  - title: 数据迁移与容灾
    description: 以发布快照、验收证据和混合部署指南为入口，区分规划、预演与真实验收。
    links:
      - label: 平台操作中心与 Daily Snapshot
        href: /docs/design/platform-operations-daily-snapshot
      - label: 混合部署架构源码 README
        href: https://github.com/ai-workspace-services/knowledge/blob/main/docs/zh/hybrid-serverless-architecture-vault-pipeline-plan/README.md
      - label: Serverless 与低成本架构指南
        href: /blogs/04-infra-platform/serverless-edge-cloud/how-to-leverage-free-saas-for-online-services.zh
  - title: 安全与工程规范
    description: 从无密钥 CI、内容契约和覆盖矩阵开始，保持公开文档与实现边界一致。
    links:
      - label: GitHub 组织：ai-workspace-infra
        href: https://github.com/ai-workspace-infra
      - label: OIDC 无密钥 CI
        href: /blogs/02-iac-devops/cloud-infrastructure-devsecops-baseline/01-github-actions-oidc-keyless-ci
      - label: 参考资料总览
        href: /docs/reference/overview
      - label: 内容规范
        href: /docs/reference/content-schema
      - label: 覆盖矩阵
        href: /docs/reference/coverage-matrix
      - label: 历史文档映射
        href: /docs/reference/legacy-docs
---
