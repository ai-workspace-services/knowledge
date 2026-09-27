# XConnect + Vault Migration, Deployment, Scaling, and Rollback Runbook

## 1. Purpose and scope

This runbook turns the `vault.svc.plus` migration into a repeatable operating procedure. It covers the XConnect data plane, GCP resource deployment, Vault Integrated Storage (Raft), migration from the legacy node, DNS cutover, one-to-three and three-to-one scaling, and rollback.

It is intended for:

- keeping the legacy Vault as an independent server while GCP becomes the service entry point;
- using WireGuard over VLESS between XConnect Gateway/One nodes for Raft and operations traffic;
- running Vault with local Integrated Storage (Raft) at either one or three nodes;
- using GitHub Actions for declaration resolution, IaC, Playbook orchestration, and read-only acceptance, while initialization, unseal, and the final traffic decision stay in a controlled operator session.

Tokens, unseal shares, private keys, invitation URIs, and age private keys must never be stored in Git, Actions logs, inventories, or this documentation.

## 2. Current final state

| Item | Current value |
| --- | --- |
| Service domain | `vault.svc.plus` |
| GCP project | `open-platform-prod` |
| GCP network | `vault-shared` |
| GCP node | `vault-prod-0`, `RUNNING` |
| GCP addresses | private `10.81.0.4`, public `35.221.167.104` |
| Vault | 1.21.4, Raft, initialized, unsealed, active leader |
| Raft size | one voter/leader |
| Legacy node | `46.250.251.132`, `vault-2`, independent Vault server, container paused for observation |
| DNS | `vault.svc.plus` returns only `35.221.167.104` |
| XConnect Gateway | `10.79.0.1` |

The legacy and GCP servers were both derived from the same Raft snapshot and therefore have the same `cluster_id`. They must never serve writes at the same time. Any rollback must first point DNS to one active entry point and stop the other write-capable server.

## 3. Architecture and boundaries

```text
                         Control plane
                 Accounts API / XConnect Zero
                  policy, devices, config delivery
                              |
                              v
      Legacy 46.250.251.132          GCP vault-prod-0
              |                         |
              | WireGuard over VLESS    | Gateway
              +-------- XConnect -------+ 10.79.0.1
                         data plane
                              |
                   Vault Raft TCP 8200/8201
                              |
                    vault.svc.plus / Caddy TLS
```

### 3.1 XConnect control plane and data plane

- The control plane creates networks, issues one-time invitations, distributes signed configuration, reconciles peers, and revokes devices.
- The data plane is the WireGuard peer and local Xray/Caddy transport on Gateway/One. Established data-plane connections may continue during a short control-plane outage.
- Public ingress carries only protected VLESS/TLS TCP 443. WireGuard UDP 51820 is not exposed directly to the Internet.
- Caddy terminates TLS and forwards `/xconnect` to the local Xray socket; Xray forwards into the Gateway WireGuard data plane.
- Vault Raft ports 8200/8201 are reachable only through the private network or XConnect overlay and are never public ingress.

### 3.2 Vault control boundary

- Playbooks install and configure Vault but never run `vault operator init` or `vault operator unseal`, and never read or write root tokens or unseal shares.
- GitHub Actions does not hold root tokens, unseal shares, operator tokens, or age private keys.
- DNS changes, Raft leadership transfer, legacy-peer removal, and rollback require explicit confirmation phrases and the protected `prod` Environment.

## 4. Preconditions

### 4.1 Required declarations

Prepare the following GitOps declarations and record the full commit SHA used for each run:

1. Provider-neutral Vault service declaration:
   - `storage.backend: raft`;
   - `storage.members: 1` or `3`;
   - `storage.leader` and `storage.peers` match the node list;
   - `storage.address_scope: private`;
   - `migration.raft_network: private` or `overlay`;
   - stable legacy ID, SSH host key, and overlay address.
2. Shared GCP resource declaration:
   - project `open-platform-prod`;
   - network `vault-shared`;
   - subnet `10.81.0.0/20`;
   - either `vault-prod-0`, or `vault-prod-0/1/2`;
   - OS Login, an SSH `/32` allowlist, and private Raft firewall rules.
