// SEED.swift · 全量 demo 数据
// ⚠️ 对齐 Web Round 3 最新口径 (itsuki 2026-04-22 决策):
//   - M101 / 男寮 / 4.5 分 (迟到 5 · 欠席 2)
//   - リュウ イヒ / 2006-10-14 / 19 岁

import Foundation

enum SEED {
    nonisolated(unsafe) static var user: User = User(
        account: "060218",        // 06(高3) + 02(B組) + 18(出席番号) → "060218"
        name: "リュウ イヒ",
        nameKana: "りゅう いひ",
        birth: "2006-10-14",
        age: 19,
        gender: "女",
        dorm: "男寮",
        room: "M101",
        category: "一般寮生",
        email: "otogi2025@gmail.com",
        phone: "090-0000-0000",
        avatar: "リ",
        points: 4.5,
        lateCount: 5,
        absentCount: 2,
        grade: "高3",
        classSuffix: "B",
        seatNo: 18
    )

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
        let days = ["2026-04-21","2026-04-20","2026-04-19","2026-04-18","2026-04-17","2026-04-16","2026-04-15","2026-04-14","2026-04-13","2026-04-12","2026-04-11","2026-04-10","2026-04-09","2026-04-08","2026-04-07","2026-04-06","2026-04-05"]
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

    static let cleaning: [CleaningRecord] = [
        .init(date: "2026-04-19", range: "部屋", status: "通過", score: 5, rejected: false, comment: nil),
        .init(date: "2026-04-05", range: "共用エリア", status: "退回", score: nil, rejected: true, comment: "床が汚れている"),
    ]

    static let packages: [PackageItem] = [
        .init(id: 1, date: "2026-04-22", from: "Amazon", status: "待領", tracking: "JP12345"),
        .init(id: 2, date: "2026-04-18", from: "佐川", status: "領済", tracking: nil),
        .init(id: 3, date: "2026-04-10", from: "ヤマト", status: "領済", tracking: nil),
        .init(id: 4, date: "2026-04-05", from: "郵便局", status: "領済", tracking: nil),
    ]

    static let notifications: [NotificationItem] = [
        .init(id: 1, type: "宅配", title: "Amazon 荷物到着", time: "今日 14:20", body: "寮管理員室で受取り", unread: true),
        .init(id: 2, type: "申請", title: "外泊申請が承認されました", time: "昨日 16:30", body: "田中先生が承認しました", unread: true),
        .init(id: 3, type: "減点", title: "遅刻警告", time: "昨日 9:00", body: "今月の遅刻が 5 回に到達", unread: false),
        .init(id: 4, type: "活動", title: "明日 18:00 新入生歓迎会", time: "昨日", body: "食堂集合", unread: true),
        .init(id: 5, type: "リクエスト曲", title: "あなたの投稿曲が採用されました", time: "2 日前", body: "Lemon / 米津玄師", unread: false),
    ]

    static let applications: [ApplicationItem] = [
        .init(id: "a1", type: "stay", status: "pending", date: "2026-04-20", summary: "東京 · 2 泊 3 日"),
        .init(id: "a2", type: "other", status: "returned", date: "2026-04-05", summary: "共用エリア掃除"),
        .init(id: "a3", type: "holiday", status: "approved", date: "2026-04-15", summary: "茨城 · 帰省"),
        .init(id: "a4", type: "outing", status: "approved", date: "2026-04-02", summary: "駅前 · タクシー予約"),
        .init(id: "a5", type: "return", status: "approved", date: "2026-04-08", summary: "晩点呼 早帰"),
    ]

    // 実スクールバス時刻表（2026-04-29 水 GW外泊・帰省等 特別運行便パターン）
    // 詳細は DMSD/02_design/bus_schedule_real.md 参照
    static let buses: [BusLine] = [
        .init(time: "07:30", route: "高校棟 → 岡山駅西口", seats: "空きあり", next: true),
        .init(time: "10:10", route: "高校棟 → 金川駅",     seats: "空きあり", next: false),
        .init(time: "15:33", route: "金川駅 → 寮",         seats: "残 3",    next: false),
        .init(time: "17:02", route: "金川駅 → 寮",         seats: "残 5",    next: false),
    ]

    static let busNotice: (active: Bool, text: String) = (
        true,
        "4/29(水) GW外泊・帰省・買い物 特別運行便 · 乗車名簿に事前チェック"
    )

    // 完整巴士日程（DMSD/02_design/bus_schedule_real.md 対応 · 日別グループ）
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
            notice: nil,
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

