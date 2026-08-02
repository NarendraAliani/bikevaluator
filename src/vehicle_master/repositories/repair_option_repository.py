# Full Path: src/vehicle_master/repositories/repair_option_repository.py
# Relative Path: repositories/repair_option_repository.py
# Module: vehicle_master
# Purpose: Persistence-only repository for the RepairOption model.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-002 §3, DBD-001 §2, BRR-001 BR-0010, EP-002 §2
"""
Persistence-only repository for ``RepairOption`` (DBD-001 §2). Read-only
for Dealer views - same reasoning as ``RepairComponentRepository``;
``get_by_component_and_option_name``/``create`` exist only for IMP-003's
data importer.
"""

import uuid
from typing import Optional

from vehicle_master.models import RepairOption


class RepairOptionRepository:
    """Persistence for ``RepairOption`` rows - read-only for Dealer views, write for the IMP-003 importer."""

    def get_active_by_component(
        self, repair_component_id: uuid.UUID
    ) -> list[RepairOption]:
        """Return all active RepairOptions for a given RepairComponent."""
        return list(
            RepairOption.objects.filter(
                repair_component_id=repair_component_id, active=True
            ).order_by("option_name")
        )

    def get_active_by_components(self, repair_component_ids: list[uuid.UUID]) -> dict:
        """
        Batched form of ``get_active_by_component`` - one query for
        every id in ``repair_component_ids`` instead of one query per
        component (IMP-003B Task 3 - fixes the N+1 pattern in
        ``ValuationService.list_repair_components``).

        :returns: ``{repair_component_id: [RepairOption, ...]}``.
        """
        if not repair_component_ids:
            return {}
        grouped: dict = {component_id: [] for component_id in repair_component_ids}
        options = RepairOption.objects.filter(
            repair_component_id__in=repair_component_ids, active=True
        ).order_by("option_name")
        for option in options:
            grouped[option.repair_component_id].append(option)
        return grouped

    def get_by_id(self, repair_option_id: uuid.UUID) -> Optional[RepairOption]:
        """Return a single RepairOption by id, or ``None`` if not found."""
        return RepairOption.objects.filter(id=repair_option_id).first()

    def get_by_component_and_option_name(
        self, repair_component_id: uuid.UUID, option_name: str
    ) -> Optional[RepairOption]:
        """Return a single active RepairOption by (component, option_name), or ``None`` (IMP-003's importer)."""
        return RepairOption.objects.filter(
            repair_component_id=repair_component_id,
            option_name=option_name,
            active=True,
        ).first()

    def create(self, repair_component_id: uuid.UUID, option_name: str) -> RepairOption:
        """Persist a new RepairOption row (IMP-003's importer only)."""
        return RepairOption.objects.create(
            repair_component_id=repair_component_id, option_name=option_name
        )
