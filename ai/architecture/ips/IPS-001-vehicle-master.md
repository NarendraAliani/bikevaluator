# IPS-001 — Vehicle Master Implementation Planning Specification

| Field | Value |
|---|---|
| Document ID | IPS-001 |
| Version | 1.0 |
| Status | Needs Review |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | FS-000, SDD-000, BRR-001, API-000, NS-001, CSS-001, DOC-001, TEST-001, LOG-001, SEC-001, DD-Vehicle, requirements-traceability-matrix.md, decision-traceability-matrix.md |
| Next Documents | IPS-002 (Valuation Engine), FS-001 (if a separate business-requirements document is still wanted ahead of implementation) |

This is a **planning document only**. No Flutter, Django, PostgreSQL,
API, repository, service, widget, or test code is produced here. Its
purpose is to remove implementation ambiguity so a future implementation
prompt can generate deterministic code without inventing architecture or
business rules. Every business rule referenced below cites a `BR-000x`
ID from BRR-001 — none are restated or reinvented.

---

## 1. Module Overview

**Purpose:** Vehicle Master is the authoritative catalog of what a
vehicle *is* (Brand, Model, Variant, Year) and what it's centrally priced
at (MSP, Margin, Scrap Value). It is the data every Evaluation reads from
but never writes to (BR-0004).

**Responsibilities:** Maintain the Brand/Model/Variant/Year catalog;
maintain MSP/Margin/Scrap Value per catalog entry; enforce that pricing
is Admin-only; expose an Active/Draft/Deprecated lifecycle (SDD-000 §3)
so incomplete or retired catalog entries can't be selected for new
Evaluations (BR-0005).

**Business Goal:** Give the Valuation Engine a reliable, centrally
controlled source of pricing truth, so the Purchase Price calculation
(BR-0001) is only ever as good as this module's data.

**Out of Scope:** Evaluation lifecycle, Repair Component Assessments,
Calculation, Recommendation, Reports, Authentication, Subscription,
Payments — see §2.

**Dependencies:** None upstream (Vehicle Master is a foundational
module per the roadmap — BUS-0002). Downstream: Valuation Engine,
Admin, Reports all read from it.

---

## 2. Module Boundaries

Per SDD-000 §4, with one flagged discrepancy (see Open Questions §17.1).

### Vehicle Master owns

- Brand
- Model
- Variant
- Year (as a dimension of the catalog entry, not the Evaluation's
  selected year — see DD-Vehicle: Vehicle.evaluation copies/references
  this at Evaluation time but does not own it)
- Minimum Selling Price (MSP)
- Margin
- Scrap Value
- Status (Draft / Active / Deprecated — SDD-000 §3)
- Versioning (see §5 — how a pricing change is tracked without mutating
  history other modules already referenced)
- Future Extensions (see §16)

### Vehicle Master does NOT own

- Evaluations (Valuation Engine)
- Calculation (Valuation Engine)
- Reports (Reports module)
- Authentication (Authentication module)
- Subscription (Subscription module)
- Payments (Payments module)

---

## 3. Folder Structure

Architecture only — no files created.

### Proposed Flutter structure

```text
lib/
  modules/
    vehicle_master/
      models/            # VehicleMasterRecord, Brand, Model, Variant (Dart, PascalCase per NS-001 §4)
      repositories/       # API client wrapper for Vehicle Master endpoints
      screens/            # Vehicle Selector, Admin Pricing screens (see §7)
      widgets/            # Dropdown/search components specific to this module
      state/              # State management for catalog selection flow
```

### Proposed Django structure

```text
vehicle_master/            # one Django app per module boundary (CSS-001)
  models.py                 # Brand, Model, Variant, VehicleMasterRecord (snake_case files, PascalCase classes — NS-001 §5)
  serializers.py
  views.py                   # or viewsets.py depending on final API-000 conformance
  permissions.py             # Admin-only write enforcement (BR-0004)
  admin.py                   # Django admin registration for internal Admin use, if applicable
  migrations/
  tests/
```

### Proposed PostgreSQL structure

