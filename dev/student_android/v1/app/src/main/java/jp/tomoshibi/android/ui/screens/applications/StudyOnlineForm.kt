package jp.tomoshibi.android.ui.screens.applications

import jp.tomoshibi.android.data.store.LocalAppStore

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
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshots.SnapshotStateList
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.ui.components.DateField
import jp.tomoshibi.android.ui.components.Field
import jp.tomoshibi.android.ui.components.GhostButton
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.components.TArea
import jp.tomoshibi.android.ui.components.TimeField
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// ───────────────────────────────────────────────────────────────
// StudyOnlineForm — オンライン学習申請（在线学习届）
// 对齐 iOS Features/Apply/StudyOnlineForm.swift（对齐规格 §4，行 1887-1914 + §5 契約書文件选择）
// 画面结构：黄色提示横幅 + §1 期間（開始日/終了日）+ §2 曜日・時間（月～金 时段列表）
//          + §3 契約書（文件选择桩 + 補足説明）+ §4 理由（必須）
// 不接后端：字段用本地 state 收集，三态流程 edit→preview→done（不开新路由）；
//          完成弹 toast 后 navController.popBackStack() 回列表。
// ───────────────────────────────────────────────────────────────

// 周课表里的一个时段（起〜终）。带稳定 id 当列表 key ——
// 删中间行不会串内容（对齐规格 §4 / §2 提的 iOS IX-032「下标当 key」坑）。
private data class ScheduleSlot(
    val id: Long,
    val start: String,
    val end: String,
)

// 周一～周五（键是日语单字，对齐 iOS weekly_schedule 字典键「月火水木金」）
private val WEEKDAYS = listOf("月", "火", "水", "木", "金")

// 默认时段（点「+」加一行时填的初值），对齐规格 §4「默认时段 19:40〜21:00」
private const val DEFAULT_SLOT_START = "19:40"
private const val DEFAULT_SLOT_END = "21:00"

@Composable
fun StudyOnlineForm(navController: NavHostController) {
    val store = LocalAppStore.current
    val t = SuzuT.current
    val ctx = LocalContext.current

    // 三态：edit=填表 / preview=只读确认 / done=提交完成
    var stage by remember { mutableStateOf("edit") }

    // ── §1 期間 ──
    var periodFrom by remember { mutableStateOf("") } // 開始日 yyyy-MM-dd
    var periodTo by remember { mutableStateOf("") } // 終了日 yyyy-MM-dd

    // ── §2 曜日・時間 ──
    // 自增 id 计数器：每加一个时段 +1，保证每行 key 唯一稳定（不用下标当 key）
    var slotIdSeq by remember { mutableStateOf(0L) }
    // 每个曜日各持一个可观察时段列表。remember 一次性建好「月→[] 火→[] …」5 个空列表
    val schedule: Map<String, SnapshotStateList<ScheduleSlot>> =
        remember { WEEKDAYS.associateWith { mutableStateListOf<ScheduleSlot>() } }

    // ── §3 契約書 ──
    var contractFileName by remember { mutableStateOf<String?>(null) } // 选中的（假）文件名，null=未选
    var contractNote by remember { mutableStateOf("") } // 補足説明

    // ── §4 理由 ──
    var reason by remember { mutableStateOf("") }

    // 已填的全部时段（跨 5 个曜日）
    val allSlots = schedule.values.flatten()

    // canSubmit（对齐规格 §4）：理由非空 + 終了日≥開始日 + 至少 1 个时段 + 所有时段 end>start。
    // 日期是 yyyy-MM-dd 字面串，字典序就等于时间序，直接字符串比较即可；时刻同理（HH:mm 补零）。
    val canSubmit =
        reason.trim().isNotEmpty() &&
            periodFrom.isNotEmpty() &&
            periodTo.isNotEmpty() &&
            periodTo >= periodFrom &&
            allSlots.isNotEmpty() &&
            allSlots.all { it.end > it.start }

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            // 标题逐字照规格 §4 行 1889「オンライン学習申請」
            PageHeader(
                title = "オンライン学習申請",
                level = 2,
                onLeft = {
                    // preview 态返回 = 回 edit；其余直接 popBackStack 回列表
                    if (stage == "preview") stage = "edit" else navController.popBackStack()
                },
            )

            when (stage) {
                // ── 编辑态：表单字段 + 底部「確認する」──
                "edit" -> {
                    EditBody(
                        periodFrom = periodFrom,
                        periodTo = periodTo,
                        schedule = schedule,
                        contractFileName = contractFileName,
                        contractNote = contractNote,
                        reason = reason,
                        canSubmit = canSubmit,
                        onPickFrom = { periodFrom = it },
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
                        onPickContract = {
                            // 文件选择 Android 暂不做真实 picker —— 点了弹提示 + 填假文件名占位
                            contractFileName = "contract.pdf"
                            store.showToast("ファイル選択は後日対応")
                            // TODO 真实 ContractFilePicker（拍照/相册/PDF + HEIC→JPEG + 10MB 限制）待做 —— 见规格 §5
                        },
                        onRemoveContract = { contractFileName = null },
                        onNote = { contractNote = it },
                        onReason = { reason = it },
                        onNext = { stage = "preview" },
                    )
                }

                // ── 确认态：只读键值卡 + 「提出する」/「修正する」──
                "preview" -> {
                    PreviewBody(
                        periodFrom = periodFrom,
                        periodTo = periodTo,
                        schedule = schedule,
                        contractFileName = contractFileName,
                        contractNote = contractNote,
                        reason = reason,
                        onSubmit = { stage = "done" },
                        onEdit = { stage = "edit" },
                    )
                }

                // ── 完成态：绿勾 + 大标题 + 预想审查时间 + 「一覧に戻る」──
                "done" -> {
                    DoneBody(
                        onBack = {
                            store.showToast("オンライン学習申請を提出しました")
                            navController.popBackStack()
                        },
                    )
                }
            }
        }
    }
}

