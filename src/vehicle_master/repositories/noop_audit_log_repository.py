# Full Path: src/vehicle_master/repositories/noop_audit_log_repository.py
# Relative Path: repositories/noop_audit_log_repository.py
# Module: vehicle_master
# Purpose: No-op AuditLogRepository implementation used until the real
#   Audit module (a shared common/audit app) exists.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §3, EP-001 §2 (common/audit, not yet built),
#   IMP-001A/B/C (introduced this inline as _InMemoryAuditLogRepository
#   in admin_vehicle_views.py), IMP-001D (this refactor - relocated to
#   the repository layer per architect review)
"""
``NoOpAuditRepository`` (IMP-001D refactor).

IMP-001C defined this as ``_InMemoryAuditLogRepository`` directly inside
``admin_vehicle_views.py``, meaning a view module owned a persistence
concern. Per the architect's review, it is relocated here, where
``AuditLogRepository`` (the interface it implements) already lives -
views now depend on the repositories package for this, same as every
other repository, and know nothing about there being no real
implementation.

Still discards every entry (no persistence) - the real Audit module
(``common/audit``, per EP-001 §2) remains unbuilt. Swapping this for a
real implementation requires changing only ``service_factory.py``'s
default argument, not any view.
"""

import uuid
from typing import Optional

from vehicle_master.repositories.audit_log_repository import AuditLogRepository


class NoOpAuditRepository(AuditLogRepository):
    """Discards every audit entry - a placeholder until the real Audit module exists."""

    def create(
        self,
        actor_id: uuid.UUID,
        entity_type: str,
        entity_id: uuid.UUID,
        old_value: Optional[dict],
        new_value: Optional[dict],
        ip_address: str,
        *,
        action: Optional[str] = None,
        correlation_id: Optional[str] = None,
        request_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> None:
        return None
