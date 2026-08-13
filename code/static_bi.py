from __future__ import annotations

import json
from typing import Any

REQUIRED_SOURCE_FIELDS = {
    "provider",
    "source_organization",
    "series_id",
    "series_name",
    "source_url",
    "release",
}


def validate_snapshot(snapshot: dict[str, Any]) -> None:
    if snapshot.get("schema_version") != "finbi.snapshot.v1":
        raise ValueError("unsupported snapshot schema")
    source = snapshot.get("source")
    if not isinstance(source, dict) or not REQUIRED_SOURCE_FIELDS <= source.keys():
        raise ValueError("snapshot source metadata is incomplete")
    if not str(source["source_url"]).startswith("https://"):
        raise ValueError("source_url must be HTTPS")
    for field in ("retrieved_at", "observation_start", "observation_end", "unit", "frequency"):
        if not snapshot.get(field):
            raise ValueError(f"missing snapshot field: {field}")
    observations = snapshot.get("observations")
    if not isinstance(observations, list) or len(observations) < 2:
        raise ValueError("snapshot needs at least two observations")
    dates: set[str] = set()
    for row in observations:
        if not isinstance(row, dict) or set(row) != {"date", "value"}:
            raise ValueError("invalid observation record")
        if row["date"] in dates:
            raise ValueError("duplicate observation date")
        dates.add(row["date"])
        if not isinstance(row["value"], (int, float)):
            raise ValueError("observation value must be numeric")


def compare_dates(snapshot: dict[str, Any], start_date: str, end_date: str) -> dict[str, Any]:
    validate_snapshot(snapshot)
    by_date = {row["date"]: float(row["value"]) for row in snapshot["observations"]}
    if start_date not in by_date or end_date not in by_date:
        raise ValueError("selected date is outside the committed snapshot")
    if start_date >= end_date:
        raise ValueError("end_date must be later than start_date")
    start_value = by_date[start_date]
    end_value = by_date[end_date]
    delta = end_value - start_value
    return {
        "series_id": snapshot["source"]["series_id"],
        "start_date": start_date,
        "end_date": end_date,
        "start_value": start_value,
        "end_value": end_value,
        "delta": round(delta, 10),
        "unit": snapshot["unit"],
        "currency": snapshot.get("currency"),
        "retrieved_at": snapshot["retrieved_at"],
        "source_url": snapshot["source"]["source_url"],
    }


def compare_dates_json(snapshot_json: str, start_date: str, end_date: str) -> str:
    result = compare_dates(json.loads(snapshot_json), start_date, end_date)
    return json.dumps(result, ensure_ascii=False, sort_keys=True)
