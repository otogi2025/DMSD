package jp.tomoshibi.android.data.network

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonObject

// NetworkModels.kt
// data/network — backend 响应 / 请求体的 @Serializable 模型
//
// 1:1 从 iOS NetworkModels.swift（425 行）+ Endpoints/ApplicationsCreateBodies.swift 翻译。
// 类名跟 iOS struct 一字不差（如 ApplicationOut / TokenOut / StudyOnlineRequestOut），端点才能正确引用。
//
// 日期方针（跟 iOS 同源、跟现有 Android 模型一致）：
//   - 所有日期 / 时刻 / datetime 字段一律用 String（不用 Date/Instant），形态由后端决定
//     （"yyyy-MM-dd" 纯日期 / "HH:mm:ss" 时刻 / "YYYY-MM-DDTHH:mm:ssZ" 带时区 datetime）
//   - UUID 字段用 String
//   - 可空字段用 ? + 默认 null
//
// 自由 JSON 字段（iOS 用 AnyJSON 薄包装）：
//   - stay_locations / meals_skip：iOS 是 [[String: AnyJSON]]?（一组松散 map），这里用 List<JsonObject>?
//   - audit payload：iOS 是 [String: AnyJSON]?（单个松散 map），这里用 JsonObject?
//   - weekly_schedule：形状已知（map → list of {weekday,start,end} 之类），用具体类型 Map<String, List<Map<String, String>>>
//   两者都靠 JsonObject / JsonElement 让 decode 不因形状松散而整段失败，对齐 iOS AnyJSON 的意图。

// ============================================================
// 学生
// ============================================================

// 申请里嵌入的学生简易信息（GET /applications/:id 响应内）
@Serializable
data class StudentBrief(
    val id: String,
    @SerialName("student_no") val studentNo: String,
    val name: String,
    @SerialName("dorm_unit") val dormUnit: Int,
    @SerialName("is_overseas") val isOverseas: Boolean,
    @SerialName("room_no") val roomNo: String,
)

// ============================================================
// 申请
// ============================================================

// 承认 chain 的 1 步（每个役职的决定状态）
@Serializable
data class ApprovalStepOut(
    @SerialName("approver_role") val approverRole: String, // "担任" / "寮務課長" / "管理係" / 等
    val decision: String? = null, // "approve" | "reject" | null（未决）
    @SerialName("decided_at") val decidedAt: String? = null, // ISO 8601 datetime（未决时 null）
    val comment: String? = null,
    @SerialName("approver_id") val approverId: String? = null,
)

// 出寮届详细（POST /applications / GET /applications/:id 响应）
//
// 按 kind 分字段：
//   - 帰省: stay_locations / meals_skip / flight_* 全 null
//   - 外泊: stay_locations / meals_skip 有值，flight_* 全 null
//   - 帰国: 全字段都有值
@Serializable
data class ApplicationOut(
    val id: String,
    @SerialName("student_id") val studentId: String,
    val student: StudentBrief? = null,
    val kind: String, // "帰省" | "外泊" | "帰国"
    val reason: String? = null,
    @SerialName("contact_phone") val contactPhone: String? = null,
    @SerialName("meal_note") val mealNote: String? = null,
    val companion: String? = null,
    @SerialName("dest_cities") val destCities: String? = null,
    // 后端 schemas 非 Optional、_to_application_out 用 bool(...) 强转，永不 null（对齐 iOS）
    @SerialName("receipt_submitted") val receiptSubmitted: Boolean = false,
    @SerialName("is_long_vacation") val isLongVacation: Boolean = false,
    // 日期、时刻：backend 用 date / time 类型 → 保 String
    @SerialName("leave_date") val leaveDate: String, // "2026-05-03"
    @SerialName("leave_method") val leaveMethod: String,
    @SerialName("leave_time") val leaveTime: String, // "19:40:00"
    @SerialName("return_date") val returnDate: String,
    @SerialName("return_method") val returnMethod: String,
    @SerialName("return_time") val returnTime: String,
    @SerialName("taxi_reservation_time") val taxiReservationTime: String? = null, // 出租车预约时刻 "HH:MM:SS"，null = 不预约
    // 仅外泊 / 帰国（松散 JSON 一组 map）
    @SerialName("stay_locations") val stayLocations: List<JsonObject>? = null,
    @SerialName("meals_skip") val mealsSkip: List<JsonObject>? = null,
    // 仅帰国
    @SerialName("flight_dep_air") val flightDepAir: String? = null,
    @SerialName("flight_dep_at") val flightDepAt: String? = null,
    @SerialName("flight_arr_air") val flightArrAir: String? = null,
    @SerialName("flight_arr_at") val flightArrAt: String? = null,
    // FC-020: backend 一直有 bus_route_id，不显示也保留以免 decode 整段 fail
    @SerialName("bus_route_id") val busRouteId: String? = null,
    @SerialName("submitted_at") val submittedAt: String,
    val status: String, // "pending" | "approved_partial" | "approved" | "rejected" | "withdrawn" | "returned"
    @SerialName("withdrawn_at") val withdrawnAt: String? = null,
    @SerialName("approval_chain") val approvalChain: List<ApprovalStepOut>,
)

