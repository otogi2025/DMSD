# ST25DV16K 替代方案：NTAG215 + iOS Shortcuts Automation  <!-- VERSION_OK -->

> **背景**: ST25DV16K 动态 NFC 贴纸淘宝空运 7-10 天，4-28 demo 前到不了
> **决策**: 2026-04-21 拍板方案 A（NTAG215 静态贴纸 + iOS Shortcuts Automation）
> **影响**: Demo 版安全性降级（静态 URL 可复制）+ 用户体验 100% 对齐最终版（iPhone 碰一下自动签到）
> **最后更新**: 2026-04-21

---

## 1. 方案对比（决策快照）

| 方案 | 硬件 | 体验 | 优点 | 缺点 | 决策 |
|---|---|---|---|---|---|
| **A. NTAG215 静态贴纸 + iOS Shortcuts Automation** | 0 额外（NTAG215 本来要买）| iPhone 碰贴纸 → 自动签到，和最终版一致 | 体验 100% 对齐 + 0 成本 + demo 叙事加分 | 静态 URL（demo 不演示代签漏洞 + 说明"上线版用 ST25DV16K 动态 nonce"）| ✅ **选 A** |
| B. iPhone 桌面 Shortcut 按钮 | 0 | 按屏幕按钮 | 最简单 | 没有 tap 动作，管理员感受差 | ❌ |
| C. iPad Web 模拟按钮 | 0 | 老师点"模拟学生签到" | 0 门槛 | 太假 | ❌ |
| D. Pi 接 OLED 屏 + 动态二维码 | +¥2000 日元 OLED + 开发时间 | iPhone 扫码 | 动态 nonce 保留 | 加硬件 + 加开发 + 不是 NFC 体验 | ❌ |
| E. 等 ST25DV 到货 | 原方案 | 同最终版 | 最理想 | **供货来不及 4-28** | ❌ |

---

## 2. 硬件准备

### 2.1 材料

- 1 张 NTAG215 空白卡（Amazon 日本买的 10 张之一）
- 双面胶 / 3M 贴（把卡粘在点呼机 Pi 3A+ 外壳上）

### 2.2 贴的位置

点呼机外壳正面醒目位置，建议：
- 距离 Pi 主板至少 5cm（避免干扰）
- 贴一个图标"📱 把手机放这里签到"作为视觉引导

---

## 3. NTAG215 写入步骤（iPhone 操作）

### 3.1 装 NFC Tools App

- App Store 搜 "NFC Tools"（开发者：wakdev，免费，蓝色图标）
- 下载安装

### 3.2 写入 URL

1. 打开 NFC Tools App
2. 下方 tab 切到 **"Write"**
3. 点 **"Add a record"**
4. 选 **"URL / URI"**
5. 填入 URL：
   ```
   https://dmsd.local/checkin?device=DEV001&student=1
   ```
   - **注意**：demo 阶段 URL 可以是"看起来像 URL"的字符串，只要 iOS Shortcut 能识别触发就行
   - 也可以用真实后端 URL：`http://[Mac的局域网IP]:8000/api/checkin?student=1`
   - **student=1 是硬编码 student_id，demo 时演 itsuki 签到**。如果要演别的学生切别的卡
6. 点右上 **"Write"**
7. iPhone 靠近 NTAG215 空白卡 → "Tag written" → 完成

### 3.3 验证

- 把 iPhone 再靠近刚写的卡
- iPhone 屏幕顶部会弹 URL 预览（确认 URL 内容正确）

---

## 4. iOS Shortcuts Automation 配置步骤（iOS 26）

### 4.1 创建 Automation

1. iPhone 打开 **"快捷指令"**（Shortcuts）App
2. 底部 tab 切到 **"自动化"**（Automation）
3. 右上 **"+"** → **"创建个人自动化"**
4. 滚动到 **"NFC"** → 点进去
5. 点 **"扫描"** 按钮
6. iPhone 靠近刚写好的 NTAG215 → 扫描成功
7. 给标签命名：`Tomoshibi-点呼机-DEV001`
8. 点 **"下一步"**

### 4.2 配置动作

9. 点 **"添加操作"**
10. 搜索 **"获取 URL 的内容"**（Get Contents of URL）→ 添加
11. 配置请求：
    - **URL**：填后端签到 API（demo 时是 Mac 局域网地址，例如 `http://192.168.1.100:8000/api/checkin`）
    - **方法（Method）**：POST
    - **请求头（Headers）**：添加 `Content-Type: application/json`
    - **请求体（Request Body）**：选 JSON，填 `{"student_id": 1, "method": "shortcut"}`
12. 点 **"下一步"**

### 4.3 关闭确认

13. **关闭"运行前询问"**（Ask Before Running）开关 — iOS 17+ 支持（你 iOS 26 支持）
14. 弹窗确认 "不询问" → 点 **"完成"**

