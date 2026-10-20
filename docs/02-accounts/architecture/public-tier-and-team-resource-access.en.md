# Shared, Plus, Pro and Team resource access

Design approved by the user on 2026-10-21. This document specifies intended behavior, not deployment acceptance. The detailed [Chinese whitepaper](public-tier-and-team-resource-access.zh.md) is the companion reference.

Personal entitlements inherit lower tiers: Free ⊆ Plus ⊆ Pro. Pro currently aggregates shared/free and plus resources; it does not require a new physical Pro pool or dedicated hosts. Existing explicitly classified Pro resources, if present, remain available only to Pro.

| Caller | shared/free | plus | Existing pro resources | Own Team | Other Teams |
| --- | --- | --- | --- | --- | --- |
| Free | Allow | Deny | Deny | Hidden | Hidden |
| Plus | Allow | Allow | Deny | Hidden | Hidden |
| Pro | Allow | Allow | Allow | Hidden | Hidden |
| Dedicated Team member | Existing dedicated-only scope | Same | Same | Allow while valid | Hidden |
| Ordinary admin/operator | Own entitlement | Own entitlement | Own entitlement | Own valid membership only | Hidden |
| Root inventory view | Visible | Visible | Visible | Visible | Visible |

Team is the only team-owned exclusive resource category. Root inventory visibility does not automatically grant customer proxy access or bypass account suspension, quota, credential validity or team membership. All other callers, including admins/operators, must not receive cross-team endpoint metadata.

Accounts owns entitlement decisions. Reuse one public-tier authorization function for node discovery, full Agent user configuration and incremental/reconnect updates. Team membership remains a separate explicit check. Reject unknown or contradictory scopes; preserve account, quota, blacklist, node freshness and health gates.

Tests must cover the complete tier matrix; Pro aggregation without a physical pro node; root versus ordinary administrator inventory; own/other/expired/removed teams; node-list/configuration consistency; blocked users; downgrade/removal and stale events; and UI validation without fabricated endpoints. Fixtures must remain isolated from real subscriptions and financial data.

The UI retains its layout. Quota-exhausted status explains that upgrading can restore access after confirmed payment and effective entitlement, provided the new quota permits it. Same-cycle upgrades preserve used traffic and change the quota ceiling without stacking or clearing usage. Renewal or reviewed quota adjustment can also restore access.

No schema migration, new business database role, quota refill or financial write is required for this policy. Deliver the reviewed design, Accounts implementation/tests, Portal presentation and immutable release through their respective owners. Code checks, merge, deployment and live acceptance are distinct evidence gates.
