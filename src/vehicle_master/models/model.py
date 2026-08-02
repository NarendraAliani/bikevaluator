# Full Path: src/vehicle_master/models/model.py
# Relative Path: models/model.py
# Module: vehicle_master
# Purpose: Django ORM model for the Model (product line) catalog entity.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: DBD-001 §2 (Vehicle Master - models table),
#   DDD-001 §3 (Model domain object), EP-001 §3 (Database Package)
import uuid

from django.db import models

from vehicle_master.models.brand import Brand


class Model(models.Model):
    """
    A product line within a Brand (e.g. Honda Activa) - DDD-001 §3.

    Named ``Model`` to match DDD-001/DBD-001's own domain terminology
    verbatim (NS-001 §13). This does not collide with Django's own
    ``django.db.models`` module, since that module is imported and
    referenced as ``models.Model`` (the base class), not as a bare
    ``Model`` name - see IMP-001A Known Limitations for the readability
    note this naming choice carries for callers.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.RESTRICT,
        related_name="models",
        help_text="Roots the Variant list for this Model (DDD-001 §3).",
    )
    model_name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "models"
        ordering = ["model_name"]
        indexes = [
            models.Index(fields=["brand"], name="idx_models_brand_id"),
            models.Index(
                fields=["brand", "model_name"], name="idx_models_brand_model_name"
            ),
        ]

    def __str__(self) -> str:
        return self.model_name
