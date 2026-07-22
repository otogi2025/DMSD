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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.format.JstDate
import jp.tomoshibi.android.data.model.User
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.MiscRequestBody
import jp.tomoshibi.android.data.network.endpoints.MiscRequestsAPI
import jp.tomoshibi.android.data.network.endpoints.OutingCreateBody
import jp.tomoshibi.android.data.network.endpoints.OutingsAPI
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.ChipGroup
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.TToggle
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

private val DATE_FMT = DateTimeFormatter.ofPattern("yyyy/MM/dd")
private val OUTING_TRANSPORTS = listOf("電車", "バス", "車", "徒歩", "その他")

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

        "夜学習欠席", "学習欠席" -> {
            // 「学習欠席」兼容旧路由；显示名以「夜学習欠席」为准（G9）
            StudyAbsenceForm(navController)
            return
        }

        "オンライン学習" -> {
            StudyOnlineForm(navController) // 在线学习届
            return
        }

        "行事企画" -> {
            DormEventProposalForm(navController) // 行事企画書
            return
        }

        "冷蔵庫購入" -> {
            FridgePurchaseForm(navController) // 冷蔵庫購入届
            return
        }

        "物品所持" -> {
            ItemPossessionForm(navController) // 物品所持許可願
            return
        }
    }

    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()
    val user = state.user
    var submitting by remember { mutableStateOf(false) }

    val today = remember { JstDate.today() }
    val tomorrow = remember { today.plusDays(1) }
    // 注意 kind 是日语显示名（「外出」），不是 ApplyType.key 那个英文 "outing"
    val isOuting = kind == OUTING_KIND
    // 外出可选今天；其余出寮日默认明天
    var leaveDate by remember { mutableStateOf(if (isOuting) today else tomorrow) }
    var returnDate by remember { mutableStateOf(tomorrow.plusDays(1)) }
    var dest by remember { mutableStateOf("") }
    var reason by remember { mutableStateOf("") }
    var leaveTime by remember { mutableStateOf("18:00") }
    var returnTime by remember { mutableStateOf("20:00") }
    var transport by remember { mutableStateOf<String?>(null) }
    var taxiReserved by remember { mutableStateOf(false) }
    var taxiTime by remember { mutableStateOf("18:00") }

    // 字段 visibility（kind 切 → hide）
    val showLeaveDate = kind in listOf("外出", "外泊", "帰省", "帰国")
    val showReturnDate = kind in listOf("外泊", "帰省", "帰国")
    val showReturnDateOnly = kind == "早帰"
    val showRepairFields = kind == "修繕"
    val showStudyFields = kind == "学習"
    val showGuestField = kind == "来訪者" // 来訪者必填「来訪者氏名」，対齐 iOS isGuest
    val showParcelField = kind == "代理受取" // 代理受取必填「荷物の概要」，対齐 iOS isParcel
    val showDestField = kind in listOf("外出", "外泊", "帰省", "帰国")
    val isMisc = kind in listOf("修繕", "来訪者", "代理受取")

    // 外出禁止（禁足）闸 — itsuki 2026-07-22 拍板：当月扣分 ≥8 分的学生不能提外出申请。
    // 8 分口径跟 TopRollBar.CleaningFlagRow 那条「外出禁止」标签同一套（user.points 由
    // AppStore.loadMe → DisciplineAPI.mySummary 填），别另发明阈值。
    // 这里只是客户端提前拦；真正的把关在后端 POST /outings（422 OUTING_BANNED），
    // 学生分数刚变化本地还没刷新时由后端兜底。
    val outingBanned = isOuting && user.points >= OUTING_BAN_POINTS

    // 期限校验：外出无 48h 截止（当天回寮）；其余有出寮日的类型适用
    val hasLeaveDateDeadline = !isOuting && (showLeaveDate || showReturnDateOnly)
    val now = LocalDateTime.now()
    val depAtSix = leaveDate.atTime(18, 0)
    val deadline48h = depAtSix.minusHours(48)
    val pastDeadline = hasLeaveDateDeadline && now.isAfter(deadline48h)

    // 出発日 picker dialog
    var showLeavePicker by remember { mutableStateOf(false) }
    var showReturnPicker by remember { mutableStateOf(false) }

    // 通用表单内置 3 段（对齐 iOS edit → ApplyPreviewView → ApplyDoneView）
    var stage by remember { mutableStateOf("edit") }

    // 外出 / 修繕 / 来訪者 / 代理受取 → 真后端提出
    fun submitNetwork() {
        if (submitting) return
        scope.launch {
            submitting = true
            val tokenAtStart = store.snapshot().authToken
            try {
                when {
                    isOuting -> {
                        OutingsAPI.create(
                            OutingCreateBody(
                                outingDate = leaveDate.toString(),
                                destination = dest.trim().takeIf { it.isNotEmpty() },
                                leaveTime = leaveTime,
                                returnTime = returnTime,
                                taxiReservationTime = if (taxiReserved) taxiTime else null,
                                reason = reason.trim().takeIf { it.isNotEmpty() },
                            ),
                        )
                        if (store.snapshot().authToken != tokenAtStart) return@launch
                        store.showToast("外出申請を提出しました")
                        stage = "done"
                    }

                    isMisc -> {
                        val backendKind =
                            when (kind) {
                                "修繕" -> "repair"
                                "来訪者" -> "guest"
                                "代理受取" -> "proxy_receipt"
                                else -> return@launch
                            }
                        val subject =
                            when (kind) {
                                "修繕" -> dest.trim().ifEmpty { kind }
                                else -> dest.trim().ifEmpty { kind }
                            }
                        val targetDate = if (kind == "来訪者") leaveDate.toString() else null
                        MiscRequestsAPI.create(
                            MiscRequestBody(
                                kind = backendKind,
                                subject = subject,
                                detail = reason.trim().takeIf { it.isNotEmpty() },
                                targetDate = targetDate,
                            ),
                        )
                        if (store.snapshot().authToken != tokenAtStart) return@launch
                        store.showToast("${kind}申請を提出しました")
                        stage = "done"
                    }

                    else -> {
                        // 早帰/学習等有专属表单分派，正常流程到不了这里；深链/异常 kind 落到 else 不假报成功
                        // （复审 android#13：原 stage="done" 会让未对接后端的 kind 显示「提出しました」但一覧无记录）
                        store.showToast("この申請種別は未対応です")
                    }
                }
            } catch (e: ApiError) {
                if (store.handleIfUnauthorized(e, tokenAtStart)) return@launch
                store.showToast(e.display)
            } catch (e: Exception) {
                store.showToast("申請の提出に失敗しました")
            } finally {
                submitting = false
            }
        }
    }

    // 确认页 — 对齐 iOS ApplyPreviewView（键值确认卡 +「提出後は審査待ち」banner +「戻る」「提出する」按钮）
    if (stage == "preview") {
        GenericApplyPreview(
            kind = kind,
            user = user,
            dest = dest,
            leaveDate = leaveDate,
            returnDate = returnDate,
            reason = reason,
            hasReturn = showReturnDate || showReturnDateOnly,
            navController = navController,
            onBack = { stage = "edit" },
            onSubmit = {
                // 外出/杂项走真后端；其余（早帰/学習等）不再写 store.applications（一覧从不读本地）
                submitNetwork()
            },
        )
        return
    }
    // 完成页 — 对齐 iOS ApplyDoneView（绿勾 +「申請を提出しました」+「審査時間の目安」卡 +「一覧へ」按钮）
    if (stage == "done") {
        GenericApplyDone(kind = kind, navController = navController)
        return
    }

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
                // ── 外出禁止 banner ── 当月扣分 ≥8 分时置顶显示，下面提交按钮同时置灰
                if (outingBanned) {
                    Row(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(10.dp))
                                .background(tokens.dangerBg)
                                .padding(12.dp),
                        verticalAlignment = Alignment.Top,
                    ) {
                        Text("⚠", color = tokens.danger, style = TextStyle(fontSize = 14.sp))
                        Spacer(Modifier.width(8.dp))
                        Text(
                            OUTING_BAN_NOTICE,
                            color = tokens.danger,
                            style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp),
                        )
                    }
                }

                // ── deadline warning banner ── 只对有出寮日的类型显示（修繕/来訪者/代理受取 无出寮日，隐藏）
                if (hasLeaveDateDeadline) {
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
                            // android#8: 原文案承诺「または週の水曜 23:59」但代码只算 48h（deadline48h），
                            // 两者矛盾 → 横幅改成与代码实际口径一致（出発 48 時間前）。
                            // TODO(S14 前评估): 分类型截止对齐 iOS（帰省=毎週水曜18:00 / 外泊=出発3日前）
                            // 需其它类型（早帰/学習等 iOS 未覆盖）的产品规则，另立跨端截止对齐项。
                            "出発日の 48 時間前までに提出してください",
                            color = tokens.warnDeep,
                            style = TextStyle(fontSize = 12.sp, lineHeight = 16.sp),
                        )
                    }
                }

                // ── 申請者本人 read-only block ──
                SectionTitle("1", "申請者本人")
                Column(
                    modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(tokens.paper),
                ) {
                    InfoRow("アカウント番号", user.studentNo, mono = true)
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
                        DateField(
                            if (isOuting) "外出日" else "出寮日",
                            leaveDate.format(DATE_FMT),
                        ) { showLeavePicker = true }
                        if (!isOuting) {
                            Text(
                                "※ 出寮日は明日以降のみ選択できます",
                                color = tokens.inkMute,
                                style = TextStyle(fontSize = 10.sp),
                            )
                        }
                        TimeChip(if (isOuting) "外出時刻" else "出寮時刻", leaveTime) { leaveTime = it }
                    }
                    if (isOuting) {
                        TimeChip("帰寮予定時刻", returnTime) { returnTime = it }
                    }
                    if (showReturnDate || showReturnDateOnly) {
                        DateField("帰寮日", returnDate.format(DATE_FMT)) { showReturnPicker = true }
                        TimeChip("帰寮時刻", returnTime) { returnTime = it }
                    }
                    if (showDestField) {
                        TextField2(if (isOuting) "行き先" else "行先", dest, "行き先を入力") { dest = it }
                    }
                    if (isOuting) {
                        Text(
                            "交通手段",
                            color = tokens.inkSub,
                            style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
                        )
                        ChipGroup(
                            options = OUTING_TRANSPORTS,
                            selected = transport,
                            onSelect = { transport = it },
                        )
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(
                                "タクシーを予約する",
                                color = tokens.ink,
                                modifier = Modifier.weight(1f),
                                style = TextStyle(fontSize = 13.sp),
                            )
                            TToggle(checked = taxiReserved, onCheckedChange = { taxiReserved = it })
                        }
                        if (taxiReserved) {
                            TimeChip("タクシー希望時刻", taxiTime) { taxiTime = it }
                        }
                    }
                    if (showRepairFields) {
                        TextField2("修繕場所", dest, "M101 室・洗面所") { dest = it }
                    }
                    if (showGuestField) {
                        TextField2("来訪者氏名", dest, "来訪者氏名を入力") { dest = it }
                    }
                    if (showParcelField) {
                        TextField2("荷物の概要", dest, "配送業者・個数") { dest = it }
                    }
                    if (showStudyFields) {
                        DateField("夜学習日", leaveDate.format(DATE_FMT)) { showLeavePicker = true }
                        TextField2("場所", dest, "図書室") { dest = it }
                    }
                    TextField2("理由", reason, "詳細を記入してください", multiline = true) { reason = it }
                }

                // ── submit ──
                // 「行先」/「来訪者氏名」/「荷物の概要」必填（对齐 iOS canSubmit needsDest）
                val needsDestField = showDestField || showGuestField || showParcelField || showRepairFields
                val canSubmit =
                    !pastDeadline &&
                        !outingBanned &&
                        !submitting &&
                        reason.isNotBlank() &&
                        (!needsDestField || dest.trim().isNotEmpty())
                Box(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .height(54.dp)
                            .clip(RoundedCornerShape(16.dp))
                            .background(if (canSubmit) tokens.ink else tokens.inkFaint)
                            .clickable(enabled = canSubmit) {
                                if (isOuting || isMisc) {
                                    // 外出 / 杂项：直接提后端（对齐 iOS GenericApplyForm 生产版）
                                    submitNetwork()
                                } else {
                                    stage = "preview"
                                }
                            },
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        when {
                            pastDeadline -> "提出期限を過ぎています"
                            submitting -> "提出中…"
                            else -> "提出する"
                        },
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
                        // 外出：今天起可选；其余出寮日：明天起
                        val todayJst = JstDate.today()
                        val ok = if (isOuting) !picked.isBefore(todayJst) else picked.isAfter(todayJst)
                        if (ok) leaveDate = picked
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

// ── 通用申请 确认页（对齐 iOS ApplyPreviewView）——键值确认卡 + info banner +「戻る」「提出する」──
@Composable
private fun GenericApplyPreview(
    kind: String,
    user: User,
    dest: String,
    leaveDate: LocalDate,
    returnDate: LocalDate,
    reason: String,
    hasReturn: Boolean,
    navController: NavHostController,
    onBack: () -> Unit,
    onSubmit: () -> Unit,
) {
    val t = SuzuT.current
    // 按类型拼确认行（左标签 / 右值），对齐 iOS ApplyPreviewView.rows
    val rows =
        buildList {
            add("種別" to "${kind}申請")
            add("申請者" to user.name)
            if (dest.isNotBlank()) add((if (kind == "修繕") "修繕場所" else "行先") to dest)
            if (kind in listOf("外出", "外泊", "帰省", "帰国", "学習")) {
                add("出寮日" to leaveDate.format(DATE_FMT))
            }
            if (hasReturn) add("帰寮日" to returnDate.format(DATE_FMT))
            add("理由" to reason.ifBlank { "—" })
        }
    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .background(t.pearl)
                    .verticalScroll(rememberScrollState()),
        ) {
            PageHeader(title = "申請内容の確認", level = 2, onLeft = onBack)
            Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp)) {
                // info banner
                Box(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(t.pill)
                            .padding(horizontal = 16.dp, vertical = 14.dp),
                ) {
                    Text(
                        "ℹ 提出後は審査待ちとなります。承認されるまでは内容の変更が可能です。",
                        color = t.inkSub,
                        style = TextStyle(fontSize = 13.sp, lineHeight = 18.sp),
                    )
                }
                Spacer(Modifier.height(18.dp))
                // 键值确认卡
                Column(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(14.dp))
                            .background(t.paper),
                ) {
                    rows.forEachIndexed { i, (label, value) ->
                        if (i > 0) Divider(color = t.hair, thickness = 0.5.dp)
                        Row(
                            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 14.dp),
                            verticalAlignment = Alignment.Top,
                        ) {
                            Text(label, color = t.inkSub, modifier = Modifier.width(100.dp), style = TextStyle(fontSize = 13.sp))
                            Text(
                                value,
                                color = t.ink,
                                modifier = Modifier.weight(1f),
                                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
                            )
                        }
                    }
                }
                Spacer(Modifier.height(20.dp))
                // 「戻る」「提出する」双按钮
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    Box(
                        modifier =
                            Modifier
                                .weight(1f)
                                .height(52.dp)
                                .clip(RoundedCornerShape(16.dp))
                                .background(t.paper)
                                .border(1.5.dp, t.hair, RoundedCornerShape(16.dp))
                                .clickable(onClick = onBack),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text("戻る", color = t.inkSub, style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold))
                    }
                    PrimaryButton(title = "提出する", modifier = Modifier.weight(1f), onClick = onSubmit)
                }
                Spacer(Modifier.height(24.dp))
            }
        }
    }
}

