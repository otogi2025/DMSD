package jp.tomoshibi.android.data.model

import kotlinx.serialization.Serializable

// 数据模型 — 对应 React app-shell.jsx DEFAULT_STATE 各字段
// kotlinx.serialization 给 DataStore JSON 持久化用

@Serializable
data class User(
    val name: String = "",
    val kana: String = "",
    val email: String = "",
    val dorm: String = "A棟",
    val room: String = "203",
    val avatar: String = "春"
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
    val tag: String,            // 点呼 / 申請 / お知らせ / 宅配 / 減点 / 活動
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

enum class ThemeMode { LIGHT, DARK }

// AppState — 对应 React StoreProvider state，整体序列化进 DataStore
@Serializable
data class AppState(
    val authed: Boolean = false,
    val onboarded: Boolean = false,
    val user: User = User(),
    val themeMode: ThemeMode = ThemeMode.LIGHT,
    val hueOffset: Int = 0,
    val fontScale: Float = 1.0f,
    val applications: List<Application> = emptyList(),
    val rollCalls: List<RollCall> = emptyList(),
    val deductions: List<Deduction> = emptyList(),
    val notifications: List<Notification> = emptyList(),
    val musicVotes: Map<String, String> = emptyMap(),       // id -> 'up'
    val musicRequests: List<MusicRequest> = emptyList(),
    val lostFoundClaims: Map<String, Boolean> = emptyMap(),
    val feedback: List<String> = emptyList()                // 简化为 JSON string 列表
)
