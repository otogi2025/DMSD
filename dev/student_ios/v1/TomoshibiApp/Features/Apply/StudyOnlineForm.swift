// StudyOnlineForm.swift
// Features · Apply — 夜学習欠席届 类型 A「オンライン夜学習申請」

import QuickLook // 契約書（图片 / PDF）的 .quickLookPreview 预览（A3）
import SwiftUI

private struct OnlineScheduleSlot: Identifiable, Hashable {
    let id: UUID
    var start: Date
    var end: Date

    init(start: Date = ApplyFormDate.parseHM("19:40"),
         end: Date = ApplyFormDate.parseHM("21:00"))
    {
        id = UUID()
        self.start = start
        self.end = end
    }
}

struct StudyOnlineForm: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var reason: String = ""
    @State private var periodFrom: Date = ApplyFormDate.threeDaysLater
    @State private var periodTo: Date = ApplyFormDate.threeDaysLater
    @State private var contractRef: String = ""
    @State private var pickedContract: PickedContract?
    @State private var isSubmitting = false
    @State private var schedule: [String: [OnlineScheduleSlot]] = StudyOnlineForm.emptySchedule

    private static let emptySchedule: [String: [OnlineScheduleSlot]] = [
        "月": [], "火": [], "水": [], "木": [], "金": [],
    ]
    private let weekdays = ["月", "火", "水", "木", "金"]

    private var hasAnySlot: Bool {
        schedule.values.contains { !$0.isEmpty }
    }

    private var allSlotsValid: Bool {
        schedule.values.flatMap { $0 }.allSatisfy { $0.end > $0.start }
    }

    private var canSubmit: Bool {
        !reason.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            && periodTo >= periodFrom
            // ios#15: 开始日须 ≥ 今天+3天（与 DateField minDate / 后端 ONLINE_REQUEST_TOO_LATE 对齐；跨日开着表单时挡住过期开始日）
            && periodFrom >= ApplyFormDate.threeDaysLater
            && hasAnySlot
            && allSlotsValid
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "オンライン夜学習申請", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    listButton
                        .padding(.bottom, 18)

                    notice
                        .padding(.bottom, 18)

                    ApplyFormSectionLabel(n: "1", label: "期間")
                    Card(padding: 14) {
                        VStack(alignment: .leading, spacing: 12) {
                            Field(label: "開始日", hint: "オンライン夜学習開始の3日前までに提出してください", required: true) {
                                // JST 由 ApplyDateField 内部保证（外层 environment 会被内层覆盖，叠了也无效）
                                ApplyDateField(date: $periodFrom, minDate: ApplyFormDate.threeDaysLater)
                            }
                            Field(label: "終了日", required: true) {
                                ApplyDateField(date: $periodTo, minDate: periodFrom)
                                    // 开始日往后调时把越界的終了日钳回（minDate 只限选择器范围、不回钳已绑定值），
                                    // 否则終了日 < 開始日，canSubmit 永远 false、提交键静默置灰无提示（同 StayForm 修复）
                                    .onChangeCompat(of: periodFrom) {
                                        if periodTo < periodFrom { periodTo = periodFrom }
                                    }
                            }
                        }
                    }
                    .padding(.bottom, 18)

                    ApplyFormSectionLabel(n: "2", label: "曜日・時間")
                    Card(padding: 14) {
                        VStack(alignment: .leading, spacing: 14) {
                            ForEach(weekdays, id: \.self) { day in
                                scheduleDay(day)
                            }
                        }
                    }
                    .padding(.bottom, 18)

                    ApplyFormSectionLabel(n: "3", label: "契約書")
                    Card(padding: 14) {
                        VStack(alignment: .leading, spacing: 14) {
                            Field(label: "契約書ファイル", hint: "契約書の写真または PDF を添付してください（任意）") {
                                ContractFilePicker(picked: $pickedContract)
                            }
                            Field(label: "補足説明", hint: "契約書の内容・受講証明・リンクなど（任意）") {
                                TArea(text: $contractRef,
                                      placeholder: "契約書や受講証明の内容・リンクを入力してください",
                                      rows: 3)
                            }
                        }
                    }
                    .padding(.bottom, 18)

                    ApplyFormSectionLabel(n: "4", label: "理由")
                    Field(label: "理由", required: true) {
                        TArea(text: $reason,
                              placeholder: "オンライン夜学習を希望する理由を入力してください",
                              rows: 4)
                    }
                    .padding(.bottom, 22)

                    Button { submit() } label: {
                        Text(isSubmitting ? "提出中…" : "提出する")
                            .font(.system(size: 15, weight: .bold))
                            .foregroundStyle(.white)
                            .frame(maxWidth: .infinity, minHeight: 52)
                            .background {
                                RoundedRectangle(cornerRadius: 16, style: .continuous)
                                    .fill(canSubmit && !isSubmitting ? T.primary : T.inkFaint)
                            }
                    }
                    .buttonStyle(.plain)
                    .disabled(!canSubmit || isSubmitting)
                    .padding(.bottom, 32)
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl)
    }

    private var listButton: some View {
        Button {
            router.go(.studyOnlineList)
        } label: {
            HStack(spacing: 8) {
                Image(systemName: "list.bullet.rectangle")
                    .font(.system(size: 15, weight: .semibold))
                Text("提出済み一覧")
                    .font(.system(size: 13, weight: .bold))
                Spacer()
                Image(systemName: "chevron.right")
                    .font(.system(size: 12, weight: .bold))
            }
            .foregroundStyle(T.primary)
            .padding(.horizontal, 14)
            .padding(.vertical, 12)
            .background {
                RoundedRectangle(cornerRadius: 12, style: .continuous).fill(T.pill)
            }
        }
        .buttonStyle(.plain)
    }

    private var notice: some View {
        HStack(spacing: 8) {
            Image(systemName: "info.circle")
                .font(.system(size: 14, weight: .semibold))
            Text("オンライン夜学習開始の3日前までに提出してください")
                .font(.system(size: 12))
        }
        .foregroundStyle(T.warnDeep)
        .padding(.horizontal, 14)
        .padding(.vertical, 12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background {
            RoundedRectangle(cornerRadius: 12, style: .continuous).fill(T.warnBg)
        }
        .overlay {
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(T.warn.opacity(0.25), lineWidth: 1)
        }
    }

    private func scheduleDay(_ day: String) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text(day + "曜日")
                    .font(.system(size: 13, weight: .bold))
                    .foregroundStyle(T.ink)
                Spacer()
                Button {
                    addSlot(day: day)
                } label: {
                    Image(systemName: "plus.circle")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundStyle(T.primary)
                }
                .buttonStyle(.plain)
                .accessibilityLabel(Text(day + "曜日に時間を追加"))
            }

            let slots = schedule[day] ?? []
            if slots.isEmpty {
                Text("設定なし")
                    .font(.system(size: 12))
                    .foregroundStyle(T.inkMute)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.vertical, 4)
            } else {
                // IX-032: 用每个时段 OnlineScheduleSlot.id 当列表项身份。
                // 之前 id: \.self 用数组下标当身份，删中间一行时输入框内容 / 焦点会串到别行。
                ForEach(slots) { slot in
                    VStack(alignment: .leading, spacing: 4) {
                        HStack(spacing: 8) {
                            ApplyTimeField(date: slotStartBinding(day: day, id: slot.id))
                            Text("〜")
                                .font(.system(size: 13, weight: .semibold))
                                .foregroundStyle(T.inkSub)
                            ApplyTimeField(date: slotEndBinding(day: day, id: slot.id))
                            Button {
                                removeSlot(day: day, id: slot.id)
                            } label: {
                                Image(systemName: "minus.circle.fill")
                                    .font(.system(size: 22))
                                    .foregroundStyle(T.danger)
                            }
                            .buttonStyle(.plain)
                        }
                        // CB-01: 时刻不能像日期那样简单回钳（end=start 仍不满足 >），
                        // 故对 end<=start 的时段显示行内提示，避免提交键静默置灰让留学生不知卡在哪。
                        if slot.end <= slot.start {
                            Text("終了は開始より後の時刻にしてください")
                                .font(.system(size: 11))
                                .foregroundStyle(T.danger)
                        }
                    }
                }
            }
        }
        .padding(.bottom, day == "金" ? 0 : 10)
        .overlay(alignment: .bottom) {
            if day != "金" {
                Rectangle().fill(T.hair).frame(height: 0.5)
            }
        }
    }

    private func addSlot(day: String) {
        var slots = schedule[day] ?? []
        slots.append(OnlineScheduleSlot())
        schedule[day] = slots
    }

    // IX-032: 删除 / 更新 / 绑定全部按 id 定位，不再用数组下标，避免删中间行后串行。
    private func removeSlot(day: String, id: UUID) {
        var slots = schedule[day] ?? []
        slots.removeAll { $0.id == id }
        schedule[day] = slots
    }

    private func updateSlot(day: String, id: UUID, update: (inout OnlineScheduleSlot) -> Void) {
        var slots = schedule[day] ?? []
        guard let index = slots.firstIndex(where: { $0.id == id }) else { return }
        update(&slots[index])
        schedule[day] = slots
    }

    private func slotStartBinding(day: String, id: UUID) -> Binding<Date> {
        Binding(
            get: { (schedule[day] ?? []).first { $0.id == id }?.start ?? ApplyFormDate.parseHM("19:40") },
            set: { newValue in
                updateSlot(day: day, id: id) { $0.start = newValue }
            }
        )
    }

    private func slotEndBinding(day: String, id: UUID) -> Binding<Date> {
        Binding(
            get: { (schedule[day] ?? []).first { $0.id == id }?.end ?? ApplyFormDate.parseHM("21:00") },
            set: { newValue in
                updateSlot(day: day, id: id) { $0.end = newValue }
            }
        )
    }

    private var weeklySchedulePayload: [String: [[String: String]]] {
        var payload: [String: [[String: String]]] = [:]
        for day in weekdays {
            payload[day] = (schedule[day] ?? []).map {
                ["start": ApplyFormDate.formatHM($0.start), "end": ApplyFormDate.formatHM($0.end)]
            }
        }
        return payload
    }

    private func submit() {
        Task { await submitAsync() }
    }

    private func submitAsync() async {
        // 防连点：提交期间再点直接忽略（两步提交会放大重复申请问题）
        guard !isSubmitting else { return }
        isSubmitting = true
        defer { isSubmitting = false }

        let body = StudyAPI.OnlineRequestBody(
            reason: reason.trimmingCharacters(in: .whitespacesAndNewlines),
            period_from: ApplyFormDate.formatYMD(periodFrom),
            period_to: ApplyFormDate.formatYMD(periodTo),
            weekly_schedule: weeklySchedulePayload,
            contract_ref: ApplyFormDate.nilIfBlank(contractRef)
        )

        do {
            let out = try await StudyAPI.submitOnlineRequest(body: body)
            // 选了契約書文件 → 申请建好后第二步把文件传上去（用户感知是点一次「提出」）
            if let contract = pickedContract {
                do {
                    _ = try await StudyAPI.uploadOnlineContract(
                        requestId: out.id,
                        fileData: contract.data,
                        fileName: contract.fileName,
                        mimeType: contract.mime
                    )
                } catch APIError.unauthorized {
                    // 上传时令牌已失效（用户其实已登出）→ 清 token + 跳回登录，不进完成页
                    app.authToken = nil
                    router.replace(.login)
                    return
                } catch {
                    // 申请已成立但合同没传上 — 不回退申请，提示用户稍后从一覧重新添付
                    app.showToast("申請は受け付けましたが、契約書の添付に失敗しました。後で一覧から再度添付してください")
                    router.go(.applyDone(kind: "studyOnline"))
                    return
                }
            }
            app.showToast("オンライン夜学習申請を提出しました")
            router.go(.applyDone(kind: "studyOnline"))
        } catch let APIError.unprocessable(msg) {
            app.showToast(msg)
        } catch let APIError.server(409, msg) {
            // ios#14: 期间重叠 409 — 优先展示后端 message（勿落通用 catch 被 Presenter 吞成「サーバーエラー」）
            app.showToast(msg.isEmpty ? "同じ期間の申請が既に存在します" : msg)
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch APIError.network {
            app.showToast("通信エラーが発生しました。電波を確認してください")
        } catch {
            app.showToast(APIErrorPresenter.userMessage(for: error, fallback: "オンライン夜学習申請の提出に失敗しました"))
        }
    }
}

