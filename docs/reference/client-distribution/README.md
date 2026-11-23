---
title: 客户端多区域下载与双镜像分发规划（Client Distribution）
description: 围绕 console.svc.plus/download?product=xconnect 的 CN/Global 线路分流、应用商店与直装双渠道矩阵、阿里云 OSS（cn-dl.svc.plus）与 Cloudflare R2（dl.svc.plus）双镜像架构，以及 Vault KV + GitOps 声明式对接规划。
slug: client-distribution-readme
lang: zh
tags:
  - xconnect
  - download
  - client-distribution
  - aliyun-oss
  - cloudflare-r2
  - vault
  - gitops
  - planning
---

# 客户端多区域下载与双镜像分发规划（Client Distribution）

> [!NOTE]
> 本文档目录为**实施规划（Planning / Target Architecture）**，基线核查日期为 `2026-11-23`，记录目标架构、界面微调规范、镜像契约、Vault KV / GitOps 对接模型与跨仓库任务拆解，不代表对应代码或线上环境已完成交付或验收。所有现状核查均基于 `ai-workspace-services/portal`、`ai-workspace-infra/gitops` 与 `ai-workspace-xstream/xconnect-app` 仓库当前代码与已发布产物。

---

## 一、核心锁定决策摘要（Locked Decisions）

| 决策维度 | 锁定方案 | 说明与演进预留 |
| :--- | :--- | :--- |
| **CN 镜像域名与存储** | `https://cn-dl.svc.plus`（阿里云 OSS + 阿里云 CDN） | **面向所有产品矩阵设计**的中国大陆主镜像根域，统一承接 `/releases/<product>/*` 与 `/offline-package/<product>/*` |
| **Global 镜像域名与存储** | `https://dl.svc.plus`（Cloudflare R2） | **面向所有产品矩阵设计**的全球主镜像根域（沿用既有 `dl.svc.plus`），与 CN 镜像保持目录与 `release-matrix.json` 同构 |
| **应用商店渠道状态** | 四端商店当前均标记为 **暂未上架 / 仅提供直装**，并在 GitOps 与 UI 中**完整预留链接槽** | 覆盖 iOS（App Store / TestFlight）、Android（Google Play）、Windows（Microsoft Store）、macOS（Mac App Store）；后续商店过审上架后仅需更新 GitOps ConfigMap 状态与 URL，无需改动前端代码 |
| **CN OSS 防盗链 / 防刷策略** | 首期采用 **公开读 + CDN 带宽封顶** | 降低首期对接复杂度，通过阿里云 CDN 带宽封顶与告警控制异常流量成本；在 Vault KV 与 Portal 中预留后续切换为 **阿里云 CDN Type-A 短期签名鉴权** 的扩展位 |
| **版本矩阵权威源与前端边界** | **CI 生成 Release 版本矩阵（Single Source of Truth），前端 UI 纯展示** | 由 `xconnect-app/.github/workflows/build-and-release.yml` 产出统一 `release-matrix.json`（含 `stable` / `latest` 通道与近期版本历史、各平台架构/格式/校验值/受众分类）并原子同步至 `cn-dl.svc.plus` 与 `dl.svc.plus`；`portal` 仅拉取该矩阵并叠加 GitOps 商店预留槽进行纯数据驱动渲染，**零文件名正则猜测、零硬编码平台/格式表** |
| **本次规划覆盖范围** | **Phase 1（Portal）+ Phase 2（GitOps 模板与 Vault 契约）+ Phase 3（xconnect-app CI 同步与可观测性）** | 全链路从 CI 版本矩阵同步、GitOps 声明注入到纯展示前端渲染与黑盒探测一次对齐 |

---

## 二、目录文档索引

| 文档 | 内容概要 | 状态 |
| :--- | :--- | :--- |
| [01-xconnect-download-page-and-dual-mirror-plan.md](01-xconnect-download-page-and-dual-mirror-plan.md) | `console.svc.plus/download?product=xconnect` 现状诊断、CI Release 版本矩阵同步规范（`build-and-release.yml`）、前端纯展示 UX 与数据层设计、同构对象存储与 `release-matrix.json` 契约、Vault KV v2 与 GitOps 声明式模板及 Phase 1–3 任务单 | 规划草案 |

---

## 三、关联代码仓库与职责归属

| 仓库 | 组件 / 路径 | 核心职责 |
| :--- | :--- | :--- |
| `ai-workspace-services/portal` | `console.svc.plus`（`/download`） | **纯展示渲染层**：读取 GitOps 挂载的渠道配置、根据 `CF-IPCountry` 推断初始地区、拉取并缓存双镜像 `release-matrix.json`（叠加上架预留槽），直接渲染版本/通道切换、地区切换、商店与直装分流、多格式切换及 SHA-256 校验，不做文件正则猜测 |
| `ai-workspace-infra/gitops` | `services/*/web-saas-*`、`security/vault/*`、`services/*/observability-*` | 声明非密 `download-channels` ConfigMap（域名、矩阵路径与商店预留槽）、`HelmRelease` 挂载配置、Vault ACL Policy / JWT Auth Role 与 `ExternalSecret`、双镜像黑盒探活 |
| `ai-workspace-xstream/xconnect-app` | `.github/workflows/build-and-release.yml`、`scripts/ci/*` | **权威版本矩阵生产者（全产品矩阵首批试点）**：构建多平台安装包并解析版本/通道元数据，生成 `<tag>/matrix.json`、`channels/{stable,latest}.json` 与聚合 `release-matrix.json`，经 Vault JWT OIDC 获取 OSS 与 R2 最小权限凭据并原子同步至双镜像 |
| `ai-workspace-services/knowledge` | `docs/reference/client-distribution/` | 沉淀全链路设计契约、跨仓接口规范与分阶段验收标准 |

---

## 四、上线前人工前置清单（`P2-4`）与关联 PR

1. **Vault KV 写入最小权限凭据（`https://vault.svc.plus`）**：
   - `kv/prod/platform/storage/aliyun-oss`：`access_key_id`、`access_key_secret`、`bucket`、`endpoint`、`cdn_domain`（`cn-dl.svc.plus`）
   - `kv/prod/platform/storage/cloudflare-r2`：`access_key_id`、`secret_access_key`、`bucket`、`endpoint`
2. **存储与域名配置（面向全产品矩阵）**：
   - 确认 `https://cn-dl.svc.plus` 已绑定阿里云 OSS + CDN（开启公开读或私有 Bucket 回源 + **CDN 带宽封顶与告警**），可服务 `/releases/<product>/*` 与 `/offline-package/*`。
   - 确认 `https://dl.svc.plus` R2 自定义域可正常服务 `/releases/<product>/*`（含 `/releases/xconnect/*`），且不影响既有 `/dl-index/*` 与 `/offline-package/*`。
3. **关联 PR 与开启强门禁（可选）**：
   - 关联 PR：`knowledge#429`、`portal#541`、`gitops#964`、`xconnect-app#323`。
   - 上述凭据与域名验证通过、且合并全部 4 个 PR 后，可在 `ai-workspace-xstream/xconnect-app` 仓库变量设置 `XCONNECT_REQUIRE_MIRROR_SYNC=true` 启用同步强门禁。