// 改动履历 entry（GET /applications/:id/audit）
@Serializable
data class AuditLogOut(
    val id: String,
    @SerialName("actor_type") val actorType: String, // "student" | "teacher"
    @SerialName("actor_id") val actorId: String? = null,
    val action: String, // "application.submit" | "application.approve" | "application.amend" 等
    val payload: JsonObject? = null, // 松散 JSON（单个 map）
    @SerialName("created_at") val createdAt: String,
)

// ============================================================
// 学習（夜学习）
// ============================================================

// 「夜学習欠席届」（POST /study/absence-requests 响应）
@Serializable
data class StudyAbsenceRequestOut(
    val id: String,
    @SerialName("student_id") val studentId: String,
    @SerialName("target_date") val targetDate: String, // "2026-05-03"
    val period: String, // "first_half" | "second_half" | "full"
    val reason: String,
    @SerialName("submitted_at") val submittedAt: String,
    val status: String, // "pending" | "approved" | "rejected"
    @SerialName("decided_by") val decidedBy: String? = null,
    @SerialName("decided_at") val decidedAt: String? = null,
    val comment: String? = null,
)

// 学習オンライン申請（POST /study/online-requests 响应）
@Serializable
data class StudyOnlineRequestOut(
    val id: String,
    @SerialName("student_id") val studentId: String,
    val reason: String,
    @SerialName("period_from") val periodFrom: String,
    @SerialName("period_to") val periodTo: String,
    @SerialName("weekly_schedule") val weeklySchedule: Map<String, List<Map<String, String>>>,
    @SerialName("contract_ref") val contractRef: String? = null,
    // 契約書文件信息（合同照片 / PDF）— 非 null 表示已上传。
    // 不含服务器物理路径（安全）；看内容调 GET /study/online-requests/{id}/contract。
    @SerialName("contract_file_name") val contractFileName: String? = null,
    @SerialName("contract_mime") val contractMime: String? = null,
    @SerialName("contract_size") val contractSize: Int? = null,
    @SerialName("submitted_at") val submittedAt: String,
    val status: String, // "pending" | "approved" | "rejected" | "revoked"
    @SerialName("decided_by") val decidedBy: String? = null,
    @SerialName("decided_at") val decidedAt: String? = null,
    val comment: String? = null,
)

// ============================================================
// 宿舍生活类申請
// ============================================================

// 寮生行事企画申請書（POST /dorm-life/event-proposals 响应）
@Serializable
data class DormEventProposalOut(
    val id: String,
    @SerialName("proposer_id") val proposerId: String,
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
    @SerialName("submitted_at") val submittedAt: String,
    val result: String, // "pending" | "approved" | "approved_conditional" | "resubmit" | "rejected"
    @SerialName("decided_by") val decidedBy: String? = null,
    @SerialName("decided_at") val decidedAt: String? = null,
    val comment: String? = null,
)

