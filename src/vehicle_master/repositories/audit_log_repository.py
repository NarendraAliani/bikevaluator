# Full Path: src/vehicle_master/repositories/audit_log_repository.py
# Relative Path: repositories/audit_log_repository.py
# Module: vehicle_master
# Purpose: Abstract interface for audit-log persistence, consumed by
#   VehicleMasterAdminService via dependency injection. No concrete
#   implementation - the Audit module itself is out of scope here.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: ISP-001 §3 (AuditLogRepository contract), EP-001 §2
#   (common/audit app - not implemented in this prompt, per its explicit
#   "Do not implement Audit module. Use interface only." instruction),
#   DBD-001 §2 (Audit Logs table)
"""
Abstract ``AuditLogRepository`` interface.

ARCHITECTURE OBSERVATION: EP-001 §2 planned this interface's concrete
implementation in a shared ``common/audit`` Django app (since
``audit_logs`` is cross-module, not Vehicle-Master-specific per
DBD-001 §2). IMP-001A-D only implemented the abstract contract plus a
``NoOpAuditRepository`` stand-in. IMP-003B (Task 2, "Real Audit
Repository") adds the first concrete, persistent implementation
(``PersistentAuditLogRepository``) - still inside ``vehicle_master``
for minimal footprint, not yet moved to a ``common/audit`` app. A
future prompt should still do that move per EP-001 §2.

IMP-003B extends this signature with four optional, keyword-only
fields (``action``, ``correlation_id``, ``request_id``, ``success``,
``error_message``) rather than changing the five original positional
parameters - every existing call site in
``VehicleMasterAdminService`` (11 methods) continues to work
completely unchanged; only the concrete implementation's behavior
changed, per this round's explicit "do not redesign architecture,
only improve engineering quality" instruction.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Optional


class AuditLogRepository(ABC):
    """Persistence contract for writing audit-trail entries (DBD-001 §2)."""

    @abstractmethod
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
        """
        Persist one audit-trail entry.

        :param actor_id: id of the Super Admin who performed the write.
        :param entity_type: e.g. ``"Brand"``, ``"ValuationMaster"``.
        :param entity_id: id of the entity that was changed.
        :param old_value: prior field values, or ``None`` on create.
        :param new_value: new field values, or ``None`` on deactivate.
        :param ip_address: request-origin IP address.
        :param action: e.g. ``"CREATE"``/``"UPDATE"``/``"DEACTIVATE"``.
            If omitted, a concrete implementation may infer it from
            whether ``old_value``/``new_value`` are ``None``.
        :param correlation_id: groups every audit row from one logical
            operation (e.g. one importer run). Falls back to the
            ambient value set via ``audit_context`` if omitted.
        :param request_id: identifies one HTTP request/CLI invocation.
            Falls back to the ambient value set via ``audit_context``
            if omitted.
        :param success: whether the write this entry describes
            actually succeeded.
        :param error_message: populated only when ``success=False``.
        """
        raise NotImplementedError
