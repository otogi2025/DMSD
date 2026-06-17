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
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
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
import jp.tomoshibi.android.data.model.EventItem
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.Avatar
import jp.tomoshibi.android.ui.components.GhostButton
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.SectionHeader
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// ───────────────────────────────────────────────────────────────
// MyPageScreen（個人页着陆页 L1）— 对齐 iOS MyLandingView（截图 11）
// 从上到下 6 块：头像档案卡 / 行事予定卡 / 3 状态卡 / 履歴小标题 / 5 格宫格 / 设置 3 行
// 加 LogoutSheet（登出弹窗）并入本文件
// 数据全部从 MockData / 登录态 store 读，无网络层（跟 iOS 未接后端的屏一致）
// ───────────────────────────────────────────────────────────────

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MyPageScreen(navController: NavHostController) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()
    var showLogoutSheet by remember { mutableStateOf(false) }
    val sheetState = rememberModalBottomSheetState()

    // 用户档案：优先读登录态，空则回落假数据
    val user = state.user

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            // L1 头：左上 Home 图标，点回首页
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
                // ── 2.1 头像档案卡 ──
                ProfileCard(user.avatar, user.name, user.studentNo, user.dorm, user.room, user.category)

                // ── 2.2 行事予定卡 ──
                ScheduleCard(MockData.EVENTS_PREVIEW) { navController.navigate(Route.Schedule.path) }

                // ── 2.3 主要状态卡群（3 张竖排）──
                StudyStatusCard(user.isStudyTarget) { navController.navigate(Route.MyStudy.path) }
                RollcallStatusCard { navController.navigate(Route.MyRollcall.path) }
                PointsStatusCard(state.deductions.sumOf { it.points }) { navController.navigate(Route.MyPoints.path) }

                // ── 2.4 履歴 小标题 ──
                Spacer(Modifier.height(2.dp))
                SectionHeader(title = "履歴")

                // ── 2.5 履歴宫格（5 格 2 列）──
                HistoryGrid(navController)

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
                    // 登出：清登录态 + 令牌（DataStore authToken + 内存 ApiClient.token）+ 跳登录页（清空返回栈，回不去个人页）
                    jp.tomoshibi.android.data.network.ApiClient.token = null
                    store.update { it.copy(authed = false, authToken = null) }
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

// ── 2.2 行事予定卡：整卡可点去日程屏；列表取最近 3 条活动 ──
@Composable
private fun ScheduleCard(
    events: List<EventItem>,
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
            Spacer(Modifier.width(12.dp))
            Text("行事予定", color = t.ink, style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold))
            Spacer(Modifier.weight(1f))
            Text("すべて見る", color = primary, style = TextStyle(fontSize = 11.sp))
            Icon(SuzuIcons.ChevR, contentDescription = null, tint = primary, modifier = Modifier.size(14.dp))
        }
        // 列表（最多 3 条）；空时显示「当面の予定はありません」
        val shown = events.take(3)
        if (shown.isEmpty()) {
            Text("当面の予定はありません", color = t.inkMute, style = TextStyle(fontSize = 12.sp))
        } else {
            shown.forEachIndexed { i, ev ->
                if (i > 0) HorizontalDivider(color = t.hair, thickness = 0.5.dp)
                ScheduleRow(ev)
            }
        }
    }
}

// 行事予定 单行：左竖块「月 / 日」+ 竖线 + 右标题 / 时间
@Composable
private fun ScheduleRow(ev: EventItem) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    // EventItem.date 形如 "04-05"，拆出「月 / 日」
    val parts = ev.date.split("-")
    val month = parts.getOrNull(0)?.trimStart('0').orEmpty()
    val day = parts.getOrNull(1).orEmpty()
    Row(verticalAlignment = Alignment.CenterVertically) {
        Column(
            modifier = Modifier.width(40.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text("${month}月", color = primary, style = TextStyle(fontSize = 10.sp))
            Text(day, color = t.ink, style = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.Bold))
        }
        Box(modifier = Modifier.width(1.dp).height(32.dp).background(t.hair))
        Spacer(Modifier.width(12.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(ev.title, color = t.ink, style = TextStyle(fontSize = 13.5.sp, fontWeight = FontWeight.Bold), maxLines = 1)
            if (ev.time.isNotEmpty()) {
                Text(ev.time, color = t.inkSub, style = TextStyle(fontSize = 11.sp), maxLines = 1)
            }
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

// A.「夜学習ステータス」卡 — isStudyTarget=false 时显「対象外（今日）」；入口始终显示
@Composable
private fun StudyStatusCard(
    isStudyTarget: Boolean,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    val statusText = if (isStudyTarget) "進行中" else "対象外（今日）"
    StatusCardShell(iconBg = primary.copy(alpha = 0.10f), emoji = "📚", onClick = onClick) {
        Text("夜学習ステータス", color = t.inkSub, style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold))
        Text(statusText, color = t.ink, style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold))
        Text("履歴を見る →", color = primary, style = TextStyle(fontSize = 11.sp))
    }
}

// B. 今月の点呼卡 — 统计当月（2026-04）DEFAULT_ROLLCALL 的 時間内 / 遅刻 / 欠席 数
@Composable
private fun RollcallStatusCard(onClick: () -> Unit) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    // 演示口径：固定「2026-04」前缀过滤（生产版取系统当前年月）
    val thisMonth = MockData.DEFAULT_ROLLCALL.filter { it.date.startsWith("2026-04") }
    val onTime = thisMonth.count { it.status == "時間内" }
    val late = thisMonth.count { it.status == "遅刻" }
    val absent = thisMonth.count { it.status == "欠席" }
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

// C. 減点明細卡 — 分数 4.5（DEFAULT_DEDUCTIONS 合计）→ 4–7.9 档 = 橙 warn + Pill「注意」
@Composable
private fun PointsStatusCard(
    points: Double,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    // 分数档：<4 良好(绿) / 4–7.9 注意(橙) / ≥8 禁足(红)
    val (iconBg, numColor, tier) =
        when {
            points < 4.0 -> Triple(t.okBg, t.ok, PillTone.Ok to "良好")
            points < 8.0 -> Triple(t.warnBg, t.warn, PillTone.Warn to "注意")
            else -> Triple(t.dangerBg, t.danger, PillTone.Danger to "禁足")
        }
    StatusCardShell(iconBg = iconBg, emoji = "📉", onClick = onClick) {
        Text("減点明細", color = t.inkSub, style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold))
        Row(verticalAlignment = Alignment.Bottom, horizontalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(
                fmtPoints(points),
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

// ── 2.5 履歴宫格（5 格 2 列）── 格子标签 + 图标 + 目标路由（荷物受取履歴带红徽标「1」）
private data class GridBlock(
    val label: String,
    val icon: androidx.compose.ui.graphics.vector.ImageVector,
    val route: String,
    val badge: String? = null,
)

@Composable
private fun HistoryGrid(navController: NavHostController) {
    val blocks =
        listOf(
            GridBlock("個人情報", SuzuIcons.Person, Route.MyInfo.path),
            GridBlock("処分履歴", SuzuIcons.Warn, Route.MyDiscipline.path),
            GridBlock("体調報告履歴", SuzuIcons.Face, Route.MyHealth.path),
            GridBlock("申請履歴", SuzuIcons.Doc, Route.Applications.path),
            GridBlock("荷物受取履歴", SuzuIcons.Pkg, Route.MyPackages.path, badge = "1"),
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
        SettingsRow("通知設定", onClick = onNotify)
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
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
        containerColor = t.paper,
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
