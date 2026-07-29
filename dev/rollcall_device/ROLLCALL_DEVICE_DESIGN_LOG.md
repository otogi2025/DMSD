# Tomoshibi 点呼机 · 设计 + v1.0 实装档案

> **作用**：点呼机（roll call device,跑在 Raspberry Pi 3A+ 上的 Python 程序）端的设计权威源。对称 iOS 的 `IOS_DESIGN_LOG.md` / Web 的 `WEB_DESIGN_LOG.md` / 后端的 `BACKEND_DESIGN_LOG.md` —— 5 端各一个档案。
>
> **建立**：2026-05-08（骨架）
> **范围**：v1.0 P0 — 读卡签到（路径 A）/ 读手机写进 ST25DV 邮箱的身份数据（路径 B）/ LED 反馈 / 日语播报（后端预生成 wav 下发）/ 调后端（WebSocket + HTTP）
>
> ⚠️ **2026-06-03 架构反转**（itsuki 6-02 拍板，对齐 `hardware_design.md §2.3` + `flow_design.md §3`）：手机从「读 ST25DV」改「写 ST25DV」，点呼机从「每 10 秒写 nonce」改「被动读手机写进邮箱的数据」。连带改动散落在 §1.1 / §3 / §6 / §10，本轮已追平。本文属「点呼机架构链」（hardware_design / flow_design / 本文 / 项目骨架文档），改一个必核对其余三个。
>
> ⚠️ **实装进度速查表（2026-05-21 A-027 / A-029 加）**
>
> | 层 | 进度 | 说明 |
> |---|---|---|
> | 设计文档（本文） | ✅ 100% | 226 行设计，含主循环 / 模块 / GPIO 草案 |
> | 硬件采购 | ✅ 已下单 | 2026-06-04 日本本地三家（Amazon / Switch Science / 秋月電子）全部下单，订单截图存档于 `点呼机采购清单.html` + `采购截图/`。到货后接线 |
> | `src/` 代码 | ✅ 全实装（2026-07-17） | 全模块落地（读卡 / 邮箱驱动 / 认证 / 上报 / WS / 离线队列 / LED / 播报 / `--simulate`），75 条 pytest Mac 全绿（mock 硬件层）；模块指针见 §4 |
> | 端到端跑通 | 🟡 软件链路已通 | 后端设备接入已实装（`Device_Contract.md` 契约 + `dev/backend/v1` devices 路由）；剩硬件到货联调（ST25DV 寄存器位 / PN532 跳线 / GPO 引脚 / 音频设备串——代码内已逐处标「待硬件联调核实」）|
>
> **agent 阅读顺序**（两层结构）：
> 1. **共用层（必读）**：`design/system_features.md` —— 角色 / 数据模型 / R1-R4 硬约束
> 2. **物理层（必读）**：`design/hardware_design.md` —— Pi 3A+ 选型 / PN532 / ST25DV / 接线 / BOM
> 3. **专属层（本文）**：点呼机软件实装层 —— 程序架构 / GPIO 分配 / 启动 / 错误处理
>
> **其他权威源**：
> - `specs/rollcall/RollCall_Spec.md` —— 点呼业务规则
> - `design/flow_design.md` —— 端到端流程（路径 A 卡 / 路径 B iOS+Android）

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
| OS | **Raspberry Pi OS (Legacy, 64-bit) Lite**（Bookworm）| ✅ 2026-07-27 实机烧卡确认（Debian 12 / aarch64 / Python 3.11.2）。选 Lite = Pi 3A+ 只有 512MB 且无显示器；选 Legacy = Imager 第一屏已换成新一代 Trixie，Legacy 这条才是本项目声明的目标环境 Bookworm |
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

> **采购历程（已闭环）**：原 2026-05-08 的中国海运清单（11 件 ¥381 RMB）在 5-12~16 走中国海运被海关查扣全没 → itsuki 5-22 拍板撤回中国海运、改日本本地买 → 5-27 日本本地选型定稿（4 家：秋月電子 / Switch Science / Amazon Japan / ヨドバシ.com）→ **2026-06-04 三家全部下单完成**。完整渠道 / 价格 / 订单截图见 `design/hardware_design.md §5.1'` + `点呼机采购清单.html` + `采购截图/`。

