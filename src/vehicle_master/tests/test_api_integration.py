# Full Path: src/vehicle_master/tests/test_api_integration.py
# Relative Path: tests/test_api_integration.py
# Module: vehicle_master
# Purpose: End-to-end integration tests exercising the full stack -
#   HTTP -> Serializer -> Service -> Repository -> Database - across a
#   realistic Admin-then-Dealer lifecycle.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: FS-001 (whole document), ISP-001, EP-001, IMP-001C, TEST-001
import uuid

from rest_framework.test import APITestCase

from vehicle_master.models import Brand, Model, ValuationMaster, Variant

API_PREFIX = "/api/v1"
SUPER_ADMIN_HEADERS = {"HTTP_X_ACTOR_ROLE": "super_admin", "HTTP_X_ACTOR_ID": str(uuid.uuid4())}


class FullVehicleMasterLifecycleIntegrationTest(APITestCase):
    """
    Simulates a realistic sequence: Super Admin builds out the catalog
    and sets a price; a Dealer then browses the catalog and loads the
    Configuration - all purely over HTTP, verifying the database state
    at each step (not just the HTTP response).
    """

    def test_full_admin_build_then_dealer_read_lifecycle(self):
        # 1. Super Admin creates a Brand.
        brand_response = self.client.post(
            f"{API_PREFIX}/admin/vehicles",
            {"entityType": "BRAND", "name": "Honda"},
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(brand_response.status_code, 201)
        brand_id = brand_response.data["data"]["id"]
        self.assertTrue(Brand.objects.filter(id=brand_id, brand_name="Honda").exists())

        # 2. Super Admin creates a Model under that Brand.
        model_response = self.client.post(
            f"{API_PREFIX}/admin/vehicles",
            {"entityType": "MODEL", "parentId": brand_id, "name": "Activa"},
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(model_response.status_code, 201)
        model_id = model_response.data["data"]["id"]
        self.assertTrue(Model.objects.filter(id=model_id, brand_id=brand_id).exists())

        # 3. Super Admin creates a Variant under that Model.
        variant_response = self.client.post(
            f"{API_PREFIX}/admin/vehicles",
            {"entityType": "VARIANT", "parentId": model_id, "name": "125 Standard"},
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(variant_response.status_code, 201)
        variant_id = variant_response.data["data"]["id"]
        self.assertTrue(Variant.objects.filter(id=variant_id, model_id=model_id).exists())

        # 4. Dealer browses the catalog - each level should now be visible.
        brands = self.client.get(f"{API_PREFIX}/vehicles/brands")
        self.assertEqual([b["id"] for b in brands.data["data"]["brands"]], [brand_id])

        models = self.client.get(f"{API_PREFIX}/vehicles/models", {"brand_id": brand_id})
        self.assertEqual([m["id"] for m in models.data["data"]["models"]], [model_id])

        variants = self.client.get(f"{API_PREFIX}/vehicles/variants", {"model_id": model_id})
        self.assertEqual([v["id"] for v in variants.data["data"]["variants"]], [variant_id])

        # 5. Before pricing exists, Configuration Load must fail with VAL003 (BR-0005).
        no_pricing = self.client.get(
            f"{API_PREFIX}/vehicles/configuration",
            {"year": 2022, "brand_id": brand_id, "model_id": model_id, "variant_id": variant_id},
        )
        self.assertEqual(no_pricing.status_code, 404)
        self.assertEqual(no_pricing.data["errors"][0]["code"], "VAL003")

        # 6. Super Admin sets the price (BR-0007 first version).
        pricing_response = self.client.post(
            f"{API_PREFIX}/admin/valuation-master",
            {
                "year": 2022,
                "variantId": variant_id,
                "minimumSellingPrice": "50000.00",
                "margin": "5000.00",
                "scrapValue": "10000.00",
            },
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(pricing_response.status_code, 201)
        valuation_master_id = pricing_response.data["data"]["id"]
        self.assertTrue(
            ValuationMaster.objects.filter(id=valuation_master_id, active=True).exists()
        )

        # 7. Dealer can now load the Configuration successfully.
        configuration = self.client.get(
            f"{API_PREFIX}/vehicles/configuration",
            {"year": 2022, "brand_id": brand_id, "model_id": model_id, "variant_id": variant_id},
        )
        self.assertEqual(configuration.status_code, 200)
        self.assertEqual(configuration.data["data"]["minimumSellingPrice"], "50000.00")
        self.assertEqual(configuration.data["data"]["valuationMasterId"], valuation_master_id)

        # 8. Super Admin revises the price - BR-0007 versioning, old row closed.
        revision_response = self.client.post(
            f"{API_PREFIX}/admin/valuation-master",
            {
                "year": 2022,
                "variantId": variant_id,
                "minimumSellingPrice": "52000.00",
                "margin": "5000.00",
                "scrapValue": "10000.00",
                "previousVersionUpdatedAt": pricing_response.data["data"]["updatedAt"],
            },
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(revision_response.status_code, 201)
        self.assertFalse(ValuationMaster.objects.get(id=valuation_master_id).active)

        # 9. Dealer's next Configuration Load reflects the revised price.
        revised_configuration = self.client.get(
            f"{API_PREFIX}/vehicles/configuration",
            {"year": 2022, "brand_id": brand_id, "model_id": model_id, "variant_id": variant_id},
        )
        self.assertEqual(revised_configuration.data["data"]["minimumSellingPrice"], "52000.00")

        # 10. Deactivating the Variant blocks the Dealer with E-CATALOG-002.
        self.client.delete(
            f"{API_PREFIX}/admin/vehicles/{variant_id}?entityType=VARIANT",
            **SUPER_ADMIN_HEADERS,
        )
        blocked_configuration = self.client.get(
            f"{API_PREFIX}/vehicles/configuration",
            {"year": 2022, "brand_id": brand_id, "model_id": model_id, "variant_id": variant_id},
        )
        self.assertEqual(blocked_configuration.status_code, 409)
        self.assertEqual(blocked_configuration.data["errors"][0]["code"], "E-CATALOG-002")
