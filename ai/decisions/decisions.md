# Decisions Log — BIKEVALUATOR

Use `ai/templates/decision-template.md` for new entries. Newest entries at
the top. Never delete a decision — supersede it with a new entry that
references the old id.

## Category ID Migration (as of AEP-002)

New decisions use category-prefixed IDs: `BUS` (business), `ARC`
(architecture), `DB` (database), `API`, `SEC` (security), `OPS`
(operations), `AI` (AI-framework/process). Format: `<CATEGORY>-<NNNN>`,
numbered independently per category.

`BUS` (business) decisions were added in AEP-003, the first prompt to
carry confirmed product/business facts.

Historical decisions `DEC-0001` through `DEC-0003` are **not renamed or
rewritten** — they remain valid under their original flat IDs and are
retroactively understood as category `AI` (AI-framework/process
decisions), documented here for cross-reference:

- `DEC-0001` ≈ `AI-0001` (framework adoption)
- `DEC-0002` ≈ `AI-0002` (universal/project-specific tagging)
- `DEC-0003` ≈ `ARC-0001` (production root placeholder)

Going forward, cite decisions by their real ID (`DEC-000x` for legacy,
`CATEGORY-000x` for new). Do not retroactively edit legacy entries beyond
this mapping note.

---

## ARC-0001

- **Timestamp:** 2026-08-02T00:00
- **Context:** AEP-002 introduces a full architecture document repository
  (`ai/architecture/{brd,sdd,dbd,api,adr,uxs,ds,dds,pep,gov,fs}`) and needs
  a home for structural/architecture-category decisions going forward.
- **Decision:** Adopt the categorized decision-ID scheme described above,
  and create the architecture folder set as empty placeholders pending
  real content.
- **Reasons:** Flat sequential decision IDs don't scale once decisions span
  distinct concerns (business, architecture, security, ops); categorized
  IDs make it possible to scan a single domain's decision history.
- **Alternatives considered:** Keep flat `DEC-NNNN` numbering — rejected,
  becomes unwieldy as decision volume grows across concerns. Renumber
  history into categories — rejected, violates the never-rewrite-history
  rule.
- **Consequences:** All future architecture-scoped decisions use `ARC-`
  IDs; legacy `DEC-0003` is cross-referenced as `ARC-0001` but keeps its
  original identity.

## AI-0001

- **Timestamp:** 2026-08-02T00:00
- **Context:** The closed-loop engineering workflow (architect writes
  prompt → AI implements → AI reports → architect reviews) requires
  standardized, mandatory reporting so reviews are consistent and nothing
  is missed.
- **Decision:** Add two permanent constitution rules: (1) every prompt
  execution must produce a Prompt Execution Report, and (2) every prompt
  execution must produce a Repository Health Report with an automated
  audit and health score. Also mandate that any change synchronize all
  affected tracking files (todo, decisions, session-state, changelog,
  context, project-memory, prompt-index, review logs) with no manual
  step required.
- **Reasons:** Makes AI output auditable and reviewable in a fixed format;
  removes reliance on the AI "remembering" to update peripheral files.
- **Alternatives considered:** Freeform end-of-response summaries —
  rejected, inconsistent structure makes review slower and error-prone.
- **Consequences:** This and all future prompts must end with both
  reports; the documenter agent role exists specifically to own this
  synchronization.

## BUS-0001

- **Timestamp:** 2026-08-02T00:00
- **Context:** AEP-001/AEP-002 left BIKEVALUATOR's domain officially
  unconfirmed (RISK-0001), blocking FS work. The architect has since
  confirmed the domain from prior discussion.
- **Decision:** BIKEVALUATOR is a B2B SaaS platform for dealer-focused
  used two-wheeler valuation, centered on a centralized pricing/valuation
  engine, sold via subscription. Tech stack: Flutter (client) + Django
  (backend) + PostgreSQL (database).
- **Reasons:** Unblocks all functional-specification work; without a
  confirmed domain no FS document can be written without guessing.
- **Alternatives considered:** None — this records a fact confirmed by the
  architect, not a choice among options.
- **Consequences:** RISK-0001 in `ai/risks/risk-register.md` should be
  closed/updated; `ai/glossary/business-glossary.md` and
  `ai/memory/project-memory.md` updated with confirmed domain terms;
  FS-000 (`ai/architecture/fs/FS-000-core-domain-valuation.md`) authored
  as the foundational spec.

## BUS-0002

- **Timestamp:** 2026-08-02T00:00
- **Context:** AEP-002's roadmap defaulted to Authentication as the first
  module, based on the (now outdated) assumption that the domain was
  still unconfirmed. With the domain confirmed (BUS-0001), the valuation
  engine is understood to be the product's core intellectual property.
- **Decision:** Reorder Phase 1 of the roadmap to: Vehicle Master →
  Valuation Engine → Authentication → Admin → Subscription → Payments.
- **Reasons:** If the valuation logic is wrong, the entire product is
  wrong; authentication is a supporting module that can be built later
  without blocking validation of the core business logic.
- **Alternatives considered:** Keep Authentication-first (original
  AEP-002 plan) — rejected now that the domain is known, since it
  delays validating the riskiest, highest-value part of the product.
- **Consequences:** `ai/roadmap/roadmap.md` updated; next recommended
  prompt is FS-001 (Vehicle Master), not FS-001 (Authentication) as
  previously implied.

## ARC-0002