3. XConnect topology:
   - Gateway ID, WireGuard public key, overlay address, and endpoint;
   - the `fixed_nodes` expansion template;
   - the operator Mac device ID and overlay address.

The three-node list retained in the production provider file is an expansion template, not the live shared resource declaration. Before scaling, explicitly confirm the network, subnet, machine type, and zones so old provider defaults are not applied accidentally.

### 4.2 Credentials and backups

- Use a short-lived SSH CA identity (for example `vault-migrate`) for the legacy node; do not use a long-lived root key in CI.
- Read XConnect network secrets, JWT roles, and invitations only from controlled Vault paths. Invitations must be single-use and short-lived.
- Before migration, take a Vault Raft snapshot, verify checksums, run a disposable restore drill, encrypt with age, upload to object storage, and verify a read-back copy.
- Keep unseal keys, operator tokens, and the age private key in controlled operator storage, for example:
  - `/root/vault-migration/operator-token`
  - `/root/vault-migration/unseal-keys.json`

These files must not be uploaded to GitHub, placed in Actions artifacts, or printed by commands.

### 4.3 Change window and stop conditions

Before changing anything, confirm:

- KV path count and path set have been compared read-only at the old and new entry points;
- the current DNS target is known;
- the legacy snapshot is readable and the restore drill has passed;
- every new SSH host key matches the declaration pin;
- TCP 8200/8201 are reachable in both directions over the intended data plane;
- a DNS rollback target and observation window are defined;
- a failed gate stops the run; no `stage_plan.py` or live-state check is bypassed.

## 5. Workflow entry point

All stages use `platform-ops-toolkit/.github/workflows/vault-server.yml`. Dispatch one class of action at a time:

| Input | Purpose |
| --- | --- |
| `deploy_action=plan` | Read-only GCP IaC plan |
| `deploy_action=apply` | Apply the GCP resource declaration; requires `main` and `prod` approval |
| `deploy_action=none` | Run one node stage or a read-only stage |
| `service_stage=<stage>` | Select one `node-*`, `fresh-*`, or `migrate-*` stage |
| `dns_action=verify` | Read-only DNS and HTTPS verification |
| `dns_action=switch` | Switch to the new entry point with `confirm=SWITCH-VAULT-DNS` |
| `dns_action=rollback` | Restore the legacy entry point with `confirm=ROLLBACK-VAULT-DNS` |

`dns_action` must be dispatched separately from node stages and IaC apply. Live stages use the workflow on `main` and a reviewed GitOps ref.

## 6. Phase A: deploy GCP nodes

### A1. Plan first

```bash
gh workflow run vault-server.yml \
  --repo ai-workspace-infra/platform-ops-toolkit \
  -f cloud_provider=gcp-cloud \
  -f deploy_action=plan \
  -f service_stage=none \
  -f dns_action=none \
  -f gitops_repo_ref=main \
  -f provider_manifest=resources/xworktech.com/shared/gcp/vault-shared.yaml
```

Confirm that the plan creates or destroys only the expected `vault-prod-*` resources. A one-node shrink should destroy only `vault-prod-1/2` and their addresses, disks, and associated resources.

### A2. Apply resources

```bash
gh workflow run vault-server.yml \
  --repo ai-workspace-infra/platform-ops-toolkit \
  -f cloud_provider=gcp-cloud \
  -f deploy_action=apply \
  -f service_stage=none \
  -f dns_action=none \
  -f gitops_repo_ref=main
```

Do not switch DNS immediately after apply. Run `node-preflight` and `node-process-metrics`; confirm OS Login, temporary SSH, no swap, sudo, disks, forwarding settings, and monitoring.

## 7. Phase B: establish the XConnect data plane

### B1. Create or rebuild the network

Use the XConnect Zero Cloud and Network Bootstrap workflow:

