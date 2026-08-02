# Business Glossary — BIKEVALUATOR

Definitions of domain-specific terms used across BIKEVALUATOR
documentation, prompts, and code. Update whenever a new business term is
introduced in a BRD, FS, or decision. Canonical source for these
definitions: `ai/architecture/fs/FS-000-core-domain-valuation.md`.

| Term | Definition | Source |
|---|---|---|
| BIKEVALUATOR | B2B SaaS platform for dealer-focused used two-wheeler valuation, built around a centralized pricing/valuation engine, sold via subscription | BUS-0001 |
| Dealer | The B2B customer/tenant using the platform to evaluate vehicles for purchase | FS-000 |
| Vehicle | A specific used two-wheeler being evaluated, identified by Year + Brand + Model + Variant | FS-000 |
| Brand | Manufacturer (e.g. Honda, Bajaj, TVS) | FS-000 |
| Model | A product line within a brand (e.g. Honda Activa) | FS-000 |
| Variant | A specific configuration of a model (e.g. Activa 125 Standard, Disc) | FS-000 |
| Year | Manufacturing year of the specific vehicle instance being evaluated | FS-000 |
| MSP (Minimum Selling Price) | Baseline resale market price for a given Year+Brand+Model+Variant, maintained centrally | FS-000 |
| Margin | Required profit buffer subtracted from MSP to derive purchase price | FS-000 |
| Purchase Price | Recommended price the dealer should pay to acquire the vehicle | FS-000 |
| Scrap Value | Floor price — a vehicle is never valued below this | FS-000 |
| Repair Cost | Estimated cost to bring inspected components to sellable condition | FS-000 |
| Recommendation | Categorical buy signal: Excellent/Good/Average Buy or Scrap | FS-000 §5 |
| Excellent / Good / Average Buy, Scrap | Recommendation tiers by score band (≥90% / 75-89% / 60-74% / <60%, provisional) | FS-000 §5 |

| Evaluation | The stateful record of a dealer assessing one Vehicle, from Draft through Completed/Archived | SDD-000 §2, §3 |
| Vehicle Master Record | The catalog entry (Brand+Model+Variant+Year+pricing) a Vehicle instance refers to | SDD-000 §2 |
| Calculation Result | Immutable system-computed record of MSP/Margin/Repair Cost/Scrap Value inputs and the resulting Purchase Price | SDD-000 §2 |
| Super Admin | The single administrative role (no separate plain "Admin" tier) that may edit MSP, Margin, Scrap Value, repair costs, and vehicles | BRD-001 §5 |
| Rounding Rule | Final Purchase Price is rounded to the nearest ₹10 before display | BR-0009 |

_Populate further as Vehicle Master and Valuation Engine FS documents add
terms (e.g. component-specific vocabulary for Engine/Color/Tyres/
Gearbox/Clutch/Plastic states)._
