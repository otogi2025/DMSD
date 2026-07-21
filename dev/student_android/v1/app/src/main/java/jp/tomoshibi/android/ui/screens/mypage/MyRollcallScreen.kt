package jp.tomoshibi.android.ui.screens.mypage

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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.ListLoadState
import jp.tomoshibi.android.data.network.endpoints.ProfileRollCallEntry
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// 点呼履历 + 详情 — 对齐 iOS MyRollcallView / MyRollcallDetailView 生产分支
// （无月份胶囊；数据来自 StudentProfileAPI → AppStore.myRollcallEvents）

private data class RollcallDisplay(
    val id: String,
    val date: String,
    val session: String,
    val state: String,
    val method: String,
    val checkinTime: String?,
    val windowStart: String?,
    val onTimeEnd: String?,
) {
    val isMorning: Boolean get() = session.startsWith("朝")
}

private fun ProfileRollCallEntry.toDisplay(): RollcallDisplay =
    RollcallDisplay(
        id = id,
        date = isoToYmd(checkedInAt),
        session = if (sessionType == "morning") "朝点呼" else "夜点呼",
        state = rollcallStateLabel(baseStatus),
        method = if (statusSource == "auto_nfc") "NFC" else "―",
        checkinTime = isoToHms(checkedInAt),
        windowStart = scheduledWindowStartAt?.let { isoToHms(it) },
        onTimeEnd = scheduledOnTimeEndAt?.let { isoToHms(it) },
    )

private fun toneOf(status: String): PillTone =
    when (status) {
        "時間内" -> PillTone.Ok
        "遅刻" -> PillTone.Warn
        "免除" -> PillTone.Neutral
        else -> PillTone.Danger
    }

@Composable
fun MyRollcallScreen(navController: NavHostController) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val events by store.myRollcallEvents.collectAsState()
    val profileState by store.profileState.collectAsState()

    LaunchedEffect(Unit) {
        store.loadMyProfile()
    }

    val grouped =
        rememberGrouped(events.map { it.toDisplay() })

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "点呼履歴", level = 2, onLeft = { navController.popBackStack() })

            Column(
                modifier =
                    Modifier
                        .fillMaxSize()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
            ) {
                Spacer(modifier = Modifier.height(4.dp))

                if (grouped.isEmpty()) {
                    when (val s = profileState) {
                        ListLoadState.Loading -> {
                            CircularProgressIndicator(
                                modifier =
                                    Modifier
                                        .align(Alignment.CenterHorizontally)
                                        .padding(vertical = 16.dp),
                            )
                        }

                        is ListLoadState.Failed -> {
                            EmptyState(
                                icon = SuzuIcons.Warn,
                                title = "読み込みに失敗しました",
                                message = s.message,
                            )
                        }

                        else -> {
                            EmptyState(icon = SuzuIcons.CheckCirc, title = "なし")
                        }
                    }
                }

                grouped.forEach { (date, entries) ->
                    Text(
                        date,
                        color = t.inkMute,
                        style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
                        modifier = Modifier.padding(bottom = 6.dp),
                    )
                    Column(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(16.dp))
                                .background(t.paper),
                    ) {
                        entries.forEachIndexed { index, entry ->
                            RollcallRow(
                                entry = entry,
                                onClick = {
                                    navController.navigate(Route.MyRollcallDetail(entry.id).path)
                                },
                            )
                            if (index < entries.lastIndex) {
                                Box(
                                    modifier =
                                        Modifier
                                            .fillMaxWidth()
                                            .height(1.dp)
                                            .background(t.hairSoft),
                                )
                            }
                        }
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                }

                Spacer(modifier = Modifier.height(20.dp))
            }
        }
    }
}

@Composable
private fun rememberGrouped(items: List<RollcallDisplay>): List<Pair<String, List<RollcallDisplay>>> =
    androidx.compose.runtime.remember(items) {
        val seen = linkedSetOf<String>()
        val map = linkedMapOf<String, MutableList<RollcallDisplay>>()
        items.forEach { d ->
            if (map[d.date] == null) {
                seen.add(d.date)
                map[d.date] = mutableListOf()
            }
            map[d.date]!!.add(d)
        }
        seen.map { it to (map[it] ?: emptyList()) }
    }

