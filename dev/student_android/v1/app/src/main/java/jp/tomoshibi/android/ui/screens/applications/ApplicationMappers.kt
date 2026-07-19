package jp.tomoshibi.android.ui.screens.applications

import jp.tomoshibi.android.data.model.Application
import jp.tomoshibi.android.data.model.ApplicationStatus
import jp.tomoshibi.android.data.model.StayApplication
import jp.tomoshibi.android.data.model.StayApprovalStep
import jp.tomoshibi.android.data.model.StayAuditEntry
import jp.tomoshibi.android.data.model.StayDecision
import jp.tomoshibi.android.data.model.StayStatus
import jp.tomoshibi.android.data.network.ApplicationOut
import jp.tomoshibi.android.data.network.ApprovalStepOut
import jp.tomoshibi.android.data.network.AuditLogOut
import jp.tomoshibi.android.data.network.endpoints.OutingOut
import kotlinx.serialization.json.contentOrNull
import kotlinx.serialization.json.jsonPrimitive

// ApplicationMappers.kt
// 出寮届 / 外出 DTO → 各申請屏现有 UI 本地模型的映射，集中在此各屏共用。
//
// 为什么要映射层：后端 status 是英语小写蛇形（"pending"/"approved_partial"/...），
// 承认链 decision 是 "approve"/"reject"/null；而界面用的本地枚举是大写名。
// 两套形状不同，集中在这里转一次，列表/详情屏只管「调 API → 映射 → 套三态」。

// 后端 status 英语 → ApplicationStatus（申请一览 / ApplicationDetail 用）。
// approved_partial 归 APPROVED；withdrawn 独立为 WITHDRAWN（勿标成「差し戻し」）。
fun mapApplicationStatus4(backend: String): ApplicationStatus =
    when (backend) {
        "pending" -> ApplicationStatus.PENDING

        "approved" -> ApplicationStatus.APPROVED

        "approved_partial" -> ApplicationStatus.APPROVED_PARTIAL

        "returned" -> ApplicationStatus.RETURNED

        "withdrawn" -> ApplicationStatus.WITHDRAWN

        "rejected" -> ApplicationStatus.REJECTED

        // 后端 CHECK 约束外的值不可达（含 draft）；iOS 会显原文，枚举模型下保守落 REJECTED。
        else -> ApplicationStatus.REJECTED
    }

// ApplicationStatus 枚举 → 状态徽章文案（对齐 iOS statusPair）。
fun applicationStatusLabel(status: ApplicationStatus): String =
    when (status) {
        ApplicationStatus.PENDING -> "審査中"
        ApplicationStatus.APPROVED -> "承認済"
        ApplicationStatus.APPROVED_PARTIAL -> "一部承認"
        ApplicationStatus.RETURNED -> "要修正"
        ApplicationStatus.REJECTED -> "差し戻し"
        ApplicationStatus.WITHDRAWN -> "取消済"
    }

// 外出三态徽章文案（对齐 iOS outingStatusPair：「確認待ち」/「確認済」/「取消済」）。
fun outingStatusLabel(status: ApplicationStatus): String =
    when (status) {
        ApplicationStatus.PENDING -> "確認待ち"
        ApplicationStatus.APPROVED -> "確認済"
        ApplicationStatus.WITHDRAWN -> "取消済"
        else -> applicationStatusLabel(status)
    }

// 列表卡按 kind 选文案：外出走 outing 三态，其余走出寮届 statusPair。
fun rowStatusLabel(
    kind: String,
    status: ApplicationStatus,
): String = if (kind == "外出") outingStatusLabel(status) else applicationStatusLabel(status)

// 后端 status 英语 → StayStatus（7 值，StayListScreen / StayDetailScreen 用）。
fun mapStayStatus(backend: String): StayStatus =
    when (backend) {
        "pending" -> StayStatus.PENDING
        "approved_partial" -> StayStatus.APPROVED_PARTIAL
        "approved" -> StayStatus.APPROVED
        "rejected" -> StayStatus.REJECTED
        "returned" -> StayStatus.RETURNED
        "withdrawn" -> StayStatus.WITHDRAWN
        else -> StayStatus.PENDING
    }

// 承认链单步 decision 英语 → StayDecision.name。
private fun mapDecisionName(d: String?): String =
    when (d) {
        "approve" -> StayDecision.APPROVED.name
        "reject" -> StayDecision.REJECTED.name
        else -> StayDecision.PENDING.name
    }

