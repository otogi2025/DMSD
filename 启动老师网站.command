#!/bin/bash
# 一键启动 Tomoshibi 老师网站 —— 后端（8000 端口）+ 前端（8787 端口）一起起
#
# 双击这个文件 → 同时起后端和前端 → 自动打开浏览器
# 用完：关掉这个终端窗口，或按 Ctrl+C → 后端和前端一起停
#
# 为什么要起后端：2026-05-27 老师登录改成实名账户（一人一密码，密码存在
# 后端数据库里），登录第一屏的老师名单 + 验密码都要问后端。所以前端
# 不能再单独跑了，必须两个一起起。

DMSD="$HOME/dev/DMSD"
BACKEND_DIR="$DMSD/03_dev/backend/v1"
WEB_SRC="$DMSD/03_dev/teacher_web/v1/src"
BACKEND_PORT=8000
WEB_PORT=8787

# 杀掉指定端口上的旧进程（避免端口被占住起不来）
kill_port() {
  local pids
  pids=$(lsof -ti tcp:"$1" 2>/dev/null)
  [ -n "$pids" ] && kill -9 $pids 2>/dev/null
}

# 关窗口 / Ctrl+C 时，把后端和前端都收掉
cleanup() {
  trap - INT TERM HUP EXIT
  echo ""
  echo "正在关闭后端和前端……"
  kill_port "$BACKEND_PORT"
  kill_port "$WEB_PORT"
  exit 0
}
trap cleanup INT TERM HUP EXIT

# 先清掉可能残留的旧进程
kill_port "$BACKEND_PORT"
kill_port "$WEB_PORT"

# ① 起后端
echo "① 启动后端（端口 $BACKEND_PORT）……"
if [ ! -d "$BACKEND_DIR/.venv" ]; then
  echo "❌ 找不到后端虚拟环境：$BACKEND_DIR/.venv"
  echo "   第一次跑要先按 03_dev/backend/v1/README.md 的「起動」段建一次。"
  echo "   按回车键关闭。"
  read -r _
  exit 1
fi
cd "$BACKEND_DIR" || exit 1
source .venv/bin/activate
python -m app.main > /tmp/tomoshibi_backend.log 2>&1 &

# 等后端就绪（最多等 20 秒）
echo "   等后端起来……"
for i in $(seq 1 20); do
  if curl -s "http://localhost:$BACKEND_PORT/docs" > /dev/null 2>&1; then
    echo "   ✅ 后端就绪"
    break
  fi
  if [ "$i" -eq 20 ]; then
    echo "   ⚠️ 等了 20 秒后端还没起来，看日志：/tmp/tomoshibi_backend.log"
  fi
  sleep 1
done

# ② 起前端
echo "② 启动前端网站（端口 $WEB_PORT）……"
cd "$WEB_SRC" || exit 1

# 1.5 秒后自动打开浏览器
( sleep 1.5 && open "http://localhost:$WEB_PORT/" ) &

echo ""
echo "════════════════════════════════════════════"
echo "  Tomoshibi 老师网站已启动"
echo ""
echo "  网站地址：http://localhost:$WEB_PORT/"
echo "  后端日志：/tmp/tomoshibi_backend.log"
echo ""
echo "  用完关掉这个窗口（或按 Ctrl+C）= 全部停止"
echo "════════════════════════════════════════════"
echo ""

# 前台跑前端静态服务器（占住窗口；它一退脚本就结束，触发上面的 cleanup）
python3 -m http.server "$WEB_PORT"
