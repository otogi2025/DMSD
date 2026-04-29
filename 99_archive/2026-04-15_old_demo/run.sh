#!/bin/bash
set -e

# 切换到脚本所在目录 (不管你在哪里执行这个脚本, 都能跑)
cd "$(dirname "$0")"

# 检查 python3 是否安装
if ! command -v python3 >/dev/null 2>&1; then
  echo "错误: 没找到 python3。请先安装 Python 3 (推荐去 https://www.python.org/ 下载)。"
  exit 1
fi

# 安装后端依赖
# --user 参数: 装到用户目录而不是系统目录, 避免 macOS 自带 Python 的权限问题
echo "正在安装后端依赖 (Flask 等)..."
pip3 install --user -r backend/requirements.txt

echo ""
echo "========================================"
echo "  Mac 本机 IP 地址 (局域网)"
echo "========================================"
ifconfig | grep "inet " | grep -v 127.0.0.1
echo "========================================"
echo ""
echo "⚠️  请把上面的 IP 地址填到 frontend/script.js 的 MAC_IP 字段(如果要让 iPhone 连接)"
echo ""
echo "现在用浏览器打开 frontend/index.html(双击即可)"
echo ""
echo "按 Ctrl+C 停止后端"
echo ""

# 清理占用 8000 端口的残留进程 (Flask debug 模式有时会留 zombie)
STALE=$(lsof -ti :8000 2>/dev/null || true)
if [ -n "$STALE" ]; then
  echo "检测到 8000 端口被占用, 清理中... (PID: $STALE)"
  echo "$STALE" | xargs kill -9 2>/dev/null || true
  sleep 0.5
fi

# 启动后端 Flask 服务器
cd backend && python3 app.py
