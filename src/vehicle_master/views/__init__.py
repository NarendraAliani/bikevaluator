# Full Path: src/vehicle_master/views/__init__.py
# Relative Path: views/__init__.py
# Module: vehicle_master
# Purpose: Re-exports every Vehicle Master REST view.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: API-001, EP-001 §5 (Endpoint Implementation Order), IMP-001C, ISP-002 §1, EP-002 §5
from vehicle_master.views.admin_valuation_master_views import (
    AdminValuationMasterDetailView,
    AdminValuationMasterView,
)
from vehicle_master.views.admin_vehicle_views import (
    AdminVehicleCatalogDetailView,
    AdminVehicleCatalogView,
)
from vehicle_master.views.catalog_views import (
    BrandListView,
    ConfigurationView,
    ModelListView,
    VariantListView,
)
from vehicle_master.views.valuation_views import (
    RepairComponentListView,
    ValuationCalculateView,
)

__all__ = [
    "BrandListView",
    "ModelListView",
    "VariantListView",
    "ConfigurationView",
    "AdminVehicleCatalogView",
    "AdminVehicleCatalogDetailView",
    "AdminValuationMasterView",
    "AdminValuationMasterDetailView",
    "RepairComponentListView",
    "ValuationCalculateView",
]
