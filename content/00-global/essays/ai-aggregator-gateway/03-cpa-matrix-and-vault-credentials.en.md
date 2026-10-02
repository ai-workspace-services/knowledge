---
title: "No More Multi-Account Switching: Building Your Personal All-in-One AI Aggregator Gateway (Part 3) — Credentials: CPA Account Matrix & Vault Injection"
description: A practical deep dive into CLIProxyAPI single-account physical isolation matrices, strict 0700 OAuth credential security boundaries, interactive CLI login workflows with SSH tunnels, and dynamic tmpfs injection from HashiCorp Vault.
slug: ai-aggregator-gateway-03-credentials
lang: en
date: 2026-10-01T00:00:00Z
author: shenlan
tags:
  - ai-gateway
  - oauth
  - vault
  - security
  - cpa
category: essays
---

# No More Multi-Account Switching: Building Your Personal All-in-One AI Aggregator Gateway (Part 3)

> **Editor's Note**: When integrating personal subscription accounts across multiple AI providers, the most formidable obstacle is rarely network connectivity—it is risk management and credential isolation. Running multiple accounts within shared processes or unsegmented user environments invites catastrophic cascading failures. As the third installment in the "All-in-One AI Aggregator Gateway" series, this article explores single-account physical isolation matrices, interactive OAuth procedures, and secure tmpfs injection powered by HashiCorp Vault.

![Engineering Decision Canvas: CPA Matrix & Dynamic Vault Injection](/assets/images/gateway-canvas-03-credentials.png)

---

## 1. Account Matrix Design Philosophy: Physical Isolation Against Cascading Risk

Adapting personal subscription tiers (e.g., ChatGPT Plus/Pro, Claude Team, Google One) into API services requires navigating strict upstream **session fingerprinting, concurrency controls, and behavioral fraud defenses**.

Monolithic architectures that pool multiple accounts within a single runtime daemon face severe operational vulnerabilities: if one account encounters a challenge captcha, geographic suspension, or abrupt rate limiting, the entire shared process risks locking up or triggering correlated upstream bans. To prevent this, we adhere strictly to the **"Single Instance, Single Account, Dedicated Unix User, Dedicated Persistence Directory"** model:

| Instance Identifier | Provider Platform | CPA Interactive Login Command | Bound Account Identifier | Local Listening Port |
| :--- | :--- | :--- | :--- | :--- |
| `cpa-codex-01` | OpenAI / Codex | `--codex-device-login` | `manbuzhe2009@qq.com` | Dedicated Local Port A |
| `cpa-codex-02` | OpenAI / Codex | `--codex-device-login` | `manbuzhe2008@gmail.com` | Dedicated Local Port B |
| `cpa-claude-01` | Anthropic / Claude | `--claude-login` | `haitaopanhq@gmail.com` | Dedicated Local Port C |
| `cpa-antigravity-01` | Google / Antigravity | `--antigravity-login` | `haitaopanhq@gmail.com` | Dedicated Local Port D |
| `cpa-grok-01` | xAI / Grok | `--xai-login` | Planned for deployment | Dedicated Local Port E |

Each CPA daemon encapsulates a single account identity, operating on an exclusive local port with independent configuration and process isolation. If an individual account requires credential re-authentication, adjacent instances continue serving production requests unaffected.

---

## 2. Four Inviolable Rules of OAuth Credential Storage and Execution

OAuth artifacts generated upon successful authentication (such as refresh tokens and session bundles) represent persistent administrative keys to individual accounts. They must be protected by strict operational controls:

1. **Unprivileged Operating System User Isolation**: Never execute CPA background daemons as `root`. Each instance must be assigned an isolated, non-login system user (e.g., `cpa-codex-01`).
2. **Strict Local Filesystem Permissions (`0700`)**: OAuth tokens must reside exclusively within dedicated local directories: `/var/lib/ai-aggregator/cpa/<instance-id>/auth/`. Both the directory and its contents must be owned by the instance's specific system user, with permissions locked to `0700`.
3. **The "Never Upload" Red Line**: OAuth bundles **must never be committed to Git repositories, never stored in Vault, never persisted in plain database tables, and never bundled into CI build artifacts or application logs**.
4. **Navigating the Root Execution Directory Trap**: When switching user context via `runuser -u <user>` to execute interactive login CLIs, executing the command while remaining inside `/root` causes the CLI to fail immediately with `stat .: permission denied`. **Operators must change directories (`cd /tmp`) prior to switching user contexts.**

