# FS-000 — Core Domain & Valuation Business Specification

| Field | Value |
|---|---|
| Document ID | FS-000 |
| Version | 1.0 |
| Status | Approved |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | BUS-0001, BUS-0002, SDD-000, BRR-001, requirements-traceability-matrix.md |
| Next Documents | FS-001 (Vehicle Master) |

This document is the business DNA of BIKEVALUATOR. Every future module
(Vehicle Master, Authentication, Admin, Subscription, Payments, Reports)
must reference this specification rather than re-deriving business rules
independently.

## Product Summary

BIKEVALUATOR is a **B2B SaaS platform for used two-wheeler valuation**,
built for **dealers**. Its core function is to let a dealer select a
vehicle (year, brand, model, variant), record its condition, and receive
a data-driven **purchase price recommendation** backed by a centralized
pricing engine. Access is sold via subscription.

**Tech stack:** Flutter (client) + Django (backend) + PostgreSQL
(database).

---

## 1. Business Terminology

| Term | Definition |
|---|---|
| Dealer | The B2B customer/tenant using the platform to evaluate vehicles for purchase. |
| Vehicle | A specific used two-wheeler being evaluated, identified by Year + Brand + Model + Variant. |
| Brand | Manufacturer (e.g. Honda, Bajaj, TVS). |
| Model | A product line within a brand (e.g. Honda Activa). |
| Variant | A specific configuration of a model (e.g. Activa 125 Standard, Disc). |
| Year | Manufacturing year of the specific vehicle instance being evaluated. |
| MSP (Minimum Selling Price) | The baseline resale market price for a given Year+Brand+Model+Variant, maintained centrally. |
| Margin | The dealer's/platform's required profit buffer, subtracted from MSP to derive purchase price. |
| Purchase Price | The recommended price the dealer should pay to acquire the vehicle, after margin and repair deductions. |
| Scrap Value | The floor price — a vehicle is never valued below this, regardless of calculation. |
| Repair Cost | The estimated cost to bring a vehicle's inspected components up to sellable condition, deducted from MSP. |
| Recommendation | The categorical buy signal produced by the engine (Excellent/Good/Average Buy or Scrap) — see §5. |
| Good Buy / Average Buy / Scrap Buy | Specific recommendation tiers — see §5 for exact thresholds. |

---

## 2. Valuation Flow

```
Select Year
        ↓
Select Brand
        ↓
Select Model
        ↓
Select Variant
        ↓
Load MSP
        ↓
Load Margin
        ↓
Repair Inspection
        ↓
Calculation Engine
        ↓
Scrap Validation
        ↓
Recommendation
        ↓
Report
```

Each step depends on the Vehicle Master module (Year/Brand/Model/Variant
+ MSP/Margin data) being populated before the Valuation Engine can
function — this is why Vehicle Master precedes the Valuation Engine in
the roadmap.

---

## 3. Repair Components

Each component has a condition scale used during Repair Inspection. Scales
are intentionally coarse (2–3 states) to keep dealer data entry fast.

| Component | States | Notes |
|---|---|---|
| Engine | OK / Half / Full | "Half"/"Full" indicate partial vs. full rebuild cost. |
| Color (paint) | OK / Partial / Full | Full = complete repaint. |
| Tyres | OK / Replace | Binary — no partial state. |
| Gearbox | OK / Repair | Binary. |
| Clutch | OK / Repair | Binary. |
| Plastic (body panels) | OK / Partial / Full | Full = full panel replacement. |

**Future components (not in initial scope, see §9):** Battery, Chain Kit,
Suspension, Lights, Accessories. Each will need its own cost table once
added — do not hardcode the component list; the schema must support
adding components without a migration that breaks existing inspections
(see §6).

---

## 4. Business Rules

### 4.1 Purchase Price Calculation

```
Purchase Price = MSP − Margin − Repair Costs

if Purchase Price < Scrap Value:
    Purchase Price = Scrap Value
```

Repair Costs is the sum of the cost mapped to each component's inspected
state (an "OK" state costs 0; other states map to a cost figure
maintained centrally, analogous to MSP/Margin).

### 4.2 Open Questions on Business Rules (must be resolved before Valuation Engine implementation)

- Are Margin and per-component repair costs fixed values per
  Brand+Model+Variant, or configurable per dealer/region? (Assumption:
  centrally set, editable by Admin only — see §6.)
- Is Scrap Value itself derived (e.g. % of MSP) or independently
  maintained data? (Assumption: independently maintained per
  Brand+Model+Variant, editable by Admin.)

These are logged as open questions in `ai/context/context.md` and must be
answered — not assumed further — before FS-001 (Vehicle Master) locks its
schema.

---

## 5. Recommendation Rules

