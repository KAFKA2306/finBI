import { COLUMNS, readEtfCsv, screenRows, metrics, csvOutput } from './screener-core.mjs';

const $ = id => document.getElementById(id);
const state = {source:[], visible:[], selected:new Set(), date:'', file:''};
const controls = ['search','sector','max-fee','min-size','sort','long-only','drawdown'];
const svgNS = 'http://www.w3.org/2000/svg';
const number = (v, digits=2) => v === null || v === undefined ? '—' : Number(v).toLocaleString('ja-JP',{maximumFractionDigits:digits,minimumFractionDigits:digits});
const text = (tag, value, className) => { const el=document.createElement(tag); el.textContent=value; if (className) el.className=className; return el; };
const svg = (tag, attrs={}, label='') => { const el=document.createElementNS(svgNS, tag); for (const [k,v] of Object.entries(attrs)) el.setAttribute(k,String(v)); if (label) el.textContent=label; return el; };

function message(value, isError=false) { $('load-message').textContent=value; $('load-message').classList.toggle('is-error',isError); }
function filterState() {return {
  query:$('search').value,sector:$('sector').value,maxFee:$('max-fee').value,
  minSize:$('min-size').value,sort:$('sort').value,longOnly:$('long-only').checked,
  drawdown:$('drawdown').checked,
};}
function categoryOptions() {
  const control=$('sector'); const old=control.value;
  control.replaceChildren(new Option('すべての分野',''));
  [...new Set(state.source.map(x=>x.sector))].sort((a,b)=>a.localeCompare(b,'ja')).forEach(v=>control.add(new Option(v,v)));
  if([...control.options].some(o=>o.value===old)) control.value=old;
}
function resetFilters(update=true) {
  $('search').value=''; $('sector').value=''; $('max-fee').value=''; $('min-size').value='';
  $('long-only').checked=true; $('drawdown').checked=false; $('sort').value='size';
  if(update) render();
}
function applyPreset(key) {
  resetFilters(false);
  if (key === 'lowfee') $('max-fee').value='0.2';
  if (key === 'infra') {
    const match=[...$('sector').options].find(x=>/公益|インフラ|電力|utilities|infrastructure/i.test(x.value));
    if (match) $('sector').value=match.value;
    else $('search').value='インフラ';
  }
  if (key === 'semis') {
    const match=[...$('sector').options].find(x=>/半導体|semiconductor/i.test(x.value));
    if (match) $('sector').value=match.value;
    else $('search').value='半導体';
  }
  if (key === 'drawdown') $('drawdown').checked=true;
  render();
}
function renderSummary() {
  if (!state.source.length) {
    for (const id of ['metric-count','metric-fee','metric-decliners','metric-sectors']) $(id).textContent='—';
    $('metric-count-sub').textContent='データを選択してください';
    $('metric-decliners-sub').textContent='値動きのある行のみ';return;
  }
  const s=metrics(state.visible);
  $('metric-count').textContent=s.count.toLocaleString('ja-JP');
  $('metric-count-sub').textContent=`全${state.source.length.toLocaleString('ja-JP')}件から抽出`;
  $('metric-fee').textContent=s.medianFee===null?'—':`${number(s.medianFee)}%`;
  $('metric-decliners').textContent=s.decliners===null?'—':`${s.decliners}件`;
  $('metric-decliners-sub').textContent=`観測あり ${s.observationCount}件中`;
  $('metric-sectors').textContent=String(s.sectorCount);
}
function drawSectors() {
  const target=$('sector-chart');target.replaceChildren();
  if(!state.visible.length) {target.textContent='条件に合うデータがありません。';return;}
  const counts=new Map(); for(const r of state.visible) counts.set(r.sector,(counts.get(r.sector)||0)+1);
  const sorted=[...counts].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0],'ja')).slice(0,8);
  const maximum=sorted[0][1];
  for(const [sector,count] of sorted){
    const row=text('div','','sector-bar-row');
    const name=text('span',sector);name.title=sector;
    const track=text('div','','bar'); const fill=text('span','');fill.style.width=`${count/maximum*100}%`;track.append(fill);
    row.append(name,track,text('strong',count.toLocaleString('ja-JP'))); target.append(row);
  }
  target.setAttribute('aria-label',sorted.map(([s,n])=>`${s}: ${n}件`).join('、'));
}
function drawScatter() {
  const el=$('fee-chart');el.replaceChildren(svg('title',{},'経費率と1か月騰落率'));
  const values=state.visible.filter(r=>r.fee!==null&&r.m1!==null);
  if(!values.length) {el.append(svg('text',{x:20,y:100,fill:'currentColor','font-size':13},'描画できる数値がありません。'));return;}
  const sample=values.length<=500?values:values.filter((_,i)=>i % Math.ceil(values.length/500)===0);
  const W=480,H=210, p={left:48,right:20,top:18,bottom:28};
  const loX=0,hiX=Math.max(...values.map(x=>x.fee),.1);
  const rawY=values.map(x=>x.m1),loY=Math.min(0,...rawY),hiY=Math.max(0,...rawY);
  const hi=Math.max(hiY,loY+1);
  const xx=x=>p.left + (x-loX)/hiX*(W-p.left-p.right);
  const yy=y=>p.top + (hi-y)/(hi-loY)*(H-p.top-p.bottom);
  for(let i=0;i<=4;i++) {
    const y=loY+(hi-loY)*i/4;
    el.append(svg('line',{x1:p.left,x2:W-p.right,y1:yy(y),y2:yy(y),stroke:'var(--k-color-border)'}));
    el.append(svg('text',{x:5,y:yy(y)+4,fill:'var(--k-color-muted-foreground)','font-size':10},number(y,1)));
  }
  if(loY<0 && hi>0) el.append(svg('line',{x1:p.left,x2:W-p.right,y1:yy(0),y2:yy(0),stroke:'var(--k-color-foreground)','stroke-dasharray':'4 3',opacity:.5}));
  for(let i=0;i<=4;i++) {
    const x=hiX*i/4;
    el.append(svg('text',{x:xx(x),y:H-8,'text-anchor':'middle',fill:'var(--k-color-muted-foreground)','font-size':10},number(x,2)));
  }
  for(const r of sample) {
    const dot=svg('circle',{cx:xx(r.fee),cy:yy(r.m1),r:3,fill:r.m1<0?'var(--k-color-danger)':'var(--k-color-primary)',opacity:.65});
    dot.append(svg('title',{},`${r.ticker}｜経費率 ${number(r.fee)}%｜1か月 ${number(r.m1)}%`));el.append(dot);
  }
  el.setAttribute('aria-label',`費用と値動きの散布図。対象${values.length}件、描画${sample.length}点。`);
}
function td(value, cls) {return text('td',value,cls);}
function tableRow(r) {
  const tr=document.createElement('tr');
  const check=td('','check-cell'); const input=document.createElement('input');
  input.type='checkbox'; input.checked=state.selected.has(r.ticker); input.setAttribute('aria-label',`${r.ticker}を比較に追加`);
  input.addEventListener('change',()=>{
    if(input.checked && state.selected.size>=4) {input.checked=false;message('比較できるのは最大4銘柄です。',true);return;}
    if(input.checked)state.selected.add(r.ticker);else state.selected.delete(r.ticker);
    renderCompare();
  });check.append(input);tr.append(check);
  const name=td('','name-cell');name.append(text('strong',r.ticker),text('span',r.name));tr.append(name,td(r.sector));
  tr.append(td(number(r.size,0),'numeric'),td(r.fee===null?'—':`${number(r.fee)}%`,'numeric'));
  tr.append(td(r.m1===null?'—':`${r.m1>0?'+':''}${number(r.m1)}%`,'numeric '+(r.m1===null?'':r.m1<0?'down':'up')));
  tr.append(td(number(r.pe),'numeric'));
  const source=td(''); if(r.url){const link=document.createElement('a');link.href=r.url;link.target='_blank';link.rel='noopener noreferrer';link.textContent='出典';source.append(link);}else source.textContent='未記載';
  tr.append(source);return tr;
}
function renderTable() {
  const target=$('table-body');target.replaceChildren();
  if(!state.source.length || !state.visible.length){ const tr=document.createElement('tr');const empty=td(state.source.length?'条件に合うETFがありません。':'CSVを読み込むと、ここに候補が表示されます。','table-empty');empty.colSpan=8;tr.append(empty);target.append(tr); }
  else {const fragment=document.createDocumentFragment();state.visible.slice(0,200).forEach(r=>fragment.append(tableRow(r)));target.append(fragment);}
  $('table-status').textContent=state.source.length?`${state.visible.length.toLocaleString('ja-JP')}件該当・画面は先頭${Math.min(state.visible.length,200)}件`: 'データがありません。';
  $('export').disabled=!state.visible.length;
}
function renderCompare() {
  const target=$('compare-grid');target.replaceChildren();
  const chosen=[...state.selected].map(t=>state.source.find(r=>r.ticker===t)).filter(Boolean);
  $('compare-help').textContent=chosen.length?`${chosen.length} / 4銘柄選択中。提供数値を並べています。`:'表の左側で、最大4銘柄を選べます。';
  for(const r of chosen){
    const tile=text('div','','compare-tile');tile.append(text('h3',r.ticker));
    const dl=document.createElement('dl');
    for(const [label,value] of [['分野',r.sector],['経費率',r.fee===null?'—':number(r.fee)+'%'],['規模',number(r.size,0)],['1か月',r.m1===null?'—':number(r.m1)+'%'],['1年',r.y1===null?'—':number(r.y1)+'%'],['PER参考',number(r.pe)]]){
      const row=document.createElement('div');row.append(text('dt',label),text('dd',value));dl.append(row);
    }
    tile.append(dl); target.append(tile);
  }
}
function render() {
  state.visible=screenRows(state.source,filterState());
  renderSummary();drawSectors();drawScatter();renderTable();renderCompare();
}
async function loadFile(file) {
  if(!file) return;
  if(file.size>8*1024*1024) {message('ファイルサイズは8MB以下にしてください。',true);return;}
  if(!/\.csv$/i.test(file.name)){message('CSV形式のファイルを選んでください。',true);return;}
  try{
    const parsed=readEtfCsv(await file.text());
    state.source=parsed.rows;state.date=parsed.date;state.file=file.name;state.selected.clear();
    $('dataset-label').textContent=file.name;
    $('as-of-label').textContent=parsed.date;
    $('source-count').textContent=parsed.rows.length.toLocaleString('ja-JP');
    categoryOptions();resetFilters(false);render();
    message(`${parsed.rows.length.toLocaleString('ja-JP')}件を読み込みました。${parsed.skipped.length?`重複ティッカー ${parsed.skipped.length}件を除外。`:''} 絞り込みと比較ができます。`);
  }catch(error){message(`読み込み不可: ${error.message}`,true);}
}
function exportCsv(filename, rows) {
  const value=csvOutput(rows);
  const blob=new Blob([value],{type:'text/csv;charset=utf-8'});
  const url=URL.createObjectURL(blob),link=document.createElement('a');
  link.href=url;link.download=filename;document.body.append(link);link.click();link.remove();
  URL.revokeObjectURL(url);
}

$('data-file').addEventListener('change',e=>loadFile(e.target.files?.[0]));
for(const id of controls) $(id).addEventListener(id==='search'?'input':'change',render);
$('reset').addEventListener('click',()=>resetFilters());
document.querySelectorAll('[data-preset]').forEach(b=>b.addEventListener('click',()=>applyPreset(b.dataset.preset)));
$('export').addEventListener('click',()=>state.visible.length && exportCsv(`finbi-etf-filtered-${state.date}.csv`,state.visible));
$('clear-selected').addEventListener('click',()=>{state.selected.clear();renderTable();renderCompare();});
$('template').addEventListener('click',()=>{
  const head=COLUMNS.map(x=>x[1]).join(',')+'\r\n';
  const blob=new Blob(['\ufeff'+head],{type:'text/csv;charset=utf-8'});
  const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='finbi-etf-template.csv';document.body.append(a);a.click();a.remove();URL.revokeObjectURL(url);
});
render();
