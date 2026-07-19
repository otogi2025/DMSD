package jp.tomoshibi.android.data.network.endpoints

import jp.tomoshibi.android.data.network.ApiClient
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// MiscRequestsAPI.kt
// data/network/endpoints — 杂项申请（修繕 / 来訪者 / 代理受取）endpoint 包装
//
// 对齐 iOS Endpoints/MiscRequestsAPI.swift。
// 后端路由 app/routers/misc_requests.py（prefix /api/v1/misc-requests）：
//   POST /api/v1/misc-requests  提出（kind: repair / guest / proxy_receipt）
//
// 学生 app 当前只用提出；GET /mine 与 PATCH withdraw iOS 也未包，此处不额外做。
// UI「代理受取 · 不在時の荷物代理受取」对应后端 kind="proxy_receipt"。

object MiscRequestsAPI {
    // 杂项申请提出。
    suspend fun create(body: MiscRequestBody): MiscRequestOut = ApiClient.post("/api/v1/misc-requests", body)
}

// POST /api/v1/misc-requests 请求 body（对齐后端 MiscRequestCreateIn）。
@Serializable
data class MiscRequestBody(
    val kind: String, // "repair" | "guest" | "proxy_receipt"
    val subject: String,
    val detail: String? = null,
    @SerialName("target_date") val targetDate: String? = null, // "yyyy-MM-dd"
)

// 杂项申请响应（对齐后端 MiscRequestOut）。提出后只关心成功与否。
@Serializable
data class MiscRequestOut(
    val id: String,
    @SerialName("student_id") val studentId: String,
    val kind: String,
    val subject: String,
    val detail: String? = null,
    @SerialName("target_date") val targetDate: String? = null,
    val status: String, // "pending" | "confirmed" | "withdrawn"
    @SerialName("created_at") val createdAt: String,
)
