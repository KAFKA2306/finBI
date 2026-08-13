# Canonical architecture

```text
verified JSON snapshot
        │
        ├──→ app.js ──→ SVG / controls / provenance
        │                 │
        │                 └── postMessage
        │                       ↓
        └──────────────→ worker.mjs ──→ Pyodide ──→ code/static_bi.py
                                              │
                                              └── comparison result
```

The repository intentionally has no application server, browser financial API client, credential layer, database, frontend framework, bundler, or duplicate JavaScript financial formula.

The same `static_bi.py` executed by offline tests is fetched by the public Web Worker. This is the architectural invariant CI should protect.
