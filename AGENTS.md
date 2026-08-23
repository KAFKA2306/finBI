# Repository Agent Contract

## Mission

Own point-in-time market-observation comparison views for this repository. Present versioned observations with source/as-of semantics so users can compare instruments or periods without turning finBI into a second primary-source warehouse.

## Canonical authority

- Consume versioned observations from their owning source/provider/repository when possible; do not create a second authority merely for presentation.
- Preserve instrument identity, timestamp/as-of, market session/field, unit/currency, source/provenance and point-in-time semantics required by the view.
- Keep observed values, deterministic derived comparisons and interpretation distinct.

## Simplification

- Keep current executable mechanisms on the current surface; keep future work in Issues or target design.
- One responsibility should have one canonical entry point, data authority and implementation path.
- Remove dead code, stale docs/config, duplicate wrappers, completed scaffolding and repository-local compatibility once evidence shows they are no longer required.
- Prefer source data plus deterministic derivation over storing a second maintained copy of derived results.
- Test deletion hypotheses; restore anything that direct evidence shows is still required.
- Preserve migration/data-safety controls until their completion criteria are actually satisfied.
- Put machine-decidable rules in tests/CI instead of prose when practical.

## Autonomous execution

1. Inspect current `main`, README, open Issues/PRs, canonical inputs, view artifacts, workflows/tests and the deployed public surface when release evidence is in scope.
2. Continue one canonical workline before adding another data store, chart layer or Issue.
3. Prefer correction of point-in-time/source semantics, a working comparison flow, production read-back, or deletion/consolidation of duplicate views/data paths.
4. Use source data by reference/version/hash where practical rather than copying the same fact into another maintained dataset.
5. Run focused deterministic/UI checks and verify the exact reviewed revision before merge.
6. Stop at the fixed point; do not add charts or metrics that do not change a user decision/comparison task.

## Merge and release are separate

A PR may merge when the repository-local view/data contract is correct on the exact head revision: point-in-time/source semantics are preserved, relevant deterministic/UI tests pass, generated output is reproducible when affected, and no unresolved correctness blocker remains.

Release is a separate post-merge decision. Treat a public view as released only after the merged `main` revision and actual production surface are read back and verified when release is in scope. Field analytics or user outcomes are evidence of operation/adoption, not ordinary merge prerequisites.

A merged PR does not prove production release. A production blocker does not retroactively invalidate a correctly merged repository change. Report merge and release independently.

## Boundaries

- Do not infer prices, returns, timestamps, sessions or missing market observations.
- Do not relabel stale/cached data as live or real-time.
- Do not execute trades, transfers or account actions.
- Browser/local state is not durable analytics unless a canonical backend/source proves it.
- Unobserved source, CI, deployment or user outcomes remain unverified.

## Completion report

Report user/data outcome Before -> After, owning source/canonical view, Issue/PR/commit/check evidence, `merged` and `released` separately, duplicate authority/manual work removed, and remaining blockers.
