# Full Path: src/vehicle_master/serializers/valuation_master_serializers.py
# Relative Path: serializers/valuation_master_serializers.py
# Module: vehicle_master
# Purpose: Request/response serializers for /admin/valuation-master.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §2.3/§2.4, BRR-001 BR-0007/BR-0011, ENG-0003
"""No business logic - field parsing/UUID/Decimal parsing/required fields only."""

from rest_framework import serializers


class CreateValuationMasterVersionSerializer(serializers.Serializer):
    """Request body for ``POST /admin/valuation-master`` (ISP-001 §2.3)."""

    year = serializers.IntegerField(required=True)
    variantId = serializers.UUIDField(source="variant_id", required=True)
    minimumSellingPrice = serializers.DecimalField(
        source="minimum_selling_price", max_digits=12, decimal_places=2, required=True
    )
    margin = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    scrapValue = serializers.DecimalField(
        source="scrap_value", max_digits=12, decimal_places=2, required=True
    )
    previousVersionUpdatedAt = serializers.DateTimeField(
        source="previous_version_updated_at", required=False, allow_null=True
    )


class ValuationMasterSerializer(serializers.Serializer):
    """Response shape (ISP-001 §2.4's ``ValuationMasterDto``)."""

    id = serializers.UUIDField()
    year = serializers.IntegerField()
    variantId = serializers.UUIDField(source="variant_id")
    minimumSellingPrice = serializers.DecimalField(
        source="minimum_selling_price", max_digits=12, decimal_places=2
    )
    margin = serializers.DecimalField(max_digits=12, decimal_places=2)
    scrapValue = serializers.DecimalField(
        source="scrap_value", max_digits=12, decimal_places=2
    )
    active = serializers.BooleanField()
    effectiveFrom = serializers.DateTimeField(source="effective_from")
    effectiveTo = serializers.DateTimeField(source="effective_to", allow_null=True)
    updatedAt = serializers.DateTimeField(source="updated_at")
