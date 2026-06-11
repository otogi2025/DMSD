// SEED.swift · 全量 demo 数据
// ⚠️ 对齐 Web Round 3 最新口径 (itsuki 2026-04-22 决策):
//   - 房间号 A5 / 男寮 / 4.5 分 (迟到 5 · 欠席 2) — itsuki 2026-05-28 指定 demo 房间号默认 A5
//   - リュウ イヒ / 2006-10-14 / 19 岁

import Foundation

enum SEED {
    /// 演示默认用户的不可变副本 — 登出 / 令牌失效时 SEED.user 复位用（IX-008：
    /// 生产态 loadMe 会把真实用户写回 SEED.user 当安全网，登出必须复位防真实用户数据残留）。
    static let demoUserSeed = User(
        account: "060218", // 06(高3) + 02(B組) + 18(出席番号) → "060218"
        name: "リュウ イヒ",
        nameKana: "りゅう いひ",
        birth: "2006-10-14",
        age: 19,
        gender: "男", // iosmypage-06：原「女」跟男寮 + 后端 seed(060218 gender=male) 矛盾 → 对齐成男
        dorm: "男寮",
        room: "A5", // demo 房间号 (itsuki 2026-05-28 指定默认 A5)
        category: "一般寮生",
        email: "demo@example.com",
        phone: "090-0000-0000",
        avatar: "リ",
        points: 4.5,
        lateCount: 5,
        absentCount: 2,
        grade: "高3",
        classSuffix: "B",
        seatNo: 18
    )

    nonisolated(unsafe) static var user: User = demoUserSeed

    static let points: [PointRecord] = [
        .init(date: "2026-04-05", session: "朝点呼", kind: "遅刻", val: 0.5),
        .init(date: "2026-04-07", session: "朝点呼", kind: "遅刻", val: 0.5),
        .init(date: "2026-04-12", session: "朝点呼", kind: "遅刻", val: 0.5),
        .init(date: "2026-04-15", session: "晩点呼", kind: "欠席", val: 1.0),
        .init(date: "2026-04-18", session: "朝点呼", kind: "遅刻", val: 0.5),
        .init(date: "2026-04-20", session: "晩点呼", kind: "欠席", val: 1.0),
        .init(date: "2026-04-21", session: "朝点呼", kind: "遅刻", val: 0.5),
    ]

    static let rollcall: [RollcallEntry] = {
        let days = ["2026-04-21", "2026-04-20", "2026-04-19", "2026-04-18", "2026-04-17", "2026-04-16", "2026-04-15", "2026-04-14", "2026-04-13", "2026-04-12", "2026-04-11", "2026-04-10", "2026-04-09", "2026-04-08", "2026-04-07", "2026-04-06", "2026-04-05"]
        let specials: [String: String] = [
            "2026-04-21:朝": "遅刻",
            "2026-04-20:晩": "欠席",
            "2026-04-18:朝": "遅刻",
            "2026-04-15:晩": "欠席",
            "2026-04-12:朝": "遅刻",
            "2026-04-07:朝": "遅刻",
            "2026-04-05:朝": "遅刻",
        ]
        var arr: [RollcallEntry] = []
        for d in days {
            for s in ["朝", "晩"] {
                let k = "\(d):\(s)"
                let state = specials[k] ?? "時間内"
                let method = state == "欠席" ? "―" : "NFC"
                arr.append(.init(date: d, session: s + "点呼", state: state, method: method))
            }
        }
        return arr
    }()

    static let health: [HealthRecord] = [
        .init(date: "2026-04-14", sym: "頭痛", temp: 37.2, note: "午後ずっと頭が重い"),
        .init(date: "2026-04-03", sym: "腹痛", temp: nil, note: ""),
    ]

