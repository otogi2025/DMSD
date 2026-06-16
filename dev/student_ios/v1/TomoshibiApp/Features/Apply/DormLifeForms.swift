// DormLifeForms.swift
// Features · Apply — 行事企画 / 冷蔵庫購入 / 物品所持許可願

import SwiftUI

struct DormEventProposalForm: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var teamName: String = ""
    @State private var title: String = ""
    @State private var heldDate: Date = .init()
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
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "行事企画申請", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    listButton
                        .padding(.bottom, 18)

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
                                    ApplyDateField(date: $heldDate)
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
                                TArea(text: $riskSolution, placeholder: "予想される問題と対応策", rows: 5)
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
    }

    private var listButton: some View {
        Button {
            router.go(.dormEventList)
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
            _ = try await DormLifeAPI.submitEventProposal(body: body)
            app.showToast("行事企画申請を提出しました")
            router.go(.applyDone(kind: "event"))
        } catch let APIError.unprocessable(msg) {
            app.showToast(msg)
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch APIError.network {
            app.showToast("通信エラーが発生しました。電波を確認してください")
        } catch {
            app.showToast(APIErrorPresenter.userMessage(for: error, fallback: "行事企画申請の提出に失敗しました"))
        }
    }
}

struct DormEventProposalListView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var items: [DormEventProposalOut] = []
    @State private var loading: Bool = true

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "行事企画一覧", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    Button {
                        router.go(.applyForm(kind: "event"))
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
        do {
            items = try await DormLifeAPI.listMyEventProposals()
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch APIError.network {
            app.showToast("通信エラーが発生しました。電波を確認してください")
        } catch {
            app.showToast(APIErrorPresenter.userMessage(for: error, fallback: "行事企画一覧の取得に失敗しました"))
        }
        loading = false
    }
}

private struct DormEventProposalRow: View {
    let item: DormEventProposalOut

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
        Button {
            router.go(.fridgeList)
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

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "冷蔵庫購入届一覧", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    Button {
                        router.go(.applyForm(kind: "fridge"))
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
                    } else if items.isEmpty {
                        EmptyState(icon: "snowflake", title: "提出済みの届はありません")
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
        do {
            items = try await DormLifeAPI.listMyFridgePurchases()
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch APIError.network {
            app.showToast("通信エラーが発生しました。電波を確認してください")
        } catch {
            app.showToast(APIErrorPresenter.userMessage(for: error, fallback: "冷蔵庫購入届一覧の取得に失敗しました"))
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
        Button {
            router.go(.itemList)
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

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "物品所持許可願一覧", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    Button {
                        router.go(.applyForm(kind: "item"))
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
        do {
            items = try await DormLifeAPI.listMyItemPossessions()
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch APIError.network {
            app.showToast("通信エラーが発生しました。電波を確認してください")
        } catch {
            app.showToast(APIErrorPresenter.userMessage(for: error, fallback: "物品所持許可願一覧の取得に失敗しました"))
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
