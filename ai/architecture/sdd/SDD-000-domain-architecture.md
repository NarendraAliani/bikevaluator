# SDD-000 — Domain Architecture & Entity Model

| Field | Value |
|---|---|
| Document ID | SDD-000 |
| Version | 1.1 |
| Status | Approved |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | FS-000, ARC-0002, BUS-0003, BRR-001, requirements-traceability-matrix.md, decision-traceability-matrix.md, AI-0005, ABL-001 |
| Next Documents | FS-001 (Vehicle Master) |

This document is the bridge between FS-000 (business requirements) and
implementation. It formalizes relationships, lifecycles, ownership,
interactions, constraints, and non-functional requirements that FS-000
named but did not structure. FS-001 (Vehicle Master) and all later FS
documents must conform to this document rather than re-deriving domain
structure independently.

---

## 1. Domain Model

```text
Dealer
  │
  │ initiates
  ▼
Evaluation ──────────────┐
  │                       │ references
  │ references            ▼
  ▼                    Vehicle Master Record
Vehicle                 (Brand, Model, Variant, Year,
  │                       MSP, Margin, Scrap Value)
  │ inspected via
  ▼
Repair Component Set
  │
  │ feeds
  ▼
Calculation
  │
  │ produces
  ▼
Recommendation
  │
  │ rendered as
  ▼
Report
```

Relationships:

- **Dealer** 1—N **Evaluation** (a dealer runs many evaluations).
- **Evaluation** N—1 **Vehicle** (each evaluation is for exactly one
  vehicle instance).
- **Vehicle** N—1 **Vehicle Master Record** (a vehicle instance is a
  concrete occurrence of a Year+Brand+Model+Variant catalog entry).
- **Evaluation** 1—N **Repair Component Assessment** (one per component
  inspected: Engine, Color, Tyres, Gearbox, Clutch, Plastic, and future
  components).
- **Evaluation** 1—1 **Calculation Result** → 1—1 **Recommendation** →
  1—1 **Report** (each evaluation produces exactly one of each,
  recalculated in place if the evaluation is revised — see §3).

---

## 2. Entity Catalogue

### Dealer
- **Fields:** id, name, contact info, subscription tier reference, status
  (active/suspended), created_at.
- **Ownership:** Admin creates/suspends; Dealer edits own profile fields
  only (not tier or status).
- **Lifecycle:** see §3.

### Vehicle Master Record (Brand/Model/Variant/Year + pricing)
- **Fields:** brand, model, variant, year, MSP, margin, scrap_value,
  active flag.
- **Ownership:** Admin only (per FS-000 §6 — dealers never edit pricing).
- **Lifecycle:** Draft → Active → Deprecated (superseded/discontinued
  variant, kept for historical evaluations, not selectable for new ones).

### Vehicle
- **Fields:** id, vehicle_master_record_id, evaluation_id (owning
  evaluation), created_at.
- **Ownership:** Created implicitly when a Dealer starts an Evaluation.
- **Lifecycle:** Tied 1:1 to its Evaluation; not independently mutable.

### Evaluation
- **Fields:** id, dealer_id, vehicle_id, state (see §3), repair
  component assessments, calculation_result, recommendation,
  created_at, updated_at, completed_at.
- **Ownership:** Dealer creates and progresses; system computes
  calculation/recommendation; Admin can view all, not edit dealer input.
- **Lifecycle:** see §3 — this is the central stateful entity.

### Repair Component Assessment
- **Fields:** evaluation_id, component_type (Engine/Color/Tyres/Gearbox/
  Clutch/Plastic/future), state (per FS-000 §3 scale), cost_applied.
- **Ownership:** Dealer records state during inspection; cost lookup is
  system-computed from Admin-maintained cost tables.

### Calculation Result
- **Fields:** evaluation_id, msp_used, margin_used, total_repair_cost,
  scrap_value_used, purchase_price, scrap_floor_applied (bool).
- **Ownership:** System-computed only, per FS-000 §4.1. Immutable once
  written; a re-calculation creates a new result tied to the same
  evaluation (old result retained for audit — see §6 NFR Audit Logging).

### Recommendation
- **Fields:** evaluation_id, score_percent, band (Excellent/Good/
  Average/Scrap).
- **Ownership:** System-computed from Calculation Result per FS-000 §5.

### Report
- **Fields:** evaluation_id, generated_at, format (PDF/share link),
  snapshot of all above at generation time.
