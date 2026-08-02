# BIKEVALUATOR — AI Engineering Constitution

Version: 1.7.0
Established: 2026-08-02
Last amended: 2026-08-02 (EP-001 — added Rules 25–26, Engineering Package Pipeline Stage + CTO-Level Engineering Review Rubric)
Status: Active

This document is the permanent governing rule set for how AI-assisted
development happens in the BIKEVALUATOR repository. It supersedes ad-hoc
conventions. Changes to this constitution are themselves decisions and must
be logged in `ai/decisions/decisions.md`.

Each rule is tagged **[Universal]** (reusable across any future project) or
**[Project-specific]** (particular to BIKEVALUATOR).

---

## 1. Repository Separation Rule — [Universal]

AI framework files (`ai/**`) must remain outside production/runtime folders
(`src/`, `app/`, or equivalent). Prompts, decisions, todo logs, changelogs,
and session state must never be imported by, bundled into, or deployed as
part of the application. Build tooling must be able to exclude `ai/**` from
any deployment artifact.

**Why universal:** every project benefits from a hard boundary between
"how we think and decide" and "what ships to users."

## 2. Universal vs Project-Specific Rule — [Universal]

Every rule in this constitution (and in future rules added to it) must be
tagged as **Universal** or **Project-specific**, with a one-line reason.
This lets the framework be reused as a template for future repositories
without dragging along BIKEVALUATOR-only assumptions.

**Why universal:** enables this constitution to seed future projects.

## 3. File Header Rule — [Universal]

Every source file created in this project must begin with a first-line
comment block containing:

```text
// Full Path: <absolute or repo-root-relative full path>
// Relative Path: <path relative to nearest module root>
// Module: <module/package/component name>
// Purpose: <one-line description>
```

Adapt the comment syntax to the language (`#`, `--`, `/* */`, etc.) but keep
the four fields and their order consistent.

**Why universal:** consistent file headers aid navigation and AI context
loading in any codebase.

## 4. Commenting Rule — [Universal]

Comments must explain **why** something exists, **how** it's used, and any
**business rule linkage** — not restate what the code already says. Avoid
comments that merely repeat the code in prose.

**Why universal:** high-value comments reduce onboarding cost regardless of
project domain.

## 5. Timestamp Rule — [Universal]

All entries added to `todo.md`, `decisions.md`, `changelog.md`, and
`session-state.md` must include an ISO-like timestamp (`YYYY-MM-DD` or
`YYYY-MM-DDTHH:MM`).

**Why universal:** chronological traceability is required for any audit
trail, independent of domain.

## 6. Decision Logging Rule — [Universal]

Any important product, architecture, or implementation choice must be
recorded in `ai/decisions/decisions.md` using the fields: decision id,
timestamp, context, decision, reasons, alternatives considered,
consequences. Use `ai/templates/decision-template.md`.

**Why universal:** prevents re-litigating settled choices and preserves
reasoning for future maintainers (human or AI).

## 7. To-Do Logging Rule — [Universal]

All live tasks are tracked in `ai/todo/todo.md` with: timestamp, status,
owner, task, priority, notes, next action. Use
`ai/templates/todo-template.md`.

**Why universal:** a single visible task ledger keeps humans and AI aligned
on current state regardless of project.

## 8. Prompt Versioning Rule — [Universal]

All prompts used to drive meaningful AI work must be versioned and stored
under `ai/prompts/`, registered in `ai/prompts/prompt-index.md`, with:
prompt id, version, date, purpose, output expectation, linked decision ids.
Use `ai/templates/prompt-template.md`.

**Why universal:** reproducibility of AI-driven work requires knowing
exactly what prompt produced what output.

## 9. Session Bootstrap Rule — [Universal]

Every AI session should **begin** by reading, in order: constitution,
decisions, todo, session-state, prompt index. Every AI session should
**end** by updating: todo, session-state, changelog, and any new decisions.

**Why universal:** stateless AI sessions need an explicit, repeatable
bootstrap/handoff protocol to stay coherent across time.

## 10. Approval Rule — [Universal]

AI may draft and propose (code, decisions, documents, plans). Humans
approve. No autonomous production deployment, irreversible action, or
business assumption may be taken without explicit human sign-off.

