package jp.tomoshibi.android.data.network.endpoints

import jp.tomoshibi.android.data.network.ApiClient
import jp.tomoshibi.android.data.network.StudyAbsenceRequestOut
import jp.tomoshibi.android.data.network.StudyOnlineRequestOut
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// StudyAPI.kt
// data/network/endpoints — 学习（夜学习）相关 endpoint 包装。
//
// 1:1 对齐 iOS StudyAPI.swift。学生侧能用的：
//   - POST /api/v1/study/absence-requests        学习请假条提交
//   - POST /api/v1/study/online-requests         在线学习申请提交
//   - GET  /api/v1/study/online-requests/mine    我的在线学习申请列表
//   - POST /api/v1/study/online-requests/{id}/contract  上传契約書（multipart）
//   - GET  /api/v1/study/online-requests/{id}/contract  下载契約書（二进制）
//   - GET  /api/v1/study/absence-requests/me/summary  当月请假次数

object StudyAPI {
    // 学习请假条（「夜学習欠席届」）提交。
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

    // 上传在线学习申请的契約書（合同 = 网课报名凭证）照片 / PDF。
    // multipart/form-data；先提交申请拿到 id，再调本方法把文件传上去。
    suspend fun uploadOnlineContract(
        requestId: String,
        fileData: ByteArray,
        fileName: String,
        mimeType: String,
    ): StudyOnlineRequestOut =
        ApiClient.upload(
            path = "/api/v1/study/online-requests/$requestId/contract",
            fileData = fileData,
            fileName = fileName,
            mimeType = mimeType,
        )

    // 下载在线学习申请的契約書文件（二进制：图片 / PDF）。
    suspend fun downloadOnlineContract(requestId: String): ByteArray =
        ApiClient.download("/api/v1/study/online-requests/$requestId/contract")

    // 当月学习请假条次数 — 当前登录学生（按 target_date 落当月计数）。
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
    @SerialName("weekly_schedule") val weeklySchedule: Map<String, List<Map<String, String>>>,
    @SerialName("contract_ref") val contractRef: String? = null,
)

// GET /api/v1/study/absence-requests/me/summary 响应 — 当前学生当月请假次数。
@Serializable
data class MyAbsenceSummaryOut(
    val month: String,
    val count: Int,
)
