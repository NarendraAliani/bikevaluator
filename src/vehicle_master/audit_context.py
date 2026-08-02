# Full Path: src/vehicle_master/audit_context.py
# Relative Path: audit_context.py
# Module: vehicle_master
# Purpose: Ambient correlation_id/request_id for audit records, without
#   threading new parameters through every Service method signature.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: IMP-003B Task 2 (Real Audit Repository), LOG-001
#   (structured logging fields), RequestContext (already anticipated
#   these two fields, IMP-001D, but nothing populates them yet)
"""
``PersistentAuditLogRepository.create()`` (IMP-003B) needs a
correlation_id/request_id for every audit row, but
``VehicleMasterAdminService``'s write methods (``create_brand`` etc.)
were not changed here - IMP-003B is a stabilization release, not an
architecture change, and threading two new parameters through eleven
existing method signatures would be exactly that.

Instead, both IDs are ambient (Python ``contextvars``), set once at the
top of a logical unit of work (one HTTP request via
``RequestIdMiddleware``, or one importer run via ``audit_run_context``)
and read automatically by the audit repository if not explicitly
passed. No existing call site needs to change.
"""

import uuid
from contextlib import contextmanager
from typing import Optional
from contextvars import ContextVar, Token

_correlation_id_var: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
_request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def set_correlation_id(value: Optional[str]) -> Token:
    return _correlation_id_var.set(value)


def get_correlation_id() -> Optional[str]:
    return _correlation_id_var.get()


def reset_correlation_id(token: Token) -> None:
    _correlation_id_var.reset(token)


def set_request_id(value: Optional[str]) -> Token:
    return _request_id_var.set(value)


def get_request_id() -> Optional[str]:
    return _request_id_var.get()


def reset_request_id(token: Token) -> None:
    _request_id_var.reset(token)


@contextmanager
def audit_run_context(correlation_id: Optional[str] = None, request_id: Optional[str] = None):
    """
    Scope one correlation_id/request_id pair for the duration of a
    logical unit of work (e.g. one importer run). Every audit record
    created inside this block picks up these values automatically.
    """
    correlation_id = correlation_id or str(uuid.uuid4())
    request_id = request_id or correlation_id
    correlation_token = set_correlation_id(correlation_id)
    request_token = set_request_id(request_id)
    try:
        yield correlation_id
    finally:
        reset_correlation_id(correlation_token)
        reset_request_id(request_token)
