# Roadmap — BIKEVALUATOR

High-level sequencing of engineering-framework and product phases. Detail
lives in `ai/architecture/pep` once drafted; this file is the top-level
index.

## Phase 0 — Foundation (complete, approved with minor improvements)

- [x] AEP-001: Repository bootstrap.
- [x] AEP-002: Enterprise AI engineering operating system.
- [x] AEP-003: Domain confirmed — used two-wheeler valuation platform,
      B2B SaaS, dealer-focused, centralized pricing engine, subscription
      model. Stack: Flutter + Django + PostgreSQL.
- [x] FS-000: Core Domain & Valuation Business Specification (the
      business DNA every module depends on).
- [x] AEP-004: SDD-000 Domain Architecture & Entity Model (domain model,
      entity catalogue, state machines, module boundaries, event flow,
      constraints, NFRs, error catalogue, traceability matrix).
- [x] AEP-005: Document Review Protocol (DRP-001) — review-package.md,
      file classification, document metadata/status standard.
- [x] AEP-006: Business Rule Registry (BRR-001), Decision Traceability
      Matrix, Data Dictionary convention, API-000 standards, Document
      Approval Workflow, Pre/Post-Execution Checklists.
- [x] AEP-007: Engineering Standards (NS-001, CSS-001, DOC-001, TEST-001,
      LOG-001, SEC-001) + `ai/governance/` operational standards;
      applied AR-001 revisions to BRR-001 and Data Dictionary; FS-000,
      SDD-000, BRR-001, API-000 moved to Approved.
- [x] BUS-0004: adopted architect-supplied BRD-001/DBD-001/API-001 as
      canonical business/schema/API documents, resolving 10 of 14 open
      BDRs (Margin scope, Scrap Value derivation, Brand/Model/Variant
      decomposition, roles, offline/currency scope, status modeling,
      pricing versioning) and surfacing 2 new rules (BR-0009 rounding,
      BR-0010 fixed repair costs).
- [x] DDD-001: canonical business domain model (bounded contexts,
      objects, aggregates, value objects, events, services, business-
      level diagrams, traceability matrix) — modeling only, no code.
- [x] SSD-001: canonical system sequence diagrams (actors, 8 flow
      diagrams, business events, state sync model, failure scenarios,
      cross-cutting concerns, policy placeholders, traceability
      matrix) — modeling only, no code.
- [x] AFR-001: Architecture Freeze & Readiness Review — consolidated
      every open question (BDR-001, DDD-001, SSD-001) into a single
      deduplicated matrix (OQ-01 through OQ-18), certified FS-001 is
      **not yet ready** (blocked by OQ-08 role storage and OQ-14
      transaction/concurrency policy — both Critical), recommended
      NS-001/CSS-001/DOC-001/LOG-001 → Approved and TEST-001/SEC-001 →
      Needs Revision (minor), archived 9 completed architecture
      prompts. No document was marked Locked (flagged as a judgment
      call — see AFR-001 §6).
- [x] ADR-001: converted all 18 of AFR-001's open questions into 17
      formally numbered decisions (`BUS-0005..0007`, `ARC-0005..0010`,
      `ENG-0001..0004` [new category], `SEC-0001..0003`, `OPS-0001`)
      under `AI-0005` in `decisions.md`, each with a Recommended Option,
      a 5-entry Risk Register, and an Architecture Lock Readiness
      answer. All Pending Human Approval — nothing self-approved.
