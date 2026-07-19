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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshots.SnapshotStateList
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.format.JstDate
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.OnlineRequestBody
import jp.tomoshibi.android.data.network.endpoints.StudyAPI
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.ApplyDoneBody
import jp.tomoshibi.android.ui.components.ContractFilePicker
import jp.tomoshibi.android.ui.components.DateField
import jp.tomoshibi.android.ui.components.Field
import jp.tomoshibi.android.ui.components.GhostButton
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PickedContract
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.components.TArea
import jp.tomoshibi.android.ui.components.TimeField
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.time.format.DateTimeFormatter

// 「オンライン夜学習申請」— 对齐 iOS StudyOnlineForm.swift
// Android 保留 edit → preview → done 三段；提交走 StudyAPI。

private val WEEKDAYS = listOf("月", "火", "水", "木", "金")
private const val DEFAULT_SLOT_START = "19:40"
private const val DEFAULT_SLOT_END = "21:00"
private const val PERIOD_HINT = "オンライン夜学習開始の3日前までに提出してください"

// 周课表时段；稳定 id 作列表 key（删中间行不串内容）
private data class ScheduleSlot(
    val id: Long,
    val start: String,
    val end: String,
)

@Composable
fun StudyOnlineForm(navController: NavHostController) {
    val store = LocalAppStore.current
    val t = SuzuT.current
    val scope = rememberCoroutineScope()

    var stage by remember { mutableStateOf("edit") }
    var submitting by remember { mutableStateOf(false) }

    val threeDaysLater =
        remember {
            JstDate.today().plusDays(3).format(DateTimeFormatter.ISO_LOCAL_DATE)
        }

    var periodFrom by remember { mutableStateOf(threeDaysLater) }
    var periodTo by remember { mutableStateOf(threeDaysLater) }

    var slotIdSeq by remember { mutableStateOf(0L) }
    val schedule: Map<String, SnapshotStateList<ScheduleSlot>> =
        remember { WEEKDAYS.associateWith { mutableStateListOf() } }

    var pickedContract by remember { mutableStateOf<PickedContract?>(null) }
    var contractRef by remember { mutableStateOf("") }
    var reason by remember { mutableStateOf("") }

    val allSlots = schedule.values.flatten()
    val canSubmit =
        reason.trim().isNotEmpty() &&
            periodFrom.isNotEmpty() &&
            periodTo.isNotEmpty() &&
            periodFrom >= threeDaysLater &&
            periodTo >= periodFrom &&
            allSlots.isNotEmpty() &&
            allSlots.all { it.end > it.start }

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(
                title = "オンライン夜学習申請",
                level = 2,
                onLeft = {
                    if (stage == "preview") stage = "edit" else navController.popBackStack()
                },
            )

            when (stage) {
                "edit" -> {
                    EditBody(
                        threeDaysLater = threeDaysLater,
                        periodFrom = periodFrom,
                        periodTo = periodTo,
                        schedule = schedule,
                        pickedContract = pickedContract,
                        contractRef = contractRef,
                        reason = reason,
                        canSubmit = canSubmit,
                        onList = { navController.navigate(Route.StudyOnlineList.path) },
                        onPickFrom = { newFrom ->
                            periodFrom = newFrom
                            if (periodTo < newFrom) periodTo = newFrom
                        },
                        onPickTo = { periodTo = it },
                        onAddSlot = { day ->
                            slotIdSeq += 1
                            schedule[day]?.add(
                                ScheduleSlot(id = slotIdSeq, start = DEFAULT_SLOT_START, end = DEFAULT_SLOT_END),
                            )
                        },
                        onRemoveSlot = { day, id -> schedule[day]?.removeAll { it.id == id } },
                        onSlotStart = { day, id, v ->
                            schedule[day]?.let { list ->
                                val i = list.indexOfFirst { it.id == id }
                                if (i >= 0) list[i] = list[i].copy(start = v)
                            }
                        },
                        onSlotEnd = { day, id, v ->
                            schedule[day]?.let { list ->
                                val i = list.indexOfFirst { it.id == id }
                                if (i >= 0) list[i] = list[i].copy(end = v)
                            }
                        },
                        onPickedContract = { pickedContract = it },
                        onContractRef = { contractRef = it },
                        onReason = { reason = it },
                        onNext = { stage = "preview" },
                    )
                }

                "preview" -> {
                    PreviewBody(
                        periodFrom = periodFrom,
                        periodTo = periodTo,
                        schedule = schedule,
                        pickedContract = pickedContract,
                        contractRef = contractRef,
                        reason = reason,
                        submitting = submitting,
                        onSubmit = {
                            if (submitting) return@PreviewBody
                            scope.launch {
                                submitting = true
                                val tokenAtStart = store.snapshot().authToken
                                try {
                                    val body =
                                        OnlineRequestBody(
                                            reason = reason.trim(),
                                            periodFrom = periodFrom,
                                            periodTo = periodTo,
                                            weeklySchedule = buildWeeklySchedule(schedule),
                                            contractRef = contractRef.trim().ifBlank { null },
                                        )
                                    val out = StudyAPI.submitOnlineRequest(body)
                                    if (store.snapshot().authToken != tokenAtStart) return@launch

                                    val contract = pickedContract
                                    if (contract != null) {
                                        try {
                                            StudyAPI.uploadOnlineContract(
                                                requestId = out.id,
                                                fileData = contract.data,
                                                fileName = contract.fileName,
                                                mimeType = contract.mime,
                                            )
                                        } catch (e: ApiError) {
                                            if (store.handleIfUnauthorized(e, tokenAtStart)) return@launch
                                            store.showToast(
                                                "申請は受け付けましたが、契約書の添付に失敗しました。後で一覧から再度添付してください",
                                            )
                                            stage = "done"
                                            return@launch
                                        } catch (_: Exception) {
                                            store.showToast(
                                                "申請は受け付けましたが、契約書の添付に失敗しました。後で一覧から再度添付してください",
                                            )
                                            stage = "done"
                                            return@launch
                                        }
                                    }

                                    store.showToast("オンライン夜学習申請を提出しました")
                                    stage = "done"
                                } catch (e: ApiError) {
                                    if (store.handleIfUnauthorized(e, tokenAtStart)) return@launch
                                    store.showToast(e.display)
                                } catch (_: Exception) {
                                    store.showToast("オンライン夜学習申請の提出に失敗しました")
                                } finally {
                                    submitting = false
                                }
                            }
                        },
                        onEdit = { stage = "edit" },
                    )
                }

                "done" -> {
                    ApplyDoneBody(
                        kindName = "オンライン夜学習",
                        onBack = {
                            navController.popBackStack()
                            Unit
                        },
                    )
                }
            }
        }
    }
}

