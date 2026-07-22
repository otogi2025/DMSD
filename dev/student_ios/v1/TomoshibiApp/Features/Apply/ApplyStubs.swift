// ApplyStubs.swift · Apply feature 13 views (v2 HTML-fidelity rewrite)
// ⭐ Agent D · v2 · 1:1 对照 refs/phaseB_src/100ba570__ApplyListPage_ApplyNewPage_ApplyFormPage.js
// 12 种 APPLY_TYPES · StayForm 8 section · GenericApplyForm · Detail workflow · Preview · Done
// 注意:
//   - 日文字符串逐字照抄 JSX
//   - 颜色全部走 T.* tokens
//   - SF Symbols 用 Ic.* (JSX 源用 SVG path 但 Ic 已是视觉接近的 SF Symbol wrapper,
//     保持 Agent D 与 Foundation 的一致性, 避免 feature 级重复造轮)
//   - StayForm 对应 JSX line 92-292 的 8 section（本人联系方式 / 同行者 / 日期时间 / 交通方式 / 住宿地点 / 餐食 / 理由 / 备注）

import SwiftUI

// MARK: - APPLY_TYPES (12 种)

private struct ApplyTypeMeta {
    let k: String
    let name: String
    let icon: String // SF Symbol name
    let desc: String
}

private let APPLY_TYPES: [ApplyTypeMeta] = [
    .init(k: "outing", name: "外出", icon: "calendar", desc: "当日帰寮の外出"),
    .init(k: "stay", name: "外泊", icon: "house", desc: "寮外での宿泊"),
    .init(k: "holiday", name: "帰省", icon: "house.lodge", desc: "実家帰省・長期休暇"),
    .init(k: "returncountry", name: "帰国", icon: "airplane", desc: "一時帰国（航空機利用）"),
    .init(k: "repair", name: "修繕", icon: "wrench.and.screwdriver", desc: "部屋・設備の修繕依頼"),
    .init(k: "parcel", name: "代理受取", icon: "shippingbox", desc: "不在時の荷物代理受取"),
    .init(k: "guest", name: "来訪者", icon: "person.2", desc: "家族・友人の来訪"),
    .init(k: "studyAbsence", name: "夜学習欠席", icon: "book.closed", desc: "夜学習の欠席届（前半・後半・両方）"),
    .init(k: "studyOnline", name: "オンライン学習", icon: "laptopcomputer", desc: "自室でのオンライン学習"),
    .init(k: "event", name: "行事企画", icon: "sparkles", desc: "寮内イベントの企画申請"),
    .init(k: "fridge", name: "冷蔵庫購入", icon: "snowflake", desc: "指定冷蔵庫の購入届"),
    .init(k: "item", name: "物品所持", icon: "shippingbox", desc: "持込物品の許可願"),
]

private func applyType(_ k: String) -> ApplyTypeMeta {
    APPLY_TYPES.first { $0.k == k } ?? APPLY_TYPES[0]
}

// MARK: - APPLY_STATUS 映射 (JSX line 14-21)

private func statusPair(_ status: String) -> (label: String, tone: Pill.Tone) {
    switch status {
    case "draft": return ("下書き", .neutral)
    case "pending": return ("審査中", .warn)
    case "approved": return ("承認済", .ok)
    case "approved_partial": return ("一部承認", .ok) // codex: 原来落 default 显示原始英文
    case "rejected": return ("差し戻し", .danger)
    case "returned": return ("要修正", .danger)
    case "withdrawn": return ("取消済", .neutral)
    default: return (status, .neutral)
    }
}

// ============================================================================
// §2.1 ApplyListView — L1 · 4-tab + SEED.applications + FAB
// ============================================================================

struct ApplyListView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore // codex: 401 时清登录态跳登录页用
    @State private var tab: String = "all"

    // IX-007: 列表数据源。原来直接读 SEED 假数据；现在演示读种子、生产调 GET /applications/mine。
    @State private var items: [ApplicationItem] = []
    @State private var loading: Bool = true
    @State private var loadError: String? = nil
    @State private var hasLoaded: Bool = false // codex: 防切 tab / 重入时重复拉

    // ios#6: 「下書き」tab 生产恒空（草稿保存已删、后端无 draft）——仅 DEMO 保留，生产隐藏。
    // 注：Swift 不允许 #if 直接出现在数组字面量元素位，故用闭包构造 + append 条件加入。
    private let tabs: [(String, String)] = {
        var t: [(String, String)] = [
            ("all", "すべて"),
            ("pending", "審査中"),
            ("approved", "承認済"),
        ]
        #if DEMO
            t.append(("draft", "下書き"))
        #endif
        return t
    }()

    private var filtered: [ApplicationItem] {
        items.filter { matchesTab($0.status) }
    }

    /// codex:「承認済」tab 要同时收 approved 和 approved_partial（一部承認），
    /// 否则部分通过的申请哪个 tab 都不显示、只在「全部」tab 露面
    private func matchesTab(_ status: String) -> Bool {
        switch tab {
        case "all": return true
        case "approved": return status == "approved" || status == "approved_partial"
        default: return status == tab
        }
    }

    /// 后端 ApplicationOut → 列表用 ApplicationItem（两个模型字段不同，做一层转换）
    private func mapToItem(_ o: ApplicationOut) -> ApplicationItem {
        ApplicationItem(
            id: o.id.uuidString,
            type: ApplyKindMapper.decode(o.kind),
            status: o.status,
            date: o.leave_date,
            summary: "\(o.kind)・\(o.leave_date)〜\(o.return_date)"
        )
    }

    /// 后端 OutingOut → 列表用 ApplicationItem。外出在独立 outings 表，
    /// id 加 "outing:" 前缀 → 详情页 ApplyDetailView 按前缀分流到 OutingDetailView。
    private func mapOutingToItem(_ o: OutingOut) -> ApplicationItem {
        ApplicationItem(
            id: "outing:\(o.id.uuidString)",
            type: "outing",
            status: o.status,
            date: o.outing_date,
            summary: o.destination.map { "外出・\($0)" } ?? "外出"
        )
    }

    /// 拉列表数据：演示读 SEED，生产调 GET /applications/mine
    private func load() async {
        loading = true
        loadError = nil
        #if DEMO
            items = SEED.applications
            hasLoaded = true
        #else
            do {
                let apps = try await ApplicationsAPI.listMine()
                var merged = apps.map(mapToItem)
                // 外出（独立 outings 表）失败不拖垮出寮届列表：拉不到就只是不显示外出
                if let outings = try? await OutingsAPI.listMine() {
                    merged += outings.map(mapOutingToItem)
                }
                // 出寮届 + 外出按日期倒序合并展示
                items = merged.sorted { $0.date > $1.date }
                hasLoaded = true
            } catch APIError.unauthorized {
                // codex: 令牌过期/失效 → 清登录态走登录页（跟 StayListView 一致），
                // 不要卡在「请重新登录」错误页里、人还停在已登录的壳里
                app.authToken = nil
                router.replace(.login)
            } catch {
                loadError = APIErrorPresenter.userMessage(
                    for: error, fallback: "申請一覧の取得に失敗しました"
                )
            }
        #endif
        loading = false
    }

    var body: some View {
        ZStack(alignment: .bottomTrailing) {
            VStack(spacing: 0) {
                PageHeader(title: "申し込み", level: 1)
                ScrollView {
                    VStack(alignment: .leading, spacing: 0) {
                        // Tabs (pill row)
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 6) {
                                ForEach(tabs, id: \.0) { k, l in
                                    Button { tab = k } label: {
                                        Text(l)
                                            .font(.system(size: 12.5, weight: .semibold))
                                            .padding(.horizontal, 14).padding(.vertical, 7)
                                            .foregroundStyle(tab == k ? Color.white : T.primary)
                                            .background {
                                                Capsule().fill(tab == k ? T.primary : T.pill)
                                            }
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                            .padding(.bottom, 14)
                        }

                        if loading {
                            // IX-007: 拉后端数据时显示加载中
                            ProgressView()
                                .frame(maxWidth: .infinity)
                                .padding(40)
                        } else if let loadError {
                            // IX-007: 后端取数据失败时显示错误 + 重试，不再静默给假数据
                            VStack(spacing: 10) {
                                Text("⚠️").font(.system(size: 40))
                                Text(loadError)
                                    .font(.system(size: 13))
                                    .foregroundStyle(T.inkSub)
                                    .multilineTextAlignment(.center)
                                Button("再読み込み") { Task { await load() } }
                                    .font(.system(size: 13, weight: .semibold))
                                    .foregroundStyle(T.primary)
                            }
                            .frame(maxWidth: .infinity)
                            .padding(40)
                        } else if filtered.isEmpty {
                            VStack(spacing: 10) {
                                Text("📋").font(.system(size: 40))
                                Text("申請はありません")
                                    .font(.system(size: 14, weight: .semibold))
                                    .foregroundStyle(T.inkSub)
                                Text("下の＋ボタンから新規作成できます")
                                    .font(.system(size: 12))
                                    .foregroundStyle(T.inkMute)
                            }
                            .frame(maxWidth: .infinity)
                            .padding(40)
                        } else {
                            VStack(spacing: 10) {
                                ForEach(filtered) { item in
                                    ApplicationRow(item: item)
                                        .onTapGesture {
                                            router.go(.applyDetail(id: item.id))
                                        }
                                }
                            }
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.bottom, 120)
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(T.pearl)

            // FAB
            Button {
                router.go(.applyNew)
            } label: {
                Ic.plus(24)
                    .foregroundStyle(.white)
                    .frame(width: 56, height: 56)
                    .background {
                        RoundedRectangle(cornerRadius: 18, style: .continuous)
                            .fill(T.primary)
                            .shadow(color: T.primary.opacity(0.35), radius: 12, x: 0, y: 8)
                    }
            }
            .padding(.trailing, 18)
            .padding(.bottom, 96)
        }
        .task { if !hasLoaded { await load() } } // IX-007: 进页面拉申请列表（codex: hasLoaded 防重复拉）
    }
}

private struct ApplicationRow: View {
    let item: ApplicationItem

    var body: some View {
        let t = applyType(item.type)
        // 外出是独立 outings 表、四态语义不同（承認不要/確認済/却下/取消済），别套出寮届的「審査中/承認済」
        let sp = item.type == "outing" ? outingStatusPair(item.status) : statusPair(item.status)
        Card(padding: 14) {
            VStack(alignment: .leading, spacing: 0) {
                HStack(spacing: 12) {
                    // icon square
                    Image(systemName: t.icon)
                        .font(.system(size: 17))
                        .foregroundStyle(T.primary)
                        .frame(width: 40, height: 40)
                        .background {
                            RoundedRectangle(cornerRadius: 10, style: .continuous).fill(T.pill)
                        }
                    VStack(alignment: .leading, spacing: 3) {
                        HStack(spacing: 8) {
                            Text(t.name)
                                .font(.system(size: 14, weight: .bold))
                                .foregroundStyle(T.ink)
                            Pill(text: sp.label, tone: sp.tone)
                        }
                        Text(item.summary)
                            .font(.system(size: 12))
                            .foregroundStyle(T.inkSub)
                    }
                    Spacer(minLength: 0)
                }
                .padding(.bottom, 8)

                // bottom row
                HStack {
                    Text(item.date)
                        .font(.system(size: 11, design: .monospaced))
                        .foregroundStyle(T.inkMute)
                    Spacer()
                }
                .padding(.top, 8)
                .overlay(alignment: .top) {
                    Rectangle().fill(T.hair).frame(height: 0.5)
                }
            }
        }
    }
}

#Preview("ApplyList") {
    ApplyListView()
        .environmentObject(RouterStore(initial: .apply))
        .environmentObject(AppStore())
}

// ============================================================================
// §2.2 ApplyNewView — L2 · 12 APPLY_TYPES grid 2 col
// ============================================================================

struct ApplyNewView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    private let cols: [GridItem] = [
        GridItem(.flexible(), spacing: 10),
        GridItem(.flexible(), spacing: 10),
    ]

    /// 外出禁止（当月扣分 ≥8 = 禁足）—— 只置灰「外出」这一张卡，其余 11 种申请照常可点。
    /// 阈值 8 与主页减点卡（HomeStubs.cleaningFlagRow）同一口径。
    private var outingBanned: Bool {
        app.displayUser.points >= 8
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "新規申請", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    Text("申請の種類を選択してください")
                        .font(.system(size: 13))
                        .foregroundStyle(T.inkSub)
                        .padding(.horizontal, 4)
                        .padding(.bottom, 14)

                    // 禁足中 → 说明为什么「外出」那张卡是灰的、点不动
                    if outingBanned {
                        HStack(alignment: .top, spacing: 8) {
                            Image(systemName: "exclamationmark.octagon.fill")
                                .font(.system(size: 13, weight: .semibold))
                                .foregroundStyle(T.danger)
                            Text("外出禁止中のため申請できません。特別な事情がある場合は寮監に相談してください")
                                .font(.system(size: 12.5))
                                .foregroundStyle(T.ink)
                                .lineSpacing(3)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.horizontal, 14).padding(.vertical, 12)
                        .background {
                            RoundedRectangle(cornerRadius: 14, style: .continuous).fill(T.dangerBg)
                        }
                        .overlay {
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .stroke(T.danger.opacity(0.25), lineWidth: 1)
                        }
                        .padding(.bottom, 14)
                    }

                    LazyVGrid(columns: cols, spacing: 10) {
                        ForEach(APPLY_TYPES, id: \.k) { t in
                            let disabled = t.k == "outing" && outingBanned
                            Button {
                                router.go(.applyForm(kind: t.k))
                            } label: {
                                Card(padding: 16) {
                                    VStack(spacing: 0) {
                                        Image(systemName: t.icon)
                                            .font(.system(size: 22))
                                            .foregroundStyle(T.primary)
                                            .frame(width: 52, height: 52)
                                            .background {
                                                RoundedRectangle(cornerRadius: 14, style: .continuous).fill(T.pill)
                                            }
                                            .padding(.bottom, 10)
                                        Text(t.name)
                                            .font(.system(size: 14, weight: .bold))
                                            .foregroundStyle(T.ink)
                                            .padding(.bottom, 3)
                                        Text(t.desc)
                                            .font(.system(size: 11))
                                            .foregroundStyle(T.inkMute)
                                            .lineSpacing(2)
                                            .multilineTextAlignment(.center)
                                    }
                                    .frame(maxWidth: .infinity)
                                }
                            }
                            .buttonStyle(.plain)
                            .disabled(disabled)
                            .opacity(disabled ? 0.4 : 1) // 置灰：整张卡（图标 / 名称 / 说明）一起淡出
                        }
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 4).padding(.bottom, 24)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl)
    }
}

