---
name: UI placeholder 禁用剧情化例子
description: SwiftUI / Web / Android UI 文本输入 placeholder 不要写「例：友人の結婚式…」这种剧情化例子，用中性字段提示（如「理由を入力」「住所を入力」）— itsuki 2026-05-04 怒怼拍板
type: feedback
originSessionId: ac7a3961-2ae1-4777-b9d0-3f00ae76a78e
---
UI 文本输入字段（TField / TArea / `<input>` / `EditText` 等）的 placeholder **不要写「例：xxx」剧情化例子**。剧情例子（祖父母宅 / 友人の結婚式 / 祖母の通院 / 祖父の米寿祝い / 山田 花子 等）一律删，改成中性字段提示。

**Why:** 2026-05-04 itsuki 真机看到外泊申请 +外泊修改届 placeholder 写「例：友人の結婚式に出席するため」「例：祖母の通院と重なったため」等怒怼 ——「你不要给我写例子了，你写的例子太他妈蠢了」。后续 grep 全 iOS app 删了 8 处「例：xxx」。剧情化 placeholder 的真问题：
1. **诱导虚假填写** — 用户看到「友人の結婚式」会编一个相似理由
2. **审美降智** — 严肃应用（学校宿舍点呼系统）里 jarring，每次打开看到都讨厌
3. **隐私 / 文化预设错位** — 「祖母の通院」「祖父の米寿祝い」假设了核心家庭 + 日本文化语境，海外学生（itsuki 自己）这些预设全错位
4. **placeholder 本身已是 hint，不需要再加「例」前缀** — Material Design / HIG 都建议中性 placeholder

**How to apply:**
- 写新字段 placeholder 时，**不要从 demo / prototype 直接抄剧情例子**到生产代码（这是 CC 之前的失职 — JSX demo 抄到 Swift 时没区分 demo vs 生产）
- 模式：
  - 理由类 → 「理由を入力してください」/「修改の理由を入力してください」
  - 地点类 → 「滞在先住所」/「宿泊先住所」/「行き先を入力」
  - 名前类 → 「氏名」/「来訪者氏名を入力」
  - 数值类 → 「体温（℃）」（带单位即可，不写「例: 37.2」）
  - 标识类 → 「空港名」（不写「例：岡山空港（OKJ）」IATA 码这种格式提示）
- 唯一例外：纯字段格式提示（如 phone「090-1234-5678」格式 mask）— 但这种用 mask / formatter，不用 placeholder 例子
- 改完跑 grep `'例：' src/` 全 repo 找漏
