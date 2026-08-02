# CSS-001 — Code Style Standards

| Field | Value |
|---|---|
| Document ID | CSS-001 |
| Version | 1.0 |
| Status | Needs Review |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | NS-001, API-000 |
| Next Documents | DOC-001, TEST-001 |

Style, not naming (NS-001 owns naming) — how code is formatted, ordered,
and documented. Standards only; no implementation yet.

## Python / Django

- Follow PEP 8; line length 88 (Black default) unless the team decides
  otherwise before FS-001 implementation.
- Import order: standard library → third-party → local, each group
  alphabetized, blank line between groups (isort convention).
- One Django app per module boundary (SDD-000 §4): `vehicle_master`,
  `valuation_engine`, `authentication`, `admin_panel`, `subscription`,
  `payments`, `reports`.

## Flutter / Dart

- Follow Effective Dart (style, usage, documentation).
- Widget files: one primary widget per file, named to match the file
  (per NS-001 §4).
- Folder structure mirrors module boundaries (SDD-000 §4), not
  screen-by-screen ad hoc grouping.

## Markdown (this repository's own documents)

- Tables for structured/tabular data (metadata blocks, entity fields,
  registries) — established convention, keep it.
- `##`/`###` headers, not bold text, for section structure.
- Fenced code blocks for diagrams/flows (as used throughout FS-000,
  SDD-000).

## Comments (per Constitution Rule 4)

- Explain why, not what — no restating code in prose.
- Every code file begins with the File Header block (Constitution
  Rule 3): Full Path, Relative Path, Module, Purpose.

## Dependency Ordering

- Explicit version pinning in `requirements.txt` / `pubspec.yaml` — no
  floating versions for direct dependencies.

## Open Items

- Exact linter/formatter tool choices (Black vs. autopep8, `dart format`
  config) deferred to FS-001 implementation kickoff — not blocking this
  standards document's approval.
