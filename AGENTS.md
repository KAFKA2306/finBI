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
5. Run focused deterministic/UI checks and verify the exact reviewed revision before merge.
6. Stop at the fixed point; do not add charts or metrics that do not change a user decision/comparison task.

## Merge and release are separate

### PR merge conditions

A PR may merge when the repository-local view/data contract is correct on the exact head revision: point-in-time/source semantics are preserved, relevant deterministic/UI tests pass, generated output is reproducible when affected, and no unresolved review or correctness blocker remains.

A production URL, field analytics, deployment completion, fresh market observation after merge, or actual user traffic is **not** a merge condition unless the PR specifically changes the release mechanism and pre-merge validation of that mechanism is part of the bounded contract.

### Product release conditions

Release is a separate post-merge decision. Treat a public market view as released only after the merged `main` revision and the actual production surface are read back and verified, including deployment identity and the material user path when in scope. Field analytics or user outcomes are evidence of operation/adoption, not proof required for ordinary code merge.

A merged PR does not prove production release. A production blocker does not retroactively invalidate a correctly merged repository change. Report merge and release independently.

## Boundaries

- Do not infer prices, returns, timestamps, sessions or missing market observations.
- Do not relabel stale/cached data as live or real-time.
- Do not execute trades, transfers or account actions.
- Browser/local state is not durable analytics unless a canonical backend/source proves it.
- Unobserved source, CI, deployment or user outcomes remain unverified.

## Completion report

Report user/data outcome Before -> After, owning source/canonical view, Issue/PR/commit/check evidence, then report `merged` and `released` separately with direct evidence for each. Include production evidence only for the release side, duplicate authority/manual work removed, and remaining blocker.