- [x] ABL-001: Human architect approved all 17 `AI-0005` decisions as
      recommended (blanket approval, 2026-08-02). Propagated into
      DBD-001 (v1.1: `users.role`, transaction/concurrency policy,
      webhook dedup), API-001 (v1.1: envelope, idempotency, rate-limit,
      re-auth), API-000 (v1.1: envelope revised to match API-001),
      BRR-001 (v1.2: BR-0003 confirmed, BR-0011 added), SDD-000 (v1.1:
      E-AUTHZ-001, stale open-questions corrected), DDD-001 (v1.1: all
      7 open questions resolved, Needs Review → Approved), SSD-001
      (v1.1: 8/9 open questions resolved, Needs Review → Approved).
      Established **Architecture Baseline v1.0**
      (`ai/architecture/ABL-001-architecture-baseline.md`) with a
      Decision Traceability Matrix and a lightweight Architecture
      Change Control Policy for post-Baseline changes. **FS-001 —
      Vehicle Master has no remaining architectural blockers.**
- [x] FSS-000: established the Functional Specification Standard —
      mandatory 21-section structure, Definition of Ready, Definition
      of Done, Architecture Compliance Checklist, Cross-FS Dependency
      Rules (`ai/architecture/fs/
      FSS-000-functional-specification-standard.md`, Needs Review) plus
      a copy-paste skeleton (`ai/templates/fs-template.md`). Added
      Constitution Rule 22 (conformance gates FS `Approved` status) and
      Rule 23 (Fixed Quality Rubric — Architecture/Business/Engineering/
      Governance/Readiness — applied to every future artifact),
      Constitution → v1.5.0. Logged `AI-0006`, `AI-0007`.
- [x] FS-001: drafted the Vehicle Master Functional Specification per
      FSS-000 (`ai/architecture/fs/FS-001-vehicle-master.md`, Status:
      Draft). Scoped to Brand/Model/Variant/Year catalog + ValuationMaster
      (MSP/Margin/Scrap) — Dealer read, Super Admin CRUD; excludes Repair
      Component/Option administration (deferred to FS-004 per SSD-001
      §10). No new API/schema/rule/decision introduced; 5 Open Questions
      surfaced, none block document Approval. Awaiting human review.
- [x] ISP-001: drafted the Vehicle Master Implementation Specification
      (`ai/architecture/isp/ISP-001-vehicle-master-implementation-
      specification.md`, Status: Draft) — backend API contract, DTOs,
      Repository/Service interfaces, 3 Flutter screen contracts,
      Validation Matrix, Test Matrix. Formalized the pipeline as
      **Architecture → FS → ISP → Code → Testing** (Constitution Rule
      24, v1.6.0, `AI-0008`). Flagged that FS-001's own Status field
      still reads Draft despite being referred to as approved — not
      resolved silently either way.
- [x] EP-001: **FS-001 marked Approved and closed** per explicit human
      confirmation. Drafted the Vehicle Master Engineering Package
      (`engineering/packages/EP-001-vehicle-master.md`, Status: Draft
      — first document at this new top-level location, per explicit
      instruction) — Backend/Database/Flutter/API/Validation/Error/
      Test Packages, Development Order, 62-file inventory. Formalized
      the pipeline as Architecture → FS → **ISP → EP** → Code → Testing
      (Constitution Rule 25, v1.7.0, flagged as a proposed
      reconciliation since EP-001's prompt didn't reference ISP-001)
      and adopted a 10-dimension CTO-level review rubric (Rule 26,
      layered onto Rule 23). Two real cross-module blockers surfaced:
      the Flutter state-management library choice, and whether FS-003's
      `users.role` migration must land before Vehicle Master's
      authorization checks are testable end-to-end.
- [x] IMP-001A: **first production code in the repository.** Created
      the Django project (`src/manage.py`, `src/bikevaluator/`) and the
      complete `vehicle_master` app per EP-001: 4 ORM models (with a
      partial-unique-index implementation of BR-0011 and non-negative
      CHECK constraints), migrations `0001`–`0004` in EP-001's exact
      order, 5 fully-implemented repositories (incl. `ValuationMaster`'s
      BR-0007/ENG-0003 versioning + optimistic concurrency), an abstract
      `AuditLogRepository` interface (no concrete Audit module, per
      explicit scope), 2 DI-wired Service skeletons (no business logic
      yet), validators, exceptions, and 37 passing unit tests. REST
      APIs, authentication, valuation logic, and Flutter explicitly
      excluded this round. No architecture/business rule/approved
      document was changed — implementation-level clarifications are
      recorded as Architecture Observations, not new decisions.
