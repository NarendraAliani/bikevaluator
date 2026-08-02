# Full Path: src/vehicle_master/models/valuation_master.py
# Relative Path: models/valuation_master.py
# Module: vehicle_master
# Purpose: Django ORM model for ValuationMaster (MSP/Margin/Scrap Value pricing).
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: DBD-001 §2/§6/§6a (Valuation Master table, versioning,
#   transaction/concurrency policy), DDD-001 §3 (ValuationMaster domain
#   object), BRR-001 BR-0007/BR-0011, EP-001 §3 (Database Package)
import uuid

from django.db import models

from vehicle_master.models.variant import Variant
from vehicle_master.validators import validate_non_negative_amount, validate_year_range


class ValuationMaster(models.Model):
    """
    The centrally-controlled pricing truth for a given Year+Variant -
    MSP, Margin, Scrap Value (DDD-001 §3). This is BIKEVALUATOR's
    business IP table (DBD-001 §1).

    Versioning (BR-0007): a pricing edit closes the current Active
    row's ``effective_to`` and inserts a new row - never an in-place
    overwrite. ``updated_at`` is the optimistic-concurrency token for
    that write (ENG-0003, DBD-001 §6a) - this is the ONE model in this
    module where ``updated_at`` is confirmed to serve that purpose
    (contrast Brand/Model/Variant, where it is bookkeeping only).

    Uniqueness (BR-0011): exactly one Active row per Year+Variant,
    enforced below as a **partial unique constraint** (``active=True``
    only) - a plain unique constraint would incorrectly block
    BR-0007's legitimate superseded/historical rows, which share the
    same Year+Variant while inactive.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.PositiveIntegerField(validators=[validate_year_range])
    variant = models.ForeignKey(
        Variant,
        on_delete=models.RESTRICT,
        related_name="valuation_master_versions",
    )
    minimum_selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[validate_non_negative_amount],
        help_text="MSP - proposed precision default (max_digits/decimal_places not specified in DBD-001).",
    )
    margin = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[validate_non_negative_amount]
    )
    scrap_value = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[validate_non_negative_amount]
    )
    active = models.BooleanField(default=True)
    effective_from = models.DateTimeField()
    effective_to = models.DateTimeField(null=True, blank=True)
    # Confirmed optimistic-concurrency token (ENG-0003, DBD-001 §6a) -
    # NOT merely bookkeeping, unlike the same-named field on
    # Brand/Model/Variant.
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "valuation_master"
        ordering = ["-effective_from"]
        constraints = [
            # BR-0011 implementation detail (EP-001 §3): a plain unique
            # constraint on (year, variant) would wrongly reject
            # BR-0007's historical (inactive) rows for the same
            # Year+Variant. The partial condition restricts uniqueness
            # to Active rows only.
            models.UniqueConstraint(
                fields=["year", "variant"],
                condition=models.Q(active=True),
                name="uniq_active_valmaster_year_variant",
            ),
            models.CheckConstraint(
                condition=models.Q(minimum_selling_price__gte=0),
                name="chk_valmaster_msp_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(margin__gte=0),
                name="chk_valmaster_margin_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(scrap_value__gte=0),
                name="chk_valmaster_scrap_non_negative",
            ),
        ]
        indexes = [
            models.Index(fields=["active"], name="idx_valmaster_active"),
        ]

    def __str__(self) -> str:
        return f"ValuationMaster(year={self.year}, variant_id={self.variant_id})"
