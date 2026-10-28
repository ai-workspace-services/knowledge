---
title: 多云资源三档权限、IAM 与 Vault 安全集成及 Shared CMDB 技术规范白皮书
description: 面向每个资源与服务及初始化 OS、PostgreSQL、Supabase 用户的 reader/operator/admin 权限合同、IaC/Vault 集成、Shared CMDB 和实施验收规范。
slug: multi-cloud-iam-vault-cmdb-security-whitepaper
lang: zh
date: 2026-10-28
version: "1.3"
status: active-with-implementation
category: reference
tags:
  - multi-cloud
  - iam
  - vault
  - least-privilege
  - cmdb
  - postgresql
  - gitops
---

# 多云资源三档权限、IAM 与 Vault 安全集成及 Shared CMDB 技术规范白皮书

版本：1.3 · 规划基准：2026-10-10 · 落地更新：2026-10-28（Infrastructure-MCP-Server CMDB 动态对账、只读 CLI Guardrails 与 15 依赖边图拓扑联动已通过 PR #4 合并落地）· 状态：核心模块已落地实施并归档。

1.2 补充：将三档权限拆分为云账号、主机 OS、自建服务三个独立授权层；三层分别初始化、分别验收，不自动继承。
1.3 补充：CMDB 动态对账与只读 reader 策略通过 Go 原生 Infrastructure-MCP-Server 网关实现，打通 SIT/UAT/PROD 多云资产动态汇总、service/observability-gateway 15 条拓扑依赖检索及 safe CLI 工具受控执行。详见《[Infrastructure-MCP-Server 部署、集中式可观测性、CMDB 与 QMD 记忆系统交付全景技术规范](infrastructure-mcp-observability-cmdb-qmd-delivery-spec.zh.md)》。

[参考资料总索引](index.md) · [平台工程白皮书](multi-cloud-platform-engineering-whitepaper.zh.md) · [原 CMDB 落地规划](multi-cloud-cmdb-postgresql-grafana-plan.zh.md)

## 摘要

平台统一采用轻量级三档权限：只读 `reader`、业务操作 `operator`、管理员 `admin`。每个资源或服务都必须具有三档权限合同、明确身份绑定和可验证的授权边界；三档是能力分层，不要求每个资源机械创建三个静态用户，也不允许三个档位共享同一管理员凭据。

CMDB 采集程序与独立 PostgreSQL 数据库 `cmdb` 均运行在 Shared 主机，观察 Shared、UAT、PROD 全量资源。源资源所属范围、采集运行范围和数据库存储范围分别记录。IaC 管理云身份与资源事实，Vault 控制运行时秘密访问，Playbooks 管理主机、服务与数据库，Toolkit/Pipeline 负责授权编排和证据门禁。

三档权限必须在初始化时建立，而不是部署结束后补一个 reader 用户：云账号 IAM、主机 OS 授权、自建服务控制面/业务面、数据库 SQL 角色、Supabase 应用用户/API 策略分别落地，不能以任一层的角色名称代替另一层的能力验证。

本文形成目标规范与实施规划。写入文档不创建账户、云 IAM、Vault 记录、policy、role 或 bootstrap 脚本，不执行部署、迁移或线上验证。现有模块可以部分复用，但专用身份、字段适配、采集入口、其他 provider adapters 和线上验收仍有缺口。

## 1. 范围、规范等级与证据边界

### 1.1 适用范围

覆盖 GCP、AWS、Linode/Akamai、UCloud 以及 Cloudflare、Supabase 等 Serverless/托管资源；适用于云 API、主机、数据库、应用服务、Observability 和相关交付流程。新增 provider 必须实现相同的权限与证据合同。

本文中的“必须/禁止”为目标强制规范；“建议”为可经评审调整的默认方案；“待核实”表示不能据此上线。规划组件名、路径模板与合同示例不代表已有可执行实现或有效凭据。

### 1.2 本次源码基线

IaC 复用评估以 `iac_modules` 的 `origin/main@4dab50df81eceb58b4b31b46a2ba7404d70ad6cf` 为源码基线。采集、认证、发布和模块证据见第 13 章固定提交链接。源码存在只证明实现可检查，不证明对应 IAM/Vault 配置已应用。

此前 Shared 主机的 Compute 查询 403、数据库文件凭据和部分 GCP 入库结果，属于 [2026-10-09 历史证据](cmdb-shared-uat-evidence-20261009.zh.md)，不是本文重新核验的线上现状。主机数 GCP 7、AWS 1、Linode 1、UCloud TW/PH 各 1 是初始对账口径，不是实时库存或完整性证明。

### 1.3 与旧文档的关系

| 旧表述 | 本次目标约定 | 迁移约束 |
| --- | --- | --- |
| 数据库连接及秘密路径属于 UAT | CMDB 执行和存储均属于 Shared | 不因改路径重建数据库、改写历史观察或删除旧凭据 |
| `open-platform-shared` 可作为另一项目的配置别名 | `open-platform-shared` 与 `open-platform-shared-510113` 是两个独立原生 project ID | 分别声明、授权、采集和对账 |
| UAT collector 汇总 PROD | Shared collector 观察 Shared/UAT/PROD | 跨范围只读授权不等于跨范围业务或管理员权限 |
| 旧部署身份字段及旧 KV 根路径 | 新消费者按本白皮书合同适配 | 旧 caller 未迁移前保留明确兼容合同，不静默回退 |

本章仅更新目标设计的优先解释，不追认旧文档的部署状态。原规划、[Vault 路径规划](cmdb-vault-paths.zh.md) 和历史证据保留适用日期，后续代码变更需逐项对齐。

## 2. 每个资源与服务的三档权限

### 2.1 统一能力矩阵

| 能力 | reader：只读 | operator：业务操作 | admin：管理员 |
| --- | --- | --- | --- |
| 查看状态、库存、分析与授权范围内日志 | 允许，限制敏感字段 | 允许 | 允许 |
| 重启服务、发布与日常配置调整 | 禁止 | 仅明确的资源和操作 allowlist | 允许，仍受变更门禁 |
| 业务数据写入 | 禁止 | 按表、接口或业务职责授权 | 按目标服务管理职责授权 |
| 读取秘密 | 默认禁止 | 仅运行必需的精确记录 | 不默认批量读取；按管理任务授权 |
| 创建用户、分配权限、修改信任关系 | 禁止 | 禁止 | 在授权资源边界内允许 |
| 资源销毁、清库、重大网络/生命周期变更 | 禁止 | 默认禁止 | 经审批、备份及目标确认后允许 |
| 修改自己的权限或审批自己的提权 | 禁止 | 禁止 | 不得绕过独立审批 |
| 删除独立审计证据或关闭平台审计 | 禁止 | 禁止 | 日常资源管理员不得掌握独立审计存储管理权 |

管理员表示目标资源/服务内的最高管理能力，不自动代表组织 root、整个云账户 Administrator 或 Vault root。组织级 IAM、跨项目授权和平台审计控制属于独立管理边界。

