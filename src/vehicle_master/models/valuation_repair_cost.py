# Full Path: src/vehicle_master/models/valuation_repair_cost.py
# Relative Path: models/valuation_repair_cost.py
# Module: vehicle_master
# Purpose: Django ORM model for ValuationRepairCost - the ₹ deduction
#   amount for one RepairOption, scoped to one ValuationMaster (i.e. one
#   Year+Variant pricing version).
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: IMP-003 Architecture Observation (amends DBD-001 §9),
#   BRR-001 BR-0010, DDD-001 §3, ISP-002 §3
"""
IMP-003 discovered that the real 2W Valuation master data (the
architect-supplied spreadsheet) has repair deduction amounts that vary
per Year+Variant - e.g. Full Engine Expense is Rs.5000 for a 2012 Activa
but Rs.8000 for a 2025 Shine CB. DBD-001 Section 9's original
``repair_options`` table modeled ``deduction_amount`` as global per
(component, option) - that table can no longer hold this data
losslessly.

Per architect decision (2026-08-02, in response to an AskUserQuestion
raised before writing any import code): repair costs are now scoped per
ValuationMaster, exactly like ``minimum_selling_price``/``margin``
already are. This is a real DBD-001 amendment, not a silent
reinterpretation - flagged as an Architecture Observation and recorded
as a new decision in ``ai/decisions/decisions.md``.

No BR-0007-style versioning here: a superseded ``ValuationMaster`` row
keeps its own historical ``ValuationRepairCost`` rows untouched (FK is
to the specific pricing-version id, not to Year+Variant directly), so
history is preserved for free without a second effective_from/to
mechanism.
"""
import uuid

from django.db import models

from vehicle_master.models.repair_option import RepairOption
from vehicle_master.models.valuation_master import ValuationMaster
from vehicle_master.validators import validate_non_negative_amount


class ValuationRepairCost(models.Model):
    """The ₹ deduction amount for one RepairOption, for one ValuationMaster (pricing version)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    valuation_master = models.ForeignKey(
        ValuationMaster,
        on_delete=models.CASCADE,
        related_name="repair_costs",
    )
    repair_option = models.ForeignKey(
        RepairOption,
        on_delete=models.RESTRICT,
        related_name="valuation_costs",
    )
    deduction_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[validate_non_negative_amount],
        help_text="Fixed Rs. deduction (BR-0010) for this option, scoped to this vehicle/year.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "valuation_repair_costs"
        # IMP-003B (Database Optimization): no standalone index on
        # `valuation_master` alone - the UniqueConstraint below already
        # creates a composite index with `valuation_master` as its
        # leading column, which every mainstream RDBMS (incl. SQLite/
        # PostgreSQL) can and does use to serve a
        # `filter(valuation_master_id=...)` query on its own. A separate
        # single-column index here would be pure duplicate write
        # overhead (IMP-003A review finding) - removed, not added.
        constraints = [
            models.UniqueConstraint(
                fields=["valuation_master", "repair_option"],
                name="uniq_valuation_repair_cost_master_option",
            ),
            models.CheckConstraint(
                condition=models.Q(deduction_amount__gte=0),
                name="chk_valuation_repair_cost_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"ValuationRepairCost(valuation_master_id={self.valuation_master_id}, repair_option_id={self.repair_option_id})"