1. `deployment_profile=declared-network`;
2. `network_environment=prod` or an approved custom scope;
3. a GitOps manifest and immutable commit SHA;
4. `mode=dry-run` first, checking network ID, CIDR, Gateway ID, transport SNI/path, and invitation TTL;
5. `mode=apply` only after `prod` Environment approval.

The control plane writes only a short-lived, single-use invitation to a controlled Vault path. CI cannot read the invitation back.

### B2. Gateway frontend and enrollment

Run the Vault workflow stages in this order:

```text
vault-gateway-frontend
  -> xconnect-gateway
  -> xconnect-one
  -> xconnect-operator-invite (optional)
```

`vault-gateway-frontend` configures Caddy TLS 443 and `/xconnect` on the Gateway. It does not open WireGuard UDP directly.

`xconnect-gateway`:

- creates the Gateway device identity and WireGuard key;
- enrolls with a single-use invitation;
- verifies Gateway runtime, Xray, WireGuard, and Caddy.

`xconnect-one`:

- enrolls one node at a time;
- uses a distinct device identity for each new and legacy node;
- records overlay addresses in the GitOps topology and migration source;
- never reuses device keys or writes a join URI into shell history.

### B3. Data-plane acceptance

Before any Vault Raft join, verify from an allowed data-plane path:

```bash
systemctl is-active xconnect-gateway 2>/dev/null || systemctl is-active xconnect-one
ip addr show xconzero0 2>/dev/null || ip addr show xconone0
ping -c 3 10.79.0.1
curl -fsS http://<overlay-or-private-address>:8200/v1/sys/health
nc -vz <peer-overlay-or-private-address> 8200
nc -vz <peer-overlay-or-private-address> 8201
```

Every expected peer must have a recent WireGuard handshake; overlay ping must succeed; TCP 8200/8201 must work both ways; and public scans must not see 8200/8201 or UDP 51820.

## 8. Phase C: fresh cluster deployment

The fresh path is for an empty cluster only. Never use it for a migration target that contains historical data.

### C1. Install the leader

```text
service_stage=fresh-leader
deploy_action=none
```

The `vault-shared-leader` Playbook installs and configures `vault-prod-0`. From a controlled operator terminal:

```bash
export VAULT_ADDR=https://<leader-entrypoint>
vault operator init
vault operator unseal <one-share>
```

Move the remaining shares and root token into controlled storage immediately. Do not paste them into Actions logs.

### C2. Join peers one at a time

Dispatch `fresh-peers` once per peer:

1. the Playbook installs the next unjoined peer;
2. the operator unseals it using approved material;
3. `vault operator raft list-peers` confirms it is a voter;
4. the next `fresh-peers` dispatch starts only after that check.

After all three nodes are ready, run `service_stage=vault-raft-verify` with `deploy_action=none`. All nodes must be unsealed, Raft quorum must be healthy, roles must be correct, and Raft addresses must be private or overlay addresses.

## 9. Phase D: migrate the historical Vault

The migration path preserves the old data. Do not run `fresh-leader` or `vault operator init` on this path.

### D1. Migration preflight

```text
service_stage=node-preflight
service_stage=node-process-metrics
service_stage=migrate-preflight
```

`migrate-preflight` is read-only. It checks legacy reachability, Vault seal state, storage type, version, backup directory, and overlay address.

### D2. Convert the legacy node to single-node Raft

After the legacy node is enrolled and the `legacy-overlay` gate passes:

```text
service_stage=migrate-convert
confirm=CONVERT-VAULT-TO-RAFT
deploy_action=none
```

`deploy_vault_legacy_migration.yml` runs the `vault-legacy-convert` and `vault-single-raft` tags to:

1. back up the old `vault_storage` and calculate sha256;
2. stop Vault;
3. migrate the PostgreSQL-backed data into the local Raft data directory;
4. write the single-node Raft configuration;
5. install a host port guard allowing 8200/8201 only from loopback/overlay;
6. start Vault.

The operator then unseals with the existing key and confirms `vault.svc.plus` remains readable.

If conversion fails, and no Raft writes need to be kept, run:

```text
service_stage=migrate-rollback
confirm=ROLLBACK-VAULT-TO-POSTGRESQL
```

