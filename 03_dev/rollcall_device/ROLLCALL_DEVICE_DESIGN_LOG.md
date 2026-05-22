# Tomoshibi 点呼机 · 设计 + v1.0 实装档案

> **作用**：点呼机（roll call device,跑在 Raspberry Pi 3A+ 上的 Python 程序）端的设计权威源。对称 iOS 的 `IOS_DESIGN_LOG.md` / Web 的 `WEB_DESIGN_LOG.md` / 后端的 `BACKEND_DESIGN_LOG.md` —— 5 端各一个档案。
>
> **建立**：2026-05-08（骨架）
> **范围**：v1.0 P0 — 读卡签到 / 动态贴纸 nonce 写入 / LED 反馈 / 日语播报 / 调后端
>
> ⚠️ **实装进度速查表（2026-05-21 A-027 / A-029 加）**
>
> | 层 | 进度 | 说明 |
> |---|---|---|
> | 设计文档（本文） | ✅ 100% | 226 行设计，含主循环 / 模块 / GPIO 草案 |
> | 硬件采购 | ⏳ 0% | 5-08 选型定稿，未下单 |
> | `src/` 代码 | ⏳ 0% | `main.py` 是 9 行 placeholder；`nfc/` / `api/` / `led/` / `audio/` 全空 `__init__.py` |
> | 端到端跑通 | ⏳ 0% | 依赖 Pi 实物 + backend ECDSA 验签实装（A-010） |
>
> **agent 阅读顺序**（两层结构）：
> 1. **共用层（必读）**：`02_design/system_features.md` —— 角色 / 数据模型 / R1-R4 硬约束
> 2. **物理层（必读）**：`02_design/hardware_design.md` —— Pi 3A+ 选型 / PN532 / ST25DV / 接线 / BOM
> 3. **专属层（本文）**：点呼机软件实装层 —— 程序架构 / GPIO 分配 / 启动 / 错误处理
>
> **其他权威源**：
> - `01_specs/rollcall/RollCall_Spec.md` —— 点呼业务规则
> - `02_design/flow_design.md` —— 端到端流程（路径 A 卡 / 路径 B iOS+Android）

---

## 0. 文档使用方法

- 实装时 → 从 §1 读到 §3 拿全局,再按 §5 模块顺序逐个写代码
- itsuki 来 review 时 → 跳 §10「待 itsuki 拍板」
- 决策标记：
  - ✅ **已定** = 上游真值或 itsuki 明示
  - 🟡 **CC 假设** = 可直接按此实装,但 itsuki 有否决权
  - ⏳ **待拍板** = 必须 itsuki 决定才动手

---

## 1. 技术栈与启动条件

### 1.1 技术栈（待 itsuki 拍板细节,先列 CC 推荐 ⏳）

| 层 | 选型 | 出处 |
|---|---|---|
| 语言 | **Python 3.11+** | itsuki 学习路径 + Pi OS 默认 |
| OS | **Raspberry Pi OS (Bookworm,64-bit)** | 🟡 CC 推荐（官方默认 + 最新 Debian base）|
| NFC 读卡（PN532） | `nfcpy` 或 `Adafruit-PN532` 库 | ⏳ §10-D1 待 itsuki 决定 |
| ST25DV 写 nonce | `smbus2` Python 库 + 自写底层 I2C | ⏳ §10-D2（无现成 Python 库,要 port 或自写）|
| HTTP 调后端 | `httpx`（async）| 🟡 CC 推荐 |
| WebSocket | `websockets` 库 | 🟡 CC 推荐 |
| TTS（日语播报） | `pyttsx3` 或预录音频 + `pygame.mixer` | ⏳ §10-D3 待拍板 |
| LED 控制 | `gpiozero` | 🟡 CC 推荐（最简）|
| 日志 | `structlog` JSON 格式 | 🟡 CC 推荐 |
| 进程守护 | `systemd` unit | 🟡 CC 推荐（Pi OS 标配）|
| 测试 | `pytest`（mock 硬件层）| 🟡 CC 推荐 |

