# Rollback Guide — 2W Valuation Master Importer

See [importer-README.md](importer-README.md) for the index. For
recovering from a broken process/corrupted database, see the
[Recovery Guide](recovery-guide.md).

## There is no "undo import" command

Treat a bad import exactly like any other pricing correction — do
**not** edit the database directly (this bypasses BR-0004 authorization,
BR-0007 versioning, and the audit trail entirely, and is exactly the
kind of raw-ORM bypass this project's architecture deliberately avoids
everywhere else).

## To correct a wrong ValuationMaster (MSP/Margin/Scrap Value)

1. Fix the source CSV to the correct values.
2. Re-run the importer against that file.
3. Because the import is idempotent and versioned (BR-0007), this
   creates a **proper new `ValuationMaster` version** superseding the
   wrong one — the incorrect version is closed (`active=False`,
   `effective_to` set), not deleted. History is preserved, not erased.
4. Alternatively, use the existing `POST /admin/valuation-master`
   endpoint directly for a one-off correction (same versioning
   mechanics, no CSV file needed).

## To correct a wrong repair cost (`ValuationRepairCost`)

1. Fix the source CSV.
2. Re-run the importer. Repair costs are upserted
   (`update_or_create`) against the *current* `ValuationMaster` for
   that Year+Variant — the corrected amount simply overwrites the
   previous one for that `(valuation_master, repair_option)` pair.
   Unlike `ValuationMaster` itself, `ValuationRepairCost` has no
   independent version history (see the Developer Guide's Known
   Limitations) — the old amount is not retained once overwritten.

## To remove a wrongly-created Brand/Model/Variant

There is no soft-delete-via-importer path. Use the existing Admin API
(`DELETE /admin/vehicles/{id}?entityType=...`) which soft-deactivates
the entry (`active=False`) per DBD-001 §5's no-hard-delete policy —
never delete the row directly in the database.

## What "rollback" does *not* mean here

- It does not mean restoring a database backup to undo a *correct* but
  unwanted import — that would also discard any other legitimate writes
  that happened after the import ran. Prefer the correction path above.
- It does not mean deleting `AuditLog` rows for a bad import — the
  audit trail should remain intact regardless of whether the underlying
  data was later corrected; that is the point of an audit trail.