This restores the PostgreSQL-backed Vault. New writes made after conversion are not copied back automatically.

### D3. Snapshot and restore drill

```text
service_stage=vault-snapshot
deploy_action=none
```

The stage retrieves a Raft snapshot through the Vault API, checks `meta.json`, `state.bin`, and `SHA256SUMS`, restores it into a disposable Vault on the runner, encrypts it with age, uploads it to object storage, and verifies a read-back copy.

Do not run `migrate-join` until the snapshot, restore drill, encrypted upload, and read-back all succeed.

### D4. Join new nodes one at a time

```text
service_stage=migrate-join
deploy_action=none
```

The gates require the legacy node to be the active Raft leader, no foreign cluster on the new node, working `raft-overlay` and `overlay-raft-path`, the next unjoined declared peer, and the snapshot-first protection check.

The Playbook configures a join; it does not initialize a new cluster. After each peer joins:

1. unseal it with the existing material;
2. confirm it is a voter with `vault operator raft list-peers`;
3. check replication and leader address;
4. dispatch `migrate-join` again for the next peer.

### D5. Transfer leadership

After all new nodes are unsealed voters:

```text
service_stage=migrate-cutover
confirm=MOVE-VAULT-LEADER
deploy_action=none
```

The runner uses the restricted raft-operator token to request a step-down from the legacy node and retries until a new node leads. The legacy node may still forward as a standby, so DNS has not moved yet.

### D6. DNS cutover and observation

Run read-only verification first:

```text
deploy_action=apply
service_stage=none
dns_action=verify
```

Check every target HTTPS endpoint, Vault health, cluster ID, version, and leader/standby state. After the matrix passes:

```text
deploy_action=apply
service_stage=none
dns_action=switch
confirm=SWITCH-VAULT-DNS
```

Record `spec.migration.observation.dns_switched_at` and observe DNS resolvers, `sys/health`, client reads/writes, Raft peers/leader, XConnect handshakes, ports 8200/8201, monitoring, audit logs, and error rates.

### D7. Remove the legacy peer after observation

```text
service_stage=migrate-remove
confirm=REMOVE-LEGACY-VAULT-PEER
deploy_action=none
```

This stage requires DNS to have moved, the old node to be standby, all new nodes to be voters, and the observation window to be complete. It then removes the old peer through the Vault API, stops and disables the old Vault service, and retains the old data for the audit window. The operator must still complete rekey, old root-token rotation/revocation, and `vault_init.json` cleanup.

## 10. Scaling between one and three nodes

### 10.1 Expand from one to three

Use the order “declaration, resources, then Raft join”:

1. change the service declaration to `members: 3` and add `vault-prod-1/2` to `peers`;
2. add the two nodes, zones, host keys, machine types, and bootstrap addresses to the shared GCP declaration;
3. add both One nodes to the XConnect topology with non-conflicting overlay addresses;
4. run `deploy_action=plan` and review only the expected additions;
5. run `deploy_action=apply`;
6. run `node-preflight` and `node-process-metrics`;
7. enroll each node with `xconnect-one`;
8. use `migrate-join` for an existing data set, or `fresh-peers` for an empty cluster;
9. unseal each node and confirm it is a voter;
10. run `vault-raft-verify` and `vault-service-verify`.

Do not create VMs first and patch Raft addresses later. `cluster_addr` and listener addresses must be generated from private or overlay declarations.

### 10.2 Shrink from three to one

1. confirm `vault-prod-0` is the intended leader;
2. remove `vault-prod-1/2` as controlled Raft peers and verify they are no longer voters;
3. verify `vault-prod-0` remains initialized, unsealed, and active;
4. change GitOps to `members: 1`, `peers: []`, and only `vault-prod-0`;
5. run `deploy_action=plan` and confirm only `prod-1/2` instances, addresses, disks, and associated resources are destroyed;
6. run `deploy_action=apply`;
7. regenerate the CMDB contract and confirm one node;
8. run DNS verification and `vault-service-verify`.

Shrinking GCP must not delete the independent legacy Vault. Pausing that node is a separate operational action, not a GCP IaC deletion.