**Why universal:** keeps human accountability for consequential actions
regardless of how capable the tooling becomes.

## 11. BIKEVALUATOR Domain Placeholder Rule — [Project-specific]

Until the first functional specification is approved (see
`ai/todo/todo.md`), no business logic, UI screens, or backend APIs specific
to bike evaluation are to be implemented. This bootstrap phase is
structure-only.

**Why project-specific:** BIKEVALUATOR's actual domain requirements
(vehicle data model, evaluation criteria, scoring rules) are not yet
defined and are unique to this product.

## 12. Production Root Rule — [Project-specific]

BIKEVALUATOR's production code root is `src/` (created empty during
bootstrap; adjust here if the team later chooses `app/` or another
convention). This rule must be updated the moment that choice is made.

**Why project-specific:** the concrete folder name is a BIKEVALUATOR
convention, not a universal law.

## 13. Prompt Execution Report Rule — [Universal]

Every prompt execution must end with a standardized Prompt Execution
Report covering: prompt metadata (id, version, date, status), files
created, files modified, files moved, decisions added, TODO updates,
changelog updates, session updates, memory updates, context updates,
assumptions made, open questions, risks found, recommendations, and the
next suggested prompt. See `ai/templates/prompt-execution-report-template.md`.

**Why universal:** a fixed report format is what makes the closed-loop
review step (architect reviews → approves/rejects → writes next prompt)
fast and reliable in any project.

## 14. Repository Health Report Rule — [Universal]

Every prompt execution must end with an automated Repository Health
Report checking: folder structure validity, broken references, duplicate
files/folders, naming consistency, missing documentation, stale TODOs,
stale decisions, architecture drift, and security observations — plus an
overall health score with justification. See
`ai/templates/repository-health-report-template.md`.

**Why universal:** continuous, automated self-audit catches drift before
it compounds, independent of what the project actually builds.

## 15. Mandatory File Synchronization Rule — [Universal]

Any change made during a prompt execution must automatically update every
affected governance/tracking file — `ai/todo/**`, `ai/decisions/decisions.md`,
`ai/session/session-state.md`, `ai/changelog/changelog.md`,
`ai/context/context.md`, `ai/memory/project-memory.md`,
`ai/prompts/prompt-index.md`, and relevant files under `ai/reviews/` — in
the same execution, with no manual follow-up step required. Additionally,
no file changes may be made silently: each modified file must be
accompanied by a stated Reason, Impact, and (if applicable) Linked
Decision / Linked Prompt.

**Why universal:** manual synchronization is the single most common way
process documentation silently rots; making it mandatory and automatic
removes reliance on memory or discipline.

## 16. Mandatory Context Bootstrap Rule — [Universal]

Every prompt must begin execution by reading, in this order:
`ai/context/context.md`, `ai/memory/project-memory.md`,
`ai/constitution/constitution.md`, `ai/decisions/decisions.md`,
`ai/todo/` (index plus relevant module files), and any document directly
related to the prompt's subject (e.g. an existing FS/BRD/ADR being
extended). The AI must not assume business rules that are not already
documented — existing project documentation is the source of truth, and
gaps are surfaced as open questions rather than invented.

**Why universal:** stateless AI sessions drift toward inventing plausible
but wrong assumptions unless the bootstrap read is forced every time,
regardless of project.

## 17. Architecture Impact Report Rule — [Universal]

Every prompt execution must end with a third standardized report — the
Architecture Impact Report — alongside the Prompt Execution Report and
Repository Health Report. It must cover: BRD impact, SDD impact, DBD
impact, API impact, ADR impact, Design System impact, which future
prompts are affected, breaking changes, backward compatibility, and
recommended follow-up prompts. See
`ai/templates/architecture-impact-report-template.md`.

**Why universal:** as architecture documents multiply, changes in one
ripple into others; an explicit impact report is what keeps that graph of
dependencies visible instead of silently stale.

## 18. Review Package Rule — [Universal]

