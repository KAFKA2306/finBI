# finBI Pages design baseline (2026-08-13)

## Goal

Make a public financial-data page that a first-time visitor can understand without reading the repository, while keeping provenance and financial calculations auditable.

## Adopted ideas

- **Pyodide Web Worker**: run the repository's canonical Python in the browser without a server and without blocking the UI.
- **Declarative visualization principles**: keep visual encodings explicit and simple; use one primary time-series view instead of a dashboard wall.
- **Reactive / reproducible notebook practice**: an input change should deterministically update the dependent result, while source data and code remain version-controlled.
- **WCAG 2.2 baseline**: visible focus, large controls, keyboard operation, no drag-only interaction, reduced-motion support, and semantic status text.
- **Progressive disclosure**: show the answer, source, and interaction first; put implementation detail behind an optional disclosure.

## Deliberately not adopted yet

### DuckDB-Wasm
Useful when committed datasets grow large enough that client-side SQL, Parquet, or Arrow materially reduces complexity. A five-row JSON snapshot does not justify a second analytical runtime.

### Perspective
Excellent for user-configurable analytics, large/streaming datasets, datagrids, and many chart types. finBI currently benefits more from one opinionated question and one chart than from a configurable BI workspace.

### marimo as the public runtime
marimo's reproducible, git-friendly, WASM app model is a strong reference, but replacing the current three-file static UI with a notebook runtime would increase shipped surface area. Its reactive design principles are adopted without adding the runtime dependency.

## Product contract

1. A visitor can tell what the number is, what period it covers, and where it came from on one screen.
2. Two dates are enough to get a meaningful comparison.
3. Basis-point and direction calculations exist only in `code/static_bi.py`.
4. JavaScript owns I/O, interaction, formatting, and SVG rendering only.
5. No browser API keys and no live financial API calls.
6. The current snapshot is never presented as a current market value.
7. The public root URL is the app itself; no `/web/` redirect is required.
8. Large analytical dependencies are added only after a measured need exists.

## Revisit thresholds

- Consider DuckDB-Wasm when snapshot storage moves to Parquet/Arrow or client-side filtering over materially larger tables becomes necessary.
- Consider Perspective when users need arbitrary grouping, pivoting, or multi-chart self-service analysis.
- Consider marimo export when the product becomes primarily a Python-authored interactive explanatory notebook rather than a compact public product page.
