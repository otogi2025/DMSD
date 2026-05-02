// HomeStubs.swift · Home feature v2 · HTML 1:1 fidelity rewrite
// Agent B v2 · 对等 phaseB_src 364061ea__HomePage_RollcallSheet_FeedbackSheet.js
//
// Views: HomeView / LifeTab / CommunityTab / NotifTab
//      + RollcallSheet / FeedbackSheet / HealthSheet / AbsenceSheet / OtherSheet
//
// 设计原则：
//   - 日本語文案逐字照抄 JSX，不翻译不润色
//   - 数值 (pt/gap/radius) 严格对照 JSX inline style
//   - Sheet 走 AppStore.sheetOpen + GlobalOverlays 三层堆叠
//   - TopRollBar / BottomNav 在 GlobalOverlays 挂，本 View 不重挂
//   - SEED 数据按 Web Round 3 口径 (M101 / 男寮 / 4.5 / 5 / 2)

import SwiftUI

// ───────────────────────────────────────────────────────────
// MARK: - 私有扩展：hex string → Color（Lost 用）
// ───────────────────────────────────────────────────────────

private extension Color {
    /// "#3b82f6" → Color
    init?(hexString: String) {
        var s = hexString.trimmingCharacters(in: .whitespacesAndNewlines)
        if s.hasPrefix("#") { s.removeFirst() }
        guard s.count == 6, let v = UInt32(s, radix: 16) else { return nil }
        self.init(hex: v)
    }
}

// ───────────────────────────────────────────────────────────
// MARK: - DemoCardCycleGesture · amber Card 长按循环 demo 状态
// ───────────────────────────────────────────────────────────
//
// production 版（默认）= no-op（不加任何 gesture）
// demo 版（DEMO flag）= 长按 0.6 秒循环点呼 / 学習状态
// memory project_demo_scaffolds_to_remove_before_v1.md #1, #15

private struct DemoCardCycleGesture: ViewModifier {
    let app: AppStore

    func body(content: Content) -> some View {
        #if DEMO
        content.simultaneousGesture(
            LongPressGesture(minimumDuration: 0.6).onEnded { _ in
                if SEED.user.isStudyTarget && app.studyState != .idle {
                    app.cycleDemoStudyState()
                } else {
                    app.cycleDemoRollState()
                }
                UIImpactFeedbackGenerator(style: .medium).impactOccurred()
            }
        )
        #else
        content
        #endif
    }
}

// ───────────────────────────────────────────────────────────
// MARK: - 私有原子：HomeCard（JSX Card pad=14 · shadow · radius 18）
// ───────────────────────────────────────────────────────────

/// JSX Card 对等：white bg + radius 18 + shadow + 0.5pt hair border
/// Foundation Card 默认 radius 16，但 JSX 原版是 18 — 本 feature 私有版对齐
private struct HomeCard<Content: View>: View {
    var pad: CGFloat = 14
    var onTap: (() -> Void)? = nil
    @ViewBuilder var content: () -> Content

    var body: some View {
        let inner = content()
            .padding(pad)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background {
                RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .fill(T.paper)
            }
            .overlay {
                RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .stroke(T.hair, lineWidth: 0.5)
            }
            .shadow(color: T.ink.opacity(0.04), radius: 2, x: 0, y: 1)
            .shadow(color: T.ink.opacity(0.05), radius: 14, x: 0, y: 4)

        if let onTap {
            Button(action: onTap) { inner }
                .buttonStyle(.plain)
        } else {
            inner
        }
    }
}

// ───────────────────────────────────────────────────────────
// MARK: - 私有原子：NotifPill（JSX Pill tone）
// ───────────────────────────────────────────────────────────

/// JSX Pill 5 tone 直译（Foundation Pill 缺"accent"调色，本地重绘）
private struct NotifPill: View {
    let text: String
    let tone: Tone

    enum Tone { case neutral, warn, ok, danger, accent }

    var body: some View {
        Text(text)
            .font(.system(size: 11.5, weight: .bold))
            .kerning(0.22)
            .padding(.horizontal, 10).padding(.vertical, 3)
            .foregroundStyle(fg)
            .background(Capsule().fill(bg))
    }

    private var fg: Color {
        switch tone {
        case .neutral: return T.pillFg
        case .warn:    return T.warnDeep
        case .ok:      return T.okDeep
        case .danger:  return T.danger
        case .accent:  return T.primary
        }
    }
    private var bg: Color {
        switch tone {
        case .neutral: return T.pill
        case .warn:    return T.warnBg
        case .ok:      return T.okBg
        case .danger:  return T.dangerBg
        case .accent:  return Color(hex: 0xe8f4f6)
        }
    }
}

// ───────────────────────────────────────────────────────────
// MARK: - HomeView · greeting + 扣分 card + 3 segmented tab
// ───────────────────────────────────────────────────────────

