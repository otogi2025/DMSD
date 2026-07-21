// DormLifeForms.swift
// Features · Apply — 行事企画 / 冷蔵庫購入 / 物品所持許可願

import SwiftUI

struct DormEventProposalForm: View {
    /// 非 nil = 再提出模式：用这个 id 拉回原企画预填，提交走 resubmit endpoint（仅 result==resubmit 的企画可重提）。
    /// nil = 新规提出模式（默认）。
    let resubmitId: String?

    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var teamName: String = ""
    @State private var title: String = ""
    @State private var heldDate: Date = ApplyFormDate.today // JST 日历锚定，避免裸 Date() 随设备时区漂
    @State private var heldTime: Date = ApplyFormDate.parseHM("19:00")
    @State private var place: String = ""
    @State private var expectedCountText: String = ""
    @State private var target: String = ""
    @State private var purpose: String = ""
    @State private var content: String = ""
    @State private var riskSolution: String = ""
    @State private var expectedCost: String = ""
    @State private var note: String = ""
    @State private var isSubmitting = false
    /// 再提出模式：预填加载中标志（拉原企画时显示 ProgressView）
    @State private var isPrefilling = false
    /// 再提出模式：已预填守卫，防 task 重入覆盖用户已改的内容
    @State private var didPrefill = false

    init(resubmitId: String? = nil) {
        self.resubmitId = resubmitId
    }

    /// 是否再提出模式
    private var isResubmit: Bool {
        resubmitId != nil
    }

    private var expectedCount: Int? {
        Int(expectedCountText.trimmingCharacters(in: .whitespacesAndNewlines))
    }

