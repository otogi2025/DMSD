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

    /// 拼 M/W 前缀 → 完整 room_no（backend §5.0 编码规则）。
    /// 判定逻辑抽到纯函数 assembleRoomNo（可单测，见 RoomAssemblyTests）；本属性只做参数转发。
    var computedRoomNo: String {
        RegistrationDraft.assembleRoomNo(suffix: room_no_suffix, gender: gender)
    }

    /// 从 room_no_suffix 前缀 + gender 推 dorm_unit（§5.0 房号编码）。
    /// 判定逻辑抽到纯函数 dormUnit（可单测）；本属性只做参数转发。
    var computedDormUnit: Int {
        RegistrationDraft.dormUnit(suffix: room_no_suffix, gender: gender)
    }

    /// 纯函数：房号数字后缀 + 性别 → 完整 room_no（§5.0 编码规则）。抽出便于单测，行为与旧 computedRoomNo 逐字一致。
    /// - suffix 空 = 上层 UI 漏了校验 → 返回空串让 backend 拒绝（room_no 必填字段）。
    /// - IX-014: suffix 首位已是字母（如 "A5"）= 已含楼栋标识，原样返回、不再加 M/W 前缀（否则变 "MA5"）。
    ///   ⭐ A 前缀 = 2 寮，由字母编码，绝不能被性别覆盖（6-17 五处散布 bug 的根因：判寮看字母前缀，不看性别/数字）。
    /// - 纯数字 suffix（如 "101"）才加前缀：male → "M"、其余（female）→ "W"。前缀只在这一处加，避免双前缀。
    static func assembleRoomNo(suffix: String, gender: String) -> String {
        guard !suffix.isEmpty else { return "" }
        if suffix.first?.isLetter == true { return suffix }
        let prefix = (gender == "male") ? "M" : "W"
        return prefix + suffix
    }

    /// 纯函数：房号后缀 + 性别 → dorm_unit（§5.0）。抽出便于单测，行为与旧 computedDormUnit 逐字一致。
    /// female → 4 寮；male 且 A 前缀房号（A1〜A12）→ 2 寮；其余 male → 1 寮。
    /// ⭐ 判寮看字母前缀，不看性别/数字 —— 旧逻辑用「数字首位 == 2」永远推不出 2 寮，
    /// 会导致 2 寮学生发 dorm_unit=1 + 不带 A 前缀的请求、被后端 422 拒绝（生产版整条注册流断）。
    static func dormUnit(suffix: String, gender: String) -> Int {
        if gender == "female" { return 4 }
        if suffix.first?.uppercased() == "A" { return 2 }
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
        f.timeZone = TimeZone(identifier: "Asia/Tokyo") // 固定 JST，与生日 DatePicker 时区一致，date-only 不随设备时区偏天
        return f.string(from: b)
    }
}

/// 账号关联字段的变更历史记录（MyInfo 编辑时 append）
struct ChangeLogEntry: Hashable, Identifiable {
    let id: UUID
    let at: Date // 变更时刻
    let field: String // 例: "grade" / "room"
    let label: String // 日语界面显示名: "学年" / "部屋番号"
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
                    studentNotifications = []
                    studentNotificationUnreadCount = 0
                    // IX-008 Batch 3: push 推送列表也要清 —— 否则 A 登出后 B 在同一进程登录，
                    // 会在通知中心看到 A 收到的推送（含減点 / 申請隐私）。feedNotifications /
                    // packageNotifications 是从 studentNotifications / packages 派生的计算属性，
                    // 那两个源已清、它们自动空；只有 pushNotifications 是存储属性需显式清。
                    pushNotifications = []
                    packages = []
                    studyLeaveCountThisMonth = 0
                    cleaningHistory = []
                    songRequests = []
                    lostFound = []
                    myRollcallEvents = []
                    myDemeritEvents = []
                    // codex m-1: 列表加载三态也要重置，否则下个登录用户短暂看到上个账号的失败 / 加载文案
                    profileState = .idle
                    cleaningHistoryState = .idle
                    songsState = .idle
                    lostFoundState = .idle
                    packagesState = .idle
                    notificationsState = .idle
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

    /// IX-008 + ios⑥: 各页显示当前用户统一走这个。
    /// 演示版：currentUser 拉到就用真的、否则 SEED.user 假人撑叙事。
    /// 生产版：拉到用真的；已登录但还没拉到 → User.placeholder 空白占位「—」（不回退演示假人，防泄漏给真实用户）；未登录 → SEED 占位过场。
    var displayUser: User {
        if let u = currentUser { return u }
        #if DEMO
            return SEED.user
        #else
            return isAuthenticated ? User.placeholder : SEED.user
        #endif
    }

    /// 生产构建已登录但 currentUser 还没拉到（displayUser 当前是 User.placeholder 占位）。演示版恒 false。
    /// HomeStubs amber 卡等读数值的地方靠它把占位的 0 显成「—」（占位的字符串字段已自带「—」，数值字段得 view 层判）。
    var profileIsPlaceholder: Bool {
        #if DEMO
            return false
        #else
            return isAuthenticated && currentUser == nil
        #endif
    }

    /// 列表加载三态（ios④ 上线缺口）：区分「加载中 / 加载失败 / 真没数据」，
    /// 防网断时把「有 5 条扣分」静默显示成「減点なし」。演示版不调 loadXxx → 状态保持 .idle 走原空态。
    enum ListLoadState: Equatable {
        case idle, loading, loaded
        case failed(String) // 携带用户友好错误文案
    }

