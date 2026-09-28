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


### 4.4 Repository responsibilities and boundaries

The migration is implemented across several repositories. These boundaries distinguish a declaration drift problem from a runtime reconciliation problem:

| Repository | Key files/directories | Post-migration responsibility | Comparison source |
| --- | --- | --- | --- |
| `ai-workspace-infra/gitops` | `resources/svc.plus/shared/vault/server.yaml` | Vault service contract: domain, legacy source, Raft leader/peers, migration stages, SSH/overlay entry points | Legacy records and live Raft state |
| `ai-workspace-infra/gitops` | `resources/xworktech.com/shared/gcp/vault-shared.yaml` | Actual shared GCP resources in `open-platform-prod`: zones, machine type, host keys, SSH mode | `gcloud compute`/CMDB instances, addresses, disks and status |
| `ai-workspace-infra/gitops` | `vpn-overlay/shared/xconnect-vault-shared.yaml` | `net_shared_vault` CIDR, Gateway, One nodes, operator devices, VLESS transport and SSH policy | Accounts signed-config, device status and WireGuard peers |
| `ai-workspace-infra/platform-ops-toolkit` | `.github/workflows/vault-server.yml` | Single Vault entry point for declaration resolution, IaC, node stages, DNS verify/switch/rollback | Actions run, step summary and live-state gates |
| `ai-workspace-infra/platform-ops-toolkit` | `scripts/node_deploy/{resolve_vault_server_declaration.py,stage_plan.py,xconnect_stage.py,verify_vault_stage.py}` | Convert the GitOps contract into inventory, XConnect invitations, Playbook extra-vars and read-only checks | Rendered contract, node probes and Raft/DNS/XConnect results |
| `ai-workspace-infra/playbooks` | `deploy_vault_shared_services.yml`, `roles/vhosts/{vault,xconnect_gateway,xconnect_one,vault_gateway_frontend}` | Change hosts: install Vault/Caddy/Xray/WireGuard, write configuration and manage systemd; never initialize or unseal Vault | `systemctl`, configuration, ports and logs |
| `ai-workspace-service/accounts` | `internal/overlay`, `api/overlay_v1.go` | XConnect control plane: networks, devices, credentials, signed-config, ACK and revocation | Accounts API, device generation and Gateway peer snapshot |
| `ai-workspace-infra/iac-modules*` | GCP workload namespace/renderer and Terraform state | Render GCP declarations into instances, addresses, disks, firewall and IAM | Terraform plan/state and GCP CMDB |
| `ai-workspace-service/knowledge` | This runbook | Solution, evidence index, ordering and rollback rules; never a runtime configuration source | Git commit, Actions run ID and operator record |

The post-migration state must satisfy three kinds of consistency:

1. **Declaration consistency**: node count, overlay addresses, roles and migration source match the approved topology.
2. **Resource consistency**: CMDB/GCP instances, addresses, disks, zones and host keys match the provider manifest.
3. **Runtime consistency**: Vault Raft peers, Accounts signed-config, XConnect handshakes and DNS results agree with both declarations and resources.

When one layer disagrees with another, stop before the next stage. Do not hide GitOps drift by hand-editing a host. Fix the declaration, rerun `plan` or a read-only stage, and only then apply.

### 4.5 Post-migration declaration versus live-state comparison

The live shared state and the retained scale-out template are separate objects:

| Object | Current live steady state | Retained scale-out or historical object | Verification |
| --- | --- | --- | --- |
| Vault GCP resources | Only `vault-prod-0`, `asia-east1-a`, `RUNNING` | `vault-prod-1/2` can be declared again for scale-out | `gcloud compute instances list`, CMDB resolver |
| Vault Raft | `vault-prod-0` is the single voter/leader | Three-node join order is controlled by `members: 3` and `peers` | `vault operator raft list-peers` |
| XConnect Gateway | `vault-prod-0`, `10.79.0.1` | One addresses `10.79.0.2/10.79.0.3` are scale-out targets | Gateway signed-config, `wg show` |
| LAN SecOPS One | `10.79.0.7`, independent device ID, persistent systemd service | Not a Vault Raft voter | Accounts device, `xconnect-one status`, Mac → `10.79.0.7` |
| Operations Mac One | Re-enrolled device currently uses `10.79.0.9` | Old registration remains for a separate revoke window | GitOps operator device, signed-config, `utun7` |
| Legacy node | `46.250.251.132`/`vault-2`, independent server under observation | Not deleted by GCP IaC | Legacy service state, DNS and Vault health |
| DNS | `vault.svc.plus` points to the current GCP entry point | Legacy target remains the rollback target | Multiple resolver `dig`, HTTPS health |

Always compare resource count, Raft voter count, active Accounts device count and KV path count separately. An operator/LAN One is not a Vault voter, and the legacy node must not be destroyed as a side effect of GCP scale-down.


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