struct HomeView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    // segmented + Tab 已砍 — itsuki 4-30: 通知去右上角，功能集中到一个页面（unread 留给右上角铃铛 badge）

    /// 未读数 — 用 AppStore.allNotifications（包含 push mock）
    private var unread: Int { app.unreadNotificationCount }

    // 1 秒ごとに active 中の倒计时を進める Timer
    private let countdownTimer = Timer.publish(every: 1, on: .main, in: .common).autoconnect()

    var body: some View {
        // safeAreaInset 现在自动让出 TopRollBar / BottomNav · 不用 placeholder
        ScrollView(showsIndicators: false) {
            VStack(spacing: 0) {
                // §1 Greeting  ——  JSX: padding 14px 20px 6px
                greetingRow
                    .padding(.leading, 20).padding(.trailing, 20)
                    .padding(.top, 14).padding(.bottom, 6)

                // §2 扣分 amber Card  ——  JSX: padding 12px 16px 6px
                pointsCard
                    .padding(.horizontal, 16)
                    .padding(.top, 12).padding(.bottom, 6)
                    .onReceive(countdownTimer) { _ in
                        app.tickCountdown()
                        app.tickStudyCountdown()  // 4-30 學習 demo
                    }

                // §3 LifeTab 内容直显（segmented + コミュニティ + 通知 tab 砍掉，通知用右上角按钮看）
                LifeTab()
                    .padding(.horizontal, 16)
                    .padding(.top, 14).padding(.bottom, 16)
            }
        }
        .background(T.pearl.ignoresSafeArea())
    }

    // MARK: greeting

    private var greetingRow: some View {
        HStack(alignment: .center, spacing: 12) {
            VStack(alignment: .leading, spacing: 3) {
                // JSX: fontSize 20 / 700 / letterSpacing 0.01em
                Text("おかえり、\(SEED.user.name) さん")
                    .font(.system(size: 20, weight: .bold))
                    .kerning(0.2)
                    .foregroundStyle(T.ink)
                // JSX: fontSize 12 / inkMute / marginTop 3
                Text("2026 年 4 月 22 日（火）")
                    .font(.system(size: 12))
                    .foregroundStyle(T.inkMute)
            }
            Spacer(minLength: 0)

            // JSX: 44×44 / radius 14 / hair border / paper bg / bell 22 / unread badge
            Button { router.go(.homeNotifications) } label: {
                ZStack(alignment: .topTrailing) {
                    RoundedRectangle(cornerRadius: 14, style: .continuous)
                        .fill(T.paper)
                        .frame(width: 44, height: 44)
                        .overlay(
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .stroke(T.hair, lineWidth: 0.5)
                        )
                        .shadow(color: T.ink.opacity(0.04), radius: 2, x: 0, y: 1)
                        .shadow(color: T.ink.opacity(0.05), radius: 14, x: 0, y: 4)
                        .overlay {
                            Ic.bell(22).foregroundStyle(T.ink)
                        }

                    if unread > 0 {
                        // JSX: top 6 right 6 / minW 16 h 16 / padding 0 4 / radius 8 / danger bg / 10/700 mono / 1.5 white border
                        Text("\(unread)")
                            .font(.system(size: 10, weight: .bold, design: .monospaced))
                            .foregroundStyle(.white)
                            .padding(.horizontal, 4)
                            .frame(minWidth: 16, minHeight: 16)
                            .background(Capsule().fill(T.danger))
                            .overlay(Capsule().stroke(.white, lineWidth: 1.5))
                            .offset(x: -4, y: 4)
                    }
                }
            }
            .buttonStyle(.plain)
        }
    }

    // MARK: 扣分 Card（amber · JSX #5c3410 ink）
    //
    // idle 時：今月の減点を大表示（4.5点 + progress bar + 遅刻/欠席 counts）
    // active/late/done 時：点呼ヒーロー表示に切替（大きな 点呼中 · 2:50 / 遅刻 / 時間内 + 欠席申請 / 体調報告 ボタン）
    //                      今月点数は右下に小さく退避

    private var pointsCard: some View {
        // JSX ink：#5c3410（深褐）
        let deepBrown = Color(hex: 0x5c3410)
        return ZStack {
            // JSX: radius 22 / padding 20 22 / amber gradient
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .fill(cardGradient)
                .shadow(color: Color(hex: 0xd4a547).opacity(0.24), radius: 20, x: 0, y: 6)

            // JSX: radial-gradient 装饰圆斑 top-right
            Circle()
                .fill(
                    RadialGradient(
                        colors: [Color.white.opacity(0.4), .clear],
                        center: .center,
                        startRadius: 0, endRadius: 60
                    )
                )
                .frame(width: 120, height: 120)
                .offset(x: 140, y: -70)
                .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))

            Group {
                // ⚠️ DEMO-ONLY 三态切换 (system_features §7.3.8 — v1.0 删)
                // 学習対象学生 + studyState in upcoming/active → study mode 优先
                if SEED.user.isStudyTarget && (app.studyState == .upcoming || app.studyState == .active) {
                    studyContent(deepBrown: deepBrown)
                } else if app.rollState == .idle {
                    idleContent(deepBrown: deepBrown)
                } else {
                    rollActiveContent(deepBrown: deepBrown)
                }
            }
            .padding(.horizontal, 22).padding(.vertical, 20)
        }
        .contentShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
        .modifier(DemoCardCycleGesture(app: app))
        .animation(.spring(response: 0.34, dampingFraction: 0.82), value: app.rollState)
        .animation(.spring(response: 0.34, dampingFraction: 0.82), value: app.studyState)
    }

    /// absent 時は赤グラデーション、それ以外は amber
    private var cardGradient: LinearGradient {
        if app.rollState == .absent {
            return LinearGradient(
                stops: [
                    .init(color: Color(hex: 0xffd6d0), location: 0.0),
                    .init(color: Color(hex: 0xef6a58), location: 0.55),
                    .init(color: Color(hex: 0xc83b29), location: 1.0),
                ],
                startPoint: .topLeading, endPoint: .bottomTrailing
            )
        }
        return LinearGradient(
            stops: [
                .init(color: Color(hex: 0xffefc2), location: 0.0),
                .init(color: Color(hex: 0xf4c677), location: 0.55),
                .init(color: Color(hex: 0xd99f3e), location: 1.0),
            ],
            startPoint: .topLeading, endPoint: .bottomTrailing
        )
    }

    // MARK: study content (4-30 後續 拍板 — ⚠️ DEMO-ONLY · v1.0 删)
    //
    // 学習対象学生 + studyState upcoming/active 时 amber Card 显示这套:
    // - 学習迟到倒计时（mm:ss）
    // - 「請假」按钮 → 学習欠席届提交

    @ViewBuilder
    private func studyContent(deepBrown: Color) -> some View {
        let mm = app.studyCountdownSec / 60
        let ss = app.studyCountdownSec % 60
        let countdownText = String(format: "%02d:%02d", mm, ss)
        let isActive = app.studyState == .active

        VStack(alignment: .leading, spacing: 0) {
            // header row — タイトル + ステータス pill
            HStack(alignment: .top) {
                Text(isActive ? "学習中" : "学習開始まで")
                    .font(.system(size: 11, weight: .bold))
                    .kerning(1.98)
                    .textCase(.uppercase)
                    .foregroundStyle(deepBrown.opacity(0.8))
                Spacer()
                Text(isActive ? "進行中" : "10 分前")
                    .font(.system(size: 11.5, weight: .bold))
                    .kerning(0.22)
                    .padding(.horizontal, 10).padding(.vertical, 3)
                    .foregroundStyle(deepBrown)
                    .background(Capsule().fill(Color.white.opacity(0.45)))
            }
            .padding(.bottom, 6)

            if isActive {
                // active = NFC 3 回タップの進捗 + 「NFC で签到」入口（system_features §7.3.3）
                studyTapsProgress(deepBrown: deepBrown)
                    .padding(.bottom, 14)
                studyActionButtons(deepBrown: deepBrown)
            } else {
                // upcoming = 倒计时 hero + 請假ボタン
                Button { router.go(.applyForm(kind: "studyAbsence")) } label: {
                    VStack(alignment: .leading, spacing: 0) {
                        HStack(alignment: .firstTextBaseline, spacing: 6) {
                            Text(countdownText)
                                .font(.system(size: 56, weight: .heavy, design: .monospaced))
                                .kerning(-1.12)
                                .foregroundStyle(deepBrown)
                            Text("分:秒")
                                .font(.system(size: 16, weight: .semibold))
                                .foregroundStyle(deepBrown.opacity(0.75))
                        }
                        .padding(.bottom, 12)
                        Text("前半節 19:40〜20:40 ／ 後半節 20:45〜21:45")
                            .font(.system(size: 12))
                            .foregroundStyle(deepBrown.opacity(0.85))
                            .padding(.bottom, 12)
                        HStack {
                            Text("休む場合は")
                                .font(.system(size: 12))
                                .foregroundStyle(deepBrown.opacity(0.85))
                            Spacer()
                            HStack(spacing: 4) {
                                Ic.chevR(14)
                                Text("請假")
                                    .font(.system(size: 12, weight: .bold))
                            }
                            .foregroundStyle(deepBrown)
                            .padding(.horizontal, 10).padding(.vertical, 5)
                            .background(Capsule().fill(Color.white.opacity(0.5)))
                        }
                    }
                }
                .buttonStyle(.plain)
            }
        }
    }

    /// 学習 NFC 3 回タップの進捗 dot row（active のみ表示）
    @ViewBuilder
    private func studyTapsProgress(deepBrown: Color) -> some View {
        let taps = app.studyTaps
        let items: [(StudyTap, String, String)] = [
            (.start, "開始",  "19:40"),
            (.mid,   "中場",  "20:45"),
            (.end,   "終了",  "21:45"),
        ]
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 0) {
                ForEach(Array(items.enumerated()), id: \.offset) { (i, item) in
                    let (tap, label, time) = item
                    let done = taps.contains(tap)
                    VStack(spacing: 6) {
                        ZStack {
                            Circle()
                                .fill(done ? Color.white : Color.white.opacity(0.3))
                                .frame(width: 36, height: 36)
                                .overlay(
                                    Circle().stroke(deepBrown.opacity(done ? 1 : 0.4), lineWidth: 1.8)
                                )
                            if done {
                                Image(systemName: "checkmark")
                                    .font(.system(size: 14, weight: .heavy))
                                    .foregroundStyle(deepBrown)
                            } else {
                                Text("\(i + 1)")
                                    .font(.system(size: 14, weight: .heavy, design: .monospaced))
                                    .foregroundStyle(deepBrown.opacity(0.6))
                            }
                        }
                        Text(label)
                            .font(.system(size: 11, weight: .bold))
                            .foregroundStyle(deepBrown)
                        Text(time)
                            .font(.system(size: 10, design: .monospaced))
                            .foregroundStyle(deepBrown.opacity(0.7))
                    }
                    .frame(maxWidth: .infinity)
                    if i < items.count - 1 {
                        Rectangle()
                            .fill(deepBrown.opacity(taps.contains(items[i + 1].0) ? 0.7 : 0.25))
                            .frame(height: 2)
                            .padding(.bottom, 28)
                    }
                }
            }
        }
    }

    /// active 時のアクション row — 「NFC で签到」+「請假」 (next tap が無い時は「全 3 回完了」表示)
    @ViewBuilder
    private func studyActionButtons(deepBrown: Color) -> some View {
        if let _ = app.nextStudyTap {
            HStack(spacing: 10) {
                Button {
                    app.openSheet(.studyCheckin)
                } label: {
                    HStack(spacing: 6) {
                        Image(systemName: "iphone.radiowaves.left.and.right")
                            .font(.system(size: 14, weight: .semibold))
                        Text("NFC で签到")
                            .font(.system(size: 13.5, weight: .bold))
                    }
                    .foregroundStyle(deepBrown)
                    .frame(maxWidth: .infinity)
                    .frame(height: 44)
                    .background(
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .fill(Color.white.opacity(0.7))
                    )
                    .shadow(color: deepBrown.opacity(0.18), radius: 6, x: 0, y: 2)
                }
                .buttonStyle(.plain)
                Button { router.go(.applyForm(kind: "studyAbsence")) } label: {
                    HStack(spacing: 6) {
                        Image(systemName: "calendar.badge.exclamationmark")
                            .font(.system(size: 14, weight: .semibold))
                        Text("請假")
                            .font(.system(size: 13.5, weight: .semibold))
                    }
                    .foregroundStyle(deepBrown)
                    .frame(maxWidth: .infinity)
                    .frame(height: 44)
                    .background(
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .fill(Color.white.opacity(0.45))
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .stroke(Color.white.opacity(0.6), lineWidth: 1)
                    )
                }
                .buttonStyle(.plain)
            }
        } else {
            // 全 3 回完了
            HStack(spacing: 8) {
                Image(systemName: "checkmark.seal.fill")
                    .font(.system(size: 16, weight: .semibold))
                Text("本日の学習出席は完了しました")
                    .font(.system(size: 13, weight: .bold))
            }
            .foregroundStyle(deepBrown)
            .frame(maxWidth: .infinity)
            .frame(height: 44)
            .background(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .fill(Color.white.opacity(0.55))
            )
        }
    }

    // MARK: idle content（今月の減点 hero）

    @ViewBuilder
    private func idleContent(deepBrown: Color) -> some View {
        Button { router.go(.myPoints) } label: {
            VStack(alignment: .leading, spacing: 0) {
                HStack(alignment: .top) {
                    Text("今月の減点")
                        .font(.system(size: 11, weight: .bold))
                        .kerning(1.98)
                        .textCase(.uppercase)
                        .foregroundStyle(deepBrown.opacity(0.8))
                    Spacer()
                    Text(pointsPillText)
                        .font(.system(size: 11.5, weight: .bold))
                        .kerning(0.22)
                        .padding(.horizontal, 10).padding(.vertical, 3)
                        .foregroundStyle(pointsPillFg(deepBrown: deepBrown))
                        .background(Capsule().fill(pointsPillBg))
                }
                .padding(.bottom, 6)

                HStack(alignment: .firstTextBaseline, spacing: 6) {
                    Text(String(format: "%.1f", SEED.user.points))
                        .font(.system(size: 56, weight: .heavy, design: .monospaced))
                        .kerning(-1.12)
                        .foregroundStyle(deepBrown)
                    Text("点")
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundStyle(deepBrown.opacity(0.75))
                }
                .padding(.bottom, 12)

                progressRow(deepBrown: deepBrown)

                HStack {
                    HStack(spacing: 0) {
                        Text("遅刻 ")
                        Text("\(SEED.user.lateCount)")
                            .font(.system(size: 12, weight: .bold, design: .monospaced))
                        Text(" 回 · 欠席 ")
                        Text("\(SEED.user.absentCount)")
                            .font(.system(size: 12, weight: .bold, design: .monospaced))
                        Text(" 回")
                    }
                    .font(.system(size: 12))
                    .foregroundStyle(deepBrown.opacity(0.85))
                    Spacer()
                    HStack(spacing: 4) {
                        Text("詳細")
                            .font(.system(size: 12, weight: .bold))
                        Ic.chevR(14)
                    }
                    .foregroundStyle(deepBrown)
                }
                .padding(.top, 12)
            }
        }
        .buttonStyle(.plain)
    }

    // MARK: active / late / done content（点呼 hero）

    @ViewBuilder
    private func rollActiveContent(deepBrown: Color) -> some View {
        // absent 時はカード全体が赤 → テキストは白系に
        let isAbsent = app.rollState == .absent
        let labelColor: Color = isAbsent ? Color.white.opacity(0.9) : deepBrown.opacity(0.8)
        let valueColor: Color = isAbsent ? .white : deepBrown
        let chevColor: Color = isAbsent ? Color.white.opacity(0.9) : deepBrown.opacity(0.85)

        VStack(alignment: .leading, spacing: 0) {
            // Row 1: 小さな 今月の減点 · 4.5 点 / 詳細
            Button { router.go(.myPoints) } label: {
                HStack(spacing: 8) {
                    Text("今月の減点")
                        .font(.system(size: 11, weight: .bold))
                        .kerning(1.98)
                        .textCase(.uppercase)
                        .foregroundStyle(labelColor)
                    Text(String(format: "%.1f 点", SEED.user.points))
                        .font(.system(size: 13, weight: .bold, design: .monospaced))
                        .foregroundStyle(valueColor)
                    Spacer()
                    HStack(spacing: 2) {
                        Text("詳細")
                            .font(.system(size: 11, weight: .bold))
                        Ic.chevR(12)
                    }
                    .foregroundStyle(chevColor)
                }
            }
            .buttonStyle(.plain)
            .padding(.bottom, 10)

            // Row 2: Hero status display
            heroStatus(deepBrown: deepBrown)
                .padding(.bottom, 14)

            // Row 3: アクションボタン（absent 時は単独の「寮監に連絡」、それ以外は 欠席申請 + 体調報告）
            if isAbsent {
                Button {
                    app.showToast("寮監：田中先生（内線 101）へ直接ご連絡ください")
                } label: {
                    HStack(spacing: 8) {
                        Image(systemName: "phone.fill")
                            .font(.system(size: 15, weight: .semibold))
                        Text("寮監に連絡")
                            .font(.system(size: 15, weight: .bold))
                    }
                    .foregroundStyle(T.danger)
                    .frame(maxWidth: .infinity)
                    .frame(height: 46)
                    .background(
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .fill(Color.white)
                    )
                    .shadow(color: Color.black.opacity(0.18), radius: 8, x: 0, y: 3)
                }
                .buttonStyle(.plain)
            } else {
                HStack(spacing: 10) {
                    rollActionButton(icon: "calendar.badge.exclamationmark", label: "欠席申請") {
                        app.openSheet(.absence)
                    }
                    rollActionButton(icon: "heart.text.square", label: "体調報告") {
                        app.openSheet(.health)
                    }
                }
            }
        }
    }

    /// active: 大きな「点呼中 · 2:50」カウントダウン / late: 赤の遅刻 / done: 緑の時間内
    @ViewBuilder
    private func heroStatus(deepBrown: Color) -> some View {
        switch app.rollState {
        case .active:
            if app.rollCountdownSec <= 0 {
                heroBlock(
                    caption: "今回の点呼",
                    big: "遅刻",
                    sub: "欠席申請または体調報告で救済可能",
                    bigColor: T.danger,
                    captionColor: deepBrown.opacity(0.7),
                    subColor: deepBrown.opacity(0.8)
                )
            } else {
                let m = app.rollCountdownSec / 60
                let s = app.rollCountdownSec % 60
                heroBlock(
                    caption: "点呼中 · 残り",
                    big: String(format: "%d:%02d", m, s),
                    sub: "NFC にタッチでチェックイン",
                    bigColor: deepBrown,
                    captionColor: deepBrown.opacity(0.7),
                    subColor: deepBrown.opacity(0.8),
                    bigMonospaced: true
                )
            }
        case .absent:
            heroBlock(
                caption: "欠席判定 · 要対応",
                big: "欠席",
                sub: "寮監室まで直接お越しください",
                bigColor: .white,
                captionColor: Color.white.opacity(0.9),
                subColor: Color.white.opacity(0.95)
            )
        case .done:
            heroBlock(
                caption: "\(app.checkinAt ?? "21:02")",
                big: "時間内",
                sub: "今回の点呼は完了しました",
                bigColor: Color(hex: 0x2c6048),
                captionColor: deepBrown.opacity(0.7),
                subColor: deepBrown.opacity(0.8)
            )
        case .idle:
            EmptyView()
        }
    }

    @ViewBuilder
    private func heroBlock(
        caption: String,
        big: String,
        sub: String,
        bigColor: Color,
        captionColor: Color,
        subColor: Color,
        bigMonospaced: Bool = false
    ) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(caption)
                .font(.system(size: 12, weight: .semibold))
                .foregroundStyle(captionColor)
            Text(big)
                .font(.system(
                    size: 44, weight: .heavy,
                    design: bigMonospaced ? .monospaced : .default
                ))
                .kerning(bigMonospaced ? -0.5 : 0)
                .foregroundStyle(bigColor)
            Text(sub)
                .font(.system(size: 12))
                .foregroundStyle(subColor)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    @ViewBuilder
    private func rollActionButton(icon: String, label: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack(spacing: 6) {
                Image(systemName: icon)
                    .font(.system(size: 14, weight: .semibold))
                Text(label)
                    .font(.system(size: 13.5, weight: .semibold))
            }
            .foregroundStyle(Color(hex: 0x5c3410))
            .frame(maxWidth: .infinity)
            .frame(height: 40)
            .background(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .fill(Color.white.opacity(0.55))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .stroke(Color.white.opacity(0.7), lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }

    /// JSX progress bar: h 8 / radius 4 / bg white.4 / fill 50% amber / 2 threshold marks
    private func progressRow(deepBrown: Color) -> some View {
        VStack(alignment: .leading, spacing: 5) {
            GeometryReader { geo in
                let w = geo.size.width
                // 当前 4.5 点，但 JSX 固定画 50%（4/8）— 严格按 JSX 固定 50%
                // 为避免硬编码失真，用 points/8 上限 1
                let pct = min(SEED.user.points / 8.0, 1.0)

                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 4, style: .continuous)
                        .fill(Color.white.opacity(0.4))
                        .frame(height: 8)

                    RoundedRectangle(cornerRadius: 4, style: .continuous)
                        .fill(
                            LinearGradient(
                                colors: [Color(hex: 0xd99f3e), Color(hex: 0xb07a28)],
                                startPoint: .leading, endPoint: .trailing
                            )
                        )
                        .frame(width: w * pct, height: 8)

                    // JSX: threshold 4 点（50%）
                    Rectangle()
                        .fill(deepBrown.opacity(0.4))
                        .frame(width: 2, height: 12)
                        .offset(x: w * 0.5 - 1, y: 0)
                    // JSX: threshold 8 点（100%）
                    Rectangle()
                        .fill(deepBrown.opacity(0.4))
                        .frame(width: 2, height: 12)
                        .offset(x: w - 2, y: 0)
                }
            }
            .frame(height: 12)

            // JSX: fontSize 10 / mono / opacity .7 · "0" "4 · 清掃" "8 · 外出禁止"
            HStack {
                Text("0")
                Spacer()
                Text("4 · 清掃")
                Spacer()
                Text("8 · 外出禁止")
            }
            .font(.system(size: 10, design: .monospaced))
            .foregroundStyle(deepBrown.opacity(0.7))
        }
    }

    // MARK: 点呼状态 pill 文字/颜色（amber card 右上）
    // 老师点开始点呼前 = 来月より清掃対象（普通 warn 提示）
    // 点呼中 = 残り XX:XX で遅刻判定（warn orange）
    // 遅刻（倒计时归零未签到）= 遅刻（danger red）
    // 已签到 = 時間内にチェックイン（ok green）

    private var pointsPillText: String {
        switch app.rollState {
        case .idle:
            return "来月より清掃対象"
        case .active:
            if app.rollCountdownSec <= 0 {
                return "遅刻"
            }
            let m = app.rollCountdownSec / 60
            let s = app.rollCountdownSec % 60
            return String(format: "点呼中 · %d:%02d", m, s)
        case .absent:
            return "欠席 · 要連絡"
        case .done:
            return "時間内にチェックイン"
        }
    }

    private func pointsPillFg(deepBrown: Color) -> Color {
        switch app.rollState {
        case .idle: return deepBrown
        case .active: return app.rollCountdownSec <= 0 ? .white : Color(hex: 0x7a4a0e)
        case .absent: return .white
        case .done: return Color(hex: 0x2c6048)
        }
    }

    private var pointsPillBg: Color {
        switch app.rollState {
        case .idle: return Color.white.opacity(0.45)
        case .active: return app.rollCountdownSec <= 0 ? T.danger : Color(hex: 0xfdf4e1)
        case .absent: return T.danger
        case .done: return Color(hex: 0xe3f1ea)
        }
    }
}