    @Published var profileState: ListLoadState = .idle // 减点⑧+点呼⑦ 共用 loadMyProfile
    @Published var cleaningHistoryState: ListLoadState = .idle
    @Published var songsState: ListLoadState = .idle
    @Published var lostFoundState: ListLoadState = .idle
    @Published var packagesState: ListLoadState = .idle // NET-01: 宅配（包裹）列表三态（idle/loading/loaded/failed）
    @Published var notificationsState: ListLoadState = .idle // NET-02: 通知中心 feed 三态

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

    /// 集中处理「令牌过期 / 失效（401）」。
    /// 多个 load 方法（loadMyPackages / loadSongs / loadLostFound / loadMyProfile）原本把 401 吞进通用 catch、
    /// 不清令牌也不重登，用户卡在「取得に失敗」死循环。统一在它们的 catch 里先调本方法：
    /// 若 error 是 401 → 清令牌（authToken=nil 触发 didSet 清 Keychain + currentUser，RootView 据此跳登录页）并返回 true，
    /// 调用方据此直接 return、不再写失败态；否则返回 false，调用方按原逻辑处理非 401 错误。
    /// 跟 loadMe 的 401 处理对齐同一套机制（清 authToken 触发统一登出）。
    /// - Parameter tokenAtStart: 调用方进入时捕获的令牌，用于比对竞态 —— A 的旧请求在 A 登出、B 登录后才返 401 时，
    ///   不能误清掉 B 刚拿到的令牌（跟 loadMe IX-034 修复②同口径）。
    /// - Returns: true = 是 401（已尝试清令牌，调用方应 return）；false = 非 401，调用方继续原有错误处理。
    @MainActor
    @discardableResult
    func handleIfUnauthorized(_ error: Error, tokenAtStart: String?) -> Bool {
        guard case APIError.unauthorized = error else { return false }
        // 401 也比对令牌 —— 只在仍是当初那个登录令牌时才清，防误踢已换上的新用户。
        guard authToken == tokenAtStart else { return true }
        authToken = nil // didSet 清 Keychain + currentUser，RootView 跳登录页
        return true
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
                    // 罚扫对象 flag：优先后端实时算 needs_cleaning，缺省本地按 total_points>=4 兜底
                    // （needs_cleaning 是 Bool?，防后端字段名敲定前 / 旧后端没返时整段 summary 解码失败）。
                    mapped.needsCleaning = summary.needs_cleaning ?? (summary.total_points >= 4)
                }
                // IX-034: 再拉当月夜学習欠席届次数（按月真实数，替代纯内存累加 —
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
                // §7.13.1：登录 / 启动即拉学生通知 feed，让 Home 铃铛 badge 首屏含通知未読数
                // （feed 是进通知中心才刷的，不在这拉则首屏 badge 漏掉巴士/行事/通知公告的未読）。
                await loadStudentNotifications()
                // IX-009：登录 / 启动即拉包裹，让 Home 铃铛 badge 首屏含包裹未読。
                await loadMyPackages()
                // IX-009：补报启动时还没登录就拿到的 APNs deviceToken。
                await flushDeviceTokenIfPossible()
                // R-1/R-2：拉今日点呼场次，驱动首页点呼卡真实状态（idle/进行中/時間内/遅刻/欠席）
                await loadTodayRollcall()
                // 罚扫：拉本人罚扫安排，驱动主页「下次罚扫」小卡 + 履历页首屏
                await loadCleaningHistory()
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
                #if DEBUG
                    print("[loadMe] /students/me 拉取失败：\(error)")
                #endif
            }
        #endif
    }

    /// 后端 /me 响应（StudentMeOut）映射成 iOS User。/me 只给身份字段：
    /// - 统计（points / lateCount / absentCount）/me 没有 → 这里先填 0，loadMe 再拉 DisciplineAPI.mySummary 覆盖（IX-008b）
    /// - isStudyTarget（夜学習対象）/me 没这 flag → 默认 false（只有老师后台设的才是；
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

    /// Toast 自动清理的代次令牌：每次 showToast 自增，定时清理只在「自己仍是最新那条」时才置 nil。
    /// 防 2.2 秒内连续两次 showToast 时，旧 toast 的定时任务把后一个 toast 提前清掉（清单 #26）。
    private var toastGeneration: Int = 0

    /// 暗色模式 toggle（MySettings 控制）
    @AppStorage("isDark") var isDark: Bool = false

    /// 点呼倒计时（active 时，秒数）· Demo 期初始 180 秒
    @Published var rollCountdownSec: Int = 180

    /// 已签到时刻（done 时用）
    @Published var checkinAt: String? = nil

    /// 已签到判定（"時間内" / "遅刻"）
    @Published var checkinKind: String? = nil

    /// 今日「我所属寮」的点呼场次（GET /rollcall/me/today）。
    /// 生产版 rollState / 倒计时 / 「時間内」「遅刻」判定的真实数据源（R-1/R-2）；演示版空、走本地假状态机。
    @Published var todaySessions: [MyRollCallTodaySession] = []

    /// 账号关联字段的变更履歴（MyInfo 编辑时 append）
    /// production 版初始空、登录后从后端拉；demo 版有进级 placeholder seed。
    @Published var changeLog: [ChangeLogEntry] = {
        #if DEMO
            return [ChangeLogEntry(field: "grade", label: "学年", before: "高2", after: "高3")]
        #else
            return []
        #endif
    }()

    /// 记录字段变更（逐字段比对，before == after 则跳过）
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

    // MARK: - 学生通知中心 feed（2026-06-15 加，spec §7.13.1）

    //
    // 老师投稿 公告/巴士/行事 时勾「学生に通知する」(notify_students) 的内容，由后端统一聚合成
    // 一个 feed 返回（按学生可见范围过滤）。替代原「拉全部公告自映射成通知」(announcementNotifications)，
    // 改由后端单一真值 + notify_students 开关控制哪条进通知中心，也为将来 Android 复用同一接口铺路。

    /// 通知中心 feed 缓存（生产构建用；refreshNotificationSources / loadMe 拉真后端填）。
    @Published var studentNotifications: [StudentNotificationItem] = []

    /// feed 未読数 —— Home 铃铛 badge 用（loadMe 登录/启动即拉，首屏不依赖进通知中心）。
    @Published var studentNotificationUnreadCount: Int = 0

    /// 拉学生通知 feed（items + 未読数）。带令牌守卫，登出/切用户不写回旧用户数据。
    @MainActor
    func loadStudentNotifications() async {
        #if DEMO
            return // 演示构建用 SEED.notifications 撑叙事，不拉后端
        #else
            let tokenAtStart = authToken
            notificationsState = .loading
            do {
                let feed = try await StudentNotificationsAPI.feed()
                guard authToken == tokenAtStart else { return }
                studentNotifications = feed.items
                studentNotificationUnreadCount = feed.unreadCount
                notificationsState = .loaded
            } catch {
                // 401 → 集中清令牌触发重登；非 401 → 反映到 notificationsState 让通知中心显失败态。
                if handleIfUnauthorized(error, tokenAtStart: tokenAtStart) { return }
                guard authToken == tokenAtStart else { return } // 切用户/登出后不写回旧状态
                // NET-02: feed 拉取失败时显失败态（代表 feed 源失败），不再静默吞成「通知はありません」假空态。
                notificationsState = .failed(APIErrorPresenter.userMessage(for: error, fallback: "通知の取得に失敗しました"))
            }
        #endif
    }

    /// 标记一条 feed 通知已读（点通知卡片时调）。乐观更新：本条翻已読 + 未読数减 1。
    /// 公告写 announcement_reads / 巴士·行事写 student_notification_reads（后端幂等）。
    @MainActor
    func markStudentNotificationRead(kind: String, refId: UUID) async {
        #if DEMO
            return
        #else
            let tokenAtStart = authToken
            // 找不到 / 已是已读 → 不发重复请求
            guard let idx = studentNotifications.firstIndex(where: { $0.kind == kind && $0.refId == refId }),
                  !studentNotifications[idx].isRead else { return }
            do {
                try await StudentNotificationsAPI.markRead(kind: kind, refId: refId)
                guard authToken == tokenAtStart else { return }
                // await 后数组可能已变 → 重新定位再翻已読
                if let i = studentNotifications.firstIndex(where: { $0.kind == kind && $0.refId == refId }),
                   !studentNotifications[i].isRead
                {
                    studentNotifications[i].isRead = true
                    studentNotificationUnreadCount = max(0, studentNotificationUnreadCount - 1)
                }
            } catch {
                if handleIfUnauthorized(error, tokenAtStart: tokenAtStart) { return }
                // 非 401：标已读失败不影响显示，静默（下次刷新 feed 会带回真实已読态）
            }
        #endif
    }

    /// 拉未读数
    func loadAnnouncementUnreadCount() async {
        #if DEMO
            announcementUnreadCount = SEED.announcements.filter { !$0.isRead }.count
            return
        #else
            let tokenAtStart = authToken
            do {
                let res = try await AnnouncementsAPI.unreadCount()
                // IX-009：登出 / 切用户后不写回旧用户的未読数（防 badge 串号）。
                guard authToken == tokenAtStart else { return }
                announcementUnreadCount = res.unreadCount
            } catch {
                // 拉失败不阻塞主页其他功能 — 静默忽略，下次刷新再试
            }
        #endif
    }

    /// 拉列表（一覧 view 进入时调）
    func loadAnnouncementList() async throws {
        #if DEMO
            // 演示版用 SEED 假公告，不连后端（否则演示无网 / 无真令牌时整列表报通信错误）
            announcements = SEED.announcements
            return
        #else
            let tokenAtStart = authToken
            let res = try await AnnouncementsAPI.list()
            // IX-009：登出 / 切用户后不写回旧用户的公告列表（防上一个人的公告残留到下一个人）。
            guard authToken == tokenAtStart else { return }
            announcements = res.items
        #endif
    }

    /// 拉详情（详情 view 进入时调；自动写已读 → backend 下次 list 返回 isRead=true）
    func loadAnnouncementDetail(id: String) async throws {
        #if DEMO
            // 演示版从 SEED 取详情（id 是 UUID 大写串，SEED 字典按小写键查）
            if let d = SEED.announcementDetails[id.lowercased()] {
                announcementDetails[id] = d
            }
            // demo 也把列表那条翻已读 + 同步未读数（让 badge 实时减）
            if let idx = announcements.firstIndex(where: { $0.id.uuidString.caseInsensitiveCompare(id) == .orderedSame }) {
                let old = announcements[idx]
                announcements[idx] = AnnouncementBrief(
                    id: old.id, title: old.title, bodySummary: old.bodySummary,
                    scope: old.scope, authorTeacherId: old.authorTeacherId,
                    authorTeacherName: old.authorTeacherName,
                    createdAt: old.createdAt, updatedAt: old.updatedAt,
                    isRead: true, replyCount: old.replyCount
                )
            }
            announcementUnreadCount = announcements.filter { !$0.isRead }.count
            return
        #else
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
        #endif
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
        toastGeneration &+= 1
        let gen = toastGeneration
        withAnimation { toast = text }
        Task {
            try? await Task.sleep(nanoseconds: 2_200_000_000)
            await MainActor.run {
                // 自己已被后一条 toast 顶替（gen 落后）→ 不清，交给最新那条的任务清。
                guard self.toastGeneration == gen else { return }
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

    // 生产版签到不经本类提交：iOS 只用 ST25DVWriter 把载荷写进墙上 ST25DV 邮箱，
    // 点呼机读走后由它上报后端；本端签到状态一律由 my_checked_in_at 经
    // refreshRollStateFromSessions 反向驱动（2026-06-02 架构反转）。下面仅演示版用。

    #if DEMO
        /// done 表示自动恢复 idle 的任务（避免重复持有）
        /// 仅演示版：本地 mock 点呼状态机用。生产版点呼状态由后端 my_checked_in_at 经
        /// refreshRollStateFromSessions 驱动，绝不本地置 done（否则被每秒 timer 覆盖回去，体验像签到失败）。
        private var autoDismissDoneTask: Task<Void, Never>?

        /// NFC tap 成功后调（仅演示版本地假确认；生产版不调它——权威判定在点呼机 + 后端）
        func recordCheckin() {
            let fmt = DateFormatter()
            fmt.dateFormat = "HH:mm"
            fmt.timeZone = TimeZone(identifier: "Asia/Tokyo")
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
    #endif

    // A-030 / A-033 (2026-05-21): cycleDemoRollState() 已删
    // memory project_demo_scaffolds_to_remove_before_v1.md #1, #15
    // 接 backend event 驱动后 rollState 由 server 推送，不再 demo 循环

    /// HomeView 的 countdownTimer 每秒调一次。
    func tickCountdown() {
        #if DEMO
            // 演示版：本地假状态机倒计时（给宿舍管理员演示用）
            guard rollState == .active, rollCountdownSec > 0 else { return }
            rollCountdownSec -= 1
        #else
            // 生产版（R-1/R-2）：按今日真实点呼场次 + 当前时刻重算状态，
            // idle→进行中→欠席 自动流转、倒计时按「時間内」截止真实递减，不再本地写死。
            refreshRollStateFromSessions()
        #endif
    }

    /// 登录 / 启动后拉今日「我所属寮」的点呼场次（演示版不拉，保留本地假状态机）。
    func loadTodayRollcall() async {
        #if DEMO
            return
        #else
            guard let tokenAtStart = authToken else { return }
            do {
                let rows = try await RollCallAPI.myToday()
                guard authToken == tokenAtStart else { return } // await 后换人则丢弃
                todaySessions = rows
                refreshRollStateFromSessions()
            } catch {
                if handleIfUnauthorized(error, tokenAtStart: tokenAtStart) { return }
                // 非 401：保持现状（不显假数据）；打日志便于开发期发现字段漂移
                #if DEBUG
                    print("[loadTodayRollcall] /rollcall/me/today 拉取失败：\(error)")
                #endif
            }
        #endif
    }

    /// 时间窗状态机的纯判定结果（不碰 @Published / 时钟 / 格式化 — 方便单测）。
    struct RollStateDecision: Equatable {
        var rollState: RollState
        var checkinKind: String? // 「時間内」/「遅刻」/ nil
        var checkedInAt: Date? // 已签到时刻原始值（格式化留给调用方）；未签到 nil
        var countdownSec: Int? // active 时到「時間内」截止的倒计时秒；其余状态 nil（不改原值）
    }

    /// 纯函数：从场次列表 + 注入的「现在」派生点呼状态。无副作用、不读真实时钟 → 可单测（R-1/R-2 时间窗状态机）。
    /// 选「当前进行中场次」(now 落在 window_start..auto_end)；否则最近的未来场次做预告(idle)。
    /// nonisolated：纯值计算、不碰主线程状态 → 测试可在非主线程同步调用（AppStore 本身是 @MainActor）。
    nonisolated static func decideRollState(sessions: [MyRollCallTodaySession], now: Date) -> RollStateDecision {
        let current = sessions.first {
            now >= $0.scheduled_window_start_at && now <= $0.scheduled_auto_end_at
        }
        let upcoming = sessions
            .filter { now < $0.scheduled_window_start_at }
            .min { $0.scheduled_window_start_at < $1.scheduled_window_start_at }
        guard let s = current ?? upcoming else {
            // 本日我寮无点呼 → 安全落 idle（点呼卡显减点预告、不显假倒计时）
            return RollStateDecision(rollState: .idle, checkinKind: nil, checkedInAt: nil, countdownSec: nil)
        }
        // 已签到/已结算 → 按后端 my_status 完整映射（ios#101 契约收口）。
        // 后端自动结算/老师改判会给 absent/exempt_range 也写 checked_in_at（rollcall.py _settle），
        // 故不能只凭 my_checked_in_at 非空就当"按时签到"。「時間内」只留给 present。
        if let at = s.my_checked_in_at {
            switch s.my_status {
            case "present":
                return RollStateDecision(rollState: .done, checkinKind: "時間内", checkedInAt: at, countdownSec: nil)
            case "late":
                return RollStateDecision(rollState: .done, checkinKind: "遅刻", checkedInAt: at, countdownSec: nil)
            case "absent":
                // 被结算欠席：显欠席态，不是签到、不显时刻
                return RollStateDecision(rollState: .absent, checkinKind: nil, checkedInAt: nil, countdownSec: nil)
            case "exempt_range":
                // 承認済出寮願免除：良性完了，复用 done 但文案「免除」、不显假签到时刻
                return RollStateDecision(rollState: .done, checkinKind: "免除", checkedInAt: nil, countdownSec: nil)
            default:
                // 未知状态：保守显 done 但不猜判定文案（绝不兜底「時間内」），仍显真实时刻
                return RollStateDecision(rollState: .done, checkinKind: nil, checkedInAt: at, countdownSec: nil)
            }
        }
        // 未签到，按时间窗判定
        if now < s.scheduled_window_start_at {
            return RollStateDecision(rollState: .idle, checkinKind: nil, checkedInAt: nil, countdownSec: nil) // 下次点呼预告
        } else if now <= s.scheduled_late_end_at {
            // 受付中（含遅刻段）→ active；倒计时到「時間内」截止时刻
            return RollStateDecision(
                rollState: .active,
                checkinKind: nil,
                checkedInAt: nil,
                countdownSec: max(0, Int(s.scheduled_on_time_end_at.timeIntervalSince(now)))
            )
        } else {
            // 超过迟到截止仍未签到 → 欠席
            return RollStateDecision(rollState: .absent, checkinKind: nil, checkedInAt: nil, countdownSec: nil)
        }
    }

    /// 从 todaySessions + 当前时刻派生 rollState / checkinAt / checkinKind / rollCountdownSec。
    /// 判定逻辑全在纯函数 decideRollState 里（可单测）；本方法只负责取真实时钟 + 写 @Published + 格式化。
    func refreshRollStateFromSessions() {
        #if DEMO
            return
        #else
            let d = Self.decideRollState(sessions: todaySessions, now: Date())
            // 每秒由 tickCountdown 调一次。@Published 即便赋同值也会触发 objectWillChange → 整树重绘，
            // 故赋值前做相等判断：idle 态四值都不变 → 一次都不写 → 不重绘；active 态只 countdown 真递减。
            if rollState != d.rollState { rollState = d.rollState }
            if checkinKind != d.checkinKind { checkinKind = d.checkinKind }
            let newCheckinAt = d.checkedInAt.map { Self.jstHHmm.string(from: $0) }
            if checkinAt != newCheckinAt { checkinAt = newCheckinAt }
            if let sec = d.countdownSec, rollCountdownSec != sec { rollCountdownSec = sec }
        #endif
    }

    /// HH:mm（JST）— 点呼签到时刻显示用
    private static let jstHHmm: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "HH:mm"
        f.timeZone = TimeZone(identifier: "Asia/Tokyo")
        return f
    }()

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

    /// 夜学習欠席届 提交（system_features §7.3.5）— 后端通过后 += 1、> 3 触发提醒
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
            showToast("今月の欠席はすでに\(studyLeaveCountThisMonth)回目です。体調管理に十分気をつけてください。")
        } else {
            showToast("夜学習欠席届を提出しました")
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
        showToast("アカウント番号を更新しました")
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
            case .idle: studyState = .upcoming; studyCountdownSec = 600; showToast("Demo · 夜学習 10 分前 (残り 10:00)")
            case .upcoming: studyState = .active; studyTaps = []; showToast("Demo · 夜学習進行中（NFC で 2 回タップ）")
            case .active: studyState = .done; showToast("Demo · 夜学習終了")
            case .done: studyState = .idle; studyTaps = []; showToast("Demo · 夜学習対象外")
            }
        }
    #endif

    // MARK: - 学习 NFC 2 次签到 (system_features §7.3.3-6) — 2026-04-30 / 5-31 中场废止

    /// 学习出席已达成的 tap 集合（2 种类: start / end）
    @Published var studyTaps: Set<StudyTap> = []

    /// 現在の夜学習出席状態（studyTaps + studyState から導出）
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
            case .start: return "夜学習開始"
            case .end: return "夜学習終了"
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

    /// マイページ「夜学習履歴」用 — production 空、demo 加 fixture seed
    /// TODO[backend]: 登录后从 GET /study/attendance/mine 拉真数据
    @Published var studyHistory: [StudyHistoryEntry] = {
        #if DEMO
            return StudyHistoryEntry.demoSeed
        #else
            return []
        #endif
    }()

    private static func nowHM() -> String {
        let f = DateFormatter()
        f.dateFormat = "HH:mm"
        f.locale = Locale(identifier: "ja_JP")
        f.timeZone = TimeZone(identifier: "Asia/Tokyo")
        return f.string(from: Date())
    }

    private static func todayJa() -> String {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        f.locale = Locale(identifier: "ja_JP")
        f.timeZone = TimeZone(identifier: "Asia/Tokyo")
        return f.string(from: Date())
    }

    // MARK: - 登录锁定升级 (内部账号规则 + 4-22 拍板的 5 阶段)

    //
    // 失败次数 → 锁定时长: 1=30秒 / 2=1分 / 3=5分 / 4=30分 / 5=1小时 / 6+=永久
    // 永久锁定须联系宿舍管理员解除。下次登录成功后 counter 重置。

    /// 登录失败累计次数（永久锁定为 6 以上）
    @Published var loginFailCount: Int = 0

    /// 各锁定阶段时长（秒数，与 failCount 对应 — 6+ 为 nil = 永久）
    static let lockoutDurations: [Int] = [30, 60, 300, 1800, 3600]

    /// 当前锁定阶段的秒数（永久 → nil）
    var currentLockoutSeconds: Int? {
        let idx = loginFailCount - 1
        guard idx >= 0 else { return nil }
        if idx < Self.lockoutDurations.count {
            return Self.lockoutDurations[idx]
        }
        return nil // 永久
    }

    /// 当前锁定阶段的显示文字串
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

    /// 下一阶段的显示文字串（已是最后阶段则为 nil）
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

    /// 登录失败时调用 — failCount += 1
    func recordLoginFailure() {
        loginFailCount += 1
    }

    /// 登录成功 / 锁定到期 时调用 — 重置计数器
    func resetLoginFailures() {
        loginFailCount = 0
    }

    // MARK: - Push 通知 listener (system_features §7.13 R1 例外)

    //
    // TODO[backend]: 真 production 由 APNs delegate（AppDelegate.didReceiveRemoteNotification）
    //   → 解析 payload → 调 handleIncomingPush(...) 把通知 insert 到 pushNotifications。
    // 当前是接入前的 store：APNs 接通前 pushNotifications 空。

    /// 收到真实 push 后动态追加的通知（SEED.notifications 是静态初始占位数据）
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
        let itemCount: Int // 宅配件数（后端 item_count；2026-06-14 加）
        let status: String // pending / notified / picked_up / expired / discarded
        // datetime 用 Date —— 后端统一输出带 +09:00 日本时间（TZDateTime），APIClient.decodeISO8601Date 直接解码。
        // 跟相邻公告(AnnouncementBrief)同方针，全走健壮解码器。
        let createdAt: Date
        let notifiedAt: Date?

        enum CodingKeys: String, CodingKey {
            case id, kind, description, location, status
            case itemCount = "item_count"
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
                title: p.status == "picked_up"
                    ? "荷物を受け取りました"
                    : "荷物が届いています（\(p.itemCount)件）",
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
        packagesState = .loading
        do {
            let items: [FrontDeskItemBrief] = try await APIClient.shared.get(
                path: "/api/v1/front-desk/mine"
            )
            guard authToken == tokenAtStart else { return }
            packages = items
            packagesState = .loaded
        } catch {
            // 401 令牌过期 → 集中清令牌触发重登（否则用户卡在静默失败、永远刷不出包裹）。
            if handleIfUnauthorized(error, tokenAtStart: tokenAtStart) { return }
            guard authToken == tokenAtStart else { return } // 切用户/登出后不写回旧状态
            // NET-01: 非 401（网络 / 解码失败）→ 反映到 packagesState 让宅配页显失败态，不再静默吞成假空态。
            // 只动 packagesState、不碰通知中心其他源（refreshNotificationSources 复用本方法）。
            packagesState = .failed(APIErrorPresenter.userMessage(for: error, fallback: "荷物の取得に失敗しました"))
        }
    }

    // MARK: - 罚扫提出履历（功能① · GET /api/v1/cleaning/me）

    /// 当前学生的罚扫安排 + 检查结果缓存（生产构建用，loadCleaningHistory 拉真后端填）。
    @Published var cleaningHistory: [CleaningAssignmentOut] = []

    /// 拉当前学生的罚扫履历（后端按计划时刻倒序）。带令牌守卫 —— 登出 / 切用户不写回旧用户数据。
    @MainActor
    func loadCleaningHistory() async {
        let tokenAtStart = authToken
        cleaningHistoryState = .loading
        do {
            let items = try await CleaningAPI.listMine()
            guard authToken == tokenAtStart else { return }
            cleaningHistory = items
            cleaningHistoryState = .loaded
        } catch {
            // 401 令牌过期 → 集中清令牌触发重登（跟 loadSongs 对齐）。
            if handleIfUnauthorized(error, tokenAtStart: tokenAtStart) { return }
            guard authToken == tokenAtStart else { return } // 切用户/登出后不写回旧状态
            cleaningHistoryState = .failed(APIErrorPresenter.userMessage(for: error, fallback: "罰則清掃の取得に失敗しました"))
        }
    }

    /// 主页「下次罚扫」小卡数据：取未完成、scheduled_at 最早的一条；没有则 nil（小卡不显示）。
    var nextCleaning: NextCleaningInfo? {
        #if DEMO
            // 演示：SEED.cleaning 里挑「未完成」的一条
            guard let c = SEED.cleaning.first(where: { $0.status == "未提出" || $0.status == "未完成" }) else { return nil }
            return NextCleaningInfo(dateText: c.dateLabel, timeText: c.timeLabel, area: c.range)
        #else
            // 正式：cleaningHistory 里未完成（assigned/done，未 passed/failed/skipped）+ scheduled_at 最早
            let pending = cleaningHistory
                .filter { $0.status == "assigned" || $0.status == "done" }
                .sorted { $0.scheduled_at < $1.scheduled_at }
            guard let c = pending.first else { return nil }
            return NextCleaningInfo(
                dateText: Self.jstMonthDay.string(from: c.scheduled_at),
                timeText: Self.jstHour.string(from: c.scheduled_at),
                area: c.area
            )
        #endif
    }

    // 下面 3 个 formatter 标 nonisolated —— AppStore 是 @MainActor，静态属性默认继承隔离，
    // 但 CleaningDisplay.init(real:) 是普通 struct init（非隔离上下文）要读它们。
    // DateFormatter 不可变引用、只读用，跨上下文安全，故 nonisolated。

    /// M月d日（JST）— 「下次罚扫」小卡日期
    nonisolated static let jstMonthDay: DateFormatter = {
        let f = DateFormatter()
        f.locale = Locale(identifier: "ja_JP")
        f.dateFormat = "M月d日"
        f.timeZone = TimeZone(identifier: "Asia/Tokyo")
        return f
    }()

    /// H時mm分（JST）— 「下次罚扫」小卡时刻（带分钟，老师可排 19:30）
    nonisolated static let jstHour: DateFormatter = {
        let f = DateFormatter()
        f.locale = Locale(identifier: "ja_JP")
        f.dateFormat = "H時mm分"
        f.timeZone = TimeZone(identifier: "Asia/Tokyo")
        return f
    }()

    /// M月d日 H時mm分（JST）— 罚扫履历行日期+时刻（带分钟）
    nonisolated static let jstDateTimeLabel: DateFormatter = {
        let f = DateFormatter()
        f.locale = Locale(identifier: "ja_JP")
        f.dateFormat = "M月d日 H時mm分"
        f.timeZone = TimeZone(identifier: "Asia/Tokyo")
        return f
    }()

    // MARK: - 点歌一览（功能④ · GET /api/v1/songs）

    /// 点歌一览缓存（生产构建用，loadSongs 拉真后端填；后端已新→旧排序）。
    @Published var songRequests: [SongRequestOut] = []

    /// 拉点歌一览（生产构建用）。带令牌守卫 —— 登出 / 切用户不写回旧用户数据。
    @MainActor
    func loadSongs() async {
        let tokenAtStart = authToken
        songsState = .loading
        do {
            let items = try await SongsAPI.list()
            guard authToken == tokenAtStart else { return }
            songRequests = items
            songsState = .loaded
        } catch {
            // 401 令牌过期 → 集中清令牌触发重登（否则卡在「取得に失敗」死循环、重试也只会再 401）。
            if handleIfUnauthorized(error, tokenAtStart: tokenAtStart) { return }
            guard authToken == tokenAtStart else { return }
            songsState = .failed(APIErrorPresenter.userMessage(for: error, fallback: "リクエスト曲の取得に失敗しました"))
        }
    }

    // MARK: - 遗失物一览（功能⑤ · GET /api/v1/lost-found）

    /// 遗失物一览缓存（生产构建用，loadLostFound 拉真后端填；后端已新→旧排序）。
    @Published var lostFound: [LostFoundOut] = []

    /// 拉遗失物一览（生产构建用）。带令牌守卫 —— 登出 / 切用户不写回旧用户数据。
    @MainActor
    func loadLostFound() async {
        let tokenAtStart = authToken
        lostFoundState = .loading
        do {
            let items = try await LostFoundAPI.list()
            guard authToken == tokenAtStart else { return }
            lostFound = items
            lostFoundState = .loaded
        } catch {
            // 401 令牌过期 → 集中清令牌触发重登（否则卡在「取得に失敗」死循环、重试也只会再 401）。
            if handleIfUnauthorized(error, tokenAtStart: tokenAtStart) { return }
            guard authToken == tokenAtStart else { return }
            lostFoundState = .failed(APIErrorPresenter.userMessage(for: error, fallback: "落とし物の取得に失敗しました"))
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
        profileState = .loading
        if myStudentId == nil {
            await loadMe()
            guard authToken == tokenAtStart else { return }
        }
        guard let sid = myStudentId else {
            // 拿不到学号（loadMe 失败 / 未登录）→ 算加载失败，让点呼/减点页显失败态而非「なし」
            profileState = .failed("学生情報の取得に失敗しました")
            return
        }
        do {
            let out = try await StudentProfileAPI.profile(studentId: sid)
            guard authToken == tokenAtStart else { return }
            myRollcallEvents = out.rollcall_events
            myDemeritEvents = out.demerit_events
            profileState = .loaded
        } catch {
            // 401 令牌过期 → 集中清令牌触发重登（否则点呼/减点页卡在「取得に失敗」死循环、重试也只会再 401）。
            if handleIfUnauthorized(error, tokenAtStart: tokenAtStart) { return }
            guard authToken == tokenAtStart else { return }
            profileState = .failed(APIErrorPresenter.userMessage(for: error, fallback: "点呼・減点情報の取得に失敗しました"))
        }
    }

    /// 通知中心显示用。
    /// - 演示构建：push（接通前空）+ SEED.notifications fixture，撑住演示叙事。
    /// - 生产构建：push + 学生通知 feed（feedNotifications）+ 包裹，不再泄漏 SEED 假通知（IX-009）。
    ///   §7.13.1：feed = 老师勾了「学生に通知する」的 公告/巴士/行事，替代原「拉全部公告自映射」announcementNotifications。
    var allNotifications: [NotificationItem] {
        #if DEMO
            return pushNotifications + SEED.notifications
        #else
            return pushNotifications + feedNotifications + packageNotifications
        #endif
    }

    /// §7.13.1：把后端学生通知 feed（studentNotifications）映射成通知卡。
    /// 替代原 announcementNotifications（IX-009 的「拉全部公告自映射」）—— 现在 公告/巴士/行事
    /// 由后端按 notify_students 开关 + 学生可见范围统一聚合，老师没勾「通知」的不进来。
    /// - type 按 kind 分：announcement→「お知らせ」/ bus→「バス」/ event→「カレンダー」（都在「すべて」标签显示）。
    /// - id 用负数（按列表序）—— push 的 id 是正数（≥1000）、包裹用大负数，三段不相撞。
    /// - kind / refId 带上 → 点卡片调 markStudentNotificationRead 标已读。
    private var feedNotifications: [NotificationItem] {
        studentNotifications.enumerated().map { idx, n in
            NotificationItem(
                id: -(idx + 1),
                type: Self.feedNotifType(n.kind),
                title: n.title,
                time: Self.notifTimeLabel(n.createdAt),
                body: n.body,
                unread: !n.isRead,
                kind: n.kind,
                refId: n.refId
            )
        }
    }

    /// feed kind → 通知中心 UI 分类标签。
    private static func feedNotifType(_ kind: String) -> String {
        switch kind {
        case "bus": return "バス"
        case "event": return "カレンダー"
        default: return "お知らせ" // announcement
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

    /// 进入通知中心时刷新通知来源。生产拉学生通知 feed + 包裹；演示构建不动（用 SEED）。
    func refreshNotificationSources() async {
        #if !DEMO
            await loadStudentNotifications()
            await loadMyPackages()
        #endif
    }

    /// 未読数（home greetingRow bell badge 用）
    var unreadNotificationCount: Int {
        #if DEMO
            return allNotifications.filter { $0.unread }.count
        #else
            // 生产：feed 是进通知中心才刷的、首屏 Home 可能还没拉 → badge 用后端 feed 未読数
            //   studentNotificationUnreadCount（loadMe 登录/启动即拉），首屏不依赖是否进过通知中心（§7.13.1）。
            //   feed 一旦加载（studentNotifications 非空），改用列表自身未読条数 —— 与通知中心 feedNotifications 同源，
            //   避免某条点已读后列表已减、badge 仍用后端旧 count 对不上的中间态。空（未加载）时回退后端 count。
            let feedUnread = studentNotifications.isEmpty
                ? studentNotificationUnreadCount
                : studentNotifications.filter { !$0.isRead }.count
            return pushNotifications.filter { $0.unread }.count + feedUnread
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

    /// APNs delegate 收到推送后调用 — 插入 1 条 push 通知
    /// - Parameters:
    ///   - type: NotificationItem.type 字段（"申請" / "減点" / "夜学習" / "リクエスト曲" 等）
    ///   - title: 标题
    ///   - body: 正文
    func handleIncomingPush(type: String, title: String, body: String) {
        let nextId = (pushNotifications.map(\.id).max() ?? 999) + 1
        let item = NotificationItem(
            id: nextId,
            type: type,
            title: title,
            time: "たった今",
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
                type: "夜学習",
                title: "夜学習欠席届が承認されました",
                body: "本日の前半節について、夜学習担当の先生が承認しました。"
            )
        }

        func simulateStudyLeaveRejected() {
            handleIncomingPush(
                type: "夜学習",
                title: "夜学習欠席届が不承認でした",
                body: "本日の前半節は出席をお願いします。詳細は夜学習担当の先生にお尋ねください。"
            )
        }

        func simulateStudyRosterAdded() {
            handleIncomingPush(
                type: "夜学習",
                title: "夜学習対象になりました",
                body: "今日から夜学習の対象に追加されました。19:40 までに自習室へお越しください。"
            )
        }

        func simulateAmendmentRebatch() {
            handleIncomingPush(
                type: "申請",
                title: "外泊届（変更届）が承認されました",
                body: "変更届の内容で寮務課長まで承認が進みました。残り1名の承認をお待ちください。"
            )
        }
    #endif
}

// MARK: - 学習 NFC 出席（system_features §7.3.3-6）

enum StudyTap: String, Hashable, CaseIterable {
    case start // 19:35 ～ 19:40 学习开始
    case end // 21:45 学习结束（itsuki 2026-05-31：废除中场 tap，简化成开始 / 结束 2 次）
}

/// 出席状态（在 amber Card / 个人页里显示）
enum StudyAttendance: String {
    case idle // 学习时间外
    case none // 进行中但 0 次 tap
    case progressing // 已 tap 1 次（正常进行中）
    case green // 两次 tap 均完成 = 时间内
    case yellow // 迟到
    case red // 缺席
    case abnormal // 前后不一致 = 异常，须老师手动判定
    case excused // 缺席已获批准
}

/// マイページ 夜学習履歴 entry
struct StudyHistoryEntry: Hashable, Identifiable {
    let id: UUID
    let date: String // "2026-04-30"
    let tapKind: StudyTap
    let tapLabel: String // 例："夜学習開始" / "夜学習終了"
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

    /// マイページ 夜学習履歴 demo seed
    static var demoSeed: [StudyHistoryEntry] {
        [
            .init(date: "2026-04-29", tapKind: .end, tapLabel: "夜学習終了", timeHM: "21:46", note: nil),
            .init(date: "2026-04-29", tapKind: .start, tapLabel: "夜学習開始", timeHM: "19:37", note: nil),
            .init(date: "2026-04-28", tapKind: .end, tapLabel: "夜学習終了", timeHM: "21:45", note: nil),
            .init(date: "2026-04-28", tapKind: .start, tapLabel: "夜学習開始", timeHM: "19:42", note: "1 分遅刻"),
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
