# Tomoshibi 点呼机 · 设计 + v1.0 实装档案

> **作用**：点呼机（roll call device,跑在 Raspberry Pi 3A+ 上的 Python 程序）端的设计权威源。对称 iOS 的 `IOS_DESIGN_LOG.md` / Web 的 `WEB_DESIGN_LOG.md` / 后端的 `BACKEND_DESIGN_LOG.md` —— 5 端各一个档案。
>
> **建立**：2026-05-08（骨架）
> **范围**：v1.0 P0 — 读卡签到（路径 A）/ 读手机写进 ST25DV 邮箱的身份数据（路径 B）/ LED 反馈 / 日语播报（后端预生成 wav 下发）/ 调后端（WebSocket + HTTP）
>
> ⚠️ **2026-06-03 架构反转**（itsuki 6-02 拍板，对齐 `hardware_design.md §2.3` + `flow_design.md §3`）：手机从「读 ST25DV」改「写 ST25DV」，点呼机从「每 10 秒写 nonce」改「被动读手机写进邮箱的数据」。连带改动散落在 §1.1 / §3 / §6 / §10，本轮已追平。本文属「点呼机架构链」（hardware_design / flow_design / 本文 / 项目心智模型），改一个必核对其余三个。
>
> ⚠️ **实装进度速查表（2026-05-21 A-027 / A-029 加）**
>
> | 层 | 进度 | 说明 |
> |---|---|---|
> | 设计文档（本文） | ✅ 100% | 226 行设计，含主循环 / 模块 / GPIO 草案 |
> | 硬件采购 | ⏳ 0% | 5-08 选型定稿，未下单 |
> | `src/` 代码 | ⏳ 0% | `main.py` 是 9 行 placeholder；`nfc/` / `api/` / `led/` / `audio/` 全空 `__init__.py` |
> | 端到端跑通 | ⏳ 0% | 依赖 Pi 实物 + 点呼机↔后端传输安全（ECDSA 验签降级 v1.1 可选，见 flow_design §5） |
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
| ST25DV 读 Mailbox 邮箱 | `smbus2` Python 库 + 自写底层 I2C | ⏳ §10-D2（无现成库；2026-06-03 反转：从「写 nonce」改「读手机写进来的邮箱数据」）|
| HTTP 调后端 | `httpx`（async）| ✅ 已定 — 常规请求：上报签到 / 下载音频 wav / 历史查询 |
| WebSocket | `websockets` 库 | ✅ 已定 — 后端推指令：判定结果 / 播放 / 亮灯 / 删音频；**必写断线自动重连（见 §6）** |
| 日语播报 | ~~本地合成 TTS~~ → **后端预生成 wav 下发**，点呼机只用 `aplay` 播放 | ✅ 已定（§10-D3 拍板 c — 512MB 跑不动本地合成）|
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
| **ST25DV16K（手机写入邮箱）** | I2C(GPIO 2/3) + GPO 中断引脚(GPIO 待定) | I2C 读 Mailbox 邮箱 + GPO 中断监听（旧「Pi 写 nonce」已废）|
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
  init: GPIO + PN532(SPI 读卡) + ST25DV(I2C，开 Mailbox 邮箱 + GPO 中断)
        + Audio + API(WebSocket + HTTP) + LED 状态机
  queue = 线程安全队列

  # ── 线程 A：硬件采集（只管读，读到丢队列，立刻释放芯片）──
  def thread_A():
    while True:
      uid = pn532.read_card(timeout=0.5s)          # 路径 A：实体卡
      if uid:
        queue.put({type:"card", uid, swipe_time: ntp_now()})
      if st25dv.gpo_triggered():                   # 路径 B：手机写进邮箱（GPO 门铃）
        data = st25dv.read_mailbox()
        st25dv.clear_mailbox()                     # 立刻清空，不挡下一个学生（~165ms）
        queue.put({type:"phone", data, swipe_time: ntp_now()})

  # ── 线程 B：网络 + 反馈（处理队列，不阻塞采集）──
  def thread_B():
    while True:
      item = queue.get()
      led.flash_blue()                             # 处理中
      try:
        result = api.post_checkin(item)            # HTTP 上报，带点呼机盖的 swipe_time
      except NetworkError:                         # 断网降级（见 §6）
        offline_log.append(item)
        led.green(); play_wav(local_name(item)); continue
      if result.ok:
        led.green()
        play_wav(f"{result.student_id}.wav")       # 播后端下发的全名 wav，新声音掐断老声音
      else:
        led.red(); play_wav("error.wav")

  # ── WebSocket 长连接：后端主动推指令（判定 / 播放 / 亮灯 / 删音频）──
  #     必带断线自动重连（见 §6）；旧的「每 10s 写 nonce 线程」已删
  start(thread_A); start(thread_B); start(ws_listener)
