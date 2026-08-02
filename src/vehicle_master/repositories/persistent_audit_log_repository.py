# Full Path: src/vehicle_master/repositories/persistent_audit_log_repository.py
# Relative Path: repositories/persistent_audit_log_repository.py
# Module: vehicle_master
# Purpose: Real, DB-backed AuditLogRepository implementation (IMP-003B
#   Task 2), replacing NoOpAuditRepository as service_factory's default.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: DBD-001 §2, IMP-003B Task 2, audit_context.py
import uuid
from typing import Optional

from vehicle_master.audit_context import get_correlation_id, get_request_id
from vehicle_master.models import AuditLog
from vehicle_master.repositories.audit_log_repository import AuditLogRepository


def _infer_action(old_value: Optional[dict], new_value: Optional[dict]) -> str:
    """Best-effort action label when the caller doesn't pass one explicitly."""
    if old_value is None and new_value is not None:
        return "CREATE"
    if old_value is not None and new_value is None:
        return "DEACTIVATE"
    if old_value is not None and new_value is not None:
        return "UPDATE"
    return "UNKNOWN"


class PersistentAuditLogRepository(AuditLogRepository):
    """Writes every audit entry to the ``audit_logs`` table - never discards one."""

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
        AuditLog.objects.create(
            actor_id=actor_id,
            action=action or _infer_action(old_value, new_value),
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            correlation_id=correlation_id or get_correlation_id(),
            request_id=request_id or get_request_id(),
            success=success,
            error_message=error_message,
        )
