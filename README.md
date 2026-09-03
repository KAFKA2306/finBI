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
| FX | **CANONICAL / UNVERIFIED** | `KAFKA2306/investor2` の公開 `investor2.fx-overlay.v1` artifactを直接read-only表示。finBIではcarry / leverage / break-even / stress / PnLを再計算しない |
| Rates | **LIVE** | 保存済みTreasury snapshotを `code/static_bi.py` で比較 |
| Portfolio | PLANNED | private/canonical position output待ち |
| Frontier | PLANNED | investor2 canonical frontier output待ち |
| Valuation / Macro / Products / Tax / Backtest / Audit | PLANNED | owning sourceの正準output接続待ち |

PLANNED viewにsynthetic/fixture値を本番結果として表示しません。

## FX authority

正準artifact:
https://kafka2306.github.io/investor2/artifacts/api/v1/portfolio/fx-overlay.json

正準仕様:
https://github.com/KAFKA2306/investor2/blob/main/docs/specs/fx_overlay_contract.md

正準計算ownerは `KAFKA2306/investor2` です。finBIは上記production artifactをブラウザから直接読み、同じ結果のsnapshotをrepository内へ複製しません。

現在は、実際のportfolio position snapshotと十分なrealized daily swap historyが正準入力として未整備のため `UNVERIFIED` です。数値が無い場合は0やproxyへfallbackせず、無いまま表示します。

関連:
- https://github.com/KAFKA2306/investor2/issues/251
- https://github.com/KAFKA2306/investor2/issues/252

## Rates authority

保存済みTreasury snapshotを使い、開始日・終了日の比較、basis point差、2s10s curve shapeを表示します。`code/static_bi.py` はRatesのpresentation-layer calculationだけを所有します。

snapshotのsource、observed range、retrieved_at、availabilityが不足・矛盾する場合はfail closedします。

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

GitHub Actionsはfast quality gate、canonical investor2 artifact、Pages artifact、HTTP smoke、clean checkout、production Pagesのdesktop/mobile E2Eを検証します。CI成功だけでrelease成功とは扱いません。

## Work state

- Master: https://github.com/KAFKA2306/finBI/issues/19
- Issues: https://github.com/KAFKA2306/finBI/issues
- Actions: https://github.com/KAFKA2306/finBI/actions
