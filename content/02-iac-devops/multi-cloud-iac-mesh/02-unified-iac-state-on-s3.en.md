---
title: "A Centralized IaC State Control Plane on AWS S3"
description: "Maintaining independent Terraform backends per cloud creates operational silos and prevents cross-cloud dependency orchestration. Our archit…"
slug: multi-cloud-iac-mesh-02-unified-iac-state-on-s3
lang: en
date: 2026-10-06
author: shenlan
category: iac-devops
series: multi-cloud-iac-mesh
weight: 2
tags:
  - multi-cloud
  - iac
  - terraform
  - vault
  - finops
  - global-mesh
---

# A Centralized IaC State Control Plane on AWS S3

> This is Part 2 of 5 in the series “Tearing Down Cloud Walls: Unifying Heterogeneous Multi-Cloud with IaC and Global Mesh”. See the [series index](README.md) for the reading order.

## 2. Centralized State Control Plane on AWS S3

Maintaining independent Terraform backends per cloud creates operational silos and prevents cross-cloud dependency orchestration. Our architecture designates **AWS S3** as the single source of truth for global infrastructure state.

### 2.1 Unified State Contract & Provider Registry

The provider registry enforces a strict execution contract:

| Provider | Provisioner | State Type | Credential Resolution Path |
|---|---|---|---|
| `aws-cloud` | `terraform` | TF State (S3) | GitHub OIDC → AWS STS AssumeRole |
| `gcp-cloud` | `terraform` | TF State (S3) | GitHub OIDC → GCP Workload Identity Federation |
| `azure-cloud` | `terraform` | TF State (S3) | GitHub OIDC → Azure Federated Identity |
| `vultr-vps` | `terraform` | TF State (S3) | GitHub OIDC → Vault JWT → `VULTR_API_KEY` |
| `akamai-cloud` | `terraform` | TF State (S3) | GitHub OIDC → Vault JWT → `LINODE_TOKEN` |
| `ucloud` | **`existing`** | External Inventory | Vault Token + Ansible Facts (TF Apply Prohibited) |
| `ulighthost` | **`existing`** | External Inventory | Vault Token + Ansible Facts (TF Apply Prohibited) |

### 2.2 S3 Key Hierarchy & Native State Locking (use_lockfile)

All Terraform configurations target Terraform `>= 1.10.x`, utilizing native S3 state locking (`use_lockfile = true`) alongside bucket versioning and server-side encryption (SSE-S3/KMS). This completely removes the operational overhead and billing footprint of legacy DynamoDB lock tables.

* **Terraform State Key (Five-Tier Hierarchy)**:
  ```text
  terraform/<provider>/<project>/<env>/<account>/<resource_group>.tfstate
  ```
* **State Lock File**:
  ```text
  terraform/<provider>/<project>/<env>/<account>/<resource_group>.tfstate.tflock
  ```
* **Non-Terraform Asset Facts**:
  ```text
  inventory/<provider>/<project>/<env>/<account>/<resource_group>.json
  ```
* **Execution Audit Logs**:
  ```text
  runs/<env>/<run_id>.json
  ```

For platforms lacking Terraform providers (UCloud, Ulighthost), resource metadata explicitly declares:

```yaml
management_mode: existing
provisioner: ansible
lifecycle: external
```

The CI/CD engine is strictly forbidden from executing `terraform apply` or `terraform destroy` against `existing` assets.

---

Previous: [Background and the FinOps Topology Arbitrage Model](01-background-and-finops-arbitrage.en.md) · Next: [The Zero-Secret Credential Brokerage Mesh](03-zero-secret-credential-mesh.en.md) · [Back to series index](README.md)
