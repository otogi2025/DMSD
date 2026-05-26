#!/usr/bin/env python3
"""
demo_server.py — Tomoshibi 教师 Web demo 用 HTTP server

承接 itsuki TODO §🛠️ §L 第 1 条要求的功能:
  - NFC iPhone 快捷指令 → demo_server → 浏览器实时 polling 点呼 demo
  - 当前 ./tomoshibi start 跑 python3 -m http.server 只做静态，NFC 实时点呼功能失效
  - 本 server 替换它，恢复实时点呼 demo

提供 3 个端点 + src/ 静态文件 serve:
  - GET  /api/server-info  — 返回 LAN IP + port（浏览器 auto-detect 用）
  - POST /checkin?no=XX    — 接 iPhone 快捷指令的 NFC 点呼（存 event with seq）
  - GET  /events/latest    — 浏览器 1 秒 poll，返最新 event（{event: null} 表示没新事件）
  - 其他                    — src/ 配下走 SimpleHTTPRequestHandler 默认静态 serve

实现注:
  - stdlib only（不引 aiohttp 等外部依赖）
  - threading 支持同时连接（iPhone tap 中不 block 浏览器 poll）
  - events 是 in-memory list（重启清空 — demo 用所以 OK）
  - CORS 头 Access-Control-Allow-Origin: *（iPhone Shortcuts 一般不发 origin 头但加上保险）

用法:
  cd ~/dev/DMSD/03_dev/teacher_web/v1
  python3 demo_server.py
  → port 8787 起 / iPhone Shortcuts URL 是 http://<LAN_IP>:8787/checkin?no=XX

从 tomoshibi CLI 启动时把 cmd_start() 里的 `python3 -m http.server $PORT` 改成
`python3 demo_server.py`（本 commit 同步改）。
"""

from __future__ import annotations

import json
import os
import socket
import sys
import threading
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PORT = 8787

# event 内存存储 — append-only，最新在末尾
_events_lock = threading.Lock()
_events: list[dict] = []
_seq = 0


def _lan_ip() -> str:
    """UDP trick 拿 outbound IP（热点 / Wi-Fi 都准）。"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


class TomoshibiHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/server-info":
            self._send_json({"ip": _lan_ip(), "port": PORT})
            return
        if parsed.path == "/events/latest":
            with _events_lock:
                latest = _events[-1] if _events else None
            self._send_json({"event": latest})
            return
        # 其他路径走静态文件
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/checkin":
            self._send_json({"error": "unknown endpoint"}, status=404)
            return
        global _seq
        qs = parse_qs(parsed.query)
        no = (qs.get("no", [""])[0] or "").strip()
        if not no:
            self._send_json({"error": "missing ?no=XX"}, status=400)
            return
        with _events_lock:
            _seq += 1
            event = {
                "seq": _seq,
                "no": no,
                "type": "checkin",
                "at": datetime.now().isoformat(timespec="seconds"),
            }
            _events.append(event)
        self._send_json({"ok": True, "event": event})

    def do_OPTIONS(self) -> None:
        # CORS preflight（iPhone Shortcuts 一般不发但浏览器 fetch 会用）
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:  # type: ignore[override]
        sys.stderr.write(
            "[demo_server] %s - %s\n" % (self.address_string(), fmt % args),
        )


def main() -> None:
    # SimpleHTTPRequestHandler 以 src/ 为 root serve，所以先 cd 进去
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.join(here, "src"))
    ip = _lan_ip()
    print(f"  ✓ Tomoshibi demo_server 起動 · port {PORT} · LAN IP {ip}")
    print(f"    ローカル          http://localhost:{PORT}/")
    print(f"    iPhone 接続用      http://{ip}:{PORT}/")
    print(f"    NFC checkin       POST http://{ip}:{PORT}/checkin?no=XX")
    print(f"    最新 event        GET  http://localhost:{PORT}/events/latest")
    print(f"    server-info       GET  http://localhost:{PORT}/api/server-info")
    print()
    print("  Ctrl+C で停止")
    with ThreadingHTTPServer(("", PORT), TomoshibiHandler) as srv:
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\n  停止しました")


if __name__ == "__main__":
    main()
