const SNAPSHOT_URL = "../data/snapshots/fred-dgs10-2026-07-20_2026-07-24.json";
const worker = new Worker("./worker.mjs", { type: "module" });
const start = document.querySelector("#start");
const end = document.querySelector("#end");
const status = document.querySelector("#status");
const result = document.querySelector("#result");
const metadata = document.querySelector("#metadata");
let snapshot;
function addMeta(label, value) { const div=document.createElement("div"); const strong=document.createElement("strong"); strong.textContent=label; div.append(strong,document.createElement("br"),document.createTextNode(value)); metadata.append(div); }
async function init(){ const response=await fetch(SNAPSHOT_URL); if(!response.ok) throw new Error(`snapshot fetch failed: ${response.status}`); snapshot=await response.json(); const dates=snapshot.observations.map(row=>row.date); for(const date of dates){ for(const select of [start,end]){ const option=document.createElement("option"); option.value=date; option.textContent=date; select.append(option); } } start.value=dates[0]; end.value=dates[dates.length-1]; addMeta("Series",snapshot.source.series_id); addMeta("Unit",snapshot.unit); addMeta("Currency",snapshot.currency ?? "N/A"); addMeta("Observed",`${snapshot.observation_start} - ${snapshot.observation_end}`); addMeta("Retrieved",snapshot.retrieved_at); const link=document.createElement("a"); link.href=snapshot.source.source_url; link.textContent="FRED / H.15 source"; metadata.append(link); status.textContent="準備完了。計算時だけPyodideを読み込みます。"; }
worker.addEventListener("message",event=>{ if(event.data.error){ status.textContent=`計算失敗: ${event.data.error}`; return; } const out=event.data.result; result.textContent=`${out.start_date}: ${out.start_value} -> ${out.end_date}: ${out.end_value} ${out.unit} (delta ${out.delta})`; status.textContent=`Python計算完了 / retrieved_at: ${out.retrieved_at}`; });
document.querySelector("#compare").addEventListener("click",()=>{ status.textContent="Pyodideで計算中..."; result.textContent=""; worker.postMessage({snapshot,startDate:start.value,endDate:end.value}); });
init().catch(error=>{ status.textContent=`初期化失敗: ${error.message}`; });
