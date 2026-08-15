import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from static_bi import compare_curve, compare_dates, validate_snapshot

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "data" / "snapshots" / "fred-dgs10-2026-07-20_2026-07-23.json"
SHORT_SNAPSHOT = ROOT / "data" / "snapshots" / "fred-dgs2-2026-07-20_2026-07-23.json"
THREE_MONTH_SNAPSHOT = (
    ROOT / "data" / "snapshots" / "fred-dgs3mo-2026-07-20_2026-07-23.json"
)
DECISION_LEDGER = (
    ROOT / "data" / "decisions" / "treasury-curves-2026-07-20_2026-07-23.json"
)
AVAILABILITY_FIXTURE = (
    ROOT / "code" / "tests" / "fixtures" / "fred-dgs10-availability-2026-07-24.json"
)


class StaticBITest(unittest.TestCase):
    def snapshot(self):
        return json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    def short_snapshot(self):
        return json.loads(SHORT_SNAPSHOT.read_text(encoding="utf-8"))

    def three_month_snapshot(self):
        return json.loads(THREE_MONTH_SNAPSHOT.read_text(encoding="utf-8"))

    def decision_ledger(self):
        return json.loads(DECISION_LEDGER.read_text(encoding="utf-8"))

    def availability_fixture(self):
        return json.loads(AVAILABILITY_FIXTURE.read_text(encoding="utf-8"))

    def test_snapshot_and_comparison(self):
        data = self.snapshot()
        validate_snapshot(data)
        result = compare_dates(data, "2026-07-20", "2026-07-23")
        self.assertEqual(result["series_id"], "DGS10")
        self.assertAlmostEqual(result["delta"], 0.11)
        self.assertAlmostEqual(result["basis_points"], 11.0)
        self.assertEqual(result["direction"], "up")
        self.assertEqual(result["calendar_days"], 3)

    def test_2s10s_brief_rejects_steepening_hypothesis(self):
        result = compare_curve(
            self.snapshot(), self.short_snapshot(), "2026-07-20", "2026-07-23"
        )
        self.assertEqual(result["schema_version"], "finbi.comparison-brief.v1")
        self.assertEqual(result["decision"], "REJECT")
        self.assertEqual(result["curve_shape"], "FLATTENED")
        self.assertAlmostEqual(result["start_spread_bp"], 39.0)
        self.assertAlmostEqual(result["end_spread_bp"], 34.0)
        self.assertAlmostEqual(result["spread_change_bp"], -5.0)
        self.assertAlmostEqual(result["long_move_bp"], 11.0)
        self.assertAlmostEqual(result["short_move_bp"], 16.0)
        self.assertEqual(result["long_series_id"], "DGS10")
        self.assertEqual(result["short_series_id"], "DGS2")
        self.assertEqual(
            result["hypothesis"],
            "The Treasury curve between DGS2 and DGS10 steepened over the selected window.",
        )
        self.assertEqual(len(result["sources"]), 2)

    def test_3m10y_brief_accepts_steepening_hypothesis(self):
        result = compare_curve(
            self.snapshot(), self.three_month_snapshot(), "2026-07-20", "2026-07-23"
        )
        self.assertEqual(result["decision"], "ACCEPT")
        self.assertEqual(result["curve_shape"], "STEEPENED")
        self.assertAlmostEqual(result["start_spread_bp"], 74.0)
        self.assertAlmostEqual(result["end_spread_bp"], 76.0)
        self.assertAlmostEqual(result["spread_change_bp"], 2.0)
        self.assertAlmostEqual(result["long_move_bp"], 11.0)
        self.assertAlmostEqual(result["short_move_bp"], 9.0)
        self.assertEqual(result["long_series_id"], "DGS10")
        self.assertEqual(result["short_series_id"], "DGS3MO")
        self.assertEqual(
            result["hypothesis"],
            "The Treasury curve between DGS3MO and DGS10 steepened over the selected window.",
        )
        self.assertNotIn("2s10s", result["hypothesis"])

    def test_decision_ledger_recomputes_from_verified_snapshots(self):
        ledger = self.decision_ledger()
        self.assertEqual(ledger["schema_version"], "finbi.decision-ledger.v1")
        snapshots = {
            "DGS10": self.snapshot(),
            "DGS2": self.short_snapshot(),
            "DGS3MO": self.three_month_snapshot(),
        }
        for decision in ledger["hypotheses"]:
            result = compare_curve(
                snapshots[decision["long_series_id"]],
                snapshots[decision["short_series_id"]],
                ledger["window"]["start_date"],
                ledger["window"]["end_date"],
            )
            for key in (
                "long_series_id",
                "short_series_id",
                "start_spread_bp",
                "end_spread_bp",
                "spread_change_bp",
                "curve_shape",
                "decision",
            ):
                self.assertEqual(result[key], decision[key])
            self.assertEqual(result["sources"], decision["source_urls"])

    def test_curve_requires_distinct_series(self):
        with self.assertRaisesRegex(ValueError, "distinct series"):
            compare_curve(self.snapshot(), self.snapshot(), "2026-07-20", "2026-07-23")

    def test_one_day_move_is_explained(self):
        result = compare_dates(self.snapshot(), "2026-07-22", "2026-07-23")
        self.assertAlmostEqual(result["basis_points"], 4.0)
        self.assertEqual(result["direction"], "up")
        self.assertEqual(result["calendar_days"], 1)

    def test_known_future_observation_regression_fails(self):
        data = self.snapshot()
        fixture = self.availability_fixture()
        rejected = fixture["known_unavailable_observation"]
        self.assertEqual(data["retrieved_at"], fixture["retrieved_at"])
        self.assertEqual(
            data["availability"]["latest_available_observation"],
            fixture["verified_availability"]["latest_available_observation"],
        )
        data["observations"].append(
            {"date": rejected["date"], "value": rejected["value"]}
        )
        data["observation_end"] = rejected["date"]
        with self.assertRaisesRegex(
            ValueError, "observation was not available at retrieved_at"
        ):
            validate_snapshot(data)

    def test_unverified_availability_fails_closed(self):
        data = self.snapshot()
        data["availability"]["verified"] = False
        with self.assertRaisesRegex(ValueError, "availability is not verified"):
            validate_snapshot(data)

    def test_source_update_after_retrieval_fails(self):
        data = self.snapshot()
        fixture = self.availability_fixture()
        data["availability"]["source_updated_at"] = fixture[
            "known_unavailable_observation"
        ]["first_visible_at"]
        with self.assertRaisesRegex(
            ValueError, "source availability is later than retrieved_at"
        ):
            validate_snapshot(data)

    def test_missing_availability_evidence_fails(self):
        data = self.snapshot()
        del data["availability"]["evidence_url"]
        with self.assertRaisesRegex(ValueError, "availability evidence is incomplete"):
            validate_snapshot(data)

    def test_bad_range_fails(self):
        with self.assertRaises(ValueError):
            compare_dates(self.snapshot(), "2026-07-23", "2026-07-20")

    def test_missing_source_fails(self):
        data = self.snapshot()
        del data["source"]["source_url"]
        with self.assertRaises(ValueError):
            validate_snapshot(data)

    def test_unsorted_observations_fail(self):
        data = self.snapshot()
        data["observations"][0], data["observations"][1] = (
            data["observations"][1], data["observations"][0]
        )
        with self.assertRaises(ValueError):
            validate_snapshot(data)


if __name__ == "__main__":
    unittest.main()
