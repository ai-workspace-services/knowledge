# 平台交付与节点运维文档

本目录归档五份专项参考文档，并提供一份跨组件总体架构。规划和目标图不代表代码已实现或线上已验收；运行状态以各文档标注的观察时间和回执为准。

## 总体架构

- [OpenplatForm Delivery Architecture](OpenplatForm-Delivery-Architecture.md) — 基础运行环境、统一架构图、多环境发布、观测与安全边界。

## 专项参考

1. [环境与业务发布解析：最小实施草案](环境与业务发布解析-最小实施草案.md)
2. [GitHub Actions 流水线实施草案](GitHub-Actions流水线实施草案.md)
3. [Linux OS 三类操作身份：最小实施草案](Linux-OS三类操作身份-最小实施草案.md)
4. [K3s role 职责与依赖清单](K3s-role职责与依赖清单.md)
5. [PROD-K3S-V6 独立节点、集群冷启动规划与部署状态归档](PROD-K3S-V6-规划与部署状态归档.md)

来源：`ai-workspace-infra/docs` 的 `archives/2026-10-30`；其中流水线草案与 V6 状态归档包含归档时尚未提交的工作树更新。K3s role 清单中的日期和运行状态反映其原始记录；当前 V6 状态以 V6 归档中最新核对条目为准。
