# OIDC Authentication Configuration Guide

This guide defines the UAT-to-PROD OAuth release contract for the console and
Accounts services. Each environment has its own OAuth application, callback
URLs, GitOps declaration, and Vault secret path.

## Architecture Overview

```
┌──────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  Browser     │      │  console host    │      │ accounts host     │
│  (User)      │      │   (Frontend)     │      │   (Backend)      │
└──────┬───────┘      └────────┬─────────┘      └────────┬─────────┘
       │  1. Click "Login      │                         │
       │     with GitHub"      │                         │
       │──────────────────────>│                         │
       │                       │                         │
       │  2. Redirect to       │                         │
       │     accounts /api/    │                         │
       │     auth/oauth/login/ │                         │
       │     github            │                         │
       │<──────────────────────│                         │
       │                       │                         │
       │  3. accounts redirects to GitHub/Google         │
       │     with client_id & callback URL               │
       │<────────────────────────────────────────────────│
       │                       │                         │
       │  4. User authorizes   │                         │
       │     on GitHub/Google  │                         │
       │                       │                         │
       │  5. GitHub/Google redirects back to             │
       │     accounts /api/auth/oauth/callback/github    │
       │─────────────────────────────────────────────────>
       │                       │                         │
       │  6. accounts exchanges code for token,          │
       │     creates/links user, redirects to console    │
       │<────────────────────────────────────────────────│
       │                       │                         │
```

## Prerequisites

