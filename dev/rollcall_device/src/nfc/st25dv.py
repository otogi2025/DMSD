"""ST25DV16K 邮箱驱动（路径 B）—— smbus2 自写 I²C 驱动。

设计日志 §10-D2 拍板「无现成 Python 库、自写 I²C 寄存器读写」。本文件基于 ST 官方
datasheet **DS12448（ST25DV04K / ST25DV16K / ST25DV64K）** 编写。

⚠️ 无真实硬件，本驱动「结构对、常量尽最大努力对」。所有寄存器地址 / 位定义集中在下方
常量区并逐个附 datasheet 章节，凡不能 100% 确认的标「待硬件联调核实」。

--------------------------------------------------------------------------------
工作流程（对齐契约 §7 + 硬件设计 §2.3 核心工作模式）：
1. 启动：开 I²C 安全会话（present 默认口令 8 字节全 0x00）
2. 置 MB_MODE=1（静态系统寄存器，允许邮箱功能）+ 配 GPO 寄存器 RF_PUT_MSG 中断使能
3. 每次会话动态置 MB_CTRL_Dyn.MB_EN=1
4. 手机写入 → GPO 引脚拉低（硬件门铃）→ 读 MB_LEN_Dyn 取长度 → 从邮箱 RAM（0x2008）
   读消息 → 读完自动复位（读满长度即清 RF_PUT_MSG）
--------------------------------------------------------------------------------
"""

from __future__ import annotations

import time

from .interfaces import MailboxReader

try:
    from smbus2 import SMBus, i2c_msg  # type: ignore

    SMBUS_AVAILABLE = True
except Exception:  # noqa: BLE001
    SMBUS_AVAILABLE = False


# ============================================================================
# 常量区 —— ST25DV16K 寄存器地址 / 位定义（datasheet DS12448）
# ============================================================================

# --- I²C 设备地址（7-bit）。datasheet §6.2 "I2C device select code" ---
# E2 引脚决定：用户区 / 动态寄存器 / 邮箱走 0x53；系统配置区走 0x57。
I2C_ADDR_USER = 0x53  # 用户存储区 + 动态寄存器 + 邮箱 RAM
I2C_ADDR_SYSTEM = 0x57  # 系统配置寄存器（改前须开安全会话）

# --- 系统配置寄存器（16-bit 地址，走 I2C_ADDR_SYSTEM，改前须开会话）。datasheet §7.4 表 ---
REG_GPO = 0x0000  # GPO 配置（哪些事件驱动 GPO 引脚）
REG_MB_MODE = 0x000D  # 邮箱模式：bit0=1 允许邮箱功能（静态使能）
REG_I2C_PWD = 0x0900  # I²C 口令（present / write password），datasheet §7.5 "I2C security session"

# --- 动态寄存器（16-bit 地址，走 I2C_ADDR_USER，无需会话）。datasheet §7.6 表 ---
REG_GPO_DYN = 0x2000  # GPO 动态镜像
REG_I2C_SSO_DYN = 0x2004  # bit0=1 表示安全会话已打开
REG_IT_STS_DYN = 0x2005  # 中断状态，读后自动清零（读取即确认中断）
REG_MB_CTRL_DYN = 0x2006  # 邮箱动态控制
REG_MB_LEN_DYN = 0x2007  # 邮箱消息长度寄存器：实际长度 = 本值 + 1
ADDR_MAILBOX_RAM = 0x2008  # 邮箱 RAM 起始（共 256 字节，0x2008..0x2107）
MAILBOX_SIZE = 256

# --- GPO 寄存器位（datasheet §7.4 GPO register）---
# 待硬件联调核实：位序以 datasheet Table 为准，此处按常见 ST25DV 定义。
GPO_RF_PUT_MSG_EN = 1 << 4  # RF 写入邮箱（手机→邮箱）触发 GPO
GPO_EN = 1 << 7  # GPO 输出总使能

# --- MB_CTRL_Dyn 位（datasheet §7.6 MB_CTRL_Dyn）---
MB_CTRL_MB_EN = 1 << 0  # 邮箱动态使能
MB_CTRL_RF_PUT_MSG = 1 << 2  # RF 端已写入新消息（=有手机数据待读）

# --- IT_STS_Dyn 位（datasheet §7.6 IT_STS_Dyn）---
# 待硬件联调核实：RF_PUT_MSG 中断位，按与 GPO 寄存器对齐取 bit4。
IT_STS_RF_PUT_MSG = 1 << 4

# --- present password 命令常量（datasheet §7.5）---
PWD_DEFAULT = bytes(8)  # 出厂默认口令 = 8 字节全 0x00
PWD_VALIDATION_PRESENT = 0x09  # 校验码 0x09 = present（开会话）；0x07 = write（改口令）

