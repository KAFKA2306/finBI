const SNAPSHOT_URL = "./data/snapshots/fred-dgs10-2026-07-20_2026-07-23.json";
const worker = new Worker("./worker.mjs", { type: "module" });
const SVG_NS = "http://www.w3.org/2000/svg";

const start = document.querySelector("#start");
const end = document.querySelector("#end");
const compareButton = document.querySelector("#compare");
const status = document.querySelector("#status");
const headline = document.querySelector("#headline");
const story = document.querySelector("#story");
const metadata = document.querySelector("#metadata");
const sourceLink = document.querySelector("#source-link");
const seriesName = document.querySelector("#series-name");
const windowLabel = document.querySelector("#window-label");
const quickPicks = document.querySelector("#quick-picks");
const chart = document.querySelector("#chart");
const chartDesc = document.querySelector("#chart-desc");
const chartHint = document.querySelector("#chart-hint");

let snapshot;
let pending = false;
let chartPickPhase = "start";

function el(name, attrs = {}, text = null) {
  const node = document.createElementNS(SVG_NS, name);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  if (text !== null) node.textContent = text;
  return node;
}

function addMeta(label, value) {
  const group = document.createElement("div");
  const term = document.createElement("dt");
  const definition = document.createElement("dd");
  term.textContent = label;
  definition.textContent = value;
  group.append(term, definition);
  metadata.append(group);
}

function formatDate(value) {
  return new Intl.DateTimeFormat("ja-JP", { month: "short", day: "numeric" }).format(new Date(`${value}T00:00:00Z`));
}

function formatNumber(value) {
  return new Intl.NumberFormat("ja-JP", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value);
}

function selectedPointLabel(row, role) {
  return `${role} ${formatDate(row.date)} · ${formatNumber(row.value)}%`;
}

function chooseChartPoint(date) {
  if (chartPickPhase === "start") {
    start.value = date;
    chartPickPhase = "end";
    status.textContent = `${formatDate(date)}を開始日にしました。次に終了日を選んでください。`;
    chartHint.textContent = "2点目を選ぶと比較します。selectから選ぶ方法も使えます。";
    renderChart();
    return;
  }

  if (date <= start.value) {
    status.textContent = "終了日は開始日より後の点を選んでください。";
    return;
  }
  end.value = date;
  chartPickPhase = "start";
  chartHint.textContent = "グラフの点を2つ選ぶと比較できます。1点目が開始日、2点目が終了日です。";
  runComparison();
}

function renderChart(selectedStart = start.value, selectedEnd = end.value) {
  const rows = snapshot.observations;
  const values = rows.map((row) => row.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const spread = Math.max(max - min, 0.02);
  const pad = spread * 0.28;
  const low = min - pad;
  const high = max + pad;
  const width = 760;
  const height = 360;
  const left = 58;
  const right = 26;
  const top = 28;
  const bottom = 52;
  const plotWidth = width - left - right;
  const plotHeight = height - top - bottom;
  const x = (index) => left + (plotWidth * index) / Math.max(rows.length - 1, 1);
  const y = (value) => top + ((high - value) / (high - low)) * plotHeight;

  chart.querySelectorAll(".dynamic").forEach((node) => node.remove());

  for (let i = 0; i < 3; i += 1) {
    const yy = top + (plotHeight * i) / 2;
    chart.append(el("line", { x1: left, x2: width - right, y1: yy, y2: yy, class: "chart-grid dynamic" }));
    const labelValue = high - ((high - low) * i) / 2;
    chart.append(el("text", { x: 4, y: yy + 4, class: "chart-label dynamic" }, formatNumber(labelValue)));
  }

  const points = rows.map((row, index) => [x(index), y(row.value)]);
  const linePath = points.map(([px, py], index) => `${index === 0 ? "M" : "L"} ${px} ${py}`).join(" ");
  const areaPath = `${linePath} L ${points.at(-1)[0]} ${height - bottom} L ${points[0][0]} ${height - bottom} Z`;
  chart.append(el("path", { d: areaPath, class: "chart-area dynamic" }));
  chart.append(el("path", { d: linePath, class: "chart-line dynamic" }));

  rows.forEach((row, index) => {
    const isStart = row.date === selectedStart;
    const isEnd = row.date === selectedEnd;
    const selected = isStart || isEnd;
    const [cx, cy] = points[index];
    const dot = el("circle", {
      cx,
      cy,
      r: selected ? 7 : 5,
      class: `chart-dot dynamic${selected ? " is-selected" : ""}`,
      "aria-hidden": "true",
    });
    const hit = el("circle", {
      cx,
      cy,
      r: 18,
      class: "chart-hit dynamic",
      role: "button",
      "aria-label": `${row.date} ${formatNumber(row.value)}%。比較点として選択`,
      tabindex: "-1",
      "data-date": row.date,
    });
    hit.addEventListener("click", () => chooseChartPoint(row.date));
    chart.append(dot, hit);

    if (selected) {
      const role = isStart ? "開始" : "終了";
      const labelX = Math.min(Math.max(cx, 100), width - 100);
      const labelY = Math.max(cy - 18, 20);
      chart.append(el("text", {
        x: labelX,
        y: labelY,
        "text-anchor": "middle",
        class: "chart-selected-label dynamic",
      }, selectedPointLabel(row, role)));
    }
  });

  chart.append(el("text", { x: left, y: height - 14, class: "chart-label dynamic" }, formatDate(rows[0].date)));
  chart.append(el("text", { x: width - right, y: height - 14, "text-anchor": "end", class: "chart-label dynamic" }, formatDate(rows.at(-1).date)));
  chartDesc.textContent = `${snapshot.source.series_name}。${rows[0].date}から${rows.at(-1).date}までの${rows.length}観測。選択日は${selectedStart}と${selectedEnd}です。`;
}

function setBusy(value) {
  pending = value;
  compareButton.disabled = value;
  compareButton.textContent = value ? "計算中…" : "比べる";
}

function runComparison() {
  if (!snapshot || pending) return;
  if (start.value >= end.value) {
    status.textContent = "終了日は開始日より後を選んでください。";
    return;
  }
  setBusy(true);
  status.textContent = "比較を計算しています…";
  renderChart();
  worker.postMessage({ snapshot, startDate: start.value, endDate: end.value });
}

function addQuickPick(startDate, endDate, prefix) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "chip";
  button.textContent = `${prefix} ${formatDate(startDate)} → ${formatDate(endDate)}`;
  button.addEventListener("click", () => {
    start.value = startDate;
    end.value = endDate;
    chartPickPhase = "start";
    runComparison();
  });
  quickPicks.append(button);
}

