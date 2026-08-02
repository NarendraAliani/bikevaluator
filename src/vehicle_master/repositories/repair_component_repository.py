# Full Path: src/vehicle_master/repositories/repair_component_repository.py
# Relative Path: repositories/repair_component_repository.py
# Module: vehicle_master
# Purpose: Persistence-only repository for the RepairComponent model.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-002 §3, DBD-001 §2, EP-002 §2
"""
Persistence-only repository for ``RepairComponent`` (DBD-001 §2).
Read-only from every Dealer-facing View in this module; administration
is FS-004's concern (ISP-002 §3). ``get_by_name``/``create`` exist only
because IMP-003's data importer must bootstrap this catalog itself -
FS-004 doesn't exist yet to do it via an Admin API. No business rules.
"""

import uuid
from typing import Optional

from vehicle_master.models import RepairComponent


class RepairComponentRepository:
    """Persistence for ``RepairComponent`` rows - read-only for Dealer views, write for the IMP-003 importer."""

    def get_active(self) -> list[RepairComponent]:
        """Return all active RepairComponents, e.g. for `/repairs/components`."""
        return list(RepairComponent.objects.filter(active=True).order_by("name"))

    def get_by_id(self, repair_component_id: uuid.UUID) -> Optional[RepairComponent]:
        """Return a single RepairComponent by id, or ``None`` if not found."""
        return RepairComponent.objects.filter(id=repair_component_id).first()

    def get_by_name(self, name: str) -> Optional[RepairComponent]:
        """Return a single active RepairComponent by exact name, or ``None`` (IMP-003's importer)."""
        return RepairComponent.objects.filter(name=name, active=True).first()

    def create(self, name: str) -> RepairComponent:
        """Persist a new RepairComponent row (IMP-003's importer only)."""
        return RepairComponent.objects.create(name=name)
