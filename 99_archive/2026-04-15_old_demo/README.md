# DMSD 2026-04-15 演示 Demo

## 这是什么

这是给老师看的演示 demo, 展示 DMSD 宿舍管理系统的核心点呼流程: **NFC 刷卡 → Web 座位表实时变绿 + 语音播报**。目的是让老师直观看到"学生用 NFC 卡刷一下, 系统立刻知道谁到了"的完整链路。

**重要**: 这是演示代码, 不是生产代码。为了 15 分钟能跑起来, 做了大量简化 —— 没有数据库 (数据存内存, 重启清空), 没有用户认证, 没有错误处理兜底, 没有日志持久化。真正上线版会基于 `01_specs/` 里的规范重写。这里**只**保留能让老师看到"视觉效果"的那部分。

## 演示效果

老师会在 Mac 浏览器看到一张宿舍座位表, 24 个床位排成 6 个房间。一开始全是灰色 (未到)。当你点"模拟刷卡"按钮或者 iPhone 碰一下 NFC 卡时, 对应座位会立刻变绿色, 同时浏览器会用合成语音播报一句"欢迎 itsuki"。演示核心: **刷卡 → 实时响应**。

## 怎么跑起来(一步一步)

### Step 1: 启动后端

```bash
cd 03_dev/demo_2026-04-15
chmod +x run.sh
./run.sh
```

看到 `Running on http://0.0.0.0:8000` 就是启动成功。

> **解释**: `chmod +x` 意思是 change mode + executable, 给这个脚本添加"可以被执行"的权限 (Linux/macOS 文件默认只有"读"权限, 不能当程序跑)。只需要做一次, 以后直接 `./run.sh` 就行。

### Step 2: 打开前端

在 Finder 里双击 `frontend/index.html`, 浏览器会自动打开。

### Step 3: 测试能不能看到座位表

应该看到 24 个灰色座位, 6 个房间。顶部状态栏应显示 "🟢 后端已连接"。

### Step 4: 先用"模拟刷卡"按钮试试

点页面底部的"模拟刷卡 S001"按钮, 看 101-A 座位是否变绿并播报"欢迎 itsuki"。

如果这一步能工作, 说明后端 + 前端通讯正常, 可以继续配 iPhone。

### Step 5: iPhone NFC 设置

详见 `iphone_shortcuts_guide.md`。核心流程:

- 在 Mac 终端查 IP: `ifconfig | grep "inet " | grep -v 127.0.0.1`
- 打开 `frontend/script.js`, 把 `MAC_IP = 'localhost'` 改成你的 Mac IP
- 刷新浏览器
- 在 iPhone 上设置快捷指令 → 碰 NFC 卡触发 HTTP POST → 座位变绿

## 文件结构说明

- `backend/app.py` — Flask 后端, 提供 `/checkin` 和 `/events` 两个接口
- `backend/students.json` — 24 个假学生数据 (S001-S024, 分布在 6 个房间)
- `backend/requirements.txt` — Python 依赖清单 (Flask)
- `frontend/index.html` — 前端页面骨架
- `frontend/style.css` — 座位表样式
- `frontend/script.js` — 前端逻辑 (轮询后端 + 更新 UI + TTS 播报)
- `run.sh` — 一键启动脚本
- `iphone_shortcuts_guide.md` — iPhone 快捷指令配置步骤
- `README.md` — 本文件

## 老师面前怎么演示(建议脚本)

1. "这是我做的宿舍点呼系统的 demo, 展示核心流程。"
2. 打开浏览器, 展示 24 个灰色座位: "这是宿舍 4 楼的 24 个床位, 6 个房间, 每个房间 4 张床。"
3. 点"模拟刷卡"按钮, 座位变绿 + 播报: "学生刷卡后, 系统实时响应, 座位变绿, 并用语音播报谁到了。"
4. 拿出 iPhone 演示: iPhone 碰 NFC 卡 → 座位变绿 + 播报: "正式部署时学生用 NFC 卡, 点呼机识别后实时同步到老师的后台屏幕。"
5. 指着老师看的屏幕: "老师可以实时看到谁到了、谁还没来, 不用人工点名, 也不会有人代答。"

## 常见问题

- **浏览器打开页面显示"后端未连接"**: 确认 `run.sh` 是否还在运行, 没被 Ctrl+C 关掉。Terminal 窗口应该还开着, 显示 Flask 的日志。
- **iPhone 碰卡没反应 / 不能触发**: 先检查 Mac 和 iPhone 在同一 WiFi。如果公司/学校 WiFi 隔离设备 (不让设备之间通讯), 备选方案: iPhone 开个人热点, Mac 连到热点再试。此时 Mac IP 会变, 要重新查 IP 并更新 `script.js`。
- **TTS 不说话**: 某些浏览器首次加载会屏蔽自动播放, 点页面任何位置一下激活"用户手势"即可。
- **座位变绿但没声音**: Mac 系统音量是否开? 浏览器是否静音了这个标签页? (Chrome 可以右键标签页 → 取消静音)
- **想重新演示**: 点右上角"重置"按钮清空所有打卡状态。

## 技术栈

- **后端**: Python 3 + Flask (最简单的 Web 框架, 不是 FastAPI —— demo 不需要那么正式)
- **前端**: 纯 HTML + CSS + JavaScript (不用框架, 双击 html 就能跑)
- **通信**: HTTP 轮询 (前端每秒 GET `/events`; 比 WebSocket 简单, 不用配置长连接)
- **语音**: 浏览器内置 SpeechSynthesis API (不是外部服务, 离线可用, 不花钱)
- **数据**: 内存 dict (重启 = 清空, demo 友好, 不需要配数据库)
