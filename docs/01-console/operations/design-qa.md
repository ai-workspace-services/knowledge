# Operations design QA — 2026-10-06

Source: selected knowledge `form-and-plan-prod-v2.png`. Implementation: `/panel/operations`, existing Portal shell/theme retained.

Evidence: `/private/tmp/operations-comparison-full-20261006.png` combines source (left) and implementation (right). `/private/tmp/operations-mobile-20261006.png` captures 390px layout. No signed-in user data appears in these captures.

## Review

- Desktop form/plan split, UAT selection, protected PROD badge, blue preview notice, advanced disclosure, repository choices and MCP entry match the chosen direction.
- Mobile environment choices and form stack without clipped controls. Preview shell hides the desktop sidebar, matching the real Panel responsive rule. The temporary preview route was removed before the production build.
- Intentional differences: existing XWorkmate shell, no fabricated generated tag or completed run, pending stages explicitly labeled pending. The explicit import JSON editor adds height; this is not a pixel-identical copy.
- PROD selection disables Daily inputs and plan creation, with the protected entry marked not connected.
- Real API remains authenticated. Unauthenticated preview shows a release-load error, not sample data. Existing real Releases catalog remains unchanged.
- Console UAT Worker production build passed after replacing the out-of-root local dependency symlink with cloned dependencies. Existing OpenNext queue/copy/tsconfig warnings remain.
- Remaining: actual workflow dispatch, durable operation records, child-run synchronization and protected PROD execution are not implemented. No authenticated UAT acceptance exists yet.

final result: blocked

Visual layout and first-stage interactions verified. Full execution design and signed-in UAT acceptance remain incomplete; this report does not attest to deployment or migration.
