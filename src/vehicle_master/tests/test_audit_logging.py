# Full Path: src/vehicle_master/tests/test_audit_logging.py
# Relative Path: tests/test_audit_logging.py
# Module: vehicle_master
# Purpose: IMP-003B Task 2 - verifies PersistentAuditLogRepository
#   actually persists audit rows, that every Admin write path (HTTP and
#   the importer) creates one, and that correlation_id/request_id
#   threading via audit_context works.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: IMP-003B Task 2, DBD-001 §2, TEST-001
import uuid
from decimal import Decimal
from types import SimpleNamespace

from django.test import TestCase
from rest_framework.test import APITestCase

from vehicle_master.audit_context import audit_run_context
from vehicle_master.models import AuditLog
from vehicle_master.repositories import PersistentAuditLogRepository
from vehicle_master.service_factory import build_vehicle_master_admin_service

API_PREFIX = "/api/v1"
SUPER_ADMIN_HEADERS = {"HTTP_X_ACTOR_ROLE": "super_admin", "HTTP_X_ACTOR_ID": str(uuid.uuid4())}


class PersistentAuditLogRepositoryTests(TestCase):
    def setUp(self):
        self.repository = PersistentAuditLogRepository()
        self.actor_id = uuid.uuid4()
        self.entity_id = uuid.uuid4()

    def test_create_persists_a_row(self):
        self.repository.create(
            actor_id=self.actor_id,
            entity_type="Brand",
            entity_id=self.entity_id,
            old_value=None,
            new_value={"brand_name": "Honda"},
            ip_address="127.0.0.1",
        )
        self.assertEqual(AuditLog.objects.count(), 1)
        row = AuditLog.objects.first()
        self.assertEqual(row.actor_id, self.actor_id)
        self.assertEqual(row.entity_type, "Brand")
        self.assertEqual(row.new_value, {"brand_name": "Honda"})

    def test_infers_create_action_when_not_given(self):
        self.repository.create(
            actor_id=self.actor_id, entity_type="Brand", entity_id=self.entity_id,
            old_value=None, new_value={"brand_name": "Honda"}, ip_address="127.0.0.1",
        )
        self.assertEqual(AuditLog.objects.first().action, "CREATE")

    def test_infers_deactivate_action_when_not_given(self):
        self.repository.create(
            actor_id=self.actor_id, entity_type="Brand", entity_id=self.entity_id,
            old_value={"active": True}, new_value=None, ip_address="127.0.0.1",
        )
        self.assertEqual(AuditLog.objects.first().action, "DEACTIVATE")

    def test_infers_update_action_when_not_given(self):
        self.repository.create(
            actor_id=self.actor_id, entity_type="Brand", entity_id=self.entity_id,
            old_value={"brand_name": "Old"}, new_value={"brand_name": "New"}, ip_address="127.0.0.1",
        )
        self.assertEqual(AuditLog.objects.first().action, "UPDATE")

    def test_picks_up_ambient_correlation_and_request_id(self):
        with audit_run_context(correlation_id="corr-1", request_id="req-1"):
            self.repository.create(
                actor_id=self.actor_id, entity_type="Brand", entity_id=self.entity_id,
                old_value=None, new_value={"brand_name": "Honda"}, ip_address="127.0.0.1",
            )
        row = AuditLog.objects.first()
        self.assertEqual(row.correlation_id, "corr-1")
        self.assertEqual(row.request_id, "req-1")

    def test_explicit_ids_override_ambient_context(self):
        with audit_run_context(correlation_id="ambient-corr"):
            self.repository.create(
                actor_id=self.actor_id, entity_type="Brand", entity_id=self.entity_id,
                old_value=None, new_value={"brand_name": "Honda"}, ip_address="127.0.0.1",
                correlation_id="explicit-corr",
            )
        self.assertEqual(AuditLog.objects.first().correlation_id, "explicit-corr")

    def test_success_and_error_message_fields(self):
        self.repository.create(
            actor_id=self.actor_id, entity_type="Brand", entity_id=self.entity_id,
            old_value=None, new_value=None, ip_address="127.0.0.1",
            success=False, error_message="Something went wrong",
        )
        row = AuditLog.objects.first()
        self.assertFalse(row.success)
        self.assertEqual(row.error_message, "Something went wrong")


