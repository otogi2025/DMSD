// StayListStubs.swift · 申请履历 列表 + 承认 chain 详情
// ⭐ 会话 C · 老師 38 条 #5「提交后给提交者展示承认状态」
//
// API 对应（B 未到位 → mock）:
//   GET /applications/mine    → StayListView         (BACKEND_DESIGN_LOG §5.2.2)
//   GET /applications/:id     → StayDetailView       (BACKEND_DESIGN_LOG §5.2.3)
//
// chain 规则（IOS_DESIGN_LOG §11.9 I11）:
//   外泊届 一般 = 担任 / 寮務課長 / 管理係                         (3 役职)
//   外泊届 留学生 = 担任 / 国際交流部長 / 寮務課長 / 寮務部長 / 管理係  (5 役职)
//   帰省 / 帰国届 chain = ⏳ 实物表 evidence 待确认

import SwiftUI

// MARK: - 角色 / 决定 / chain 步骤模型

enum ApprovalRole: String, CaseIterable, Hashable {
    case homeroom = "担任"
    case dormHead = "寮務部長"
    case dormChief = "寮務課長"
    case intlHead = "国際交流部長"
    case intlChief = "国際交流課長"
    case management = "管理係"
    case principal = "校長"

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
        case .rejected: return "差し戻し"
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
    let approverName: String? // nil = 老师未指定 / 仅显示役职名
    let decision: ApprovalDecision
    let decidedAt: String? // "2026-04-21 11:02"
    let comment: String?

    var id: String {
        role.rawValue
    }
}

/// 应用内处理的出寮届详情（GET /applications/:id 返回值的 iOS 数据模型）
struct StayApplication: Hashable, Identifiable {
    let id: String // "a1" 等
    var kind: ApplicationKind // 外泊 / 帰省 / 帰国 / 其他
    var status: ApplicationStatus // pending / approved / rejected / returned / withdrawn / draft
    var leaveDate: String // "2026-05-03"
    var returnDate: String?
    var summary: String // ApplicationItem.summary 互換
    var destination: String?
    var leaveMethod: String?
    var returnMethod: String?
    var taxiReservationTime: String? = nil // 出租车预约时刻 "HH:MM:SS"，nil = 不预约（itsuki 2026-06-03）
    var chain: [ApprovalStep]
    let submittedAt: String // "2026-04-20 10:24"
    var auditLog: [AuditLogEntry] = [] // 操作履歴（提出 / 修改届 / 差戻 / 承認）

    /// 修改届 可提交：仅 pending / approved_partial / returned 状态可
    /// system_features §7.2.4 「pending / partiallyApproved / returned 状态可编辑」
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
    let action: String // 操作类型，如「提出」「変更届を提出」「差戻」「承認」等
    let actor: String // 役职名 + 担当者名 / 申請者本人
    let detail: String? // 修改届时的 amendReason / 差戻理由 等

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

    /// 从 SEED.applications.type ("stay" / "holiday" / "return" / ...) 映射
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
        case .rejected: return "差し戻し"
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

// MARK: - chain 生成器（mock / I11 规则对应）

enum ApprovalChainBuilder {
    /// 生成外泊届 chain（IOS_DESIGN_LOG §11.9 I11 的规则）
    /// - Parameter isOverseas: 学生是否为留学生（system_features §7.2.2 / Q11）
    static func stayChain(isOverseas: Bool) -> [ApprovalRole] {
        if isOverseas {
            // 留学生 = 担任 / 国際交流部長 / 寮務課長 / 寮務部長 / 管理係（5 役职）
            return [.homeroom, .intlHead, .dormChief, .dormHead, .management]
        } else {
            // 一般 = 担任 / 寮務課長 / 管理係（3 役职）
            return [.homeroom, .dormChief, .management]
        }
    }

