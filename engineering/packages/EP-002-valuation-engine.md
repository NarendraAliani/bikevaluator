# EP-002 — Valuation Engine Engineering Package

| Field | Value |
|---|---|
| Document ID | EP-002 |
| Version | 1.0 |
| Status | Draft |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | FS-002, ISP-002, EP-001, IMP-001A-D, DDD-001, DBD-001, API-001, BRR-001, SSD-001 |
| Next Documents | Production code (Valuation Engine + Flutter) |

Second Engineering Package, following EP-001's structure (Constitution
Rule 25). Builds directly on ISP-002 — no architecture reinterpreted,
no new API/schema/business rule introduced.

**Reuse posture (explicit, per this round's instruction):**
`api_utils.py` (response envelope, exception handler) — reused
unchanged. `service_factory.py` — extended with 2 new builders, not
duplicated. `ActorProvider`/`RequestContext`/`authorization.py` — **not
reused**, because Valuation Engine has no Super-Admin-only write; there
is no BR-0004 concern for these two read/compute endpoints. This is a
deliberate scope match, not an oversight (see ISP-002 for the same
note).

---

## 1. Module Summary

**Purpose:** turns a Vehicle Selection (FS-001) + Repair Component
Assessment into a Purchase Price and Recommendation, per BR-0001/
BR-0002/BR-0003/BR-0008/BR-0009/BR-0010.

**Dependencies:** `ValuationMasterRepository` (reused, IMP-001A).
**New:** `RepairComponentRepository`/`RepairOptionRepository` — this
module's implementation creates their models (ISP-002 §3's sequencing
resolution); FS-004 extends the same classes with write methods later.

**Inputs:** Year, Variant id, a list of `{repairComponentId,
repairOptionId}` pairs. **Outputs:** `{recommendedPrice, roundedPrice,
label}` — stateless, nothing persisted (`valuation_requests` stays
inactive).

---

## 2. Backend Package

### Folder Structure (extends the existing `vehicle_master` app — no new app)

Per SDD-000 §4, Valuation Engine and Vehicle Master are separate
*modules* conceptually, but per CSS-001's "one Django app per module
boundary" rule *and* the practical reality that this repository has one
Django project with one app so far, this package adds Valuation Engine
files **inside the existing `vehicle_master` app**, not a new
`valuation_engine` app — flagged as an Architecture Observation (see
below), since CSS-001 read literally would want a second app.

```
src/vehicle_master/
  models/
    repair_component.py       (new)
    repair_option.py          (new)
  migrations/
    0005_create_repair_components.py   (new)
    0006_create_repair_options.py      (new)
  repositories/
    repair_component_repository.py    (new)
    repair_option_repository.py       (new)
  services/
    valuation_service.py               (new)
    recommendation_service.py          (new)
  serializers/
    valuation_serializers.py           (new)
    repair_component_serializers.py    (new)
  views/
    valuation_views.py                 (new)
  tests/
    test_repair_repositories.py        (new)
    test_valuation_service.py          (new)
    test_recommendation_service.py     (new)
    test_valuation_views.py            (new)
    test_valuation_integration.py      (new)
```