#Preview("ApplyNew") {
    ApplyNewView()
        .environmentObject(RouterStore(initial: .applyNew))
        .environmentObject(AppStore())
}

// ============================================================================
// §2.3 ApplyFormDispatcher — kind 分派
// ============================================================================

struct ApplyFormDispatcher: View {
    let kind: String

    var body: some View {
        // 老师反馈 #1-#4 对应：出寮届 = 帰省 / 外泊 / 帰国 三种类型全部走 StayForm
        // 按 §7.2 字段累积表动态显示（StayForm 内部根据 kind 判断）
        if kind == "stay" || kind == "holiday" || kind == "returncountry" {
            StayForm(kind: kind)
        } else if kind == "studyAbsence" {
            StudyAbsenceForm()
        } else if kind == "studyOnline" {
            StudyOnlineForm()
        } else if kind == "event" {
            DormEventProposalForm()
        } else if kind == "fridge" {
            FridgePurchaseForm()
        } else if kind == "item" {
            ItemPossessionForm()
        } else {
            GenericApplyForm(kind: kind)
        }
    }
}

// ============================================================================
// §2.4 StayForm ⭐⭐⭐ — 出寮届（帰省 / 外泊 / 帰国）· §7.2 spec 实装
//
// 老师 38 条反馈 #1-#4 对应：
//   #1 学生只能提交自己的申请 → 申请者本人 = SEED.user 固定 read-only · 提交时 assert
//   #2 三种类型（帰省 / 外泊 / 帰国）字段累积模型
//   #3 出寮日 = 仅限明日以后（DatePicker minDate = tomorrow）
//   #4 不需要的字段隐藏（按 kind 动态显示）
//
// 字段累积：
//   帰省  : 出寮日 / 帰省方式 / 出寮时刻 / 帰寮日 / 帰寮方式 / 帰寮时刻
//   外泊  : 帰省字段 + 外泊地点（可多个）+ 免餐期间
//   帰国  : 外泊字段 + 出发机场 / 出发时刻 / 到达机场 / 到达时刻
// ============================================================================

struct StayForm: View {
    let kind: String
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    /// ── 申請者本人 · app.displayUser 読取（IX-008：登录拉真人，演示/未登录回退 SEED 占位）────
    private var meAccount: String {
        app.displayUser.account
    } // 6 桁学号 = student_id
    private var meName: String {
        app.displayUser.name
    }

    private var meClass: String {
        "\(app.displayUser.grade)\(app.displayUser.classSuffix)組"
    }

    private var meNo: String {
        "\(app.displayUser.seatNo)番"
    }

    private var meDorm: String {
        "\(app.displayUser.dorm) \(app.displayUser.room)"
    }

    private var mePhone: String {
        app.displayUser.phone
    }

    private var meCategory: String {
        app.displayUser.category
    } // 一般寮生 / 留学生
    private var meIsOverseas: Bool {
        app.displayUser.isOverseas
    }

    // ── 实物表補完字段（2026-05-28）──────────────────────────────────────
    @State private var contactPhone: String = "" // 预填移到 .onAppear 从 app.displayUser 拿（@State 默认值 view init 时抓全局假人 SEED.user，loadMe 晚到 / 切账号不刷新）
    @State private var didPrefillContact = false
    @State private var isLongVacation: Bool = false
    @State private var companion: String = ""
    @State private var destCities: String = ""
    @State private var mealNote: String = ""

    // ── §7.2 共通字段（帰省 / 外泊 / 帰国 三种类型通用）────────────────────────
    @State private var leaveDate: Date = ApplyFormDate.tomorrow
    @State private var leaveTime: Date = ApplyFormDate.parseHM("18:00")
    @State private var leaveMethod: String = "JR"
    @State private var returnDate: Date = ApplyFormDate.tomorrow
    @State private var returnTime: Date = ApplyFormDate.parseHM("20:00")
    @State private var returnMethod: String = "JR"

    // ── 仅外泊 / 帰国 ────────────────────────────────────────────────────
    // 滞在先 1 件 = 稳定 id + 地址。用 id 当列表项身份（不用数组下标），
    // 删中间一行时输入框内容 / 焦点不会串到别行（IX-032）。
    @State private var stayPlaces: [StayPlaceItem] = [StayPlaceItem()] // 外泊地点(可多个)
    @State private var skipStartDate: Date = ApplyFormDate.tomorrow
    @State private var skipStartMeal: String = "夕食" // 朝食 / 昼食 / 夕食
    @State private var skipEndDate: Date = ApplyFormDate.tomorrow
    @State private var skipEndMeal: String = "朝食"
    @State private var skipEnabled: Bool = true // 是否申告免餐期间

    // ── 仅帰国 ───────────────────────────────────────────────────────────
    @State private var departAirport: String = ""
    @State private var departFlightTime: Date = ApplyFormDate.parseHM("10:00")
    @State private var arriveAirport: String = ""
    @State private var arriveFlightTime: Date = ApplyFormDate.parseHM("14:00")

    /// ── 共通: 理由 ────────────────────────────────────────────────────────
    @State private var reason: String = ""

    /// ── 出租车预约「タクシー予約」— 出寮方法选了「タクシー」时想坐车的时刻（itsuki 2026-06-04：废止独立开关，改成出寮方法连动）──
    @State private var taxiTime: Date = ApplyFormDate.parseHM("18:00")
    @State private var isSubmitting = false

    /// 出租车这个移动方式的字面量 —— 出寮方法选了它才出预约时刻选择器。
    /// 抽成常量：下面 LEAVE_TRANSPORTS 数组 + UI 条件 + 提交逻辑三处都引这一个，改文案只改这里、不会漏改某处静默失效
    private static let TAXI_METHOD = "タクシー"

    /// 出寮方法（去程·离开宿舍去车站 / 机场）。不含飞机 —— 帰国坐飞机的信息在「飛行機」段单独填（航班时刻 ≠ 出寮时刻）
    private let LEAVE_TRANSPORTS = [
        "西口1便", "西口2便", "金川1便", "金川2便", "寮生特別運行",
        "JR", "自家用車", StayForm.TAXI_METHOD, "教員", "その他",
    ]
    /// 帰寮方法（回程·回宿舍 / 登校）。不含飞机 —— 同上，飞机走「飛行機」段
    private let RETURN_TRANSPORTS = [
        "西口登校便", "金川登校便", "寮生特別運行",
        "JR", "自家用車", "タクシー", "教員", "その他",
    ]
    private let HOLIDAY_FORM_TYPES = ["通常時用", "長期休暇用"]
    private let MEALS = ["朝食", "昼食", "夕食"]

    /// ── kind 判定 helper ─────────────────────────────────────────────────
    private var isHoliday: Bool {
        kind == "holiday"
    }

    private var isStay: Bool {
        kind == "stay"
    }

    private var isReturnCountry: Bool {
        kind == "returncountry"
    }

    private var needPlaces: Bool {
        isStay || isReturnCountry
    } // §4 外泊地点
    private var needSkipMeal: Bool {
        isStay || isReturnCountry
    } // §5 食事不要期間
    private var needFlight: Bool {
        isReturnCountry
    } // §6 飛行機
    private var type: ApplyTypeMeta {
        applyType(kind)
    }

    /// 出寮日 / 免餐开始日往后调时，把依赖它们、且已落在新下限之前的日期一并钳回。
    /// SwiftUI 的 ApplyDateField(minDate:) 只限制选择器能选的范围，不会回钳「已绑定且越界」的旧值——
    /// 否则用户先选好帰寮日、再把出寮日改到更晚，帰寮日仍停在旧值 < 出寮日，canSubmit 永远 false、
    /// 提交键静默置灰且无任何提示（留学生完全不知卡在哪）。
    private func clampDependentDates() {
        if returnDate < leaveDate { returnDate = leaveDate }
        if skipStartDate < leaveDate { skipStartDate = leaveDate }
        if skipEndDate < skipStartDate { skipEndDate = skipStartDate }
        // A-377: 免餐区间不能超出帰寮日 —— 帰寮日往前调时把越界的免餐起止回钳，
        // 否则同样会出现「提交键静默置灰且无提示」。
        if skipStartDate > returnDate { skipStartDate = returnDate }
        if skipEndDate > returnDate { skipEndDate = returnDate }
    }

    /// 是否可提交：必填项是否已填写（reason / 机场名 trim 后判空，与 stayPlaces 口径一致）
    private var canSubmit: Bool {
        if reason.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty { return false }
        // IX-018: 把离校 / 返校都按「日期 + 时刻」合成成完整时间再比较。
        // 同一天 20:00 离校 → 08:00 返校 这种时刻倒挂也能拦下来。
        if StayForm.combine(date: returnDate, time: returnTime)
            <= StayForm.combine(date: leaveDate, time: leaveTime)
        {
            return false
        }
        if needPlaces {
            // stayPlaces 是 StayPlaceItem 数组。address 全为空就当作没填。
            if stayPlaces.allSatisfy({ $0.address.trimmingCharacters(in: .whitespaces).isEmpty }) {
                return false
            }
        }
        if needFlight {
            if departAirport.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                || arriveAirport.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            {
                return false
            }
            // ios#8: 帰国航班到着必须晚于出发（与后端 KikokuCreateIn 一致）；倒挂/相等 → 置灰
            if StayForm.combine(date: returnDate, time: arriveFlightTime)
                <= StayForm.combine(date: leaveDate, time: departFlightTime)
            {
                return false
            }
        }
        return true
    }

