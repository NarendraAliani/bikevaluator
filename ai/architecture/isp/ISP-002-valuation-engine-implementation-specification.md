# ISP-002 — Valuation Engine Implementation Specification

| Field | Value |
|---|---|
| Document ID | ISP-002 |
| Version | 1.0 |
| Status | Draft |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | FS-002, FSS-000, ISP-001, EP-001, IMP-001A/B/C/D, DDD-001, DBD-001, API-001, BRR-001, SSD-001 |
| Next Documents | EP-002 (Valuation Engine Engineering Package) |

**Note on FS-002's status:** this document's commissioning message
refers to FS-002 as "the approved FS-002." As of this writing,
`FS-002-valuation-engine.md`'s own Status field still reads **Draft** —
it has not been explicitly closed the way FS-001 was ("I consider
FS-001 closed. No more revisions."). Flagged transparently, same as
IMP-001A's analogous note about FS-001: the substantive work below
proceeds regardless (blocking on the field alone wastes the round), but
FS-002's Status should be explicitly confirmed before this ISP is
treated as final.

Second Implementation Specification, following ISP-001's template
(Constitution Rule 24) plus this round's additional requested elements
(explicit Architecture Compliance Checklist, cited sequence diagrams,
dependency analysis). Per FSS-000/Rule 24: no new API, schema, or
business rule is introduced — every genuinely open item is recorded in
§Open Questions.

**Reuse of Vehicle Master's shared infrastructure, as requested:**
`api_utils.py` (response envelope, exception handler) is reused
unchanged. `service_factory.py` will gain two new builder functions
(§4) rather than a parallel factory. **`ActorProvider`/`RequestContext`/
`authorization.py` are explicitly NOT dependencies of this module** —
unlike Vehicle Master's Admin endpoints, Valuation Engine has no
Super-Admin-only write (FS-002 §15: "no Super-Admin-only concern in
this module"), so there is no BR-0004 check to perform. Noted here so
this isn't mistaken for an oversight.

---

## 1. Backend API Contract

### 1.1 `POST /valuation/calculate`

| Field | Value |
|---|---|
| Authentication | Required (valid JWT) |
| Authorization | Any authenticated Dealer (no Super-Admin concern — FS-002 §15) |
| Request Body | `CalculateValuationRequest` (§2.1) |
| Query Parameters | None |
| Response Schema | `{ success, message, data: ValuationResultDto }` |
| Error Codes | `VAL003`/`E-PRICING-001` (no Active ValuationMaster, BR-0005), `VAL001`/`VAL002` (unresolvable variant, reusing FS-001's existing errors) |
| Validation Rules | See §6. |

**Implementation clarification (not a new endpoint):** API-001 writes
this response's field names in snake_case (`recommended_price`,
`rounded_price`, `label`), inconsistent with NS-001 §7's camelCase
convention that every other endpoint already implements (IMP-001C).
Treated as a documentation shorthand, not a deliberate exception —
`ValuationResultDto` (§2.2) uses `recommendedPrice`/`roundedPrice`/
`label`, matching every other response in this codebase. Flagged for a
future API-001 wording fix, not changed there now.

**No idempotency key** (`ENG-0002`, FS-002 §6/§19) — unchanged from
FS-002, this endpoint is stateless.

### 1.2 `GET /repairs/components`

| Field | Value |
|---|---|
| Authentication | Required |
| Authorization | Any authenticated Dealer |
| Request Body | None |
| Query Parameters | None |
| Response Schema | `{ success, message, data: { components: RepairComponentDto[] } }` |
| Error Codes | None beyond framework-level (401) |
| Validation Rules | None (no input). |

---

## 2. DTO Definitions

### 2.1 `CalculateValuationRequest`

| Field | Type | Nullable | Required | Validation |
|---|---|---|---|---|
| `year` | integer | No | Yes | Same range as FS-001 §8 (reused, not redefined) |
| `variantId` | UUID | No | Yes | Must reference an existing, active `variants` row (FS-001's `VariantRepository`, reused) |
| `repairAssessment` | array of `{ repairComponentId: UUID, repairOptionId: UUID }` | No | Yes, non-empty | Exactly one `repairOptionId` per required `repairComponentId` (FR-002-001/002) — structural check only; which components are "required" is itself an open question (see §Open Questions) |

### 2.2 `ValuationResultDto`

| Field | Type | Nullable |
|---|---|---|
| `recommendedPrice` | decimal | No |
| `roundedPrice` | decimal | No |
| `label` | enum (`EXCELLENT`\|`GOOD`\|`AVERAGE`\|`SCRAP`) | No |

### 2.3 `RepairComponentDto` / `RepairOptionDto`

| Field | Type | Nullable |
|---|---|---|
| `id` | UUID | No |
| `name` | string | No |
| `options` | array of `RepairOptionDto` | No |

**`RepairOptionDto`:**

| Field | Type | Nullable |
|---|---|---|
| `id` | UUID | No |
| `optionName` | enum (`OK`\|`PARTIAL`\|`FULL`) | No |
| `deductionAmount` | decimal | No |

**Cross-cutting note:** this is the same shape FS-001's `Configuration`
response has been returning empty (`repairOptions: []`) since IMP-001B,
because Repair Master had no implementation anywhere. Once this ISP's
repositories exist, **FS-001's `VehicleCatalogService.get_configuration`
could be updated to return real data here too** — out of this ISP's own
scope (that's a Vehicle Master change, not a Valuation Engine one), but
recorded as a direct architectural consequence worth a follow-up task,
not silently ignored.

---

## 3. Repository Layer

New interfaces (no implementation) - concrete classes, matching the
plain-class pattern established in `vehicle_master/repositories/*.py`
(IMP-001A) rather than an ABC, since (unlike `AuditLogRepository`) no
interface-only constraint applies here.

```python
class RepairComponentRepository:
    """Persistence-only. Read methods only - this module never writes
    to repair_components (administration is FS-004's concern, per
    FS-001 §2's precedent for excluding Repair Master's write side)."""

    def get_active(self) -> list[RepairComponent]: ...
    def get_by_id(self, repair_component_id: uuid.UUID) -> RepairComponent | None: ...


class RepairOptionRepository:
    """Persistence-only. Read methods only - same reasoning as above."""

    def get_active_by_component(self, repair_component_id: uuid.UUID) -> list[RepairOption]: ...
    def get_by_id(self, repair_option_id: uuid.UUID) -> RepairOption | None: ...
```

**Reused, not redefined:** `ValuationMasterRepository.
get_active_by_year_variant(year, variant_id)` (IMP-001A) - Valuation
Engine reads pricing through Vehicle Master's existing repository,
exactly as FS-002 §12 specifies.

**Sequencing note, resolved here (not an architecture decision):**
FS-002 Open Question #1 left "who creates the `repair_components`/
`repair_options` Django models" open, recommending "whichever module
implements first creates the models." This ISP resolves that
sequencing question: **this module's implementation (EP-002/IMP-002)
will create the `RepairComponent`/`RepairOption` models and migrations**,
since Valuation Engine is the first to need them. FS-004 (Admin) will
later *extend* these same repository classes with write methods
(create/update/deactivate), not create parallel ones - flagged here so
that reuse expectation is explicit ahead of time.

---

## 4. Service Layer

Two new services, matching SSD-001's actor separation (Valuation
Service computes the price; Recommendation Service is a distinct actor
applying the band) rather than one monolithic service:

```python
class ValuationService:
    """
    Orchestrates BR-0001 (formula), BR-0002 (scrap floor), BR-0009
    (rounding). Depends on ValuationMasterRepository (reused from
    Vehicle Master, IMP-001A), RepairOptionRepository (new, §3), and
    RecommendationService (below) to produce the final label.
    """

    def __init__(
        self,
        valuation_master_repository: ValuationMasterRepository,
        repair_option_repository: RepairOptionRepository,
        recommendation_service: "RecommendationService",
    ) -> None: ...

    def calculate(
        self, year: int, variant_id: uuid.UUID, repair_option_ids: list[uuid.UUID]
    ) -> ValuationResult:
        """
        FR-002-003..009. Raises PricingNotAvailableError (VAL003,
        reused from vehicle_master.exceptions) if no Active
        ValuationMaster exists (BR-0005).
        """
        ...


class RecommendationService:
    """Applies BR-0003/BR-0008 to a computed price. No repository dependency - pure calculation."""

    def recommend(self, rounded_price: Decimal, msp: Decimal) -> RecommendationLabel:
        """FR-002-008. Thresholds: 90/75/60% (confirmed final, BUS-0005) - never hardcoded elsewhere (BR-0008)."""
        ...
```

**BR-0006 (Subscription gate) is explicitly NOT this Service's
responsibility** - FS-002 §4/§23 already establishes this as a
precondition owned by FS-005, not implemented here. `ValuationService.
calculate()` takes no subscription-related parameter; gating happens
(once FS-005 exists) at the View layer, the same separation-of-concerns
pattern BR-0004/`ActorProvider` already established for Vehicle
Master's Admin writes.

**Extending `service_factory.py`** (reuse, not a parallel factory):

```python
def build_valuation_service() -> ValuationService:
    return ValuationService(
        valuation_master_repository=ValuationMasterRepository(),
        repair_option_repository=RepairOptionRepository(),
        recommendation_service=build_recommendation_service(),
    )

def build_recommendation_service() -> RecommendationService:
    return RecommendationService()
```

---

## 5. Flutter Contract

Same open dependency as ISP-001 §5 (Flutter state-management library
undecided) - carried forward, not re-litigated.

### 5.1 Repair Assessment Screen

| Field | Value |
|---|---|
| Screen ID | `RepairAssessmentScreen` |
| Route | `/repair-assessment` (proposed) |
| Provider/BLoC | `RepairAssessmentController` (library TBD) |
| API Calls | `GET /repairs/components` (on load), `POST /valuation/calculate` (on submit) |
| States | `Loading`, `Loaded`, `Submitting`, `Result`, `Error` |
| Loading | Component list loading indicator |
| Empty | No repair components configured yet - FS-002 doesn't specify this state explicitly; treated the same as FS-001 §20's empty-catalog precedent (show empty, not an error) |
| Validation | Every required component must have a selection before submit is enabled (FR-002-002, client-side, per SSD-001 §3.3) |
| Error Handling | `VAL003` -> distinct "pricing not available" state (reused from FS-001 §9's precedent) |
| Permissions | Any authenticated Dealer |

### 5.2 Result Screen

| Field | Value |
|---|---|
| Screen ID | `ValuationResultScreen` |
| Route | `/valuation-result` (proposed) |
| Provider/BLoC | Same controller as 5.1, or a dedicated one (TBD) |
| API Calls | None (receives result from 5.1's submit) |
| States | `Loaded` |
| Loading/Empty | N/A |
| Validation | N/A |
| Error Handling | N/A |
| Permissions | Any authenticated Dealer |

---

## 6. Validation Matrix

| Field | Required | Min | Max | Pattern | Error Message |
|---|---|---|---|---|---|
| `year` | Yes | (reused from FS-001 §8/ISP-001 §6) | (reused) | Integer | (reused) |
| `variantId` | Yes | - | - | UUID, must resolve to an active Variant | "variantId must reference an existing, active Variant" |
| `repairAssessment` | Yes | 1 entry | - | Array of `{repairComponentId, repairOptionId}` pairs | "At least one repair assessment entry is required" |
| `repairOptionId` (per entry) | Yes | - | - | UUID, must reference an active RepairOption belonging to the paired `repairComponentId` | "repairOptionId must belong to the specified repairComponentId" |

No new proposed defaults introduced - this module reuses FS-001/ISP-001's
existing field-length/range conventions wherever a field overlaps.

---

## 7. Error Mapping

| Error | Source | HTTP Status | Notes |
|---|---|---|---|
| `VAL001`/`VAL002` | API-001 (reused) | 404 | Unresolvable variant/component reference |
| `VAL003`/`E-PRICING-001` | API-001/SDD-000 §8 (reused) | 404 | No Active ValuationMaster (BR-0005) |
| `SUB001`/`E-SUB-001` | API-001/SDD-000 §8 | *(not enforced by this module)* | BR-0006's gate - FS-005's responsibility once it exists; listed here for completeness, not implemented in `ValuationService` |
| `E-NET-001` | SDD-000 §8 | *(client-side only)* | Client retains unsaved assessment locally (SSD-001 §3.3), no server-side handling needed |

No new error code introduced.

---

## 8. Sequence Diagrams

Per FSS-000 §5 ("add a new diagram only if this module's flow doesn't
already exist in SSD-001"): **not re-drawn.** SSD-001 §3.3 (Repair
Assessment) and §3.4 (Valuation) already cover this flow completely,
including the Recommendation Service as a distinct participant - cited
by reference, matching ISP-001's own precedent for FS-001's flows.

---

## 9. Test Strategy

Per TEST-001's conventions (test levels, `test_br_000x_...` naming,
synthetic fixtures only):

- **Unit tests:** `ValuationService.calculate` (BR-0001 formula,
  BR-0002 floor, BR-0009 rounding, each independently), `Recommendation
  Service.recommend` (all four bands + boundary values 90%/75%/60%,
  confirmed thresholds per `BUS-0005`).
- **Repository tests:** `RepairComponentRepository`/
  `RepairOptionRepository` - initialization/shape (per IMP-001A's
  precedent) plus behavior (active-filtering, scoping by component) per
  IMP-001B's expanded-coverage precedent.
- **API integration tests:** `POST /valuation/calculate` success path,
  `VAL003` path, malformed `repairAssessment` payload (400); `GET
  /repairs/components` success and empty-catalog paths.
- **Full-lifecycle integration test:** Admin creates Brand/Model/
  Variant/ValuationMaster/RepairComponent/RepairOption (once FS-004's
  admin writes exist, or via direct ORM calls in the test setup if
  FS-004 hasn't landed yet) -> Dealer loads Configuration -> Dealer
  submits a Repair Assessment -> `/valuation/calculate` returns the
  expected price and label - mirroring IMP-001C's
  `test_api_integration.py` pattern.

## 10. Architecture Compliance Checklist

| Field | Content |
|---|---|
| Architecture documents referenced | DDD-001 §3/§7 (RepairComponent, RepairOption, Valuation, Recommendation domain objects/services); DBD-001 §2/§6a (repair_components/repair_options schema, ENG-0003 concurrency policy - relevant once FS-004 adds writes); API-001 v1.1 (`/valuation/calculate`, `/repairs/components`); BRR-001 v1.2 (BR-0001/0002/0003/0005/0006/0008/0009/0010); SSD-001 v1.1 §3.3/§3.4; FS-002; ISP-001 (pattern reused); EP-001/IMP-001A-D (shared infrastructure reused). |
| Decision IDs implemented | `BUS-0005` (thresholds, §4/§9), `ARC-0009` (RepairAssessment transient - this module never persists one), `ENG-0002` (no idempotency key, §1.1). |
| Business Rule IDs referenced | BR-0001, BR-0002, BR-0003, BR-0005, BR-0006 (dependency only, not enforced here), BR-0008, BR-0009, BR-0010. |
| APIs used | `/valuation/calculate`, `/repairs/components`. |
| Database tables used | `valuation_master` (read-only, reused repository), `repair_components`, `repair_options` (read-only, new repositories - models/migrations to be created by this module's implementation, per §3's sequencing resolution). |
| Deviations | None from FS-002. One pre-existing API-001 wording inconsistency noted (snake_case response fields), resolved in favor of NS-001 §7's camelCase convention already used everywhere else - not a deviation from architecture, a correction of documentation shorthand. |
| New architectural questions | See §Open Questions - two carried unresolved from FS-002 (MSP=0/Margin≥MSP edge case; concurrent pricing edit during in-flight calculation), one resolved here (Repair Master model sequencing), one refined (FS-005/BR-0006 - now concretely deferred to the View layer once FS-005 exists, not `ValuationService`). |

---

## Dependency Analysis (Cross-FS Dependencies)

| Depends On (must be Approved first) | Provides To (future FS depending on this one) |
|---|---|
| **FS-001 (Vehicle Master):** Approved. Reuses `ValuationMasterRepository` directly. | **FS-004 (Admin):** will extend `RepairComponentRepository`/`RepairOptionRepository` (created here) with write methods for Repair Master administration - not duplicate them. |
| **FS-005 (Subscription) — still does not exist.** BR-0006 remains a precondition this module depends on conceptually; `ValuationService` itself takes no subscription parameter, deferring the gate entirely to the View layer once FS-005 exists (same pattern as `ActorProvider` for BR-0004). | **Reports (future):** would read `ValuationResult`/Recommendation once persistence (`valuation_requests` v2) activates - out of scope. |

---

## Open Questions

Carried from FS-002 (restated by reference), one resolved, one
refined, plus nothing new invented:

1. **Repair Master model/migration ownership — RESOLVED by this ISP.**
   This module's implementation creates `RepairComponent`/`RepairOption`
   Django models; FS-004 extends the same repositories later, per §3.
2. **FS-005/BR-0006 — refined, not resolved.** `ValuationService` is
   explicitly designed with no subscription-awareness at all; the gate
   is deferred entirely to the View layer, mirroring the `ActorProvider`
   pattern. Still cannot be code-enforced until FS-005 exists.
3. **MSP=0 / Margin ≥ MSP edge case** — unchanged from FS-002, still
   genuinely undefined.
4. **Concurrent pricing edit during an in-flight calculation** —
   unchanged from FS-002, still genuinely undefined (a read-then-use
   timing question, distinct from `ENG-0003`'s write-conflict
   protection).
