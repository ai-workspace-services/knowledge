---
title: 附录 A　年份勘误与口径说明
---

## 合集勘误（collection-r2）

> 2026-10-19 整理版 r2 新增。年龄榜逐条勘误表见专题「趣味篇：AI 家族年龄榜 → 年份勘误与口径说明」。图片本身没有重画，下表只更正文字口径。

| # | 位置 | 原写法 | 更正 |
|---|---|---|---|
| 1 | 年龄榜全部条目 | 按 2025 年计算 | 按 2026 年计算，全部 +1 岁 |
| 2 | 年龄榜 · DeepSeek-R1/V3 | 1 岁 | **2 岁**（V3 2024-12、R1 2025-01，按 2024 计） |
| 3 | 公司寿命篇副标题 | 「2 岁估值百亿」 | 「**3 岁**估值百亿」（Mistral 2023-04 成立；估值说法沿用原句，未另行核实） |
| 4 | BabyAGI 冷知识 | 约 100 行代码 | 原版约 **140 行**（classic/babyagi.py 共 138 行） |
| 5 | BabyAGI 首发时间 | 2023-04 | **2023-03-28** 首发（Task-Driven Autonomous Agent），4 月初以 BabyAGI 之名开源；年份不变 |
| 6 | 年龄榜小结 | Agent 1~3 岁、LLM 2~8 岁、DL/ML 10~39 岁 | Agent 2~4 岁、LLM 2~9 岁、DL/ML 8~68 岁 |
| 7 | 第 9 章「企业开源替代」 | Vault 列为开源方案 | HashiCorp 自 2023-08 起把 Terraform、Vault 等改为 BSL 许可，已不是 OSI 开源（见「缺口与建议补写」第 7 条） |

## 趣味篇「AI 家族年龄榜」年份口径

**勘误**（2026-10-19 v2，依据 `age-board-errata.md`，与 ages.py 年份口径一致）：

| # | 条目 | 原稿 | 更正为 | 依据 |
|---|---|---|---|---|
| 1 | 全部条目 | 按 2025 年计 | 按 2026 年计，全部 +1 岁 | 年龄 = 2026 − 诞生年 |
| 2 | DeepSeek-R1/V3 | 1 岁（2024–2025） | **2 岁**（按 2024 计） | V3 2024-12-26 发布，R1 2025-01-20 发布 |
| 3 | 公司组副标题「2 岁估值百亿」 | 2 岁 | **3 岁** | Mistral 2023-04 成立；“估值百亿”沿用原句，未另行核实。v2 文案 12 篇标题已是「3 岁估值百亿」 |
| 4 | BabyAGI 冷知识「约 100 行代码」 | 约 100 行 | **约 140 行** | 原版 classic/babyagi.py 共 138 行；作者说代码由 GPT-4 写成，约用了 50 个提示词 |
| 5 | BabyAGI 首发时间（ages.py 备注 2023-04） | 2023-04 | **2023-03-28** | 原版 Task-Driven Autonomous Agent 首发于 2023-03-28，4 月初才以 BabyAGI 之名开源；年份不变。ages.py 只报告，未修改 |
| 6 | 小结「Agent 1~3 岁、LLM 2~8 岁」 | — | Agent 2~4 岁、LLM 2~9 岁 | 按 2026 重算：Transformer 9 岁；Word2Vec（13 岁）属前 LLM 时代，不计入 |
| 7 | 小结「DL/ML 底座 10~39 岁」 | — | 8~68 岁 | JAX 8 岁到感知机 68 岁 |

其余条目年份核对无误。下面列出有多种起算口径的条目和本版采用的依据。

