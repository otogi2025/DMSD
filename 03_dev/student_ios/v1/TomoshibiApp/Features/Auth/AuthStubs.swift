// AuthStubs.swift — Agent A · Auth feature v2 · HTML-fidelity 1:1 rewrite
//
// 对等 refs/phaseB_src/c13988a3__SplashPage_OnboardingPage_RegisterDonePage.js
// 9 个 struct View（+ private helpers）:
//   1. SplashView            — 火焰 wordmark · 2s fadeIn · → .onboarding
//   2. OnboardingView        — 3 slide TabView + スキップ · → .login
//   3. RegisterStep1View     — 氏名 / 生年月日 / 性別 / アバター
//   4. RegisterStep2View     — 点呼区分 radio (一般寮生 / サッカー部)
//   5. RegisterStep3View     — メール / 電話
//   6. RegisterStep4View     — パスワード × 2
//   7. RegisterDoneView      — ✅ zoom + アカウント番号 00
//   8. LoginView             — 番号 / メール tab · magic seed
//   9. LockoutView           — 30 秒 カウントダウン
//   10. PwResetView          — 寮監ご連絡説明
//
// Fidelity 铁律:
//   - 日文字符串逐字照抄 JSX（JSX 的 "晚" 按 v2 HTML 规约替换为 "晩"）
//   - fontSize / padding / spacing 严格对照 JSX inline style
//   - 颜色 = T.* tokens（JSX 独立 hex 用 Color(hex:) inline override）
//   - 自绘 icon（flame / check / lock / phoneTap / mail / calendar）不用 SF Symbols
//   - 动画: fadeIn 0.2s → .easeIn(0.2) · zoom 0.22s → .easeOut(0.22) · slideUp 0.34s → spring
//   - 无 NavigationStack · 无 .sheet() · Route 驱动
//   - Liquid Glass 仅 .glassEffect 许可 — Auth 流程不用 glass（bg = T.pearl / paper / gradient）

import SwiftUI

// Apple Image Playground · 设备本地 AI 插画生成（iOS 18.2+，仅 Apple Intelligence 支持机型）
// → 用于注册第 1 步的头像 AI 生成功能（RegisterStep1View）
import ImagePlayground

// ═══════════════════════════════════════════════════════════════════════════════
// MARK: - §0.1 Splash

// ═══════════════════════════════════════════════════════════════════════════════
//
// JSX 对等:
//   background: radial-gradient(ellipse at 50% 42%, #e8f4f6 0%, #eff2f3 60%, #e4ebec 100%)
//   logo 160×160, boxShadow 0 20px 60px rgba(31,107,116,0.2), borderRadius 36
//   wordmark "Tomoshibi · 灯火"  fontSize:15, fontWeight:700, letterSpacing 0.12em
//   version  "v0.1.0-demo"        fontSize:11, mono
//   fadeIn 1s（JSX）— 以 iOS 感觉 0.8s fadeIn + 2s 总停留
//   → router.replace(.onboarding)  (assignment override, JSX 走 /login)

struct SplashView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore
    @State private var appear: Bool = false
    /// 「介绍页看过没」标记 — @AppStorage 自动读写 UserDefaults（手机本地小仓库）。
    /// 首次安装本机没这条记录 → 默认 false → 走一次介绍页；OnboardingView 看完/跳过置 true，以后再不弹。
    @AppStorage("hasSeenOnboarding") private var hasSeenOnboarding = false

    var body: some View {
        ZStack {
            // 白/极浅灰 bg（Image #29 效果）
            LinearGradient(
                colors: [Color.white, Color(hex: 0xF4F7F8)],
                startPoint: .top, endPoint: .bottom
            )
            .ignoresSafeArea()

            VStack(spacing: 0) {
                Spacer()

                // 白色 rounded square card · 含火焰 logo
                ZStack {
                    RoundedRectangle(cornerRadius: 32, style: .continuous)
                        .fill(Color.white)
                        .shadow(color: Color.black.opacity(0.08), radius: 20, x: 0, y: 10)
                        .shadow(color: Color.black.opacity(0.04), radius: 2, x: 0, y: 1)

                    Image("TomoshibiFlame")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 120, height: 120)
                }
                .frame(width: 168, height: 168)

                Spacer().frame(height: 36)

                VStack(spacing: 8) {
                    Text("Tomoshibi · 灯火")
                        .font(.system(size: 18, weight: .bold))
                        .foregroundStyle(T.primaryDk)
                        .kerning(2.2)
                    Text(AppVersionTag.full)
                        .font(.system(size: 11, design: .monospaced))
                        .foregroundStyle(T.inkMute)
                }

                Spacer()
                Spacer()
            }
            .opacity(appear ? 1 : 0)
        }
        .onAppear {
            withAnimation(.easeIn(duration: 0.6)) { appear = true }
            Task {
                try? await Task.sleep(nanoseconds: 2_200_000_000)
                await MainActor.run {
                    // 启动跳转逻辑：
                    //   - Keychain 已恢复 token → 自动登录跳 home（老用户不看介绍页）
                    //   - 没 token + 本机没看过介绍 → 走一次介绍页（首次安装的新用户）
                    //   - 没 token + 已看过介绍 → 跳 login（老用户再登录 / 新用户在 login 点「新規登録」注册）
                    // 介绍页只在首次安装看一次（hasSeenOnboarding 标记），不每次启动都弹（2026-05-07 itsuki 拍板「太烦」）
                    if app.authToken != nil {
                        router.replace(.home)
                    } else if !hasSeenOnboarding {
                        router.replace(.onboarding)
                    } else {
                        router.replace(.login)
                    }
                }
            }
        }
    }
}

#Preview("Splash") {
    SplashView()
        .environmentObject(RouterStore())
        .environmentObject(AppStore())
}

/// 自绘 Tomoshibi 火焰 logo（红橙外焰 + 黄色灯芯 · Image #29 样式）
private struct TomoshibiFlameLogo: View {
    var body: some View {
        GeometryReader { geo in
            let w = geo.size.width
            let h = geo.size.height
            ZStack {
                // 外焰（红橙渐变，描边样式）
                FlameShape()
                    .fill(
                        LinearGradient(
                            colors: [
                                Color(hex: 0xFF6A3D), // 橙红 top
                                Color(hex: 0xE23A1F), // 深红 bottom
                            ],
                            startPoint: .top, endPoint: .bottom
                        )
                    )
                    .overlay(
                        FlameShape()
                            .stroke(Color(hex: 0x3A1008), lineWidth: 1.5)
                    )

                // 黄色灯芯（底部中央圆）
                Circle()
                    .fill(
                        RadialGradient(
                            colors: [Color(hex: 0xFFF3A8), Color(hex: 0xFFD24D)],
                            center: .center,
                            startRadius: 0,
                            endRadius: w * 0.2
                        )
                    )
                    .overlay(
                        Circle().stroke(Color(hex: 0x3A1008), lineWidth: 1.2)
                    )
                    .frame(width: w * 0.32, height: w * 0.32)
                    .offset(y: h * 0.18)
            }
        }
    }
}

