package jp.tomoshibi.android.ui.screens.mypage

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
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
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
import jp.tomoshibi.android.data.format.JstDate
import jp.tomoshibi.android.data.model.StudyState
import jp.tomoshibi.android.data.network.EventOut
import jp.tomoshibi.android.data.network.endpoints.EventsAPI
import jp.tomoshibi.android.data.network.endpoints.ProfileRollCallEntry
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.Avatar
import jp.tomoshibi.android.ui.components.GhostButton
import jp.tomoshibi.android.ui.components.GlassBottomSheet
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.SectionHeader
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.screens.community.isWaiting
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.format.DateTimeFormatter

// ───────────────────────────────────────────────────────────────
// MyPageScreen（个人页着陆页 L1）— 对齐 iOS MyLandingView 方案 B 五块式
// 头像档案 / 行事予定 / 3 状态卡 / 履歴 6 格 / 设置 3 行 + LogoutSheet
// ───────────────────────────────────────────────────────────────

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MyPageScreen(navController: NavHostController) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val packages by store.packages.collectAsState()
    val rollcallEvents by store.myRollcallEvents.collectAsState()
    val studyCountdown by store.studyCountdownSec.collectAsState()
    val scope = rememberCoroutineScope()
    var showLogoutSheet by remember { mutableStateOf(false) }
    val sheetState = rememberModalBottomSheetState()

    val user = state.user
    val placeholder = store.isProfilePlaceholder(state)

    // 进入个人页补拉 profile（点呼/减点当月统计）+ 包裹徽标
    LaunchedEffect(state.authed, state.authToken) {
        if (!state.authed || state.authToken.isNullOrEmpty()) return@LaunchedEffect
        store.loadMyProfile()
        store.loadMyPackages(reflectFailure = false)
    }

    // 行事予定卡：今天起升序取前 3（对齐 iOS upcomingEvents）
    var scheduleEvents by remember { mutableStateOf<List<EventOut>>(emptyList()) }
    var scheduleLoading by remember { mutableStateOf(false) }
    var scheduleFailed by remember { mutableStateOf(false) }
    LaunchedEffect(state.authed, state.authToken) {
        if (!state.authed || state.authToken.isNullOrEmpty()) return@LaunchedEffect
        scheduleLoading = true
        scheduleFailed = false
        try {
            val today = JstDate.today()
            val to = "${today.year + 1}-12-31"
            val raw = EventsAPI.listEvents(fromDate = today.toString(), toDate = to)
            scheduleEvents =
                raw
                    .filter { it.eventDate >= today.toString() }
                    .sortedBy { it.eventDate }
                    .take(3)
        } catch (_: Exception) {
            scheduleEvents = emptyList()
            scheduleFailed = true
        } finally {
            scheduleLoading = false
        }
    }

    val waitingBadge =
        packages.count { it.isWaiting }.takeIf { it > 0 }?.toString()

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(
                title = "マイページ",
                level = 1,
                onLeft = { navController.navigate(Route.Home.path) },
            )

            Column(
                modifier =
                    Modifier
                        .fillMaxSize()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                ProfileCard(user.avatar, user.name, user.studentNo, user.dorm, user.room, user.category)

                ScheduleCard(
                    events = scheduleEvents,
                    loading = scheduleLoading,
                    failed = scheduleFailed,
                ) { navController.navigate(Route.Schedule.path) }

                StudyStatusCard(
                    studyState = state.studyState,
                    countdownSec = studyCountdown,
                ) { navController.navigate(Route.MyStudy.path) }
                RollcallStatusCard(events = rollcallEvents) {
                    navController.navigate(Route.MyRollcall.path)
                }
                PointsStatusCard(
                    points = user.points,
                    placeholder = placeholder,
                ) { navController.navigate(Route.MyPoints.path) }

                Spacer(Modifier.height(2.dp))
                SectionHeader(title = "履歴")

                HistoryGrid(navController, packagesBadge = waitingBadge)

                // ── 2.6 设置列表（3 行）──
                SettingsCard(
                    onNotify = { navController.navigate(Route.MySettings.path) },
                    onAbout = { navController.navigate(Route.MyAbout.path) },
                    onLogout = { showLogoutSheet = true },
                )

                Spacer(Modifier.height(20.dp))
            }
        }
    }

    // ── 13. LogoutSheet（登出弹窗）──
    if (showLogoutSheet) {
        LogoutSheet(
            sheetState = sheetState,
            onDismiss = { showLogoutSheet = false },
            onLogout = {
                scope.launch {
                    // 登出：走 AppStore.clearSession（清加密令牌 + ApiClient + 用户绑定字段）
                    // 跳登录由 TomoshibiApp 会话门在 authed 变 false 时统一处理；这里再 navigate 一次保证栈清空。
                    store.clearSession()
                    showLogoutSheet = false
                    navController.navigate(Route.Login.path) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            },
        )
    }
}

