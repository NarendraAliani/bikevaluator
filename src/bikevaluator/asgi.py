# Full Path: src/bikevaluator/asgi.py
# Relative Path: asgi.py
# Module: bikevaluator (project config package)
# Purpose: ASGI entry point for asynchronous production servers.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: EP-001-vehicle-master.md
"""ASGI config for bikevaluator."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bikevaluator.settings")

application = get_asgi_application()
