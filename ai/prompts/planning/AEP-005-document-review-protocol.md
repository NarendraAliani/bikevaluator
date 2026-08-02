# AEP-005 — Document Review Protocol (DRP-001)

- **Prompt ID:** AEP-005
- **Version:** 1.0
- **Date:** 2026-08-02
- **Purpose:** Stop sharing the entire repository after every prompt.
  Establish a Document Review Protocol: a generated `review-package.md`
  classifying every touched file (Category A/B/C/D) with a review
  priority, plus a metadata/status standard on architecture documents, so
  future prompt executions share only `review-package.md` + the critical
  (🔴/🟠) files by default.
- **Output expectation:** `ai/review/review-package.md` (this execution's
  package); `ai/templates/review-package-template.md`;
  `ai/templates/architecture-document-metadata-template.md`; metadata
  blocks retrofitted onto FS-000 and SDD-000; constitution v1.3.0 (Rules
  18-19); synchronized decisions/todo/changelog/session/context/memory/
  prompt-index/prompt-history.
- **Linked decisions:** AI-0002

## Revision history

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-02 | Initial version |
