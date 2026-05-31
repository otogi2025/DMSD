// AppStore.swift
// ⭐ Foundation · 全局 app state（对等 phaseB_src AppProvider）

import Combine
import Foundation
import SwiftUI

/// 学生注册流程累积器（Step1-5 各自填字段、Step5 提交时整体送 backend）
///
/// spec: system_features §7.16 + BACKEND §5.1.5
/// 字段命名跟 backend `StudentAccountCreateBody` 一对一，方便对照。
struct RegistrationDraft {
    // Step1 基本信息
    var name: String = ""
    var birthday: Date? = nil
    var gender: String = "male" // "male" or "female"
    var is_overseas: Bool = false
    var grade_code: String = "" // 2 桁
    var class_code: String = "" // 2 桁
    var seat_no: String = "" // 2 桁
    /// room 输入框只让学生填数字部分（"101" / "205B"），M/W 前缀由 gender 自动加
    var room_no_suffix: String = ""

    /// Step2 点呼区分
    var category: String = "一般寮生"

    // Step3 联络方式
    var email: String? = nil
    var phone: String? = nil

    /// Step4 密码
    var password: String = ""

    /// 拼 M/W 前缀 → 完整 room_no（backend §5.0 编码规则）
    /// suffix 空 = 上层 UI 漏了校验，返回空字符串让 backend 拒绝（room_no 是必填字段）
    var computedRoomNo: String {
        guard !room_no_suffix.isEmpty else { return "" }
        let prefix = (gender == "male") ? "M" : "W"
        return prefix + room_no_suffix
    }

    /// 从 room_no_suffix 第一位 + gender 推 dorm_unit
    /// 男生 1xx → 1 寮 / 2xx → 2 寮；女生不论房号都 4 寮
    var computedDormUnit: Int {
        if gender == "female" { return 4 }
        if let first = room_no_suffix.first, first == "2" { return 2 }
        return 1
    }

    /// 生日 ISO 字符串（"yyyy-MM-dd"），没填则 nil
    var birthdayString: String? {
        guard let b = birthday else { return nil }
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        // IX-015: 锁定公历 + 固定 locale，否则用户把 iPhone 系统日历设成「和暦（日本年号）」时
        // 年份会被格式化成年号纪年（令和7年 → 0007），把生日写错。参照 todayJaYMD() 的写法。
        f.locale = Locale(identifier: "en_US_POSIX")
        f.calendar = Calendar(identifier: .gregorian)
        return f.string(from: b)
    }
}

/// アカウント関連フィールドの変更履歴（MyInfo 編集時に append）
struct ChangeLogEntry: Hashable, Identifiable {
    let id: UUID
    let at: Date // 変更時刻
    let field: String // 例: "grade" / "room"
    let label: String // 日本語表示: "学年" / "部屋番号"
    let before: String
    let after: String

    init(field: String, label: String, before: String, after: String) {
        id = UUID()
        at = Date()
        self.field = field
        self.label = label
        self.before = before
        self.after = after
    }
}

@MainActor
final class AppStore: ObservableObject {
    /// JWT 访问 token — login 成功后赋值、跟 APIClient.shared.token 同步
    /// 同时持久化到 KeychainService（app 重启后能恢复）
    @Published var authToken: String? = nil {
        didSet {
            APIClient.shared.token = authToken
            if let t = authToken {
                KeychainService.save(token: t)
            } else {
                KeychainService.delete()
            }
        }
    }

    /// A-036 (2026-05-21): 登录 gate
    /// 用 token 是否存在判断（token 失效会在 401 时清空触发重新登录）
    /// view 应该用此 gate 决定是否回退到 SEED.user 占位（登录前）或显示「— 」（登录后未拉到数据）
    var isAuthenticated: Bool {
        authToken != nil
    }

    /// IX-036: 令牌过期时刻（UserDefaults key）。
    /// 有效期本身不是机密（机密的是令牌正文，仍存 Keychain），所以过期时刻放 UserDefaults。
    private static let tokenExpiryKey = "authTokenExpiresAt"