`operator` 不等于全部非管理员权限：部署、重启、业务写入等必须细分，避免通过任意脚本、实例身份替换、secret 注入、通用 sudo 或 role pass/impersonation 间接提权。涉及执行新代码或选择运行身份的发布权限必须单独评审。

### 2.2 身份与角色绑定

1. 人员使用实名身份/用户组；工作负载使用独立 service account、role 或专用 API principal，禁止共享管理员账号。
2. 按 provider、原生账号、scope、资源或服务分别绑定角色。同一主体可以在云 API 上是 reader、在 CMDB 指定表上是 writer 型 operator。
3. 日常人员和服务默认没有常驻 admin；管理操作采用受保护流程与有界会话。人工特权访问应具有 MFA、审批、过期和审计要求。
4. `auditor`、`backup`、`migrator` 是职责特化，不强行合并成三个登录用户：auditor 属只读特化，backup 按经评审的读/恢复能力分开，migrator 属受保护管理职责。
5. 应急身份单独登记、托管、演练和审计，不作为普通业务流程缺少权限时的 fallback。

### 2.3 产品能力不一致的处理

每个资源必须有三档目标合同，但产品未必原生支持三档精细授权。必须记录 `supported`、`constrained`、`unsupported` 或 `pending_verification`，及作用范围、实际权限和补偿控制。禁止用名字为 reader 的写入 token 冒充只读；应用代理/流程门禁不能被表述为已消除底层凭据权限。

不能建立安全 reader 的 provider 不启用常驻 API 采集；可评估有出处、时间戳和 TTL 的 external inventory，继续保留 API/权限缺口。

### 2.4 三个独立授权层

平台权限按“云账号层 → OS 层 → 自建服务层”拆分。三层的 `reader / operator / admin` 是同名、不同边界的能力，不是跨层继承关系：云账号 `operator` 不自动取得主机 shell，OS `admin` 不自动取得云 IAM，自建服务 `admin` 不自动取得 PostgreSQL、主机或云账号管理员权限。

| 层面 | reader：只读 | operator：业务操作 | admin：管理员 |
| --- | --- | --- | --- |
| 云账号层 | 读取账号/项目、资源清单、状态、配置摘要、审计/监控中允许的内容；禁止创建、修改、删除、启停、部署和 IAM 变更 | 仅对明确资源和服务执行日常业务动作，例如发布已批准版本、扩缩容、重启指定服务或修改业务配置；禁止 IAM/信任关系、账户账单所有权和跨范围授权 | 在批准的账号/项目边界内管理资源生命周期、网络、IAM、联邦、密钥与策略；高风险删除、跨账号授权和组织级操作仍需独立审批 |
| 主机 OS 层 | 受限查询、脱敏状态/日志和只读诊断；禁止写文件、改配置、服务控制、sudo、Docker socket、网络和用户/key 管理 | 仅操作批准的业务服务、工作目录和受控命令；禁止通用 root、任意 sudo、软件/网络/用户管理和通过可写脚本提权 | 管理目标主机 OS、包、网络、用户、服务、文件和安全策略；应使用实名/临时特权，会话和变更可审计 |
| 自建服务层 | 查看服务状态、业务分析、非敏感配置和授权范围内日志；禁止业务写入、发布、重启、密钥管理与权限管理 | 执行服务定义的日常业务操作、有限数据写入、已批准发布/回滚；禁止修改权限模型、读取无关秘密、执行任意代码或跨租户操作 | 管理服务配置、版本、租户/业务权限、数据生命周期和受控恢复；不能自动拥有底层 OS、云账号或 Vault root |

云厂商的“查看/编辑/管理员”、Linux 的 UID/GID/sudo、应用的 RBAC、数据库 ACL 和 Supabase Data API/RLS 是不同机制。实施时要把三档合同翻译成各层实际 policy/grant/ACL，并记录 `capability_status`；不能只创建同名用户或组。

跨层访问按最小组合授权：例如 CMDB collector 可以是云账号 `reader` + 自建 CMDB 服务的 `operator`，但仍不是 OS `operator`；Playbooks 探针部署可能需要精确 OS `operator`，但不应取得云账号 `admin`；Grafana 是自建服务 `reader` + PostgreSQL `reader`，不取得云账号身份。任一层缺少能力时，整体任务应失败或标记为未放行，不得自动向上一层提权。

每个资源/服务的声明必须同时包含 `cloud_access_profile`、`os_access_profile`、`service_access_profile`；不适用的层面使用 `not_applicable` 并说明原因。三档初始化回执分别记录云主体/role、OS 用户/组、服务 principal/role、实际 policy 摘要、测试时间和 owner 版本。

## 3. Shared 执行、Shared 存储、全范围观察

| 维度 | 合同字段 | 目标 |
| --- | --- | --- |
| 采集程序运行归属 | `execution_scope` | `shared` |
| CMDB 数据库归属 | `storage_scope` | `shared` |
| 被观察资源范围 | `observed_scopes` | `[shared, uat, prod]` |
| 单项资源来源 | 现有 observations 的 `scope` | 保留资源实际归属，不因汇总改成 shared |
| 云账号身份 | `account_ref`、`project_ref` | 原生 AWS account ID、GCP project ID 等 |

逻辑项目固定使用 `svc.plus`，不得代替云厂商的原生账号/项目。未确认归属的资源使用 `unknown`；跨环境共用资源通过关系表表达，不能复制成多个不同环境资源充数。

首批 Shared 落点声明以 `open-platform-shared` 的 `observability-shared-0` 为规划目标，实施时重新核验主机原生 ID、zone、容量及运行服务。不得将它与另一 Shared 项目的 Observability 实例按名称或域名合并。

“独立 cmdb 数据库”必须具有独立 database/schema、角色、迁移、连接限制、备份和恢复生命周期。与 Observability 共用主机不构成故障域隔离；必须设置采集并发、连接池、磁盘/CPU/内存预算及数据库网络限制，评估宿主机特权被攻陷后的共同风险。

验证环境可以是 UAT 或隔离演练，但不能因此把目标数据库的 `storage_scope` 改成 uat。观测来源全量也不授权部署到全量主机。

## 4. owner 分工与两条执行链

| 层 | owner 职责 | 不应承担 |
| --- | --- | --- |
| GitOps | 非秘密资源/身份绑定、三档权限、范围、版本、周期、Vault 引用 | 秘密值、运行事实伪造 |
| IaC Modules | 云 IAM/联邦信任、provider collectors、归一化与资源事实合同 | 主机安装、数据库引擎部署、SQL 迁移 |
| Playbooks | 主机/服务授权、Vault Agent 配置、PostgreSQL、迁移、入库执行、备份恢复、Grafana、采集定时服务 | 云管理员授权绕过、全量 inventory 自动部署 |
| Toolkit/Pipeline | 操作选择、审批、身份选择、固定 SHA dispatch、回执与门禁 | 复制一套云/主机执行器；Pipeline 不是新增资源 owner |
| Vault 管理边界 | auth role/policy、秘密签发、轮换与吊销 | 通过 KV 名称替代实际 IAM 或数据库权限 |

