# Full Path: src/vehicle_master/tests/test_serializers.py
# Relative Path: tests/test_serializers.py
# Module: vehicle_master
# Purpose: Unit tests for request/response serializers - field parsing,
#   UUID/Decimal parsing, required fields. No business logic tested here.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §2, TEST-001, IMP-001C
import uuid
from decimal import Decimal

from django.test import SimpleTestCase

from vehicle_master.serializers import (
    ConfigurationQuerySerializer,
    CreateValuationMasterVersionSerializer,
    CreateVehicleCatalogEntrySerializer,
    EntityTypeQuerySerializer,
    ModelListQuerySerializer,
)


class CreateVehicleCatalogEntrySerializerTests(SimpleTestCase):
    def test_valid_brand_payload(self):
        serializer = CreateVehicleCatalogEntrySerializer(
            data={"entityType": "BRAND", "name": "Honda"}
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["entity_type"], "BRAND")
        self.assertEqual(serializer.validated_data["name"], "Honda")

    def test_valid_model_payload_with_parent_id(self):
        parent_id = uuid.uuid4()
        serializer = CreateVehicleCatalogEntrySerializer(
            data={"entityType": "MODEL", "parentId": str(parent_id), "name": "Activa"}
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["parent_id"], parent_id)

    def test_invalid_entity_type_rejected(self):
        serializer = CreateVehicleCatalogEntrySerializer(
            data={"entityType": "NOT_A_TYPE", "name": "Honda"}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("entityType", serializer.errors)

    def test_missing_name_rejected(self):
        serializer = CreateVehicleCatalogEntrySerializer(data={"entityType": "BRAND"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_blank_name_rejected(self):
        serializer = CreateVehicleCatalogEntrySerializer(
            data={"entityType": "BRAND", "name": ""}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_malformed_parent_id_uuid_rejected(self):
        serializer = CreateVehicleCatalogEntrySerializer(
            data={"entityType": "MODEL", "parentId": "not-a-uuid", "name": "Activa"}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("parentId", serializer.errors)


class EntityTypeQuerySerializerTests(SimpleTestCase):
    def test_valid_entity_type_passes(self):
        serializer = EntityTypeQuerySerializer(data={"entityType": "VARIANT"})
        self.assertTrue(serializer.is_valid())

    def test_missing_entity_type_rejected(self):
        serializer = EntityTypeQuerySerializer(data={})
        self.assertFalse(serializer.is_valid())


class ModelListQuerySerializerTests(SimpleTestCase):
    def test_valid_uuid_passes(self):
        serializer = ModelListQuerySerializer(data={"brand_id": str(uuid.uuid4())})
        self.assertTrue(serializer.is_valid())

    def test_missing_brand_id_rejected(self):
        serializer = ModelListQuerySerializer(data={})
        self.assertFalse(serializer.is_valid())

    def test_malformed_uuid_rejected(self):
        serializer = ModelListQuerySerializer(data={"brand_id": "abc"})
        self.assertFalse(serializer.is_valid())


class ConfigurationQuerySerializerTests(SimpleTestCase):
    def test_valid_payload_passes(self):
        serializer = ConfigurationQuerySerializer(
            data={
                "year": 2022,
                "brand_id": str(uuid.uuid4()),
                "model_id": str(uuid.uuid4()),
                "variant_id": str(uuid.uuid4()),
            }
        )
        self.assertTrue(serializer.is_valid())

    def test_non_integer_year_rejected(self):
        serializer = ConfigurationQuerySerializer(
            data={
                "year": "not-a-year",
                "brand_id": str(uuid.uuid4()),
                "model_id": str(uuid.uuid4()),
                "variant_id": str(uuid.uuid4()),
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("year", serializer.errors)

    def test_missing_variant_id_rejected(self):
        serializer = ConfigurationQuerySerializer(
            data={"year": 2022, "brand_id": str(uuid.uuid4()), "model_id": str(uuid.uuid4())}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("variant_id", serializer.errors)


class CreateValuationMasterVersionSerializerTests(SimpleTestCase):
    def test_valid_payload_parses_decimal_fields(self):
        serializer = CreateValuationMasterVersionSerializer(
            data={
                "year": 2022,
                "variantId": str(uuid.uuid4()),
                "minimumSellingPrice": "50000.00",
                "margin": "5000.00",
                "scrapValue": "10000.00",
            }
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["minimum_selling_price"], Decimal("50000.00")
        )

    def test_previous_version_updated_at_optional(self):
        serializer = CreateValuationMasterVersionSerializer(
            data={
                "year": 2022,
                "variantId": str(uuid.uuid4()),
                "minimumSellingPrice": "50000.00",
                "margin": "5000.00",
                "scrapValue": "10000.00",
            }
        )
        self.assertTrue(serializer.is_valid())
        self.assertIsNone(serializer.validated_data.get("previous_version_updated_at"))

    def test_missing_required_field_rejected(self):
        serializer = CreateValuationMasterVersionSerializer(
            data={"year": 2022, "variantId": str(uuid.uuid4())}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("minimumSellingPrice", serializer.errors)

    def test_non_decimal_amount_rejected(self):
        serializer = CreateValuationMasterVersionSerializer(
            data={
                "year": 2022,
                "variantId": str(uuid.uuid4()),
                "minimumSellingPrice": "not-a-number",
                "margin": "5000.00",
                "scrapValue": "10000.00",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("minimumSellingPrice", serializer.errors)
