# Full Path: src/vehicle_master/tests/test_repositories_behavior.py
# Relative Path: tests/test_repositories_behavior.py
# Module: vehicle_master
# Purpose: Behavioral unit tests for the repository layer (CRUD paths,
#   ValuationMaster versioning + concurrency exception translation) -
#   distinct from test_repository_initialization.py, which covers shape
#   only. Added per the CTO review's Level 2 testing recommendation.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §3, DBD-001 §6a, BRR-001 BR-0007/BR-0011, TEST-001
from decimal import Decimal

from django.test import TestCase

from vehicle_master.exceptions import ConcurrencyConflictError
from vehicle_master.models import Brand, Model, Variant
from vehicle_master.repositories import (
    BrandRepository,
    ModelRepository,
    ValuationMasterRepository,
    VariantRepository,
)


class BrandRepositoryBehaviorTests(TestCase):
    def setUp(self):
        self.repository = BrandRepository()

    def test_get_active_excludes_inactive(self):
        active = Brand.objects.create(brand_name="Honda")
        Brand.objects.create(brand_name="Retired", active=False)
        self.assertEqual(self.repository.get_active(), [active])

    def test_get_by_id_returns_none_when_missing(self):
        import uuid

        self.assertIsNone(self.repository.get_by_id(uuid.uuid4()))

    def test_name_exists_true_for_active_match(self):
        Brand.objects.create(brand_name="Honda")
        self.assertTrue(self.repository.name_exists("Honda"))

    def test_name_exists_false_when_only_inactive_match(self):
        Brand.objects.create(brand_name="Honda", active=False)
        self.assertFalse(self.repository.name_exists("Honda"))

    def test_name_exists_excludes_given_id(self):
        brand = Brand.objects.create(brand_name="Honda")
        self.assertFalse(self.repository.name_exists("Honda", exclude_id=brand.id))

    def test_create_persists_row(self):
        brand = self.repository.create("Honda")
        self.assertTrue(Brand.objects.filter(id=brand.id, brand_name="Honda").exists())

    def test_update_changes_name(self):
        brand = Brand.objects.create(brand_name="Honda")
        self.repository.update(brand.id, "Honda Motors")
        brand.refresh_from_db()
        self.assertEqual(brand.brand_name, "Honda Motors")

    def test_deactivate_sets_active_false_without_deleting(self):
        brand = Brand.objects.create(brand_name="Honda")
        self.repository.deactivate(brand.id)
        brand.refresh_from_db()
        self.assertFalse(brand.active)


class ModelRepositoryBehaviorTests(TestCase):
    def setUp(self):
        self.repository = ModelRepository()
        self.brand = Brand.objects.create(brand_name="Honda")

    def test_get_active_by_brand_scopes_correctly(self):
        model = Model.objects.create(brand=self.brand, model_name="Activa")
        other_brand = Brand.objects.create(brand_name="Bajaj")
        Model.objects.create(brand=other_brand, model_name="Pulsar")
        self.assertEqual(self.repository.get_active_by_brand(self.brand.id), [model])

    def test_name_exists_scoped_per_brand(self):
        Model.objects.create(brand=self.brand, model_name="Activa")
        other_brand = Brand.objects.create(brand_name="Bajaj")
        self.assertFalse(self.repository.name_exists(other_brand.id, "Activa"))
        self.assertTrue(self.repository.name_exists(self.brand.id, "Activa"))


class VariantRepositoryBehaviorTests(TestCase):
    def setUp(self):
        self.repository = VariantRepository()
        brand = Brand.objects.create(brand_name="Honda")
        self.model = Model.objects.create(brand=brand, model_name="Activa")

    def test_get_active_by_model_scopes_correctly(self):
        variant = Variant.objects.create(model=self.model, variant_name="125 Standard")
        other_model = Model.objects.create(
            brand=self.model.brand, model_name="CB Shine"
        )
        Variant.objects.create(model=other_model, variant_name="Drum")
        self.assertEqual(self.repository.get_active_by_model(self.model.id), [variant])


class ValuationMasterRepositoryBehaviorTests(TestCase):
    def setUp(self):
        self.repository = ValuationMasterRepository()
        brand = Brand.objects.create(brand_name="Honda")
        model = Model.objects.create(brand=brand, model_name="Activa")
        self.variant = Variant.objects.create(model=model, variant_name="125 Standard")

    def test_create_new_version_first_version_has_no_prior_to_close(self):
        valuation_master = self.repository.create_new_version(
            year=2022,
            variant_id=self.variant.id,
            minimum_selling_price=Decimal("50000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            expected_previous_updated_at=None,
        )
        self.assertTrue(valuation_master.active)
        self.assertIsNone(valuation_master.effective_to)

    def test_create_new_version_with_none_token_when_active_row_exists_raises_conflict(self):
        """expected_previous_updated_at=None while a current Active row exists must be treated as a stale/missing token."""
        self.repository.create_new_version(
            year=2022,
            variant_id=self.variant.id,
            minimum_selling_price=Decimal("50000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            expected_previous_updated_at=None,
        )
        with self.assertRaises(ConcurrencyConflictError):
            self.repository.create_new_version(
                year=2022,
                variant_id=self.variant.id,
                minimum_selling_price=Decimal("51000.00"),
                margin=Decimal("5000.00"),
                scrap_value=Decimal("10000.00"),
                expected_previous_updated_at=None,
            )

    def test_get_version_history_returns_all_versions_newest_first(self):
        first = self.repository.create_new_version(
            year=2022,
            variant_id=self.variant.id,
            minimum_selling_price=Decimal("50000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            expected_previous_updated_at=None,
        )
        second = self.repository.create_new_version(
            year=2022,
            variant_id=self.variant.id,
            minimum_selling_price=Decimal("52000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            expected_previous_updated_at=first.updated_at,
        )
        history = self.repository.get_version_history(2022, self.variant.id)
        self.assertEqual([row.id for row in history], [second.id, first.id])

    def test_deactivate_sets_active_false(self):
        valuation_master = self.repository.create_new_version(
            year=2022,
            variant_id=self.variant.id,
            minimum_selling_price=Decimal("50000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            expected_previous_updated_at=None,
        )
        self.repository.deactivate(valuation_master.id)
        valuation_master.refresh_from_db()
        self.assertFalse(valuation_master.active)