- **Ownership:** System-generated on Dealer request once Evaluation is
  Completed.

### Subscription (forward-declared for later FS, not detailed here)
- **Fields:** dealer_id, tier, status, renewal_date.
- **Ownership:** Admin manages tier changes; billing owns status
  transitions (see Payments module, out of scope until FS-005).

---

## 3. State Machines

### Evaluation (the core lifecycle)

```text
Draft → Inspection → Calculated → Reviewed → Completed → Archived
```

- **Draft:** Vehicle selected (Year/Brand/Model/Variant), no repair data
  yet.
- **Inspection:** Repair Component Assessments being recorded.
- **Calculated:** All required components assessed; Calculation Result
  and Recommendation produced automatically on entry to this state.
- **Reviewed:** Dealer has viewed the result (distinguishes "computed"
  from "seen" for reporting/audit purposes).
- **Completed:** Report generated; Evaluation is now read-only except for
  re-opening (see below).
- **Archived:** Retained for history/audit, excluded from active dealer
  lists by default.
- **Re-opening:** A Completed evaluation can return to Inspection if the
  dealer amends repair data — this creates a new Calculation Result (old
  one retained, not overwritten) rather than mutating history.

### Vehicle Master Record

```text
Draft → Active → Deprecated
```

- **Draft:** Admin has entered Brand/Model/Variant/Year but not yet set
  MSP/Margin/Scrap Value — not selectable in the Vehicle Selector screen.
- **Active:** Fully priced, selectable for new Evaluations.
- **Deprecated:** No longer selectable for new Evaluations; existing
  Evaluations that reference it are unaffected.

### Dealer

```text
Invited → Active → Suspended → (Reactivated → Active | Deleted)
```

### Subscription (forward-declared, detailed in a later FS)

```text
Trial → Active → Expired → (Renewed → Active | Cancelled)
```

---

## 4. Module Boundaries

| Module | Owns | Does NOT own |
|---|---|---|
| **Vehicle Master** | Brand, Model, Variant, Year catalog; MSP, Margin, Scrap Value; Repair component cost tables | Evaluation state, Calculation logic |
| **Valuation Engine** | Evaluation lifecycle, Repair Component Assessments, Calculation, Recommendation | Pricing data (reads from Vehicle Master, never writes it) |
| **Authentication** | Dealer/Admin identity, login, roles/permissions | Business data of any kind |
| **Admin** | CRUD over Vehicle Master data, Dealer management, cost tables | Running Evaluations on a dealer's behalf (view-only) |
| **Subscription** | Dealer tier, trial/active/expired state | Payment processing (hands off to Payments) |
| **Payments** | Billing transactions, invoices | Subscription tier logic (only flips status on payment events) |
| **Reports** | PDF/report generation, report history, sharing | Calculation logic (reads Calculation Result, does not recompute) |

This table is the authority for "which module does X belong to" —
FS documents for each module must not claim ownership outside their row.

---

## 5. Event Flow

```text
Dealer selects Year → Brand → Model → Variant
        ↓
Vehicle Master module loads MSP, Margin, Scrap Value
        ↓ (if pricing missing → Error Catalogue: E-PRICING-001, evaluation blocked)
Evaluation enters Inspection state
        ↓
Dealer records Repair Component Assessments
        ↓
Valuation Engine computes Calculation Result on last required component
        ↓
Valuation Engine computes Recommendation
        ↓
Evaluation enters Calculated state
        ↓
Dealer views result → Evaluation enters Reviewed state
        ↓
Dealer requests Report → Reports module generates Report
        ↓
Evaluation enters Completed state
```

Branch: if the Dealer's Subscription is Expired at "Dealer selects
Year..." the flow is blocked before Vehicle Master load (see Error
Catalogue E-SUB-001).

---

## 6. Business Constraints

Centralized rules that apply across modules (supersedes any
module-local restatement — modules reference this list, they don't
redefine it):

1. MSP, Margin, and Scrap Value are editable only by Admin — never by
   Dealer (FS-000 §6).
2. Purchase Price is never below Scrap Value, regardless of calculation
   (FS-000 §4.1, AC-3).
3. An Evaluation cannot enter Inspection state without a fully Active
   Vehicle Master Record (Variant with MSP/Margin/Scrap Value set) —
   AC-5 in FS-000.
4. A Dealer with an Expired Subscription cannot start a new Evaluation
   (existing Evaluations remain viewable/read-only).
