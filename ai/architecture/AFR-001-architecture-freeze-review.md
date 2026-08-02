# AFR-001 — Architecture Freeze & Readiness Review

| Field | Value |
|---|---|
| Document ID | AFR-001 |
| Version | 1.0 |
| Status | Needs Review |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | Every architecture document listed in §1 |
| Next Documents | FS-001 (Vehicle Master) — once this review is approved and the Architecture Freeze Checklist (§3) is worked through |

Purpose: certify whether BIKEVALUATOR's architecture baseline is
implementation-ready, consolidate every outstanding open question into
one matrix, and recommend approval status for the six standards
documents still marked "Needs Review." **No implementation code and no
new architecture documents beyond this one were generated.**

---

## 1. Architecture Readiness Assessment

| Document | Current Status | AFR-001 Note |
|---|---|---|
| Constitution v1.4.0 | Approved (stable per AR-001) | No change recommended |
| FS-000 (Core Domain & Valuation) | Approved | Superseded in places by BRD-001 (BUS-0004) — both remain valid where not contradicted |
| SDD-000 (Domain Architecture) | Approved | Superseded in places by DDD-001/DBD-001 — both remain valid where not contradicted |
| BRR-001 (Business Rule Registry) v1.1 | Approved | BR-0003 alone remains Provisional (thresholds unconfirmed — OQ-01) |
| BDR-001 (Business Decision Records) v2.0 | Partially Resolved | 4 of 14 items still open (OQ-02, OQ-03, OQ-04, OQ-05) |
| BRD-001 (Business Requirements) | Approved | No open items block it directly |
| DBD-001 (Database Design) | Approved | Two open questions affect it materially (OQ-08 role storage, OQ-14 transactionality) — see §5 |
| API-001 (Endpoints) | Approved | Response-envelope conflict with API-000 unresolved (OQ-06); OQ-04 (Year filtering) affects its query shape |
| API-000 (API Standards/conventions) | Approved | Conflicts with API-001's concrete envelope (OQ-06) — one must yield |
| DDD-001 (Canonical Domain Model) | Needs Review | 7 open questions (OQ-07 through OQ-13 below) |
| SSD-001 (System Sequence Diagrams) | Needs Review | 9 open questions (OQ-08, OQ-14 through OQ-21 below) |
| NS-001 (Naming Standards) | Needs Review | AFR-001 recommends **Approved** — see §4 |
| CSS-001 (Code Style Standards) | Needs Review | AFR-001 recommends **Approved** — see §4 |
| DOC-001 (Documentation Standards) | Needs Review | AFR-001 recommends **Approved** — see §4 |
| TEST-001 (Testing Standards) | Needs Review | AFR-001 recommends **Needs Revision** — see §4 |
| LOG-001 (Logging Standards) | Needs Review | AFR-001 recommends **Approved** — see §4 |
| SEC-001 (Security Standards) | Needs Review | AFR-001 recommends **Needs Revision** — see §4 |
| DD-Vehicle (Data Dictionary example) | Needs Review | No blocking issue found |
| ADR/UXS/DS/DDS/PEP/GOV folders | Empty placeholders | The architect-supplied external document contains full ADR-001..018/UXS-001/DS-001/DDS-001/PEP-001/GOV-001 content, referenced (not transcribed) via BUS-0004. **Recommendation: do not create these five as separate canonical files right now** — BUS-0004's reference is sufficient, and AFR-001 is explicitly scoped to avoid introducing new architecture documents unless strictly necessary. Flagged as a deliberate deferral, not an oversight — see §3. |

---

## 2. Open Question Resolution Matrix

Every open item from BDR-001, DDD-001 §12, and SSD-001 §9, deduplicated
(some questions were raised by more than one document) and given a
single `OQ-NN` ID for cross-reference going forward.

