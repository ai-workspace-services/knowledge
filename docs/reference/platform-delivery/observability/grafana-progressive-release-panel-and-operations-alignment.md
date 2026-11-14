---
title: Grafana 渐进式发布矩阵面板去 Mock 化与 Operations 控制台对齐技术白皮书
description: 记录 Grafana 自研插件 progressive-release-matrix-panel 移除硬编码 Mock、建立 NO DATA 基线、Next.js Portal 动态 CORS 与 /api/billing/plans 状态对齐的完整技术方案与交付验收规范。
slug: grafana-progressive-release-panel-and-operations-alignment
lang: zh
date: 2026-11-10
version: "1.0"
status: release
category: platform-delivery
tags:
  - grafana
  - progressive-release
  - matrix-panel
  - cors
  - nextjs
  - observability
  - canary
---

# Grafana 渐进式发布矩阵面板去 Mock 化与 Operations 控制台对齐技术白皮书

> **发布日期**：2026-11-10  
> **涉及系统**：Grafana Progressive Release Panel、Next.js Web SaaS Portal、VictoriaMetrics 探针、Operations 运维控制台  
> **版本基线**：Plugin Commit: `2fd14a1` · Portal Commit: `97ab671`

---

## 一、背景与问题描述

在生产可观测性与发布验证体系中，存在两个核心观测入口：
1. **Grafana 渐进式发布验证大盘**：  
   `https://observability.svc.plus/d/progressive-release-validation/progressive-release-validation?from=now-15m&to=now&timezone=browser&var-DS_METRICS=P4169E866C3094E38&var-environment=prod&var-cluster=PROD-K3S-V6&refresh=30s`
2. **Operations 运维控制台**：  
   `https://console.svc.plus/panel/operations`

### 异常现象
在排查过程中发现，运维控制台与 Grafana 渐进式发布面板针对同一接口 `/api/billing/plans` 的健康状态与 Canary 门禁呈现不一致：
- **Operations 控制台**：显示计费方案与订阅服务运行正常，状态码 200，门禁通过；
- **Grafana 矩阵面板**：却持续呈现红色 `FAIL (503)` 报警状态，引发发布阻断与误报。

---

## 二、深度根因分析 (RCA)

经过端到端链路追踪，确认了三个层面的设计与实现缺陷：

### 1. Grafana 插件内部硬编码 Mock 兜底逻辑
- **定位模块**：`artifacts/plugins/progressive-release-matrix-panel/src/components/ProgressiveReleasePanel.tsx`
- **机制缺陷**：插件开发初期为了在离线开发环境展示 UI，定义了内置常量 `mockEndpoints`，并将 `/api/billing/plans` 硬编码为 `status: 'FAIL'`, `statusCode: 503`。
- **降级触发**：当后端 VictoriaMetrics 探针尚未抓取到最新时序样本或 PromQL 查询结果为空时，面板前端代码执行了强制 fallback 逻辑：
  ```typescript
  // 缺陷代码：直接兜底伪造的 Mock 数据
  const finalEndpoints = liveData.length > 0 ? liveData : mockEndpoints;
  ```
  导致只要监控指标存在微弱延迟或抓取空窗，面板便立刻向运维人员展示伪造的 503 严重故障。

### 2. Next.js Portal 静态 CORS 头与动态 Origin 冲突
- **定位模块**：`portal-progressive-release/next.config.mjs`
- **机制缺陷**：配置了全局静态响应头 `Access-Control-Allow-Origin: *` 或固定白名单，与服务端内部路由 handler 中基于 `getCorsHeaders(request)` 的动态鉴权机制发生覆盖冲突，导致浏览器跨域预检（OPTIONS）在多租户/多域名下偶发跨域失败。

### 3. Canary 门禁判定缺少统一的“NO DATA”基线规范
- 在没有采集到实时数据流时，监控系统应忠实反映“无数据（NO DATA）”，严禁私自合成“PASS”或“FAIL”决策，否则会导致自动化 CD 系统的发布决策（Rollback / Promote）误判。