// stay_locations[0].name（「宿泊先」地址文本；对齐 iOS IX-010）
private fun firstStayLocationName(out: ApplicationOut): String? {
    val locs = out.stayLocations ?: return null
    val name =
        locs
            .firstOrNull()
            ?.get("name")
            ?.jsonPrimitive
            ?.contentOrNull
            ?.trim()
    return name?.takeIf { it.isNotEmpty() }
}

// 一览 summary：日期范围 · 「宿泊先」（对齐 iOS makeSummary）
private fun makeStaySummary(out: ApplicationOut): String {
    val dateRange =
        if (out.returnDate == out.leaveDate) {
            out.leaveDate
        } else {
            "${out.leaveDate} 〜 ${out.returnDate}"
        }
    val loc = firstStayLocationName(out)
    return if (loc != null) "$dateRange · $loc" else dateRange
}

// ApplicationOut → 本地 Application（ApplicationsScreen 列表 / ApplicationDetailScreen 用）。
// 行先优先「宿泊先」stay_locations，再 dest_cities / reason。
fun ApplicationOut.toUiApplication(): Application =
    Application(
        id = id,
        kind = kind,
        dest = firstStayLocationName(this) ?: destCities ?: reason ?: "—",
        from = leaveDate,
        to = returnDate,
        status = mapApplicationStatus4(status),
        reason = reason ?: "",
        createdAt = submittedAt,
    )

// OutingOut → 本地 Application（申请一览合并外出记录；id 加 "outing:" 前缀，详情按前缀分流）。
fun OutingOut.toUiApplication(): Application =
    Application(
        id = "outing:$id",
        kind = "外出",
        dest = destination ?: reason ?: "—",
        from = outingDate,
        to = outingDate,
        status = mapApplicationStatus4(status),
        reason = reason ?: "",
        createdAt = submittedAt,
    )

// 承认链单步 ApprovalStepOut → 本地 StayApprovalStep。DTO 不含担当者姓名，approverName 置 null。
private fun ApprovalStepOut.toStayStep(): StayApprovalStep =
    StayApprovalStep(
        role = approverRole,
        approverName = null,
        decision = mapDecisionName(decision),
        decidedAt = decidedAt,
        comment = comment,
    )

// ApplicationOut → 本地 StayApplication（StayListScreen / StayDetailScreen 用）。
// destination / summary 取 stay_locations[0].name（不是 dest_cities）。
// auditLog 默认空；详情页另调 ApplicationsAPI.audit 填入。
fun ApplicationOut.toStayApplication(): StayApplication {
    val firstLoc = firstStayLocationName(this)
    return StayApplication(
        id = id,
        kind = kind,
        status = mapStayStatus(status).name,
        leaveDate = leaveDate,
        returnDate = returnDate,
        summary = makeStaySummary(this),
        destination = firstLoc,
        leaveMethod = leaveMethod,
        returnMethod = returnMethod,
        taxiReservationTime = taxiReservationTime,
        chain = approvalChain.map { it.toStayStep() },
        submittedAt = submittedAt,
        auditLog = emptyList(),
    )
}

// AuditLogOut → StayAuditEntry（对齐 iOS AuditLogOut.toAuditLogEntry）
fun AuditLogOut.toStayAuditEntry(studentName: String): StayAuditEntry {
    val actionLabel = translateAuditAction(action)
    val actorLabel = if (actorType == "student") studentName else "教員"
    val detailText =
        payload?.get("amend_reason")?.jsonPrimitive?.contentOrNull
            ?: payload?.get("reason")?.jsonPrimitive?.contentOrNull
            ?: payload?.get("comment")?.jsonPrimitive?.contentOrNull
    return StayAuditEntry(
        at = formatAuditAt(createdAt),
        action = actionLabel,
        actor = actorLabel,
        detail = detailText?.takeIf { it.isNotEmpty() },
    )
}

// 后端 action 关键字 → UI 日语文案（对齐 iOS translateAction）
fun translateAuditAction(raw: String): String =
    when (raw) {
        "application.submit" -> "提出"
        "application.amend", "application.update" -> "変更届を提出"
        "application.approve" -> "承認"
        "application.reject" -> "差し戻し"
        "application.withdraw" -> "取消"
        else -> raw
    }

// created_at ISO → 显示用 yyyy-MM-dd HH:mm（截取常见形态；已是显示形则原样）
private fun formatAuditAt(raw: String): String {
    val normalized = raw.replace('T', ' ')
    return when {
        normalized.length >= 16 -> normalized.substring(0, 16)
        else -> raw
    }
}
