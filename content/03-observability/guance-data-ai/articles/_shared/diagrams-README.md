# 图表清单（graphviz 源在 src/*.dot，`src/compose.py` 合成；-wechat.png 宽 1080，-xhs.png 为 1080×1440）

| 文件 | 图注 |
| --- | --- |
| a1-01-stack-blindspots | 图1｜低成本栈各层都有指标，但用户体验、跨层上下文和数据库内部仍是盲区 |
| a1-02-free-boundary | 图2｜免费空间与合作/商业空间的权限边界（核验日期 2026-10-27，发布前复核） |
| a1-03-automation-path | 图3｜GitOps 声明 → PR → Terraform → Playbook，Vault 在运行时分开注入凭据 |
| a1-04-evidence-chain | 图4｜一条 UAT 请求的证据链：未实测关联的环节一律标为盲区 |
| a1-05-saas-or-selfhost | 图5｜按“是否需要跨信号/用户视角”和维护成本，决定交给 SaaS 还是继续自建 |
| a2-01-migration-funnel | 图1｜从 Grafana JSON 盘点到 3 个面板，再逐个定性为可迁移/需重写/暂保留 |
| a2-02-query-traps | 图2｜PromQL/LogsQL 到观测云查询的六类语义陷阱，以同窗并排比对为准 |
| a2-03-gitops-hcl | 图3｜监控意图进 Git，renderer 生成 HCL；无 API 权限的空间只做离线生成 |
| a2-04-side-by-side-rollback | 图4｜新旧链路并排对照；配置回退靠 Git + plan/apply，数据回退靠原始存储 |

图中不含任何实测数值；额度数字来自官方版本区分页。重新生成：`cd src && for f in *.dot; do dot -Tpng -Gdpi=150 $f -o ${f%.dot}.raw.png; done && cd .. && python3 src/compose.py`