- **Timestamp:** 2026-08-02T00:00
- **Context:** FS-000 defined terminology and business rules but not
  relationships, lifecycles, module ownership, interaction sequencing, or
  non-functional requirements. Drafting FS-001 (Vehicle Master) without
  these risked different developers/agents interpreting entities and
  boundaries inconsistently.
- **Decision:** Insert a domain-architecture step (AEP-004) between FS-000
  and FS-001: author `SDD-000-domain-architecture.md` (domain model,
  entity catalogue, state machines, module boundaries, event flow, NFRs,
  error catalogue) and a permanent
  `ai/architecture/traceability/requirements-traceability-matrix.md`.
- **Reasons:** Cheaper to formalize structure once, centrally, than to
  have it inferred inconsistently across FS-001 through FS-006.
- **Alternatives considered:** Let each module FS derive its own entity/
  state/boundary definitions inline — rejected, risks contradictions
  between modules (e.g. Vehicle Master and Valuation Engine disagreeing
  on who owns Repair Cost).
- **Consequences:** All future FS documents (FS-001 onward) must conform
  to `SDD-000-domain-architecture.md` rather than redefining structure;
  the traceability matrix becomes a permanent, additive-only governance
  artifact updated on every module FS.

## BUS-0003

- **Timestamp:** 2026-08-02T00:00
- **Context:** SDD-000 surfaced business constraints implied by FS-000
  but not previously stated explicitly (e.g. Purchase Price floor,
  Admin-only pricing edits, Subscription gating).
- **Decision:** Adopt the 6 business constraints listed in SDD-000 §6 as
  binding, centralized rules that no module-level FS may contradict or
  redefine locally.
- **Reasons:** Prevents constraint drift/duplication across module FS
  documents; gives a single place to update a constraint if it changes.
- **Alternatives considered:** Restate constraints per-module as each FS
  is written — rejected, same drift risk as ARC-0002's rationale.
- **Consequences:** FS-001 onward reference SDD-000 §6 rather than
  re-deriving these constraints.

## AI-0002

- **Timestamp:** 2026-08-02T00:00
- **Context:** As the architecture repository grows (FS-000, SDD-000,
  traceability matrix, and more to come), sharing every created/modified
  file after each prompt does not scale and dilutes the architect's
  review attention.
- **Decision:** Adopt the Document Review Protocol (DRP-001): every
  prompt execution generates `ai/review/review-package.md` classifying
  touched files into Category A (Architecture, always review), B
  (Engineering, usually review), C (Operational, review only if
  materially changed), D (Generated, not sent unless asked), each with a
  Review Priority (🔴/🟠/🟡/🟢). By default, only the review package plus
  🔴/🟠 files are shared. Also adopt a mandatory metadata/status block
  (Document ID, Version, Status, Owner, Reviewer, Created, Last Updated,
  Related/Next Documents) on every architecture document.
- **Reasons:** Keeps the human's review effort focused on what needs
  judgment; turns the architecture folder into a navigable, versioned
  knowledge graph instead of isolated files.
- **Alternatives considered:** Continue sharing full repository trees —
  rejected, doesn't scale. Let the AI guess which files matter — rejected,
  inconsistent and error-prone versus a structured classification.
- **Consequences:** Constitution Rules 18-19 added (v1.3.0); all future
  prompt executions must produce `review-package.md` and default to
  sharing only it plus critical files; FS-000 and SDD-000 retrofitted
  with metadata blocks.

## ARC-0003

- **Timestamp:** 2026-08-02T00:00
- **Context:** Business rules were scattered across FS-000, SDD-000, and
  decisions with no single ID scheme, risking drift as more FS documents
  are drafted. Similarly, no API conventions or data dictionaries existed
  before the first API/schema work.
- **Decision:** Create `ai/architecture/business-rules/BRR-001-business-rule-registry.md`
  (BR-000x IDs for every business rule, referenced not restated by future
  FS documents); `ai/architecture/data-dictionary/` (per-entity field
  dictionaries, `DD-Vehicle.md` as the worked example); and
  `ai/architecture/api/API-000-standards.md` (URL/versioning/error/
  pagination/date conventions, no endpoints yet).
- **Reasons:** Centralizing rules, field definitions, and API conventions
  before FS-001 prevents drift and inconsistent interpretation across
  modules/agents.
- **Alternatives considered:** Let each FS restate rules/fields/API shape
  inline — rejected, same drift risk noted in ARC-0002.
- **Consequences:** FS-001 onward must reference `BR-000x` IDs, use the
  `DD-<Entity>.md` format for schema fields, and follow API-000's
  conventions for any endpoint design.

## AI-0003

- **Timestamp:** 2026-08-02T00:00
- **Context:** A document's existence (Draft/Needs Review) was being
  treated informally as sufficient for implementation to begin; no
  formal gate existed. Also, prompt executions followed the reporting
  rules (13-15, 17-18) without an explicit, checkable start/end
  checklist.
- **Decision:** Adopt a fixed document status lifecycle — `Draft → Needs
  Review → Review Comments → Approved → Locked → Superseded` (or
  `Approved → Deprecated`) — with implementation gated on `Approved` or
  `Locked` status. Adopt a Pre-Execution Checklist and Post-Execution
  Checklist reported as part of every Prompt Execution Report.
- **Reasons:** Closes the gap where "drafted" silently became "safe to
  build on"; makes the constitution's existing bootstrap/reporting rules
  auditable per-execution instead of aspirational.
