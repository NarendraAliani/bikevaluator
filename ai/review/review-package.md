# Review Package

## Prompt ID

IMP-003B — Engineering Stabilization Release (closes IMP-003A's findings)

## Files Created

1. `src/vehicle_master/models/audit_log.py` — `AuditLog` model.
2. `src/vehicle_master/migrations/0008_create_audit_logs.py`
3. `src/vehicle_master/audit_context.py` — ambient correlation_id/request_id (contextvars).
4. `src/vehicle_master/middleware.py` — `RequestIdMiddleware`.
5. `src/vehicle_master/repositories/persistent_audit_log_repository.py`
6. `src/vehicle_master/tests/test_audit_logging.py`
7. `docs/importer-README.md` — developer guide (Task 6).
8. Scratch/benchmark scripts (not committed — scratchpad only).

## Files Modified

1. `src/vehicle_master/models/valuation_repair_cost.py` (removed redundant index)
2. `src/vehicle_master/models/__init__.py`, `repositories/__init__.py`
3. `src/vehicle_master/repositories/audit_log_repository.py` (extended signature, backward-compatible)
4. `src/vehicle_master/repositories/noop_audit_log_repository.py` (matching signature)
5. `src/vehicle_master/repositories/valuation_repair_cost_repository.py` (`get_amounts` batched method)
6. `src/vehicle_master/repositories/repair_option_repository.py` (`get_active_by_components` batched method)
7. `src/vehicle_master/services/valuation_service.py` (N+1 fixes)
8. `src/vehicle_master/service_factory.py` (`PersistentAuditLogRepository` default)
9. `src/vehicle_master/management/commands/import_valuation_master.py` (encoding fallback, thousands separators, progress, structured logging, audit_run_context)
10. `src/bikevaluator/settings.py` (`MIDDLEWARE`, `LOGGING`)
11. `src/vehicle_master/tests/test_valuation_service.py`, `test_import_valuation_master.py` (new regression/robustness tests)
12. `mobile/bikevaluator_app/lib/core/api_client.dart`, `api_exception.dart` (timeout, singleton, error categories)
13. `mobile/bikevaluator_app/lib/features/**/presentation/screens/*.dart` (use `ApiClient.instance`, `userFriendlyMessage`)
14. `mobile/bikevaluator_app/test/core/api_client_test.dart` (timeout/network/server/validation/retry tests)
15. `ai/architecture/api/API-001-endpoints.md`, `ai/architecture/isp/ISP-002-...md`, `engineering/packages/EP-002-valuation-engine.md` (synced stale `/repairs/components` contract)
16. `ai/architecture/dbd/DBD-001-database-design.md` (§2 Audit Logs, `AI-0012`)
17. `ai/decisions/decisions.md` (`AI-0012`)
18. `ai/context/context.md`, `ai/session/session-state.md`, `ai/roadmap/roadmap.md`, `ai/todo/todo.md`, `ai/todo/modules/valuation.md`, `ai/changelog/changelog.md`, `ai/prompts/prompt-index.md`, `ai/history/prompt-history.md` — all synced, timestamped.

No Constitution amendment. One new decision (`AI-0012`) — a real,
persistent `AuditLogRepository`, additive-signature only, no existing
call site changed.

----------------------------------

## File Classification

### Category A — Architecture (always review)

- `ai/decisions/decisions.md` (`AI-0012`)
- `ai/architecture/dbd/DBD-001-database-design.md` (§2 amendment)

### Category B — Code (review as engineering work)

- Everything under `src/vehicle_master/` and `mobile/bikevaluator_app/lib/`.

### Category C — Operational (review only if materially changed)

- context, session-state, roadmap, todo files, changelog, prompt-index,
  prompt-history — routine sync, but larger than usual this round since
  several of these files had drifted stale across 2-3 prior rounds and
  were brought current here too.

----------------------------------

## Review Priority

🔴 Critical

- **`AI-0012` (real audit trail)** — confirm the additive-signature
  approach (five new optional kwargs on `AuditLogRepository.create()`,
  ambient `correlation_id`/`request_id` via `contextvars`) is
  acceptable, versus a more conventional (but more invasive) explicit
  parameter-threading approach.
- **Audit module still lives inside `vehicle_master`**, not the
  `common/audit` app EP-001 §2 planned. Flagged a second time now
  (first in EP-002/RepairComponent) — worth an explicit decision on
  whether to actually relocate it in a future prompt, or formally amend
  EP-001 §2 to accept the pragmatic in-module placement permanently.

🟠 Important

- The importer's 10,000-row benchmark was **not run to completion** in
  this environment — a background run got killed by a tool timeout
  mid-write, which corrupted the working SQLite file (cleanly restored
  from a pre-benchmark backup; confirmed healthy). The 10k figure in
  `docs/importer-README.md` is an **extrapolation** from the measured
  100/1000-row rates, not a direct measurement — worth knowing before
  relying on it for capacity planning.
- No bulk-write fix was made to the importer this round (it was Low
  Priority/"nice to have" in IMP-003A, not High) — still slow for large
  files; documented, not fixed.

🟡 Recommended

- N+1 query fixes in `ValuationService` — regression-guarded with
  `assertNumQueries`, straightforward to verify.
- Redundant index removal — one-line change, low risk.

🟢 Informational

- Flutter `ApiClient.instance` singleton, timeout, and error-category
  differentiation — additive, backward-compatible with existing tests.
- `docs/importer-README.md` — new developer-facing doc, not
  architecture.

----------------------------------

## Mandatory Human Review

⭐ `ai/decisions/decisions.md` `AI-0012` — the audit-repository decision
⭐ Whether to relocate the Audit module to `common/audit/` now or defer again
⭐ Whether the 10k-row importer benchmark should be re-attempted with a
  longer-lived process (outside this session's tool-timeout constraints)
  before being relied upon for capacity planning

----------------------------------

## Open Questions

Carried from IMP-003/IMP-003A (unchanged): Scrap Value defaulted to
Rs.0.00 for all 86 imported rows (no source column); no Login screen
(FS-003 doesn't exist); Flutter state management still `setState`-only.
New this round: whether the Audit module's in-`vehicle_master` location
should become permanent or still move to `common/audit/`.

## Known Issues / Conflicts

None found beyond what's already flagged above. All 211 backend + 11
Flutter tests pass; `manage.py check`/`makemigrations --check` clean;
E2E re-verified live on the Android emulator with real imported data.

## Architecture Impact

One new decision (`AI-0012`), amending DBD-001 §2 (Audit Logs). No
business rule changed. No API contract broken (the one breaking change,
`/repairs/components`, was already `AI-0011` from IMP-003 — this round
only synced the documentation that had gone stale describing it).

## Next Prompt Recommendation

Human reviews IMP-003B, decides on the Audit-module-location open
question, and then makes the freeze decision (Architecture + Vehicle
Master + Valuation Engine + Data Import + Flutter Client Bootstrap).
After freezing, the next module is expected to be FS-003
(Authentication) or FS-004 (Admin).