    static let packages: [PackageItem] = [
        .init(id: 1, date: "2026-04-22", from: "宅配便", status: "待領", tracking: "JP12345"),
        .init(id: 2, date: "2026-04-18", from: "佐川", status: "領済", tracking: nil),
        .init(id: 3, date: "2026-04-10", from: "ヤマト", status: "領済", tracking: nil),
        .init(id: 4, date: "2026-04-05", from: "郵便局", status: "領済", tracking: nil),
    ]

    // IX-009：演示假通知 fixture —— 圈进 #if DEMO，生产构建物理上没有这段，
    //   防 5 条假通知（荷物到着 / 誕生日会 / 遅刻警告 等）泄漏到上线 app。
    //   生产通知源 = 真公告（AppStore.announcementNotifications）+ 真 push。
    #if DEMO
        static let notifications: [NotificationItem] = [
            .init(id: 1, type: "宅配", title: "荷物到着", time: "今日 14:20", body: "寮管室前で受取り", unread: true),
            .init(id: 2, type: "申請", title: "外泊申請が承認されました", time: "昨日 16:30", body: "承認されました", unread: true),
            .init(id: 3, type: "減点", title: "遅刻警告", time: "昨日 9:00", body: "今月の遅刻が 5 回に到達", unread: false),
            .init(id: 4, type: "活動", title: "明日 18:00 誕生日会", time: "昨日", body: "カフェテリア集合", unread: true),
            .init(id: 5, type: "リクエスト曲", title: "あなたの投稿曲が採用されました", time: "2 日前", body: "Lemon / 米津玄師", unread: false),
        ]
    #endif

    static let applications: [ApplicationItem] = [
        .init(id: "a1", type: "stay", status: "pending", date: "2026-04-20", summary: "東京 · 2 泊 3 日"),
        .init(id: "a3", type: "holiday", status: "approved", date: "2026-04-15", summary: "茨城 · 帰省"),
        .init(id: "a4", type: "outing", status: "approved", date: "2026-04-02", summary: "駅前 · タクシー予約"),
    ]

    /// 実スクールバス時刻表（2026-04-29 水 GW外泊・帰省等 特別運行便パターン）
    /// 詳細は DMSD/02_design/bus_schedule_real.md 参照
    static let buses: [BusLine] = [
        .init(time: "07:30", route: "高校棟 → 岡山駅西口", seats: "空きあり", next: true),
        .init(time: "10:10", route: "高校棟 → 金川駅", seats: "空きあり", next: false),
        .init(time: "15:33", route: "金川駅 → 寮", seats: "残 3", next: false),
        .init(time: "17:02", route: "金川駅 → 寮", seats: "残 5", next: false),
    ]

    static let busNotice: (active: Bool, text: String) = (
        true,
        "4/29(水) GW外泊・帰省・買い物 特別運行便 · 乗車名簿に事前チェック"
    )

