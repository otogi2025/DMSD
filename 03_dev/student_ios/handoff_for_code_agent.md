> ⚠️ **DEPRECATED · 2026-04-22 夜**
>
> itsuki 在本 handoff 写完后**推翻了 Xcode WebView 壳方案**，选择 **最简路径**：demo 当天直接用 **普通浏览器（Safari）打开 `designs/Tomoshibi_iOS_PhaseB_v2.html`** 展示 iOS App 效果。
>
> 理由（itsuki 决策）：Phase B HTML 自带 iPhone frame（390×844 带侧键）已经有"像 iPhone App"的视觉效果，Xcode WKWebView 壳多投 0.5-1 天换不到显著体验提升。Demo 重心是后端 + 点呼 flow 跑通，不是 iOS App 精度。
>
> **本文件保留**作推翻痕迹 + AC 叙事素材（"投 0.5 天做 Xcode 壳 vs 直接 Safari" 的最简选择）。
>
> **代码 agent 不需要起 Xcode session**。v2 HTML 就是 demo 产物。未来 v1.0 正式开发 iOS 时，本任务书重新激活作 SwiftUI 起点参考。

---

# Handoff · 学生 iOS App 代码实装任务书（v2） · DEPRECATED

> **收件人**：[Code-Agent]（新起 Xcode 会话）
> **寄件人**：[Mac-demo-sprint] · 2026-04-22 夜
> **优先级**：~~demo 4-28 · 还剩约 6 天~~ · **推翻 → post-demo v1.0 用**
> **范围**：**SwiftUI + WKWebView 壳**（非 73 页 SwiftUI 重写）
> **产物位置**：**`~/dev/TomoshibiiOSApp/`（DMSD 外，和 DMSD 同级）** —— itsuki 指示：VS Code / Xcode 打开独立工程，左代码 + 右 Simulator

---

## 1. 为什么是 WebView 壳不是 SwiftUI 重写

- **时间约束**：6 天内 SwiftUI 重写 73 页不现实
- **视觉保真**：Claude Design HTML 已 pixel-perfect + Liquid Glass 用 CSS `backdrop-filter` 模拟；WebView 里 iOS 26 Safari engine 渲染效果 90%+ 接近真 SwiftUI `.glassEffect()`
- **Demo 真需求**：管理员在 Mac 大屏看 iPhone 17 Pro 模拟器，视觉 90% 够，交互完整就行
- **Post-demo 路径**：demo 通过 → v1.0 渐进用 SwiftUI 重写 native 化
- **itsuki 决策**（2026-04-22 夜）：选方案 A = WebView 壳 + 工程 DMSD 外独立放

---

## 2. 输入材料

### 2.1 HTML 源（C1 + C2 已修，C3 待 Round 2）

```
/Users/kurekoduki/dev/DMSD/03_dev/student_ios/designs/Tomoshibi_iOS_PhaseB_v2.html
```

**v2 = 已修的版本**（2026-04-22 夜 [Mac-demo-sprint] 直接改源重打包）：
- ✅ C1 中文词汇残留 → 日语自然版：点歌→リクエスト曲 / 宿舍墙→寮ウォール / 快递→宅配 / 晚→晩（全量）
- ✅ C2 リュウ イヒ 数据 Web/iOS 同步：W101→M101 / 女寮→男寮 / 4.0→4.5 点 / 迟到 2→5 次 / 欠席 3→2 次 + SEED.points array + SEED.rollcall specials 同步重建
- ⏳ C3 申请类型 kind 与 prompt 不一致（Phase B 是 outing/stay/holiday/return/repair/parcel/guest/other 8 种 · prompt 要 stay/帰国/帰省/タクシー/掃除/欠席届/免点呼 7 种）→ **等 Round 2 Claude Design 补丁** (见 `designs/Round2_Prompt_C3.md`)

**⚠️ 注意**：v1 原版 `Tomoshibi_iOS_PhaseB.html` 保留作对照，代码 agent **用 v2 版本**。

**v2 的 stripped integrity**：template 里 `integrity="sha384-..."` + `crossorigin="anonymous"` 已剥离（否则 SHA hash 不匹配 + file:// CORS 报错 → 白屏）。可直接双击 HTML 跑，也能被 WKWebView 加载。

### 2.2 设计决策权威（供你理解架构）

```
/Users/kurekoduki/dev/DMSD/03_dev/student_ios/IOS_DESIGN_LOG.md   # Q1-8 + N1-20 决策
/Users/kurekoduki/dev/DMSD/03_dev/student_ios/DESIGN_BRIEF.md     # 页面清单
/Users/kurekoduki/dev/DMSD/03_dev/student_ios/round1_handoff/Round1_Prompt.md  # 给 Claude Design 的 prompt 原文
/Users/kurekoduki/dev/DMSD/03_dev/student_ios/designs/QA_Round1_PhaseB.md      # QA 报告
```

### 2.3 App icon 源图

```
/Users/kurekoduki/dev/DMSD/03_dev/student_ios/round1_handoff/references/01_tomoshibi_logo.png
```

465 KB · 白底 + 红橙火焰 + 中央黄球。

