# DBD-001 — Database Design Document

| Field | Value |
|---|---|
| Document ID | DBD-001 |
| Version | 1.1 |
| Status | Approved |
| Owner | Database Architect |
| Reviewer | Architecture AI |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | BRD-001, BRR-001, BUS-0004, NS-001, data-dictionary/README.md, AI-0005, ABL-001 |
| Next Documents | API-001, per-entity `DD-<Entity>.md` files (extending DD-Vehicle) |

Canonical schema adopted per BUS-0004. Confirms and supersedes IPS-001
§5's schema sketch where they differ (notably: no separate `status` enum
— see §5 below). **v1.1 (ABL-001, 2026-08-02):** propagated `SEC-0001`,
`ENG-0003`, `ARC-0008`, `ARC-0009`, and `SEC-0002` from the now-Approved
`AI-0005` decision batch — see §2 (Authentication, Valuation Master,
Payments) and §6a (new).

## 1. Philosophy

Configuration-driven, not hardcoded: MSP, Margin, repair costs, and
scrap values live in the database so business changes never require a
code release. UUID primary keys throughout (not integers) — harder to
guess, better for distributed/public APIs.

## 2. Core Tables

### Authentication

- **users**: id (UUID), mobile, email, name, business_name, city, state,
  status, **role** (enum: `dealer` | `super_admin`, per `SEC-0001` —
  resolves DDD-001 §12.2/SSD-001 §9.5; a boolean `is_super_admin` was
  the documented alternative but a `role` enum reads more clearly and
  costs nothing extra for exactly two roles), created_at, updated_at.
- **devices**: id, user_id (FK), device_id, device_name, platform,
  last_login.

### Subscription

- **plans**: id, name, duration_days, ads_enabled, model_limit, active.
- **subscriptions**: id, user_id (FK), plan_id (FK), start_date,
  expiry_date, status.

### Payments

- **payments**: id, user_id (FK), subscription_id (FK), gateway,
  transaction_id, amount, payment_status, paid_on.

