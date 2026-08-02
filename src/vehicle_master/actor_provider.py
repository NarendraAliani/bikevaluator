# Full Path: src/vehicle_master/actor_provider.py
# Relative Path: actor_provider.py
# Module: vehicle_master
# Purpose: Abstraction for resolving the acting Actor from an HTTP request,
#   isolating the temporary header-based placeholder from views so FS-003
#   (Authentication) can swap in a real implementation without touching them.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: BRR-001 BR-0004, IMP-001C (introduced the header
#   placeholder inline in views), IMP-001D (this refactor - extracts it
#   behind an interface per architect review)
"""
``ActorProvider`` abstraction (IMP-001D refactor).

IMP-001C read ``X-Actor-Id``/``X-Actor-Role`` headers directly inside
``admin_vehicle_views.py``/``admin_valuation_master_views.py`` (via
``api_utils.get_actor_from_request``). Per the architect's review, this
coupled views to an authentication implementation detail that will
change once FS-003 exists. Views now depend on ``ActorProvider`` (this
interface) instead - swapping ``DummyActorProvider`` for a future
``AuthenticatedActorProvider`` (backed by FS-003's real session/token
mechanism) requires no view changes, only a different return value from
``build_actor_provider()`` below.

``DummyActorProvider`` is EXPLICITLY insecure - it trusts unverified
request headers with zero verification. This is unchanged behavior from
IMP-001C, only relocated behind an interface.
"""

import uuid
from abc import ABC, abstractmethod
from types import SimpleNamespace

from vehicle_master.authorization import Actor


class ActorProvider(ABC):
    """Resolves the ``Actor`` (see ``authorization.Actor``) performing the current request."""

    @abstractmethod
    def get_actor(self, request) -> Actor:
        raise NotImplementedError


class DummyActorProvider(ActorProvider):
    """
    Temporary, insecure ``ActorProvider`` reading unverified
    ``X-Actor-Id``/``X-Actor-Role`` headers - IMP-001C's original inline
    logic, unchanged, just relocated behind the interface. Must be
    replaced by an ``AuthenticatedActorProvider`` once FS-003
    (Authentication) exists.
    """

    def get_actor(self, request) -> Actor:
        actor_id_header = request.headers.get("X-Actor-Id")
        role_header = request.headers.get("X-Actor-Role")
        try:
            actor_id = uuid.UUID(actor_id_header) if actor_id_header else uuid.uuid4()
        except ValueError:
            actor_id = uuid.uuid4()
        return SimpleNamespace(id=actor_id, role=role_header)


def build_actor_provider() -> ActorProvider:
    """
    The one seam views depend on. Returns ``DummyActorProvider`` today;
    change only this function's body to ``AuthenticatedActorProvider()``
    once FS-003 exists - no view changes required.
    """
    return DummyActorProvider()