### 4.1 授权配置链

GitOps 声明 → 合同校验 → IaC render/plan → 管理审批 → 增量 IAM apply → 精确身份及权限验证 → 脱敏回执。

现有 `bootstrap → account → resources → summary` 可承载授权配置；普通 CMDB 变更不隐式执行 bootstrap。云 trust/IAM 归 IaC，Vault role/policy 由独立受保护管理流程应用，数据库权限归 Playbooks。

### 4.2 日常采集链

范围校验 → 采集身份解析/核验 → 并行只读 provider API → 脱敏 observations/回执 → 验证与幂等入库 → Grafana/覆盖报告。

采集入口禁止 Terraform apply/destroy、bootstrap reconcile、DNS 写入、实例启停、SSH 和探针安装。不加载 Terraform backend 凭据。云 reader 与数据库最小 writer 分开授权；发现资源不产生任何管理授权。

## 5. IaC 现有模块复用与改造清单

| 现有组件 | 源码行为 | 目标改造 |
| --- | --- | --- |
| GCP `modules/iam` | 独立 `google_project_iam_member` 授权 | 复用增量授权；新增 reader/operator/admin 的明确策略绑定 |
| GCP `modules/identity` | deployer SA、GitHub WIF，固定 Run/Artifact Registry 管理能力 | 不将 deployer 用于 reader；新增可参数化的专用 workload identity 能力，保持旧模块兼容 |
| AWS `modules/iam` | role、传入 trust、managed policy attachments | 复用角色骨架；声明专用 reader/operator/admin 策略，缺少 custom policy 支持时在 owner 补齐 |
| AWS bootstrap identity | 部署 role 附加 AdministratorAccess | 不用于 CMDB 采集，不按角色名称推断只读 |
| `unified/auth.py` | 读取旧字段、无条件读取 state、CI JWT 登录 | 抽取基础能力，新增采集 resolver；不能直接复用完整部署 resolver |
| GCP runtime identity 验证 | 部署 UAT 路径要求不能访问 PROD | 为 Shared 全范围采集新增 verifier，保留原部署隔离检查 |
| `publish-runtime` | bootstrap 专用、固定旧路径/字段 | 不用于 CMDB 新路径发布；本阶段不新增 Vault writer |
| `cmdb_collect_scope.py` | GCP Compute/Cloud Run，metadata/gcloud，不消费 identity_ref | 接入认证方式、预期 principal、身份引用及其他 adapters |
| 既有 observations 与 receipt | 原生身份、成功/部分/失败、scope 完整性 | 复用、版本化扩展，补足权限合同与采集范围证据 |

规划新增逻辑组件为 `ResourceAccessContract`、`CMDBIdentityBinding`、`cmdb_identity_resolver` 和 `iac-cmdb-collect`，均为建议接口，不是已存在的目录或命令。

新 env 必须遵循仓库约束：GitOps YAML 为人工入口，Python/Jinja2 展开显式 Terraform 块，env 不使用 HCL 循环。授权标识应以稳定的角色/主体/资源键生成；不能因声明列表重排导致现有绑定撤销或重建。

WIF pool/provider、OIDC provider 和 state 都有唯一 owner；新增 CMDB 身份可引用已审查的信任资源，但不得重复创建同名对象、直接接管已有 state 或扩大旧 deployment trust。复用、import、迁移均需单独计划。

## 6. 版本化非秘密声明合同

每个资源/服务的权限合同必须包含以下信息：

| 字段组 | 必填信息 |
| --- | --- |
| 目标身份 | 逻辑项目、scope、provider、原生 account/project、资源/服务稳定标识 |
| 三档权限 | reader/operator/admin 能力、明确禁止项、provider policy 映射、原生支持程度 |
| 主体绑定 | workforce/workload 类型、预期 principal、用途、认证方式、精确 identity_ref |
| 执行约束 | 允许操作、账号与区域范围、审批、TTL/会话期限、owner/版本 |
| Vault 定位 | vault_cluster_ref、auth mount/role 引用；不能仅从 KV scope 推断集群 |
| 验证 | 正向/负向测试、授权证据、例外到期、回退条件 |

采集 scope 必须另包含 resource kind、region 策略、分页、超时、并发、freshness、expected scope catalogue、writer 引用及 schedule 开关。

`identity_ref` 统一采用逻辑 KV 路径，由专用 resolver 转换 API 路径一次；禁止双重插入 `/data/`、任意路径覆盖或静默回退到旧/admin 身份。`cloud_audience` 与 `vault_audience` 分开，旧字段 `audience` 只能在明确版本的适配器中解释。

非秘密声明只描述配置与授权，不保存密码、token、STS credentials 或服务账号私钥。示例中的占位 account、region、principal 必须经声明和 API 核验，不能作为默认有效值。

## 7. Vault 路径、字段与最小访问规范

### 7.1 路径规则

采用 `kv/<scope>/<project>/<category>/.../<record>`，本方案逻辑项目为 `svc.plus`。scope 表示记录归属，不表示调用者执行环境。云资源记录按其来源 scope、原生 account/project 分开；CMDB 数据库记录归 Shared。

KV v2 逻辑路径 `kv/shared/svc.plus/services/observability/database/cmdb/reader` 的读取 API 路径为 `kv/data/shared/svc.plus/services/observability/database/cmdb/reader`。metadata 使用 `/metadata/`；常驻消费者默认不获得 list 权限。

`cmdb-readonly` 是用途记录，映射 `access_profile=reader`。业务/管理员用途必须独立声明、绑定和授权，不能把一个 token 复制到三个不同名称的记录就视为权限分离。联邦绑定为非秘密元数据，可保留 Vault 合同引用；issuer/trust/permission 声明仍由 GitOps/IaC 管理。

### 7.2 云身份路径与字段

| 用途 | 逻辑路径 | 字段合同与约束 |
| --- | --- | --- |
| GCP 只读联邦 | `kv/<scope>/svc.plus/cloud/gcp/<project-id>/federation/cmdb-readonly` | `project_id`、`service_account_email`、`workload_identity_provider`、`cloud_audience`；仅联邦方式要求 WIF 字段，不存私钥/access token |
| AWS 只读联邦 | `kv/<scope>/svc.plus/cloud/aws/<12-digit-account-id>/federation/cmdb-readonly` | `account_id`、`role_arn`、`cloud_audience`；只有实际采用 OIDC 时要求 audience；Vault AssumeRole 增加精确签发引用 |
| Linode API | `kv/<scope>/svc.plus/cloud/linode/<account-id>/api/cmdb-readonly` | `account_id`、`token`；账号标识映射与读取能力必须实际验证 |
| UCloud 轻量产品 API | `kv/<scope>/svc.plus/cloud/ucloud/<project-id>/api/cmdb-readonly` | `project_id`、`public_key`、`private_key`；不能复用未证实只读的写入 key |
| Cloudflare API | `kv/<scope>/svc.plus/cloud/cloudflare/<account-id>/api/cmdb-readonly` | `account_id`、`api_token`；限定目标 account 和所需产品读取能力 |
| Supabase 管理 API | `kv/<scope>/svc.plus/cloud/supabase/<organization-id>/api/cmdb-readonly` | `organization_id`、`management_token`；核实产品授权能力，不以数据库 service_role key 替代 |

