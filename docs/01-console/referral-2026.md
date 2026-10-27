# XConnect Referral Program 2026

## Ownership and content provenance

Portal owns `/referral` marketing UI, `/referrals` authenticated account UI, referral attribution in application state and authenticated Accounts proxies. Accounts owns verification, unique invitation relationships, invoice rewards, settlement review and the subscription ledger. Portal never computes a real reward, accepts a user id for viewing another account, or updates an entitlement.

Canonical bilingual copy: `ai-workspace-services/knowledge/content/website/campaign/referral/{zh,en}.json`, reviewed source commit `4313937b74f0d0f15ec6133b82d19e4e2cca56c1`. `src/data/content/referral.json` is a generated artifact of that source, not an editorial source. Regenerate with the usual content sync and `scripts/generate-content.ts --campaign=referral`.

The center returns bounded recent histories with an explicit notice when older rows exist; Accounts computes summary values across the full ledger. Self-service history pagination remains a follow-up; earlier records can be requested through official support.

The campaign is new on the Knowledge PR branch. A build against an earlier Knowledge revision that does not declare this entrypoint retains and validates the checked-in generated campaign artifact. Once a source declares `referral` in its manifest, missing or invalid locale sources fail validation. Partial locale sources fail generation. This keeps existing CI usable while the content PR is pending; reviewed Knowledge should be merged before a Portal release and the release built against its immutable source revision.

## API contracts

- `GET /api/auth/referrals`: session-authorized proxy to Accounts self overview; never forwards client query/user identifiers. Currency-separated balances, masked invitation records and actual entitlement ledger records come only from Accounts. Failures display error/retry or expired-login recovery; no fake rewards.
- `POST /api/auth/referrals/settlements`: same-origin session-authorized proxy, only accepts an uppercase ISO currency. Accounts reserves its actual available balance for manual review. Caller-supplied amounts and user ids are ignored.
- Staff Accounts review completes an already performed offline payout through `POST /api/auth/admin/referrals/settlements/:settlementId/complete` with `payoutReference` and `reason`; reversing a reward uses `POST /api/auth/admin/referrals/rewards/:rewardId/reverse` with `reason`. This MVP keeps staff actions in the authenticated Accounts procedure; it does not initiate an external payout from a user request.
- Registration adds optional validated `referralCode` to the existing Accounts registration request. The first valid URL code (`ref` or `code`) persists in application Zustand state and browser session storage through navigation. Accounts independently validates eligibility and unique assignment.

The calculator rounds the 10% estimate per invoice in integer minor units and multiplies by successful invite count. Annual days require the inviter-active-subscription checkbox, and monthly subscriptions always estimate zero extra days. All calculator figures are labeled estimates and cannot become settlement or subscription records.

## Routing

`/referral` belongs to the public boundary and is indexed in the sitemap. `/referrals` belongs to the authenticated console boundary, uses the existing login redirect and is `noindex`. Edge routing must consume the updated console suffix `/referrals*` and route `/api/auth/referrals` plus `/api/auth/referrals/settlements` to the console worker; these two exact BFF handlers are explicitly bundled in console by the build allowlist. Otherwise the public fallback could route the invitation center to the wrong worker. The requested `svc.plus/referrals` host must be confirmed in existing domain routing before UAT acceptance; the existing runtime console host determines cross-boundary links.

## UAT acceptance

1. Inspect Chinese and English `/referral` at 390px and desktop widths. Check navigation, calculator, eligibility checkbox, FAQ disclosure, terms anchor and keyboard focus.
2. Follow a valid invitation link into registration. Verify the existing registration flow sends referralCode and Accounts assigns the relationship once; malformed/self-existing relationships must fail safely server-side.
3. Sign in to `/referrals`; verify real empty, real populated, service unavailable and expired-session states. Verify records are masked and another user's query parameters cannot change the account.
4. Verify first paid invoice, seven-day no-refund/no-dispute hold and currency-separated reward amounts against Accounts records. Repeated webhook delivery must not duplicate rewards.
5. Verify one annual referral extends the active inviter's actual ledger exactly 30 days and shows the prior and resulting expiry. Monthly or inactive inviters must not receive days.
6. Request settlement for one available currency. Verify it enters manual review, cannot overdraw on retry, and no front-end request directly triggers a payment.
7. Verify refund/dispute reversal and extension ledger corrections with Accounts. Confirm no full invitee email, payment credential or Stripe identifier is returned to the browser.

## Release and rollback

No production database changes are included in Portal. Release requires separately reviewed Accounts migration/rollback, Knowledge content and edge routing PRs. Apply Accounts changes first in UAT, build the Portal image with the reviewed Knowledge revision, deploy through existing GitOps and capture runtime evidence. Portal deployment rollback restores its prior immutable image and route configuration; the database rollback belongs to Accounts and must preserve financial and entitlement audit records. Production deployment and production database migration require separate release authorization.


## Accounts migration and operator boundaries

Accounts migration `sql/migrations/2026101301_referral_program.up.sql` adds:

- `referral_codes`, `referrals`: unique code and single-level attribution.
- `referral_rewards`, `referral_reward_events`: invoice reward and idempotent audit/reversal entries.
- `referral_payment_risks`: refund/dispute facts, including events arriving before the reward.
- `referral_settlements`, `referral_settlement_items`: currency-separated manual-review reservation and reconciliation.
- `subscription_extension_ledger`: actual subscription extension and reversal records.

Verified payment facts reuse existing `finance_invoices` and `finance_payments`. Nullable `service_period_start` and `service_period_end` invoice fields preserve verified service periods for payment-time eligibility across renewals; Accounts also updates its checked native schema and transfer contract. No database runtime, IaC or separate payment/account system is introduced.

Staff completion and manual reversal require existing `admin.billing.money.write`; an unprivileged operator must be rejected. Complete a settlement only after the actual offline payout is independently confirmed, recording a non-secret reconciliation reference and reason. Do not enter payment credentials in either field.

The down migration intentionally refuses any existing referral or ledger data. It is suitable for an empty, disposable migration qualification database. After awards exist, preserve financial history and release a reviewed forward fix. In particular, reverting Accounts to a binary without the ledger reader would remove granted extension access: retain ledger-based entitlement reads while stopping faulty new reward writes. Portal/router may revert together to prior immutable images; that does not authorize dropping financial records.

## Remaining UAT-only checks

- Validate both requested hosts and router/worker bindings with the reviewed immutable releases.
- Run Stripe test-mode signed events, out-of-order retries, refunds and disputes through the deployed stack; a direct Store fixture is not equivalent evidence.
- Confirm real session/cookie scope across public, registration and console hosts, copy-to-system-clipboard and native share behavior on supported devices.
- Validate migration against a non-production copy of the current schema, and reconcile retained paid rewards/extensions during the rollback rehearsal.
- Native App Store/Play purchase or external-link changes require their applicable storefront review; this web change introduces no native purchase flow.