### 4.4 测试

15. 回到主屏幕
16. iPhone 靠近 NTAG215 贴纸
17. 屏幕顶部应弹出"自动化运行中" → 然后静默完成（不弹窗）
18. 查看后端日志，看 `/api/checkin` 是否收到 POST

---

## 5. 现场演示叙事（给管理员听的说法）

### 5.1 演示时 itsuki 的话术

开点呼后，itsuki 把 iPhone 靠近点呼机贴纸：

> "我现在拿手机碰一下点呼机上这个 NFC 贴纸。（碰一下，iPad 座位瞬间变绿 + 喇叭出声）
>
> 看，老师手上的 iPad 实时显示我签到成功，点呼机也喊出了我的名字。"

### 5.2 如果管理员追问"学生把 URL 复制发给别人代签怎么办"

**这是加分的 AC 素材 —— 直接讲出来**：

> "好问题。这个是 demo 版本用的静态 NFC 贴纸，URL 确实是固定的。
>
> 上线版本我会用一种叫 **ST25DV16K** 的动态 NFC 标签，它里面的 URL 每 10 秒自动换一次（换一个叫 nonce 的随机数），学生复制的 URL 10 秒后就失效。所以代签是做不到的。
>
> 这种标签是从中国进口的，空运到日本要 8-13 天，我是 4-21 下的单，所以 demo 今天用静态版先演示完整流程。代签防御这个安全点我是设计时就考虑到了的。"

### 5.3 如果管理员追问"那 App 还能做什么额外防御"

> "另外学生 App 还会用手机的 Secure Enclave（苹果的硬件级安全芯片）生成一对密钥，每次签到带一个数字签名。服务器验证签名合法才算签到。即使有人复制 URL，没有这个学生的私钥也签不出合法签名。
>
> 而且同一场点呼同一个学生重复签到后端会自动去重（幂等）。"

---

## 6. 风险 + Fallback

| 风险 | 概率 | 影响 | Fallback |
|---|---|---|---|
| iOS Shortcuts Automation 在 itsuki iPhone 不触发 | 低（iOS 26 支持好）| 中 | 方案 B：iPhone 桌面放 Shortcut 按钮，demo 时按一下按钮代替 tap |
| iPhone 连 WiFi 不同于 Mac（后端 API 请求失败）| 中 | 高 | Demo 前确认 iPhone + Mac 同一 WiFi + 测试一次 |
| NTAG215 写入失败 / 贴歪 | 低 | 低 | 备 2-3 张写好的 |
| 现场 WiFi 不稳 / 断开 | 中 | 高 | 方案：Mac 开 iPhone 热点 → 所有设备连这个热点（iPad / iPhone / Pi） |
| 后端 Mac 电池耗光 | 低 | 高 | Demo 前 Mac 插电源 |

---

## 7. Demo 前 itsuki checklist

D7 彩排前必确认：

- [ ] NFC Tools App 装好
- [ ] NTAG215 写入 URL 成功
- [ ] 贴纸贴在点呼机正确位置
- [ ] Shortcuts Automation 配置完成
- [ ] "运行前询问" 已关闭
- [ ] 测试一次：iPhone 碰贴纸 → 后端日志收到 POST 请求
- [ ] 备用卡 2-3 张（每张写不同 student_id 演多学生）
- [ ] 方案 B 桌面 Shortcut 按钮也做一个作为 fallback

---

## 8. 上线版本迁移（v1.0）

4-28 demo 后，ST25DV16K 到货，迁移方案：

1. Pi 上跑 I²C 刷新程序（每 10 秒从后端取 nonce + 写入 ST25DV EEPROM）
2. 把原来贴的 NTAG215 换成 ST25DV16K 贴纸
3. iOS Shortcuts Automation 不用改（它只认 NFC 标签的物理识别 + 触发 URL，URL 变动态不影响触发）
4. 后端签到 API 加 nonce 校验（额外一步，不影响现有流程）

**迁移零用户侧改动**：学生还是碰一下手机签到，体验不变。这就是选 NTAG215 + Shortcuts 方案的架构优势。

---

## 9. AC 叙事点

**标题候选**："ST25DV 延迟 → NTAG215 + iOS Shortcuts：Demo 救急方案的架构思考"

**可讲点**：
1. 供应链风险识别（硬件靠中国空运，时间窗不可控）
2. 找到 0 成本替代方案（利用 iOS 原生能力：Shortcuts Automation + NFC 触发）
3. 替代方案不改用户侧体验（tap 动作保留）
4. 替代方案不影响上线版本迁移（架构兼容）
5. Demo 时主动讲出安全降级（诚实 + 体现全链路安全思考）

**核心问题映射**：
- #2 問題意識：供应链风险 + demo deadline 硬约束
- #3 問題解決：找替代 + 保体验 + 保迁移路径
- #4 自己認識："零成本等价方案"的工程直觉
