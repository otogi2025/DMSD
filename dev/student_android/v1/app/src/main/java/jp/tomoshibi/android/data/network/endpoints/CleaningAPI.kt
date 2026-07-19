package jp.tomoshibi.android.data.network.endpoints

import jp.tomoshibi.android.data.network.ApiClient
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// CleaningAPI.kt
// data/network/endpoints — 罚扫（罰則清掃）履历 endpoint 包装
//
// 对齐 iOS Endpoints/CleaningAPI.swift。
// 后端路由 app/routers/cleaning.py（prefix /api/v1/cleaning）：
//   GET /api/v1/cleaning/me   学生查自己的罚扫安排 + 检查结果（按计划时刻倒序）

object CleaningAPI {
    // 我的罚扫提出履历（按计划时刻倒序，后端排好）。
    suspend fun listMine(): List<CleaningAssignmentOut> = ApiClient.get("/api/v1/cleaning/me")
}

// GET /cleaning/me 返回的单条罚扫安排（对齐后端 schemas.CleaningAssignmentOut）。
@Serializable
data class CleaningAssignmentOut(
    val id: String,
    @SerialName("student_id") val studentId: String,
    val area: String, // 清扫地点（老师自由文本，如「廊下 2F」）
    @SerialName("scheduled_at") val scheduledAt: String, // 罚扫预定时刻（带时区 datetime）
    val status: String, // "assigned" | "done" | "passed" | "failed" | "skipped"
    @SerialName("failure_reason") val failureReason: String? = null, // 却下（failed）理由
)

// 主页「下次罚扫」小卡展示用（纯前端结构，非网络响应）。
data class NextCleaningInfo(
    val dateText: String, // "5月20日"
    val timeText: String, // "19時"
    val area: String, // "廊下 2F"
)
