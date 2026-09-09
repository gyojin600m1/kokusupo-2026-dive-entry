# -*- coding: utf-8 -*-
"""国スポ2026 飛込 エントリー確認アプリ データ構築 + 検算
  ・組合せ表PDF(CID埋め込み→ページ画像から判読)を人手で起こしたものが RAW
  ・SEIKO公式スタートリスト(1日目3競技)と自動突合して転記ミスを検出する
"""
import json, re, unicodedata
import pdfplumber

# 競技 = (No, 日, 日付, 曜日, 種別, 性別, 種目, 開始時刻)
EVENTS = [
    (1, 1, "2026-09-10", "木", "少年", "女子", "高飛込",   "10:00"),
    (2, 1, "2026-09-10", "木", "少年", "男子", "飛板飛込", "12:30"),
    (3, 1, "2026-09-10", "木", "成年", "女子", "高飛込",   "15:00"),
    (4, 2, "2026-09-11", "金", "少年", "女子", "飛板飛込", None),
    (5, 2, "2026-09-11", "金", "少年", "男子", "高飛込",   None),
    (6, 2, "2026-09-11", "金", "成年", "男子", "飛板飛込", None),
    (7, 3, "2026-09-12", "土", "成年", "女子", "飛板飛込", None),
    (8, 3, "2026-09-12", "土", "成年", "男子", "高飛込",   None),
]

# 飛順: (氏名, 都道府県, 学年)  学年空欄は None
RAW = {
1: [("荒木 花音","茨城県","高3"),("鈴木 静玖","千葉県","高3"),("杉本 絢菜","山形県","高1"),
    ("千葉 優奈","福島県","高1"),("山口 真菜","奈良県","高1"),("植田 恵麻","香川県","中3"),
    ("野坂 律季","鳥取県","中3"),("山本 彩華","広島県","中3"),("豊田 宙未","埼玉県","高2"),
    ("山田 比歩未","東京都","高1"),("長岡 凜","群馬県","高3"),("八木 星輝","神奈川県","高2"),
    ("井上 優奈","高知県","高1")],
2: [("佐藤 海志","長野県","高1"),("後藤 大輝","京都府","高3"),("久保 彪","鹿児島県","高3"),
    ("中山 一颯","石川県","高1"),("二階堂 律","高知県","高1"),("和田 颯仁","和歌山県","中3"),
    ("金箱 琉海","愛知県","高2"),("廣冨 諒","島根県","高2"),("伴 和真","岡山県","高3"),
    ("猿田 煌大","神奈川県","高3"),("古戎 徠人","広島県","中3"),("北村 応吏","佐賀県","高1"),
    ("石沢 遥斗","新潟県","高3"),("茶木 琉聖","大分県","高1")],
3: [("跡邊 あずき","福岡県","大1"),("近藤 花菜","群馬県",None),("青山 由唯加","静岡県","大4"),
    ("森淵 茉莉愛","広島県",None),("坂田 丹寧","茨城県","大2"),("西沢 明歩","福島県",None),
    ("乗松 飛羽","愛媛県","大3"),("山崎 佳蓮","高知県","大4"),("金戸 凜","東京都",None),
    ("荒井 祭里","佐賀県",None)],
4: [("杉本 絢菜","山形県","高1"),("千葉 優奈","福島県","高1"),("豊田 宙未","埼玉県","高2"),
    ("山口 真菜","奈良県","高1"),("荒木 花音","茨城県","高3"),("山本 彩華","広島県","中3"),
    ("鈴木 静玖","千葉県","高3"),("近藤 和","東京都","中3"),("植田 恵麻","香川県","中3"),
    ("赤木 陽音","鳥取県","高2"),("長岡 凜","群馬県","高3"),("八木 星輝","神奈川県","高2"),
    ("井上 優奈","高知県","高1")],
5: [("大島 幹央","福島県","高3"),("後藤 大輝","京都府","高3"),("和田 颯仁","和歌山県","中3"),
    ("中山 一颯","石川県","高1"),("久保 彪","鹿児島県","高3"),("佐藤 海志","長野県","高1"),
    ("金箱 琉海","愛知県","高2"),("廣冨 諒","島根県","高2"),("猿田 煌大","神奈川県","高3"),
    ("古戎 徠人","広島県","中3"),("二階堂 律","高知県","高1"),("茶木 琉聖","大分県","高1"),
    ("北村 応吏","佐賀県","高1"),("石沢 遥斗","新潟県","高3")],
6: [("坂田 力毅","富山県","大1"),("佐々木 康平","宮城県",None),("古谷 英成","栃木県","大1"),
    ("池辺 寛人","大分県","大2"),("荒木 宥図","新潟県",None),("伊熊 扇李","兵庫県","大4"),
    ("山田 周汰","静岡県",None),("金戸 快","東京都",None),("西田 玲雄","大阪府",None),
    ("片岡 三亮","愛知県","大1"),("坂田 慈央","長野県",None),("瓶子 礼智","高知県","大2"),
    ("坂田 麗鳳","宮崎県",None),("伊藤 洸輝","滋賀県",None),("二羽 倖駕","石川県","大3"),
    ("須山 晴貴","島根県",None),("坂井 丞","神奈川県",None)],
7: [("跡邊 あずき","福岡県","大1"),("山口 歩夏","三重県","大4"),("青山 由唯加","静岡県","大4"),
    ("森淵 茉莉愛","広島県",None),("坂田 丹寧","茨城県","大2"),("西沢 明歩","福島県",None),
    ("山崎 佳蓮","高知県","大4"),("荒井 祭里","佐賀県",None),("近藤 花菜","群馬県",None),
    ("乗松 飛羽","愛媛県","大3"),("榎本 遼香","栃木県",None),("三上 紗也可","鳥取県",None)],
8: [("松原 旭稀","岩手県","大2"),("坂之上 卓","鹿児島県",None),("古谷 英成","栃木県","大1"),
    ("坂田 力毅","富山県","大1"),("池辺 寛人","大分県","大2"),("片岡 三亮","愛知県","大1"),
    ("瓶子 礼智","高知県","大2"),("坂田 麗鳳","宮崎県",None),("坂田 慈央","長野県",None),
    ("大久保 柊","茨城県",None),("二羽 倖駕","石川県","大3"),("山田 周汰","静岡県",None),
    ("金戸 快","東京都",None),("西田 玲雄","大阪府",None),("玉井 陸斗","兵庫県","大2")],
}

