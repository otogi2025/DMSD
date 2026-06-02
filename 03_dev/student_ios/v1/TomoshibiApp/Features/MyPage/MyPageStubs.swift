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

/// 月份过滤工具 · 点呼记录 date 形如 "2026-04-21"，按 "yyyy-MM" 前缀归月
private enum MyPageMonthUtil {
    /// 系统当前年月，输出形如 "2026-04"（用于按当月过滤记录）
    static func currentMonthPrefix() -> String {
        let comps = Calendar.current.dateComponents([.year, .month], from: Date())
        return String(format: "%04d-%02d", comps.year ?? 0, comps.month ?? 0)
    }

    /// "4月" / "3月" / "2月" 这类筛选标签 → 该年月前缀 "yyyy-MM"
    /// 演示版基准年固定 2026；生产版用系统当前年（同年内不同月份切换）
    static func prefix(forJapaneseMonthLabel label: String) -> String? {
        // 去掉末尾「月」取数字部分
        let digits = label.filter { $0.isNumber }
        guard let month = Int(digits), (1 ... 12).contains(month) else { return nil }
        #if DEMO
            let year = 2026
        #else
            let year = Calendar.current.component(.year, from: Date())
        #endif
        return String(format: "%04d-%02d", year, month)
    }
}

/// MyLanding 顶部 2-col grid block · 对等 JSX blocks map
private struct MyLandingGridBlock: Identifiable {
    let id = UUID()
    let key: String // "info" / "rollcall" / ...
    let label: String
    let icon: String // emoji
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

    // 2026-05-03 itsuki 拍板「方案 B 分层重设计」:
    //   - profile 缩小（avatar 56 + 一行 info + Pill）
    //   - 学習 / 点呼 / 減点 = Card 化置顶（最重要 → 最显眼）
    //   - 履歴 grid 缩到 6 件（删点呼 / 減点 / 学習 — 已 Card 化）
    //   - settings 删特別運航便（已搬到 Home busCard）

    /// 履歴 grid（6 件 · 2-col grid）
    private var blocks: [MyLandingGridBlock] {
        let pendingPackages = SEED.packages.filter { $0.status == "待領" }.count
        let packagesBadge = pendingPackages > 0 ? "\(pendingPackages)" : nil

        return [
            .init(key: "info", label: "個人情報", icon: "👤", badge: nil, route: .myInfo),
            .init(key: "discipline", label: "処分履歴", icon: "⚖️", badge: nil, route: .myDiscipline),
            .init(key: "health", label: "体調報告履歴", icon: "🤒", badge: nil, route: .myHealth),
            .init(key: "apps", label: "申請履歴", icon: "📄", badge: nil, route: .stayList),
            .init(key: "clean", label: "掃除提出履歴", icon: "🧹", badge: nil, route: .myClean),
            .init(key: "packages", label: "荷物受取履歴", icon: "📦", badge: packagesBadge, route: .myPackages),
        ]
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "マイページ", level: 1)

            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // 1. Profile（紧凑）
                    profileSection
                        .padding(.horizontal, 16)
                        .padding(.top, 6)
                        .padding(.bottom, 14)

                    // 2. ⭐ 主要状态 Card 群（学習 / 点呼 / 減点）
                    VStack(spacing: 10) {
                        // IX-008: 学習卡片入口始终显示（itsuki：UI 还是可以看得到），
                        // 非学習対象点进去由学習详情页显「不需要晚自习」，不在这隐藏。
                        studyStatusCard
                        rollcallStatusCard
                        pointsStatusCard
                    }
                    .padding(.horizontal, 16)
                    .padding(.bottom, 18)

                    // 3. 履歴 section header
                    Text("履歴")
                        .font(.system(size: 11, weight: .heavy))
                        .kerning(0.6)
                        .foregroundStyle(T.inkSub)
                        .padding(.horizontal, 22)
                        .padding(.bottom, 8)

                    // 4. 履歴 grid（6 件）
                    gridSection
                        .padding(.horizontal, 16)
                        .padding(.bottom, 16)

