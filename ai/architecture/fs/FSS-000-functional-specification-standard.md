# FSS-000 — Functional Specification Standard

| Field | Value |
|---|---|
| Document ID | FSS-000 |
| Version | 1.0 |
| Status | Needs Review |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | Constitution (Rules 19, 20, 22), ABL-001, DBD-001, API-001, BRR-001, DDD-001, SSD-001, `ai/templates/fs-template.md` |
| Next Documents | FS-001 (Vehicle Master) — first document required to conform |

This is **not** a feature specification. It is the engineering standard
that every module-level Functional Specification (**FS-001 onward**)
must follow, so that FS-001, FS-002 (Valuation Engine), FS-003
(Authentication), FS-004 (Admin), FS-005 (Subscription), and FS-006
(Payments) are structurally identical, equally reviewable, and never
individually reinvent their own format.

**Note on scope — FS-000 is exempt.** `FS-000-core-domain-valuation.md`
predates this standard and serves a different purpose: it is the
business-DNA document every module references, not a single module's
functional spec. It is not required to be retrofitted against this
standard, and this document does not certify or decertify it. FSS-000
governs FS-001 onward only.

A ready-to-copy skeleton implementing this standard lives at
`ai/templates/fs-template.md`.

---

## 1. Mandatory Structure

Every FS document (FS-001 onward) must contain all 21 sections below,
in this order, using the section titles verbatim. A section may be
marked **"N/A — <reason>"** if genuinely not applicable to that module,
but it must still appear — sections are never silently omitted.

| # | Section | Required Content |
|---|---|---|
| 1 | **Purpose** | One paragraph: what business problem this module solves and why it exists, in FS-000's terms (no re-derivation of business DNA). |
| 2 | **Scope** | What this module does and — explicitly — does **not** do (in-scope / out-of-scope lists), including which future FS module owns anything explicitly excluded. |
| 3 | **Actors** | Every actor who interacts with this module (Dealer, Super Admin, System, external gateway, etc.), cited from SSD-001's actor list where they overlap — not redefined. |
| 4 | **Preconditions** | What must already be true (data state, prior module completion, Approved decisions) before this module's flows can begin. |
| 5 | **User Stories** | `As a <actor>, I want <capability>, so that <benefit>` — one per distinct capability, traceable to a Functional Requirement below. |
| 6 | **Functional Requirements** | Numbered, testable statements (`FR-<FS#>-NNN`) of what the system must do. Each must trace to at least one User Story. |
| 7 | **Business Rules** | **Reference BRR-001 rule IDs only** (`BR-000x`) — never restate a rule's logic here. If a genuinely new rule is needed, it is proposed as a new `BR-00xx` addition to BRR-001 (a decision), not invented inline. |
| 8 | **Validation Rules** | Field-level/input validation (required fields, formats, ranges) — distinct from Business Rules (§7), which are cross-field business logic. |
| 9 | **UI Requirements** | Screen-level requirements (per screen: purpose, key fields/actions). No visual design/mockups — that's Design System (DS-001) territory; this is behavioral, not visual. |
| 10 | **Navigation** | Entry points into this module and exit points to others (which screen/flow leads here, where completing this module's flow goes next). |
| 11 | **API Mapping** | Every endpoint this module uses, **cited from API-001 by path** — never invents a new endpoint inline. If a new endpoint is genuinely needed, it is proposed as an API-001 addition (a decision), not invented in the FS. |
| 12 | **Database Mapping** | Every table/column this module reads or writes, **cited from DBD-001 by table name** — same rule as §11: new schema is proposed as a DBD-001 addition, not invented here. |
| 13 | **Sequence Flow** | Reference the relevant SSD-001 diagram(s) by section number; only add a new Mermaid sequence diagram here if this module's flow doesn't already exist in SSD-001. |
| 14 | **Error Handling** | Every applicable error from SDD-000 §8 / API-001's error codes that this module can trigger, and the user-facing behavior for each. New error codes are proposed as SDD-000 §8 additions, not invented inline. |
| 15 | **Permissions** | Who can do what (Dealer vs. Super Admin), citing BR-0004 and `E-AUTHZ-001` (SDD-000 §8) rather than restating the authorization mechanism. |
| 16 | **Audit Logging** | Which actions in this module produce an `audit_logs` entry (per DBD-001 §2), and what old/new values are captured. |
| 17 | **Performance Expectations** | Module-specific refinement of SDD-000 §7's NFRs (e.g. catalog lookup latency target) — must not contradict SDD-000, only specialize it. |
| 18 | **Security Considerations** | Module-specific application of SEC-001 (once Approved) and BR-0004/E-AUTHZ-001 — data exposure risks specific to this module's screens/endpoints. |
| 19 | **Acceptance Criteria** | Numbered, testable `AC-<FS#>-NNN` statements — the Definition of Done for the *feature*, distinct from FSS-000's Definition of Done for the *document* (§3 below). |
| 20 | **Edge Cases** | Boundary conditions and unusual-but-real scenarios (empty catalogs, concurrent admin edits, expired subscriptions mid-flow, etc.) — cross-check against SSD-001's Failure Scenarios matrix for this flow. |
| 21 | **Future Enhancements** | Explicitly out-of-v1-scope ideas for this module, so they're captured without expanding current scope. |

Two further mandatory trailing sections apply to every FS on top of the
21 above — detailed in §4 and §5 below:

- **22. Architecture Compliance Checklist**
- **23. Cross-FS Dependencies**

---

## 2. Definition of Ready (DoR)

An FS document **may not begin being drafted** until all of the
following are true. If any item is unmet, the correct action is to
raise it as a blocking decision or architecture gap, not to draft
around it.

- [ ] The module's Blocking-Module architecture dependencies (per the
  ABL-001 Decision Traceability Matrix) are all Approved — no relevant
  `AI-0005` (or later) decision for this module is still Pending.
