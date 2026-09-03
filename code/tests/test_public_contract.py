import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class PublicContractTest(unittest.TestCase):
    def test_public_ui_keeps_financial_math_out_of_javascript(self):
        app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        fx = (ROOT / "web" / "fx.js").read_text(encoding="utf-8")
        for forbidden in (
            "out.delta * 100",
            'snapshot.unit === "Percent"',
            "snapshot.unit === 'Percent'",
            "const basisPoints",
            "let basisPoints",
            "long_move_bp - short_move_bp",
        ):
            self.assertNotIn(forbidden, app)
        for forbidden in (
            "* 365",
            "365 *",
            "leverage *",
            "spot_return *",
            "annualized_swap",
            "break_even_spot_return =",
        ):
            self.assertNotIn(forbidden, fx)
        self.assertGreaterEqual(app.count("out.basis_points"), 2)
        self.assertIn("out.direction", app)
        self.assertIn("brief.carry_on_initial_equity_percent", fx)
        self.assertIn("brief.break_even_spot_return_percent", fx)

    def test_public_ui_has_no_live_financial_provider_fetch(self):
        browser_files = "\n".join(
            (ROOT / "web" / name).read_text(encoding="utf-8")
            for name in ("app.js", "fx.js", "worker.mjs")
        )
        for forbidden in (
            "api.stlouisfed.org",
            "query1.finance.yahoo.com",
            "simfin.com/api",
            "www.reuters.com/world",
            "www.sbisec.co.jp/ETGate",
        ):
            self.assertNotIn(forbidden, browser_files)

    def test_worker_is_module_pyodide_and_python_core_is_same_origin(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        fx = (ROOT / "web" / "fx.js").read_text(encoding="utf-8")
        worker = (ROOT / "web" / "worker.mjs").read_text(encoding="utf-8")
        self.assertIn('new Worker("./worker.mjs", { type: "module" })', app)
        self.assertIn('new Worker("./worker.mjs", { type: "module" })', fx)
        self.assertIn('fetch("./code/static_bi.py")', worker)
        self.assertIn("compare_curve_json", worker)
        self.assertIn("analyze_fx_snapshot_json", worker)
        self.assertIn('role="status"', html)

    def test_curve_brief_uses_same_date_controls_and_two_sources(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="curve-brief-heading"', html)
        self.assertIn('id="curve-long-source"', html)
        self.assertIn('id="curve-short-source"', html)
        self.assertIn('document.querySelector("#start")', app)
        self.assertIn('document.querySelector("#end")', app)
        self.assertIn("fred-dgs10-2026-07-20_2026-07-23.json", app)
        self.assertIn("fred-dgs2-2026-07-20_2026-07-23.json", app)

    def test_fx_view_uses_saved_snapshot_and_exposes_audit_state(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        fx = (ROOT / "web" / "fx.js").read_text(encoding="utf-8")
        self.assertIn('id="fx-desk"', html)
        self.assertIn('id="fx-scenarios"', html)
        self.assertIn('id="fx-assumptions"', html)
        self.assertIn("usdjpy-sbi-2026-09-03.json", fx)
        self.assertIn('worker.postMessage({ kind: "fx", snapshot })', fx)
        self.assertIn("raw swap", html)
        self.assertIn("付与日数未確認", html)

    def test_chart_points_are_directly_selectable_without_removing_selects(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="start"', html)
        self.assertIn('id="end"', html)
        self.assertIn('class: "chart-hit dynamic"', app)
        self.assertIn('hit.addEventListener("click"', app)
        self.assertIn('chartPickPhase = "end"', app)
        self.assertIn('class: "chart-selected-label dynamic"', app)

    def test_comparison_period_is_shareable_and_owned_by_app_module(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        self.assertEqual(html.count('<script type="module"'), 2)
        self.assertIn('<script type="module" src="./fx.js"></script>', html)
        self.assertIn('<script type="module" src="./app.js"></script>', html)
        self.assertNotIn("URLSearchParams", html)
        self.assertIn('requested.get("start")', app)
        self.assertIn('requested.get("end")', app)
        self.assertIn('url.searchParams.set("start", start.value)', app)
        self.assertIn('url.searchParams.set("end", end.value)', app)
        self.assertIn('window.history.replaceState(null, "", url)', app)
        self.assertIn("requestedStart < requestedEnd", app)

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
