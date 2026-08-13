# finBI

金融データは、数字を並べるだけでは「何が起きたか」が分かりにくい。`finBI` は、保存済みの検証済みデータから **2つの日付を選ぶだけで、変化を見て・比べて・出典まで確かめられる** 小さな金融BIです。

**公開版:** https://kafka2306.github.io/finBI/

2023年の壊れたStreamlit試作は復旧しません。現在の正準線は **verified snapshot → pure Python calculation → one-screen static Pages** だけです。

## 使い方

公開Pagesでは次の順だけで完結します。

1. 時系列を見る
2. グラフ上の2点、または開始日・終了日のselectで比較範囲を選ぶ
3. Pythonで比較する
4. 元の%値、percentage point差、basis point差を読む
5. 同じ画面で一次情報・観測期間・取得時刻を確認する

現在値、live market dashboard、投資助言としては扱いません。

## 現在の正準データ

現在のsnapshotは `data/snapshots/fred-dgs10-2026-07-20_2026-07-23.json` です。

- series: `DGS10`
- source: Federal Reserve Bank of St. Louis (FRED) / Board of Governors H.15
- unit: Percent
- frequency: Daily
- observed: 2026-07-20〜2026-07-23
- retrieved_at: `2026-07-24T20:17:00Z`
- source updated at: `2026-07-24T20:17:00Z`
- latest available observation at retrieval: `2026-07-23 = 4.71`
- source URL: https://fred.stlouisfed.org/series/DGS10
- FRED availability evidence: https://fred.stlouisfed.org/graph/?graph_id=907169
- ALFRED vintage download: https://alfred.stlouisfed.org/series/downloaddata?seid=DGS10

snapshotには source / series ID / observation range / retrieved_at / unit / currency / frequency に加え、`availability.verified` / source更新時刻 / その時点の最新利用可能観測日 / 一次証拠URLを保持します。

`observation_date <= retrieved_at.date()` だけではPIT整合性を保証できません。観測日当日にまだ公開されていない値があるため、finBIは **source availability timestamp <= retrieved_at** と、その時点のlatest available observationを検証します。availabilityを一次情報で証明できないsnapshotはfail-closeし、`verified` として扱いません。

## 計算はPythonだけ

`code/static_bi.py` が正準計算です。現在は以下を返します。

- 2観測日の値
- 差分
- basis points（Percent系列のみ）
- 上昇 / 低下 / 横ばい
- 暦日差
- provenance

snapshot外の日付、逆転した期間、provenance欠落、観測順序の破損、未検証availability、取得時刻より後のsource availability、当該時点で未公開だった観測はfail-closeします。金融計算式をJavaScriptへ複製しません。

```bash
python -m unittest discover -s code/tests -v
```

## Pages UI

`web/index.html` / `web/styles.css` / `web/app.js` / `web/worker.mjs` の4ファイルが公開UIの全runtime surfaceです。

- frameworkなし
- build toolなし
- API keyなし
- browserから金融APIへのlive fetchなし
- responsive
- light / dark mode
- visible keyboard focus
- reduced-motion対応
- drag操作不要
- グラフの観測点をclick / tapして比較範囲を選択可能
- selectによるkeyboard経路を維持
- 元の%値 / percentage point / basis pointを同じ結果で説明
- 主要button / select / chipはfinBI独自contractとして44px以上
- source / observed range / retrieved_atを1画面表示

Pyodideはmodule Web Workerで動かし、`code/static_bi.py` をそのまま実行します。JavaScriptはI/O、操作、文字整形、SVG描画だけを担当します。

## なぜDuckDB-Wasm / Perspective / marimoを入れていないか

どれも2026年時点で有力なOSSですが、小さなsnapshotに分析runtimeを追加すると複雑性が増えます。考え方は参照し、必要になるまで依存は増やしません。

採用・不採用の境界は `docs/design-2026.md`、一次参照一覧は `docs/references-2026.md` に固定しています。

## 2023互換層は削除

旧 `your_streamlit_app.py` / `categories.py` / `settings.py` / `provider_status.py` と、それら専用のimport/credential互換testsは現行treeから削除しました。必要ならGit履歴から参照できますが、現行アーキテクチャとしては維持しません。判断理由は `docs/legacy-removal.md` に残します。

## CI / GitHub Pages

`.github/workflows/static-bi.yml` が以下を直接検証します。

- Python compile
- offline unit tests
- PIT provenance / availability regression
- JS syntax
- accessibility / UI contractの最低限チェック
- public root build
- HTTP route smoke test
- generated residue cleanup
- clean checkout

GitHub Pagesは **GitHub Actions sourceで有効化済み**です。`main` の同じ正準buildを `configure-pages → upload-pages-artifact → deploy-pages` で公開します。

2026-08-13にPages有効化後のdeployを実行し、`Build Pages artifact` / `Configure Pages` / `Upload Pages artifact` / `Deploy Pages` がすべて成功しました。

- public URL: https://kafka2306.github.io/finBI/
- Pages settings: https://github.com/KAFKA2306/finBI/settings/pages
- deploy evidence: https://github.com/KAFKA2306/finBI/actions/runs/31678299234

GitHub Pages API上では `build_type: workflow`、sourceは `main`、public、HTTPS enforcedです。

## Security / boundary

- browserへAPI keyを置かない
- pickleを公開UI input/cacheとして使わない
- source URL、series ID、observed range、retrieved_at、unit、currencyをsnapshotに保持する
- availabilityを一次情報で証明できないsnapshotをverified扱いしない
- retrieved_atより後に利用可能になった観測をsnapshotへ混入させない
- snapshot外を補間・推定しない
- 未検証providerを自動的に復活させない
- 現在値でないsnapshotを現在値に見せない

## Issues / current status

- [Issue #8](https://github.com/KAFKA2306/finBI/issues/8): 公開UIの最終E2E。Pages有効化・deployまでは完了し、公開URLでのdesktop / mobile操作確認が残る
- [Issue #10](https://github.com/KAFKA2306/finBI/issues/10): PIT provenance / availability fail-close — **completed**
- [Issue #11](https://github.com/KAFKA2306/finBI/issues/11): グラフ直接選択・bpの意味づけ — 実装済み。公開URLでのdesktop / mobile E2Eが残る

Pagesが公開されたこと自体と、公開ブラウザ上で全操作がE2E確認済みであることは分けて扱います。後者を確認するまでは #8 / #11 をcloseしません。