    /// IX-036: 存令牌 + 有效期。登录 / 注册成功后调，把 expires_in（秒）换算成绝对过期时刻存下，
    /// 启动时 init() 能据此判断是否已过期。
    func setAuthToken(_ token: String, expiresIn: Int) {
        let expiresAt = Date().addingTimeInterval(TimeInterval(expiresIn))
        UserDefaults.standard.set(expiresAt.timeIntervalSince1970, forKey: Self.tokenExpiryKey)
        authToken = token // didSet 同步 APIClient + Keychain
    }

    /// app 启动时从 Keychain 恢复 token（实现自动登录）
    init() {
        if let saved = KeychainService.load() {
            // IX-036: 之前只判断「有没有令牌」就当已登录，登录响应解码了 expires_in 却从不使用，
            // 令牌过期后启动仍进主页，直到某请求 401 才被踢，中间所有请求全部加载失败。
            // 现在启动时若已过期就删令牌（authToken=nil → didSet 删 Keychain）+ 清过期时刻，走登录页。
            let expiryTs = UserDefaults.standard.object(forKey: Self.tokenExpiryKey) as? Double
            if let ts = expiryTs, Date().timeIntervalSince1970 >= ts {
                // 已过期 → 不恢复，删令牌 + 过期记录
                KeychainService.delete()
                UserDefaults.standard.removeObject(forKey: Self.tokenExpiryKey)
            } else {
                // 未过期（或没存过期时刻的旧令牌 → 保守恢复，由后续 401 兜底）
                // 直接赋 _authToken 会跳过 didSet → APIClient 同步不上、所以走 self.authToken
                authToken = saved
            }
        }
        // A-038 (2026-05-21): seedDemoAnnouncements() 调用已删
        // 公告 demo seed 整段函数已删；公告全走 backend AnnouncementsAPI
    }

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

    /// 账号关联字段的变更履歴（MyInfo 编辑时 append）
    /// production 版初始空、登录后从后端拉；demo 版有进级 placeholder seed。
    @Published var changeLog: [ChangeLogEntry] = {
        #if DEMO
            return [ChangeLogEntry(field: "grade", label: "学年", before: "高2", after: "高3")]
        #else
            return []
        #endif
    }()

    /// 変更を記録（field ごと · before == after ならスキップ）
    func appendChange(field: String, label: String, before: String, after: String) {
        guard before != after else { return }
        changeLog.insert(
            ChangeLogEntry(field: field, label: label, before: before, after: after),
            at: 0
        )
    }

    // MARK: - 学生新规注册（2026-05-04 加，spec system_features.md §7.16）

    //
    // 注册流程: Step1 基本信息 → Step2 点呼区分 → Step3 联络方式 → Step4 密码 → Step5 注册码
    //   - 各 Step 在 onNext 时把自己的字段写入 registrationDraft
    //   - Step5 提交时 createAccount(registrationCode) 用 draft 字段拼 body 调 backend
    //   - 注册成功 → registerDone view 进入时 resetRegistrationDraft 清空（避免下次注册脏数据）

    /// 注册流程累积器 — RegisterStep1-4 各自把 local @State 写入这里
    @Published var registrationDraft = RegistrationDraft()

