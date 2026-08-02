# DD-Vehicle — Data Dictionary: Vehicle

| Field | Value |
|---|---|
| Document ID | DD-Vehicle |
| Version | 2.0 |
| Status | Needs Review |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | SDD-000 (Entity Catalogue §2), FS-000, BRR-001, NS-001 |
| Next Documents | DD-Evaluation, DD-VehicleMasterRecord (pending FS-001) |

Regenerated against the enriched template in `README.md` v1.1 per AR-001.
Covers the `Vehicle` entity from SDD-000 §2.

| Business Name | Technical Name | Type | Owner Module | Lifecycle | Validation Rules | Default Value | Allowed Values | Editable By | Visible To | Audit Required | PII | Encrypted | Indexed | Unique | Nullable | Future Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Vehicle ID | id | identifier (UUID) | Valuation Engine | n/a (immutable) | System-generated, never user-supplied | — | — | System-generated | Dealer, Admin | No | No | No | Yes (PK) | Yes | No | — |
| Vehicle Master Record Reference | vehicle_master_record_id | reference (FK) | Valuation Engine | n/a | Must reference an Active Vehicle Master Record (BR-0005) | — | — | System-set at creation | Dealer, Admin | Yes | No | No | Yes | No | No | — |
| Evaluation Reference | evaluation_id | reference (FK) | Valuation Engine | Tied to Evaluation state machine (SDD-000 §3) | Exactly one Evaluation per Vehicle | — | — | System-set at creation | Dealer, Admin | No | No | No | Yes | No | No | — |
| Created At | created_at | timestamp (UTC) | Valuation Engine | n/a (immutable) | Set once at creation, never updated | now() | — | System-set | Dealer, Admin | No | No | No | Yes | No | No | Time zone display conversion is a Flutter-client concern (SDD-000 §7) |

Not independently mutable after creation — per SDD-000 §2, a Vehicle is
"tied 1:1 to its Evaluation." Corrections happen by re-opening the
Evaluation (BR-0007), not by editing the Vehicle record.

**Naming note:** field names above are placeholders pending confirmation
against `NS-001-naming-standards.md` (e.g. `snake_case` for Postgres
columns, as shown) — do not treat as final until NS-001 is approved.
