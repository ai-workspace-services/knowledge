---
title: "以 AWS S3 为中央控制面的统一 IaC 状态中枢"
description: "在异构多云环境中，若各云独立维护 Terraform Backend，状态将四分五裂，无法进行跨云依赖编排。本架构确立以 AWS S3 为全网中央状态仓库。"
slug: multi-cloud-iac-mesh-02-unified-iac-state-on-s3
lang: zh
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

# 以 AWS S3 为中央控制面的统一 IaC 状态中枢

> 本文是《撕破云厂高墙：把割裂的异构云拧成一股绳》系列第 2 篇（共 5 篇），系列导读与目录见[这里](README.md)。

## 第二章：以 AWS S3 为中央控制面的统一 IaC 状态中枢

在异构多云环境中，若各云独立维护 Terraform Backend，状态将四分五裂，无法进行跨云依赖编排。本架构确立以 **AWS S3** 为全网中央状态仓库。

### 2.1 统一状态契约与 Provider Registry

整个基础设施注册表（Provider Registry）对纳管平台做出统一契约划分：

| Provider | Provisioner | State 类型 | 运行时凭据注入链条 |
|---|---|---|---|
| `aws-cloud` | `terraform` | TF State (S3) | GitHub OIDC → AWS STS AssumeRole |
| `gcp-cloud` | `terraform` | TF State (S3) | GitHub OIDC → GCP Workload Identity Federation |
| `azure-cloud` | `terraform` | TF State (S3) | GitHub OIDC → Azure Federated Identity |
| `vultr-vps` | `terraform` | TF State (S3) | GitHub OIDC → Vault JWT → `VULTR_API_KEY` |
| `akamai-cloud` | `terraform` | TF State (S3) | GitHub OIDC → Vault JWT → `LINODE_TOKEN` |
| `ucloud` | **`existing`** | External Inventory | Vault 临时凭据 + Ansible 采集事实（严禁 TF Apply） |
| `ulighthost` | **`existing`** | External Inventory | Vault 临时凭据 + Ansible 采集事实（严禁 TF Apply） |

### 2.2 S3 路径规范与原生状态锁（use_lockfile）

所有 Terraform 资源树统一提升至 Terraform `>= 1.10.x`。全面启用 S3 原生状态锁（`use_lockfile = true`），配合 Bucket Versioning 与服务端加密（SSE-S3/KMS），彻底舍弃繁琐且额外产生费用的 DynamoDB 锁表。

* **Terraform 状态键结构（五级隔离）**：
  ```text
  terraform/<provider>/<project>/<env>/<account>/<resource_group>.tfstate
  ```
* **状态锁文件**：
  ```text
  terraform/<provider>/<project>/<env>/<account>/<resource_group>.tfstate.tflock
  ```
* **非 Terraform 资源事实归档**：
  ```text
  inventory/<provider>/<project>/<env>/<account>/<resource_group>.json
  ```
* **执行追溯记录**：
  ```text
  runs/<env>/<run_id>.json
  ```

针对 UCloud / Ulighthost 等非 Terraform 资源，在元数据中强制注入规范：

```yaml
management_mode: existing
provisioner: ansible
lifecycle: external
```

流水线中坚决禁止对标记为 `existing` 的资源调用 `terraform apply` 或 `destroy`，杜绝任何状态覆写风险。

---

上一篇：[问题背景与 FinOps 拓扑对冲模型](01-background-and-finops-arbitrage.zh.md) · 下一篇：[全链路零信任凭据网络（Zero-Secret）](03-zero-secret-credential-mesh.zh.md) · [返回系列目录](README.md)