- **Alternatives considered:** Rely on `ai/review/review-package.md`
  alone to signal review need — rejected, it tracks what to review, not
  whether review concluded with approval.
- **Consequences:** Constitution Rules 20-21 added (v1.4.0); FS-001 may
  not begin production implementation until FS-000, SDD-000, BRR-001,
  API-000 (and any documents it depends on) reach `Approved`/`Locked`.

## ARC-0004

- **Timestamp:** 2026-08-02T00:00
- **Context:** Architecture Review AR-001 found the Constitution mature
  enough that further rules should be rare, but identified real gaps —
  naming, code style, documentation, testing, logging, and security
  standards — none of which are constitutional in nature (they're
  operational conventions, not binding governance).
- **Decision:** Create `ai/governance/` for operational standards
  (engineering principles, git workflow, branching, release policy) kept
  separate from the Constitution, and
  `ai/architecture/standards/{NS-001,CSS-001,DOC-001,TEST-001,LOG-001,
  SEC-001}.md` for naming/code-style/documentation/testing/logging/
  security conventions. Apply AR-001's two requested revisions: enrich
  BRR-001 with Category/Priority/Owner/Affected Modules columns plus a
  Business Rule Dependency Graph, and enrich the Data Dictionary
  template (regenerating `DD-Vehicle.md` against it).
- **Reasons:** Keeps the Constitution lightweight and rarely-changing
  (per AR-001's explicit recommendation) while still giving every future
  FS document a naming/style/test/log/security baseline to inherit.
- **Alternatives considered:** Add Rule 22+ to the Constitution for each
  new standard — rejected per AR-001's explicit recommendation against
  continuing to grow the Constitution.
- **Consequences:** FS-001 onward must follow NS-001 for all
  naming (fields, files, IDs, enums) and CSS-001 for code style;
  BRR-001 v1.1 and `DD-Vehicle.md` v2.0 supersede their prior versions
  in place (both re-issued under the same Document ID, versioned, not
  renamed — consistent with the additive-history principle).

## AI-0004

- **Timestamp:** 2026-08-02T00:00
- **Context:** AR-001 observed that the `ai/` framework has grown larger
  and more general than BIKEVALUATOR itself, and recommended eventually
  separating universal AI-engineering-framework assets from
  BIKEVALUATOR-specific business/architecture content, to let future
  products bootstrap from the same framework.
- **Decision:** Record this as a **planned future decision**, not
  executed now: a future reorganization would split the repository into
  an AIEF (AI Engineering Framework — Constitution, Prompt Workflow,
  Review Protocol, Naming/Code-Style Standards, Templates, Governance)
  and a BIKEVALUATOR project layer (Business Rules, FS documents, Domain
  Model, Vehicle Master, Valuation Engine, APIs, UI, Database). No
  folders are renamed or moved as part of this decision.
- **Reasons:** A full repository restructuring is a significant,
  effectively irreversible change (breaks every existing cross-reference
  in this document set) and deserves a dedicated, deliberate prompt
  rather than being folded into AEP-007 alongside six new standards
  documents.
- **Alternatives considered:** Execute the AIEF/BIKEVALUATOR split now —
  rejected as too large and risky to bundle with this prompt's other
  changes; better done as its own reviewed step once FS-001 work has
  given us real signal on where the universal/project-specific line
  actually falls.
- **Consequences:** Logged here and in `ai/roadmap/roadmap.md` as a
  future phase item. No action taken on the physical repository
  structure in this execution.

## BUS-0004

- **Timestamp:** 2026-08-02T00:00
- **Context:** The architect supplied a complete, pre-authored external
  documentation set (BRD-001, SDD-001, DBD-001, API-001, ADR-001 through
  ADR-018, UXS-001, DS-001, DDS-001, PEP-001, GOV-001) covering
  BIKEVALUATOR's business requirements, schema, API contracts,
  architecture decisions, UX, design system, engineering standards, and
  governance in full detail.
- **Decision:** Adopt this document as the canonical source of truth for
  BIKEVALUATOR's business/architecture specifics, superseding earlier
  provisional assumptions in FS-000/SDD-000 wherever they conflict. This
  resolves the majority of BDR-001's open questions (see BDR-001 for the
  per-question resolution). New canonical documents
  (`BRD-001-business-requirements.md`, `DBD-001-database-design.md`,
  `API-001-endpoints.md`) are created under `ai/architecture/` to carry
  this content forward in our repository's format.
- **Reasons:** The external document is internally consistent, more
  detailed than our provisional FS-000/SDD-000 drafts, and directly
  answers nearly every open BDR — adopting it removes speculation and
  unblocks Vehicle Master planning.
- **Alternatives considered:** Treat it as reference-only and keep
  FS-000/SDD-000 as authoritative — rejected; the external document is
  more complete and was explicitly supplied to resolve open questions.
- **Consequences:** BRR-001 rules move from Provisional to Approved
  where resolved (BR-0001, BR-0002, BR-0003 remain partially provisional
  only on exact recommendation-threshold numbers — the source document
  does not give numeric thresholds either, only qualitative labels). Two
  new business rules are added: BR-0009 (round final price to nearest
  ₹10) and BR-0010 (repair costs are fixed ₹ amounts per option, not
  percentages — confirms ADR-018 in the source document). FS-000/SDD-000
  remain valid as our internal planning documents but must not be read
  as contradicting BRD-001/DBD-001/API-001 where they overlap.

