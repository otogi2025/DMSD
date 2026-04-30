// StayListStubs.swift · 申請履歴 一覧 + 承認 chain 詳細
// ⭐ 会话 C · 老師 38 条 #5「提交后给提交者展示承认状态」
//
// API 対応（B 未到位 → mock）:
//   GET /applications/mine    → StayListView         (BACKEND_DESIGN_LOG §5.2.2)
//   GET /applications/:id     → StayDetailView       (BACKEND_DESIGN_LOG §5.2.3)
//
// chain 規則（IOS_DESIGN_LOG §11.9 I11）:
//   外泊届 一般 = 担任 / 寮務課長 / 管理係                         (3 役职)
//   外泊届 留学生 = 担任 / 国際交流部長 / 寮務課長 / 寮務部長 / 管理係  (5 役职)
//   帰省 / 帰国届 chain = ⏳ 实物表 evidence 待ち

import SwiftUI

// MARK: - 役职 / 決定 / chain entry モデル

enum ApprovalRole: String, CaseIterable, Hashable {
    case homeroom       = "担任"
    case dormHead       = "寮務部長"
    case dormChief      = "寮務課長"
    case intlHead       = "国際交流部長"
    case intlChief      = "国際交流課長"
    case management     = "管理係"

    var label: String { rawValue }
}

enum ApprovalDecision: String, Hashable {
    case pending, approved, rejected

    var label: String {
        switch self {
        case .pending:  return "審査中"
        case .approved: return "承認"
        case .rejected: return "差戻"
        }
    }

    var tone: Pill.Tone {
        switch self {
        case .pending:  return .warn
        case .approved: return .ok
        case .rejected: return .danger
        }
    }
}

struct ApprovalStep: Hashable, Identifiable {
    let role: ApprovalRole
    let approverName: String?       // nil = 老师未指定 / 役职名のみ表示
    let decision: ApprovalDecision
    let decidedAt: String?          // "2026-04-21 11:02"
    let comment: String?

    var id: String { role.rawValue }
}

/// アプリ内で扱う出寮届の詳細（GET /applications/:id 返り値の iOS 模型）
struct StayApplication: Hashable, Identifiable {
    let id: String                  // "a1" 等
    let kind: ApplicationKind       // 外泊 / 帰省 / 帰国 / その他
    let status: ApplicationStatus   // pending / approved / rejected / returned / cancelled / draft
    let leaveDate: String           // "2026-05-03"
    let returnDate: String?
    let summary: String             // ApplicationItem.summary 互換
    let destination: String?
    let leaveMethod: String?
    let returnMethod: String?
    let chain: [ApprovalStep]
    let submittedAt: String         // "2026-04-20 10:24"
}

enum ApplicationKind: String, Hashable {
    case stay     = "外泊"
    case holiday  = "帰省"
    case `return` = "帰国"
    case other    = "その他"

    /// SEED.applications.type ("stay" / "holiday" / "return" / ...) からマップ
    static func fromSeedType(_ t: String) -> ApplicationKind {
        switch t {
        case "stay":    return .stay
        case "holiday": return .holiday
        case "return":  return .return
        default:        return .other
        }
    }
}

enum ApplicationStatus: String, Hashable {
    case draft, pending, approved, rejected, returned, cancelled

    var label: String {
        switch self {
        case .draft:     return "下書き"
        case .pending:   return "審査中"
        case .approved:  return "承認済"
        case .rejected:  return "差戻"
        case .returned:  return "要修正"
        case .cancelled: return "取消済"
        }
    }

    var tone: Pill.Tone {
        switch self {
        case .draft:     return .neutral
        case .pending:   return .warn
        case .approved:  return .ok
        case .rejected:  return .danger
        case .returned:  return .danger
        case .cancelled: return .neutral
        }
    }

    static func fromSeed(_ s: String) -> ApplicationStatus {
        ApplicationStatus(rawValue: s) ?? .pending
    }
}

// MARK: - chain ジェネレータ（モック / I11 規則対応）

enum ApprovalChainBuilder {
    /// 外泊届 chain を生成（IOS_DESIGN_LOG §11.9 I11 の規則）
    /// - Parameter isOverseas: 学生が留学生か（system_features §7.2.2 / Q11）
    static func stayChain(isOverseas: Bool) -> [ApprovalRole] {
        if isOverseas {
            // 留学生 = 担任 / 国際交流部長 / 寮務課長 / 寮務部長 / 管理係（5 役职）
            return [.homeroom, .intlHead, .dormChief, .dormHead, .management]
        } else {
            // 一般 = 担任 / 寮務課長 / 管理係（3 役职）
            return [.homeroom, .dormChief, .management]
        }
    }

