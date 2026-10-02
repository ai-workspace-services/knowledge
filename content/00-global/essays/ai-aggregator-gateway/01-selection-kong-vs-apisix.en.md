---
title: "No More Multi-Account Switching: Building Your Personal All-in-One AI Aggregator Gateway (Part 1) — Technology Selection: Kong vs APISIX"
description: An in-depth evaluation of architectural trade-offs for personal and small-team AI aggregator gateways. Comparing Kong vs APISIX Standalone across GitOps workflows, control plane dependencies, AI proxy plugin ecosystems, and operational overhead.
slug: ai-aggregator-gateway-01-selection
lang: en
date: 2026-10-01T00:00:00Z
author: shenlan
tags:
  - ai-gateway
  - apisix
  - kong
  - home-lab
  - architecture
category: essays
---

# No More Multi-Account Switching: Building Your Personal All-in-One AI Aggregator Gateway (Part 1)

> **Editor's Note**: In today's flourishing ecosystem of AI developer tools, engineers constantly juggle multiple subscription accounts, API keys, distinct base URLs, and divergent protocol endpoints. As the opening piece of the "All-in-One AI Aggregator Gateway" practical guide, this article explores the architectural background, component responsibilities, and why Apache APISIX Standalone was selected over Kong for this deployment.

![Engineering Decision Canvas: AI Gateway Technology Selection](/assets/images/gateway-canvas-01-selection.png)

---

## 1. The Problem: Fragmented AI Productivity

With the rapid emergence of agentic workflows and AI-assisted programming, modern engineering toolchains have become severely fragmented:
* **Command-Line Terminals**: Constantly running Codex CLI, Claude Code, Google Gemini CLI, and custom agent daemons.
* **IDEs and Editors**: Configured with Google Antigravity, Android Studio, Cursor, and various VS Code extensions.
* **Workflows and Automation**: Writing Python and Node.js code utilizing official OpenAI, Anthropic, or xAI SDKs.
* **Account and Resource Management**: Managing multiple ChatGPT Plus/Pro personal subscriptions, Claude Team subscriptions, Google accounts, and several pay-as-you-go commercial API keys.

In daily practice, this multi-origin reality creates substantial friction:
1. **Endpoint and Authentication Sprawl**: Different tools impose divergent expectations for Base URLs, authentication headers (`Authorization: Bearer` vs `x-api-key`), and model identifier mappings.
2. **Imbalanced Quota Utilization**: Some subscriptions sit idle near the end of billing cycles, while others repeatedly trigger strict hourly or weekly rate limits.
3. **Absence of Transparent Failover**: When a specific upstream subscription experiences temporary network turbulence or upstream security blocks, terminal agents typically crash without graceful retries or fallback mechanisms.

Our objective is crystal clear: **Build a unified AI Aggregator Gateway within a Home-Lab or small-team private network. Expose a single HTTPS domain and a unified token, maintain full compatibility with mainstream AI protocols, and aggregate personal subscription accounts alongside commercial API keys into a resilient, load-balanced, and securely isolated ingress.**

---

## 2. High-Level Architecture and Component Responsibilities

To achieve minimal operational overhead without sacrificing scalability, we eschew monolithic all-in-one servers in favor of a decoupled, layered component matrix:

| Core Component | Primary Responsibilities | Deployment Model & Storage Dependency |
| :--- | :--- | :--- |
| **Caddy** | Edge TLS termination, automated certificate lifecycle, reverse proxying | Native systemd service, static configuration |
| **APISIX** | Unified authentication, IP whitelisting, tenant ACL, dynamic rate limiting, routing & audit logging | Standalone file mode, systemd, no etcd/DB dependency |
| **New API** | Unified model catalog, Model Alias mapping, CPA channel load balancing & health checking | systemd service, PostgreSQL database |
| **LiteLLM** | Commercial pay-as-you-go API adaptation (OpenAI/Anthropic/xAI), retries, token usage & cost tracking | systemd service, independent PostgreSQL DB |
| **CLIProxyAPI (CPA)** | Single-account OAuth subscription adaptation, local protocol emulation (OpenAI/Claude) | Multi-instance matrix, dedicated Unix user & systemd unit per instance |
| **Vault** | Database connection strings (DSN), gateway credentials, official provider API keys | Secret retrieval during orchestration; injected into memory tmpfs at runtime |

