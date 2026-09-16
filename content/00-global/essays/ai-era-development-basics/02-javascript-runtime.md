# 02 / 10｜JavaScript 到底运行在哪里？

## 微信 / 朋友圈

很多初学 Web 的人会产生一个错觉：

> JavaScript = 浏览器语言。

其实不是。

JavaScript 是语言。

**Browser 和 Node.js 才是运行时。**

同一段 JavaScript，因为运行环境不同，可以拥有完全不同的能力：

浏览器可以访问 DOM、window、Cookie；

Node.js 可以访问文件、进程、环境变量、数据库和后台任务。

所以碰到 JS 代码，第一件事不要问：

> “这是什么语法？”

而是问：

> **“它运行在哪里？”**

这也是理解 Next.js Server / Client 边界的基础。

## 小红书

**标题：**

> JavaScript 到底运行在哪里？很多人第一步就搞错了

JavaScript 不等于 Browser。

也不等于 Node.js。

更准确地说：

**JavaScript = 语言  
Browser / Node.js = Runtime**

Browser 给 JavaScript：

DOM、window、Web Storage、fetch、用户事件、UI 渲染。

Node.js 给 JavaScript：

Process、文件系统、环境变量、服务器、数据库、后台任务。

所以同样是：

```js
console.log("hello")
```

背后的能力边界可能完全不同。

这也是为什么开发 Next.js 时经常会遇到：

`window is not defined`

它不是 JavaScript 不支持。

而是：

**你把浏览器代码放到了服务器运行。**

AI 时代很重要的一项能力，就是能判断代码属于哪个 Runtime。

## X

JavaScript is a language.

Browser and Node.js are runtimes.

That distinction explains a surprising amount of Web development:

Browser → DOM, window, storage, UI  
Node.js → fs, process, env, DB, background jobs

Same language. Different runtime. Different capabilities.

Before debugging JavaScript, ask:

**Where is this code actually running?**

02/10

## LinkedIn

One of the most useful distinctions in modern JavaScript development:

**JavaScript is the language.  
Browser and Node.js are runtimes.**

The runtime determines the capabilities available to the code.

Browser: DOM, window, storage, user interaction, rendering.

Node.js: processes, filesystem, environment variables, servers, databases and background jobs.

This simple model makes many Next.js issues easier to understand, especially server/client boundaries.

Before debugging the syntax, ask:

**Where is the code executing?**

