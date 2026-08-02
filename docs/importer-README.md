# 2W Valuation Master Importer — Documentation Index

`python manage.py import_valuation_master` loads the "2W Valuation Calc"
spreadsheet (`data/imports/2w-valuation-calc.csv`) into `ValuationMaster`
and `ValuationRepairCost`. It is idempotent, transactional per row, and
writes a real audit trail (`AuditLog`) for every Brand/Model/Variant/
ValuationMaster it touches — see IMP-003/IMP-003A/IMP-003B for full
background and the architecture decision (`AI-0011`) behind it.

This is the index. Full guides:

- **[Developer Guide](developer-guide.md)** — how the importer works,
  prerequisites, example commands, what happens per row.
- **[Troubleshooting Guide](troubleshooting-guide.md)** — symptom →
  cause → fix table for every known failure mode.
- **[Recovery Guide](recovery-guide.md)** — what to do if a run is
  interrupted, partially fails, or the database looks corrupted.
- **[Rollback Guide](rollback-guide.md)** — how to undo or correct a
  bad import without editing the database directly.
- **[Testing Guide](testing-guide.md)** — how to run the test suite
  relevant to the importer, and how to write a new test for it.

## Quick start

```bash
python manage.py migrate
python manage.py import_valuation_master --dry-run   # preview
python manage.py import_valuation_master             # run for real
```

## Expected execution time (measured, IMP-003B)

Measured against an isolated, freshly-migrated SQLite database (a real
disk-backed file, not Django's faster in-memory-style test database),
with every row a brand-new insert (worst case — no "unchanged" rows to
skip):

| Rows | Elapsed | Rows/sec | Method |
|---|---|---|---|
| 100 | 17.6s | 5.7 | Measured |
| 1,000 | 272.5s (~4.5 min) | 3.7 | Measured |
| 10,000 | 4,149.2s (~69.2 min) | 2.4 | **Measured** (run to completion as a background task, IMP-003B final completion pass — 0 failures, 100,000 `ValuationRepairCost` rows written) |

Note the per-row rate degrades somewhat as the table grows (5.7 → 3.7
→ 2.4 rows/sec) — consistent with the lack of bulk writes/indexed
lookups scaling linearly rather than staying flat. At 10,000 rows this
is over an hour; **do not run a file this large in an interactive
session you might need to close** (see the Recovery Guide).

Per-row query count (measured on a 5-row sample with query logging
enabled): **~114 queries/row** — confirms the importer has no bulk-write
path (see Known Limitations in the Developer Guide). This is fine for
the real ~86-row spreadsheet; expect a large synthetic file to take a
while.
