# Troubleshooting Guide — 2W Valuation Master Importer

See [importer-README.md](importer-README.md) for the index.

| Symptom | Likely cause | Fix |
|---|---|---|
| `CommandError: File not found` | Wrong `--file` path | Check the path; default is `data/imports/2w-valuation-calc.csv` relative to the repo root |
| A specific row fails with `"<field> is not a valid number"` | A non-numeric or malformed value in that column | Fix the source spreadsheet; re-run — already-imported rows are untouched |
| A row fails with `"Amount must be zero or greater"` | A negative number in an expense/price column | Fix the source data |
| Import runs but `Failed rows` > 0 | Check the printed `Failures:` list (also written to `logs/import.log`) — each entry names the row number and reason | Fix those specific source rows and re-run; already-succeeded rows are unaffected |
| Import looks "stuck" on a large file | It probably isn't — progress is logged every 500 rows (`... processed N rows`). Check `logs/import.log` for the latest progress line | Wait, or check the log file's last timestamp to estimate remaining time |
| `UnicodeDecodeError`-style file read failure | An encoding this importer doesn't try (only UTF-8 and Windows-1252 are attempted) | Re-save the CSV as UTF-8 |
| A cell like `"45,000"` fails to parse | Older versions of this importer didn't strip thousands separators | Update to the current version (IMP-003B) — this is now tolerated automatically |
| `python: can't open file 'manage.py'` | Not running from `src/` | `cd src` first, or use an absolute path to `manage.py` |
| Flutter app shows "No connection to the server" | Backend not running, or wrong base URL | Confirm `python manage.py runserver 0.0.0.0:8000` is running and reachable at `http://10.0.2.2:8000` from the Android emulator |
| Flutter app shows "The request took too long" | Backend reachable but slow/hung, or a genuine network black hole | Check backend logs; confirm the emulator's network path; the client times out after 15s by design (`kRequestTimeout`) |
| Flutter app shows "Pricing is not available for this vehicle/year yet." | No Active `ValuationMaster` for that Year+Variant (VAL003) | Run the importer for that data, or set pricing via `POST /admin/valuation-master` |

If none of these match, check `logs/import.log` for the full structured
log of the run, and the `Failures:` list printed at the end of the
command's own output.
