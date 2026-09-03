from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE_DIR = ROOT / "code"
DATA_DIR = ROOT / "data"
WEB_DIR = ROOT / "web"


class StaticBoundaryTests(unittest.TestCase):
    def test_python_runtime_surface_is_one_module(self) -> None:
        modules = sorted(path.name for path in CODE_DIR.glob("*.py"))
        self.assertEqual(modules, ["static_bi.py"])

    def test_public_ui_surface_is_explicit_and_small(self) -> None:
        files = sorted(path.name for path in WEB_DIR.iterdir() if path.is_file())
        self.assertEqual(
            files,
            [
                "app.js",
                "design-tokens.css",
                "fx.css",
                "fx.js",
                "index.html",
                "question-router.js",
                "styles.css",
                "worker.mjs",
            ],
        )

    def test_public_rates_data_matches_live_view(self) -> None:
        snapshots = sorted(
            path.name for path in (DATA_DIR / "snapshots").glob("*.json")
        )
        self.assertEqual(
            snapshots,
            [
                "fred-dgs10-2026-07-20_2026-07-23.json",
                "fred-dgs2-2026-07-20_2026-07-23.json",
            ],
        )

    def test_derived_decisions_are_not_stored(self) -> None:
        self.assertFalse((DATA_DIR / "decisions").exists())

    def test_no_personal_path_pickle_or_legacy_runtime(self) -> None:
        source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [
                CODE_DIR / "static_bi.py",
                WEB_DIR / "app.js",
                WEB_DIR / "fx.js",
                WEB_DIR / "question-router.js",
                WEB_DIR / "worker.mjs",
            ]
        )
        self.assertIsNone(re.search(r"[A-Za-z]:\\\\(?:Users|ML|Documents)\\\\", source))
        for forbidden in (
            "pickle.load",
            "pd.read_pickle",
            "streamlit",
            "ngrok",
            "heroku",
        ):
            self.assertNotIn(forbidden, source.casefold())

    def test_public_modules_do_not_embed_private_financial_data(self) -> None:
        source = "\n".join(
            (WEB_DIR / name).read_text(encoding="utf-8")
            for name in ("question-router.js", "fx.js")
        )
        for forbidden in (
            "account_number",
            "口座番号",
            "tax_document",
            "private transaction",
            "api_key",
            "secret",
        ):
            self.assertNotIn(forbidden, source.casefold())


if __name__ == "__main__":
    unittest.main()
