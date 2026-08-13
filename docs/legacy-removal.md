# Legacy removal decision

2026-08-13: the 2023 Streamlit recovery code is removed from the active repository tree rather than retained as an archive.

The historical implementation remains recoverable from Git history. Keeping `your_streamlit_app.py`, provider readiness helpers, and credential-era tests in the current tree would preserve a second architecture that the public product no longer uses.

The canonical implementation after this change is intentionally limited to:

- committed verified snapshots under `data/snapshots/`
- `code/static_bi.py` plus tests
- four public UI files under `web/`
- one CI / Pages workflow

This is a destructive simplification, not a compatibility migration.
