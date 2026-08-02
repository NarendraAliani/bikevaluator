# Full Path: src/vehicle_master/tests/test_catalog_views.py
# Relative Path: tests/test_catalog_views.py
# Module: vehicle_master
# Purpose: API integration tests for the Dealer-facing catalog endpoints
#   (HTTP -> Serializer -> Service -> Repository -> Database).
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: API-001 (Vehicle Master endpoints), API-000 v1.1
#   (Response Envelope), FS-001 §14/§19, TEST-001
from decimal import Decimal

from django.utils import timezone
from rest_framework.test import APITestCase

from vehicle_master.models import Brand, Model, ValuationMaster, Variant

API_PREFIX = "/api/v1"


class BrandListViewTests(APITestCase):
    def test_returns_only_active_brands_in_approved_envelope(self):
        Brand.objects.create(brand_name="Honda")
        Brand.objects.create(brand_name="Retired", active=False)

        response = self.client.get(f"{API_PREFIX}/vehicles/brands")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "Success")
        self.assertEqual(len(response.data["data"]["brands"]), 1)
        self.assertEqual(response.data["data"]["brands"][0]["brandName"], "Honda")

    def test_empty_catalog_returns_empty_list_not_error(self):
        response = self.client.get(f"{API_PREFIX}/vehicles/brands")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["brands"], [])


class ModelListViewTests(APITestCase):
    def setUp(self):
        self.brand = Brand.objects.create(brand_name="Honda")
        Model.objects.create(brand=self.brand, model_name="Activa")

    def test_returns_models_for_brand(self):
        response = self.client.get(
            f"{API_PREFIX}/vehicles/models", {"brand_id": str(self.brand.id)}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["data"]["models"]), 1)
        self.assertEqual(response.data["data"]["models"][0]["modelName"], "Activa")

    def test_missing_brand_id_returns_400_validation_error(self):
        response = self.client.get(f"{API_PREFIX}/vehicles/models")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["success"])

    def test_unknown_brand_id_returns_404_val001(self):
        import uuid

        response = self.client.get(
            f"{API_PREFIX}/vehicles/models", {"brand_id": str(uuid.uuid4())}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["errors"][0]["code"], "VAL001")


class VariantListViewTests(APITestCase):
    def setUp(self):
        brand = Brand.objects.create(brand_name="Honda")
        self.model = Model.objects.create(brand=brand, model_name="Activa")
        Variant.objects.create(model=self.model, variant_name="125 Standard")

    def test_returns_variants_for_model(self):
        response = self.client.get(
            f"{API_PREFIX}/vehicles/variants", {"model_id": str(self.model.id)}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["data"]["variants"]), 1)


class ConfigurationViewTests(APITestCase):
    def setUp(self):
        self.brand = Brand.objects.create(brand_name="Honda")
        self.model = Model.objects.create(brand=self.brand, model_name="Activa")
        self.variant = Variant.objects.create(model=self.model, variant_name="125 Standard")

    def _query(self, year=2022, brand_id=None, model_id=None, variant_id=None):
        return {
            "year": year,
            "brand_id": str(brand_id or self.brand.id),
            "model_id": str(model_id or self.model.id),
            "variant_id": str(variant_id or self.variant.id),
        }

    def test_success_returns_pricing_and_empty_repair_options(self):
        ValuationMaster.objects.create(
            year=2022,
            variant=self.variant,
            minimum_selling_price=Decimal("50000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            active=True,
            effective_from=timezone.now(),
        )
        response = self.client.get(f"{API_PREFIX}/vehicles/configuration", self._query())
        self.assertEqual(response.status_code, 200)
        data = response.data["data"]
        self.assertEqual(data["minimumSellingPrice"], "50000.00")
        self.assertEqual(data["repairOptions"], [])  # never fabricated

    def test_no_pricing_returns_404_val003(self):
        response = self.client.get(f"{API_PREFIX}/vehicles/configuration", self._query())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["errors"][0]["code"], "VAL003")

    def test_year_has_no_filtering_effect_on_brand_list(self):
        """ARC-0005: `year` on catalog list endpoints has no effect - proven on /vehicles/brands here."""
        Brand.objects.create(brand_name="Honda2")
        without_year = self.client.get(f"{API_PREFIX}/vehicles/brands")
        with_year = self.client.get(f"{API_PREFIX}/vehicles/brands", {"year": 1999})
        self.assertEqual(without_year.data["data"], with_year.data["data"])

    def test_deprecated_variant_returns_409_catalog_002(self):
        self.variant.active = False
        self.variant.save(update_fields=["active"])
        response = self.client.get(f"{API_PREFIX}/vehicles/configuration", self._query())
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data["errors"][0]["code"], "E-CATALOG-002")

    def test_variant_not_under_model_returns_404_val002(self):
        import uuid

        response = self.client.get(
            f"{API_PREFIX}/vehicles/configuration", self._query(variant_id=uuid.uuid4())
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["errors"][0]["code"], "VAL002")