---

## 3. Interactive OAuth Login Workflows for Four Platforms (TLDR)

On headless cloud instances or headless Home-Lab servers, authenticating browser-based OAuth flows is accomplished by pairing CLI commands with local SSH port forwarding:

```bash
# Log in to target deployment node
ssh -t root@10.79.0.7
cd /tmp

# 1. Authenticate OpenAI First Instance (Device code flow: fetch code in terminal, approve in local browser)
runuser -u cpa-codex-01 -- /opt/ai-aggregator/cliproxyapi \
  --config /run/ai-aggregator/cpa-codex-01.yaml --codex-device-login --no-browser

# 2. Authenticate OpenAI Second Instance (Ensure browser is logged into manbuzhe2008@gmail.com)
runuser -u cpa-codex-02 -- /opt/ai-aggregator/cliproxyapi \
  --config /run/ai-aggregator/cpa-codex-02.yaml --codex-device-login --no-browser

# 3. Authenticate Claude Instance (Local callback flow)
runuser -u cpa-claude-01 -- /opt/ai-aggregator/cliproxyapi \
  --config /run/ai-aggregator/cpa-claude-01.yaml --claude-login --no-browser

# 4. Authenticate Google Antigravity Instance
runuser -u cpa-antigravity-01 -- /opt/ai-aggregator/cliproxyapi \
  --config /run/ai-aggregator/cpa-antigravity-01.yaml --antigravity-login --no-browser
```

### Essential Technique: SSH Reverse Callback Tunnels
When executing commands like `--claude-login`, the CLI outputs an authorization URL and binds a temporary local port (e.g., `http://localhost:54321/callback`) waiting for browser redirects. Because the server and developer workstation are physically separated, the browser redirect cannot reach the server directly.

To resolve this, open a separate terminal on your local machine and establish an SSH tunnel:
```bash
# Forward the server's local callback port to your local workstation
ssh -N -L 54321:127.0.0.1:54321 root@10.79.0.7
```
Next, navigate to the authorization link in your local desktop browser and approve access. The browser redirects to `localhost:54321`, traversing the SSH tunnel directly to the server's listening process and saving the credential bundle in seconds.

### Clarification: Google Antigravity vs Gemini CLI
Within the Google platform ecosystem, Antigravity and the Gemini CLI represent distinct integration surfaces. The instance `cpa-antigravity-01` runs an Antigravity-specific adapter, storing session tokens strictly within its private auth directory. Never copy workstation files like `~/.gemini/config/config.json` into CPA directories.

---

## 4. Vault KV Hierarchy and Dynamic tmpfs Memory Injection

While personal OAuth bundles remain confined to disk-backed `0700` directories, database DSNs, gateway tokens, and official pay-as-you-go commercial API keys are managed centrally via HashiCorp Vault.

### 1. Standardized Vault KV v2 Namespace Layout
Secrets adhere to a predictable environment hierarchy (e.g., UAT):

```text
kv/data/uat/ai-aggregator/database/new-api       # New API database connection string (DSN)
kv/data/uat/ai-aggregator/database/litellm       # LiteLLM database connection string (DSN)
kv/data/uat/ai-aggregator/gateway/caddy          # Caddy TLS certificate metadata & references
kv/data/uat/ai-aggregator/gateway/apisix         # bootstrap_client_key gateway client credential
kv/data/uat/ai-aggregator/litellm/providers/*    # Official commercial provider keys (OpenAI/Anthropic/xAI)
```

### 2. Runtime tmpfs Memory Injection
During deployment orchestration, Ansible pulls secrets dynamically from Vault and renders configuration templates directly into a tmpfs filesystem mounted at `/run/ai-aggregator/`:
* All runtime configuration files containing sensitive credentials exist exclusively in volatile system RAM with restricted ownership and permissions (`0600`).
* The client key consumed by APISIX (`/run/ai-aggregator/apisix/client-key`) is read directly from tmpfs.
* Upon node reboot or power loss, decrypted secrets residing in memory vanish completely, preventing credential exposure from decommissioned or stolen physical storage media.

