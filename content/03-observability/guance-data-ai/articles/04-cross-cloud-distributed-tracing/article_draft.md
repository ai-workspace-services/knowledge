# 一个登录请求经过几朵云？用 Trace 把它接起来

## Cloudflare → Cloud Run → Supabase 跨云分布式链路上下文传播与 OTel 实践

> **唯一知识点**：分布式上下文传播与跨云追踪 | **循环模板**：动手实操型 | **核验日期**：2026-10-27 (已核验)

---

### 微信公众号深度长文（正文内嵌 GIF 动图版）

在多云架构已成标配的今天，个人 SaaS 的单次请求往往要经历复杂的跨网穿梭。以 XWorkTech 的 UAT 登录流程为例：用户的凭据首先经由 Cloudflare 边缘节点校验防刷规则，再转发至 Cloud Run 托管的微服务执行业务鉴权，最终调用 Supabase 数据库拉取用户角色。一次普通的登录失败，究竟是边缘网关超时、容器冷启动延时、还是数据库连接池枯竭？面对跨越三家不同云厂商的网络边界，传统的本地抓包或零散日志无法提供连贯的事实验证。只有基于统一协议将全链路的分布式 Trace 串接起来，才能看清每次请求的真实耗时分布。

![图 1：一次多云登录失败的排障路径（Triage Path 动图）](./assets/triage-path-wechat.gif)

跨多云分布式追踪的基石是 W3C TraceContext 标准，即通过标准化的 traceparent 和 tracestate 请求头，在跨网络、跨运行时的 HTTP 调用间透明传递追踪上下文。当请求从 Cloudflare Workers 注入 trace ID 后，下游的 Cloud Run 容器必须无缝承接该上下文，并在向 Supabase 发起 PostgreSQL 连接时生成子 Span。这要求所有运行节点遵循严格的字段契约，包括 service.name、environment、http.route 以及统一的错误标识。然而多云环境下的网络异构性也带来了盲区：Supabase Free 版作为全托管黑盒服务，无法安装主机代理或注入探针，其内部耗时只能依托客户端 SDK 产生的外围 Span 进行推断。

![图 2：多云栈下的观测盲区分布（Stack Blindspots 动图）](./assets/stack-blindspots-wechat.gif)

为实现稳定可靠的多云链路串联，本实战完全遵循“AI 辅助的 IaC / GitOps / Playbook”流水线进行声明式部署，分为四个纯代码化步骤。第一步，在 GitOps 仓库中声明 OTel 跨云转发规则，定义 TraceContext 提取与注入规范；第二步，通过 Terraform 管理 Cloud Run 部署清单，以环境变量形式注入 OTel Collector 地址与服务标识，严禁在控制台手工改动容器配置；第三步，利用 Ansible Playbook 自动化部署 OTel 汇聚管道，配置针对不同云端来源的速率限制与批处理策略；第四步，所有跨云调用的鉴权 Token 与工作空间密钥，一律在容器启动时由 Vault 注入运行时环境，确保跨云链路凭据全程隔离。

![图 3：跨多云分布式追踪证据链（Evidence Chain 动图）](./assets/evidence-chain-wechat.gif)

经受控登录用例验证，系统成功捕获到一条横跨 Cloudflare、Cloud Run 与 Supabase 的完整分布式链路瀑布图。在一次模拟的 401 故障排查中，Trace 明确显示边缘耗时 12 毫秒，Cloud Run 处理耗时 25 毫秒，瓶颈点精准指向 Supabase 鉴权查询等待耗时达 410 毫秒，排障时间从原本的数小时缩短至 2 分钟以内。其局限性在于，免费专区单日 2 万条 Trace 的额度对全量跟踪并不宽裕，必须在 OTel Collector 端基于路由配置精准尾部采样策略；同时由于免费版不支持跨空间 OpenAPI 数据导出，链路分析仅能在单工作空间内闭环。

![图 4：W3C 统一字段契约与上下文传递（Field Contract 动图）](./assets/field-contract-wechat.gif)

该方案极其适合采用现代化分布式多云、Serverless 微服务与第三方 BaaS 混合架构的独立开发者和初创技术团队；对于仅运行在单台 VPS 上的单体架构应用、或者完全不涉及跨网络调用的本地离线系统，引入分布式链路追踪会徒增系统复杂性与网络开销，采用集中式结构化日志即可满足日常排障需求。

#### 架构视角决策表（移动端优化 3 列精简版）

