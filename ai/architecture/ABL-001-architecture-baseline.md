# ABL-001 — Architecture Baseline v1.0

| Field | Value |
|---|---|
| Document ID | ABL-001 |
| Version | 1.0 |
| Status | Approved |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | AI-0005 (decisions.md), DBD-001, API-001, API-000, BRR-001, SDD-000, DDD-001, SSD-001, AFR-001 |
| Next Documents | FS-001 (Vehicle Master) |

This document is the single point-in-time record of BIKEVALUATOR's
architecture reaching a buildable baseline: every decision the human
architect approved, exactly what changed as a result, and what — if
anything — is still deliberately deferred. It does not introduce new
architecture; it certifies and indexes decisions already made
elsewhere (`AI-0005`) and already propagated (see the Decision
Propagation Report delivered alongside this document).

---

## 1. Baseline Summary

**Baseline Version:** v1.0
**Approval Date:** 2026-08-02
**Approved By:** Human (architect) — blanket approval of all 17
`AI-0005` decisions as recommended, given in response to this prompt
(ABL-001).

### Approved Documents (status confirmed or elevated as of this baseline)

| Document | Version | Status |
|---|---|---|
| DBD-001 — Database Design | 1.1 | Approved |
| API-001 — Endpoint Inventory | 1.1 | Approved |
| API-000 — API Standards | 1.1 | Approved |
| BRR-001 — Business Rule Registry | 1.2 | Approved |
| SDD-000 — Domain Architecture & Entity Model | 1.1 | Approved |
| DDD-001 — Canonical Domain Model | 1.1 | Approved (was Needs Review) |
| SSD-001 — Canonical System Sequence Diagrams | 1.1 | Approved (was Needs Review) |
| FS-000 — Core Domain & Valuation Business Specification | 1.0 | Approved (unchanged this round) |

### Outstanding Deferred Decisions

Not part of `AI-0005` and **not** resolved by this baseline — carried
forward, tracked separately so they are never confused with the 17
decisions just approved:

1. **Standards Approval Matrix** (AFR-001 §4): NS-001/CSS-001/DOC-001/
   LOG-001 were *recommended* for Approved, TEST-001/SEC-001 for Needs
   Revision — this was a recommendation, never explicitly approved by
   the architect. Statuses remain as they were; still `Needs Review`.
   Not blocking FS-001 per AFR-001's own checklist, but should be
   closed out before FS-001's Definition of Done.
2. **SDD-000 §9 items 4-5** (offline capability, multi-region/
   multi-currency) — genuinely open, out of scope for `AI-0005`.
3. **SSD-001 §9 item 4** (payment webhook reconciliation/polling for
   lost deliveries) — explicitly deferred to FS-006 by `SEC-0002`
   itself, not an oversight.

### Deferred Modules / Scope

- **Notification, Analytics, Future-AI** domain objects — deferred per
  `OPS-0001`; no modeling until those bounded contexts are actually
  scoped.
- **`valuation_requests` (v2)** — schema exists in DBD-001 but remains
  inactive; not part of the v1 build.
- **ENG-0001** (Vehicle Selector always type-ahead) — approved in
  principle, but has no document to propagate into yet since no
  Flutter/FS-001 UI specification exists. It will be referenced by ID
  when FS-001's UI section is authored; no repository change was made
  for it this round, correctly, since nothing yet exists to change.

### Known Risks (carried from `AI-0005`'s Risk Register, still open)

| Risk ID | Description | Status after this baseline |
|---|---|---|
| RISK-ADR-01 | Authorization mechanism approved but could be implemented inconsistently across Admin endpoints | Open — now a live implementation risk for FS-001, not just a paper risk |
| RISK-ADR-02 | Concurrency policy approved on paper but not enforced in code | Open — same; a stale-write rejection test is recommended before FS-001 is called done |
| RISK-ADR-03 | API-000 left unrevised, contradicting API-001 | **Closed** — API-000 v1.1 now matches API-001 |
| RISK-ADR-04 | Recommendation thresholds confirmed without real valuation data | Open — accepted risk, thresholds kept easily revisable |
| RISK-ADR-05 | Webhook-dedup principle adopted but FS-006 forgets to implement it | Open — tracked for FS-006, not a v1/FS-001 concern |

### Baseline Scope

This baseline certifies **FS-001 (Vehicle Master)** is architecturally
unblocked: both Critical decisions (`SEC-0001`, `ENG-0003`) and the
High-priority decision (`ARC-0007`) are Approved and propagated, along
with all 14 other decisions relevant to later modules (recorded now so
they don't need to be re-litigated when FS-002/003/005/006 are
drafted). This baseline does **not** certify FS-002 through FS-006 are
ready to build — only that their architectural inputs are now decided;
each still needs its own FS document.

---

## 2. Decision Traceability Matrix

Decision ID → Affected Documents → Affected Modules → Affected APIs →
Affected DB Tables → Future FS.

