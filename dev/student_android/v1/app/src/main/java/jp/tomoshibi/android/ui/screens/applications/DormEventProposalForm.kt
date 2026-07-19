package jp.tomoshibi.android.ui.screens.applications

import androidx.compose.foundation.background
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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.derivedStateOf
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.DormLifeAPI
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.ApplyDoneBody
import jp.tomoshibi.android.ui.components.DateField
import jp.tomoshibi.android.ui.components.Field
import jp.tomoshibi.android.ui.components.GhostButton
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.components.TArea
import jp.tomoshibi.android.ui.components.TField
import jp.tomoshibi.android.ui.components.TimeField
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.ZoneId
import java.time.format.DateTimeFormatter

// ─────────────────────────────────────────────────────────────────────
// DormEventProposalForm —— 行事企画申請 / 再提出
// 对齐 iOS DormLifeForms.swift DormEventProposalForm（含 resubmitId 双模式）。
// 三段内部流程：edit → preview → done；提交走 DormLifeAPI。
// ─────────────────────────────────────────────────────────────────────

private val JST = ZoneId.of("Asia/Tokyo")

private fun todayJst(): String = LocalDate.now(JST).format(DateTimeFormatter.ISO_LOCAL_DATE)

private fun nilIfBlank(s: String): String? = s.trim().takeIf { it.isNotEmpty() }

// 日期 + 时刻 → 「yyyy-MM-ddTHH:mm:ss+09:00」（对齐 iOS combineDateAndTimeISO）
private fun combineHeldAt(
    dateYmd: String,
    timeHm: String,
): String {
    val hm = if (timeHm.length == 5) "$timeHm:00" else timeHm
    return "${dateYmd}T$hm+09:00"
}

// 从后端 held_at ISO 拆出日期 / 时刻
private fun splitHeldAt(iso: String): Pair<String, String> {
    val date = iso.take(10)
    val time =
        iso
            .substringAfter('T', "")
            .take(5)
            .ifEmpty { "19:00" }
    return date to time
}

