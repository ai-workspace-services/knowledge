---
hero:
  badge: Open-platform solution
  title: Build an open platform you control
  subtitle: Combine IaC, GitOps, security, identity, and observability for self-managed and multi-cloud platforms. Keep control of code, data, and deployment from architecture selection to delivery governance.
  cta:
    label: Read the solution architecture
    href: /docs/reference/multi-cloud-platform-engineering-whitepaper
wizard:
  title: From environment planning to deployment acceptance
  description: Select components for your needs and establish traceable delivery and operations step by step.
  steps:
    - step: 1
      title: Define environment and components
      description: Map cloud resources, self-managed environments, dependencies, and data boundaries before choosing an architecture.
    - step: 2
      title: Configure identity and delivery
      description: Plan identity, permissions, and secrets, then manage resources and environment configuration with IaC and GitOps.
    - step: 3
      title: Verify operations and governance
      description: Use observability, release records, and acceptance checks to verify deployment and plan ongoing operations.
showcases:
  - title: Infrastructure and multi-cloud
    description: Manage resources and state with IaC, with clear ownership across clouds, environments, and components.
    icon: layers
    image: ''
  - title: Delivery and security governance
    description: Manage environment configuration with GitOps and include identity, permissions, secrets, and release checks in delivery.
    icon: shield-check
    image: ''
  - title: Observability and operations
    description: Use runtime observations, change records, and deployment acceptance as evidence for diagnosis and ongoing operations.
    icon: activity
    image: ''
solutions:
  - title: Multi-cloud architecture
    description: Understand orchestration boundaries, state contracts, and the public white paper before choosing an implementation path.
    links:
      - label: Reference index and PDF compilation plan
        href: /docs/reference/index
      - label: Multi-Cloud Platform Engineering Technical White Paper
        href: /docs/reference/multi-cloud-platform-engineering-whitepaper
      - label: Multi-cloud orchestrator architecture
        href: /blogs/02-iac-devops/cloud-infrastructure-devsecops-baseline/10-multi-cloud-orchestrator-architecture.zh
  - title: Deployment and delivery
    description: Follow the public OIDC Bootstrap contract, GitOps boundaries, and execution-owner repositories.
    links:
      - label: Cloud OIDC bootstrap and state contract
        href: /blogs/02-iac-devops/cloud-infrastructure-devsecops-baseline/11-cloud-oidc-bootstrap-contract.zh
      - label: platform-ops-toolkit
        href: https://github.com/ai-workspace-infra/platform-ops-toolkit
      - label: gitops
        href: https://github.com/ai-workspace-infra/gitops
      - label: iac_modules
        href: https://github.com/ai-workspace-infra/iac_modules
      - label: playbooks
        href: https://github.com/ai-workspace-infra/playbooks
  - title: Data migration and resilience
    description: Use release snapshots, acceptance evidence, and the hybrid deployment guide to distinguish plans, rehearsals, and verified releases.
    links:
      - label: Platform operations and Daily Snapshot
        href: /docs/design/platform-operations-daily-snapshot
      - label: Hybrid deployment source README
        href: https://github.com/ai-workspace-services/knowledge/blob/main/docs/zh/hybrid-serverless-architecture-vault-pipeline-plan/README.md
      - label: Serverless and low-cost architecture guide
        href: /blogs/04-infra-platform/serverless-edge-cloud/how-to-leverage-free-saas-for-online-services.en
  - title: Security and engineering standards
    description: Start with keyless CI, the content contract, and the coverage matrix to keep public documentation aligned with implementation boundaries.
    links:
      - label: 'GitHub organization: ai-workspace-infra'
        href: https://github.com/ai-workspace-infra
      - label: OIDC keyless CI
        href: /blogs/02-iac-devops/cloud-infrastructure-devsecops-baseline/01-github-actions-oidc-keyless-ci
      - label: Reference overview
        href: /docs/reference/overview
      - label: Content schema
        href: /docs/reference/content-schema
      - label: Coverage matrix
        href: /docs/reference/coverage-matrix
      - label: Legacy docs map
        href: /docs/reference/legacy-docs
---
