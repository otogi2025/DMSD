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
        case .upcoming: studyState = .active; studyTaps = []; showToast("Demo · 学習進行中（NFC で 3 回タップ）")
        case .active:   studyState = .done; showToast("Demo · 学習終了")
        case .done:     studyState = .idle; studyTaps = []; showToast("Demo · 学習対象外")
        }
    }

    // MARK: - 学習 NFC 3 回タップ签到 (system_features §7.3.3-6) — 2026-04-30 後續

    /// 学習出席で達成した tap の集合（3 種類: start / mid / end）
    @Published var studyTaps: Set<StudyTap> = []

    /// 現在の学習出席状態（studyTaps + studyState から導出）
    var studyAttendance: StudyAttendance {
        // start / mid / end 集合に応じて state を判定（§7.3.6 異常テーブル）
        let s = studyTaps.contains(.start)
        let m = studyTaps.contains(.mid)
        let e = studyTaps.contains(.end)
        // 学習未開始 → idle
        if studyState == .idle || studyState == .upcoming { return .idle }
        // 全 3 回 tap → 緑（時間内）
        if s && m && e { return .green }
        // 1 + 3 だけ / 2 + 3 だけ / 1 + 2 だけ → ⚠️ 異常
        if (s && !m && e) || (!s && m && e) || (s && m && !e) { return .abnormal }
        // 1 だけ → まだ進行中（途中の通常）
        if s && !m && !e { return .progressing }
        // 2 + 3 のみ（開始未碰）→ 遅刻 + 異常（§7.3.6 4 行目に近い）
        if !s && m && !e { return .progressing }
        if !s && !m && e { return .abnormal }
        // 何もしてない / done なのに何もない → 缺席 (§7.3.6 1 行目)
        if studyState == .done && !s && !m && !e { return .red }
        // active で何もしてない = 進行中だがまだ tap 0
        return .none
    }

    /// 何回目の tap を期待しているか（next tap）— UI で次のステップを案内
    var nextStudyTap: StudyTap? {
        if !studyTaps.contains(.start) { return .start }
        if !studyTaps.contains(.mid)   { return .mid }
        if !studyTaps.contains(.end)   { return .end }
        return nil
    }

    /// NFC 1 回 tap を記録（重複は無視）— sheet flow から呼ぶ
    /// - Returns: 記録した tap 種別（既に全部 tap 済なら nil）
    @discardableResult
    func recordStudyTap() -> StudyTap? {
        guard let next = nextStudyTap else { return nil }
        studyTaps.insert(next)
        // 履歴 1 件追加（最新が先頭）
        let label: String = {
            switch next {
            case .start: return "学習開始"
            case .mid:   return "中場確認"
            case .end:   return "学習終了"
            }
        }()
        let entry = StudyHistoryEntry(
            date: Self.todayJa(),
            tapKind: next,
            tapLabel: label,
            timeHM: Self.nowHM(),
            note: nil
        )
        studyHistory.insert(entry, at: 0)
        return next
    }

    /// マイページ「学習履歴」用 — 過去 N 日分の出席 entry 列
    @Published var studyHistory: [StudyHistoryEntry] = StudyHistoryEntry.demoSeed

    // MARK: - リクエスト曲 通報・封禁 (system_features §7.11.2) — 2026-05-01 拍板

    /// 各曲の通報件数（songId → count）。一覧の老師側 badge は 7 件以上で出る。
    @Published var songReportCounts: [Int: Int] = [:]

    /// 自分が投稿した曲への通報合計（badge 7 判定用 + 自動封禁判定用）
    @Published var myReportTotal: Int = 0

    /// 自分の投稿封禁レベル（0=制限なし / 1=1ヶ月 / 2=3ヶ月 / 3=永久）
    @Published var songBanLevel: Int = 0

    /// 投稿封禁解除時刻（nil = 制限なし、level=3 は遠い未来扱いで実質 nil で許す）
    @Published var songBanUntil: Date? = nil

    /// 投稿可能か — banLevel + banUntil 判定
    var canPostSong: Bool {
        if songBanLevel == 0 { return true }
        if songBanLevel >= 3 { return false }   // 永久禁止
        guard let until = songBanUntil else { return true }
        return Date() >= until
    }

    /// 封禁状態の表示文字列 (MusicNewView で表示)
    var songBanDescription: String? {
        guard !canPostSong else { return nil }
        if songBanLevel >= 3 { return "投稿は永久に停止されています。" }
        if let until = songBanUntil {
            let f = DateFormatter()
            f.dateFormat = "M月d日"
            f.locale = Locale(identifier: "ja_JP")
            return "現在投稿停止中（\(f.string(from: until)) まで）"
        }
        return "現在投稿停止中"
    }

    /// 通報を 1 件記録（demo: 全件自分宛にカウントして自動封禁を体感できるようにする）
    /// 実装時は backend が songId → 投稿者 をルックアップして本人にだけ加算する。
    func reportSong(songId: Int, reason: SongReportReason, freeText: String?) {
        songReportCounts[songId, default: 0] += 1
        // demo: 投稿者の本人累計にも加算（実 prod は songs.posted_by_id を見る）
        myReportTotal += 1
        // 5 件超で次の段階へ自動エスカレーション
        let prevLevel = songBanLevel
        if myReportTotal >= 15 {
            songBanLevel = 3
            songBanUntil = nil
        } else if myReportTotal >= 10 {
            songBanLevel = 2
            songBanUntil = Calendar.current.date(byAdding: .month, value: 3, to: Date())
        } else if myReportTotal >= 5 {
            songBanLevel = 1
            songBanUntil = Calendar.current.date(byAdding: .month, value: 1, to: Date())
        }
        if songBanLevel != prevLevel {
            switch songBanLevel {
            case 1: showToast("通報多数のため、1 ヶ月間投稿停止になりました。")
            case 2: showToast("通報多数のため、3 ヶ月間投稿停止になりました。")
            case 3: showToast("通報多数のため、永久に投稿停止になりました。")
            default: break
            }
        } else {
            showToast("通報を送信しました。")
        }
    }

    /// demo 用 reset (マイページ 設定から呼ぶ想定 — 今回は未配線)
    func resetSongBan() {
        songBanLevel = 0
        songBanUntil = nil
        myReportTotal = 0
        songReportCounts = [:]
    }

    private static func nowHM() -> String {
        let f = DateFormatter()
        f.dateFormat = "HH:mm"
        f.locale = Locale(identifier: "ja_JP")
        return f.string(from: Date())
    }

    private static func todayJa() -> String {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        f.locale = Locale(identifier: "ja_JP")
        return f.string(from: Date())
    }

    // MARK: - ログインロック升级 (CLAUDE.md §App 账号规则 + 4-22 拍板の 5 段階)
    //
    // 失敗回数 → ロック期間: 1=30秒 / 2=1分 / 3=5分 / 4=30分 / 5=1時間 / 6+=永久
    // 永久ロックは寮監に連絡して解除。次回ログイン成功で counter リセット。

    /// ログイン失敗累計 (永久ロックは 6 以上)
    @Published var loginFailCount: Int = 0

    /// ロック期間 (failCount に対応する秒数 — 6+ は nil = 永久)
    static let lockoutDurations: [Int] = [30, 60, 300, 1800, 3600]

    /// 現在のロック段階の秒数 (永久 → nil)
    var currentLockoutSeconds: Int? {
        let idx = loginFailCount - 1
        guard idx >= 0 else { return nil }
        if idx < Self.lockoutDurations.count {
            return Self.lockoutDurations[idx]
        }
        return nil   // 永久
    }

    /// 現在のロック段階の表示文字列
    var currentLockoutLabel: String {
        switch loginFailCount {
        case 1:  return "30 秒"
        case 2:  return "1 分"
        case 3:  return "5 分"
        case 4:  return "30 分"
        case 5:  return "1 時間"
        default: return "永久"
        }
    }

    /// 次の段階の表示文字列 (後段が無いなら nil)
    var nextLockoutLabel: String? {
        switch loginFailCount {
        case 1: return "1 分"
        case 2: return "5 分"
        case 3: return "30 分"
        case 4: return "1 時間"
        case 5: return "永久"
        default: return nil
        }
    }

    /// ログイン失敗時に呼ぶ — failCount += 1
    func recordLoginFailure() {
        loginFailCount += 1
    }

    /// ログイン成功時 / ロック明け で呼ぶ — counter reset
    func resetLoginFailures() {
        loginFailCount = 0
    }

    // MARK: - Push 通知 mock (system_features §7.13 R1 例外)
    //
    // 真后端没接通,iOS push listener 用本地模拟:
    // demo 用 settings 里点按钮 → simulatePush(...) → 给 pushNotifications 头部 insert 一条
    // + 弹 toast banner。NotificationsView 显示 pushNotifications + SEED.notifications 合并。

    /// demo 期间动态加进来的通知（push 接收的）— SEED.notifications 是静态默认
    @Published var pushNotifications: [NotificationItem] = []

    /// 通知中心显示用 — push 在前 + SEED.notifications
    var allNotifications: [NotificationItem] {
        pushNotifications + SEED.notifications
    }

    /// 未读数（home greetingRow bell badge 用）
    var unreadNotificationCount: Int {
        allNotifications.filter { $0.unread }.count
    }

    /// 模拟接收一条 push 通知
    /// - Parameters:
    ///   - type: NotificationItem.type 字段（"申請" / "減点" / "学習" / "リクエスト曲" 等）
    ///   - title: 标题
    ///   - body: 正文
    func simulatePush(type: String, title: String, body: String) {
        // 生成新 ID（避免和 SEED 冲突）
        let nextId = (pushNotifications.map(\.id).max() ?? 999) + 1
        let item = NotificationItem(
            id: nextId,
            type: type,
            title: title,
            time: "今",
            body: body,
            unread: true
        )
        pushNotifications.insert(item, at: 0)
        showToast("📣 \(title)")
    }

    // 4 个 demo 触发器（system_features §7.13 R1 例外里列出的事件）

    /// 学習欠席届 承認された
    func simulateStudyLeaveApproved() {
        simulatePush(
            type: "学習",
            title: "学習欠席届が承認されました",
            body: "本日の前半節について、学習担当の先生から承認されました。"
        )
    }

    /// 学習欠席届 不承認
    func simulateStudyLeaveRejected() {
        simulatePush(
            type: "学習",
            title: "学習欠席届が不承認でした",
            body: "本日の前半節は出席をお願いします。詳細は学習担当の先生にお尋ねください。"
        )
    }

    /// 学習対象 名单加入
    func simulateStudyRosterAdded() {
        simulatePush(
            type: "学習",
            title: "学習対象になりました",
            body: "今日から晩自習の対象に追加されました。19:40 までに学習室へお越しください。"
        )
    }

    /// 出寮届 修改届 chain 再批通过
    func simulateAmendmentRebatch() {
        simulatePush(
            type: "申請",
            title: "外泊届（修改届）が承認されました",
            body: "修改届の内容で寮務課長まで承認が進みました。残り 1 名の承認をお待ちください。"
        )
    }
}

