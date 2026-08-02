# SSD-001 — Canonical System Sequence Diagrams (prompt record)

- **Prompt ID:** SSD-001
- **Version:** 1.0
- **Date:** 2026-08-02
- **Purpose:** Produce the canonical behavioral architecture — actors,
  Mermaid sequence diagrams for 8 major flows (Authentication, Vehicle
  Selection, Repair Assessment, Valuation, Subscription Validation,
  Payment, Vehicle Master Administration, Repair Master Administration),
  business events, state-synchronization authority model, failure
  scenarios, cross-cutting concerns, domain policy placeholders, and a
  traceability matrix — independent of implementation, API payload
  detail, or database schema.
- **Output expectation:** `ai/architecture/sequence/
  SSD-001-system-sequence-diagrams.md`. No Flutter/Django/SQL/REST
  implementation, no UI mockups.
- **Linked decisions:** None new — synthesis over already-approved
  DDD-001/BRD-001/DBD-001/API-001/BRR-001; 9 behavioral open questions
  surfaced (idempotency, concurrency, webhook reconciliation,
  authorization mechanism, transactionality, mid-flight expiry, OTP
  rate-limiting, session refresh), none assumed away. No conflicts
  between source documents found — only gaps.

## Revision history

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-02 | Initial version |
