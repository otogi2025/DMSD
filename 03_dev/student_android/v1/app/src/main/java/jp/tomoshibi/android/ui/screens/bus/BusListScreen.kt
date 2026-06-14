package jp.tomoshibi.android.ui.screens.bus

import androidx.compose.foundation.background
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
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.BusRouteOut
import jp.tomoshibi.android.data.network.endpoints.BusAPI
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.TToggle
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.time.DayOfWeek
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter

// 特別運行便一覧 — 接真后端 BusAPI.listRoutes()（spec §7.6，GET /api/v1/bus/routes）。
//   PageHeader「特別運行便」level 2 + 空港案内 banner +「空港送迎便のみ」开关 + 日别分组列表
//   只显示寮生特別運行便（dorm_special），平日通学便不显示（itsuki 2026-06-13，与 iOS 对齐）
//   「次便」高亮在「筛选后可见列表」里临场算（不在数据里写死），切筛选不会错位
//
// 三态外壳照 AnnouncementsScreen 模板：Loading / Failed(重试) / Empty / Success。
// 拿到后端 List<BusRouteOut> 后，整屏交互（筛选 / 分组 / 次便）在「成功内容」里基于 routes 跑。
//
// DTO → UI 字段映射（DTO BusRouteOut 字段名跟原界面模型 SpecialBusRoute 不同，按含义对应）：
//   id        → id（直接）
//   kind      → 后端代码 "daily_commute" / "dorm_special"；本屏只显示 dorm_special，徽章日语「特別運行便」
//   direction → direction（直接）
//   schedule_at（ISO 完整日期时间 String，如 "2026-05-06T09:20:00+09:00"）→ 拆出 date "2026-05-06" + time "09:20"，weekday 由 date 算
//   isAirport → DTO 没有此字段，从 name + direction 是否含「空港」推断
//   seats     → DTO 没有座席字段，原 UI 的「残り N 席」显示项暂无数据来源，恒为 null（见下方 TODO）
@Composable
fun BusListScreen(navController: NavHostController) {
    val t = SuzuT.current
    val scope = rememberCoroutineScope()
    // 三态：Loading / Failed(消息) / Empty / Success(后端 BusRouteOut 列表)
    var ui by remember { mutableStateOf<LoadState<List<BusRouteOut>>>(LoadState.Loading) }

    // 加载函数（重试也调它）。失败必须落 Failed，绝不退化成空列表。
    suspend fun load() {
        ui = LoadState.Loading
        ui =
            try {
                val items = BusAPI.listRoutes()
                if (items.isEmpty()) LoadState.Empty else LoadState.Success(items)
            } catch (e: ApiError) {
                LoadState.Failed(e.display)
            } catch (e: Exception) {
                LoadState.Failed("読み込みに失敗しました")
            }
    }
    LaunchedEffect(Unit) { load() }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "特別運行便", level = 2, onLeft = { navController.popBackStack() })

            // 三态渲染
            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox()
                }

                is LoadState.Failed -> {
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }

                // 空态（后端返回零条便）
                LoadState.Empty -> {
                    EmptyState(
                        icon = SuzuIcons.Bus,
                        title = "運行便はありません",
                    )
                }

                is LoadState.Success -> {
                    BusListContent(navController = navController, routes = s.value)
                }
            }
        }
    }
}

