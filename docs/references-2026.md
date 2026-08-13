# 2026 reference set

Reviewed on 2026-08-13. These are design references, not runtime dependencies unless stated otherwise.

## Browser Python

- Pyodide Web Worker documentation: https://pyodide.org/en/stable/usage/webworker.html
- Pyodide 314 release notes: https://blog.pyodide.org/posts/314-release/

Decision: keep Pyodide as the only analytical browser runtime. Run it in a module Web Worker and pin the runtime version used by the application.

## Browser analytics OSS considered

- DuckDB-Wasm: https://duckdb.org/docs/stable/clients/wasm/overview
- Perspective: https://github.com/perspective-dev/perspective
- marimo: https://github.com/marimo-team/marimo
- Vega-Lite: https://vega.github.io/vega-lite/

Decision: borrow their browser-local, declarative, reactive, reproducible design patterns without adding their runtime weight to a five-row snapshot application.

## Research

- Data Visualization for Improving Financial Literacy: A Systematic Review (2025): https://arxiv.org/abs/2506.20901
- ProVega: A Grammar to Ease the Prototyping, Creation, and Reproducibility of Progressive Data Analysis and Visualization Solutions (2026): https://arxiv.org/abs/2604.02096
- Formal Semantics and Type System for Vega Data Transformations (2026): https://arxiv.org/abs/2606.15013

Decision: optimize for interpretability, reproducibility, and immediate feedback rather than maximum chart count.

## Web accessibility and deployment

- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- GitHub Pages custom workflows: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- configure-pages: https://github.com/actions/configure-pages
- upload-pages-artifact: https://github.com/actions/upload-pages-artifact
- deploy-pages: https://github.com/actions/deploy-pages

Decision: treat keyboard visibility, control target size, reduced motion, provenance, and public-route smoke testing as product requirements rather than polish.
