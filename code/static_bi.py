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
        "hypothesis": (
            f"The Treasury curve between {short_move['series_id']} and "
            f"{long_move['series_id']} steepened over the selected window."
        ),
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


def _require_number(value: Any, field: str, *, positive: bool = False) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{field} must be numeric")
    number = float(value)
    if positive and number <= 0:
        raise ValueError(f"{field} must be positive")
    return number


def _require_https(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("https://"):
        raise ValueError(f"{field} must be HTTPS")
    return value


def validate_fx_snapshot(snapshot: dict[str, Any]) -> None:
    if snapshot.get("schema_version") != "finbi.fx-snapshot.v1":
        raise ValueError("unsupported FX snapshot schema")
    if snapshot.get("pair") != "USDJPY":
        raise ValueError("first FX BI contract supports USDJPY only")
    _parse_timestamp(snapshot.get("retrieved_at"), "retrieved_at")

    spot = snapshot.get("spot")
    if not isinstance(spot, dict):
        raise ValueError("missing spot block")
    _require_number(spot.get("value"), "spot.value", positive=True)
    try:
        date.fromisoformat(str(spot.get("observed_date")))
    except ValueError as exc:
        raise ValueError("invalid spot observed_date") from exc
    spot_source = spot.get("source")
    if not isinstance(spot_source, dict):
        raise ValueError("missing spot source")
    _require_https(spot_source.get("source_url"), "spot.source.source_url")

    broker = snapshot.get("broker")
    if not isinstance(broker, dict) or broker.get("name") != "SBI Securities":
        raise ValueError("missing SBI broker block")
    swap = broker.get("swap")
    if not isinstance(swap, dict):
        raise ValueError("missing swap block")
    raw = swap.get("current_raw")
    reference = swap.get("normalized_reference")
    if not isinstance(raw, dict) or not isinstance(reference, dict):
        raise ValueError("swap observations are incomplete")
    _require_number(raw.get("buy_yen_per_10000"), "current raw buy swap")
    _require_number(reference.get("buy_yen_per_10000_per_day"), "daily buy swap")
    if raw.get("award_days") is not None or raw.get("normalized_daily_yen_per_10000") is not None:
        raise ValueError("unverified current raw swap must remain unnormalized")
    _require_https(raw.get("source_url"), "current raw swap source")
    _require_https(reference.get("source_url"), "normalized swap source")

    margin = broker.get("margin_reference")
    loss_cut = broker.get("loss_cut_reference")
    if not isinstance(margin, dict) or not isinstance(loss_cut, dict):
        raise ValueError("margin/loss-cut references are incomplete")
    _require_number(
        margin.get("required_margin_yen", {}).get("3x"),
        "3x required margin",
        positive=True,
    )
    _require_number(
        loss_cut.get("initial_loss_cut_ratio_percent"),
        "initial loss-cut ratio",
        positive=True,
    )
    _require_https(margin.get("source_url"), "margin source")
    _require_https(loss_cut.get("source_url"), "loss-cut source")

    rates = snapshot.get("policy_rates")
    if not isinstance(rates, dict):
        raise ValueError("missing policy rates")
    fed = rates.get("fed")
    boj = rates.get("boj")
    if not isinstance(fed, dict) or not isinstance(boj, dict):
        raise ValueError("policy-rate sources are incomplete")
    fed_low = _require_number(fed.get("target_low_percent"), "Fed target low")
    fed_high = _require_number(fed.get("target_high_percent"), "Fed target high")
    fed_mid = _require_number(fed.get("target_midpoint_percent"), "Fed midpoint")
    if fed_low >= fed_high or round((fed_low + fed_high) / 2, 6) != round(fed_mid, 6):
        raise ValueError("Fed target midpoint is inconsistent")
    _require_number(
        boj.get("uncollateralized_overnight_call_guideline_percent"),
        "BOJ guideline",
    )
    _require_https(fed.get("source_url"), "Fed source")
    _require_https(boj.get("source_url"), "BOJ source")

    contract = snapshot.get("scenario_contract")
    if not isinstance(contract, dict):
        raise ValueError("missing FX scenario contract")
    _require_number(contract.get("leverage"), "scenario leverage", positive=True)
    _require_number(contract.get("usd_notional"), "scenario USD notional", positive=True)
    horizon = contract.get("horizon_days")
    if not isinstance(horizon, int) or isinstance(horizon, bool) or horizon <= 0:
        raise ValueError("scenario horizon_days must be a positive integer")
    scenarios = contract.get("spot_return_scenarios_percent")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("FX scenario list is empty")
    for scenario in scenarios:
        _require_number(scenario, "spot return scenario")
    assumptions = contract.get("assumptions")
    if not isinstance(assumptions, list) or not assumptions:
        raise ValueError("FX scenario assumptions are required")


def analyze_fx_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    validate_fx_snapshot(snapshot)
    spot = float(snapshot["spot"]["value"])
    broker = snapshot["broker"]
    reference = broker["swap"]["normalized_reference"]
    rates = snapshot["policy_rates"]
    contract = snapshot["scenario_contract"]

    leverage = float(contract["leverage"])
    usd_notional = float(contract["usd_notional"])
    horizon_days = int(contract["horizon_days"])
    daily_swap = float(reference["buy_yen_per_10000_per_day"])
    if usd_notional != 10000:
        daily_swap *= usd_notional / 10000

    notional_yen = spot * usd_notional
    initial_equity_yen = notional_yen / leverage
    annualized_swap_yen = daily_swap * horizon_days
    carry_on_notional = annualized_swap_yen / notional_yen
    carry_on_equity = annualized_swap_yen / initial_equity_yen
    break_even_spot_return = -carry_on_notional

    fed_midpoint = float(rates["fed"]["target_midpoint_percent"])
    boj_rate = float(rates["boj"]["uncollateralized_overnight_call_guideline_percent"])
    policy_rate_gap = fed_midpoint - boj_rate

    scenarios = []
    for scenario_percent in contract["spot_return_scenarios_percent"]:
        spot_return = float(scenario_percent) / 100
        equity_return = leverage * spot_return + carry_on_equity
        ending_spot = spot * (1 + spot_return)
        pnl_yen = initial_equity_yen * equity_return
        scenarios.append(
            {
                "spot_return_percent": round(spot_return * 100, 4),
                "ending_spot": round(ending_spot, 4),
                "equity_return_percent": round(equity_return * 100, 4),
                "pnl_yen": round(pnl_yen, 2),
            }
        )

    return {
        "schema_version": "finbi.fx-brief.v1",
        "pair": snapshot["pair"],
        "as_of": snapshot["spot"]["observed_date"],
        "spot": spot,
        "spot_status": snapshot["spot"]["status"],
        "broker": broker["name"],
        "leverage": leverage,
        "usd_notional": usd_notional,
        "notional_yen": round(notional_yen, 2),
        "initial_equity_yen": round(initial_equity_yen, 2),
        "broker_3x_required_margin_reference_yen": float(
            broker["margin_reference"]["required_margin_yen"]["3x"]
        ),
        "broker_margin_reference_date": broker["margin_reference"]["application_date"],
        "initial_loss_cut_ratio_percent": float(
            broker["loss_cut_reference"]["initial_loss_cut_ratio_percent"]
        ),
        "current_raw_buy_swap_yen_per_10000": float(
            broker["swap"]["current_raw"]["buy_yen_per_10000"]
        ),
        "current_raw_swap_application_date": broker["swap"]["current_raw"][
            "application_date"
        ],
        "current_raw_swap_normalized": False,
        "scenario_daily_buy_swap_yen_per_10000": float(
            reference["buy_yen_per_10000_per_day"]
        ),
        "scenario_swap_reference_date": reference["application_date"],
        "annualized_swap_yen": round(annualized_swap_yen, 2),
        "carry_on_notional_percent": round(carry_on_notional * 100, 4),
        "carry_on_initial_equity_percent": round(carry_on_equity * 100, 4),
        "break_even_spot_return_percent": round(break_even_spot_return * 100, 4),
        "fed_target_midpoint_percent": fed_midpoint,
        "boj_policy_rate_percent": boj_rate,
        "policy_rate_gap_percentage_points": round(policy_rate_gap, 4),
        "scenarios": scenarios,
        "assumptions": contract["assumptions"],
        "sources": {
            "spot": snapshot["spot"]["source"]["source_url"],
            "swap_current_raw": broker["swap"]["current_raw"]["source_url"],
            "swap_scenario_reference": reference["source_url"],
            "margin": broker["margin_reference"]["source_url"],
            "loss_cut": broker["loss_cut_reference"]["source_url"],
            "fed": rates["fed"]["source_url"],
            "boj": rates["boj"]["source_url"],
        },
        "retrieved_at": snapshot["retrieved_at"],
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


def analyze_fx_snapshot_json(snapshot_json: str) -> str:
    result = analyze_fx_snapshot(json.loads(snapshot_json))
    return json.dumps(result, ensure_ascii=False, sort_keys=True)