// ───────────────────────────────────────────────────────────
// MARK: - LifeTab · bus / package / events / lost / suggest
// ───────────────────────────────────────────────────────────

struct LifeTab: View {
    @EnvironmentObject var router: RouterStore

    /// 次回運行バス情報（busSchedule を見て「今日」or「直近未来日」の最初の便を返す）
    private struct UpcomingBus {
        let date: String        // "2026-04-29"
        let weekday: String     // "水"
        let line: BusLine
        let isToday: Bool
    }

    private static let ymdFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        f.locale = Locale(identifier: "ja_JP")
        return f
    }()

    private static let hmFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "HH:mm"
        f.locale = Locale(identifier: "ja_JP")
        return f
    }()

    private var upcomingBus: UpcomingBus? {
        let now = Date()
        let today = Self.ymdFormatter.string(from: now)
        let nowHM = Self.hmFormatter.string(from: now)

        // 今日の便（時刻が今より後のもの）
        if let day = SEED.busSchedule.first(where: { $0.date == today }),
           let line = day.lines.first(where: { $0.time > nowHM }) {
            return UpcomingBus(date: day.date, weekday: day.weekday, line: line, isToday: true)
        }
        // 未来日の最初の便
        if let day = SEED.busSchedule.first(where: { $0.date > today }),
           let line = day.lines.first {
            return UpcomingBus(date: day.date, weekday: day.weekday, line: line, isToday: false)
        }
        return nil
    }

    private var pendingPkg: Int { SEED.packages.filter { $0.status == "待領" }.count }

    var body: some View {
        VStack(spacing: 10) {
            busCard
            packageCard
            eventsCard
            musicCard
            lostCard
            suggestCard
        }
    }

    // MARK: Bus card — JSX: 44×44 primary.12 bg / bus icon / 13 inkSub / 22 mono bold time

    private var busCard: some View {
        HomeCard(pad: 14, onTap: { router.go(.homeBus) }) {
            HStack(spacing: 12) {
                ZStack {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(T.primary.opacity(0.07))      // JSX ${T.primary}12 = ~7% alpha
                        .frame(width: 44, height: 44)
                    Ic.bus(22).foregroundStyle(T.primary)
                }
                VStack(alignment: .leading, spacing: 2) {
                    if let ub = upcomingBus {
                        Text(ub.isToday ? "次のバス便" : "次回運行")
                            .font(.system(size: 13))
                            .foregroundStyle(T.inkSub)
                        HStack(alignment: .firstTextBaseline, spacing: 8) {
                            Text(ub.line.time)
                                .font(.system(size: 22, weight: .bold, design: .monospaced))
                                .foregroundStyle(T.ink)
                            if ub.isToday {
                                Text("· \(ub.line.route)")
                                    .font(.system(size: 12))
                                    .foregroundStyle(T.inkMute)
                                    .lineLimit(1)
                            } else {
                                // "4/29(水) 07:30" 形式
                                let md = String(ub.date.dropFirst(5)).replacingOccurrences(of: "-", with: "/")
                                Text("· \(md)(\(ub.weekday))")
                                    .font(.system(size: 12))
                                    .foregroundStyle(T.inkMute)
                            }
                        }
                        if !ub.isToday {
                            Text(ub.line.route)
                                .font(.system(size: 11))
                                .foregroundStyle(T.inkMute)
                                .lineLimit(1)
                        }
                    } else {
                        Text("次のバス便")
                            .font(.system(size: 13))
                            .foregroundStyle(T.inkSub)
                        Text("予定なし")
                            .font(.system(size: 14))
                            .foregroundStyle(T.inkMute)
                    }
                }
                Spacer(minLength: 0)
                Ic.chevR(16).foregroundStyle(T.inkMute)
            }
        }
    }

    // MARK: Package — JSX: dangerBg / danger icon / 快递 · N 件待領

    private var packageCard: some View {
        HomeCard(pad: 14, onTap: { router.go(.homePackages) }) {
            HStack(spacing: 12) {
                ZStack(alignment: .topTrailing) {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(T.dangerBg)
                        .frame(width: 44, height: 44)
                        .overlay { Ic.package(22).foregroundStyle(T.danger) }
                    if pendingPkg > 0 {
                        // JSX: top -4 right -4 / 20×20 / radius 10 / danger / 11 700 / 2 white border
                        Text("\(pendingPkg)")
                            .font(.system(size: 11, weight: .bold, design: .monospaced))
                            .foregroundStyle(.white)
                            .frame(width: 20, height: 20)
                            .background(Circle().fill(T.danger))
                            .overlay(Circle().stroke(.white, lineWidth: 2))
                            .offset(x: 4, y: -4)
                    }
                }

                VStack(alignment: .leading, spacing: 2) {
                    // 自然日本語: 宅配便 · N 件未受取
                    Text("宅配便 · \(pendingPkg) 件未受取")
                        .font(.system(size: 15, weight: .bold))
                        .foregroundStyle(T.ink)
                    Text("Amazon · 本日到着")
                        .font(.system(size: 12))
                        .foregroundStyle(T.inkSub)
                }
                Spacer(minLength: 0)
                Ic.chevR(16).foregroundStyle(T.inkMute)
            }
        }
    }

    // MARK: Events — JSX: accent.22 32×32 icon / 今週の活動 · 3 件 / 列 2 件

    private var eventsCard: some View {
        HomeCard(pad: 14, onTap: { router.go(.homeEvents) }) {
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    HStack(spacing: 10) {
                        ZStack {
                            RoundedRectangle(cornerRadius: 10, style: .continuous)
                                .fill(T.accent.opacity(0.13))        // JSX ${T.accent}22 = ~13% alpha
                                .frame(width: 32, height: 32)
                            Ic.calendar(18).foregroundStyle(T.primary)
                        }
                        Text("今週の活動 · \(SEED.events.count) 件")
                            .font(.system(size: 14, weight: .bold))
                            .foregroundStyle(T.ink)
                    }
                    Spacer(minLength: 0)
                    Ic.chevR(16).foregroundStyle(T.inkMute)
                }

                VStack(spacing: 0) {
                    ForEach(SEED.events.prefix(2), id: \.id) { e in
                        HStack(spacing: 10) {
                            // JSX: mono 11 / inkMute / w 50 · slice(5) = "MM-DD"
                            Text(String(e.date.dropFirst(5)))
                                .font(.system(size: 11, design: .monospaced))
                                .foregroundStyle(T.inkMute)
                                .frame(width: 50, alignment: .leading)
                            Text(e.title)
                                .font(.system(size: 13))
                                .foregroundStyle(T.ink)
                            Spacer(minLength: 0)
                            Text(e.time)
                                .font(.system(size: 11))
                                .foregroundStyle(T.inkMute)
                        }
                        .padding(.vertical, 6)
                    }
                }
            }
        }
    }

    // MARK: Music — リクエスト曲（CommunityTab 砍后 #37 入口在这里恢复）
    //
    // 老師 38 条 #37「音楽機能は残す」→ 紫グラデの 44 アイコン + 件数 + トップ 1 曲のプレビュー
    // top song = SEED.songs[0]（up 順で sort 済み seed）

    private var musicCard: some View {
        let topSong = SEED.songs.first
        return HomeCard(pad: 14, onTap: { router.go(.homeMusic) }) {
            HStack(spacing: 12) {
                ZStack {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(
                            LinearGradient(
                                colors: [Color(hex: 0xa78bfa), Color(hex: 0x7c3aed)],
                                startPoint: .topLeading, endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 44, height: 44)
                    Ic.music(22).foregroundStyle(.white)
                }
                VStack(alignment: .leading, spacing: 2) {
                    Text("リクエスト曲 · \(SEED.songs.count) 件")
                        .font(.system(size: 14, weight: .bold))
                        .foregroundStyle(T.ink)
                    if let s = topSong {
                        Text("\(s.title) · \(s.artist)")
                            .font(.system(size: 12))
                            .foregroundStyle(T.inkSub)
                            .lineLimit(1)
                    } else {
                        Text("まだ投稿がありません")
                            .font(.system(size: 12))
                            .foregroundStyle(T.inkMute)
                    }
                }
                Spacer(minLength: 0)
                Ic.chevR(16).foregroundStyle(T.inkMute)
            }
        }
    }

    // MARK: Lost — JSX: 3 列方格 / aspect 1 / color .22 bg + linear-gradient overlay

    private var lostCard: some View {
        HomeCard(pad: 14, onTap: { router.go(.homeLost) }) {
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Text("遺失物 · 最新")
                        .font(.system(size: 14, weight: .bold))
                        .foregroundStyle(T.ink)
                    Spacer(minLength: 0)
                    Ic.chevR(16).foregroundStyle(T.inkMute)
                }
                LazyVGrid(columns: [
                    GridItem(.flexible(), spacing: 8),
                    GridItem(.flexible(), spacing: 8),
                    GridItem(.flexible(), spacing: 8),
                ], spacing: 8) {
                    ForEach(SEED.lost.prefix(3), id: \.id) { item in
                        lostTile(item)
                    }
                }
            }
        }
    }

    @ViewBuilder
    private func lostTile(_ item: LostItem) -> some View {
        let c = Color(hexString: item.color) ?? T.inkFaint
        ZStack(alignment: .bottomLeading) {
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .fill(c.opacity(0.13))                      // JSX color+'22' ≈ 13%
                .aspectRatio(1, contentMode: .fit)
                .overlay(
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                        .stroke(T.hair, lineWidth: 0.5)
                )
            // JSX: linear-gradient(135deg, color66 0%, color22 100%)
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .fill(
                    LinearGradient(
                        colors: [c.opacity(0.4), c.opacity(0.13)],
                        startPoint: .topLeading, endPoint: .bottomTrailing
                    )
                )
                .aspectRatio(1, contentMode: .fit)

            // JSX: title.slice(0,8) / 10 / 600 white / text-shadow
            Text(String(item.title.prefix(8)))
                .font(.system(size: 10, weight: .semibold))
                .foregroundStyle(.white)
                .shadow(color: .black.opacity(0.4), radius: 1, x: 0, y: 1)
                .padding(8)
        }
    }

    // MARK: Suggest — JSX: 💭 emoji 20 / 40×40 pill bg

    private var suggestCard: some View {
        HomeCard(pad: 14, onTap: { router.go(.homeSuggest) }) {
            HStack(spacing: 12) {
                ZStack {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(T.pill)
                        .frame(width: 40, height: 40)
                    Text("💭").font(.system(size: 20))
                }
                VStack(alignment: .leading, spacing: 2) {
                    Text("匿名で建議を送る")
                        .font(.system(size: 13.5, weight: .semibold))
                        .foregroundStyle(T.ink)
                    Text("寮運営への匿名フィードバック")
                        .font(.system(size: 11))
                        .foregroundStyle(T.inkMute)
                }
                Spacer(minLength: 0)
                Ic.chevR(16).foregroundStyle(T.inkMute)
            }
        }
    }
}


