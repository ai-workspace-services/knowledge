# 06 / 10｜fetch 和 Axios，真正的区别不是性能

## 微信 / 朋友圈

**标题：** fetch 和 Axios，真正的区别不是性能

fetch 和 Axios 都可以发 HTTP 请求。

真正的区别不是“谁更快”。

而是抽象层次。

**fetch：平台能力。**

**Axios：工程约定。**

小项目、精细控制、减少依赖：

fetch 很合适。

团队项目，需要统一：鉴权、超时、错误处理、重试、baseURL、日志……

Axios 会更省心。

所以我更喜欢这个判断方式：

> **先统一请求边界，再决定 fetch 还是 Axios。**

## 小红书

**标题：**

> fetch 和 Axios 到底选哪个？其实不是性能问题

很多讨论最后都会变成：

fetch 还是 Axios？

实际上两者最大的区别是：

**fetch 是平台原生能力。**

**Axios 是更高一级的 HTTP Client 抽象。**

fetch：

- 原生
- 依赖少
- 自由度高
- 行为需要自己约定

Axios：

- Interceptor
- timeout
- JSON transform
- 统一错误处理
- baseURL
- 团队约定更方便

所以我一般不会单独问：

“这个项目到底该用 Axios 还是 fetch？”

而是先问：

**HTTP 请求层有没有统一边界？**

如果连鉴权、错误、重试、日志都散落在组件里面，换哪个库都救不了。

## X

**Title:** fetch vs Axios is an abstraction decision, not a speed contest.

fetch vs Axios is mostly about abstraction level.

fetch → platform primitive  
Axios → engineering conventions

If you need minimal dependencies and explicit control: fetch.

If you need shared auth, interceptors, timeout, error handling and conventions across a team: Axios can be convenient.

First design the HTTP boundary.

Then choose the client.

06/10

## LinkedIn

**Title:** Define the HTTP boundary before choosing fetch or Axios.

The fetch vs Axios discussion is often framed as a library comparison.

I find it more useful to think in terms of abstraction.

**fetch is a platform primitive.**

**Axios provides additional engineering conventions.**

The important decision is usually not the HTTP client itself, but whether the application has a consistent request boundary for authentication, timeouts, errors, retries, tracing and response normalization.

First define the boundary.

Then choose the tool.
