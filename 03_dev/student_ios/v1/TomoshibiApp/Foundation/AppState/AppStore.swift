// AppStore.swift
// ⭐ Foundation · 全局 app state（对等 phaseB_src AppProvider）

import Foundation
import Combine
import SwiftUI

/// アカウント関連フィールドの変更履歴（MyInfo 編集時に append）
struct ChangeLogEntry: Hashable, Identifiable {
    let id: UUID
    let at: Date          // 変更時刻
    let field: String     // 例: "grade" / "room"
    let label: String     // 日本語表示: "学年" / "部屋番号"
    let before: String
    let after: String

    init(field: String, label: String, before: String, after: String) {
        self.id = UUID()
        self.at = Date()
        self.field = field
        self.label = label
        self.before = before
        self.after = after
    }
}

@MainActor
final class AppStore: ObservableObject {
    /// 点呼状态
    @Published var rollState: RollState = .idle

    /// 当前 overlay sheet（nil = 无 sheet）
    @Published var sheetOpen: SheetKind? = nil

    /// 长按返回 breadcrumb popup 开关
    @Published var breadcrumbOpen: Bool = false

    /// Toast 文本（nil = 不显示）· 2.2 秒自动清
    @Published var toast: String? = nil

    /// 暗色模式 toggle（MySettings 控制）
    @AppStorage("isDark") var isDark: Bool = false

    /// 点呼倒计时（active 时，秒数）· Demo 期初始 180 秒
    @Published var rollCountdownSec: Int = 180

    /// 已签到时刻（done 时用）
    @Published var checkinAt: String? = nil

    /// 已签到判定（"時間内" / "遅刻"）
    @Published var checkinKind: String? = nil

    /// アカウント関連の変更履歴（MyInfo 編集フロー）
    @Published var changeLog: [ChangeLogEntry] = [
        // demo seed: 過去の進級記録（例示用）
        ChangeLogEntry(field: "grade", label: "学年", before: "高2", after: "高3"),
    ]

    /// 変更を記録（field ごと · before == after ならスキップ）
    func appendChange(field: String, label: String, before: String, after: String) {
        guard before != after else { return }
        changeLog.insert(
            ChangeLogEntry(field: field, label: label, before: before, after: after),
            at: 0
        )
    }

    // MARK: - Toast 辅助

    func showToast(_ text: String) {
        withAnimation { toast = text }
        Task {
            try? await Task.sleep(nanoseconds: 2_200_000_000)
            await MainActor.run {
                withAnimation { self.toast = nil }
            }
        }
    }

    // MARK: - Sheet 辅助

    func openSheet(_ kind: SheetKind) {
        withAnimation(.spring(response: 0.34, dampingFraction: 0.82)) {
            sheetOpen = kind
        }
    }

    func closeSheet() {
        withAnimation(.spring(response: 0.34, dampingFraction: 0.82)) {
            sheetOpen = nil
        }
    }

    // MARK: - 点呼成功模拟（Demo 用）

    /// done 表示を自動で idle に戻すタスク（重複を防ぐため保持）
    private var autoDismissDoneTask: Task<Void, Never>?

    func simulateCheckin() {
        let fmt = DateFormatter()
        fmt.dateFormat = "HH:mm"
        checkinAt = fmt.string(from: Date())
        checkinKind = "時間内"
        rollState = .done

        // 5 秒後に自動で idle に戻す（緑のバー / 完了表示を自然消滅）
        autoDismissDoneTask?.cancel()
        autoDismissDoneTask = Task { [weak self] in
            try? await Task.sleep(nanoseconds: 5_000_000_000)
            guard !Task.isCancelled else { return }
            await MainActor.run {
                guard let self else { return }
                // done のままの時だけ戻す（手動で他の状態に切り替えられてたら触らない）
                if self.rollState == .done {
                    withAnimation(.easeInOut(duration: 0.4)) {
                        self.rollState = .idle
                        self.rollCountdownSec = 180
                        self.checkinAt = nil
                        self.checkinKind = nil
                    }
                }
            }
        }
    }

