package jp.tomoshibi.android.data.network.endpoints

import jp.tomoshibi.android.data.network.ApiClient
import jp.tomoshibi.android.data.network.StudentNotificationFeedOut
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// StudentNotificationsAPI.kt
// data/network/endpoints — 学生通知中心 feed endpoint 包装
//
// 对齐 iOS Endpoints/StudentNotificationsAPI.swift。
// 对应后端 spec §7.13.1（routers/student_notifications.py）：
//   GET  /api/v1/student/notifications      — 拉通知 feed
//   POST /api/v1/student/notifications/read — 标记已读（幂等，返 204）

object StudentNotificationsAPI {
    // 拉学生通知 feed（items + 未読数）。
    suspend fun feed(): StudentNotificationFeedOut = ApiClient.get("/api/v1/student/notifications")

    // 标记一条通知已读。后端返 204 → 用 postNoContent。
    // kind ∈ {"announcement","bus","event"}；refId = 该条对应实体的 id。
    suspend fun markRead(
        kind: String,
        refId: String,
    ) {
        val body = MarkReadBody(kind = kind, refId = refId)
        ApiClient.postNoContent("/api/v1/student/notifications/read", body)
    }

    @Serializable
    private data class MarkReadBody(
        val kind: String,
        @SerialName("ref_id") val refId: String,
    )
}
