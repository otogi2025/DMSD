# 03_dev/student_ios/v1/

**学生 iOS v1.0 实装 — Swift / SwiftUI**。

## 实装位置 — 独立 repo

Swift 实装代码 **不在本 DMSD repo**，而是在独立 GitHub repo：

```
~/dev/TomoshibiiOSApp/
├── TomoshibiApp/         ← Swift 主体（Features/ Foundation/ Root/）
├── TomoshibiApp.xcodeproj
├── refs/                 ← DMSD 内设计档案的物理拷贝（cloud agent 用）
├── REMOTE_AGENT_GUIDE.md
├── STATUS.md
└── ...
```

GitHub: `otogi2025/Tomoshibi-iOS`

## 为什么独立

- itsuki workflow: VS Code / Xcode 左代码 + 右 Simulator
- DMSD 是设计/文档仓，iOS Swift 实装是另一种类型的产出（pixel-level fidelity 的真 SwiftUI）
- 跨 repo 同步规则见 `CLAUDE.md §文档一致性规则 → 跨 repo 同步规则`

## 启动 Xcode

```bash
open ~/dev/TomoshibiiOSApp/TomoshibiApp.xcodeproj
# 选 iPhone 17 Pro Simulator（iOS 26.0）
# ▶ Run
```

## 设计权威

- 共用规则: `02_design/system_features.md`
- iOS 専属设计: `../IOS_DESIGN_LOG.md`
- HTML プロトタイプ参考: `../demo/Tomoshibi_iOS_PhaseB_v2.html`（pixel-level fidelity 起点）
