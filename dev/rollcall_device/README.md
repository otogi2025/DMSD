# Tomoshibi 点呼机（Roll Call Device）

> **作用**：宿舍点呼机的 Python 程序代码 + 部署。跑在 **Raspberry Pi 3 Model A+** 上,接 PN532 NFC 读卡器（读学生 NTAG215 卡）+ ST25DV16K 动态贴纸（学生手机把身份数据写入贴纸 Mailbox 邮箱,点呼机经 I2C 被动读取）+ LED 状态灯 + USB 小音响（日语播报）。
>
> **当前状态**：软件全实装（2026-07-17）,Mac 上 78 条 pytest 全绿（mock 硬件层）;硬件已到货未组装,真机联调未做 — 进度以 `ROLLCALL_DEVICE_DESIGN_LOG.md` 顶部「实装进度速查表」为真值
>
> **角色定位**：thin client / thick server — 本机只搬运数据（读卡 → 调后端 → 接收响应 → 反馈）,业务判断全在后端。

---

## 目录结构

```
dev/rollcall_device/
├── README.md                       本文
├── ROLLCALL_DEVICE_DESIGN_LOG.md   软件设计权威源（程序架构 / GPIO 分配 / 启动 / 错误处理）
├── 点呼机接线说明.md                针脚接线对照（PN532 / ST25DV / LED / 音响）
├── 点呼机采购清单.html              硬件采购清单
├── requirements.txt                树莓派运行依赖（含硬件库）
├── requirements-dev.txt            Mac 开发 / 测试依赖（不含硬件库）
├── src/                            源代码（24 文件）
│   ├── main.py                     入口 — 双线程主循环 + `--simulate` 无硬件模式
│   ├── config.py                   配置加载 / events.py 事件类型 / feedback.py 反馈编排
│   ├── timeutil.py                 时间口径（swipe_time 生成,判定归后端）
│   ├── roster.py                   本地名簿缓存（断网时放行判断）
│   ├── nfc/                        PN532 SPI 读卡 + ST25DV I2C 读 Mailbox 邮箱（手机写入,点呼机被动读）+ 载荷解析 + 去抖
│   ├── audio/                      播报队列（后端预生成 wav 下发,本机只播放）
│   ├── led/                        LED 状态机（待机 / 成功 / 失败 / 错误）
│   ├── api/                        调 backend HTTP / WebSocket + Ed25519 设备认证 + 响应信封解包
│   └── offline/                    断网离线队列（SQLite,恢复后补传）
├── tests/                          pytest（78 条,Mac 上 mock 硬件层跑）
├── tools/                          gen_tones.py — 生成内置提示音
├── assets/                         内置提示音 wav（成功 / 失败 / 等待）
├── config/                         config.example.json + systemd unit
└── docs/                           部署 SOP
```

## 上游 / 下游

- **上游设计真值**：
  - `design/hardware_design.md` — 物理硬件层（板子选型 / 模块选型 / BOM）
  - `design/system_features.md` — 共用层功能设计（≥2 端涉及）
  - `design/flow_design.md` — 端到端流程（学生→点呼机→后端→老师端）
  - `specs/rollcall/RollCall_Spec.md` — 点呼业务规则
- **下游协作**：
  - `dev/backend/` — 调后端 API（认证 / 签到 / 时间窗判定）
  - `dev/student_ios/` + `dev/student_android/` — 间接联动（学生 app 把身份数据写入点呼机贴纸的 Mailbox 邮箱,点呼机读出后上报后端）

## 启动

```bash
# 装依赖（含硬件库,只在树莓派上装；Mac 开发测试用 requirements-dev.txt）
pip install -r requirements.txt

# 树莓派上正常启动（注意是 -m src.main,不是 python src/main.py——后者会 ImportError）
.venv/bin/python -m src.main --config config/config.json --log-level INFO

# Mac 上无硬件试跑：stdin 模拟刷卡,LED / 音频降级成控制台打印
.venv/bin/python -m src.main --config config/config.json --simulate
```

部署 SOP（systemd 服务 / 开机自启 / 接线后首次上电）见 `docs/部署SOP.md`。
