// TopRollBar.swift · 全 App 持续顶部点呼状态 bar
// 3 态: idle (日常) / active (点呼中倒计时) / done (已签到)
// ⭐ Foundation · 对等 phaseB_src TopRollBar

import SwiftUI

struct TopRollBar: View {
    @EnvironmentObject var app: AppStore

    var body: some View {
        HStack(spacing: 10) {
            icon
            VStack(alignment: .leading, spacing: 2) {
                Text(primaryText)
                    .font(.system(size: 12, weight: .semibold))
                Text(secondaryText)
                    .font(.system(size: 10))
                    .foregroundStyle(.secondary)
            }
            Spacer()
            if app.rollState != .done {
                Ic.chevR().opacity(0.5)
            }
        }
        .padding(.horizontal, 14).padding(.vertical, 10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .foregroundStyle(fg)
        .background {
            background
        }
        .clipShape(Capsule(style: .continuous))
        .contentShape(Capsule())
        .onTapGesture {
            if app.rollState != .done {
                app.openSheet(.feedback)
            }
        }
    }

    @ViewBuilder
    private var icon: some View {
        switch app.rollState {
        case .idle:
            Image(systemName: "clock")
                .foregroundStyle(T.primary)
        case .active:
            Image(systemName: "dot.circle.fill")
                .foregroundStyle(T.danger)
                .pulseIfAvailable()
        case .absent:
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundStyle(.white)
        case .done:
            Image(systemName: "checkmark.circle.fill")
                .foregroundStyle(T.ok)
        }
    }

    private var primaryText: String {
        switch app.rollState {
        // idle 时 RootView（RootView.swift:20 的 `app.rollState != .idle`）不挂载本 bar，
        // 故 .idle 分支永不显示，仅为 switch 穷尽性占位。不写死「次の点呼 21:00」避免误导
        // 维护者以为下次点呼固定 21:00（点呼时刻由后端 schedule 决定）。
        case .idle: return ""
        case .active:
            // 時間内受付段：countdownSec > 0 → 显「几点之后算遅刻」的钟点（跟首页卡片同口径，不让学生心算）；
            //   钟点取不到时回退成原来的「あと N 分 M 秒」。
            // 遅刻受付段：countdownSec == 0 但仍 active → 已进遅刻宽限，催尽快签到（ios#88）
            if app.rollCountdownSec > 0 {
                if let deadline = app.rollOnTimeDeadlineText {
                    return "点呼中 · \(deadline) を過ぎると遅刻"
                }
                let m = app.rollCountdownSec / 60
                let s = app.rollCountdownSec % 60
                return String(format: "点呼中 · 遅刻まであと %d分%02d秒", m, s)
            } else {
                return "遅刻受付中・早めにチェックインを"
            }
        case .absent:
            return "欠席になりました · 寮監まで直接ご連絡ください"
        case .done:
            // 契约收口：exempt_range→done+无时刻 是新可达态；「チェックイン済み」只留给真签到(present/late)
            switch app.checkinKind {
            case "時間内", "遅刻":
                return "チェックイン済み \(app.checkinAt ?? "") · \(app.checkinKind ?? "")"
            case "免除":
                return "点呼免除 · 本日は点呼対象外です"
            default:
                return "点呼記録を確認しました"
            }
        }
    }

    private var secondaryText: String {
        switch app.rollState {
        // 同 primaryText：idle 时本 bar 不挂载，.idle 分支仅为穷尽性占位、不会显示。
        case .idle: return "タップで体調報告・欠席届"
        case .active: return "タップで欠席届・体調報告"
        case .absent: return "寮監室までお越しください"
        case .done: return "お疲れさまでした"
        }
    }

    private var fg: Color {
        switch app.rollState {
        case .idle: return T.ink
        case .active: return T.warnDeep
        case .absent: return .white
        case .done: return T.okDeep
        }
    }

    @ViewBuilder
    private var background: some View {
        switch app.rollState {
        case .idle:
            if #available(iOS 26.0, *) {
                Color.clear.glassEffect(.regular, in: .capsule)
            } else {
                T.glassBar
            }
        case .active: T.warnBg
        case .absent: T.danger
        case .done: T.okBg
        }
    }
}

/// .symbolEffect(.pulse) 脉冲动画 iOS 17+ 才有；iOS 16 退化成无动画（最低支持 iOS 16 编译兼容）
private extension View {
    @ViewBuilder
    func pulseIfAvailable() -> some View {
        if #available(iOS 17.0, *) {
            symbolEffect(.pulse)
        } else {
            self
        }
    }
}
