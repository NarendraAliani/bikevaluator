# Full Path: src/vehicle_master/tests/test_valuation_views.py
# Relative Path: tests/test_valuation_views.py
# Module: vehicle_master
# Purpose: API integration tests for GET /repairs/components and
#   POST /valuation/calculate (HTTP -> Serializer -> Service -> Repository -> DB).
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: API-001, API-000 v1.1 (Response Envelope), ISP-002,
#   EP-002, IMP-003 (repairs/components now requires year/variant_id), TEST-001
from decimal import Decimal

from django.utils import timezone
from rest_framework.test import APITestCase

from vehicle_master.models import (
    Brand,
    Model,
    RepairComponent,
    RepairOption,
    ValuationMaster,
    ValuationRepairCost,
    Variant,
)

API_PREFIX = "/api/v1"


class RepairComponentListViewTests(APITestCase):
    def setUp(self):
        brand = Brand.objects.create(brand_name="Honda")
        model = Model.objects.create(brand=brand, model_name="Activa")
        self.variant = Variant.objects.create(model=model, variant_name="125 Standard")
        self.valuation_master = ValuationMaster.objects.create(
            year=2022,
            variant=self.variant,
            minimum_selling_price=Decimal("50000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("0.00"),
            active=True,
            effective_from=timezone.now(),
        )

    def _query(self, **overrides):
        query = {"year": 2022, "variant_id": str(self.variant.id)}
        query.update(overrides)
        return query

    def test_returns_active_components_with_vehicle_scoped_options(self):
        component = RepairComponent.objects.create(name="Engine")
        option = RepairOption.objects.create(repair_component=component, option_name="OK")
        ValuationRepairCost.objects.create(
            valuation_master=self.valuation_master, repair_option=option,
            deduction_amount=Decimal("0"),
        )
        response = self.client.get(f"{API_PREFIX}/repairs/components", self._query())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
        components = response.data["data"]["components"]
        self.assertEqual(len(components), 1)
        self.assertEqual(components[0]["name"], "Engine")
        self.assertEqual(components[0]["options"][0]["optionName"], "OK")

    def test_empty_catalog_returns_empty_list(self):
        response = self.client.get(f"{API_PREFIX}/repairs/components", self._query())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["components"], [])

    def test_missing_year_returns_400(self):
        response = self.client.get(
            f"{API_PREFIX}/repairs/components", {"variant_id": str(self.variant.id)}
        )
        self.assertEqual(response.status_code, 400)

    def test_no_pricing_returns_404_val003(self):
        response = self.client.get(
            f"{API_PREFIX}/repairs/components", self._query(year=2099)
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["errors"][0]["code"], "VAL003")


class ValuationCalculateViewTests(APITestCase):
    def setUp(self):
        brand = Brand.objects.create(brand_name="Honda")
        model = Model.objects.create(brand=brand, model_name="Activa")
        self.variant = Variant.objects.create(model=model, variant_name="125 Standard")
        self.component = RepairComponent.objects.create(name="Engine")
        self.option = RepairOption.objects.create(
            repair_component=self.component, option_name="PARTIAL"
        )

    def _payload(self, **overrides):
        payload = {
            "year": 2022,
            "variantId": str(self.variant.id),
            "repairAssessment": [
                {
                    "repairComponentId": str(self.component.id),
                    "repairOptionId": str(self.option.id),
                }
            ],
        }
        payload.update(overrides)
        return payload

    def _create_pricing_with_cost(self):
        valuation_master = ValuationMaster.objects.create(
            year=2022,
            variant=self.variant,
            minimum_selling_price=Decimal("50000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("0.00"),
            active=True,
            effective_from=timezone.now(),
        )
        ValuationRepairCost.objects.create(
            valuation_master=valuation_master, repair_option=self.option,
            deduction_amount=Decimal("3000.00"),
        )
        return valuation_master

    def test_success_returns_price_and_label_in_approved_envelope(self):
        self._create_pricing_with_cost()
        response = self.client.post(
            f"{API_PREFIX}/valuation/calculate", self._payload(), format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "Success")
        data = response.data["data"]
        self.assertEqual(data["recommendedPrice"], "42000.00")
        self.assertEqual(data["roundedPrice"], "42000")
        # 42000 / 50000 = 84% of MSP -> Good (BR-0003 band: 75-89%).
        self.assertEqual(data["label"], "GOOD")

    def test_no_pricing_returns_404_val003(self):
        response = self.client.post(
            f"{API_PREFIX}/valuation/calculate", self._payload(), format="json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["errors"][0]["code"], "VAL003")

    def test_missing_repair_assessment_returns_400(self):
        response = self.client.post(
            f"{API_PREFIX}/valuation/calculate",
            {"year": 2022, "variantId": str(self.variant.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["success"])

    def test_empty_repair_assessment_is_valid_no_repairs_needed(self):
        """An empty repairAssessment is legitimate input (vehicle needs no repairs), not an error."""
        self._create_pricing_with_cost()
        response = self.client.post(
            f"{API_PREFIX}/valuation/calculate",
            self._payload(repairAssessment=[]),
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["recommendedPrice"], "45000.00")

    def test_malformed_uuid_returns_400(self):
        response = self.client.post(
            f"{API_PREFIX}/valuation/calculate",
            self._payload(variantId="not-a-uuid"),
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_idempotent_retry_is_safe(self):
        """ENG-0002: stateless - retrying an identical request produces identical results, no error."""
        self._create_pricing_with_cost()
        first = self.client.post(
            f"{API_PREFIX}/valuation/calculate", self._payload(), format="json"
        )
        second = self.client.post(
            f"{API_PREFIX}/valuation/calculate", self._payload(), format="json"
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data["data"], second.data["data"])