```

### 3.2 模块职责

| 模块 | 职责 | 文件 |
|---|---|---|
| `src/main.py` | 入口 + 双线程（采集 / 网络反馈）+ 队列 + 信号处理 | `main.py` |
| `src/nfc/` | PN532 SPI 读卡 + ST25DV I2C 读 Mailbox 邮箱 + GPO 中断监听 | `pn532.py` / `st25dv.py` |
| `src/audio/` | 播放后端下发的 wav（`aplay`）+ 播报队列（新声音掐断老声音）| `player.py` |
| `src/led/` | LED GPIO 封装 + 状态机映射 | `led.py` |
| `src/api/` | WebSocket（收后端指令 + 断线自动重连）+ HTTP（上报签到 / 下载 wav）+ 离线缓冲 | `client.py` |

### 3.3 点呼机↔后端通讯设计（2026-06-03 itsuki 拍板 D5）

两种通讯各司其职：

| 通道 | 干什么 | 为什么用它 |
|---|---|---|
| **WebSocket**（长连接）| 后端**主动推**给点呼机：判定结果 / 「播 `10023.wav`」/ 亮绿灯 / 删某学生音频 | 后端判定后要立刻命令点呼机亮灯放音，长连接零延迟 |
| **HTTP**（一问一答）| 点呼机**主动发**：上报签到 / 下载音频 wav / 历史查询 | 不要求极致实时，开发最快最稳 |

**断线自动重连（必做，不能省）**：宿舍 Wi-Fi 会闪断。WebSocket 长连接一旦断了又没重连逻辑，点呼机就再也收不到后端指令 = 机器变哑巴。所以 `src/api/client.py` 必须写一套断线自动重连（断开 → 退避重试 → 连上后补订阅）。闪断期间的签到走**离线降级**（见 §6）。

**音频文件生命周期**（后端管，点呼机只存只播）：学号当文件名（如 `10023.wav`）→ 新生注册时后端生成 + HTTP 下发到点呼机本地 → 点呼时后端 WebSocket 发 `{action:"play", file:"10023.wav"}` → 学生毕业后端发 `{action:"delete", file:"10023.wav"}` 远程删 → SD 卡坏了用「同步全部语音」一键重灌。

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

### 6.1 点呼机↔后端断网 → 离线降级 ✅（2026-06-03 itsuki 拍板）

宿舍 Wi-Fi 闪断时，不能让学生堵在门口。降级策略：

1. WebSocket 断开 → `src/api/client.py` 启动断线自动重连（退避重试）。
2. 重连期间学生照样签到：点呼机比对**本地缓存的学生名单**（SD 卡里），学号 / 卡 UID 存在就**直接放绿灯 + 播报**，先让学生通过。
3. 这些签到先写**本地离线日志**（带点呼机盖的 swipe_time 时间戳）。
4. 网络恢复 → 把离线日志**批量补传**后端，后端按 swipe_time 补判定。

> 核心：点呼队伍物理上绝不被网络问题堵住。判定可以晚一点（补传后算），但人先过。

### 6.2 其他故障（待 itsuki 跟管理员确认现场策略后细化）

⏳ 卡 / 邮箱读不出、后端 5xx、声音失败、LED 烧 等场景。

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
| D3 | 日语播报怎么出声 | ~~(a) pyttsx3 本地 / (b) 云 TTS / (c) 预录~~ → **拍板：后端预生成 wav 下发，点呼机 `aplay` 播放** | ✅ 已定（6-03 — 512MB 跑不动本地 TTS；学号当文件名如 `10023.wav`）|
| D4 | PN532 接 Pi 用 SPI 还是 I2C | (a) SPI 稳 / (b) I2C 占 GPIO 少但 Pi 上不稳 | 🟡 (a) SPI |
| D5 | 点呼机↔后端用 HTTP 还是 WebSocket | ~~二选一~~ → **拍板：两个都用，各司其职** | ✅ 已定（6-03）— WebSocket 推指令 + HTTP 常规请求；**断线自动重连必写 → §6** |
| D6 | 设备认证方式 | (a) 设备 ID + 密钥 / (b) JWT | 🟡 (a) 简单 |

---

## 11. 历史

- 2026-05-08：itsuki 拍板「点呼机当第 5 端」+ 联动机制升级（4 端反向规则 + 点呼机加入 system-features 联动）+ 本档案骨架建成
