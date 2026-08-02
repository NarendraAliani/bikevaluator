# Full Path: src/vehicle_master/repositories/repair_option_repository.py
# Relative Path: repositories/repair_option_repository.py
# Module: vehicle_master
# Purpose: Persistence-only repository for the RepairOption model.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-002 §3, DBD-001 §2, BRR-001 BR-0010, EP-002 §2
"""
Persistence-only repository for ``RepairOption`` (DBD-001 §2). Read
methods only - same reasoning as ``RepairComponentRepository``.
"""

import uuid
from typing import Optional

from vehicle_master.models import RepairOption


class RepairOptionRepository:
    """Read-only persistence for ``RepairOption`` rows, scoped by parent RepairComponent."""

    def get_active_by_component(
        self, repair_component_id: uuid.UUID
    ) -> list[RepairOption]:
        """Return all active RepairOptions for a given RepairComponent."""
        return list(
            RepairOption.objects.filter(
                repair_component_id=repair_component_id, active=True
            ).order_by("option_name")
        )

    def get_by_id(self, repair_option_id: uuid.UUID) -> Optional[RepairOption]:
        """Return a single RepairOption by id, or ``None`` if not found."""
        return RepairOption.objects.filter(id=repair_option_id).first()