- ✅ **日本本地选型定稿**（2026-05-27）：Pi 3A+ / PN532 V3 红板 / ST25DV16K × 2 / NTAG215 × 50 / LED 5 色 + 杜邦线 + 面包板 / USB 小音响 + 风扇 + 5V 电源 + 外壳 — 详见 `hardware_design.md §5.1'`
- ✅ **日本本地实物下单**（2026-06-04）：Amazon / Switch Science / 秋月電子 三家全部下单
- ⏳ 实物到货 + 接线组装
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
| **LED 白** | GPIO 23 | 数字输出（2026-06-04 改 **5V 驱动 / 低电平=亮**：裸 LED 长腿→220Ω→5V，短腿→GPIO，代码反逻辑。详见 hardware_design §2.4.1 + 接线说明 §4）|
| **风扇** | 5V + GND | 直供电（不走 GPIO 控制）|
| **USB 小音响** | USB 2.0 + 3.5mm 音频口 | USB 取电 + 音频走模拟口 |

参考：design/hardware_design.md §2

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

## 4. 模块设计（2026-07-17 全实装 — 本节改为实装指针）

### 4.1 NFC 模块

- `src/nfc/pn532_reader.py` — PN532 **SPI** 读 NTAG215 UID（7 字节 → 14 位小写 hex），import 守卫（无硬件库时可测）
- `src/nfc/st25dv.py` — smbus2 自写 ST25DV16K 驱动：I2C 用户区 0x53 / 系统区 0x57，present 默认口令开安全会话 → MB_MODE=1 + GPO(RF_PUT_MSG) → 每会话 MB_CTRL_Dyn.MB_EN；GPO 中断 → 读 MB_LEN_Dyn + 邮箱 RAM(0x2008) → 自复位。寄存器常量集中附 datasheet DS12448 章节注释，不确定位标「待硬件联调核实」
- `src/nfc/payload.py` — 34 字节载荷解析（`Device_Contract.md §7` 双端对齐）；`src/nfc/debounce.py` — 同 UID 2 秒防抖

### 4.2 Audio 模块

- `src/audio/player.py` — `aplay` 子进程播 `{学号}.wav`（缺失回退通用提示音；新声掐断老声）；内置提示音 `assets/tone_*.wav`（`tools/gen_tones.py` 纯标准库生成）

### 4.3 LED 状态机

- `src/led/controller.py` — gpiozero 低电平点亮（红17/绿27/蓝22/白23）；状态映射按契约 §9（黄灯无实灯 → 红+绿同亮近似）

### 4.4 API 客户端

- `src/api/auth.py` — Ed25519 密钥（0600）+ enroll + 令牌换取（契约 §2.3 签名串）+ 过半续期
- `src/api/client.py` — httpx：device-checkins / roster / 音频 manifest 差量下载 / heartbeat；`src/api/envelope.py` — `{ok,data}` 信封解包
- `src/api/ws.py` — websockets 长连接，指数退避 1s→60s，心跳 30s，4 类推送分派
- 配套：`src/offline/queue.py`（SQLite 离线队列，契约 §6 补传语义）/ `src/roster.py`（断网本地放行名单）/ `src/feedback.py`（契约 §9 反馈纯函数）/ `src/events.py` / `src/timeutil.py`（JST）/ `src/config.py`（契约 §10）

---

## 5. 启动 / 部署

### 5.1 systemd unit（草稿）

> ⚠️ 下面只是设计阶段的示意骨架，**实际投产的单元文件以 `config/tomoshibi-rollcall.service` 为准**
> （那份多了对时依赖 `time-sync.target`、`RestartPreventExitStatus=3`、`StateDirectory=tomoshibi`）。

```ini
# /etc/systemd/system/tomoshibi-rollcall.service
[Unit]
Description=Tomoshibi 点呼机主程序
After=network-online.target time-sync.target
Wants=network-online.target time-sync.target

[Service]
Type=simple
User=rollcall-1
WorkingDirectory=/home/rollcall-1/rollcall_device
# 走 venv 里的 python，用 -m 跑 src 包（相对 import 需要）
ExecStart=/home/rollcall-1/rollcall_device/.venv/bin/python -m src.main --config /home/rollcall-1/rollcall_device/config/config.json
Restart=on-failure
RestartSec=5
RestartPreventExitStatus=3
StateDirectory=tomoshibi

[Install]
WantedBy=multi-user.target
```

