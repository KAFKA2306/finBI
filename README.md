# finBI

`finBI` は2023年のStreamlit金融BI試作を、そのまま延命しないためのrecovery repositoryです。通常利用の正準線は **検証済み静的snapshot → pure Python比較 → 静的Web UI** とします。旧Streamlitは現行entry pointではありません。

## 現在の正準データ

最初の検証済みsnapshotは `data/snapshots/fred-dgs10-2026-07-20_2026-07-24.json` です。

- series: `DGS10`
- source: Federal Reserve Bank of St. Louis (FRED) / Board of Governors H.15
- unit: Percent
- frequency: Daily
- observed: 2026-07-20〜2026-07-24
- source URL: https://fred.stlouisfed.org/series/DGS10

snapshotには `source / series_id / observation range / retrieved_at / unit / currency / frequency` を必須で保持します。現在値として扱わず、保存済み期間の比較だけに使います。

## 計算

`code/static_bi.py` が正準Python計算です。選択した2観測日の値と差分を返し、snapshot外の日付、逆転した期間、provenance欠落をfail-closeします。JavaScriptへ金融計算式を複製しません。

```bash
python -m unittest discover -s code/tests -v
```

## Web

`web/index.html` は1画面の静的UI入口です。画面上で「現在値・live market dashboard・投資助言ではない」ことを固定表示します。Pyodide Web Worker接続はIssue #6の残作業です。公開前に実ブラウザE2EでPython coreとのparityを確認します。

## Legacy

`code/your_streamlit_app.py`、`categories.py`、`settings.py`、`provider_status.py` は2023試作のrecovery/archive文脈です。公開UIのentry pointではありません。個人Windows/ngrok起動scriptは正準経路から削除します。

## Security / boundary

- browserからYahoo/FRED/SimFin等の金融APIへ直接通信しない
- API keyをbrowserやrepositoryへ置かない
- pickleを公開UI input/cacheとして使わない
- source URL、series ID、observed_at、retrieved_at、unit、currencyをsnapshotに保持する
- snapshot外を補間・推定しない

## Issue

Static Python BIへの縮約は Issue #6 で管理します。
