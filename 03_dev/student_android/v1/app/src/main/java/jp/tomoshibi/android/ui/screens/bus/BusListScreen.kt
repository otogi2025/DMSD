package jp.tomoshibi.android.ui.screens.bus

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
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
import jp.tomoshibi.android.data.model.SpecialBusRoute
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.TToggle
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter

// 特別運航便一覧 — 対齐 iOS BusListView：
//   PageHeader「特別運航便」level 2 + 空港案内 banner + 3 胶囊筛选 tab + 空港のみ开关 + 日别分组列表
//   「次便」高亮在「筛选后可见列表」里临场算（不在数据里写死），切筛选不会错位
@Composable
fun BusListScreen(navController: NavHostController) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme

    // 筛选 tab：all=すべて / dorm=特別便 / commute=通学便（本地 state）
    var filter by remember { mutableStateOf("all") }
    // 「空港送迎便のみ」开关
    var airportOnly by remember { mutableStateOf(false) }

    // 先按筛选条件过滤出可见列表
    val visible =
        MockData.DEFAULT_BUS_ROUTES.filter { route ->
            val passKind =
                when (filter) {
                    "dorm" -> route.kind == "特別便"
                    "commute" -> route.kind == "通学便"
                    else -> true
                }
            val passAirport = !airportOnly || route.isAirport
            passKind && passAirport
        }

    // 「次便」判定：日本时区当前时刻拼成 "yyyy-MM-dd HH:mm"，
    // 在可见列表里取第一个「现在 <= 便发车时刻」的便 id
    val now =
        LocalDateTime
            .now(ZoneId.of("Asia/Tokyo"))
            .format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm"))
    val nextId = visible.firstOrNull { now <= "${it.date} ${it.time}" }?.id

    // 按日期分组，组 key 升序排列
    val groups = visible.groupBy { it.date }.toSortedMap()

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "特別運航便", level = 2, onLeft = { navController.popBackStack() })

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Spacer(Modifier.height(4.dp))

                // 空港送迎案内 banner — 浅药丸底圆角卡，左「✈」+ 右两行
                Row(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(16.dp))
                            .background(t.pill)
                            .padding(14.dp),
                    verticalAlignment = Alignment.Top,
                ) {
                    Text("✈", style = TextStyle(fontSize = 24.sp))
                    Spacer(Modifier.width(12.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            "空港送迎便について",
                            color = t.ink,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                        )
                        Spacer(Modifier.height(3.dp))
                        Text(
                            "帰国届を出す場合は、空港便にチェックを入れて選択してください。",
                            color = t.inkSub,
                            style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp),
                        )
                    }
                }

                // 筛选区第一行：3 颗胶囊 tab
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    FilterPill("すべて", filter == "all") { filter = "all" }
                    FilterPill("特別便", filter == "dorm") { filter = "dorm" }
                    FilterPill("通学便", filter == "commute") { filter = "commute" }
                }

                // 筛选区第二行：开关 +「空港送迎便のみ」（开时文字变主色）
                Row(verticalAlignment = Alignment.CenterVertically) {
                    TToggle(checked = airportOnly, onCheckedChange = { airportOnly = it })
                    Spacer(Modifier.width(8.dp))
                    Text(
                        "空港送迎便のみ",
                        color = if (airportOnly) cs.primary else t.inkSub,
                        style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Medium),
                    )
                }

                // 筛选后无结果 → 空态
                if (visible.isEmpty()) {
                    EmptyState(
                        icon = SuzuIcons.Bus,
                        title = "該当する便はありません",
                        message = "条件を変えてお試しください。",
                    )
                }

                // 日别分组列表 — 每组一张圆角卡
                groups.forEach { (date, routes) ->
                    BusDayGroup(date = date, weekday = routes.first().weekday, routes = routes, nextId = nextId)
                }

                // 底部备注（弱字）
                Text(
                    "※ 通常日のスクールバスは別途ご確認ください。特別便は乗車名簿への事前チェックが必要です。",
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, lineHeight = 15.sp),
                )

                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

// 筛选胶囊单颗：选中 = 主色底白字 / 未选 = pill 底主色字
@Composable
private fun FilterPill(
    label: String,
    active: Boolean,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    Box(
        modifier =
            Modifier
                .clip(RoundedCornerShape(percent = 50))
                .background(if (active) cs.primary else t.pill)
                .clickable(onClick = onClick)
                .padding(horizontal = 16.dp, vertical = 8.dp),
    ) {
        Text(
            label,
            color = if (active) Color.White else cs.primary,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
        )
    }
}

// 一个日别分组卡：组头（月/日 等宽 +「(曜日)」）+ 多行便
@Composable
private fun BusDayGroup(
    date: String,
    weekday: String,
    routes: List<SpecialBusRoute>,
    nextId: String?,
) {
    val t = SuzuT.current
    // "2026-05-06" → "05/06"
    val monthDay = date.removePrefix("2026-").replace("-", "/")
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(16.dp))
                .background(t.paper),
    ) {
        // 组头（浅主色底）
        Row(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .background(t.pill)
                    .padding(horizontal = 14.dp, vertical = 10.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                monthDay,
                color = t.ink,
                style = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace),
            )
            Spacer(Modifier.width(6.dp))
            Text(
                "($weekday)",
                color = t.inkSub,
                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Medium),
            )
        }
        // 组内每行
        routes.forEachIndexed { index, route ->
            if (index > 0) {
                // 行间分隔线（左缩进 58）
                Box(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .padding(start = 58.dp)
                            .height(0.5.dp)
                            .background(t.hair),
                )
            }
            BusRow(route = route, isNext = route.id == nextId)
        }
    }
}

// 单条便：左 36 圆角图标块 + 中（时刻 + Pill）+ direction + 右（次便 Pill + seats）
@Composable
private fun BusRow(
    route: SpecialBusRoute,
    isNext: Boolean,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        // 左侧 36×36 圆角图标块：次便 = 主色填充白图标，否则浅主色底
        Box(
            modifier =
                Modifier
                    .size(36.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(if (isNext) cs.primary else t.pill),
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                imageVector = if (route.isAirport) SuzuIcons.Plane else SuzuIcons.Bus,
                contentDescription = null,
                tint = if (isNext) Color.White else cs.primary,
                modifier = Modifier.size(18.dp),
            )
        }
        Spacer(Modifier.width(12.dp))

        // 中间：时刻 + Pill 行 + direction
        Column(modifier = Modifier.weight(1f)) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(
                    route.time,
                    color = t.ink,
                    style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace),
                )
                // 通学便 = Neutral / 特別便 = Accent
                Pill(route.kind, tone = if (route.kind == "特別便") PillTone.Accent else PillTone.Neutral)
                if (route.isAirport) {
                    Pill("空港", tone = PillTone.Accent)
                }
            }
            Spacer(Modifier.height(3.dp))
            Text(
                route.direction,
                color = t.inkSub,
                style = TextStyle(fontSize = 12.sp),
            )
        }

        // 右侧：次便 Pill + seats 弱字
        if (isNext || route.seats != null) {
            Spacer(Modifier.width(8.dp))
            Column(horizontalAlignment = Alignment.End, verticalArrangement = Arrangement.spacedBy(3.dp)) {
                if (isNext) {
                    Pill("次便", tone = PillTone.Accent)
                }
                if (route.seats != null) {
                    Text(
                        route.seats,
                        color = t.inkMute,
                        style = TextStyle(fontSize = 11.sp),
                    )
                }
            }
        }
    }
}