private struct FlameShape: Shape {
    func path(in rect: CGRect) -> Path {
        var p = Path()
        let w = rect.width
        let h = rect.height
        // teardrop-ish flame
        p.move(to: CGPoint(x: w * 0.5, y: 0))
        p.addCurve(
            to: CGPoint(x: w, y: h * 0.62),
            control1: CGPoint(x: w * 0.95, y: h * 0.22),
            control2: CGPoint(x: w, y: h * 0.42)
        )
        p.addCurve(
            to: CGPoint(x: w * 0.5, y: h),
            control1: CGPoint(x: w, y: h * 0.88),
            control2: CGPoint(x: w * 0.78, y: h)
        )
        p.addCurve(
            to: CGPoint(x: 0, y: h * 0.62),
            control1: CGPoint(x: w * 0.22, y: h),
            control2: CGPoint(x: 0, y: h * 0.88)
        )
        p.addCurve(
            to: CGPoint(x: w * 0.5, y: 0),
            control1: CGPoint(x: 0, y: h * 0.34),
            control2: CGPoint(x: w * 0.2, y: h * 0.18)
        )
        p.closeSubpath()
        return p
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// MARK: - §0.2 Onboarding

// ═══════════════════════════════════════════════════════════════════════════════
//
// JSX 对等:
//   background: T.paper
//   top-right スキップ button (fontSize:14, fontWeight:500, T.inkSub)
//   3 slides: [点呼自動化 / 申請線上化 / 生活機能一体]
//   illustration: 220×220 rounded 28 with linear-gradient + Ic.phoneTap/mail/calendar(40) scaled 2.6
//   tag   : fontSize:11, weight:700, letterSpacing 0.18em, uppercase
//   title : fontSize:26, weight:700, lineHeight:1.35
//   body  : fontSize:14, lineHeight:1.7
//   dots  : active 24×8 / inactive 8×8, gap:8
//   CTA   : 次へ / 始める (PrimaryBtn full)
//   → router.replace(.login)   (assignment override, JSX 走 /register/1)

struct OnboardingView: View {
    @EnvironmentObject var router: RouterStore
    // 看完标记 — 置 true 后 SplashView 不再走介绍页（与 SplashView 同一个 @AppStorage key）
    @AppStorage("hasSeenOnboarding") private var hasSeenOnboarding = false
    @State private var idx: Int = 0

    /// 介绍页一行功能（仅 AI 页用，每行一个小图标 + 一句话）
    private struct Feature {
        let icon: String
        let label: String
    }

    private struct Slide {
        let sfSymbol: String
        let title: String
        let sub: String? // 页 1-3 用（可含换行）
        let features: [Feature]? // 页 4（AI）用：nil = 普通页
        let footnote: String? // 页 4 设备机种小字
        let gradStart: UInt32
        let gradEnd: UInt32
        let fg: Color

        init(
            sfSymbol: String, title: String,
            sub: String? = nil, features: [Feature]? = nil, footnote: String? = nil,
            gradStart: UInt32, gradEnd: UInt32, fg: Color
        ) {
            self.sfSymbol = sfSymbol
            self.title = title
            self.sub = sub
            self.features = features
            self.footnote = footnote
            self.gradStart = gradStart
            self.gradEnd = gradEnd
            self.fg = fg
        }
    }

    private let slides: [Slide] = [
        // ① 点呼 — v1.0 只支持「卡贴点呼机」，不支持手机签到，故只讲卡（手机签到留 v1.1）
        Slide(
            sfSymbol: "wave.3.right.circle.fill",
            title: "カードでかんたん点呼",
            sub: "カードをかざすだけ。\n毎晩の点呼が数秒で完了。",
            gradStart: 0xE8F4F6, gradEnd: 0xA8DCE2,
            fg: T.primary
        ),
        // ② 申请
        Slide(
            sfSymbol: "square.and.pencil.circle.fill",
            title: "外出も帰省もアプリから",
            sub: "外泊・帰省・タクシー…\n申請はすべてここで。",
            gradStart: 0xFDF4E1, gradEnd: 0xFFE9B5,
            fg: T.warnDeep
        ),
        // ③ 看记录
        Slide(
            sfSymbol: "person.text.rectangle.fill",
            title: "自分の記録をいつでも",
            sub: "点呼履歴も減点も、\nマイページで確認。",
            gradStart: 0xE3F1EA, gradEnd: 0x8BC6A3,
            fg: T.okDeep
        ),
        // ④ AI 功能（翻译全机种 / 总结、头像需 Apple Intelligence 机种）
        Slide(
            sfSymbol: "sparkles",
            title: "AI でもっと便利に",
            features: [
                Feature(icon: "globe", label: "お知らせをワンタップ翻訳"),
                Feature(icon: "list.bullet.rectangle", label: "お知らせをワンタップ要約"),
                Feature(icon: "person.crop.circle.badge.plus", label: "アバターを AI で生成"),
            ],
            footnote: "※ AI 要約とアバター生成は iPhone 15 Pro 以降（Apple Intelligence 対応機種）が必要です",
            gradStart: 0xF0EBFB, gradEnd: 0xC9B8F0,
            fg: Color(hex: 0x7A5CC4)
        ),
    ]

    /// 看完 / 跳过 → 标记已看，跳登录页（新用户在登录页点「新規登録」进注册）
    private func finish() {
        hasSeenOnboarding = true
        router.replace(.login)
    }

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Spacer()
                Button("スキップ") { finish() }
                    .font(.system(size: 14, weight: .medium))
                    .foregroundStyle(T.inkSub)
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 8)

            TabView(selection: $idx) {
                ForEach(slides.indices, id: \.self) { i in
                    slideView(slides[i]).tag(i)
                }
            }
            .tabViewStyle(.page(indexDisplayMode: .never))
            .frame(maxWidth: .infinity, maxHeight: .infinity)

            VStack(spacing: 20) {
                HStack(spacing: 8) {
                    ForEach(slides.indices, id: \.self) { i in
                        RoundedRectangle(cornerRadius: 4, style: .continuous)
                            .fill(i == idx ? T.primary : T.inkFaint)
                            .frame(width: i == idx ? 24 : 8, height: 8)
                            .animation(.easeInOut(duration: 0.2), value: idx)
                    }
                }

                PrimaryButton(title: idx < slides.count - 1 ? "次へ" : "始める") {
                    if idx < slides.count - 1 {
                        withAnimation { idx += 1 }
                    } else {
                        finish()
                    }
                }
            }
            .padding(.horizontal, 24)
            .padding(.top, 20)
            .padding(.bottom, 32)
        }
        .background(T.paper.ignoresSafeArea())
    }

    private func slideView(_ s: Slide) -> some View {
        VStack(spacing: 0) {
            RoundedRectangle(cornerRadius: 36, style: .continuous)
                .fill(
                    LinearGradient(
                        colors: [Color(hex: s.gradStart), Color(hex: s.gradEnd)],
                        startPoint: .topLeading, endPoint: .bottomTrailing
                    )
                )
                .frame(width: 200, height: 200)
                .overlay {
                    Image(systemName: s.sfSymbol)
                        .font(.system(size: 100, weight: .regular))
                        .foregroundStyle(s.fg)
                }
                .shadow(color: Color(hex: 0x0F1E22, alpha: 0.10), radius: 30, x: 0, y: 24)
                .padding(.bottom, 36)

            Text(s.title)
                .font(.system(size: 26, weight: .bold))
                .foregroundStyle(T.ink)
                .multilineTextAlignment(.center)
                .padding(.bottom, 12)
                .padding(.horizontal, 24)

            // 普通页：副标题
            if let sub = s.sub {
                Text(sub)
                    .font(.system(size: 15))
                    .foregroundStyle(T.inkSub)
                    .multilineTextAlignment(.center)
                    .lineSpacing(4)
                    .padding(.horizontal, 24)
            }

            // AI 页：功能列表 + 机种小字
            if let features = s.features {
                VStack(alignment: .leading, spacing: 12) {
                    ForEach(features.indices, id: \.self) { i in
                        let f = features[i]
                        HStack(spacing: 10) {
                            Image(systemName: f.icon)
                                .font(.system(size: 14, weight: .semibold))
                                .foregroundStyle(s.fg)
                                .frame(width: 28, height: 28)
                                .background { Circle().fill(s.fg.opacity(0.12)) }
                            Text(f.label)
                                .font(.system(size: 14.5, weight: .medium))
                                .foregroundStyle(T.ink)
                        }
                    }
                }
                .padding(.horizontal, 40)

                if let footnote = s.footnote {
                    Text(footnote)
                        .font(.system(size: 11))
                        .foregroundStyle(T.inkMute)
                        .multilineTextAlignment(.center)
                        .lineSpacing(2)
                        .padding(.top, 18)
                        .padding(.horizontal, 28)
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

#Preview("Onboarding") {
    OnboardingView()
        .environmentObject(RouterStore())
        .environmentObject(AppStore())
}

// ───────────────────────────── Inline Icon paths ──────────────────────────────
// 对等 phaseB_src Ic.phoneTap / mail / calendar / check / lock 的 SVG d 属性

private struct PhoneTapIcon: View {
    var size: CGFloat = 40
    var body: some View {
        Canvas { ctx, _ in
            let scale = size / 48.0
            // <rect x="16" y="10" width="16" height="28" rx="3"/>
            let phoneRect = Path(roundedRect: CGRect(x: 16 * scale, y: 10 * scale, width: 16 * scale, height: 28 * scale), cornerRadius: 3 * scale)
            ctx.stroke(phoneRect, with: .foreground, style: StrokeStyle(lineWidth: 1.8 * scale, lineCap: .round, lineJoin: .round))
            // <path d="M22 33h4"/>
            var home = Path()
            home.move(to: CGPoint(x: 22 * scale, y: 33 * scale))
            home.addLine(to: CGPoint(x: 26 * scale, y: 33 * scale))
            ctx.stroke(home, with: .foreground, style: StrokeStyle(lineWidth: 1.8 * scale, lineCap: .round, lineJoin: .round))
            // wave arc 1: M35 18c1.8 1.5 3 3.6 3 6s-1.2 4.5-3 6
            var wave1 = Path()
            wave1.move(to: CGPoint(x: 35 * scale, y: 18 * scale))
            wave1.addCurve(
                to: CGPoint(x: 35 * scale, y: 30 * scale),
                control1: CGPoint(x: 36.8 * scale, y: 19.5 * scale),
                control2: CGPoint(x: 38 * scale, y: 21.6 * scale)
            )
            ctx.stroke(wave1, with: .foreground, style: StrokeStyle(lineWidth: 1.8 * scale, lineCap: .round, lineJoin: .round))
            // wave arc 2: M39 14c3 2.5 5 6 5 10s-2 7.5-5 10  (opacity .8)
            var wave2 = Path()
            wave2.move(to: CGPoint(x: 39 * scale, y: 14 * scale))
            wave2.addCurve(
                to: CGPoint(x: 39 * scale, y: 34 * scale),
                control1: CGPoint(x: 42 * scale, y: 16.5 * scale),
                control2: CGPoint(x: 44 * scale, y: 20 * scale)
            )
            ctx.opacity = 0.8
            ctx.stroke(wave2, with: .foreground, style: StrokeStyle(lineWidth: 1.8 * scale, lineCap: .round, lineJoin: .round))
        }
        .frame(width: size, height: size)
    }
}

private struct MailIcon: View {
    var size: CGFloat = 40
    var body: some View {
        Canvas { ctx, _ in
            let scale = size / 24.0
            // <rect x="3" y="5" width="18" height="14" rx="2.4"/>
            let env = Path(roundedRect: CGRect(x: 3 * scale, y: 5 * scale, width: 18 * scale, height: 14 * scale), cornerRadius: 2.4 * scale)
            ctx.stroke(env, with: .foreground, style: StrokeStyle(lineWidth: 1.6 * scale, lineCap: .round, lineJoin: .round))
            // <path d="m3.6 6.4 8.4 7 8.4-7"/>
            var flap = Path()
            flap.move(to: CGPoint(x: 3.6 * scale, y: 6.4 * scale))
            flap.addLine(to: CGPoint(x: 12 * scale, y: 13.4 * scale))
            flap.addLine(to: CGPoint(x: 20.4 * scale, y: 6.4 * scale))
            ctx.stroke(flap, with: .foreground, style: StrokeStyle(lineWidth: 1.6 * scale, lineCap: .round, lineJoin: .round))
        }
        .frame(width: size, height: size)
    }
}

private struct CalendarIcon: View {
    var size: CGFloat = 40
    var body: some View {
        Canvas { ctx, _ in
            let scale = size / 24.0
            // <rect x="3.5" y="5" width="17" height="15" rx="2.4"/>
            let frame = Path(roundedRect: CGRect(x: 3.5 * scale, y: 5 * scale, width: 17 * scale, height: 15 * scale), cornerRadius: 2.4 * scale)
            ctx.stroke(frame, with: .foreground, style: StrokeStyle(lineWidth: 1.6 * scale, lineCap: .round, lineJoin: .round))
            // M3.5 10h17
            var top = Path()
            top.move(to: CGPoint(x: 3.5 * scale, y: 10 * scale))
            top.addLine(to: CGPoint(x: 20.5 * scale, y: 10 * scale))
            ctx.stroke(top, with: .foreground, style: StrokeStyle(lineWidth: 1.6 * scale, lineCap: .round, lineJoin: .round))
            // M8 3v4
            var peg1 = Path()
            peg1.move(to: CGPoint(x: 8 * scale, y: 3 * scale))
            peg1.addLine(to: CGPoint(x: 8 * scale, y: 7 * scale))
            ctx.stroke(peg1, with: .foreground, style: StrokeStyle(lineWidth: 1.6 * scale, lineCap: .round, lineJoin: .round))
            // M16 3v4
            var peg2 = Path()
            peg2.move(to: CGPoint(x: 16 * scale, y: 3 * scale))
            peg2.addLine(to: CGPoint(x: 16 * scale, y: 7 * scale))
            ctx.stroke(peg2, with: .foreground, style: StrokeStyle(lineWidth: 1.6 * scale, lineCap: .round, lineJoin: .round))
        }
        .frame(width: size, height: size)
    }
}

private struct CheckIcon: View {
    var size: CGFloat = 28
    var body: some View {
        Canvas { ctx, _ in
            let scale = size / 24.0
            // <path d="m5 12.5 5 5L19 7"/>
            var check = Path()
            check.move(to: CGPoint(x: 5 * scale, y: 12.5 * scale))
            check.addLine(to: CGPoint(x: 10 * scale, y: 17.5 * scale))
            check.addLine(to: CGPoint(x: 19 * scale, y: 7 * scale))
            ctx.stroke(check, with: .foreground, style: StrokeStyle(lineWidth: 2.4 * scale, lineCap: .round, lineJoin: .round))
        }
        .frame(width: size, height: size)
    }
}

private struct LockIcon: View {
    var size: CGFloat = 36
    var body: some View {
        Canvas { ctx, _ in
            let scale = size / 24.0
            // <rect x="5" y="10.5" width="14" height="10" rx="2.4"/>
            let body = Path(roundedRect: CGRect(x: 5 * scale, y: 10.5 * scale, width: 14 * scale, height: 10 * scale), cornerRadius: 2.4 * scale)
            ctx.stroke(body, with: .foreground, style: StrokeStyle(lineWidth: 1.6 * scale, lineCap: .round, lineJoin: .round))
            // <path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/>
            var shackle = Path()
            shackle.move(to: CGPoint(x: 8 * scale, y: 10.5 * scale))
            shackle.addLine(to: CGPoint(x: 8 * scale, y: 8 * scale))
            shackle.addArc(
                center: CGPoint(x: 12 * scale, y: 8 * scale),
                radius: 4 * scale,
                startAngle: .degrees(180),
                endAngle: .degrees(0),
                clockwise: false
            )
            shackle.addLine(to: CGPoint(x: 16 * scale, y: 10.5 * scale))
            ctx.stroke(shackle, with: .foreground, style: StrokeStyle(lineWidth: 1.6 * scale, lineCap: .round, lineJoin: .round))
        }
        .frame(width: size, height: size)
    }
}

private struct BackChevronIcon: View {
    var size: CGFloat = 22
    var body: some View {
        Canvas { ctx, _ in
            let scale = size / 24.0
            // M15 5 8 12l7 7
            var chev = Path()
            chev.move(to: CGPoint(x: 15 * scale, y: 5 * scale))
            chev.addLine(to: CGPoint(x: 8 * scale, y: 12 * scale))
            chev.addLine(to: CGPoint(x: 15 * scale, y: 19 * scale))
            ctx.stroke(chev, with: .foreground, style: StrokeStyle(lineWidth: 2 * scale, lineCap: .round, lineJoin: .round))
        }
        .frame(width: size, height: size)
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// MARK: - Register 共通: Progress bar + Header

// ═══════════════════════════════════════════════════════════════════════════════
//
// 注册进度 · 5 步（Step5 = 认证代码，5-04 加 RegisterStep5 时把硬编码 4 改成 5）

private struct RegisterProgress: View {
    let step: Int // 1...5

    var body: some View {
        VStack(spacing: 8) {
            HStack(alignment: .firstTextBaseline) {
                Text("アカウント作成")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundStyle(T.inkSub)
                Spacer()
                Text("\(step) / 5")
                    .font(.system(size: 12, design: .monospaced))
                    .foregroundStyle(T.inkMute)
            }

            GeometryReader { g in
                ZStack(alignment: .leading) {
                    Capsule()
                        .fill(T.hair)
                        .frame(height: 4)
                    Capsule()
                        .fill(
                            LinearGradient(
                                colors: [T.accent, T.primary],
                                startPoint: .leading, endPoint: .trailing
                            )
                        )
                        .frame(width: g.size.width * CGFloat(step) / 5.0, height: 4)
                        .animation(.easeInOut(duration: 0.4), value: step)
                }
            }
            .frame(height: 4)
        }
        .padding(.horizontal, 24)
        .padding(.top, 12)
        .padding(.bottom, 20)
    }
}

/// level=2 header (Back arrow + title centered) — 对等 phaseB_src PageHeader level=2
/// 不复用 Foundation PageHeader 因为那里 title 是 leading，JSX 要求居中 + 自绘 back icon
private struct RegisterHeader: View {
    let title: String
    @EnvironmentObject var router: RouterStore

    var body: some View {
        HStack(spacing: 8) {
            Button { router.back() } label: {
                BackChevronIcon(size: 22)
                    .foregroundStyle(T.ink)
                    .frame(width: 36, height: 36)
            }
            .buttonStyle(.plain)

            Spacer(minLength: 0)

            Text(title)
                .font(.system(size: 17, weight: .bold))
                .foregroundStyle(T.ink)
                .kerning(0.2)

            Spacer(minLength: 0)

            // spacer to balance back button (36pt) for centered title
            Color.clear.frame(width: 36, height: 36)
        }
        .frame(height: 48)
        .padding(.horizontal, 12)
    }
}

// 对等 phaseB_src PrimaryBtn full + GhostBtn full (JSX 的 disabled tint = T.inkFaint)
// Foundation PrimaryButton / GhostButton 已覆盖，仅 GhostButton full 需 wrapper

private struct GhostButtonFull: View {
    let title: String
    var action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: 15, weight: .semibold))
                .foregroundStyle(T.ink)
                .frame(maxWidth: .infinity)
                .frame(height: 52)
                .background {
                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                        .stroke(T.hair, lineWidth: 1)
                }
                .contentShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
        .buttonStyle(.plain)
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// MARK: - §0.3 RegisterStep1 基本情報

// ═══════════════════════════════════════════════════════════════════════════════
//
// JSX:
//   氏名 TField (default "リュウ イヒ")
//   生年月日 button 48pt with date string (hint: ホイール式の日付ピッカーが表示されます)
//   性別 Radio 男/女 (hint: 性別により自動的に男寮 / 女寮に配属されます)
//   アバター: Avatar 64 letter + 2 buttons "写真を選択" / "デフォルトを使う"
//   footer: PrimaryBtn full disabled=!ok  → go('/register/2')

struct RegisterStep1View: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore
    @State private var name: String = {
        #if DEMO
            return SEED.user.name
        #else
            return ""
        #endif
    }()

    @State private var birth: Date = {
        #if DEMO
            var c = DateComponents(); c.year = 2006; c.month = 10; c.day = 14
            return Calendar.current.date(from: c) ?? Date()
        #else
            // 非 DEMO 默认值 = 在校生年龄中位数（初一到高三平均 15 岁）→ 2011-01-01
            // 任意年级学生只需双向滚 2-4 年就到自己生日（vs Date() 要滚 12-18 年）
            // itsuki 2026-05-27 主动提报「人性化设计」拍板 — 群体中位数默认
            var c = DateComponents(); c.year = 2011; c.month = 1; c.day = 1
            return Calendar.current.date(from: c) ?? Date()
        #endif
    }()

    @State private var gender: String = {
        #if DEMO
            return SEED.user.gender == "男" ? "male" : "female"
        #else
            return "" // 必选 — 不预设性别，防女学生被错误归男寮
        #endif
    }()

    @State private var avatar: String = "default"

    // ── Apple Image Playground · AI 头像生成（iOS 18.2+ 且 Apple Intelligence 机种）──────
    // 18.2 专属 API（@Environment(\.supportsImagePlayground) + .imagePlaygroundSheet）全部隔离在
    // 文件末的 AIAvatarGenerateButton 子视图里（标 @available(iOS 18.2)）。父视图只在 if #available 分支挂它，
    // 所以部署目标 16.0 也能编译，低于 18.2 / 不支持 Apple Intelligence 的机种不显示该按钮。
    @State private var generatedAvatarURL: URL? = nil
    @State private var isOverseas: Bool = {
        #if DEMO
            return SEED.user.isOverseas // 留学生 flag (system_features §8.1 / Q11)
        #else
            return false
        #endif
    }()

    // 学年 / 组 / 出席番号 — demo 也默认空（这 3 个影响账号番号预览，留空方便演示随输入实时变化）
    @State private var grade: String = ""
    @State private var classSuffix: String = ""
    @State private var seatNoStr: String = ""
    // 房间号：demo 预填 A5（itsuki 2026-05-28 指定），生产版留空
    #if DEMO
        @State private var room: String = "A5"
    #else
        @State private var room: String = ""
    #endif

    private let grades = ["中1", "中2", "中3", "高1", "高2", "高3"]

    private var gradeCode: String {
        switch grade {
        case "中1": return "01"
        case "中2": return "02"
        case "中3": return "03"
        case "高1": return "04"
        case "高2": return "05"
        case "高3": return "06"
        default: return "00"
        }
    }

    private var classCode: String {
        // A組 → 01 / B組 → 02 / 未选 → 00（防 canNext 兜底失效时也不写假数据）
        switch classSuffix {
        case "A": return "01"
        case "B": return "02"
        default: return "00"
        }
    }

    /// 6 桁: 年級(2) + 組(2) + 出席番号(2) · 高3 B 18 → "060218"
    private var computedAccount: String {
        let n = max(0, min(99, Int(seatNoStr) ?? 0))
        return gradeCode + classCode + String(format: "%02d", n)
    }

    private var canNext: Bool {
        // 必填检查 — 8 字段全部必选/必填才放行下一步
        // 防止用户跳过性别 / 学年 / 组别 / 出席番号 / 部屋番号导致提交假数据到 backend
        !name.trimmingCharacters(in: .whitespaces).isEmpty
            && (gender == "male" || gender == "female")
            && !grade.isEmpty
            && !classSuffix.isEmpty
            && (Int(seatNoStr) ?? 0) > 0
            && (Int(seatNoStr) ?? 0) <= 99 // backend seat_no 是 2 位数字码，>99 会被 ^\d{2}$ 校验打回
            && !room.trimmingCharacters(in: .whitespaces).isEmpty
    }

    private var avatarLetter: String {
        name.first.map { String($0) } ?? "リ"
    }

    private static let birthFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        return f
    }()

    var body: some View {
        VStack(spacing: 0) {
            RegisterHeader(title: "基本情報")
            RegisterProgress(step: 1)

            ScrollView {
                VStack(spacing: 18) {
                    // 1. アバター（最初に選ぶ）
                    Field(label: "アバター") {
                        HStack(alignment: .center, spacing: 14) {
                            // 有 AI 生成 URL 就显示图片，否则 fallback 到字母 Avatar
                            if let url = generatedAvatarURL {
                                AsyncImage(url: url) { phase in
                                    switch phase {
                                    case let .success(img):
                                        img.resizable().scaledToFill()
                                    default:
                                        // 加载中 / 失败时显示灰色占位
                                        T.pearl
                                    }
                                }
                                .frame(width: 64, height: 64)
                                .clipShape(Circle())
                                .overlay { Circle().stroke(T.hair, lineWidth: 1) }
                            } else {
                                Avatar(letter: avatarLetter, size: 64)
                            }

                            VStack(spacing: 8) {
                                Button {
                                    // demo — 不接真相册
                                } label: {
                                    Text("写真を選択")
                                        .font(.system(size: 13))
                                        .foregroundStyle(T.ink)
                                        .frame(maxWidth: .infinity)
                                        .frame(height: 38)
                                        .background {
                                            RoundedRectangle(cornerRadius: 10, style: .continuous)
                                                .fill(T.pearl)
                                        }
                                        .overlay {
                                            RoundedRectangle(cornerRadius: 10, style: .continuous)
                                                .stroke(T.hair, lineWidth: 1)
                                        }
                                }
                                .buttonStyle(.plain)

                                Button {
                                    avatar = "default"
                                    generatedAvatarURL = nil // 清掉 AI 生成结果，退回字母 Avatar
                                } label: {
                                    Text("デフォルトを使う")
                                        .font(.system(size: 13, weight: .semibold))
                                        .foregroundStyle(T.primary)
                                        .frame(maxWidth: .infinity)
                                        .frame(height: 38)
                                        .background {
                                            RoundedRectangle(cornerRadius: 10, style: .continuous)
                                                .fill(T.primary.opacity(0.08))
                                        }
                                }
                                .buttonStyle(.plain)

                                // ⭐ AI 生成头像（Apple Image Playground · 设备本地推理，零成本零网络）
                                // iOS 18.2+ 且 Apple Intelligence 机种才显示；其余机种这颗按钮不出现 → UX 一致
                                // 18.2 专属 API 全部隔离在 AIAvatarGenerateButton 子视图里（见文件末）
                                if #available(iOS 18.2, *) {
                                    AIAvatarGenerateButton(
                                        name: name,
                                        generatedAvatarURL: $generatedAvatarURL,
                                        avatar: $avatar
                                    )
                                }
                            }
                        }
                    }

                    // 2. 氏名
                    Field(
                        label: "氏名",
                        hint: "日本人は漢字、留学生はカタカナで入力してください",
                        required: true
                    ) {
                        TField(text: $name, placeholder: "")
                    }

                    // 3. 性別
                    Field(
                        label: "性別",
                        hint: "性別により自動的に男寮 / 女寮に配属されます",
                        required: true
                    ) {
                        HStack(spacing: 8) {
                            inlineRadio(value: "male", label: "男")
                            inlineRadio(value: "female", label: "女")
                        }
                    }

                    // 3.5 留学生标志 (system_features §8.1 / Q11 — 出寮届审批链 3 vs 5 役职 因此必须)
                    Field(
                        label: "学生区分",
                        required: true
                    ) {
                        HStack(spacing: 8) {
                            overseasChip(value: false, label: "一般生")
                            overseasChip(value: true, label: "留学生")
                        }
                    }

                    // 4. 生年月日（inline wheel picker · 日本語 locale）
                    Field(label: "生年月日", required: true) {
                        DatePicker("", selection: $birth, in: ...Date(), displayedComponents: .date)
                            .datePickerStyle(.wheel)
                            .labelsHidden()
                            .environment(\.locale, Locale(identifier: "ja_JP"))
                            .frame(maxWidth: .infinity)
                            .frame(height: 160)
                            .clipped()
                            .background {
                                RoundedRectangle(cornerRadius: 12, style: .continuous)
                                    .fill(T.pearl)
                            }
                            .overlay {
                                RoundedRectangle(cornerRadius: 12, style: .continuous)
                                    .stroke(T.hair, lineWidth: 1)
                            }
                    }

                    // 5. 学年
                    Field(label: "学年", required: true) {
                        HStack(spacing: 6) {
                            ForEach(grades, id: \.self) { g in
                                Button {
                                    grade = g
                                } label: {
                                    Text(g)
                                        .font(.system(size: 13, weight: grade == g ? .bold : .medium))
                                        .foregroundStyle(grade == g ? Color.white : T.ink)
                                        .frame(maxWidth: .infinity)
                                        .frame(height: 36)
                                        .background {
                                            RoundedRectangle(cornerRadius: 10, style: .continuous)
                                                .fill(grade == g ? T.primary : T.pearl)
                                        }
                                        .overlay {
                                            RoundedRectangle(cornerRadius: 10, style: .continuous)
                                                .stroke(grade == g ? T.primary : T.hair, lineWidth: 1)
                                        }
                                        .contentShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    }

                    // 6. 組
                    Field(label: "組", required: true) {
                        HStack(spacing: 8) {
                            classChip("A")
                            classChip("B")
                        }
                    }

                    // 7. 出席番号
                    Field(label: "出席番号", required: true) {
                        TField(text: $seatNoStr, placeholder: "", keyboard: .numberPad)
                    }

                    // 8. 部屋番号
                    Field(label: "部屋番号", required: true) {
                        TField(text: $room, placeholder: "")
                    }
                    .onChangeCompat(of: room) { newVal in
                        // 英数字のみ、最大 4 桁
                        let filtered = newVal.filter { $0.isLetter || $0.isNumber }
                            .uppercased()
                        room = String(filtered.prefix(4))
                    }

                    // アカウント番号 プレビュー
                    HStack {
                        Text("アカウント番号")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundStyle(T.inkSub)
                        Spacer()
                        Text(computedAccount)
                            .font(.system(size: 22, weight: .bold, design: .monospaced))
                            .foregroundStyle(T.primary)
                            .kerning(2)
                    }
                    .padding(.horizontal, 14).padding(.vertical, 10)
                    .background {
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .fill(T.primary.opacity(0.06))
                    }
                    .overlay {
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .stroke(T.primary.opacity(0.15), lineWidth: 1)
                    }
                }
                .padding(.horizontal, 24)
                .padding(.top, 8)
                .padding(.bottom, 24)
            }

            footerSingle
        }
        .background(T.paper.ignoresSafeArea())
    }

    /// Inline radio (row) — JSX Radio row layout 风格化
    @ViewBuilder
    private func inlineRadio(value: String, label: String) -> some View {
        let sel = gender == value
        Button { gender = value } label: {
            Text(label)
                .font(.system(size: 14, weight: sel ? .bold : .medium))
                .foregroundStyle(sel ? T.primary : T.ink)
                .frame(maxWidth: .infinity)
                .frame(height: 42)
                .background {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(sel ? T.primary.opacity(0.06) : T.pearl)
                }
                .overlay {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .stroke(sel ? T.primary : T.hair, lineWidth: sel ? 1.5 : 1)
                }
                .contentShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
        }
        .buttonStyle(.plain)
    }

    @ViewBuilder
    private func overseasChip(value: Bool, label: String) -> some View {
        let sel = isOverseas == value
        Button { isOverseas = value } label: {
            Text(label)
                .font(.system(size: 14, weight: sel ? .bold : .medium))
                .foregroundStyle(sel ? T.primary : T.ink)
                .frame(maxWidth: .infinity)
                .frame(height: 42)
                .background {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(sel ? T.primary.opacity(0.06) : T.pearl)
                }
                .overlay {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .stroke(sel ? T.primary : T.hair, lineWidth: sel ? 1.5 : 1)
                }
                .contentShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
        }
        .buttonStyle(.plain)
    }

    @ViewBuilder
    private func classChip(_ v: String) -> some View {
        let sel = classSuffix == v
        Button { classSuffix = v } label: {
            Text("\(v)組")
                .font(.system(size: 14, weight: sel ? .bold : .medium))
                .foregroundStyle(sel ? T.primary : T.ink)
                .frame(maxWidth: .infinity)
                .frame(height: 42)
                .background {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(sel ? T.primary.opacity(0.06) : T.pearl)
                }
                .overlay {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .stroke(sel ? T.primary : T.hair, lineWidth: sel ? 1.5 : 1)
                }
                .contentShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
        }
        .buttonStyle(.plain)
    }

    private var footerSingle: some View {
        VStack(spacing: 0) {
            Rectangle()
                .fill(T.hair)
                .frame(height: 0.5)
            PrimaryButton(title: "次へ", enabled: canNext) {
                #if DEMO
                    // 仅演示构建：即时把表单写进全局假人 SEED.user 供后续页面预览。
                    // 生产构建不写 —— 注册数据只走下面的 registrationDraft → createAccount → loadMe，
                    // 否则真名配演示残留的 4.5 点 / 假邮箱电话会变「混血」资料（codex + Claude 双审逮到）。
                    SEED.user.name = name
                    SEED.user.gender = gender == "male" ? "男" : "女"
                    SEED.user.dorm = gender == "male" ? "男寮" : "女寮"
                    SEED.user.isOverseas = isOverseas
                    SEED.user.grade = grade
                    SEED.user.classSuffix = classSuffix
                    SEED.user.seatNo = Int(seatNoStr) ?? 18
                    let prefix = (gender == "male") ? "M" : "W"
                    // room 已含字母前缀（如 "A5" / "M101"）就直接用，避免 "MA5" 双前缀
                    SEED.user.room = (room.first?.isLetter == true) ? room : prefix + room
                    SEED.user.account = computedAccount
                    SEED.user.avatar = name.first.map { String($0) } ?? "リ"
                #endif

                // 2026-05-04 加: 累积到 RegistrationDraft（Step5 提交时整体送 backend）
                app.registrationDraft.name = name
                app.registrationDraft.birthday = birth
                app.registrationDraft.gender = gender
                app.registrationDraft.is_overseas = isOverseas
                // backend schemas.py §588-590 三字段都是 ^\d{2}$（2 位数字码），不能送中文 "高3" / 字母 "B" / 1 位出席号
                app.registrationDraft.grade_code = gradeCode
                app.registrationDraft.class_code = classCode
                app.registrationDraft.seat_no = String(format: "%02d", Int(seatNoStr) ?? 0)
                // IX-014 修正：room_no_suffix 存裸房号（不加前缀）。前缀只在 AppStore.computedRoomNo
                // 一处加 —— 这里再加会让发后端的 computedRoomNo 二次加前缀变 "MM101"（codex 逮到的回归）。
                app.registrationDraft.room_no_suffix = room

                router.go(.registerStep2)
            }
            .padding(.horizontal, 24)
            .padding(.top, 16)
            .padding(.bottom, 32)
        }
        .background(T.paper)
        // ⭐ Apple Image Playground sheet 已隔离进 AIAvatarGenerateButton 子视图（见下），
        // 不再挂在这里 —— 那样能把 iOS 18.2 专属 modifier 关进 @available 子视图，部署目标 16.0 也能编译。
    }
}

#Preview("RegisterStep1") {
    RegisterStep1View()
        .environmentObject(RouterStore())
        .environmentObject(AppStore())
}

// ═══════════════════════════════════════════════════════════════════════════════
// MARK: - AI 头像生成按钮（Apple Image Playground · iOS 18.2+ 且 Apple Intelligence 机种）

// ═══════════════════════════════════════════════════════════════════════════════
//
// 整个子视图标 @available(iOS 18.2)，把两处 18.2 专属 API 关在里面：
//   - @Environment(\.supportsImagePlayground) — 设备是否支持 Image Playground + Apple Intelligence 已在系统设置开启
//   - .imagePlaygroundSheet(...)             — 弹设备本地 AI 生成头像浮层
// 父视图（RegisterStep1View）只在 if #available(iOS 18.2, *) 分支里挂它，所以低部署目标编译无碍、旧机种不显示。

@available(iOS 18.2, *)
private struct AIAvatarGenerateButton: View {
    let name: String
    @Binding var generatedAvatarURL: URL?
    @Binding var avatar: String

    @Environment(\.supportsImagePlayground) private var supportsImagePlayground
    @State private var showSheet: Bool = false
    /// 模型 cold start 5 秒掩饰 — 点击后立刻显示 loading，5.5 秒兜底复位
    @State private var isLoading: Bool = false

    var body: some View {
        // 设备不支持（机种旧 / Apple Intelligence 没开）→ 整颗按钮不出现，UX 跟不支持机种一致
        if supportsImagePlayground {
            Button {
                isLoading = true
                showSheet = true
                DispatchQueue.main.asyncAfter(deadline: .now() + 5.5) {
                    isLoading = false
                }
            } label: {
                HStack(spacing: 6) {
                    if isLoading {
                        ProgressView()
                            .controlSize(.small)
                            .tint(.white)
                        Text("準備中…")
                            .font(.system(size: 13, weight: .semibold))
                    } else {
                        Image(systemName: "sparkles")
                            .font(.system(size: 12, weight: .semibold))
                        Text("AI で生成")
                            .font(.system(size: 13, weight: .semibold))
                    }
                }
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity)
                .frame(height: 38)
                .background {
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                        .fill(isLoading ? T.accent.opacity(0.7) : T.accent)
                }
            }
            .buttonStyle(.plain)
            .disabled(isLoading)
            .imagePlaygroundSheet(
                isPresented: $showSheet,
                concept: "学生 アバター \(name) 笑顔 cute",
                onCompletion: { url in
                    // onCompletion 拿到的 url 是 iOS 系统给的临时文件路径（v1.x 上传后端时改存远程 URL）
                    generatedAvatarURL = url
                    avatar = url.absoluteString
                    isLoading = false
                }
            )
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// MARK: - §0.4 RegisterStep2 点呼区分

// ═══════════════════════════════════════════════════════════════════════════════
//
// JSX:
//   heading "あなたの点呼区分" fontSize:15, weight:700, marginBottom:14
//   2 custom radio cards:
//     regular : "一般寮生" + detail "平日: 朝 7:00 / 晩 21:00  ·  土日: 朝 8:00 / 晩 21:30"
//     soccer  : "サッカー部" + detail "早朝練があるため  ·  平日: 朝 6:00 / 晩 21:00"
//   card: padding 18, radius 16, border selected: 1.5 T.primary + bg: T.primary08 + shadow
//   radio visual: 22×22 circle, when selected: border 6 T.primary + bg #fff
//   footer: 2 buttons (戻る / 次へ) gap:10
//   (注意: JSX 写作 "晚" — 按 REMOTE_AGENT_GUIDE §1.1 v2 HTML 已修为 "晩"，Swift 写 "晩")

struct RegisterStep2View: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore
    @State private var cat: String = "regular"

    /// UI 选项 → backend category 字符串
    /// backend Student.category 没 CHECK 约束，但保持人类可读的日语名（管理员后台看的）
    private func categoryLabel(_ v: String) -> String {
        switch v {
        case "soccer": return "サッカー部"
        default: return "一般寮生"
        }
    }

    private struct CatOption {
        let v: String
        let l: String
        let d: String
    }

    private let options: [CatOption] = [
        CatOption(
            v: "regular",
            l: "一般寮生",
            d: "平日: 朝 7:40 / 晩 22:00  ·  土日: 朝 8:50 / 晩 20:00"
        ),
        CatOption(
            v: "soccer",
            l: "サッカー部",
            d: "平日: 朝 7:10 / 晩 22:00  ·  土日: 朝 7:10 / 晩 20:00"
        ),
    ]

    var body: some View {
        VStack(spacing: 0) {
            RegisterHeader(title: "点呼区分")
            RegisterProgress(step: 2)

            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    Text("あなたの点呼区分")
                        .font(.system(size: 15, weight: .bold))
                        .foregroundStyle(T.ink)
                        .padding(.bottom, 2)

                    ForEach(options, id: \.v) { o in
                        catCard(o)
                    }
                }
                .padding(.horizontal, 24)
                .padding(.top, 8)
                .padding(.bottom, 24)
            }

            footerDouble(
                onBack: { router.go(.registerStep1) },
                onNext: {
                    // 2026-05-04 加: 累积 category 到 draft
                    app.registrationDraft.category = categoryLabel(cat)
                    router.go(.registerStep3)
                }
            )
        }
        .background(T.paper.ignoresSafeArea())
    }

    @ViewBuilder
    private func catCard(_ o: CatOption) -> some View {
        let sel = cat == o.v
        Button { cat = o.v } label: {
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    Text(o.l)
                        .font(.system(size: 16, weight: .bold))
                        .foregroundStyle(T.ink)
                    Spacer()
                    // 22×22 custom radio marker
                    ZStack {
                        Circle()
                            .stroke(sel ? T.primary : T.inkFaint, lineWidth: sel ? 6 : 1.5)
                            .frame(width: 22, height: 22)
                        if sel {
                            Circle()
                                .fill(Color.white)
                                .frame(width: 22 - 12, height: 22 - 12)
                        }
                    }
                }
                Text(o.d)
                    .font(.system(size: 12.5))
                    .foregroundStyle(T.inkSub)
                    .lineSpacing(2)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .padding(18)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background {
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .fill(sel ? T.primary.opacity(0.03) : T.paper)
            }
            .overlay {
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(sel ? T.primary : T.hair, lineWidth: sel ? 1.5 : 1)
            }
            .shadow(color: sel ? Color(hex: 0x1F6B74, alpha: 0.08) : .clear, radius: 14, x: 0, y: 4)
        }
        .buttonStyle(.plain)
    }
}

#Preview("RegisterStep2") {
    RegisterStep2View()
        .environmentObject(RouterStore())
        .environmentObject(AppStore())
}

