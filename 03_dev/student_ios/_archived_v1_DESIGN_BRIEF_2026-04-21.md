# 学生 iOS App — Claude Design 设计任务书

> **面向**：Claude.ai 的 Claude Design 功能（HTML UI 设计 agent）
> **产出定位**：iPhone frame 里的 HTML 屏幕 mockup —— 给 itsuki 和代码 agent 做 SwiftUI 的视觉参考
> **非产出**：不是 SwiftUI 代码（实际 Swift 代码由代码 agent 在 Xcode 里写）
> **建立**：2026-04-21 by [Code-Agent]
> **使用方式**：把下方 §1 整段粘到 Claude.ai 新开 Project 的第一条消息。**和 Teacher Web 分开 project 做**，因为两边 design system 可以不同（Web 是 admin tool，iOS 是 native app）

---

## 0. 重要前置

**签到不在 iOS App 里发生**。学生 tap iPhone 到点呼机的 NTAG215 贴纸时，由 iOS Shortcuts Automation 直接 POST `/api/checkin`（不打开 App）。iOS App 的本质是**剩下 5 件事的入口** + 学生查看自己状态。**不要在 App 里做"签到按钮"当主流程** —— 只做辅助。

**iOS App 在 Demo 当天用 Xcode 模拟器演示**（不上实机、无 Apple Developer 账号）。

---

## 1. Opening Prompt（整段粘到 Claude Design）

````
你好。我是 itsuki，在做 DMSD 项目（项目代号），系统对外名叫 **Tomoshibi（灯火 / ともしび）**—— 日本高中宿舍点呼数字化系统。中国留学生，高三，筑波大学 AC 入試准备。现在需要为 2026-04-28 demo 做**学生用的 iOS App UI mockup**。App title / 启动画面品牌名 = **Tomoshibi**（不是 DMSD）。

请作为 UX/UI designer 使用 **`ios_frame.jsx` starter component** 交付一份 **日语界面 iOS App** 的 hi-fi HTML mockup（不是真 Swift 代码，是视觉参考给我的代码 agent 抄）。

## Context（硬约束）

- **用户**：日本 / 中国留学生（宿舍学生，使用 iPhone iOS 17+）
- **设备**：iPhone 14 / 15 portrait。用 `ios_frame.jsx` starter 包裹你的屏幕设计
- **语言**：**UI 文字全部日语**。不是中英
- **字体**：Hiragino Sans / Noto Sans JP。**不要 Inter / Roboto**
- **图标**：SF Symbols 风格（直接用 Material Symbols Rounded 代替，视觉近）
- **风格方向**：**iOS native 惯用模式优先** —— Tab bar、Large Title、分组 List、iOS 系统色（iOS Blue / Green / Red / Orange），不要强行 "custom brand"。App 只有学生用，不需要管理感 —— 偏 iOS 系统感觉 + 学校管理 app 的稳妥即可。

## 签到不在 App 里（核心前提）

学生日常签到走 iOS Shortcuts Automation（碰一下点呼机 NFC 贴纸 → 自动 POST，不开 App）。App 做其他 5 件事 + 状态查看。**不要把"签到按钮"当主页主角**。

## 6 屏清单

用 Tab bar 组织，4 个 tab + 2 个 push-in 页：

### Tab 1: ホーム（Home / 主页）
- 顶部：「おかえり、{name} さん」+ 当前学期出席率 + 本月扣分 + 距离罚扫/禁足的距离
- 卡片 1：今日の点呼（如果 session active → 绿 badge "チェックイン済 HH:MM" / 灰 "未開始" / 红 "結束・欠席"）
- 卡片 2：保留占位 "最近の通知"（mock 2 条）
- 无"签到按钮"（签到走外部 Shortcut）

### Tab 2: 申請（Applications）
- List 4 项导航：
  - 体調報告 → push-in sub-screen
  - 欠席届（本次不去点呼）→ push-in sub-screen
  - 外泊申請
  - 帰国申請
- 每项进去一个 form 页

### Tab 3: 規律（Discipline / 扣分查看）
- 顶部卡片：本月合計 {N} 点
- 下方 progress bar：
  - 距離 清掃罰則 {4 - N} 点
  - 距離 外出禁止 {8 - N} 点
- 时间线：本月每条违规的日期 + 原因
- 底部说明：規則文字（迟到・欠席の点数、月累計閾値）

