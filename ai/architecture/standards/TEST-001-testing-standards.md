# TEST-001 — Testing Standards

| Field | Value |
|---|---|
| Document ID | TEST-001 |
| Version | 1.0 |
| Status | Needs Review |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | BRR-001, `ai/agents/tester.md`, requirements-traceability-matrix.md |
| Next Documents | Test suites (per-module, once FS-001 begins implementation) |

Standards for how BIKEVALUATOR is tested. No test code yet — conventions
only, so FS-001's implementation starts with a shared testing vocabulary.

## Test Levels

- **Unit:** individual business rule (BR-000x) calculations — e.g. a
  test per acceptance criterion in FS-000 §10 (AC-1 through AC-5).
- **Integration:** module boundary interactions (SDD-000 §4) — e.g.
  Valuation Engine correctly reading Vehicle Master pricing.
- **End-to-end:** full event flow (SDD-000 §5) — Dealer selects Variant
  through Report generation.

## Naming

- Test file/function names reference the Requirement ID or Business
  Rule ID they verify (e.g. `test_br_0002_scrap_value_floor`), per
  NS-001's ID conventions — keeps the requirements traceability matrix's
  "Test Case" column meaningful rather than freeform.

## Coverage Expectation

- Every acceptance criterion in an approved FS document must have at
  least one corresponding test before that FS's implementation is
  considered complete (ties to the requirements traceability matrix).

## Test Data

- No production dealer data in test fixtures — synthetic Vehicle Master
  records and Evaluations only.

## Open Items

- Specific framework choice (pytest, Flutter `test`/`flutter_test`)
  deferred to FS-001 implementation kickoff — not blocking approval of
  this standards document.
