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
DBD-001 §2). This prompt explicitly instructs "Do not implement Audit
module. Use interface only" - so only the abstract contract lives
here, temporarily inside ``vehicle_master.repositories``, purely so
``VehicleMasterAdminService`` has a type to depend on (dependency
injection). No ``common`` app, no ``audit_logs`` table/migration, and
no concrete implementation exist yet. A future prompt should create
``common/audit/`` per EP-001 §2 and move/re-export this interface from
there instead.
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
    ) -> None:
        """
        Persist one audit-trail entry.

        :param actor_id: id of the Super Admin who performed the write.
        :param entity_type: e.g. ``"Brand"``, ``"ValuationMaster"``.
        :param entity_id: id of the entity that was changed.
        :param old_value: prior field values, or ``None`` on create.
        :param new_value: new field values, or ``None`` on deactivate.
        :param ip_address: request-origin IP address.
        """
        raise NotImplementedError
