# 本机 QMD：跨 Code APP 接力与 Knowledge 向量归档

日期：2026-11-03。需求：Code APP 之间共享任务进度、决策和下一步，避免复制聊天；最终文档统一进入 [Knowledge](https://github.com/ai-workspace-services/knowledge)，归档后再更新 QMD 文档索引与向量。源码修复由 [QMD #11](https://github.com/ai-workspace-lab/qmd/issues/11) / [PR #12](https://github.com/ai-workspace-lab/qmd/pull/12) 跟踪，文档由 [Knowledge #355](https://github.com/ai-workspace-services/knowledge/issues/355) 跟踪。

## 数据归属与连接

| 内容 | 来源与职责 |
| --- | --- |
| 当前任务、driver、决策、阻塞、下一步 | 同一 PostgreSQL 中的 QMD 任务状态，跨 MCP 进程共享 |
| 最终规划、操作手册、事实摘要、交付结论 | Knowledge 的 Git commit / PR |
| 文档全文索引与 embedding | QMD，可从 Knowledge 固定版本重建 |
| 原始响应、敏感现场证据 | 受控 artifact，仅将脱敏摘要与引用归档 |

本机 Codex、Claude、Antigravity 的 QMD stdio 配置已核对使用同一数据库。MCP 进程独立存在不影响共享状态，无须把任务内容互相复制。配置文件为 `~/.codex/config.toml`、`~/.claude.json`、`~/.gemini/config/mcp_config.json`；不得把其中连接串提交到 Git。

原有 `127.0.0.1:8181` 是容器的桥接后端，要求 Token，直接访问任务 API 会返回 401。本次新增原生桌面服务，使用 `127.0.0.1:8182`；本机任务 API 和 `/mcp` 均可无 Token 读写。容器的远程桥接鉴权不变。两者不应混用地址；本机免密指向 8182 或直接使用 stdio。

原生服务以当前桌面用户运行，通过 LaunchAgent 自启。启用 `QMD_LOCAL_NO_AUTH=1` 且绑定回环地址；绑定 `0.0.0.0` 等非回环地址会拒绝启动，即使已有远程 Token 也不能绕过。Host/Origin 校验保留。不依赖转发头推断可信来源，不修改 PostgreSQL 自身认证，不把管理数据库凭据展示到回执。

## 接力步骤

1. 新客户端先调用 `task_catalog`，传相同的规范化仓库 scope，例如 `github.com/ai-workspace-services/knowledge`。修复后的文字与结构化结果均包含最近任务的 `thread_id`、branch 和状态。
2. 用已有 `thread_id` 调用 `task_resume`，填写真实 client。不同 worktree、分支或默认 main 下，都不要仅凭当前目录创建新的“同一任务”。默认分支本来不能唯一标识任务，应从目录发现后接续。
3. 保存返回的 `sessionId`；需要安排方向时获取 driver lease，并保存 `fence`。及时通过 `task_note` 写入脱敏决策、验证结果、阻塞和下一步；资料指向 Knowledge 相对路径及 commit/PR。
4. 交接用 `task_handoff` 写清一个可执行的下一步，提交当前 session 与 fence，释放 driver。下一客户端接续同一 thread，并在已交接后取得新的 fence。活跃 driver 尚未交接时先作为 peer 贡献，不强制抢占。

这些操作传递的是共享状态，不会自动向另一 APP 发送聊天消息，也不保证另一 APP 已启动。接力方通过任务目录取得上下文，无需重复粘贴完整提示词。

本轮实测采用两个独立 stdio MCP 协议客户端和一个 HTTP 客户端：HTTP 无认证写入 → stdio A 读取、写入、交接 → stdio B 接手、写入 → HTTP 读取，全部成功，driver fence 正常递增。隔离验收 thread 为 `3c27f23e-be1b-4b32-88a8-7a7135f1ed1d`。这是协议与存储实测，不等于真实 GUI APP 的完整操作已验收。已启动的旧 MCP 进程需要重连以加载新代码及工具 schema。

## Knowledge 归档后生成向量

本机选择 Ollama 的 `qwen3-embedding:0.6b`，通过 `http://127.0.0.1:11434/v1/embeddings` 接入 QMD。模型采用 [Apache 2.0 许可](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B)，Ollama 分发约 [639 MB](https://ollama.com/library/qwen3-embedding:0.6b)，适合中文、多语言及代码资料检索。模型只负责 embedding，任务数据库、归档流程及全文索引仍由各自组件负责。

QMD 使用 `models.embed: qwen3-embedding:0.6b` 与 `QMD_EMBED_API_BASE_URL=http://127.0.0.1:11434/v1`。本机回环 embedding API 不要求密钥，也不发送伪造的 Bearer 字段；远程 embedding 端点仍要求凭据。本次不改变生成模型和 reranker 的选择，向量验收使用纯 `vsearch`，避免其他模型依赖影响判断。

标准顺序：

1. 将最终文档提交 Knowledge 分支并推送，记录 commit 与 PR；尚未合并时明确标为 PR 归档版本，不能称为 main。
2. 从选定 commit 创建只读索引快照，collection 指向归档快照；不将其他 dirty checkout 的未提交文件当作已归档内容。
3. 更新 collection，并为该 collection 执行 `qmd embed -c knowledge-platform-delivery`。模型和维度改变时要重建该集合向量，不能混用不同模型的旧向量。
4. 用中文纯向量查询 `qmd vsearch 'Grafana 三个节点面板数据流排查' -c knowledge-platform-delivery --format json`，确认命中已归档提示词；用另一条跨 APP 接力查询命中本文。记录文档数、chunk 数、向量维度、模型摘要和来源 commit。
5. 将索引/检索回执记录到共享任务；需要固化的结论再补入 Knowledge，随后增量更新。合并到 main 后将 collection 切换到新的已合并快照。

不要把有文档条目、有全文检索结果或有任务记录称为“向量化完成”。必须有实际 embedding 写入和纯向量命中证据。模型下载或 embedding 未完成时明确标为进行中。

## 回退与本次边界

源码修改使用独立 worktree；现有 QMD 主工作树的未跟踪部署文件未改动。桌面客户端配置有本机受保护备份，原生服务可停止，客户端可恢复旧 executable 路径；共享任务保存在原数据库，不靠删除数据库来回退。切回 embedding 模型时同步恢复模型配置及对应向量，不把不同模型向量混用。

本次仅修本机 QMD 任务发现、免密访问、接力及 Knowledge 向量检索。Grafana 21 面板的生产数据流修复由[Antigravity 专项提示词](Antigravity-21个Grafana面板数据流检查与修复提示词.md)接力执行。