    /// 帰省 / 帰国届 chain — evidence 待ち（暫定: 外泊と同一 / 老師 LINE「外泊と同じ」）
    static func holidayChain(isOverseas: Bool) -> [ApprovalRole] {
        // ⏳ 实物表到着後に確定。暫定で外泊と同一 chain を使用。
        return stayChain(isOverseas: isOverseas)
    }

    static func chain(for kind: ApplicationKind, isOverseas: Bool) -> [ApprovalRole] {
        switch kind {
        case .stay:     return stayChain(isOverseas: isOverseas)
        case .holiday:  return holidayChain(isOverseas: isOverseas)
        case .return:   return holidayChain(isOverseas: isOverseas)
        case .other:    return []
        }
    }
}

// MARK: - モックデータ（B 未到位 → SEED.applications を拡張）

enum StayListMock {
    /// 暫定の留学生フラグ（SEED.user に is_overseas が無いため、リュウ イヒ = 留学生 扱いとする）
    static let isOverseas: Bool = true

    /// SEED.applications を全件 StayApplication に拡張
    static var all: [StayApplication] {
        SEED.applications.compactMap { item in
            let kind = ApplicationKind.fromSeedType(item.type)
            let status = ApplicationStatus.fromSeed(item.status)
            let chainRoles = ApprovalChainBuilder.chain(for: kind, isOverseas: isOverseas)
            let steps = makeSteps(for: chainRoles, applicationStatus: status, baseDate: item.date)
            // outing / return / parcel / repair / guest / other は #5 の対象外（chain 無し）
            // → 見せても意味がないので、出寮届 系（stay / holiday / return）のみ表示
            guard kind != .other else { return nil }
            return StayApplication(
                id: item.id,
                kind: kind,
                status: status,
                leaveDate: item.date,
                returnDate: addDays(item.date, days: 2),
                summary: item.summary,
                destination: extractDestination(item.summary),
                leaveMethod: "JR + バス",
                returnMethod: "JR",
                chain: steps,
                submittedAt: "\(item.date) 10:24"
            )
        }
    }

    static func find(_ id: String) -> StayApplication? {
        all.first(where: { $0.id == id })
    }

    // chain の各 step に decision / decided_at を割り当てる（status から逆算）
    private static func makeSteps(
        for roles: [ApprovalRole],
        applicationStatus status: ApplicationStatus,
        baseDate: String
    ) -> [ApprovalStep] {
        guard !roles.isEmpty else { return [] }
        let names: [ApprovalRole: String] = [
            .homeroom:   "松本 先生",
            .dormHead:   "高野 先生",
            .dormChief:  "新股 先生",
            .intlHead:   "難波 先生",
            .intlChief:  "小林 先生",
            .management: "田中 先生",
        ]
        // status に応じて承認済の数を決める
        let approvedCount: Int = {
            switch status {
            case .approved:                  return roles.count
            case .rejected, .returned:       return max(roles.count - 1, 1)   // 最後の役职が差戻
            case .pending:                   return roles.count > 2 ? 1 : 0   // 進行中: 先頭だけ承認
            case .draft, .cancelled:         return 0
            }
        }()
        // 差戻の場合、最後の承認役职は rejected
        let rejectedIndex: Int? = (status == .rejected) ? approvedCount : nil

        return roles.enumerated().map { (idx, role) in
            let decision: ApprovalDecision
            let decidedAt: String?
            let comment: String?
            if let r = rejectedIndex, idx == r {
                decision = .rejected
                decidedAt = "\(baseDate) 14:32"
                comment = "外泊先の連絡先を追加で記入してください"
            } else if idx < approvedCount {
                decision = .approved
                decidedAt = "\(baseDate) \(11 + idx):0\(idx % 10)"
                comment = nil
            } else {
                decision = .pending
                decidedAt = nil
                comment = nil
            }
            return ApprovalStep(
                role: role,
                approverName: names[role],
                decision: decision,
                decidedAt: decidedAt,
                comment: comment
            )
        }
    }

    private static func extractDestination(_ summary: String) -> String? {
        // "東京 · 2 泊 3 日" → "東京"
        summary.split(separator: "·").first.map { $0.trimmingCharacters(in: .whitespaces) }
    }

    private static func addDays(_ d: String, days: Int) -> String? {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        f.locale = Locale(identifier: "ja_JP")
        guard let date = f.date(from: d),
              let added = Calendar.current.date(byAdding: .day, value: days, to: date)
        else { return nil }
        return f.string(from: added)
    }
}

