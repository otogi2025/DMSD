package jp.tomoshibi.android.ui.screens.applications

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.StayApplication
import jp.tomoshibi.android.data.model.StayApprovalStep
import jp.tomoshibi.android.data.model.StayAuditEntry
import jp.tomoshibi.android.data.model.StayDecision
import jp.tomoshibi.android.data.model.StayKind
import jp.tomoshibi.android.data.model.StayStatus
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.ApplicationsAPI
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import jp.tomoshibi.android.ui.theme.SuzuTokens
import kotlinx.coroutines.launch

// ─────────────────────────────────────────────────────────────────────
// StayDetailScreen —— 「申請詳細」（申請内容 + 承認状況 timeline + 操作履歴）
// 対齐 iOS StayDetailView（StayListStubs.swift 行 676-1171）。
// iOS 原本带「詳細 / 履歴」分页切换；Android 端把三块铺在同一滚动列里（任务区块定义）：
//   1) Header 卡：种类图标 +「<种类>届」+ 状态徽章
//   2) 申請内容卡：出寮日 / 帰寮日 / 帰省方法 / 帰寮方法 / タクシー予約 / 宿泊先 / 提出日時 键值行
//   3) 承認状況 timeline：chain 每环 役职名 + 决定 Pill + 担当者 + 时刻 + 审查中标记
//   4) 差戻评语卡：chain 里最后一个带 comment 的环（红底警告）
//   5) 操作履歴：auditLog 逐条 at / action / actor / detail（竖线串联的时间轴）
// 数据从真后端 ApplicationsAPI.detail(id) 拉单条 ApplicationOut，再 .toStayApplication() 转本地模型。
// 套三态外壳（加载中 / 失败 / 成功）；详情屏是单条，不需要 Empty 态，找不到 / 异常都走 FailedBox。
// isEditable 为 true 时底部「変更届を提出」按钮 → 跳 StayEdit 路由。
// ─────────────────────────────────────────────────────────────────────