// ── 2.1 头像档案卡：Avatar + 姓名 / 账号 / 两个 Pill（accent「寮 房间」+ neutral 区分）──
@Composable
private fun ProfileCard(
    avatar: String,
    name: String,
    studentNo: String,
    dorm: String,
    room: String,
    category: String,
) {
    val t = SuzuT.current
    SuzuCard(padding = 18, radius = 18) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Avatar(letter = avatar.ifEmpty { "リ" }, size = 56)
            Spacer(Modifier.width(14.dp))
            Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(
                    name.ifEmpty { "リュウ イヒ" },
                    color = t.ink,
                    style = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.Bold),
                )
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("アカウント ", color = t.inkMute, style = TextStyle(fontSize = 11.sp))
                    Text(
                        studentNo,
                        color = t.ink,
                        style =
                            TextStyle(
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                fontFamily = FontFamily.Monospace,
                            ),
                    )
                }
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    Pill("$dorm $room", PillTone.Accent)
                    Pill(category, PillTone.Neutral)
                }
            }
        }
    }
}

// ── 2.2 行事予定卡：整卡可点去日程屏；今天起升序取最近 3 条 ──
@Composable
private fun ScheduleCard(
    events: List<EventOut>,
    loading: Boolean,
    failed: Boolean,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(18.dp))
                .background(t.paper)
                .border(0.5.dp, t.hair, RoundedCornerShape(18.dp))
                .clickable(onClick = onClick)
                .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        // 头部一行：日历图标方块 +「行事予定」+「すべて見る →」
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier =
                    Modifier
                        .size(40.dp)
                        .clip(RoundedCornerShape(10.dp))
                        .background(primary.copy(alpha = 0.10f)),
                contentAlignment = Alignment.Center,
            ) {
                Icon(SuzuIcons.Cal, contentDescription = null, tint = primary, modifier = Modifier.size(20.dp))
            }
            Spacer(modifier = Modifier.width(12.dp))
            Text("行事予定", color = t.ink, style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold))
            Spacer(modifier = Modifier.weight(1f))
            Text("すべて見る", color = primary, style = TextStyle(fontSize = 11.sp))
            Icon(SuzuIcons.ChevR, contentDescription = null, tint = primary, modifier = Modifier.size(14.dp))
        }
        when {
            loading -> {
                Text("読み込み中…", color = t.inkMute, style = TextStyle(fontSize = 12.sp))
            }

            failed -> {
                Text("読み込みに失敗しました", color = t.inkMute, style = TextStyle(fontSize = 12.sp))
            }

            events.isEmpty() -> {
                Text("直近の予定はありません", color = t.inkMute, style = TextStyle(fontSize = 12.sp))
            }

            else -> {
                events.forEachIndexed { i, ev ->
                    if (i > 0) HorizontalDivider(color = t.hair, thickness = 0.5.dp)
                    ScheduleRow(ev)
                }
            }
        }
    }
}

