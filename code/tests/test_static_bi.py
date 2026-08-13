import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from static_bi import compare_dates, validate_snapshot

SNAPSHOT = Path(__file__).resolve().parents[2] / "data" / "snapshots" / "fred-dgs10-2026-07-20_2026-07-24.json"

class StaticBITest(unittest.TestCase):
    def snapshot(self):
        return json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    def test_snapshot_and_comparison(self):
        data = self.snapshot()
        validate_snapshot(data)
        result = compare_dates(data, "2026-07-20", "2026-07-24")
        self.assertEqual(result["series_id"], "DGS10")
        self.assertAlmostEqual(result["delta"], 0.09)

    def test_bad_range_fails(self):
        with self.assertRaises(ValueError):
            compare_dates(self.snapshot(), "2026-07-24", "2026-07-20")

    def test_missing_source_fails(self):
        data = self.snapshot()
        del data["source"]["source_url"]
        with self.assertRaises(ValueError):
            validate_snapshot(data)

if __name__ == "__main__":
    unittest.main()
