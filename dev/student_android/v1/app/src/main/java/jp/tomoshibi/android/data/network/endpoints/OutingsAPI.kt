package jp.tomoshibi.android.data.network.endpoints

import jp.tomoshibi.android.data.network.ApiClient
import jp.tomoshibi.android.data.network.StudentBrief
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// OutingsAPI.kt
// data/network/endpoints — 外出申请（当天回寮、单一老师确认）endpoint 包装
//
// 对齐 iOS Endpoints/OutingsAPI.swift。
// 后端路由 app/routers/outings.py（prefix /api/v1/outings）。
// 跟出寮届（applications）的区别：不过夜 / 没有多级审查 / 一名老师点「確認」即可。
//
// 2026-07-22 起改事后确认制：学生提交即生效可直接出门，老师点「確認」只是事后留记录、
// 不是放行开关；老师仍可「却下」（只发通知 + 留记录，不要求学生立刻回寮）。
// 提交侧新增闸：当月扣分 ≥8 分（外出禁止 / 禁足）的学生 POST 会被后端挡回 422 OUTING_BANNED。

object OutingsAPI {
    // 外出申请提出。
    suspend fun create(body: OutingCreateBody): OutingOut = ApiClient.post("/api/v1/outings", body)

    // 我的外出申请一览（最近优先）。
    suspend fun listMine(): List<OutingOut> = ApiClient.get("/api/v1/outings/mine")

    // 外出申请详情。
    suspend fun detail(id: String): OutingOut = ApiClient.get("/api/v1/outings/$id")

    // 撤回自己 pending 的外出申请（无 body）。
    suspend fun withdraw(id: String): OutingOut = ApiClient.patchNoBody("/api/v1/outings/$id/withdraw")
}

// POST /outings 请求体（对齐后端 schemas.OutingCreateIn）。
@Serializable
data class OutingCreateBody(
    @SerialName("outing_date") val outingDate: String, // "2026-06-05"（必填）
    val destination: String? = null,
    @SerialName("leave_time") val leaveTime: String? = null, // "HH:mm"
    @SerialName("return_time") val returnTime: String? = null,
    @SerialName("taxi_reservation_time") val taxiReservationTime: String? = null,
    val reason: String? = null,
)

// 外出申请查询返回（对齐后端 schemas.OutingOut）。
// status 保留裸 String（不转 enum），防后端新增值时解码崩。
@Serializable
data class OutingOut(
    val id: String,
    @SerialName("student_id") val studentId: String,
    val student: StudentBrief? = null,
    @SerialName("outing_date") val outingDate: String,
    val destination: String? = null,
    @SerialName("leave_time") val leaveTime: String? = null,
    @SerialName("return_time") val returnTime: String? = null,
    @SerialName("taxi_reservation_time") val taxiReservationTime: String? = null,
    val reason: String? = null,
    val status: String, // "pending" | "approved" | "rejected" | "withdrawn"
    @SerialName("submitted_at") val submittedAt: String,
    @SerialName("withdrawn_at") val withdrawnAt: String? = null,
    // confirmed_* 三个字段语义是「処理した先生 / 処理時刻」——
    // status=approved 时是确认者、status=rejected 时是却下者（后端 schemas.OutingOut 同一套字段共用）。
    // 所以显示文案必须按 status 分支（approved →「確認 · ○○ 先生」/ rejected →「却下 · ○○ 先生」），
    // 不能一律写「確認 · ○○ 先生」。
    @SerialName("confirmed_by_teacher_id") val confirmedByTeacherId: String? = null,
    @SerialName("confirmed_by_name") val confirmedByName: String? = null,
    @SerialName("confirmed_at") val confirmedAt: String? = null,
    // 却下理由 — 只在 status=rejected 时可能有值；老师没填理由时仍是 null。
    @SerialName("reject_reason") val rejectReason: String? = null,
)
