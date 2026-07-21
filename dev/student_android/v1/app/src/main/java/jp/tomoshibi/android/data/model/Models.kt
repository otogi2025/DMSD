package jp.tomoshibi.android.data.model

import kotlinx.serialization.Serializable

// 数据模型 — 对应 React app-shell.jsx DEFAULT_STATE 各字段
// kotlinx.serialization 给 DataStore JSON 持久化用

@Serializable
data class User(
    val name: String = "",
    val kana: String = "",
    val email: String = "",
    val dorm: String = "男寮",
    val room: String = "M101",
    val avatar: String = "リ",
    // iOS 060218 编码 = 学年(06) + 組(02) + 番号(18)
    val studentNo: String = "060218",
    val gradeClass: String = "高3B組 18番",
    val category: String = "一般寮生", // 一般寮生 / 留学生 / サッカー部
    val phone: String = "090-0000-0000",
    val birthDate: String = "2006-10-14", // 生年月日
    val gender: String = "男", // 性別
    val isStudyTarget: Boolean = false, // 夜学习对象，false=対象外
    // 以下由 loadMe → DisciplineAPI.mySummary 填（/me 本身不含统计）
    val points: Double = 0.0,
    val lateCount: Int = 0,
    val absentCount: Int = 0,
    val needsCleaning: Boolean = false,
)

// 6 值：后端集合 pending/approved_partial/approved/rejected/withdrawn/returned（models.py CHECK 无 draft）。
// APPROVED_PARTIAL 独立显「一部承認」（iOS ApplyStubs:48）；withdrawn 独立，勿并入 REJECTED。
enum class ApplicationStatus { PENDING, APPROVED, APPROVED_PARTIAL, RETURNED, REJECTED, WITHDRAWN }

@Serializable
data class Application(
    val id: String,
    val kind: String, // 外泊 / 外出 / 帰省 / 帰国 / 早帰 / 修繕 / 代理受取 / 来訪者 / その他 / 学習
    val dest: String,
    val from: String, // ISO date string
    val to: String,
    val status: ApplicationStatus,
    val reason: String,
    val createdAt: String,
)

@Serializable
data class RollCall(
    val id: String,
    val ts: Long, // unix millis
    val status: String, // ok / late / miss
    val method: String, // nfc / manual
)

@Serializable
data class Deduction(
    val id: String,
    val date: String,
    val points: Double,
    val reason: String,
    val tier: Int, // 处罚档（§862 月累计）：0=无 / 8=禁足(月累计≥8)（原 4=罚扫随清扫功能删）
)

@Serializable
data class Notification(
    val id: String,
    val tag: String, // 筛选标签，如「申請」「宅配」「お知らせ」「バス」等
    val title: String,
    val body: String,
    val ts: String, // 显示用文本（"今日 18:30" / "M/d HH:mm"）
    val read: Boolean = false,
    // feed 来源才有：点卡片调 markRead 用；push / 宅配 为 null（对齐 iOS NotificationItem.kind/refId）
    val kind: String? = null,
    val refId: String? = null,
)

@Serializable
data class MusicRequest(
    val id: String,
    val title: String,
    val artist: String,
    val votes: Int = 0,
)

@Serializable
data class LostItem(
    val id: String,
    val label: String,
    val colorHex: String, // 用 hex string 序列化 — Compose 侧 Color(0xFF + 后 6 位) parse
    val place: String = "", // 拾得場所（详情屏用，对齐 iOS LostItem.place）
    val date: String = "", // 拾得日「2026-04-25」（详情屏用，对齐 iOS LostItem.date）
)

@Serializable
data class EventItem(
    val date: String, // home 预览用短格式 "04-05"；日历用 ISO "2026-04-05"
    val title: String,
    val time: String, // "08:30"
    val id: Int = 0, // 日历详情用（DEFAULT_EVENTS 给真 id；预览用默认 0）
    val place: String = "", // 场所，可空（如「食堂」）
    val desc: String = "", // 描述，可空
)

// 点歌单条（对应 iOS SongItem；賛成/反対投票 2026-05-01 已废，up/down 保留字段不显示）
@Serializable
data class SongItem(
    val id: Int,
    val title: String,
    val artist: String,
    val by: String, // 投稿者号（如「00号」）
    val up: Int = 0,
    val down: Int = 0,
)

@Serializable
data class PackageItem(
    val id: Int,
    val date: String, // "本日" / "04-22"
    val from: String, // 发货方（Amazon / 佐川急便 等）
    val status: String, // 待領 / 領済
    val tracking: String? = null, // 追跡番号，可空
)

// 点呼履历单条 — 对应 iOS SeedModels.swift RollcallEntry（个人页「点呼履歴」屏用）
@Serializable
data class RollcallEntry(
    val id: String, // "RC-0405-AM"
    val date: String, // "2026-04-05"
    val session: String, // 朝点呼 / 晩点呼
    val status: String, // 時間内 / 遅刻 / 欠席
    val method: String, // NFC / ―（欠席时无方式）
)