// 冷蔵庫購入届（POST /dorm-life/fridge-purchases 响应）
@Serializable
data class FridgePurchaseRequestOut(
    val id: String,
    @SerialName("student_id") val studentId: String,
    @SerialName("contact_phone") val contactPhone: String,
    @SerialName("contact_wechat") val contactWechat: String? = null,
    val product: String, // "A" | "B"
    @SerialName("submitted_at") val submittedAt: String,
    @SerialName("delivered_sign") val deliveredSign: String? = null,
    val status: String, // "pending" | "ordered" | "delivered" | "rejected"
    @SerialName("decided_by") val decidedBy: String? = null,
    @SerialName("decided_at") val decidedAt: String? = null,
    val comment: String? = null,
)

// 物品所持許可願（POST /dorm-life/item-possessions 响应）
@Serializable
data class ItemPossessionRequestOut(
    val id: String,
    @SerialName("student_id") val studentId: String,
    @SerialName("room_no") val roomNo: String,
    val item: String,
    val reason: String,
    @SerialName("guardian_name") val guardianName: String,
    @SerialName("submitted_at") val submittedAt: String,
    val status: String, // "pending" | "approved" | "rejected"
    @SerialName("decided_by") val decidedBy: String? = null,
    @SerialName("decided_at") val decidedAt: String? = null,
    val comment: String? = null,
)

// ============================================================
// 巴士便（寮生特別運行 / 平日上下学班车）
// ============================================================

// 巴士便响应体（GET /api/v1/bus/routes 列表里的单条）。spec §7.6。
// kind: "daily_commute"=平日上下学班车 / "dorm_special"=寮生特別運行
@Serializable
data class BusRouteOut(
    val id: String,
    val kind: String,
    val name: String,
    val direction: String,
    @SerialName("schedule_at") val scheduleAt: String, // 出发时刻（完整日期时间）
    @SerialName("arrival_at") val arrivalAt: String? = null, // 到达时刻（空港便等才有）
    @SerialName("visible_to") val visibleTo: String, // "all" | "dorm_only" | "men" | "women"
    val note: String? = null,
    val purpose: String? = null, // 班车用途说明（老师录入，日期头右上角每天显示一条），对齐后端 + iOS
    val deprecated: Boolean,
    @SerialName("created_by_teacher_id") val createdByTeacherId: String,
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String? = null,
)

// GET /api/v1/bus/routes 列表包装
@Serializable
data class BusRouteListOut(
    val items: List<BusRouteOut>,
)

// ============================================================
// 行事预定（日历「行事予定」页）
// ============================================================

// 行事预定响应体（GET /api/v1/events 列表里的单条）。spec §7.5。
// category 取值之一：「学校行事」「寮行事」「外部」「その他」。
@Serializable
data class EventOut(
    val id: String,
    val title: String,
    val category: String,
    @SerialName("event_date") val eventDate: String, // "2026-04-23"（纯日期，无时分）
    @SerialName("start_at") val startAt: String? = null, // 开始时刻（带时分时区，可空）
    @SerialName("end_at") val endAt: String? = null, // 结束时刻（可空）
    val description: String? = null,
    @SerialName("created_by_teacher_id") val createdByTeacherId: String,
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String? = null,
)

// GET /api/v1/events 列表包装
@Serializable
data class EventListOut(
    val items: List<EventOut>,
)

// ============================================================
// 学生新规注册（POST /accounts）
// ============================================================

// POST /api/v1/accounts 响应（成功 201）
// 跟 backend StudentAccountCreateOut 对齐
@Serializable
data class StudentAccountCreateResponse(
    @SerialName("access_token") val accessToken: String,
    @SerialName("token_type") val tokenType: String, // "bearer"
    @SerialName("expires_in") val expiresIn: Int,
    val student: StudentBrief,
)

// ============================================================
// 老师公告（spec system_features.md §7.15）
// ============================================================

// 列表 view 用 — 本文摘要 + 已读状态 + 回复数
@Serializable
data class AnnouncementBrief(
    val id: String,
    val title: String,
    @SerialName("body_summary") val bodySummary: String,
    val scope: String, // "all" / "male" / "female"
    @SerialName("author_teacher_id") val authorTeacherId: String,
    @SerialName("author_teacher_name") val authorTeacherName: String,
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String,
    @SerialName("is_read") val isRead: Boolean,
    @SerialName("reply_count") val replyCount: Int,
)

