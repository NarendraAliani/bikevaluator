# EP-001 — Vehicle Master Engineering Package

| Field | Value |
|---|---|
| Document ID | EP-001 |
| Version | 1.0 |
| Status | Draft |
| Owner | Architecture AI |
| Reviewer | Human (architect), reviewed as CTO from this document onward |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | FS-001 (Approved), ISP-001, DDD-001, DBD-001, API-001, SSD-001, BRR-001, NS-001, CSS-001, DOC-001, TEST-001, LOG-001, SEC-001, ABL-001 |
| Next Documents | Production code (Vehicle Master), EP-002 (Valuation Engine) |

**Location note:** per this prompt's explicit instruction, this
document lives at `engineering/packages/EP-001-vehicle-master.md` — a
new top-level folder, not under `ai/architecture/**` like every
document so far. This establishes a new repository convention not yet
recorded in NS-001 §1 (Repository/Folder Naming); not corrected there,
per this prompt's "do not modify approved documents" constraint —
flagged as a recommended future NS-001 addition instead.

**Pipeline note:** Constitution Rule 24 (added under ISP-001)
established Architecture → FS → ISP → Code → Testing. This prompt
introduces an Engineering Package (EP) stage that overlaps substantially
with ISP-001's content but goes one level more concrete (actual folder
structure, migration sequence, file inventory) and — notably — this
prompt's own "Read First" list does not include ISP-001. Rather than
silently treat EP-001 as a from-scratch replacement (risking
contradicting the interfaces ISP-001 already defined) or silently
ignore the gap, this document explicitly builds on ISP-001's contracts
(§2–§7 below cite ISP-001 throughout) and treats EP as the concrete
"how the folders/files are organized" layer between ISP and code. See
§Open Questions and the Prompt Execution Report for the recommended
Constitution amendment (Rule 25) clarifying the pipeline as
**Architecture → FS → ISP → EP → Code → Testing**.

Per this prompt's explicit constraints: no architecture was
reinterpreted, no business rule was invented, no approved document was
modified (beyond FS-001's Status field, per the architect's explicit
"I consider FS-001 closed" instruction), and no production code is
included below.

---

## 1. Module Summary

**Purpose:** Vehicle Master is the catalog and pricing system of
record — Brand→Model→Variant hierarchy plus `ValuationMaster`
(MSP/Margin/Scrap Value) — that every Dealer evaluation and every
Admin pricing operation depends on (FS-001 §1).

**Dependencies:**

- **`users.role`** (`SEC-0001`, DBD-001) — Vehicle Master's Admin
  authorization checks require this column to exist. It is owned by
  Authentication (FS-003), not this module. **This is a real
  cross-module sequencing dependency, not just a documentation
  reference:** if FS-003's `users` table/migration isn't in place, this
  module's `E-AUTHZ-001` checks have nothing to check against. Flagged
  prominently, not buried — see §9 Development Order.
- **`audit_logs`** (DBD-001 §2) — shared across all Admin-owned
  modules, not Vehicle-Master-specific; treated as an external/shared
  dependency (see §2 Folder Structure).
- Authenticated request context (valid JWT) — FS-003 scope, assumed
  present at the API boundary.

**Inputs:** Super Admin catalog/pricing writes; Dealer catalog
read/Configuration-Load requests.

**Outputs:** Brand/Model/Variant lists; a resolved `ValuationMaster`
configuration (MSP/Margin/Scrap Value + read-only repair options) for
FS-002 (Valuation Engine) to consume; `audit_logs` entries for every
Admin write.

**External Services:** None beyond BIKEVALUATOR's own Repair Master
context (read-only, for the Configuration response's repair-options
pass-through — FS-001 §2/§11) and Authentication (for `users.role`).
No third-party/external API integration in this module (contrast
Payments/FS-006, which does).

---

## 2. Backend Package

### Folder Structure (Django, `src/` root per Constitution Rule 12)

One app per module boundary (CSS-001): `vehicle_master`.

