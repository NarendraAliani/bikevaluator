# Full Path: src/vehicle_master/services/valuation_service.py
# Relative Path: services/valuation_service.py
# Module: vehicle_master
# Purpose: Orchestrates BR-0001 (formula), BR-0002 (scrap floor), BR-0009
#   (rounding) to compute a Purchase Price, then delegates to
#   RecommendationService for the label. Also lists Repair Components
#   scoped to a vehicle's ValuationMaster (IMP-003).
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: BRR-001 BR-0001/BR-0002/BR-0005/BR-0009/BR-0010,
#   ISP-002 §4, EP-002, ENG-0002 (stateless, no idempotency key needed),
#   IMP-003 (repair costs now scoped per ValuationMaster, not global)
"""
``ValuationService`` - the core calculation engine. Stateless: no write
happens anywhere in either method (v1, per FS-002 §2/§12 - `valuation_
requests` stays inactive). Depends on `ValuationMasterRepository`
(reused from Vehicle Master, IMP-001A), `RepairComponentRepository`, and
`ValuationRepairCostRepository` (IMP-003 - deduction amounts are scoped
per ValuationMaster, see that model's docstring for why).
"""

import uuid
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from vehicle_master.exceptions import PricingNotAvailableError
from vehicle_master.repositories import (
    RepairComponentRepository,
    RepairOptionRepository,
    ValuationMasterRepository,
    ValuationRepairCostRepository,
)
from vehicle_master.services.recommendation_service import RecommendationService


@dataclass
class ValuationResult:
    """Mirrors ISP-002 §2.2's ``ValuationResultDto`` - this Service layer's return type."""

    recommended_price: Decimal
    rounded_price: Decimal
    label: str


class ValuationService:
    """Orchestrates BR-0001/BR-0002/BR-0009, then BR-0003/BR-0008 via RecommendationService."""

    def __init__(
        self,
        valuation_master_repository: ValuationMasterRepository,
        repair_component_repository: RepairComponentRepository,
        valuation_repair_cost_repository: ValuationRepairCostRepository,
        recommendation_service: RecommendationService,
        repair_option_repository: RepairOptionRepository = None,
    ) -> None:
        self._valuation_master_repository = valuation_master_repository
        self._repair_component_repository = repair_component_repository
        self._valuation_repair_cost_repository = valuation_repair_cost_repository
        self._recommendation_service = recommendation_service
        # IMP-003B Task 3: batched RepairOption lookup to fix the N+1
        # query pattern list_repair_components() previously had via
        # `component.repair_options.filter(...)` per component. Kept
        # optional (default None -> lazily constructed) so existing
        # callers that built this service before this round's change
        # don't break - see service_factory.build_valuation_service.
        self._repair_option_repository = repair_option_repository or RepairOptionRepository()

    def list_repair_components(self, year: int, variant_id: uuid.UUID) -> list[dict]:
        """
        FR-002-002: Repair Components + their Options, with deduction
        amounts scoped to this vehicle's Year+Variant ValuationMaster
        (IMP-003 - amounts are no longer global per option).

        :raises PricingNotAvailableError: VAL003/E-PRICING-001 (BR-0005)
            if no Active ValuationMaster exists for Year+Variant - a
            Dealer cannot browse repair costs for a vehicle with no
            pricing configured at all.
        """
        valuation_master = self._valuation_master_repository.get_active_by_year_variant(
            year, variant_id
        )
        if valuation_master is None:
            raise PricingNotAvailableError(
                f"No Active ValuationMaster for Year={year}, Variant={variant_id}."
            )

        cost_by_option_id = {
            cost.repair_option_id: cost.deduction_amount
            for cost in self._valuation_repair_cost_repository.get_by_valuation_master(
                valuation_master.id
            )
        }

        # IMP-003B Task 3: two queries total (components, then every
        # component's options in one batched IN query) instead of the
        # previous 1+N pattern (one query per component).
        active_components = self._repair_component_repository.get_active()
        options_by_component_id = self._repair_option_repository.get_active_by_components(
            [component.id for component in active_components]
        )

        components = []
        for component in active_components:
            priced_options = [
                option
                for option in options_by_component_id.get(component.id, [])
                if option.id in cost_by_option_id
            ]
            components.append(
                {
                    "id": component.id,
                    "name": component.name,
                    "options": [
                        {
                            "id": option.id,
                            "option_name": option.option_name,
                            "deduction_amount": cost_by_option_id[option.id],
                        }
                        for option in priced_options
                    ],
                }
            )
        return components

    def calculate(
        self, year: int, variant_id: uuid.UUID, repair_option_ids: list[uuid.UUID]
    ) -> ValuationResult:
        """
        FR-002-003..009.

        :raises PricingNotAvailableError: VAL003/E-PRICING-001 (BR-0005)
            if no Active ValuationMaster exists for Year+Variant.
        """
        valuation_master = self._valuation_master_repository.get_active_by_year_variant(
            year, variant_id
        )
        if valuation_master is None:
            raise PricingNotAvailableError(
                f"No Active ValuationMaster for Year={year}, Variant={variant_id}."
            )

        # IMP-003B Task 3: one batched query for every selected repair
        # option instead of one query per option (previously N+1 for an
        # N-option repair assessment).
        amounts_by_option_id = self._valuation_repair_cost_repository.get_amounts(
            valuation_master.id, repair_option_ids
        )
        total_repair_cost = sum(amounts_by_option_id.values(), Decimal("0"))

        # BR-0001: Purchase Price = MSP - Margin - Repair Cost
        purchase_price = (
            valuation_master.minimum_selling_price
            - valuation_master.margin
            - total_repair_cost
        )

        # BR-0002: floor at Scrap Value
        if purchase_price < valuation_master.scrap_value:
            purchase_price = valuation_master.scrap_value

        # BR-0009: round to nearest ₹10
        rounded_price = (purchase_price / 10).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        ) * 10

        label = self._recommendation_service.recommend(
            rounded_price, valuation_master.minimum_selling_price
        )

        return ValuationResult(
            recommended_price=purchase_price,
            rounded_price=rounded_price,
            label=label,
        )
