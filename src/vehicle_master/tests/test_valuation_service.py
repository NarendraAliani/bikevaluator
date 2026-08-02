# Full Path: src/vehicle_master/tests/test_valuation_service.py
# Relative Path: tests/test_valuation_service.py
# Module: vehicle_master
# Purpose: Unit tests for ValuationService - BR-0001 formula, BR-0002
#   scrap floor, BR-0009 rounding, BR-0005 (no pricing), and IMP-003's
#   vehicle-scoped repair cost lookup + list_repair_components.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: BRR-001 BR-0001/BR-0002/BR-0005/BR-0009/BR-0010,
#   ISP-002 §4, EP-002, IMP-003, TEST-001
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from vehicle_master.exceptions import PricingNotAvailableError
from vehicle_master.models import (
    Brand,
    Model,
    RepairComponent,
    RepairOption,
    ValuationMaster,
    ValuationRepairCost,
    Variant,
)
from vehicle_master.repositories import (
    RepairComponentRepository,
    ValuationMasterRepository,
    ValuationRepairCostRepository,
)
from vehicle_master.services.recommendation_service import RecommendationService
from vehicle_master.services.valuation_service import ValuationService


class ValuationServiceTests(TestCase):
    def setUp(self):
        self.service = ValuationService(
            valuation_master_repository=ValuationMasterRepository(),
            repair_component_repository=RepairComponentRepository(),
            valuation_repair_cost_repository=ValuationRepairCostRepository(),
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
        valuation_master = self._create_pricing()
        component = RepairComponent.objects.create(name="Engine")
        option = RepairOption.objects.create(repair_component=component, option_name="PARTIAL")
        ValuationRepairCost.objects.create(
            valuation_master=valuation_master, repair_option=option,
            deduction_amount=Decimal("3000.00"),
        )
        result = self.service.calculate(2022, self.variant.id, [option.id])
        # 50000 - 5000 - 3000 = 42000
        self.assertEqual(result.recommended_price, Decimal("42000.00"))

    def test_br_0002_scrap_floor_applies(self):
        """AC-002-002: heavy deductions push price below Scrap Value - floors at Scrap Value."""
        valuation_master = self._create_pricing(msp="50000.00", margin="5000.00", scrap="10000.00")
        component = RepairComponent.objects.create(name="Engine")
        option = RepairOption.objects.create(repair_component=component, option_name="FULL")
        ValuationRepairCost.objects.create(
            valuation_master=valuation_master, repair_option=option,
            deduction_amount=Decimal("40000.00"),
        )
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
        """A repair_option_id with no cost row for this vehicle contributes 0 - no crash."""
        import uuid

        self._create_pricing(msp="50000.00", margin="5000.00", scrap="0.00")
        result = self.service.calculate(2022, self.variant.id, [uuid.uuid4()])
        self.assertEqual(result.recommended_price, Decimal("45000.00"))

    def test_repair_cost_is_scoped_per_vehicle_not_global(self):
        """IMP-003: the same RepairOption can cost different amounts for different vehicles."""
        other_model = Model.objects.create(brand=self.variant.model.brand, model_name="Shine")
        other_variant = Variant.objects.create(model=other_model, variant_name="BS6")
        valuation_master_a = self._create_pricing(msp="50000.00", margin="5000.00", scrap="0.00")
        valuation_master_b = ValuationMaster.objects.create(
            year=2022, variant=other_variant, minimum_selling_price=Decimal("60000.00"),
            margin=Decimal("5000.00"), scrap_value=Decimal("0.00"), active=True,
            effective_from=timezone.now(),
        )
        component = RepairComponent.objects.create(name="Engine")
        option = RepairOption.objects.create(repair_component=component, option_name="FULL")
        ValuationRepairCost.objects.create(
            valuation_master=valuation_master_a, repair_option=option,
            deduction_amount=Decimal("5000.00"),
        )
        ValuationRepairCost.objects.create(
            valuation_master=valuation_master_b, repair_option=option,
            deduction_amount=Decimal("8000.00"),
        )
        result_a = self.service.calculate(2022, self.variant.id, [option.id])
        result_b = self.service.calculate(2022, other_variant.id, [option.id])
        self.assertEqual(result_a.recommended_price, Decimal("40000.00"))  # 50000-5000-5000
        self.assertEqual(result_b.recommended_price, Decimal("47000.00"))  # 60000-5000-8000

    def test_stateless_no_row_written_anywhere(self):
        """FR-002-012: v1 is stateless - calculate() must not create any new ValuationMaster row."""
        self._create_pricing()
        before = ValuationMaster.objects.count()
        self.service.calculate(2022, self.variant.id, [])
        after = ValuationMaster.objects.count()
        self.assertEqual(before, after)

    def test_calculate_query_count_does_not_scale_with_selected_option_count(self):
        """
        IMP-003B Task 3 regression guard: before the fix, calculate()
        issued 1 query per selected repair option (N+1). With the
        batched `get_amounts` fix, the query count must stay fixed
        regardless of how many options are in the assessment.
        """
        valuation_master = self._create_pricing()
        component = RepairComponent.objects.create(name="Engine")
        option_ids = []
        for i in range(5):
            option = RepairOption.objects.create(repair_component=component, option_name=f"OPT{i}"[:10])
            ValuationRepairCost.objects.create(
                valuation_master=valuation_master, repair_option=option,
                deduction_amount=Decimal("100.00"),
            )
            option_ids.append(option.id)
        # 1 (ValuationMaster) + 1 (batched amounts) = 2, regardless of len(option_ids)
        with self.assertNumQueries(2):
            self.service.calculate(2022, self.variant.id, option_ids)


class ListRepairComponentsTests(TestCase):
    def setUp(self):
        self.service = ValuationService(
            valuation_master_repository=ValuationMasterRepository(),
            repair_component_repository=RepairComponentRepository(),
            valuation_repair_cost_repository=ValuationRepairCostRepository(),
            recommendation_service=RecommendationService(),
        )
        brand = Brand.objects.create(brand_name="Honda")
        model = Model.objects.create(brand=brand, model_name="Activa")
        self.variant = Variant.objects.create(model=model, variant_name="125 Standard")
        self.valuation_master = ValuationMaster.objects.create(
            year=2022, variant=self.variant, minimum_selling_price=Decimal("50000.00"),
            margin=Decimal("5000.00"), scrap_value=Decimal("0.00"), active=True,
            effective_from=timezone.now(),
        )

    def test_raises_pricing_not_available_when_no_active_valuation_master(self):
        with self.assertRaises(PricingNotAvailableError):
            self.service.list_repair_components(2099, self.variant.id)

    def test_only_returns_options_with_a_cost_row_for_this_vehicle(self):
        component = RepairComponent.objects.create(name="Engine")
        priced_option = RepairOption.objects.create(repair_component=component, option_name="PARTIAL")
        unpriced_option = RepairOption.objects.create(repair_component=component, option_name="FULL")
        ValuationRepairCost.objects.create(
            valuation_master=self.valuation_master, repair_option=priced_option,
            deduction_amount=Decimal("3000.00"),
        )
        components = self.service.list_repair_components(2022, self.variant.id)
        self.assertEqual(len(components), 1)
        option_ids = [o["id"] for o in components[0]["options"]]
        self.assertIn(priced_option.id, option_ids)
        self.assertNotIn(unpriced_option.id, option_ids)

    def test_list_repair_components_query_count_does_not_scale_with_component_count(self):
        """
        IMP-003B Task 3 regression guard: before the fix, this method
        issued 1 query for the ValuationMaster, 1 for its repair costs,
        then 1 MORE per RepairComponent (N+1). With the batched
        `get_active_by_components` fix, the query count must stay fixed
        regardless of how many components exist.
        """
        for i in range(5):
            component = RepairComponent.objects.create(name=f"Component{i}")
            option = RepairOption.objects.create(repair_component=component, option_name="FULL")
            ValuationRepairCost.objects.create(
                valuation_master=self.valuation_master, repair_option=option,
                deduction_amount=Decimal("1000.00"),
            )
        # 1 (ValuationMaster) + 1 (repair costs) + 1 (components) + 1 (options, batched) = 4
        with self.assertNumQueries(4):
            self.service.list_repair_components(2022, self.variant.id)
