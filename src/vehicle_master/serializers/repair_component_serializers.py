# Full Path: src/vehicle_master/serializers/repair_component_serializers.py
# Relative Path: serializers/repair_component_serializers.py
# Module: vehicle_master
# Purpose: Query and response serializers for GET /repairs/components.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-002 §2.3, API-001, NS-001 §7 (camelCase JSON),
#   IMP-003 (added year/variant_id query params - repair costs are now
#   scoped per vehicle, so the endpoint can no longer be parameterless)
"""No business logic - field parsing/shaping only."""

from rest_framework import serializers


class RepairComponentListQuerySerializer(serializers.Serializer):
    """
    Query-param validation for ``GET /repairs/components`` (IMP-003).

    Mirrors ``ConfigurationQuerySerializer`` deliberately - both
    endpoints now need the same Year+Variant scope to resolve a
    ValuationMaster.
    """

    year = serializers.IntegerField(required=True)
    variant_id = serializers.UUIDField(required=True)


class RepairOptionSerializer(serializers.Serializer):
    """Maps a ``RepairOption`` model instance to ISP-002 §2.3's shape."""

    id = serializers.UUIDField()
    optionName = serializers.CharField(source="option_name")
    deductionAmount = serializers.DecimalField(
        source="deduction_amount", max_digits=12, decimal_places=2
    )


class RepairComponentSerializer(serializers.Serializer):
    """
    Maps a component dict (assembled by
    ``ValuationService.list_repair_components``, IMP-003 - deduction
    amounts are scoped per vehicle, not assembled directly from the
    repositories by the view) to ISP-002 §2.3's ``RepairComponentDto`` shape.
    """

    id = serializers.UUIDField()
    name = serializers.CharField()
    options = RepairOptionSerializer(many=True)
