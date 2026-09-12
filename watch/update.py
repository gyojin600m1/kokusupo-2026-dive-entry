# -*- coding: utf-8 -*-
"""国スポ2026 飛込：公式の順位一覧が出たら取り込んで公開ページを更新する。
launchdから呼ばれる（最終日は1分おき）。Claudeもトークンも使わない。"""
import json, subprocess, sys, os
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "watch" / "log.txt"
STATE = ROOT / "watch" / "state.json"
LABEL = "com.fukuda.swim.kokusupo2026-dive"
STOP_AFTER = datetime(2026, 9, 12, 20, 0)      # 大会終了で自分を止める
WINDOWS = {"2026-09-10": (9, 19), "2026-09-11": (9, 19), "2026-09-12": (9, 19)}

def log(msg):
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}\n")

def notify(title, msg):
    subprocess.run(["osascript", "-e",
                    f'display notification "{msg}" with title "{title}"'], capture_output=True)

def main():
    now = datetime.now()
    # 自己停止は窓ガードより先（[[swim-meet-updater-schedule]]）
    if now >= STOP_AFTER:
        log("大会終了。見張りを解除します")
        notify("国スポ飛込", "見張りを終了しました")
        subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{LABEL}"], capture_output=True)
        return
    day, hour = f"{now:%Y-%m-%d}", now.hour
    win = WINDOWS.get(day)
    if not win or not (win[0] <= hour < win[1]):
        return                                   # 競技のない時間は静かにする

    before = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"done": []}
    r = subprocess.run([sys.executable, "tools/fetch_results.py"], cwd=ROOT,
                       capture_output=True, text=True)
    if r.returncode != 0:
        log("取り込み失敗（検算に落ちた）: " + (r.stdout + r.stderr).strip().replace("\n", " / "))
        notify("国スポ飛込 見張り", "検算に落ちました。log.txt を確認してください")
        return
    done = json.loads((ROOT / "tools" / "results.json").read_text(encoding="utf-8"))["done"]
    new = [n for n in done if n not in before["done"]]
    if not new:
        return

    b = subprocess.run([sys.executable, "make_app.py"], cwd=ROOT / "tools",
                       capture_output=True, text=True)
    if b.returncode != 0:
        log("ビルド失敗: " + (b.stdout + b.stderr).strip().replace("\n", " / "))
        return
    (ROOT / "tools" / "index.html").replace(ROOT / "index.html")

    # 結果に関係するファイルだけを入れる（無関係な変更を巻き込まない）
    subprocess.run(["git", "add", "index.html", "tools/results.json", "watch/state.json"],
                   cwd=ROOT, capture_output=True)
    msg = f"結果を反映（競技 {'・'.join(map(str, new))}）"
    subprocess.run(["git", "-c", "user.name=gyojin600m1", "-c",
                    "user.email=gyojin600m1@gmail.com", "commit", "-q", "-m", msg],
                   cwd=ROOT, capture_output=True)
    changed = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode != 0
    p = subprocess.run(["git", "push", "-q", "origin", "main"], cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        log("push失敗: " + (p.stdout + p.stderr).strip().replace("\n", " / "))
        notify("国スポ飛込 見張り", "pushに失敗しました")
        return
    STATE.write_text(json.dumps({"done": done}, ensure_ascii=False), encoding="utf-8")
    log(f"{msg} → 公開済み（{len(done)}/8競技）")
    notify("国スポ飛込 結果更新", f"競技 {'・'.join(map(str, new))} の結果を反映しました")

if __name__ == "__main__":
    main()
