# NFC 替代方案：iPhone Shortcuts + itsuki 自有 NFC 卡（银行卡 / Suica / 学生证）  <!-- VERSION_OK -->

> **⚠️ 文档状态（2026-04-29 加注）**：本文件为 **demo 4-28 阶段的临时 fallback 方案**。demo 已 4-28 跑完且管理员同意采纳系统。**v1.0 上线时硬件路径恢复 = ST25DV16K 动态 NFC 贴纸**（见 `02_design/hardware_design.md §2.1`）。本文件作为"v1.0 上线遇到 ST25DV 供货 / 部署问题时的硬件 fallback 参考"保留，**不是当前活跃方案**。
>
> **背景**: Demo 阶段 ~~ST25DV16K 供货延迟~~ **整个点呼机硬件砍掉**（2026-04-22 拍板，见 `scope_tier.md §0.1`）
> **决策**: **不买任何 NFC 硬件**，itsuki 用她手里已有的 NFC 卡（银行卡 / Suica / PASMO / 学生证 任选）+ iOS Shortcuts Automation 绑定该卡 + POST 后端
> **影响**:
> - Demo 安全性降级（静态 UID 可被读；但 demo 只演 itsuki 一人所以不展示代签场景）
> - 用户体验 100% 对齐最终版（iPhone 碰一下自动签到）
> - 采购 0 成本（砍了 NTAG215 + 点呼机硬件）
> **最后更新**: 2026-04-29（加 v1.0 fallback 定位说明；4-22 内容保留）

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

## 2. 硬件准备（2026-04-22 简化 — 0 采购）

### 2.1 材料

- **itsuki 手里已有的任意 NFC 卡**（不用买）：
  - 银行卡（日本 IC 付带カード）— **先测**，EMV 协议可能被 iOS Shortcuts 拒识别
  - **Suica / PASMO / ICOCA** 交通卡 — FeliCa 规范，大概率 iOS 能识别
  - **学生证** — 如果是 FeliCa / Mifare 芯片可识别
  - **门禁卡** — 如果是 Mifare Classic / NTAG 系列可识别
- 不需要双面胶，不贴任何东西（demo 时 itsuki 手持 NFC 卡，手机碰卡即可）

### 2.2 位置安排

Demo 桌面上放 NFC 卡即可（或 itsuki 手持）：
- 不贴点呼机（没点呼机了）
- 现场动作：itsuki 把卡拿出来，手机碰一下
- **叙事**（给管理员听）："上线版这张卡是贴在玄关点呼机上的专用 NFC 贴纸，每 10 秒刷新防代签；今天 demo 用我自己的卡代替，动作一样"

---

## 3. NFC 卡准备（2026-04-22 简化）

**不需要写卡** — itsuki 自己的 NFC 卡已有固定的 UID（硬件厂商烧的），Shortcuts 直接按 UID 绑定即可触发。

### 3.1 自测步骤（itsuki D2 前做）

1. iPhone 解锁，打开 **"快捷指令"**（Shortcuts）App
2. 底部 **"自动化"** → **"+"** → **"NFC"** → **"扫描"**
3. 把你的 NFC 卡（银行卡 / Suica / PASMO / 学生证 / 门禁卡）靠近 iPhone 顶部
4. 如果 iPhone 震动 + 出现 "扫描完成" → ✅ **这张卡可用**，给它命名 `Tomoshibi-学生卡-00`
5. 如果 iPhone 无反应或报错 "无法读取此标签" → ❌ 换下一张卡重测
6. 推荐优先级：**Suica / PASMO > 学生证 / 门禁卡 > 银行卡**（银行卡因 EMV 协议，Shortcuts 失败率最高）

### 3.2 如果手里所有卡都失败怎么办

**Fallback 采购**：日本 Amazon 买 NTAG215 空白卡 10 张（¥400 日元，明天到），按下方 §3.3 写一次 URL 即可。

### 3.3 NTAG215 写入（仅 Fallback 情况用）

（原步骤保留作 fallback，只在 §3.1 自测全失败时才执行）

1. App Store 装 **NFC Tools**（wakdev，免费）
2. App 里 Write → Add a record → URL / URI
3. 填任意 URL（例如 `https://tomoshibi.demo/checkin/00`），写入 NTAG215
4. 然后回到 §4 配 Shortcuts Automation

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

### 5.1 演示时 itsuki 的话术（2026-04-22 更新）

开点呼后，itsuki 拿出 NFC 卡，iPhone 靠近它：

> "我现在拿手机碰一下这张 NFC 卡。上线版这张卡是贴在宿舍玄关点呼机上的专用贴纸，今天用我手里这张卡代替，动作一样。（碰一下，iPad 座位瞬间变绿 + iPad 发声）
>
> 看，老师手上的 iPad 实时显示我签到成功，iPad 也念出了我的名字 リュウイヒ。"

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

## 7. Demo 前 itsuki checklist（2026-04-22 简化）

**D2（4-22）前**：
- [ ] iOS Shortcuts 自测 NFC 卡识别（见 §3.1，找到至少 1 张能用的卡）
- [ ] 如果全失败 → Amazon 日本下单 NTAG215 × 10（¥400 日元）

**D7（4-27）彩排前**：
- [ ] Shortcuts Automation 配置完成（见 §4）
- [ ] "运行前询问"已关闭
- [ ] 测试一次：iPhone 碰 NFC 卡 → 后端日志收到 POST 请求
- [ ] 备用卡 2-3 张（防现场那张读不出来）
- [ ] 方案 B 桌面 Shortcut 按钮也做一个作为 fallback（无 NFC 也能 demo）

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
