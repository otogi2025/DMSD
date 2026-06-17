package jp.tomoshibi.android.data.network.endpoints

import jp.tomoshibi.android.data.network.ApiClient
import jp.tomoshibi.android.data.network.DormEventProposalOut
import jp.tomoshibi.android.data.network.FridgePurchaseRequestOut
import jp.tomoshibi.android.data.network.ItemPossessionRequestOut
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// DormLifeAPI.kt
// data/network/endpoints — 宿舍生活类申請 endpoint 包装
//
// 对齐 iOS DormLifeAPI.swift（enum DormLifeAPI）。
// iOS 把 3 个请求 body（EventProposalBody / FridgePurchaseBody / ItemPossessionBody）嵌在 enum 里，
// Android 这里同样把它们放在 object 内（NetworkModels.kt 只放 *Out 响应类，请求 body 跟随各端点）。
//
// 后端 spec §宿舍生活类申請:
//   POST /api/v1/dorm-life/event-proposals        — 提交寮生行事企画申請書
//   GET  /api/v1/dorm-life/event-proposals/mine   — 我提交过的行事企画
//   POST /api/v1/dorm-life/fridge-purchases       — 提交冷蔵庫購入届
//   GET  /api/v1/dorm-life/fridge-purchases/mine  — 我提交过的冷蔵庫購入届
//   POST /api/v1/dorm-life/item-possessions       — 提交物品所持許可願
//   GET  /api/v1/dorm-life/item-possessions/mine  — 我提交过的物品所持許可願
object DormLifeAPI {
    // 寮生行事企画申請書请求 body（对齐 iOS DormLifeAPI.EventProposalBody）
    @Serializable
    data class EventProposalBody(
        @SerialName("team_name") val teamName: String? = null,
        val title: String,
        @SerialName("held_at") val heldAt: String,
        val place: String,
        @SerialName("expected_count") val expectedCount: Int,
        val target: String,
        val purpose: String,
        val content: String,
        @SerialName("risk_solution") val riskSolution: String,
        @SerialName("expected_cost") val expectedCost: String,
        val note: String? = null,
    )

    // 冷蔵庫購入届请求 body（对齐 iOS DormLifeAPI.FridgePurchaseBody）
    @Serializable
    data class FridgePurchaseBody(
        @SerialName("contact_phone") val contactPhone: String,
        @SerialName("contact_wechat") val contactWechat: String? = null,
        val product: String,
    )

    // 物品所持許可願请求 body（对齐 iOS DormLifeAPI.ItemPossessionBody）
    @Serializable
    data class ItemPossessionBody(
        @SerialName("room_no") val roomNo: String,
        val item: String,
        val reason: String,
        @SerialName("guardian_name") val guardianName: String,
    )

    // 提交寮生行事企画申請書
    suspend fun submitEventProposal(body: EventProposalBody): DormEventProposalOut =
        ApiClient.post("/api/v1/dorm-life/event-proposals", body)

    // 我提交过的行事企画
    suspend fun listMyEventProposals(): List<DormEventProposalOut> = ApiClient.get("/api/v1/dorm-life/event-proposals/mine")

    // 行事企画 再提出（老师差戻后学生重提）。body 是完整行事企画字段（跟首次提交同形）。
    // 后端只在 result=="resubmit" 状态接受，否则 409 CANNOT_RESUBMIT；成功后 result 变 "pending"。
    suspend fun resubmitEventProposal(
        id: String,
        body: EventProposalBody,
    ): DormEventProposalOut = ApiClient.post("/api/v1/dorm-life/event-proposals/$id/resubmit", body)

    // 提交冷蔵庫購入届
    suspend fun submitFridgePurchase(body: FridgePurchaseBody): FridgePurchaseRequestOut =
        ApiClient.post("/api/v1/dorm-life/fridge-purchases", body)

    // 我提交过的冷蔵庫購入届
    suspend fun listMyFridgePurchases(): List<FridgePurchaseRequestOut> = ApiClient.get("/api/v1/dorm-life/fridge-purchases/mine")

    // 提交物品所持許可願
    suspend fun submitItemPossession(body: ItemPossessionBody): ItemPossessionRequestOut =
        ApiClient.post("/api/v1/dorm-life/item-possessions", body)

    // 我提交过的物品所持許可願
    suspend fun listMyItemPossessions(): List<ItemPossessionRequestOut> = ApiClient.get("/api/v1/dorm-life/item-possessions/mine")
}
