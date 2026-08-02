# NS-001 — Naming Standards

| Field | Value |
|---|---|
| Document ID | NS-001 |
| Version | 1.0 |
| Status | Needs Review |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | BRR-001, API-000, DD-Vehicle, all `ai/**` conventions |
| Next Documents | CSS-001, DOC-001, TEST-001, LOG-001, SEC-001 |

Single naming authority for BIKEVALUATOR. Where this document conflicts
with an existing file/folder already created, this document wins for all
**future** work; existing names are not force-renamed retroactively
(avoids destructive churn) — flag inconsistencies for a deliberate cleanup
decision instead.

## 1. Repository / Folder Naming

- Top-level process folders: lowercase, singular where the folder holds
  one kind of thing conceptually but plural content is fine
  (`ai/decisions/`, `ai/prompts/`) — matches existing convention, not
  changed.
- Category subfolders: lowercase-kebab (`ai/prompts/architecture/`,
  `ai/architecture/data-dictionary/`).

## 2. Files

- Markdown docs: `UPPER-KEBAB-ID-descriptive-title.md` for identified
  architecture documents (`FS-000-core-domain-valuation.md`,
  `NS-001-naming-standards.md`); plain `kebab-case.md` for non-ID
  documents (`business-glossary.md`, `roadmap.md`).

## 3. Markdown Structure

- H1 title matches the Document ID + title.
- Metadata table immediately follows the H1 (per
  `architecture-document-metadata-template.md`).
- Numbered `## N. Section Title` headers for structured specs (as used
  in FS-000, SDD-000).

## 4. Flutter (Dart)

- Classes/Types: `PascalCase` (e.g. `VehicleMasterRecord`).
- Variables/functions: `camelCase` (e.g. `purchasePrice`).
- Files: `snake_case.dart` (Dart/Flutter convention).
- Constants: `lowerCamelCase` with `k` prefix optional per Effective Dart
  (finalized in CSS-001).

## 5. Django / Python

- Modules/files: `snake_case.py`.
- Classes: `PascalCase`.
- Functions/variables: `snake_case`.
- Constants: `UPPER_SNAKE_CASE`.

## 6. PostgreSQL

- Tables: `snake_case`, singular (e.g. `vehicle`, `evaluation`,
  `vehicle_master_record`) — matches Entity Catalogue names
  lowercased/snake-cased.
- Columns: `snake_case` (e.g. `created_at`, `purchase_price`).
- Foreign keys: `<referenced_table>_id` (e.g. `evaluation_id`).
- Indexes: `idx_<table>_<column(s)>`.

## 7. API

- URL paths: `kebab-case` plural nouns (per API-000 §2).
- JSON field names: `camelCase` in request/response bodies (client-facing
  layer), translated from `snake_case` at the API boundary — this is the
  one deliberate case-convention boundary in the system, chosen so the
  Flutter client never has to convert casing.

## 8. Enums

- Enum type names: `PascalCase` (e.g. `EvaluationState`).
- Enum values: `UPPER_SNAKE_CASE` in Python/DB, `camelCase` in
  Dart/JSON — same boundary-translation rule as §7 (e.g. DB/Python
  `DRAFT` ↔ JSON/Dart `draft`).

## 9. Booleans

- Prefix with `is_`/`has_`/`can_` (e.g. `is_active`, `has_pii`).

## 10. IDs

- Internal PKs: `id` (UUID).
- Foreign keys: `<entity>_id`.
- Business-facing IDs (Document IDs, Decision IDs, Rule IDs, Error IDs,
  Prompt IDs): `<PREFIX>-<NNNN>` zero-padded to 4 digits, prefix
  UPPERCASE (`BR-0001`, `DEC-0001`, `ARC-0002`, `BUS-0001`, `AI-0001`,
  `AEP-001`, `FS-000`, `SDD-000`, `E-PRICING-001`) — this matches every
  ID scheme already in use; NS-001 formalizes rather than changes it.

## 11. Environment Variables

- `UPPER_SNAKE_CASE`, prefixed by concern where useful (e.g.
  `DATABASE_URL`, `BIKEVALUATOR_SECRET_KEY`).

## 12. Status / Lifecycle Names

- Document status values: `Draft`, `Needs Review`, `Review Comments`,
  `Approved`, `Locked`, `Deprecated`, `Superseded` (Title Case, exact
  strings, per Constitution Rule 20) — never abbreviate or reword.
- Entity lifecycle states (SDD-000 §3): `PascalCase` in code
  (`Draft`, `Inspection`, `Calculated`, `Reviewed`, `Completed`,
  `Archived`), matching the state machine diagrams verbatim.

## 13. Business Terminology

- Use the exact terms from `ai/glossary/business-glossary.md` — do not
  introduce synonyms (e.g. always "Dealer," never "Subscriber" or
  "Customer"; always "Vehicle Master Record," never "Vehicle Catalog
  Entry"). If a synonym is genuinely needed, propose it via a BUS
  decision and update the glossary, not ad hoc in code or a new
  document.

## Open Items

- None — this is the naming baseline referenced by CSS-001 and all
  future entity/API work.
