# -*- coding: utf-8 -*-
"""公式の順位一覧PDFを取り込んで results.json を作る。
未作成の競技はプレースホルダ(約8.5KB)なので飛ばす。取れた分だけ書き出す。"""
import json, re, sys, urllib.request
from pathlib import Path
import pdfplumber

BASE = "https://swim.seiko.co.jp/diving/2026/07/jp/pdf"
FILES = {1:"001_wm_pf_fnl_Girls", 2:"002_mn_3msb_fnl_Boys", 3:"003_wm_pf_fnl_Women",
         4:"004_wm_3msb_fnl_Girls", 5:"005_mn_pf_fnl_Boys", 6:"006_mn_3msb_fnl_Men",
         7:"007_wm_3msb_fnl_Women", 8:"008_mn_pf_fnl_Men"}
ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools" / "_pdf"; CACHE.mkdir(exist_ok=True)
PLACEHOLDER = 12000  # これ未満は「まだ作成されていません」のPDF

PREFS = ["北海道","青森県","岩手県","宮城県","秋田県","山形県","福島県","茨城県","栃木県","群馬県",
         "埼玉県","千葉県","東京都","神奈川県","新潟県","富山県","石川県","福井県","山梨県","長野県",
         "岐阜県","静岡県","愛知県","三重県","滋賀県","京都府","大阪府","兵庫県","奈良県","和歌山県",
         "鳥取県","島根県","岡山県","広島県","山口県","徳島県","香川県","愛媛県","高知県","福岡県",
         "佐賀県","長崎県","熊本県","大分県","宮崎県","鹿児島県","沖縄県"]
PREF_RE = "|".join(PREFS)
ROW = re.compile(r"^(\d+|棄権|失格)\s+(.+?)\s+([ｦ-ﾟ][ｦ-ﾟ\s]*?)\s+(" + PREF_RE + r")\s*([\d.\s]*)$")

def fetch(no):
    url = f"{BASE}/{FILES[no]}_02ranking.pdf"
    p = CACHE / f"{FILES[no]}_02ranking.pdf"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=30).read()
    except Exception as e:
        print(f"  競技{no}: 取得できず {e}"); return None
    p.write_bytes(data)
    if len(data) < PLACEHOLDER:
        return None            # まだ出ていない
    return p

def parse(path):
    with pdfplumber.open(path) as pdf:
        text = "\n".join((pg.extract_text() or "") for pg in pdf.pages)
    start = re.search(r"開始時間\s*(\d+)[：:](\d+)", text)
    rows = []
    for line in text.split("\n"):
        m = ROW.match(line.strip())
        if not m:
            continue
        rank, name, kana, pref, nums = m.groups()
        pts = re.findall(r"\d+\.\d+", nums or "")
        rows.append({"rank": None if rank in ("棄権", "失格") else int(rank),
                     "status": rank if rank in ("棄権", "失格") else None,
                     "name": re.sub(r"\s+", " ", name).strip(),
                     "pref": pref,
                     "points": float(pts[-1]) if pts else None})
    return (f"{int(start.group(1))}:{start.group(2)}" if start else None), rows

def main():
    built = json.loads((ROOT / "tools" / "dive_built.json").read_text(encoding="utf-8"))
    entry_key = {(e["name"].replace(" ", ""), e["pref"]): e for e in built["entries"] if True}
    by_ev = {}
    for e in built["entries"]:
        by_ev.setdefault(e["ev"], set()).add((e["name"].replace(" ", ""), e["pref"]))

    results, problems, done = {}, [], []
    for no in FILES:
        path = fetch(no)
        if not path:
            print(f"  競技{no}: 結果まだ"); continue
        start, rows = parse(path)
        if not rows:
            problems.append(f"競技{no}: 行が取れない"); continue
        seen = set()
        for r in rows:
            k = (r["name"].replace(" ", ""), r["pref"])
            if k not in by_ev.get(no, set()):
                problems.append(f"競技{no}: エントリーに無い {r['name']}({r['pref']})")
            seen.add(k)
        missing = by_ev.get(no, set()) - seen
        if missing:
            problems.append(f"競技{no}: 結果に出てこない {missing}")
        ranks = sorted(r["rank"] for r in rows if r["rank"])
        if ranks and ranks[0] != 1:
            problems.append(f"競技{no}: 1位が無い")
        pts = [r["points"] for r in rows if r["rank"]]
        if pts != sorted(pts, reverse=True):
            problems.append(f"競技{no}: 得点が順位の順に並んでいない")
        results[str(no)] = {"start": start, "rows": rows}
        done.append(no)
        print(f"  競技{no}: {len(rows)}行 取り込み（1位 {rows[0]['name']} / 棄権 "
              f"{sum(1 for r in rows if r['status'])}）")

    for p in problems:
        print("  ⚠", p)
    if problems:
        sys.exit("検算に落ちたので書き出さない")
    (ROOT / "tools" / "results.json").write_text(
        json.dumps({"results": results, "done": done}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"→ results.json（{len(done)}/8競技）")

if __name__ == "__main__":
    main()
