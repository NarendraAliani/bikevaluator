# LOG-001 — Logging Standards

| Field | Value |
|---|---|
| Document ID | LOG-001 |
| Version | 1.0 |
| Status | Needs Review |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | SDD-000 (§7 NFR — Audit logging), SEC-001 |
| Next Documents | Logging implementation (per-module, once FS-001 begins) |

Standards for application logging and audit trails. No implementation
yet.

## Log Levels

- `DEBUG`: development-only detail, never enabled in production.
- `INFO`: normal operational events (Evaluation state transitions).
- `WARNING`: recoverable anomalies (e.g. E-NET-001 retry).
- `ERROR`: failed operations requiring attention.
- `AUDIT`: a distinct, non-suppressible level for anything SDD-000 §7
  marks "Audit Required" (Admin pricing edits, Calculation Results,
  including superseded ones from re-opened Evaluations).

## Structured Logging

- All logs are structured (JSON), not freeform strings — minimum fields:
  `timestamp` (UTC, per NS-001), `level`, `module` (per SDD-000 §4
  ownership), `message`, `correlation_id` (see API-000's future
  Correlation ID addition).

## What Must Never Be Logged

- Dealer PII beyond what's needed for the audit trail itself (aligns
  with the Data Dictionary's PII flag — see `DD-Vehicle.md` and future
  `DD-Dealer.md`).
- Credentials, tokens, or secrets, ever, at any log level.

## Retention

- Audit-level logs: retained indefinitely (or per a future OPS decision
  on backup/retention policy — SDD-000 §7 flags this as still open).
- Standard operational logs: retention period deferred to an OPS
  decision once hosting is chosen.

## Open Items

- Exact log aggregation/observability tooling deferred to FS-001
  implementation kickoff — not blocking approval of this document.