GCP 必须分别声明 `open-platform-shared`、`open-platform-shared-510113`、确认后的 UAT 项目和 `open-platform-prod`。没有已确认 UAT project ID 时保持 pending，不能猜测项目名称。UCloud TW/PH 的原生 region 代码及产品 endpoint 放 GitOps，以实际 API 合同核实。

GCE metadata 模式由 workload 绑定声明提供 project、预期 SA 和授权范围；无需为了满足联邦路径字段而伪造 WIF provider。跨范围授权仅允许核实后的精确 reader 能力。

### 7.3 数据库与服务路径

| 用途 | 逻辑路径 | 字段/权限 |
| --- | --- | --- |
| CMDB 迁移 | `kv/shared/svc.plus/services/observability/database/cmdb/migrator` | `host`、`port`、`database`、`username`、`password`、`sslmode`、`ca_ref`；仅受保护迁移流程 |
| CMDB 写入 | `kv/shared/svc.plus/services/observability/database/cmdb/writer` | 同连接字段；指定表 SELECT/INSERT/UPDATE 和必要 sequence 权限 |
| Grafana 查询 | `kv/shared/svc.plus/services/observability/database/cmdb/reader` | 同连接字段；只读脱敏视图 |
| 审计查询 | `kv/shared/svc.plus/services/observability/database/cmdb/auditor` | 同连接字段；限定历史与回执视图 |
| 备份读取 | `kv/shared/svc.plus/services/observability/database/cmdb/backup` | 同连接字段；经数据库 owner 评审，不复用 migrator |
| 监控认证 | `kv/<scope>/svc.plus/services/observability/integrations/remote-write/<binding>` | `metrics_username`、`metrics_password`、`logs_username`、`logs_password`；consumer 字段适配，endpoint 在 GitOps |
| 精确 SSH | `kv/<scope>/svc.plus/hosts/<provider-native-node-ref>/ssh/<user>` | 必要时 `private_key`、审核后的 `known_hosts`；GCP 优先 OS Login；node ref 采用稳定、安全编码 |

通用服务可声明 `services/<service>/access/<reader|operator|admin>` 用途记录，但不是强制秘密存储：动态身份仅保存必要引用，不创建无意义的静态密码。账户绑定和 group membership 不由秘密值隐式决定。

主机初始化在 GitOps 声明实名用户/工作负载、UID/GID、三档组映射、登录方式、允许服务及 SSH 引用；不能在 KV 创建共享 root 密码作为三档身份。PostgreSQL/Supabase 的 SQL 登录材料沿用 `kv/<scope>/svc.plus/services/<service>/database/<database-binding>/<principal>`，database-binding 必须唯一关联 provider/project、实际数据库和目标 endpoint；Supabase 不同项目都使用数据库名 postgres 时，不能因此复用同一绑定。权限组 NOLOGIN，不创建密码记录；各个 LOGIN principal 独立交付，禁止三档共享同一 DSN。

### 7.4 消费者 ACL

| 消费者 | 最小材料 | 不应获得 |
| --- | --- | --- |
| Collector | 已确认 provider 的精确身份记录、CMDB writer；动态签发时另给精确签发 endpoint 能力 | migrator/admin、Terraform state、SSH、remote-write、跨环境通配 read/list |
| Grafana | CMDB reader | writer/migrator、云 token、全部 Vault secret |
| 审计任务 | auditor | 修改业务数据、删除独立审计证据 |
| 迁移流程 | migrator，限定目标与窗口 | 常驻分发给 collector 或 Grafana |
| 备份任务 | backup 与精确备份目的地能力 | 常驻恢复/清库能力 |
| 探针部署 | 精确 SSH 与对应 remote-write binding | 复用 CMDB collector 的整套身份 |

禁止 `kv/data/*`、整棵 `shared/*` 和跨环境通配读取。管理写入/轮换身份独立；常驻 consumer 不修改授权或轮换他人凭据。自身 Token/lease 的续期与清理按认证机制单独限定，不能据此获得全局吊销权限。

## 8. 运行时认证与凭据交付

### 8.1 GitHub Actions