worker.addEventListener("message", (event) => {
  setBusy(false);
  if (event.data.error) {
    status.textContent = `計算失敗: ${event.data.error}`;
    headline.textContent = "—";
    story.textContent = "snapshotと比較条件を確認してください。";
    return;
  }

  const out = event.data.result;
  const arrow = out.direction === "up" ? "↗" : out.direction === "down" ? "↘" : "→";
  const sign = out.basis_points > 0 ? "+" : "";
  const bpText = out.basis_points === null ? `${sign}${formatNumber(out.delta)} ${out.unit}` : `${sign}${formatNumber(out.basis_points)} bp`;
  headline.textContent = `${arrow} ${bpText}`;
  const pointSign = out.delta > 0 ? "+" : "";
  const pointText = out.basis_points === null ? "" : ` 差は${pointSign}${formatNumber(out.delta)} percentage point = ${sign}${formatNumber(out.basis_points)} bpです。`;
  story.textContent = `${formatDate(out.start_date)} ${formatNumber(out.start_value)}% → ${formatDate(out.end_date)} ${formatNumber(out.end_value)}%。${pointText}${out.calendar_days}暦日の比較です。`;
  status.textContent = `比較完了 · snapshot取得 ${out.retrieved_at}`;
});

worker.addEventListener("error", (event) => {
  setBusy(false);
  status.textContent = `計算処理を起動できません: ${event.message}`;
});

compareButton.addEventListener("click", () => {
  chartPickPhase = "start";
  runComparison();
});
start.addEventListener("change", () => {
  chartPickPhase = "start";
  renderChart();
});
end.addEventListener("change", () => {
  chartPickPhase = "start";
  renderChart();
});

async function init() {
  const response = await fetch(SNAPSHOT_URL);
  if (!response.ok) throw new Error(`snapshot fetch failed: ${response.status}`);
  snapshot = await response.json();
  const dates = snapshot.observations.map((row) => row.date);

  for (const date of dates) {
    for (const select of [start, end]) {
      const option = document.createElement("option");
      option.value = date;
      option.textContent = date;
      select.append(option);
    }
  }

  start.value = dates[0];
  end.value = dates.at(-1);
  seriesName.textContent = `${snapshot.source.series_id} · 米国10年国債利回り`;
  windowLabel.textContent = `${snapshot.observation_start} → ${snapshot.observation_end}`;
  sourceLink.href = snapshot.source.source_url;

  addMeta("Series", snapshot.source.series_id);
  addMeta("単位", snapshot.unit);
  addMeta("頻度", snapshot.frequency);
  addMeta("季節調整", snapshot.seasonal_adjustment);
  addMeta("観測期間", `${snapshot.observation_start} → ${snapshot.observation_end}`);
  addMeta("取得時刻", snapshot.retrieved_at);

  addQuickPick(dates[0], dates.at(-1), "全期間");
  if (dates.length >= 3) addQuickPick(dates[0], dates[1], "最初");
  if (dates.length >= 3) addQuickPick(dates.at(-2), dates.at(-1), "直近");

  renderChart();
  status.textContent = "データを読み込みました。";
  runComparison();
}

init().catch((error) => {
  setBusy(false);
  status.textContent = `初期化失敗: ${error.message}`;
  seriesName.textContent = "snapshotを読み込めませんでした";
});
