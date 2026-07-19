package jp.tomoshibi.android.data.network.endpoints

import jp.tomoshibi.android.data.network.ApiClient
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// SongsAPI.kt
// data/network/endpoints — 点歌（UI「リクエスト曲」）endpoint 包装
//
// 对齐 iOS Endpoints/SongsAPI.swift。
// 后端路由 app/routers/songs.py（prefix /api/v1/songs）：
//   POST /api/v1/songs  投稿（dorm_unit 后端按登录学生寮自动取）
//   GET  /api/v1/songs  一览（新→旧；学生不传 dorm=全部）
//
// 注意：data/model 里的 SongItem（含 by/up/down）是纯 UI mock，跟本响应形状不一致，接线时勿直接塞。

object SongsAPI {
    // 点歌投稿。
    suspend fun create(body: SongRequestBody): SongRequestOut = ApiClient.post("/api/v1/songs", body)

    // 点歌一览（后端按投稿顺新→旧返回）。
    suspend fun list(): List<SongRequestOut> = ApiClient.get("/api/v1/songs")
}

// POST /api/v1/songs 请求 body（对齐后端 SongRequestCreateIn）。
@Serializable
data class SongRequestBody(
    @SerialName("song_title") val songTitle: String,
    val artist: String? = null,
    val note: String? = null,
)

// 点歌投稿响应（对齐后端 SongRequestOut）。无投稿者名 / 賛否票数（投票 v1.1）。
@Serializable
data class SongRequestOut(
    val id: String,
    @SerialName("student_id") val studentId: String,
    @SerialName("dorm_unit") val dormUnit: Int,
    @SerialName("song_title") val songTitle: String,
    val artist: String? = null,
    val note: String? = null, // 投稿理由
    @SerialName("created_at") val createdAt: String,
)
