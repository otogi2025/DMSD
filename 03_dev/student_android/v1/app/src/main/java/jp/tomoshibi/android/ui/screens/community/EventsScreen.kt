package jp.tomoshibi.android.ui.screens.community

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.EventItem
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// 「カレンダー」屏 — 1:1 对齐 iOS EventsView（CommunityStubs.swift 999-1222）。
//   上半：月历卡（4 月 / 5 月 切换头 + 7 列网格，有行事的日子打小圆点）。
//   下半：选中日的行事列表（标题「M 月 D 日（曜日）」+ N 件胶囊 / 空态「予定なし」）。
//   数据 = MockData.DEFAULT_EVENTS（ISO 日期 "2026-04-05"）。点一条行事跳详情。
//   iOS 用 GlassSheet 在本屏没出现，本屏纯页面，无弹窗。

// 演示版「今天」固定 2026-04-23，对齐 iOS EventsView 的 todayMonth=4 / todayDay=23
private const val YEAR = 2026
private const val TODAY_MONTH = 4
private const val TODAY_DAY = 23

// 曜日表头（日 月 火 水 木 金 土）— 周日=索引 0，对齐 iOS weekdayJP
private val WEEKDAY_JP = listOf("日", "月", "火", "水", "木", "金", "土")

@Composable
fun EventsScreen(navController: NavHostController) {
    val t = SuzuT.current

    // 当前显示月份（4 月 / 5 月 两态切换，对齐 iOS selectedMonth）
    var selectedMonth by remember { mutableIntStateOf(TODAY_MONTH) }
    // 当前选中的「日」（1 起，初始今天）—— 对齐 iOS selectedDay
    var selectedDay by remember { mutableIntStateOf(TODAY_DAY) }

    // 当月 1 号是星期几（周日=0）：iOS 写死 4 月=水(3) / 5 月=金(5)
    val firstWeekdayOfMonth = if (selectedMonth == 4) 3 else 5
    // 当月天数：iOS 写死 4 月=30 / 5 月=31
    val daysInMonth = if (selectedMonth == 4) 30 else 31

    // 切月：先改月份，再把已选日 clamp 到新月天数（对齐 iOS switchMonth IX-022 修复，
    //   防 5 月选 31 日切回只有 30 天的 4 月时显示不存在的「4月31日」）
    fun switchMonth(month: Int) {
        selectedMonth = month
        val newDaysInMonth = if (month == 4) 30 else 31
        selectedDay = selectedDay.coerceAtMost(newDaysInMonth)
    }

    // 某天的行事（按 ISO 日期 "YYYY-MM-DD" 过滤）
    fun eventsForDay(day: Int): List<EventItem> {
        val dateStr = "%d-%02d-%02d".format(YEAR, selectedMonth, day)
        return MockData.DEFAULT_EVENTS.filter { it.date == dateStr }
    }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .background(t.pearl)
                    .verticalScroll(rememberScrollState()),
        ) {
            // 标题「カレンダー」抄 iOS PageHeader(title: "カレンダー", level: 2)
            PageHeader(title = "カレンダー", level = 2, onLeft = { navController.popBackStack() })

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp),
            ) {
                CalendarCard(
                    selectedMonth = selectedMonth,
                    selectedDay = selectedDay,
                    firstWeekdayOfMonth = firstWeekdayOfMonth,
                    daysInMonth = daysInMonth,
                    hasEvent = { day -> eventsForDay(day).isNotEmpty() },
                    onPrevMonth = { switchMonth(maxOf(4, selectedMonth - 1)) },
                    onNextMonth = { switchMonth(minOf(5, selectedMonth + 1)) },
                    onSelectDay = { selectedDay = it },
                )
                SelectedDaySection(
                    selectedMonth = selectedMonth,
                    selectedDay = selectedDay,
                    firstWeekdayOfMonth = firstWeekdayOfMonth,
                    events = eventsForDay(selectedDay),
                    onEventClick = { ev -> navController.navigate(Route.EventDetail(ev.id).path) },
                )
                Spacer(Modifier.height(12.dp))
            }
        }
    }
}