| Decision ID | Affected Documents | Affected Modules | Affected APIs | Affected DB Tables | Future FS |
|---|---|---|---|---|---|
| BUS-0005 | BRR-001 (BR-0003), DDD-001 §12.5 | Valuation Engine, Reports | `/valuation/calculate` (response) | — | FS-002 |
| ARC-0005 | API-001 (Vehicle Master endpoints) | Vehicle Master | `/vehicles/brands`, `/vehicles/models`, `/vehicles/variants` | — | FS-001 |
| ARC-0006 | SDD-000 §8 (E-AUTHZ-001), API-000 §4 | Cross-cutting | All `/admin/*` | — | FS-001, FS-004 |
| ARC-0007 | API-000 (§3/§4/§6), API-001 | Cross-cutting | All endpoints | — | FS-001 onward |
| ARC-0008 | DBD-001 §2, DDD-001 §12.1 | Vehicle Master, Valuation Engine | `/vehicles/configuration` | (none — confirmed ephemeral) | FS-002 |
| SEC-0001 | DBD-001 §2 (`users.role`), SDD-000 §8 | Authentication, Admin, Cross-cutting | All `/admin/*`, `/auth/*` | `users` | FS-001, FS-003, FS-004 |
| ARC-0009 | DBD-001 §2, DDD-001 §12.3 | Valuation Engine | `/valuation/calculate` (request) | (none — confirmed transient) | FS-002 |
| ARC-0010 | DDD-001 §12.4 | Vehicle Master | — (code organization only) | `brands`, `models`, `variants` | FS-001 |
| BUS-0006 | BRR-001 (BR-0011), DBD-001 §2 | Vehicle Master | `/admin/valuation-master` | `valuation_master` (unique constraint) | FS-001 |
| OPS-0001 | DDD-001 §12.7 | Notification, Analytics, Future-AI (deferred) | — | — | Future scope |
| ENG-0001 | (none yet — no FS-001 UI doc exists) | Vehicle Master (Flutter UI) | — | — | FS-001 |
| ENG-0002 | API-001 (`/valuation/calculate`), SSD-001 §9.1 | Valuation Engine | `/valuation/calculate` | — | FS-002 |
| ENG-0003 | DBD-001 §6a, SSD-001 §9.2/§9.6 | Vehicle Master (Admin writes) | `/admin/valuation-master`, `/admin/repair-components` | `valuation_master`, `repair_options` | FS-001 |
| SEC-0002 | DBD-001 (Payments), API-001 (`/payment/webhook`), SSD-001 §9.3 | Payments | `/payment/webhook` | `payments` (unique `transaction_id`) | FS-006 |
| BUS-0007 | SSD-001 §9.7 | Subscription, Valuation Engine | `/valuation/calculate`, `/subscription/current` | — | FS-002, FS-005 |
| SEC-0003 | API-001 (`/auth/request-otp`), SSD-001 §9.8 | Authentication | `/auth/request-otp` | — | FS-003 |
| ENG-0004 | API-001 (Authentication), SSD-001 §9.9 | Authentication | `/auth/*` (no refresh endpoint) | — | FS-003 |

---

## 3. Architecture Change Control Policy (post-Baseline)

Lightweight, proportionate to this project's stage — not a heavyweight
change-board process.

1. **Any change to an Approved document's decided content** (not typos/
   formatting) requires a new or amended entry in `ai/decisions/
   decisions.md`, citing which prior decision it supersedes or amends.
   A document is never silently edited to contradict a decision that
   is still Approved.
2. **Superseding, never rewriting history.** If a decision changes
   (e.g. thresholds turn out wrong after real dealer usage), the
   original decision (e.g. `BUS-0005`) is marked Superseded with a
   pointer to the new decision ID — it is not edited or deleted.
3. **FS-level deviations must be logged, not silently absorbed.** If an
   FS document (starting with FS-001) needs to deviate from a baseline
   decision, that deviation is itself a new decision (with its own ID)
   requiring human approval — consistent with Rule 10. This is also the
   mechanism for closing the Outstanding Deferred Decisions above.
4. **Locked status still requires implementation to have begun**
   (Constitution Rule 20) — this baseline does not change that
   threshold. Once FS-001 code exists, the documents this baseline
   touched become eligible for `Locked`, not before.
5. **This baseline document itself is not re-issued per change.** Small
   corrections (e.g. closing a Deferred Decision) are appended as a
   dated note in §1; a new `ABL-002` is only warranted for another
   batch-scale decision-resolution event, not incremental drift.

---

## 4. Readiness Confirmation

**Is FS-001 — Vehicle Master ready to begin?** **Yes.** Both Critical
blockers identified in AFR-001 (`SEC-0001`, `ENG-0003`) and the
High-priority item (`ARC-0007`) are Approved and propagated into
DBD-001, API-001, and API-000. No architectural ambiguity remains for
Vehicle Master specifically. The three Outstanding Deferred Decisions
(§1) are explicitly non-blocking for FS-001 — they concern Standards
sign-off, offline/multi-region scope, and payment reconciliation, none
of which FS-001 (a catalog/pricing module) touches.
