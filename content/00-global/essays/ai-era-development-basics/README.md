# 《AI 时代需要掌握的开发基础知识》

Engineering Decision Canvas · 工程决策画布

## 文件索引

| 文件 | 主题 |
|---|---|
| [00-series-overview.md](00-series-overview.md) | 系列统一定位、平台发布策略、统一 Hashtag |
| [01-modern-web.md](01-modern-web.md) | 一张图看懂现代 Web 开发 |
| [02-javascript-runtime.md](02-javascript-runtime.md) | JavaScript 到底运行在哪里 |
| [03-react-nextjs.md](03-react-nextjs.md) | React、Next.js、Node.js 分别负责什么 |
| [04-csr-ssr-rsc.md](04-csr-ssr-rsc.md) | CSR、SSR、RSC 怎么选 |
| [05-hydration.md](05-hydration.md) | Hydration 到底是什么 |
| [06-fetch-axios.md](06-fetch-axios.md) | fetch 和 Axios 到底差在哪 |
| [07-state.md](07-state.md) | State 到底放在哪里 |
| [08-api-request.md](08-api-request.md) | 一次 API 请求到底经过谁 |
| [09-npm-pnpm-packagejson.md](09-npm-pnpm-packagejson.md) | npm、pnpm、package.json 为什么能让项目跑起来 |
| [10-ai-era-minimum-stack.md](10-ai-era-minimum-stack.md) | AI 时代真正需要掌握什么 |

## 推荐发布方式

- 建议按 01–10 连续发布，形成 10 天内容系列。
- 图片负责系统解释，文案负责提出问题、给出观点并引导收藏或讨论。
- 微信/朋友圈突出观点与收藏价值；小红书使用问题型标题；X 保持短结论；LinkedIn 强调工程判断与系统边界。
- 每一期配套使用对应编号图片。本文案整理过程中未修改、重绘或重新生成用户提供的图片。
- 发布前可根据平台字数限制、账号语气和配图版式做轻微删减，不改变核心观点即可。

## 系列核心问题

> 代码运行在哪里？什么时候运行？数据属于谁？失败如何观察？结果如何验证？

## 系列总开场

### 微信公众号 / 视频号整套发布

> **AI 会写代码以后，我们到底还需要掌握什么？**
>
> 过去学开发，经常从语言开始：
>
> JavaScript 怎么写？  
> React 怎么写？  
> SQL 怎么写？
>
> 但 AI Coding 出现以后，我觉得学习顺序应该反过来。
>
> 先理解系统。  
> 再理解边界。  
> 最后才是工具。
>
> 我把现代 Web 开发中最容易混淆的几个问题，整理成了一套 **10 张「工程决策画布」**。
>
> 整套内容其实都围绕几个问题：
>
> **运行在哪里？  
> 什么时候运行？  
> 谁拥有数据？  
> 失败如何观察？  
> 结果如何验证？**
>
> AI 可以越来越快地生成代码。
>
> 但真正决定系统质量的，依然是人对**边界、职责、数据流和取舍**的理解。
>
> **先判断边界，再让 AI 加速实现。**

### 小红书整套首发标题

> **AI 都能写代码了，这 10 张图才是现在真正该学的开发基础**

备选：

- 别再背语法了：10 张图看懂 AI 时代的 Web 开发
- 从 Browser 到 PostgreSQL：10 张图建立现代 Web 工程脑图

封面第一句话：

> **AI 会写代码，但架构边界还是得你判断。**

### X 整套 Thread 开场

> AI can now write a surprising amount of production code.
>
> So what should developers still understand?
>
> Not every syntax detail.
>
> The important part is understanding:
>
> **runtime, boundaries, data flow, ownership, failure and trade-offs.**
>
> I turned my mental model of modern Web development into 10 engineering decision canvases.
>
> A thread 🧵

### LinkedIn 整套首发版

> **What development fundamentals still matter when AI can write the code?**
>
> I have been thinking about this question while using AI more deeply in software engineering.
>
> My conclusion is that the value is gradually shifting away from memorizing syntax toward understanding **boundaries and systems**.
>
> I summarized that mental model into a 10-part Engineering Decision Canvas.
>
> The recurring questions across all ten diagrams are:
>
> **Where does it run?  
> When does it execute?  
> Who owns the data?  
> Where is the trust boundary?  
> How does failure become observable?  
> How do we verify the result?**
>
> AI is becoming exceptionally good at implementation.
>
> That makes architectural judgment, system boundaries, contracts and verification more—not less—important.
>
> **Understand the boundary first. Then let AI accelerate implementation.**

