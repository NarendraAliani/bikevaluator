# FS-001 — Vehicle Master

| Field | Value |
|---|---|
| Document ID | FS-001 |
| Version | 1.0 |
| Status | Approved |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | FS-000, FSS-000, DDD-001, DBD-001, API-001, BRR-001, SDD-000, SSD-001, ABL-001 |
| Next Documents | FS-002 (Valuation Engine) |

**Approved by the Human Architect, 2026-08-02** — closed, no further
revisions ("I consider FS-001 closed. No more revisions."). Its 5 Open
Questions remain as the permanent record of what was flagged during
drafting (per DOC-001 — documents are not rewritten to erase history);
they are carried forward into ISP-001/EP-001 rather than resolved
retroactively here.

First module built against the Baselined architecture (ABL-001) and the
first document required to conform to FSS-000. Per FSS-000's Definition
of Ready, this draft only proceeds because: every `AI-0005` decision
tagged Blocking Module = FS-001 (`ARC-0005`, `ARC-0006`, `ARC-0007`,
`SEC-0001`, `ARC-0010`, `BUS-0006`, `ENG-0003`, `ENG-0001`) is Approved;
DBD-001, API-001, BRR-001, SDD-000, DDD-001, SSD-001 are all Approved;
no FS precedes this one; and the roadmap confirms FS-001 is next. No new
API, schema, business rule, or architectural decision is introduced
here — every genuinely open item found while drafting is recorded in
§Open Questions, not resolved by assumption.

## 1. Purpose

Vehicle Master is the catalog and pricing system of record for
BIKEVALUATOR: it lets a Super Admin maintain the Brand → Model →
Variant hierarchy and the centrally-controlled MSP/Margin/Scrap Value
pricing for each Year+Variant (`ValuationMaster` — "the business's
intellectual property," DDD-001 §3), and lets a Dealer browse that
catalog and load a specific Year+Brand+Model+Variant's pricing
configuration to begin an evaluation. Without this module, neither the
Valuation Engine (FS-002) nor any Admin back-office work has data to
operate on (FS-000, DDD-001 §2 Bounded Contexts).

## 2. Scope

**In scope:**

- Dealer-facing read access to the Brand/Model/Variant catalog and to
  a specific Year+Variant's `ValuationMaster` configuration
  (`/vehicles/brands`, `/vehicles/models`, `/vehicles/variants`,
  `/vehicles/configuration` — API-001).
- Super-Admin-facing CRUD over Brand, Model, Variant, and
  `ValuationMaster` pricing (`/admin/vehicles`, `/admin/vehicles/{id}`,
  `/admin/valuation-master` — API-001), including BR-0007's
  version-on-write pricing history and audit logging of every write.
- Enforcement of BR-0004 (Super-Admin-only pricing/catalog writes) and
  BR-0011 (one Active `ValuationMaster` per Year+Variant) at the API
  boundary.

**Out of scope (owned elsewhere):**

- **Repair Component / Repair Option administration** (`/admin/
  repair-components`) — per SSD-001 §10's traceability, §3.8 (Repair
  Master Administration) maps only to **FS-004**, not FS-001. DDD-001
  §2 and DBD-001's "Repair Module" section both independently confirm
  Vehicle Master and Repair Master are deliberately separate bounded
  contexts. **Note:** SDD-000 §4's Module Boundaries table still reads
  "Vehicle Master... owns... Repair component cost tables," which
  contradicts the three later, more specific documents above — this
  drift is not resolved here (see Open Questions); FS-001 follows
  DDD-001/DBD-001/SSD-001 as the more specific and more recent sources.
  `/vehicles/configuration`'s response does surface repair options
  read-only (see §11) — that is Vehicle Master *consuming* Repair
  Master data for a Dealer-facing response, not administering it.
- **Evaluation lifecycle, Repair Assessment, Calculation, Recommendation**
  — SDD-000 §4, FS-002 (Valuation Engine). Vehicle Master only supplies
  pricing inputs; it never computes a Purchase Price.
- **Authentication, JWT issuance/validation, role assignment** — FS-003.
  This document assumes an authenticated request carrying a valid
  `users.role` (`SEC-0001`) arrives at the API boundary; it does not
  specify login itself.
- **Subscription tier logic and its effect on catalog visibility** —
  FS-005 owns Subscription state; see Open Questions for an unresolved
  interaction between Free-tier "limited vehicle DB" (SSD-001 §3.5) and
  this module's catalog endpoints.