// ── 通用申请 完成页（对齐 iOS ApplyDoneView）——绿勾 +「申請を提出しました」+「審査時間の目安」+「一覧へ」──
@Composable
private fun GenericApplyDone(
    kind: String,
    navController: NavHostController,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .background(t.paper)
                    .padding(horizontal = 28.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            // 绿勾徽章 — 青→accent 渐变（对齐 iOS LinearGradient [primary, accent]）
            Box(
                modifier =
                    Modifier
                        .size(96.dp)
                        .clip(RoundedCornerShape(28.dp))
                        .background(Brush.linearGradient(listOf(cs.primary, cs.secondary))),
                contentAlignment = Alignment.Center,
            ) {
                Text("✓", color = Color.White, style = TextStyle(fontSize = 44.sp, fontWeight = FontWeight.Bold))
            }
            Spacer(Modifier.height(22.dp))
            Text("申請を提出しました", color = t.ink, style = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.ExtraBold))
            Spacer(Modifier.height(8.dp))
            Text(
                "${kind}申請を受け付けました。\n審査完了時に通知でお知らせします。",
                color = t.inkSub,
                textAlign = androidx.compose.ui.text.style.TextAlign.Center,
                style = TextStyle(fontSize = 14.sp, lineHeight = 20.sp),
            )
            Spacer(Modifier.height(28.dp))
            // 「審査時間の目安」卡（对齐 iOS ApplyDoneView）
            Row(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(14.dp))
                        .background(t.pearl)
                        .padding(horizontal = 16.dp, vertical = 14.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text("審査時間の目安", color = t.inkSub, style = TextStyle(fontSize = 12.sp))
                Spacer(Modifier.weight(1f))
                Text("1〜2 時間", color = t.ink, style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold))
            }
            Spacer(Modifier.height(28.dp))
            PrimaryButton(
                title = "一覧へ",
                modifier = Modifier.fillMaxWidth(),
                onClick = {
                    navController.navigate(jp.tomoshibi.android.nav.Route.Applications.path) {
                        popUpTo(jp.tomoshibi.android.nav.Route.Applications.path) { inclusive = true }
                    }
                },
            )
        }
    }
}
