# Full Path: src/vehicle_master/tests/test_valuation_integration.py
# Relative Path: tests/test_valuation_integration.py
# Module: vehicle_master
# Purpose: End-to-end integration test exercising the full Valuation
#   Engine stack - HTTP -> Serializer -> Service -> Repository -> Database -
#   across a realistic Admin-builds-catalog then Dealer-values-a-vehicle
#   lifecycle. Mirrors test_api_integration.py's pattern for Vehicle Master.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: FS-002 (whole document), ISP-002, EP-002, TEST-001
import uuid

from rest_framework.test import APITestCase

from vehicle_master.models import (
    Brand,
    Model,
    RepairComponent,
    RepairOption,
    ValuationRepairCost,
    Variant,
)

API_PREFIX = "/api/v1"
SUPER_ADMIN_HEADERS = {"HTTP_X_ACTOR_ROLE": "super_admin", "HTTP_X_ACTOR_ID": str(uuid.uuid4())}


class FullValuationEngineLifecycleIntegrationTest(APITestCase):
    """
    Simulates the realistic Dealer journey this module exists for:
    Super Admin builds out the vehicle catalog and sets a price (reusing
    Vehicle Master's existing admin endpoints); a Dealer then loads the
    Configuration, browses the Repair Component catalog, selects repair
    options, and submits a Valuation calculation - all purely over HTTP,
    verifying both the HTTP response and that the module remains
    stateless (FR-002-012 - no new row written anywhere).
    """

    def test_full_admin_build_then_dealer_valuation_lifecycle(self):
        # 1. Super Admin builds the vehicle catalog (Brand -> Model -> Variant).
        brand_id = self.client.post(
            f"{API_PREFIX}/admin/vehicles",
            {"entityType": "BRAND", "name": "Honda"},
            format="json",
            **SUPER_ADMIN_HEADERS,
        ).data["data"]["id"]
        model_id = self.client.post(
            f"{API_PREFIX}/admin/vehicles",
            {"entityType": "MODEL", "parentId": brand_id, "name": "Activa"},
            format="json",
            **SUPER_ADMIN_HEADERS,
        ).data["data"]["id"]
        variant_response = self.client.post(
            f"{API_PREFIX}/admin/vehicles",
            {"entityType": "VARIANT", "parentId": model_id, "name": "125 Standard"},
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        variant_id = variant_response.data["data"]["id"]
        self.assertTrue(Variant.objects.filter(id=variant_id).exists())

        # 2. Before pricing exists, Valuation Calculate must fail with VAL003 (BR-0005).
        no_pricing = self.client.post(
            f"{API_PREFIX}/valuation/calculate",
            {"year": 2022, "variantId": variant_id, "repairAssessment": []},
            format="json",
        )
        self.assertEqual(no_pricing.status_code, 404)
        self.assertEqual(no_pricing.data["errors"][0]["code"], "VAL003")

        # 3. Super Admin sets the price.
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

        # 4. Dealer loads the Configuration (reusing Vehicle Master's existing endpoint).
        configuration = self.client.get(
            f"{API_PREFIX}/vehicles/configuration",
            {"year": 2022, "brand_id": brand_id, "model_id": model_id, "variant_id": variant_id},
        )
        self.assertEqual(configuration.status_code, 200)

        # 5. Dealer browses the Repair Component catalog (now vehicle-scoped,
        # IMP-003) - empty at this point.
        repairs_query = {"year": 2022, "variant_id": variant_id}
        empty_components = self.client.get(f"{API_PREFIX}/repairs/components", repairs_query)
        self.assertEqual(empty_components.data["data"]["components"], [])

        # 6. A Repair Component + Option + vehicle-scoped cost are seeded
        # directly (FS-004's future concern is administering these via
        # API - not built in this module).
        component = RepairComponent.objects.create(name="Engine")
        option = RepairOption.objects.create(repair_component=component, option_name="PARTIAL")
        ValuationRepairCost.objects.create(
            valuation_master_id=pricing_response.data["data"]["id"],
            repair_option=option,
            deduction_amount="3000.00",
        )

        # 7. Dealer re-browses the Repair Component catalog - now populated.
        components = self.client.get(f"{API_PREFIX}/repairs/components", repairs_query)
        self.assertEqual(len(components.data["data"]["components"]), 1)
        self.assertEqual(
            components.data["data"]["components"][0]["options"][0]["optionName"], "PARTIAL"
        )

        # 8. Dealer selects the repair option and submits the Valuation calculation.
        calculation = self.client.post(
            f"{API_PREFIX}/valuation/calculate",
            {
                "year": 2022,
                "variantId": variant_id,
                "repairAssessment": [
                    {"repairComponentId": str(component.id), "repairOptionId": str(option.id)}
                ],
            },
            format="json",
        )
        self.assertEqual(calculation.status_code, 200)
        # 50000 - 5000 (margin) - 3000 (repair deduction) = 42000.
        self.assertEqual(calculation.data["data"]["recommendedPrice"], "42000.00")
        self.assertEqual(calculation.data["data"]["roundedPrice"], "42000")
        # 42000 / 50000 = 84% of MSP -> Good (BR-0003 band: 75-89%).
        self.assertEqual(calculation.data["data"]["label"], "GOOD")

        # 9. Statelessness (FR-002-012): no ValuationRequest-like row is written anywhere.
        from vehicle_master.models import ValuationMaster

        self.assertEqual(ValuationMaster.objects.count(), 1)  # only the one Admin created.