// ───────────────────────────────────────────────────────────────
// 编辑态主体
// ───────────────────────────────────────────────────────────────
@Composable
private fun EditBody(
    periodFrom: String,
    periodTo: String,
    schedule: Map<String, SnapshotStateList<ScheduleSlot>>,
    contractFileName: String?,
    contractNote: String,
    reason: String,
    canSubmit: Boolean,
    onPickFrom: (String) -> Unit,
    onPickTo: (String) -> Unit,
    onAddSlot: (String) -> Unit,
    onRemoveSlot: (String, Long) -> Unit,
    onSlotStart: (String, Long, String) -> Unit,
    onSlotEnd: (String, Long, String) -> Unit,
    onPickContract: () -> Unit,
    onRemoveContract: () -> Unit,
    onNote: (String) -> Unit,
    onReason: (String) -> Unit,
    onNext: () -> Unit,
) {
    val t = SuzuT.current
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Spacer(Modifier.height(0.dp))

        // 黄色提示横幅（对齐规格 §4 行 1892）
        WarnBanner("オンライン学習開始の 3 日前までに提出してください")

        // ── §1 期間 ──
        SuzuCard {
            SectionTitle("期間")
            Spacer(Modifier.height(12.dp))
            DateField(
                label = "開始日",
                value = periodFrom,
                required = true,
                onPick = onPickFrom,
            )
            // 開始日的 hint 单独画一行（DateField 内不直接挂 hint）
            Text(
                "オンライン学習開始の 3 日前までに提出してください",
                color = t.inkMute,
                style = TextStyle(fontSize = 11.sp, lineHeight = 14.sp),
                modifier = Modifier.padding(top = 4.dp),
            )
            Spacer(Modifier.height(12.dp))
            DateField(
                label = "終了日",
                value = periodTo,
                required = true,
                onPick = onPickTo,
            )
        }

        // ── §2 曜日・時間 ── 周一～周五，每天一块
        SuzuCard {
            SectionTitle("曜日・時間")
            WEEKDAYS.forEach { day ->
                Spacer(Modifier.height(14.dp))
                DayBlock(
                    day = day,
                    slots = schedule[day] ?: emptyList(),
                    onAdd = { onAddSlot(day) },
                    onRemove = { id -> onRemoveSlot(day, id) },
                    onStart = { id, v -> onSlotStart(day, id, v) },
                    onEnd = { id, v -> onSlotEnd(day, id, v) },
                )
            }
        }

        // ── §3 契約書 ──
        SuzuCard {
            SectionTitle("契約書")
            Spacer(Modifier.height(12.dp))
            Field(
                label = "契約書ファイル",
                hint = "契約書の写真または PDF を添付してください（任意）",
            ) {
                if (contractFileName == null) {
                    // 未选：一个「契約書を選択」按钮（点了走文件选择桩）
                    GhostButton(title = "契約書を選択", onClick = onPickContract)
                } else {
                    // 已选：横行卡显示假文件名 + 右侧「×」删除
                    Row(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(12.dp))
                                .background(t.pill)
                                .padding(horizontal = 14.dp, vertical = 12.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Icon(SuzuIcons.Doc, contentDescription = null, tint = t.inkSub, modifier = Modifier.size(20.dp))
                        Spacer(Modifier.width(10.dp))
                        Text(
                            contractFileName,
                            color = t.ink,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium),
                            modifier = Modifier.weight(1f),
                        )
                        Box(
                            modifier =
                                Modifier
                                    .size(24.dp)
                                    .clip(RoundedCornerShape(percent = 50))
                                    .clickable(onClick = onRemoveContract),
                            contentAlignment = Alignment.Center,
                        ) {
                            Text("×", color = t.inkMute, style = TextStyle(fontSize = 18.sp))
                        }
                    }
                }
            }
            Spacer(Modifier.height(14.dp))
            Field(
                label = "補足説明",
                hint = "契約書の内容・受講証明・リンクなど（任意）",
            ) {
                TArea(
                    value = contractNote,
                    onValueChange = onNote,
                    placeholder = "契約書や受講証明の内容・リンクを入力",
                    rows = 3,
                )
            }
        }

        // ── §4 理由（必須）──
        SuzuCard {
            SectionTitle("理由")
            Spacer(Modifier.height(12.dp))
            Field(label = "理由", required = true) {
                TArea(
                    value = reason,
                    onValueChange = onReason,
                    placeholder = "オンライン学習を希望する理由を入力してください",
                    rows = 4,
                )
            }
        }

        // 底部「確認する」（必填齐了才可点）
        PrimaryButton(title = "確認する", enabled = canSubmit, onClick = onNext)
        Spacer(Modifier.height(24.dp))
    }
}

