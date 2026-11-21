// In-memory, presentation-only ETF screening. Financial observations remain owned by the CSV provider.
const HEADER = {
  sector: ['分野', 'sector', 'category', 'industry'],
  ticker: ['ティッカー', 'ticker', 'symbol', 'code'],
  name: ['商品名', 'name', 'fund_name', 'description'],
  size: ['参考規模(百万USD)', 'market_cap_million_usd', 'size_musd', 'size'],
  fee: ['経費率(%)', 'expense_ratio_pct', 'fee_pct', 'fee'],
  beta: ['ベータ', 'beta'],
  m1: ['1か月騰落率(%)', 'return_1m_pct', '1m_return'],
  y1: ['1年騰落率(%)', 'return_1y_pct', '1y_return'],
  ytd: ['年初来騰落率(%)', 'return_ytd_pct', 'ytd_return'],
  pe: ['ETF PER参考', 'pe_reference', 'pe'],
  form: ['形態', 'position_type', 'form'],
  score: ['商品条件点', 'score_source', 'score'],
  bucket: ['調査区分', 'research_bucket', 'bucket'],
  date: ['基準日', 'as_of', 'date'],
  url: ['出典URL', 'source_url', 'source'],
  note: ['注意事項', 'note', 'notes'],
};
const REQUIRED = ['ticker', 'name', 'sector', 'date'];
export const COLUMNS = [
  ['sector', '分野'], ['ticker', 'ティッカー'], ['name', '商品名'],
  ['size', '参考規模(百万USD)'], ['fee', '経費率(%)'], ['beta', 'ベータ'],
  ['m1', '1か月騰落率(%)'], ['y1', '1年騰落率(%)'], ['ytd', '年初来騰落率(%)'],
  ['pe', 'ETF PER参考'], ['form', '形態'], ['score', '商品条件点'],
  ['bucket', '調査区分'], ['date', '基準日'], ['url', '出典URL'], ['note', '注意事項'],
];

export function parseCsv(input) {
  const text = input.replace(/^\ufeff/, '');
  if (!text.trim()) throw new Error('CSVが空です。');
  const rows = []; let row = []; let value = ''; let quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') { value += '"'; i++; }
      else if (ch === '"') quoted = false;
      else value += ch;
    } else if (ch === '"') {
      if (value !== '') throw new Error('CSVの引用符の位置が不正です。');
      quoted = true;
    } else if (ch === ',') { row.push(value); value = ''; }
    else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && text[i + 1] === '\n') i++;
      row.push(value); value = '';
      if (row.some(v => v.trim() !== '')) rows.push(row);
      row = [];
    } else value += ch;
  }
  if (quoted) throw new Error('CSVの引用符が閉じられていません。');
  row.push(value);
  if (row.some(v => v.trim() !== '')) rows.push(row);
  return rows;
}

function numberOrNull(value, label, line) {
  if (value === '' || value === undefined || value === null || value.trim() === '—') return null;
  const number = Number(value.replaceAll(',', ''));
  if (!Number.isFinite(number)) throw new Error(`${line}行目の「${label}」が数値ではありません。`);
  return number;
}
function validSource(value) {
  if (!value) return '';
  try { const u = new URL(value); return ['https:', 'http:'].includes(u.protocol) ? u.href : ''; }
  catch { return ''; }
}
function validDate(value) {
  if (!value) return false;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const [y,m,d] = value.split('-').map(Number);
  const dt = new Date(Date.UTC(y,m-1,d));
  return dt.toISOString().slice(0,10) === value;
}

