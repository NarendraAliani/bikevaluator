# Full Path: src/vehicle_master/tests/test_vehicle_catalog_service.py
# Relative Path: tests/test_vehicle_catalog_service.py
# Module: vehicle_master
# Purpose: Unit tests for VehicleCatalogService business logic.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §4.1, FS-001 §6/§19, BR-0005, TEST-001
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from vehicle_master.exceptions import (
    DeprecatedVariantError,
    PricingNotAvailableError,
    VariantMissingError,
    VehicleNotFoundError,
)
from vehicle_master.models import Brand, Model, ValuationMaster, Variant
from vehicle_master.repositories import (
    BrandRepository,
    ModelRepository,
    ValuationMasterRepository,
    VariantRepository,
)
from vehicle_master.services.vehicle_catalog_service import VehicleCatalogService


class VehicleCatalogServiceTests(TestCase):
    """
    Covers FR-001-001..005 and their error paths (VAL001/VAL002/VAL003,
    E-CATALOG-002, BR-0005).
    """

    def setUp(self):
        self.service = VehicleCatalogService(
            brand_repository=BrandRepository(),
            model_repository=ModelRepository(),
            variant_repository=VariantRepository(),
            valuation_master_repository=ValuationMasterRepository(),
        )
        self.brand = Brand.objects.create(brand_name="Honda")
        self.model = Model.objects.create(brand=self.brand, model_name="Activa")
        self.variant = Variant.objects.create(model=self.model, variant_name="125 Standard")

    # --- list_brands -----------------------------------------------------

    def test_list_brands_excludes_inactive(self):
        Brand.objects.create(brand_name="Discontinued", active=False)
        brands = self.service.list_brands()
        self.assertIn(self.brand, brands)
        self.assertEqual(len(brands), 1)

    # --- list_models -----------------------------------------------------

    def test_list_models_returns_active_models_for_brand(self):
        models = self.service.list_models(self.brand.id)
        self.assertEqual(list(models), [self.model])

    def test_list_models_raises_vehicle_not_found_for_unknown_brand(self):
        with self.assertRaises(VehicleNotFoundError):
            self.service.list_models(brand_id=self._random_uuid())

    # --- list_variants ---------------------------------------------------

    def test_list_variants_returns_active_variants_for_model(self):
        variants = self.service.list_variants(self.model.id)
        self.assertEqual(list(variants), [self.variant])

    def test_list_variants_raises_vehicle_not_found_for_unknown_model(self):
        with self.assertRaises(VehicleNotFoundError):
            self.service.list_variants(model_id=self._random_uuid())

    # --- get_configuration -------------------------------------------------

    def test_get_configuration_success(self):
        valuation_master = ValuationMaster.objects.create(
            year=2022,
            variant=self.variant,
            minimum_selling_price=Decimal("50000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            active=True,
            effective_from=timezone.now(),
        )
        configuration = self.service.get_configuration(
            year=2022,
            brand_id=self.brand.id,
            model_id=self.model.id,
            variant_id=self.variant.id,
        )
        self.assertEqual(configuration.valuation_master_id, valuation_master.id)
        self.assertEqual(configuration.minimum_selling_price, Decimal("50000.00"))
        self.assertEqual(configuration.repair_options, [])

    def test_get_configuration_raises_pricing_not_available_br_0005(self):
        """No ValuationMaster row exists at all -> VAL003/E-PRICING-001 (BR-0005)."""
        with self.assertRaises(PricingNotAvailableError):
            self.service.get_configuration(
                year=2022,
                brand_id=self.brand.id,
                model_id=self.model.id,
                variant_id=self.variant.id,
            )

    def test_get_configuration_raises_vehicle_not_found_for_unknown_brand(self):
        with self.assertRaises(VehicleNotFoundError):
            self.service.get_configuration(
                year=2022,
                brand_id=self._random_uuid(),
                model_id=self.model.id,
                variant_id=self.variant.id,
            )

    def test_get_configuration_raises_vehicle_not_found_when_model_not_under_brand(self):
        """Referential-consistency check (ISP-001 §1.4) - model exists but under a different Brand."""
        other_brand = Brand.objects.create(brand_name="Bajaj")
        other_model = Model.objects.create(brand=other_brand, model_name="Pulsar")
        with self.assertRaises(VehicleNotFoundError):
            self.service.get_configuration(
                year=2022,
                brand_id=self.brand.id,
                model_id=other_model.id,
                variant_id=self.variant.id,
            )

    def test_get_configuration_raises_variant_missing_for_unknown_variant(self):
        with self.assertRaises(VariantMissingError):
            self.service.get_configuration(
                year=2022,
                brand_id=self.brand.id,
                model_id=self.model.id,
                variant_id=self._random_uuid(),
            )

    def test_get_configuration_raises_deprecated_variant_error(self):
        """E-CATALOG-002: a deactivated Variant is blocked for new evaluations."""
        self.variant.active = False
        self.variant.save(update_fields=["active"])
        with self.assertRaises(DeprecatedVariantError):
            self.service.get_configuration(
                year=2022,
                brand_id=self.brand.id,
                model_id=self.model.id,
                variant_id=self.variant.id,
            )

    @staticmethod
    def _random_uuid():
        import uuid

        return uuid.uuid4()
