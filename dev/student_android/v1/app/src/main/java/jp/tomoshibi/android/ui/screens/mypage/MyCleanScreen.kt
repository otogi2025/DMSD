package jp.tomoshibi.android.ui.screens.mypage

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
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
import jp.tomoshibi.android.data.network.endpoints.CleaningAssignmentOut
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter

// 罚扫履历（L2）— 对齐 iOS MyCleanView：
//   PageHeader「罰則清掃 履歴」+ 卡片（地点 / 日期时刻 / 状态 Pill + 却下理由）+ 三态空态

@Composable
fun MyCleanScreen(navController: NavHostController) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val rows by store.cleaningHistory.collectAsState()
    val loadState by store.cleaningHistoryState.collectAsState()

    LaunchedEffect(Unit) {
        store.loadCleaningHistory()
    }

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "罰則清掃 履歴", level = 2, onLeft = { navController.popBackStack() })

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 20.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                Spacer(modifier = Modifier.height(4.dp))

                if (rows.isEmpty()) {
                    when (val s = loadState) {
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
                            EmptyState(icon = SuzuIcons.Sparkles, title = "なし")
                        }
                    }
                } else {
                    rows.forEach { a ->
                        CleanCard(a)
                    }
                }

                Spacer(modifier = Modifier.height(24.dp))
            }
        }
    }
}

@Composable
private fun CleanCard(a: CleaningAssignmentOut) {
    val t = SuzuT.current
    val pillText = statusLabel(a.status)
    val tone = statusTone(a.status)
    val rejected = a.status == "failed"
    SuzuCard(padding = 14) {
        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    Text(
                        a.area,
                        color = t.ink,
                        style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                    )
                    Text(
                        formatCleaningDateTime(a.scheduledAt),
                        color = t.inkMute,
                        style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
                    )
                }
                Pill(text = pillText, tone = tone)
            }
            if (rejected && !a.failureReason.isNullOrBlank()) {
                Text(
                    a.failureReason!!,
                    color = t.danger,
                    style = TextStyle(fontSize = 12.sp),
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(8.dp))
                            .background(t.dangerBg)
                            .padding(horizontal = 10.dp, vertical = 8.dp),
                )
            }
        }
    }
}

private fun statusLabel(s: String): String =
    when (s) {
        "passed" -> "通過"
        "failed" -> "差し戻し"
        "done" -> "提出済"
        "assigned" -> "未提出"
        "skipped" -> "免除"
        else -> s
    }

private fun statusTone(s: String): PillTone =
    when (s) {
        "passed" -> PillTone.Ok
        "failed" -> PillTone.Danger
        "done" -> PillTone.Accent
        else -> PillTone.Neutral
    }

private val cleaningFmt: DateTimeFormatter =
    DateTimeFormatter
        .ofPattern("M月d日 H時mm分")
        .withZone(ZoneId.of("Asia/Tokyo"))

private fun formatCleaningDateTime(iso: String): String =
    try {
        val instant = OffsetDateTime.parse(iso).toInstant()
        cleaningFmt.format(instant)
    } catch (_: Exception) {
        try {
            val instant = java.time.Instant.parse(iso)
            cleaningFmt.format(instant)
        } catch (_: Exception) {
            iso.take(16).replace('T', ' ')
        }
    }
