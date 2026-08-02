# BDR-001 — Business Decision Records

| Field | Value |
|---|---|
| Document ID | BDR-001 |
| Version | 2.0 |
| Status | Partially Resolved |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | IPS-001, SDD-000, FS-000, BRR-001, BUS-0004, BRD-001, DBD-001, requirements-traceability-matrix.md, decision-traceability-matrix.md |
| Next Documents | BRD-001, DBD-001, API-001 (canonical documents created from the resolving source material) |

Every open question carried forward from IPS-001 §17 (plus the
long-standing FS-000/SDD-000 questions) was converted into a formal
Business Decision Record. **Update (v2.0):** the architect supplied a
complete external documentation set (BRD-001/DBD-001/API-001/ADR-001..18/
UXS-001/DS-001/DDS-001/PEP-001/GOV-001) that directly answers 10 of the
14 BDRs below. See `ai/decisions/decisions.md` BUS-0004 for the
authoritative per-question resolution table and the two new business
rules it surfaced (BR-0009 rounding, BR-0010 fixed repair costs). The
individual "Decision: Pending Human Decision" lines in each BDR section
below are **not** individually edited (preserving this document's
original as-drafted content per the additive-history principle) —
BUS-0004 is the resolution record of authority. Still genuinely open:
BDR-0004 (exact thresholds), BDR-0007 (search threshold), BDR-0008
(Year-based Brand/Model filtering), BDR-0012 (E-AUTHZ-001
formalization).

---

## BDR-0001 — Repair Component Cost Table Ownership

| Field | Value |
|---|---|
| Category | Data Ownership / Architecture |
| Priority | Critical |
| Blocking? | Yes — blocks Vehicle Master DB-001 and Valuation Engine IPS-002 |
| Implementation Impact | High |
| Related BR IDs | BR-0004, BR-0005 (indirectly — depends on where the pricing-editable data lives) |
| Related Decisions | SDD-000 §4 (Module Boundaries), IPS-001 §2, §17.1 |

**Question:** Does Vehicle Master or the Valuation Engine own repair
component cost tables?

**Background:** SDD-000 §4's Module Boundaries table explicitly assigns
"Repair component cost tables" to Vehicle Master. IPS-001 §2, when asked
to restate Vehicle Master's ownership list, did not include repair cost
tables and implied by omission that the Valuation Engine (which owns
Repair Component Assessments) should own the cost data behind them.
This is a direct, unresolved conflict between two architecture
documents.

**Affected Documents:** SDD-000 §4, §6 (DB Mapping); IPS-001 §2, §5, §6.

**Affected Modules:** Vehicle Master, Valuation Engine.

**Possible Options:**

- **Option A:** Vehicle Master owns repair cost tables (per SDD-000 as
  written). Valuation Engine reads them, same pattern as MSP/Margin.
  - *Pros:* Consistent with SDD-000; keeps all "centrally priced by
    Admin" data in one module; Valuation Engine stays purely
    computational.
  - *Cons:* Vehicle Master's scope grows to include component-level
    cost data that's conceptually closer to "how repairs are priced,"
    not "what the vehicle catalog is."
- **Option B:** Valuation Engine owns repair cost tables (per IPS-001's
  implicit framing). Vehicle Master owns only Brand/Model/Variant/Year/
  MSP/Margin/Scrap Value.
  - *Pros:* Keeps repair-specific data next to the Repair Component
    Assessment entity that consumes it; Vehicle Master stays a pure
    "what is this vehicle worth" catalog.
  - *Cons:* Contradicts SDD-000 as currently written — requires
    amending SDD-000 §4 and §6, not just IPS-001.
- **Option C:** Split ownership — Vehicle Master owns the cost *values*
  (Admin-editable, like MSP/Margin), Valuation Engine owns the
  *component definitions* (Engine/Color/Tyres/etc. as a fixed list) and
  reads costs from Vehicle Master.
  - *Pros:* Mirrors how MSP/Margin already work (Admin-owned value,
    Valuation Engine-consumed); avoids growing either module's write
    surface unnecessarily.
  - *Cons:* Adds a third table split; more coordination overhead across
    two modules for what is otherwise a single feature.

**Recommendation (Architecture Recommendation, NOT Approved Decision):**
Option C — it's the most consistent with the existing MSP/Margin
pattern and avoids rewriting SDD-000's higher-level module philosophy
while still resolving the conflict cleanly.

**Decision:** Pending Human Decision

**Decision Rationale:** —

**Architecture Impact:** Whichever option is chosen requires either
confirming SDD-000 §4/§6 as-is (Option A) or amending them (Options B/C)
— this is the one BDR here with direct, mandatory SDD-000 edits attached.

**Implementation Impact:** High — determines which Django app and which
database tables hold repair cost data; must be resolved before Vehicle
Master's migrations (DB-001) are written.

