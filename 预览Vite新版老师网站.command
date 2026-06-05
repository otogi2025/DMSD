#!/bin/bash
# 预览 Vite 新版老师网站（React+TypeScript+Vite 迁移后的版本）
#
# 双击这个文件 →（1）build 前端出 dist →（2）起后端托管 dist →（3）浏览器打开看新版
# 用完：关掉这个终端窗口，或按 Ctrl+C → 后端停止
#
# 想跟旧版对比界面：另开一个「终端」窗口跑下面两行，浏览器开 http://localhost:8787
#   cd ~/dev/DMSD/03_dev/teacher_web/v1/src
#   python3 -m http.server 8787
#
# 确认新版界面跟旧版一致后，再去改正式的「启动老师网站.command」切到 dist（或叫 CC 改）。

DMSD="$HOME/dev/DMSD"
BACKEND_DIR="$DMSD/03_dev/backend/v1"
WEB_DIR="$DMSD/03_dev/teacher_web/v1"
BACKEND_PORT=8000

kill_port() {
  local pids
  pids=$(lsof -ti tcp:"$1" 2>/dev/null)
  [ -n "$pids" ] && kill -9 $pids 2>/dev/null
}

cleanup() {
  trap - INT TERM HUP EXIT
  echo ""
  echo "正在关闭后端……"
  kill_port "$BACKEND_PORT"
  exit 0
}
trap cleanup INT TERM HUP EXIT

kill_port "$BACKEND_PORT"

# ① build Vite 前端 → dist
echo "① 正在 build Vite 前端（第一次或改动后会慢几秒）……"
cd "$WEB_DIR" || exit 1
if [ ! -d node_modules ]; then
  echo "   首次运行，先 npm install……"
  npm install || { echo "❌ npm install 失败"; read -r _; exit 1; }
fi
npm run build || { echo "❌ build 失败，看上面报错"; read -r _; exit 1; }
echo "   ✅ build 完成 → dist/"

# ② 起后端托管 dist
echo "② 启动后端（端口 $BACKEND_PORT）托管 dist……"
if [ ! -d "$BACKEND_DIR/.venv" ]; then
  echo "❌ 找不到后端虚拟环境：$BACKEND_DIR/.venv"
  echo "   第一次跑要先按 03_dev/backend/v1/README.md 的「起動」段建一次。"
  read -r _
  exit 1
fi
cd "$BACKEND_DIR" || exit 1
source .venv/bin/activate
export TEACHER_WEB_DIR="$WEB_DIR/dist"
python -m app.main > /tmp/tomoshibi_backend_vite.log 2>&1 &

echo "   等后端起来……"
for i in $(seq 1 20); do
  if curl -s "http://localhost:$BACKEND_PORT/docs" > /dev/null 2>&1; then
    echo "   ✅ 后端就绪"
    break
  fi
  if [ "$i" -eq 20 ]; then
    echo "   ⚠️ 等了 20 秒后端还没起来，看日志：/tmp/tomoshibi_backend_vite.log"
  fi
  sleep 1
done

WEB_URL="http://localhost:$BACKEND_PORT/teacher/"
( sleep 1.5 && open "$WEB_URL" ) &

echo ""
echo "════════════════════════════════════════════"
echo "  Tomoshibi 老师网站 · Vite 新版预览"
echo ""
echo "  新版地址：$WEB_URL"
echo "  后端日志：/tmp/tomoshibi_backend_vite.log"
echo ""
echo "  对比旧版：另开终端跑 python3 -m http.server 8787（在 v1/src 下）→ 开 localhost:8787"
echo "  用完关掉这个窗口（或 Ctrl+C）= 停止"
echo "════════════════════════════════════════════"
echo ""

wait
