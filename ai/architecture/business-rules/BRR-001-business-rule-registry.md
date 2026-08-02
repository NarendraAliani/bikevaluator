# BRR-001 — Business Rule Registry

| Field | Value |
|---|---|
| Document ID | BRR-001 |
| Version | 1.2 |
| Status | Approved |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | FS-000, SDD-000, BUS-0001, BUS-0002, BUS-0003, NS-001, AI-0005, ABL-001 |
| Next Documents | FS-001 (Vehicle Master), FS-002 (Valuation Engine) |

Central registry of every business rule. Every FS/SDD/BRD document must
**reference** a rule by ID (`BR-000x`) rather than restating it — this is
the single source of truth, preventing rule drift across documents.

Approved per AR-001 (Architecture Review AR-001) with the revision
requested: added Category/Priority/Owner/Affected Modules columns and a
Business Rule Dependency Graph. **v1.2 (ABL-001, 2026-08-02):** `BR-0003`
moves from Provisional to Approved (thresholds confirmed final per
`BUS-0005`, `AI-0005`); `BR-0011` added per `BUS-0006` (`AI-0005`).

## Rule Index

| Rule ID | Category | Priority | Owner | Rule | Source | Affected Modules | Status |
|---|---|---|---|---|---|---|---|
| BR-0001 | Pricing | Critical | Valuation Engine | Purchase Price = MSP − Margin − Repair Cost | FS-000 §4.1, confirmed BRD-001 §7 | Valuation Engine | Approved |
| BR-0002 | Pricing | Critical | Valuation Engine | If Purchase Price < Scrap Value, Purchase Price = Scrap Value | FS-000 §4.1, SDD-000 §6.2, confirmed BRD-001 §7 | Valuation Engine | Approved |
| BR-0003 | Recommendation | Critical | Valuation Engine | Recommendation = band(Purchase Price / MSP): ≥90% Excellent, 75-89% Good, 60-74% Average, <60% Scrap | FS-000 §5, thresholds confirmed final per `BUS-0005` (`AI-0005`, ABL-001) | Valuation Engine, Reports | Approved |
| BR-0009 | Pricing | High | Valuation Engine | Final Purchase Price is rounded to the nearest ₹10 | BRD-001 §6, API-001 §9 | Valuation Engine | Approved |
| BR-0010 | Pricing | High | Repair Cost Master | Repair costs are fixed ₹ deduction amounts per option (OK/Partial/Full), never percentage-based | ADR-018, DBD-001 §9 | Repair Cost Master, Valuation Engine | Approved |
| BR-0004 | Access Control | High | Vehicle Master | MSP, Margin, and Scrap Value are editable only by Super Admin, never by Dealer (only two roles exist: Dealer, Super Admin) | FS-000 §6, SDD-000 §6.1, confirmed BRD-001 §8 | Vehicle Master, Admin | Approved |
| BR-0005 | Data Integrity | High | Valuation Engine | An Evaluation cannot enter Inspection state without a fully Active Vehicle Master Record | FS-000 AC-5, SDD-000 §6.3 | Vehicle Master, Valuation Engine | Approved |
| BR-0006 | Subscription | High | Subscription | A Dealer with an Expired Subscription cannot start a new Evaluation; existing Evaluations remain read-only viewable | SDD-000 §6.4, confirmed BRD-001 §10 | Subscription, Valuation Engine | Approved |
| BR-0007 | Data Integrity | Medium | Valuation Engine | Calculation Results are versioned via `effective_from`/`effective_to`/`active` fields rather than a separate history table; corrections happen by superseding, not editing in place | SDD-000 §6.5, resolved DBD-001 §21 | Valuation Engine | Approved |
| BR-0008 | Recommendation | Medium | Valuation Engine | Recommendation bands/thresholds are centrally defined (BR-0003); no module or screen may hardcode its own thresholds | SDD-000 §6.6 | Valuation Engine, Reports, Flutter client | Approved |
| BR-0011 | Data Integrity | Medium | Vehicle Master | Exactly one Active `ValuationMaster` record may exist per Year+Variant combination at any point in time | DBD-001 §2 (unique constraint), formalized per `BUS-0006` (`AI-0005`, ABL-001) | Vehicle Master, Valuation Engine | Approved |

## Business Rule Dependency Graph

```text
BR-0001 (Purchase Price formula)
   ├── BR-0002 (Scrap Value floor — applies after BR-0001 computes)
   ├── BR-0003 (Recommendation band — reads BR-0001's output)
   │      └── BR-0008 (centralized thresholds — BR-0003 must use these, not its own)
   ├── BR-0004 (Admin-only pricing inputs — feeds BR-0001's MSP/Margin/Scrap Value)
   └── BR-0005 (gates whether BR-0001 can even run)

BR-0006 (Subscription gate) — independent precondition, gates entry to the
   whole flow before BR-0001 is reached

BR-0007 (immutability) — applies to the *result* of BR-0001/BR-0002/BR-0003,
   not a computational dependency

BR-0011 (ValuationMaster uniqueness) — independent data-integrity constraint
   that guarantees BR-0001 always resolves to exactly one MSP/Margin/Scrap
   row for a given Year+Variant; not a computational dependency of BR-0001,
   but a precondition for BR-0001's inputs being unambiguous
```

**How to read this:** if BR-0001 changes (e.g. the formula itself), BR-0002,
BR-0003, BR-0004, and BR-0005 must all be re-verified, since each either
consumes BR-0001's output or gates its execution. If BR-0008's thresholds
change, only BR-0003 is directly affected. If BR-0011 were ever relaxed
(e.g. multiple concurrent ValuationMaster rows per Year+Variant allowed),
BR-0001 would need a tie-breaking rule to remain unambiguous.

## Open Items

- None. `BR-0003`'s exact numeric thresholds (90/75/60%) are now
  confirmed final per `BUS-0005` (`AI-0005`, ABL-001) — every rule in
  this registry is Approved.
- As FS-001 onward are drafted, new rules are appended here with the
  next sequential `BR-00xx` ID — never renumbered, only marked
  Superseded if replaced. New rules must also be added to the Dependency
  Graph.