@Composable
fun StayDetailScreen(
    navController: NavHostController,
    id: String,
) {
    val t = SuzuT.current
    val scope = rememberCoroutineScope()
    // 三态：Loading / Failed(消息) / Success(映射后的 StayApplication)。详情单条不设 Empty。
    var ui by remember { mutableStateOf<LoadState<StayApplication>>(LoadState.Loading) }

    // 撤回中标志（防重复点击 + 按钮显示禁用态）。撤回失败时把后端消息落到 actionError 给用户看。
    var withdrawing by remember { mutableStateOf(false) }
    var actionError by remember { mutableStateOf<String?>(null) }

    // 加载函数（重试也调它）。失败必须落 Failed，绝不退化成假数据。
    suspend fun load() {
        ui = LoadState.Loading
        ui =
            try {
                // GET /applications/:id → ApplicationOut，经共享映射转成界面用的 StayApplication
                val item = ApplicationsAPI.detail(id).toStayApplication()
                LoadState.Success(item)
            } catch (e: ApiError) {
                LoadState.Failed(e.display)
            } catch (e: Exception) {
                LoadState.Failed("読み込みに失敗しました")
            }
    }
    LaunchedEffect(Unit) { load() }

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .background(t.pearl)
                    .verticalScroll(rememberScrollState()),
        ) {
            PageHeader(
                title = "申請詳細",
                level = 2,
                onLeft = { navController.popBackStack() },
            )

            // 三态渲染（详情屏只有 Loading / Failed / Success）
            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox()
                }

                is LoadState.Failed -> {
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }

                // Empty 态详情屏用不到（detail 永远是单条），理论上不会进这分支；兜底当失败处理
                LoadState.Empty -> {
                    FailedBox("読み込みに失敗しました", onRetry = { scope.launch { load() } })
                }

                is LoadState.Success -> {
                    val item = s.value
                    Column(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 16.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp),
                    ) {
                        Spacer(Modifier.height(2.dp))

                        HeaderCard(t, item)
                        FieldsCard(t, item)
                        ChainCard(t, item)

                        // chain 里最后一个带评语的环 → 差戻评语卡
                        val lastComment = item.chain.lastOrNull { !it.comment.isNullOrBlank() }
                        if (lastComment != null) {
                            CommentCard(t, lastComment)
                        }

                        HistoryCard(t, item)

                        // ── 底部操作区 ──
                        // 编辑（变更届 / 再提出）可提交时露出。状态决定按钮文案：
                        //   要修正（returned）→「修正して再提出」（差戻后改完重提，语义对齐 iOS）
                        //   其余可编辑态（pending / approved_partial）→「変更届を提出」
                        // 两者都走既有编辑流程（StayEdit → PUT /applications/:id，重提=改完回 pending）。
                        if (item.isEditable) {
                            val isReturned = item.status == StayStatus.RETURNED.name
                            PrimaryButton(
                                title = if (isReturned) "修正して再提出" else "変更届を提出",
                                icon = SuzuIcons.Edit,
                                enabled = !withdrawing,
                                onClick = { navController.navigate(Route.StayEdit(id).path) },
                            )
                        }

                        // 撤回（取消）可执行时露出红色危险按钮 → POST /applications/:id/withdraw。
                        // 仅 pending / approved_partial / returned 可撤回（跟后端 CANNOT_WITHDRAW 约束一致，
                        // 复用 isEditable 的同一状态集合）。点击 → 调 withdraw → 成功后 reload 拉到 withdrawn 态。
                        if (item.isEditable) {
                            PrimaryButton(
                                title = if (withdrawing) "取消中…" else "取消（撤回）",
                                icon = SuzuIcons.Close,
                                destructive = true,
                                enabled = !withdrawing,
                                onClick = {
                                    scope.launch {
                                        withdrawing = true
                                        actionError = null
                                        try {
                                            ApplicationsAPI.withdraw(id)
                                            // 撤回成功 → 重新拉详细（状态会变 取消済，按钮随之消失）
                                            load()
                                        } catch (e: ApiError) {
                                            actionError = e.display
                                        } catch (e: Exception) {
                                            actionError = "取消に失敗しました"
                                        } finally {
                                            withdrawing = false
                                        }
                                    }
                                },
                            )
                            // 撤回失败时把后端消息（如 409 的拒绝理由）显示在按钮下方
                            actionError?.let {
                                Text(
                                    it,
                                    color = t.danger,
                                    style = TextStyle(fontSize = 12.sp),
                                )
                            }
                        }

                        Spacer(Modifier.height(40.dp))
                    }
                }
            }
        }
    }
}

// ════════════════════════════════════════════════════════════════════
// Header 卡 —— 种类图标方块 +「<种类>届」+ 状态徽章 Pill
// ════════════════════════════════════════════════════════════════════
@Composable
private fun HeaderCard(
    t: SuzuTokens,
    item: StayApplication,
) {
    SuzuCard(padding = 18) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            // 种类图标方块（44dp 圆角 12 pill 底 + 主色图标）
            Box(
                modifier =
                    Modifier
                        .size(44.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(t.pill),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = kindIcon(item.kind),
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(18.dp),
                )
            }
            Spacer(Modifier.width(12.dp))
            // kind 已是 StayKind.label（日语显示名），后缀「届」对齐 iOS
            Text(
                "${item.kind}届",
                color = t.ink,
                style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.ExtraBold),
            )
            Spacer(Modifier.weight(1f))
            // 状态徽章：StayStatus.label 文字 + 任务给定的色调映射
            val status = StayStatus.valueOf(item.status)
            Pill(text = status.label, tone = statusTone(status))
        }
    }
}

