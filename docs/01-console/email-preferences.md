# Email management and recipient preferences

`/panel/management` has a Root-only **邮件与通知 / Email & notifications** workspace with:

- **Announcement campaigns:** new feature, app release and announcement drafts; plain text plus optional HTTPS CTA; Free/subscriber/Team/all segments; frequency grouping; reviewed content/audience digest; explicit queue confirmation; cancellation and results.
- **Welcome journey:** editable Hello, get-started and discover-more templates, activation switches and per-step delays. Hello is an account-service guide; follow-ups require tutorial consent and respect recipient frequency and step order.
- **Delivery log:** bounded queue processing, SMTP acceptance, safe retries, suppressed/cancelled outcomes and explicit acknowledgment before retrying an uncertain SMTP result.
- **Bounces and complaints:** Root registers provider-confirmed suppression events. A suppressed address cannot bypass the list by opting back into marketing.
- **Sender and footer:** real legal identity and personalized preference/unsubscribe links. Preview links belong only to the current Root account and must not be forwarded.

All categories default off. User account settings link to `/email/preferences`; email capabilities permit preference changes or unsubscribe without login. Marketing adds `AD:` and the shared footer; necessary account/security/billing messages remain independent. UI success for `sent` is labeled **SMTP accepted**, not inbox delivery.

## Content and API ownership

Knowledge's `content/website/account/email-preferences/{zh,en}.json` is canonical for bilingual UI and default onboarding template copy. Portal's generated JSON is a build artifact. Operator-authored campaign/template payloads and queue state are dynamic Accounts data, not website content publication.

Refresh only this surface:

```sh
WEBSITE_CONTENT_DIR=/path/to/knowledge/content/website yarn exec tsx scripts/generate-content.ts --account=email-preferences
```

Older source revisions retain the reviewed generated artifact until the matching Knowledge content is merged. Merge Knowledge before releasing Portal. Selfhost uses the existing authenticated `/api/auth/admin/[...segments]` BFF and public preference BFF. Serverless announcement pages use the existing public-page fallback, while `/api/auth/*` reaches the Accounts auth gateway; no new gateway topology is introduced.

## Dispatch and rollout

Accounts owns SMTP dispatch and enables its bounded background worker only under the existing database background-writer policy. The Root log can process a bounded due batch manually when background dispatch is unavailable. This change does not provision serverless scheduler infrastructure. Every step is disabled by default; saving drafts does not send. No implementation test sends real email.

The two additive migrations and qualified PostgreSQL 17 native snapshot must pass the normal reviewed release gate. The three onboarding steps are enabled for new accounts by default; Root can disable or edit any step. Before enabling real mail, configure the actual sender identity and SMTP, redact `key` parameters from ingress logs, verify DKIM/unsubscribe signing, and test opt-in, preview/launch, unsubscribe-after-queue, retry, cancellation and welcome enrollment on UAT.

Local validation: lint, typecheck, UI confirmation/BFF tests and `yarn build --webpack` (the local worktree uses an external dependency symlink that Turbopack rejects). Browser QA uses a fictional Root and recipient and a fake SMTP sender; screenshots are fixtures. Accounts separately tests PostgreSQL concurrent queue claiming, deduplication, native init and business-data transfer. See Accounts' `docs/architecture/email-preferences.md` for retry and consent semantics.

Root can resolve an uncertain delivery as SMTP accepted only after provider verification; this records acceptance without sending again. A suppressed or cancelled onboarding predecessor stops later steps.