@Composable
fun DormEventProposalForm(
    navController: NavHostController,
    resubmitId: String? = null,
) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    val isResubmit = resubmitId != null
    val kindName = "行事企画"
    val today = remember { todayJst() }

    var stage by remember { mutableStateOf("edit") }
    var submitting by remember { mutableStateOf(false) }
    var prefilling by remember { mutableStateOf(false) }
    var didPrefill by remember { mutableStateOf(false) }

    var teamName by remember { mutableStateOf("") }
    var title by remember { mutableStateOf("") }
    var heldDate by remember { mutableStateOf("") }
    var heldTime by remember { mutableStateOf("19:00") }
    var place by remember { mutableStateOf("") }
    var expectedCountText by remember { mutableStateOf("") }
    var target by remember { mutableStateOf("") }
    var purpose by remember { mutableStateOf("") }
    var content by remember { mutableStateOf("") }
    var riskSolution by remember { mutableStateOf("") }
    var expectedCost by remember { mutableStateOf("") }
    var note by remember { mutableStateOf("") }

    val expectedCount by remember {
        derivedStateOf { expectedCountText.trim().toIntOrNull() }
    }

    // canSubmit：字段齐全 + 実施日 ≥ 今天（JST）
    val canSubmit by remember {
        derivedStateOf {
            if (title.trim().isEmpty()) return@derivedStateOf false
            if (place.trim().isEmpty()) return@derivedStateOf false
            val cnt = expectedCount ?: return@derivedStateOf false
            if (cnt < 0) return@derivedStateOf false
            if (target.trim().isEmpty()) return@derivedStateOf false
            if (purpose.trim().isEmpty()) return@derivedStateOf false
            if (content.trim().isEmpty()) return@derivedStateOf false
            if (riskSolution.trim().isEmpty()) return@derivedStateOf false
            if (expectedCost.trim().isEmpty()) return@derivedStateOf false
            if (heldDate.isEmpty() || heldDate < today) return@derivedStateOf false
            true
        }
    }

    // 再提出：从 /mine 拉原企画预填
    LaunchedEffect(resubmitId) {
        if (!isResubmit || didPrefill) return@LaunchedEffect
        val rid = resubmitId ?: return@LaunchedEffect
        prefilling = true
        try {
            val all = DormLifeAPI.listMyEventProposals()
            val item = all.firstOrNull { it.id.equals(rid, ignoreCase = true) }
            if (item == null) {
                store.showToast("企画が見つかりませんでした")
                navController.popBackStack()
                return@LaunchedEffect
            }
            teamName = item.teamName.orEmpty()
            title = item.title
            val (d, tm) = splitHeldAt(item.heldAt)
            heldDate = d
            heldTime = tm
            place = item.place
            expectedCountText = item.expectedCount.toString()
            target = item.target
            purpose = item.purpose
            content = item.content
            riskSolution = item.riskSolution
            expectedCost = item.expectedCost
            note = item.note.orEmpty()
            didPrefill = true
        } catch (e: ApiError) {
            if (store.handleIfUnauthorized(e, store.snapshot().authToken)) return@LaunchedEffect
            store.showToast(e.display.ifBlank { "企画の取得に失敗しました" })
            navController.popBackStack()
        } catch (_: Exception) {
            store.showToast("企画の取得に失敗しました")
            navController.popBackStack()
        } finally {
            prefilling = false
        }
    }

    suspend fun doSubmit() {
        val count = expectedCount ?: return
        val body =
            DormLifeAPI.EventProposalBody(
                teamName = nilIfBlank(teamName),
                title = title.trim(),
                heldAt = combineHeldAt(heldDate, heldTime),
                place = place.trim(),
                expectedCount = count,
                target = target.trim(),
                purpose = purpose.trim(),
                content = content.trim(),
                riskSolution = riskSolution.trim(),
                expectedCost = expectedCost.trim(),
                note = nilIfBlank(note),
            )
        val tokenAtStart = store.snapshot().authToken
        try {
            if (isResubmit) {
                DormLifeAPI.resubmitEventProposal(id = resubmitId!!, body = body)
                if (store.snapshot().authToken != tokenAtStart) return
                store.showToast("行事企画を再提出しました")
            } else {
                DormLifeAPI.submitEventProposal(body)
                if (store.snapshot().authToken != tokenAtStart) return
                store.showToast("行事企画申請を提出しました")
            }
            stage = "done"
        } catch (e: ApiError.Server) {
            if (e.code == 409) {
                store.showToast("この企画は再提出できません")
            } else if (store.handleIfUnauthorized(e, tokenAtStart)) {
                return
            } else {
                store.showToast(e.display)
            }
        } catch (e: ApiError) {
            if (store.handleIfUnauthorized(e, tokenAtStart)) return
            store.showToast(e.display)
        } catch (_: Exception) {
            store.showToast(
                if (isResubmit) "行事企画の再提出に失敗しました" else "行事企画申請の提出に失敗しました",
            )
        }
    }

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(
                title = if (isResubmit) "行事企画 再提出" else "行事企画申請",
                level = 2,
                onLeft = {
                    if (stage == "preview") stage = "edit" else navController.popBackStack()
                },
            )

            when (stage) {
                "done" -> {
                    ApplyDoneBody(kindName = kindName) {
                        navController.navigate(jp.tomoshibi.android.nav.Route.Applications.path) {
                            popUpTo(jp.tomoshibi.android.nav.Route.Applications.path) { inclusive = false }
                            launchSingleTop = true
                        }
                    }
                }

                else -> {
                    if (prefilling) {
                        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                            CircularProgressIndicator()
                        }
                    } else {
                        Column(
                            modifier =
                                Modifier
                                    .fillMaxWidth()
                                    .verticalScroll(rememberScrollState())
                                    .padding(horizontal = 16.dp),
                            verticalArrangement = Arrangement.spacedBy(14.dp),
                        ) {
                            Spacer(Modifier.height(2.dp))
                            if (stage == "edit") {
                                EditBody(
                                    t = t,
                                    isResubmit = isResubmit,
                                    teamName = teamName,
                                    onTeamName = { teamName = it },
                                    title = title,
                                    onTitle = { title = it },
                                    heldDate = heldDate,
                                    onHeldDate = { heldDate = it },
                                    heldTime = heldTime,
                                    onHeldTime = { heldTime = it },
                                    place = place,
                                    onPlace = { place = it },
                                    expectedCountText = expectedCountText,
                                    onExpectedCountText = { expectedCountText = it },
                                    target = target,
                                    onTarget = { target = it },
                                    purpose = purpose,
                                    onPurpose = { purpose = it },
                                    content = content,
                                    onContent = { content = it },
                                    riskSolution = riskSolution,
                                    onRiskSolution = { riskSolution = it },
                                    expectedCost = expectedCost,
                                    onExpectedCost = { expectedCost = it },
                                    note = note,
                                    onNote = { note = it },
                                    today = today,
                                    onList = {
                                        navController.navigate(jp.tomoshibi.android.nav.Route.DormEventList.path)
                                    },
                                    canSubmit = canSubmit && !submitting,
                                    confirmTitle = if (isResubmit) "再提出する" else "確認する",
                                    onConfirm = {
                                        // 再提出：iOS 无 preview，直接提交；新规保留 Android 三段防呆
                                        if (isResubmit) {
                                            if (submitting) return@EditBody
                                            scope.launch {
                                                submitting = true
                                                try {
                                                    doSubmit()
                                                } finally {
                                                    submitting = false
                                                }
                                            }
                                        } else {
                                            stage = "preview"
                                        }
                                    },
                                )
                            } else {
                                PreviewBody(
                                    t = t,
                                    kindName = kindName,
                                    teamName = teamName,
                                    title = title,
                                    heldDate = heldDate,
                                    heldTime = heldTime,
                                    place = place,
                                    expectedCountText = expectedCountText,
                                    target = target,
                                    purpose = purpose,
                                    content = content,
                                    riskSolution = riskSolution,
                                    expectedCost = expectedCost,
                                    note = note,
                                    submitting = submitting,
                                    onSubmit = {
                                        if (submitting) return@PreviewBody
                                        scope.launch {
                                            submitting = true
                                            try {
                                                doSubmit()
                                            } finally {
                                                submitting = false
                                            }
                                        }
                                    },
                                    onEdit = { stage = "edit" },
                                )
                            }
                            Spacer(Modifier.height(40.dp))
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun EditBody(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    isResubmit: Boolean,
    teamName: String,
    onTeamName: (String) -> Unit,
    title: String,
    onTitle: (String) -> Unit,
    heldDate: String,
    onHeldDate: (String) -> Unit,
    heldTime: String,
    onHeldTime: (String) -> Unit,
    place: String,
    onPlace: (String) -> Unit,
    expectedCountText: String,
    onExpectedCountText: (String) -> Unit,
    target: String,
    onTarget: (String) -> Unit,
    purpose: String,
    onPurpose: (String) -> Unit,
    content: String,
    onContent: (String) -> Unit,
    riskSolution: String,
    onRiskSolution: (String) -> Unit,
    expectedCost: String,
    onExpectedCost: (String) -> Unit,
    note: String,
    onNote: (String) -> Unit,
    today: String,
    onList: () -> Unit,
    canSubmit: Boolean,
    confirmTitle: String,
    onConfirm: () -> Unit,
) {
    if (isResubmit) {
        // 差戻提示条（对齐 iOS resubmitBanner）
        Row(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(t.dangerBg)
                    .padding(horizontal = 14.dp, vertical = 12.dp),
            verticalAlignment = Alignment.Top,
        ) {
            Text("↩", color = t.danger, style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold))
            Spacer(Modifier.width(8.dp))
            Text(
                "この企画は差し戻されました。内容を修正して再提出してください。",
                color = t.ink,
                style = TextStyle(fontSize = 12.5.sp, lineHeight = 18.sp),
            )
        }
    } else {
        Row(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(t.pill)
                    .clickable(onClick = onList)
                    .padding(horizontal = 14.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            androidx.compose.material3.Icon(
                SuzuIcons.Doc,
                contentDescription = null,
                tint = MaterialPrimary(),
                modifier = Modifier.size(15.dp),
            )
            Spacer(Modifier.width(8.dp))
            Text("提出済み一覧", color = MaterialPrimary(), style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold))
            Spacer(Modifier.weight(1f))
            androidx.compose.material3.Icon(
                SuzuIcons.ChevR,
                contentDescription = null,
                tint = MaterialPrimary(),
                modifier = Modifier.size(14.dp),
            )
        }
    }

    SectionLabel(t, "1", "企画")
    SuzuCard {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Field(label = "起案団体名") {
                TField(value = teamName, onValueChange = onTeamName, placeholder = "団体名（個人の場合は空欄）")
            }
            Field(label = "企画名", required = true) {
                TField(value = title, onValueChange = onTitle, placeholder = "企画名")
            }
        }
    }

    SectionLabel(t, "2", "実施情報")
    SuzuCard {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Field(label = "実施日時", required = true) {
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    DateField(
                        label = "",
                        value = heldDate,
                        minDate = today,
                        modifier = Modifier.weight(1f),
                        onPick = onHeldDate,
                    )
                    TimeField(label = "", value = heldTime, modifier = Modifier.weight(1f), onPick = onHeldTime)
                }
            }
            Field(label = "実施場所", required = true) {
                TField(value = place, onValueChange = onPlace, placeholder = "実施場所")
            }
            Field(label = "参加予定人数", required = true) {
                TField(
                    value = expectedCountText,
                    onValueChange = onExpectedCountText,
                    placeholder = "0",
                    keyboard = KeyboardType.Number,
                )
            }
            Field(label = "参加対象", required = true) {
                TField(value = target, onValueChange = onTarget, placeholder = "例：寮生全員 / 高校生 / 希望者")
            }
        }
    }

    SectionLabel(t, "3", "内容")
    SuzuCard {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Field(label = "目的", required = true) {
                TArea(value = purpose, onValueChange = onPurpose, placeholder = "企画の目的", rows = 4)
            }
            Field(label = "企画内容", required = true, hint = "スケジュールも含めて入力してください") {
                TArea(value = content, onValueChange = onContent, placeholder = "具体的な内容・スケジュール", rows = 6)
            }
        }
    }

    SectionLabel(t, "4", "確認事項")
    SuzuCard {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Field(label = "想定される問題点と対応策", required = true) {
                TArea(
                    value = riskSolution,
                    onValueChange = onRiskSolution,
                    placeholder = "想定される問題点と対応策",
                    rows = 5,
                )
            }
            Field(label = "概算経費", required = true) {
                TArea(value = expectedCost, onValueChange = onExpectedCost, placeholder = "必要な費用・内訳", rows = 3)
            }
            Field(label = "その他") {
                TArea(value = note, onValueChange = onNote, placeholder = "補足事項", rows = 3)
            }
        }
    }

    PrimaryButton(title = confirmTitle, enabled = canSubmit, onClick = onConfirm)
}