                    // 5. Settings list
                    settingsSection
                        .padding(.horizontal, 16)
                        .padding(.top, 4)
                        .padding(.bottom, 16)
                }
            }
        }
        .background(T.pearl.ignoresSafeArea())
    }

    // MARK: Profile card（紧凑：avatar 56 + 名字 + 账号 + Pill 一行）

    private var profileSection: some View {
        Card(padding: 18) {
            HStack(alignment: .center, spacing: 14) {
                Avatar(letter: app.displayUser.avatar, size: 56)
                VStack(alignment: .leading, spacing: 4) {
                    Text(app.displayUser.name)
                        .font(.system(size: 18, weight: .heavy))
                        .kerning(-0.2)
                        .foregroundStyle(T.ink)
                    HStack(spacing: 4) {
                        Text("アカウント ")
                            .font(.system(size: 11))
                            .foregroundStyle(T.inkMute)
                        Text(app.displayUser.account)
                            .font(.system(size: 11, weight: .bold))
                            .foregroundStyle(T.ink)
                            .monospaced()
                    }
                    HStack(spacing: 6) {
                        Pill(text: "\(app.displayUser.dorm) \(app.displayUser.room)", tone: .accent)
                        Pill(text: app.displayUser.category, tone: .neutral)
                    }
                    .padding(.top, 2)
                }
                Spacer(minLength: 0)
            }
        }
    }

    // MARK: ⭐ 学習ステータス Card

    private var studyStatusCard: some View {
        Button { router.go(.myStudy) } label: {
            HStack(spacing: 14) {
                ZStack {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(T.primary.opacity(0.10))
                        .frame(width: 48, height: 48)
                    Text("📚").font(.system(size: 22))
                }
                VStack(alignment: .leading, spacing: 4) {
                    Text("学習ステータス")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundStyle(T.inkSub)
                    Text(studyStateText)
                        .font(.system(size: 16, weight: .heavy))
                        .foregroundStyle(T.ink)
                    Text("履歴を見る →")
                        .font(.system(size: 11, weight: .semibold))
                        .foregroundStyle(T.primary)
                }
                Spacer(minLength: 0)
            }
            .padding(16)
            .background(landingCardBg)
            .overlay(landingCardBorder)
        }
        .buttonStyle(.plain)
    }

    private var studyStateText: String {
        switch app.studyState {
        case .idle: return "対象外（今日）"
        case .upcoming: return "開始まで \(formatCountdown(app.studyCountdownSec))"
        case .active: return "進行中"
        case .done: return "本日完了 ✅"
        }
    }

    private func formatCountdown(_ sec: Int) -> String {
        let m = sec / 60, s = sec % 60
        return String(format: "%d:%02d", m, s)
    }

    // MARK: ⭐ 点呼履歴 Card

    private var rollcallStatusCard: some View {
        let stats = monthRollcallStats()
        return Button { router.go(.myRollcall) } label: {
            HStack(spacing: 14) {
                ZStack {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(T.okBg)
                        .frame(width: 48, height: 48)
                    Text("📋").font(.system(size: 22))
                }
                VStack(alignment: .leading, spacing: 4) {
                    Text("今月の点呼")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundStyle(T.inkSub)
                    HStack(spacing: 12) {
                        statBlock(num: stats.onTime, label: "時間内", color: T.ok)
                        statBlock(num: stats.late, label: "遅刻", color: T.warn)
                        statBlock(num: stats.absent, label: "欠席", color: T.danger)
                    }
                    Text("詳細を見る →")
                        .font(.system(size: 11, weight: .semibold))
                        .foregroundStyle(T.primary)
                }
                Spacer(minLength: 0)
            }
            .padding(16)
            .background(landingCardBg)
            .overlay(landingCardBorder)
        }
        .buttonStyle(.plain)
    }

    private func monthRollcallStats() -> (onTime: Int, late: Int, absent: Int) {
        var onTime = 0, late = 0, absent = 0
        // IX-025: 标题写「今月」就只统计当月记录，否则接后端多月数据后会偏大。
        // r.date 形如 "2026-04-21"，取前 7 位 "2026-04" 当月份键来过滤。
        #if DEMO
            // 演示版：种子数据全是 2026-04，固定按 4 月口径统计，保持原演示效果
            let monthPrefix = "2026-04"
        #else
            // 生产版：按系统当前年月过滤
            let monthPrefix = MyPageMonthUtil.currentMonthPrefix()
        #endif
        for r in SEED.rollcall where r.date.hasPrefix(monthPrefix) {
            switch r.state {
            case "時間内": onTime += 1
            case "遅刻": late += 1
            case "欠席": absent += 1
            default: break
            }
        }
        return (onTime, late, absent)
    }

    private func statBlock(num: Int, label: String, color: Color) -> some View {
        HStack(spacing: 4) {
            Text(verbatim: "\(num)")
                .font(.system(size: 17, weight: .heavy, design: .monospaced))
                .foregroundStyle(color)
            Text(label)
                .font(.system(size: 10.5))
                .foregroundStyle(T.inkSub)
        }
    }

    // MARK: ⭐ 減点明細 Card

    private var pointsStatusCard: some View {
        let pts = app.displayUser.points
        let level: (numColor: Color, bgColor: Color, label: String, pillTone: Pill.Tone) = {
            if pts >= 8 { return (T.danger, T.dangerBg, "禁足", .danger) }
            if pts >= 4 { return (T.warn, T.warnBg, "罰掃 注意", .warn) }
            return (T.ok, T.okBg, "良好", .ok)
        }()
        return Button { router.go(.myPoints) } label: {
            HStack(spacing: 14) {
                ZStack {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(level.bgColor)
                        .frame(width: 48, height: 48)
                    Text("📉").font(.system(size: 22))
                }
                VStack(alignment: .leading, spacing: 4) {
                    Text("減点明細")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundStyle(T.inkSub)
                    HStack(alignment: .firstTextBaseline, spacing: 6) {
                        Text(String(format: "%.1f", pts))
                            .font(.system(size: 22, weight: .heavy, design: .monospaced))
                            .foregroundStyle(level.numColor)
                        Text("点")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundStyle(T.inkSub)
                        Pill(text: level.label, tone: level.pillTone)
                    }
                    Text("詳細を見る →")
                        .font(.system(size: 11, weight: .semibold))
                        .foregroundStyle(T.primary)
                }
                Spacer(minLength: 0)
            }
            .padding(16)
            .background(landingCardBg)
            .overlay(landingCardBorder)
        }
        .buttonStyle(.plain)
    }

    // MARK: Card 共通背景 + 边框

    private var landingCardBg: some View {
        RoundedRectangle(cornerRadius: 18, style: .continuous)
            .fill(T.paper)
            .shadow(color: T.ink.opacity(0.04), radius: 2, x: 0, y: 1)
            .shadow(color: T.ink.opacity(0.05), radius: 14, x: 0, y: 4)
    }

    private var landingCardBorder: some View {
        RoundedRectangle(cornerRadius: 18, style: .continuous)
            .stroke(T.hair, lineWidth: 0.5)
    }

    // MARK: 履歴 2-col grid（6 件）

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
                .frame(minHeight: 80, alignment: .topLeading)
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
                            Capsule().fill(T.dangerBg)
                        }
                        .foregroundStyle(T.danger)
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
                // 特別運航便 入口は 2026-05-03 Home busCard へ移設（itsuki 拍板：重複解消）
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
        let u = app.displayUser
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

