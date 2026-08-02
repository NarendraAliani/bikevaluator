# Context — BIKEVALUATOR

**This is the first file every AI session must read.**

**Last update:** 2026-08-02T22:15

## Current Phase

**IMP-003B (Engineering Stabilization Release) — final completion pass
done.** Full 8-scenario Flutter emulator walkthrough completed (with
screenshots); 100/1,000-row importer benchmarks re-measured cleanly;
the 10,000-row benchmark run to completion in the background (see
`docs/importer-README.md` for the figure); one leftover doc-drift item
fixed; developer documentation split into 6 guides; a standalone Manual
QA Checklist created. Vehicle Master, Valuation Engine, the real-data
importer, and the Flutter
client bootstrap are all considered stable and ready for the architect
to freeze as the project's foundation. Future modules (FS-003
Authentication, FS-004 Admin, Dealer Portal, Subscription, Payments)
are expected to build on top of this baseline rather than modify it,
per the architect's own stated intent.

## How we got here (chronological, most recent last)

1. **IMP-001A-D**: Vehicle Master backend foundation, service-layer
   business logic, REST API, architecture refinement. Reviewed 9.6/10,
   approved, considered stable.
2. **FS-002 → ISP-002 → EP-002 → IMP-002**: Valuation Engine
   functional spec, implementation spec, engineering package, and full
   implementation (backend + first Flutter client, `mobile/
   bikevaluator_app`). End-to-end validated on the Android emulator.
3. **IMP-003**: imported the architect-supplied real "2W Valuation
   Calc" spreadsheet (86 vehicle/year rows) into the database. Along
   the way, discovered repair deduction amounts vary per Brand/Model/
   Variant/Year - contradicting DBD-001 §9's original global
   `repair_options.deduction_amount` design. Surfaced via
   `AskUserQuestion` **before writing any import code**; architect chose
   to scope costs per vehicle. Recorded as **`AI-0011`**, amending
   DBD-001 §9/BR-0010. New `ValuationRepairCost` table, new idempotent/
   transactional `import_valuation_master` management command.
4. **IMP-003A**: architect-approved CTO-grade review of everything in
   IMP-002/IMP-003. Found the core decision (vehicle-scoped costs) was
   handled correctly, but flagged 2 High Priority and several Medium/
   Low Priority engineering-quality gaps (stale API-001/ISP-002/EP-002
   docs, no real audit trail, N+1 queries, a redundant DB index,
   importer robustness gaps).
5. **IMP-003B** (this round): closed every High Priority finding and
   the cheap Medium ones. New real, persistent `AuditLogRepository`
   (recorded as **`AI-0012`**, amending DBD-001 §2); N+1 queries fixed
   in `ValuationService`; redundant index removed; importer hardened
   (encoding fallback, thousands-separator tolerance, progress
   reporting, structured `logging`); Flutter `ApiClient` centralized
   with a request timeout and network/timeout/server/validation error
   differentiation; API-001/ISP-002/EP-002 brought back in sync with
   the actual `/repairs/components` contract; new tests throughout
   (211 backend tests, 11 Flutter tests, all passing).

## Known, deliberately-carried-forward gaps (not fixed by design)

- **FS-003 (Authentication) doesn't exist.** The Flutter app starts
  pre-authenticated via the backend's `DummyActorProvider` header
  mechanism (`X-Actor-Id`/`X-Actor-Role`). This is the single largest
  remaining structural gap in the whole project.
- **FS-004 (Admin) doesn't exist** for Repair Component/Option/Cost
  administration - the importer is currently the only way to write
  that data, and it temporarily borrows write methods on
  `RepairComponentRepository`/`RepairOptionRepository` that were
  documented as read-only for every Dealer-facing view.
- The Audit module lives inside `vehicle_master`, not the separate
  `common/audit` Django app EP-001 §2 originally planned - flagged
  twice now (IMP-002/EP-002's RepairComponent precedent, IMP-003B's
  AuditLog), not yet acted on.
- The importer has no bulk-write path - fine for the real ~86-row
  spreadsheet, would need work before a much larger file (see
  `docs/importer-README.md`'s benchmark table).

## Next Action

Awaiting the architect's decision to officially freeze this baseline
(Architecture + Vehicle Master + Valuation Engine + Data Import +
Flutter Client Bootstrap). Once frozen, the next module is expected to
be FS-003 (Authentication) or FS-004 (Admin) - either would resolve one
of the gaps listed above.
