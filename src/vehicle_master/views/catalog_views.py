# Full Path: src/vehicle_master/views/catalog_views.py
# Relative Path: views/catalog_views.py
# Module: vehicle_master
# Purpose: Dealer-facing, read-only REST views - thin transport over VehicleCatalogService.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: API-001 (Vehicle Master endpoints), ISP-001 §1.1-1.4,
#   EP-001 §5, IMP-001C, IMP-001D (architecture refinement: centralized
#   service factory, no behavior change, per architect review)
"""
Thin transport only - every method calls exactly one
``VehicleCatalogService`` method. No business logic here: existence
checks, error selection, and the actual pricing lookup all happen in
the Service layer (IMP-001B); a view's only jobs are request parsing
(via serializers), calling the service, and shaping the response.

Service construction goes through ``service_factory`` (IMP-001D) -
this module no longer defines its own ``_build_vehicle_catalog_service()``.
"""

from rest_framework.views import APIView

from vehicle_master.api_utils import success_response
from vehicle_master.serializers import (
    BrandSerializer,
    ConfigurationQuerySerializer,
    ConfigurationSerializer,
    ModelListQuerySerializer,
    ModelSerializer,
    VariantListQuerySerializer,
    VariantSerializer,
)
from vehicle_master.service_factory import build_vehicle_catalog_service


class BrandListView(APIView):
    """``GET /vehicles/brands`` - FR-001-001."""

    def get(self, request):
        service = build_vehicle_catalog_service()
        brands = service.list_brands()
        data = BrandSerializer(brands, many=True).data
        return success_response({"brands": data})


class ModelListView(APIView):
    """``GET /vehicles/models?brand_id=`` - FR-001-002."""

    def get(self, request):
        query = ModelListQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        service = build_vehicle_catalog_service()
        models = service.list_models(query.validated_data["brand_id"])
        data = ModelSerializer(models, many=True).data
        return success_response({"models": data})


class VariantListView(APIView):
    """``GET /vehicles/variants?model_id=`` - FR-001-003."""

    def get(self, request):
        query = VariantListQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        service = build_vehicle_catalog_service()
        variants = service.list_variants(query.validated_data["model_id"])
        data = VariantSerializer(variants, many=True).data
        return success_response({"variants": data})


class ConfigurationView(APIView):
    """``GET /vehicles/configuration?year=&brand_id=&model_id=&variant_id=`` - FR-001-004/005."""

    def get(self, request):
        query = ConfigurationQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        validated = query.validated_data
        service = build_vehicle_catalog_service()
        configuration = service.get_configuration(
            year=validated["year"],
            brand_id=validated["brand_id"],
            model_id=validated["model_id"],
            variant_id=validated["variant_id"],
        )
        data = ConfigurationSerializer(configuration).data
        return success_response(data)
