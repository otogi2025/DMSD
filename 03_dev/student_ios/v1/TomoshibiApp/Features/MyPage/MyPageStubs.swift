// MyPageStubs.swift · MyPage feature v2 · Agent E 产出
// 对等 phaseB_src e38fcebf__LogoutSheet.js (12 views + LogoutSheet)
// 遵循 REMOTE_AGENT_GUIDE §1 Fidelity 铁律：逐字照抄文字 / 严格对照数值 / 颜色 hex 精确
//
// Views:
//   1. MyLandingView (L1)
//   2. MyInfoView (L2)
//   3. MyRollcallView (L2)
//   4. MyRollcallDetailView (L2)
//   5. MyPointsView (L2)
//   6. MyPointsChartView (L2 / L3)
//   7. MyDisciplineView (L2)
//   8. MyHealthView (L2)
//   9. MyCleanView (L2)
//   10. MyPackagesView (L2)
//   11. MySettingsView (L2)
//   12. MyAboutView (L2)
//   13. LogoutSheet
//
// 重要 data hooks:
//   - SEED.user: 4.5 点 / 男寮 M101 / リュウ イヒ / 19 歳（Web Round 3 口径）
//   - SEED.points: 7 件
//   - SEED.rollcall: 34 件
//   - SEED.health: 2 件
//   - SEED.cleaning: 2 件
//   - SEED.packages: 4 件

import SwiftUI

// MARK: - Helpers

/// MyLanding 顶部 2-col grid block · 对等 JSX blocks map
private struct MyLandingGridBlock: Identifiable {
    let id = UUID()
    let key: String           // "info" / "rollcall" / ...
    let label: String
    let icon: String          // emoji
    let badge: String?
    let route: Route
}

/// Emoji icon wrapper · 24pt
private struct EmojiIcon: View {
    let emoji: String
    var size: CGFloat = 24
    var body: some View {
        Text(emoji).font(.system(size: size))
    }
}

// MARK: - 1. MyLandingView (L1)

struct MyLandingView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    /// 对等 JSX blocks (8 件 · 2-col grid)
    private var blocks: [MyLandingGridBlock] {
        // JSX badge: points = 4.0 → 我们 SEED 是 4.5 → 动态取 SEED.user.points
        let pointsBadge = String(format: "%.1f", SEED.user.points)
        let pendingPackages = SEED.packages.filter { $0.status == "待領" }.count
        let packagesBadge = pendingPackages > 0 ? "\(pendingPackages)" : nil

        return [
            .init(key: "info", label: "個人情報", icon: "👤", badge: nil, route: .myInfo),
            .init(key: "rollcall", label: "点呼履歴", icon: "📋", badge: nil, route: .myRollcall),
            .init(key: "points", label: "減点明細", icon: "📉", badge: pointsBadge, route: .myPoints),
            .init(key: "discipline", label: "処分履歴", icon: "⚖️", badge: nil, route: .myDiscipline),
            .init(key: "health", label: "体調報告履歴", icon: "🤒", badge: nil, route: .myHealth),
            // 2026-04-30 会话 C 修正: 「申請履歴」は届の履歴 → .stayList へ
            // （旧 .apply は申し込み tab root = 新規作成導線、履歴閲覧用ではない）
            .init(key: "apps", label: "申請履歴", icon: "📄", badge: nil, route: .stayList),
            .init(key: "clean", label: "掃除提出履歴", icon: "🧹", badge: nil, route: .myClean),
            .init(key: "packages", label: "荷物受取履歴", icon: "📦", badge: packagesBadge, route: .myPackages),
        ]
    }

    var body: some View {
        VStack(spacing: 0) {
            // PageHeader(level: 1) 左上 Home icon → router.replace(.home)
            PageHeader(title: "マイページ", level: 1)

            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // Profile card
                    profileSection
                        .padding(.horizontal, 16)
                        .padding(.top, 6)
                        .padding(.bottom, 12)

                    // 2-col grid
                    gridSection
                        .padding(.horizontal, 16)
                        .padding(.top, 4)
                        .padding(.bottom, 12)

                    // Settings list
                    settingsSection
                        .padding(.horizontal, 16)
                        .padding(.top, 4)
                        .padding(.bottom, 16)
                }
            }
        }
        .background(T.pearl.ignoresSafeArea())
    }

    // MARK: Profile card

    private var profileSection: some View {
        Card(padding: 20) {
            VStack(alignment: .leading, spacing: 14) {
                HStack(alignment: .center, spacing: 14) {
                    Avatar(letter: SEED.user.avatar, size: 64)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(SEED.user.name)
                            .font(.system(size: 20, weight: .heavy))
                            .kerning(-0.2)
                            .foregroundStyle(T.ink)
                        HStack(spacing: 4) {
                            Text("アカウント番号 ")
                                .font(.system(size: 12))
                                .foregroundStyle(T.inkMute)
                            Text(SEED.user.account)
                                .font(.system(size: 12, weight: .bold))
                                .foregroundStyle(T.ink)
                                .monospaced()
                        }
                        .padding(.top, 2)
                    }
                    Spacer(minLength: 0)
                }
                HStack(spacing: 6) {
                    Pill(text: "\(SEED.user.dorm) \(SEED.user.room)", tone: .accent)
                    Pill(text: SEED.user.category, tone: .neutral)
                }
            }
        }
    }

    // MARK: 2-col grid

    private var gridSection: some View {
        LazyVGrid(columns: [GridItem(.flexible(), spacing: 10), GridItem(.flexible(), spacing: 10)], spacing: 10) {
            ForEach(blocks) { b in
                gridCell(b)
            }
        }
    }

    private func gridCell(_ b: MyLandingGridBlock) -> some View {
        Button {
            router.go(b.route)
        } label: {
            ZStack(alignment: .topTrailing) {
                VStack(alignment: .leading, spacing: 0) {
                    EmojiIcon(emoji: b.icon, size: 24)
                    Spacer(minLength: 0)
                    Text(b.label)
                        .font(.system(size: 13.5, weight: .bold))
                        .foregroundStyle(T.ink)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .frame(minHeight: 88, alignment: .topLeading)
                .padding(.horizontal, 14)
                .padding(.vertical, 14)
                .background {
                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                        .fill(T.paper)
                        .shadow(color: T.ink.opacity(0.04), radius: 2, x: 0, y: 1)
                        .shadow(color: T.ink.opacity(0.05), radius: 14, x: 0, y: 4)
                }
                .overlay {
                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                        .stroke(T.hair, lineWidth: 0.5)
                }

                if let badge = b.badge {
                    Text(badge)
                        .font(.system(size: 11, weight: .bold))
                        .monospaced()
                        .padding(.horizontal, 8)
                        .padding(.vertical, 2)
                        .background {
                            Capsule()
                                .fill(b.key == "points" ? T.warnBg : T.dangerBg)
                        }
                        .foregroundStyle(b.key == "points" ? T.warnDeep : T.danger)
                        .padding(.top, 12)
                        .padding(.trailing, 12)
                }
            }
        }
        .buttonStyle(.plain)
    }

    // MARK: Settings list

    private var settingsSection: some View {
        Card(padding: 0) {
            VStack(spacing: 0) {
                // 2026-04-30 会话 C 追加: V1 リファレンス系（老師 38 条 #8 / #9）
                settingsRow(label: "行事予定", chev: true, danger: false) {
                    router.go(.schedule)
                }
                Divider().background(T.hair).padding(.leading, 0)
                settingsRow(label: "特別運航便", chev: true, danger: false) {
                    router.go(.busList)
                }
                Divider().background(T.hair).padding(.leading, 0)
                settingsRow(label: "通知設定", chev: true, danger: false) {
                    router.go(.mySettings)
                }
                Divider().background(T.hair).padding(.leading, 0)
                settingsRow(label: "Tomoshibi について", chev: true, danger: false) {
                    router.go(.myAbout)
                }
                Divider().background(T.hair).padding(.leading, 0)
                settingsRow(label: "ログアウト", chev: false, danger: true) {
                    app.openSheet(.logout)
                }
            }
        }
    }

    private func settingsRow(label: String, chev: Bool, danger: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack {
                Text(label)
                    .font(.system(size: 14.5, weight: .medium))
                    .foregroundStyle(danger ? T.danger : T.ink)
                Spacer()
                if chev {
                    Ic.chevR(16)
                        .foregroundStyle(T.inkMute)
                }
            }
            .padding(.horizontal, 18)
            .padding(.vertical, 16)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }
}

