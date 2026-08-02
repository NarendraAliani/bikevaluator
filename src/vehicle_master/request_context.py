# Full Path: src/vehicle_master/request_context.py
# Relative Path: request_context.py
# Module: vehicle_master
# Purpose: RequestContext value object bundling per-request metadata
#   (actor, IP, request/correlation IDs) for views to pass to services.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: LOG-001 (structured logging fields, incl.
#   correlation_id), API-000 (a future correlation-id addition is
#   already anticipated there), IMP-001C (threaded actor/ip_address as
#   two separate parameters), IMP-001D (this refactor - bundles them,
#   per architect review)
"""
``RequestContext`` (IMP-001D refactor).

IMP-001C threaded ``actor`` and ``ip_address`` as two separate
parameters on every Service write method. This bundles them into one
value object, with room for fields no view populates yet
(``request_id``, ``correlation_id``) - LOG-001 already anticipates a
correlation_id addition; this gives it a home without inventing that
decision now. Both new fields default to ``None`` until something
actually sets them - no behavior change from IMP-001C.
"""

from dataclasses import dataclass
from typing import Optional

from vehicle_master.actor_provider import ActorProvider
from vehicle_master.authorization import Actor


@dataclass
class RequestContext:
    """Per-request metadata a view assembles once and passes to a Service method."""

    actor: Actor
    ip_address: str
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None


def build_request_context(request, actor_provider: ActorProvider) -> RequestContext:
    """Assemble a ``RequestContext`` for the given Django/DRF ``request``."""
    return RequestContext(
        actor=actor_provider.get_actor(request),
        ip_address=request.META.get("REMOTE_ADDR", "") or "",
    )
