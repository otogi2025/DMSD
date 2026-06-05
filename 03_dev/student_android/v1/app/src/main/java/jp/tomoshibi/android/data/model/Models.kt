package jp.tomoshibi.android.data.model

import kotlinx.serialization.Serializable

// 数据模型 — 对应 React app-shell.jsx DEFAULT_STATE 各字段
// kotlinx.serialization 给 DataStore JSON 持久化用

@Serializable
data class User(
    val name: String = "",
    val kana: String = "",
    val email: String = "",
    val dorm: String = "男寮",
    val room: String = "M101",
    val avatar: String = "リ",
    // iOS 060218 编码 = 学年(06) + 組(02) + 番号(18)
    val studentNo: String = "060218",
    val gradeClass: String = "高3B組 18番",
    val category: String = "一般寮生", // 一般寮生 / 留学生 / サッカー部
    val phone: String = "090-0000-0000",
    val birthDate: String = "2006-10-14", // 生年月日
    val gender: String = "男", // 性別
    val isStudyTarget: Boolean = false, // 晚自习（夜間学習）对象，false=対象外
)

enum class ApplicationStatus { PENDING, APPROVED, RETURNED, REJECTED }

@Serializable
data class Application(
    val id: String,
    val kind: String, // 外泊 / 外出 / 帰省 / 帰国 / 早帰 / 修繕 / 代理受取 / 来訪者 / その他 / 学習
    val dest: String,
    val from: String, // ISO date string
    val to: String,
    val status: ApplicationStatus,
    val reason: String,
    val createdAt: String,
)

@Serializable
data class RollCall(
    val id: String,
    val ts: Long, // unix millis
    val status: String, // ok / late / miss
    val method: String, // nfc / manual
)

@Serializable
data class Deduction(
    val id: String,
    val date: String,
    val points: Double,
    val reason: String,
    val tier: Int, // 处罚档（§862 月累计）：0=无 / 4=罚扫(月累计≥4) / 8=禁足(月累计≥8)
)

@Serializable
data class Notification(
    val id: String,
    val tag: String, // 点呼 / 申請 / お知らせ / 宅配 / 減点 / 活動 / リクエスト
    val title: String,
    val body: String,
    val ts: String, // 显示用文本（"今日 18:30"）
    val read: Boolean = false,
)

@Serializable
data class MusicRequest(
    val id: String,
    val title: String,
    val artist: String,
    val votes: Int = 0,
)

@Serializable
data class LostItem(
    val id: String,
    val label: String,
    val colorHex: String, // 用 hex string 序列化 — Compose 侧 Color(0xFF + 后 6 位) parse
)

@Serializable
data class EventItem(
    val date: String, // "04-05"
    val title: String,
    val time: String, // "08:30"
)

@Serializable
data class PackageItem(
    val id: Int,
    val date: String, // "本日" / "04-22"
    val from: String, // 发货方（Amazon / 佐川急便 等）
    val status: String, // 待領 / 領済
    val tracking: String? = null, // 追跡番号，可空
)

// 点呼履历单条 — 对应 iOS SeedModels.swift RollcallEntry（个人页「点呼履歴」屏用）
@Serializable
data class RollcallEntry(
    val id: String, // "RC-0405-AM"
    val date: String, // "2026-04-05"
    val session: String, // 朝点呼 / 晩点呼
    val status: String, // 時間内 / 遅刻 / 欠席
    val method: String, // NFC / ―（欠席时无方式）
)

// 体调报告履历单条 — 对应 iOS SeedModels.swift HealthRecord
@Serializable
data class HealthRecord(
    val id: String,
    val date: String, // "2026-04-14"
    val symptom: String, // 症状（頭痛 / 腹痛）
    val tempC: Double? = null, // 体温，可空（无温度时不显）
    val note: String? = null, // 备注，可空
)

// 扫除提出履历单条 — 对应 iOS SeedModels.swift CleaningRecord
@Serializable
data class CleaningRecord(
    val id: String,
    val date: String, // "2026-04-19"
    val scope: String, // 范围（「部屋」/「共用エリア」）
    val status: String, // 通過 / 退回
    val score: Int? = null, // 分数，可空（退回时无分）
    val comment: String? = null, // 退回评语，可空
)

enum class ThemeMode { LIGHT, DARK }

// 点呼状态机 — 对应 iOS HomeStubs.swift 的 4 态 hero
enum class RollState { IDLE, ACTIVE, ABSENT, DONE }

// 学習状态机 — 对应 iOS Home long-press 切换
enum class StudyState { OFF, UPCOMING, ACTIVE }

// AppState — 对应 React StoreProvider state，整体序列化进 DataStore
@Serializable
data class AppState(
    val authed: Boolean = false,
    val onboarded: Boolean = false,
    val user: User = User(),
    val themeMode: ThemeMode = ThemeMode.LIGHT,
    val hueOffset: Int = 0,
    val fontScale: Float = 1.0f,
    // 点呼实时状态（demo / Stage 1 加 cycle）
    val rollState: RollState = RollState.IDLE,
    val rollCountdownSec: Int = 170,
    val checkinAt: String? = null,
    val studyState: StudyState = StudyState.OFF,
    val applications: List<Application> = emptyList(),
    val rollCalls: List<RollCall> = emptyList(),
    val deductions: List<Deduction> = emptyList(),
    val notifications: List<Notification> = emptyList(),
    val musicVotes: Map<String, String> = emptyMap(), // id -> 'up'
    val musicRequests: List<MusicRequest> = emptyList(),
    val lostFoundClaims: Map<String, Boolean> = emptyMap(),
)
