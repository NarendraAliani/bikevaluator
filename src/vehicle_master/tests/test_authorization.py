# Full Path: src/vehicle_master/tests/test_authorization.py
# Relative Path: tests/test_authorization.py
# Module: vehicle_master
# Purpose: Unit tests for BR-0004 enforcement (enforce_super_admin).
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: BRR-001 BR-0004, SDD-000 §8 (E-AUTHZ-001)
from types import SimpleNamespace

from django.test import SimpleTestCase

from vehicle_master.authorization import enforce_super_admin
from vehicle_master.exceptions import NotAuthorizedError


class EnforceSuperAdminTests(SimpleTestCase):
    def test_super_admin_passes(self):
        actor = SimpleNamespace(role="super_admin")
        enforce_super_admin(actor)  # should not raise

    def test_dealer_raises_not_authorized(self):
        actor = SimpleNamespace(role="dealer")
        with self.assertRaises(NotAuthorizedError):
            enforce_super_admin(actor)

    def test_missing_role_attribute_raises_not_authorized(self):
        actor = SimpleNamespace()
        with self.assertRaises(NotAuthorizedError):
            enforce_super_admin(actor)

    def test_error_code_is_e_authz_001(self):
        actor = SimpleNamespace(role="dealer")
        with self.assertRaises(NotAuthorizedError) as ctx:
            enforce_super_admin(actor)
        self.assertEqual(ctx.exception.error_code, "E-AUTHZ-001")
