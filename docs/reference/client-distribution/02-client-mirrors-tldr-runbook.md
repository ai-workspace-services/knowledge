---
title: TL;DR：双镜像（Cloudflare R2 + Aliyun OSS/CDN）Token 轮换与一键对接
description: 快速完成 Cloudflare 最小权限 API Token 创建、Vault kv/prod/serverless/cloudflare 非交互轮换、playbooks/roles/saas/client_mirrors 的 plan/apply 对接及双端 HTTPS/CORS 验收的操作手册。
slug: client-mirrors-tldr-runbook
lang: zh
tags:
  - client-distribution
  - cloudflare-r2
  - aliyun-oss
  - vault
  - playbooks
  - runbook
  - tldr
---

# TL;DR：双镜像（Cloudflare R2 + Aliyun OSS/CDN）Token 轮换与一键对接

> 目标域名：`https://dl.svc.plus`（Cloudflare R2）+ `https://cn-dl.svc.plus`（Aliyun `oss-cn-hongkong` + CDN `overseas`）  
> 执行仓库：`ai-workspace-infra/playbooks`（`roles/saas/client_mirrors` + `configure_client_mirrors.yml`）  
> IaC 资源定义：`ai-workspace-infra/iac_modules`（`terraform-hcl-standard/client-mirrors/`）  
> GitOps 声明：`ai-workspace-infra/gitops`（`resources/svc.plus/prod/client-mirrors/mirrors.yaml`）

---

## 1. 在 Cloudflare 控制台创建最小权限 API Token

进入 **Manage Account → Account API Tokens**（或 **User Profile → API Tokens**）创建/更新 Token，授予以下最小权限：

| 作用域 | 权限项 | 用途 |
| :--- | :--- | :--- |
| **Account** | `Workers R2 Storage: Edit` | 创建/对账 R2 Bucket、Custom Domain (`dl.svc.plus`) 与 CORS |
| **Account** | `Account API Tokens: Edit` | 自动签发 Bucket-Scoped R2 S3 Token 并回写 Vault |
| **Zone (`svc.plus`)** | `Zone: Read` | 查询 `svc.plus` Zone ID |
| **Zone (`svc.plus`)** | `DNS: Edit` | 同步 `verification.svc.plus` TXT 与 `cn-dl.svc.plus` CNAME（非代理） |

---

## 2. 将新 Token 非交互轮换写入 Vault (`kv/prod/serverless/cloudflare`)

> 先确认 `kv/prod/serverless/cloudflare` 当前版本号（例如执行时为 `current_version: 2`）：
> `VAULT_ADDR=https://vault.svc.plus VAULT_TOKEN=$(cat ~/.vault-token) vault kv metadata get -mount=kv -format=json prod/serverless/cloudflare`  
> 以下命令自动复用现有 `CLOUDFLARE_ACCOUNT_ID`，仅以非交互方式更新 `CLOUDFLARE_API_TOKEN`：

```bash
cd /Users/shenlan/workspaces/ai-workspace-infra/playbooks/roles/saas/client_mirrors/files
export VAULT_ADDR="https://vault.svc.plus"

CLOUDFLARE_ACCOUNT_ID="$(VAULT_TOKEN=$(cat ~/.vault-token) vault kv get -mount=kv -field=CLOUDFLARE_ACCOUNT_ID prod/serverless/cloudflare)" \
CLOUDFLARE_API_TOKEN='<新的Cloudflare_API_Token>' \
./bootstrap-admin-vault-kv.sh --provider cloudflare --non-interactive --rotate --expected-version 2
```

*(若需补录或轮换阿里云管理员 AK/SK，可执行：)*

```bash
ALICLOUD_ACCESS_KEY='<阿里云AccessKeyId>' \
ALICLOUD_SECRET_KEY='<阿里云AccessKeySecret>' \
./bootstrap-admin-vault-kv.sh --provider alicloud --non-interactive
```

---

## 3. 执行只读预览（`plan`）与正式对接（`apply`）

```bash
cd /Users/shenlan/workspaces/ai-workspace-infra/playbooks
export VAULT_ADDR="https://vault.svc.plus"
export VAULT_TOKEN="$(cat ~/.vault-token)"

# 1) 只读预览（零变更）
ansible-playbook -i 'localhost,' configure_client_mirrors.yml -e client_mirrors_mode=plan

# 2) 正式执行（R2 + OSS + CDN 归属 TXT + CDN 域名/限速 + 非代理 CNAME + RAM 最小子账号 + Vault 回写 + 双端 HTTPS/CORS 探针）
ansible-playbook -i 'localhost,' configure_client_mirrors.yml -e client_mirrors_mode=apply
```

---

## 4. 验收清单

- Vault 自动生成并写入最小权限 CI 存储凭据：
  - `kv/prod/platform/storage/cloudflare-r2`
  - `kv/prod/platform/storage/aliyun-oss`
- `apply` 输出中 `verification.https_probes` 两条探针均为 `"ok": true`（HTTP `200` 且返回 `Access-Control-Allow-Origin: https://console.svc.plus`）：
  - `https://dl.svc.plus/releases/_health/probe.json`
  - `https://cn-dl.svc.plus/releases/_health/probe.json`
- 后续仅做健康探针复核时，可执行：

```bash
ansible-playbook -i 'localhost,' configure_client_mirrors.yml -e client_mirrors_mode=verify
```
