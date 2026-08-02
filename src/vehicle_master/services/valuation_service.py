# Full Path: src/vehicle_master/services/valuation_service.py
# Relative Path: services/valuation_service.py
# Module: vehicle_master
# Purpose: Orchestrates BR-0001 (formula), BR-0002 (scrap floor), BR-0009
#   (rounding) to compute a Purchase Price, then delegates to
#   RecommendationService for the label.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: BRR-001 BR-0001/BR-0002/BR-0005/BR-0009/BR-0010,
#   ISP-002 §4, EP-002, ENG-0002 (stateless, no idempotency key needed)
"""
``ValuationService`` - the core calculation engine. Stateless: no write
happens anywhere in this method (v1, per FS-002 §2/§12 - `valuation_
requests` stays inactive). Depends on `ValuationMasterRepository`
(reused from Vehicle Master, IMP-001A) and `RepairOptionRepository`
(new, this module).
"""

import uuid
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from vehicle_master.exceptions import PricingNotAvailableError
from vehicle_master.repositories import RepairOptionRepository, ValuationMasterRepository
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
        repair_option_repository: RepairOptionRepository,
        recommendation_service: RecommendationService,
    ) -> None:
        self._valuation_master_repository = valuation_master_repository
        self._repair_option_repository = repair_option_repository
        self._recommendation_service = recommendation_service

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

        total_repair_cost = Decimal("0")
        for repair_option_id in repair_option_ids:
            repair_option = self._repair_option_repository.get_by_id(repair_option_id)
            if repair_option is not None:
                total_repair_cost += repair_option.deduction_amount

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
