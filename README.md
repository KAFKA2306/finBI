# finBI

金融データは、数字を並べるだけでは「何が起きたか」が分かりにくい。`finBI` は、保存済みの検証済みデータから **2つの日付を選ぶだけで、変化を見て・比べて・出典まで確かめられる** 小さな金融BIです。

**公開版:** https://kafka2306.github.io/finBI/

## Vision

金融dashboardを大きくすることではなく、**利用者が任意の2観測日を選び、元の値・差・bpを読み、その場で「いつ取得し、いつ利用可能だった、どの一次情報か」まで確認できる一画面の比較体験**を作ります。

現在値の速報や売買判断を出すことは目的ではありません。保存済みsnapshotの変化を、時点整合性と根拠を保ったまま読むためのUIです。

## Design philosophy

- 現在値の速報性より、snapshotの時点整合性を優先する
- `%` / percentage point / basis point を混同させない
- chart操作だけに依存せず、keyboard/select経路を維持する
- 金融計算はpure Pythonを正準とし、JavaScriptへ二重実装しない
- source availabilityを一次情報で証明できない観測をverifiedへ昇格させない
- Pages deploy成功と、公開browser上のdesktop/mobile E2E成功を分離する
- snapshot外の値を補間・推定しない

## Why / 差別化

一般的なlive金融dashboardのように「最新値を多く並べる」ことではなく、**小さなsnapshotを「比較 → 意味理解 → 出典確認」まで一画面で完結させ、PIT（point-in-time）整合性を利用者から隠さないこと**を中心にしています。

Pyodide、frameworkなし、44px controls、GitHub Actionsはその体験を支える実装手段であり、価値そのものではありません。

## 2-point comparison user journey

公開Pagesでは次の順だけで完結します。

1. 時系列を見る
2. グラフ上の2点、または開始日・終了日のselectで比較範囲を選ぶ
3. Pythonで比較する
4. 元の%値、percentage point差、basis point差を読む
5. 同じ画面で一次情報・観測期間・取得時刻を確認する

たとえば `4.60% → 4.69%` なら、`+0.09 percentage point = +9 bp` のように、元の値と差の単位を同時に読める設計です。

## What the current snapshot means

現在の正準snapshotは `data/snapshots/fred-dgs10-2026-07-20_2026-07-23.json` です。

- series: `DGS10`
- source: Federal Reserve Bank of St. Louis (FRED) / Board of Governors H.15
- unit: Percent
- frequency: Daily
- observed: 2026-07-20〜2026-07-23
- observations: 4
- retrieved_at: `2026-07-24T20:17:00Z`
- source updated at: `2026-07-24T20:17:00Z`
- latest available observation at retrieval: `2026-07-23 = 4.71`
- source URL: https://fred.stlouisfed.org/series/DGS10
- FRED availability evidence: https://fred.stlouisfed.org/graph/?graph_id=907169
- ALFRED vintage download: https://alfred.stlouisfed.org/series/downloaddata?seid=DGS10

これは現在値ではありません。`2026-07-24T20:17:00Z` に取得・検証した保存済みsnapshotです。

## PIT provenance / fail-close

snapshotには source / series ID / observation range / retrieved_at / unit / currency / frequency に加え、`availability.verified` / source更新時刻 / その時点の最新利用可能観測日 / 一次証拠URLを保持します。

`observation_date <= retrieved_at.date()` だけではPIT整合性を保証できません。観測日当日にまだ公開されていない値があるため、finBIは **source availability timestamp <= retrieved_at** と、その時点のlatest available observationを検証します。

availabilityを一次情報で証明できないsnapshot、取得時刻より後に利用可能になった観測、provenance欠落、観測順序破損はfail-closeし、`verified` として扱いません。

## Pages UI / accessibility

`web/index.html` / `web/styles.css` / `web/app.js` / `web/worker.mjs` の4ファイルが公開UIのruntime surfaceです。

