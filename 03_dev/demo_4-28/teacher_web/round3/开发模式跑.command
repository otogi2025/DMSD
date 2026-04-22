#!/bin/bash
# 双击这个文件就会：
# 1. 在 round3/src/ 启动本地 HTTP server（端口 8787）
# 2. 自动打开浏览器到 http://localhost:8787/
#
# 为什么需要 server：
# 浏览器直接 open file:// 时，JSX 组件用 <script type="text/babel" src="..."> 引入，
# Babel standalone 通过 fetch() 拉源文件。file:// 下 fetch 跨源被浏览器拒绝，
# 所以页面全空白。HTTP server 解决这个问题。
#
# 退出 server：关闭弹出的终端窗口 或者在终端按 Ctrl+C

cd "$(dirname "$0")/src"

PORT=8787

# 先杀掉可能已在跑的旧 server
lsof -ti tcp:$PORT | xargs -r kill -9 2>/dev/null

# 后台启动自动打开浏览器
( sleep 0.6 && open "http://localhost:$PORT/" ) &

echo "==========================================="
echo "  Tomoshibi Round 3 · dev server"
echo "  http://localhost:$PORT/"
echo ""
echo "  终了は この窓を閉じる or Ctrl+C"
echo "==========================================="
echo ""

python3 -m http.server $PORT
