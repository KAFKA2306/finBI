# Repository Agent Contract

## Mission

Own the **financial BI layer** for this repository.

finBI is not an Issue tracker, research agent, workflow engine, trading engine, or second primary-source warehouse. Its job is to expose decision-relevant financial information as reproducible BI:

`canonical data -> validated metrics -> comparison/scenario -> chart/table/KPI -> provenance`

Financial GitHub Issues are requirement sources for deciding which BI metrics and views matter. Issue state, task state, completion criteria, and issue bodies are not finBI product data and must not be duplicated into a second Issue-management system.

The current two-date Treasury comparison remains supported as one `Rates` BI view rather than the product mission.

## BI scope

Canonical surfaces may cover:

- Overview / market and portfolio KPIs
- Portfolio / allocation / currency exposure / overlap / risk contribution
- Efficient Frontier / what-if allocation / risk constraints
- FX / spot / carry / leverage / margin / liquidation stress
- Rates / bonds / real yields / yield curves
- Valuation / earnings yield / EPS and FCF growth / IRR scenarios
- Macro / liquidity / inflation / regime
- Event comparison / before-after market and fundamental changes
- Broker / bank / ETF / fund / deposit comparison
- Tax / household cashflow scenario tables
- Backtests / rolling windows / stress / start-date sensitivity
- Audit / revision / as-of / provenance

A new chart is useful only when it exposes a registered financial metric, comparison, scenario, or audit state. Do not add Issue-management UI.

## Visual authority

`KAFKA2306/design` is the canonical visual authority for KAFKA2306 product UI. finBI must not create a competing palette, spacing scale, radius system, typography scale, shadow system, table density, or generic product-component grammar.

Because `KAFKA2306/design` is private while finBI and its Pages are public, production must not depend on fetching the private repository at runtime or during public CI. `web/design-tokens.css` is a public-safe, versioned snapshot of canonical design tokens and must record the exact design commit and canonical blob it came from.

- Use `--k-*` tokens from `web/design-tokens.css` for visual values.
- Keep finBI-specific CSS limited to financial layout, chart semantics, responsive composition, and view-specific presentation.
- Prefer dense decision surfaces, 30px data rows, compact hierarchy, square 2px surfaces, and zero decorative shadow as defined upstream.
- Do not migrate finBI to React/TypeScript merely to consume the design system. Framework choice and visual authority are separate concerns.
- When refreshing the snapshot, copy values from the canonical design source and update provenance in the same change.
- CI must prove the public artifact contains both the token snapshot and the finBI stylesheet that consumes it.

## Question catalog

`data/questions/catalog.v1.json` is an internal BI-requirements catalog derived from recurring financial questions. It helps map a question to the data, metrics, comparison axes, risk outputs, and provenance that finBI should make visible.

It is not an Issue Solver and not a workflow authority.

Tests should enforce machine-decidable catalog integrity.

## Data authority

- Consume versioned observations and analytics from their owning source/provider/repository when possible; do not create a second authority merely for presentation.
- Likely upstream owners include `investor2` for portfolio analytics, `CrewTrade` for canonical market artifacts where established, `kakeibo` for household cashflow, `econalert` for macro events, `auto-invest` for strategy experiments, broker/bank exports for account facts, and official/market providers for public observations.
- Preserve instrument identity, timestamp/as-of, market session/field, unit/currency, source/provenance and point-in-time semantics required by the view.
- Keep observed values, deterministic derived values, estimates/assumptions, interpretation, and recommendations distinct.
- Prefer reading canonical analytics output over reimplementing the same calculation inside finBI.

## Public / private boundary

This repository and its Pages surface are public.

- Never commit account numbers, private transaction exports, tax documents, credentials, personal identifiers, or raw private balances.
- Public Pages may use verified public observations or publication-safe sample data only.
- Private portfolio/account/tax BI must obtain data from local or connected private sources at runtime or in a private execution environment.
- Public and private modes may share schemas, metric contracts, and view contracts, but not raw private data.

## Financial correctness

- Never silently mix daily executable mechanics, monthly averages, quarterly proxies, or different observation windows.
- State annualization method and sampling frequency.
- State leverage mechanics explicitly: fixed notional, constant leverage/rebalanced, or a leveraged product.
- Backtests must expose sample window and, where decision-relevant, start-date/regime sensitivity.
- Current rates, prices, swaps, product terms, tax rules, company facts, and news require current verification before presenting them as current.
- Do not relabel stale/cached data as live or real-time.
- Do not infer missing prices, holdings, returns, timestamps, sessions, product rules, or market observations.
- Do not interpret missing holdings as zero.
- Do not substitute policy-rate spread for actual broker swap without explicit proxy labeling.
- Source/PIT conflicts fail closed.
- Recommendations or decision implications must be traceable to visible inputs, calculations/scenarios, and constraints.

## Simplification

- One responsibility should have one canonical data authority and one BI implementation path.
- Remove dead code, stale docs/config, duplicate wrappers, completed scaffolding and obsolete single-purpose product assumptions once evidence shows they are no longer required.
- Do not build an Issue registry, task queue, agent memory, or research notebook inside finBI.
- Preserve migration/data-safety controls until their completion criteria are actually satisfied.
- Put machine-decidable rules in tests/CI instead of prose when practical.

## Autonomous execution

1. Inspect current `main`, README, open financial Issues as requirement evidence, the BI catalog, canonical inputs/outputs, views, workflows/tests, and the deployed surface when release evidence is in scope.
2. Start from a high-value financial metric/comparison missing from the BI, not from a desire to add a library or task-management feature.
3. Resolve the owning data source and as-of semantics before adding calculation or UI.
4. Prefer reading canonical analytics from the owner. Add deterministic finBI-only calculations only when they are presentation-layer metrics and would not create competing authority.
5. Expose source/as-of/status beside decision-relevant outputs.
6. Prefer correction, integration, deletion, or consolidation over parallel mechanisms.
7. Run focused deterministic/UI checks and verify the exact reviewed revision before release.

## Merge and release are separate

A change may merge when the repository-local data/metric/view contract is correct on the exact head revision, relevant deterministic/UI tests pass, generated output is reproducible when affected, and no unresolved correctness blocker remains.

Release is separate. Treat a public view as released only after the merged `main` revision and actual production surface are read back and verified when release is in scope.

A merged commit does not prove production release. A production blocker does not retroactively invalidate a correctly merged repository change.

## Boundaries

- finBI may present analytics and decision support but does not execute trades, transfers, tax filings, bank actions, or account changes.
- finBI does not own GitHub Issue workflow or completion state.
- Browser/local state is not durable financial data unless a canonical backend/source proves it.
- Unobserved source, CI, deployment or user outcomes remain unverified.
- A dashboard placeholder must say unavailable/not connected/planned rather than display invented demo values as facts.

## Completion report

Report:

- BI outcome Before -> After
- owning source and canonical view/metric
- observed vs derived vs assumed inputs
- commit/check evidence
- `merged` and `released` separately
- duplicate authority/manual work removed
- remaining unsupported BI views or data blockers
