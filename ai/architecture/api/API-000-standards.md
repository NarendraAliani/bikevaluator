# API-000 — API Naming & Engineering Standards

| Field | Value |
|---|---|
| Document ID | API-000 |
| Version | 1.1 |
| Status | Approved |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | SDD-000 (§8 Error Catalogue), BRR-001, API-001, AI-0005, ABL-001 |
| Next Documents | API-001 (Vehicle Master), API-002 (Valuation Engine) — endpoints, not standards |

Standards every future API document must follow. This document defines
**conventions**, not endpoints — no endpoint is designed here. **v1.1
(ABL-001, 2026-08-02):** §3/§4/§6 revised per `ARC-0007` (`AI-0005`) —
the response envelope now matches API-001's concrete, architect-supplied
shape rather than the other way around.

## 1. Versioning

All endpoints are prefixed `/api/v1/...`. A breaking change requires a
new version prefix (`/api/v2/...`); the old version is deprecated, not
silently changed.

## 2. URL Conventions

- Plural nouns for collections: `/api/v1/vehicles`, not `/api/v1/vehicle`.
- Nested resources reflect ownership from SDD-000 §4 Module Boundaries,
  e.g. `/api/v1/evaluations/{id}/repair-components`.
- kebab-case for multi-word path segments.

## 3. Response Envelope (revised per `ARC-0007`, `AI-0005`)

```json
{ "success": true, "message": "Success", "data": {} }
```

```json
{ "success": false, "message": "Validation Error", "errors": {} }
```

`success` is a boolean discriminator; `data` is present (and `errors`
omitted) on success, `errors` is present (and `data` omitted) on
failure. This supersedes the earlier `data`/`meta`/`errors` shape — that
draft was superseded before any endpoint was built against it, so no
migration is needed.

## 4. Error Response Structure

```json
{
  "success": false,
  "message": "Validation Error",
  "errors": [
    { "code": "E-PRICING-001", "message": "...", "field": null }
  ]
}
```

`code` values come from SDD-000 §8's Error Catalogue (E-PRICING-001,
E-CATALOG-001, E-CATALOG-002, E-SUB-001, E-NET-001, E-DEALER-001,
E-AUTHZ-001, and future additions) — the error catalogue is the source
of truth, this API standard just fixes the wire format.

## 5. Validation Error Structure

Validation errors use the same `errors` array with `field` populated:

```json
{ "code": "E-VALIDATION-001", "message": "MSP is required", "field": "msp" }
```

## 6. Pagination (revised per `ARC-0007`, `AI-0005`)

Cursor-based: `?cursor=<opaque>&limit=<n>` (default `limit`: 25, max:
100). Since the envelope (§3) has no `meta` field, pagination state
nests inside `data`: `data.items` (the page) and `data.next_cursor`
(null when exhausted).

## 7. Date & Time Format

ISO 8601, UTC, e.g. `2026-08-02T00:00:00Z` — matches SDD-000 §7 (all
timestamps stored UTC; client converts for display).

## 8. Authentication

Out of scope until FS-003 (Authentication) — this document only
reserves the convention: bearer token in `Authorization: Bearer <token>`.

## Open Items

- Rate limiting, CORS policy, and API key management deferred to a
  GOV/SEC document once the Authentication module (FS-003) is scoped.
