# Full Path: src/vehicle_master/tests/test_repository_initialization.py
# Relative Path: tests/test_repository_initialization.py
# Module: vehicle_master
# Purpose: Unit tests verifying every repository class initializes
#   correctly and exposes the method shape ISP-001 §3 specified.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §3, TEST-001
"""
These tests deliberately check *initialization and shape* only - not
full CRUD/behavioral coverage. Full repository-behavior tests (create/
update/deactivate paths, the ValuationMaster concurrency/BR-0011
exception-translation path) are noted as a Known Limitation in this
prompt's Implementation Summary and left for the business-logic
implementation prompt, which is what will actually exercise these
methods through the (currently skeleton) Service layer.
"""

from django.test import SimpleTestCase

from vehicle_master.repositories import (
    AuditLogRepository,
    BrandRepository,
    ModelRepository,
    ValuationMasterRepository,
    VariantRepository,
)


class BrandRepositoryInitializationTests(SimpleTestCase):
    def test_instantiates_without_arguments(self):
        repository = BrandRepository()
        self.assertIsInstance(repository, BrandRepository)

    def test_exposes_expected_methods(self):
        repository = BrandRepository()
        for method_name in (
            "get_active",
            "get_by_id",
            "name_exists",
            "create",
            "update",
            "deactivate",
        ):
            self.assertTrue(
                callable(getattr(repository, method_name, None)),
                f"BrandRepository is missing callable '{method_name}' (ISP-001 §3).",
            )


class ModelRepositoryInitializationTests(SimpleTestCase):
    def test_instantiates_without_arguments(self):
        repository = ModelRepository()
        self.assertIsInstance(repository, ModelRepository)

    def test_exposes_expected_methods(self):
        repository = ModelRepository()
        for method_name in (
            "get_active_by_brand",
            "get_by_id",
            "name_exists",
            "create",
            "update",
            "deactivate",
        ):
            self.assertTrue(
                callable(getattr(repository, method_name, None)),
                f"ModelRepository is missing callable '{method_name}' (ISP-001 §3).",
            )


class VariantRepositoryInitializationTests(SimpleTestCase):
    def test_instantiates_without_arguments(self):
        repository = VariantRepository()
        self.assertIsInstance(repository, VariantRepository)

    def test_exposes_expected_methods(self):
        repository = VariantRepository()
        for method_name in (
            "get_active_by_model",
            "get_by_id",
            "name_exists",
            "create",
            "update",
            "deactivate",
        ):
            self.assertTrue(
                callable(getattr(repository, method_name, None)),
                f"VariantRepository is missing callable '{method_name}' (ISP-001 §3).",
            )


class ValuationMasterRepositoryInitializationTests(SimpleTestCase):
    def test_instantiates_without_arguments(self):
        repository = ValuationMasterRepository()
        self.assertIsInstance(repository, ValuationMasterRepository)

    def test_exposes_expected_methods(self):
        repository = ValuationMasterRepository()
        for method_name in (
            "get_active_by_year_variant",
            "get_by_id",
            "get_version_history",
            "create_new_version",
            "deactivate",
        ):
            self.assertTrue(
                callable(getattr(repository, method_name, None)),
                f"ValuationMasterRepository is missing callable '{method_name}' (ISP-001 §3).",
            )


class AuditLogRepositoryInterfaceTests(SimpleTestCase):
    """
    AuditLogRepository is an abstract interface only (this prompt's
    explicit "use interface only" instruction) - it must not be
    directly instantiable.
    """

    def test_cannot_instantiate_directly(self):
        with self.assertRaises(TypeError):
            AuditLogRepository()  # abstract method `create` is unimplemented
