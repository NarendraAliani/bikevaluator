# Full Path: src/vehicle_master/tests/test_admin_vehicle_views.py
# Relative Path: tests/test_admin_vehicle_views.py
# Module: vehicle_master
# Purpose: API integration tests for /admin/vehicles (Brand/Model/Variant
#   create/update/deactivate) - success, validation, authorization,
#   duplicate, and 404 paths.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: API-001 (/admin/vehicles), BRR-001 BR-0004/BR-0011,
#   SDD-000 §8, TEST-001
import uuid

from rest_framework.test import APITestCase

from vehicle_master.models import Brand, Model, Variant

API_PREFIX = "/api/v1"
SUPER_ADMIN_HEADERS = {"HTTP_X_ACTOR_ROLE": "super_admin", "HTTP_X_ACTOR_ID": str(uuid.uuid4())}
DEALER_HEADERS = {"HTTP_X_ACTOR_ROLE": "dealer", "HTTP_X_ACTOR_ID": str(uuid.uuid4())}


class CreateBrandViewTests(APITestCase):
    def test_success_creates_brand_returns_201(self):
        response = self.client.post(
            f"{API_PREFIX}/admin/vehicles",
            {"entityType": "BRAND", "name": "Honda"},
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "Honda")
        self.assertEqual(response.data["data"]["entityType"], "BRAND")
        self.assertTrue(Brand.objects.filter(brand_name="Honda").exists())

    def test_rejects_non_super_admin_with_403(self):
        response = self.client.post(
            f"{API_PREFIX}/admin/vehicles",
            {"entityType": "BRAND", "name": "Honda"},
            format="json",
            **DEALER_HEADERS,
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["errors"][0]["code"], "E-AUTHZ-001")

    def test_rejects_missing_actor_role_with_403(self):
        """No X-Actor-Role header at all -> treated as unauthenticated/unauthorized."""
        response = self.client.post(
            f"{API_PREFIX}/admin/vehicles", {"entityType": "BRAND", "name": "Honda"}, format="json"
        )
        self.assertEqual(response.status_code, 403)

    def test_rejects_duplicate_active_brand_with_409(self):
        Brand.objects.create(brand_name="Honda")
        response = self.client.post(
            f"{API_PREFIX}/admin/vehicles",
            {"entityType": "BRAND", "name": "Honda"},
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data["errors"][0]["code"], "E-CATALOG-001")

    def test_rejects_malformed_body_with_400(self):
        response = self.client.post(
            f"{API_PREFIX}/admin/vehicles",
            {"entityType": "NOT_VALID", "name": "Honda"},
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(response.status_code, 400)


class CreateModelViewTests(APITestCase):
    def setUp(self):
        self.brand = Brand.objects.create(brand_name="Honda")

    def test_success_creates_model(self):
        response = self.client.post(
            f"{API_PREFIX}/admin/vehicles",
            {"entityType": "MODEL", "parentId": str(self.brand.id), "name": "Activa"},
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["data"]["parentId"], str(self.brand.id))

    def test_unknown_parent_brand_returns_404(self):
        response = self.client.post(
            f"{API_PREFIX}/admin/vehicles",
            {"entityType": "MODEL", "parentId": str(uuid.uuid4()), "name": "Activa"},
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["errors"][0]["code"], "VAL001")


class UpdateAndDeactivateBrandViewTests(APITestCase):
    def setUp(self):
        self.brand = Brand.objects.create(brand_name="Honda")

    def test_update_success(self):
        response = self.client.put(
            f"{API_PREFIX}/admin/vehicles/{self.brand.id}?entityType=BRAND",
            {"name": "Honda Motors"},
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["name"], "Honda Motors")

    def test_update_missing_entity_type_query_param_returns_400(self):
        """The discovered-gap fix: entityType is required as a query param on PUT."""
        response = self.client.put(
            f"{API_PREFIX}/admin/vehicles/{self.brand.id}",
            {"name": "Honda Motors"},
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(response.status_code, 400)

    def test_update_unknown_id_returns_404(self):
        response = self.client.put(
            f"{API_PREFIX}/admin/vehicles/{uuid.uuid4()}?entityType=BRAND",
            {"name": "X"},
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(response.status_code, 404)

    def test_deactivate_success_soft_deletes(self):
        response = self.client.delete(
            f"{API_PREFIX}/admin/vehicles/{self.brand.id}?entityType=BRAND",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(response.status_code, 200)
        self.brand.refresh_from_db()
        self.assertFalse(self.brand.active)
        self.assertTrue(Brand.objects.filter(id=self.brand.id).exists())  # soft delete, not hard

    def test_deactivate_rejects_non_super_admin(self):
        response = self.client.delete(
            f"{API_PREFIX}/admin/vehicles/{self.brand.id}?entityType=BRAND",
            **DEALER_HEADERS,
        )
        self.assertEqual(response.status_code, 403)


class VariantAdminViewTests(APITestCase):
    def setUp(self):
        brand = Brand.objects.create(brand_name="Honda")
        self.model = Model.objects.create(brand=brand, model_name="Activa")

    def test_create_variant_success(self):
        response = self.client.post(
            f"{API_PREFIX}/admin/vehicles",
            {"entityType": "VARIANT", "parentId": str(self.model.id), "name": "125 Standard"},
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(response.status_code, 201)

    def test_create_variant_duplicate_under_same_model_returns_409(self):
        Variant.objects.create(model=self.model, variant_name="125 Standard")
        response = self.client.post(
            f"{API_PREFIX}/admin/vehicles",
            {"entityType": "VARIANT", "parentId": str(self.model.id), "name": "125 Standard"},
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(response.status_code, 409)
