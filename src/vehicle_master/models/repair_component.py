# Full Path: src/vehicle_master/models/repair_component.py
# Relative Path: models/repair_component.py
# Module: vehicle_master
# Purpose: Django ORM model for the RepairComponent catalog entity.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: DBD-001 §2 (Repair Module - repair_components table),
#   DDD-001 §3 (RepairComponent domain object), ISP-002 §3, EP-002 §3
import uuid

from django.db import models


class RepairComponent(models.Model):
    """
    A named part of the vehicle whose condition affects price (Engine,
    Colour, Gearbox, Tyre, Plastic, Clutch, and future components) -
    DDD-001 §3. Groups its RepairOptions.

    Read-only from this module's (Valuation Engine's) perspective -
    administration is FS-004's concern (ISP-002 §3). No business logic
    here, matching the Brand/Model/Variant precedent (IMP-001A).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    active = models.BooleanField(
        default=True, help_text="Soft-delete flag (DBD-001 §5) - no hard deletes."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "repair_components"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"], name="idx_repair_components_name"),
        ]

    def __str__(self) -> str:
        return self.name