### BDR-001 Resolution Summary (per original question)

| BDR | Question | Resolution | Source |
|---|---|---|---|
| BDR-0001 | Repair cost table ownership | Vehicle Master and Repair Cost Master are sibling modules — both Admin/Super-Admin-owned, neither nested inside the other (`repair_components`/`repair_options` tables, distinct from `valuation_master`) | DBD-001 §7, §9 |
| BDR-0002 | Margin per-dealer or global | Global — one Margin value per Year+Variant, stored in `valuation_master` | DBD-001 §8, BRD-001 §7 |
| BDR-0003 | Scrap Value derivation | Independently maintained field (`scrap_value`), not derived from MSP | DBD-001 §8 |
| BDR-0004 | Recommendation thresholds | Still not numerically specified — only qualitative labels (Good Buy/Average/Scrap) confirmed; exact % cutoffs remain open | UXS-001 §7 |
| BDR-0005 | Brand/Model/Variant decomposition | Confirmed as separate normalized tables (`brands`, `models`, `variants`) | DBD-001 §7 |
| BDR-0006 | Status enum implementation | Resolved differently than proposed: use a simple `active` boolean + soft-delete fields (`deleted_at`, `deleted_by`), not a multi-value enum | DBD-001 §16 |
| BDR-0007 | Search threshold for Vehicle Selector | Not specified — remains open | — |
| BDR-0008 | Brand/Model varying by Year | Not explicitly addressed — cascading dropdown order is Year→Brand→Model→Variant but filtering behavior isn't specified; remains open | UXS-001 §5 |
| BDR-0009 | Admin vs Super Admin | Resolved — only two roles exist: **Dealer** and **Super Admin**; no separate plain "Admin" tier | BRD-001 §8, SDD-001 §5 |
| BDR-0010 | Pricing edit audit/versioning | Resolved via `effective_from`/`effective_to`/`active` columns on `valuation_master` (temporal versioning), not a separate history table | DBD-001 §21 |
| BDR-0011 | Distinct "Archived" state | Resolved — no distinct Archived state; superseded by the `active` boolean + soft-delete approach (see BDR-0006) | DBD-001 §16 |
| BDR-0012 | E-AUTHZ-001 in error catalogue | Not addressed in the source document; still an open recommendation | — |
| BDR-0013 | Offline capability for v1 | Resolved — not supported in v1; internet required | UXS-001 §11 |
| BDR-0014 | Multi-region/multi-currency | Resolved — India-wide deployment, single currency (₹); no multi-currency support indicated | BRD-001 §12 |

**New rules discovered, not previously captured:**
- **BR-0009:** Final Purchase Price is rounded to the nearest ₹10.
- **BR-0010:** Repair costs are fixed ₹ deduction amounts per option
  (OK/Partial/Full), never percentage-based (confirms ADR-018).

**Still open, not resolved by this document:** BDR-0004 (exact
thresholds), BDR-0007 (search threshold), BDR-0008 (Year-based Brand/
Model filtering), BDR-0012 (E-AUTHZ-001 formalization).

## AI-0005

- **Timestamp:** 2026-08-02T00:00
- **Context:** AFR-001 certified FS-001 was not yet ready, consolidating
  18 open questions (OQ-01 through OQ-18) across BDR-001, DDD-001, and
  SSD-001, of which OQ-08 and OQ-14 were Critical blockers and OQ-06 was
  High priority. This prompt (ADR-001) converts every one of those open
  questions into a formally numbered, owned, dated Architecture
  Decision, so the architect can approve or revise them as a single
  batch rather than scattered open items across four documents.
- **Decision:** Introduce a new decision-category prefix, **`ENG`**
  (Engineering Decision), extending ARC-0001's original scheme (`BUS`,
  `ARC`, `DB`, `API`, `SEC`, `OPS`, `AI`) to cover implementation-pattern
  choices (UI thresholds, retry/idempotency policy, session handling)
  that don't cleanly belong to Business/Architecture/Security/
  Operations. Then log all 17 substantive open questions below as
  individually numbered decisions (`BUS-0005`..`BUS-0007`,
  `ARC-0005`..`ARC-0010`, `ENG-0001`..`ENG-0004`, `SEC-0001`..`SEC-0003`,
  `OPS-0001`), each with a Recommended Option and **Final Status:
  Pending Human Approval** — none are self-approved by this decision;
  per Constitution Rule 10, only the architect can move them to
  Approved. (OQ-05 was AFR-001's own placeholder row — no distinct
  question existed there, so it is formally closed with no decision
  needed.)
- **Reasons:** A single batch of numbered, owned decisions is faster to
  approve or amend than re-reading three separate open-question lists;
  giving each item a citable ID (e.g. `SEC-0001`) lets future documents
  reference the resolution directly instead of re-explaining context.
- **Alternatives considered:** Leave the 18 items as open questions
  inside AFR-001/DDD-001/SSD-001 — rejected, they'd never gain a citable
  decision ID and would keep being re-described rather than resolved.
  Force every item into the existing `BUS/ARC/DB/API/SEC/OPS/AI`
  categories without adding `ENG` — rejected, several items (e.g. OQ-02
  Vehicle Selector search threshold) don't fit any of them honestly.