@Composable
private fun EditBody(
    threeDaysLater: String,
    periodFrom: String,
    periodTo: String,
    schedule: Map<String, SnapshotStateList<ScheduleSlot>>,
    pickedContract: PickedContract?,
    contractRef: String,
    reason: String,
    canSubmit: Boolean,
    onList: () -> Unit,
    onPickFrom: (String) -> Unit,
    onPickTo: (String) -> Unit,
    onAddSlot: (String) -> Unit,
    onRemoveSlot: (String, Long) -> Unit,
    onSlotStart: (String, Long, String) -> Unit,
    onSlotEnd: (String, Long, String) -> Unit,
    onPickedContract: (PickedContract?) -> Unit,
    onContractRef: (String) -> Unit,
    onReason: (String) -> Unit,
    onNext: () -> Unit,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme

    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        Spacer(Modifier.height(2.dp))

        // 顶部「提出済み一覧」
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
            Icon(SuzuIcons.Doc, contentDescription = null, tint = cs.primary, modifier = Modifier.size(15.dp))
            Spacer(Modifier.width(8.dp))
            Text(
                "提出済み一覧",
                color = cs.primary,
                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold),
            )
            Spacer(Modifier.weight(1f))
            Icon(SuzuIcons.ChevR, contentDescription = null, tint = cs.primary, modifier = Modifier.size(14.dp))
        }

        WarnBanner(PERIOD_HINT)

        SectionLabel(t, "1", "期間")
        SuzuCard {
            DateField(
                label = "開始日",
                value = periodFrom,
                required = true,
                minDate = threeDaysLater,
                onPick = onPickFrom,
            )
            Text(
                PERIOD_HINT,
                color = t.inkMute,
                style = TextStyle(fontSize = 11.sp, lineHeight = 14.sp),
                modifier = Modifier.padding(top = 4.dp),
            )
            Spacer(Modifier.height(12.dp))
            DateField(
                label = "終了日",
                value = periodTo,
                required = true,
                minDate = periodFrom.ifEmpty { threeDaysLater },
                onPick = onPickTo,
            )
        }

        SectionLabel(t, "2", "曜日・時間")
        SuzuCard {
            WEEKDAYS.forEachIndexed { index, day ->
                if (index > 0) Spacer(Modifier.height(14.dp))
                DayBlock(
                    day = day,
                    isLast = day == "金",
                    slots = schedule[day] ?: emptyList(),
                    onAdd = { onAddSlot(day) },
                    onRemove = { id -> onRemoveSlot(day, id) },
                    onStart = { id, v -> onSlotStart(day, id, v) },
                    onEnd = { id, v -> onSlotEnd(day, id, v) },
                )
            }
        }

        SectionLabel(t, "3", "契約書")
        SuzuCard {
            Field(
                label = "契約書ファイル",
                hint = "契約書の写真または PDF を添付してください（任意）",
            ) {
                ContractFilePicker(
                    picked = pickedContract,
                    onPicked = onPickedContract,
                )
            }
            Spacer(Modifier.height(14.dp))
            Field(
                label = "補足説明",
                hint = "契約書の内容・受講証明・リンクなど（任意）",
            ) {
                TArea(
                    value = contractRef,
                    onValueChange = onContractRef,
                    placeholder = "契約書や受講証明の内容・リンクを入力してください",
                    rows = 3,
                )
            }
        }

        SectionLabel(t, "4", "理由")
        SuzuCard {
            Field(label = "理由", required = true) {
                TArea(
                    value = reason,
                    onValueChange = onReason,
                    placeholder = "オンライン夜学習を希望する理由を入力してください",
                    rows = 4,
                )
            }
        }

        PrimaryButton(title = "確認する", enabled = canSubmit, onClick = onNext)
        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun DayBlock(
    day: String,
    isLast: Boolean,
    slots: List<ScheduleSlot>,
    onAdd: () -> Unit,
    onRemove: (Long) -> Unit,
    onStart: (Long, String) -> Unit,
    onEnd: (Long, String) -> Unit,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme

    Column {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                "${day}曜日",
                color = t.ink,
                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold),
            )
            Spacer(Modifier.weight(1f))
            Box(
                modifier =
                    Modifier
                        .size(28.dp)
                        .clip(RoundedCornerShape(percent = 50))
                        .clickable(onClick = onAdd),
                contentAlignment = Alignment.Center,
            ) {
                Icon(SuzuIcons.Plus, contentDescription = null, tint = cs.primary, modifier = Modifier.size(20.dp))
            }
        }

        if (slots.isEmpty()) {
            Text(
                "設定なし",
                color = t.inkMute,
                style = TextStyle(fontSize = 12.sp),
                modifier = Modifier.padding(top = 6.dp, bottom = 4.dp),
            )
        } else {
            slots.forEach { slot ->
                Spacer(Modifier.height(8.dp))
                Column {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        TimeField(
                            label = "",
                            value = slot.start,
                            modifier = Modifier.weight(1f),
                            onPick = { onStart(slot.id, it) },
                        )
                        Text(
                            "〜",
                            color = t.inkSub,
                            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
                            modifier = Modifier.padding(horizontal = 8.dp),
                        )
                        TimeField(
                            label = "",
                            value = slot.end,
                            modifier = Modifier.weight(1f),
                            onPick = { onEnd(slot.id, it) },
                        )
                        Spacer(Modifier.width(8.dp))
                        Box(
                            modifier =
                                Modifier
                                    .size(28.dp)
                                    .clip(RoundedCornerShape(percent = 50))
                                    .background(t.dangerBg)
                                    .clickable { onRemove(slot.id) },
                            contentAlignment = Alignment.Center,
                        ) {
                            Text("－", color = t.danger, style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold))
                        }
                    }
                    if (slot.end <= slot.start) {
                        Text(
                            "終了は開始より後の時刻にしてください",
                            color = t.danger,
                            style = TextStyle(fontSize = 11.sp),
                            modifier = Modifier.padding(top = 4.dp),
                        )
                    }
                }
            }
        }

        if (!isLast) {
            Spacer(Modifier.height(10.dp))
            Box(modifier = Modifier.fillMaxWidth().height(0.5.dp).background(t.hair))
        }
    }
}