// 上半：月历卡 — Card(padding 16)
@Composable
private fun CalendarCard(
    selectedMonth: Int,
    selectedDay: Int,
    firstWeekdayOfMonth: Int,
    daysInMonth: Int,
    hasEvent: (Int) -> Boolean,
    onPrevMonth: () -> Unit,
    onNextMonth: () -> Unit,
    onSelectDay: (Int) -> Unit,
) {
    val t = SuzuT.current
    val teal = MaterialTheme.colorScheme.primary // 主色
    SuzuCard(padding = 16) {
        // 月切换头：左箭头（4 月时禁用）+「YYYY 年 M 月」+ 右箭头（5 月时禁用）
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            ArrowButton(
                icon = SuzuIcons.ChevL,
                enabled = selectedMonth > 4,
                onClick = onPrevMonth,
            )
            Spacer(Modifier.weight(1f))
            // 年份纯字符串拼接，不过数字格式化（否则 2026 → 2,026）
            Text(
                "$YEAR 年 $selectedMonth 月",
                color = t.ink,
                style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold),
            )
            Spacer(Modifier.weight(1f))
            ArrowButton(
                icon = SuzuIcons.ChevR,
                enabled = selectedMonth < 5,
                onClick = onNextMonth,
            )
        }

        Spacer(Modifier.height(14.dp))

        // 曜日表头 7 列（统一弱字色，对齐 iOS T.inkMute）
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            WEEKDAY_JP.forEach { label ->
                Text(
                    label,
                    modifier = Modifier.weight(1f),
                    color = t.inkMute,
                    textAlign = TextAlign.Center,
                    style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.SemiBold),
                )
            }
        }

        Spacer(Modifier.height(4.dp))

        // 7 列网格：月初前空白格（firstWeekdayOfMonth 个）+ 当月各天
        val totalCells = firstWeekdayOfMonth + daysInMonth
        val rows = (totalCells + 6) / 7 // 向上取整成完整周行数
        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
            for (rowIdx in 0 until rows) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                ) {
                    for (col in 0 until 7) {
                        val cellIndex = rowIdx * 7 + col
                        val day = cellIndex - firstWeekdayOfMonth + 1
                        if (day in 1..daysInMonth) {
                            DayCell(
                                day = day,
                                isSelected = day == selectedDay,
                                isToday = selectedMonth == TODAY_MONTH && day == TODAY_DAY,
                                hasEvent = hasEvent(day),
                                teal = teal,
                                modifier = Modifier.weight(1f),
                                onClick = { onSelectDay(day) },
                            )
                        } else {
                            // 月初空白格
                            Spacer(Modifier.weight(1f).aspectRatio(1f))
                        }
                    }
                }
            }
        }
    }
}