- A GitHub account with access to **Settings > Developer Settings**
- A Google account with access to [Google Cloud Console](https://console.cloud.google.com/)
- The selected environment's console and Accounts hosts are reachable
- The matching GitHub/Google OAuth applications have been created
- Sensitive values are available through Vault at the selected environment path

---

## 1. GitHub OAuth Apps

Create two separate OAuth Apps. Do not reuse the PROD client ID or secret in
UAT.

1. Go to [GitHub Developer Settings > OAuth Apps](https://github.com/settings/developers)
2. Click **"OAuth Apps"** tab, then **"New OAuth App"**
3. Fill in the form:

| Field | Value |
|---|---|
| Environment | Application name | Homepage URL | Authorization callback URL |
|---|---|---|---|
| UAT | `onwalk.net Console (UAT)` | `https://console-cloudflare-uat.onwalk.net` | `https://accounts-cloudflare-uat.onwalk.net/api/auth/oauth/callback/github` |
| PROD | `svc.plus Console (PROD)` | `https://console.svc.plus` | `https://accounts.svc.plus/api/auth/oauth/callback/github` |

For both applications:

- **Allow wildcard matching**: off
- **Enable Device Flow**: off
- **Expire user access tokens**: on

4. Click **"Register application"**

### 1.2 Generate Client Secret

1. On the app detail page, copy the **Client ID** (displayed at the top)
2. Click **"Generate a new client secret"**
3. **Immediately copy the Client Secret** — it will only be shown once

### 1.3 Record Credentials

```
GitHub Client ID:     <environment_client_id>
GitHub Client Secret: <environment_client_secret>
Callback URL:         <environment_github_callback_url>
```

> ⚠️ **Security**: Never commit Client Secret to version control. Store it as an environment variable or in a secret manager.

### 1.4 GitHub OAuth Scopes

The OAuth App requests these scopes by default:
- `user:email` — Read the user's email addresses (used for account binding)

No additional GitHub permissions are required.

---

## 2. Google OAuth Clients

Create one Web OAuth client for UAT and one for PROD. Use the same environment
separation as GitHub:

| Environment | Client name | Authorized JavaScript origin | Authorized redirect URI |
|---|---|---|---|
| UAT | `onwalk.net Console (UAT)` | `https://console-cloudflare-uat.onwalk.net` | `https://accounts-cloudflare-uat.onwalk.net/api/auth/oauth/callback/google` |
| PROD | `svc.plus Console (PROD)` | `https://console.svc.plus` | `https://accounts.svc.plus/api/auth/oauth/callback/google` |

### 2.1 Configure OAuth Consent Screen

> This step is required before creating credentials. If already configured, skip to 2.2.

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select or create a project
3. Navigate to **APIs & Services > OAuth consent screen**
4. Choose **External** user type (allows any Google user to sign in)
5. Fill in the required fields:

| Field | Value |
|---|---|
| **App name** | `<environment> Console` |
| **User support email** | your email address |
| **Developer contact email** | your email address |

6. Add scopes: `email`, `profile`, `openid`
7. Click **Save and Continue** through the remaining steps
8. Under **Publishing status**, click **"Publish App"** to move out of testing mode
   - In testing mode, only manually added test users can sign in

### 2.2 Create OAuth Client ID

1. Go to **APIs & Services > Credentials**
2. Click **"Create Credentials" > "OAuth client ID"**
3. Fill in the form:

| Field | Value |
|---|---|
| **Application type** | `Web application` |
| **Name** | `<environment> Console` |
| **Authorized JavaScript origins** | `<environment_console_url>` |
| **Authorized redirect URIs** | `<environment_google_callback_url>` |

4. Click **"Create"**
5. Copy the **Client ID** and **Client Secret** from the popup

### 2.3 Record Credentials

```
Google Client ID:     <environment_client_id>
Google Client Secret: <environment_client_secret>
Callback URL:         <environment_google_callback_url>
```

---

## 3. Backend Configuration (environment-scoped)

Select the environment-specific GitOps declaration first. GitOps stores only
non-sensitive OAuth configuration; Vault stores provider secrets at the matching
environment path.

| Environment | Console | Accounts | GitHub callback |
|---|---|---|---|
| UAT | `https://console-cloudflare-uat.onwalk.net` | `https://accounts-cloudflare-uat.onwalk.net` | `https://accounts-cloudflare-uat.onwalk.net/api/auth/oauth/callback/github` |
| PROD | `https://console.svc.plus` | `https://accounts.svc.plus` | `https://accounts.svc.plus/api/auth/oauth/callback/github` |
| PROD Serverless | `https://console.svc.plus` | `https://accounts.svc.plus` | `https://accounts.svc.plus/api/auth/oauth/callback/github` |

The runtime deployment injects the following variables after resolving the
matching GitOps and Vault entries:

```bash
# ── GitHub OAuth ──
GITHUB_CLIENT_ID=<your_github_client_id>
GITHUB_CLIENT_SECRET=<your_github_client_secret>

# ── Google OAuth ──
GOOGLE_CLIENT_ID=<your_google_client_id>
GOOGLE_CLIENT_SECRET=<your_google_client_secret>

# ── Environment-specific non-sensitive values from GitOps ──
OAUTH_FRONTEND_URL=<environment_console_url>
OAUTH_GITHUB_REDIRECT_URL=<environment_github_callback>
OAUTH_GOOGLE_REDIRECT_URL=<environment_google_callback>
```

These variables are referenced in `config/account.yaml`:

```yaml
auth:
  oauth:
    frontendUrl: "${OAUTH_FRONTEND_URL}"
    github:
      clientId: "${GITHUB_CLIENT_ID}"
      clientSecret: "${GITHUB_CLIENT_SECRET}"
      redirectUrl: "${OAUTH_GITHUB_REDIRECT_URL}"
    google:
      clientId: "${GOOGLE_CLIENT_ID}"
      clientSecret: "${GOOGLE_CLIENT_SECRET}"
      redirectUrl: "${OAUTH_GOOGLE_REDIRECT_URL}"
```

`GITHUB_CLIENT_SECRET` and `GOOGLE_CLIENT_SECRET` are read from Vault only;
they must not be committed to GitOps or stored in GitHub Variables.

---

## 4. Frontend Configuration (environment-aware)

The frontend resolves the accounts service URL **server-side** via `getAccountServiceBaseUrl()`, which reads:

```bash
# Set by the environment deployment; do not hardcode the PROD URL in UAT.
ACCOUNT_SERVICE_URL=<environment_accounts_url>
```

If not set, the function falls back to a runtime default. **No `NEXT_PUBLIC_*` env var is needed** — the OAuth login URLs are constructed server-side and passed to the client components as props.

### OAuth Login URLs (auto-generated)

| Provider | Login URL |
|---|---|
| GitHub | `{accountServiceBaseUrl}/api/auth/oauth/login/github` |
| Google | `{accountServiceBaseUrl}/api/auth/oauth/login/google` |

### OAuth Callback URLs (handled by accounts.svc.plus)

| Provider | Callback URL |
|---|---|
| UAT GitHub | `https://accounts-cloudflare-uat.onwalk.net/api/auth/oauth/callback/github` |
| UAT Google | `https://accounts-cloudflare-uat.onwalk.net/api/auth/oauth/callback/google` |
| PROD GitHub | `https://accounts.svc.plus/api/auth/oauth/callback/github` |
| PROD Google | `https://accounts.svc.plus/api/auth/oauth/callback/google` |

---

## 5. Troubleshooting

### `undefined/api/auth/oauth/login/github`

**Cause**: OAuth URLs were using a client-side env var (`NEXT_PUBLIC_ACCOUNTS_SVC_URL`) that was not set.

**Fix** (applied in commit `4ce4147`): OAuth URLs now use the server-resolved `accountServiceBaseUrl` prop.

### OAuth login redirects to wrong domain

Check that `OAUTH_FRONTEND_URL` matches the console URL for the selected environment.
UAT must use `https://console-cloudflare-uat.onwalk.net`; PROD must use the
current Console origin (`https://console.svc.plus` or
`https://console-serverless-prod.svc.plus`).

### Google "Access blocked: This app's request is invalid"

Ensure the **Authorized redirect URI** in Google Cloud Console exactly matches the
selected environment, for example:
```
https://accounts-cloudflare-uat.onwalk.net/api/auth/oauth/callback/google
```
Trailing slashes or mismatched protocols will cause this error.

### GitHub "The redirect_uri MUST match the registered callback URL"

Ensure the **Authorization callback URL** in GitHub Developer Settings exactly matches
the selected environment, for example:
```
https://accounts-cloudflare-uat.onwalk.net/api/auth/oauth/callback/github
```

### Google OAuth in "Testing" mode — only test users can sign in

Go to **OAuth consent screen > Publishing status** and click **"Publish App"** to allow any Google user to sign in.

---

## 6. Quick Reference

| Item | Value |
|---|---|
| GitHub OAuth App Settings | https://github.com/settings/developers |
| Google Cloud Credentials | https://console.cloud.google.com/apis/credentials |
| UAT GitHub Callback URL | `https://accounts-cloudflare-uat.onwalk.net/api/auth/oauth/callback/github` |
| PROD GitHub Callback URL | `https://accounts.svc.plus/api/auth/oauth/callback/github` |
| PROD Serverless Console | `https://console.svc.plus/login` |
| UAT Google Callback URL | `https://accounts-cloudflare-uat.onwalk.net/api/auth/oauth/callback/google` |
| PROD Google Callback URL | `https://accounts.svc.plus/api/auth/oauth/callback/google` |
| Backend Config File | `accounts.svc.plus/config/account.yaml` |
| Frontend URL Resolution | `getAccountServiceBaseUrl()` in `src/server/serviceConfig.ts` |
