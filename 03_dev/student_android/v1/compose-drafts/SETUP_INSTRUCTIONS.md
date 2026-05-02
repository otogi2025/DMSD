# Tomoshibi-Android · 工程 bootstrap 操作清单

> **作用**：等 Android Studio 装完后，按本清单走完 setup → 把 `compose-drafts/` 落地为可 build 的真实工程。
> **路径假设**：本地工程 = `~/dev/TomoshibiAndroidApp/`，远端 repo = `github.com/otogi2025/Tomoshibi-Android`。

---

## 0. 前提（CC 已完成）

- ✅ aria2 多线程下载 Android Studio dmg
- ✅ `compose-drafts/` 36 个 .kt 文件就位（4 主题 + 5 框架 + 2 数据 + 1 icons + 1 组件 + 23 屏）
- ✅ ANDROID_DESIGN_LOG.md 落地

## 1. itsuki 必做：GitHub repo 创建

1. 浏览器打开 https://github.com/new
2. 字段：
   - Repository name: `Tomoshibi-Android`
   - Description: `Tomoshibi 寮生活アプリ — Android 学生 App（Kotlin + Jetpack Compose）`
   - Public ✅（参照 DMSD repo 2026-04-29 起 public）
   - **不要** initialize with README / .gitignore / license（让 Android Studio New Project 自带的 .gitignore 留下来）
3. 点 Create repository
4. 复制 git URL（HTTPS 形式：`https://github.com/otogi2025/Tomoshibi-Android.git`）

## 2. CC 接管：brew install --cask android-studio

下载完成后，CC 跑：
```bash
brew install --cask android-studio
```
（此时 dmg 已在 brew cache，install 步骤只 mount + 拷贝 .app 到 /Applications，2-3 分钟）

## 3. itsuki 必做：Android Studio 首次启动 wizard

1. 启动 `/Applications/Android Studio.app`
2. Wizard 步骤（**全部默认 Next**，除非下面标 ⚠）：
   - **Import settings**: Do not import settings → Next
   - **Welcome wizard**: Standard → Next
   - **SDK Components Setup** ⚠：勾选
     - Android SDK
     - Android SDK Platform（最新 API 35）
     - Performance（**Apple Silicon 必勾 — Intel HAXM 不需要**）
     - Android Virtual Device
     - 路径默认 `~/Library/Android/sdk`
   - **Verify Settings** → Finish → SDK 开始下载（800MB-1.5GB，~10-30 min 看网速）

## 4. itsuki 必做：创建 AVD（Android Virtual Device = 模拟器）

启动后主页 → More Actions → Virtual Device Manager → Create Virtual Device

| 项 | 选择 |
|---|---|
| Category | Phone |
| Device | **Pixel 8**（412×892，最接近 Tomoshibi 设计稿尺寸）|
| System Image | **API 35（Android 15, "VanillaIceCream"）arm64-v8a** ⚠ Apple Silicon 必选 arm64 |
| AVD Name | `Pixel_8_API_35` |
| Startup orientation | Portrait |
| Camera | Webcam0 |
| 其他 | 默认 |

→ Finish。第一次启动模拟器需要 1-2 min（下次启动 ~15s）。

## 5. itsuki 必做：New Project 创建工程

Android Studio 主页 → New Project

| 步骤 | 选择 |
|---|---|
| Template | **Empty Activity**（Phone and Tablet → Empty Activity）|
| Name | `Tomoshibi` |
| Package name | `jp.tomoshibi.android` |
| Save location | `/Users/itsuki/dev/TomoshibiAndroidApp` |
| Language | Kotlin |
| Minimum SDK | **API 26: Android 8.0 (Oreo)** |
| Build configuration language | Kotlin DSL (build.gradle.kts) |

→ Finish。Gradle sync 5-15 min（下载 Gradle wrapper + Kotlin / Compose 依赖）。

## 6. CC 接管：drop in compose-drafts/

待 Gradle sync 完成后：

```bash
# 1. 删掉 wizard 自带的 default Color/Theme/Type
rm -rf ~/dev/TomoshibiAndroidApp/app/src/main/java/jp/tomoshibi/android/ui/theme

# 2. 拷贝 compose-drafts 全部 .kt 到工程
cp -R ~/dev/DMSD/03_dev/student_android/v1/compose-drafts/app/src/main/java/jp/tomoshibi/android/* \
       ~/dev/TomoshibiAndroidApp/app/src/main/java/jp/tomoshibi/android/

# 3. 覆盖 wizard 生成的 MainActivity.kt（compose-drafts 版含 LocalAppStore + Theme）
# （上一步 cp 已经覆盖）

# 4. 加依赖到 libs.versions.toml + app/build.gradle.kts（见下 §7）
```

## 7. 添加依赖

`gradle/libs.versions.toml` 顶部 `[versions]` 加：

```toml
nav-compose = "2.8.5"
datastore = "1.1.1"
serialization = "1.7.3"
material-icons-extended = "1.7.6"
```

`[libraries]` 加：

```toml
androidx-navigation-compose = { module = "androidx.navigation:navigation-compose", version.ref = "nav-compose" }
androidx-datastore-preferences = { module = "androidx.datastore:datastore-preferences", version.ref = "datastore" }
kotlinx-serialization-json = { module = "org.jetbrains.kotlinx:kotlinx-serialization-json", version.ref = "serialization" }
androidx-material-icons-extended = { module = "androidx.compose.material:material-icons-extended", version.ref = "material-icons-extended" }
```

`[plugins]` 加：

```toml
kotlin-serialization = { id = "org.jetbrains.kotlin.plugin.serialization", version.ref = "kotlin" }
```

`app/build.gradle.kts`：
- `plugins { ... }` 里加 `alias(libs.plugins.kotlin.serialization)`
- `dependencies { ... }` 里加：
  ```kotlin
  implementation(libs.androidx.navigation.compose)
  implementation(libs.androidx.datastore.preferences)
  implementation(libs.kotlinx.serialization.json)
  implementation(libs.androidx.material.icons.extended)
  ```

## 8. 第一次 Gradle sync + build + run

1. Android Studio 顶栏点 🐘 (Sync Project with Gradle Files) — 拉新依赖（2-5 min）
2. 顶栏选 `Pixel_8_API_35` AVD
3. ▶ Run（绿三角）

**预期**：emulator 启动 → 显示 Splash 灯字 → 1.4 秒后跳 Onboarding（stub 屏 "OnboardingScreen — TODO"）

## 9. 第一次 git commit + push 到 Tomoshibi-Android

```bash
cd ~/dev/TomoshibiAndroidApp
git init
git add -A
git commit -m "feat(bootstrap): initial Compose project with Suzu theme + 23-screen routing skeleton"
git branch -M main
git remote add origin https://github.com/otogi2025/Tomoshibi-Android.git
git push -u origin main
```

## 10. 接下来

- P2: 实装 Onboarding + Account + Welcome 真实 UI（替换 stub）
- P3: 实装 Applications 流（list + new + detail）
- P4: 实装 MyPage + Settings + Deduction + RollCall
- P5: 实装 Community 7 屏

**预期 build error**：CC 写代码没编译过，会有 import 错 / API mismatch / Material3 deprecation 等。第一次 build 后 itsuki 把 error log 发给 CC，逐个修。
