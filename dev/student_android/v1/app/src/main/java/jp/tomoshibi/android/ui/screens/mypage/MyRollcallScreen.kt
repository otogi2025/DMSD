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
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
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
import jp.tomoshibi.android.data.model.RollcallEntry
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// ───────────────────────────────────────────────────────────────
// 点呼履歴（点呼出席履历）+ 点呼セッション詳細（单次点呼详情）
// 对齐 iOS MyRollcallView / MyRollcallDetailView（对齐规格 §4 / §5）
// 数据全部来自 MockData.DEFAULT_ROLLCALL，无网络层
// ───────────────────────────────────────────────────────────────

// 状态 → Pill 色调：時間内=绿 / 遅刻=橙 / 欠席=红
private fun toneOf(status: String): PillTone =
    when (status) {
        "遅刻" -> PillTone.Warn
        "欠席" -> PillTone.Danger
        else -> PillTone.Ok
    }

// ───────────────────────────────────────────────────────────────
// §4 点呼履歴（L2）
// ───────────────────────────────────────────────────────────────
@Composable
fun MyRollcallScreen(navController: NavHostController) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme

    // 月份筛选胶囊（默认选 4 月）
    val months = listOf("4月", "3月", "2月")
    var selectedMonth by remember { mutableStateOf("4月") }

    // 把「4月」转成日期前缀「2026-04」用来过滤
    val monthPrefix =
        when (selectedMonth) {
            "4月" -> "2026-04"
            "3月" -> "2026-03"
            else -> "2026-02"
        }
    val filtered = MockData.DEFAULT_ROLLCALL.filter { it.date.startsWith(monthPrefix) }

    // 按日期分组（保持原顺序），每组内同时含「朝点呼 / 晩点呼」两条
    val grouped = filtered.groupBy { it.date }.toList()

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
                // 月份筛选胶囊横排
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    months.forEach { m ->
                        val active = m == selectedMonth
                        Box(
                            modifier =
                                Modifier
                                    .clip(RoundedCornerShape(percent = 50))
                                    .background(if (active) cs.primary else t.pill)
                                    .clickable { selectedMonth = m }
                                    .padding(horizontal = 14.dp, vertical = 6.dp),
                        ) {
                            Text(
                                m,
                                color = if (active) Color.White else cs.primary,
                                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
                            )
                        }
                    }
                }

                Spacer(Modifier.height(16.dp))

                // 按日期分组列表：每组 = 日期小标题 + 卡内若干行
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
                            // 行间细分隔线（最后一行不画）
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
                    Spacer(Modifier.height(16.dp))
                }

                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

// 履历单行：场次（60 宽）+ 状态 Pill + 方式 + 右箭头
@Composable
private fun RollcallRow(
    entry: RollcallEntry,
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
        // 场次：朝点呼 / 晩点呼
        Text(
            entry.session,
            color = t.ink,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
            modifier = Modifier.width(60.dp),
        )
        Spacer(Modifier.width(8.dp))
        // 状态 Pill
        Pill(text = entry.status, tone = toneOf(entry.status))
        Spacer(Modifier.weight(1f))
        // 方式（NFC / ―）
        Text(
            entry.method,
            color = t.inkMute,
            style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
        )
        Spacer(Modifier.width(8.dp))
        // 右箭头
        Icon(
            SuzuIcons.ChevR,
            contentDescription = null,
            tint = t.inkFaint,
            modifier = Modifier.width(18.dp),
        )
    }
}

// ───────────────────────────────────────────────────────────────
// §5 点呼セッション詳細（L2）
// ───────────────────────────────────────────────────────────────
@Composable
fun MyRollcallDetailScreen(
    navController: NavHostController,
    id: String,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme

    // 按 id 取那条；取不到给个兜底（防崩）
    val entry =
        MockData.DEFAULT_ROLLCALL.find { it.id == id }
            ?: RollcallEntry(id, "―", "―", "―", "―")

    // 朝场 / 晩场 → 开始 / 截止时刻
    val isMorning = entry.session == "朝点呼"
    val startTime = if (isMorning) "07:00:00" else "21:00:00"
    val deadlineTime = if (isMorning) "07:10:00" else "21:10:00"
    // 遅刻演示用的チェックイン时刻（朝 07:12:34 / 晩 21:12:34）
    val checkinTime = if (isMorning) "07:12:34" else "21:12:34"

    // 状態文字：遅刻→扣 0.5 点 / 欠席→扣 1.0 点 / 時間内→無扣分
    val statusText =
        when (entry.status) {
            "遅刻" -> "遅刻 0.5 点"
            "欠席" -> "欠席 1.0 点"
            "時間内" -> "時間内"
            else -> entry.status
        }
    val isLate = entry.status == "遅刻"

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
                // 主卡
                Column(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(18.dp))
                            .background(t.paper)
                            .padding(18.dp),
                ) {
                    // 标题「{date} {场次}」
                    Text(
                        "${entry.date} ${entry.session}",
                        color = cs.primary,
                        style =
                            TextStyle(
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold,
                                fontFamily = FontFamily.Monospace,
                            ),
                    )
                    Spacer(Modifier.height(4.dp))
                    // セッション ID（id 本身就是 RC-纯数字日期-AM/PM 格式）
                    Text(
                        "セッション ID: ${entry.id}",
                        color = t.inkMute,
                        style = TextStyle(fontSize = 12.sp, fontFamily = FontFamily.Monospace),
                    )

                    Spacer(Modifier.height(16.dp))

                    // 键值行：状態 / 方式 / 開始時刻 / 締切時刻（遅刻多两项）
                    KvRow("状態", statusText)
                    KvRow("方式", entry.method)
                    KvRow("開始時刻", startTime)
                    KvRow("締切時刻", deadlineTime)
                    if (isLate) {
                        KvRow("チェックイン", checkinTime)
                        KvRow("遅れ", "+2分34秒")
                    }
                }

                // info box：青绿 4% 底 + 「改判はされていません」
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
                    Spacer(Modifier.width(8.dp))
                    Text(
                        "改判はされていません",
                        color = t.inkSub,
                        style = TextStyle(fontSize = 12.sp),
                    )
                }

                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

// 键值行：左标签 inkSub / 右值 ink
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