| OQ | Source Document(s) | Question | Blocking FS-001? | Recommended Decision (Architecture Recommendation, not approved) | Human Decision Required? | Implementation Impact | Priority |
|---|---|---|---|---|---|---|---|
| OQ-01 | BDR-0004, DDD-001 §12.5 | Exact recommendation-band thresholds (BR-0003) | No — Valuation Engine (FS-002) concern | Confirm 90/75/60% as final (simplest, already reasoned about) | Yes | Low (constant value) | Medium |
| OQ-02 | BDR-0007 | Vehicle Selector search threshold | No — Flutter UI concern | Always use type-ahead (consistency over threshold-tuning) | Yes | Low | Low |
| OQ-03 | BDR-0008 | Does Brand/Model availability vary by Year? | **Yes** — affects `/vehicles/*` query shape (FS-001) | No Year-based filtering in v1 (matches API-001 as written) | Yes | Medium (API query params) | Medium |
| OQ-04 | BDR-0012 | Formalize E-AUTHZ-001 in the error catalogue? | No — cross-cutting, deferrable | Add it now to SDD-000 §8 (low cost, prevents drift) | Yes | Low | Low |
| OQ-05 | (BDR-001 residual) | — *(BDR-0004/07/08/12 above are the 4 remaining BDRs; this row intentionally left as a placeholder for renumbering clarity — no 5th distinct BDR remains open)* | — | — | — | — | — |
| OQ-06 | AFR-001 (new, this review) | API-000's `data`/`meta`/`errors` envelope conflicts with API-001's `success`/`message`/`data`/`errors` | **Yes** — FS-001 must pick one shape | API-001's envelope wins (it's the concrete, later, architect-supplied shape); revise API-000 to match | Yes | Medium (affects every endpoint) | **High** |
| OQ-07 | DDD-001 §12.1 | Is `Vehicle` persisted in v1, or purely ephemeral? | Partially — Vehicle is owned by Valuation Engine (FS-002), not Vehicle Master, but FS-001's schema should not need to change if the answer is "ephemeral" | Ephemeral in v1 (matches DBD-001 having no v1 vehicle-instance table) | Yes | Low for FS-001 (confirms no new table needed); Medium for FS-002 | Medium |
| OQ-08 | DDD-001 §12.2, SSD-001 §9.5 | How is Dealer vs. SuperAdmin distinguished at the data level? DBD-001's `users` table shows no role column | **Yes — the single most consequential open item for FS-001** | Add a `role` column (enum or boolean `is_super_admin`) to `users` in DBD-001 | Yes | **High** — every Admin endpoint's authorization check depends on this | **Critical** |
| OQ-09 | DDD-001 §12.3 | Is `RepairAssessment` ever persisted independently in v1? | No — Repair Master/Valuation Engine (FS-002) concern | Transient only in v1 (matches API-001's stateless `/valuation/calculate`) | Yes | Low | Low |
| OQ-10 | DDD-001 §12.4 | Is Brand the correct aggregate root over Model/Variant? | No — informs code organization (FS-001), not the schema (DBD-001 already fixes the three tables regardless) | Accept as documented (Brand-rooted) — no source document contradicts it, only silence | No (can proceed on DDD-001's stated assumption; revisit if wrong) | Low | Low |
| OQ-11 | DDD-001 §12.6 | Should "one ValuationMaster per Year+Variant" become a formal `BR-0011`? | No — already enforced as a DB constraint regardless of BR numbering | Yes, add `BR-0011` for completeness/traceability | Yes | Low | Low |
| OQ-12 | DDD-001 §12.7 | Notification/Analytics/Future-AI domain objects not yet modeled | No — explicitly future scope | Defer — no action needed now | No | None (future) | Low |
| OQ-13 | SSD-001 §9.1 | Is `/valuation/calculate` idempotent/safely retryable? | No — Valuation Engine (FS-002) concern | Not idempotent in v1 (stateless, side-effect-free — safe to retry naturally since it performs no writes); revisit if it becomes a write in v2 | Yes | Low | Medium |
| OQ-14 | SSD-001 §9.2, §9.6 | Concurrent master-data edits (locking) and transactionality of ValuationMaster versioning + AuditLog write | **Yes** — both are Vehicle Master (FS-001) admin-write concerns | Wrap the versioned write (close old row's `effective_to`, insert new row) and its AuditLog entry in one DB transaction; use optimistic concurrency (a `version`/`updated_at` check) on ValuationMaster/RepairOption writes to detect concurrent edits | Yes | **High** — affects the correctness of FS-001's admin write path | **Critical** |
| OQ-15 | SSD-001 §9.3, §9.4 | Payment webhook idempotency and reconciliation | No — Payments (FS-006) concern | Defer to FS-006 | Yes | Medium (for FS-006 only) | Low (for FS-001) |
| OQ-16 | SSD-001 §9.7 | Is an in-flight Valuation honored if Subscription expires mid-flow? | No — Valuation Engine/Subscription (FS-002/FS-005) concern | Honor the in-flight request (check expiry only at flow start, not mid-flow) — simplest, least surprising to the Dealer | Yes | Low | Low |
| OQ-17 | SSD-001 §9.8 | OTP resend/rate-limiting | No — Authentication (FS-003) concern | Defer to FS-003 | Yes | Medium (for FS-003 only) | Low (for FS-001) |
| OQ-18 | SSD-001 §9.9 | Session/token refresh vs. full re-auth on JWT expiry | No — Authentication (FS-003) concern | Defer to FS-003; full re-auth is simplest for v1 | Yes | Medium (for FS-003 only) | Low (for FS-001) |

**Reading this table for FS-001 specifically:** only **OQ-03, OQ-06,
OQ-07, OQ-08, OQ-11, OQ-14** have any bearing on Vehicle Master. Of
those, **OQ-08 and OQ-14 are the true blockers** — everything else is
either already resolved-by-recommendation-and-low-stakes, or belongs to
a later module (FS-002/FS-003/FS-005/FS-006).

---

## 3. Architecture Freeze Checklist

For the human architect. Each item lists Decision / Rationale / Impact
/ Owner / Status.

| # | Item | Decision | Rationale | Impact | Owner | Status |
|---|---|---|---|---|---|---|
| 1 | Add `role` column to `users` (DBD-001) | **Pending** | OQ-08 — the single Critical blocker | High | Human | Open |
| 2 | Adopt DB-transaction + optimistic-concurrency policy for versioned master-data writes | **Pending** | OQ-14 — Critical blocker | High | Human | Open |
| 3 | Resolve API-000 vs. API-001 envelope conflict | **Pending** | OQ-06 — High priority, affects every endpoint | Medium | Human | Open |
| 4 | Confirm no Year-based Brand/Model filtering in v1 | **Recommended: confirm** | OQ-03 — matches API-001 as already written | Medium | Human | Open |
| 5 | Confirm recommendation thresholds (90/75/60%) | **Recommended: confirm** | OQ-01 — already reasoned about, low cost to revisit later | Low | Human | Open |
| 6 | Add `BR-0011` (ValuationMaster Year+Variant uniqueness) | **Recommended: yes** | OQ-11 — completeness/traceability, no functional change | Low | Human | Open |
| 7 | Formalize `E-AUTHZ-001` | **Recommended: yes** | OQ-04 — low cost, prevents future drift | Low | Human | Open |
| 8 | Do **not** create separate DS-001/UXS-001/DDS-001/PEP-001/GOV-001 files right now | **Recommended: defer** | BUS-0004's reference to the external document is sufficient; AFR-001 is scoped against introducing new documents | None (deferral) | Human | Open |
| 9 | Whether to mark any document "Locked" (vs. remaining "Approved") | **Recommended: do not lock yet** | Per Constitution Rule 20, "Locked" means implementation has begun — AFR-001 explicitly prohibits generating implementation code this round, so nothing has crossed that threshold yet. Locking now would be marking a state that hasn't actually occurred. See §6. | None (naming/status accuracy only) | Human | Open — flagged as a judgment call, not silently applied |
| 10 | Remaining low-priority OQs (OQ-02, 07, 09, 10, 12, 13, 15, 16, 17, 18) | **Recommended: defer to their owning FS** | None block FS-001; each is scoped to a later module | Low individually | Human | Open (non-blocking) |

---

## 4. Standards Approval Matrix

| Document | Recommendation | Justification |
|---|---|---|
| **NS-001** (Naming Standards) | **Approved** | Comprehensive coverage (repo/file/Markdown/Flutter/Django/Postgres/API/enums/booleans/IDs/env vars/status names/business terminology); no gap found against the documents produced since (DDD-001, SSD-001, DBD-001, API-001) — everything they name follows NS-001's conventions already. |
| **CSS-001** (Code Style Standards) | **Approved** | Solid baseline (PEP 8/Black/isort, Effective Dart, Markdown conventions, file-header/comment rules, dependency pinning). Exact linter tool versions are explicitly deferred to FS-001 kickoff, which is a reasonable non-blocking scope boundary, not a gap. |
| **DOC-001** (Documentation Standards) | **Approved** | Matches the conventions every document since AEP-001 has actually followed (metadata blocks, ID-based cross-referencing, tables over prose); no drift found. |
| **TEST-001** (Testing Standards) | **Needs Revision (minor)** | Written before SSD-001 existed. It defines unit/integration/e2e levels and BR-ID-referenced test naming, but has no explicit guidance for testing the failure/retry/concurrency scenarios SSD-001 §6 catalogs (idempotency, concurrent-edit conflicts, webhook redelivery). Recommend adding one short section cross-referencing SSD-001 §6 once OQ-08/OQ-14 are resolved — not a rewrite, an addition. |
| **LOG-001** (Logging Standards) | **Approved** | Levels, structured logging, PII exclusion, and retention are well specified. Minor forward-looking note: once OQ-08 (role storage) and OQ-14 (concurrency) are resolved, LOG-001's `AUDIT` level should explicitly cover authorization-check failures and concurrent-edit rejections — worth a follow-up note, not a blocking revision. |
| **SEC-001** (Security Standards) | **Needs Revision (minor)** | States the *principle* that authorization is enforced server-side (correct), but does not yet reference the fact that the authorization *mechanism itself* (OQ-08) is still an open question. Recommend adding a line pointing to OQ-08/AFR-001 §2 as a pre-implementation dependency for every Admin endpoint, so the gap isn't accidentally missed during FS-001 implementation. |

---

## 5. Readiness Certification

**Is FS-001 (Vehicle Master) ready?**
**Not yet.** Blocked specifically by **OQ-08** (role storage/
authorization mechanism) and **OQ-14** (transaction/concurrency policy
for master-data writes). Both are Critical and both are Vehicle
Master's own concerns (admin writes to Brand/Model/Variant/
ValuationMaster). Once those two are answered, FS-001 has everything
else it needs: DBD-001's schema, API-001's endpoint inventory, DDD-001's
object model, SSD-001's flow diagrams (§3.2, §3.7), and BRR-001's rules
(BR-0001, BR-0002, BR-0004, BR-0005, BR-0007, BR-0009, BR-0010).

**Is DBD-001 (database design) ready?**
**Mostly, with one pending edit.** The schema itself (Brand/Model/
Variant/ValuationMaster/RepairComponent/RepairOption + soft-delete +
temporal versioning) is sound and Approved. It needs exactly one
addition once OQ-08 is resolved: a `role` column (or equivalent) on
`users`. No other schema change is indicated.

**Is API-001 (endpoints) ready?**
**Mostly, with two pending items.** The endpoint inventory itself is
complete and Approved. It carries forward the unresolved response-
envelope conflict with API-000 (OQ-06) and would need a query-parameter
addition if OQ-03 is answered "yes, filter by Year" (current
recommendation is "no," which requires no change).

**What still blocks implementation?**
In priority order: **OQ-08** (role storage) → **OQ-14** (transaction/
concurrency policy) → **OQ-06** (envelope conflict) → confirmation of
OQ-01/OQ-03/OQ-11/OQ-04 (all low-cost, already-recommended confirmations).
Everything else in §2 belongs to a later FS module and does not block
FS-001.

---

## 6. Repository Cleanup

- **Prompt archiving:** `ai/prompts/prompt-index.md` status column
  updated — AEP-003 through AEP-007, IPS-001, BUS-001, BUS-0004,
  DDD-001, and SSD-001 are marked **Archived** (fully executed,
  deliverables now part of the frozen baseline under review here).
  AFR-001 itself is Active until approved.
- **Document locking:** **No document was moved to "Locked."** Per
  Constitution Rule 20, Locked specifically means "implementation has
  begun" — since this prompt explicitly prohibits generating
  implementation code, that threshold hasn't been crossed yet, and
  marking documents Locked now would misrepresent that. This is flagged
  as Checklist item #9 for your explicit call — if you want a status
  between Approved and Locked (e.g. "Approved — frozen pending FS-001"),
  that's worth a quick constitution amendment rather than reusing
  Locked's existing, narrower definition.
- **New architecture documents:** none beyond this one. The five
  external-document sections (ADR/UXS/DS/DDS/PEP) were deliberately
  **not** transcribed into new canonical files (Checklist item #8).
- **No business rule was changed** in this review.

---

## Open Items

See §2's Open Question Resolution Matrix in full — 18 items, of which 2
(OQ-08, OQ-14) are Critical blockers for FS-001, and 1 (OQ-06) is High
priority. All others are either low-cost confirmations or deferred to a
later FS module.