// 一个曜日块：标题「<曜日>曜日」+ 右侧「+」；无时段灰字「申請なし」；有时段每行 起〜终 + 红减号
@Composable
private fun DayBlock(
    day: String,
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
                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
            )
            Spacer(Modifier.weight(1f))
            // 蓝色「+」加时段按钮
            Box(
                modifier =
                    Modifier
                        .size(28.dp)
                        .clip(RoundedCornerShape(percent = 50))
                        .background(cs.primary)
                        .clickable(onClick = onAdd),
                contentAlignment = Alignment.Center,
            ) {
                Icon(SuzuIcons.Plus, contentDescription = null, tint = Color.White, modifier = Modifier.size(18.dp))
            }
        }
        if (slots.isEmpty()) {
            Spacer(Modifier.height(6.dp))
            Text("申請なし", color = t.inkMute, style = TextStyle(fontSize = 12.sp))
        } else {
            slots.forEach { slot ->
                Spacer(Modifier.height(8.dp))
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
                        style = TextStyle(fontSize = 15.sp),
                        modifier = Modifier.padding(horizontal = 8.dp),
                    )
                    TimeField(
                        label = "",
                        value = slot.end,
                        modifier = Modifier.weight(1f),
                        onPick = { onEnd(slot.id, it) },
                    )
                    Spacer(Modifier.width(8.dp))
                    // 红减号删除（无 trash 图标，用红底「－」）
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
            }
        }
    }
}