# 每次 I²C 传输后给芯片的喘息时间（datasheet tW EEPROM 写周期约 5ms；读操作更短）
_WRITE_SETTLE_S = 0.006


class ST25DV(MailboxReader):
    """ST25DV16K 邮箱真实驱动（smbus2 + 16-bit 地址原始 I²C 事务）。

    smbus2 的 SMBus 高层函数只支持 8-bit 寄存器；ST25DV 用 16-bit 内存地址，故全部走
    `i2c_msg` + `i2c_rdwr` 原始事务（先写 2 字节地址，再读/写数据）。
    """

    def __init__(self, i2c_bus: int = 1, password: bytes = PWD_DEFAULT) -> None:
        if not SMBUS_AVAILABLE:
            raise RuntimeError("smbus2 不可用或非树莓派环境。开发机请用 --simulate。")
        if len(password) != 8:
            raise ValueError("ST25DV I²C 口令必须为 8 字节")
        self._bus = SMBus(i2c_bus)
        self._password = password

    # --------------------------- 底层 16-bit I²C 读写 ---------------------------

    def _read(self, dev_addr: int, mem_addr: int, length: int) -> bytes:
        """从指定设备地址的 16-bit 内存地址读 length 字节。"""
        addr_hi = (mem_addr >> 8) & 0xFF
        addr_lo = mem_addr & 0xFF
        write = i2c_msg.write(dev_addr, [addr_hi, addr_lo])
        read = i2c_msg.read(dev_addr, length)
        self._bus.i2c_rdwr(write, read)
        return bytes(read)

    def _write(self, dev_addr: int, mem_addr: int, data: bytes) -> None:
        """向指定设备地址的 16-bit 内存地址写 data。"""
        addr_hi = (mem_addr >> 8) & 0xFF
        addr_lo = mem_addr & 0xFF
        msg = i2c_msg.write(dev_addr, [addr_hi, addr_lo, *data])
        self._bus.i2c_rdwr(msg)
        time.sleep(_WRITE_SETTLE_S)

    def _read_reg(self, dev_addr: int, mem_addr: int) -> int:
        return self._read(dev_addr, mem_addr, 1)[0]

    # --------------------------- 初始化流程 ---------------------------

    def begin(self) -> None:
        """启动初始化：开会话 → 置 MB_MODE → 配 GPO → 动态开 MB_EN。"""
        self.present_password(self._password)
        self._enable_mailbox_static()
        self._configure_gpo()
        self.enable_mailbox_dynamic()

    def present_password(self, password: bytes) -> None:
        """present 口令开 I²C 安全会话（datasheet §7.5）。

        命令格式：地址 0x0900（系统区），载荷 = 口令[8] + 校验码 0x09 + 口令[8]，共 17 字节。
        成功后 I2C_SSO_Dyn.bit0 = 1。
        """
        payload = bytes(password) + bytes([PWD_VALIDATION_PRESENT]) + bytes(password)
        self._write(I2C_ADDR_SYSTEM, REG_I2C_PWD, payload)

    def session_open(self) -> bool:
        """查 I2C_SSO_Dyn.bit0 判断安全会话是否已开。"""
        return bool(self._read_reg(I2C_ADDR_USER, REG_I2C_SSO_DYN) & 0x01)

    def _enable_mailbox_static(self) -> None:
        """置系统寄存器 MB_MODE.bit0 = 1，允许邮箱功能（需已开会话）。"""
        current = self._read_reg(I2C_ADDR_SYSTEM, REG_MB_MODE)
        self._write(I2C_ADDR_SYSTEM, REG_MB_MODE, bytes([current | 0x01]))

    def _configure_gpo(self) -> None:
        """配 GPO 寄存器：使能 RF_PUT_MSG 中断 + GPO 总开关（需已开会话）。"""
        value = GPO_RF_PUT_MSG_EN | GPO_EN
        self._write(I2C_ADDR_SYSTEM, REG_GPO, bytes([value]))

    def enable_mailbox_dynamic(self) -> None:
        """动态置 MB_CTRL_Dyn.MB_EN = 1（每次会话开始时调，datasheet §7.6）。"""
        self._write(I2C_ADDR_USER, REG_MB_CTRL_DYN, bytes([MB_CTRL_MB_EN]))

    # --------------------------- 邮箱读取 ---------------------------

    def message_pending(self) -> bool:
        """查 MB_CTRL_Dyn.RF_PUT_MSG 判断邮箱是否有手机写入的新消息。"""
        ctrl = self._read_reg(I2C_ADDR_USER, REG_MB_CTRL_DYN)
        return bool(ctrl & MB_CTRL_RF_PUT_MSG)

    def read_mailbox(self) -> bytes:
        """读走邮箱消息。

        MB_LEN_Dyn 存的是「长度 - 1」（datasheet §7.6），故实际长度 = 值 + 1。
        从 0x2008 连读该长度字节。读满整条消息后 RF_PUT_MSG 自动清（datasheet 邮箱语义）。
        """
        length = self._read_reg(I2C_ADDR_USER, REG_MB_LEN_DYN) + 1
        length = max(1, min(length, MAILBOX_SIZE))
        return self._read(I2C_ADDR_USER, ADDR_MAILBOX_RAM, length)

    def reset_mailbox(self) -> None:
        """读 IT_STS_Dyn 清中断状态 + 重新动态使能邮箱，为下一个学生腾空（约 165ms 内）。"""
        # 读 IT_STS_Dyn 即清中断标志（datasheet：读操作确认并清零）
        self._read_reg(I2C_ADDR_USER, REG_IT_STS_DYN)
        self.enable_mailbox_dynamic()

    # --------------------------- MailboxReader 接口 ---------------------------

    def poll(self) -> bytes | None:
        """线程 A 调用：有新消息则读走并复位，返回原始字节；否则 None。

        注：GPO 引脚（硬件门铃）由 `MailboxGpoReader` 组合监听边沿以降低轮询频率；
        本方法用 I²C 寄存器轮询作为不依赖 GPO 接线也能工作的兜底路径。
        """
        if not self.message_pending():
            return None
        data = self.read_mailbox()
        self.reset_mailbox()
        return data

    def close(self) -> None:
        try:
            self._bus.close()
        except Exception:  # noqa: BLE001
            pass