// 成功内容：原本整屏的筛选 / 分组 / 次便逻辑搬到这里，吃后端 routes（List<BusRouteOut>）。
@Composable
private fun BusListContent(
    navController: NavHostController,
    routes: List<BusRouteOut>,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme

    // 「空港送迎便のみ」开关
    var airportOnly by remember { mutableStateOf(false) }

    // 本页只显示寮生特別運行便（dorm_special），平日通学便隐藏（itsuki 2026-06-13，与 iOS 对齐）。
    val visible =
        routes.filter { route ->
            route.kind == "dorm_special" && (!airportOnly || route.isAirport())
        }

    // 「次便」判定：日本时区当前时刻拼成 "yyyy-MM-dd HH:mm"，
    // 在可见列表里取第一个「现在 <= 便发车时刻」的便 id
    val now =
        LocalDateTime
            .now(ZoneId.of("Asia/Tokyo"))
            .format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm"))
    val nextId = visible.firstOrNull { now <= "${it.date()} ${it.time()}" }?.id

    // 按日期分组，组 key 升序排列
    val groups = visible.groupBy { it.date() }.toSortedMap()

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

        // 班次类型筛选条（原「すべて」「特別便」「通学便」三胶囊）已删 —— 本页只显示特別運行便。
        // 仅保留下方开关 +「空港送迎便のみ」（开时文字变主色）
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
        groups.forEach { (date, dayRoutes) ->
            BusDayGroup(date = date, weekday = dayRoutes.first().weekday(), routes = dayRoutes, nextId = nextId)
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

// === BusRouteOut（后端 DTO）→ 原 UI 显示项的小转换函数 ===
// 后端只给 schedule_at（ISO 完整日期时间）+ kind 代码 + name/direction，原界面需要的
// date / time / weekday / 日语 kind / isAirport 在这里从 DTO 字段临场推算。

// schedule_at "2026-05-06T09:20:00+09:00" → 日期 "2026-05-06"。解析失败原样返回前 10 字符。
private fun BusRouteOut.date(): String = runCatching { scheduleAt.substring(0, 10) }.getOrDefault(scheduleAt.take(10))

// schedule_at → 出发时刻 "09:20"。解析失败返回空串。
private fun BusRouteOut.time(): String = runCatching { scheduleAt.substring(11, 16) }.getOrDefault("")

// date() → 日语单字曜日（如「水」）。解析失败返回空串。
private fun BusRouteOut.weekday(): String =
    runCatching {
        when (LocalDate.parse(date()).dayOfWeek) {
            DayOfWeek.MONDAY -> "月"
            DayOfWeek.TUESDAY -> "火"
            DayOfWeek.WEDNESDAY -> "水"
            DayOfWeek.THURSDAY -> "木"
            DayOfWeek.FRIDAY -> "金"
            DayOfWeek.SATURDAY -> "土"
            DayOfWeek.SUNDAY -> "日"
        }
    }.getOrDefault("")

// kind 后端代码 → 日语显示。"dorm_special"=特別運行便 / "daily_commute"=通学便（本页只显示前者）。
private fun BusRouteOut.kindLabel(): String =
    when (kind) {
        "dorm_special" -> "特別運行便"
        "daily_commute" -> "通学便"
        else -> kind
    }

// 是否空港送迎便：DTO 没有专门字段，从便名 name + 方向 direction 是否含「空港」推断。
private fun BusRouteOut.isAirport(): Boolean = name.contains("空港") || direction.contains("空港")

// 座席说明（如「残り 8 席」）：DTO 没有座席字段，原 UI 显示项暂无数据来源。
// TODO 接后端：缺 endpoint —— BusRouteOut 不含残席数，待后端加座席字段后填这里，现恒为 null（右侧弱字不显示）。
private fun BusRouteOut.seats(): String? = null

// 一个日别分组卡：组头（月/日 等宽 +「(曜日)」）+ 多行便
@Composable
private fun BusDayGroup(
    date: String,
    weekday: String,
    routes: List<BusRouteOut>,
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
    route: BusRouteOut,
    isNext: Boolean,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    val isAirport = route.isAirport()
    val kindLabel = route.kindLabel()
    val seats = route.seats()
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
                imageVector = if (isAirport) SuzuIcons.Plane else SuzuIcons.Bus,
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
                    route.time(),
                    color = t.ink,
                    style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace),
                )
                // 特別運行便 = Accent（本页只显示这类，恒为强调色）
                Pill(kindLabel, tone = if (kindLabel == "特別運行便") PillTone.Accent else PillTone.Neutral)
                if (isAirport) {
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
        if (isNext || seats != null) {
            Spacer(Modifier.width(8.dp))
            Column(horizontalAlignment = Alignment.End, verticalArrangement = Arrangement.spacedBy(3.dp)) {
                if (isNext) {
                    Pill("次便", tone = PillTone.Accent)
                }
                if (seats != null) {
                    Text(
                        seats,
                        color = t.inkMute,
                        style = TextStyle(fontSize = 11.sp),
                    )
                }
            }
        }
    }
}
