const LONG_URL = "./data/snapshots/fred-dgs10-2026-07-20_2026-07-23.json";
const SHORT_URL = "./data/snapshots/fred-dgs2-2026-07-20_2026-07-23.json";

const headline = document.querySelector("#curve-brief-headline");
const detail = document.querySelector("#curve-brief-detail");
const status = document.querySelector("#curve-brief-status");
const start = document.querySelector("#start");
const end = document.querySelector("#end");
const compare = document.querySelector("#compare");
const longSource = document.querySelector("#curve-long-source");
const shortSource = document.querySelector("#curve-short-source");
const worker = new Worker("./worker.mjs", { type: "module" });

let longSnapshot;
let shortSnapshot;
let requestKey = null;

function signed(value) {
  return `${value > 0 ? "+" : ""}${value.toFixed(1)}`;
}

function requestBrief() {
  if (!longSnapshot || !shortSnapshot || !start.value || !end.value || start.value >= end.value) return;
  const nextKey = `${start.value}:${end.value}`;
  if (nextKey === requestKey) return;
  requestKey = nextKey;
  status.textContent = "2s10sを計算しています…";
  worker.postMessage({
    snapshot: longSnapshot,
    shortSnapshot,
    startDate: start.value,
    endDate: end.value,
  });
}

worker.addEventListener("message", (event) => {
  if (event.data.error) {
    status.textContent = `2s10s計算失敗: ${event.data.error}`;
    return;
  }
  const brief = event.data.brief;
  const shape = brief.curve_shape === "FLATTENED" ? "フラット化" : brief.curve_shape === "STEEPENED" ? "スティープ化" : "横ばい";
  headline.textContent = `${brief.start_spread_bp.toFixed(1)} bp → ${brief.end_spread_bp.toFixed(1)} bp · ${shape}`;
  detail.textContent = `10年は${signed(brief.long_move_bp)} bp、2年は${signed(brief.short_move_bp)} bp。2s10sスプレッドは${signed(brief.spread_change_bp)} bp変化したため、「この期間にスティープ化した」という仮説は${brief.decision}です。`;
  status.textContent = `${brief.start_date} → ${brief.end_date} · ${brief.unit} · verified snapshots`;
});

worker.addEventListener("error", (event) => {
  status.textContent = `2s10s workerを起動できません: ${event.message}`;
});

async function init() {
  const [longResponse, shortResponse] = await Promise.all([fetch(LONG_URL), fetch(SHORT_URL)]);
  if (!longResponse.ok || !shortResponse.ok) throw new Error("comparison snapshot fetch failed");
  [longSnapshot, shortSnapshot] = await Promise.all([longResponse.json(), shortResponse.json()]);
  longSource.href = longSnapshot.source.source_url;
  shortSource.href = shortSnapshot.source.source_url;
  const refresh = () => {
    requestKey = null;
    requestBrief();
  };
  start.addEventListener("change", refresh);
  end.addEventListener("change", refresh);
  compare.addEventListener("click", refresh);
  const timer = setInterval(() => {
    if (start.value && end.value) {
      clearInterval(timer);
      requestBrief();
    }
  }, 50);
}

init().catch((error) => {
  status.textContent = `2s10s初期化失敗: ${error.message}`;
});
