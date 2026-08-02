# Full Path: src/vehicle_master/models/repair_option.py
# Relative Path: models/repair_option.py
# Module: vehicle_master
# Purpose: Django ORM model for the RepairOption catalog entity.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: DBD-001 §2 (Repair Module - repair_options table),
#   DDD-001 §3 (RepairOption domain object), BRR-001 BR-0010,
#   DBD-001 §6a (ENG-0003 - updated_at reserved for a future FS-004
#   write path, unused by this read-only module), ISP-002 §3, EP-002 §3,
#   IMP-003 (deduction_amount moved to ValuationRepairCost - see that
#   model's docstring for why)
import uuid

from django.db import models

from vehicle_master.models.repair_component import RepairComponent


class RepairOption(models.Model):
    """
    One selectable condition state for a RepairComponent (OK/Partial/
    Full) - DDD-001 §3. Pure catalog identity only: which options exist
    for a component. The ₹ deduction amount for a given option is no
    longer stored here (see ``ValuationRepairCost`` - IMP-003 discovered
    that real deduction amounts vary per Year+Variant, not globally per
    option, contradicting this table's original DBD-001 §9 design;
    resolved as a flagged Architecture Observation, not a silent change).

    Read-only from this module's (Valuation Engine's) perspective;
    ``updated_at`` is reserved as a future optimistic-concurrency token
    for FS-004's admin writes (same policy as ``valuation_master``,
    DBD-001 §6a) - not used by any method in this module, since
    Valuation Engine never writes here.
    """

    OPTION_NAME_CHOICES = (
        ("OK", "OK"),
        ("PARTIAL", "Partial"),
        ("FULL", "Full"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    repair_component = models.ForeignKey(
        RepairComponent,
        on_delete=models.RESTRICT,
        related_name="repair_options",
    )
    option_name = models.CharField(max_length=10, choices=OPTION_NAME_CHOICES)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "repair_options"
        ordering = ["option_name"]
        indexes = [
            models.Index(
                fields=["repair_component"], name="idx_repair_options_component"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.repair_component_id}:{self.option_name}"
