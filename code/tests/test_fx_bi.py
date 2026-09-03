import json
import unittest
from pathlib import Path

from static_bi import analyze_fx_snapshot, validate_fx_snapshot

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "data" / "snapshots" / "usdjpy-sbi-2026-09-03.json"


def load_snapshot():
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


class FxBiTest(unittest.TestCase):
    def test_snapshot_validates_without_normalizing_unverified_current_swap(self):
        snapshot = load_snapshot()
        validate_fx_snapshot(snapshot)
        raw = snapshot["broker"]["swap"]["current_raw"]
        self.assertEqual(raw["buy_yen_per_10000"], 468)
        self.assertIsNone(raw["award_days"])
        self.assertIsNone(raw["normalized_daily_yen_per_10000"])

    def test_three_x_fixed_notional_scenario_is_deterministic(self):
        brief = analyze_fx_snapshot(load_snapshot())
        self.assertEqual(brief["pair"], "USDJPY")
        self.assertEqual(brief["spot"], 156.17)
        self.assertEqual(brief["leverage"], 3.0)
        self.assertEqual(brief["usd_notional"], 10000.0)
        self.assertAlmostEqual(brief["initial_equity_yen"], 520566.67, places=2)
        self.assertEqual(brief["scenario_daily_buy_swap_yen_per_10000"], 117.0)
        self.assertEqual(brief["annualized_swap_yen"], 42705.0)
        self.assertAlmostEqual(
            brief["carry_on_initial_equity_percent"], 8.2036, places=4
        )
        self.assertAlmostEqual(brief["break_even_spot_return_percent"], -2.7345, places=4)
        self.assertEqual(brief["policy_rate_gap_percentage_points"], 2.625)

    def test_scenarios_do_not_hide_fx_downside(self):
        brief = analyze_fx_snapshot(load_snapshot())
        by_spot_return = {
            row["spot_return_percent"]: row for row in brief["scenarios"]
        }
        self.assertAlmostEqual(
            by_spot_return[-5.0]["equity_return_percent"], -6.7964, places=4
        )
        self.assertAlmostEqual(
            by_spot_return[0.0]["equity_return_percent"], 8.2036, places=4
        )
        self.assertAlmostEqual(
            by_spot_return[10.0]["equity_return_percent"], 38.2036, places=4
        )

    def test_unverified_current_swap_normalization_fails_closed(self):
        snapshot = load_snapshot()
        snapshot["broker"]["swap"]["current_raw"]["award_days"] = 4
        with self.assertRaisesRegex(ValueError, "must remain unnormalized"):
            validate_fx_snapshot(snapshot)


if __name__ == "__main__":
    unittest.main()
