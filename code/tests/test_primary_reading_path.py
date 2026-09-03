import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class PrimaryReadingPathTest(unittest.TestCase):
    def test_primary_navigation_contains_only_usable_views(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertNotIn("PLANNED", html)
        self.assertIn('class="appnav"', html)
        self.assertIn('href="#fx-desk"', html)
        self.assertIn('href="#rates-desk"', html)
        self.assertNotIn('class="desk-card is-live"', html)
        self.assertLess(html.index('id="fx-desk"'), html.index('class="utility-drawer"'))
        self.assertLess(html.index('id="rates-desk"'), html.index('class="utility-drawer"'))

    def test_fx_primary_path_is_status_reason_measures_action_then_identity(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        markers = [
            'id="fx-overlay-status"',
            'id="fx-reason"',
            'id="fx-current-exposure"',
            'id="fx-incremental-exposure"',
            'id="fx-total-exposure"',
            'class="primary-link"',
            'id="fx-schema"',
        ]
        positions = [html.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("USD exposure overlay の正準状態", html)
        self.assertIn("詳細と根拠", html)


if __name__ == "__main__":
    unittest.main()