**iOS 要求**：App icon 1024×1024 方形 **无圆角 + 无透明背景**（iOS 自动加圆角）。源图已带圆角白底，**需重新导出方形**。代码 agent 用 `sips` 或 Preview.app 处理：
```bash
# 取正方形中心裁切 + 去圆角（iOS 13+ 会自动加圆角 mask）
sips -c 1024 1024 01_tomoshibi_logo.png --out TomoshibiAppIcon_1024.png
```

Phase B HTML 也内嵌一份 icon（manifest UUID `597b0ad5-*.png`，620 KB），但同样带圆角。用源图处理即可。

---

## 3. 技术约束（硬）

| 项 | 要求 |
|---|---|
| Target 平台 | **iOS 26** only |
| 设备 | **iPhone 17 Pro**（Portrait only）+ **iOS Simulator**（无 Apple Developer 账号）|
| Xcode 版本 | Xcode 17（iOS 26 SDK） |
| Bundle ID | `com.itsuki.tomoshibi.demo`（placeholder，itsuki 无 Developer Program） |
| 语言 | Swift + SwiftUI |
| 配置 | 无需后端 / 无需 APNs / 无需 Keychain / 无需 Core NFC |
| Deployment | 只在模拟器跑（不上实机） |
| 工程位置 | **`~/dev/TomoshibiiOSApp/`（DMSD 外）** |

---

## 4. 任务清单

### 4.1 Xcode 项目骨架

**位置**：`~/dev/TomoshibiiOSApp/`（新建，独立工程目录，**不放 DMSD repo 里**）

**为什么独立**：itsuki workflow = VS Code / Xcode 左边代码 + 右边 Simulator；DMSD 是设计/文档仓，不污染。

**App 结构**（~30 行 Swift）:

