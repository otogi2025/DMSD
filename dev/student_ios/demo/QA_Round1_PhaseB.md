# QA · Round 1 Phase B · 静态源码扫描报告

> **建立**：2026-04-22 夜 · [Mac-demo-sprint]
> **输入**：`designs/Tomoshibi_iOS_PhaseB.html`（1.9 MB · Claude Design Phase B self-unpacking bundle）
> **解包结果**：`designs/phaseB_src/` 7 个 component JS + vendor（React 18 / ReactDOM / Babel）+ 1 个 image + template
> **方法**：manifest 解码 + 源码 grep（我看不到渲染，视觉 QA 需 itsuki 自己 run HTML）
> **后续**：❌ 视觉走查（itsuki）→ 🎯 修复优先级拍板 → 📝 Round 2 补丁 prompt OR 代码 agent WebView 层 CSS fix

---

## 1. 源码结构（解包后）

| UUID | 主要内容 | 大小 |
|---|---|---|
| `c281cafa` | **全局 state + SEED**（T tokens + SEED user/bus/events/notifications/wall-post/etc）| 7 KB |
| `c13988a3` | **Auth flow** — SplashPage / OnboardingPage / RegisterStep1-4 / RegisterDonePage / LoginPage / LockoutPage / PwResetPage | 22 KB |
| `364061ea` | **Home + Sheets** — HomePage / RollcallSheet / FeedbackSheet / HealthSheet / AbsenceSheet / OtherSheet | 24 KB |
| `33f0266b` | **Home 子页** — Notifications / Packages / Lost / Music / Wall / Events / Bus / Suggest 全 18 页 | 26 KB |
| `100ba570` | **申し込み tab** — ApplyList / ApplyNew / ApplyForm / StayForm / GenericApplyForm / ApplyDetail | 35 KB |
| `e38fcebf` | **マイページ tab** — MyLanding / MyInfo / MyRollcall / MyPoints / MyDiscipline / MyHealth / etc + LogoutSheet | 19 KB |
| `8b866e02` | **Router + AppProvider + BreadcrumbPopup + Toast** | 35 KB |

✅ **全 73 画面 route 都声明了**（见 `_template.html` bottom App component，32 route rules）

---

## 2. 🔴 Critical 问题（影响 demo / 必改）

### C1 · 中文词汇残留约 6 处

和 Web Round 3 同类 bug。`SEED` 和 UI 多处中文 term：

| 残留词 | 日语自然版 | 出现文件 · 位置 |
|---|---|---|
| `点歌` | `リクエスト曲` | `364061ea` (home card) + `33f0266b` (MusicPage header) + `c13988a3` (onboarding body) |
| `宿舍墙` | `寮ウォール` | `364061ea` + `33f0266b` (WallPage header) + `c13988a3` (onboarding) |
| `快递` | `宅配` 或 `荷物` | `c281cafa` (notifications seed) + `364061ea` (home card) + `33f0266b` (filter) + `e38fcebf` (履歴 label) |
| `晚` (中文字) → `晩` (日语字) | `晩` | `c281cafa` seed 点呼履歴 `'晚点呼'` + `c13988a3` RegisterStep2 `'平日: 朝 7:00 / 晚 21:00'` (2 次) |
| `遗失物` | `落とし物` / `忘れ物` | 存在与否待视觉 QA（route 用 `lost` 英文） |

**影响**：管理员日本人视角看会觉得 UI 「中日混血」，不专业感。修复量 < 5 行源码 replace。

### C2 · リュウ イヒ 数据 Web / iOS 不一致

| 项 | iOS (Phase B) | Web (Round 3 最新) | 出处 |
|---|---|---|---|
| 部屋 | **W101** | **M101** | iOS: `c281cafa:71` / Web: `内部记录 §17:40` |
| 寮 | **女寮** | **男寮** | 同上 |
| 扣分 | **4.0** 点（迟到 2 + 缺席 3）| **4.5** 点（迟到 5 + 缺席 2） | iOS: `364061ea:57` / Web: `内部记录 §17:40` |

**原因**：我写 iOS Round 1 Prompt 时（18:45+）没同步 Web [Code-Agent] 4-22 下午（~17:40）的改动。Phase B 就 naturally 跟了 iOS Prompt 的规格。

**影响**：demo 当天管理员可能同时看 iPad Web + iPhone App → 两端不一致会穿帮。必须统一。

**决策点**：
- **(a)** 改 iOS 同步 Web（M101 / 4.5 分）— 推荐，Web Round 3 已 QA
- **(b)** 改 Web 回 W101 / 4.0 分 — 回退 Web 修改，不推荐

### C3 · 申请类型 kind 与 Prompt 不一致

我 Round 1 Prompt §5.1 定义 7 种申请：外泊 / 帰国 / 帰省 / タクシー / 掃除 / 欠席届 / 免点呼閲覧。

Phase B 实际实装（`100ba570`）的 kind：
- ✅ **stay**（外泊）
- ✅ **holiday**（帰省）
- ❓ **repair** / **parcel** / **guest** / **return** — 这 4 种 Claude Design 自创

