# Full Path: src/vehicle_master/tests/test_import_valuation_master.py
# Relative Path: tests/test_import_valuation_master.py
# Module: vehicle_master
# Purpose: Tests for the `import_valuation_master` management command -
#   idempotency, validation, transactional row isolation, dry-run.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: IMP-003, TEST-001
import io
from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase

from vehicle_master.models import (
    Brand,
    Model,
    ValuationMaster,
    ValuationRepairCost,
    Variant,
)

HEADER = (
    "Year,Brand,Model,Variant,MinSellingPrice,Margin,HalfEngineExp,FullEngineExp,"
    "FullColourExp,HalfColourExp,ShockForkExp,TyresExp,GearBoxExp,ClutchExp,"
    "FullPlasticExp,HalfPlasticExp\n"
)


def _write_csv(tmp_path, rows: str):
    file_path = tmp_path / "import.csv"
    file_path.write_text(HEADER + rows, encoding="utf-8")
    return file_path


class ImportValuationMasterCommandTests(TestCase):
    def setUp(self):
        import tempfile
        from pathlib import Path

        self._tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmp_dir.name)

    def tearDown(self):
        self._tmp_dir.cleanup()

    def _run(self, csv_rows: str, dry_run: bool = False):
        file_path = _write_csv(self.tmp_path, csv_rows)
        out = io.StringIO()
        call_command(
            "import_valuation_master", f"--file={file_path}",
            *(["--dry-run"] if dry_run else []), stdout=out,
        )
        return out.getvalue()

    def test_imports_new_vehicle_and_repair_costs(self):
        output = self._run(
            "2022,Honda,Activa,6g,45000,5000,5000,7500,6000,5000,2000,2000,3500,1500,2000,1000\n"
        )
        self.assertIn("ValuationMaster created:          1", output)
        self.assertIn("ValuationRepairCost rows written:  10", output)
        self.assertTrue(Brand.objects.filter(brand_name="Honda").exists())
        self.assertTrue(Model.objects.filter(model_name="Activa").exists())
        variant = Variant.objects.get(variant_name="6g")
        valuation_master = ValuationMaster.objects.get(year=2022, variant=variant)
        self.assertEqual(valuation_master.minimum_selling_price, Decimal("45000.00"))
        self.assertEqual(ValuationRepairCost.objects.filter(valuation_master=valuation_master).count(), 10)

    def test_reruns_are_idempotent_no_duplicates(self):
        rows = "2022,Honda,Activa,6g,45000,5000,5000,7500,6000,5000,2000,2000,3500,1500,2000,1000\n"
        self._run(rows)
        second_output = self._run(rows)
        self.assertIn("ValuationMaster unchanged (skipped):   1", second_output)
        self.assertEqual(Brand.objects.filter(brand_name="Honda").count(), 1)
        self.assertEqual(ValuationMaster.objects.count(), 1)

    def test_changed_price_creates_new_version_not_duplicate(self):
        self._run("2022,Honda,Activa,6g,45000,5000,5000,7500,6000,5000,2000,2000,3500,1500,2000,1000\n")
        output = self._run(
            "2022,Honda,Activa,6g,48000,5000,5000,7500,6000,5000,2000,2000,3500,1500,2000,1000\n"
        )
        self.assertIn("ValuationMaster updated (new version): 1", output)
        variant = Variant.objects.get(variant_name="6g")
        self.assertEqual(ValuationMaster.objects.filter(year=2022, variant=variant).count(), 2)
        active = ValuationMaster.objects.get(year=2022, variant=variant, active=True)
        self.assertEqual(active.minimum_selling_price, Decimal("48000.00"))

    def test_reuses_existing_brand_model_variant_no_duplicates(self):
        self._run("2022,Honda,Activa,6g,45000,5000,5000,7500,6000,5000,2000,2000,3500,1500,2000,1000\n")
        self._run("2023,Honda,Activa,6g,50000,5000,5000,7500,6000,5000,2000,2000,3500,1500,2000,1000\n")
        self.assertEqual(Brand.objects.filter(brand_name="Honda").count(), 1)
        self.assertEqual(Model.objects.filter(model_name="Activa").count(), 1)
        self.assertEqual(Variant.objects.filter(variant_name="6g").count(), 1)
        self.assertEqual(ValuationMaster.objects.count(), 2)

    def test_blank_rows_are_skipped_not_failed(self):
        output = self._run(
            "2022,Honda,Activa,6g,45000,5000,5000,7500,6000,5000,2000,2000,3500,1500,2000,1000\n"
            ",,,,,,,,,,,,,,,\n"
        )
        self.assertIn("Skipped (fully blank rows):       1", output)
        self.assertIn("Failed rows:                       0", output)

    def test_invalid_row_fails_but_does_not_abort_other_rows(self):
        output = self._run(
            "2022,Honda,Activa,6g,45000,5000,5000,7500,6000,5000,2000,2000,3500,1500,2000,1000\n"
            "not-a-year,TVS,Jupiter,BS6,35000,4000,5000,7000,6000,4000,2000,2000,2500,2500,6000,4000\n"
        )
        self.assertIn("Failed rows:                       1", output)
        self.assertIn("ValuationMaster created:          1", output)
        self.assertTrue(Variant.objects.filter(variant_name="6g").exists())
        self.assertFalse(Brand.objects.filter(brand_name="TVS").exists())

    def test_negative_amount_fails_validation(self):
        output = self._run(
            "2022,Honda,Activa,6g,45000,5000,-100,7500,6000,5000,2000,2000,3500,1500,2000,1000\n"
        )
        self.assertIn("Failed rows:                       1", output)
        self.assertEqual(ValuationMaster.objects.count(), 0)

    def test_dry_run_persists_nothing(self):
        self._run(
            "2022,Honda,Activa,6g,45000,5000,5000,7500,6000,5000,2000,2000,3500,1500,2000,1000\n",
            dry_run=True,
        )
        self.assertEqual(Brand.objects.count(), 0)
        self.assertEqual(ValuationMaster.objects.count(), 0)

    def test_thousands_separator_is_tolerated(self):
        """IMP-003B Task 5: a common Excel export artifact, e.g. "45,000"."""
        output = self._run(
            '2022,Honda,Activa,6g,"45,000",5000,5000,7500,6000,5000,2000,2000,3500,1500,2000,1000\n'
        )
        self.assertIn("Failed rows:                       0", output)
        variant = Variant.objects.get(variant_name="6g")
        valuation_master = ValuationMaster.objects.get(year=2022, variant=variant)
        self.assertEqual(valuation_master.minimum_selling_price, Decimal("45000.00"))

    def test_windows_1252_encoded_file_is_read_via_fallback(self):
        """IMP-003B Task 5: default Excel-on-Windows CSV export encoding."""
        file_path = self.tmp_path / "import.csv"
        # A Brand name containing a curly apostrophe (U+2019), encoded
        # as Windows-1252 byte 0x92 - not valid UTF-8 on its own.
        content = HEADER + "2022,Honda’s,Activa,6g,45000,5000,5000,7500,6000,5000,2000,2000,3500,1500,2000,1000\n"
        file_path.write_bytes(content.encode("cp1252"))
        out = io.StringIO()
        call_command("import_valuation_master", f"--file={file_path}", stdout=out)
        self.assertIn("Failed rows:                       0", out.getvalue())
        self.assertTrue(Brand.objects.filter(brand_name="Honda’s").exists())

    def test_large_import_completes_and_reports_progress(self):
        """
        IMP-003B Task 5: progress reporting for a multi-batch file.
        Uses a smaller PROGRESS_INTERVAL so this stays a fast unit test -
        the actual 10k-row timing is measured separately (Task 10's
        benchmark script), not on every test run.
        """
        from unittest.mock import patch

        rows = "".join(
            f"{2000 + (i % 26)},Brand{i},Model{i},Variant{i},{10000 + i},1000,"
            "1000,2000,1500,1000,500,500,750,500,500,250\n"
            for i in range(45)
        )
        with patch("vehicle_master.management.commands.import_valuation_master.PROGRESS_INTERVAL", 10):
            output = self._run(rows)
        self.assertIn("... processed 10 rows", output)
        self.assertIn("... processed 40 rows", output)
        self.assertIn("ValuationMaster created:          45", output)
        self.assertEqual(ValuationMaster.objects.count(), 45)

    def test_sequential_reimports_of_same_row_remain_idempotent(self):
        """
        Best-effort concurrency-adjacent test: repeatedly re-running the
        importer against the same row (modeling closely-spaced retries)
        must never create duplicate Brand/Model/Variant/ValuationMaster
        rows. True multi-process concurrent writes are not exercised
        here - see Known Limitations (SQLite dev DB, single-writer).
        """
        rows = "2022,Honda,Activa,6g,45000,5000,5000,7500,6000,5000,2000,2000,3500,1500,2000,1000\n"
        for _ in range(5):
            self._run(rows)
        self.assertEqual(Brand.objects.filter(brand_name="Honda").count(), 1)
        self.assertEqual(Model.objects.filter(model_name="Activa").count(), 1)
        self.assertEqual(Variant.objects.filter(variant_name="6g").count(), 1)
        self.assertEqual(ValuationMaster.objects.count(), 1)
