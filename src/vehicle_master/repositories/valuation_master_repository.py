# Full Path: src/vehicle_master/repositories/valuation_master_repository.py
# Relative Path: repositories/valuation_master_repository.py
# Module: vehicle_master
# Purpose: Persistence-only repository for ValuationMaster, including
#   BR-0007 versioning and ENG-0003 optimistic concurrency.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §3 (ValuationMasterRepository contract),
#   DBD-001 §6/§6a (versioning, transaction & concurrency policy),
#   BRR-001 BR-0007/BR-0011
"""
Persistence-only repository for ``ValuationMaster``. Implements the
contract ISP-001 §3 defined.

``create_new_version`` embeds the *mechanics* of BR-0007 versioning and
ENG-0003 optimistic concurrency (this is how a write is done correctly
- persistence logic), but does not decide *whether* a write should
happen (that policy call belongs to ``VehicleMasterAdminService`` -
this is why the method still exists here rather than in the service:
ISP-001 already specified this exact contract at the repository layer).
"""

import uuid
from decimal import Decimal
from typing import Optional

from django.db import IntegrityError, transaction
from django.utils import timezone

from vehicle_master.exceptions import ConcurrencyConflictError, DuplicateCatalogEntryError
from vehicle_master.models import ValuationMaster


class ValuationMasterRepository:
    """CRUD + versioning persistence for ``ValuationMaster`` rows."""

    def get_active_by_year_variant(
        self, year: int, variant_id: uuid.UUID
    ) -> Optional[ValuationMaster]:
        """Return the Active ValuationMaster row for a Year+Variant, or ``None``."""
        return ValuationMaster.objects.filter(
            year=year, variant_id=variant_id, active=True
        ).first()

    def get_by_id(self, valuation_master_id: uuid.UUID) -> Optional[ValuationMaster]:
        """Return a single ValuationMaster row by id, or ``None`` if not found."""
        return ValuationMaster.objects.filter(id=valuation_master_id).first()

    def get_version_history(
        self, year: int, variant_id: uuid.UUID
    ) -> list[ValuationMaster]:
        """Return every version (Active and superseded) for a Year+Variant, newest first."""
        return list(
            ValuationMaster.objects.filter(year=year, variant_id=variant_id).order_by(
                "-effective_from"
            )
        )

    def create_new_version(
        self,
        year: int,
        variant_id: uuid.UUID,
        minimum_selling_price: Decimal,
        margin: Decimal,
        scrap_value: Decimal,
        expected_previous_updated_at,
    ) -> ValuationMaster:
        """
        Close the current Active row's ``effective_to`` and insert a
        new Active row, atomically (BR-0007, ENG-0003, DBD-001 §6a).

        :param expected_previous_updated_at: the ``updated_at`` value
            the caller last observed on the current Active row, or
            ``None`` when creating the very first version for this
            Year+Variant (ISP-001 §2.3).
        :raises ConcurrencyConflictError: if a current Active row
            exists and its ``updated_at`` no longer matches
            ``expected_previous_updated_at`` (someone else wrote to it
            first).
        :raises DuplicateCatalogEntryError: if the database's partial
            unique index (``uniq_active_valmaster_year_variant``,
            BR-0011) is violated despite the above check (defense in
            depth against a race condition).
        """
        now = timezone.now()
        with transaction.atomic():
            current = ValuationMaster.objects.filter(
                year=year, variant_id=variant_id, active=True
            ).first()

            if current is not None:
                if expected_previous_updated_at is None or (
                    current.updated_at != expected_previous_updated_at
                ):
                    raise ConcurrencyConflictError(
                        "The current ValuationMaster row for this Year+Variant "
                        "has changed since it was last read; reload before retrying."
                    )
                updated_rows = ValuationMaster.objects.filter(
                    id=current.id, updated_at=expected_previous_updated_at
                ).update(active=False, effective_to=now)
                if updated_rows == 0:
                    # Someone else won the race between our read above
                    # and this write - same outcome as the check above.
                    raise ConcurrencyConflictError(
                        "The current ValuationMaster row for this Year+Variant "
                        "was modified concurrently; reload before retrying."
                    )

            try:
                return ValuationMaster.objects.create(
                    year=year,
                    variant_id=variant_id,
                    minimum_selling_price=minimum_selling_price,
                    margin=margin,
                    scrap_value=scrap_value,
                    active=True,
                    effective_from=now,
                )
            except IntegrityError as exc:
                # Defense in depth: the partial unique index
                # (BR-0011) rejects a second Active row for the same
                # Year+Variant if one slipped through the check above.
                raise DuplicateCatalogEntryError(
                    "An Active ValuationMaster row already exists for this "
                    "Year+Variant (BR-0011)."
                ) from exc

    def deactivate(self, valuation_master_id: uuid.UUID) -> None:
        """Soft-deactivate a ValuationMaster row (retire pricing entirely, no new version)."""
        ValuationMaster.objects.filter(id=valuation_master_id).update(active=False)