// 行事予定 单行：左竖块「月 / 日」+ 竖线 + 右标题（生产版 place 恒空，不显副行）
@Composable
private fun ScheduleRow(ev: EventOut) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    // eventDate 形如 "2026-04-05"，拆出「月 / 日」
    val parts = ev.eventDate.split("-")
    val month = parts.getOrNull(1)?.trimStart('0').orEmpty()
    val day = parts.getOrNull(2).orEmpty()
    Row(verticalAlignment = Alignment.CenterVertically) {
        Column(
            modifier = Modifier.width(40.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text("${month}月", color = primary, style = TextStyle(fontSize = 10.sp, fontWeight = FontWeight.Bold))
            Text(day, color = t.ink, style = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.Bold))
        }
        Box(
            modifier =
                Modifier
                    .width(1.dp)
                    .height(32.dp)
                    .background(t.hair),
        )
        Spacer(modifier = Modifier.width(12.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(ev.title, color = t.ink, style = TextStyle(fontSize = 13.5.sp, fontWeight = FontWeight.Bold), maxLines = 1)
        }
    }
}

// ── 2.3 状态卡外壳：左 48 方块 emoji + 右 3 行文字，整卡可点 ──
@Composable
private fun StatusCardShell(
    iconBg: Color,
    emoji: String,
    onClick: () -> Unit,
    rightContent: @Composable () -> Unit,
) {
    val t = SuzuT.current
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(18.dp))
                .background(t.paper)
                .border(0.5.dp, t.hair, RoundedCornerShape(18.dp))
                .clickable(onClick = onClick)
                .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            modifier =
                Modifier
                    .size(48.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(iconBg),
            contentAlignment = Alignment.Center,
        ) {
            Text(emoji, style = TextStyle(fontSize = 22.sp))
        }
        Spacer(Modifier.width(12.dp))
        Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            rightContent()
        }
    }
}

// A.「夜学習ステータス」卡 — 4 态（对齐 iOS studyStateText）
@Composable
private fun StudyStatusCard(
    studyState: StudyState,
    countdownSec: Int,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    val statusText =
        when (studyState) {
            StudyState.OFF -> {
                "本日は対象外"
            }

            StudyState.UPCOMING -> {
                val m = countdownSec / 60
                val s = countdownSec % 60
                "開始まで $m:${s.toString().padStart(2, '0')}"
            }

            StudyState.ACTIVE -> {
                "進行中"
            }

            StudyState.DONE -> {
                "本日完了"
            }
        }
    StatusCardShell(iconBg = primary.copy(alpha = 0.10f), emoji = "📚", onClick = onClick) {
        Text("夜学習ステータス", color = t.inkSub, style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold))
        Text(statusText, color = t.ink, style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold))
        Text("履歴を見る →", color = primary, style = TextStyle(fontSize = 11.sp))
    }
}

// B.「今月の点呼」卡 — 按当月真 profile 事件统计
@Composable
private fun RollcallStatusCard(
    events: List<ProfileRollCallEntry>,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    val monthPrefix = JstDate.monthPrefix()
    var onTime = 0
    var late = 0
    var absent = 0
    events.forEach { e ->
        val date = isoToYmd(e.checkedInAt)
        if (!date.startsWith(monthPrefix)) return@forEach
        when (rollcallStateLabel(e.baseStatus)) {
            "時間内" -> onTime++
            "遅刻" -> late++
            "欠席" -> absent++
        }
    }
    StatusCardShell(iconBg = t.okBg, emoji = "📋", onClick = onClick) {
        Text("今月の点呼", color = t.inkSub, style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold))
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.CenterVertically) {
            RollcallStat(onTime, "時間内", t.ok)
            RollcallStat(late, "遅刻", t.warn)
            RollcallStat(absent, "欠席", t.danger)
        }
        Text("詳細を見る →", color = primary, style = TextStyle(fontSize = 11.sp))
    }
}

// 点呼统计单块：数字 + 小标签
@Composable
private fun RollcallStat(
    n: Int,
    label: String,
    color: Color,
) {
    Row(verticalAlignment = Alignment.Bottom, horizontalArrangement = Arrangement.spacedBy(3.dp)) {
        Text(
            "$n",
            color = color,
            style = TextStyle(fontSize = 17.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace),
        )
        Text(label, color = color, style = TextStyle(fontSize = 10.5.sp))
    }
}

