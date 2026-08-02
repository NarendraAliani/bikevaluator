# Full Path: src/vehicle_master/services/vehicle_catalog_service.py
# Relative Path: services/vehicle_catalog_service.py
# Module: vehicle_master
# Purpose: Dealer-facing, read-only Vehicle Master business logic.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §4.1, FS-001 §6 (FR-001-001..005), BR-0005,
#   ARC-0005 (no Year filtering on catalog lists)
"""
``VehicleCatalogService`` - implemented (IMP-001B).

Business logic here is deliberately thin: existence/referential checks
and error-code selection. The actual pricing computation (BR-0001,
BR-0002, BR-0009) belongs to the Valuation Engine (FS-002), not this
module (SDD-000 §4) - ``get_configuration`` only resolves and returns
the already-stored MSP/Margin/Scrap Value, it does not compute a
Purchase Price.
"""

import uuid
from dataclasses import dataclass, field
from decimal import Decimal

from vehicle_master.exceptions import (
    DeprecatedVariantError,
    PricingNotAvailableError,
    VariantMissingError,
    VehicleNotFoundError,
)
from vehicle_master.repositories import (
    BrandRepository,
    ModelRepository,
    ValuationMasterRepository,
    VariantRepository,
)


@dataclass
class Configuration:
    """
    Resolved Vehicle Master configuration for a Year+Variant
    (mirrors ISP-001 §2.4's ``ConfigurationDto`` shape - this is the
    Service layer's internal return type; a future serializer converts
    this into the actual API response, per EP-001 §2 Serializer Plan).

    ``repair_options`` is always empty today: Repair Master (a separate
    bounded context, DDD-001 §2) has no implementation anywhere in this
    codebase yet. Returning an empty list rather than fabricating data
    is deliberate - see this round's Architecture Observations.
    """

    valuation_master_id: uuid.UUID
    year: int
    variant_id: uuid.UUID
    minimum_selling_price: Decimal
    margin: Decimal
    scrap_value: Decimal
    repair_options: list = field(default_factory=list)


class VehicleCatalogService:
    """Dealer-facing, read-only service (ISP-001 §4.1)."""

    def __init__(
        self,
        brand_repository: BrandRepository,
        model_repository: ModelRepository,
        variant_repository: VariantRepository,
        valuation_master_repository: ValuationMasterRepository,
    ) -> None:
        self._brand_repository = brand_repository
        self._model_repository = model_repository
        self._variant_repository = variant_repository
        self._valuation_master_repository = valuation_master_repository

    def list_brands(self):
        """FR-001-001: all active Brands (ARC-0005: never filtered by Year)."""
        return self._brand_repository.get_active()

    def list_models(self, brand_id: uuid.UUID):
        """FR-001-002: all active Models for a Brand. Raises VehicleNotFoundError (VAL001) if brand_id doesn't resolve."""
        brand = self._brand_repository.get_by_id(brand_id)
        if brand is None:
            raise VehicleNotFoundError(f"Brand {brand_id} not found.")
        return self._model_repository.get_active_by_brand(brand_id)

    def list_variants(self, model_id: uuid.UUID):
        """FR-001-003: all active Variants for a Model. Raises VehicleNotFoundError (VAL001) if model_id doesn't resolve."""
        model = self._model_repository.get_by_id(model_id)
        if model is None:
            raise VehicleNotFoundError(f"Model {model_id} not found.")
        return self._variant_repository.get_active_by_model(model_id)

    def get_configuration(
        self, year: int, brand_id: uuid.UUID, model_id: uuid.UUID, variant_id: uuid.UUID
    ) -> Configuration:
        """
        FR-001-004/FR-001-005: resolve the Active ValuationMaster
        configuration for a Year+Variant.

        ``brand_id``/``model_id`` are validated for referential
        correctness (they must actually be the Variant's ancestry) but
        do not affect the lookup itself - only ``year`` + ``variant_id``
        key the ValuationMaster row (ISP-001 §1.4).
        """
        brand = self._brand_repository.get_by_id(brand_id)
        if brand is None:
            raise VehicleNotFoundError(f"Brand {brand_id} not found.")

        model = self._model_repository.get_by_id(model_id)
        if model is None or model.brand_id != brand_id:
            raise VehicleNotFoundError(
                f"Model {model_id} not found under Brand {brand_id}."
            )

        variant = self._variant_repository.get_by_id(variant_id)
        if variant is None or variant.model_id != model_id:
            raise VariantMissingError(
                f"Variant {variant_id} not found under Model {model_id}."
            )
        if not variant.active:
            # E-CATALOG-002 (SDD-000 §8): Deprecated Variant blocked for new evaluations.
            raise DeprecatedVariantError(f"Variant {variant_id} is deprecated.")

        valuation_master = self._valuation_master_repository.get_active_by_year_variant(
            year, variant_id
        )
        if valuation_master is None:
            # VAL003 / E-PRICING-001 (BR-0005): no pricing, block evaluation.
            raise PricingNotAvailableError(
                f"No Active ValuationMaster for Year={year}, Variant={variant_id}."
            )

        return Configuration(
            valuation_master_id=valuation_master.id,
            year=year,
            variant_id=variant_id,
            minimum_selling_price=valuation_master.minimum_selling_price,
            margin=valuation_master.margin,
            scrap_value=valuation_master.scrap_value,
            repair_options=[],  # Repair Master not implemented anywhere yet.
        )