class AdminServiceCreatesRealAuditRecordsTests(TestCase):
    """service_factory now defaults to PersistentAuditLogRepository (IMP-003B)."""

    def test_create_brand_via_service_factory_default_writes_audit_row(self):
        service = build_vehicle_master_admin_service()
        actor = SimpleNamespace(id=uuid.uuid4(), role="super_admin")
        brand = service.create_brand("Honda", actor, "127.0.0.1")
        self.assertTrue(
            AuditLog.objects.filter(entity_type="Brand", entity_id=brand.id).exists()
        )

    def test_create_valuation_master_version_writes_audit_row(self):
        from vehicle_master.models import Brand, Model, Variant

        brand = Brand.objects.create(brand_name="Honda")
        model = Model.objects.create(brand=brand, model_name="Activa")
        variant = Variant.objects.create(model=model, variant_name="6g")
        service = build_vehicle_master_admin_service()
        actor = SimpleNamespace(id=uuid.uuid4(), role="super_admin")
        valuation_master = service.create_valuation_master_version(
            year=2022, variant_id=variant.id, minimum_selling_price=Decimal("45000.00"),
            margin=Decimal("5000.00"), scrap_value=Decimal("0.00"),
            expected_previous_updated_at=None, actor=actor, ip_address="127.0.0.1",
        )
        self.assertTrue(
            AuditLog.objects.filter(
                entity_type="ValuationMaster", entity_id=valuation_master.id
            ).exists()
        )


class AdminHttpEndpointsCreateAuditRecordsTests(APITestCase):
    """Every real Admin HTTP write path now leaves a persisted audit trail."""

    def test_creating_a_brand_over_http_writes_an_audit_row(self):
        response = self.client.post(
            f"{API_PREFIX}/admin/vehicles",
            {"entityType": "BRAND", "name": "Honda"},
            format="json",
            **SUPER_ADMIN_HEADERS,
        )
        self.assertEqual(response.status_code, 201)
        brand_id = response.data["data"]["id"]
        audit_row = AuditLog.objects.get(entity_type="Brand", entity_id=brand_id)
        self.assertEqual(audit_row.action, "CREATE")
        self.assertIsNotNone(audit_row.request_id)  # RequestIdMiddleware sets this


class ImporterWritesAuditRecordsTests(TestCase):
    def test_import_run_creates_audit_rows_sharing_one_correlation_id(self):
        import io
        import tempfile
        from pathlib import Path

        from django.core.management import call_command

        header = (
            "Year,Brand,Model,Variant,MinSellingPrice,Margin,HalfEngineExp,FullEngineExp,"
            "FullColourExp,HalfColourExp,ShockForkExp,TyresExp,GearBoxExp,ClutchExp,"
            "FullPlasticExp,HalfPlasticExp\n"
        )
        row = "2022,Honda,Activa,6g,45000,5000,5000,7500,6000,5000,2000,2000,3500,1500,2000,1000\n"
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "import.csv"
            file_path.write_text(header + row, encoding="utf-8")
            call_command("import_valuation_master", f"--file={file_path}", stdout=io.StringIO())

        audit_rows = AuditLog.objects.filter(entity_type__in=["Brand", "Model", "Variant", "ValuationMaster"])
        self.assertGreaterEqual(audit_rows.count(), 4)
        correlation_ids = set(audit_rows.values_list("correlation_id", flat=True))
        self.assertEqual(len(correlation_ids), 1)  # every row from the same run shares one id
        self.assertIsNotNone(list(correlation_ids)[0])