@Composable
private fun RollcallRow(
    entry: RollcallDisplay,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clickable(onClick = onClick)
                .padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            entry.session,
            color = t.ink,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
            modifier = Modifier.width(60.dp),
        )
        Spacer(modifier = Modifier.width(8.dp))
        Pill(text = entry.state, tone = toneOf(entry.state))
        Spacer(modifier = Modifier.weight(1f))
        Text(
            entry.method,
            color = t.inkMute,
            style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
        )
        Spacer(modifier = Modifier.width(8.dp))
        Icon(
            SuzuIcons.ChevR,
            contentDescription = null,
            tint = t.inkFaint,
            modifier = Modifier.width(18.dp),
        )
    }
}

@Composable
fun MyRollcallDetailScreen(
    navController: NavHostController,
    id: String?,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    val store = LocalAppStore.current
    val events by store.myRollcallEvents.collectAsState()

    LaunchedEffect(Unit) {
        if (events.isEmpty()) store.loadMyProfile()
    }

    val record =
        events
            .firstOrNull { it.id.equals(id, ignoreCase = true) }
            ?.toDisplay()

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "点呼セッション詳細", level = 2, onLeft = { navController.popBackStack() })

            Column(
                modifier =
                    Modifier
                        .fillMaxSize()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp),
            ) {
                if (record == null) {
                    EmptyState(icon = SuzuIcons.Search, title = "記録が見つかりません")
                } else {
                    val statusText =
                        when (record.state) {
                            "時間内", "present" -> "時間内"
                            "遅刻" -> "遅刻 0.5 点"
                            "欠席" -> "欠席 1.0 点"
                            "免除" -> "免除"
                            "記録なし" -> "記録なし"
                            else -> record.state // 未知态原样回显，不再兜底「時間内」（ios#58 对端）
                        }
                    val datePart = record.date.filter { it.isDigit() }
                    val sessionId = "RC-$datePart-${if (record.isMorning) "AM" else "PM"}"

                    Column(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(18.dp))
                                .background(t.paper)
                                .padding(18.dp),
                    ) {
                        Text(
                            "${record.date} ${record.session}",
                            color = cs.primary,
                            style =
                                TextStyle(
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.Bold,
                                    fontFamily = FontFamily.Monospace,
                                ),
                        )
                        Spacer(Modifier.height(4.dp))
                        Text(
                            "セッション ID: $sessionId",
                            color = t.inkMute,
                            style = TextStyle(fontSize = 12.sp, fontFamily = FontFamily.Monospace),
                        )
                        Spacer(Modifier.height(16.dp))
                        KvRow("状態", statusText)
                        KvRow("方式", record.method)
                        record.windowStart?.let { KvRow("開始時刻", it) }
                        record.onTimeEnd?.let { KvRow("締切時刻", it) }
                        if (record.checkinTime != null && record.state != "欠席") {
                            KvRow("チェックイン", record.checkinTime)
                        }
                    }

                    Row(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(12.dp))
                                .background(cs.primary.copy(alpha = 0.04f))
                                .padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Icon(
                            SuzuIcons.Info,
                            contentDescription = null,
                            tint = cs.primary,
                            modifier = Modifier.width(16.dp),
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            "判定の変更はされていません",
                            color = t.inkSub,
                            style = TextStyle(fontSize = 12.sp),
                        )
                    }
                }

                Spacer(modifier = Modifier.height(20.dp))
            }
        }
    }
}

@Composable
private fun KvRow(
    key: String,
    value: String,
) {
    val t = SuzuT.current
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            key,
            color = t.inkSub,
            style = TextStyle(fontSize = 13.sp),
            modifier = Modifier.width(96.dp),
        )
        Text(
            value,
            color = t.ink,
            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
        )
    }
}