- responsive
- light / dark mode
- visible keyboard focus
- reduced-motion対応
- drag操作不要
- グラフの観測点をclick / tapして比較範囲を選択可能
- selectによるkeyboard経路を維持
- 選択した2点の日付と値をhover不要で表示
- 元の%値 / percentage point / basis pointを同じ結果で説明
- 主要button / select / chipはfinBI独自contractとして44px以上
- source / observed range / retrieved_atを1画面表示
- browserから金融APIへのlive fetchなし
- API keyなし

GitHub PagesはGitHub Actions sourceで有効化されています。

- public URL: https://kafka2306.github.io/finBI/
- Pages settings: https://github.com/KAFKA2306/finBI/settings/pages
- build type: `workflow`
- source: `main`
- public: `true`
- HTTPS enforced: `true`

Pagesの公開成功と、公開browser上で全操作がdesktop/mobileともE2E確認済みであることは別の状態として扱います。

## Calculation / CI / architecture

2023年の壊れたStreamlit試作は復旧しません。現在の正準線は **verified snapshot → pure Python calculation → one-screen static Pages** だけです。

`code/static_bi.py` が正準計算で、現在は次を返します。

- 2観測日の値
- 差分
- basis points（Percent系列のみ）
- 上昇 / 低下 / 横ばい
- 暦日差
- provenance

Pyodideはmodule Web Workerで `code/static_bi.py` を実行します。JavaScriptはI/O、操作、文字整形、SVG描画だけを担当します。

### Fast quality gate

localとPR CIのfast gateは `prek.toml` に一本化します。fresh cloneでuvが利用可能なら、検証コマンドは1つです。

```bash
uvx --from prek==0.4.11 prek run --all-files
```

この1コマンドが次のownerを固定します。

- Python format: Ruff `0.16.0`
- Python lint: Ruff `0.16.0`
- Python type check: Pyrefly `1.1.1`
- offline tests: `unittest`
- browser syntax / accessibility contract: Node native checks + repository assertions
- hook orchestration: prek `0.4.11`

`.github/workflows/static-bi.yml` も同じprek commandを実行し、その後にpublic root build / HTTP route smoke test / clean checkoutを行います。公開Pagesのdesktop/mobile Selenium E2Eはdeploy後のintegration gateとして分離したままです。

## Dependency boundary

現在のproduction runtimeは第三者Python packageを持ちません。そのためproject dependency graph用の `pyproject.toml` / `uv.lock` は追加せず、quality toolのversionを `prek.toml` 内でexact pinします。production dependencyを追加する時点でuv project + lockfileへ移行し、CIでlock driftをfailさせます。

Pydanticは現在N/Aです。snapshot JSONは `code/static_bi.py` の単一のuntrusted-data boundaryでfail-close検証され、その同じpure Python codeがPyodideでも実行されます。現在の4観測snapshotだけのためにPydanticを導入するとbrowser runtime dependencyを増やすため、複数schema・外部API・backend boundaryが生まれるまで導入しません。

Biome / Oxlint / `tsc --noEmit` / Zodも現在N/Aです。公開Web面は小さなplain JavaScript 2 moduleで、TypeScript・npm dependency graph・bundlerを持ちません。現状はNode native syntax checkを維持し、TypeScript導入またはJS surface拡大時に再評価します。

Nx / Turborepoも単一static projectのためN/Aです。monorepo化しない限り追加しません。

DuckDB-Wasm / Perspective / marimoは有力な選択肢ですが、現在の小さなsnapshotでは分析runtimeを増やす方が複雑です。採用・不採用の境界は `docs/design-2026.md`、一次参照一覧は `docs/references-2026.md` に固定しています。

旧 `your_streamlit_app.py` / `categories.py` / `settings.py` / `provider_status.py` と、それら専用のimport/credential互換testsは現行treeから削除済みです。判断理由は `docs/legacy-removal.md` に残します。

## Issue workflow

現在の未解決作業はGitHub Issuesを正準とし、READMEへ個別Issueの状態を複製しません。closed Issueを「現在の課題」として残さないためです。

- Issues: https://github.com/KAFKA2306/finBI/issues
- Actions: https://github.com/KAFKA2306/finBI/actions

現在値、live market dashboard、投資助言、自動売買許可としては扱いません。
