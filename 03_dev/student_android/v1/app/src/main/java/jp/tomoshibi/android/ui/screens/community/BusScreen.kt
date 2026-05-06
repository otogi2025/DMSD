package jp.tomoshibi.android.ui.screens.community

import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.MonoNumeralStyle
import jp.tomoshibi.android.ui.theme.SuzuT

// 路线 mock — 高校棟 → 金川駅 同一路线
private data class BusRow(val time: String, val route: String, val highlight: Boolean = false)

private val WEEKDAY = listOf(
    BusRow("07:30", "高校棟 → 金川駅"),
    BusRow("08:20", "高校棟 → 金川駅"),
    BusRow("09:20", "高校棟 → 金川駅", highlight = true),
    BusRow("12:30", "金川駅 → 高校棟"),
    BusRow("15:30", "金川駅 → 高校棟"),
    BusRow("17:00", "金川駅 → 高校棟"),
    BusRow("18:30", "金川駅 → 高校棟"),
    BusRow("21:00", "金川駅 → 高校棟")
)

private val SATURDAY = listOf(
    BusRow("08:00", "高校棟 → 金川駅"),
    BusRow("11:00", "高校棟 → 金川駅"),
    BusRow("14:00", "金川駅 → 高校棟"),
    BusRow("17:00", "金川駅 → 高校棟"),
    BusRow("20:00", "金川駅 → 高校棟")
)

private val SUNDAY = listOf(
    BusRow("09:00", "高校棟 → 金川駅"),
    BusRow("15:00", "金川駅 → 高校棟"),
    BusRow("19:00", "金川駅 → 高校棟")
)

@Composable
fun BusScreen(navController: NavHostController) {
    val tokens = SuzuT.current

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(
            modifier = Modifier.fillMaxSize().background(tokens.pearl)
                .verticalScroll(rememberScrollState())
        ) {
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
                Text("バス時刻表", color = tokens.ink,
                    style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold))
            }

            // 次回運行 hero
            Column(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp)
                    .clip(RoundedCornerShape(18.dp))
                    .background(tokens.btnGrad)
                    .padding(20.dp)
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(SuzuIcons.Bus, contentDescription = null, tint = Color.White, modifier = Modifier.size(20.dp))
                    Spacer(Modifier.width(8.dp))
                    Text("次回運行", color = Color.White.copy(alpha = 0.9f),
                        style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Medium))
                }
                Spacer(Modifier.height(8.dp))
                Row(verticalAlignment = Alignment.Bottom) {
                    Text("09:20", color = Color.White,
                        style = MonoNumeralStyle.copy(fontSize = 44.sp, lineHeight = 48.sp))
                    Spacer(Modifier.width(10.dp))
                    Text("05/06(水)", color = Color.White.copy(alpha = 0.9f),
                        modifier = Modifier.padding(bottom = 6.dp),
                        style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Medium))
                }
                Spacer(Modifier.height(4.dp))
                Text("高校棟 → 金川駅", color = Color.White,
                    style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold))
            }

            Spacer(Modifier.height(20.dp))

            // 平日
            ScheduleSection("平日", WEEKDAY, tokens)
            Spacer(Modifier.height(16.dp))
            ScheduleSection("土曜", SATURDAY, tokens)
            Spacer(Modifier.height(16.dp))
            ScheduleSection("日曜", SUNDAY, tokens)
            Spacer(Modifier.height(20.dp))
        }
    }
}

@Composable
private fun ScheduleSection(label: String, rows: List<BusRow>, tokens: jp.tomoshibi.android.ui.theme.SuzuTokens) {
    Column(modifier = Modifier.padding(horizontal = 16.dp)) {
        Text(label, color = tokens.inkSub,
            style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Medium))
        Spacer(Modifier.height(8.dp))
        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
            rows.forEach { r ->
                val borderColor = if (r.highlight) tokens.ink else tokens.hair
                Row(
                    modifier = Modifier.fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(tokens.paper)
                        .border(if (r.highlight) 2.dp else 1.dp, borderColor, RoundedCornerShape(12.dp))
                        .padding(horizontal = 14.dp, vertical = 12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(r.time, color = tokens.ink,
                        style = MonoNumeralStyle.copy(fontSize = 16.sp, lineHeight = 20.sp,
                            fontWeight = FontWeight.SemiBold))
                    Spacer(Modifier.width(14.dp))
                    Text(r.route, color = tokens.inkSub,
                        style = TextStyle(fontSize = 13.sp))
                    Spacer(Modifier.weight(1f))
                    if (r.highlight) {
                        Box(
                            modifier = Modifier.clip(RoundedCornerShape(99.dp))
                                .background(tokens.pill)
                                .padding(horizontal = 8.dp, vertical = 2.dp)
                        ) {
                            Text("次回", color = tokens.ink,
                                style = TextStyle(fontSize = 10.sp, fontWeight = FontWeight.Bold))
                        }
                    }
                }
            }
        }
    }
}
