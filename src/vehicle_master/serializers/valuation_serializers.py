# Full Path: src/vehicle_master/serializers/valuation_serializers.py
# Relative Path: serializers/valuation_serializers.py
# Module: vehicle_master
# Purpose: Request/response serializers for POST /valuation/calculate.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-002 §2.1/§2.2, API-001, NS-001 §7 (camelCase JSON)
"""
No business logic - field parsing/UUID parsing/required fields only.
Response field names resolved to camelCase (``recommendedPrice``/
``roundedPrice``/``label``) per NS-001 §7, not API-001's literal
snake_case example - see ISP-002 §1.1's Architecture Compliance note.
"""

from rest_framework import serializers


class RepairAssessmentEntrySerializer(serializers.Serializer):
    """One ``{repairComponentId, repairOptionId}`` pair (ISP-002 §2.1)."""

    repairComponentId = serializers.UUIDField(source="repair_component_id")
    repairOptionId = serializers.UUIDField(source="repair_option_id")


class CalculateValuationRequestSerializer(serializers.Serializer):
    """Request body for ``POST /valuation/calculate`` (ISP-002 §2.1)."""

    year = serializers.IntegerField(required=True)
    variantId = serializers.UUIDField(source="variant_id", required=True)
    repairAssessment = RepairAssessmentEntrySerializer(
        many=True, source="repair_assessment", allow_empty=True
    )


class ValuationResultSerializer(serializers.Serializer):
    """Response shape (ISP-002 §2.2's ``ValuationResultDto``)."""

    recommendedPrice = serializers.DecimalField(
        source="recommended_price", max_digits=12, decimal_places=2
    )
    roundedPrice = serializers.DecimalField(
        source="rounded_price", max_digits=12, decimal_places=0
    )
    label = serializers.CharField()
