# Full Path: src/vehicle_master/tests/test_validators.py
# Relative Path: tests/test_validators.py
# Module: vehicle_master
# Purpose: Unit tests for vehicle_master.validators.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §6 (Validation Matrix), TEST-001
import uuid
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from vehicle_master.validators import (
    MAX_CATALOG_NAME_LENGTH,
    MIN_YEAR,
    validate_catalog_name,
    validate_name_not_duplicate,
    validate_non_negative_amount,
    validate_uuid,
    validate_year_range,
)


class ValidateYearRangeTests(SimpleTestCase):
    """validate_year_range - proposed default range (ISP-001 §6, FS-001 Open Question #3)."""

    def test_current_year_is_valid(self):
        validate_year_range(date.today().year)  # should not raise

    def test_year_below_minimum_raises(self):
        with self.assertRaises(ValidationError):
            validate_year_range(MIN_YEAR - 1)

    def test_year_above_maximum_raises(self):
        with self.assertRaises(ValidationError):
            validate_year_range(date.today().year + 2)

    def test_boundary_min_year_is_valid(self):
        validate_year_range(MIN_YEAR)  # should not raise

    def test_boundary_max_year_is_valid(self):
        validate_year_range(date.today().year + 1)  # should not raise


class ValidateNonNegativeAmountTests(SimpleTestCase):
    """validate_non_negative_amount (FS-001 §8)."""

    def test_zero_is_valid(self):
        validate_non_negative_amount(Decimal("0"))  # should not raise

    def test_positive_is_valid(self):
        validate_non_negative_amount(Decimal("50000.00"))  # should not raise

    def test_negative_raises(self):
        with self.assertRaises(ValidationError):
            validate_non_negative_amount(Decimal("-0.01"))


class ValidateCatalogNameTests(SimpleTestCase):
    """validate_catalog_name - structure-only (no duplicate check, see below)."""

    def test_valid_name_passes(self):
        validate_catalog_name("Honda")  # should not raise

    def test_empty_string_raises(self):
        with self.assertRaises(ValidationError):
            validate_catalog_name("")

    def test_whitespace_only_raises(self):
        with self.assertRaises(ValidationError):
            validate_catalog_name("   ")

    def test_name_over_max_length_raises(self):
        with self.assertRaises(ValidationError):
            validate_catalog_name("A" * (MAX_CATALOG_NAME_LENGTH + 1))

    def test_name_at_max_length_is_valid(self):
        validate_catalog_name("A" * MAX_CATALOG_NAME_LENGTH)  # should not raise


class ValidateUuidTests(SimpleTestCase):
    """validate_uuid - defensive validator for raw string/UUID inputs."""

    def test_uuid_instance_passes(self):
        validate_uuid(uuid.uuid4())  # should not raise

    def test_valid_uuid_string_passes(self):
        validate_uuid(str(uuid.uuid4()))  # should not raise

    def test_invalid_string_raises(self):
        with self.assertRaises(ValidationError):
            validate_uuid("not-a-uuid")

    def test_none_raises(self):
        with self.assertRaises(ValidationError):
            validate_uuid(None)


class ValidateNameNotDuplicateTests(SimpleTestCase):
    """
    validate_name_not_duplicate - explicitly structure-only in this
    prompt; always raises NotImplementedError until a business-logic
    prompt wires it to a real repository existence check.
    """

    def test_always_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            validate_name_not_duplicate("Honda", exists_check=lambda name: False)