- **Admin back-office shell/navigation** — SSD-001 §10 lists both FS-001
  and **FS-004** for §3.7 (Vehicle Master Administration). This document
  takes the position that FS-001 specifies the Vehicle-Master-owned
  admin *operations* (validation, permissions, audit, concurrency) since
  they operate on this module's own tables and rules, while FS-004 owns
  the shared admin UI shell that surfaces them alongside other modules'
  admin capabilities (see §23 Cross-FS Dependencies).

## 3. Actors

Per SSD-001 §2 (restated, not redefined):

| Actor | Role in this module |
|---|---|
| **Dealer** | Browses catalog, loads a Configuration to begin a vehicle pricing attempt (feeds FS-002). Read-only here — cannot write catalog or pricing (BR-0004). |
| **Super Admin** | Creates/edits Brand, Model, Variant, and `ValuationMaster` pricing. Sole writer (BR-0004). |
| **Flutter Client** | Mediates both Dealer and Admin actions; computes no business rules itself (ADR-005, ADR-014). |
| **Vehicle Master (service)** | Owns Brand/Model/Variant/`ValuationMaster`; source of Configuration Load responses (SSD-001 §2). |
| **Audit Service** | Records every Vehicle Master admin write (SSD-001 §3.7). |

## 4. Preconditions

- Requesting user is authenticated (valid JWT) — FS-003 scope, assumed
  here.
- For Admin operations: `users.role = super_admin` (`SEC-0001`); enforced
  server-side, never trusted from client display (SDD-000 §7 Security
  NFR, `E-AUTHZ-001`).
- For Dealer catalog browsing: any authenticated Dealer may read
  (SSD-001 §6 Failure Scenarios: "N/A (read-only, any authenticated
  Dealer)") — subject to the unresolved Free-tier visibility question
  in Open Questions.

## 5. User Stories

- As a **Dealer**, I want to select Year → Brand → Model → Variant with
  type-ahead search (`ENG-0001`), so that I can quickly find the exact
  vehicle I'm pricing without scrolling a long list.
- As a **Dealer**, I want to load a specific Variant+Year's pricing
  configuration, so that I can proceed to a Repair Assessment (FS-002)
  with the correct MSP/Margin/Scrap Value already resolved.
- As a **Super Admin**, I want to create and edit Brand/Model/Variant
  catalog entries, so that new vehicles can be priced as they come to
  market.
- As a **Super Admin**, I want to set and later revise a Year+Variant's
  MSP/Margin/Scrap Value without losing the prior pricing's history, so
  that past evaluations remain explainable (BR-0007).
- As a **Super Admin**, I want every catalog/pricing change audit-logged,
  so that any dispute about "who changed this price and when" is
  answerable.
- As a **Dealer or Super Admin**, I want a Dealer-role account to be
  rejected if it attempts an Admin write, so that pricing integrity
  can't be bypassed by a compromised or misconfigured client
  (`E-AUTHZ-001`).

## 6. Functional Requirements

| ID | Requirement | Traces to User Story |
|---|---|---|
| FR-001-001 | System shall list all active Brands via `GET /vehicles/brands`. | US-1 |
| FR-001-002 | System shall list all active Models for a given Brand via `GET /vehicles/models?brand_id=`. | US-1 |
| FR-001-003 | System shall list all active Variants for a given Model via `GET /vehicles/variants?model_id=`. | US-1 |
| FR-001-004 | System shall return the Active `ValuationMaster` (MSP, Margin, Scrap Value) plus available repair options for a given Year+Brand+Model+Variant via `GET /vehicles/configuration`. | US-2 |
| FR-001-005 | If no Active `ValuationMaster` exists for the requested Year+Variant, system shall return `VAL003`/`E-PRICING-001` and must not return a partial/default configuration (BR-0005). | US-2 |
| FR-001-006 | System shall allow a Super Admin to create or update a Brand, Model, or Variant via `/admin/vehicles`. | US-3 |
| FR-001-007 | System shall reject a duplicate Brand/Model/Variant/Year combination at write time (`E-CATALOG-001`). | US-3 |
| FR-001-008 | System shall allow a Super Admin to create a new `ValuationMaster` pricing version via `/admin/valuation-master`, closing the prior row's `effective_to` and inserting a new row rather than overwriting (BR-0007). | US-4 |
| FR-001-009 | System shall enforce exactly one Active `ValuationMaster` row per Year+Variant at any time (BR-0011), rejecting a write that would violate it. | US-4 |
| FR-001-010 | System shall reject any Admin write (`/admin/vehicles`, `/admin/valuation-master`) from a non-`super_admin` account with `E-AUTHZ-001`/403, checked server-side. | US-6 |
| FR-001-011 | System shall write an `audit_logs` entry (who, when, old value, new value) for every Brand/Model/Variant/`ValuationMaster` write, in the same transaction as the write itself for `ValuationMaster` (`ENG-0003`, DBD-001 §6a). | US-5 |
| FR-001-012 | System shall reject a `ValuationMaster`/`RepairOption`-style concurrent write to a stale row with `409 Conflict` when the submitted `updated_at` does not match the current row (`ENG-0003`) — for `ValuationMaster` specifically; see Open Questions for Brand/Model/Variant, which have no `updated_at` column today. | US-4 |
| FR-001-013 | System shall never apply Year-based filtering to `/vehicles/brands`, `/vehicles/models`, or `/vehicles/variants` (`ARC-0005`) — `year` is accepted only by `/vehicles/configuration`. | US-1 |

