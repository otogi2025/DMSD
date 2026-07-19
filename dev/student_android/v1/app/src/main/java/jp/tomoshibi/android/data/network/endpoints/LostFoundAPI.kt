package jp.tomoshibi.android.data.network.endpoints

import jp.tomoshibi.android.data.network.ApiClient
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// LostFoundAPI.kt
// data/network/endpoints — 遗失物（UI「遺失物」）endpoint 包装
//
// 对齐 iOS Endpoints/LostFoundAPI.swift。
// 后端路由 app/routers/lost_found.py（prefix /api/v1/lost-found）：
//   POST  /api/v1/lost-found              投稿
//   GET   /api/v1/lost-found              一览（新→旧；不传 status=全部）
//   PATCH /api/v1/lost-found/{id}/resolve 标为已解决（仅投稿者本人）

object LostFoundAPI {
    // 遗失物投稿。
    suspend fun create(body: LostFoundBody): LostFoundOut = ApiClient.post("/api/v1/lost-found", body)

    // 遗失物一览（后端按新→旧返回；不传 status = 全部）。
    suspend fun list(): List<LostFoundOut> = ApiClient.get("/api/v1/lost-found")

    // 标为已解决（仅投稿者本人）。非本人 403 / 已 resolved 409。
    suspend fun resolve(id: String): LostFoundOut = ApiClient.patchNoBody("/api/v1/lost-found/$id/resolve")
}

// POST /api/v1/lost-found 请求 body（对齐后端 LostFoundCreateIn）。
@Serializable
data class LostFoundBody(
    @SerialName("post_type") val postType: String, // "found" | "lost"
    @SerialName("item_name") val itemName: String,
    val description: String? = null,
    val location: String? = null,
)

// 遗失物投稿（对齐后端 LostFoundOut）。
@Serializable
data class LostFoundOut(
    val id: String,
    @SerialName("student_id") val studentId: String,
    @SerialName("post_type") val postType: String, // "found" | "lost"
    @SerialName("item_name") val itemName: String,
    val description: String? = null,
    val location: String? = null,
    val status: String, // "open" | "resolved"
    @SerialName("created_at") val createdAt: String,
    @SerialName("resolved_at") val resolvedAt: String? = null,
)