### 5.2 部署 SOP

✅ 已写（2026-07-17）→ `docs/部署SOP.md` — 烧卡 → raspi-config 开 SPI/I²C + 音频切 3.5mm → venv 装依赖 → 填 config → enroll 激活 + 首次干跑 → systemd 开机自启,附 8 条常见故障对照表。

组装侧配套（2026-07-19 硬件到货时加）→ `docs/组装联调清单.md` — 从拆快递到第一次刷卡成功的 5 阶段路线图 + 每步验收标准 + 焊接教学 + 万用表通断验焊法。三份分工：接线说明 = 查表（哪根线接哪根针）/ 部署SOP = 命令流水（软件怎么装）/ 组装联调清单 = 顺序与验收（先做什么、怎么算过关）。

---

## 6. 错误处理 / 故障恢复

### 6.1 点呼机↔后端断网 → 离线降级 ✅（2026-06-03 itsuki 拍板）

宿舍 Wi-Fi 闪断时，不能让学生堵在门口。降级策略：

1. 双线程里的**线程 B（网络反馈线程）**检测到 WebSocket 断开 → 切离线模式，同时 `src/api/client.py` 启动断线自动重连（退避重试）。
2. 重连期间学生照样签到：点呼机比对**本地缓存的学生名单**（SD 卡里），学号 / 卡 UID 存在就**直接放绿灯 + 播报**，先让学生通过。
3. 这些签到先写**本地离线日志**（带点呼机盖的 swipe_time 时间戳）。
4. 网络恢复 → 把离线日志**批量补传**后端，后端按 swipe_time 补判定。

> 核心：点呼队伍物理上绝不被网络问题堵住。判定可以晚一点（补传后算），但人先过。

**老师侧同步接管（2026-06-04 itsuki 拍板）**：点呼机断网时它自己通知不了后端 / 老师（都断网了）。所以「老师平板告警」靠**后端**发现长连接断、再推给老师网页（见 `BACKEND_DESIGN_LOG.md §5.8` + `WEB_DESIGN_LOG.md §5.8A`）：老师平板弹「点呼机已离线」→ 老师确认 → 进手动点呼模式逐个点学生状态。点呼机这端照常本地放行 + 记日志，网络恢复后补传；补传数据若与老师手动判定撞同一学生，默认老师手动优先。

### 6.2 其他故障（待 itsuki 跟管理员确认现场策略后细化）

⏳ 卡 / 邮箱读不出、后端 5xx、声音失败、LED 烧 等场景。

---

## 7. 测试

✅ pytest 75 条（2026-07-17）：mock 硬件层（`src/nfc/interfaces.py` 抽象 + Fake 实现）+ httpx MockTransport，Mac 可全跑（`.venv` + `requirements-dev.txt`）。覆盖：载荷解析 / 认证签名串 / 离线队列补传语义 / 状态机主流程 / LED 对照表 / roster 放行 / 防抖 / WS 退避。集成测试用真硬件 ⏳ 等到货；无硬件联调后端用 `python -m src.main --simulate`（stdin 模拟刷卡）。

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

- **D1 落地（2026-07-17）**：PN532 库选 `adafruit-circuitpython-pn532` + Blinka——SPI 接法下 `nfcpy` 不支持 SPI，唯一可选项（硬约束，非偏好）
- **D2 落地（2026-07-17）**：ST25DV 驱动走 (a) smbus2 自写——16-bit 内存地址用 `i2c_msg` + `i2c_rdwr` 原始事务
- **黄灯硬件取舍（2026-07-17）**：无黄色 LED 实灯，`SESSION_NOT_RUNNING` 用红+绿同亮近似
- **判定语义对齐（2026-07-17）**：`TIMEOUT` 随「迟到无截止」拍板（spec commit `dda0b3d`）删除——结束后签到归 `SESSION_NOT_RUNNING`，离线补传出队不重试

---

