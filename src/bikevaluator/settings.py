# Full Path: src/bikevaluator/settings.py
# Relative Path: settings.py
# Module: bikevaluator (project config package)
# Purpose: Django project settings for BIKEVALUATOR's backend foundation (IMP-001A).
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: DBD-001 (database engine), NS-001 §11 (env var naming),
#   SEC-001 (secrets management), Constitution Rule 12 (src/ production root)
"""
Django settings for the bikevaluator project.

ARCHITECTURE OBSERVATION (see IMP-001A Architecture Observations):
EP-001 defined the vehicle_master app's internal structure but never
specified the overall Django project skeleton (this file, manage.py,
urls.py, wsgi.py, asgi.py). This file is new scaffolding required to
make the vehicle_master app buildable/testable at all - not a business
or architecture decision, just minimal project bootstrapping.

DATABASE NOTE: DBD-001 mandates PostgreSQL for production. This
environment has no live PostgreSQL server and no `psycopg2` installed,
so `DATABASES` below defaults to SQLite for local development and
automated testing only. Django's ORM (including the partial unique
index used by ValuationMaster, see vehicle_master/models/
valuation_master.py) behaves identically on SQLite for this module's
purposes. Production deployment MUST set the `BIKEVALUATOR_DATABASE_URL`
environment variable (or equivalent) to a real PostgreSQL connection
and install `psycopg2`/`psycopg2-binary` (already pinned in
requirements.txt) - this is a deliberate dev-convenience choice, not an
architecture change.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Per SEC-001 ("no secrets in source control") and NS-001 §11
# (UPPER_SNAKE_CASE, BIKEVALUATOR_ prefix) - the fallback below is
# explicitly insecure and for local development only.
SECRET_KEY = os.environ.get(
    "BIKEVALUATOR_SECRET_KEY",
    "insecure-dev-only-key-do-not-use-in-production",
)

DEBUG = os.environ.get("BIKEVALUATOR_DEBUG", "True") == "True"

_allowed_hosts_env = os.environ.get("BIKEVALUATOR_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_env.split(",") if h.strip()]

INSTALLED_APPS = [
    # Minimal footprint: only what vehicle_master's models/tests need
    # today. django.contrib.auth ships Django's own User model, kept
    # only for framework-internal migration compatibility - it is NOT
    # the same as DBD-001's `users` table (with its `role` column),
    # which is Authentication's (FS-003) concern, not implemented here.
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "vehicle_master",
]

# IMP-001C: centralized exception translation (Service exceptions ->
# HTTP responses), per API-000 v1.1's approved envelope (ARC-0007) -
# NOT the ad-hoc {"success","errorCode","message"} shape sketched in
# IMP-001C's prompt, which conflicts with the already-Approved
# {"success","message","data"/"errors"} envelope. See this round's
# Architecture Compliance Report for the full reasoning.
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "vehicle_master.api_utils.bikevaluator_exception_handler",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    # IMP-003B Task 2: assigns request_id (from X-Request-Id, or a new
    # UUID) to every request, for audit records - no view code changes.
    "vehicle_master.middleware.RequestIdMiddleware",
]

ROOT_URLCONF = "bikevaluator.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
            ],
        },
    },
]

WSGI_APPLICATION = "bikevaluator.wsgi.application"
ASGI_APPLICATION = "bikevaluator.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"

# All timestamps stored UTC per SDD-000 §7 - display conversion is a
# Flutter-client concern, not this module's.
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# IMP-003B Task 8: structured logging via Python's `logging` module -
# the importer must not rely on stdout alone. Console handler keeps
# interactive `manage.py` output; the file handler gives a durable,
# grep-able record independent of whatever captured stdout.
LOG_DIR = BASE_DIR.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "structured": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "structured",
        },
        "import_file": {
            "class": "logging.FileHandler",
            "filename": str(LOG_DIR / "import.log"),
            "formatter": "structured",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "vehicle_master.import": {
            "handlers": ["console", "import_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
