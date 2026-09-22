# 06 / 10｜AI 设计请求层时，fetch 和 Axios 到底怎么选？

## 微信 / 朋友圈

AI 可以很快生成一个 HTTP 请求，但“能发出去”不等于“请求层设计正确”。

fetch 和 Axios 都可以发 HTTP 请求。

真正的区别不是“谁更快”，而是它们承担的抽象层次不同：

**fetch：平台能力。**
**Axios：工程约定。**

让 AI 设计请求层时，先把请求边界定义清楚：

1. 请求从哪里发出？Browser、Server 还是后台任务？
2. 鉴权、超时、重试和错误处理由谁统一负责？
3. 响应数据如何校验、转换和记录？
4. 哪些错误要展示给用户，哪些错误只进入日志？

### fetch 和 Axios 怎么选？

**fetch 更适合：**

- 小型项目或平台原生能力优先
- 依赖越少越好
- 需要精细控制请求生命周期
- 团队已经有统一的请求封装

**Axios 更适合：**

- 多个服务需要统一请求约定
- 需要拦截器、超时、baseURL 和响应转换
- 鉴权、重试、错误处理需要集中管理
- 团队希望减少重复样板代码

一句话记住：

> **先设计 HTTP 请求边界，再决定使用 fetch 还是 Axios。**

## 如何排查请求失败？

按这个顺序检查：

1. **请求有没有发出？** 检查调用路径、事件绑定和 Network 面板。
2. **请求发往哪里？** 检查 URL、baseURL、环境变量和代理配置。
3. **请求是否被拦截？** 检查 CORS、TLS、网关、鉴权和浏览器策略。
4. **服务端返回什么？** 区分 HTTP 状态码、响应体和业务错误码。
5. **错误有没有被正确处理？** 检查超时、重试、取消请求和日志。

如果这些逻辑散落在组件里，换库通常解决不了问题。

让 AI 写请求代码之前，先提供请求契约、错误模型和验收场景。

## 小红书

**标题：**

> AI 写请求代码前，先搞清楚 fetch 和 Axios 的边界

很多人问：

**fetch 和 Axios 到底选哪个？**

但这个问题通常问早了。

AI 生成请求代码时，最容易遗漏的不是语法，而是工程约定：

- 请求从 Browser 还是 Server 发出？
- Token 放在哪里，谁负责刷新？
- 超时后要不要重试？
- 哪些错误需要提示用户？
- 响应数据是否需要 Schema 校验？
- 请求日志和 Trace ID 放在哪里？

两者可以这样理解：

**fetch = 平台原生能力**

- 依赖少
- 自由度高
- 行为需要自己约定

**Axios = HTTP Client 工程抽象**

- Interceptor
- timeout
- baseURL
- JSON transform
- 统一错误处理
- 团队约定更方便

### AI 设计请求层的正确顺序

1. 先定义请求和响应契约。
2. 再定义鉴权、超时、重试和错误模型。
3. 再决定请求代码运行在 Browser、Server 还是 Worker。
4. 最后选择 fetch 或 Axios。

### 请求失败怎么查？

1. Network 里有没有请求？
2. URL、baseURL、环境变量是否正确？
3. 是否被 CORS、TLS 或鉴权拦截？
4. 状态码和响应体分别说明什么？
5. 错误是否被统一记录和展示？

如果鉴权、错误、重试和日志都散落在组件里，换哪个库都救不了。

## X

**Title:** AI should design the HTTP boundary before choosing fetch or Axios.

fetch and Axios solve different problems:

**fetch → platform primitive**
**Axios → engineering conventions**

Before asking AI to generate request code, define:

1. Where does the request run: browser, server, or worker?
2. Who owns auth, timeout, retry, cancellation, and logging?
3. What is the response and error contract?
4. Which failures are user-facing?

Choose fetch when you want minimal dependencies and explicit control.

Choose Axios when shared interceptors, baseURL, timeout, transformation, and team conventions reduce repetition.

Debug failed requests in layers:

1. Was a request sent?
2. Is the URL and environment configuration correct?
3. Was it blocked by CORS, TLS, gateway, or auth?
4. What do the status code and response body say?
5. Were timeout and errors handled consistently?

**Design the boundary first. Choose the client second.**

06/10

## LinkedIn

**Title:** Designing an AI-ready HTTP request layer: fetch, Axios and failure boundaries

The fetch vs Axios discussion is often framed as a library comparison.

A more useful framing is abstraction:

**fetch is a platform primitive.**
**Axios adds engineering conventions around HTTP clients.**

When asking AI to design a request layer, make the following explicit:

1. **Execution boundary** — does the request run in the browser, on the server, or in a worker?
2. **Ownership boundary** — who owns authentication, retries, timeouts, cancellation and tracing?
3. **Contract boundary** — how are successful responses and business errors represented?
4. **Observation boundary** — where are status codes, latency, request IDs and failures recorded?

fetch is often sufficient when a team wants minimal dependencies, explicit control, or already has a reliable wrapper.

Axios can be useful when interceptors, base URLs, timeout behavior, response transformation and shared conventions are valuable.

When a request fails, debug the boundary rather than the library:

1. Confirm that the request was initiated.
2. Confirm the resolved URL and runtime configuration.
3. Check CORS, TLS, gateway and authentication failures.
4. Separate transport errors, HTTP errors and business errors.
5. Verify that retries, cancellation and logging behave as designed.

The broader lesson is:

> **AI can generate the HTTP call, but engineers still need to define the request contract, ownership model and failure policy.**

