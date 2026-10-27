# Account quota and plan API contract

This is a Portal presentation contract for Project #2 P0-Q1. The authoritative
catalog and assignment state live in Supabase/PostgreSQL through accounts;
Portal does not derive plan identity from a Stripe field or keep a local quota
catalog.

## Account summaries

Portal reads `currentPlan`, `defaultPlan`, and `planAssignmentStatus` from
`GET /api/account/usage/summary` (also returned by the billing summary).

- `currentPlan.assigned=true` means an account entitlement is active. Its
  `maxTrafficBytes` is the effective limit used for that assignment.
- `defaultPlan.assigned=false` is reference data from the local Free catalog.
  It exposes the Free 5 GiB monthly maximum without assigning that plan to a
  pre-existing account.
- `planAssignmentStatus=unassigned` must render as unassigned, never as a
  Free entitlement. Usage UI does not invent a quota from a package-name
  string or a frontend constant. Legacy profiles named `default` without a
  resolvable catalog plan are also unassigned; their stored quota remains
  unchanged.
- `currentPlan.unlimited=true` is rendered as unlimited; a zero byte field in
  that case is not shown as a zero-byte limit.

The public catalog `GET /api/billing/plans` keeps `includedQuotaBytes` and
adds the explicit alias `maxTrafficBytes`. Free is 5 GiB per natural month,
Plus is 20 GiB per natural month, and Unlimited Beta is an internal-only tier.
Stripe price identifiers remain adapter details and are used only when a
checkout needs a provider price.

The account page keeps its existing card layout. It changes only the displayed
plan metadata and distinguishes assigned quota from a default reference.
Administration of user groups, including batch edits, remains out of scope
for P0-Q1 (tracked as P2-2).
