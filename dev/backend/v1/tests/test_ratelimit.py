"""限速器 key_func 单元测试（H1）— 按真实客户端 IP 分桶。

生产反代后 request.client.host 恒为反代内网 IP，限速会退化成全站共享一个桶。
_client_ip 优先读 X-Forwarded-For 第一跳，保证不同客户端各自独立计数。
限速本体在 dev/test 环境是关闭的（见 ratelimit._rate_limit_enabled），
故这里直接单元测 key_func 的取值逻辑，不依赖 limiter 真正触发 429。
"""

from __future__ import annotations

from starlette.requests import Request

from app.ratelimit import _client_ip


def _make_request(headers: dict[str, str], client_host: str | None) -> Request:
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/",
        "headers": [(k.encode(), v.encode()) for k, v in headers.items()],
        "client": (client_host, 12345) if client_host else None,
        "query_string": b"",
    }
    return Request(scope)


def test_client_ip_prefers_xff_first_hop():
    """带 XFF → 取第一跳（最靠近客户端的地址），忽略后续反代链。"""
    req = _make_request({"x-forwarded-for": "203.0.113.7, 10.0.0.1"}, "10.0.0.1")
    assert _client_ip(req) == "203.0.113.7"


def test_client_ip_strips_whitespace():
    req = _make_request({"x-forwarded-for": "  198.51.100.9  "}, "10.0.0.1")
    assert _client_ip(req) == "198.51.100.9"


def test_client_ip_falls_back_to_remote_addr_without_xff():
    """无 XFF（本地直连）→ 回退 request.client.host。"""
    req = _make_request({}, "192.0.2.55")
    assert _client_ip(req) == "192.0.2.55"


def test_client_ip_distinct_xff_distinct_keys():
    """同一反代后的两个不同客户端 → 不同分桶键（各自独立计数的前提）。

    修复前两者都落到反代内网 IP（同一个键）→ 共享一个桶。
    """
    a = _make_request({"x-forwarded-for": "1.1.1.1"}, "10.0.0.1")
    b = _make_request({"x-forwarded-for": "2.2.2.2"}, "10.0.0.1")
    assert _client_ip(a) == "1.1.1.1"
    assert _client_ip(b) == "2.2.2.2"
    assert _client_ip(a) != _client_ip(b)
