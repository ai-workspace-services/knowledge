# 08 / 10｜AI 设计 API 时，不能只画一条调用线

## 微信 / 朋友圈

AI 可以很快生成一个 `GET /api/user`，但一个 API 请求真正重要的，不是“能不能调通”，而是：

**它经过哪些边界？每一层负责什么？失败以后能不能查清楚？**

一次看似简单的请求，可能经过：

**Browser  
→ HTTP / TLS  
→ API / BFF  
→ Go Service  
→ Redis  
→ PostgreSQL  
→ Service  
→ BFF  
→ Browser**

### 让 AI 设计 API 时，先明确 5 件事

1. **调用者是谁？** 浏览器、移动端、内部服务还是后台任务？
2. **谁负责鉴权？** 网关、BFF 还是业务服务？
3. **谁拥有业务规则？** 不要把关键校验只放在前端。
4. **谁拥有持久化事实？** 数据库不能被浏览器直接访问。
5. **如何观察失败？** 每一层都需要状态码、日志、Trace 或指标。

一个清晰的所有权模型是：

**前端负责体验。**  
**服务端负责规则。**  
**数据库负责事实。**

## 如何排查 API 请求失败？

按请求路径从外到内排查：

1. **Browser**：请求是否发出？URL、参数、Cookie、Token 是否正确？
2. **HTTP / TLS**：是否被 CORS、证书、代理或网关拦截？
3. **API / BFF**：路由、鉴权、协议转换和参数校验是否通过？
4. **Service**：业务规则、事务和依赖调用是否失败？
5. **Cache / Database**：缓存是否过期、击穿，数据库是否超时或数据不存在？
6. **Response**：返回的是传输错误、HTTP 错误还是业务错误？

不要只让 AI “修复请求失败”，而要给它完整链路、错误日志和预期契约。

> **API 设计不是把前端连到数据库，而是设计一条可验证、可观察、可控的信任边界。**

## 小红书

**标题：**

> AI 写 API 之前，先画清楚这条请求经过哪些边界

浏览器发一个请求：

```text
/api/orders
```

AI 可能很快帮你写出调用代码，但真实系统通常不是：

**Browser → Database**

而是：

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

### AI 设计 API 时，先问 5 个问题

1. 谁在调用？
2. 谁负责鉴权？
3. 谁负责业务规则？
4. 谁拥有最终数据？
5. 出错时去哪里查？

每一层的责任最好明确：

- **前端**：体验、交互和展示
- **BFF**：聚合、协议适配和权限入口
- **业务服务**：规则、认证、事务
- **数据库**：持久化事实

### API 失败怎么排查？

按链路从外到内：

1. 浏览器有没有发出请求？
2. URL、参数、Cookie、Token 是否正确？
3. 是否被 CORS、TLS、网关或代理拦截？
4. BFF 的路由和参数校验是否通过？
5. 业务服务或数据库是否超时？
6. 返回的是 HTTP 错误还是业务错误？

尤其要记住：

> **不要让 Browser 直接拥有数据库权限。**

AI 可以帮你补齐 API 代码，但边界、权限和错误契约必须由人先定义。

## X

**Title:** AI should design API boundaries, not just generate fetch calls.

A request like `GET /api/user` may cross:

Browser → HTTP/TLS → BFF/API → Service → Cache → Database → Service → Browser

Before asking AI to design the endpoint, define:

1. Who is calling?
2. Where is authentication enforced?
3. Which layer owns business rules?
4. Which system owns durable truth?
5. How will each failure become observable?

Debug from the outside inward:

1. Browser: request, URL, params, cookies, token.
2. Transport: CORS, TLS, proxy, gateway.
3. BFF: routing, auth, validation, composition.
4. Service: business rules, transactions, dependencies.
5. Cache/database: expiry, latency, consistency, missing data.
6. Response: transport, HTTP, or business error?

**Frontend owns experience. Services own rules. Databases own durable truth.**

08/10

## LinkedIn

**Title:** Designing AI-assisted APIs around trust, ownership and observability

An API request is not merely a frontend call. It is a chain of runtime, trust and data boundaries.

A production request may cross:

Browser → HTTP/TLS → BFF/API → domain service → cache → database → response composition → browser.

When asking AI to design an endpoint, make five responsibilities explicit:

1. **Caller** — browser, mobile client, internal service or background job.
2. **Authentication** — where identity and authorization are enforced.
3. **Business rules** — which service owns validation, transactions and invariants.
4. **Durable truth** — which data store is authoritative.
5. **Observability** — how latency, errors, traces and dependency failures are recorded.

When a request fails, debug it along the actual path:

1. Verify the client request and runtime configuration.
2. Check transport, TLS, CORS, proxy and gateway behavior.
3. Check BFF routing, authentication and contract validation.
4. Check service rules, transactions and dependency calls.
5. Check cache behavior and database latency or consistency.
6. Separate transport errors, HTTP errors and business errors.

The key security principle remains simple:

> **The browser should not own database privileges.**

AI can generate the endpoint implementation, but engineers still need to define the trust boundary, ownership model, error contract and verification path.

