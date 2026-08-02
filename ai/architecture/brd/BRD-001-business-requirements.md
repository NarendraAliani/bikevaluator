# BRD-001 — Business Requirements Document

| Field | Value |
|---|---|
| Document ID | BRD-001 |
| Version | 1.0 |
| Status | Approved |
| Owner | Product Owner (architect) |
| Reviewer | Architecture AI |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | FS-000, BUS-0004, BRR-001, SDD-001 (see DBD-001/API-001), UXS-001, PEP-001 |
| Next Documents | DBD-001, API-001 |

Canonical business requirements for BIKEVALUATOR, adopted per BUS-0004
from the architect-supplied external documentation set. Supersedes
FS-000 wherever the two differ; FS-000 remains valid where not
contradicted.

## 1. Project Vision

BIKEVALUATOR is a B2B SaaS platform that lets used two-wheeler dealers
instantly calculate a consistent purchase price using centrally
configurable business rules — a rule engine, not a market-price
predictor. Dealer valuation expertise, encoded as business rules, is the
platform's core intellectual property (per ADR-013).

## 2. Business Problem

Dealers face inconsistent buying prices, staff-dependent judgment, slow
response times, manual calculation, and difficulty updating changing
market prices. BIKEVALUATOR centralizes this into one rule engine.

## 3. Target Audience

- **Primary:** used two-wheeler dealers, showrooms, vehicle traders,
  franchise dealers.
- **Future:** multi-branch dealers, dealer chains, corporate networks.

## 4. Core Business Philosophy

Rule-based, not AI/predictive (v1). Every valuation follows dealer-
defined business rules held centrally, not client-side logic (ADR-005,
ADR-013).

## 5. Roles

Only two roles exist in v1:

- **Dealer** — runs valuations, views the final recommendation only
  (read-only for pricing internals).
- **Super Admin** — the only role that may edit MSP, Margin, Scrap
  Value, repair costs, or add vehicles (BR-0004). There is no separate
  intermediate "Admin" tier.

## 6. Valuation Flow

```text
Select Year → Select Brand → Select Model → Select Variant
   → Load Vehicle Configuration (MSP, Margin, Scrap, repair options)
   → Repair Cost Selection
   → Calculate Purchase Price
   → Apply Scrap Rule
   → Round to nearest ₹10 (BR-0009)
   → Display Final Recommended Buying Price
```

## 7. Business Rules (reference only — see BRR-001 for authoritative text)

- **BR-0001:** Purchase Price = MSP − Margin − Repair Cost.
- **BR-0002:** If result < Scrap Value, Final Price = Scrap Value.
- **BR-0009:** Final price rounds to the nearest ₹10.
- **BR-0010:** Repair costs are fixed ₹ amounts per option (OK/Partial/
  Full), never percentage-based (confirms ADR-018).
- Margin is global per Year+Variant, not per-dealer (resolves BDR-0002).
- Scrap Value is independently maintained, not derived from MSP
  (resolves BDR-0003).

## 8. Business Data Ownership & Visibility

Only Super Admin may update MSP, Margin, Repair Costs, Scrap Values, or
add vehicles/modify business rules. Dealers see the Final Recommended
Price only in v1; a future version may optionally expose MSP/Margin/
repair breakdown as read-only.

## 9. Subscription Model

- **Trial:** 30 days, full access, no ads.
- **Free:** limited vehicle database, ads enabled (post-trial default).
- **Pro:** full database, no ads, premium features.

## 10. Subscription Enforcement (BR-0006)

A Dealer with an expired subscription cannot start a new Evaluation;
existing evaluations remain read-only viewable.

## 11. Authentication

- **v1:** Mobile OTP login (ADR-009), JWT session tokens (ADR-008).
- **Future:** Google, Apple, email login (additive, no core auth model
  change required).
- Single user per subscription in v1; future device control supported.

## 12. Geographic Scope

India-wide, no city restriction, single currency (₹) — no multi-region/
multi-currency support in v1 (resolves BDR-0014).

## 13. Technology Stack

Flutter (Android/iOS/Web) + Django REST Framework + PostgreSQL + JWT/OTP
auth + Razorpay (payments) + Firebase Cloud Messaging (notifications,
future) + cloud object storage + cloud infrastructure deployment.

## 14. Development Philosophy

Business Rules First → Code Second → Database Driven → API First →
Modular Architecture → Future Ready → Documentation Before Development.

## Open Items

- Exact numeric recommendation thresholds (BR-0003) remain unconfirmed —
  only qualitative labels (Good Buy / Average / Scrap) are settled.
- Search threshold for the Vehicle Selector, and whether Brand/Model
  availability varies by Year, remain open (BDR-0007, BDR-0008).
