// StudyOnlineForm.swift
// Features · Apply — 学習欠席届 类型 A「オンライン学習申請」

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
            && hasAnySlot
            && allSlotsValid
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "オンライン学習申請", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    listButton
                        .padding(.bottom, 18)

                    notice
                        .padding(.bottom, 18)

                    ApplyFormSectionLabel(n: "1", label: "期間")
                    Card(padding: 14) {
                        VStack(alignment: .leading, spacing: 12) {
                            Field(label: "開始日", hint: "オンライン学習開始の 3 日前までに提出してください", required: true) {
                                ApplyDateField(date: $periodFrom, minDate: ApplyFormDate.threeDaysLater)
                                    .environment(\.timeZone, TimeZone(identifier: "Asia/Tokyo") ?? .current) // 选日按 JST，跟 formatYMD 提交口径一致（非 JST 设备不偏天）
                            }
                            Field(label: "終了日", required: true) {
                                ApplyDateField(date: $periodTo, minDate: periodFrom)
                                    .environment(\.timeZone, TimeZone(identifier: "Asia/Tokyo") ?? .current) // 选日按 JST，跟 formatYMD 提交口径一致
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
                    Field(label: "契約書・受講証明の説明", hint: "オンライン授業の契約書、申込完了画面、URL などを入力してください。ファイル添付は後続対応です。") {
                        TArea(text: $contractRef,
                              placeholder: "契約書や受講証明の内容・リンクを入力",
                              rows: 4)
                    }
                    .padding(.bottom, 18)

                    ApplyFormSectionLabel(n: "4", label: "理由")
                    Field(label: "理由", required: true) {
                        TArea(text: $reason,
                              placeholder: "オンライン学習を希望する理由を入力してください",
                              rows: 4)
                    }
                    .padding(.bottom, 22)

                    Button { submit() } label: {
                        Text("提出する")
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
            Text("オンライン学習開始の 3 日前までに提出してください")
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
                Text("申請なし")
                    .font(.system(size: 12))
                    .foregroundStyle(T.inkMute)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.vertical, 4)
            } else {
                // IX-032: 用每个时段 OnlineScheduleSlot.id 当列表项身份。
                // 之前 id: \.self 用数组下标当身份，删中间一行时输入框内容 / 焦点会串到别行。
                ForEach(slots) { slot in
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
        let body = StudyAPI.OnlineRequestBody(
            reason: reason,
            period_from: ApplyFormDate.formatYMD(periodFrom),
            period_to: ApplyFormDate.formatYMD(periodTo),
            weekly_schedule: weeklySchedulePayload,
            contract_ref: ApplyFormDate.nilIfBlank(contractRef)
        )

        do {
            _ = try await StudyAPI.submitOnlineRequest(body: body)
            app.showToast("オンライン学習申請を提出しました")
            router.go(.applyDone(kind: "studyOnline"))
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

struct StudyOnlineRequestListView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var items: [StudyOnlineRequestOut] = []
    @State private var loading: Bool = true

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "オンライン学習申請一覧", level: 2)
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
                    } else if items.isEmpty {
                        EmptyState(icon: "laptopcomputer", title: "提出済みの申請はありません")
                            .frame(maxWidth: .infinity)
                    } else {
                        ForEach(items) { item in
                            StudyOnlineRequestRow(item: item)
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
            items = try await StudyAPI.listMyOnlineRequests()
        } catch APIError.unauthorized {
            app.authToken = nil
            router.replace(.login)
        } catch APIError.network {
            app.showToast("通信エラーが発生しました。電波を確認してください")
        } catch {
            app.showToast(error.localizedDescription)
        }
        loading = false
    }
}

private struct StudyOnlineRequestRow: View {
    let item: StudyOnlineRequestOut

    var body: some View {
        Card(padding: 14) {
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
        }
    }
}

private func studyOnlineStatusPair(_ status: String) -> (label: String, tone: Pill.Tone) {
    switch status {
    case "approved": return ("許可", .ok)
    case "rejected": return ("却下", .danger)
    case "revoked": return ("取消", .neutral)
    default: return ("審査中", .warn)
    }
}

private extension Array {
    subscript(safe index: Index) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}

#Preview("StudyOnlineForm") {
    StudyOnlineForm()
        .environmentObject(RouterStore(initial: .applyForm(kind: "studyOnline")))
        .environmentObject(AppStore())
}
