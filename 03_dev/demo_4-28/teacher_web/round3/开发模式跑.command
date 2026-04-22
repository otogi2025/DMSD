#!/bin/bash
# 双击这个 → 在 round3/ 起 demo_server.py（默认 port 8787）
# 功能：
#   (a) 静态文件服务（跟 python3 -m http.server 等价）
#   (b) POST /checkin?no=XX 接收 iPhone 快捷指令（点呼機 代替モード）
#   (c) GET /events/latest 前端 1 秒 poll
#
# 启动后会：
#   - 打印 localhost 和局域网 IP（iPhone 快捷指令要用局域网 IP）
#   - 自动开浏览器到 http://localhost:8787/
#
# 終了は この窓を閉じる or Ctrl+C

cd "$(dirname "$0")"

PORT=8787

# 先杀掉已在跑的 server
lsof -ti tcp:$PORT | xargs -r kill -9 2>/dev/null

# 0.8 秒後に自動でブラウザを開く
( sleep 0.8 && open "http://localhost:$PORT/" ) &

python3 demo_server.py
