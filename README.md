# finBI

`finBI` は2023年のStreamlit金融BI試作を、そのまま延命しないためのrecovery repositoryです。通常利用の正準線は **検証済み静的snapshot → pure Python比較 → 1画面の静的Web UI** とします。旧Streamlitは現行entry pointではありません。

## 現在の正準データ

最初の検証済みsnapshotは `data/snapshots/fred-dgs10-2026-07-20_2026-07-24.json` です。

- series: `DGS10`
- source: Federal Reserve Bank of St. Louis (FRED) / Board of Governors H.15
- unit: Percent
- currency: N/A
- frequency: Daily
- observed: 2026-07-20〜2026-07-24
- source URL: https://fred.stlouisfed.org/series/DGS10

snapshotには `source / series_id / observation range / retrieved_at / unit / currency / frequency` を保持します。現在値として扱わず、保存済み期間の比較だけに使います。

## 計算

`code/static_bi.py` が正準Python計算です。選択した2観測日の値と差分を返し、snapshot外の日付、逆転した期間、provenance欠落をfail-closeします。JavaScriptへ金融計算式を複製しません。

```bash
python -m unittest discover -s code/tests -v
```

## Web

`web/index.html` が1画面の静的UI入口です。画面上で「現在値・live market dashboard・投資助言ではない」ことを固定表示します。

`web/app.js` は入出力と描画だけを担当し、`web/worker.mjs` のmodule Web Workerが、利用者が比較ボタンを押した時だけPyodideを読み込みます。Workerは同一repositoryの `code/static_bi.py` を実行するため、金融計算式はPythonに一意です。

静的buildは `web/`、検証済みsnapshot、`code/static_bi.py` だけを配信対象へコピーします。browserからFRED/Yahoo/SimFin等の金融APIへデータ取得通信は行いません。

## Legacy

`code/your_streamlit_app.py`、`categories.py`、`settings.py`、`provider_status.py` は2023試作のrecovery/archive文脈です。公開UIのentry pointではありません。個人Windows/ngrok起動scriptと旧Poetry依存定義は正準経路から削除しました。

## Security / boundary

- browserへAPI keyを置かない
- pickleを公開UI input/cacheとして使わない
- source URL、series ID、observed_at、retrieved_at、unit、currencyをsnapshotに保持する
- snapshot外を補間・推定しない
- 未検証providerを自動的に復活させない

## CI / 公開状態

`.github/workflows/static-bi.yml` がPython、snapshot、JavaScript、静的route、clean checkoutを直接検証します。

GitHub Pages siteのrepository設定が存在することを確認できるまでは、公開済みとは扱いません。Pages有効化後に同じ静的buildをdeployし、実URLのE2E確認を行います。

## Issue

Static Python BIへの縮約は Issue #6 で管理します。