## 7. Business Rules

This module implements: **BR-0004, BR-0005, BR-0007, BR-0011**. Rule
text is not restated here — see BRR-001 v1.2 for the authoritative
definitions. Where each is applied is cited in §6 (Functional
Requirements), §14 (Error Handling), and §15 (Permissions).

## 8. Validation Rules

Field-level input constraints (distinct from §7's cross-field business
rules):

- `brand_name` / `model_name` / `variant_name`: required, non-empty
  string. Maximum length is not documented anywhere in NS-001/CSS-001/
  DBD-001 — see Open Questions.
- `year`: required, positive integer. No documented valid range (e.g.
  earliest supported manufacture year, or a cap relative to the current
  year) — see Open Questions.
- `minimum_selling_price`, `margin`, `scrap_value`: required, numeric,
  **non-negative** — a negative price has no business meaning, though
  no document states this constraint explicitly; treated as an
  implied, not invented, validation rule (not a numbered `BR-000x`,
  per FSS-000 §1's Validation Rules vs. Business Rules distinction).
- `ValuationMaster` write: `effective_from` must not be after
  `effective_to` when both are present (BR-0007's ordering, made
  explicit as a field check).

## 9. UI Requirements

Behavioral only — no visual design (Design System territory, per
FSS-000 §1 item 9):

- **Dealer — Vehicle Selector screen:** four sequential type-ahead
  selection fields (Year, Brand, Model, Variant), always type-ahead
  regardless of list length (`ENG-0001` — no plain-dropdown fallback).
  Selecting a Variant triggers Configuration Load; a missing-pricing
  result (`VAL003`) must be shown as a distinct "pricing not available"
  state, not a generic error (SDD-000 §8).
- **Super Admin — Vehicle Master management screens:** a Brand/Model/
  Variant list-and-edit screen and a `ValuationMaster` pricing
  list-and-edit screen (showing current Active row plus its
  version history per BR-0007). A `409 Conflict` on save must prompt
  the Admin to reload the record rather than silently retry
  (DBD-001 §6a).

## 10. Navigation

- **Dealer entry point:** Dealer dashboard → "New Evaluation" → Vehicle
  Selector screen (this module) → on successful Configuration Load,
  proceeds to Repair Assessment screen (FS-002 — out of this module's
  scope beyond the handoff).
- **Super Admin entry point:** Admin dashboard (FS-004 shell) → Vehicle
  Master section → Brand/Model/Variant list or `ValuationMaster`
  pricing list. Exit: back to Admin dashboard.

## 11. API Mapping

Cited from API-001 v1.1 by path only — no new endpoint introduced:

| Endpoint | Method | Used For |
|---|---|---|
| `/vehicles/brands` | GET | FR-001-001 |
| `/vehicles/models?brand_id=` | GET | FR-001-002 |
| `/vehicles/variants?model_id=` | GET | FR-001-003 |
| `/vehicles/configuration?year=&brand=&model=&variant=` | GET | FR-001-004, FR-001-005. Response includes MSP, Margin, Scrap Value, and available repair options (API-001) — the repair-options portion is read-only pass-through from the separate Repair Master context (DDD-001 §2), not administered here. |
| `/admin/vehicles` | GET/POST | FR-001-006, FR-001-007, FR-001-010 |
| `/admin/vehicles/{id}` | PUT/DELETE | FR-001-006 (update/deactivate) |
| `/admin/valuation-master` | CRUD | FR-001-008, FR-001-009, FR-001-010, FR-001-012 |

Envelope: `{success, message, data}` / `{success, message, errors}`
(API-000 v1.1, `ARC-0007`) — not restated here.

## 12. Database Mapping

Cited from DBD-001 v1.1 by table/column only — no new schema
introduced:

| Table | Used For |
|---|---|
| `brands` (id, brand_name, active) | FR-001-001, FR-001-006, FR-001-007 |
| `models` (id, brand_id, model_name, active) | FR-001-002, FR-001-006, FR-001-007 |
| `variants` (id, model_id, variant_name, active) | FR-001-003, FR-001-006, FR-001-007 |
| `valuation_master` (id, year, variant_id, minimum_selling_price, margin, scrap_value, active, effective_from, effective_to, updated_at) | FR-001-004, FR-001-005, FR-001-008, FR-001-009, FR-001-012 |
| `audit_logs` (who, when, old_value, new_value, ip_address) | FR-001-011 |
| `users` (`role` column, read-only from this module) | FR-001-010 |

## 13. Sequence Flow

No new diagram — this module conforms exactly to two existing SSD-001
diagrams:

- **SSD-001 §3.2 — Vehicle Selection:** Dealer-facing Year→Brand→Model→
  Variant→Configuration Load, including the `VAL003`/BR-0005 failure
  branch.
- **SSD-001 §3.7 — Vehicle Master Administration:** Super-Admin-facing
  Brand/Model/Variant creation and `ValuationMaster` versioning, with
  the authorization check and Audit Service call.

## 14. Error Handling

| Error | Source | Behavior |
|---|---|---|
| `VAL001` (Vehicle Not Found) | API-001 | Invalid brand/model/variant id in a catalog GET → 404. |
| `VAL002` (Variant Missing) | API-001 | Referenced variant id doesn't resolve → 404. |
| `VAL003` / `E-PRICING-001` | API-001 / SDD-000 §8 | No Active `ValuationMaster` for the requested Year+Variant → block, "pricing not available" (BR-0005). |
| `E-CATALOG-001` | SDD-000 §8 | Duplicate Brand/Model/Variant/Year at write time → reject, 409/422, surfaced to Admin UI. Also the enforcement mechanism for **BR-0011**. |
| `E-CATALOG-002` | SDD-000 §8 | Selected Variant is Deprecated (`active=false`) → block selection for new evaluations; existing evaluations unaffected (out of this module's runtime scope, but the flag it reads is owned here). |
| `E-AUTHZ-001` | SDD-000 §8 | Dealer-role account attempts an Admin write → 403, logged (LOG-001 Audit level). |
| `409 Conflict` | DBD-001 §6a | Stale `updated_at` on a `ValuationMaster` write → Admin must reload before retrying. |

## 15. Permissions

Per **BR-0004**: MSP, Margin, and Scrap Value — and the Brand/Model/
Variant catalog itself — are editable only by `super_admin`, never by
`dealer`. Enforced server-side via the `users.role` column (`SEC-0001`)
at the API boundary for every `/admin/vehicles` and `/admin/
valuation-master` call, using **`E-AUTHZ-001`** (SDD-000 §8) as the
rejection response — never inferred from client-side role display
(SDD-000 §7 Security NFR). Dealer access to `/vehicles/*` is read-only
and requires no additional permission beyond authentication.

## 16. Audit Logging

Every write to `brands`, `models`, `variants`, or `valuation_master`
produces an `audit_logs` entry capturing who (Super Admin id), when,
old value, new value, and ip_address (DBD-001 §2 Audit Logs). For
`valuation_master` specifically, the write and its audit entry occur in
**one database transaction** (`ENG-0003`, DBD-001 §6a) — never as two
separate writes that could diverge. Whether the same one-transaction
guarantee is required for Brand/Model/Variant writes is not specified
in DBD-001 §6a (which names only `valuation_master`/`repair_options`)
— see Open Questions.

## 17. Performance Expectations

Specializes SDD-000 §7's NFR ("Vehicle selection and calculation must
complete within an interactive response budget — target: sub-second for
catalog lookups") for this module specifically: `/vehicles/brands`,
`/vehicles/models`, `/vehicles/variants`, and `/vehicles/configuration`
should each target sub-second response, consistent with the type-ahead
UX (`ENG-0001`) that depends on fast per-keystroke lookups. Exact SLOs
remain deferred to a future PEP document, per SDD-000 §7 — not
introduced here.

## 18. Security Considerations

- Authorization enforced server-side, never via client-side role
  display (SDD-000 §7, `E-AUTHZ-001`) — see §15.
- All Admin pricing/catalog edits audit-logged (SDD-000 §7 Security
  NFR) — see §16.
- SEC-001 (Security Standards) is currently `Needs Review` (AFR-001's
  Standards Approval Matrix, not part of the `AI-0005` batch resolved
  by ABL-001) — this FS does not depend on any SEC-001 content beyond
  what's already cited from SDD-000/DBD-001 above; flagged so its
  eventual approval/revision is checked against this document later.

## 19. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-001-001 | Given active Brands exist, when a Dealer calls `GET /vehicles/brands`, then only Brands with `active=true` are returned. |
| AC-001-002 | Given an Active `ValuationMaster` exists for Year=2022, Variant=X, when a Dealer calls `/vehicles/configuration` with that Year+Variant, then the response includes MSP, Margin, Scrap Value, and the Variant's available repair options, with HTTP 200. |
| AC-001-003 | Given no Active `ValuationMaster` exists for a requested Year+Variant, when a Dealer calls `/vehicles/configuration`, then the response is `VAL003`/`E-PRICING-001` and contains no partial pricing data. |
| AC-001-004 | Given a Super Admin submits a new `ValuationMaster` row for a Year+Variant that already has an Active row, when the write is processed, then the prior row's `effective_to` is closed, the new row is inserted as Active, and both changes occur atomically with one `audit_logs` entry. |
| AC-001-005 | Given a Super Admin attempts to create a second Active `ValuationMaster` for the same Year+Variant without closing the first (a direct BR-0011 violation), when the write is processed, then it is rejected with `E-CATALOG-001`. |
| AC-001-006 | Given a Dealer-role account calls any `/admin/vehicles` or `/admin/valuation-master` endpoint, when the request is processed, then it is rejected with `E-AUTHZ-001`/403 regardless of any client-side UI state. |
| AC-001-007 | Given a Super Admin submits a `ValuationMaster` update with a stale `updated_at`, when the write is processed, then it is rejected with `409 Conflict` and no partial write occurs. |
| AC-001-008 | Given `/vehicles/brands`, `/vehicles/models`, or `/vehicles/variants` is called with any `year` parameter, then the parameter has no filtering effect (`ARC-0005`) — the full active list for that level is always returned. |

## 20. Edge Cases

Cross-checked against SSD-001 §6's Failure Scenarios matrix for
Vehicle Selection and Vehicle Master Administration:

- Catalog is empty (no Brands yet created) — Dealer sees an empty list,
  not an error; no document specifies distinct empty-state handling
  beyond this (reasonable default, not a new business rule).
- A Variant is deactivated (`active=false`) between a Dealer loading
  the Variant list and submitting a Configuration request for it — a
  read/write race SSD-001 §6 marks "read-only, no conflict" for the
  read side; the Configuration call itself should then hit
  `E-CATALOG-002` if the variant lookup checks `active`, or `VAL003` if
  it instead falls through to the pricing lookup — **which of the two
  fires is not specified**; see Open Questions.
- Two Super Admins editing the same `ValuationMaster` row concurrently
  — `409 Conflict` per `ENG-0003` (AC-001-007).
- Super Admin deactivates a Brand/Model/Variant that has an Active
  `ValuationMaster` referencing it — no document specifies whether this
  should cascade-deprecate the `ValuationMaster` row or leave it
  orphaned-but-inactive-catalog; see Open Questions.
- Dealer on a Free-tier Subscription browsing the catalog — SSD-001
  §3.5 says Free tier gets "Access granted (limited vehicle DB)," but
  no document specifies what "limited" means at the API/data level for
  this module's endpoints; see Open Questions.

## 21. Future Enhancements

- Year-based catalog filtering, if a real dead-end-selection problem
  emerges (`ARC-0005`'s decision was for v1 only; revisit if usage data
  warrants it).
- Per-dealer/region Margin override — explicitly rejected for v1
  (DDD-001 §3 `ValuationMaster`, BDR-0002), noted here only as a
  documented future possibility, not a current plan.
- Admin-configurable recommendation thresholds — explicitly rejected in
  favor of a fixed constant for v1 (`BUS-0005`); would touch this
  module only insofar as it might one day need its own settings screen.

## 22. Architecture Compliance Checklist

| Field | Content |
|---|---|
| Architecture documents referenced | DDD-001 §2, §3 (Brand, Model, Variant, ValuationMaster); DBD-001 v1.1 §2 (Vehicle Master, Valuation Master), §5, §6, §6a; API-001 v1.1 (Vehicle Master, Admin sections); BRR-001 v1.2 (BR-0004, BR-0005, BR-0007, BR-0011); SDD-000 v1.1 §4, §7, §8; SSD-001 v1.1 §3.2, §3.7, §6, §10; ABL-001; FSS-000. |
| Decision IDs implemented | `SEC-0001` (role column, §15), `ENG-0003` (transaction/concurrency, §12/§16), `ARC-0005` (no Year filtering, FR-001-013/AC-001-008), `ARC-0006` (`E-AUTHZ-001`, §14/§15), `ARC-0010` (Brand aggregate root — code-organization only, no FS-001 content changes), `BUS-0006`/`BR-0011` (§7/§9), `ARC-0008` (Vehicle ephemeral — confirms no vehicle-instance table is this module's concern). |
| Business Rule IDs referenced | BR-0004, BR-0005, BR-0007, BR-0011. |
| APIs used | `/vehicles/brands`, `/vehicles/models`, `/vehicles/variants`, `/vehicles/configuration`, `/admin/vehicles`, `/admin/vehicles/{id}`, `/admin/valuation-master`. |
| Database tables used | `brands`, `models`, `variants`, `valuation_master`, `audit_logs`, `users` (read-only). |
| Deviations | None introduced by this FS. One pre-existing documentation inconsistency was found, not introduced: SDD-000 §4's Module Boundaries table still reads "Vehicle Master owns... Repair component cost tables," which contradicts DDD-001 §2, DBD-001's Repair Module section, and SSD-001 §10 (all three treat Repair Master as a separate context/FS-004 concern). This FS follows the three more specific, more recent sources; SDD-000 §4 itself was not edited (out of this FS's scope) — see Open Questions. |
| New architectural questions | See §Open Questions below — five items, none resolved by assumption. |

## 23. Cross-FS Dependencies

| Depends On (must be Approved first) | Provides To (future FS depending on this one) |
|---|---|
| None — FS-001 is first in sequence. | **FS-002 (Valuation Engine):** reads `ValuationMaster` MSP/Margin/Scrap Value via Vehicle Master (SSD-001 §3.4); BR-0005's gate depends on this module's Active-record state. |
| | **FS-004 (Admin):** the shared admin UI shell surfaces this module's `/admin/vehicles`/`/admin/valuation-master` operations (SSD-001 §10 lists both FS-001 and FS-004 for §3.7 — this document owns the operations themselves; FS-004 owns the shell they're presented through). |

## Open Questions

Genuinely undefined — not invented, not silently resolved:

1. **SDD-000 §4 vs. DDD-001/DBD-001/SSD-001 on Repair Master ownership** —
   SDD-000 §4 still lists Repair component cost tables under Vehicle
   Master's ownership, while three later, more specific documents treat
   Repair Master as a separate context whose administration belongs to
   FS-004. Recommend a future SDD-000 revision (a new decision) to
   correct §4's wording; not resolved inline here.
2. **Free-tier catalog visibility** — SSD-001 §3.5 states Free-tier
   Dealers get "Access granted (limited vehicle DB)" but no document
   defines what is limited (fewer Brands? fewer Models? a cap on
   Variants?) or how `/vehicles/*` endpoints would express that limit.
3. **Field length / Year range validation** — no document specifies a
   maximum length for `brand_name`/`model_name`/`variant_name`, nor a
   valid range for `year`.
4. **Cascade behavior on catalog deactivation** — deactivating a Brand/
   Model/Variant that has an Active `ValuationMaster` referencing it:
   should the `ValuationMaster` row be cascade-deprecated, or left
   orphaned-but-inactive-catalog? Not specified anywhere.
5. **Concurrency policy scope** — `ENG-0003`/DBD-001 §6a's optimistic-
   concurrency policy explicitly names `valuation_master`/
   `repair_options` only. Brand/Model/Variant tables have no `updated_at`
   column today, so the same policy cannot apply to them as currently
   schema'd — is last-write-wins acceptable for catalog-only edits, or
   should `updated_at` be added there too? Not specified; no schema
   change made here pending that answer.
