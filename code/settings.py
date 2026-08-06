"""Typed, side-effect-free runtime settings for the finBI recovery shell."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

_PROVIDER_ENV = {
    "fred": "FRED_API_KEY",
    "simfin": "SIMFIN_API_KEY",
    "alpha_vantage": "ALPHA_VANTAGE_API_KEY",
    "financial_modeling_prep": "FINANCIAL_MODELING_PREP_API_KEY",
    "finnhub": "FINNHUB_API_KEY",
}


@dataclass(frozen=True)
class Settings:
    """Configuration loaded without network, file writes, or provider imports."""

    data_dir: Path
    credentials: Mapping[str, str | None]

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        source = os.environ if env is None else env
        default_data_dir = Path(__file__).resolve().parent.parent / "data"
        data_dir = Path(source.get("FINBI_DATA_DIR", str(default_data_dir))).expanduser().resolve()
        credentials = {
            provider: _clean_secret(source.get(variable))
            for provider, variable in _PROVIDER_ENV.items()
        }
        return cls(data_dir=data_dir, credentials=credentials)

    def credential_status(self, provider: str) -> str:
        if provider not in self.credentials:
            raise KeyError(f"unknown provider: {provider}")
        return "CONFIGURED" if self.credentials[provider] else "DISABLED_MISSING_CREDENTIAL"


def _clean_secret(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped or stripped.lower() in {"yours", "changeme", "placeholder"}:
        return None
    return stripped
