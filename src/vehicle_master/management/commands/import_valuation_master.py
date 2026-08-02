# Full Path: src/vehicle_master/management/commands/import_valuation_master.py
# Relative Path: management/commands/import_valuation_master.py
# Module: vehicle_master
# Purpose: Idempotent, transactional, validated import of the architect-
#   supplied 2W Valuation Calc spreadsheet into ValuationMaster and the
#   vehicle-scoped ValuationRepairCost rows (IMP-003, hardened IMP-003B).
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: IMP-003, IMP-003B Tasks 2/5/8, BRR-001
#   BR-0007/BR-0010/BR-0011, DBD-001 §9 (as amended), ISP-002, EP-002
"""
See ``docs/importer-README.md`` (IMP-003B Task 6) for a
usage-and-troubleshooting guide aimed at a developer running this
command for the first time.

IMP-003's single source of truth is the spreadsheet at
``data/imports/2w-valuation-calc.csv``. No amount from that file is
ever hardcoded here - the column->(RepairComponent, option_name)
mapping below is structural metadata (which column means what), not a
business value; every rupee figure is read from the file at import time.

ASSUMPTIONS (documented, not silently resolved):

1. Scrap Value has no column in the spreadsheet at all. Defaulted to
   Rs.0.00 (conservative - the BR-0002 floor never activates until an
   Admin sets a real value later via the existing
   ``POST /admin/valuation-master`` endpoint, which supersedes this
   import's version like any other pricing edit, per BR-0007).
2. Single-value repair columns (Shock/Fork, Tyres, Gearbox, Clutch) map
   to a single ``FULL`` RepairOption each - the spreadsheet has no
   "half" variant for these repairs.
3. "Shock/Fork" is a new RepairComponent name not listed in DBD-001 §9's
   original example list - treated as a normal catalog extension.
4. The importer acts as a system Actor (``role="super_admin"``) since
   this is a data-migration context, not an authenticated HTTP request -
   FS-003 (Authentication) still doesn't exist. Every write still goes
   through ``VehicleMasterAdminService`` (BR-0004 enforcement, BR-0011
   duplicate detection, real audit trail as of IMP-003B) exactly as a
   real Super Admin's request would - the importer never bypasses
   those checks.

IMP-003B HARDENING (Task 5):

- Encoding: tries UTF-8 (with/without BOM) first, falls back to
  Windows-1252 (the default Excel-on-Windows CSV export encoding) if
  UTF-8 decoding fails, instead of crashing the whole command.
- Thousands separators (e.g. ``"1,000"``) are stripped before parsing
  as a ``Decimal`` - a common artifact of default Excel number
  formatting that a prior version of this command did not tolerate.
- Progress is logged every ``PROGRESS_INTERVAL`` rows, not only at the
  end, so a large import doesn't look hung.
- Every run is logged via Python's ``logging`` module (logger
  ``vehicle_master.import``, see ``settings.LOGGING``), not only
  ``self.stdout.write`` - see IMP-003B Task 8.
"""

import csv
import io
import logging
import time
import uuid
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from vehicle_master.audit_context import audit_run_context
from vehicle_master.exceptions import ConcurrencyConflictError, DuplicateCatalogEntryError
from vehicle_master.repositories import (
    BrandRepository,
    ModelRepository,
    RepairComponentRepository,
    RepairOptionRepository,
    ValuationMasterRepository,
    ValuationRepairCostRepository,
    VariantRepository,
)
from vehicle_master.service_factory import build_vehicle_master_admin_service
from vehicle_master.validators import validate_non_negative_amount, validate_year_range

logger = logging.getLogger("vehicle_master.import")

DEFAULT_FILE = Path(settings.BASE_DIR).parent / "data" / "imports" / "2w-valuation-calc.csv"

# Encodings tried in order - UTF-8 (incl. BOM) first, then the default
# encoding Excel-on-Windows uses when "Save As CSV" is chosen without
# explicitly picking UTF-8.
CANDIDATE_ENCODINGS = ["utf-8-sig", "cp1252"]

