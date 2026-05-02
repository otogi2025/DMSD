# compose-drafts/ 归档（2026-05-02 夜）

**原位置**：`03_dev/student_android/v1/compose-drafts/`
**归档原因**：被 Tomoshibi-Android repo 取代，DMSD 侧不再需要这个 staging copy

## 来历

5-02 夜 Tomoshibi Android bootstrap 时，CC 在 Android Studio 工程还没建好之前，先在 DMSD 侧 `03_dev/student_android/v1/compose-drafts/` 写了 36 个 .kt 文件作为「待落地的草稿」。Android Studio 工程建好后，全部 cp 进 `~/dev/TomoshibiAndroidApp/`，从那时起 Tomoshibi-Android repo（GitHub `otogi2025/Tomoshibi-Android`）成为 Android 代码的 single source of truth。

## 当前 single source

- **Android 代码** = https://github.com/otogi2025/Tomoshibi-Android（独立 repo，参照 iOS Tomoshibi-iOS 模式）
- **Android 设计文档** = `03_dev/student_android/ANDROID_DESIGN_LOG.md`（DMSD 侧，权威设计源）

## 这个归档里有什么

- `compose-drafts/SETUP_INSTRUCTIONS.md` — 当时给 itsuki 的 10 步 bootstrap 操作清单（已完成执行）
- `compose-drafts/app/src/main/java/jp/tomoshibi/android/...` — 36 个 .kt 文件初稿
  - 这些文件后续在 Tomoshibi-Android repo 被 4 会话并行 (feature/A/B/C/D) 大幅升级 + 重写
  - 历史价值：保留 5-02 bootstrap 时的"第一版" — Tomoshibi-Android repo 的 `feat(bootstrap): initial Tomoshibi Android Compose 工程` commit (`f48fc09`) 内容跟这里几乎一致

## 不要恢复

如果未来想看 Android 代码当前最新版 → 去 Tomoshibi-Android repo，不要恢复这里。
