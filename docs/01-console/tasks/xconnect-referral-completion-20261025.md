# XConnect referral completion — Portal

Parent requirement: Accounts `docs/tasks/xconnect-referral-completion-20261025.md` on `feature/referral-completion-20261025` (repository Issues disabled). Portal base: `79fd0bc133e59413027629ecf61f48db7d7edb06`.

## Final scope

Preserve existing UI structure, styling, editorial sentence structure and images. Activity registration returns to `/referrals`; login/registration/MFA links preserve a validated same-origin destination. Explicit referral query parameters survive website-to-Console navigation without relying on shared browser storage. Reject protocol-relative, backslash and control-character destinations. Clear attribution after successful registration or an explicit server `invalid_referral_code`, preserving the existing first-valid attribution rule until then. Accounts owns immutable registration binding and reward facts.

Add the anonymous `/api/referrals/campaign` BFF for Accounts' public campaign metadata. Validate and whitelist `revision`, `enabled`, `active`, nullable `startsAt`/`endsAt`, `cashbackBps` and `annualBonusDays`; never forward browser credentials or expose private metadata. Include this exact API in the public SSR bundle, leaving arbitrary referral APIs excluded. The separate frontend-router change routes this exact path to public SSR; parent agent reports its check suite passed 186 tests.

The shared Zustand campaign state refreshes every 30 seconds and on window focus. Existing hero, FAQ and terms dates derive from the API, with the exclusive end converted to the last included display minute. Nullable boundaries use the existing empty-value glyph `—`. Activity registration CTAs fail closed while loading, unavailable, disabled, before start or after end. Ordinary registration and invitation-center access remain available. No new UI design, dependencies or environment variables.

Tighten the existing overview validator for already-defined fields: plan type, integer paid amount, eligibility/completion dates and optional history flags. Additional campaign metadata remains compatible.

## Verification

- Targeted Vitest: **10 files / 39 tests passed**, covering safe authentication navigation, attribution lifecycle, overview and campaign contracts, public/private BFFs, invitation-center entry and dynamic activity CTA state.
- SSR BFF boundary tests: **8 passed**.
- `yarn lint`, explicit repository ESLint, `yarn typecheck` and `git diff --check`: **passed**. Typecheck was repeated after restoring unrelated build-generated tracked changes.
- Reviewed content input pinned to local Knowledge **`ede2f5408eb6489fe7025d1d1051e79803ff0dd0`**. No authoritative content was modified.
- Production build passed with the existing Next Webpack mode and reusable dependencies:

  ```sh
  WEBSITE_CONTENT_REPOSITORY=/Users/shenlan/workspaces/ai-workspace-service/knowledge \
  WEBSITE_CONTENT_REF=ede2f5408eb6489fe7025d1d1051e79803ff0dd0 \
  yarn build --webpack
  ```

  Output includes `/api/referrals/campaign`. Webpack supports the isolated checkout's reused node_modules symlink.
- Final code review checked website-to-Console query preservation, login/register switch links, registration fallback and MFA return links, success-path precedence, and safe redirect validation. No further authentication defect was established by this review.
- Unrelated build-generated tracked content and next-env.d.ts changes were restored. Ignored generated modules remain available for validation. The untracked node_modules symlink must not be committed.

No commit, push or deployment. Real website/Console browser E2E with email verification and MFA remains separate acceptance evidence. These Portal tests do not establish Stripe payment, production deployment or actual payout acceptance. Payout remains manually reviewed and recorded off-platform.