### 1.2 启动前提

> **2026-05-22 banner — 采购渠道方向反转**：原 2026-05-08 itsuki 复核的中国海运清单（11 件 ¥381 RMB 含 Pi 3A+ / PN532 V3 / ST25DV16K × 2 / NTAG215 × 50 / LED 5 色 / 小音响 / 面包板 / 杜邦线 / 电源 / 透明壳）在 5-12~16 之间走中国海运被海关查扣全没。itsuki 5-22 拍板撤回中国海运渠道，改日本本地买（详见 `02_design/hardware_design.md §5.1' 新方向` + AC 素材 `05_logs/raw/2026-05-22.md`）。6 类硬件全部待重新选型 ⏳。

- 🔴 **5-22 撤回**：原中国海运清单 11 件（5-08 复核版）作废 — 详见 `hardware_design.md §5.1 ❌`
- ⏳ **日本本地重新选型 6 类硬件**：Pi 3A+（或升级 Pi 4 / Pi 5）/ PN532 V3 红板 / ST25DV16K × 2 / NTAG215 × 50 / LED 5 色 + 杜邦线 + 面包板 / USB 小音响 + 透明壳 + 风扇 + 5V 电源 — 渠道候选见 `hardware_design.md §5.1'`
- ⏳ 日本本地配件实物下单 + 到货
- ⏳ Pi OS 装好 + SSH 通
- ⏳ 后端 API 可达（v1 backend 上线后）

### 1.3 起点

**从零写 Python**（demo 期没有点呼机代码,4-28 demo 是 iPhone Shortcuts + Flask 后端 mock）。

---

## 2. 硬件接线（GPIO 分配）⏳

> **B-035 (2026-05-21) 修复**: 单一真值 = `hardware_design.md §2.4.1`（已落 GPIO 数字 + 新增白色 LED = GPIO 23）。本表跟 hardware_design.md §2.4 同步；如本表跟 hardware_design 漂，**以 hardware_design.md 为准**。
>
> 实物到货后接线图待绘制，本表为分配预留。

GPIO 分配（已对齐 `hardware_design.md §2.4.1`）：

| 模块 | 接 Pi 引脚 | 协议 |
|---|---|---|
| **PN532 NFC 读卡** | SPI(GPIO 8/9/10/11)| SPI 模式（I2C 在 Pi 上不稳,推荐 SPI 见 §10-D4）|
| **ST25DV16K 动态贴纸** | I2C(GPIO 2/3) | I2C 默认总线,Pi 写 nonce |
| **LED 红** | GPIO 17 | 数字输出 |
| **LED 绿** | GPIO 27 | 数字输出 |
| **LED 蓝** | GPIO 22 | 数字输出 |
| **LED 白** | GPIO 23 | 数字输出（B-035 新加白色，套装 5 色之一） |
| **风扇** | 5V + GND | 直供电（不走 GPIO 控制）|
| **USB 小音响** | USB 2.0 + 3.5mm 音频口 | USB 取电 + 音频走模拟口 |

参考：02_design/hardware_design.md §2

---

## 3. 程序架构

### 3.1 主循环（伪代码）

```
main.py:
  init: GPIO + NFC + Audio + API client + LED 状态机
  state = IDLE  # 待机

  while True:
    if state == IDLE:
      # 蓝灯常亮（待机）
      uid = nfc.read_card(timeout=1s)  # 非阻塞,1s 超时
      if uid:
        state = SUBMITTING
        led.flash_blue()  # 处理中

    elif state == SUBMITTING:
      result = api.submit_checkin(uid, device_id, timestamp)
      if result.ok:
        state = SUCCESS
      else:
        state = FAIL

    elif state == SUCCESS:
      led.green()
      audio.play(jp_tts(f"{name}さん、お帰りなさい"))
      sleep(2s)
      state = IDLE

    elif state == FAIL:
      led.red()
      audio.play(jp_tts(error_msg))
      sleep(2s)
      state = IDLE

  # 后台线程：每 10s 写一次新 nonce 到 ST25DV
  nonce_writer_thread.start()
```

