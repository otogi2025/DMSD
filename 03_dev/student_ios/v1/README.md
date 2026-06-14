# 03_dev/student_ios/v1/

**学生 iOS v1.0 实装 — Swift / SwiftUI**。

## 实装位置

Swift 实装代码就在本目录下：

```
TomoshibiApp/         ← Swift 主体（Features/ Foundation/ Root/）
TomoshibiApp.xcodeproj
TomoshibiAppTests/
...
```

> 早期曾用独立 repo 模式，2026-05-06 退役，全部代码统一移入本目录。

## 为什么放在 DMSD 内

- itsuki workflow: VS Code / Xcode 左代码 + 右 Simulator
- 5 端统一在 DMSD monorepo 内管理，版本 / commit 单一来源
- iOS Swift 实装是 pixel-level fidelity 的真 SwiftUI 产出

## 启动 Xcode

```bash
# 打开本目录下的 TomoshibiApp.xcodeproj
# 选 iPhone 17 Pro Simulator（iOS 26.0）
# ▶ Run
```

## 设计权威

- 共用规则: `02_design/system_features.md`
- iOS 専属设计: `../IOS_DESIGN_LOG.md`
- HTML プロトタイプ参考: `../demo/Tomoshibi_iOS_PhaseB_v2.html`（pixel-level fidelity 起点）
