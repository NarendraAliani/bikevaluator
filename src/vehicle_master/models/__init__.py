# Full Path: src/vehicle_master/models/__init__.py
# Relative Path: models/__init__.py
# Module: vehicle_master
# Purpose: Re-exports every Vehicle Master ORM model for `from vehicle_master.models import X` usage.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: DBD-001 §2, EP-001 §2 (Backend Package - Folder Structure), EP-002 (Valuation Engine models)
from vehicle_master.models.brand import Brand
from vehicle_master.models.model import Model
from vehicle_master.models.repair_component import RepairComponent
from vehicle_master.models.repair_option import RepairOption
from vehicle_master.models.valuation_master import ValuationMaster
from vehicle_master.models.variant import Variant

__all__ = [
    "Brand",
    "Model",
    "Variant",
    "ValuationMaster",
    "RepairComponent",
    "RepairOption",
]
