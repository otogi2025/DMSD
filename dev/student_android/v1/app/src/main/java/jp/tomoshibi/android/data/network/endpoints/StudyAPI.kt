package jp.tomoshibi.android.data.network.endpoints

import jp.tomoshibi.android.data.network.ApiClient
import jp.tomoshibi.android.data.network.StudyAbsenceRequestOut
import jp.tomoshibi.android.data.network.StudyOnlineRequestOut
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// StudyAPI.kt
// data/network/endpoints — 学习（晚自习）相关 endpoint 包装。
//
// 1:1 对齐 iOS StudyAPI.swift。学生侧能用的：
//   - POST /api/v1/study/absence-requests        学习请假条（日语申请名「晩自習欠席届」）提交
//   - POST /api/v1/study/online-requests         在线学习申请（日语申请名「学習オンライン申請」）提交
//   - GET  /api/v1/study/online-requests/mine    我的在线学习申请列表
//   - GET  /api/v1/study/absence-requests/me/summary  当月请假次数
//
// 不在这里的（老师侧 endpoint，学生不会调）：老师批准 / 拒绝；学习出席 NFC tap 提交（backend 待实装）。
//
// 注意：iOS 的 uploadOnlineContract（上传契约书 = 网课报名凭证照片 / PDF）走 multipart/form-data，
// 依赖 APIClient.upload。当前 Android ApiClient 只有 get/post/put/delete，没有 multipart 方法，
// 故本端点暂不实装上传（需先给 ApiClient 加 multipart 能力，不在本文件职责内）。
//
// 请求 / 响应 DTO 说明：
//   - AbsenceRequestBody / OnlineRequestBody / MyAbsenceSummaryOut 在 iOS 里也写在 StudyAPI.swift 内
//     （不在 NetworkModels），这里照搬同样布局，co-locate（跟端点放一起）在本文件。
//   - StudyAbsenceRequestOut / StudyOnlineRequestOut 已在 NetworkModels.kt，这里直接引用。

object StudyAPI {
    // 学习请假条（「晩自習欠席届」）提交。
    // 失败：422 → 同日重复提交 / target_date 超范围等；401 → 重新登录。
    suspend fun submitAbsenceRequest(
        targetDate: String,
        period: String,
        reason: String,
    ): StudyAbsenceRequestOut {
        val body = AbsenceRequestBody(targetDate = targetDate, period = period, reason = reason)
        return ApiClient.post("/api/v1/study/absence-requests", body)
    }

    // 在线学习申请（「学習オンライン申請」）提交。
    suspend fun submitOnlineRequest(body: OnlineRequestBody): StudyOnlineRequestOut = ApiClient.post("/api/v1/study/online-requests", body)

    // 在线学习申请 我的列表。
    suspend fun listMyOnlineRequests(): List<StudyOnlineRequestOut> = ApiClient.get("/api/v1/study/online-requests/mine")

    // 当月学习请假条次数 — 当前登录学生（按 target_date 落当月计数）。
    // 与后端 MyAbsenceSummaryOut 对齐。
    suspend fun myAbsenceSummary(): MyAbsenceSummaryOut = ApiClient.get("/api/v1/study/absence-requests/me/summary")
}

// POST /api/v1/study/absence-requests 请求 body。
@Serializable
data class AbsenceRequestBody(
    @SerialName("target_date") val targetDate: String, // "2026-05-03"
    val period: String, // "first_half" | "second_half" | "full"
    val reason: String, // 申请理由（必填、1-2000 字）
)

// POST /api/v1/study/online-requests 请求 body。
@Serializable
data class OnlineRequestBody(
    val reason: String,
    @SerialName("period_from") val periodFrom: String,
    @SerialName("period_to") val periodTo: String,
    // 形状已知：weekday → 一组 {start,end} 之类（跟 NetworkModels weeklySchedule 同结构）
    @SerialName("weekly_schedule") val weeklySchedule: Map<String, List<Map<String, String>>>,
    @SerialName("contract_ref") val contractRef: String? = null,
)

// GET /api/v1/study/absence-requests/me/summary 响应 — 当前学生当月请假次数。
// 与后端 MyAbsenceSummaryOut 对齐。
@Serializable
data class MyAbsenceSummaryOut(
    val month: String,
    val count: Int,
)