```swift
// TomoshibiiOSApp.swift
import SwiftUI

@main
struct TomoshibiiOSApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .statusBar(hidden: false)
                .preferredColorScheme(.none) // 跟随系统
        }
    }
}

// ContentView.swift
import SwiftUI
import WebKit

struct ContentView: View {
    var body: some View {
        WebViewContainer()
            .ignoresSafeArea()
    }
}

// WebViewContainer.swift — WKWebView wrapper
import SwiftUI
import WebKit

struct WebViewContainer: UIViewRepresentable {
    func makeUIView(context: Context) -> WKWebView {
        let cfg = WKWebViewConfiguration()

        // iOS 14+ correct API
        let pagePrefs = WKWebpagePreferences()
        pagePrefs.allowsContentJavaScript = true
        cfg.defaultWebpagePreferences = pagePrefs

        // CSS override: 隐藏 Phase B 自带 iPhone frame + dev caption bar
        // （Phase B HTML 内有完整 390x844 iPhone 13 frame + 侧键 + dev caption —
        //  WebView 壳里会和 Simulator iPhone 17 Pro frame 重复，必须隐藏）
        let userScript = WKUserScript(
            source: cssOverrideJS,
            injectionTime: .atDocumentEnd,
            forMainFrameOnly: true
        )
        cfg.userContentController.addUserScript(userScript)

        let wv = WKWebView(frame: .zero, configuration: cfg)
        wv.scrollView.bounces = false
        wv.isOpaque = false
        wv.backgroundColor = .black
        wv.scrollView.backgroundColor = .black

        if let url = Bundle.main.url(
            forResource: "Tomoshibi_iOS_PhaseB_v2",
            withExtension: "html"
        ) {
            wv.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
        }
        return wv
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}

    private var cssOverrideJS: String { """
        const s = document.createElement('style');
        s.textContent = `
            .stage, .caption { display:none !important; }
            .device {
                width:100vw !important; height:100vh !important;
                padding:0 !important; border-radius:0 !important;
                box-shadow:none !important; background:transparent !important;
                position:fixed !important; inset:0 !important;
            }
            .btn-side { display:none !important; }
            .screen {
                position:static !important; inset:auto !important;
                border-radius:0 !important;
                width:100% !important; height:100% !important;
            }
            body { background:#eff2f3 !important; }
        `;
        document.head.appendChild(s);
    """ }
}
```

### 4.2 HTML 放入 App bundle

**步骤**（Xcode 里）:
1. 把 `designs/Tomoshibi_iOS_PhaseB_v2.html` 拖入 Xcode project navigator
2. 勾选 "Copy items if needed"
3. Target Membership 选中 App target
4. Build Phases → Copy Bundle Resources 确认有这个文件

**替换新版本**（itsuki 未来 Round 2/3 出新 HTML）:
- 只换 `Tomoshibi_iOS_PhaseB_v2.html` 文件内容（同名覆盖），不改 Swift
- Xcode 重新 Run → 新版 UI 立即生效

### 4.3 App icon 导入

1. 打开 `Assets.xcassets`，选 AppIcon
2. 用源图 `01_tomoshibi_logo.png` 处理成 1024×1024 方形（见 §2.3）
3. 拖入对应 size slot

### 4.4 Build & Run

- Target: **iPhone 17 Pro (iOS 26.0 Simulator)**
- ▶ Run
- 看到 Simulator 启动 → iPhone 17 Pro frame 出现 → 桌面显示 Tomoshibi 火焰 App icon → 点进去 → Phase B HTML 全屏加载 → 73 页可操作

---

## 5. 已修 + 待修 bug 清单

| # | Bug | 状态 |
|---|---|---|
| **C1** | 中文词汇 6 处残留（点歌 / 宿舍墙 / 快递 / 晚）| ✅ **已修**（v2 HTML）|
| **C2** | リュウ イヒ 数据 Web/iOS 不一致 | ✅ **已修**（v2 HTML · M101 男寮 4.5 分）|
| **C3** | 申请类型 kind 不对齐 prompt 7 种 | ⏳ **等 Round 2 Claude Design 补丁**（见 `designs/Round2_Prompt_C3.md`），itsuki 拿去跑后出 v3 HTML |
| **C4** | Phase B iPhone frame 双层 | ✅ **已修**（CSS override 在 §4.1 WebViewContainer.cssOverrideJS）|
| **I1** | LockoutPage 升级 logic 固定 30 秒 | ⏳ Post-demo TODO（demo 当天管理员不测 3 次错密码）|
| **N1** | Dev caption bar | ✅ **已修**（CSS override 隐藏 `.caption`）|
| **N2** | 登录页显示真 email `otogi2025@gmail.com` | 🤔 itsuki 决定是否改 demo@tomoshibi.jp |
| **I3** | 「早朝練があるため」文案措辞 | 🤔 低优先，post-demo 优化 |

---

## 6. 交付物

代码 agent 完成后应产出：

1. **`~/dev/TomoshibiiOSApp/`** Xcode 工程（`.xcodeproj` + Swift 源 + Assets + 内嵌 HTML）
2. **`~/dev/TomoshibiiOSApp/README.md`**：
   - 如何 build（Xcode 17 + iPhone 17 Pro simulator）
   - 如何 itsuki 替换未来 Round 2/3 HTML（只换文件，不改 Swift）
   - 已知 bug + 修复状态
   - Demo 前的验证清单
3. **第一次成功 Run 的 Simulator 截图**（放 `~/dev/TomoshibiiOSApp/screenshots/`）

---

## 7. 不该做的

- ❌ **不要重写 SwiftUI** —— 73 页 SwiftUI 重写 6 天做不完，且 itsuki 明确选 WebView 路径
- ❌ **不要把工程放 DMSD 里** —— itsuki 明确要求独立（VS Code 左 / Simulator 右 workflow）
- ❌ **不要改 Phase B v2 HTML 原文件** —— 那是设计权威；修改走 CSS inject 或让 Round 2 Claude Design 重出
- ❌ **不要接真后端** —— demo 当天签到走 iPhone Shortcuts 绕过 iOS App（4-22 晚定案），App 纯展示
- ❌ **不要实装 Core NFC** —— WebView 里没法调 iOS 原生 NFC API，demo 也不需要
- ❌ **不要加 Apple Developer 证书流程** —— itsuki 无账号，只在 Simulator 跑
- ❌ **不要误删 QA 没 cover 的 bug** —— 遇到可疑 bug ping 回来问

---

## 8. 联系

遇到阻塞问题：
- **需求层**（"这个功能要不要做"）→ 回 [Mac-demo-sprint]（我）或 itsuki
- **架构层**（"整个模块该怎么组织"）→ 回 itsuki 拍板
- **Claude Design 补丁**（比如 C3 需要 Round 2）→ itsuki 自己发 prompt

---

## 9. 验证 checklist（代码 agent Run 完后自测）

- [ ] Simulator 启动 iPhone 17 Pro iOS 26，frame 正确
- [ ] App icon 桌面显示为火焰 logo
- [ ] 点 App 进入 → Splash 淡入 → 注册 flow（`/register/1`）
- [ ] **没有双层 iPhone frame**（CSS override 生效）
- [ ] **没有 dev caption bar**（"↻ リセット / 🏠 Home" 被隐藏）
- [ ] 注册 4 step 输入 リュウ イヒ / 2006-10-14 / 女 / 一般寮生 / ... / 密码 8 字以上 → 完成
- [ ] Login 页输入 `00` + 任意密码 → 进 Home
- [ ] Home 扣分卡显示 **4.5 点**（不是 4.0）+ 迟到 5 回 · 欠席 2 回
- [ ] Home 点歌卡 → 点进去标题是 **リクエスト曲**（不是 "点歌"）
- [ ] 宿舍墙卡 → 标题 **寮ウォール**
- [ ] 快递 → **宅配**
- [ ] マイページ → 個人情報 显示 **男寮 M101**
- [ ] 中央 ⭐ 点呼按钮 → sheet 滑上来 → Liquid Glass 背景 + キャンセル 可关闭
- [ ] 长按左上返回 0.4 秒 → Breadcrumb popup 弹出
- [ ] 暗色模式切换（Simulator Settings → Developer → Dark Appearance）→ 页面颜色适配

---

**END** — 代码 agent 开 session 时优先读此文件 + QA 报告 §2-§4 + IOS_DESIGN_LOG §2 架构段。
