# Full Path: src/vehicle_master/serializers/catalog_serializers.py
# Relative Path: serializers/catalog_serializers.py
# Module: vehicle_master
# Purpose: Response serializers for Brand/Model/Variant, and query-param
#   serializers for the list endpoints.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §2.4 (BrandDto/ModelDto/VariantDto), NS-001 §7
#   (camelCase JSON field names, snake_case ORM fields)
"""
No business logic - field parsing/shaping only, per IMP-001C's explicit
scope. Field names are camelCase in JSON (NS-001 §7's client-facing
boundary translation), mapped via ``source=`` to the snake_case ORM
field.
"""

from rest_framework import serializers


class BrandSerializer(serializers.Serializer):
    """Maps a ``Brand`` model instance to ISP-001 §2.4's ``BrandDto`` shape."""

    id = serializers.UUIDField()
    brandName = serializers.CharField(source="brand_name")


class ModelSerializer(serializers.Serializer):
    """Maps a ``Model`` model instance to ISP-001 §2.4's ``ModelDto`` shape."""

    id = serializers.UUIDField()
    brandId = serializers.UUIDField(source="brand_id")
    modelName = serializers.CharField(source="model_name")


class VariantSerializer(serializers.Serializer):
    """Maps a ``Variant`` model instance to ISP-001 §2.4's ``VariantDto`` shape."""

    id = serializers.UUIDField()
    modelId = serializers.UUIDField(source="model_id")
    variantName = serializers.CharField(source="variant_name")


class ModelListQuerySerializer(serializers.Serializer):
    """Query-param validation for ``GET /vehicles/models``."""

    brand_id = serializers.UUIDField(required=True)


class VariantListQuerySerializer(serializers.Serializer):
    """Query-param validation for ``GET /vehicles/variants``."""

    model_id = serializers.UUIDField(required=True)
