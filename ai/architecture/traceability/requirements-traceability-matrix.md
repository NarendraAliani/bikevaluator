# Requirements Traceability Matrix — BIKEVALUATOR

Every requirement must be traceable: **Decision → Functional Spec →
Entity → Database Table → API → Screen → Test Case**. Update this file
whenever a new FS document, entity, API, or screen is added — this is a
mandatory sync target alongside the files listed in Constitution Rule 15.

## Cross-Reference Matrix (FS-000 section → ownership)

| FS-000 Section | Future Module (Roadmap) | API | Database | UI Screen | Owner (Agent) |
|---|---|---|---|---|---|
| §1 Terminology | All | — | — | — | documenter |
| §2 Valuation Flow | Vehicle Master, Valuation Engine | Vehicle Master API, Valuation API | vehicle_master, evaluation | Vehicle Selector, Repair Inspection, Valuation Result | architect |
| §3 Repair Components | Valuation Engine | Valuation API | repair_component_assessment | Repair Inspection | backend |
| §4 Business Rules (Purchase Price) | Valuation Engine | Valuation API (Calculation) | calculation_result | Valuation Result | backend |
| §5 Recommendation Rules | Valuation Engine | Valuation API (Recommendation) | recommendation | Valuation Result | backend |
| §6 DB Mapping | Vehicle Master, Valuation Engine | — | vehicle_master, evaluation, calculation_result | — | database |
| §7 API Mapping | Vehicle Master, Valuation Engine | Vehicle Master API, Valuation API | — | — | architect |
| §8 UI Mapping | Flutter client | — | — | Vehicle Selector, Repair Inspection, Valuation Result, Valuation Report | flutter |
| §9 Future Scope | Deferred (Phase 3) | — | — | — | architect |
| §10 Acceptance Criteria | Valuation Engine | Valuation API | calculation_result, recommendation | Valuation Result | tester |

## Requirement Traceability Matrix

| Req ID | Business Rule | Entity | DB Table | API | UI Screen | Test Case |
|---|---|---|---|---|---|---|
| REQ-0001 | Purchase Price = MSP − Margin − Repair Costs (FS-000 §4.1) | Calculation Result | calculation_result | Valuation API `/calculate` | Valuation Result | AC-1, AC-2 (FS-000 §10) |
| REQ-0002 | Purchase Price floors at Scrap Value (FS-000 §4.1) | Calculation Result | calculation_result | Valuation API `/calculate` | Valuation Result | AC-3 |
| REQ-0003 | Recommendation banding at 90/75/60% (FS-000 §5, provisional) | Recommendation | recommendation | Valuation API `/recommend` | Valuation Result | AC-4 |
| REQ-0004 | Evaluation blocked without Active Vehicle Master pricing (FS-000 AC-5, SDD-000 §6.3) | Evaluation, Vehicle Master Record | evaluation, vehicle_master | Vehicle Master API `/pricing`, Valuation API | Vehicle Selector | AC-5 |
| REQ-0005 | MSP/Margin/Scrap Value editable only by Admin (FS-000 §6, SDD-000 §6.1) | Vehicle Master Record | vehicle_master | Vehicle Master API (Admin-only endpoints) | Admin Pricing screen | TBD (pending FS-001) |
| REQ-0006 | Calculation Results immutable; re-open creates new result (SDD-000 §6.5) | Calculation Result | calculation_result | Valuation API `/calculate` | Valuation Result | TBD (pending FS-002) |
| REQ-0007 | Expired Subscription blocks new Evaluation (SDD-000 §6.4, Error E-SUB-001) | Dealer, Subscription | dealer, subscription | Evaluation API | Vehicle Selector (entry gate) | TBD (pending FS-005) |

Rows marked "TBD" will be completed as FS-001 (Vehicle Master), FS-002
(Valuation Engine), and later FS documents lock down concrete schema/API/
UI details. This matrix is additive-only — do not delete a row once a
requirement exists; mark it superseded and link forward if it changes.
