"""Import-safe recovery entry point for the legacy finBI prototype.

The original 2023 module mixed provider setup, pickle loading, network access, and
Streamlit rendering at import time. This recovery shell deliberately exposes only
an offline readiness view. Data acquisition and financial analysis remain disabled
until provider adapters and a schema-validated cache are implemented and tested.
"""

from __future__ import annotations

import json
from typing import Sequence

from provider_status import diagnose_providers
from settings import Settings


def build_readiness_report(settings: Settings | None = None) -> dict[str, object]:
    """Return a deterministic offline status report without side effects."""

    runtime_settings = settings or Settings.from_env()
    return {
        "application": "finBI",
        "mode": "RECOVERY_OFFLINE",
        "investment_decision_ready": False,
        "data_dir": str(runtime_settings.data_dir),
        "providers": [
            status.to_dict() for status in diagnose_providers(runtime_settings)
        ],
    }


def render_streamlit() -> None:
    """Render the recovery status page; import Streamlit only on explicit launch."""

    try:
        import streamlit as st
    except ImportError as exc:  # pragma: no cover - depends on optional UI package
        raise RuntimeError(
            "Streamlit is not installed. Use `python code/your_streamlit_app.py --diagnose` "
            "for the offline diagnostic."
        ) from exc

    report = build_readiness_report()
    st.title("finBI recovery status")
    st.warning(
        "Legacy financial-data functions are disabled and cannot be used for "
        "investment decisions."
    )
    st.json(report)


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="finBI recovery diagnostics")
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help="print the offline provider readiness report as JSON",
    )
    args = parser.parse_args(argv)

    if args.diagnose:
        print(
            json.dumps(
                build_readiness_report(), ensure_ascii=False, indent=2, sort_keys=True
            )
        )
        return 0

    render_streamlit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