# 公式スタートリストPDF(1日目のみ公開済み)
STARTLISTS = {1: "sl_001_wm_pf_fnl_Girls.pdf", 2: "sl_002_mn_3msb_fnl_Boys.pdf",
              3: "sl_003_wm_pf_fnl_Women.pdf"}

PREFS = ["北海道","青森県","岩手県","宮城県","秋田県","山形県","福島県","茨城県","栃木県","群馬県",
         "埼玉県","千葉県","東京都","神奈川県","新潟県","富山県","石川県","福井県","山梨県","長野県",
         "岐阜県","静岡県","愛知県","三重県","滋賀県","京都府","大阪府","兵庫県","奈良県","和歌山県",
         "鳥取県","島根県","岡山県","広島県","山口県","徳島県","香川県","愛媛県","高知県","福岡県",
         "佐賀県","長崎県","熊本県","大分県","宮崎県","鹿児島県","沖縄県"]

def han2hira(s):
    """半角カナ(公式ふりがな) → ひらがな"""
    s = unicodedata.normalize("NFKC", s)
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)

def parse_startlist(path):
    """公式スタートリストから 演技順・氏名・ふりがな・都道府県・棄権・開始時刻 を取る"""
    rows, start = [], None
    with pdfplumber.open(path) as pdf:
        text = "\n".join((p.extract_text() or "") for p in pdf.pages)
    m = re.search(r"開始時間\s*(\d+)[：:](\d+)", text)
    if m:
        start = f"{int(m.group(1))}:{m.group(2)}"
    lines = [l.strip() for l in text.split("\n")]
    i = 0
    while i < len(lines):
        m = re.match(r"^(\d+|棄権)\s+([^\d]+?)(?:\s+\d{3,4}\s|$)", lines[i])
        if m and i + 2 < len(lines):
            kana_line, pref_line = lines[i + 1], lines[i + 2]
            km = re.match(r"^([ｦ-ﾟ\s]+)", kana_line)
            pm = pref_line.strip()
            if km and pm in PREFS:
                rows.append({"order": None if m.group(1) == "棄権" else int(m.group(1)),
                             "withdrawn": m.group(1) == "棄権",
                             "name": re.sub(r"\s+", " ", m.group(2)).strip(),
                             "kana": han2hira(km.group(1).strip()),
                             "pref": pm})
                i += 3
                continue
        i += 1
    return start, rows

# ---------- 1日目3競技を公式スタートリストと突合 ----------
print("── 公式スタートリストとの突合（1日目・3競技） ──")
official_kana, withdrawn, problems = {}, set(), []
for no, path in STARTLISTS.items():
    start, rows = parse_startlist(path)
    ev = next(e for e in EVENTS if e[0] == no)
    if start != ev[7]:
        problems.append(f"競技{no}: 開始時刻 表={ev[7]} 公式={start}")
    if len(rows) != len(RAW[no]):
        problems.append(f"競技{no}: 人数 表={len(RAW[no])} 公式={len(rows)}")
    seq = 0
    for r in rows:
        # 公式の並び順 = 飛順（棄権者もその位置に残る）
        mine = RAW[no][seq]
        seq += 1
        if r["name"].replace(" ", "") != mine[0].replace(" ", ""):
            problems.append(f"競技{no} 飛順{seq}: 氏名 表={mine[0]} 公式={r['name']}")
        if r["pref"] != mine[1]:
            problems.append(f"競技{no} 飛順{seq}: 県 表={mine[1]} 公式={r['pref']}")
        official_kana[(r["name"].replace(" ", ""), r["pref"])] = r["kana"]
        if r["withdrawn"]:
            withdrawn.add((no, seq))
    print(f"  競技{no} {ev[4]}{ev[5]} {ev[6]}: {len(rows)}名 照合 / 開始{start} / 棄権{sum(1 for r in rows if r['withdrawn'])}名")
