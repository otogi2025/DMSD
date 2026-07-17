"""Tomoshibi 点呼机主程序 —— 入口 + 主状态机 + 双线程编排。

架构（设计日志 §3.1 + 契约 §4-§6）：
- 线程 A（硬件采集）：PN532 轮询读卡 + ST25DV GPO/邮箱轮询，只往队列塞事件，不做网络。
- 线程 B（网络反馈）：从队列取事件 → 上报后端 → LED / 播音；断网走离线降级 + 恢复补传。
- WS 监听（独立线程 + asyncio）：收 session/roster/audio 推送，转成 ControlEvent 入队。
- 优雅退出：SIGINT / SIGTERM → 置停机标志 → 各线程收尾 → 关硬件。

状态机：IDLE(待机/蓝) → PROCESSING(处理/蓝闪) → SUCCESS/FAIL/WAITING/AUTH_ERROR → IDLE。

`--simulate`：无硬件时用 stdin 模拟刷卡（便于跟本地后端联调），LED/音频降级为控制台打印。
"""

from __future__ import annotations

import argparse
import logging
import queue
import signal
import sys
import threading
import time
import uuid
from pathlib import Path

import httpx

from . import config as config_mod
from .api.auth import AuthError, AuthManager, DeviceKey
from .api.client import ApiClient
from .api.envelope import ApiResponse, NetworkError
from .api.ws import WsClient
from .audio.player import Tone
from .config import Config
from .events import CardEvent, CheckinEvent, ControlEvent, PhoneEvent
from .feedback import Feedback, for_offline, for_response
from .led.controller import FakeLedBackend, LedController, LedState
from .nfc.debounce import UidDebouncer
from .nfc.interfaces import CardReader, FakeCardReader, FakeMailboxReader, MailboxReader
from .nfc.payload import PayloadError, build_mailbox_payload, parse_mailbox_payload
from .offline.queue import OfflineQueue

logger = logging.getLogger("rollcall")

# 反馈灯保持时长（秒）—— 显示成功/失败后回待机
FEEDBACK_HOLD_S = 1.5
# 线程 A 无卡时的轮询间隔（秒）
POLL_INTERVAL_S = 0.05


# ============================================================================
# 控制台降级实现（--simulate 用，无硬件时打印代替声光）
# ============================================================================


class ConsoleAudioPlayer:
    """把播音动作打印到控制台（simulate 模式，无真实喇叭）。"""

    def play_tone(self, tone: Tone) -> bool:
        logger.info("[音频] 提示音：%s", tone.value)
        return True

    def play_name(self, audio_file: str) -> bool:
        logger.info("[音频] 播报：%s", audio_file)
        return True

    def stop(self) -> None:
        pass

    def close(self) -> None:
        pass


class LoggingLedController(LedController):
    """LED 状态切换时打印（simulate 模式）。"""

    def set(self, state: LedState) -> None:
        super().set(state)
        logger.info("[LED] → %s", state.value)


# ============================================================================
# 主设备编排
# ============================================================================