**Future Impact:** Sets the precedent for how "shared" pricing-adjacent
data is split across modules going forward (e.g. future regional pricing,
BDR-0002).

---

## BDR-0002 — Margin Scope (Per-Dealer/Region vs. Global)

| Field | Value |
|---|---|
| Category | Pricing |
| Priority | Critical |
| Blocking? | Yes — blocks Vehicle Master DB-001 (schema shape for Margin) |
| Implementation Impact | High |
| Related BR IDs | BR-0001, BR-0004 |
| Related Decisions | FS-000 §4.2 |

**Question:** Is Margin per-dealer/region-configurable, or global (one
value per Vehicle Master Record)?

**Background:** FS-000 §4.2 raised this as an open question from the
very first business specification; it has remained unresolved through
SDD-000, BRR-001, and IPS-001.

**Affected Documents:** FS-000 §4.1/§4.2, BRR-001 BR-0001/BR-0004,
IPS-001 §5 (schema).

**Affected Modules:** Vehicle Master (schema), Valuation Engine (BR-0001
calculation input).

**Possible Options:**

- **Option A — Global:** one Margin value per Vehicle Master Record,
  editable only by Admin.
  - *Pros:* Simple schema (single column); matches the simplest reading
    of FS-000 §4.1's formula.
  - *Cons:* No flexibility if dealer-specific or regional pricing
    strategy is ever needed — would require a schema migration later.
- **Option B — Per-dealer override:** a base global Margin plus an
  optional per-dealer override table.
  - *Pros:* Future-proofs for dealer-tier pricing without redesigning
    the base schema.
  - *Cons:* More complex from day one; adds a table and a resolution
    order (dealer override → global fallback) that must be specified
    precisely to avoid ambiguity in BR-0001's calculation.