Recommendation is expressed as a percentage of MSP retained after margin
and repair deductions (`Purchase Price / MSP`), then bucketed:

| Score band | Recommendation |
|---|---|
| ≥ 90% | Excellent Buy |
| 75–89% | Good Buy |
| 60–74% | Average Buy |
| < 60% | Scrap |

**Thresholds are provisional** — flagged explicitly per the user's
instruction ("You can later decide the exact thresholds"). Do not treat
90/75/60 as final without a BUS-category decision confirming them.

---

## 6. Database Mapping

Each field in the domain must be classified along these axes before
Vehicle Master/Valuation Engine schema work begins. This table is a
starting scaffold — DBD documents (`ai/architecture/dbd/`) own the actual
schema.

| Field | Editable by Admin? | Visible to Dealer? | Visible in Report? | Mandatory? | Nullable? | Future Enhancement? |
|---|---|---|---|---|---|---|
| Brand | Yes | Yes | Yes | Yes | No | — |
| Model | Yes | Yes | Yes | Yes | No | — |
| Variant | Yes | Yes | Yes | Yes | No | — |
| Year | No (dealer selects at evaluation time) | Yes | Yes | Yes | No | — |
| MSP | Yes | No (backend only) | Derived only (via Purchase Price) | Yes | No | AI-assisted pricing (§9) |
| Margin | Yes | No | No | Yes | No | Per-dealer margin (§9, open question) |
| Scrap Value | Yes | No | No | Yes | No | — |
| Repair component states | No (dealer records at inspection time) | Yes | Yes | Yes | No | Additional components (battery, chain kit, suspension, lights, accessories) |
| Repair component costs | Yes | No | No | Yes | No | — |
| Recommendation | System-computed | Yes | Yes | Yes | No | Threshold tuning |
| Purchase Price | System-computed | Yes | Yes | Yes | No | — |

---

## 7. API Mapping

| Concern | Owning API (module) |
|---|---|
| Vehicle Master (Brand/Model/Variant/Year lookup) | Vehicle Master module |
| Pricing (MSP, Margin, Scrap Value) | Vehicle Master module (pricing sub-resource) |
| Repairs (component list, cost table) | Valuation Engine module |
| Calculation (Purchase Price derivation) | Valuation Engine module |
| Recommendation | Valuation Engine module |

Exact endpoint contracts belong in `ai/architecture/api/` once the
Vehicle Master and Valuation Engine FS documents are drafted — this
mapping only establishes ownership boundaries.

---

## 8. UI Mapping

| Screen | Owns |
|---|---|
| Vehicle Selector | Year, Brand, Model, Variant selection |
| Repair Inspection | Engine, Color, Tyres, Gearbox, Clutch, Plastic states |
| Valuation Result | Purchase Price, Recommendation |
| Valuation Report | Full read-only summary of all above, for sharing/export |

Detailed wireframes/UX flows belong in `ai/architecture/uxs/` once
drafted.

---

## 9. Future Scope

Explicitly out of scope for the initial Vehicle Master + Valuation Engine
build, but tracked so the schema/API aren't designed in a way that
blocks them later:

- AI-assisted pricing (dynamic MSP suggestions)
- OCR (registration certificate / document capture)
- VIN recognition
- Photo-based inspection
- Inventory management
- CRM
- Analytics

---

## 10. Acceptance Criteria

Every business rule above must have acceptance criteria before
implementation begins. Initial set (to be expanded per-module):

- **AC-1:** Given a Year+Brand+Model+Variant with MSP, Margin, and Scrap
  Value populated, and all repair components marked "OK", Purchase Price
  equals `MSP − Margin`.
- **AC-2:** Given the same vehicle with one or more repair components in
  a non-OK state, Purchase Price equals `MSP − Margin − sum(repair
  costs)`.
- **AC-3:** If the computed Purchase Price is less than Scrap Value, the
  displayed Purchase Price is Scrap Value, and the Recommendation is
  "Scrap" regardless of the score-band calculation.
- **AC-4:** Recommendation band is computed as `Purchase Price / MSP` and
  bucketed per §5's thresholds (pending threshold confirmation).
- **AC-5:** A vehicle with no MSP data for its Year+Brand+Model+Variant
  cannot proceed past the "Load MSP" step — the dealer sees an
  explicit "pricing not available" state, not a silent zero/default.

---

## Open Questions (block downstream FS documents)

1. Is Margin per-dealer/region-configurable, or global? (§4.2)
2. Is Scrap Value independently maintained or derived from MSP? (§4.2)
3. Final recommendation thresholds (currently provisional 90/75/60). (§5)

These must be resolved — via a BUS-category decision — before FS-001
(Vehicle Master) finalizes its schema.
