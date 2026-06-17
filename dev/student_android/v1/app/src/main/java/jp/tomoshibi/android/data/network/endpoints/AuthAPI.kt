package jp.tomoshibi.android.data.network.endpoints

import jp.tomoshibi.android.data.network.AnnouncementDetail
import jp.tomoshibi.android.data.network.AnnouncementListResponse
import jp.tomoshibi.android.data.network.AnnouncementReplyOut
import jp.tomoshibi.android.data.network.AnnouncementUnreadCount
import jp.tomoshibi.android.data.network.ApiClient
import jp.tomoshibi.android.data.network.StudentAccountCreateBody
import jp.tomoshibi.android.data.network.StudentAccountCreateResponse
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// AuthAPI.kt
// data/network/endpoints — 认证相关 endpoint 包装
//
// 1:1 从 iOS AuthAPI.swift 翻译。包 backend 的 /api/v1/sessions/* 等 endpoint：
//   - 学生登录 / 新规注册 / 账号删除（认证流）
//   - 老师公告（学生面向）
//   - 当前登录学生基本信息 + 番号再設定 + 当月扣分汇总
// iOS 把这几组都 inline 在同一文件（避免给 .pbxproj 加单独 file），这里照搬同结构。
//
// 响应体 DTO：能引用 NetworkModels.kt 已建好的就引用；iOS 在本文件内 inline 定义的
//   响应类（StudentMeOut / MyDisciplineSummaryOut）这里也跟着 inline。TokenOut iOS 放在
//   APIClient.swift，Android 这边 NetworkModels.kt 没有它，按「只建本文件」铁律不去碰
//   NetworkModels.kt，故也 inline 在本文件。

// ============================================================
// 响应体 DTO（iOS 在 AuthAPI.swift / APIClient.swift 内 inline 定义、NetworkModels.kt 暂无）
// ============================================================

// / 登录 / token 颁发响应（对齐 iOS TokenOut，源 APIClient.swift）
@Serializable
data class TokenOut(
    @SerialName("access_token") val accessToken: String,
    @SerialName("token_type") val tokenType: String,
    @SerialName("expires_in") val expiresIn: Int,
)

// / GET /students/me 响应 — 后端 StudentProfileBasic（学生基本信息）。
// / 只含身份字段；统计（扣分/迟到/欠席）+ 夜学习对象 flag 不在这接口。
@Serializable
data class StudentMeOut(
    val id: String,
    @SerialName("student_no") val studentNo: String,
    val name: String,
    @SerialName("name_kana") val nameKana: String? = null,
    @SerialName("grade_code") val gradeCode: String,
    @SerialName("class_code") val classCode: String,
    @SerialName("seat_no") val seatNo: String,
    val gender: String,
    val category: String,
    @SerialName("room_no") val roomNo: String,
    @SerialName("dorm_unit") val dormUnit: Int,
    @SerialName("is_overseas") val isOverseas: Boolean,
    val email: String? = null,
    val phone: String? = null,
    @SerialName("avatar_url") val avatarUrl: String? = null,
    val status: String,
    // 学年更新「待更新」标记 — true 时主页顶部显示「更新番号」按钮（spec §4.2）。
    // 可空兜底：分阶段部署时若后端未发该字段，避免整个 /me 解码失败。
    @SerialName("needs_renewal") val needsRenewal: Boolean? = null,
    // registered_at 解码时忽略（ApiClient.json 设 ignoreUnknownKeys=true，多余字段跳过）
)

// / GET /discipline/me/summary 响应 — 当前学生当月扣分统计。
// / 与后端 MyDisciplineSummaryOut 对齐：当月总扣分 + 点呼迟到 / 欠席次数。
@Serializable
data class MyDisciplineSummaryOut(
    val month: String,
    @SerialName("total_points") val totalPoints: Double,
    @SerialName("late_count") val lateCount: Int,
    @SerialName("absent_count") val absentCount: Int,
    // 罚扫对象标记（≥4 分需罚扫）— 与 iOS Bool? 对齐。
    // 可空兜底：分阶段部署时旧后端不发该字段，避免整个 summary 解码失败。
    // 消费侧按 needsCleaning ?? (totalPoints >= 4) 兜底（对齐 AppStore.swift）。
    @SerialName("needs_cleaning") val needsCleaning: Boolean? = null,
)

// ============================================================
// 学生登录
// ============================================================

object AuthAPI {
    // / POST /api/v1/sessions/student 用的请求 body
    @Serializable
    private data class StudentLoginRequest(
        @SerialName("student_no") val studentNo: String, // 6 桁学号 "060218"
        val password: String,
    )

