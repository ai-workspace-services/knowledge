---
ui:
  title: Create release plan
  subtitle: Daily Main Snapshot
  environment: Select environment
  environmentHelp: SIT / UAT use Daily; PROD uses a protected release workflow.
  sitDescription: System integration testing
  uatDescription: User acceptance testing
  prodDescription: Production
  protectedRelease: Protected release
  prodHelp: PROD switches to a protected release plan; execution is not connected yet.
  source: Snapshot source
  sourceRef: Branch / reference
  tag: Snapshot tag
  autoTag: Leave empty to resolve an immutable tag
  repositories: Repository scope
  allRepositories: All repositories
  selectedRepositories: Selected repositories
  repositoryHelp: Filtered snapshots do not trigger full UAT deployment.
  dataMode: Data operation
  none: No data operation
  preview: Import preview
  import: Write import
  baseline: Adopt baseline
  schema: Schema migration
  previewNotice: Preview does not write to the database or continue deployment.
  writeNotice: Import writes to the target database; source, target and recovery evidence are required.
  importConfig: Non-secret import configuration JSON
  advanced: Advanced settings (XConnect / Shared)
  schemaExpected: Starting schema version
  schemaTarget: Target schema version
  schemaHash: SQL SHA-256
  oneTag: XConnect One release tag
  gatewayTag: XConnect Gateway release tag
  gitopsDefault: Leave empty to use GitOps configuration
  stripe: Request skipping Stripe sync
  stripeHelp: Current Hybrid execution always skips Stripe catalog sync.
  vaultEndpoint: Vault readiness endpoint
  observabilityEndpoint: Observability readiness endpoint
  iamEndpoint: IAM readiness endpoint
  iamIssuer: IAM issuer
  timeout: Readiness timeout (seconds)
  plan: Execution plan
  planHelp: Derived from current parameters; stages have not run.
  planned: Planned
  validate: Validate parameters
  snapshot: Immutable snapshot
  build: Cross-repository builds
  shared: Read-only Shared readiness
  deploy: UAT deployment and verification
  protected_release: Protected release workflow
  stopAtPreview: Stop after import preview
  createPlan: Create plan
  planning: Creating plan
  viewParameters: View parameters
  executionUnavailable: Execution backend is not connected; this page creates plans without dispatching workflows.
  prodUnavailable: Production release execution is not connected; Daily cannot dispatch PROD.
  planCreated: Plan created; not executed
  validationError: Invalid parameters. Correct them and try again.
  releases: View release history
  recent: Recent releases
  noReleases: No release records available
  releaseUnavailable: Release records unavailable
  loading: Loading
  evidencePending: Live acceptance requires corresponding evidence
  mcp: AI / MCP interface
  mcpHelp: People and AI use the same validation and planning API.
  mcpScope: Catalog, planning and release reads are available; dispatch tools are not exposed.
---

English content for the Portal Operations UI.