class RollCallDevice:
    """点呼机运行时：持有全部组件 + 双线程 + WS。"""

    def __init__(
        self,
        cfg: Config,
        card_reader: CardReader,
        mailbox_reader: MailboxReader,
        led: LedController,
        audio,  # AudioPlayer | ConsoleAudioPlayer（鸭子类型：play_tone/play_name/close）
        api: ApiClient,
        auth: AuthManager,
        offline_queue: OfflineQueue,
        roster,
        ws: WsClient | None,
        simulate: bool = False,
    ) -> None:
        self._cfg = cfg
        self._card_reader = card_reader
        self._mailbox_reader = mailbox_reader
        self._led = led
        self._audio = audio
        self._api = api
        self._auth = auth
        self._queue = offline_queue
        self._roster = roster
        self._ws = ws
        self._simulate = simulate

        self._event_queue: queue.Queue = queue.Queue()
        self._stop = threading.Event()
        self._debouncer = UidDebouncer(window=2.0)
        self._threads: list[threading.Thread] = []

    # --------------------------- 生命周期 ---------------------------

    def start(self) -> None:
        self._led.set(LedState.STANDBY)
        if self._ws is not None:
            self._ws.start()
        thread_a = threading.Thread(
            target=self._collect_loop, name="collect", daemon=True
        )
        thread_b = threading.Thread(
            target=self._consume_loop, name="consume", daemon=False
        )
        thread_a.start()
        thread_b.start()
        self._threads = [thread_a, thread_b]
        logger.info("点呼机启动完成，进入待机（device_id=%s）", self._cfg.device_id)

    def request_stop(self) -> None:
        self._stop.set()
        if self._ws is not None:
            self._ws.stop()

    def wait(self) -> None:
        """主线程阻塞至停机信号。"""
        try:
            while not self._stop.is_set():
                time.sleep(0.2)
        except KeyboardInterrupt:
            self.request_stop()

    def shutdown(self) -> None:
        logger.info("正在停机…")
        self.request_stop()
        # 唤醒 consume 线程
        for thread in self._threads:
            thread.join(timeout=5.0)
        try:
            self._card_reader.close()
        except Exception:  # noqa: BLE001
            pass
        try:
            self._mailbox_reader.close()
        except Exception:  # noqa: BLE001
            pass
        self._led.close()
        self._audio.close()
        self._queue.close()
        if self._ws is not None:
            self._ws.join(timeout=2.0)
        logger.info("已停机")

    # --------------------------- WS 回调 ---------------------------

    def on_ws_event(self, kind: str, data: dict) -> None:
        """WS 线程调用：把控制消息塞进事件队列，交线程 B 串行处理。"""
        self._event_queue.put(ControlEvent(kind=kind, data=data))

    # --------------------------- 线程 A：采集 ---------------------------

    def _collect_loop(self) -> None:
        if self._simulate:
            self._collect_from_stdin()
        else:
            self._collect_from_hardware()

    def _collect_from_hardware(self) -> None:
        from .timeutil import now_jst_iso

        while not self._stop.is_set():
            # 路径 A：实体卡
            try:
                uid = self._card_reader.read_uid(timeout=0.5)
            except Exception:  # noqa: BLE001 —— 采集异常不拖垮线程
                uid = None
            if uid and self._debouncer.accept(uid):
                self._event_queue.put(CardEvent(card_uid=uid, swipe_time=now_jst_iso()))

            # 路径 B：手机写进 ST25DV 邮箱
            try:
                raw = self._mailbox_reader.poll()
            except Exception:  # noqa: BLE001
                raw = None
            if raw is not None:
                self._handle_mailbox_raw(raw)

            time.sleep(POLL_INTERVAL_S)

    def _handle_mailbox_raw(self, raw: bytes) -> None:
        from .timeutil import now_jst_iso

        try:
            payload = parse_mailbox_payload(raw)
        except PayloadError as exc:
            # 契约 §7：长度 / 版本不符即丢弃、记日志、不上报
            logger.warning("邮箱载荷非法，丢弃：%s", exc)
            return
        self._event_queue.put(
            PhoneEvent(
                student_id=payload.student_id,
                idempotency_key=payload.idempotency_key,
                swipe_time=now_jst_iso(),
                checkin_type=payload.checkin_type,
            )
        )

    def _collect_from_stdin(self) -> None:
        """simulate：从 stdin 读模拟刷卡。

        输入格式：
          - 14 位 hex        → 路径 A 刷卡（card_uid）
          - card <uid>       → 同上
          - phone <uuid>     → 路径 B 手机写邮箱（student_id，自动生成 idempotency_key）
          - <uuid>           → 同 phone
          - quit / exit      → 停机
        """
        from .timeutil import now_jst_iso

        print(
            "=== simulate 模式：输入刷卡数据（card <uid> / phone <uuid> / quit）===",
            flush=True,
        )
        for line in sys.stdin:
            if self._stop.is_set():
                break
            text = line.strip()
            if not text:
                continue
            if text in ("quit", "exit"):
                self.request_stop()
                break
            event = self._parse_sim_line(text, now_jst_iso())
            if event is not None:
                self._event_queue.put(event)

    def _parse_sim_line(self, text: str, swipe_time: str) -> CheckinEvent | None:
        parts = text.split()
        keyword = parts[0].lower()
        if keyword == "card" and len(parts) >= 2:
            return CardEvent(card_uid=parts[1].lower(), swipe_time=swipe_time)
        if keyword == "phone" and len(parts) >= 2:
            return self._make_phone_event(parts[1], swipe_time)
        if _looks_like_uid(text):
            return CardEvent(card_uid=text.lower(), swipe_time=swipe_time)
        if _looks_like_uuid(text):
            return self._make_phone_event(text, swipe_time)
        logger.warning("无法识别的模拟输入：%s", text)
        return None

    def _make_phone_event(self, student_id: str, swipe_time: str) -> PhoneEvent | None:
        try:
            # 走一遍 34 字节载荷构造 + 解析，验证与真实路径 B 同构
            raw = build_mailbox_payload(student_id, str(uuid.uuid4()))
            payload = parse_mailbox_payload(raw)
        except (ValueError, PayloadError) as exc:
            logger.warning("模拟 phone 输入非法（需合法 UUID）：%s", exc)
            return None
        return PhoneEvent(
            student_id=payload.student_id,
            idempotency_key=payload.idempotency_key,
            swipe_time=swipe_time,
            checkin_type=payload.checkin_type,
        )

    # --------------------------- 线程 B：消费 ---------------------------

    def _consume_loop(self) -> None:
        while not self._stop.is_set():
            try:
                item = self._event_queue.get(timeout=0.3)
            except queue.Empty:
                continue
            try:
                if isinstance(item, ControlEvent):
                    self._handle_control(item)
                else:
                    self._handle_checkin(item)
            except Exception:  # noqa: BLE001 —— 单条处理异常不拖垮线程
                logger.exception("处理事件出错")

    def _handle_control(self, event: ControlEvent) -> None:
        if event.kind == "roster_updated":
            self._refresh_roster()
        elif event.kind == "audio_updated":
            self._sync_audio()
        elif event.kind == "session_started":
            logger.info("场次开始：%s", event.data.get("session_id"))
        elif event.kind == "session_ended":
            logger.info("场次结束：%s", event.data.get("session_id"))

    def _handle_checkin(self, event: CheckinEvent) -> None:
        self._led.set(LedState.PROCESSING)
        body = event.to_checkin_body()
        try:
            resp: ApiResponse = self._api.post_checkin(body)
        except NetworkError as exc:
            logger.warning("上报网络失败，转离线队列：%s", exc)
            self._handle_offline(event, body)
            return
        fb = for_response(resp.ok, resp.data, resp.error_code)
        self._apply_feedback(fb)
        if fb.led == LedState.AUTH_ERROR:
            # 令牌被拒 → 作废，下次调用自动换新
            self._auth.invalidate()
        else:
            # 在线成功一次 → 顺手补传离线队列
            self._try_replay_queue()

    def _handle_offline(self, event: CheckinEvent, body: dict) -> None:
        # 契约 §6.1：POST 失败一律入队（含原始 swipe_time）
        self._queue.enqueue(body)
        student = self._roster_lookup(event)
        fb = for_offline(student)
        self._apply_feedback(fb)

    def _roster_lookup(self, event: CheckinEvent) -> dict | None:
        if isinstance(event, CardEvent):
            return self._roster.find_by_uid(event.card_uid)
        if isinstance(event, PhoneEvent):
            return self._roster.find_by_student_id(event.student_id)
        return None

    def _apply_feedback(self, fb: Feedback) -> None:
        self._led.set(fb.led)
        if fb.audio_file:
            self._audio.play_name(fb.audio_file)
        elif fb.tone is not None:
            self._audio.play_tone(fb.tone)
        if fb.broadcast_text:
            logger.info("播报文本：%s", fb.broadcast_text)
        # 保持反馈灯一小段再回待机
        self._stop.wait(FEEDBACK_HOLD_S)
        if not self._stop.is_set():
            self._led.set(LedState.STANDBY)

    # --------------------------- 离线补传 ---------------------------

    def _try_replay_queue(self) -> None:
        if self._queue.count() == 0:
            return

        def sender(body: dict):
            try:
                resp = self._api.post_checkin(body)
            except NetworkError:
                return None  # 网络未通 → 停止本轮
            return resp.ok, resp.error_code

        removed = self._queue.replay(sender)
        if removed:
            logger.info(
                "离线队列补传成功 %d 条，剩 %d 条", removed, self._queue.count()
            )

    # --------------------------- 名单 / 音频刷新 ---------------------------

    def _refresh_roster(self) -> None:
        try:
            generated_at, students = self._api.fetch_roster()
        except NetworkError as exc:
            logger.warning("刷新名单失败：%s", exc)
            return
        from .roster import save_roster

        save_roster(self._cfg.roster_path, generated_at, students)
        self._roster.replace(generated_at, students)
        logger.info("名单已刷新：%d 人", self._roster.size())

    def _sync_audio(self) -> None:
        try:
            count = self._api.sync_audio(self._cfg.audio_cache_dir)
        except NetworkError as exc:
            logger.warning("同步音频失败：%s", exc)
            return
        logger.info("音频同步完成，新下载 %d 个", count)