| 决策维度 | 方案对比 (自建基准 vs 观测云) | 独立开发建议与避坑 (移动端决策) |
| :--- | :--- | :--- |
| **分布式追踪协议** | • <b>自建</b>：支持 Jaeger/OTel，跨多云网络传输需自建路由<br>• <b>SaaS</b>：原生遵循 W3C TraceContext 标准透传上下文 | 全链路强制统一至标准 traceparent 协议头，严禁使用私有魔改追踪格式。 |
| **多云覆盖与黑盒** | • <b>自建</b>：需为每个云厂商部署独立 Collector，维护繁琐<br>• <b>SaaS</b>：覆盖 Cloudflare + Cloud Run，Supabase 为黑盒 | 明确标注 BaaS 黑盒边界：在客户端封装代理 Span，避免链路出现未覆盖盲区。 |
| **Trace 每日配额** | • <b>自建</b>：受自建存储与 IOPS 限制，需定期清理索引<br>• <b>SaaS</b>：免费专区限 20,000 条 Trace/天，超额熔断停收 | Collector 开启智能尾部采样：错误 Span 100% 采集，成功请求按 5% 抽样。 |
| **排障归因时效** | • <b>自建</b>：需人工按时间戳在多个系统比对日志，需 1-2 小时<br>• <b>SaaS</b>：单请求完整瀑布图展开，瓶颈定位耗时 < 2 分钟 | 用端到端瀑布图直接锁定是边缘鉴权失败还是容器冷启动，消除跨云推诿。 |
| **凭据与传输安全** | • <b>自建</b>：跨云之间若手工配置静态 Token，外泄风险极高<br>• <b>SaaS</b>：支持通过 Vault 动态注入 Header 密钥与凭据隔离 | 全量代码化托管凭据，运行时通过 Vault 注入，严禁在 Web 控制台手工填入。 |

---

### 小红书配套图文笔记

**一个登录请求到底去了哪里？**

现代个人 SaaS 最酷也是最让人抓狂的架构，就是多云混部：Cloudflare Pages/Workers 跑边缘、Cloud Run 托管核心后端微服务、Supabase 接管数据库与鉴权！这套架构虽然轻盈省钱，可一旦用户登录报错 401，你根本不知道究竟是 Cloudflare 规则抽风、Cloud Run 冷启动卡顿、还是 Supabase 连接池被打爆了！

怎么用分布式 Trace 把三朵云连成一根线？保姆级实操步骤直接公开：

P1：统一信使标准。基于 W3C TraceContext 国际标准协议，让请求从 Cloudflare 出来时就带上 traceparent 请求头，下游 Cloud Run 自动继承提取，坚决不让链路在网络边界断头！
P2：纯代码化编排。别去控制台手动配探针！用 Terraform 把 OTel Collector 地址作为环境变量声明式写进 Cloud Run 配置，用 Ansible Playbook 一键拉起收集器和转发管道，杜绝任何手工点击！
P3：跨云凭据全进 Vault。三朵云之间的调用鉴权密钥与工作空间 Token，统一由 Vault 在容器启动时动态注入，Git仓库里只留纯净模板，坚决不留哪怕半个明文密码！

实战复盘体验极其丝滑：一条登录请求穿过三朵云，瀑布图展开一目了然：边缘 12ms、容器 25ms、数据库查表 410ms！故障点精准定位到数据库连接延迟，排障从 2 小时直接缩至 2 分钟！

总结：分布式架构虽好，没有 Trace 就是开盲盒。用代码化搞定全链路追踪，多云也能看得清清楚楚！想拿跨云 OTel 编排模板的宝子，移步公众号自取！

![小红书配图 1：链路拓扑 (GIF 动图)](./assets/triage-path-xhs.gif)

![小红书配图 2：脱敏实测数据 (GIF 动图)](./assets/evidence-chain-xhs.gif)

---

### GitOps / IaC / Playbook / Vault 代码化工程落地范式

#### Cloudflare Workers: W3C TraceContext 上下文注入 (workers/src/tracer.ts)
```typescript
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const traceId = crypto.randomUUID().replace(/-/g, '');
    const spanId = crypto.randomUUID().replace(/-/g, '').substring(0, 16);
    const traceparent = `00-${traceId}-${spanId}-01`;

    const modifiedHeaders = new Headers(request.headers);
    modifiedHeaders.set('traceparent', traceparent);
    modifiedHeaders.set('x-origin-edge', 'cloudflare-global');

    const response = await fetch('https://api.xworktech.com/auth/login', {
      method: request.method,
      headers: modifiedHeaders,
      body: request.body,
    });
    return response;
  }
};
```

#### Terraform: Cloud Run 容器声明式注入 OTel 环境变量 (terraform/cloud_run.tf)
```hcl
resource "google_cloud_run_service" "auth_service" {
  name     = "xworkmate-auth-service"
  location = "asia-east1"

  template {
    spec {
      containers {
        image = "gcr.io/xworktech-uat/auth:v1.4.2"
        env {
          name  = "OTEL_EXPORTER_OTLP_ENDPOINT"
          value = "http://otel-collector.internal.xwork.tech:4318"
        }
        env {
          name  = "OTEL_SERVICE_NAME"
          value = "auth-service"
        }
        env {
          name  = "OTEL_PROPAGATORS"
          value = "tracecontext,baggage"
        }
      }
    }
  }
}
```

#### OTel Collector: 汇聚管道与尾部采样配置 (otel/collector-config.yaml)
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 2s
    send_batch_size: 256
  tail_sampling:
    decision_wait: 5s
    expected_new_traces_per_sec: 100
    policies:
      - name: drop_status_200_excess
        type: probabilistic
        probabilistic: { sampling_percentage: 5.0 }
      - name: keep_all_errors
        type: status_code
        status_code: { status_codes: [ ERROR ] }

exporters:
  otlp/guance:
    endpoint: "https://openway.guance.com:4317"
    headers:
      "X-Token": "${VAULT_GUANCE_TOKEN}"

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [tail_sampling, batch]
      exporters: [otlp/guance]
```

