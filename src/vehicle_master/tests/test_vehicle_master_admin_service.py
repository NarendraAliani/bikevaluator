# Full Path: src/vehicle_master/tests/test_vehicle_master_admin_service.py
# Relative Path: tests/test_vehicle_master_admin_service.py
# Module: vehicle_master
# Purpose: Unit tests for VehicleMasterAdminService business logic -
#   BR-0004 authorization, duplicate detection (BR-0011/E-CATALOG-001),
#   BR-0007 versioning, ENG-0003 optimistic concurrency, audit logging.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §4.2, BRR-001 BR-0004/BR-0007/BR-0011,
#   DBD-001 §6a, TEST-001
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from vehicle_master.exceptions import (
    ConcurrencyConflictError,
    DuplicateCatalogEntryError,
    NotAuthorizedError,
    VehicleNotFoundError,
)
from vehicle_master.models import Brand, Model, ValuationMaster, Variant
from vehicle_master.repositories import (
    BrandRepository,
    ModelRepository,
    ValuationMasterRepository,
    VariantRepository,
)
from vehicle_master.services.vehicle_master_admin_service import (
    VehicleMasterAdminService,
)
from vehicle_master.tests.fixtures import (
    FakeAuditLogRepository,
    make_dealer_actor,
    make_super_admin_actor,
)

TEST_IP = "203.0.113.1"


class VehicleMasterAdminServiceTestCase(TestCase):
    def setUp(self):
        self.audit_repository = FakeAuditLogRepository()
        self.service = VehicleMasterAdminService(
            brand_repository=BrandRepository(),
            model_repository=ModelRepository(),
            variant_repository=VariantRepository(),
            valuation_master_repository=ValuationMasterRepository(),
            audit_log_repository=self.audit_repository,
        )
        self.super_admin = make_super_admin_actor()
        self.dealer = make_dealer_actor()


class CreateBrandTests(VehicleMasterAdminServiceTestCase):
    def test_success_creates_brand_and_writes_audit_entry(self):
        brand = self.service.create_brand("Honda", self.super_admin, TEST_IP)
        self.assertEqual(brand.brand_name, "Honda")
        self.assertEqual(len(self.audit_repository.entries), 1)
        entry = self.audit_repository.entries[0]
        self.assertEqual(entry["entity_type"], "Brand")
        self.assertEqual(entry["actor_id"], self.super_admin.id)
        self.assertIsNone(entry["old_value"])
        self.assertEqual(entry["ip_address"], TEST_IP)

    def test_rejects_non_super_admin(self):
        """BR-0004 / E-AUTHZ-001."""
        with self.assertRaises(NotAuthorizedError):
            self.service.create_brand("Honda", self.dealer, TEST_IP)
        self.assertEqual(len(self.audit_repository.entries), 0)

    def test_rejects_duplicate_active_name(self):
        """BR-0011's sibling duplicate-detection rule / E-CATALOG-001."""
        Brand.objects.create(brand_name="Honda")
        with self.assertRaises(DuplicateCatalogEntryError):
            self.service.create_brand("Honda", self.super_admin, TEST_IP)

    def test_allows_name_reuse_after_original_deactivated(self):
        """Duplicate check is scoped to active=True rows only."""
        Brand.objects.create(brand_name="Honda", active=False)
        brand = self.service.create_brand("Honda", self.super_admin, TEST_IP)
        self.assertEqual(brand.brand_name, "Honda")

    def test_rejects_empty_name(self):
        with self.assertRaises(ValidationError):
            self.service.create_brand("", self.super_admin, TEST_IP)


