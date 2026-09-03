import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class PrimaryReadingPathTest(unittest.TestCase):
    def test_primary_navigation_contains_only_usable_views(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertNotIn("PLANNED", html)
        self.assertEqual(html.count('class="desk-card is-live"'), 2)
        self.assertIn('href="#fx-desk"', html)
        self.assertIn('href="#rates-desk"', html)
        self.assertIn("未実装のsurfaceは主要導線に置きません", html)

    def test_fx_primary_metrics_follow_status_to_decision_to_identity(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        markers = [
            'id="fx-overlay-status"',
            'id="fx-current-exposure"',
            'id="fx-incremental-exposure"',
            'id="fx-schema"',
            'id="fx-audit-heading"',
        ]
        positions = [html.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("状態と根拠を確認する", html)


if __name__ == "__main__":
    unittest.main()
