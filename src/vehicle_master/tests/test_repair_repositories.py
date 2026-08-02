# Full Path: src/vehicle_master/tests/test_repair_repositories.py
# Relative Path: tests/test_repair_repositories.py
# Module: vehicle_master
# Purpose: Unit tests for RepairComponent/RepairOption/ValuationRepairCost
#   models and their repositories - shape, behavior, and constraints.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: DBD-001 §2, BRR-001 BR-0010, ISP-002 §3, EP-002,
#   IMP-003 (ValuationRepairCost - deduction amounts scoped per vehicle), TEST-001
from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

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
    RepairOptionRepository,
    ValuationRepairCostRepository,
)


class RepairComponentModelTests(TestCase):
    def test_created_with_uuid_pk_and_active_default(self):
        component = RepairComponent.objects.create(name="Engine")
        self.assertTrue(component.active)

    def test_str_returns_name(self):
        component = RepairComponent.objects.create(name="Gearbox")
        self.assertEqual(str(component), "Gearbox")


class RepairOptionModelTests(TestCase):
    def setUp(self):
        self.component = RepairComponent.objects.create(name="Engine")

    def test_created_as_pure_catalog_entry(self):
        """IMP-003: RepairOption no longer carries a deduction_amount - pure catalog identity."""
        option = RepairOption.objects.create(
            repair_component=self.component, option_name="PARTIAL"
        )
        self.assertFalse(hasattr(option, "deduction_amount"))

    def test_restrict_on_delete_protects_component(self):
        RepairOption.objects.create(repair_component=self.component, option_name="OK")
        with self.assertRaises(IntegrityError):
            self.component.delete()


class RepairComponentRepositoryTests(TestCase):
    def setUp(self):
        self.repository = RepairComponentRepository()

    def test_get_active_excludes_inactive(self):
        active = RepairComponent.objects.create(name="Engine")
        RepairComponent.objects.create(name="Retired", active=False)
        self.assertEqual(self.repository.get_active(), [active])

    def test_get_by_id_returns_none_when_missing(self):
        import uuid

        self.assertIsNone(self.repository.get_by_id(uuid.uuid4()))


class RepairOptionRepositoryTests(TestCase):
    def setUp(self):
        self.repository = RepairOptionRepository()
        self.component = RepairComponent.objects.create(name="Engine")

    def test_get_active_by_component_scopes_correctly(self):
        option = RepairOption.objects.create(
            repair_component=self.component, option_name="OK"
        )
        other_component = RepairComponent.objects.create(name="Tyre")
        RepairOption.objects.create(repair_component=other_component, option_name="OK")
        self.assertEqual(
            self.repository.get_active_by_component(self.component.id), [option]
        )

    def test_get_active_by_component_excludes_inactive(self):
        RepairOption.objects.create(
            repair_component=self.component, option_name="FULL", active=False
        )
        self.assertEqual(
            self.repository.get_active_by_component(self.component.id), []
        )


class ValuationRepairCostModelAndRepositoryTests(TestCase):
    """IMP-003: repair deduction amounts are scoped per ValuationMaster (vehicle+year)."""

    def setUp(self):
        brand = Brand.objects.create(brand_name="Honda")
        model = Model.objects.create(brand=brand, model_name="Activa")
        self.variant = Variant.objects.create(model=model, variant_name="125 Standard")
        self.valuation_master = ValuationMaster.objects.create(
            year=2022,
            variant=self.variant,
            minimum_selling_price=Decimal("50000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            active=True,
            effective_from=timezone.now(),
        )
        self.component = RepairComponent.objects.create(name="Engine")
        self.option = RepairOption.objects.create(
            repair_component=self.component, option_name="PARTIAL"
        )
        self.repository = ValuationRepairCostRepository()

    def test_negative_deduction_rejected_by_check_constraint(self):
        """BR-0010: deductions are fixed Rs. amounts, never negative - DB-level backstop."""
        with self.assertRaises(IntegrityError):
            ValuationRepairCost.objects.create(
                valuation_master=self.valuation_master,
                repair_option=self.option,
                deduction_amount=Decimal("-1.00"),
            )

    def test_unique_together_valuation_master_and_option(self):
        ValuationRepairCost.objects.create(
            valuation_master=self.valuation_master,
            repair_option=self.option,
            deduction_amount=Decimal("3000.00"),
        )
        with self.assertRaises(IntegrityError):
            ValuationRepairCost.objects.create(
                valuation_master=self.valuation_master,
                repair_option=self.option,
                deduction_amount=Decimal("4000.00"),
            )

    def test_get_amount_returns_none_when_no_cost_row(self):
        self.assertIsNone(
            self.repository.get_amount(self.valuation_master.id, self.option.id)
        )

    def test_get_amount_returns_the_scoped_value(self):
        ValuationRepairCost.objects.create(
            valuation_master=self.valuation_master,
            repair_option=self.option,
            deduction_amount=Decimal("3000.00"),
        )
        self.assertEqual(
            self.repository.get_amount(self.valuation_master.id, self.option.id),
            Decimal("3000.00"),
        )

    def test_upsert_is_idempotent(self):
        self.repository.upsert(self.valuation_master.id, self.option.id, Decimal("3000.00"))
        self.repository.upsert(self.valuation_master.id, self.option.id, Decimal("3500.00"))
        self.assertEqual(ValuationRepairCost.objects.count(), 1)
        self.assertEqual(
            self.repository.get_amount(self.valuation_master.id, self.option.id),
            Decimal("3500.00"),
        )

    def test_get_by_valuation_master_returns_all_scoped_rows(self):
        other_option = RepairOption.objects.create(
            repair_component=self.component, option_name="FULL"
        )
        ValuationRepairCost.objects.create(
            valuation_master=self.valuation_master,
            repair_option=self.option,
            deduction_amount=Decimal("3000.00"),
        )
        ValuationRepairCost.objects.create(
            valuation_master=self.valuation_master,
            repair_option=other_option,
            deduction_amount=Decimal("8000.00"),
        )
        rows = self.repository.get_by_valuation_master(self.valuation_master.id)
        self.assertEqual(len(rows), 2)
