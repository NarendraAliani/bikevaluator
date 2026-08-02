# Full Path: src/vehicle_master/views/admin_vehicle_views.py
# Relative Path: views/admin_vehicle_views.py
# Module: vehicle_master
# Purpose: Super-Admin REST views for Brand/Model/Variant CRUD - thin
#   transport over VehicleMasterAdminService.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: API-001 (/admin/vehicles), ISP-001 §1.5/§1.6,
#   BRR-001 BR-0004/BR-0011, IMP-001C, IMP-001D (architecture refinement:
#   centralized service factory, ActorProvider, RequestContext,
#   dispatch-map deduplication - per architect review, no behavior change)
"""
Thin transport only. Authorization (BR-0004) is enforced inside
``VehicleMasterAdminService`` (via ``authorization.enforce_super_admin``)
- these views never check ``actor.role`` themselves, they only build a
``RequestContext`` (actor + IP, via the injected ``ActorProvider``) and
pass it through, exactly once per call, to exactly one Service method.

``/admin/vehicles`` remains one shared endpoint for Brand/Model/Variant,
discriminated by ``entityType`` (ISP-001 §1.5, unchanged from IMP-001C -
this is an API-contract detail, not touched by this refactor). Dispatch
now goes through lookup maps (``_CREATE_HANDLERS``/``_UPDATE_HANDLERS``/
``_DEACTIVATE_HANDLERS``/``_TO_DICT``) instead of repeated if/elif
chains (IMP-001D, per architect review) - still selects and calls
exactly one Service method per request, identical HTTP behavior to
IMP-001C.
"""

import uuid

from rest_framework.views import APIView

from vehicle_master.actor_provider import build_actor_provider
from vehicle_master.api_utils import success_response
from vehicle_master.request_context import build_request_context
from vehicle_master.serializers import (
    AdminVehicleCatalogEntrySerializer,
    CreateVehicleCatalogEntrySerializer,
    EntityTypeQuerySerializer,
    UpdateVehicleCatalogEntrySerializer,
)
from vehicle_master.service_factory import build_vehicle_master_admin_service


def _brand_to_dict(brand) -> dict:
    return {
        "id": brand.id,
        "entity_type": "BRAND",
        "parent_id": None,
        "name": brand.brand_name,
        "active": brand.active,
    }


def _model_to_dict(model) -> dict:
    return {
        "id": model.id,
        "entity_type": "MODEL",
        "parent_id": model.brand_id,
        "name": model.model_name,
        "active": model.active,
    }


def _variant_to_dict(variant) -> dict:
    return {
        "id": variant.id,
        "entity_type": "VARIANT",
        "parent_id": variant.model_id,
        "name": variant.variant_name,
        "active": variant.active,
    }


#: entityType -> to_dict converter (IMP-001D: replaces repeated if/elif).
_TO_DICT = {
    "BRAND": _brand_to_dict,
    "MODEL": _model_to_dict,
    "VARIANT": _variant_to_dict,
}

#: entityType -> create handler. Each: (service, name, parent_id, context) -> model instance.
#: Signatures differ per entity (Model/Variant need parent_id, Brand doesn't) - the lambda
#: wrapper normalizes that so the view's call site is uniform regardless of entityType.
_CREATE_HANDLERS = {
    "BRAND": lambda service, name, parent_id, context: service.create_brand(
        name, context.actor, context.ip_address
    ),
    "MODEL": lambda service, name, parent_id, context: service.create_model(
        parent_id, name, context.actor, context.ip_address
    ),
    "VARIANT": lambda service, name, parent_id, context: service.create_variant(
        parent_id, name, context.actor, context.ip_address
    ),
}

#: entityType -> update handler. Each: (service, entity_id, name, context) -> model instance.
_UPDATE_HANDLERS = {
    "BRAND": lambda service, entity_id, name, context: service.update_brand(
        entity_id, name, context.actor, context.ip_address
    ),
    "MODEL": lambda service, entity_id, name, context: service.update_model(
        entity_id, name, context.actor, context.ip_address
    ),
    "VARIANT": lambda service, entity_id, name, context: service.update_variant(
        entity_id, name, context.actor, context.ip_address
    ),
}

#: entityType -> deactivate handler. Each: (service, entity_id, context) -> None.
_DEACTIVATE_HANDLERS = {
    "BRAND": lambda service, entity_id, context: service.deactivate_brand(
        entity_id, context.actor, context.ip_address
    ),
    "MODEL": lambda service, entity_id, context: service.deactivate_model(
        entity_id, context.actor, context.ip_address
    ),
    "VARIANT": lambda service, entity_id, context: service.deactivate_variant(
        entity_id, context.actor, context.ip_address
    ),
}


class AdminVehicleCatalogView(APIView):
    """``POST /admin/vehicles`` - FR-001-006/007/011 (Brand/Model/Variant creation)."""

    def post(self, request):
        body = CreateVehicleCatalogEntrySerializer(data=request.data)
        body.is_valid(raise_exception=True)
        validated = body.validated_data
        entity_type = validated["entity_type"]
        name = validated["name"]
        parent_id = validated.get("parent_id")

        context = build_request_context(request, build_actor_provider())
        service = build_vehicle_master_admin_service()

        created = _CREATE_HANDLERS[entity_type](service, name, parent_id, context)
        entry = _TO_DICT[entity_type](created)

        data = AdminVehicleCatalogEntrySerializer(entry).data
        return success_response(data, status_code=201)


class AdminVehicleCatalogDetailView(APIView):
    """``PUT``/``DELETE /admin/vehicles/{entity_id}`` - FR-001-006/010/011."""

    def put(self, request, entity_id: uuid.UUID):
        entity_type = self._entity_type(request)
        body = UpdateVehicleCatalogEntrySerializer(data=request.data)
        body.is_valid(raise_exception=True)
        name = body.validated_data["name"]

        context = build_request_context(request, build_actor_provider())
        service = build_vehicle_master_admin_service()

        updated = _UPDATE_HANDLERS[entity_type](service, entity_id, name, context)
        entry = _TO_DICT[entity_type](updated)

        data = AdminVehicleCatalogEntrySerializer(entry).data
        return success_response(data)

    def delete(self, request, entity_id: uuid.UUID):
        entity_type = self._entity_type(request)
        context = build_request_context(request, build_actor_provider())
        service = build_vehicle_master_admin_service()

        _DEACTIVATE_HANDLERS[entity_type](service, entity_id, context)

        return success_response(None)

    @staticmethod
    def _entity_type(request) -> str:
        """
        Discovered-gap fix (IMP-001C, unchanged by this refactor):
        ``entityType`` is required as a query parameter on PUT/DELETE,
        mirroring GET/POST's pattern, since ``{entity_id}`` alone
        doesn't say which table it belongs to.
        """
        query = EntityTypeQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        return query.validated_data["entity_type"]