Every prompt execution must generate `ai/review/review-package.md`
(overwritten each prompt; history lives in `ai/history/prompt-history.md`)
listing: prompt id, files created, files modified, files deleted, files
renamed, a classification of every touched file into Category A
(Architecture — BRD/SDD/DBD/API/ADR/FS/DDS/PEP/GOV/DS/UXS/domain model/
entity catalog/business rules/decision records — always reviewed),
Category B (Engineering — constitution/prompts/roadmap/memory/context/
glossary/risk register — usually reviewed), Category C (Operational —
todo/changelog/session/history/review logs — reviewed only if materially
changed), or Category D (Generated — reports/execution logs/health
reports/audit reports — not sent unless asked), a Review Priority per
Category-A/B file (🔴 Critical / 🟠 Important / 🟡 Recommended / 🟢
Informational), open questions, known issues, architecture impact
summary, and the recommended next prompt. The AI shares only
`review-package.md` plus the files marked 🔴/🟠 by default — not the full
repository — unless the human asks for more.

**Why universal:** as a repository's document count grows, sharing
everything after every prompt becomes noise; a structured review package
keeps the human's attention on what actually needs judgment.

## 19. Document Metadata & Status Standard — [Universal]

Every architecture document (anything under `ai/architecture/**`,
including FS/SDD/DBD/BRD/API/ADR/DDS/PEP/GOV/DS/UXS) must open with a
metadata block: Document ID, Version, Status (Draft / Needs Review /
Approved / Deprecated / Superseded), Owner, Reviewer, Created, Last
Updated, Related Documents, Next Documents. See
`ai/templates/architecture-document-metadata-template.md`. Status changes
must be reflected in the document itself, not only in a review log.

**Why universal:** turns a folder of Markdown files into a navigable
knowledge graph instead of isolated documents, independent of project.

## 20. Document Approval Workflow Rule — [Universal]

Every architecture document moves through a fixed status lifecycle:
`Draft → Needs Review → Review Comments → Approved → Locked → Superseded`
(a document may also go `Approved → Deprecated` if retired without a
direct successor). No Functional Specification (or any document it
depends on) may be implemented in production code unless its Status is
`Approved` or `Locked`. `Review Comments` means the human has responded
with requested changes; the document returns to `Needs Review` once
addressed. `Locked` means implementation has begun and the document's
core content is now frozen — further changes require a new version and a
Superseded note on the old one, not an in-place edit.

**Why universal:** prevents the common failure mode where "a document
exists" is silently treated as "a document is approved," independent of
project.

## 21. Pre/Post-Execution Checklist Rule — [Universal]

Every prompt execution must open with a Pre-Execution Checklist
(constitution read, context read, memory read, decisions read, relevant
architecture documents read, prior review package reviewed, open
questions identified, conflicting decisions checked, traceability
checked) and close with a Post-Execution Checklist (files synchronized,
decisions updated, TODO updated, context updated, memory updated, prompt
history updated, review package generated, repository health generated,
architecture impact generated, open questions listed). Both checklists
are reported as part of the Prompt Execution Report, not a separate
document.

**Why universal:** makes the bootstrap/handoff discipline (Rules 9, 16)
and the reporting discipline (Rules 13-15, 17-18) auditable per-execution
rather than merely aspirational.

## 22. Functional Specification Standard Rule — [Universal]

