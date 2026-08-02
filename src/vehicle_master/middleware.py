# Full Path: src/vehicle_master/middleware.py
# Relative Path: middleware.py
# Module: vehicle_master
# Purpose: Assigns a request_id to every HTTP request (from an
#   incoming X-Request-Id header, or a fresh UUID), for audit records
#   (IMP-003B Task 2) - no view code needs to change.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: IMP-003B Task 2 (Real Audit Repository), LOG-001
import uuid

from vehicle_master.audit_context import reset_request_id, set_request_id


class RequestIdMiddleware:
    """Sets an ambient request_id for the lifetime of one HTTP request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        token = set_request_id(request_id)
        try:
            response = self.get_response(request)
        finally:
            reset_request_id(token)
        response["X-Request-Id"] = request_id
        return response
