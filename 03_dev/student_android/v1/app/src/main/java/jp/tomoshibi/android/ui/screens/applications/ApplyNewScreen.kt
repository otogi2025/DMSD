package jp.tomoshibi.android.ui.screens.applications

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
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
import jp.tomoshibi.android.data.model.Application
import jp.tomoshibi.android.data.model.ApplicationStatus
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

// 7 类申请 — 对应 iOS APPLY_TYPES 前 7 个高頻 kind
private data class ApplyKindMeta(
    val key: String,
    val name: String,
    val sub: String,
)

private val APPLY_KINDS_7 =
    listOf(
        ApplyKindMeta("外出", "外出", "当日帰寮"),
        ApplyKindMeta("外泊", "外泊", "寮外宿泊"),
        ApplyKindMeta("帰省", "帰省", "実家帰省"),
        ApplyKindMeta("帰国", "帰国", "一時帰国"),
        ApplyKindMeta("早帰", "早帰", "門限前帰寮"),
        ApplyKindMeta("修繕", "修繕", "設備修繕"),
        ApplyKindMeta("学習", "学習", "学習関連"),
    )

private val DATE_FMT = DateTimeFormatter.ofPattern("yyyy/MM/dd")

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ApplyNewScreen(
    navController: NavHostController,
    kind: String = "外泊",
) {
    // 按申请类型分派到专属表单；外出/早帰/修繕/代理受取/来访/行事企画/冷藏库/物品/其他 等类型走下面通用表单
    when (kind) {
        "外泊", "帰省", "帰国" -> {
            StayForm(navController, kind) // 出寮届三合一
            return
        }

        "学習欠席" -> {
            StudyAbsenceForm(navController) // 学習欠席届
            return
        }

        "オンライン学習" -> {
            StudyOnlineForm(navController) // 在线学习届
            return
        }
    }

    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()
    val user = state.user

    val tomorrow = remember { LocalDate.now().plusDays(1) }
    var leaveDate by remember { mutableStateOf(tomorrow) }
    var returnDate by remember { mutableStateOf(tomorrow.plusDays(1)) }
    var dest by remember { mutableStateOf("") }
    var reason by remember { mutableStateOf("") }
    var leaveTime by remember { mutableStateOf("18:00") }
    var returnTime by remember { mutableStateOf("20:00") }

    // 申请期限：出発日 48 時間前 OR 出発日属週水曜 23:59、いずれか早い方
    val now = LocalDateTime.now()
    val depAtSix = leaveDate.atTime(18, 0)
    val deadline48h = depAtSix.minusHours(48)
    val pastDeadline = now.isAfter(deadline48h)

    // 字段 visibility（kind 切 → hide）
    val showLeaveDate = kind in listOf("外出", "外泊", "帰省", "帰国")
    val showReturnDate = kind in listOf("外泊", "帰省", "帰国")
    val showReturnDateOnly = kind == "早帰"
    val showRepairFields = kind == "修繕"
    val showStudyFields = kind == "学習"

    // 出発日 picker dialog
    var showLeavePicker by remember { mutableStateOf(false) }
    var showReturnPicker by remember { mutableStateOf(false) }

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            // ── header ──
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
                Text("${kind}申請", color = tokens.ink, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold))
            }

            Column(
                modifier =
                    Modifier
                        .weight(1f)
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 20.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp),
            ) {
                // ── deadline warning banner ──
                Row(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(10.dp))
                            .background(tokens.warnBg)
                            .padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text("⚠", color = tokens.warnDeep, style = TextStyle(fontSize = 14.sp))
                    Spacer(Modifier.width(8.dp))
                    Text(
                        "出発日の 48 時間前まで、または週の水曜 23:59 までに提出してください",
                        color = tokens.warnDeep,
                        style = TextStyle(fontSize = 12.sp, lineHeight = 16.sp),
                    )
                }

                // ── 申請者本人 read-only block ──
                SectionTitle("1", "申請者本人")
                Column(
                    modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(tokens.paper),
                ) {
                    InfoRow("学号", user.studentNo, mono = true)
                    Divider(color = tokens.hair, thickness = 0.5.dp)
                    InfoRow("氏名", user.name)
                    Divider(color = tokens.hair, thickness = 0.5.dp)
                    InfoRow("学年・組", user.gradeClass)
                    Divider(color = tokens.hair, thickness = 0.5.dp)
                    InfoRow("寮・部屋", "${user.dorm} ${user.room}")
                    Divider(color = tokens.hair, thickness = 0.5.dp)
                    InfoRow("区分", user.category)
                    Divider(color = tokens.hair, thickness = 0.5.dp)
                    InfoRow("携帯電話", user.phone, mono = true)
                }
                Text(
                    "※ ログイン中のアカウントで提出されます。他の生徒の代理提出はできません。",
                    color = tokens.inkMute,
                    style = TextStyle(fontSize = 11.sp, lineHeight = 16.sp),
                )

                // ── dynamic fields ──
                SectionTitle("2", "申請内容")
                Column(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(14.dp))
                            .background(tokens.paper)
                            .padding(14.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    if (showLeaveDate) {
                        DateField("出寮日", leaveDate.format(DATE_FMT)) { showLeavePicker = true }
                        Text(
                            "※ 出寮日は明日以降のみ選択できます",
                            color = tokens.inkMute,
                            style = TextStyle(fontSize = 10.sp),
                        )
                        TimeChip("出寮時刻", leaveTime) { leaveTime = it }
                    }
                    if (showReturnDate || showReturnDateOnly) {
                        DateField("帰寮日", returnDate.format(DATE_FMT)) { showReturnPicker = true }
                        TimeChip("帰寮時刻", returnTime) { returnTime = it }
                    }
                    if (kind in listOf("外出", "外泊", "帰省", "帰国")) {
                        TextField2("行先", dest, "実家（神戸市東灘区）") { dest = it }
                    }
                    if (showRepairFields) {
                        TextField2("修繕場所", dest, "M101 室・洗面所") { dest = it }
                    }
                    if (showStudyFields) {
                        DateField("学習日", leaveDate.format(DATE_FMT)) { showLeavePicker = true }
                        TextField2("場所", dest, "図書室") { dest = it }
                    }
                    TextField2("理由", reason, "詳細を記入してください", multiline = true) { reason = it }
                }

                // ── submit ──
                val canSubmit = !pastDeadline && reason.isNotBlank()
                Box(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .height(54.dp)
                            .clip(RoundedCornerShape(16.dp))
                            .background(if (canSubmit) tokens.ink else tokens.inkFaint)
                            .clickable(enabled = canSubmit) {
                                scope.launch {
                                    val newApp =
                                        Application(
                                            id = "A-${System.currentTimeMillis() % 100000}",
                                            kind = kind,
                                            dest = dest.ifBlank { "—" },
                                            from = leaveDate.toString(),
                                            to = if (showReturnDate || showReturnDateOnly) returnDate.toString() else leaveDate.toString(),
                                            status = ApplicationStatus.PENDING,
                                            reason = reason,
                                            createdAt = LocalDate.now().toString(),
                                        )
                                    store.update { it.copy(applications = listOf(newApp) + it.applications) }
                                    navController.popBackStack()
                                }
                            },
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        if (pastDeadline) "提出期限を過ぎています" else "提出する",
                        color = if (canSubmit) Color.White else tokens.inkSub,
                        style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold),
                    )
                }
                if (pastDeadline) {
                    Text(
                        "期限後の申請は寮監に直接ご相談ください",
                        color = tokens.danger,
                        style = TextStyle(fontSize = 11.sp),
                    )
                }
                Spacer(Modifier.height(40.dp))
            }
        }
    }

    if (showLeavePicker) {
        val pickerState =
            rememberDatePickerState(
                initialSelectedDateMillis =
                    leaveDate
                        .atStartOfDay(java.time.ZoneOffset.UTC)
                        .toInstant()
                        .toEpochMilli(),
            )
        DatePickerDialog(
            onDismissRequest = { showLeavePicker = false },
            confirmButton = {
                TextButton(onClick = {
                    pickerState.selectedDateMillis?.let {
                        val picked =
                            java.time.Instant
                                .ofEpochMilli(it)
                                .atZone(java.time.ZoneOffset.UTC)
                                .toLocalDate()
                        if (picked.isAfter(LocalDate.now())) leaveDate = picked
                    }
                    showLeavePicker = false
                }) { Text("OK") }
            },
            dismissButton = { TextButton(onClick = { showLeavePicker = false }) { Text("キャンセル") } },
        ) {
            DatePicker(state = pickerState)
        }
    }
    if (showReturnPicker) {
        val pickerState =
            rememberDatePickerState(
                initialSelectedDateMillis =
                    returnDate
                        .atStartOfDay(java.time.ZoneOffset.UTC)
                        .toInstant()
                        .toEpochMilli(),
            )
        DatePickerDialog(
            onDismissRequest = { showReturnPicker = false },
            confirmButton = {
                TextButton(onClick = {
                    pickerState.selectedDateMillis?.let {
                        val picked =
                            java.time.Instant
                                .ofEpochMilli(it)
                                .atZone(java.time.ZoneOffset.UTC)
                                .toLocalDate()
                        if (!picked.isBefore(leaveDate)) returnDate = picked
                    }
                    showReturnPicker = false
                }) { Text("OK") }
            },
            dismissButton = { TextButton(onClick = { showReturnPicker = false }) { Text("キャンセル") } },
        ) {
            DatePicker(state = pickerState)
        }
    }
}

