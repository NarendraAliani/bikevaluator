# Full Path: src/bikevaluator/urls.py
# Relative Path: urls.py
# Module: bikevaluator (project config package)
# Purpose: Root URL configuration - mounts vehicle_master's routes under /api/v1/.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: API-001 (Base URLs: /api/v1/), EP-001 §5, IMP-001C
"""
Root URL configuration for bikevaluator.

``vehicle_master.urls`` is mounted at ``api/v1/`` to match API-001's
Base URL convention (``https://.../api/v1/...``).
"""

from django.urls import include, path

urlpatterns = [
    path("api/v1/", include("vehicle_master.urls")),
]