// 体调报告履历单条 — 对应 iOS SeedModels.swift HealthRecord
@Serializable
data class HealthRecord(
    val id: String,
    val date: String, // "2026-04-14"
    val symptom: String, // 症状（頭痛 / 腹痛）
    val tempC: Double? = null, // 体温，可空（无温度时不显）
    val note: String? = null, // 备注，可空
)

// 特別運行便单条（界面模型，对应 iOS SpecialBusRoute）
@Serializable
data class SpecialBusRoute(
    val id: String,
    val date: String, // "2026-05-06"
    val weekday: String, // 日语单字曜日（如「水」）
    val time: String, // 出发时刻 "09:20"
    val direction: String, // 路线方向（如「高校棟 → 金川駅」）
    val kind: String, // 「通学便」/「特別便」
    val isAirport: Boolean = false, // 是否空港送迎便
    val seats: String? = null, // 座席说明，可空（如「残り 8 席」）
)

// android#81: data.model 的 AnnouncementBrief / AnnouncementReply / AnnouncementDetail 已成死代码
//   —— 所有 UI/API 都用 data.network 同名 DTO（各文件均 import data.network.Announcement*），
//   此处三类无任何引用，删除以消除跨包同名歧义、防未来误引错版本。

enum class ThemeMode { LIGHT, DARK }

// 点呼状态机 — 对应 iOS HomeStubs.swift 的 4 态 hero
enum class RollState { IDLE, ACTIVE, ABSENT, DONE }

// 学習状态机 — 对齐 iOS StudyState（idle / upcoming / active / done）
// OFF = iOS .idle（本日対象外）；DONE = 本日完了
enum class StudyState { OFF, UPCOMING, ACTIVE, DONE }

/** 账号字段变更履历一条（对齐 iOS ChangeLogEntry；MyInfo 编辑成功后 append） */
data class ChangeLogEntry(
    val id: String =
        java.util.UUID
            .randomUUID()
            .toString(),
    val atEpochMs: Long = System.currentTimeMillis(),
    val field: String,
    val label: String,
    val before: String,
    val after: String,
)

/** 列表加载三态（对齐 iOS AppStore.ListLoadState） */
sealed class ListLoadState {
    data object Idle : ListLoadState()

    data object Loading : ListLoadState()

    data object Loaded : ListLoadState()

    data class Failed(
        val message: String,
    ) : ListLoadState()
}

// AppState — 对应 React StoreProvider state，整体序列化进 DataStore
@Serializable
data class AppState(
    val authed: Boolean = false,
    // 登录令牌（后端颁发的 access_token）。内存态仍挂在 AppState 上供 UI 读写；
    // 持久化由 AppStore → SecureTokenStore（EncryptedSharedPreferences）负责，DataStore JSON 不落明文。
    // null = 未登录 / 已登出。
    val authToken: String? = null,
    // 令牌绝对过期时刻（epoch 毫秒）。非机密，可落 DataStore；启动时据此主动清过期令牌（对齐 iOS tokenExpiryKey）。
    val tokenExpiresAtEpochMs: Long? = null,
    val onboarded: Boolean = false,
    val user: User = User(),
    // GET /students/me 的 id —— 遗失物本人判断 / 拉个人 profile 用；登出清空。
    val myStudentId: String? = null,
    // 学年更新「待更新」标记（spec §4.2）— GET /students/me 的 needs_renewal。
    val needsRenewal: Boolean = false,
    // 当月夜学習欠席届次数（loadMe → StudyAPI.myAbsenceSummary）。
    val studyLeaveCountThisMonth: Int = 0,
    // 公告未読数 / 学生通知 feed 未読数（loadMe 级联拉取，供铃铛 badge；UI 接线归后续工单）。
    val announcementUnreadCount: Int = 0,
    val studentNotificationUnreadCount: Int = 0,
    // 点呼签到种类标签（「時間内」/「遅刻」），由 loadMe → RollStateMachine 填。
    val checkinKind: String? = null,
    val themeMode: ThemeMode = ThemeMode.LIGHT,
    val hueOffset: Int = 0,
    val fontScale: Float = 1.0f,
    // 点呼实时状态（demo / Stage 1 加 cycle）
    val rollState: RollState = RollState.IDLE,
    val rollCountdownSec: Int = 170,
    val checkinAt: String? = null,
    val studyState: StudyState = StudyState.OFF,
    val applications: List<Application> = emptyList(),
    val rollCalls: List<RollCall> = emptyList(),
    val deductions: List<Deduction> = emptyList(),
    val notifications: List<Notification> = emptyList(),
    val musicVotes: Map<String, String> = emptyMap(), // id -> 'up'
    val musicRequests: List<MusicRequest> = emptyList(),
    val lostFoundClaims: Map<String, Boolean> = emptyMap(),
)

// ───────── 申請履歴 family（对应 iOS StayListStubs.swift）─────────
// 老師 38 条 #5「提交后给提交者展示承认状态」。后端 GET /applications/mine 未接 → MockData。
// 为避免跟上面「申し込み tab」用的 ApplicationStatus(4 值) 撞名，这家全部加 Stay 前缀。