/// 共通 2 按钮 footer (戻る + 次へ) — private 避免污染其他 feature
@MainActor
private func footerDouble(
    nextTitle: String = "次へ",
    nextEnabled: Bool = true,
    onBack: @escaping @MainActor () -> Void,
    onNext: @escaping @MainActor () -> Void
) -> some View {
    VStack(spacing: 0) {
        Rectangle()
            .fill(T.hair)
            .frame(height: 0.5)
        HStack(spacing: 10) {
            GhostButtonFull(title: "戻る", action: onBack)
            PrimaryButton(title: nextTitle, enabled: nextEnabled, action: onNext)
        }
        .padding(.horizontal, 24)
        .padding(.top, 16)
        .padding(.bottom, 32)
    }
    .background(T.paper)
}

// ═══════════════════════════════════════════════════════════════════════════════
// MARK: - §0.5 RegisterStep3 連絡先

// ═══════════════════════════════════════════════════════════════════════════════
//
// JSX:
//   メールアドレス (required, hint: 認証メールは送信されません。将来のパスワードリセット時の確認用です)
//     default: demo@example.com
//   電話番号 (required, hint: 寮監があなたに連絡する場合に使います)
//     default: 090-0000-0000

struct RegisterStep3View: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore
    @State private var email: String = {
        #if DEMO
            return "demo@example.com"
        #else
            return ""
        #endif
    }()

    @State private var phone: String = {
        #if DEMO
            return "090-0000-0000"
        #else
            return ""
        #endif
    }()

    var body: some View {
        VStack(spacing: 0) {
            RegisterHeader(title: "連絡先")
            RegisterProgress(step: 3)

            ScrollView {
                VStack(spacing: 18) {
                    Field(
                        label: "メールアドレス",
                        hint: "学校のメールアドレスでも、ご自身のメールアドレスでも登録できます。認証メールは送信されません（将来のパスワードリセット時の確認用です）",
                        required: true
                    ) {
                        TField(text: $email, placeholder: "example@email.com", keyboard: .emailAddress)
                    }

                    Field(
                        label: "電話番号",
                        hint: "寮監があなたに連絡する場合に使います",
                        required: true
                    ) {
                        TField(text: $phone, placeholder: "090-1234-5678", keyboard: .phonePad)
                    }
                }
                .padding(.horizontal, 24)
                .padding(.top, 8)
                .padding(.bottom, 24)
            }

            footerDouble(
                // 邮箱 / 电话 两个字段都标 required（必填），空值不应能进下一步
                nextEnabled: !email.isEmpty && !phone.isEmpty,
                onBack: { router.go(.registerStep2) },
                onNext: {
                    // 2026-05-04 加: 累积 email / phone 到 draft（任意字段，空则传 nil）
                    app.registrationDraft.email = email.isEmpty ? nil : email
                    app.registrationDraft.phone = phone.isEmpty ? nil : phone
                    router.go(.registerStep4)
                }
            )
        }
        .background(T.paper.ignoresSafeArea())
    }
}

