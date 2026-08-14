import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class PublicContractTest(unittest.TestCase):
    def test_public_ui_keeps_financial_math_out_of_javascript(self):
        app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        for forbidden in (
            "out.delta * 100",
            'snapshot.unit === "Percent"',
            "snapshot.unit === 'Percent'",
            "const basisPoints",
            "let basisPoints",
        ):
            self.assertNotIn(forbidden, app)
        self.assertGreaterEqual(app.count("out.basis_points"), 2)
        self.assertIn("out.direction", app)

    def test_public_ui_has_no_live_financial_provider_fetch(self):
        browser_files = "\n".join(
            (ROOT / "web" / name).read_text(encoding="utf-8")
            for name in ("app.js", "worker.mjs")
        )
        for forbidden in (
            "api.stlouisfed.org",
            "query1.finance.yahoo.com",
            "simfin.com/api",
        ):
            self.assertNotIn(forbidden, browser_files)

    def test_worker_is_module_pyodide_and_python_core_is_same_origin(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        worker = (ROOT / "web" / "worker.mjs").read_text(encoding="utf-8")
        self.assertIn('new Worker("./worker.mjs", { type: "module" })', app)
        self.assertIn('fetch("./code/static_bi.py")', worker)
        self.assertIn('role="status"', html)

    def test_chart_points_are_directly_selectable_without_removing_selects(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="start"', html)
        self.assertIn('id="end"', html)
        self.assertIn('class: "chart-hit dynamic"', app)
        self.assertIn('hit.addEventListener("click"', app)
        self.assertIn('chartPickPhase = "end"', app)
        self.assertIn('class: "chart-selected-label dynamic"', app)

    def test_quick_picks_show_dates_and_bp_is_explained(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        self.assertIn(
            "`${prefix} ${formatDate(startDate)} → ${formatDate(endDate)}`", app
        )
        self.assertIn("percentage point", app)
        self.assertIn("1 bp = 0.01 percentage point", html)

    def test_controls_do_not_override_44px_minimum(self):
        css = (ROOT / "web" / "styles.css").read_text(encoding="utf-8")
        compact = re.sub(r"\s+", "", css)
        self.assertIn("button,select{min-height:44px}", compact)
        self.assertIn(".chip{min-height:44px", compact)
        self.assertNotIn(".chip{min-height:40px", compact)


if __name__ == "__main__":
    unittest.main()