@Composable
private fun PreviewBody(
    periodFrom: String,
    periodTo: String,
    schedule: Map<String, SnapshotStateList<ScheduleSlot>>,
    pickedContract: PickedContract?,
    contractRef: String,
    reason: String,
    submitting: Boolean,
    onSubmit: () -> Unit,
    onEdit: () -> Unit,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme

    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Row(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(t.pill)
                    .padding(14.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(SuzuIcons.Info, contentDescription = null, tint = cs.primary, modifier = Modifier.size(18.dp))
            Spacer(Modifier.width(10.dp))
            Text(
                "提出後は審査待ちとなります。承認されるまでは内容の変更が可能です。",
                color = t.inkSub,
                style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp),
            )
        }

        SuzuCard {
            KvRow("開始日", periodFrom)
            KvRow("終了日", periodTo)
            schedule.forEach { (day, slots) ->
                if (slots.isNotEmpty()) {
                    KvRow("${day}曜日", slots.joinToString("、") { "${it.start}〜${it.end}" })
                }
            }
            KvRow("契約書", pickedContract?.fileName ?: "（未添付）")
            if (contractRef.isNotBlank()) KvRow("補足説明", contractRef)
            KvRow("理由", reason)
        }

        PrimaryButton(
            title = if (submitting) "提出中…" else "提出する",
            enabled = !submitting,
            onClick = onSubmit,
        )
        GhostButton(title = "修正する", onClick = onEdit)
        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun SectionLabel(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    num: String,
    label: String,
) {
    val cs = MaterialTheme.colorScheme
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Box(
            modifier =
                Modifier
                    .size(22.dp)
                    .clip(RoundedCornerShape(6.dp))
                    .background(cs.primary),
            contentAlignment = Alignment.Center,
        ) {
            Text(num, color = Color.White, style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold))
        }
        Text(label, color = t.ink, style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold))
    }
}

@Composable
private fun WarnBanner(text: String) {
    val t = SuzuT.current
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(t.warnBg)
                .border(1.dp, t.warn.copy(alpha = 0.25f), RoundedCornerShape(12.dp))
                .padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(SuzuIcons.Info, contentDescription = null, tint = t.warnDeep, modifier = Modifier.size(14.dp))
        Spacer(Modifier.width(8.dp))
        Text(text, color = t.warnDeep, style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp))
    }
}

@Composable
private fun KvRow(
    label: String,
    value: String,
) {
    val t = SuzuT.current
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 10.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Text(
            label,
            color = t.inkSub,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
            modifier = Modifier.width(88.dp),
        )
        Text(
            value,
            color = t.ink,
            style = TextStyle(fontSize = 14.sp, lineHeight = 19.sp),
            modifier = Modifier.weight(1f),
        )
    }
}

private fun buildWeeklySchedule(schedule: Map<String, SnapshotStateList<ScheduleSlot>>): Map<String, List<Map<String, String>>> =
    WEEKDAYS.associateWith { day ->
        (schedule[day] ?: emptyList()).map { slot ->
            mapOf("start" to slot.start, "end" to slot.end)
        }
    }
