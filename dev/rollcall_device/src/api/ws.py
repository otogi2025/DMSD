"""设备 WebSocket 长连接（契约 §5）。

- URL：`{ws_url}/api/v1/ws/device?token=<device JWT>`
- 收（server→device）：session_started / session_ended / roster_updated / audio_updated
  → 通过 `on_event(kind, data)` 回调交给主程序（主程序把它转成 ControlEvent 入队）。
- 发（device→server）：每 30 秒 heartbeat `{ts, fw_version}`。
- 断线重连：指数退避，初始 1 秒、上限 60 秒（契约 §5）。核心签到不依赖 WS 存活。

在独立线程里跑自己的 asyncio 事件循环（主程序用线程模型，WS 用异步，互不阻塞）。
退避计算与消息分派抽成纯函数便于单测。
"""

from __future__ import annotations

import asyncio
import json
import threading
from collections.abc import Callable

from ..timeutil import now_jst_iso
from .auth import AuthManager

# 契约 §5 的两个定时/退避常量
HEARTBEAT_INTERVAL_S = 30.0
BACKOFF_INITIAL_S = 1.0
BACKOFF_CAP_S = 60.0

# server→device 已知消息类型（契约 §5 表）
SERVER_MESSAGE_TYPES = frozenset(
    {"session_started", "session_ended", "roster_updated", "audio_updated"}
)

EventCallback = Callable[[str, dict], None]


def next_backoff(current: float) -> float:
    """指数退避：翻倍，封顶 60 秒（契约 §5）。"""
    return min(current * 2.0, BACKOFF_CAP_S)


def parse_ws_message(raw: str) -> tuple[str, dict] | None:
    """解析一条 WS 文本消息为 (type, data)；非法 / 未知类型返回 None。"""
    try:
        msg = json.loads(raw)
    except (ValueError, TypeError):
        return None
    if not isinstance(msg, dict):
        return None
    msg_type = msg.get("type")
    if msg_type not in SERVER_MESSAGE_TYPES:
        return None
    data = msg.get("data")
    if not isinstance(data, dict):
        data = {}
    return msg_type, data


class WsClient:
    """设备 WebSocket 客户端（线程 + asyncio）。"""

    def __init__(
        self,
        ws_url: str,
        auth: AuthManager,
        on_event: EventCallback,
        fw_version: str = "rollcall-device-unknown",
    ) -> None:
        self._ws_url = ws_url.rstrip("/")
        self._auth = auth
        self._on_event = on_event
        self._fw_version = fw_version
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        # 当前连接 + 所属事件循环：stop() 时 close 打断 async for / sleep
        self._conn = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._async_stop: asyncio.Event | None = None

    def start(self) -> None:
        """起独立线程跑 WS 循环。"""
        self._thread = threading.Thread(
            target=self._run, name="ws-listener", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        """置停机标志，并主动关闭当前连接 / 唤醒异步等待，让 shutdown 毫秒级生效。"""
        self._stop.set()
        loop = self._loop
        async_stop = self._async_stop
        conn = self._conn
        if loop is None or not loop.is_running():
            return
        if async_stop is not None:
            loop.call_soon_threadsafe(async_stop.set)
        if conn is not None:
            # close() 打断 _session 里的 async for，以及连接上下文
            asyncio.run_coroutine_threadsafe(conn.close(), loop)

    def join(self, timeout: float | None = None) -> None:
        if self._thread is not None:
            self._thread.join(timeout)

    def _url_with_token(self) -> str:
        token = self._auth.ensure_token()
        return f"{self._ws_url}/api/v1/ws/device?token={token}"

    def _run(self) -> None:
        try:
            asyncio.run(self._run_loop())
        except Exception:  # noqa: BLE001 —— WS 线程绝不能拖垮主程序
            pass

    async def _run_loop(self) -> None:
        import websockets  # 延迟导入：无 websockets 库也不影响其余模块

        self._loop = asyncio.get_running_loop()
        self._async_stop = asyncio.Event()
        if self._stop.is_set():
            self._async_stop.set()

        backoff = BACKOFF_INITIAL_S
        while not self._stop.is_set():
            try:
                url = self._url_with_token()
                async with websockets.connect(url) as conn:
                    self._conn = conn
                    backoff = BACKOFF_INITIAL_S  # 连上即复位退避
                    await self._session(conn)
            except Exception:  # noqa: BLE001 —— 断线 / 握手失败都退避重连
                if self._stop.is_set():
                    break
                # 退避 sleep 与停机事件并行等待，stop() 可立刻打断
                try:
                    await asyncio.wait_for(self._async_stop.wait(), timeout=backoff)
                    break  # 停机事件已置位
                except TimeoutError:
                    pass
                backoff = next_backoff(backoff)
            finally:
                self._conn = None

    async def _session(self, conn) -> None:
        """一次连接生命周期：并行跑心跳发送 + 消息接收。"""
        hb_task = asyncio.create_task(self._heartbeat_loop(conn))
        try:
            async for raw in conn:
                parsed = parse_ws_message(raw)
                if parsed is not None:
                    kind, data = parsed
                    try:
                        self._on_event(kind, data)
                    except Exception:  # noqa: BLE001 —— 回调异常不断连接
                        pass
                if self._stop.is_set():
                    break
        finally:
            hb_task.cancel()

    async def _heartbeat_loop(self, conn) -> None:
        while not self._stop.is_set():
            # 心跳间隔也可被停机事件打断
            async_stop = self._async_stop
            if async_stop is not None:
                try:
                    await asyncio.wait_for(
                        async_stop.wait(), timeout=HEARTBEAT_INTERVAL_S
                    )
                    break
                except TimeoutError:
                    pass
            else:
                await asyncio.sleep(HEARTBEAT_INTERVAL_S)
            if self._stop.is_set():
                break
            msg = {
                "type": "heartbeat",
                "data": {"ts": now_jst_iso(), "fw_version": self._fw_version},
            }
            await conn.send(json.dumps(msg))
