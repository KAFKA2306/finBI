"""Offline provider diagnostics.

Importing this module never imports provider SDKs and never attempts live access.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib.util import find_spec
from typing import Iterable

from settings import Settings


@dataclass(frozen=True)
class ProviderStatus:
    provider: str
    dependency: str | None
    dependency_available: bool
    credential_status: str
    cache_status: str
    live_access_attempted: bool
    last_verified_date: str | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


_PROVIDER_DEPENDENCIES = {
    "yahoo": "yfinance",
    "fred": "fredapi",
    "simfin": "simfin",
    "alpha_vantage": None,
    "financial_modeling_prep": None,
    "finnhub": None,
}


def diagnose_providers(
    settings: Settings,
    providers: Iterable[str] | None = None,
) -> list[ProviderStatus]:
    selected = tuple(providers or _PROVIDER_DEPENDENCIES)
    results: list[ProviderStatus] = []
    for provider in selected:
        if provider not in _PROVIDER_DEPENDENCIES:
            raise KeyError(f"unknown provider: {provider}")
        dependency = _PROVIDER_DEPENDENCIES[provider]
        dependency_available = dependency is None or find_spec(dependency) is not None
        credential_status = (
            "NOT_REQUIRED"
            if provider == "yahoo"
            else settings.credential_status(provider)
        )
        results.append(
            ProviderStatus(
                provider=provider,
                dependency=dependency,
                dependency_available=dependency_available,
                credential_status=credential_status,
                cache_status="NOT_CHECKED",
                live_access_attempted=False,
                last_verified_date=None,
            )
        )
    return results