    /// 「寮生特別運行の時刻表を見る」按钮 — 出寮方法 / 帰寮方法 下方各放一个，
    /// 因为这两组移动方式里都能选「寮生特別運行」。点了跳到特別運行便一覧（BusListView）。
    private var busTimetableButton: some View {
        Button {
            router.go(.busList)
        } label: {
            HStack(spacing: 4) {
                Image(systemName: "bus")
                    .font(.system(size: 12, weight: .semibold))
                Text("寮生特別運行の時刻表を見る")
                    .font(.system(size: 12, weight: .semibold))
                Image(systemName: "chevron.right")
                    .font(.system(size: 10, weight: .semibold))
            }
            .foregroundStyle(T.primary)
            .padding(.top, 2)
        }
        .buttonStyle(.plain)
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "\(type.name)申請", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // ── kind 別 hint banner ─────────────────────────────────
                    if isHoliday {
                        kindBanner(text: "⏰ 帰省申請の締切は毎週水曜日18:00です")
                    } else if isReturnCountry {
                        kindBanner(text: "✈️ 帰国申請は航空券確定後に提出してください")
                    } else {
                        kindBanner(text: "📝 外泊申請は出発の3日前までに提出してください")
                    }

                    // ── Header card（申请类型）──────────────────────────────
                    headerCard
                        .padding(.bottom, 20)

                    // ── §1 申請者本人 = app.displayUser（生产 currentUser / 演示或未登录回退 SEED 占位）──
                    SectionLabel(n: "1", label: "申請者本人")
                    Card(padding: 0) {
                        VStack(spacing: 0) {
                            InfoRow(k: "アカウント番号", v: meAccount, isFirst: true)
                            InfoRow(k: "氏名", v: meName)
                            InfoRow(k: "学年・組", v: "\(meClass)  \(meNo)")
                            InfoRow(k: "寮・部屋", v: meDorm)
                            InfoRow(k: "区分", v: meCategory)
                            InfoRow(k: "携帯電話", v: mePhone)
                        }
                    }
                    .padding(.bottom, 8)
                    Text("※ ログイン中のアカウントで提出されます。他の生徒の代理提出はできません。")
                        .font(.system(size: 11))
                        .foregroundStyle(T.inkMute)
                        .padding(.bottom, 18)

                    // ── §2 実物表補完: 連絡先 + 帰省届区分 ────────────────
                    SectionLabel(n: "2", label: "連絡先・届の区分")
                    Card(padding: 14) {
                        VStack(alignment: .leading, spacing: 12) {
                            Field(label: "本人連絡先（携帯電話）") {
                                TField(text: $contactPhone, placeholder: "090-0000-0000", keyboard: .phonePad)
                            }
                            if isHoliday {
                                Field(label: "帰省届の区分") {
                                    ChipGroup(
                                        options: HOLIDAY_FORM_TYPES,
                                        value: Binding(
                                            get: { isLongVacation ? "長期休暇用" : "通常時用" },
                                            set: { isLongVacation = ($0 == "長期休暇用") }
                                        )
                                    )
                                }
                            }
                        }
                    }
                    .padding(.bottom, 18)

                    // ── §3 出寮 ────────────────────────────────────────────
                    SectionLabel(n: "3", label: "出寮")
                    Card(padding: 14) {
                        VStack(alignment: .leading, spacing: 12) {
                            // 出寮日 — DatePicker minDate = tomorrow (#3)
                            VStack(alignment: .leading, spacing: 6) {
                                Text("出寮日")
                                    .font(.system(size: 12, weight: .semibold))
                                    .foregroundStyle(T.inkSub)
                                HStack(spacing: 10) {
                                    ApplyDateField(date: $leaveDate, minDate: ApplyFormDate.tomorrow)
                                        .onChangeCompat(of: leaveDate) { clampDependentDates() }
                                    ApplyTimeField(date: $leaveTime)
                                }
                                Text("※ 出寮日は明日以降のみ選択できます")
                                    .font(.system(size: 10.5))
                                    .foregroundStyle(T.inkMute)
                            }
                            // 帰省方法（= 出寮时的交通方式）
                            VStack(alignment: .leading, spacing: 6) {
                                Text(isHoliday ? "帰省方法" : "出寮方法")
                                    .font(.system(size: 12, weight: .semibold))
                                    .foregroundStyle(T.inkSub)
                                ChipGroup(options: LEAVE_TRANSPORTS, value: $leaveMethod)
                                busTimetableButton
                            }
                            // 出租车预约：出寮方法选了「タクシー」就当场露出希望时刻选择器
                            // （itsuki 2026-06-04：废止旧·独立「タクシー予約」开关框，改成跟出寮方法连动）
                            if leaveMethod == StayForm.TAXI_METHOD {
                                VStack(alignment: .leading, spacing: 6) {
                                    Text("タクシー希望時刻")
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundStyle(T.inkSub)
                                    ApplyTimeField(date: $taxiTime)
                                }
                            }
                        }
                    }
                    .padding(.bottom, 18)

                    // ── §4 帰寮 ────────────────────────────────────────────
                    SectionLabel(n: "4", label: "帰寮")
                    Card(padding: 14) {
                        VStack(alignment: .leading, spacing: 12) {
                            VStack(alignment: .leading, spacing: 6) {
                                Text("帰寮日")
                                    .font(.system(size: 12, weight: .semibold))
                                    .foregroundStyle(T.inkSub)
                                HStack(spacing: 10) {
                                    ApplyDateField(date: $returnDate, minDate: leaveDate)
                                        // A-377: 帰寮日改早时回钳越界的免餐起止
                                        .onChangeCompat(of: returnDate) { clampDependentDates() }
                                    ApplyTimeField(date: $returnTime)
                                }
                            }
                            VStack(alignment: .leading, spacing: 6) {
                                Text("帰寮方法")
                                    .font(.system(size: 12, weight: .semibold))
                                    .foregroundStyle(T.inkSub)
                                ChipGroup(options: RETURN_TRANSPORTS, value: $returnMethod)
                                busTimetableButton
                            }
                        }
                    }
                    .padding(.bottom, 18)

                    // ── §5 外泊地点（外泊 / 帰国 限定 · 动态显示 #4）──────────
                    if needPlaces {
                        SectionLabel(n: "5", label: "同行者・行先・宿泊先")
                        Card(padding: 14) {
                            VStack(alignment: .leading, spacing: 12) {
                                Field(label: "同行者") {
                                    TField(text: $companion, placeholder: "同行者がいる場合は入力")
                                }
                                // 帰国 时隐藏「行先（都市名）」—— 只填下面的「宿泊先」住所（itsuki 2026-06-03）
                                if !isReturnCountry {
                                    Field(label: "行先（都市名）") {
                                        TField(text: $destCities, placeholder: "例：東京・大阪・ソウル")
                                    }
                                }
                                VStack(alignment: .leading, spacing: 10) {
                                    Text("宿泊先")
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundStyle(T.inkSub)
                                    // IX-032: 用 $stayPlaces 按稳定 id 列举每一行。
                                    // 删中间一行时输入框内容 / 焦点不会串到别行。
                                    ForEach($stayPlaces) { $place in
                                        HStack(spacing: 8) {
                                            TField(text: $place.address, placeholder: "宿泊先住所")
                                            if stayPlaces.count > 1 {
                                                Button {
                                                    // 按 id 删除（不用数组下标，用身份删）
                                                    stayPlaces.removeAll { $0.id == place.id }
                                                } label: {
                                                    Image(systemName: "minus.circle.fill")
                                                        .font(.system(size: 22))
                                                        .foregroundStyle(T.danger)
                                                }
                                                .buttonStyle(.plain)
                                            }
                                        }
                                    }
                                    Button {
                                        stayPlaces.append(StayPlaceItem())
                                    } label: {
                                        HStack(spacing: 6) {
                                            Image(systemName: "plus.circle")
                                                .font(.system(size: 14, weight: .semibold))
                                            Text("滞在先を追加")
                                                .font(.system(size: 13, weight: .semibold))
                                        }
                                        .foregroundStyle(T.primary)
                                    }
                                    .buttonStyle(.plain)
                                    Text("※ 複数の場所に滞在する場合はすべて入力してください")
                                        .font(.system(size: 10.5))
                                        .foregroundStyle(T.inkMute)
                                }
                            }
                        }
                        .padding(.bottom, 18)
                    }

                    // ── §6 食事不要期間（外泊 / 帰国 限定）─────────────────
                    if needSkipMeal {
                        SectionLabel(n: "6", label: "寮食堂 食事の申し込み")
                        Card(padding: 14) {
                            VStack(alignment: .leading, spacing: 14) {
                                if meIsOverseas {
                                    Toggle(isOn: $skipEnabled) {
                                        Text("食事不要期間を登録する")
                                            .font(.system(size: 13, weight: .semibold))
                                            .foregroundStyle(T.ink)
                                    }
                                    .tint(T.primary)

                                    if skipEnabled {
                                        Divider().background(T.hair)
                                        VStack(alignment: .leading, spacing: 6) {
                                            Text("不要 開始")
                                                .font(.system(size: 11.5, weight: .semibold))
                                                .foregroundStyle(T.inkSub)
                                            HStack(spacing: 8) {
                                                ApplyDateField(date: $skipStartDate, minDate: leaveDate)
                                                    .onChangeCompat(of: skipStartDate) {
                                                        // CB-06: skipStartDate 主动往后拖时 clampDependentDates 不触发（只挂 leaveDate/returnDate），
                                                        // 补钳「开始日不得晚于帰寮日」，否则下面 skipEndDate 的 DateField 会 min>max 运行期崩溃
                                                        if skipStartDate > returnDate { skipStartDate = returnDate }
                                                        if skipEndDate < skipStartDate { skipEndDate = skipStartDate }
                                                    }
                                                ChipGroup(options: MEALS, value: $skipStartMeal)
                                            }
                                        }
                                        VStack(alignment: .leading, spacing: 6) {
                                            Text("不要 終了")
                                                .font(.system(size: 11.5, weight: .semibold))
                                                .foregroundStyle(T.inkSub)
                                            HStack(spacing: 8) {
                                                // A-377: 終了日不能晚于帰寮日（免餐区间不能超出外泊期）
                                                // CB-06: minDate 用 min(skipStartDate, returnDate) 兜底，防 skipStartDate>returnDate 时 min>max 崩溃
                                                DateField(date: $skipEndDate, minDate: Swift.min(skipStartDate, returnDate), maxDate: returnDate)
                                                ChipGroup(options: MEALS, value: $skipEndMeal)
                                            }
                                        }
                                        Text("※ 上記の期間（開始の食事から終了の食事まで）は寮食堂の食事を停止します")
                                            .font(.system(size: 10.5))
                                            .foregroundStyle(T.inkMute)
                                    }

                                    Field(label: "食事備考") {
                                        TArea(text: $mealNote,
                                              placeholder: "例：8月10日の朝食まで必要、8月20日の夕食から必要",
                                              rows: 3)
                                    }
                                } else {
                                    Text("食事の変更は食事入力表にご記入ください")
                                        .font(.system(size: 13, weight: .semibold))
                                        .foregroundStyle(T.ink)
                                    Text("※ 日本人生徒の食事の変更は、学校指定の食事入力表で行ってください。")
                                        .font(.system(size: 10.5))
                                        .foregroundStyle(T.inkMute)
                                }
                            }
                        }
                        .padding(.bottom, 18)
                    }

                    // ── §7 飛行機（帰国 限定）─────────────────────────────
                    if needFlight {
                        SectionLabel(n: "7", label: "飛行機")
                        Card(padding: 14) {
                            VStack(alignment: .leading, spacing: 12) {
                                Field(label: "出発空港", required: true) {
                                    TField(text: $departAirport, placeholder: "出発空港名")
                                }
                                VStack(alignment: .leading, spacing: 6) {
                                    Text("出発時刻")
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundStyle(T.inkSub)
                                    ApplyTimeField(date: $departFlightTime)
                                }
                                Field(label: "到着空港", required: true) {
                                    TField(text: $arriveAirport, placeholder: "到着空港名")
                                }
                                VStack(alignment: .leading, spacing: 6) {
                                    Text("到着時刻")
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundStyle(T.inkSub)
                                    ApplyTimeField(date: $arriveFlightTime)
                                }
                            }
                        }
                        .padding(.bottom, 18)
                    }

                    // ── §8 理由 (全種類共通) ─────────────────────────────────
                    let reasonSectionN = needFlight ? "8" : (needSkipMeal ? "7" : "5")
                    SectionLabel(n: reasonSectionN,
                                 label: isHoliday ? "帰省の理由" : (isReturnCountry ? "帰国の理由" : "外泊の理由"))
                    TArea(text: $reason,
                          placeholder: "理由を入力してください",
                          rows: 3)
                        .padding(.bottom, 22)

                    // ── 提出 button row ─────────────────────────────────────
                    // 注：原「下書き保存」按钮是假动作（只弹 toast、什么都不存，「下書き」tab 生产永远空）。
                    // v1.0 移除，避免误导用户以为草稿已保存。本地草稿留 v1.1（需设计存储方案）。
                    HStack(spacing: 10) {
                        Button {
                            submit()
                        } label: {
                            Text("提出する")
                                .font(.system(size: 14, weight: .bold))
                                .foregroundStyle(.white)
                                .frame(maxWidth: .infinity, minHeight: 52)
                                .background {
                                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                                        .fill((canSubmit && !isSubmitting) ? T.primary : T.inkFaint)
                                }
                        }
                        .buttonStyle(.plain)
                        .disabled(!canSubmit || isSubmitting)
                    }
                    .padding(.bottom, 14)

                    Text("提出後は担当の先生へメールで承認依頼が送信されます。")
                        .font(.system(size: 10.5))
                        .foregroundStyle(T.inkFaint)
                        .multilineTextAlignment(.center)
                        .frame(maxWidth: .infinity)
                }
                .padding(.horizontal, 20)
                .padding(.top, 4).padding(.bottom, 28)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl)
        .onAppear { prefillContact() }
        .onChangeCompat(of: app.currentUser?.account) { prefillContact() } // 自动登录冷启动：真实用户晚到时补填一次（Codex 6-03）
    }

    /// 预填本人联系电话：生产只在拿到真实 currentUser 后填（冷启动假人 SEED.user 不写入字段）；演示构建直接用 SEED 占位。didPrefill 守卫防重复覆盖。
    private func prefillContact() {
        guard !didPrefillContact else { return }
        #if DEMO
            contactPhone = app.displayUser.phone
            didPrefillContact = true
        #else
            guard app.currentUser != nil else { return }
            contactPhone = app.displayUser.phone
            didPrefillContact = true
        #endif
    }

    // MARK: - subviews

    private func kindBanner(text: String) -> some View {
        HStack(spacing: 8) {
            Text(text)
                .font(.system(size: 12))
                .foregroundStyle(T.warnDeep)
        }
        .padding(.horizontal, 14).padding(.vertical, 12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background {
            RoundedRectangle(cornerRadius: 12, style: .continuous).fill(T.warnBg)
        }
        .overlay {
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(T.warn.opacity(0.25), lineWidth: 1)
        }
        .padding(.bottom, 14)
    }

    private var headerCard: some View {
        HStack(spacing: 12) {
            Image(systemName: type.icon)
                .font(.system(size: 17))
                .foregroundStyle(.white)
                .frame(width: 40, height: 40)
                .background {
                    RoundedRectangle(cornerRadius: 10, style: .continuous).fill(T.primary)
                }
            VStack(alignment: .leading, spacing: 2) {
                Text("\(type.name)許可願")
                    .font(.system(size: 14, weight: .bold))
                    .foregroundStyle(T.ink)
                Text("朝日塾中等教育学校 国際交流部寮")
                    .font(.system(size: 11.5))
                    .foregroundStyle(T.inkSub)
            }
            Spacer(minLength: 0)
        }
        .padding(.horizontal, 16).padding(.vertical, 14)
        .background {
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .fill(T.primary.opacity(0.03))
        }
        .overlay {
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .stroke(T.primary.opacity(0.12), lineWidth: 1)
        }
    }

    // MARK: - submit (POST /api/v1/applications)

    //
    // F1: kind 用 ApplyKindMapper 转日文 (stay → 外泊 等)
    // F2: stay_locations 是 [{kind, name, address?, phone?}] 对象数组
    // F3: meals_skip 是 [{date, meal}, ...] entry 列表
    // F4: student_id 从 JWT 拿、不发送
    // F7: 实接 ApplicationsAPI.create（按 kind dispatch 到 3 个 typed body）

    private func submit() {
        Task { await submitAsync() }
    }

    private func submitAsync() async {
        // 防连点：提交在途再点直接忽略，避免重复提交
        guard !isSubmitting else { return }
        isSubmitting = true
        defer { isSubmitting = false }

        // 共通字段（backend time 要 "HH:mm:ss" 格式、append :00）
        let backendKind = ApplyKindMapper.encode(kind)
        let leaveDateStr = ApplyFormDate.formatYMD(leaveDate)
        let leaveTimeStr = ApplyFormDate.formatHM(leaveTime) + ":00"
        let returnDateStr = ApplyFormDate.formatYMD(returnDate)
        let returnTimeStr = ApplyFormDate.formatHM(returnTime) + ":00"
        let contactPhoneValue = ApplyFormDate.nilIfBlank(contactPhone)
        let mealNoteValue = meIsOverseas ? ApplyFormDate.nilIfBlank(mealNote) : nil
        let companionValue = ApplyFormDate.nilIfBlank(companion)
        let destCitiesValue = ApplyFormDate.nilIfBlank(destCities)
        // 出租车预约：出寮方法选了「タクシー」→ "HH:MM:SS"；选别的 → nil（不预约）
        let taxiTimeValue: String? = leaveMethod == StayForm.TAXI_METHOD ? ApplyFormDate.formatHM(taxiTime) + ":00" : nil

        // F2: stay_locations object 数组（外泊 / 帰国届用、帰省届不带）
        // IX-010: UI 输入框标的是「滞在先住所」（地址），所以写进 address 字段。
        // backend 的 name 是必填，把地址也填进 name 不让它空。
        let stayLocations: [StayLocationBody] = stayPlaces
            .map { $0.address.trimmingCharacters(in: .whitespaces) }
            .filter { !$0.isEmpty }
            .map { StayLocationBody(kind: "その他", name: $0, address: $0, phone: nil) }

        // F3: meals_skip 范围 → entry 列表
        let mealsSkip: [MealSkipBody]
        if needSkipMeal, meIsOverseas, skipEnabled {
            mealsSkip = StayForm.expandMealsSkip(
                from: skipStartDate, startMeal: skipStartMeal,
                to: skipEndDate, endMeal: skipEndMeal
            ).map { dict in
                MealSkipBody(date: dict["date"] ?? "", meal: dict["meal"] ?? "")
            }
            // IX-013: 起「夕食」终「朝食」放同一天，展开出来是空数组。
            // 开关还开着却发空数组 = 用户以为申报了免餐、其实什么都没申报。
            // 这里拦下来，让用户改餐次顺序。
            if mealsSkip.isEmpty {
                app.showToast("食事不要期間が指定されていません。開始と終了の食事の順序をご確認ください")
                return
            }
        } else {
            mealsSkip = []
        }

        // ios#5: 提交前抓令牌；成功后若已切号/登出则不再 toast/导航（同 submitOuting）
        let tokenAtStart = app.authToken
        do {
            // 按 kind dispatch 到 3 个 typed Encodable body
            switch backendKind {
            case "帰省":
                let body = KisheiCreateBody(
                    reason: reason.trimmingCharacters(in: .whitespacesAndNewlines),
                    contact_phone: contactPhoneValue,
                    meal_note: mealNoteValue,
                    is_long_vacation: isLongVacation,
                    leave_date: leaveDateStr,
                    leave_method: leaveMethod,
                    leave_time: leaveTimeStr,
                    return_date: returnDateStr,
                    return_method: returnMethod,
                    return_time: returnTimeStr,
                    taxi_reservation_time: taxiTimeValue
                )
                _ = try await ApplicationsAPI.create(body)
            case "外泊":
                let body = GaihakuCreateBody(
                    reason: reason.trimmingCharacters(in: .whitespacesAndNewlines),
                    contact_phone: contactPhoneValue,
                    meal_note: mealNoteValue,
                    companion: companionValue,
                    dest_cities: destCitiesValue,
                    leave_date: leaveDateStr,
                    leave_method: leaveMethod,
                    leave_time: leaveTimeStr,
                    return_date: returnDateStr,
                    return_method: returnMethod,
                    return_time: returnTimeStr,
                    stay_locations: stayLocations,
                    meals_skip: mealsSkip,
                    taxi_reservation_time: taxiTimeValue
                )
                _ = try await ApplicationsAPI.create(body)
            case "帰国":
                let body = KikokuCreateBody(
                    reason: reason.trimmingCharacters(in: .whitespacesAndNewlines),
                    contact_phone: contactPhoneValue,
                    meal_note: mealNoteValue,
                    companion: companionValue,
                    dest_cities: destCitiesValue,
                    leave_date: leaveDateStr,
                    leave_method: leaveMethod,
                    leave_time: leaveTimeStr,
                    return_date: returnDateStr,
                    return_method: returnMethod,
                    return_time: returnTimeStr,
                    stay_locations: stayLocations,
                    meals_skip: mealsSkip,
                    flight_dep_air: departAirport.trimmingCharacters(in: .whitespacesAndNewlines),
                    // IX-005: ApplyTimeField 只有时刻，底层日期停在 2000-01-01。
                    // 出发跟出寮日合成、到着跟帰寮日合成，凑成完整 datetime，
                    // 用带 +09:00 的 ISO 字符串发出去（bare ISO8601 会变成 UTC 的 Z，跟 backend 期望不符）。
                    flight_dep_at: ApplyFormDate.combineDateAndTimeISO(date: leaveDate, time: departFlightTime),
                    flight_arr_air: arriveAirport.trimmingCharacters(in: .whitespacesAndNewlines),
                    flight_arr_at: ApplyFormDate.combineDateAndTimeISO(date: returnDate, time: arriveFlightTime),
                    taxi_reservation_time: taxiTimeValue
                )
                _ = try await ApplicationsAPI.create(body)
            default:
                app.showToast("この種類の届には対応していません")
                return
            }
            // 提交成功
            guard app.authToken == tokenAtStart else { return } // 切账号 / 登出后不在新会话弹 toast / 导航
            app.showToast("\(type.name)申請を提出しました")
            router.go(.applyDone(kind: kind))
        } catch let APIError.unprocessable(msg) {
            // backend 验证错误（例：出寮日是今日 / chain 役职配置缺失 等）
            app.showToast(msg)
        } catch APIError.unauthorized {
            // token 失效 → 清掉 + 跳登录
            app.authToken = nil
            router.replace(.login)
        } catch APIError.network {
            app.showToast("通信エラーが発生しました。電波を確認してください")
        } catch {
            app.showToast(APIErrorPresenter.userMessage(for: error, fallback: "申請の提出に失敗しました"))
        }
    }

    // MARK: - meals_skip 展开辅助方法

    ///
    /// 生成（skipStartDate, skipStartMeal）→（skipEndDate, skipEndMeal）区间内的所有餐食条目
    static func expandMealsSkip(
        from startDate: Date, startMeal: String,
        to endDate: Date, endMeal: String
    ) -> [[String: String]] {
        let mealOrder = ["朝食", "昼食", "夕食"]
        var result: [[String: String]] = []
        let cal = ApplyFormDate.tokyoCalendar // 固定 JST：日期步进与 formatYMD(JST) 一致，非 JST 设备 meals_skip 不偏（codex 审出）
        var current = startDate
        while current <= endDate {
            let isFirst = cal.isDate(current, inSameDayAs: startDate)
            let isLast = cal.isDate(current, inSameDayAs: endDate)
            let lo = isFirst ? (mealOrder.firstIndex(of: startMeal) ?? 0) : 0
            let hi = isLast ? (mealOrder.firstIndex(of: endMeal) ?? 2) : 2
            if lo <= hi {
                let dateStr = ApplyFormDate.formatYMD(current)
                for i in lo ... hi {
                    result.append(["date": dateStr, "meal": mealOrder[i]])
                }
            }
            guard let next = cal.date(byAdding: .day, value: 1, to: current) else { break }
            current = next
        }
        return result
    }

    // MARK: - helpers（日期合成；parse/format 统一走 ApplyFormDate）

    /// 把一个日期的年月日 + 一个时刻的时分合成成一个 Date。
    /// ApplyTimeField 只带时刻、底层日期是 2000-01-01，所以要跟对应的日期组合起来用。
    static func combine(date: Date, time: Date) -> Date {
        let cal = ApplyFormDate.tokyoCalendar
        let d = cal.dateComponents([.year, .month, .day], from: date)
        let t = cal.dateComponents([.hour, .minute], from: time)
        var c = DateComponents()
        c.year = d.year
        c.month = d.month
        c.day = d.day
        c.hour = t.hour
        c.minute = t.minute
        c.second = 0
        return cal.date(from: c) ?? date
    }
}