```
src/
  vehicle_master/
    __init__.py
    apps.py
    models/
      __init__.py
      brand.py
      model.py
      variant.py
      valuation_master.py
    migrations/
      __init__.py
      0001_create_brands.py
      0002_create_models.py
      0003_create_variants.py
      0004_create_valuation_master.py
    repositories/
      __init__.py
      brand_repository.py
      model_repository.py
      variant_repository.py
      valuation_master_repository.py
    services/
      __init__.py
      vehicle_catalog_service.py
      vehicle_master_admin_service.py
    serializers/
      __init__.py
      catalog_serializers.py
      configuration_serializer.py
      admin_catalog_serializers.py
      valuation_master_serializers.py
    views/
      __init__.py
      catalog_views.py
      admin_vehicle_views.py
      admin_valuation_master_views.py
    permissions.py
    exceptions.py
    validators.py
    urls.py
    tests/
      __init__.py
      test_brand_repository.py
      test_model_repository.py
      test_variant_repository.py
      test_valuation_master_repository.py
      test_vehicle_catalog_service.py
      test_vehicle_master_admin_service.py
      test_catalog_views.py
      test_admin_vehicle_views.py
      test_admin_valuation_master_views.py
      fixtures.py
  common/
    audit/
      __init__.py
      models.py
      repositories.py
```

`common/audit/` is **not** part of the `vehicle_master` app —
`audit_logs` is shared across every Admin-owned module (DBD-001 §2);
placing it in a shared `common` app avoids `vehicle_master` owning a
table it doesn't conceptually own. `vehicle_master`'s services depend
on `common.audit.repositories.AuditLogRepository` as an external
collaborator (§4 Service Layer).

### Module Layout

Layering follows ISP-001 §3/§4 exactly: `views` (HTTP concern only) →
`services` (business logic, transaction boundaries, BR enforcement) →
`repositories` (persistence only) → `models` (Django ORM). Serializers
sit alongside views, translating between DTOs (ISP-001 §2) and service
inputs/outputs. No layer is skipped (e.g. a view must never call a
repository directly).

### Repository Interfaces

As defined in ISP-001 §3 (`BrandRepository`, `ModelRepository`,
`VariantRepository`, `ValuationMasterRepository`) — not redefined here;
`repositories/*.py` above are their concrete Django-ORM
implementations, one file per interface, per CSS-001's file-per-concern
convention.

### Service Interfaces

As defined in ISP-001 §4 (`VehicleCatalogService`,
`VehicleMasterAdminService`) — not redefined here; `services/*.py`
implement them.

### Validation Layer

