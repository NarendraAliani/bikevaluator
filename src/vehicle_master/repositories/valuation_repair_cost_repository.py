# Full Path: src/vehicle_master/repositories/valuation_repair_cost_repository.py
# Relative Path: repositories/valuation_repair_cost_repository.py
# Module: vehicle_master
# Purpose: Persistence for the ValuationRepairCost model - the ₹
#   deduction amount for one RepairOption, scoped to one ValuationMaster.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: IMP-003 (introduces this model/repository),
#   BRR-001 BR-0010, DDD-001 §3, IMP-003B Task 3 (batched get_amounts,
#   replacing a per-option N+1 query pattern in ValuationService.calculate)
import uuid
from decimal import Decimal
from typing import Optional

from vehicle_master.models import ValuationRepairCost


class ValuationRepairCostRepository:
    """Persistence for ``ValuationRepairCost`` rows, scoped by parent ValuationMaster."""

    def get_by_valuation_master(
        self, valuation_master_id: uuid.UUID
    ) -> list[ValuationRepairCost]:
        """Return every repair-cost row for one ValuationMaster (pricing version)."""
        return list(
            ValuationRepairCost.objects.filter(
                valuation_master_id=valuation_master_id
            ).select_related("repair_option", "repair_option__repair_component")
        )

    def get_amount(
        self, valuation_master_id: uuid.UUID, repair_option_id: uuid.UUID
    ) -> Optional[Decimal]:
        """Return the deduction amount for one (ValuationMaster, RepairOption) pair, or ``None``."""
        row = ValuationRepairCost.objects.filter(
            valuation_master_id=valuation_master_id, repair_option_id=repair_option_id
        ).first()
        return row.deduction_amount if row is not None else None

    def get_amounts(
        self, valuation_master_id: uuid.UUID, repair_option_ids: list[uuid.UUID]
    ) -> dict:
        """
        Batched form of ``get_amount`` - one query for every id in
        ``repair_option_ids`` instead of one query per id (IMP-003B
        Task 3 - fixes the N+1 pattern in ``ValuationService.calculate``).

        :returns: ``{repair_option_id: deduction_amount}`` - ids with no
            cost row for this vehicle are simply absent from the dict.
        """
        if not repair_option_ids:
            return {}
        rows = ValuationRepairCost.objects.filter(
            valuation_master_id=valuation_master_id,
            repair_option_id__in=repair_option_ids,
        )
        return {row.repair_option_id: row.deduction_amount for row in rows}

    def upsert(
        self,
        valuation_master_id: uuid.UUID,
        repair_option_id: uuid.UUID,
        deduction_amount: Decimal,
    ) -> ValuationRepairCost:
        """
        Create or update the deduction amount for one (ValuationMaster,
        RepairOption) pair - used by the data importer (IMP-003), never
        by a Dealer-facing view.
        """
        row, _ = ValuationRepairCost.objects.update_or_create(
            valuation_master_id=valuation_master_id,
            repair_option_id=repair_option_id,
            defaults={"deduction_amount": deduction_amount},
        )
        return row