/// 滞在先一条 —— 带稳定 id，给 ForEach 当列表项身份用（IX-032）。
/// 输入框只有地址，所以只有 address 一个字段。
struct StayPlaceItem: Identifiable, Hashable {
    let id = UUID()
    var address: String = ""
}

#Preview("StayForm · 外泊") {
    StayForm(kind: "stay")
        .environmentObject(RouterStore(initial: .applyForm(kind: "stay")))
        .environmentObject(AppStore())
}

#Preview("StayForm · 帰省") {
    StayForm(kind: "holiday")
        .environmentObject(RouterStore(initial: .applyForm(kind: "holiday")))
        .environmentObject(AppStore())
}

#Preview("StayForm · 帰国") {
    StayForm(kind: "returncountry")
        .environmentObject(RouterStore(initial: .applyForm(kind: "returncountry")))
        .environmentObject(AppStore())
}

// MARK: - StayForm 私有 helpers

private struct SectionLabel: View {
    let n: String
    let label: String
    var body: some View {
        HStack(spacing: 8) {
            Text(n)
                .font(.system(size: 11, weight: .bold))
                .foregroundStyle(.white)
                .frame(width: 22, height: 22)
                .background {
                    RoundedRectangle(cornerRadius: 6, style: .continuous).fill(T.primary)
                }
            Text(label)
                .font(.system(size: 13, weight: .bold))
                .foregroundStyle(T.ink)
            Spacer(minLength: 0)
        }
        .padding(.top, 4).padding(.bottom, 10)
    }
}

private struct InfoRow: View {
    let k: String
    let v: String
    var isFirst: Bool = false
    var body: some View {
        HStack(alignment: .top, spacing: 0) {
            Text(k)
                .font(.system(size: 12))
                .foregroundStyle(T.inkSub)
                .frame(width: 88, alignment: .leading)
            Text(v)
                .font(.system(size: 13.5, weight: .semibold))
                .foregroundStyle(T.ink)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding(.horizontal, 16).padding(.vertical, 12)
        .overlay(alignment: .top) {
            if !isFirst {
                Rectangle().fill(T.hair).frame(height: 0.5)
            }
        }
    }
}

private struct ChipGroup: View {
    let options: [String]
    @Binding var value: String
    var body: some View {
        FlowLayout(hSpacing: 6, vSpacing: 6) {
            ForEach(options, id: \.self) { opt in
                Button {
                    value = opt
                } label: {
                    Text(opt)
                        .font(.system(size: 12, weight: .semibold))
                        .padding(.horizontal, 12).padding(.vertical, 7)
                        .foregroundStyle(value == opt ? Color.white : T.ink)
                        .background {
                            Capsule().fill(value == opt ? T.primary : T.paper)
                        }
                        .overlay {
                            Capsule().stroke(value == opt ? T.primary : T.hair, lineWidth: 1)
                        }
                        .contentShape(Capsule())
                }
                .buttonStyle(.plain)
            }
        }
    }
}

/// iOS 16+ Layout protocol-based flow — chips auto-wrap 到下一行，不会跟 label 混
private struct FlowLayout: Layout {
    var hSpacing: CGFloat = 6
    var vSpacing: CGFloat = 6

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache _: inout Void) -> CGSize {
        let maxWidth = proposal.width ?? .infinity
        var x: CGFloat = 0
        var y: CGFloat = 0
        var rowHeight: CGFloat = 0
        for sub in subviews {
            let size = sub.sizeThatFits(.unspecified)
            if x + size.width > maxWidth && x > 0 {
                y += rowHeight + vSpacing
                x = 0
                rowHeight = 0
            }
            x += size.width + hSpacing
            rowHeight = max(rowHeight, size.height)
        }
        return CGSize(width: maxWidth.isFinite ? maxWidth : x, height: y + rowHeight)
    }

    func placeSubviews(in bounds: CGRect, proposal _: ProposedViewSize, subviews: Subviews, cache _: inout Void) {
        let maxWidth = bounds.width
        var x: CGFloat = bounds.minX
        var y: CGFloat = bounds.minY
        var rowHeight: CGFloat = 0
        for sub in subviews {
            let size = sub.sizeThatFits(.unspecified)
            if x - bounds.minX + size.width > maxWidth, x > bounds.minX {
                y += rowHeight + vSpacing
                x = bounds.minX
                rowHeight = 0
            }
            sub.place(at: CGPoint(x: x, y: y), anchor: .topLeading, proposal: ProposedViewSize(size))
            x += size.width + hSpacing
            rowHeight = max(rowHeight, size.height)
        }
    }
}

private struct DateField: View {
    @Binding var date: Date
    var minDate: Date? = nil // 仅 skipEndDate 仍用本组件（需 maxDate；ApplyDateField 尚无 maxDate）
    var maxDate: Date? = nil // A-377: 食事不要 終了日 上限 = 帰寮日，免餐区间不能超出外泊期
    var body: some View {
        Group {
            switch (minDate, maxDate) {
            case let (min?, max?):
                // CB-06: min>max 会让 ClosedRange 崩溃（Range requires lowerBound<=upperBound）。
                // 全局兜底：任何调用方倒挂时收紧成 min(min,max)...max，杜绝运行期崩溃。
                DatePicker("", selection: $date, in: Swift.min(min, max) ... max, displayedComponents: .date)
            case let (min?, nil):
                DatePicker("", selection: $date, in: min..., displayedComponents: .date)
            case let (nil, max?):
                DatePicker("", selection: $date, in: ...max, displayedComponents: .date)
            case (nil, nil):
                DatePicker("", selection: $date, displayedComponents: .date)
            }
        }
        .labelsHidden()
        .datePickerStyle(.compact)
        .environment(\.locale, Locale(identifier: "ja_JP")) // itsuki 反馈: 月份要日语/数字 (西暦 2026年4月)
        // 固定 JST 时区+日历：非 JST 设备也按日本时间存储，否则 combine 用东京日历提取会偏 1 小时（codex 审出，同 ApplyFormSupport）
        .environment(\.timeZone, TimeZone(identifier: "Asia/Tokyo")!)
        .environment(\.calendar, ApplyFormDate.tokyoCalendar)
        .frame(maxWidth: .infinity, minHeight: 42)
        .padding(.horizontal, 8)
        .background {
            RoundedRectangle(cornerRadius: 10, style: .continuous).fill(T.paper)
        }
        .overlay {
            RoundedRectangle(cornerRadius: 10, style: .continuous).stroke(T.hair, lineWidth: 1)
        }
    }
}

// ============================================================================
// §2.5 StudyAbsenceForm — 夜学習欠席届（晚自习请假）· system_features §7.3.5
// 4-30 後續 itsuki 拍板 — 字段：理由 textarea + 范围 select（前半/后半/両方）
// ============================================================================

