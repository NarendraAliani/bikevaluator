# Full Path: src/vehicle_master/repositories/model_repository.py
# Relative Path: repositories/model_repository.py
# Module: vehicle_master
# Purpose: Persistence-only repository for the Model model.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §3 (ModelRepository contract), DBD-001 §2
"""
Persistence-only repository for ``Model`` (DBD-001 §2). Implements the
contract ISP-001 §3 defined. Contains no business rules.
"""

import uuid
from typing import Optional

from vehicle_master.models import Model


class ModelRepository:
    """CRUD persistence for ``Model`` rows, scoped by parent Brand. No business rules."""

    def get_active_by_brand(self, brand_id: uuid.UUID) -> list[Model]:
        """Return all active Models for a given Brand (FR-001-002)."""
        return list(
            Model.objects.filter(brand_id=brand_id, active=True).order_by("model_name")
        )

    def get_by_id(self, model_id: uuid.UUID) -> Optional[Model]:
        """Return a single Model by id, or ``None`` if not found."""
        return Model.objects.filter(id=model_id).first()

    def name_exists(
        self, brand_id: uuid.UUID, model_name: str, exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Return ``True`` if an active Model with this name already exists under the Brand."""
        queryset = Model.objects.filter(
            brand_id=brand_id, model_name=model_name, active=True
        )
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()

    def get_by_name(self, brand_id: uuid.UUID, model_name: str) -> Optional[Model]:
        """Return a single active Model by exact name under a Brand, or ``None`` (IMP-003's importer)."""
        return Model.objects.filter(
            brand_id=brand_id, model_name=model_name, active=True
        ).first()

    def create(self, brand_id: uuid.UUID, model_name: str) -> Model:
        """Persist a new Model row under the given Brand."""
        return Model.objects.create(brand_id=brand_id, model_name=model_name)

    def update(self, model_id: uuid.UUID, model_name: str) -> Model:
        """Update an existing Model's name."""
        model = Model.objects.get(id=model_id)
        model.model_name = model_name
        model.save(update_fields=["model_name", "updated_at"])
        return model

    def deactivate(self, model_id: uuid.UUID) -> None:
        """Soft-deactivate a Model (``active=False``) - no hard delete (DBD-001 §5)."""
        Model.objects.filter(id=model_id).update(active=False)