- **Consequences:** Once the architect approves each row below (or
  amends it), the corresponding `Approved` status should be recorded
  directly in this decision's matrix (updating "Final Status" per row)
  rather than creating a second decision entry. FS-001 becomes
  buildable once `SEC-0001` (OQ-08) and `ENG-0003` (OQ-14) are approved;
  `ARC-0007` (OQ-06) should ideally be resolved alongside them.

### Decision Matrix (all 17 items from AFR-001's Open Question Resolution Matrix)

| Decision ID | Category | Description (from OQ) | Recommended Option | Key Alternative & Trade-off | Human Approval Required | Final Status | Owner | Priority | Blocking Module |
|---|---|---|---|---|---|---|---|---|---|
| BUS-0005 (OQ-01) | Business | Exact recommendation-band thresholds (BR-0003) | Confirm 90/75/60% as final | Admin-configurable thresholds — more flexible, but adds config surface for a value not yet used in anger | Yes | **Approved** (ABL-001, 2026-08-02) | Human (architect) | Medium | FS-002 |
| ARC-0005 (OQ-03) | Architecture | Does Brand/Model availability vary by Year? | No Year-based filtering in v1 | Filter by Year throughout — prevents dead-end selections, but adds a `year` param to every Vehicle Master endpoint for no confirmed need | Yes | **Approved** (ABL-001, 2026-08-02) | Human (architect) | Medium | FS-001 |
| ARC-0006 (OQ-04) | Architecture | Formalize `E-AUTHZ-001` in the error catalogue? | Yes, add to SDD-000 §8 now | Keep it Vehicle-Master-local — cheaper now, but risks each future module inventing its own authorization error code | Yes | **Approved** (ABL-001, 2026-08-02) | Human (architect) | Low | Cross-cutting |
| ARC-0007 (OQ-06) | Architecture | API-000 vs. API-001 response-envelope conflict | API-001's `success`/`message`/`data`/`errors` shape wins; revise API-000 to match | Keep API-000's `data`/`meta`/`errors` shape and revise API-001 instead — equally valid, but API-001 is the later, concrete, architect-supplied shape | Yes | **Approved** (ABL-001, 2026-08-02) | Human (architect) | **High** | FS-001 |
| ARC-0008 (OQ-07) | Architecture | Is `Vehicle` persisted in v1? | Ephemeral only (no v1 table) | Persist a minimal Vehicle-selection row now — simpler v2 migration later, but no confirmed v1 need | Yes | **Approved** (ABL-001, 2026-08-02) | Human (architect) | Medium | FS-002 |
| SEC-0001 (OQ-08) | Security | How is Dealer vs. SuperAdmin distinguished at the data level? | Add a `role` (or `is_super_admin`) column to `users` in DBD-001 | Separate `super_admins` table — cleaner separation, but overkill for a two-role system and complicates the single-`users` login flow (§3.1 SSD-001) | Yes | **Approved** (ABL-001, 2026-08-02) | Human (architect) | **Critical** | FS-001 |
| ARC-0009 (OQ-09) | Architecture | Is `RepairAssessment` persisted independently in v1? | Transient only (matches stateless `/valuation/calculate`) | Persist per-attempt for resume/retry — better UX on network loss, but no v1 table exists and adds scope | Yes | **Approved** (ABL-001, 2026-08-02) | Human (architect) | Low | FS-002 |
| ARC-0010 (OQ-10) | Architecture | Is Brand the correct aggregate root over Model/Variant? | Accept as documented in DDD-001 | Treat Brand/Model/Variant as three independent aggregates — equally defensible, no source document mandates either | No (can proceed; revisit if wrong) | **Approved** (ABL-001, 2026-08-02) | Human (architect) | Low | FS-001 (code organization only) |
| BUS-0006 (OQ-11) | Business | Formalize "one ValuationMaster per Year+Variant" as a numbered rule? | Yes, add `BR-0011` | Leave as DB-constraint-only — already enforced regardless, but harder to cite from future FS documents | Yes | **Approved** (ABL-001, 2026-08-02) | Human (architect) | Low | FS-001 |
| OPS-0001 (OQ-12) | Operational | Notification/Analytics/Future-AI domain objects not yet modeled | Defer — no action needed now | Model them now speculatively — premature, no requirements exist yet | No | **Approved** (ABL-001, 2026-08-02, informational only) | Human (architect) | Low | Future scope |
| ENG-0001 (OQ-02) | Engineering | Vehicle Selector search threshold | Always use type-ahead search | Plain dropdown below N items, type-ahead above — avoids a maintained threshold constant, at the cost of one extra widget-choice branch | Yes | **Approved** (ABL-001, 2026-08-02) | Human (architect) | Low | FS-001 (Flutter UI only) |
| ENG-0002 (OQ-13) | Engineering | Is `/valuation/calculate` idempotent/safely retryable? | No idempotency key needed in v1 (stateless, no writes — naturally safe to retry) | Add an idempotency key now — future-proofs for when it starts writing (v2), but unnecessary complexity today | Yes | **Approved** (ABL-001, 2026-08-02) | Human (architect) | Medium | FS-002 |
| ENG-0003 (OQ-14) | Engineering | Transaction/concurrency policy for ValuationMaster/RepairOption admin writes | One DB transaction per write (versioned row + AuditLog entry together); optimistic concurrency via an `updated_at`/version check | Pessimistic row-level locking — simpler mental model, but risks lock contention on a low-write-volume table for no real benefit | Yes | **Approved** (ABL-001, 2026-08-02) | Human (architect) | **Critical** | FS-001 |
| SEC-0002 (OQ-15) | Security | Payment webhook idempotency and reconciliation | Adopt the principle now (dedupe by gateway `transaction_id`); detailed design deferred to FS-006 | Rely solely on the gateway's own delivery guarantees — simpler, but exposes BIKEVALUATOR to duplicate-activation bugs if the gateway ever redelivers | Yes | **Approved** (ABL-001, 2026-08-02) | Human (architect) | Medium | FS-006 |
| BUS-0007 (OQ-16) | Business | Is an in-flight Valuation honored if Subscription expires mid-flow? | Honor the in-flight request (check expiry only at flow start) | Re-check expiry at every step — stricter, but surprises the Dealer mid-calculation for a rare timing edge case | Yes | **Approved** (ABL-001, 2026-08-02) | Human (architect) | Low | FS-002/FS-005 |
| SEC-0003 (OQ-17) | Security | OTP resend/rate-limiting | Adopt the principle now (e.g. max 3 resends/hour); detailed design deferred to FS-003 | No rate limit — simplest, but exposes the SMS provider to abuse/cost | Yes | **Approved** (ABL-001, 2026-08-02) | Human (architect) | Medium | FS-003 |
| ENG-0004 (OQ-18) | Engineering | Session/token refresh vs. full re-auth on JWT expiry | Full re-auth on expiry (no refresh-token flow in v1) | Silent refresh-token flow — better UX, but adds a new token type and rotation policy with no confirmed v1 need | Yes | **Approved** (ABL-001, 2026-08-02) | Human (architect) | Medium | FS-003 |

