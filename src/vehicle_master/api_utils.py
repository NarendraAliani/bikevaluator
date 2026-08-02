# Full Path: src/vehicle_master/api_utils.py
# Relative Path: api_utils.py
# Module: vehicle_master
# Purpose: Cross-cutting REST API helpers - response envelope and
#   centralized exception translation.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: API-000 v1.1 (Response Envelope, ARC-0007), SDD-000 §8
#   (Error Catalogue), EP-001 §7 (Error Package), IMP-001C, IMP-001D
#   (architecture refinement - moved actor/IP extraction out of this
#   file into actor_provider.py/request_context.py, per architect review)
"""
Cross-cutting API-layer helpers, kept in one file since both belong to
response handling specifically (envelope shaping, exception
translation) - not to any single view.

**ARCHITECTURE COMPLIANCE NOTE (IMP-001C):** IMP-001C's own prompt
sketched a response envelope - ``{"success": true, "data": {}}`` /
``{"success": false, "errorCode": "...", "message": "..."}`` - that
conflicts with the envelope already Approved in API-000 v1.1 (per
`ARC-0007`): ``{"success", "message", "data"}`` /
``{"success", "message", "errors": [{"code","message","field"}]}``.
Per this prompt's own constraint ("do not modify approved architecture
unless absolutely necessary") and Constitution Rule 20, this file
implements the **already-Approved API-000 v1.1 envelope**, not the
prompt's ad-hoc sketch. Flagged prominently here and in the Architecture
Compliance Report rather than silently picked.

**IMP-001D note:** actor/IP resolution (``get_actor_from_request``/
``get_ip_address_from_request``) previously lived in this file. Per the
architect's review, that coupled views to an authentication
implementation detail through this module. It has moved to
``actor_provider.py`` (``ActorProvider``/``DummyActorProvider``) and
``request_context.py`` (``RequestContext``) - see those files for the
same "temporary, insecure, must be replaced once FS-003 exists" note,
unchanged in substance, only relocated.
"""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_exception_handler

from vehicle_master.exceptions import (
    ConcurrencyConflictError,
    DeprecatedVariantError,
    DuplicateCatalogEntryError,
    NotAuthorizedError,
    PricingNotAvailableError,
    VariantMissingError,
    VehicleMasterError,
    VehicleNotFoundError,
)


def success_response(data, status_code: int = status.HTTP_200_OK) -> Response:
    """Wrap ``data`` in the Approved API-000 v1.1 success envelope."""
    return Response({"success": True, "message": "Success", "data": data}, status=status_code)


def error_response(code: str, message: str, status_code: int, field=None) -> Response:
    """Wrap an error in the Approved API-000 v1.1 error envelope."""
    return Response(
        {
            "success": False,
            "message": message,
            "errors": [{"code": code, "message": message, "field": field}],
        },
        status=status_code,
    )


#: Maps each VehicleMasterError subclass to its HTTP status.
#: DeprecatedVariantError and VariantMissingError were not explicitly
#: named in IMP-001C's exception-mapping examples - inferred here
#: (VariantMissingError alongside VehicleNotFoundError as "not found";
#: DeprecatedVariantError as a state conflict, alongside the other
#: 409s), and flagged as an inference in the Architecture Compliance
#: Report.
_ERROR_STATUS_MAP = {
    VehicleNotFoundError: status.HTTP_404_NOT_FOUND,
    VariantMissingError: status.HTTP_404_NOT_FOUND,
    PricingNotAvailableError: status.HTTP_404_NOT_FOUND,
    DuplicateCatalogEntryError: status.HTTP_409_CONFLICT,
    DeprecatedVariantError: status.HTTP_409_CONFLICT,
    ConcurrencyConflictError: status.HTTP_409_CONFLICT,
    NotAuthorizedError: status.HTTP_403_FORBIDDEN,
}


def bikevaluator_exception_handler(exc, context):
    """
    Centralized DRF exception handler (`REST_FRAMEWORK.EXCEPTION_HANDLER`).

    Translates every ``VehicleMasterError`` subclass and both
    Django's/DRF's ``ValidationError`` into the Approved error envelope.
    Anything else falls through to DRF's own default handler (which
    itself falls through to Django's 500 handling for truly unexpected
    exceptions) - never silently swallowed.
    """
    if isinstance(exc, VehicleMasterError):
        status_code = _ERROR_STATUS_MAP.get(type(exc), status.HTTP_400_BAD_REQUEST)
        return error_response(exc.error_code, str(exc), status_code)

    if isinstance(exc, DjangoValidationError):
        message = "; ".join(exc.messages) if hasattr(exc, "messages") else str(exc)
        return error_response("VALIDATION_ERROR", message, status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, DRFValidationError):
        return error_response(
            "VALIDATION_ERROR", str(exc.detail), status.HTTP_400_BAD_REQUEST
        )

    # Framework-native exceptions (NotFound, ParseError, NotAuthenticated,
    # etc.) - re-wrap DRF's default response into our envelope so callers
    # never see two different shapes.
    response = drf_default_exception_handler(exc, context)
    if response is not None:
        return error_response("REQUEST_ERROR", str(response.data), response.status_code)
    return None  # truly unexpected -> Django's default 500 behavior