@Composable
private fun SectionTitle(
    num: String,
    label: String,
) {
    val t = SuzuT.current
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        Box(
            modifier = Modifier.size(20.dp).clip(RoundedCornerShape(6.dp)).background(t.ink),
            contentAlignment = Alignment.Center,
        ) {
            Text(num, color = t.pearl, style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold))
        }
        Text(label, color = t.ink, style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold))
    }
}

@Composable
private fun InfoRow(
    label: String,
    value: String,
    mono: Boolean = false,
) {
    val t = SuzuT.current
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(label, color = t.inkSub, modifier = Modifier.width(80.dp), style = TextStyle(fontSize = 12.sp))
        Text(
            value,
            color = t.ink,
            style =
                TextStyle(
                    fontSize = 14.sp,
                    fontWeight = FontWeight.SemiBold,
                    fontFamily = if (mono) androidx.compose.ui.text.font.FontFamily.Monospace else null,
                ),
        )
    }
}

@Composable
private fun DateField(
    label: String,
    value: String,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Column {
        Text(label, color = t.inkSub, style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.SemiBold))
        Spacer(Modifier.height(6.dp))
        Box(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(10.dp))
                    .background(t.pill)
                    .clickable(onClick = onClick)
                    .padding(horizontal = 14.dp, vertical = 12.dp),
        ) {
            Text(
                value,
                color = t.ink,
                style =
                    TextStyle(
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                    ),
            )
        }
    }
}