**Approval event:** On 2026-08-02, the Human Architect approved all 17 rows above as recommended, in a single blanket approval issued as part of ABL-001 (Architecture Baseline Finalization) — no row was amended from its Recommended Option. This is recorded here as the citable approval event; see `ai/architecture/ABL-001-architecture-baseline.md` for the full Baseline v1.0 record and per-document propagation detail.

### Risk Register (new risks surfaced by this decision batch)

| Risk ID | Description | Impact | Probability | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| RISK-ADR-01 | Authorization mechanism (SEC-0001) is approved but implemented inconsistently across Admin endpoints (some check `role`, some check something else) | High — could allow a Dealer to write master data | Medium | Centralize the check in one `AuthorizationPolicy` service (SSD-001 §8 placeholder), never inline per-endpoint | Backend Lead (future) | Open — SEC-0001 approved; risk now live, carries into FS-001 implementation |
| RISK-ADR-02 | Concurrency policy (ENG-0003) is approved on paper but not actually enforced in code, leading to silent lost updates on ValuationMaster | High — pricing data corruption | Low-Medium | Add an automated test asserting a stale-write rejection (per the future TEST-001 revision recommended in AFR-001 §4) | QA/Backend Lead (future) | Open — ENG-0003 approved; risk now live, carries into FS-001 implementation |
| RISK-ADR-03 | API-001's envelope (ARC-0007) is adopted, but API-000 is never actually revised to match, leaving a stale, contradictory document in the repo | Medium — confuses future readers/agents | Medium | Track "revise API-000" as an explicit follow-up task in `ai/todo/modules/global.md`, not just a decision note | Documenter role | **Closed** — API-000 v1.1 revised to match under ABL-001, see Decision Propagation Report |
| RISK-ADR-04 | Recommendation thresholds (BUS-0005) are confirmed at 90/75/60% without real valuation data to validate them, and turn out to misclassify real vehicles once dealers start using the system | Medium — wrong buy signal is the product's core value proposition | Medium | Treat thresholds as easily revisable (a config value, not hardcoded in multiple places) so a future correction is cheap | Product Owner | Open — accepted risk; BUS-0005 approved as recommended |
| RISK-ADR-05 | Payment webhook idempotency principle (SEC-0002) is deferred to FS-006 in detail, but FS-006 implementation forgets to actually implement dedup, causing duplicate Subscription activations from a redelivered webhook | High — billing/subscription integrity | Low | FS-006's Definition of Done must explicitly require a webhook-dedup test case | Backend Lead (future) | Open — tracked for FS-006, not FS-001 |

### Architecture Lock Readiness

**Can architecture become LOCKED once this decision batch is approved?**
**Content-wise, yes** — every previously open question that blocked
FS-001 (`SEC-0001`, `ENG-0003`) or was High priority (`ARC-0007`) now
has a concrete, recommended answer; approving them removes all
remaining architectural ambiguity for Vehicle Master. **Formally, no —
not to the "Locked" status specifically.** Per Constitution Rule 20,
`Locked` means "implementation has begun," which is still true only
once FS-001 code exists. Approving this decision batch should move the
affected documents (DBD-001, API-001, BRR-001, SDD-000 §8) to
`Approved` — the correct terminal pre-implementation state — with
`Locked` following naturally once FS-001 implementation actually
starts. This is the same distinction raised in AFR-001 §6/Checklist
item #9 and is carried forward unchanged here rather than silently
resolved a second, different way.

**Update (ABL-001, 2026-08-02):** All 17 decisions above are now
Approved. Per this exact reasoning, the affected documents were moved
to `Approved` status (they already carried that status; no regression
to `Needs Review`/`Draft` was needed since propagation only added
content) as part of Baseline v1.0 — see
`ai/architecture/ABL-001-architecture-baseline.md`. None were marked
`Locked`; that remains reserved for when FS-001 implementation begins.

