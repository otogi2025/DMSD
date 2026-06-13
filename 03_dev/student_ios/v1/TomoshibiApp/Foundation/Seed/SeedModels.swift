// SeedModels.swift · 14 数据结构 · 对等 phaseB_src c281cafa SEED

import Foundation

struct User: Hashable {
    var account: String // 年级码(2) + 出席番号(2) · 高3 18号 → "0618"
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
    var grade: String = "高3"
    var classSuffix: String = "B"
    var seatNo: Int = 18
    /// 学習対象学生 flag (system_features §7.3 — 中学全员 / 高中考试不合格者). demo seed = true 让所有学習 UI 可见
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
    let session: String // 朝点呼 / 晩点呼（保留日语原词）
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

struct PackageItem: Hashable, Identifiable {
    let id: Int
    let date: String
    let from: String
    let status: String // 待領 / 領済
    let tracking: String?
}

struct NotificationItem: Hashable, Identifiable {
    let id: Int
    let type: String // UI 分类标签：「宅配」/「申請」/「減点」/「活動」/「リクエスト曲」
    let title: String
    let time: String
    let body: String
    let unread: Bool
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
    var id: String {
        date + title
    }

    let date: String
    let time: String
    let title: String
    let place: String
    let desc: String
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
