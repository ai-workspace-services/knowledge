---
title: "全链路零信任凭据网络（Zero-Secret）"
description: "多云运维的第一大忌是在代码仓库或 CI/CD 变量中长期存放 AccessKey / SecretKey。本体系基于 GitHub Actions OIDC 与 HashiCorp Vault 搭建了凭据置换网格："
slug: multi-cloud-iac-mesh-03-zero-secret-credential-mesh
lang: zh
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

# 全链路零信任凭据网络（Zero-Secret）

> 本文是《撕破云厂高墙：把割裂的异构云拧成一股绳》系列第 3 篇（共 5 篇），系列导读与目录见[这里](README.md)。

## 第三章：全链路零信任凭据网络（Zero-Secret）

多云运维的第一大忌是在代码仓库或 CI/CD 变量中长期存放 AccessKey / SecretKey。本体系基于 GitHub Actions OIDC 与 HashiCorp Vault 搭建了凭据置换网格：

```text
GitHub Actions Runner (id-token: write)
    │
    ├── [通道 1: S3 控制面鉴权]
    │    └── GitHub OIDC ──> AWS STS (AssumeRole) ──> 获取环境前缀隔离的 S3 读写权限
    │
    ├── [通道 2: 二级云厂商凭据置换]
    │    └── GitHub OIDC ──> HashiCorp Vault (JWT 登录)
    │         ├── 读取 kv/data/CICD/<env>/akamai-cloud/primary ──> 注入 LINODE_TOKEN
    │         └── 读取 kv/data/CICD/<env>/vultr-vps/primary ──> 注入 VULTR_API_KEY
    │
    └── [通道 3: 一线公有云联邦直接认证]
         ├── GCP: Workload Identity Federation (WIF)
         └── Azure: Federated Identity Credentials
```

### 3.1 HashiCorp Vault 最小权限策略实现

以 Akamai Cloud (Linode) 为例，CI/CD 角色仅授予对特定环境路径的只读租约：

```hcl
# Vault 访问策略：仅限 UAT 环境只读
path "kv/data/CICD/uat/akamai-cloud/primary" {
  capabilities = ["read"]
}

path "kv/metadata/CICD/uat/akamai-cloud/primary" {
  capabilities = ["read"]
}
```

GitHub Actions 工作流配置严格绑定代码仓库分支与环境契约：

```yaml
# .github/workflows/deploy-akamai.yml
jobs:
  provision:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write # 必须：用于请求短期 OIDC Token
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

所有敏感令牌全程仅驻留内存，严禁持久化至磁盘，且绝不进入日志或 Git 历史。

---

上一篇：[以 AWS S3 为中央控制面的统一 IaC 状态中枢](02-unified-iac-state-on-s3.zh.md) · 下一篇：[Global Mesh 跨云流量抹平与跨仓库工程闭环](04-global-mesh-and-cross-repo-orchestration.zh.md) · [返回系列目录](README.md)
