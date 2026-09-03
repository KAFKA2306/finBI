https://kafka2306.github.io/finBI/

# finBI

[![Static Python BI](https://github.com/KAFKA2306/finBI/actions/workflows/static-bi.yml/badge.svg)](https://github.com/KAFKA2306/finBI/actions/workflows/static-bi.yml)

**finBI is financial BI.**

目的はIssue管理や分析エージェント化ではありません。金融・投資で繰り返し出てくる論点を、**同じデータ・同じ計算・同じ比較軸で見える化し、判断しやすくするBI**です。

金融系GitHub Issuesは、finBIが「何を見せられるべきか」を決める要求源として使います。Issue番号・タスク状態・完了条件そのものをfinBIの正本にはしません。

```text
canonical data
  ↓
validated metrics
  ↓
comparison / scenario
  ↓
chart / table / KPI
  ↓
decision-supporting BI view
  ↓
source / as-of / revision
```

現在の公開Pagesで実稼働しているのは、保存済み米国債snapshotを使った `Rates Desk` の2点比較です。これはfinBI全体では最初のBI viewです。

## What should finBI make visible?

### Portfolio / allocation

- 現在の資産配分、通貨配分、口座横断配分
- risk contribution、集中、重複
- 効率的フロンティア
- minimum variance / same-return min-vol / max Sharpe
- 何%追加・削減した場合のbefore / after

### FX / Rates / Bonds

- USD/JPY spot、swap、carry、実効レバレッジ
- fixed-notional / constant leverage / leveraged productの差
- margin、loss-cut headroom、stress
- SBI・楽天・銀行・FX業者の比較
- 政策金利、実質金利、イールドカーブ
- JGB / UST / MMF / MRF / 定期預金との比較

### Valuation / Fundamentals

- PER、earnings yield、EPS / FCF growth
- Revenue / EPS/share / FCF/share CAGR
- growth × terminal multipleのIRR scenario
- Mag7 / Top10 / semis / AI infrastructure比較
- revision history

### Macro / Liquidity / Events

- CPI / PCE / jobs / PMI / money supply / liquidity
- 前回、1週、1か月、前年差
- market / portfolio exposureとの関係
- observed fact / forecast / interpretationの分離

### Backtest / Risk

- CAGR、Vol、Sharpe、Sortino、Max DD、CVaR
- rolling period、start-date sensitivity、regime差
- transaction cost、carry、funding、turnover
- proxyとexecutable strategyの区別

### Products / Tax / Cashflow

- ETF・投信・預金・証券会社・銀行の横比較
- fee、金利、税、為替、流動性
- 予定納税、ふるさと納税、NISA/iDeCo、副業cashflowのシナリオ表

### Audit

- source
- observation date / as-of
- retrieved_at
- vintage / revision
- verified / proxy / estimate / assumption
- stale / unavailable

## BI surfaces

| Surface | BI role |
|---|---|
| Overview | 総資産、市場、主要リスク、重要KPI |
| Portfolio | 保有、配分、重複、risk contribution、rebalance |
| Frontier | efficient frontier、制約、what-if配分 |
| FX | USDJPY、swap、carry、leverage、margin、stress |
| Rates | policy rates、yield curve、real yields、bond alternatives |
| Valuation | PER、earnings yield、EPS/FCF growth、IRR scenario |
| Macro | inflation、liquidity、growth、regime |
| Events | event前後の市場・fundamental変化とexposure |
| Products | broker、bank、ETF、fund、deposit比較 |
| Tax & Cashflow | 税、NISA/iDeCo、ふるさと納税、副業cashflow |
| Backtest | strategy、rolling window、regime、stress |
| Audit | source、as-of、vintage、assumption、revision |

`data/questions/catalog.v1.json` は、過去に繰り返し出た金融質問を **どのBI surface / metricで解けるようにすべきか整理する内部カタログ**です。UIやdata authorityより上位の「Issue Solver」にはしません。

## Architecture

finBIは表示・集計・比較のBI layerです。一次データのwarehouse、Issue tracker、研究実行基盤を複製しません。

```text
investor2 / CrewTrade / econalert / auto-invest / official providers
                         ↓
              canonical outputs / snapshots
                         ↓
                  finBI adapters
                         ↓
             deterministic BI metrics
                         ↓
             charts / tables / scenarios
                         ↓
                       finBI
```

Issueで必要になった分析は、可能な限り既存ownerの正準出力をfinBIで可視化します。計算authorityをfinBIへ重複移植しません。

## Public / private boundary

このrepositoryとGitHub Pagesはpublicです。

そのため、**口座番号、個人の取引明細、生の残高、税務書類、credential、個人識別情報はcommitしません。**

- Public Pages: verified public dataまたは公開可能なsample data
- Private analysis: localまたはconnected private source
- 両者で共有するもの: schema、計算規則、view contract
- 共有しないもの: private raw data

## First live BI view: Rates / two-point comparison

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