    /// 把当前 draft + 注册码 拼成 backend body 调 POST /accounts。
    /// 成功后 access_token 自动写入 authToken（didSet 同步给 APIClient + Keychain）。
    /// 字段空值由上层 Step 校验拦截 — 这里不做 demo fallback，空值直接传给 backend 让 422 拒绝
    func createAccount(registrationCode: String) async throws -> StudentAccountCreateResponse {
        let d = registrationDraft
        let body = StudentAccountCreateBody(
            name: d.name,
            name_kana: nil, // Step1 没收集 kana，先传 nil
            birthday: d.birthdayString, // 没填 = nil
            gender: d.gender,
            grade_code: d.grade_code,
            class_code: d.class_code,
            seat_no: d.seat_no,
            category: d.category,
            room_no: d.computedRoomNo, // 拼 M/W 前缀
            dorm_unit: d.computedDormUnit, // 从 room_suffix + gender derive
            is_overseas: d.is_overseas,
            email: (d.email?.isEmpty == false) ? d.email : nil,
            phone: (d.phone?.isEmpty == false) ? d.phone : nil,
            password: d.password,
            registration_code: registrationCode
        )
        // IX-026: 发请求前先跑客户端校验（max length / 密码长度）。校验不过抛错、不发请求，
        // 避免白发一趟必被 backend 422 拒绝的请求。validate() 返回 nil = OK，否则返回日语错误信息。
        if let validationError = body.validate() {
            throw APIError.unprocessable(validationError)
        }
        let res = try await AccountsAPI.createAccount(body: body)
        // IX-036: 存令牌时一并存有效期，启动时能判断是否过期
        setAuthToken(res.accessToken, expiresIn: res.expiresIn)
        return res
    }

    /// 注册完成后清空 draft（registerDone view 进入时调）
    func resetRegistrationDraft() {
        registrationDraft = RegistrationDraft()
    }

    // MARK: - 老师公告 state（2026-05-04 加，spec §7.15）

    /// 主页 badge 用未读数（每次进入主页 + 收到 push 时刷新）
    @Published var announcementUnreadCount: Int = 0

    /// 列表 cache — 进入一覧 view 时 reload；详情访问后该 entry 的 isRead 翻 true
    @Published var announcements: [AnnouncementBrief] = []

    /// 详情 cache — 按 id 缓存，回复发完后 append 到对应 detail
    @Published var announcementDetails: [String: AnnouncementDetail] = [:]

    /// 拉未读数
    func loadAnnouncementUnreadCount() async {
        do {
            let res = try await AnnouncementsAPI.unreadCount()
            announcementUnreadCount = res.unreadCount
        } catch {
            // 拉失败不阻塞主页其他功能 — 静默忽略，下次刷新再试
        }
    }

    /// 拉列表（一覧 view 进入时调）
    func loadAnnouncementList() async throws {
        let res = try await AnnouncementsAPI.list()
        announcements = res.items
    }

    /// 拉详情（详情 view 进入时调；自动写已读 → backend 下次 list 返回 isRead=true）
    func loadAnnouncementDetail(id: String) async throws {
        let detail = try await AnnouncementsAPI.detail(id: id)
        announcementDetails[id] = detail
        // 详情 GET 后端会自动 mark read，本地 cache 也同步翻 true
        if let idx = announcements.firstIndex(where: { $0.id.uuidString == id }) {
            // brief 是 immutable struct — 整条替换
            let old = announcements[idx]
            announcements[idx] = AnnouncementBrief(
                id: old.id, title: old.title, bodySummary: old.bodySummary,
                scope: old.scope, authorTeacherId: old.authorTeacherId,
                authorTeacherName: old.authorTeacherName,
                createdAt: old.createdAt, updatedAt: old.updatedAt,
                isRead: true, // ← flip 已读
                replyCount: old.replyCount
            )
        }
        // 同步未读数
        await loadAnnouncementUnreadCount()
    }

    /// 发回复（学生用 — 老师 reply 走 teacher_web）
    func postAnnouncementReply(announcementId: String, body: String) async throws {
        let reply = try await AnnouncementsAPI.postReply(
            announcementId: announcementId, body: body
        )
        // 同步本地 detail cache
        if let detail = announcementDetails[announcementId] {
            // detail.replies 是 let 字段 — 整条替换
            let updated = AnnouncementDetail(
                id: detail.id, title: detail.title, body: detail.body,
                scope: detail.scope, authorTeacherId: detail.authorTeacherId,
                authorTeacherName: detail.authorTeacherName,
                createdAt: detail.createdAt, updatedAt: detail.updatedAt,
                replies: detail.replies + [reply]
            )
            announcementDetails[announcementId] = updated
        }
    }

