# dev/student_ios/v1/

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

## 构建（先看这段再动手）

工程有 **两个 scheme**（scheme = Xcode 里的构建方案），已在 `project.yml` 定义好：

| scheme | 用途 |
|---|---|
| `TomoshibiApp` | 正式版（不含任何 demo 代码）|
| `TomoshibiAppDemo` | 演示版（自带 `DEMO` 编译 flag）— 要演示版直接选这个 scheme，**不要手动加 `SWIFT_ACTIVE_COMPILATION_CONDITIONS`** |

```bash
# 打开本目录下的 TomoshibiApp.xcodeproj
# 顶部 scheme 切换器选 TomoshibiApp（正式）或 TomoshibiAppDemo（演示）
# 选 iPhone 17 Pro Simulator → ▶ Run
```

命令行构建 / 双版本差异详见 `BUILD.md`。

**工程配置的真值是 `project.yml`**（xcodegen 配置文件）— `.xcodeproj` 由 xcodegen 从它生成，在 Xcode 里手动改的工程配置会在下次 xcodegen 重新生成时被擦掉；改配置必须写进 `project.yml` 再重新生成。

## 设计权威

- 共用规则: `design/system_features.md`
- iOS 専属设计: `../IOS_DESIGN_LOG.md`