export function readEtfCsv(text) {
  const rows = parseCsv(text);
  if (rows.length < 2) throw new Error('見出しに加えて、少なくとも1件のデータが必要です。');
  if (rows.length > 20001) throw new Error('一度に読み込めるのは20,000銘柄までです。');
  const labels = rows[0].map(h => h.trim().toLowerCase());
  if (new Set(labels).size !== labels.length) throw new Error('CSV見出しが重複しています。');
  const col = {};
  for (const [key, aliases] of Object.entries(HEADER)) col[key] = labels.findIndex(h => aliases.some(a => a.toLowerCase() === h));
  const missing = REQUIRED.filter(key => col[key] < 0);
  if (missing.length) throw new Error(`必要な見出しがありません: ${missing.map(k => HEADER[k][0]).join('、')}`);
  const out = [], seen = new Set(), dates = new Set(), skipped = [];
  for (let i = 1; i < rows.length; i++) {
    const r = rows[i];
    if (r.length !== labels.length) throw new Error(`${i+1}行目の列数が見出しと異なります。`);
    const get = k => col[k] < 0 ? '' : r[col[k]].trim();
    const ticker = get('ticker').toUpperCase();
    if (!/^[A-Z0-9.\-^]{1,18}$/.test(ticker)) throw new Error(`${i+1}行目のティッカーが不正です。`);
    if (!get('name')) throw new Error(`${i+1}行目の商品名が空です。`);
    const date = get('date');
    if (!validDate(date)) throw new Error(`${i+1}行目の基準日が不正です（YYYY-MM-DD形式）。`);
    dates.add(date);
    if (seen.has(ticker)) { skipped.push(ticker); continue; }
    seen.add(ticker);
    const entry = {ticker, name:get('name'), sector:get('sector') || '未分類', date,
      form:get('form') || '未記載', bucket:get('bucket'), note:get('note'),
      url:validSource(get('url'))};
    for (const k of ['size','fee','beta','m1','y1','ytd','pe','score']) {
      entry[k] = numberOrNull(get(k), HEADER[k][0], i+1);
    }
    if (entry.fee !== null && entry.fee < 0 || entry.size !== null && entry.size < 0 || entry.pe !== null && entry.pe < 0) {
      throw new Error(`${i+1}行目の規模・経費率・PERに負数があります。`);
    }
    out.push(entry);
  }
  if (dates.size !== 1) throw new Error(`基準日が${dates.size}種類混在しています。同一日のCSVだけを比較してください。`);
  return {rows:out, date:[...dates][0], skipped};
}

export function screenRows(rows, filters={}) {
  const query = (filters.query || '').trim().toLowerCase();
  const maxFee = filters.maxFee === '' || filters.maxFee == null ? null : Number(filters.maxFee);
  const minSize = filters.minSize === '' || filters.minSize == null ? null : Number(filters.minSize);
  const valid = rows.filter(r => {
    if (query && !`${r.ticker} ${r.name} ${r.sector}`.toLowerCase().includes(query)) return false;
    if (filters.sector && r.sector !== filters.sector) return false;
    if (maxFee !== null && (r.fee === null || r.fee > maxFee)) return false;
    if (minSize !== null && (r.size === null || r.size < minSize)) return false;
    if (filters.longOnly && r.form !== 'L') return false;
    if (filters.drawdown && (r.m1 === null || r.m1 > -10)) return false;
    return true;
  });
  const key = filters.sort || 'size', asc = key === 'fee' || key === 'pe' || key === 'm1asc';
  const prop = key === 'm1asc' ? 'm1' : key;
  return valid.sort((a,b) => {
    const av=a[prop],bv=b[prop];
    if(av === null && bv !== null) return 1;
    if(bv === null && av !== null) return -1;
    const diff=(av ?? 0)-(bv ?? 0);
    return diff === 0 ? a.ticker.localeCompare(b.ticker) : (asc ? diff : -diff);
  });
}

export function metrics(rows) {
  const fees=rows.map(r=>r.fee).filter(n=>n !== null).sort((a,b)=>a-b);
  const observed=rows.filter(r=>r.m1 !== null);
  const mid=Math.floor(fees.length / 2);
  return {
    count: rows.length,
    medianFee: fees.length ? fees.length % 2 ? fees[mid] : (fees[mid-1]+fees[mid])/2 : null,
    decliners: observed.length ? observed.filter(r=>r.m1<0).length : null,
    observationCount: observed.length,
    sectorCount: new Set(rows.map(r=>r.sector)).size,
  };
}

export function csvOutput(rows) {
  const esc = (v, key) => {
    let s = v == null ? '' : String(v);
    // Guard spreadsheet apps against formula execution from untrusted text cells.
    if (['name','sector','bucket','note','form'].includes(key) && /^[=+@\-\t\r]/.test(s)) s = "'" + s;
    return /[",\r\n]/.test(s) ? `"${s.replaceAll('"','""')}"` : s;
  };
  return '\ufeff' + [COLUMNS.map(x=>esc(x[1],x[0])).join(','), ...rows.map(r=>COLUMNS.map(([k])=>esc(r[k],k)).join(','))].join('\r\n')+'\r\n';
}
