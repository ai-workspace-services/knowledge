# 内容链路缓存契约（portal → content-service → knowledge）

面向 Cloudflare Workers/Pages 免费额度的静态优先渲染约定。适用于 5 个 SSR
boundary Worker（`frontend-ssr-*`）；VPS/Selfhost 运行时不受影响。

## 1. 为什么要改

改造前，`/blogs`、`/docs/*`、`/support`、`/products/*` 全部是
`dynamic = "force-dynamic"` + `revalidate = 0`，并且 `docsServiceClient` 用
`cache: "no-store"` 取数。结果是：

- 每一次页面访问都触发一次 SSR Worker 渲染（计入 Worker 请求额度）；
- 每一次渲染都向 Cloud Run 上的 content-service 发一次子请求（计入 Cloud Run
  请求额度，并叠加冷启动延迟）；
- content-service 每 `DOCS_RELOAD_INTERVAL`（默认 5 分钟）才从 knowledge 仓库
  重建一次快照，**这些实时请求换不来更新的内容**，只是重复取同一份快照。

## 2. 现在的分层

```text
knowledge (Git)
   │  push → Publish Content Release workflow（秒级）
   │  + DOCS_RELOAD_INTERVAL 轮询兜底（5 分钟）
   ▼
content-service（Cloud Run，内存快照）
   │  ETag = contentHash + 请求目标 + 语言
   │  Cache-Control: s-maxage=<reload 间隔>, stale-while-revalidate
   ▼
portal SSR boundary Worker
   │  fetch → Next Data Cache（next.revalidate + tags）
   │  page  → 预渲染 / ISR，存入 incremental cache
   │  incremental cache = 各 colo 的 Cache API → R2/KV
   ▼
浏览器
```

一次内容页访问的下游请求数：改造前每次渲染 1 次 Cloud Run 调用，改造后在
revalidate 窗口内为 0。

## 3. 渲染约定

| 路由 | 渲染方式 | revalidate |
| :--- | :--- | :--- |
| `/blogs` | 预渲染 | 300s |
| `/blogs/[...slug]` | `generateStaticParams` + ISR，`dynamicParams` 允许新文章按需渲染 | 300s |
| `/docs/[collection]`、`/docs/[collection]/[...slug]` | 同上 | 300s |
| `/support` | 预渲染 | 300s |
| `/products/*` | 预渲染（取不到 content-service 时回落到 `src/data/content/*.json`） | 900s，实际受 fetch 窗口收敛到 300s |
| `/download`、`/download/[...segments]` | 预渲染，清单每小时回源一次 | 3600s |
| `/sitemap.xml` | 预渲染 | 3600s |
| `/login`、`/logout`、`/register`、`/email-verification` | 保持 `force-dynamic` | — |

`/login`、`/logout` 的 `force-dynamic` 是跨 boundary 软导航挂死的修复
（见 PR #241），**不要**为了静态化把它改回去。

### 构建期取不到 content-service 时

`generateStaticParams` 与内容页正文都会捕获异常：预渲染降级为按需渲染 +
ISR 缓存，构建不会失败。代价是首次访问那一下要真渲染一次。**要拿到完整的
构建期预渲染，CI 必须能访问 content-service**：

```bash
DOCS_SERVICE_URL=https://<content-service>   # 或 runtime-config 中的 docsServiceUrl
INTERNAL_SERVICE_TOKEN=<X-Service-Token>
```

缺任意一个都会在构建日志里留下 `Skipping blog prerender` /
`Skipping docs prerender` 的告警，可据此判断。

## 4. 语言

`LanguageProvider` 的首屏渲染在任何运行时都固定为 `zh`，浏览器偏好在 hydrate
之后才生效。服务端取内容因此也钉死同一个默认语言（`CONTENT_LANGUAGE_MODE=static`，
默认值），否则同一个 URL 会因为 `Accept-Language` 产生多份文档，静态化无从谈起。

- 需要按访问者语言协商的地方走动态 API：`/api/docs/catalog`、`/api/docs/search`、
  `/api/blogs/latest` 依然读取 `x-language` / `accept-language`。
- `CONTENT_LANGUAGE_MODE=request` 可恢复逐请求协商，代价是这些页面重新变成动态
  渲染。VPS/Selfhost 运行时可以这样跑，渲染在那边不花额度。
- 默认语言由 `NEXT_PUBLIC_DEFAULT_LANGUAGE` 决定（`en` 以外的值都按 `zh` 处理）。

## 5. Incremental cache 绑定

`open-next.config.ts` 与 `scripts/build-open-next-boundary.mjs` 共用
`scripts/incremental-cache-target.mjs`，override 与 wrangler 绑定不会跑偏。

| 环境变量 | 作用 |
| :--- | :--- |
| `PORTAL_INCREMENTAL_CACHE` | `r2`（推荐）/ `kv` / `assets` / `none`。不设则按下面两个变量推断，都没有就是 `none` |
| `PORTAL_INCREMENTAL_CACHE_BUCKET` | R2 桶名，绑定为 `NEXT_INC_CACHE_R2_BUCKET` |
| `PORTAL_INCREMENTAL_CACHE_KV_ID` | KV namespace id，绑定为 `NEXT_INC_CACHE_KV` |
| `CONTENT_REVALIDATE_SECONDS` | 内容 fetch 的 revalidate 窗口，默认 300 |

选型：R2 免费额度（每月 100 万次 A 类 / 1000 万次 B 类操作）足以覆盖 ISR 写入；
KV 免费额度每天只有 1000 次写，页面一多就会被 revalidate 写爆。`withRegionalCache`
在两者前面加了一层 colo 本地 Cache API，热页面不消耗 R2/KV 操作数。

`assets` 只读，适合完全不需要 revalidate、只要构建期预渲染的场景。

### 部署

```bash
yarn build:ssr:content
yarn deploy:ssr --boundary content
```

`deploy:ssr` 会先 `opennextjs-cloudflare populateCache remote` 把构建期预渲染
灌进 R2/KV，再 `wrangler deploy`。**只跑 `wrangler deploy` 会留下一个空缓存**，
预渲染产物白做，所有页面都要等第一次访问才生成。

## 6. 热加载还在

内容更新不需要重新部署 portal：

1. knowledge 仓库 `content/**` 合入 main → `Publish Content Release` workflow
   调用 content-service `POST /api/v1/admin/reload?pull=true`（秒级）；
2. 兜底仍是 content-service 自己的 `DOCS_RELOAD_INTERVAL` 轮询；
3. portal 的 ISR 窗口（300s）到期后，后台重新取数换页面，读者拿到的始终是
   已缓存的那一份，不会等在渲染上。

端到端可见延迟 ≈ ISR 窗口。要做到秒级，需要在 boundary 上加 tag cache
（D1 或 Durable Object）并从 content-service 回调 `revalidateTag('content')`；
当前没有引入，因为它换来的新鲜度对文档站没有意义，却要多一个绑定。

## 7. 还没做的

- **frontend-router 的 Cache API**：路由 Worker 目前对每个请求都转发到 boundary
  Worker，一次 HTML 访问因此是 2 次 Worker 调用。在 router 里按
  （path + 归一化语言）读写 `caches.default`，命中时可以省掉 boundary 那一次。
- **静态资产旁路**：已由 `NEXT_PUBLIC_STATIC_CDN_URL` 解决（PR #242 / #243），
  `_next` 与 `_edge/*` 直连 Pages CDN，不再穿透 Worker。
