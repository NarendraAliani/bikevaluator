# Full Path: src/vehicle_master/tests/test_models.py
# Relative Path: tests/test_models.py
# Module: vehicle_master
# Purpose: Unit tests for Brand/Model/Variant/ValuationMaster ORM models,
#   including the BR-0011 partial-unique-index and non-negative CHECK constraints.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: TEST-001 (test naming references BR/FR IDs),
#   BRR-001 BR-0007/BR-0011, DBD-001 §5/§6a, EP-001 §3 (Database Package)
"""
Model-layer unit tests. Uses only synthetic data (TEST-001 - "no
production dealer data in test fixtures").
"""

import uuid
from datetime import datetime, timezone as dt_timezone
from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase

from vehicle_master.models import Brand, Model, ValuationMaster, Variant


class BrandModelTests(TestCase):
    """Unit tests for the Brand model."""

    def test_brand_created_with_uuid_pk_and_active_default(self):
        """A new Brand gets a UUID primary key and defaults to active=True (DBD-001 §5)."""
        brand = Brand.objects.create(brand_name="Honda")
        self.assertIsInstance(brand.id, uuid.UUID)
        self.assertTrue(brand.active)

    def test_brand_str_returns_name(self):
        """__str__ returns the brand_name for readability in admin/shell/logs."""
        brand = Brand.objects.create(brand_name="Bajaj")
        self.assertEqual(str(brand), "Bajaj")

    def test_brand_soft_deactivate_does_not_delete_row(self):
        """Deactivating sets active=False; the row is never hard-deleted (DBD-001 §5)."""
        brand = Brand.objects.create(brand_name="TVS")
        brand.active = False
        brand.save(update_fields=["active"])
        self.assertTrue(Brand.objects.filter(id=brand.id).exists())
        self.assertFalse(Brand.objects.get(id=brand.id).active)


class ModelModelTests(TestCase):
    """Unit tests for the Model model (product line, e.g. Honda Activa)."""

    def setUp(self):
        self.brand = Brand.objects.create(brand_name="Honda")

    def test_model_requires_brand_fk(self):
        """A Model row is linked to its parent Brand (DBD-001 §2)."""
        model = Model.objects.create(brand=self.brand, model_name="Activa")
        self.assertEqual(model.brand_id, self.brand.id)

    def test_model_restrict_on_delete_protects_brand(self):
        """
        FK uses on_delete=RESTRICT (DBD-001 §5 - no hard deletes
        anywhere in this schema); deleting a referenced Brand must be
        rejected by the database, not silently cascade.
        """
        Model.objects.create(brand=self.brand, model_name="Activa")
        with self.assertRaises(IntegrityError):
            self.brand.delete()


class VariantModelTests(TestCase):
    """Unit tests for the Variant model."""

    def setUp(self):
        self.brand = Brand.objects.create(brand_name="Honda")
        self.model = Model.objects.create(brand=self.brand, model_name="Activa")

    def test_variant_requires_model_fk(self):
        """A Variant row is linked to its parent Model (DBD-001 §2)."""
        variant = Variant.objects.create(model=self.model, variant_name="125 Standard")
        self.assertEqual(variant.model_id, self.model.id)


class ValuationMasterModelTests(TestCase):
    """
    Unit tests for ValuationMaster - BR-0007 versioning shape and the
    BR-0011 partial-unique-index (EP-001 §3).
    """

    def setUp(self):
        brand = Brand.objects.create(brand_name="Honda")
        model = Model.objects.create(brand=brand, model_name="Activa")
        self.variant = Variant.objects.create(model=model, variant_name="125 Standard")

    def test_br_0011_rejects_second_active_row_same_year_variant(self):
        """
        BR-0011: exactly one Active ValuationMaster per Year+Variant.
        A second Active row for the same Year+Variant must be rejected
        by the database's partial unique index.
        """
        ValuationMaster.objects.create(
            year=2022,
            variant=self.variant,
            minimum_selling_price=Decimal("50000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            active=True,
            effective_from=datetime(2026, 1, 1, tzinfo=dt_timezone.utc),
        )
        with self.assertRaises(IntegrityError):
            ValuationMaster.objects.create(
                year=2022,
                variant=self.variant,
                minimum_selling_price=Decimal("51000.00"),
                margin=Decimal("5000.00"),
                scrap_value=Decimal("10000.00"),
                active=True,
                effective_from=datetime(2026, 2, 1, tzinfo=dt_timezone.utc),
            )

    def test_br_0007_allows_inactive_historical_row_same_year_variant(self):
        """
        BR-0007: superseded (inactive) rows may legitimately share the
        same Year+Variant as the current Active row - the partial
        index must NOT block this (this is exactly why a plain unique
        constraint would have been wrong, per EP-001 §3).
        """
        ValuationMaster.objects.create(
            year=2022,
            variant=self.variant,
            minimum_selling_price=Decimal("48000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            active=False,
            effective_from=datetime(2025, 1, 1, tzinfo=dt_timezone.utc),
            effective_to=datetime(2026, 1, 1, tzinfo=dt_timezone.utc),
        )
        # Should not raise - the historical row above is inactive.
        ValuationMaster.objects.create(
            year=2022,
            variant=self.variant,
            minimum_selling_price=Decimal("50000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            active=True,
            effective_from=datetime(2026, 1, 1, tzinfo=dt_timezone.utc),
        )
        self.assertEqual(
            ValuationMaster.objects.filter(year=2022, variant=self.variant).count(), 2
        )

    def test_negative_msp_rejected_by_check_constraint(self):
        """
        A negative minimum_selling_price violates the DB-level CHECK
        constraint (EP-001 §3 - defense in depth alongside
        validate_non_negative_amount, which only runs on full_clean(),
        not on .create()).
        """
        with self.assertRaises(IntegrityError):
            ValuationMaster.objects.create(
                year=2023,
                variant=self.variant,
                minimum_selling_price=Decimal("-1.00"),
                margin=Decimal("5000.00"),
                scrap_value=Decimal("10000.00"),
                active=True,
                effective_from=datetime(2026, 1, 1, tzinfo=dt_timezone.utc),
            )

    def test_different_years_can_each_have_an_active_row(self):
        """The partial unique index is scoped to (year, variant) together - different Years are independent."""
        ValuationMaster.objects.create(
            year=2022,
            variant=self.variant,
            minimum_selling_price=Decimal("50000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            active=True,
            effective_from=datetime(2026, 1, 1, tzinfo=dt_timezone.utc),
        )
        # Should not raise - different year.
        ValuationMaster.objects.create(
            year=2023,
            variant=self.variant,
            minimum_selling_price=Decimal("55000.00"),
            margin=Decimal("5000.00"),
            scrap_value=Decimal("10000.00"),
            active=True,
            effective_from=datetime(2026, 1, 1, tzinfo=dt_timezone.utc),
        )
