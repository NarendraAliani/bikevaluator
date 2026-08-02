# Full Path: src/vehicle_master/services/vehicle_master_admin_service.py
# Relative Path: services/vehicle_master_admin_service.py
# Module: vehicle_master
# Purpose: Super-Admin-facing Vehicle Master write business logic.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §4.2, BRR-001 BR-0004/BR-0007/BR-0011,
#   DBD-001 §6a (Transaction Boundaries), EP-001 §2
"""
``VehicleMasterAdminService`` - implemented (IMP-001B).

Every method: enforces BR-0004 first (``authorization.
enforce_super_admin``), then applies duplicate detection (BR-0011 /
E-CATALOG-001) or delegates versioning/concurrency mechanics to
``ValuationMasterRepository`` (already implemented in IMP-001A), then
writes exactly one ``AuditLogRepository`` entry. For ``ValuationMaster``
writes, the repository call and the audit write share **one**
``transaction.atomic()`` block (ENG-0003, DBD-001 §6a) - the repository
method's own internal atomic block nests inside it via Django
savepoints, so both are truly one transaction together.

ARCHITECTURE OBSERVATION: every write method takes an explicit
``ip_address: str`` parameter for the audit trail. ISP-001 §4.2's
original signatures did not include this - it was implicit that a
future View/middleware layer would supply it. Since no View layer
exists yet, threading it explicitly here is the only way to keep
``AuditLogRepository.create()``'s existing (IMP-001A) contract
satisfied without inventing a request-context mechanism prematurely.
"""

import uuid
from decimal import Decimal
from typing import Optional

from django.db import transaction

from vehicle_master.authorization import Actor, enforce_super_admin
from vehicle_master.exceptions import DuplicateCatalogEntryError, VehicleNotFoundError
from vehicle_master.repositories import (
    AuditLogRepository,
    BrandRepository,
    ModelRepository,
    ValuationMasterRepository,
    VariantRepository,
)
from vehicle_master.validators import validate_catalog_name, validate_non_negative_amount


