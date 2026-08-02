# FS-002 — Valuation Engine

| Field | Value |
|---|---|
| Document ID | FS-002 |
| Version | 1.0 |
| Status | Draft |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | FS-000, FS-001, FSS-000, DDD-001, DBD-001, API-001, BRR-001, SDD-000, SSD-001, ABL-001 |
| Next Documents | ISP-002 (Valuation Engine Implementation Specification) |

Second module built against the Baselined architecture (ABL-001), the
second document conforming to FSS-000. Per FSS-000's Definition of
Ready: every `AI-0005` decision tagged Blocking Module = FS-002
(`BUS-0005`, `ARC-0008`, `ENG-0002`, `BUS-0007`) is Approved; DBD-001,
API-001, BRR-001, SDD-000, DDD-001, SSD-001 are all Approved; FS-001
(the one FS this module depends on) is Approved and closed; the
roadmap (BUS-0002) places Valuation Engine immediately after Vehicle
Master, confirmed explicitly by the architect this round. No new API,
schema, business rule, or architectural decision is introduced here —
genuinely open items are recorded in §Open Questions, not resolved by
assumption.

## 1. Purpose

The Valuation Engine is BIKEVALUATOR's core IP (roadmap: reordered
ahead of Authentication for exactly this reason — "if it's wrong,
nothing built on top of it matters"). It turns a Dealer's vehicle
selection (FS-001's output) plus a Repair Component Assessment into a
Purchase Price and a Recommendation label, by applying BR-0001
(pricing formula), BR-0002 (scrap floor), BR-0009 (rounding), BR-0003/
BR-0008 (recommendation banding) — server-side only, never in the
Flutter client (ADR-005, ADR-014).

## 2. Scope

**In scope:**

- Repair Component Assessment: the Dealer records one condition
  (RepairOption) per RepairComponent (SSD-001 §3.3).
- Calculation: BR-0001 (Purchase Price = MSP − Margin − Repair Cost),
  BR-0002 (scrap floor), BR-0009 (round to nearest ₹10) via
  `POST /valuation/calculate` (API-001, SSD-001 §3.4).
- Recommendation: BR-0003/BR-0008 (centralized bands, now confirmed
  90/75/60% per `BUS-0005`).
- Read-only consumption of `RepairComponent`/`RepairOption` data
  (DBD-001 §2's already-Approved schema) needed to look up each
  selected option's fixed ₹ deduction (BR-0010).

**Out of scope (owned elsewhere):**

- **Repair Component/Option administration** (creating/editing the
  catalog of components and their deduction amounts) — SSD-001 §10
  traces this to **FS-004** (Admin), the same precedent FS-001 §2
  established for excluding Repair Master's write side. FS-002 only
  *reads* this data (BR-0010's lookup), never writes it.
- **Vehicle Master catalog/pricing** — FS-001 (Approved). FS-002 reads
  `ValuationMaster` via Vehicle Master, never writes it (SDD-000 §4:
  "Valuation Engine... does NOT own: Pricing data").
- **Subscription tier/expiry logic itself** — FS-005 (not yet drafted).
  BR-0006 (expired Subscription blocks new Valuation) is a
  *precondition* this module depends on, not something it implements —
  see §4 Preconditions and §23 Cross-FS Dependencies for how this is
  handled given FS-005 doesn't exist yet.
- **Authentication** — FS-003 (not yet drafted). Assumed satisfied at
  the API boundary, same as FS-001.
- **Report generation** (PDF/share link) — a separate "Reports"
  bounded context (DDD-001 §2, v2/disabled) — out of scope for v1.

**Important framing, sourced from DBD-001 (not invented):** in v1,
this entire flow is **stateless**. `valuation_requests` (the only table
that could persist an Evaluation/Calculation/Recommendation) is
explicitly "not written to in v1" (DBD-001 §2). SDD-000 §3's Evaluation
state machine (Draft→Inspection→Calculated→Reviewed→Completed→Archived)
therefore describes a **client-side/UI-flow concept in v1**, not a
row's state in a database — confirmed by SSD-001 §5's State
Synchronization table, which marks all in-progress Repair Assessment
state as client-held and "always disposable." This document treats the
Evaluation lifecycle accordingly: real for UX sequencing, not backed by
a persisted Evaluation entity.

## 3. Actors

Per SSD-001 §2 (restated, not redefined):

| Actor | Role in this module |
|---|---|
| **Dealer** | Records Repair Component Assessments, submits for calculation, views the Recommendation. |
| **Flutter Client** | Holds in-progress assessment state locally (disposable); computes no business rules (ADR-005, ADR-014). |
| **Valuation Engine (Valuation Service + Pricing Service)** | Orchestrates BR-0001/BR-0002/BR-0009. |
| **Recommendation Service** | Applies BR-0003/BR-0008 to the computed price. |
| **Vehicle Master** | Supplies MSP/Margin/Scrap Value (FS-001, read-only dependency). |
| **Repair Master** | Supplies fixed ₹ deduction per RepairOption (read-only dependency; administration is FS-004's). |
| **Subscription Service** | Gates entry per BR-0006 (FS-005 dependency, not yet implemented — see §23). |

## 4. Preconditions

- Requesting user is authenticated (FS-003 scope, assumed).
- A Dealer has already completed FS-001's Vehicle Selection flow
  (Year+Brand+Model+Variant chosen, Configuration Loaded) — this
  module's Repair Assessment screen only makes sense after that.
- BR-0005: an Active `ValuationMaster` record must exist for the
  selected Year+Variant (enforced by FS-001's `get_configuration`,
  already implemented — `PricingNotAvailableError`/VAL003).
- BR-0006: the Dealer's Subscription must not be Expired at flow start
  (`BUS-0007`: checked only at flow start, not re-checked mid-flow) —
  **FS-005 does not exist yet**, so this precondition cannot be
  code-enforced until FS-005 is implemented; see §23.

## 5. User Stories

- As a **Dealer**, I want to record each visible component's condition
  (OK/Partial/Full), so that the price reflects the vehicle's actual
  state.
- As a **Dealer**, I want the system to compute the Purchase Price
  automatically once I submit my assessment, so that I don't have to
  do the arithmetic myself (the exact problem BIKEVALUATOR replaces —
  the dealer's Excel model, FS-000).
- As a **Dealer**, I want a clear Excellent/Good/Average/Scrap
  recommendation, so that I can make a fast buy/pass decision.
- As a **Dealer**, I want the Purchase Price to never go below the
  Scrap Value, so that I'm never told to pay more than the vehicle is
  worth as scrap (BR-0002).
- As a **Dealer**, I want to safely retry the calculation if my
  network drops mid-request, so that a lost response doesn't force me
  to re-enter my assessment (`ENG-0002`).

## 6. Functional Requirements

| ID | Requirement | Traces to User Story |
|---|---|---|
| FR-002-001 | System shall accept a Repair Component Assessment (one `RepairOption` selection per required `RepairComponent`) in the `POST /valuation/calculate` request body. | US-1 |
| FR-002-002 | System shall reject a submission with any required `RepairComponent` unassessed, client-side, before the request is sent (SSD-001 §3.3) — not this module's server-side concern beyond receiving a complete payload. | US-1 |
| FR-002-003 | System shall load the Active `ValuationMaster` (MSP, Margin, Scrap Value) for the submitted Year+Variant from Vehicle Master (FS-001). | US-2 |
| FR-002-004 | System shall load each selected `RepairOption`'s fixed ₹ deduction amount from Repair Master (read-only). | US-2 |
| FR-002-005 | System shall compute Purchase Price = MSP − Margin − Σ(Repair Cost deductions) (BR-0001). | US-2 |
| FR-002-006 | System shall floor the result at Scrap Value if the computed price is lower (BR-0002). | US-4 |
| FR-002-007 | System shall round the final Purchase Price to the nearest ₹10 (BR-0009). | US-2 |
| FR-002-008 | System shall compute `score_percent` = rounded Purchase Price / MSP, and select a Recommendation band from the confirmed 90/75/60% thresholds (BR-0003, `BUS-0005`), never a module-local threshold (BR-0008). | US-3 |
| FR-002-009 | System shall return `{recommended_price, rounded_price, label}` in the response (API-001). | US-3 |
| FR-002-010 | System shall raise `PricingNotAvailableError` (VAL003/E-PRICING-001, BR-0005) if no Active `ValuationMaster` exists — delegated to/reusing FS-001's existing check, not reimplemented. | US-2 |
| FR-002-011 | System shall perform no idempotency-key check or deduplication on `/valuation/calculate` — the endpoint is stateless (no writes to `valuation_requests`), so a retried request is naturally safe (`ENG-0002`). | US-5 |
| FR-002-012 | System shall not persist the Calculation Result or Recommendation anywhere in v1 (`valuation_requests` stays inactive, DBD-001 §2). | — |
| FR-002-013 | System shall honor an in-flight Valuation even if the Dealer's Subscription expires between Configuration Load and the calculation request (`BUS-0007`) — expiry is checked only at flow start (FS-005 dependency, not yet implementable — see §23). | — |

## 7. Business Rules

This module implements: **BR-0001, BR-0002, BR-0003, BR-0005 (consumed,
not re-enforced), BR-0008, BR-0009, BR-0010, BR-0006 (dependency, see
§4/§23)**. Rule text is not restated here — see BRR-001 v1.2 for the
authoritative definitions.

## 8. Validation Rules

Field-level input constraints (distinct from §7's cross-field business
rules):

- Repair Assessment payload: exactly one `RepairOption` id per required
  `RepairComponent` — a missing or duplicate component selection is a
  request-shape error, not a business-rule violation.
- `year`, `variant_id`: same validation as FS-001 §8 (already
  implemented) — reused, not redefined here.
- No new field-length/range validators are introduced by this module.

## 9. UI Requirements

Behavioral only — no visual design (Design System territory, per
FSS-000 §1 item 9):

- **Repair Assessment screen:** one control per `RepairComponent`
  (Engine, Colour, Gearbox, Tyre, Plastic, Clutch, and future
  components per DBD-001 §2), defaulting every component to "OK"
  (SSD-001 §3.3 note — a Dealer opts into a worse condition, not the
  reverse). Submission is blocked client-side until every required
  component has a selection (FR-002-002).
- **Result screen:** displays the Recommendation label prominently
  (Excellent/Good/Average/Scrap) alongside the rounded Purchase Price —
  the label, not the raw percentage, is the primary UX signal (FS-000
  §5).

## 10. Navigation

- **Entry point:** hands off directly from FS-001's Vehicle Selector
  screen on successful Configuration Load (FS-001 §10).
- **Exit:** Result screen → (future) Report generation, out of this
  module's scope (a separate "Reports" bounded context, DDD-001 §2).

## 11. API Mapping

Cited from API-001 v1.1 by path only — no new endpoint introduced:

| Endpoint | Method | Used For |
|---|---|---|
| `/valuation/calculate` | POST | FR-002-001 through FR-002-011. Request: VehicleIdentity (year, variant_id) + RepairAssessment. Response: `{recommended_price, rounded_price, label}` (API-001). |
| `/repairs/components` | GET | Supplies the Repair Assessment screen's component/option list (FR-002-004's client-side counterpart) — read-only, per API-001. |

Envelope: `{success, message, data}` / `{success, message, errors}`
(API-000 v1.1, `ARC-0007`) — not restated here.

## 12. Database Mapping

Cited from DBD-001 v1.1 by table/column only — no new schema
introduced. **Sequencing note, not an architecture question:** the
`repair_components`/`repair_options` tables are already schema'd in
DBD-001 §2, but no IMP-* prompt has created their Django models/
migrations yet (FS-001's implementation excluded them, per FS-001 §2).
FS-002 is the first module that needs to *read* this data — see §23
for who should create these models.

| Table | Used For |
|---|---|
| `valuation_master` (read-only) | FR-002-003, FR-002-006, FR-002-010 |
| `repair_components`, `repair_options` (read-only) | FR-002-004 |
| `valuation_requests` (v2, inactive) | Not used in v1 (FR-002-012) |

No table is written to by this module in v1.

## 13. Sequence Flow

No new diagram — this module conforms exactly to two existing SSD-001
diagrams:

- **SSD-001 §3.3 — Repair Assessment:** Dealer records conditions,
  client validates completeness, submits `/valuation/calculate`.
- **SSD-001 §3.4 — Valuation:** Configuration retrieval → BR-0001 →
  BR-0002 → BR-0009 → BR-0003/BR-0008 → response, stateless.

## 14. Error Handling

| Error | Source | Behavior |
|---|---|---|
| `VAL003` / `E-PRICING-001` | API-001 / SDD-000 §8 | No Active `ValuationMaster` — block, reuse FS-001's existing check (BR-0005). |
| `SUB001` / `E-SUB-001` | API-001 / SDD-000 §8 | Dealer's Subscription is Expired — block new Valuation (BR-0006); not code-enforceable until FS-005 exists (§23). |
| `E-NET-001` | SDD-000 §8 | Network lost mid-Evaluation — client retains unsaved Repair Component Assessments locally and retries; safe because of `ENG-0002` (FR-002-011). |

No new error code is introduced by this module.

## 15. Permissions

Any authenticated Dealer with a valid (non-Expired) Subscription may
call `/valuation/calculate` — no Super-Admin-only concern in this
module (contrast FS-001's Admin write endpoints). No new permission
model introduced.

## 16. Audit Logging

**None.** This module performs no writes (v1 is fully stateless, §2),
so DBD-001's audit-log requirement ("logs all Super Admin master-data
changes") does not apply here — there is nothing to log.

## 17. Performance Expectations

Specializes SDD-000 §7's NFR ("target: sub-2s for full calculation")
for this module specifically: `/valuation/calculate` should target
sub-2-second response, including its two read dependencies (Vehicle
Master's `ValuationMaster` lookup, Repair Master's deduction lookups).
Exact SLOs remain deferred to a future PEP document, per SDD-000 §7.

## 18. Security Considerations

- Business logic (BR-0001/BR-0002/BR-0003/BR-0008/BR-0009) executes
  server-side only, never in the Flutter client (ADR-005, ADR-014,
  restated from FS-001's own §18 for this module's calculation logic
  specifically).
- No PII is processed by this module beyond what FS-001/FS-003 already
  handle at the request-authentication layer.
- SEC-001 remains `Needs Review` (unchanged status) — this FS depends
  on nothing beyond what's already cited from SDD-000/DBD-001.

## 19. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-002-001 | Given MSP=₹50,000, Margin=₹5,000, and total Repair Cost deductions=₹3,000, when `/valuation/calculate` is called, then the computed Purchase Price before rounding is ₹42,000. |
| AC-002-002 | Given a computed Purchase Price below Scrap Value, when `/valuation/calculate` is called, then the returned price equals the Scrap Value, not the lower computed figure (BR-0002). |
| AC-002-003 | Given a Purchase Price of ₹42,003, when rounded per BR-0009, then the returned `rounded_price` is ₹42,000. |
| AC-002-004 | Given `rounded_price`/MSP ≥ 90%, when the Recommendation is computed, then `label` = "Excellent"; given 75–89%, "Good"; given 60–74%, "Average"; given <60%, "Scrap" (BR-0003, thresholds confirmed via `BUS-0005`). |
| AC-002-005 | Given no Active `ValuationMaster` for the requested Year+Variant, when `/valuation/calculate` is called, then the response is `VAL003`/`E-PRICING-001`, with no partial calculation returned. |
| AC-002-006 | Given a `/valuation/calculate` request is retried identically after a client-observed timeout, when both requests are eventually processed, then no error or duplicate side effect occurs (the endpoint being stateless makes this trivially true — `ENG-0002`). |
| AC-002-007 | Given the calculation completes successfully, then no row is written to `valuation_requests` or any other table (v1 statelessness, FR-002-012). |

## 20. Edge Cases

Cross-checked against SSD-001 §6's Failure Scenarios matrix for
Valuation:

- All `RepairComponent`s assessed as "OK" (no deductions) — Purchase
  Price = MSP − Margin, per BR-0001; not a special case, just Σ=0.
- Every component assessed "Full" (maximum deductions) — Purchase
  Price could reasonably fall below Scrap Value; BR-0002's floor
  applies (AC-002-002).
- MSP = 0 or Margin ≥ MSP — SSD-001 §6 marks this "open question" at
  the behavioral level; FS-001 §8 already requires MSP/Margin/Scrap
  Value ≥ 0 individually, but no document specifies whether Margin may
  legitimately exceed MSP. Not resolved here — see Open Questions.
- Concurrent pricing edit *during* a calculation (Super Admin revises
  `ValuationMaster` mid-request) — SSD-001 §6 marks this an open
  question too; not resolved here (see Open Questions), though
  `ENG-0003`'s optimistic-concurrency mechanism means the *write* side
  is protected regardless — it's specifically the *read-then-use*
  timing on the Valuation Engine's side that remains open.

## 21. Future Enhancements

- Persisting Calculation Results (`valuation_requests` v2) once that
  table is activated — explicitly deferred, not planned for this
  module's v1 scope.
- Per-dealer/region Margin override — explicitly rejected for v1
  (DDD-001 §3 `ValuationMaster`, BDR-0002); noted only as a documented
  future possibility.
- Admin-configurable recommendation thresholds — explicitly rejected in
  favor of the fixed 90/75/60% constant for v1 (`BUS-0005`).

## 22. Architecture Compliance Checklist

| Field | Content |
|---|---|
| Architecture documents referenced | DDD-001 §3 (RepairComponent, RepairOption, RepairAssessment, Valuation, Recommendation); DBD-001 §2 (Valuation Master, Repair Module, valuation_requests); API-001 v1.1 (`/valuation/calculate`, `/repairs/components`); BRR-001 v1.2 (BR-0001/0002/0003/0005/0006/0008/0009/0010); SDD-000 v1.1 §3, §4, §7, §8; SSD-001 v1.1 §3.3, §3.4, §5, §6, §10; ABL-001; FSS-000; FS-001. |
| Decision IDs implemented | `BUS-0005` (thresholds, §6/§19), `ARC-0008` (Vehicle ephemeral — this module never persists a Vehicle instance either), `ENG-0002` (no idempotency key, §6/§19), `BUS-0007` (in-flight Valuation honored on Subscription expiry, §4/§6). |
| Business Rule IDs referenced | BR-0001, BR-0002, BR-0003, BR-0005, BR-0006, BR-0008, BR-0009, BR-0010. |
| APIs used | `/valuation/calculate`, `/repairs/components`. |
| Database tables used | `valuation_master` (read-only), `repair_components`, `repair_options` (read-only). No table written. |
| Deviations | None introduced. One pre-existing sequencing gap noted, not a deviation: `repair_components`/`repair_options` have no Django models/migrations anywhere yet — see §23/Open Questions for the recommended resolution. |
| New architectural questions | See §Open Questions below — three items, none resolved by assumption. |

## 23. Cross-FS Dependencies

| Depends On (must be Approved first) | Provides To (future FS depending on this one) |
|---|---|
| **FS-001 (Vehicle Master):** Approved. Reads `ValuationMaster` (MSP/Margin/Scrap Value) for every calculation. | **FS-005 (Subscription):** conceptually — BR-0006's gate is checked *before* this module's flow begins; FS-005 will own that check's implementation. |
| **FS-005 (Subscription) — not yet Approved, does not yet exist.** BR-0006 (§4) is a precondition this module's *specification* depends on conceptually, but cannot be code-enforced until FS-005 exists. This is a genuine forward dependency, flagged rather than silently worked around — see Open Questions. | **Reports (future bounded context):** would read this module's Calculation Result/Recommendation once persistence (`valuation_requests` v2) is activated — not yet in scope. |
| **Repair Master (no FS number assigned to its own creation)** — see Open Questions for who creates `repair_components`/`repair_options` models first. | |

## Open Questions

Genuinely undefined — not invented, not silently resolved:

1. **Repair Master model/migration ownership (sequencing, not
   architecture)** — `repair_components`/`repair_options` are already
   schema'd in DBD-001 §2, but no FS/IMP prompt has created their
   Django models yet. FS-002 is the first module needing to *read*
   this data; FS-004 will eventually *administer* it. Recommend
   whichever module is implemented first creates the models (mirroring
   how FS-001 already created `valuation_master`, which FS-002 now
   reuses) — not resolved here, since it's an implementation-sequencing
   choice for ISP-002, not a specification-level decision.
2. **FS-005 doesn't exist yet — BR-0006 can't be code-enforced today.**
   This document specifies the precondition (§4) and defers its actual
   implementation mechanism (likely a duck-typed "Subscription status"
   placeholder, analogous to FS-002/IMP-001B's duck-typed `Actor` for
   BR-0004) to ISP-002/IMP-002 — flagged now so it isn't a surprise
   later.
3. **MSP=0 / Margin ≥ MSP edge case** — carried from SSD-001 §6, still
   undefined at the behavioral level: is a resulting negative or
   zero Purchase Price (before the Scrap floor applies) valid, or
   should it be rejected as a data-quality error at the Vehicle Master
   layer instead? Not resolved here.
4. **Concurrent pricing edit during an in-flight calculation** —
   carried from SSD-001 §6: if a Super Admin revises `ValuationMaster`
   between this module's read and its use in the formula, is the
   Dealer's result silently based on stale data, or should the read
   be repeated at write-commit time? `ENG-0003` protects the write
   side; this is specifically about the Valuation Engine's read-then-
   compute timing, which remains open.