#Preview("MyLanding") {
    MyLandingView()
        .environmentObject(RouterStore(initial: .my))
        .environmentObject(AppStore())
}

// MARK: - 2. MyInfoView (L2)

struct MyInfoView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    private var rows: [(String, String)] {
        let u = SEED.user
        return [
            ("氏名", u.name),
            ("フリガナ", u.nameKana),
            ("生年月日", "\(u.birth) (\(u.age) 歳)"),
            ("性別", u.gender),
            ("アカウント番号", u.account),
            ("学年・組・番号", "\(u.grade) \(u.classSuffix)組 \(u.seatNo)番"),
            ("寮・部屋", "\(u.dorm) \(u.room)"),
            ("区分", u.category),
            ("メール", u.email),
            ("電話", u.phone),
        ]
    }

    private static let logFormatter: DateFormatter = {
        let f = DateFormatter()
        f.locale = Locale(identifier: "ja_JP")
        f.dateFormat = "yyyy-MM-dd HH:mm"
        return f
    }()

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "個人情報", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    Card(padding: 0) {
                        VStack(spacing: 0) {
                            ForEach(Array(rows.enumerated()), id: \.offset) { idx, pair in
                                if idx > 0 {
                                    Divider().background(T.hair)
                                }
                                HStack(alignment: .top, spacing: 0) {
                                    Text(pair.0)
                                        .font(.system(size: 13))
                                        .foregroundStyle(T.inkSub)
                                        .frame(width: 120, alignment: .leading)
                                    Text(pair.1)
                                        .font(.system(size: 13.5, weight: .medium))
                                        .foregroundStyle(T.ink)
                                        .frame(maxWidth: .infinity, alignment: .leading)
                                }
                                .padding(.horizontal, 16)
                                .padding(.vertical, 14)
                            }
                        }
                    }

                    // 編集ボタン（学年・組・番号・部屋番号）
                    Button {
                        router.go(.myInfoEdit)
                    } label: {
                        HStack(spacing: 6) {
                            Text("✎")
                            Text("学年・組・番号・部屋を編集")
                        }
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundStyle(T.primary)
                        .frame(maxWidth: .infinity)
                        .frame(height: 44)
                        .background {
                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                .fill(T.primary.opacity(0.08))
                        }
                    }
                    .buttonStyle(.plain)
                    .padding(.top, 12)

                    // 変更履歴
                    if !app.changeLog.isEmpty {
                        Text("変更履歴")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundStyle(T.inkSub)
                            .padding(.top, 20)
                            .padding(.bottom, 6)

                        Card(padding: 0) {
                            VStack(spacing: 0) {
                                ForEach(Array(app.changeLog.enumerated()), id: \.element.id) { idx, entry in
                                    if idx > 0 {
                                        Divider().background(T.hair)
                                    }
                                    VStack(alignment: .leading, spacing: 4) {
                                        HStack(spacing: 6) {
                                            Text(entry.label)
                                                .font(.system(size: 12, weight: .semibold))
                                                .foregroundStyle(T.primary)
                                            Spacer()
                                            Text(Self.logFormatter.string(from: entry.at))
                                                .font(.system(size: 11))
                                                .foregroundStyle(T.inkSub)
                                        }
                                        HStack(spacing: 6) {
                                            Text(entry.before)
                                                .font(.system(size: 13))
                                                .foregroundStyle(T.inkSub)
                                                .strikethrough()
                                            Text("→")
                                                .font(.system(size: 13))
                                                .foregroundStyle(T.inkSub)
                                            Text(entry.after)
                                                .font(.system(size: 13, weight: .semibold))
                                                .foregroundStyle(T.ink)
                                        }
                                    }
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                    .padding(.horizontal, 16)
                                    .padding(.vertical, 12)
                                }
                            }
                        }
                    }

                    // Info box
                    HStack(alignment: .top, spacing: 4) {
                        Text("ℹ")
                        Text(" 氏名・生年月日・性別・メール・電話などの変更は、寮監にご連絡ください。")
                    }
                    .font(.system(size: 12.5))
                    .foregroundStyle(T.primaryDk)
                    .lineSpacing(4)
                    .padding(.horizontal, 14)
                    .padding(.vertical, 12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background {
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .fill(T.primary.opacity(0.04))
                    }
                    .overlay {
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .stroke(T.primary.opacity(0.13), lineWidth: 1)
                    }
                    .padding(.top, 16)
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .background(T.pearl.ignoresSafeArea())
    }
}

