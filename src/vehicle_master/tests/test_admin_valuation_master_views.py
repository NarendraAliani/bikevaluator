# Full Path: src/vehicle_master/tests/test_admin_valuation_master_views.py
# Relative Path: tests/test_admin_valuation_master_views.py
# Module: vehicle_master
# Purpose: API integration tests for /admin/valuation-master - success,
#   BR-0007 versioning, BR-0011 duplicate, ENG-0003 concurrency,
#   validation, and authorization paths.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: API-001 (/admin/valuation-master), BRR-001
#   BR-0007/BR-0011, DBD-001 §6a, TEST-001
import uuid

from rest_framework.test import APITestCase

from vehicle_master.models import Brand, Model, ValuationMaster, Variant

API_PREFIX = "/api/v1"
SUPER_ADMIN_HEADERS = {"HTTP_X_ACTOR_ROLE": "super_admin", "HTTP_X_ACTOR_ID": str(uuid.uuid4())}
DEALER_HEADERS = {"HTTP_X_ACTOR_ROLE": "dealer", "HTTP_X_ACTOR_ID": str(uuid.uuid4())}


class CreateValuationMasterVersionViewTests(APITestCase):
    def setUp(self):
        brand = Brand.objects.create(brand_name="Honda")
        model = Model.objects.create(brand=brand, model_name="Activa")
        self.variant = Variant.objects.create(model=model, variant_name="125 Standard")

    def _payload(self, **overrides):
        payload = {
            "year": 2022,
            "variantId": str(self.variant.id),
            "minimumSellingPrice": "50000.00",
            "margin": "5000.00",
            "scrapValue": "10000.00",
        }
        payload.update(overrides)
        return payload

    def test_first_version_success_returns_201(self):
        response = self.client.post(
            f"{API_PREFIX}/admin/valuation-master",
            self._payload(),
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["data"]["active"])
        self.assertEqual(response.data["data"]["minimumSellingPrice"], "50000.00")

    def test_second_version_without_token_returns_409_concurrency(self):
        """A first Active row already exists; omitting previousVersionUpdatedAt must fail (ENG-0003)."""
        self.client.post(
            f"{API_PREFIX}/admin/valuation-master",
            self._payload(),
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        response = self.client.post(
            f"{API_PREFIX}/admin/valuation-master",
            self._payload(minimumSellingPrice="52000.00"),
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data["errors"][0]["code"], "409_CONFLICT")

    def test_versioning_with_correct_token_succeeds_and_closes_prior_row(self):
        first = self.client.post(
            f"{API_PREFIX}/admin/valuation-master",
            self._payload(),
            format="json",
            **SUPER_ADMIN_HEADERS,
        ).data["data"]

        second = self.client.post(
            f"{API_PREFIX}/admin/valuation-master",
            self._payload(
                minimumSellingPrice="52000.00", previousVersionUpdatedAt=first["updatedAt"]
            ),
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(second.status_code, 201)
        self.assertEqual(
            ValuationMaster.objects.filter(year=2022, variant=self.variant).count(), 2
        )
        prior = ValuationMaster.objects.get(id=first["id"])
        self.assertFalse(prior.active)

    def test_negative_amount_returns_400(self):
        response = self.client.post(
            f"{API_PREFIX}/admin/valuation-master",
            self._payload(minimumSellingPrice="-1.00"),
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(response.status_code, 400)

    def test_rejects_non_super_admin(self):
        response = self.client.post(
            f"{API_PREFIX}/admin/valuation-master",
            self._payload(),
            format="json",
            **DEALER_HEADERS,
        )
        self.assertEqual(response.status_code, 403)

    def test_unknown_variant_returns_404(self):
        response = self.client.post(
            f"{API_PREFIX}/admin/valuation-master",
            self._payload(variantId=str(uuid.uuid4())),
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(response.status_code, 404)


class DeactivateValuationMasterViewTests(APITestCase):
    def setUp(self):
        brand = Brand.objects.create(brand_name="Honda")
        model = Model.objects.create(brand=brand, model_name="Activa")
        self.variant = Variant.objects.create(model=model, variant_name="125 Standard")
        create_response = self.client.post(
            f"{API_PREFIX}/admin/valuation-master",
            {
                "year": 2022,
                "variantId": str(self.variant.id),
                "minimumSellingPrice": "50000.00",
                "margin": "5000.00",
                "scrapValue": "10000.00",
            },
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.valuation_master_id = create_response.data["data"]["id"]

    def test_deactivate_success(self):
        response = self.client.delete(
            f"{API_PREFIX}/admin/valuation-master/{self.valuation_master_id}",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            ValuationMaster.objects.get(id=self.valuation_master_id).active
        )

    def test_deactivate_rejects_non_super_admin(self):
        response = self.client.delete(
            f"{API_PREFIX}/admin/valuation-master/{self.valuation_master_id}",
            **DEALER_HEADERS,
        )
        self.assertEqual(response.status_code, 403)
