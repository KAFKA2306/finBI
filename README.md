# finBI

[![Static Python BI](https://github.com/KAFKA2306/finBI/actions/workflows/static-bi.yml/badge.svg)](https://github.com/KAFKA2306/finBI/actions/workflows/static-bi.yml)

保存済み・検証済みの金融snapshotから、**2つの日付を選んで変化を比較し、出典と取得時点まで確認する**小さな金融BIです。

**公開版:** https://kafka2306.github.io/finBI/

## What it does

公開Pagesでは次の流れを一画面で完結させます。

1. 保存済み時系列を見る
2. グラフまたはselectから開始日・終了日を選ぶ
3. Pythonで比較する
4. 元の値、percentage point差、basis point差を読む
5. source / observed range / retrieved_atを確認する

比較期間はURLの`start` / `end`で復元できます。現在値の速報、投資助言、自動売買は対象外です。

## Data authority

`data/snapshots/` のversioned snapshotだけを入力として保持します。各snapshotはseries ID、単位、観測期間、取得時刻、source/provenance、availability evidenceを持ちます。

観測値から得られる差分、bp、direction、yield-curve shapeなどは保存済みの別ledgerを持たず、`code/static_bi.py` が決定論的に導出します。これにより、**source observation + one calculation authority** に保ちます。

availabilityを一次情報で証明できないsnapshot、取得時刻より後に利用可能になった観測、provenance欠落、観測順序破損はfail-closeします。snapshot外の値は補間・推定しません。

現在の公開UIはDGS10とDGS2を読み、10年債の2点比較と2s10s Comparison Briefを表示します。追加のcommitted snapshotは比較入力として保持し、事前計算した判定結果は保存しません。

## Architecture

```text
verified snapshots
       ↓
code/static_bi.py
       ↓
Pyodide module Web Worker
       ↓
static Pages UI
```

金融計算は`code/static_bi.py`だけが担当します。JavaScriptはI/O、interaction、formatting、SVG renderingを担当し、同じ金融計算を二重実装しません。

公開runtime surfaceは4ファイルです。

- `web/index.html`
- `web/app.js`
- `web/worker.mjs`
- `web/styles.css`

ブラウザから金融providerへlive fetchせず、API keyも持ちません。

## Verification

fresh cloneでPython 3.12、Node.js、uvが利用可能ならfast gateは1コマンドです。

```bash
uvx --from prek==0.4.11 prek run --all-files
```

`prek.toml` がRuff format/lint、Pyrefly、offline unittest、browser syntax/accessibility contractを所有します。GitHub Actionsは同じgateに加え、Pages artifact build、HTTP route smoke、clean checkoutを検証します。mainへのpush後は公開Pagesをdesktop/mobile Selenium E2Eで確認します。

## Design boundaries

- snapshotの時点整合性を速報性より優先する
- `%` / percentage point / basis pointを混同しない
- chart操作だけでなくselect経路を維持する
- observed / deterministic derived / interpretationを分離する
- Pages deploymentとproduction E2Eを別の証拠として扱う
- 大きな分析runtimeは実測上必要になるまで追加しない

設計判断と再評価条件は [`docs/design-2026.md`](docs/design-2026.md)、一次参照は [`docs/references-2026.md`](docs/references-2026.md) にあります。

## Work state

未解決作業はREADMEへ複製せずGitHub Issuesを正準とします。

- Issues: https://github.com/KAFKA2306/finBI/issues
- Actions: https://github.com/KAFKA2306/finBI/actions
