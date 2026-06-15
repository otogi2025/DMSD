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
import androidx.compose.runtime.Composable
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

// 晩自習履歴 — 显示当月累计 + 历史明细
// 数据为 mock（v1.0 demo 不接 backend）；P6 后接真 Repository 时换成 store.studyLogs
private data class StudyEntry(val date: String, val place: String, val enter: String, val leave: String)

private val MOCK_ENTRIES = listOf(
    StudyEntry("04-01", "自習室 A", "19:30", "21:50"),
    StudyEntry("04-03", "自習室 B", "20:00", "22:00"),
    StudyEntry("04-05", "自習室 A", "18:45", "21:30"),
    StudyEntry("04-08", "自習室 A", "19:15", "20:45"),
    StudyEntry("04-10", "自習室 B", "20:10", "22:10"),
    StudyEntry("04-12", "自習室 A", "19:00", "21:30"),
    StudyEntry("04-15", "自習室 A", "19:30", "20:50")
)

@Composable
fun StudyScreen(navController: NavHostController) {
    val tokens = SuzuT.current

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            // 头部 — 返回按钮 + 标题
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
                Text("晩自習履歴", color = tokens.ink,
                    style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold))
            }

            // 统计卡 — 月累计大字（mono 数字）
            Column(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp)
                    .clip(RoundedCornerShape(18.dp))
                    .background(tokens.paper)
                    .padding(20.dp)
            ) {
                Text("今月の自習時間", color = tokens.inkSub,
                    style = TextStyle(fontSize = 12.sp))
                Spacer(Modifier.height(6.dp))
                Row(verticalAlignment = Alignment.Bottom) {
                    Text("12", color = tokens.ink,
                        style = MonoNumeralStyle.copy(fontSize = 48.sp, lineHeight = 52.sp))
                    Spacer(Modifier.width(4.dp))
                    Text("h", color = tokens.inkSub,
                        modifier = Modifier.padding(bottom = 8.dp),
                        style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.SemiBold))
                    Spacer(Modifier.width(8.dp))
                    Text("30", color = tokens.ink,
                        style = MonoNumeralStyle.copy(fontSize = 48.sp, lineHeight = 52.sp))
                    Spacer(Modifier.width(4.dp))
                    Text("min", color = tokens.inkSub,
                        modifier = Modifier.padding(bottom = 8.dp),
                        style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.SemiBold))
                }
            }

            Spacer(Modifier.height(16.dp))

            // 履歴 section title
            Text("履歴", color = tokens.inkSub,
                modifier = Modifier.padding(horizontal = 16.dp).padding(bottom = 8.dp),
                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Medium))

            // 历史列表
            Column(
                modifier = Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState())
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                MOCK_ENTRIES.forEach { e ->
                    Row(
                        modifier = Modifier.fillMaxWidth()
                            .clip(RoundedCornerShape(14.dp))
                            .background(tokens.paper)
                            .padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // 日期 pill
                        Box(
                            modifier = Modifier.clip(RoundedCornerShape(8.dp)).background(tokens.pill)
                                .padding(horizontal = 8.dp, vertical = 4.dp)
                        ) {
                            Text(e.date, color = tokens.ink,
                                style = MonoNumeralStyle.copy(fontSize = 12.sp, lineHeight = 16.sp,
                                    fontWeight = FontWeight.SemiBold))
                        }
                        Spacer(Modifier.width(12.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(e.place, color = tokens.ink,
                                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold))
                            Spacer(Modifier.height(2.dp))
                            Text(
                                text = "${e.enter} → ${e.leave}",
                                color = tokens.inkSub,
                                style = MonoNumeralStyle.copy(fontSize = 13.sp, lineHeight = 18.sp,
                                    fontWeight = FontWeight.Medium)
                            )
                        }
                    }
                }
                Spacer(Modifier.height(20.dp))
            }
        }
    }
}
