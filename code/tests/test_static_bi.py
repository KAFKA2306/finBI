import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from static_bi import compare_dates, validate_snapshot

SNAPSHOT = Path(__file__).resolve().parents[2] / "data" / "snapshots" / "fred-dgs10-2026-07-20_2026-07-23.json"


class StaticBITest(unittest.TestCase):
    def snapshot(self):
        return json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    def test_snapshot_and_comparison(self):
        data = self.snapshot()
        validate_snapshot(data)
        result = compare_dates(data, "2026-07-20", "2026-07-23")
        self.assertEqual(result["series_id"], "DGS10")
        self.assertAlmostEqual(result["delta"], 0.11)
        self.assertAlmostEqual(result["basis_points"], 11.0)
        self.assertEqual(result["direction"], "up")
        self.assertEqual(result["calendar_days"], 3)

    def test_one_day_move_is_explained(self):
        result = compare_dates(self.snapshot(), "2026-07-22", "2026-07-23")
        self.assertAlmostEqual(result["basis_points"], 4.0)
        self.assertEqual(result["direction"], "up")
        self.assertEqual(result["calendar_days"], 1)

    def test_known_future_observation_regression_fails(self):
        data = self.snapshot()
        data["observations"].append({"date": "2026-07-24", "value": 4.69})
        data["observation_end"] = "2026-07-24"
        with self.assertRaisesRegex(ValueError, "observation was not available at retrieved_at"):
            validate_snapshot(data)

    def test_unverified_availability_fails_closed(self):
        data = self.snapshot()
        data["availability"]["verified"] = False
        with self.assertRaisesRegex(ValueError, "availability is not verified"):
            validate_snapshot(data)

    def test_source_update_after_retrieval_fails(self):
        data = self.snapshot()
        data["availability"]["source_updated_at"] = "2026-07-27T20:16:00Z"
        with self.assertRaisesRegex(ValueError, "source availability is later than retrieved_at"):
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
        data["observations"][0], data["observations"][1] = data["observations"][1], data["observations"][0]
        with self.assertRaises(ValueError):
            validate_snapshot(data)


if __name__ == "__main__":
    unittest.main()