// ============================================================================
// MARK: - StayListView · 申請履歴 一覧（マイページ → 申請履歴）
// ============================================================================

struct StayListView: View {
    @EnvironmentObject var router: RouterStore

    @State private var filter: ApplicationStatus? = nil   // nil = すべて
    private var items: [StayApplication] {
        let all = StayListMock.all.sorted { $0.leaveDate > $1.leaveDate }
        guard let f = filter else { return all }
        return all.filter { $0.status == f }
    }

    private let tabs: [(label: String, value: ApplicationStatus?)] = [
        ("すべて", nil),
        ("審査中", .pending),
        ("承認済", .approved),
        ("差戻", .rejected),
    ]

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "申請履歴", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    filterTabs
                        .padding(.bottom, 14)

                    if items.isEmpty {
                        EmptyState(
                            icon: "tray",
                            title: "申請はありません",
                            message: filter == nil ? "外泊・帰省・帰国届を提出すると、ここに表示されます。" : "条件に一致する申請はありません。"
                        )
                        .frame(maxWidth: .infinity)
                    } else {
                        VStack(spacing: 10) {
                            ForEach(items) { item in
                                Button {
                                    router.go(.stayDetail(id: item.id))
                                } label: {
                                    StayRow(item: item)
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 4)
                .padding(.bottom, 28)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }

    private var filterTabs: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 6) {
                ForEach(Array(tabs.enumerated()), id: \.offset) { (_, tab) in
                    let selected = filter == tab.value
                    Button { filter = tab.value } label: {
                        Text(tab.label)
                            .font(.system(size: 12.5, weight: .semibold))
                            .padding(.horizontal, 14).padding(.vertical, 7)
                            .foregroundStyle(selected ? Color.white : T.primary)
                            .background {
                                Capsule().fill(selected ? T.primary : T.pill)
                            }
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }
}

// MARK: 一覧 row

private struct StayRow: View {
    let item: StayApplication

    var body: some View {
        Card(padding: 14) {
            VStack(alignment: .leading, spacing: 10) {
                // 1 段目: kind icon + 種別 + 期間 + status pill
                HStack(spacing: 12) {
                    Image(systemName: kindIcon(item.kind))
                        .font(.system(size: 17))
                        .foregroundStyle(T.primary)
                        .frame(width: 40, height: 40)
                        .background {
                            RoundedRectangle(cornerRadius: 10, style: .continuous).fill(T.pill)
                        }
                    VStack(alignment: .leading, spacing: 3) {
                        HStack(spacing: 8) {
                            Text("\(item.kind.rawValue)届")
                                .font(.system(size: 14, weight: .bold))
                                .foregroundStyle(T.ink)
                            Pill(text: item.status.label, tone: item.status.tone)
                        }
                        Text(item.summary)
                            .font(.system(size: 12))
                            .foregroundStyle(T.inkSub)
                            .lineLimit(1)
                    }
                    Spacer(minLength: 0)
                    Ic.chevR(14).foregroundStyle(T.inkMute)
                }

                // 2 段目: 承認 chain サマリ（dot 列）
                if !item.chain.isEmpty {
                    chainDots
                }

                // 3 段目: 出寮日 + ID
                HStack {
                    HStack(spacing: 4) {
                        Ic.calendar(11).foregroundStyle(T.inkMute)
                        Text(item.leaveDate)
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundStyle(T.inkMute)
                    }
                    Spacer()
                    Text("ID: \(item.id)")
                        .font(.system(size: 11, design: .monospaced))
                        .foregroundStyle(T.inkMute)
                }
                .padding(.top, 4)
                .overlay(alignment: .top) {
                    Rectangle().fill(T.hair).frame(height: 0.5)
                }
            }
        }
    }

    private var chainDots: some View {
        HStack(spacing: 6) {
            ForEach(Array(item.chain.enumerated()), id: \.offset) { (i, step) in
                HStack(spacing: 4) {
                    chainDot(step.decision)
                    Text(step.role.label)
                        .font(.system(size: 10.5, weight: .semibold))
                        .foregroundStyle(roleFg(step.decision))
                }
                .padding(.horizontal, 7).padding(.vertical, 3)
                .background {
                    Capsule().fill(roleBg(step.decision))
                }
                if i < item.chain.count - 1 {
                    Rectangle().fill(T.hair).frame(width: 8, height: 0.5)
                }
            }
        }
    }

    @ViewBuilder
    private func chainDot(_ d: ApprovalDecision) -> some View {
        ZStack {
            Circle().fill(dotFill(d)).frame(width: 12, height: 12)
            switch d {
            case .approved:
                Image(systemName: "checkmark")
                    .font(.system(size: 7, weight: .heavy))
                    .foregroundStyle(.white)
            case .rejected:
                Image(systemName: "xmark")
                    .font(.system(size: 7, weight: .heavy))
                    .foregroundStyle(.white)
            case .pending:
                Circle().fill(.white).frame(width: 4, height: 4)
            }
        }
    }

    private func dotFill(_ d: ApprovalDecision) -> Color {
        switch d {
        case .approved: return T.ok
        case .rejected: return T.danger
        case .pending:  return T.inkFaint
        }
    }
    private func roleBg(_ d: ApprovalDecision) -> Color {
        switch d {
        case .approved: return T.okBg
        case .rejected: return T.dangerBg
        case .pending:  return T.hairSoft
        }
    }
    private func roleFg(_ d: ApprovalDecision) -> Color {
        switch d {
        case .approved: return T.okDeep
        case .rejected: return T.danger
        case .pending:  return T.inkSub
        }
    }

    private func kindIcon(_ k: ApplicationKind) -> String {
        switch k {
        case .stay:    return "house"
        case .holiday: return "house.lodge"
        case .return:  return "airplane"
        case .other:   return "doc.text"
        }
    }
}

// ============================================================================
// MARK: - StayDetailView · 申請詳細 + 承認 chain 縦 timeline
// ============================================================================

struct StayDetailView: View {
    let id: String
    @EnvironmentObject var router: RouterStore

    private var item: StayApplication {
        StayListMock.find(id) ?? StayListMock.all.first ?? StayApplication(
            id: id, kind: .stay, status: .pending,
            leaveDate: "—", returnDate: nil,
            summary: "—", destination: nil,
            leaveMethod: nil, returnMethod: nil,
            chain: [], submittedAt: "—"
        )
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "申請詳細", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    headerCard
                    fieldsCard
                    chainCard
                    if let last = item.chain.last(where: { $0.comment != nil }) {
                        commentCard(last)
                    }
                    Color.clear.frame(height: 12)
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
                .padding(.bottom, 28)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }

    private var headerCard: some View {
        Card(padding: 18) {
            VStack(alignment: .leading, spacing: 12) {
                HStack(spacing: 12) {
                    Image(systemName: kindIcon(item.kind))
                        .font(.system(size: 18))
                        .foregroundStyle(T.primary)
                        .frame(width: 44, height: 44)
                        .background {
                            RoundedRectangle(cornerRadius: 12, style: .continuous).fill(T.pill)
                        }
                    VStack(alignment: .leading, spacing: 2) {
                        Text("\(item.kind.rawValue)届")
                            .font(.system(size: 16, weight: .heavy))
                            .foregroundStyle(T.ink)
                        Text(item.id)
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundStyle(T.inkMute)
                    }
                    Spacer()
                    Pill(text: item.status.label, tone: item.status.tone)
                }
            }
        }
    }

    private var fieldsCard: some View {
        Card(padding: 16) {
            VStack(alignment: .leading, spacing: 0) {
                Text("申請内容")
                    .font(.system(size: 12, weight: .bold))
                    .foregroundStyle(T.inkSub).kerning(1.2)
                    .padding(.bottom, 12)
                fieldRow(label: "出寮日", value: item.leaveDate)
                if let r = item.returnDate {
                    divider; fieldRow(label: "帰寮日", value: r)
                }
                if let m = item.leaveMethod {
                    divider; fieldRow(label: "帰省方法", value: m)
                }
                if let m = item.returnMethod {
                    divider; fieldRow(label: "帰寮方法", value: m)
                }
                if let d = item.destination {
                    divider; fieldRow(label: "宿泊先", value: d)
                }
                divider; fieldRow(label: "提出日時", value: item.submittedAt)
            }
        }
    }

    private var divider: some View {
        Rectangle().fill(T.hair).frame(height: 0.5).padding(.vertical, 9)
    }

    private func fieldRow(label: String, value: String) -> some View {
        HStack(alignment: .firstTextBaseline) {
            Text(label)
                .font(.system(size: 13))
                .foregroundStyle(T.inkSub)
            Spacer()
            Text(value)
                .font(.system(size: 13, weight: .semibold))
                .foregroundStyle(T.ink)
                .multilineTextAlignment(.trailing)
        }
    }

    private var chainCard: some View {
        Card(padding: 18) {
            VStack(alignment: .leading, spacing: 0) {
                HStack {
                    Text("承認 chain")
                        .font(.system(size: 12, weight: .bold))
                        .foregroundStyle(T.inkSub).kerning(1.2)
                    Spacer()
                    Text("\(approvedCount) / \(item.chain.count)")
                        .font(.system(size: 11, weight: .semibold, design: .monospaced))
                        .foregroundStyle(T.inkMute)
                }
                .padding(.bottom, 14)
                if item.chain.isEmpty {
                    Text("この種別の届は承認 chain が定義されていません。")
                        .font(.system(size: 12))
                        .foregroundStyle(T.inkMute)
                } else {
                    ChainTimelineView(chain: item.chain)
                }
            }
        }
    }

    private func commentCard(_ s: ApprovalStep) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 6) {
                Text("⚠")
                    .font(.system(size: 12, weight: .bold))
                    .foregroundStyle(T.danger)
                Text("\(s.role.label) からのコメント")
                    .font(.system(size: 12, weight: .bold))
                    .foregroundStyle(T.danger)
            }
            Text(s.comment ?? "")
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
    }

    private var approvedCount: Int {
        item.chain.filter { $0.decision == .approved }.count
    }

    private func kindIcon(_ k: ApplicationKind) -> String {
        switch k {
        case .stay:    return "house"
        case .holiday: return "house.lodge"
        case .return:  return "airplane"
        case .other:   return "doc.text"
        }
    }
}

// MARK: - 承認 chain 縦 timeline

private struct ChainTimelineView: View {
    let chain: [ApprovalStep]

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            ForEach(Array(chain.enumerated()), id: \.offset) { (i, step) in
                HStack(alignment: .top, spacing: 14) {
                    rail(step: step, isLast: i == chain.count - 1, prevDone: i > 0 && chain[i - 1].decision == .approved)
                    body(step: step, isLast: i == chain.count - 1)
                    Spacer(minLength: 0)
                }
            }
        }
    }

    @ViewBuilder
    private func rail(step: ApprovalStep, isLast: Bool, prevDone: Bool) -> some View {
        VStack(spacing: 0) {
            ZStack {
                Circle()
                    .fill(circleFill(step.decision))
                    .frame(width: 26, height: 26)
                switch step.decision {
                case .approved:
                    Image(systemName: "checkmark")
                        .font(.system(size: 12, weight: .heavy))
                        .foregroundStyle(.white)
                case .rejected:
                    Image(systemName: "xmark")
                        .font(.system(size: 12, weight: .heavy))
                        .foregroundStyle(.white)
                case .pending:
                    Circle().fill(.white).frame(width: 8, height: 8)
                }
            }
            if !isLast {
                Rectangle()
                    .fill(step.decision == .approved ? T.ok : T.hair)
                    .frame(width: 2)
                    .frame(maxHeight: .infinity)
                    .padding(.top, 4)
            }
        }
        .frame(width: 26)
    }

    @ViewBuilder
    private func body(step: ApprovalStep, isLast: Bool) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(spacing: 8) {
                Text(step.role.label)
                    .font(.system(size: 14, weight: .bold))
                    .foregroundStyle(T.ink)
                Pill(text: step.decision.label, tone: step.decision.tone)
            }
            if let name = step.approverName {
                Text("担当：\(name)")
                    .font(.system(size: 12))
                    .foregroundStyle(T.inkSub)
            }
            if let at = step.decidedAt {
                Text(at)
                    .font(.system(size: 11, design: .monospaced))
                    .foregroundStyle(T.inkMute)
            }
            if step.decision == .pending {
                Text("審査中")
                    .font(.system(size: 12))
                    .foregroundStyle(T.warnDeep)
            }
        }
        .padding(.top, 2)
        .padding(.bottom, isLast ? 0 : 18)
    }

    private func circleFill(_ d: ApprovalDecision) -> Color {
        switch d {
        case .approved: return T.ok
        case .rejected: return T.danger
        case .pending:  return T.inkFaint
        }
    }
}

// MARK: - Previews

#Preview("StayList · all") {
    StayListView()
        .environmentObject(RouterStore(initial: .stayList))
        .environmentObject(AppStore())
}

#Preview("StayDetail · pending（外泊・留学生 = 5 役职）") {
    StayDetailView(id: "a1")
        .environmentObject(RouterStore(initial: .stayDetail(id: "a1")))
        .environmentObject(AppStore())
}

#Preview("StayDetail · approved") {
    StayDetailView(id: "a3")
        .environmentObject(RouterStore(initial: .stayDetail(id: "a3")))
        .environmentObject(AppStore())
}

#Preview("StayDetail · returned（差戻）") {
    StayDetailView(id: "a2")
        .environmentObject(RouterStore(initial: .stayDetail(id: "a2")))
        .environmentObject(AppStore())
}
