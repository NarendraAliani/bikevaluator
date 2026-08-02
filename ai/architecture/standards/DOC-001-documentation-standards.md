# DOC-001 — Documentation Standards

| Field | Value |
|---|---|
| Document ID | DOC-001 |
| Version | 1.0 |
| Status | Needs Review |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | NS-001, CSS-001, all `ai/architecture/**` documents |
| Next Documents | TEST-001, LOG-001 |

Governs how documentation (both `ai/` process docs and future `docs/`
user/developer docs) is written and maintained. Standards only.

## Architecture Documents (`ai/architecture/**`)

- Metadata block required (Constitution Rule 19) immediately after the
  H1 title.
- Status transitions logged in the document's own "Last Updated" field
  and, if the change is consequential, in `ai/decisions/decisions.md`.
- Reference other documents by ID (`BR-0001`, `FS-000`), not by
  describing them — keeps documents stable as titles evolve.

## Process Documents (`ai/` governance/tracking files)

- Timestamp every entry (Constitution Rule 5).
- Newest-first ordering except `ai/history/prompt-history.md`, which is
  chronological (oldest-first) by design — it's a story, not a log to
  scan for "what's current."

## User/Developer Documentation (`docs/`)

- Not yet populated (Phase 0/1 constraint) — when it begins, one file
  per user-facing concern (setup, API usage, deployment), cross-linked
  from `docs/README.md`, never duplicating content already canonical in
  `ai/architecture/**` (link to it instead).

## Tone and Structure

- Prefer tables over prose for anything enumerable (fields, statuses,
  priorities) — established convention across FS-000/SDD-000/BRR-001.
- No marketing language ("cutting-edge," "seamless") — descriptive,
  factual statements only.

## Open Items

None — this document formalizes conventions already in consistent use
since AEP-001.