PROGRESS_INTERVAL = 500

# Structural column -> (RepairComponent name, RepairOption.option_name) mapping.
# This is metadata about the spreadsheet's shape, not a business value -
# no rupee amount is ever written into this file (see module docstring).
REPAIR_COLUMN_MAP = [
    ("HalfEngineExp", "Engine", "PARTIAL"),
    ("FullEngineExp", "Engine", "FULL"),
    ("HalfColourExp", "Colour", "PARTIAL"),
    ("FullColourExp", "Colour", "FULL"),
    ("ShockForkExp", "Shock/Fork", "FULL"),
    ("TyresExp", "Tyres", "FULL"),
    ("GearBoxExp", "Gearbox", "FULL"),
    ("ClutchExp", "Clutch", "FULL"),
    ("HalfPlasticExp", "Plastic", "PARTIAL"),
    ("FullPlasticExp", "Plastic", "FULL"),
]

DEFAULT_SCRAP_VALUE = Decimal("0.00")

SYSTEM_IMPORTER_ACTOR_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
SYSTEM_IMPORTER_IP = "system-importer"


class RowImportError(Exception):
    """A single row failed validation or a business-rule check - the row is skipped, import continues."""


@dataclass
class ImportStats:
    total_rows: int = 0
    skipped_blank: int = 0
    valuation_master_created: int = 0
    valuation_master_updated: int = 0
    valuation_master_unchanged: int = 0
    repair_costs_written: int = 0
    failed: int = 0
    failures: list = field(default_factory=list)  # (row_number, reason)


def _read_text_with_fallback(file_path: Path) -> str:
    """
    Decode ``file_path`` trying ``CANDIDATE_ENCODINGS`` in order
    (IMP-003B Task 5) - a bad encoding guess no longer crashes the
    whole command with an unhandled ``UnicodeDecodeError``.
    """
    raw_bytes = file_path.read_bytes()
    last_error: Optional[UnicodeDecodeError] = None
    for encoding in CANDIDATE_ENCODINGS:
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
            continue
    raise CommandError(
        f"Could not decode {file_path} using any of {CANDIDATE_ENCODINGS}: {last_error}"
    )