struct StudyAbsenceForm: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var reason: String = ""
    @State private var range: StudyLeaveRange = .first
    /// 请假日期。默认 = 今天。可选范围：今天起 14 天以内。
    // CB-03: 初值用 ApplyFormDate.today（JST 日历锚定），与 dateRange/formatYMD 的 JST 口径统一，避免裸 Date() 随设备时区漂
    @State private var targetDate: Date = ApplyFormDate.today
    @State private var isSubmitting = false

    /// 可选日期范围：今天～14 天后
    private var dateRange: ClosedRange<Date> {
        // 按 JST 算「今天～14 天后」，避免非 JST 设备范围边界偏一天（DatePicker 已固定东京时区）（codex 审出）
        let cal = ApplyFormDate.tokyoCalendar
        let today0 = cal.startOfDay(for: Date())
        let later = cal.date(byAdding: .day, value: 14, to: today0) ?? today0
        return today0 ... later
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "夜学習欠席届", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    // 生产一览无 studyAbsence 列表：提交前告知不会进一览（ios#0）
                    Text("※提出後は一覧に表示されません（受付は完了します）")
                        .font(.system(size: 11))
                        .foregroundStyle(T.inkMute)
                        .padding(.horizontal, 16)

                    // §1 缺席日期（DatePicker）
                    VStack(alignment: .leading, spacing: 8) {
                        SectionLabel(n: "1", label: "欠席する日付")
                        DatePicker(
                            "",
                            selection: $targetDate,
                            in: dateRange,
                            displayedComponents: .date
                        )
                        .datePickerStyle(.compact)
                        .labelsHidden()
                        .environment(\.locale, Locale(identifier: "ja_JP"))
                        // 固定 JST 时区+日历：非 JST 设备 target_date 不偏（提交走 formatYMD 已固定 JST，输入端也要对齐）（codex 审出）
                        .environment(\.timeZone, TimeZone(identifier: "Asia/Tokyo")!)
                        .environment(\.calendar, ApplyFormDate.tokyoCalendar)
                        .padding(12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background {
                            RoundedRectangle(cornerRadius: 10, style: .continuous).fill(T.paper)
                        }
                        .overlay {
                            RoundedRectangle(cornerRadius: 10, style: .continuous).stroke(T.hair, lineWidth: 1)
                        }
                    }
                    .padding(.horizontal, 16)

                    // §2 範囲 select (3 choices)
                    VStack(alignment: .leading, spacing: 8) {
                        SectionLabel(n: "2", label: "欠席する範囲")
                        VStack(spacing: 8) {
                            ForEach(StudyLeaveRange.allCases, id: \.self) { r in
                                Button { range = r } label: {
                                    HStack(spacing: 12) {
                                        Image(systemName: range == r ? "checkmark.circle.fill" : "circle")
                                            .font(.system(size: 22))
                                            .foregroundStyle(range == r ? T.primary : T.inkMute)
                                        Text(r.label)
                                            .font(.system(size: 14, weight: range == r ? .semibold : .regular))
                                            .foregroundStyle(T.ink)
                                        Spacer()
                                    }
                                    .padding(12)
                                    .background {
                                        RoundedRectangle(cornerRadius: 10, style: .continuous)
                                            .fill(range == r ? T.primary.opacity(0.06) : T.paper)
                                    }
                                    .overlay {
                                        RoundedRectangle(cornerRadius: 10, style: .continuous)
                                            .stroke(range == r ? T.primary : T.hair, lineWidth: 1)
                                    }
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    }
                    .padding(.horizontal, 16)

                    // §3 理由 textarea (必填)
                    VStack(alignment: .leading, spacing: 8) {
                        SectionLabel(n: "3", label: "理由（必須）")
                        ZStack(alignment: .topLeading) {
                            if reason.isEmpty {
                                Text("欠席する理由を入力してください")
                                    .font(.system(size: 14))
                                    .foregroundStyle(T.inkMute)
                                    .padding(12)
                            }
                            TextEditor(text: $reason)
                                .font(.system(size: 14))
                                .padding(8)
                                .frame(minHeight: 120)
                                .scrollContentBackground(.hidden)
                        }
                        .background {
                            RoundedRectangle(cornerRadius: 10, style: .continuous).fill(T.paper)
                        }
                        .overlay {
                            RoundedRectangle(cornerRadius: 10, style: .continuous).stroke(T.hair, lineWidth: 1)
                        }
                    }
                    .padding(.horizontal, 16)

                    // §3 提出 button
                    Button {
                        guard !reason.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
                            app.showToast("理由を入力してください")
                            return
                        }
                        // 防连点：提交在途再点直接忽略，避免重复提交
                        guard !isSubmitting else { return }
                        isSubmitting = true
                        Task {
                            defer { isSubmitting = false }
                            // ios#5: 提交前抓令牌；成功后若已切号/登出则不再导航（同 submitOuting）
                            let tokenAtStart = app.authToken
                            do {
                                try await app.submitStudyLeave(
                                    targetDate: ApplyFormDate.formatYMD(targetDate),
                                    reason: reason,
                                    range: range
                                )
                                guard app.authToken == tokenAtStart else { return } // 切账号 / 登出后不在新会话弹 toast / 导航
                                router.go(.applyDone(kind: "studyAbsence"))
                            } catch let APIError.unprocessable(msg) {
                                // 同日重复提交 / target_date 范围超过 等
                                app.showToast(msg)
                            } catch APIError.unauthorized {
                                app.authToken = nil
                                router.replace(.login)
                            } catch APIError.network {
                                app.showToast("通信エラーが発生しました。電波を確認してください")
                            } catch is CancellationError {
                                // IX-034：提交在途登出 / 切用户 → 静默中止，不导航完成页、不弹错误
                            } catch {
                                app.showToast(APIErrorPresenter.userMessage(for: error, fallback: "申請の提出に失敗しました"))
                            }
                        }
                    } label: {
                        Text("提出する")
                            .font(.system(size: 15, weight: .semibold))
                            .foregroundStyle(.white)
                            .frame(maxWidth: .infinity, minHeight: 48)
                            .background(Capsule().fill(isSubmitting ? T.inkFaint : T.primary))
                    }
                    .buttonStyle(.plain)
                    .disabled(isSubmitting)
                    .padding(.horizontal, 16)
                    .padding(.top, 8)
                    .padding(.bottom, 32)
                }
                .padding(.top, 16)
            }
        }
        .background(T.pearl.ignoresSafeArea())
    }
}

#Preview("StudyAbsenceForm") {
    StudyAbsenceForm()
        .environmentObject(RouterStore(initial: .applyForm(kind: "studyAbsence")))
        .environmentObject(AppStore())
}

// ============================================================================
// §2.6 GenericApplyForm — 通用表单 (outing / repair / parcel / guest)
// ============================================================================

struct GenericApplyForm: View {
    let kind: String
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var dest: String = ""
    @State private var reason: String = ""
    @State private var date: Date = ApplyFormDate.tomorrow
    @State private var time: Date = ApplyFormDate.parseHM("18:00")
    @State private var contact: String = ""
    @State private var didPrefillContact: Bool = false
    // 出租车预约「タクシー予約」（itsuki 2026-06-03）— 外出也能预约
    @State private var taxiReserved: Bool = false
    @State private var taxiTime: Date = ApplyFormDate.parseHM("18:00")
    @State private var transport: String = "電車"
    @State private var repairPlace: String = "自室"

    // ── 外出（outing）専用 — 接 outings 后端（A1）。后端 OutingCreateIn.outing_date 必填 ──
    @State private var outingDate: Date = ApplyFormDate.today // 外出日（今日以降）；CB-02: 初值锚 JST 今天 + ApplyDateField minDate 前置挡
    @State private var outingLeaveTime: Date = ApplyFormDate.parseHM("13:00")
    @State private var outingReturnTime: Date = ApplyFormDate.parseHM("17:00")
    @State private var isSubmittingOuting: Bool = false

    private var type: ApplyTypeMeta {
        applyType(kind)
    }

    /// GenericApplyForm 只承接 outing/repair/parcel/guest；stay/holiday/returncountry 走 StayForm
    private var needsDest: Bool {
        kind == "outing"
    }

    private var needsTransport: Bool {
        kind == "outing"
    }

    private var isRepair: Bool {
        kind == "repair"
    }

    private var isParcel: Bool {
        kind == "parcel"
    }

    private var isGuest: Bool {
        kind == "guest"
    }

    private var isOuting: Bool {
        kind == "outing"
    }

    /// 外出禁止（当月扣分 ≥8 = 禁足）—— 只挡外出，修繕 / 代理受取 / 来訪者 不受影响。
    /// 阈值 8 与主页减点卡（HomeStubs.cleaningFlagRow）同一口径，别另发明一套。
    /// 分数来自 app.displayUser.points（登录时 loadMe 从减点接口填）；没拉到时是 0 → 闸不生效，
    /// 由后端 POST 的 422（code=OUTING_BANNED）兜底，学生会看到同一句禁止说明的 toast。
    private var isOutingBanned: Bool {
        isOuting && app.displayUser.points >= 8
    }

    /// 修繕 / 来訪者 / 代理受取（iOS「parcel」）三类 → 接 misc-requests 后端（功能⑥）。
    private var isMiscKind: Bool {
        ["repair", "guest", "parcel"].contains(kind)
    }

    /// 提交按钮文案：外出 / 生产版 misc 直接提交显「提出する」，否则走确认页显「次へ · 確認」。
    private var submitButtonLabel: String {
        if isSubmittingOuting { return "提出中…" }
        #if DEMO
            return isOuting ? "提出する" : "次へ · 確認"
        #else
            return (isOuting || isMiscKind) ? "提出する" : "次へ · 確認"
        #endif
    }

