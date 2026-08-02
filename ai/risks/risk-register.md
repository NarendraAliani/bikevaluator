# Risk Register — BIKEVALUATOR

| Risk ID | Description | Category | Likelihood | Impact | Status | Mitigation | Related Decision |
|---|---|---|---|---|---|---|---|
| RISK-0001 | Domain of "BIKEVALUATOR" was undefined, risking wasted architecture work if assumed incorrectly | Business | — | High | Closed (2026-08-02) | Domain confirmed: dealer-focused B2B used two-wheeler valuation SaaS | BUS-0001 |
| RISK-0002 | Production tech stack (frontend/backend/mobile) was unconfirmed, risking rework of `src/` skeleton and architecture docs | Technical | — | Medium | Closed (2026-08-02) | Stack confirmed: Flutter + Django + PostgreSQL | BUS-0001 |
| RISK-0003 | Valuation business rules have unresolved open questions (Margin configurability, Scrap Value derivation, recommendation thresholds) that could be implemented incorrectly if guessed | Business | Medium | High | Open | Resolve via BUS decision before FS-001 (Vehicle Master) schema is finalized | BUS-0001 (FS-000 §4.2, §5) |
| RISK-0004 | Offline capability and multi-region/multi-currency requirements are unconfirmed, could affect Flutter client and data model design | Technical | Low | Medium | Open | Confirm before Flutter client architecture / FS-001 finalization | ARC-0002 (SDD-000 §9) |
