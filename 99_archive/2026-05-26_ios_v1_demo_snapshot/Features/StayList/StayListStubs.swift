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
    case homeroom = "担任"
    case dormHead = "寮務部長"
    case dormChief = "寮務課長"
    case intlHead = "国際交流部長"
    case intlChief = "国際交流課長"
    case management = "管理係"

    var label: String {
        rawValue
    }
}

enum ApprovalDecision: String, Hashable {
    case pending, approved, rejected

    var label: String {
        switch self {
        case .pending: return "審査中"
        case .approved: return "承認"
        case .rejected: return "差戻"
        }
    }

    var tone: Pill.Tone {
        switch self {
        case .pending: return .warn
        case .approved: return .ok
        case .rejected: return .danger
        }
    }
}

struct ApprovalStep: Hashable, Identifiable {
    let role: ApprovalRole
    let approverName: String? // nil = 老师未指定 / 役职名のみ表示
    let decision: ApprovalDecision
    let decidedAt: String? // "2026-04-21 11:02"
    let comment: String?

    var id: String {
        role.rawValue
    }
}

/// アプリ内で扱う出寮届の詳細（GET /applications/:id 返り値の iOS 模型）
struct StayApplication: Hashable, Identifiable {
    let id: String // "a1" 等
    var kind: ApplicationKind // 外泊 / 帰省 / 帰国 / その他
    var status: ApplicationStatus // pending / approved / rejected / returned / withdrawn / draft
    var leaveDate: String // "2026-05-03"
    var returnDate: String?
    var summary: String // ApplicationItem.summary 互換
    var destination: String?
    var leaveMethod: String?
    var returnMethod: String?
    var chain: [ApprovalStep]
    let submittedAt: String // "2026-04-20 10:24"
    var auditLog: [AuditLogEntry] = [] // 操作履歴（提出 / 修改届 / 差戻 / 承認）

    /// 修改届 可提交：仅 pending / approved_partial / returned 状态可
    /// system_features §7.2.4 「pending / partiallyApproved / returned で編集可」
    /// backend PUT /applications/:id 同条件接受。
    var isEditable: Bool {
        switch status {
        case .pending, .approved_partial, .returned: return true
        default: return false
        }
    }
}

// MARK: - 操作履歴 entry

struct AuditLogEntry: Hashable, Identifiable {
    let id: UUID
    let at: String // "2026-05-01 14:32"
    let action: String // "提出" / "修改届を提出" / "差戻" / "承認" 等
    let actor: String // 役职名 + 担当者名 / 申請者本人
    let detail: String? // 修改届時の amendReason / 差戻理由 等

    init(at: String, action: String, actor: String, detail: String? = nil) {
        id = UUID()
        self.at = at
        self.action = action
        self.actor = actor
        self.detail = detail
    }
}

enum ApplicationKind: String, Hashable {
    case stay = "外泊"
    case holiday = "帰省"
    case `return` = "帰国"
    case other = "その他"

    /// SEED.applications.type ("stay" / "holiday" / "return" / ...) からマップ
    static func fromSeedType(_ t: String) -> ApplicationKind {
        switch t {
        case "stay": return .stay
        case "holiday": return .holiday
        case "return": return .return
        default: return .other
        }
    }
}

enum ApplicationStatus: String, Hashable {
    case draft, pending
    case approved_partial // chain 部分通过的中间态（backend 6 个值之一）
    case approved, rejected, returned, withdrawn

    var label: String {
        switch self {
        case .draft: return "下書き"
        case .pending: return "審査中"
        case .approved_partial: return "一部承認"
        case .approved: return "承認済"
        case .rejected: return "差戻"
        case .returned: return "要修正"
        case .withdrawn: return "取消済"
        }
    }

    var tone: Pill.Tone {
        switch self {
        case .draft: return .neutral
        case .pending: return .warn
        case .approved_partial: return .warn // amber 色、介于 approved 和 pending 之间
        case .approved: return .ok
        case .rejected: return .danger
        case .returned: return .danger
        case .withdrawn: return .neutral
        }
    }

    static func fromSeed(_ s: String) -> ApplicationStatus {
        ApplicationStatus(rawValue: s) ?? .pending
    }

    /// backend 的 status 字符串（6 个值）→ enum 转换。未知值就 fallback 到 pending。
    static func fromBackend(_ s: String) -> ApplicationStatus {
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
        case .stay: return stayChain(isOverseas: isOverseas)
        case .holiday: return holidayChain(isOverseas: isOverseas)
        case .return: return holidayChain(isOverseas: isOverseas)
        case .other: return []
        }
    }
}

