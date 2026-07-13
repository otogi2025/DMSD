package jp.tomoshibi.android.ui.screens.applications

import jp.tomoshibi.android.data.model.Application
import jp.tomoshibi.android.data.model.ApplicationStatus
import jp.tomoshibi.android.data.model.StayApplication
import jp.tomoshibi.android.data.model.StayApprovalStep
import jp.tomoshibi.android.data.model.StayDecision
import jp.tomoshibi.android.data.model.StayStatus
import jp.tomoshibi.android.data.network.ApplicationOut
import jp.tomoshibi.android.data.network.ApprovalStepOut

// ApplicationMappers.kt
// 出寮届 DTO（data/network/ApplicationOut）→ 各申請屏现有 UI 本地模型（data/model）的映射，集中在此各屏共用。
//
// 为什么要映射层：后端 ApplicationOut 的 status 是英语小写蛇形（"pending"/"approved_partial"/...），
// 承認链 decision 是 "approve"/"reject"/null；而界面用的本地枚举（ApplicationStatus / StayStatus / StayDecision）
// 是大写名。两套形状不同，集中在这里转一次，列表/详情屏只管「调 API → 映射 → 套三态」，UI 代码完全不动。

// 后端 status 英语 → ApplicationStatus（4 值，ApplicationsScreen / ApplicationDetailScreen 用）。
// 后端 7 状态压到 4：approved_partial 也归 APPROVED；withdrawn 归 REJECTED 兜底（已撤回一般不出现在主列表）。
fun mapApplicationStatus4(backend: String): ApplicationStatus =
    when (backend) {
        "pending" -> ApplicationStatus.PENDING
        "approved", "approved_partial" -> ApplicationStatus.APPROVED
        "returned" -> ApplicationStatus.RETURNED
        else -> ApplicationStatus.REJECTED // rejected / withdrawn
    }

// ApplicationStatus 枚举 → 状态徽章（chip）文案。原散在 ApplicationStatusPill 的 when 里，抽出成纯函数可单测。
// iOS rejected 标签是「差戻」（不是「却下」）—— 双端徽章文案对齐。
fun applicationStatusLabel(status: ApplicationStatus): String =
    when (status) {
        ApplicationStatus.PENDING -> "審査中"
        ApplicationStatus.APPROVED -> "承認済"
        ApplicationStatus.RETURNED -> "要修正"
        ApplicationStatus.REJECTED -> "差戻"
    }

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

// 承認链单步 decision 英语 → StayDecision.name（"approve"→APPROVED / "reject"→REJECTED / null（未决）→PENDING）。
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
// summary 取 dest_cities，退而取 reason，再退「<种别>届」；auditLog 需单独 GET /applications/:id/audit，
// 列表/详情默认置空（操作履历卡空态会显示「履歴はまだありません」）。
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
