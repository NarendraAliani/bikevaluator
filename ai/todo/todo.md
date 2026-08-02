# To-Do — Index (BIKEVALUATOR)

As of AEP-002, TODOs are split by module under `ai/todo/modules/`:
`global.md`, `authentication.md`, `valuation.md`, `vehicle-master.md`,
`subscription.md`, `payment.md`, `admin.md`, `future.md`.

This file is now an index only — see `ai/todo/modules/global.md` for
cross-cutting/framework tasks (the successor to the original flat
`todo.md`). Use `ai/templates/todo-template.md` for new entries in any
module file.

**Vehicle Master** now has real, active tasks (IMP-001C code review,
two cross-module blockers) — no longer a placeholder; see
`ai/todo/modules/vehicle-master.md`. FS-001 is Approved and closed.
IMP-001A (Backend Foundation, 10/10 CTO-approved, frozen), IMP-001B
(Service-layer business logic, 91 tests), and IMP-001C (REST API
layer, 143 tests total) are complete at `src/`. All 8 Vehicle Master
endpoints are live over HTTP at `/api/v1/`.

**Valuation** now has real, active tasks (FS-002 drafted) — no longer a
placeholder; see `ai/todo/modules/valuation.md`.

| Module | File | Status |
|---|---|---|
| Global / Framework | `modules/global.md` | Active |
| Authentication | `modules/authentication.md` | Placeholder — no tasks yet |
| Valuation | `modules/valuation.md` | Active |
| Vehicle Master | `modules/vehicle-master.md` | Active |
| Subscription | `modules/subscription.md` | Placeholder — no tasks yet |
| Payment | `modules/payment.md` | Placeholder — no tasks yet |
| Admin | `modules/admin.md` | Placeholder — no tasks yet |
| Future | `modules/future.md` | Backlog / ideas not yet scheduled |