// ───────────────────────────────────────────────────────────
// MARK: - RollcallSheet · 4 态 state machine (⭐ money shot)
// ───────────────────────────────────────────────────────────

/// State: idle（準備・pulse）→ scanning（0.5s spinner）→ success（2s auto close）/ fail（retry）
struct RollcallSheet: View {
    @EnvironmentObject var app: AppStore

    enum Step { case idle, scanning, success, fail }

    @State private var step: Step = .idle
    @State private var pulseOn: Bool = false
    @State private var successZoomIn: Bool = false
    @State private var rotating: Bool = false

    var body: some View {
        GlassSheet(onClose: { cancel() }) {
            ZStack {
                switch step {
                case .idle:     idleView
                case .scanning: scanningView
                case .success:  successView
                case .fail:     failView
                }
            }
            .animation(.easeOut(duration: 0.22), value: step)
        }
        .onAppear {
            step = .idle
            pulseOn = true
        }
        .onDisappear {
            pulseOn = false
            successZoomIn = false
            rotating = false
        }
    }

    // MARK: idle — scanning の準備ができました

    private var idleView: some View {
        VStack(alignment: .leading, spacing: 0) {
            // JSX: 24 800 / letterSpacing -0.01em / lineHeight 1.3 / marginBottom 14
            Text("スキャンの準備が\nできました")
                .font(.system(size: 24, weight: .heavy))
                .kerning(-0.24)
                .lineSpacing(6)
                .foregroundStyle(T.ink)
                .padding(.bottom, 14)

            // JSX: 14 inkSub / lineHeight 1.75 / marginBottom 24
            VStack(alignment: .leading, spacing: 4) {
                Text("① 入口の NFC マークにスマホをかざす")
                Text("② 画面が光ったら完了")
            }
            .font(.system(size: 14))
            .lineSpacing(4)
            .foregroundStyle(T.inkSub)
            .padding(.bottom, 20)

            // JSX idle 専用 warn banner
            // JSX: padding 10 14 / radius 12 / warnBg / warn.40 border / warnDeep 12 / lh 1.5
            HStack(alignment: .top, spacing: 6) {
                Text("⚠")
                    .font(.system(size: 12))
                Text("点呼時間外です。点呼開始まで少々お待ちください。")
                    .font(.system(size: 12))
                    .lineSpacing(2)
            }
            .foregroundStyle(T.warnDeep)
            .padding(.horizontal, 14).padding(.vertical, 10)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .fill(T.warnBg)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .stroke(T.warn.opacity(0.25), lineWidth: 1)
                    )
            )
            .padding(.bottom, 20)