### 7.4 Complete XConnect establishment sequence

XConnect establishment has five layers: declaration, control-plane bootstrap, host enrollment, signed-config delivery, and data-plane reload. Troubleshooting must identify the layer that stopped:

```text
GitOps topology
   │  immutable commit
   ▼
Bootstrap workflow / xconnect_stage.py
   │  X-Service-Token exists only in runner memory
   ▼
Accounts net_shared_vault + one-use invite
   │  xconnect://join/... in a 0600 ephemeral file or controlled Vault path
   ▼
Gateway/One join
   │  WireGuard private key generated locally
   ▼
Signed-config + ACK
   │  peers, addresses, transport, policy, generation
   ▼
Caddy TLS :443 → Xray socket/UDP relay → WireGuard :51820
```

1. **Declare topology**: `vpn-overlay/shared/xconnect-vault-shared.yaml` defines `net_shared_vault`, `10.79.0.0/24`, Gateway `10.79.0.1`, nodes/operators and the `vless-xhttp` parameters. GitOps contains IDs, addresses, public keys and paths, never tokens, private keys or join URIs.
2. **Create network and invitation**: the `declared-network` profile of `xconnect-zero-cloud.yaml`, or the Vault server XConnect stage, consumes the reviewed manifest. `dry-run` validates only; `apply` calls Accounts `POST /api/internal/overlay/networks/bootstrap` with the owner, network, Gateway public key/address, transport and invite metadata. Each invite is bound to a device ID, role, platform and TTL. The returned `join_uri` is written only to a runner `0600` file or controlled Vault path and never to logs.
3. **Enroll Gateway**: the Gateway generates its local WireGuard identity and consumes a Gateway one-use invite. Accounts receives only the public key and stores device state and a credential hash; the Gateway receives its device credential and signature verification material.
4. **Enroll One devices**: each GCP peer, legacy node, LAN SecOPS node and Mac has its own device ID and one-use invite. One generates its private key locally, fetches `/api/overlay/v1/enrollment/signed-config`, and ACKs the corresponding generation.
5. **Load the Gateway peer snapshot**: the Gateway fetches active One peers, allowed IPs, relay and transport settings from `/api/overlay/v1/gateway/signed-config`. A device being registered in Accounts does not mean its peer is loaded; `wg show` changes only after Gateway sync/reload.
6. **Transport path**: the One WireGuard packet enters the local Xray loopback relay; Xray connects through VLESS + TLS/XHTTP to `vault-xconnect.svc.plus:443/xconnect`; Caddy terminates TLS and forwards to `/run/xconnect-gateway/xray.sock`; Gateway Xray sends the traffic to the local WireGuard peer.
7. **Persistence**: Gateway/One systemd services use `Restart=on-failure`, a stable state directory and a sync watcher. The Mac uses a LaunchDaemon and LAN SecOPS uses `xconnect-one-secops.service`. Reboots reuse the enrolled device credential rather than generating an unregistered temporary peer.

### 7.5 XConnect control-plane API and data-plane checkpoints

| Checkpoint | Control-plane evidence | Host/data-plane evidence | Failure meaning |
| --- | --- | --- | --- |
| Network exists | Accounts network `net_shared_vault` | Topology ID/CIDR match | Bootstrap incomplete or wrong network ID |
| Device enrolled | device ID, role, platform, active status | `xconnect-one status` reports `joined: true` | Invite not consumed or device conflict |
| Signed-config applied | generation/revision and ACK | `runtime.applied: true`, interface exists | Credential is valid but local sync failed |
| Gateway peer loaded | Gateway signed-config contains key/address | Gateway `wg show` has peer and fresh handshake | Gateway sync/reload is missing |
| Overlay reachable | allowed IP and policy are correct | `ping`, TCP 8200/8201 | WireGuard/Xray/firewall path failure |
| Vault reachable | Not guaranteed by the control plane | `curl /v1/sys/health`, `nc 8200/8201` | Vault listener or ACL failure |

The One `/api/overlay/v1/enrollment/signed-config` and Gateway `/api/overlay/v1/gateway/signed-config` are different snapshots. Do not use a One config as a Gateway peer config. A short control-plane outage may leave an already-loaded data plane forwarding, but new enrollment, revocation and peer changes wait for control-plane recovery and sync.

### 7.6 XConnect roles in this migration

