#!/bin/bash
# 2026-05-26 frontend-design polish 后改 — 退 Vite，直接静态服务跑 Ryō standalone HTML
#
# 双击这个 → 在 src/ 起 Python 内建 HTTP 服务器（端口 8787）+ 自动开浏览器
#
# 功能：
#   静态文件服务（serve src/ 目录里的 index.html + assets + vendor）
#
# 已废弃：
#   - POST /checkin?no=XX（iPhone 快捷指令端点） — 需要 demo_server.py，文件不存在
#   - GET /events/latest（1 秒 poll 端点） — 同上
#   → NFC 实时点呼 demo 功能暂时失效；想恢复要写 demo_server.py
#
# 終了 = この窓を閉じる or Ctrl+C

cd "$(dirname "$0")"

PORT=8787

# 先杀掉已在跑的 server（避免端口冲突）
lsof -ti tcp:$PORT | xargs -r kill -9 2>/dev/null

# 0.8 秒後に自動でブラウザを開く
( sleep 0.8 && open "http://localhost:$PORT/" ) &

# 在 src/ 目录跑 Python 内建静态服务器
cd src
exec python3 -m http.server $PORT
