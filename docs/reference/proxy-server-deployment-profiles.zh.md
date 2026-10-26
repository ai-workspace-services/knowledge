---
title: Proxy Server 三种部署形态与控制面边界
description: 从 GitOps PR 428 迁入知识库白皮书体系的部署形态记录，保留固定来源并区分设计与运行验收。
slug: proxy-server-deployment-profiles
lang: zh
date: 2026-10-25
status: archived-design-not-runtime-acceptance
tags:
  - xconnect
  - proxy-server
  - platform-engineering
category: reference
---

# Proxy Server 三种部署形态与控制面边界

[English](proxy-server-deployment-profiles.en.md) · [多云平台工程技术白皮书](multi-cloud-platform-engineering-whitepaper.zh.md) · [参考资料总览](overview.zh.md)

本文将 GitOps PR #428 中的架构说明归档到知识库，作为平台工程白皮书的专题参考。记录的是原文定义的三种部署形态，不代表各形态已部署或通过真实连接、租户隔离与恢复验收。

## 三种形态

| 形态 | Proxy 节点与控制端 | 原文约束 |
| --- | --- | --- |
| 完全单节点自建 | 一个节点运行 Proxy Server 及本地控制组件 | 控制能力与代理同节点部署 |
| 共享 Proxy Server | 单个 Proxy Server 节点连接共享 Full 控制端 | 从选定环境声明获取控制端及范围 |
| 团队或共享 Proxy Server | 专用 Proxy Server 节点连接 Full 控制端 | 访问限制在配置的团队或共享租户范围 |

后两种形态在原文中的差异是共享节点与专用节点及访问范围；原文没有定义完整的租户模型、权限实现或运行验收结果，不能据此推导自动授权。后续 Team 节点登记与审批行为另见 [Team Proxy 节点登记、分配与审批](team-proxy-node-enrollment-20261020.zh.md)，其实施和验收状态以该记录的证据为准。

## 声明与运行时边界

Proxy Server 节点和 Full 控制端是独立部署目标。所选环境声明提供控制端地址、tenant/team scope、region 和 pool；凭据由 Vault 在运行时注入，不写入文档或 GitOps 声明。

- GitOps 保留可执行消费者读取的非敏感目标状态、版本及配置引用。
- 架构解释、部署形态比较与历史决策记录由 Knowledge 的白皮书和参考资料承接。
- 云资源、主机/服务和编排的执行仍分别归 IaC Modules、Playbooks、Toolkit；本次文档归档不改变执行归属。

## 后续运维验证约束

实施时遵循系统管理、业务运行、审计读取三类身份分离：系统管理身份不作为日常业务身份；服务独立读写并渐进降权；审计身份由权限强制只读。先核实实际权限，再按已确认问题逐服务验证和切换，保留证据与回退。本段是当前执行约束，不是原提交已实现安全改造的证明，也不扩大生产操作授权。

## 来源与归档记录

- 原需求与讨论：[ai-workspace-infra/gitops PR #428](https://github.com/ai-workspace-infra/gitops/pull/428)。
- 固定原文：[README.md，提交 4c965e6](https://github.com/ai-workspace-infra/gitops/blob/4c965e657441140c65ae50cfaa52b2c2647571f1/README.md#proxy-server-deployment-profiles)。
- 原提交日期：2026-10-14；本次归档日期：2026-10-25（Asia/Shanghai）。
- 归档任务：[Knowledge #229](https://github.com/ai-workspace-services/knowledge/issues/229)。
- 英文原始内容完整保留在 [英文版来源摘录](proxy-server-deployment-profiles.en.md#original-source-text)。

归档范围仅为该提交在 README 新增的 14 行。核查时原 PR 仍开放、未合并；其对当前 main 的差异已包含其他祖先提交的资源和拓扑文件，不能按“仅 README”合入。本次不迁移这些声明，不改写原分支或删除其他工作。当前 GitOps main 未包含该形态小节，因此无需从 main 删除正文。

验证分层：原文与来源可核查；本次只做文档和链接检查；真实部署、权限隔离、连接与恢复测试未执行。归档不代表站点已发布或 PR 已合并。
