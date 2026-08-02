# Full Path: src/vehicle_master/urls.py
# Relative Path: urls.py
# Module: vehicle_master
# Purpose: URL routing - Dealer APIs and Admin APIs kept in two
#   explicitly separate pattern lists, per IMP-001C's routing constraint.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: API-001 (endpoint inventory), EP-001 §5
#   (Endpoint Implementation Order), IMP-001C
"""
Routing created exactly once - no path is registered twice. Dealer and
Admin endpoints are kept in two distinct lists (never interleaved) so
the separation is visible in the code itself, not just conventionally.
"""

from django.urls import path

from vehicle_master.views import (
    AdminValuationMasterDetailView,
    AdminValuationMasterView,
    AdminVehicleCatalogDetailView,
    AdminVehicleCatalogView,
    BrandListView,
    ConfigurationView,
    ModelListView,
    RepairComponentListView,
    ValuationCalculateView,
    VariantListView,
)

# --- Dealer APIs (read-only/compute, any authenticated role) ----------------

dealer_urlpatterns = [
    path("vehicles/brands", BrandListView.as_view(), name="vehicle-master-brands"),
    path("vehicles/models", ModelListView.as_view(), name="vehicle-master-models"),
    path("vehicles/variants", VariantListView.as_view(), name="vehicle-master-variants"),
    path(
        "vehicles/configuration",
        ConfigurationView.as_view(),
        name="vehicle-master-configuration",
    ),
    path(
        "repairs/components",
        RepairComponentListView.as_view(),
        name="vehicle-master-repair-components",
    ),
    path(
        "valuation/calculate",
        ValuationCalculateView.as_view(),
        name="vehicle-master-valuation-calculate",
    ),
]

# --- Admin APIs (Super Admin only, BR-0004) ---------------------------------

admin_urlpatterns = [
    path(
        "admin/vehicles",
        AdminVehicleCatalogView.as_view(),
        name="vehicle-master-admin-vehicles",
    ),
    path(
        "admin/vehicles/<uuid:entity_id>",
        AdminVehicleCatalogDetailView.as_view(),
        name="vehicle-master-admin-vehicles-detail",
    ),
    path(
        "admin/valuation-master",
        AdminValuationMasterView.as_view(),
        name="vehicle-master-admin-valuation-master",
    ),
    path(
        "admin/valuation-master/<uuid:valuation_master_id>",
        AdminValuationMasterDetailView.as_view(),
        name="vehicle-master-admin-valuation-master-detail",
    ),
]

urlpatterns = dealer_urlpatterns + admin_urlpatterns