class UpdateAndDeactivateBrandTests(VehicleMasterAdminServiceTestCase):
    def setUp(self):
        super().setUp()
        self.brand = Brand.objects.create(brand_name="Honda")

    def test_update_success(self):
        updated = self.service.update_brand(
            self.brand.id, "Honda Motors", self.super_admin, TEST_IP
        )
        self.assertEqual(updated.brand_name, "Honda Motors")
        entry = self.audit_repository.entries[0]
        self.assertEqual(entry["old_value"], {"brand_name": "Honda"})
        self.assertEqual(entry["new_value"], {"brand_name": "Honda Motors"})

    def test_update_raises_not_found_for_unknown_brand(self):
        import uuid

        with self.assertRaises(VehicleNotFoundError):
            self.service.update_brand(uuid.uuid4(), "X", self.super_admin, TEST_IP)

    def test_update_rejects_non_super_admin(self):
        with self.assertRaises(NotAuthorizedError):
            self.service.update_brand(self.brand.id, "X", self.dealer, TEST_IP)

    def test_deactivate_success(self):
        self.service.deactivate_brand(self.brand.id, self.super_admin, TEST_IP)
        self.brand.refresh_from_db()
        self.assertFalse(self.brand.active)
        entry = self.audit_repository.entries[0]
        self.assertEqual(entry["new_value"], {"active": False})

    def test_deactivate_rejects_non_super_admin(self):
        with self.assertRaises(NotAuthorizedError):
            self.service.deactivate_brand(self.brand.id, self.dealer, TEST_IP)


class ModelAndVariantAdminTests(VehicleMasterAdminServiceTestCase):
    """
    Model/Variant follow the identical pattern as Brand - one
    representative test per concern each, to avoid redundant coverage
    of the same code shape already fully exercised above.
    """

    def setUp(self):
        super().setUp()
        self.brand = Brand.objects.create(brand_name="Honda")
        self.model = Model.objects.create(brand=self.brand, model_name="Activa")

    def test_create_model_success(self):
        model = self.service.create_model(self.brand.id, "CB Shine", self.super_admin, TEST_IP)
        self.assertEqual(model.brand_id, self.brand.id)

    def test_create_model_rejects_duplicate_under_same_brand(self):
        with self.assertRaises(DuplicateCatalogEntryError):
            self.service.create_model(self.brand.id, "Activa", self.super_admin, TEST_IP)

    def test_create_model_allows_same_name_under_different_brand(self):
        other_brand = Brand.objects.create(brand_name="Bajaj")
        model = self.service.create_model(other_brand.id, "Activa", self.super_admin, TEST_IP)
        self.assertEqual(model.model_name, "Activa")

    def test_create_model_raises_not_found_for_unknown_brand(self):
        import uuid

        with self.assertRaises(VehicleNotFoundError):
            self.service.create_model(uuid.uuid4(), "X", self.super_admin, TEST_IP)

    def test_create_variant_success(self):
        variant = self.service.create_variant(
            self.model.id, "125 Disc", self.super_admin, TEST_IP
        )
        self.assertEqual(variant.model_id, self.model.id)

    def test_create_variant_rejects_duplicate_under_same_model(self):
        Variant.objects.create(model=self.model, variant_name="125 Standard")
        with self.assertRaises(DuplicateCatalogEntryError):
            self.service.create_variant(
                self.model.id, "125 Standard", self.super_admin, TEST_IP
            )

    def test_deactivate_variant_success(self):
        variant = Variant.objects.create(model=self.model, variant_name="125 Standard")
        self.service.deactivate_variant(variant.id, self.super_admin, TEST_IP)
        variant.refresh_from_db()
        self.assertFalse(variant.active)