// MARK: - モックデータ（B 未到位 → SEED.applications を拡張）

@MainActor
enum StayListMock {
    /// 暫定の留学生フラグ（SEED.user に is_overseas が無いため、リュウ イヒ = 留学生 扱いとする）
    static let isOverseas: Bool = true

    /// 修改届 mock store（lazy init から initial seed を構築）
    /// `@MainActor` で囲い込んでいるので nonisolated unsafe は不要。view は全て MainActor で動く。
    /// API 接続時は `URLSession + async/await`（IOS_DESIGN_LOG §11.9 I2）に置換。
    private static var _store: [StayApplication]?

    static var all: [StayApplication] {
        if _store == nil { _store = buildInitial() }
        return _store ?? []
    }

    static func find(_ id: String) -> StayApplication? {
        all.first(where: { $0.id == id })
    }

    /// 修改届 提出 — chain 全員 reset to pending + auditLog append + status = pending
    /// system_features §7.2.5「修改届 提交后，承认 chain 全员重置」
    static func applyAmendment(
        id: String,
        leaveDate: String,
        returnDate: String?,
        leaveMethod: String?,
        returnMethod: String?,
        destination: String?,
        amendReason: String
    ) {
        if _store == nil { _store = buildInitial() }
        guard var arr = _store, let idx = arr.firstIndex(where: { $0.id == id }) else { return }
        var item = arr[idx]

        // 字段更新
        item.leaveDate = leaveDate
        item.returnDate = returnDate
        item.leaveMethod = leaveMethod
        item.returnMethod = returnMethod
        if destination != nil { item.destination = destination }

        // chain 全員 reset to pending
        item.chain = item.chain.map { step in
            ApprovalStep(
                role: step.role,
                approverName: step.approverName,
                decision: .pending,
                decidedAt: nil,
                comment: nil
            )
        }
        item.status = .pending

        // auditLog append（最新が先頭）
        let entry = AuditLogEntry(
            at: nowJaString(),
            action: "修改届を提出",
            actor: SEED.user.name,
            detail: amendReason
        )
        item.auditLog.insert(entry, at: 0)

        arr[idx] = item
        _store = arr
    }

