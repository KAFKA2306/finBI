# Tooling audit — 2026

This document records the repository-local tooling decision for Issue #16.

## Inventory

- Runtime languages: Python 3.12 for the canonical calculation core; browser JavaScript modules plus HTML/CSS for the static UI.
- Python project manifest / dependency lock: none.
- JS/TS package manifest / lock: none.
- Workspace / monorepo graph: none; this is one small static application.
- Formatter authority: none.
- Python lint authority: none; `py_compile` is syntax validation only.
- Python type authority: none; annotations are used, but no maintained type checker is configured.
- JS lint/type authority: none; `node --check` is syntax validation only and the repository has no TypeScript.
- Runtime validation authority: `code/static_bi.py::validate_snapshot` at the untrusted snapshot boundary, with fail-closed source/provenance/availability checks.
- Hooks: none.
- CI: `.github/workflows/static-bi.yml` runs fast validation, Pages deployment, and public desktop/mobile E2E.
- Legacy debt: the former Streamlit/provider/credential runtime has already been removed; the maintained line is verified snapshot → pure Python calculation → static Pages.

## Decision

The repository does **not** install Ruff, Pyrefly/Pyright, Pydantic, Biome, Oxlint, TypeScript, Zod, Turborepo, Nx, or prek in this maintenance unit.

Reason: there is no duplicated formatter/linter/type authority to consolidate, no package/workspace graph to manage, and the maintained surface is small. Adding those tools now would create new dependency/configuration authority rather than remove overlapping authority. Runtime financial validation already exists exactly at the untrusted snapshot boundary, so adding Pydantic solely for internal data would duplicate that contract.

The useful consolidation is instead to move the existing fast repository checks out of workflow YAML into `scripts/check.sh`. Local development and CI now call the same repository-owned check entrypoint. Integration/public-browser E2E remains a separate post-deploy CI job because it depends on the deployed GitHub Pages site.

## Canonical commands

Fresh clone requires Python 3.12+, Node.js, curl, and no package installation for fast validation.

```bash
bash scripts/check.sh
```

The command owns:

1. Python syntax compilation.
2. Offline unit and PIT/provenance regression tests.
3. Browser JavaScript module syntax checks.
4. Static accessibility/UI contract assertions.
5. Public artifact assembly.
6. Local HTTP route smoke tests.
7. Generated-residue cleanup.

CI additionally verifies a clean checkout after the script exits. Public Selenium E2E remains in its own job after Pages deployment.

## Lock drift

Not applicable. The maintained application has no Python or JS dependency manifest/lock. Selenium is an explicit CI-only E2E dependency and is intentionally not part of the static application runtime.

## Tool ownership

- Format: N/A — no formatter is configured or required to replace an existing formatter.
- Lint: N/A — no maintained linter exists; syntax and contract checks are intentionally narrow.
- Type checking: N/A — no existing primary type checker exists to preserve or consolidate.
- Runtime financial validation: `validate_snapshot` is the single authority for committed snapshot identity, provenance, ordering, availability, and fail-closed validation.
- Fast repository check orchestration: `scripts/check.sh` is the single repository-owned entrypoint.

## Baseline timing

GitHub Actions run 31824615155 (`dc3dea202aaf591cc2265e5d24e9a9fc130ebf1e`) completed the `validate` job from 17:34:33Z to 17:34:39Z on 2026-08-14: **6 seconds wall-clock**. This is the before-change baseline. The exact-head PR CI after this consolidation is the after-change measurement; no vendor benchmark multiplier is used as repository evidence.

## Primary documentation consulted

- Ruff formatter: https://docs.astral.sh/ruff/formatter/
- uv locking/sync: https://docs.astral.sh/uv/concepts/projects/sync/
- Pyrefly: https://pyrefly.org/en/docs/

These references inform the decision boundary; they are not evidence that those tools should be installed here.