    // / 学生登录。成功返 TokenOut（access_token + token_type + expires_in）
    // / 抛出：
    // /   - ApiError.Unauthorized — 学号 / 密码错（401）
    // /   - ApiError.Unprocessable — 学号格式错等（422）
    // /   - ApiError.Network — 通信失败
    suspend fun loginStudent(
        studentNo: String,
        password: String,
    ): TokenOut {
        val body = StudentLoginRequest(studentNo = studentNo, password = password)
        return ApiClient.post("/api/v1/sessions/student", body)
    }
}

// ============================================================
// 学生新规注册（POST /accounts，App Store 上架对策）
// ============================================================

object AccountsAPI {
    // / 学生新规注册 — 必须传教师生成的 registrationCode（6 桁数字、5 分钟有效）。
    // / 成功 201 → 永久 session JWT + 学生 brief。
    // /
    // / spec: system_features.md §7.16 + BACKEND §5.1.5
    // /
    // / 抛出：
    // /   - ApiError.Unprocessable（422）— 注册码无效 / 学号重复 / room↔dorm 不对 / email 重复
    // /   - ApiError.Network — 通信失败
    suspend fun createAccount(body: StudentAccountCreateBody): StudentAccountCreateResponse = ApiClient.post("/api/v1/accounts", body)

    // / DELETE /api/v1/accounts/me — App Store 5.1.1(v) 强制要求的账号删除接口。
    // / 成功返 204 No Content。调用方收到后把 ApiClient.token = null 触发登出跳转。
    suspend fun deleteMyAccount() {
        ApiClient.delete("/api/v1/accounts/me")
    }
}

// ============================================================
// 老师公告 endpoint（spec §7.15）
// ============================================================

object AnnouncementsAPI {
    // / GET /announcements — 列表（按当前学生 scope 自动过滤、新→旧）
    suspend fun list(): AnnouncementListResponse = ApiClient.get("/api/v1/announcements")

    // / GET /announcements/unread-count — 主页 badge 用未读数
    suspend fun unreadCount(): AnnouncementUnreadCount = ApiClient.get("/api/v1/announcements/unread-count")

    // / GET /announcements/:id — 详情 + 回复（访问时自动写已读）
    suspend fun detail(id: String): AnnouncementDetail = ApiClient.get("/api/v1/announcements/$id")

    // / POST /announcements/:id/replies 用的请求 body
    @Serializable
    private data class ReplyBody(
        val body: String,
    )

    // / POST /announcements/:id/replies — 发回复（学生用）
    suspend fun postReply(
        announcementId: String,
        body: String,
    ): AnnouncementReplyOut {
        val req = ReplyBody(body = body)
        return ApiClient.post("/api/v1/announcements/$announcementId/replies", req)
    }

    // / DELETE /announcements/:id/replies/:rid — 删自己发的回复
    suspend fun deleteReply(
        announcementId: String,
        replyId: String,
    ) {
        ApiClient.delete("/api/v1/announcements/$announcementId/replies/$replyId")
    }
}

// ============================================================
// 当前登录学生（GET /students/me，替换假数据）
// ============================================================

object StudentsAPI {
    // / GET /students/me — 当前登录学生的基本信息。
    // / 仿 teachers/me；后端从令牌取学生，无需传 id。
    suspend fun me(): StudentMeOut = ApiClient.get("/api/v1/students/me")
}

// ============================================================
// 番号再設定（学年更新 / 学生自设番号，spec §4.2）
// ============================================================

object StudentRenewalAPI {
    // / POST /api/v1/students/me/renew-number 请求 body — 身份从登录令牌取，不含 student_id。
    @Serializable
    private data class RenewBody(
        @SerialName("grade_code") val gradeCode: String,
        @SerialName("class_code") val classCode: String,
        @SerialName("seat_no") val seatNo: String,
    )

    // / 学生自设番号 — 选新的 学年 / 组 / 出席番号。
    // / 撞号时后端返 422 → ApiError.Unprocessable（日语提示），原样弹给学生。
    // / 成功返回更新后的 StudentMeOut（新 student_no + needsRenewal=false）。
    suspend fun renewNumber(
        gradeCode: String,
        classCode: String,
        seatNo: String,
    ): StudentMeOut {
        val body = RenewBody(gradeCode = gradeCode, classCode = classCode, seatNo = seatNo)
        return ApiClient.post("/api/v1/students/me/renew-number", body)
    }
}

// ============================================================
// 当月扣分汇总（GET /discipline/me/summary）
// ============================================================

object DisciplineAPI {
    // / GET /discipline/me/summary — 当前登录学生当月扣分汇总（总分 / 迟到 / 欠席）。
    suspend fun mySummary(): MyDisciplineSummaryOut = ApiClient.get("/api/v1/discipline/me/summary")
}
