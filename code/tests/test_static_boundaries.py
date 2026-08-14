from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE_DIR = ROOT / "code"
WEB_DIR = ROOT / "web"


class StaticBoundaryTests(unittest.TestCase):
    def test_python_runtime_surface_is_one_module(self) -> None:
        modules = sorted(path.name for path in CODE_DIR.glob("*.py"))
        self.assertEqual(modules, ["static_bi.py"])

    def test_public_ui_surface_is_four_files(self) -> None:
        files = sorted(path.name for path in WEB_DIR.iterdir() if path.is_file())
        self.assertEqual(files, ["app.js", "index.html", "styles.css", "worker.mjs"])

    def test_no_personal_path_pickle_or_legacy_runtime(self) -> None:
        source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [
                CODE_DIR / "static_bi.py",
                WEB_DIR / "app.js",
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


if __name__ == "__main__":
    unittest.main()
