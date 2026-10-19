---
title: "AI Workspace 顶层架构与远景项目设计：系列导读与目录"
description: "AI Workspace 顶层架构与远景设计系列（5 篇）的导读与目录：愿景、组织边界、声明式契约、Lego 模型、产品演进、Lab 与 XConnect、治理与路线图。"
slug: ai-workspace-architecture-vision
lang: zh
date: 2026-10-06
author: shenlan
category: design
series: ai-workspace-architecture-vision
weight: 0
tags:
  - ai-workspace
  - architecture
  - vision
  - roadmap
---

# AI Workspace 顶层架构与远景项目设计：系列导读与目录

> **Status**: Vision / Architecture Draft  
> **Scope**: 顶层架构、组织边界、声明式模型与路线图  
> **Non-goal**: 本文不定义实现代码、具体框架或单一供应商方案

## 导读

本系列由原单篇长文《AI Workspace 顶层架构与远景项目设计》按章节拆分而成，正文保持原意。建议按顺序阅读：先确定愿景与组织边界，再看总体架构与核心声明式契约，随后是组合模型与产品演进、各运行层的边界，最后是治理规则与路线图。

## 目录

1. [愿景与四个组织的长期边界](01-vision-and-org-boundaries.zh.md)：核心分工可概括为：Lab 发现积木 → XConnect 标准化连接积木 → Infra 运行积木 → Services 组合成产品。
2. [总体架构与 Workspace Specification 声明式契约](02-architecture-and-workspace-spec.zh.md)：这里的四个动词代表职责流，而不是强制的线性部署顺序。生产 Workspace 通常由 Services 编排 XConnect 的能力，并请求 Infra 在目标环境运行。
3. [两级 Lego 模型、三种消费方式与三阶段产品演进](03-lego-model-and-product-evolution.zh.md)：ai-desktop-lab 可作为 Desktop Module 与 Profile 的参考实现来源：XLaunch/XDock 属于桌面交互 Module，Remote Desktop 属于 Desktop Access Module，isobuilder 属于 Image/…
4. [Services 层、Lab 生命周期、XConnect 与 Infra](04-services-lab-xconnect-infra.zh.md)：StartFast 调研得到的启发仅用于定义 Product Shell：Services 需要具备清晰的 Auth、Billing、Onboarding、Workspace 管理、API 与 SEO 能力，使底层复杂性变成可理解的产品体验。该思路不绑定 Next.js、Bett…
5. [架构治理、Roadmap 与 North Star（附术语速查）](05-governance-roadmap-north-star.zh.md)：依赖应优先指向稳定的 Contract，而不是反向依赖具体仓库。跨组织变更需要版本、Owner、兼容窗口、迁移说明和回滚策略。
