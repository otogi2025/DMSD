// ApplyStubs.swift · Apply feature 13 views (v2 HTML-fidelity rewrite)
// ⭐ Agent D · v2 · 1:1 对照 refs/phaseB_src/100ba570__ApplyListPage_ApplyNewPage_ApplyFormPage.js
// 8 APPLY_TYPES · StayForm 8 section · GenericApplyForm · Detail workflow · Preview · Done
// 注意:
//   - 日文字符串逐字照抄 JSX
//   - 颜色全部走 T.* tokens
//   - SF Symbols 用 Ic.* (JSX 源用 SVG path 但 Ic 已是视觉接近的 SF Symbol wrapper,
//     保持 Agent D 与 Foundation 的一致性, 避免 feature 级重复造轮)
//   - StayForm 对应 JSX line 92-292 的 8 section (本人連絡先 / 同行者 / 日時 / 方法 / 宿泊先 / 食事 / 理由 / 備考)

import SwiftUI

// MARK: - APPLY_TYPES (8 kind · 严格对照 JSX line 3-12)

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
    .init(k: "studyAbsence", name: "学習欠席", icon: "book.closed", desc: "晚自习の欠席届（前半・後半・両方）"),
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
    case "rejected": return ("差戻", .danger)
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

    private let tabs: [(String, String)] = [
        ("all", "すべて"),
        ("pending", "審査中"),
        ("approved", "承認済"),
        ("draft", "下書き"),
    ]

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
        // 外出是独立 outings 表、三态语义不同（確認待ち/確認済/取消済），别套出寮届的「審査中/承認済」
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
// §2.2 ApplyNewView — L2 · 8 APPLY_TYPES grid 2 col
// ============================================================================

struct ApplyNewView: View {
    @EnvironmentObject var router: RouterStore

    private let cols: [GridItem] = [
        GridItem(.flexible(), spacing: 10),
        GridItem(.flexible(), spacing: 10),
    ]

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

                    LazyVGrid(columns: cols, spacing: 10) {
                        ForEach(APPLY_TYPES, id: \.k) { t in
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
        // 老師反饋 #1-#4 対応: 出寮届 = 帰省 / 外泊 / 帰国 三種類はすべて StayForm へ
        // §7.2 字段累積表に従い動的表示（StayForm 内部で kind 判定）
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
// §2.4 StayForm ⭐⭐⭐ — 出寮届 (帰省 / 外泊 / 帰国) · §7.2 spec 実装
//
// 老師 38 条反饋 #1-#4 対応:
//   #1 学生は自分のみ提出可 → 申請者本人 = SEED.user 固定 read-only · 提出時 assert
//   #2 三種類字段 (帰省 / 外泊 / 帰国) 累積モデル
//   #3 出寮日 = 明日以降のみ (DatePicker minDate = tomorrow)
//   #4 不要な field は隠す (kind 別 dynamic 表示)
//
// 字段累積:
//   帰省  : 出寮日 / 帰省方法 / 出寮時刻 / 帰寮日 / 帰寮方法 / 帰寮時刻
//   外泊  : 帰省字段 + 外泊地点(可多个) + 食事不要期間
//   帰国  : 外泊字段 + 出発空港 / 出発時刻 / 到着空港 / 到着時刻
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

    // ── §7.2 共通字段 (帰省/外泊/帰国 三種類すべて) ─────────────────────────
    @State private var leaveDate: Date = StayForm.tomorrow
    @State private var leaveTime: Date = StayForm.parseHM("18:00") ?? Date()
    @State private var leaveMethod: String = "JR"
    @State private var returnDate: Date = StayForm.tomorrow
    @State private var returnTime: Date = StayForm.parseHM("20:00") ?? Date()
    @State private var returnMethod: String = "JR"

    // ── 外泊 / 帰国 only ─────────────────────────────────────────────────
    // 滞在先 1 件 = 稳定 id + 地址。用 id 当列表项身份（不用数组下标），
    // 删中间一行时输入框内容 / 焦点不会串到别行（IX-032）。
    @State private var stayPlaces: [StayPlaceItem] = [StayPlaceItem()] // 外泊地点(可多个)
    @State private var skipStartDate: Date = StayForm.tomorrow
    @State private var skipStartMeal: String = "夕食" // 朝食 / 昼食 / 夕食
    @State private var skipEndDate: Date = StayForm.tomorrow
    @State private var skipEndMeal: String = "朝食"
    @State private var skipEnabled: Bool = true // 食事不要期間 を申告するか

    // ── 帰国 only ────────────────────────────────────────────────────────
    @State private var departAirport: String = ""
    @State private var departFlightTime: Date = StayForm.parseHM("10:00") ?? Date()
    @State private var arriveAirport: String = ""
    @State private var arriveFlightTime: Date = StayForm.parseHM("14:00") ?? Date()

    /// ── 共通: 理由 ────────────────────────────────────────────────────────
    @State private var reason: String = ""

    /// ── 出租车预约「タクシー予約」— 出寮方法选了「タクシー」时想坐车的时刻（itsuki 2026-06-04：废止独立开关，改成出寮方法连动）──
    @State private var taxiTime: Date = StayForm.parseHM("18:00") ?? Date()

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

    // 提出可否: 必須項目が埋まっているか
    private var canSubmit: Bool {
        if reason.isEmpty { return false }
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
            if departAirport.isEmpty || arriveAirport.isEmpty { return false }
        }
        return true
    }

    /// 「寮生特別運行の時刻表を見る」按钮 — 出寮方法 / 帰寮方法 下方各放一个，
    /// 因为这两组移动方式里都能选「寮生特別運行」。点了跳到特別運航便一覧（BusListView）。
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
                        kindBanner(text: "⏰ 帰省申請は毎週水曜日 18:00 が締切です")
                    } else if isReturnCountry {
                        kindBanner(text: "✈️ 帰国申請は航空券確定後に提出してください")
                    } else {
                        kindBanner(text: "📝 外泊申請は出発 3 日前までに提出してください")
                    }