    private var canSubmit: Bool {
        if isOutingBanned { return false } // 禁足中不让提交外出（其他申请种类不受影响）
        guard !reason.isEmpty else { return false }
        if needsDest && dest.trimmingCharacters(in: .whitespaces).isEmpty { return false } // 外出: 去的地方「行き先」必填（trim 防只填空格）
        // 来訪者(guest)「来訪者氏名」/ 代理受取(parcel)「荷物の概要」也走 dest 字段、标了必填 → 同样 trim 后必须非空（codex 复审 minor-1）
        if (isGuest || isParcel) && dest.trimmingCharacters(in: .whitespaces).isEmpty { return false }
        // ios#7: 外出 — 帰寮时刻须 ≥ 外出时刻（同日 combine；倒挂时置灰，对齐后端 OutingCreateIn）
        if isOuting {
            if StayForm.combine(date: outingDate, time: outingReturnTime)
                < StayForm.combine(date: outingDate, time: outingLeaveTime)
            {
                return false
            }
        }
        return true
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "\(type.name)申請", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // Header card
                    HStack(spacing: 12) {
                        Image(systemName: type.icon)
                            .font(.system(size: 17))
                            .foregroundStyle(.white)
                            .frame(width: 40, height: 40)
                            .background {
                                RoundedRectangle(cornerRadius: 10, style: .continuous).fill(T.primary)
                            }
                        VStack(alignment: .leading, spacing: 2) {
                            Text(type.name)
                                .font(.system(size: 14, weight: .bold))
                                .foregroundStyle(T.ink)
                            Text(type.desc)
                                .font(.system(size: 11.5))
                                .foregroundStyle(T.inkSub)
                        }
                        Spacer(minLength: 0)
                    }
                    .padding(.horizontal, 16).padding(.vertical, 14)
                    .background {
                        RoundedRectangle(cornerRadius: 14, style: .continuous).fill(T.primary.opacity(0.03))
                    }
                    .overlay {
                        RoundedRectangle(cornerRadius: 14, style: .continuous).stroke(T.primary.opacity(0.12), lineWidth: 1)
                    }
                    .padding(.bottom, 20)

                    // 禁足中（当月扣分 ≥8）→ 顶部红框说明为什么提交按钮点不动
                    if isOutingBanned {
                        HStack(alignment: .top, spacing: 8) {
                            Image(systemName: "exclamationmark.octagon.fill")
                                .font(.system(size: 13, weight: .semibold))
                                .foregroundStyle(T.danger)
                            Text("外出禁止中のため申請できません。特別な事情がある場合は寮監に相談してください")
                                .font(.system(size: 12.5))
                                .foregroundStyle(T.ink)
                                .lineSpacing(3)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.horizontal, 14).padding(.vertical, 12)
                        .background {
                            RoundedRectangle(cornerRadius: 14, style: .continuous).fill(T.dangerBg)
                        }
                        .overlay {
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .stroke(T.danger.opacity(0.25), lineWidth: 1)
                        }
                        .padding(.bottom, 16)
                    }

                    // repair / parcel / guest 无学生端列表：提交前告知不会进一览（ios#0）；outing 会进一览，不显
                    if isMiscKind {
                        Text("※提出後は一覧に表示されません（受付は完了します）")
                            .font(.system(size: 11))
                            .foregroundStyle(T.inkMute)
                            .padding(.bottom, 14)
                    }

                    if needsDest {
                        Field(label: "行先", required: true) {
                            TField(text: $dest, placeholder: "行き先を入力")
                        }.padding(.bottom, 14)
                    }
                    if isOuting {
                        // 外出是当天回寮 — 外出日（必填）+ 外出/回寮时刻。后端 OutingCreateIn 要 outing_date
                        Field(label: "外出日", required: true) {
                            // CB-02: minDate=今天，DatePicker 直接挡过去日期，不再仅靠后端 422 拒
                            ApplyDateField(date: $outingDate, minDate: ApplyFormDate.today)
                        }.padding(.bottom, 14)
                        Field(label: "外出時刻") {
                            ApplyTimeField(date: $outingLeaveTime)
                        }.padding(.bottom, 14)
                        Field(label: "帰寮予定時刻") {
                            ApplyTimeField(date: $outingReturnTime)
                        }.padding(.bottom, 14)
                    }
                    if isGuest {
                        Field(label: "来訪者氏名", required: true) {
                            TField(text: $dest, placeholder: "来訪者氏名を入力")
                        }.padding(.bottom, 14)
                    }
                    if isParcel {
                        Field(label: "荷物の概要", required: true) {
                            TField(text: $dest, placeholder: "配送業者・個数")
                        }.padding(.bottom, 14)
                    }

                    // guest：来訪日 + 帰寮予定時刻（outing 自有外出日字段；repair/parcel 无日期）
                    if isGuest {
                        Field(label: "日付", required: true) {
                            ApplyDateField(date: $date, minDate: ApplyFormDate.tomorrow)
                        }
                        .padding(.bottom, 14)
                        Field(label: "帰寮予定時刻", required: true) {
                            ApplyTimeField(date: $time)
                        }
                        .padding(.bottom, 14)
                    }

                    if needsTransport {
                        Field(label: "交通手段") {
                            ChipGroup(options: ["電車", "バス", "車", "徒歩", "その他"], value: $transport)
                        }.padding(.bottom, 14)
                    }

                    if isOuting {
                        Field(label: "タクシー予約") {
                            VStack(alignment: .leading, spacing: 8) {
                                Toggle(isOn: $taxiReserved) {
                                    Text("タクシーを予約する")
                                        .font(.system(size: 13))
                                        .foregroundStyle(T.ink)
                                }
                                .tint(T.primary)
                                if taxiReserved {
                                    ApplyTimeField(date: $taxiTime)
                                }
                            }
                        }.padding(.bottom, 14)
                    }

                    if isRepair {
                        Field(label: "場所", required: true) {
                            VStack(spacing: 8) {
                                RadioCard(selection: $repairPlace, value: "自室", title: "自室")
                                RadioCard(selection: $repairPlace, value: "共用スペース", title: "共用スペース")
                                RadioCard(selection: $repairPlace, value: "水回り", title: "水回り")
                                RadioCard(selection: $repairPlace, value: "その他", title: "その他")
                            }
                        }.padding(.bottom, 14)

                        Field(label: "写真") {
                            VStack(spacing: 6) {
                                Ic.camera(24).foregroundStyle(T.primary)
                                Text("写真を追加（任意）")
                                    .font(.system(size: 13))
                                    .foregroundStyle(T.inkSub)
                            }
                            .frame(maxWidth: .infinity)
                            .padding(20)
                            .background {
                                RoundedRectangle(cornerRadius: 14, style: .continuous)
                                    .strokeBorder(style: StrokeStyle(lineWidth: 1.5, dash: [6, 4]))
                                    .foregroundStyle(T.inkFaint)
                            }
                        }.padding(.bottom, 14)
                    }

                    Field(label: isRepair ? "不具合の内容" : "理由・詳細", required: true) {
                        TArea(text: $reason,
                              placeholder: isRepair ? "状態を具体的に" : "申請の理由を具体的に",
                              rows: 4)
                    }.padding(.bottom, 14)

                    if !isRepair && !isParcel {
                        Field(label: "連絡先", hint: "緊急時用") {
                            TField(text: $contact, keyboard: .phonePad)
                        }.padding(.bottom, 14)
                    }

                    // 注：原「下書き保存」假按钮（只弹 toast 不存）已移除，同 StayForm。本地草稿留 v1.1。
                    HStack(spacing: 10) {
                        Button {
                            // 外出 = 直接接 outings 后端（跳过演示确认页）；
                            // 修繕/来訪/代理(仅生产) = 直接接 misc-requests（确认页拿不到表单数据，必须在此提交）；
                            // 其他类型 + 演示版全部仍走确认页。
                            if isOuting {
                                Task { await submitOuting() }
                            } else {
                                #if DEMO
                                    router.go(.applyPreview(kind: kind))
                                #else
                                    if isMiscKind {
                                        Task { await submitMisc() }
                                    } else {
                                        router.go(.applyPreview(kind: kind))
                                    }
                                #endif
                            }
                        } label: {
                            Text(submitButtonLabel)
                                .font(.system(size: 14, weight: .bold))
                                .foregroundStyle(.white)
                                .frame(maxWidth: .infinity, minHeight: 52)
                                .background {
                                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                                        .fill(canSubmit && !isSubmittingOuting ? T.primary : T.inkFaint)
                                }
                        }
                        .buttonStyle(.plain)
                        .disabled(!canSubmit || isSubmittingOuting)
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 4).padding(.bottom, 24)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl)
        .onAppear { prefillContact() }
        .onChangeCompat(of: app.currentUser?.account) { prefillContact() } // 自动登录冷启动：真实用户晚到时补填一次
    }

    /// 预填本人联系电话：照搬 StayForm.prefillContact —— 生产只在拿到真实 currentUser 后填（冷启动假人 SEED.user 不写入），演示构建直接用 SEED 占位。didPrefillContact 守卫防重复覆盖，学生可手动改。
    private func prefillContact() {
        guard !didPrefillContact else { return }
        #if DEMO
            contact = app.displayUser.phone
            didPrefillContact = true
        #else
            guard app.currentUser != nil else { return }
            contact = app.displayUser.phone
            didPrefillContact = true
        #endif
    }

    /// A1：外出申请直接接 outings 后端提出。
    /// 事后确认制 —— 提交即生效可以出门，pending 只是「先生の記録待ち」不是等放行。
    /// 演示构建不连后端、直接跳完成页讲叙事。
    private func submitOuting() async {
        guard !isSubmittingOuting else { return }
        guard !isOutingBanned else { return } // 禁足中兜底（按钮本就置灰、这里防将来改动漏掉）
        isSubmittingOuting = true
        defer { isSubmittingOuting = false }
        #if DEMO
            app.showToast("外出申請を提出しました")
            router.go(.applyDone(kind: "outing"))
        #else
            let trimmedDest = dest.trimmingCharacters(in: .whitespacesAndNewlines)
            let trimmedReason = reason.trimmingCharacters(in: .whitespacesAndNewlines)
            let body = OutingCreateBody(
                outing_date: ApplyFormDate.formatYMD(outingDate),
                destination: trimmedDest.isEmpty ? nil : trimmedDest,
                leave_time: ApplyFormDate.formatHM(outingLeaveTime),
                return_time: ApplyFormDate.formatHM(outingReturnTime),
                taxi_reservation_time: taxiReserved ? ApplyFormDate.formatHM(taxiTime) : nil,
                reason: trimmedReason.isEmpty ? nil : trimmedReason
            )
            let tokenAtStart = app.authToken
            do {
                _ = try await OutingsAPI.create(body)
                guard app.authToken == tokenAtStart else { return } // 切账号 / 登出后不在新会话弹 toast / 导航
                app.showToast("外出申請を提出しました")
                router.go(.applyDone(kind: "outing"))
            } catch let APIError.unprocessable(msg) {
                // 外出日是过去 / 时刻矛盾 等的输入错误
                app.showToast(msg)
            } catch APIError.unauthorized {
                app.authToken = nil
                router.replace(.login)
            } catch APIError.network {
                app.showToast("通信エラーが発生しました。電波を確認してください")
            } catch {
                app.showToast(APIErrorPresenter.userMessage(for: error, fallback: "外出申請の提出に失敗しました"))
            }
        #endif
    }

    /// 功能⑥：修繕 / 来訪 / 代理受取直接接 misc-requests 后端提出（仅生产调用；演示走确认页不调）。
    /// 确认页 ApplyPreviewView 只传 kind、拿不到表单数据 → 必须在此（数据所在处）提交。
    private func submitMisc() async {
        guard !isSubmittingOuting else { return }
        isSubmittingOuting = true
        defer { isSubmittingOuting = false }

        // iOS kind → 后端 kind（iOS「parcel」=「代理受取」对应后端 proxy_receipt）。
        let backendKind: String
        switch kind {
        case "repair": backendKind = "repair"
        case "guest": backendKind = "guest"
        case "parcel": backendKind = "proxy_receipt"
        default: return
        }

        // subject / target_date 按类型取：
        //   修繕   = 場所(repairPlace) / 无日期
        //   来訪者 = 来訪者氏名(dest) / 来訪日(date)
        //   代理受取 = 荷物概要(dest) / 无日期
        let trimmedDest = dest.trimmingCharacters(in: .whitespacesAndNewlines)
        let subject: String
        let targetDate: String?
        switch kind {
        case "repair":
            subject = repairPlace
            targetDate = nil
        case "guest":
            subject = trimmedDest.isEmpty ? type.name : trimmedDest
            targetDate = ApplyFormDate.formatYMD(date)
        default: // parcel
            subject = trimmedDest.isEmpty ? type.name : trimmedDest
            targetDate = nil
        }

        let trimmedReason = reason.trimmingCharacters(in: .whitespacesAndNewlines)
        let body = MiscRequestBody(
            kind: backendKind,
            subject: subject,
            detail: trimmedReason.isEmpty ? nil : trimmedReason,
            target_date: targetDate
        )
        let tokenAtStart = app.authToken
        do {
            _ = try await MiscRequestsAPI.create(body)
            guard app.authToken == tokenAtStart else { return } // 切账号 / 登出后不在新会话弹 toast / 导航
            app.showToast("\(type.name)申請を提出しました")
            router.go(.applyDone(kind: kind))
        } catch let APIError.unprocessable(msg) {
            app.showToast(msg)
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch APIError.network {
            app.showToast("通信エラーが発生しました。電波を確認してください")
        } catch {
            app.showToast(APIErrorPresenter.userMessage(for: error, fallback: "申請の提出に失敗しました"))
        }
    }
}

#Preview("GenericApplyForm · outing") {
    GenericApplyForm(kind: "outing")
        .environmentObject(RouterStore(initial: .applyForm(kind: "outing")))
        .environmentObject(AppStore())
}

#Preview("GenericApplyForm · repair") {
    GenericApplyForm(kind: "repair")
        .environmentObject(RouterStore(initial: .applyForm(kind: "repair")))
        .environmentObject(AppStore())
}

// ============================================================================
// §2.11 ApplyPreviewView — 確認画面
// ============================================================================

struct ApplyPreviewView: View {
    let kind: String
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    private var type: ApplyTypeMeta {
        applyType(kind)
    }

    private var rows: [(String, String)] {
        var base: [(String, String)] = [
            ("種別", type.name),
            ("申請番号", "A-TEMP"),
            ("申請者", "12番 · Nishimura Aoi"),
        ]
        switch kind {
        case "outing": base += [("行き先", "新宿")]
        case "stay": base += [("行き先", "実家"), ("期間", "2026-04-25 〜 04-26"), ("保護者", "同意済")]
        case "holiday": base += [("行き先", "実家 福岡"), ("期間", "2026-04-28 〜 05-05"), ("保護者", "同意済")]
        case "repair": base += [("場所", "自室"), ("依頼日", "2026-04-22")]
        case "parcel": base += [("荷物", "小包1件"), ("配達予定", "2026-04-23")]
        case "guest": base += [("来訪者", "山田 花子"), ("来訪日", "2026-04-25")]
        case "return": base += [("日付", "2026-04-25"), ("帰寮時刻", "17:30")]
        default: break
        }
        base.append(("理由", "（入力された理由が表示されます）"))
        return base
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "申請内容の確認", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // Info banner
                    Text("ℹ 提出後は審査待ちとなります。承認されるまでは内容の変更が可能です。")
                        .font(.system(size: 12.5))
                        .foregroundStyle(T.primaryDk)
                        .lineSpacing(3)
                        .padding(.horizontal, 16).padding(.vertical, 14)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background {
                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                .fill(T.accent.opacity(0.1))
                        }
                        .padding(.bottom, 18)

                    Card(padding: 0) {
                        VStack(spacing: 0) {
                            ForEach(Array(rows.enumerated()), id: \.offset) { i, pair in
                                HStack(alignment: .top, spacing: 0) {
                                    Text(pair.0)
                                        .font(.system(size: 12.5))
                                        .foregroundStyle(T.inkSub)
                                        .frame(width: 100, alignment: .leading)
                                    Text(pair.1)
                                        .font(.system(size: 13.5, weight: .semibold))
                                        .foregroundStyle(T.ink)
                                        .frame(maxWidth: .infinity, alignment: .leading)
                                }
                                .padding(.horizontal, 16).padding(.vertical, 14)
                                .overlay(alignment: .top) {
                                    if i > 0 {
                                        Rectangle().fill(T.hair).frame(height: 0.5)
                                    }
                                }
                            }
                        }
                    }
                    .padding(.bottom, 20)

                    HStack(spacing: 10) {
                        Button {
                            router.back()
                        } label: {
                            Text("戻る")
                                .font(.system(size: 14, weight: .bold))
                                .foregroundStyle(T.inkSub)
                                .frame(maxWidth: .infinity, minHeight: 52)
                                .background {
                                    RoundedRectangle(cornerRadius: 16, style: .continuous).fill(T.paper)
                                }
                                .overlay {
                                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                                        .stroke(T.hair, lineWidth: 1.5)
                                }
                        }
                        .buttonStyle(.plain)

                        PrimaryButton(title: "提出する") {
                            app.showToast("申請を提出しました")
                            Task {
                                try? await Task.sleep(nanoseconds: 400_000_000)
                                await MainActor.run {
                                    router.go(.applyDone(kind: kind))
                                }
                            }
                        }
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 4).padding(.bottom, 24)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl)
    }
}

#Preview("ApplyPreview") {
    ApplyPreviewView(kind: "stay")
        .environmentObject(RouterStore(initial: .applyPreview(kind: "stay")))
        .environmentObject(AppStore())
}

// ============================================================================
// §2.12 ApplyDoneView — 提出完了
// ============================================================================

struct ApplyDoneView: View {
    let kind: String
    @EnvironmentObject var router: RouterStore

    private var type: ApplyTypeMeta {
        applyType(kind)
    }

    /// 外出是事后确认制（2026-07-22）：提交完就能走，没有「審査」这一步。这一屏是学生按下
    /// 提出后看到的第一个界面，原来的通用文案写「審査完了時に通知でお知らせします」+
    /// 「審査時間の目安 1〜2 時間」，等于当面推翻上一屏刚说过的「承認不要」，所以外出走自己一套。
    private var isOuting: Bool {
        kind == "outing"
    }