- [ ] DBD-001, API-001, BRR-001, SDD-000, DDD-001, and SSD-001 all cover
  this module's domain objects, endpoints, tables, and flows at least
  at the level FS-001 needed them (i.e., no architecture gap specific
  to this module remains undocumented).
- [ ] Any FS this module depends on (per §5 Cross-FS Dependency Rules)
  is at least `Approved` in status.
- [ ] The roadmap (`ai/roadmap/roadmap.md`) confirms this module is next
  in sequence, or an explicit human instruction authorizes drafting out
  of order.
- [ ] The prior `review-package.md` has been reviewed (Constitution Rule
  21's Pre-Execution Checklist) so this FS doesn't repeat a
  already-flagged open item.

---

## 3. Definition of Done (DoD)

An FS document **is not complete** until all of the following are true.
This is the document's own DoD — distinct from the feature's Acceptance
Criteria (§1 item 19), which is the DoD for the *feature being built*.

- [ ] All 21 mandatory sections (§1) are present, in order, none silently
  omitted (N/A entries carry a reason).
- [ ] §22 Architecture Compliance Checklist and §23 Cross-FS Dependencies
  are both present and filled in, not left as placeholders.
- [ ] Every Business Rule reference is a citation (`BR-000x`), not a
  restatement of the rule's logic.
- [ ] Every API endpoint cited exists in API-001; every DB table/column
  cited exists in DBD-001. Anything genuinely new is flagged as a
  required decision, not silently added to the FS as if already
  architecture-approved.
- [ ] Every error code cited exists in SDD-000 §8 / API-001; new ones
  are flagged the same way.
- [ ] Acceptance Criteria (§1 item 19) are individually testable —
  no vague criteria like "works correctly."
- [ ] Metadata block (Constitution Rule 19) is present and complete;
  Status is `Draft` or `Needs Review` — an FS is never self-marked
  `Approved` by the AI that drafted it (Constitution Rule 10).
- [ ] Open questions (if any) are listed explicitly rather than silently
  resolved by assumption.
- [ ] Repository synchronization has run: context, session-state,
  roadmap, todo, changelog, review-package, prompt-index, and
  prompt-history all reflect this FS's creation.

---

## 4. Architecture Compliance Checklist

Section 22 of every FS. A fixed, filled-in table — not free prose —
so compliance is scannable at a glance:

| Field | Content |
|---|---|
| Architecture documents referenced | List every document this FS actually cited (e.g. DBD-001, API-001, BRR-001, SSD-001 §3.2, SDD-000 §8). |
| Decision IDs implemented | List every `AI-0005` (or later) decision this FS's content depends on or implements (e.g. `SEC-0001`, `ENG-0003`, `ARC-0005`). |
| Business Rule IDs referenced | Every `BR-000x` cited in §7. |
| APIs used | Every endpoint cited in §11, by path. |
| Database tables used | Every table cited in §12. |
| Deviations | Any place this FS intentionally diverges from an architecture document, with a reason and — if the deviation is more than cosmetic — a new decision ID proposed to formalize it. "None" if there are none; never omitted. |
| New architectural questions | Anything this FS surfaced that no existing document answers. Logged here **and** cross-referenced as a new item the next architecture-review prompt should pick up — never silently resolved inline. |

This is the mechanism referenced in ABL-001's Strategic Recommendation:
from FS-001 onward, this checklist is what makes "did the AI actually
follow the baseline" auditable per-document rather than assumed.

---

## 5. Cross-FS Dependency Rules

Section 23 of every FS, plus the rules governing how FS documents may
reference one another:

1. **Reference by ID, never restate.** If FS-002 needs a rule/object/
   endpoint already defined by FS-001 (or by an architecture document),
   it cites the ID — it does not copy the content in. This is the same
   principle as BRR-001's rule for Business Rules, applied to FS-to-FS
   references.
2. **Every FS's §23 Cross-FS Dependencies table has exactly two
   columns:**

   | Depends On (must be Approved first) | Provides To (future FS that will depend on this one) |
   |---|---|
   | e.g. none (FS-001 is first) | e.g. FS-002 (Valuation Engine reads Vehicle Master catalog/pricing) |

3. **No circular dependencies.** If FS-A needs something from FS-B and
   FS-B needs something from FS-A, that is an architecture-layer gap
   (SDD-000 Module Boundaries, §4, should already prevent this) —
   escalate as a new architectural question, don't resolve it inside
   either FS.
4. **Sequence follows the roadmap.** A later FS may depend on an
   earlier one; an earlier FS must never depend on a later one. If a
   genuine forward dependency is discovered, it is raised as an open
   question for the architect (does the roadmap order need to change?),
   not silently worked around.
5. **A dependency is satisfied at `Approved`, not `Locked`.** Per
   Constitution Rule 20, `Locked` requires implementation to have
   begun — requiring `Locked` as a dependency gate would mean no second
   FS could ever be drafted before the first is fully built, which
   isn't the intent.
6. **Shared domain objects/business rules are never forked.** If two FS
   documents both touch, say, `ValuationMaster`, both cite DDD-001/
   DBD-001/BRR-001 directly — neither FS "owns" a private redefinition
   of a shared object.

---

## Open Items

- None from this standard itself. As FS-001 is drafted, if any of the
  21 sections or the DoR/DoD checklists prove to not fit a real module
  cleanly, that is feedback for a revision of this document (a new
  version, per Constitution Rule 20's Superseded/versioning discipline)
  — not a silent per-FS exception.
