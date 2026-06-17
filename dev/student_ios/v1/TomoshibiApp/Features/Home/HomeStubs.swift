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

// Translation（翻译框架）— 公告「翻訳」按钮用 TranslationSession 程序化接口（iOS 18.0+）把正文原地翻成母语，拿到译文自己显示
// @preconcurrency：Translation 框架的 TranslationSession 还没标 Sendable，在 Swift 6 完全并发下从 MainActor 闭包调 translate 会报「sending session」数据竞争；用 @preconcurrency 把这类来自该模块的并发报错降级，是 Apple 框架并发标注未跟上时的标准过渡手段。
@preconcurrency import Translation

// FoundationModels（设备端大模型框架，iOS 26+ 且 Apple Intelligence 机种）— 公告「AI 要約」按钮用它直接调本地模型生成要点
// 框架弱链接：import 本身在低部署目标（16.0）下能编译，真正调用一律包在 if #available(iOS 26.0) 里
import FoundationModels

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
// A-030 / A-033 (2026-05-21): cycleDemoRollState long-press 已删
// memory project_demo_scaffolds_to_remove_before_v1.md #1, #15
// 留空 modifier 保留调用点不报错 — 等接 backend event 驱动后整段删

private struct DemoCardCycleGesture: ViewModifier {
    let app: AppStore

    func body(content: Content) -> some View {
        // production = no-op；demo long-press cycle 已删（A-030 / A-033）
        content
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
        case .warn: return T.warnDeep
        case .ok: return T.okDeep
        case .danger: return T.danger
        case .accent: return T.primary
        }
    }

    private var bg: Color {
        switch tone {
        case .neutral: return T.pill
        case .warn: return T.warnBg
        case .ok: return T.okBg
        case .danger: return T.dangerBg
        case .accent: return Color(hex: 0xE8F4F6)
        }
    }
}

// ───────────────────────────────────────────────────────────
// MARK: - HomeView · greeting + 扣分 card + 3 segmented tab

// ───────────────────────────────────────────────────────────

/// 首页问候日期：JST 今天「yyyy 年 M 月 d 日（曜日）」（ios-home-05：原写死 2026/4/22 演示残留）。
private func homeGreetingDateLabel() -> String {
    let f = DateFormatter()
    f.locale = Locale(identifier: "ja_JP")
    f.timeZone = TimeZone(identifier: "Asia/Tokyo")
    f.dateFormat = "yyyy 年 M 月 d 日（E）"
    return f.string(from: Date())
}