### Core Architectural Separation

In this design, **LiteLLM and New API function as parallel upstreams**:
* **New API** aggregates the CPA account matrix, exposing a unified model namespace via Model Alias mechanisms.
* **LiteLLM** connects directly to commercial pay-as-you-go provider endpoints, managing complex error retries and cost calculations.
* **LiteLLM is strictly prohibited from serving as a reverse proxy in front of CPA**. This boundary prevents cascading retries, double billing accounting, and unnecessary latency overhead.

---

## 3. Gateway Decision: Why APISIX Standalone Over Kong?

As the gatekeeper of all incoming traffic, API gateway stability is paramount. In modern infrastructure, Kong and Apache APISIX are the primary contenders. In this implementation, we opted for **APISIX Standalone**, driven by **declarative GitOps contracts, zero database dependencies, and open-source multi-model routing capabilities**:

| Dimension | Kong | Apache APISIX | Decision Rationale for This Project |
| :--- | :--- | :--- | :--- |
| **Configuration Backend** | Traditional mode requires PostgreSQL; DB-less mode loads YAML/JSON via decK | Traditional mode requires etcd; **Standalone mode reads local `apisix.yaml` directly** | We enforce a **file-driven GitOps reconciliation model**. APISIX Standalone completely eliminates database and etcd dependencies, minimizing the operational footprint. |
| **PostgreSQL Requirement** | Native support for configuration storage in Traditional mode | Not used as a native configuration store | If relational database-backed dynamic entity management is required, Kong is a strong contender; for file-driven GitOps, zero DB is vastly simpler. |
| **Generic Gateway Features** | Robust authentication, ACLs, route rewrites, rate limiting, and extensive plugin ecosystem | Consumer authentication, route groups, plugin chains, multi-tenant ACLs | Both platforms are equally capable of acting as an enterprise-grade security and traffic control barrier. |
| **AI Proxy Capabilities** | Built-in `ai-proxy`; multi-model scheduling and advanced features require `ai-proxy-advanced` | Open-source ecosystem provides `ai-proxy` and `ai-proxy-multi` | While both offer AI adaptations, Kong's advanced capabilities carry commercial enterprise licensing boundaries; APISIX's `ai-proxy-multi` is fully open-source Apache software. |
| **Dynamic Tenant Management** | Traditional mode updates entities dynamically via Admin API | Standalone mode reconciles state by re-rendering and applying complete YAML declarations | For individual engineers and small teams, declarative file reconciliation followed by seamless reloads is preferable to maintaining a dynamic control plane. |
| **Multi-Node Rate Limiting** | Relies on shared distributed storage (e.g., Redis) or local memory | Local `limit-count` mode tracks quotas in single-node memory | A single node provides ample throughput for Home-Lab environments; Redis-backed shared quotas can be integrated when scaling horizontally. |
| **Operational Overhead** | Traditional mode introduces DB migrations, schema backups, and connection pooling | Standalone mode eliminates control plane components entirely | Fewer moving parts directly translates to higher Mean Time Between Failures (MTBF). |

---

## 4. Operational Trade-Offs and Boundary Conditions

Adopting APISIX Standalone provides a clean, minimal operational footprint, but requires adhering to specific engineering constraints:

1. **Strict Runtime Environment Pinning**: The gateway operates on pinned APISIX 3.16.0 source code built against a dedicated OpenResty runtime. Early test deployments encountered missing shared Lua libraries, uninitialized shared memory dictionaries (`lua_shared_dict`), and file permission issues for worker processes. These dependencies, build parameters, and directory permissions must be strictly codified in Ansible roles rather than relying on unvetted container images.
2. **Surrendering Dynamic REST Control Planes**: Standalone mode does not support incremental route updates via HTTP Admin APIs. All tenant additions, routing tweaks, and rate limit adjustments must flow through the GitOps pipeline: modify declarative specs → render `apisix.yaml` → trigger graceful service reload.
3. **Mutual Exclusivity Enforcement**: Legacy Kong installations on the node were disabled and stopped to eliminate port conflicts, competing runtime daemons, and troubleshooting ambiguity.

---

## 5. Summary

Technology selection is the art of balancing **operational complexity, organizational scale, and infrastructure control**. By combining Caddy, APISIX Standalone, New API, LiteLLM, and CPA, we establish a robust, declarative foundation that eliminates redundant control plane databases.

