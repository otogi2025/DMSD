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
    let icon: String         // SF Symbol name
    let desc: String
}

private let APPLY_TYPES: [ApplyTypeMeta] = [
    .init(k: "outing",        name: "外出",     icon: "calendar",                     desc: "当日帰寮の外出"),
    .init(k: "stay",          name: "外泊",     icon: "house",                        desc: "寮外での宿泊"),
    .init(k: "holiday",       name: "帰省",     icon: "house.lodge",                  desc: "実家帰省・長期休暇"),
    .init(k: "returncountry", name: "帰国",     icon: "airplane",                     desc: "一時帰国（航空機利用）"),
    .init(k: "return",        name: "早帰",     icon: "calendar.badge.clock",         desc: "門限前の早帰・遅帰"),
    .init(k: "repair",        name: "修繕",     icon: "wrench.and.screwdriver",       desc: "部屋・設備の修繕依頼"),
    .init(k: "parcel",        name: "代理受取", icon: "shippingbox",                  desc: "不在時の荷物代理受取"),
    .init(k: "guest",         name: "来訪者",   icon: "person.2",                     desc: "家族・友人の来訪"),
    .init(k: "other",         name: "その他",   icon: "ellipsis.bubble",              desc: "上記以外のご依頼"),
]

private func applyType(_ k: String) -> ApplyTypeMeta {
    APPLY_TYPES.first { $0.k == k } ?? APPLY_TYPES[0]
}

// MARK: - APPLY_STATUS 映射 (JSX line 14-21)

private func statusPair(_ status: String) -> (label: String, tone: Pill.Tone) {
    switch status {
    case "draft":     return ("下書き", .neutral)
    case "pending":   return ("審査中", .warn)
    case "approved":  return ("承認済", .ok)
    case "rejected":  return ("差戻", .danger)
    case "returned":  return ("要修正", .danger)
    case "cancelled": return ("取消済", .neutral)
    default:          return (status, .neutral)
    }
}

// ============================================================================
// §2.1 ApplyListView — L1 · 4-tab + SEED.applications + FAB
// ============================================================================

struct ApplyListView: View {
    @EnvironmentObject var router: RouterStore
    @State private var tab: String = "all"

    private let tabs: [(String, String)] = [
        ("all", "すべて"),
        ("pending", "審査中"),
        ("approved", "承認済"),
        ("draft", "下書き"),
    ]

