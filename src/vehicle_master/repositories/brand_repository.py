# Full Path: src/vehicle_master/repositories/brand_repository.py
# Relative Path: repositories/brand_repository.py
# Module: vehicle_master
# Purpose: Persistence-only repository for the Brand model.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §3 (BrandRepository contract), DBD-001 §2
"""
Persistence-only repository for ``Brand`` (DBD-001 §2, "Vehicle
Master"). Implements the contract ISP-001 §3 defined. Contains no
business rules - e.g. duplicate-name rejection is a Service-layer
concern (ISP-001 FR-001-007 / E-CATALOG-001), never enforced here.
"""

import uuid
from typing import Optional

from vehicle_master.models import Brand


class BrandRepository:
    """CRUD persistence for ``Brand`` rows. No validation, no business rules."""

    def get_active(self) -> list[Brand]:
        """Return all Brands with ``active=True`` (FR-001-001)."""
        return list(Brand.objects.filter(active=True).order_by("brand_name"))

    def get_by_id(self, brand_id: uuid.UUID) -> Optional[Brand]:
        """Return a single Brand by id, or ``None`` if not found."""
        return Brand.objects.filter(id=brand_id).first()

    def name_exists(self, brand_name: str, exclude_id: Optional[uuid.UUID] = None) -> bool:
        """Return ``True`` if an active Brand with this name already exists."""
        queryset = Brand.objects.filter(brand_name=brand_name, active=True)
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()

    def create(self, brand_name: str) -> Brand:
        """Persist a new Brand row. No validation performed here (Service layer's job)."""
        return Brand.objects.create(brand_name=brand_name)

    def update(self, brand_id: uuid.UUID, brand_name: str) -> Brand:
        """Update an existing Brand's name."""
        brand = Brand.objects.get(id=brand_id)
        brand.brand_name = brand_name
        brand.save(update_fields=["brand_name", "updated_at"])
        return brand

    def deactivate(self, brand_id: uuid.UUID) -> None:
        """Soft-deactivate a Brand (``active=False``) - no hard delete (DBD-001 §5)."""
        Brand.objects.filter(id=brand_id).update(active=False)
