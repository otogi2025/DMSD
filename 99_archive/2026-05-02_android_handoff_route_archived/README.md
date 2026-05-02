# Android Round 1 Handoff 路线归档

**归档日期**：2026-05-02
**原位置**：`03_dev/student_android/v1/round1_handoff/`
**归档原因**：路线变更 — 改用 Claude Design 出的 standalone HTML 蓝图 + CC 直接对译 Compose

---

## 原来的路线（已废）

itsuki 截 iOS demo 15-20 张关键页截图 → 打包 `round1_handoff/` 全套（Round1_Prompt.md + iOS_Inventory + Design_Tokens + 28 个 .swift 源码 + spec excerpts + 截图）→ 拖给 **Claude Design**（claude.ai 网页端 design 模式）→ 它出 3 variations × 5 关键页 → itsuki 选 1 个 → Phase B 出全 Compose 工程 → clone 到 `~/dev/Tomoshibi-Android/`。

## 问题

1. **多了一层中转**：iOS 已有完整设计 + itsuki 又在 Claude Design 上画了完整的 Tomoshibi App 蓝图（standalone HTML），没必要再让 Claude Design 重新出一遍 Compose
2. **CC 不在 loop**：handoff 走 Claude Design 网页端，CC 不参与设计→实装流程，逐屏对译时上下文断裂
3. **AC 叙事考虑**：itsuki 自己说每段代码要能在面试讲，外包出去的工程拿回来再讲不如 CC 边写边教

## 改成的路线（2026-05-02 拍板）

1. itsuki 在 Claude Design 上画好的 Tomoshibi App 蓝图 → **Export as Handoff to Claude Code** → 给 CC
2. CC 在本地 Android Studio 工程（独立 repo `Tomoshibi-Android`）里 **逐屏对译** 成 Kotlin + Jetpack Compose
3. 每写一段都给 itsuki 解释代码做什么（AC 面试要能讲）
4. 不派 sub agent / Claude Design

## 这个文件夹里还有用的资产

虽然主路线废了，**以下文件还能当参考**（CC 写 Compose 时如果需要可以回查）：

| 文件 | 还能用在哪 |
|---|---|
| `Design_Tokens.md` | iOS 的颜色 / 字体 / 圆角 / 间距 token，写 Compose 时确保跨平台一致 |
| `iOS_Inventory.md` | 31 个 .swift 文件索引 + Route + 数据模型 — 翻译 Compose 时核对 Route case 名 1:1 |
| `iOS_source_pack/*.swift` | 28 个 iOS 关键 .swift 源码，遇到 iOS 行为不确定时回查 |
| `spec_excerpts/system_features.md` | 共用规则（账号 / 扣分 / session）— 但权威源已经在 `02_design/system_features.md`，这是当时的 snapshot |
| `Round1_Prompt.md` | 已废 — 当时给 Claude Design 的 prompt，CC 不需要 |
| `截图/` | 老 demo 的截图，可能跟当前 standalone HTML 蓝图有出入，参考价值低 |

## 如果想恢复 Claude Design 路线

`mv` 整个 `round1_handoff/` 回 `03_dev/student_android/v1/` 即可。但请先想清楚为什么之前废了。
