# Feature SIT image build dispatch

This catalog describes `.github/workflows/ci-pipeline.yml` at the current Main revision. It builds and publishes an image; it does not deploy a lane or authorize DNS. Recheck the workflow and scripts before dispatch because the catalog may drift.

| Input | Type / default | Feature SIT requirement |
| --- | --- | --- |
| `deployment_environment` | required choice, default `uat` | `sit` |
| `feature_sit` | boolean, default `false` | `true` |
| `sit_hostname` | optional string, default empty | reviewed console hostname matching `<label>-sit.onwalk.net`; label including `-sit` at most 54 characters so service prefixes fit |
| `website_content_sha` | optional string, default empty | exact lowercase 40-character commit SHA from the configured content repository |

Use the protected `main` ref. Feature SIT rejects other refs/events or environment values before credential retrieval. The configured website repository must be a credential-free GitHub HTTPS URL; the build fetches the selected commit and fails if the resolved SHA differs. `sit_hostname` and `website_content_sha` are only used when `feature_sit` is true; without it they do not configure an isolated build. A dispatch from Main with `feature_sit=false` may publish `latest` and must not be treated as an isolated SIT candidate.

Before dispatch, verify the exact Portal Main SHA, content repository and commit, intended hostname, and Vault role/ref/workflow binding. Ensure no conflicting run is pending in the `console-pipeline-main` concurrency group. A successful dispatch only initiates the build; verify its workflow ref, event, run ID and attempt, and retrieve `console-build-provenance-<run>-<attempt>` from that exact run. Check the source SHA, content repository and SHA, `environment=sit`, candidate hostname, build mode and image digest against the reviewed candidate. A SHA tag is a locator, not an immutable artifact; deploy only the verified digest. Recheck Main and candidate freshness before use.

Feature SIT sets lane public URLs and disables known Bridge proxy routes. This does not prove all runtime configuration, external dependencies, network isolation, or business health. Those remain deployment and acceptance gates. Never use this build as a substitute for a completed SIT release receipt.