// GET /announcements 响应
@Serializable
data class AnnouncementListResponse(
    val items: List<AnnouncementBrief>,
)

// 回复条目
@Serializable
data class AnnouncementReplyOut(
    val id: String,
    @SerialName("author_kind") val authorKind: String, // "student" or "teacher"
    @SerialName("author_id") val authorId: String,
    @SerialName("author_name") val authorName: String,
    val body: String,
    @SerialName("created_at") val createdAt: String,
)

// 详情 view — 本文全文 + 回复列表
@Serializable
data class AnnouncementDetail(
    val id: String,
    val title: String,
    val body: String,
    val scope: String,
    @SerialName("author_teacher_id") val authorTeacherId: String,
    @SerialName("author_teacher_name") val authorTeacherName: String,
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String,
    val replies: List<AnnouncementReplyOut>,
)

// GET /announcements/unread-count 响应
@Serializable
data class AnnouncementUnreadCount(
    @SerialName("unread_count") val unreadCount: Int,
)

// ============================================================
// 请求体（POST / PUT 用，从 ApplicationsCreateBodies.swift 翻译）
// ============================================================

// ---- 共通子模型 ----

// 滞在先（外泊 / 帰国届的 stay_locations 元素）
@Serializable
data class StayLocationBody(
    val kind: String, // "ホテル" / "親戚宅" / "自宅" 等
    val name: String,
    val address: String? = null,
    val phone: String? = null,
)

// 食堂跳过的 1 顿（外泊 / 帰国届的 meals_skip 元素）
@Serializable
data class MealSkipBody(
    val date: String, // "2026-05-03"
    val meal: String, // "朝食" | "昼食" | "夕食"
)

// ---- 学生新规注册请求 body ----

// POST /api/v1/accounts 请求 body
// 跟 backend StudentAccountCreateIn 对齐（schemas.py）
// 字段约束：name≤100 / name_kana≤100 / email≤200 / phone≤32 / room_no min 2 max 8
// （room_no min=2：2 寮 A1〜A9 是 A+1 位 = 2 字符，对齐 iOS / 后端）
@Serializable
data class StudentAccountCreateBody(
    val name: String,
    @SerialName("name_kana") val nameKana: String? = null,
    val birthday: String? = null, // "yyyy-MM-dd"，没填传 null
    val gender: String, // "male" or "female"
    @SerialName("grade_code") val gradeCode: String, // 2 桁
    @SerialName("class_code") val classCode: String, // 2 桁
    @SerialName("seat_no") val seatNo: String, // 2 桁
    val category: String, // "一般寮生" 等
    @SerialName("room_no") val roomNo: String, // "M101" / "W205" / "A1" 等
    @SerialName("dorm_unit") val dormUnit: Int, // 1 / 2 / 4
    @SerialName("is_overseas") val isOverseas: Boolean,
    val email: String? = null,
    val phone: String? = null,
    val password: String,
    @SerialName("registration_code") val registrationCode: String, // 6 桁数字（教师生成、5 分钟有效）
) {
    // 客户端 form 校验。返回 null = OK，否则返回日语错误信息（对齐 iOS validate()）。
    // 9 条规则对齐后端 schemas.StudentAccountCreateIn，提交前先跑、省一次 422 往返。
    fun validate(): String? {
        if (name.isEmpty()) return "氏名を入力してください"
        if (name.length > 100) return "氏名は100文字以内で入力してください"
        if (nameKana != null && nameKana.length > 100) {
            return "フリガナは 100 文字以内で入力してください"
        }
        if (gender != "male" && gender != "female") {
            return "性別を選択してください"
        }
        if (!isTwoDigits(gradeCode)) return "学年は2桁の数字で入力してください"
        if (!isTwoDigits(classCode)) return "クラスは2桁の数字で入力してください"
        if (!isTwoDigits(seatNo)) return "出席番号は2桁の数字で入力してください"
        // room_no：backend min_length=2（2 寮 A1〜A9），max_length=8
        if (roomNo.length < 2) return "部屋番号を正しく入力してください"
        if (roomNo.length > 8) return "部屋番号は8文字以内で入力してください"
        // dorm_unit：Literal[1, 2, 4]（没有 3 寮）；由房号+性别推导，落到这里说明房号填错
        if (dormUnit != 1 && dormUnit != 2 && dormUnit != 4) {
            return "部屋番号をご確認ください"
        }
        if (email != null && email.length > 200) {
            return "メールアドレスは200文字以内で入力してください"
        }
        if (phone != null && phone.length > 32) {
            return "電話番号は32文字以内で入力してください"
        }
        if (password.length < 6 || password.length > 128) {
            return "パスワードは6〜128文字で入力してください"
        }
        if (registrationCode.length != 6 || !registrationCode.all { it.isDigit() }) {
            return "登録コードは6桁の数字で入力してください"
        }
        return null
    }

    private fun isTwoDigits(s: String): Boolean = s.length == 2 && s.all { it.isDigit() }
}