struct StudyOnlineRequestListView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var items: [StudyOnlineRequestOut] = []
    @State private var loading: Bool = true
    @State private var loadError: String? = nil

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "オンライン夜学習申請一覧", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    Button {
                        router.go(.applyForm(kind: "studyOnline"))
                    } label: {
                        HStack(spacing: 8) {
                            Image(systemName: "plus.circle")
                                .font(.system(size: 15, weight: .semibold))
                            Text("新しく提出")
                                .font(.system(size: 13, weight: .bold))
                            Spacer()
                        }
                        .foregroundStyle(T.primary)
                        .padding(.horizontal, 14)
                        .padding(.vertical, 12)
                        .background {
                            RoundedRectangle(cornerRadius: 12, style: .continuous).fill(T.pill)
                        }
                    }
                    .buttonStyle(.plain)

                    if loading {
                        VStack(spacing: 10) {
                            Skeleton(height: 74)
                            Skeleton(height: 74)
                            Skeleton(height: 74)
                        }
                    } else if let loadError {
                        loadErrorState(loadError)
                    } else if items.isEmpty {
                        EmptyState(icon: "laptopcomputer", title: "提出済みの申請はありません")
                            .frame(maxWidth: .infinity)
                    } else {
                        ForEach(items) { item in
                            StudyOnlineRequestRow(item: item, onChanged: { await load() })
                        }
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 4)
                .padding(.bottom, 32)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl)
        .task { await load() }
    }

    private func load() async {
        loading = true
        loadError = nil
        do {
            items = try await StudyAPI.listMyOnlineRequests()
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch {
            // 网络 / 其他错误：显式错误态（区分「取得失敗」与「0件」），不再 toast 后退回假空态
            loadError = APIErrorPresenter.userMessage(for: error, fallback: "オンライン夜学習申請一覧の取得に失敗しました")
        }
        loading = false
    }

    /// 加载失败错误态：错误文案 + 再試行（与 StayList / DormLife 一覧同款）。
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
}

