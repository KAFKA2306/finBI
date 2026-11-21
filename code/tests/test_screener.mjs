import test from 'node:test';
import assert from 'node:assert/strict';
import {readEtfCsv, parseCsv, screenRows, metrics, csvOutput} from '../../web/screener-core.mjs';
import {readFileSync} from 'node:fs';

const sample = `分野,ティッカー,商品名,参考規模(百万USD),経費率(%),1か月騰落率(%),形態,基準日,出典URL\n半導体,SMH,Semis,50000,0.35,-18,L,2026-11-20,https://example.com/smh\n公益,XLU,Utilities,20000,0.08,3,L,2026-11-20,https://example.com/xlu\n公益,SOXL,"Leveraged, fund",400,0.8,-54,L3X,2026-11-20,https://example.com/soxl\n`;
const data = readEtfCsv(sample);
test('CSVの引用符と見出しを正しく読み、必要な値だけ扱う',()=>{
  assert.equal(parseCsv(sample).length,4);
  assert.equal(data.rows.length,3);
  assert.equal(data.rows[2].name,'Leveraged, fund');
  assert.equal(data.date,'2026-11-20');
});
test('レバレッジを除き、厳格な価格フィルターと並び順で絞り込む',()=>{
  assert.deepEqual(screenRows(data.rows,{longOnly:true, maxFee:0.4, sort:'fee'}).map(x=>x.ticker),['XLU','SMH']);
  assert.deepEqual(screenRows(data.rows,{drawdown:true, longOnly:true,sort:'size'}).map(x=>x.ticker),['SMH']);
  assert.equal(metrics(screenRows(data.rows,{longOnly:true})).medianFee,0.215);
});
test('異なる基準日・不正数値を安易に比較しない',()=>{
  assert.throws(()=>readEtfCsv(sample.replace('SOXL,"Leveraged, fund",400,0.8,-54,L3X,2026-11-20','SOXL,"Leveraged, fund",400,0.8,-54,L3X,2026-11-19')),/基準日が2種類/);
  assert.throws(()=>readEtfCsv(sample.replace('20000,0.08','20000,not-a-number')),/数値ではありません/);
  assert.throws(()=>readEtfCsv(sample.replace('2026-11-20','2026-11-31')),/基準日が不正/);
});
test('エクスポート結果を同じ入力として再読込でき、CSV式注入を抑止する',()=>{
  const unsafe=sample.replace('Semis','"=""HYPERLINK"""');
  const extracted=csvOutput(readEtfCsv(unsafe).rows);
  assert.ok(extracted.includes("'="));
  assert.equal(readEtfCsv(extracted).rows.length,3);
});
test('20,000件のCSVを扱い、201件目以降もフィルターで取得可能',()=>{
  const header='分野,ティッカー,商品名,基準日';
  const rows=Array.from({length:20000},(_,i)=>`公益,E${String(i).padStart(5,'0')},Fund ${i},2026-11-20`);
  const full=readEtfCsv([header,...rows].join('\n'));
  assert.equal(full.rows.length,20000);
  assert.equal(screenRows(full.rows,{query:'E19999'}).length,1);
});
