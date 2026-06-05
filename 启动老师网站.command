#!/bin/bash
# 一键启动 Tomoshibi 老师网站（React + TypeScript + Vite 版）
#
# 双击这个文件 →（1）build 前端出 dist →（2）起后端（8000 端口）托管 dist →（3）自动打开浏览器
# 用完：关掉这个终端窗口，或按 Ctrl+C → 后端停止
#
# 2026-06-05 起改成 Vite 版：老师网页从「单文件 index.html + 浏览器现场 Babel 编译」
# 迁成正规 React + TypeScript + Vite 工程。这个脚本现在先 build 出 dist/（构建产物），
# 再让后端把 dist/ 托管到 /teacher/ 路径。网页和接口同源（都在 8000），不需要跨域处理。
#
# 为什么要起后端：老师登录是实名账户（一人一密码，密码存后端数据库），登录第一屏的
# 老师名单 + 验密码都要问后端。所以前端不能单独跑，必须后端一起起。

DMSD="$HOME/dev/DMSD"
BACKEND_DIR="$DMSD/03_dev/backend/v1"
WEB_DIR="$DMSD/03_dev/teacher_web/v1"
BACKEND_PORT=8000

# 杀掉指定端口上的旧进程（避免端口被占住起不来）
kill_port() {
  local pids
  pids=$(lsof -ti tcp:"$1" 2>/dev/null)
  [ -n "$pids" ] && kill -9 $pids 2>/dev/null
}

# 关窗口 / Ctrl+C 时，把后端收掉
cleanup() {
  trap - INT TERM HUP EXIT
  echo ""
  echo "正在关闭后端……"
  kill_port "$BACKEND_PORT"
  exit 0
}
trap cleanup INT TERM HUP EXIT

# 先清掉可能残留的旧进程
kill_port "$BACKEND_PORT"

# ① build Vite 前端 → dist
echo "① 正在 build 前端（第一次或改动后会慢几秒）……"
cd "$WEB_DIR" || exit 1
if [ ! -d node_modules ]; then
  echo "   首次运行，先 npm install……"
  npm install || { echo "❌ npm install 失败"; read -r _; exit 1; }
fi
npm run build || { echo "❌ build 失败，看上面报错。按回车关闭。"; read -r _; exit 1; }
echo "   ✅ build 完成 → dist/"

# ② 起后端托管 dist
echo "② 启动后端（端口 $BACKEND_PORT）托管 dist……"
if [ ! -d "$BACKEND_DIR/.venv" ]; then
  echo "❌ 找不到后端虚拟环境：$BACKEND_DIR/.venv"
  echo "   第一次跑要先按 03_dev/backend/v1/README.md 的「起動」段建一次。"
  echo "   按回车键关闭。"
  read -r _
  exit 1
fi
cd "$BACKEND_DIR" || exit 1
source .venv/bin/activate
# 后端托管前端 dist（同 origin → 前端用相对地址 /api/v1 就能连到后端）
export TEACHER_WEB_DIR="$WEB_DIR/dist"
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

# ③ 前端由后端在 /teacher/ 路径托管，直接打开浏览器
WEB_URL="http://localhost:$BACKEND_PORT/teacher/"
( sleep 1.5 && open "$WEB_URL" ) &

echo ""
echo "════════════════════════════════════════════"
echo "  Tomoshibi 老师网站已启动（Vite 版）"
echo ""
echo "  网站地址：$WEB_URL"
echo "  后端日志：/tmp/tomoshibi_backend.log"
echo ""
echo "  用完关掉这个窗口（或按 Ctrl+C）= 全部停止"
echo "════════════════════════════════════════════"
echo ""

# 占住窗口（前台等后端进程；关窗口 / Ctrl+C 触发上面的 cleanup 收掉后端）
wait
