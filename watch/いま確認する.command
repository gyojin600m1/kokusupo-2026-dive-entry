#!/bin/bash
cd "$(dirname "$0")/.."
echo "=== 国スポ2026 飛込 見張り ==="
launchctl print "gui/$(id -u)/com.fukuda.swim.kokusupo2026-dive" >/dev/null 2>&1 && echo "見張り: 動いています" || echo "見張り: 止まっています"
echo
echo "--- 取り込み済み ---"
python3 -c "import json;d=json.load(open('tools/results.json'));print(f\"{len(d['done'])}/8競技  競技{d['done']}\")" 2>/dev/null || echo "まだありません"
echo
echo "--- ログ（最後の15行）---"
tail -15 watch/log.txt 2>/dev/null || echo "まだありません"
echo
echo "公開ページ: https://gyojin600m1.github.io/kokusupo-2026-dive-entry/"
read -n1 -p "Enterで閉じます"
