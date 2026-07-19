package jp.tomoshibi.android.ui.screens.applications

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Divider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.ApplicationStatus
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.ApplicationOut
import jp.tomoshibi.android.data.network.ApprovalStepOut
import jp.tomoshibi.android.data.network.endpoints.ApplicationsAPI
import jp.tomoshibi.android.data.network.endpoints.OutingOut
import jp.tomoshibi.android.data.network.endpoints.OutingsAPI
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 承認チェーン 1 步 — 役職 / 状态 / 时间戳
private data class ChainStep(
    val role: String,
    val state: String /* approved/pending/idle */,
    val ts: String?,
)

// 详情载荷：出寮届 ApplicationOut，或外出 OutingOut（列表 id 带 "outing:" 前缀）
private sealed class DetailPayload {
    data class App(
        val dto: ApplicationOut,
    ) : DetailPayload()

    data class Outing(
        val dto: OutingOut,
    ) : DetailPayload()
}

@Composable
fun ApplicationDetailScreen(
    navController: NavHostController,
    id: String,
) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()

    var ui by remember { mutableStateOf<LoadState<DetailPayload>>(LoadState.Loading) }
    var withdrawing by remember { mutableStateOf(false) }
    var actionError by remember { mutableStateOf<String?>(null) }

    val isOuting = id.startsWith("outing:")
    val rawOutingId = id.removePrefix("outing:")

    suspend fun load() {
        ui = LoadState.Loading
        val tokenAtStart = store.snapshot().authToken
        ui =
            try {
                if (isOuting) {
                    LoadState.Success(DetailPayload.Outing(OutingsAPI.detail(rawOutingId)))
                } else {
                    LoadState.Success(DetailPayload.App(ApplicationsAPI.detail(id)))
                }
            } catch (e: ApiError) {
                if (store.handleIfUnauthorized(e, tokenAtStart)) {
                    return
                }
                LoadState.Failed(e.display)
            } catch (e: Exception) {
                LoadState.Failed("読み込みに失敗しました")
            }
    }
    LaunchedEffect(id) { load() }

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(top = 24.dp, bottom = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    modifier = Modifier.size(36.dp).clip(CircleShape).clickable { navController.popBackStack() },
                    contentAlignment = Alignment.Center,
                ) {
                    Text("←", color = tokens.ink, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.SemiBold))
                }
                Spacer(Modifier.width(8.dp))
                Text("申請詳細", color = tokens.ink, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold))
            }

            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox()
                }

                is LoadState.Failed -> {
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }

                LoadState.Empty -> {
                    FailedBox("読み込みに失敗しました", onRetry = { scope.launch { load() } })
                }

                is LoadState.Success -> {
                    when (val payload = s.value) {
                        is DetailPayload.Outing -> {
                            OutingDetailBody(
                                tokens = tokens,
                                outing = payload.dto,
                                withdrawing = withdrawing,
                                actionError = actionError,
                                onWithdraw = {
                                    scope.launch {
                                        withdrawing = true
                                        actionError = null
                                        val tokenAtStart = store.snapshot().authToken
                                        try {
                                            OutingsAPI.withdraw(rawOutingId)
                                            load()
                                        } catch (e: ApiError) {
                                            if (store.handleIfUnauthorized(e, tokenAtStart)) return@launch
                                            // 409 等：重拉最新状态，提示「確認待ちの申請のみ取り消せます」
                                            actionError =
                                                if (e is ApiError.Server && e.code == 409) {
                                                    "確認待ちの申請のみ取り消せます"
                                                } else {
                                                    e.display
                                                }
                                            load()
                                        } catch (e: Exception) {
                                            actionError = "取消に失敗しました"
                                        } finally {
                                            withdrawing = false
                                        }
                                    }
                                },
                            )
                        }

                        is DetailPayload.App -> {
                            ApplicationDetailBody(
                                tokens = tokens,
                                dto = payload.dto,
                                userStudentNo = state.user.studentNo,
                                userName = state.user.name,
                                userGradeClass = state.user.gradeClass,
                                userDorm = state.user.dorm,
                                userRoom = state.user.room,
                                userCategory = state.user.category,
                                withdrawing = withdrawing,
                                actionError = actionError,
                                onEdit = { navController.navigate(Route.StayEdit(id).path) },
                                onWithdraw = {
                                    scope.launch {
                                        withdrawing = true
                                        actionError = null
                                        val tokenAtStart = store.snapshot().authToken
                                        try {
                                            ApplicationsAPI.withdraw(id)
                                            load()
                                        } catch (e: ApiError) {
                                            if (store.handleIfUnauthorized(e, tokenAtStart)) return@launch
                                            actionError = e.display
                                        } catch (e: Exception) {
                                            actionError = "取消に失敗しました"
                                        } finally {
                                            withdrawing = false
                                        }
                                    }
                                },
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun ApplicationDetailBody(
    tokens: jp.tomoshibi.android.ui.theme.SuzuTokens,
    dto: ApplicationOut,
    userStudentNo: String,
    userName: String,
    userGradeClass: String,
    userDorm: String,
    userRoom: String,
    userCategory: String,
    withdrawing: Boolean,
    actionError: String?,
    onEdit: () -> Unit,
    onWithdraw: () -> Unit,
) {
    val app = dto.toUiApplication()
    // 可编辑 / 可撤回：以后端裸 status 为准（pending / approved_partial / returned）
    val actionable = dto.status in setOf("pending", "approved_partial", "returned")
    val isStayKind = app.kind in setOf("外泊", "帰省", "帰国")

    Column(
        modifier =
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        Row(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(14.dp))
                    .background(tokens.paper)
                    .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier =
                    Modifier
                        .clip(RoundedCornerShape(6.dp))
                        .background(tokens.pill)
                        .padding(horizontal = 8.dp, vertical = 2.dp),
            ) {
                Text(
                    app.kind,
                    color = tokens.ink,
                    style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold),
                )
            }
            Spacer(Modifier.width(8.dp))
            ApplicationStatusPill(app.status, kind = app.kind)
            Spacer(Modifier.weight(1f))
            Text(
                "#${app.id.take(8)}",
                color = tokens.inkMute,
                style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
            )
        }

        Section("申請者本人")
        Column(
            modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(tokens.paper),
        ) {
            KvRow("学号", userStudentNo, mono = true)
            Divider(color = tokens.hair, thickness = 0.5.dp)
            KvRow("氏名", userName)
            Divider(color = tokens.hair, thickness = 0.5.dp)
            KvRow("学年・組", userGradeClass)
            Divider(color = tokens.hair, thickness = 0.5.dp)
            KvRow("寮・部屋", "$userDorm $userRoom")
            Divider(color = tokens.hair, thickness = 0.5.dp)
            KvRow("区分", userCategory)
        }

        Section("申請内容")
        Column(
            modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(tokens.paper),
        ) {
            KvRow("種類", app.kind)
            Divider(color = tokens.hair, thickness = 0.5.dp)
            KvRow("行先", app.dest)
            Divider(color = tokens.hair, thickness = 0.5.dp)
            KvRow("期間", if (app.from == app.to) app.from else "${app.from} 〜 ${app.to}")
            Divider(color = tokens.hair, thickness = 0.5.dp)
            KvRow("理由", app.reason)
            Divider(color = tokens.hair, thickness = 0.5.dp)
            KvRow("提出日", app.createdAt)
        }

        Section("承認の流れ")
        val chain = chainFromBackend(dto.approvalChain)
        Column(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(14.dp))
                    .background(tokens.paper)
                    .padding(vertical = 8.dp),
        ) {
            chain.forEachIndexed { idx, step ->
                ChainRow(step, isLast = idx == chain.lastIndex)
            }
        }

        // 修改届入口（仅出寮三类 + 可编辑状态）
        if (actionable && isStayKind) {
            val editTitle = if (dto.status == "returned") "修正して再提出" else "変更届を提出"
            Box(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .height(48.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(tokens.ink)
                        .clickable(enabled = !withdrawing, onClick = onEdit),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    editTitle,
                    color = Color.White,
                    style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                )
            }
        }

        // 撤回：POST /applications/:id/withdraw
        if (actionable) {
            Box(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .height(48.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .border(1.5.dp, tokens.danger.copy(alpha = 0.4f), RoundedCornerShape(12.dp))
                        .clickable(enabled = !withdrawing, onClick = onWithdraw),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    if (withdrawing) "取消中…" else "申請を撤回する",
                    color = tokens.danger,
                    style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                )
            }
            actionError?.let {
                Text(it, color = tokens.danger, style = TextStyle(fontSize = 12.sp))
            }
        }
        Spacer(Modifier.height(40.dp))
    }
}

