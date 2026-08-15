import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.2/full/pyodide.mjs";

const runtimePromise = loadPyodide();
const sourcePromise = fetch("./code/static_bi.py").then((response) => {
  if (!response.ok) throw new Error(`Python source fetch failed: ${response.status}`);
  return response.text();
});
let coreLoaded = false;

async function getRuntime() {
  const pyodide = await runtimePromise;
  if (!coreLoaded) {
    pyodide.runPython(await sourcePromise);
    coreLoaded = true;
  }
  return pyodide;
}

self.onmessage = async (event) => {
  try {
    const pyodide = await getRuntime();
    pyodide.globals.set("snapshot_json", JSON.stringify(event.data.snapshot));
    pyodide.globals.set("short_snapshot_json", JSON.stringify(event.data.shortSnapshot));
    pyodide.globals.set("start_date", event.data.startDate);
    pyodide.globals.set("end_date", event.data.endDate);
    const movement = pyodide.runPython("compare_dates_json(snapshot_json, start_date, end_date)");
    const brief = pyodide.runPython(
      "compare_curve_json(snapshot_json, short_snapshot_json, start_date, end_date)",
    );
    self.postMessage({ result: JSON.parse(movement), brief: JSON.parse(brief) });
  } catch (error) {
    self.postMessage({ error: String(error) });
  }
};