class Command(BaseCommand):
    help = (
        "Import the 2W Valuation Calc spreadsheet into ValuationMaster + "
        "ValuationRepairCost (IMP-003). Idempotent - safe to re-run."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default=str(DEFAULT_FILE),
            help="Path to the CSV export of the valuation spreadsheet.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and report without writing anything to the database.",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file"])
        dry_run = options["dry_run"]

        if not file_path.exists():
            raise CommandError(f"File not found: {file_path}")

        run_id = str(uuid.uuid4())
        start_time = time.monotonic()
        logger.info(
            "Import started file=%s dry_run=%s correlation_id=%s", file_path, dry_run, run_id
        )

        actor = SimpleNamespace(id=SYSTEM_IMPORTER_ACTOR_ID, role="super_admin")
        admin_service = build_vehicle_master_admin_service()
        valuation_master_repository = ValuationMasterRepository()
        valuation_repair_cost_repository = ValuationRepairCostRepository()
        brand_repository = BrandRepository()
        model_repository = ModelRepository()
        variant_repository = VariantRepository()
        component_repository = RepairComponentRepository()
        option_repository = RepairOptionRepository()

        stats = ImportStats()
        text = _read_text_with_fallback(file_path)

        with audit_run_context(correlation_id=run_id, request_id=f"cli:import_valuation_master:{run_id}"):
            reader = csv.DictReader(io.StringIO(text))
            for row_number, row in enumerate(reader, start=2):  # header is line 1
                stats.total_rows += 1

                if stats.total_rows % PROGRESS_INTERVAL == 0:
                    elapsed = time.monotonic() - start_time
                    logger.info(
                        "Import progress rows_read=%s elapsed_seconds=%.2f", stats.total_rows, elapsed
                    )
                    self.stdout.write(f"... processed {stats.total_rows} rows ({elapsed:.1f}s elapsed)")

                if all(not (value or "").strip() for value in row.values()):
                    stats.skipped_blank += 1
                    continue

                try:
                    with transaction.atomic():
                        outcome = self._import_row(
                            row,
                            actor=actor,
                            admin_service=admin_service,
                            valuation_master_repository=valuation_master_repository,
                            valuation_repair_cost_repository=valuation_repair_cost_repository,
                            brand_repository=brand_repository,
                            model_repository=model_repository,
                            variant_repository=variant_repository,
                            component_repository=component_repository,
                            option_repository=option_repository,
                        )
                        if dry_run:
                            transaction.set_rollback(True)
                except (RowImportError, DjangoValidationError, DuplicateCatalogEntryError,
                        ConcurrencyConflictError) as exc:
                    stats.failed += 1
                    stats.failures.append((row_number, str(exc)))
                    logger.warning("Row %s failed: %s", row_number, exc)
                    continue

                if outcome["valuation_master_status"] == "created":
                    stats.valuation_master_created += 1
                elif outcome["valuation_master_status"] == "updated":
                    stats.valuation_master_updated += 1
                else:
                    stats.valuation_master_unchanged += 1
                stats.repair_costs_written += outcome["repair_costs_written"]

        elapsed_seconds = time.monotonic() - start_time
        logger.info(
            "Import completed rows=%s skipped=%s created=%s updated=%s unchanged=%s "
            "repair_costs=%s failed=%s elapsed_seconds=%.2f correlation_id=%s",
            stats.total_rows, stats.skipped_blank, stats.valuation_master_created,
            stats.valuation_master_updated, stats.valuation_master_unchanged,
            stats.repair_costs_written, stats.failed, elapsed_seconds, run_id,
        )
        self._print_report(stats, dry_run, elapsed_seconds)

    def _import_row(
        self,
        row,
        *,
        actor,
        admin_service,
        valuation_master_repository,
        valuation_repair_cost_repository,
        brand_repository,
        model_repository,
        variant_repository,
        component_repository,
        option_repository,
    ) -> dict:
        year = self._parse_year(row.get("Year"))
        brand_name = self._required_text(row.get("Brand"), "Brand")
        model_name = self._required_text(row.get("Model"), "Model")
        variant_name = self._required_text(row.get("Variant"), "Variant")
        minimum_selling_price = self._parse_amount(row.get("MinSellingPrice"), "MinSellingPrice")
        margin = self._parse_amount(row.get("Margin"), "Margin")

        repair_amounts = {}
        for column, component_name, option_name in REPAIR_COLUMN_MAP:
            repair_amounts[(component_name, option_name)] = self._parse_amount(
                row.get(column), column
            )

        brand = brand_repository.get_by_name(brand_name)
        if brand is None:
            brand = admin_service.create_brand(brand_name, actor, SYSTEM_IMPORTER_IP)

        model = model_repository.get_by_name(brand.id, model_name)
        if model is None:
            model = admin_service.create_model(brand.id, model_name, actor, SYSTEM_IMPORTER_IP)

        variant = variant_repository.get_by_name(model.id, variant_name)
        if variant is None:
            variant = admin_service.create_variant(
                model.id, variant_name, actor, SYSTEM_IMPORTER_IP
            )

        valuation_master, valuation_master_status = self._upsert_valuation_master(
            year=year,
            variant_id=variant.id,
            minimum_selling_price=minimum_selling_price,
            margin=margin,
            admin_service=admin_service,
            valuation_master_repository=valuation_master_repository,
            actor=actor,
        )

        repair_costs_written = 0
        for (component_name, option_name), amount in repair_amounts.items():
            component = component_repository.get_by_name(component_name)
            if component is None:
                component = component_repository.create(component_name)

            option = option_repository.get_by_component_and_option_name(
                component.id, option_name
            )
            if option is None:
                option = option_repository.create(component.id, option_name)

            valuation_repair_cost_repository.upsert(valuation_master.id, option.id, amount)
            repair_costs_written += 1

        return {
            "valuation_master_status": valuation_master_status,
            "repair_costs_written": repair_costs_written,
        }

    def _upsert_valuation_master(
        self,
        *,
        year,
        variant_id,
        minimum_selling_price,
        margin,
        admin_service,
        valuation_master_repository,
        actor,
    ):
        current = valuation_master_repository.get_active_by_year_variant(year, variant_id)
        if current is None:
            valuation_master = admin_service.create_valuation_master_version(
                year=year,
                variant_id=variant_id,
                minimum_selling_price=minimum_selling_price,
                margin=margin,
                scrap_value=DEFAULT_SCRAP_VALUE,
                expected_previous_updated_at=None,
                actor=actor,
                ip_address=SYSTEM_IMPORTER_IP,
            )
            return valuation_master, "created"

        unchanged = (
            current.minimum_selling_price == minimum_selling_price
            and current.margin == margin
            and current.scrap_value == DEFAULT_SCRAP_VALUE
        )
        if unchanged:
            return current, "unchanged"

        valuation_master = admin_service.create_valuation_master_version(
            year=year,
            variant_id=variant_id,
            minimum_selling_price=minimum_selling_price,
            margin=margin,
            scrap_value=DEFAULT_SCRAP_VALUE,
            expected_previous_updated_at=current.updated_at,
            actor=actor,
            ip_address=SYSTEM_IMPORTER_IP,
        )
        return valuation_master, "updated"

    @staticmethod
    def _parse_year(raw: Optional[str]) -> int:
        if raw is None or not raw.strip():
            raise RowImportError("Year is required.")
        try:
            year = int(raw.strip())
        except ValueError:
            raise RowImportError(f"Year '{raw}' is not a valid integer.")
        try:
            validate_year_range(year)
        except DjangoValidationError as exc:
            raise RowImportError(f"Year {year}: {exc.message}")
        return year

    @staticmethod
    def _required_text(raw: Optional[str], field_name: str) -> str:
        if raw is None or not raw.strip():
            raise RowImportError(f"{field_name} is required.")
        return raw.strip()

    @staticmethod
    def _parse_amount(raw: Optional[str], field_name: str) -> Decimal:
        if raw is None or not raw.strip():
            raise RowImportError(f"{field_name} is required.")
        # IMP-003B Task 5: tolerate thousands separators (e.g. "1,000"),
        # a common artifact of default Excel number formatting.
        cleaned = raw.strip().replace(",", "")
        try:
            amount = Decimal(cleaned)
        except InvalidOperation:
            raise RowImportError(f"{field_name} '{raw}' is not a valid number.")
        try:
            validate_non_negative_amount(amount)
        except DjangoValidationError as exc:
            raise RowImportError(f"{field_name}: {exc.message}")
        return amount

    def _print_report(self, stats: ImportStats, dry_run: bool, elapsed_seconds: float) -> None:
        mode = "DRY RUN (no changes written)" if dry_run else "LIVE IMPORT"
        self.stdout.write(self.style.MIGRATE_HEADING(f"\n=== 2W Valuation Master Import - {mode} ==="))
        self.stdout.write(f"Total data rows read:            {stats.total_rows}")
        self.stdout.write(f"Skipped (fully blank rows):       {stats.skipped_blank}")
        self.stdout.write(f"ValuationMaster created:          {stats.valuation_master_created}")
        self.stdout.write(f"ValuationMaster updated (new version): {stats.valuation_master_updated}")
        self.stdout.write(f"ValuationMaster unchanged (skipped):   {stats.valuation_master_unchanged}")
        self.stdout.write(f"ValuationRepairCost rows written:  {stats.repair_costs_written}")
        self.stdout.write(f"Failed rows:                       {stats.failed}")
        self.stdout.write(f"Elapsed time:                      {elapsed_seconds:.2f}s")
        if stats.failures:
            self.stdout.write(self.style.WARNING("\nFailures:"))
            for row_number, reason in stats.failures:
                self.stdout.write(self.style.WARNING(f"  Row {row_number}: {reason}"))
        self.stdout.write("")