    private static func buildInitial() -> [StayApplication] {
        SEED.applications.compactMap { item in
            let kind = ApplicationKind.fromSeedType(item.type)
            let status = ApplicationStatus.fromSeed(item.status)
            let chainRoles = ApprovalChainBuilder.chain(for: kind, isOverseas: isOverseas)
            let steps = makeSteps(for: chainRoles, applicationStatus: status, baseDate: item.date)
            // outing / return / parcel / repair / guest / other は #5 の対象外（chain 無し）
            // → 見せても意味がないので、出寮届 系（stay / holiday / return）のみ表示
            guard kind != .other else { return nil }
            // 初期 auditLog: 提出 entry 1 件 + 差戻 / 承認 ある場合の history も補足
            var auditLog: [AuditLogEntry] = []
            auditLog.append(AuditLogEntry(
                at: "\(item.date) 10:24",
                action: "提出",
                actor: SEED.user.name,
                detail: nil
            ))
            for step in steps where step.decision != .pending {
                let actionLabel = step.decision == .approved ? "承認" : "差戻"
                auditLog.append(AuditLogEntry(
                    at: step.decidedAt ?? item.date,
                    action: actionLabel,
                    actor: "\(step.role.label)：\(step.approverName ?? "—")",
                    detail: step.comment
                ))
            }
            // 最新が先頭
            auditLog.sort { $0.at > $1.at }

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
                submittedAt: "\(item.date) 10:24",
                auditLog: auditLog
            )
        }
    }

    private static func nowJaString() -> String {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd HH:mm"
        f.locale = Locale(identifier: "ja_JP")
        return f.string(from: Date())
    }

    /// chain の各 step に decision / decided_at を割り当てる（status から逆算）
    private static func makeSteps(
        for roles: [ApprovalRole],
        applicationStatus status: ApplicationStatus,
        baseDate: String
    ) -> [ApprovalStep] {
        guard !roles.isEmpty else { return [] }
        let names: [ApprovalRole: String] = [
            .homeroom: "松本 先生",
            .dormHead: "高野 先生",
            .dormChief: "新股 先生",
            .intlHead: "難波 先生",
            .intlChief: "小林 先生",
            .management: "田中 先生",
        ]
        // 按 status 判断已承认的役职数
        let approvedCount: Int = {
            switch status {
            case .approved: return roles.count
            case .approved_partial: return max(roles.count - 1, 1) // 部分承认: 最后一个还未决
            case .rejected, .returned: return max(roles.count - 1, 1) // 最后一个差戻
            case .pending: return roles.count > 2 ? 1 : 0 // 进行中: 仅头部承认
            case .draft, .withdrawn: return 0
            }
        }()
        // 差戻の場合、最後の承認役职は rejected
        let rejectedIndex: Int? = (status == .rejected) ? approvedCount : nil

        return roles.enumerated().map { idx, role in
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
    @EnvironmentObject var app: AppStore

    @State private var filter: ApplicationStatus? = nil // nil = すべて
    // A-037 (2026-05-21): 切回 ApplicationsAPI.listMine() — StayListMock 仅作未登录态兜底
    @State private var apps: [StayApplication] = []
    @State private var isLoading: Bool = false
    @State private var firstLoadDone: Bool = false
    @State private var loadError: String? = nil

    private var items: [StayApplication] {
        let sorted = apps.sorted { $0.leaveDate > $1.leaveDate }
        guard let f = filter else { return sorted }
        return sorted.filter { $0.status == f }
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

                    if isLoading && !firstLoadDone {
                        // 首次加载、显示 spinner 居中
                        ProgressView()
                            .tint(T.primary)
                            .frame(maxWidth: .infinity, minHeight: 120)
                    } else if items.isEmpty {
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
            .refreshable { await load() }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
        .task { await load() }
    }

    /// A-037 (2026-05-21): 切回 ApplicationsAPI.listMine()
    /// 未登录态（401 / 无 token）回退到 StayListMock；登录后真数据
    private func load() async {
        isLoading = true
        loadError = nil
        defer {
            isLoading = false
            firstLoadDone = true
        }
        // 未登录态用 mock 兜底（开发时无 backend / Apple reviewer 没真账号也能看效果）
        guard app.isAuthenticated else {
            apps = StayListMock.all
            return
        }
        do {
            let raw = try await ApplicationsAPI.listMine()
            apps = raw.map { $0.toStayApplication() }
        } catch {
            // 出错降级到 mock，避免空 view 影响调试
            loadError = "申請一覧の取得に失敗しました"
            apps = StayListMock.all
        }
    }

    private var filterTabs: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 6) {
                ForEach(Array(tabs.enumerated()), id: \.offset) { _, tab in
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
            ForEach(Array(item.chain.enumerated()), id: \.offset) { i, step in
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
        case .pending: return T.inkFaint
        }
    }

    private func roleBg(_ d: ApprovalDecision) -> Color {
        switch d {
        case .approved: return T.okBg
        case .rejected: return T.dangerBg
        case .pending: return T.hairSoft
        }
    }

    private func roleFg(_ d: ApprovalDecision) -> Color {
        switch d {
        case .approved: return T.okDeep
        case .rejected: return T.danger
        case .pending: return T.inkSub
        }
    }

    private func kindIcon(_ k: ApplicationKind) -> String {
        switch k {
        case .stay: return "house"
        case .holiday: return "house.lodge"
        case .return: return "airplane"
        case .other: return "doc.text"
        }
    }
}

// ============================================================================
// MARK: - StayDetailView · 申請詳細 + 承認 chain 縦 timeline

// ============================================================================

struct StayDetailView: View {
    let id: String
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var tab: DetailTab = .detail
    /// API 拉到的详情；nil = 加载中
    @State private var loadedItem: StayApplication? = nil
    /// API 拉到的改动履历
    @State private var loadedAuditLog: [AuditLogEntry] = []
    @State private var isLoading: Bool = false

    enum DetailTab: Hashable { case detail, history }

    /// 已加载的 item 或 placeholder（用于 view 渲染前的占位）
    private var item: StayApplication {
        loadedItem ?? StayApplication(
            id: id, kind: .stay, status: .pending,
            leaveDate: "—", returnDate: nil,
            summary: "—", destination: nil,
            leaveMethod: nil, returnMethod: nil,
            chain: [], submittedAt: "—",
            auditLog: loadedAuditLog
        )
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "申請詳細", level: 2)
            tabBar
                .padding(.horizontal, 20)
                .padding(.top, 12)
                .padding(.bottom, 8)
            ScrollView {
                if isLoading && loadedItem == nil {
                    ProgressView()
                        .tint(T.primary)
                        .frame(maxWidth: .infinity, minHeight: 200)
                } else {
                    VStack(alignment: .leading, spacing: 16) {
                        if tab == .detail {
                            headerCard
                            fieldsCard
                            chainCard
                            if let last = item.chain.last(where: { $0.comment != nil }) {
                                commentCard(last)
                            }
                            if item.isEditable {
                                editButton
                            }
                        } else {
                            headerCard
                            historyCard
                        }
                        Color.clear.frame(height: 12)
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 4)
                    .padding(.bottom, 28)
                }
            }
            .refreshable { await load() }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
        .task { await load() }
    }

    /// ⚠️ DEMO-ONLY-SCAFFOLD（2026-05-03）：纯 mock，无后端依赖
    /// v1.0 切回：UUID guard + ApplicationsAPI.detail / .audit 并行 + 4 个 catch 分支
    private func load() async {
        isLoading = true
        defer { isLoading = false }
        if let item = StayListMock.find(id) {
            loadedItem = item
            loadedAuditLog = item.auditLog
        } else {
            app.showToast("申請が見つかりません")
            router.back()
        }
    }

    // MARK: - segmented tab

    private var tabBar: some View {
        HStack(spacing: 0) {
            tabButton(label: "詳細", value: .detail)
            tabButton(label: "履歴 (\(item.auditLog.count))", value: .history)
        }
        .padding(3)
        .background {
            RoundedRectangle(cornerRadius: 12, style: .continuous).fill(T.pill)
        }
    }

    @ViewBuilder
    private func tabButton(label: String, value: DetailTab) -> some View {
        let selected = tab == value
        Button { tab = value } label: {
            Text(label)
                .font(.system(size: 13, weight: .semibold))
                .foregroundStyle(selected ? Color.white : T.inkSub)
                .frame(maxWidth: .infinity)
                .frame(height: 32)
                .background {
                    RoundedRectangle(cornerRadius: 9, style: .continuous)
                        .fill(selected ? T.primary : Color.clear)
                }
        }
        .buttonStyle(.plain)
    }

    // MARK: - 編集 button (isEditable のみ)

    private var editButton: some View {
        Button {
            router.go(.stayEdit(id: item.id))
        } label: {
            HStack(spacing: 8) {
                Image(systemName: "pencil")
                    .font(.system(size: 14, weight: .semibold))
                Text("修改届を提出")
                    .font(.system(size: 14, weight: .bold))
            }
            .foregroundStyle(.white)
            .frame(maxWidth: .infinity)
            .frame(height: 50)
            .background {
                RoundedRectangle(cornerRadius: 14, style: .continuous).fill(T.primary)
            }
        }
        .buttonStyle(.plain)
    }

    // MARK: - 履歴 card

    private var historyCard: some View {
        Card(padding: 18) {
            VStack(alignment: .leading, spacing: 0) {
                HStack {
                    Text("操作履歴")
                        .font(.system(size: 12, weight: .bold))
                        .foregroundStyle(T.inkSub).kerning(1.2)
                    Spacer()
                    Text("\(item.auditLog.count) 件")
                        .font(.system(size: 11, weight: .semibold, design: .monospaced))
                        .foregroundStyle(T.inkMute)
                }
                .padding(.bottom, 14)
                if item.auditLog.isEmpty {
                    Text("履歴はまだありません。")
                        .font(.system(size: 12))
                        .foregroundStyle(T.inkMute)
                } else {
                    ForEach(Array(item.auditLog.enumerated()), id: \.element.id) { i, e in
                        auditRow(entry: e, isFirst: i == 0, isLast: i == item.auditLog.count - 1)
                    }
                }
            }
        }
    }

    private func auditRow(entry: AuditLogEntry, isFirst _: Bool, isLast: Bool) -> some View {
        HStack(alignment: .top, spacing: 12) {
            VStack(spacing: 0) {
                Circle()
                    .fill(auditColor(entry.action))
                    .frame(width: 10, height: 10)
                if !isLast {
                    Rectangle()
                        .fill(T.hair)
                        .frame(width: 1.5)
                        .frame(maxHeight: .infinity)
                        .padding(.top, 4)
                }
            }
            .frame(width: 10)
            .padding(.top, 4)

            VStack(alignment: .leading, spacing: 4) {
                HStack(spacing: 8) {
                    Text(entry.action)
                        .font(.system(size: 13, weight: .bold))
                        .foregroundStyle(T.ink)
                    Text(entry.at)
                        .font(.system(size: 11, design: .monospaced))
                        .foregroundStyle(T.inkMute)
                }
                Text(entry.actor)
                    .font(.system(size: 12))
                    .foregroundStyle(T.inkSub)
                if let d = entry.detail, !d.isEmpty {
                    Text(d)
                        .font(.system(size: 12))
                        .foregroundStyle(T.inkSub)
                        .lineSpacing(3)
                        .padding(.top, 2)
                        .padding(.horizontal, 10).padding(.vertical, 7)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background {
                            RoundedRectangle(cornerRadius: 8, style: .continuous).fill(T.pill)
                        }
                }
            }
            .padding(.bottom, isLast ? 0 : 14)
        }
    }

    private func auditColor(_ action: String) -> Color {
        if action.contains("承認") { return T.ok }
        if action.contains("差戻") { return T.danger }
        if action.contains("修改") { return T.warn }
        return T.primary
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
                    Text("承認の流れ")
                        .font(.system(size: 12, weight: .bold))
                        .foregroundStyle(T.inkSub).kerning(1.2)
                    Spacer()
                    Text("\(approvedCount) / \(item.chain.count)")
                        .font(.system(size: 11, weight: .semibold, design: .monospaced))
                        .foregroundStyle(T.inkMute)
                }
                .padding(.bottom, 14)
                if item.chain.isEmpty {
                    Text("この種別の届は承認手続きの設定がありません。")
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
        case .stay: return "house"
        case .holiday: return "house.lodge"
        case .return: return "airplane"
        case .other: return "doc.text"
        }
    }
}

