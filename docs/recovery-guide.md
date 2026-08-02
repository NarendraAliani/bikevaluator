# Recovery Guide — 2W Valuation Master Importer

See [importer-README.md](importer-README.md) for the index. For undoing
already-imported *data* (as opposed to recovering from a broken
process/database), see the [Rollback Guide](rollback-guide.md).

## A run is still in progress and you need to stop it

Prefer letting it finish if at all possible. If you must interrupt it,
use **Ctrl-C**, not a forced kill (`kill -9`, Task Manager "End Task",
or an automated tool timeout that force-terminates the process). A
forced kill mid-write can corrupt a SQLite database file — this is a
real, observed failure mode, not a theoretical one (see the incident
note below).

## Checking for corruption after an interrupted run

```bash
python -c "import sqlite3; print(sqlite3.connect('db.sqlite3').execute('PRAGMA integrity_check').fetchone())"
```

- If this prints `('ok',)`, the database is fine.
- If it prints anything else (e.g. `btreeInitPage() returns error
  code 11`), the file is corrupted. **Do not attempt to repair a
  corrupted SQLite file in place.** Restore from your most recent
  backup instead.

**This is exactly why DBD-001 mandates PostgreSQL for production** —
PostgreSQL's WAL-based durability does not have this failure mode; a
killed connection there simply loses its own uncommitted transaction,
it does not corrupt the on-disk file.

### Incident on record (IMP-003B)

During this project's own 10,000-row benchmark, a background process
running the importer was killed by an external tool timeout mid-write.
The working `db.sqlite3` was left corrupted (`PRAGMA integrity_check`
failed with `btreeInitPage()` errors on multiple pages). It was restored
cleanly from a pre-benchmark backup and confirmed healthy. No data was
lost because a backup existed — **always keep a recent backup before
running the importer against a database you care about**, exactly as
you would before any other bulk data operation.

## A run partially completed with some failed rows

Fix the source data for the failed rows only (see the `Failures:` list
printed at the end of the run, or `logs/import.log`) and re-run the
**same file**. The import is idempotent — already-succeeded rows are
simply reported as "unchanged" and skipped, not duplicated or
re-processed.

## Recommended safety practice before any large or unattended run

1. Back up the database file (SQLite) or take a snapshot (PostgreSQL).
2. Run with `--dry-run` first to confirm the file parses cleanly.
3. Run the real import in a way that survives your terminal closing
   (e.g. `nohup`, a background job, or a process supervisor) rather
   than an interactive shell you might need to Ctrl-C.
4. After completion, verify row counts against expectations (`ValuationMaster.objects.count()`, etc.) before trusting the run.