private struct StudyOnlineRequestRow: View {
    let item: StudyOnlineRequestOut
    /// 上传成功后让父列表重新拉数据（这行就会从「未添付」变成「已上传」展示）
    var onChanged: () async -> Void
    @EnvironmentObject var app: AppStore

    @State private var picked: PickedContract?
    @State private var uploading = false
    @State private var downloading = false
    @State private var previewURL: URL?

    var body: some View {
        Card(padding: 14) {
            VStack(alignment: .leading, spacing: 12) {
                HStack(alignment: .top, spacing: 10) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("期間")
                            .font(.system(size: 12))
                            .foregroundStyle(T.inkSub)
                        Text("\(item.period_from) 〜 \(item.period_to)")
                            .font(.system(size: 15, weight: .bold, design: .monospaced))
                            .foregroundStyle(T.ink)
                    }
                    Spacer()
                    let pair = studyOnlineStatusPair(item.status)
                    Pill(text: pair.label, tone: pair.tone)
                }

                contractSection
            }
        }
        .quickLookPreview($previewURL)
        .onChangeCompat(of: picked) { newValue in
            // 选好文件就立刻上传（用户感知是点一下「契約書を添付」就传上去）
            if newValue != nil { Task { await upload() } }
        }
    }

    /// 契約書区：已上传 → 文件名 +「表示」(A3 下载查看)；审查中且没合同 → 补传入口 (A2)。
    @ViewBuilder
    private var contractSection: some View {
        if let name = item.contract_file_name {
            // A3：已上传 → 文件名 +「表示」（下载二进制 → QuickLook 预览图片 / PDF）
            Rectangle().fill(T.hair).frame(height: 0.5)
            HStack(spacing: 8) {
                Image(systemName: item.contract_mime == "application/pdf" ? "doc.fill" : "photo.fill")
                    .font(.system(size: 15))
                    .foregroundStyle(T.primary)
                Text(name)
                    .font(.system(size: 12))
                    .foregroundStyle(T.inkSub)
                    .lineLimit(1)
                Spacer()
                Button {
                    Task { await showContract() }
                } label: {
                    Text(downloading ? "読み込み中…" : "表示")
                        .font(.system(size: 12, weight: .bold))
                        .foregroundStyle(downloading ? T.inkMute : T.primary)
                }
                .buttonStyle(.plain)
                .disabled(downloading)
            }
        } else if item.status == "pending" {
            // A2：审查中 + 没合同（提交时第二步上传失败 / 当时没传）→ 给补传入口
            Rectangle().fill(T.hair).frame(height: 0.5)
            VStack(alignment: .leading, spacing: 6) {
                Text("契約書が未添付です")
                    .font(.system(size: 12))
                    .foregroundStyle(T.inkSub)
                if uploading {
                    HStack(spacing: 8) {
                        ProgressView().controlSize(.small)
                        Text("アップロード中…")
                            .font(.system(size: 12))
                            .foregroundStyle(T.inkSub)
                    }
                } else {
                    ContractFilePicker(picked: $picked)
                }
            }
        }
    }

    /// A2：把选好的契約書传到这条申请（仅 pending 状态后端才接受）。
    private func upload() async {
        guard let contract = picked else { return }
        uploading = true
        defer { uploading = false }
        do {
            _ = try await StudyAPI.uploadOnlineContract(
                requestId: item.id,
                fileData: contract.data,
                fileName: contract.fileName,
                mimeType: contract.mime
            )
            app.showToast("契約書を添付しました")
            picked = nil
            await onChanged()
        } catch let APIError.unprocessable(msg) {
            // 类型不符 / 超大 / 已审查不能改
            app.showToast(msg)
            picked = nil
        } catch APIError.unauthorized {
            // 与其它错误分支一致：清 picked，便于登录后重选同一文件再传
            app.authToken = nil
            picked = nil
        } catch APIError.network {
            app.showToast("通信エラーが発生しました。電波を確認してください")
            picked = nil
        } catch {
            app.showToast(APIErrorPresenter.userMessage(for: error, fallback: "契約書の添付に失敗しました"))
            picked = nil
        }
    }

    /// A3：下载契約書文件 → 写临时文件 → QuickLook 预览。
    private func showContract() async {
        downloading = true
        defer { downloading = false }
        do {
            let data = try await StudyAPI.downloadOnlineContract(requestId: item.id)
            let ext = item.contract_mime == "application/pdf" ? "pdf" : "jpg"
            let tmp = FileManager.default.temporaryDirectory
                .appendingPathComponent("contract_\(item.id.uuidString).\(ext)")
            try data.write(to: tmp, options: .atomic)
            previewURL = tmp
        } catch APIError.unauthorized {
            app.authToken = nil
        } catch APIError.network {
            app.showToast("通信エラーが発生しました。電波を確認してください")
        } catch {
            app.showToast("契約書の取得に失敗しました")
        }
    }
}

private func studyOnlineStatusPair(_ status: String) -> (label: String, tone: Pill.Tone) {
    switch status {
    case "approved": return ("許可", .ok)
    case "rejected": return ("却下", .danger)
    case "revoked": return ("取消済み", .neutral)
    default: return ("審査中", .warn)
    }
}

#Preview("StudyOnlineForm") {
    StudyOnlineForm()
        .environmentObject(RouterStore(initial: .applyForm(kind: "studyOnline")))
        .environmentObject(AppStore())
}
