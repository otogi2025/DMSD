---
name: 修 build error 不替 itsuki 撤销设计意图
description: CC 遇到 build error / API deprecated / 工具链报错时，不要单方面回退到「老格式 / 传统方案」 — 那等于撤销 itsuki 主动选择的设计意图。先诊断到根因再修，找不到根因要先报告
type: feedback
originSessionId: ac7a3961-2ae1-4777-b9d0-3f00ae76a78e
---
CC 修 build error / 工具链报错 / API deprecated 时，**不能为了让 build 通过就单方面回退到老格式 / 传统方案**。如果 itsuki 主动选择了新格式 / 新设计 / 新架构，CC 必须先诊断到根因再修。诊断不出来要先**报告 + 列方案让 itsuki 选**，不能私自走 fallback 用「BUILD SUCCEEDED」伪装"修好了"。

**Why:** 2026-05-04 iOS bug 修复会话 itsuki 戳穿 case：
1. itsuki commit `f7747f9` 主动用 Apple Liquid Glass `.icon` 新格式（在 `06_assets/icons/Tomoshibi icon.icon/` + `03_dev/.../AppIcon.icon/`）
2. Xcode 26 build error: actool 找不到 AppIcon → CC 第一次直接**回退到传统 `.appiconset` + 用 v2 PNG 替换 Icon-1024.png**，xcodebuild 通过报告完事
3. itsuki 立刻怒怼："不对，我现在的图标不对，我现在图标还是白色背景 / 这个新的图标，你到底更新了没？"
4. 戳穿点：CC 替 itsuki 撤销了他主动选择的 Liquid Glass 设计意图。**真根因**（CC 第二次重诊+WebSearch 才找到）：Xcode 26 把 `.icon` 当**单一文件 reference** 处理，不能塞 `.xcassets/` 里 — 必须移到项目根 + 改 pbxproj 加 PBXFileReference

**How to apply:**
- 修 build / 工具链 error 第一步：**判断这个 error 是不是涉及 itsuki 主动选择的格式 / 设计 / 架构**
  - 看 git log / commit message — 有没有「feat(...)」「chore(...)」体现 itsuki 拍板换新方案
  - 看相关文件路径有没有 untracked / 新增 — 这些往往是 itsuki 还没 commit 的设计意图
- 涉及设计意图的 build error，**修复路径必须是「让新格式真工作」而非「回退到老格式」**
- 如果 30 分钟试了多种方法都修不通新格式：**报告 + 列 A/B 方案给 itsuki 选**，不能默默回退
- 不要把 BUILD SUCCEEDED 当成"修好了"的唯一信号 — 还要看**视觉效果是否符合 itsuki 的设计意图**（Liquid Glass 火焰 vs 白底 v1 PNG 是完全不同的产物）
- 涉及 untracked 文件的删除 / 移动 / 替换前 — 必须先弄清楚这是 itsuki 在做的设计还是该清理的垃圾