#Preview("RegisterStep3") {
    RegisterStep3View()
        .environmentObject(RouterStore())
        .environmentObject(AppStore())
}

// ═══════════════════════════════════════════════════════════════════════════════
// MARK: - §0.6 RegisterStep4 パスワード設定

// ═══════════════════════════════════════════════════════════════════════════════
//
// JSX:
//   amber banner: 24×24 orange circle with "!" + "ご注意ください" heading + body
//     padding: 14×16, radius 14, bg T.warnBg, border T.warn40
//   パスワード (required, hint "8 文字以上", secure)
//   パスワード（確認） (required, error "パスワードが一致しません" when mismatch, secure)
//   footer: 戻る + アカウント作成完了  (disabled when !pw || !pw2 || mismatch)

struct RegisterStep4View: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore
    /// 上架版（DEMO 标志关）= 空字符串，让用户必填；DEMO build 保留预填方便演示
    @State private var pw: String = {
        #if DEMO
            return "demo1234"
        #else
            return ""
        #endif
    }()

    @State private var pw2: String = {
        #if DEMO
            return "demo1234"
        #else
            return ""
        #endif
    }()

    private var mismatch: Bool {
        !pw.isEmpty && !pw2.isEmpty && pw != pw2
    }

    private var canSubmit: Bool {
        !pw.isEmpty && !pw2.isEmpty && !mismatch
    }

    var body: some View {
        VStack(spacing: 0) {
            RegisterHeader(title: "パスワード設定")
            RegisterProgress(step: 4)

            ScrollView {
                VStack(spacing: 20) {
                    // amber 注意 banner
                    HStack(alignment: .top, spacing: 12) {
                        ZStack {
                            Circle()
                                .fill(T.warn)
                                .frame(width: 24, height: 24)
                            Text("!")
                                .font(.system(size: 14, weight: .bold))
                                .foregroundStyle(.white)
                        }
                        .frame(width: 24, height: 24)

                        VStack(alignment: .leading, spacing: 3) {
                            Text("ご注意ください")
                                .font(.system(size: 12.5, weight: .bold))
                                .foregroundStyle(T.warnDeep)
                            Text("パスワードは自分では変更できません。変更には寮監への連絡が必要です。入力時は慎重にお願いします。")
                                .font(.system(size: 12.5))
                                .foregroundStyle(T.warnDeep)
                                .lineSpacing(3)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    .padding(.vertical, 14)
                    .padding(.horizontal, 16)
                    .frame(maxWidth: .infinity, alignment: .topLeading)
                    .background {
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .fill(T.warnBg)
                    }
                    .overlay {
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .stroke(T.warn.opacity(0.25), lineWidth: 1)
                    }

                    Field(
                        label: "パスワード",
                        hint: "8 文字以上",
                        required: true
                    ) {
                        TField(text: $pw, placeholder: "", secure: true)
                    }

                    Field(
                        label: "パスワード（確認）",
                        error: mismatch ? "パスワードが一致しません" : nil,
                        required: true
                    ) {
                        TField(text: $pw2, placeholder: "", secure: true)
                    }
                }
                .padding(.horizontal, 24)
                .padding(.top, 8)
                .padding(.bottom, 24)
            }

            footerDouble(
                nextTitle: "次へ",
                nextEnabled: canSubmit,
                onBack: { router.go(.registerStep3) },
                // 2026-05-04 改: Step4 之后跳到 Step5 (注册码输入)，不再直接 replace done
                onNext: {
                    // 累积 password 到 draft，Step5 提交时整体送 backend
                    app.registrationDraft.password = pw
                    router.go(.registerStep5)
                }
            )
        }
        .background(T.paper.ignoresSafeArea())
    }
}

#Preview("RegisterStep4") {
    RegisterStep4View()
        .environmentObject(RouterStore())
        .environmentObject(AppStore())
}