// ════════════════════════════════════════════════════════════════════
// 申請内容卡 —— 键值行列表（按 iOS fieldsCard 顺序，可空字段缺省不显示）
// ════════════════════════════════════════════════════════════════════
@Composable
private fun FieldsCard(
    t: SuzuTokens,
    item: StayApplication,
) {
    SuzuCard(padding = 16) {
        Column(modifier = Modifier.fillMaxWidth()) {
            // 小标题「申請内容」（全大写效果靠字间距，文案保持日语原文）
            Text(
                "申請内容",
                color = t.inkSub,
                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.2.sp),
            )
            Spacer(Modifier.height(12.dp))

            FieldRow(t, "出寮日", item.leaveDate, first = true)
            item.returnDate?.let { FieldRow(t, "帰寮日", it) }
            item.leaveMethod?.let { FieldRow(t, "帰省方法", it) }
            item.returnMethod?.let { FieldRow(t, "帰寮方法", it) }
            item.taxiReservationTime?.let { FieldRow(t, "タクシー予約", it) }
            item.destination?.let { FieldRow(t, "宿泊先", it) }
            FieldRow(t, "提出日時", item.submittedAt)
        }
    }
}

// 键值行（左标签 inkSub + 右值 ink 加粗右对齐；非首行顶部 0.5 细线分隔）
@Composable
private fun FieldRow(
    t: SuzuTokens,
    label: String,
    value: String,
    first: Boolean = false,
) {
    if (!first) {
        Box(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .padding(vertical = 9.dp)
                    .height(0.5.dp)
                    .background(t.hair),
        )
    }
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.Top,
    ) {
        Text(label, color = t.inkSub, style = TextStyle(fontSize = 13.sp))
        Spacer(Modifier.weight(1f))
        Text(
            value,
            color = t.ink,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
        )
    }
}

// ════════════════════════════════════════════════════════════════════
// 承認状況卡 ——「承認の流れ」标题 + 已承認/总数 计数 + 竖向 timeline
// ════════════════════════════════════════════════════════════════════
@Composable
private fun ChainCard(
    t: SuzuTokens,
    item: StayApplication,
) {
    SuzuCard(padding = 18) {
        Column(modifier = Modifier.fillMaxWidth()) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "承認の流れ",
                    color = t.inkSub,
                    style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.2.sp),
                )
                Spacer(Modifier.weight(1f))
                // 已承認环数 / 总环数（等宽字体）
                val approvedCount = item.chain.count { it.decision == StayDecision.APPROVED.name }
                Text(
                    "$approvedCount / ${item.chain.size}",
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.SemiBold, fontFamily = FontFamily.Monospace),
                )
            }
            Spacer(Modifier.height(14.dp))

            if (item.chain.isEmpty()) {
                Text(
                    "この種別の届は承認手続きの設定がありません。",
                    color = t.inkMute,
                    style = TextStyle(fontSize = 12.sp),
                )
            } else {
                item.chain.forEachIndexed { index, step ->
                    ChainRow(t, step, isLast = index == item.chain.size - 1)
                }
            }
        }
    }
}

// 承認链一环 —— 左侧圆点+竖线轨道 + 右侧 役职名/决定 Pill/担当者/时刻/审查中
@Composable
private fun ChainRow(
    t: SuzuTokens,
    step: StayApprovalStep,
    isLast: Boolean,
) {
    val decision = StayDecision.valueOf(step.decision)
    Row(modifier = Modifier.fillMaxWidth()) {
        // ── 左轨道：状态圆点（26dp）+ 下方竖线 ──
        Column(
            modifier = Modifier.width(26.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Box(
                modifier =
                    Modifier
                        .size(26.dp)
                        .clip(RoundedCornerShape(percent = 50))
                        .background(circleFill(t, decision)),
                contentAlignment = Alignment.Center,
            ) {
                when (decision) {
                    StayDecision.APPROVED -> {
                        Icon(
                            SuzuIcons.Check,
                            contentDescription = null,
                            tint = Color.White,
                            modifier = Modifier.size(14.dp),
                        )
                    }

                    // 差戻 = iOS xmark；SuzuIcons 无 X，用白色「✕」字符渲染
                    StayDecision.REJECTED -> {
                        Text(
                            "✕",
                            color = Color.White,
                            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.ExtraBold),
                        )
                    }

                    // 審査中 = 中央小白点
                    StayDecision.PENDING -> {
                        Box(
                            modifier =
                                Modifier
                                    .size(8.dp)
                                    .clip(RoundedCornerShape(percent = 50))
                                    .background(Color.White),
                        )
                    }
                }
            }
            // 非末环：圆点下方竖线（已承認 = ok 绿 / 其余 = hair 灰）
            if (!isLast) {
                Box(
                    modifier =
                        Modifier
                            .padding(top = 4.dp)
                            .width(2.dp)
                            .height(40.dp)
                            .background(if (decision == StayDecision.APPROVED) t.ok else t.hair),
                )
            }
        }

        Spacer(Modifier.width(14.dp))

        // ── 右侧正文 ──
        Column(
            modifier = Modifier.padding(bottom = if (isLast) 0.dp else 18.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                // role 已是 StayApprovalRole.label（日语役职名）
                Text(
                    step.role,
                    color = t.ink,
                    style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                )
                Spacer(Modifier.width(8.dp))
                Pill(text = decision.label, tone = decisionTone(decision))
            }
            step.approverName?.let {
                Text("担当：$it", color = t.inkSub, style = TextStyle(fontSize = 12.sp))
            }
            step.decidedAt?.let {
                Text(
                    it,
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
                )
            }
            if (decision == StayDecision.PENDING) {
                Text("審査中", color = t.warnDeep, style = TextStyle(fontSize = 12.sp))
            }
        }
    }
}