```text
brand                (id, name, status, created_at, updated_at)
model                (id, brand_id FK, name, status, created_at, updated_at)
variant              (id, model_id FK, name, status, created_at, updated_at)
vehicle_master_record (id, variant_id FK, year, msp, margin, scrap_value,
                        status, version, created_at, updated_at)
```

Table/column names follow NS-001 §6 (`snake_case`, singular table names).
Exact column list is finalized in §5.

---

## 4. Entity Breakdown

| Entity | Responsibility | Relationships | Future Entities |
|---|---|---|---|
| Brand | Manufacturer identity (e.g. Honda) | 1—N Model | — |
| Model | Product line within a Brand (e.g. Activa) | N—1 Brand, 1—N Variant | — |
| Variant | Specific configuration (e.g. Activa 125 Standard) | N—1 Model, 1—N Vehicle Master Record (one per Year) | — |
| Vehicle Master Record | The priced catalog entry: Variant + Year + MSP + Margin + Scrap Value + Status | N—1 Variant, referenced by Vehicle (Valuation Engine, read-only) | Regional Vehicle Master Record (see §16) |

No new entities beyond SDD-000's Entity Catalogue are introduced here —
Brand/Model/Variant are a decomposition of SDD-000's single "Vehicle
Master Record" concept, made explicit because FS-000/SDD-000 described
them as terminology (§1) without giving them entity status individually.
**This decomposition itself is flagged as an open question** (§17.2) —
it is a reasonable inference, not a confirmed decision.

---

## 5. Database Planning

### Tables (see §3 for column sketch)

- `brand`, `model`, `variant`, `vehicle_master_record`.

### Indexes

- `idx_model_brand_id` on `model.brand_id`.
- `idx_variant_model_id` on `variant.model_id`.
- `idx_vehicle_master_record_variant_id_year` on
  `vehicle_master_record(variant_id, year)` — the lookup path the
  Valuation Engine's Vehicle Selector flow uses (SDD-000 §2, §5).

### Constraints

- `vehicle_master_record` unique on `(variant_id, year)` — one pricing
  record per Variant per Year (prevents duplicate catalog entries,
  addresses Error E-CATALOG-001 from SDD-000 §8).
- `vehicle_master_record.status` — enum constraint, values `draft`,
  `active`, `deprecated` (DB/Python `UPPER_SNAKE_CASE` per NS-001 §12;
  shown lowercase here as a Postgres enum label convention — confirm
  against NS-001 before implementation, flagged §17.3).
- Foreign keys `model.brand_id`, `variant.model_id`,
  `vehicle_master_record.variant_id` — `NOT NULL`, `ON DELETE RESTRICT`
  (a Brand/Model/Variant referenced by any pricing record or downstream
  Vehicle should not be deletable outright — deprecate instead, per the
  Status lifecycle).

### Relationships

Brand 1—N Model 1—N Variant 1—N Vehicle Master Record (one per Year).

### Migration Order

1. `brand`
2. `model` (FK → brand)
3. `variant` (FK → model)
4. `vehicle_master_record` (FK → variant)

### Future Migrations

- Repair component cost tables (see §17.1 — ownership unresolved).
- Regional/per-dealer Margin override (see §17 open question #1,
  carried from FS-000 §4.2).
- Versioning/audit table for pricing history (see §16).

---

## 6. API Planning

Inventory only — no implementation. All endpoints follow API-000
conventions (`/api/v1/...`, response envelope, error structure,
pagination, ISO 8601 UTC dates).