    private var canSubmit: Bool {
        !title.trimmed.isEmpty
            && !place.trimmed.isEmpty
            && expectedCount != nil
            && (expectedCount ?? -1) >= 0
            && !target.trimmed.isEmpty
            && !purpose.trimmed.isEmpty
            && !content.trimmed.isEmpty
            && !riskSolution.trimmed.isEmpty
            && !expectedCost.trimmed.isEmpty
            // 実施日時 不得早于今天（JST 日历锚定）—— 与 ApplyDateField 的 minDate 下限一致，挡住过去日期
            && heldDate >= ApplyFormDate.today
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: isResubmit ? "行事企画 再提出" : "行事企画申請", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // 再提出模式不显示「提出済み一覧」入口（它是新规模式的导航），改显差戻提示条
                    if isResubmit {
                        resubmitBanner
                            .padding(.bottom, 18)
                    } else {
                        listButton
                            .padding(.bottom, 18)
                    }

                    ApplyFormSectionLabel(n: "1", label: "企画")
                    Card(padding: 14) {
                        VStack(alignment: .leading, spacing: 12) {
                            Field(label: "起案団体名") {
                                TField(text: $teamName, placeholder: "団体名（個人の場合は空欄）")
                            }
                            Field(label: "企画名", required: true) {
                                TField(text: $title, placeholder: "企画名")
                            }
                        }
                    }
                    .padding(.bottom, 18)

                    ApplyFormSectionLabel(n: "2", label: "実施情報")
                    Card(padding: 14) {
                        VStack(alignment: .leading, spacing: 12) {
                            Field(label: "実施日時", required: true) {
                                HStack(spacing: 10) {
                                    ApplyDateField(date: $heldDate, minDate: ApplyFormDate.today)
                                    ApplyTimeField(date: $heldTime)
                                }
                            }
                            Field(label: "実施場所", required: true) {
                                TField(text: $place, placeholder: "実施場所")
                            }
                            Field(label: "参加予定人数", required: true) {
                                TField(text: $expectedCountText, placeholder: "0", keyboard: .numberPad)
                            }
                            Field(label: "参加対象", required: true) {
                                TField(text: $target, placeholder: "例：寮生全員 / 高校生 / 希望者")
                            }
                        }
                    }
                    .padding(.bottom, 18)

                    ApplyFormSectionLabel(n: "3", label: "内容")
                    Card(padding: 14) {
                        VStack(alignment: .leading, spacing: 12) {
                            Field(label: "目的", required: true) {
                                TArea(text: $purpose, placeholder: "企画の目的", rows: 4)
                            }
                            Field(label: "企画内容", hint: "スケジュールも含めて入力してください", required: true) {
                                TArea(text: $content, placeholder: "具体的な内容・スケジュール", rows: 6)
                            }
                        }
                    }
                    .padding(.bottom, 18)

                    ApplyFormSectionLabel(n: "4", label: "確認事項")
                    Card(padding: 14) {
                        VStack(alignment: .leading, spacing: 12) {
                            Field(label: "想定される問題点と対応策", required: true) {
                                TArea(text: $riskSolution, placeholder: "想定される問題点と対応策", rows: 5)
                            }
                            Field(label: "概算経費", required: true) {
                                TArea(text: $expectedCost, placeholder: "必要な費用・内訳", rows: 3)
                            }
                            Field(label: "その他") {
                                TArea(text: $note, placeholder: "補足事項", rows: 3)
                            }
                        }
                    }
                    .padding(.bottom, 22)

                    submitButton(title: isResubmit ? "再提出する" : "提出する", canSubmit: canSubmit && !isSubmitting && !isPrefilling) {
                        submit()
                    }
                    .padding(.bottom, 32)
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl)
        .task { await prefillIfNeeded() }
    }

    /// 再提出模式差戻提示条
    private var resubmitBanner: some View {
        HStack(spacing: 8) {
            Image(systemName: "arrow.uturn.backward.circle.fill")
                .font(.system(size: 14, weight: .semibold))
                .foregroundStyle(T.danger)
            Text("この企画は差し戻されました。内容を修正して再提出してください。")
                .font(.system(size: 12.5))
                .foregroundStyle(T.ink)
                .lineSpacing(3)
            Spacer(minLength: 0)
        }
        .padding(.horizontal, 14).padding(.vertical, 12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background {
            RoundedRectangle(cornerRadius: 12, style: .continuous).fill(T.dangerBg)
        }
    }

    /// 再提出模式：用 resubmitId 从 /mine 一览里找回原企画并预填各字段。
    /// 单个企画后端没有 GET-by-id 接口，沿用 listMyEventProposals + 按 id 过滤（同 StayEditForm 拉详情的思路）。
    private func prefillIfNeeded() async {
        guard isResubmit, !didPrefill, let rid = resubmitId else { return }
        // 未登录 / 非 UUID（reviewer / 开发态）—— 无真数据源，留空表单即可，不报错
        guard app.isAuthenticated, UUID(uuidString: rid) != nil else { return }

        isPrefilling = true
        defer { isPrefilling = false }
        do {
            let all = try await DormLifeAPI.listMyEventProposals()
            guard let item = all.first(where: { $0.id.uuidString.lowercased() == rid.lowercased() }) else {
                app.showToast("企画が見つかりませんでした")
                router.back()
                return
            }
            teamName = item.team_name ?? ""
            title = item.title
            // ios#20: 再提出时原企画 held_at 可能已过；钳到今天，否则 canSubmit 恒 false 且选择器不含该值
            heldDate = max(item.held_at, ApplyFormDate.today)
            heldTime = item.held_at
            place = item.place
            expectedCountText = String(item.expected_count)
            target = item.target
            purpose = item.purpose
            content = item.content
            riskSolution = item.risk_solution
            expectedCost = item.expected_cost
            note = item.note ?? ""
            didPrefill = true
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch {
            app.showToast(APIErrorPresenter.userMessage(for: error, fallback: "企画の取得に失敗しました"))
            router.back()
        }
    }

    private var listButton: some View {
        ApplyListEntryButton(title: "提出済み一覧", icon: "list.bullet.rectangle", showsChevron: true) {
            router.go(.dormEventList)
        }
    }

    private func submit() {
        guard let count = expectedCount, count >= 0 else {
            app.showToast("参加予定人数を入力してください")
            return
        }
        Task { await submitAsync(expectedCount: count) }
    }

    private func submitAsync(expectedCount: Int) async {
        // 防连点：提交在途再点直接忽略，避免重复提交
        guard !isSubmitting else { return }
        isSubmitting = true
        defer { isSubmitting = false }

        let body = DormLifeAPI.EventProposalBody(
            team_name: ApplyFormDate.nilIfBlank(teamName),
            title: title.trimmed,
            held_at: ApplyFormDate.combineDateAndTimeISO(date: heldDate, time: heldTime),
            place: place.trimmed,
            expected_count: expectedCount,
            target: target.trimmed,
            purpose: purpose.trimmed,
            content: content.trimmed,
            risk_solution: riskSolution.trimmed,
            expected_cost: expectedCost.trimmed,
            note: ApplyFormDate.nilIfBlank(note)
        )

        do {
            if let rid = resubmitId, let uuid = UUID(uuidString: rid) {
                // 再提出：仅 result==resubmit 的企画后端接受，成功后 result 回 pending（失败 409 = CANNOT_RESUBMIT）
                _ = try await DormLifeAPI.resubmitEventProposal(id: uuid, body: body)
                app.showToast("行事企画を再提出しました")
                router.go(.applyDone(kind: "event"))
            } else {
                _ = try await DormLifeAPI.submitEventProposal(body: body)
                app.showToast("行事企画申請を提出しました")
                router.go(.applyDone(kind: "event"))
            }
        } catch let APIError.unprocessable(msg) {
            app.showToast(msg)
        } catch APIError.server(409, _) {
            app.showToast("この企画は再提出できません")
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch APIError.network {
            app.showToast("通信エラーが発生しました。電波を確認してください")
        } catch {
            let fallback = isResubmit ? "行事企画の再提出に失敗しました" : "行事企画申請の提出に失敗しました"
            app.showToast(APIErrorPresenter.userMessage(for: error, fallback: fallback))
        }
    }
}

struct DormEventProposalListView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var items: [DormEventProposalOut] = []
    @State private var loading: Bool = true
    @State private var loadError: String? = nil

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "行事企画一覧", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    ApplyListEntryButton(title: "新しく提出", icon: "plus.circle") {
                        router.go(.applyForm(kind: "event"))
                    }

                    if loading {
                        VStack(spacing: 10) {
                            Skeleton(height: 74)
                            Skeleton(height: 74)
                            Skeleton(height: 74)
                        }
                    } else if let loadError {
                        listLoadErrorState(loadError) { Task { await load() } }
                    } else if items.isEmpty {
                        EmptyState(icon: "sparkles", title: "提出済みの企画はありません")
                            .frame(maxWidth: .infinity)
                    } else {
                        ForEach(items) { item in
                            DormEventProposalRow(item: item)
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
            items = try await DormLifeAPI.listMyEventProposals()
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch {
            // 网络 / 其他错误：显式错误态（区分「取得失敗」与「0件」），不再 toast 后退回假空态
            loadError = APIErrorPresenter.userMessage(for: error, fallback: "行事企画一覧の取得に失敗しました")
        }
        loading = false
    }
}

private struct DormEventProposalRow: View {
    let item: DormEventProposalOut
    @EnvironmentObject var router: RouterStore

    var body: some View {
        Card(padding: 14) {
            VStack(alignment: .leading, spacing: 10) {
                HStack(alignment: .top, spacing: 10) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(item.title)
                            .font(.system(size: 15, weight: .bold))
                            .foregroundStyle(T.ink)
                        Text(item.place)
                            .font(.system(size: 12))
                            .foregroundStyle(T.inkSub)
                    }
                    Spacer()
                    let pair = eventResultPair(item.result)
                    Pill(text: pair.label, tone: pair.tone)
                }
                HStack {
                    Text(ApplyFormDate.displayDateTime(item.held_at))
                    Spacer()
                    Text("\(item.expected_count)名")
                }
                .font(.system(size: 11, design: .monospaced))
                .foregroundStyle(T.inkMute)

                // 再提出（result == resubmit）：显示老师差戻意见 + 「再提出」入口
                if item.result == "resubmit" {
                    if let c = item.comment, !c.trimmed.isEmpty {
                        Text("先生のコメント：\(c)")
                            .font(.system(size: 12))
                            .foregroundStyle(T.ink)
                            .lineSpacing(3)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.horizontal, 10).padding(.vertical, 8)
                            .background {
                                RoundedRectangle(cornerRadius: 8, style: .continuous).fill(T.dangerBg)
                            }
                    }
                    Button {
                        router.go(.dormEventResubmit(id: item.id.uuidString.lowercased()))
                    } label: {
                        HStack(spacing: 6) {
                            Image(systemName: "arrow.uturn.up")
                                .font(.system(size: 13, weight: .semibold))
                            Text("修正して再提出")
                                .font(.system(size: 13, weight: .bold))
                            Spacer()
                            Image(systemName: "chevron.right")
                                .font(.system(size: 11, weight: .bold))
                        }
                        .foregroundStyle(T.primary)
                        .padding(.horizontal, 12).padding(.vertical, 10)
                        .background {
                            RoundedRectangle(cornerRadius: 10, style: .continuous).fill(T.pill)
                        }
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }
}

struct FridgePurchaseForm: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var contactPhone: String = "" // 预填移到 .onAppear（同 StayForm / MyInfoEditView：@State 默认值会抓全局假人 SEED.user）
    @State private var didPrefillContact = false
    @State private var contactWechat: String = ""
    @State private var product: String = "A"
    @State private var isSubmitting = false

    private var canSubmit: Bool {
        !contactPhone.trimmed.isEmpty && ["A", "B"].contains(product)
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "冷蔵庫購入届", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    listButton
                        .padding(.bottom, 18)

                    ApplyFormSectionLabel(n: "1", label: "連絡先")
                    Card(padding: 14) {
                        VStack(alignment: .leading, spacing: 12) {
                            Field(label: "携帯電話", required: true) {
                                TField(text: $contactPhone, placeholder: "090-0000-0000", keyboard: .phonePad)
                            }
                            Field(label: "WeChat") {
                                TField(text: $contactWechat, placeholder: "WeChat ID")
                            }
                        }
                    }
                    .padding(.bottom, 18)

                    ApplyFormSectionLabel(n: "2", label: "購入製品")
                    VStack(spacing: 10) {
                        RadioCard(
                            selection: $product,
                            value: "A",
                            title: "A: BESTEK 小型 1ドア 47L",
                            detail: "氷温室付き（BTMF107）約 1 万円"
                        )
                        RadioCard(
                            selection: $product,
                            value: "B",
                            title: "B: Haier 2ドア 85L",
                            detail: "直冷式（JR-N85A-W）約 2 万円。A にない小型冷凍室付き"
                        )
                    }
                    .padding(.bottom, 18)

                    ApplyFormSectionLabel(n: "3", label: "注意事項")
                    Card(padding: 14) {
                        VStack(alignment: .leading, spacing: 8) {
                            noteLine("指定された冷蔵庫のみ設置できます")
                            noteLine("他の寮生との共用は禁止です")
                            noteLine("庫内の衛生と賞味期限を管理してください")
                            noteLine("コンセント周辺を整理し、防火に注意してください")
                            noteLine("費用は原則として寮費から差し引かれます")
                        }
                    }
                    .padding(.bottom, 22)

                    submitButton(title: "提出する", canSubmit: canSubmit && !isSubmitting) {
                        submit()
                    }
                    .padding(.bottom, 32)
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl)
        .onAppear { prefillContact() }
        .onChangeCompat(of: app.currentUser?.account) { prefillContact() } // 自动登录冷启动：真实用户晚到时补填一次（Codex 6-03）
    }

    /// 预填本人联系电话：生产只在拿到真实 currentUser 后填（冷启动假人 SEED.user 不写入）；演示构建直接用 SEED。didPrefill 守卫防重复覆盖。
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

    private var listButton: some View {
        ApplyListEntryButton(title: "提出済み一覧", icon: "list.bullet.rectangle", showsChevron: true) {
            router.go(.fridgeList)
        }
    }

    private func submit() {
        let body = DormLifeAPI.FridgePurchaseBody(
            contact_phone: contactPhone.trimmed,
            contact_wechat: ApplyFormDate.nilIfBlank(contactWechat),
            product: product
        )
        Task { await submitAsync(body: body) }
    }

    private func submitAsync(body: DormLifeAPI.FridgePurchaseBody) async {
        // 防连点：提交在途再点直接忽略，避免重复提交
        guard !isSubmitting else { return }
        isSubmitting = true
        defer { isSubmitting = false }

        do {
            _ = try await DormLifeAPI.submitFridgePurchase(body: body)
            app.showToast("冷蔵庫購入届を提出しました")
            router.go(.applyDone(kind: "fridge"))
        } catch let APIError.unprocessable(msg) {
            app.showToast(msg)
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch APIError.network {
            app.showToast("通信エラーが発生しました。電波を確認してください")
        } catch {
            app.showToast(APIErrorPresenter.userMessage(for: error, fallback: "冷蔵庫購入届の提出に失敗しました"))
        }
    }
}

struct FridgePurchaseListView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var items: [FridgePurchaseRequestOut] = []
    @State private var loading: Bool = true
    @State private var loadError: String? = nil

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "冷蔵庫購入届一覧", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    ApplyListEntryButton(title: "新しく提出", icon: "plus.circle") {
                        router.go(.applyForm(kind: "fridge"))
                    }

                    if loading {
                        VStack(spacing: 10) {
                            Skeleton(height: 74)
                            Skeleton(height: 74)
                            Skeleton(height: 74)
                        }
                    } else if let loadError {
                        listLoadErrorState(loadError) { Task { await load() } }
                    } else if items.isEmpty {
                        EmptyState(icon: "snowflake", title: "提出済みの届出はありません")
                            .frame(maxWidth: .infinity)
                    } else {
                        ForEach(items) { item in
                            FridgePurchaseRow(item: item)
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
            items = try await DormLifeAPI.listMyFridgePurchases()
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch {
            // 网络 / 其他错误：显式错误态（区分「取得失敗」与「0件」），不再 toast 后退回假空态
            loadError = APIErrorPresenter.userMessage(for: error, fallback: "冷蔵庫購入届一覧の取得に失敗しました")
        }
        loading = false
    }
}

private struct FridgePurchaseRow: View {
    let item: FridgePurchaseRequestOut

    var body: some View {
        Card(padding: 14) {
            HStack(alignment: .top, spacing: 10) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("購入製品")
                        .font(.system(size: 12))
                        .foregroundStyle(T.inkSub)
                    Text(fridgeProductText(item.product))
                        .font(.system(size: 15, weight: .bold))
                        .foregroundStyle(T.ink)
                }
                Spacer()
                let pair = fridgeStatusPair(item.status)
                Pill(text: pair.label, tone: pair.tone)
            }
        }
    }
}

