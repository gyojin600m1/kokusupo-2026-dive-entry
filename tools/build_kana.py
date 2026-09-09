# -*- coding: utf-8 -*-
"""ひらがな検索用の読み候補（公式ふりがなが無い選手向け）。KANJIDIC2の音・訓・名乗りから。"""
import gzip, json, re, xml.etree.ElementTree as ET
from pathlib import Path

DIC = Path.home() / "jo-summer-2026-dive-entry" / "data" / "kanjidic2.xml.gz"
BUILT = json.load(open("dive_built.json"))

VOICED = {"か":"が","き":"ぎ","く":"ぐ","け":"げ","こ":"ご","さ":"ざ","し":"じ","す":"ず","せ":"ぜ","そ":"ぞ",
          "た":"だ","ち":"ぢ","つ":"づ","て":"で","と":"ど","は":"ば","ひ":"び","ふ":"ぶ","へ":"べ","ほ":"ぼ"}
HANDAKU = {"は":"ぱ","ひ":"ぴ","ふ":"ぷ","へ":"ぺ","ほ":"ぽ"}
ITAIJI = {"髙":"高","﨑":"崎","濵":"浜","濱":"浜","栁":"柳","𠮷":"吉","邊":"辺","邉":"辺","眞":"真",
          "齋":"斎","齊":"斉","澤":"沢","嶋":"島","廣":"広","冨":"富","戎":"戎","凜":"凛"}

kata2hira = lambda t: "".join(chr(ord(c)-0x60) if "ァ" <= c <= "ヶ" else c for c in t)

def clean(r):
    r = kata2hira(r.strip()).split(".")[0].strip("-").replace("-", "")
    return r if r and re.fullmatch(r"[ぁ-ゖー]+", r) else ""

def variants(r):
    out = {r}
    if r[0] in VOICED: out.add(VOICED[r[0]] + r[1:])
    if r[0] in HANDAKU: out.add(HANDAKU[r[0]] + r[1:])
    if len(r) > 1 and r[-1] in "つちくき": out.add(r[:-1] + "っ")
    return out

PREFS = sorted({p["pref"] for p in BUILT["people"]})
PREF_KANA = {
 "岩手県":"いわてけん","宮城県":"みやぎけん","山形県":"やまがたけん","福島県":"ふくしまけん",
 "茨城県":"いばらきけん","栃木県":"とちぎけん","群馬県":"ぐんまけん","埼玉県":"さいたまけん",
 "千葉県":"ちばけん","東京都":"とうきょうと","神奈川県":"かながわけん","新潟県":"にいがたけん",
 "富山県":"とやまけん","石川県":"いしかわけん","長野県":"ながのけん","静岡県":"しずおかけん",
 "愛知県":"あいちけん","三重県":"みえけん","滋賀県":"しがけん","京都府":"きょうとふ",
 "大阪府":"おおさかふ","兵庫県":"ひょうごけん","奈良県":"ならけん","和歌山県":"わかやまけん",
 "鳥取県":"とっとりけん","島根県":"しまねけん","岡山県":"おかやまけん","広島県":"ひろしまけん",
 "香川県":"かがわけん","愛媛県":"えひめけん","高知県":"こうちけん","福岡県":"ふくおかけん",
 "佐賀県":"さがけん","大分県":"おおいたけん","宮崎県":"みやざきけん","鹿児島県":"かごしまけん",
}
missing_pref = [p for p in PREFS if p not in PREF_KANA]
assert not missing_pref, missing_pref

chars = set()
for p in BUILT["people"]:
    for ch in p["name"]:
        if not ch.isspace() and ch != "々":
            chars.add(ITAIJI.get(ch, ch))
            chars.add(ch)

with gzip.open(DIC, "rt", encoding="utf-8") as f:
    tree = ET.parse(f)
yomi = {}
for ch in tree.getroot().iter("character"):
    lit = ch.findtext("literal")
    if lit not in chars:
        continue
    rs = set()
    for node in ch.iter("reading"):
        if node.get("r_type") in ("ja_on", "ja_kun"):
            c = clean(node.text or "")
            if c: rs |= variants(c)
    for node in ch.iter("nanori"):
        c = clean(node.text or "")
        if c: rs |= variants(c)
    # 1文字読みは落とさない。名前は「之(の)・斗(と)・汰(た)・音(と)・可(か)・也(や)」など
    # 1文字の名乗りで出来ている部分が多く、落とすと 坂之上→「さかのうえ」が引けなくなる。
    if rs:
        yomi[lit] = sorted(rs, key=lambda r: (-len(r), r))
for src, std in ITAIJI.items():
    if std in yomi and src not in yomi:
        yomi[src] = yomi[std]

missing = sorted({ch for p in BUILT["people"] for ch in p["name"]
                  if "一" <= ch <= "鿿" and ch not in yomi})
noofficial = [p["name"] for p in BUILT["people"] if not p["kana"]]
print("漢字", len(yomi), "／読みが引けなかった漢字", missing)
print("公式ふりがな無し", len(noofficial), "名 →", "・".join(noofficial))
json.dump({"yomi": yomi, "prefKana": PREF_KANA}, open("kana.json", "w"), ensure_ascii=False)
print("→ kana.json")
