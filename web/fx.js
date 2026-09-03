const FX_OVERLAY_URL = "./data/snapshots/investor2-fx-overlay.json";
const FX_OVERLAY_SCHEMA = "investor2.fx-overlay.v1";

const fxStyles = document.createElement("link");
fxStyles.rel = "stylesheet";
fxStyles.href = "./fx.css";
document.head.append(fxStyles);

const status = document.querySelector("#fx-status");
const percent = new Intl.NumberFormat("ja-JP", {
  style: "percent",
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});
const decimal = new Intl.NumberFormat("ja-JP", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

function setText(selector, value) {
  const element = document.querySelector(selector);
  if (element) element.textContent = value;
}

function optionalPercent(value) {
  return Number.isFinite(value) ? percent.format(value) : "—";
}

function optionalDecimal(value) {
  return Number.isFinite(value) ? decimal.format(value) : "—";
}

function clearCanonicalMetrics() {
  for (const selector of [
    "#fx-current-exposure",
    "#fx-current-exposure-detail",
    "#fx-incremental-exposure",
    "#fx-incremental-exposure-detail",
    "#fx-total-exposure",
    "#fx-hedge-ratio",
    "#fx-margin-requirement",
    "#fx-liquidation-headroom",
    "#fx-cagr",
    "#fx-volatility",
    "#fx-sharpe",
    "#fx-max-drawdown",
    "#fx-expected-shortfall",
    "#fx-turnover",
  ]) {
    setText(selector, "—");
  }
}

function validateOverlay(result) {
  if (!result || result.schema_version !== FX_OVERLAY_SCHEMA) {
    throw new Error("unsupported canonical FX overlay schema");
  }
  if (!new Set(["VERIFIED", "TEST_ONLY", "UNVERIFIED"]).has(result.status)) {
    throw new Error("unsupported canonical FX overlay status");
  }
  if (result.status === "UNVERIFIED" && !result.reason) {
    throw new Error("UNVERIFIED canonical output requires a reason");
  }
}

function renderVerified(result) {
  const current = optionalPercent(result.currentUsdExposure);
  const incremental = optionalPercent(result.recommendedIncrementalUsdExposure);
  setText("#fx-current-exposure", current);
  setText("#fx-current-exposure-detail", current);
  setText("#fx-incremental-exposure", incremental);
  setText("#fx-incremental-exposure-detail", incremental);
  setText("#fx-total-exposure", optionalPercent(result.recommendedTotalUsdExposure));
  setText("#fx-hedge-ratio", optionalDecimal(result.hedgeRatio));
  setText("#fx-margin-requirement", optionalPercent(result.marginRequirementFraction));
  setText(
    "#fx-liquidation-headroom",
    optionalPercent(result.liquidationHeadroomFraction),
  );

  const oos = result.oos ?? {};
  setText("#fx-cagr", optionalPercent(oos.cagr));
  setText("#fx-volatility", optionalPercent(oos.annualizedVolatility));
  setText("#fx-sharpe", optionalDecimal(oos.sharpe));
  setText("#fx-max-drawdown", optionalPercent(oos.maxDrawdown));
  setText("#fx-expected-shortfall", optionalPercent(oos.expectedShortfall95));
  setText("#fx-turnover", optionalDecimal(oos.turnover));
  setText(
    "#fx-reason",
    result.status === "TEST_ONLY"
      ? "Canonical calculation completed with test-fixture evidence. Production recommendation is not verified."
      : "Canonical investor2 output is verified. finBI is displaying it without recalculation.",
  );
}

function renderOverlay(result) {
  validateOverlay(result);
  setText("#fx-schema", result.schema_version);
  setText("#fx-overlay-status", result.status);
  clearCanonicalMetrics();

  if (result.status === "UNVERIFIED") {
    setText("#fx-reason", result.reason);
  } else {
    renderVerified(result);
  }

  status.textContent = `${result.status} · read-only investor2 output · finBI calculation authorityなし`;
}

async function initFx() {
  try {
    const response = await fetch(FX_OVERLAY_URL);
    if (!response.ok) throw new Error(`canonical output fetch failed: ${response.status}`);
    renderOverlay(await response.json());
  } catch (error) {
    clearCanonicalMetrics();
    setText("#fx-overlay-status", "UNVERIFIED");
    setText("#fx-reason", `Canonical outputを読み込めません: ${error.message}`);
    status.textContent = "UNVERIFIED · fail closed";
  }
}

initFx();
