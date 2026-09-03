const FX_SNAPSHOT_URL = "./data/snapshots/usdjpy-sbi-2026-09-03.json";

const worker = new Worker("./worker.mjs", { type: "module" });
const status = document.querySelector("#fx-status");
const scenarioBody = document.querySelector("#fx-scenarios");

function number(value, digits = 2) {
  return Number(value).toLocaleString("ja-JP", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function signed(value, digits = 2, suffix = "") {
  const numeric = Number(value);
  const prefix = numeric > 0 ? "+" : "";
  return `${prefix}${number(numeric, digits)}${suffix}`;
}

function setText(selector, value) {
  const element = document.querySelector(selector);
  if (element) element.textContent = value;
}

function setSource(selector, href) {
  const link = document.querySelector(selector);
  if (link) link.href = href;
}

function renderScenarios(rows) {
  scenarioBody.replaceChildren();
  for (const row of rows) {
    const tr = document.createElement("tr");
    const values = [
      signed(row.spot_return_percent, 1, "%"),
      number(row.ending_spot, 2),
      signed(row.equity_return_percent, 2, "%"),
      signed(row.pnl_yen, 0, "円"),
    ];
    for (const value of values) {
      const td = document.createElement("td");
      td.textContent = value;
      tr.append(td);
    }
    scenarioBody.append(tr);
  }
}

function renderBrief(brief) {
  setText("#fx-spot", number(brief.spot, 2));
  setText("#fx-asof", `as of ${brief.as_of}`);
  setText("#fx-carry", `${number(brief.carry_on_initial_equity_percent, 2)}%`);
  setText("#fx-break-even", `${number(brief.break_even_spot_return_percent, 2)}%`);
  setText("#fx-rate-gap", `${number(brief.policy_rate_gap_percentage_points, 3)} pp`);
  setText("#fx-fed", `${number(brief.fed_target_midpoint_percent, 3)}%`);
  setText("#fx-boj", `${number(brief.boj_policy_rate_percent, 3)}%`);
  setText(
    "#fx-swap-current",
    `${number(brief.current_raw_buy_swap_yen_per_10000, 0)}円 / 1万USD`,
  );
  setText(
    "#fx-swap-reference",
    `${number(brief.scenario_daily_buy_swap_yen_per_10000, 0)}円/日 · ${brief.scenario_swap_reference_date}`,
  );
  setText("#fx-notional", `${number(brief.notional_yen, 0)}円`);
  setText("#fx-equity", `${number(brief.initial_equity_yen, 0)}円`);
  setText(
    "#fx-margin-reference",
    `${number(brief.broker_3x_required_margin_reference_yen, 0)}円 · ${brief.broker_margin_reference_date}`,
  );
  setText(
    "#fx-loss-cut",
    `${number(brief.initial_loss_cut_ratio_percent, 0)}% 初期設定`,
  );
  setText("#fx-annual-swap", `${number(brief.annualized_swap_yen, 0)}円/年`);

  setSource("#fx-source-spot", brief.sources.spot);
  setSource("#fx-source-swap", brief.sources.swap_current_raw);
  setSource("#fx-source-margin", brief.sources.margin);
  setSource("#fx-source-fed", brief.sources.fed);
  setSource("#fx-source-boj", brief.sources.boj);
  renderScenarios(brief.scenarios);

  const assumptions = document.querySelector("#fx-assumptions");
  assumptions.replaceChildren();
  for (const item of brief.assumptions) {
    const li = document.createElement("li");
    li.textContent = item;
    assumptions.append(li);
  }

  status.textContent = `verified snapshot + deterministic Python scenario · retrieved ${brief.retrieved_at}`;
}

worker.addEventListener("message", (event) => {
  if (event.data.kind !== "fx") return;
  if (event.data.error) {
    status.textContent = `FX BIを計算できません: ${event.data.error}`;
    return;
  }
  renderBrief(event.data.brief);
});

async function initFx() {
  try {
    const response = await fetch(FX_SNAPSHOT_URL);
    if (!response.ok) throw new Error(`snapshot fetch failed: ${response.status}`);
    const snapshot = await response.json();
    worker.postMessage({ kind: "fx", snapshot });
  } catch (error) {
    status.textContent = `FX snapshotを読み込めません: ${error.message}`;
  }
}

initFx();
