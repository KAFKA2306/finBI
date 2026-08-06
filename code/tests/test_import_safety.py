from __future__ import annotations

import builtins
import importlib
import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

CODE_DIR = Path(__file__).resolve().parents[1]
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))


class ImportSafetyTests(unittest.TestCase):
    def test_import_has_no_network_file_write_pickle_or_ui_side_effect(self) -> None:
        sys.modules.pop("your_streamlit_app", None)
        stdout = io.StringIO()
        stderr = io.StringIO()
        real_open = builtins.open

        def guarded_open(file, mode="r", *args, **kwargs):
            if any(flag in mode for flag in ("w", "a", "+", "x")):
                raise AssertionError(f"file write during import: {file}")
            return real_open(file, mode, *args, **kwargs)

        with (
            patch("builtins.open", side_effect=guarded_open),
            patch("pathlib.Path.write_text", side_effect=AssertionError("write_text during import")),
            patch("pathlib.Path.write_bytes", side_effect=AssertionError("write_bytes during import")),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            module = importlib.import_module("your_streamlit_app")

        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")
        self.assertNotIn("streamlit", sys.modules)
        self.assertTrue(callable(module.build_readiness_report))

    def test_missing_credentials_are_provider_local(self) -> None:
        from settings import Settings

        settings = Settings.from_env({"FINBI_DATA_DIR": str(CODE_DIR / "data")})
        report = importlib.import_module("your_streamlit_app").build_readiness_report(settings)
        providers = {item["provider"]: item for item in report["providers"]}
        self.assertEqual(providers["fred"]["credential_status"], "DISABLED_MISSING_CREDENTIAL")
        self.assertEqual(providers["yahoo"]["credential_status"], "NOT_REQUIRED")
        self.assertFalse(providers["yahoo"]["live_access_attempted"])

    def test_placeholder_credentials_are_not_treated_as_configured(self) -> None:
        from settings import Settings

        settings = Settings.from_env({
            "FINBI_DATA_DIR": str(CODE_DIR / "data"),
            "FRED_API_KEY": " yours ",
            "FINNHUB_API_KEY": "real-local-value",
        })
        self.assertEqual(settings.credential_status("fred"), "DISABLED_MISSING_CREDENTIAL")
        self.assertEqual(settings.credential_status("finnhub"), "CONFIGURED")

    def test_data_directory_is_portable(self) -> None:
        from settings import Settings

        settings = Settings.from_env({})
        self.assertNotIn("M:\\", str(settings.data_dir))
        self.assertTrue(settings.data_dir.is_absolute())


if __name__ == "__main__":
    unittest.main()