@Composable
private fun OutingDetailBody(
    tokens: jp.tomoshibi.android.ui.theme.SuzuTokens,
    outing: OutingOut,
    withdrawing: Boolean,
    actionError: String?,
    onWithdraw: () -> Unit,
) {
    val status = mapApplicationStatus4(outing.status)
    Column(
        modifier =
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        Row(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(14.dp))
                    .background(tokens.paper)
                    .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier =
                    Modifier
                        .clip(RoundedCornerShape(6.dp))
                        .background(tokens.pill)
                        .padding(horizontal = 8.dp, vertical = 2.dp),
            ) {
                Text("外出", color = tokens.ink, style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold))
            }
            Spacer(Modifier.width(8.dp))
            ApplicationStatusPill(status, kind = "外出")
        }

        Section("申請内容")
        Column(
            modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(tokens.paper),
        ) {
            KvRow("外出日", outing.outingDate)
            Divider(color = tokens.hair, thickness = 0.5.dp)
            KvRow("行き先", outing.destination ?: "—")
            Divider(color = tokens.hair, thickness = 0.5.dp)
            KvRow("外出時刻", outing.leaveTime ?: "—")
            Divider(color = tokens.hair, thickness = 0.5.dp)
            KvRow("帰寮予定時刻", outing.returnTime ?: "—")
            Divider(color = tokens.hair, thickness = 0.5.dp)
            KvRow("タクシー予約", outing.taxiReservationTime ?: "なし")
            Divider(color = tokens.hair, thickness = 0.5.dp)
            KvRow("理由", outing.reason ?: "—")
            Divider(color = tokens.hair, thickness = 0.5.dp)
            KvRow("提出日", outing.submittedAt)
            if (outing.confirmedByName != null) {
                Divider(color = tokens.hair, thickness = 0.5.dp)
                KvRow("確認", outing.confirmedByName)
            }
        }

        // 仅 pending 可撤（对齐 iOS OutingDetailView）
        if (outing.status == "pending") {
            Box(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .height(48.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .border(1.5.dp, tokens.danger.copy(alpha = 0.4f), RoundedCornerShape(12.dp))
                        .clickable(enabled = !withdrawing, onClick = onWithdraw),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    if (withdrawing) "取消中…" else "申請を撤回する",
                    color = tokens.danger,
                    style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                )
            }
            actionError?.let {
                Text(it, color = tokens.danger, style = TextStyle(fontSize = 12.sp))
            }
        }
        Spacer(Modifier.height(40.dp))
    }
}