| Role | Device/node | Address | Establishment | Current purpose |
| --- | --- | ---: | --- | --- |
| Gateway | `vault-prod-0` | `10.79.0.1` | Gateway one-use invite + Gateway signed-config | VLESS ingress, WireGuard relay and private Vault entry |
| Vault One template | `vault-prod-1` | `10.79.0.2` | One invite during scale-out | Raft voter/standby (not deployed in the current live state) |
| Vault One template | `vault-prod-2` | `10.79.0.3` | One invite during scale-out | Raft voter/standby (not deployed in the current live state) |
| Legacy Vault One | `vault-legacy` | `10.79.0.4` | Independent One enrollment for migration source | Legacy data plane and rollback observation |
| LAN SecOPS One | `xconnect-linux-secops-shenlan-inspiron-5415-ops` | `10.79.0.7` | Independent One invite + systemd | Operations access, not Raft |
| Mac One | `xconnect-darwin-haitaodemacbook-pro-rejoin.local` | `10.79.0.9` | Re-enrollment with protected credential | Operations access, not Raft |

Historical allocations such as `.5` or `.8` must not be manually reused because they appear free. Accounts signed-config and active-device state are the source of truth for address availability.

### 7.7 XConnect establishment/reload order

```text
1. Change and review the GitOps topology
2. XConnect Zero bootstrap dry-run
3. XConnect Zero bootstrap apply (one-use invite)
4. Gateway frontend (Caddy TLS + Xray socket)
5. Gateway identity/enrollment
6. Enroll One/legacy/LAN/Mac devices one at a time
7. Sync/reload Gateway peers
8. Handshake + overlay ping + TCP 8200/8201
9. Only then run Vault fresh/join/cutover or DNS stages
```

If a One reports `joined=true` but Gateway `wg show` has no peer, do not generate another local key or hand-edit allowed IPs. Check Gateway signed-config generation, the Gateway sync service and Accounts device status, then reload the Gateway. If a device ID already exists, issuing another invite with the same ID may return `state_conflict` or `device_conflict`; use the controlled revoke/re-enroll flow or a new explicit device ID, then update the GitOps policy.


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

### 12.3.1 XConnect overlay DNS implementation

The single source of truth for private DNS is `spec.dns` in the GitOps shared
Vault topology. The pipeline passes it through
`scripts/node_deploy/xconnect_stage.py` as `xconnect_gateway_dns_*` and
`xconnect_one_dns_*` Ansible variables, so a joining node does not need a
manually maintained DNS address.

The Gateway (`10.79.0.1`) runs the lightweight `dnsmasq` forwarder alongside
the XConnect data plane and listens on `xconone0` at `10.79.0.1:53`:

- when Accounts enrolls a new One, it assigns a unique overlay `/32`; on each
  sync the Gateway verifies its signed peer configuration and generates
  `<device-id>.shared.internal -> <overlay-ip>` in the hosts file consumed by
  dnsmasq, so operators do not enter a new node's address manually;
- after device revocation, the next signed Gateway configuration sync removes
  its A record;
- `spec.dns.records` declares service aliases by target `device_id`, for
  example `internal-xworkmate-bridge.svc.plus ->
  xconnect-linux-secops-shenlan-inspiron-5415-ops`; the Gateway resolves the
  alias to that One's current overlay address. The alias is absent while the
  device is not enrolled.
- `shared.internal` is marked as a local authoritative zone;
- names not present in the local zone are forwarded to
  `spec.dns.upstream_servers` (by default `1.1.1.1` and `8.8.8.8`) for public
  recursive resolution;
- dnsmasq binds only the overlay interface and address, never the public NIC.

After a Linux XConnect One joins, `systemd-resolved` installs the Gateway DNS
on `xconone0` and adds route-only domains for `shared.internal` and `svc.plus`.
By default `/etc/resolv.conf` points to the resolved stub. Private names
therefore use the Gateway while public names keep the host's normal resolver
path. If all queries must traverse the Gateway, add `~.` to the client route
domains; the Gateway will then recurse to the public DNS servers.

The native macOS XConnect One CLI does not change the system resolver. Create
the following files on an enrolled Mac:

```bash
sudo mkdir -p /etc/resolver
printf 'nameserver 10.79.0.1\n' | sudo tee /etc/resolver/shared.internal
printf 'nameserver 10.79.0.1\n' | sudo tee /etc/resolver/svc.plus
```

The XWorkMate app uses `https://internal-xworkmate-bridge.svc.plus`. The
`internal-` prefix distinguishes the private entry point from the public
hostname. Do not use an overlay IP, port 8787, or XRDP. The service alias
follows the current overlay address of the enrolled SecOPS One (currently
`10.79.0.7`). Caddy loads `tls_fullchain_pem_b64` and
`tls_key_pem_b64` from Vault `kv/data/CICD/domains/svc.plus` and validates SAN,
expiry, and key pairing before reloading. Enter a valid Bridge user Bearer
token in the app's access-token field; do not use a Vault token or XConnect
enrollment token.

Verify a newly enrolled One's automatic record and public recursion:

```bash
dig +short @10.79.0.1 xconnect-linux-secops-shenlan-inspiron-5415-ops.shared.internal
dig +short @10.79.0.1 internal-xworkmate-bridge.svc.plus
dig +short @10.79.0.1 example.com
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