// ───────────────────────────────────────────────────────────────
// 确认态主体（只读键值卡）
// ───────────────────────────────────────────────────────────────
@Composable
private fun PreviewBody(
    periodFrom: String,
    periodTo: String,
    schedule: Map<String, SnapshotStateList<ScheduleSlot>>,
    contractFileName: String?,
    contractNote: String,
    reason: String,
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
        Spacer(Modifier.height(0.dp))

        // 蓝底信息条（对齐 iOS 确认页 ApplyPreviewView 提示）
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

        // 只读键值卡
        SuzuCard {
            KvRow("開始日", periodFrom.ifEmpty { "—" })
            KvRow("終了日", periodTo.ifEmpty { "—" })
            // 周课表逐曜日展示已填时段
            schedule.forEach { (day, slots) ->
                if (slots.isNotEmpty()) {
                    KvRow("${day}曜日", slots.joinToString("、") { "${it.start}〜${it.end}" })
                }
            }
            KvRow("契約書", contractFileName ?: "（未添付）")
            if (contractNote.isNotBlank()) KvRow("補足説明", contractNote)
            KvRow("理由", reason)
        }

        // 「提出する」 + 「修正する」
        PrimaryButton(title = "提出する", onClick = onSubmit)
        GhostButton(title = "修正する", onClick = onEdit)
        Spacer(Modifier.height(24.dp))
    }
}

// 只读键值行（左标签固定宽 + 右值；非首行顶部细线）
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

// ───────────────────────────────────────────────────────────────
// 完成态主体（居中绿勾 + 大标题 + 预想审查时间卡 + 「一覧に戻る」）
// 文案逐字照规格 §9 行 2009 ApplyDoneView
// ───────────────────────────────────────────────────────────────
@Composable
private fun DoneBody(onBack: () -> Unit) {
    val t = SuzuT.current
    Column(
        modifier =
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Spacer(Modifier.height(48.dp))
        // 居中绿勾
        Box(
            modifier =
                Modifier
                    .size(72.dp)
                    .clip(RoundedCornerShape(percent = 50))
                    .background(t.okBg),
            contentAlignment = Alignment.Center,
        ) {
            Icon(SuzuIcons.CheckCirc, contentDescription = null, tint = t.okDeep, modifier = Modifier.size(44.dp))
        }
        Text(
            "申請を提出しました",
            color = t.ink,
            style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold),
        )
        Text(
            "オンライン学習申請を受け付けました。\n審査完了時に通知でお知らせします。",
            color = t.inkSub,
            style = TextStyle(fontSize = 14.sp, lineHeight = 20.sp),
        )
        // 预想审查时间卡
        SuzuCard {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(SuzuIcons.CalClock, contentDescription = null, tint = t.inkSub, modifier = Modifier.size(18.dp))
                Spacer(Modifier.width(10.dp))
                Text(
                    "予想審査時間 1〜2 時間",
                    color = t.inkSub,
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Medium),
                )
            }
        }
        Spacer(Modifier.height(8.dp))
        PrimaryButton(title = "一覧に戻る", onClick = onBack)
        Spacer(Modifier.height(24.dp))
    }
}

// ───────────────────────────────────────────────────────────────
// 内部小组件
// ───────────────────────────────────────────────────────────────

// 卡内区块标题（14sp bold）
@Composable
private fun SectionTitle(title: String) {
    val t = SuzuT.current
    Text(title, color = t.ink, style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold))
}

// 黄色提示横幅（⚠ 图标 + 文字，圆角 12，warnBg 底）
@Composable
private fun WarnBanner(text: String) {
    val t = SuzuT.current
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(t.warnBg)
                .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(SuzuIcons.Warn, contentDescription = null, tint = t.warnDeep, modifier = Modifier.size(18.dp))
        Spacer(Modifier.width(10.dp))
        Text(text, color = t.warnDeep, style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp))
    }
}