### 3.2 模块职责

| 模块 | 职责 | 文件 |
|---|---|---|
| `src/main.py` | 入口 + 主循环 + 状态机 + 信号处理 | `main.py` |
| `src/nfc/` | PN532 SPI 封装 + ST25DV I2C nonce 写入 | `pn532.py` / `st25dv.py` |
| `src/audio/` | 日语 TTS / 播报队列（避免并发播放冲突）| `tts.py` / `player.py` |
| `src/led/` | LED GPIO 封装 + 状态机映射 | `led.py` |
| `src/api/` | 后端 HTTP / WebSocket 客户端 + 重试 | `client.py` |

---

## 4. 模块设计（待实装）

### 4.1 NFC 模块（§10-D1 + D2 拍板后写）

⏳

### 4.2 Audio 模块（§10-D3 拍板后写）

⏳

### 4.3 LED 状态机

⏳

### 4.4 API 客户端

⏳

---

## 5. 启动 / 部署

### 5.1 systemd unit（草稿）

```ini
# /etc/systemd/system/tomoshibi-rollcall.service
[Unit]
Description=Tomoshibi 点呼机主程序
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/rollcall_device
ExecStart=/usr/bin/python3 src/main.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 5.2 部署 SOP

⏳ 待写,会放 `docs/部署SOP.md`

---

## 6. 错误处理 / 故障恢复

⏳ 待 itsuki 跟管理员确认现场可恢复策略后写
（断网、卡读不出、后端 5xx、声音失败、LED 烧 等场景）

---

## 7. 测试

⏳ pytest 用 mock 替换硬件层（PN532 / ST25DV / GPIO）+ 集成测试用真硬件

---

## 8. 已知坑

| # | 坑 | 解决方向 |
|---|---|---|
| 1 | **ST25DV16K 没官方 Python 库** | 自写 I2C 寄存器读写（基于 ST 官方 datasheet）或 port Arduino 库。学习成本中等,1-2 周 |
| 2 | **PN532 在 Pi 上 I2C 不稳定** | 切 SPI 模式（板子上 I0/I1 跳线帽改）|
| 3 | **Pi 3A+ 只有 1 个 USB 口** | USB 占给小音响后,部署期只能 SSH 远程登录改 |
| 4 | **3.5mm 音频默认走 HDMI** | OS 里 `raspi-config` 改音频输出为模拟 |

---

## 9. 决策清单

⏳ 实装中累积

---

## 10. 待 itsuki 拍板（⏳）

| # | 决策点 | 选项 | CC 倾向 |
|---|---|---|---|
| D1 | PN532 用什么 Python 库 | (a) `nfcpy`(社区)/ (b) `Adafruit-PN532`(更轻)| 🟡 (b) 更简单 |
| D2 | ST25DV16K 驱动怎么解决 | (a) 自写 I2C / (b) port Arduino C++ 到 Python / (c) 干脆用 C 写一个 daemon Python 调 | 🟡 (a) 学习价值最高 |
| D3 | 日语 TTS 用什么 | (a) `pyttsx3` 离线 / (b) Google Cloud TTS 联网 / (c) 预录音频文件 | 🟡 (c) 最稳（无网无延迟）|
| D4 | PN532 接 Pi 用 SPI 还是 I2C | (a) SPI 稳 / (b) I2C 占 GPIO 少但 Pi 上不稳 | 🟡 (a) SPI |
| D5 | 是否用 WebSocket 接收老师端推送 | (a) HTTP 轮询 / (b) WebSocket | 🟡 (b) 但 v1 P0 可先 HTTP |
| D6 | 设备认证方式 | (a) 设备 ID + 密钥 / (b) JWT | 🟡 (a) 简单 |

---

## 11. 历史

- 2026-05-08：itsuki 拍板「点呼机当第 5 端」+ 联动机制升级（4 端反向规则 + 点呼机加入 system-features 联动）+ 本档案骨架建成
