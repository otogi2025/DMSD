package jp.tomoshibi.android.ui.screens.applications

import jp.tomoshibi.android.data.model.Application
import jp.tomoshibi.android.data.model.ApplicationStatus
import jp.tomoshibi.android.data.model.StayApplication
import jp.tomoshibi.android.data.model.StayApprovalStep
import jp.tomoshibi.android.data.model.StayDecision
import jp.tomoshibi.android.data.model.StayStatus
import jp.tomoshibi.android.data.network.ApplicationOut
import jp.tomoshibi.android.data.network.ApprovalStepOut
import jp.tomoshibi.android.data.network.endpoints.OutingOut

// ApplicationMappers.kt
// 出寮届 / 外出 DTO → 各申請屏现有 UI 本地模型的映射，集中在此各屏共用。
//
// 为什么要映射层：后端 status 是英语小写蛇形（"pending"/"approved_partial"/...），
// 承認链 decision 是 "approve"/"reject"/null；而界面用的本地枚举是大写名。
// 两套形状不同，集中在这里转一次，列表/详情屏只管「调 API → 映射 → 套三态」。

// 后端 status 英语 → ApplicationStatus（申请一览 / ApplicationDetail 用）。
// approved_partial 归 APPROVED；withdrawn 独立为 WITHDRAWN（勿标成差戻）。
fun mapApplicationStatus4(backend: String): ApplicationStatus =
    when (backend) {
        "pending" -> ApplicationStatus.PENDING
        "approved", "approved_partial" -> ApplicationStatus.APPROVED
        "returned" -> ApplicationStatus.RETURNED
        "withdrawn" -> ApplicationStatus.WITHDRAWN
        "rejected" -> ApplicationStatus.REJECTED
        else -> ApplicationStatus.REJECTED
    }

// ApplicationStatus 枚举 → 状态徽章文案（对齐 iOS statusPair）。
fun applicationStatusLabel(status: ApplicationStatus): String =
    when (status) {
        ApplicationStatus.PENDING -> "審査中"
        ApplicationStatus.APPROVED -> "承認済"
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

// 承認链单步 decision 英语 → StayDecision.name。
private fun mapDecisionName(d: String?): String =
    when (d) {
        "approve" -> StayDecision.APPROVED.name
        "reject" -> StayDecision.REJECTED.name
        else -> StayDecision.PENDING.name
    }

// ApplicationOut → 本地 Application（ApplicationsScreen 列表 / ApplicationDetailScreen 用）。
// kind 后端已是日语「帰省/外泊/帰国」，直接用；行先取 dest_cities，退而取 reason，再退「—」。
fun ApplicationOut.toUiApplication(): Application =
    Application(
        id = id,
        kind = kind,
        dest = destCities ?: reason ?: "—",
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

// 承認链单步 ApprovalStepOut → 本地 StayApprovalStep。DTO 不含担当者姓名，approverName 置 null。
private fun ApprovalStepOut.toStayStep(): StayApprovalStep =
    StayApprovalStep(
        role = approverRole,
        approverName = null,
        decision = mapDecisionName(decision),
        decidedAt = decidedAt,
        comment = comment,
    )

// ApplicationOut → 本地 StayApplication（StayListScreen / StayDetailScreen 用）。
fun ApplicationOut.toStayApplication(): StayApplication =
    StayApplication(
        id = id,
        kind = kind,
        status = mapStayStatus(status).name,
        leaveDate = leaveDate,
        returnDate = returnDate,
        summary = destCities ?: reason ?: "${kind}届",
        destination = destCities,
        leaveMethod = leaveMethod,
        returnMethod = returnMethod,
        taxiReservationTime = taxiReservationTime,
        chain = approvalChain.map { it.toStayStep() },
        submittedAt = submittedAt,
        auditLog = emptyList(),
    )