    private var filtered: [ApplicationItem] {
        SEED.applications.filter { tab == "all" ? true : $0.status == tab }
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
                                ForEach(tabs, id: \.0) { (k, l) in
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

                        if filtered.isEmpty {
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
    }
}

private struct ApplicationRow: View {
    let item: ApplicationItem

    var body: some View {
        let t = applyType(item.type)
        let sp = statusPair(item.status)
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
                    Text("ID: \(item.id)")
                        .font(.system(size: 11, design: .monospaced))
                        .foregroundStyle(T.inkMute)
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

    // ── 申請者本人 · SEED.user 直接読取 (#1 学生只能提交自己的) ────────────────
    private var meAccount: String { SEED.user.account }     // 6 桁学号 = student_id
    private var meName: String { SEED.user.name }
    private var meClass: String { "\(SEED.user.grade)\(SEED.user.classSuffix)組" }
    private var meNo: String { "\(SEED.user.seatNo)番" }
    private var meDorm: String { "\(SEED.user.dorm) \(SEED.user.room)" }
    private var mePhone: String { SEED.user.phone }
    private var meCategory: String { SEED.user.category }   // 一般寮生 / 留学生

    // ── §7.2 共通字段 (帰省/外泊/帰国 三種類すべて) ─────────────────────────
    @State private var leaveDate: Date = StayForm.tomorrow
    @State private var leaveTime: Date = StayForm.parseHM("18:00") ?? Date()
    @State private var leaveMethod: String = "JR"
    @State private var returnDate: Date = StayForm.tomorrow
    @State private var returnTime: Date = StayForm.parseHM("20:00") ?? Date()
    @State private var returnMethod: String = "JR"

    // ── 外泊 / 帰国 only ─────────────────────────────────────────────────
    @State private var stayPlaces: [String] = [""]                          // 外泊地点(可多个)
    @State private var skipStartDate: Date = StayForm.tomorrow
    @State private var skipStartMeal: String = "夕食"                        // 朝食 / 昼食 / 夕食
    @State private var skipEndDate: Date = StayForm.tomorrow
    @State private var skipEndMeal: String = "朝食"
    @State private var skipEnabled: Bool = true                              // 食事不要期間 を申告するか

    // ── 帰国 only ────────────────────────────────────────────────────────
    @State private var departAirport: String = ""
    @State private var departFlightTime: Date = StayForm.parseHM("10:00") ?? Date()
    @State private var arriveAirport: String = ""
    @State private var arriveFlightTime: Date = StayForm.parseHM("14:00") ?? Date()

    // ── 共通: 理由 ────────────────────────────────────────────────────────
    @State private var reason: String = ""

    // 移動方法選択肢 — 帰省方法 / 帰寮方法
    private let TRANSPORTS = ["JR", "バス", "自家用車", "タクシー", "教員送迎", "飛行機", "その他"]
    private let MEALS = ["朝食", "昼食", "夕食"]

    // ── kind 判定 helper ─────────────────────────────────────────────────
    private var isHoliday: Bool { kind == "holiday" }
    private var isStay: Bool { kind == "stay" }
    private var isReturnCountry: Bool { kind == "returncountry" }
    private var needPlaces: Bool { isStay || isReturnCountry }              // §4 外泊地点
    private var needSkipMeal: Bool { isStay || isReturnCountry }            // §5 食事不要期間
    private var needFlight: Bool { isReturnCountry }                        // §6 飛行機
    private var type: ApplyTypeMeta { applyType(kind) }

    // 提出可否: 必須項目が埋まっているか
    private var canSubmit: Bool {
        if reason.isEmpty { return false }
        if returnDate < leaveDate { return false }                          // 帰寮日は出寮日以降
        if needPlaces {
            if stayPlaces.allSatisfy({ $0.trimmingCharacters(in: .whitespaces).isEmpty }) {
                return false
            }
        }
        if needFlight {
            if departAirport.isEmpty || arriveAirport.isEmpty { return false }
        }
        return true
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

                    // ── §2 出寮 ────────────────────────────────────────────
                    SectionLabel(n: "2", label: "出寮（寮を出る）")
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
                                ChipGroup(options: TRANSPORTS, value: $leaveMethod)
                            }
                        }
                    }
                    .padding(.bottom, 18)

                    // ── §3 帰寮 ────────────────────────────────────────────
                    SectionLabel(n: "3", label: "帰寮（寮に戻る）")
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
                                ChipGroup(options: TRANSPORTS, value: $returnMethod)
                            }
                        }
                    }
                    .padding(.bottom, 18)

                    // ── §4 外泊地点（外泊 / 帰国 のみ · 動的表示 #4）──────────
                    if needPlaces {
                        SectionLabel(n: "4", label: "外泊地点")
                        Card(padding: 14) {
                            VStack(alignment: .leading, spacing: 10) {
                                ForEach(stayPlaces.indices, id: \.self) { i in
                                    HStack(spacing: 8) {
                                        TField(text: Binding(
                                            get: { i < stayPlaces.count ? stayPlaces[i] : "" },
                                            set: { newVal in
                                                if i < stayPlaces.count { stayPlaces[i] = newVal }
                                            }
                                        ), placeholder: "例：祖父母宅（岡山市北区表町 1-1-3）")
                                        if stayPlaces.count > 1 {
                                            Button {
                                                if i < stayPlaces.count { stayPlaces.remove(at: i) }
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
                                    stayPlaces.append("")
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
                        .padding(.bottom, 18)
                    }

                    // ── §5 食事不要期間（外泊 / 帰国 のみ）─────────────────
                    if needSkipMeal {
                        SectionLabel(n: "5", label: "寮食堂 食事不要期間")
                        Card(padding: 14) {
                            VStack(alignment: .leading, spacing: 14) {
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
                            }
                        }
                        .padding(.bottom, 18)
                    }

                    // ── §6 飛行機（帰国 のみ）─────────────────────────────
                    if needFlight {
                        SectionLabel(n: "6", label: "飛行機")
                        Card(padding: 14) {
                            VStack(alignment: .leading, spacing: 12) {
                                Field(label: "出発空港", required: true) {
                                    TField(text: $departAirport, placeholder: "例：岡山空港（OKJ）")
                                }
                                VStack(alignment: .leading, spacing: 6) {
                                    Text("出発時刻")
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundStyle(T.inkSub)
                                    TimeField(date: $departFlightTime)
                                }
                                Field(label: "到着空港", required: true) {
                                    TField(text: $arriveAirport, placeholder: "例：上海浦東国際空港（PVG）")
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

                    // ── §7 理由 (全種類共通) ─────────────────────────────────
                    let reasonSectionN = needFlight ? "7" : (needSkipMeal ? "6" : "4")
                    SectionLabel(n: reasonSectionN,
                                 label: isHoliday ? "帰省の理由" : (isReturnCountry ? "帰国の理由" : "外泊の理由"))
                    TArea(text: $reason,
                          placeholder: isHoliday ? "例：祖父の米寿祝いのため親族で集まるため。"
                                                 : (isReturnCountry ? "例：家族の都合により一時帰国。"
                                                                    : "例：友人の結婚式に出席するため。"),
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

    // MARK: - submit (mock POST /applications)

    private func submit() {
        // ── (#1) 学生は自分のみ提出可: payload の student_id = ログイン中アカウント ──
        // 真実装ではバックエンドが JWT 等で再校验。フロント側もここで明示する。
        let studentId = SEED.user.account
        precondition(studentId == meAccount,
                     "student_id mismatch — 提出者は SEED.user 本人でなければなりません")

        var payload: [String: Any] = [
            "student_id": studentId,
            "kind": kind,                                       // holiday / stay / returncountry
            "leave_date": StayForm.formatYMD(leaveDate),
            "leave_time": StayForm.formatHM(leaveTime),
            "leave_method": leaveMethod,
            "return_date": StayForm.formatYMD(returnDate),
            "return_time": StayForm.formatHM(returnTime),
            "return_method": returnMethod,
            "reason": reason,
        ]
        if needPlaces {
            payload["stay_places"] = stayPlaces.filter {
                !$0.trimmingCharacters(in: .whitespaces).isEmpty
            }
        }
        if needSkipMeal && skipEnabled {
            payload["skip_meal_from"] = [
                "date": StayForm.formatYMD(skipStartDate),
                "meal": skipStartMeal,
            ]
            payload["skip_meal_to"] = [
                "date": StayForm.formatYMD(skipEndDate),
                "meal": skipEndMeal,
            ]
        }
        if needFlight {
            payload["depart_airport"] = departAirport
            payload["depart_flight_time"] = StayForm.formatHM(departFlightTime)
            payload["arrive_airport"] = arriveAirport
            payload["arrive_flight_time"] = StayForm.formatHM(arriveFlightTime)
        }

        // mock POST /applications
        print("[mock POST /applications] payload=\(payload)")

        app.showToast("\(type.name)申請を提出しました")
        router.go(.applyDone(kind: kind))
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
        return f.string(from: d)
    }
    static func formatHM(_ d: Date) -> String {
        let f = DateFormatter()
        f.dateFormat = "HH:mm"
        f.locale = Locale(identifier: "en_US_POSIX")
        return f.string(from: d)
    }
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

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout Void) -> CGSize {
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

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout Void) {
        let maxWidth = bounds.width
        var x: CGFloat = bounds.minX
        var y: CGFloat = bounds.minY
        var rowHeight: CGFloat = 0
        for sub in subviews {
            let size = sub.sizeThatFits(.unspecified)
            if x - bounds.minX + size.width > maxWidth && x > bounds.minX {
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
    var minDate: Date? = nil          // 老師反饋 #3: 出寮日 = 明日以降 → minDate = StayForm.tomorrow
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

struct GenericApplyForm: View {
    let kind: String
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var dest: String = ""
    @State private var reason: String = ""
    @State private var date: Date = StayForm.parseYMD("2026-04-25") ?? Date()
    @State private var endDate: Date = StayForm.parseYMD("2026-04-26") ?? Date()
    @State private var time: Date = StayForm.parseHM("18:00") ?? Date()
    @State private var contact: String = "090-1234-5678"
    @State private var emergency: String = ""
    @State private var transport: String = "電車"
    @State private var repairPlace: String = "自室"
    @State private var guardian: Bool = false

    private var type: ApplyTypeMeta { applyType(kind) }
    private var needsDest: Bool { ["outing", "stay", "holiday"].contains(kind) }
    private var needsEnd: Bool { ["stay", "holiday"].contains(kind) }
    private var needsGuardian: Bool { ["stay", "holiday"].contains(kind) }
    private var needsTransport: Bool { ["outing", "stay", "holiday"].contains(kind) }
    private var isRepair: Bool { kind == "repair" }
    private var isParcel: Bool { kind == "parcel" }
    private var isGuest: Bool { kind == "guest" }
    private var isReturn: Bool { kind == "return" }

    private var canSubmit: Bool {
        !reason.isEmpty && (isRepair || isParcel || true)
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
                            TField(text: $dest, placeholder: "例：新宿・実家など")
                        }.padding(.bottom, 14)
                    }
                    if isGuest {
                        Field(label: "来訪者氏名", required: true) {
                            TField(text: $dest, placeholder: "例：山田 花子")
                        }.padding(.bottom, 14)
                    }
                    if isParcel {
                        Field(label: "荷物の概要", required: true) {
                            TField(text: $dest, placeholder: "配送業者・個数")
                        }.padding(.bottom, 14)
                    }

                    if !isRepair && !isParcel {
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
                    if !needsEnd && !isRepair && !isParcel {
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

                    if isRepair {
                        Field(label: "場所", required: true) {
                            VStack(spacing: 8) {
                                RadioCard(selection: $repairPlace, value: "自室",         title: "自室")
                                RadioCard(selection: $repairPlace, value: "共用スペース", title: "共用スペース")
                                RadioCard(selection: $repairPlace, value: "水回り",       title: "水回り")
                                RadioCard(selection: $repairPlace, value: "その他",       title: "その他")
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
                            router.go(.applyPreview(kind: kind))
                        } label: {
                            Text("次へ · 確認")
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
                }
                .padding(.horizontal, 20)
                .padding(.top, 4).padding(.bottom, 24)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl)
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

    private var type: ApplyTypeMeta { applyType(kind) }

    private var rows: [(String, String)] {
        var base: [(String, String)] = [
            ("種別", type.name),
            ("申請番号", "A-TEMP"),
            ("申請者", "12号 · Nishimura Aoi"),
        ]
        switch kind {
        case "outing":  base += [("行き先", "新宿"), ("日付", "2026-04-25"), ("帰寮予定", "18:00")]
        case "stay":    base += [("行き先", "実家"), ("期間", "2026-04-25 〜 04-26"), ("保証人", "同意済")]
        case "holiday": base += [("行き先", "実家 福岡"), ("期間", "2026-04-28 〜 05-05"), ("保証人", "同意済")]
        case "repair":  base += [("場所", "自室"), ("依頼日", "2026-04-22")]
        case "parcel":  base += [("荷物", "Amazon 小包 1 件"), ("配達予定", "2026-04-23")]
        case "guest":   base += [("来訪者", "山田 花子"), ("来訪日", "2026-04-25")]
        case "return":  base += [("日付", "2026-04-25"), ("帰寮時刻", "17:30")]
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
                            ForEach(Array(rows.enumerated()), id: \.offset) { (i, pair) in
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

    private var type: ApplyTypeMeta { applyType(kind) }

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
                VStack(spacing: 4) {
                    HStack {
                        Text("申請 ID").font(.system(size: 12)).foregroundStyle(T.inkSub)
                        Spacer()
                        Text("A-240422-07")
                            .font(.system(size: 12, weight: .bold, design: .monospaced))
                            .foregroundStyle(T.ink)
                    }
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

                HStack(spacing: 10) {
                    Button {
                        router.go(.applyDetail(id: "A-240422-07"))
                    } label: {
                        Text("詳細を見る")
                            .font(.system(size: 14, weight: .bold))
                            .foregroundStyle(T.ink)
                            .frame(maxWidth: .infinity, minHeight: 52)
                            .background {
                                RoundedRectangle(cornerRadius: 16, style: .continuous).fill(T.paper)
                            }
                            .overlay {
                                RoundedRectangle(cornerRadius: 16, style: .continuous).stroke(T.hair, lineWidth: 1.5)
                            }
                    }
                    .buttonStyle(.plain)

                    PrimaryButton(title: "一覧へ") {
                        router.replace(.apply)
                    }
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

    private var item: ApplicationItem {
        SEED.applications.first(where: { $0.id == id }) ?? SEED.applications[0]
    }

    fileprivate struct StepMeta {
        let k: String
        let label: String
        let done: Bool
        let active: Bool
        let time: String?
        let label2: String?
    }

    fileprivate var steps: [StepMeta] {
        let a = item
        let submitTime = a.date + " 10:24"
        let reviewDone = a.status == "approved" || a.status == "rejected"
        let reviewActive = a.status == "pending"
        let reviewTime: String? = reviewActive ? nil : a.date + " 11:02"
        let finalDone = a.status == "approved" || a.status == "rejected"
        let finalLabel2 = a.status == "rejected" ? "差戻" : "承認"
        return [
            .init(k: "submit", label: "提出", done: true, active: false, time: submitTime, label2: nil),
            .init(k: "review", label: "審査", done: reviewDone, active: reviewActive, time: reviewTime, label2: nil),
            .init(k: "final",  label: "完了", done: finalDone, active: false, time: nil, label2: finalLabel2),
        ]
    }

    var body: some View {
        let a = item
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
                                    Text(a.id)
                                        .font(.system(size: 11, design: .monospaced))
                                        .foregroundStyle(T.inkMute)
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
    }
}

private struct WorkflowStepsView: View {
    let steps: [ApplyDetailView.StepMeta]

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            ForEach(Array(steps.enumerated()), id: \.offset) { (i, s) in
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
                        if s.active {
                            Text("担当者：松本 先生 · 審査中")
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
