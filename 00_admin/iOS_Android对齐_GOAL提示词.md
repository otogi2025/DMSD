# iOS↔Android 对齐 — 让两个 App 几乎一模一样 — GOAL 提示词

> itsuki 2026-06-05 的任务提示词。手动 `/goal` 后粘贴下面整段，或定时醒来读本文件自主长跑。
> **配套蓝图（必读）**：`00_admin/iOS_Android_对齐规格.md`（3000+ 行，逐屏规格，agent 读 iOS 真实代码写出来的）。
> **配套截图**：`06_assets/app_screens_2026-06-05_ios/`（14 张 iOS 实机界面图，视觉真值）。

---

【目标】
把 **Android 学生 App 做得跟 iOS 学生 App 几乎一模一样** —— 功能、界面布局、配色、文案、调的后端接口、用的数据字段、业务规则，全部对齐到 iOS。iOS 是真值基准，后端是字段/接口真值。施工照 `00_admin/iOS_Android_对齐规格.md` 一屏一屏来，做完每屏跟 `06_assets/app_screens_2026-06-05_ios/` 对应截图肉眼对照。

【铁律约束 — 动手前必读】
1.「一模一样」= 功能 + 界面布局 + 配色 + 文案 一样，**不是把 Swift 逐字翻成 Kotlin**。iOS 是 Swift+SwiftUI，Android 是 Kotlin+Compose，语言和框架不同。要还原的是：每屏长什么样（布局/卡片/列表/网格）、什么颜色（色板已在对齐规格 §1）、什么字（日语文案逐条照抄，不许翻译）、点了去哪、调哪个后端接口、用哪些字段。
2. **UI 文案保持日语原文**，跟 iOS 一字不差（对齐规格里每屏都列了日语原文）。别翻成中文/英文。
3. Android 现状 = 早期演示桩：只有 UI 桩 + 本地 `MockData.kt` 假数据，**没有任何网络层**（无 retrofit/okhttp/ktor）。所以有两大块从零做：① 网络层（照对齐规格 §「后端 API 契约」接同一个后端、对同样字段）② 把缺的功能屏逐个补齐。
4. 防作弊核心（nonce 一次性随机数 / ECDSA 数字签名 / 设备注册校验 / 卡→学生映射）后端还没写，是单独大议题，本次遇到只记 TODO，不动。
5. **别改 iOS 文件**：iOS 是真值，只读参照。要动 iOS 先问 itsuki。

【路径】
- 对齐蓝图：`00_admin/iOS_Android_对齐规格.md`（**主文档，先通读**）
- 界面截图：`06_assets/app_screens_2026-06-05_ios/`（14 张 + README 映射表）
- iOS（真值，只读）：`03_dev/student_ios/v1/TomoshibiApp/`
- Android（要补）：`03_dev/student_android/v1/`
- 后端（字段/接口真值）：`03_dev/backend/v1/app/`（路由 `app/routers/`，模型 `models.py`，契约 `schemas.py`）

【执行方式 — ultracode 模式（本会话已开 ultracode：质量优先，token 不设限）】
- 用 Workflow 工具做多代理编排，不要手动一个个 Agent。
- 阶段 0 摸底：派并行子代理扫 Android 现状 vs 对齐规格，产出「每个功能在 Android 是 有 / 缺 / 半成品」差异矩阵 + 网络层缺口清单（写报告存 `05_logs/raw/`）。
- 阶段 1+ 逐屏补齐：每屏一个子代理照对齐规格 §对应段 + 截图实装，做完独立验证（gradle 编译）+ 跟 iOS 截图肉眼对照。
- 找差异时多视角并行（界面布局 / 配色 / 文案 / 接口字段），可疑项派 skeptic 子代理对抗验证再保留。
- 醒来根据 Android 真实代码结构现写最优 workflow，别套死模板。

【分阶段执行】
阶段 0 摸底（先做，只产报告别急着改）：扫 Android vs iOS，产出功能差异矩阵 + 网络层缺口。
阶段 1 地基：照对齐规格 §1「设计系统」把 Android 共享组件库补齐（中央 `ui/components/`：Card / Pill / PrimaryButton / GhostButton / Field / TField / TArea / RadioCard / SectionHeader / Avatar / BottomNav / TopRollBar / GlassSheet 等，现在散在各屏内联）。色板/字号/圆角/间距照 §1 表。
阶段 2 网络层：照对齐规格 §「后端 API 契约」从零写 Android 网络层（retrofit 或 ktor），接一模一样的端点、对一模一样的 snake_case 字段、同样的 401/422 错误处理。
阶段 3 骨架 + 登录注册：照 §「导航」补底部 3 tab（申し込み/点呼/マイページ）+ 全局弹窗机制；照 §「登录注册」补登录页 + 注册流程 + 自动登录。
阶段 4 各功能屏逐个补：ホーム → 申し込み（列表+新規申請+各表单）→ マイページ → 減点明細（含 Compose Canvas 折线图）→ バス/宅配/曲/カレンダー/通知 → 点呼/NFC。每屏照对齐规格 §对应段 + 截图。
  · **注意新功能**：番号再設定（学年更新，2026-06-05 新加）iOS 已实装，Android 也要做 —— 见对齐规格「各申请表单」段 + `02_design/system_features.md` §4.2。学生顶部「待更新」横幅 → 选学年/组/出席番号弹窗 → POST `/api/v1/students/me/renew-number`。

【验证铁律 — 不许偷工】
- 每改完 Android 真跑 `gradle` 编译，不能只语法解析。
- 每屏做完跟 `06_assets/app_screens_2026-06-05_ios/` 对应截图肉眼对照（布局/配色/文案）。
- 接后端的屏，字段名跟后端 `schemas.py` 逐个核对（snake_case ↔ Kotlin 命名）。
- 派子代理/codex 干活后独立核实自报，别信「做好了」，多轮对抗复审到收敛。
- 每阶段完成派 codex 只读审查挑刺，自己核实再修。

【完成定义】
差异矩阵每条有结论（已补 / 记 TODO 待决）；Android `gradle` 编译通过；每屏跟 iOS 截图对照一致；产出对齐总结报告存 `05_logs/raw/`。

【禁止】
- 不 push（除非 itsuki 明示）
- commit 不写 Co-Authored-By
- 不碰 iCloud 文档
- 不改 iOS 文件（只读参照）
- 开工前先看 `00_admin/WIP.md`「多会话占用」避免跟别会话撞文件；用显式 pathspec 提交，不 `git add -A`
