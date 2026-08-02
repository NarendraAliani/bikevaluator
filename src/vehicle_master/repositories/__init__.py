# Full Path: src/vehicle_master/repositories/__init__.py
# Relative Path: repositories/__init__.py
# Module: vehicle_master
# Purpose: Re-exports every Vehicle Master repository class.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §3, EP-001 §2 (Backend Package - Folder Structure), ISP-002 §3, EP-002 §2
from vehicle_master.repositories.audit_log_repository import AuditLogRepository
from vehicle_master.repositories.brand_repository import BrandRepository
from vehicle_master.repositories.model_repository import ModelRepository
from vehicle_master.repositories.noop_audit_log_repository import NoOpAuditRepository
from vehicle_master.repositories.persistent_audit_log_repository import (
    PersistentAuditLogRepository,
)
from vehicle_master.repositories.repair_component_repository import (
    RepairComponentRepository,
)
from vehicle_master.repositories.repair_option_repository import RepairOptionRepository
from vehicle_master.repositories.valuation_master_repository import (
    ValuationMasterRepository,
)
from vehicle_master.repositories.valuation_repair_cost_repository import (
    ValuationRepairCostRepository,
)
from vehicle_master.repositories.variant_repository import VariantRepository

__all__ = [
    "AuditLogRepository",
    "NoOpAuditRepository",
    "PersistentAuditLogRepository",
    "BrandRepository",
    "ModelRepository",
    "VariantRepository",
    "ValuationMasterRepository",
    "RepairComponentRepository",
    "RepairOptionRepository",
    "ValuationRepairCostRepository",
]
