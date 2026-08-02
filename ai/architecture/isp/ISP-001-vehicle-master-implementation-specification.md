# ISP-001 — Vehicle Master Implementation Specification

| Field | Value |
|---|---|
| Document ID | ISP-001 |
| Version | 1.0 |
| Status | Draft |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | FS-001, FSS-000, DDD-001, DBD-001, API-001, BRR-001, ABL-001 |
| Next Documents | Backend implementation, Flutter implementation |

**Note on FS-001's status:** this document's commissioning prompt refers
to FS-001 as "the approved Functional Specification." As of this
writing, `FS-001-vehicle-master.md`'s own Status field still reads
**Draft** — it has not been changed to `Approved` in the repository.
This is flagged transparently rather than silently assumed either way:
the substantive work below proceeds (blocking on a status-field
technicality would waste the round), but FS-001's Status should be
explicitly set before this ISP is treated as final, per Constitution
Rule 20/22. Status here is set to `Draft` to mirror FS-001's own actual
status rather than overclaim readiness.

This document translates FS-001 into precise, language-level
implementation contracts. **No architecture was modified, no business
rule was changed, no new API endpoint was introduced** — every endpoint,
table, and rule below is cited from an Approved document. Where FS-001
or API-001 left a genuine implementation-level gap (e.g. exact field
length limits, or how one shared endpoint serves three catalog levels),
this document proposes a concrete, clearly-flagged default so a
developer isn't blocked — never silently, always marked as a proposal
rather than a settled fact.

---

## 1. Backend API Contract

### 1.1 `GET /vehicles/brands`

| Field | Value |
|---|---|
| Authentication | Required (valid JWT) |
| Authorization | Any authenticated role (`dealer` or `super_admin`) |
| Request Body | None |
| Query Parameters | None. If a `year` parameter is present it is accepted but ignored — no filtering effect (`ARC-0005`, FS-001 AC-001-008), not rejected as invalid. |
| Response Schema | `{ success, message, data: { brands: BrandDto[] } }` |
| Error Codes | `401` (missing/invalid JWT, FS-003 scope) |
| Validation Rules | None (no input). |

### 1.2 `GET /vehicles/models?brand_id=`

| Field | Value |
|---|---|
| Authentication | Required |
| Authorization | Any authenticated role |
| Request Body | None |
| Query Parameters | `brand_id` (UUID, required) |
| Response Schema | `{ success, message, data: { models: ModelDto[] } }` |
| Error Codes | `400` (missing/malformed `brand_id`), `404`/`VAL001` (brand_id does not resolve to an active Brand) |
| Validation Rules | `brand_id`: required, valid UUID, must reference an existing `brands` row. |

### 1.3 `GET /vehicles/variants?model_id=`

| Field | Value |
|---|---|
| Authentication | Required |
| Authorization | Any authenticated role |
| Request Body | None |
| Query Parameters | `model_id` (UUID, required) |
| Response Schema | `{ success, message, data: { variants: VariantDto[] } }` |
| Error Codes | `400` (missing/malformed `model_id`), `404`/`VAL001` (model_id does not resolve) |
| Validation Rules | `model_id`: required, valid UUID, must reference an existing `models` row. |

### 1.4 `GET /vehicles/configuration?year=&brand_id=&model_id=&variant_id=`