缺失：**帰国 / タクシー / 掃除 / 欠席届 / 免点呼閲覧**（部分可能在其他组件里，需视觉走查）。

**Claude Design 可能的推理**：日本寮实际纸质申请 6 种 ≈ 外泊 / 帰省 / 修理（設備）/ 宅配（受取）/ 来客 / 返却 → 把我的"归国"视为"长假出国 = 归省+外泊子集"合并。

**决策点**：
- **(a)** 接受 Claude Design 重构（AI product thinking 产出，可能更贴日本实际）— 需 itsuki 真实寮生 review
- **(b)** Round 2 补丁回归 Prompt 原 7 种 — 严格按需求

### C4 · iPhone frame 尺寸错（390×844 = iPhone 13 base · 非 iPhone 17 Pro）

Phase B 的 `.device` CSS：`width:390px; height:844px;` —— 是 **iPhone 13 / 14 / 15 basic** 的 logical points。iPhone 17 Pro 应是 **402×874 pt**（1206×2622 px）。

**更大问题**：HTML 里画了完整 iPhone frame（黑边 + 侧边按钮 + 刘海）。WebView wrapper 包在 iOS Simulator iPhone 17 Pro 里 = **双层 iPhone frame**。

**解决方案**（代码 agent 做）：WebView 加载 HTML 时注入 CSS override：
```css
.stage, .caption { display:none !important; }
.device { width:100vw !important; height:100vh !important; padding:0 !important;
  border-radius:0 !important; box-shadow:none !important; background:transparent !important; }
.btn-side { display:none !important; }
.screen { position:static !important; inset:auto !important; border-radius:0 !important;
  width:100% !important; height:100% !important; }
```
→ 隐藏 HTML 自带 frame + 侧键 + caption 工具栏，让内部 `.screen` 占满 WebView，由 Simulator 提供真实 iPhone 17 Pro frame。

---

## 3. 🟡 Important 问题（建议改但不阻塞）

### I1 · LockoutPage 倒计时固定 30 秒（没升级 logic）

`c13988a3:385` `useState(30)` 硬编码 + 每次都跳 `/login`。UI 显示「次回失敗で 1 分間ロックに上がります」但实际永远 30 秒。

**Demo 影响**：低（管理员不会真去试 3 次错密码 + 多次触发升级）。Post-demo TODO。

### I2 · 上线版 iOS API 安全模型未实装

Phase B 纯 UI mock，没有真 API 调用（符合 HTML mockup 定位）。Demo 当天 iOS App 在 Simulator 只做展示，签到走 iPhone Shortcuts + 自有 NFC 卡（[Code-Agent] 4-22 晚 demo_server.py 定型）。

**Post-demo**：iOS SwiftUI 版才需要真 API + Keychain 私钥 + ECDSA 签名。

### I3 · サッカー部 选项独有的点呼时间展示

RegisterStep2 line 171-172 已有 "平日: 朝 7:00 / **晚** 21:00" (regular) vs "早朝練があるため · 平日: 朝 6:00 / **晚** 21:00" (soccer)。

- **问题**：「早朝練があるため」在一般寮生选项里是**负述**（"因为有早朝练"），但一般生没早朝练 → 应是正述；sakkā-bu 选项也没完整表达差异
- **建议文案**：
  - 一般寮生：「朝 7:00 点呼 · 晩 21:00 点呼（平日）」
  - サッカー部：「朝 6:00 点呼（早朝練のため 1 時間早い） · 晩 21:00 点呼」

---

## 4. 🟢 Nice-to-have (不影响 demo)

### N1 · Dev 工具 caption bar

HTML 顶部有 "Tomoshibi · Phase B /splash [↻ リセット] [🏠 Home]" caption pill。是 Claude Design 方便测试用的跳转工具，**管理员看到会奇怪**。

**建议**：WebView CSS override 里 `.caption { display:none !important; }` 隐藏。

### N2 · 登录页 demo hint 暴露 itsuki 真 email

`c13988a3:377`：「デモでは · 番号: 00 · メール: otogi2025@gmail.com でログインしてください」

管理员会看到你的真 Gmail。可以：
- 保留（demo 友好，demo 后人人知道）
- 改成 `demo@tomoshibi.jp` 这种 mock email（隐私）

### N3 · 锁定升级时间阶梯提示

LockoutPage 只说"次回失敗で 1 分間"。完整升级链应是 30s → 1m → 5m → 30m → 1h → 永久锁。UI 没全 visualize。

**建议**：加一个小 "アカウント保護レベル" progress bar（5 阶段）让管理员一看就懂。

---

## 5. ✅ 正确实装的（可以称赞的）

