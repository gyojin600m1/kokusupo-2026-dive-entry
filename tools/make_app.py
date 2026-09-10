# -*- coding: utf-8 -*-
"""国スポ2026 飛込 エントリー確認アプリ（index.html 1枚）を書き出す。"""
import json
from pathlib import Path

built = json.load(open("dive_built.json"))
kana = json.load(open("kana.json"))
try:
    RES = json.load(open("results.json"))
except FileNotFoundError:
    RES = {"results": {}, "done": []}

PREFS = ["北海道","青森県","岩手県","宮城県","秋田県","山形県","福島県","茨城県","栃木県","群馬県",
         "埼玉県","千葉県","東京都","神奈川県","新潟県","富山県","石川県","福井県","山梨県","長野県",
         "岐阜県","静岡県","愛知県","三重県","滋賀県","京都府","大阪府","兵庫県","奈良県","和歌山県",
         "鳥取県","島根県","岡山県","広島県","山口県","徳島県","香川県","愛媛県","高知県","福岡県",
         "佐賀県","長崎県","熊本県","大分県","宮崎県","鹿児島県","沖縄県"]

# ---- 公式の順位一覧を entries / people に流し込む ----
RANK = {}
for no, blk in RES["results"].items():
    for r in blk["rows"]:
        RANK[(int(no), r["name"].replace(" ", ""), r["pref"])] = r
for e in built["entries"]:
    r = RANK.get((e["ev"], e["name"].replace(" ", ""), e["pref"]))
    if r:
        e["r"] = {"rank": r["rank"], "pts": r["points"], "st": r["status"]}
        if r["status"]:
            e["wd"] = True
for ev in built["events"]:
    blk = RES["results"].get(str(ev["no"]))
    if blk:
        ev["done"] = True
        if blk["start"] and not ev.get("start"):
            ev["start"] = blk["start"]
        ev["wd"] = sum(1 for r in blk["rows"] if r["status"])
bykey = {}
for e in built["entries"]:
    bykey.setdefault((e["name"].replace(" ", ""), e["pref"]), {})[e["ev"]] = e
for p in built["people"]:
    for ref in p["evs"]:
        src = bykey.get((p["name"].replace(" ", ""), p["pref"]), {}).get(ref["ev"])
        if src and "r" in src:
            ref["r"] = src["r"]
            ref["wd"] = src["wd"]

people = built["people"]
have = {p["pref"] for p in people}
data = {
    "meet": {
        "dates": "2026年9月10日（木）〜12日（土）",
        "venue": "セントラルスポーツ宮城Ｇ21プール（宮城県利府町）",
    },
    "stats": {
        "entries": len(built["entries"]),
        "people": len(people),
        "men": sum(1 for p in people if p["gender"] == "男子"),
        "women": sum(1 for p in people if p["gender"] == "女子"),
        "prefs": len(have),
        "events": len(built["events"]),
        "done": len(RES["done"]),
    },
    "days": [
        {"day": 1, "date": "2026-09-10", "label": "9月10日（木）"},
        {"day": 2, "date": "2026-09-11", "label": "9月11日（金）"},
        {"day": 3, "date": "2026-09-12", "label": "9月12日（土）"},
    ],
    "events": built["events"],
    "entries": built["entries"],
    "people": people,
    "absent": [p for p in PREFS if p not in have],
    "yomi": kana["yomi"],
    "prefKana": kana["prefKana"],
}

