# Developer Guide — 2W Valuation Master Importer

See [importer-README.md](importer-README.md) for the index.

## Prerequisites

- Migrations applied: `python manage.py migrate`
- The CSV file present at `data/imports/2w-valuation-calc.csv` (or pass
  `--file` to point at a different path)

## Example commands

```bash
# Preview what would happen, without writing anything:
python manage.py import_valuation_master --dry-run

# Run for real, using the default file:
python manage.py import_valuation_master

# Run against a different file:
python manage.py import_valuation_master --file=/path/to/other.csv
```

## What it does, per row

1. Validates Year, Brand, Model, Variant, and all 12 numeric columns
   (MinSellingPrice, Margin, 10 repair-expense columns). Thousands
   separators (`"45,000"`) are tolerated.
2. Looks up (or creates) the Brand/Model/Variant via the same
   `VehicleMasterAdminService` a real Super Admin API call would use —
   BR-0004 authorization, BR-0011 duplicate detection, and a real audit
   trail all apply exactly as they would over HTTP (IMP-003B).
3. Looks up the current Active `ValuationMaster` for that Year+Variant:
   - **Doesn't exist** → creates the first version.
   - **Exists, values identical** → no-op ("unchanged" in the summary).
   - **Exists, values differ** → creates a new version (BR-0007 — the
     old row is closed, never overwritten in place).
4. Upserts a `ValuationRepairCost` row for each of the 10 repair columns
   against that `ValuationMaster`.

Every row runs in its own database transaction — one bad row cannot
roll back rows already imported earlier in the same run. Progress is
logged every 500 rows, and every run (start, completion, per-row
failures) goes through Python's `logging` module (logger
`vehicle_master.import`, see `settings.LOGGING` — console +
`logs/import.log`), not `stdout` alone.

## Architecture notes

- Repair costs are scoped **per Year+Variant** (`ValuationRepairCost`),
  not global per option — this was a real DBD-001 §9 amendment
  (`AI-0011`), not an implementation detail. See `ai/decisions/
  decisions.md`.
- The importer acts as a system Actor (`role="super_admin"`) since
  FS-003 (Authentication) doesn't exist yet — every write still goes
  through the real service layer, never a raw ORM bypass.
- `correlation_id`/`request_id` are set once per run via
  `audit_context.audit_run_context` (Python `contextvars`) — every
  audit row from one run shares one `correlation_id`.

## Known limitations

- **No bulk writes** — each row does its own lookups/creates (~114
  queries/row, measured). Fine for the current ~86-row file; would need
  `bulk_create`/batching before being used on a file with tens of
  thousands of rows.
- **No `.xlsx` support** — only CSV. Export your spreadsheet as CSV
  first.
- **Encoding fallback** only tries UTF-8 (with/without BOM) and
  Windows-1252 — a file saved in another encoding will fail to read
  entirely (whole-file failure, not per-row).
- **Concurrency**: no database-level unique constraint protects against
  two simultaneous importer runs (or an importer run racing a real
  Admin API write) creating duplicate Brand/Model/Variant rows — don't
  run two imports against the same database at the same time.
