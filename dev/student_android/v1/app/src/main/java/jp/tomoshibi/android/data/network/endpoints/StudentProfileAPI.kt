package jp.tomoshibi.android.data.network.endpoints

import jp.tomoshibi.android.data.network.ApiClient
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// StudentProfileAPI.kt
// data/network/endpoints — 学生个人 profile 聚合查询 endpoint 包装
//
// 对齐 iOS Endpoints/StudentProfileAPI.swift。
// 后端路由 app/routers/student_profile.py：
//   GET /api/v1/students/{id}/profile?limit=  学生本人可查自己
//
// 学生 app 只取两块：点呼事件（点呼履历）+ 减点事件（減点明細）。
// 其余字段（applications 等）靠 ignoreUnknownKeys 跳过。

object StudentProfileAPI {
    // 拉学生本人 profile。limit 默认 100（覆盖 12 个月图表用更长历史）。
    suspend fun profile(
        studentId: String,
        limit: Int = 100,
    ): StudentProfileOut = ApiClient.get("/api/v1/students/$studentId/profile?limit=$limit")
}

// 点呼事件 entry（对齐后端 ProfileRollCallEntry）。
@Serializable
data class ProfileRollCallEntry(
    val id: String,
    @SerialName("session_id") val sessionId: String,
    @SerialName("session_type") val sessionType: String, // "morning" | "evening"
    @SerialName("base_status") val baseStatus: String, // "init" | "present" | "late" | "absent" | "exempt_range"
    @SerialName("status_source") val statusSource: String,
    @SerialName("checked_in_at") val checkedInAt: String,
    @SerialName("scheduled_window_start_at") val scheduledWindowStartAt: String? = null,
    @SerialName("scheduled_on_time_end_at") val scheduledOnTimeEndAt: String? = null,
)

// 减点事件 entry（对齐后端 ProfileDemeritEntry）。
@Serializable
data class ProfileDemeritEntry(
    val id: String,
    @SerialName("source_type") val sourceType: String,
    val points: Double,
    val reason: String,
    val month: String, // "yyyy-MM"
    @SerialName("created_at") val createdAt: String,
)

// GET /students/{id}/profile 聚合响应（只解码用得到的两块）。
@Serializable
data class StudentProfileOut(
    @SerialName("rollcall_events") val rollcallEvents: List<ProfileRollCallEntry>,
    @SerialName("demerit_events") val demeritEvents: List<ProfileDemeritEntry>,
)