// ═══════════════════════════════════════════════════════════════════════════════
// MARK: - §0.7 RegisterDoneView

// ═══════════════════════════════════════════════════════════════════════════════
//
// JSX:
//   100×100 green circle w/ linear-gradient #8bc6a3 → #4a9478
//     Ic.check(28) scale(2.4) → 实际 ~67pt
//     shadow: 0 12px 40px rgba(74,148,120,0.3)
//     animation: zoom .4s cubic-bezier(0.2,0.8,0.2,1)
//   "ようこそ、リュウ イヒ さん"  fontSize:22, weight:700
//   "アカウントが作成されました"  fontSize:13, T.inkSub
//   Account panel: padding 20×24, radius 20, bg linear-gradient #e8f4f6 → #a8dce2
//     "あなたのアカウント番号" fontSize:11, weight:700, letterSpacing 0.18em, uppercase, T.primaryDk
//     "00"  fontSize:64, weight:800, mono, T.primaryDk, letterSpacing -0.02em
//     次回からはこの...  fontSize:12, T.primaryDk opacity:.8
//   footer: "始める" PrimaryBtn full → go('/home')

struct RegisterDoneView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore
    @State private var checkAppear: Bool = false

    var body: some View {
        VStack(spacing: 0) {
            Spacer()

            // 100×100 green circle + check mark (zoom animation)
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color(hex: 0x8BC6A3), Color(hex: 0x4A9478)],
                            startPoint: .topLeading, endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 100, height: 100)
                    .shadow(color: Color(hex: 0x4A9478, alpha: 0.30), radius: 24, x: 0, y: 12)

                // Ic.check(28) scale(2.4) ≈ 67pt canvas stroke
                CheckIcon(size: 28)
                    .scaleEffect(2.4)
                    .foregroundStyle(.white)
            }
            .scaleEffect(checkAppear ? 1 : 0.2)
            .opacity(checkAppear ? 1 : 0)
            .padding(.bottom, 28)

            // Welcome + subtitle
            Text("ようこそ、\(SEED.user.name) さん")
                .font(.system(size: 22, weight: .bold))
                .foregroundStyle(T.ink)
                .padding(.bottom, 10)

            Text("アカウントが作成されました")
                .font(.system(size: 13))
                .foregroundStyle(T.inkSub)
                .padding(.bottom, 32)

            // Account number panel
            VStack(alignment: .leading, spacing: 8) {
                Text("あなたのアカウント番号")
                    .font(.system(size: 11, weight: .bold))
                    .kerning(2)
                    .foregroundStyle(T.primaryDk)
                    .textCase(.uppercase)

                Text(SEED.user.account)
                    .font(.system(size: 44, weight: .heavy, design: .monospaced))
                    .foregroundStyle(T.primaryDk)
                    .kerning(-0.9)
                    .padding(.top, -2)
                    .minimumScaleFactor(0.6)
                    .lineLimit(1)

                Text("次回からはこの 6 桁番号\nまたはメールアドレスと\nパスワードでログインしてください")
                    .font(.system(size: 12))
                    .foregroundStyle(T.primaryDk.opacity(0.8))
                    .lineSpacing(3)
                    .padding(.top, 2)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(.vertical, 20)
            .padding(.horizontal, 24)
            .background {
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .fill(
                        LinearGradient(
                            colors: [Color(hex: 0xE8F4F6), Color(hex: 0xA8DCE2)],
                            startPoint: .topLeading, endPoint: .bottomTrailing
                        )
                    )
            }
            .padding(.horizontal, 32)

            Spacer()

            PrimaryButton(title: "始める") {
                router.replace(.home)
            }
            .padding(.horizontal, 24)
            .padding(.top, 16)
            .padding(.bottom, 32)
        }
        .background(T.paper.ignoresSafeArea())
        .onAppear {
            // JSX: zoom .4s cubic-bezier(0.2,0.8,0.2,1)  — spring 对等
            withAnimation(.spring(response: 0.4, dampingFraction: 0.7)) {
                checkAppear = true
            }
            // 2026-05-04 加: 注册成功后清空 draft（避免下次注册脏数据）
            app.resetRegistrationDraft()
        }
    }
}