### Tab 4: マイ（Me / 我的）
- 学生基本信息 + **"学生切替" 下拉**（demo 用 —— 学生 ID 不做真登录，下拉切 mock 学生；详见 §切学生）
- 设置入口（サーバー URL / 通知 / バージョン）

### Push-in 1: 体調報告 form
- 问题类型单选（発熱 / 頭痛 / 腹痛 / 吐き気 / その他）
- 補足 textarea
- 提出ボタン（大 primary）
- 成功后 push toast "老師に通知しました"

### Push-in 2: 欠席届 form（本次不去点呼）
- 理由 textarea
- 提出ボタン
- 成功后显示 "審査中" pending 状态，等老师审批

### 外泊申請 / 帰国申請 form
- 開始日 / 終了日 date picker
- 行き先（或航空券番号，归国用）
- 理由 textarea
- 提出ボタン

## 切学生（demo 专用，§Q3 拍板）

App **不做真登录**。Tab 4 "マイ" 顶部一个下拉从 `GET /api/students` 返回的列表里选 student_id，所有 API 带这个 id。Demo 时 itsuki 切到 itsuki 演健康上报，切到"張三"演请假，让老师 iPad 看到多座位叠加 badge。**这不是生产设计，请把它做成显眼的 DEV 标签区**（黄色 warning 色 + "開発モード" 标记），让管理员也能一眼看出是 demo 简化。

## 交付节奏

**第 1 轮**：3 variations，轴 = **配色 × 字体 × 圆角量**
- 每个 variation 一个 HTML，展示：Home 屏预览 + button / input / card / progress bar / list row 基础组件
- 用 `ios_frame.jsx` 包裹屏幕

**第 2 轮**（选定后）：Tab 1 ホーム + Tab 3 規律 完整屏 + 切 tab 交互

**第 3 轮**：Tab 2 申請 + Tab 4 マイ + 2 个 push-in form + 外泊/帰国 form = 剩余全部

**第 4 轮**：Tweaks 面板
- 配色切换、Dark mode 切换、Dynamic Type size 模拟（iOS accessibility）

## 预先答复

- 没有 codebase / UI kit / brand 参考
- 没有 screenshot reference
- 用 `ios_frame.jsx` starter 包装，不要自己画 iPhone 边框
- 请 invoke your `Frontend design` skill 定方向
- 3 variations 轴：**配色 + 字体 + 圆角量**
- 日语措辞你可 propose，我校对
- 签到不做（外部 Shortcut 处理），**不要画"签到大按钮"**
- Dark mode：第 1 轮不做，第 2 轮之后 Tweaks 里 toggle

请开始。若判断信息仍缺，一次性问完；否则直接进入第 1 轮 3 variations。
````

---

## 2. 后续轮次 Follow-up 模板

**选定**：
```
我选 Variation 1 的配色 + Variation 3 的圆角量。字体用 Hiragino Sans。进入第 2 轮做 Home + 規律 两屏。
```

**导出最终**：
```
请 invoke "Save as standalone HTML" skill 打包成单 .html。另外截图 6 屏（Home / 規律 / 申請 list / マイ / 体調報告 form / 欠席届 form）各一张 1179×2556 (iPhone 15 Pro) 的大图。
```

---

## 3. 日语 UI 术语 draft（和 Teacher Web 那份保持一致；§teacher_web/DESIGN_BRIEF.md §3 有完整表）

iOS 特有补充：

| 中文概念 | 日语 draft |
|---|---|
| 主页 | ホーム |
| 申请 | 申請 |
| 我的 | マイ |
| 本次不去点呼 | 欠席届 |
| 审查中 | 審査中 |
| 已通过 | 承認済 |
| 被驳回 | 却下 |
| 老师已通知 | 先生に通知しました |
| 开发模式 | 開発モード |
| 学生切替 | 学生切替 |

---

## 4. 使用提示

- 和 Teacher Web 那个 DESIGN_BRIEF **分 project 做** —— 因为：
  - Web = iPad admin tool，信息密集
  - iOS = 手机 native app，iOS 惯用模式
  - 两边 design system 不同是正常的（Apple HIG vs Material / custom）
  - **但 brand 色可以让 iOS 沿用 Web 的 accent 色**，后续轮次再对齐
- Claude Design 的 `ios_frame.jsx` 已经画好 iPhone 状态栏 / 圆角 / 刘海，**不要让它自己画 iPhone 边框**
- 最终 HTML artifact 下载到 `03_dev/student_ios/designs/`
- 代码 agent（D6 开工 iOS）会对着这些截图在 Xcode 里写 SwiftUI