- **Option C — Per-region:** Margin varies by a region dimension, not
  per-dealer specifically.
  - *Pros:* Matches common used-vehicle market pricing practice
    (regional resale variance).
  - *Cons:* Introduces a "region" concept not defined anywhere yet
    (Dealer's own region? A fixed region list?) — this option creates
    its own new open question rather than resolving one.

**Recommendation (Architecture Recommendation, NOT Approved Decision):**
Option A for the initial Vehicle Master implementation, with Option B
explicitly reserved in the schema as a documented Future Enhancement
(IPS-001 §16) rather than built now — avoids both premature complexity
and a later breaking migration, provided the table design leaves room
for it (e.g. Margin stored on Vehicle Master Record, not hardcoded into
application logic).

**Decision:** Pending Human Decision

**Decision Rationale:** —

**Architecture Impact:** Confirms or narrows FS-000 §4.1's formula
(BR-0001) to a single, unambiguous Margin source.

**Implementation Impact:** High — directly shapes the
`vehicle_master_record` table schema in IPS-001 §5.

**Future Impact:** If Option A is chosen now and per-dealer/regional
Margin is wanted later, this becomes its own migration decision, not a
day-one concern.

---

## BDR-0003 — Scrap Value Derivation

| Field | Value |
|---|---|
| Category | Pricing |
| Priority | Critical |
| Blocking? | Yes — blocks Vehicle Master DB-001 |
| Implementation Impact | Medium |
| Related BR IDs | BR-0001, BR-0002 |
| Related Decisions | FS-000 §4.2 |

**Question:** Is Scrap Value independently maintained (its own
Admin-entered field) or derived from MSP (e.g. a fixed percentage)?

**Background:** FS-000 §4.2 raised this alongside the Margin question;
still unresolved.

**Affected Documents:** FS-000 §4.1/§4.2, BRR-001 BR-0001/BR-0002,
IPS-001 §5 (schema), §8 (validation).

**Affected Modules:** Vehicle Master (schema/validation), Valuation
Engine (BR-0002 floor check).

**Possible Options:**

- **Option A — Independently maintained:** Admin enters Scrap Value
  directly per Vehicle Master Record, same as MSP/Margin.
  - *Pros:* Matches the current schema in IPS-001 §5 exactly; no
    derivation logic to get wrong.
  - *Cons:* Requires Admin to keep Scrap Value manually in sync with
    market reality as MSP changes.
- **Option B — Derived as a percentage of MSP:** e.g. Scrap Value =
  MSP × fixed_percentage (percentage itself Admin-configurable, globally
  or per-Variant).
  - *Pros:* Reduces Admin data-entry burden; Scrap Value automatically
    tracks MSP changes.
  - *Cons:* Introduces a new configurable percentage value (global or
    per-Variant?) that itself would need a BDR if chosen; less
    transparent to reason about for a given vehicle.

**Recommendation (Architecture Recommendation, NOT Approved Decision):**
Option A — keeps IPS-001's existing schema and validation plan (§5, §8)
unchanged and matches how MSP/Margin already work; simplest to implement
and audit.

**Decision:** Pending Human Decision

**Decision Rationale:** —

**Architecture Impact:** Confirms BR-0001/BR-0002 read Scrap Value as a
stored field, not a computed one — affects whether the Valuation Engine
ever needs to know the derivation formula.

**Implementation Impact:** Medium — mainly a validation-rule question
(IPS-001 §8) rather than a structural schema change either way.

**Future Impact:** If Option B is chosen later, this becomes a new BDR
against the then-current schema, not a blocker today.

---

## BDR-0004 — Recommendation Thresholds

| Field | Value |
|---|---|
| Category | Pricing / Reporting |
| Priority | Critical |
| Blocking? | Partially — does not block Vehicle Master DB-001, but blocks Valuation Engine implementation and any Report screen |
| Implementation Impact | Low (a config value, not a schema change) |
| Related BR IDs | BR-0003, BR-0008 |
| Related Decisions | FS-000 §5 |

**Question:** Are the provisional recommendation thresholds (≥90%
Excellent, 75-89% Good, 60-74% Average, <60% Scrap) final, or should they
change?

**Background:** FS-000 §5 explicitly marked these as provisional pending
architect confirmation.

**Affected Documents:** FS-000 §5, BRR-001 BR-0003/BR-0008.

**Affected Modules:** Valuation Engine, Reports, Flutter client (display
only, per BR-0008 — no module may hardcode its own copy).

**Possible Options:**

- **Option A — Confirm as-is:** 90/75/60% thresholds become final.
  - *Pros:* No further work — already fully specified and reasoned
    about in FS-000.
  - *Cons:* Thresholds were originally described as "you can decide
    later" — confirming without domain data behind them may need
    revisiting once real valuations are run.
- **Option B — Adjust thresholds:** architect supplies new percentages.
  - *Pros:* Reflects actual business judgment once articulated.
  - *Cons:* None beyond needing the specific numbers.
- **Option C — Defer to a configurable value:** store thresholds as
  Admin-editable configuration rather than hardcoded constants.
  - *Pros:* Allows tuning without a new decision/migration each time.
  - *Cons:* Adds configuration surface and a "who can edit this and
    where" question not otherwise needed yet.

**Recommendation (Architecture Recommendation, NOT Approved Decision):**
Option A to unblock Valuation Engine planning now, with Option C flagged
as a Future Enhancement — avoids inventing a new configuration subsystem
for a value that hasn't even been used in anger yet.

**Decision:** Pending Human Decision

**Decision Rationale:** —

**Architecture Impact:** Removes the "provisional" flag from BR-0003 in
BRR-001 (once a BUS decision confirms), but does not require a BRR-001
document edit as part of *this* BDR — that follow-up decision is
separate.

**Implementation Impact:** Low — a constant value in the Valuation
Engine's calculation logic.

**Future Impact:** If thresholds prove wrong after real usage, revisit as
its own future decision — cheap to change if Option A/B, more involved
if Option C's configurability is built.

---

## BDR-0005 — Brand/Model/Variant Entity Decomposition

| Field | Value |
|---|---|
| Category | Vehicle Identity |
| Priority | High |
| Blocking? | Yes — blocks Vehicle Master DB-001 |
| Implementation Impact | High |
| Related BR IDs | BR-0005 |
| Related Decisions | SDD-000 §2 (Entity Catalogue), IPS-001 §4 |

**Question:** Is decomposing "Vehicle Master Record" into separate
Brand, Model, and Variant entities (as IPS-001 §4 proposes) the correct
model, or should SDD-000 be amended to make this explicit at the domain
level first?

**Background:** FS-000/SDD-000 treat Brand/Model/Variant/Year as
terminology and a compound catalog key, not as individually normalized
entities. IPS-001 §4 inferred a normalized Brand→Model→Variant hierarchy
to support the database design in §5 — a reasonable but unconfirmed
extrapolation.

**Affected Documents:** SDD-000 §2, IPS-001 §3, §4, §5, §6.

**Affected Modules:** Vehicle Master (schema, entirely).

**Possible Options:**

- **Option A — Normalize (as IPS-001 proposes):** separate `brand`,
  `model`, `variant` tables, each referencing its parent.
  - *Pros:* Avoids data duplication (e.g. "Honda" typed once, not once
    per Variant row); supports future per-Brand/per-Model features
    (e.g. Brand-level filtering) cleanly.
  - *Cons:* More joins for every catalog lookup; more migration
    complexity for a v1.
- **Option B — Denormalize:** a single `vehicle_master_record` table
  with `brand`, `model`, `variant`, `year` as plain columns (possibly
  with a lookup/autocomplete table for known values, not a strict FK
  hierarchy).
  - *Pros:* Simpler schema and queries for a first version; matches
    FS-000/SDD-000's literal treatment of these as terminology, not
    entities.
  - *Cons:* Harder to enforce consistent Brand/Model naming without FK
    constraints; potential data-quality drift (e.g. "Honda" vs "honda").

**Recommendation (Architecture Recommendation, NOT Approved Decision):**
Option A — the normalized structure IPS-001 already sketched avoids data
duplication and is the more conventional approach for a catalog with
this shape; the extra joins are not a meaningful cost at this scale.

**Decision:** Pending Human Decision

**Decision Rationale:** —

**Architecture Impact:** If Option A, SDD-000 §2 should be updated to
name these as explicit entities (not just terminology) for consistency;
if Option B, IPS-001 §3-§6 need revision instead.

**Implementation Impact:** High — this is the single biggest schema
shape decision in IPS-001.

**Future Impact:** Affects every future Vehicle Master feature (bulk
import, per-Brand filtering, etc. — IPS-001 §16).

---

## BDR-0006 — Postgres Enum Implementation for `status`

| Field | Value |
|---|---|
| Category | Database |
| Priority | Medium |
| Blocking? | Yes (minor) — blocks finalizing DB-001's migration syntax, not the schema shape itself |
| Implementation Impact | Low |
| Related BR IDs | BR-0005 |
| Related Decisions | IPS-001 §5, §17.3 |

**Question:** Should `vehicle_master_record.status` be a native
PostgreSQL enum type, a `varchar` with a check constraint, or an
integer with an application-level enum mapping?

**Background:** NS-001 defines naming (`UPPER_SNAKE_CASE` for DB enum
values conceptually) but not the storage mechanism.

**Affected Documents:** IPS-001 §5.

**Affected Modules:** Vehicle Master (and any future module reusing the
same status pattern, e.g. Dealer, Subscription).

**Possible Options:**

- **Option A — Native Postgres enum type.**
  - *Pros:* Database-enforced valid values; self-documenting in schema.
  - *Cons:* Adding a new status value later requires an `ALTER TYPE`
    migration, slightly more ceremony than a check constraint.
- **Option B — `varchar` + check constraint.**
  - *Pros:* Easier to extend (just update the constraint); still
    DB-enforced.
  - *Cons:* Slightly more storage than a native enum; less
    self-documenting at a glance.
- **Option C — Integer + application-level enum.**
  - *Pros:* Smallest storage footprint.
  - *Cons:* Meaning not visible in raw SQL without the application's
    enum mapping — worst for auditability/debugging.

**Recommendation (Architecture Recommendation, NOT Approved Decision):**
Option B — nearly as safe as a native enum, easier to extend as the
lifecycle evolves (e.g. if an "Archived" state is added per BDR-0011).

**Decision:** Pending Human Decision

**Decision Rationale:** —

**Architecture Impact:** None beyond IPS-001 §5's migration detail.

**Implementation Impact:** Low — purely a schema-definition choice.

**Future Impact:** Sets the pattern for every other entity with a status
lifecycle (Dealer, Subscription, Evaluation).

---

## BDR-0007 — Vehicle Selector Search Threshold

| Field | Value |
|---|---|
| Category | UX |
| Priority | Low |
| Blocking? | No |
| Implementation Impact | Low |
| Related BR IDs | — |
| Related Decisions | IPS-001 §7, §17.4 |

**Question:** At what catalog size does the Vehicle Selector need
type-ahead search instead of plain dropdowns?

**Background:** IPS-001 §7 flagged this as undefined; not addressed in
any prior document.

**Affected Documents:** IPS-001 §7 (UI Planning).

**Affected Modules:** Vehicle Master (Flutter UI only).

**Possible Options:**

- **Option A:** Always use type-ahead search, regardless of catalog
  size.
  - *Pros:* Consistent UX; no threshold logic to maintain.
  - *Cons:* Slightly more UI complexity than a plain dropdown for what
    may be small lists (e.g. Brands).
- **Option B:** Plain dropdown below a fixed item count (e.g. 20),
  type-ahead above it.
  - *Pros:* Simpler UI for small lists, better UX for large ones.
  - *Cons:* Requires picking and maintaining a threshold number.

**Recommendation (Architecture Recommendation, NOT Approved Decision):**
Option A for simplicity and UX consistency — avoids a threshold that
would otherwise need periodic revisiting as the catalog grows.

**Decision:** Pending Human Decision

**Decision Rationale:** —

**Architecture Impact:** None.

**Implementation Impact:** Low — Flutter widget choice only.

**Future Impact:** None significant.

---

## BDR-0008 — Brand/Model Availability Varying by Year

| Field | Value |
|---|---|
| Category | Vehicle Identity / UX |
| Priority | Medium |
| Blocking? | Yes — affects whether the cascading dropdown order (Year→Brand→Model→Variant, per FS-000 §2) needs a Year-filtered Brand/Model query |
| Implementation Impact | Medium |
| Related BR IDs | — |
| Related Decisions | FS-000 §2, IPS-001 §7, §17.5 |

**Question:** Can Brand/Model availability vary by Year (e.g. a Brand
that only entered the market in a later year), requiring the cascading
dropdown to filter Brand/Model by the selected Year?

**Background:** FS-000 §2's flow selects Year first, then Brand, which
implies Year might filter what Brands are shown — but this was never
confirmed as a real requirement vs. simply the order terminology was
listed in.

**Affected Documents:** FS-000 §2, IPS-001 §6, §7.

**Affected Modules:** Vehicle Master (API filtering logic, UI dropdown
chain).

**Possible Options:**

- **Option A — No Year-based filtering:** Brand/Model lists are always
  complete regardless of selected Year; only the final Vehicle Master
  Record lookup (Variant + Year) can fail to find pricing.
  - *Pros:* Simpler API (`GET /brands` needs no Year parameter);
    matches IPS-001 §6's current endpoint list as written.
  - *Cons:* A Dealer could select a Brand/Model/Variant combination that
    never existed for the chosen Year, only discovering the mismatch at
    the final pricing-lookup step (E-PRICING-001).
- **Option B — Year-based filtering throughout:** each dropdown level
  filters by the previously selected Year.
  - *Pros:* Prevents dead-end selections; better UX.
  - *Cons:* Every endpoint in §6 needs a `year` query parameter added;
    more complex queries.

**Recommendation (Architecture Recommendation, NOT Approved Decision):**
Option A for v1 (matches IPS-001 §6 as already planned), with Option B
as a Future Enhancement once real catalog data shows whether dead-end
selections are actually a problem in practice.

**Decision:** Pending Human Decision

**Decision Rationale:** —

**Architecture Impact:** If Option B, IPS-001 §6's endpoint signatures
need revision.

**Implementation Impact:** Medium — mainly an API query-parameter
change, not a schema change.

**Future Impact:** Could be added later without a breaking schema
change either way.

---

## BDR-0009 — Admin vs. Super Admin Role Distinction

| Field | Value |
|---|---|
| Category | Permissions |
| Priority | Medium |
| Blocking? | Yes — blocks finalizing IPS-001 §9's permission table and the eventual Authentication module scope |
| Implementation Impact | Medium |
| Related BR IDs | BR-0004 |
| Related Decisions | IPS-001 §9, §17.6 |

**Question:** Is there a real distinction between "Admin" and "Super
Admin" roles for Vehicle Master, or was that carried over from the
prompt template without a confirmed requirement?

**Background:** No FS/SDD document defines role granularity beyond
"Dealer" vs. "Admin." IPS-001 §9 included a "Super Admin" column only
because the requested table shape asked for it.

**Affected Documents:** IPS-001 §9, future FS-003 (Authentication).

**Affected Modules:** Vehicle Master (permissions), Authentication
(role definitions).

**Possible Options:**

- **Option A — No distinction:** collapse to a single "Admin" role for
  now; drop "Super Admin" from IPS-001 §9 as premature.
  - *Pros:* Matches what FS-000/SDD-000 actually define; avoids
    building permission logic for an undefined role.
  - *Cons:* If a real need for privilege tiers emerges later, requires
    revisiting.
- **Option B — Confirm the distinction now:** define what Super Admin
  can do that Admin cannot (e.g. deleting Brands outright, managing
  other Admins).
  - *Pros:* Future-proofs permission design.
  - *Cons:* Invents scope not requested anywhere else yet — risks
    building unused complexity.

**Recommendation (Architecture Recommendation, NOT Approved Decision):**
Option A — defer role granularity to FS-003 (Authentication) when it's
actually scoped, rather than deciding it piecemeal inside Vehicle
Master's permission table.

**Decision:** Pending Human Decision

**Decision Rationale:** —

**Architecture Impact:** IPS-001 §9 should be simplified to Dealer/Admin
only if Option A is chosen.

**Implementation Impact:** Medium — affects the permission-check logic
shape, not the schema.

**Future Impact:** Directly informs FS-003's scope when drafted.

---

## BDR-0010 — Pricing Edit Audit/Versioning Trail

| Field | Value |
|---|---|
| Category | Versioning / Security |
| Priority | Medium |
| Blocking? | Partially — does not block the base schema, but blocks finalizing the `version` column IPS-001 §3 already sketched |
| Implementation Impact | Medium |
| Related BR IDs | BR-0007 (by analogy, not directly — BR-0007 covers Calculation Results, not Vehicle Master pricing) |
| Related Decisions | SDD-000 §7 (NFR — Audit logging), IPS-001 §10, §17.7 |

**Question:** Do in-place pricing edits on an Active Vehicle Master
Record need their own audit/versioning trail, distinct from Calculation
Result immutability (BR-0007, which covers a different entity)?

**Background:** IPS-001 §3 sketched a `version` column on
`vehicle_master_record` without confirming whether it's actually needed,
and SDD-000 §7 already flags "all pricing edits are audit-logged" as an
NFR — but audit-*logging* (LOG-001's Audit level) and audit-*versioning*
(keeping old pricing rows queryable) are different mechanisms.

**Affected Documents:** SDD-000 §7, IPS-001 §3, §5, §10, §16.

**Affected Modules:** Vehicle Master.

**Possible Options:**

- **Option A — Log only, no versioning table:** rely on LOG-001's
  Audit-level logging for every pricing change; the `vehicle_master_
  record` row itself is simply updated in place.
  - *Pros:* Simpler schema; satisfies SDD-000 §7's audit-logging NFR
    without extra tables.
  - *Cons:* Reconstructing "what was the MSP on date X" requires
    replaying logs, not a simple query.
- **Option B — Versioned table:** every pricing edit creates a new row
  (or a history table), and the `version` column IPS-001 §3 sketched is
  used for real.
  - *Pros:* Direct queryability of pricing history; supports future
    "what did this vehicle's price look like when the Evaluation was
    done" reporting.
  - *Cons:* More schema complexity now, for a reporting need not yet
    requested anywhere.

**Recommendation (Architecture Recommendation, NOT Approved Decision):**
Option A for v1 — satisfies the existing SDD-000 §7 NFR via LOG-001
without adding schema complexity; drop the `version` column from
IPS-001 §3 unless Option B is chosen, and move full versioning to
IPS-001 §16 Future Enhancements (where "Version history" is already
listed).

**Decision:** Pending Human Decision

**Decision Rationale:** —

**Architecture Impact:** If Option A, IPS-001 §3's schema sketch is
simplified (drop `version`); if Option B, LOG-001's audit-log approach
needs a cross-reference note rather than replacing it.

**Implementation Impact:** Medium — schema and migration complexity
difference between the two options.

**Future Impact:** Option B, if deferred, becomes a clean "add a
history table" migration later without disrupting the base schema.

---

## BDR-0011 — Distinct "Archived" State

| Field | Value |
|---|---|
| Category | Vehicle Identity / Database |
| Priority | Low |
| Blocking? | No |
| Implementation Impact | Low |
| Related BR IDs | — |
| Related Decisions | SDD-000 §3, IPS-001 §10, §17.8 |

**Question:** Does Vehicle Master need a distinct "Archived" terminal
state beyond "Deprecated," or is Deprecated sufficient?

**Background:** SDD-000 §3's state machine for Vehicle Master Record
only defines Draft → Active → Deprecated. IPS-001 §10 asked whether a
separate Archival step (as exists for Evaluation) makes sense here too.

**Affected Documents:** SDD-000 §3, IPS-001 §10.

**Affected Modules:** Vehicle Master.

**Possible Options:**

- **Option A — Keep Deprecated as terminal:** no separate Archived
  state.
  - *Pros:* Matches SDD-000 exactly; one less enum value to maintain.
  - *Cons:* No way to distinguish "recently deprecated, might still be
    relevant" from "long retired, hide from all admin views by
    default" if that distinction ever matters.
- **Option B — Add Archived after Deprecated:** mirrors the Evaluation
  lifecycle's Archived state.
  - *Pros:* Consistent lifecycle pattern across entities; supports
    hiding very old catalog entries from default Admin views.
  - *Cons:* Requires an SDD-000 §3 amendment; not currently justified
    by any stated requirement.

**Recommendation (Architecture Recommendation, NOT Approved Decision):**
Option A — no stated need justifies the extra state; add it later if a
real requirement emerges (cheap enum addition given BDR-0006's Option B
recommendation).

**Decision:** Pending Human Decision

**Decision Rationale:** —

**Architecture Impact:** None if Option A.

**Implementation Impact:** Low.

**Future Impact:** Easy to add later regardless of choice now.

---

## BDR-0012 — E-AUTHZ-001 Addition to the Error Catalogue

| Field | Value |
|---|---|
| Category | Security / Architecture |
| Priority | Low |
| Blocking? | No |
| Implementation Impact | Low |
| Related BR IDs | BR-0004 |
| Related Decisions | SDD-000 §8 (Error Catalogue), IPS-001 §12, §17.9 |

**Question:** Should `E-AUTHZ-001` (Dealer attempts to write pricing/
catalog data) be formally added to SDD-000 §8's Error Catalogue, or is
it Vehicle-Master-local?

**Background:** IPS-001 §12 introduced this error code because SDD-000
§8's catalogue has no generic authorization-failure entry, only
domain-specific errors (E-PRICING-001, E-CATALOG-001/002, E-SUB-001,
E-NET-001, E-DEALER-001).

**Affected Documents:** SDD-000 §8, IPS-001 §12.

**Affected Modules:** All (any module with Admin-only write endpoints
will hit the same class of error).

**Possible Options:**

- **Option A — Add a generic authorization error family to SDD-000
  §8** (e.g. `E-AUTHZ-001` as a reusable, module-agnostic code).
  - *Pros:* Consistent error handling across all modules per API-000's
    error structure; avoids each module inventing its own.
  - *Cons:* Requires an SDD-000 edit now, slightly ahead of when other
    modules actually need it.
- **Option B — Keep it Vehicle-Master-local for now,** formalize
  centrally only when a second module needs the same pattern.
  - *Pros:* No SDD-000 edit needed yet.
  - *Cons:* Risk of each module inventing a slightly different
    authorization error code later, requiring cleanup.

**Recommendation (Architecture Recommendation, NOT Approved Decision):**
Option A — this is exactly the kind of cross-cutting concern SDD-000 §8
should own, and the cost of adding one generic entry now is low.

**Decision:** Pending Human Decision

**Decision Rationale:** —

**Architecture Impact:** If Option A, requires a (minor, additive) edit
to SDD-000 §8 — flagged here, not made, per this prompt's constraint not
to modify SDD-000.

**Implementation Impact:** Low.

**Future Impact:** Sets the pattern for Authentication/Admin/Subscription
modules' own authorization errors.

---

## BDR-0013 — Offline Capability for v1

| Field | Value |
|---|---|
| Category | Architecture / Scalability |
| Priority | Medium |
| Blocking? | No — does not block Vehicle Master DB-001, but affects Flutter client architecture broadly |
| Implementation Impact | High (if required) |
| Related BR IDs | — |
| Related Decisions | SDD-000 §7 (NFR) |

**Question:** Is offline capability required for the Flutter client in
v1?

**Background:** SDD-000 §7 listed this as an explicit assumption ("Not
required for v1") rather than a confirmed decision.

**Affected Documents:** SDD-000 §7, any future Flutter architecture
document.

**Affected Modules:** All (client-wide concern, not Vehicle-Master
specific).

**Possible Options:**

- **Option A — No offline support in v1** (confirm SDD-000's
  assumption).
  - *Pros:* Simpler client architecture; no local-cache/sync-conflict
    design needed now.
  - *Cons:* Dealers in low-connectivity environments (plausible for a
    dealer-lot use case) may find this limiting.
- **Option B — Offline support required.**
  - *Pros:* Better fit if dealer connectivity is unreliable in
    practice.
  - *Cons:* Significant added architecture (local storage, sync,
    conflict resolution) — a substantial scope increase this late in
    planning.

**Recommendation (Architecture Recommendation, NOT Approved Decision):**
Option A — confirm the existing assumption; revisit only if real dealer
usage shows connectivity is a genuine problem.

**Decision:** Pending Human Decision

**Decision Rationale:** —

**Architecture Impact:** Confirms SDD-000 §7 as final rather than
provisional, if Option A.

**Implementation Impact:** High if Option B is chosen instead — this
would be a significant scope addition.

**Future Impact:** None if Option A; major if Option B chosen later.

---

## BDR-0014 — Multi-Region / Multi-Currency Support for v1

| Field | Value |
|---|---|
| Category | Scalability / Pricing |
| Priority | Medium |
| Blocking? | Yes (partially) — interacts with BDR-0002 (Margin scope); affects whether pricing fields need a currency dimension |
| Implementation Impact | High (if required) |
| Related BR IDs | BR-0001 |
| Related Decisions | SDD-000 §7 (NFR) |

**Question:** Is multi-region/multi-currency support required for v1?

**Background:** SDD-000 §7 listed this as an assumption ("single locale/
currency") rather than a confirmed decision.

**Affected Documents:** SDD-000 §7, IPS-001 §5 (pricing columns would
need a currency/region dimension if required).

**Affected Modules:** Vehicle Master (schema), Valuation Engine
(calculation currency handling).

**Possible Options:**

- **Option A — Single locale/currency for v1** (confirm SDD-000's
  assumption).
  - *Pros:* Simplest schema — MSP/Margin/Scrap Value as plain numeric
    columns, no currency code needed.
  - *Cons:* A future multi-region expansion would require adding a
    currency dimension retroactively.
- **Option B — Multi-region/currency from v1.**
  - *Pros:* Avoids a future migration if BIKEVALUATOR expands regions
    early.
  - *Cons:* Adds complexity (currency conversion, region-scoped
    catalog entries) with no confirmed near-term need.

**Recommendation (Architecture Recommendation, NOT Approved Decision):**
Option A — no stated business requirement justifies the added
complexity yet; this interacts with BDR-0002, so both should ideally be
decided together.

**Decision:** Pending Human Decision

**Decision Rationale:** —

**Architecture Impact:** Confirms SDD-000 §7 as final, if Option A.

**Implementation Impact:** High if Option B — affects the core pricing
schema (IPS-001 §5).

**Future Impact:** None if Option A now, but a real cost later if
multi-region is added retroactively.

---

## Categorization Summary

| Category | BDRs |
|---|---|
| Pricing | BDR-0002, BDR-0003, BDR-0004, BDR-0014 |
| Vehicle Identity | BDR-0005, BDR-0008, BDR-0011 |
| Permissions | BDR-0009 |
| Security | BDR-0012 |
| Versioning | BDR-0010 |
| Data Ownership | BDR-0001 |
| UX | BDR-0007, BDR-0008 |
| Database | BDR-0006, BDR-0011 |
| Reporting | BDR-0004 |
| Architecture | BDR-0001, BDR-0012, BDR-0013 |
| Scalability | BDR-0013, BDR-0014 |

---

## Decision Dependency Graph

```text
BDR-0005 (Brand/Model/Variant decomposition)
   ↓
BDR-0001 (Repair cost table ownership) ── interacts with schema shape from BDR-0005
   ↓
BDR-0002 (Margin scope) ── ↔ BDR-0014 (multi-region/currency) — decide together
   ↓
BDR-0003 (Scrap Value derivation)
   ↓
BDR-0006 (status enum implementation) ── ↔ BDR-0011 (Archived state)
   ↓
Database schema (IPS-001 §5) finalized
   ↓
BDR-0008 (Brand/Model by Year) ── affects API query shape
   ↓
API (IPS-001 §6)
   ↓
BDR-0009 (Admin vs Super Admin) ── affects API permission checks
   ↓
Flutter (IPS-001 §7)
   ↓
BDR-0007 (search threshold) ── Flutter UI detail only
   ↓
Reports (downstream, reads BDR-0004's thresholds via BR-0003/BR-0008)

Independent of the above chain:
BDR-0010 (audit/versioning trail) — affects schema (IPS-001 §3) but not
   the Brand/Model/Variant/pricing chain directly
BDR-0012 (E-AUTHZ-001) — cross-cutting, affects SDD-000 §8 for all
   modules, not just Vehicle Master
BDR-0013 (offline capability) — client-wide, independent of Vehicle
   Master's schema entirely
```

**How to read this:** BDR-0005 and BDR-0001 are upstream of nearly
everything else — resolve those first. BDR-0002/0003/0006/0011 shape the
rest of the schema. BDR-0008/0009 shape the API and Flutter layers.
BDR-0004/0007/0010/0012/0013/0014 are comparatively independent and can
be decided in any order relative to each other.

---

## Blocking Matrix

| Decision | Blocks | Priority | Owner |
|---|---|---|---|
| BDR-0001 (Repair Cost Ownership) | Vehicle Master DB-001, Valuation Engine IPS-002 | Critical | Human |
| BDR-0002 (Margin Scope) | Vehicle Master DB-001 (pricing schema) | Critical | Human |
| BDR-0003 (Scrap Value Derivation) | Vehicle Master DB-001 (validation rules) | Critical | Human |
| BDR-0005 (Brand/Model/Variant Decomposition) | Vehicle Master DB-001 (entire schema shape) | Critical | Human |
| BDR-0006 (Status Enum Implementation) | Vehicle Master DB-001 (migration syntax) | Medium | Human |
| BDR-0008 (Brand/Model by Year) | Vehicle Master API design (IPS-001 §6) | Medium | Human |
| BDR-0009 (Admin vs Super Admin) | Vehicle Master permissions (IPS-001 §9), FS-003 scope | Medium | Human |
| BDR-0010 (Audit/Versioning Trail) | Vehicle Master DB-001 (`version` column decision) | Medium | Human |
| BDR-0004 (Recommendation Thresholds) | Valuation Engine implementation, Reports | Critical (for those modules) | Human |
| BDR-0011 (Archived State) | Nothing blocking — cosmetic/future | Low | Human |
| BDR-0012 (E-AUTHZ-001) | Nothing blocking — cross-cutting cleanup | Low | Human |
| BDR-0007 (Search Threshold) | Nothing blocking — Flutter UX detail | Low | Human |
| BDR-0013 (Offline Capability) | Flutter client architecture (whenever that's drafted) | Medium | Human |
| BDR-0014 (Multi-Region/Currency) | Vehicle Master DB-001 (pricing schema, interacts with BDR-0002) | Medium | Human |

**Recommended order for answering them** (matches the Decision
Dependency Graph): BDR-0005 → BDR-0001 → BDR-0002 + BDR-0014 (together)
→ BDR-0003 → BDR-0006 + BDR-0011 (together) → BDR-0008 → BDR-0009 →
BDR-0010 → BDR-0004 → BDR-0012 → BDR-0007 → BDR-0013.