    var body: some View {
        VStack(spacing: 0) {
            Spacer()
            VStack(spacing: 0) {
                // Check badge
                ZStack {
                    RoundedRectangle(cornerRadius: 28, style: .continuous)
                        .fill(LinearGradient(
                            colors: [T.primary, T.accent],
                            startPoint: .topLeading, endPoint: .bottomTrailing
                        ))
                        .shadow(color: T.primary.opacity(0.35), radius: 24, x: 0, y: 16)
                    Image(systemName: "checkmark")
                        .font(.system(size: 40, weight: .bold))
                        .foregroundStyle(.white)
                }
                .frame(width: 96, height: 96)
                .padding(.bottom, 22)

                Text("申請を提出しました")
                    .font(.system(size: 24, weight: .heavy))
                    .foregroundStyle(T.ink)
                    .padding(.bottom, 8)

                // 外出的第二句直接复用详情页那句已定稿的说明，不另造日语。
                Text(
                    isOuting
                        ? "外出申請を受け付けました。\n確認は記録のためで、外出は可能です"
                        : "\(type.name)申請を受け付けました。\n審査完了時に通知でお知らせします。"
                )
                .font(.system(size: 14))
                .foregroundStyle(T.inkSub)
                .multilineTextAlignment(.center)
                .lineSpacing(4)
                .padding(.bottom, 28)

                // Info card
                // IX-006: 原来这里显示写死的假申请号「A-240422-07」。后端 ApplicationOut 只有
                // UUID、没有人类可读的申请号，所以去掉这行假数据，只留预想审查时间。
                // 外出没有审查这一步 → 整张卡不出现（写「0 時間」之类反而更让人误会要等）。
                if !isOuting {
                    VStack(spacing: 4) {
                        HStack {
                            Text("審査時間の目安").font(.system(size: 12)).foregroundStyle(T.inkSub)
                            Spacer()
                            Text("1〜2 時間")
                                .font(.system(size: 12, weight: .bold))
                                .foregroundStyle(T.ink)
                        }
                    }
                    .padding(.horizontal, 16).padding(.vertical, 14)
                    .frame(maxWidth: .infinity)
                    .background {
                        RoundedRectangle(cornerRadius: 14, style: .continuous).fill(T.pearl)
                    }
                    .padding(.bottom, 28)
                }

                // IX-006: 原来左边还有个「詳細を見る」按钮跳 .applyDetail(id: "A-240422-07") 假 id，
                // 而且详情页现在还读 SEED 假数据、传真 id 也查不到。先去掉这个按钮，
                // 只留「一覧へ」跳申请列表，用户在列表里看自己真实的申请（列表接后端见 IX-007）。
                PrimaryButton(title: "一覧へ") {
                    router.replace(.apply)
                }
            }
            .padding(.horizontal, 28)
            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.paper)
    }
}

#Preview("ApplyDone") {
    ApplyDoneView(kind: "stay")
        .environmentObject(RouterStore(initial: .applyDone(kind: "stay")))
        .environmentObject(AppStore())
}

// ============================================================================
// §2.13 ApplyDetailView — 申請詳細 + workflow 進捗
// ============================================================================

struct ApplyDetailView: View {
    let id: String
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    #if DEMO
        /// ⚠️ 仅 DEMO，生产严禁引用 —— item / steps / otherDetailBody 整组都读 SEED.applications（假种子）+ 编造步骤时间。
        /// 生产路径（stayOrOtherBody 的 #else）只走真后端 StayDetailView(id)，不碰这三个成员。
        /// 找不到返回 nil（旧代码 `?? SEED.applications[0]` 退回第一条 → SEED 为空数组时下标越界崩溃）。
        /// 改 optional，下面 steps / otherDetailBody 找不到时显示空状态。
        private var item: ApplicationItem? {
            SEED.applications.first(where: { $0.id == id })
        }
    #endif

    fileprivate struct StepMeta {
        let k: String
        let label: String
        let done: Bool
        let active: Bool
        let time: String?
        let label2: String?
        var activeNote: String? = nil // 进行中那一步显示的副标题（如审查中说明 / 确认中说明）
        /// 这一步以「失败」告终（外出被却下）。done 打绿勾、active 是黄色进行中，
        /// 两个都不占的话只剩灰圈数字＝看着像还没轮到，把终局状态显示成了半路状态。
        var failed: Bool = false
    }

    #if DEMO
        /// ⚠️ 仅 DEMO，生产严禁引用 —— 读 item（SEED）+ 编造步骤时间，只被 otherDetailBody（亦 DEMO）消费。
        fileprivate var steps: [StepMeta] {
            guard let a = item else { return [] }
            let submitTime = a.date + " 10:24"
            // 外出申請（outing）= 事后确认制，没有「審査」步骤（itsuki 2026-06-04 定 2 步 /
            // 2026-07-22 改事后确认）。第 2 步不是放行闸、只是老师事后留记录，所以文案跟生产路径
            // 的 OutingDetailView.steps 逐字对齐 —— 演示版给宿管看的就是真实语义，不能停在旧文案。
            // 确认老师名演示版用代表性的「松本 先生」（生产读后端 confirmed_by_name）。
            if a.type == "outing" {
                // 四态各走各的，别只分 approved / 非 approved —— 那样 rejected 和 withdrawn
                // 会显示成「先生の記録待ち」+「外出は可能です」，等于告诉学生一次被却下 / 自己
                // 取消掉的外出还能去（分支逻辑跟生产 OutingDetailView.steps 一一对应）。
                let confirmed = a.status == "approved"
                let rejected = a.status == "rejected"
                let withdrawn = a.status == "withdrawn"
                let isOpen = !confirmed && !rejected && !withdrawn
                let secondLabel: String
                if confirmed {
                    secondLabel = "確認"
                } else if rejected {
                    secondLabel = "却下"
                } else if withdrawn {
                    secondLabel = "取消"
                } else {
                    secondLabel = "先生の記録待ち"
                }
                let processedTime: String? = isOpen ? nil : a.date + " 11:02"
                return [
                    .init(k: "submit", label: "提出", done: true, active: false, time: submitTime, label2: nil),
                    .init(k: "confirm",
                          label: secondLabel,
                          // 却下不打绿勾（绿勾=办成了，用在却下上给错信号），改用 failed 出红叉
                          done: confirmed, active: isOpen, time: processedTime,
                          label2: confirmed || rejected ? "松本 先生" : nil,
                          activeNote: isOpen ? "確認は記録のためで、外出は可能です" : nil,
                          failed: rejected),
                ]
            }
            let reviewDone = a.status == "approved" || a.status == "rejected"
            let reviewActive = a.status == "pending"
            let reviewTime: String? = reviewActive ? nil : a.date + " 11:02"
            let finalDone = a.status == "approved" || a.status == "rejected"
            let finalLabel2 = a.status == "rejected" ? "差し戻し" : "承認"
            return [
                .init(k: "submit", label: "提出", done: true, active: false, time: submitTime, label2: nil),
                .init(k: "review", label: "審査", done: reviewDone, active: reviewActive, time: reviewTime, label2: nil, activeNote: "担当者：松本 先生 · 審査中"),
                .init(k: "final", label: "完了", done: finalDone, active: false, time: nil, label2: finalLabel2),
            ]
        }
    #endif

    var body: some View {
        if id.hasPrefix("outing:") {
            // 生产：外出申请走独立 outings 后端，ApplyListView 给外出 id 加了 "outing:" 前缀
            OutingDetailView(outingId: String(id.dropFirst("outing:".count)))
        } else {
            stayOrOtherBody
        }
    }

    @ViewBuilder
    private var stayOrOtherBody: some View {
        // 4-30 後續: 出寮届系（stay/holiday/returncountry/return）→ 显示 chain timeline (StayDetailView)
        // 老师 #5 要求：申请人能看到 chain 上每个役职是否已许可
        #if DEMO
            // 演示：SEED 含修繕/来訪/代理受取等「出寮届以外」类型，按 SEED 的 type 路由
            // （otherDetailBody 读 SEED + 编造步骤时间，仅讲叙事用）。
            if let it = item, ["stay", "holiday", "return", "returncountry"].contains(it.type) {
                StayDetailView(id: id)
            } else {
                otherDetailBody
            }
        #else
            // 生产（IX-007 Option A）：出寮届系走真后端 StayDetailView(id)。
            // misc-requests 后端有 create + /mine 一览、缺单条 detail 端点；学生 app 暂未接一览页，
            // 故生产提交后暂无法在 app 内检索单条详情，详情页统一走 StayDetailView；补齐见 TODO Y-10。
            StayDetailView(id: id)
        #endif
    }

    #if DEMO
        /// ⚠️ 仅 DEMO，生产严禁引用 —— 出寮届以外（修繕 / 来訪 / 代理受取 等）的 demo 3 步 workflow，读 item（SEED）。
        @ViewBuilder
        private var otherDetailBody: some View {
            if let a = item {
                let t = applyType(a.type)
                // 外出走事后确认制自己那套四态文案（approved→「確認済」而非出寮届的「承認済」）。
                // 列表页 ApplyListView 早就按 type 分流了，这里漏了 → 演示版点开详情会显示成
                // 出寮届的措辞，跟同一屏列表里的徽章对不上（2026-07-22 补）。
                let sp = a.type == "outing" ? outingStatusPair(a.status) : statusPair(a.status)
                VStack(spacing: 0) {
                    PageHeader(title: "申請詳細", level: 2)
                    ScrollView {
                        VStack(alignment: .leading, spacing: 0) {
                            // Header card
                            Card(padding: 18) {
                                VStack(alignment: .leading, spacing: 12) {
                                    HStack(spacing: 12) {
                                        Image(systemName: t.icon)
                                            .font(.system(size: 18))
                                            .foregroundStyle(T.primary)
                                            .frame(width: 44, height: 44)
                                            .background {
                                                RoundedRectangle(cornerRadius: 12, style: .continuous).fill(T.pill)
                                            }
                                        VStack(alignment: .leading, spacing: 2) {
                                            Text("\(t.name)申請")
                                                .font(.system(size: 16, weight: .heavy))
                                                .foregroundStyle(T.ink)
                                        }
                                        Spacer()
                                        Pill(text: sp.label, tone: sp.tone)
                                    }

                                    // divider + fields
                                    VStack(alignment: .leading, spacing: 8) {
                                        HStack {
                                            Text("日時").font(.system(size: 13)).foregroundStyle(T.inkSub)
                                            Spacer()
                                            Text(a.date)
                                                .font(.system(size: 13, weight: .semibold))
                                                .foregroundStyle(T.ink)
                                        }
                                        HStack {
                                            Text("内容").font(.system(size: 13)).foregroundStyle(T.inkSub)
                                            Spacer()
                                            Text(a.summary)
                                                .font(.system(size: 13, weight: .semibold))
                                                .foregroundStyle(T.ink)
                                        }
                                    }
                                    .padding(.top, 12)
                                    .overlay(alignment: .top) {
                                        Rectangle().fill(T.hair).frame(height: 0.5)
                                    }
                                }
                            }
                            .padding(.bottom, 16)

                            // Progress workflow card (4-段 workflow: 担任 → 寮務課長 → 管理課長 → 国際交流部長)
                            Card(padding: 18) {
                                VStack(alignment: .leading, spacing: 0) {
                                    Text("進捗")
                                        .font(.system(size: 12, weight: .bold))
                                        .foregroundStyle(T.inkSub)
                                        .kerning(1.2)
                                        .padding(.bottom, 14)

                                    WorkflowStepsView(steps: steps)
                                }
                            }
                            .padding(.bottom, 16)

                            // Rejected banner
                            // 外出走的是事后确认制：却下只是「老师记了一笔 + 通知你」，既不要求立刻回寮、
                            // 也没有「改一改再交一次」这条路，所以跟出寮届的「差し戻し（打回重交）」不是一回事，
                            // 文案照抄生产 OutingDetailView 的却下卡。出寮届仍是事前审批，原样不动。
                            if a.status == "rejected" {
                                VStack(alignment: .leading, spacing: 6) {
                                    Text(a.type == "outing" ? "⚠ 却下されました" : "⚠ 差し戻し理由")
                                        .font(.system(size: 12, weight: .bold))
                                        .foregroundStyle(T.danger)
                                    if a.type == "outing" {
                                        // 生产版这里显示老师填的却下理由（没填就不显示），演示版没有这个字段
                                        Text("※ 詳しくは寮監に確認してください")
                                            .font(.system(size: 12))
                                            .foregroundStyle(T.inkSub)
                                    } else {
                                        Text("帰寮予定時刻が門限（22:00）を過ぎています。外泊申請として再提出してください。")
                                            .font(.system(size: 13))
                                            .foregroundStyle(T.ink)
                                            .lineSpacing(3)
                                    }
                                }
                                .padding(.horizontal, 16).padding(.vertical, 14)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background {
                                    RoundedRectangle(cornerRadius: 14, style: .continuous).fill(T.dangerBg)
                                }
                                .overlay {
                                    RoundedRectangle(cornerRadius: 14, style: .continuous)
                                        .stroke(T.danger.opacity(0.25), lineWidth: 1)
                                }
                                .padding(.bottom, 16)
                            }

                            // Actions per status
                            // 外出的「取消」语义是「我不去了」（itsuki 2026-07-22 拍板 A），不是撤回一张待批的申请，
                            // 所以文案对象是外出本身；跟生产 OutingDetailView 的按钮逐字一致。
                            if a.status == "pending" {
                                Button {
                                    app.showToast(a.type == "outing" ? "外出を取りやめました" : "申請を取り消しました")
                                    Task {
                                        try? await Task.sleep(nanoseconds: 400_000_000)
                                        await MainActor.run { router.replace(.apply) }
                                    }
                                } label: {
                                    Text(a.type == "outing" ? "外出を取りやめる" : "申請を取り消し")
                                        .font(.system(size: 14, weight: .bold))
                                        .foregroundStyle(T.danger)
                                        .frame(maxWidth: .infinity, minHeight: 48)
                                        .background {
                                            RoundedRectangle(cornerRadius: 14, style: .continuous).fill(T.paper)
                                        }
                                        .overlay {
                                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                                .stroke(T.danger.opacity(0.25), lineWidth: 1.5)
                                        }
                                }
                                .buttonStyle(.plain)
                            } else if a.status == "rejected", a.type != "outing" {
                                // 外出没有「改一改再交一次」——却下只是记录，学生要么直接再提一次新外出，
                                // 要么去问寮監，所以这个按钮不给外出出。
                                PrimaryButton(title: "内容を修正して再提出") {
                                    router.go(.applyForm(kind: a.type))
                                }
                            }
                        }
                        .padding(.horizontal, 20)
                        .padding(.top, 4).padding(.bottom, 24)
                    }
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(T.pearl)
            } else {
                // SEED 里没有该 id（正常不会发生，纯防御）。显示空状态，不再退回第一条假数据。
                VStack(spacing: 12) {
                    PageHeader(title: "申請詳細", level: 2)
                    Spacer()
                    Text("申請が見つかりません")
                        .font(.system(size: 14))
                        .foregroundStyle(T.inkSub)
                    Spacer()
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(T.pearl)
            }
        }
    #endif
}

private struct WorkflowStepsView: View {
    let steps: [ApplyDetailView.StepMeta]

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            ForEach(Array(steps.enumerated()), id: \.offset) { i, s in
                HStack(alignment: .top, spacing: 14) {
                    // rail with circle + line
                    VStack(spacing: 0) {
                        ZStack {
                            Circle().fill(s.failed ? T.danger : (s.done ? T.ok : (s.active ? T.warn : T.pill)))
                                .frame(width: 24, height: 24)
                            if s.failed {
                                Image(systemName: "xmark")
                                    .font(.system(size: 11, weight: .bold))
                                    .foregroundStyle(.white)
                            } else if s.done {
                                Image(systemName: "checkmark")
                                    .font(.system(size: 11, weight: .bold))
                                    .foregroundStyle(.white)
                            } else {
                                Text("\(i + 1)")
                                    .font(.system(size: 12, weight: .bold))
                                    .foregroundStyle(s.active ? Color.white : T.primary)
                            }
                        }
                        if i < steps.count - 1 {
                            Rectangle()
                                .fill(s.done ? T.ok : T.hair)
                                .frame(width: 2)
                                .frame(maxHeight: .infinity)
                                .padding(.top, 4)
                        }
                    }
                    .frame(width: 24)

                    // body
                    VStack(alignment: .leading, spacing: 2) {
                        Text(s.label2 != nil ? "\(s.label) · \(s.label2!)" : s.label)
                            .font(.system(size: 13.5, weight: .bold))
                            .foregroundStyle(s.active ? T.warn : T.ink)
                        if let t = s.time {
                            Text(t)
                                .font(.system(size: 11, design: .monospaced))
                                .foregroundStyle(T.inkMute)
                        }
                        if s.active, let note = s.activeNote {
                            Text(note)
                                .font(.system(size: 12))
                                .foregroundStyle(T.warnDeep)
                                .padding(.top, 2)
                        }
                    }
                    .padding(.top, 1)
                    .padding(.bottom, i < steps.count - 1 ? 18 : 0)

                    Spacer(minLength: 0)
                }
            }
        }
    }
}