    /// 帰省 / 帰国届 chain — evidence 待确认（暂定: 与外泊相同 / 老师 LINE「外泊と同じ」）
    static func holidayChain(isOverseas: Bool) -> [ApprovalRole] {
        // ⏳ 实物表到达后确定。暂定使用与外泊相同的 chain。
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

// MARK: - mock 数据（后端 B 未到位 → 扩展 SEED.applications）

@MainActor
enum StayListMock {
    /// 暂定留学生标志（因 SEED.user 无 is_overseas 字段，将「リュウ イヒ」视为留学生处理）
    static let isOverseas: Bool = true

    /// 修改届 mock store（从 lazy init 构建初始 seed）
    /// 已用 `@MainActor` 包裹，无需 nonisolated unsafe。所有 view 均在 MainActor 上运行。
    /// API 接入时替换为 `URLSession + async/await`（IOS_DESIGN_LOG §11.9 I2）。
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

        // auditLog append（最新记录在首位）
        let entry = AuditLogEntry(
            at: nowJaString(),
            action: "変更届を提出",
            actor: SEED.user.name,
            detail: amendReason
        )
        item.auditLog.insert(entry, at: 0)

        arr[idx] = item
        _store = arr
    }

    /// 撤回（mock）—— 未登录 / reviewer 态本地把 status 改成 withdrawn + 追加履历。
    /// 真实生产走 ApplicationsAPI.withdraw，不经此分支。
    static func applyWithdraw(id: String) {
        if _store == nil { _store = buildInitial() }
        guard var arr = _store, let idx = arr.firstIndex(where: { $0.id == id }) else { return }
        var item = arr[idx]
        item.status = .withdrawn

        let entry = AuditLogEntry(
            at: nowJaString(),
            action: "申請を取り消し",
            actor: SEED.user.name,
            detail: nil
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
            // outing / return / parcel / repair / guest / other 不在 #5 范围内（无 chain）
            // → 显示无意义，仅显示出寮届系（stay / holiday / return）
            guard kind != .other else { return nil }
            // 初始 auditLog: 1 条提出 entry + 有差戻 / 承認 时补充 history
            var auditLog: [AuditLogEntry] = []
            auditLog.append(AuditLogEntry(
                at: "\(item.date) 10:24",
                action: "提出",
                actor: SEED.user.name,
                detail: nil
            ))
            for step in steps where step.decision != .pending {
                let actionLabel = step.decision == .approved ? "承認" : "差し戻し"
                auditLog.append(AuditLogEntry(
                    at: step.decidedAt ?? item.date,
                    action: actionLabel,
                    actor: "\(step.role.label)：\(step.approverName ?? "—")",
                    detail: step.comment
                ))
            }
            // 最新记录在首位
            auditLog.sort { $0.at > $1.at }

            return StayApplication(
                id: item.id,
                kind: kind,
                status: status,
                leaveDate: item.date,
                returnDate: addDays(item.date, days: 2),
                summary: item.summary,
                destination: extractDestination(item.summary),
                leaveMethod: "JR",
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

    /// 为 chain 的各 step 分配 decision / decided_at（从 status 反推）
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
        // 差戻 的情况下，最后的承认役职为 rejected
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
        f.timeZone = TimeZone(identifier: "Asia/Tokyo") // 固定 JST，与 formatYMD 一致（codex 时区排查统一）
        guard let date = f.date(from: d),
              let added = ApplyFormDate.tokyoCalendar.date(byAdding: .day, value: days, to: date)
        else { return nil }
        return f.string(from: added)
    }
}

// ============================================================================
// MARK: - StayListView · 申請履歴 一览（我的页面 → 申請履歴）

// ============================================================================

struct StayListView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var filter: ApplicationStatus? = nil // nil = 全部
    // A-037 (2026-05-21): 切回 ApplicationsAPI.listMine() — StayListMock 仅作未登录态兜底
    @State private var apps: [StayApplication] = []
    @State private var isLoading: Bool = false
    @State private var firstLoadDone: Bool = false
    @State private var loadError: String? = nil

    private var items: [StayApplication] {
        let sorted = apps.sorted { $0.leaveDate > $1.leaveDate }
        guard let f = filter else { return sorted }
        // IX-019: 标签按状态组匹配，不再精确相等。
        // 「差戻」标签同时收 .rejected（差戻）和 .returned（要修正）—— 被退回要修正的申请才不会消失。
        // 「承認済」标签同时收 .approved（承認済）和 .approved_partial（一部承認）。
        return sorted.filter { statuses(for: f).contains($0.status) }
    }

    /// IX-019: 把选中的标签代表状态展开成它该匹配的状态集合。
    private func statuses(for tab: ApplicationStatus) -> Set<ApplicationStatus> {
        switch tab {
        case .rejected: return [.rejected, .returned]
        case .approved: return [.approved, .approved_partial]
        default: return [tab]
        }
    }

    private let tabs: [(label: String, value: ApplicationStatus?)] = [
        ("すべて", nil),
        ("審査中", .pending),
        ("承認済", .approved),
        ("差し戻し", .rejected),
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
                    } else if let loadError {
                        // 加载失败：显错误态 + 再試行，绝不退回「申請はありません」假空态
                        // （断网时显假空态会让用户误以为自己没有任何申请 — 块C 单点兜底 2026-06-17）
                        loadErrorState(loadError)
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
        } catch APIError.unauthorized {
            // 401 = token 失效：清 authToken → RootView 全局 onChange 守卫(ios⑤ 上线缺口)自动跳登录页
            // 不再显示 mock 假数据（避免用户以为登录还有效 — 2026-05-27 codex 审查后改）
            app.authToken = nil
            apps = []
        } catch {
            // 其他错误：用 helper 给日语友好提示 + 空列表（不降级假数据）
            loadError = APIErrorPresenter.userMessage(
                for: error,
                fallback: "申請一覧の取得に失敗しました"
            )
            apps = []
        }
    }

    /// 加载失败错误态：错误文案 + 再試行（下拉刷新外再给一个显式重试入口）。
    /// 与 LostView / MusicView 的失败态同款（EmptyState + exclamationmark.triangle）。
    private func loadErrorState(_ message: String) -> some View {
        VStack(spacing: 14) {
            EmptyState(icon: "exclamationmark.triangle", title: "読み込みに失敗しました", message: message)
            Button { Task { await load() } } label: {
                Text("再試行")
                    .font(.system(size: 13, weight: .bold))
                    .foregroundStyle(.white)
                    .padding(.horizontal, 24)
                    .frame(height: 42)
                    .background { Capsule().fill(T.primary) }
            }
            .buttonStyle(.plain)
        }
        .frame(maxWidth: .infinity)
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

                // 第 2 行: 承認 chain 摘要（点列）
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
                }
                .padding(.top, 4)
                .overlay(alignment: .top) {
                    Rectangle().fill(T.hair).frame(height: 0.5)
                }
            }
        }
    }

    /// 进度横线 + 节点样式（2026-05-28 itsuki 拍板把役职名 chip 链改成无名节点）
    /// 进度比例 = approvedCount / total（无论 approve 顺序，往右推进）
    /// 任一 rejected → 进度条变红色
    private var chainDots: some View {
        let total = item.chain.count
        let approvedCount = item.chain.filter { $0.decision == .approved }.count
        let hasRejected = item.chain.contains { $0.decision == .rejected }
        let progressFrac: CGFloat = total > 0 ? CGFloat(approvedCount) / CGFloat(total) : 0
        let dotSize: CGFloat = 12

        return ZStack {
            // 横线层（底灰 + 上层进度）
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    Capsule()
                        .fill(T.hair)
                        .frame(height: 2)
                    Capsule()
                        .fill(hasRejected ? T.danger : T.ok)
                        .frame(width: geo.size.width * progressFrac, height: 2)
                }
            }
            .frame(height: 2)
            .padding(.horizontal, dotSize / 2)

            // 节点层（HStack Spacer 等距分布）
            HStack(spacing: 0) {
                ForEach(Array(item.chain.enumerated()), id: \.offset) { i, _ in
                    chainDot(item.chain[i].decision)
                    if i < total - 1 {
                        Spacer(minLength: 0)
                    }
                }
            }
        }
        .frame(height: dotSize)
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
    /// 撤回在途标志（防连点 + 按钮显示「取消中…」）
    @State private var isWithdrawing: Bool = false

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
                            // 差戻（要修正）状态：先显眼提示「修正して再提出」，再给编辑入口
                            if item.status == .returned {
                                returnedBanner
                            }
                            if item.isEditable {
                                editButton
                            }
                            // 撤回（pending / approved_partial / returned 状态可撤回，与后端 withdraw 条件一致）
                            if item.isEditable {
                                withdrawButton
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

    /// 详情加载（2026-05-27 codex 审查后改 — 拆 guard + 401 清 token + audit 失败容错 + helper）
    /// 1. 未登录 → 走 mock（Apple reviewer / 开发态看 UI）
    /// 2. 非 UUID id（mock id 如 "a1"）→ 走 mock，找不到就 toast 区分「无效 ID」
    /// 3. UUID → detail + audit 并行（audit 失败不致命）
    /// 4. catch 401 清 token 触发跳登录；其他 catch 走 helper 统一文案
    private func load() async {
        isLoading = true
        defer { isLoading = false }

        // 未登录态：用 mock（reviewer / 开发态看 UI）
        guard app.isAuthenticated else {
            if let item = StayListMock.find(id) {
                loadedItem = item
                loadedAuditLog = item.auditLog
            } else {
                app.showToast("ログインが必要です")
                router.back()
            }
            return
        }

        // 已登录但 id 不是 UUID 格式：理论上 backend 不会返这样的 id，
        // 出现 = 调用方传错（如硬编码 mock id 跳详情）。show 明确提示而不是静默 back
        guard let uuid = UUID(uuidString: id) else {
            if let item = StayListMock.find(id) {
                // 开发态：mock id 真存在就显示
                loadedItem = item
                loadedAuditLog = item.auditLog
            } else {
                app.showToast("申請が見つかりませんでした")
                router.back()
            }
            return
        }

        do {
            // detail 失败 = 致命（没详情无法显示），audit 失败 = 非致命（履历空就行）
            let detailOut = try await ApplicationsAPI.detail(id: uuid)
            var item = detailOut.toStayApplication()

            // audit 单独 try？，失败时空履历不影响 detail 显示
            let entries: [AuditLogEntry]
            do {
                let auditOut = try await ApplicationsAPI.audit(id: uuid)
                entries = auditOut.map { $0.toAuditLogEntry() }
            } catch {
                // audit 拉取失败不致命（详情仍显示），但提示用户「没拉到 ≠ 没有履历」（ios-staylist-05：原只 print 静默）
                #if DEBUG
                    print("[StayDetailView] audit 取得失败: \(error)")
                #endif
                // 不要把已加载的真实履历擦成空（下拉刷新时 audit 抖动不该让履历消失）：
                // 沿用上次拿到的履历；toast 只在「之前也没有履历可显示」时弹，刷新重试时静默。
                entries = loadedAuditLog
                if loadedAuditLog.isEmpty {
                    app.showToast("操作履歴の取得に失敗しました")
                }
            }

            item.auditLog = entries
            loadedItem = item
            loadedAuditLog = entries
        } catch APIError.unauthorized {
            // 401 = token 失效：清 authToken → RootView 全局 onChange 守卫(ios⑤)跳登录页（不显示 mock 假数据）
            app.authToken = nil
            router.back()
        } catch {
            // 其他错误：helper 统一文案
            app.showToast(APIErrorPresenter.userMessage(
                for: error,
                fallback: "申請詳細の取得に失敗しました"
            ))
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

    // MARK: - 编辑按钮（仅 isEditable 时显示）

    private var editButton: some View {
        Button {
            router.go(.stayEdit(id: item.id))
        } label: {
            HStack(spacing: 8) {
                Image(systemName: "pencil")
                    .font(.system(size: 14, weight: .semibold))
                // 差戻 状态用「修正して再提出」更贴合语义；其余可编辑状态保持「変更届を提出」
                Text(item.status == .returned ? "修正して再提出" : "変更届を提出")
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

    // MARK: - 差戻（退回要修正）提示条（仅 returned 状态显示）

    private var returnedBanner: some View {
        HStack(spacing: 8) {
            Image(systemName: "arrow.uturn.backward.circle.fill")
                .font(.system(size: 14, weight: .semibold))
                .foregroundStyle(T.danger)
            Text("この届出は差し戻されました。内容を修正して再提出してください。")
                .font(.system(size: 12.5))
                .foregroundStyle(T.ink)
                .lineSpacing(3)
            Spacer(minLength: 0)
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

    // MARK: - 撤回按钮（pending / approved_partial / returned 状态显示）

    private var withdrawButton: some View {
        Button {
            Task { await withdraw() }
        } label: {
            Text(isWithdrawing ? "取り消し中…" : "申請を取り消し")
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

    /// 撤回出寮届。沿用 OutingDetailView.withdraw 的写法：
    /// 未登录 / 非 UUID（reviewer / 开发态）→ 本地 mock 改状态；已登录 → 调 POST /applications/:id/withdraw。
    /// 并发被老师处理时后端回 409（CANNOT_WITHDRAW）→ 重拉最新状态。
    private func withdraw() async {
        guard !isWithdrawing else { return }
        isWithdrawing = true
        defer { isWithdrawing = false }

        // 未登录态 / 非 UUID id（reviewer / 开发态）→ mock 本地撤回（同 StayEditForm 的 mock 分支策略）
        guard app.isAuthenticated, let uuid = UUID(uuidString: id) else {
            StayListMock.applyWithdraw(id: id)
            if let updated = StayListMock.find(id) {
                loadedItem = updated
            }
            app.showToast("申請を取り消しました")
            return
        }

        do {
            let out = try await ApplicationsAPI.withdraw(id: uuid)
            loadedItem = out.toStayApplication()
            app.showToast("申請を取り消しました")
            // 撤回后履历会新增一条 —— 重拉 audit（失败不致命，沿用 load 的容错）
            if let auditOut = try? await ApplicationsAPI.audit(id: uuid) {
                let entries = auditOut.map { $0.toAuditLogEntry() }
                loadedItem?.auditLog = entries
                loadedAuditLog = entries
            }
        } catch let APIError.unprocessable(msg) {
            app.showToast(msg)
        } catch APIError.server(409, _) {
            app.showToast("この状態の申請は取り消せません")
            await load()
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch APIError.network {
            app.showToast("通信エラーが発生しました。電波を確認してください")
        } catch {
            app.showToast(APIErrorPresenter.userMessage(for: error, fallback: "申請の取り消しに失敗しました"))
        }
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
        if action.contains("差し戻し") { return T.danger }
        if action.contains("変更") { return T.warn }
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
                    // kind 为 .holiday（回老家）时标签用「帰省方法」；其余（外出过夜 / 回国 / 其他）离寮，用更通用的「出寮方法」
                    divider; fieldRow(label: item.kind == .holiday ? "帰省方法" : "出寮方法", value: m)
                }
                if let m = item.returnMethod {
                    divider; fieldRow(label: "帰寮方法", value: m)
                }
                if let t = item.taxiReservationTime {
                    divider; fieldRow(label: "タクシー予約", value: t)
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
                    Text("この届出には承認の手続きはありません。")
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
// 修改理由 必填（chain 重新审批时向各 approver 展示）
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

    // ── 编辑目标（init 时从 original 预填）──────────────────────────
    @State private var leaveDate: Date = .init()
    @State private var returnDate: Date = .init()
    @State private var leaveMethod: String = "JR"
    @State private var returnMethod: String = "JR"
    @State private var destination: String = ""
    @State private var amendReason: String = ""
    @State private var didInit: Bool = false

    /// 出寮方法（去程）/ 帰寮方法（回程）— 跟新建表单 StayForm 的 LEAVE / RETURN_TRANSPORTS 保持一致（itsuki 2026-06-03：出寮帰寮拆两串 + 删「飛行機」走单独段 +「教員送迎」→「教員」+ 加「寮生特別運行」）
    private let LEAVE_TRANSPORTS = [
        "西口1便", "西口2便", "金川1便", "金川2便", "寮生特別運行",
        "JR", "自家用車", "タクシー", "教員", "その他",
    ]
    private let RETURN_TRANSPORTS = [
        "西口登校便", "金川登校便", "寮生特別運行",
        "JR", "自家用車", "タクシー", "教員", "その他",
    ]

    private var needsDestination: Bool {
        original.kind == .stay || original.kind == .return
    }

    private var canSubmit: Bool {
        guard !amendReason.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
              returnDate >= leaveDate else { return false }
        // CB-04: 仅当用户主动改了出寮日（与原届不同）时，才要求新出寮日不早于今天（JST，与提交口径同用 formatYMD）。
        // 没改则保留原值合法 —— returned/rejected 旧届的原出寮日可能已过去，硬钳 minDate 会把原值顶坏（故不在 DatePicker 加下限）。
        let newLeaveYMD = formatYMD(leaveDate)
        if newLeaveYMD != original.leaveDate, newLeaveYMD < formatYMD(Date()) { return false }
        return true
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "\(original.kind.rawValue)届の変更", level: 3)
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

    /// IX-004: 修改届预填加载。原来只 StayListMock.find 纯 mock（注释写「v1.0 切回」但没做）。
    /// 现在照搬 StayDetailView 的写法：未登录 / 非 UUID → mock；已登录 → ApplicationsAPI.detail 拉真申请预填。
    private func load() async {
        isLoading = true
        defer { isLoading = false }

        // 未登录态（reviewer / 开发态看 UI）→ mock
        guard app.isAuthenticated else {
            if let item = StayListMock.find(id) {
                loadedOriginal = item
                initFields()
            } else {
                app.showToast("ログインが必要です")
                router.back()
            }
            return
        }

        // 非 UUID id（如硬编码 mock id 跳进来）→ mock 兜底
        guard let uuid = UUID(uuidString: id) else {
            if let item = StayListMock.find(id) {
                loadedOriginal = item
                initFields()
            } else {
                app.showToast("申請が見つかりませんでした")
                router.back()
            }
            return
        }

        do {
            let detailOut = try await ApplicationsAPI.detail(id: uuid)
            loadedOriginal = detailOut.toStayApplication()
            initFields()
        } catch APIError.unauthorized {
            // 401 = 令牌失效：清 authToken（didSet 删 Keychain）→ RootView 全局 onChange 守卫(ios⑤)跳登录页，不显示假数据
            app.authToken = nil
            router.back()
        } catch {
            app.showToast(APIErrorPresenter.userMessage(
                for: error, fallback: "申請の取得に失敗しました"
            ))
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
                Text("変更届を提出すると、承認の流れが最初からやり直しになります。")
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
            sectionLabel("申請者情報（変更不可）")
            Card(padding: 0) {
                VStack(spacing: 0) {
                    idRow("アカウント番号", app.displayUser.account, isFirst: true)
                    idRow("氏名", app.displayUser.name)
                    idRow("学年・組", "\(app.displayUser.grade) \(app.displayUser.classSuffix)組 \(app.displayUser.seatNo)番")
                    idRow("寮・部屋", "\(app.displayUser.dorm) \(app.displayUser.room)")
                    idRow("区分", app.displayUser.category)
                    idRow("携帯電話", app.displayUser.phone)
                }
            }
            Text("※ 個人情報の変更は寮監にご連絡ください。変更届では変更できません。")
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
                            .environment(\.timeZone, TimeZone(identifier: "Asia/Tokyo") ?? .current) // IX-034 修复④(补)：选日按 JST，跟提交格式一致
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
                            .environment(\.timeZone, TimeZone(identifier: "Asia/Tokyo") ?? .current) // IX-034 修复④(补)：选日按 JST，跟提交格式一致
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
                        chipRow(options: LEAVE_TRANSPORTS, selected: $leaveMethod)
                        if let m = original.leaveMethod, m != leaveMethod {
                            originalNote(label: "原値", text: m)
                        }
                    }
                    Divider().background(T.hair)
                    VStack(alignment: .leading, spacing: 6) {
                        Text("帰寮方法")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundStyle(T.inkSub)
                        chipRow(options: RETURN_TRANSPORTS, selected: $returnMethod)
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
                sectionLabel("変更の理由")
                Text("*").foregroundStyle(T.danger).font(.system(size: 13, weight: .heavy))
            }
            TArea(
                text: $amendReason,
                placeholder: "変更の理由を入力してください",
                rows: 4
            )
            Text("※ 各役職の先生にこの理由が表示されます。")
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
                Text("変更届を提出")
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

    /// IX-004: 修改届提交。原来只调 StayListMock.applyAmendment 纯 mock（注释写「v1.0 切回」但没做）。
    /// 现在：未登录 / 非 UUID → mock；已登录 → 构造 ApplicationUpdateBody 调 PUT /applications/:id。
    /// codex 阶段2 收口：amendReason 发后端 amend_reason（记 audit 给老师 / 履历看）；日期 / 方法只发真改过的（防误拒旧届）。
    private func submitAsync() async {
        guard !isSubmitting else { return } // codex: 防连点并发发多个 PUT（后端每次都重置承认流程 + 发邮件）
        let trimmedDest = destination.trimmingCharacters(in: .whitespaces)
        isSubmitting = true
        defer { isSubmitting = false }

        // 未登录态 / 非 UUID id（reviewer / 开发态）→ mock
        guard app.isAuthenticated, let uuid = UUID(uuidString: original.id) else {
            StayListMock.applyAmendment(
                id: original.id,
                leaveDate: formatYMD(leaveDate),
                returnDate: formatYMD(returnDate),
                leaveMethod: leaveMethod,
                returnMethod: returnMethod,
                destination: trimmedDest.isEmpty ? nil : trimmedDest,
                amendReason: amendReason
            )
            app.showToast("変更届を提出しました")
            router.back()
            return
        }

        // 生产：只把用户真改过的字段塞进 ApplicationUpdateBody（其余 nil 不发，后端只更新非 nil）。
        var body = ApplicationUpdateBody()
        // codex(IX-004): 修改理由必发 — 后端写进 audit（canSubmit 已保证非空，这里再防一道空白）。
        let trimmedReason = amendReason.trimmingCharacters(in: .whitespacesAndNewlines)
        if !trimmedReason.isEmpty { body.amend_reason = trimmedReason }
        // codex(IX-004): 日期 / 方法只发改过的。无条件发 leave_date 会触发后端「出寮日>今日」校验、
        // 误拒已过出寮日但只改帰寮日 / 方法 / 理由的旧届（尤其 returned 退回的届）。基准 = initFields 加载时的值。
        let newLeaveYMD = formatYMD(leaveDate)
        if newLeaveYMD != original.leaveDate { body.leave_date = newLeaveYMD }
        let newReturnYMD = formatYMD(returnDate)
        if newReturnYMD != (original.returnDate ?? original.leaveDate) { body.return_date = newReturnYMD }
        if leaveMethod != (original.leaveMethod ?? "JR") { body.leave_method = leaveMethod }
        if returnMethod != (original.returnMethod ?? "JR") { body.return_method = returnMethod }
        // codex: destination 加载时是从 stay_locations.first.name 读的（不是 dest_cities 行先都市名）。
        // 原来写进 dest_cities = 覆盖错字段、真正的滞在先住所反而不改。改成发 stay_locations、且改了才发。
        if needsDestination, trimmedDest != (original.destination ?? "") {
            body.stay_locations = trimmedDest.isEmpty
                ? []
                : [StayLocationBody(kind: "その他", name: trimmedDest, address: trimmedDest, phone: nil)]
        }

        do {
            _ = try await ApplicationsAPI.update(id: uuid, body: body)
            app.showToast("変更届を提出しました")
            router.back()
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch let APIError.unprocessable(msg) {
            app.showToast(msg)
        } catch let APIError.server(_, msg) {
            app.showToast(msg.isEmpty ? "修正に失敗しました" : msg)
        } catch {
            app.showToast(APIErrorPresenter.userMessage(for: error, fallback: "修正に失敗しました"))
        }
    }

    private func parseYMD(_ s: String) -> Date? {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = TimeZone(identifier: "Asia/Tokyo") // IX-034 修复④(补)：编辑流程也固定 JST，跟 formatYMD 配对
        return f.date(from: s)
    }

    private func formatYMD(_ d: Date) -> String {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = TimeZone(identifier: "Asia/Tokyo") // IX-034 修复④(补)：编辑提交的出寮日/帰寮日固定 JST，非 JST 设备不偏天
        return f.string(from: d)
    }

    private func formatYMDJa(_ d: Date) -> String {
        let f = DateFormatter()
        f.dateFormat = "yyyy 年 M 月 d 日"
        f.locale = Locale(identifier: "ja_JP")
        f.timeZone = TimeZone(identifier: "Asia/Tokyo") // IX-034 修复④(补)：原値显示按 JST，跟 parseYMD/提交一致
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
    StayDetailView(id: "a1")
        .environmentObject(RouterStore(initial: .stayDetail(id: "a1")))
        .environmentObject(AppStore())
}

#Preview("StayEdit · 変更届") {
    StayEditForm(id: "a1")
        .environmentObject(RouterStore(initial: .stayEdit(id: "a1")))
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

        // 滞在先（仅用于显示第一行）
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
            taxiReservationTime: taxi_reservation_time,
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
        // codex(IX-004): 修改届的 amend_reason 优先显示，让履历看得到「为什么改」。
        let detailText: String? = payload?["amend_reason"]?.value
            ?? payload?["reason"]?.value ?? payload?["comment"]?.value
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
        case "application.amend", "application.update": return "変更届を提出"
        case "application.approve": return "承認"
        case "application.reject": return "差し戻し"
        case "application.withdraw": return "取消"
        default: return raw
        }
    }
}
