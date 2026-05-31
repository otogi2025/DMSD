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
    val category: String = "一般寮生",   // 一般寮生 / 留学生 / サッカー部
    val phone: String = "090-0000-0000"
)

enum class ApplicationStatus { PENDING, APPROVED, RETURNED, REJECTED }

@Serializable
data class Application(
    val id: String,
    val kind: String,           // 外泊 / 外出 / 帰省 / 帰国 / 早帰 / 修繕 / 代理受取 / 来訪者 / その他 / 学習
    val dest: String,
    val from: String,           // ISO date string
    val to: String,
    val status: ApplicationStatus,
    val reason: String,
    val createdAt: String
)

@Serializable
data class RollCall(
    val id: String,
    val ts: Long,               // unix millis
    val status: String,         // ok / late / miss
    val method: String          // nfc / manual
)

@Serializable
data class Deduction(
    val id: String,
    val date: String,
    val points: Double,
    val reason: String,
    val tier: Int               // 4 (罚扫) or 8 (禁足)
)

@Serializable
data class Notification(
    val id: String,
    val tag: String,            // 点呼 / 申請 / お知らせ / 宅配 / 減点 / 活動 / リクエスト
    val title: String,
    val body: String,
    val ts: String,             // 显示用文本（"今日 18:30"）
    val read: Boolean = false
)

@Serializable
data class MusicRequest(
    val id: String,
    val title: String,
    val artist: String,
    val votes: Int = 0
)

@Serializable
data class LostItem(
    val id: String,
    val label: String,
    val colorHex: String        // 用 hex string 序列化 — Compose 侧 Color(0xFF + 后 6 位) parse
)

@Serializable
data class EventItem(
    val date: String,           // "04-05"
    val title: String,
    val time: String            // "08:30"
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
    val musicVotes: Map<String, String> = emptyMap(),       // id -> 'up'
    val musicRequests: List<MusicRequest> = emptyList(),
    val lostFoundClaims: Map<String, Boolean> = emptyMap(),
    val feedback: List<String> = emptyList()                // 简化为 JSON string 列表
)