- [x] IMP-001A **reviewed by the architect as CTO: 10/10, APPROVED,
      FROZEN.** No further revisions to this phase.
- [x] IMP-001B: **Service-layer business logic implemented.**
      `VehicleCatalogService` and `VehicleMasterAdminService` are no
      longer skeletons — full CRUD + BR-0004 (authorization, new
      `authorization.py`), BR-0007 (versioning), BR-0011 (duplicate
      detection), and ENG-0003 (optimistic concurrency) are enforced
      and tested. Added `tests/fixtures.py` (fake Audit repository/
      Actor) and 4 new test files; expanded repository tests beyond
      initialization-only, per the CTO review's Level 2 recommendation.
      **91/91 tests passing.** REST APIs, authentication, and Flutter
      remain out of scope, per the architect's own "API as thin
      transport over tested services" sequencing rationale.
- [x] IMP-001B **reviewed by the architect (implicit approval via
      issuing IMP-001C immediately after)**; no revisions requested.
- [x] IMP-001C: **REST API layer complete.** All 8 Vehicle Master
      endpoints (4 Dealer: `/vehicles/brands|models|variants|
      configuration`; 4 Admin: `/admin/vehicles` [POST/PUT/DELETE,
      entityType-discriminated for Brand/Model/Variant],
      `/admin/valuation-master` [POST/DELETE]) now live over HTTP,
      mounted at `/api/v1/`. Thin transport only — every view calls
      exactly one Service method; all business logic remains in
      IMP-001B's Service layer. **Two architecture-compliance findings,
      resolved in favor of the Approved documents over this prompt's
      own sketch:** the response envelope (API-000 v1.1's
      `success/message/data`+`errors[]`, not the prompt's
      `success/data`+`errorCode` sketch) and endpoint shapes (API-001's
      query-param/snake_case design, not the prompt's path-param/
      camelCase sketch). **One discovered-and-fixed gap:** ISP-001's
      `UpdateVehicleCatalogEntryRequest` had no way to route
      `PUT`/`DELETE /admin/vehicles/{id}` to the right table — fixed by
      requiring `entityType` as a query param there too. 52 new tests
      (serializers, 3 view-test files, 1 full-lifecycle integration
      test) — **143/143 tests passing total.** Actor identity over HTTP
      uses temporary, explicitly-flagged `X-Actor-Id`/`X-Actor-Role`
      headers (not real auth, pending FS-003); Audit logging over HTTP
      uses a non-persistent in-memory stand-in (real Audit module still
      not implemented).
- [x] IMP-001D: **Vehicle Master Architecture Refinement**, per the
      architect's 8.8/10 review of IMP-001C and their explicit
      recommended sequencing (IMP-001A→B→C→**D (this)**→Approve Vehicle
      Master→FS-002→ISP-002, inserted ahead of jumping straight to
      FS-002). Pure refactor of the REST API infrastructure — no
      business rule, repository, service, validator, schema, or API
      contract changed. Centralized service construction
      (`service_factory.py`, replacing 3 duplicated `_build_*_service()`
      functions); extracted `ActorProvider`/`DummyActorProvider` so the
      temporary header-based actor resolution no longer lives inline in
      views (swappable for a real `AuthenticatedActorProvider` once
      FS-003 exists, with zero view changes); relocated the audit
      stand-in from a view-local `_InMemoryAuditLogRepository` to
      `repositories/noop_audit_log_repository.py`'s `NoOpAuditRepository`;
      introduced `RequestContext` bundling actor/IP (with room for a
      future request/correlation id); replaced entityType `if/elif`
      dispatch with 4 lookup maps. **143/143 tests pass, unmodified** —
      verified beforehand that no test imported the refactored
      internals directly, so this is proof of zero behavior change, not
      an assumption. Explicitly deferred (not in this round's Tasks
      list): splitting `/admin/vehicles` into 3 endpoints,
      response-helper classes, API versioning folder reorg, expanded
      edge-case tests.