// MARK: - MyInfoEditView (L3) — 連絡先・部屋編集

//
// system_features §6「学生改动履歴」拍板:
//   - 学生可改: 房间号(数字部) / 邮箱 / 电话 / 密码 / 头像
//   - 老师专改(学生 read-only): 学号构成(学年/组/番号) / 姓名
// → 当前 view は room/email/phone のみ編集可。学号・姓名は read-only 表示。

struct MyInfoEditView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    // IX-008: 不再用 @State 默认值在 view init 时抓全局假人 SEED.user
    // （loadMe 晚到 / 切账号都不刷新 → 把演示假房号/邮箱预填进编辑框、存下去当成自己的）。
    // 改在 .onAppear 从 app.displayUser（当前登录用户）填。
    @State private var room: String = ""
    @State private var email: String = ""
    @State private var phone: String = ""

    private var canSave: Bool {
        !room.trimmingCharacters(in: .whitespaces).isEmpty
            && !email.trimmingCharacters(in: .whitespaces).isEmpty
            && !phone.trimmingCharacters(in: .whitespaces).isEmpty
    }

    /// 性別 → prefix（M = 男寮 1 寮 / W = 女寮 4 寮 / A = 男寮 2 寮）
    /// 注: A 寮の判別は元 room の prefix を継承（性別だけでは決まらない）
    private var roomPrefix: String {
        let original = app.displayUser.room
        if let first = original.first, first == "A" { return "A" }
        return app.displayUser.gender == "男" ? "M" : "W"
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "連絡先・部屋編集", level: 3)
            ScrollView {
                VStack(spacing: 18) {
                    readonlyHeader
                    Field(
                        label: "部屋番号",
                        hint: "数字部分のみ。寮プレフィックス（\(roomPrefix)）は性別・寮から自動付与",
                        required: true
                    ) {
                        HStack(spacing: 8) {
                            Text(roomPrefix)
                                .font(.system(size: 18, weight: .heavy, design: .monospaced))
                                .foregroundStyle(T.primary)
                                .frame(width: 38, height: 48)
                                .background {
                                    RoundedRectangle(cornerRadius: T.Radius.sm, style: .continuous)
                                        .fill(T.primary.opacity(0.08))
                                }
                            TField(text: $room, placeholder: "101", keyboard: .numberPad)
                        }
                    }
                    .onChange(of: room) { _, newVal in
                        let filtered = newVal.filter { $0.isNumber }
                        room = String(filtered.prefix(3))
                    }

                    Field(label: "メール", required: true) {
                        TField(text: $email, placeholder: "you@example.com", keyboard: .emailAddress)
                    }

                    Field(label: "電話", required: true) {
                        TField(text: $phone, placeholder: "090-1234-5678", keyboard: .phonePad)
                    }

                    helpInfoBox
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
        .onAppear { loadCurrentInfo() }
    }

    /// IX-008: 进页面时从当前登录用户（app.displayUser）填预填值。
    /// 不在 @State 默认值里抓 —— 那样 view init 一次性捕获，loadMe 晚到 / 切账号都不刷新。
    private func loadCurrentInfo() {
        let u = app.displayUser
        var s = u.room
        if let first = s.first, first == "M" || first == "A" || first == "W" {
            s.removeFirst()
        }
        room = s
        email = u.email
        phone = u.phone
    }

    /// read-only 表示（学号 / 姓名 — 老师専改字段）
    private var readonlyHeader: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("変更不可（先生に依頼）")
                .font(.system(size: 11, weight: .bold))
                .kerning(0.8)
                .foregroundStyle(T.inkMute)
                .textCase(.uppercase)
            Card(padding: 0) {
                VStack(spacing: 0) {
                    HStack {
                        Text("学号")
                            .font(.system(size: 13))
                            .foregroundStyle(T.inkSub)
                            .frame(width: 90, alignment: .leading)
                        Text(app.displayUser.account)
                            .font(.system(size: 14, weight: .semibold, design: .monospaced))
                            .foregroundStyle(T.ink)
                        Spacer()
                        Image(systemName: "lock.fill")
                            .font(.system(size: 11))
                            .foregroundStyle(T.inkMute)
                    }
                    .padding(.horizontal, 16).padding(.vertical, 13)
                    Divider().background(T.hair)
                    HStack {
                        Text("氏名")
                            .font(.system(size: 13))
                            .foregroundStyle(T.inkSub)
                            .frame(width: 90, alignment: .leading)
                        Text(app.displayUser.name)
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundStyle(T.ink)
                        Spacer()
                        Image(systemName: "lock.fill")
                            .font(.system(size: 11))
                            .foregroundStyle(T.inkMute)
                    }
                    .padding(.horizontal, 16).padding(.vertical, 13)
                }
            }
        }
    }

    private var helpInfoBox: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("ℹ 学号・姓名・生年月日・性別の変更は寮監にご連絡ください。")
                .font(.system(size: 12, weight: .semibold))
                .foregroundStyle(T.primaryDk)
            Text("変更履歴は次の画面で確認できます。")
                .font(.system(size: 11))
                .foregroundStyle(T.primaryDk.opacity(0.85))
        }
        .padding(.horizontal, 14).padding(.vertical, 12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background {
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(T.primary.opacity(0.04))
        }
        .overlay {
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(T.primary.opacity(0.13), lineWidth: 1)
        }
    }

    private func saveAndLog() {
        let u0 = app.displayUser
        let newRoom = roomPrefix + room

        app.appendChange(field: "room", label: "部屋番号", before: u0.room, after: newRoom)
        app.appendChange(field: "email", label: "メール", before: u0.email, after: email)
        app.appendChange(field: "phone", label: "電話", before: u0.phone, after: phone)

        // IX-008: 更新当前用户（已迁移到 displayUser 的站点响应式刷新）+ 安全网 SEED.user（未迁移站点仍读它）
        if var u = app.currentUser {
            u.room = newRoom
            u.email = email
            u.phone = phone
            app.currentUser = u
        }
        SEED.user.room = newRoom
        SEED.user.email = email
        SEED.user.phone = phone

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
    /// IX-020: 先按选中月份过滤记录日期再分组，否则点了「4月/3月/2月」按钮列表纹丝不动。
    private var grouped: [(date: String, items: [RollcallEntry])] {
        // selectedMonth 形如 "4月" → 解析成 "yyyy-MM" 前缀，按 r.date 前缀过滤
        let monthPrefix = MyPageMonthUtil.prefix(forJapaneseMonthLabel: selectedMonth)
        var seen: [String] = []
        var map: [String: [RollcallEntry]] = [:]
        for r in SEED.rollcall {
            // 解析失败（理论不会发生）时退回不过滤，保证至少显示全部
            if let p = monthPrefix, !r.date.hasPrefix(p) { continue }
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
                                            router.go(.myRollcallDetail(entryId: r.id))
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
    // IX-012: 详情页原来用写死常量（永远显示 "2026-04-12 朝点呼 / 遅刻 0.5 点"），
    // 连「欠席」记录点进来也显示「遅刻 0.5 点」。改成按被点那行记录渲染。
    //
    // 路由层已补：Route.myRollcallDetail(entryId:) 带关联值，列表点击传 r.id，
    // RootView 按 id 从 SEED.rollcall 查记录传进来；entry 为 nil 时退回第一条做 fallback。
    let entry: RollcallEntry?

    init(entry: RollcallEntry? = nil) {
        self.entry = entry
    }

    /// 实际渲染用的记录：没传就退回种子里第一条记录，至少不再凭空写死
    private var record: RollcallEntry {
        entry ?? SEED.rollcall.first
            ?? RollcallEntry(date: "—", session: "—", state: "時間内", method: "―")
    }

    /// 标题行 "2026-04-21 朝点呼"
    private var titleText: String {
        "\(record.date) \(record.session)"
    }

    /// 点呼场次 ID：由日期 + 朝/晚场次派生，朝场→AM / 晚场→PM，形如 RC-20260421-AM
    private var sessionID: String {
        let datePart = record.date.filter { $0.isNumber }
        let suffix = record.session.hasPrefix("朝") ? "AM" : "PM"
        return "RC-\(datePart)-\(suffix)"
    }

    /// 状態行文字：迟到/缺席带扣分点数，时间内不带点数
    private var stateText: String {
        switch record.state {
        case "遅刻": return "遅刻 0.5 点"
        case "欠席": return "欠席 1.0 点"
        default: return "時間内"
        }
    }

    /// 键值明细：只有迟到才有「打卡时刻 / 迟到时长」两行，缺席和时间内不显示迟到专属行
    private var kvPairs: [(String, String)] {
        var pairs: [(String, String)] = [
            ("状態", stateText),
            ("方式", record.method),
        ]
        if record.session.hasPrefix("朝") {
            pairs.append(("開始時刻", "07:00:00"))
            pairs.append(("締切時刻", "07:10:00"))
        } else {
            pairs.append(("開始時刻", "21:00:00"))
            pairs.append(("締切時刻", "21:10:00"))
        }
        // 打卡时刻 / 迟到时长 仅在迟到（state == "遅刻"）时有意义：缺席没打卡、时间内不迟到
        if record.state == "遅刻" {
            pairs.append(("チェックイン", "07:12:34"))
            pairs.append(("遅れ", "+2分34秒"))
        }
        return pairs
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "点呼セッション詳細", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    Card(padding: 18) {
                        VStack(alignment: .leading, spacing: 0) {
                            Text(titleText)
                                .font(.system(size: 16, weight: .bold))
                                .monospaced()
                                .foregroundStyle(T.primary)
                                .padding(.bottom, 2)
                            Text("セッション ID: \(sessionID)")
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
        .environmentObject(RouterStore(initial: .myRollcallDetail(entryId: nil)))
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
                        Text("グラフ →")
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
                            .foregroundStyle(Color(hex: 0x5C3410).opacity(0.8))
                        HStack(alignment: .lastTextBaseline, spacing: 6) {
                            Text(totalText)
                                .font(.system(size: 48, weight: .heavy))
                                .monospaced()
                                .foregroundStyle(Color(hex: 0x5C3410))
                            Text("点")
                                .font(.system(size: 14))
                                .foregroundStyle(Color(hex: 0x5C3410).opacity(0.7))
                        }
                    }
                    .padding(.horizontal, 22)
                    .padding(.vertical, 20)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background {
                        RoundedRectangle(cornerRadius: 20, style: .continuous)
                            .fill(LinearGradient(
                                colors: [Color(hex: 0xFFEFC2), Color(hex: 0xF4C677)],
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
                            colors: [Color(hex: 0xF4C677), T.warn],
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
            PageHeader(title: "減点グラフ", level: 2)
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
                let bottom: CGFloat = size.height - 20 // 保留 x-label 空间

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
                                        text: c.score.map { "\(c.status) · \($0)点" } ?? c.status,
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
            PageHeader(title: "荷物受取履歴", level: 2) // iosmypage-11：原中文「快递領取履歴」→ 日语
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
    @EnvironmentObject var router: RouterStore // IX-002: 删账号成功后跳登录页用

    // 通知 prefs (demo 用 local state; 不接后端)
    @State private var prefRoll: Bool = true // 点呼リマインダー
    @State private var prefApp: Bool = true // 申請結果
    @State private var prefPkg: Bool = true // 快递到着 (JSX 原文：快递到着)
    @State private var prefAct: Bool = true // 活動リマインダー
    @State private var prefPts: Bool = true // 減点警告

    // App Store 5.1.1(v) 强制要求的账号删除流程
    @State private var showDeleteConfirm: Bool = false
    @State private var deleting: Bool = false
    @State private var deleteError: String? = nil

    private var notifRows: [(key: String, label: String, binding: Binding<Bool>)] {
        [
            ("roll", "点呼リマインダー", $prefRoll),
            ("app", "申請結果", $prefApp),
            ("pkg", "荷物到着", $prefPkg), // iosmypage-11：原中文「快递到着」→ 日语
            ("act", "活動リマインダー", $prefAct),
            ("pts", "減点警告", $prefPts),
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

                    // 暗色模式（iOS 扩展，不在 JSX 但 TASK_E 要求）
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

                    #if DEMO
                        // Push 通知 demo 触发段（仅 demo 版显示、production 编译时排除）
                        pushDemoSection
                    #endif

                    // 账号删除入口（App Store 5.1.1(v) 强制要求）
                    accountDeletionSection
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .background(T.pearl.ignoresSafeArea())
        .alert("アカウントを削除しますか？", isPresented: $showDeleteConfirm) {
            Button("キャンセル", role: .cancel) {}
            Button("削除する", role: .destructive) {
                Task { await performDelete() }
            }
        } message: {
            Text("削除すると元に戻せません。点呼履歴・申請履歴・プロフィール情報がすべて閲覧できなくなります。")
        }
        .alert("削除に失敗しました", isPresented: .constant(deleteError != nil)) {
            Button("OK") { deleteError = nil }
        } message: {
            Text(deleteError ?? "")
        }
    }

    /// 账号删除入口 section（设置页末尾、危险操作走红色系）
    private var accountDeletionSection: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("アカウント")
                .font(.system(size: 11, weight: .bold))
                .foregroundStyle(T.inkMute)
                .kerning(0.6)
                .padding(.top, 14)
            Card(padding: 0) {
                Button {
                    showDeleteConfirm = true
                } label: {
                    HStack {
                        Text(deleting ? "削除中…" : "アカウントを削除")
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundStyle(.red)
                        Spacer()
                        if deleting {
                            ProgressView().scaleEffect(0.8)
                        } else {
                            Image(systemName: "chevron.right")
                                .font(.system(size: 12, weight: .semibold))
                                .foregroundStyle(.red.opacity(0.6))
                        }
                    }
                    .padding(.horizontal, 18)
                    .padding(.vertical, 14)
                    .contentShape(Rectangle())
                }
                .buttonStyle(.plain)
                .disabled(deleting)
            }
            Text("削除すると元に戻せません。")
                .font(.system(size: 11))
                .foregroundStyle(T.inkMute)
                .padding(.top, 4)
                .padding(.horizontal, 4)
        }
    }

    /// 调用后端 DELETE /api/v1/accounts/me 真删账号，成功后清 token 跳登录
    private func performDelete() async {
        deleting = true
        defer { deleting = false }
        do {
            try await AccountsAPI.deleteMyAccount()
            // 成功 → 清 token 触发 didSet 同步 Keychain + APIClient，再跳回登录页（IX-002）。
            // 账号已删，若停在设置页会显示已失效数据；照 LogoutSheet 的登出写法跳 .login。
            app.authToken = nil
            router.replace(.login)
        } catch {
            // 2026-05-27 codex 审查后改：catch 走 helper 统一文案（含 .unprocessable 真 message）
            deleteError = APIErrorPresenter.userMessage(
                for: error,
                fallback: "アカウント削除に失敗しました。時間をおいて再度お試しください。"
            )
        }
    }

    #if DEMO
        /// Push 通知 demo 触发段 — 4 个事件按钮（学習批 / 学習拒 / 名单加入 / 修改届再批）
        /// memory project_demo_scaffolds_to_remove_before_v1.md（push trigger 项）
        private var pushDemoSection: some View {
            VStack(alignment: .leading, spacing: 6) {
                Text("⚠️ Push 通知 デモ")
                    .font(.system(size: 11, weight: .bold))
                    .foregroundStyle(T.warnDeep)
                    .kerning(0.6)
                    .padding(.top, 8)
                Text("この section は demo 版限定です（production では非表示）。")
                    .font(.system(size: 10))
                    .foregroundStyle(T.inkMute)
                Card(padding: 0) {
                    VStack(spacing: 0) {
                        pushDemoRow(label: "学習欠席届 → 承認") {
                            app.simulateStudyLeaveApproved()
                        }
                        Divider().background(T.hair)
                        pushDemoRow(label: "学習欠席届 → 不承認") {
                            app.simulateStudyLeaveRejected()
                        }
                        Divider().background(T.hair)
                        pushDemoRow(label: "学習対象に追加された") {
                            app.simulateStudyRosterAdded()
                        }
                        Divider().background(T.hair)
                        pushDemoRow(label: "外泊届（修改届）が再承認された") {
                            app.simulateAmendmentRebatch()
                        }
                    }
                }
            }
        }

        private func pushDemoRow(label: String, action: @escaping () -> Void) -> some View {
            Button(action: action) {
                HStack {
                    Image(systemName: "bell.badge.fill")
                        .font(.system(size: 13))
                        .foregroundStyle(T.warn)
                    Text(label)
                        .font(.system(size: 13))
                        .foregroundStyle(T.ink)
                    Spacer()
                    Text("送信")
                        .font(.system(size: 11, weight: .semibold))
                        .foregroundStyle(T.primary)
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
        }
    #endif
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
                        Text(AppVersionTag.full)
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

// MARK: - 学習履歴 (system_features §7.3.10) — isStudyTarget のみ

struct MyStudyView: View {
    @EnvironmentObject var app: AppStore

    /// 当月（demo: 全件）の出席状況サマリ
    private var thisMonthStats: (present: Int, late: Int, abnormal: Int, absentExcused: Int) {
        let entries = app.studyHistory
        // 按日期分组 → 当天 tap 种类齐全(= StudyTap 全部 2 种) = present / 缺一种 = abnormal / 0 = absent
        let dates = Set(entries.map { $0.date })
        var present = 0, late = 0, abnormal = 0
        for d in dates {
            let dayEntries = entries.filter { $0.date == d }
            let tapKinds = Set(dayEntries.map { $0.tapKind })
            if tapKinds.count == StudyTap.allCases.count {
                let lateNote = dayEntries.contains { $0.note?.contains("遅刻") == true }
                if lateNote { late += 1 } else { present += 1 }
            } else if tapKinds.count > 0 {
                abnormal += 1
            }
        }
        return (present, late, abnormal, app.studyLeaveCountThisMonth)
    }

    private var groupedByDate: [(date: String, items: [StudyHistoryEntry])] {
        var seen: [String] = []
        var map: [String: [StudyHistoryEntry]] = [:]
        for e in app.studyHistory {
            if map[e.date] == nil { seen.append(e.date) }
            map[e.date, default: []].append(e)
        }
        return seen.map { (date: $0, items: map[$0] ?? []) }
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "学習履歴", level: 2)
            // IX-008: 非学習対象（老师后台未指定）→ 点进来显「不需要晚自习」，不显履历
            // （itsuki：UI 入口可见、点进去显示他不需要晚自习）。
            if app.displayUser.isStudyTarget {
                ScrollView {
                    VStack(alignment: .leading, spacing: 14) {
                        summaryCard
                        leaveStatsCard
                        historyCard
                        helpInfoBox
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 4)
                    .padding(.bottom, 24)
                }
            } else {
                notStudyTargetNotice
            }
        }
        .background(T.pearl.ignoresSafeArea())
    }

    /// 非晚自习对象学生点进「学習履歴」时看到的提示页。
    private var notStudyTargetNotice: some View {
        VStack(spacing: 14) {
            Spacer()
            Text("📚").font(.system(size: 44))
            Text("学習対象外です")
                .font(.system(size: 17, weight: .heavy))
                .foregroundStyle(T.ink)
            Text("あなたは現在、晩学習（夜間学習）の対象ではありません。\n学習担当の先生が対象に指定すると、ここに出席状況が表示されます。")
                .font(.system(size: 13))
                .foregroundStyle(T.inkSub)
                .multilineTextAlignment(.center)
                .lineSpacing(4)
                .padding(.horizontal, 32)
            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    // MARK: 月度 summary

    private var summaryCard: some View {
        let stats = thisMonthStats
        return Card(padding: 18) {
            VStack(alignment: .leading, spacing: 14) {
                HStack {
                    Text("今月の学習出席")
                        .font(.system(size: 12, weight: .bold))
                        .foregroundStyle(T.inkSub).kerning(1.2)
                    Spacer()
                    Text(app.displayUser.isStudyTarget ? "対象" : "対象外")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundStyle(T.primary)
                        .padding(.horizontal, 8).padding(.vertical, 2)
                        .background { Capsule().fill(T.primary.opacity(0.10)) }
                }
                HStack(spacing: 12) {
                    statBox(label: "出席", count: stats.present, color: T.ok)
                    statBox(label: "遅刻", count: stats.late, color: T.warn)
                    statBox(label: "異常", count: stats.abnormal, color: T.danger)
                }
            }
        }
    }

    private func statBox(label: String, count: Int, color: Color) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label)
                .font(.system(size: 11, weight: .semibold))
                .foregroundStyle(T.inkSub)
            HStack(alignment: .lastTextBaseline, spacing: 3) {
                Text("\(count)")
                    .font(.system(size: 24, weight: .heavy, design: .monospaced))
                    .foregroundStyle(color)
                Text("回")
                    .font(.system(size: 11))
                    .foregroundStyle(T.inkMute)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 12).padding(.vertical, 10)
        .background {
            RoundedRectangle(cornerRadius: 12, style: .continuous).fill(T.pill)
        }
    }

    // MARK: 当月 leave count

    private var leaveStatsCard: some View {
        Card(padding: 14) {
            HStack(spacing: 10) {
                ZStack {
                    Circle().fill(T.warnBg).frame(width: 40, height: 40)
                    Text("📝").font(.system(size: 22))
                }
                VStack(alignment: .leading, spacing: 2) {
                    Text("今月の学習欠席届")
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundStyle(T.inkSub)
                    HStack(alignment: .lastTextBaseline, spacing: 4) {
                        Text("\(app.studyLeaveCountThisMonth)")
                            .font(.system(size: 22, weight: .heavy, design: .monospaced))
                            .foregroundStyle(app.studyLeaveCountThisMonth > 3 ? T.danger : T.ink)
                        Text("回")
                            .font(.system(size: 12))
                            .foregroundStyle(T.inkMute)
                    }
                }
                Spacer()
                if app.studyLeaveCountThisMonth > 3 {
                    Text("超過")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundStyle(T.danger)
                        .padding(.horizontal, 8).padding(.vertical, 3)
                        .background { Capsule().fill(T.dangerBg) }
                }
            }
        }
    }

    // MARK: 履歴 list

    private var historyCard: some View {
        Card(padding: 0) {
            VStack(spacing: 0) {
                HStack {
                    Text("出席タップ履歴")
                        .font(.system(size: 12, weight: .bold))
                        .foregroundStyle(T.inkSub).kerning(1.2)
                    Spacer()
                    Text("\(app.studyHistory.count) 件")
                        .font(.system(size: 11, weight: .semibold, design: .monospaced))
                        .foregroundStyle(T.inkMute)
                }
                .padding(.horizontal, 16).padding(.top, 14).padding(.bottom, 8)

                if app.studyHistory.isEmpty {
                    VStack(spacing: 10) {
                        Text("✨").font(.system(size: 40))
                        Text("履歴はまだありません")
                            .font(.system(size: 13))
                            .foregroundStyle(T.inkMute)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 30)
                } else {
                    ForEach(Array(groupedByDate.enumerated()), id: \.offset) { idx, grp in
                        if idx > 0 { Divider().background(T.hair) }
                        dayBlock(date: grp.date, items: grp.items)
                    }
                }
            }
        }
    }

    @ViewBuilder
    private func dayBlock(date: String, items: [StudyHistoryEntry]) -> some View {
        let kinds = Set(items.map { $0.tapKind })
        let complete = kinds.count == StudyTap.allCases.count
        // IX-033: 日块原来只看打卡数齐全就贴绿色「時間内」，跟汇总卡（齐全 + 备注含「遅刻」算迟到）口径不一致。
        // 这里也判断当天是否有打卡备注含「遅刻」，齐全但迟到 → 黄色「遅刻」，齐全且无迟到 → 绿色「時間内」。
        let hasLate = items.contains { $0.note?.contains("遅刻") == true }
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 8) {
                Text(date)
                    .font(.system(size: 12, weight: .semibold, design: .monospaced))
                    .foregroundStyle(T.inkSub)
                if complete && hasLate {
                    Text("遅刻")
                        .font(.system(size: 10.5, weight: .bold))
                        .foregroundStyle(T.warnDeep)
                        .padding(.horizontal, 7).padding(.vertical, 2)
                        .background { Capsule().fill(T.warnBg) }
                } else if complete {
                    Text("時間内")
                        .font(.system(size: 10.5, weight: .bold))
                        .foregroundStyle(T.okDeep)
                        .padding(.horizontal, 7).padding(.vertical, 2)
                        .background { Capsule().fill(T.okBg) }
                } else {
                    Text("未完")
                        .font(.system(size: 10.5, weight: .bold))
                        .foregroundStyle(T.danger)
                        .padding(.horizontal, 7).padding(.vertical, 2)
                        .background { Capsule().fill(T.dangerBg) }
                }
                Spacer()
                Text("\(items.count) / \(StudyTap.allCases.count)")
                    .font(.system(size: 11, design: .monospaced))
                    .foregroundStyle(T.inkMute)
            }
            VStack(spacing: 0) {
                ForEach(Array(items.enumerated()), id: \.element.id) { i, e in
                    HStack(spacing: 12) {
                        Text(e.timeHM)
                            .font(.system(size: 12, weight: .semibold, design: .monospaced))
                            .foregroundStyle(T.ink)
                            .frame(width: 50, alignment: .leading)
                        Text(e.tapLabel)
                            .font(.system(size: 12.5))
                            .foregroundStyle(T.ink)
                        Spacer()
                        if let n = e.note {
                            Text(n)
                                .font(.system(size: 11, weight: .semibold))
                                .foregroundStyle(T.warnDeep)
                                .padding(.horizontal, 6).padding(.vertical, 1)
                                .background { Capsule().fill(T.warnBg) }
                        }
                    }
                    .padding(.vertical, 6)
                    if i < items.count - 1 {
                        Rectangle().fill(T.hair).frame(height: 0.5)
                    }
                }
            }
            .padding(.leading, 4)
        }
        .padding(.horizontal, 16).padding(.vertical, 10)
    }

    // MARK: help info box

    private var helpInfoBox: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("ℹ 学習出席は NFC を 1 日 2 回タップ")
                .font(.system(size: 12, weight: .bold))
                .foregroundStyle(T.primaryDk)
            Text("学習開始 (19:40) ／ 学習終了 (21:45)。2 回揃わない場合は異常扱いとなり、学習担当の先生が手動で判定します。")
                .font(.system(size: 11.5))
                .foregroundStyle(T.primaryDk.opacity(0.85))
                .lineSpacing(3)
        }
        .padding(.horizontal, 14).padding(.vertical, 12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background {
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(T.primary.opacity(0.04))
        }
        .overlay {
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(T.primary.opacity(0.13), lineWidth: 1)
        }
    }
}

#Preview("MyStudy") {
    MyStudyView()
        .environmentObject(RouterStore(initial: .myStudy))
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
                        app.authToken = nil // didSet 清 Keychain + APIClient token — 真登出（原来只跳转没清令牌）
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