// 月切换箭头按钮 — 36 圆，禁用时变弱字色不可点（对齐 iOS chevR + disabled）
@Composable
private fun ArrowButton(
    icon: ImageVector,
    enabled: Boolean,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Box(
        modifier =
            Modifier
                .size(32.dp)
                .clip(RoundedCornerShape(percent = 50))
                .clickable(enabled = enabled, onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Icon(
            icon,
            contentDescription = null,
            tint = if (enabled) t.ink else t.inkMute,
            modifier = Modifier.size(16.dp),
        )
    }
}

// 单日格子 — 正方形：
//   选中 = 主色实心 + 白字加粗；今天（非选中）= 浅主色底 + 主色描边；
//   有行事且非选中 = 底部画 1 个强调色小圆点（对齐 iOS T.accent = colorScheme.secondary）
@Composable
private fun DayCell(
    day: Int,
    isSelected: Boolean,
    isToday: Boolean,
    hasEvent: Boolean,
    teal: Color,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val accent = MaterialTheme.colorScheme.secondary // 圆点用强调色，对齐 iOS T.accent
    Box(
        modifier =
            modifier
                .aspectRatio(1f)
                .clip(RoundedCornerShape(8.dp))
                .then(
                    when {
                        isSelected -> Modifier.background(teal)
                        isToday -> Modifier.background(teal.copy(alpha = 0.12f)).border(1.5.dp, teal, RoundedCornerShape(8.dp))
                        else -> Modifier
                    },
                ).clickable(onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            Text(
                "$day",
                color =
                    when {
                        isSelected -> Color.White
                        else -> t.ink
                    },
                style =
                    TextStyle(
                        fontSize = 13.sp,
                        fontFamily = FontFamily.Monospace, // 数字等宽
                        fontWeight = if (isSelected || isToday) FontWeight.Bold else FontWeight.Medium,
                    ),
            )
            // 有行事且非选中才画小圆点（选中态底已是主色，画点没意义）
            if (hasEvent && !isSelected) {
                Spacer(Modifier.height(2.dp))
                Box(
                    modifier =
                        Modifier
                            .size(4.dp)
                            .clip(RoundedCornerShape(percent = 50))
                            .background(accent),
                )
            }
        }
    }
}

// 下半：选中日的行事区
//   标题「M 月 D 日（曜日）」+ 右「N 件」胶囊（>0 才画）；空态「予定なし」卡。
@Composable
private fun SelectedDaySection(
    selectedMonth: Int,
    selectedDay: Int,
    firstWeekdayOfMonth: Int,
    events: List<EventItem>,
    onEventClick: (EventItem) -> Unit,
) {
    val t = SuzuT.current
    val teal = MaterialTheme.colorScheme.primary // 主色
    // 选中日的曜日索引（周日=0）：iOS (firstWeekdayOfMonth + selectedDay - 1) % 7
    val weekday = (firstWeekdayOfMonth + selectedDay - 1) % 7

    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        // 标题行
        Row(
            modifier = Modifier.fillMaxWidth().padding(top = 4.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                "$selectedMonth 月 $selectedDay 日",
                color = t.ink,
                style = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.Bold),
            )
            Text(
                "（${WEEKDAY_JP[weekday]}）",
                color = t.inkSub,
                style = TextStyle(fontSize = 13.sp),
            )
            Spacer(Modifier.weight(1f))
            // 行事数 > 0 才画「N 件」小胶囊（主色字 + 主色 0.1 底，对齐 iOS）
            if (events.isNotEmpty()) {
                Box(
                    modifier =
                        Modifier
                            .clip(RoundedCornerShape(percent = 50))
                            .background(teal.copy(alpha = 0.1f))
                            .padding(horizontal = 8.dp, vertical = 3.dp),
                ) {
                    Text(
                        "${events.size} 件",
                        color = teal,
                        style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold),
                    )
                }
            }
        }

        if (events.isEmpty()) {
            // 空态卡：Cal 图标 +「予定なし」+「この日の活動はありません」
            SuzuCard(padding = 24) {
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Icon(
                        SuzuIcons.Cal,
                        contentDescription = null,
                        tint = t.inkMute,
                        modifier = Modifier.size(36.dp),
                    )
                    Text(
                        "予定なし",
                        color = t.inkSub,
                        style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
                    )
                    Text(
                        "この日の活動はありません",
                        color = t.inkMute,
                        style = TextStyle(fontSize = 12.sp),
                    )
                }
            }
        } else {
            events.forEach { ev ->
                EventRow(
                    event = ev,
                    teal = teal,
                    onClick = { onEventClick(ev) },
                )
            }
        }
    }
}

// 行事一条 — Card(padding 14)：左 56 宽时刻（主色等宽）+ 1dp 竖分隔 + 标题加粗 +「📍 场所」+ 右 ChevR
@Composable
private fun EventRow(
    event: EventItem,
    teal: Color,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Box(modifier = Modifier.clickable(onClick = onClick)) {
        SuzuCard(padding = 14) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                // 左 56 宽时刻（主色等宽）
                Text(
                    event.time,
                    modifier = Modifier.width(56.dp),
                    color = teal,
                    textAlign = TextAlign.Center,
                    style =
                        TextStyle(
                            fontSize = 13.sp,
                            fontFamily = FontFamily.Monospace,
                            fontWeight = FontWeight.Bold,
                        ),
                )
                // 1dp 竖分隔
                Box(
                    modifier =
                        Modifier
                            .width(1.dp)
                            .height(38.dp)
                            .background(t.hair),
                )
                Spacer(Modifier.width(12.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        event.title,
                        color = t.ink,
                        style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                    )
                    Spacer(Modifier.height(3.dp))
                    // 「📍 场所」一行（对齐 iOS 📍 + e.place）
                    Text(
                        "📍 ${event.place}",
                        color = t.inkSub,
                        style = TextStyle(fontSize = 12.sp),
                    )
                }
                Spacer(Modifier.width(8.dp))
                Icon(
                    SuzuIcons.ChevR,
                    contentDescription = null,
                    tint = t.inkMute,
                    modifier = Modifier.size(14.dp),
                )
            }
        }
    }
}