- [x] **IMP-001D reviewed and APPROVED (9.6/10)** — "I would consider
      Vehicle Master architecturally stable... I would not request
      another refactoring round before moving on." Recommended
      proceeding directly to ISP-002 while reusing the shared
      infrastructure established for Vehicle Master.
- [x] FS-002: drafted the Valuation Engine Functional Specification per
      FSS-000 (`ai/architecture/fs/FS-002-valuation-engine.md`, Status:
      Draft), continuing the roadmap's established order after the
      architect explicitly chose to proceed here rather than jump ahead
      to Authentication or the Audit module. **Established directly
      from DBD-001:** this module is entirely stateless in v1
      (`valuation_requests` inactive) — the Evaluation state machine
      (SDD-000 §3) is a client-side UI-flow concept, not a persisted
      entity's state. Scoped to Repair Assessment + Calculation
      (BR-0001/BR-0002/BR-0009) + Recommendation (BR-0003/BR-0008);
      excludes Repair Master administration (FS-004) and Subscription
      logic itself (FS-005, doesn't exist yet — flagged as a genuine
      forward dependency). 4 Open Questions surfaced, none block
      Approval. Awaiting human review.
- [x] ISP-002: drafted the Valuation Engine Implementation Specification
      (`ai/architecture/isp/ISP-002-valuation-engine-implementation-
      specification.md`, Status: Draft). Two new Services
      (`ValuationService`, `RecommendationService` — matching SSD-001's
      actor separation), two new read-only Repositories
      (`RepairComponentRepository`/`RepairOptionRepository` — resolving
      FS-002's Open Question #1: this module's implementation creates
      these models, FS-004 extends them later for administration, not
      duplicates). Explicitly reused Vehicle Master's shared
      infrastructure where it genuinely applies (`api_utils.py`,
      `service_factory.py` extended) and explicitly did NOT force-fit
      `ActorProvider`/`RequestContext`/`authorization.py`, since
      Valuation Engine has no Super-Admin-only write at all. Flagged
      (again) that FS-002's Status field still reads Draft despite
      being called "approved."
- [x] EP-002 + IMP-002: Engineering Package + full implementation of
      the Valuation Engine backend (176 tests) and the **first Flutter
      code in the repository** (`mobile/bikevaluator_app`) — Vehicle
      Selector/Repair Assessment/Result screens, end-to-end validated
      on the Android emulator. One real defect found and fixed during
      self-review (network-error message masking on Vehicle Selector).
- [x] IMP-003: imported the architect-supplied real "2W Valuation Calc"
      spreadsheet (86 rows). Discovered repair costs vary per vehicle,
      contradicting DBD-001 §9's global design — surfaced via
      `AskUserQuestion` before coding, resolved as **`AI-0011`**
      (amends DBD-001 §9/BR-0010). New `ValuationRepairCost` table,
      idempotent `import_valuation_master` command. 194/194 tests pass.
- [x] IMP-003A: architect-approved CTO-grade review of IMP-002/IMP-003.
      Judged the `AI-0011` decision sound; found 2 High Priority
      engineering-quality gaps (stale API-001/ISP-002/EP-002 docs, no
      real audit trail) + several Medium/Low (N+1 queries, a redundant
      index, importer robustness).
- [x] IMP-003B: Engineering Stabilization Release closing every High
      Priority finding — real audit trail (**`AI-0012`**, amends
      DBD-001 §2), N+1 fixes, redundant index removed, importer
      hardened, Flutter `ApiClient` centralized with timeout + error
      differentiation, stale docs synced. 211 backend + 11 Flutter
      tests pass. **Awaiting the architect's decision to officially
      freeze this foundation** (Architecture + Vehicle Master +
      Valuation Engine + Data Import + Flutter Client Bootstrap) before
      FS-003 (Authentication) or FS-004 (Admin) begins.