`transaction_id` (the gateway's own ID) carries a **unique constraint**
— the webhook-dedup principle from `SEC-0002` (`AI-0005`): a redelivered
webhook for the same `transaction_id` is a no-op, not a duplicate
activation. Detailed reconciliation design (polling for lost webhooks)
remains deferred to FS-006, per `SEC-0002`'s own scope.

### Vehicle Master

- **brands**: id, brand_name, active.
- **models**: id, brand_id (FK), model_name, active.
- **variants**: id, model_id (FK), variant_name, active.

(Resolves BDR-0005 — confirmed normalized decomposition, not a single
denormalized table.)

**No `vehicles` table in v1** (confirms `ARC-0008`, `AI-0005`): a
Vehicle selection (Year+Brand+Model+Variant) is request-scoped/ephemeral
only — resolved DDD-001 §12.1. A snapshot is persisted only once
`valuation_requests` (v2, below) is activated.

### Valuation Master

- **valuation_master**: id, year, variant_id (FK), minimum_selling_price,
  margin, scrap_value, active, effective_from, effective_to,
  **updated_at** (used as the optimistic-concurrency check value, per
  `ENG-0003`).

One row per Year+Variant, enforced as a unique constraint on
(year, variant_id) — formalized as **`BR-0011`** per `BUS-0006`
(`AI-0005`; see BRR-001 v1.2). This is the business IP table — replaces
the dealer's Excel model.

### Repair Module

**Amended by `AI-0011` (IMP-003, 2026-08-02)** — see that decision for
full context. The real 2W Valuation Calc spreadsheet showed repair
deduction amounts vary per Year+Variant, not globally per option; a
purely global `repair_options.deduction_amount` could not hold that
data losslessly.

- **repair_components**: id, name (Engine, Colour, Gearbox, Tyre,
  Plastic, Clutch, Shock/Fork [added `AI-0011`], Battery [future],
  Accessories [future]).
- **repair_options**: id, repair_component_id (FK), option_name (OK/
  Partial/Full) — **pure catalog identity only as of `AI-0011`; no
  longer carries `deduction_amount`.**
- **valuation_repair_costs** (new, `AI-0011`): id, valuation_master_id
  (FK, CASCADE), repair_option_id (FK, RESTRICT), deduction_amount
  (fixed ₹, confirms BR-0010/ADR-018), unique on (valuation_master_id,
  repair_option_id). Scopes the deduction amount to one Year+Variant
  pricing version, exactly like `minimum_selling_price`/`margin`. No
  separate versioning mechanism - a superseded `valuation_master` row
  keeps its own historical `valuation_repair_costs` rows untouched.

Sibling to Vehicle Master, not nested inside it (resolves BDR-0001 —
both are Admin-owned modules, Vehicle Master owns catalog+pricing,
Repair Cost Master owns repair-specific deductions).

**No `repair_assessments` table in v1** (confirms `ARC-0009`, `AI-0005`):
a Dealer's per-component repair selections are transient, submitted
directly in the `/valuation/calculate` request payload and never stored
independently — resolved DDD-001 §12.3.

### Valuation Requests (v2, disabled in v1)

- **valuation_requests**: id, user_id (FK), vehicle (Year/Brand/Model/
  Variant snapshot), deductions, recommendation, created_at.

Not written to in v1 (BR-0007's "corrections via re-opening" pattern
applies once this table is active in v2).

### Notifications (future)

Push / Email / SMS / WhatsApp — no schema finalized yet.

### System Settings

Key-value config: default scrap value, support number, app version,
maintenance mode, privacy policy, terms, ad settings.

### Audit Logs

who, when, old_value, new_value, ip_address — logs all Super Admin
master-data changes.

**Implemented `AI-0012` (IMP-003B, 2026-08-02):** `audit_logs` table
(`AuditLog` model) plus `actor_id`, `action`, `entity_type`, `entity_id`,
`correlation_id`, `request_id`, `success`, `error_message`. Placed
directly inside `vehicle_master` (not a separate `common/audit` app as
EP-001 §2 originally planned) - same pragmatic, minimal-footprint call
already made for `RepairComponent`/`RepairOption` in EP-002, flagged
again here rather than silently resolved. `PersistentAuditLogRepository`
replaces `NoOpAuditRepository` as `service_factory`'s default - every
Admin write path (HTTP and the IMP-003 importer) now creates a real
record. `correlation_id`/`request_id` are populated ambiently via
`audit_context.py` (Python `contextvars`) rather than by threading two
new parameters through eleven existing `VehicleMasterAdminService`
method signatures - zero existing call sites changed.

## 3. Entity Relationship Overview

```text
users ── subscriptions ── payments

brands ── models ── variants ── valuation_master

repair_components ── repair_options

valuation_requests (references users + vehicle selection, v2)

system_settings (standalone)
```

## 4. Primary Keys

UUID everywhere (ADR-010) — more secure, better for APIs and
distributed systems than sequential integers.

## 5. Status / Lifecycle Modeling (resolves BDR-0006, BDR-0011)

**No multi-value status enum.** Every table uses:

- `active` (boolean)
- `deleted_at` (nullable timestamp — soft delete)
- `deleted_by` (nullable FK to users)

No permanent deletes. This supersedes IPS-001 §5's proposed Postgres
enum/status-column approach and removes the need for a distinct
"Archived" state (§17.8/BDR-0011) — deprecation is just `active = false`
plus optional soft-delete.

## 6. Pricing Versioning (resolves BDR-0010)

`valuation_master` uses `effective_from` / `effective_to` / `active`
columns to keep historical pricing versions queryable — a new pricing
period is a new row, not an overwrite. This is the resolution for
"do in-place pricing edits need an audit/versioning trail" — yes, via
temporal columns, not a separate history table.

## 6a. Transaction & Concurrency Policy (resolves `ENG-0003`, `AI-0005`)

Every Admin write to `valuation_master` or `repair_options` (a new
pricing/deduction version, or the `effective_to` close of the
superseded row) and its corresponding `audit_logs` entry happen in
**one database transaction** — never as two separate writes that could
diverge (this was SSD-001 §9.6's open question; now resolved).

**Concurrency:** optimistic, not pessimistic. The write includes a
`WHERE updated_at = :last_seen_updated_at` guard; if zero rows match,
the write is rejected with a 409 Conflict (API-001 already reserves
this status code) and the Admin UI must reload the current row before
retrying. Pessimistic row-level locking was considered and rejected —
unnecessary lock contention for a low-write-volume table with no
concurrent-editor requirement in scope.

## 7. Indexes

Mobile, Brand, Model, Variant, Year, Subscription Status, Transaction
ID, Created Date.

## 8. Naming Standards (extends NS-001)

- Tables/columns: `snake_case` (e.g. `minimum_selling_price`).
- API objects: `camelCase`.
- Flutter models: `PascalCase`.

## 9. Recommended PostgreSQL Extensions

`uuid-ossp` (UUID generation), `pgcrypto`, `citext` (case-insensitive
email, if needed).

## 10. Security

Row-level validation in the application layer, ORM/prepared statements
(no raw SQL string interpolation), encrypted secrets outside the
database, automated backups, point-in-time recovery, audit trail for
all master-data changes.

## Open Items

- Recommendation-threshold storage remains a fixed constant (90/75/60%,
  confirmed final per `BUS-0005`), not an Admin-configurable value — no
  schema needed for this in v1; revisit only if a future decision makes
  thresholds configurable.
- `valuation_requests` schema is provisional (v2 feature, disabled in
  v1) and may change before it's activated.
