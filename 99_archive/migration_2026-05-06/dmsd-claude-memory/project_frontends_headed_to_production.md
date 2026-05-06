---
name: iOS + Web 前端大概率真上线（非 demo 一次性）
description: 2026-04-24 itsuki 表态 — 为 4-28 演示做的 iOS Swift app + teacher_web/round3 两个前端，演示通过后会直接拿去做 v1.0 产品化基础，不会重写
type: project
originSessionId: 9a96438b-2521-4457-b233-b57724553507
---
**事实**（2026-04-24 itsuki 原话）：「虽然我现在一切都是为了给老师演示才做成现在这个样子的，但是这两个前端，Web 和 APP 的前端，我大概率也会真的拿去用。」

**Why**: 这影响很多决策的权重 —
- 硬编码 SEED 数据、demo 捷径、mock 状态机、假 API response 等 "临时代码"，如果不显式标记和清理，会带着上生产
- 跨会话再改 Web / iOS 时要考虑"这段代码生产版也要见人"，不能只图演示效果乱糊
- v1.0 架构 spec 不要推翻这两个前端的整体结构（Router / AppStore / PhaseB 视觉），只做替换（前端 → 真后端）

**How to apply**:
- 新功能在 iOS / Web 落地时：判断"这段代码生产版会不会删" → 会删的显式加 `// DEMO-ONLY` 注释 / 记 `project_demo_scaffolds_to_remove_before_v1.md`
- Spec 写作时把 "4-28 演示版" 和 "v1.0 产品版" 分开讨论（哪些字段 demo 是硬编码、生产要接后端）
- 跟 itsuki 说 "这是 demo 方便做的, 生产要改" 时 → 同时记 demo-scaffolds memory，不然就是口头说说等于没记
- 早期 iOS 代码 throwaway 的 memory（`feedback_ios_early_code.md`）只适用于 2026-04 以前旧代码；**当前 `~/dev/TomoshibiiOSApp/` 不是 throwaway**
