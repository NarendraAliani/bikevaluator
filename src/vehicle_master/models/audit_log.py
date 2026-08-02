# Full Path: src/vehicle_master/models/audit_log.py
# Relative Path: models/audit_log.py
# Module: vehicle_master
# Purpose: Django ORM model for AuditLog - the persistent record behind
#   PersistentAuditLogRepository (IMP-003B Task 2, replacing NoOpAuditRepository).
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: DBD-001 §2 (Audit Logs table), IMP-003B Task 2,
#   audit_log_repository.py's own Architecture Observation
"""
DBD-001 §2 and ``audit_log_repository.py``'s own docstring both note
that the Audit module ideally belongs in a future shared ``common/
audit`` Django app, since ``audit_logs`` is cross-module, not
Vehicle-Master-specific. IMP-003B is a stabilization release, not an
architecture change - this model is added directly to ``vehicle_master``
for minimal footprint (the same pragmatic call EP-002 made for
RepairComponent/RepairOption over a separate app), flagged again here
rather than silently resolved. A future prompt should move this to
``common/audit/`` per that plan.
"""
import uuid

from django.db import models


class AuditLog(models.Model):
    """One immutable audit-trail entry (DBD-001 §2)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    actor_id = models.UUIDField()
    action = models.CharField(max_length=30)
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField()
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    ip_address = models.CharField(max_length=64)
    correlation_id = models.CharField(max_length=64, null=True, blank=True)
    request_id = models.CharField(max_length=64, null=True, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["entity_type", "entity_id"], name="idx_auditlog_entity"),
            models.Index(fields=["correlation_id"], name="idx_auditlog_correlation"),
            models.Index(fields=["timestamp"], name="idx_auditlog_timestamp"),
        ]

    def __str__(self) -> str:
        return f"AuditLog({self.action} {self.entity_type}:{self.entity_id} @ {self.timestamp})"