// MARK: - MyInfoEditView (L3) — 学年 / 組 / 番号 / 部屋 編集

struct MyInfoEditView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @State private var grade: String = SEED.user.grade
    @State private var classSuffix: String = SEED.user.classSuffix
    @State private var seatNoStr: String = "\(SEED.user.seatNo)"
    @State private var room: String = {
        var s = SEED.user.room
        if let first = s.first, first == "M" || first == "W" { s.removeFirst() }
        return s
    }()

    private let grades = ["中1", "中2", "中3", "高1", "高2", "高3"]

    private var gradeCode: String {
        switch grade {
        case "中1": return "01"; case "中2": return "02"; case "中3": return "03"
        case "高1": return "04"; case "高2": return "05"; case "高3": return "06"
        default: return "00"
        }
    }
    private var classCode: String { classSuffix == "A" ? "01" : "02" }
    private var computedAccount: String {
        let n = max(0, min(99, Int(seatNoStr) ?? 0))
        return gradeCode + classCode + String(format: "%02d", n)
    }

    private var canSave: Bool {
        (Int(seatNoStr) ?? 0) > 0
            && !room.trimmingCharacters(in: .whitespaces).isEmpty
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "個人情報編集", level: 3)
            ScrollView {
                VStack(spacing: 18) {
                    Field(label: "学年", required: true) {
                        HStack(spacing: 6) {
                            ForEach(grades, id: \.self) { g in
                                Button { grade = g } label: {
                                    Text(g)
                                        .font(.system(size: 13, weight: grade == g ? .bold : .medium))
                                        .foregroundStyle(grade == g ? Color.white : T.ink)
                                        .frame(maxWidth: .infinity)
                                        .frame(height: 36)
                                        .background {
                                            RoundedRectangle(cornerRadius: 10, style: .continuous)
                                                .fill(grade == g ? T.primary : T.pearl)
                                        }
                                        .overlay {
                                            RoundedRectangle(cornerRadius: 10, style: .continuous)
                                                .stroke(grade == g ? T.primary : T.hair, lineWidth: 1)
                                        }
                                        .contentShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    }

                    Field(label: "組", required: true) {
                        HStack(spacing: 8) {
                            ForEach(["A", "B"], id: \.self) { v in
                                let sel = classSuffix == v
                                Button { classSuffix = v } label: {
                                    Text("\(v)組")
                                        .font(.system(size: 14, weight: sel ? .bold : .medium))
                                        .foregroundStyle(sel ? T.primary : T.ink)
                                        .frame(maxWidth: .infinity)
                                        .frame(height: 42)
                                        .background {
                                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                                .fill(sel ? T.primary.opacity(0.06) : T.pearl)
                                        }
                                        .overlay {
                                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                                .stroke(sel ? T.primary : T.hair, lineWidth: sel ? 1.5 : 1)
                                        }
                                        .contentShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    }

                    Field(label: "出席番号", required: true) {
                        TField(text: $seatNoStr, placeholder: "18", keyboard: .numberPad)
                    }

                    Field(
                        label: "部屋番号",
                        hint: "例：101 / 12B · 男寮 M / 女寮 W は性別から自動付与",
                        required: true
                    ) {
                        TField(text: $room, placeholder: "101")
                    }
                    .onChange(of: room) { _, newVal in
                        let filtered = newVal.filter { $0.isLetter || $0.isNumber }
                            .uppercased()
                        room = String(filtered.prefix(4))
                    }

                    // アカウント番号 プレビュー
                    HStack {
                        Text("アカウント番号（自動）")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundStyle(T.inkSub)
                        Spacer()
                        Text(computedAccount)
                            .font(.system(size: 22, weight: .bold, design: .monospaced))
                            .foregroundStyle(T.primary)
                            .kerning(2)
                    }
                    .padding(.horizontal, 14).padding(.vertical, 10)
                    .background {
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .fill(T.primary.opacity(0.06))
                    }
                    .overlay {
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .stroke(T.primary.opacity(0.15), lineWidth: 1)
                    }
                }
                .padding(.horizontal, 24)
                .padding(.top, 12)
                .padding(.bottom, 24)
            }

            VStack(spacing: 0) {
                Rectangle().fill(T.hair).frame(height: 0.5)
                PrimaryButton(title: "保存する", enabled: canSave) {
                    saveAndLog()
                }
                .padding(.horizontal, 24)
                .padding(.top, 16)
                .padding(.bottom, 32)
            }
            .background(T.paper)
        }
        .background(T.paper.ignoresSafeArea())
    }

    private func saveAndLog() {
        let u0 = SEED.user
        let newSeat = Int(seatNoStr) ?? u0.seatNo
        // 性別から M/W プレフィックスを自動付与
        let prefix = (u0.gender == "男") ? "M" : "W"
        let newRoom = prefix + room

        app.appendChange(field: "grade",       label: "学年",     before: u0.grade,              after: grade)
        app.appendChange(field: "classSuffix", label: "組",       before: u0.classSuffix,        after: classSuffix)
        app.appendChange(field: "seatNo",      label: "出席番号", before: "\(u0.seatNo)",         after: "\(newSeat)")
        app.appendChange(field: "room",        label: "部屋番号", before: u0.room,                after: newRoom)
        app.appendChange(field: "account",     label: "アカウント番号", before: u0.account,        after: computedAccount)

        SEED.user.grade = grade
        SEED.user.classSuffix = classSuffix
        SEED.user.seatNo = newSeat
        SEED.user.room = newRoom
        SEED.user.account = computedAccount

        app.showToast("保存しました")
        router.back()
    }
}

#Preview("MyInfo") {
    MyInfoView()
        .environmentObject(RouterStore(initial: .myInfo))
        .environmentObject(AppStore())
}

// MARK: - 3. MyRollcallView (L2)

struct MyRollcallView: View {
    @EnvironmentObject var router: RouterStore
    @State private var selectedMonth: String = "4月"

    private let monthOptions: [String] = ["4月", "3月", "2月"]

    /// 按 date group (preserve original order from SEED)
    private var grouped: [(date: String, items: [RollcallEntry])] {
        var seen: [String] = []
        var map: [String: [RollcallEntry]] = [:]
        for r in SEED.rollcall {
            if map[r.date] == nil {
                seen.append(r.date)
                map[r.date] = []
            }
            map[r.date]?.append(r)
        }
        return seen.map { (date: $0, items: map[$0] ?? []) }
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "点呼履歴", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // Month filter pills
                    HStack(spacing: 6) {
                        ForEach(monthOptions, id: \.self) { m in
                            Button {
                                selectedMonth = m
                            } label: {
                                Text(m)
                                    .font(.system(size: 12, weight: .semibold))
                                    .padding(.horizontal, 14)
                                    .padding(.vertical, 6)
                                    .foregroundStyle(selectedMonth == m ? Color.white : T.primary)
                                    .background {
                                        Capsule()
                                            .fill(selectedMonth == m ? T.primary : T.pill)
                                    }
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.bottom, 14)

                    // Grouped list
                    ForEach(grouped, id: \.date) { grp in
                        VStack(alignment: .leading, spacing: 6) {
                            Text(grp.date)
                                .font(.system(size: 11, weight: .semibold))
                                .monospaced()
                                .foregroundStyle(T.inkMute)
                                .padding(.horizontal, 4)

                            Card(padding: 0) {
                                VStack(spacing: 0) {
                                    ForEach(Array(grp.items.enumerated()), id: \.offset) { idx, r in
                                        if idx > 0 {
                                            Divider().background(T.hair)
                                        }
                                        Button {
                                            router.go(.myRollcallDetail)
                                        } label: {
                                            rollcallRow(r)
                                        }
                                        .buttonStyle(.plain)
                                    }
                                }
                            }
                        }
                        .padding(.bottom, 14)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .background(T.pearl.ignoresSafeArea())
    }

    private func rollcallRow(_ r: RollcallEntry) -> some View {
        HStack(spacing: 12) {
            Text(r.session)
                .font(.system(size: 13, weight: .semibold))
                .foregroundStyle(T.ink)
                .frame(width: 60, alignment: .leading)
            Pill(text: r.state, tone: pillTone(r.state))
            Spacer()
            Text(r.method)
                .font(.system(size: 11))
                .monospaced()
                .foregroundStyle(T.inkMute)
            Ic.chevR(14)
                .foregroundStyle(T.inkFaint)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .contentShape(Rectangle())
    }

    private func pillTone(_ state: String) -> Pill.Tone {
        switch state {
        case "時間内": return .ok
        case "遅刻": return .warn
        default: return .danger
        }
    }
}

#Preview("MyRollcall") {
    MyRollcallView()
        .environmentObject(RouterStore(initial: .myRollcall))
        .environmentObject(AppStore())
}

// MARK: - 4. MyRollcallDetailView (L2)

struct MyRollcallDetailView: View {
    private let kvPairs: [(String, String)] = [
        ("状態", "遅刻 0.5 点"),
        ("方式", "NFC"),
        ("開始時刻", "07:00:00"),
        ("締切時刻", "07:10:00"),
        ("チェックイン", "07:12:34"),
        ("遅れ", "+2分34秒"),
    ]

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "点呼セッション詳細", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    Card(padding: 18) {
                        VStack(alignment: .leading, spacing: 0) {
                            Text("2026-04-12 朝点呼")
                                .font(.system(size: 16, weight: .bold))
                                .monospaced()
                                .foregroundStyle(T.primary)
                                .padding(.bottom, 2)
                            Text("セッション ID: RC-20260412-AM")
                                .font(.system(size: 12))
                                .foregroundStyle(T.inkMute)
                                .padding(.bottom, 14)
                            LazyVGrid(
                                columns: [GridItem(.flexible(), spacing: 12), GridItem(.flexible(), spacing: 12)],
                                alignment: .leading,
                                spacing: 12
                            ) {
                                ForEach(Array(kvPairs.enumerated()), id: \.offset) { _, pair in
                                    VStack(alignment: .leading, spacing: 3) {
                                        Text(pair.0)
                                            .font(.system(size: 11))
                                            .foregroundStyle(T.inkMute)
                                        Text(pair.1)
                                            .font(.system(size: 14, weight: .semibold))
                                            .foregroundStyle(T.ink)
                                    }
                                }
                            }
                        }
                    }

                    // Info box
                    Text("ℹ 改判はされていません")
                        .font(.system(size: 12))
                        .foregroundStyle(T.primaryDk)
                        .padding(.horizontal, 14)
                        .padding(.vertical, 12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background {
                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                .fill(T.primary.opacity(0.04))
                        }
                        .padding(.top, 14)
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .background(T.pearl.ignoresSafeArea())
    }
}

#Preview("MyRollcallDetail") {
    MyRollcallDetailView()
        .environmentObject(RouterStore(initial: .myRollcallDetail))
        .environmentObject(AppStore())
}

// MARK: - 5. MyPointsView (L2)

struct MyPointsView: View {
    @EnvironmentObject var router: RouterStore

    /// 今月合計 · 动态从 SEED.user.points (目前 4.5)
    private var totalText: String {
        String(format: "%.1f", SEED.user.points)
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(
                title: "減点明細",
                level: 2,
                right: AnyView(
                    Button {
                        router.go(.myPointsChart)
                    } label: {
                        Text("推移 →")
                            .font(.system(size: 12, weight: .bold))
                            .foregroundStyle(T.primary)
                    }
                    .buttonStyle(.plain)
                )
            )
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // Amber gradient card (#ffefc2 → #f4c677, color #5c3410)
                    VStack(alignment: .leading, spacing: 4) {
                        Text("今月合計")
                            .font(.system(size: 12, weight: .bold))
                            .kerning(1.7)
                            .textCase(.uppercase)
                            .foregroundStyle(Color(hex: 0x5c3410).opacity(0.8))
                        HStack(alignment: .lastTextBaseline, spacing: 6) {
                            Text(totalText)
                                .font(.system(size: 48, weight: .heavy))
                                .monospaced()
                                .foregroundStyle(Color(hex: 0x5c3410))
                            Text("点")
                                .font(.system(size: 14))
                                .foregroundStyle(Color(hex: 0x5c3410).opacity(0.7))
                        }
                    }
                    .padding(.horizontal, 22)
                    .padding(.vertical, 20)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background {
                        RoundedRectangle(cornerRadius: 20, style: .continuous)
                            .fill(LinearGradient(
                                colors: [Color(hex: 0xffefc2), Color(hex: 0xf4c677)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ))
                    }
                    .padding(.bottom, 16)

                    // Progress bar with threshold markers (0 / 4 / 8)
                    progressBar
                        .padding(.bottom, 16)

                    // Points list
                    Card(padding: 0) {
                        VStack(spacing: 0) {
                            ForEach(Array(SEED.points.enumerated()), id: \.offset) { idx, p in
                                if idx > 0 {
                                    Divider().background(T.hair)
                                }
                                pointRow(p)
                            }
                        }
                    }
                    .padding(.bottom, 14)

                    // Rule info
                    VStack(alignment: .leading, spacing: 0) {
                        HStack(spacing: 4) {
                            Text("現在のルール:")
                                .font(.system(size: 12, weight: .bold))
                                .foregroundStyle(T.inkSub)
                            Text("遅刻 0.5 点 / 欠席 1.0 点")
                                .font(.system(size: 12))
                                .foregroundStyle(T.inkSub)
                        }
                        Text("月累計 4 点で清掃罰則 · 月累計 8 点で外出禁止")
                            .font(.system(size: 12))
                            .foregroundStyle(T.inkSub)
                            .padding(.top, 2)
                    }
                    .lineSpacing(3)
                    .padding(.horizontal, 14)
                    .padding(.vertical, 12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background {
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .fill(T.pill)
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .background(T.pearl.ignoresSafeArea())
    }

    private func pointRow(_ p: PointRecord) -> some View {
        HStack(spacing: 12) {
            Text(p.date)
                .font(.system(size: 12))
                .monospaced()
                .foregroundStyle(T.inkMute)
                .frame(width: 80, alignment: .leading)
            Text("\(p.session) · \(p.kind)")
                .font(.system(size: 13))
                .foregroundStyle(T.ink)
            Spacer()
            Text(String(format: "+%.1f", p.val))
                .font(.system(size: 14, weight: .bold))
                .monospaced()
                .foregroundStyle(p.val >= 1 ? T.danger : T.warnDeep)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 14)
    }

    /// 进度条 0 → 8 with threshold markers at 4 (清掃) / 8 (外出禁止)
    private var progressBar: some View {
        let maxVal: Double = 8
        let v = min(SEED.user.points, maxVal)
        let ratio = v / maxVal
        return VStack(alignment: .leading, spacing: 6) {
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    Capsule()
                        .fill(T.hair)
                        .frame(height: 8)
                    Capsule()
                        .fill(LinearGradient(
                            colors: [Color(hex: 0xf4c677), T.warn],
                            startPoint: .leading,
                            endPoint: .trailing
                        ))
                        .frame(width: geo.size.width * CGFloat(ratio), height: 8)

                    // Threshold marker 4
                    Rectangle()
                        .fill(T.warn)
                        .frame(width: 2, height: 14)
                        .offset(x: geo.size.width * CGFloat(4.0 / maxVal) - 1, y: 0)

                    // Threshold marker 8 (at far right, visible as small cap)
                    Rectangle()
                        .fill(T.danger)
                        .frame(width: 2, height: 14)
                        .offset(x: geo.size.width - 2, y: 0)
                }
                .frame(height: 14)
            }
            .frame(height: 14)

            HStack {
                Text("0")
                    .font(.system(size: 10))
                    .monospaced()
                    .foregroundStyle(T.inkMute)
                Spacer()
                Text("4 清掃罰則")
                    .font(.system(size: 10))
                    .foregroundStyle(T.warnDeep)
                Spacer()
                Text("8 外出禁止")
                    .font(.system(size: 10))
                    .foregroundStyle(T.danger)
            }
        }
    }
}

#Preview("MyPoints") {
    MyPointsView()
        .environmentObject(RouterStore(initial: .myPoints))
        .environmentObject(AppStore())
}

// MARK: - 6. MyPointsChartView (L3)

struct MyPointsChartView: View {
    /// 12 个月数据 · 对等 JSX `[0, 0, 1, 0, 0.5, 1, 0, 2, 0, 1, 2, 4]`
    /// 注意：最后一月对齐 SEED.user.points (4.5) 以保持全局一致
    private let data: [Double] = [0, 0, 1, 0, 0.5, 1, 0, 2, 0, 1, 2, 4.5]
    private let months: [String] = ["5", "6", "7", "8", "9", "10", "11", "12", "1", "2", "3", "4"]
    private let maxVal: Double = 8

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "減点推移", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    Card(padding: 20) {
                        VStack(alignment: .leading, spacing: 0) {
                            Text("過去 12 ヶ月")
                                .font(.system(size: 12))
                                .foregroundStyle(T.inkSub)
                                .padding(.bottom, 14)

                            // Canvas chart
                            chartCanvas
                                .frame(height: 200)

                            // Legend
                            HStack(spacing: 16) {
                                Spacer()
                                HStack(spacing: 6) {
                                    Rectangle()
                                        .fill(T.warn)
                                        .frame(width: 14, height: 2)
                                    Text("清掃罰則閾値")
                                        .font(.system(size: 11))
                                        .foregroundStyle(T.inkSub)
                                }
                                HStack(spacing: 6) {
                                    Rectangle()
                                        .fill(T.danger)
                                        .frame(width: 14, height: 2)
                                    Text("外出禁止閾値")
                                        .font(.system(size: 11))
                                        .foregroundStyle(T.inkSub)
                                }
                                Spacer()
                            }
                            .padding(.top, 14)
                        }
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .background(T.pearl.ignoresSafeArea())
    }

    /// 对等 JSX SVG viewBox 0 0 320 180 · gridlines 0/2/4/6/8 · 2 threshold lines · path + dots + x labels
    private var chartCanvas: some View {
        GeometryReader { geo in
            Canvas { ctx, size in
                let left: CGFloat = 30
                let right: CGFloat = size.width
                let top: CGFloat = 10
                let bottom: CGFloat = size.height - 20      // 保留 x-label 空间

                let innerW = right - left
                let innerH = bottom - top

                let yFor: (Double) -> CGFloat = { v in
                    bottom - innerH * CGFloat(v / self.maxVal)
                }
                let xFor: (Int) -> CGFloat = { i in
                    left + innerW * CGFloat(i) / CGFloat(self.data.count - 1)
                }

                // Gridlines 0 / 2 / 4 / 6 / 8
                for g: Double in [0, 2, 4, 6, 8] {
                    let y = yFor(g)
                    var p = Path()
                    p.move(to: CGPoint(x: left, y: y))
                    p.addLine(to: CGPoint(x: right, y: y))
                    ctx.stroke(
                        p,
                        with: .color(T.hair),
                        style: StrokeStyle(lineWidth: 1, dash: [2, 3])
                    )

                    // Y label
                    let text = Text("\(Int(g))")
                        .font(.system(size: 9))
                        .monospaced()
                        .foregroundStyle(T.inkMute)
                    ctx.draw(text, at: CGPoint(x: 10, y: y), anchor: .leading)
                }

                // Threshold line 4 (warn · orange dashed)
                var th4 = Path()
                th4.move(to: CGPoint(x: left, y: yFor(4)))
                th4.addLine(to: CGPoint(x: right, y: yFor(4)))
                ctx.stroke(th4, with: .color(T.warn), style: StrokeStyle(lineWidth: 1, dash: [3, 2]))

                // Threshold line 8 (danger · red dashed)
                var th8 = Path()
                th8.move(to: CGPoint(x: left, y: yFor(8)))
                th8.addLine(to: CGPoint(x: right, y: yFor(8)))
                ctx.stroke(th8, with: .color(T.danger), style: StrokeStyle(lineWidth: 1, dash: [3, 2]))

                // Data polyline
                var line = Path()
                for (i, v) in self.data.enumerated() {
                    let pt = CGPoint(x: xFor(i), y: yFor(v))
                    if i == 0 {
                        line.move(to: pt)
                    } else {
                        line.addLine(to: pt)
                    }
                }
                ctx.stroke(
                    line,
                    with: .color(T.primary),
                    style: StrokeStyle(lineWidth: 2.5, lineCap: .round, lineJoin: .round)
                )

                // Dots · 最后一月 highlight (r=5, warn), others r=3.5
                for (i, v) in self.data.enumerated() {
                    let x = xFor(i)
                    let y = yFor(v)
                    let isLast = (i == self.data.count - 1)
                    let r: CGFloat = isLast ? 5 : 3.5
                    let dot = Path(ellipseIn: CGRect(x: x - r, y: y - r, width: r * 2, height: r * 2))
                    ctx.fill(dot, with: .color(isLast ? T.warn : T.primary))
                }

                // X labels
                for (i, m) in self.months.enumerated() {
                    let x = xFor(i)
                    let text = Text(m)
                        .font(.system(size: 9))
                        .monospaced()
                        .foregroundStyle(T.inkMute)
                    ctx.draw(text, at: CGPoint(x: x, y: size.height - 8), anchor: .center)
                }
            }
            .frame(width: geo.size.width, height: geo.size.height)
        }
    }
}

#Preview("MyPointsChart") {
    MyPointsChartView()
        .environmentObject(RouterStore(initial: .myPointsChart))
        .environmentObject(AppStore())
}

// MARK: - 7. MyDisciplineView (L2)

struct MyDisciplineView: View {
    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "処分履歴", level: 2)
            ScrollView {
                VStack(spacing: 0) {
                    // JSX uses ✨ emoji icon 48pt
                    VStack(spacing: 10) {
                        Text("✨")
                            .font(.system(size: 48))
                        Text("処分歴はまだありません")
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundStyle(T.inkSub)
                    }
                    .padding(40)
                    .frame(maxWidth: .infinity)
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .background(T.pearl.ignoresSafeArea())
    }
}

#Preview("MyDiscipline") {
    MyDisciplineView()
        .environmentObject(RouterStore(initial: .myDiscipline))
        .environmentObject(AppStore())
}

// MARK: - 8. MyHealthView (L2)

struct MyHealthView: View {
    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "体調報告履歴", level: 2)
            ScrollView {
                VStack(spacing: 10) {
                    ForEach(Array(SEED.health.enumerated()), id: \.offset) { _, h in
                        Card(padding: 14) {
                            VStack(alignment: .leading, spacing: 6) {
                                HStack {
                                    HStack(spacing: 8) {
                                        Text(h.sym)
                                            .font(.system(size: 14, weight: .bold))
                                            .foregroundStyle(T.ink)
                                        if let temp = h.temp {
                                            Text(String(format: "%.1f°C", temp))
                                                .font(.system(size: 13, weight: .semibold))
                                                .monospaced()
                                                .foregroundStyle(T.danger)
                                        }
                                    }
                                    Spacer()
                                    Text(h.date)
                                        .font(.system(size: 11))
                                        .monospaced()
                                        .foregroundStyle(T.inkMute)
                                }
                                if !h.note.isEmpty {
                                    Text(h.note)
                                        .font(.system(size: 12.5))
                                        .foregroundStyle(T.inkSub)
                                        .lineSpacing(3)
                                }
                            }
                        }
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .background(T.pearl.ignoresSafeArea())
    }
}

#Preview("MyHealth") {
    MyHealthView()
        .environmentObject(RouterStore(initial: .myHealth))
        .environmentObject(AppStore())
}

// MARK: - 9. MyCleanView (L2)

struct MyCleanView: View {
    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "掃除提出履歴", level: 2)
            ScrollView {
                VStack(spacing: 10) {
                    ForEach(Array(SEED.cleaning.enumerated()), id: \.offset) { _, c in
                        Card(padding: 14) {
                            VStack(alignment: .leading, spacing: 6) {
                                HStack(alignment: .center) {
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(c.range)
                                            .font(.system(size: 14, weight: .bold))
                                            .foregroundStyle(T.ink)
                                        Text(c.date)
                                            .font(.system(size: 11))
                                            .monospaced()
                                            .foregroundStyle(T.inkMute)
                                    }
                                    Spacer()
                                    Pill(
                                        text: c.score != nil
                                            ? "\(c.status) · \(c.score!)点"
                                            : c.status,
                                        tone: c.status == "通過" ? .ok : .danger
                                    )
                                }
                                if c.rejected, let comment = c.comment {
                                    Text(comment)
                                        .font(.system(size: 12))
                                        .foregroundStyle(T.danger)
                                        .padding(.horizontal, 10)
                                        .padding(.vertical, 8)
                                        .frame(maxWidth: .infinity, alignment: .leading)
                                        .background {
                                            RoundedRectangle(cornerRadius: 8, style: .continuous)
                                                .fill(T.dangerBg)
                                        }
                                        .padding(.top, 2)
                                }
                            }
                        }
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .background(T.pearl.ignoresSafeArea())
    }
}

#Preview("MyClean") {
    MyCleanView()
        .environmentObject(RouterStore(initial: .myClean))
        .environmentObject(AppStore())
}

// MARK: - 10. MyPackagesView (L2)

struct MyPackagesView: View {
    @EnvironmentObject var router: RouterStore
    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "快递領取履歴", level: 2)
            ScrollView {
                VStack(spacing: 10) {
                    ForEach(SEED.packages) { p in
                        Button {
                            router.go(.homePackageDetail(id: p.id))
                        } label: {
                            Card(padding: 14) {
                                HStack(spacing: 12) {
                                    Text("📦")
                                        .font(.system(size: 28))
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(p.from)
                                            .font(.system(size: 14, weight: .bold))
                                            .foregroundStyle(T.ink)
                                        Text(p.date)
                                            .font(.system(size: 11))
                                            .monospaced()
                                            .foregroundStyle(T.inkMute)
                                    }
                                    Spacer()
                                    Pill(text: p.status, tone: p.status == "待領" ? .warn : .neutral)
                                }
                            }
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .background(T.pearl.ignoresSafeArea())
    }
}

#Preview("MyPackages") {
    MyPackagesView()
        .environmentObject(RouterStore(initial: .myPackages))
        .environmentObject(AppStore())
}

// MARK: - 11. MySettingsView (L2)

struct MySettingsView: View {
    @EnvironmentObject var app: AppStore

    // 通知 prefs (demo 用 local state; 不接后端)
    @State private var prefRoll: Bool = true       // 点呼リマインダー
    @State private var prefApp: Bool = true        // 申請結果
    @State private var prefPkg: Bool = true        // 快递到着 (JSX 原文：快递到着)
    @State private var prefAct: Bool = true        // 活動リマインダー
    @State private var prefPts: Bool = true        // 減点警告

    private var notifRows: [(key: String, label: String, binding: Binding<Bool>)] {
        [
            ("roll", "点呼リマインダー", $prefRoll),
            ("app",  "申請結果",       $prefApp),
            ("pkg",  "快递到着",       $prefPkg),
            ("act",  "活動リマインダー", $prefAct),
            ("pts",  "減点警告",       $prefPts),
        ]
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "通知設定", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    Card(padding: 0) {
                        VStack(spacing: 0) {
                            ForEach(Array(notifRows.enumerated()), id: \.offset) { idx, row in
                                if idx > 0 {
                                    Divider().background(T.hair)
                                }
                                HStack {
                                    Text(row.label)
                                        .font(.system(size: 14))
                                        .foregroundStyle(T.ink)
                                    Spacer()
                                    TToggle(on: row.binding)
                                }
                                .padding(.horizontal, 18)
                                .padding(.vertical, 14)
                            }
                        }
                    }

                    // Dark mode toggle (iOS 扩展：不在 JSX 但 TASK_E 要求)
                    Card(padding: 0) {
                        HStack {
                            Text("ダークモード")
                                .font(.system(size: 14))
                                .foregroundStyle(T.ink)
                            Spacer()
                            Toggle("", isOn: Binding(
                                get: { app.isDark },
                                set: { app.isDark = $0 }
                            ))
                                .labelsHidden()
                                .toggleStyle(.switch)
                                .tint(T.primary)
                        }
                        .padding(.horizontal, 18)
                        .padding(.vertical, 14)
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .background(T.pearl.ignoresSafeArea())
    }
}

#Preview("MySettings") {
    MySettingsView()
        .environmentObject(RouterStore(initial: .mySettings))
        .environmentObject(AppStore())
}

// MARK: - 12. MyAboutView (L2)

struct MyAboutView: View {
    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "Tomoshibi について", level: 2)
            ScrollView {
                VStack(spacing: 0) {
                    // Wordmark block
                    VStack(spacing: 0) {
                        Text("Tomoshibi")
                            .font(.system(size: 40, weight: .heavy))
                            .kerning(-0.8)
                            .foregroundStyle(T.primaryDk)
                            .padding(.bottom, 4)
                        Text("灯 火")
                            .font(.system(size: 14, weight: .semibold))
                            .kerning(4.2)
                            .foregroundStyle(T.primary)
                            .padding(.bottom, 12)
                        Text("v0.1.0-demo")
                            .font(.system(size: 11))
                            .monospaced()
                            .foregroundStyle(T.inkMute)
                            .padding(.bottom, 32)
                    }
                    .frame(maxWidth: .infinity)

                    // AC signature block
                    VStack(alignment: .leading, spacing: 0) {
                        Text("Tomoshibi は、日本の寮での点呼と生活管理を一体化したシステムです。")
                            .font(.system(size: 13))
                            .foregroundStyle(T.inkSub)
                            .lineSpacing(6)

                        Spacer().frame(height: 12)

                        Text("「日本で留学する私にとって、寮は異国の第二の家。このシステムが守るのは『灯火』—— 毎晩学生が無事に帰宅し、部屋に灯りが灯ること。だから日本語名を Tomoshibi（灯火）にしました。」")
                            .font(.system(size: 13))
                            .foregroundStyle(T.inkSub)
                            .lineSpacing(6)

                        Spacer().frame(height: 16)
                        Divider().background(T.hair)
                        Spacer().frame(height: 16)

                        VStack(alignment: .leading, spacing: 2) {
                            Text("2026 年 AC 入試プロジェクト成果物")
                                .font(.system(size: 12))
                                .foregroundStyle(T.inkMute)
                            Text("— リュウ イヒ")
                                .font(.system(size: 12))
                                .foregroundStyle(T.inkMute)
                        }
                    }
                    .padding(.horizontal, 20)
                    .padding(.vertical, 20)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background {
                        RoundedRectangle(cornerRadius: 18, style: .continuous)
                            .fill(T.paper)
                            .shadow(color: T.ink.opacity(0.04), radius: 2, x: 0, y: 1)
                            .shadow(color: T.ink.opacity(0.05), radius: 14, x: 0, y: 4)
                    }
                    .overlay {
                        RoundedRectangle(cornerRadius: 18, style: .continuous)
                            .stroke(T.hair, lineWidth: 0.5)
                    }
                }
                .padding(.horizontal, 28)
                .padding(.top, 32)
                .padding(.bottom, 24)
            }
        }
        .background(T.pearl.ignoresSafeArea())
    }
}