@Composable
private fun PreviewBody(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    kindName: String,
    teamName: String,
    title: String,
    heldDate: String,
    heldTime: String,
    place: String,
    expectedCountText: String,
    target: String,
    purpose: String,
    content: String,
    riskSolution: String,
    expectedCost: String,
    note: String,
    submitting: Boolean,
    onSubmit: () -> Unit,
    onEdit: () -> Unit,
) {
    Box(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(t.pill)
                .padding(14.dp),
    ) {
        Text(
            "ℹ 提出後は審査待ちとなります。承認されるまでは内容の変更が可能です。",
            color = t.inkSub,
            style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp),
        )
    }

    Text("申請内容の確認", color = t.ink, style = TextStyle(fontSize = 17.sp, fontWeight = FontWeight.Bold))

    SuzuCard(padding = 0) {
        KvRow(t, "種別", "${kindName}申請", first = true)
        if (teamName.isNotBlank()) KvRow(t, "起案団体名", teamName)
        KvRow(t, "企画名", dash(title))
        KvRow(t, "実施日時", "${dash(heldDate)} ${dash(heldTime)}")
        KvRow(t, "実施場所", dash(place))
        KvRow(t, "参加予定人数", "${dash(expectedCountText)}名")
        KvRow(t, "参加対象", dash(target))
        KvRow(t, "目的", dash(purpose))
        KvRow(t, "企画内容", dash(content))
        KvRow(t, "想定される問題点と対応策", dash(riskSolution))
        KvRow(t, "概算経費", dash(expectedCost))
        if (note.isNotBlank()) KvRow(t, "その他", note)
    }

    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        GhostButton(title = "戻る", modifier = Modifier.weight(1f), onClick = onEdit)
        PrimaryButton(
            title = if (submitting) "提出中…" else "提出する",
            enabled = !submitting,
            modifier = Modifier.weight(1f),
            onClick = onSubmit,
        )
    }
}

@Composable
private fun SectionLabel(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    num: String,
    label: String,
) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Box(
            modifier =
                Modifier
                    .size(22.dp)
                    .clip(RoundedCornerShape(6.dp))
                    .background(MaterialPrimary()),
            contentAlignment = Alignment.Center,
        ) {
            Text(num, color = Color.White, style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold))
        }
        Text(label, color = t.ink, style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold))
    }
}

@Composable
private fun KvRow(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    label: String,
    value: String,
    first: Boolean = false,
) {
    if (!first) {
        Box(modifier = Modifier.fillMaxWidth().height(0.5.dp).background(t.hair))
    }
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 12.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Text(label, color = t.inkSub, modifier = Modifier.width(100.dp), style = TextStyle(fontSize = 12.sp))
        Text(value, color = t.ink, modifier = Modifier.weight(1f), style = TextStyle(fontSize = 14.sp, lineHeight = 19.sp))
    }
}

@Composable
private fun MaterialPrimary(): Color = androidx.compose.material3.MaterialTheme.colorScheme.primary

private fun dash(s: String?): String = if (s.isNullOrBlank()) "—" else s