| 条目 | 采用年份 | 依据 | 口径 |
|---|---|---|---|
| SQL | 1974 | 1974 年 Chamberlin 与 Boyce 发表 SEQUEL 论文；1986 年 ANSI X3.135 首个 SQL 标准 | 取语言诞生年 1974；按标准化算则为 1986 年（40 岁） |
| Word2Vec | 2013 | Mikolov 等 arXiv 1301.3781（2013-01）及同年 NeurIPS 论文 | 无争议，保留 |
| SVM | 1995 | 1963 Vapnik 最大间隔线性分类器；1992 Boser/Guyon/Vapnik 核技巧；1995 Cortes & Vapnik 软间隔《Support-Vector Networks》 | 取今日通用形式 1995；按 1963 起算则 63 岁 |
| k-NN | 1967 | 1951 Fix & Hodges 技术报告首提非参数近邻判别；1967 Cover & Hart 给出误差界 | 保留 1967（理论化之年）；按最早提出算为 1951 年（75 岁） |
| PyTorch | 2016 | 2016-09 Alpha 版发布；2017-01-18 正式公开 | 取 2016 |
| Scikit-learn | 2007 | 2007 GSoC 项目起步；2010-02-01 首次公开发布 | 取 2007 |
| Pandas | 2008 | 2008 AQR 内部开发；2009 年底开源 | 取 2008 |
| NumPy | 2005 | 2005 开始整合 Numeric/Numarray；2006-01 首个版本 0.9.2，2006-10 1.0 | 取 2005 |
| Spark | 2009 | 2009 伯克利 AMPLab 研究项目；2010 开源 | 取 2009 |
| 随机森林 | 2001 | 1995 Ho 提出 random decision forests；2001 Breiman《Random Forests》 | 取 2001 |
| 感知机 | 1958 | 1957 Rosenblatt 技术报告；1958 Psychological Review 论文 | 取 1958 |
| ID3 | 1986 | Quinlan 1986《Induction of Decision Trees》 | 取 1986 |
| Weka | 1993 | 1993 怀卡托大学立项；Java 版 1997 | 取 1993 |
| SAS | 1976 | 软件 1966 起于北卡州立大学；SAS Institute 1976 成立 | 取公司成立 1976；按软件起点则为 60 岁 |
| Excel | 1985 | 1985 Mac 版 Excel 1.0；1987 Windows 版 | 取 1985 |
| Caffe | 2013 | 2013 春 DeCAF；2013-12 Caffe 公开发布 | 取 2013 |
| DeepSeek-R1/V3 | 2024 | V3 2024-12；R1 2025-01 | 取 2024（R1 单独算为 1 岁） |
| IBM | 1911 | 1911-06-16 以 CTR 公司注册；1924 更名 IBM | 取 1911 |
| Meta | 2004 | 2004 Facebook 成立；2021 更名 Meta | 取 2004 |

## 年龄榜长图 r2 勘误记录

- 计算口径：年龄 = 2026 − 诞生年。用户原稿是按 2025 年算的，所以**所有年龄都 +1**。例如 IBM 115、SQL 52、C 语言 54、NVIDIA 33、Excel 41。
- 年份口径对齐 `/workspace/it-history/build/src/ages.py`（《图解 IT 简史》合集已上传，以它为准），并逐条用 WebSearch 复核。
- 复核时间：2026-10-19（UTC+8）。

## 一、需要更正或改写的地方

| 条目 | 用户原稿 | v2 采用 | 依据 |
|---|---|---|---|
| 全部条目 | 按 2025 年计 | 按 2026 年计，全部 +1 岁 | 用户要求 |
| DeepSeek-R1/V3 | 1 岁（2024-2025） | 2 岁（按 2024 计） | V3 发布于 2024-12-26，R1 发布于 2025-01-20；口径同 ages.py |
| 小结「Agent 1~3 岁、LLM 2~8 岁」 | — | Agent 2~4 岁、LLM 2~9 岁 | 按 2026 年重算：Transformer 9 岁；Word2Vec 13 岁属于前 LLM 时代，不计入 |
| 小结「DL/ML 底座 10~39 岁」 | — | 8~68 岁 | 范围从 JAX 8 岁到感知机 68 岁 |
| 公司组副标题「2 岁估值百亿」 | 2 岁 | 3 岁 | Mistral 成立于 2023-04；估值说法沿用用户原句，未另行核实 |
| BabyAGI 冷知识「约 100 行代码」（父任务示例） | 约 100 行 | 约 140 行 | 原版 classic/babyagi.py 共 138 行；作者自述代码由 GPT-4 写成，约用了 50 个提示词 |

## 二、年份正确，但需要标注口径的条目

