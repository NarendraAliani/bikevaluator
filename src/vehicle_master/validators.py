# Full Path: src/vehicle_master/validators.py
# Relative Path: validators.py
# Module: vehicle_master
# Purpose: Reusable field-level validators for Vehicle Master models and serializers.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §6 (Validation Matrix), EP-001 §6 (Validation Package),
#   FS-001 §8 (Validation Rules), FS-001 Open Question #3 (field length/Year range)
"""
Reusable validators for Vehicle Master.

These implement ISP-001 §6's Validation Matrix. Two of them (year range,
name max length) enforce **proposed implementation defaults**, not
settled business rules - neither DBD-001 nor BRR-001 specifies a valid
Year range or a maximum catalog-name length (FS-001 Open Question #3).
They are applied here so development is not blocked, and are easy to
change in one place if the architect sets different values later.
"""

import uuid as uuid_lib
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError

#: Proposed default (ISP-001 §6) - not specified in DBD-001/BRR-001.
MIN_YEAR = 1980

#: Proposed default max length for Brand/Model/Variant names (ISP-001 §6).
MAX_CATALOG_NAME_LENGTH = 100


def validate_year_range(value: int) -> None:
    """
    Validate that ``value`` is a plausible vehicle Year.

    Range is 1980 through (current year + 1) - a proposed
    implementation default (ISP-001 §6, FS-001 Open Question #3), not a
    numbered business rule. Raises ``django.core.exceptions.
    ValidationError`` if out of range.
    """
    max_year = date.today().year + 1
    if value < MIN_YEAR or value > max_year:
        raise ValidationError(
            f"Year must be between {MIN_YEAR} and {max_year} (got {value})."
        )


def validate_non_negative_amount(value: Decimal) -> None:
    """
    Validate that a monetary amount (MSP/Margin/Scrap Value) is zero or
    greater (FS-001 §8) - a negative price has no business meaning.
    This is a validation rule, not a numbered `BR-000x` (FSS-000 §1
    distinguishes the two).
    """
    if value < 0:
        raise ValidationError(f"Amount must be zero or greater (got {value}).")


def validate_catalog_name(value: str) -> None:
    """
    Structure-only validation for a Brand/Model/Variant name: required,
    non-empty, within the proposed max length.

    Does NOT check for duplicates - duplicate-name rejection
    (E-CATALOG-001) is Service-layer business logic (ISP-001
    FR-001-007), not a field-level validator concern, and is
    intentionally out of scope for this prompt (see
    ``validate_name_not_duplicate`` below).
    """
    if not value or not value.strip():
        raise ValidationError("Name is required.")
    if len(value) > MAX_CATALOG_NAME_LENGTH:
        raise ValidationError(
            f"Name must be {MAX_CATALOG_NAME_LENGTH} characters or fewer "
            f"(got {len(value)})."
        )


def validate_uuid(value: object) -> None:
    """
    Validate that ``value`` is a well-formed UUID (string or
    ``uuid.UUID``). Defensive validator for repository/service inputs
    that may arrive as raw strings (e.g. from future API path/query
    params) before this module implements API views.
    """
    if isinstance(value, uuid_lib.UUID):
        return
    try:
        uuid_lib.UUID(str(value))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValidationError(f"'{value}' is not a valid UUID.") from exc


def validate_name_not_duplicate(name: str, exists_check) -> None:
    """
    Structure-only duplicate-name validator (explicitly scoped this way
    by this prompt's instructions).

    A real invocation requires a repository-backed ``exists_check``
    callable (e.g. ``BrandRepository.name_exists``) - not wired up in
    this prompt, since doing so would require calling the repository
    layer from a validator, which is Service-layer responsibility
    (ISP-001 FR-001-007 / E-CATALOG-001 / BR-0011). Left as an explicit
    TODO for the business-logic implementation prompt.

    :param name: the candidate name to check.
    :param exists_check: a callable ``(name: str) -> bool``, expected to
        be a bound repository method once wired up.
    :raises NotImplementedError: always, in this prompt.
    """
    # TODO(business-logic prompt): wire this to a real repository
    # existence check once Service-layer business logic (BR-0011 /
    # E-CATALOG-001 enforcement) is implemented. See EP-001 §6,
    # ISP-001 FR-001-007.
    raise NotImplementedError(
        "Duplicate-name validation requires repository access and is "
        "deferred to the business-logic implementation prompt "
        "(see EP-001 §6, ISP-001 FR-001-007)."
    )
