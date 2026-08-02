# Full Path: src/vehicle_master/service_factory.py
# Relative Path: service_factory.py
# Module: vehicle_master
# Purpose: Centralized construction of Vehicle Master + Valuation Engine
#   Service instances, replacing per-view-module _build_*_service() functions.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §4, ISP-002 §4, IMP-001C (introduced the
#   duplicated per-view factories), IMP-001D (centralized them per
#   architect review), EP-002/IMP-002 (extended for Valuation Engine,
#   reusing this module rather than creating a parallel one, per this
#   round's explicit "do not duplicate infrastructure" instruction)
"""
Service construction, centralized (IMP-001D refactor, extended by
IMP-002).

IMP-001C defined ``_build_vehicle_catalog_service()`` in
``catalog_views.py`` and ``_build_admin_service()`` in
``admin_vehicle_views.py`` (re-imported by
``admin_valuation_master_views.py``) - identical repository wiring
duplicated across files. This module is the one place that wiring lives
now, for both Vehicle Master and Valuation Engine.

IMP-001D's docstring said "this module has exactly two services" as the
reason not to introduce a general-purpose DI container. IMP-002 adds two
more (`ValuationService`, `RecommendationService`) - still four plain
builder functions, not a framework. Revisit the "no container needed"
judgment once this file's growth (not just its existence) becomes the
actual problem, not before.
"""

from typing import Optional

from vehicle_master.repositories import (
    AuditLogRepository,
    BrandRepository,
    ModelRepository,
    NoOpAuditRepository,
    RepairOptionRepository,
    ValuationMasterRepository,
    VariantRepository,
)
from vehicle_master.services.recommendation_service import RecommendationService
from vehicle_master.services.valuation_service import ValuationService
from vehicle_master.services.vehicle_catalog_service import VehicleCatalogService
from vehicle_master.services.vehicle_master_admin_service import (
    VehicleMasterAdminService,
)


def build_vehicle_catalog_service() -> VehicleCatalogService:
    """Construct a ``VehicleCatalogService`` with its repository dependencies."""
    return VehicleCatalogService(
        brand_repository=BrandRepository(),
        model_repository=ModelRepository(),
        variant_repository=VariantRepository(),
        valuation_master_repository=ValuationMasterRepository(),
    )


def build_vehicle_master_admin_service(
    audit_log_repository: Optional[AuditLogRepository] = None,
) -> VehicleMasterAdminService:
    """
    Construct a ``VehicleMasterAdminService`` with its repository
    dependencies. Defaults to ``NoOpAuditRepository`` - no real Audit
    module exists yet (IMP-001A/B/C). Pass a real implementation once
    one exists; no view changes required either way.
    """
    return VehicleMasterAdminService(
        brand_repository=BrandRepository(),
        model_repository=ModelRepository(),
        variant_repository=VariantRepository(),
        valuation_master_repository=ValuationMasterRepository(),
        audit_log_repository=audit_log_repository or NoOpAuditRepository(),
    )


def build_recommendation_service() -> RecommendationService:
    """Construct a ``RecommendationService`` - no repository dependency."""
    return RecommendationService()


def build_valuation_service() -> ValuationService:
    """Construct a ``ValuationService`` with its repository/service dependencies."""
    return ValuationService(
        valuation_master_repository=ValuationMasterRepository(),
        repair_option_repository=RepairOptionRepository(),
        recommendation_service=build_recommendation_service(),
    )
