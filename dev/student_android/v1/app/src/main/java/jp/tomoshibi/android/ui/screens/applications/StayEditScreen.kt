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
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.format.JstDate
import jp.tomoshibi.android.data.model.StayApplication
import jp.tomoshibi.android.data.model.StayKind
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.ApplicationUpdateBody
import jp.tomoshibi.android.data.network.StayLocationBody
import jp.tomoshibi.android.data.network.endpoints.ApplicationsAPI
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.ChipGroup
import jp.tomoshibi.android.ui.components.DateField
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GhostButton
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.components.TArea
import jp.tomoshibi.android.ui.components.TField
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
// ─────────────────────────────────────────────────────────────────────
// StayEditScreen —— 出寮届 变更届（编辑已提交的出寮届）
// 对齐 iOS StayEditForm：GET detail 预填 → PUT /applications/:id（ApplicationUpdateBody）。
// 区块：警告横幅 → 申請者本人（变更不可）→ 出寮/帰寮日 → 移動方法
//   →（外泊/帰国才有）宿泊先 →「変更の理由」（必填）→ 提交行。
// ─────────────────────────────────────────────────────────────────────

// 出寮方法（去程）选项 —— 跟 StayForm 的 LEAVE_METHODS 一致
private val EDIT_LEAVE_TRANSPORTS =
    listOf(
        "西口1便",
        "西口2便",
        "金川1便",
        "金川2便",
        "寮生特別運行",
        "JR",
        "自家用車",
        "タクシー",
        "教員",
        "その他",
    )

// 帰寮方法（回程）选项 —— 跟 StayForm 的 RETURN_METHODS 一致
private val EDIT_RETURN_TRANSPORTS =
    listOf(
        "西口登校便",
        "金川登校便",
        "寮生特別運行",
        "JR",
        "自家用車",
        "タクシー",
        "教員",
        "その他",
    )

@Composable
fun StayEditScreen(
    navController: NavHostController,
    id: String,
) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val user = state.user

    var ui by remember { mutableStateOf<LoadState<StayApplication>>(LoadState.Loading) }

    suspend fun load() {
        ui = LoadState.Loading
        val tokenAtStart = store.snapshot().authToken
        ui =
            try {
                LoadState.Success(ApplicationsAPI.detail(id).toStayApplication())
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
        when (val s = ui) {
            LoadState.Loading -> {
                Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
                    PageHeader(title = "変更届", level = 3, onLeft = { navController.popBackStack() })
                    LoadingBox()
                }
            }

            is LoadState.Failed -> {
                Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
                    PageHeader(title = "変更届", level = 3, onLeft = { navController.popBackStack() })
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }
            }

            LoadState.Empty -> {
                Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
                    PageHeader(title = "変更届", level = 3, onLeft = { navController.popBackStack() })
                    FailedBox("読み込みに失敗しました", onRetry = { scope.launch { load() } })
                }
            }

            is LoadState.Success -> {
                StayEditFormBody(
                    navController = navController,
                    original = s.value,
                    userStudentNo = user.studentNo,
                    userName = user.name,
                    userGradeClass = user.gradeClass,
                    userDorm = user.dorm,
                    userRoom = user.room,
                    userCategory = user.category,
                    userPhone = user.phone,
                    onSubmitted = { navController.popBackStack() },
                )
            }
        }
    }
}

