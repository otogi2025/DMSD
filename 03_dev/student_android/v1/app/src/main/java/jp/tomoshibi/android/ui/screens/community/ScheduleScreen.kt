package jp.tomoshibi.android.ui.screens.community

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.MonoNumeralStyle
import jp.tomoshibi.android.ui.theme.SuzuT

// 行事 — 14 件 mock，包含 iOS Home preview 用的两条权威值（04-05/04-07）
private data class ScheduleEvent(val date: String, val title: String, val time: String)

private val MOCK_EVENTS = listOf(
    ScheduleEvent("04-02", "新入生 オリエンテーション", "09:00"),
    ScheduleEvent("04-05", "留 4 アクティビティ", "08:30"),
    ScheduleEvent("04-07", "帰寮日", "15:33"),
    ScheduleEvent("04-09", "防災訓練", "10:00"),
    ScheduleEvent("04-12", "寮ミーティング", "19:00"),
    ScheduleEvent("04-14", "クラブ活動説明会", "16:30"),
    ScheduleEvent("04-17", "面談（担任）", "14:00"),
    ScheduleEvent("04-20", "図書館見学", "13:00"),
    ScheduleEvent("04-22", "中間試験開始", "08:30"),
    ScheduleEvent("04-25", "留学生交流会", "18:00"),
    ScheduleEvent("04-27", "バス遠足申込締切", "17:00"),
    ScheduleEvent("04-29", "親睦食事会", "18:30"),
    ScheduleEvent("05-01", "GW 開始", "00:00"),
    ScheduleEvent("05-06", "GW 後 帰寮", "20:00")
)

@Composable
fun ScheduleScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    var month by remember { mutableStateOf(4) }

    // 按日期分组（保持原顺序）— mock 内已有序
    val grouped = remember(month) {
        val prefix = month.toString().padStart(2, '0')
        MOCK_EVENTS.filter { it.date.startsWith(prefix) }.groupBy { it.date }
    }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            // 头部
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp).padding(top = 18.dp, bottom = 12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier.size(44.dp).clip(CircleShape).clickable { navController.popBackStack() },
                    contentAlignment = Alignment.Center
                ) {
                    Icon(SuzuIcons.ChevL, contentDescription = "戻る", tint = tokens.ink, modifier = Modifier.size(24.dp))
                }
                Spacer(Modifier.width(4.dp))
                Text("行事スケジュール", color = tokens.ink,
                    style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold))
            }

            // 月切替
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp).padding(bottom = 12.dp),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier.size(36.dp).clip(CircleShape)
                        .background(tokens.paper)
                        .clickable(enabled = month > 1) { if (month > 1) month -= 1 },
                    contentAlignment = Alignment.Center
                ) {
                    Icon(SuzuIcons.ChevL, contentDescription = "前月",
                        tint = if (month > 1) tokens.ink else tokens.inkFaint,
                        modifier = Modifier.size(20.dp))
                }
                Spacer(Modifier.width(20.dp))
                Text("${month.toString().padStart(2, '0')} 月",
                    color = tokens.ink,
                    style = MonoNumeralStyle.copy(fontSize = 22.sp, lineHeight = 28.sp,
                        fontWeight = FontWeight.SemiBold))
                Spacer(Modifier.width(20.dp))
                Box(
                    modifier = Modifier.size(36.dp).clip(CircleShape)
                        .background(tokens.paper)
                        .clickable(enabled = month < 12) { if (month < 12) month += 1 },
                    contentAlignment = Alignment.Center
                ) {
                    Icon(SuzuIcons.ChevR, contentDescription = "次月",
                        tint = if (month < 12) tokens.ink else tokens.inkFaint,
                        modifier = Modifier.size(20.dp))
                }
            }

            // 列表
            Column(
                modifier = Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState())
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                if (grouped.isEmpty()) {
                    Box(
                        modifier = Modifier.fillMaxWidth().padding(vertical = 60.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("この月の予定はありません", color = tokens.inkMute,
                            style = TextStyle(fontSize = 14.sp))
                    }
                }
                grouped.forEach { (date, events) ->
                    events.forEach { e ->
                        Row(
                            modifier = Modifier.fillMaxWidth()
                                .clip(RoundedCornerShape(12.dp))
                                .background(tokens.paper)
                                .padding(14.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            // 日期 pill
                            Box(
                                modifier = Modifier.clip(RoundedCornerShape(8.dp))
                                    .background(tokens.pill)
                                    .padding(horizontal = 8.dp, vertical = 4.dp)
                            ) {
                                Text(date, color = tokens.ink,
                                    style = MonoNumeralStyle.copy(fontSize = 12.sp, lineHeight = 16.sp,
                                        fontWeight = FontWeight.SemiBold))
                            }
                            Spacer(Modifier.width(12.dp))
                            Column(modifier = Modifier.weight(1f)) {
                                Text(e.title, color = tokens.ink,
                                    style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold))
                            }
                            Spacer(Modifier.width(8.dp))
                            Text(e.time, color = tokens.inkSub,
                                style = MonoNumeralStyle.copy(fontSize = 13.sp, lineHeight = 18.sp,
                                    fontWeight = FontWeight.Medium))
                        }
                    }
                }
                Spacer(Modifier.height(20.dp))
            }
        }
    }
}
