# Full Path: src/vehicle_master/models/repair_option.py
# Relative Path: models/repair_option.py
# Module: vehicle_master
# Purpose: Django ORM model for the RepairOption catalog entity.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: DBD-001 §2 (Repair Module - repair_options table),
#   DDD-001 §3 (RepairOption domain object), BRR-001 BR-0010,
#   DBD-001 §6a (ENG-0003 - updated_at reserved for a future FS-004
#   write path, unused by this read-only module), ISP-002 §3, EP-002 §3
import uuid

from django.db import models

from vehicle_master.models.repair_component import RepairComponent
from vehicle_master.validators import validate_non_negative_amount


class RepairOption(models.Model):
    """
    One selectable condition state for a RepairComponent (OK/Partial/
    Full), with a fixed ₹ deduction (BR-0010) - DDD-001 §3.

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
    deduction_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[validate_non_negative_amount],
        help_text="Fixed ₹ deduction (BR-0010) - never a percentage.",
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "repair_options"
        ordering = ["option_name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(deduction_amount__gte=0),
                name="chk_repair_option_deduction_non_negative",
            ),
        ]
        indexes = [
            models.Index(
                fields=["repair_component"], name="idx_repair_options_component"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.repair_component_id}:{self.option_name}"