struct HomeView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    // segmented + Tab 已砍 — itsuki 4-30: 通知去右上角，功能集中到一个页面（unread 留给右上角铃铛 badge）

    /// 未读数 — 用 AppStore.allNotifications（包含 push mock）
    private var unread: Int {
        app.unreadNotificationCount
    }

    /// 每 1 秒推进 active 中倒计时的 Timer
    private let countdownTimer = Timer.publish(every: 1, on: .main, in: .common).autoconnect()

    var body: some View {
        // safeAreaInset 现在自动让出 TopRollBar / BottomNav · 不用 placeholder
        ScrollView(showsIndicators: false) {
            VStack(spacing: 0) {
                // §1 Greeting  ——  JSX: padding 14px 20px 6px
                greetingRow
                    .padding(.leading, 20).padding(.trailing, 20)
                    .padding(.top, 14).padding(.bottom, 6)

                // 学年更新「待更新」时顶部横幅 → 点开番号再設定弹窗（spec §4.2）
                if app.needsRenewal {
                    renewBanner
                        .padding(.horizontal, 16)
                        .padding(.top, 6)
                }

                // §2 扣分 amber Card  ——  JSX: padding 12px 16px 6px
                pointsCard
                    .padding(.horizontal, 16)
                    .padding(.top, 12).padding(.bottom, 6)
                    .onReceive(countdownTimer) { _ in
                        app.tickCountdown()
                        app.tickStudyCountdown() // 4-30 學習 demo
                    }

                // §2.5 「下次罚扫」小卡 —— 有未完成罚扫安排时显示，否则整张不渲染
                if let next = app.nextCleaning {
                    nextCleaningCard(next)
                        .padding(.horizontal, 16)
                        .padding(.top, 4).padding(.bottom, 6)
                }

                // §3 LifeTab 内容直显（segmented + 社区 + 通知 tab 砍掉，通知用右上角按钮看）
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
                Text("おかえり、\(app.displayUser.name) さん")
                    .font(.system(size: 20, weight: .bold))
                    .kerning(0.2)
                    .foregroundStyle(T.ink)
                // JSX: fontSize 12 / inkMute / marginTop 3
                Text(homeGreetingDateLabel()) // ios-home-05：原写死「2026 年 4 月 22 日（火）」→ JST 今天
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

    // MARK: 学年更新「待更新」横幅（spec §4.2）

    private var renewBanner: some View {
        Button { app.openSheet(.renewStudentNo) } label: {
            HStack(spacing: 12) {
                Image(systemName: "person.text.rectangle")
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundStyle(T.primary)
                VStack(alignment: .leading, spacing: 2) {
                    Text("アカウント番号の更新が必要です")
                        .font(.system(size: 14, weight: .bold))
                        .foregroundStyle(T.ink)
                    Text("新学年の学年・組・出席番号を設定してください")
                        .font(.system(size: 12))
                        .foregroundStyle(T.inkMute)
                }
                Spacer(minLength: 0)
                Text("更新")
                    .font(.system(size: 13, weight: .bold))
                    .foregroundStyle(.white)
                    .padding(.horizontal, 14).padding(.vertical, 8)
                    .background(Capsule().fill(T.primary))
            }
            .padding(14)
            .background {
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .fill(T.primary.opacity(0.06))
            }
            .overlay {
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(T.primary.opacity(0.3), lineWidth: 1)
            }
        }
        .buttonStyle(.plain)
    }

    // MARK: 扣分 Card（amber · JSX #5c3410 ink）

    //
    // idle 时：大字显示本月减点（4.5点 + progress bar + 迟到/缺席 counts）
    // active/late/done 时：切换到点呼英雄显示（大字「点呼中 · 2:50 / 遅刻 / 時間内」+ 欠席申請 / 体調報告 按钮）
    //                      本月分数退避到右下角小字

    private var pointsCard: some View {
        // JSX ink：#5c3410（深褐）
        let deepBrown = Color(hex: 0x5C3410)
        return ZStack {
            // JSX: radius 22 / padding 20 22 / amber gradient
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .fill(cardGradient)
                .shadow(color: Color(hex: 0xD4A547).opacity(0.24), radius: 20, x: 0, y: 6)

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
                // 夜学習対象学生 + studyState in upcoming/active → study mode 优先
                if app.displayUser.isStudyTarget && (app.studyState == .upcoming || app.studyState == .active) {
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

    // MARK: 「下次罚扫」小卡（amber 卡之外、下方）

    /// 有未完成罚扫安排时显示；点进罚扫履历页。无安排则 body 里整张不渲染。
    private func nextCleaningCard(_ info: NextCleaningInfo) -> some View {
        Button { router.go(.myClean) } label: {
            HStack(spacing: 12) {
                Image(systemName: "sparkles")
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundStyle(Color(hex: 0xB07A28))
                    .frame(width: 38, height: 38)
                    .background(Circle().fill(Color(hex: 0xFDF4E1)))
                VStack(alignment: .leading, spacing: 2) {
                    Text("次の罰則清掃")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundStyle(T.inkSub)
                    Text("\(info.dateText) \(info.timeText) · \(info.area)")
                        .font(.system(size: 14, weight: .bold))
                        .foregroundStyle(T.ink)
                }
                Spacer()
                Ic.chevR(14)
                    .foregroundStyle(T.inkMute)
            }
            .padding(14)
            .background(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .fill(Color.white)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(T.hair, lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }

    /// absent 时显红色渐变，其余情况显 amber
    private var cardGradient: LinearGradient {
        if app.rollState == .absent {
            return LinearGradient(
                stops: [
                    .init(color: Color(hex: 0xFFD6D0), location: 0.0),
                    .init(color: Color(hex: 0xEF6A58), location: 0.55),
                    .init(color: Color(hex: 0xC83B29), location: 1.0),
                ],
                startPoint: .topLeading, endPoint: .bottomTrailing
            )
        }
        return LinearGradient(
            stops: [
                .init(color: Color(hex: 0xFFEFC2), location: 0.0),
                .init(color: Color(hex: 0xF4C677), location: 0.55),
                .init(color: Color(hex: 0xD99F3E), location: 1.0),
            ],
            startPoint: .topLeading, endPoint: .bottomTrailing
        )
    }

    // MARK: study content (4-30 後續 拍板 — ⚠️ DEMO-ONLY · v1.0 删)

    //
    // 夜学習対象学生 + studyState upcoming/active 时 amber Card 显示这套:
    // - 学習迟到倒计时（mm:ss）
    // - 「欠席届」按钮 → 夜学習欠席届提交

    @ViewBuilder
    private func studyContent(deepBrown: Color) -> some View {
        let mm = app.studyCountdownSec / 60
        let ss = app.studyCountdownSec % 60
        let countdownText = String(format: "%02d:%02d", mm, ss)
        let isActive = app.studyState == .active

        VStack(alignment: .leading, spacing: 0) {
            // header row — 标题 + 状态 pill
            HStack(alignment: .top) {
                Text(isActive ? "夜学習中" : "夜学習開始まで")
                    .font(.system(size: 11, weight: .bold))
                    .kerning(1.98)
                    .textCase(.uppercase)
                    .foregroundStyle(deepBrown.opacity(0.8))
                Spacer()
                Text(isActive ? "進行中" : "開始前")
                    .font(.system(size: 11.5, weight: .bold))
                    .kerning(0.22)
                    .padding(.horizontal, 10).padding(.vertical, 3)
                    .foregroundStyle(deepBrown)
                    .background(Capsule().fill(Color.white.opacity(0.45)))
            }
            .padding(.bottom, 6)

            if isActive {
                // active = NFC 2 次签到进度 + 「NFC で签到」入口（system_features §7.3.3）
                studyTapsProgress(deepBrown: deepBrown)
                    .padding(.bottom, 14)
                studyActionButtons(deepBrown: deepBrown)
            } else {
                // upcoming = 倒计时 hero + 请假按钮
                Button { router.go(.applyForm(kind: "studyAbsence")) } label: {
                    VStack(alignment: .leading, spacing: 0) {
                        HStack(alignment: .firstTextBaseline, spacing: 6) {
                            Text(countdownText)
                                .font(.system(size: 56, weight: .heavy, design: .monospaced))
                                .kerning(-1.12)
                                .foregroundStyle(deepBrown)
                        }
                        .padding(.bottom, 12)
                        Text("前半 19:40〜20:40 ／ 後半 20:45〜21:45")
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
                                Text("欠席届")
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

    /// 学习 NFC 2 次签到进度 dot row（仅 active 显示）
    @ViewBuilder
    private func studyTapsProgress(deepBrown: Color) -> some View {
        let taps = app.studyTaps
        let items: [(StudyTap, String, String)] = [
            (.start, "開始", "19:40"),
            (.end, "終了", "21:45"),
        ]
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 0) {
                ForEach(Array(items.enumerated()), id: \.offset) { i, item in
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

    /// active 时的操作 row — 「NFC で签到」+「欠席届」（无下一 tap 时显示「全 2 次完了」）
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
                        Text("NFC でチェックイン")
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
                        Text("欠席届")
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
            // 两次都完成
            HStack(spacing: 8) {
                Image(systemName: "checkmark.seal.fill")
                    .font(.system(size: 16, weight: .semibold))
                Text("本日の夜学習の出席が完了しました")
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

    // MARK: idle content（本月减点 hero）

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
                    Text(app.profileIsPlaceholder ? "—" : String(format: "%.1f", app.displayUser.points))
                        .font(.system(size: 56, weight: .heavy, design: .monospaced))
                        .kerning(-1.12)
                        .foregroundStyle(deepBrown)
                    Text("点")
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundStyle(deepBrown.opacity(0.75))
                }
                .padding(.bottom, 12)

                // ≥8 = 外出禁止（赤）/ 4–7 = 罰則清掃 対象（橙）/ <4 不显示。占位时不显示。
                if !app.profileIsPlaceholder {
                    cleaningFlagRow(deepBrown: deepBrown)
                }

                progressRow(deepBrown: deepBrown)

                HStack {
                    HStack(spacing: 0) {
                        Text("遅刻 ")
                        Text(app.profileIsPlaceholder ? "—" : "\(app.displayUser.lateCount)")
                            .font(.system(size: 12, weight: .bold, design: .monospaced))
                        Text(" 回 · 欠席 ")
                        Text(app.profileIsPlaceholder ? "—" : "\(app.displayUser.absentCount)")
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
        // absent 时卡片整体变红 → 文字改为白色系
        let isAbsent = app.rollState == .absent
        let labelColor: Color = isAbsent ? Color.white.opacity(0.9) : deepBrown.opacity(0.8)
        let valueColor: Color = isAbsent ? .white : deepBrown
        let chevColor: Color = isAbsent ? Color.white.opacity(0.9) : deepBrown.opacity(0.85)

        VStack(alignment: .leading, spacing: 0) {
            // Row 1: 小字显示 本月减点 · 4.5 点 / 详细
            Button { router.go(.myPoints) } label: {
                HStack(spacing: 8) {
                    Text("今月の減点")
                        .font(.system(size: 11, weight: .bold))
                        .kerning(1.98)
                        .textCase(.uppercase)
                        .foregroundStyle(labelColor)
                    Text(app.profileIsPlaceholder ? "—" : String(format: "%.1f 点", app.displayUser.points))
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

            // Row 3: 操作按钮（absent 时单独显示「寮監に連絡」，其余显 欠席申請 + 体調報告）
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

    /// active: 大字「点呼中 · 2:50」倒计时 / late: 红色迟到 / done: 绿色时间内
    @ViewBuilder
    private func heroStatus(deepBrown: Color) -> some View {
        switch app.rollState {
        case .active:
            if app.rollCountdownSec <= 0 {
                heroBlock(
                    caption: "今回の点呼",
                    big: "遅刻",
                    sub: "欠席申請または体調報告で、判定の見直しを申請できます",
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
                    sub: "NFC にタッチしてチェックイン",
                    bigColor: deepBrown,
                    captionColor: deepBrown.opacity(0.7),
                    subColor: deepBrown.opacity(0.8),
                    bigMonospaced: true
                )
            }
        case .absent:
            heroBlock(
                caption: "欠席判定・要連絡",
                big: "欠席",
                sub: "寮監室まで直接お越しください",
                bigColor: .white,
                captionColor: Color.white.opacity(0.9),
                subColor: Color.white.opacity(0.95)
            )
        case .done:
            // R-1②：判定不再写死「時間内」，按后端 my_status 派生的 checkinKind 显（遅刻 → 赤）
            let isLate = app.checkinKind == "遅刻"
            heroBlock(
                // ios-home-07：checkinAt 为 nil（罕见竞态）时不显写死假时刻 21:02，用中性占位
                caption: "\(app.checkinAt ?? "--:--")",
                big: app.checkinKind ?? "時間内",
                sub: "今回の点呼は完了しました",
                bigColor: isLate ? T.danger : Color(hex: 0x2C6048),
                captionColor: deepBrown.opacity(0.7),
                subColor: deepBrown.opacity(0.8)
            )
        case .idle:
            EmptyView()
        }
    }

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

    private func rollActionButton(icon: String, label: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack(spacing: 6) {
                Image(systemName: icon)
                    .font(.system(size: 14, weight: .semibold))
                Text(label)
                    .font(.system(size: 13.5, weight: .semibold))
            }
            .foregroundStyle(Color(hex: 0x5C3410))
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

    /// JSX progress bar: h 8 / radius 4 / bg white.4 / fill 50% amber / 2 threshold marks (4/8)
    private func progressRow(deepBrown: Color) -> some View {
        VStack(alignment: .leading, spacing: 5) {
            GeometryReader { geo in
                let w = geo.size.width
                // 为避免硬编码失真，进度按 points/8 动态算、上限 1
                let pct = min(app.displayUser.points / 8.0, 1.0)

                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 4, style: .continuous)
                        .fill(Color.white.opacity(0.4))
                        .frame(height: 8)

                    RoundedRectangle(cornerRadius: 4, style: .continuous)
                        .fill(
                            LinearGradient(
                                colors: [Color(hex: 0xD99F3E), Color(hex: 0xB07A28)],
                                startPoint: .leading, endPoint: .trailing
                            )
                        )
                        .frame(width: w * pct, height: 8)

                    // threshold 4 点（50% = 4/8）· 罰則清掃
                    Rectangle()
                        .fill(deepBrown.opacity(0.4))
                        .frame(width: 2, height: 12)
                        .offset(x: w * 0.5 - 1, y: 0)
                    // threshold 8 点（100%）· 外出禁止
                    Rectangle()
                        .fill(deepBrown.opacity(0.4))
                        .frame(width: 2, height: 12)
                        .offset(x: w - 2, y: 0)
                }
            }
            .frame(height: 12)

            // fontSize 10 / mono / opacity .7 · "0" "4 · 清掃" "8 · 外出禁止"
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

    /// 减点等级标识行：≥8 外出禁止 / 4–7 罰則清掃 対象 / <4 不显示。
    /// 数据：≥8 用本地 points（点数本地就有）；4–7 优先后端 needsCleaning，本地 pts>=4 兜底。
    @ViewBuilder
    private func cleaningFlagRow(deepBrown _: Color) -> some View {
        let pts = app.displayUser.points
        if pts >= 8 {
            cleaningFlagLabel(icon: "exclamationmark.octagon.fill", text: "外出禁止", tint: T.danger)
                .padding(.bottom, 12)
        } else if app.displayUser.needsCleaning || pts >= 4 {
            cleaningFlagLabel(icon: "sparkles", text: "罰則清掃 対象", tint: Color(hex: 0xB07A28))
                .padding(.bottom, 12)
        }
    }

    private func cleaningFlagLabel(icon: String, text: String, tint: Color) -> some View {
        HStack(spacing: 6) {
            Image(systemName: icon)
                .font(.system(size: 12, weight: .semibold))
            Text(text)
                .font(.system(size: 12.5, weight: .bold))
        }
        .foregroundStyle(tint)
        .padding(.horizontal, 10)
        .padding(.vertical, 5)
        .background(Capsule().fill(Color.white.opacity(0.5)))
    }

    // MARK: 点呼状态 pill 文字/颜色（amber card 右上）

    // 老师点开始点呼前 = 点呼開始前（普通提示）
    // 点呼中 = 剩余 XX:XX 遅刻判定（warn orange）
    // 遅刻（倒计时归零未签到）= 遅刻（danger red）
    // 已签到 = 时间内签到（ok green）

    private var pointsPillText: String {
        switch app.rollState {
        case .idle:
            return "点呼開始前"
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
        case .active: return app.rollCountdownSec <= 0 ? .white : Color(hex: 0x7A4A0E)
        case .absent: return .white
        case .done: return Color(hex: 0x2C6048)
        }
    }

    private var pointsPillBg: Color {
        switch app.rollState {
        case .idle: return Color.white.opacity(0.45)
        case .active: return app.rollCountdownSec <= 0 ? T.danger : Color(hex: 0xFDF4E1)
        case .absent: return T.danger
        case .done: return Color(hex: 0xE3F1EA)
        }
    }
}

// ───────────────────────────────────────────────────────────
// MARK: - LifeTab · bus / package / events / lost

// ───────────────────────────────────────────────────────────

struct LifeTab: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    /// 首页活动卡数据源（M-1 上线缺口）：演示版读 SEED.events / 生产版 .task 拉 EventsAPI 到这里
    @State private var loadedEvents: [EventItem] = []
    /// 首页巴士卡数据源：演示版 BusListMock / 生产版 .task 拉 BusAPI.listRoutes 到这里
    @State private var loadedBusRoutes: [SpecialBusRoute] = []

    /// 下一班巴士信息（从巴士便列表里取「今日且时刻未过」或「最近未来日」的第一班）
    private struct UpcomingBus {
        let route: SpecialBusRoute
        let isToday: Bool
    }

    private static let ymdFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        f.locale = Locale(identifier: "ja_JP")
        f.timeZone = TimeZone(identifier: "Asia/Tokyo")
        return f
    }()

    private static let hmFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "HH:mm"
        f.locale = Locale(identifier: "ja_JP")
        f.timeZone = TimeZone(identifier: "Asia/Tokyo")
        return f
    }()

    private var upcomingBus: UpcomingBus? {
        let now = Date()
        let today = Self.ymdFormatter.string(from: now)
        let nowHM = Self.hmFormatter.string(from: now)

        // 数据源：演示版假数据 / 生产版后端拉到的真巴士便（空 = 未登录/还没拉到/真没班 → 显「予定なし」不喂假）
        #if DEMO
            let source = BusListMock.all
        #else
            let source = loadedBusRoutes
        #endif
        // 只取寮生特別運行便，与点进去的 BusListView 口径一致（它只显示 .dormSpecial）——
        // 否则「下一班」可能算出一班通学便，点进详情却找不到，首页与详情自相矛盾。
        let active = source.filter { !$0.deprecated && $0.kind == .dormSpecial }

        // 今日且时刻未过的第一班（source 已按出发时刻排序）
        if let r = active.first(where: { $0.date == today && $0.scheduleAt > nowHM }) {
            return UpcomingBus(route: r, isToday: true)
        }
        // 最近未来日的第一班
        if let r = active.first(where: { $0.date > today }) {
            return UpcomingBus(route: r, isToday: false)
        }
        return nil
    }

    private var pendingPkg: Int {
        // 演示版：读 SEED 假快递（status 用日语「受取待ち」）
        // 生产版：读 app.packages 真实快递（status 用后端英文「pending」/「notified」= 还没取走）
        #if DEMO
            return SEED.packages.filter { $0.status == "受取待ち" }.count
        #else
            return app.packages.filter { $0.status == "pending" || $0.status == "notified" }.count
        #endif
    }

    var body: some View {
        VStack(spacing: 10) {
            announcementCard
            busCard
            packageCard
            eventsCard
            musicCard
            lostCard
        }
        .task {
            // 公告列表 + 未读数：demo 走 SEED / 生产走后端（两个 load 都已 demo-aware），让公告卡显最新标题 + 红点
            try? await app.loadAnnouncementList()
            await app.loadAnnouncementUnreadCount()
            // 其余卡片：生产拉后端，演示直接读 SEED（不在这拉）
            #if !DEMO
                await app.loadSongs()
                await app.loadLostFound()
                await loadHomeEventsAndBus()
            #endif
        }
    }

    #if !DEMO
        /// 生产版拉首页活动卡 + 巴士卡的真数据（M-1 上线缺口）。
        /// 未登录不拉；拉失败保持空 → 卡片显「0 件」/「无预定」，绝不退回 SEED 假数据让学生误事。
        private func loadHomeEventsAndBus() async {
            guard app.isAuthenticated else { return }
            let today = Self.ymdFormatter.string(from: Date())
            let toYear = (Int(today.prefix(4)) ?? 2026) + 1
            do {
                let raw = try await EventsAPI.listEvents(fromDate: today, toDate: "\(toYear)-12-31")
                loadedEvents = EventMapper.map(raw)
            } catch {
                loadedEvents = []
            }
            do {
                loadedBusRoutes = try BusRouteMapper.map(await BusAPI.listRoutes())
            } catch {
                loadedBusRoutes = []
            }
        }
    #endif

    // MARK: 公告卡「お知らせ」— 主页公告入口（itsuki 6-11 发现 AnnouncementListView 是孤儿页：老师网页发了公告、iOS 学生从任何地方都进不去；本卡补入口）

    private var announcementCard: some View {
        HomeCard(pad: 14, onTap: { router.go(.homeAnnouncements) }) {
            HStack(spacing: 12) {
                ZStack(alignment: .topTrailing) {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(T.primary.opacity(0.07))
                        .frame(width: 44, height: 44)
                        .overlay {
                            Image(systemName: "megaphone.fill")
                                .font(.system(size: 20))
                                .foregroundStyle(T.primary)
                        }
                    if app.announcementUnreadCount > 0 {
                        Text("\(app.announcementUnreadCount)")
                            .font(.system(size: 11, weight: .bold, design: .monospaced))
                            .foregroundStyle(.white)
                            .frame(width: 20, height: 20)
                            .background(Circle().fill(T.danger))
                            .overlay(Circle().stroke(.white, lineWidth: 2))
                            .offset(x: 4, y: -4)
                    }
                }
                VStack(alignment: .leading, spacing: 2) {
                    Text("お知らせ")
                        .font(.system(size: 15, weight: .bold))
                        .foregroundStyle(T.ink)
                    Text(latestAnnouncementSubtitle)
                        .font(.system(size: 12))
                        .foregroundStyle(T.inkSub)
                        .lineLimit(1)
                }
                Spacer(minLength: 0)
                Ic.chevR(16).foregroundStyle(T.inkMute)
            }
        }
    }

    /// 公告卡副标题：有列表显最新一条标题；否则按未读数 / 兜底文案
    private var latestAnnouncementSubtitle: String {
        if let first = app.announcements.first { return first.title }
        if app.announcementUnreadCount > 0 { return "未読 \(app.announcementUnreadCount) 件" }
        return "寮からのお知らせ"
    }

    // MARK: Bus card — JSX: 44×44 primary.12 bg / bus icon / 13 inkSub / 22 mono bold time

    private var busCard: some View {
        // 2026-05-03 itsuki: 跳转目标从 .homeBus（旧 BusView 简陋一覧）改为 .busList（带 filter 的 BusListView）
        // MyPage 入口同时移除，统一从 Home 进
        HomeCard(pad: 14, onTap: { router.go(.busList) }) {
            HStack(spacing: 12) {
                ZStack {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(T.primary.opacity(0.07)) // JSX ${T.primary}12 = ~7% alpha
                        .frame(width: 44, height: 44)
                    Ic.bus(22).foregroundStyle(T.primary)
                }
                VStack(alignment: .leading, spacing: 2) {
                    if let ub = upcomingBus {
                        Text(ub.isToday ? "次のバス便" : "次回運行")
                            .font(.system(size: 13))
                            .foregroundStyle(T.inkSub)
                        HStack(alignment: .firstTextBaseline, spacing: 8) {
                            Text(ub.route.scheduleAt)
                                .font(.system(size: 22, weight: .bold, design: .monospaced))
                                .foregroundStyle(T.ink)
                            if ub.isToday {
                                Text("· \(ub.route.direction)")
                                    .font(.system(size: 12))
                                    .foregroundStyle(T.inkMute)
                                    .lineLimit(1)
                            } else {
                                // "4/29(水) 07:30" 形式
                                let md = String(ub.route.date.dropFirst(5)).replacingOccurrences(of: "-", with: "/")
                                Text("· \(md)(\(ub.route.weekday))")
                                    .font(.system(size: 12))
                                    .foregroundStyle(T.inkMute)
                            }
                        }
                        if !ub.isToday {
                            Text(ub.route.direction)
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
                    // 原写死「本日到着」会让学生误以为都是今天刚到的（实际可能前几天到）。
                    // 这里只拿到未受取件数（pendingPkg），无逐件到达日，故用不绑定日期的中性文案。
                    Text("未受取あり")
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
        // 演示=SEED 假行事 / 生产=后端真行事（首页预览卡，靠 #if DEMO 守卫；空 = 未登录/拉失败 → 显 0 件不喂假）
        #if DEMO
            let events = SEED.events
        #else
            let events = loadedEvents
        #endif
        return HomeCard(pad: 14, onTap: { router.go(.schedule) }) {
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    HStack(spacing: 10) {
                        ZStack {
                            RoundedRectangle(cornerRadius: 10, style: .continuous)
                                .fill(T.accent.opacity(0.13)) // JSX ${T.accent}22 = ~13% alpha
                                .frame(width: 32, height: 32)
                            Ic.calendar(18).foregroundStyle(T.primary)
                        }
                        Text("今週の活動 · \(events.count) 件")
                            .font(.system(size: 14, weight: .bold))
                            .foregroundStyle(T.ink)
                    }
                    Spacer(minLength: 0)
                    Ic.chevR(16).foregroundStyle(T.inkMute)
                }

                VStack(spacing: 0) {
                    ForEach(events.prefix(2), id: \.id) { e in
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
    // 老師 38 条 #37「音楽機能は残す」→ 紫色渐变的 44 图标 + 件数 + 排名第 1 的曲目预览
    // top song = SEED.songs[0]（按投票数排序的 seed）

    private var musicCard: some View {
        // 演示=SEED 假数据 / 生产=后端真数据（首页预览卡，靠 #if DEMO 守卫）
        #if DEMO
            let songCount = SEED.songs.count
            let topLine: String? = SEED.songs.first.map { "\($0.title) · \($0.artist)" }
        #else
            let songCount = app.songRequests.count
            let topLine: String? = app.songRequests.first.map { "\($0.song_title) · \($0.artist ?? "")" }
        #endif
        return HomeCard(pad: 14, onTap: { router.go(.homeMusic) }) {
            HStack(spacing: 12) {
                ZStack {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(
                            LinearGradient(
                                colors: [Color(hex: 0xA78BFA), Color(hex: 0x7C3AED)],
                                startPoint: .topLeading, endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 44, height: 44)
                    Ic.music(22).foregroundStyle(.white)
                }
                VStack(alignment: .leading, spacing: 2) {
                    Text("リクエスト曲 · \(songCount) 件")
                        .font(.system(size: 14, weight: .bold))
                        .foregroundStyle(T.ink)
                    if let line = topLine {
                        Text(line)
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
        // 演示=SEED 假数据 / 生产=后端真数据最新 3 条（首页预览卡，靠 #if DEMO 守卫，归一成 LostDisplay）
        #if DEMO
            let tiles = SEED.lost.prefix(3).map(LostDisplay.init(demo:))
        #else
            let tiles = app.lostFound.prefix(3).map(LostDisplay.init(real:))
        #endif
        return HomeCard(pad: 14, onTap: { router.go(.homeLost) }) {
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
                    ForEach(tiles) { item in
                        lostTile(item)
                    }
                }
            }
        }
    }

    @ViewBuilder
    private func lostTile(_ item: LostDisplay) -> some View {
        let c = Color(hexString: item.colorHex) ?? T.inkFaint
        ZStack(alignment: .bottomLeading) {
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .fill(c.opacity(0.13)) // JSX color+'22' ≈ 13%
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
    // IX-024: 把点呼成功后的延时任务存成可取消的 Task，弹窗消失时取消，关弹窗前确认展示的还是点呼弹窗
    @State private var scanTask: Task<Void, Never>? = nil

    var body: some View {
        GlassSheet(onClose: { cancel() }) {
            ZStack {
                switch step {
                case .idle: idleView
                case .scanning: scanningView
                case .success: successView
                case .fail: failView
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
            // IX-024: 弹窗消失时取消未跑完的延时任务，避免它在用户新开别的弹窗后误关
            scanTask?.cancel()
            scanTask = nil
        }
    }

    // MARK: idle — 扫描准备完毕

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
                Text("① 入口の NFC マークにスマートフォンをかざす")
                Text("② 画面が光ったら完了")
            }
            .font(.system(size: 14))
            .lineSpacing(4)
            .foregroundStyle(T.inkSub)
            .padding(.bottom, 20)

            // JSX idle 専用 warn banner
            // JSX: padding 10 14 / radius 12 / warnBg / warn.40 border / warnDeep 12 / lh 1.5
            // R-1①：文案 + 配色按真实 rollState（受付中=绿 / 时间外=黄），不再写死「時間外」误导
            HStack(alignment: .top, spacing: 6) {
                Text(app.rollState == .active ? "✓" : "⚠")
                    .font(.system(size: 12))
                Text(app.rollState == .active
                    ? "点呼受付中です。下のボタンでチェックインしてください。"
                    : "点呼時間外です。点呼開始まで少々お待ちください。")
                    .font(.system(size: 12))
                    .lineSpacing(2)
            }
            .foregroundStyle(app.rollState == .active ? T.okDeep : T.warnDeep)
            .padding(.horizontal, 14).padding(.vertical, 10)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .fill(app.rollState == .active ? T.okBg : T.warnBg)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .stroke((app.rollState == .active ? T.okDeep : T.warn).opacity(0.25), lineWidth: 1)
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
                    .kerning(0.64) // 0.04em × 16
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

    // MARK: success — 签到完成 · 21:02 · 時間内

    private var successView: some View {
        VStack(spacing: 0) {
            // JSX: 96×96 circle / linear-gradient(135deg, 8bc6a3 → 4a9478) / checkmark 28 · scale 2.4
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color(hex: 0x8BC6A3), Color(hex: 0x4A9478)],
                            startPoint: .topLeading, endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 96, height: 96)
                    .shadow(color: Color(hex: 0x4A9478).opacity(0.3), radius: 16, x: 0, y: 12)
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
            // ios-home-07：nil 兜底用中性占位（原写死假时刻 21:02）
            Text("\(app.checkinAt ?? "--:--") · \(app.checkinKind ?? "時間内")")
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
                            colors: [Color(hex: 0xE88A80), Color(hex: 0xC44848)],
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

            Text("読み取りに失敗しました")
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
        #if DEMO
            // 演示版：原假动作（0.5s 扫描动画 → 假签到 → 2s 自动关），给宿舍管理员演示用
            withAnimation(.easeOut(duration: 0.22)) { step = .scanning }
            // IX-024: 把延时任务存进 scanTask，弹窗消失时 onDisappear 会 cancel 它
            scanTask = Task {
                try? await Task.sleep(nanoseconds: 500_000_000)
                await MainActor.run {
                    guard !Task.isCancelled, app.sheetOpen == .rollcall else { return }
                    app.recordCheckin()
                    withAnimation(.easeOut(duration: 0.22)) { step = .success }
                }
                try? await Task.sleep(nanoseconds: 2_000_000_000)
                await MainActor.run {
                    guard !Task.isCancelled, app.sheetOpen == .rollcall else { return }
                    let at = app.checkinAt ?? "--:--"
                    app.closeSheet()
                    app.showToast("チェックイン完了 · \(at)")
                    step = .idle
                }
            }
        #else
            // 生产版（ios① 上线缺口）：真用 CoreNFC 把学号写进墙上 ST25DV Mailbox（手机不联网，点呼机读走发后端）。
            // 架构反转后手机不再 POST checkin，本地只做物理确认（做法 A）、不等后端结果。
            withAnimation(.easeOut(duration: 0.22)) { step = .scanning }
            let writer = ST25DVWriter()
            scanTask = Task {
                await withTaskCancellationHandler {
                    // codex M-2: 冷启动 token 已恢复但 loadMe 没跑完 → myStudentId 暂时 nil，先补拉一次再判断
                    if app.myStudentId == nil { await app.loadMe() }
                    // codex 二轮 M-1: 取消若发生在 loadMe 等待期间，这里拦住 —— 否则往下会创建 NFC session（已取消却开扫描）
                    guard !Task.isCancelled else { return }
                    guard let sid = app.myStudentId, let uuid = UUID(uuidString: sid) else {
                        await MainActor.run {
                            guard app.sheetOpen == .rollcall else { return }
                            withAnimation(.easeOut(duration: 0.22)) { step = .fail }
                            app.showToast("学生情報の取得に失敗しました")
                        }
                        return
                    }
                    do {
                        try await writer.writeCheckin(studentId: uuid, type: .rollcall)
                        await MainActor.run {
                            guard !Task.isCancelled, app.sheetOpen == .rollcall else { return }
                            // 生产版不本地置 done（伪判定，会被每秒 refreshRollStateFromSessions 覆盖回受付中/欠席）；
                            // 只显「写卡成功」绿勾，点呼状态由后端 my_checked_in_at 驱动。
                            withAnimation(.easeOut(duration: 0.22)) { step = .success }
                        }
                        try? await Task.sleep(nanoseconds: 2_000_000_000)
                        await MainActor.run {
                            guard !Task.isCancelled, app.sheetOpen == .rollcall else { return }
                            app.closeSheet()
                            app.showToast("点呼機に送信しました")
                            step = .idle
                        }
                    } catch ST25DVError.unavailable {
                        await MainActor.run {
                            guard app.sheetOpen == .rollcall else { return }
                            withAnimation(.easeOut(duration: 0.22)) { step = .fail }
                            app.showToast("この端末は NFC 非対応です")
                        }
                    } catch {
                        // codex M-1: catch 也加 guard，用户已关弹窗 / 取消时不再改 step
                        await MainActor.run {
                            guard !Task.isCancelled, app.sheetOpen == .rollcall else { return }
                            withAnimation(.easeOut(duration: 0.22)) { step = .fail }
                        }
                    }
                } onCancel: {
                    // codex M-1: 取消 Swift Task 时也 invalidate NFC session，否则系统 NFC 界面不随弹窗关闭
                    writer.cancel()
                }
            }
        #endif
    }

    private func cancel() {
        // IX-024: 用户主动取消时也取消未跑完的延时任务
        scanTask?.cancel()
        scanTask = nil
        app.closeSheet()
        step = .idle
    }
}

// ───────────────────────────────────────────────────────────
// MARK: - StudyCheckinSheet · 学习 NFC 2 次签到 (system_features §7.3.3)

// ───────────────────────────────────────────────────────────

/// State: idle → scanning（0.5s）→ success（2s auto close）/ fail（retry）
/// 每次打开 sheet 记录 1 次 tap（下次打开时记录下一次 tap）
struct StudyCheckinSheet: View {
    @EnvironmentObject var app: AppStore

    enum Step { case idle, scanning, success, fail }

    @State private var step: Step = .idle
    @State private var pulseOn: Bool = false
    @State private var rotating: Bool = false
    @State private var recordedTap: StudyTap? = nil
    // IX-011: 把扫描后的延时任务存成可取消的 Task，弹窗消失时取消，防止已关掉的打卡仍写进出席记录
    @State private var scanTask: Task<Void, Never>? = nil

    private var nextTap: StudyTap? {
        app.nextStudyTap
    }

    private var stepLabel: String {
        switch nextTap {
        case .start: return "夜学習開始のタップ"
        case .end: return "夜学習終了のタップ"
        case .none: return "本日完了"
        }
    }

    private var stepNumber: Int {
        switch nextTap {
        case .start: return 1
        case .end: return 2
        case .none: return 2
        }
    }

    private var stepTimeWindow: String {
        switch nextTap {
        case .start: return "19:35〜19:40"
        case .end: return "21:40〜21:50"
        case .none: return "—"
        }
    }

    var body: some View {
        GlassSheet(onClose: { cancel() }) {
            ZStack {
                switch step {
                case .idle: idleView
                case .scanning: scanningView
                case .success: successView
                case .fail: failView
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
            // IX-011: 弹窗消失（含用户点背景关闭）时取消未跑完的延时任务，避免已取消的打卡仍写入出席记录
            scanTask?.cancel()
            scanTask = nil
        }
    }

    // MARK: idle

    private var idleView: some View {
        VStack(alignment: .leading, spacing: 0) {
            Text("\(stepNumber) / 2 回目")
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
                Text("① 自習室入口の NFC マークにスマートフォンをかざす")
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
                            colors: [Color(hex: 0x8BC6A3), Color(hex: 0x4A9478)],
                            startPoint: .topLeading, endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 96, height: 96)
                    .shadow(color: Color(hex: 0x4A9478).opacity(0.3), radius: 16, x: 0, y: 12)
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
                Text("次回：\(n.label)（\(n.window)）")
                    .font(.system(size: 13))
                    .foregroundStyle(T.inkSub)
            } else {
                Text("\(Self.fmtNow()) · 本日の夜学習の出席が完了しました")
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
        case .end: return "終了タップ完了"
        case .none: return "完了"
        }
    }

    private var nextTapAfterRecord: (label: String, window: String)? {
        // 记录后若还有下一次 tap 则给出提示
        let after = app.nextStudyTap
        switch after {
        case .start: return ("夜学習開始", "19:35〜19:40")
        case .end: return ("夜学習終了", "21:40〜21:50")
        case .none: return nil
        }
    }

    private var failView: some View {
        VStack(spacing: 0) {
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color(hex: 0xE88A80), Color(hex: 0xC44848)],
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

            Text("読み取りに失敗しました")
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
        #if DEMO
            // 演示版：原假动作（0.5s 扫描 → 假打卡 → 2s 自动关）
            withAnimation(.easeOut(duration: 0.22)) { step = .scanning }
            // IX-011: 把延时任务存进 scanTask，弹窗消失时 onDisappear 会 cancel 它
            scanTask = Task {
                try? await Task.sleep(nanoseconds: 500_000_000)
                await MainActor.run {
                    // IX-011: 跑 recordStudyTap 前先确认任务没被取消、且当前展示的还是本签到弹窗
                    guard !Task.isCancelled, app.sheetOpen == .studyCheckin else { return }
                    recordedTap = app.recordStudyTap()
                    withAnimation(.easeOut(duration: 0.22)) { step = .success }
                }
                try? await Task.sleep(nanoseconds: 2_000_000_000)
                await MainActor.run {
                    guard !Task.isCancelled, app.sheetOpen == .studyCheckin else { return }
                    let label = recordedTap?.label ?? "—"
                    app.closeSheet()
                    if app.nextStudyTap == nil {
                        app.showToast("夜学習出席完了 · 全2回タップ済み")
                    } else {
                        app.showToast("\(label) 完了")
                    }
                    step = .idle
                }
            }
        #else
            // 生产版（ios① 上线缺口）：真用 CoreNFC 把学号写进墙上 ST25DV Mailbox（类型 0x02 学習签到）。
            withAnimation(.easeOut(duration: 0.22)) { step = .scanning }
            let writer = ST25DVWriter()
            scanTask = Task {
                await withTaskCancellationHandler {
                    // codex M-2: 冷启动 token 已恢复但 loadMe 没跑完 → myStudentId 暂时 nil，先补拉一次再判断
                    if app.myStudentId == nil { await app.loadMe() }
                    // codex 二轮 M-1: 取消若发生在 loadMe 等待期间，这里拦住 —— 否则往下会创建 NFC session（已取消却开扫描）
                    guard !Task.isCancelled else { return }
                    guard let sid = app.myStudentId, let uuid = UUID(uuidString: sid) else {
                        await MainActor.run {
                            guard app.sheetOpen == .studyCheckin else { return }
                            withAnimation(.easeOut(duration: 0.22)) { step = .fail }
                            app.showToast("学生情報の取得に失敗しました")
                        }
                        return
                    }
                    do {
                        try await writer.writeCheckin(studentId: uuid, type: .study)
                        await MainActor.run {
                            guard !Task.isCancelled, app.sheetOpen == .studyCheckin else { return }
                            recordedTap = app.recordStudyTap() // 本地物理确认、非权威
                            withAnimation(.easeOut(duration: 0.22)) { step = .success }
                        }
                        try? await Task.sleep(nanoseconds: 2_000_000_000)
                        await MainActor.run {
                            guard !Task.isCancelled, app.sheetOpen == .studyCheckin else { return }
                            app.closeSheet()
                            app.showToast("点呼機に送信しました")
                            step = .idle
                        }
                    } catch ST25DVError.unavailable {
                        await MainActor.run {
                            guard app.sheetOpen == .studyCheckin else { return }
                            withAnimation(.easeOut(duration: 0.22)) { step = .fail }
                            app.showToast("この端末は NFC 非対応です")
                        }
                    } catch {
                        // codex M-1: catch 也加 guard，用户已关弹窗 / 取消时不再改 step
                        await MainActor.run {
                            guard !Task.isCancelled, app.sheetOpen == .studyCheckin else { return }
                            withAnimation(.easeOut(duration: 0.22)) { step = .fail }
                        }
                    }
                } onCancel: {
                    // codex M-1: 取消 Swift Task 时也 invalidate NFC session
                    writer.cancel()
                }
            }
        #endif
    }

    private func cancel() {
        // IX-011: 用户主动取消时也取消未跑完的延时任务
        scanTask?.cancel()
        scanTask = nil
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
        case .start: return "夜学習開始"
        case .end: return "夜学習終了"
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
        .init(id: "health", icon: "🤒",
              label: "体調問題を報告",
              detail: "発熱・頭痛・その他の症状を先生に通知",
              kind: .health),
        .init(id: "absence", icon: "📝",
              label: "今回の欠席を申請",
              detail: "今回の点呼を欠席する理由を入力",
              kind: .absence),
        .init(id: "other", icon: "💬",
              label: "その他の問題",
              detail: "遅刻理由・外出中・NFC 不具合など",
              kind: .other),
    ]

    var body: some View {
        GlassSheet(onClose: { app.closeSheet() }) {
            VStack(alignment: .leading, spacing: 0) {
                // JSX: 20 800 / marginBottom 6
                Text("報告・連絡を送る")
                    .font(.system(size: 20, weight: .heavy))
                    .foregroundStyle(T.ink)
                    .padding(.bottom, 6)

                // JSX: 13 inkSub / marginBottom 18
                Text("どの種類の報告を送りますか？")
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
    @State private var submitting = false

    /// JSX options
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
                        TField(text: $temp, placeholder: "体温（℃）", keyboard: .decimalPad)
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

                    PrimaryButton(title: submitting ? "送信中…" : "提出",
                                  enabled: !sym.isEmpty && !submitting)
                    {
                        submit()
                    }
                    .padding(.top, 2)
                }
                .padding(.top, 8)
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .frame(maxHeight: 560)
        }
    }

    /// 体调上报提交 —— 演示版假 toast / 生产版 POST /rollcall/reports（kind=health）。
    private func submit() {
        #if DEMO
            app.closeSheet()
            app.showToast("先生に通知しました")
        #else
            // 把「症状」「体温」「補足」三栏内容拼成后端 body 自由文本（后两栏任意，空则省略）。
            var lines = ["症状：\(sym)"]
            let t = temp.trimmingCharacters(in: .whitespaces)
            if !t.isEmpty { lines.append("体温：\(t)℃") }
            let n = note.trimmingCharacters(in: .whitespacesAndNewlines)
            if !n.isEmpty { lines.append("補足：\(n)") }
            let bodyText = lines.joined(separator: "\n")
            let tokenAtStart = app.authToken
            submitting = true
            Task {
                do {
                    _ = try await RollCallReportsAPI.create(kind: "health", body: bodyText)
                    guard app.authToken == tokenAtStart else { return } // 切账号 / 登出后不在新会话弹 toast
                    app.closeSheet()
                    app.showToast("先生に通知しました")
                } catch {
                    submitting = false // 失败留在弹窗让学生重试
                    app.showToast("送信に失敗しました")
                }
            }
        #endif
    }

    /// JSX Radio option chip · selected: primary outline + pill tint
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
    @State private var submitting = false

    var body: some View {
        GlassSheet(onClose: { app.closeSheet() }) {
            VStack(alignment: .leading, spacing: 18) {
                Text("今回の点呼を欠席する")
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
                    title: submitting ? "送信中…" : "提出",
                    enabled: !reason.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                        && !submitting
                ) {
                    submit()
                }
                .padding(.top, 2)
            }
            .padding(.top, 8)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    /// 当次欠席上报提交 —— 演示版假 toast / 生产版 POST /rollcall/reports（kind=absence）。
    private func submit() {
        #if DEMO
            app.closeSheet()
            app.showToast("審査中です")
        #else
            let bodyText = reason.trimmingCharacters(in: .whitespacesAndNewlines)
            let tokenAtStart = app.authToken
            submitting = true
            Task {
                do {
                    _ = try await RollCallReportsAPI.create(kind: "absence", body: bodyText)
                    guard app.authToken == tokenAtStart else { return } // 切账号 / 登出后不在新会话弹 toast
                    app.closeSheet()
                    app.showToast("審査中です")
                } catch {
                    submitting = false // 失败留在弹窗让学生重试
                    app.showToast("送信に失敗しました")
                }
            }
        #endif
    }
}

// ───────────────────────────────────────────────────────────
// MARK: - OtherSheet · 分類 + 内容

// ───────────────────────────────────────────────────────────

struct OtherSheet: View {
    @EnvironmentObject var app: AppStore

    @State private var cat: String = ""
    @State private var content: String = ""
    @State private var submitting = false

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
                    title: submitting ? "送信中…" : "提出",
                    enabled: !cat.isEmpty &&
                        !content.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                        && !submitting
                ) {
                    submit()
                }
                .padding(.top, 2)
            }
            .padding(.top, 8)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    /// 其他问题上报提交 —— 演示版假 toast / 生产版 POST /rollcall/reports（kind=other）。
    private func submit() {
        #if DEMO
            app.closeSheet()
            app.showToast("送信しました")
        #else
            // 把「分類」「内容」拼成后端 body 自由文本。
            let c = content.trimmingCharacters(in: .whitespacesAndNewlines)
            let bodyText = "分類：\(cat)\n内容：\(c)"
            let tokenAtStart = app.authToken
            submitting = true
            Task {
                do {
                    _ = try await RollCallReportsAPI.create(kind: "other", body: bodyText)
                    guard app.authToken == tokenAtStart else { return } // 切账号 / 登出后不在新会话弹 toast
                    app.closeSheet()
                    app.showToast("送信しました")
                } catch {
                    submitting = false // 失败留在弹窗让学生重试
                    app.showToast("送信に失敗しました")
                }
            }
        #endif
    }

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
// MARK: - RenewStudentNoSheet · 番号再設定（学年更新 / 学生自设番号，spec §4.2）

// ───────────────────────────────────────────────────────────

/// 学年更新时学生自设新番号 —— 选 学年 / 组 / 出席番号 → 提交。
/// 撞号后端返 422 → 原样弹日语提示。成功后 AppStore 清 needsRenewal、顶部按钮消失。
struct RenewStudentNoSheet: View {
    @EnvironmentObject var app: AppStore

    @State private var gradeCode: String = ""
    @State private var classCode: String = ""
    @State private var seatInput: String = ""
    @State private var submitting = false

    /// 学年：中高一貫 6 年制（01→中1 … 06→高3）
    private let grades: [(code: String, label: String)] = [
        ("01", "中1"), ("02", "中2"), ("03", "中3"),
        ("04", "高1"), ("05", "高2"), ("06", "高3"),
    ]
    /// 组：A→01 / B→02
    private let classes: [(code: String, label: String)] = [
        ("01", "A組"), ("02", "B組"),
    ]

    private var seatNo: Int? {
        Int(seatInput)
    }

    private var canSubmit: Bool {
        !gradeCode.isEmpty && !classCode.isEmpty
            && (seatNo.map { $0 >= 1 && $0 <= 99 } ?? false)
            && !submitting
    }

    var body: some View {
        GlassSheet(onClose: { app.closeSheet() }) {
            VStack(alignment: .leading, spacing: 18) {
                Text("アカウント番号の再設定")
                    .font(.system(size: 20, weight: .heavy))
                    .foregroundStyle(T.ink)

                Text("新学年の学年・組・出席番号を選んでください。アカウント番号は自動で計算されます。")
                    .font(.system(size: 13))
                    .foregroundStyle(T.inkSub)

                fieldLabel("学年")
                FlowLayout(spacing: 8) {
                    ForEach(grades, id: \.code) { g in
                        radioChip(title: g.label, selected: gradeCode == g.code) {
                            gradeCode = g.code
                        }
                    }
                }

                fieldLabel("組")
                FlowLayout(spacing: 8) {
                    ForEach(classes, id: \.code) { c in
                        radioChip(title: c.label, selected: classCode == c.code) {
                            classCode = c.code
                        }
                    }
                }

                fieldLabel("出席番号")
                TField(text: $seatInput, placeholder: "例: 18", keyboard: .numberPad)
                    .onChangeCompat(of: seatInput) {
                        // 只留数字、最多 2 桁
                        let digits = seatInput.filter { $0.isNumber }
                        seatInput = String(digits.prefix(2))
                    }

                // 实时预览新学号（3 段齐了才显示）
                if !gradeCode.isEmpty, !classCode.isEmpty,
                   let s = seatNo, s >= 1, s <= 99
                {
                    Text("新しいアカウント番号: \(gradeCode)\(classCode)\(String(format: "%02d", s))")
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundStyle(T.primary)
                }

                PrimaryButton(
                    title: submitting ? "送信中…" : "更新する",
                    enabled: canSubmit
                ) {
                    submit()
                }
                .padding(.top, 2)
            }
            .padding(.top, 8)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private func fieldLabel(_ text: String) -> some View {
        HStack(spacing: 4) {
            Text(text)
                .font(.system(size: 13, weight: .semibold))
                .foregroundStyle(T.inkSub)
            Text("*").foregroundStyle(T.danger)
        }
    }

    private func submit() {
        guard let s = seatNo else { return }
        submitting = true
        let seat = String(format: "%02d", s)
        Task {
            do {
                try await app.submitRenewStudentNo(
                    gradeCode: gradeCode, classCode: classCode, seatNo: seat
                )
                app.closeSheet() // 成功 toast 已在 submitRenewStudentNo 内显示
            } catch is CancellationError {
                // 提交在途登出 / 切用户 → 静默中止
            } catch {
                // 撞号(422)「已有人设定」/ 网络错 → 弹后端日语提示，留在弹窗让学生改
                submitting = false
                app.showToast(APIErrorPresenter.userMessage(for: error, fallback: "アカウント番号の設定に失敗しました"))
            }
        }
    }

    private func radioChip(
        title: String, selected: Bool, onTap: @escaping () -> Void
    ) -> some View {
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

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache _: inout ()) -> CGSize {
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

    func placeSubviews(in bounds: CGRect, proposal _: ProposedViewSize, subviews: Subviews, cache _: inout ()) {
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

// ═══════════════════════════════════════════════════════════════════════════════
// MARK: - 老师公告（2026-05-04 加，spec system_features.md §7.15）

// ═══════════════════════════════════════════════════════════════════════════════
//
// 视图（v1.0 最小可工作版）：
//   - AnnouncementListView: GET /announcements 列表（新→旧、scope 已 backend 过滤）
//   - AnnouncementDetailView: GET /announcements/:id 详情 + 回复 + 发回复
//
// 后送（v1.1）：
//   - HomeView 顶部嵌 AnnouncementCard（最新 1 件 + 红点 N，§7.15.3）
//   - AI 要約 (Foundation Models, iOS 26)、翻译 (Translation, iOS 17.4+)
//   - push 通知

// MARK: - 列表 view

struct AnnouncementListView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var isLoading: Bool = false
    @State private var loadError: String? = nil

    var body: some View {
        VStack(spacing: 0) {
            // 顶部 header (返回 + 标题)
            HStack(spacing: 12) {
                Button {
                    router.back()
                } label: {
                    Image(systemName: "chevron.left")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundStyle(T.ink)
                        .frame(width: 36, height: 36)
                }
                Text("お知らせ")
                    .font(.system(size: 20, weight: .bold))
                    .foregroundStyle(T.ink)
                Spacer()
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)

            if isLoading {
                ProgressView().padding(.top, 60)
                Spacer()
            } else if let err = loadError {
                Text(err)
                    .font(.system(size: 14))
                    .foregroundStyle(.red)
                    .padding(.top, 40)
                    .padding(.horizontal, 24)
                Spacer()
            } else if app.announcements.isEmpty {
                VStack(spacing: 12) {
                    Image(systemName: "bell.slash")
                        .font(.system(size: 48))
                        .foregroundStyle(T.inkMute)
                    Text("お知らせはありません")
                        .font(.system(size: 14))
                        .foregroundStyle(T.inkSub)
                }
                .padding(.top, 80)
                Spacer()
            } else {
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(app.announcements) { ann in
                            AnnouncementListCard(ann: ann)
                                .onTapGesture {
                                    router.go(.homeAnnouncementDetail(id: ann.id.uuidString))
                                }
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.top, 4)
                    .padding(.bottom, 24)
                }
            }
        }
        .background(T.paper.ignoresSafeArea())
        .task { await reload() }
    }

    private func reload() async {
        isLoading = true
        loadError = nil
        do {
            try await app.loadAnnouncementList()
        } catch {
            loadError = "通信エラーが発生しました"
        }
        isLoading = false
    }
}

/// 列表 1 行 card — 标题 / 摘要 / 老师名 / 时刻 / 已读 dot / 回复数
private struct AnnouncementListCard: View {
    let ann: AnnouncementBrief

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            // 已读状态 dot — 未读时蓝色实心
            Circle()
                .fill(ann.isRead ? Color.clear : T.primary)
                .frame(width: 8, height: 8)
                .padding(.top, 6)

            VStack(alignment: .leading, spacing: 4) {
                Text(ann.title)
                    .font(.system(size: 15, weight: ann.isRead ? .regular : .semibold))
                    .foregroundStyle(T.ink)
                    .lineLimit(2)

                Text(ann.bodySummary)
                    .font(.system(size: 13))
                    .foregroundStyle(T.inkSub)
                    .lineLimit(2)

                HStack(spacing: 8) {
                    Text(ann.authorTeacherName)
                        .font(.system(size: 11))
                        .foregroundStyle(T.inkMute)
                    Text("·")
                        .font(.system(size: 11))
                        .foregroundStyle(T.inkMute)
                    Text(formatRelative(ann.createdAt))
                        .font(.system(size: 11))
                        .foregroundStyle(T.inkMute)
                    if ann.replyCount > 0 {
                        Spacer()
                        HStack(spacing: 3) {
                            Image(systemName: "bubble.left")
                                .font(.system(size: 10))
                            Text("\(ann.replyCount)")
                                .font(.system(size: 11, weight: .medium))
                        }
                        .foregroundStyle(T.inkSub)
                    }
                }
                .padding(.top, 2)
            }
        }
        .padding(.vertical, 12)
        .padding(.horizontal, 14)
        .background {
            RoundedRectangle(cornerRadius: 14).fill(T.paper)
        }
        .overlay {
            RoundedRectangle(cornerRadius: 14).stroke(T.hair, lineWidth: 1)
        }
    }

    /// "X 分前 / X 時間前 / MM/dd" 简化日期格式（UI 字符串日语保留）
    private func formatRelative(_ date: Date) -> String {
        let now = Date()
        let diff = Int(now.timeIntervalSince(date))
        if diff < 60 { return "たった今" }
        if diff < 3600 { return "\(diff / 60) 分前" }
        if diff < 86400 { return "\(diff / 3600) 時間前" }
        let f = DateFormatter()
        f.dateFormat = "MM/dd"
        f.timeZone = TimeZone(identifier: "Asia/Tokyo")
        return f.string(from: date)
    }
}

// MARK: - 详情 view

// ═══════════════════════════════════════════════════════════════════════════════
// MARK: - 公告 AI 助手（翻訳 / AI 要約）

// ═══════════════════════════════════════════════════════════════════════════════
//
// 两个能力分别走 Apple 的两套系统框架，机种门槛不同：
//   - 翻訳   : Translation 框架（iOS 17.4+，全机种、设备端、免费、不联网）→ .translationPresentation 弹系统浮层
//   - AI 要約: FoundationModels 框架（iOS 26+ 且 Apple Intelligence 机种）→ 直接调本地 3B 模型生成要点
// 留学生看不懂日文公告时一键翻成母语 / 公告太长时一键提炼要点 —— 都在设备本地跑，不上传任何内容。

/// 公告翻译支持的语言 — 宿舍留学生的主要母语（英 / 中 / 泰 / 越）。
/// rawValue = 翻译目标语言代码（BCP-47 标准），存进 UserDefaults（手机本地小仓库）当「默认翻译语言」用的也是这个字符串。
enum TranslateLang: String, CaseIterable, Identifiable {
    case english = "en"
    case chinese = "zh-Hans" // 简体中文
    case thai = "th"
    case vietnamese = "vi"

    var id: String {
        rawValue
    }

    /// 语言选择窗里显示的名字 — 母语原文拼写（让用户一眼找到自己的语言）+ 日语括注。
    var pickerLabel: String {
        switch self {
        case .english: return "English（英語）"
        case .chinese: return "简体中文（中国語）"
        case .thai: return "ไทย（タイ語）"
        case .vietnamese: return "Tiếng Việt（ベトナム語）"
        }
    }

    /// 翻译完成状态条 / 设置页里显示的短名字。
    var shortLabel: String {
        switch self {
        case .english: return "English"
        case .chinese: return "简体中文"
        case .thai: return "ไทย"
        case .vietnamese: return "Tiếng Việt"
        }
    }
}

/// 一次翻译请求 —— id 每次新建都不同。父视图拿它当 SwiftUI 的 `.id`，
/// 换语言 / 重新翻译时让隐藏执行器整个重建、重新触发翻译。不含 iOS 18 专属类型，能直接放进父视图状态里。
struct TranslateRequest: Identifiable, Equatable {
    let id = UUID()
    let code: String // 目标语言代码 = TranslateLang.rawValue
}

/// 只负责「执行翻译」的隐藏子视图（iOS 18.0+）。
/// `TranslationSession.Configuration` / `.translationTask` 是 iOS 18.0 才存在的类型，
/// 直接写在父视图本体（部署目标 16.0）里会因类型解析报编译错 → 隔离到这里。
/// 父视图侧用 `.id("<语言>-<次数>")` 贴换、把这个子视图整个重建，靠 `.task` 触发翻译。
@available(iOS 18.0, *)
private struct AnnouncementTranslateRunner: View {
    let text: String
    let targetCode: String
    // 用 @Binding（值类型 String?/Bool 都是 Sendable）回写结果，而不是传回调闭包：
    // 回调闭包是非 Sendable，会把 translationTask 的 action 整个推断成 MainActor 隔离，
    // 进而让 session 变「main actor-isolated」、再调 nonisolated 的 translate 触发 Swift 6 数据竞争报错。
    // 只捕获 Sendable 值后，action 保持 nonisolated，session 干净；结果回写统一切到 MainActor.run。
    @Binding var translatedText: String?
    @Binding var isTranslating: Bool
    @Binding var failed: Bool

    @State private var config: TranslationSession.Configuration?

    var body: some View {
        // 把 binding 取成局部 let，让 translationTask 闭包只捕获这几个局部值、不捕获 self。
        // translationTask 的 action 是 nonisolated 非 @Sendable，闭包一旦捕获 self（@MainActor 视图）
        // 就被推断成 MainActor 隔离，session 随之变「main actor-isolated」→ 调 nonisolated 的 translate 报数据竞争。
        let resultBinding = $translatedText
        let loadingBinding = $isTranslating
        let failBinding = $failed
        let body = text
        return Color.clear
            .frame(height: 0)
            .translationTask(config) { session in
                let translated = try? await session.translate(body).targetText
                await MainActor.run {
                    if let translated {
                        resultBinding.wrappedValue = translated
                    } else {
                        failBinding.wrappedValue = true
                    }
                    loadingBinding.wrappedValue = false
                }
            }
            .task {
                // source: nil = 自动判定原文语言（公告是日语）。target = 用户选的母语。
                config = TranslationSession.Configuration(
                    source: nil,
                    target: Locale.Language(identifier: targetCode)
                )
            }
    }
}

/// FoundationModels 调用封装 — 全部成员标 @available(iOS 26.0)，只在 if #available 分支里碰
enum AnnouncementAI {
    /// 当前机种 + 系统 + Apple Intelligence 状态是否允许用本地模型（决定「AI 要約」按钮显不显示）
    @available(iOS 26.0, *)
    static var isSummarizeAvailable: Bool {
        if case .available = SystemLanguageModel.default.availability { return true }
        return false
    }

    /// 把公告正文交给设备端模型，返回日文要点总结
    @available(iOS 26.0, *)
    static func summarize(_ text: String) async throws -> String {
        let session = LanguageModelSession {
            "あなたは寮のお知らせを要約するアシスタントです。本文の重要な点を、3 つまでの短い箇条書きで、日本語で簡潔にまとめてください。余計な前置きは書かないでください。"
        }
        let response = try await session.respond(to: text)
        return response.content
    }
}

struct AnnouncementDetailView: View {
    let id: String
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var isLoading: Bool = false
    @State private var loadError: String? = nil
    @State private var replyText: String = ""
    @State private var isPosting: Bool = false

    // 公告 AI 操作状态（翻訳 / 要約）
    // ── 翻訳（原地把正文翻成母语）──
    @State private var translateReq: TranslateRequest? = nil // 非 nil = 当前要翻成哪个语言（喂给隐藏执行器 AnnouncementTranslateRunner）
    @State private var translatedText: String? = nil // 译文（nil = 显示原文）
    @State private var translatedLabel: String? = nil // 译文语言短名（状态条用，如「简体中文」）
    @State private var isTranslating: Bool = false // 翻译进行中 loading
    @State private var translateFailed: Bool = false // 翻译失败标记
    @State private var showLangPicker: Bool = false // 语言选择窗开关
    @State private var rememberAsDefault: Bool = false // 语言选择窗里「以后默认翻成这个语言」勾选状态（临时，确认后才写入 AppStorage）
    /// 默认翻译语言代码（空串 = 没设默认、每次翻译都先弹语言选择窗）。跟设置页 MySettingsView 同一个 key、改一边另一边即时生效。
    @AppStorage("translate_default_lang") private var defaultTranslateLang: String = ""
    // ── AI 要約 ──
    @State private var showSummary: Bool = false // 要約结果 sheet 开关
    @State private var summaryText: String? = nil // 要約结果文字（nil = 还没出）
    @State private var isSummarizing: Bool = false // 要約生成中 loading
    @State private var summaryError: String? = nil // 要約失败提示

    private var detail: AnnouncementDetail? {
        app.announcementDetails[id]
    }

    var body: some View {
        VStack(spacing: 0) {
            // header
            HStack(spacing: 12) {
                Button {
                    router.back()
                } label: {
                    Image(systemName: "chevron.left")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundStyle(T.ink)
                        .frame(width: 36, height: 36)
                }
                Text("お知らせ詳細")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundStyle(T.ink)
                Spacer()
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)

            if isLoading && detail == nil {
                ProgressView().padding(.top, 60)
                Spacer()
            } else if let err = loadError {
                Text(err)
                    .font(.system(size: 14))
                    .foregroundStyle(.red)
                    .padding(.top, 40)
                    .padding(.horizontal, 24)
                Spacer()
            } else if let d = detail {
                ScrollView {
                    VStack(alignment: .leading, spacing: 16) {
                        // 标题 + 元信息
                        VStack(alignment: .leading, spacing: 6) {
                            Text(d.title)
                                .font(.system(size: 20, weight: .bold))
                                .foregroundStyle(T.ink)
                            HStack(spacing: 8) {
                                Text(d.authorTeacherName)
                                    .font(.system(size: 12))
                                    .foregroundStyle(T.inkSub)
                                Text("·").foregroundStyle(T.inkMute)
                                Text(formatFull(d.createdAt))
                                    .font(.system(size: 12))
                                    .foregroundStyle(T.inkMute)
                            }
                        }

                        // 正文 —— 翻译完成后原地显示译文，否则显示原文
                        Text(translatedText ?? d.body)
                            .font(.system(size: 14))
                            .foregroundStyle(T.ink)
                            .lineSpacing(4)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .textSelection(.enabled) // 可选中复制

                        // 翻译状态条（翻译中 loading / 失败重试 / 已翻译可切回原文）
                        translateStatusBar

                        // AI 操作行：翻訳（iOS 18+）+ AI 要約（iOS 26+ 且 Apple Intelligence 機種）
                        announcementAIRow(body: d.body)

                        // 隐藏执行器：translateReq 非 nil 时真正跑翻译（iOS 18 专属类型隔离在子视图里）。
                        // req.id 换了就重建 → 重新触发翻译，支持换语言 / 重试。
                        if #available(iOS 18.0, *), let req = translateReq {
                            AnnouncementTranslateRunner(
                                text: d.body,
                                targetCode: req.code,
                                translatedText: $translatedText,
                                isTranslating: $isTranslating,
                                failed: $translateFailed
                            )
                            .id(req.id)
                        }

                        Divider().padding(.vertical, 4)

                        // 回复列表（旧→新，Slack 风）
                        Text("返信 (\(d.replies.count))")
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundStyle(T.inkSub)

                        if d.replies.isEmpty {
                            Text("まだ返信はありません")
                                .font(.system(size: 12))
                                .foregroundStyle(T.inkMute)
                                .padding(.vertical, 8)
                        } else {
                            ForEach(d.replies) { r in
                                AnnouncementReplyRow(reply: r)
                            }
                        }
                    }
                    .padding(.horizontal, 20)
                    .padding(.vertical, 16)
                }
                // 翻訳浮层（点「翻訳」弹）+ AI 要約结果弹窗（点「AI 要約」弹）
                .sheet(isPresented: $showLangPicker) {
                    langPickerSheet
                }
                .sheet(isPresented: $showSummary) {
                    summarySheet
                }

                // 回复输入框
                HStack(spacing: 8) {
                    TextField("返信を入力…", text: $replyText, axis: .vertical)
                        .lineLimit(1 ... 4)
                        .font(.system(size: 14))
                        .padding(.horizontal, 12)
                        .padding(.vertical, 10)
                        .background {
                            RoundedRectangle(cornerRadius: 18).fill(T.paper)
                        }
                        .overlay {
                            RoundedRectangle(cornerRadius: 18).stroke(T.hair, lineWidth: 1)
                        }

                    Button {
                        sendReply()
                    } label: {
                        Image(systemName: isPosting ? "ellipsis" : "paperplane.fill")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundStyle(.white)
                            .frame(width: 40, height: 40)
                            .background {
                                Circle().fill(canSend ? T.primary : T.inkMute)
                            }
                    }
                    .disabled(!canSend || isPosting)
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
                .background(T.paper)
            } else {
                Spacer()
            }
        }
        .background(T.paper.ignoresSafeArea())
        .task { await loadDetail() }
    }

    private var canSend: Bool {
        !replyText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    /// ── AI 操作行（翻訳 / AI 要約）──────────────────────────────
    /// 翻訳 = iOS 18+ 显示（程序化翻译接口门槛）；AI 要約 = 仅 iOS 26+ 且 Apple Intelligence 机种显示（否则整颗按钮不出现）
    private func announcementAIRow(body: String) -> some View {
        HStack(spacing: 10) {
            if #available(iOS 18.0, *) {
                Button {
                    onTapTranslate()
                } label: {
                    aiActionChip(icon: "globe", title: "翻訳")
                }
                .buttonStyle(.plain)
            }

            if #available(iOS 26.0, *) {
                if AnnouncementAI.isSummarizeAvailable {
                    Button {
                        startSummarize(body)
                    } label: {
                        aiActionChip(icon: "sparkles", title: "AI 要約")
                    }
                    .buttonStyle(.plain)
                }
            }

            Spacer()
        }
    }

    private func aiActionChip(icon: String, title: String) -> some View {
        HStack(spacing: 5) {
            Image(systemName: icon).font(.system(size: 12, weight: .semibold))
            Text(title).font(.system(size: 12.5, weight: .semibold))
        }
        .foregroundStyle(T.primary)
        .padding(.horizontal, 12)
        .padding(.vertical, 7)
        .background { Capsule().fill(T.primary.opacity(0.08)) }
    }

    /// 翻译状态条 —— 正文下方那行：翻译中转圈 / 失败可重试 / 已翻译可切回原文（没翻译时整行不出现）
    @ViewBuilder
    private var translateStatusBar: some View {
        if isTranslating {
            HStack(spacing: 8) {
                ProgressView().controlSize(.small)
                Text("翻訳中…")
                    .font(.system(size: 12))
                    .foregroundStyle(T.inkSub)
                Spacer()
            }
        } else if translateFailed {
            HStack(spacing: 8) {
                Image(systemName: "exclamationmark.triangle")
                    .font(.system(size: 12, weight: .semibold))
                Text("翻訳に失敗しました")
                    .font(.system(size: 12))
                Spacer()
                Button {
                    if let req = translateReq { retryTranslate(req.code) }
                } label: {
                    Text("再試行").font(.system(size: 12, weight: .semibold))
                }
                .buttonStyle(.plain)
            }
            .foregroundStyle(.red)
        } else if let label = translatedLabel, translatedText != nil {
            HStack(spacing: 8) {
                Image(systemName: "globe").font(.system(size: 11, weight: .semibold))
                Text("\(label) に翻訳しました")
                    .font(.system(size: 12, weight: .medium))
                Spacer()
                Button {
                    resetToOriginal()
                } label: {
                    Text("原文に戻す").font(.system(size: 12, weight: .semibold))
                }
                .buttonStyle(.plain)
            }
            .foregroundStyle(T.primary)
        }
    }

    /// 点「翻訳」：有默认语言就直接翻，没设默认就弹语言选择窗
    private func onTapTranslate() {
        if !defaultTranslateLang.isEmpty, let lang = TranslateLang(rawValue: defaultTranslateLang) {
            startTranslate(lang)
        } else {
            rememberAsDefault = false
            showLangPicker = true
        }
    }

    /// 真正发起翻译：清掉旧译文、亮 loading、塞一个新请求给隐藏执行器（执行器靠 req.id 重建触发）
    private func startTranslate(_ lang: TranslateLang) {
        translatedText = nil
        translateFailed = false
        isTranslating = true
        translatedLabel = lang.shortLabel
        translateReq = TranslateRequest(code: lang.rawValue)
    }

    /// 语言选择窗里点某语言：勾了「以后默认」就写进 UserDefaults，然后翻译
    private func pickLang(_ lang: TranslateLang) {
        if rememberAsDefault {
            defaultTranslateLang = lang.rawValue
        }
        showLangPicker = false
        startTranslate(lang)
    }

    /// 失败后重试当前语言
    private func retryTranslate(_ code: String) {
        guard let lang = TranslateLang(rawValue: code) else { return }
        startTranslate(lang)
    }

    /// 切回原文：清掉译文 + 请求
    private func resetToOriginal() {
        translatedText = nil
        translatedLabel = nil
        translateFailed = false
        isTranslating = false
        translateReq = nil
    }

    /// 语言选择窗 —— 点「翻訳」且没设默认语言时弹出。4 个语言行 + 一个「以后默认翻成这个语言」勾选
    private var langPickerSheet: some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack {
                HStack(spacing: 6) {
                    Image(systemName: "globe").font(.system(size: 15, weight: .semibold))
                    Text("翻訳する言語").font(.system(size: 16, weight: .bold))
                }
                .foregroundStyle(T.primary)
                Spacer()
                Button { showLangPicker = false } label: {
                    Image(systemName: "xmark")
                        .font(.system(size: 14, weight: .bold))
                        .foregroundStyle(T.inkMute)
                        .frame(width: 32, height: 32)
                }
                .buttonStyle(.plain)
            }
            .padding(.horizontal, 20)
            .padding(.top, 18)
            .padding(.bottom, 8)

            VStack(spacing: 0) {
                ForEach(Array(TranslateLang.allCases.enumerated()), id: \.element.id) { idx, lang in
                    if idx > 0 { Divider().background(T.hair) }
                    Button {
                        pickLang(lang)
                    } label: {
                        HStack {
                            Text(lang.pickerLabel)
                                .font(.system(size: 15))
                                .foregroundStyle(T.ink)
                            Spacer()
                            Image(systemName: "chevron.right")
                                .font(.system(size: 12, weight: .semibold))
                                .foregroundStyle(T.inkMute)
                        }
                        .padding(.horizontal, 20)
                        .padding(.vertical, 14)
                        .contentShape(Rectangle())
                    }
                    .buttonStyle(.plain)
                }
            }

            Button {
                rememberAsDefault.toggle()
            } label: {
                HStack(spacing: 10) {
                    Image(systemName: rememberAsDefault ? "checkmark.square.fill" : "square")
                        .font(.system(size: 18))
                        .foregroundStyle(rememberAsDefault ? T.primary : T.inkMute)
                    Text("次回からこの言語に翻訳する")
                        .font(.system(size: 13))
                        .foregroundStyle(T.ink)
                    Spacer()
                }
                .padding(.horizontal, 20)
                .padding(.top, 8)
                .padding(.vertical, 14)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)

            Text("デフォルトの言語は設定画面でいつでも変更できます。")
                .font(.system(size: 11))
                .foregroundStyle(T.inkMute)
                .padding(.horizontal, 20)
                .padding(.bottom, 16)
        }
        .presentationDetents([.medium])
        .presentationDragIndicator(.visible)
    }

    /// 点「AI 要約」→ 弹 sheet + 调设备端模型生成要点（只在 iOS 26+ 调，签名标 @available）
    @available(iOS 26.0, *)
    private func startSummarize(_ text: String) {
        showSummary = true
        summaryText = nil
        summaryError = nil
        isSummarizing = true
        Task {
            do {
                summaryText = try await AnnouncementAI.summarize(text)
            } catch {
                summaryError = "要約の生成に失敗しました。もう一度お試しください。"
            }
            isSummarizing = false
        }
    }

    /// AI 要約结果弹窗（内容是纯文字展示，不碰 iOS 26 专属 API，所以不用标 @available）
    private var summarySheet: some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack {
                HStack(spacing: 6) {
                    Image(systemName: "sparkles").font(.system(size: 15, weight: .semibold))
                    Text("AI 要約").font(.system(size: 16, weight: .bold))
                }
                .foregroundStyle(T.primary)
                Spacer()
                Button { showSummary = false } label: {
                    Image(systemName: "xmark")
                        .font(.system(size: 14, weight: .bold))
                        .foregroundStyle(T.inkMute)
                        .frame(width: 32, height: 32)
                }
                .buttonStyle(.plain)
            }
            .padding(.horizontal, 20)
            .padding(.top, 18)
            .padding(.bottom, 12)

            Divider()

            ScrollView {
                if isSummarizing {
                    HStack(spacing: 10) {
                        ProgressView()
                        Text("要約を生成中…")
                            .font(.system(size: 14))
                            .foregroundStyle(T.inkSub)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.top, 40)
                } else if let err = summaryError {
                    Text(err)
                        .font(.system(size: 14))
                        .foregroundStyle(.red)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.top, 24)
                        .padding(.horizontal, 20)
                } else if let s = summaryText {
                    Text(s)
                        .font(.system(size: 14))
                        .foregroundStyle(T.ink)
                        .lineSpacing(5)
                        .textSelection(.enabled)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(20)
                }
            }

            Text("※ この要約は端末内の Apple Intelligence で生成されています。内容は送信されません。")
                .font(.system(size: 10.5))
                .foregroundStyle(T.inkMute)
                .padding(.horizontal, 20)
                .padding(.bottom, 16)
        }
        .presentationDetents([.medium])
        .presentationDragIndicator(.visible)
    }

    private func loadDetail() async {
        isLoading = true
        loadError = nil
        do {
            try await app.loadAnnouncementDetail(id: id)
        } catch {
            loadError = "通信エラーが発生しました"
        }
        isLoading = false
    }

    private func sendReply() {
        let body = replyText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !body.isEmpty, !isPosting else { return }
        isPosting = true
        Task {
            do {
                try await app.postAnnouncementReply(announcementId: id, body: body)
                replyText = ""
            } catch {
                // 失败时保留输入内容、用户可重试；提示用户没发出去（ios-home-10：原静默吞、用户以为发成功）
                app.showToast("送信に失敗しました。もう一度お試しください")
            }
            isPosting = false
        }
    }

    private func formatFull(_ date: Date) -> String {
        let f = DateFormatter()
        f.dateFormat = "yyyy/MM/dd HH:mm"
        f.timeZone = TimeZone(identifier: "Asia/Tokyo")
        return f.string(from: date)
    }
}

private struct AnnouncementReplyRow: View {
    let reply: AnnouncementReplyOut

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(spacing: 6) {
                Text(reply.authorName)
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundStyle(reply.authorKind == "teacher" ? T.primary : T.ink)
                if reply.authorKind == "teacher" {
                    Text("教員")
                        .font(.system(size: 9, weight: .bold))
                        .foregroundStyle(.white)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background {
                            Capsule().fill(T.primary)
                        }
                }
                Spacer()
                Text(formatTime(reply.createdAt))
                    .font(.system(size: 11))
                    .foregroundStyle(T.inkMute)
            }
            Text(reply.body)
                .font(.system(size: 13))
                .foregroundStyle(T.ink)
                .lineSpacing(3)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding(.vertical, 8)
        .padding(.horizontal, 12)
        .background {
            RoundedRectangle(cornerRadius: 10).fill(T.paper.opacity(0.6))
        }
    }

    private func formatTime(_ date: Date) -> String {
        let f = DateFormatter()
        f.dateFormat = "HH:mm"
        f.timeZone = TimeZone(identifier: "Asia/Tokyo")
        return f.string(from: date)
    }
}