// ════════════════════════════════════════════════════════════════════
// 差戻评语卡 —— chain 里最后一个带 comment 的环（红底警告框）
// ════════════════════════════════════════════════════════════════════
@Composable
private fun CommentCard(
    t: SuzuTokens,
    step: StayApprovalStep,
) {
    Box(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(14.dp))
                .background(t.dangerBg)
                .border(1.dp, t.danger.copy(alpha = 0.25f), RoundedCornerShape(14.dp))
                .padding(horizontal = 16.dp, vertical = 14.dp),
    ) {
        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("⚠", color = t.danger, style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold))
                Spacer(Modifier.width(6.dp))
                // role 已是日语役职名 —「<役职> からのコメント」
                Text(
                    "${step.role} からのコメント",
                    color = t.danger,
                    style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold),
                )
            }
            Text(
                step.comment ?: "",
                color = t.ink,
                style = TextStyle(fontSize = 13.sp, lineHeight = 19.sp),
            )
        }
    }
}

// ════════════════════════════════════════════════════════════════════
// 操作履歴卡 ——「操作履歴」标题 + 件数 + 逐条时间轴（at / action / actor / detail）
// ════════════════════════════════════════════════════════════════════
@Composable
private fun HistoryCard(
    t: SuzuTokens,
    item: StayApplication,
) {
    SuzuCard(padding = 18) {
        Column(modifier = Modifier.fillMaxWidth()) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "操作履歴",
                    color = t.inkSub,
                    style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.2.sp),
                )
                Spacer(Modifier.weight(1f))
                Text(
                    "${item.auditLog.size} 件",
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.SemiBold, fontFamily = FontFamily.Monospace),
                )
            }
            Spacer(Modifier.height(14.dp))

            if (item.auditLog.isEmpty()) {
                Text(
                    "履歴はまだありません。",
                    color = t.inkMute,
                    style = TextStyle(fontSize = 12.sp),
                )
            } else {
                item.auditLog.forEachIndexed { index, entry ->
                    AuditRow(t, entry, isLast = index == item.auditLog.size - 1)
                }
            }
        }
    }
}