            // JSX: 140×140 circle / radial accent gradient / 2pt accent border / pulse 1.8s
            HStack {
                Spacer()
                ZStack {
                    Circle()
                        .fill(
                            RadialGradient(
                                colors: [T.accent.opacity(0.25), T.accent.opacity(0.05)],
                                center: .center,
                                startRadius: 0, endRadius: 70
                            )
                        )
                        .frame(width: 140, height: 140)
                        .overlay(
                            Circle().stroke(T.accent, lineWidth: 2)
                        )
                        .scaleEffect(pulseOn ? 1.0 : 0.94)
                        .opacity(pulseOn ? 0.9 : 0.55)
                        .animation(
                            .easeInOut(duration: 0.7).repeatForever(autoreverses: true),
                            value: pulseOn
                        )

                    // phoneTap 近似图（SF Symbol）· JSX: scale 1.6 · 48pt * 1.6 ≈ 64
                    Image(systemName: "iphone.radiowaves.left.and.right")
                        .font(.system(size: 60, weight: .regular))
                        .foregroundStyle(T.primary)
                }
                Spacer()
            }
            .padding(.bottom, 24)

            // JSX: h 54 / radius 16 / btnGradRadial / 16 700 / letterSpacing 0.04em / shadow
            Button { simulate() } label: {
                Text("NFC をかざす")
                    .font(.system(size: 16, weight: .bold))
                    .kerning(0.64)           // 0.04em × 16
                    .foregroundStyle(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 54)
                    .background {
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .fill(T.rollBtnGrad)
                    }
                    .shadow(color: T.primary.opacity(0.32), radius: 18, x: 0, y: 6)
            }
            .buttonStyle(.plain)
            .padding(.bottom, 10)

