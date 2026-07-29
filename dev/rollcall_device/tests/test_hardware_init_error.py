"""硬件初始化失败要给人话提示，不能甩栈就崩（device#2）。

组装现场排错的核心诉求：看一眼日志就知道是哪块硬件、该查哪根线，
而不是被 systemd 每 5 秒一次的重启刷屏淹没。
"""

import json

from src import main as main_mod
from src.config import Config


def _cfg(tmp_path) -> Config:
    return Config(
        device_id="test-dev",
        server_url="http://127.0.0.1:1",
        ws_url="ws://127.0.0.1:1",
        key_path=str(tmp_path / "key"),
        data_dir=str(tmp_path / "data"),
        audio_output="plughw:1,0",
    )


def test_真硬件在非树莓派上起不来时抛带提示的异常(tmp_path):
    """Mac 上没有读卡器，走真实硬件分支必然失败 —— 第一块挂的是 PN532。"""
    try:
        main_mod.build_hardware(_cfg(tmp_path), simulate=False)
    except main_mod.HardwareInitError as exc:
        assert exc.part == "PN532 读卡器（SPI）"
        assert "SPI" in exc.hint  # 提示里指明了该查哪个开关
    else:
        raise AssertionError("非树莓派上构造真实硬件竟然没报错")


def test_跳过读卡器后PN532不再被构造(tmp_path, monkeypatch):
    """`--skip-card-reader`（组装期 PN532 未焊）：读卡器整块不碰，第一块挂的变成 ST25DV。

    伪造 pn532_reader 模块有两个作用：① 让非树莓派上的 import 守卫放行，跑得到跳过分支；
    ② 一旦跳过失效、真去构造读卡器，就当场炸出断言错误。
    """
    import sys
    import types

    fake = types.ModuleType("src.nfc.pn532_reader")

    def _must_not_be_called():
        raise AssertionError("skip_card_reader=True 时不该构造 PN532")

    fake.build_card_reader = _must_not_be_called
    monkeypatch.setitem(sys.modules, "src.nfc.pn532_reader", fake)

    try:
        main_mod.build_hardware(_cfg(tmp_path), simulate=False, skip_card_reader=True)
    except main_mod.HardwareInitError as exc:
        # 开发机没有 I²C 总线 —— 挂在 ST25DV 恰好证明 PN532 那步被整块跳过了
        assert exc.part == "ST25DV 手机贴芯片（I²C）"
    else:
        raise AssertionError("开发机上构造真实 ST25DV 竟然没报错")


def test_跳过读卡器的开关从命令行传得到装配层(tmp_path, monkeypatch):
    """开关接线检查：`--skip-card-reader` 必须一路传到 bootstrap，中途丢了等于没做。"""
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(
        json.dumps(
            {
                "device_id": "test-dev",
                "server_url": "http://127.0.0.1:1",
                "ws_url": "ws://127.0.0.1:1",
                "key_path": str(tmp_path / "key"),
                "data_dir": str(tmp_path / "data"),
                "audio_output": "plughw:1,0",
            }
        ),
        encoding="utf-8",
    )
    captured: dict[str, bool] = {}

    def _capture(_cfg_arg, simulate, config_path, skip_card_reader=False):
        captured["skip"] = skip_card_reader
        raise main_mod.HardwareInitError("停在这里就够了", "无", RuntimeError("stop"))

    monkeypatch.setattr(main_mod, "bootstrap", _capture)

    assert main_mod.main(["--config", str(cfg_path), "--skip-card-reader"]) == 3
    assert captured["skip"] is True

    captured.clear()
    assert main_mod.main(["--config", str(cfg_path)]) == 3
    assert captured["skip"] is False  # 不带参数时必须保持「硬件缺一不可」的默认


def test_模拟模式不受影响(tmp_path):
    card, mailbox, led, audio = main_mod.build_hardware(_cfg(tmp_path), simulate=True)
    assert card is not None and mailbox is not None
    assert led is not None and audio is not None


def test_主程序把硬件失败翻译成退出码3并打印提示(tmp_path, monkeypatch, caplog):
    """退出码 3 = systemd 的 RestartPreventExitStatus 认的「别再重启了」。"""
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(
        json.dumps(
            {
                "device_id": "test-dev",
                "server_url": "http://127.0.0.1:1",
                "ws_url": "ws://127.0.0.1:1",
                "key_path": str(tmp_path / "key"),
                "data_dir": str(tmp_path / "data"),
                "audio_output": "plughw:1,0",
            }
        ),
        encoding="utf-8",
    )

    def _boom(*_args, **_kwargs):
        raise main_mod.HardwareInitError(
            "PN532 读卡器（SPI）", "检查 SPI 是否已启用", RuntimeError("no spi")
        )

    monkeypatch.setattr(main_mod, "bootstrap", _boom)

    with caplog.at_level("ERROR"):
        code = main_mod.main(["--config", str(cfg_path)])

    assert code == 3
    logged = "\n".join(r.getMessage() for r in caplog.records)
    assert "PN532 读卡器（SPI）" in logged
    assert "检查 SPI 是否已启用" in logged
    assert "--simulate" in logged
