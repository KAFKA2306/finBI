https://kafka2306.github.io/finBI/

# finBI

[![Static Python BI](https://github.com/KAFKA2306/finBI/actions/workflows/static-bi.yml/badge.svg)](https://github.com/KAFKA2306/finBI/actions/workflows/static-bi.yml)

**finBI is a Financial Decision Workbench.**

金融チャートを集めるのではなく、繰り返し出てくる質問を、同じデータ・同じ計算・同じ監査規則で再実行できるようにします。

```text
question
  ↓
required data
  ↓
observed facts
  ↓
deterministic calculation
  ↓
comparison / scenario
  ↓
decision implication
  ↓
source / as-of / revision
```

現在の公開Pagesで実稼働しているのは、保存済み米国債snapshotを使った `Rates Desk` の2点比較です。これはfinBI全体では**最初の1レシピ**です。

## What questions should finBI answer?

### Portfolio / allocation

- 今のポートフォリオはどうか
- 何を買う、何を売る、何%追加する
- リスク寄与・集中・重複はどうか
- 効率的フロンティアはどう変わるか
- 同じリターンでリスクだけ下げられるか
- 口座をまたいだ資産配分をどう直すか

### FX / Rates / Bonds

- USD/JPY 3倍は本当に効率が良いか
- swap、日米金利差、実効レバレッジはどうか
- 固定USD建玉と3倍リセットはどう違うか
- SBI・楽天・銀行・FX業者をどう比較するか
- 国債・債券・MMF・定期預金と株をどう比べるか
- 政策金利、実質金利、イールドカーブは何を意味するか

### Valuation / Macro / Events

- PERや益利回りは投資判断に使えるか
- EPS CAGR・実需成長と現在価格は整合しているか
- AI、半導体、クラウド需要をどの資産で取るか
- M2・流動性・CPI/PCE・雇用・PMIからレジームをどう読むか
- ニュースは本当か、何が改定されたか
- そのニュースで今のポートフォリオを変えるべきか

### Backtest / Risk

- CAGR、Vol、Sharpe、Max DDはどうか
- 開始時点を変えると結論は変わるか
- 有利な期間だけ切り取っていないか
- proxyと実際に約定できる戦略は一致しているか

### Products / Tax / Cashflow

- ETF・投信・預金・証券会社・銀行のどれを使うか
- 信託報酬・金利・税・為替・流動性を入れるとどうか
- 予定納税・ふるさと納税上限はいくらか
- 給与、副業、事業所得、青色申告、NISA/iDeCoをどう組み合わせるか
- 法人化や投資税務をどう比較するか

### Audit

- この数字はいつ時点か
- 一次情報は何か
- verified / proxy / estimate / assumption のどれか
- 過去の回答から何が変わったか
- 改定履歴を含めて信じてよいか

## Product surfaces

finBIは次のDeskへ収束させます。

| Surface | Role |
|---|---|
| Command Center | 総資産、主要リスク、未解決の意思決定 |
| Portfolio | 保有、配分、重複、risk contribution、rebalance |
| Frontier Lab | efficient frontier、制約、what-if配分 |
| FX Desk | USDJPY、swap、carry、leverage、margin、stress |
| Rates Desk | policy rates、yield curve、real yields、bond alternatives |
| Valuation | PER、earnings yield、EPS growth、factor comparison |
| Macro | inflation、liquidity、growth、regime |
| Event Lens | news → affected assets → portfolio impact → action/no-action |
| Products | broker、bank、ETF、fund、deposit比較 |
| Tax & Cashflow | 税、NISA/iDeCo、ふるさと納税、副業cashflow |
| Backtest Lab | strategy、rolling window、regime、stress |
| Ask / Recipes | 質問を正準分析レシピへroute |
| Audit | source、as-of、vintage、assumption、revision |

対応質問の正準定義は [`data/questions/catalog.v1.json`](data/questions/catalog.v1.json) が所有します。**新しいchartを増やすだけでは機能追加とみなしません。質問レシピが増えて初めてcapabilityが増えます。**

## Architecture

finBIは表示と意思決定のsemantic layerです。一次データのwarehouseを複製しません。

```text
investor2      portfolio analytics / optimization
kakeibo        household cashflow
econalert      macro events
auto-invest    strategy experiments
broker / bank / official / market providers
             ↓
finBI adapters / versioned observation contracts
             ↓
question recipe registry
             ↓
calculation / comparison / scenario
             ↓
Financial Decision Workbench
```

既存のpoint-in-time snapshot検証、source/as-of/unit、fail-closeは維持します。

## Public / private boundary

このrepositoryとGitHub Pagesはpublicです。

そのため、**口座番号、個人の取引明細、生の残高、税務書類、credential、個人識別情報はcommitしません。**

- Public Pages: verified public dataまたはsynthetic/sample data
- Private analysis: localまたはconnected private source
- 両者で共有するもの: schema、計算レシピ、view contract
- 共有しないもの: private raw data

## First live recipe: Rates Desk / two-point comparison

現在の公開UIは保存済みDGS10/DGS2 snapshotを使い、次を行います。

1. 保存済み時系列を見る
2. 開始日・終了日を選ぶ
3. Pythonで比較する
4. 元の値、percentage point差、basis point差を読む
5. source / observed range / retrieved_atを確認する

比較期間はURLの`start` / `end`で復元できます。現在値の速報ではありません。

### Current data authority

`data/snapshots/` のversioned snapshotは、series ID、単位、観測期間、取得時刻、source/provenance、availability evidenceを保持します。

観測値から得られる差分、bp、direction、yield-curve shapeは保存済みの別ledgerを持たず、`code/static_bi.py` が決定論的に導出します。

availabilityを一次情報で証明できないsnapshot、取得時刻より後に利用可能になった観測、provenance欠落、観測順序破損はfail-closeします。

## Financial correctness rules

- observed / derived / estimate / assumption / interpretationを分離する
- 日次・月次平均・四半期proxy・実際のbroker mechanicsを黙って混ぜない
- 年率化方法とsampling frequencyを明示する
- leverageは fixed-notional / constant leverage / leveraged product を区別する
- backtestはwindowとstart-date/regime sensitivityを確認する
- 現在の価格・金利・swap・商品条件・税制・ニュースはcurrent sourceで再確認する
- stale/cached値をliveと呼ばない
- provenance矛盾はfail-closeする

## Verification

fresh cloneでPython 3.12、Node.js、uvが利用可能ならfast gateは1コマンドです。

```bash
uvx --from prek==0.4.11 prek run --all-files
```

`prek.toml` がRuff format/lint、Pyrefly、offline unittest、browser syntax/accessibility contractを所有します。GitHub Actionsは同じgateに加え、Pages artifact build、HTTP route smoke、clean checkoutを検証します。

## Work state

未解決作業はREADMEへ複製せずGitHub Issuesを正準とします。

- Master redesign: https://github.com/KAFKA2306/finBI/issues/19
- Issues: https://github.com/KAFKA2306/finBI/issues
- Actions: https://github.com/KAFKA2306/finBI/actions
