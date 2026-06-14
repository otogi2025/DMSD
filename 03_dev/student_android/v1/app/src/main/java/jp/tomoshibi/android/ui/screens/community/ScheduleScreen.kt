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
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.EmptyState
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

// 行事予定（カレンダー）— 对齐 iOS ScheduleView：
//   月历卡（月切换头 + 7 列网格）+ 选中日详情。已接真后端 EventsAPI.listEvents()（spec §7.5，GET /api/v1/events）。
//   后端 DTO 是 EventOut（id/title/category/event_date/start_at/...），按含义映射到日历显示项。
//
// ★ 接后端三态：外层包 LoadState（加载中 / 失败 / 空 / 成功），日历的月份/选中日状态在 Success 分支内根据真数据算。
//   失败必走 FailedBox，绝不退化成空日历（否则学生会误以为「这段时间没有任何行事」）。

// 演示版「今天」固定值 — 对齐 iOS DEMO 构建 2026-04-23。
// 仅用于日历高亮「今天」格 + 初始停在今天所在月，跟数据来源无关，故保留固定值。
private val TODAY = LocalDate.parse("2026-04-23")

// 曜日表头（日 月 火 水 木 金 土）— 周日=索引 0，对齐 iOS Calendar.weekday-1
private val WEEKDAY_LABELS = listOf("日", "月", "火", "水", "木", "金", "土")

@Composable
fun ScheduleScreen(navController: NavHostController) {
    val t = SuzuT.current
    val scope = rememberCoroutineScope()
    // 三态：Loading / Failed(消息) / Empty / Success(后端 EventOut 列表)
    var ui by remember { mutableStateOf<LoadState<List<EventOut>>>(LoadState.Loading) }

    // 加载函数（重试也调它）。失败必须落 Failed，绝不退化成空列表 / 空日历。
    // 不传 from_date / to_date = 后端返回全部行事（跟原 MockData 全量行为一致）。
    suspend fun load() {
        ui = LoadState.Loading
        ui =
            try {
                val items = EventsAPI.listEvents()
                if (items.isEmpty()) LoadState.Empty else LoadState.Success(items)
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

                // 空态 —— 日历图标 SuzuIcons.Cal
                LoadState.Empty -> {
                    EmptyState(title = "行事予定はありません", icon = SuzuIcons.Cal)
                }

                is LoadState.Success -> {
                    CalendarBody(navController = navController, events = s.value)
                }
            }
        }
    }
}

