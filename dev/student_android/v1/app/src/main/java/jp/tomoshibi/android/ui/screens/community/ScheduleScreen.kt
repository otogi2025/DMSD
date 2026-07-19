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
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.YearMonth
import java.time.ZoneId

// 行事予定（カレンダー）— 对齐 iOS ScheduleView：
//   月历卡（月切换头 + 7 列网格）+ 选中日详情。已接真后端 EventsAPI.listEvents(from/to)。
//   后端 DTO 是 EventOut（id/title/category/event_date/start_at/...），按含义映射到日历显示项。
//
// ★ 接后端三态：外层包 LoadState（加载中 / 失败 / 成功）。
//   成功态即使 0 条也持续显示日历本体（对齐 iOS；空态落在选中日「予定なし」卡上）。
//   失败必走 FailedBox，绝不退化成空日历。

// 生产版「今天」= 东京时区真实当天（对齐 iOS #else 分支；Android 无 DEMO 编译开关）
private fun todayJst(): LocalDate = LocalDate.now(ZoneId.of("Asia/Tokyo"))

// 一次取够的日期范围：去年 1/1 ～ 明年 12/31（对齐 iOS fetchRange）
private fun fetchRange(today: LocalDate): Pair<String, String> {
    val y = today.year
    return "${y - 1}-01-01" to "${y + 1}-12-31"
}

// 曜日表头（日 月 火 水 木 金 土）— 周日=索引 0，对齐 iOS Calendar.weekday-1
private val WEEKDAY_LABELS = listOf("日", "月", "火", "水", "木", "金", "土")

@Composable
fun ScheduleScreen(navController: NavHostController) {
    val t = SuzuT.current
    val scope = rememberCoroutineScope()
    // 三态：Loading / Failed(消息) / Success(后端 EventOut 列表，可为空)
    // 不再用 LoadState.Empty —— 0 条也走 Success，日历持续显示（G7）
    var ui by remember { mutableStateOf<LoadState<List<EventOut>>>(LoadState.Loading) }

    // 加载函数（重试也调它）。失败必须落 Failed，绝不退化成假数据。
    suspend fun load() {
        ui = LoadState.Loading
        ui =
            try {
                val today = todayJst()
                val (from, to) = fetchRange(today)
                val items = EventsAPI.listEvents(fromDate = from, toDate = to)
                LoadState.Success(items)
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
            PageHeader(title = "行事予定", level = 2, onLeft = { navController.popBackStack() })

            // 三态渲染（header 永远在，下面这块随状态切换）
            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox()
                }

                is LoadState.Failed -> {
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }

                // Empty 理论上不再出现；若旧路径残留，按成功空列表处理
                LoadState.Empty -> {
                    CalendarBody(events = emptyList())
                }

                is LoadState.Success -> {
                    CalendarBody(events = s.value)
                }
            }
        }
    }
}

