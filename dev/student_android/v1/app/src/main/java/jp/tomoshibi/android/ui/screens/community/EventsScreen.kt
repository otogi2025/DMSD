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
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
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
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.EventOut
import jp.tomoshibi.android.data.network.endpoints.EventsAPI
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.YearMonth
import java.time.ZoneId

// 「カレンダー」屏 — 旧入口仍可达（首页「今週の活動」若仍跳本屏）。
// community G1/G2：任意月份翻页（YearMonth 真实天数/星期）+ 生产版行事行不画箭头、不可点。
// 数据 = EventsAPI.listEvents(from/to)（去年初～明年底），与 ScheduleScreen 对齐。

private fun todayJst(): LocalDate = LocalDate.now(ZoneId.of("Asia/Tokyo"))

private fun fetchRange(today: LocalDate): Pair<String, String> {
    val y = today.year
    return "${y - 1}-01-01" to "${y + 1}-12-31"
}

private val WEEKDAY_JP = listOf("日", "月", "火", "水", "木", "金", "土")

// start_at →「HH:mm」；空 → 空串（对齐 iOS 生产版，不显「終日」）
private fun fmtEventTime(startAt: String?): String {
    if (startAt == null) return ""
    return runCatching { startAt.substring(11, 16) }.getOrDefault("")
}

@Composable
fun EventsScreen(navController: NavHostController) {
    val t = SuzuT.current
    val scope = rememberCoroutineScope()

    var ui by remember { mutableStateOf<LoadState<List<EventOut>>>(LoadState.Loading) }

    suspend fun load() {
        ui = LoadState.Loading
        ui =
            try {
                val today = todayJst()
                val (from, to) = fetchRange(today)
                LoadState.Success(EventsAPI.listEvents(fromDate = from, toDate = to))
            } catch (e: ApiError) {
                LoadState.Failed(e.display)
            } catch (e: Exception) {
                LoadState.Failed("読み込みに失敗しました")
            }
    }
    LaunchedEffect(Unit) { load() }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .background(t.pearl)
                    .verticalScroll(rememberScrollState()),
        ) {
            PageHeader(title = "カレンダー", level = 2, onLeft = { navController.popBackStack() })

            when (val s = ui) {
                LoadState.Loading -> LoadingBox()
                is LoadState.Failed -> FailedBox(s.message, onRetry = { scope.launch { load() } })
                LoadState.Empty -> EventsCalendarBody(events = emptyList())
                is LoadState.Success -> EventsCalendarBody(events = s.value)
            }
        }
    }
}