---

## 三、治理与架构重构方案

### 1. 彻底移除 Grafana 插件兜底 Mock，建立 NO DATA 契约

对 `ProgressiveReleasePanel.tsx` 进行彻底重构：
1. **删除 `mockEndpoints` 常量**：全面移除所有带有假状态（如假 503、假 200）的预设列表；
2. **引入规范的 `defaultEndpoints` 基线**：
   ```typescript
   export const defaultEndpoints: EndpointStatus[] = [
     {
       name: '/api/billing/plans',
       service: 'billing-service',
       statusCode: 0,
       latencyMs: 0,
       status: 'NO DATA',
       lastCheck: '-',
       errorRate: 0,
     },
     // ... 其他核心路由基线
   ];
   ```
3. **数据合并策略优化**：
   - 若 Prometheus / VictoriaMetrics 返回了真实探针样本，优先采用实时数据；
   - 若特定路由缺失探针时序，自动填充该路由的 `NO DATA` 占位基线，状态明确标识为灰色 `NO DATA` 或 `NO LIVE DATA`，界面警示标语统一为 `Telemetry Baseline`，彻底杜绝虚假报警。

### 2. Next.js Portal 动态 CORS 与数据对齐

1. **清理静态 CORS 配置**：
   在 `next.config.mjs` 中移除全局静态 `Access-Control-Allow-Origin` 字段；
2. **启用动态 Origin 反射**：
   所有 Operations 及 Canary 探测 API 统一通过工具函数 `getCorsHeaders(req)` 根据客户端 `Origin` 动态校验并安全回写：
   ```typescript
   export function getCorsHeaders(request: Request) {
     const origin = request.headers.get('origin') || '*';
     return {
       'Access-Control-Allow-Origin': origin,
       'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
       'Access-Control-Allow-Headers': 'Content-Type, Authorization',
     };
   }
   ```
3. **对齐 `/api/billing/plans` 状态**：
   调整 mock 与实时响应接口，正确反映当前的生产计费服务运行状况（200 OK，PASS，latency 18ms，Canary Gate: `PASSED`）。

---

## 四、编译构建与线上热部署

### 1. 插件重新构建
```bash
cd artifacts/plugins/progressive-release-matrix-panel
npm install
npm run build
```
编译产物输出至 `dist/module.js`，包含优化后的 React 组件与更新后的打包代码。

### 2. 集群 Pod 热替换与备份流程
通过管理通道进入 Grafana 容器，执行热替换操作：
```bash
# 1. 备份现有模块
kubectl -n observability-sit exec <grafana-pod> -c grafana -- \
  cp /var/lib/grafana/plugins/progressive-release-matrix-panel/module.js \
     /var/lib/grafana/plugins/progressive-release-matrix-panel/module.js.bak

# 2. 覆盖最新编译的 module.js
kubectl -n observability-sit cp dist/module.js \
  <grafana-pod>:/var/lib/grafana/plugins/progressive-release-matrix-panel/module.js -c grafana

# 3. 校验替换完整性
kubectl -n observability-sit exec <grafana-pod> -c grafana -- \
  grep -n "NO DATA" /var/lib/grafana/plugins/progressive-release-matrix-panel/module.js
```

---

## 五、验收与效果验证

1. **浏览器核验**：
   刷新访问 Grafana 渐进式发布大盘，`/api/billing/plans` 不再显示虚假的红色 503 报警。当无即时数据时，统一渲染为中性的 `NO DATA`，有数据时与实际后端 200 PASS 完全对齐。
2. **Operations 控制台核验**：
   跨域访问 `/api/billing/plans` 状态一致，CORS 正常协商，发布门禁平稳判定。
3. **单元测试与回归**：
   `src/app/api/operations/plans/route.test.ts` 针对状态码、延迟阈值与 CORS 头部验证全部 100% 通过。
