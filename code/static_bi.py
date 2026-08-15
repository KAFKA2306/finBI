from __future__ import annotations

import json
from datetime import UTC, date, datetime
from typing import Any

REQUIRED_SOURCE_FIELDS = {
    "provider",
    "source_organization",
    "series_id",
    "series_name",
    "source_url",
    "release",
}
REQUIRED_AVAILABILITY_FIELDS = {
    "verified",
    "source_updated_at",
    "latest_available_observation",
    "evidence_url",
}


def _parse_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError(f"missing snapshot field: {field}")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"invalid timestamp: {field}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp must include timezone: {field}")
    return parsed.astimezone(UTC)


def validate_snapshot(snapshot: dict[str, Any]) -> None:
    if snapshot.get("schema_version") != "finbi.snapshot.v1":
        raise ValueError("unsupported snapshot schema")
    source = snapshot.get("source")
    if not isinstance(source, dict) or not REQUIRED_SOURCE_FIELDS <= source.keys():
        raise ValueError("snapshot source metadata is incomplete")
    if not str(source["source_url"]).startswith("https://"):
        raise ValueError("source_url must be HTTPS")
    for field in (
        "retrieved_at",
        "observation_start",
        "observation_end",
        "unit",
        "frequency",
    ):
        if not snapshot.get(field):
            raise ValueError(f"missing snapshot field: {field}")

    retrieved_at = _parse_timestamp(snapshot["retrieved_at"], "retrieved_at")
    availability = snapshot.get("availability")
    if (
        not isinstance(availability, dict)
        or not REQUIRED_AVAILABILITY_FIELDS <= availability.keys()
    ):
        raise ValueError("snapshot availability evidence is incomplete")
    if availability["verified"] is not True:
        raise ValueError("snapshot availability is not verified")
    if not str(availability["evidence_url"]).startswith("https://"):
        raise ValueError("availability evidence_url must be HTTPS")
    source_updated_at = _parse_timestamp(
        availability["source_updated_at"], "availability.source_updated_at"
    )
    if source_updated_at > retrieved_at:
        raise ValueError("source availability is later than retrieved_at")
    try:
        latest_available = date.fromisoformat(
            str(availability["latest_available_observation"])
        )
    except ValueError as exc:
        raise ValueError("invalid latest_available_observation") from exc

    observations = snapshot.get("observations")
    if not isinstance(observations, list) or len(observations) < 2:
        raise ValueError("snapshot needs at least two observations")
    dates: set[str] = set()
    previous_date: str | None = None
    for row in observations:
        if not isinstance(row, dict) or set(row) != {"date", "value"}:
            raise ValueError("invalid observation record")
        row_date = row["date"]
        try:
            parsed_row_date = date.fromisoformat(row_date)
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid observation date") from exc
        if parsed_row_date > latest_available:
            raise ValueError("observation was not available at retrieved_at")
        if row_date in dates:
            raise ValueError("duplicate observation date")
        if previous_date is not None and row_date <= previous_date:
            raise ValueError("observations must be strictly chronological")
        dates.add(row_date)
        previous_date = row_date
        if not isinstance(row["value"], (int, float)) or isinstance(row["value"], bool):
            raise ValueError("observation value must be numeric")

    if snapshot["observation_start"] != observations[0]["date"]:
        raise ValueError("observation_start does not match first observation")
    if snapshot["observation_end"] != observations[-1]["date"]:
        raise ValueError("observation_end does not match last observation")


def compare_dates(
    snapshot: dict[str, Any], start_date: str, end_date: str
) -> dict[str, Any]:
    validate_snapshot(snapshot)
    by_date = {row["date"]: float(row["value"]) for row in snapshot["observations"]}
    if start_date not in by_date or end_date not in by_date:
        raise ValueError("selected date is outside the committed snapshot")
    if start_date >= end_date:
        raise ValueError("end_date must be later than start_date")

    start_value = by_date[start_date]
    end_value = by_date[end_date]
    delta = end_value - start_value
    direction = "up" if delta > 0 else "down" if delta < 0 else "flat"
    basis_points = (
        round(delta * 100, 4) if snapshot["unit"].casefold() == "percent" else None
    )
    calendar_days = (date.fromisoformat(end_date) - date.fromisoformat(start_date)).days

    return {
        "series_id": snapshot["source"]["series_id"],
        "start_date": start_date,
        "end_date": end_date,
        "start_value": start_value,
        "end_value": end_value,
        "delta": round(delta, 10),
        "basis_points": basis_points,
        "direction": direction,
        "calendar_days": calendar_days,
        "unit": snapshot["unit"],
        "currency": snapshot.get("currency"),
        "retrieved_at": snapshot["retrieved_at"],
        "source_url": snapshot["source"]["source_url"],
    }


def compare_curve(
    long_snapshot: dict[str, Any],
    short_snapshot: dict[str, Any],
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    validate_snapshot(long_snapshot)
    validate_snapshot(short_snapshot)
    if (
        long_snapshot["unit"].casefold() != "percent"
        or short_snapshot["unit"].casefold() != "percent"
    ):
        raise ValueError("curve comparison requires percent series")
    if long_snapshot["source"]["series_id"] == short_snapshot["source"]["series_id"]:
        raise ValueError("curve comparison requires distinct series")

    long_move = compare_dates(long_snapshot, start_date, end_date)
    short_move = compare_dates(short_snapshot, start_date, end_date)
    start_spread_bp = round(
        (long_move["start_value"] - short_move["start_value"]) * 100, 4
    )
    end_spread_bp = round((long_move["end_value"] - short_move["end_value"]) * 100, 4)
    spread_change_bp = round(end_spread_bp - start_spread_bp, 4)
    shape = (
        "STEEPENED"
        if spread_change_bp > 0
        else "FLATTENED"
        if spread_change_bp < 0
        else "UNCHANGED"
    )
    steepening_hypothesis = (
        "ACCEPT"
        if shape == "STEEPENED"
        else "REJECT"
        if shape == "FLATTENED"
        else "MAINTAIN"
    )

    return {
        "schema_version": "finbi.comparison-brief.v1",
        "hypothesis": "The 2s10s Treasury curve steepened over the selected window.",
        "decision": steepening_hypothesis,
        "curve_shape": shape,
        "start_date": start_date,
        "end_date": end_date,
        "long_series_id": long_move["series_id"],
        "short_series_id": short_move["series_id"],
        "start_spread_bp": start_spread_bp,
        "end_spread_bp": end_spread_bp,
        "spread_change_bp": spread_change_bp,
        "long_move_bp": long_move["basis_points"],
        "short_move_bp": short_move["basis_points"],
        "unit": "basis points",
        "sources": [long_move["source_url"], short_move["source_url"]],
        "retrieved_at": [long_move["retrieved_at"], short_move["retrieved_at"]],
    }


def compare_dates_json(snapshot_json: str, start_date: str, end_date: str) -> str:
    result = compare_dates(json.loads(snapshot_json), start_date, end_date)
    return json.dumps(result, ensure_ascii=False, sort_keys=True)


def compare_curve_json(
    long_snapshot_json: str,
    short_snapshot_json: str,
    start_date: str,
    end_date: str,
) -> str:
    result = compare_curve(
        json.loads(long_snapshot_json),
        json.loads(short_snapshot_json),
        start_date,
        end_date,
    )
    return json.dumps(result, ensure_ascii=False, sort_keys=True)