            // JSX: h 48 / radius 16 / ink.06 bg / inkSub 15 600
            Button { cancel() } label: {
                Text("キャンセル")
                    .font(.system(size: 15, weight: .semibold))
                    .foregroundStyle(T.inkSub)
                    .frame(maxWidth: .infinity)
                    .frame(height: 48)
                    .background {
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .fill(T.ink.opacity(0.06))
                    }
            }
            .buttonStyle(.plain)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.top, 4)
    }

    // MARK: scanning — 0.5s interim spinner

    private var scanningView: some View {
        VStack(spacing: 18) {
            // JSX 未直接定义 — 本态从 prompt 约束推导
            Text("スキャン中…")
                .font(.system(size: 22, weight: .bold))
                .foregroundStyle(T.ink)

            ZStack {
                Circle()
                    .stroke(T.accent.opacity(0.3), lineWidth: 3)
                    .frame(width: 120, height: 120)
                Circle()
                    .trim(from: 0, to: 0.3)
                    .stroke(T.primary, style: StrokeStyle(lineWidth: 3, lineCap: .round))
                    .frame(width: 120, height: 120)
                    .rotationEffect(.degrees(rotating ? 360 : 0))
                    .animation(
                        .linear(duration: 0.9).repeatForever(autoreverses: false),
                        value: rotating
                    )
                Image(systemName: "dot.radiowaves.left.and.right")
                    .font(.system(size: 44))
                    .foregroundStyle(T.primary)
            }
            .padding(.vertical, 6)
            .onAppear { rotating = true }
            .onDisappear { rotating = false }

            Text("動かないでください")
                .font(.system(size: 13))
                .foregroundStyle(T.inkSub)
        }
        .padding(.vertical, 28)
        .frame(maxWidth: .infinity)
    }

    // MARK: success — チェックイン完了 · 21:02 · 時間内

    private var successView: some View {
        VStack(spacing: 0) {
            // JSX: 96×96 circle / linear-gradient(135deg, 8bc6a3 → 4a9478) / checkmark 28 · scale 2.4
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color(hex: 0x8bc6a3), Color(hex: 0x4a9478)],
                            startPoint: .topLeading, endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 96, height: 96)
                    .shadow(color: Color(hex: 0x4a9478).opacity(0.3), radius: 16, x: 0, y: 12)
                Image(systemName: "checkmark")
                    .font(.system(size: 44, weight: .heavy))
                    .foregroundStyle(.white)
            }
            // JSX: zoom .4s cubic-bezier(.2,.8,.2,1) · 成功圆进场 pop-in
            .scaleEffect(successZoomIn ? 1.0 : 0.6)
            .opacity(successZoomIn ? 1.0 : 0)
            .animation(.spring(response: 0.4, dampingFraction: 0.7), value: successZoomIn)
            .onAppear {
                // reset first, then animate
                successZoomIn = false
                DispatchQueue.main.async { successZoomIn = true }
            }
            .onDisappear { successZoomIn = false }
            .padding(.bottom, 20)

            // JSX: 22 700 / marginBottom 10
            Text("チェックイン完了")
                .font(.system(size: 22, weight: .bold))
                .foregroundStyle(T.ink)
                .padding(.bottom, 10)

            // JSX: Pill tone=ok / 13 / padding 6 14
            Text("\(app.checkinAt ?? "21:02") · \(app.checkinKind ?? "時間内")")
                .font(.system(size: 13, weight: .bold))
                .kerning(0.26)
                .padding(.horizontal, 14).padding(.vertical, 6)
                .foregroundStyle(T.okDeep)
                .background(Capsule().fill(T.okBg))

            Text("お疲れさまでした")
                .font(.system(size: 13))
                .foregroundStyle(T.inkSub)
                .padding(.top, 18)
        }
        .padding(.vertical, 28)
        .frame(maxWidth: .infinity)
    }

    // MARK: fail — retry

    private var failView: some View {
        VStack(spacing: 0) {
            // 赤 circle + ✗
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color(hex: 0xe88a80), Color(hex: 0xc44848)],
                            startPoint: .topLeading, endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 88, height: 88)
                    .shadow(color: T.danger.opacity(0.3), radius: 14, x: 0, y: 10)
                Image(systemName: "xmark")
                    .font(.system(size: 40, weight: .heavy))
                    .foregroundStyle(.white)
            }
            .padding(.bottom, 18)

            Text("失敗。もう一度")
                .font(.system(size: 22, weight: .bold))
                .foregroundStyle(T.ink)
                .padding(.bottom, 10)

            Text("NFC を読み取れませんでした")
                .font(.system(size: 13))
                .foregroundStyle(T.inkSub)
                .padding(.bottom, 22)

            Button {
                withAnimation(.easeOut(duration: 0.22)) { step = .idle }
            } label: {
                Text("再試行")
                    .font(.system(size: 16, weight: .bold))
                    .kerning(0.64)
                    .foregroundStyle(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 54)
                    .background {
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .fill(T.rollBtnGrad)
                    }
                    .shadow(color: T.primary.opacity(0.32), radius: 18, x: 0, y: 6)
            }
            .buttonStyle(.plain)
        }
        .padding(.vertical, 12)
        .frame(maxWidth: .infinity)
    }

    // MARK: transition helpers

    private func simulate() {
        withAnimation(.easeOut(duration: 0.22)) { step = .scanning }
        Task {
            try? await Task.sleep(nanoseconds: 500_000_000)
            await MainActor.run {
                app.recordCheckin()
                withAnimation(.easeOut(duration: 0.22)) { step = .success }
            }
            try? await Task.sleep(nanoseconds: 2_000_000_000)
            await MainActor.run {
                let at = app.checkinAt ?? "21:02"
                app.closeSheet()
                app.showToast("チェックイン完了 · \(at)")
                step = .idle
            }
        }
    }

    private func cancel() {
        app.closeSheet()
        step = .idle
    }
}

// ───────────────────────────────────────────────────────────
// MARK: - StudyCheckinSheet · 学習 NFC 3 回タップ签到 (system_features §7.3.3)
// ───────────────────────────────────────────────────────────

/// State: idle → scanning（0.5s）→ success（2s auto close）/ fail（retry）
/// 1 sheet 開く度に 1 回分の tap を記録する（次回開いた時は次の tap）
struct StudyCheckinSheet: View {
    @EnvironmentObject var app: AppStore

    enum Step { case idle, scanning, success, fail }

    @State private var step: Step = .idle
    @State private var pulseOn: Bool = false
    @State private var rotating: Bool = false
    @State private var recordedTap: StudyTap? = nil

    private var nextTap: StudyTap? { app.nextStudyTap }

    private var stepLabel: String {
        switch nextTap {
        case .start: return "学習開始のタップ"
        case .mid:   return "中場のタップ"
        case .end:   return "学習終了のタップ"
        case .none:  return "本日完了"
        }
    }

    private var stepNumber: Int {
        switch nextTap {
        case .start: return 1
        case .mid:   return 2
        case .end:   return 3
        case .none:  return 3
        }
    }

    private var stepTimeWindow: String {
        switch nextTap {
        case .start: return "19:35〜19:40"
        case .mid:   return "20:40〜20:50"
        case .end:   return "21:40〜21:50"
        case .none:  return "—"
        }
    }

    var body: some View {
        GlassSheet(onClose: { cancel() }) {
            ZStack {
                switch step {
                case .idle:     idleView
                case .scanning: scanningView
                case .success:  successView
                case .fail:     failView
                }
            }
            .animation(.easeOut(duration: 0.22), value: step)
        }
        .onAppear {
            step = .idle
            pulseOn = true
        }
        .onDisappear {
            pulseOn = false
            rotating = false
        }
    }

    // MARK: idle

    private var idleView: some View {
        VStack(alignment: .leading, spacing: 0) {
            Text("\(stepNumber) / 3 回目")
                .font(.system(size: 11, weight: .heavy))
                .kerning(1.8)
                .textCase(.uppercase)
                .foregroundStyle(T.primary)
                .padding(.bottom, 6)
            Text(stepLabel)
                .font(.system(size: 24, weight: .heavy))
                .kerning(-0.24)
                .lineSpacing(6)
                .foregroundStyle(T.ink)
                .padding(.bottom, 12)

            HStack(spacing: 6) {
                Image(systemName: "clock")
                    .font(.system(size: 12))
                Text("受付時間: \(stepTimeWindow)")
                    .font(.system(size: 12.5, weight: .semibold))
            }
            .foregroundStyle(T.inkSub)
            .padding(.horizontal, 12).padding(.vertical, 8)
            .background {
                RoundedRectangle(cornerRadius: 10, style: .continuous).fill(T.pill)
            }
            .padding(.bottom, 18)

            VStack(alignment: .leading, spacing: 4) {
                Text("① 学習室入口の NFC マークにスマホをかざす")
                Text("② 画面が光ったら完了")
            }
            .font(.system(size: 14))
            .lineSpacing(4)
            .foregroundStyle(T.inkSub)
            .padding(.bottom, 22)

            HStack {
                Spacer()
                ZStack {
                    Circle()
                        .fill(
                            RadialGradient(
                                colors: [T.accent.opacity(0.25), T.accent.opacity(0.05)],
                                center: .center,
                                startRadius: 0, endRadius: 70
                            )
                        )
                        .frame(width: 140, height: 140)
                        .overlay(Circle().stroke(T.accent, lineWidth: 2))
                        .scaleEffect(pulseOn ? 1.0 : 0.94)
                        .opacity(pulseOn ? 0.9 : 0.55)
                        .animation(
                            .easeInOut(duration: 0.7).repeatForever(autoreverses: true),
                            value: pulseOn
                        )
                    Image(systemName: "iphone.radiowaves.left.and.right")
                        .font(.system(size: 60, weight: .regular))
                        .foregroundStyle(T.primary)
                }
                Spacer()
            }
            .padding(.bottom, 24)

            Button { simulate() } label: {
                Text("NFC をかざす")
                    .font(.system(size: 16, weight: .bold))
                    .kerning(0.64)
                    .foregroundStyle(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 54)
                    .background {
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .fill(T.rollBtnGrad)
                    }
                    .shadow(color: T.primary.opacity(0.32), radius: 18, x: 0, y: 6)
            }
            .buttonStyle(.plain)
            .padding(.bottom, 10)

            Button { cancel() } label: {
                Text("キャンセル")
                    .font(.system(size: 15, weight: .semibold))
                    .foregroundStyle(T.inkSub)
                    .frame(maxWidth: .infinity)
                    .frame(height: 48)
                    .background {
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .fill(T.ink.opacity(0.06))
                    }
            }
            .buttonStyle(.plain)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.top, 4)
    }

