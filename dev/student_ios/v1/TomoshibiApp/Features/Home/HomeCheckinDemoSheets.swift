// HomeCheckinDemoSheets.swift
// Features · Home — 演示版（DEMO scheme）専用的两个自制签到弹窗：点呼 / 夜学習
//
// ⭐ 为什么整个文件包在 #if DEMO 里（2026-07-29 itsuki 真机实测后拍板「一按就扫」）：
//   生产版签到已经不再经过这两个弹窗 —— 首页按钮按下去就直接开 CoreNFC，成功 / 失败全部由
//   苹果自己的 NFC 系统面板显示（见 Foundation/Network/NFC/NFCCheckinLauncher.swift）。
//   原流程要按两次（先弹自制弹窗，再点弹窗里的「NFC をかざす」），而且苹果面板还会盖在自制弹窗上，
//   两层界面重叠 = 多余。生产版删干净；演示版留着 —— 演示机 / 模拟器没有真 NFC 可碰，
//   给宿舍管理员看流程只能靠这套假动画。
//
// 原位置 = HomeStubs.swift（本次整块搬出；除删掉「生产版分支」外内容未改）。

import SwiftUI

#if DEMO
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

        // MARK: idle — 扫描准备界面（仅演示版）

        private var idleView: some View {
            scanIdle
        }

        // MARK: scanIdle — 扫描准备完毕（「NFC をかざす」按钮入口）

        private var scanIdle: some View {
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
                // ios#49：点呼时间外禁用主按钮，避免走完整写入却被当成已点呼
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
                .disabled(app.rollState != .active)
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

                Text("書き込みに失敗しました")
                    .font(.system(size: 22, weight: .bold))
                    .foregroundStyle(T.ink)
                    .padding(.bottom, 10)

                // ios#45：架构已从「读 NFC」改为「写 ST25DV」，失败文案跟进；副标题给操作指引不重复标题（jp-reviewer）
                Text("もう一度カードをかざしてください")
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
            // 演示版假动作（0.5s 扫描动画 → 假签到 → 2s 自动关），给宿舍管理员演示用。
            // 生产版不走这里 —— 首页点呼按钮直接开 CoreNFC（NFCCheckinLauncher）。
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

                Text("書き込みに失敗しました")
                    .font(.system(size: 22, weight: .bold))
                    .foregroundStyle(T.ink)
                    .padding(.bottom, 10)

                // ios#45：架构已从「读 NFC」改为「写 ST25DV」，失败文案跟进；副标题给操作指引不重复标题（jp-reviewer）
                Text("もう一度カードをかざしてください")
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
            // 演示版假动作（0.5s 扫描 → 假打卡 → 2s 自动关），给宿舍管理员演示用。
            // 生产版不走这里 —— 首页夜学習按钮直接开 CoreNFC（NFCCheckinLauncher）。
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
            f.timeZone = TimeZone(identifier: "Asia/Tokyo")
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
    // MARK: - Previews

    // ───────────────────────────────────────────────────────────

    #Preview("RollcallSheet") {
        ZStack {
            T.pearl.ignoresSafeArea()
            RollcallSheet()
        }
        .environmentObject(AppStore())
    }

#endif