| Endpoint | Purpose | Auth | Permission | Consumes | Produces | Errors | Dependencies |
|---|---|---|---|---|---|---|---|
| `GET /api/v1/brands` | List brands for Vehicle Selector | Required | Any authenticated Dealer/Admin | — | Brand list | — | — |
| `GET /api/v1/brands/{id}/models` | List models for a brand | Required | Any authenticated Dealer/Admin | — | Model list | — | Brand must exist |
| `GET /api/v1/models/{id}/variants` | List variants for a model | Required | Any authenticated Dealer/Admin | — | Variant list | — | Model must exist |
| `GET /api/v1/variants/{id}/pricing?year=` | Load MSP/Margin/Scrap Value for a Variant+Year | Required | Any authenticated Dealer/Admin | — | Vehicle Master Record (pricing fields only, not Admin-only edit fields) | E-PRICING-001 (no Active record for that Variant+Year) | Variant must exist, record must be Active (BR-0005) |
| `POST /api/v1/vehicle-master-records` | Create a new catalog entry (Draft) | Required | Admin only (BR-0004) | Variant, Year, MSP, Margin, Scrap Value | Created record | E-CATALOG-001 (duplicate Variant+Year) | Variant must exist |
| `PATCH /api/v1/vehicle-master-records/{id}` | Update pricing or status (e.g. Draft→Active, Active→Deprecated) | Required | Admin only (BR-0004) | Any updatable field | Updated record | E-CATALOG-002 (invalid status transition) | — |
| `GET /api/v1/vehicle-master-records/{id}` | Read a single catalog entry (Admin view, includes pricing) | Required | Admin only | — | Full record | — | — |

Endpoint set intentionally excludes delete — Status transitions (Draft →
Active → Deprecated) are the only lifecycle mutation path, per SDD-000
§3 and this module's Workflow (§10).

---

## 7. UI Planning

### Screen Inventory

- **Vehicle Selector** (Dealer-facing): Year → Brand → Model → Variant
  cascading selection, per FS-000 §2 flow. Read-only pricing display
  after Variant+Year selection succeeds.
- **Admin Pricing** (Admin-facing): CRUD-minus-delete over Brand/Model/
  Variant/Vehicle Master Record, with Status controls.

### Dialogs / Bottom Sheets

- Confirmation dialog on Status transition to `Deprecated` (irreversible
  in effect — existing Evaluations keep referencing it, but it becomes
  unselectable, per SDD-000 §3).
- Bottom sheet for Variant search when the list is long (see Search
  below).

### Search / Filters

- Type-ahead search within Model/Variant dropdowns once catalog size
  makes plain dropdowns impractical (threshold not yet defined — open
  question §17.4).
- Admin Pricing screen: filter by Status (Draft/Active/Deprecated),
  Brand.

### Dropdown Dependencies

Year → Brand → Model → Variant is a cascading-dependent dropdown chain;
each selection filters the next (Brand list may itself be filtered by
Year if year-specific brand availability becomes a rule — not currently
specified, flagged §17.5).

### Theme Support / Dark Mode / Accessibility

- Follows the (not yet created) Design System (`ai/architecture/ds/`) —
  no Vehicle-Master-specific theming; standard light/dark support and
  accessibility (screen-reader labels on dropdowns, minimum tap target
  sizes) expected as a baseline, not a module-specific requirement.

### Navigation

- Vehicle Selector is the entry point into the Evaluation flow (owned by
  Valuation Engine) — Vehicle Master does not own post-selection
  navigation.
