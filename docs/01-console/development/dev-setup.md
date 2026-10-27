# Development Setup

Local development setup and the commands you will use day to day.

## Prerequisites

- **Node 20** — `.nvmrc` pins it; `engines` allows `>=18.17 <25`
- **Yarn 4.12.0 via Corepack** — run `corepack enable` once

This repo has no `package-lock.json`. Do not run `npm install`; it will not
produce the dependency tree `yarn.lock` describes.

## Install

```bash
corepack enable
yarn install
```

## Run

```bash
yarn dev
```

Serves on port 3000 with Turbopack. `.claude/launch.json` carries the same
command for editor-driven previews.

> If the dev server fails on startup with a stale `.next/dev/lock`, remove
> `.next` and start again.

## Everyday commands

| Command | What it does |
|---|---|
| `yarn dev` | Dev server on :3000 |
| `yarn build` | `scripts/prebuild.sh` (content sync + generate) then `next build` |
| `yarn start` | Serve a production build |
| `yarn lint` | ESLint + boundary-link guard + **type-scale guard** |
| `yarn typecheck` | `tsc --noEmit` |
| `yarn test` | Vitest unit tests |
| `yarn test:e2e` | Playwright end-to-end tests |
| `yarn format` | Prettier |
| `yarn content:pull` | Pull marketing copy from the CMS repository |

`yarn build` runs `scripts/prebuild.sh`, which syncs content from the
`knowledge` repository and regenerates `src/data/content/`. A build with no
network access will skip the remote content and log 401s for the docs and blog
services — that is expected locally and not a build failure.

## Conventions that are enforced

`yarn lint` fails the build on these, so check them before pushing:

- **Type scale** — every font size comes from the ladder in
  `src/app/globals.css`. No `text-[13px]`, no `font-size: 0.86rem`, no inline
  `fontSize: 14`. The full rule set is in `skills/ui-typography/SKILL.md`;
  run it alone with `yarn check:type-scale`.
- **Boundary links** — `yarn check:boundary-links` validates cross-boundary
  navigation. See `skills/portal-frontend-content-boundary/SKILL.md`.

## Editing copy

Marketing and docs copy is **not** in this repository — it comes from the
`ai-workspace-services/knowledge` CMS repo and is generated into
`src/data/content/`. Editing `src/content/` or `src/data/content/` directly is
discarded on the next sync or build. See `docs/usage/config.md`.

## Related

- `docs/usage/config.md` — every config file and what it is for
- `docs/development/testing.md` — test layout and strategy
- `docs/development/contributing.md` — contribution workflow