private fun chainFromBackend(steps: List<ApprovalStepOut>): List<ChainStep> =
    steps.map { step ->
        val state =
            when (step.decision) {
                "approve" -> "approved"
                "reject" -> "rejected"
                else -> "pending"
            }
        ChainStep(role = step.approverRole, state = state, ts = step.decidedAt)
    }

@Composable
private fun ChainRow(
    step: ChainStep,
    isLast: Boolean,
) {
    val t = SuzuT.current
    val (dotColor, label) =
        when (step.state) {
            "approved" -> t.ok to "承認"
            "pending" -> t.warn to "審査中"
            "rejected" -> t.danger to "差し戻し"
            else -> t.inkFaint to "—"
        }
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(
            modifier = Modifier.width(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Box(
                modifier = Modifier.size(14.dp).clip(CircleShape).background(dotColor),
                contentAlignment = Alignment.Center,
            ) {
                if (step.state == "approved") {
                    Text("✓", color = Color.White, style = TextStyle(fontSize = 9.sp, fontWeight = FontWeight.Bold))
                } else if (step.state == "rejected") {
                    Text("×", color = Color.White, style = TextStyle(fontSize = 9.sp, fontWeight = FontWeight.Bold))
                }
            }
            if (!isLast) {
                Box(modifier = Modifier.height(20.dp).width(1.5.dp).background(t.hair))
            }
        }
        Spacer(Modifier.width(12.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(step.role, color = t.ink, style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold))
            if (step.ts != null) {
                Text(
                    step.ts,
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
                )
            }
        }
        Box(
            modifier =
                Modifier
                    .clip(RoundedCornerShape(6.dp))
                    .background(dotColor.copy(alpha = 0.12f))
                    .padding(horizontal = 8.dp, vertical = 2.dp),
        ) {
            Text(label, color = dotColor, style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold))
        }
    }
}

@Composable
private fun Section(label: String) {
    val t = SuzuT.current
    Text(
        label,
        color = t.inkSub,
        style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.5.sp),
    )
}

@Composable
private fun KvRow(
    label: String,
    value: String,
    mono: Boolean = false,
) {
    val t = SuzuT.current
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Text(label, color = t.inkSub, modifier = Modifier.width(80.dp), style = TextStyle(fontSize = 12.sp))
        Text(
            value,
            color = t.ink,
            style =
                TextStyle(
                    fontSize = 14.sp,
                    fontWeight = FontWeight.SemiBold,
                    fontFamily = if (mono) FontFamily.Monospace else null,
                    lineHeight = 20.sp,
                ),
        )
    }
}