- Admin Pricing is reached via an Admin-only navigation section (owned
  by the Admin module's future FS).

---

## 8. Validation Planning

| Layer | Validation |
|---|---|
| Business | A Vehicle Master Record cannot be set `Active` without MSP, Margin, and Scrap Value all populated (extends BR-0005's precondition to the Admin-authoring side). |
| System | Uniqueness of (Variant, Year) enforced before Draft creation succeeds. |
| Database | `NOT NULL` on FK columns; unique constraint on `(variant_id, year)`; enum constraint on `status`. |
| API | Request body validation per API-000 §5 (Validation Error Structure) — e.g. `msp` must be a positive number. |
| UI | Required-field indication on Admin Pricing form; client-side numeric validation as a UX convenience only (never the authority — SEC-001). |

---

## 9. Permissions

| Action | Dealer | Admin | Super Admin | Future Roles |
|---|---|---|---|---|
| Create (Brand/Model/Variant/Record) | No | Yes | Yes | TBD |
| Edit (pricing, status) | No | Yes | Yes | TBD |
| Delete | No | No (no delete endpoint — see §6) | No | TBD |
| Archive (Status → Deprecated) | No | Yes | Yes | TBD |
| View (catalog, pricing for selection) | Yes (read-only, no Admin-only fields) | Yes | Yes | TBD |
| Import (bulk) | No | Deferred to §16 Future Enhancements | Deferred | TBD |
| Export | No | Deferred to §16 Future Enhancements | Deferred | TBD |

"Super Admin" and "Future Roles" are carried from the prompt's requested
table shape — no role distinction between Admin and Super Admin is
defined anywhere in FS-000/SDD-000 yet. Flagged as an open question
(§17.6), not assumed.

---

## 10. Workflow

Vehicle Master lifecycle (Vehicle Master Record), per SDD-000 §3:

```text
Draft → Active → Deprecated
```

- **Creation:** Admin creates a Vehicle Master Record with Variant+Year;
  status starts `Draft`.
- **Activation:** Admin sets MSP, Margin, Scrap Value; status moves to
  `Active` once all three are present (see §8) — only then selectable
  in the Vehicle Selector (BR-0005).
- **Update:** While `Active`, Admin may revise MSP/Margin/Scrap Value in
  place (this is a live pricing table, not an immutable record like
  Calculation Result — BR-0007 applies to Calculation Results, not to
  Vehicle Master pricing; whether pricing *changes* need their own audit
  trail is addressed in §16 Versioning, not yet decided — §17.7).
- **Deprecation:** Admin sets status to `Deprecated`; record becomes
  unselectable for new Evaluations; existing Evaluations that already
  reference it are unaffected (SDD-000 §3).
- **Archival:** No distinct "Archived" state exists in SDD-000's state
  machine for Vehicle Master Record — `Deprecated` is the terminal
  state. If a separate Archival state is wanted, that's a new decision,
  not assumed here (§17.8).

---

## 11. Business Rules Used

Referenced by ID only — full text lives in BRR-001.

- **BR-0004** — MSP, Margin, Scrap Value editable only by Admin.
- **BR-0005** — Evaluation cannot proceed without an Active Vehicle
  Master Record.

BR-0001, BR-0002, BR-0003 (Purchase Price formula, Scrap floor,
Recommendation bands) are Valuation Engine rules that *consume* this
module's data but are not implemented by Vehicle Master — listed here
only to note the dependency.

---

## 12. Error Planning

| Error Code | Type | Condition | Source |
|---|---|---|---|
| E-PRICING-001 | Business | No Active Vehicle Master Record for selected Variant+Year | SDD-000 §8 |
| E-CATALOG-001 | Validation | Duplicate (Variant, Year) on create | SDD-000 §8 |
| E-CATALOG-002 | Business | Invalid status transition (e.g. Deprecated → Active directly) | SDD-000 §8, extended here to cover the Draft→Active precondition in §8 above |
| E-VALIDATION-001 (pattern, per API-000 §5) | Validation | Required pricing field missing/invalid on Admin write | API-000 |
| E-AUTHZ-001 (new — not yet in SDD-000's catalogue) | Authorization | Dealer attempts to write pricing/catalog data | New — flagged §17.9 |

---

## 13. Testing Strategy

Per TEST-001 — what must be tested, no test code:

- **Unit:** uniqueness constraint on (Variant, Year); Draft→Active
  precondition (all three pricing fields present); status-transition
  validity checks.
- **Integration:** Vehicle Selector's cascading Brand→Model→Variant→
  pricing lookup returns E-PRICING-001 correctly when no Active record
  exists (ties to BR-0005/AC-5 in FS-000).
- **Permission tests:** Dealer cannot write to any Admin-only endpoint,
  at the API layer (SEC-001).
- **Traceability:** Each test should reference the Requirement ID or
  BR ID it verifies (TEST-001 naming convention) — e.g.
  `test_br_0005_blocks_evaluation_without_active_record`.

---

## 14. Implementation Order

1. **Database** — migrations for `brand`, `model`, `variant`,
   `vehicle_master_record` in that dependency order (§5).
2. **Backend (Django models + permissions)** — models, Admin-only
   permission enforcement (BR-0004), status-transition validation.
3. **API** — endpoints per §6, following API-000 conventions.
4. **Flutter** — Vehicle Selector (Dealer-facing) first (it's the
   critical path into the Valuation Engine), then Admin Pricing screen.
5. **Testing** — unit/integration tests per §13, written alongside each
   layer above rather than deferred to the end.
6. **Documentation** — `DD-Brand.md`, `DD-Model.md`, `DD-Variant.md`,
   `DD-VehicleMasterRecord.md` (Data Dictionaries, extending the
   DD-Vehicle precedent) produced once schema is finalized in step 1,
   and an `API-001-vehicle-master-endpoints.md` once step 3 is locked.

---

## 15. Acceptance Criteria

IPS-001 is complete when:

- **AC-IPS-1:** Every SDD-000 Module Boundary item assigned to Vehicle
  Master (§2) has a corresponding entity, table, or explicit "future"
  deferral in this document.
- **AC-IPS-2:** Every endpoint in §6 maps to a permission in §9 and an
  error condition in §12.
- **AC-IPS-3:** No business rule is restated — all are BR-000x
  references (§11).
- **AC-IPS-4:** All ambiguities are captured in §17, not resolved by
  assumption.
- **AC-IPS-5:** This document is reviewed and moved to Approved/Locked
  (Constitution Rule 20) before any Vehicle Master implementation prompt
  begins.

---

## 16. Future Enhancements

- Bulk import (CSV upload) for Brand/Model/Variant/pricing data.
- Regional/per-dealer pricing overrides (depends on resolving open
  question #1 below).
- Version history / audit trail for pricing changes (distinct from
  Calculation Result immutability, which is a Valuation Engine concern).
- AI-assisted pricing suggestions (already listed in FS-000 §9).
- Full audit history of Admin edits (ties to LOG-001's Audit level).

---

## 17. Open Questions

Carried forward, unresolved, and not assumed:

1. **(Blocking BR-0001/BR-0004 precision)** Is Margin per-dealer/region-
   configurable, or global? If per-dealer, Vehicle Master's schema (§5)
   needs a Margin-override table, not a single column.
2. Is decomposing "Vehicle Master Record" into separate Brand/Model/
   Variant entities (§4) the correct model, or should FS-000/SDD-000 be
   amended to make this explicit at the SDD level first?
3. Should `status` be stored as a Postgres native enum, a `varchar` with
   a check constraint, or an integer with an application-level enum —
   NS-001 doesn't specify a preferred Postgres enum implementation.
4. At what catalog size does the Vehicle Selector need type-ahead search
   vs. plain dropdowns?
5. Can Brand/Model availability vary by Year (i.e., does the cascading
   dropdown ever need to filter Brand by Year), or is Year independent
   of Brand/Model/Variant existence?
6. Is there a real distinction between "Admin" and "Super Admin" roles
   for this module, or was that carried over from the prompt template
   without a confirmed requirement?
7. Do in-place pricing edits on an Active Vehicle Master Record need
   their own audit/versioning trail (distinct from Calculation Result
   immutability, BR-0007)?
8. Does Vehicle Master need a distinct "Archived" terminal state beyond
   "Deprecated," or is Deprecated sufficient?
9. E-AUTHZ-001 is a new error code not present in SDD-000 §8's Error
   Catalogue — should it be formally added there, or is it Vehicle
   Master-local?

**§17.1 (flagged in §2):** SDD-000 §4's Module Boundaries table assigns
"Repair component cost tables" to Vehicle Master, but this prompt's own
module-boundary framing (owns: Brand/Model/Variant/Year/MSP/Margin/
Scrap Value/Status/Versioning/Future Extensions) omits repair cost
tables entirely and implies they belong elsewhere (the Valuation Engine
owns Repair Component Assessments per SDD-000 §4). **This is an
unresolved conflict between SDD-000 and this prompt's framing** — not
assumed either way. Recommend a BUS/ARC decision before FS/IPS-002
(Valuation Engine) is drafted, since it affects that module's schema
too.

Unchanged from prior sessions, still open:
10. Is Scrap Value independently maintained or derived from MSP?
11. Final recommendation thresholds (currently provisional 90/75/60%).
12. Is offline capability required for v1?
13. Is multi-region/multi-currency support required for v1?
