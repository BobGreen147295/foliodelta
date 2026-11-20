import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills" / "foliodelta"
SCRIPT = SKILL / "scripts" / "compare.py"
HEADER = ["order_id", "created_at", "total", "currency"]
STAMP = "2026-05-01T01:00:00+01:00"


class BusinessChecks(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.work = Path(work.name)

    def write(self, name, rows, header=HEADER):
        path = self.work / name
        with path.open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(rows)
        return path

    def run_cli(self, left, right, *flags):
        return subprocess.run([sys.executable, str(SCRIPT), str(left), str(right), *flags],
                              cwd=self.work, capture_output=True, encoding="utf-8")

    def result(self, left, right, *flags):
        run = self.run_cli(left, right, "--json", *flags)
        self.assertEqual(run.returncode, 0, run.stderr)
        return json.loads(run.stdout)

    def test_multiline_shopify_demo_handoff(self):
        left, right = [SKILL / "examples" / n for n in ("before.csv", "after.csv")]
        r = self.result(left, right)
        self.assertEqual((r["scope"], r["left_count"], r["right_count"]), ("unconfirmed", 3, 3))
        self.assertEqual((r["left_minor"], r["right_minor"], r["delta_minor"]), (16975, 12325, -4650))
        self.assertEqual([(d["kind"], d["delta_minor"]) for d in r["changes"]],
                         [("left_only", -6000), ("right_only", 1850), ("changed", -500)])
        self.assertEqual(r["changes"][0]["left"]["line"], 4)
        text = self.run_cli(left, right, "--scope-confirmed")
        self.assertEqual(text.returncode, 0)
        self.assertEqual(r["sample"], "bundled_fictional")
        for phrase in ("Fictional demo", "operator_declared", "-46.50 USD", "DEMO-721", "left line 4", "cannot establish"):
            self.assertIn(phrase, text.stdout)

    def test_timestamp_only_and_offsetting_changes(self):
        left = self.write("a", [(k, STAMP, "10", "EUR") for k in "ABC"])
        right = self.write("b", [("A", STAMP, "11", "EUR"), ("B", STAMP, "9", "EUR"),
                                 ("C", "2026-05-02T00:00:00Z", "10", "EUR")])
        r = self.result(left, right)
        self.assertEqual(r["delta_minor"], 0)
        self.assertEqual([d["delta_minor"] for d in r["changes"]], [100, -100, 0])

    def test_timezone_and_physical_lines_with_unused_private_columns(self):
        left = self.write("a", [("A", STAMP, "1", "EUR", "example\nprivate value"),
                                ("B", STAMP, "2", "EUR", "secret field")], HEADER + ["customer note"])
        right = self.write("b", [("A", "2026-05-01T00:00:00Z", "1.00", "EUR")])
        r = self.result(left, right)
        self.assertEqual(len(r["changes"]), 1)
        self.assertEqual(r["changes"][0]["left"]["line"], 4)
        self.assertNotIn("private", json.dumps(r))
        self.assertNotIn("secret", json.dumps(r))

    def test_empty_one_side_and_currency_precision(self):
        empty = self.write("empty", [])
        for unit, value, expected in [("JPY", "31.00", 31), ("KWD", "4.321", 4321), ("USD", "-0.01", -1)]:
            with self.subTest(unit=unit):
                right = self.write("b", [("X", STAMP, value, unit)])
                self.assertEqual(self.result(empty, right)["delta_minor"], expected)
        self.assertEqual(self.run_cli(empty, empty).returncode, 2)

    def test_reject_invalid_rows_without_echoing_raw_cells(self):
        valid = self.write("a", [("X", STAMP, "1", "USD")])
        for rows in [
            [("X", STAMP, "1", "USD"), ("X", STAMP, "1", "USD")],
            [("X", STAMP, "1", "USD"), ("Y", STAMP, "1", "EUR")],
            [("X", STAMP, "1", "EUR")], [("X", STAMP, "1.001", "USD")],
            [("X", STAMP, "9", "XYZ")], [("X", STAMP, "private-amount", "USD")],
            [("X", "2026-05-01", "2", "USD")], [("", STAMP, "1", "USD")],
        ]:
            with self.subTest(rows=rows):
                run = self.run_cli(valid, self.write("b", rows), "--json")
                self.assertEqual((run.returncode, run.stdout), (2, ""))
                self.assertNotIn("private-amount", run.stderr)

    def test_reject_ambiguous_item_continuation(self):
        header = ["Name", "Created at", "Total", "Currency", "Lineitem name"]
        left = self.write("a", [("A", STAMP, "2", "USD", "demo"), ("B", "", "", "", "demo")], header)
        run = self.run_cli(left, left)
        self.assertEqual(run.returncode, 2)
        self.assertIn("left, line 3", run.stderr)

    def test_large_export_keeps_small_discrepancy_traceable(self):
        rows = [(str(i), STAMP, "1.99", "USD") for i in range(10000)]
        left = self.write("a", rows)
        rows[-1] = ("9999", STAMP, "2.00", "USD")
        r = self.result(left, self.write("b", reversed(rows)))
        self.assertEqual((r["delta_minor"], len(r["changes"])), (1, 1))
        self.assertEqual((r["changes"][0]["left"]["line"], r["changes"][0]["right"]["line"]), (10001, 2))

    def test_short_handoff_keeps_full_evidence_available(self):
        left = self.write("a", [])
        right = self.write("b", [(f"O{i:02}", STAMP, str(i), "USD") for i in range(1, 13)])
        summary = self.run_cli(left, right)
        self.assertEqual(summary.returncode, 0)
        self.assertIn("top 10", summary.stdout)
        self.assertIn("O12 |", summary.stdout)
        self.assertNotIn("O01 |", summary.stdout)
        r = self.result(left, right)
        self.assertEqual((len(r["changes"]), r["delta_minor"]), (12, 7800))

    def test_merchant_review_groups_include_offsets_and_rows_below_display_limit(self):
        left_rows = [(str(i), STAMP, "10", "USD") for i in range(12)]
        right_rows = [(str(i), STAMP, "11" if i < 5 else "9", "USD") for i in range(10)]
        right_rows += [("10", "2026-05-02T00:00:00Z", "10", "USD"), ("new", STAMP, "10", "USD")]
        left, right = self.write("a", left_rows), self.write("b", right_rows)
        r = self.result(left, right)
        self.assertEqual(r["delta_minor"], 0)
        observed = {k: (g["count"], g["increase_minor"], g["decrease_minor"])
                    for k, g in r["review_groups"].items()}
        self.assertEqual(observed, {"amount_changed": (10, 500, -500), "time_only": (1, 0, 0),
                                    "left_only": (1, 0, -1000), "right_only": (1, 1000, 0)})
        self.assertEqual(sum(g["count"] for g in r["review_groups"].values()), len(r["changes"]))
        text = self.run_cli(left, right)
        self.assertEqual(text.returncode, 0)
        self.assertIn("Time only | 1 order |", text.stdout)
        self.assertIn("Reporting operations", text.stdout)
        self.assertIn("successful refund transactions", text.stdout)
        self.assertEqual(self.result(left, left)["review_groups"], {})
