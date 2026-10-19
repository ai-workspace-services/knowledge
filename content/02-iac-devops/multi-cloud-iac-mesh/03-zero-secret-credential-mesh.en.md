---
title: "The Zero-Secret Credential Brokerage Mesh"
description: "Storing long-lived cloud API keys (AK/SK) in repositories or CI/CD runners is an unacceptable security posture. We deploy a dynamic credenti…"
slug: multi-cloud-iac-mesh-03-zero-secret-credential-mesh
lang: en
date: 2026-10-06
author: shenlan
category: iac-devops
series: multi-cloud-iac-mesh
weight: 3
tags:
  - multi-cloud
  - iac
  - terraform
  - vault
  - finops
  - global-mesh
---

# The Zero-Secret Credential Brokerage Mesh

> This is Part 3 of 5 in the series “Tearing Down Cloud Walls: Unifying Heterogeneous Multi-Cloud with IaC and Global Mesh”. See the [series index](README.md) for the reading order.

## 3. Zero-Secret Credential Brokerage Mesh

Storing long-lived cloud API keys (AK/SK) in repositories or CI/CD runners is an unacceptable security posture. We deploy a dynamic credential brokerage model anchored on GitHub Actions OIDC and HashiCorp Vault:

```text
GitHub Actions Runner (id-token: write)
    │
    ├── [Channel 1: S3 State Access]
    │    └── GitHub OIDC ──> AWS STS (AssumeRole) ──> Scoped S3 Read/Write Token
    │
    ├── [Channel 2: Tier-2 Cloud Token Exchange]
    │    └── GitHub OIDC ──> HashiCorp Vault (JWT Auth)
    │         ├── Read kv/data/CICD/<env>/akamai-cloud/primary ──> Inject LINODE_TOKEN
    │         └── Read kv/data/CICD/<env>/vultr-vps/primary ──> Inject VULTR_API_KEY
    │
    └── [Channel 3: Direct Tier-1 Cloud Federation]
         ├── GCP: Workload Identity Federation (WIF)
         └── Azure: Federated Identity Credentials
```

### 3.1 HashiCorp Vault Least-Privilege Policy

Vault grants time-bound, read-only leases scoped to specific environments and roles:

```hcl
# Vault Access Policy: Read-only access for UAT Akamai Cloud
path "kv/data/CICD/uat/akamai-cloud/primary" {
  capabilities = ["read"]
}

path "kv/metadata/CICD/uat/akamai-cloud/primary" {
  capabilities = ["read"]
}
```

GitHub Actions workflows bind strictly to repository, environment, and ref constraints:

```yaml
# .github/workflows/deploy-akamai.yml
jobs:
  provision:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write # Required for short-lived OIDC exchange
    steps:
      - name: Retrieve Vault Secrets
        uses: hashicorp/vault-action@v3
        with:
          url: https://vault.infra.internal:8200
          role: github-actions-platform-ops-toolkit-uat-akamai-oidc-bootstrap-primary
          method: jwt
          secrets: |
            kv/data/CICD/uat/akamai-cloud/primary LINODE_TOKEN | TF_VAR_linode_token
```

Sensitive tokens exist solely in runner memory and are never persisted to disk or logged.

---

Previous: [A Centralized IaC State Control Plane on AWS S3](02-unified-iac-state-on-s3.en.md) · Next: [Global Mesh Ingress Hardening and Cross-Repository Orchestration](04-global-mesh-and-cross-repo-orchestration.en.md) · [Back to series index](README.md)
