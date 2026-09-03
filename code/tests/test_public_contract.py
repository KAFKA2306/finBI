import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANONICAL_FX_URL = (
    "https://kafka2306.github.io/investor2/artifacts/api/v1/portfolio/fx-overlay.json"
)


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
            "leverage *",
            "spot_return",
            "annualized_swap",
            "break_even",
            "pnl_yen",
            "policy_rate_gap",
        ):
            self.assertNotIn(forbidden, fx)
        self.assertGreaterEqual(app.count("out.basis_points"), 2)
        self.assertIn("out.direction", app)
        self.assertIn('FX_OVERLAY_SCHEMA = "investor2.fx-overlay.v1"', fx)

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

    def test_worker_is_rates_only_and_python_core_is_same_origin(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        fx = (ROOT / "web" / "fx.js").read_text(encoding="utf-8")
        worker = (ROOT / "web" / "worker.mjs").read_text(encoding="utf-8")
        core = (ROOT / "code" / "static_bi.py").read_text(encoding="utf-8")
        self.assertIn('new Worker("./worker.mjs", { type: "module" })', app)
        self.assertNotIn("new Worker", fx)
        self.assertIn('fetch("./code/static_bi.py")', worker)
        self.assertIn("compare_curve_json", worker)
        self.assertNotIn("analyze_fx_snapshot", worker)
        self.assertNotIn("analyze_fx_snapshot", core)
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

    def test_theme_follows_system_color_scheme_without_second_palette(self):
        app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        tokens = (ROOT / "web" / ".kafka-design" / "kafka-tokens.css").read_text(
            encoding="utf-8"
        )

        self.assertIn('matchMedia("(prefers-color-scheme: dark)")', app)
        self.assertIn("document.documentElement.dataset.theme = theme", app)
        self.assertIn("document.documentElement.style.colorScheme = theme", app)
        self.assertIn('systemTheme.addEventListener("change", syncSystemTheme)', app)
        self.assertNotRegex(app, r"#[0-9A-Fa-f]{3,8}")
        self.assertIn('[data-theme="dark"]', tokens)
        self.assertIn("--k-color-canvas: #F7F5EF", tokens)
        self.assertIn("--k-color-canvas: #0B0F17", tokens)

    def test_fx_view_consumes_investor2_contract_without_local_copy(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        fx = (ROOT / "web" / "fx.js").read_text(encoding="utf-8")
        duplicated = ROOT / "data" / "snapshots" / "investor2-fx-overlay.json"

        self.assertIn('id="fx-desk"', html)
        self.assertIn('id="fx-overlay-status"', html)
        self.assertIn('id="fx-reason"', html)
        self.assertIn(CANONICAL_FX_URL, fx)
        self.assertIn('fetch(FX_OVERLAY_URL, { cache: "no-store" })', fx)
        self.assertFalse(duplicated.exists())
        self.assertIn(
            "KAFKA2306/investor2/blob/main/docs/specs/fx_overlay_contract.md", html
        )
        self.assertIn("KAFKA2306/investor2/issues/251", html)
        self.assertIn("KAFKA2306/investor2/issues/252", html)
        self.assertNotIn("usdjpy-sbi-2026-09-03.json", fx)
        self.assertNotIn("1Y Scenario · 3x", html)
        self.assertNotIn("raw swap", html)

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
        self.assertRegex(compact, r"button,select\{min-height:44px;?\}")
        self.assertIn(".chip{min-height:44px", compact)
        self.assertNotIn(".chip{min-height:40px", compact)

    def test_public_css_consumes_locked_canonical_design(self):
        styles = (ROOT / "web" / "styles.css").read_text(encoding="utf-8")
        fx = (ROOT / "web" / "fx.css").read_text(encoding="utf-8")
        entry = (ROOT / "web" / "design-tokens.css").read_text(encoding="utf-8")
        config = json.loads((ROOT / "design.config.json").read_text(encoding="utf-8"))
        lock = json.loads((ROOT / "design.lock.json").read_text(encoding="utf-8"))

        self.assertIn('@import url("./design-tokens.css")', styles)
        self.assertEqual(
            config["designSha"], "6ef94b60a9fefcd7577ec25d2edd4bca06096314"
        )
        self.assertEqual(lock["designSha"], config["designSha"])
        self.assertEqual(lock["integration"]["cssEntry"], "web/design-tokens.css")
        self.assertEqual(entry.count("/* kafka-design:managed-start */"), 1)
        self.assertEqual(entry.count("/* kafka-design:managed-end */"), 1)
        self.assertIn("desk-card:not(.is-live)", entry)

        for item in lock["managedFiles"]:
            managed = ROOT / item["path"]
            self.assertTrue(managed.is_file())
            self.assertEqual(
                hashlib.sha256(managed.read_bytes()).hexdigest(), item["sha256"]
            )

        tokens = (ROOT / "web" / ".kafka-design" / "kafka-tokens.css").read_text(
            encoding="utf-8"
        )
        self.assertIn("--k-dimension-table-row: 30px", tokens)
        self.assertIn("--k-dimension-radius: 2px", tokens)
        self.assertIn("--k-number-shadow-opacity: 0", tokens)
        self.assertIn("var(--k-dimension-table-row)", fx)
        self.assertIn("var(--k-dimension-radius)", styles)
        self.assertNotIn("box-shadow:0 18px 48px", re.sub(r"\s+", "", styles))


if __name__ == "__main__":
    unittest.main()