5. Calculation Results are immutable once written — corrections happen
   via re-opening the Evaluation (new result recorded, old retained), not
   by editing history.
6. Recommendation bands and thresholds are centrally defined (FS-000 §5)
   — no module or screen may hardcode its own thresholds.

---

## 7. Non-Functional Requirements (NFR)

| NFR | Requirement (initial — refine per module FS) |
|---|---|
| Performance | Vehicle selection and calculation must complete within an interactive response budget (target: sub-second for catalog lookups, sub-2s for full calculation) — exact SLOs deferred to a future PEP document. |
| Security | Dealer accounts cannot access or edit pricing data (enforced at API layer, not just UI); all Admin pricing edits are audit-logged. |
| Scalability | Vehicle Master catalog and Evaluation history must scale per-dealer without cross-dealer data leakage (multi-tenant isolation). |
| Offline capability | Not required for v1 (assumption — confirm before Flutter client architecture is finalized). |
| Backup | Standard PostgreSQL backup/retention policy — exact cadence deferred to an Ops decision (OPS category). |
| Audit logging | All pricing edits (Admin) and all Calculation Results (including superseded ones from re-opened Evaluations) must be retained, not deleted. |
| Availability | Not yet defined — deferred to a future OPS decision once hosting is chosen. |
| Localization | Not required for v1 (assumption — single locale/currency; revisit if multi-region dealers are in scope). |
| Time zone handling | All timestamps stored UTC; display conversion is a Flutter-client concern. |

Items marked "assumption" are open questions, not settled decisions —
see §9 and `ai/context/context.md`.

---

## 8. Error Catalogue

| Error ID | Condition | Handling |
|---|---|---|
| E-PRICING-001 | No MSP/Margin/Scrap Value for selected Year+Brand+Model+Variant | Block Evaluation from entering Inspection; show "pricing not available" (FS-000 AC-5) |
| E-CATALOG-001 | Duplicate Brand/Model/Variant/Year combination created by Admin | Reject at write time, surfaced to Admin UI |
| E-CATALOG-002 | Selected Variant is Deprecated | Block selection for new Evaluations; existing Evaluations unaffected |
| E-SUB-001 | Dealer's Subscription is Expired | Block new Evaluation creation; existing Evaluations remain read-only accessible |
| E-NET-001 | Network lost mid-Evaluation | Client retains unsaved Repair Component Assessments locally and retries (client-side concern, no server state corruption) |
| E-DEALER-001 | Dealer account Suspended | Block all Evaluation actions; Admin/Auth-owned |
| E-AUTHZ-001 | A Dealer-role account attempts a Super-Admin-only action (e.g. editing MSP/Margin/Scrap Value, or any `/admin/*` endpoint) | Reject with 403 Forbidden at the API boundary; log the attempt (LOG-001 Audit level); never rely on client-side role display |

Added per `ARC-0006` (`AI-0005`, ABL-001) — a single, cross-cutting
authorization error rather than each future module inventing its own.
Checked against the `users.role` column added to DBD-001 per `SEC-0001`.

This catalogue will grow per-module as FS-001 onward are drafted — this
is the seed list derived directly from constraints already named in
FS-000 and this document.

---

## 9. Open Questions Carried Forward

**Correction (ABL-001, 2026-08-02):** items 1-3 below were left listed
as open in this document after they were actually resolved by BUS-0004
and BUS-0005 — an oversight in prior propagation, corrected now rather
than left contradicting BRR-001 (the source of truth for rule status).

Resolved:

1. ~~Is Margin per-dealer/region-configurable, or global?~~ — Global,
   resolved BUS-0004.
2. ~~Is Scrap Value independently maintained or derived from MSP?~~ —
   Independently maintained, resolved BUS-0004.
3. ~~Final recommendation thresholds~~ — Confirmed 90/75/60% per
   `BUS-0005` (`AI-0005`, ABL-001); see BRR-001 v1.2 BR-0003.

Still genuinely open (product/NFR scope, not covered by `AI-0005`):

4. Is offline capability required for the Flutter client in v1?
5. Is multi-region/multi-currency support required, or single-locale for
   v1?

---

## 10. Cross-Reference and Traceability

Per-section mapping (which future module/API/DB/UI owns each FS-000
section) and the full requirement→entity→DB→API→UI→test traceability
matrix are maintained separately in
`ai/architecture/traceability/requirements-traceability-matrix.md` so
that file can be updated independently as each module FS is drafted,
without re-editing this document.
