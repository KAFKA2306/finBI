# Repository Agent Contract

## Mission

Own the **financial decision surface and question-to-analysis semantic layer** for this repository.

finBI is not a second primary-source warehouse and not merely a chart collection. Its job is to turn recurring questions into reproducible decision workflows:

`question -> required data -> observed facts -> deterministic calculation -> comparison/scenario -> decision implication -> provenance`

The current two-date Treasury comparison remains supported, but it is one `Rates Desk` recipe rather than the product mission.

## Product scope

Canonical desks may cover:

- Command Center
- Portfolio / allocation / overlap / risk contribution / rebalance
- Efficient Frontier / what-if allocation
- FX / carry / leverage / margin / liquidation stress
- Rates / bonds / real yields / yield curves
- Valuation / earnings yield / EPS growth
- Macro / liquidity / inflation / regime
- Event impact / news-to-portfolio mapping
- Broker / bank / ETF / fund / deposit product comparison
- Tax / household cashflow scenarios
- Backtests / rolling windows / stress / start-date sensitivity
- Audit / revision / as-of / provenance
- Ask / recipe routing

A new chart is not a feature unless it answers a registered question.

## Canonical question authority

`data/questions/catalog.v1.json` owns the supported question contract.

Each recipe declares:

- question identity and intent
- required inputs
- data authority
- as-of policy
- calculation
- comparison/scenario
- decision and risk outputs
- provenance output
- freshness requirement
- failure mode

Tests should enforce machine-decidable parts of this contract.

## Data authority

- Consume versioned observations from their owning source/provider/repository when possible; do not create a second authority merely for presentation.
- Likely upstream owners include `investor2` for portfolio analytics, `kakeibo` for household cashflow, `econalert` for macro events, `auto-invest` for strategy experiments, broker/bank exports for account facts, and official/market providers for public observations.
- Preserve instrument identity, timestamp/as-of, market session/field, unit/currency, source/provenance and point-in-time semantics required by the question.
- Keep observed values, deterministic derived values, estimates/assumptions, interpretation, and decisions distinct.
- Prefer source data plus deterministic derivation over storing a second maintained copy of derived results.

## Public / private boundary

This repository and its Pages surface are public.

- Never commit account numbers, private transaction exports, tax documents, credentials, personal identifiers, or raw private balances.
- Public Pages may use verified public observations or synthetic/sample data only.
- Private portfolio/account/tax workflows must obtain data from local or connected private sources at runtime or in a private execution environment.
- Public and private modes may share schemas and deterministic recipes, but not raw private data.

## Financial correctness

- Never silently mix daily executable mechanics, monthly averages, quarterly proxies, or different observation windows.
- State annualization method and sampling frequency.
- State leverage mechanics explicitly: fixed notional, constant leverage/rebalanced, or a leveraged product.
- Backtests must expose sample window and, where decision-relevant, start-date/regime sensitivity.
- Current rates, prices, swaps, product terms, tax rules, company facts, and news require current verification before a current decision.
- Do not relabel stale/cached data as live or real-time.
- Do not infer missing prices, returns, timestamps, sessions, product rules, or market observations.
- Source/PIT conflicts fail closed.
- Recommendations or decision implications must be traceable to inputs, calculations, scenarios, and constraints.

## Simplification

- One responsibility should have one canonical entry point, data authority and implementation path.
- Remove dead code, stale docs/config, duplicate wrappers, completed scaffolding and repository-local compatibility once evidence shows they are no longer required.
- Demote obsolete single-purpose product assumptions rather than preserving them as parallel authorities.
- Test deletion hypotheses; restore anything that direct evidence shows is still required.
- Preserve migration/data-safety controls until their completion criteria are actually satisfied.
- Put machine-decidable rules in tests/CI instead of prose when practical.

## Autonomous execution

1. Inspect current `main`, README, open Issues/PRs, the question catalog, canonical inputs, view artifacts, workflows/tests and the deployed surface when release evidence is in scope.
2. Start from a user question or missing high-value recipe, not from a desire to add a chart/library.
3. Resolve the owning data source and as-of semantics before adding calculation or UI.
4. Implement one canonical calculation/scenario path and expose provenance/status alongside the output.
5. Prefer correction, integration, deletion, or consolidation over parallel mechanisms.
6. Run focused deterministic/UI checks and verify the exact reviewed revision before merge.
7. Stop at the fixed point; do not add metrics that do not change a supported question or decision.

## Merge and release are separate

A PR may merge when the repository-local question/data/calculation/view contract is correct on the exact head revision, relevant deterministic/UI tests pass, generated output is reproducible when affected, and no unresolved correctness blocker remains.

Release is separate. Treat a public view as released only after the merged `main` revision and actual production surface are read back and verified when release is in scope.

A merged PR does not prove production release. A production blocker does not retroactively invalidate a correctly merged repository change.

## Boundaries

- finBI may analyze and recommend but does not execute trades, transfers, tax filings, bank actions, or account changes.
- Browser/local state is not durable analytics unless a canonical backend/source proves it.
- Unobserved source, CI, deployment or user outcomes remain unverified.
- A dashboard placeholder must say unavailable/not connected rather than display invented demo values as facts.

## Completion report

Report:

- user question/outcome Before -> After
- owning source and canonical recipe/view
- observed vs derived vs assumed inputs
- Issue/PR/commit/check evidence
- `merged` and `released` separately
- duplicate authority/manual work removed
- remaining unsupported questions or blockers
