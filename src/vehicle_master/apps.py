# Full Path: src/vehicle_master/apps.py
# Relative Path: apps.py
# Module: vehicle_master
# Purpose: Django AppConfig for the vehicle_master app.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: CSS-001 §Python/Django ("one Django app per module boundary")
from django.apps import AppConfig


class VehicleMasterConfig(AppConfig):
    """
    AppConfig for the Vehicle Master module (SDD-000 §4).

    Owns the Brand/Model/Variant catalog and ValuationMaster pricing
    (FS-001 §2 Scope). Does not own Repair Master administration
    (deferred to FS-004, per SSD-001 §10) or Evaluation/Calculation
    logic (FS-002).
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "vehicle_master"
    verbose_name = "Vehicle Master"
