import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.2/full/pyodide.mjs";
let runtime;
async function getRuntime(){ if(!runtime) runtime=loadPyodide(); return runtime; }
self.onmessage=async(event)=>{ try{ const pyodide=await getRuntime(); const source=await (await fetch("../code/static_bi.py")).text(); pyodide.runPython(source); pyodide.globals.set("snapshot_json",JSON.stringify(event.data.snapshot)); pyodide.globals.set("start_date",event.data.startDate); pyodide.globals.set("end_date",event.data.endDate); const output=pyodide.runPython("compare_dates_json(snapshot_json, start_date, end_date)"); self.postMessage({result:JSON.parse(output)}); }catch(error){ self.postMessage({error:String(error)}); } };
