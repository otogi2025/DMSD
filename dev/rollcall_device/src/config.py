"""设备配置读取 —— 对应 `Device_Contract.md` §10 的 `config.json`。

字段全部小写蛇形，与契约示例逐字对齐。GPIO 引脚表对齐
`design/hardware_design.md §2.4.1` + `点呼机接线说明.md`（LED 低电平点亮）。

本模块只做纯数据解析与校验，无硬件依赖，可在 Mac 直接测试。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


class ConfigError(Exception):
    """配置文件缺字段 / 格式错误时抛出。"""


@dataclass(frozen=True)
class GpioConfig:
    """GPIO 引脚分配（BCM 编号）。

    LED 引脚号来自 `hardware_design.md §2.4.1`：红 17 / 绿 27 / 蓝 22 / 白 23，
    低电平点亮（5V 驱动，代码侧反逻辑，见 `led/controller.py`）。
    `st25dv_gpo` = ST25DV 邮箱「门铃」中断脚，契约 §10 取默认 GPIO24（⏳ 待硬件联调核实）。
    """

    led_red: int = 17
    led_green: int = 27
    led_blue: int = 22
    led_white: int = 23
    st25dv_gpo: int = 24


@dataclass(frozen=True)
class Config:
    """点呼机运行配置。"""

    device_id: str
    server_url: str
    ws_url: str
    key_path: str
    data_dir: str
    audio_output: str
    gpio: GpioConfig = field(default_factory=GpioConfig)
    # 一次性激活码：首启 enroll 成功后由程序清空（契约 §2.2）。可为 None（已激活的机器）。
    enroll_code: str | None = None
    # 上报心跳时携带的固件版本串（非项目语义版本号，运维自定，默认占位）。
    fw_version: str = "rollcall-device-unknown"

    @property
    def roster_path(self) -> Path:
        """本地名单缓存文件路径（离线兜底放行用，契约 §4.2）。"""
        return Path(self.data_dir) / "roster.json"

    @property
    def audio_cache_dir(self) -> Path:
        """学生姓名 wav 缓存目录（契约 §4.3 差量下载落地处）。"""
        return Path(self.data_dir) / "audio"

    @property
    def queue_db_path(self) -> Path:
        """离线队列 SQLite 文件路径（契约 §6 断网补传）。"""
        return Path(self.data_dir) / "offline_queue.sqlite3"


def load_config(path: str | Path) -> Config:
    """从 JSON 文件加载配置。缺必填字段即抛 `ConfigError`。"""
    raw_path = Path(path)
    if not raw_path.exists():
        raise ConfigError(f"配置文件不存在：{raw_path}")
    try:
        data = json.loads(raw_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"配置文件不是合法 JSON：{exc}") from exc
    return parse_config(data)


def clear_enroll_code(path: str | Path) -> None:
    """首启 enroll 成功后清除配置里的一次性激活码（契约 §10：激活后自动清除）。

    保留其余字段原样，只把 `enroll_code` 置空串。原子写。
    """
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    data["enroll_code"] = ""
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


def parse_config(data: dict) -> Config:
    """把 dict 解析成 `Config`，做必填校验。"""
    required = [
        "device_id",
        "server_url",
        "ws_url",
        "key_path",
        "data_dir",
        "audio_output",
    ]
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise ConfigError(f"配置缺少必填字段：{', '.join(missing)}")

    gpio_raw = data.get("gpio", {})
    if not isinstance(gpio_raw, dict):
        raise ConfigError("gpio 字段必须是对象")
    gpio = GpioConfig(
        led_red=int(gpio_raw.get("led_red", 17)),
        led_green=int(gpio_raw.get("led_green", 27)),
        led_blue=int(gpio_raw.get("led_blue", 22)),
        led_white=int(gpio_raw.get("led_white", 23)),
        st25dv_gpo=int(gpio_raw.get("st25dv_gpo", 24)),
    )

    return Config(
        device_id=str(data["device_id"]),
        server_url=str(data["server_url"]).rstrip("/"),
        ws_url=str(data["ws_url"]).rstrip("/"),
        key_path=str(data["key_path"]),
        data_dir=str(data["data_dir"]),
        audio_output=str(data["audio_output"]),
        gpio=gpio,
        enroll_code=(str(data["enroll_code"]) if data.get("enroll_code") else None),
        fw_version=str(data.get("fw_version", "rollcall-device-unknown")),
    )