@Composable
private fun TimeChip(
    label: String,
    value: String,
    onChange: (String) -> Unit,
) {
    val t = SuzuT.current
    val options = listOf("06:00", "12:00", "18:00", "20:00", "22:00")
    Column {
        Text(label, color = t.inkSub, style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.SemiBold))
        Spacer(Modifier.height(6.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            options.forEach { opt ->
                val active = opt == value
                Box(
                    modifier =
                        Modifier
                            .clip(RoundedCornerShape(99.dp))
                            .background(if (active) t.ink else t.paper)
                            .then(if (active) Modifier else Modifier.border(1.dp, t.hair, RoundedCornerShape(99.dp)))
                            .clickable { onChange(opt) }
                            .padding(horizontal = 10.dp, vertical = 6.dp),
                ) {
                    Text(
                        opt,
                        color = if (active) t.pearl else t.ink,
                        style =
                            TextStyle(
                                fontSize = 12.sp,
                                fontWeight = FontWeight.SemiBold,
                                fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                            ),
                    )
                }
            }
        }
    }
}

@Composable
private fun TextField2(
    label: String,
    value: String,
    hint: String,
    multiline: Boolean = false,
    onChange: (String) -> Unit,
) {
    val t = SuzuT.current
    Column {
        Text(label, color = t.inkSub, style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.SemiBold))
        Spacer(Modifier.height(6.dp))
        Box(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(10.dp))
                    .background(t.pill)
                    .padding(horizontal = 14.dp, vertical = 12.dp),
        ) {
            BasicTextField(
                value = value,
                onValueChange = onChange,
                textStyle = TextStyle(fontSize = 14.sp, color = t.ink),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Text),
                modifier = Modifier.fillMaxWidth().heightIn(min = if (multiline) 64.dp else 20.dp),
                singleLine = !multiline,
                decorationBox = { inner ->
                    if (value.isEmpty()) {
                        Text(hint, color = t.inkFaint, style = TextStyle(fontSize = 14.sp))
                    }
                    inner()
                },
            )
        }
    }
}