    // 活動・行事（カレンダー表示用）· bus_schedule_real.md の行事日も連動
    static let events: [EventItem] = [
        .init(date: "2026-04-05", time: "08:30", title: "留4アクティビティ", place: "岡山城・後楽園", desc: "お花見弁当・岡山城見学・後楽園散策・さくらカーニバル。参加希望者は高野まで。"),
        .init(date: "2026-04-07", time: "15:33", title: "帰寮日", place: "金川駅・岡山駅西口", desc: "15:33 金川駅発 / 18:45 岡山駅西口発（寮行き）"),
        .init(date: "2026-04-08", time: "09:00", title: "始業式・新任式・高等部進級式", place: "本校", desc: ""),
        .init(date: "2026-04-09", time: "09:00", title: "入学式", place: "本校", desc: "家庭学習日 2①②③"),
        .init(date: "2026-04-10", time: "09:00", title: "春期課題考査", place: "本校", desc: "1〜③ + 新入生オリエンテーション"),
        .init(date: "2026-04-11", time: "08:30", title: "みつ元気プロジェクト", place: "御津公民館", desc: "戦略会議 9:45〜。特別運行便あり。"),
        .init(date: "2026-04-23", time: "18:00", title: "新入生歓迎会", place: "食堂", desc: "夕食後、軽食と自己紹介タイム"),
        .init(date: "2026-04-25", time: "10:00", title: "避難訓練", place: "寮ロビー集合", desc: "全員参加必須"),
        .init(date: "2026-04-26", time: "14:00", title: "茶道部体験", place: "和室", desc: "初心者歓迎"),
        .init(date: "2026-04-29", time: "07:30", title: "GW外泊・帰省・買い物", place: "特別運行便", desc: "7:30 高校棟→岡山駅西口 / 10:10 高校棟→金川駅 / 15:33,17:02 金川駅→寮"),
        .init(date: "2026-05-06", time: "09:20", title: "GW後帰寮日", place: "特別運行便", desc: "9:20,10:10 高校棟→金川駅 / 15:33 金川駅→寮 / 18:45 岡山駅西口→寮"),
        .init(date: "2026-05-16", time: "08:30", title: "みつ元気プロジェクト", place: "御津公民館", desc: "4/11 同パターン"),
        .init(date: "2026-05-23", time: "07:30", title: "音楽と青空市", place: "岡山市立御津公民館", desc: "基本ボランティア用。時間帯注意。"),
        .init(date: "2026-05-31", time: "06:40", title: "英検 第1回 一次試験", place: "会場", desc: "時程調整予定。級受験者 + 買い物希望者向け特別運行便あり。"),
    ]

    static let lost: [LostItem] = [
        .init(id: 1, title: "青い折りたたみ傘", place: "食堂", date: "04-21", color: "#3b82f6"),
        .init(id: 2, title: "黒の鍵", place: "玄関", date: "04-20", color: "#1f2937"),
        .init(id: 3, title: "赤のペンケース", place: "図書室", date: "04-18", color: "#ef4444"),
        .init(id: 4, title: "緑のノート", place: "食堂", date: "04-16", color: "#10b981"),
        .init(id: 5, title: "イヤホン (白)", place: "ロビー", date: "04-15", color: "#f3f4f6"),
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

    static let wall: [WallPost] = [
        .init(id: 1, author: "05号", time: "1時間前", text: "食堂のカレー美味しかった〜", likes: 12, comments: 3),
        .init(id: 2, author: "08号", time: "3時間前", text: "明日のバス、時間変更に注意!", likes: 5, comments: 1),
        .init(id: 3, author: "11号", time: "6時間前", text: "自習室の Wi-Fi 遅い気がする", likes: 8, comments: 6),
        .init(id: 4, author: "03号", time: "昨日", text: "部屋の電球が切れました。交換お願いします", likes: 2, comments: 4),
        .init(id: 5, author: "14号", time: "2 日前", text: "茶道部の体験会参加しました、楽しかった!", likes: 15, comments: 2),
    ]

    static let suggestions: [SuggestItem] = [
        .init(id: 1, q: "食堂のメニューに野菜料理を増やしてほしい", a: "来月から週 2 回、野菜定食を追加予定です。", date: "2026-04-10"),
        .init(id: 2, q: "Wi-Fi のルーター増設お願いします", a: "4 階・5 階に追加設置予定（5 月中）。", date: "2026-04-08"),
        .init(id: 3, q: "洗濯機の台数を増やしてほしい", a: "来年度の予算で検討します。", date: "2026-04-02"),
    ]
}
