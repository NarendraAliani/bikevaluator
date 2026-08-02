# Full Path: src/vehicle_master/repositories/repair_component_repository.py
# Relative Path: repositories/repair_component_repository.py
# Module: vehicle_master
# Purpose: Persistence-only repository for the RepairComponent model.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-002 §3, DBD-001 §2, EP-002 §2
"""
Persistence-only repository for ``RepairComponent`` (DBD-001 §2).
Read methods only - this module (Valuation Engine) never writes here;
administration is FS-004's concern (ISP-002 §3). No business rules.
"""

import uuid
from typing import Optional

from vehicle_master.models import RepairComponent


class RepairComponentRepository:
    """Read-only persistence for ``RepairComponent`` rows."""

    def get_active(self) -> list[RepairComponent]:
        """Return all active RepairComponents, e.g. for `/repairs/components`."""
        return list(RepairComponent.objects.filter(active=True).order_by("name"))

    def get_by_id(self, repair_component_id: uuid.UUID) -> Optional[RepairComponent]:
        """Return a single RepairComponent by id, or ``None`` if not found."""
        return RepairComponent.objects.filter(id=repair_component_id).first()