CI 分别取得面向 Vault 与云厂商的 JWT，不能混用 audience。Vault JWT role 绑定实际仓库、受保护 workflow、ref/environment；云 trust 校验相应 issuer、audience、subject/允许的 claims。不能仅校验来自 GitHub 就接受全部仓库或工作流。[Vault JWT 认证规则](https://developer.hashicorp.com/vault/docs/auth/jwt)。

CI 使用与目标能力匹配的短期 reader/operator/admin 会话；采集路径无 state/backend 权限。旧 `deploy_service_account`、`gcp_workload_identity_provider`、`gcp_oidc_audience` 由显式旧版本适配器转换，不在新合同继续混用部署语义。

### 8.2 Shared 主机

GCP API 优先使用附着的运行时 SA；如需 impersonation，只对精确目标 SA 授权，并审查其最终能力。不得为了 reader 查询授予项目级任意 SA impersonation。

Vault 访问可采用 GCE instance identity JWT 与 GCP auth，约束 project、SA、zone、标签等；metadata OAuth access token 与 Vault 登录 JWT 不是同一种凭据。Vault 服务端核验实例的云权限也应独立评审。[Vault GCP auth](https://developer.hashicorp.com/vault/docs/auth/gcp)。

同主机上的工作负载可能共享 metadata 身份。必须审查容器/进程隔离、metadata 访问、凭据挂载、UID/GID 和允许出口；单纯 root-owned 0600 文件不能证明服务之间身份隔离。

AWS 在 Shared 主机不能依赖 GitHub Actions OIDC 运行时。建议评估 Vault 短期 AssumeRole；IaC 创建目标 role/policy/trust，Vault 签发方必须具备真实 AWS 身份与精确 AssumeRole 能力。KV 中的 role_arn 本身不能签发凭据。此签发配置属于后续独立授权工作，不随本文创建。[Vault AWS secrets engine](https://developer.hashicorp.com/vault/docs/secrets/aws)。

### 8.3 交付与轮换

优先短期凭据、按需签发与受控文件交付。材料使用专用 UID 或 root-owned 0600 文件，父目录受限；不得为非 root consumer 将权限改成 world-readable。短期环境注入仅限必要进程及生命周期。

禁止打印 JWT、Token、DSN、密码、私钥；禁止使用 env/set 展示秘密，禁止把秘密置于 CLI 参数、inventory、Git、公开 receipt 或构建 artifact。环境注入或 sensitive 标志均不能替代泄漏审查。

秘密不通过普通 Terraform data/resource/output 持久化进 state；`sensitive` 隐藏显示但仍可能保存在 state/plan。是否可用 ephemeral/write-only 必须核实 Terraform/provider 版本和字段支持，不能默认现有工具链具备。[Terraform 敏感数据规范](https://developer.hashicorp.com/terraform/language/manage-sensitive-data)。

轮换必须验证 consumer 重载、连接恢复与旧材料退出；短期租约过期后重新取得材料，不能无限缓存。已失效或已吊销凭据不能通过切回旧文件恢复服务。

### 8.4 初始化主机 OS 用户的三档能力

每台新增、重装或接管的主机必须声明 OS reader/operator/admin 能力组，并绑定实名登录用户或独立工作负载用户。组名可带服务/节点前缀，不强制创建三个共享登录账号。现有云镜像默认用户、OS Login 与其他 sudoers 来源必须一并审核，不能只看新建用户。

| OS 能力 | reader：只读 | operator：业务操作 | admin：管理员 |
| --- | --- | --- | --- |
| 状态与日志 | 精确状态查询及脱敏日志；不开放全部 journal/进程环境 | 目标业务服务排障材料 | 管理范围内完整诊断，仍保护秘密 |
| 登录方式 | 严格只读采用受限查询入口；无登录需求用 nologin | 实名登录或受限操作入口，不使用 root 登录 | 实名登录，经批准临时提权；应急 root 单独托管 |
| 文件与配置 | 不能修改业务文件、服务配置、凭据、用户/key 或授权 | 仅指定业务工作目录与经批准配置；无任意系统路径写入 | 目标主机系统与服务管理，受保护变更 |
| 服务控制 | 禁止 restart/reload/start/stop、部署或信号操作 | 仅批准的服务与动作 | 可管理主机服务及生命周期 |
| sudo/运行身份 | 无通用 sudo 或高权限组 | 精确动作 wrapper/RunAs，无任意 sudo、shell、解释器、编辑器 | 管理任务按需 root 权限；不能伪称仍受普通文件 ACL 限制 |
| 系统与账号 | 禁止软件安装、网络变更、账号/组/key 管理 | 同样禁止；不得拥有通用 Docker socket 或其他提权通路 | 包、网络、用户、组及安全配置管理 |

普通 Linux 用户没有 sudo，不等于主机严格只读：它仍可能写 home/tmp、执行代码或修改有写权限的文件。若 reader 的合同要求只查询，必须使用无通用 shell/SFTP 上传能力的查询入口，并检查转发、PTY、用户 rc 和其他会话通路；需要可写分析工作区的用户应明确登记为受限分析例外，不标成严格 OS reader。

SSH 受限入口可评估 Match/ForceCommand，并显式禁用不需要的 TCP/agent/socket/X11 转发、用户 rc 和 PTY。ForceCommand 本身不会关闭转发；规则需按实际 OpenSSH 版本与 OS Login 的兼容性核实。[OpenSSH sshd_config](https://man.openbsd.org/sshd_config)。

reader 的查询工具必须无 pager/editor/shell escape，不回传秘密或任意路径内容。operator 特权 wrapper 及其父目录、unit、依赖脚本和高权限 EnvironmentFile 不能由 operator 任意改写；严格校验参数与服务名，不执行用户拼接的 shell 命令。业务配置若可加载代码或改变执行身份，必须改走独立受控发布，不以可写配置绕过提权边界。

初始化由 Playbooks 执行：先盘点镜像用户、UID/GID、组与有效 sudo/SSH 配置，声明冲突先停止；再建立能力组/实名绑定、服务系统用户、目录 ACL 和精确动作；检查配置语法，测试登录和正反例；最后受控退出多余默认权限。禁止在新管理入口验证前删除唯一可用身份。变更回执记录用户/组/动作及来源摘要，不含私钥、密码或完整敏感日志。

OS 三档角色不自动带来云 IAM、Vault 或 PostgreSQL 管理权限。应用进程使用独立、默认无交互登录的服务 UID；检查进程环境、文件挂载、metadata 和数据库 socket 是否形成跨层提权。

## 9. PostgreSQL、Supabase 初始化与 Grafana 权限映射

### 9.1 PostgreSQL 通用用户/角色初始化

每个新数据库或新服务 schema 的初始化必须声明 `<service>_reader`、`<service>_operator`、`<service>_admin` 权限组及独立 LOGIN principal；能力组建议 NOLOGIN，对象 owner 单独 NOLOGIN。角色命名包含服务/绑定上下文，避免多个数据库把同名角色误当作各自独立用户。

| SQL 能力组 | 允许 | 禁止/隔离 |
| --- | --- | --- |
| reader | 目标数据库 CONNECT、必要 schema USAGE、批准表/列或脱敏视图 SELECT | DML、DDL、sequence nextval/setval、角色管理、绕过 RLS、可写函数/程序入口 |
| operator | reader 能力加指定表 INSERT/UPDATE、必要 sequence 权限；DELETE 仅按业务合同另批 | 默认无 DELETE/TRUNCATE、对象所有权、DDL、GRANT OPTION、角色管理、REPLICATION/BYPASSRLS |
| admin | 受保护会话内管理目标对象、迁移、授权及恢复，按明确 owner/管理委托实施 | 不默认赋予整个 cluster SUPERUSER/CREATEDB/CREATEROLE；托管产品不支持的权限明确登记 |

reader/operator 登录身份必须检查 NOSUPERUSER、NOCREATEDB、NOCREATEROLE、NOREPLICATION、NOBYPASSRLS；审查所有 membership 和 SET ROLE 通路，不能继承或切换到 admin/owner。NOINHERIT 不是单独的防提权证明。PostgreSQL 角色是 cluster 级对象，CREATEROLE/CREATEDB 不是限定在某一个数据库内的权限；创建/委托角色由受保护平台管理身份执行，不下放给普通业务 admin。[PostgreSQL CREATE ROLE](https://www.postgresql.org/docs/current/sql-createrole.html)。

授权同时覆盖 database、schema、表/列、视图、sequence、函数与对象所有权；审查 PUBLIC、TEMP/CREATE、可写 schema/search_path 和 SECURITY DEFINER。对生产共享库的 PUBLIC 权限调整必须先做影响分析，不能全局回收造成其他服务失效。reader 可设默认只读事务作为防误操作，但真实边界来自 ACL/RLS，不能只设置 `default_transaction_read_only` 就认定只读。[事务默认值](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-DEFAULT-TRANSACTION-READ-ONLY)。

已有对象显式授权，新对象针对实际创建者设置 default privileges；迁移使用另一个 creator 时必须覆盖它的规则。默认权限不是已存在对象的补授权，不能用未核实的 ALL TABLES 覆盖整个业务库。[ALTER DEFAULT PRIVILEGES](https://www.postgresql.org/docs/current/sql-alterdefaultprivileges.html)。

数据库 admin 的对象所有权可能绕过 RLS，必须把跨租户读取能力列为管理风险，而不是宣称 owner 仍与业务用户一样受限。reader/operator 不得持有 owner、BYPASSRLS、服务器文件读取/写入或程序执行角色；连接、角色成员、查询超时及有效授权均进入验收。[PostgreSQL RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)。

### 9.2 Supabase 用户与角色初始化

Supabase 同样必须满足三档目标能力，但必须区分以下层次，不能把一个层次的 admin 当作其他层次的管理员：

| 层次 | 三档实现与边界 |
| --- | --- |
| 数据库直接连接 | 按第 9.1 节建立专用 SQL 权限组与 LOGIN principal，核验 direct/session/transaction pooler 的实际 current_user/session_user |
| 应用用户与 Data API | 每个 Auth 用户的服务端可信成员关系映射 reader/operator/admin，结合 SQL grants、RLS 和受控后端接口；不为每个 Auth 用户创建数据库登录 |
| 项目/组织控制面 | 使用产品实际支持的成员角色和管理 API 身份，单独验证其能力；应用 admin 不自动获得 Dashboard、SQL Editor、组织或平台管理权 |

业务数据对象初始化时必须同步批准的 grants/RLS：reader 只读获准数据，operator 仅指定业务写入且不跨租户，应用 admin 的租户/服务管理范围也必须明确。Supabase 内置 anon/authenticated/service_role 等角色不直接等同于本文三档；初始化不得改名、接管或批量重置平台角色及 auth/storage 等受管 schema。[Supabase Postgres roles](https://supabase.com/docs/guides/database/postgres/roles)。

`service_role` 或通过该角色授权的秘密 API key 具有 RLS 绕过能力，不能作为普通 reader/operator 或直接发给客户端的应用 admin 身份。应用角色来自服务端可信授权记录/claims，不能信任用户可编辑的 metadata 自行提权；视图、函数/RPC 及其他暴露接口同样需要检查行/列边界。[Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security)。

托管 Supabase 的 admin 只具备产品允许的项目/数据库管理能力，不承诺底层真实 superuser、宿主 OS root 或无限平台操作。自托管 Supabase 的主机 OS 管理依第 8.4 节，数据库管理依第 9.1 节分别初始化；保留产品内部必需身份，禁止将其登录凭据交给日常业务用户。[Supabase superuser 与操作限制](https://supabase.com/docs/guides/database/postgres/roles-superuser)。

### 9.3 初始化顺序与放行门禁

1. 固定目标主机/数据库/Supabase project、版本、owner、服务 schema 与全部既有身份。现有角色名称碰撞、未知成员/权限或云托管能力不明时停止，不强行接管。
2. 明确创建三档能力组/角色与实名或工作负载绑定；owner/迁移/恢复身份独立，运行时凭据使用不同引用，不生成共享默认密码。
3. 初始化 OS ACL/SSH/精确 sudo 动作；数据库 ACL/default privileges/RLS、连接网络及 TLS；Supabase 的 API grants、可信应用成员关系和控制面授权分别验证。
4. 使用各档真实身份完成允许/拒绝测试，reader/operator 不使用 admin 代测。对生产的破坏性负例只采用权限评估、隔离演练或经批准的无副作用检查。
5. 输出脱敏初始化回执，绑定主机原生 ID、database/project、principal、版本、有效权限摘要和测试结果；只有三档合同全部通过或具有明确未放行例外，才允许普通服务部署。
6. 后续 deploy/probe 只检查准备状态，不隐式创建用户、补全权限或重置密码；restore、镜像重装、schema 迁移和角色轮换后重新核验新旧对象与三档能力，过期的 admin 会话及现有连接按生命周期机制退出。

Playbooks 负责 OS/自管 PostgreSQL/Supabase 服务内部初始化与迁移；托管产品支持的控制面身份/角色配置由对应 IaC adapter 管理。不能因为模块名为 database provision 就把 OS 用户初始化或受管平台角色修改交给 Terraform。

### 9.4 CMDB 特化角色与 Grafana

| 数据库 principal | 权限档位 | 约束 |
| --- | --- | --- |
| cmdb_reader | reader | CONNECT、必要 schema USAGE、脱敏视图 SELECT，无写入、DDL、角色管理 |
| cmdb_auditor | reader 特化 | 经授权的历史/采集回执视图，不因此获得原始敏感字段 |
| cmdb_writer | operator 特化 | 指定表 SELECT/INSERT/UPDATE、必要 sequences；无 DDL、DELETE、角色管理或跨业务库权限 |
| cmdb_migrator | admin 特化 | 受保护窗口内目标 schema 迁移；不得授予 cluster superuser 作为默认实现 |
| cmdb_owner | 对象所有权 | NOLOGIN，不作为常驻客户端 |
| cmdb_backup | 独立备份职责 | 所需读取、工具/对象权限经评审；恢复使用独立受保护身份 |

Vault ACL、网络访问和 PostgreSQL GRANT 三层均必须通过。检查 PUBLIC/default privileges、owner inheritance、SECURITY DEFINER、视图及新对象权限，不能仅验证一次 UPDATE 被拒绝就认定全部权限完整。

远程数据库采用 TLS、CA 与主机名验证；`ca_ref` 必须解析为实际受信 CA，不能因字段存在就宣称 TLS 已完成。Docker 私网连接与远程 TLS 发布分别验收；不开放公网 5432。

第一阶段可采用精确 KV 静态凭据，但必须明确唯一秘密来源和轮换流程。后续可评估 PostgreSQL secrets engine 的动态 writer、static reader；动态凭据从 `database/creds/<role>` 获取，不复制回 KV。Grafana static role 轮换需验证 datasource 更新和连接恢复；rootless 静态轮换属于 Enterprise 能力，不能默认可用。[Vault PostgreSQL 插件](https://developer.hashicorp.com/vault/docs/secrets/databases/postgresql)。

现有 Grafana 首页 `default-home-dashboard` 为目标展示入口。读取资源来源 scope/provider/region、采集健康和 freshness；Grafana 应用侧 viewer/editor/admin 与 PG reader 是独立授权层，不因编辑 dashboard 就取得数据库 writer。

## 10. 全量资源采集、归一化与审计

全量指已登记组织/账号 × Shared/UAT/PROD × 产品/资源种类 × 区域/全局范围的完整覆盖，不只统计当前 RUNNING 主机。账号与区域发现需经授权配置；API 可见性不等于完整组织资产范围。

| Provider | 首批能力与后续范围 |
| --- | --- |
| GCP | Compute 全状态、Cloud Run；磁盘、网络、托管数据库等按产品能力清单逐项接入 |
| AWS | EC2 与区域分页；其他服务按 adapter 和精确权限逐项接入 |
| Linode | 实例、账号与 region；其他产品按能力清单接入 |
| UCloud | TW/PH 轻量产品优先；不能以 UHost 查询证明轻量产品完整 |
| Cloudflare | Workers/Pages 服务及部署关系；路由、revision 不重复计为服务 |
| Supabase | organization/project 与托管数据库关系；避免重复计数 |

每个范围必须记录 enabled、supported、expected catalogue、实际 account/project、region、分页完成、时间、成功/部分/失败、数量及脱敏错误。只有全部目标范围成功才能宣称平台全量覆盖；unsupported/pending 也必须进入覆盖报告，不能被从分母删除。

复用 `cmdb.observations.v1` 与原生唯一键 `(provider, account_ref, project_ref, resource_kind, native_resource_id)`。保留原始 provider 状态、scope、source、observed_at、owner SHA；IP/名称不是资源身份。

raw snapshots 必须经字段 allowlist 脱敏，不保存完整 provider 响应、环境变量值、user data、启动脚本或秘密。除敏感键检测外还需检查自由文本泄漏；公开证据仅含核验所需最小信息，PROD 资产明细按受控数据处理。

403、API 未启用、限速、网络/分页失败记录 unknown/partial，不能写成成功零资源；保留最近成功观察。只有范围完整采集及独立删除确认满足合同才能更新退役状态。入库采用幂等 run ID、事务/锁、内容 hash 和时间顺序保护。

采集 receipt 与数据库 ingestion receipt 分开，关联同一 run/correlation、GitOps SHA、IaC SHA、Playbooks SHA、目标/范围、输入 hash 和迁移版本。定时主机执行也生成独立 run ID，不假造 GitHub run/attempt。

三档权限的目标绑定、实际核验、例外与最后测试时间应进入非秘密授权审计记录，desired 与 observed 分开。发现权限漂移只告警，不由 reader 自动修复 IAM。审计保留与清理使用独立审批，不由资源管理员随意删除。

## 11. 实施批次、迁移与回退

| 阶段 | 交付物 | 放行条件 |
| --- | --- | --- |
| P0 合同 | 三档能力矩阵、Shared 架构、原生账号、KV 字段版本、产品覆盖清单 | 无未知默认账号，无秘密值；旧目标差异已登记 |
| P1 IaC owner | 云账号三档 profile、增量 IAM、专用 workload identity、采集 resolver/verifier、独立 collect 入口 | 离线正反例、render/validate/plan；无现有资源替换/销毁，无部署 admin fallback |
| P2 独立授权 | 经批准的云 IAM 与 Vault auth/ACL/凭据交付 | 精确主体/路径生效、错误主体拒绝；本文未授权执行此阶段 |
| P3 Shared GCP 闭环 | OS 三档初始化、GCP collector、自建 Observability/CMDB 服务三档、Playbooks 入库、PG 三档/特化、Grafana 查询 | 云/OS/服务/数据库四类身份初始化门禁、同 run 原生 ID/计数对账、重放与角色边界通过 |
| P4 多云覆盖 | AWS/Linode/UCloud/Cloudflare/Supabase adapters | 分页/区域/产品权限与身份验证；不支持项透明报告 |
| P5 常驻启用 | Agent、采集定时服务、资源预算、freshness 告警、备份恢复 | 凭据失效/轮换、失败隔离、持续采集、隔离恢复演练通过 |
| P6 普及三档权限 | 各云账号、主机 OS、PostgreSQL/Supabase 与自建服务合同、实名/工作负载绑定 | 三层初始化及恢复后均有三档验收与漂移审计，缺口保持未放行 |

按 owner 实现 → 固定 SHA caller → 合同/真实环境验证 → 旧副本退休推进。当前文档不会创建或补全 bootstrap 脚本；日后 Vault 管理应用需另行明确范围和授权，不能被日常采集隐式触发。

### 11.1 旧 UAT 路径迁移

1. 固定实际 Shared 主机、数据库/volume、连接用户、consumer 和新旧引用清单。
2. 在受保护管理流程中准备 Shared 引用及最小权限；只检查新 consumer，不复制密码到文档/PR。
3. 备份并验证新 reader/writer；固定版本切换，记录数据源 UID 和定时任务引用。
4. 验证权限、数据与连接恢复，轮换或退出旧凭据。回退只使用仍有效且经审查的材料。
5. 单独批准旧记录、policy 或旧 executor 的清理；禁止随路径改名销毁数据库、重建 volume 或改写历史来源 scope。

### 11.2 不影响生产的验证原则

先验证离线合同、增量 plan 和隔离目标；线上只读身份使用 list/get 等获准能力。越权负例优先使用 policy simulation、合同测试及隔离演练，不对生产实例执行真实重启/删除作为测试。跨环境采集不自动开启生产 API、修改生产网络或扩大管理员授权。

Shared 接入前确认同主机现有服务健康、备份、资源预算和回退；任何数据库迁移、Agent 配置及重载都通过精确目标流程。数据库 schema 演练不能污染生产业务库。

## 12. 验收与当前未完成事项

| 验收项 | 必须证明 |
| --- | --- |
| reader | 可读授权范围；不可写、重启、部署、修改 IAM、读取无关秘密 |
| operator | 日常允许操作成功；role/pass/身份替换、权限管理、无关数据访问被拒绝 |
| admin | 仅明确目标管理能力；审批/TTL/审计有效，无普通流程隐式提权 |
| 云账号层 | reader/operator/admin 分别通过资源读、限定业务操作、目标账号管理测试；云 IAM/跨账号/组织级边界单独验证 |
| OS 初始化 | reader 无通用写入/控制入口；operator 仅精确服务动作；sudo/组/socket/unit/metadata 无未审查提权路径；新管理入口验证后才退出旧入口 |
| 自建服务层 | reader 查询/分析无写入；operator 仅业务 allowlist；admin 能管理服务但不获得底层 OS/云/Vault root；跨租户与任意代码路径被拒 |
| PostgreSQL 初始化 | 各档真实身份连接正确；reader DML/sequence 变更被拒，operator DDL/角色管理/SET ROLE 提权被拒；新对象默认权限和恢复后 ACL 均正确 |
| Supabase 初始化 | SQL、Auth/Data API、控制面角色分别核验；reader 写入与 operator 跨租户访问被拒；应用 admin 不持有 service_role/client secret，也不自动拥有组织管理权 |
| 联邦/Vault | 错 issuer/audience/repo/workflow/ref/principal/account 被拒绝；准确匹配 claims |
| Shared 架构 | execution/storage 均为 shared；来源 scope 不变，两个 Shared project 不合并 |
| 云与数据库分权 | Collector 云 reader + 最小 writer；Grafana 无 writer；migrator 不常驻 |
| 覆盖完整性 | 全部登记 scope/product/region 的结果可核验；失败/pending 不变成零库存 |
| 数据安全 | 快照和回执脱敏；旧 run 不覆盖新 run；变更重放被拒绝或按合同处理 |
| 持续运行 | 短期凭据更新、过期拒绝、轮换后恢复、并发/限速/数据库故障可控 |
| 恢复 | 隔离恢复演练、版本校验、最后有效 run 与查询恢复；无业务库影响 |

源码基线已具备 GCP 部分采集和 observations 合同；尚需 Shared 声明/数据库引用对齐、identity_ref 真实消费、云账号/OS/PostgreSQL/Supabase/自建服务三层初始化、Vault live 授权、其他 provider adapters、全范围采集和持续运行验收。本次没有创建或验证实际用户/角色。

每项完成必须记录精确 PR/commit、环境、目标、运行及证据，区分设计、静态检查、CI、merge、部署与 live acceptance。本文不能作为“权限已应用”“全量已采集”或“11 台探针已部署”的证据。

### 12.4 2026-10-28 落地进展：Infrastructure-MCP-Server CMDB 与只读安全网关交付

2026-10-28 期间，团队在 `ai-workspace-infra/Infrastructure-MCP-Server` 仓库中完成了 CMDB 动态对账引擎、安全受控 CLI 驱动与集中式可观测性网关的实现与交付，并通过 GitHub [PR #4](https://github.com/ai-workspace-infra/Infrastructure-MCP-Server/pull/4) 合并至 `main`（提交基线 `36f7441`）：

1. **CMDB 动态对账与多云资产收敛**：
   * 实现了 `infra.cmdb.summary`、`infra.cmdb.query`、`infra.cmdb.sync` 三项核心资产工具。
   * 建立了规范的 `Resource`、`ServiceStatus` 与 `EnvironmentSummary` 数据模型，支持 SIT（100% selfhost standby 待命）、UAT（Akamai Linode `45.79.175.119` + Vultr `167.179.105.137` + GCP Serverless 混合）与 PROD（GCP `34.81.174.112` + AWS Tokyo `43.207.194.92` + Vultr K3s + Cloudflare Edge）资产自动对账。
2. **只读三档权限落地（Safe CLI Guardrails）**：
   * 通过 `infra.cli.exec` 实现受控云/运维工具调用，限制命令白名单（`linode-cli`, `aws`, `gcloud`, `gh`, `curl`, `jq`）。
   * 严格实施只读 `reader` 边界，强行阻断包含 `delete`, `destroy`, `drop`, `rm`, `create`, `apply`, `push`, `write` 等任何变更动词，以及非 GET/HEAD 的 `curl` 动作。
3. **Environment Graph 15 依赖边图拓扑联动**：
   * 支持通过 `infra.cmdb.query` 传入 `node_id: "service/observability-gateway"` 进行一阶子图抽取，精确对应上游 6 条编排/凭据边与下游 9 条遥测/MCP 暴露边。
   * 对应全景规范见《[Infrastructure-MCP-Server 部署、集中式可观测性、CMDB 与 QMD 记忆系统交付全景技术规范](infrastructure-mcp-observability-cmdb-qmd-delivery-spec.zh.md)》。

## 13. 来源与维护

### 13.1 固定源码证据

- [GCP IAM 增量成员模块](https://github.com/ai-workspace-infra/iac_modules/blob/4dab50df81eceb58b4b31b46a2ba7404d70ad6cf/terraform-hcl-standard/gcp-cloud/modules/iam/main.tf)。
- [GCP deployment identity 与固定管理权限](https://github.com/ai-workspace-infra/iac_modules/blob/4dab50df81eceb58b4b31b46a2ba7404d70ad6cf/terraform-hcl-standard/gcp-cloud/modules/identity/main.tf)。
- [AWS IAM role 模块](https://github.com/ai-workspace-infra/iac_modules/blob/4dab50df81eceb58b4b31b46a2ba7404d70ad6cf/terraform-hcl-standard/aws-cloud/modules/iam/main.tf)、[AWS bootstrap deployment identity](https://github.com/ai-workspace-infra/iac_modules/blob/4dab50df81eceb58b4b31b46a2ba7404d70ad6cf/terraform-hcl-standard/aws-cloud/bootstrap/identity/main.tf)。
- [现有部署认证与 UAT/PROD 检查](https://github.com/ai-workspace-infra/iac_modules/blob/4dab50df81eceb58b4b31b46a2ba7404d70ad6cf/scripts/pipeline/unified/auth.py)、[bootstrap 专用发布入口](https://github.com/ai-workspace-infra/iac_modules/blob/4dab50df81eceb58b4b31b46a2ba7404d70ad6cf/scripts/pipeline/unified_cli.py)。
- [GCP scope collector](https://github.com/ai-workspace-infra/iac_modules/blob/4dab50df81eceb58b4b31b46a2ba7404d70ad6cf/terraform-hcl-standard/scripts/cmdb_collect_scope.py)、[GCP token 获取](https://github.com/ai-workspace-infra/iac_modules/blob/4dab50df81eceb58b4b31b46a2ba7404d70ad6cf/terraform-hcl-standard/scripts/cmdb_collect_gcp.py)。
- [observations.v1 合同](https://github.com/ai-workspace-infra/iac_modules/blob/4dab50df81eceb58b4b31b46a2ba7404d70ad6cf/terraform-hcl-standard/scripts/cmdb_observations_v1.py)、[IaC env 渲染约束](https://github.com/ai-workspace-infra/iac_modules/blob/4dab50df81eceb58b4b31b46a2ba7404d70ad6cf/terraform-hcl-standard/AGENTS.md)。

### 13.2 关联规划

- [多云平台工程技术白皮书](multi-cloud-platform-engineering-whitepaper.zh.md)：本方案沿用其 scope/project/category 路径目标，不代表旧 consumer 已迁移。
- [CMDB 落地规划](multi-cloud-cmdb-postgresql-grafana-plan.zh.md)、[旧 Vault 路径规划](cmdb-vault-paths.zh.md)：架构和路径冲突按第 1.3 节解释，保留历史基准。
- [多云 IaC owner/caller 迁移记录](multi-cloud-iac-cleanup-batches-20261007.zh.md)：复用职责、固定版本和回执机制，不把其只读 dry-run 作为本方案的 live 验收。
- [Shared 历史验证记录](cmdb-shared-uat-evidence-20261009.zh.md)：历史记录的 UAT 命名不是本次 storage_scope 的目标归属。
- [Supabase 专用只读角色、RLS 与受控连接参考](supabase-operations.zh.md)：只读源账号的历史特化合同不等于所有 PostgreSQL/Supabase 用户已完成三档初始化。

官方资料核对日期为 2026-10-10；实际 Vault、Terraform/provider、云 API 版本及许可证在实施前核实。规范变更需同步 GitOps schema、IaC/Playbooks consumer、Toolkit 门禁和验证证据，并重新评审最小授权边界。
