# Pagesを「金利の動きを触って読む」1画面体験へ再設計する

## 目的

2026年時点のbrowser-local Python、宣言的可視化、再現可能な分析、アクセシビリティ、GitHub Pages運用の一次情報を参照し、finBIを専門家向けBIの縮小版ではなく、初見ユーザーが説明なしで使える1画面の金融データ体験へ作り直す。

## 方針

- 「2日を選ぶ → 変化を見る → 出典を確かめる」の1操作に絞る
- 公開rootをアプリ本体にする
- 正準金融計算はPythonだけに置き、Pyodide module Web Workerから同じコードを実行する
- JavaScriptはI/O、SVG描画、表示のみ
- live金融API、API key、DB、frontend framework、bundlerを持ち込まない
- 2023 Streamlit/provider/credential互換層を現行treeから削除する
- keyboard、focus visibility、44px controls、reduced motion、responsive、semantic statusをCI境界にする
- DuckDB-Wasm / Perspective / marimoは比較対象として記録するが、現在のsnapshot規模では依存にしない

## Acceptance Criteria

- [ ] 初見ユーザーがREADMEなしで意味のある比較を完了できる
- [ ] chart / comparison / provenance / warningが1つのresponsive flowに収まる
- [ ] basis point / direction / calendar-day計算がPythonだけに存在する
- [ ] public UIから金融providerへのlive API通信がない
- [ ] current snapshotを現在値として表示しない
- [ ] 2023 legacy runtimeとその専用testsを現行treeから削除する
- [ ] public runtimeのWeb面を `index.html / styles.css / app.js / worker.mjs` の4ファイルに固定する
- [ ] GitHub Actions現行majorを使い、offline tests / JS syntax / HTTP routes / clean checkoutを検証する
- [ ] repository PagesをGitHub Actions sourceで有効化する
- [ ] 公開URLでPyodide比較をE2E確認する

## 一次参照

- https://pyodide.org/en/stable/usage/webworker.html
- https://duckdb.org/docs/stable/clients/wasm/overview
- https://github.com/perspective-dev/perspective
- https://github.com/marimo-team/marimo
- https://vega.github.io/vega-lite/
- https://arxiv.org/abs/2506.20901
- https://www.w3.org/TR/WCAG22/
- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## 完了条件

技術mergeだけではcloseしない。Pages有効化後、公開URLでsnapshot読込・SVG表示・Pyodide比較・provenance linkを確認してcloseする。
