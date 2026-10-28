# 文章工作区

每个主题使用独立目录，建议命名：

```text
articles/
└── 01-vibe-coding-needs-observability/
    ├── wechat.md
    ├── xhs.md
    ├── fact-sheet.md
    └── asset-manifest.md
```

状态统一使用：`idea` → `evidence` → `outline` → `draft` → `fact-review` → `approved` → `published` → `retrospective`。

每篇发布前必须具备：

- 真实案例或实验记录；
- 官方产品事实来源与核验日期；
- 素材授权、脱敏和复用范围；
- 公众号稿、XHS 分镜及单一 CTA；
- 发布链接与一周复盘。

## 本季度前两篇重点

- [01｜个人 SaaS 为什么先试观测云免费专区](./01-free-tier-for-indie-saas/outline.md)：以免费专区为低风险 POC，核验额度、条款（含免费版非商业用途条款）、维护工时与商业版估算成本。
- [02｜从自建 observability 到 Guance 的平滑迁移与可回退切换](./02-observability-migration-with-rollback/outline.md)：以 `ai-workspace-infra/observability` 为现状，以开关、双写、并行对账、7 条切换标准和 15 分钟回退完成可回退切换；完整矩阵与验证实验见[附录](./02-observability-migration-with-rollback/migration-matrix.md)。

- [00｜11 月开篇补充案例（OPE）：编程 Agent 直接 debug vs Obsy Agent Teams 巡检](./00-nov-opener-ope-case/article_draft.md)：以平台编排流水线两次真实失败为案例；Obsy 侧待实测。

这两篇属于本次季度合作的重点交付；后续题库仅是候选储备，不代表已承诺继续由 Guance 赞助或实施。