## 10. 待 itsuki 拍板（⏳）

| # | 决策点 | 选项 | CC 倾向 |
|---|---|---|---|
| D1 | PN532 用什么 Python 库 | ~~(a) `nfcpy` / (b) `Adafruit-PN532`~~ → **落地 (b)**（nfcpy 不支持 SPI，硬约束） | ✅ 已定（7-17，见 §9）|
| D2 | ST25DV16K 驱动怎么解决 | ~~三选一~~ → **落地 (a) smbus2 自写** | ✅ 已定（7-17，见 §9 + §4.1）|
| D3 | 日语播报怎么出声 | ~~(a) pyttsx3 本地 / (b) 云 TTS / (c) 预录~~ → **拍板：后端预生成 wav 下发，点呼机 `aplay` 播放** | ✅ 已定（6-03 — 512MB 跑不动本地 TTS；学号当文件名如 `10023.wav`）|
| D4 | PN532 接 Pi 用 SPI 还是 I2C | ~~二选一~~ → **落地 (a) SPI**（实装如此，`board.D8`/CE0） | ✅ 已定（7-17）|
| D5 | 点呼机↔后端用 HTTP 还是 WebSocket | ~~二选一~~ → **拍板：两个都用，各司其职** | ✅ 已定（6-03）— WebSocket 推指令 + HTTP 常规请求；**断线自动重连必写 → §6** |
| D6 | 设备认证方式 | ~~(a) 设备 ID + 密钥 / (b) JWT~~ → **契约定稿 = Ed25519 设备私钥挑战签名换 12h JWT（a+b 合体）** | ✅ 已定（7-17，`specs/rollcall/Device_Contract.md §2` 唯一真值）|

---

## 11. 历史

- 2026-05-08：itsuki 拍板「点呼机当第 5 端」+ 联动机制升级（4 端反向规则 + 点呼机加入 system-features 联动）+ 本档案骨架建成
- 2026-07-17：软件从零全实装（`a0e1595`，依 itsuki /goal「点呼真实装」）——契约 `Device_Contract.md` 定稿 + src/ 全模块 + 75 条 pytest + systemd + 部署SOP；D1/D2/D4/D6 落地（§9/§10）；剩硬件到货联调
- 2026-07-18：审查修复批（`9347a89`，cursor grok-4.5 只读审查 2 条采纳）——
  ① **鉴权错误码集合合并到 `src/api/envelope.py` 单一真值**，并补上漏掉的 `INVALID_CREDENTIALS`。原来反馈层（`feedback.py`，决定白灯闪烁）和离线队列（`offline/queue.py`，决定不出队 + 停补传刷令牌）各存一份，都漏了这个码 —— 而它正是后端 `deps.get_current_device` 在令牌解码失败 / 世代过期时实际返回的码。**后果**：令牌一过期，断网攒下的整晚补传会被当成「终态业务错误」逐条出队丢光，现场还走红灯失败而不是白灯 + 刷新令牌。新增测试锁死三处引用的是同一个对象，防以后再分家。
  ② `client.py` 的 `sync_audio` 对 manifest 文件名做设备侧白名单校验（正则与后端 `_AUDIO_NAME_RE` 同款）+ `resolve()` 后确认仍在缓存目录内 —— 后端被攻破 / manifest 出错时不至于把文件写到缓存目录外（纵深防御）。
  验证：78 passed（原 75 + 新增 3）。
