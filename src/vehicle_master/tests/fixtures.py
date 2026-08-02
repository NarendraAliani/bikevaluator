# Full Path: src/vehicle_master/tests/fixtures.py
# Relative Path: tests/fixtures.py
# Module: vehicle_master
# Purpose: Shared test doubles - a fake AuditLogRepository and a fake
#   Actor - used across the service-layer test suite.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: TEST-001 ("no production dealer data in test
#   fixtures - synthetic ... only"), ISP-001 §4, IMP-001B
"""
Test doubles only - never imported by production code.

``FakeAuditLogRepository`` stands in for the real Audit module (still
not implemented anywhere in this codebase, per IMP-001A/B's explicit
"interface only" scope) so Service-layer tests can assert an audit
entry was recorded without a real ``audit_logs`` table existing yet.

``make_super_admin_actor``/``make_dealer_actor`` stand in for a real
Authentication-provided user (FS-003 not implemented yet) - see
``vehicle_master/authorization.py``'s Architecture Observation.
"""

import uuid
from types import SimpleNamespace
from typing import Optional

from vehicle_master.repositories import AuditLogRepository


class FakeAuditLogRepository(AuditLogRepository):
    """Records every call it receives, in memory, for test assertions."""

    def __init__(self) -> None:
        self.entries: list[dict] = []

    def create(
        self,
        actor_id: uuid.UUID,
        entity_type: str,
        entity_id: uuid.UUID,
        old_value: Optional[dict],
        new_value: Optional[dict],
        ip_address: str,
    ) -> None:
        self.entries.append(
            {
                "actor_id": actor_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "old_value": old_value,
                "new_value": new_value,
                "ip_address": ip_address,
            }
        )


def make_super_admin_actor():
    """A fake actor satisfying the `Actor` protocol with role='super_admin'."""
    return SimpleNamespace(id=uuid.uuid4(), role="super_admin")


def make_dealer_actor():
    """A fake actor satisfying the `Actor` protocol with role='dealer'."""
    return SimpleNamespace(id=uuid.uuid4(), role="dealer")