for p in problems:
    print("  ⚠", p)
if not problems:
    print("  ✓ 1日目の氏名・都道府県・人数・開始時刻すべて公式と一致")

# ---------- 組み立て ----------
events, entries, people = [], [], {}
for (no, day, date, dow, cat, gender, event, start) in EVENTS:
    rows = RAW[no]
    for idx, (name, pref, grade) in enumerate(rows, 1):
        key = (name.replace(" ", ""), pref)
        kana = official_kana.get(key)
        wd = (no, idx) in withdrawn
        entries.append({"ev": no, "order": idx, "name": name, "pref": pref,
                        "grade": grade, "wd": wd})
        p = people.setdefault(key, {"name": name, "pref": pref, "grade": grade,
                                    "gender": gender, "cat": cat, "kana": kana, "evs": []})
        if kana and not p["kana"]:
            p["kana"] = kana
        if grade and not p["grade"]:
            p["grade"] = grade
        p["evs"].append({"ev": no, "order": idx, "wd": wd})
    events.append({"no": no, "day": day, "date": date, "dow": dow, "cat": cat,
                   "gender": gender, "event": event, "start": start,
                   "n": len(rows), "wd": sum(1 for i in range(1, len(rows) + 1) if (no, i) in withdrawn)})

# ---------- 検算 ----------
print("\n── 検算 ──")
tot = sum(len(v) for v in RAW.values())
print(f"  競技数        {len(EVENTS)}   （要項の種目数 8 と一致）" )
print(f"  エントリー件数 {tot}")
print(f"  選手（実人数） {len(people)}")
print(f"  都道府県       {len(set(p['pref'] for p in people.values()))}")
ng = 0
# 規定1: 各都道府県の参加は各種目1名
for no, rows in RAW.items():
    prefs = [r[1] for r in rows]
    dup = {p for p in prefs if prefs.count(p) > 1}
    if dup:
        print(f"  ⚠ 競技{no} に同一県が複数: {dup}"); ng += 1
# 規定2: 選手1人2種目まで
over = {k: len(v["evs"]) for k, v in people.items() if len(v["evs"]) > 2}
if over:
    print(f"  ⚠ 3種目以上の選手: {over}"); ng += 1
# 規定3: 各都道府県 選手4名以内
by_pref = {}
for k, v in people.items():
    by_pref.setdefault(v["pref"], []).append(v["name"])
over_p = {p: n for p, n in by_pref.items() if len(n) > 4}
if over_p:
    print(f"  ⚠ 選手5名以上の県: {over_p}"); ng += 1
# 規定4: 種別と性別が競技と一致
for e in entries:
    ev = next(x for x in EVENTS if x[0] == e["ev"])
    pp = people[(e["name"].replace(" ", ""), e["pref"])]
    if pp["gender"] != ev[5] or pp["cat"] != ev[4]:
        print(f"  ⚠ 種別/性別 不一致: {e['name']}"); ng += 1
if not ng:
    print("  ✓ 要項の規定（各種目1県1名・1人2種目まで・1県4名以内・種別整合）すべて満たす")

print(f"\n  1種目のみ {sum(1 for v in people.values() if len(v['evs'])==1)}名 / "
      f"2種目 {sum(1 for v in people.values() if len(v['evs'])==2)}名")
print(f"  男子 {sum(1 for v in people.values() if v['gender']=='男子')}名 / "
      f"女子 {sum(1 for v in people.values() if v['gender']=='女子')}名")
print(f"  少年 {sum(1 for v in people.values() if v['cat']=='少年')}名 / "
      f"成年 {sum(1 for v in people.values() if v['cat']=='成年')}名")
print(f"  公式ふりがなあり {sum(1 for v in people.values() if v['kana'])}名 / "
      f"なし {sum(1 for v in people.values() if not v['kana'])}名")
kago = [v for v in people.values() if v["pref"] == "鹿児島県"]
print(f"  鹿児島県 {len(kago)}名: " + " / ".join(f"{v['name']}({len(v['evs'])}種目)" for v in kago))

json.dump({"events": events, "entries": entries,
           "people": [dict(v, key=f"{k[0]}|{k[1]}") for k, v in people.items()]},
          open("dive_built.json", "w"), ensure_ascii=False, indent=1)
print("\n  → dive_built.json")
