# Full Path: src/vehicle_master/repositories/variant_repository.py
# Relative Path: repositories/variant_repository.py
# Module: vehicle_master
# Purpose: Persistence-only repository for the Variant model.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §3 (VariantRepository contract), DBD-001 §2
"""
Persistence-only repository for ``Variant`` (DBD-001 §2). Implements
the contract ISP-001 §3 defined. Contains no business rules.
"""

import uuid
from typing import Optional

from vehicle_master.models import Variant


class VariantRepository:
    """CRUD persistence for ``Variant`` rows, scoped by parent Model. No business rules."""

    def get_active_by_model(self, model_id: uuid.UUID) -> list[Variant]:
        """Return all active Variants for a given Model (FR-001-003)."""
        return list(
            Variant.objects.filter(model_id=model_id, active=True).order_by(
                "variant_name"
            )
        )

    def get_by_id(self, variant_id: uuid.UUID) -> Optional[Variant]:
        """Return a single Variant by id, or ``None`` if not found."""
        return Variant.objects.filter(id=variant_id).first()

    def name_exists(
        self, model_id: uuid.UUID, variant_name: str, exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Return ``True`` if an active Variant with this name already exists under the Model."""
        queryset = Variant.objects.filter(
            model_id=model_id, variant_name=variant_name, active=True
        )
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()

    def get_by_name(self, model_id: uuid.UUID, variant_name: str) -> Optional[Variant]:
        """Return a single active Variant by exact name under a Model, or ``None`` (IMP-003's importer)."""
        return Variant.objects.filter(
            model_id=model_id, variant_name=variant_name, active=True
        ).first()

    def create(self, model_id: uuid.UUID, variant_name: str) -> Variant:
        """Persist a new Variant row under the given Model."""
        return Variant.objects.create(model_id=model_id, variant_name=variant_name)

    def update(self, variant_id: uuid.UUID, variant_name: str) -> Variant:
        """Update an existing Variant's name."""
        variant = Variant.objects.get(id=variant_id)
        variant.variant_name = variant_name
        variant.save(update_fields=["variant_name", "updated_at"])
        return variant

    def deactivate(self, variant_id: uuid.UUID) -> None:
        """Soft-deactivate a Variant (``active=False``) - no hard delete (DBD-001 §5)."""
        Variant.objects.filter(id=variant_id).update(active=False)
