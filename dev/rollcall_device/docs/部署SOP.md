# 点呼机部署 SOP（从烧卡到跑起来）

> 对象：一台 Raspberry Pi 3A+ 点呼机。硬件接线见 `../点呼机接线说明.md`；软件设计见
> `../ROLLCALL_DEVICE_DESIGN_LOG.md`；协议契约见 `specs/rollcall/Device_Contract.md`。
> 全程 headless（不插键鼠，用 SSH），因为 Pi 3A+ 唯一的 USB 口被小音响占了（已知坑 §8-#3）。

---

## 0. 名词先解释

| 名词 | 是什么 |
|---|---|
| 烧卡 | 把树莓派操作系统镜像写进 microSD 卡 |
| SSH | 远程登录树莓派命令行的方式（Mac 终端敲 `ssh pi@<树莓派IP>`）|
| venv | Python 虚拟环境，把本项目依赖跟系统 Python 隔开，互不污染 |
| systemd | Linux 的开机自启 / 服务守护机制，让点呼机断电重启后自动跑起来 |
| enroll | 设备激活：把设备公钥登记到后端，换一次性激活码（契约 §2.2）|

---

## 1. 烧系统卡

1. Mac 装 **Raspberry Pi Imager**（官方烧录工具）。
2. 选 **Raspberry Pi OS (64-bit)**（Bookworm）。
3. 烧录前点齿轮（高级设置）预置：
   - 主机名：如 `rollcall-1`
   - 开 **SSH**（用密码或公钥登录）
   - 用户名固定 **`pi`**（systemd 单元里写死 `User=pi` + 家目录 `/home/pi`）
   - Wi-Fi 名 + 密码（宿舍网）
   - 地区/时区 **Asia/Tokyo**（全链路 JST，契约 §12）
4. 写卡 → 插 Pi → 上电 → 等 1-2 分钟联网。
5. Mac 终端 `ssh pi@rollcall-1.local`（或路由器查到的 IP）登录。

## 2. 开 SPI / I2C + 音频切 3.5mm

```bash
sudo raspi-config
```

- `Interface Options → SPI → Yes`（PN532 走 SPI，接线说明 §2）
- `Interface Options → I2C → Yes`（ST25DV 走 I2C，接线说明 §3）
- 音频输出切 **模拟 3.5mm**（已知坑 §8-#4，默认走 HDMI 不出声）：
  Bookworm 用 `sudo raspi-config` → `System Options → Audio → Headphones`，
  或桌面版右上角音量图标选模拟口。

改完 `sudo reboot`，重连 SSH。核对：

```bash
ls /dev/spidev*      # 应见 /dev/spidev0.0
ls /dev/i2c-*        # 应见 /dev/i2c-1
i2cdetect -y 1       # ST25DV 接好后应见 0x53 与 0x57 两个地址
```

## 3. 装代码 + venv 装依赖

把 `dev/rollcall_device/` 整个目录拷到 Pi 的 `/home/pi/rollcall_device`（scp 或 git clone
后取该子目录）。然后：

```bash
cd /home/pi/rollcall_device
sudo apt update
sudo apt install -y python3-venv python3-dev libgpiod2 i2c-tools
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt      # 含硬件库，仅 Pi 上装
```

> 若 `lgpio` / `adafruit-blinka` 装报错，多半缺系统包 —— 补 `sudo apt install -y python3-libgpiod`
> 后重试。硬件库只在 Pi 上装，Mac 开发用 `requirements-dev.txt`。

生成内置提示音（成功/失败/等待）：

```bash
.venv/bin/python tools/gen_tones.py     # 写到 assets/
```

## 4. 填 config

```bash
cp config/config.example.json config/config.json
nano config/config.json
```

按契约 §10 填：
- `device_id`：这台的编号（如 `dorm-1-01`，DEVICE_REGISTRY §6）
- `enroll_code`：**管理员在后端建设备记录后拿到的一次性激活码**（契约 §2.2 步骤 1）
- `server_url` / `ws_url`：生产后端地址（`https://api.tomoshibi.cc` / `wss://api.tomoshibi.cc`）
- `key_path` / `data_dir`：默认 `/var/lib/tomoshibi/*`，需可写：
  ```bash
  sudo mkdir -p /var/lib/tomoshibi && sudo chown pi:pi /var/lib/tomoshibi
  ```
- `gpio.st25dv_gpo`：默认 GPIO24（⏳ 契约 §10 待硬件联调核实，接线后如改动同步三处）
- `audio_output`：aplay 设备串。用 `aplay -l` 查小音响的 card/device，填 `plughw:<card>,<device>`。

## 5. enroll 激活 + 首次干跑

首次直接前台跑一次，看激活 + 拉名单是否成功：

```bash
.venv/bin/python -m src.main --config config/config.json --log-level INFO
```

- 首启会：生成 Ed25519 私钥（0600 存 `key_path`）→ 用 `enroll_code` 激活 → 清空配置里的
  `enroll_code` → 换 12h 令牌 → 拉名单 + 同步音频 → 进待机（蓝灯）。
- 刷一张已绑定的卡：应绿灯 + 播报姓名。
- `Ctrl-C` 优雅退出。

**无硬件联调本地后端**：加 `--simulate`，用 stdin 模拟刷卡：

```bash
.venv/bin/python -m src.main --config config/config.json --simulate
# 然后输入：
#   card 04a1b2c3d4e5f6       ← 路径 A 刷卡（14 位 hex）
#   phone <student-uuid>       ← 路径 B 手机写邮箱
#   quit                       ← 停机
```

## 6. systemd 开机自启

```bash
sudo cp config/tomoshibi-rollcall.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now tomoshibi-rollcall
systemctl status tomoshibi-rollcall        # 看是否 active (running)
journalctl -u tomoshibi-rollcall -f        # 实时看日志
```

断电重启后会自动跑（`After=network-online.target time-sync.target` 保证等到网 + 对时）。

---

## 7. 常见故障对照（设计日志 §8 已知坑）

| 现象 | 排查 | 出处 |
|---|---|---|
| ST25DV 读不到（`i2cdetect` 无 0x53/0x57）| 检查 I2C 接线 + `raspi-config` 开 I2C；GPO 脚接对且有 10kΩ 上拉 | 已知坑 #1 / 接线说明 §3 |
| PN532 读卡无反应 | 确认板上跳线切到 **SPI 模式**；`/dev/spidev0.0` 存在；CE0 接 GPIO8 | 已知坑 #2 / 接线说明 §2 |
| 刷卡有反应但没声音 | `raspi-config` 把音频切模拟 3.5mm；`aplay -l` 核对 `audio_output` 设备串 | 已知坑 #4 |
| 白灯闪烁（AUTH_ERROR）| 令牌/激活问题：确认 `enroll_code` 正确未用过、设备在后端 `device_active=true`；看日志 | 契约 §9 |
| 黄灯（红+绿）| SESSION_NOT_RUNNING，点呼未开始，属正常等待态，非故障 | 契约 §9 |
| 断网时刷卡 | 绿灯（本地名单命中）/ 红灯（未命中）；恢复后自动补传 | 契约 §6 |
| 开机瞬间 LED 微亮 | 正常，程序启动第一件事把 LED 全置灭（接线说明 §4）| — |
| 换机 / 换钥 | 管理员先 `POST /devices/{id}/reset-enroll` 重发激活码，删本地 `key_path` 后重启 | 契约 §2.2 |
