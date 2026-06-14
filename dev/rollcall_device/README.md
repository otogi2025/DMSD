# Tomoshibi 点呼机（Roll Call Device）

> **作用**：宿舍点呼机的 Python 程序代码 + 部署。跑在 **Raspberry Pi 3 Model A+** 上,接 PN532 NFC 读卡器（读学生 NTAG215 卡）+ ST25DV16K 动态贴纸（给学生 iPhone 读）+ LED 状态灯 + USB 小音响（日语播报）。
>
> **建立**：2026-05-08
> **当前状态**：⏳ 骨架阶段（目录 + 设计文档大纲建成,代码未实装）
>
> **角色定位**：thin client / thick server — 本机只搬运数据（读卡 → 调后端 → 接收响应 → 反馈）,业务判断全在后端。

---

## 目录结构

```
dev/rollcall_device/
├── README.md                       本文
├── ROLLCALL_DEVICE_DESIGN_LOG.md   软件设计权威源（程序架构 / GPIO 分配 / 启动 / 错误处理）
├── requirements.txt                Python 依赖
├── src/                            源代码
│   ├── main.py                     入口（启动主循环）
│   ├── nfc/                        PN532 读卡 + ST25DV 写 nonce 驱动封装
│   ├── audio/                      日语 TTS + 播报队列
│   ├── led/                        LED 状态机（待机 / 成功 / 失败 / 错误）
│   └── api/                        调 backend HTTP / WebSocket 客户端
├── config/                         systemd unit / boot config / 环境变量
└── docs/                           部署 SOP / 装系统步骤 / 接线图
```

## 上游 / 下游

- **上游设计真值**：
  - `design/hardware_design.md` — 物理硬件层（板子选型 / 模块选型 / BOM）
  - `design/system_features.md` — 共用层功能设计（≥2 端涉及）
  - `design/flow_design.md` — 端到端流程（学生→点呼机→后端→老师端）
  - `specs/rollcall/RollCall_Spec.md` — 点呼业务规则
- **下游协作**：
  - `dev/backend/` — 调后端 API（认证 / 签到 / 时间窗判定）
  - `dev/student_ios/` + `dev/student_android/` — 间接联动（学生 app 通过点呼机贴纸的 nonce 签到）

## 启动（开发期暂未实装）

```bash
# 装依赖
pip install -r requirements.txt

# 启动主程序（开发期）
python src/main.py
```

部署 SOP（systemd 服务 / 开机自启）见 `docs/`(待写)。