// ============================================================
// 学生通知中心 feed（对齐 iOS NetworkModels StudentNotification*）
// ============================================================

// 一条学生通知 = 某条 公告/巴士/行事（老师投稿时勾了「学生に通知する」）
@Serializable
data class StudentNotificationItem(
    val kind: String, // "announcement" | "bus" | "event"
    @SerialName("ref_id") val refId: String, // UUID
    val title: String,
    val body: String, // 摘要（后端截断到 80 字）
    @SerialName("created_at") val createdAt: String,
    // 已读态不可变；乐观更新用 copy(isRead=true) 生成新列表赋 StateFlow，禁止原地改
    @SerialName("is_read") val isRead: Boolean,
)

// GET /api/v1/student/notifications 响应
@Serializable
data class StudentNotificationFeedOut(
    val items: List<StudentNotificationItem>,
    @SerialName("unread_count") val unreadCount: Int, // 三类未读合计 → 驱动铃铛 badge
)

// ---- 帰省届（最简、不带滞在先和飞机）----

// 帰省届创建 body（罗马字 Kisei）。旧拼写 KisheiCreateBody 保留 typealias，兼容 StayForm 等引用。
@Serializable
data class KiseiCreateBody(
    val kind: String = "帰省", // discriminated union 的判定字段
    val reason: String? = null,
    @SerialName("contact_phone") val contactPhone: String? = null,
    @SerialName("meal_note") val mealNote: String? = null,
    @SerialName("is_long_vacation") val isLongVacation: Boolean,
    @SerialName("leave_date") val leaveDate: String, // "2026-05-03"
    @SerialName("leave_method") val leaveMethod: String,
    @SerialName("leave_time") val leaveTime: String, // "19:40:00" — backend 是 time 类型
    @SerialName("return_date") val returnDate: String,
    @SerialName("return_method") val returnMethod: String,
    @SerialName("return_time") val returnTime: String,
    @SerialName("taxi_reservation_time") val taxiReservationTime: String? = null, // null = 不预约
)

typealias KisheiCreateBody = KiseiCreateBody

// ---- 外泊届（带滞在先 + 食事跳过）----

@Serializable
data class GaihakuCreateBody(
    val kind: String = "外泊",
    val reason: String? = null,
    @SerialName("contact_phone") val contactPhone: String? = null,
    @SerialName("meal_note") val mealNote: String? = null,
    val companion: String? = null,
    @SerialName("dest_cities") val destCities: String? = null,
    @SerialName("leave_date") val leaveDate: String,
    @SerialName("leave_method") val leaveMethod: String,
    @SerialName("leave_time") val leaveTime: String,
    @SerialName("return_date") val returnDate: String,
    @SerialName("return_method") val returnMethod: String,
    @SerialName("return_time") val returnTime: String,
    @SerialName("stay_locations") val stayLocations: List<StayLocationBody>, // 至少 1 件（backend 校验）
    @SerialName("meals_skip") val mealsSkip: List<MealSkipBody>, // 0 件以上
    @SerialName("taxi_reservation_time") val taxiReservationTime: String? = null, // null = 不预约
)

