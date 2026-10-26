---
title: Proxy Server deployment profiles and control-plane boundaries
description: The deployment-profile note from GitOps PR 428, archived as a platform engineering white-paper reference with fixed provenance.
slug: proxy-server-deployment-profiles
lang: en
date: 2026-10-25
status: archived-design-not-runtime-acceptance
tags:
  - xconnect
  - proxy-server
  - platform-engineering
category: reference
---

# Proxy Server deployment profiles and control-plane boundaries

[中文版](proxy-server-deployment-profiles.zh.md) · [Platform engineering white paper](multi-cloud-platform-engineering-whitepaper.en.md) · [Reference overview](overview.en.md)

This record relocates the architecture note from GitOps PR #428 into the Knowledge white-paper reference collection. It preserves the three profiles described by the source; it does not establish deployment, connectivity, tenant isolation, or recovery acceptance.

## Original source text

The following text is preserved verbatim from the fixed source commit:

Proxy Server supports these deployment profiles:

1. **Fully self-hosted single node** — one node runs the Proxy Server and its local control
   components.
2. **Shared Proxy Server** — one Proxy Server node connects to the shared Full control plane.
3. **Team or shared Proxy Server** — one dedicated Proxy Server node connects to the Full control
   plane, with access limited by the configured team or shared tenant.

The Proxy Server node and Full control plane are separate deployment targets. The control-plane
endpoint, tenant/team scope, region and pool are supplied by the selected environment declaration;
credentials remain runtime-injected through Vault.

## Interpretation and ownership

The source distinguishes a shared node from a dedicated node and its access scope. It does not define the full tenancy model, authorization implementation, or runtime test results. Enrollment must not be treated as an automatic access grant. Later Team enrollment and approval behavior is recorded separately in the [Team Proxy enrollment reference (Chinese)](team-proxy-node-enrollment-20261020.zh.md), with its own implementation and acceptance evidence.

GitOps retains machine-consumed, non-sensitive desired state and configuration references. Knowledge owns this explanatory design record. IaC Modules, Playbooks, and Toolkit retain their resource, host/service, and orchestration responsibilities.

## Operational constraints for future implementation

Separate system administration, service runtime, and audit identities. Administrative identities must not run daily business processes; each service uses scoped read/write access and moves toward non-root operation incrementally; independent audit access must be read-only through enforced permissions. Verify the existing permissions first, change only confirmed issues and their minimum dependencies, and validate and switch one service at a time with evidence and rollback. These are current execution constraints, not evidence that the original commit implemented them or authorization for production changes.

## Provenance and archive scope

- Source discussion: [GitOps PR #428](https://github.com/ai-workspace-infra/gitops/pull/428).
- Fixed source: [README at 4c965e6](https://github.com/ai-workspace-infra/gitops/blob/4c965e657441140c65ae50cfaa52b2c2647571f1/README.md#proxy-server-deployment-profiles).
- Original commit: October 14, 2026; archive date: October 25, 2026, Asia/Shanghai.
- Archive task: [Knowledge #229](https://github.com/ai-workspace-services/knowledge/issues/229).

The scope is the 14 README lines added by that commit. At inspection, the source PR was open and unmerged, and its current diff included resource and topology files from other ancestor commits. It must not be merged as a README-only change. Those declarations and the original branch are preserved. GitOps main did not contain this profile section, so no removal from main was required.

This migration checks documentation and links only. Live deployment, permission isolation, connection, and recovery tests were not run. Archiving does not establish website publication or PR merge.