// MARK: - 学習 NFC 出席（system_features §7.3.3-6）

enum StudyTap: String, Hashable, CaseIterable {
    case start      // 19:35 ～ 19:40 学習開始
    case mid        // 20:45 ± 中場
    case end        // 21:45 学習終了
}

/// 出席状態（amber Card / マイページ で表示）
enum StudyAttendance: String {
    case idle           // 学習時間外
    case none           // active だが 0 tap
    case progressing    // 1 tap 済（通常進行中）
    case green          // 全 3 tap 済 = 時間内
    case yellow         // 遅刻
    case red            // 缺席
    case abnormal       // 不一致 = ⚠️ 異常 老師手動判
    case excused        // 欠席承認済
}

// MARK: - 通報理由 (system_features §7.11.2)

enum SongReportReason: String, CaseIterable, Hashable {
    case noisy      // うるさい
    case taste      // 曲調が好みでない / 不快
    case lyrics     // 歌詞が不適切
    case other      // その他（自由記入）

    var label: String {
        switch self {
        case .noisy:  return "うるさい"
        case .taste:  return "曲調が好みでない / 不快"
        case .lyrics: return "歌詞が不適切"
        case .other:  return "その他"
        }
    }
}

/// マイページ 学習履歴 entry
struct StudyHistoryEntry: Hashable, Identifiable {
    let id: UUID
    let date: String        // "2026-04-30"
    let tapKind: StudyTap
    let tapLabel: String    // "学習開始" / "中場確認" / "学習終了"
    let timeHM: String      // "19:38"
    let note: String?

    init(date: String, tapKind: StudyTap, tapLabel: String, timeHM: String, note: String?) {
        self.id = UUID()
        self.date = date
        self.tapKind = tapKind
        self.tapLabel = tapLabel
        self.timeHM = timeHM
        self.note = note
    }

    /// マイページ 学習履歴 demo seed
    static var demoSeed: [StudyHistoryEntry] {
        [
            .init(date: "2026-04-29", tapKind: .end,   tapLabel: "学習終了", timeHM: "21:46", note: nil),
            .init(date: "2026-04-29", tapKind: .mid,   tapLabel: "中場確認", timeHM: "20:46", note: nil),
            .init(date: "2026-04-29", tapKind: .start, tapLabel: "学習開始", timeHM: "19:37", note: nil),
            .init(date: "2026-04-28", tapKind: .end,   tapLabel: "学習終了", timeHM: "21:45", note: nil),
            .init(date: "2026-04-28", tapKind: .mid,   tapLabel: "中場確認", timeHM: "20:46", note: nil),
            .init(date: "2026-04-28", tapKind: .start, tapLabel: "学習開始", timeHM: "19:42", note: "1 分遅刻"),
        ]
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
