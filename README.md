# BIKEVALUATOR

## Project Overview

BIKEVALUATOR is a **B2B SaaS platform for dealer-focused used two-wheeler
valuation**, built around a centralized pricing/valuation engine and sold
via subscription. Stack: Flutter (client) + Django (backend) + PostgreSQL
(database). The repository is currently in **Phase 1 — Core Domain
Build-out**: the engineering framework (Phase 0) is complete, and the
foundational business specification (FS-000) is authored and pending
approval. No business-logic code, UI, or backend API exists yet — see
`ai/context/context.md`.

## Repository Structure

```text
/
├── ai/                     AI engineering framework (process only — see below)
├── docs/                   User/developer-facing documentation
├── src/                    Production code root (placeholder)
├── .gitignore
└── README.md               This file
```

## AI Framework Overview

The `ai/` directory is the permanent process layer for this repository —
never deployed as part of the application. Key entry points:

| Path | Purpose |
|---|---|
| `ai/constitution/constitution.md` | Governing rules for AI-assisted development (read this first) |
| `ai/context/context.md` | **First file every AI session reads** — current phase/task/blockers |
| `ai/memory/project-memory.md` | Permanent project knowledge that must never be forgotten |
| `ai/decisions/decisions.md` | Log of all product/architecture/process decisions |
| `ai/todo/` | Task tracking, split by module under `ai/todo/modules/` |
| `ai/changelog/changelog.md` | History of framework/repository changes |
| `ai/session/session-state.md` | Snapshot of current session state |
| `ai/prompts/` | Versioned prompts, organized by category |
| `ai/reviews/` | Review logs, organized by category |
| `ai/architecture/` | BRD, SDD, DBD, API, ADR, UXS, DS, DDS, PEP, GOV, FS documents |
| `ai/agents/` | Role profiles (architect, backend, flutter, database, reviewer, tester, security, documenter) |
| `ai/risks/risk-register.md` | Tracked risks |
| `ai/glossary/business-glossary.md` | Domain terminology |
| `ai/roadmap/roadmap.md` | Phase-level roadmap |
| `ai/templates/` | Templates for prompts, decisions, TODOs, and mandatory reports |

Full rules: see `ai/constitution/constitution.md`. Full onboarding: see
`ai/README.md`.

## Architecture Documents

None yet — `ai/architecture/**` folders are placeholders pending the first
approved functional specification.

## Development Workflow

This repository uses a closed-loop engineering process:

```text
Architect writes a prompt (ai/prompts/<category>/AEP-NNNN-*.md)
        → AI implements + updates repository
        → AI produces a Prompt Execution Report + Repository Health Report
        → Architect reviews, summarizes, finds gaps, approves/rejects
        → Architect updates architecture decisions
        → Architect writes the next prompt
```

Every prompt execution must synchronize all governance files (todo,
decisions, session-state, changelog, context, project-memory,
prompt-index, review logs) — see Constitution Rules 13–15.

## Current Project Phase

**Phase 1 — Core Domain Build-out.** Phase 0 (AEP-001, AEP-002) is
complete and approved. FS-000 (business spec) and SDD-000 (domain
architecture — domain model, entity catalogue, state machines, module
boundaries, constraints, NFRs, error catalogue) are authored and pending
approval, along with the permanent requirements traceability matrix.
Module build order: Vehicle Master → Valuation Engine → Authentication →
Admin → Subscription → Payments (see `ai/roadmap/roadmap.md`), each
conforming to SDD-000. Blocked on: resolving three open valuation
business-rule questions (see `ai/context/context.md` and
`ai/risks/risk-register.md`, RISK-0003).

## Contribution Guide

1. Read `ai/context/context.md`, then `ai/constitution/constitution.md`.
2. Check `ai/todo/todo.md` and the relevant `ai/todo/modules/*.md` for
   open tasks.
3. Any non-trivial change is proposed via a versioned prompt under
   `ai/prompts/<category>/`, not made ad hoc.
4. Log any consequential decision in `ai/decisions/decisions.md` using the
   appropriate category prefix.
5. Humans approve; AI drafts and proposes (Constitution Rule 10).

## Quick Links

- [AI Framework Overview](ai/README.md)
- [Constitution](ai/constitution/constitution.md)
- [Current Context](ai/context/context.md)
- [Decisions Log](ai/decisions/decisions.md)
- [Roadmap](ai/roadmap/roadmap.md)
- [Risk Register](ai/risks/risk-register.md)
- [Prompt History](ai/history/prompt-history.md)
- [FS-000 — Core Domain & Valuation Spec](ai/architecture/fs/FS-000-core-domain-valuation.md)
- [SDD-000 — Domain Architecture & Entity Model](ai/architecture/sdd/SDD-000-domain-architecture.md)
- [Requirements Traceability Matrix](ai/architecture/traceability/requirements-traceability-matrix.md)
- [Latest Review Package](ai/review/review-package.md)
- [Business Rule Registry (BRR-001)](ai/architecture/business-rules/BRR-001-business-rule-registry.md)
- [Decision Traceability Matrix](ai/architecture/traceability/decision-traceability-matrix.md)
- [API Standards (API-000)](ai/architecture/api/API-000-standards.md)
- [Naming Standards (NS-001)](ai/architecture/standards/NS-001-naming-standards.md)
- [Governance (operational standards)](ai/governance/README.md)
- [Business Requirements (BRD-001)](ai/architecture/brd/BRD-001-business-requirements.md)
- [Database Design (DBD-001)](ai/architecture/dbd/DBD-001-database-design.md)
- [API Endpoints (API-001)](ai/architecture/api/API-001-endpoints.md)
- [Canonical Domain Model (DDD-001)](ai/architecture/domain/DDD-001-domain-model.md)
- [Canonical System Sequence Diagrams (SSD-001)](ai/architecture/sequence/SSD-001-system-sequence-diagrams.md)
- [Architecture Freeze & Readiness Review (AFR-001)](ai/architecture/AFR-001-architecture-freeze-review.md)
- [Architecture Baseline v1.0 (ABL-001)](ai/architecture/ABL-001-architecture-baseline.md)
- [Functional Specification Standard (FSS-000)](ai/architecture/fs/FSS-000-functional-specification-standard.md)
- [FS Template](ai/templates/fs-template.md)
