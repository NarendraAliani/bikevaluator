# Full Path: src/vehicle_master/models/variant.py
# Relative Path: models/variant.py
# Module: vehicle_master
# Purpose: Django ORM model for the Variant catalog entity.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: DBD-001 §2 (Vehicle Master - variants table),
#   DDD-001 §3 (Variant domain object), EP-001 §3 (Database Package)
import uuid

from django.db import models

from vehicle_master.models.model import Model


class Variant(models.Model):
    """
    A specific configuration of a Model (e.g. Activa 125 Standard,
    Disc) - DDD-001 §3. The unit that ValuationMaster prices, per Year.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey(
        Model,
        on_delete=models.RESTRICT,
        related_name="variants",
        help_text="Roots the ValuationMaster rows priced against this Variant.",
    )
    variant_name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "variants"
        ordering = ["variant_name"]
        indexes = [
            models.Index(fields=["model"], name="idx_variants_model_id"),
            models.Index(
                fields=["model", "variant_name"], name="idx_variants_model_var_name"
            ),
        ]

    def __str__(self) -> str:
        return self.variant_name