// 日历主体 —— 拿到后端行事列表后才渲染（月切换 + 网格 + 选中日详情）。
// 月份 / 选中日 state 全在这里 remember，依赖真数据 events 计算。
@Composable
private fun CalendarBody(
    navController: NavHostController,
    events: List<EventOut>,
) {
    val t = SuzuT.current
    val teal = MaterialTheme.colorScheme.primary // 主色
    val accent = MaterialTheme.colorScheme.secondary // 圆点用强调色

    // 全部行事按日期解析成 LocalDate（后端 event_date 是 ISO "2026-04-05"，直接 parse）
    val eventDates = remember(events) { events.map { LocalDate.parse(it.eventDate) } }

    // 月份范围 = 最早行事月 ~ 最晚行事月，且强制含「今天」所在月
    val months =
        remember(eventDates) {
            val ymList = eventDates.map { YearMonth.from(it) } + YearMonth.from(TODAY)
            val minYm = ymList.min()
            val maxYm = ymList.max()
            // 从最早到最晚逐月列出，做切月边界判断
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
        mutableIntStateOf(months.indexOf(YearMonth.from(TODAY)).coerceAtLeast(0))
    }
    val curMonth = months[monthIndex]

    // 当前选中的「日」（1 起）—— 初始选今天那一天（若不在当前月则选 1 号）
    var selectedDay by remember {
        mutableIntStateOf(if (YearMonth.from(TODAY) == curMonth) TODAY.dayOfMonth else 1)
    }
    val selectedDate = curMonth.atDay(selectedDay.coerceIn(1, curMonth.lengthOfMonth()))

    // 当天行事（按 selectedDate 过滤，后端 event_date 解析比对）
    val dayEvents = events.filter { LocalDate.parse(it.eventDate) == selectedDate }

    // 切月：边界禁用 + 切完把选中日 clamp 到新月天数（防 5/31 切到没有 31 号的月）
    fun changeMonth(delta: Int) {
        val next = monthIndex + delta
        if (next < 0 || next > months.lastIndex) return
        monthIndex = next
        val newMonth = months[next]
        selectedDay = selectedDay.coerceIn(1, newMonth.lengthOfMonth())
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
                    enabled = monthIndex > 0,
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
                    enabled = monthIndex < months.lastIndex,
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

                                // 日
                                6 -> teal

                                // 土
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
            val rows = (totalCells + 6) / 7 // 向上取整成完整周行数

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
                                // 当天行事数（最多画 3 个圆点）
                                val dotCount =
                                    eventDates.count { it == cellDate }.coerceAtMost(3)
                                DayCell(
                                    day = day,
                                    isSelected = day == selectedDay,
                                    isToday = cellDate == TODAY,
                                    dotCount = dotCount,
                                    teal = teal,
                                    accent = accent,
                                    modifier = Modifier.weight(1f),
                                    onClick = { selectedDay = day },
                                )
                            } else {
                                // 月初/月末空白格
                                Spacer(Modifier.weight(1f).aspectRatio(1f))
                            }
                        }
                    }
                }
            }
        }
    }

    Spacer(Modifier.height(16.dp))

    // ── 选中日详情 ──
    // 标题「M 月 D 日（曜日）」+ 右「N 件」胶囊
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            "${selectedDate.monthValue} 月 ${selectedDate.dayOfMonth} 日（${WEEKDAY_LABELS[selectedDate.dayOfWeek.value % 7]}）",
            color = t.ink,
            style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold),
        )
        Spacer(Modifier.weight(1f))
        Pill("${dayEvents.size} 件", tone = PillTone.Accent)
    }

    Spacer(Modifier.height(10.dp))

    Column(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        if (dayEvents.isEmpty()) {
            // 无事件空态：Cal 图标 +「予定なし」+「この日の活動はありません」
            SuzuCard(padding = 14) {
                Column(
                    modifier = Modifier.fillMaxWidth().padding(vertical = 16.dp),
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
            dayEvents.forEach { ev ->
                EventRow(
                    event = ev,
                    teal = teal,
                    // TODO 接后端：EventOut.id 是 String(UUID) 但 EventDetail 路由是 Int 且详情屏仍读 MockData，
                    // toIntOrNull 失败会传 0、导航到错误详情，故暂禁用点击（对齐 EventsScreen），等详情屏接后端 + 路由改 String 再恢复。
                    onClick = { },
                )
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
                        isSelected -> Modifier.background(teal)
                        isToday -> Modifier.background(t.pill).border(1.dp, teal, RoundedCornerShape(10.dp))
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
                        isToday -> teal
                        else -> t.ink
                    },
                style =
                    TextStyle(
                        fontSize = 14.sp,
                        fontFamily = FontFamily.Monospace, // 数字等宽
                        fontWeight = if (isSelected || isToday) FontWeight.Bold else FontWeight.Normal,
                    ),
            )
            // 圆点行：有行事且非选中才画（选中态底已是主色，画点没意义）
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

// 行事一条 — Card(padding 14)：左 56 宽时刻（主色等宽）+ 1dp 竖分隔 + 标题加粗 +「カテゴリ」+ 右 ChevR
// 后端 EventOut 字段映射：start_at（带时分时区，可空）→ 左侧时刻；title → 标题；
//   原 EventItem.place（场所）后端 DTO 无对应字段 → 改用 category（行事区分，取值「学校行事」「寮行事」「外部」「その他」之一）填副行。
@Composable
private fun EventRow(
    event: EventOut,
    teal: Color,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Box(modifier = Modifier.clickable(onClick = onClick)) {
        SuzuCard(padding = 14) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                // 左 56 宽时刻（主色等宽）。后端 start_at 是带时分时区的 datetime 字符串，可空。
                // 截 "HH:mm" 显示；为 null（全天行事，无开始时刻）显「終日」。
                Text(
                    fmtTime(event.startAt),
                    modifier = Modifier.width(56.dp),
                    color = teal,
                    textAlign = TextAlign.Center,
                    style =
                        TextStyle(
                            fontSize = 15.sp,
                            fontFamily = FontFamily.Monospace,
                            fontWeight = FontWeight.SemiBold,
                        ),
                )
                // 1dp 竖分隔
                Box(
                    modifier =
                        Modifier
                            .width(1.dp)
                            .height(36.dp)
                            .background(t.hair),
                )
                Spacer(Modifier.width(12.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        event.title,
                        color = t.ink,
                        style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                    )
                    // 区分（category）非空才画，对应原 place 副行位置
                    if (event.category.isNotEmpty()) {
                        Spacer(Modifier.height(3.dp))
                        Text(
                            "📍 ${event.category}",
                            color = t.inkSub,
                            style = TextStyle(fontSize = 12.sp),
                        )
                    }
                }
                Spacer(Modifier.width(8.dp))
                Icon(
                    SuzuIcons.ChevR,
                    contentDescription = null,
                    tint = t.inkFaint,
                    modifier = Modifier.size(18.dp),
                )
            }
        }
    }
}

// 后端 start_at（"2026-04-23T08:30:00+09:00" 这类带时分时区的 datetime 字符串）→ 取「HH:mm」。
// 为 null = 无开始时刻的全天行事，显「終日」。解析失败（格式异常 / 串太短）也回退「終日」，避免崩溃。
private fun fmtTime(startAt: String?): String {
    if (startAt == null) return "終日"
    return runCatching { startAt.substring(11, 16) }.getOrDefault("終日")
}
