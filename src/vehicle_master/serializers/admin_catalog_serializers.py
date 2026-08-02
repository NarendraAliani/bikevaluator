# Full Path: src/vehicle_master/serializers/admin_catalog_serializers.py
# Relative Path: serializers/admin_catalog_serializers.py
# Module: vehicle_master
# Purpose: Request/response serializers for the Admin /admin/vehicles
#   endpoint (Brand/Model/Variant CRUD, entityType-discriminated).
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §1.5/§1.6/§2.1/§2.2 (entityType-discriminator
#   design), EP-001 §5
"""
No business logic here - field parsing/required-field checks only.
Name length/emptiness is intentionally NOT validated at this layer
(deferred entirely to ``vehicle_master.validators.validate_catalog_name``
in the Service layer) so the 100-char default (ISP-001 §6, itself a
proposed default, not a settled rule) has exactly one source of truth.

**DISCOVERED GAP, FIXED (IMP-001C):** ISP-001 §2.2's
``UpdateVehicleCatalogEntryRequest`` had no ``entityType`` field, yet
``PUT``/``DELETE /admin/vehicles/{id}`` must know whether ``{id}``
refers to a Brand, Model, or Variant to call the right Service method.
Minimal fix: ``entityType`` is required as a **query parameter** on
PUT/DELETE too (mirroring the pattern already used for GET/POST) -
see ``EntityTypeQuerySerializer`` below. No DBD-001/API-001/BRR-001
content was changed; this is an ISP-001-level implementation detail.
"""

from rest_framework import serializers

ENTITY_TYPE_CHOICES = ("BRAND", "MODEL", "VARIANT")


class CreateVehicleCatalogEntrySerializer(serializers.Serializer):
    """Request body for ``POST /admin/vehicles`` (ISP-001 §2.1)."""

    entityType = serializers.ChoiceField(choices=ENTITY_TYPE_CHOICES, source="entity_type")
    parentId = serializers.UUIDField(source="parent_id", required=False, allow_null=True)
    name = serializers.CharField(required=True, allow_blank=False)


class UpdateVehicleCatalogEntrySerializer(serializers.Serializer):
    """Request body for ``PUT /admin/vehicles/{id}`` (ISP-001 §2.2)."""

    name = serializers.CharField(required=True, allow_blank=False)


class EntityTypeQuerySerializer(serializers.Serializer):
    """
    Query-param for ``PUT``/``DELETE /admin/vehicles/{id}`` - the
    discovered-gap fix described in this file's module docstring.
    """

    entityType = serializers.ChoiceField(choices=ENTITY_TYPE_CHOICES, source="entity_type")


class AdminVehicleCatalogEntrySerializer(serializers.Serializer):
    """
    Response shape (ISP-001 §2.4's ``AdminVehicleCatalogEntryDto``).
    Operates on a plain dict assembled by the view (not directly on a
    Brand/Model/Variant instance, since those three models don't share
    a common ``entity_type``/``parent_id`` shape) - this is presentational
    mapping, not a business decision.
    """

    id = serializers.UUIDField()
    entityType = serializers.ChoiceField(choices=ENTITY_TYPE_CHOICES, source="entity_type")
    parentId = serializers.UUIDField(source="parent_id", allow_null=True)
    name = serializers.CharField()
    active = serializers.BooleanField()
