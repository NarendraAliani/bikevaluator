# BIKEVALUATOR — AI Engineering Constitution

Version: 1.0.0
Established: 2026-08-02
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

---

## Amending this Constitution

1. Propose the change as a decision in `ai/decisions/decisions.md`.
2. Get human approval (Rule 10).
3. Update this file and bump the version number at the top.
4. Log the change in `ai/changelog/changelog.md`.
