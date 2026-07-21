// BusListStubs.swift · 寮生专用特别运行班次一览
// ⭐ 会话 C · 老师 38 条 #8「寮生专用特别运行班次一览（参考用 + 外出申请表选择回家方式时确认）」
//
// API 对应（后端 B 尚未到位 → 使用 mock 数据）:
//   GET /buses                → BusListView         (system_features §7.6)
//
// system_features.md §7.6.1 的数据模型对应:
//   bus_routes
//     ├── kind         ENUM('daily_commute','dorm_special')
//     ├── name         "朝便 6:50 寮 → 駅"
//     ├── direction    "寮 → 駅" / "駅 → 寮" / "寮 → 空港"
//     ├── schedule_at  TIMESTAMPTZ
//     ├── arrival_at   TIMESTAMPTZ NULL
//     └── visible_to   ENUM('all','dorm_only','men','women')
//
// 差异点:
//   - 原有 BusView（CommunityStubs.swift）= 按日分组显示（demo 纯列表）
//   - 本 BusListView = 可按班次类型过滤（特别班 / 通学班）+ 突出显示机场接送 + 申请入口

import SwiftUI

// MARK: - 数据模型

enum BusKind: String, Hashable {
    case dailyCommute = "daily_commute" // 平日通学便
    case dormSpecial = "dorm_special" // 寮特別運行便

    var label: String {
        switch self {
        case .dailyCommute: return "通学便"
        case .dormSpecial: return "特別運行便"
        }
    }

    var tone: Pill.Tone {
        switch self {
        case .dailyCommute: return .neutral
        case .dormSpecial: return .accent
        }
    }
}

enum BusVisibility: String, Hashable {
    case all, dormOnly, men, women
}

struct SpecialBusRoute: Hashable, Identifiable {
    let id: String
    let kind: BusKind
    let name: String // 显示用短名称，如 "GW外泊 朝便"
    let direction: String // 如 "高校棟 → 岡山駅西口"
    let date: String // 如 "2026-04-29"
    let weekday: String // 如 "水"
    let scheduleAt: String // 如 "07:30"
    let arrivalAt: String? // 如 "08:25" / nil
    let visibleTo: BusVisibility
    let isAirport: Bool // 机场接送班次（对归国届申请尤为重要）
    let purpose: String? // 如 "GW外泊・帰省・買い物" — 用途标签
    let seatsLabel: String // 如 "空きあり" / "残 3" 等
    let isNext: Bool // 最近班次高亮标记
    let deprecated: Bool
}

// MARK: - 模拟数据（以 SEED.busSchedule 为基础，附加 kind/visibility 字段）

enum BusListMock {
    static let all: [SpecialBusRoute] = makeAll()

    private static func makeAll() -> [SpecialBusRoute] {
        var routes: [SpecialBusRoute] = []
        for sched in SEED.busSchedule {
            for (i, line) in sched.lines.enumerated() {
                // 岡山駅是电车站不是机场，只在路线名含「空港」（机场）时才判定为机场接送班次
                let isAirport = line.route.contains("空港")
                let kind: BusKind = sched.notice != nil ? .dormSpecial : .dailyCommute
                routes.append(SpecialBusRoute(
                    id: "\(sched.date)-\(i)",
                    kind: kind,
                    name: shortName(from: sched.label, time: line.time),
                    direction: line.route,
                    date: sched.date,
                    weekday: sched.weekday,
                    scheduleAt: line.time,
                    arrivalAt: nil,
                    visibleTo: .all,
                    isAirport: isAirport,
                    purpose: sched.label,
                    seatsLabel: line.seats,
                    isNext: line.next,
                    deprecated: false
                ))
            }
        }
        return routes
    }

    private static func shortName(from label: String, time: String) -> String {
        // "GW外泊・帰省・買い物" + "07:30" → 取第一个用途词拼成 "GW外泊 07:30 便"
        let head = label.split(separator: "・").first.map(String.init) ?? label
        return "\(head) \(time) 便"
    }
}

// MARK: - 后端 BusRouteOut → SpecialBusRoute 映射

