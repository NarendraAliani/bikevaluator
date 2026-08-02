# BUS-001 — Review Checklist

| Field | Value |
|---|---|
| Document ID | BUS-001-review-checklist |
| Version | 1.0 |
| Status | Needs Review |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | BDR-001-business-decisions.md |
| Next Documents | New BUS/ARC decisions logged in `ai/decisions/decisions.md` once answered |

Answer each item below, then return this file (or a copy) so answers can
be converted into formal `BUS-000x`/`ARC-000x` decisions and applied to
BRR-001/SDD-000/IPS-001. Recommended answering order matches BDR-001's
Blocking Matrix: BDR-0005 → BDR-0001 → BDR-0002 + BDR-0014 → BDR-0003 →
BDR-0006 + BDR-0011 → BDR-0008 → BDR-0009 → BDR-0010 → BDR-0004 →
BDR-0012 → BDR-0007 → BDR-0013.

---

### BDR-0005 — Brand/Model/Variant Entity Decomposition

☐ Option A — Normalize into separate Brand/Model/Variant tables
☐ Option B — Denormalize into a single table with plain columns
☐ Custom: _______________________________________________

Rationale:
```



```

---

### BDR-0001 — Repair Component Cost Table Ownership

☐ Option A — Vehicle Master owns repair cost tables (per SDD-000 as written)
☐ Option B — Valuation Engine owns repair cost tables
☐ Option C — Split: Vehicle Master owns cost values, Valuation Engine owns component definitions
☐ Custom: _______________________________________________

Rationale:
```



```

---

### BDR-0002 — Margin Scope

☐ Option A — Global (one value per Vehicle Master Record)
☐ Option B — Per-dealer override
☐ Option C — Per-region
☐ Custom: _______________________________________________

Rationale:
```



```

---

### BDR-0014 — Multi-Region / Multi-Currency Support for v1

☐ Option A — Single locale/currency for v1
☐ Option B — Multi-region/currency from v1
☐ Custom: _______________________________________________

Rationale:
```



```

---

### BDR-0003 — Scrap Value Derivation

☐ Option A — Independently maintained (Admin-entered)
☐ Option B — Derived as a percentage of MSP
☐ Custom: _______________________________________________

Rationale:
```



```

---

### BDR-0006 — Status Enum Implementation

☐ Option A — Native Postgres enum type
☐ Option B — `varchar` + check constraint
☐ Option C — Integer + application-level enum
☐ Custom: _______________________________________________

Rationale:
```



```

---

### BDR-0011 — Distinct "Archived" State

☐ Option A — Keep Deprecated as terminal (no separate Archived state)
☐ Option B — Add Archived after Deprecated
☐ Custom: _______________________________________________

Rationale:
```



```

---

### BDR-0008 — Brand/Model Availability Varying by Year

☐ Option A — No Year-based filtering (Brand/Model always complete lists)
☐ Option B — Year-based filtering throughout the cascading dropdown
☐ Custom: _______________________________________________

Rationale:
```



```

---

### BDR-0009 — Admin vs. Super Admin Role Distinction

☐ Option A — No distinction; collapse to a single "Admin" role for now
☐ Option B — Confirm and define the Super Admin distinction now
☐ Custom: _______________________________________________

Rationale:
```



```

---

### BDR-0010 — Pricing Edit Audit/Versioning Trail

☐ Option A — Log only (LOG-001 Audit level), no versioning table
☐ Option B — Versioned table (history of pricing changes)
☐ Custom: _______________________________________________

Rationale:
```



```

---

### BDR-0004 — Recommendation Thresholds

☐ Option A — Confirm as-is (≥90% Excellent, 75-89% Good, 60-74% Average, <60% Scrap)
☐ Option B — Adjust thresholds (specify below)
☐ Option C — Defer to Admin-configurable value
☐ Custom: _______________________________________________

If Option B, new thresholds:
```



```

Rationale:
```



```

---

### BDR-0012 — E-AUTHZ-001 Addition to the Error Catalogue

☐ Option A — Add a generic authorization error family to SDD-000 §8
☐ Option B — Keep it Vehicle-Master-local for now
☐ Custom: _______________________________________________

Rationale:
```



```

---

### BDR-0007 — Vehicle Selector Search Threshold

☐ Option A — Always use type-ahead search
☐ Option B — Plain dropdown below a fixed item count, type-ahead above it
☐ Custom: _______________________________________________

If Option B, threshold count: _______

Rationale:
```



```

---

### BDR-0013 — Offline Capability for v1

☐ Option A — No offline support in v1
☐ Option B — Offline support required
☐ Custom: _______________________________________________

Rationale:
```



```

---

## Sign-off

Reviewed by: _______________________
Date: _______________________