In the next installment, we will dive inside the gateway's routing and security layers:
**"No More Multi-Account Switching: Building Your Personal All-in-One AI Aggregator Gateway (Part 2) — Architecture: Dual-Layer Routing & Traffic Hub"**.

---

## 6. Multi-Platform Distribution Suite (X / LinkedIn / Hacker News)

### 1. X (Twitter) Thread

![X/Twitter Banner (16:9 Aspect Ratio)](/assets/images/gateway-01-x-cover.png)

**Tweet 1 (Hook)**:
Tired of juggling ChatGPT Plus, Claude Team, and commercial API keys across different CLIs and IDEs?

I built a self-hosted, all-in-one AI Aggregator Gateway in my Home-Lab.

Here is Part 1 of the blueprint: Why APISIX Standalone beat Kong for personal GitOps AI infrastructure 🧵👇

**Tweet 2 (The Multi-Account Problem)**:
If you run Codex CLI, Claude Code, and Gemini CLI simultaneously:
• Divergent auth headers (`Authorization` vs `x-api-key`)
• Fragmented rate limits across personal subscriptions
• A single upstream 429 crashes your coding workflows

The solution: a single internal HTTPS domain with a unified gateway token.

**Tweet 3 (Why APISIX Standalone?)**:
Why APISIX Standalone over Kong?
1. Zero DB / etcd overhead: Reads local YAML for pure GitOps reconciliation.
2. Fully open-source `ai-proxy-multi`: No enterprise licensing paywalls.
3. Minimal operational footprint: Fewer dependencies = higher reliability in Home-Lab.

**Tweet 4 (Engineering Trade-offs)**:
Every architecture choice has consequences:
• Requires strict OpenResty runtime & Lua library pinning (APISIX 3.16.0).
• Replaces dynamic REST APIs with declarative YAML commits and reloads.
• Kong was completely disabled to prevent port collisions.

Next up: Dual-layer Caddy + APISIX traffic routing and single-token decoupling!
Repost if this helps your developer workflow 🚀 #AIGateway #APISIX #HomeLab #DevOps

---

### 2. LinkedIn Engineering Post

**Hook**: How many AI API keys and subscription accounts are scattered across your terminal and IDEs right now?

As autonomous coding agents become daily drivers (Codex CLI, Claude Code, Gemini CLI, Antigravity), managing heterogeneous endpoints creates immense friction.

In this deep dive, I share the architecture behind my self-hosted **All-in-One AI Aggregator Gateway**:
• **The Goal**: A single HTTPS domain, a single token, aggregating personal subscriptions alongside commercial API keys with transparent load balancing.
• **The Technology Decision**: Why we selected **Apache APISIX Standalone** instead of Kong.

Key Takeaways:
1. **Declarative GitOps**: By leveraging APISIX Standalone mode, the gateway loads local YAML files directly, eliminating both PostgreSQL and etcd dependencies.
2. **AI Proxy Ecosystem**: APISIX provides the open-source `ai-proxy-multi` plugin without enterprise licensing constraints.
3. **Decoupled Architecture**: Caddy for TLS termination, APISIX for security and routing, New API for channel dispatch, and LiteLLM as a parallel upstream for commercial APIs.

Read the full technical breakdown below!

#SoftwareEngineering #AIGateway #SystemArchitecture #APISIX #DevOps #HomeLab

---

### 3. Hacker News / Reddit (r/selfhosted) Summary

**Title**: Show HN: Building a Personal AI Aggregator Gateway with Caddy, APISIX Standalone, and Multi-Account Isolation

**Text**:
Like many developers, I found myself constantly swapping tokens, endpoints, and environment variables across multiple LLM providers (ChatGPT Plus accounts, Claude Team, official OpenAI/Anthropic/xAI keys).

To solve this, I designed a layered gateway stack running on Home-Lab hardware:
- **Caddy**: Edge TLS termination and reverse proxying.
- **APISIX Standalone**: Zero-database YAML-driven gateway handling tenant ACL, token validation, and rate limiting.
- **New API & CPA Matrix**: Single-account OAuth adapters running in isolated Unix user namespaces with 0700 permissions.
- **Vault**: Secrets dynamically injected into tmpfs RAM at runtime.

This first post compares the operational trade-offs of Kong vs APISIX Standalone in a GitOps setup. Feedback and architecture critiques welcome!
