https://kafka2306.github.io/finBI/

# finBI

[![Static Python BI](https://github.com/KAFKA2306/finBI/actions/workflows/static-bi.yml/badge.svg)](https://github.com/KAFKA2306/finBI/actions/workflows/static-bi.yml)

finBIは金融判断に必要な正準データ・正準analytics outputを、比較可能なBIとして表示するrepositoryです。Issue tracker、research engine、取引engine、第二の計算authorityにはしません。

```text
canonical data / analytics
  -> finBI read-only adapter or presentation metric
  -> chart / table / KPI
  -> source / as-of / status
```

## Current views

| View | State | Authority |
|---|---|---|
| ETF Screener | **LOCAL CSV** | ブラウザで取り込んだ同一基準日のCSVを表示のみ。検索・絞り込み・中央値・分布・横比較・CSV再出力。元データの正本と公開権限は提供元に保持 |
| FX | **CANONICAL** | `KAFKA2306/investor2` の公開 `investor2.fx-overlay.v1` artifactを直接read-only表示。statusは上流artifactに追従し、finBIではcarry / leverage / break-even / stress / PnLを再計算しない |
| Rates | **HISTORICAL SNAPSHOT** | 2026-07-20〜2026-11-17の84観測日を `code/static_bi.py` で比較。画面に観測期間と取得時刻を表示する |
| Portfolio | PLANNED | private/canonical position output待ち |
| Frontier | PLANNED | investor2 canonical frontier output待ち |
| Valuation / Macro / Products / Tax / Backtest / Audit | PLANNED | owning sourceの正準output接続待ち |

PLANNED viewにsynthetic/fixture値を本番結果として表示しません。

## ETFスクリーナー（新しい主な入口）

公開ページ: https://kafka2306.github.io/finBI/screener.html

1. 「CSVを読み込む」からデータを選択します。元ファイルは公開サーバーへ送信せず、ブラウザ内のメモリにのみ置きます。
2. ティッカー、分野、経費率、規模、レバレッジの有無、1か月下落幅で絞り込み、分野別件数と費用・1か月騰落率の分布を確認できます。
3. 最大4銘柄を横並びで比較し、該当結果をCSVで再出力できます。画面の表は最大200行ですが、検索・集計・出力対象は最大20,000行です。

CSVの必須列は「ティッカー」「商品名」「分野」「基準日（YYYY-MM-DD）」です。「経費率(%)」「参考規模(百万USD)」「1か月騰落率(%)」「出典URL」などは任意列。空欄は未取得であり、ゼロとは扱いません。同一ファイルに複数の基準日がある場合は取り込みを拒否します。参考PER・提供スコアは元の定義が保証されないため、画面では参考値として明示し、売買推奨には用いません。

このrepositoryはデータ提供元のライセンスを引き継ぎません。第三者の有料データや非公開口座情報をGitHub Pagesで公開することはありません。入力は利用者本人が適切な許可で取得したCSVに限定してください。

テスト:

```bash
node --test code/tests/test_screener.mjs
```

## FX authority

正準artifact:
https://kafka2306.github.io/investor2/artifacts/api/v1/portfolio/fx-overlay.json

正準仕様:
https://github.com/KAFKA2306/investor2/blob/main/docs/specs/fx_overlay_contract.md

正準計算ownerは `KAFKA2306/investor2` です。finBIは上記production artifactをブラウザから直接読み、同じ結果のsnapshotをrepository内へ複製しません。`VERIFIED` / `TEST_ONLY` / `UNVERIFIED` のstatusも上流artifactをそのまま表示します。

正準入力が不足して上流が `UNVERIFIED` を返す場合、finBIは0やproxyへfallbackせず、理由と欠損状態をそのまま表示します。

関連:
- https://github.com/KAFKA2306/investor2/issues/251
- https://github.com/KAFKA2306/investor2/issues/252

## Rates authority

FREDの米国債2年・10年利回りを、任意の共通観測日2日で比較できます。直近5観測日、直近20観測日、全期間をワンクリックで選べます。比較日のURLを共有すると同じ日付が開きます。`code/static_bi.py` はRatesのpresentation-layer calculationだけを所有します。

現行の保存データは `data/snapshots/fred-dgs2.json` と `data/snapshots/fred-dgs10.json` です。各ファイルにFREDの系列URL、取得時刻、元のCSVのURLとSHA-256を記録します。2026年7月分の旧保存データも取得時点の証拠として参照できます。

## Public / private boundary

このrepositoryとGitHub Pagesはpublicです。

- account number、private transaction、raw balance、tax document、credential、personal identifierをcommitしない
- public Pagesはverified public dataまたはpublication-safe canonical outputのみ
- private portfolio/account dataはlocal/connected private sourceまたはowning private execution environmentで扱う
- missing holdingを0として扱わない
- stale/cached dataをliveと呼ばない

## Visual authority

`KAFKA2306/design` がKAFKA2306 product UIの正準visual authorityです。finBIはReact依存を追加せず、locked design assetsを利用します。

## Verification

```bash
uvx --from prek==0.4.11 prek run --all-files
```

GitHub Actionsはfast quality gate、canonical investor2 production artifact、Pages artifact、HTTP smoke、clean checkout、production Pagesのdesktop/mobile E2Eを検証します。E2Eは上流FX artifactの実statusとfinBI表示が一致することも確認します。CI成功だけでrelease成功とは扱いません。

## Work state

- Master: https://github.com/KAFKA2306/finBI/issues/19
- Issues: https://github.com/KAFKA2306/finBI/issues
- Actions: https://github.com/KAFKA2306/finBI/actions

## Operational ontology

[Project ontology](ontology/project.yaml) defines domain objects, evidence-bearing relations, guarded actions and outcome metrics under the [shared Causal–Evidence Core](https://github.com/KAFKA2306/know/blob/main/ontology/causal-evidence-core.yaml). This contract does not add real-world execution capability or replace this repository's canonical source.
