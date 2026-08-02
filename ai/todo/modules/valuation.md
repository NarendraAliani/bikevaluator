# To-Do — Valuation Module

Second module in Phase 1 per the revised roadmap (BUS-0002) — depends on
Vehicle Master (FS-001, Approved). Business rules defined in
`ai/architecture/business-rules/BRR-001-business-rule-registry.md`
(BR-0001/0002/0003/0005/0006/0008/0009/0010, all Approved). The three
open business-rule questions this file used to track (Margin scope,
Scrap Value derivation, recommendation thresholds) were resolved via
BUS-0004/BUS-0005 — this file was stale until this round.

| Timestamp | Status | Owner | Task | Priority | Notes | Next Action |
|---|---|---|---|---|---|---|
| 2026-08-02T00:00 | Done | AI | Draft FS-002 — Valuation Engine, per FSS-000/fs-template.md | High | `ai/architecture/fs/FS-002-valuation-engine.md` (Draft): stateless Repair Assessment + Calculation + Recommendation flow via `/valuation/calculate`; BR-0001/0002/0003/0005/0006/0008/0009/0010 cited; 4 Open Questions surfaced | Human review of FS-002 |
| 2026-08-02T00:00 | Open | Human | Review FS-002 and its 4 Open Questions (Repair Master model/migration sequencing, FS-005 not existing yet for BR-0006, MSP=0/Margin≥MSP edge case, concurrent pricing edit during in-flight calculation) | Medium | None block FS-002 from being Approved as a document | Human answers, defers, or confirms document Approval |
| 2026-08-02T00:00 | Done | AI | Draft ISP-002 — Valuation Engine Implementation Specification | High | `ai/architecture/isp/ISP-002-valuation-engine-implementation-specification.md` (Draft): `ValuationService`/`RecommendationService`, new read-only `RepairComponentRepository`/`RepairOptionRepository` (resolves FS-002 Open Question #1), reuses Vehicle Master's `api_utils`/`service_factory`; explicitly does NOT use `ActorProvider`/`RequestContext` (no BR-0004 concern in this module) | Human review of ISP-002; confirm FS-002's Status (still Draft despite being called "approved") |
| 2026-08-02T00:00 | Open | Human | Confirm FS-002's Status field — ISP-002's commissioning message called it "approved" but the document itself still reads Draft | Medium | Same pattern as the FS-001/IMP-001A situation; not silently resolved either way | Set FS-002 Status explicitly |
| 2026-08-02T00:00 | Open | AI (once ISP-002 reviewed) | Draft EP-002 — Valuation Engine Engineering Package | High | Following the EP-001 precedent | Awaiting human review of ISP-002 |