// C.「減点明細」卡 — 真 user.points；占位时显「—」
@Composable
private fun PointsStatusCard(
    points: Double,
    placeholder: Boolean,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    val (iconBg, numColor, tier) =
        when {
            placeholder -> Triple(t.pill, t.inkMute, PillTone.Neutral to "—")
            points >= 8.0 -> Triple(t.dangerBg, t.danger, PillTone.Danger to "禁足")
            points >= 4.0 -> Triple(t.warnBg, t.warn, PillTone.Warn to "注意")
            else -> Triple(t.okBg, t.ok, PillTone.Ok to "良好")
        }
    StatusCardShell(iconBg = iconBg, emoji = "📉", onClick = onClick) {
        Text("減点明細", color = t.inkSub, style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold))
        Row(verticalAlignment = Alignment.Bottom, horizontalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(
                if (placeholder) "—" else fmtPoints(points),
                color = numColor,
                style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace),
            )
            Text("点", color = t.inkSub, style = TextStyle(fontSize = 12.sp))
            Spacer(Modifier.width(4.dp))
            Pill(tier.second, tier.first)
        }
        Text("詳細を見る →", color = primary, style = TextStyle(fontSize = 11.sp))
    }
}

// 分数格式化：整数去小数点（4.0→「4」），否则保留 1 位（4.5→「4.5」）
private fun fmtPoints(p: Double): String = if (p % 1.0 == 0.0) p.toInt().toString() else p.toString()

internal fun rollcallStateLabel(baseStatus: String): String =
    when (baseStatus) {
        "present" -> "時間内"
        "late" -> "遅刻"
        "absent" -> "欠席"
        "exempt_range" -> "免除"
        "init" -> "記録なし"
        else -> baseStatus
    }

internal fun isoToYmd(iso: String): String =
    try {
        val instant =
            try {
                java.time.OffsetDateTime
                    .parse(iso)
                    .toInstant()
            } catch (_: Exception) {
                java.time.Instant.parse(iso)
            }
        DateTimeFormatter
            .ofPattern("yyyy-MM-dd")
            .withZone(JstDate.TOKYO)
            .format(instant)
    } catch (_: Exception) {
        iso.take(10)
    }

internal fun isoToHms(iso: String): String? =
    try {
        val instant =
            try {
                java.time.OffsetDateTime
                    .parse(iso)
                    .toInstant()
            } catch (_: Exception) {
                java.time.Instant.parse(iso)
            }
        DateTimeFormatter
            .ofPattern("HH:mm:ss")
            .withZone(JstDate.TOKYO)
            .format(instant)
    } catch (_: Exception) {
        null
    }

// ── 履歴宫格（6 格 2 列）── 含罚扫履历；荷物徽标按待取件数动态算
private data class GridBlock(
    val label: String,
    val icon: androidx.compose.ui.graphics.vector.ImageVector,
    val route: String,
    val badge: String? = null,
)

@Composable
private fun HistoryGrid(
    navController: NavHostController,
    packagesBadge: String?,
) {
    val blocks =
        listOf(
            GridBlock("個人情報", SuzuIcons.Person, Route.MyInfo.path),
            GridBlock("処分履歴", SuzuIcons.Warn, Route.MyDiscipline.path),
            GridBlock("体調報告履歴", SuzuIcons.Face, Route.MyHealth.path),
            GridBlock("申請履歴", SuzuIcons.Doc, Route.Applications.path),
            GridBlock("罰則清掃 履歴", SuzuIcons.Sparkles, Route.MyClean.path),
            GridBlock("荷物受取履歴", SuzuIcons.Pkg, Route.MyPackages.path, badge = packagesBadge),
        )
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        blocks.chunked(2).forEach { rowItems ->
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                rowItems.forEach { block ->
                    GridCell(block, modifier = Modifier.weight(1f)) { navController.navigate(block.route) }
                }
                if (rowItems.size == 1) Spacer(Modifier.weight(1f))
            }
        }
    }
}

