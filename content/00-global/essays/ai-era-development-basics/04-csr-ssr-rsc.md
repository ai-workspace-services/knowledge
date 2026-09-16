# 04 / 10｜CSR、SSR、RSC 怎么选？

## 微信 / 朋友圈

CSR、SSR、RSC 没有谁天然更高级。

它们解决的是不同问题。

**CSR：交互优先。**

**SSR：首屏和 SEO 优先。**

**RSC：减少客户端 JS，同时复用服务端能力。**

所以渲染策略不应该变成框架信仰。

而应该根据约束做选择：

> 首屏、SEO、交互、服务器成本，到底哪个更重要？

**渲染策略不是信仰，是约束下的取舍。**

## 小红书

**标题：**

> CSR、SSR、RSC 到底怎么选？不要再站队了

CSR、SSR、RSC 经常被讨论成：

“哪个更先进？”

其实这个问题就错了。

应该问：

**你最在意什么？**

需要极强交互：

→ CSR

公开内容、SEO、首屏很重要：

→ SSR

希望减少浏览器 JS，又要保留服务端组件能力：

→ RSC

现在的 Next.js App Router，本质上也不是逼你只选一种。

真实应用通常就是混合使用。

我的判断原则：

> **渲染策略不是信仰，是约束下的取舍。**

## X

CSR vs SSR vs RSC is not a religion.

Choose based on constraints.

CSR → interaction  
SSR → first paint + SEO  
RSC → less client JS + server composition

The right question is not:

“Which one is best?”

It is:

**What are you optimizing for?**

04/10

## LinkedIn

CSR, SSR and RSC are better understood as engineering trade-offs than competing ideologies.

CSR optimizes for rich client interaction.

SSR helps with initial content delivery and SEO.

RSC can reduce client-side JavaScript while moving more composition to the server.

The useful question is therefore not:

“Which rendering model is best?”

But:

**Which constraint matters most for this route?**