@Composable
private fun StayEditFormBody(
    navController: NavHostController,
    original: StayApplication,
    userStudentNo: String,
    userName: String,
    userGradeClass: String,
    userDorm: String,
    userRoom: String,
    userCategory: String,
    userPhone: String,
    onSubmitted: () -> Unit,
) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()

    // needsDestination：外泊 / 帰国 才填宿泊先
    val needsDestination = original.kind == StayKind.STAY.label || original.kind == StayKind.RETURN.label

    var leaveDate by remember(original.id) { mutableStateOf(original.leaveDate.takeIf { it != "—" } ?: "") }
    var returnDate by remember(original.id) { mutableStateOf(original.returnDate ?: (original.leaveDate.takeIf { it != "—" } ?: "")) }
    var leaveMethod by remember(original.id) { mutableStateOf(original.leaveMethod ?: "JR") }
    var returnMethod by remember(original.id) { mutableStateOf(original.returnMethod ?: "JR") }
    var destination by remember(original.id) { mutableStateOf(original.destination ?: "") }
    var amendReason by remember { mutableStateOf("") }
    var submitting by remember { mutableStateOf(false) }

    val today = remember { JstDate.today().toString() }
    // CB-04：出寮日被主动改动时，新值不得早于今天
    val leaveChanged = leaveDate.isNotEmpty() && leaveDate != original.leaveDate
    val canSubmit =
        amendReason.trim().isNotEmpty() &&
            !submitting &&
            (returnDate.isEmpty() || leaveDate.isEmpty() || returnDate >= leaveDate) &&
            (!leaveChanged || leaveDate >= today)

    Column(
        modifier =
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState()),
    ) {
        PageHeader(
            title = "${original.kind}届の変更",
            level = 3,
            onLeft = { navController.popBackStack() },
        )

        Column(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(18.dp),
        ) {
            WarningBanner()

            SectionLabel("申請者本人（変更不可）")
            SuzuCard(padding = 0) {
                Column(modifier = Modifier.fillMaxWidth()) {
                    IdRow("アカウント番号", userStudentNo, isFirst = true)
                    IdRow("氏名", userName)
                    IdRow("学年・組", userGradeClass)
                    IdRow("寮・部屋", "$userDorm $userRoom")
                    IdRow("区分", userCategory)
                    IdRow("携帯電話", userPhone)
                }
            }
            Text(
                "※ 個人情報の変更は寮監にご連絡ください。変更届では変更できません。",
                color = t.inkMute,
                style = TextStyle(fontSize = 11.sp),
            )

            SectionLabel("出寮 / 帰寮日")
            SuzuCard(padding = 14) {
                Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                    DateField(
                        label = "出寮日",
                        value = leaveDate,
                        minDate = today,
                        onPick = { leaveDate = it },
                    )
                    original.leaveDate.takeIf { it != "—" }?.let { OriginalNote("原値", it) }
                    DateField(
                        label = "帰寮日",
                        value = returnDate,
                        minDate = leaveDate.ifEmpty { today },
                        onPick = { returnDate = it },
                    )
                    original.returnDate?.let { OriginalNote("原値", it) }
                }
            }

            SectionLabel("移動方法")
            SuzuCard(padding = 14) {
                Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(
                            "出寮方法",
                            color = t.inkSub,
                            style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
                        )
                        ChipGroup(
                            options = EDIT_LEAVE_TRANSPORTS,
                            selected = leaveMethod,
                            onSelect = { leaveMethod = it },
                        )
                        original.leaveMethod?.takeIf { it != leaveMethod }?.let { OriginalNote("原値", it) }
                    }
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(
                            "帰寮方法",
                            color = t.inkSub,
                            style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
                        )
                        ChipGroup(
                            options = EDIT_RETURN_TRANSPORTS,
                            selected = returnMethod,
                            onSelect = { returnMethod = it },
                        )
                        original.returnMethod?.takeIf { it != returnMethod }?.let { OriginalNote("原値", it) }
                    }
                }
            }

            if (needsDestination) {
                SectionLabel("宿泊先")
                SuzuCard(padding = 14) {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        TField(
                            value = destination,
                            onValueChange = { destination = it },
                            placeholder = "宿泊先住所",
                        )
                        original.destination?.takeIf { it != destination }?.let { OriginalNote("原値", it) }
                    }
                }
            }

            // 「変更の理由」必填 — 后端写进 audit，不覆盖 reason
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "変更の理由",
                    color = t.ink,
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold),
                )
                Text(
                    " *",
                    color = t.danger,
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold),
                )
            }
            TArea(
                value = amendReason,
                onValueChange = { amendReason = it },
                placeholder = "変更の理由を入力してください",
                rows = 4,
            )
            Text(
                "※ 各役職の先生にこの理由が表示されます。",
                color = t.inkMute,
                style = TextStyle(fontSize = 11.sp),
            )

            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                GhostButton(
                    title = "キャンセル",
                    modifier = Modifier.weight(1f),
                    onClick = { navController.popBackStack() },
                )
                PrimaryButton(
                    title = if (submitting) "提出中…" else "変更届を提出",
                    modifier = Modifier.weight(1f),
                    enabled = canSubmit,
                    onClick = {
                        scope.launch {
                            submitting = true
                            val tokenAtStart = store.snapshot().authToken
                            try {
                                // 只发改过的字段 + amend_reason（对齐 iOS IX-004）
                                // 只发改过的字段；宿泊先走 stay_locations（勿用 dest_cities）
                                val body =
                                    ApplicationUpdateBody(
                                        amendReason = amendReason.trim(),
                                        leaveDate = leaveDate.takeIf { it.isNotEmpty() && it != original.leaveDate },
                                        returnDate = returnDate.takeIf { it.isNotEmpty() && it != original.returnDate },
                                        leaveMethod = leaveMethod.takeIf { it != original.leaveMethod },
                                        returnMethod = returnMethod.takeIf { it != original.returnMethod },
                                        stayLocations =
                                            if (needsDestination && destination.trim().isNotEmpty() &&
                                                destination.trim() != (original.destination ?: "")
                                            ) {
                                                listOf(
                                                    StayLocationBody(
                                                        kind = "その他",
                                                        name = destination.trim(),
                                                        address = destination.trim(),
                                                    ),
                                                )
                                            } else {
                                                null
                                            },
                                    )
                                ApplicationsAPI.update(original.id, body)
                                if (store.snapshot().authToken != tokenAtStart) return@launch
                                store.showToast("変更届を提出しました")
                                onSubmitted()
                            } catch (e: ApiError) {
                                if (store.handleIfUnauthorized(e, tokenAtStart)) return@launch
                                store.showToast(e.display)
                            } catch (e: Exception) {
                                store.showToast("変更届の提出に失敗しました")
                            } finally {
                                submitting = false
                            }
                        }
                    },
                )
            }

            Spacer(Modifier.height(8.dp))
        }
    }
}