1. **注册 4 Step 字段全齐**（氏名 / 生年月日 pickup hint / 性別 auto-dorm / 一般 vs サッカー部 / メール / 電話 / パスワード×2 + 警示 banner 「寮監に連絡」）
2. **LoginPage 2 tab**（番号 / メール）+ 00 seed 匹配 `acc==='00' || email==='otogi2025@gmail.com'` — 实装了**注册 flow 假装魔法**
3. **LockoutPage 视觉** — 🔒 + MM:SS 倒计时 + 「宿監に通知しました」+ 升级 hint
4. **PwResetPage** — 明确说「App 内では行えません · 寮監に直接お声がけください · 寮監がシステム後台で手動でリセットします」
5. **Long-press 400ms** 触发 BreadcrumbPopup（`8b866e02:163` `setTimeout 400`）
6. **RollcallSheet**：スキャンの準備ができました + キャンセル + Liquid Glass backdrop
7. **Home omnibus 10+ card** 实装（扣分 / 通知 / 快递 / 遗失物 / 点歌 / 宿舍墙 / 活動 / バス / 建議）
8. **Global overlays**：RollcallSheet / FeedbackSheet / HealthSheet / AbsenceSheet / OtherSheet / LogoutSheet / BreadcrumbPopup / Toast 全部在 App root declare
9. **配色与 Ryō + 火焰暖色混用** — Liquid Glass backdrop rgba(15,30,34,0.35) + rollBtnShadow 带橙光 — 和 Splash 火焰 logo 呼应
10. **iPhone frame 有侧边按钮**（mute / vol up / vol down / power）细节

---

## 6. QA 不能 cover 的（需 itsuki 视觉走查）

我看不到渲染。以下必须 itsuki 自己打开 HTML 走一遍：

- [ ] Splash 动画（logo 淡入 + 跳转 timing）
- [ ] Onboarding 3 屏滑动
- [ ] 注册 4 step 进度条 + 每 step 输入 + 字段校验
- [ ] 注册完成 → Login → "00" 输入 → Home 的完整 flow
- [ ] Home 主屏 10+ card 布局 + 扣分 4.0 黄色 card
- [ ] Home inner tab（生活情報 / コミュニティ / 通知）切换
- [ ] 中央 ⭐ 点呼按钮 tap → Liquid Glass sheet 滑上来 → 成功态切换
- [ ] 顶部点呼 bar 3 态（日常 / 点呼中 / 已签到）— **有没有实装？**（Phase B 看起来 HomePage 里有但不 sure 是否在其他页持续显示）
- [ ] 长按返回 0.4 秒 → breadcrumb 弹出
- [ ] 申し込み 7 种 kind 齐不齐（C3 问题）
- [ ] 外泊 form 字段全量（实体表 digital 化）
- [ ] マイページ 10+ 入口 + 点呼履歴 30 件 mock + 減点明細 list + 減点推移 chart
- [ ] 各 sheet（健康 / 欠席 / 其他问题）form 体验
- [ ] 暗色模式 toggle（Q1-8 答复要求做暗色）
- [ ] Toast 动画

---

## 7. 推荐修复路径

按修复成本排序：

### 路径 A · CSS 层 override（代码 agent 在 WebView wrapper 里做）
**修复**: C4（iPhone frame 双层）+ N1（caption bar）
**成本**: 10 行 CSS inject · **0 额度消耗**
**优先级**: ⭐⭐⭐ 必做（demo 日 must）

### 路径 B · 直接改 JS 源文件（sed 批量 replace）
**修复**: C1（中文残留 ~6 处）+ C2（W101→M101 / 4.0→4.5）+ I3（晚→晩 + 时刻表文案）
**方式**: `sed -i '' 's/点歌/リクエスト曲/g; s/宿舍墙/寮ウォール/g; s/快递/宅配/g; s/晚点呼/晩点呼/g; s/晚 21:00/晩 21:00/g; s/W101/M101/g; s/女寮/男寮/g; s/4.0/4.5/g'` 之类
**成本**: 0（代码 agent 5 分钟做）· **0 额度消耗**
**优先级**: ⭐⭐⭐ 必做
**风险**: `4.0` 全替换可能误改（比如 padding:4.0px）→ 需要 contextual replace 不能粗 sed

### 路径 C · Round 2 Claude Design 补丁
**修复**: C3（申请类型 kind 重构）+ LockoutPage 升级 logic（I1）+ 补 Tier 1 完整 7 种申请 kind
**成本**: 1-2 次 Claude Design conversation（额度消耗中等）
**优先级**: ⭐⭐ 建议做但不阻塞 demo
**替代**: 接受 Claude Design 重构（可能更贴日本实际）+ 补 handoff 文档说明

---

## 8. 下一步（itsuki 决定）

1. **视觉走查**：打开 `designs/Tomoshibi_iOS_PhaseB.html`（双击即跑，不需 server）→ 走过 §6 清单 → 标记额外 bug
2. **拍板修复策略**：
   - 路径 A（iPhone frame override）→ **default yes**
   - 路径 B（源文件 sed 修复）→ 文字 + 数据一致性，default yes
   - 路径 C（Round 2 prompt）→ default no，除非 §6 走查发现架构级 bug
3. **代码 agent handoff**：写 `handoff_for_code_agent.md` 交 WKWebView 壳任务（下一步）

---

**END** — QA 报告只是静态扫描，视觉层必须 itsuki 双击 HTML 走一遍。