## AI-0006

- **Timestamp:** 2026-08-02T00:00
- **Context:** With Architecture Baseline v1.0 established (ABL-001),
  FS-001 (Vehicle Master) and every module FS after it needed one
  identical engineering standard for structure, readiness, and
  completion — otherwise each module FS risks reinventing its own
  format, making cross-module review inconsistent. This was
  commissioned directly by an explicit, itemized prompt (FSS-000)
  naming the exact 21 mandatory sections required.
- **Decision:** Adopt `ai/architecture/fs/
  FSS-000-functional-specification-standard.md` as the mandatory
  structure, Definition of Ready, Definition of Done, Architecture
  Compliance Checklist, and Cross-FS Dependency Rules for every FS
  document from FS-001 onward (FS-000 is explicitly exempt — it
  predates this standard and serves a different purpose). Add
  Constitution **Rule 22** requiring conformance and gating `Approved`
  status on FSS-000's Definition of Done. Create `ai/templates/
  fs-template.md` as the literal copy-paste skeleton.
- **Reasons:** The 21-section list was specified verbatim by the
  architect in the commissioning prompt, so that part carries its own
  authorization; the Definition of Ready/Done, Compliance Checklist,
  and Cross-FS Dependency Rules are this decision's own drafting and
  are flagged `Needs Review` on the document itself pending explicit
  sign-off, consistent with Rule 10 — commissioning the standard is not
  the same as pre-approving every internal judgment call made while
  writing it.
- **Alternatives considered:** Let each FS document define its own
  structure ad hoc — rejected, this is exactly the drift FSS-000 exists
  to prevent, and was explicitly what this prompt asked to avoid.
- **Consequences:** FS-001 becomes the first document required to
  conform. No FS may reach `Approved` without satisfying FSS-000's DoD
  (Rule 22 ties this to the existing Document Approval Workflow, Rule
  20).

## AI-0007

- **Timestamp:** 2026-08-02T00:00
- **Context:** Alongside FSS-000, the architect proposed — as an
  explicit "Final Recommendation" inside the same prompt, not a
  speculative aside — a fixed five-dimension quality rubric to evaluate
  every future AI-produced artifact (FS, backend, Flutter, tests,
  deployment), going beyond the existing three mandatory reports
  (Prompt Execution, Repository Health, Architecture Impact).
- **Decision:** Adopt the rubric as Constitution **Rule 23**: every
  future artifact is evaluated and that evaluation reported against
  Architecture Compliance, Business Compliance, Engineering Quality,
  Repository Governance, and Implementation Readiness, alongside (not
  replacing) the existing mandatory reports.
- **Reasons:** Unlike the 17 `AI-0005` items (open architectural
  questions the AI could not resolve unilaterally), this proposal came
  from the human architect — the approving authority — stated
  affirmatively within an executable prompt rather than as an open
  question. Adopting it directly is consistent with Rule 10 (the human
  is the one approving here, not the AI self-approving); it is also
  low-risk and reversible (a review lens, not an irreversible action).
- **Alternatives considered:** Treat it as a mere suggestion and ask
  before adopting, per the earlier pattern used for the "5-part review
  framework" strategic suggestion in ADR-001 — rejected this time,
  since that prior offer was explicitly speculative ("if you'd like,
  say so explicitly"), whereas this prompt's phrasing is a direct,
  dated instruction ("from this point onward"). Flagged here
  transparently in case the architect intended it as discussion rather
  than direction — easy to revert (Superseded) if so.
- **Consequences:** Every future Prompt Execution Report must include
  this five-dimension self-assessment starting with FS-001.

## AI-0008

- **Timestamp:** 2026-08-02T00:00
- **Context:** Alongside commissioning ISP-001 (the concrete Vehicle
  Master implementation specification), the architect proposed — again
  as a direct, dated recommendation within the executable prompt, the
  same pattern as `AI-0007` — inserting a formal Implementation
  Specification stage between FS and code: **Architecture → FS → ISP →
  Code → Testing**.
- **Decision:** Adopt Constitution **Rule 24**: every module requires
  an ISP (backend API contract, DTOs, Repository interfaces, Service
  interfaces, Flutter contract, Validation Matrix, Test Matrix) between
  its Approved FS and any implementation code. An ISP may not introduce
  new APIs, change business rules, or alter architecture.
- **Reasons:** Same basis as `AI-0007` — the human architect, the
  approving authority, stated this as direct forward-looking process
  direction rather than an open question, and it is low-risk/reversible
  (a documentation-stage addition, not an irreversible action).
- **Alternatives considered:** Treat it as a suggestion pending
  separate confirmation — rejected for the same reason `AI-0007` wasn't:
  the phrasing ("I recommend adopting... From this stage onward") is a
  direct instruction, not "if you'd like."
- **Consequences:** FS-002 onward will each need their own ISP before
  implementation begins. `ISP-001-vehicle-master-implementation-
  specification.md` is the first instance, created this round.

## AI-0009

- **Timestamp:** 2026-08-02T00:00
- **Context:** EP-001 ("Engineering Package") was commissioned as the
  bridge between FS-001 and production code, described as producing
  "the folder structure, migration sequence, ... file inventory" — but
  its prompt's "Read First" list did not include ISP-001, and its
  narrative didn't acknowledge Rule 24's just-established Architecture
  → FS → ISP → Code → Testing pipeline. EP-001's actual content overlaps
  heavily with ISP-001 but goes one level more concrete (real files/
  folders/migrations vs. contracts/signatures).
- **Decision:** Record Constitution **Rule 25**: the pipeline is
  clarified as **Architecture → FS → ISP → EP → Code → Testing**, with
  EP building on (not replacing) its module's ISP. This is recorded as
  a **proposed reconciliation**, not a self-approved resolution — the
  architect may instead have intended EP to replace ISP, or something
  else; flagged for explicit confirmation in the Prompt Execution
  Report rather than silently picked.
- **Reasons:** Silently treating EP-001 as a from-scratch document
  risked contradicting the Repository/Service interfaces ISP-001
  already defined; silently ignoring the gap between the two prompts'
  instructions would leave Rule 24 stale without explanation. Making
  the reconciliation explicit, while still flagging it as unconfirmed,
  serves both continuity and transparency.
- **Alternatives considered:** Treat EP-001 as superseding ISP-001
  entirely (rejected — EP-001's own content cites ISP-001's contracts
  throughout, implying continuation, not replacement). Say nothing and
  let the pipeline rules silently conflict (rejected — contradicts this
  project's established discipline of surfacing drift rather than
  letting documents go stale against each other, as done for SDD-000 §4
  and §9 in ABL-001).
- **Consequences:** EP-002 onward (Valuation Engine and later modules)
  will follow the same ISP → EP sequencing unless the architect amends
  Rule 25.

## AI-0010

- **Timestamp:** 2026-08-02T00:00
- **Context:** EP-001's commissioning prompt states, as a direct
  instruction: "From EP-001 onward, I'll review it as a Chief Technology
  Officer (CTO)," naming ten review dimensions (Engineering quality,
  Scalability, Performance, Maintainability, Security, Code
  organization, Production readiness, Technical debt, Developer
  experience, AI-generated code quality) and declaring the project is
  "officially leaving the planning phase and entering the engineering
  phase."
- **Decision:** Adopt Constitution **Rule 26**: a ten-dimension
  CTO-level rubric applies to every deliverable from EP-001 onward,
  layered onto (not replacing) Rule 23's five-dimension Fixed Quality
  Rubric — specifically refining Rule 23's "Engineering Quality"
  dimension into CTO-level specificity now that code is imminent.
- **Reasons:** Same basis as `AI-0007`/`AI-0008` — a direct, dated
  instruction from the human architect (the approving authority), not a
  speculative suggestion; adopted directly rather than held pending.
- **Alternatives considered:** Treat the ten dimensions as replacing
  Rule 23 entirely — rejected; nothing in the prompt says Architecture
  Compliance/Business Compliance/Repository Governance/Implementation
  Readiness stop mattering, only that Engineering Quality now gets
  reviewed at CTO depth.
- **Consequences:** Every future Prompt Execution Report must include a
  CTO-rubric self-assessment alongside the existing Rule 23
  self-assessment, starting with this EP-001 round.

## DEC-0001

- **Timestamp:** 2026-08-02T00:00
- **Context:** Repository was empty. Needed a controlled foundation before
  any BIKEVALUATOR feature work begins, so that AI-assisted development is
  auditable, versioned, and safely separated from production code.
- **Decision:** Adopt the `ai/` framework structure (constitution,
  decisions, todo, changelog, session, prompts, reviews, templates) as the
  permanent process layer for this repository, per AEP-001.
- **Reasons:** Establishes a repeatable session bootstrap/handoff protocol;
  prevents AI process artifacts from leaking into deployable code; gives
  humans a durable audit trail of decisions and reasoning.
- **Alternatives considered:** (a) No formal framework, rely on chat
  history only — rejected, not durable or auditable. (b) Store process
  docs inside `docs/` alongside user-facing docs — rejected, conflates
  audience and risks accidental inclusion in doc-site builds.
- **Consequences:** All future significant decisions must be logged here;
  all prompts must be versioned under `ai/prompts/`; production code
  cannot begin until a first functional specification is drafted and
  approved (see TODO-0004).

## DEC-0002

- **Timestamp:** 2026-08-02T00:00
- **Context:** Needed a way to keep the constitution reusable across future
  projects while still capturing BIKEVALUATOR-specific constraints.
- **Decision:** Tag every constitution rule as Universal or
  Project-specific, each with a one-line rationale.
- **Reasons:** Lets this same `ai/` framework be copied into future
  repositories as a starting template without manual pruning of
  project-specific assumptions.
- **Alternatives considered:** Single undifferentiated rule list — rejected,
  harder to reuse and harder to know what's safe to change per-project.
- **Consequences:** Any new rule added to the constitution must be tagged
  on creation.

## DEC-0003

- **Timestamp:** 2026-08-02T00:00
- **Context:** Production code root not yet decided in detail (`src/` vs
  `app/`), and no domain model exists yet.
- **Decision:** Use `src/` as a placeholder production root, created empty
  during bootstrap. No business logic, UI, or API code is written in this
  phase.
- **Reasons:** Keeps folder structure predictable now while leaving room to
  rename before first real code lands.
- **Alternatives considered:** Deferring folder creation entirely — rejected,
  the AEP-001 spec asks for a skeleton to exist now.
- **Consequences:** `ai/constitution/constitution.md` Rule 12 must be
  revisited and confirmed/updated once the first functional spec is
  approved.