**Implementation clarification (not a new endpoint):** API-001 wrote
this endpoint's params as `year=&brand=&model=&variant=` without the
`_id` suffix used elsewhere in the same document. This spec treats them
as `brand_id`/`model_id`/`variant_id` for consistency with
`/vehicles/models`/`/vehicles/variants`'s own established param naming
— recommend API-001 be tightened to match in a future revision (not
done here, out of this document's scope).

| Field | Value |
|---|---|
| Authentication | Required |
| Authorization | Any authenticated role. Subscription-tier catalog-visibility interaction is undefined (FS-001 Open Question #2) — not enforced here pending that answer. |
| Request Body | None |
| Query Parameters | `year` (int, required), `brand_id` (UUID, required), `model_id` (UUID, required), `variant_id` (UUID, required). Only `year` + `variant_id` are actually used to resolve the `valuation_master` row (BR-0011 keys on Year+Variant); `brand_id`/`model_id` are required for request-shape consistency and are validated for referential correctness but do not affect the lookup. |
| Response Schema | `{ success, message, data: ConfigurationDto }` |
| Error Codes | `VAL001`/`VAL002` (brand/model/variant id doesn't resolve), `VAL003`/`E-PRICING-001` (no Active `ValuationMaster` for Year+Variant — BR-0005) |
| Validation Rules | All four params required; `year` must be a positive integer (exact valid range: FS-001 Open Question #3, proposed default in §6). |

### 1.5 `GET /admin/vehicles` and `POST /admin/vehicles`

**Implementation clarification (not a new endpoint):** API-001 defines
one endpoint for Brand/Model/Variant CRUD ("List/create Brand/Model/
Variant/pricing"). This spec resolves the shape as an `entityType`
discriminator (`BRAND`|`MODEL`|`VARIANT`) shared across one request/
response contract, rather than three separate paths — no new API
surface is introduced, only the existing single path's payload shape
is made concrete. ("/pricing" in API-001's description is treated as a
documentation imprecision — pricing is `/admin/valuation-master`'s
concern, §1.7; not addressed here.)

| Field | Value |
|---|---|
| Authentication | Required |
| Authorization | `super_admin` only (BR-0004); `E-AUTHZ-001`/403 otherwise |
| Request Body (POST) | `CreateVehicleCatalogEntryRequest` (§2.1) |
| Query Parameters (GET) | `entityType` (required), `parentId` (required for `MODEL`/`VARIANT`, ignored for `BRAND`) |
| Response Schema | GET: `{ success, message, data: { entries: AdminVehicleCatalogEntryDto[] } }`. POST: `{ success, message, data: AdminVehicleCatalogEntryDto }` |
| Error Codes | `E-CATALOG-001` (duplicate Brand/Model/Variant/Year combination), `E-AUTHZ-001`/403, `400` (missing `entityType`/`parentId`) |
| Validation Rules | See §6 Validation Matrix. |

### 1.6 `PUT /admin/vehicles/{id}` and `DELETE /admin/vehicles/{id}`

| Field | Value |
|---|---|
| Authentication | Required |
| Authorization | `super_admin` only; `E-AUTHZ-001`/403 otherwise |
| Request Body (PUT) | `UpdateVehicleCatalogEntryRequest` (§2.2) |
| Query Parameters | None |
| Response Schema | `{ success, message, data: AdminVehicleCatalogEntryDto }` (PUT); `{ success, message, data: null }` (DELETE — soft-deactivate, sets `active=false` per DBD-001 §5, no hard delete) |
| Error Codes | `404`/`VAL001` (id not found), `E-CATALOG-001` (rename creates a duplicate), `E-AUTHZ-001`/403 |
| Validation Rules | See §6. `DELETE` has no body. |

### 1.7 `/admin/valuation-master` (CRUD)

**Implementation clarification (not a new endpoint):** API-001 marks
this "CRUD" without enumerating methods. Since BR-0007 forbids in-place
pricing edits, this spec resolves it as: `GET` (list/history), `GET
/{id}` (single version), `POST` (create a new version — the only
"edit" operation, implicitly closing the current Active row), `DELETE
/{id}` (soft-deactivate, retire pricing entirely, no new version). **No
`PUT`** — BR-0007 does not permit overwriting a version in place.

| Field | Value |
|---|---|
| Authentication | Required |
| Authorization | `super_admin` only; `E-AUTHZ-001`/403 otherwise |
| Request Body (POST) | `CreateValuationMasterVersionRequest` (§2.3) |
| Query Parameters (GET) | `year` + `variant_id` (both required — returns full version history for that Year+Variant, Active and superseded) |
| Response Schema | GET list: `{ success, message, data: { versions: ValuationMasterDto[] } }`. GET `/{id}`, POST: `{ success, message, data: ValuationMasterDto }`. DELETE: `{ success, message, data: null }` |
| Error Codes | `E-CATALOG-001` (BR-0011 violation — a second Active row for the same Year+Variant), `409 Conflict` (stale `updatedAt` on the row being superseded — `ENG-0003`), `E-AUTHZ-001`/403, `404` (id not found) |
| Validation Rules | See §6. |

---

## 2. DTO Definitions

### 2.1 `CreateVehicleCatalogEntryRequest`

| Field | Type | Nullable | Required | Validation |
|---|---|---|---|---|
| `entityType` | enum (`BRAND`\|`MODEL`\|`VARIANT`) | No | Yes | Must be one of the three values |
| `parentId` | UUID | Yes | Conditional — required if `entityType` is `MODEL` (references `brands.id`) or `VARIANT` (references `models.id`); must be absent/ignored if `BRAND` | Must resolve to an existing, active parent row when required |
| `name` | string | No | Yes | 1–100 chars (proposed default, FS-001 Open Question #3) |

### 2.2 `UpdateVehicleCatalogEntryRequest`

| Field | Type | Nullable | Required | Validation |
|---|---|---|---|---|
| `name` | string | No | Yes | 1–100 chars (same proposed default) |

`entityType`/`parentId` are not editable after creation (moving a
Model to a different Brand, or a Variant to a different Model, is not
specified anywhere as a supported operation — not addressed here; if
needed, treat as a new Functional Requirement for a future FS-001
revision, not invented in this ISP).

### 2.3 `CreateValuationMasterVersionRequest`

| Field | Type | Nullable | Required | Validation |
|---|---|---|---|---|
| `year` | integer | No | Yes | Proposed range 1980–(current year + 1), FS-001 Open Question #3 |
| `variantId` | UUID | No | Yes | Must reference an existing, active `variants` row |
| `minimumSellingPrice` | decimal | No | Yes | ≥ 0 |
| `margin` | decimal | No | Yes | ≥ 0 |
| `scrapValue` | decimal | No | Yes | ≥ 0 |
| `previousVersionUpdatedAt` | datetime (ISO 8601) | Yes | Required only if an Active `ValuationMaster` row already exists for this Year+Variant (optimistic-concurrency token, `ENG-0003`); omitted when creating the very first version | Must exactly match the current Active row's `updated_at`, else `409 Conflict` |

`effectiveFrom`/`effectiveTo` are **not** client-supplied fields —
server-assigned (`effectiveFrom = now()` on the new row; `effectiveTo =
now()` on the row being closed), per SSD-001 §3.7.

### 2.4 Response DTOs

**`BrandDto`**

| Field | Type | Nullable |
|---|---|---|
| `id` | UUID | No |
| `brandName` | string | No |

**`ModelDto`**

| Field | Type | Nullable |
|---|---|---|
| `id` | UUID | No |
| `brandId` | UUID | No |
| `modelName` | string | No |

**`VariantDto`**

| Field | Type | Nullable |
|---|---|---|
| `id` | UUID | No |
| `modelId` | UUID | No |
| `variantName` | string | No |

**`ConfigurationDto`**

| Field | Type | Nullable |
|---|---|---|
| `valuationMasterId` | UUID | No |
| `year` | integer | No |
| `variantId` | UUID | No |
| `minimumSellingPrice` | decimal | No |
| `margin` | decimal | No |
| `scrapValue` | decimal | No |
| `repairOptions` | `RepairOptionGroupDto[]` | No (may be empty array) |

**`RepairOptionGroupDto`** (read-only pass-through; authoritative shape
belongs to whichever FS ends up owning Repair Master administration,
likely FS-004 — included here only because `/vehicles/configuration`'s
response contains it per API-001)

| Field | Type | Nullable |
|---|---|---|
| `repairComponentId` | UUID | No |
| `repairComponentName` | string | No |
| `options` | array of `{ id: UUID, optionName: string, deductionAmount: decimal }` | No |

**`AdminVehicleCatalogEntryDto`**

| Field | Type | Nullable |
|---|---|---|
| `id` | UUID | No |
| `entityType` | enum (`BRAND`\|`MODEL`\|`VARIANT`) | No |
| `parentId` | UUID | Yes (null for `BRAND`) |
| `name` | string | No |
| `active` | boolean | No |

**`ValuationMasterDto`**

| Field | Type | Nullable |
|---|---|---|
| `id` | UUID | No |
| `year` | integer | No |
| `variantId` | UUID | No |
| `minimumSellingPrice` | decimal | No |
| `margin` | decimal | No |
| `scrapValue` | decimal | No |
| `active` | boolean | No |
| `effectiveFrom` | datetime | No |
| `effectiveTo` | datetime | Yes (null while Active) |
| `updatedAt` | datetime | No |

**Error DTO** — per API-000 v1.1 (`ARC-0007`), not redefined:
`{ success: false, message: string, errors: [{ code, message, field }] }`.

---

## 3. Repository Layer

Interfaces only — no implementation. Python/Django-flavored (NS-001 §5:
`snake_case` methods, `PascalCase` classes).

```python
class BrandRepository(ABC):
    def get_active(self) -> list[Brand]: ...
    def get_by_id(self, brand_id: UUID) -> Brand | None: ...
    def name_exists(self, brand_name: str, exclude_id: UUID | None = None) -> bool: ...
    def create(self, brand_name: str) -> Brand: ...
    def update(self, brand_id: UUID, brand_name: str) -> Brand: ...
    def deactivate(self, brand_id: UUID) -> None: ...

class ModelRepository(ABC):
    def get_active_by_brand(self, brand_id: UUID) -> list[Model]: ...
    def get_by_id(self, model_id: UUID) -> Model | None: ...
    def name_exists(self, brand_id: UUID, model_name: str, exclude_id: UUID | None = None) -> bool: ...
    def create(self, brand_id: UUID, model_name: str) -> Model: ...
    def update(self, model_id: UUID, model_name: str) -> Model: ...
    def deactivate(self, model_id: UUID) -> None: ...

class VariantRepository(ABC):
    def get_active_by_model(self, model_id: UUID) -> list[Variant]: ...
    def get_by_id(self, variant_id: UUID) -> Variant | None: ...
    def name_exists(self, model_id: UUID, variant_name: str, exclude_id: UUID | None = None) -> bool: ...
    def create(self, model_id: UUID, variant_name: str) -> Variant: ...
    def update(self, variant_id: UUID, variant_name: str) -> Variant: ...
    def deactivate(self, variant_id: UUID) -> None: ...

class ValuationMasterRepository(ABC):
    def get_active_by_year_variant(self, year: int, variant_id: UUID) -> ValuationMaster | None: ...
    def get_by_id(self, valuation_master_id: UUID) -> ValuationMaster | None: ...
    def get_version_history(self, year: int, variant_id: UUID) -> list[ValuationMaster]: ...
    def create_new_version(
        self,
        year: int,
        variant_id: UUID,
        minimum_selling_price: Decimal,
        margin: Decimal,
        scrap_value: Decimal,
        expected_previous_updated_at: datetime | None,
    ) -> ValuationMaster:
        """Closes the current Active row's effective_to and inserts the
        new row as one atomic operation (BR-0007, ENG-0003). Raises
        ConcurrencyConflictError if expected_previous_updated_at does not
        match the current row's updated_at."""
        ...
    def deactivate(self, valuation_master_id: UUID) -> None: ...

class AuditLogRepository(ABC):
    def create(
        self, actor_id: UUID, entity_type: str, entity_id: UUID,
        old_value: dict | None, new_value: dict | None, ip_address: str,
    ) -> None: ...
```

---

## 4. Service Layer

### 4.1 `VehicleCatalogService` (Dealer-facing, read-only)

| Method | Responsibility |
|---|---|
| `list_brands() -> list[Brand]` | FR-001-001 |
| `list_models(brand_id: UUID) -> list[Model]` | FR-001-002 |
| `list_variants(model_id: UUID) -> list[Variant]` | FR-001-003 |
| `get_configuration(year: int, brand_id: UUID, model_id: UUID, variant_id: UUID) -> Configuration` | FR-001-004, FR-001-005. Raises `PricingNotAvailableError` (→ `VAL003`) if no Active `ValuationMaster` exists. |

**Dependencies:** `BrandRepository`, `ModelRepository`, `VariantRepository`,
`ValuationMasterRepository`, and a read-only Repair Master
collaborator (external to this module — see FS-001 §2 scope note;
interface not defined here, owned by whichever FS specifies Repair
Master).

### 4.2 `VehicleMasterAdminService` (Super-Admin-facing, write)

| Method | Responsibility |
|---|---|
| `create_brand(name: str, actor: User) -> Brand` | FR-001-006, FR-001-007, FR-001-011 |
| `update_brand(brand_id: UUID, name: str, actor: User) -> Brand` | FR-001-006, FR-001-011 |
| `deactivate_brand(brand_id: UUID, actor: User) -> None` | FR-001-006, FR-001-011 |
| `create_model(brand_id: UUID, name: str, actor: User) -> Model` | Same pattern as Brand |
| `update_model(model_id: UUID, name: str, actor: User) -> Model` | Same pattern |
| `deactivate_model(model_id: UUID, actor: User) -> None` | Same pattern |
| `create_variant(model_id: UUID, name: str, actor: User) -> Variant` | Same pattern |
| `update_variant(variant_id: UUID, name: str, actor: User) -> Variant` | Same pattern |
| `deactivate_variant(variant_id: UUID, actor: User) -> None` | Same pattern |
| `create_valuation_master_version(year, variant_id, msp, margin, scrap_value, expected_previous_updated_at, actor: User) -> ValuationMaster` | FR-001-008, FR-001-009, FR-001-011, FR-001-012 |
| `deactivate_valuation_master(valuation_master_id: UUID, actor: User) -> None` | FR-001-011 |

**Responsibilities:** enforces BR-0004 (via `AuthorizationPolicy`
collaborator — raises `AuthorizationError` → `E-AUTHZ-001` if
`actor.role != super_admin`), BR-0007 (versioning), BR-0011 (uniqueness,
via `E-CATALOG-001`), and FR-001-011 (writes an `AuditLogRepository`
entry for every mutation). For `ValuationMaster` writes, wraps the
repository call and the audit write in **one transaction**
(`ENG-0003`) via a `UnitOfWork`/transaction-manager collaborator — not
two separate calls.

**Dependencies:** `BrandRepository`, `ModelRepository`,
`VariantRepository`, `ValuationMasterRepository`, `AuditLogRepository`,
`AuthorizationPolicy`, transaction manager (Django's
`transaction.atomic()` or equivalent unit-of-work abstraction).

---

## 5. Flutter Contract

**Open implementation question, not resolved here:** no architecture
document specifies BIKEVALUATOR's Flutter state-management library
(BLoC, Provider, Riverpod, or other). This is a real technical choice
with long-term implications — not assumed. Below, each screen's state
container is named generically (`...Controller`) and works under any of
these; picking one is recommended as a small, explicit follow-up
decision before Flutter work starts (see §Open Questions).

### 5.1 Vehicle Selector Screen (Dealer)

| Field | Value |
|---|---|
| Screen ID | `VehicleSelectorScreen` |
| Route | `/vehicle-selector` (proposed — no Flutter routing convention exists in NS-001; flagged) |
| Provider/BLoC | `VehicleSelectorController` (library TBD, see above) |
| API Calls | `GET /vehicles/brands` (on load), `GET /vehicles/models?brand_id=` (on Brand selected), `GET /vehicles/variants?model_id=` (on Model selected), `GET /vehicles/configuration?...` (on Variant + Year selected) |
| States | `Initial`, `LoadingBrands`, `BrandsLoaded`, `LoadingModels`, `ModelsLoaded`, `LoadingVariants`, `VariantsLoaded`, `LoadingConfiguration`, `ConfigurationLoaded`, `ConfigurationUnavailable` (`VAL003`), `Error` |
| Loading | Per-field loading indicator on the active type-ahead (`ENG-0001`) while its list is being fetched |
| Empty | Brand/Model/Variant list empty at a given level → type-ahead shows "No results," not an error (FS-001 §20) |
| Validation | Year, Brand, Model, Variant all required before Configuration Load fires. Year selection is independent of Brand/Model/Variant fetching (no server-side dependency, per `ARC-0005`) — only required alongside `variant_id` at the final call. |
| Error Handling | `VAL001`/`VAL002` → toast + allow retry; `VAL003` → distinct "pricing not available" empty state (FS-001 §9), not a generic error; network failure on any `GET` → safe to auto-retry (idempotent, SSD-001 §6). |
| Permissions | Any authenticated Dealer — no additional screen-level check. |

### 5.2 Admin Vehicle Catalog Screen (Super Admin)

| Field | Value |
|---|---|
| Screen ID | `AdminVehicleCatalogScreen` |
| Route | `/admin/vehicle-catalog` (proposed) |
| Provider/BLoC | `AdminVehicleCatalogController` (library TBD) |
| API Calls | `GET /admin/vehicles?entityType=` (list per level), `POST /admin/vehicles` (create), `PUT /admin/vehicles/{id}` (update), `DELETE /admin/vehicles/{id}` (deactivate) |
| States | `Loading`, `Loaded`, `Empty`, `Saving`, `SaveSuccess`, `SaveError` |
| Empty | No entries yet at a given level → "create your first Brand/Model/Variant" prompt |
| Validation | `name` required, non-empty, client-side pre-check mirrors §6; server remains authoritative |
| Error Handling | `E-CATALOG-001` → inline "already exists" form error; `E-AUTHZ-001` → "not authorized" (should not normally be reachable if screen-level permission gating works, see below) |
| Permissions | Screen itself should not be navigable by a `dealer`-role account (client-side UX gate); server-side `E-AUTHZ-001`/BR-0004 is the actual enforcement, not this gate. |

### 5.3 Admin ValuationMaster Screen (Super Admin)

| Field | Value |
|---|---|
| Screen ID | `AdminValuationMasterScreen` |
| Route | `/admin/valuation-master` (proposed, mirrors API path) |
| Provider/BLoC | `AdminValuationMasterController` (library TBD) |
| API Calls | `GET /admin/valuation-master?year=&variant_id=` (history), `POST /admin/valuation-master` (new version), `DELETE /admin/valuation-master/{id}` (deactivate) |
| States | `Loading`, `Loaded`, `Empty`, `Saving`, `SaveSuccess`, `SaveConflict` (409), `SaveError` |
| Empty | No pricing set yet for the selected Year+Variant → prompt to create the first version (distinct from the Dealer-facing `VAL003` empty state — this is the Admin's own "not yet priced" view) |
| Validation | MSP/Margin/Scrap Value non-negative (§6); `previousVersionUpdatedAt` sent automatically from the last-loaded record, never user-edited |
| Error Handling | `409 Conflict` → explicit "this record changed, reload before retrying" prompt (FS-001 §9 UI Requirement, `ENG-0003`) — never silently retried; `E-CATALOG-001` → "a pricing record for this Year+Variant already exists" |
| Permissions | Super Admin only, same pattern as §5.2. |

---

## 6. Validation Matrix

| Field | Required | Min | Max | Pattern | Error Message |
|---|---|---|---|---|---|
| `brandName` / `modelName` / `variantName` | Yes | 1 char | 100 chars *(proposed default — FS-001 Open Question #3, not specified in NS-001/CSS-001/DBD-001)* | Free text | "Name is required" / "Name must be 100 characters or fewer" |
| `year` | Yes | 1980 *(proposed default)* | current year + 1 *(proposed default)* | Integer | "Year must be between 1980 and {max}" |
| `minimumSellingPrice` | Yes | 0 | — (none specified) | Decimal, ≥ 0 | "MSP must be zero or greater" |
| `margin` | Yes | 0 | — | Decimal, ≥ 0 | "Margin must be zero or greater" |
| `scrapValue` | Yes | 0 | — | Decimal, ≥ 0 | "Scrap value must be zero or greater" |
| `entityType` | Yes | — | — | Enum: `BRAND`\|`MODEL`\|`VARIANT` | "entityType must be BRAND, MODEL, or VARIANT" |
| `parentId` | Conditional (MODEL/VARIANT) | — | — | UUID, must reference an active parent | "parentId is required and must reference an existing, active record" |
| `variantId` (ValuationMaster write) | Yes | — | — | UUID, must reference an active `variants` row | "variantId must reference an existing, active Variant" |
| `previousVersionUpdatedAt` | Conditional (when superseding) | — | — | ISO 8601 datetime, exact match to current row | *(surfaced as `409 Conflict`, not a field-level validation error)* |

Fields marked "proposed default" are **implementation-level defaults,
not business rules** — they unblock development now and should be
confirmed or revised by the architect; not treated as settled fact.

---

## 7. Test Matrix

| FR | Acceptance Criteria | Suggested Test Cases |
|---|---|---|
| FR-001-001 (list Brands) | *(FS-001 has no dedicated AC for this — gap noted, recommend FS-001 add one in a future revision)* | Returns only `active=true` Brands; returns empty array when none exist; rejects unauthenticated request with 401. |
| FR-001-002 (list Models) | *(no dedicated AC — same gap)* | Returns only active Models for a valid `brand_id`; 404/`VAL001` for a non-existent `brand_id`. |
| FR-001-003 (list Variants) | *(no dedicated AC — same gap)* | Returns only active Variants for a valid `model_id`; 404/`VAL001` for a non-existent `model_id`. |
| FR-001-004 (Configuration Load, success) | AC-001-002 | Given an Active `ValuationMaster` for Year+Variant, returns MSP/Margin/Scrap + repair options, HTTP 200. |
| FR-001-005 (Configuration Load, missing pricing) | AC-001-003 | Given no Active `ValuationMaster`, returns `VAL003`/`E-PRICING-001` with no partial data. |
| FR-001-006 (Brand/Model/Variant CRUD) | *(no dedicated AC — gap noted)* | Create/update/deactivate each entity type succeeds for a `super_admin`; deactivated entries excluded from Dealer-facing lists. |
| FR-001-007 (duplicate rejection) | *(implied by `E-CATALOG-001`, no dedicated AC)* | Creating a duplicate Brand/Model/Variant/Year combination returns `E-CATALOG-001`, no row written. |
| FR-001-008 (ValuationMaster versioning) | AC-001-004 | New version closes the prior row's `effectiveTo` and inserts a new Active row atomically with one audit entry. |
| FR-001-009 (BR-0011 uniqueness) | AC-001-005 | Attempting a second Active row for the same Year+Variant without closing the first is rejected with `E-CATALOG-001`. |
| FR-001-010 (authorization) | AC-001-006 | A `dealer`-role token on any `/admin/*` endpoint is rejected with `E-AUTHZ-001`/403, regardless of client-side state. |
| FR-001-011 (audit logging) | *(no dedicated AC — gap noted)* | Every Brand/Model/Variant/ValuationMaster write produces exactly one `audit_logs` entry with correct old/new values and actor. |
| FR-001-012 (concurrency) | AC-001-007 | A `ValuationMaster` write with a stale `previousVersionUpdatedAt` is rejected with `409`, no partial write. |
| FR-001-013 (no Year filtering) | AC-001-008 | `/vehicles/brands`/`/models`/`/variants` called with any `year` param returns the same result as without it. |

Three FRs (FR-001-001/002/003) and two more (FR-001-006/007, FR-001-011)
have no dedicated Acceptance Criterion in FS-001 — test cases above are
inferred directly from the FR text itself. Recommend a small FS-001
revision to add the missing ACs for full traceability; not done here
(out of this document's scope, and FS-001 itself is unmodified per this
prompt's constraint).

---

## Open Questions

Carried from FS-001 (still unresolved, restated only by reference, not
re-litigated) plus two new ones surfaced by implementation-level detail:

1–5. FS-001's original five (SDD-000 §4 vs. DDD-001/DBD-001/SSD-001
   drift on Repair Master ownership; Free-tier catalog visibility;
   field length/Year range — **this document proposes defaults for
   these in §6, pending confirmation**; catalog-deactivation cascade
   behavior; Brand/Model/Variant concurrency policy scope).
6. **Flutter state-management library** — BLoC, Provider, Riverpod, or
   other is not decided anywhere. Needed before Flutter implementation
   of any of the three screens in §5 begins.
7. **`/admin/vehicles` entityType-discriminator design** — this
   document's resolution of API-001's single shared endpoint into one
   discriminated contract is an ISP-level interpretation, not something
   API-001 itself specifies. Recommend reflecting this back into a
   future API-001 revision for clarity, once confirmed.
