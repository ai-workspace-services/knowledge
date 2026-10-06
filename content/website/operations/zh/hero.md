---
ui:
  title: 创建发布计划
  subtitle: Daily Main Snapshot
  environment: 选择环境
  environmentHelp: SIT / UAT 使用 Daily；PROD 使用受保护发布流程。
  sitDescription: 系统集成测试环境
  uatDescription: 用户验收测试环境
  prodDescription: 生产环境
  protectedRelease: 受保护发布
  prodHelp: PROD 将切换至受保护 Release 流程；生产发布入口待接入。
  source: 快照来源
  sourceRef: 分支 / 引用
  tag: Snapshot 标签
  autoTag: 留空自动解析不可变 tag
  repositories: 仓库范围
  allRepositories: 全部仓库
  selectedRepositories: 指定仓库
  repositoryHelp: 指定仓库仅构建快照，不执行完整 UAT 部署。
  dataMode: 数据操作模式
  none: 不执行数据操作
  preview: 导入预览
  import: 实际导入
  baseline: Baseline 补齐
  schema: Schema 迁移
  previewNotice: 预览不会写入数据库，也不会继续部署。
  writeNotice: 实际导入会写入目标数据库；需明确源、目标及恢复依据。
  importConfig: 非敏感导入配置 JSON
  advanced: 高级设置（XConnect / Shared）
  schemaExpected: 起始 Schema 版本
  schemaTarget: 目标 Schema 版本
  schemaHash: SQL SHA-256
  oneTag: XConnect One Release tag
  gatewayTag: XConnect Gateway Release tag
  gitopsDefault: 留空沿用 GitOps 声明
  stripe: 请求跳过 Stripe 同步
  stripeHelp: 当前 Hybrid 实际固定跳过 Stripe 目录同步。
  vaultEndpoint: Vault readiness endpoint
  observabilityEndpoint: Observability readiness endpoint
  iamEndpoint: IAM readiness endpoint
  iamIssuer: IAM issuer
  timeout: Readiness 超时（秒）
  plan: 执行计划
  planHelp: 根据当前参数生成，阶段尚未执行。
  planned: 待执行
  validate: 参数校验
  snapshot: 不可变快照
  build: 跨仓库构建
  shared: Shared 只读就绪检查
  deploy: UAT 部署及验证
  protected_release: 受保护 Release 流程
  stopAtPreview: 导入预览后结束
  createPlan: 创建计划
  planning: 正在创建计划
  viewParameters: 查看参数
  executionUnavailable: 执行后端尚未接入；此页仅生成计划，不派发工作流。
  prodUnavailable: 生产发布入口待接入，不能通过 Daily 派发 PROD。
  planCreated: 计划已生成；尚未执行
  validationError: 参数校验失败，请修正后重试。
  releases: 查看发布记录
  recent: 最近发布
  noReleases: 暂无可用发布记录
  releaseUnavailable: 发布记录暂不可用
  loading: 加载中
  evidencePending: 实际验收需查看对应证据
  mcp: AI / MCP 接口
  mcpHelp: 人和 AI 使用相同的参数校验与计划接口。
  mcpScope: 当前提供目录、计划与发布查询；派发工具尚未开放。
---

Portal 平台操作中心的中文界面内容。