- **PyTorch 2016**：2016-09 发布 Alpha，2017-01-18 正式公开。
- **Scikit-learn 2007**：2007 年作为 GSoC 项目起步，2010-02-01 首次公开发布。
- **NumPy 2005**：2005 年创建，1.0 版于 2006-10 发布。
- **Jupyter 2014**：2014 年从 IPython 拆分出来；IPython Notebook 本身发布于 2011 年。
- **Weka 1993**：1993 年立项，1994 年内部首发，1996 年首次公开（2.1 版），1997 年起用 Java 重写。
- **Caffe 2013**：2013-12 公开发布，论文是 2014 年。
- **ID3 1986**：采用 Quinlan 1986 年的论文；Quinlan 1979 年已首次提出。
- **k-NN 1967**：采用 Cover & Hart 1967 年的理论化论文；Fix & Hodges 1951 年已最早提出。系列 08 的冷知识写的是这一点。
- **BP 1986**：原稿写的是「推广」，对应 Rumelhart、Hinton、Williams 1986 年的论文。更早有 Linnainmaa 1970、Werbos 1982。
- **SPSS 1968**：1968 年首发；也有资料写 1969 年推出，SPSS Inc. 1975 年成立。
- **SAS 1976**：SAS Institute 1976 年成立，软件起源于 1960 年代后期的北卡州立大学。
- **SQL 1974**：1974-05 发表 SEQUEL 论文；后因 Hawker Siddeley 公司持有该商标，改名 SQL。
- **IBM 1911**：1911 年以 CTR 公司成立，1924 年改名 IBM。
- **Spark 2009**：2009 年在伯克利起步，2010 年开源。
- **Pandas 2008**：2008 年在 AQR 起步。
- **Tableau 2003**：2003 年成立，源自斯坦福的 Polaris 项目。
- **CrewAI 2023**：v0.1.0 发布于 2023-11-14。
- **AutoGen 2023**：2023-03 在 FLAML 中起步，论文 2023-08，2023-10 独立成仓库。
- **MetaGPT 2023**：2023-06-30 开源。
- **AutoGPT 2023**：2023-03-30。
- **BabyAGI 2023**：2023-03-28 首发（Task-Driven Autonomous Agent）。
- **LangChain 2022**：2022-10。
- **LlamaIndex 2022**：2022-11 以 GPT Index 之名发布。
- **Devin 2024**：2024-03-12。
- **其余条目已核实无误**：
  - 模型：Claude 3 2024-03；LLaMA 2023-02；GPT-4 2023-03；ChatGPT 2022-11；InstructGPT 2022-01；T5 2019-10；BERT 2018-10；GPT-1 2018-06；Transformer 2017-06；Word2Vec 2013。
  - 深度学习：JAX 2018-12；TensorFlow 2015-11；ResNet 2015-12；Keras 2015-03；AlexNet 2012；Theano 2007；LeNet-5 1998；LSTM 1997。
  - 机器学习：XGBoost 2014-03；LightGBM 2016-10；CatBoost 2017-07；随机森林 2001；SVM 1995；感知机 1958。
  - 数据分析：Polars 2020；DuckDB 2019-06；R 1993-08；Excel 1985-09（Mac 版）。
  - 公司：Mistral 2023-04；DeepSeek 2023-07；月之暗面 2023-03；Perplexity 2022-08；Anthropic 2021；智谱 2019-06；Cohere 2019；Hugging Face 2016；OpenAI 2015-12；DeepMind 2010；Meta 2004；Google 1998；NVIDIA 1993-04；Apple 1976；Microsoft 1975；C 语言 1972。

## 三、对 ages.py 的复核结论（只报告，未修改）

- 年份数值没有发现错误。
- 一处月份可以更精确：`BabyAGI` 的备注写的是「2023-04」。原版 Task-Driven Autonomous Agent 首发于 2023-03-28，4 月初才以 BabyAGI 之名开源。年份不受影响。

## 四、v2 冷知识的出处（均已用 WebSearch 核实）

- SQL 原名 SEQUEL，因商标问题去掉元音改名（Chamberlin，1995 SQL Reunion 访谈）。
- Pandas 2008 年诞生于对冲基金 AQR（pandas 官网 About 页）。
- DuckDB 的名字来自创始人的宠物鸭 Wilbur（CWI；BigDATAwire 2024 采访）。
- Python 1991 年发布，比 Java（1995）早 4 年。
- Jupyter 的名字致敬 Julia、Python 和 R。
- Tableau 源自斯坦福 Polaris 项目；Excel 1985 年首发于 Mac，1987 年才有 Windows 版。
- 1958 年《纽约时报》称感知机将来能「走路、说话、看、写、自我复制，并意识到自己的存在」。
- XGBoost 在 2014 年 Kaggle 希格斯挑战赛中走红（1785 支队伍参赛）。
- Weka 是新西兰一种不会飞的鸟。
- AlexNet 用两块 3GB 显存的 GTX 580 训练了 5–6 天。
- LeNet-5 曾用于美国银行的支票识别，一度读取全美约 10% 的支票。
- Keras 一词源自希腊语 κέρας（角）。
- 《Attention Is All You Need》共有 8 位作者。
- GPT-2 在 2019 年分阶段发布，11 月才放出 15 亿参数的完整版。
- ChatGPT 上线 5 天用户破百万，约 2 个月月活过亿。
- BabyAGI 原版约 140 行代码。
- Devin 在 SWE-bench 570 题子集上独立解决 13.86%，此前无辅助的最好成绩是 1.96%。
- MCP 2024-11 开源，2025-12-09 捐给 Linux 基金会旗下的 Agentic AI Foundation。
- Claude Code 2025-02 发布预览、2025-05 正式发布；Codex CLI 2025-04-16；Gemini CLI 2025-06-25；Xcode 26.3（2026-02）集成编码 Agent 并支持 MCP。
- NVIDIA 在 Denny's 餐厅里谋划诞生。
- Google 早期叫 BackRub。
- Hugging Face 最初是给青少年做的聊天机器人 App。
- DeepMind 2014 年被 Google 收购。
- 时间轴补充：
  - ChatGPT Code Interpreter 2023-07；Python in Excel 2023-08 公测。
  - PyTorch 2.0 2023-03；Keras 3 2023-11。
  - 树模型在表格数据上的论文 2022-07；TabPFN 2025-01 登上 Nature。

## 五、未采用的说法

- Theano 以古希腊女数学家命名：检索结果没有给出明确出处，所以没写。
