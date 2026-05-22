#!/usr/bin/env python3
"""
Tomoshibi demo server
=====================
用途：
  - 原本的静态文件服务（替代 `python3 -m http.server`）
  - 新增：POST /checkin?no=XX 接收 iPhone 快捷指令的点呼请求
  - 新增：GET /events/latest 前端 poll 最新事件

架构（点呼機 代替方案 · 2026-04-22 确定）：
  iPhone (快捷指令 · NFC Auto 触发)
    ↓ POST http://<Mac IP>:8787/checkin?no=00
  demo_server.py (本程序)
    ↓ 记录事件 → in-memory latest_event
  Web (live-roll-call.jsx · 每 1s fetch /events/latest)
    ↓ 收到新事件 → 座席变绿 + SpeechSynthesis 日语播報

使用：
  python3 demo_server.py
  或双击 `开发模式跑.command`
"""
import http.server
import socketserver
import json
import time
import os
import sys
import urllib.request
import urllib.error
from urllib.parse import urlparse, parse_qs

BACKEND_URL = 'http://localhost:8000'

PORT = 8787
SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')

# Shared state (single-threaded http.server → no lock needed)
latest_event = {"no": None, "name": None, "timestamp": 0, "seq": 0}
event_history = []  # for debugging


class TomoshibiHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SRC_DIR, **kwargs)

    def log_message(self, format, *args):
        # Quiet logging — only show non-font requests
        msg = format % args
        if '.woff2' in msg or '/events/latest' in msg:
            return
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), msg))

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store')

    def end_headers(self):
        self._cors()
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def _proxy_to_backend(self):
        """将请求透传到 FastAPI 后端（localhost:8000）。"""
        target = BACKEND_URL + self.path
        body_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(body_len) if body_len > 0 else None
        req = urllib.request.Request(target, data=body, method=self.command)
        for key in ('Content-Type', 'Authorization'):
            if key in self.headers:
                req.add_header(key, self.headers[key])
        try:
            with urllib.request.urlopen(req) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in ('transfer-encoding', 'connection'):
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(e.read())

    def do_GET(self):
        parsed = urlparse(self.path)

        # /api/v1/ → FastAPI backend
        if parsed.path.startswith('/api/v1/'):
            self._proxy_to_backend()
            return

        if parsed.path == '/events/latest':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(latest_event, ensure_ascii=False).encode('utf-8'))
            return

        if parsed.path == '/events/history':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(event_history[-50:], ensure_ascii=False).encode('utf-8'))
            return

        if parsed.path == '/api/server-info':
            # 返回 Mac 的局域网 IP，用于 iPhone 快捷指令 URL 自动生成
            import socket
            ips = []
            # 方法 1: UDP connect 拿 outbound IP（热点 / Wi-Fi 都准确）
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ips.append(s.getsockname()[0])
                s.close()
            except Exception:
                pass
            # 方法 2: hostname 解析（补齐其他网卡 IP）
            try:
                for info in socket.getaddrinfo(socket.gethostname(), None):
                    ip = info[4][0]
                    if ':' not in ip and not ip.startswith('127.') and ip not in ips:
                        ips.append(ip)
            except Exception:
                pass
            primary = ips[0] if ips else '127.0.0.1'
            info = {
                "ips": ips,
                "primary": primary,
                "port": PORT,
                "checkin_url_template": f"http://{primary}:{PORT}/checkin?no=XX",
                "generated_at": int(time.time() * 1000),
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(info, ensure_ascii=False).encode('utf-8'))
            return

        # 静态文件 fallback
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)

        # /api/v1/ → FastAPI backend
        if parsed.path.startswith('/api/v1/'):
            self._proxy_to_backend()
            return

        if parsed.path == '/checkin':
            global latest_event
            qs = parse_qs(parsed.query)
            no = qs.get('no', [''])[0].strip()
            name = qs.get('name', [''])[0].strip() or None

            if not no:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"ok":false,"error":"no= required"}')
                return

            latest_event = {
                "no": no,
                "name": name,
                "timestamp": int(time.time() * 1000),
                "seq": latest_event["seq"] + 1,
            }
            event_history.append(latest_event)
            print(f"  ✔ 点呼: 番号 {no}" + (f" ({name})" if name else "") + f" · seq={latest_event['seq']}", flush=True)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "no": no, "seq": latest_event["seq"]}).encode())
            return

        self.send_response(404)
        self.end_headers()


def main():
    import socket
    # Get local IPs (for iPhone Shortcuts setup)
    hostname = socket.gethostname()
    ips = []
    try:
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            if ':' not in ip and not ip.startswith('127.'):
                if ip not in ips:
                    ips.append(ip)
    except Exception:
        pass

    print("=" * 64)
    print("  Tomoshibi demo server")
    print("=" * 64)
    print(f"  ローカル:           http://localhost:{PORT}/")
    for ip in ips:
        print(f"  iPhone から接続用:   http://{ip}:{PORT}/")
    print()
    print(f"  iPhone 快捷指令 URL  →  http://<上の IP>:{PORT}/checkin?no=00")
    print()
    print("  終了: Ctrl+C or ウィンドウを閉じる")
    print("=" * 64)
    print()

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), TomoshibiHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  shutdown")


if __name__ == '__main__':
    main()
