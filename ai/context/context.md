# Context — BIKEVALUATOR

**This is the first file every AI session must read.**

**Last update:** 2026-08-02T00:00

## Current Phase

**IMP-001D approved (9.6/10)** — the architect considers Vehicle
Master architecturally stable and did not request another refinement
round. **ISP-002 — Valuation Engine Implementation Specification
drafted** (`ai/architecture/isp/ISP-002-valuation-engine-
implementation-specification.md`, Status: Draft), continuing the
pipeline for FS-002.

**Flagged discrepancy (same pattern as IMP-001A/FS-001):** ISP-002's
commissioning message referred to FS-002 as "the approved FS-002," but
`FS-002-valuation-engine.md`'s own Status field still reads `Draft` —
no explicit closure statement like FS-001's "I consider FS-001 closed"
has been given for it yet. Not silently resolved either way — ISP-002
was still produced.

## Current Sprint

Review of ISP-002. Next: EP-002 (Valuation Engine Engineering
Package), following the same FS→ISP→EP→IMP pipeline as Vehicle Master.

## Current Objective

Human reviews ISP-002 and confirms FS-002's Status explicitly. Key
items: the new `RepairComponentRepository`/`RepairOptionRepository`
(this ISP resolves FS-002's Open Question #1 — this module's future
implementation creates these models, FS-004 extends them later, not
duplicates); the API-001 snake_case-vs-camelCase wording inconsistency
in `/valuation/calculate`'s response (resolved in favor of the
camelCase convention already used everywhere else); and confirmation
that `ValuationService` correctly has zero subscription-awareness
(BR-0006 deferred entirely to the View layer, once FS-005 exists).

## Last Completed Task

Executed ISP-002: two new Service classes (`ValuationService` — BR-0001/
BR-0002/BR-0009; `RecommendationService` — BR-0003/BR-0008, matching
SSD-001's actor separation rather than one monolithic service), two new
Repository interfaces (`RepairComponentRepository`/
`RepairOptionRepository`, read-only — administration stays FS-004's per
FS-001's own precedent), DTOs for `/valuation/calculate` and
`/repairs/components`, a Validation Matrix, an Error Mapping table, an
explicit Architecture Compliance Checklist (newly requested this
round), and a Dependency Analysis table. Sequence diagrams: cited
SSD-001 §3.3/§3.4 rather than re-drawn, per FSS-000 §5's own rule.
Explicitly reused Vehicle Master's shared infrastructure where it
genuinely applies (`api_utils.py`, `service_factory.py` extended with
2 new builders) and explicitly did NOT force-reuse `ActorProvider`/
`RequestContext`/`authorization.py`, since Valuation Engine has no
Super-Admin-only write (no BR-0004 concern exists in this module) —
flagged this distinction rather than mechanically applying every
Vehicle Master pattern regardless of fit. Cross-cutting note recorded
(not implemented): once this module's repositories exist, FS-001's
`get_configuration` could return real repair options instead of an
empty list — a follow-up task, not in this ISP's own scope.

## Current Task

Awaiting human review of ISP-002 and explicit confirmation of FS-002's
Status.

## Blockers

None hard-blocking the review. Two of ISP-002's 4 Open Questions carry
real weight before EP-002/implementation: the FS-005/BR-0006 deferral
pattern (confirm the View-layer-gate design is right) and the two
genuinely-undefined edge cases (MSP=0/Margin≥MSP; concurrent pricing
edit during calculation).

## Next Action

Human reviews ISP-002. Once satisfied (and FS-002's Status is
confirmed), draft EP-002 (Valuation Engine Engineering Package),
following the same pipeline used for Vehicle Master.
