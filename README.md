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

現在の公開Pagesでは、**FX** と **Rates** の2つのBI viewが実稼働しています。その他のSurfaceは、正準データまたは正準analytics outputが接続されるまで `PLANNED` とし、仮の数値を表示しません。

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

| Surface | State | BI role |
|---|---|---|
| FX | **LIVE** | USDJPY、SBI swap、3x carry、scenario、margin reference、source audit |
| Rates | **LIVE** | policy rates、Treasury yield curve、point-in-time comparison |
| Overview | PLANNED | 総資産、市場、主要リスク、重要KPI |
| Portfolio | PLANNED | 保有、配分、重複、risk contribution、rebalance |
| Frontier | PLANNED | efficient frontier、制約、what-if配分 |
| Valuation | PLANNED | PER、earnings yield、EPS/FCF growth、IRR scenario |
| Macro | PLANNED | inflation、liquidity、growth、regime |
| Events | PLANNED | event前後の市場・fundamental変化とexposure |
| Products | PLANNED | broker、bank、ETF、fund、deposit比較 |
| Tax & Cashflow | PLANNED | 税、NISA/iDeCo、ふるさと納税、副業cashflow |
| Backtest | PLANNED | strategy、rolling window、regime、stress |
| Audit | PLANNED | source、as-of、vintage、assumption、revisionの横断表示 |

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

この制約のため、個人ポートフォリオや口座横断Frontierをpublic snapshotへコピーしません。`investor2` 等の正準analytics outputまたはprivate/local inputをread-onlyで接続できるまでは `PLANNED` とします。

## Live BI view: FX / USDJPY 3x

`data/snapshots/usdjpy-sbi-2026-09-03.json` に、公開確認できた情報をpoint-in-time snapshotとして固定しています。

- USD/JPY: Reutersの2026-09-03市場観測
- SBI FX current raw swap: 2026-09-03適用分
- SBI FX normalized scenario reference: 2026-09-02適用分 117円/日/1万USD
- SBI 3x必要保証金reference
- SBI 3x loss-cut reference
- Fed target midpoint
- BOJ overnight-call guideline

重要な境界として、2026-09-03のSBI buy swap `468円 / 1万USD` は **付与日数を検証できていないraw observation** です。これを1日分とはみなしません。

1年scenarioは別に、2026-09-02の `117円/日/1万USD` が365日変わらないと明示的に仮定して計算します。したがってこれは将来swap予測ではありません。

現在のsnapshot contractでは、1万USD・初期3倍・fixed initial notionalとして次をPythonで決定論的に導出します。

- initial notional / equity
- annualized scenario swap
- carry on initial equity
- carryを相殺するbreak-even FX move
- Fed midpoint - BOJ policy-rate gap
- USDJPY -20%〜+10%の1年scenario table

spread、slippage、tax、transaction cost、途中のmargin-call / liquidation pathは含めません。特にpolicy-rate gapをbroker swapへ代用しません。

金融計算は `code/static_bi.py` が所有し、`web/fx.js` はPythonから返された結果の描画だけを行います。

## Live BI view: Rates / two-point comparison

保存済みDGS10/DGS2 snapshotを使い、次を行います。

1. 保存済み時系列を見る
2. 開始日・終了日を選ぶ
3. Pythonで比較する
4. 元の値、percentage point差、basis point差を読む
5. source / observed range / retrieved_atを確認する

比較期間はURLの`start` / `end`で復元できます。現在値の速報ではありません。

### Snapshot authority

`data/snapshots/` のversioned snapshotは、対象viewに必要なsource、観測時点、取得時刻、availability、assumptionを保持します。

Treasury観測値から得られる差分、bp、direction、yield-curve shapeは保存済みの別ledgerを持たず、`code/static_bi.py` が決定論的に導出します。

availabilityを一次情報で証明できないsnapshot、取得時刻より後に利用可能になった観測、provenance欠落、観測順序破損はfail-closeします。

## Financial correctness rules

- observed / derived / estimate / assumption / interpretationを分離する
- 日次・月次平均・四半期proxy・実際のbroker mechanicsを黙って混ぜない
- 年率化方法とsampling frequencyを明示する
- leverageは fixed-notional / constant leverage / leveraged product を区別する
- backtestはwindowとstart-date/regime sensitivityを確認する
- 現在の価格・金利・swap・商品条件・税制・ニュースはcurrent sourceで再確認する
- stale/cached値をliveと呼ばない
- missing holdingを0として扱わない
- policy-rate gapをactual broker swapへsilent代用しない
- provenance矛盾はfail-closeする

## Verification

fresh cloneでPython 3.12、Node.js、uvが利用可能ならfast gateは1コマンドです。

```bash
uvx --from prek==0.4.11 prek run --all-files
```

`prek.toml` がRuff format/lint、Pyrefly、offline unittest、browser syntax/accessibility contractを所有します。GitHub Actionsは同じgateに加え、Pages artifact build、HTTP route smoke、clean checkout、公開Pagesのdesktop/mobile E2Eを検証します。

## Work state

未解決作業はREADMEへ複製せずGitHub Issuesを正準とします。

- Master redesign: https://github.com/KAFKA2306/finBI/issues/19
- Issues: https://github.com/KAFKA2306/finBI/issues
- Actions: https://github.com/KAFKA2306/finBI/actions