// 月历主体：任意年月（由行事范围 + 今天月算出），真实天数/月初星期
@Composable
private fun EventsCalendarBody(events: List<EventOut>) {
    val t = SuzuT.current
    val teal = MaterialTheme.colorScheme.primary
    val today = remember { todayJst() }

    val eventDates =
        remember(events) {
            events.mapNotNull { runCatching { LocalDate.parse(it.eventDate) }.getOrNull() }
        }

    val months =
        remember(eventDates, today) {
            val ymList = eventDates.map { YearMonth.from(it) } + YearMonth.from(today)
            val minYm = ymList.min()
            val maxYm = ymList.max()
            val list = mutableListOf<YearMonth>()
            var cur = minYm
            while (!cur.isAfter(maxYm)) {
                list.add(cur)
                cur = cur.plusMonths(1)
            }
            list
        }

    var monthIndex by remember {
        mutableIntStateOf(months.indexOf(YearMonth.from(today)).coerceAtLeast(0))
    }
    val safeMonthIndex = monthIndex.coerceIn(0, months.lastIndex.coerceAtLeast(0))
    val curMonth = months[safeMonthIndex]

    var selectedDay by remember {
        mutableIntStateOf(if (YearMonth.from(today) == curMonth) today.dayOfMonth else 1)
    }
    val selectedDate = curMonth.atDay(selectedDay.coerceIn(1, curMonth.lengthOfMonth()))

    fun eventsForDay(day: Int): List<EventOut> {
        val dateStr = curMonth.atDay(day).toString()
        return events.filter { it.eventDate == dateStr }.sortedBy { it.startAt ?: "" }
    }

    fun changeMonth(delta: Int) {
        val next = safeMonthIndex + delta
        if (next < 0 || next > months.lastIndex) return
        monthIndex = next
        val newMonth = months[next]
        val clamped = selectedDay.coerceIn(1, newMonth.lengthOfMonth())
        selectedDay =
            if (clamped != selectedDay && newMonth == YearMonth.from(today)) {
                today.dayOfMonth
            } else {
                clamped
            }
    }

    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        SuzuCard(padding = 16) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                ArrowButton(
                    icon = SuzuIcons.ChevL,
                    enabled = safeMonthIndex > 0,
                    onClick = { changeMonth(-1) },
                )
                Spacer(Modifier.weight(1f))
                Text(
                    "${curMonth.year} 年 ${curMonth.monthValue} 月",
                    color = t.ink,
                    style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold),
                )
                Spacer(Modifier.weight(1f))
                ArrowButton(
                    icon = SuzuIcons.ChevR,
                    enabled = safeMonthIndex < months.lastIndex,
                    onClick = { changeMonth(1) },
                )
            }

            Spacer(Modifier.height(14.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                WEEKDAY_JP.forEachIndexed { i, label ->
                    Text(
                        label,
                        modifier = Modifier.weight(1f),
                        color =
                            when (i) {
                                0 -> t.danger
                                6 -> teal
                                else -> t.inkMute
                            },
                        textAlign = TextAlign.Center,
                        style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.SemiBold),
                    )
                }
            }

            Spacer(Modifier.height(4.dp))

            val firstWeekday = curMonth.atDay(1).dayOfWeek.value % 7
            val daysInMonth = curMonth.lengthOfMonth()
            val totalCells = firstWeekday + daysInMonth
            val rows = (totalCells + 6) / 7
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                for (rowIdx in 0 until rows) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(4.dp),
                    ) {
                        for (col in 0 until 7) {
                            val cellIndex = rowIdx * 7 + col
                            val day = cellIndex - firstWeekday + 1
                            if (day in 1..daysInMonth) {
                                val cellDate = curMonth.atDay(day)
                                DayCell(
                                    day = day,
                                    isSelected = day == selectedDay,
                                    isToday = cellDate == today,
                                    hasEvent = eventsForDay(day).isNotEmpty(),
                                    teal = teal,
                                    modifier = Modifier.weight(1f),
                                    onClick = { selectedDay = day },
                                )
                            } else {
                                Spacer(Modifier.weight(1f).aspectRatio(1f))
                            }
                        }
                    }
                }
            }
        }

        SelectedDaySection(
            selectedDate = selectedDate,
            events = eventsForDay(selectedDay),
        )
        Spacer(Modifier.height(12.dp))
    }
}

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
    val accent = MaterialTheme.colorScheme.secondary
    Box(
        modifier =
            modifier
                .aspectRatio(1f)
                .clip(RoundedCornerShape(8.dp))
                .then(
                    when {
                        isSelected -> {
                            Modifier.background(teal)
                        }

                        isToday -> {
                            Modifier
                                .background(teal.copy(alpha = 0.12f))
                                .border(1.5.dp, teal, RoundedCornerShape(8.dp))
                        }

                        else -> {
                            Modifier
                        }
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
                color = if (isSelected) Color.White else t.ink,
                style =
                    TextStyle(
                        fontSize = 13.sp,
                        fontFamily = FontFamily.Monospace,
                        fontWeight = if (isSelected || isToday) FontWeight.Bold else FontWeight.Medium,
                    ),
            )
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

@Composable
private fun SelectedDaySection(
    selectedDate: LocalDate,
    events: List<EventOut>,
) {
    val t = SuzuT.current
    val teal = MaterialTheme.colorScheme.primary
    val weekday = WEEKDAY_JP[selectedDate.dayOfWeek.value % 7]

    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(top = 4.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                "${selectedDate.monthValue} 月 ${selectedDate.dayOfMonth} 日",
                color = t.ink,
                style = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.Bold),
            )
            Text(
                "（$weekday）",
                color = t.inkSub,
                style = TextStyle(fontSize = 13.sp),
            )
            Spacer(Modifier.weight(1f))
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
                        "この日の予定はありません",
                        color = t.inkMute,
                        style = TextStyle(fontSize = 12.sp),
                    )
                }
            }
        } else {
            // community G2：生产版不画箭头、不包点击（行内信息已完整）
            events.forEach { ev ->
                EventRow(event = ev, teal = teal)
            }
        }
    }
}

@Composable
private fun EventRow(
    event: EventOut,
    teal: Color,
) {
    val t = SuzuT.current
    SuzuCard(padding = 14) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                fmtEventTime(event.startAt),
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
            }
        }
    }
}
