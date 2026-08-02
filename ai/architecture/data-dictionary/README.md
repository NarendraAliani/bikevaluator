# Data Dictionaries — BIKEVALUATOR

One document per entity, named `DD-<EntityName>.md`, using the field
table format below. Purpose: prevent different developers/agents from
interpreting the same field differently. Every entity in SDD-000's Entity
Catalogue (§2) gets one of these before its owning module's FS is
implemented.

Template revised per AR-001 (Architecture Review AR-001) — enriched from
the original 6-column format to the enterprise-grade set below.

## Field Table Format

| Business Name | Technical Name | Type | Owner Module | Lifecycle | Validation Rules | Default Value | Allowed Values | Editable By | Visible To | Audit Required | PII | Encrypted | Indexed | Unique | Nullable | Future Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

- **Business Name / Technical Name:** the human-facing term (per
  `ai/glossary/business-glossary.md`) vs. the exact field name used in
  code/schema — naming itself follows `NS-001-naming-standards.md`.
- **Owner Module:** from SDD-000 §4 Module Boundaries.
- **Lifecycle:** which entity state machine (SDD-000 §3) this field is
  tied to, if any.
- **Validation Rules / Default Value / Allowed Values:** kept factual and
  short — link to the relevant BR/FS section rather than re-deriving
  business logic here.
- **Editable By / Visible To:** role or module name (Admin, Dealer,
  System-computed, etc.).
- **Audit Required:** whether writes to this field must be logged (see
  SDD-000 §7 NFR — Audit logging).
- **PII / Encrypted:** flag any personally identifiable or sensitive
  field — feeds the future SEC-001 Security Standards document.
- **Indexed / Unique / Nullable:** schema-level constraints, to be
  confirmed against the DBD document once written.
- **Future Notes:** anything deferred (e.g. multi-currency, offline sync)
  — link to the relevant open question if one exists.

See `DD-Vehicle.md` for a worked example, covering the first entity from
SDD-000's Entity Catalogue.