`validators.py` implements ISP-001 §6's Validation Matrix as reusable
Django/DRF validator functions (`validate_catalog_name`,
`validate_year_range`, `validate_non_negative_amount`) — called from
serializers (API-boundary validation, per SEC-001 "all validation
happens at the API boundary") and reused by services where a
cross-field check (e.g. `effective_from` ≤ `effective_to`) can't be
expressed in a single-field serializer validator.

### Serializer Plan

One serializer module per resource family, each with a Request and a
Response serializer class (mirroring ISP-001 §2's DTOs 1:1):
`catalog_serializers.py` (Brand/Model/Variant read), `configuration_
serializer.py` (Configuration response, including the read-only
`RepairOptionGroupDto` pass-through), `admin_catalog_serializers.py`
(`CreateVehicleCatalogEntryRequest`/`UpdateVehicleCatalogEntryRequest`/
`AdminVehicleCatalogEntryDto`), `valuation_master_serializers.py`
(`CreateValuationMasterVersionRequest`/`ValuationMasterDto`).

### Exception Strategy

`exceptions.py` defines one exception class per error code this module
raises (`VehicleNotFoundError` → `VAL001`, `VariantMissingError` →
`VAL002`, `PricingNotAvailableError` → `VAL003`/`E-PRICING-001`,
`DuplicateCatalogEntryError` → `E-CATALOG-001`, `DeprecatedVariantError`
→ `E-CATALOG-002`, `NotAuthorizedError` → `E-AUTHZ-001`,
`ConcurrencyConflictError` → `409`). A single DRF exception handler
(shared across all BIKEVALUATOR modules, likely `common/exceptions.py`
— out of this module's own inventory, flagged as a cross-cutting
dependency) maps each to the API-000 v1.1 error envelope. See §7 Error
Package for the full per-layer mapping.

### Transaction Boundaries

Per `ENG-0003`/DBD-001 §6a: `VehicleMasterAdminService.
create_valuation_master_version(...)` wraps the repository's version
write and the `AuditLogRepository` write in **one**
`transaction.atomic()` block. Brand/Model/Variant writes: each
individual create/update/deactivate call is its own atomic operation
paired with its audit write (no cross-entity transaction needed, since
Brand/Model/Variant edits are independent of each other).

---

## 3. Database Package

### Migration Sequence

1. `0001_create_brands` — `brands` table (DBD-001 §2).
2. `0002_create_models` — `models` table, FK → `brands`.
3. `0003_create_variants` — `variants` table, FK → `models`.
4. `0004_create_valuation_master` — `valuation_master` table, FK →
   `variants`, including `updated_at`.
5. **Prerequisite, not part of this module's own migrations:**
   `common/audit` app's `audit_logs` table migration must exist before
   any Admin write path is exercised. **Prerequisite, cross-module:**
   Authentication's `users.role` column migration (`SEC-0001`) must
   exist before `E-AUTHZ-001` checks are meaningful — see §1
   Dependencies.

### Indexes

Per DBD-001 §7 (Brand, Model, Variant, Year already named there):

| Table | Index |
|---|---|
| `brands` | `brand_name` (lookup/uniqueness support) |
| `models` | `brand_id`; `(brand_id, model_name)` |
| `variants` | `model_id`; `(model_id, variant_name)` |
| `valuation_master` | `(year, variant_id)` — see Constraints below for the partial-unique form; `active` (fast "get current Active row" lookups) |

### Constraints

- FK: `models.brand_id → brands.id`, `variants.model_id → models.id`,
  `valuation_master.variant_id → variants.id`.
- `NOT NULL` on all required fields per ISP-001 §6.
- `CHECK (minimum_selling_price >= 0)`, `CHECK (margin >= 0)`,
  `CHECK (scrap_value >= 0)` on `valuation_master` — a DB-layer
  backstop for ISP-001 §6's validation rules, consistent with SEC-001's
  input-validation guidance being about the API boundary as the
  *authority*, not the *only* place a constraint may exist.
- **`BR-0011` implementation detail** (not a new rule — a precise
  reading of the existing one): "exactly one Active `ValuationMaster`
  per Year+Variant" must be a **partial unique index**:
  `UNIQUE (year, variant_id) WHERE active = true` — a plain unique
  constraint on `(year, variant_id)` would incorrectly block BR-0007's
  superseded/historical rows, which legitimately share the same
  Year+Variant while `active = false`.

### Foreign Keys

Listed above under Constraints; all `ON DELETE RESTRICT` (soft-delete
convention, DBD-001 §5 — no hard deletes anywhere in this schema, so no
FK should cascade a hard delete).

### Versioning Strategy

BR-0007, unchanged from DBD-001 §6/ISP-001 §3: a pricing edit closes
the current Active row's `effective_to` and inserts a new row, in one
transaction with its audit entry (`ENG-0003`).

### Optimistic Locking Implementation

`valuation_master.updated_at` is the concurrency token
(`ENG-0003`/DBD-001 §6a): the write is a conditional `UPDATE ... WHERE
id = :id AND updated_at = :expected_updated_at` to close the prior row;
zero rows affected ⇒ `ConcurrencyConflictError` → `409`. **Not
implemented for Brand/Model/Variant** — they have no `updated_at`
column (ISP-001 Open Question #5, still unresolved; carried forward,
not resolved here).

---

## 4. Flutter Package

**Open dependency, carried from ISP-001 Open Question #6, still
unresolved:** no architecture document specifies BIKEVALUATOR's
state-management library (BLoC, Provider, Riverpod). The structure
below is written to work under any of them; the `controllers/` folder
name and per-screen controller classes are placeholders pending that
decision.

### Feature Folder Layout

Feature-first, mirroring module boundaries (CSS-001) — proposed
convention, since no Flutter folder-structure standard exists yet in
NS-001/CSS-001 beyond "mirrors module boundaries":

```
lib/
  features/
    vehicle_master/
      data/
        models/
          brand_dto.dart
          model_dto.dart
          variant_dto.dart
          configuration_dto.dart
          repair_option_group_dto.dart
          admin_vehicle_catalog_entry_dto.dart
          valuation_master_dto.dart
        datasources/
          vehicle_master_remote_data_source.dart
      presentation/
        screens/
          vehicle_selector_screen.dart
          admin_vehicle_catalog_screen.dart
          admin_valuation_master_screen.dart
        widgets/
          type_ahead_vehicle_selector_field.dart
          valuation_master_form.dart
          concurrency_conflict_dialog.dart
        controllers/
          vehicle_selector_controller.dart
          admin_vehicle_catalog_controller.dart
          admin_valuation_master_controller.dart
      vehicle_master_routes.dart
```

### Screens

Per ISP-001 §5 — `VehicleSelectorScreen`, `AdminVehicleCatalogScreen`,
`AdminValuationMasterScreen` — not redefined here.

### Navigation

Per FS-001 §10: Dealer dashboard → Vehicle Selector → (hands off to
FS-002's Repair Assessment screen, outside this module). Admin
dashboard (FS-004 shell) → Admin Vehicle Catalog / Admin ValuationMaster
screens. `vehicle_master_routes.dart` registers all three routes with
the app's central router (owned outside this module's inventory).

### State Management

See the Open dependency note above. Whichever library is chosen, the
three controllers own exactly the states enumerated in ISP-001 §5.

### Providers / Bloc / Riverpod Usage

Not specified — blocked on the same open decision. Once chosen, each
controller above is instantiated per-screen (not app-global), since
Vehicle Master's UI state (in-progress selection, in-progress admin
form) is screen-scoped and disposable (SSD-001 §5 — Client State is
never authoritative).

### Reusable Widgets

- `type_ahead_vehicle_selector_field.dart` — the type-ahead field used
  four times in `VehicleSelectorScreen` (Year/Brand/Model/Variant,
  `ENG-0001`), parameterized rather than duplicated.
- `valuation_master_form.dart` — shared between create-new-version and
  (read-only) history-detail views in `AdminValuationMasterScreen`.
- `concurrency_conflict_dialog.dart` — the "this record changed, reload
  before retrying" prompt (FS-001 §9), reusable for any future
  screen that hits a `409`.

### Loading States

Per ISP-001 §5's `Loading*`/`Saving` states — one loading indicator per
in-flight request, scoped to the field/section awaiting data (not a
full-screen blocking spinner for the type-ahead fields, to preserve the
type-ahead UX `ENG-0001` implies).

### Error States

Per ISP-001 §5/§14 — `VAL001`/`VAL002` (toast + retry), `VAL003`
(distinct empty state), `E-CATALOG-001` (inline form error),
`E-AUTHZ-001` (defensive "not authorized" state, should not normally be
reachable), `409` (explicit reload-then-retry dialog, never silent
retry).

### Empty States

Per FS-001 §20: empty catalog list → "No results" in the type-ahead
(Dealer side); empty Admin list → "create your first Brand/Model/
Variant" (Admin side); no pricing yet for a Year+Variant → distinct
"not yet priced" prompt (Admin ValuationMaster screen), separate from
the Dealer-facing `VAL003` state.

### Dark / Light Theme Considerations

**No Design System content exists in this repository** — DS-001 was
explicitly not transcribed (BUS-0004's decision). There are no color/
typography tokens to reference. Proposed, generic guidance only: all
three screens and their widgets consume `Theme.of(context)` (Flutter's
standard light/dark `ThemeData`) rather than hardcoding colors — no
module-specific theme logic in Vehicle Master. Actual token values
remain undefined pending a future DS-001 transcription decision; not
resolved here.

---

## 5. API Package

### Endpoint Implementation Order

Read endpoints before write endpoints (lower risk, no side effects,
easiest to test in isolation), catalog before pricing (pricing depends
on Variant existing):

1. `GET /vehicles/brands`
2. `GET /vehicles/models?brand_id=`
3. `GET /vehicles/variants?model_id=`
4. `GET /admin/vehicles` (read side of the discriminated endpoint,
   lower risk than its write side)
5. `POST /admin/vehicles`, `PUT /admin/vehicles/{id}`,
   `DELETE /admin/vehicles/{id}`
6. `GET /vehicles/configuration` (depends on at least one
   `ValuationMaster` row existing to return a non-`VAL003` result)
7. `GET /admin/valuation-master`, `POST /admin/valuation-master`,
   `DELETE /admin/valuation-master/{id}` (depends on Variant CRUD
   above)

### Request DTOs / Response DTOs

Per ISP-001 §2 — not redefined here.

### Validation Pipeline

Serializer-level field validation (§2 Validation Layer) →
service-level cross-field/business-rule validation (BR-0011 uniqueness,
`ENG-0003` concurrency) → repository-level DB constraints (§3) as a
final backstop. Three layers, not one — consistent with SEC-001's
"authority is the API boundary" while still defending in depth at the
DB layer.

### Authorization Checks

Every `/admin/*` view applies a `SuperAdminOnly` DRF permission class
(`permissions.py`) checking `request.user.role == 'super_admin'`
(`SEC-0001`) before the view body executes — never after, never
delegated to the service layer alone (defense in depth: permission
class **and** service-layer check, per SEC-001 "enforced at the API
layer, not only the UI").

---

## 6. Validation Package

### Validation Matrix

Per ISP-001 §6 — not redefined here; `validators.py` (§2) is its
implementation.

### Business Validation

BR-0004 (authorization, §5), BR-0007 (versioning, enforced in
`VehicleMasterAdminService`), BR-0011 (uniqueness — enforced at both
the service layer, for a clean `E-CATALOG-001` response, and the DB
layer, via the partial unique index, as a race-condition backstop).

### Database Validation

`NOT NULL`, `CHECK (>= 0)`, FK constraints, the BR-0011 partial unique
index — all §3 Constraints.

### API Validation

Serializer field validation (required/type/range) — §2 Validation
Layer, §5 Validation Pipeline.

### Client Validation

Flutter-side pre-checks mirror the Validation Matrix for immediate
user feedback (FS-001 §9 UI Requirements) — never authoritative
(SEC-001); the server re-validates every field regardless of what the
client already checked.

---

## 7. Error Package

| Error Code | Backend | API | Flutter UI |
|---|---|---|---|
| `VAL001` (Vehicle Not Found) | `VehicleNotFoundError` raised by repository/service when an id doesn't resolve | `404`, error envelope | Toast: "Vehicle not found," auto-retry not applicable (not a transient failure) |
| `VAL002` (Variant Missing) | `VariantMissingError` | `404` | Toast: "Selection incomplete," prompt to re-select |
| `VAL003` / `E-PRICING-001` (no pricing) | `PricingNotAvailableError` raised by `VehicleCatalogService.get_configuration` | `404`/`422`, error envelope | Distinct "pricing not available" empty state (not a generic error toast) |
| `E-CATALOG-001` (duplicate / BR-0011 violation) | `DuplicateCatalogEntryError` raised by `VehicleMasterAdminService` (service-layer check) or surfaced from the DB's partial-unique-index violation (race-condition path) | `409`/`422`, error envelope | Inline form error: "already exists" |
| `E-CATALOG-002` (Variant Deprecated) | Repository returns `active=false` row; service raises `DeprecatedVariantError` if selection attempted | `409` | Block selection, "no longer available" message |
| `E-AUTHZ-001` (not authorized) | `NotAuthorizedError`, raised by the `SuperAdminOnly` permission class before the view body runs | `403`, error envelope | Defensive "not authorized" state — should not normally be reachable if the Admin screens are correctly gated client-side (§4) |
| `409 Conflict` (concurrency) | `ConcurrencyConflictError` raised by `ValuationMasterRepository.create_new_version` on a stale `updated_at` | `409`, error envelope | Explicit `concurrency_conflict_dialog.dart` — reload-then-retry, never silent |

---

## 8. Test Package

Per TEST-001's conventions (test level definitions, `test_br_000x_...`
naming, coverage tied to Acceptance Criteria, synthetic fixtures only):

- **Unit tests:** one per Repository method (mocked DB session) and one
  per Service method (mocked Repositories) — `tests/
  test_*_repository.py`, `tests/test_*_service.py`. Named for the
  Business Rule or FR they verify where applicable (e.g.
  `test_br_0011_rejects_second_active_valuation_master`).
- **Integration tests:** Service ↔ real (test-DB) Repository — verifies
  the `ENG-0003` transaction actually rolls back both the version write
  and the audit write together on failure, not just in isolation.
- **API tests:** one per endpoint in §5.1, covering the success path and
  every error code in §7's table — `tests/test_*_views.py`.
- **Flutter widget tests:** one per screen in §4 Screens, covering
  every state in ISP-001 §5 (Loading/Loaded/Empty/Error/Conflict) —
  file location TBD pending the Flutter project's own test-folder
  convention (not yet established anywhere; proposed:
  `test/features/vehicle_master/` mirroring `lib/features/
  vehicle_master/`).
- **Golden tests (future):** deferred — TEST-001 doesn't yet name golden
  testing as a convention; not invented here, listed only because this
  prompt's task list names it as a "future" placeholder.
- **Manual QA checklist:** every Acceptance Criterion in FS-001 §19
  (`AC-001-001` through `AC-001-008`), plus the 5 FRs ISP-001 flagged as
  lacking a dedicated AC (FR-001-001/002/003/006/007/011) — manually
  verified against the FR text directly per ISP-001 §7's own note.

Per TEST-001's Coverage Expectation: every FS-001 Acceptance Criterion
must have at least one corresponding automated test before this
module's implementation is considered complete.

---

## 9. Development Order

```
Database (migrations 0001–0004, per §3)
   ↓
Repositories (Brand → Model → Variant → ValuationMaster, per §2/§3)
   ↓
Services (VehicleCatalogService, then VehicleMasterAdminService)
   ↓
API (read endpoints before write endpoints, per §5's Endpoint
     Implementation Order)
   ↓
Flutter (blocked on the state-management decision — §4 — before any
         screen work starts)
   ↓
Testing (unit/integration tests can begin as soon as each layer above
         exists; API/widget tests follow their respective layer;
         manual QA checklist last)
```

**Two sequencing dependencies outside this module's own control, not
resolved here:**

1. **Authentication's `users.role` migration (FS-003)** must exist
   before `E-AUTHZ-001`/`SuperAdminOnly` can be meaningfully tested
   end-to-end (unit tests can still mock `request.user.role`, but
   integration/API tests need a real `users` table with the column).
2. **The Flutter state-management library decision** (ISP-001 Open
   Question #6) must be made before any Flutter work in §4 begins —
   this is the single largest blocker to starting the Flutter half of
   this module in parallel with the backend half.

---

## 10. File Inventory

No file contents — paths only.

### Backend

```
src/vehicle_master/__init__.py
src/vehicle_master/apps.py
src/vehicle_master/models/__init__.py
src/vehicle_master/models/brand.py
src/vehicle_master/models/model.py
src/vehicle_master/models/variant.py
src/vehicle_master/models/valuation_master.py
src/vehicle_master/migrations/__init__.py
src/vehicle_master/migrations/0001_create_brands.py
src/vehicle_master/migrations/0002_create_models.py
src/vehicle_master/migrations/0003_create_variants.py
src/vehicle_master/migrations/0004_create_valuation_master.py
src/vehicle_master/repositories/__init__.py
src/vehicle_master/repositories/brand_repository.py
src/vehicle_master/repositories/model_repository.py
src/vehicle_master/repositories/variant_repository.py
src/vehicle_master/repositories/valuation_master_repository.py
src/vehicle_master/services/__init__.py
src/vehicle_master/services/vehicle_catalog_service.py
src/vehicle_master/services/vehicle_master_admin_service.py
src/vehicle_master/serializers/__init__.py
src/vehicle_master/serializers/catalog_serializers.py
src/vehicle_master/serializers/configuration_serializer.py
src/vehicle_master/serializers/admin_catalog_serializers.py
src/vehicle_master/serializers/valuation_master_serializers.py
src/vehicle_master/views/__init__.py
src/vehicle_master/views/catalog_views.py
src/vehicle_master/views/admin_vehicle_views.py
src/vehicle_master/views/admin_valuation_master_views.py
src/vehicle_master/permissions.py
src/vehicle_master/exceptions.py
src/vehicle_master/validators.py
src/vehicle_master/urls.py
src/vehicle_master/tests/__init__.py
src/vehicle_master/tests/test_brand_repository.py
src/vehicle_master/tests/test_model_repository.py
src/vehicle_master/tests/test_variant_repository.py
src/vehicle_master/tests/test_valuation_master_repository.py
src/vehicle_master/tests/test_vehicle_catalog_service.py
src/vehicle_master/tests/test_vehicle_master_admin_service.py
src/vehicle_master/tests/test_catalog_views.py
src/vehicle_master/tests/test_admin_vehicle_views.py
src/vehicle_master/tests/test_admin_valuation_master_views.py
src/vehicle_master/tests/fixtures.py
src/common/audit/__init__.py
src/common/audit/models.py
src/common/audit/repositories.py
```

### Flutter

```
lib/features/vehicle_master/data/models/brand_dto.dart
lib/features/vehicle_master/data/models/model_dto.dart
lib/features/vehicle_master/data/models/variant_dto.dart
lib/features/vehicle_master/data/models/configuration_dto.dart
lib/features/vehicle_master/data/models/repair_option_group_dto.dart
lib/features/vehicle_master/data/models/admin_vehicle_catalog_entry_dto.dart
lib/features/vehicle_master/data/models/valuation_master_dto.dart
lib/features/vehicle_master/data/datasources/vehicle_master_remote_data_source.dart
lib/features/vehicle_master/presentation/screens/vehicle_selector_screen.dart
lib/features/vehicle_master/presentation/screens/admin_vehicle_catalog_screen.dart
lib/features/vehicle_master/presentation/screens/admin_valuation_master_screen.dart
lib/features/vehicle_master/presentation/widgets/type_ahead_vehicle_selector_field.dart
lib/features/vehicle_master/presentation/widgets/valuation_master_form.dart
lib/features/vehicle_master/presentation/widgets/concurrency_conflict_dialog.dart
lib/features/vehicle_master/presentation/controllers/vehicle_selector_controller.dart
lib/features/vehicle_master/presentation/controllers/admin_vehicle_catalog_controller.dart
lib/features/vehicle_master/presentation/controllers/admin_valuation_master_controller.dart
lib/features/vehicle_master/vehicle_master_routes.dart
test/features/vehicle_master/vehicle_selector_screen_test.dart
test/features/vehicle_master/admin_vehicle_catalog_screen_test.dart
test/features/vehicle_master/admin_valuation_master_screen_test.dart
```

**Total: 42 backend files, 20 Flutter files — 62 files this module is
expected to produce.**

---

## Open Questions

Carried from ISP-001 (restated by reference, not re-litigated) plus two
new ones from this document's own level of detail:

1–7. ISP-001's seven (SDD-000 §4 drift; Free-tier catalog visibility;
   field length/Year range — proposed defaults in ISP-001 §6, unchanged
   here; catalog-deactivation cascade; Brand/Model/Variant concurrency
   scope; Flutter state-management library; `/admin/vehicles`
   entityType-discriminator confirmation).
8. **Pipeline clarification** — should Rule 24 (ISP stage) be amended to
   Architecture → FS → **ISP → EP** → Code → Testing, formalizing EP as
   its own stage (recommended, see Prompt Execution Report), or was EP
   intended to *replace* ISP going forward? Not assumed either way.
9. **`users.role` cross-module dependency** (§1/§9) — is FS-003
   (Authentication) expected to land before Vehicle Master
   implementation begins, or should Vehicle Master implementation
   start with a minimal stub `users` table? Not specified by any
   document; a real scheduling decision, not an architecture question.