class CreateValuationMasterVersionTests(VehicleMasterAdminServiceTestCase):
    def setUp(self):
        super().setUp()
        self.brand = Brand.objects.create(brand_name="Honda")
        self.model = Model.objects.create(brand=self.brand, model_name="Activa")
        self.variant = Variant.objects.create(model=self.model, variant_name="125 Standard")

    def test_first_version_success(self):
        """No prior Active row -> expected_previous_updated_at=None is valid."""
        valuation_master = self.service.create_valuation_master_version(
            year=2022,
            variant_id=self.variant.id,
            minimum_selling_price=Decimal("50000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            expected_previous_updated_at=None,
            actor=self.super_admin,
            ip_address=TEST_IP,
        )
        self.assertTrue(valuation_master.active)
        self.assertEqual(len(self.audit_repository.entries), 1)

    def test_br_0007_new_version_closes_prior_active_row(self):
        first = self.service.create_valuation_master_version(
            year=2022,
            variant_id=self.variant.id,
            minimum_selling_price=Decimal("50000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            expected_previous_updated_at=None,
            actor=self.super_admin,
            ip_address=TEST_IP,
        )
        second = self.service.create_valuation_master_version(
            year=2022,
            variant_id=self.variant.id,
            minimum_selling_price=Decimal("52000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            expected_previous_updated_at=first.updated_at,
            actor=self.super_admin,
            ip_address=TEST_IP,
        )
        first.refresh_from_db()
        self.assertFalse(first.active)
        self.assertIsNotNone(first.effective_to)
        self.assertTrue(second.active)
        self.assertEqual(
            ValuationMaster.objects.filter(year=2022, variant=self.variant).count(), 2
        )

    def test_eng_0003_rejects_stale_concurrency_token(self):
        first = self.service.create_valuation_master_version(
            year=2022,
            variant_id=self.variant.id,
            minimum_selling_price=Decimal("50000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            expected_previous_updated_at=None,
            actor=self.super_admin,
            ip_address=TEST_IP,
        )
        stale_token = first.updated_at
        # Someone else updates it first, advancing updated_at...
        self.service.create_valuation_master_version(
            year=2022,
            variant_id=self.variant.id,
            minimum_selling_price=Decimal("51000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            expected_previous_updated_at=stale_token,
            actor=self.super_admin,
            ip_address=TEST_IP,
        )
        # ...then our caller retries with the now-stale token.
        with self.assertRaises(ConcurrencyConflictError):
            self.service.create_valuation_master_version(
                year=2022,
                variant_id=self.variant.id,
                minimum_selling_price=Decimal("53000.00"),
                margin=Decimal("5000.00"),
                scrap_value=Decimal("10000.00"),
                expected_previous_updated_at=stale_token,
                actor=self.super_admin,
                ip_address=TEST_IP,
            )

    def test_rejects_negative_amount(self):
        with self.assertRaises(ValidationError):
            self.service.create_valuation_master_version(
                year=2022,
                variant_id=self.variant.id,
                minimum_selling_price=Decimal("-1.00"),
                margin=Decimal("5000.00"),
                scrap_value=Decimal("10000.00"),
                expected_previous_updated_at=None,
                actor=self.super_admin,
                ip_address=TEST_IP,
            )

    def test_rejects_non_super_admin(self):
        with self.assertRaises(NotAuthorizedError):
            self.service.create_valuation_master_version(
                year=2022,
                variant_id=self.variant.id,
                minimum_selling_price=Decimal("50000.00"),
                margin=Decimal("5000.00"),
                scrap_value=Decimal("10000.00"),
                expected_previous_updated_at=None,
                actor=self.dealer,
                ip_address=TEST_IP,
            )

    def test_rejects_unknown_variant(self):
        import uuid

        with self.assertRaises(VehicleNotFoundError):
            self.service.create_valuation_master_version(
                year=2022,
                variant_id=uuid.uuid4(),
                minimum_selling_price=Decimal("50000.00"),
                margin=Decimal("5000.00"),
                scrap_value=Decimal("10000.00"),
                expected_previous_updated_at=None,
                actor=self.super_admin,
                ip_address=TEST_IP,
            )

    def test_deactivate_valuation_master_success(self):
        valuation_master = self.service.create_valuation_master_version(
            year=2022,
            variant_id=self.variant.id,
            minimum_selling_price=Decimal("50000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            expected_previous_updated_at=None,
            actor=self.super_admin,
            ip_address=TEST_IP,
        )
        self.service.deactivate_valuation_master(
            valuation_master.id, self.super_admin, TEST_IP
        )
        valuation_master.refresh_from_db()
        self.assertFalse(valuation_master.active)