# GPO 漏边沿兜底轮询间隔（秒）—— 未见触发标志时也按此间隔走一次 I²C 确认。
# GPO 只是「加速唤醒」，不能作唯一读条件：边沿抖动 / 上电时序 / gpiozero 回调丢失 /
# 接触不良时漏一个下降沿，邮箱载荷就永久漏读（路径 B 签到静默丢失、现场难排障）
GPO_FALLBACK_POLL_S = 1.0


class MailboxGpoReader(MailboxReader):
    """GPO 中断 + I²C 读取组合。

    GPO 引脚是开漏「门铃」：手机写入邮箱时被拉低。用 gpiozero 监听下降沿设标志位，
    `poll()` 见到标志立即走 I²C 读；未见标志时按 GPO_FALLBACK_POLL_S 间隔低频兜底
    确认（I²C 从主循环 20Hz 降到 1Hz，仍避免高频空转总线）。接线说明 §3：外部
    10kΩ 上拉到 3.3V + 代码内部上拉（PUD_UP）兜底。
    """

    def __init__(self, st25dv: ST25DV, gpo_pin: int) -> None:
        self._st25dv = st25dv
        self._triggered = False
        self._button = None
        # monotonic 时刻（不用墙钟：NTP 对时完成时墙钟会阶跃，打乱间隔计算）。
        # 初值 0 → 启动后首次 poll 即兜底一次，扫掉上电前滞留在邮箱里的载荷
        self._last_i2c = 0.0
        try:
            from gpiozero import Button  # type: ignore

            # pull_up=True 开内部上拉；GPO 拉低 → when_pressed 触发
            self._button = Button(gpo_pin, pull_up=True, bounce_time=0.02)
            self._button.when_pressed = self._on_gpo
        except Exception:  # noqa: BLE001
            # 无 GPIO 库时退化为纯 I²C 轮询（message_pending 兜底）
            self._button = None

    def _on_gpo(self) -> None:
        self._triggered = True

    def poll(self) -> bytes | None:
        if self._button is not None:
            now = time.monotonic()
            if self._triggered:
                self._triggered = False
            elif now - self._last_i2c < GPO_FALLBACK_POLL_S:
                return None
            self._last_i2c = now
        # GPO 触发 / 到达兜底时刻（或无 GPIO 时每次都试）→ 走 I²C 确认并读取
        return self._st25dv.poll()

    def close(self) -> None:
        if self._button is not None:
            try:
                self._button.close()
            except Exception:  # noqa: BLE001
                pass
        self._st25dv.close()


def build_mailbox_reader(i2c_bus: int = 1, gpo_pin: int = 24) -> MailboxReader:
    """工厂：构造并初始化真实邮箱读取器（含 GPO 监听）。"""
    st25dv = ST25DV(i2c_bus=i2c_bus)
    st25dv.begin()
    return MailboxGpoReader(st25dv, gpo_pin=gpo_pin)
