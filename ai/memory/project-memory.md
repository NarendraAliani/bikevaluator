# Project Memory — BIKEVALUATOR

Permanent project knowledge that must persist across every AI session
regardless of context window resets. This file is read every session
bootstrap (Constitution Rule 9) and updated whenever new permanent facts
are established. Unlike `context.md` (current state, changes often), this
file changes rarely — only when something becomes permanently true.

## Product identity

- **Name:** BIKEVALUATOR
- **What it is (confirmed BUS-0001):** A B2B SaaS platform for
  dealer-focused used two-wheeler valuation, centered on a centralized
  pricing/valuation engine, sold via subscription.
- **Tech stack:** Flutter (client) + Django (backend) + PostgreSQL
  (database).
- **Core IP:** The Valuation Engine (see FS-000) — not Authentication.
  Roadmap order is Vehicle Master → Valuation Engine → Authentication →
  Admin → Subscription → Payments (BUS-0002).

## Business terminology

Canonical definitions live in `ai/glossary/business-glossary.md`, sourced
from `ai/architecture/fs/FS-000-core-domain-valuation.md`. Foundational
terms every session should already know: Dealer, Vehicle, Brand, Model,
Variant, Year, MSP, Margin, Purchase Price, Scrap Value, Repair Cost,
Recommendation.

## Naming conventions

- Decision IDs are categorized by domain prefix (see
  `ai/decisions/decisions.md` migration note): `BUS`, `ARC`, `DB`, `API`,
  `SEC`, `OPS`, `AI`. Legacy flat IDs `DEC-0001`..`DEC-0003` remain valid
  and are not renamed (see migration strategy).
- Prompt IDs use the `AEP-<NNNN>` sequence, organized by category folder
  under `ai/prompts/<category>/`.
- Architecture Decision Records use `ADR-<NNNN>-<kebab-title>.md` and
  cross-reference an `ARC-xxxx` decision entry.
- Functional specs use `FS-<NNN>-<kebab-title>.md` under
  `ai/architecture/fs/`.

## Permanent architectural assumptions

- Production code root is `src/` (placeholder, per DEC-0003 / ARC-0001).
  Confirm final layout (e.g. Django project layout vs. `src/`) when
  FS-001 Vehicle Master implementation begins.
- The `ai/` directory is process-only and must never be part of a
  deployable build artifact (Constitution Rule 1).
- No business logic, UI, or backend API exists yet as of this entry —
  FS-000 is a specification only, not implementation.
- Open valuation business-rule questions (Margin configurability, Scrap
  Value derivation, recommendation thresholds — see FS-000 §4.2, §5 and
  RISK-0003) must be resolved via a BUS decision before FS-001 (Vehicle
  Master) finalizes its schema — do not assume answers.
- All module FS documents (FS-001 onward) must conform to
  `ai/architecture/sdd/SDD-000-domain-architecture.md` (domain model,
  entity catalogue, state machines, module boundaries, event flow,
  business constraints, NFRs, error catalogue) rather than redefining
  structure inline — per ARC-0002.
- The 6 centralized business constraints in SDD-000 §6 (e.g. Purchase
  Price never below Scrap Value, MSP/Margin/Scrap Value Admin-only,
  Evaluation immutability of Calculation Results) are binding across all
  modules — per BUS-0003.
- Document Review Protocol (DRP-001, AI-0002) is active: every prompt
  produces `ai/review/review-package.md`; by default only that file plus
  🔴/🟠-priority files are shared with the human — never the full
  repository unless asked. Every architecture document must carry the
  Document ID/Status/Owner/Reviewer metadata block.
- Document Approval Workflow (AI-0003): status lifecycle is `Draft →
  Needs Review → Review Comments → Approved → Locked → Superseded` (or
  `Approved → Deprecated`). No FS may be implemented until it and its
  dependencies are `Approved`/`Locked`.
- All business rules live in `ai/architecture/business-rules/BRR-001-business-rule-registry.md`
  under `BR-000x` IDs — FS/SDD documents reference them, never restate
  them (ARC-0003).
- Data Dictionaries (`ai/architecture/data-dictionary/DD-<Entity>.md`)
  and API standards (`ai/architecture/api/API-000-standards.md`) are the
  source of truth for field definitions and API conventions,
  respectively — reference, don't redefine.
- Naming (NS-001), code style (CSS-001), documentation (DOC-001),
  testing (TEST-001), logging (LOG-001), and security (SEC-001)
  standards live under `ai/architecture/standards/` — reference these,
  don't redefine per-module. Operational (non-constitutional) standards
  live in `ai/governance/` (git workflow, branching, release policy,
  engineering principles) — the Constitution itself is considered
  largely stable per AR-001 and should rarely gain new rules.
- Future plan (not yet executed, AI-0004): split the repository into a
  universal AIEF (AI Engineering Framework) layer and a BIKEVALUATOR
  project layer, so future products can reuse the framework. This is
  deliberately deferred to its own prompt — do not assume it has
  happened.
- Per BUS-0004: canonical business/schema/API documents are `BRD-001`,
  `DBD-001`, `API-001` (adopted from an architect-supplied external
  documentation set) — these supersede FS-000/SDD-000/API-000 wherever
  they conflict. Key confirmed facts: only two roles exist (Dealer,
  Super Admin — no separate "Admin"); Margin is global per Year+Variant,
  not per-dealer; Scrap Value is independently maintained; repair costs
  are fixed ₹ amounts (BR-0010), never percentages; final price rounds
  to nearest ₹10 (BR-0009); status/lifecycle uses an `active` boolean +
  soft-delete fields, not an enum; pricing history uses
  `effective_from`/`effective_to` temporal columns, not a separate
  history table; offline capability and multi-currency are NOT
  supported in v1. Still genuinely open: exact recommendation
  thresholds (BR-0003), Vehicle Selector search threshold, Year-based
  Brand/Model filtering, E-AUTHZ-001 formalization.

## Things AI must never forget

- Humans approve; AI drafts and proposes (Constitution Rule 10).
- Every prompt execution must end with a Prompt Execution Report and
  Repository Health Report (see Constitution Rules 13–14, added under
  AEP-002).
- Historical decisions (`DEC-0001..0003`) are never deleted or rewritten,
  only superseded or migrated forward with a documented mapping.