enum BusRouteMapper {
    /// 把后端巴士便（含完整日期时间）映射成 UI 用的 SpecialBusRoute（拆成日期 / 时分 / 曜日）。
    /// 时刻一律按日本时区（JST）显示。isNext = 排序后第一个「出发时刻 ≥ 现在」的便（高亮「次便」）。
    static func map(_ outs: [BusRouteOut]) -> [SpecialBusRoute] {
        let jst = TimeZone(identifier: "Asia/Tokyo") ?? .current
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = jst

        let dateFmt = DateFormatter()
        dateFmt.locale = Locale(identifier: "en_US_POSIX")
        dateFmt.timeZone = jst
        dateFmt.dateFormat = "yyyy-MM-dd"

        let timeFmt = DateFormatter()
        timeFmt.locale = Locale(identifier: "en_US_POSIX")
        timeFmt.timeZone = jst
        timeFmt.dateFormat = "HH:mm"

        // 周日=1 … 周六=7（Calendar 的 .weekday 约定），减 1 当下标取日语单字曜日
        let weekdayChars = ["日", "月", "火", "水", "木", "金", "土"]

        // isNext（「次便」高亮）改由 BusListView.nextVisibleId 按当前筛选结果实时算，
        // 这里只排序、不定 isNext —— 否则切到「特别便 / 仅空港」筛选后标记会错位（codex 审查 LOW）。
        let sorted = outs.sorted { $0.schedule_at < $1.schedule_at }

        return sorted.map { o in
            let weekdayIndex = cal.component(.weekday, from: o.schedule_at) - 1
            let weekday = weekdayChars.indices.contains(weekdayIndex) ? weekdayChars[weekdayIndex] : ""
            let isAirport = o.direction.contains("空港") || o.name.contains("空港")
            return SpecialBusRoute(
                id: o.id.uuidString,
                kind: BusKind(rawValue: o.kind) ?? .dailyCommute,
                name: o.name,
                direction: o.direction,
                date: dateFmt.string(from: o.schedule_at),
                weekday: weekday,
                scheduleAt: timeFmt.string(from: o.schedule_at),
                arrivalAt: o.arrival_at.map { timeFmt.string(from: $0) },
                visibleTo: mapVisibility(o.visible_to),
                isAirport: isAirport,
                purpose: o.purpose, // 老师在加便表单写的「用途・説明」，日期头右上角每天显示一条
                seatsLabel: "",
                isNext: false, // 实时由 nextVisibleId 决定，见 busRow
                deprecated: o.deprecated
            )
        }
    }

    private static func mapVisibility(_ raw: String) -> BusVisibility {
        switch raw {
        case "dorm_only": return .dormOnly
        case "men": return .men
        case "women": return .women
        default: return .all
        }
    }
}

// ============================================================================
// MARK: - BusListView · 特別運行便 一覧

// ============================================================================

struct BusListView: View {
    @EnvironmentObject var app: AppStore // 判断登录态：已登录拉真后端 / 未登录回退假数据
    @State private var airportOnly: Bool = false
    @State private var routes: [SpecialBusRoute] = [] // 数据源：后端 GET /api/v1/bus/routes 或 mock 兜底
    @State private var isLoading: Bool = false
    @State private var loadError: String? = nil // 已登录拉取失败时的报错（不喂假数据，见 load）

    private var filtered: [SpecialBusRoute] {
        // 本页只显示寮生特別運行便，隐藏平日通学便（itsuki 2026-06-13）
        var arr = routes.filter { $0.kind == .dormSpecial }
        // ios#28：按 visibleTo 过滤（取值 all / dorm_only / men / women）。
        // 口径对齐后端 bus_visible_to_for_student：all + dorm_only 全员可见；
        // men / women 只对本性别。dorm_only 与 all 等价（无通学生字段）。
        // ⚠️ gender 有两套约定：真实 User 用 "male"/"female"（英文，AppStore.User.gender），
        // SEED 演示用户用「男」/「女」（SEED.swift）。displayUser 生产=真实用户(英文)/演示=SEED(日语)，
        // 故两套都认，否则生产下 men/women 班次对谁都不显示。未解析(占位)时男女限定一律不显（防异性看见）。
        let gender = app.displayUser.gender
        let isMale = (gender == "male" || gender == "男")
        let isFemale = (gender == "female" || gender == "女")
        arr = arr.filter { route in
            switch route.visibleTo {
            case .all, .dormOnly:
                return true
            case .men:
                return isMale
            case .women:
                return isFemale
            }
        }
        if airportOnly {
            arr = arr.filter { $0.isAirport }
        }
        return arr.sorted {
            if $0.date != $1.date { return $0.date < $1.date }
            return $0.scheduleAt < $1.scheduleAt
        }
    }

