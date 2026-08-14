# Tooling audit — 2026

This document records the repository-local tooling decision for Issue #16.

## Inventory

- Runtime languages: Python 3.12 for the canonical calculation core; browser JavaScript modules plus HTML/CSS for the static UI.
- Python production dependency manifest / lock: none.
- JS/TS package manifest / lock: none.
- Workspace / monorepo graph: none; this is one small static application.
- Existing Python checks before this change: `py_compile` + `unittest`.
- Existing JS checks before this change: `node --check` + repository assertions.
- Runtime validation authority: `code/static_bi.py::validate_snapshot` at the untrusted snapshot boundary, with fail-closed source/provenance/availability checks.
- Public integration gate: deployed GitHub Pages desktop/mobile Selenium E2E.

## Decision

Adopt only the tools that remove a real quality gap without introducing a second application runtime.

- **uv**: tool bootstrap/execution authority in CI and local checks.
- **prek 0.4.11**: single local/CI fast-gate orchestrator.
- **Ruff 0.16.0**: sole Python formatter and linter authority.
- **Pyrefly 1.1.1**: sole Python static type-check authority.
- **unittest**: existing offline test authority remains.
- **Node native checks**: existing plain-JavaScript syntax/UI contract authority remains.

Do **not** add Pydantic, Biome, Oxlint, TypeScript, Zod, Nx, or Turborepo in this maintenance unit.

### Why the N/A tools stay out

- Pydantic: production Python runs inside Pyodide and currently has no third-party runtime dependency. `validate_snapshot` is already the one fail-closed boundary for the committed external snapshot. Adding Pydantic for this single small schema would expand the browser runtime dependency surface rather than remove duplication. Re-evaluate if multiple external schemas, APIs, or a backend boundary appear.
- Biome/Oxlint/TypeScript/Zod: the web surface is two small plain-JavaScript modules with no npm dependency graph or bundler. Introducing an npm toolchain solely for those files adds a second dependency authority. Re-evaluate when TypeScript or a larger JS surface is introduced.
- Nx/Turborepo: this is not a monorepo or multi-project workspace.

## Canonical commands

Fresh clone requires Python 3.12+, Node.js, curl, and uv. The repository check is one command:

```bash
bash scripts/check.sh
```

The script executes the exact pinned prek runner:

```bash
uvx --from prek==0.4.11 prek run --all-files
```

`prek.toml` then owns:

1. Ruff format check.
2. Ruff lint check.
3. Pyrefly project type check.
4. Offline unit/PIT provenance tests.
5. Browser JavaScript syntax and accessibility/UI assertions.

CI then runs public artifact assembly, local HTTP route smoke tests, generated-residue cleanup, and clean-checkout verification. Public Selenium E2E remains a separate post-deploy integration job.

## Lock drift

The production application still has no Python or JS third-party dependency graph, so a project `uv.lock` is not applicable yet. Quality tools are exact-pinned in `prek.toml`, and the prek runner itself is exact-pinned in `scripts/check.sh`.

If a production Python dependency is introduced, migrate to a uv project and require `uv lock --check` / locked sync in CI. If an npm runtime dependency is introduced, add one package manager and one lockfile rather than mixing authorities.

## Tool ownership

- Python format: Ruff 0.16.0.
- Python lint: Ruff 0.16.0.
- Python type checking: Pyrefly 1.1.1.
- Runtime financial validation: `validate_snapshot` remains the single boundary authority.
- Fast repository orchestration: prek 0.4.11 via `scripts/check.sh`.
- Public integration/E2E: GitHub Actions after Pages deployment.

## Baseline timing

Before this migration, GitHub Actions run 31824615155 on `dc3dea202aaf591cc2265e5d24e9a9fc130ebf1e` completed the full workflow in about 71 seconds wall-clock (created 17:34:30Z, updated 17:35:41Z on 2026-08-14). The exact-head PR/main run for this change is the after-change measurement. Repository timing, not vendor benchmark multipliers, is the performance evidence used here.

## Primary documentation consulted

- uv GitHub Actions integration: https://docs.astral.sh/uv/guides/integration/github/
- uv locking/sync: https://docs.astral.sh/uv/concepts/projects/sync/
- Ruff formatter: https://docs.astral.sh/ruff/formatter/
- Ruff linter: https://docs.astral.sh/ruff/linter/
- Pyrefly configuration: https://pyrefly.org/en/docs/configuration/
- Pyrefly installation/CLI: https://pyrefly.org/en/docs/installation/
- prek configuration: https://prek.j178.dev/reference/configuration/
- prek CLI: https://prek.j178.dev/reference/cli/
