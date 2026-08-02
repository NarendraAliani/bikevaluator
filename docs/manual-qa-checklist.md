# Manual QA Checklist — IMP-003B Final Completion

Last run: 2026-08-02T22:15

## Backend Tests

- [x] `python manage.py check` — clean
- [x] `python manage.py makemigrations --check --dry-run` — no drift
- [x] `python manage.py test vehicle_master` — **211/211 pass**

## Flutter Tests

- [x] `flutter clean` / `pub get` / `analyze` — clean, no issues
- [x] `flutter test` — **11/11 pass**

## Manual Tests (Android emulator, real imported data)

- [x] Vehicle Selection: Year → Brand → Model → Variant → Next
- [x] Repair Selection: vehicle-scoped costs displayed correctly (Honda
      Activa 6g 2022's real spreadsheet values)
- [x] Valuation Result: correct price and recommendation label (hand-
      verified against BR-0001/BR-0003 math)
- [x] Back navigation preserves prior selections at each screen
- [x] "Start New Valuation" returns to the root screen cleanly

## Regression Tests

- [x] Empty `repairAssessment` still accepted as valid (no repairs
      needed) — confirmed via a fresh valuation with zero selections
- [x] Vehicle-scoped `/repairs/components` still requires
      `year`/`variant_id` (IMP-003 contract, re-verified this round)
- [x] Retry after a network failure recovers cleanly, no stale error
      state left over

## Edge Cases

- [x] Year field cleared entirely — Next button correctly stays
      non-functional (verified: tap has no effect); **UX observation**:
      the disabled-button visual contrast is low against the enabled
      state on this theme — cosmetic, not functional, worth a future
      polish pass
- [x] Unpriced Year/Vehicle combination (2099) — VAL003 shown, distinct
      from a network error
- [x] Thousands-separator (`"45,000"`) and Windows-1252-encoded CSV
      files — both handled by the importer (automated tests)

## Negative Tests

- [x] Malformed `variantId` → HTTP 400, `VALIDATION_ERROR` (confirmed
      live via curl; Flutter client categorizes this as `validation`
      with a distinct message — automated test)
- [x] Missing required query param → HTTP 400 (confirmed live via curl)
- [x] Negative repair-cost amount in importer input → row fails
      validation, does not corrupt other rows (automated test)

## Acceptance Tests

- [x] A Dealer can complete a full valuation for a real, imported
      vehicle and receive a correct, recommendation-labeled price
- [x] An Admin write (via HTTP) leaves a real, queryable `AuditLog` row
      with a `request_id`
- [x] An importer run leaves `AuditLog` rows sharing one
      `correlation_id`
- [x] Re-running the importer against unchanged data is a true no-op
      (no duplicate rows, no new audit noise beyond what already exists)

## Production Smoke Tests

- [x] Backend boots cleanly (`manage.py runserver 0.0.0.0:8000`),
      reachable from the Android emulator at `10.0.2.2:8000`
- [x] Flutter app boots to the Vehicle Selector on a cold, forced-stop
      relaunch (not just a hot-reload)
- [x] A stopped backend surfaces a distinct, user-friendly "No
      connection to the server" message, not a crash or blank screen
- [x] A genuinely slow/unreachable endpoint surfaces a distinct "took
      too long" message after the configured timeout (verified live
      with a temporary black-hole address, reverted after)

## Known Gaps in This QA Pass

- Timeout/network scenarios required temporarily editing
  `kApiBaseUrl`/`kRequestTimeout` for a controlled test, since the
  emulator's default networking can't be made to hang on demand without
  it. Reverted immediately after capture; `git diff` confirmed clean.
- "API validation failure" and "Invalid input" were demonstrated via a
  combination of the app's own client-side constraints (which correctly
  prevent most malformed requests from ever being sent — a positive
  finding) and direct backend verification (curl) for the cases the UI
  itself won't let you construct.