struct ItemPossessionForm: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var roomNo: String = "" // 预填移到 .onAppear（同上：@State 默认值抓全局假人 SEED.user.room）
    @State private var didPrefillRoom = false
    @State private var item: String = ""
    @State private var reason: String = ""
    @State private var guardianName: String = ""
    @State private var isSubmitting = false

    private var canSubmit: Bool {
        !roomNo.trimmed.isEmpty
            && !item.trimmed.isEmpty
            && !reason.trimmed.isEmpty
            && !guardianName.trimmed.isEmpty
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "物品所持許可願", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    listButton
                        .padding(.bottom, 18)

                    ApplyFormSectionLabel(n: "1", label: "申請内容")
                    Card(padding: 14) {
                        VStack(alignment: .leading, spacing: 12) {
                            Field(label: "部屋番号", required: true) {
                                TField(text: $roomNo, placeholder: "M101")
                            }
                            Field(label: "所持物品", required: true) {
                                TField(text: $item, placeholder: "所持したい物品")
                            }
                            Field(label: "所持理由", required: true) {
                                TArea(text: $reason, placeholder: "理由を入力してください", rows: 4)
                            }
                            Field(label: "保護者氏名", required: true) {
                                TField(text: $guardianName, placeholder: "保護者氏名")
                            }
                        }
                    }
                    .padding(.bottom, 18)

                    ApplyFormSectionLabel(n: "2", label: "確認事項")
                    Card(padding: 14) {
                        VStack(alignment: .leading, spacing: 8) {
                            noteLine("寮のルールを守って使用してください")
                            noteLine("自分や他人の生活を妨げないようにしてください")
                            noteLine("故障・紛失などの事故は本人の責任となります")
                        }
                    }
                    .padding(.bottom, 22)

                    submitButton(title: "提出する", canSubmit: canSubmit && !isSubmitting) {
                        submit()
                    }
                    .padding(.bottom, 32)
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl)
        .onAppear { prefillRoom() }
        .onChangeCompat(of: app.currentUser?.account) { prefillRoom() } // 自动登录冷启动：真实用户晚到时补填一次（Codex 6-03）
    }

    /// 预填房间号：生产只在拿到真实 currentUser 后填（冷启动假人 SEED.user.room 不写入）；演示构建直接用 SEED。didPrefill 守卫防重复覆盖。
    private func prefillRoom() {
        guard !didPrefillRoom else { return }
        #if DEMO
            roomNo = app.displayUser.room
            didPrefillRoom = true
        #else
            guard app.currentUser != nil else { return }
            roomNo = app.displayUser.room
            didPrefillRoom = true
        #endif
    }

    private var listButton: some View {
        ApplyListEntryButton(title: "提出済み一覧", icon: "list.bullet.rectangle", showsChevron: true) {
            router.go(.itemList)
        }
    }

    private func submit() {
        let body = DormLifeAPI.ItemPossessionBody(
            room_no: roomNo.trimmed,
            item: item.trimmed,
            reason: reason.trimmed,
            guardian_name: guardianName.trimmed
        )
        Task { await submitAsync(body: body) }
    }

    private func submitAsync(body: DormLifeAPI.ItemPossessionBody) async {
        // 防连点：提交在途再点直接忽略，避免重复提交
        guard !isSubmitting else { return }
        isSubmitting = true
        defer { isSubmitting = false }

        do {
            _ = try await DormLifeAPI.submitItemPossession(body: body)
            app.showToast("物品所持許可願を提出しました")
            router.go(.applyDone(kind: "item"))
        } catch let APIError.unprocessable(msg) {
            app.showToast(msg)
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch APIError.network {
            app.showToast("通信エラーが発生しました。電波を確認してください")
        } catch {
            app.showToast(APIErrorPresenter.userMessage(for: error, fallback: "物品所持許可願の提出に失敗しました"))
        }
    }
}