#Preview("ApplyDetail · pending") {
    ApplyDetailView(id: "a1")
        .environmentObject(RouterStore(initial: .applyDetail(id: "a1")))
        .environmentObject(AppStore())
}

#Preview("ApplyDetail · approved") {
    ApplyDetailView(id: "a3")
        .environmentObject(RouterStore(initial: .applyDetail(id: "a3")))
        .environmentObject(AppStore())
}

// ============================================================================
// §2.14 OutingDetailView — 外出申请详情（接 outings 后端 · 2 步进度）A1
//
// 外出是独立 outings 表（不是出寮届 applications）：不过夜 / 一名老师处理即可。
// itsuki 2026-07-22 拍板事后确认制 —— 提交即生效，老师的「確認」是留记录不是放行开关。
// 四态映射 2 步进度：pending=「先生の記録待ち」（外出已可成行）/ approved=「確認済」（显示确认老师名）/
// rejected=「却下」（显示却下老师名 + 却下理由卡，但不要求立刻回寮）/ withdrawn=「取消済」。
// 只在生产被调（ApplyListView 给外出 id 加了 "outing:" 前缀），演示版外出仍走 SEED otherDetailBody。
// ============================================================================

struct OutingDetailView: View {
    let outingId: String
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var loaded: OutingOut?
    @State private var isLoading = false
    @State private var isWithdrawing = false

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "申請詳細", level: 2)
            ScrollView {
                if isLoading, loaded == nil {
                    ProgressView()
                        .tint(T.primary)
                        .frame(maxWidth: .infinity, minHeight: 200)
                } else if let o = loaded {
                    content(o)
                        .padding(.horizontal, 20)
                        .padding(.top, 4)
                        .padding(.bottom, 28)
                } else {
                    VStack(spacing: 12) {
                        Spacer(minLength: 80)
                        Text("申請が見つかりません")
                            .font(.system(size: 14))
                            .foregroundStyle(T.inkSub)
                    }
                    .frame(maxWidth: .infinity)
                }
            }
            .refreshable { await load() }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
        .task { await load() }
    }

    private func content(_ o: OutingOut) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            // 详情卡
            Card(padding: 18) {
                VStack(alignment: .leading, spacing: 12) {
                    HStack(spacing: 12) {
                        Image(systemName: "calendar")
                            .font(.system(size: 18))
                            .foregroundStyle(T.primary)
                            .frame(width: 44, height: 44)
                            .background {
                                RoundedRectangle(cornerRadius: 12, style: .continuous).fill(T.pill)
                            }
                        Text("外出申請")
                            .font(.system(size: 16, weight: .heavy))
                            .foregroundStyle(T.ink)
                        Spacer()
                        let sp = outingStatusPair(o.status)
                        Pill(text: sp.label, tone: sp.tone)
                    }
                    VStack(alignment: .leading, spacing: 8) {
                        outingRow(label: "外出日", value: o.outing_date)
                        if let d = o.destination, !d.isEmpty {
                            divider; outingRow(label: "行き先", value: d)
                        }
                        if let t = o.leave_time {
                            divider; outingRow(label: "外出時刻", value: hm(t))
                        }
                        if let t = o.return_time {
                            divider; outingRow(label: "帰寮予定時刻", value: hm(t))
                        }
                        if let t = o.taxi_reservation_time {
                            divider; outingRow(label: "タクシー予約", value: hm(t))
                        }
                        if let r = o.reason, !r.isEmpty {
                            divider; outingRow(label: "理由", value: r)
                        }
                    }
                    .padding(.top, 12)
                    .overlay(alignment: .top) { Rectangle().fill(T.hair).frame(height: 0.5) }
                }
            }

            // 进捗（2 步）
            Card(padding: 18) {
                VStack(alignment: .leading, spacing: 0) {
                    Text("進捗")
                        .font(.system(size: 12, weight: .bold))
                        .foregroundStyle(T.inkSub).kerning(1.2)
                        .padding(.bottom, 14)
                    WorkflowStepsView(steps: steps(o))
                }
            }

            // 却下通知（仅 rejected）—— 事后确认制下却下只是记录 + 通知，不要求学生立刻回寮，
            // 所以这里不写「すぐ帰寮してください」，只给理由（老师填了才有）+ 固定的问询指引。
            if o.status == "rejected" {
                VStack(alignment: .leading, spacing: 6) {
                    Text("⚠ 却下されました")
                        .font(.system(size: 12, weight: .bold))
                        .foregroundStyle(T.danger)
                    if let reason = o.reject_reason?.trimmingCharacters(in: .whitespacesAndNewlines),
                       !reason.isEmpty
                    {
                        Text(reason)
                            .font(.system(size: 13))
                            .foregroundStyle(T.ink)
                            .lineSpacing(3)
                    }
                    Text("※ 詳しくは寮監に確認してください")
                        .font(.system(size: 12))
                        .foregroundStyle(T.inkSub)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, 16).padding(.vertical, 14)
                .background {
                    RoundedRectangle(cornerRadius: 14, style: .continuous).fill(T.dangerBg)
                }
                .overlay {
                    RoundedRectangle(cornerRadius: 14, style: .continuous)
                        .stroke(T.danger.opacity(0.25), lineWidth: 1)
                }
            }

            // 撤回（仅 pending）——事后确认制下语义是「我不去了」，不是「撤回一张待批的申请」，
            // 所以文案对象是「外出」本身而不是「申請」（itsuki 2026-07-22 拍板 A）。出寮届那侧
            // 仍是事前审批，保持「申請を取り消し」不动。
            if o.status == "pending" {
                Button {
                    Task { await withdraw(o) }
                } label: {
                    Text(isWithdrawing ? "取りやめ中…" : "外出を取りやめる")
                        .font(.system(size: 14, weight: .bold))
                        .foregroundStyle(T.danger)
                        .frame(maxWidth: .infinity, minHeight: 48)
                        .background {
                            RoundedRectangle(cornerRadius: 14, style: .continuous).fill(T.paper)
                        }
                        .overlay {
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .stroke(T.danger.opacity(0.25), lineWidth: 1.5)
                        }
                }
                .buttonStyle(.plain)
                .disabled(isWithdrawing)
            }
        }
    }

    private var divider: some View {
        Rectangle().fill(T.hair).frame(height: 0.5).padding(.vertical, 9)
    }

    private func outingRow(label: String, value: String) -> some View {
        HStack(alignment: .firstTextBaseline) {
            Text(label).font(.system(size: 13)).foregroundStyle(T.inkSub)
            Spacer()
            Text(value)
                .font(.system(size: 13, weight: .semibold))
                .foregroundStyle(T.ink)
                .multilineTextAlignment(.trailing)
        }
    }

    /// 时刻 "HH:mm:ss" → "HH:mm"（去秒、UI 简洁）
    private func hm(_ s: String) -> String {
        let parts = s.split(separator: ":")
        return parts.count >= 2 ? "\(parts[0]):\(parts[1])" : s
    }

    /// 把 OutingOut 的 datetime（submitted_at / confirmed_at）显示成 JST "yyyy-MM-dd HH:mm"。
    /// OutingOut 由 String 改 Date（对齐后端 datetime）后，弃用旧的字符串分割，改用标准格式化器。
    private func fmtDateTime(_ date: Date) -> String {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd HH:mm"
        f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = TimeZone(identifier: "Asia/Tokyo")
        return f.string(from: date)
    }

    /// 四态 → 2 步进度（提出 → 記録）。
    /// 事后确认制：第 2 步不是放行闸，只是老师事后留记录 —— 所以 pending 的文案是「先生の記録待ち」不是「確認待ち」。
    /// 处理老师名（confirmed_by_name）在 approved / rejected 两态都显示，按状态分别拼成「確認 · ○○」/「却下 · ○○」。
    private func steps(_ o: OutingOut) -> [ApplyDetailView.StepMeta] {
        let confirmed = o.status == "approved"
        let rejected = o.status == "rejected"
        let withdrawn = o.status == "withdrawn"
        let submitTime = fmtDateTime(o.submitted_at)
        // 后端 confirmed_at 是「処理時刻」——approved 是确认时刻、rejected 是却下时刻，两态共用
        let processedTime = o.confirmed_at.map { fmtDateTime($0) }
        let secondLabel: String
        if confirmed {
            secondLabel = "確認"
        } else if rejected {
            secondLabel = "却下"
        } else if withdrawn {
            secondLabel = "取消"
        } else {
            secondLabel = "先生の記録待ち"
        }
        let isOpen = !confirmed && !rejected && !withdrawn // 还没被老师处理、也没被自己取消
        return [
            .init(k: "submit", label: "提出", done: true, active: false, time: submitTime, label2: nil),
            .init(k: "confirm",
                  label: secondLabel,
                  // 却下不打绿勾（WorkflowStepsView 的 done 是绿勾，用在「却下」上会给错信号），改走 failed 出红叉
                  done: confirmed,
                  active: isOpen,
                  time: processedTime,
                  label2: confirmed || rejected ? o.confirmed_by_name : nil,
                  activeNote: isOpen ? "確認は記録のためで、外出は可能です" : nil,
                  failed: rejected),
        ]
    }

    private func load() async {
        isLoading = true
        defer { isLoading = false }
        guard let uuid = UUID(uuidString: outingId) else {
            app.showToast("申請が見つかりませんでした")
            router.back()
            return
        }
        do {
            loaded = try await OutingsAPI.detail(id: uuid)
        } catch APIError.unauthorized {
            app.authToken = nil
            router.back()
        } catch {
            app.showToast(APIErrorPresenter.userMessage(
                for: error, fallback: "外出申請の取得に失敗しました"
            ))
            router.back()
        }
    }

    /// 撤回 pending 的外出申请；并发被老师确认时后端回 409 → 重拉最新状态。
    private func withdraw(_ o: OutingOut) async {
        guard !isWithdrawing else { return }
        isWithdrawing = true
        defer { isWithdrawing = false }
        do {
            loaded = try await OutingsAPI.withdraw(id: o.id)
            app.showToast("外出を取りやめました")
        } catch let APIError.unprocessable(msg) {
            app.showToast(msg)
        } catch APIError.server(409, _) {
            // 409 = 提交后老师已经确认 / 却下了。事后确认制下老师一般是学生回来后才批量处理，
            // 撞上这里多半意味着这次外出已经过去了；万一是老师手快，学生仍需要一条出路 → 指向寮監。
            app.showToast("先生が処理した後は取りやめできません。寮監に直接お伝えください")
            await load()
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch APIError.network {
            app.showToast("通信エラーが発生しました。電波を確認してください")
        } catch {
            app.showToast(APIErrorPresenter.userMessage(for: error, fallback: "外出の取りやめに失敗しました"))
        }
    }
}

/// 外出四态 → 状态 Pill（事后确认制语义：承認不要 / 確認済 / 却下 / 取消済）
///
/// pending 用 .accent（品牌色）不用 .warn（琥珀警示色）—— 事后确认制下「提交即生效」不是等待放行的警示态，
/// 琥珀色会让学生误以为还不能出门。
private func outingStatusPair(_ status: String) -> (label: String, tone: Pill.Tone) {
    switch status {
    case "pending": return ("承認不要", .accent)
    case "approved": return ("確認済", .ok)
    case "rejected": return ("却下", .danger)
    case "withdrawn": return ("取消済", .neutral)
    // DC-01: 显式列出后端四值；未知值（后端将来新增 status）落「不明な状態」而非被误显成「承認不要」（pending 标签）。
    // 撤回 / 进度处用的是精确 == 比较，未知值本就不会被误判为某个已知状态。
    default: return ("不明な状態", .neutral)
    }
}