- 2026-07-21：审查 S2 修复批（`b840878`，五端 568 条修复计划 S2 场，三方辩论两轮定案 + 四家终审）——
  ① **device#0（critical）取令牌被拒不再卡灯丢签到**：`_handle_checkin` 原来只捕网络错误，取令牌被后端明确拒绝（`AuthError`）时异常冒泡到消费线程的笼统 except，LED 卡在处理中蓝闪、这次刷卡静默消失。现在捕获后：令牌作废 + 签到入队待补传 + 白灯回待机。
  ② **device#2 在线签到遇鉴权错误码改为「刷新令牌重发一次，仍失败入队」**——鉴权失败永不丢签到。整段重试链自捕 `AuthError`/`NetworkError`（辩论认定的头号风险：`ensure_token` 在重试路径里同样会抛，不包住等于原病复发）。
  ③ **device#3 补传自愈**：补传撞鉴权停轮后，主循环侧刷新令牌再补一轮（仅一次防重放风暴）；刷新失败保留队列等下次在线成功。
  ④ **device#1 GPO 兜底轮询**：邮箱读取原来把 GPO 边沿当唯一读条件，漏一个边沿（抖动/上电时序/回调丢失）路径 B 签到就永久漏读。现在未见触发也按 1 秒间隔走 I²C 确认（`monotonic` 计时防 NTP 阶跃），GPO 降级为「加速唤醒」。
  ⑤ **device#8 systemd 对时依赖补全**：`Wants` 加 `time-sync.target`（原来只写 `After` 不进启动事务，排序空转）。不用 `Requires`——对时单元异常不该拖死离线点呼。运维注意：Pi 镜像需确认 `systemd-timesyncd` 已启用，否则该行无实际保障。
  验证：88 passed（原 79 + 新增 9：AuthError 捕获 / 重试链 4 分支 / 补传自愈 2 / GPO 门控 4，既有白灯测试按新语义更新）。
  ⑥ **终审阻断修复（`d5fba97`，四家终审中 Fable 5 high 抓出）**：`AuthManager.obtain_token`/`enroll` 原来裸调 httpx——主状态机重试链直接调 `ensure_token` 时若网络恰好断掉，抛的传输层异常（`httpx.ConnectError` 等）既不是 `NetworkError` 也不是 `AuthError`，穿透重试段捕获冒到消费线程，签到丢失 + LED 卡处理中（①要治的原病在重试路径复现）。修法取根治版：`auth.py` 新增 `_post_raw` 统一把传输层异常转 `NetworkError`（enroll 的同型潜洞一并堵上），上层自然走离线入队。回归 +2（auth 层异常转换 / 刷新令牌撞网络断走离线），全量 90 passed。教训：桩对象（StubAuth）只会抛测试作者想到的异常类型，模拟不出真实现的第三种异常——异常契约要在源头收窄，别指望调用方枚举。
- 2026-07-21：审查 S9 修复批（五端 568 条修复计划 S9 场，点呼机 medium 5 条 + 双票复审 grok/opus 背对背只读审收敛）——
  ① **device#4 控制事件与签到解耦**：WS 推来的名单/音频刷新原走同一签到队列、由消费线程串行处理，其同步网络 I/O 会堵住后续刷卡上报（队头阻塞）。改为独立 `_control_queue` + `control` 线程消费；`Roster` 内部已有锁、音频写走 tmp+replace 原子替换，跨线程读写无竞态（复审确认）。
  ② **device#5 反馈灯回待机改非阻塞**：原 `_apply_feedback` 用 `_stop.wait(1.5)` 硬等，离线回补时每条叠加 1.5s。改用 `threading.Timer` 到期切待机、消费线程立即处理下一条。**复审（grok 判重大）抓出回归**：新计时器会在下一条签到处理期间触发、把 PROCESSING 灯打回待机——补 `_handle_checkin` 抢占时先取消旧计时 + 世代号守卫（`cancel()` 挡不住已 fire 的回调，靠世代号作废）。**第二轮双票复审（grok+opus 各自独立同指）再抓 TOCTOU**：`_restore_standby` 世代校验在锁内、`_led.set(STANDBY)` 在锁外——校验通过后放锁、新签到抢占切 PROCESSING、旧回调锁外补写 STANDBY 打回待机。修：世代校验与改灯挪进同一 `with _feedback_timer_lock` 临界区，check+act 原子化。
  ③ **device#7 HTTP 心跳兜底**：WS 长期断线无心跳、设备被误判离线——新增 30s HTTP 心跳线程。**复审抓出启动空窗**：原 `wait(30)` 后才首发、启动后前 30s 无兜底——改先发一次再进等待循环。
  ④ **device#9 非标 UID 丢弃**：读到长度 ≠14 hex（非 NTAG215 7 字节）的卡打警告返回 None，不上报、不占防抖窗口。
  ⑤ **device#10 音频 sha256 校验**：`download_audio` 落盘前校验 sha256，不匹配删临时文件抛错；`sync_audio` 捕获后跳过不计入 downloaded，截断/损坏内容不落成正式缓存。
  验证：90 passed（无回归）。保留（记 TODO，非阻塞）：`_apply_feedback` 末 `if FEEDBACK_HOLD_S<0.1` 测试专用分支（生产恒 inert，清理需改十余处测试断言点）；HTTP 心跳 AuthError 只警告不刷新令牌（既有约束、非本场引入）。
