# Configuration

Reference for the configuration files that actually exist in this repository.

## Module system

Every config file in this repo is an ES module. `next.config.mjs` and
`postcss.config.mjs` use the `.mjs` extension; `tailwind.config.js` is `.js`
but uses `import` / `export default` and is loaded as ESM by Tailwind's own
loader. `package.json` deliberately carries **no** `"type": "module"` field —
adding one would change how every plain `.js` file in the repo is parsed.

> An earlier revision of this page tracked an in-flight CommonJS → ESM
> migration and instructed readers to `mv tailwind.config.mjs tailwind.config.js`.
> That migration is finished and no `.mjs` variants of the Tailwind or PostCSS
> config remain, so those steps would now break the build. They have been removed.

## Toolchain

| | Value | Source |
|---|---|---|
| Node | 20 (engines allow `>=18.17 <25`) | `.nvmrc`, `package.json` |
| Package manager | Yarn 4.12.0 via Corepack | `packageManager` in `package.json` |
| Lockfile | `yarn.lock` | — |

There is no `package-lock.json`; do not run `npm install`. Enable Corepack once
(`corepack enable`), then use `yarn`.

## Build and framework config

| File | Purpose |
|---|---|
| `next.config.mjs` | Next.js config: headers, redirects, Turbopack root |
| `tailwind.config.js` | Design tokens surfaced as Tailwind theme — **font sizes come from the type ladder**, see `skills/ui-typography/SKILL.md` |
| `postcss.config.mjs` | PostCSS pipeline for Tailwind |
| `tsconfig.json` | TypeScript compiler options and path aliases (`@/`, `@lib/`, `@server/`, …) |
| `contentlayer.config.ts` | Contentlayer document types |
| `middleware.ts` | Request middleware |
| `.eslintrc.json` | ESLint rules |

## Deployment config

| File | Purpose |
|---|---|
| `open-next.config.ts` | OpenNext adapter settings for Cloudflare Workers |
| `wrangler.worker.jsonc` | Worker names per environment (`frontend-server-edge-sit` / `-uat` / `-prod`) |
| `config/cloudflare-boundaries.json` | Console host and zone per environment |
| `config/feature_flags.yaml` | Feature flags |
| `config/gitleaks.toml` | Secret-scanning rules |

## Environment files

| File | Used for |
|---|---|
| `.env.example` | Documented template — start here |
| `.env.development` | Local development defaults |
| `.env.production` | Production build defaults |

Runtime service endpoints are not baked into these files for SIT / UAT / PROD;
they are resolved at runtime from `runtime-service-config.<env>.yaml` or from
explicit container environment variables. See `.env.production` for the contract.

## Content configuration

Marketing and documentation copy does **not** live in this repository. It is
pulled from the Git-backed CMS and then generated into typed modules:

```
ai-workspace-services/knowledge → content/website/**.md
  ↓  scripts/sync-content.sh pull
src/content/**.md                        (untracked; overwritten by every sync)
  ↓  scripts/generate-content.ts
src/data/content/*.ts / *.json           (generated; overwritten by every build)
```

Edit copy in the `knowledge` repository. Edits to `src/content/` or
`src/data/content/` are discarded on the next sync or build.

## Related

- `docs/development/dev-setup.md` — local setup and everyday commands
- `docs/zh/deployment/frontend-split.md` — delivery topology and UAT deployment
- `skills/ui-typography/SKILL.md` — type scale, enforced by `yarn lint`
