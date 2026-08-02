# Branching Strategy — BIKEVALUATOR

Operational standard, not a constitutional rule.

## Proposed (not yet in force — single-branch repository today)

- `main` — always deployable.
- `feature/<module>-<short-desc>` — one branch per FS implementation
  (e.g. `feature/vehicle-master-catalog`).
- No long-lived environment branches until a release cadence exists
  (see `release-policy.md`).

## Open Items

- This strategy activates once FS-001 implementation begins and more
  than a single working branch is needed — not binding while the
  repository holds only architecture documents.