#Preview("MyAbout") {
    MyAboutView()
        .environmentObject(RouterStore(initial: .myAbout))
        .environmentObject(AppStore())
}

// MARK: - 13. LogoutSheet

struct LogoutSheet: View {
    @EnvironmentObject var app: AppStore
    @EnvironmentObject var router: RouterStore

    var body: some View {
        GlassSheet(onClose: { app.closeSheet() }) {
            VStack(spacing: 0) {
                Text("ログアウトしますか？")
                    .font(.system(size: 20, weight: .heavy))
                    .foregroundStyle(T.ink)
                    .padding(.top, 8)
                    .padding(.bottom, 10)

                Text("次回起動時はアカウント番号と\nパスワードが必要です")
                    .font(.system(size: 13))
                    .foregroundStyle(T.inkSub)
                    .multilineTextAlignment(.center)
                    .lineSpacing(4)
                    .padding(.bottom, 24)

                VStack(spacing: 10) {
                    PrimaryButton(title: "ログアウト", destructive: true) {
                        app.closeSheet()
                        router.replace(.login)
                    }
                    GhostButton(title: "キャンセル") {
                        app.closeSheet()
                    }
                }
            }
            .padding(.horizontal, 4)
        }
    }
}

#Preview("LogoutSheet") {
    ZStack {
        T.pearl.ignoresSafeArea()
        LogoutSheet()
            .environmentObject(RouterStore(initial: .my))
            .environmentObject(AppStore())
    }
}
