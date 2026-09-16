# 05 / 10｜AI 写 SSR 页面时，为什么按钮还点不了？

## 微信 / 朋友圈

AI 可以很快生成一个 SSR 页面，但页面“看得见”，不代表它已经“能交互”。

设计一个 SSR 页面时，先把页面拆成两部分：

**HTML = 结构与内容**  
**JavaScript = 状态与行为**

服务器先把 HTML 返回给浏览器，所以用户可能已经看到了标题、列表和按钮。

但浏览器还需要下载 JavaScript，React 再对现有 DOM 进行匹配，并绑定状态与事件。

这个接管过程就是 **Hydration**。

所以，让 AI 设计交互页面时，先明确三件事：

1. 哪些内容可以由服务端直接生成？
2. 哪些组件必须在客户端运行？
3. 服务端和客户端第一次渲染的结果是否稳定一致？

### 如何排查按钮点不了？

按这个顺序检查：

1. **HTML 是否已经返回？** 没有返回，先查服务端渲染和请求。
2. **JavaScript 是否加载？** 检查 Network、构建产物和浏览器 Console。
3. **Hydration 是否完成？** 确认组件是否被客户端接管。
4. **事件是否绑定？** 检查组件是否需要 Client Component，以及事件处理函数是否存在。
5. **是否发生 Hydration mismatch？** 对比服务端和客户端第一次渲染，重点检查 `Date`、`Math.random()`、`window`、`localStorage`。

一句话记住：

> **Hydration 不是重新生成页面，而是给已有 HTML 补上行为。**

让 AI 写代码之前，先告诉它运行环境、交互边界和验收方式。

## 小红书

**标题：**

> AI 写出来的 SSR 页面，为什么按钮还点不了？附 Hydration 排查顺序

AI 很擅长生成页面结构，但它经常遗漏一个问题：

**这段交互代码到底运行在哪里？**

SSR 页面通常经历两步：

**第一步：服务端生成 HTML**

用户先看到页面结构。

**第二步：浏览器下载 JavaScript 并完成 Hydration**

React 找到已有 HTML，对齐组件树，恢复状态并绑定事件。

所以：

> **看得见 ≠ 已经可交互。**

### 让 AI 设计页面时，先给这 3 个约束

1. **运行位置**：这个组件在 Server 还是 Client？
2. **交互范围**：哪些按钮、输入框和状态需要客户端行为？
3. **一致性要求**：服务端和客户端第一次渲染能否得到同样的结果？

### 按钮点不了，按这个顺序查

1. HTML 有没有成功返回？
2. JavaScript 有没有加载？
3. Hydration 有没有完成？
4. 组件是不是需要 Client Component？
5. Console 有没有 `Hydration mismatch`？

如果有 mismatch，优先检查：

`Date`、`Math.random()`、`window`、`localStorage`，以及依赖浏览器环境的条件渲染。

最终页面才是：

**HTML + JavaScript = Interactive UI**

AI 负责生成实现，人负责定义运行边界和验收标准。

## X

**Title:** AI can generate SSR markup. Can it explain why the button does not work?

SSR has two phases:

**Server → HTML structure**  
**Browser → JavaScript behavior**

Hydration is React attaching state and event handlers to the HTML that already exists.

When asking AI to design an interactive SSR page, specify:

1. Where does each component run?
2. Which interactions require the client?
3. Will server and client produce the same first render?

Debug in this order:

1. Did the server return HTML?
2. Did the JavaScript bundle load?
3. Did hydration complete?
4. Does this component need to be a Client Component?
5. Is there a `Hydration mismatch`?

Check nondeterministic values first: `Date`, `Math.random()`, `window`, and `localStorage`.

**AI writes the implementation. You define the runtime boundary and acceptance criteria.**

05/10

## LinkedIn

**Title:** Designing and debugging hydration in AI-generated SSR interfaces

AI can generate an SSR interface quickly, but a rendered page is not necessarily an interactive page.

A useful model is:

**Server-rendered HTML provides structure.**  
**Client-side JavaScript provides behavior.**

Hydration is the reconciliation step in which React matches the existing DOM with the component tree and attaches state and event handlers.

When asking AI to design an SSR interface, make three constraints explicit:

1. **Runtime boundary** — which components run on the server and which run in the browser?
2. **Interaction boundary** — which controls require client-side state and event handlers?
3. **Determinism** — will the server and client produce the same initial output?

When an interface is visible but not interactive, debug in layers:

1. Verify the server response and returned HTML.
2. Verify that the client bundle loads successfully.
3. Verify that hydration completes.
4. Verify that the component can handle client interaction.
5. Inspect the console for hydration mismatches.

For mismatches, check dates, random values, `window`, `localStorage`, and browser-dependent conditional rendering first.

The engineering lesson is broader than React:

> **AI can generate implementation details, but humans still need to define runtime boundaries, invariants and acceptance criteria.**

