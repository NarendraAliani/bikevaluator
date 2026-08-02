# Full Path: src/vehicle_master/authorization.py
# Relative Path: authorization.py
# Module: vehicle_master
# Purpose: BR-0004 (Super-Admin-only writes) enforcement for VehicleMasterAdminService.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: BRR-001 BR-0004, SDD-000 §8 (E-AUTHZ-001), SSD-001 §8
#   ("AuthorizationPolicy" domain policy placeholder), ISP-001 §4.2
"""
BR-0004 enforcement, as SSD-001 §8's ``AuthorizationPolicy`` placeholder
(one central check, never inline per-endpoint - RISK-ADR-01, AI-0005).

ARCHITECTURE OBSERVATION (IMP-001B): FS-003 (Authentication) has not
been implemented yet - there is no real ``users`` table/model with a
``role`` column (SEC-0001) wired into this codebase. ``Actor`` below is
therefore a structural (duck-typed) protocol, not a Django model FK -
any object with ``id`` and ``role`` attributes satisfies it (e.g. a
plain ``types.SimpleNamespace`` in tests today, and presumably a real
Authentication-provided user object once FS-003 exists). This file adds
one new module file beyond EP-001's original inventory, which did not
anticipate needing this collaborator to be its own file.
"""

import uuid
from typing import Protocol

from vehicle_master.exceptions import NotAuthorizedError

SUPER_ADMIN_ROLE = "super_admin"


class Actor(Protocol):
    """Structural protocol for 'whoever is making this write' (see module docstring)."""

    id: uuid.UUID
    role: str


def enforce_super_admin(actor: Actor) -> None:
    """
    Enforce BR-0004: only ``super_admin`` may write Vehicle Master
    catalog/pricing data.

    :raises NotAuthorizedError: if ``actor.role`` is not
        ``"super_admin"`` - maps to E-AUTHZ-001 (SDD-000 §8).
    """
    if getattr(actor, "role", None) != SUPER_ADMIN_ROLE:
        raise NotAuthorizedError(
            "Only a super_admin account may perform this write (BR-0004)."
        )