    // A-038 (2026-05-21): seedDemoAnnouncements() 整段函数已删（141 行 demo seed）
    // 公告全走 backend AnnouncementsAPI；本地不再 mock

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

    // MARK: - 点呼 NFC 签到记录

    //
    // TODO[backend]: 真 production 流程 = NFC sheet "NFC をかざす" tap
    //   → core NFC delegate 拿到 tag UID → POST /checkins (uid, session_id, ts)
    //   → 后端返回 checkin record → 这里更新 rollState / checkinAt / checkinKind
    // 当前是接入前的 mock：直接本地记录，后端联通后改成 await api.postCheckin(...)。

    /// done 表示自动恢复 idle 的任务（避免重复持有）
    private var autoDismissDoneTask: Task<Void, Never>?

    /// NFC tap 成功后调（真 production 由后端 response 触发）
    func recordCheckin() {
        let fmt = DateFormatter()
        fmt.dateFormat = "HH:mm"
        checkinAt = fmt.string(from: Date())
        checkinKind = "時間内"
        rollState = .done

        // 5 秒后自动恢复 idle（done 完成提示自然消失）
        autoDismissDoneTask?.cancel()
        autoDismissDoneTask = Task { [weak self] in
            try? await Task.sleep(nanoseconds: 5_000_000_000)
            guard !Task.isCancelled else { return }
            await MainActor.run {
                guard let self else { return }
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

    // A-030 / A-033 (2026-05-21): cycleDemoRollState() 已删
    // memory project_demo_scaffolds_to_remove_before_v1.md #1, #15
    // 接 backend event 驱动后 rollState 由 server 推送，不再 demo 循环

    /// active 中に 1 秒ごと呼ばれる（HomeView の Timer から）
    func tickCountdown() {
        guard rollState == .active, rollCountdownSec > 0 else { return }
        rollCountdownSec -= 1
    }

    // MARK: - 学習（晚自习）状态机

    //
    // TODO[backend]: 真 production 由后端 cron 5 分前自动开启 upcoming，老师手动切 active / done。
    // 当前是首次启动 placeholder（idle），等接 GET /study/today/state 拉。
    // amber Card 三态切换 demo 用 long press 切（仅 #if DEMO 启用）

    /// 学習状态（idle / upcoming / active / done）
    @Published var studyState: StudyState = .idle

    /// 学習迟到倒计时（upcoming 时秒数）— 默认 10 分（19:35-19:40 窗口的 spec 值）
    @Published var studyCountdownSec: Int = 600

    /// 当月学習请假次数（> 3 → 弹提醒文案）— production 初始 0、登录后从后端拉；demo 初始 3 触发提醒
    @Published var studyLeaveCountThisMonth: Int = {
        #if DEMO
            return 3
        #else
            return 0
        #endif
    }()

    /// upcoming 时 1 秒一次 tick（HomeView Timer 同时触发 roll + study）
    func tickStudyCountdown() {
        guard studyState == .upcoming, studyCountdownSec > 0 else { return }
        studyCountdownSec -= 1
    }

    /// 学習欠席届 提交（system_features §7.3.5）— 后端通过后 += 1、> 3 触发提醒
    /// 接 POST /api/v1/study/absence-requests。target_date は呼び出し側が JST yyyy-MM-dd で指定。
    /// async throws，调用方负责 catch 错误（重复提交 / 401 等）。
    func submitStudyLeave(targetDate: String, reason: String, range: StudyLeaveRange) async throws {
        // backend 接收成功后才 += 1，避免重复提交把计数推爆
        _ = try await StudyAPI.submitAbsenceRequest(
            targetDate: targetDate,
            period: range.wireValue,
            reason: reason
        )
        studyLeaveCountThisMonth += 1
        if studyLeaveCountThisMonth > 3 {
            showToast("今月、もう \(studyLeaveCountThisMonth) 回お休みされていますね。体調管理、お気をつけて。")
        } else {
            showToast("学習欠席届を提出しました")
        }
    }

    /// JST 今日的 "yyyy-MM-dd" 字符串
    private static func todayJaYMD() -> String {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = TimeZone(identifier: "Asia/Tokyo")
        return f.string(from: Date())
    }

    #if DEMO
        /// Demo 用：长按学習卡循环 4 态状态（演示用、production 砍）
        /// memory project_demo_scaffolds_to_remove_before_v1.md #15
        func cycleDemoStudyState() {
            switch studyState {
            case .idle: studyState = .upcoming; studyCountdownSec = 600; showToast("Demo · 学習 10 分前 (倒计时 10:00)")
            case .upcoming: studyState = .active; studyTaps = []; showToast("Demo · 学習進行中（NFC で 3 回タップ）")
            case .active: studyState = .done; showToast("Demo · 学習終了")
            case .done: studyState = .idle; studyTaps = []; showToast("Demo · 学習対象外")
            }
        }
    #endif

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
        if !studyTaps.contains(.mid) { return .mid }
        if !studyTaps.contains(.end) { return .end }
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
            case .mid: return "中場確認"
            case .end: return "学習終了"
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

    /// マイページ「学習履歴」用 — production 空、demo 加 fixture seed
    /// TODO[backend]: 登录后从 GET /study/attendance/mine 拉真数据
    @Published var studyHistory: [StudyHistoryEntry] = {
        #if DEMO
            return StudyHistoryEntry.demoSeed
        #else
            return []
        #endif
    }()

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
        if songBanLevel >= 3 { return false } // 永久禁止
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
    func reportSong(songId: Int, reason _: SongReportReason, freeText _: String?) {
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
        return nil // 永久
    }

    /// 現在のロック段階の表示文字列
    var currentLockoutLabel: String {
        switch loginFailCount {
        case 1: return "30 秒"
        case 2: return "1 分"
        case 3: return "5 分"
        case 4: return "30 分"
        case 5: return "1 時間"
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

    // MARK: - Push 通知 listener (system_features §7.13 R1 例外)

    //
    // TODO[backend]: 真 production 由 APNs delegate（AppDelegate.didReceiveRemoteNotification）
    //   → 解析 payload → 调 handleIncomingPush(...) 把通知 insert 到 pushNotifications。
    // 当前是接入前的 store：APNs 接通前 pushNotifications 空。

    /// 真 push 接收後動的に追加される通知（SEED.notifications は静的の初期 placeholder）
    @Published var pushNotifications: [NotificationItem] = []

    /// 通知中心显示用 — push 在前 + SEED.notifications fixture
    var allNotifications: [NotificationItem] {
        pushNotifications + SEED.notifications
    }

    /// 未読数（home greetingRow bell badge 用）
    var unreadNotificationCount: Int {
        allNotifications.filter { $0.unread }.count
    }

    /// APNs delegate 受信後调 — push 1 条 insert
    /// - Parameters:
    ///   - type: NotificationItem.type 字段（"申請" / "減点" / "学習" / "リクエスト曲" 等）
    ///   - title: 标题
    ///   - body: 正文
    func handleIncomingPush(type: String, title: String, body: String) {
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

    #if DEMO
        // Demo 用 4 个 push 触发器（system_features §7.13 R1 例外列出的事件）
        // production 砍：APNs 接通后由真 push 触发 handleIncomingPush

        func simulateStudyLeaveApproved() {
            handleIncomingPush(
                type: "学習",
                title: "学習欠席届が承認されました",
                body: "本日の前半節について、学習担当の先生から承認されました。"
            )
        }

        func simulateStudyLeaveRejected() {
            handleIncomingPush(
                type: "学習",
                title: "学習欠席届が不承認でした",
                body: "本日の前半節は出席をお願いします。詳細は学習担当の先生にお尋ねください。"
            )
        }

        func simulateStudyRosterAdded() {
            handleIncomingPush(
                type: "学習",
                title: "学習対象になりました",
                body: "今日から晩自習の対象に追加されました。19:40 までに学習室へお越しください。"
            )
        }

        func simulateAmendmentRebatch() {
            handleIncomingPush(
                type: "申請",
                title: "外泊届（修改届）が承認されました",
                body: "修改届の内容で寮務課長まで承認が進みました。残り 1 名の承認をお待ちください。"
            )
        }
    #endif
}

// MARK: - 学習 NFC 出席（system_features §7.3.3-6）

enum StudyTap: String, Hashable, CaseIterable {
    case start // 19:35 ～ 19:40 学習開始
    case mid // 20:45 ± 中場
    case end // 21:45 学習終了
}

/// 出席状態（amber Card / マイページ で表示）
enum StudyAttendance: String {
    case idle // 学習時間外
    case none // active だが 0 tap
    case progressing // 1 tap 済（通常進行中）
    case green // 全 3 tap 済 = 時間内
    case yellow // 遅刻
    case red // 缺席
    case abnormal // 不一致 = ⚠️ 異常 老師手動判
    case excused // 欠席承認済
}

// MARK: - 通報理由 (system_features §7.11.2)

enum SongReportReason: String, CaseIterable, Hashable {
    case noisy // うるさい
    case taste // 曲調が好みでない / 不快
    case lyrics // 歌詞が不適切
    case other // その他（自由記入）

    var label: String {
        switch self {
        case .noisy: return "うるさい"
        case .taste: return "曲調が好みでない / 不快"
        case .lyrics: return "歌詞が不適切"
        case .other: return "その他"
        }
    }
}

/// マイページ 学習履歴 entry
struct StudyHistoryEntry: Hashable, Identifiable {
    let id: UUID
    let date: String // "2026-04-30"
    let tapKind: StudyTap
    let tapLabel: String // "学習開始" / "中場確認" / "学習終了"
    let timeHM: String // "19:38"
    let note: String?

    init(date: String, tapKind: StudyTap, tapLabel: String, timeHM: String, note: String?) {
        id = UUID()
        self.date = date
        self.tapKind = tapKind
        self.tapLabel = tapLabel
        self.timeHM = timeHM
        self.note = note
    }

    /// マイページ 学習履歴 demo seed
    static var demoSeed: [StudyHistoryEntry] {
        [
            .init(date: "2026-04-29", tapKind: .end, tapLabel: "学習終了", timeHM: "21:46", note: nil),
            .init(date: "2026-04-29", tapKind: .mid, tapLabel: "中場確認", timeHM: "20:46", note: nil),
            .init(date: "2026-04-29", tapKind: .start, tapLabel: "学習開始", timeHM: "19:37", note: nil),
            .init(date: "2026-04-28", tapKind: .end, tapLabel: "学習終了", timeHM: "21:45", note: nil),
            .init(date: "2026-04-28", tapKind: .mid, tapLabel: "中場確認", timeHM: "20:46", note: nil),
            .init(date: "2026-04-28", tapKind: .start, tapLabel: "学習開始", timeHM: "19:42", note: "1 分遅刻"),
        ]
    }
}

// MARK: - 学習状态 + 请假范围 (4-30 後續 拍板)

enum StudyState: String {
    case idle // 平常 (非学習时段)
    case upcoming // 学習开始 10 分前 → amber Card 显示倒计时
    case active // 学習进行中
    case done // 当晚学習已结束
}

enum StudyLeaveRange: String, CaseIterable {
    case first // 前半節 19:40-20:40
    case second // 後半節 20:45-21:45
    case both // 両方

    var label: String {
        switch self {
        case .first: return "前半節（19:40〜20:40）"
        case .second: return "後半節（20:45〜21:45）"
        case .both: return "両方"
        }
    }

    /// backend wire format: schemas.StudyAbsenceRequestIn.period の値
    var wireValue: String {
        switch self {
        case .first: return "first_half"
        case .second: return "second_half"
        case .both: return "full"
        }
    }
}