#Preview("RegisterDone") {
    RegisterDoneView()
        .environmentObject(RouterStore())
        .environmentObject(AppStore())
}

// ═══════════════════════════════════════════════════════════════════════════════
// MARK: - §0.8 LoginView

// ═══════════════════════════════════════════════════════════════════════════════
//
// JSX:
//   bg: linear-gradient(180deg, #eff2f3 → #e4ebec)
//   header centered: "Tomoshibi"  fontSize:28, weight:700, T.primaryDk, letterSpacing 0.04em
//                    "灯火 · ログイン"  fontSize:12, T.inkMute, letterSpacing 0.08em
//   mode tab 2 segments: 番号で / メールで  (active: T.paper bg + T.primary fg + shadow)
//     container: T.pill (primary08) bg, radius 12, padding 3
//   番号: アカウント番号 Input numeric (fontSize:20, mono, letterSpacing 0.1em), default "060217"
//   メール: メールアドレス Input type=email, default "demo@example.com"
//   パスワード: secure, default "12345678"
//   ログイン btn
//   row: 新規登録 (T.inkSub) ←→ パスワードを忘れた → (T.primary)
//   footer mono: Tomoshibi v0.1.0-demo · 2026 AC 入試プロジェクト
//   magic seed（仅 DEMO 编译 + 番号 mode）: acc=="060217" && pw=="12345678" → router.replace(.home)
//   （「メール」mode 暂不支持登录，只提示切学号；真账号走 AuthAPI / 401 → lockout）