    private var scanningView: some View {
        VStack(spacing: 18) {
            Text("スキャン中…")
                .font(.system(size: 22, weight: .bold))
                .foregroundStyle(T.ink)

            ZStack {
                Circle().stroke(T.accent.opacity(0.3), lineWidth: 3)
                    .frame(width: 120, height: 120)
                Circle()
                    .trim(from: 0, to: 0.3)
                    .stroke(T.primary, style: StrokeStyle(lineWidth: 3, lineCap: .round))
                    .frame(width: 120, height: 120)
                    .rotationEffect(.degrees(rotating ? 360 : 0))
                    .animation(
                        .linear(duration: 0.9).repeatForever(autoreverses: false),
                        value: rotating
                    )
                Image(systemName: "dot.radiowaves.left.and.right")
                    .font(.system(size: 44))
                    .foregroundStyle(T.primary)
            }
            .padding(.vertical, 6)
            .onAppear { rotating = true }
            .onDisappear { rotating = false }

            Text("動かないでください")
                .font(.system(size: 13))
                .foregroundStyle(T.inkSub)
        }
        .padding(.vertical, 28)
        .frame(maxWidth: .infinity)
    }

    private var successView: some View {
        VStack(spacing: 0) {
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color(hex: 0x8bc6a3), Color(hex: 0x4a9478)],
                            startPoint: .topLeading, endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 96, height: 96)
                    .shadow(color: Color(hex: 0x4a9478).opacity(0.3), radius: 16, x: 0, y: 12)
                Image(systemName: "checkmark")
                    .font(.system(size: 44, weight: .heavy))
                    .foregroundStyle(.white)
            }
            .padding(.bottom, 20)

            Text(successTitle)
                .font(.system(size: 22, weight: .bold))
                .foregroundStyle(T.ink)
                .padding(.bottom, 10)

            if let n = nextTapAfterRecord {
                Text("次は \(n.label) を \(n.window) に")
                    .font(.system(size: 13))
                    .foregroundStyle(T.inkSub)
            } else {
                Text("\(Self.fmtNow()) · 本日の学習出席は完了")
                    .font(.system(size: 13, weight: .bold))
                    .kerning(0.26)
                    .padding(.horizontal, 14).padding(.vertical, 6)
                    .foregroundStyle(T.okDeep)
                    .background(Capsule().fill(T.okBg))
            }
        }
        .padding(.vertical, 28)
        .frame(maxWidth: .infinity)
    }

    private var successTitle: String {
        switch recordedTap {
        case .start: return "開始タップ完了"
        case .mid:   return "中場タップ完了"
        case .end:   return "終了タップ完了"
        case .none:  return "完了"
        }
    }

    private var nextTapAfterRecord: (label: String, window: String)? {
        // record 後に次の tap があれば案内
        let after = app.nextStudyTap
        switch after {
        case .start: return ("学習開始", "19:35〜19:40")
        case .mid:   return ("中場", "20:40〜20:50")
        case .end:   return ("学習終了", "21:40〜21:50")
        case .none:  return nil
        }
    }

    private var failView: some View {
        VStack(spacing: 0) {
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color(hex: 0xe88a80), Color(hex: 0xc44848)],
                            startPoint: .topLeading, endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 88, height: 88)
                    .shadow(color: T.danger.opacity(0.3), radius: 14, x: 0, y: 10)
                Image(systemName: "xmark")
                    .font(.system(size: 40, weight: .heavy))
                    .foregroundStyle(.white)
            }
            .padding(.bottom, 18)

            Text("失敗。もう一度")
                .font(.system(size: 22, weight: .bold))
                .foregroundStyle(T.ink)
                .padding(.bottom, 10)

            Text("NFC を読み取れませんでした")
                .font(.system(size: 13))
                .foregroundStyle(T.inkSub)
                .padding(.bottom, 22)

            Button {
                withAnimation(.easeOut(duration: 0.22)) { step = .idle }
            } label: {
                Text("再試行")
                    .font(.system(size: 16, weight: .bold))
                    .kerning(0.64)
                    .foregroundStyle(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 54)
                    .background {
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .fill(T.rollBtnGrad)
                    }
                    .shadow(color: T.primary.opacity(0.32), radius: 18, x: 0, y: 6)
            }
            .buttonStyle(.plain)
        }
        .padding(.vertical, 12)
        .frame(maxWidth: .infinity)
    }

    private func simulate() {
        withAnimation(.easeOut(duration: 0.22)) { step = .scanning }
        Task {
            try? await Task.sleep(nanoseconds: 500_000_000)
            await MainActor.run {
                recordedTap = app.recordStudyTap()
                withAnimation(.easeOut(duration: 0.22)) { step = .success }
            }
            try? await Task.sleep(nanoseconds: 2_000_000_000)
            await MainActor.run {
                let label = recordedTap?.label ?? "—"
                app.closeSheet()
                if app.nextStudyTap == nil {
                    app.showToast("学習出席完了 · 全 3 回 タップ済み")
                } else {
                    app.showToast("\(label) 完了")
                }
                step = .idle
            }
        }
    }

    private func cancel() {
        app.closeSheet()
        step = .idle
    }

    private static func fmtNow() -> String {
        let f = DateFormatter()
        f.dateFormat = "HH:mm"
        f.locale = Locale(identifier: "ja_JP")
        return f.string(from: Date())
    }
}

private extension StudyTap {
    var label: String {
        switch self {
        case .start: return "学習開始"
        case .mid:   return "中場"
        case .end:   return "学習終了"
        }
    }
}

// ───────────────────────────────────────────────────────────
// MARK: - FeedbackSheet · 3 選 1
// ───────────────────────────────────────────────────────────

struct FeedbackSheet: View {
    @EnvironmentObject var app: AppStore

    private struct Item: Identifiable {
        let id: String
        let icon: String
        let label: String
        let detail: String
        let kind: SheetKind
    }

    private let items: [Item] = [
        .init(id: "health",  icon: "🤒",
              label: "体調問題を報告",
              detail: "発熱・頭痛・その他の症状を先生に通知",
              kind: .health),
        .init(id: "absence", icon: "📝",
              label: "今回欠席の申請",
              detail: "今回の点呼を欠席したい理由を申請",
              kind: .absence),
        .init(id: "other",   icon: "💬",
              label: "その他の問題",
              detail: "遅刻理由・外出中・NFC 不具合など",
              kind: .other),
    ]