    /// 按日期分组
    private var grouped: [(date: String, weekday: String, purpose: String?, items: [SpecialBusRoute])] {
        let groups = Dictionary(grouping: filtered, by: { $0.date })
        let keys = groups.keys.sorted()
        return keys.compactMap { date in
            guard let arr = groups[date], let first = arr.first else { return nil }
            return (date: date, weekday: first.weekday, purpose: first.purpose, items: arr)
        }
    }

    /// 当前筛选结果里「下一班」（第一个出发时刻 ≥ 现在）的 id —— 按筛选后的可见列表实时算。
    /// date("yyyy-MM-dd") + scheduleAt("HH:mm") 解析回 Date(JST) 再比较时间先后，不依赖零填充字典序。
    private var nextVisibleId: String? {
        let jst = TimeZone(identifier: "Asia/Tokyo") ?? .current
        let fmt = DateFormatter()
        fmt.locale = Locale(identifier: "en_US_POSIX")
        fmt.timeZone = jst
        fmt.dateFormat = "yyyy-MM-dd HH:mm"
        let now = Date()
        return filtered.first { row in
            // CC-03: 解析失败应跳过脏行（return false），不能把识别不出时刻的行错误高亮成「下一班」。
            // 当前数据流下 date/scheduleAt 全由 DateFormatter 产出固定格式、解析必成功，这里是健壮性兜底。
            guard let depart = fmt.date(from: "\(row.date) \(row.scheduleAt)") else { return false }
            return now <= depart
        }?.id
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "特別運行便", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    headerNotice
                    filters
                    if isLoading && routes.isEmpty {
                        ProgressView()
                            .frame(maxWidth: .infinity)
                            .padding(.top, 40)
                    } else if let err = loadError, routes.isEmpty {
                        EmptyState(
                            icon: "bus",
                            title: "読み込みに失敗しました",
                            message: err
                        )
                        .frame(maxWidth: .infinity)
                    } else if grouped.isEmpty {
                        EmptyState(
                            icon: "bus",
                            title: "該当する便はありません",
                            message: "条件を変えてお試しください。"
                        )
                        .frame(maxWidth: .infinity)
                    } else {
                        let nextId = nextVisibleId
                        ForEach(grouped, id: \.date) { group in
                            daySection(group, nextId: nextId)
                        }
                    }
                    Text("※ 通常日のスクールバスは別途ご確認ください。特別便のご利用には、事前に届出（許可願）の提出が必要です。")
                        .font(.system(size: 11))
                        .foregroundStyle(T.inkMute)
                        .lineSpacing(3)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.top, 4)
                }
                .padding(.horizontal, 16)
                .padding(.top, 8)
                .padding(.bottom, 28)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
        .task { await load() }
    }

    // MARK: 数据加载（已登录拉真后端 / 未登录或失败回退 mock）

    /// 未登录 → 回退 BusListMock（开发无 backend / Apple reviewer 没真账号也能看效果）。
    /// 已登录 → GET /api/v1/bus/routes 真数据，按时刻映射成 SpecialBusRoute。
    /// 已登录但拉取失败 → 不喂假时刻表（学生靠这个赶车，假时间会害人误车 — codex 审查 MEDIUM）：
    ///   401（token 失效）清登录态（didSet 自动跳登录）；其它错误显示报错 + 空列表。
    private func load() async {
        isLoading = true
        defer { isLoading = false }
        guard app.isAuthenticated else {
            routes = BusListMock.all
            return
        }
        loadError = nil
        do {
            let raw = try await BusAPI.listRoutes()
            routes = BusRouteMapper.map(raw)
        } catch APIError.unauthorized {
            // token 失效：清登录态（令牌已死）+ 明确提示重登。
            // 不留空列表让用户误以为「没有班次」（codex 复审 MEDIUM）。
            // 跟 StayList 等列表页一致 —— 不在子页强行跳登录（全 App 无中途 401 跳转模式）。
            app.authToken = nil
            loadError = "セッションの有効期限が切れました。再度ログインしてください。"
            routes = []
        } catch {
            loadError = APIErrorPresenter.userMessage(
                for: error,
                fallback: "時刻表の取得に失敗しました"
            )
            routes = []
        }
    }

    // MARK: 上部 banner（帰国届 提示）

    private var headerNotice: some View {
        HStack(alignment: .top, spacing: 8) {
            Text("✈")
                .font(.system(size: 14, weight: .bold))
                .foregroundStyle(T.primary)
            VStack(alignment: .leading, spacing: 2) {
                Text("空港送迎便について")
                    .font(.system(size: 12.5, weight: .bold))
                    .foregroundStyle(T.primary)
                Text("帰国許可願を提出する場合は、「空港送迎便のみ」をオンにして該当の便を選択してください。")
                    .font(.system(size: 11.5))
                    .foregroundStyle(T.inkSub)
                    .lineSpacing(2)
            }
            Spacer(minLength: 0)
        }
        .padding(.horizontal, 14).padding(.vertical, 12)
        .background(T.pill)
        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
    }

    // MARK: 筛选 row

    private var filters: some View {
        // 班次类型筛选条（原「すべて」「特別便」「通学便」三选项）已删 —— 本页只显示特別運行便，
        // 仅保留「空港送迎便のみ」开关（提交帰国届选机场班次时用）。
        HStack(spacing: 8) {
            Toggle(isOn: $airportOnly) { EmptyView() }
                .labelsHidden()
                .toggleStyle(.switch)
                .tint(T.primary)
                .scaleEffect(0.85)
                .frame(width: 50)
            Text("空港送迎便のみ")
                .font(.system(size: 12, weight: .semibold))
                .foregroundStyle(airportOnly ? T.primary : T.inkSub)
            Spacer()
        }
    }

    // MARK: 日別 section

    private func daySection(_ g: (date: String, weekday: String, purpose: String?, items: [SpecialBusRoute]), nextId: String?) -> some View {
        VStack(spacing: 0) {
            HStack(alignment: .firstTextBaseline, spacing: 10) {
                Text(monthDayLabel(g.date))
                    .font(.system(size: 17, weight: .heavy, design: .monospaced))
                    .foregroundStyle(T.primaryDk)
                Text("(\(g.weekday))")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundStyle(T.inkSub)
                Spacer(minLength: 6)
                if let p = g.purpose {
                    Text(p)
                        .font(.system(size: 11.5))
                        .foregroundStyle(T.inkSub)
                        .lineLimit(1)
                        .truncationMode(.tail)
                }
            }
            .padding(.horizontal, 14).padding(.vertical, 12)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(T.primary.opacity(0.05))

            VStack(spacing: 0) {
                ForEach(Array(g.items.enumerated()), id: \.offset) { i, route in
                    busRow(route, isNext: route.id == nextId)
                    if i < g.items.count - 1 {
                        Rectangle().fill(T.hair).frame(height: 0.5)
                            .padding(.leading, 58)
                    }
                }
            }
            .background(T.paper)
        }
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .stroke(T.hair, lineWidth: 0.5)
        )
        .shadow(color: T.ink.opacity(0.05), radius: 10, x: 0, y: 3)
    }

    // MARK: bus row

    private func busRow(_ r: SpecialBusRoute, isNext: Bool) -> some View {
        HStack(spacing: 12) {
            ZStack {
                RoundedRectangle(cornerRadius: 10, style: .continuous)
                    .fill(isNext ? T.primary : T.primary.opacity(0.08))
                    .frame(width: 36, height: 36)
                Image(systemName: r.isAirport ? "airplane" : "bus")
                    .font(.system(size: 16))
                    .foregroundStyle(isNext ? .white : T.primary)
            }
            VStack(alignment: .leading, spacing: 3) {
                HStack(spacing: 6) {
                    Text(r.scheduleAt)
                        .font(.system(size: 17, weight: .bold, design: .monospaced))
                        .foregroundStyle(T.ink)
                    Pill(text: r.kind.label, tone: r.kind.tone)
                    if r.isAirport {
                        Pill(text: "空港", tone: .accent)
                    }
                }
                Text(r.direction)
                    .font(.system(size: 11.5))
                    .foregroundStyle(T.inkSub)
                    .lineLimit(1)
            }
            Spacer()
            VStack(alignment: .trailing, spacing: 3) {
                if isNext {
                    Pill(text: "次便", tone: .accent)
                }
                Text(r.seatsLabel)
                    .font(.system(size: 10.5))
                    .foregroundStyle(T.inkMute)
            }
        }
        .padding(.horizontal, 14).padding(.vertical, 11)
    }

    private func monthDayLabel(_ s: String) -> String {
        let p = s.split(separator: "-")
        guard p.count >= 3, let m = Int(p[1]), let d = Int(p[2]) else { return s }
        return "\(m)/\(d)"
    }
}

#Preview("BusList · all") {
    BusListView()
        .environmentObject(RouterStore(initial: .busList))
        .environmentObject(AppStore())
}
