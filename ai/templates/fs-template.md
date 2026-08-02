<!--
Master template for every Functional Specification, FS-001 onward.
Implements FSS-000 (ai/architecture/fs/FSS-000-functional-specification-standard.md).
Copy this file to ai/architecture/fs/FS-<NNN>-<kebab-title>.md and fill
in every section — do not delete a section, mark it "N/A — <reason>"
instead if genuinely not applicable (FSS-000 §1).
-->

# FS-<NNN> — <Module Title>

| Field | Value |
|---|---|
| Document ID | FS-<NNN> |
| Version | 1.0 |
| Status | Draft |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | <YYYY-MM-DD> |
| Last Updated | <YYYY-MM-DD> |
| Related Documents | FS-000, DDD-001, SSD-001, DBD-001, API-001, BRR-001, SDD-000, FSS-000 |
| Next Documents | <next FS in sequence, if known> |

## 1. Purpose

## 2. Scope

**In scope:**

**Out of scope:** (name which future FS module owns each excluded item)

## 3. Actors

## 4. Preconditions

## 5. User Stories

- As a <actor>, I want <capability>, so that <benefit>.

## 6. Functional Requirements

| ID | Requirement | Traces to User Story |
|---|---|---|
| FR-<NNN>-001 | | |

## 7. Business Rules

Reference `BR-000x` only — do not restate rule logic here.

## 8. Validation Rules

## 9. UI Requirements

## 10. Navigation

## 11. API Mapping

Cite API-001 endpoints by path only. New endpoints require an API-001
decision first, not an inline addition here.

## 12. Database Mapping

Cite DBD-001 tables/columns only. New schema requires a DBD-001
decision first, not an inline addition here.

## 13. Sequence Flow

Reference the relevant SSD-001 diagram section(s). Add a new Mermaid
sequence diagram only if this flow doesn't already exist in SSD-001.

## 14. Error Handling

## 15. Permissions

Cite BR-0004 / `E-AUTHZ-001` — do not restate the authorization
mechanism.

## 16. Audit Logging

## 17. Performance Expectations

Specialize SDD-000 §7's NFRs — must not contradict them.

## 18. Security Considerations

## 19. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-<NNN>-001 | |

## 20. Edge Cases

Cross-check against SSD-001's Failure Scenarios matrix for this flow.

## 21. Future Enhancements

## 22. Architecture Compliance Checklist

| Field | Content |
|---|---|
| Architecture documents referenced | |
| Decision IDs implemented | |
| Business Rule IDs referenced | |
| APIs used | |
| Database tables used | |
| Deviations | None. |
| New architectural questions | None. |

## 23. Cross-FS Dependencies

| Depends On (must be Approved first) | Provides To (future FS depending on this one) |
|---|---|
| | |

## Open Questions

None invented — list only genuinely undefined items surfaced while
drafting this FS.
