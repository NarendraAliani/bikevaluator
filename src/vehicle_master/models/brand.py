# Full Path: src/vehicle_master/models/brand.py
# Relative Path: models/brand.py
# Module: vehicle_master
# Purpose: Django ORM model for the Brand catalog entity.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: DBD-001 §2 (Vehicle Master - brands table),
#   DDD-001 §3 (Brand domain object), EP-001 §3 (Database Package)
import uuid

from django.db import models


class Brand(models.Model):
    """
    Manufacturer identity (e.g. Honda, Bajaj, TVS) - DDD-001 §3.

    Roots the Model -> Variant hierarchy (DBD-001 §2). No business
    logic lives here (per IMP-001A scope) - duplicate-name rejection
    and any other write-time policy belong to the Service layer
    (ISP-001 FR-001-007 / E-CATALOG-001), not this model.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand_name = models.CharField(
        max_length=100,
        help_text=(
            "Proposed max length default (ISP-001 §6) - not specified in "
            "DBD-001/BRR-001; see FS-001 Open Question #3."
        ),
    )
    active = models.BooleanField(
        default=True,
        help_text="Soft-delete flag (DBD-001 §5) - no hard deletes in this schema.",
    )
    # Bookkeeping timestamps only - NOT an optimistic-concurrency token.
    # DBD-001/ENG-0003 scope optimistic locking to valuation_master and
    # repair_options only (see EP-001 Open Question #5, still unresolved).
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "brands"
        ordering = ["brand_name"]
        indexes = [
            models.Index(fields=["brand_name"], name="idx_brands_brand_name"),
        ]

    def __str__(self) -> str:
        return self.brand_name