                    // ── Header card (届の種類) ──────────────────────────────
                    headerCard
                        .padding(.bottom, 20)

                    // ── §1 申請者本人 · SEED.user 自動 (#1 学生只能提交自己的) ──
                    SectionLabel(n: "1", label: "申請者本人")
                    Card(padding: 0) {
                        VStack(spacing: 0) {
                            InfoRow(k: "学号", v: meAccount, isFirst: true)
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
                                    DateField(date: $leaveDate, minDate: StayForm.tomorrow)
                                    TimeField(date: $leaveTime)
                                }
                                Text("※ 出寮日は明日以降のみ選択できます")
                                    .font(.system(size: 10.5))
                                    .foregroundStyle(T.inkMute)
                            }
                            // 帰省方法 (= 出寮時の移動手段)
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
                                    TimeField(date: $taxiTime)
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
                                    DateField(date: $returnDate, minDate: leaveDate)
                                    TimeField(date: $returnTime)
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

                    // ── §5 外泊地点（外泊 / 帰国 のみ · 動的表示 #4）──────────
                    if needPlaces {
                        SectionLabel(n: "5", label: "同行者・行先・外泊地点")
                        Card(padding: 14) {
                            VStack(alignment: .leading, spacing: 12) {
                                Field(label: "同行者") {
                                    TField(text: $companion, placeholder: "同行者がいる場合は入力")
                                }
                                // 帰国 时隐藏「行先（都市名）」—— 只填下面的「宿泊先」住所（itsuki 2026-06-03）
                                if !isReturnCountry {
                                    Field(label: "行先（都市名）") {
                                        TField(text: $destCities, placeholder: "例：東京 / 大阪 / ソウル")
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
                                            Text("地点を追加")
                                                .font(.system(size: 13, weight: .semibold))
                                        }
                                        .foregroundStyle(T.primary)
                                    }
                                    .buttonStyle(.plain)
                                    Text("※ 複数の地点に滞在する場合はすべて入力してください")
                                        .font(.system(size: 10.5))
                                        .foregroundStyle(T.inkMute)
                                }
                            }
                        }
                        .padding(.bottom, 18)
                    }

                    // ── §6 食事不要期間（外泊 / 帰国 のみ）─────────────────
                    if needSkipMeal {
                        SectionLabel(n: "6", label: "寮食堂 食事申告")
                        Card(padding: 14) {
                            VStack(alignment: .leading, spacing: 14) {
                                if meIsOverseas {
                                    Toggle(isOn: $skipEnabled) {
                                        Text("食事不要期間を申告する")
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
                                                DateField(date: $skipStartDate, minDate: leaveDate)
                                                ChipGroup(options: MEALS, value: $skipStartMeal)
                                            }
                                        }
                                        VStack(alignment: .leading, spacing: 6) {
                                            Text("不要 終了")
                                                .font(.system(size: 11.5, weight: .semibold))
                                                .foregroundStyle(T.inkSub)
                                            HStack(spacing: 8) {
                                                DateField(date: $skipEndDate, minDate: skipStartDate)
                                                ChipGroup(options: MEALS, value: $skipEndMeal)
                                            }
                                        }
                                        Text("※ 上記期間（開始の食事から終了の食事まで）の寮食堂を不要とします")
                                            .font(.system(size: 10.5))
                                            .foregroundStyle(T.inkMute)
                                    }

                                    Field(label: "食事備考") {
                                        TArea(text: $mealNote,
                                              placeholder: "例：8月10日朝食まで必要、8月20日夕食から必要",
                                              rows: 3)
                                    }
                                } else {
                                    Text("食事は食事入力表でご記入ください")
                                        .font(.system(size: 13, weight: .semibold))
                                        .foregroundStyle(T.ink)
                                    Text("※ 日本人生徒の食事変更は学校指定の食事入力表で扱います。")
                                        .font(.system(size: 10.5))
                                        .foregroundStyle(T.inkMute)
                                }
                            }
                        }
                        .padding(.bottom, 18)
                    }

                    // ── §7 飛行機（帰国 のみ）─────────────────────────────
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
                                    TimeField(date: $departFlightTime)
                                }
                                Field(label: "到着空港", required: true) {
                                    TField(text: $arriveAirport, placeholder: "到着空港名")
                                }
                                VStack(alignment: .leading, spacing: 6) {
                                    Text("到着時刻")
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundStyle(T.inkSub)
                                    TimeField(date: $arriveFlightTime)
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
                    HStack(spacing: 10) {
                        Button {
                            app.showToast("下書き保存しました")
                        } label: {
                            Text("下書き保存")
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

                        Button {
                            submit()
                        } label: {
                            Text("提出する")
                                .font(.system(size: 14, weight: .bold))
                                .foregroundStyle(.white)
                                .frame(maxWidth: .infinity, minHeight: 52)
                                .background {
                                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                                        .fill(canSubmit ? T.primary : T.inkFaint)
                                }
                        }
                        .buttonStyle(.plain)
                        .disabled(!canSubmit)
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
        // 共通字段（backend time 要 "HH:mm:ss" 格式、append :00）
        let backendKind = ApplyKindMapper.encode(kind)
        let leaveDateStr = StayForm.formatYMD(leaveDate)
        let leaveTimeStr = StayForm.formatHM(leaveTime) + ":00"
        let returnDateStr = StayForm.formatYMD(returnDate)
        let returnTimeStr = StayForm.formatHM(returnTime) + ":00"
        let contactPhoneValue = StayForm.nilIfBlank(contactPhone)
        let mealNoteValue = meIsOverseas ? StayForm.nilIfBlank(mealNote) : nil
        let companionValue = StayForm.nilIfBlank(companion)
        let destCitiesValue = StayForm.nilIfBlank(destCities)
        // 出租车预约：出寮方法选了「タクシー」→ "HH:MM:SS"；选别的 → nil（不预约）
        let taxiTimeValue: String? = leaveMethod == StayForm.TAXI_METHOD ? StayForm.formatHM(taxiTime) + ":00" : nil

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
                app.showToast("食事不要期間が空です。開始・終了の食事の順序をご確認ください")
                return
            }
        } else {
            mealsSkip = []
        }

        do {
            // 按 kind dispatch 到 3 个 typed Encodable body
            switch backendKind {
            case "帰省":
                let body = KisheiCreateBody(
                    reason: reason,
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
                    reason: reason,
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
                    reason: reason,
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
                    flight_dep_air: departAirport,
                    // IX-005: TimeField 只有时刻，底层日期停在 2000-01-01。
                    // 出发跟出寮日合成、到着跟帰寮日合成，凑成完整 datetime，
                    // 用带 +09:00 的 ISO 字符串发出去（bare ISO8601 会变成 UTC 的 Z，跟 backend 期望不符）。
                    flight_dep_at: StayForm.formatISOWithTokyo(date: leaveDate, time: departFlightTime),
                    flight_arr_air: arriveAirport,
                    flight_arr_at: StayForm.formatISOWithTokyo(date: returnDate, time: arriveFlightTime),
                    taxi_reservation_time: taxiTimeValue
                )
                _ = try await ApplicationsAPI.create(body)
            default:
                app.showToast("未対応の届です")
                return
            }
            // 提交成功
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
            app.showToast(error.localizedDescription)
        }
    }

    // MARK: - meals_skip 展開ヘルパー

    ///
    /// (skipStartDate, skipStartMeal) → (skipEndDate, skipEndMeal) の間の全食事エントリを生成
    static func expandMealsSkip(
        from startDate: Date, startMeal: String,
        to endDate: Date, endMeal: String
    ) -> [[String: String]] {
        let mealOrder = ["朝食", "昼食", "夕食"]
        var result: [[String: String]] = []
        let cal = Calendar.current
        var current = startDate
        while current <= endDate {
            let isFirst = cal.isDate(current, inSameDayAs: startDate)
            let isLast = cal.isDate(current, inSameDayAs: endDate)
            let lo = isFirst ? (mealOrder.firstIndex(of: startMeal) ?? 0) : 0
            let hi = isLast ? (mealOrder.firstIndex(of: endMeal) ?? 2) : 2
            if lo <= hi {
                let dateStr = formatYMD(current)
                for i in lo ... hi {
                    result.append(["date": dateStr, "meal": mealOrder[i]])
                }
            }
            guard let next = cal.date(byAdding: .day, value: 1, to: current) else { break }
            current = next
        }
        return result
    }

    // MARK: - helpers (parse / format date · 静的)

    /// 明日 0:00 — DatePicker minDate に使う (#3)
    static var tomorrow: Date {
        let cal = Calendar.current
        let today0 = cal.startOfDay(for: Date())
        return cal.date(byAdding: .day, value: 1, to: today0) ?? today0
    }

    static func parseYMD(_ s: String) -> Date? {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = TimeZone(identifier: "Asia/Tokyo") // IX-034 修复④：固定 JST，跟 formatYMD 配对、保证日期串往返恒等
        return f.date(from: s)
    }

    static func parseHM(_ s: String) -> Date? {
        let f = DateFormatter()
        f.dateFormat = "HH:mm"
        f.locale = Locale(identifier: "en_US_POSIX")
        return f.date(from: s)
    }

    static func formatYMD(_ d: Date) -> String {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = TimeZone(identifier: "Asia/Tokyo") // IX-034 修复④：固定 JST，否则非 JST 设备 target_date / 出寮日口径偏一天
        return f.string(from: d)
    }

    static func formatHM(_ d: Date) -> String {
        let f = DateFormatter()
        f.dateFormat = "HH:mm"
        f.locale = Locale(identifier: "en_US_POSIX")
        return f.string(from: d)
    }

    /// 把一个日期的年月日 + 一个时刻的时分合成成一个 Date。
    /// TimeField 只带时刻、底层日期是 2000-01-01，所以要跟对应的日期组合起来用。
    static func combine(date: Date, time: Date) -> Date {
        let cal = Calendar.current
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

    /// 把日期 + 时刻合成后输出带 +09:00 的 ISO 8601 字符串。
    /// backend 的 flight_dep_at / flight_arr_at 期望 "2026-05-03T18:00:00+09:00" 这种格式。
    /// bare ISO8601DateFormatter 会输出 UTC（末尾带 Z），所以这里显式指定日本时间偏移。
    static func formatISOWithTokyo(date: Date, time: Date) -> String {
        let combined = combine(date: date, time: time)
        let f = ISO8601DateFormatter()
        f.timeZone = TimeZone(identifier: "Asia/Tokyo")
        f.formatOptions = [.withInternetDateTime] // 保留 +09:00 偏移
        return f.string(from: combined)
    }

    /// 空白だけの入力は backend へ送らない
    static func nilIfBlank(_ s: String) -> String? {
        let trimmed = s.trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmed.isEmpty ? nil : trimmed
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
    var minDate: Date? = nil // 老師反饋 #3: 出寮日 = 明日以降 → minDate = StayForm.tomorrow
    var body: some View {
        Group {
            if let min = minDate {
                DatePicker("", selection: $date, in: min..., displayedComponents: .date)
            } else {
                DatePicker("", selection: $date, displayedComponents: .date)
            }
        }
        .labelsHidden()
        .datePickerStyle(.compact)
        .environment(\.locale, Locale(identifier: "ja_JP")) // itsuki 反馈: 月份要日语/数字 (西暦 2026年4月)
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

private struct TimeField: View {
    @Binding var date: Date
    var body: some View {
        DatePicker("", selection: $date, displayedComponents: .hourAndMinute)
            .labelsHidden()
            .datePickerStyle(.compact)
            .environment(\.locale, Locale(identifier: "ja_JP")) // itsuki 反馈: 月份/时刻要日语
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

private struct MealCheckbox: View {
    let isOn: Bool
    let toggle: () -> Void
    var body: some View {
        Button(action: toggle) {
            ZStack {
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .stroke(isOn ? T.primary : T.hair, lineWidth: 1.5)
                    .background {
                        RoundedRectangle(cornerRadius: 8, style: .continuous)
                            .fill(isOn ? T.primary : T.paper)
                    }
                    .frame(width: 28, height: 28)
                if isOn {
                    Text("✕")
                        .font(.system(size: 14, weight: .bold))
                        .foregroundStyle(.white)
                }
            }
        }
        .buttonStyle(.plain)
    }
}

// ============================================================================
// §2.5 GenericApplyForm — 共通フォーム (outing / return / repair / parcel / guest / other)
// ============================================================================

// ============================================================================
// §2.5 StudyAbsenceForm — 学習欠席届（晚自习请假）· system_features §7.3.5
// 4-30 後續 itsuki 拍板 — 字段：理由 textarea + 范围 select（前半/后半/両方）
// ============================================================================

struct StudyAbsenceForm: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var reason: String = ""
    @State private var range: StudyLeaveRange = .first
    /// 欠席する日付。デフォルト = 今日。今後 14 日まで選択可。
    @State private var targetDate: Date = .init()

    /// 選択可能な日付範囲: 今日〜14 日後
    private var dateRange: ClosedRange<Date> {
        let now = Date()
        let later = now.addingTimeInterval(60 * 60 * 24 * 14)
        return now ... later
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "学習欠席届", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    // §1 欠席する日付 (DatePicker)
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
                        Task {
                            do {
                                try await app.submitStudyLeave(
                                    targetDate: StayForm.formatYMD(targetDate),
                                    reason: reason,
                                    range: range
                                )
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
                                app.showToast(error.localizedDescription)
                            }
                        }
                    } label: {
                        Text("提出する")
                            .font(.system(size: 15, weight: .semibold))
                            .foregroundStyle(.white)
                            .frame(maxWidth: .infinity, minHeight: 48)
                            .background(Capsule().fill(T.primary))
                    }
                    .buttonStyle(.plain)
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

struct GenericApplyForm: View {
    let kind: String
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var dest: String = ""
    @State private var reason: String = ""
    @State private var date: Date = StayForm.parseYMD("2026-04-25") ?? Date()
    @State private var endDate: Date = StayForm.parseYMD("2026-04-26") ?? Date()
    @State private var time: Date = StayForm.parseHM("18:00") ?? Date()
    @State private var contact: String = ""
    @State private var didPrefillContact: Bool = false
    // 出租车预约「タクシー予約」（itsuki 2026-06-03）— 外出也能预约；外出表单是纯演示桩未接后端，仅 UI 展示
    @State private var taxiReserved: Bool = false
    @State private var taxiTime: Date = StayForm.parseHM("18:00") ?? Date()
    @State private var emergency: String = ""
    @State private var transport: String = "電車"
    @State private var repairPlace: String = "自室"
    @State private var guardian: Bool = false

    // ── 外出（outing）専用 — 接 outings 后端（A1）。后端 OutingCreateIn.outing_date 必填，旧表单缺这些字段 ──
    @State private var outingDate: Date = .init() // 外出日（今日以降）；后端拒过去日期
    @State private var outingLeaveTime: Date = StayForm.parseHM("13:00") ?? Date()
    @State private var outingReturnTime: Date = StayForm.parseHM("17:00") ?? Date()
    @State private var isSubmittingOuting: Bool = false

    private var type: ApplyTypeMeta {
        applyType(kind)
    }

    private var needsDest: Bool {
        ["outing", "stay", "holiday"].contains(kind)
    }

    private var needsEnd: Bool {
        ["stay", "holiday"].contains(kind)
    }

    private var needsGuardian: Bool {
        ["stay", "holiday"].contains(kind)
    }

    private var needsTransport: Bool {
        ["outing", "stay", "holiday"].contains(kind)
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

    private var isReturn: Bool {
        kind == "return"
    }

    private var isOuting: Bool {
        kind == "outing"
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
        guard !reason.isEmpty else { return false }
        if needsDest && dest.trimmingCharacters(in: .whitespaces).isEmpty { return false } // 外出: 去的地方「行き先」必填（trim 防只填空格）
        // 来訪者(guest)「来訪者氏名」/ 代理受取(parcel)「荷物の概要」也走 dest 字段、标了必填 → 同样 trim 后必须非空（codex 复审 minor-1）
        if (isGuest || isParcel) && dest.trimmingCharacters(in: .whitespaces).isEmpty { return false }
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

                    if needsDest {
                        Field(label: "行き先", required: true) {
                            TField(text: $dest, placeholder: "行き先を入力")
                        }.padding(.bottom, 14)
                    }
                    if isOuting {
                        // 外出是当天回寮 — 外出日（必填）+ 外出/回寮时刻。后端 OutingCreateIn 要 outing_date
                        Field(label: "外出日", required: true) {
                            DateField(date: $outingDate)
                        }.padding(.bottom, 14)
                        Field(label: "外出時刻") {
                            TimeField(date: $outingLeaveTime)
                        }.padding(.bottom, 14)
                        Field(label: "帰寮予定時刻") {
                            TimeField(date: $outingReturnTime)
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

                    if !isRepair && !isParcel && !isOuting {
                        Field(label: isReturn ? "日付" : (needsEnd ? "開始日" : "日付"), required: true) {
                            DateField(date: $date)
                        }
                        .padding(.bottom, 14)
                    }
                    if needsEnd {
                        Field(label: "終了日", required: true) {
                            DateField(date: $endDate)
                        }
                        .padding(.bottom, 14)
                    }
                    if !needsEnd && !isRepair && !isParcel && !isOuting {
                        Field(label: "帰寮予定時刻", required: true) {
                            TimeField(date: $time)
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
                                    TimeField(date: $taxiTime)
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

                    if needsGuardian {
                        Field(label: "保証人連絡先") {
                            TField(text: $emergency, placeholder: "保護者電話番号", keyboard: .phonePad)
                        }.padding(.bottom, 14)

                        Button { guardian.toggle() } label: {
                            HStack(alignment: .top, spacing: 10) {
                                ZStack {
                                    RoundedRectangle(cornerRadius: 4, style: .continuous)
                                        .stroke(guardian ? T.warnDeep : T.inkFaint, lineWidth: 1.5)
                                        .frame(width: 18, height: 18)
                                    if guardian {
                                        RoundedRectangle(cornerRadius: 4, style: .continuous).fill(T.warnDeep)
                                            .frame(width: 18, height: 18)
                                        Image(systemName: "checkmark")
                                            .font(.system(size: 11, weight: .bold))
                                            .foregroundStyle(.white)
                                    }
                                }
                                .padding(.top, 3)
                                Text("外泊・帰省は保証人の同意が必要です。上記の保証人に連絡済み／同意を得ていることを確認します。")
                                    .font(.system(size: 12.5))
                                    .foregroundStyle(T.warnDeep)
                                    .multilineTextAlignment(.leading)
                                    .lineSpacing(2)
                                Spacer(minLength: 0)
                            }
                            .padding(.horizontal, 14).padding(.vertical, 12)
                            .background {
                                RoundedRectangle(cornerRadius: 12, style: .continuous).fill(T.warnBg)
                            }
                            .overlay {
                                RoundedRectangle(cornerRadius: 12, style: .continuous).stroke(T.warn.opacity(0.25), lineWidth: 1)
                            }
                        }
                        .buttonStyle(.plain)
                        .padding(.bottom, 16)
                    }

                    HStack(spacing: 10) {
                        Button {
                            app.showToast("下書き保存しました")
                        } label: {
                            Text("下書き保存")
                                .font(.system(size: 14, weight: .bold))
                                .foregroundStyle(T.inkSub)
                                .frame(maxWidth: .infinity, minHeight: 52)
                                .background {
                                    RoundedRectangle(cornerRadius: 16, style: .continuous).fill(T.paper)
                                }
                                .overlay {
                                    RoundedRectangle(cornerRadius: 16, style: .continuous).stroke(T.hair, lineWidth: 1.5)
                                }
                        }
                        .buttonStyle(.plain)

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

    /// A1：外出申请直接接 outings 后端提出（pending → 等老师确认）。
    /// 演示构建不连后端、直接跳完成页讲叙事。
    private func submitOuting() async {
        guard !isSubmittingOuting else { return }
        isSubmittingOuting = true
        defer { isSubmittingOuting = false }
        #if DEMO
            app.showToast("外出申請を提出しました")
            router.go(.applyDone(kind: "outing"))
        #else
            let trimmedDest = dest.trimmingCharacters(in: .whitespacesAndNewlines)
            let trimmedReason = reason.trimmingCharacters(in: .whitespacesAndNewlines)
            let body = OutingCreateBody(
                outing_date: StayForm.formatYMD(outingDate),
                destination: trimmedDest.isEmpty ? nil : trimmedDest,
                leave_time: StayForm.formatHM(outingLeaveTime),
                return_time: StayForm.formatHM(outingReturnTime),
                taxi_reservation_time: taxiReserved ? StayForm.formatHM(taxiTime) : nil,
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
                app.showToast(error.localizedDescription)
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
            targetDate = StayForm.formatYMD(date)
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
            app.showToast(error.localizedDescription)
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
            ("申請者", "12号 · Nishimura Aoi"),
        ]
        switch kind {
        case "outing": base += [("行き先", "新宿")]
        case "stay": base += [("行き先", "実家"), ("期間", "2026-04-25 〜 04-26"), ("保証人", "同意済")]
        case "holiday": base += [("行き先", "実家 福岡"), ("期間", "2026-04-28 〜 05-05"), ("保証人", "同意済")]
        case "repair": base += [("場所", "自室"), ("依頼日", "2026-04-22")]
        case "parcel": base += [("荷物", "小包 1 件"), ("配達予定", "2026-04-23")]
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

                Text("\(type.name)申請を受け付けました。\n審査完了時に通知でお知らせします。")
                    .font(.system(size: 14))
                    .foregroundStyle(T.inkSub)
                    .multilineTextAlignment(.center)
                    .lineSpacing(4)
                    .padding(.bottom, 28)

                // Info card
                // IX-006: 原来这里显示写死的假申请号「A-240422-07」。后端 ApplicationOut 只有
                // UUID、没有人类可读的申请号，所以去掉这行假数据，只留预想审查时间。
                VStack(spacing: 4) {
                    HStack {
                        Text("予想審査時間").font(.system(size: 12)).foregroundStyle(T.inkSub)
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

    /// 找不到返回 nil（旧代码 `?? SEED.applications[0]` 退回第一条 → SEED 为空数组时下标越界崩溃）。
    /// 改 optional，下面 steps / otherDetailBody 找不到时显示空状态。
    private var item: ApplicationItem? {
        SEED.applications.first(where: { $0.id == id })
    }

    fileprivate struct StepMeta {
        let k: String
        let label: String
        let done: Bool
        let active: Bool
        let time: String?
        let label2: String?
        var activeNote: String? = nil // 进行中那一步显示的副标题（如审查中说明 / 确认中说明）
    }

    fileprivate var steps: [StepMeta] {
        guard let a = item else { return [] }
        let submitTime = a.date + " 10:24"
        // 外出申請（outing）= 一名老师确认即可，没有「審査」步骤 — itsuki 2026-06-04 拍板。
        // 确认老师的名字本应从登录的老师账号自动记录（后端实装待做），
        // 演示版先用代表性的「松本 先生」展示。
        if a.type == "outing" {
            let confirmed = a.status == "approved"
            let confirmTime: String? = confirmed ? a.date + " 11:02" : nil
            return [
                .init(k: "submit", label: "提出", done: true, active: false, time: submitTime, label2: nil),
                .init(k: "confirm",
                      label: confirmed ? "確認" : "先生の確認待ち",
                      done: confirmed, active: !confirmed, time: confirmTime,
                      label2: confirmed ? "松本 先生" : nil,
                      activeNote: "担当の先生が確認します"),
            ]
        }
        let reviewDone = a.status == "approved" || a.status == "rejected"
        let reviewActive = a.status == "pending"
        let reviewTime: String? = reviewActive ? nil : a.date + " 11:02"
        let finalDone = a.status == "approved" || a.status == "rejected"
        let finalLabel2 = a.status == "rejected" ? "差戻" : "承認"
        return [
            .init(k: "submit", label: "提出", done: true, active: false, time: submitTime, label2: nil),
            .init(k: "review", label: "審査", done: reviewDone, active: reviewActive, time: reviewTime, label2: nil, activeNote: "担当者：松本 先生 · 審査中"),
            .init(k: "final", label: "完了", done: finalDone, active: false, time: nil, label2: finalLabel2),
        ]
    }

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
            // 生产（IX-007 Option A）：后端只支持出寮届系（帰省/外泊/帰国），全部走真后端 StayDetailView(id)。
            // 修繕/来訪/代理受取 后端零实装、生产不存在这类申请；显式直连真后端，
            // 不再依赖「item 落到 SEED.applications[0] 恰好是 stay 型」的巧合、也不会退回 SEED 显假人。
            StayDetailView(id: id)
        #endif
    }

    /// 出寮届以外（修繕 / 来訪 / 代理受取 等）的 demo 3 步 workflow
    @ViewBuilder
    private var otherDetailBody: some View {
        if let a = item {
            let t = applyType(a.type)
            let sp = statusPair(a.status)
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
                        if a.status == "rejected" {
                            VStack(alignment: .leading, spacing: 6) {
                                Text("⚠ 差戻理由")
                                    .font(.system(size: 12, weight: .bold))
                                    .foregroundStyle(T.danger)
                                Text("帰寮予定時刻が門限（22:00）を超えています。外泊申請として再提出してください。")
                                    .font(.system(size: 13))
                                    .foregroundStyle(T.ink)
                                    .lineSpacing(3)
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
                        if a.status == "pending" {
                            Button {
                                app.showToast("申請を取消しました")
                                Task {
                                    try? await Task.sleep(nanoseconds: 400_000_000)
                                    await MainActor.run { router.replace(.apply) }
                                }
                            } label: {
                                Text("申請を取消")
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
                        } else if a.status == "rejected" {
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
                            Circle().fill(s.done ? T.ok : (s.active ? T.warn : T.pill))
                                .frame(width: 24, height: 24)
                            if s.done {
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
// 外出是独立 outings 表（不是出寮届 applications）：不过夜 / 一名老师确认即可。
// 三态映射 2 步进度：pending=先生確認待ち / approved=確認済（显示确认老师名）/ withdrawn=取消。
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

            // 撤回（仅 pending）
            if o.status == "pending" {
                Button {
                    Task { await withdraw(o) }
                } label: {
                    Text(isWithdrawing ? "取消中…" : "申請を取消")
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

    /// datetime "2026-06-05T13:55:04[.xxx][+09:00]" → "2026-06-05 13:55"（兼容带/不带时区·小数秒）
    private func fmtDateTime(_ iso: String) -> String {
        let parts = iso.split(separator: "T", maxSplits: 1)
        guard parts.count == 2 else { return iso }
        let hmParts = parts[1].split(separator: ":")
        return hmParts.count >= 2 ? "\(parts[0]) \(hmParts[0]):\(hmParts[1])" : String(parts[0])
    }

    /// 三态 → 2 步进度（提出 → 確認）。confirmed 时第 2 步显示确认老师名。
    private func steps(_ o: OutingOut) -> [ApplyDetailView.StepMeta] {
        let confirmed = o.status == "approved"
        let withdrawn = o.status == "withdrawn"
        let submitTime = fmtDateTime(o.submitted_at)
        let confirmTime = o.confirmed_at.map { fmtDateTime($0) }
        return [
            .init(k: "submit", label: "提出", done: true, active: false, time: submitTime, label2: nil),
            .init(k: "confirm",
                  label: confirmed ? "確認" : (withdrawn ? "取消" : "先生の確認待ち"),
                  done: confirmed,
                  active: !confirmed && !withdrawn,
                  time: confirmTime,
                  label2: confirmed ? o.confirmed_by_name : nil,
                  activeNote: confirmed || withdrawn ? nil : "担当の先生が確認します"),
        ]
    }

    private func load() async {
        isLoading = true
        defer { isLoading = false }
        guard let uuid = UUID(uuidString: outingId) else {
            app.showToast("無効な申請 ID です")
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
            app.showToast("申請を取消しました")
        } catch let APIError.unprocessable(msg) {
            app.showToast(msg)
        } catch APIError.server(409, _) {
            app.showToast("確認待ちの申請のみ取消できます")
            await load()
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch APIError.network {
            app.showToast("通信エラーが発生しました。電波を確認してください")
        } catch {
            app.showToast(error.localizedDescription)
        }
    }
}

/// 外出三态 → 状态 Pill（外出语义：確認待ち / 確認済 / 取消済）
private func outingStatusPair(_ status: String) -> (label: String, tone: Pill.Tone) {
    switch status {
    case "approved": return ("確認済", .ok)
    case "withdrawn": return ("取消済", .neutral)
    default: return ("確認待ち", .warn)
    }
}
