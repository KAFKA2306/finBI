#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

python -m py_compile code/static_bi.py
python -m unittest discover -s code/tests -v

node --check web/app.js
node --check web/worker.mjs
test -s web/styles.css
grep -q 'prefers-reduced-motion' web/styles.css
grep -q 'aria-live="polite"' web/index.html
grep -q 'role="status"' web/index.html

rm -rf site
mkdir -p site/data/snapshots site/code
cp web/index.html web/app.js web/worker.mjs web/styles.css site/
cp data/snapshots/fred-dgs10-2026-07-20_2026-07-23.json site/data/snapshots/
cp code/static_bi.py site/code/

python -m http.server 8123 -d site >/tmp/finbi-http.log 2>&1 &
server_pid=$!
cleanup() {
  kill "$server_pid" 2>/dev/null || true
  rm -rf site
  find . -type d -name __pycache__ -prune -exec rm -rf {} +
}
trap cleanup EXIT
sleep 1
curl --fail --silent http://127.0.0.1:8123/ | grep -q '金利の動きを'
curl --fail --silent http://127.0.0.1:8123/styles.css >/dev/null
curl --fail --silent http://127.0.0.1:8123/data/snapshots/fred-dgs10-2026-07-20_2026-07-23.json >/dev/null
curl --fail --silent http://127.0.0.1:8123/code/static_bi.py >/dev/null
