# 08 / 10｜一个 API 请求，究竟经过了多少层？

## 微信 / 朋友圈

**标题：** 一个 API 请求，究竟经过了多少层？

一次看似简单的：

```text
GET /api/user
```

背后可能经过：

**Browser  
→ HTTP  
→ API / BFF  
→ Go Service  
→ Redis  
→ PostgreSQL  
→ Service  
→ BFF  
→ Browser**

每一层都有自己的责任和信任边界。

尤其有一个原则很重要：

> **不要让 Browser 直接拥有数据库权限。**

前端负责体验。

服务端负责规则。

数据库负责事实。

这三者最好不要混为一谈。

## 小红书

**标题：**

> 一个 API 请求，到底经过了多少层？

浏览器发一个请求：

```text
/api/orders
```

看起来很简单。

但真实系统可能是：

Browser  
↓  
HTTP / TLS  
↓  
API Gateway / BFF  
↓  
Go Service  
↓  
Redis  
↓  
PostgreSQL  
↓  
返回结果  
↓  
BFF 整形  
↓  
Browser Rendering

每一层都有责任：

前端：体验和交互。

BFF：聚合、协议适配、权限入口。

业务服务：规则、认证、事务。

数据库：持久化事实。

我特别喜欢一句话：

> **前端负责体验，服务端负责规则，数据库负责事实。**

当系统越来越复杂时，边界就是维护成本。

## X

**Title:** A simple API request crosses more boundaries than you think.

A “simple” API request may actually be:

Browser  
→ HTTP/TLS  
→ BFF/API  
→ Service  
→ Cache  
→ Database  
→ Service  
→ BFF  
→ Browser

A useful ownership rule:

**Frontend owns experience.  
Backend owns rules.  
Database owns durable truth.**

And the browser should not directly own database privileges.

08/10

## LinkedIn

**Title:** An API request is a chain of boundaries, not just a frontend call.

An API request is rarely just “frontend calls backend.”

In a production system it may cross several boundaries:

Browser → HTTP/TLS → BFF/API → domain service → cache → database → response composition → browser.

Each layer exists for a reason.

A mental model I find useful:

**Frontend owns experience.**

**Services own business rules.**

**Databases own durable facts.**

Explicit boundaries also make security, tracing, caching and failure analysis much easier.