---

## 5. Summary

Robust operational security stems from disciplined boundaries. By coupling an unprivileged single-account process matrix with `0700` filesystem isolation, SSH tunnel callbacks, and memory-only Vault secret injection, we establish an enterprise-grade security posture for personal multi-account infrastructure.

In the next installment, we transition from infrastructure configuration to practical developer usage:
**"No More Multi-Account Switching: Building Your Personal All-in-One AI Aggregator Gateway (Part 4) — Integration: Zero-Friction Client Access & GitOps Delivery"**.

---

## 6. Multi-Platform Distribution Suite (X / LinkedIn / Security Newsletter)

### 1. X (Twitter) Thread

**Tweet 1 (Hook)**:
Running multiple personal LLM subscriptions on a single server?
One upstream anti-fraud flag or challenge captcha will cascade and ban ALL your accounts.

Here is Part 3 of the AI Aggregator Gateway: CPA physical isolation & Vault tmpfs injection 🧵👇

**Tweet 2 (The Multi-Account Vulnerability)**:
Never pool multiple OAuth sessions into a single process!
Our defense: The physical isolation matrix.
• Dedicated Linux user per account (e.g., `cpa-codex-01`, `cpa-claude-01`)
• Dedicated local loopback ports
• Local storage permissions locked strictly to `0700`
• Zero blast radius: One account failure has 0 impact on adjacent instances.

**Tweet 3 (Headless OAuth via SSH Reverse Tunnels)**:
How do you authorize OAuth without a desktop GUI on remote headless nodes?
Use SSH port forwarding:
`ssh -N -L 54321:127.0.0.1:54321 root@server`
Authorize via your local Mac browser; the redirect hits localhost, travels the encrypted tunnel, and saves credentials on the server in seconds.

**Tweet 4 (Secrets Live Only in RAM)**:
No sensitive plaintext ever hits physical disk.
Ansible fetches secrets from HashiCorp Vault KV v2 and renders them into `/run/ai-aggregator/` (tmpfs).
Power down the machine, and all decrypted tokens vanish instantly.

Next up: Client SDK integration and automated GitOps pipelines!
Retweet & Follow to follow the build 🚀 #CyberSecurity #AIGateway #Vault #Linux #HomeLab

---

### 2. LinkedIn Security & Infrastructure Note

**Hook**: How do you safely aggregate personal AI subscription accounts (ChatGPT Plus, Claude Team) into production APIs without triggering upstream bans?

When building personal and small-team AI gateways, security is not just about perimeter defense—it is about **fault containment and credential isolation**.

Key Architectural Practices from Part 3:
1. **The Single-Account Physical Isolation Matrix**: Rather than running a monolithic adapter, every subscription runs as an independent Linux system user with isolated ports, directories, and systemd units.
2. **The 0700 Storage Red Line**: OAuth tokens remain strictly on local disk with 0700 permissions—never committed to Git, never in databases, and never exposed in CI logs.
3. **Volatile Memory Injection (tmpfs)**: Commercial API keys and database connection strings are pulled dynamically from HashiCorp Vault into RAM-based `/run/ai-aggregator/` files, leaving zero persistent plaintext traces.

Check out the full article for practical commands and SSH tunnel recipes!

#CyberSecurity #DevSecOps #AIGateway #HashiCorpVault #LinuxSecurity #Infrastructure

---

### 3. Security Digest / Newsletter Summary

**Subject**: Security Posture: Preventing Blast Radius Cascades in Multi-Account AI Gateways

**Summary**:
Adapting consumer subscription accounts into high-availability developer APIs exposes teams to aggressive upstream bot and fraud detection. This issue breaks down:
- Why single-process account pooling is an anti-pattern.
- Practical implementation of unprivileged Unix user boundaries and 0700 directory permissions.
- Leveraging SSH reverse tunnels to complete browser-based OAuth callbacks on headless nodes.
- Memory-only secret delivery using HashiCorp Vault and Linux tmpfs mounts.
