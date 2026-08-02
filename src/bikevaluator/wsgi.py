# Full Path: src/bikevaluator/wsgi.py
# Relative Path: wsgi.py
# Module: bikevaluator (project config package)
# Purpose: WSGI entry point for synchronous production servers.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: EP-001-vehicle-master.md
"""WSGI config for bikevaluator."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bikevaluator.settings")

application = get_wsgi_application()