    /// 完整巴士日程（DMSD/02_design/bus_schedule_real.md 対応 · 日別グループ）
    static let busSchedule: [BusDaySchedule] = [
        .init(
            date: "2026-04-29", weekday: "水",
            label: "GW外泊・帰省・買い物",
            notice: "特別運行便 · 乗車名簿に事前チェック",
            lines: [
                .init(time: "07:30", route: "高校棟 → 岡山駅西口", seats: "空きあり", next: true),
                .init(time: "10:10", route: "高校棟 → 金川駅", seats: "空きあり", next: false),
                .init(time: "15:33", route: "金川駅 → 寮", seats: "残 3", next: false),
                .init(time: "17:02", route: "金川駅 → 寮", seats: "残 5", next: false),
            ]
        ),
        .init(
            date: "2026-05-06", weekday: "水",
            label: "GW後帰寮日・買い物",
            notice: "特別運行便",
            lines: [
                .init(time: "09:20", route: "高校棟 → 金川駅", seats: "空きあり", next: false),
                .init(time: "10:10", route: "高校棟 → 金川駅", seats: "空きあり", next: false),
                .init(time: "15:33", route: "金川駅 → 寮", seats: "空きあり", next: false),
                .init(time: "18:45", route: "岡山駅西口 → 寮", seats: "空きあり", next: false),
            ]
        ),
        .init(
            date: "2026-05-16", weekday: "土",
            label: "みつ元気プロジェクト・買い物",
            // IX-023: 这条是特别运行班车（4-11 同款事件也注明了特别运行），原 notice 写死空值
            // 会被 BusList 按「有无 notice」错判成通学便，补上 notice 修正分类（仅演示数据）
            notice: "特別運行便",
            lines: [
                .init(time: "08:30", route: "西口発", seats: "空きあり", next: false),
                .init(time: "09:20", route: "高校棟 → 御津公民館", seats: "空きあり", next: false),
                .init(time: "10:10", route: "高校棟 → 金川駅", seats: "空きあり", next: false),
                .init(time: "12:00", route: "御津公民館発", seats: "空きあり", next: false),
                .init(time: "12:20", route: "高校棟 → 西口", seats: "空きあり", next: false),
                .init(time: "15:33", route: "金川駅 → 寮", seats: "空きあり", next: false),
                .init(time: "17:02", route: "金川駅 → 寮", seats: "空きあり", next: false),
            ]
        ),
        .init(
            date: "2026-05-23", weekday: "土",
            label: "音楽と青空市（御津公民館）",
            notice: "基本ボランティア用 · 時間帯注意",
            lines: [
                .init(time: "07:30", route: "岡山駅西口発", seats: "空きあり", next: false),
                .init(time: "08:15", route: "高校棟発", seats: "空きあり", next: false),
                .init(time: "08:35", route: "御津公民館着", seats: "空きあり", next: false),
                .init(time: "16:00", route: "御津公民館発", seats: "空きあり", next: false),
                .init(time: "16:20", route: "高校棟発", seats: "空きあり", next: false),
                .init(time: "17:00", route: "岡山駅西口着", seats: "空きあり", next: false),
            ]
        ),
        .init(
            date: "2026-05-31", weekday: "日",
            label: "英検 第1回 一次試験・買い物",
            notice: "時程調整予定",
            lines: [
                .init(time: "06:40", route: "高校棟 → 金川駅", seats: "受験者+買い物", next: false),
                .init(time: "09:20", route: "高校棟 → 金川駅", seats: "買い物のみ", next: false),
                .init(time: "11:00", route: "高校棟 → 金川駅", seats: "受験者+買い物", next: false),
                .init(time: "15:33", route: "金川駅 → 寮", seats: "買い物のみ", next: false),
                .init(time: "17:31", route: "金川駅 → 寮", seats: "受験者+買い物", next: false),
            ]
        ),
    ]