// MARK: - 承認 chain 縦 timeline

private struct ChainTimelineView: View {
    let chain: [ApprovalStep]

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            ForEach(Array(chain.enumerated()), id: \.offset) { i, step in
                HStack(alignment: .top, spacing: 14) {
                    rail(step: step, isLast: i == chain.count - 1, prevDone: i > 0 && chain[i - 1].decision == .approved)
                    body(step: step, isLast: i == chain.count - 1)
                    Spacer(minLength: 0)
                }
            }
        }
    }

    private func rail(step: ApprovalStep, isLast: Bool, prevDone _: Bool) -> some View {
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
        case .pending: return T.inkFaint
        }
    }
}

// ============================================================================
// MARK: - StayEditForm · 出寮届 修改届（system_features §7.2.4-5）

//
// 提出条件: original.isEditable == true（status ∈ {pending, returned}）
// 提出後: chain 全員 reset to pending + auditLog append + status = pending
// 身份字段（学号/姓名/学年・組/寮・部屋/区分/携帯）read-only
// 修改の理由 必填（chain 再批時に各 approver に見せる）
// ============================================================================

struct StayEditForm: View {
    let id: String
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    /// API 拉到的原 item；nil = 加载中
    @State private var loadedOriginal: StayApplication? = nil
    @State private var isLoading: Bool = false
    @State private var isSubmitting: Bool = false