# ============================================================================
# 组装与入口
# ============================================================================


def _looks_like_uid(text: str) -> bool:
    if len(text) != 14:
        return False
    try:
        int(text, 16)
        return True
    except ValueError:
        return False


def _looks_like_uuid(text: str) -> bool:
    try:
        uuid.UUID(text)
        return True
    except ValueError:
        return False


def build_hardware(cfg: Config, simulate: bool):
    """构造硬件层：真实 or 假实现（simulate / 无硬件降级）。

    返回 (card_reader, mailbox_reader, led, audio)。
    """
    if simulate:
        card_reader: CardReader = FakeCardReader()
        mailbox_reader: MailboxReader = FakeMailboxReader()
        led = LoggingLedController(FakeLedBackend())
        audio = ConsoleAudioPlayer()
        return card_reader, mailbox_reader, led, audio

    # 真实硬件（仅树莓派可用，import 守卫兜底）
    from .audio.player import AudioPlayer as RealAudio
    from .led.controller import build_led_controller
    from .nfc.pn532_reader import build_card_reader
    from .nfc.st25dv import build_mailbox_reader

    card_reader = build_card_reader()
    mailbox_reader = build_mailbox_reader(gpo_pin=cfg.gpio.st25dv_gpo)
    led = build_led_controller(
        {
            "red": cfg.gpio.led_red,
            "green": cfg.gpio.led_green,
            "blue": cfg.gpio.led_blue,
            "white": cfg.gpio.led_white,
        }
    )
    audio = RealAudio(audio_output=cfg.audio_output, cache_dir=cfg.audio_cache_dir)
    return card_reader, mailbox_reader, led, audio