## 11. Rollback matrix

| Failure point | Action | Limitation |
| --- | --- | --- |
| XConnect is not connected | Stop, fix Gateway/One, handshakes, and 8200/8201 | Do not join Raft |
| Fresh leader initialization fails | Keep the empty node and fix declaration/Playbook | Do not reuse a legacy snapshot |
| Legacy conversion fails | `migrate-rollback` | Post-conversion Raft writes do not return to PostgreSQL |
| Snapshot or restore drill fails | Stop migration and fix backup | Do not run `migrate-join` |
| Peer join or unseal fails | Keep the old leader; repair or remove the problem peer | Do not cut over |
| Cutover succeeds but DNS has not moved | Repair the new leader | Do not remove the old peer |
| DNS observation fails | `dns_action=rollback` with `ROLLBACK-VAULT-DNS` | Confirm the legacy node can safely serve first |
| Failure after the observation window | Perform a manual disaster-recovery assessment | The old peer may be gone |
| Failure after old-peer removal | Restore using the most recent snapshot/DR procedure | The old node cannot be assumed to rejoin automatically |

Example DNS rollback:

```text
deploy_action=apply
service_stage=none
dns_action=rollback
confirm=ROLLBACK-VAULT-DNS
```

After rollback, repeat resolver, HTTPS health, Raft, and read-only KV checks. Never let both independent servers accept writes.

## 12. Acceptance checklist

### 12.1 CMDB and GCP

```bash
gcloud compute instances list \
  --project=open-platform-prod \
  --filter='name~^vault-prod-' \
  --format='table(name,zone,status,machineType,networkInterfaces[0].networkIP,networkInterfaces[0].accessConfigs[0].natIP)'

gcloud compute addresses list \
  --project=open-platform-prod \
  --filter='name~^vault-prod-' \
  --format='table(name,address,status,region)'
```

The output must match the one- or three-node live shared declaration. The generated `NodeDeployment` must have the expected provider, public/private addresses, host key, auth adapter, and groups.

### 12.2 Vault and Raft

```bash
export VAULT_ADDR=https://vault.svc.plus
vault status
vault operator raft list-peers
curl -fsS "$VAULT_ADDR/v1/sys/health"
```

Confirm initialized/unsealed state, the correct leader and voters, private/overlay cluster addresses, and the expected version, cluster ID, audit configuration, and KV mounts.

### 12.3 DNS and endpoint

```bash
for resolver in 1.1.1.1 8.8.8.8 9.9.9.9; do
  dig +short vault.svc.plus A @"$resolver"
done
curl -fsS https://vault.svc.plus/v1/sys/health
```

### 12.4 KV reconciliation

Recursively list KV v2 metadata paths read-only and compare the old and new entry points by mount set, mount version, secret-path count, and a digest of sorted paths. Do not read or print secret values. Matching paths do not prove business semantics; a service owner may perform a controlled canary read if needed.

## 13. Evidence index for the completed migration

| Operation | Run ID |
| --- | ---: |
| Three-node scale-up apply | `36281561086` |
| One-node plan | `36287710987` |
| One-node apply | `36287784202` |
| Read-only node preflight | `36288700637` |
| DNS verify | `36288820528` |
| DNS switch | `36288982485`, `36289337733` |
| DNS rollback | `36289258912` |

The implementation record is maintained in the platform-ops toolkit repository as `docs/vault/2026-09-27-gcp-vault-migration-implementation-record-zh.md`.

## 14. Incident handling principles

1. Stop before the next stage; never bypass a gate with a force flag.
2. Inspect live state first: Vault health, Raft peers, WireGuard handshakes, Caddy/Xray logs, and DNS.
3. Establish the one active write entry point before repairing or rolling back.
4. Perform any action requiring a root token, unseal share, or operator token in a controlled terminal, never in GitHub Actions output.
5. After fixing a declaration, run `plan` again and confirm that only expected resources change before `apply`.
6. Record the Git commit, Actions run ID, DNS result, and Vault/Raft state for every change.
