# Decisions Log — BIKEVALUATOR

Use `ai/templates/decision-template.md` for new entries. Newest entries at
the top. Never delete a decision — supersede it with a new entry that
references the old id.

---

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