HTML = r"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src https://abacus.jasoncameron.dev; img-src 'self' data:; base-uri 'none'; form-action 'none'">
<meta name="theme-color" content="#10182f">
<title>国スポ2026 飛込 エントリー・結果</title>
<style>
:root{
  --bg:#10182f;--panel:#182442;--panel2:#1d2b4d;--text:#f4f8ff;--muted:#aebbd5;--accent:#00c4ff;--gold:#ffd766;--line:#30436c;
  --male:#1565c0;--female:#b71c6e;--maleText:#6fb7ff;--femaleText:#ff92c2;
}
*{box-sizing:border-box}
/* display を持つクラス(.status は flex)が [hidden] に勝ってしまうので明示的に殺す */
[hidden]{display:none!important}
body{margin:0;background:linear-gradient(180deg,#10182f,#142040 54%,#10182f);color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Yu Gothic",sans-serif;min-height:100vh;-webkit-text-size-adjust:100%}
main{width:min(720px,100%);margin:auto;padding:calc(16px + env(safe-area-inset-top)) 16px 40px}
.eyebrow{color:var(--accent);font-size:11px;font-weight:800;letter-spacing:.12em}
h1{margin:6px 0 8px;font-size:clamp(20px,6vw,30px);line-height:1.25;letter-spacing:.01em}
.facts{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 4px;padding:0;list-style:none}
.facts li{background:#0d1730;border:1px solid var(--line);border-radius:999px;padding:6px 11px;font-size:12px;color:#dbe6fb}
.facts b{color:var(--accent)}

.hero{margin:16px 0 4px;padding:15px;border:1px solid #ffd76699;border-radius:18px;
  background:radial-gradient(circle at 100% 0,#33528a,#1a2b4e 62%);box-shadow:0 12px 32px #0004}
.hero h2{margin:0 0 5px;font-size:16px}
.hero p{margin:0;color:#dce8ff;font-size:12.5px;line-height:1.6}
.kago-grid{display:grid;gap:9px;margin-top:11px}
.kago{border-radius:13px;border:1px solid #ffd766a8;background:#16294a;padding:11px 12px;border-left-width:5px}
.kago small{display:block;color:var(--gold);font-weight:800;margin-bottom:3px;font-size:11px}
.kago strong{font-size:17px;letter-spacing:.03em}
.kago .sub{display:block;color:#d3ddf1;margin-top:3px;font-size:11.5px}
.kago .evs{margin-top:7px;display:grid;gap:4px}

.views{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin:16px 0 0}
.view{min-height:48px;border:1px solid #425884;border-radius:13px;background:#182442;color:#cfdbf0;
  font:800 14px inherit;cursor:pointer}
.view.on{background:var(--accent);border-color:var(--accent);color:#06172c}

.search{position:sticky;top:0;z-index:5;margin:12px -4px 0;padding:10px 4px 6px;background:#10182ff2;backdrop-filter:blur(12px)}
input{width:100%;border:1px solid #3a517f;border-radius:13px;background:#0d1730;color:var(--text);font:inherit;font-size:16px;padding:13px 14px;outline:0}
input:focus{border-color:var(--accent);box-shadow:0 0 0 3px #00c4ff2e}
.hint{margin:6px 2px 0;font-size:11px;color:var(--muted)}
.chips{display:flex;flex-wrap:wrap;gap:7px;padding:9px 0 3px}
.chip{flex:0 1 auto;min-height:48px;border:1px solid #425884;border-radius:999px;background:#182442;color:#cfdbf0;
  padding:0 14px;font:700 13px inherit;cursor:pointer;display:inline-flex;align-items:center;gap:5px}
.chip.active{color:#06172c;border-color:var(--accent);background:var(--accent)}
.chip.m.active{background:var(--maleText);border-color:var(--maleText)}
.chip.f.active{background:var(--femaleText);border-color:var(--femaleText)}
.chip.k{border-color:#e5bd48;color:#ffe79a}
.chip.k.active{background:var(--gold);color:#342900}

.status{display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin:14px 0 8px;font-size:12.5px;color:var(--muted)}
.status b{color:var(--text);font-size:15px}
.block{margin:18px 0 0}
.block:first-child{margin-top:0}
.bhead{display:flex;align-items:center;gap:8px;margin:0 0 9px;font-size:14px;font-weight:800;letter-spacing:.02em}
.bhead .bar{width:5px;height:19px;border-radius:3px;background:var(--male)}
.bhead.f .bar{background:var(--female)}
.bhead .n{margin-left:auto;font-weight:700;font-size:12px;color:var(--muted)}
.list{display:grid;gap:8px}

.card{border:1px solid var(--line);border-left:5px solid var(--male);border-radius:14px;
  background:linear-gradient(120deg,var(--panel),var(--panel2));padding:12px 13px;
  display:grid;grid-template-columns:1fr auto;gap:6px 10px}
.card.f{border-left-color:var(--female)}
.card.kago{border-color:var(--gold);border-left-color:var(--gold);background:linear-gradient(120deg,#263c60,#1d3159)}
.name{font-size:18px;font-weight:800;letter-spacing:.04em;line-height:1.3}
.meta{color:#c3d0e8;font-size:12.5px;margin-top:2px}
.tag{font-size:11px;font-weight:800;border-radius:999px;padding:5px 9px;height:max-content;white-space:nowrap}
.tag.m{background:#1565c033;color:var(--maleText);border:1px solid #1565c0aa}
.tag.f{background:#b71c6e33;color:var(--femaleText);border:1px solid #b71c6eaa}
.evlist{grid-column:1/-1;border-top:1px solid #ffffff17;padding-top:8px;display:grid;gap:5px}
.ev{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:12.5px;color:#dbe6fb}
.ev .ename{font-weight:800}
.ev .day{color:var(--muted);font-size:11.5px}
.ev .ord{margin-left:auto;font-weight:900;font-variant-numeric:tabular-nums;color:var(--gold);font-size:12.5px;white-space:nowrap}
.ev.wd .ename,.ev.wd .day{color:#8e9cb8;text-decoration:line-through}
.ev .wdtag{font-size:10.5px;font-weight:800;color:#ffb9c9;background:#5a1f31;border:1px solid #8c3a58;border-radius:999px;padding:3px 8px}

.day-h{display:flex;align-items:baseline;gap:9px;margin:22px 0 10px;font-size:15px;font-weight:800}
.day-h .dn{color:var(--accent);font-size:12px;letter-spacing:.1em}
.race{border:1px solid var(--line);border-radius:14px;background:#131f3b;overflow:hidden;margin-bottom:9px}
.race>summary{padding:13px 14px;cursor:pointer;min-height:48px;display:flex;align-items:center;gap:9px;
  border-left:5px solid var(--male);list-style:none;flex-wrap:wrap}
.race.f>summary{border-left-color:var(--female)}
.race>summary::-webkit-details-marker{display:none}
.race>summary::after{content:"▾";margin-left:auto;color:var(--muted);font-size:13px}
.race[open]>summary::after{content:"▴"}
.race .rt{font-weight:900;font-variant-numeric:tabular-nums;color:var(--gold);font-size:13.5px;min-width:44px}
.race .rn{font-weight:800;font-size:14px}
.race .rc{color:var(--muted);font-size:11.5px}
.rows{padding:2px 10px 10px}
.row{display:flex;align-items:center;gap:10px;padding:9px 6px;border-top:1px solid #ffffff12;font-size:13.5px}
.row .o{flex:0 0 auto;width:30px;height:30px;border-radius:9px;display:grid;place-items:center;
  background:#0d1730;border:1px solid var(--line);font-weight:900;font-size:13px;font-variant-numeric:tabular-nums}
.row .rnm{font-weight:800;letter-spacing:.03em}
.row .rp{color:#c3d0e8;font-size:11.5px;margin-top:1px}
.row.kago{background:#23375c;border-radius:10px;border-top-color:transparent}
.row.kago .o{background:var(--gold);color:#342900;border-color:var(--gold)}
.row.wd .rnm{color:#8e9cb8;text-decoration:line-through}
.row.wd .o{color:#8e9cb8}
.row .wdtag{margin-left:auto;font-size:10.5px;font-weight:800;color:#ffb9c9;background:#5a1f31;border:1px solid #8c3a58;border-radius:999px;padding:3px 8px}
/* 順位・得点（結果が出た競技） */
.ev .ord.p1{color:#ffe89a}.ev .ord.p2{color:#e6eefa}.ev .ord.p3{color:#f0c396}.ev .ord.win{color:#7ff0bd}
.row .o.rk{color:#eaf3ff}
.row .o.rk.p1{background:linear-gradient(150deg,#ffe89a,#e0a93a);color:#3a2a00;border-color:#ffd766}
.row .o.rk.p2{background:linear-gradient(150deg,#eaf0f8,#a9b7c9);color:#25303f;border-color:#dbe4f0}
.row .o.rk.p3{background:linear-gradient(150deg,#f0c396,#b9773c);color:#3a2208;border-color:#e8b183}
.row .o.rk.win{background:#123a2c;border-color:#2e7d59;color:#7ff0bd}
.row .o.wdo{color:var(--muted)}
.row .pts{margin-left:auto;text-align:right;font-variant-numeric:tabular-nums;font-weight:800;font-size:13px;color:#eaf3ff;white-space:nowrap}
.row .pts b{display:block;font-size:10px;font-weight:800;color:#7ff0bd}
.race .rc .fin{color:#7ff0bd;font-weight:800}
.empty{padding:28px 10px;text-align:center;color:var(--muted)}

details.box{margin-top:20px;border:1px solid var(--line);border-radius:14px;background:#131f3b;overflow:hidden}
details.box>summary{padding:14px;font-weight:800;font-size:13.5px;cursor:pointer;min-height:48px;display:flex;align-items:center;gap:8px}
details.box>summary::-webkit-details-marker{display:none}
details.box>summary::after{content:"▾";margin-left:auto;color:var(--muted)}
details.box[open]>summary::after{content:"▴"}
.dbody{padding:0 14px 14px;font-size:12.5px;line-height:1.75;color:#d3ddf1}
.info dt{font-weight:800;color:var(--accent);font-size:12px;margin-top:10px}
.info dt:first-child{margin-top:0}
.info dd{margin:2px 0 0;color:#d8e3f7}
.warn{margin-top:12px;padding:11px 12px;border-radius:11px;background:#3a1f2c;border:1px solid #8c3a58;color:#ffd7e4;font-size:12px;line-height:1.65}
.viewCounter{display:inline-flex;align-items:center;gap:6px;margin-top:16px;padding:5px 12px;background:#0b1222;border:1px solid var(--line);border-radius:999px;font-size:12px;color:var(--muted)}
.viewCounter strong{color:var(--accent);font-size:14px}
footer{margin-top:22px;padding-top:14px;border-top:1px solid var(--line);color:var(--muted);font-size:11px;line-height:1.7}
a{color:var(--accent)}
@media(max-width:400px){ .chip{padding:0 12px;font-size:12px} }
@media(max-width:360px){
  main{padding-left:12px;padding-right:12px}
  h1{font-size:19px}
  .name{font-size:17px}
  .race>summary{gap:7px}
  .race .rn{font-size:13px}
}
</style>
</head>
<body>
<main>
  <div class="eyebrow">KOKUSPO 2026 · DIVING</div>
  <h1>国スポ 飛込<br>エントリー・結果</h1>
  <ul class="facts">
    <li><b>9月10日</b>〜<b>12日</b></li>
    <li>全<b>8種目</b></li>
    <li><b id="fPeople">0</b>名</li>
    <li>宮城・利府</li>
  </ul>

  <section class="hero">
    <h2>🔥 鹿児島県の選手</h2>
    <p>一覧でも金色で目立つように表示しています。</p>
    <div class="kago-grid" id="kagoGrid"></div>
  </section>

  <div class="views" role="tablist">
    <button class="view on" data-v="people" role="tab">👤 選手でさがす</button>
    <button class="view" data-v="schedule" role="tab">📅 日程・飛順</button>
  </div>

  <section class="search" id="searchBox">
    <input id="q" type="search" autocomplete="off" placeholder="選手名・都道府県で検索" aria-label="選手名・都道府県で検索">
    <p class="hint">ひらがなでも探せます（3文字以上）。「くぼ」「かごしま」など。</p>
    <div class="chips" role="group" aria-label="絞り込み">
      <button class="chip active" data-f="all">全員</button>
      <button class="chip m" data-f="男子">🔵 男子</button>
      <button class="chip f" data-f="女子">🔴 女子</button>
      <button class="chip" data-f="少年">少年</button>
      <button class="chip" data-f="成年">成年</button>
      <button class="chip k" data-f="kago">🔥 鹿児島</button>
    </div>
  </section>

  <div class="status" id="statusBar"><span><b id="count">0</b> 名を表示</span><span id="hint2"></span></div>
  <div id="out" aria-live="polite"></div>
  <div id="sched" hidden></div>

  <details class="box" id="absentBox">
    <summary>🚫 出場者がいない都道府県</summary>
    <div class="dbody" id="absentBody"></div>
  </details>

  <details class="box">
    <summary>ℹ️ 大会情報</summary>
    <div class="dbody">
      <dl class="info">
        <dt>期日</dt><dd>2026年9月10日（木）・11日（金）・12日（土）</dd>
        <dt>会場</dt><dd>セントラルスポーツ宮城Ｇ21プール（宮城県宮城郡利府町菅谷字舘40-1）</dd>
        <dt>競技方法</dt><dd>各種目とも決勝競技のみ。都道府県対抗。</dd>
        <dt>種目</dt><dd>成年男子・成年女子・少年男子・少年女子の各 飛板飛込／高飛込（計8種目）</dd>
        <dt>出場枠</dt><dd>各都道府県は各種目1名。選手1人あたり2種目まで。1県あたり選手4名以内。</dd>
        <dt>演技数</dt><dd>成年男子 6演技／成年女子・少年男子 5演技／少年女子 4演技（いずれも自由選択飛）</dd>
        <dt>年齢</dt><dd>成年 2008年4月1日以前生まれ／少年 2008年4月2日〜2012年4月1日生まれ</dd>
        <dt>表彰</dt><dd>各種目 第1位から第8位までに賞状。1位8点〜8位1点の競技得点。</dd>
      </dl>
      <div class="warn">
        このページは個人が作った確認用の非公式ページです。飛順や出場者は変更されることがあります。
        最終的な内容は必ず大会の公式発表をご確認ください。
      </div>
    </div>
  </details>

  <div class="viewCounter" id="viewCounter" hidden>👀 のべ閲覧 <strong id="viewCount">-</strong> 回</div>
  <footer>
    個人が作った確認補助用のページです。内容の正確性は保証しません。
  </footer>
</main>

<script id="app-data" type="application/json">__DATA__</script>
<script>
(function(){
const D = JSON.parse(document.getElementById('app-data').textContent);
const YOMI = D.yomi, PK = D.prefKana;
const EV = new Map(D.events.map(e => [e.no, e]));

/* ---------- 文字ゆらぎ（異体字は正字に寄せる。表示は公式のまま） ---------- */
const ITAIJI = {'髙':'高','﨑':'崎','濵':'浜','濱':'浜','栁':'柳','𠮷':'吉','邊':'辺','邉':'辺','眞':'真',
                '齋':'斎','齊':'斉','澤':'沢','嶋':'島','廣':'広','冨':'富','凜':'凛'};
const kanaToHira = v => String(v||'').replace(/[ァ-ヶ]/g, c => String.fromCharCode(c.charCodeAt(0)-0x60));
const fold = v => String(v||'').replace(/./gu, c => ITAIJI[c] || c);
const normalize = v => fold(kanaToHira(String(v||'').normalize('NFKC').toLowerCase())).replace(/[\s　・･\.\-ー,，、。]/g,'');
const safe = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

/* ---------- ひらがな検索（読みは画面に出さない） ---------- */
const isHiraQuery = v => /^[ぁ-ゖ]{3,}$/.test(v);
const readingsOf = text => {
  const out = []; let prev = '';
  for (const ch of text) {
    if (ch === '々' && prev) out.push(YOMI[prev] || []);
    else if (ch >= 'ぁ' && ch <= 'ゖ') out.push([ch]);
    else out.push(YOMI[ch] || []);
    prev = ch;
  }
  return out;
};
function kanaScan(text, query){
  const name = normalize(text);
  if (!name || !query) return -1;
  const readings = readingsOf(name);
  const seen = new Map();
  const walk = (index, position) => {
    if (position >= query.length) return 2;
    if (index >= name.length) return 0;
    const key = index + ':' + position;
    if (seen.has(key)) return seen.get(key);
    seen.set(key, 0);
    let best = 0;
    const rest = query.slice(position);
    for (const reading of readings[index]) {
      if (reading.startsWith(rest)) best = Math.max(best, 1);
      if (rest.startsWith(reading)) {
        const next = position + reading.length;
        best = Math.max(best, walk(index+1, next));
        if ('のがつっ'.includes(query[next] || '') && next + 1 < query.length) best = Math.max(best, walk(index+1, next+1));
      }
      if (best === 2) break;
    }
    seen.set(key, best);
    return best;
  };
  let best = -1;
  for (let start = 0; start < name.length; start += 1) {
    seen.clear();
    const score = walk(start, 0);
    if (!score) continue;
    if (start === 0) return score === 2 ? 3 : 2;
    best = Math.max(best, 1);
  }
  return best;
}
function hit(a, raw){
  const q = normalize(raw);
  if (!q) return true;
  const pk = PK[a.pref] || '';
  if (normalize(a.name).includes(q) || normalize(a.pref).includes(q) || pk.includes(q)) return true;
  if (a.kana && normalize(a.kana).includes(q)) return true;   // 公式ふりがな
  if (!isHiraQuery(q)) return false;
  return kanaScan(a.name, q) >= 0;                            // 読み候補から推定
}

/* ---------- 表示の小道具 ---------- */
const gCls = g => g === '男子' ? 'm' : 'f';
const gMark = g => g === '男子' ? '🔵' : '🔴';
const isKago = a => a.pref === '鹿児島県';
const evName = e => e.event;
const dayOf = e => e.day + '日目';
const medal = r => r === 1 ? ' p1' : r === 2 ? ' p2' : r === 3 ? ' p3' : r <= 8 ? ' win' : '';
const evLine = (ref) => {
  const e = EV.get(ref.ev);
  const r = ref.r;
  let tail;
  if (r && r.st) tail = `<span class="wdtag">${safe(r.st)}</span>`;
  else if (r) tail = `<span class="ord${medal(r.rank)}">${r.rank}位　${r.pts.toFixed(2)}</span>`;
  else if (ref.wd) tail = '<span class="wdtag">棄権</span>';
  else tail = `<span class="ord">飛順 ${ref.order}</span>`;
  return `<div class="ev${(r && r.st) || (ref.wd && !r) ? ' wd' : ''}">
    <span class="ename">${safe(evName(e))}</span>
    <span class="day">${dayOf(e)}${e.start ? ' ' + safe(e.start) : ''}</span>
    ${tail}
  </div>`;
};

/* ---------- 鹿児島 ---------- */
document.getElementById('fPeople').textContent = D.stats.people;
const kago = D.people.filter(isKago);
document.getElementById('kagoGrid').innerHTML = kago.map(a => `
  <div class="kago"><small>${gMark(a.gender)} ${safe(a.cat)}${safe(a.gender)}</small>
    <strong>${safe(a.name)}</strong>
    <span class="sub">${safe(a.pref)}${a.grade ? ' · ' + safe(a.grade) : ''}</span>
    <div class="evs">${a.evs.map(evLine).join('')}</div>
  </div>`).join('') || '<div class="kago"><span class="sub">鹿児島県の出場者はいません。</span></div>';

/* ---------- 出場者がいない都道府県 ---------- */
document.getElementById('absentBody').innerHTML =
  `<p style="margin:0 0 6px">${D.absent.map(safe).join('・')}</p>
   <p style="margin:0;color:#aebbd5;font-size:11.5px">47都道府県のうち ${D.stats.prefs} 県から出場しています。</p>`;
document.getElementById('absentBox').querySelector('summary').textContent =
  `🚫 出場者がいない都道府県（${D.absent.length}）`;

/* ---------- 選手ビュー ---------- */
const q = document.getElementById('q'), out = document.getElementById('out'),
      count = document.getElementById('count'), hint2 = document.getElementById('hint2');
let filter = 'all', view = 'people';

function card(a){
  return `<article class="card ${gCls(a.gender)}${isKago(a) ? ' kago' : ''}">
    <div>
      <div class="name">${isKago(a) ? '🔥 ' : ''}${safe(a.name)}</div>
      <div class="meta">${safe(a.pref)}${a.grade ? ' · ' + safe(a.grade) : ''} · ${safe(a.cat)}</div>
    </div>
    <span class="tag ${gCls(a.gender)}">${gMark(a.gender)} ${safe(a.gender)}</span>
    <div class="evlist">${a.evs.map(evLine).join('')}</div>
  </article>`;
}
function renderPeople(){
  const raw = q.value;
  const found = D.people.filter(a => {
    if (filter === 'kago') { if (!isKago(a)) return false; }
    else if (filter === '男子' || filter === '女子') { if (a.gender !== filter) return false; }
    else if (filter === '少年' || filter === '成年') { if (a.cat !== filter) return false; }
    return hit(a, raw);
  });
  count.textContent = found.length;
  hint2.textContent = filter === 'kago' ? '鹿児島県' : filter === 'all' ? '男女別' : filter;
  if (!found.length){ out.innerHTML = '<div class="empty">見つかりませんでした。<br>漢字でも、ひらがな3文字以上でも探せます。</div>'; return; }
  out.innerHTML = ['男子','女子'].map(g => {
    const rows = found.filter(a => a.gender === g)
      .sort((x,y) => (x.cat === y.cat ? PREF_ORDER(x.pref) - PREF_ORDER(y.pref) : (x.cat === '成年' ? -1 : 1)));
    if (!rows.length) return '';
    return `<section class="block"><h2 class="bhead ${gCls(g)}"><span class="bar"></span>${gMark(g)} ${g}<span class="n">${rows.length}名</span></h2>
      <div class="list">${rows.map(card).join('')}</div></section>`;
  }).join('');
}
const PREF_LIST = Object.keys(PK);
const PREF_ORDER = p => { const i = PREF_LIST.indexOf(p); return i < 0 ? 99 : i; };

/* ---------- 日程ビュー ---------- */
const entriesOf = no => D.entries.filter(e => e.ev === no).sort((a,b) => {
  const ra = a.r && a.r.rank, rb = b.r && b.r.rank;
  if (ra && rb) return ra - rb;
  if (ra) return -1;
  if (rb) return 1;
  if (a.r && a.r.st && !(b.r && b.r.st)) return 1;
  if (b.r && b.r.st && !(a.r && a.r.st)) return -1;
  return a.order - b.order;
});
function renderSchedule(){
  document.getElementById('sched').innerHTML = D.days.map(d => {
    const races = D.events.filter(e => e.day === d.day);
    return `<div class="day-h"><span class="dn">${d.day}日目</span>${safe(d.label)}</div>` +
      races.map(e => {
        const rows = entriesOf(e.no).map(r => {
          const res = r.r;
          const badge = res && res.rank ? `<span class="o rk${medal(res.rank)}">${res.rank}</span>`
                      : res && res.st ? '<span class="o wdo">ー</span>'
                      : `<span class="o">${r.order}</span>`;
          const right = res && res.rank
              ? `<span class="pts">${res.pts.toFixed(2)}${res.rank <= 8 ? '<b>入賞</b>' : ''}</span>`
              : res && res.st ? `<span class="wdtag">${safe(res.st)}</span>`
              : r.wd ? '<span class="wdtag">棄権</span>' : '';
          return `<div class="row${r.pref === '鹿児島県' ? ' kago' : ''}${(res && res.st) || (r.wd && !res) ? ' wd' : ''}">
            ${badge}
            <div><div class="rnm">${r.pref === '鹿児島県' ? '🔥 ' : ''}${safe(r.name)}</div>
              <div class="rp">${safe(r.pref)}${r.grade ? ' · ' + safe(r.grade) : ''}${res && res.rank ? ' · 飛順' + r.order : ''}</div></div>
            ${right}
          </div>`;
        }).join('');
        return `<details class="race ${gCls(e.gender)}">
          <summary>
            ${e.start ? `<span class="rt">${safe(e.start)}</span>` : ''}
            <span class="rn">${gMark(e.gender)} ${safe(e.cat)}${safe(e.gender)} ${safe(e.event)}</span>
            <span class="rc">${e.n}名${e.wd ? '（棄権' + e.wd + '）' : ''}${e.done ? ' <b class="fin">結果</b>' : ''}</span>
          </summary>
          <div class="rows">${rows}</div>
        </details>`;
      }).join('');
  }).join('');
}

/* ---------- ビュー切替 ---------- */
function setView(v){
  view = v;
  document.querySelectorAll('.view').forEach(b => b.classList.toggle('on', b.dataset.v === v));
  const isPeople = v === 'people';
  document.getElementById('searchBox').hidden = !isPeople;
  document.getElementById('statusBar').hidden = !isPeople;
  out.hidden = !isPeople;
  document.getElementById('sched').hidden = isPeople;
}
document.querySelectorAll('.view').forEach(b => b.addEventListener('click', () => setView(b.dataset.v)));
q.addEventListener('input', renderPeople);
document.querySelectorAll('.chip').forEach(b => b.addEventListener('click', () => {
  filter = b.dataset.f;
  document.querySelectorAll('.chip').forEach(x => x.classList.toggle('active', x === b));
  renderPeople();
}));
renderPeople();
renderSchedule();
setView('people');
})();
</script>
<script>
// 閲覧カウンター: Abacus(無料API)に累計値を保存。1日1回だけ加算し、失敗時は非表示のまま。
(function(){
  const NS="gyojin600m1-kokusupo-2026-dive-entry";
  const isLocal=location.protocol==="file:"||/^(localhost|127\.|0\.0\.0\.0)/.test(location.hostname)||location.hostname==="";
  const KEY=isLocal?"views-dev":"views";
  const d=new Date();
  const today=d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0");
  const stampKey="viewCounterStamp:"+NS+":"+KEY;
  let counted=false;
  try{counted=localStorage.getItem(stampKey)===today;}catch(e){}
  fetch("https://abacus.jasoncameron.dev/"+(counted?"get":"hit")+"/"+NS+"/"+KEY)
    .then(r=>{if(!r.ok)throw new Error();return r.json();})
    .then(data=>{
      if(typeof data.value!=="number")throw new Error();
      document.getElementById("viewCount").textContent=data.value.toLocaleString("ja-JP");
      document.getElementById("viewCounter").hidden=false;
      if(!counted){try{localStorage.setItem(stampKey,today);}catch(e){}}
    })
    .catch(()=>{});
})();
</script>
</body>
</html>
"""

out = Path("index.html")
out.write_text(HTML.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":"))),
               encoding="utf-8")
print("→", out.resolve(), out.stat().st_size, "bytes")
print("選手", data["stats"]["people"], "／エントリー", data["stats"]["entries"],
      "／県", data["stats"]["prefs"], "／出場なし", len(data["absent"]))
