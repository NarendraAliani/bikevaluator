# Full Path: src/vehicle_master/exceptions.py
# Relative Path: exceptions.py
# Module: vehicle_master
# Purpose: Module exception hierarchy, each mapped to an approved error code.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: SDD-000 §8 (Error Catalogue), API-001 (Error Codes),
#   EP-001 §7 (Error Package - Backend/API/Flutter mapping)
"""
Vehicle Master's exception hierarchy.

Every exception here maps 1:1 to an error code already defined in an
approved document (SDD-000 §8 / API-001) - none are invented. See
EP-001 §7 for the full Backend -> API -> Flutter mapping each of these
participates in. No exception here is currently raised anywhere (no
business logic exists yet, per IMP-001A scope) - they exist so the
Service-layer skeletons (services/*.py) can reference them in TODO
comments and docstrings ahead of that implementation.
"""


class VehicleMasterError(Exception):
    """Base exception for every error this module can raise."""

    #: Overridden by each subclass with its approved error code.
    error_code: str = "VEHICLE_MASTER_ERROR"


class VehicleNotFoundError(VehicleMasterError):
    """Raised when a Brand/Model/Variant id does not resolve. Maps to VAL001 (API-001)."""

    error_code = "VAL001"


class VariantMissingError(VehicleMasterError):
    """Raised when a required Variant selection is missing/unresolved. Maps to VAL002 (API-001)."""

    error_code = "VAL002"


class PricingNotAvailableError(VehicleMasterError):
    """
    Raised when no Active ValuationMaster exists for a requested
    Year+Variant (BR-0005). Maps to VAL003 (API-001) / E-PRICING-001
    (SDD-000 §8).
    """

    error_code = "VAL003"


class DuplicateCatalogEntryError(VehicleMasterError):
    """
    Raised on a duplicate Brand/Model/Variant/Year combination, or a
    BR-0011 uniqueness violation. Maps to E-CATALOG-001 (SDD-000 §8).
    """

    error_code = "E-CATALOG-001"


class DeprecatedVariantError(VehicleMasterError):
    """Raised when a Deprecated (inactive) Variant is selected for a new Evaluation. Maps to E-CATALOG-002 (SDD-000 §8)."""

    error_code = "E-CATALOG-002"


class NotAuthorizedError(VehicleMasterError):
    """
    Raised when a non-``super_admin`` account attempts an Admin write
    (BR-0004). Maps to E-AUTHZ-001 (SDD-000 §8, ARC-0006).
    """

    error_code = "E-AUTHZ-001"


class ConcurrencyConflictError(VehicleMasterError):
    """
    Raised when a ValuationMaster write's optimistic-concurrency check
    fails (stale ``updated_at``). Maps to HTTP 409 (ENG-0003,
    DBD-001 §6a).
    """

    error_code = "409_CONFLICT"
