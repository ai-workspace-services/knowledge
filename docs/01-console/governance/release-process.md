# Release Process

This page tracks release summaries for published versions of the public web console served under `www.svc.plus` and `console.svc.plus`.

## Verified Release — 2026-10-09

### v2026.10.09-r2 — Account Recovery

- Portal PR [#412](https://github.com/ai-workspace-services/portal/pull/412) is merged.
- The release removes the hard-coded Google Analytics measurement-ID fallback. When Analytics is not configured, the console no longer loads Google Analytics or Google Tag Manager resources.
- The immutable Portal release is [v2026.10.09-r2](https://github.com/ai-workspace-services/portal/releases/tag/v2026.10.09-r2).

### v2026.10.09-r3 — Release Metadata Alignment

- GitOps PR [#416](https://github.com/ai-workspace-infra/gitops/pull/416) pins `prod-console` to the console image digest `sha256:e56de11c99898f315da099caef22718a54e4bf6c25b982f51b78919da05444df`.
- GitOps PR [#417](https://github.com/ai-workspace-infra/gitops/pull/417) maps the runtime `FRONTEND_IMAGE` to the same immutable `CONSOLE_IMAGE`, so `/api/ping` reports the deployed image accurately.
- The immutable GitOps release is [v2026.10.09-r3](https://github.com/ai-workspace-infra/gitops/releases/tag/v2026.10.09-r3).
- `web-saas-prod` was reconciled manually through Doco-CD `prod-console`; `prod-services` remained pinned to `v2026.10.08-r4`.

### Validation

- `https://console.svc.plus/account-recovery` returned HTTP 200.
- The password-recovery send-code and valid-code reset flow were manually verified, including mailbox delivery.
- `/api/ping` reports the `e56de11c...` immutable image digest.
- PostgreSQL, Accounts, Billing, stunnel, Caddy, and the Doco-CD controller were unchanged.
- No database or schema change was included; the PostgreSQL full-backup gate was therefore not invoked.

## Historical Release

### v0.2

Release tag: `v0.2`  
Release branch: `release/v0.2`  
Published commit: `0fab89e`

#### Highlights

- Introduced the new XWorkmate workspace with a denser assistant layout, cleaner shell, and improved entry flow.
- Added the OpenClaw assistant workspace and pairing bridge, including configurable origin override and more stable pairing fallback behavior.
- Unified navigation and AI entry points with a persistent assistant sidebar and refined panel routing.
- Added the latest blog shortcuts on the homepage and improved guest and registration messaging.
- Expanded docs with bilingual structure updates, stronger OIDC guidance, and setup/readme cleanup.
- Fixed build stability issues, including `next-mdx-remote` vulnerability-related build failures and Yarn dependency metadata alignment.

#### New Features

- Launched the XWorkmate workspace and polished its workspace entry and layout.
- Added OpenClaw assistant integration, pairing bridge support, integration probe API, and integration defaults handling.
- Added XScopeHub MCP visibility on the services page.
- Displayed the latest 7 blog article titles in homepage shortcuts.

#### Improvements

- Split observability into a tri-view workspace and refined panel assistant routing.
- Unified navigation structure and persistent AI sidebar behavior.
- Improved login and registration flows by using server-resolved account service URLs.
- Guest and demo access must not expose any backing account identity in public UI or session payloads.
- Added vault-backed token lookup for integrations.

#### Docs And Setup

- Added bilingual docs coverage and restructured the docs entry points.
- Rewrote the OIDC authentication guide with fuller setup instructions.
- Updated setup guidance and simplified README structure.

#### Build And Dependency Fixes

- Updated and aligned `next-mdx-remote` usage for secure builds.
- Removed conflicting npm lockfile state and aligned Yarn dependency metadata for reproducible builds.

## Notes

- GitHub Release: `https://github.com/x-evor/console.svc.plus/releases/tag/v0.2`
- Related docs: `docs/README.md`, `docs/en/README.md`, `docs/zh/README.md`
- Release validation must verify both `www.svc.plus` and `console.svc.plus` against the same `releaseImageRef`, `releaseImageTag`, and `releaseCommit`.
- `www.svc.plus` is the canonical public domain for metadata, sitemap, `dashboardUrl`, and shared links.