struct LoginView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    enum Mode: Hashable { case number, email }

    @State private var mode: Mode = .number
    /// demo 版预填方便演示，production 全空
    @State private var acc: String = {
        #if DEMO
            return "060217"
        #else
            return ""
        #endif
    }()

    @State private var email: String = {
        #if DEMO
            return "demo@example.com"
        #else
            return ""
        #endif
    }()

    @State private var pw: String = {
        #if DEMO
            return "12345678"
        #else
            return ""
        #endif
    }()

    /// 登录中（按钮 disable + loading）
    @State private var isLoading: Bool = false

    var body: some View {
        ZStack {
            // JSX: linear-gradient(180deg, #eff2f3 0%, #e4ebec 100%)
            LinearGradient(
                colors: [T.pearl, Color(hex: 0xE4EBEC)],
                startPoint: .top, endPoint: .bottom
            )
            .ignoresSafeArea()

            VStack(spacing: 0) {
                // JSX padding: '40px 28px 16px' · Ag top 40pt
                Spacer().frame(height: 40)

                // Title · JSX textAlign center · marginBottom 36
                VStack(spacing: 4) {
                    Text("Tomoshibi")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundStyle(T.primaryDk)
                        .kerning(1.12) // 0.04em on 28pt
                    Text("灯火 · ログイン")
                        .font(.system(size: 12))
                        .foregroundStyle(T.inkMute)
                        .kerning(1)
                }
                .padding(.bottom, 36)

                // Mode tab (2 segments)
                modeTab
                    .padding(.horizontal, 28)
                    .padding(.bottom, 22)

                // Fields
                VStack(spacing: 18) {
                    if mode == .number {
                        Field(label: "アカウント番号") {
                            TField(
                                text: $acc,
                                placeholder: "",
                                keyboard: .numberPad
                            )
                            .font(.system(size: 20, design: .monospaced))
                            .kerning(2)
                        }
                    } else {
                        Field(label: "メールアドレス") {
                            TField(
                                text: $email,
                                placeholder: "",
                                keyboard: .emailAddress
                            )
                        }
                    }

                    Field(label: "パスワード") {
                        TField(text: $pw, placeholder: "", secure: true)
                    }
                }
                .padding(.horizontal, 28)

                // Login button
                PrimaryButton(title: isLoading ? "ログイン中…" : "ログイン") {
                    Task { await tryLogin() }
                }
                .disabled(isLoading)
                .padding(.horizontal, 28)
                .padding(.top, 8)

                // Footer links
                // Footer links（v1.0 上架版：忘记密码功能未实装 → 入口隐藏，避免 Apple 4.0 死按钮 reject）
                HStack {
                    Button("新規登録") {
                        router.go(.registerStep1)
                    }
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundStyle(T.inkSub)

                    Spacer()
                }
                .padding(.horizontal, 28)
                .padding(.top, 18)

                Spacer()
            }
        }
    }

    // JSX: 2-tab segmented control, bg T.pill, padding 3
    private var modeTab: some View {
        HStack(spacing: 0) {
            tabBtn(title: "番号", active: mode == .number) { mode = .number }
            tabBtn(title: "メール", active: mode == .email) { mode = .email }
        }
        .padding(3)
        .background {
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(T.pill)
        }
    }

    private func tabBtn(title: String, active: Bool, _ action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: 13.5, weight: .bold))
                .foregroundStyle(active ? T.primary : T.inkSub)
                .frame(maxWidth: .infinity)
                .frame(height: 40)
                .background {
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                        .fill(active ? T.paper : .clear)
                }
                .shadow(color: active ? Color(hex: 0x0F1E22, alpha: 0.08) : .clear, radius: 6, x: 0, y: 2)
                .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }

    /// 登录尝试（async — 调 AuthAPI.loginStudent）
    ///
    /// 流程：
    ///  - メール mode → backend 还没实装邮箱登录,提示用户切到学号
    ///  - DEMO 编译模式 + magic creds（acc=="060217" / pw=="12345678"）→ 跳过 API 直接进 home
    ///  - 其他全走 AuthAPI.loginStudent → 401 走 lockout / 其他 error 走 toast
    private func tryLogin() async {
        isLoading = true
        defer { isLoading = false }

        // メール mode 暂未支持（backend F6 注册流程未实装、邮箱登录后做）
        if mode == .email {
            app.showToast("学号でログインしてください")
            return
        }

        // 账号去首尾空白：学号是 6 桁数字、空格永远非法，复制粘贴常带空格 / 换行
        //   → 用 .whitespacesAndNewlines 统一 trim（含换行符；原 .whitespaces 只去空格/制表符、漏换行）后再用
        // 密码不 trim：用户故意打的空格也算密码内容，原样发后端（后端只校验长度 6–128，schemas.py）
        let trimmedAcc = acc.trimmingCharacters(in: .whitespacesAndNewlines)

        // 空字段检查：账号 / 密码任一空着就当场拦下，别拿空值去请求后端
        // （原来空着也直发请求，失败落到「通信エラー」提示，跟「没填」对不上、误导用户 — itsuki 2026-06-04）
        if trimmedAcc.isEmpty || pw.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            app.showToast("アカウント番号とパスワードを入力してください")
            return
        }

        // DEMO 编译模式: magic creds 跳过 API（用于演示锁定升级 / 离线场景）
        #if DEMO
            let isDemoMagic = (trimmedAcc == "060217") && (pw == "12345678")
            if isDemoMagic {
                app.resetLoginFailures()
                router.replace(.home)
                return
            }
        #endif

        // 真实 API 调用
        do {
            let token = try await AuthAPI.loginStudent(studentNo: trimmedAcc, password: pw)
            // IX-036: 走 setAuthToken 一并存过期时刻（原来直接赋 authToken 会跳过过期记录，
            // 登录得到的令牌启动时就判不了过期）。didSet 仍同步 APIClient.token + Keychain.save。
            app.setAuthToken(token.accessToken, expiresIn: token.expiresIn)
            await app.loadMe() // IX-008: 登录后拉当前用户，主页直接显真实数据（不闪一下演示假数据）
            app.resetLoginFailures()
            router.replace(.home)
        } catch APIError.unauthorized {
            // 学号 / 密码错（后端尚未锁）
            app.recordLoginFailure() // 本地连续失败计数（纯 UX，锁定真值以后端 423 为准）
            #if DEMO
                // 演示版保留本地锁定升级演出（30/60/300… 秒倒计时）
                router.go(.lockout)
            #else
                // 生产版不走本地写死倒计时的假 LockoutView，只提示凭证错误
                app.showToast("学籍番号またはパスワードが違います")
            #endif
        } catch let APIError.server(423, msg) {
            // 后端真锁（B6 学生连续失败锁）→ 显示后端日语文案（含「残り約 X 分」），以后端为锁定真值
            app.showToast(msg.isEmpty ? "アカウントロック中です。しばらくしてからお試しください" : msg)
        } catch let APIError.server(403, msg) {
            // 账号停用（status != active）
            app.showToast(msg.isEmpty ? "アカウントが無効です。寮監にご連絡ください" : msg)
        } catch let APIError.unprocessable(msg) {
            // 学号格式错（非 6 桁数字）等
            app.showToast(msg)
        } catch APIError.network {
            app.showToast("通信エラーが発生しました。電波を確認してください")
        } catch {
            app.showToast(error.localizedDescription)
        }
    }
}

#Preview("Login") {
    LoginView()
        .environmentObject(RouterStore())
        .environmentObject(AppStore())
}

// ═══════════════════════════════════════════════════════════════════════════════
// MARK: - §0.9 LockoutView

// ═══════════════════════════════════════════════════════════════════════════════
//
// JSX:
//   100×100 danger circle bg T.dangerBg, Ic.lock(36) scale(1.6) fg T.danger
//   "ログイン試行が多すぎます"  fontSize:20, weight:700, T.ink
//   "MM:SS" fontSize:48, weight:700, mono, T.danger, letterSpacing 0.04em, margin 16/0
//   "寮監に通知しました\nセキュリティのためロック中です"  fontSize:13, T.inkSub, lineHeight 1.6
//   upgrade hint (amber pill): fontSize:11.5, T.warnDeep, padding 10×14, radius 10
//   30s countdown → router.replace(.login)