// 承認役职（对应 iOS ApprovalRole）— label 是承認链上显示的役职名
enum class StayApprovalRole(
    val label: String,
) {
    HOMEROOM("担任"),
    DORM_HEAD("寮務部長"),
    DORM_CHIEF("寮務課長"),
    INTL_HEAD("国際交流部長"),
    INTL_CHIEF("国際交流課長"),
    MANAGEMENT("管理係"),
    PRINCIPAL("校長"),
}

// 承認決定（对应 iOS ApprovalDecision）
enum class StayDecision(
    val label: String,
) {
    PENDING("審査中"),
    APPROVED("承認"),
    REJECTED("差し戻し"),
}

// 承認链一环（对应 iOS ApprovalStep）
@Serializable
data class StayApprovalStep(
    val role: String, // StayApprovalRole.label
    val approverName: String? = null, // null = 仅显示役职名
    val decision: String, // StayDecision.name（PENDING/APPROVED/REJECTED）
    val decidedAt: String? = null, // "2026-04-21 11:02"
    val comment: String? = null,
)

// 操作履历一条（对应 iOS AuditLogEntry）— 最新在前
@Serializable
data class StayAuditEntry(
    val at: String, // "2026-05-01 14:32"
    val action: String, // 操作类型，值即 UI 文案：「提出」「変更届を提出」「差し戻し」「承認」
    val actor: String, // 役职名+担当者 / 申請者本人
    val detail: String? = null, // 修改届理由 / 「差し戻し」理由
)

// 申請状态（7 值，对应 iOS ApplicationStatus）— label 是状态徽章文案
enum class StayStatus(
    val label: String,
) {
    DRAFT("下書き"),
    PENDING("審査中"),
    APPROVED_PARTIAL("一部承認"),
    APPROVED("承認済"),
    REJECTED("差し戻し"),
    RETURNED("要修正"),
    WITHDRAWN("取消済"),
}

// 申請种类（对应 iOS ApplicationKind）
enum class StayKind(
    val label: String,
) {
    STAY("外泊"),
    HOLIDAY("帰省"),
    RETURN("帰国"),
    OTHER("その他"),
}

// 申請履歴 詳細（对应 iOS StayApplication）— GET /applications/:id 的界面模型
@Serializable
data class StayApplication(
    val id: String,
    val kind: String, // StayKind.label
    val status: String, // StayStatus.name
    val leaveDate: String, // "2026-05-03"
    val returnDate: String? = null,
    val summary: String,
    val destination: String? = null,
    val leaveMethod: String? = null,
    val returnMethod: String? = null,
    val taxiReservationTime: String? = null, // 出租车预约时刻，null=不预约
    val chain: List<StayApprovalStep> = emptyList(),
    val submittedAt: String, // "2026-04-20 10:24"
    val auditLog: List<StayAuditEntry> = emptyList(),
) {
    // 修改届可提交：仅 審査中 / 一部承認 / 要修正 状态（system_features §7.2.4）
    val isEditable: Boolean
        get() =
            status in
                setOf(
                    StayStatus.PENDING.name,
                    StayStatus.APPROVED_PARTIAL.name,
                    StayStatus.RETURNED.name,
                )
}

// android#81: data.model 的 DormEventProposal 已成死代码（UI 用 data.network.DormEventProposalOut），删除。

// 在线学习申請（对应 iOS StudyOnlineRequestOut）
@Serializable
data class StudyOnlineRequest(
    val id: String,
    val reason: String,
    val periodFrom: String, // 期間 "2026-05-01"
    val periodTo: String,
    val contractFileName: String? = null, // 契約書文件名，null=未上传
    val status: String = "pending",
)

// 冷蔵庫購入 申請（对应 iOS FridgePurchaseRequestOut）
@Serializable
data class FridgePurchaseRequest(
    val id: String,
    val product: String, // "A" | "B"（指定 2 款）
    val contactPhone: String,
    val submittedAt: String,
    val status: String = "pending", // pending / ordered / delivered / rejected
)

// 物品所持 申請（对应 iOS ItemPossessionRequestOut）
@Serializable
data class ItemPossessionRequest(
    val id: String,
    val roomNo: String,
    val item: String, // 持込物品名
    val reason: String,
    val guardianName: String, // 保護者名
    val submittedAt: String,
    val status: String = "pending", // pending / approved / rejected
)

// 夜学习出席打卡种类（对应 iOS StudyTap）— 一天 2 次
enum class StudyTap(
    val label: String,
) {
    START("夜学習開始"),
    END("夜学習終了"),
}

// 夜学习出席打卡履历一条（对应 iOS StudyHistoryEntry）
@Serializable
data class StudyHistoryEntry(
    val id: String,
    val date: String, // "2026-05-10"
    val tapKind: String, // StudyTap.name（START / END）
    val timeHM: String, // "19:38"
    val note: String? = null, // 备注，可空（值即 UI 文案，如「遅刻」）
)