    private var original: StayApplication {
        loadedOriginal ?? StayApplication(
            id: id, kind: .stay, status: .pending,
            leaveDate: "—", returnDate: nil, summary: "—",
            destination: nil, leaveMethod: nil, returnMethod: nil,
            chain: [], submittedAt: "—"
        )
    }

    // ── 編集対象 (init で original から prefill) ──────────────────────────
    @State private var leaveDate: Date = .init()
    @State private var returnDate: Date = .init()
    @State private var leaveMethod: String = "JR"
    @State private var returnMethod: String = "JR"
    @State private var destination: String = ""
    @State private var amendReason: String = ""
    @State private var didInit: Bool = false

    private let TRANSPORTS = ["JR", "バス", "自家用車", "タクシー", "教員送迎", "飛行機", "その他"]

    private var needsDestination: Bool {
        original.kind == .stay || original.kind == .return
    }

    private var canSubmit: Bool {
        !amendReason.trimmingCharacters(in: .whitespaces).isEmpty
            && returnDate >= leaveDate
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "\(original.kind.rawValue)届 修改届", level: 3)
            ScrollView {
                if isLoading && loadedOriginal == nil {
                    ProgressView()
                        .tint(T.primary)
                        .frame(maxWidth: .infinity, minHeight: 200)
                } else {
                    VStack(alignment: .leading, spacing: 18) {
                        warningBanner
                        identitySection
                        dateSection
                        methodSection
                        if needsDestination {
                            destinationSection
                        }
                        amendReasonSection
                        submitRow
                        Color.clear.frame(height: 8)
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 12)
                    .padding(.bottom, 32)
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
        .task { await load() }
    }

    /// ⚠️ DEMO-ONLY-SCAFFOLD（2026-05-03）：纯 mock，无后端依赖
    /// v1.0 切回：UUID guard + ApplicationsAPI.detail + 4 个 catch 分支
    private func load() async {
        isLoading = true
        defer { isLoading = false }
        if let item = StayListMock.find(id) {
            loadedOriginal = item
            initFields()
        } else {
            app.showToast("申請が見つかりません")
            router.back()
        }
    }

    // MARK: - sections

    private var warningBanner: some View {
        HStack(alignment: .top, spacing: 8) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 13))
                .foregroundStyle(T.warnDeep)
                .padding(.top, 1)
            VStack(alignment: .leading, spacing: 3) {
                Text("修改届を提出すると、承認の流れが最初からやり直しになります。")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundStyle(T.warnDeep)
                Text("先にご承認いただいた先生にも、もう一度ご承認をお願いすることになります。")
                    .font(.system(size: 11.5))
                    .foregroundStyle(T.warnDeep.opacity(0.85))
                    .lineSpacing(3)
            }
        }
        .padding(.horizontal, 14).padding(.vertical, 12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background {
            RoundedRectangle(cornerRadius: 12, style: .continuous).fill(T.warnBg)
        }
        .overlay {
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(T.warn.opacity(0.3), lineWidth: 1)
        }
    }

    private var identitySection: some View {
        VStack(alignment: .leading, spacing: 8) {
            sectionLabel("申請者本人（変更不可）")
            Card(padding: 0) {
                VStack(spacing: 0) {
                    idRow("学号", SEED.user.account, isFirst: true)
                    idRow("氏名", SEED.user.name)
                    idRow("学年・組", "\(SEED.user.grade) \(SEED.user.classSuffix)組 \(SEED.user.seatNo)番")
                    idRow("寮・部屋", "\(SEED.user.dorm) \(SEED.user.room)")
                    idRow("区分", SEED.user.category)
                    idRow("携帯電話", SEED.user.phone)
                }
            }
            Text("※ 身份情報の変更は寮監にご連絡ください。修改届では変更できません。")
                .font(.system(size: 11))
                .foregroundStyle(T.inkMute)
        }
    }

    private var dateSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            sectionLabel("出寮 / 帰寮日")
            Card(padding: 14) {
                VStack(alignment: .leading, spacing: 14) {
                    VStack(alignment: .leading, spacing: 5) {
                        Text("出寮日")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundStyle(T.inkSub)
                        DatePicker("", selection: $leaveDate, displayedComponents: .date)
                            .labelsHidden()
                            .datePickerStyle(.compact)
                            .environment(\.locale, Locale(identifier: "ja_JP"))
                        if let orig = parseYMD(original.leaveDate) {
                            originalNote(label: "原値", text: formatYMDJa(orig))
                        }
                    }
                    Divider().background(T.hair)
                    VStack(alignment: .leading, spacing: 5) {
                        Text("帰寮日")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundStyle(T.inkSub)
                        DatePicker("", selection: $returnDate, in: leaveDate..., displayedComponents: .date)
                            .labelsHidden()
                            .datePickerStyle(.compact)
                            .environment(\.locale, Locale(identifier: "ja_JP"))
                        if let r = original.returnDate, let orig = parseYMD(r) {
                            originalNote(label: "原値", text: formatYMDJa(orig))
                        }
                    }
                }
            }
        }
    }

    private var methodSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            sectionLabel("移動方法")
            Card(padding: 14) {
                VStack(alignment: .leading, spacing: 14) {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("出寮方法")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundStyle(T.inkSub)
                        chipRow(options: TRANSPORTS, selected: $leaveMethod)
                        if let m = original.leaveMethod, m != leaveMethod {
                            originalNote(label: "原値", text: m)
                        }
                    }
                    Divider().background(T.hair)
                    VStack(alignment: .leading, spacing: 6) {
                        Text("帰寮方法")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundStyle(T.inkSub)
                        chipRow(options: TRANSPORTS, selected: $returnMethod)
                        if let m = original.returnMethod, m != returnMethod {
                            originalNote(label: "原値", text: m)
                        }
                    }
                }
            }
        }
    }

    private var destinationSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            sectionLabel("宿泊先")
            Card(padding: 14) {
                VStack(alignment: .leading, spacing: 8) {
                    TField(text: $destination, placeholder: "宿泊先住所")
                    if let d = original.destination, d != destination {
                        originalNote(label: "原値", text: d)
                    }
                }
            }
        }
    }

    private var amendReasonSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 4) {
                sectionLabel("修改の理由")
                Text("*").foregroundStyle(T.danger).font(.system(size: 13, weight: .heavy))
            }
            TArea(
                text: $amendReason,
                placeholder: "修改の理由を入力してください",
                rows: 4
            )
            Text("※ 各役职の先生にこの理由が表示されます。")
                .font(.system(size: 11))
                .foregroundStyle(T.inkMute)
        }
    }

    private var submitRow: some View {
        HStack(spacing: 10) {
            Button {
                router.back()
            } label: {
                Text("キャンセル")
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
                Text("修改届を提出")
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

    // MARK: - helpers

    private func initFields() {
        guard !didInit else { return }
        didInit = true
        if let d = parseYMD(original.leaveDate) { leaveDate = d }
        if let r = original.returnDate, let d = parseYMD(r) {
            returnDate = d
        } else {
            returnDate = leaveDate
        }
        leaveMethod = original.leaveMethod ?? "JR"
        returnMethod = original.returnMethod ?? "JR"
        destination = original.destination ?? ""
    }

    private func submit() {
        Task { await submitAsync() }
    }

    /// ⚠️ DEMO-ONLY-SCAFFOLD（2026-05-03）：纯 mock，无后端依赖
    /// v1.0 切回：UUID guard + 构造 ApplicationUpdateBody + ApplicationsAPI.update + 5 个 catch 分支
    private func submitAsync() async {
        let trimmedDest = destination.trimmingCharacters(in: .whitespaces)
        isSubmitting = true
        defer { isSubmitting = false }
        StayListMock.applyAmendment(
            id: original.id,
            leaveDate: formatYMD(leaveDate),
            returnDate: formatYMD(returnDate),
            leaveMethod: leaveMethod,
            returnMethod: returnMethod,
            destination: trimmedDest.isEmpty ? nil : trimmedDest,
            amendReason: amendReason
        )
        app.showToast("修改届を提出しました")
        router.back()
    }

    private func parseYMD(_ s: String) -> Date? {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        f.locale = Locale(identifier: "en_US_POSIX")
        return f.date(from: s)
    }

    private func formatYMD(_ d: Date) -> String {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        f.locale = Locale(identifier: "en_US_POSIX")
        return f.string(from: d)
    }

    private func formatYMDJa(_ d: Date) -> String {
        let f = DateFormatter()
        f.dateFormat = "yyyy 年 M 月 d 日"
        f.locale = Locale(identifier: "ja_JP")
        return f.string(from: d)
    }

    private func sectionLabel(_ text: String) -> some View {
        Text(text)
            .font(.system(size: 13, weight: .bold))
            .foregroundStyle(T.inkSub)
            .kerning(0.5)
    }

    private func idRow(_ k: String, _ v: String, isFirst: Bool = false) -> some View {
        VStack(spacing: 0) {
            if !isFirst { Divider().background(T.hair) }
            HStack(alignment: .top) {
                Text(k)
                    .font(.system(size: 13))
                    .foregroundStyle(T.inkSub)
                    .frame(width: 90, alignment: .leading)
                Text(v)
                    .font(.system(size: 13.5, weight: .medium))
                    .foregroundStyle(T.ink)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
            .padding(.horizontal, 16).padding(.vertical, 13)
        }
    }

    private func chipRow(options: [String], selected: Binding<String>) -> some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 6) {
                ForEach(options, id: \.self) { opt in
                    let on = selected.wrappedValue == opt
                    Button { selected.wrappedValue = opt } label: {
                        Text(opt)
                            .font(.system(size: 12, weight: .semibold))
                            .padding(.horizontal, 12).padding(.vertical, 7)
                            .foregroundStyle(on ? Color.white : T.ink)
                            .background {
                                Capsule().fill(on ? T.primary : T.paper)
                            }
                            .overlay {
                                Capsule().stroke(on ? T.primary : T.hair, lineWidth: 1)
                            }
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }

    private func originalNote(label: String, text: String) -> some View {
        HStack(spacing: 6) {
            Text(label)
                .font(.system(size: 10.5, weight: .semibold))
                .foregroundStyle(T.inkMute)
                .padding(.horizontal, 6).padding(.vertical, 1)
                .background {
                    Capsule().fill(T.pill)
                }
            Text(text)
                .font(.system(size: 11))
                .foregroundStyle(T.inkMute)
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

#Preview("StayEdit · 修改届") {
    StayEditForm(id: "a2")
        .environmentObject(RouterStore(initial: .stayEdit(id: "a2")))
        .environmentObject(AppStore())
}

// ============================================================================
// MARK: - Network → ViewModel converter

// 把 ApplicationOut（backend wire format）转成 StayApplication（UI view-model）
// + AuditLogOut → AuditLogEntry 转换 + 日付/时刻格式化
// ============================================================================

/// JST 时区 "yyyy-MM-dd HH:mm" 格式化（chain decided_at / audit created_at 用）
private let backendDisplayDateFmt: DateFormatter = {
    let f = DateFormatter()
    f.dateFormat = "yyyy-MM-dd HH:mm"
    f.locale = Locale(identifier: "en_US_POSIX")
    f.timeZone = TimeZone(identifier: "Asia/Tokyo")
    return f
}()

extension ApplicationOut {
    /// 转成 UI 用的 StayApplication（view-model）
    func toStayApplication() -> StayApplication {
        // kind 字符串 → enum（"外泊" → .stay）
        let kindEnum = ApplicationKind(rawValue: kind) ?? .other
        let statusEnum = ApplicationStatus.fromBackend(status)

        // chain 转换
        let steps: [ApprovalStep] = approval_chain.map { stepOut in
            let role = ApprovalRole(rawValue: stepOut.approver_role) ?? .management
            let decision: ApprovalDecision
            switch stepOut.decision {
            case "approve": decision = .approved
            case "reject": decision = .rejected
            default: decision = .pending // nil = 未决
            }
            let decidedStr: String? = stepOut.decided_at.map { backendDisplayDateFmt.string(from: $0) }
            return ApprovalStep(
                role: role,
                approverName: nil, // backend 暂不返 approver name（仅 approver_id）
                decision: decision,
                decidedAt: decidedStr,
                comment: stepOut.comment
            )
        }

        // 简要文案（一覧 row 用）— "外泊届 5/3〜5/5 · 友達宅"
        let summaryText = Self.makeSummary(kind: kindEnum, leaveDate: leave_date, returnDate: return_date, stayLocations: stay_locations)

        // 滞在先（一行目だけ表示用）
        let firstLocationName: String? = stay_locations?.first?["name"]?.value

        return StayApplication(
            id: id.uuidString.lowercased(),
            kind: kindEnum,
            status: statusEnum,
            leaveDate: leave_date,
            returnDate: return_date,
            summary: summaryText,
            destination: firstLocationName,
            leaveMethod: leave_method,
            returnMethod: return_method,
            chain: steps,
            submittedAt: backendDisplayDateFmt.string(from: submitted_at),
            auditLog: [] // 详情页另发 GET /audit 拉取
        )
    }

    private static func makeSummary(
        kind _: ApplicationKind,
        leaveDate: String,
        returnDate: String,
        stayLocations: [[String: AnyJSON]]?
    ) -> String {
        let dateRange = leaveDate == returnDate ? leaveDate : "\(leaveDate) 〜 \(returnDate)"
        if let first = stayLocations?.first?["name"]?.value, !first.isEmpty {
            return "\(dateRange) · \(first)"
        }
        return dateRange
    }
}

extension AuditLogOut {
    /// 转成 UI 用的 AuditLogEntry
    func toAuditLogEntry() -> AuditLogEntry {
        let timeStr = backendDisplayDateFmt.string(from: created_at)
        let actionLabel = Self.translateAction(action)
        let actorLabel = actor_type == "student" ? SEED.user.name : "教員" // 暂用 actor_type 区分
        // payload 里如果有 reason / comment 等可读字段、塞到 detail
        let detailText: String? = payload?["reason"]?.value ?? payload?["comment"]?.value
        return AuditLogEntry(
            at: timeStr,
            action: actionLabel,
            actor: actorLabel,
            detail: detailText?.isEmpty == false ? detailText : nil
        )
    }

    private static func translateAction(_ raw: String) -> String {
        switch raw {
        case "application.submit": return "提出"
        case "application.amend": return "修改届を提出"
        case "application.approve": return "承認"
        case "application.reject": return "差戻"
        case "application.withdraw": return "取消"
        default: return raw
        }
    }
}
