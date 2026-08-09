# finBI

**金融BIで危険なのは、古い数字だけではない。動かない試作を「現行システム」だと思って使うことだ。**

`finBI`は、FRED、Yahoo Finance、SimFinなどの金融・経済データをStreamlitで表示するために2023年に作成した試作コードです。現在のdefault branchはそのままでは起動できず、稼働中のdashboardや最新市場データ基盤として扱える状態ではありません。

## 現在の状態

| 項目 | 状態 |
|---|---|
| 稼働中のapplication | なし |
| 公開dashboard | なし |
| 再現可能なsetup | 未整備 |
| CI・自動test | なし |
| 外部API接続の動作確認 | 未実施 |
| 最新市場データの保証 | なし |
| 主な実装時期 | 2023年 |

このREADMEは、存在するコードと既知の制約を説明するための人間向け入口です。実装されていない機能や、現在確認できない外部API連携を稼働中とは扱いません。

## 残っているもの

`code/your_streamlit_app.py`には、次の試作処理が混在しています。

- Yahoo Financeからの価格系列取得
- FRED系列の取得
- pickleによるローカルcache
- Streamlitでの系列選択とchart表示
- 通貨換算を含むETF比較
- SimFinを使った売上高・純利益表示
- 複数の外部金融APIを使う構想

これらは一つのfileへtop-level処理と複数の`main`関数が混在した状態であり、個別機能が現在動作することを保証しません。

## 起動できない主な理由

### 依存関係

rootに`requirements.txt`はありません。依存定義は`code/pyproject.toml`にありますが、Python `^3.8`と当時のlibrary versionを前提としており、現在環境での解決・実行は確認していません。

### 設定の不整合

`code/your_streamlit_app.py`は、`code/categories.py`から次の変数をimportします。

- `SIMFIN_API_KEY`
- `ALPHA_VANTAGE_API_KEY`
- `FinancialModelingPrep_API_KEY`
- `FINNHUB_API_KEY`

現在の`code/categories.py`にはこれらの定義がないため、default branchのコードはimport時点で失敗します。

### 個人環境への依存

`code/first.bat`には、次のような個人環境のpathと前提が残っています。

- `M:\Apps\ngrok-v3-stable-windows-amd64\ngrok`
- Windows、Conda、Poetry、ngrok、Heroku CLI
- repositoryを特定のdirectory構造へ配置する前提

このbatch fileを一般環境向けの起動手順として使用しないでください。

### dataとcache

コードは`data/`配下やlocal pathのpickle fileを前提とします。必要な入力data、取得日時、source metadata、schema、再生成手順は正準化されていません。

## 構造

```text
finBI/
├── README.md
├── code/
│   ├── your_streamlit_app.py  # 複数の可視化試作を含む旧entry file
│   ├── categories.py          # ticker・FRED系列・旧local path設定
│   ├── first.bat              # 個人Windows環境向けの旧起動script
│   └── pyproject.toml         # Poetry依存定義
└── data/                      # local cacheを想定した領域
```

## セキュリティ

- API keyをrepository、Python file、batch fileへ直接記載しないでください。
- `categories.py`のplaceholderを実credentialへ置換してcommitしないでください。
- 外部から取得したpickleを読み込まないでください。pickleの復元は任意コード実行につながる可能性があります。
- ngrokなどでlocal Streamlitを公開する場合、認証なしでprivate dataやAPI結果を露出させないでください。
- 金融dataにはsource、series ID、観測日、取得日、単位、通貨、改訂状態を付与してください。

## 再開する場合

このrepositoryをそのまま本番化するのではなく、必要な機能を現行基盤へ移植します。金融・企業dataの正準候補は`KAFKA2306/investor`です。

再実装する場合の最低条件は次のとおりです。

1. 使用するdata sourceを限定し、公式API・利用規約・licenseを記録する
2. Python versionと依存を固定し、再現可能なlock fileを作る
3. credentialを環境変数またはsecret managerへ分離する
4. sourceごとのadapter、schema、cache、UIを分割する
5. pickleをParquet、SQLite、PostgreSQLなど検証可能な形式へ置換する
6. 欠損、API停止、rate limit、古いcacheをUIへ明示する
7. unit test、integration test、CI、data freshness監査を追加する

## 既知の制約

- 現在のコードはas-isでは起動しません。
- READMEに列挙した外部APIの接続成功は確認していません。
- 最新価格、企業財務、経済統計の完全性・正確性・鮮度を保証しません。
- 投資判断、売買執行、投資助言に使用できる状態ではありません。

## 関連

- 現行の投資・企業data基盤: `KAFKA2306/investor`
- README監査の正準: `KAFKA2306/com` Issue #3
- 本repositoryの不一致記録: Issue #2
