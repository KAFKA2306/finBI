# Repository Agent Contract

## Mission

Own point-in-time market-observation comparison views for this repository. Present versioned market observations in a way that preserves source/as-of semantics and helps compare instruments or periods without becoming a duplicate primary-source warehouse.

## Canonical authority

- Consume versioned observations from their owning canonical source/provider/repository when possible; do not create a second authority merely for presentation.
- Preserve instrument identity, timestamp/as-of, market session/field, unit/currency, source/provenance and point-in-time semantics required by the current view.
- Keep observed values, deterministic derived comparisons and interpretation distinct.

## Autonomous execution

1. Inspect current `main`, README, open Issues/PRs, canonical inputs, view artifacts, workflows/tests and deployed public surface.
2. Continue one canonical workline before adding another data store, chart layer, branch or Issue.
3. Prefer correction of point-in-time/source semantics, a working comparison user flow, production read-back, or deletion/consolidation of duplicate views/data paths.
4. Use source data by reference/version/hash where practical rather than copying the same fact into another maintained dataset.
5. Run focused deterministic/UI checks and verify reviewed/merged/production state when applicable.
6. Stop at the fixed point; do not add charts or metrics that do not change a user decision/comparison task.

## Boundaries

- Do not infer prices, returns, timestamps, sessions or missing market observations.
- Do not relabel stale/cached data as live or real-time.
- Do not execute trades, transfers or account actions.
- Browser/local state is not durable analytics unless a canonical backend/source proves it.
- Unobserved source, CI, deployment or user outcomes remain unverified.

## Completion report

Report user/data outcome Before -> After, owning source/canonical view, Issue/PR/commit/check/production evidence when applicable, duplicate authority/manual work removed, and remaining blocker.