**Architecture Observation:** CSS-001 ("one Django app per module
boundary," SDD-000 §4 module boundaries) would suggest Valuation Engine
is its own Django app (`valuation_engine`), separate from
`vehicle_master`. This package keeps it inside the existing
`vehicle_master` app instead, for one practical reason: `ValuationService`
depends directly on `ValuationMasterRepository`, and Django app-to-app
imports work identically either way in this codebase's current single-
project layout — splitting into a second app adds `INSTALLED_APPS`/
migration-dependency plumbing with no functional benefit at this scale
(one project, two conceptual modules, zero deployment separation
between them). Not a redesign of SDD-000 §4 (module *ownership*
boundaries are unchanged - Vehicle Master still doesn't own Valuation
logic, and vice versa, at the *code* level within the shared app);
purely a Django-project-layout pragmatism, flagged for the architect to
confirm or override.

### Repository Interfaces (concrete implementation, matching IMP-001A's pattern)

```python
class RepairComponentRepository:
    def get_active(self) -> list[RepairComponent]: ...
    def get_by_id(self, repair_component_id: uuid.UUID) -> RepairComponent | None: ...

class RepairOptionRepository:
    def get_active_by_component(self, repair_component_id: uuid.UUID) -> list[RepairOption]: ...
    def get_by_id(self, repair_option_id: uuid.UUID) -> RepairOption | None: ...
```

### Service Interfaces

Per ISP-002 §4 — `ValuationService` (BR-0001/BR-0002/BR-0009) and
`RecommendationService` (BR-0003/BR-0008) — not redefined here.

### Exception Strategy

Reuses `vehicle_master/exceptions.py` unchanged (`PricingNotAvailableError`,
`VehicleNotFoundError`, `VariantMissingError` already exist and cover
every error this module raises). No new exception class needed.

### Transaction Boundaries

None — this module performs no writes.

---

## 3. Database Package

### Migration Sequence

5. `0005_create_repair_components` — `repair_components` table
   (DBD-001 §2).
6. `0006_create_repair_options` — `repair_options` table, FK →
   `repair_components`, including `updated_at` (per DBD-001's own
   schema — a concurrency token for a future FS-004 write path, unused
   by this read-only module).

### Indexes / Constraints

Per DBD-001 §2 (repair_components: id, name; repair_options: id,
repair_component_id FK, option_name, deduction_amount, updated_at) —
index on `repair_options.repair_component_id` for the
`get_active_by_component` lookup. `CHECK (deduction_amount >= 0)` —
same non-negative-amount pattern as `valuation_master` (IMP-001A),
consistent defense in depth.

---

## 4. Flutter Package

**Reuses IMP-001A-D's precedent** (feature-first layout) rather than
inventing a new convention:

```
lib/features/valuation_engine/
  data/
    models/
      repair_component_dto.dart
      repair_option_dto.dart
      valuation_result_dto.dart
    datasources/
      valuation_remote_data_source.dart
  presentation/
    screens/
      repair_assessment_screen.dart
      valuation_result_screen.dart
    widgets/
      repair_component_card.dart
    controllers/
      repair_assessment_controller.dart
```

**State management, decided now (not further deferrable given this
round's build-and-run requirement):** plain `StatefulWidget`/`setState`
- no `Provider`/`BLoC`/`Riverpod` package adopted. This is an explicit,
flagged assumption (§Architecture Observations), not a resolution of
the long-open "Flutter state-management library" question - it
unblocks *this* build without committing the project to a framework
choice that should still be a deliberate decision.

**Architecture Observation - "Dealer Login" is not built.** The
requested user journey starts with Login. Authentication (FS-003) has
no specification anywhere in this repository - building a real login
screen means inventing business rules this package's own instructions
forbid. The app starts already-authenticated: an actor is injected via
the same `X-Actor-Id`/`X-Actor-Role` header mechanism the backend
already uses as its own temporary placeholder (`DummyActorProvider`,
IMP-001D). This is documented, not silently assumed.

---

## 5. API Package

### Endpoint Implementation Order

1. `GET /repairs/components` (read, no dependencies beyond the new
   repositories).
2. `POST /valuation/calculate` (depends on #1's data existing, and on
   `ValuationMasterRepository`, reused).

### Validation Pipeline / Authorization Checks

Serializer field validation → `ValuationService` business validation
(BR-0005 via `PricingNotAvailableError`) → response. **No authorization
check** - confirmed no Super-Admin-only concern exists in this module
(ISP-002 §title note).

---

## 6. Validation Package

Per ISP-002 §6 - not redefined here.

## 7. Error Package

| Error Code | Backend | API | Flutter UI |
|---|---|---|---|
| `VAL001`/`VAL002` | Reused `VehicleNotFoundError`/`VariantMissingError` | 404 | Toast + retry (reused FS-001 pattern) |
| `VAL003`/`E-PRICING-001` | Reused `PricingNotAvailableError` | 404 | Distinct "pricing not available" empty state (reused FS-001 pattern) |
| Malformed `repairAssessment` | DRF `ValidationError` | 400 | Inline form validation message |

## 8. Test Package

Per TEST-001 - unit (Service business logic), repository (behavior),
API integration (endpoint success/error paths), full-lifecycle
integration (Admin catalog build via ORM in test setup → Dealer
Configuration Load → Repair Assessment → Calculate → Result),
mirroring IMP-001C's `test_api_integration.py` pattern.

## 9. Development Order

```
Database (migrations 0005-0006)
   ↓
Repositories (RepairComponentRepository → RepairOptionRepository)
   ↓
Services (RecommendationService → ValuationService, since Valuation depends on Recommendation)
   ↓
API (GET /repairs/components → POST /valuation/calculate)
   ↓
Flutter (Repair Assessment screen → Result screen)
   ↓
Testing (unit/integration as each layer completes; E2E emulator run last)
```

## 10. File Inventory

**Backend (new):** 2 models, 2 migrations, 2 repositories, 2 services,
2 serializer modules, 1 view module, 5 test files = **14 files**.

**Flutter (new):** 3 DTOs, 1 data source, 2 screens, 1 widget, 1
controller, plus project scaffolding (`pubspec.yaml`, `lib/main.dart`,
platform folders via `flutter create`) = **~8 hand-written files** plus
generated scaffolding.

---

## Architecture Observations

1. Valuation Engine implemented inside the existing `vehicle_master`
   Django app rather than a new app - a project-layout pragmatism, not
   a module-ownership change (see §2).
2. Flutter state-management library chosen as plain `StatefulWidget`
   for this build only - the underlying question remains open for a
   deliberate future decision.
3. "Dealer Login" is not built - Authentication (FS-003) doesn't exist;
   the app starts pre-authenticated via the same header mechanism the
   backend already uses temporarily.
