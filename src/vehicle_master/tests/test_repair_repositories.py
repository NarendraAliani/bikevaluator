# Full Path: src/vehicle_master/tests/test_repair_repositories.py
# Relative Path: tests/test_repair_repositories.py
# Module: vehicle_master
# Purpose: Unit tests for RepairComponent/RepairOption models and their
#   repositories - shape, behavior, and constraints.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: DBD-001 §2, BRR-001 BR-0010, ISP-002 §3, EP-002, TEST-001
from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase

from vehicle_master.models import RepairComponent, RepairOption
from vehicle_master.repositories import RepairComponentRepository, RepairOptionRepository


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

    def test_created_with_fixed_deduction(self):
        option = RepairOption.objects.create(
            repair_component=self.component,
            option_name="PARTIAL",
            deduction_amount=Decimal("500.00"),
        )
        self.assertEqual(option.deduction_amount, Decimal("500.00"))

    def test_negative_deduction_rejected_by_check_constraint(self):
        """BR-0010: deductions are fixed ₹ amounts, never negative - DB-level backstop."""
        with self.assertRaises(IntegrityError):
            RepairOption.objects.create(
                repair_component=self.component,
                option_name="FULL",
                deduction_amount=Decimal("-1.00"),
            )

    def test_restrict_on_delete_protects_component(self):
        RepairOption.objects.create(
            repair_component=self.component, option_name="OK", deduction_amount=Decimal("0")
        )
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
            repair_component=self.component,
            option_name="OK",
            deduction_amount=Decimal("0"),
        )
        other_component = RepairComponent.objects.create(name="Tyre")
        RepairOption.objects.create(
            repair_component=other_component,
            option_name="OK",
            deduction_amount=Decimal("0"),
        )
        self.assertEqual(
            self.repository.get_active_by_component(self.component.id), [option]
        )

    def test_get_active_by_component_excludes_inactive(self):
        RepairOption.objects.create(
            repair_component=self.component,
            option_name="FULL",
            deduction_amount=Decimal("1000.00"),
            active=False,
        )
        self.assertEqual(
            self.repository.get_active_by_component(self.component.id), []
        )