class VehicleMasterAdminService:
    """Super-Admin-facing, write service (ISP-001 §4.2)."""

    def __init__(
        self,
        brand_repository: BrandRepository,
        model_repository: ModelRepository,
        variant_repository: VariantRepository,
        valuation_master_repository: ValuationMasterRepository,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        self._brand_repository = brand_repository
        self._model_repository = model_repository
        self._variant_repository = variant_repository
        self._valuation_master_repository = valuation_master_repository
        self._audit_log_repository = audit_log_repository

    # --- Brand ---------------------------------------------------------

    def create_brand(self, name: str, actor: Actor, ip_address: str):
        """FR-001-006/007/011: create a Brand. Duplicate name -> E-CATALOG-001 (BR-0011's sibling rule for catalog entries)."""
        enforce_super_admin(actor)
        validate_catalog_name(name)
        if self._brand_repository.name_exists(name):
            raise DuplicateCatalogEntryError(f"An active Brand named '{name}' already exists.")
        with transaction.atomic():
            brand = self._brand_repository.create(name)
            self._audit_log_repository.create(
                actor_id=actor.id,
                entity_type="Brand",
                entity_id=brand.id,
                old_value=None,
                new_value={"brand_name": name},
                ip_address=ip_address,
            )
        return brand

    def update_brand(self, brand_id: uuid.UUID, name: str, actor: Actor, ip_address: str):
        """FR-001-006/011: rename a Brand."""
        enforce_super_admin(actor)
        validate_catalog_name(name)
        brand = self._brand_repository.get_by_id(brand_id)
        if brand is None:
            raise VehicleNotFoundError(f"Brand {brand_id} not found.")
        if self._brand_repository.name_exists(name, exclude_id=brand_id):
            raise DuplicateCatalogEntryError(f"An active Brand named '{name}' already exists.")
        old_name = brand.brand_name
        with transaction.atomic():
            updated = self._brand_repository.update(brand_id, name)
            self._audit_log_repository.create(
                actor_id=actor.id,
                entity_type="Brand",
                entity_id=brand_id,
                old_value={"brand_name": old_name},
                new_value={"brand_name": name},
                ip_address=ip_address,
            )
        return updated

    def deactivate_brand(self, brand_id: uuid.UUID, actor: Actor, ip_address: str) -> None:
        """FR-001-006/011: soft-deactivate a Brand (DBD-001 §5 - no hard delete)."""
        enforce_super_admin(actor)
        brand = self._brand_repository.get_by_id(brand_id)
        if brand is None:
            raise VehicleNotFoundError(f"Brand {brand_id} not found.")
        with transaction.atomic():
            self._brand_repository.deactivate(brand_id)
            self._audit_log_repository.create(
                actor_id=actor.id,
                entity_type="Brand",
                entity_id=brand_id,
                old_value={"active": True},
                new_value={"active": False},
                ip_address=ip_address,
            )

    # --- Model -----------------------------------------------------------

    def create_model(
        self, brand_id: uuid.UUID, name: str, actor: Actor, ip_address: str
    ):
        """Same pattern as create_brand, scoped to a parent Brand."""
        enforce_super_admin(actor)
        validate_catalog_name(name)
        if self._brand_repository.get_by_id(brand_id) is None:
            raise VehicleNotFoundError(f"Brand {brand_id} not found.")
        if self._model_repository.name_exists(brand_id, name):
            raise DuplicateCatalogEntryError(
                f"An active Model named '{name}' already exists under this Brand."
            )
        with transaction.atomic():
            model = self._model_repository.create(brand_id, name)
            self._audit_log_repository.create(
                actor_id=actor.id,
                entity_type="Model",
                entity_id=model.id,
                old_value=None,
                new_value={"model_name": name, "brand_id": str(brand_id)},
                ip_address=ip_address,
            )
        return model

    def update_model(self, model_id: uuid.UUID, name: str, actor: Actor, ip_address: str):
        """Same pattern as update_brand."""
        enforce_super_admin(actor)
        validate_catalog_name(name)
        model = self._model_repository.get_by_id(model_id)
        if model is None:
            raise VehicleNotFoundError(f"Model {model_id} not found.")
        if self._model_repository.name_exists(model.brand_id, name, exclude_id=model_id):
            raise DuplicateCatalogEntryError(
                f"An active Model named '{name}' already exists under this Brand."
            )
        old_name = model.model_name
        with transaction.atomic():
            updated = self._model_repository.update(model_id, name)
            self._audit_log_repository.create(
                actor_id=actor.id,
                entity_type="Model",
                entity_id=model_id,
                old_value={"model_name": old_name},
                new_value={"model_name": name},
                ip_address=ip_address,
            )
        return updated

    def deactivate_model(self, model_id: uuid.UUID, actor: Actor, ip_address: str) -> None:
        """Same pattern as deactivate_brand."""
        enforce_super_admin(actor)
        if self._model_repository.get_by_id(model_id) is None:
            raise VehicleNotFoundError(f"Model {model_id} not found.")
        with transaction.atomic():
            self._model_repository.deactivate(model_id)
            self._audit_log_repository.create(
                actor_id=actor.id,
                entity_type="Model",
                entity_id=model_id,
                old_value={"active": True},
                new_value={"active": False},
                ip_address=ip_address,
            )

    # --- Variant ---------------------------------------------------------

    def create_variant(
        self, model_id: uuid.UUID, name: str, actor: Actor, ip_address: str
    ):
        """Same pattern as create_brand, scoped to a parent Model."""
        enforce_super_admin(actor)
        validate_catalog_name(name)
        if self._model_repository.get_by_id(model_id) is None:
            raise VehicleNotFoundError(f"Model {model_id} not found.")
        if self._variant_repository.name_exists(model_id, name):
            raise DuplicateCatalogEntryError(
                f"An active Variant named '{name}' already exists under this Model."
            )
        with transaction.atomic():
            variant = self._variant_repository.create(model_id, name)
            self._audit_log_repository.create(
                actor_id=actor.id,
                entity_type="Variant",
                entity_id=variant.id,
                old_value=None,
                new_value={"variant_name": name, "model_id": str(model_id)},
                ip_address=ip_address,
            )
        return variant

    def update_variant(
        self, variant_id: uuid.UUID, name: str, actor: Actor, ip_address: str
    ):
        """Same pattern as update_brand."""
        enforce_super_admin(actor)
        validate_catalog_name(name)
        variant = self._variant_repository.get_by_id(variant_id)
        if variant is None:
            raise VehicleNotFoundError(f"Variant {variant_id} not found.")
        if self._variant_repository.name_exists(
            variant.model_id, name, exclude_id=variant_id
        ):
            raise DuplicateCatalogEntryError(
                f"An active Variant named '{name}' already exists under this Model."
            )
        old_name = variant.variant_name
        with transaction.atomic():
            updated = self._variant_repository.update(variant_id, name)
            self._audit_log_repository.create(
                actor_id=actor.id,
                entity_type="Variant",
                entity_id=variant_id,
                old_value={"variant_name": old_name},
                new_value={"variant_name": name},
                ip_address=ip_address,
            )
        return updated

    def deactivate_variant(
        self, variant_id: uuid.UUID, actor: Actor, ip_address: str
    ) -> None:
        """Same pattern as deactivate_brand."""
        enforce_super_admin(actor)
        if self._variant_repository.get_by_id(variant_id) is None:
            raise VehicleNotFoundError(f"Variant {variant_id} not found.")
        with transaction.atomic():
            self._variant_repository.deactivate(variant_id)
            self._audit_log_repository.create(
                actor_id=actor.id,
                entity_type="Variant",
                entity_id=variant_id,
                old_value={"active": True},
                new_value={"active": False},
                ip_address=ip_address,
            )

    # --- ValuationMaster ---------------------------------------------------

    def create_valuation_master_version(
        self,
        year: int,
        variant_id: uuid.UUID,
        minimum_selling_price: Decimal,
        margin: Decimal,
        scrap_value: Decimal,
        expected_previous_updated_at: Optional[object],
        actor: Actor,
        ip_address: str,
    ):
        """
        FR-001-008/009/011/012: create a new pricing version (BR-0007),
        enforcing BR-0011 uniqueness and ENG-0003 optimistic concurrency
        via ``ValuationMasterRepository.create_new_version`` (already
        implemented, IMP-001A) - this method adds BR-0004 authorization,
        field validation, and the atomic audit write around it.
        """
        enforce_super_admin(actor)
        validate_non_negative_amount(minimum_selling_price)
        validate_non_negative_amount(margin)
        validate_non_negative_amount(scrap_value)

        if self._variant_repository.get_by_id(variant_id) is None:
            raise VehicleNotFoundError(f"Variant {variant_id} not found.")

        with transaction.atomic():
            valuation_master = self._valuation_master_repository.create_new_version(
                year=year,
                variant_id=variant_id,
                minimum_selling_price=minimum_selling_price,
                margin=margin,
                scrap_value=scrap_value,
                expected_previous_updated_at=expected_previous_updated_at,
            )
            self._audit_log_repository.create(
                actor_id=actor.id,
                entity_type="ValuationMaster",
                entity_id=valuation_master.id,
                old_value=None,
                new_value={
                    "year": year,
                    "variant_id": str(variant_id),
                    "minimum_selling_price": str(minimum_selling_price),
                    "margin": str(margin),
                    "scrap_value": str(scrap_value),
                },
                ip_address=ip_address,
            )
        return valuation_master

    def deactivate_valuation_master(
        self, valuation_master_id: uuid.UUID, actor: Actor, ip_address: str
    ) -> None:
        """FR-001-011: retire a ValuationMaster row entirely (no new version created)."""
        enforce_super_admin(actor)
        if self._valuation_master_repository.get_by_id(valuation_master_id) is None:
            raise VehicleNotFoundError(f"ValuationMaster {valuation_master_id} not found.")
        with transaction.atomic():
            self._valuation_master_repository.deactivate(valuation_master_id)
            self._audit_log_repository.create(
                actor_id=actor.id,
                entity_type="ValuationMaster",
                entity_id=valuation_master_id,
                old_value={"active": True},
                new_value={"active": False},
                ip_address=ip_address,
            )