// 日历主体 —— 拿到后端行事列表后才渲染（月切换 + 网格 + 选中日详情）。
// 月份 / 选中日 state 全在这里 remember；0 条时范围仅含今天所在月，仍可看月历。
@Composable
private fun CalendarBody(events: List<EventOut>) {
    val t = SuzuT.current
    val teal = MaterialTheme.colorScheme.primary // 主色
    val accent = MaterialTheme.colorScheme.secondary // 圆点用强调色
    val today = remember { todayJst() }

    // 全部行事按日期解析成 LocalDate（后端 event_date 是 ISO "2026-04-05"，直接 parse）
    val eventDates = remember(events) { events.mapNotNull { runCatching { LocalDate.parse(it.eventDate) }.getOrNull() } }

    // 月份范围 = 最早行事月 ~ 最晚行事月，且强制含「今天」所在月；无行事时仅今天月
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

    // 当前显示的月份索引 —— 初始停在「今天」所在月
    var monthIndex by remember {
        mutableIntStateOf(months.indexOf(YearMonth.from(today)).coerceAtLeast(0))
    }
    val safeMonthIndex = monthIndex.coerceIn(0, months.lastIndex.coerceAtLeast(0))
    val curMonth = months[safeMonthIndex]

    // 当前选中的「日」（1 起）—— 初始选今天那一天（若不在当前月则选 1 号）
    var selectedDay by remember {
        mutableIntStateOf(if (YearMonth.from(today) == curMonth) today.dayOfMonth else 1)
    }
    val selectedDate = curMonth.atDay(selectedDay.coerceIn(1, curMonth.lengthOfMonth()))

    // 当天行事（按 selectedDate 过滤，后端 event_date 解析比对）
    val dayEvents = events.filter { it.eventDate == selectedDate.toString() }

    // 当月事件数（汇总行用）
    val eventsInMonth =
        eventDates.count { YearMonth.from(it) == curMonth }

    // 切月：边界禁用 + 切完把选中日 clamp 到新月天数（防 5/31 切到没有 31 号的月）
    fun changeMonth(delta: Int) {
        val next = safeMonthIndex + delta
        if (next < 0 || next > months.lastIndex) return
        monthIndex = next
        val newMonth = months[next]
        val clamped = selectedDay.coerceIn(1, newMonth.lengthOfMonth())
        // 对齐 iOS：仅当原选中日被夹掉、且目标月是今天所在月时，复位到今天
        selectedDay =
            if (clamped != selectedDay && newMonth == YearMonth.from(today)) {
                today.dayOfMonth
            } else {
                clamped
            }
    }

    // ── 日历卡 ──
    Box(modifier = Modifier.padding(horizontal = 16.dp)) {
        SuzuCard(padding = 16) {
            // 月切换头：左右箭头 +「YYYY 年 M 月」（纯字符串拼接，不过 NumberFormat）
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
                // 年份纯字符串拼接，绝不能过 NumberFormat 否则变 2,026
                Text(
                    "${curMonth.year} 年 ${curMonth.monthValue} 月",
                    color = t.ink,
                    style = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.Bold),
                )
                Spacer(Modifier.weight(1f))
                ArrowButton(
                    icon = SuzuIcons.ChevR,
                    enabled = safeMonthIndex < months.lastIndex,
                    onClick = { changeMonth(1) },
                )
            }

            Spacer(Modifier.height(14.dp))

            // 曜日表头 7 列（日=红 / 土=主色 / 其余弱字）
            Row(modifier = Modifier.fillMaxWidth()) {
                WEEKDAY_LABELS.forEachIndexed { i, label ->
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
                        style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
                    )
                }
            }

            Spacer(Modifier.height(6.dp))

            // 7 列网格：月初前空白格（firstWeekday 个）+ 当月各天
            // 周日=0 索引：java.time getDayOfWeek 周一=1…周日=7，转成周日=0 用 % 7
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
                                val dotCount = eventDates.count { it == cellDate }.coerceAtMost(3)
                                DayCell(
                                    day = day,
                                    isSelected = day == selectedDay,
                                    isToday = cellDate == today,
                                    dotCount = dotCount,
                                    teal = teal,
                                    accent = accent,
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

            // 当月事件数汇总行（仅 >0 时显示）— 对齐 iOS「○月：N件の予定」
            if (eventsInMonth > 0) {
                Spacer(Modifier.height(10.dp))
                Text(
                    "${curMonth.monthValue}月：${eventsInMonth}件の予定",
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp),
                )
            }
        }
    }

    Spacer(Modifier.height(16.dp))

    // ── 选中日详情 ──
    // 标题拆两段：「M 月 D 日」(18 heavy) +「（曜日）」(13 inkSub)；「N 件」仅有行事时显示
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(
            "${selectedDate.monthValue} 月 ${selectedDate.dayOfMonth} 日",
            color = t.ink,
            style = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.Black),
        )
        Text(
            "（${WEEKDAY_LABELS[selectedDate.dayOfWeek.value % 7]}）",
            color = t.inkSub,
            style = TextStyle(fontSize = 13.sp),
        )
        Spacer(Modifier.weight(1f))
        if (dayEvents.isNotEmpty()) {
            Pill("${dayEvents.size} 件", tone = PillTone.Accent)
        }
    }

    Spacer(Modifier.height(10.dp))

    Column(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        if (dayEvents.isEmpty()) {
            // 无事件空态：Cal 图标 +「予定なし」+「この日の予定はありません」
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
            // 生产版：已登录拉真数据 → 不画 chevron、不可点（对齐 iOS showChevron:false）
            dayEvents.forEach { ev ->
                EventRow(event = ev, teal = teal)
            }
        }
        Spacer(Modifier.height(20.dp))
    }
}

// 月切换箭头按钮（36 圆 + 禁用时变弱字色不可点）
@Composable
private fun ArrowButton(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    enabled: Boolean,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Box(
        modifier =
            Modifier
                .size(36.dp)
                .clip(RoundedCornerShape(percent = 50))
                .background(t.pearl)
                .clickable(enabled = enabled, onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Icon(
            icon,
            contentDescription = null,
            tint = if (enabled) t.ink else t.inkFaint,
            modifier = Modifier.size(20.dp),
        )
    }
}

// 单日格子 — 正方形：
//   选中 = 主色实心 + 白字加粗；今天（非选中）= 浅主色底 + 主色描边；
//   有行事且非选中 = 底部画 1~3 个强调色小圆点（按当天事件数）
@Composable
private fun DayCell(
    day: Int,
    isSelected: Boolean,
    isToday: Boolean,
    dotCount: Int,
    teal: Color,
    accent: Color,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Box(
        modifier =
            modifier
                .aspectRatio(1f)
                .clip(RoundedCornerShape(10.dp))
                .then(
                    when {
                        isSelected -> {
                            Modifier.background(teal)
                        }

                        isToday -> {
                            Modifier
                                .background(teal.copy(alpha = 0.12f))
                                .border(1.5.dp, teal, RoundedCornerShape(10.dp))
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
                color =
                    when {
                        isSelected -> Color.White
                        isToday -> teal
                        else -> t.ink
                    },
                style =
                    TextStyle(
                        fontSize = 14.sp,
                        fontFamily = FontFamily.Monospace,
                        fontWeight = if (isSelected || isToday) FontWeight.Bold else FontWeight.Normal,
                    ),
            )
            if (dotCount > 0 && !isSelected) {
                Spacer(Modifier.height(2.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(2.dp)) {
                    repeat(dotCount) {
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
    }
}

// 行事一条 — Card(padding 14)：左 56 宽时刻（主色等宽，可空）+ 1dp 竖分隔 + 标题。
// 生产版：place 恒空不显副行；不画 chevron、整行不可点（对齐 iOS EventMapper + eventRow）。
@Composable
private fun EventRow(
    event: EventOut,
    teal: Color,
) {
    val t = SuzuT.current
    SuzuCard(padding = 14) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            // 左 56 宽时刻。start_at 为空 → 空白（不对齐「終日」占位）
            Text(
                fmtTime(event.startAt),
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
                    style = TextStyle(fontSize = 14.5.sp, fontWeight = FontWeight.Bold),
                )
            }
        }
    }
}

// 后端 start_at（"2026-04-23T08:30:00+09:00"）→「HH:mm」；null / 解析失败 → 空串（对齐 iOS）
private fun fmtTime(startAt: String?): String {
    if (startAt == null) return ""
    return runCatching { startAt.substring(11, 16) }.getOrDefault("")
}
