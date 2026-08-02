# Full Path: src/vehicle_master/serializers/configuration_serializer.py
# Relative Path: serializers/configuration_serializer.py
# Module: vehicle_master
# Purpose: Query-param and response serializers for GET /vehicles/configuration.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §1.4/§2.4 (ConfigurationDto), API-001
"""No business logic - field parsing/shaping only."""

from rest_framework import serializers


class ConfigurationQuerySerializer(serializers.Serializer):
    """Query-param validation for ``GET /vehicles/configuration`` (ISP-001 §1.4)."""

    year = serializers.IntegerField(required=True)
    brand_id = serializers.UUIDField(required=True)
    model_id = serializers.UUIDField(required=True)
    variant_id = serializers.UUIDField(required=True)


class RepairOptionGroupSerializer(serializers.Serializer):
    """
    Read-only pass-through shape (ISP-001 §2.4). Always serializes an
    empty list today - Repair Master has no implementation anywhere in
    this codebase (see ``VehicleCatalogService.get_configuration``).
    """

    repairComponentId = serializers.UUIDField()
    repairComponentName = serializers.CharField()
    options = serializers.ListField(child=serializers.DictField())


class ConfigurationSerializer(serializers.Serializer):
    """Maps the ``Configuration`` dataclass (vehicle_catalog_service.py) to ISP-001 §2.4's ``ConfigurationDto``."""

    valuationMasterId = serializers.UUIDField(source="valuation_master_id")
    year = serializers.IntegerField()
    variantId = serializers.UUIDField(source="variant_id")
    minimumSellingPrice = serializers.DecimalField(
        source="minimum_selling_price", max_digits=12, decimal_places=2
    )
    margin = serializers.DecimalField(max_digits=12, decimal_places=2)
    scrapValue = serializers.DecimalField(
        source="scrap_value", max_digits=12, decimal_places=2
    )
    repairOptions = RepairOptionGroupSerializer(source="repair_options", many=True)