struct LockoutView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore
    @State private var sec: Int = 0
    @State private var timer: Timer? = nil

    /// 是否永久锁（失败 6 次以上）
    private var isPermanent: Bool {
        app.currentLockoutSeconds == nil
    }

    private var mm: String {
        String(format: "%02d", sec / 60)
    }

    private var ss: String {
        String(format: "%02d", sec % 60)
    }

    var body: some View {
        VStack(spacing: 0) {
            Spacer()

            // 100×100 红圈 + 锁 icon
            ZStack {
                Circle()
                    .fill(T.dangerBg)
                    .frame(width: 100, height: 100)
                LockIcon(size: 36)
                    .foregroundStyle(T.danger)
                    .scaleEffect(1.6)
            }
            .padding(.bottom, 24)

            Text(isPermanent ? "アカウントがロックされました" : "ログインに失敗しました")
                .font(.system(size: 20, weight: .bold))
                .foregroundStyle(T.ink)
                .padding(.bottom, 8)

            if isPermanent {
                // 永久锁 — 不显示倒计时
                Text("永久")
                    .font(.system(size: 36, weight: .heavy))
                    .foregroundStyle(T.danger)
                    .padding(.vertical, 18)

                Text("試行回数の上限を超えました。\n寮監にご連絡ください。")
                    .font(.system(size: 13))
                    .foregroundStyle(T.inkSub)
                    .multilineTextAlignment(.center)
                    .lineSpacing(5)
            } else {
                // 倒计时
                Text("\(mm):\(ss)")
                    .font(.system(size: 48, weight: .bold, design: .monospaced))
                    .foregroundStyle(T.danger)
                    .kerning(1.9)
                    .padding(.vertical, 16)

                Text("セキュリティのため、しばらくログインできません。")
                    .font(.system(size: 13))
                    .foregroundStyle(T.inkSub)
                    .multilineTextAlignment(.center)
                    .lineSpacing(5)

                // 当前阶段 + 下一阶段提示
                VStack(spacing: 2) {
                    Text("現在 \(app.loginFailCount) 回目のロック（\(app.currentLockoutLabel)）")
                    if let next = app.nextLockoutLabel {
                        Text("次回失敗で \(next) ロックに上がります")
                    }
                }
                .font(.system(size: 11.5))
                .foregroundStyle(T.warnDeep)
                .multilineTextAlignment(.center)
                .lineSpacing(3)
                .padding(.horizontal, 14)
                .padding(.vertical, 10)
                .background {
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                        .fill(T.warnBg)
                }
                .padding(.top, 28)
            }

            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.paper.ignoresSafeArea())
        .onAppear { startTimer() }
        .onDisappear { stopTimer() }
    }

    /// 启动倒计时 — 永久锁不计时
    private func startTimer() {
        if isPermanent { return }
        // demo 阶段时长按 spec 真值（30/60/300/1800/3600 秒），但前 30 秒看完就够演示
        sec = app.currentLockoutSeconds ?? 30
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
            Task { @MainActor in
                guard sec > 0 else { return }
                sec -= 1
                if sec == 0 {
                    stopTimer()
                    router.replace(.login)
                }
            }
        }
    }

    private func stopTimer() {
        timer?.invalidate()
        timer = nil
    }
}

#Preview("Lockout") {
    LockoutView()
        .environmentObject(RouterStore())
        .environmentObject(AppStore())
}

// ═══════════════════════════════════════════════════════════════════════════════
// MARK: - §0.10 PwResetView

// ═══════════════════════════════════════════════════════════════════════════════
//
// JSX:
//   header PageHeader level=2 title "パスワードをリセット"
//   body: fontSize:15, T.ink, lineHeight:1.75
//     "パスワードのリセットは App 内では行えません。寮監に直接お声がけください。
//      寮監がシステム後台で手動でリセットします。"
//   info box: padding 14×16, radius 14, bg T.primary0a, border T.primary22
//     "ℹ リセット後、新しいパスワードが寮監から伝えられます"
//   footer: "戻る" PrimaryBtn full  → go('/login')

struct PwResetView: View {
    @EnvironmentObject var router: RouterStore

    var body: some View {
        VStack(spacing: 0) {
            RegisterHeader(title: "パスワードをリセット")

            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    Text("パスワードのリセットは App 内では行えません。寮監に直接お声がけください。寮監がシステム後台で手動でリセットします。")
                        .font(.system(size: 15))
                        .foregroundStyle(T.ink)
                        .lineSpacing(8) // 1.75 on 15 ≈ 11; per line extra ≈ 8
                        .fixedSize(horizontal: false, vertical: true)

                    // Info box
                    HStack(alignment: .top, spacing: 6) {
                        Text("ℹ")
                            .font(.system(size: 14, weight: .bold))
                            .foregroundStyle(T.primary)
                        Text("リセット後、新しいパスワードが寮監から伝えられます")
                            .font(.system(size: 12.5))
                            .foregroundStyle(T.primaryDk)
                            .lineSpacing(3)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .padding(.vertical, 14)
                    .padding(.horizontal, 16)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background {
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .fill(T.primary.opacity(0.04)) // 0a hex → ~0.04
                    }
                    .overlay {
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .stroke(T.primary.opacity(0.13), lineWidth: 1) // 22 hex → ~0.13
                    }
                }
                .padding(.horizontal, 28)
                .padding(.top, 24)
                .padding(.bottom, 24)
            }

            VStack(spacing: 0) {
                PrimaryButton(title: "戻る") {
                    router.replace(.login)
                }
                .padding(.horizontal, 24)
                .padding(.top, 16)
                .padding(.bottom, 32)
            }
            .background(T.paper)
        }
        .background(T.paper.ignoresSafeArea())
    }
}

#Preview("PwReset") {
    PwResetView()
        .environmentObject(RouterStore())
        .environmentObject(AppStore())
}

// ═══════════════════════════════════════════════════════════════════════════════
// MARK: - §0.6.5 RegisterStep5 認証コード（2026-05-04 加，App Store 上架对策）

// ═══════════════════════════════════════════════════════════════════════════════
//
// spec: system_features.md §7.16 + IOS_DESIGN_LOG.md §3.10（spec 已落 5-03）
//
// UX:
//   amber banner: 提醒「教师在后台生成的 6 桁数字、5 分钟有效」
//   1 个大字 input: 6 桁数字、键盘 .numberPad、字号 28、kerning 8、居中
//   底部 footerDouble: 戻る + アカウント作成完了 (disabled if !canSubmit || isLoading)
//   isLoading 时按钮转「送信中…」+ disabled
//   错误显示: 红色 banner，文案来自 backend (e.g. "コードが正しくないか…")

struct RegisterStep5View: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    // A-035 (2026-05-24 → 2026-05-28 解决)：demo magic value "000000" 后门
    // 之前的问题：后门写在所有 build 里 = 生产安全漏洞，所以 5-24 删了。
    // 5-28 重新引入但只在 DEMO build（演示版独立编译开关），生产版不含此分支 → 不再是漏洞。
    // 演示版：认证码预填 "000000" + submit 跳过 backend 直接进完成页（itsuki 5-28 要求「直接进入界面」）
    #if DEMO
        @State private var code: String = "000000"
    #else
        @State private var code: String = ""
    #endif
    @State private var isLoading: Bool = false
    @State private var errorMsg: String? = nil

    /// 6 桁数字才能 submit
    private var canSubmit: Bool {
        code.count == 6 && code.allSatisfy { $0.isNumber }
    }

    var body: some View {
        VStack(spacing: 0) {
            RegisterHeader(title: "認証コード")
            RegisterProgress(step: 5)

            ScrollView {
                VStack(spacing: 20) {
                    // amber 注意 banner — 解释为什么需要这个码
                    HStack(alignment: .top, spacing: 12) {
                        ZStack {
                            Circle()
                                .fill(T.warn)
                                .frame(width: 24, height: 24)
                            Text("!")
                                .font(.system(size: 14, weight: .bold))
                                .foregroundStyle(.white)
                        }
                        .frame(width: 24, height: 24)

                        VStack(alignment: .leading, spacing: 3) {
                            Text("ご注意ください")
                                .font(.system(size: 12.5, weight: .bold))
                                .foregroundStyle(T.warnDeep)
                            Text("教員から発行された 6 桁の認証コードを入力してください。コードは発行から 5 分以内のみ有効です。")
                                .font(.system(size: 12.5))
                                .foregroundStyle(T.warnDeep)
                                .lineSpacing(3)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    .padding(.vertical, 14)
                    .padding(.horizontal, 16)
                    .frame(maxWidth: .infinity, alignment: .topLeading)
                    .background {
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .fill(T.warnBg)
                    }
                    .overlay {
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .stroke(T.warn.opacity(0.25), lineWidth: 1)
                    }

                    // 6 桁数字 input — 居中大字
                    VStack(spacing: 8) {
                        Text("認証コード（6 桁）")
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundStyle(T.inkSub)
                            .frame(maxWidth: .infinity, alignment: .leading)

                        TextField("000000", text: $code)
                            .keyboardType(.numberPad)
                            .multilineTextAlignment(.center)
                            .font(.system(size: 28, weight: .heavy, design: .monospaced))
                            .kerning(8)
                            .padding(.vertical, 16)
                            .background {
                                RoundedRectangle(cornerRadius: 14)
                                    .fill(T.paper)
                            }
                            .overlay {
                                RoundedRectangle(cornerRadius: 14)
                                    .stroke(T.hair, lineWidth: 1)
                            }
                            .onChangeCompat(of: code) { new in
                                // 限制只能输入数字 + 最多 6 桁
                                let filtered = String(new.filter { $0.isNumber }.prefix(6))
                                if filtered != new { code = filtered }
                                // 输入有改动 → 清掉旧错误提示
                                if errorMsg != nil { errorMsg = nil }
                            }
                    }
                    .padding(.top, 4)

                    // 错误显示（backend 422 文案来这里）
                    if let msg = errorMsg {
                        Text(msg)
                            .font(.system(size: 13))
                            .foregroundStyle(.red)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.vertical, 10)
                            .padding(.horizontal, 14)
                            .background {
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(Color.red.opacity(0.08))
                            }
                    }
                }
                .padding(.horizontal, 24)
                .padding(.top, 8)
                .padding(.bottom, 24)
            }

            footerDouble(
                nextTitle: isLoading ? "送信中…" : "アカウント作成完了",
                nextEnabled: canSubmit && !isLoading,
                onBack: { router.go(.registerStep4) },
                onNext: submit
            )
        }
        .background(T.paper.ignoresSafeArea())
    }

    /// 调 backend POST /accounts、成功 → register done、失败 → 显示错误
    private func submit() {
        guard canSubmit, !isLoading else { return }

        #if DEMO
            // 演示版：跳过 backend，直接进注册完成页（生产版无此分支，不是后门漏洞）
            router.replace(.registerDone)
            return
        #endif

        isLoading = true
        errorMsg = nil
        Task {
            do {
                _ = try await app.createAccount(registrationCode: code)
                router.replace(.registerDone)
            } catch let APIError.unprocessable(msg) {
                // backend 给的文案直接显示给学生（spec §7.16.2 规则 7 已固定）
                errorMsg = msg
            } catch {
                errorMsg = "通信エラーが発生しました。もう一度お試しください。"
            }
            isLoading = false
        }
    }
}

#Preview("RegisterStep5") {
    RegisterStep5View()
        .environmentObject(RouterStore())
        .environmentObject(AppStore())
}