struct ItemPossessionListView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var items: [ItemPossessionRequestOut] = []
    @State private var loading: Bool = true
    @State private var loadError: String? = nil

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "物品所持許可願一覧", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    ApplyListEntryButton(title: "新しく提出", icon: "plus.circle") {
                        router.go(.applyForm(kind: "item"))
                    }

                    if loading {
                        VStack(spacing: 10) {
                            Skeleton(height: 74)
                            Skeleton(height: 74)
                            Skeleton(height: 74)
                        }
                    } else if let loadError {
                        listLoadErrorState(loadError) { Task { await load() } }
                    } else if items.isEmpty {
                        EmptyState(icon: "shippingbox", title: "提出済みの申請はありません")
                            .frame(maxWidth: .infinity)
                    } else {
                        ForEach(items) { item in
                            ItemPossessionRow(item: item)
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
            items = try await DormLifeAPI.listMyItemPossessions()
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch {
            // 网络 / 其他错误：显式错误态（区分「取得失敗」与「0件」），不再 toast 后退回假空态
            loadError = APIErrorPresenter.userMessage(for: error, fallback: "物品所持許可願一覧の取得に失敗しました")
        }
        loading = false
    }
}

private struct ItemPossessionRow: View {
    let item: ItemPossessionRequestOut

