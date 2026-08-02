# Testing Guide — 2W Valuation Master Importer

See [importer-README.md](importer-README.md) for the index.

## Running the existing tests

```bash
cd src
python manage.py test vehicle_master.tests.test_import_valuation_master
python manage.py test vehicle_master.tests.test_audit_logging
python manage.py test vehicle_master   # full backend suite (211 tests)
```

Flutter (network/timeout/error-category tests live in `api_client_test.dart`):

```bash
cd mobile/bikevaluator_app
flutter test
```

## What's already covered

- Idempotent re-runs (no duplicate Brand/Model/Variant/ValuationMaster)
- BR-0007 versioning (changed price → new version, not overwrite)
- Blank-row skipping vs. row failure
- Negative-amount validation rejection
- Dry-run persists nothing
- Thousands-separator tolerance (`"45,000"`)
- Windows-1252 encoding fallback
- Multi-batch progress reporting (patched `PROGRESS_INTERVAL` for speed)
- Sequential-reimport idempotency
- Audit row creation (persistence, action inference, ambient
  correlation_id/request_id, HTTP- and importer-driven writes)
- N+1 query regression guards (`assertNumQueries`) on
  `ValuationService.list_repair_components`/`calculate`
- Flutter: timeout, network/server/validation categorization,
  retry-recovery

## Writing a new importer test

Use `django.core.management.call_command` against a temporary CSV file
(see `test_import_valuation_master.py`'s `_write_csv`/`_run` helpers).
Each test should use its own `tempfile.TemporaryDirectory()` so tests
never share state via the filesystem. Prefer asserting on the printed
summary (`self.assertIn("...", output)`) *and* the actual database state
— the summary alone can't catch a bug where the printed count is right
but the wrong rows were touched.

## Benchmark / performance testing (not part of the automated suite)

The 100/1,000/10,000-row benchmarks in `importer-README.md` are run
manually against an **isolated** settings module pointing at a throwaway
SQLite file — never against the shared dev `db.sqlite3` or the real
Django test database. See `src/bikevaluator/benchmark_settings.py`
(created and deleted per benchmark run — not a permanent fixture) for
the pattern: import `from .settings import *` and override
`DATABASES["default"]["NAME"]`.

**Do not** run a large synthetic benchmark with `DEBUG=True` enabled —
Django's query-logging (`connection.queries`) accumulates in memory
across the whole run and causes a severe, misleading slowdown at
thousands of queries. Measure query *count* only on a small (~5-row)
sample with `DEBUG=True`, and measure *timing* separately with
`DEBUG=False` (the default).

## Manual/UI testing

See the project's Manual QA Checklist (delivered alongside each
IMP-003B completion report) for the full Dealer-journey walkthrough,
including the network/timeout/retry/validation-failure paths that
can't be exercised by an automated backend test alone.