## Phase 1 — Core Domain Build-out (module order revised in AEP-003; SDD-000 gate added in AEP-004; BRR-001/API-000 conformance added in AEP-006; NS-001/CSS-001 conformance added in AEP-007; Baseline v1.0 established in ABL-001)

**Gate status as of ABL-001 (2026-08-02):** FS-000, SDD-000, BRR-001,
API-000, DBD-001, API-001, DDD-001, and SSD-001 are all Approved; the
3 business-rule questions (Margin scope, Scrap Value derivation,
recommendation thresholds) were resolved via BUS-0004/BUS-0005.
**NS-001 and CSS-001 remain `Needs Review`** — AFR-001 recommended
Approved for both, but that recommendation itself was never explicitly
confirmed by the architect (it is separate from the `AI-0005` batch
ABL-001 just resolved). This is a non-blocking, deliberately-tracked
gap — see the Baseline document's Outstanding Deferred Decisions — but
should be closed out before FS-001 is called complete.

## Future Phase — AIEF / BIKEVALUATOR Separation (planned, not scheduled)

Per AI-0004: eventually split this repository's universal AI Engineering
Framework assets (Constitution, Prompt Workflow, Review Protocol,
Naming/Code-Style Standards, Templates, Governance) from BIKEVALUATOR-
specific content (Business Rules, FS documents, Domain Model, module
implementations), so future products can bootstrap from the same
framework. Not executed yet — deliberately deferred to its own reviewed
prompt.

Reordered from the original Authentication-first plan because the
valuation engine is the product's core IP — if it's wrong, nothing built
on top of it matters. Authentication is a supporting module and can come
later. Every module FS below must conform to
`ai/architecture/sdd/SDD-000-domain-architecture.md`.

1. [~] FS-001 — Vehicle Master — brand/model/variant/year catalog, MSP
       data. Specification **Approved and closed**; ISP-001 and EP-001
       (Draft) produced. **IMP-001A (Backend Foundation) complete**:
       Django project + `vehicle_master` app at `src/` — models,
       migrations, repositories fully implemented; Services are
       DI-wired skeletons only (business logic TODO). 37/37 tests
       passing. **IMP-001B (Service-layer business logic) and IMP-001C
       (REST API layer) complete** — all 8 endpoints live at `/api/v1/`,
       143 tests passing. **IMP-001D (Architecture Refinement) complete**
       — pure refactor, same 143 tests still passing unmodified.
       **IMP-001D reviewed and APPROVED (9.6/10) — Vehicle Master is
       considered architecturally stable.** No authentication/Flutter
       yet.
2. [x] FS-002 — Valuation Engine — calculation engine, repair components
       (read-only), scrap validation, recommendation logic (per FS-000,
       SDD-000). **EP-002/IMP-002 complete**: full backend
       implementation (176/176 tests) plus a new Flutter client
       (`mobile/bikevaluator_app`, first Flutter code in the
       repository) covering Vehicle Selection → Repair Assessment →
       Calculate → Result, validated end-to-end on the Android
       emulator. Awaiting human review.
3. [ ] FS-003 — Authentication — dealer/admin login, roles.
4. [ ] FS-004 — Admin — back-office management of vehicle master, pricing, users.
5. [ ] FS-005 — Subscription — plan/tier management for dealer access.
6. [ ] FS-006 — Payments — billing for subscriptions.

## Phase 2 — Reporting & Polish (not started)

Dealer-facing valuation reports, UI polish, design system consolidation.

## Phase 3 — Future Scope (not started, see FS-000 §9)

AI-assisted pricing, OCR, VIN recognition, photo-based inspection,
inventory management, CRM, analytics.

## Phase 4 — Hardening & Launch Readiness (not started)

Security review, QA pass, deployment prompts.
