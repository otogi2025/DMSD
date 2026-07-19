package jp.tomoshibi.android.data.network.endpoints

import jp.tomoshibi.android.data.network.ApiClient
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// RollCallAPI.kt
// data/network/endpoints — 点呼（roll call = 宿舍夜间点名）相关 endpoint 包装。
//
// 1:1 对齐 iOS RollCallAPI.swift。
//
// 注意：RollCallCheckinBody / RollCallEventOut / MyRollCallTodaySession /
// RollCallReportBody / RollCallReportOut 在 iOS 里也写在 RollCallAPI.swift 内
// （不在 NetworkModels），这里照搬同样布局。

object RollCallAPI {
    // POST /api/v1/rollcall/sessions/:id/checkins — 学生签到入口。
    // ⚠️ 架构反转后（2026-06-02）学生 app 弃用本方法：手机改写 ST25DV 邮箱，
    // 由点呼机 POST 后端。保留代码（可能给老师代点 / 路径 A 补录用），勿删。
    suspend fun checkin(
        sessionId: String,
        body: RollCallCheckinBody,
    ): RollCallEventOut = ApiClient.post("/api/v1/rollcall/sessions/$sessionId/checkins", body)

    // GET /api/v1/rollcall/me/today
    // 学生查今天自己所属寮的点呼场次 + 自己在每场的签到状态。
    // 四个 scheduled_* 时间窗喂给 RollStateMachine.decide；空数组 = 本日无我寮点呼。
    suspend fun myToday(): List<MyRollCallTodaySession> = ApiClient.get("/api/v1/rollcall/me/today")
}

// GET /api/v1/rollcall/me/today 单条响应（对齐 backend MyRollCallTodaySession）。
@Serializable
data class MyRollCallTodaySession(
    @SerialName("session_id") val sessionId: String,
    @SerialName("session_type") val sessionType: String, // morning / evening
    @SerialName("day_type") val dayType: String, // weekday / weekend_holiday
    @SerialName("session_status") val sessionStatus: String, // draft / running / ended
    @SerialName("scheduled_window_start_at") val scheduledWindowStartAt: String,
    @SerialName("scheduled_on_time_end_at") val scheduledOnTimeEndAt: String,
    @SerialName("scheduled_late_end_at") val scheduledLateEndAt: String,
    @SerialName("scheduled_auto_end_at") val scheduledAutoEndAt: String,
    @SerialName("my_status") val myStatus: String? = null, // nil = 还没签到
    @SerialName("my_checked_in_at") val myCheckedInAt: String? = null,
)

// POST /api/v1/rollcall/sessions/:id/checkins 请求 body。
@Serializable
data class RollCallCheckinBody(
    @SerialName("card_uid") val cardUid: String? = null,
    @SerialName("student_id") val studentId: String? = null,
    @SerialName("idempotency_key") val idempotencyKey: String? = null,
    @SerialName("status_source") val statusSource: String, // "auto_nfc" / "manual_checkin"
    @SerialName("ts_local") val tsLocal: String? = null,
    @SerialName("path_hint") val pathHint: String? = null, // "A" / "B" / "manual"
)

// POST /api/v1/rollcall/sessions/:id/checkins 响应。
@Serializable
data class RollCallEventOut(
    val id: String,
    @SerialName("student_id") val studentId: String,
    @SerialName("base_status") val baseStatus: String,
    @SerialName("status_source") val statusSource: String,
    @SerialName("checked_in_at") val checkedInAt: String,
    @SerialName("path_type") val pathType: String? = null,
)

// ============================================================
// 点呼时学生上报（体调不良 / 当次欠席 / 其他）— POST /rollcall/reports
// ============================================================

object RollCallReportsAPI {
    // 点呼时上报。kind 区分 health / absence / other；sessionId 学生端无缓存 → 恒 null。
    suspend fun create(
        kind: String,
        body: String,
        sessionId: String? = null,
    ): RollCallReportOut {
        val payload = RollCallReportBody(kind = kind, body = body, sessionId = sessionId)
        return ApiClient.post("/api/v1/rollcall/reports", payload)
    }

    // GET /api/v1/rollcall/reports/mine —— 自己提交过的全部上报（含三 kind，后端倒序）。
    // 「体調報告履歴」只显示 health → 调用方自行 filter。
    suspend fun listMine(): List<RollCallReportOut> = ApiClient.get("/api/v1/rollcall/reports/mine")
}

@Serializable
data class RollCallReportBody(
    val kind: String, // "health" | "absence" | "other"
    val body: String, // 自由文本 1~2000 字
    @SerialName("session_id") val sessionId: String? = null,
)

@Serializable
data class RollCallReportOut(
    val id: String,
    @SerialName("student_id") val studentId: String,
    @SerialName("session_id") val sessionId: String? = null,
    val kind: String,
    val body: String,
    @SerialName("created_at") val createdAt: String,
    @SerialName("resolved_at") val resolvedAt: String? = null,
    @SerialName("resolved_by_teacher_id") val resolvedByTeacherId: String? = null,
)
