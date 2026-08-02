# Full Path: src/vehicle_master/serializers/repair_component_serializers.py
# Relative Path: serializers/repair_component_serializers.py
# Module: vehicle_master
# Purpose: Response serializers for GET /repairs/components.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-002 §2.3, API-001, NS-001 §7 (camelCase JSON)
"""No business logic - field parsing/shaping only."""

from rest_framework import serializers


class RepairOptionSerializer(serializers.Serializer):
    """Maps a ``RepairOption`` model instance to ISP-002 §2.3's shape."""

    id = serializers.UUIDField()
    optionName = serializers.CharField(source="option_name")
    deductionAmount = serializers.DecimalField(
        source="deduction_amount", max_digits=12, decimal_places=2
    )


class RepairComponentSerializer(serializers.Serializer):
    """
    Maps a component dict (assembled by the view from
    ``RepairComponentRepository`` + ``RepairOptionRepository``) to
    ISP-002 §2.3's ``RepairComponentDto`` shape.
    """

    id = serializers.UUIDField()
    name = serializers.CharField()
    options = RepairOptionSerializer(many=True)
