# Decision Traceability Matrix

| Field | Value |
|---|---|
| Document ID | DTM-001 |
| Version | 1.0 |
| Status | Needs Review |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | requirements-traceability-matrix.md, BRR-001, decisions.md |
| Next Documents | Updated per future decision |

Answers: "if I change decision X, what breaks?" Traces each decision
forward to the documents, entities/modules, and rules it produced.
Additive-only — never delete a row; if a decision is superseded, add a
new row and mark the old one Superseded, linking forward.

| Decision | Produced/Affects | Downstream Documents | Downstream Rules | Downstream Modules | Status |
|---|---|---|---|---|---|
| DEC-0001 (AI framework adoption) | `ai/` framework structure | All `ai/**` documents | — | — | Active |
| DEC-0002 (Universal/Project-specific tagging) | Constitution tagging convention | `ai/constitution/constitution.md` | — | — | Active |
| DEC-0003 / ARC-0001 (production root placeholder) | `src/` placeholder | root `README.md` | — | All future code modules | Active — reconfirm at FS-001 implementation |
| ARC-0001 (category decision IDs) | Decision-ID scheme | `ai/decisions/decisions.md` | — | — | Active |
| AI-0001 (mandatory reporting rules) | Prompt Execution Report, Repository Health Report | Constitution Rules 13-15 | — | — | Active |
| BUS-0001 (domain/stack confirmed) | Product identity, tech stack | FS-000, `ai/memory/project-memory.md`, `ai/glossary/business-glossary.md` | BR-0001 through BR-0008 (all depend on the confirmed domain) | Vehicle Master, Valuation Engine, Authentication, Admin, Subscription, Payments | Active |
| BUS-0002 (roadmap reorder) | Module build order | `ai/roadmap/roadmap.md` | — | Vehicle Master (moved first), Authentication (moved later) | Active |
| ARC-0002 (domain-architecture gate) | SDD-000 required before module FS | SDD-000, requirements-traceability-matrix.md | — | All Phase 1 modules | Active |
| BUS-0003 (6 centralized business constraints) | Binding constraints | SDD-000 §6 | BR-0002, BR-0004, BR-0005, BR-0006, BR-0007, BR-0008 | Vehicle Master, Valuation Engine, Subscription | Active — if changed, all 6 linked rules must be re-verified |
| AI-0002 (Document Review Protocol) | review-package.md generation | Constitution Rules 18-19 | — | — | Active |

## How to use this when changing a decision

1. Find the decision's row.
2. Everything in "Downstream Rules," "Downstream Modules," and
   "Downstream Documents" must be re-reviewed before the change is
   approved.
3. Log the change as a new decision that supersedes the old one (never
   edit history in place — see Constitution's decision-logging rule).
4. Update this matrix with a new row, marking the old row "Superseded →
   see <new decision id>."