// 操作履历一条 —— 左侧色点+竖线轨道 + 右侧 action/at/actor/detail
@Composable
private fun AuditRow(
    t: SuzuTokens,
    entry: StayAuditEntry,
    isLast: Boolean,
) {
    // 主色（teal）— 履历默认分支（如「提出」）用；在此 @Composable 上下文读 MaterialTheme
    val primary = MaterialTheme.colorScheme.primary
    Row(modifier = Modifier.fillMaxWidth()) {
        // ── 左轨道：按 action 着色的小圆点（10dp）+ 下方竖线 ──
        Column(
            modifier = Modifier.width(10.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Spacer(Modifier.height(4.dp))
            Box(
                modifier =
                    Modifier
                        .size(10.dp)
                        .clip(RoundedCornerShape(percent = 50))
                        .background(auditColor(t, entry.action, primary)),
            )
            if (!isLast) {
                Box(
                    modifier =
                        Modifier
                            .padding(top = 4.dp)
                            .width(1.5.dp)
                            .height(36.dp)
                            .background(t.hair),
                )
            }
        }

        Spacer(Modifier.width(12.dp))

        // ── 右侧正文 ──
        Column(
            modifier = Modifier.padding(bottom = if (isLast) 0.dp else 14.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                // action 值即 UI 文案（如「提出」「承認」「差戻」「変更届を提出」）
                Text(entry.action, color = t.ink, style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold))
                Spacer(Modifier.width(8.dp))
                Text(
                    entry.at,
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
                )
            }
            Text(entry.actor, color = t.inkSub, style = TextStyle(fontSize = 12.sp))
            // detail（变更届理由 / 差戻理由）非空时灰底小框展示
            if (!entry.detail.isNullOrBlank()) {
                Box(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(8.dp))
                            .background(t.pill)
                            .padding(horizontal = 10.dp, vertical = 7.dp),
                ) {
                    Text(
                        entry.detail,
                        color = t.inkSub,
                        style = TextStyle(fontSize = 12.sp, lineHeight = 18.sp),
                    )
                }
            }
        }
    }
}

// ════════════════════════════════════════════════════════════════════
// 私有辅助 —— 色调映射 / 图标映射 / 圆点填充 / 履历着色
// ════════════════════════════════════════════════════════════════════

// 状态 → Pill 色调（任务给定映射）
private fun statusTone(status: StayStatus): PillTone =
    when (status) {
        StayStatus.DRAFT -> PillTone.Neutral
        StayStatus.PENDING -> PillTone.Warn
        StayStatus.APPROVED_PARTIAL -> PillTone.Warn
        StayStatus.APPROVED -> PillTone.Ok
        StayStatus.REJECTED -> PillTone.Danger
        StayStatus.RETURNED -> PillTone.Danger
        StayStatus.WITHDRAWN -> PillTone.Neutral
    }

// 承認決定 → Pill 色调（PENDING 橙 / APPROVED 绿 / REJECTED 红）
private fun decisionTone(decision: StayDecision): PillTone =
    when (decision) {
        StayDecision.PENDING -> PillTone.Warn
        StayDecision.APPROVED -> PillTone.Ok
        StayDecision.REJECTED -> PillTone.Danger
    }

// 承認链圆点填充色（已承認 ok 绿 / 差戻 danger 红 / 审查中 inkFaint 灰）
private fun circleFill(
    t: SuzuTokens,
    decision: StayDecision,
): Color =
    when (decision) {
        StayDecision.APPROVED -> t.ok
        StayDecision.REJECTED -> t.danger
        StayDecision.PENDING -> t.inkFaint
    }

// 操作履历圆点着色（按 action 文案关键字 — 对齐 iOS auditColor）
// primary 由调用方在 @Composable 上下文传入（纯函数不能读 MaterialTheme）
private fun auditColor(
    t: SuzuTokens,
    action: String,
    primary: Color,
): Color =
    when {
        action.contains("承認") -> t.ok

        // 「承認」绿
        action.contains("差戻") -> t.danger

        // 「差戻」红
        action.contains("変更") -> t.warn

        // 「変更届を提出」橙
        else -> primary // 其余（如「提出」）主色 teal
    }

// 种类 → 图标（kind 是 StayKind.label，按 label 反查类型）
private fun kindIcon(kindLabel: String): ImageVector =
    when (kindLabel) {
        StayKind.STAY.label -> SuzuIcons.House

        // 外泊 = house
        StayKind.HOLIDAY.label -> SuzuIcons.House

        // 帰省 = house.lodge → House
        StayKind.RETURN.label -> SuzuIcons.Plane

        // 帰国 = airplane → Plane
        else -> SuzuIcons.Doc // その他 = doc.text → Doc
    }
