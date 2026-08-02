# API-001 — Endpoint Inventory

| Field | Value |
|---|---|
| Document ID | API-001 |
| Version | 1.1 |
| Status | Approved |
| Owner | Backend Architect |
| Reviewer | Architecture AI |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | API-000 (conventions), BRD-001, DBD-001, BUS-0004, AI-0005, ABL-001 |
| Next Documents | Per-module implementation |

Concrete endpoint inventory, following API-000's conventions (versioned
paths, response envelope, error structure). Adopted per BUS-0004. **v1.1
(ABL-001, 2026-08-02):** propagated `ARC-0007`, `ARC-0005`, `ENG-0002`,
`SEC-0002`, `SEC-0003`, `ENG-0004` from the now-Approved `AI-0005`
decision batch.

## Base URLs

- Dev: `https://dev-api.bikevaluator.com/api/v1/`
- Prod: `https://api.bikevaluator.com/api/v1/`

## Response Envelope

```json
{ "success": true, "message": "Success", "data": {} }
```

```json
{ "success": false, "message": "Validation Error", "errors": {} }
```

**Resolved (`ARC-0007`, `AI-0005`):** this shape is now the canonical
envelope for BIKEVALUATOR — API-000 v1.1 has been revised to match it.
This is no longer an open reconciliation item.

## Authentication

| Endpoint | Method | Purpose |
|---|---|---|
| `/auth/request-otp` | POST | Send OTP to mobile. Rate-limited per `SEC-0003` (`AI-0005`): max 3 resends/hour per mobile number; detailed throttling design deferred to FS-003. |
| `/auth/verify-otp` | POST | Verify OTP, issue JWT + subscription info |
| `/auth/logout` | POST | Invalidate session |

No refresh-token endpoint exists by design (`ENG-0004`, `AI-0005`): on
JWT expiry the client performs a full re-auth via `/auth/request-otp` →
`/auth/verify-otp` again — resolves SSD-001 §9.9.

## Vehicle Master

| Endpoint | Method | Purpose |
|---|---|---|
| `/vehicles/brands` | GET | List brands |
| `/vehicles/models?brand_id=` | GET | List models for a brand |
| `/vehicles/variants?model_id=` | GET | List variants for a model |
| `/vehicles/configuration?year=&brand=&model=&variant=` | GET | Returns MSP, Margin, Scrap, available repair options |

No Year-based filtering on `/vehicles/brands`, `/vehicles/models`, or
`/vehicles/variants` (`ARC-0005`, `AI-0005`): all Brands/Models/Variants
are listed regardless of Year; only `/vehicles/configuration` takes
`year` as an input, and only to select the matching `valuation_master`
row.

## Repairs

| Endpoint | Method | Purpose |
|---|---|---|
| `/repairs/components` | GET | List repair components + their options |

## Valuation (core)

| Endpoint | Method | Purpose |
|---|---|---|
| `/valuation/calculate` | POST | Computes Purchase Price (BR-0001/0002/0009), returns `recommended_price`, `rounded_price`, `label` |

Server-side processing order: load MSP → load Margin → load Repair
Costs → apply deductions → apply Scrap Rule → round to nearest ₹10
(BR-0009) — never performed client-side (ADR-005, ADR-014).

No idempotency key required (`ENG-0002`, `AI-0005`): this endpoint is
stateless in v1 (no writes to `valuation_requests`, which stays
inactive), so a retried request after a timeout is naturally safe —
resolves SSD-001 §9.1.

## Subscription

| Endpoint | Method | Purpose |
|---|---|---|
| `/subscription/current` | GET | Current plan |
| `/subscription/plans` | GET | Available plans |
| `/subscription/upgrade` | POST | Initiate upgrade |

## Payment

| Endpoint | Method | Purpose |
|---|---|---|
| `/payment/create-order` | POST | Create Razorpay order |
| `/payment/verify` | POST | Verify payment client-side |
| `/payment/webhook` | POST | Server-to-server: updates subscription/invoice/user status. Deduped by gateway `transaction_id` (`SEC-0002`, `AI-0005`, DBD-001 unique constraint) — a redelivered webhook is a no-op, not a duplicate activation. Reconciliation-polling design remains deferred to FS-006. |

## Advertisement

| Endpoint | Method | Purpose |
|---|---|---|
| `/advertisements` | GET | Ads for Free-tier users only |

## Profile

| Endpoint | Method | Purpose |
|---|---|---|
| `/profile` | GET / PUT | Read/update dealer profile |

## Admin (Super Admin only)

| Endpoint | Method | Purpose |
|---|---|---|
| `/admin/vehicles` | GET/POST | List/create Brand/Model/Variant/pricing |
| `/admin/vehicles/{id}` | PUT/DELETE | Update/deactivate |
| `/admin/repair-components` | CRUD | Manage repair components/options |
| `/admin/valuation-master` | CRUD | Manage MSP/Margin/Scrap |
| `/admin/subscriptions` | CRUD | Manage dealer subscriptions |
| `/admin/users` | CRUD | Manage dealer accounts |

## HTTP Status Codes

`200` Success · `201` Created · `400` Validation Error · `401`
Unauthorized · `403` Forbidden · `404` Not Found · `409` Conflict ·
`422` Business Rule Error · `500` Server Error.

## Error Codes (extends SDD-000 §8's catalogue)

| Code | Meaning |
|---|---|
| AUTH001 | OTP Invalid |
| AUTH002 | Token Expired |
| VAL001 | Vehicle Not Found |
| VAL002 | Variant Missing |
| VAL003 | Business Rule Missing (no pricing for the selected Variant+Year — analogous to E-PRICING-001) |
| SUB001 | Subscription Expired (analogous to E-SUB-001) |
| PAY001 | Payment Failed |

## Security

JWT-protected, HTTPS-only, rate-limited, input-validated, SQL-injection/
XSS-safe, CSRF-safe where applicable. Business logic never resides in
the mobile client (ADR-005).

## Open Items

- ~~Reconcile this document's response envelope with API-000's `data`/
  `meta`/`errors` shape~~ — resolved via `ARC-0007`; API-000 v1.1 now
  matches this document.
- ~~E-AUTHZ-001 formalization~~ — resolved via `ARC-0006`; now in
  SDD-000 §8's Error Catalogue.
- None remaining from `AI-0005` propagation. `BUS-0006`/`BR-0011`
  (ValuationMaster Year+Variant uniqueness) is a DBD-001/BRR-001 concern
  only, no endpoint change needed.