    /// 活動・行事（カレンダー表示用）· bus_schedule_real.md の行事日も連動
    static let events: [EventItem] = [
        .init(date: "2026-04-05", time: "08:30", title: "留4アクティビティ", place: "岡山城・後楽園", desc: "お花見弁当・岡山城見学・後楽園散策・さくらカーニバル。参加希望者は高野まで。"),
        .init(date: "2026-04-07", time: "15:33", title: "帰寮日", place: "金川駅・岡山駅西口", desc: "15:33 金川駅発 / 18:45 岡山駅西口発（寮行き）"),
        .init(date: "2026-04-08", time: "09:00", title: "始業式・新任式・高等部進級式", place: "本校", desc: ""),
        .init(date: "2026-04-09", time: "09:00", title: "入学式", place: "本校", desc: "家庭学習日 2①②③"),
        .init(date: "2026-04-10", time: "09:00", title: "春期課題考査", place: "本校", desc: "1〜③ + 新入生オリエンテーション"),
        .init(date: "2026-04-11", time: "08:30", title: "みつ元気プロジェクト", place: "御津公民館", desc: "戦略会議 9:45〜。特別運行便あり。"),
        .init(date: "2026-04-23", time: "18:00", title: "誕生日会", place: "カフェテリア", desc: "夕食後、軽食と自己紹介タイム"),
        .init(date: "2026-04-25", time: "10:00", title: "避難訓練", place: "寮玄関前集合", desc: "全員参加必須"),
        .init(date: "2026-04-26", time: "14:00", title: "茶道部体験", place: "和室", desc: "初心者歓迎"),
        .init(date: "2026-04-29", time: "07:30", title: "GW外泊・帰省・買い物", place: "特別運行便", desc: "7:30 高校棟→岡山駅西口 / 10:10 高校棟→金川駅 / 15:33,17:02 金川駅→寮"),
        .init(date: "2026-05-06", time: "09:20", title: "GW後帰寮日", place: "特別運行便", desc: "9:20,10:10 高校棟→金川駅 / 15:33 金川駅→寮 / 18:45 岡山駅西口→寮"),
        .init(date: "2026-05-16", time: "08:30", title: "みつ元気プロジェクト", place: "御津公民館", desc: "4/11 同パターン"),
        .init(date: "2026-05-23", time: "07:30", title: "音楽と青空市", place: "岡山市立御津公民館", desc: "基本ボランティア用。時間帯注意。"),
        .init(date: "2026-05-31", time: "06:40", title: "英検 第1回 一次試験", place: "会場", desc: "時程調整予定。級受験者 + 買い物希望者向け特別運行便あり。"),
    ]

    static let lost: [LostItem] = [
        .init(id: 1, title: "青い折りたたみ傘", place: "玄関", date: "04-21", color: "#3b82f6"),
        .init(id: 2, title: "黒の鍵", place: "玄関", date: "04-20", color: "#1f2937"),
        .init(id: 3, title: "赤のペンケース", place: "図書室", date: "04-18", color: "#ef4444"),
        .init(id: 4, title: "緑のノート", place: "玄関", date: "04-16", color: "#10b981"),
        .init(id: 5, title: "イヤホン (白)", place: "廊下", date: "04-15", color: "#f3f4f6"),
        .init(id: 6, title: "財布", place: "男子浴場", date: "04-12", color: "#7c3aed"),
    ]

    static let songs: [SongItem] = [
        .init(id: 1, title: "Lemon", artist: "米津玄師", by: "00号", up: 24, down: 1),
        .init(id: 2, title: "夜に駆ける", artist: "YOASOBI", by: "12号", up: 18, down: 3),
        .init(id: 3, title: "Pretender", artist: "Official髭男dism", by: "07号", up: 15, down: 2),
        .init(id: 4, title: "炎", artist: "LiSA", by: "05号", up: 12, down: 4),
        .init(id: 5, title: "紅蓮華", artist: "LiSA", by: "15号", up: 10, down: 2),
        .init(id: 6, title: "マリーゴールド", artist: "あいみょん", by: "03号", up: 8, down: 1),
        .init(id: 7, title: "群青", artist: "YOASOBI", by: "11号", up: 6, down: 0),
        .init(id: 8, title: "ミックスナッツ", artist: "Official髭男dism", by: "09号", up: 4, down: 1),
    ]

