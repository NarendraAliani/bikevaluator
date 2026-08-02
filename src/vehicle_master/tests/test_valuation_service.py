# Full Path: src/vehicle_master/tests/test_valuation_service.py
# Relative Path: tests/test_valuation_service.py
# Module: vehicle_master
# Purpose: Unit tests for ValuationService - BR-0001 formula, BR-0002
#   scrap floor, BR-0009 rounding, BR-0005 (no pricing).
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: BRR-001 BR-0001/BR-0002/BR-0005/BR-0009/BR-0010,
#   ISP-002 §4, EP-002, TEST-001
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from vehicle_master.exceptions import PricingNotAvailableError
from vehicle_master.models import Brand, Model, RepairComponent, RepairOption, ValuationMaster, Variant
from vehicle_master.repositories import RepairOptionRepository, ValuationMasterRepository
from vehicle_master.services.recommendation_service import RecommendationService
from vehicle_master.services.valuation_service import ValuationService


class ValuationServiceTests(TestCase):
    def setUp(self):
        self.service = ValuationService(
            valuation_master_repository=ValuationMasterRepository(),
            repair_option_repository=RepairOptionRepository(),
            recommendation_service=RecommendationService(),
        )
        brand = Brand.objects.create(brand_name="Honda")
        model = Model.objects.create(brand=brand, model_name="Activa")
        self.variant = Variant.objects.create(model=model, variant_name="125 Standard")

    def _create_pricing(self, msp="50000.00", margin="5000.00", scrap="10000.00", year=2022):
        return ValuationMaster.objects.create(
            year=year,
            variant=self.variant,
            minimum_selling_price=Decimal(msp),
            margin=Decimal(margin),
            scrap_value=Decimal(scrap),
            active=True,
            effective_from=timezone.now(),
        )

    def test_br_0001_formula_no_repair_deductions(self):
        """AC-002-001: MSP=50000, Margin=5000, no deductions -> 45000."""
        self._create_pricing()
        result = self.service.calculate(2022, self.variant.id, [])
        self.assertEqual(result.recommended_price, Decimal("45000.00"))

    def test_br_0001_formula_with_repair_deductions(self):
        component = RepairComponent.objects.create(name="Engine")
        option = RepairOption.objects.create(
            repair_component=component, option_name="PARTIAL", deduction_amount=Decimal("3000.00")
        )
        self._create_pricing()
        result = self.service.calculate(2022, self.variant.id, [option.id])
        # 50000 - 5000 - 3000 = 42000
        self.assertEqual(result.recommended_price, Decimal("42000.00"))

    def test_br_0002_scrap_floor_applies(self):
        """AC-002-002: heavy deductions push price below Scrap Value - floors at Scrap Value."""
        component = RepairComponent.objects.create(name="Engine")
        option = RepairOption.objects.create(
            repair_component=component, option_name="FULL", deduction_amount=Decimal("40000.00")
        )
        self._create_pricing(msp="50000.00", margin="5000.00", scrap="10000.00")
        # 50000 - 5000 - 40000 = 5000, below scrap_value=10000 -> floors to 10000
        result = self.service.calculate(2022, self.variant.id, [option.id])
        self.assertEqual(result.recommended_price, Decimal("10000.00"))
        self.assertEqual(result.rounded_price, Decimal("10000"))

    def test_br_0009_rounds_to_nearest_10(self):
        """AC-002-003: 42003 rounds to 42000."""
        self._create_pricing(msp="50003.00", margin="5000.00", scrap="0.00")
        result = self.service.calculate(2022, self.variant.id, [])
        self.assertEqual(result.recommended_price, Decimal("45003.00"))
        self.assertEqual(result.rounded_price, Decimal("45000"))

    def test_br_0009_rounds_half_up(self):
        self._create_pricing(msp="50005.00", margin="0.00", scrap="0.00")
        result = self.service.calculate(2022, self.variant.id, [])
        self.assertEqual(result.rounded_price, Decimal("50010"))

    def test_recommendation_label_included(self):
        """AC-002-004: 45000/50000 = 90% -> Excellent."""
        self._create_pricing(msp="50000.00", margin="5000.00", scrap="0.00")
        result = self.service.calculate(2022, self.variant.id, [])
        self.assertEqual(result.label, "EXCELLENT")

    def test_br_0005_raises_pricing_not_available_when_no_active_valuation_master(self):
        """AC-002-005: no Active ValuationMaster -> PricingNotAvailableError, no partial result."""
        with self.assertRaises(PricingNotAvailableError):
            self.service.calculate(2022, self.variant.id, [])

    def test_unknown_repair_option_id_silently_ignored_not_erroring(self):
        """A repair_option_id that doesn't resolve contributes 0 - no crash."""
        import uuid

        self._create_pricing(msp="50000.00", margin="5000.00", scrap="0.00")
        result = self.service.calculate(2022, self.variant.id, [uuid.uuid4()])
        self.assertEqual(result.recommended_price, Decimal("45000.00"))

    def test_stateless_no_row_written_anywhere(self):
        """FR-002-012: v1 is stateless - calculate() must not create any new row."""
        self._create_pricing()
        before = ValuationMaster.objects.count()
        self.service.calculate(2022, self.variant.id, [])
        after = ValuationMaster.objects.count()
        self.assertEqual(before, after)