def bootstrap(cfg: Config, simulate: bool, config_path: str) -> RollCallDevice:
    """完整装配：认证 → 首次拉名单/音频 → 硬件 → 双线程设备。

    `config_path` = 配置文件路径，首启 enroll 成功后据此清除一次性激活码。
    """
    from .roster import load_roster, save_roster

    Path(cfg.data_dir).mkdir(parents=True, exist_ok=True)

    http = httpx.Client(timeout=10.0)
    key = DeviceKey.load_or_create(cfg.key_path)
    auth = AuthManager(cfg.device_id, key, cfg.server_url, http)

    # 首启激活（契约 §2.2）
    if cfg.enroll_code:
        logger.info("首启：用激活码 enroll…")
        auth.enroll(cfg.enroll_code)
        # 激活成功后清除配置里的一次性激活码（契约 §10）
        try:
            config_mod.clear_enroll_code(config_path)
        except Exception:  # noqa: BLE001
            logger.warning("清除 enroll_code 失败（不阻断启动）")

    api = ApiClient(cfg.server_url, auth, http, fw_version=cfg.fw_version)

    # 首次拉名单 + 音频（失败不阻断：用本地缓存 / 空名单起步）
    roster = load_roster(cfg.roster_path)
    try:
        generated_at, students = api.fetch_roster()
        save_roster(cfg.roster_path, generated_at, students)
        roster.replace(generated_at, students)
    except (NetworkError, AuthError) as exc:
        logger.warning("首次拉名单失败，用本地缓存（%d 人）：%s", roster.size(), exc)
    try:
        api.sync_audio(cfg.audio_cache_dir)
    except (NetworkError, AuthError) as exc:
        logger.warning("首次同步音频失败：%s", exc)

    card_reader, mailbox_reader, led, audio = build_hardware(cfg, simulate)
    offline_queue = OfflineQueue(cfg.queue_db_path)

    device = RollCallDevice(
        cfg=cfg,
        card_reader=card_reader,
        mailbox_reader=mailbox_reader,
        led=led,
        audio=audio,
        api=api,
        auth=auth,
        offline_queue=offline_queue,
        roster=roster,
        ws=None,
        simulate=simulate,
    )
    # WS 需要 device.on_ws_event 回调，故最后构造
    ws = WsClient(cfg.ws_url, auth, device.on_ws_event, fw_version=cfg.fw_version)
    device._ws = ws
    return device


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tomoshibi 点呼机主程序")
    parser.add_argument(
        "--config",
        default="config/config.json",
        help="配置文件路径（默认 config/config.json）",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="无硬件模拟模式：stdin 模拟刷卡，LED/音频降级为控制台打印",
    )
    parser.add_argument("--log-level", default="INFO", help="日志级别（默认 INFO）")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    try:
        cfg = config_mod.load_config(args.config)
    except config_mod.ConfigError as exc:
        logger.error("配置加载失败：%s", exc)
        return 2

    try:
        device = bootstrap(cfg, simulate=args.simulate, config_path=str(args.config))
    except (AuthError, config_mod.ConfigError) as exc:
        logger.error("启动装配失败：%s", exc)
        return 1

    def _signal_handler(signum, _frame):
        logger.info("收到信号 %s，准备停机", signum)
        device.request_stop()

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    device.start()
    device.wait()
    device.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