    /// 老师公告（演示版假数据 — 真公告走后端 /api/v1/announcements）。
    /// 6-11 itsuki 发现公告页一直是孤儿（没入口），补主页入口后才暴露演示版从来没有 seed → 列表报通信错误。
    static let announcements: [AnnouncementBrief] = [
        AnnouncementBrief(
            id: UUID(uuidString: "AAAA0001-0000-0000-0000-000000000001")!,
            title: "台風接近に伴う門限変更のお知らせ",
            bodySummary: "明日は台風の接近が予想されるため、門限を 18:00 に繰り上げます。外出予定の寮生は早めに帰寮してください。",
            scope: "all",
            authorTeacherId: UUID(uuidString: "BBBB0001-0000-0000-0000-000000000001")!,
            authorTeacherName: "田中 寮監",
            createdAt: Date().addingTimeInterval(-3600 * 5),
            updatedAt: Date().addingTimeInterval(-3600 * 5),
            isRead: false,
            replyCount: 2
        ),
        AnnouncementBrief(
            id: UUID(uuidString: "AAAA0002-0000-0000-0000-000000000002")!,
            title: "週末の定期清掃について",
            bodySummary: "今週末、共用スペースの定期清掃を行います。当日は私物を各自の部屋に移動しておいてください。",
            scope: "all",
            authorTeacherId: UUID(uuidString: "BBBB0002-0000-0000-0000-000000000002")!,
            authorTeacherName: "佐藤 先生",
            createdAt: Date().addingTimeInterval(-86400 * 2),
            updatedAt: Date().addingTimeInterval(-86400 * 2),
            isRead: false,
            replyCount: 0
        ),
        AnnouncementBrief(
            id: UUID(uuidString: "AAAA0003-0000-0000-0000-000000000003")!,
            title: "食堂メニュー変更のお知らせ",
            bodySummary: "来月より食堂の夕食メニューを一部変更します。アレルギー対応については栄養士までご相談ください。",
            scope: "all",
            authorTeacherId: UUID(uuidString: "BBBB0003-0000-0000-0000-000000000003")!,
            authorTeacherName: "山本 栄養士",
            createdAt: Date().addingTimeInterval(-86400 * 6),
            updatedAt: Date().addingTimeInterval(-86400 * 6),
            isRead: true,
            replyCount: 1
        ),
    ]

    /// 公告详情（演示版）— 全文 + 回复，按 id 字符串（小写）查
    static let announcementDetails: [String: AnnouncementDetail] = {
        func reply(_ kind: String, _ name: String, _ body: String, _ ago: TimeInterval) -> AnnouncementReplyOut {
            AnnouncementReplyOut(
                id: UUID(), authorKind: kind, authorId: UUID(),
                authorName: name, body: body, createdAt: Date().addingTimeInterval(ago)
            )
        }
        let bodies: [String: (String, [AnnouncementReplyOut])] = [
            "aaaa0001-0000-0000-0000-000000000001": (
                "明日（6/12）は台風の接近が予想されます。つきましては、安全確保のため門限を通常より早め、18:00 とします。\n\n外出予定の寮生は早めに帰寮してください。やむを得ず遅れる場合は必ず寮監まで連絡してください。",
                [reply("teacher", "田中 寮監", "進路状況によっては追加で連絡します。", -3600 * 4),
                 reply("student", "リュウ イヒ", "承知しました。", -3600 * 3)]
            ),
            "aaaa0002-0000-0000-0000-000000000002": (
                "今週末（土曜 10:00〜）、共用スペース（ラウンジ・洗濯室）の定期清掃を行います。当日は私物を各自の部屋に移動しておいてください。移動されていない私物は一時的に保管します。",
                []
            ),
            "aaaa0003-0000-0000-0000-000000000003": (
                "来月より食堂の夕食メニューを一部変更します。栄養バランスを考慮した新メニューを導入します。\n\nアレルギー対応については、これまで通り栄養士までご相談ください。",
                [reply("teacher", "山本 栄養士", "ご要望があればこの投稿に返信してください。", -86400 * 5)]
            ),
        ]
        var dict: [String: AnnouncementDetail] = [:]
        for a in announcements {
            let key = a.id.uuidString.lowercased()
            let (body, replies) = bodies[key] ?? (a.bodySummary, [])
            dict[key] = AnnouncementDetail(
                id: a.id, title: a.title, body: body, scope: a.scope,
                authorTeacherId: a.authorTeacherId, authorTeacherName: a.authorTeacherName,
                createdAt: a.createdAt, updatedAt: a.updatedAt, replies: replies
            )
        }
        return dict
    }()
}
