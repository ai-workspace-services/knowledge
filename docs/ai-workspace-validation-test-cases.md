# AI Workspace 架构验证 Test Cases

本文定义 AI Workspace 顶层架构文档的验证方式。验证对象是架构意图、职责边界、Contract 和治理规则，不是实现代码的单元测试。

## 验证分层

| Layer | 验证目标 | 证据 |
|---|---|---|
| Structure | Markdown、标题、表格、Mermaid 可解析 | 静态检查结果 |
| Architecture | 四组织边界与依赖方向正确 | 评审记录、架构矩阵 |
| Contract | Workspace Specification 字段完整且可扩展 | 字段清单、示例、版本记录 |
| Product | GUI/CLI/API 与 Human/Developer/Agent 对齐 | 场景验收记录 |
| Governance | 反模式被识别，变更可追溯 | ADR、Owner、兼容性说明 |
| Roadmap | 阶段目标与 North Star 可度量 | 指标和季度复盘 |

## Test Case 清单

| ID | Test Case | 验证步骤 | 通过标准 |
|---|---|---|---|
| TC-001 | 文档结构完整性 | 检查 H1/H2 层级、代码围栏、表格和 Mermaid 块 | 无未闭合围栏；章节覆盖 Vision、组织、Contract、Lego、接口、路线图和治理 |
| TC-002 | 四组织归属 | 随机抽取一个能力，分别判断属于 Explore/Compose/Connect/Run | 能明确归属；若跨域，存在清晰 Contract，不靠隐式共享实现 |
| TC-003 | Lab 隔离 | 检查生产架构是否直接引用 Lab PoC 或未 Promote 项目 | Lab 只能通过 Standardize/Promote 进入生产；未 Promote 项目可替换或移除 |
| TC-004 | Services 边界 | 检查产品流程是否直接执行主机命令、Ansible 或云厂商 API | Services 只提交 Workspace intent，不直接 shell exec Ansible/SSH |
| TC-005 | Infra 边界 | 检查 Infra 文档和接口是否出现 Plan、Entitlement、SEO 等产品语义 | Infra 只负责 Run；产品计费语义留在 Services |
| TC-006 | XConnect 分类 | 为 AI、Tool、Data、Service 各选一个 Connector | 每个 Connector 有 Contract、Protocol、Adapter 边界；Provider 私有字段不泄漏到核心模型 |
| TC-007 | Workspace Specification | 按字段清单审查 Identity/Profile/Compute/Runtime/AI/Connectors/Tools/Desktop/Storage/Security/Observability | 每个 domain 都能表达目标状态、权限或约束；不绑定具体框架或厂商 |
| TC-008 | Module/Profile 组合 | 用 Module 组合 CLI Only、Tiny Desktop、Standard Desktop 三个 Profile | Profile 是可替换的组合；默认值有适用场景，不成为巨型发行版 |
| TC-009 | 三种消费方式一致性 | 用 GUI、CLI、API 描述同一 Workspace 目标 | 三者共享同一 Domain Model 和 Contract，结果语义一致 |
| TC-010 | Billing 抽象 | 用一次 AI 调用或 GPU 运行追踪 Plan → Entitlement → Usage → Credit → Cost | 能解释能力授权、实际用量、额度扣减和成本归因；不依赖具体支付厂商 |
| TC-011 | Run Anywhere | 用同一 Workspace intent 分别映射 Cloud、Local、Edge | 用户意图不变；仅运行约束、能力可用性和成本策略发生可解释变化 |
| TC-012 | 安全与观测 | 审查 Secret、最小权限、隔离、审计、日志、指标、Tracing 和成本字段 | 每个跨边界操作有权限与审计语义；故障和成本可定位 |
| TC-013 | 版本兼容 | 修改一个 Contract 字段并模拟旧 Consumer | 有版本、兼容窗口、迁移说明和回滚策略；旧 Consumer 不被静默破坏 |
| TC-014 | 生命周期闭环 | 从 Discover 走到 Research、PoC、Evaluate、Standardize、Promote 或 Archive | 每一步有证据、Owner、退出条件；失败实验不会成为生产依赖 |
| TC-015 | North Star 可度量 | 为“从意图到 Ready Workspace”建立一次端到端演练 | 至少记录 Ready 时间、迁移成功率、Connector 健康度、安全事件、成本透明度和任务完成率 |

## 建议验证顺序

1. 先执行 TC-001，确认文档本身可读、可解析。
2. 再执行 TC-002 至 TC-006，确认四组织没有职责漂移。
3. 执行 TC-007 至 TC-011，确认 Contract、Lego 和消费方式能形成闭环。
4. 执行 TC-012 至 TC-014，确认安全、版本和 Lab 生命周期可治理。
5. 最后执行 TC-015，将架构语言转成可持续追踪的 North Star 指标。

## 每次变更的最小验收记录

```text
Change:
Scope:
Affected contracts:
Affected organizations:
Executed test cases:
Evidence:
Compatibility / migration:
Rollback:
Owner:
Decision:
```

## 通过门槛

- TC-001 必须通过。
- TC-002 至 TC-006 不得出现边界冲突或未声明的跨域实现依赖。
- 涉及 Contract、权限、计费或运行环境的变更，必须执行对应的 TC-007、TC-010、TC-011、TC-012、TC-013。
- Roadmap 评审必须至少更新一次 TC-015 的指标证据。