Every Functional Specification (FS-001 onward — FS-000 is exempt, see
FSS-000's own scope note) must conform to `ai/architecture/fs/
FSS-000-functional-specification-standard.md`: the 21 mandatory
sections in order, plus the Architecture Compliance Checklist and
Cross-FS Dependencies sections, plus its Definition of Ready (before
drafting begins) and Definition of Done (before the document is
considered complete). No FS may reach `Approved` status (Rule 20)
without satisfying FSS-000's Definition of Done.

**Why universal:** any project with more than one feature module needs
one identical FS format, or every module reinvents its own structure
and cross-module review becomes ad hoc.

## 23. Fixed Quality Rubric Rule — [Universal]

Every AI-produced artifact from this point onward — Functional
Specification, backend implementation, Flutter UI, tests, deployment
configuration, or any other deliverable — must be evaluated, and that
evaluation reported, against five fixed dimensions before being
presented as complete:

1. **Architecture Compliance** — does it follow the approved baseline
   (`ai/architecture/**`) and decision records (`ai/decisions/
   decisions.md`)?
2. **Business Compliance** — are all applicable business rules
   (`BRR-001`) and workflows correctly implemented?
3. **Engineering Quality** — is the design maintainable, modular,
   scalable, and internally consistent?
4. **Repository Governance** — have all required `.md` files,
   changelog, TODOs, prompt history, and review package been updated
   correctly (Rule 15)?
5. **Implementation Readiness** — is the artifact complete enough for
   the next development stage, or are there unresolved blockers?

This rubric self-assessment is reported alongside (not instead of) the
existing Prompt Execution Report, Repository Health Report, and Review
Package (Rules 13, 14, 18).

**Why universal:** a fixed, five-dimension rubric applied consistently
is what makes "is this actually done" a checkable claim rather than a
subjective one, regardless of what kind of artifact is being reviewed.

## 24. Implementation Specification Pipeline Stage Rule — [Universal]

Between an Approved Functional Specification and the first line of
production code, an **Implementation Specification (ISP)** is required:
a per-module technical contract translating the FS into backend API
contracts (method, auth, request/response, errors, validation),
Request/Response DTOs, Repository interfaces (no implementation),
Service interfaces (signatures, responsibilities, dependencies), a
Flutter contract per screen (route, state container, API calls, states,
error handling, permissions), a field-level Validation Matrix, and a
Test Matrix mapping every Functional Requirement through its Acceptance
Criteria to suggested test cases. The pipeline is: **Architecture → FS
→ ISP → Code → Testing.** An ISP must not introduce a new API endpoint,
change a business rule, or alter architecture — it may only propose
clearly-flagged implementation-level defaults (e.g. a field's maximum
length) for genuine FS-level gaps, never silently.

**Why universal:** a stable, reviewable contract between analysis and
development lets backend and client work happen in parallel and makes
code review objective (measured against the ISP) rather than a matter
of interpreting the FS afresh each time — true for any project with
more than one implementer.

## 25. Engineering Package (EP) Pipeline Stage Rule — [Universal]

The pipeline established in Rule 24 is clarified and extended:
**Architecture → FS → ISP → EP → Code → Testing.** Between a module's
Implementation Specification (ISP — API/DTO/Repository/Service
contracts) and its production code, an **Engineering Package (EP)** is
required: the concrete folder structure, migration sequence, database
constraints/indexes/locking implementation, Flutter feature layout,
per-error-code cross-layer mapping, test package, recommended
development order, and a full file inventory. An EP builds on its
module's ISP (citing it, not re-deriving its contracts) and, like an
ISP, may not introduce a new API endpoint, change a business rule, or
alter architecture — only propose clearly-flagged implementation-level
defaults for genuine gaps. **This rule is recorded as a proposed
reconciliation** between Rule 24 (which named ISP as the sole
pre-code stage) and the prompt that introduced EP-001 (which did not
reference ISP-001 at all) — flagged for the architect to confirm rather
than silently assumed as the only possible reading.

**Why universal:** as a module's technical detail grows, separating
"what the contracts are" (ISP) from "how the codebase is physically
organized to implement them" (EP) keeps each document focused and
independently reviewable, for any project with more than a trivial
number of files per module.

## 26. CTO-Level Engineering Review Rubric — [Universal]

From EP-001 onward, every future deliverable (Engineering Package,
production code, tests, deployment configuration) is reviewed against
ten dimensions, refining Rule 23's "Engineering Quality" dimension into
CTO-level specificity now that the project has left the planning phase:
Engineering quality, Scalability, Performance implications,
Maintainability, Security, Code organization, Production readiness,
Technical debt, Developer experience, and AI-generated code quality.
Rule 23's other four dimensions (Architecture Compliance, Business
Compliance, Repository Governance, Implementation Readiness) remain in
force unchanged — this rubric layers onto, not replaces, Rule 23.

**Why universal:** once a project moves from documentation to code, a
CTO-level review lens catches concerns (scalability, technical debt,
production readiness) that a purely architectural/business rubric
doesn't surface, regardless of what's being built.

---

## Amending this Constitution

1. Propose the change as a decision in `ai/decisions/decisions.md`.
2. Get human approval (Rule 10).
3. Update this file and bump the version number at the top.
4. Log the change in `ai/changelog/changelog.md`.