- 2026-07-22：审查 S13 修复批（五端 568 条修复计划 S13 场，点呼机 low 10 条 + 双票复审 grok/opus 背对背，commit `a5fbe92` + 复审 `1cbfc0a`）——
  ① **device#6 WS 停机即时打断**：`_session` 原 `async for raw in conn` 只在收到下条消息后才看 `_stop`，停机靠 `conn.close()` 打断、且有「connect 成功但 `_conn` 未赋值」竞态窗口关不到连接。改为 `recv_task` 与 `stop_task(=_async_stop.wait)` 用 `asyncio.wait(FIRST_COMPLETED)` 并行等待——停机事件一置位即时退出，不依赖 `_conn`；pending 任务 cancel + `gather(return_exceptions=True)` 回收。`stop()` 的 `call_soon/run_coroutine_threadsafe` 加 `try/except RuntimeError`（复审 opus 次-1：`is_running()` 检查后事件循环可能已关，抛错会冒出 stop→shutdown 跳过后续 join/close）。
  ② **device#14 令牌锁竞态**：`obtain_token`/`ensure_token` 判断+取令牌并入同锁 + 入口双检 `_needs_renewal`，消除两线程各发一次 `POST /token`（保留意见：POST 在锁内、令牌 12h 半衰期刷新极少、两审判影响低）。
  ③ **device#16 http.close**：`RollCallDevice` 持有共享 `httpx.Client`，`shutdown` 补 `self._http.close()` 释放连接池。
  ④ **device#17 删死字段**：`Feedback.enqueue` 无生产读取（入队恒由 `_handle_offline`/`_handle_auth_deferred` 无条件做），删字段 + 测试断言。
  ⑤ **device#20/#21 提示音淡出对称**：`gen_tones` 淡出改 `i>=total-fade` + 系数 `(total-1-i)/fade` 使末样本精确归零（原 `1/fade` 非零→爆音）；`fade=min(fade,total//2)` 防淡入淡出区重叠。
  ⑥ **device#13/#15/#18/#19 收尾**：gpio int() 包 try/except 抛 ConfigError；queue 死列 swipe_time/enqueued_at；停机注释订正；白灯鉴权测试遍历 AUTH_ERROR_CODES 补 INVALID_CREDENTIALS。
  验证：pytest 90 passed。双票复审 grok 报 device#6 重大、opus 判次要，取 substantive 硬化（并行等待即时打断 + stop RuntimeError 兜底）。
- 2026-07-27：上机前检查修复（TF 卡烧录期间的最后一道软件检查，CC 端到端真跑 + cursor grok-4.5 只读审背对背，itsuki 当场拍板只修这一条）——
  **硬件初始化失败给人话提示、systemd 不再无限重启**：原 `main()` 只捕 `AuthError`/`ConfigError`，硬件层抛的 `RuntimeError`/`OSError` 直接冒出去崩栈；叠加 `Restart=on-failure`+`RestartSec=5`，组装现场看到的是「服务每 5 秒重启一次」，真正的报错被刷屏淹没、判断不出是哪根线插错。改为：新增 `HardwareInitError`（带 `part` 哪块硬件 + `hint` 该查什么），`_init_part()` 逐块包住 PN532/ST25DV/LED/音频四处构造与驱动库 import，把各驱动不统一的异常统一翻译；`main()` 捕获后打三行中文（是哪块 / 查哪几项 / 不接硬件请加 `--simulate`）退出码 **3**，service 补 `RestartPreventExitStatus=3` 让 systemd 认定不可自愈、停在 failed 状态，`systemctl status` 第一屏即排查提示。验证：pytest 93 passed（新增 3 条）；Mac 上真跑非 simulate 模式确认三行提示与退出码 3。
  同批检查确认能跑通、未改动：设备 enroll→token→名单→刷卡→重复刷→路径B→未知卡→心跳→WS→断网本地放行→恢复补传，13 项端到端全通，接口契约与后端逐字段对上。挂 TODO 未修 6 条见 `admin/TODO.md`（后端从不推 `roster_updated`/`audio_updated` 为其中最重）。