// 警告横幅 —「変更届を提出すると、承認の流れが最初からやり直しになります。」（iOS warningBanner）
@Composable
private fun WarningBanner() {
    val t = SuzuT.current
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(t.warnBg)
                .border(1.dp, t.warn, RoundedCornerShape(12.dp))
                .padding(horizontal = 14.dp, vertical = 12.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.Top,
    ) {
        // 警告三角图标位（iOS 用 SF Symbol exclamationmark.triangle.fill；这里用同义 emoji 占位）
        Text("⚠️", color = t.warnDeep, style = TextStyle(fontSize = 13.sp))
        Column(verticalArrangement = Arrangement.spacedBy(3.dp)) {
            Text(
                "変更届を提出すると、承認の流れが最初からやり直しになります。",
                color = t.warnDeep,
                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
            )
            Text(
                "先にご承認いただいた先生にも、もう一度ご承認をお願いすることになります。",
                color = t.warnDeep,
                style = TextStyle(fontSize = 11.5.sp, lineHeight = 16.sp),
            )
        }
    }
}

// 区块小标题（iOS sectionLabel：13 bold inkSub）
@Composable
private fun SectionLabel(text: String) {
    val t = SuzuT.current
    Text(
        text,
        color = t.inkSub,
        style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold, letterSpacing = 0.5.sp),
    )
}

// 身份信息一行（iOS idRow：左 90 宽标签 inkSub + 右值 ink，行间细线）
@Composable
private fun IdRow(
    k: String,
    v: String,
    isFirst: Boolean = false,
) {
    val t = SuzuT.current
    Column(modifier = Modifier.fillMaxWidth()) {
        if (!isFirst) {
            Box(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .height(1.dp)
                        .background(t.hair),
            )
        }
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 13.dp),
            verticalAlignment = Alignment.Top,
        ) {
            Text(
                k,
                color = t.inkSub,
                style = TextStyle(fontSize = 13.sp),
                modifier = Modifier.width(90.dp),
            )
            Text(
                v,
                color = t.ink,
                style = TextStyle(fontSize = 13.5.sp, fontWeight = FontWeight.Medium),
                modifier = Modifier.weight(1f),
            )
        }
    }
}

// 原値小标（iOS originalNote：左 pill 胶囊「原値」+ 右值 inkMute）
@Composable
private fun OriginalNote(
    label: String,
    text: String,
) {
    val t = SuzuT.current
    Row(
        horizontalArrangement = Arrangement.spacedBy(6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            modifier =
                Modifier
                    .clip(RoundedCornerShape(percent = 50))
                    .background(t.pill)
                    .padding(horizontal = 6.dp, vertical = 1.dp),
        ) {
            Text(
                label,
                color = t.inkMute,
                style = TextStyle(fontSize = 10.5.sp, fontWeight = FontWeight.SemiBold),
            )
        }
        Text(text, color = t.inkMute, style = TextStyle(fontSize = 11.sp))
    }
}
