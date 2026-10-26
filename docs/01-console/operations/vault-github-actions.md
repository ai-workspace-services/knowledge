# Vault + GitHub Actions for `console.svc.plus`

This note records the Vault OIDC login pattern used by the `console.svc.plus` frontend pipeline.
It focuses on the minimal setup needed for GitHub Actions to read CI/CD secrets from Vault K/V.

## Goal

- Use GitHub Actions OIDC to authenticate to Vault.
- Read CI/CD secrets from `kv/data/CICD`.
- Keep deployment secrets out of GitHub Actions Secrets where possible.

## Required Vault prerequisites

- `jwt` auth mount enabled and configured for GitHub Actions OIDC.
- A policy that can read the `kv/data/CICD` path.
- A JWT role that binds to the `ai-workspace-services/portal` repository.

## Policy

Create a policy that allows read-only access to the shared CICD path:

```bash
export VAULT_ADDR=https://vault.svc.plus
vault login

vault policy write github-actions-console - <<'EOF'
path "kv/data/CICD" {
  capabilities = ["read"]
}
path "kv/metadata/CICD" {
  capabilities = ["read", "list"]
}
EOF
```

## JWT role

The role must bind to the `ai-workspace-services/portal` repository.

Pass a JSON body on stdin so Vault receives `bound_claims` as a map. This role
allows workflows from `main` and `release/*` only:

```bash
vault write auth/jwt/role/github-actions-console - <<'EOF'
{
  "role_type": "jwt",
  "user_claim": "repository",
  "bound_audiences": ["vault"],
  "bound_claims_type": "glob",
  "bound_claims": {
    "repository": "ai-workspace-services/portal",
    "sub": [
      "repo:ai-workspace-services/portal:ref:refs/heads/main",
      "repo:ai-workspace-services/portal:ref:refs/heads/release/*"
    ]
  },
  "token_policies": ["github-actions-console"],
  "token_ttl": "20m",
  "token_max_ttl": "30m"
}
EOF
```

## CI/CD secrets expected in `kv/data/CICD`

The frontend pipeline expects these keys to exist:

- `GHCR_TOKEN`
- `SINGLE_NODE_VPS_SSH_PRIVATE_KEY`
- `INTERNAL_SERVICE_TOKEN`
- `CLOUDFLARE_DNS_API_TOKEN`

## Workflow shape

The GitHub Actions workflow should:

1. Set `permissions.id-token: write`.
2. Use `hashicorp/vault-action@v4`.
3. Authenticate with `method: jwt`.
4. Use `role: github-actions-console`.
5. Read secrets from `kv/data/CICD`.
6. Export the values into the job environment or step outputs.

## SSH key handling

Use the raw OpenSSH private key:

```bash
SSH_KEY="${SINGLE_NODE_VPS_SSH_PRIVATE_KEY}"
```

Then write the key to `~/.ssh/id_rsa` and validate it with `ssh-keygen -y -f`.

## Common error

If Vault returns:

```text
error converting input for field "bound_claims": '' expected a map, got 'string'
```

that means `bound_claims` was passed as a string argument. Re-run the command using the JSON stdin body above. The `-` argument reads JSON from stdin; `@-` is not supported because Vault treats it as a local file named `-`.

## Service roles and workflow whitelist

The CI pipeline (`.github/workflows/ci-pipeline.yml`) authenticates to Vault with GitHub Actions OIDC, without static keys.
To keep least privilege and environment isolation, this repository's CI has its own Vault policy and roles:

1. **Credential scope (path isolation)**
   - CI has **read-only** access to `kv/data/CICD`.
   - That path holds only shared service credentials (for example `GHCR_USERNAME` and `GHCR_TOKEN`) used to push images after a build.
   - CI cannot read environment-specific cloud credentials, Terraform state, or host SSH deploy keys.

2. **Identity minting (tight binding)**
   - The service has three independent Vault roles, one per environment: `sit`, `uat`, `prod`.
   - **`job_workflow_ref` allow-list**: Vault checks the calling workflow file. Only the allow-listed workflow in this repository (`ci-pipeline.yml`) can exchange its token.
   - Adding or renaming a workflow file without authorization cannot be used to obtain credentials.

### Troubleshooting: 403 Forbidden

If the `Fetch Vault Secrets` step fails with `403`, check:

1. Whether the requested secret path is outside the `kv/data/CICD` scope.
2. Whether the workflow file name or the repository name has changed.

If the workflow must be renamed, an administrator has to update the allow-list in `docs/tasks/vault_service_repo_roles.sh` of the `platform-ops-toolkit` repository and re-run that script against the Vault server.