- 2026-07-29：新增 `--skip-card-reader`，支持分阶段硬件验收——
  **动因**：ST25DV16K 已焊通并经 `i2cdetect` 验证（7-28），PN532 尚未焊接且为全项目唯一无备份零件。App Store 审核 Guideline 2.1 要求的演示视频只涉及路径 B（手机写邮箱），不依赖读卡器；但 `build_hardware()` 中 PN532 的构造顺序早于 ST25DV，读卡器缺席会使整机在启动阶段即抛 `HardwareInitError` 退出码 3，路径 B 无从验证。为在动用不可逆零件之前先探明 RF 侧链路，需要一条「允许读卡器缺席」的降级路径。
  **实装**：`build_hardware()` / `bootstrap()` 新增 `skip_card_reader` 形参，命令行开关 `--skip-card-reader` 贯通至装配层。启用时读卡器整块不构造、替换为 `FakeCardReader`（`read_uid` 恒返回 `None`，只表现为「读不到卡」，不会伪造刷卡事件污染考勤），同时打印 WARNING 声明实体卡路径失效。
  **默认关闭的理由**：缺件仍能静默启动属上线事故风险，降级须由操作者显式声明，故不做自动探测、不改变既有「硬件缺一不可」的默认语义。
  验证：pytest 95 passed（新增 2 条——跳过分支下首个失败部件由 PN532 变为 ST25DV，证明读卡器整块未被构造；命令行开关贯通至装配层且缺省为 `False`）。
- 2026-07-29：关闭 ST25DV 邮箱看门狗 + `begin()` 校验安全会话——
  **动因**：cursor grok-4.5 只读审查报「邮箱看门狗未被写入」为重大项，itsuki 于上机前拍板先改。`MB_WDG`（系统配置寄存器 `000Eh`）出厂默认 `0x07`，非 0 即启用超时：RF 侧写入邮箱后若 I²C 侧未在窗口内读走，芯片自行清除 `MB_CTRL_Dyn.RF_PUT_MSG` 并丢弃消息。本驱动 `message_pending()` 正是以该标志位判定有无新消息，标志被清即等价于载荷永久静默丢失，且无任何错误面可见——现场表现为「学生碰了、点呼机毫无反应」。触发条件不苛刻：GPO 漏边沿时退化为 1s 兜底轮询，采集线程任何一次偶发阻塞即可越过超时窗口。
  **实装**：新增常量 `REG_MB_WDG` / `MB_WDG_DISABLED`，`_disable_mailbox_watchdog()` 先读后比，仅在当前值非 0 时写回 `0x00`（该寄存器位于 EEPROM，无条件回写等同每次开机磨损寿命）。调用点置于 `begin()` 中 `MB_MODE` 使能之前，避免存在「邮箱已开、超时仍为旧值」的中间窗口。
  **连带修正**：`begin()` 在 `present_password()` 之后校验 `I2C_SSO_Dyn`，会话未打开则抛 `RuntimeError`（上层转 `HardwareInitError` 退出码 3）。原实现下，口令不符时 `MB_WDG` / `MB_MODE` / `GPO` 三个系统寄存器均被芯片静默拒写，程序照常启动而邮箱功能全程失效——与看门狗超时同属「无错误面的静默失效」，故同批消除。
  **取舍**：关闭超时后，若进程在邮箱压有消息时崩溃，该消息不会自行消失。`MailboxGpoReader._last_i2c` 初值为 0，重启后首次 `poll()` 即兜底读取一次，滞留载荷被扫除，不阻塞后续学生。
  验证：pytest 99 passed（新增 4 条——关闭动作发生、已为 0 时不重写、会话未开即抛错且不触碰任何系统寄存器、`MB_WDG` 写入序位于 `MB_MODE` 之前）。寄存器地址与禁用值经 ST 官方社区口径核实，真机行为待上机确认。