    // MARK: - Demo 用：点呼カードを長押しで状態を循環
    //
    // idle（平常） → active 180s（点呼開始・残り時間表示）
    //            → active 10s  （遅刻直前）
    //            → active 0s   （遅刻判定）
    //            → done         （時間内にチェックイン完了）
    //            → idle に戻る
    //
    // デモ時は Home の点数カードを長押しするだけで 5 態を見せられる。
    func cycleDemoRollState() {
        switch rollState {
        case .idle:
            rollState = .active
            rollCountdownSec = 180
            checkinAt = nil
            checkinKind = nil
            showToast("Demo · 点呼開始（残り 3:00）")
        case .active where rollCountdownSec > 15:
            rollCountdownSec = 10
            showToast("Demo · 遅刻直前（残り 0:10）")
        case .active where rollCountdownSec > 0:
            rollCountdownSec = 0
            showToast("Demo · 遅刻判定")
        case .active:
            // countdown == 0 → 欠席判定（長時間未チェックイン）
            rollState = .absent
            showToast("Demo · 欠席判定（寮監へ連絡）")
        case .absent:
            // 欠席 → 時間内扱いで演出（例：寮監が手動で救済）
            simulateCheckin()
            showToast("Demo · 時間内にチェックイン")
        case .done:
            autoDismissDoneTask?.cancel()
            rollState = .idle
            rollCountdownSec = 180
            checkinAt = nil
            checkinKind = nil
            showToast("Demo · 通常状態に戻る")
        }
    }

    /// active 中に 1 秒ごと呼ばれる（HomeView の Timer から）
    func tickCountdown() {
        guard rollState == .active, rollCountdownSec > 0 else { return }
        rollCountdownSec -= 1
    }

    // MARK: - 学習（晚自习）状态机 — 2026-04-30 後續 itsuki 拍板
    //
    // ⚠️ DEMO-ONLY: amber Card 三态切换机制（system_features §7.3.8）
    // v1.0 上线前必删，改为后端 event 驱动。
    // memory project_demo_scaffolds_to_remove_before_v1.md #15

    /// 学習开始 10 分前 → upcoming（amber Card 显示倒计时）/ 进行中 → active / 当晚已结束 → done
    @Published var studyState: StudyState = .idle        // 平常打开 = idle (原扣分点显示)。long press amber Card 切到 upcoming 演示学習

    /// 学習迟到倒计时（upcoming 时秒数）— demo init 600s = 10 分
    @Published var studyCountdownSec: Int = 600

    /// 当月学習请假次数（> 3 → 弹提醒文案）
    @Published var studyLeaveCountThisMonth: Int = 3   // demo seed = 3 让 itsuki 提交一次就触发提醒

    /// upcoming 时 1 秒一次 tick（HomeView Timer 同时触发 roll + study）
    func tickStudyCountdown() {
        guard studyState == .upcoming, studyCountdownSec > 0 else { return }
        studyCountdownSec -= 1
    }

    /// 学習欠席届 提交（system_features §7.3.5）— 提交后 += 1，> 3 触发文案 A
    func submitStudyLeave(reason: String, range: StudyLeaveRange) {
        studyLeaveCountThisMonth += 1
        if studyLeaveCountThisMonth > 3 {
            // itsuki 4-30 拍板 文案 A
            showToast("今月、もう \(studyLeaveCountThisMonth) 回お休みされていますね。体調管理、お気をつけて。")
        } else {
            showToast("学習欠席届を提出しました")
        }
    }

    /// long press study card 切换 demo 状态（roll 同模式）
    func cycleDemoStudyState() {
        switch studyState {
        case .idle:     studyState = .upcoming; studyCountdownSec = 600; showToast("Demo · 学習 10 分前 (倒计时 10:00)")
        case .upcoming: studyState = .active; showToast("Demo · 学習進行中")
        case .active:   studyState = .done; showToast("Demo · 学習終了")
        case .done:     studyState = .idle; showToast("Demo · 学習対象外")
        }
    }
}

// MARK: - 学習状态 + 请假范围 (4-30 後續 拍板)

enum StudyState: String {
    case idle       // 平常 (非学習时段)
    case upcoming   // 学習开始 10 分前 → amber Card 显示倒计时
    case active     // 学習进行中
    case done       // 当晚学習已结束
}

enum StudyLeaveRange: String, CaseIterable {
    case first      // 前半節 19:40-20:40
    case second     // 後半節 20:45-21:45
    case both       // 両方

    var label: String {
        switch self {
        case .first:  return "前半節（19:40〜20:40）"
        case .second: return "後半節（20:45〜21:45）"
        case .both:   return "両方"
        }
    }
}
