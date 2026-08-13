import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class PublicContractTest(unittest.TestCase):
    def test_public_ui_keeps_financial_math_out_of_javascript(self):
        app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        for forbidden in (
            "out.delta * 100",
            "snapshot.unit === \"Percent\"",
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
        for forbidden in ("api.stlouisfed.org", "query1.finance.yahoo.com", "simfin.com/api"):
            self.assertNotIn(forbidden, browser_files)

    def test_worker_is_module_pyodide_and_python_core_is_same_origin(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        worker = (ROOT / "web" / "worker.mjs").read_text(encoding="utf-8")
        self.assertIn('new Worker("./worker.mjs", { type: "module" })', app)
        self.assertIn('fetch("./code/static_bi.py")', worker)
        self.assertIn('role="status"', html)


if __name__ == "__main__":
    unittest.main()
