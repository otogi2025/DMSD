// SeedModels.swift · 14 数据结构 · 对等 phaseB_src c281cafa SEED

import Foundation

struct User: Hashable {
    var account: String // 年级码(2) + 班组码(2) + 出席番号(2) · 高3 B組 18号 → "060218"
    var name: String
    var nameKana: String
    var birth: String
    var age: Int
    var gender: String
    var dorm: String
    var room: String
    var category: String
    var email: String
    var phone: String
    var avatar: String
    var points: Double
    var lateCount: Int
    var absentCount: Int
    /// 罚扫对象 flag — summary.needs_cleaning（后端实时算 total_points>=4）。占位/未登录 = false。
    var needsCleaning: Bool = false
    var grade: String = "高3"
    var classSuffix: String = "B"
    var seatNo: Int = 18
    /// 夜学習対象学生 flag (system_features §7.3 — 中学全员 / 高中考试不合格者). demo seed = true 让所有学習 UI 可见
    var isStudyTarget: Bool = true
    /// 留学生 flag (system_features §8.1 / Q11 — 自己申报). 演示用户「リュウ イヒ」= 留学生（承认链为 5 个角色）
    var isOverseas: Bool = true

    /// 生产构建已登录但还没拉到本人资料时的空白占位（ios⑥ 上线缺口）：
    /// 字符串字段显「—」，数值字段填 0（view 层靠 AppStore.profileIsPlaceholder 把数值也显成「—」）。
    /// 防生产环境回退到演示假人「リュウ イヒ」(4.5 点) 泄漏给真实用户。
    static let placeholder = User(
        account: "—", name: "—", nameKana: "—", birth: "—", age: 0,
        gender: "—", dorm: "—", room: "—", category: "—", email: "—",
        phone: "—", avatar: "—", points: 0, lateCount: 0, absentCount: 0
    )
}

struct PointRecord: Hashable, Identifiable {
    var id: String {
        "\(date):\(session):\(kind)"
    }

    let date: String
    let session: String // 朝点呼 / 夜点呼（保留日语原词）
    let kind: String // 遅刻 / 欠席（保留日语原词）
    let val: Double
}

struct RollcallEntry: Hashable, Identifiable {
    var id: String {
        "\(date):\(session)"
    }

    let date: String
    let session: String
    let state: String // 時間内 / 遅刻 / 欠席（保留日语原词）
    let method: String // NFC / ―
}

struct HealthRecord: Hashable, Identifiable {
    var id: String {
        date
    }

    let date: String
    let sym: String
    let temp: Double?
    let note: String
}

/// 罚扫（罰則清掃）演示假数据行（#if DEMO 时 SEED.cleaning 用）。
/// 改动1：罚扫带时刻 → 加 time 字段；dateLabel/timeLabel 把 "2026-05-20"+"19:00" → "5月20日"/"19時"。
struct CleaningRecord: Hashable, Identifiable {
    var id: String {
        "\(date):\(range)"
    }

    let date: String // "2026-05-20"（yyyy-MM-dd）
    let time: String // "19:00"（HH:mm）— 改动1：罚扫带时刻
    let range: String // 地点（自由文本）
    let status: String // 状态值「通過」/「差し戻し」/「未完了」等（演示日语直接写）
    let score: Int?
    let rejected: Bool
    let comment: String?

    /// "5月20日" — 小卡/履历展示
    var dateLabel: String {
        let f = DateFormatter()
        f.locale = Locale(identifier: "ja_JP")
        f.dateFormat = "yyyy-MM-dd"
        f.timeZone = TimeZone(identifier: "Asia/Tokyo")
        guard let d = f.date(from: date) else { return date }
        f.dateFormat = "M月d日"
        return f.string(from: d)
    }

    /// "19時30分" — 小卡/履历展示（HH:mm 带分钟，与正式版 jstHour 口径一致）
    var timeLabel: String {
        let comps = time.split(separator: ":")
        let h = comps.first.flatMap { Int($0) } ?? 0
        let m = comps.count > 1 ? String(comps[1]) : "00"
        return "\(h)時\(m)分"
    }
}

struct PackageItem: Hashable, Identifiable {
    let id: Int
    let date: String
    let from: String
    let status: String // 状态值：「受取待ち」/「受取済」
    let tracking: String?
}

struct NotificationItem: Hashable, Identifiable {
    let id: Int
    let type: String // UI 分类标签：「宅配」/「申請」/「減点」/「活動」/「リクエスト曲」/「お知らせ」/「バス」/「カレンダー」
    let title: String
    let time: String
    let body: String
    let unread: Bool
    // 后端学生通知 feed 来源标记（2026-06-15）—— 点卡片标已读用。
    // push / 宅配 / SEED 等非 feed 来源为 nil（带默认值 → 既有初始化点不受影响）。
    var kind: String? = nil // "announcement" | "bus" | "event"
    var refId: UUID? = nil // 对应实体 id
}

struct ApplicationItem: Hashable, Identifiable {
    let id: String
    let type: String // stay / holiday / outing / return / repair / parcel / guest / other（申请类型）
    let status: String // pending / approved / returned / withdrawn / draft / rejected（审批状态）
    let date: String
    let summary: String
}

struct BusLine: Hashable, Identifiable {
    var id: String {
        time + route
    }

    let time: String
    let route: String
    let seats: String
    let next: Bool
}

/// 巴士时刻表 · 按日分组（对应 bus_schedule_real.md）
struct BusDaySchedule: Hashable, Identifiable {
    var id: String {
        date
    }

    let date: String // "2026-04-29"
    let weekday: String // "水"
    let label: String // "GW外泊・帰省・買い物"
    let notice: String? // 特別運行便 note / null
    let lines: [BusLine]
}

struct EventItem: Hashable, Identifiable {
    let id: String
    let date: String
    let time: String
    let title: String
    let place: String
    let desc: String

    /// ios#67：默认 id = date+title（SEED 种子数据无 id 时兜底）；后端映射(EventMapper)传入真实
    /// EventOut.id.uuidString，保证同日同名事件不碰撞。保留 date/title 兜底让所有既有 EventItem(...) 调用不变。
    init(id: String? = nil, date: String, time: String, title: String, place: String, desc: String) {
        self.id = id ?? (date + title)
        self.date = date
        self.time = time
        self.title = title
        self.place = place
        self.desc = desc
    }
}

struct LostItem: Hashable, Identifiable {
    let id: Int
    let title: String
    let place: String
    let date: String
    let color: String // hex
}

struct SongItem: Hashable, Identifiable {
    let id: Int
    let title: String
    let artist: String
    let by: String
    let up: Int
    let down: Int
}