    var body: some View {
        Card(padding: 14) {
            HStack(alignment: .top, spacing: 10) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(item.item)
                        .font(.system(size: 15, weight: .bold))
                        .foregroundStyle(T.ink)
                    Text("部屋番号 \(item.room_no)")
                        .font(.system(size: 12))
                        .foregroundStyle(T.inkSub)
                }
                Spacer()
                let pair = itemPossessionStatusPair(item.status)
                Pill(text: pair.label, tone: pair.tone)
            }
        }
    }
}

/// 行事企画 / 冷蔵庫 / 物品所持 共用的一覧入口与「新しく提出」条。
private struct ApplyListEntryButton: View {
    let title: String
    let icon: String
    var showsChevron: Bool = false
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.system(size: 15, weight: .semibold))
                Text(title)
                    .font(.system(size: 13, weight: .bold))
                Spacer()
                if showsChevron {
                    Image(systemName: "chevron.right")
                        .font(.system(size: 12, weight: .bold))
                }
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
}

/// 列表加载失败错误态：错误文案 + 再試行。区分「取得失敗」与「0件」(块C 单点兜底 2026-06-17)，
/// 不退回「○○はありません」假空态（断网时显假空态会让用户误以为自己没有任何届出）。
/// 行事企画 / 冷蔵庫 / 物品所持 三个一覧共用。
private func listLoadErrorState(_ message: String, retry: @escaping () -> Void) -> some View {
    VStack(spacing: 14) {
        EmptyState(icon: "exclamationmark.triangle", title: "読み込みに失敗しました", message: message)
        Button(action: retry) {
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

private func submitButton(title: String, canSubmit: Bool, action: @escaping () -> Void) -> some View {
    Button(action: action) {
        Text(title)
            .font(.system(size: 15, weight: .bold))
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

private func noteLine(_ text: String) -> some View {
    HStack(alignment: .top, spacing: 8) {
        Image(systemName: "checkmark.circle.fill")
            .font(.system(size: 13))
            .foregroundStyle(T.primary)
            .padding(.top, 1)
        Text(text)
            .font(.system(size: 12.5))
            .foregroundStyle(T.inkSub)
            .fixedSize(horizontal: false, vertical: true)
        Spacer(minLength: 0)
    }
}

private func fridgeProductText(_ product: String) -> String {
    switch product {
    case "A": return "製品A: BESTEK 小型 1ドア 47L"
    case "B": return "製品B: Haier 2ドア 85L"
    default: return "製品\(product)"
    }
}

private func eventResultPair(_ result: String) -> (label: String, tone: Pill.Tone) {
    switch result {
    case "approved": return ("許可", .ok)
    case "approved_conditional": return ("条件付き許可", .accent)
    case "resubmit": return ("再提出", .warn)
    case "rejected": return ("却下", .danger)
    default: return ("審査中", .warn)
    }
}

private func fridgeStatusPair(_ status: String) -> (label: String, tone: Pill.Tone) {
    switch status {
    case "ordered": return ("注文済", .accent)
    case "delivered": return ("引渡済", .ok)
    case "rejected": return ("却下", .danger)
    default: return ("審査中", .warn)
    }
}

private func itemPossessionStatusPair(_ status: String) -> (label: String, tone: Pill.Tone) {
    switch status {
    case "approved": return ("許可", .ok)
    case "rejected": return ("却下", .danger)
    default: return ("審査中", .warn)
    }
}

private extension String {
    var trimmed: String {
        trimmingCharacters(in: .whitespacesAndNewlines)
    }
}

#Preview("DormEventProposalForm") {
    DormEventProposalForm()
        .environmentObject(RouterStore(initial: .applyForm(kind: "event")))
        .environmentObject(AppStore())
}

#Preview("FridgePurchaseForm") {
    FridgePurchaseForm()
        .environmentObject(RouterStore(initial: .applyForm(kind: "fridge")))
        .environmentObject(AppStore())
}

#Preview("ItemPossessionForm") {
    ItemPossessionForm()
        .environmentObject(RouterStore(initial: .applyForm(kind: "item")))
        .environmentObject(AppStore())
}
