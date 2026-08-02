# Full Path: src/vehicle_master/views/valuation_views.py
# Relative Path: views/valuation_views.py
# Module: vehicle_master
# Purpose: Dealer-facing REST views for Repair Components and Valuation
#   calculation - thin transport over ValuationService/RecommendationService.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: API-001 (/repairs/components, /valuation/calculate),
#   ISP-002 §1, EP-002 §5, BRR-001 BR-0001/0002/0003/0005/0008/0009/0010,
#   IMP-003 (repair costs now scoped per Year+Variant - see
#   ValuationRepairCost's docstring - so /repairs/components now
#   requires year/variant_id query params; a real, flagged API contract
#   change, not a silent one)
"""
Thin transport only - every method calls exactly one Service method
(``ValuationService.list_repair_components`` / ``.calculate``). No
business logic here - the formula, scrap floor, rounding, recommendation
banding, and (as of IMP-003) the ValuationMaster-scoped repair-cost
lookup all happen in the Service layer (EP-002 §2).

No authorization check - confirmed no Super-Admin-only concern exists
in this module (ISP-002 §title note); any authenticated Dealer may call
both endpoints.
"""

from rest_framework.views import APIView

from vehicle_master.api_utils import success_response
from vehicle_master.serializers import (
    CalculateValuationRequestSerializer,
    RepairComponentListQuerySerializer,
    RepairComponentSerializer,
    ValuationResultSerializer,
)
from vehicle_master.service_factory import build_valuation_service


class RepairComponentListView(APIView):
    """``GET /repairs/components?year=&variant_id=`` - lists components + their vehicle-scoped options (IMP-003)."""

    def get(self, request):
        query = RepairComponentListQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        validated = query.validated_data

        service = build_valuation_service()
        components = service.list_repair_components(
            year=validated["year"], variant_id=validated["variant_id"]
        )

        data = RepairComponentSerializer(components, many=True).data
        return success_response({"components": data})


class ValuationCalculateView(APIView):
    """``POST /valuation/calculate`` - FR-002-001..009."""

    def post(self, request):
        body = CalculateValuationRequestSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        validated = body.validated_data

        repair_option_ids = [
            entry["repair_option_id"] for entry in validated["repair_assessment"]
        ]

        service = build_valuation_service()
        result = service.calculate(
            year=validated["year"],
            variant_id=validated["variant_id"],
            repair_option_ids=repair_option_ids,
        )

        data = ValuationResultSerializer(result).data
        return success_response(data)