    var body: some View {
        GlassSheet(onClose: { app.closeSheet() }) {
            VStack(alignment: .leading, spacing: 0) {
                // JSX: 20 800 / marginBottom 6
                Text("反馈を送る")
                    .font(.system(size: 20, weight: .heavy))
                    .foregroundStyle(T.ink)
                    .padding(.bottom, 6)

                // JSX: 13 inkSub / marginBottom 18
                Text("どの種類の反馈を送りますか？")
                    .font(.system(size: 13))
                    .foregroundStyle(T.inkSub)
                    .padding(.bottom, 18)

                VStack(spacing: 10) {
                    ForEach(items) { it in
                        Button { app.openSheet(it.kind) } label: {
                            // JSX: padding 14 16 / radius 16 / white.55 bg / hair border / gap 14
                            HStack(spacing: 14) {
                                Text(it.icon).font(.system(size: 28))
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(it.label)
                                        .font(.system(size: 15, weight: .bold))
                                        .foregroundStyle(T.ink)
                                    Text(it.detail)
                                        .font(.system(size: 12))
                                        .foregroundStyle(T.inkSub)
                                        .multilineTextAlignment(.leading)
                                }
                                Spacer(minLength: 0)
                                Ic.chevR(16).foregroundStyle(T.inkMute)
                            }
                            .padding(.horizontal, 16).padding(.vertical, 14)
                            .background {
                                RoundedRectangle(cornerRadius: 16, style: .continuous)
                                    .fill(Color.white.opacity(0.55))
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                                            .stroke(T.hair, lineWidth: 0.5)
                                    )
                            }
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(.top, 8)
        }
    }
}

// ───────────────────────────────────────────────────────────
// MARK: - HealthSheet · 症状 + 体温 + 补足
// ───────────────────────────────────────────────────────────

struct HealthSheet: View {
    @EnvironmentObject var app: AppStore

    @State private var sym: String = ""
    @State private var temp: String = ""
    @State private var note: String = ""

    // JSX options
    private let symptoms = ["発熱", "頭痛", "腹痛", "吐き気", "風邪症状", "その他"]

    var body: some View {
        GlassSheet(onClose: { app.closeSheet() }) {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    // JSX: 20 800 / marginBottom 20
                    Text("体調不良を報告")
                        .font(.system(size: 20, weight: .heavy))
                        .foregroundStyle(T.ink)

                    // Field: 症状 *
                    VStack(alignment: .leading, spacing: 7) {
                        HStack(spacing: 4) {
                            Text("症状")
                                .font(.system(size: 13, weight: .semibold))
                                .foregroundStyle(T.inkSub)
                            Text("*").foregroundStyle(T.danger)
                        }
                        // JSX: Radio row layout, wrap
                        FlowLayout(spacing: 8) {
                            ForEach(symptoms, id: \.self) { s in
                                radioChip(title: s, selected: sym == s) { sym = s }
                            }
                        }
                    }

                    // Field: 体温（任意）
                    VStack(alignment: .leading, spacing: 7) {
                        Text("体温（任意）")
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundStyle(T.inkSub)
                        TField(text: $temp, placeholder: "例: 37.2", keyboard: .decimalPad)
                    }

                    // Field: 補足
                    VStack(alignment: .leading, spacing: 7) {
                        Text("補足")
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundStyle(T.inkSub)
                        TArea(text: $note,
                              placeholder: "具体的な症状があれば教えてください",
                              rows: 3)
                    }

                    PrimaryButton(title: "提出", enabled: !sym.isEmpty) {
                        app.closeSheet()
                        app.showToast("先生に通知しました")
                    }
                    .padding(.top, 2)
                }
                .padding(.top, 8)
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .frame(maxHeight: 560)
        }
    }

    /// JSX Radio option chip · selected: primary outline + pill tint
    @ViewBuilder
    private func radioChip(title: String, selected: Bool, onTap: @escaping () -> Void) -> some View {
        Button(action: onTap) {
            Text(title)
                .font(.system(size: 14, weight: selected ? .bold : .medium))
                .foregroundStyle(selected ? T.primary : T.ink)
                .padding(.horizontal, 16).padding(.vertical, 10)
                .background {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(selected ? T.primary.opacity(0.06) : T.pearl)
                }
                .overlay {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .stroke(selected ? T.primary : T.hair, lineWidth: selected ? 1.5 : 1)
                }
        }
        .buttonStyle(.plain)
    }
}

// ───────────────────────────────────────────────────────────
// MARK: - AbsenceSheet · reason textarea
// ───────────────────────────────────────────────────────────

struct AbsenceSheet: View {
    @EnvironmentObject var app: AppStore

    @State private var reason: String = ""

    var body: some View {
        GlassSheet(onClose: { app.closeSheet() }) {
            VStack(alignment: .leading, spacing: 18) {
                Text("今回の点呼を欠席したい")
                    .font(.system(size: 20, weight: .heavy))
                    .foregroundStyle(T.ink)

                // Field 理由 *
                VStack(alignment: .leading, spacing: 7) {
                    HStack(spacing: 4) {
                        Text("理由")
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundStyle(T.inkSub)
                        Text("*").foregroundStyle(T.danger)
                    }
                    TArea(text: $reason,
                          placeholder: "欠席の理由をお書きください",
                          rows: 5)
                }

                PrimaryButton(
                    title: "提出",
                    enabled: !reason.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                ) {
                    app.closeSheet()
                    app.showToast("審査中です")
                }
                .padding(.top, 2)
            }
            .padding(.top, 8)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}

// ───────────────────────────────────────────────────────────
// MARK: - OtherSheet · 分類 + 内容
// ───────────────────────────────────────────────────────────

struct OtherSheet: View {
    @EnvironmentObject var app: AppStore

    @State private var cat: String = ""
    @State private var content: String = ""

    private let categories = ["遅刻理由", "外出中", "NFC 不具合", "その他"]

    var body: some View {
        GlassSheet(onClose: { app.closeSheet() }) {
            VStack(alignment: .leading, spacing: 18) {
                Text("その他の問題")
                    .font(.system(size: 20, weight: .heavy))
                    .foregroundStyle(T.ink)

                VStack(alignment: .leading, spacing: 7) {
                    HStack(spacing: 4) {
                        Text("分類")
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundStyle(T.inkSub)
                        Text("*").foregroundStyle(T.danger)
                    }
                    FlowLayout(spacing: 8) {
                        ForEach(categories, id: \.self) { c in
                            radioChip(title: c, selected: cat == c) { cat = c }
                        }
                    }
                }

                VStack(alignment: .leading, spacing: 7) {
                    HStack(spacing: 4) {
                        Text("内容")
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundStyle(T.inkSub)
                        Text("*").foregroundStyle(T.danger)
                    }
                    TArea(text: $content, placeholder: "詳しく教えてください", rows: 4)
                }

                PrimaryButton(
                    title: "提出",
                    enabled: !cat.isEmpty &&
                        !content.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                ) {
                    app.closeSheet()
                    app.showToast("送信しました")
                }
                .padding(.top, 2)
            }
            .padding(.top, 8)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    @ViewBuilder
    private func radioChip(title: String, selected: Bool, onTap: @escaping () -> Void) -> some View {
        Button(action: onTap) {
            Text(title)
                .font(.system(size: 14, weight: selected ? .bold : .medium))
                .foregroundStyle(selected ? T.primary : T.ink)
                .padding(.horizontal, 16).padding(.vertical, 10)
                .background {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(selected ? T.primary.opacity(0.06) : T.pearl)
                }
                .overlay {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .stroke(selected ? T.primary : T.hair, lineWidth: selected ? 1.5 : 1)
                }
        }
        .buttonStyle(.plain)
    }
}

// ───────────────────────────────────────────────────────────
// MARK: - FlowLayout · 横流 / 换行（SwiftUI 原生 Layout）
// ───────────────────────────────────────────────────────────

/// JSX Radio layout='row' 自动换行对等（flexWrap:wrap / gap:8）
private struct FlowLayout: Layout {
    var spacing: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let maxW = proposal.width ?? .infinity
        var x: CGFloat = 0, y: CGFloat = 0, rowH: CGFloat = 0, totalW: CGFloat = 0
        for sv in subviews {
            let s = sv.sizeThatFits(.unspecified)
            if x + s.width > maxW, x > 0 {
                y += rowH + spacing
                x = 0; rowH = 0
            }
            x += s.width + spacing
            rowH = max(rowH, s.height)
            totalW = max(totalW, x)
        }
        return CGSize(width: totalW, height: y + rowH)
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let maxW = bounds.width
        var x: CGFloat = bounds.minX, y: CGFloat = bounds.minY, rowH: CGFloat = 0
        for sv in subviews {
            let s = sv.sizeThatFits(.unspecified)
            if x - bounds.minX + s.width > maxW, x > bounds.minX {
                y += rowH + spacing
                x = bounds.minX; rowH = 0
            }
            sv.place(at: CGPoint(x: x, y: y), proposal: ProposedViewSize(s))
            x += s.width + spacing
            rowH = max(rowH, s.height)
        }
    }
}

// ───────────────────────────────────────────────────────────
// MARK: - Previews
// ───────────────────────────────────────────────────────────

#Preview("HomeView") {
    HomeView()
        .environmentObject(RouterStore(initial: .home))
        .environmentObject(AppStore())
}

#Preview("LifeTab") {
    ScrollView {
        LifeTab()
            .padding(16)
    }
    .background(T.pearl.ignoresSafeArea())
    .environmentObject(RouterStore(initial: .home))
    .environmentObject(AppStore())
}


#Preview("RollcallSheet") {
    ZStack {
        T.pearl.ignoresSafeArea()
        RollcallSheet()
    }
    .environmentObject(AppStore())
}

#Preview("FeedbackSheet") {
    ZStack {
        T.pearl.ignoresSafeArea()
        FeedbackSheet()
    }
    .environmentObject(AppStore())
}

#Preview("HealthSheet") {
    ZStack {
        T.pearl.ignoresSafeArea()
        HealthSheet()
    }
    .environmentObject(AppStore())
}

#Preview("AbsenceSheet") {
    ZStack {
        T.pearl.ignoresSafeArea()
        AbsenceSheet()
    }
    .environmentObject(AppStore())
}

#Preview("OtherSheet") {
    ZStack {
        T.pearl.ignoresSafeArea()
        OtherSheet()
    }
    .environmentObject(AppStore())
}
