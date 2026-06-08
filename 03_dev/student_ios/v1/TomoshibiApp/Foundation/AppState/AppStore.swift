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
        // IX-014: 房号首位已是字母（如 "A5"）= 已含楼栋标识，不再加 M/W 前缀（否则变 "MA5"）；
        // 数字房号（如 "101"）才加 M/W 前缀 → "M101"。前缀只在这一处加，避免双前缀。
        if room_no_suffix.first?.isLetter == true { return room_no_suffix }
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
                // IX-008: 登出 / 令牌失效 → 清当前用户 + SEED.user 复位演示默认，
                // 防上一个真实用户的姓名 / 房号等残留到登录页 / 下一个人。
                currentUser = nil
                myStudentId = nil
                needsRenewal = false
                SEED.user = SEED.demoUserSeed
                #if !DEMO
                    // IX-008 Batch 2: 生产构建登出，把所有跟当前用户绑定的状态一并清空 ——
                    // 防 A 登出、B 在同一进程登录（AppStore 单例不重建）看到 A 的编辑历史 / 公告缓存残留。
                    changeLog = []
                    studyHistory = []
                    announcements = []
                    announcementDetails = [:]
                    announcementUnreadCount = 0
                    packages = []
                    studyLeaveCountThisMonth = 0
                    cleaningHistory = []
                    songRequests = []
                    lostFound = []
                    myRollcallEvents = []
                    myDemeritEvents = []
                #endif
            }
        }
    }

    /// A-036 (2026-05-21): 登录 gate
    /// 用 token 是否存在判断（token 失效会在 401 时清空触发重新登录）
    /// view 应该用此 gate 决定是否回退到 SEED.user 占位（登录前）或显示「— 」（登录后未拉到数据）
    var isAuthenticated: Bool {
        authToken != nil
    }

    /// IX-008: 当前登录学生的真实信息（登录后从 GET /students/me 拉）。
    /// nil = 未登录 / 演示 / 还没拉到 → displayUser 回退 SEED.user 假占位。
    @Published var currentUser: User? = nil

    /// 当前登录学生自己的 UUID 字符串（loadMe 从 /students/me 的 id 填）。
    /// 功能⑤遗失物「本人才能解决」owner 判断 + 功能⑦⑧拉 /students/{id}/profile 都要用它。
    /// 登出随 currentUser 一起清。
    @Published var myStudentId: String? = nil

    /// 学年更新「待更新」标记（spec §4.2）— GET /students/me 的 needs_renewal。
    /// true = 主页顶部显示「更新番号」按钮，让学生自设新番号。登出清 false。
    @Published var needsRenewal: Bool = false

    /// IX-008: 各页显示当前用户统一走这个 —— 登录拉到真实数据就用真的，否则 SEED.user 占位。
    /// 替换原来直接读 SEED.user（演示假数据泄漏到生产）。
    var displayUser: User {
        currentUser ?? SEED.user
    }

    /// AppDelegate（push 回调）拿不到 SwiftUI 的 @StateObject 实例 —— 用单例共享同一个 AppStore。
    /// App 入口的 @StateObject 也指向 shared，保证 push 回调写的状态就是界面读的那个。
    static let shared = AppStore()

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

    /// IX-008: 拉当前登录学生信息（GET /students/me）填到 currentUser。
    /// 登录成功后 + app 启动恢复令牌后调。拉不到就保持 nil（displayUser 回退 SEED 占位），不打断流程。
    @MainActor
    func loadMe() async {
        #if DEMO
            // 演示构建永不拉真后端 —— 始终用 SEED 假数据讲叙事。
            // 兑现「演示态不执行 loadMe」的承诺（之前只靠 isAuthenticated 挡，没真隔离构建）。
            return
        #else
            // IX-034 修复②：捕获进入时的令牌，每次 await 后 / 写回前都比对同一个令牌。
            // 只查 isAuthenticated 不够 —— A 登出后 B 立刻登录，isAuthenticated 仍为真，
            // A 的旧 loadMe 结果会被写进 B。比对令牌本身才能挡住这种竞态。
            guard let tokenAtStart = authToken else { return }
            do {
                let me = try await StudentsAPI.me()
                // await 之后确认还是同一个登录令牌 —— 防 await 期间已登出 / 换了人。
                guard authToken == tokenAtStart else { return }
                var mapped = Self.mapMeToUser(me)
                // IX-008b: 再拉当月扣分汇总填统计（拉不到保持 0，不打断登录）。
                if let summary = try? await DisciplineAPI.mySummary() {
                    mapped.points = summary.total_points
                    mapped.lateCount = summary.late_count
                    mapped.absentCount = summary.absent_count
                }
                // IX-034: 再拉当月学習欠席届次数（按月真实数，替代纯内存累加 —
                //   重启 / 跨月不再丢失）。拉不到 nil 保持原值，不打断登录。
                let absenceRevAtStart = absenceCountRevision
                let absenceCount = (try? await StudyAPI.myAbsenceSummary())?.count
                // summary / absence 都有 await，写回前再确认还是同一个令牌。
                guard authToken == tokenAtStart else { return }
                currentUser = mapped
                // 功能⑤⑦⑧用：存本人 UUID（遗失物 owner 判断 + 拉个人 profile）。
                myStudentId = me.id
                // 学年更新「待更新」标记（spec §4.2）— 后端 /me 的 needs_renewal，缺省按 false。
                needsRenewal = me.needs_renewal ?? false
                // IX-034 修复③(补)：代次没变才写回 —— summary 在途时若用户提交了请假
                // （+1 并自增代次），旧 summary 数不得覆盖刚更新的本地数。
                if let absenceCount, absenceCountRevision == absenceRevAtStart {
                    studyLeaveCountThisMonth = absenceCount
                }
                // 安全网：同时写回 SEED.user，覆盖那些没法用 app.displayUser 的站点
                // （@State 默认值 / 纯 mock 数据 / 静态 helper）。
                SEED.user = mapped
                // IX-009：登录 / 启动即拉公告未読数，让 Home 铃铛 badge 首屏就准
                // （announcements 列表是懒加载、首屏可能空；这里只拉轻量 count）。
                await loadAnnouncementUnreadCount()
                // IX-009：登录 / 启动即拉包裹，让 Home 铃铛 badge 首屏含包裹未読。
                await loadMyPackages()
                // IX-009：补报启动时还没登录就拿到的 APNs deviceToken。
                await flushDeviceTokenIfPossible()
            } catch APIError.unauthorized {
                // 令牌过期 / 失效（401）→ 清令牌强制重登（didSet 会清 currentUser + 复位 SEED.user），
                // 不再默默回退到演示假人身份。
                // IX-034 修复②(补)：401 也比对令牌 —— A 的旧 /me 在 A 登出、B 登录后才返 401，
                // 不能误清掉 B 的令牌。
                guard authToken == tokenAtStart else { return }
                authToken = nil
            } catch {
                // 网络 / 解码失败 → 保持 currentUser = nil，displayUser 回退占位，不打断登录。
                // 打日志区分（后端字段改名导致的解码失败，开发期能据此发现）。
                print("[loadMe] /students/me 拉取失败：\(error)")
            }
        #endif
    }

    /// 后端 /me 响应（StudentMeOut）映射成 iOS User。/me 只给身份字段：
    /// - 统计（points / lateCount / absentCount）/me 没有 → 这里先填 0，loadMe 再拉 DisciplineAPI.mySummary 覆盖（IX-008b）
    /// - isStudyTarget（学習対象）/me 没这 flag → 默认 false（只有老师后台设的才是；
    ///   UI 入口仍显示、点进去由各页据此显「不需要晚自习」）
    private static func mapMeToUser(_ me: StudentMeOut) -> User {
        // 内联三元 / 可选解包先拆成局部变量 — 否则 20 参数的 User(...) 字面量类型检查会超时
        let genderLabel = me.gender == "female" ? "女" : "男"
        let dormLabel = me.dorm_unit == 4 ? "女寮" : "男寮"
        let avatarChar = String(me.name.prefix(1)) // 头像占位 = 姓名首字
        let seat = Int(me.seat_no) ?? 0
        return User(
            account: me.student_no,
            name: me.name,
            nameKana: me.name_kana ?? "",
            birth: "", // /me 不含生日；SEED.user.birth 无站点读取，留空
            age: 0,
            gender: genderLabel,
            dorm: dormLabel,
            room: me.room_no,
            category: me.category,
            email: me.email ?? "",
            phone: me.phone ?? "",
            avatar: avatarChar,
            points: 0,
            lateCount: 0,
            absentCount: 0,
            grade: gradeLabel(me.grade_code),
            classSuffix: classLabel(me.class_code),
            seatNo: seat,
            isStudyTarget: false,
            isOverseas: me.is_overseas
        )
    }

    /// 年级码 → 标签（中高一貫 6 年制：01→中1 … 06→高3）。
    private static func gradeLabel(_ code: String) -> String {
        switch code {
        case "01": return "中1"
        case "02": return "中2"
        case "03": return "中3"
        case "04": return "高1"
        case "05": return "高2"
        case "06": return "高3"
        default: return code
        }
    }

    /// 班级码 → 字母（01→A / 02→B / …）。
    private static func classLabel(_ code: String) -> String {
        guard let n = Int(code), n >= 1, n <= 26 else { return code }
        return String(UnicodeScalar(64 + n)!) // 65 = "A"
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
                // ⚠️ Swift 规则（已 swift 实测）：在 init 内给带 didSet 的属性赋值**不触发 didSet**。
                //   所以光 `authToken = saved` 不会同步 APIClient.shared.token（didSet 才做这件事），
                //   启动后所有请求无 Authorization 头 → 401 → loadMe 把刚恢复的登录态又清掉、冷启动保持登录失效。
                //   必须在这里显式同步一次（codex 第三轮 major #1）。
                authToken = saved
                APIClient.shared.token = saved
            }
        }
        // IX-008: 启动若已恢复有效令牌，拉当前学生信息填 currentUser（各页显真实数据，非演示假数据）
        if isAuthenticated {
            Task { await loadMe() }
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
        // IX-008: 注册成功也拉 /me，跟登录路径对齐 —— 否则新注册真实学生首屏显演示假人
        // （「リュウ イヒ」/ 4.5 点）直到冷启动才恢复。
        await loadMe()
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
        let tokenAtStart = authToken
        do {
            let res = try await AnnouncementsAPI.unreadCount()
            // IX-009：登出 / 切用户后不写回旧用户的未読数（防 badge 串号）。
            guard authToken == tokenAtStart else { return }
            announcementUnreadCount = res.unreadCount
        } catch {
            // 拉失败不阻塞主页其他功能 — 静默忽略，下次刷新再试
        }
    }

    /// 拉列表（一覧 view 进入时调）
    func loadAnnouncementList() async throws {
        let tokenAtStart = authToken
        let res = try await AnnouncementsAPI.list()
        // IX-009：登出 / 切用户后不写回旧用户的公告列表（防上一个人的公告残留到下一个人）。
        guard authToken == tokenAtStart else { return }
        announcements = res.items
    }

    /// 拉详情（详情 view 进入时调；自动写已读 → backend 下次 list 返回 isRead=true）
    func loadAnnouncementDetail(id: String) async throws {
        let tokenAtStart = authToken
        let detail = try await AnnouncementsAPI.detail(id: id)
        // IX-009：登出 / 切用户后不写回旧用户的公告详情 / 已读状态（防详情缓存 + 列表已读串号）。
        guard authToken == tokenAtStart else { return }
        announcementDetails[id] = detail
        // 详情 GET 后端会自动 mark read，本地 cache 也同步翻 true
        if let idx = announcements.firstIndex(where: { $0.id.uuidString.caseInsensitiveCompare(id) == .orderedSame }) {
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
        let tokenAtStart = authToken
        let reply = try await AnnouncementsAPI.postReply(
            announcementId: announcementId, body: body
        )
        // IX-009：登出 / 切用户后不写回旧用户的回复缓存。
        guard authToken == tokenAtStart else { return }
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

    /// IX-034 修复③(补)：本月请假数的本地写回代次。submitStudyLeave 成功后自增，
    /// loadMe 写回前比对 —— 在途的旧 summary 不得覆盖刚提交后更新的本地数。
    private var absenceCountRevision = 0

    /// upcoming 时 1 秒一次 tick（HomeView Timer 同时触发 roll + study）
    func tickStudyCountdown() {
        guard studyState == .upcoming, studyCountdownSec > 0 else { return }
        studyCountdownSec -= 1
    }

    /// 学習欠席届 提交（system_features §7.3.5）— 后端通过后 += 1、> 3 触发提醒
    /// 接 POST /api/v1/study/absence-requests。target_date は呼び出し側が JST yyyy-MM-dd で指定。
    /// async throws，调用方负责 catch 错误（重复提交 / 401 等）。
    func submitStudyLeave(targetDate: String, reason: String, range: StudyLeaveRange) async throws {
        // IX-034 修复②(补)：进入即捕获令牌 —— 提交在途若登出/切到别的用户，
        // 接口成功返回后不再把 +1 / toast 写到登出态或下一个人身上。
        let tokenAtStart = authToken
        // backend 接收成功后才 += 1，避免重复提交把计数推爆
        _ = try await StudyAPI.submitAbsenceRequest(
            targetDate: targetDate,
            period: range.wireValue,
            reason: reason
        )
        // 提交在途登出/切用户：抛 CancellationError 让调用方静默中止（不导航完成页、不弹错）。
        guard authToken == tokenAtStart else { throw CancellationError() }
        // IX-034 修复①：只有 targetDate 属于 JST 当月才 +1 本月计数。
        // 表单能选今天～+14 天、可能跨到下月（5 月底提交 6 月的）——
        // 那种后端按 target_date 归到下月、不计入本月，iOS 也不能本月 +1，
        // 否则跟 loadMe 重拉的后端当月数对不上。targetDate 是 JST yyyy-MM-dd（formatYMD 已固定 JST）。
        let isThisMonth = targetDate.prefix(7) == Self.todayJaYMD().prefix(7)
        if isThisMonth {
            studyLeaveCountThisMonth += 1 // 乐观 +1，即时反馈
            absenceCountRevision += 1 // 标记本地已变更，挡在途旧 loadMe summary 覆盖（IX-034 修复③补）
            // 再拉后端 canonical 当月数收敛（含历史次数）—— 防启动恢复时 local 还是 0、
            // 只 +1 显示偏低（被代次守卫拦下的旧 summary 不会再自己收敛）。token + 代次双守卫写回。
            let revAfterSubmit = absenceCountRevision
            if let fresh = (try? await StudyAPI.myAbsenceSummary())?.count,
               authToken == tokenAtStart, absenceCountRevision == revAfterSubmit
            {
                studyLeaveCountThisMonth = fresh
            }
        }
        // IX-034 修复②(补)：canonical await 后再确认还是同一个登录 —— 提交在途登出/切用户时
        // 不把完成提示 / 完成页写到登出态或下一个人；抛 CancellationError 让调用方静默中止导航。
        guard authToken == tokenAtStart else { throw CancellationError() }
        if isThisMonth, studyLeaveCountThisMonth > 3 {
            showToast("今月、もう \(studyLeaveCountThisMonth) 回お休みされていますね。体調管理、お気をつけて。")
        } else {
            showToast("学習欠席届を提出しました")
        }
    }

    /// 番号再設定 提交（学年更新 / 学生自设番号，spec §4.2）。
    /// 接 POST /api/v1/students/me/renew-number。撞号后端返 422 → 调用方 catch 弹日语提示。
    /// 成功后清 needsRenewal 标记 + 重拉 /me 让新学号 / 扣分统计收敛（不丢统计）。
    func submitRenewStudentNo(
        gradeCode: String, classCode: String, seatNo: String
    ) async throws {
        // 提交在途若登出 / 切到别的用户，成功返回后不把结果写到别人身上。
        let tokenAtStart = authToken
        _ = try await StudentRenewalAPI.renewNumber(
            gradeCode: gradeCode, classCode: classCode, seatNo: seatNo
        )
        guard authToken == tokenAtStart else { throw CancellationError() }
        // 成功 → 即时清标记（顶部按钮立刻消失），再重拉 /me 让新学号 / 统计收敛。
        needsRenewal = false
        await loadMe()
        guard authToken == tokenAtStart else { throw CancellationError() }
        showToast("学籍番号を更新しました")
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
            case .upcoming: studyState = .active; studyTaps = []; showToast("Demo · 学習進行中（NFC で 2 回タップ）")
            case .active: studyState = .done; showToast("Demo · 学習終了")
            case .done: studyState = .idle; studyTaps = []; showToast("Demo · 学習対象外")
            }
        }
    #endif

    // MARK: - 学习 NFC 2 次签到 (system_features §7.3.3-6) — 2026-04-30 / 5-31 中场废止

    /// 学习出席已达成的 tap 集合（2 种类: start / end）
    @Published var studyTaps: Set<StudyTap> = []

    /// 現在の学習出席状態（studyTaps + studyState から導出）
    var studyAttendance: StudyAttendance {
        // 按 start / end 两个 tap 集合判定状态（§7.3.6 异常表，删中场后）
        let s = studyTaps.contains(.start)
        let e = studyTaps.contains(.end)
        // 学习未开始 → idle
        if studyState == .idle || studyState == .upcoming { return .idle }
        // 两次都碰到 → 绿（时间内）
        if s && e { return .green }
        // 没碰开始却碰了结束 → 不一致 = 异常
        if !s && e { return .abnormal }
        // 已结束(done)：时段已过、不可能再「进行中」
        if studyState == .done {
            // 碰了开始没碰结束 → 异常（两次没齐、需老师手动判，§7.3.6）
            if s && !e { return .abnormal }
            // 一次没碰（!s && !e）→ 缺席（§7.3.6 第 1 行）
            return .red
        }
        // 进行中(active)且只碰了开始 → 进行中
        if s && !e { return .progressing }
        // 进行中但一次没碰 = tap 0
        return .none
    }

    /// 何回目の tap を期待しているか（next tap）— UI で次のステップを案内
    var nextStudyTap: StudyTap? {
        if !studyTaps.contains(.start) { return .start }
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

    // MARK: - 包裹通知（IX-009 真数据源 · GET /api/v1/front-desk/mine）

    //
    // 学生自己的宅配（包裹）。生产构建聚合进通知中心「宅配」标签 + 铃铛未読 badge。
    // 演示构建不拉真后端。模型 + 拉取都内联在本文件 —— 多会话并行时不碰公共网络层文件
    // （NetworkModels.swift / Endpoints），降低跟「申请表单簇」会话的撞车风险。

    /// 通知中心「宅配」数据源 — 当前学生的包裹缓存（loadMyPackages 拉真后端填）。
    @Published var packages: [FrontDeskItemBrief] = []

    /// GET /api/v1/front-desk/mine 返回的单个包裹（只取通知需要的字段、对齐后端 FrontDeskItemOut）。
    struct FrontDeskItemBrief: Decodable, Identifiable {
        let id: UUID
        let kind: String
        let description: String
        let location: String? // 保管場所（后端 FrontDeskItem.location；宅配詳細页用）
        let status: String // pending / notified / picked_up / expired / discarded
        // datetime 用 Date —— 后端统一输出带 +09:00 日本时间（TZDateTime），APIClient.decodeISO8601Date 直接解码。
        // 跟相邻公告(AnnouncementBrief)同方针，全走健壮解码器。
        let createdAt: Date
        let notifiedAt: Date?

        enum CodingKeys: String, CodingKey {
            case id, kind, description, location, status
            case createdAt = "created_at"
            case notifiedAt = "notified_at"
        }
    }

    /// 把包裹缓存映射成通知卡（type「宅配」→ 通知中心「宅配」标签下显示）。
    /// - id 用 -(10_000_000+idx)：跟公告 -(idx+1) / push ≥1000 三段都不相撞
    ///   （偏移量取够大 —— 公告要 1000 万条才会追到包裹区，实际不可能，codex 第二轮 minor）。
    /// - 未読 = 还没取走（pending / notified）；picked_up 等终态视为已読。
    private var packageNotifications: [NotificationItem] {
        packages.enumerated().map { idx, p in
            NotificationItem(
                id: -(10_000_000 + idx),
                type: "宅配",
                title: p.status == "picked_up" ? "荷物を受け取りました" : "荷物が届いています",
                time: Self.notifTimeLabel(p.notifiedAt ?? p.createdAt),
                body: p.description,
                unread: p.status == "pending" || p.status == "notified"
            )
        }
    }

    /// 拉当前学生的包裹（生产构建用）。带令牌守卫 —— 登出 / 切用户不写回旧用户的包裹。
    @MainActor
    func loadMyPackages() async {
        let tokenAtStart = authToken
        do {
            let items: [FrontDeskItemBrief] = try await APIClient.shared.get(
                path: "/api/v1/front-desk/mine"
            )
            guard authToken == tokenAtStart else { return }
            packages = items
        } catch {
            // 拉失败不阻塞通知中心其他源 —— 静默，下次刷新再试。
        }
    }

    // MARK: - 掃除提出履历（功能① · GET /api/v1/cleaning/me）

    /// 当前学生的清扫提出履历缓存（生产构建用，loadCleaningHistory 拉真后端填）。
    @Published var cleaningHistory: [CleaningAssignmentOut] = []

    /// 拉当前学生的清扫履历（按计划日倒序）。带令牌守卫 —— 登出 / 切用户不写回旧用户数据。
    @MainActor
    func loadCleaningHistory() async {
        let tokenAtStart = authToken
        do {
            let items = try await CleaningAPI.listMine()
            guard authToken == tokenAtStart else { return }
            cleaningHistory = items
        } catch {
            // 拉失败静默，下次进页面再试。
        }
    }

    // MARK: - 点歌一览（功能④ · GET /api/v1/songs）

    /// 点歌一览缓存（生产构建用，loadSongs 拉真后端填；后端已新→旧排序）。
    @Published var songRequests: [SongRequestOut] = []

    /// 拉点歌一览（生产构建用）。带令牌守卫 —— 登出 / 切用户不写回旧用户数据。
    @MainActor
    func loadSongs() async {
        let tokenAtStart = authToken
        do {
            let items = try await SongsAPI.list()
            guard authToken == tokenAtStart else { return }
            songRequests = items
        } catch {
            // 拉失败静默，下次进页面再试。
        }
    }

    // MARK: - 遗失物一览（功能⑤ · GET /api/v1/lost-found）

    /// 遗失物一览缓存（生产构建用，loadLostFound 拉真后端填；后端已新→旧排序）。
    @Published var lostFound: [LostFoundOut] = []

    /// 拉遗失物一览（生产构建用）。带令牌守卫 —— 登出 / 切用户不写回旧用户数据。
    @MainActor
    func loadLostFound() async {
        let tokenAtStart = authToken
        do {
            let items = try await LostFoundAPI.list()
            guard authToken == tokenAtStart else { return }
            lostFound = items
        } catch {
            // 拉失败静默，下次进页面再试。
        }
    }

    // MARK: - 个人 profile：点呼事件 + 减点事件（功能⑦⑧ · GET /students/{id}/profile）

    /// 点呼事件缓存（功能⑦ 点呼履历，生产构建用）。
    @Published var myRollcallEvents: [ProfileRollCallEntry] = []

    /// 减点事件缓存（功能⑧ 減点明細，生产构建用）。
    @Published var myDemeritEvents: [ProfileDemeritEntry] = []

    /// 拉本人 profile（功能⑦⑧共用：一次 GET /students/{id}/profile 同时填点呼 + 减点两块）。
    /// 带令牌守卫。冷启动时 loadMe 异步未完成 → myStudentId 还是 nil，这里先补拉一次 loadMe，
    /// 否则点呼/减点页 .task 只触发一次、profile 永远拉不到（codex 复审 major-4）。
    @MainActor
    func loadMyProfile() async {
        let tokenAtStart = authToken
        if myStudentId == nil {
            await loadMe()
            guard authToken == tokenAtStart else { return }
        }
        guard let sid = myStudentId else { return }
        do {
            let out = try await StudentProfileAPI.profile(studentId: sid)
            guard authToken == tokenAtStart else { return }
            myRollcallEvents = out.rollcall_events
            myDemeritEvents = out.demerit_events
        } catch {
            // 拉失败静默，下次进页面再试。
        }
    }

    /// 通知中心显示用。
    /// - 演示构建：push（接通前空）+ SEED.notifications fixture，撑住演示叙事。
    /// - 生产构建：push + 真公告映射（announcementNotifications），不再泄漏 SEED 假通知（IX-009）。
    ///   审批结果 / 包裹通知聚合见 handoff §7.3（待拍板：申请列表未在 AppStore 缓存 + 后端无已读态）。
    var allNotifications: [NotificationItem] {
        #if DEMO
            return pushNotifications + SEED.notifications
        #else
            return pushNotifications + announcementNotifications + packageNotifications
        #endif
    }

    /// IX-009：把真公告缓存（AnnouncementsAPI 拉来的 announcements）映射成通知卡。
    /// - type「お知らせ」：通知中心「すべて」标签下显示；未読 = 公告未読 → 驱动铃铛 badge。
    /// - id 用负数（按列表序）—— push 的 id 是正数（≥1000），两者绝不相撞。
    private var announcementNotifications: [NotificationItem] {
        announcements.enumerated().map { idx, a in
            NotificationItem(
                id: -(idx + 1),
                type: "お知らせ",
                title: a.title,
                time: Self.notifTimeLabel(a.createdAt),
                body: a.bodySummary,
                unread: !a.isRead
            )
        }
    }

    /// 通知卡时刻显示：JST「M/d HH:mm」。
    private static func notifTimeLabel(_ d: Date) -> String {
        let f = DateFormatter()
        f.locale = Locale(identifier: "ja_JP")
        f.timeZone = TimeZone(identifier: "Asia/Tokyo")
        f.dateFormat = "M/d HH:mm"
        return f.string(from: d)
    }

    /// 进入通知中心时刷新通知来源。生产拉真公告列表 + 未読数；演示构建不动（用 SEED）。
    func refreshNotificationSources() async {
        #if !DEMO
            try? await loadAnnouncementList()
            await loadAnnouncementUnreadCount()
            await loadMyPackages()
        #endif
    }

    /// 未読数（home greetingRow bell badge 用）
    var unreadNotificationCount: Int {
        #if DEMO
            return allNotifications.filter { $0.unread }.count
        #else
            // 生产：announcements 列表是懒加载的（只在通知/公告页 .task 拉），首屏 Home 可能为空 →
            // badge 改用后端真实未読数 announcementUnreadCount（loadMe 登录/启动即拉）+ push 未読，
            // 不依赖 announcements 列表是否已加载（IX-009 修复）。
            return pushNotifications.filter { $0.unread }.count + announcementUnreadCount
                + packageNotifications.filter { $0.unread }.count
        #endif
    }

    // MARK: - APNs 设备令牌注册（IX-009 push 接通准备）

    //
    // AppDelegate 向苹果注册成功后拿到 deviceToken（设备唯一推送地址），调本方法上报后端
    // POST /api/v1/notifications/device-token。后端 push.py 之后按这些 token 群发推送。
    // ⚠️ 真机收推送还需 itsuki 在 Apple Developer 后台申请 APNs 证书(.p8) 配到后端凭证；
    //    entitlements 的 aps-environment 已就绪、不用改 project.yml。

    /// 最近一次从 APNs 拿到的 deviceToken。**上报成功后不清空** —— 切换用户后由 loadMe 再 flush 一次，
    /// 把设备重新绑定到当前登录学生（codex Finding 4：原来上报成功就清空，A 登出 B 登入同一设备不重报、
    /// 后端 token 仍归 A、A 的推送会打到 B 的设备）。后端 device-token upsert 本就会把归属转给当前学生。
    private var deviceToken: String?

    /// 去重：(令牌, 当时 authToken) 已成功上报过就跳过 —— 换用户 / 重登 authToken 会变 → 触发重报。
    private var reportedDeviceToken: String?
    private var reportedForAuthToken: String?

    /// AppDelegate 拿到 deviceToken 后调 —— 存下并尝试上报（未登录则等登录后由 flush 补报）。
    @MainActor
    func registerDeviceToken(_ token: String) async {
        deviceToken = token
        await flushDeviceTokenIfPossible()
    }

    /// 把 deviceToken 发给后端。未登录 / 失败则保留，下次登录或启动再试。
    /// 登录成功（loadMe）后也调一次 —— 补报启动时还没登录就拿到的 token + 切换用户后重新绑定设备。
    @MainActor
    func flushDeviceTokenIfPossible() async {
        #if DEMO
            return // 演示构建不连后端、不上报 token
        #else
            guard let token = deviceToken, let auth = authToken else { return } // 未登录，留着等登录后再报
            // 同一令牌已为当前会话(authToken)上报过 → 跳过，避免每次 loadMe 重复上报
            if token == reportedDeviceToken, auth == reportedForAuthToken { return }
            struct Body: Encodable {
                let platform: String
                let token: String
            }
            struct Res: Decodable { let created: Bool }
            do {
                let _: Res = try await APIClient.shared.post(
                    path: "/api/v1/notifications/device-token",
                    body: Body(platform: "ios", token: token)
                )
                reportedDeviceToken = token
                reportedForAuthToken = auth
            } catch {
                // 失败不记录 reported*，下次登录 / 启动再试。
            }
        #endif
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
    case end // 21:45 学习结束（itsuki 2026-05-31：废除中场 tap，简化成开始 / 结束 2 次）
}

/// 出席状態（amber Card / マイページ で表示）
enum StudyAttendance: String {
    case idle // 学習時間外
    case none // active だが 0 tap
    case progressing // 1 tap 済（通常進行中）
    case green // 两次 tap 完成 = 时间内
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
    let tapLabel: String // 例："学習開始" / "学習終了"
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
            .init(date: "2026-04-29", tapKind: .start, tapLabel: "学習開始", timeHM: "19:37", note: nil),
            .init(date: "2026-04-28", tapKind: .end, tapLabel: "学習終了", timeHM: "21:45", note: nil),
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
