# Full Path: src/vehicle_master/views/admin_valuation_master_views.py
# Relative Path: views/admin_valuation_master_views.py
# Module: vehicle_master
# Purpose: Super-Admin REST views for ValuationMaster versioning - thin
#   transport over VehicleMasterAdminService.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: API-001 (/admin/valuation-master), ISP-001 §1.7,
#   BRR-001 BR-0004/BR-0007/BR-0011, DBD-001 §6a (ENG-0003), IMP-001C,
#   IMP-001D (architecture refinement: centralized service factory,
#   ActorProvider, RequestContext - per architect review, no behavior change)
"""
Thin transport only - each method calls exactly one
``VehicleMasterAdminService`` method. BR-0007 versioning, BR-0011
uniqueness, and ENG-0003 optimistic concurrency are all enforced inside
the Service/Repository layers (IMP-001A/B) - this view never touches
that logic, only request parsing and response shaping.

Service construction and actor/IP resolution now go through the
centralized ``service_factory``/``ActorProvider``/``RequestContext``
(IMP-001D) instead of this module's own ``_build_admin_service()`` and
``_InMemoryAuditLogRepository`` (both removed - see
``admin_vehicle_views.py``'s IMP-001C history for where they lived).
"""

import uuid

from rest_framework.views import APIView

from vehicle_master.actor_provider import build_actor_provider
from vehicle_master.api_utils import success_response
from vehicle_master.request_context import build_request_context
from vehicle_master.serializers import (
    CreateValuationMasterVersionSerializer,
    ValuationMasterSerializer,
)
from vehicle_master.service_factory import build_vehicle_master_admin_service


class AdminValuationMasterView(APIView):
    """``POST /admin/valuation-master`` - FR-001-008/009/011/012 (new pricing version)."""

    def post(self, request):
        body = CreateValuationMasterVersionSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        validated = body.validated_data

        context = build_request_context(request, build_actor_provider())
        service = build_vehicle_master_admin_service()

        valuation_master = service.create_valuation_master_version(
            year=validated["year"],
            variant_id=validated["variant_id"],
            minimum_selling_price=validated["minimum_selling_price"],
            margin=validated["margin"],
            scrap_value=validated["scrap_value"],
            expected_previous_updated_at=validated.get("previous_version_updated_at"),
            actor=context.actor,
            ip_address=context.ip_address,
        )
        data = ValuationMasterSerializer(valuation_master).data
        return success_response(data, status_code=201)


class AdminValuationMasterDetailView(APIView):
    """``DELETE /admin/valuation-master/{valuation_master_id}`` - FR-001-011 (retire pricing entirely)."""

    def delete(self, request, valuation_master_id: uuid.UUID):
        context = build_request_context(request, build_actor_provider())
        service = build_vehicle_master_admin_service()
        service.deactivate_valuation_master(
            valuation_master_id, context.actor, context.ip_address
        )
        return success_response(None)
