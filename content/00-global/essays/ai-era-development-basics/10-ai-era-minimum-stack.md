# 10 / 10｜AI 会写代码以后，开发者还需要掌握什么？

## 微信 / 朋友圈

做完这套图以后，我越来越确定一件事：

AI 时代不需要每个人重新背一遍所有语言、框架和 API。

但开发者仍然需要一套可以判断、设计、排查和验收系统的最低知识栈。

### 1. Runtime：代码运行在哪里？

Browser、Node.js、Edge、Server 还是后台任务？

运行位置决定代码拥有什么能力，也决定它能不能访问 DOM、文件、环境变量、数据库和用户状态。

### 2. UI / Framework：页面如何生成和交互？

React、Next.js、CSR、SSR、RSC 和 Hydration 分别解决什么问题？

### 3. HTTP / Data：数据如何流动？

请求从哪里发出，经过哪些边界，错误如何返回，数据如何校验？

### 4. Service / Storage：规则和事实分别放在哪里？

前端负责体验，服务端负责规则，数据库负责持久化事实。

### 5. Engineering Delivery：如何证明它能交付？

依赖、测试、构建、部署、日志、指标、Trace 是否形成闭环？

### 6. AI Collaboration：如何与 AI 一起工作？

能否描述约束、拆分任务、提供上下文、设定验收标准，并验证 AI 的结果？

## AI 编程的正确工作流

不要只对 AI 说“帮我写一个功能”，而是依次明确：

1. **目标**：要解决什么用户或业务问题？
2. **边界**：代码运行在哪里，数据归谁，不能做什么？
3. **契约**：输入、输出、错误和权限如何定义？
4. **实现**：让 AI 生成方案和代码。
5. **验证**：用测试、日志、Schema、Review 和真实场景证明结果。
6. **迭代**：根据失败信息继续修正，而不是盲目重写。

## 如何排查 AI 生成的功能？

从 5 个问题开始：

1. **运行在哪里？** 是否把 Browser 代码放到了 Server？
2. **什么时候运行？** 首次加载、用户点击、服务端渲染还是后台任务？
3. **谁拥有数据？** 是否出现重复来源、错误缓存或越权访问？
4. **失败如何观察？** 是否有可读日志、状态码、指标和 Trace？
5. **结果如何证明正确？** 是否有测试、契约、Schema 和用户验收？

最后还是回到一句话：

> **先判断边界，再让 AI 加速实现；先定义验收，再接受生成结果。**

## 小红书

**标题：**

> AI 都会写代码了，开发者真正需要掌握的是什么？

这组 10 张图最后想表达的，不是“框架不重要”。

而是：

**当 AI 越来越会写代码，开发者越需要理解代码之外的系统。**

### 现在最值得掌握的 6 个问题

**① 运行在哪里？**

Browser / Node.js / Edge / Server？

**② 什么时候运行？**

首次加载？服务端渲染？用户点击？后台任务？

**③ 谁拥有数据？**

组件？页面？API？Service？Database？

**④ 请求经过哪些边界？**

Browser → BFF → Service → Cache → Database？

**⑤ 失败怎么看？**

Logs？Metrics？Trace？Alert？

**⑥ 怎么证明结果正确？**

Test？Schema？Contract？User Experience？

### AI 编程不要只给一句需求

更好的方式是给 AI 一份小型工程 brief：

- 背景和目标
- 运行环境
- 数据模型
- API 契约
- 权限和安全边界
- 失败场景
- 验收标准

然后让 AI 分阶段完成：

**理解 → 设计 → 实现 → 测试 → 排查 → 总结**

AI 可以从“自动补全工具”变成“工程执行加速器”，前提是人仍然负责边界、约束和验收。

这套系列最后只有一句话：

> **想清边界与取舍，比写出代码更重要。**

## X

**Title:** AI lowers implementation cost. It raises the value of engineering judgment.

The minimum knowledge stack for AI-assisted development is not every API or framework detail.

It is the ability to answer:

1. Where does the code run?
2. When does it execute?
3. Who owns the data?
4. What boundaries does the request cross?
5. How does failure become observable?
6. How do we verify the result?

A practical AI coding workflow:

**Goal → boundaries → contracts → implementation → verification → iteration**

Before asking AI to build a feature, provide:

- runtime and architecture context
- data ownership
- API and error contracts
- security constraints
- failure scenarios
- acceptance criteria

AI is excellent at implementation acceleration.

It does not remove the need for system understanding.

**Define the boundary. Define the acceptance criteria. Then accelerate the implementation.**

10/10

## LinkedIn

**Title:** The minimum engineering knowledge stack for the AI era

The AI era does not require engineers to memorize every API, framework or implementation detail.

It does require a strong mental model for designing, debugging and verifying software systems.

The minimum practical stack is:

1. **Runtime** — where code executes and what capabilities it has.
2. **UI and frameworks** — how interfaces are rendered and made interactive.
3. **HTTP and data flow** — how requests cross boundaries and how contracts are represented.
4. **Services and storage** — where business rules and durable facts belong.
5. **Engineering delivery** — how dependencies, tests, builds, deployments and observability form a trustworthy loop.
6. **AI collaboration** — how to provide context, express constraints, decompose work and verify generated output.

A reliable AI-assisted workflow looks like this:

**Goal → boundaries → contracts → implementation → verification → iteration**

Before asking AI to implement a feature, engineers should be able to define:

- execution and trust boundaries
- data ownership and lifecycle
- input, output and error contracts
- security and failure scenarios
- acceptance criteria and verification methods

When an AI-generated feature fails, start with five questions:

1. Where did the code run?
2. When did it execute?
3. Who owned the data?
4. How did the failure become observable?
5. What evidence would prove the result correct?

AI is exceptionally good at accelerating implementation. Someone still needs to define the system, the constraints and the definition of done.

> **Understand the boundary first. Then let AI accelerate the implementation.**

**Engineering Decision Canvas — 10/10**