// 履歴宫格单格：左上图标方块 + 底部标签 +（可选）右上红徽标
@Composable
private fun GridCell(
    block: GridBlock,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    Box(
        modifier =
            modifier
                .clip(RoundedCornerShape(16.dp))
                .background(t.paper)
                .border(0.5.dp, t.hair, RoundedCornerShape(16.dp))
                .clickable(onClick = onClick)
                .heightIn(min = 80.dp)
                .padding(14.dp),
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            Box(
                modifier =
                    Modifier
                        .size(38.dp)
                        .clip(RoundedCornerShape(10.dp))
                        .background(primary.copy(alpha = 0.10f)),
                contentAlignment = Alignment.Center,
            ) {
                Icon(block.icon, contentDescription = null, tint = primary, modifier = Modifier.size(17.dp))
            }
            Spacer(Modifier.weight(1f))
            Spacer(Modifier.height(8.dp))
            Text(block.label, color = t.ink, style = TextStyle(fontSize = 13.5.sp, fontWeight = FontWeight.Bold))
        }
        if (block.badge != null) {
            Box(
                modifier =
                    Modifier
                        .align(Alignment.TopEnd)
                        .clip(RoundedCornerShape(percent = 50))
                        .background(t.danger)
                        .padding(horizontal = 7.dp, vertical = 2.dp),
            ) {
                Text(block.badge, color = Color.White, style = TextStyle(fontSize = 10.sp, fontWeight = FontWeight.Bold))
            }
        }
    }
}

// ── 2.6 设置列表（3 行）── 通知設定 / Tomoshibi について / ログアウト(红，无箭头)
@Composable
private fun SettingsCard(
    onNotify: () -> Unit,
    onAbout: () -> Unit,
    onLogout: () -> Unit,
) {
    val t = SuzuT.current
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(16.dp))
                .background(t.paper)
                .border(0.5.dp, t.hair, RoundedCornerShape(16.dp)),
    ) {
        SettingsRow("設定", onClick = onNotify)
        HorizontalDivider(color = t.hair, thickness = 0.5.dp)
        SettingsRow("Tomoshibi について", onClick = onAbout)
        HorizontalDivider(color = t.hair, thickness = 0.5.dp)
        SettingsRow("ログアウト", danger = true, onClick = onLogout)
    }
}

@Composable
private fun SettingsRow(
    label: String,
    danger: Boolean = false,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clickable(onClick = onClick)
                .padding(horizontal = 18.dp, vertical = 16.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            label,
            color = if (danger) t.danger else t.ink,
            modifier = Modifier.weight(1f),
            style = TextStyle(fontSize = 14.5.sp, fontWeight = FontWeight.Medium),
        )
        // 红色 ログアウト 行不显箭头
        if (!danger) {
            Icon(SuzuIcons.ChevR, contentDescription = null, tint = t.inkFaint, modifier = Modifier.size(18.dp))
        }
    }
}

// ── 13. LogoutSheet（登出弹窗）── ModalBottomSheet + 标题 / 正文 / 红登出 / キャンセル
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun LogoutSheet(
    sheetState: androidx.compose.material3.SheetState,
    onDismiss: () -> Unit,
    onLogout: () -> Unit,
) {
    val t = SuzuT.current
    GlassBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
    ) {
        Column(
            modifier = Modifier.padding(horizontal = 24.dp).padding(bottom = 32.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(
                "ログアウトしますか？",
                color = t.ink,
                style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold),
            )
            Text(
                "次回起動時はアカウント番号と\nパスワードが必要です",
                color = t.inkSub,
                style = TextStyle(fontSize = 13.sp, lineHeight = 19.sp),
            )
            Spacer(Modifier.height(4.dp))
            PrimaryButton("ログアウト", destructive = true, onClick = onLogout)
            GhostButton("キャンセル", onClick = onDismiss)
        }
    }
}
