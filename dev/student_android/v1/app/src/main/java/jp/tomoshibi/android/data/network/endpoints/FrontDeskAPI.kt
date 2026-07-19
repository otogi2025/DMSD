package jp.tomoshibi.android.data.network.endpoints

import jp.tomoshibi.android.data.network.ApiClient
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// FrontDeskAPI.kt
// data/network/endpoints — 前台（宅配 / 荷物）endpoint 包装
//
// 对齐 iOS AppStore.loadMyPackages（GET /api/v1/front-desk/mine）。
// 后端路由 app/routers/front_desk.py：
//   GET /api/v1/front-desk/mine  当前登录学生自己的包裹一览

object FrontDeskAPI {
    // 我的包裹（未取 / 已取 / 过期等全量；按后端顺序返回）。
    suspend fun listMine(): List<FrontDeskItemOut> = ApiClient.get("/api/v1/front-desk/mine")
}

// GET /front-desk/mine 单条（对齐后端 FrontDeskItemOut / iOS FrontDeskItemBrief）。
@Serializable
data class FrontDeskItemOut(
    val id: String,
    val kind: String,
    val description: String,
    val location: String? = null,
    @SerialName("item_count") val itemCount: Int = 1,
    val status: String, // pending / notified / picked_up / expired / discarded
    @SerialName("created_at") val createdAt: String,
    @SerialName("notified_at") val notifiedAt: String? = null,
)