// ---- 帰国届（外泊 + 飞机情报）----

@Serializable
data class KikokuCreateBody(
    val kind: String = "帰国",
    val reason: String? = null,
    @SerialName("contact_phone") val contactPhone: String? = null,
    @SerialName("meal_note") val mealNote: String? = null,
    val companion: String? = null,
    @SerialName("dest_cities") val destCities: String? = null,
    @SerialName("leave_date") val leaveDate: String,
    @SerialName("leave_method") val leaveMethod: String,
    @SerialName("leave_time") val leaveTime: String,
    @SerialName("return_date") val returnDate: String,
    @SerialName("return_method") val returnMethod: String,
    @SerialName("return_time") val returnTime: String,
    @SerialName("stay_locations") val stayLocations: List<StayLocationBody>,
    @SerialName("meals_skip") val mealsSkip: List<MealSkipBody>,
    @SerialName("flight_dep_air") val flightDepAir: String, // 出発空港 (例: "羽田")
    @SerialName("flight_dep_at") val flightDepAt: String, // ISO 8601 datetime "2026-05-03T18:00:00+09:00"
    @SerialName("flight_arr_air") val flightArrAir: String,
    @SerialName("flight_arr_at") val flightArrAt: String,
    @SerialName("taxi_reservation_time") val taxiReservationTime: String? = null, // null = 不预约
)

// ---- 修改届（PUT /applications/:id 用、全字段 Optional）----

// IX-004: 全字段默认 null，修改届只改了几个字段就只传那几个（其余 null 不发，
// 后端 model_dump(exclude_none=True) 只更新非 null 的）。
// 注意：要让 null 字段不被序列化进 JSON，调用端用本类的 ApiClient.put 时
// 依赖 Json 配置 explicitNulls=false（ApiClient 共用 json 未设则 null 会被发出，
// 端点 agent 接入时需确认该配置 — 见 ApiClient.json）。
@Serializable
data class ApplicationUpdateBody(
    val reason: String? = null,
    // 修改届的「修改理由」— 后端只写进 audit 给老师 / 履历看，不覆盖 reason（申请理由本身）。
    @SerialName("amend_reason") val amendReason: String? = null,
    @SerialName("contact_phone") val contactPhone: String? = null,
    @SerialName("meal_note") val mealNote: String? = null,
    val companion: String? = null,
    @SerialName("dest_cities") val destCities: String? = null,
    @SerialName("is_long_vacation") val isLongVacation: Boolean? = null,
    @SerialName("leave_date") val leaveDate: String? = null,
    @SerialName("leave_method") val leaveMethod: String? = null,
    @SerialName("leave_time") val leaveTime: String? = null,
    @SerialName("return_date") val returnDate: String? = null,
    @SerialName("return_method") val returnMethod: String? = null,
    @SerialName("return_time") val returnTime: String? = null,
    @SerialName("stay_locations") val stayLocations: List<StayLocationBody>? = null,
    @SerialName("meals_skip") val mealsSkip: List<MealSkipBody>? = null,
    @SerialName("flight_dep_air") val flightDepAir: String? = null,
    @SerialName("flight_dep_at") val flightDepAt: String? = null,
    @SerialName("flight_arr_air") val flightArrAir: String? = null,
    @SerialName("flight_arr_at") val flightArrAt: String? = null,
    // 注：出租车预约暂为 create-only（新建时填），修改届不改 taxi。
)

// ============================================================
// 自由 JSON 占位说明
// ============================================================
// iOS 的 AnyJSON 薄包装在 Kotlin 侧用 kotlinx.serialization.json 的 JsonObject / JsonElement
// 直接表达（见上 stay_locations / meals_skip / payload 字段），无需单独类型。
// 若端点需要把松散值取成字符串，用 jsonPrimitive.contentOrNull 等 API 现场提取。
@Suppress("unused")
private typealias AnyJSON = JsonElement
