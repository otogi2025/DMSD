package jp.tomoshibi.android.data.network.endpoints

import jp.tomoshibi.android.data.network.ApiClient
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// RollCallAPI.kt
// data/network/endpoints — 点呼（roll call = 宿舍夜间点名）相关 endpoint 包装。
//
// 1:1 对齐 iOS RollCallAPI.swift。
// 学生端只用 POST /checkins（路径 B = iPhone 静态标签 tap 触发 Universal Link 后提交签到）。
// 其他 GET endpoint（today/sessions、board、summary）是老师端用，学生端不需要，故不包含。
//
// 注意：RollCallCheckinBody / RollCallEventOut 这两个 DTO 在 iOS 里也是写在 RollCallAPI.swift
// 内（不在 NetworkModels），这里照搬同样布局，co-locate（跟端点放一起）在本文件。
// 字段命名跟 backend schemas.py 的 RollCallCheckinIn / RollCallEventOut 对齐。

object RollCallAPI {
    // POST /api/v1/rollcall/sessions/:id/checkins — 学生 BTR（Back-To-Room = 回房签到）tap 入口。
    //
    // 路径 B（iPhone 静态标签）流程：
    //   - 用户 tap iPhone-BTR 标签触发 Android 深链
    //   - app 拿到 nonce（一次性随机串；v1.1+ 起带 ECDSA 签名防伪造）
    //   - 调本方法提交 checkin
    //
    // sessionId 是点呼场次的 UUID（用 String，跟 NetworkModels 日期方针一致 UUID 一律 String）。
    suspend fun checkin(
        sessionId: String,
        body: RollCallCheckinBody,
    ): RollCallEventOut = ApiClient.post("/api/v1/rollcall/sessions/$sessionId/checkins", body)
}

// POST /api/v1/rollcall/sessions/:id/checkins 请求 body。
//
// 跟 backend RollCallCheckinIn 对齐（schemas.py）。
// 字段命名保持 snake_case 跟 backend 逐字节对齐（同 NetworkModels.kt 风格）。
@Serializable
data class RollCallCheckinBody(
    @SerialName("card_uid") val cardUid: String? = null, // 路径 A（NFC 卡 UID）；路径 B 时 null
    @SerialName("student_id") val studentId: String? = null, // 路径 B / manual 时学生自身 ID（UUID 用 String）
    @SerialName("idempotency_key") val idempotencyKey: String? = null, // 路径 B 客户端生成 UUID 防重复
    @SerialName("status_source") val statusSource: String, // "auto_nfc" / "manual_checkin"
    @SerialName("ts_local") val tsLocal: String? = null, // 客户端时刻（日期一律 String）；null 由 backend 用服务器时间
    @SerialName("path_hint") val pathHint: String? = null, // "A" / "B" / "manual"
)

// POST /api/v1/rollcall/sessions/:id/checkins 响应。
//
// 跟 backend RollCallEventOut 对齐。
@Serializable
data class RollCallEventOut(
    val id: String, // UUID 用 String
    @SerialName("student_id") val studentId: String,
    @SerialName("base_status") val baseStatus: String, // "present" / "late" / "absent" / "exempt_range"
    @SerialName("status_source") val statusSource: String, // "auto_nfc" / "manual_checkin" / "teacher_override" / "auto_settle"
    @SerialName("checked_in_at") val checkedInAt: String, // datetime 一律 String
    @SerialName("path_type") val pathType: String? = null, // "A" / "B" / "manual"
)
